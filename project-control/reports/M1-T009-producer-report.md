# M1-T009 Producer Report — Pre-paid-traffic resilience for official-source connectors

- **Task ID:** M1-T009
- **Producer:** backend-engineer (worktree `.claude/worktrees/M1-T009`, branch `task/M1-T009-connector-resilience`)
- **Status requested:** `awaiting_gate`
- **Date:** 2026-07-17
- **Report path:** `project-control/reports/M1-T009-producer-report.md`

## 1. Objective delivered

Connector-layer resilience in `services/api` per the owner code-audit directive 2026-07-17 §2.5 (OWNER-REVIEW-code-audit-task-consolidation.md): TTL response caching with versioned keys, exact Retry-After honoring on 429, jittered bounded exponential backoff with a max-retry cap, per-source circuit breaker (closed/open/half_open, every transition tested), last-known-good (LKG) serving with VISIBLE staleness through existing provenance structures, per-analysis request budgets with a typed `budget_exceeded` failure, and structured secret-free metrics/log hooks. All tests deterministic (injected monotonic clock, injected wall clock, seeded RNG, sleep recorder, fixture transport — zero real sleeps, zero live network).

## 2. Files changed

New package `services/api/app/resilience/`:

| File | Content |
|---|---|
| `__init__.py` | Package doc + re-exports |
| `config.py` | `ResilienceConfig` frozen dataclass; defaults + `RESILIENCE_*` env injection; loud startup failure on invalid values |
| `metrics.py` | `ResilienceMetrics` (thread-safe counters + hook), `logging_metrics_hook` (JSON-escaped single-line events), closed event vocabulary, no-secrets contract |
| `cache.py` | `TTLCache`: injected-clock TTL, LRU-bounded (`max_entries`), versioned-key convention |
| `breaker.py` | `CircuitBreaker`: closed/open/half_open, cooldown by injected clock, transitions emitted as metrics |
| `budget.py` | `AnalysisBudget`: thread-safe per-analysis upstream-attempt counter |
| `retry.py` | `parse_retry_after` (RFC 9110 delay-seconds + HTTP-date vs injected wall clock, clamped, garbage-safe) and `backoff_delay` (full-jitter `uniform(0, min(cap, base*2^(n-1)))`) |
| `fetcher.py` | `ResilientPlutoFetcher` composition; `BudgetExceededError` (`error_type="budget_exceeded"`); `CircuitOpenError` (subclass of `SourceUnavailableError`, `detail.circuit="open"` — route status/state matrix unchanged); `LKG_NOTE_PREFIX`; `build_default_resilient_fetcher` |

Edited (additive):

- `services/api/app/connectors/pluto_soda.py` — `TransportResponse` gains optional `headers` mapping (default `{}`; every existing fixture transport constructing `(status, body)` unchanged); `urllib_transport` captures lowercase response headers defensively (`getattr(..., "headers", None)`); the 429 branch surfaces a sanitized `retry_after` value into `RateLimitedError.detail` (allowlist regex pass-through, `repr()` otherwise — same policy as `errorCode`). NO changes to field mappings, normalization, provenance emission, retry loop semantics, or error taxonomy.
- `services/api/app/api/v1/properties.py` — the production default fetcher is now a lazily built process-wide `ResilientPlutoFetcher` wrapping `fetch_by_bbl`; the `get_pluto_fetcher` dependency-override seam (used by all route tests and the web-e2e harness `apps/web/e2e/harness/fixture_api.py`) is unchanged. Removed the now-unused direct `fetch_by_bbl` import.

New tests `services/api/tests/resilience/` (53 tests): `helpers.py`, `test_cache.py`, `test_retry_after.py`, `test_backoff.py`, `test_breaker.py`, `test_lkg.py`, `test_budget.py`, `test_idempotency.py`, `test_metrics_and_config.py`, `test_route_wiring.py`, `__init__.py`.

**Not touched:** `packages/contracts/**`, `apps/web/**`, `.github/workflows/ci.yml`, `render.yaml`, `docs/**`, any other `project-control/**`. Verified via read-only `git status --porcelain`:

```
 M services/api/app/api/v1/properties.py
 M services/api/app/connectors/pluto_soda.py
?? services/api/app/resilience/
?? services/api/tests/resilience/
```

## 3. Contracts/schema changed

None. `app/resilience` matches the existing `include = ["app*"]` setuptools package discovery, so non-editable installs (web-e2e CI, production images) pick it up with no `pyproject.toml` change. The canonical property-profile schema, source_fact schema, bundled schema copies, contract-version enum/logic, and STATUS_STATE_MATRIX are all byte-identical to main.

## 4. Design decisions the G1/G3 reviewers should check

