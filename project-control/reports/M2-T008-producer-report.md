# M2-T008 Producer Report — ZTLDB lot-level zoning connector (SODA fdkv-4t4z)

- **Task ID:** M2-T008
- **Producer agent:** backend-engineer
- **Date:** 2026-07-20
- **Worktree:** `.claude/worktrees/M2-T008`, branch `task/M2-T008-ztldb-connector` (base main f410914)
- **Status requested:** `awaiting_gate`
- **Required gates:** G0 (passed at dispatch), G1, G2 (this report), G3, G4

## 1. Summary

Implemented the fixture-driven per-BBL ZTLDB connector for the official NYC Open Data SODA dataset `fdkv-4t4z` with all six packet safeguards (schema authority, query safety, bounded pagination, domain semantics, source-freshness guard under the owner two-staleness rule, cross-source reconciliation), a resilient client composed from the M1-T009 primitives, a 24-fixture pack (11 raw live captures of 2026-07-20 + 13 labeled synthetics + manifest), 86 new deterministic offline tests (72 connector + 14 cross-check/profile), the completed registry record, and additive cross-check integration into the existing contract-1.3.0 profile machinery. Full api suite: **442 passed** (baseline 356 + 86 new), `ruff` clean. No contract shape changed; no STOP condition was hit.

## 2. Files changed

New:
- `services/api/app/connectors/ztldb_soda.py` — connector module (fetch_by_bbl, fetch_source_freshness, scan_rows, ResilientZtldbFetcher, typed error taxonomy, digests, URL builders, columns-drift check).
- `services/api/app/profile/zoning_crosscheck.py` — cross-source lot-level zoning reconciliation (PLUTO vs ZTLDB vs external fixture-derived observations) emitting contract-1.3.0 conflict entries.
- `services/api/tests/connectors/test_ztldb_soda.py` — 72 tests (ZT-S1..S12, S15, S16 + regression guards).
- `services/api/tests/profile/test_ztldb_crosscheck.py` — 14 tests (ZT-S13, ZT-S14, profile integration, additive-default regression).
- `services/api/tests/fixtures/ztldb/` — `build_fixture_pack.py`, 24 fixtures, `MANIFEST.json` (~104 KB total; KB-scale, low-storage compliant).

Modified:
- `services/api/app/profile/builder.py` — ADDITIVE ONLY: three new optional keyword parameters on `build_property_profile` (`additional_provenance`, `additional_conflicts`, `additional_notes`, all default `None`); provenance/conflicts/connector_notes arrays extended with the extra entries when provided. A regression test proves the default path is byte-identical to the previous behavior. This is the packet-permitted "cross-check/conflict integration ONLY" change; no contract-shape change.
- `docs/research/source-registry-drafts/ztldb.json` — completed/confirmed: connector_implementation now describes the real implementation; staleness re-confirmation (2026-07-20), health status, new observed limitations (blank ZD1 rows live; 203-value ZD1 vocabulary probe; zonemap case difference), OQ-3/OQ-8 status updates.

Existing test files: NONE modified (the cross-check needed no additive assertion in existing files).

## 3. Contracts / schema changed

**None.** Contract 1.3.0 stands. ZTLDB facts are canonical `source_fact` v1 records (required field set complete; additive keys use the same documented open-key pattern as the accepted PLUTO connector). Cross-check conflicts use the existing profile conflict shape (`field`/`values`/`resolution`/`reason`). Profiles built with the integration validate against `property_profile.schema.json` in tests. `packages/contracts/**` and `services/api/app/_contract_schemas/**` untouched. No STOP condition (no version bump, no resilience-framework change, no PLUTO connector change — `pluto_soda.py`, `bbl.py`, `zoning_features_arcgis.py` are read-only imports only).

## 4. Design (preserved for resumption)

