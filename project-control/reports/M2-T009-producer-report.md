# M2-T009 — Producer report: Tax-lot geometry connector (MapPLUTO ArcGIS, per-BBL)

- **Task:** M2-T009
- **Producer:** backend-engineer
- **Date:** 2026-07-20 (UTC)
- **Worktree/branch:** `.claude/worktrees/M2-T009` / `task/M2-T009-mappluto-geometry` (based on main `0ec0ff7`)
- **Status requested:** `awaiting_gate`

## 1. Summary

Implemented the fixture-driven per-BBL MapPLUTO ArcGIS geometry connector with all six packet safeguards: strict identifier/result validation (zero/one/multiple explicit outcomes, condo billing-lot semantics), CRS validation before any coordinate interpretation (typed `wrong_crs`; no degrees-based area path exists — negative tests prove rejection), the full geometry-validity taxonomy, a no-silent-repair policy with separate original/normalized digests and recorded repair methods plus library versions, deterministic canonical geometry digests with exactly-pinned Shapely/GEOS and hardcoded cross-platform anchors, and TEST-level spatial scenarios against the M2-T007 district fixtures with the named plus-or-minus 20 ft boundary tolerance. Live fixtures captured 2026-07-20 UTC from the researched official endpoint. Full api suite: **522 passed** (baseline 442 + 80 new); **ruff clean**.

## 2. Files changed

| Path | Change |
|---|---|
| `services/api/app/connectors/mappluto_geometry_arcgis.py` | NEW — the connector (~1,660 lines incl. docs) |
| `services/api/tests/connectors/test_mappluto_geometry_arcgis.py` | NEW — 80 tests, GEO-S1..S12 |
| `services/api/tests/fixtures/mappluto_geometry/` | NEW — 30 fixtures (7 raw live-captured + 23 labeled synthetic) + `MANIFEST.json` + `build_fixture_pack.py` (~500 KB total, KB-scale) |
| `services/api/pyproject.toml` | `shapely==2.0.7` added to `[project.dependencies]` (DISCLOSED shared-file touch; see section 7) |
| `services/api/requirements.txt` | `shapely==2.0.7` deployment pin (DISCLOSED; satisfies the pyproject pin) |
| `docs/research/source-registry-drafts/pluto-mappluto.json` | Added third record `nyc-dcp-mappluto-arcgis` (geometry channel completed/confirmed; existing two records untouched) |
| `project-control/reports/M2-T009-producer-report.md` | this report |

**Read-only inputs honored:** `pluto_soda.py` (transport + `canonical_json_digest` reused via import only), `bbl.py` (`normalize_bbl`, `check_identifier_consistency` reused), `zoning_features_arcgis.py`/`ztldb_soda.py` (pattern reference only, unmodified). No fourth transport copy; the per-module retry loop follows the M2-T007/T008 precedent (consolidation refactor stays owner-sequenced, see section 12). Guard test: `test_s12_no_pluto_module_state_is_modified`.

## 3. Contracts changed

**None.** Contract 1.3.0 stands. No profile integration (forbidden path honored). No resilience-framework change (primitives composed only). No CI workflow change was needed (see section 7).

## 4. Endpoint (never guessed)

Researched official endpoint used exactly as documented in `docs/research/pluto-mappluto-2026-07-16.md` section 2.5 (G1-verified, correction C4):

`https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer` (layer 0)

Re-verified live at capture time (2026-07-20 UTC): name `MAPPLUTO`, `esriGeometryPolygon`, objectIdField `OBJECTID`, `maxRecordCount` 2000, spatialReference `wkid 102718 / latestWkid 2263`, 103 fields, `supportsPagination`/`supportsOrderBy` true, `editingInfo.dataLastEditDate` 1779892578102 = 2026-05-27T14:36:18Z (consistent with release 26v1; every captured feature carries `Version = "26v1"`).

## 5. Acceptance-scenario coverage map (GEO-S1..S12 → tests)

All tests in `services/api/tests/connectors/test_mappluto_geometry_arcgis.py`; offline, fixture-replayed, deterministic.

