# M2-T011 Producer Report — Shared connector transport/retry consolidation + canonical source access registry

- **Task ID:** M2-T011
- **Producer:** backend-engineer (isolated worktree `.claude/worktrees/agent-acf9b40e50546a750`, branch `worktree-agent-acf9b40e50546a750`)
- **Status requested:** `awaiting_gate`
- **Date:** 2026-07-20
- **Report path:** `project-control/reports/M2-T011-producer-report.md`

## 1. Summary

Deliverable 1 (consolidation): the transport primitives (M1-T002) and the transport retry loop previously
duplicated across the four accepted connectors now live in ONE shared module,
`services/api/app/resilience/transport.py`. Each connector keeps a thin `_request_with_retry` wrapper with
its exact accepted signature; all connector-specific semantics (error classes, messages, SODA 400
schema-drift classification, layer tagging, sanitizers, log labels) stay in the connectors and reach the
shared engine through a hooks seam (`RetryHooks` / `standard_retry_hooks`). Null hypothesis held: all 522
pre-existing tests pass UNMODIFIED (zero diffs to any existing test file); 16 new consolidation tests added
(538 total green). Ruff clean.

Deliverable 2 (registry): `docs/SOURCE_ACCESS_REGISTRY.md` created — canonical per-source access-governance
record for PLUTO SODA, DCP zoning-features ArcGIS (+ FileGDB blob), ZTLDB SODA, MapPLUTO (ArcGIS + bulk),
Geoclient v2, the DOB NOW SODA family (9 records), the DOB legacy/BIS family (12 datasets incl. two
NEVER-CONNECT dispositions), and the Zoning Resolution portal. Every owner-mandated field is populated,
cited from repo evidence, or explicitly marked "none published" / "to verify at G1". The ZoLa non-API
statement and the no-permanence/no-SLA rule are stated as governance rules 1 and 2.

## 2. Files changed (complete list)

| File | Change |
|---|---|
| `services/api/app/resilience/transport.py` | NEW (513 lines): TransportResponse/TransportTimeout/TransportFailure/Transport, NoRedirectHandler + DEFAULT_OPENER, bounded-read urllib transport (now with additive `opener=` kwarg), get_retry_after/sanitize_retry_after, DelayPolicy + `fixed_exponential_delay` (legacy M1-T002 pluto policy) + `jittered_retry_after_delay` (M1-T009 policy), `RetryHooks`, `standard_retry_hooks` factory, `request_with_retry` engine |
| `services/api/app/connectors/pluto_soda.py` | Transport section and retry loop removed; imports + compat seam (`_NoRedirectHandler = NoRedirectHandler`, `_OPENER = DEFAULT_OPENER`, `urllib_transport` wrapper reading `_OPENER` at call time); `_request_with_retry` delegates to shared engine with fixed-exponential policy + custom 400 hook; removed now-shared `_RETRY_AFTER_SAFE_RE`/`_sanitize_retry_after`/`_get_retry_after`. `__all__` unchanged — every existing import path still works |
| `services/api/app/connectors/zoning_features_arcgis.py` | Retry loop + retry-after helpers removed; `_request_with_retry` wrapper via `standard_retry_hooks` (layer tag through `error_kwargs`); transport imports moved from pluto_soda to app.resilience.transport (canonical_json_digest still from pluto_soda) |
| `services/api/app/connectors/ztldb_soda.py` | Same pattern; custom 400 schema-drift hook retained in-module |
| `services/api/app/connectors/mappluto_geometry_arcgis.py` | Same pattern; template-based unexpected-status message |
| `services/api/app/resilience/__init__.py` | Fetcher-composition exports (`BudgetExceededError`, `CircuitOpenError`, `ResilientPlutoFetcher`, `build_default_resilient_fetcher`) now LAZY via PEP 562 `__getattr__` — required to break the new import cycle (fetcher imports pluto_soda; pluto_soda now imports app.resilience.transport). `from app.resilience import X` behavior unchanged (suite green) |
| `services/api/tests/resilience/test_transport_shared.py` | NEW (367 lines, 16 tests): TC-S2 code-shape guards, TC-S3 shared-path semantics, TC-S7 fault matrix |
| `docs/SOURCE_ACCESS_REGISTRY.md` | NEW (203 lines): canonical source access registry |
| `project-control/reports/M2-T011-producer-report.md` | This report |