1. **Retry authority in ONE place.** The wrapper always calls `fetch_by_bbl(..., max_attempts=1, sleep=noop)`; the accepted connector keeps validation/typing/provenance, the resilience layer owns all retry/backoff/Retry-After behavior. No nested retry loops or double sleeps.
2. **Retry-After grounding.** The official Socrata app-tokens doc (M1-T001 E7; fixture F07 notes; M1-T003/M1-T004 registry drafts) documents ONLY the HTTP 429 status — no body shape and no Retry-After guarantee. When the header is present it is honored EXACTLY per generic RFC 9110 §10.2.3 semantics (delay-seconds and HTTP-date, date parsed against the injected wall clock, clamped ≥ 0); when absent/unparseable, jittered backoff. A Retry-After above `retry_after_max_wait_seconds` is honored by NOT retrying (typed `rate_limited` immediately, thread never blocked).
3. **Retryable classification.** Retryable = `RateLimitedError`, `SourceTimeoutError`, and `SourceUnavailableError` without a non-5xx `http_status` detail (network/5xx). Never retried: `SchemaDriftError` (M1-T001 G1: drift is never blindly retried), non-drift 400s, refused 3xx. The same classification gates breaker counting and LKG eligibility — drift can never trip the breaker or be masked by stale data.
4. **LKG staleness through EXISTING structures (no contract change).** A served LKG result keeps the ORIGINAL `retrieved_at` on the result and every fact (provenance records actual retrieval), and appends one note with the stable machine-readable prefix `served_from_last_known_good:` stating the upstream error type, serve-time wall timestamp, original retrieval timestamp, and age. The accepted builder passes notes verbatim into `reproducibility.connector_notes` (schema: array of non-empty strings — validates), and its `missing_inputs` note-prefix map ignores the new prefix (no phantom missing inputs; asserted). Tests prove the LKG-built profile passes `validate_profile` (M2-T003 boundary validation).
5. **Circuit-open surfacing.** `CircuitOpenError` deliberately keeps `error_type="source_unavailable"` so the documented route (status, state) matrix is unchanged — a fast reject means "the official source is not being called because it is failing", with `detail.circuit="open"` for operators. No new emission path, no matrix edit.
6. **Budget = upstream attempts.** One unit per upstream ATTEMPT (retries consume; cache hits free). Exhaustion raises typed `budget_exceeded` BEFORE any upstream I/O and is never masked by LKG (a budget is a caller-side condition, not an outage). The route passes no budget today (no analysis-run construct exists before M2); the typed error therefore cannot surface on the HTTP path yet — when analysis runs wire budgets, that layer adds its documented mapping.
7. **Bounded memory.** Cache and LKG stores are LRU/oldest-evicted with configurable `max_entries` (default 10,000 each; per-BBL results ~1.5 KB) — a worker process cannot grow them without limit.

## 5. Acceptance scenarios S1–S8 — commands and results

All run in `services/api` on the fixture transport; no network. Command per suite: `python -m pytest tests/resilience/<file> -q` (Python 3.11.9 local; CI runs the existing `api` job unchanged).