### 4.1 Module structure
- `ztldb_soda.py` constants: `SOURCE_ID="nyc-dcp-ztldb-soda"`, `DATASET_ID="fdkv-4t4z"`, pinned `BASE_URL`/`API_VIEWS_URL` on `data.cityofnewyork.us`; `ZTLDB_COLUMN_TYPES` = authoritative 16-column inventory transcribed from the api/views columns array (fixture ZT08; a test cross-checks the constant against the fixture so transcription drift fails the build).
- **Reuse (read-only):** transport (`urllib_transport`, `TransportResponse`, `TransportTimeout`, `TransportFailure`) and `canonical_json_digest` from `pluto_soda`; `normalize_bbl`/`check_identifier_consistency`/`BBLValidationError` from `bbl`; `TTLCache`/`CircuitBreaker`/`AnalysisBudget`/`ResilienceConfig`/`ResilienceMetrics`/`backoff_delay`/`parse_retry_after` from `app.resilience`.

### 4.2 Query construction (safeguard 2)
- `build_record_url(bbl)`: `normalize_bbl` runs FIRST (typed `BBLValidationError`, no network); only the canonical 10-digit form enters the URL: `?bbl=<canonical>&%24order=bbl&%24limit=10` (bounded even though one-row-per-tax-lot). URL-encoded `$` params match the fixture capture URLs byte-identically.
- `build_page_url(limit, offset)`: bounds-checked ints (1..1000 / 0..1,000,000, bool-guarded) else typed `disallowed_request`.
- No caller string ever reaches SoQL; origin + dataset pinned in constants. Optional `SOCRATA_APP_TOKEN` env var (or explicit arg) goes into the `X-App-Token` header only — never logged, never in URLs/payloads/fixtures (negative tests).

### 4.3 fetch_by_bbl flow
1. mint correlation/observation-event ids; validate BBL; resolve app token.
2. If no injected `freshness`: `fetch_source_freshness` first (one metadata request) — this validates the columns snapshot (removed/re-typed = typed `schema_drift`; added = visible `added_column:*` drift signals) and reads `rowsUpdatedAt`.
3. Record request with bounded retry; `retrieved_at` stamped AFTER response.
4. Body parse: invalid JSON / non-array / non-object record = `malformed_response` (never an empty result). Well-formed `[]` = status `no_record` RESULT with explanation + digests. More than 1 record for one BBL = `schema_drift` (uniqueness contract). Record bbl missing/unparseable/mismatched = `schema_drift`.
5. `check_identifier_consistency` against `borough_code`/`tax_block`/`tax_lot` (conflict field names mapped to the ZTLDB column names); conflicting facts marked `conflict_status="conflicting"`, values preserved verbatim.
6. Per-column normalization by official dataTypeName: number columns parsed to int (decimal-zero tails tolerated per M1-T001 C6), `bbl` to canonical string, text verbatim; unparseable = drift signal + verbatim passthrough. Explicit JSON null = distinct OBSERVED-NULL state (fact with normalized None + `observed_null:<column>` observation) — never conflated with omission.
7. Presence states (safeguard 1): every one of the 16 columns is either a fact or an `absences` entry: `not_applicable_per_source_semantics` (with the documented dictionary semantics text) for zd2-4/overlays/specials/limited-height, `absent_undocumented` (unknown, never fabricated) for the rest. `zoning_district_1` absence additionally emits the `zoning_district_1_absent` observation (REAL live state — see 6.3).
8. Domain semantics (safeguard 4) in `zoning_assignment`: ordered district/overlay entries with position = official column index (never resorted; ordering-semantics text embedded); special districts with slash-tie parse (`components`, `tie`, verbatim value preserved, tie semantics verbatim from the dictionary); PARK caveat flag with the official caveat verbatim; zoning-map border-code semantics. Advisory vocabulary observations only: Appendix C overlays, Appendix D limited-height, `Y` map code, open Appendix-B-shape check for districts (`open_set_vocabulary:*` — never rejection/coercion; no closed-set check for special districts because the full Appendix A table is not transcribed in the accepted research and is never guessed).
9. Facts: `source_fact` v1 records; `dataset_version = "socrata-rows-<rowsUpdatedAt RFC3339>"` (the dataset has NO version column; schema requires a non-empty string; the official rows-updated timestamp is the only official version signal — research 5.3); `provenance_id = ztldb-<dataset>-<version>-<bbl>-<column>` (idempotent per dataset-rows-version); stable `fact_key` vs per-event `observation_id`; `value_digest`, `response_digest`, additive `source_rows_updated_at`.