| Scenario | Tests (prefix `test_`) |
|---|---|
| GEO-S1 single-lot polygon + identifier/result validation | `s1_metadata_snapshot_validates_and_stamps_provenance`, `s1_required_fields_constant_matches_captured_layer_schema`, `s1_single_lot_result_validated_against_request`, `s1_socrata_style_bbl_input_is_normalized_before_query`, `s1_metadata_negatives_fail_typed` (x4), `s1_wrong_lot_returned_is_typed_result_mismatch`, `s1_component_conflict_is_visible_and_review_required` |
| GEO-S2 multipolygon + holes canonical ordering | `s2_holed_polygon_normalizes_with_stable_digest`, `s2_multipolygon_normalizes_with_stable_digest`, `s2_ring_rotation_and_member_order_do_not_change_normalized_digest` |
| GEO-S3 zero/one/multiple explicit outcomes | `s3_no_feature_is_explicit_typed_outcome_not_error`, `s3_multiple_features_is_review_required_never_first_pick`, `s3_exceeded_transfer_limit_forces_multiple_outcome` (plus GEO-S1 single case) |
| GEO-S4 condo semantics (research 2.5) | `s4_condo_billing_lot_resolves_with_complex_semantics`, `s4_condo_unit_lot_query_is_empty_with_billing_redirect_note` (LIVE-captured unit-lot emptiness), `s4_condo_unit_lot_with_polygon_is_flagged_for_review` |
| GEO-S5 invalid-geometry taxonomy | `s5_taxonomy_shape_maps_to_explicit_typed_state` (x9: self-intersection, unclosed ring, duplicate vertices, degenerate ring, empty, null, all-CCW orientation, paths geometry-collection, hole-outside-shell), `s5_missing_geometry_key_is_null_geometry`, `s5_nonfinite_coordinate_is_typed_invalid`, `s5_taxonomy_states_reach_lot_result_and_review_flag`, `s5_all_synthetic_fixtures_are_labeled_synthetic` |
| GEO-S6 no-silent-repair | `s6_repair_records_method_versions_and_separate_digests`, `s6_structural_repairs_preserve_original_digest_separately`, `s6_uncharacterizable_topology_is_review_required_not_repaired`, `s6_repaired_geometry_never_presented_as_untouched_source`, `s6_valid_geometry_records_no_repairs` |
| GEO-S7 digest determinism + pinned Shapely/GEOS | `s7_shapely_and_geos_versions_match_the_exact_pins`, `s7_hardcoded_cross_platform_anchor_reproduces_exactly` (fixture-independent hardcoded square), `s7_real_fixture_digests_reproduce_across_two_runs`, `s7_raw_original_and_normalized_digests_are_distinct_records`, `s7_digest_spec_is_self_describing_and_not_wkb` |
| GEO-S8 CRS safety | `s8_wrong_metadata_crs_is_typed_before_any_coordinate_use`, `s8_wrong_query_crs_is_typed_before_geometry_interpretation`, `s8_analysis_refuses_non_authoritative_crs`, `s8_degrees_based_area_path_does_not_exist` (negative proof: 4326/3857/empty/None all refused), `s8_area_is_projected_feet_and_cross_checked_with_official_value`, `s8_area_divergence_is_surfaced_never_reconciled` |
| GEO-S9 spatial scenarios vs M2-T007 fixtures | `s9_tolerance_is_named_and_matches_the_official_accuracy`, `s9_lot_fully_inside_district`, `s9_lot_fully_outside_district`, `s9_boundary_touch_is_uncertain_never_silently_classified`, `s9_touching_lot_from_outside_is_uncertain`, `s9_split_intersection_detected_beyond_tolerance`, `s9_hole_interaction_uses_the_real_holed_lot`, `s9_invalid_geometry_yields_no_canonical_form_to_classify`, `s9_repaired_geometry_classifies_deterministically`, `s9_repeated_runs_reproduce_identical_classifications` |
| GEO-S10 allowlist + resilience + malformed-never-empty | `s10_every_built_url_targets_the_pinned_official_root`, `s10_url_builder_reproduces_captured_fixture_urls`, `s10_invalid_bbl_is_refused_before_any_network_io`, `s10_url_builder_requires_canonical_form`, `s10_timeout_persists_to_typed_timeout_with_bounded_retries`, `s10_429_persisted_is_typed_rate_limited`, `s10_retry_after_honored_exactly_then_success`, `s10_network_failure_persists_to_typed_upstream_error`, `s10_arcgis_error_object_with_http_200_is_upstream_error`, `s10_malformed_response_is_typed_never_an_empty_result` (x2), `s10_request_budget_exhaustion_is_typed_and_pre_io`, `s10_circuit_open_is_typed_and_makes_no_upstream_call`, `s10_resilient_client_validates_bbl_before_cache_and_network`, `s10_error_taxonomy_states_are_distinguishable`, `s10_no_tokens_or_secrets_in_requests_fixtures_or_manifest` (wider needle set), `s10_manifest_digests_match_committed_fixture_bytes` |
| GEO-S11 two-staleness separation | `s11_the_two_staleness_dimensions_vary_independently` (owner quartet, M2-T008 pattern), `s11_cache_hit_serve_does_not_alter_source_timestamps` |
| GEO-S12 regression | full api suite green (section 6), `s12_no_pluto_module_state_is_modified`, `s12_correlation_id_minted_when_absent`, `s12_metadata_injection_avoids_refetch` |