**Test-file changes, line by line:** NO existing test file was modified. The only test diff is the NEW file
`services/api/tests/resilience/test_transport_shared.py`. (The pluto `_OPENER`/`_NoRedirectHandler`
monkeypatch seams and `urllib_transport.__module__ == "app.connectors.pluto_soda"` were preserved in the
connector precisely so `tests/api/**` (forbidden path) and `tests/connectors/test_pluto_soda.py` needed no
edits.)

## 3. Contracts / schema changed

NONE. No contract files, no `_contract_schemas`, no packages/contracts, no API surface, no config defaults
(retry counts, budgets, breaker thresholds, cache TTLs, staleness typing all untouched — `ResilienceConfig`
not modified).

## 4. Acceptance scenarios (TC-S1..TC-S8): commands, expected vs actual

All commands run from `services/api/` on Windows, Python 3.11.9, pytest 8.4.2, ruff 0.9.9.

### TC-S1 behavior-unchanged (primary)
- Command: `python -m pytest tests/ -q`
- Expected: full existing connector + resilience suites pass with the shared module in place; URL builders
  reproduce MANIFEST capture URLs byte-identically; digest computation unchanged.
- Actual (final run tail):
  ```
  ........................................................................ [ 93%]
  ..................................                                       [100%]
  538 passed in 3.96s
  ```
  Baseline before any change (same command): `522 passed in 17.54s`. 538 = 522 unmodified + 16 new. The
  byte-identical MANIFEST URL rebuild tests and in-test fixture digest re-verification live in the four
  existing connector suites, which are untouched and green. **PASS**

### TC-S2 consolidation proof
- Command: `grep -c "for attempt in range(1, max_attempts + 1)" app/connectors/*.py app/resilience/transport.py`
- Expected: 0 in every connector, exactly 1 shared implementation.
- Actual: `pluto_soda.py:0, zoning_features_arcgis.py:0, ztldb_soda.py:0, mappluto_geometry_arcgis.py:0, transport.py:1`.
  Guarded permanently by `test_s2_retry_loop_exists_only_in_shared_module` and
  `test_s2_all_four_wrappers_use_the_shared_symbols`.
- LOC accounting (disclosed precisely, see limitation L1): tracked app files `+323 −600 = net −277 lines`
  (connector files −294; pluto 1017→910, zf 1903→1836, ztldb 1947→1891, mappluto 2168→2104); new shared
  module +513 lines. Raw repo total therefore +236 for app code; code-only SLOC (tokenize-based, comments/
  docstrings excluded) 4938→4955 (+17, i.e. flat). Four duplicated loop implementations became one. **PASS with disclosure L1**

### TC-S3 resilience-semantics regression
- Command: `python -m pytest tests/resilience/ tests/connectors/ -q` (subset of the full run above; all green).
- Each behavior exercised through the SHARED path:
  - caching / breaker / LKG / typed staleness: existing suites `tests/resilience/test_cache.py`,
    `test_breaker.py`, `test_lkg.py`, `test_staleness.py` and the per-connector resilient-client tests —
    these all now flow through the shared loop (fetcher composes `fetch_by_bbl`, which delegates) — green unmodified.
  - request budgets: existing `test_budget.py` + NEW `test_s3_budget_unit_consumed_before_every_attempt`
    (budget refused BEFORE I/O; transport called exactly `budget` times).
  - Retry-After: existing `test_retry_after.py` + NEW `test_s3_retry_after_delay_seconds_honored_exactly`
    (sleep sequence `[7.0]` verbatim), `test_s3_retry_after_http_date_honored_via_injected_wall_clock`
    (`[30.0]`), `test_s3_retry_after_beyond_cap_stops_retrying_typed` (1 attempt, 0 sleeps).
  - jitter bounds: existing `test_backoff.py` seed-replay + NEW `test_s3_jitter_bounds_and_seed_replay_for_5xx`
    (exact `Random(7)` replay through the shared engine) and
    `test_s3_fixed_exponential_delay_matches_legacy_pluto_sequence` (`[0.5, 1.0]`, no jitter — legacy pluto policy).