### 4.4 Digests (safeguard 6, `ZT_CANONICALIZATION_SPEC`)
- `raw_digest`: sha256 over exact body bytes (order-sensitive).
- `response_digest`: canonical JSON digest of the PARSED body (key-order/whitespace independent).
- `normalized_digest`: canonical JSON digest of `{bbl, columns (present->normalized), absent_not_applicable, absent_undocumented, observed_null}` — canonical ordering before digesting. Cross-platform anchor for fixture ZT01: `sha256:5ac370992b87ff2da5eeaf883d264b9b30658da0c5bdec555fe4a6482cfc2564` (hard-coded in the test). Shuffled-fixture test proves raw flips while response/normalized digests hold.

### 4.5 Source freshness guard (safeguard 5, owner two-staleness rule)
- `SourceFreshness` frozen dataclass: `rows_updated_at_raw/rfc3339`, `checked_at` (injected clock), `age_days`, `threshold_days=45` (registry-grounded), `source_stale_suspected`, `version_label`, columns drift signals, self-describing `policy` text. Missing/invalid `rowsUpdatedAt` = typed `schema_drift` (guard cannot be silently skipped).
- Stamped into every result as `source_freshness`; `staleness` (transport) stays `None` on every fresh retrieval and is written ONLY by `ResilientZtldbFetcher` (cache hit: `{served_from_cache: true, stale: false, ...}`; LKG: `{..., stale: true, upstream_error_type, ...}` + `served_from_last_known_good:` note). The owner-required regression test drives the full quartet (old/fresh source x fresh/cached/LKG transport) off ONE real metadata fixture with two injected clocks and asserts neither dimension ever writes the other's fields.

### 4.6 Pagination (safeguard 3)
`scan_rows(page_size, max_pages<=50 mandatory)`: deterministic `$order=bbl` pages at `offset=len(collected)`; typed `paging_pathology` reasons `duplicate_page` (identical page), `no_progress` (non-empty page, zero new records), `repeated_record` (partial overlap), `unordered_page` (within-page or cross-page ordering violation — BBLs are fixed-width so lexicographic = numeric), `page_overflow` (more rows than limit), `page_budget_exhausted` (explicit typed stop, never silent truncation). One `AnalysisBudget` unit per upstream attempt, consumed pre-I/O. Full-dataset sync (857,951 rows) remains OUT of scope (owner exclusion).

### 4.7 Error taxonomy (M2-T007-aligned, all distinct, test-asserted)
`upstream_error`, `malformed_response`, `schema_drift`, `timeout`, `rate_limited`, `disallowed_request`, `paging_pathology`, `budget_exhausted`, `circuit_open`; plus the shared `validation_error` (BBLValidationError from `bbl.py`, raised before any I/O). `no_record` is a RESULT status, not an error (asserted). 400 classification: `query.soql.no-such-column` = drift signature (live-captured, fixture ZT10); any other 400 (e.g. `query.soql.type-mismatch`, fixture ZT100) = `upstream_error`, never drift, never retried.

### 4.8 Resilient client
`ResilientZtldbFetcher` mirrors the accepted `ResilientPlutoFetcher`/M2-T007 client: BBL validation before cache; versioned cache key per BBL; breaker fast-reject -> LKG or `circuit_open`; retry params from `ResilienceConfig` passed into the plain function (single retry authority); `_is_transient` = 429/timeout/5xx/network only; LKG stores `status=="ok"` only, age-bounded; `RequestBudgetExceededError` never masked by LKG.