| Scenario | Test file (tests/resilience/) | Key assertions |
|---|---|---|
| S1 cache | `test_cache.py` (7 tests) | 2nd identical request within TTL: transport call count stays 1 (proof of zero upstream); TTL-boundary hit; expiry refetches (`cache_expired`); versioned key carries version+source+dataset+bbl and differs across versions; no_match cached; LRU eviction event at `max_entries`; unit TTL/LRU test; hit-ratio 0.5 |
| S2 Retry-After | `test_retry_after.py` (8 tests) | Sleep sequence EXACTLY `[7.0]` for `retry-after: 7` (no jitter event); HTTP-date form `[30.0]` against injected wall clock; past date clamps `[0.0]`; `600 > cap 120` → typed `RateLimitedError`, zero sleeps, one transport call; missing/malformed header → jittered fallback within bound; connector surfaces sanitized detail case-insensitively; hostile CRLF header repr()-sanitized; parser garbage table |
| S3 backoff | `test_backoff.py` (7 tests) | Delay sequence equals exact seeded-RNG replay (`uniform(0,0.5)`, `uniform(0,1.0)`); spread across 20 seeds (≥15 distinct, range > 0.1, all within bound); cap enforced across 11 attempts; exactly `max_attempts` transport calls then typed failure; timeouts retried; drift and non-drift 400 never retried |
| S4 breaker | `test_breaker.py` (4 tests) | Opens at threshold 3; open → fast reject with ZERO new transport calls and `detail.circuit="open"`; cooldown elapse → half_open trial goes upstream; failed trial re-opens (fresh cooldown re-checked); successful trial closes; full transition list asserted from metrics events: closed→open, open→half_open, half_open→open, open→half_open, half_open→closed; success resets the consecutive count; drift never trips the breaker; unit cooldown_remaining/allow test |
| S5 last-known-good | `test_lkg.py` (6 tests) | Upstream 500 after a success → LKG served with original `retrieved_at` on result and every fact, exactly one `served_from_last_known_good:` note containing the original timestamp, age, error type, and the word STALE; `build_property_profile` + `validate_profile` PASS on the LKG result and the note appears in `reproducibility.connector_notes` with `missing_inputs` unchanged; no LKG → original typed failure (`lkg_unavailable`); LKG older than `lkg_max_age_seconds` → typed failure (`lkg_too_old`); drift never masked; breaker-open fast reject serves LKG with "circuit open" in the note and zero upstream I/O |
| S6 budget | `test_budget.py` (6 tests) | Budget 2: third analysis fetch raises typed `budget_exceeded` with correlation id + detail (max/consumed/analysis_id) and transport count frozen at 2, including on further attempts; cache hits consume nothing; retries consume units and stop mid-retry (2 calls of 3 possible); exhausted budget never masked by available LKG (zero upstream, zero `lkg_served`); `budget_consumed` metric reports remaining; validation + thread-safe counting |
| S7 idempotency | `test_idempotency.py` (3 tests) | timeout-then-200 retried fetch equals a clean single-attempt fetch on every fact key except the by-contract event-scoped `observation_id`; `retrieved_at` identical (stamped at the SUCCESSFUL attempt, injected clock); no attempt/retry artifacts in any fact; repeat call cache-served with no duplicate upstream call; exactly one cache and one LKG entry per key |
| S8 regression | full suite | `python -m pytest -q` → **264 passed** (baseline on this branch before my changes: **211 passed**; +53 new, zero failures, zero modified existing tests except none). No live network anywhere; new suites run inside the existing CI `api` job automatically (testpaths `tests`) — **no ci.yml change needed or made** |

Plus `test_metrics_and_config.py` (8 tests, item H + config surface) and `test_route_wiring.py` (2 tests, default-fetcher wiring + process-wide singleton).

### Exact self-check outputs (2026-07-17, `services/api`, Python 3.11.9)

```
> python -m pytest -q
264 passed in 3.01s

> python -m pytest tests/resilience -q
53 passed in 0.88s

> python -m ruff check app tests
All checks passed!
```

Baseline captured before implementation on the same branch: `python -m pytest -q` → `211 passed in 3.14s`.

## 6. How staleness is surfaced (and the recommended contract follow-up)

Existing structures only: original `retrieved_at` (result, every fact, `reproducibility.retrieved_at`) + the `served_from_last_known_good:` prefixed note in `reproducibility.connector_notes` (the schema field whose description already covers "Conflicts and stale data stay visible (PRD principle 4)"). Never silently fresh; no LKG → typed failure; LKG payloads pass M2-T003 pre-send validation (tested).

**Recommended additive follow-up (G1-reviewed, NOT done here — contract path is forbidden):** a first-class `reproducibility.staleness` object (e.g. `{served_from_cache: bool, stale: bool, upstream_error_type, original_retrieved_at, age_seconds}`) as an optional 1.3.0 key through the M2-T003 pipeline, so consumers get a typed flag instead of parsing the stable note prefix.

## 7. Configuration surface

`ResilienceConfig` defaults (all injectable per instance; env-overridable via `RESILIENCE_<FIELD>` with loud `RuntimeError` on invalid values):

| Field | Default | Env var |
|---|---|---|
| cache_ttl_seconds | 900.0 | RESILIENCE_CACHE_TTL_SECONDS |
| cache_key_version | "v1" | RESILIENCE_CACHE_KEY_VERSION |
| cache_max_entries | 10000 | RESILIENCE_CACHE_MAX_ENTRIES |
| retry_max_attempts | 3 | RESILIENCE_RETRY_MAX_ATTEMPTS |
| backoff_base_seconds | 0.5 | RESILIENCE_BACKOFF_BASE_SECONDS |
| backoff_cap_seconds | 30.0 | RESILIENCE_BACKOFF_CAP_SECONDS |
| retry_after_max_wait_seconds | 120.0 | RESILIENCE_RETRY_AFTER_MAX_WAIT_SECONDS |
| breaker_failure_threshold | 5 | RESILIENCE_BREAKER_FAILURE_THRESHOLD |
| breaker_cooldown_seconds | 60.0 | RESILIENCE_BREAKER_COOLDOWN_SECONDS |
| lkg_max_age_seconds | 86400.0 | RESILIENCE_LKG_MAX_AGE_SECONDS |
| lkg_max_entries | 10000 | RESILIENCE_LKG_MAX_ENTRIES |

