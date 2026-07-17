<!-- Verbatim reviewer return (agent-return channel; agentId a96b9ff5f1fd18ca0, qa-engineer, 2026-07-17). Saved by the orchestrator per the report-preservation rule. Verdicts: G3 PASS, G4 PASS (zero blocking defects; LOW observations O1-O4). -->

# Gate Report — M1-T009 Pre-paid-traffic connector resilience

**Gates:** G3 (independent walkthrough) + G4 (integration & regression)
**Reviewer:** qa-engineer (independent; did not produce this work)
**Target:** worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M1-T009`, branch `task/M1-T009-connector-resilience`, HEAD `8970d77`
**Method:** Reviewed from the packet's S1–S8 acceptance scenarios (`project-control/tasks/M1-T009.json`), not the producer report. Read all 7 implementation modules and all 10 test files, reran the full suite and lint myself, and wrote/ran 6 throwaway probes (temp file outside the repo, deleted after) covering edge cases the producer did not test.

## Commands run (my own executions, this worktree)

| Command | Result |
|---|---|
| `cd services/api && python -m pytest -q` | **264 passed in 5.98s** (matches expected 264; 53 of them are the new `tests/resilience/` tests) |
| `python -m ruff check app tests` | **All checks passed!** |
| `python -m pytest tests/resilience -q` | 53 passed in 0.86s |
| `git diff main...HEAD --stat` | 22 files: `services/api/**` (7 app modules, 11 test files, 2 touched app files) + `project-control/reports/M1-T009-producer-report.md` only |
| `git diff main...HEAD --name-status -- services/api/tests` | **All `A` (added), all under `tests/resilience/`** — zero existing tests edited |
| `git diff main...HEAD --name-only -- services/api/pyproject.toml .github/workflows packages apps` | **empty** |
| grep `time.sleep` in app + tests | Only 2 hits, both as injectable *defaults* (`sleep: Callable = time.sleep` in connector and fetcher signatures); tests inject `SleepRecorder`. The 5.98s wall time for 264 tests independently proves no real sleeping (scripted delays of 7s/30s/120s would dominate otherwise). |
| Reviewer probes P1–P6 (code below summary) | **ALL PROBES PASSED** |

## G3 — Scenario findings (S1–S8)

| Scenario | Verdict | Evidence (test honesty assessment) |
|---|---|---|
| **S1 cache** | PASS | `test_cache.py`: second call proven by transport call-count == 1 (script holds only ONE response — an upstream hit would raise "script exhausted", a strong seam). TTL boundary exact with injected `FakeMonotonic`: `age == ttl` still served (line 52–58), `301 > 300` refetches with `cache_expired` metric. Versioned key asserted to carry version + SOURCE_ID + DATASET_ID + bbl; v7 vs v8 keys proven non-colliding. LRU bound: `cache_max_entries=2`, third BBL evicts the LRU key, evicted key identity asserted from the metrics event. Deep-copy isolation asserted (`second.facts[0] is not first.facts[0]`). Not tautological — all proofs are transport counts and metric events, not implementation echoes. |
| **S2 Retry-After** | PASS | `test_retry_after.py`: sleep sequences asserted EXACTLY — delay-seconds `"7"` → `[7.0]` with `retry_scheduled == 0` (no jitter contamination); HTTP-date 30s ahead of the injected `FakeWallClock` → `[30.0]`; past date → `[0.0]`; `"600"` above the 120s cap → typed `RateLimitedError`, `sleeps == []`, exactly 1 transport call. Malformed/missing header → jittered fallback (asserted per variant). Connector-side: case-insensitive header pickup and repr()-sanitization of a CRLF-hostile header both tested against `fetch_by_bbl` directly. No real sleeps anywhere. |
| **S3 backoff** | PASS | Seeded-RNG exact replay: expected sequence recomputed from a *fresh* `Random(seed)` with hardcoded bounds (0.5, 1.0) — verifies `base·2^(n-1)` independently, not tautologically. Distribution: 20 seeds → ≥15 distinct values, spread > 0.1, all within bound. Cap respected for attempts 1–11. Max attempts exact: 3 transport calls, 2 sleeps (none after final failure). Schema-drift 400 and non-drift 400 both proven never-retried (1 call, zero sleeps). |
| **S4 breaker** | PASS | Full state machine asserted as an exact ordered transition list from emitted `breaker_transition` metrics events: `closed→open`, `open→half_open`, `half_open→open` (failed trial, fresh cooldown re-verified by a mid-cooldown fast reject), `open→half_open`, `half_open→closed`. Fast-reject with zero transport I/O proven by call count staying at 3; typed `CircuitOpenError` keeps outward `error_type == "source_unavailable"` with `detail.circuit == "open"` (route matrix preserved). Cooldown fully clock-controlled. Success resets the consecutive counter (2+2 failures with a success between never trips threshold 3). Drift never trips it. |
| **S5 LKG** | PASS | Staleness note validated through the **real** `build_property_profile` + `validate_profile` (M2-T003 boundary validation, not mocked) — note surfaces in `reproducibility.connector_notes`, `retrieved_at` stays the ORIGINAL retrieval on the result and on every fact, no phantom `missing_inputs`. Note content asserted: stable prefix, original timestamp, `age 120s`, error type, "STALE". No-LKG → original typed failure with `lkg_unavailable` metric. `601 > 600` too-old → refused typed. Drift never masked by LKG. Breaker-open fast-reject serves LKG with "circuit open" in the note. |
| **S6 budget** | PASS | Typed `budget_exceeded` with full detail (max/consumed/analysis_id/correlation_id); zero further upstream calls proven by transport count frozen at 2 across two subsequent attempts. Cache hits free (consumed unchanged). Retries consume units and stop mid-retry (2 calls of a 3-attempt config on budget 2). Budget exhaustion never masked by LKG (`lkg_served == 0` despite available snapshot). |
| **S7 idempotency** | PASS | Retried result compared field-by-field against a clean single-attempt run: identical `retrieved_at`, identical facts modulo `observation_id` (event-scoped by M2-T004 contract), identical notes/drift_signals, no `attempt`/`retry` artifacts in any fact. Post-retry repeat is a cache hit; stores hold exactly one entry per key. |
| **S8 regression** | PASS | 264 passed (my run, above), ruff clean, all transports are scripted fixtures, zero live network. CI PR #20: api job green per orchestrator; the failing control-plane job is the known repo-wide test-data bug tracked as M0-T017 (unrelated to this diff — the diff touches no control-plane files). |

## Reviewer probes (edge cases the producer did NOT test) — all passed

Run against the worktree via a temp script outside the repo (deleted after; key excerpts):

- **P1 — half-open concurrent trials:** `breaker.allow()` twice while `half_open` → both admitted (matches the documented no-single-flight limitation in `breaker.py`); a failed trial re-opens, and a lingering second trial's `record_success()` then closes the just-re-opened breaker immediately. Behavior matches documentation; see observation O1.
- **P2 — LKG at exactly max age:** `advance(600.0)` with `lkg_max_age_seconds=600` → **served** (`lkg_served==1`, `lkg_too_old==0`) — refusal is strictly `>`, consistent with the cache's TTL boundary semantics.
- **P3 — Retry-After exactly at cap:** header `"120"` with cap 120 → honored, `sleeps == [120.0]`, `retry_after_exceeds_cap == 0` — cap check strictly `>`, boundary safe.
- **P4 — Retry-After × breaker interaction:** two above-cap 429 final failures trip a threshold-2 breaker; while open: zero transport I/O, typed `CircuitOpenError`, zero sleeps throughout.
- **P5 — fresh cache hit while breaker open:** cache lookup precedes the breaker, so an in-TTL entry is served with zero fast-rejects and zero upstream I/O, and is correctly NOT stale-labeled (it is within TTL).
- **P6 — budget=0, no LKG:** typed `budget_exceeded` (`consumed=0`, `max=0`) before any upstream I/O — transport calls 0; never surfaces as a source error.

## G4 — Integration & regression checks

| Check | Verdict | Evidence |
|---|---|---|
| Diff scope | PASS | Only `services/api/**` + own producer report. No `ci.yml`, no `packages/contracts`, no `apps/web`, no `render.yaml`, no docs, no other project-control files. Within `allowed_paths`. |
| Route wiring | PASS | `properties.py`: `_default_fetcher` now delegates to a `@lru_cache(maxsize=1)` lazily built `ResilientPlutoFetcher` — env is not read at import time. The `get_pluto_fetcher` override seam is byte-identical in behavior (`get_pluto_fetcher() → _default_fetcher`); both existing route-test files override it via `app.dependency_overrides` exactly as before, and no route test exercises the default path. Web-e2e harness stays on the fixture path (web CI job green). `CircuitOpenError` subclasses `SourceUnavailableError` → documented (503, source_unavailable) matrix unchanged, `detail.circuit` distinguishes it for operators. |
| Process-wide singleton / test pollution | PASS | The singleton is only reachable through `_default_fetcher`, which no test invokes; `test_route_wiring.py` is the sole test touching `_default_resilient_fetcher` and calls `cache_clear()` in both setup and `finally`. Route tests bypass it entirely via the dependency override. Prod: one cache/breaker/LKG per worker process — standard and intended ("process-wide state" is the point of the layer). |
| Existing suites unmodified | PASS | `git diff main...HEAD -- services/api/tests` → additions under `tests/resilience/` only; no existing test edited to make anything pass. |
| Connector change is additive | PASS | `TransportResponse.headers` added **with a default factory** — every existing fixture transport constructing `TransportResponse(status, body)` is unaffected (proven by the untouched connector suite passing). Retry-After surfaced into the typed-error detail sanitized (allowlist regex + repr fallback, hostile CRLF header test present). Double-retry avoided: the fetcher always calls `fetch_by_bbl` with `max_attempts=1` and a no-op sleep, so retry authority lives in exactly one place. |
| No new dependencies | PASS | `pyproject.toml` untouched; all resilience modules import stdlib + existing app modules only. |
| No live network / low-storage | PASS | All tests fixture-driven; suite runs in 6s; no large artifacts written (temp probe was outside the repo and deleted). |
| Provenance discipline | PASS | `retrieved_at` never rewritten on LKG serves; staleness rides the existing `notes → reproducibility.connector_notes` contract path (no contract change smuggled in); metrics events carry no header/token material (asserted by `test_no_secret_material_in_any_metrics_event` with a planted secret). |

## Defects and observations

No blocking defects.

- **O1 (Low, non-blocking, documented):** In `half_open`, multiple concurrent trials are admitted (no single-flight latch), and a lingering trial's success can immediately close a breaker that a failed sibling just re-opened (probe P1). The limitation is explicitly documented in `breaker.py`'s docstring and is acceptable at per-BBL call volume; recommend revisiting if per-source concurrency grows (candidate hardening: ignore `record_success` while `open` unless the success belongs to the admitted trial).
- **O2 (Low, non-blocking):** `functools.lru_cache` does not guarantee single execution under a concurrent first call — two racing first requests could each build a fetcher instance, with one winning the cache (transient startup-only divergence of resilience state). A module-level lock or eager init at app startup would remove the race. Cosmetic at current traffic.
- **O3 (Info):** Delay-seconds parsing caps at 10 digits; an 11-digit `Retry-After` falls back to jittered backoff (retry) while a parseable above-cap value (e.g., `"600"`) aborts typed. Asymmetric but defensible — unparseable header data is ignored per RFC-9110-tolerant handling; noting for the record.
- **O4 (Info):** The per-analysis budget is not yet wired into the route (route calls the fetcher without a budget); this matches the module docstring ("analysis-run machinery arrives with M2") and the packet's scope — S6 governs the layer, and the typed failure + zero-upstream guarantee are fully proven. Follow-up belongs to the M2 analysis-run task.

## Verdicts

Every packet scenario S1–S8 is genuinely proven by deterministic, injected-clock/seeded-RNG tests asserting transport call counts, exact sleep sequences, and emitted metrics events — no tautological or mocked-away proofs found. All six reviewer probes at untested boundaries passed. The diff is in scope, additive, dependency-free, leaves every pre-existing test untouched and green (264/264, ruff clean), and preserves provenance and the route's status/state contract.

G3: PASS
G4: PASS