### 4.9 Cross-check integration (safeguard 6 of the packet)
`app/profile/zoning_crosscheck.py`:
- `ZONING_CROSSCHECK_FIELD_MAP`: 12 pairs (zonedist1-4, overlay1-2, spdist1-3, ltdheight, zonemap, zmcode <-> the ZTLDB columns). Conflict `field` uses the PLUTO/profile column name so the EXISTING M2-T004 analysis-readiness gate (critical `zonedist1`) applies unchanged.
- Comparison predicates (documented, never rewriting values): exact match; casefold-equal = `case_only_difference` UNCERTAINTY (real live case: PLUTO `16a` vs ZTLDB `16A`); `zmcode` compared through the documented representation mapping (checkbox true <-> text `Y`, both officially the border flag); value-vs-documented-blank = conflict with the absence and its dictionary semantics stated in the derivation; both-absent = agreement (`no_value_on_any_source`).
- `external_observation(...)` lets callers add fixture-derived observations (ZT-S14 uses the real M2-T007 fixture ZF03 ZONEDIST value) — three-way conflicts list ALL observations; no winner, `resolution` always `unresolved`; refuses cross-property and `no_record` inputs (would fabricate conflicts).
- `CrosscheckReport`: conflicts (contract shape), uncertainties, agreements (positive evidence), notes (contract-safe strings for `reproducibility.connector_notes`).
- Builder integration: `build_property_profile(pluto_result, additional_provenance=ztldb.facts, additional_conflicts=report.conflicts, additional_notes=report.notes)` — appended verbatim; readiness gating via existing machinery (zonedist1 conflict -> `blocked_data_conflict`; overlay1 conflict -> visible, `ready`).

## 5. Scenario coverage map (ZT-S1..S17 -> tests)

All in `tests/connectors/test_ztldb_soda.py` unless marked [crosscheck] = `tests/profile/test_ztldb_crosscheck.py`.