## 6. Exact commands and outputs (self-check, G2)

All run from `services/api` in the worktree on the owner PC (Windows, Python 3.11.9 local sandbox; CI runs Python 3.12 from the same pins).

1. Baseline before any change:
   - `python -m pytest -q` → `442 passed in 5.19s`
2. Fixture capture (live, keyless, bounded — 7 GET requests total):
   - `python tests/fixtures/mappluto_geometry/build_fixture_pack.py capture` → wrote MPG01..MPG07 + MANIFEST (7 fixtures; largest 115,231 B)
   - `python tests/fixtures/mappluto_geometry/build_fixture_pack.py derive` → wrote 23 synthetic fixtures + regenerated MANIFEST (30 fixtures)
3. Final verification:
   - `python -m pytest tests/connectors/test_mappluto_geometry_arcgis.py -q` → `80 passed in 0.76s`
   - `python -m pytest -q` → `522 passed in 7.14s`
   - `python -m ruff check .` → `All checks passed!`
   - `python -c "import shapely; print(shapely.__version__, shapely.geos_version_string)"` → `2.0.7 3.11.4`
   - Registry draft JSON validity: `python -c "import json; ...load..."` → `records: 3 ['nyc-dcp-pluto-soda', 'nyc-dcp-mappluto-bulk', 'nyc-dcp-mappluto-arcgis']`

## 7. Shapely pin (disclosed dependency addition)

- **Pin:** `shapely==2.0.7` in BOTH `services/api/pyproject.toml` `[project.dependencies]` and `services/api/requirements.txt`.
- **Runtime, not dev:** the connector imports shapely at module import (validity check, `make_valid` repair, canonicalization); every environment that installs the package needs it (`pip install ./services/api` in the CI e2e job, `pip install .[dev]` in the pytest job, Render via requirements.txt).
- **Exact pin rationale (deviation from the pyproject range convention, per packet directive):** deterministic geometry digests and `make_valid` behavior depend on the bundled GEOS build. The official shapely 2.0.7 wheels bundle **GEOS 3.11.4** on every platform (verified locally on the Windows wheel: `shapely.geos_version_string == "3.11.4"`). A range could silently change digests between installs. `test_s7_shapely_and_geos_versions_match_the_exact_pins` asserts both `shapely.__version__ == "2.0.7"` and `shapely.geos_version_string == "3.11.4"`, so CI proves the same behavior. Documented in both dependency files: re-pin only deliberately with re-anchored digests.
- **CI impact:** none — CI installs via `pip install .[dev]` / `pip install ./services/api` (`.github/workflows/ci.yml` lines 72, 115), which now pull shapely automatically. cp312 manylinux wheels exist for 2.0.7. **No workflow edit was needed; the STOP condition was not triggered.**
- **Disk:** shapely 2.0.7 wheel is ~2.4 MB installed (tens of MB with numpy already present) — within the local budget disclosed at G0. Local install was already present in the producer sandbox (no new install was required).
- **Python note:** local sandbox runs Python 3.11.9 while `requires-python = ">=3.12"`; the suite passes under both (CI is authoritative at 3.12). Pre-existing condition, unchanged by this task.