- Expected = actual on every assertion. **PASS**

### TC-S4 connector-specific semantics
- Command: `python -m pytest tests/connectors/ tests/profile/ -q` (within the full run).
- SODA omitted-key vs observed-null, split-lot ordering, slash-tie, PARK caveat, condo billing-lot, CRS
  gate, geometry-validity taxonomy tests: all green and UNTOUCHED — not even import-only diffs (zero test
  edits). **PASS**

### TC-S5 registry completeness
- Artifact: `docs/SOURCE_ACCESS_REGISTRY.md`.
- One record per current/researched source (PLUTO SODA; zoning-features ArcGIS + blob; ZTLDB; MapPLUTO
  ArcGIS + bulk; Geoclient v2; DOB NOW family table of 9; DOB legacy table incl. never-connect rows; Zoning
  Resolution portal). All owner-mandated fields present per record: official/endpoint URLs, access mode,
  authentication, published quota ("none published" with the official page cited where that is the fact),
  cadence, freshness signal, schema/file version, terms/attribution links, last policy-verification date,
  outage/LKG behavior, suitability. ZoLa non-API statement = governance rule 1; no-permanence/no-SLA rule =
  governance rule 2. Unevidenced items marked "to verify at G1" (never guessed): MapPLUTO bulk zip URLs
  (nyc.gov 403 bot wall), Geoclient portal quota (visible only after owner sign-in), bulk FileGDB internal
  schema, DOB dictionary XLSX contents. **PASS (self-check); G1 verifies against live pages**

### TC-S6 registry verification (reviewer scenario)
- For the data-contract-verifier: every quota/terms/attribution claim carries its source (official URL +
  the accepted research doc/draft + read date). Spot-verify against live pages per the scenario. Producer
  performed NO new web research (task instruction); the "last policy verification" dates are the dates in
  the accepted evidence chain. **Prepared for G1**

### TC-S7 failure case (simulated transport faults through the shared module)
- Command: `python -m pytest tests/resilience/test_transport_shared.py -q`
- Actual: `16 passed in 0.29s`.
- Direct shared-path faults: timeout burst (typed terminal, attempts=3, 2 sleeps),
  429 burst (typed terminal, attempts/max_attempts in detail), 429+over-cap Retry-After (stop-not-retry),
  unparseable Retry-After (repr-sanitized detail + jitter fallback), 5xx bursts, network-failure reason
  sanitizer passthrough, unexpected status never retried (`{"http_status": 302, "url": ...}` detail).
- Fixture-driven per-connector comparison (`test_s7_connector_fault_matrix_same_typed_outcomes`): the same
  fault scripts driven through `pluto_soda.fetch_by_bbl`, `ztldb_soda.fetch_by_bbl`,
  `zoning_features_arcgis.fetch_layer_metadata`, `mappluto_geometry_arcgis.fetch_layer_metadata` produce
  the ACCEPTED typed outcomes: timeout→`timeout`, 429-over-cap→`rate_limited`, 5xx-burst→
  `source_unavailable` (pluto, accepted M1-T002 taxonomy) / `upstream_error` (M2-wave connectors). **PASS**

### TC-S8 regression (repository CI)
- Local proxy run (CI runs the same commands per `.github/workflows/ci.yml` api job):
  - `ruff check .` → `All checks passed!`
  - `python -m pytest tests/ -q` → `538 passed in 3.96s`
- Full CI on both events is executed by the orchestrator after integration (out of producer authority). **PASS locally; CI pending orchestrator**

## 5. Source / API evidence for registry rows (repo citations)