- **ZT-S1:** test_s1_single_lot_maps_the_16_column_contract; test_s1_every_fact_carries_required_source_fact_fields; test_s1_column_type_snapshot_matches_the_committed_metadata_fixture; test_s1_two_records_for_one_bbl_is_typed_schema_drift
- **ZT-S2:** test_s2_split_lot_ordering_preserved; test_s2_ordering_is_never_resorted
- **ZT-S3:** test_s3_valid_bbl_without_row_is_a_typed_no_record_result; test_s3_non_array_body_is_typed_malformed_never_empty; test_s3_truncated_body_is_typed_malformed_never_empty
- **ZT-S4:** test_s4_omitted_keys_map_to_documented_absence_classes; test_s4_observed_explicit_null_is_a_distinct_state; test_s4_absent_zoning_district_1_is_surfaced_never_guessed
- **ZT-S5:** test_s5_overlay_within_appendix_c_yields_no_observation; test_s5_limited_height_within_appendix_d_yields_no_observation; test_s5_outside_vocabulary_is_advisory_observation_never_invention[2 params]
- **ZT-S6:** test_s6_slash_tie_parses_to_two_appendix_a_codes_with_tie_semantics; test_s6_single_special_district_is_not_a_tie
- **ZT-S7:** test_s7_park_carries_the_official_open_space_caveat; test_s7_non_park_lot_does_not_flag_the_caveat
- **ZT-S8:** test_s8_zr_section_number_zd1_is_accepted_as_open_set_observation
- **ZT-S9:** test_s9_two_page_scan_has_no_dupes_or_gaps; test_s9_duplicate_page_is_typed_pathology; test_s9_no_progress_page_is_typed_pathology; test_s9_page_budget_exhaustion_is_typed_never_silent_truncation; test_s9_page_overflow_is_typed_pathology; test_s9_request_budget_is_consumed_pre_io_and_typed; test_s9_scan_bounds_are_enforced
- **ZT-S10:** test_s10_old_source_with_fresh_retrieval_reports_source_age_not_staleness; test_s10_fresh_source_from_an_earlier_vantage_is_not_suspected; test_s10_missing_rows_updated_at_is_typed_schema_drift; test_s10_cache_hit_stamps_transport_staleness_without_touching_source; test_s10_lkg_serve_stamps_stale_transport_and_preserves_source; test_s10_regression_the_two_staleness_dimensions_vary_independently (owner-required regression; covers both client paths per the M2-T007 quartet pattern)
- **ZT-S11:** test_s11_columns_diff_detects_rename_as_removed_plus_added; test_s11_freshness_fails_typed_on_removed_or_retyped_column; test_s11_added_column_is_visible_typed_degradation; test_s11_no_such_column_400_is_the_drift_signature; test_s11_other_400_is_upstream_error_not_drift; test_s11_unknown_record_key_yields_signal_and_no_fact; test_s11_record_bbl_mismatch_is_typed_drift; test_s11_identifier_inconsistency_is_a_visible_conflict_not_a_fix
- **ZT-S12:** test_s12_429_persisted_is_typed_rate_limited; test_s12_retry_after_honored_exactly_then_success; test_s12_retry_after_beyond_cap_fails_typed_without_blocking; test_s12_timeout_persisted_is_typed; test_s12_network_failure_persisted_is_typed_upstream; test_s12_circuit_open_is_typed_and_makes_no_upstream_call; test_s12_budget_exhaustion_is_never_masked_by_lkg; test_s12_error_taxonomy_states_are_distinguishable
- **ZT-S13 [crosscheck]:** test_s13_official_captures_for_the_same_lot_reconcile_cleanly; test_s13_case_only_difference_is_uncertainty_not_conflict; test_s13_split_lot_and_border_flag_mapping_reconcile; test_s13_value_disagreement_is_a_typed_conflict_with_both_sides; test_s13_present_vs_documented_blank_is_a_conflict_with_absence_stated; test_s13_cross_property_comparison_is_refused; test_s13_no_record_ztldb_result_is_refused; plus test_integration_critical_conflict_gates_analysis_readiness / test_integration_noncritical_conflict_stays_visible_without_blocking / test_integration_ztldb_facts_join_provenance_with_full_lineage / test_integration_defaults_leave_existing_builder_behavior_unchanged
- **ZT-S14 [crosscheck]:** test_s14_zoning_features_fixture_value_reconciles_consistently; test_s14_external_disagreement_produces_the_same_typed_conflict_path; test_s14_external_observation_inputs_are_validated
- **ZT-S15:** test_s15_digests_reproduce_across_runs_and_match_the_anchor; test_s15_normalized_digest_is_independent_of_serialization_order; test_s15_any_value_change_flips_the_normalized_digest; test_s15_manifest_digests_match_committed_fixture_bytes
- **ZT-S16:** test_s16_injection_shaped_bbl_rejected_before_any_network[10 params]; test_s16_resilient_fetcher_validates_before_cache_and_network; test_s16_every_built_url_targets_the_pinned_official_dataset; test_s16_app_token_is_header_only_and_never_logged_or_leaked; test_s16_app_token_absent_from_typed_error_payloads; test_s16_fixture_pack_contains_no_credential_material (wide needle set per M2-T007 G5 O4 carry-forward: token, apikey, api_key, authorization, bearer, password, secret); test_s16_requests_without_token_carry_only_the_accept_header
- **ZT-S17:** full api suite run recorded in section 7 (442 passed; PLUTO/zoning-features/contract tests all green, zero modifications to existing test files); plus test_regression_no_pluto_module_state_is_modified, test_regression_correlation_id_minted_when_absent

## 6. Fixture capture log (live, tokenless, producer network use disclosed)

Capture tool: `services/api/tests/fixtures/ztldb/build_fixture_pack.py capture` (single bounded urllib GET each, anonymous, ~104 KB pack total). MANIFEST.json is the authoritative machine-readable log (`generated_at_utc 2026-07-20T04:28:52Z`). Digests are sha256 over the exact UTF-8 bytes of `response_body_raw`.

