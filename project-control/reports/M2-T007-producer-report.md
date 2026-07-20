# M2-T007 Producer Report — GIS Zoning Features connector (ArcGIS, six canonical DCP layers)

- **Task ID:** M2-T007
- **Producer:** backend-engineer (worktree `.claude/worktrees/M2-T007`, branch `task/M2-T007-zoning-features-connector`)
- **Status requested:** `awaiting_gate`
- **Date:** 2026-07-20 (UTC; fixture capture timestamps 2026-07-20T03:07:55Z through 03:08:01Z)
- **Report path:** `project-control/reports/M2-T007-producer-report.md`

## 1. Summary

Implemented the fixture-driven, deterministic, offline-testable connector for the six canonical DCP_GIS ArcGIS zoning-feature services (`nyzd`, `nyco`, `nysp`, `nysp_sd`, `nylh`, `nyzma`) at `services5.arcgis.com/GfwWNkhOj9bNBqoJ`, with endpoint allowlisting, metadata validation, mandatory explicit paging, M1-T009 resilience reuse, a 32-fixture provenance-manifested fixture pack (19 live-captured raw + 13 labeled synthetic), separate raw/canonical-normalized digests, the owner two-staleness rule, and 80 new offline tests. Full api suite: **356 passed** (276 pre-existing + 80 new), ruff clean. No contracts, profile, resilience framework, workflows, or existing connector files were modified.

## 2. Files changed (all new except the one allowed registry draft)

| Path | Change |
|---|---|
| `services/api/app/connectors/zoning_features_arcgis.py` | NEW — connector module (allowlist, metadata validation, paging, error taxonomy, digests, `ResilientZoningFeaturesClient`) |
| `services/api/tests/connectors/test_zoning_features_arcgis.py` | NEW — 80 tests covering ZF-S1..S13 |
| `services/api/tests/fixtures/zoning_features/` (35 files) | NEW — 32 `ZF*.json` fixtures + `MANIFEST.json` + `build_fixture_pack.py` (committed capture/derivation script) |
| `docs/research/source-registry-drafts/zoning-features.json` | UPDATED — `connector_implementation` now IMPLEMENTED with module path; `health_status`; freshness re-observation 2026-07-20 UTC; OQ-11 partially RESOLVED (resultOffset paging verified live; f=geojson still open); OQ-7 partial evidence; error-with-200 behavior recorded |
| `project-control/reports/M2-T007-producer-report.md` | NEW — this report |

NOT modified: `pluto_soda.py`, `bbl.py`, `app/connectors/__init__.py` (no export change needed — existing convention imports connectors by module path), `app/resilience/**`, `app/profile/**`, `packages/contracts/**`, `.github/workflows/**`.

## 3. Contracts / schema changed

**None.** Contract 1.3.0 stands. The connector emits its own result dataclasses (`LayerMetadata`, `LayerCountResult`, `LayerQueryResult`, `LayerExtractResult`); no profile-builder wiring, no persistence, no reprojection, no spatial intersection (packet exclusions honored).

## 4. Design (preserved for resumability)

### 4.1 Module structure

Single module `services/api/app/connectors/zoning_features_arcgis.py`:

1. **Constants:** `SOURCE_ID = "nyc-dcp-zoning-features-arcgis"`; pinned `SERVICE_ROOT`; `EXPECTED_WKID 102718` / `EXPECTED_LATEST_WKID 2263`; `CRS_STAMP`; `EXPECTED_GEOMETRY_TYPE esriGeometryPolygon`; `ZF_CANONICALIZATION_SPEC` (verbatim self-describing digest spec); `LAYER_SPECS` — per-layer live field inventory (name → esri type) + `queryable_fields` allowlist, mirroring fixtures ZF01a–f exactly (test-cross-checked so transcription drift fails the build).
2. **Error taxonomy** (base `ZoningFeaturesConnectorError` with `error_type`, `correlation_id`, `layer`, `detail`, `to_payload()`; no stack traces/headers/tokens in payloads): `upstream_error` (`UpstreamError`: network, 5xx-final, unexpected status, ArcGIS error-object-with-HTTP-200 — distinguished inside `detail` by `arcgis_error_code` vs `http_status` vs `reason_kind`), `malformed_response`, `schema_drift`, `timeout`, `rate_limited`, `disallowed_request`, `paging_pathology` (`detail.reason` in `repeated_object_id | duplicate_page | zero_progress | page_budget_exhausted | count_mismatch`), `budget_exhausted` (`RequestBudgetExceededError`), `circuit_open`. All nine `error_type` strings are distinct (test-asserted).
3. **Allowlisting:** `_require_layer` = exact string match against the six keys, no normalization, raised BEFORE any cache/network work. `build_attribute_where(layer, field, value)` = per-layer field allowlist + value character allowlist `[A-Za-z0-9 .,'()/&+-]{1,120}` + SQL quote doubling. `_require_known_where` re-validates any where string as either `1=1` or a reproducible bounded filter. `build_query_url` bounds `outFields` (must be `*` or known field names), `orderByFields` (known field), `resultRecordCount` (1..2000), `resultOffset` (0..1,000,000). All URLs originate from the pinned root; byte-identical to the capture URLs (test-asserted against fixture `request_url`).
4. **Transport & retry:** reuses the hardened M1-T002 transport (`urllib_transport`, `TransportResponse/Timeout/Failure` imported READ-ONLY from `pluto_soda` — bounded 10 MiB body read, refused redirects). `_request_with_retry` is the SINGLE retry authority: bounded attempts; retry only on 429/5xx/timeout/network; 429 honors `Retry-After` EXACTLY via `parse_retry_after` (M1-T009), aborting typed when it exceeds the cap (never blocks a thread); otherwise full-jitter `backoff_delay` from the injected seeded RNG; one `AnalysisBudget` unit consumed per upstream ATTEMPT before I/O.
5. **Metadata validation** (`fetch_layer_metadata`): parse (`malformed_response` on non-JSON/non-object; `upstream_error` on error object); then typed `schema_drift` on: `name` mismatch vs canonical layer, missing/unsafe `objectIdField`, missing fields array, missing expected field (covers renames), re-typed field, wrong `geometryType`, wrong/missing spatial reference (must be wkid 102718 + latestWkid 2263), missing/invalid `maxRecordCount`, lost `supportsPagination`/`supportsOrderBy`. ADDED fields → visible drift signal `added_field:<name>` (typed degradation, non-fatal). Missing `editingInfo.dataLastEditDate` → drift signal `missing_editing_info` (provenance-only, non-fatal); present value converted to RFC3339 alongside raw ms.
6. **Paging algorithm** (`extract_layer`): request sequence = metadata → count (`returnCountOnly`) → pages. `page_size = min(caller page_size, maxRecordCount)` (default `maxRecordCount`). Page URL: `where=1=1&outFields=*&orderByFields=<objectIdField> ASC&resultRecordCount=<page_size>&resultOffset=<collected-so-far>&f=json`. Loop guards, each a typed `paging_pathology`: page budget `min(max_pages or ceil(count/page_size)+2, 200)` checked BEFORE each request; empty page with `exceededTransferLimit=true` → `zero_progress`; page OID list identical to previous page → `duplicate_page`; any OID overlap with already-collected → `repeated_object_id`; final `extracted != count` → `count_mismatch` (never silently incomplete or inflated). Termination: short page without `exceededTransferLimit`, or collected ≥ count. Non-monotonic in-page order → drift signal `unordered_page:<i>` (normalization sorts deterministically anyway). count=0 → valid empty extraction with zero page requests. Page envelope validation: `features` key required (well-formed empty array IS a valid empty result), `objectIdFieldName` must match validated metadata, page `spatialReference` must be 2263 when present (absent-with-features → drift signal; live services omit it only on empty results, fixture ZF05), integer OID required per feature, unknown attribute names → drift signals.
7. **Digests:** `raw_body_digest` = sha256 over the exact UTF-8 bytes of each response body (metadata, count, and per page — kept as separate fields). `normalized_digest` = `canonical_json_digest` (reused from pluto: sorted keys, `,`/`:` separators, ensure_ascii=False) of the normalized feature list (sorted ascending by object id; each `{object_id, attributes verbatim, geometry verbatim-or-null}`; no value coercion, no reprojection). Spec text carried on every result as `digest_canonicalization`.
8. **`ResilientZoningFeaturesClient`** (M1-T009 primitives composed — no second resilience system): `TTLCache` (versioned key `<cache_key_version>:<SOURCE_ID>:<layer>:extract:page_size=<n>`), one per-source `CircuitBreaker`, LKG store (bounded, age-capped), `ResilienceConfig`/`ResilienceMetrics`; layer allowlist checked BEFORE cache. Cache hit → deepcopy + `staleness {served_from_cache: true, stale: false, original_retrieved_at, age_seconds}`. Breaker open → LKG serve or typed `circuit_open`. Transient-final failure (`rate_limited`/`timeout`/network/5xx) → breaker failure + LKG serve (staleness `{served_from_cache: true, stale: true, upstream_error_type, original_retrieved_at, age_seconds}` + human note `served_from_last_known_good:`) or the original typed error. Non-transient (drift/malformed/paging/ArcGIS-error-object/disallowed) → raised, never masked by LKG. `budget_exhausted` never masked.
9. **Two-staleness rule:** `staleness` is stamped ONLY by the resilient client on cache/LKG serves; every fresh retrieval leaves it `None`. `source_data_last_edited(_ms)` is provenance copied verbatim on every serve path and never influences the staleness stamp.