| Registry section | Evidence in repo |
|---|---|
| Governance rule 5 (Socrata baseline) | `docs/research/source-registry-drafts/pluto-mappluto.json` (E7, dev.socrata.com/docs/app-tokens read 2026-07-16); M1-T001 G1 |
| 1 PLUTO | `source-registry-drafts/pluto-mappluto.json` record 1; `docs/research/pluto-mappluto-2026-07-16.md`; fixtures F07/F08/F13 |
| 2 Zoning features | `source-registry-drafts/zoning-features.json` (both records); `docs/research/zoning-features-ztldb-2026-07-16.md` (Z6-Z13); fixtures ZF01a-f/ZF04a-c/ZF06/ZF07 |
| 3 ZTLDB | `source-registry-drafts/ztldb.json`; same research doc (Z2-Z5); fixtures ZT07b/ZT08/ZT09 |
| 4 MapPLUTO | `source-registry-drafts/pluto-mappluto.json` records 2-3; fixture MPG01_meta.json (2026-07-20) |
| 5 Geoclient | `docs/research/M0-T002-geoclient-address-resolution.md` (sections 2.2-2.4, 12; read dates 2026-07-14) — rate limits explicitly "none published on unauthenticated pages"; third-party figure recorded as UNVERIFIED |
| 6 DOB NOW | `source-registry-drafts/dob-now.json` (all 9 records); `docs/research/M1-T007-dob-now-sources.md` |
| 7 DOB legacy | `docs/research/dob-legacy-sources.md` (sections 2-8; committed probe logs and fixtures listed there) |
| 8 Zoning Resolution | `source-registry-drafts/zoning-resolution.json`; `docs/research/zoning-resolution-2026-07-16.md` (E3-E17 + G1 corrections C1-C9) |
| ZoLa statement | Owner directive in the task packet; corroborating repo mention: `docs/research/M0-T002-geoclient-address-resolution.md` line 136 (ZoLa described as a web app). Statement is a governance rule, not a sourced technical claim |

## 6. Assumptions and defaults

- A1: "Transport + retry loop" scope = the four `_request_with_retry` implementations, the transport
  primitives, and the duplicated Retry-After capture helpers. The per-connector RESILIENT COMPOSITION
  classes (`ResilientPlutoFetcher`, `ResilientZoningFeaturesClient`, `ResilientZtldbFetcher`,
  `ResilientMapPlutoGeometryClient`) with their breaker/cache/LKG/staleness logic were accepted per
  connector and are deliberately NOT consolidated here (behavior-drift risk; not named by the packet).
- A2: Shared module home chosen as `app/resilience/` (packet allowed either home); required the lazy
  `__init__` change described above.
- A3: The registry's "last policy verification" dates are the accepted research read dates (the task
  forbids re-researching the web); TC-S6 gives G1 the live re-verification role.

## 7. Known limitations and disclosed deviations

- **L1 (LOC):** Duplicated code was eliminated (net −277 lines in tracked app files; −294 in the four
  connectors; code-only SLOC flat at +17), but the RAW repository line count for app code rose by +236
  because the single shared module carries the consolidated implementation plus its provenance-style
  documentation (513 lines, ~44% docs/comments). The packet expected "net LOC reduction"; on the raw-total
  metric this was not achieved and I am disclosing it rather than stripping documentation. Every future
  connector now costs a ~30-line declarative hooks config instead of a ~120-line loop copy.