Raw captures (official responses, verbatim):
- ZT01_record_single_lot.json (HTTP 200, 2026-07-20T04:28:48Z): https://data.cityofnewyork.us/resource/fdkv-4t4z.json?bbl=1000010100&%24order=bbl&%24limit=10 -> sha256:37d1e4a4f4df9368f413dcb9175b9c8553830ba571cffccc65ca5304c3e7deac
- ZT02_record_split_lot.json (HTTP 200, 2026-07-20T04:28:48Z): ...?bbl=1000010010&%24order=bbl&%24limit=10 -> sha256:46ee03e1460f90cd2dedd813de3e341e47731c7e6229d4f439323e76df0b137c
- ZT03_no_record_valid_bbl.json (HTTP 200, 2026-07-20T04:28:48Z): ...?bbl=5999999999&%24order=bbl&%24limit=10 -> sha256:37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570
- ZT04_record_overlay_lot.json (HTTP 200, 2026-07-20T04:28:49Z): ...?bbl=1001110100&%24order=bbl&%24limit=10 -> sha256:b76f44a15c7842417de9f097d4f9aed49c48eba993eb642db7110706657505ec
- ZT05_record_park_lot.json (HTTP 200, 2026-07-20T04:28:49Z): ...?bbl=1000030001&%24order=bbl&%24limit=10 -> sha256:8e12fff2de21844ec547226dc16aa368a6539762f6fd3eeaa429b860059c1cda
- ZT06_record_limited_height_lot.json (HTTP 200, 2026-07-20T04:28:49Z): ...?bbl=1013760011&%24order=bbl&%24limit=10 -> sha256:faa8443bf62ad903800943b5f8d897d5279e1894a11dfa133c2a000178f55f75
- ZT07a_page_offset0.json (HTTP 200, 2026-07-20T04:28:50Z): ...?%24order=bbl&%24limit=5&%24offset=0 -> sha256:b4b8771accd00dcc98f68e390c9e729202d6f6216b8089e26d51c25e7cc03c42
- ZT07b_page_offset5.json (HTTP 200, 2026-07-20T04:28:50Z): ...?%24order=bbl&%24limit=5&%24offset=5 -> sha256:2ac4f3cd5f1bebfd42d0e0de94bf0b986dae7ba43d945515d9ff8c42a37299fd
- ZT08_api_views_metadata.json (HTTP 200, 2026-07-20T04:28:50Z): https://data.cityofnewyork.us/api/views/fdkv-4t4z.json -> sha256:f6dc2bbe1cdb6c190e1def54fda610b443db3e257df3ff5ff8865900ec8ce03a
- ZT09_row_count.json (HTTP 200, 2026-07-20T04:28:51Z): ...?%24select=count%28bbl%29 -> sha256:c13bebb794ab8527572a2d4d5b8de1b14ab89e1dbe0fb8e60accedb03d6f86a5
- ZT10_no_such_column_400.json (HTTP 400, 2026-07-20T04:28:51Z): ...?%24select=nonexistent_column&%24limit=1 -> sha256:c8b1d50832d3937eff18814280983a7f93ccd3bb46becfcb6aa1f45c7bbc8cac

Synthetic derivations (offline, labeled, `derived_from` lineage in the manifest; request_url/timestamp inherited from the source capture):
- ZT90_record_slash_tie_synthetic.json -> sha256:5e1bf476beae94aeb57d85dbcebcdf3e57e1313bf46e5c9183bfabe7796c00ca
- ZT91_record_open_zd1_synthetic.json -> sha256:4042841d782fc314d969dc08df84e7f52cc738c518e3ac12667b4cbf33f64d9b
- ZT92_record_observed_null_synthetic.json -> sha256:c3c6e417c2da0c56776c7b4e0c0d3b1ce16aa6c7a959dc960496878f11d648c5
- ZT93_record_duplicate_bbl_synthetic.json -> sha256:d477aff417c3933fe4b20584301b540b1b872f972f45b2def75a0cae0bb7f745
- ZT94_malformed_not_array_synthetic.json -> sha256:14dead39e5d2e6c5d8c0b5e62d1eb0a3b1bbc80a387282426451b5925eeb81e2
- ZT95_malformed_truncated_synthetic.json -> sha256:5c6e2bde413dd0400158577d3c8ff24b8df88663e90bf383869d590dc513430d
- ZT96_page_duplicate_synthetic.json -> sha256:b4b8771accd00dcc98f68e390c9e729202d6f6216b8089e26d51c25e7cc03c42
- ZT97_page_no_progress_synthetic.json -> sha256:bdbe60a5f10dfd2c64ef4f06d527b6350930daadca6ff7c269035da89a080511
- ZT98_rate_limited_429_synthetic.json (HTTP 429) -> sha256:46d41af57dabe6c6153b4e14331086ef54a30b009e948c5d5b8a66c385a3a89d
- ZT99_meta_missing_rows_updated_synthetic.json -> sha256:208e06fa1b41fb3d48a7d536ada2edc627aff30536c592502738dd93773fd4d7
- ZT100_type_mismatch_400_synthetic.json (HTTP 400) -> sha256:74b9048760b55ba2e01420fa2d1c1c90f4bb3e1f7cb7d5820e3583038acdb3e2
- ZT101_record_unknown_column_synthetic.json -> sha256:6931c483a40a987dc31cfc91c57eef7f35622ababe222c7debd9cbfdc239c2fb
- ZT102_meta_renamed_column_synthetic.json -> sha256:39f7db670c6c17bb346f15e640eb191f5bff84eb50160bf31b2ece8ccf6609b7