## 8. Fixture capture log (all URLs on the pinned official root; keyless; no auth header ever sent)

Raw captures (classification `raw`; exact full URLs and sha256 in `MANIFEST.json`; retrieval timestamps UTC):

| Fixture | Request (query core) | Captured | Bytes | sha256 (prefix) |
|---|---|---|---|---|
| MPG01_meta | `MAPPLUTO/FeatureServer/0?f=json` | 2026-07-20T05:30:57Z | 32,321 | `819a17b2e6146f6e` |
| MPG02_lot_single | `where=BBL=1008350041` (Empire State Building; 1 CW ring) | 05:30:57Z | 3,476 | `0d12247fe0d12d97` |
| MPG03_nofeature | `where=BBL=5999999999` (valid, nonexistent) → `features: []` | 05:30:57Z | 1,323 | `437b1d00810278f6` |
| MPG04_condo_billing | `where=BBL=1000157501` (lot 7501, CondoNo 1025) | 05:30:58Z | 3,402 | `2a25d5f8bc9067fb` |
| MPG05_condo_unit | `where=BBL=1000151001` (unit lot, same block) → `features: []` LIVE | 05:30:58Z | 1,465 | `437b1d00810278f6` |
| MPG06_holes | `where=BBL=1000010010` (Governors Island; 1 CW exterior + 2 CCW holes) | 05:30:58Z | 19,887 | `90a7f6dd364a64c9` |
| MPG07_multipolygon | `where=BBL=4142600001` (Queens; TWO CW exterior rings — true multipolygon, found live; NOT synthetic) | 05:30:59Z | 115,231 | `77055f215f8f9fe4` |

All lot queries use the bounded parameter set the connector itself emits: `outFields=OBJECTID,BBL,BoroCode,Borough,Block,Lot,CondoNo,Version,Shape__Area,Shape__Length&orderByFields=OBJECTID ASC&resultRecordCount=10&resultOffset=0&f=json`. `test_s10_url_builder_reproduces_captured_fixture_urls` asserts byte-identical URL reproduction. Note MPG03 and MPG05 share a body digest because the official empty-result envelope is byte-identical regardless of the query (the request URL distinguishes them in the manifest).

Synthetic derivations (classification `synthetic`, each labeled in-file and in the manifest, `derived_from` recorded): MPG80-88 invalid-geometry taxonomy (synthetic BY NECESSITY — the live service cannot politely produce broken geometry), MPG90-95 metadata negatives + old-edit-date, MPG96-99 result-validation negatives, MPG100-103 transport negatives. Total pack ~500 KB.

## 9. Geometry digest canonicalization (spec verbatim in `MPG_CANONICALIZATION_SPEC`)

Three digests, kept separately:

1. **raw_digest** — sha256 over the exact UTF-8 bytes of the HTTP response body (order-sensitive; pins the transported bytes).
2. **original_geometry_digest** — sha256 of the canonical JSON (sorted keys, compact separators) of the VERBATIM esri geometry object (null preserved). Always present, whatever the validity outcome.
3. **normalized_digest** — sha256 of `"mappluto-geom-canonical-1:" + compact JSON` of the canonical form: list of polygons → list of rings (exterior first, then holes) → list of `[x, y]` coordinate STRING pairs. Rules: coordinates rounded half-even to 0.01 ft and formatted with exactly two decimals (negative zero normalized); closing vertex and post-quantization consecutive duplicates removed (rings are OPEN cycles); each ring rotated so its lexicographically smallest pair is first; exterior CCW / holes CW; holes sorted by serialized form; polygons sorted by exterior serialized form. Default WKB/WKT is deliberately NOT used (not assumed cross-platform canonical).

