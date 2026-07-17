<!-- Verbatim reviewer return (agent-return channel; agentId a9cb57f4a6648633c, data-contract-verifier, 2026-07-17). Saved by the orchestrator per the report-preservation rule. Verdict: PASS (D1/D2 LOW non-blocking corrective follow-ups riding the next additive contract revision; follow-up task to be tracked at acceptance). -->

# G1 Gate Report — M1-T009 Pre-paid-traffic connector resilience

- **Task:** M1-T009 (`project-control/tasks/M1-T009.json`, scenarios S1–S8)
- **Gate:** G1 — Source and data-contract gate
- **Reviewer:** data-contract-verifier (independent; producer was backend-engineer)
- **Target:** worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M1-T009\`, branch `task/M1-T009-connector-resilience`, HEAD `8970d77` (merge-base with main `a18b696`)
- **Date:** 2026-07-17
- **Method:** independent read of packet + code + schema + committed research; live re-verification of the official Socrata documentation; full test execution in the worktree (not relying on producer claims or CI alone)

## 1. Scope and diff audit (lens 1, 4)

`git diff main...HEAD --stat` (merge-base diff, excluding unrelated main-side movement): only `services/api/**` and the producer's own report. `git diff main...HEAD -- packages/contracts` is **empty** — the canonical property-profile schema, `connector_notes`, and `correlation_id` definitions on this branch are byte-identical to main. No `docs/**`, `.github/workflows/ci.yml`, `render.yaml`, or other `project-control/**` changes. Allowed/forbidden paths respected.

`services/api/app/connectors/pluto_soda.py` diff verified line-by-line: **additive-only transport changes exactly as the packet permits** —
- `TransportResponse` gains `headers: Mapping[str, str] = field(default_factory=dict)` (existing 2-arg constructions unchanged);
- `urllib_transport` captures lowercase response headers defensively via `getattr(..., "headers", None)` on both success and `HTTPError` paths;
- the 429 branch adds a single `retry_after` key to `RateLimitedError.detail`, allowlist-sanitized (`^[A-Za-z0-9,: +\-]{1,64}$`, `repr()` otherwise — same policy as the accepted `errorCode` sanitizer; hostile CRLF header tested).

**No changes** to field mappings, units, normalization, vintage/effective-date handling, provenance emission, retry-loop semantics, or the error taxonomy (no new error classes in the connector; `CircuitOpenError` lives in the resilience package and deliberately subclasses `SourceUnavailableError` so the documented route (status, state) matrix is untouched — confirmed in `app/api/v1/properties.py`, whose only change is the lazily built process-wide resilient default fetcher behind the unchanged `get_pluto_fetcher` override seam).

## 2. Verification table (G1 catalog items applicable to this task)

| # | G1 item | Evidence | Result |
|---|---|---|---|
| 1 | Official source identity / endpoint unchanged | Connector URL construction, `SOURCE_ID`, `DATASET_ID` untouched by diff; cache key embeds both | PASS |
| 2 | Rate-limit semantics grounded, not guessed (S2) | Committed research: `docs/research/pluto-mappluto-2026-07-16.md` E7 (`dev.socrata.com/docs/app-tokens`, retrieved 2026-07-16, re-verified at the original G1) and registry draft `source-registry-drafts/pluto-mappluto.json` (`throttle_signal: "HTTP 429"`, no Retry-After) document ONLY the 429 status. Fixture `tests/fixtures/pluto/F07_rate_limit_429_synthetic.json` notes record this explicitly with source-doc provenance. **Independent live re-check by this reviewer (2026-07-17):** the current official page states "If you are throttled for any reason, you will receive a status code 429 response" and mentions neither Retry-After nor a body shape. Producer claim confirmed against both committed research and the current official source | PASS |
| 3 | Retry-After parser vs RFC 9110 §10.2.3 | `app/resilience/retry.py`: delay-seconds (`^\d{1,10}$` → non-negative integer) AND HTTP-date (`parsedate_to_datetime`, naive dates forced to GMT per RFC) both supported; past dates clamp to 0 (tested: `[0.0]` sleep); value above `retry_after_max_wait_seconds` → no wait, typed `RateLimitedError`, one transport call (tested); absent/unparseable → jittered fallback, never a crash (garbage table tested). Honored EXACTLY when present — sleep sequence `[7.0]` / `[30.0]` asserted verbatim against injected wall clock, zero jitter events | PASS |
| 4 | Actual response fixtures, no live CI calls (S8) | All resilience tests run on the accepted M1-T002 fixture pack + synthetic F07 via `FakeTransport`; injected monotonic/wall clocks, seeded RNG, sleep recorder; full suite ran offline in 4.3 s | PASS |
| 5 | Field mapping and units | No mapping/normalization code touched (diff audit §1) | PASS (unchanged) |
| 6 | Null/unknown semantics | Unchanged; `no_match` results cached with TTL but deliberately NOT stored as LKG (a stale absence claim is riskier than a typed failure — sound judgment, documented) | PASS |
| 7 | Retrieval/version timestamps & provenance persistence (S5, S7) | **Provenance-critical item verified.** `fetcher.py::_serve_lkg_or_raise`: served LKG deep-copy keeps the ORIGINAL `retrieved_at` on the result and every fact (asserted in `test_lkg.py` for all facts); appends exactly one note with stable prefix `served_from_last_known_good:` containing upstream error type, serve-time wall timestamp, original retrieval timestamp, age, and the literal word "STALE". Note lands in `reproducibility.connector_notes` — an existing required contract field (array of non-empty strings) whose schema description already covers "Conflicts and stale data stay visible (PRD principle 4)"; schema unchanged on branch. `build_property_profile` + `validate_profile` (M2-T003 boundary) pass on the LKG profile, `missing_inputs` unchanged (no phantom inputs) — **I reran this test: passes.** No-LKG → original typed failure (`lkg_unavailable`); LKG older than 24 h → typed refusal (`lkg_too_old`); schema drift NEVER masked by LKG; breaker-open serve carries "circuit open" in the note with zero upstream I/O | PASS |
| 8 | Schema-drift handling | `SchemaDriftError` never retried, never trips the breaker, never masked by LKG (classification in `_is_retryable`; tested in backoff, breaker, and LKG suites) — consistent with the original M1-T001 G1 finding | PASS |
| 9 | Pagination/update behavior | N/A for this layer (single-record by-BBL fetch unchanged); cache TTL 900 s justified against the quarterly/monthly PLUTO release model (config.py rationale cites README 26v1) and cannot hide a release | PASS |
| 10 | Contract compatibility | `packages/contracts` diff empty; STATUS_STATE_MATRIX unchanged; route seam unchanged; existing 211 tests + 53 new = **264 passed** (reviewer-executed); `ruff check app tests` clean (reviewer-executed) | PASS |
| 11 | Typed failures never masquerade as official answers (S4/S6) | `BudgetExceededError` (`error_type="budget_exceeded"`) raised BEFORE any upstream I/O and explicitly re-raised past the LKG path (`except BudgetExceededError: raise`); test proves an exhausted budget with an available LKG serves nothing (zero upstream, zero `lkg_served`). `CircuitOpenError` fast rejects with `detail.circuit="open"` and zero transport calls | PASS |
| 12 | Versioned cache keys (S1) | Key = `{cache_key_version}:{SOURCE_ID}:{DATASET_ID}:bbl={canonical}`; cross-version non-collision tested; TTL-boundary, expiry-refetch, LRU-eviction, deep-copy isolation all tested. A quarterly data release under the same dataset id is bounded by the 900 s TTL and truthful `retrieved_at`/`dataset_version` provenance in the cached payload | PASS |
| 13 | Idempotency/provenance (S7) | Retried (timeout→200) fetch equals a clean fetch on every fact key except the by-contract event-scoped `observation_id`; `retrieved_at` identical (stamped at the successful attempt); no `attempt`/`retry` artifacts in any fact; exactly one cache and one LKG entry per key — reviewer-executed, passes | PASS |
| 14 | Secrets/log hygiene at the data boundary | Retry-After treated as untrusted response data (allowlist/repr before typed detail); headers never logged, never in payloads unsanitized; metrics hook JSON-escapes fields; token-leak-absence asserted | PASS |

Commands executed by this reviewer in the worktree (`services/api`): `python -m pytest tests/resilience -q` → **53 passed in 0.91s**; `python -m pytest -q` → **264 passed in 4.30s**; `python -m ruff check app tests` → clean. CI note: the PR #20 control-plane job failure is the known repo-wide test-data issue tracked under M0-T017 and is outside this task's scope; the api job covering these 264 tests is green and I reproduced the run locally.

## 3. Judgments on producer-flagged items

**J1 — Correlation-id semantics on cache/LKG-served 200s (lens 5).** Judgment: **provenance-correct, not a data defect.** `reproducibility.correlation_id` is defined by the schema as "the reproducibility identifier joining this profile to logs and job records" (PRD §20 item 17); on a cached/LKG serve, the ORIGINAL fetch's id is the only value that truthfully joins to the retrieval that produced the payload — rewriting it to the serving request's id would falsify reproducibility. The per-request X-Correlation-ID header correctly identifies the HTTP exchange. What is now wrong is one non-normative schema **description** sentence ("equals the X-Correlation-ID response header"), written in the stateless-build era. Recorded as defect D1, corrective, non-blocking (see §4).

**J2 — Deferring the contract 1.3.0 staleness object (lens 4).** Judgment: **deferral acceptable.** Current visibility satisfies PRD §9 / permanent principle 4: the served profile's `retrieved_at` (result, every fact, reproducibility) is always the actual original retrieval moment, and every LKG serve carries a machine-readable stable-prefix note in a schema-valid, contract-existing field whose own description names stale-data visibility. Stale data is never presented as fresh. The typed `reproducibility.staleness` object remains the right long-term shape and must be a tracked follow-up (D2), through the M2-T003 pipeline as the packet's forbidden-paths rule requires — it could not have been done inside this task.

## 4. Defects

| ID | Severity | Blocking? | Description | Required action |
|---|---|---|---|---|
| D1 | Low | No (for G3/acceptance of this task) | Schema description of `reproducibility.correlation_id` ("equals the X-Correlation-ID response header of the M1-T005 endpoint") is stale for cache/LKG-served 200s. Descriptions are non-normative; validation passes; payload semantics are provenance-correct (J1) | Refresh the description in the additive contract 1.3.0 pass (M2-T003 pipeline, G1-reviewed). Orchestrator must create/track this follow-up task at acceptance |
| D2 | Low | No | Staleness/cache-served state is a note prefix (`served_from_last_known_good:`) rather than a typed field, and a within-TTL cache serve has no explicit `served_from_cache` marker (truthful `retrieved_at` bounds it to ≤900 s) | Same follow-up: additive `reproducibility.staleness` object (`served_from_cache`, `stale`, `upstream_error_type`, `original_retrieved_at`, `age_seconds`) in contract 1.3.0 |

Observation (no defect): `parse_retry_after` treats delay-seconds longer than 10 digits as unparseable → jittered backoff rather than typed over-cap failure; behavior is bounded and fail-safe.

## 5. Conclusion

The resilience layer is grounded (Retry-After claim matches committed research AND the current official Socrata documentation, independently re-fetched), additive-only at the connector, contract-clean, and — on the provenance-critical S5 item — never presents stale data as fresh: original retrieval timestamps are preserved everywhere and every LKG serve is loudly labeled through an existing schema-valid provenance channel, verified by executing the producer's tests myself (53/53 resilience, 264/264 full suite). D1/D2 are non-blocking corrective follow-ups that by design must ride the next additive contract revision (a path this task was forbidden to touch); the orchestrator should record the follow-up task (producer report §12 item 1) before or with the M2-T003-pipeline 1.3.0 change.

PASS