### 6.1 Bounded probe queries at build time (not fixtures; evidence only)
- `?$limit=1` liveness: 200, split-lot record 1000010010 (matches research Z3 verbatim).
- `api/views` metadata: `rowsUpdatedAt` 1775414816 = 2026-04-05T18:46:56Z — **the staleness stall PERSISTS on 2026-07-20** (research 5.1 observed 2026-07-16; a second monthly boundary has now passed).
- `$select=count(bbl)`: `[{"count_bbl":"857951"}]` — unchanged since 2026-07-16.
- Slash-tie probes: `$where=special_district_1 like '%/%'` -> `[]`; same for special_district_2 -> `[]`. NO live slash value currently exists (OQ-8) -> ZT90 synthetic, labeled.
- Open-ZD1 probe (borough 4, values outside R/C/M/PARK/BPC): `[]`; bounded group-by of `zoning_district_1` returned **203 distinct values + a null group**, all matching the Appendix-B shape -> ZT91 synthetic, labeled (the official column description still allows ZR section numbers; the open-set code path is required).
- PARK lot probe -> 1000030001; LH-1A probe -> 1013760011; overlay probe -> 1001110100 (C1-5).
- LIVE FINDING: rows with NO `zoning_district_1` key exist (e.g. 1000010201, captured inside ZT07b) — folded into the connector (absence observation) and the registry record.

## 7. Commands run and exact outputs (G2 self-check)

From `.claude/worktrees/M2-T008/services/api`:

1. Baseline before any change:
   `python -m pytest tests -q` -> `356 passed in 5.21s`
2. Fixture capture + derivation:
   `python tests/fixtures/ztldb/build_fixture_pack.py capture` -> 11 fixtures + MANIFEST (output logged per file, e.g. `wrote ZT01_record_single_lot.json (1143 bytes)` ... `wrote MANIFEST.json (11 fixtures)`)
   `python tests/fixtures/ztldb/build_fixture_pack.py derive` -> 13 synthetics -> `wrote MANIFEST.json (24 fixtures)`
3. New connector tests:
   `python -m pytest tests/connectors/test_ztldb_soda.py -q` -> `72 passed in 0.44s`
4. New cross-check tests:
   `python -m pytest tests/profile/test_ztldb_crosscheck.py -q` -> `14 passed in 0.30s`
5. FULL suite (ZT-S17):
   `python -m pytest tests -q` -> **`442 passed in 3.29s`** (356 baseline + 86 new; zero failures, zero existing tests modified)
6. Lint:
   `python -m ruff check .` -> `All checks passed!`
7. Registry JSON validity:
   `python -c "import json; json.load(open('docs/research/source-registry-drafts/ztldb.json',...))"` -> `registry JSON ok`

Execution location: owner PC worktree (source-only; fixture pack ~104 KB; no datasets, no installs; disk budget untouched). CI remains fully offline — the capture script is producer-run only.

## 8. Assumptions and defaults (disclosed)