Proven properties: two-run byte-identical reproduction; invariance under ring rotation and multipolygon member reordering (while original digests differ — separation demonstrated); hardcoded fixture-independent anchor (`SQUARE_NORMALIZED_DIGEST`) plus four fixture anchors (ESB, holes, multipolygon, repaired bowtie) that CI must reproduce on Linux/py3.12 to pass — this is the cross-platform proof (produced on Windows/py3.11, verified on CI's platform).

## 10. Geometry validity taxonomy and repair policy (as implemented)

| Input condition | Finding code | State |
|---|---|---|
| geometry JSON null / key absent | `null_geometry` | `invalid_geometry` |
| `rings: []` | `empty_geometry` | `invalid_geometry` |
| paths/points payload | `geometry_collection` | `invalid_geometry` |
| non-finite coordinate | `nonfinite_coordinate` | `invalid_geometry` |
| unclosed ring | `unclosed_ring` | `repaired` (method `ring_closure` — deterministic, characterized) |
| consecutive duplicate vertices | `duplicate_vertices` | `repaired` (method `drop_consecutive_duplicate_vertices`) |
| zero-area/collinear ring beside valid rings | `degenerate_ring` | `repaired` (method `drop_degenerate_ring`; area unchanged) — all-degenerate → `invalid_geometry` |
| self-intersection (incl. zero-signed-area bowtie) | `self_intersection` | `repaired` via `shapely_make_valid` (records GEOS reason, area before/after, shapely+GEOS versions) |
| only-CCW rings (esri orientation inverted) | `invalid_orientation` | `review_required` (intent uncharacterizable — never guessed) |
| hole outside every shell | `invalid_orientation` | `review_required` |
| unknown GEOS validity pathology / non-polygonal or empty make_valid output / repair area drift > 1% (non-self-intersection) | `validity:<reason>` / `repair_area_drift` / `geometry_collection` | `review_required` |
| valid polygon / multipolygon / holes | — | `valid` (kind + ring/hole/vertex counts + area in EPSG:2263 sq ft) |

Multiple features for one BBL → result outcome `multiple_features`, `review_required=true`, all features preserved, no assessment of a "first" feature. Zero features → `no_feature` with condo-unit redirect note where applicable. Identifier component conflicts (BoroCode/Block/Lot vs BBL) are surfaced verbatim via `check_identifier_consistency` and set `review_required` — never resolved silently. BBL attribute mismatch is the typed `result_mismatch` error.

## 11. Assumptions and defaults

1. **esri ring-orientation convention** (clockwise = exterior, counterclockwise = hole) applied for ring role assignment — standard esri JSON semantics, corroborated by every live capture (all exterior rings CW, both Governors Island holes CCW). Inverted-orientation inputs are review_required, not guessed.
2. **Boundary tolerance 20 ft** is taken from the official accuracy statement for the DCP zoning-features production chain (zoning-features research section 4.3); MapPLUTO's own layer metadata does not state a numeric accuracy on the ArcGIS side. Applied as the named uncertainty band; documented in `classify_spatial_relation` output.
3. **Coordinate quantization 0.01 ft** for the canonical digest — three orders of magnitude below stated accuracy; live coordinates already serialize at 2 decimals.
4. **`resultRecordCount=10` bound** for per-BBL queries: >1 feature is review-required regardless, so a small bound suffices; a full bounded page with `exceededTransferLimit` still forces `multiple_features`.
5. **Required-subset schema validation**: the connector validates its 10 contracted fields (of 103) for presence and exact type; other fields may drift without failing this connector (the fixture-level test pins the full 103-field inventory count). Unknown attributes in responses surface as drift signals.
6. `Shape__Area`/`Shape__Length` are treated as official informational values in EPSG:2263 units; the locally computed planar area is cross-checked and divergence >0.5% surfaces as a visible note (never silently reconciled). Live ESB lot: computed 97,113.6875065 vs official 97,113.6875.

## 12. Known limitations

1. **Per-lot channel only** — `maxRecordCount 2000` rules this endpoint out for citywide import (research 5.2); the bulk FileGDB import remains deferred behind B-001/B-002. No persistence, no profile wiring (later authorized tasks).
2. **Spatial classifier is TEST-level** — `classify_spatial_relation` proves intersection-readiness; it is explicitly documented as NOT the production intersection engine and makes no zoning assignment.
3. **Shoreline-clipped geometry** — partially underwater lots are clipped (live multipolygon MPG07 shows clipped parts); the unclipped variant exists only in the bulk release.
4. **`condo_unit_lot_with_polygon`** (unit-range lot returning a polygon) is only exercisable synthetically; live behavior matches the documented semantics (MPG05 empty).
5. **Repaired-bowtie digest anchor is GEOS-dependent** by design; it is stable under the exact pin and must be re-anchored if the pin ever changes (documented in both dependency files).
6. **Fourth instance of the per-module retry-loop pattern** (owner-acknowledged in the G0 dispatch): the shared-transport/retry consolidation refactor remains owner-sequenced AFTER this wave — recommended below.
7. Local sandbox ran Python 3.11.9 vs `requires-python >=3.12` (pre-existing repo-wide condition); CI at 3.12 is the authoritative environment.

## 13. Security and provenance impact

- **No new security surface:** keyless official service; the only header ever sent is `Accept: application/json`; pinned service root; callers cannot supply URLs, hosts, where clauses, out-fields, or paging values; BBL validated before cache and network; untrusted upstream text repr-sanitized in payloads (M2-T007 pattern); error payloads carry no stack traces.
- **Secret hygiene:** wider needle scan (`token/apikey/api_key/authorization/bearer/password/secret`) over all 30 fixtures + manifest + every outgoing request, in-test (`test_s10_no_tokens_or_secrets...`). No credential material exists in the pack; no secretscan:allow pragma was needed.
- **Provenance:** every result stamps endpoint URLs, retrieval timestamp, source edit timestamp (`dataLastEditDate`, quartet-tested as provenance-only per the owner two-staleness rule), CRS, per-feature `Version` attribute (26v1), raw/original/normalized digests, digest spec text, shapely/GEOS versions, drift signals, notes.
- **Low-storage:** ~500 KB committed fixtures; 7 live GETs at capture; no datasets, no DB, no persistent local artifacts. Cleanup: none needed (fixtures are the durable artifact, committed to git).

## 14. Recommended next tasks

1. **Shared connector transport/retry consolidation** (owner-sequenced refactor, now with four consumers: pluto_soda, zoning_features, ztldb, mappluto_geometry) — extract `_request_with_retry` + envelope parsing into one reviewed module.
2. **Profile integration task** — geometry facts (canonical geometry reference, area, condo classification, review flags) into the canonical property profile under a new packet (forbidden here).
3. **Lot-vs-district production intersection task** — promote the tested tolerance semantics into the deterministic rules/geometry engine (M2 conflict/split-lot work), using ZTLDB ZD1/ZD2 as the cross-check per research ZF-F9.
4. **Citywide FileGDB import** — remains blocked (B-001/B-002).
5. **Minor-release observation** — verify `editingInfo.dataLastEditDate` moves with the next monthly PLUTO minor release (registry open question).

## 15. Design preservation (resumability)

The complete design is embodied in the module docstring (safeguards 1-6 mapping), `MPG_CANONICALIZATION_SPEC` (self-describing digest recomputation), section 10 above (taxonomy table), and the fixture builder (`build_fixture_pack.py` — rerunnable `capture`/`derive` phases regenerating the manifest). Key decisions: esri CW=exterior role assignment with review_required on inversion; characterizable-repair whitelist (`ring_closure`, duplicate-drop, degenerate-drop, `make_valid` for known pathologies only); canonical form as quantized string-coordinate cycles (NOT WKB/WKT); `wrong_crs` as its own typed state distinct from `schema_drift`; `result_mismatch` as a connector-specific typed state (documented as additive to the shared taxonomy); bounded 10-feature per-BBL query with `multiple_features` review-required semantics; three-digest separation (raw / original geometry / normalized geometry).