Retry defaults mirror the accepted M1-T002 budget (3 attempts, 0.5 s base). TTL 900 s cannot hide a quarterly PLUTO release. All rationale documented in `config.py`.

## 8. Assumptions and defaults

- Header names in `TransportResponse.headers` are lowercase by transport contract; the connector's Retry-After lookup is additionally case-insensitive for injected test transports.
- `no_match` results are cached (TTL) but NOT stored as LKG (only `status=="ok"` results are; a stale "absence" claim is riskier than a typed failure).
- In `half_open`, more than one concurrent trial may be admitted (no single-flight latch) — documented in `breaker.py`, acceptable at per-BBL volume.
- The per-source breaker is per fetcher instance (one instance per source composition; PLUTO is the only connector in services/api today).
- Python 3.11.9 locally vs `requires-python >= 3.12`: pre-existing environment condition, unchanged by this task; CI runs the pinned version.

## 9. Known limitations (disclosed)

1. **In-process stores.** Cache/LKG/breaker state is per process and lost on restart; a Supabase-backed LKG store is future work once persistence tasks land (M2).
2. **Budget not yet wired to HTTP.** No analysis-run construct exists before M2, so `budget_exceeded` cannot surface on the route today; the matrix is intentionally unchanged. S6 is proven at the library layer, as specified.
3. **Cache-hit correlation-id nuance (flag for G1).** On a cache/LKG-served 200, `reproducibility.correlation_id` is the ORIGINAL building fetch's correlation id (the true join key to the retrieval logs), while the response `X-Correlation-ID` header is fresh per request. The schema's description sentence ("equals the X-Correlation-ID response header") was written for the stateless-build era. No test asserts that equality on the 200 path (error-body equality assertions are unaffected), but the schema description should be refreshed in the same additive 1.3.0 pass recommended in §6.
4. **Staleness flag is a note prefix,** not a typed field, until the recommended contract follow-up (§6).
5. **Retry-After live capture missing.** A polite live 429 capture with a real Retry-After header remains impossible to force (F07 rationale); the header handling is grounded in RFC 9110 + the synthetic fixture and unit-tested both forms.

## 10. Security / provenance impact

- No secrets in metrics/logs: asserted by test (`app_token` never appears in any hook event; `x-app-token` never serialized). The default hook JSON-escapes fields so hostile strings cannot inject log lines (extends M1-T002 G5 F5 policy).
- Retry-After is untrusted response data: allowlist-sanitized before entering typed-error detail (hostile CRLF header → `repr()`; tested).
- Response headers are captured lowercase for the transport contract but never logged and never placed in payloads except the sanitized `retry_after` detail. The request's `X-App-Token` is not part of response headers.
- Provenance semantics unchanged: `retrieved_at` always the actual retrieval; observation ids remain event-scoped; no retry artifacts in facts (S7).
- Memory-bounded stores (item 7 of §4) prevent unbounded worker growth.
- Local disk: pure-Python source files only (~40 KB); no datasets, no caches on disk, no cleanup needed; owner-PC budget untouched.

## 11. New risks / dependencies

- The route now serves cached results for up to `cache_ttl_seconds` (default 15 min) — a deliberate paid-traffic tradeoff; `retrieved_at` keeps it honest. If the Confirm-screen UX ever needs a forced refresh, that is the existing `POST /properties/{bbl}/refresh` PRD endpoint (future task), not a cache bypass hack.
- Future connectors should reuse `app.resilience` components rather than reimplementing (cache/breaker/budget/retry are connector-agnostic; only `fetcher.py` is PLUTO-typed).

## 12. Recommended next tasks

1. Additive contract 1.3.0: `reproducibility.staleness` typed object + refreshed correlation_id description (M2-T003 pipeline, G1-reviewed) — closes §6/§9.3/§9.4.
2. Wire `AnalysisBudget` into the analysis-run machinery when M2 lands (with the route/job `budget_exceeded` mapping and matrix addition).
3. Persist LKG snapshots in Supabase once the M2 persistence tables exist (restart-safe last-known-good).
4. Expose `ResilienceMetrics.snapshot()` + breaker state on the M1 connector-health admin surface (`api_connector_health`).

## 13. Evidence index

- Implementation: `services/api/app/resilience/*`, additive edits in `services/api/app/connectors/pluto_soda.py`, `services/api/app/api/v1/properties.py`
- Tests: `services/api/tests/resilience/*` (53 tests)
- Commands/outputs: §5 (full suite 264 passed; resilience suite 53 passed; ruff clean; baseline 211)
- Scope proof: §2 git status (read-only)