- **L2 (micro-behavior, disclosed per null-hypothesis rule):**
  1. pluto's old `_get_retry_after` iterated `headers.items()` unguarded; the shared `get_retry_after` is
     the defensive variant used by the other three (returns None if `.items()` is absent). Reachable only
     by a hand-built TransportResponse whose `headers` is not a mapping; no such caller/test exists.
  2. zf/mappluto previously constructed a fresh `{"Accept": "application/json"}` dict per attempt; the
     shared loop passes the same dict each attempt. Observable only to a transport that mutates its
     `headers` argument; none exists.
  3. Log RECORD format strings changed from literal prefixes ("pluto_soda timeout url=…") to "%s timeout
     url=…" with the label as the first arg — RENDERED messages and logger names are byte-identical; only
     `LogRecord.msg` differs. No test asserts `record.msg`.
  4. `TransportResponse`/`TransportTimeout`/`TransportFailure` are now DEFINED in
     `app.resilience.transport` and re-exported by `pluto_soda` — single class identity everywhere
     (isinstance behavior unchanged); `__module__` of these classes changed. `pluto_soda.urllib_transport`
     remains a pluto-module function (`__module__` guard test in the mappluto suite passes) and still reads
     `pluto_soda._OPENER` at call time (monkeypatch seam preserved).
  5. zf/ztldb/mappluto default transports now bind the shared `urllib_transport` (same DEFAULT_OPENER
     instance) instead of pluto's wrapper; patching `pluto_soda._OPENER` never affected those three in any
     test and still affects the pluto path exactly as before.
  6. `app.resilience` fetcher exports are lazy (PEP 562); `from app.resilience import ResilientPlutoFetcher`
     etc. unchanged (green), but `dir(app.resilience)` no longer lists the four names without access.
- **L3:** TC-S8's "CI green on both events" and TC-S6's live-page spot-verification are orchestrator/
  reviewer actions and are pending by design.
- **L4:** Registry rows for DOB dictionary XLSX contents, MapPLUTO bulk zip URLs (nyc.gov 403 wall),
  Geoclient portal quota, and Geoservice registration remain "to verify at G1"/human-session items exactly
  as the accepted research left them — not producible without new web access or owner credentials.

## 8. Security / provenance impact

- No new external calls, no credentials, no new logging of sensitive data. All G5-accepted hardening moved
  verbatim: bounded body read (F1), refused redirects incl. the X-App-Token exfiltration rationale (F3),
  Retry-After/errorCode/network-reason sanitization, token never logged. The app-token header path (ztldb/
  pluto `_build_headers`) is unchanged and stays out of the shared module's knowledge (headers are opaque).
- Provenance: raw/normalized digest computation, capture-URL builders, retrieval timestamps, staleness
  typing untouched (proven by the unmodified suites).
- The registry is a governance document; it introduces no new claims beyond cited accepted evidence.

## 9. New risks / dependencies

- R1: `app.resilience.transport` is now on the critical path of all four connectors — any future edit to it
  is a four-connector blast radius; the 16 shared-path tests plus the four untouched suites are the guard.
- R2: The lazy `__getattr__` in `app/resilience/__init__.py` would hide an ImportError inside fetcher.py
  until first attribute access; route wiring accesses it at app startup, so CI still catches breakage.

## 10. Recommended next tasks

1. G1 (data-contract-verifier): TC-S6 live spot-verification of registry links/dates; byte-identical
   re-fetch proof through the shared path per the packet's G1 note.
2. Follow-up consolidation candidate (owner decision): the four resilient-composition classes share the
   same breaker/cache/LKG/staleness pattern — a second, separately gated consolidation could apply the same
   hooks approach (NOT done here per A1).
3. Fifth-connector tasks (Geoclient after credential; DOB NOW Stage A) should consume
   `standard_retry_hooks` + `request_with_retry` directly — no new loop copies.
4. Registry maintenance rule already embedded: update rows only with cited evidence; ZTLDB stall (OQ-3)
   escalation to DCPOpendata@planning.nyc.gov is an OWNER action (no agency contact made by me).

## 11. Exact command log (final state)

```
cd services/api
ruff check .                     -> All checks passed!
python -m pytest tests/ -q      -> 538 passed in 3.96s
python -m pytest tests/resilience/test_transport_shared.py -q -> 16 passed in 0.29s
grep -c "for attempt in range(1, max_attempts + 1)" app/connectors/*.py app/resilience/transport.py
  -> connectors: 0,0,0,0 ; transport.py: 1
git diff --numstat (services/api/app tracked) -> +323 -600 (net -277); new files: transport.py 513,
  tests/resilience/test_transport_shared.py 367, docs/SOURCE_ACCESS_REGISTRY.md 203
Baseline before changes: python -m pytest tests/ -q -> 522 passed in 17.54s
```