1. **dataset_version label**: `source_fact` v1 requires a non-empty `dataset_version`; ZTLDB has no version column, so the connector uses `socrata-rows-<rowsUpdatedAt RFC3339>` derived from the official metadata. This makes provenance ids idempotent per Socrata rows-state. Grounded in research 5.3 ("freshness monitoring must use rowsUpdatedAt"); not an invented source value.
2. **Freshness threshold 45 days**: from the accepted M1-T003 registry draft ("alert when age > ~45 days"); constant `SOURCE_STALENESS_THRESHOLD_DAYS`, reported alongside the raw age so consumers can apply their own policy.
3. **Per-BBL record query bound `$limit=10`**: uniqueness violations (2+ rows) surface as drift while the query stays bounded; the dataset contract is one row per tax lot.
4. **Case-only differences are uncertainty, not conflict** in the cross-check (e.g. real `16a` vs `16A`): both verbatim values preserved and reported; content differences remain conflicts. Documented in the module and notes.
5. **zmcode comparison mapping** (PLUTO checkbox true <-> ZTLDB text `Y`): both officially flag "may be on the border of two or more zoning maps"; mapping used ONLY as a comparison predicate; values never rewritten.
6. **No closed-set validation for special-district abbreviations**: the full Appendix A table is not transcribed in the accepted research; guessing it is prohibited. Slash parse + component preservation only.
7. **Conflict `field` names use PLUTO/profile column names** so the existing critical-column gate applies without modification; the ZTLDB column name is stated in every derivation text.

## 9. Known limitations

1. Slash-tie (ZT-S6) and open-ZD1 (ZT-S8) fixtures are SYNTHETIC (labeled, lineage recorded) because no live rows currently exhibit either state (bounded probes, section 6.1). OQ-8 stays open in the registry; a future live occurrence should replace ZT90.
2. The connector is per-BBL + bounded-scan only: no full-dataset sync, no persistence, no API route wiring (`app/api/**` was outside the allowed scope), no spatial intersection. The cross-check consumes fixture values per the owner exclusion.
3. `no_record` results are not LKG-cached (mirrors the accepted PLUTO fetcher); they are TTL-cached.
4. Source-freshness check adds one metadata request per fresh fetch (mirrors the M2-T007 metadata-first pattern); injectable `freshness` lets batch callers amortize it.
5. The ~3.5-month Socrata staleness means live per-BBL answers can be one or more rezonings behind; the guard + cross-check make this visible but cannot fix the upstream stall (OQ-3; escalation to DCPOpendata@planning.nyc.gov now warranted).

## 10. Security / provenance impact

- No new secret: the optional `SOCRATA_APP_TOKEN` reuses the existing env var; header-only; negative tests prove absence from URLs, logs, payloads, results, and the fixture pack (wide needle scan per M2-T007 G5 O4 carry-forward).
- No new network surface at runtime beyond the pinned official origin+dataset; caller input reaches URLs only as validated canonical digits or bounds-checked ints; reused hardened transport (bounded body read, refused redirects).
- Provenance: every fact carries source id, dataset id, request URL, retrieval timestamp, dataset rows-version, digests, stable fact identity, and the presence-state record; conflicts/uncertainties preserve all observations verbatim. No adjudication anywhere.
- No schema/contract change; no RLS/storage/deployment surface touched. Recommended: no separate G5 needed beyond the required gates per packet (no new security surface class), but the reviewer should re-run the secret-scan test.

## 11. New risks / dependencies

- OQ-3 escalation: the Socrata stall has now crossed a second monthly boundary; recommend an orchestrator-tracked follow-up to contact DCPOpendata@planning.nyc.gov (human action).
- The `zoning_district_1_absent` live state (blank ZD1 rows) is a new verified fact recorded in the registry; downstream completeness policies (M2 confirmation workflow) should treat ZTLDB ZD1 absence as unknown-coverage, not as PARK/vacant.
- Anchor digest is content-coupled to fixture ZT01: replacing that fixture requires updating `ZT01_NORMALIZED_DIGEST` (test constant), by design.

## 12. Recommended next tasks

1. API route integration (`/api/v1` property profile endpoint) wiring `ResilientZtldbFetcher` + `crosscheck_lot_zoning` into the served profile (app/api scope, separate task).
2. Render-worker monthly ZTLDB paged sync + persistence (depends on B-001 persistence decision).
3. OQ-3 escalation blocker (human email to DCP Open Data).
4. Replace ZT90 synthetic with a live slash-tie capture when one appears (monitor via the scan).

## 13. Report path

`project-control/reports/M2-T008-producer-report.md` (this file, in the M2-T008 worktree).
