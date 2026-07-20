# M2-T007 - G3 Independent Walkthrough + G4 Integration Review (code-reviewer)

*(Orchestrator note: saved verbatim from the reviewer's agent-return channel per the report-preservation rule; transport entity-decoding only. This single report backs BOTH the G3 and G4 gate records, which are recorded separately — precedent M2-T006.)*

## 1. Scope and method

- **Review target:** committed state of git worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T007`, branch `task/M2-T007-zoning-features-connector`, commit `4468954547ac68dde8e24f3b3f0ce96e873e863d` (= PR #39). Working tree confirmed clean (`git status --short` empty).
- **Method:** started from the acceptance criteria in `project-control/tasks/M2-T007.json` (safeguards 1-6, ZF-S1..S13, error-taxonomy risk item, allowed/forbidden paths) plus `docs/GATES_AND_CHECKPOINTS.md` G3/G4 and the `docs/ACCEPTANCE_SCENARIO_STANDARD.md` connector pack. Read the full connector (`services/api/app/connectors/zoning_features_arcgis.py`, 1904 lines), full test module (1041 lines), `MANIFEST.json`, `build_fixture_pack.py`, registry draft, and sampled fixture bodies. Re-ran all executable evidence myself from the clean committed worktree. Read the producer report LAST and evaluated its section 4.2 deviations against my own findings.
- **Read-only compliance:** no git/gh writes, no `project_control.py`, no edits outside my own agent-memory. I did not run `gh` (per gate protocol); CI-green-on-both-events attestation therefore rests with the orchestrator, cited below.

## 2. G3 findings — independent walkthrough

### 2.1 Commands re-run (exact totals, my own execution)

From `<worktree>\services\api`:

| Command | Result |
|---|---|
| `python -m pytest tests/connectors/test_zoning_features_arcgis.py -q` | **80 passed** in 0.94s |
| `python -m pytest tests -q` | **356 passed** in 15.83s (zero failures, zero skips) |
| `python -m ruff check .` | **All checks passed!** |

Matches the producer's claimed 80 / 356 / clean exactly. 356 = 276 pre-existing + 80 new; no existing test was modified (diff shows only additions plus the one allowed registry draft).

### 2.2 End-to-end behavior walkthrough (as a downstream service consumer)

- **Normal:** `fetch_layer_metadata` validates name, objectIdField, full field inventory (name AND esri type), geometryType, CRS 102718/2263, maxRecordCount, supportsPagination/supportsOrderBy before returning; `LAYER_SPECS` constants are cross-checked against the six live-captured fixtures inside `test_s1_metadata_snapshot_validates_all_six_layers` (`meta.fields == LAYER_SPECS[layer].fields`), so constant/fixture transcription drift fails the build — no guessed schema. `query_features` and `extract_layer` stamp endpoint URLs, retrieval timestamp, dataLastEditDate (raw ms + RFC3339), CRS, counts, and separate raw/normalized digests with the self-describing `ZF_CANONICALIZATION_SPEC`.
- **Boundary:** page-boundary exactness proven with three REAL captured nylh pages (6/6/2, OIDs 1..14, `exceededTransferLimit` true on partial pages and absent on the final page — resolving OQ-11 with live evidence, not assumption). count=0 makes zero page requests (test-asserted, 2 transport calls). count==maxRecordCount (nylh 14=14) is safe by the `collected >= expected_count` loop-top break; I traced the loop and no extra request or truncation is possible — though this exact case at default page_size lacks a dedicated test (D3, LOW).
- **Missing/ambiguous:** missing editingInfo degrades to drift signal `missing_editing_info` (non-fatal, correct — data still fully validated); absent spatialReference on empty results is tolerated because the live ZF05 fixture proves the service omits it on empty results (I verified ZF05's body keys directly: no `spatialReference`); SR absent WITH features present becomes drift signal `page_missing_spatial_reference`. Both signals are implemented but untested (D1, LOW).
- **Failure:** all nine taxonomy states (`upstream_error`, `malformed_response`, `schema_drift`, `timeout`, `rate_limited`, `disallowed_request`, `paging_pathology`, `budget_exhausted`, `circuit_open`) are distinct classes with distinct `error_type` strings, asserted pairwise-distinct in `test_s8_error_taxonomy_states_are_distinguishable`. Malformed is never coerced to empty (typed on truncated JSON, missing `features`, non-object feature, missing/non-int OID); error-object-with-HTTP-200 is a typed upstream error distinguishable from transport failure (`arcgis_error_code` vs `http_status`/`reason_kind` in detail — test-asserted).

### 2.3 Scenario-by-scenario verification (all assertions checked non-vacuous)

- **ZF-S1:** 6 positive metadata snapshots + exactly the packet's three negative fixtures (ZF90 missing objectIdField, ZF91 wrong CRS→4326, ZF92 missing maxRecordCount) each raising typed `SchemaDriftError` with payload assertions. Real.
- **ZF-S2:** six count baselines assert the exact packet values (5416/9623/95/336/14/1414), URL reproduction, digest, retrieval timestamp; `test_s2_cap_exceedance_hazard_is_real_in_fixtures` pins the C3 hazard (95>92, 336>317, 1414>1292, 14=14). Malformed count body is typed, never zero.
- **ZF-S3:** single R3-2 feature with OID, attributes, polygon rings verbatim, CRS, endpoint/retrieval/dataLastEditDate stamps, both digests, `staleness is None`. nyzma EFFECTIVE=null preserved, never fabricated.
- **ZF-S4 (no-skip/no-dup proof):** `oids == list(range(1, 15))` across 3 real pages; URL sequence byte-identical to capture URLs; exactly 5 transport calls asserted; per-page raw digests distinct. This is a genuine completeness proof, not a count-only assertion.
- **ZF-S5:** duplicate-page, repeated-OID, and zero-progress fixtures each raise `PagingPathologyError` with the correct `detail.reason`, and `transport.script == []` proves abortion exactly at the bad page. Page-budget test asserts a hard request bound (`len(transport.calls) == 4`). Count-mismatch synthetic (inflated count 15 vs 14 extracted) is typed with exact extracted/expected details — silent truncation and silent inflation are both impossible (the final `len(collected) != expected_count` check catches shortfall from a premature well-formed end-of-data too).
- **ZF-S6:** malformed-never-empty proven with live-shaped ZF99/ZF100 plus feature-missing-OID synthetic; well-formed no-match is a valid empty result with an explicit `empty_result` note.
- **ZF-S7:** error-object-with-200 proven with the LIVE ZF06 capture (fixture asserts `http_status == 200`) on the query path and a second envelope variant on the metadata path.
- **ZF-S8:** timeout (3 attempts, 2 backoff sleeps), Retry-After honored exactly (`sleeps.delays == [7.0]`, no jitter), Retry-After beyond cap fails typed with ZERO sleeps and ONE call (never blocks a thread), persisted 429 typed, network typed, budget exhaustion pre-I/O (`len(transport.calls) == 2`, `budget.consumed == 2`), circuit-open with zero upstream I/O, LKG serve with truthful full staleness dict.
- **ZF-S9:** renamed field fails typed with `missing_fields == ["ZONEDIST"]`; added field is a visible non-fatal signal that propagates into query results; response objectIdFieldName mismatch and re-typed field both typed.
- **ZF-S10:** two-run digest reproduction PLUS a hard-coded cross-platform anchor digest (CI on Linux must reproduce it from committed fixtures); shuffled-fixture proof asserts same normalized digest + DIFFERENT raw digest + re-sorted output — order-independence genuinely proven. Manifest-integrity test re-hashes all 32 fixture bodies against manifest digests on every run and asserts full file/manifest bijection.
- **ZF-S11:** 8 hostile layer values (traversal, absolute URL, view-service name, case, whitespace, empty, None, int) refused with `transport.calls == []` — zero-transport-call refusals verified; resilient client refuses before cache (`cache_miss` count 0); 8 unsafe where inputs refused; quote-escaping proven; outFields/orderBy/count/offset bounds proven including bool-as-int traps; pinned-root assertion; no-token scan over requests, fixtures, and manifest.
- **ZF-S12 (both directions):** old source (2020-01-01) + fresh retrieval → `staleness is None` (plain and client paths); within-TTL cache hit → `{served_from_cache: True, stale: False, ...}` with source timestamps verbatim; LKG serve → `stale: True` caused by the timeout, source timestamps untouched. Owner two-staleness rule enforced in both directions, test-proven.
- **ZF-S13:** full suite green (re-run by me); pluto module-state non-interference asserted.

### 2.4 Clarity, recovery, hidden assumptions

Error payloads (`to_payload`) carry error_type, actionable message, correlation_id, source_id, layer, and bounded detail; untrusted upstream text is allowlist-or-repr sanitized (pluto G5 F4 policy); no stack traces, headers, or tokens (services are keyless — verified: only `Accept` header ever sent, test-asserted). Correlation IDs are caller-supplied or minted (test-asserted). LKG serves carry both the typed staleness object and a human-readable `served_from_last_known_good:` note stating the original retrieval time. I found no hidden defaults that change results silently; the one behavioral default (page_size = maxRecordCount) is the official transfer limit.

### 2.5 Owner-PC storage

Fixture pack directory totals 801,312 bytes (~782 KB; largest file 106 KB — synthetic nyzd metadata negatives carrying the full live drawingInfo body). No downloads, no temp litter, no persistent artifacts outside the repo; tests are offline. Within low-storage policy. (Producer's "~700 KB" is a slight underestimate — observation O2, not a defect.)

## 3. G3 VERDICT: **PASS**

(Defects D1-D3 are LOW, non-blocking test-coverage/cosmetic residuals; see section 6.)

## 4. G4 findings — integration and regression

- **pluto_soda coupling:** read-only reuse of five public names (`TransportFailure`, `TransportResponse`, `TransportTimeout`, `canonical_json_digest`, `urllib_transport`). `pluto_soda.py` is not in the diff (byte-identical to merge-base); import direction is one-way (no cycle). Reusing the G5-hardened transport (bounded 10 MiB read, refused redirects) and the canonical digest is the right call versus duplicating them.
- **No second resilience system / no double-retry:** verified by reading both `app/resilience/fetcher.py` and the new module. Exactly one retry loop exists per call path: `_request_with_retry` (built from M1-T009 `backoff_delay`/`parse_retry_after`); `ResilientZoningFeaturesClient` adds only `TTLCache`, `CircuitBreaker`, LKG, `AnalysisBudget` pass-through, and `ResilienceMetrics` — it never re-retries or sleeps. The disclosed deviation from the pluto pattern (retry authority in the plain functions rather than the wrapper) is sound and better-motivated here: per-request retry is the only correct granularity for multi-page extraction. The staleness dict shape matches the contract-1.3.0 semantics established by the pluto fetcher (consistent, not contradictory). `pluto_soda`'s private `_request_with_retry` pattern is now duplicated per-connector — pattern-level duplication by established convention, with a tracked additive refactor recommendation (producer report §11.1/§12.3); not a contradictory implementation.
- **Regression:** full suite 356/356 green re-run by me from the committed worktree; ruff clean; zero changes to existing tests/fixtures; `packages/contracts/**` and `services/api/app/_contract_schemas/**` untouched (contract 1.3.0 stands, no typegen changes); `app/profile/**`, `app/resilience/**`, `.github/workflows/**`, `.claude/**` untouched. **CI on both events: I did not run gh per the gate protocol; the producer report cites no run URLs, so the orchestrator must attest CI green on PR #39 (both events) when recording the gates.** My local full-suite + ruff re-run is direct evidence for the same tree.
- **Scope:** `git diff --name-status merge-base..HEAD` = 38 files, ALL within the five allowed_paths entries (1 registry draft M, 37 A under connectors/tests/fixtures + own producer report). No forbidden path touched. Exact match.
- **Performance/budgets/determinism:** bounded page budget (`ceil(count/page_size)+2`, hard cap 200), bounded response reads (reused 10 MiB transport), bounded parameters (`resultRecordCount` <= 2000, `resultOffset` <= 1,000,000), bounded LKG/cache stores, per-attempt `AnalysisBudget` consumption BEFORE I/O. Tests are fully deterministic: injected `FakeTransport`, `SleepRecorder` (no real sleeps), `FakeMonotonic`, fixed wall clock, seeded `Random(42)`/`Random(7)` — no wall-clock or sleep flakiness; the 80 tests run in under a second.
- **Fixture provenance (G4 supporting):** MANIFEST.json records official endpoint, layer, query parameters, retrieval timestamp, source edit ms, CRS, expected count, sha256, raw/synthetic classification, `derived_from` lineage, purpose, and supported scenarios for all 32 fixtures; integrity is re-verified by a test on every run. Capture timestamps (2026-07-20T03:07:55Z–03:08:01Z) are consistent with the commit time (2026-07-19 23:25 EDT = 2026-07-20 03:25 UTC). Registry draft honestly discloses the f=geojson residue (OQ-11 still open), OQ-7 partial evidence, and the error-with-200 finding — no silent uncertainty.
- **Producer deviations (§4.2) judged:** (1) consolidated retry authority — sound, verified single-loop; (2) pluto export reuse — sound, read-only, non-circular; (3) `paging_pathology` ninth taxonomy state — permitted by the packet's "names may follow the existing resilience taxonomy" clause, all eight required states remain distinct; (4) synthetic 429 — correctly disclosed, transport handling is body-independent; (5) f=geojson unexercised — correctly recorded as open in the registry, connector pins `f=json`. All five deviations are acceptable and honestly disclosed.

## 5. G4 VERDICT: **PASS**

(Conditional only on the orchestrator's standing CI attestation for PR #39 on both events, per the evidence-capture division of labor; my local full-suite re-run on the same tree is green.)

## 6. Defect list

- **D1 (LOW)** — Implemented drift signals `missing_editing_info` (`zoning_features_arcgis.py:1186`) and `page_missing_spatial_reference` (`zoning_features_arcgis.py:829`) have no test asserting they are emitted. The negative behavior they guard (typed degradation, never silent guessing) is packet safeguard 2 language; the code paths exist and are correct by inspection, but a regression removing either signal would not fail the build. Recheck at next connector touch or the import-worker task.
- **D2 (LOW, cosmetic)** — `test_s9_added_field_signal_propagates_into_extraction_result` (`test_zoning_features_arcgis.py:706-723`) asserts propagation via `query_features`, not `extract_layer` as its name implies, and contains dead code (a page is loaded then `del`eted unused). The assertion itself is real and passes; rename or extend to the extraction path in a future cleanup.
- **D3 (LOW)** — The count==maxRecordCount boundary (nylh 14=14, packet-highlighted) is not directly tested at DEFAULT page_size (all nylh extraction tests use page_size=6). I traced `extract_layer`'s loop and confirmed the `collected >= expected_count` top-of-loop break makes this case safe (single page, no extra request, count-mismatch guard behind it), but a one-line test would pin it.

No MEDIUM/HIGH/CRITICAL defects found.

## 7. Observations / recommendations (non-blocking)

- **O1** — Shared-transport refactor: `_request_with_retry`-style loops now exist in both pluto_soda (private) and this module. The producer's recommended additive `connectors/_transport.py` extraction should be contracted before a third connector (M2-T008) repeats the pattern a third time.
- **O2** — Fixture pack measures ~782 KB on disk vs the report's "~700 KB"; within policy, but the five synthetic nyzd metadata negatives each carry the full ~106 KB drawingInfo body. Future synthetic metadata derivations could strip `drawingInfo` (it is not validated) to keep repo weight down.
- **O3** — `ResilientZoningFeaturesClient` cache key includes `page_size` but not `max_pages`; correct (only successful complete extractions are cached and those are max_pages-independent), noted so the future import worker does not misread it.
- **O4** — The client serves a within-TTL cache hit without consuming `AnalysisBudget` — correct per the packet ("budget exhaustion never masked by cache" refers to the error path, and cache serves cost no upstream I/O), but the import worker should know cached serves are budget-free.
- **O5** — Registry draft update is exemplary provenance practice: OQ-11 split into resolved (resultOffset, live-verified) and still-open (f=geojson) halves rather than blanket-closing the question; the two-channel (ArcGIS vs Socrata blob) freshness-lag disclosure is preserved.
- **O6** — The two-staleness test quartet (ZF95 fresh-old-source, cache-hit, LKG, both client paths) is a strong reference pattern for M2-T008/M2-T009 scenario packs.

Key file paths (worktree root `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T007`):
- `services\api\app\connectors\zoning_features_arcgis.py`
- `services\api\tests\connectors\test_zoning_features_arcgis.py`
- `services\api\tests\fixtures\zoning_features\MANIFEST.json`
- `docs\research\source-registry-drafts\zoning-features.json`
- `project-control\reports\M2-T007-producer-report.md`
- `project-control\tasks\M2-T007.json`