### 4.2 Key decisions / deviations to disclose

1. **Retry authority consolidated in the connector** (not split connector-retry + wrapper-retry as in the pluto/M1-T009 pair): `_request_with_retry` uses the M1-T009 `backoff_delay`/`parse_retry_after` primitives directly; the resilient client passes `ResilienceConfig` values through and adds cache/breaker/LKG/metrics only. One retry loop, no double sleeps. Reason: paging makes per-request retry the only correct granularity (re-running a whole multi-page extraction on one page's 429 would waste budget and traffic).
2. **Read-only reuse of `pluto_soda` exports** (`urllib_transport`, `TransportResponse/Timeout/Failure`, `canonical_json_digest`): avoids duplicating the G5-hardened transport (bounded read, refused redirects) and the canonical digest helper. `pluto_soda.py` itself is untouched; `app/connectors/__init__.py` untouched (no export-list convention exists for connectors).
3. **`paging_pathology` added to the packet's eight-state taxonomy** (packet allows naming to follow existing conventions; the eight required states remain distinct and test-asserted). Page-budget exhaustion is a `paging_pathology` reason; the resilience `AnalysisBudget` exhaustion is the separate `budget_exhausted` type.
4. **ArcGIS 429 body shape is synthetic** (ZF101): cannot be triggered politely against the official service; transport-level 429 handling is body-independent.
5. **`f=json` only.** `f=geojson` (research OQ-11 second half) deliberately not exercised; registry records it as still open.
6. **nyzd metadata fixtures are ~98–106 KB** (large drawingInfo renderer with one symbol per zoning class). Still KB-scale JSON; total fixture pack ~700 KB.

## 5. Acceptance scenarios — coverage map (ZF-S1..S13 → tests)

All tests in `services/api/tests/connectors/test_zoning_features_arcgis.py`; offline, no network.

| Scenario | Tests (prefix `test_`) | Result |
|---|---|---|
| ZF-S1 schema snapshot x6 + 3 negatives | `s1_metadata_snapshot_validates_all_six_layers[6x]`, `s1_all_six_data_last_edited_decode_to_2026_07_01`, `s1_metadata_negatives_fail_typed[3x]` (ZF90 missing objectIdField, ZF91 wrong CRS, ZF92 missing maxRecordCount) | PASS |
| ZF-S2 count baseline x6 + consistency | `s2_count_baselines_with_provenance[6x]` (5416/9623/95/336/14/1414), `s2_cap_exceedance_hazard_is_real_in_fixtures`, `s2_count_malformed_body_is_typed_not_zero`; count-vs-page-total in `s4_*` and `s5_count_mismatch_*` | PASS |
| ZF-S3 single-feature query | `s3_single_feature_query_nyzd_r3_2` (attrs + rings + CRS + endpoint + retrieval + dataLastEditDate stamps), `s3_url_builder_reproduces_captured_query_url`, `s3_nyzma_date_field_preserved_verbatim` | PASS |
| ZF-S4 paging complete extraction | `s4_paged_extraction_complete_no_skip_no_duplicate` (nylh 3 real pages, OIDs 1..14, URL sequence byte-identical to capture, exactly 5 requests), `s4_exceeded_transfer_limit_respected_across_boundaries` | PASS |
| ZF-S5 paging pathologies | `s5_paging_pathologies_fail_typed[3x]` (duplicate_page ZF96, repeated_object_id ZF97, zero_progress ZF98), `s5_page_budget_exhaustion_bounds_requests` (test-enforced request bound), `s5_count_mismatch_is_typed_never_silent` | PASS |
| ZF-S6 empty vs malformed | `s6_well_formed_no_match_is_valid_empty_result` (live ZF05), `s6_empty_layer_count_zero_makes_no_page_requests`, `s6_malformed_page_is_typed_never_empty_result[2x]` (ZF99 truncated, ZF100 missing features key), `s6_feature_without_object_id_is_malformed` | PASS |
| ZF-S7 error-with-HTTP-200 | `s7_live_captured_error_with_http_200_is_upstream_error` (ZF06 LIVE: HTTP 200 + error.code 400), `s7_error_envelope_variant_and_metadata_path` (ZF102) | PASS |
| ZF-S8 resilience | `s8_timeout_persists_to_typed_timeout_with_bounded_retries`, `s8_429_retry_after_honored_exactly_then_success` (sleep == [7.0]), `s8_429_persisted_is_typed_rate_limited`, `s8_retry_after_beyond_cap_fails_typed_without_blocking`, `s8_network_failure_persists_to_typed_upstream_error`, `s8_request_budget_exhaustion_is_typed_and_pre_io`, `s8_circuit_open_is_typed_and_makes_no_upstream_call`, `s8_last_known_good_serve_stamps_transport_staleness_truthfully`, `s8_error_taxonomy_states_are_distinguishable` | PASS |
| ZF-S9 schema drift | `s9_renamed_field_fails_typed_never_guessed` (ZF93), `s9_added_field_is_visible_typed_degradation` (ZF94), `s9_added_field_signal_propagates_into_extraction_result`, `s9_response_object_id_field_mismatch_is_drift`, `s9_retyped_field_fails_typed` | PASS |
| ZF-S10 determinism | `s10_extraction_digests_reproduce_across_runs` (+ hardcoded cross-platform anchor `sha256:aa48af94d1c66d8ab567107b454cd307da8a15313f32efcfdccc23fbae54c947`), `s10_normalized_digest_is_independent_of_response_order` (shuffled-fixture proof: same normalized digest, different raw digest), `s10_raw_and_normalized_digests_are_kept_separately`, `s10_manifest_digests_match_committed_fixture_bytes` (manifest integrity over all 32 fixtures) | PASS |
| ZF-S11 allowlist security | `s11_non_allowlisted_layer_refused_before_network[8x]` (traversal, absolute URL, view-service name, case, whitespace, empty, None, int — zero transport calls), `s11_resilient_client_refuses_before_cache_and_network`, `s11_bounded_where_refuses_unsafe_input[8x]`, `s11_quote_in_value_is_escaped_not_injected`, `s11_out_fields_and_paging_parameters_are_bounded`, `s11_every_built_url_targets_the_pinned_official_root`, `s11_no_tokens_or_secrets_in_requests_fixtures_or_manifest` | PASS |
| ZF-S12 two-staleness | `s12_old_source_with_fresh_retrieval_is_not_stale` (ZF95: 2020-01-01 source + fresh retrieval → `staleness is None`), `s12_old_source_fresh_retrieval_via_resilient_client`, `s12_cache_hit_serve_does_not_alter_source_timestamps`, `s12_lkg_serve_preserves_source_timestamps_and_flags_transport` | PASS |
| ZF-S13 regression | full suite 356 passed (section 6); `s13_no_pluto_module_state_is_modified`, `s13_correlation_id_minted_when_absent` | PASS |

## 6. Commands run — exact outputs (producer self-check, G2)

Environment: Windows 11, Python 3.11.9 (worktree sandbox), ruff 0.9.9. Note: `pyproject.toml` targets py312; CI runs 3.12 — no 3.12-only syntax is used and the suite passes on 3.11 locally.

```
cd .claude/worktrees/M2-T007/services/api

> python -m pytest tests/connectors/test_zoning_features_arcgis.py -q
80 passed in 0.48s

> python -m pytest tests -q          (before registry/date edits)
356 passed in 5.70s

> python -m pytest tests -q          (final state)
356 passed in 4.06s

> python -m ruff check .
All checks passed!

> python tests/fixtures/zoning_features/build_fixture_pack.py capture
wrote ZF01a_meta_nyzd.json (98206 bytes) ... wrote MANIFEST.json (19 fixtures)

> python tests/fixtures/zoning_features/build_fixture_pack.py derive
wrote ZF90_... through ZF102_... ; wrote MANIFEST.json (32 fixtures)

> python -c "json.load(open('docs/research/source-registry-drafts/zoning-features.json'))"
registry JSON valid
```

Expected vs actual: pre-existing suite was 276 tests, expected to stay green — actual 356 total passed (276 + 80 new), zero failures, zero skips. Ruff clean over the whole `services/api` package.

## 7. Source / API evidence — fixture capture log

Live capture: 19 raw fixtures, single bounded KB-scale GET each, keyless (only header sent: `Accept: application/json`), by this producer via `build_fixture_pack.py capture` on 2026-07-20 UTC. Exact request URL is recorded inside each fixture (`request_url`) and in `MANIFEST.json`; digests are sha256 over the exact UTF-8 bytes of `response_body_raw`.

| Fixture | Class | Retrieved (UTC) | sha256 (prefix) |
|---|---|---|---|
| ZF01a_meta_nyzd.json | raw | 2026-07-20T03:07:55Z | 7b126c00046a0eee |
| ZF01b_meta_nyco.json | raw | 2026-07-20T03:07:56Z | f2223216b7765341 |
| ZF01c_meta_nysp.json | raw | 2026-07-20T03:07:56Z | 594897e7d4199626 |
| ZF01d_meta_nysp_sd.json | raw | 2026-07-20T03:07:57Z | bb26678adf8b9306 |
| ZF01e_meta_nylh.json | raw | 2026-07-20T03:07:57Z | 6172069c8ebb6253 |
| ZF01f_meta_nyzma.json | raw | 2026-07-20T03:07:58Z | aa61e70af8ba6553 |
| ZF02a_count_nyzd.json (5416) | raw | 2026-07-20T03:07:55Z | c7e3f02e5932b327 |
| ZF02b_count_nyco.json (9623) | raw | 2026-07-20T03:07:56Z | 24d66015192014c1 |
| ZF02c_count_nysp.json (95) | raw | 2026-07-20T03:07:57Z | 19659dee1004cf06 |
| ZF02d_count_nysp_sd.json (336) | raw | 2026-07-20T03:07:57Z | f64f449f422f4f27 |
| ZF02e_count_nylh.json (14) | raw | 2026-07-20T03:07:58Z | d086d346fbb21cce |
| ZF02f_count_nyzma.json (1414) | raw | 2026-07-20T03:07:58Z | 9175d53271f72ffe |
| ZF03_query_nyzd_single_R3-2.json | raw | 2026-07-20T03:07:59Z | 0971e3d825d962ba |
| ZF04a_page_nylh_offset0.json | raw | 2026-07-20T03:07:59Z | 4cac70ec7a2cc4ad |
| ZF04b_page_nylh_offset6.json | raw | 2026-07-20T03:08:00Z | 60587eaa68775e78 |
| ZF04c_page_nylh_offset12.json | raw | 2026-07-20T03:08:00Z | 30d8f8ee3eaa589d |
| ZF05_query_nyzd_nomatch_XX.json | raw | 2026-07-20T03:08:00Z | 437b1d00810278f6 |
| ZF06_arcgis_error_bad_field.json | raw | 2026-07-20T03:08:01Z | 082b5a4372eb60c1 |
| ZF07_query_nyzma_single.json | raw | 2026-07-20T03:08:01Z | 53ed84d831069e95 |

Synthetic fixtures ZF90–ZF102 (13 files) are derived offline from the raws by `build_fixture_pack.py derive`, labeled `"classification": "synthetic"` with `derived_from`, and never presented as official data. Full 64-hex digests for all 32 fixtures: `services/api/tests/fixtures/zoning_features/MANIFEST.json` (integrity re-verified on every test run by `test_s10_manifest_digests_match_committed_fixture_bytes`).

Key live findings recorded:

1. **OQ-11 (paging) RESOLVED for resultOffset:** all six layers advertise `advancedQueryCapabilities.supportsPagination=true` and `supportsOrderBy=true`; `resultOffset`+`resultRecordCount`+`orderByFields` verified live on nylh — 3 pages (6/6/2 OIDs 1–14), `exceededTransferLimit: true` on partial pages, key ABSENT on the final page. `f=geojson` remains unexercised (still open).
2. **Error-with-HTTP-200 verified live (ZF06):** invalid field query returned HTTP **200** with `{"error":{"code":400,"message":"Cannot perform query. Invalid query parameters."...}}` — exactly the packet's hazard.
3. **Freshness/counts unchanged vs research:** all six `dataLastEditDate` raw ms values and all six counts identical to the 2026-07-16 G1 observations (source last edited 2026-07-01; no monthly boundary crossed).
4. **Empty result shape (ZF05):** empty `features` responses omit `spatialReference`/`fields`/`geometryType` — connector treats page SR as required-when-features-present only.
5. **nyzma (ZF07):** `EFFECTIVE` can be null even on a STATUS `Adopted` record (OQ-7 partial evidence).

## 8. Assumptions and defaults

1. Page ordering uses `orderByFields=<objectIdField> ASC` (server-side) + client-side re-sort; server order violations are drift-signaled, not fatal, because normalization is order-independent.
2. `HARD_MAX_PAGES = 200` absolute ceiling (largest live layer nyco needs 5 pages at cap 2000; 200 is generous headroom, still a hard bound).
3. Default page budget = `ceil(count/page_size) + 2` slack (one extra request can occur when the final page is exactly full).
4. `ResilienceConfig` defaults reused verbatim (15-min TTL, 24-h LKG age, threshold 5, etc.); a zoning-specific tuning pass can ride a later task — values are env-overridable via `RESILIENCE_*` already.
5. Missing `editingInfo` treated as provenance degradation (drift signal + null source timestamps), not fatal, because the payload data itself is still fully validated.
6. Attribute values are preserved verbatim (incl. `EFFECTIVE` epoch-ms/null); no value normalization beyond structural ordering — normalization of dates to RFC3339 is applied only to the layer-level `dataLastEditDate` provenance stamp (raw ms kept alongside).

## 9. Known limitations

1. `f=geojson` support untested (OQ-11 residue, recorded in the registry draft).
2. ArcGIS 429 body/headers shape is assumed-typical (synthetic ZF101); transport handling is body-independent, and Retry-After handling follows RFC 9110 via the shared M1-T009 parser.
3. No persistence, no PostGIS import, no profile wiring — explicitly out of scope (B-001 stands); the registry draft names the follow-up worker plan.
4. The resilient client caches by `(layer, page_size)`; two callers using different page sizes cache separately (correct but worth knowing for the future import worker).
5. Live fixture bodies pin the July 2026 release; after the next "last Monday of the month" refresh, live counts/edit dates will differ from fixtures (tests are offline so CI is unaffected; re-capture is a deliberate act via the committed script).
6. Producer sandbox ran Python 3.11.9 (project targets 3.12); no 3.12-only features used; CI will re-prove on 3.12.

## 10. Security / provenance impact

- **SSRF surface:** none added — six pinned service roots, exact-match layer allowlist, bounded parameters, no caller URLs; refusal is typed and pre-network (test-proven with zero transport calls).
- **Secrets:** the services are keyless; no token handling exists; requests carry only `Accept`; fixtures/manifest scanned (test-asserted) for credential material.
- **Injection:** where-values are character-allowlisted + quote-escaped; untrusted upstream text (error messages, field names, Retry-After) is allowlist-or-repr sanitized before entering payloads/logs (pluto G5 F4 policy); metrics hook JSON-encodes fields.
- **Provenance:** every result carries endpoint URLs, layer, retrieval timestamp, source edit timestamp (ms + RFC3339), CRS stamp, counts, and separate raw/normalized digests with the self-describing canonicalization spec. Two-staleness rule enforced and test-proven in both directions.
- **Bounded resources:** 10 MiB response cap (reused transport), bounded page budgets, bounded cache/LKG stores, KB-scale fixtures (~700 KB pack total) — low-storage policy respected; no datasets downloaded.

## 11. New risks / dependencies

1. Coupling: this module imports transport/digest helpers from `pluto_soda` — a future refactor extracting them into a shared `connectors/_transport.py` would be cleaner (recommended, additive).
2. The monthly source refresh will eventually make the registry's "counts identical" note historical; the freshness monitor task (existing plan) owns that.

## 12. Recommended next tasks

1. M2-T008 (owner-ordered next connector wave item).
2. Follow-up: Render worker persisting paged extractions into PostGIS geometry tables + Supabase Storage raw-page snapshots (registry `connector_implementation` REMAINING PLAN; unblocks split-lot geometry work).
3. Additive refactor: shared connector transport module (see 11.1).

## 13. G2 self-check declaration

All 13 packet acceptance scenarios have executable, passing, offline tests; the full api suite is green (356 passed); ruff is clean; no forbidden path was touched; fixture provenance is manifested with digests; live capture used exactly 19 bounded keyless requests against the official services plus the pre-capture probes (2 metadata/page probes and 1 connectivity probe, all KB-scale GETs to the same official services). This report does not self-accept the task; independent gates (G1 data-contract, G3 code review, G5 security) are requested.
