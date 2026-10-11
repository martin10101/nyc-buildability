# M5-T154 - independent reviews: G1 one independent data-contract-verifier; G3 one independent code-reviewer; G4 one independent qa-engineer; G5 one independent security-reviewer

First reviewed head: `3619744ebba6698cfd699f47d836294bdf979881`. Corrected head: `6c8c9f7d526539bc1d5d8ef942d8a3770aba420b`. Every reviewer is an AI agent that produced none of the work; this is not a human or professional review. The code review's first return came in two parts; its record joins them unchanged.

**CI:** CI at the corrected head 6c8c9f7d: all 46 checks success (workflow CI runs 38097919683 on the pull request and 38097916934 on the push, including web-e2e (vitest and the whole Playwright suite), the api job, control-plane and the dependency-security jobs; secret-scan and context-budget success).

**The orchestrator's own checks:** The orchestrator printed the report through the real website and route at every round and measured it: at the corrected head 9 A4 pages, no element wider than the printable width (overflow check n = 0), body text and drawing labels at true size (N/print-w22g). The first reviewed head printed shrunk to about 77% because page 1's row was wider than the paper (already true on main); corrected in M5-T156 correction 2.

**Verdicts:** every reviewer PASS at the first head, with required corrections (code: M5-T154-C1; QA: C1 to C4; visual: T155-C1, T156-C1, T156-C2; security: advisory A1); every one applied, and every reviewer PASS at the corrected head. Not run (needs a person): the ten-second test with a real architect and a real screen-reader pass.

The returns follow unchanged.

---

### Return 1 of 8: G1 data-contract review (M5-T154) (return-w22-data.md)

```
PART 1 of 1 — G1 DATA-CONTRACT GATE REPORT, task M5-T154 (data-contract-verifier, independent, read-only)

VERDICT: PASS (no required corrections; three non-blocking observations recorded below).

SCOPE OF THIS GATE: I am the data-contract-verifier for gate G1 of M5-T154 (the map data around the lot: the neighbouring-lot MapPLUTO window connector, map document 1.1.0, the report map-context provider, and the recorded benchmark window pack). M5-T155 (drawings) and M5-T156 (report) ride the same branch/head (ruling Y1) but are judged by their own gates/reviewers; I render no G1 verdict on them, though I confirm the 1.1.0 contract they consume is sound.

HEAD: confirmed `git rev-parse HEAD` = 3619744ebba6698cfd699f47d836294bdf979881 on task/wave22-site-context in /root/project/w-wave20 (checkout not modified). Base main = 9ab3a47e6a55fc75e13140e910f0839541754874 is the merge-base and an ancestor; only 78 files differ against that base. (Caution for the orchestrator: the worktree's LOCAL `main` ref is stale at d8b3899f61 — a `git diff main...HEAD` there falsely reports ~7213 files/985k insertions; always diff against the SHA 9ab3a47e6, not the local ref.)

METHOD: read the packet, rulings Y1-Y13, the scope correction, directives source-082/083, and the producer report; then independently reproduced every claim — connector source, builder, provider, schema, pack — with /root/project/lanes-runtime/venv/bin/python (PYTHONDONTWRITEBYTECODE=1), ran the producer tests and contract validators, and made two live keyless GETs to the official services. No repo writes; no server/Playwright; ports 3000/3001/8000 untouched.

=========================================================
CHECK 1 — OFFICIAL SOURCE IDENTITY / ENDPOINTS / LAYERS: PASS
- MapPLUTO neighbouring-lot WINDOW (new connector /root/project/w-wave20/services/api/app/connectors/mappluto_window_arcgis.py): https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0; SOURCE_ID nyc-dcp-mappluto-arcgis; wkid 102718 / latestWkid 2263; spatialRel esriSpatialRelIntersects on an esriGeometryEnvelope; inSR=2263/outSR=2263; outFields EXACTLY OBJECTID,BBL,Block,Lot,Address,Version (NO OwnerName or any personal field). It imports the parent per-BBL connector's pinned constants (SERVICE_ROOT, LAYER_NAME, SOURCE_ID, EXPECTED_WKID/LATEST_WKID, CRS_STAMP, raw_body_digest) and the parent file mappluto_geometry_arcgis.py is byte-identical at main and HEAD (sha256 unchanged) — parent not modified.
- Building footprints (reused fetch_context_buildings): https://services6.arcgis.com/yG5s3afENB5iO9fj/arcgis/rest/services/BUILDING_view/FeatureServer/0; nyc-oti-building-footprints-arcgis; outFields OBJECTID,DOITT_ID,BIN,BASE_BBL,MAPPLUTO_BBL,HEIGHT_ROOF,GROUND_ELEVATION,CONSTRUCTION_YEAR,FEATURE_CODE,GEOM_SOURCE,LAST_EDITED_DATE,LAST_STATUS_TYPE.
- DCM street centre lines (reused fetch_street_segment_geometries): https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/DCM_Street_Center_Line/FeatureServer/0; nyc-dcp-dcm-street-centerline-arcgis.
- Out CRS EPSG:2263 (US survey feet) on all three; no reprojection path.
- I reproduced all three request URLs from the connectors and they are BYTE-IDENTICAL to the pack MANIFEST (mappluto_window_arcgis.build_window_query_url, building_footprints_arcgis.build_query_url, dcm_street_centerline_arcgis.build_segment_query_url).

CHECK 2 — RECORDED PACK (/root/project/w-wave20/services/api/tests/fixtures/benchmark_215_16_northern_window/): PASS
- sha256 of each data file equals its MANIFEST digest: mappluto df19e542…cf19; building cb153371…0abfb; dcm 5c01484c…1ed1ec — all match.
- Request URLs in MANIFEST equal the connector-built URLs (Check 1).
- Retrieval times present (RFC-3339) with http_date/last_modified; windows derived from the subject bbox (1048788.63,216310.44,1048911.58,216431.10): +400 ft for lots/footprints, +1,000 ft for streets — arithmetic verified.
- .gitattributes `* -text`; git check-attr reports text:unset → bytes preserved; files carry no CR.
- LIVE keyless GET cross-check (1 request): MapPLUTO where BBL IN (…0001,0011,0061,0070), outSR=2263 → HTTP 200, SR 102718/2263. All four lots agree with the recording: addresses identical (215-10 Northern Blvd; 45-12 215 Place; 45-11 215 Street; 215-16 Northern Blvd), Version 26v2, geometry identical to 0.01 ft, same vertex counts.

CHECK 3 — FIELD MAPPING & UNITS: PASS
- BBL: served as esriFieldTypeDouble, normalised to canonical 10-digit string; a non-numeric/invalid BBL raises MalformedResponseError.
- address: optional, kept only when a non-empty string; outline rings kept VERBATIM (float cast only — no quantize/repair/re-orient); subject lot excluded from neighbours.
- streets: name from Street_NM; width_text = raw Streetwidth unchanged; mapped_width_ft via parse_mapped_width_ft = fullmatch(\d+(?:\.\d+)?). I exercised it directly: '60'→60, '100'→100, ' 60 '→60, '60.5'→60.5, and '60-75','<=75','80-100','>90','Unknown','',None → null. This satisfies S4 and D-052 exactly, and is correctly NOT a wide/narrow legal classification (code comment and schema state this).
- Units: EPSG:2263 US survey feet throughout (CRS_STAMP authority string "NAD83 / New York Long Island, US survey feet").

CHECK 4 — NULL/UNKNOWN, PAGING, RATE-LIMIT, SCHEMA-DRIFT, PROVENANCE: PASS
- Provider /root/project/w-wave20/services/api/app/api/v1/report_context.py: flag off → None with ZERO connector calls; flag on → document; each layer fetch wrapped so a refusal demotes ONLY that layer to not_available; no subject outline → None; NEVER raises (S5). Verified by the provider tests and by building the document from the recorded pack via recorded_pack_provider.
- Paging: bounded (HARD_MAX_PAGES=50, MAX_WINDOW_LOTS=5000, over-page-count / repeated-OBJECTID / zero-progress / cap → PagingPathologyError; never silent truncation).
- Rate-limit/timeout/upstream: shared bounded-retry engine with typed RateLimitedError / SourceTimeoutError / UpstreamError; an ArcGIS error object delivered with HTTP 200 is treated as upstream error, not data.
- Schema drift: metadata gate checks name==MAPPLUTO, geometryType esriGeometryPolygon, objectIdField OBJECTID, required fields present with expected esri types, maxRecordCount valid; a query page not wkid 102718/latestWkid 2263 → WrongCRSError before any coordinate is read.
- Provenance (built document, all three available layers): source_id, dataset_id, request_url (byte-exact), retrieved_at, raw_digest_sha256, source_data_last_edited (date), dataset_version — all present and fail-closed (a layer with incomplete provenance is dropped to not_available). raw_digest_sha256 equals the recorded file digest for every layer (tax_lots sha256:df19e542…, footprints sha256:cb153371…, streets sha256:5c01484c…).

CHECK 5 — SCHEMA 1.1.0 ADDITIVE: PASS
- /root/project/w-wave20/packages/contracts/schemas/v1/map_context.schema.json and the bundled copy services/api/app/_contract_schemas/v1/map_context.schema.json are BYTE-IDENTICAL (sha256 equal; sync_contract_schemas.py --check exit 0).
- contract_version enum = ["1.0.0","1.1.0"]; three OPTIONAL members (context_window, tax_lots, streets) added to map_context — NOT in required, so every 1.0.0 document stays valid. street_entry.width_text type ["string","null"]; mapped_width_ft type ["number","null"] min 0; line minItems 2. Reuses existing $defs (polygon/point/provenance/layer_unavailable). No unknown keyword (no minProperties etc.).
- python .github/scripts/validate_contracts.py → exit 0, 23 schemas, 0 failures; the 4 existing 1.0.0 map_context fixtures still validate; new valid fixture synthetic_window_1_1_0.json passes; new invalid fixture street_mapped_width_not_a_number.json is correctly REJECTED ($.map_context.streets satisfies 0 schemas in oneOf — its mapped_width_ft is the string "60" instead of number-or-null, matching the fixture's _expected_failure).

CHECK 6 — SECOND OFFICIAL PRESENTATION (DOF Digital Tax Map): PASS
- LIVE keyless GET (1 request) to https://services6.arcgis.com/yG5s3afENB5iO9fj/ArcGIS/rest/services/DTM_ETL_DAILY_view/FeatureServer/0 (layer TAX_LOT_POLYGON), BBL IN (…0001,0011,0061,0070), outSR=2263 → HTTP 200, SR 102718/2263. All four lots present in BLOCK 7334 / BORO 4. The subject (lot 70) and lot 1 share an edge with vertices (1048810.23,216310.44) and (1048788.63,216408.05), edge length 99.97 ft — identical to MapPLUTO (99.9765 ft, S7 within 0.01 ft of 99.98 ft). Adjacency confirmed by the independent authority.

=========================================================
SCENARIO COVERAGE (S1-S8) — all encoded as tests and reproduced green:
- S1: test_window_returns_each_neighbour_once_in_2263, test_subject_lot_is_not_among_the_neighbours, test_request_url_is_byte_identical_to_the_manifest, test_request_never_asks_for_an_owner_name.
- S2: test_wrong_crs_is_refused, test_arcgis_error_object_is_refused, test_paging_fault_is_refused, test_malformed_ring_is_refused_whole.
- S3/1.0.0-still-valid: test_document_is_schema_valid_1_1_0_with_all_layers, test_every_existing_1_0_0_example_still_validates, test_outlines_and_paths_are_input_geometry_unchanged.
- S4: test_mapped_width_parser_only_parses_a_plain_number, test_width_text_is_kept_verbatim_from_the_source.
- S5: test_flag_off_returns_none_and_makes_no_connector_call, test_a_refusing_fetcher…, test_a_refusing_window_fetcher…, test_no_subject_outline_gives_none.
- S7: test_independent_window_check. S8: test_recorded_pack_provider_returns_the_same_document.
Built the document via the harness entry point recorded_pack_provider('…benchmark_215_16_northern_window') → contract_version 1.1.0, tax_lots available with 200 neighbour entries (subject 4073340070 absent), context_window = bbox+400 ft, streets available with 35 entries and window = bbox+1,000 ft, zoning_districts not_available, building_footprints available.

SCOPE / MODULARITY / PRIVACY:
- The M5-T154 producer commit c322e6760 touched ONLY M5-T154 allowed paths (incl. the scope-corrected test_map_context_contract.py in a separate commit). The drawings/report/report_read/apps-web files in the 78-file diff belong to M5-T155/M5-T156 on the shared branch — not an M5-T154 breach. Forbidden parent connectors (mappluto_geometry/building_footprints/dcm_*) are byte-identical at main and HEAD.
- No OwnerName/personal field anywhere in the recorded MapPLUTO response (grep + field list confirm OBJECTID,BBL,Block,Lot,Address,Version only).
- ruff check on the three new sources → All checks passed. python tools/modularity_check.py --check → exit 0 (no M5-T154 file flagged; map_context.py 577 / mappluto_window_arcgis.py 718 / report_context.py 374 lines).

TESTS RUN (venv python, offline replay):
- 39 passed: the four M5-T154 test files.
- 2235 passed, 0 failed: tests/contracts + tests/connectors + tests/api/test_report_context_provider.py + tests/spatial (confirms the additive 1.1.0 change breaks no 1.0.0 consumer; the 2 pre-correction failures in test_map_context_contract.py are now fixed).
- validate_contracts.py exit 0; sync_contract_schemas.py --check exit 0; .github/scripts tests not rerun (CI's job), validator direct exit codes used.

OBSERVATIONS (non-blocking, no correction required):
1. In the HARNESS REPLAY only, the building-footprints provenance source_data_last_edited = 2026-09-27 is served from the reused base-pack metadata, while the freshly captured footprints window file's HTTP last-modified is 2026-10-04 (the live layer edit date had advanced ~1 week at capture). This is documented in the pack README/extends_note and the producer report; the LIVE provider fetches current metadata, so production provenance is unaffected — benchmark replay artifact only.
2. In the harness replay, retrieved_at differs across layers (MapPLUTO/footprints stamp the connector replay clock 2026-10-10T19:05:57Z; streets carries the DCM pack retrieved_at 19:08:27Z because the DCM connector takes the transport response time). Cosmetic; the live path stamps a real per-layer wall-clock.
3. dataset_version in provenance is the dataLastEditDate epoch-ms string (e.g. '1788967824444'), not the MapPLUTO human "Version" string "26v2" (which is captured per-lot). This matches the existing 1.0.0 layer convention and is internally consistent.

FINAL: M5-T154 G1 = PASS. The official sources, endpoints, layers, fields, units, null/paging/rate-limit/schema-drift behavior, provenance, and the additive 1.1.0 schema are all verified against current official data (two live keyless cross-checks) and the recorded pack is byte-faithful.

END-OF-REPORT
```

### Return 2 of 8: G1 delta review at 6c8c9f7d (delta-w22-data.md)

```
G1 DELTA REVIEW — M5-T154 (data-contract-verifier, read-only) at HEAD 6c8c9f7d526539bc1d5d8ef942d8a3770aba420b (confirmed via git rev-parse; checkout unchanged).

1. MY REQUIRED CORRECTIONS: I had none in my first review (PASS with three non-blocking observations), so there is nothing to re-close. The three observations were explicitly non-blocking and remain accurate (unchanged files).

2. THE M5-T154 DELTA (3619744e..6c8c9f7d) — scoped to three files only:
- services/api/app/api/v1/report_context.py (+22): new helper _resolve_inside (lines 297-306) refusing any MANIFEST `file` entry that is not a plain name resolving inside its own pack folder (blocks `..`/absolute/nested), applied in _pack_url_map (line ~324). Pure loader path-containment hardening (G5).
- tests/api/test_report_context_provider.py (+49): switch-off call-count assertion in test_flag_off_returns_none_and_makes_no_connector_call (line 61); new test_recorded_pack_loader_refuses_a_path_escaping_the_pack (line 155, parametrized).
- tests/connectors/test_mappluto_window_arcgis.py (+47): window-pack integrity — test_manifest_lists_exactly_the_recorded_files (150), test_file_bytes_match_manifest_sha256 (164), test_pack_has_readme_and_byte_exact_gitattributes (173).

3. NO CHANGE TO WHAT I VERIFIED. Byte-identical across the two heads (git diff empty) for: the connector mappluto_window_arcgis.py; the builder map_context.py; BOTH schema copies (schemas/v1 and app/_contract_schemas/v1); all three recorded pack files + MANIFEST; and both new fixtures. Therefore connector behaviour, field mapping, units, null/paging/rate-limit/schema-drift behaviour, pack bytes and the 1.1.0 schema are UNCHANGED. The report_context.py edit is containment-only: for the real pack whose MANIFEST entries are all plain filenames, _resolve_inside resolves exactly as before, so the harness url_map and the built document are identical — it only adds a refusal path for a hostile/broken MANIFEST. It changes no fetch/assembly result.

RE-RUN AT NEW HEAD (lanes venv, offline, direct exit code):
- pytest tests/connectors/test_mappluto_window_arcgis.py tests/contracts/test_map_context_window.py tests/contracts/test_map_context_contract.py tests/api/test_report_context_provider.py → 47 passed, PYTEST_EXIT=0 (8 more than the prior 39, matching the added tests). No live request made (none needed).
- Schema/pack validators not re-run beyond this because the schema and fixture bytes are provably identical to the head I already validated green (validate_contracts.py exit 0; sync --check exit 0 there).

4. NOTHING IN THE DELTA BREAKS ANYTHING I PASSED. The change strictly adds a security guard plus tests; no regression on S1-S8 or the six G1 checks.

VERDICT (task I cover, M5-T154 G1) at 6c8c9f7d: PASS.

END-OF-REPORT
```

### Return 3 of 8: G3 code review (all three tasks) (return-w22-code.md)

```
Transmission: part 1 arrived first; part 2 was requested from the same reviewer and is joined here unchanged.

CODE-REVIEW GATE (G3) — Wave 22 "site context" — tasks M5-T154, M5-T155, M5-T156
Reviewer: code-reviewer (independent AI agent; I produced none of this work). Read-only.
Head under review: 3619744ebba6698cfd699f47d836294bdf979881 on task/wave22-site-context (confirmed `git -C /root/project/w-wave20 rev-parse HEAD`). Base: main 9ab3a47e6a55.
Method: product files inspected at the head; required suites rerun in a scratch extract (`git -C /root/project/w-wave20 archive 3619744 | tar -x -C <scratch>`) with `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`; 8 mutations run in-memory (no repo write). No server started; ports 3000/3001/8000 untouched.

PART 1 of 2

=================== VERDICTS ===================
- M5-T154 (map data / connector / provider / schema): PASS with 1 required correction (a weak test; the production code is correct).
- M5-T155 (context drawings): PASS (1 advisory modularity recommendation; non-blocking).
- M5-T156 (the report): PASS.

Note on scope: these are the CODE-side (G3) verdicts. The task packets also require a `directive-compliance-verifier` pass (its verification.json rows for all three tasks are still "pending", verifier "") and a `visual-quality-reviewer` pass for M5-T155/M5-T156. Those are separate reviewers; R938 ("looks like my competitors") and the printed-page look are a visual-reviewer judgement, not decided here. Acceptance still needs those passes.

=================== REQUIRED CORRECTIONS ===================
M5-T154-C1 (weak test, non-blocking): `services/api/tests/api/test_report_context_provider.py:57` `test_flag_off_returns_none_and_makes_no_connector_call` does NOT actually enforce "makes no connector call". Its `_boom` fetchers raise AssertionError, but `_assemble` (`services/api/app/api/v1/report_context.py:214`, `except Exception ... return None`) swallows that into None. I confirmed by mutation: removing the flag gate (`report_context.py:275-277`) so the provider always assembles still makes the test PASS (see survivor below). The gate itself is correct (I read it and the flag-off path returns None with zero calls), so this is a test-adequacy gap for the S5 "no call" half, not a code defect. Fix: assert a call counter == 0 independent of the return, or make `_boom` raise a BaseException (e.g. SystemExit) the broad except won't catch.

=================== CHECK 1 — Law boundary (Y6, Y13) ===================
PASS. The drawings and report compute no law. `street_areas.py` derives street space purely as window-minus-tax-lots (shapely); `site_context_plan.py` draws only street_area / subject_lot / neighbour_lot / building_footprint + street names, mapped widths and the subject's own edge lengths (drawing measures of the outline). No yard/court/setback/coverage/envelope/building-position. Enforced by `tests/drawings/maps/test_site_context_plan.py::test_s7_no_law_is_drawn` (kinds ⊆ {street_area, subject_lot, neighbour_lot, building_footprint}; disjoint from a LAW_KINDS set). `contracts/map_context.py` places geometry verbatim and only formats; `parse_mapped_width_ft` returns a number only for one plain number (D-052). report figures come from the results/map documents (`readers.py` is defensive `.get`, invents nothing). Nothing is labelled Verified: grep of the new maps/report/provider/contract code found no "Verified"; `test_s8_no_developer_words` caps "Verified" at 1 (the status-key legend). The site plan draws EXISTING OTI building footprints — this is required by R936 ("the existing buildings") and is not a proposed/placed building; Y8's "no footprint" (the proposed building) is honoured by printing the fixed not-placed line and drawing no building on the subject lot. Consistent, not a law computation.

=================== CHECK 2 — One-outline check (Y5) ===================
PASS. `drawings/report/page_location.py::outlines_match` shifts both outlines to their own min x/y and compares vertex-for-vertex within 0.01 ft, any start vertex and either winding; mismatched vertex counts fail closed. `builder.py:65-74` draws the map-based site plan ONLY when `surroundings.available` (outline matched); otherwise today's lot-only plan — so exactly one outline is ever drawn. Covered by `tests/drawings/report/test_location_sheet.py::test_s2_one_outline_check_passes_for_the_benchmark`, `::test_s2_moved_outline_drops_the_surroundings` (a 0.5-ft interior move drops the maps, keeps the lot-only plan, prints the limitation line, and the location sheet draws no SVG), `::test_s2_tolerance_is_one_hundredth_of_a_foot`.

=================== CHECK 3 — Provider & connector ===================
PASS. `report_context.default_report_map_context_provider` returns None with zero connector calls unless `live_spatial_provider_enabled()` is true (`report_context.py:275-277`). `_assemble` never raises: every fetch is guarded; a `MapPlutoWindowConnectorError`/any error demotes that layer to not_available; a missing subject outline returns None; a build/validation failure returns None. The window connector (`connectors/mappluto_window_arcgis.py`) requests OUT_FIELDS = (OBJECTID, BBL, Block, Lot, Address, Version) only — no owner/personal field — and fails CLOSED by raising typed errors on wrong CRS, ArcGIS error object, paging pathology, malformed geometry (no partial result); the subject is excluded from neighbours. Adapter (`drawings/maps/adapter.py`) is fully fail-closed on the 1.1.0 layers (XML-illegal text, non-finite, out-of-range, unclosed/degenerate/non-simple/zero-area rings, hole-outside-exterior, too-many-features, empty window, short line). The recorded-pack entry point `recorded_pack_provider` reads only MANIFEST-listed files under the given pack folder plus its documented base-pack sibling (`../benchmark_215_16_northern`, per ruling Y4) — no arbitrary path traversal; app-package-only. Covered by the connector S1/S2 tests and the provider S5/S8 tests (all green). Caveat = M5-T154-C1 above.

=================== CHECK 4 — Escaping / no external resource ===================
PASS. All SVG text and attribute values go through `drawings/kit/svg.py::escape` (XML-escapes &,<,>,\" and RAISES on XML-illegal chars; adapter rejects them earlier); `svg_document` escapes the title; the bar chart escapes name/value. Report HTML uses `drawings/report/html.py::el` which HTML-escapes text children; `raw()` is only used for self-escaped SVG and module-built fragments. No `<script>` in the report code; no `<image>`/`xlink:href`/external SVG resource in the new maps/report modules. The only hyperlink is the intended, escaped official ZR law link (`page_evidence.py:21` `https://zoningresolution.planning.nyc.gov/`, via `escape_attr`), present on main. `test_s2_streets...`/`test_s5_no_url_field_name_or_code_word`/`test_s8_no_developer_words` back this up.

END OF PART 1 — PART 2 follows.

PART 2 of 2 — Wave 22 G3 code-review (head 3619744ebba6698cfd699f47d836294bdf979881)

=================== CHECK 5 — Modularity ===================
PASS (with one advisory recommendation). `python3 tools/modularity_check.py --check` run read-only in the reviewed checkout `/root/project/w-wave20`: "selected 786 files; failures 0; warnings 33", exit 0. (The scratch extract is not a git tree, so modularity_check — which calls `git ls-files` — must run in the checkout; it only reads.)
`services/api/app/drawings/maps/site_context_plan.py` = 863 physical lines / 719 code lines; it draws two modularity warnings (symbol_ceiling + review_signal "above the warning threshold"), but is NOT above the justification/hard threshold, so the gate passes. The file legitimately hosts the shared scene primitives (ViewFrame/projection, fit_view scaling, label placement/collision, street-area drawing, caption/furniture composition) that the two genuinely-thin sibling modules reuse — `block_map.py` (80 lines) and `neighbourhood_map.py` (58 lines). It does, however, mix several concerns and was born large.
Advisory (non-blocking): a future split extracting the view-frame/projection math and the label-placement helpers into a `context_scene.py` would clear the warning; it is out of this packet's allowed paths, so flagging it for a later task is the right call, not a scope-breaking edit now. No other changed file grew without need (new files street_areas 307, adapter +, model +, report pages small; the connector 718 and map_context 719-code are under their thresholds per the check).

=================== CHECK 6 — Tests ===================
PASS. Every packet scenario has a behaviour-coupled test (S1–S8 for T154/T155; S1–S9 for T156), all green in the full run. Changed assertions in PRE-EXISTING test files — none weakened:
- `tests/contracts/test_map_context_contract.py` (M5-T154, the two the brief named): VALID count 4→5 and INVALID set gains `street_mapped_width_not_a_number.json` (STRONGER); version enum `["1.0.0"]`→`["1.0.0","1.1.0"]` (correct additive reflection, still an exact pin). Both strengthenings, matching the recorded scope correction.
- `tests/drawings/report/test_report_pages.py` Q3 (M5-T156): the stub `_FakeMap`/monkeypatched renders were replaced by the REAL recorded window pack (stronger, realistic); the one relaxed assertion ("Context maps" moved from the site-section text to the whole-report text) reflects the label moving to page 1's coverage block, and is compensated by the dedicated `test_location_sheet.py::test_s5_context_maps_moves_only_when_printed`, which pins the move precisely. Net: not a meaningful weakening. Two new no-split table tests are additive.
- `apps/web/e2e/report-print.flag-on.spec.ts` (run by the orchestrator, not here): purely additive location-sheet assertions (title order, 2 SVGs, wide neighbourhood + compact block, caption-with-edit-date, no dataset id, no `<img>`, no photo words). No existing assertion weakened.

Eight independent mutations (in-memory; green BEFORE, red AFTER; original restored), spread 3/3/2 across the tasks — each caught, test named:
  M1 T154 connector OUT_FIELDS += "OwnerName" → CAUGHT test_mappluto_window_arcgis::test_request_never_asks_for_an_owner_name
  M2 T154 parse_mapped_width_ft fullmatch→search ("60-75"→60) → CAUGHT test_map_context_window::test_mapped_width_parser_only_parses_a_plain_number
  M3 T154 _window_polygon skips geometry validation → CAUGHT test_mappluto_window_arcgis::test_malformed_ring_is_refused_whole
  M4 T155 edge_sharing_lots→[] → CAUGHT test_site_context_plan::test_s2_only_the_subject_and_its_edge_sharing_neighbours_are_labelled
  M5 T155 subtitle_from_bbl→raw BBL → CAUGHT test_site_context_plan::test_s2_has_north_arrow_scale_bar_legend_title_and_subtitle
  M6 T155 street_areas _runs_through→() (gaps unnamed) → CAUGHT test_street_areas::test_street_area_is_the_window_minus_the_lots_named_by_its_centre_lines
  M7 T156 outlines_match default tol 0.01→1.0 → CAUGHT test_location_sheet::test_s2_tolerance_is_one_hundredth_of_a_foot
  M8 T156 map_caption _readable_date→None (captions lose dates) → CAUGHT test_location_sheet::test_s1_captions_name_sources_and_their_dates
One deliberate SURVIVOR (the basis of M5-T154-C1): removing the flag gate so the provider always assembles still PASSES `test_report_context_provider.py::test_flag_off_returns_none_and_makes_no_connector_call` (verified via pytest in-process: `1 passed`). The broad `except Exception` in `_assemble` swallows the probe fetcher's error into None, so the test's "no connector call" promise is vacuous. Production gating is correct; only the test needs hardening.

=================== CHECK 7 — Required runs (scratch copy, direct exit codes) ===================
- `python -m ruff check .` (services/api) → exit 1. The ONLY 2 errors are in `services/api/app/rules/coverage/render_coverage_matrix.py` (F841 unused `column_order` line 70; E501 line 94) — a file NOT in this diff, byte-identical to base main, flagged only by the newer ruff 0.13.0 in this venv. Ruff restricted to the 37 wave-22-changed files: "All checks passed!", exit 0. So the wave is clean; the whole-tree exit 1 is a pre-existing ruff-version artifact, not a wave-22 defect (CI uses its pinned ruff, under which the producer reported exit 0).
- `pytest -q -p no:cacheprovider tests/connectors tests/contracts tests/api tests/spatial tests/drawings tests/cad tests/journey` → `5057 passed, 6 skipped` in 244s, exit 0.
- `python .github/scripts/validate_contracts.py` → "Checked 23 schema file(s); 0 failure(s)", exit 0 (the new valid 1.1.0 fixture passes; the invalid `street_mapped_width_not_a_number.json` is correctly rejected).
- `python3 services/api/scripts/sync_contract_schemas.py --check` → "runtime-bundled contract schemas are byte-identical to the canonical source", exit 0.
Schema change confirmed additive: `contract_version` enum appends "1.1.0"; context_window/tax_lots/streets are OPTIONAL members of map_context (not in required), so every 1.0.0 document stays valid (`test_every_existing_1_0_0_example_still_validates` green); only known keywords used (type arrays for the number-or-null / string-or-null fields).

=================== DIRECTIVE REQUIREMENTS (code side) ===================
Code-side satisfaction observed: R936 (lot among surroundings — streets, widths, neighbours, existing buildings drawn), R937 (neighbourhood map + block close-up with sources/dates), R939 (fixed not-placed line on site plan and scenario sheet; no proposed building drawn), R940 (no street photo, no empty frame, no photo wording; the figure grid takes a third figure later; `test_s4` green). R938 (competitor visual standard) and the printed-page look are the visual-quality-reviewer's call. The directive-compliance-verifier per-ID pass (verification.json rows pending) remains required before acceptance.

=================== KEY FILES ===================
/root/project/w-wave20/services/api/app/connectors/mappluto_window_arcgis.py
/root/project/w-wave20/services/api/app/api/v1/report_context.py
/root/project/w-wave20/services/api/app/contracts/map_context.py
/root/project/w-wave20/packages/contracts/schemas/v1/map_context.schema.json
/root/project/w-wave20/services/api/app/drawings/maps/{street_areas,site_context_plan,block_map,neighbourhood_map,adapter,model}.py
/root/project/w-wave20/services/api/app/drawings/report/{page_location,builder,page_site_context,page_decision_summary,page_scenario_sheet,map_caption,drawings_embed,readers,sources,html}.py
/root/project/w-wave20/services/api/app/api/v1/report_read.py
/root/project/w-wave20/services/api/tests/api/test_report_context_provider.py (M5-T154-C1 target)

=================== SUMMARY ===================
M5-T154 PASS (required correction M5-T154-C1: strengthen the "no connector call" test). M5-T155 PASS (advisory: consider splitting site_context_plan.py in a later task). M5-T156 PASS. No FAIL, no BLOCKED. Orchestrator to record the G3 gate and still obtain the directive-compliance-verifier and visual-quality-reviewer passes before acceptance.

END-OF-REPORT
```

### Return 4 of 8: G3 delta review at 6c8c9f7d (delta-w22-code.md)

```
DELTA REVIEW — Wave 22 — code-reviewer (G3). New head 6c8c9f7d526539bc1d5d8ef942d8a3770aba420b on task/wave22-site-context (confirmed `git rev-parse HEAD`). Read-only; no server; scratch extract + lanes venv.

=== 1. MY ITEMS — both fixed ===
M5-T154-C1 (switch-off test was vacuous) — FIXED.
- `services/api/tests/api/test_report_context_provider.py:62` `test_flag_off_returns_none_and_makes_no_connector_call` now installs COUNTING spies that return valid replay values and asserts `calls == {lot:0, window:0, footprints:0, streets:0}` (line 86). It no longer uses a raising double that `_assemble` would swallow.
- Proof: I re-ran my gate-removal mutation (provider always assembles) against this test in-process → now FAILS at `test_report_context_provider.py:86` (AssertionError), `PYTEST_RC=1`. Previously it survived. The regression is now caught.
- Bonus hardening I had flagged under CHECK 3: `report_context.py:297` `_resolve_inside` rejects any MANIFEST `file` entry that is non-plain, `..`-traversing or absolute (`ValueError`); covered by new parametrized `test_recorded_pack_loader_refuses_a_path_escaping_the_pack` (`../escape.json`, `sub/deep.json`, `/etc/passwd`).

Advisory (split site_context_plan.py) — DONE.
- View/projection/label helpers moved to new `services/api/app/drawings/maps/context_scene.py` (446 code lines); `site_context_plan.py` dropped 719→509 code lines (595 physical). `modularity_check --check` at the new head: 0 failures, 31 warnings (down from 33); neither file is flagged any more. Siblings `block_map.py`/`neighbourhood_map.py` remain thin re-users.

=== 2. CHECKS RE-RUN AT 6c8c9f7d (direct exit codes) ===
- ruff on the 30 changed/new wave-22 py files: "All checks passed!", exit 0. (The whole-tree exit-1 remains only the pre-existing `render_coverage_matrix.py`, not in this diff.)
- `pytest -q -p no:cacheprovider tests/connectors tests/contracts tests/api tests/spatial tests/drawings tests/cad` (scratch extract): 5097 passed, 6 skipped, exit 0.
- `validate_contracts.py` exit 0; `sync_contract_schemas.py --check` exit 0 (schemas byte-identical).
- `modularity_check --check` exit 0.
- Print overflow (per brief): `node print-w22e/overflow.cjs print-w22g/report.html` → `{"W":688,"docW":688,"n":0,"first":[]}`, exit 0 — nothing wider than the page; the report prints at true size (the 889→688 shrink is fixed).

=== 3. DID THE DELTA BREAK ANYTHING I PASSED? ===
No. Law boundary (CHECK 1) intact: the new `existing_building` kind (dashed outline, legend "Existing building (city records)", DXF A-BLDG-EXST) is a factual existing structure required by R936, not a proposed/law feature; `test_s7_no_law_is_drawn` still asserts disjoint from the unchanged LAW_KINDS set and only widens the whitelist to include it. Escaping, fail-closed parsing, one-outline check, provider gating, additive schema — all still green in the rerun. The new map/report behaviours (lot-only fallback when a layer is missing; two stacked wide maps; no near-empty page; tall tables break with repeated headers while short ≤70 mm tables stay whole; scenario sheet kept together) are additive and carry their own passing tests.

=== 4. VERDICTS AT 6c8c9f7d ===
- M5-T154: PASS (no remaining corrections).
- M5-T155: PASS (advisory resolved).
- M5-T156: PASS.

Acceptance still additionally needs the directive-compliance-verifier per-ID pass (verification.json rows still pending) and the visual-quality-reviewer pass (R938 look / printed pages) — outside this code gate.

END-OF-REPORT
```

### Return 5 of 8: G4 QA review (all three tasks) (return-w22-qa.md)

```
GATE REPORT — G4 (independent QA, read-only) — wave 22 "where is the lot?"
Reviewer: qa-engineer (AI agent; not a human/professional review). Produced none of this work.
Head under review: 3619744ebba6698cfd699f47d836294bdf979881 on task/wave22-site-context (confirmed `git rev-parse HEAD`; clean tree). Base main: 9ab3a47e6. The head differs from the print head 2d68f2919 only in project-control/reports/M5-T155-producer-report.md, so every product file is identical — the print-w22d evidence is faithful to this head.
Method: product files extracted to a scratch tar copy OUTSIDE the repos; tests/mutations run there with /root/project/lanes-runtime/venv/bin/python, PYTHONDONTWRITEBYTECODE=1. No server started; ports 3000/3001/8000 untouched; no Playwright; no network (replay only); no ledger/git/gh writes.

================= VERDICTS =================
- M5-T154 (map data / provider / recorded pack): PASS WITH REQUIRED CORRECTIONS (C1, C2). Behaviour correct and all independent values verified; two test-adequacy gaps.
- M5-T155 (context drawings): PASS. No defect or test gap found; one non-blocking modularity observation.
- M5-T156 (the report): PASS WITH REQUIRED CORRECTIONS (C3 behavioural, C4 test). Printed report is correct and clean on the default and maps-present paths; one flag-gated fallback defect with no test.

Corrections are recorded as PASS but BLOCK acceptance until applied (repo gate-verdict semantics). Each is numbered below with file:line and the one-line fix.

================= REQUIRED CORRECTIONS =================
C1 (M5-T154, S5 test gap). services/api/tests/api/test_report_context_provider.py:57-65 — test_flag_off_returns_none_and_makes_no_connector_call does NOT actually verify the "makes no connector call" clause (ruling Y4/S5 "off gives None and makes no call"). My mutation M3 (disable the flag gate in app/api/v1/report_context.py:276) SURVIVED this test: `_assemble` (report_context.py:213-216) wraps fetch_lot in `except Exception` and returns None on any error, so the _boom double's AssertionError is swallowed and the provider still returns None. Fix: assert ZERO calls with a counting spy (increment a list on each fetcher call; assert the list is empty while the flag is off), instead of relying on a raising double.

C2 (M5-T154, S6 test gap). The new window pack has no integrity test for 2 of its 3 recordings. Only the MapPLUTO window digest is guarded (test_mappluto_window_arcgis.py:82 via result.raw_digests[0]==window_digest). building_footprints_window_*.json and dcm_street_centerline_window_*.json have NO digest assertion, and nothing checks README/.gitattributes presence or that the MANIFEST file list equals the files on disk — the base pack has exactly such a test (tests/connectors/test_benchmark_215_16_northern_fixtures.py) but the window pack does not. Fix: add a mirror test iterating MANIFEST["files"], asserting sha256(bytes)==entry["sha256"] for all three, MANIFEST list==on-disk non-recording set, and the gitattributes `* -text` rule. (I verified all three digests + byte counts match the MANIFEST by hand — the files ARE correct; only the regression guard is missing.)

C3 (M5-T156, behavioural; flag-gated). services/api/app/drawings/report/builder.py:66 — `if surroundings.available and surroundings.report_plan is not None:` does not check `.is_drawing`. When a 1.1.0 map document is present and the one-outline check passes but tax_lots OR building_footprints is not_available while streets IS available, report_plan is a non-drawing Embedded; the constraints sheet then prints the site-context-plan's Unavailable reason line instead of falling back to today's lot-only plan + the R843 limitation line. This deviates from S6/R843 ("the site plan is today's lot-only plan with the limitation line"). page_decision_summary.py:110 handles the same non-drawing Embedded correctly (page 1 falls back), so page 1 is fine — only the constraints branch is wrong. Reachable only when LIVE_SPATIAL_PROVIDER_ENABLED is on (OFF by default, so unreachable in the shipping config and in the printed evidence, where the harness binds the full recorded pack). Fix: add `and surroundings.report_plan.is_drawing` to builder.py:66 (match page_decision_summary.py:110). If the orchestrator rules the live path out of this gate's scope (flag off, activation still an owner hold), C3 may be tracked as a next-task item instead of blocking — but the brief's check 3 explicitly asked me to exercise "each layer not available," and it fails there.

C4 (M5-T156, test gap paired with C3). No report-level test covers the partially-unavailable map document (document present, outline matches, one layer not_available). S6's test (test_s6_without_map_data_one_line_never_blank) covers only provider=None. Add a test building the benchmark report with tax_lots (and separately building_footprints) not_available and streets available, asserting the constraints sheet shows today's lot-only plan (an <svg>) plus the limitation line — the path C3 fixes.

Observation (M5-T155, non-blocking): app/drawings/maps/site_context_plan.py is 719 SLOC (tool's own counter) — a modularity WARN (>600) but under the 750 justify and 1000 hard thresholds; modularity_check passes. It is a NEW file created this wave; a clean split (a context_scene.py) is a reasonable future refactor but was outside the packet's allowed paths. Not a gate blocker.

================= CHECK 1: SCENARIO-TO-TEST TABLE =================
All test files read expected values from the recorded packs / documents, never from a program run. "catches?" = would the named test fail if the behaviour broke (confirmed by mutation where noted).

M5-T154
- S1 neighbouring lots in a window → test_mappluto_window_arcgis.py::test_window_returns_each_neighbour_once_in_2263 / ::test_subject_lot_is_not_among_the_neighbours / ::test_request_url_is_byte_identical_to_the_manifest / ::test_request_never_asks_for_an_owner_name. Catches: yes (M1 subject-included → 201≠200 caught).
- S2 connector refuses bad answers → ::test_wrong_crs_is_refused / ::test_arcgis_error_object_is_refused / ::test_paging_fault_is_refused / ::test_malformed_ring_is_refused_whole (each pytest.raises a typed error). Catches: yes.
- S3 map document 1.1.0 → test_map_context_window.py::test_document_is_schema_valid_1_1_0_with_all_layers / ::test_every_existing_1_0_0_example_still_validates / ::test_outlines_and_paths_are_input_geometry_unchanged. Catches: yes (M4 enum-drop caught).
- S4 street widths → ::test_mapped_width_parser_only_parses_a_plain_number / ::test_width_text_is_kept_verbatim_from_the_source. Catches: yes (M2 and M9 caught).
- S5 provider gating → test_report_context_provider.py::test_flag_off_returns_none_and_makes_no_connector_call / ::test_flag_on_with_replayed_fetchers_returns_the_document / ::test_a_refusing_fetcher_makes_only_that_layer_unavailable / ::test_a_refusing_window_fetcher_makes_only_tax_lots_unavailable / ::test_no_subject_outline_gives_none. THIN: the "no connector call" clause is NOT caught (M3 survived) → C1. The other clauses catch.
- S6 recorded pack integrity → THIN: only the MapPLUTO digest is asserted; footprints/streets recordings and README/.gitattributes/MANIFEST-list are unguarded → C2.
- S7 independent window check → ::test_independent_window_check (shared edge 99.98±0.01; widths 100/60/60). Catches: yes.
- S8 harness binding → ::test_recorded_pack_provider_returns_the_same_document. Catches: yes.

M5-T155
- S1 street areas → test_street_areas.py::test_street_area_is_the_window_minus_the_lots_named_by_its_centre_lines / ::test_a_gap_no_centre_line_runs_through_is_drawn_unnamed / ::test_slivers_under_the_minimum_are_dropped / ::test_street_area_never_overlaps_a_tax_lot / ::test_street_areas_are_deterministic / ::test_clip_street_keeps_only_the_in_window_pieces. Catches: yes (M5 caught).
- S2 site plan among surroundings → test_site_context_plan.py::test_s2_subject_is_coloured_with_its_edge_lengths / ::test_s2_only_the_subject_and_its_edge_sharing_neighbours_are_labelled / ::test_s2_streets_are_named_with_their_mapped_widths / ::test_s2_has_north_arrow_scale_bar_legend_title_and_subtitle / ::test_s2_rotated_to_the_frontage_with_grid_north_noted. Catches: yes (M6 caught).
- S3 block + neighbourhood → test_context_maps.py::test_s3_block_marks_only_the_subject_and_names_the_streets / ::test_s3_neighbourhood_shows_the_street_network_with_the_lot_marked / ::test_s3_neighbourhood_is_north_up_and_block_is_rotated / ::test_s3_each_street_is_named_once / ::test_block_street_areas_stay_inside_the_data_window. Catches: yes.
- S4 printed size → test_site_context_plan.py::test_s4_report_frame_fits_and_every_label_is_at_least_7pt + test_context_maps.py::test_s4_fits_and_every_label_is_at_least_7pt_with_no_overlaps / ::test_s4_caption_is_returned_with_dates. Catches: yes (label<7pt caught).
- S5 sources and limits → ::test_s5_caption_names_each_source_and_its_date / ::test_s5_the_street_area_and_survey_notes_are_present / ::test_s5_no_url_field_name_or_code_word_in_any_drawn_text. Catches: yes.
- S6 missing layers → test_site_context_plan.py + test_context_maps.py ::test_s6_* and test_context_adapter.py fail-closed suite. Catches: yes.
- S7 no law drawn → test_site_context_plan.py::test_s7_no_law_is_drawn (kinds_drawn ⊆ {street_area, subject_lot, neighbour_lot, building_footprint}). Catches: yes.
- S8 deterministic → ::test_s8_same_input_gives_byte_identical_svg (both files, per frame). Catches: yes.

M5-T156
- S1 location sheet → test_location_sheet.py::test_s1_location_sheet_opens_page_type_two / ::test_page1_carries_the_summary_frame_site_plan / ::test_location_page_layout_full_neighbourhood_and_compact_block / ::test_s1_captions_name_sources_and_their_dates / ::test_s1_captions_are_plain_no_dataset_id_no_doubled_date / ::test_s1_six_page_types_unchanged. Catches: yes.
- S2 one outline → ::test_s2_one_outline_check_passes_for_the_benchmark / ::test_s2_moved_outline_drops_the_surroundings / ::test_s2_tolerance_is_one_hundredth_of_a_foot. Catches: yes (M7 caught).
- S3 not yet placed → ::test_s3_not_yet_placed_on_site_plan_and_scenario_sheet. Catches: yes (M8 caught).
- S4 no photo → ::test_s4_no_photo_no_empty_frame_no_photo_wording. Catches: yes.
- S5 scope list → ::test_s5_context_maps_moves_only_when_printed. Catches: yes.
- S6 without map data → ::test_s6_without_map_data_one_line_never_blank / ::test_s6_resolve_returns_unavailable_without_a_document. THIN: covers provider=None only; the per-layer-unavailable report path is uncovered → C4 (and the defect C3 lives there).
- S7 route → test_report_read_context.py::test_s7_report_shows_surroundings_with_the_recorded_pack / ::test_s7_provider_is_asked_for_the_same_lot_as_the_body / ::test_s7_provider_error_never_fails_the_report / ::test_s7_default_provider_is_mapless_like_wave_21 / ::test_s7_flag_off_is_still_404. Catches: yes.
- S8 no typed number / no dev words → ::test_s8_no_developer_words_with_maps_present. Catches: yes.
- S9 contract entry → ::test_s9_presentation_contract_has_the_dated_entry. Catches: yes.

================= CHECK 2: INDEPENDENT VALUES (from the recorded pack, re-derived myself) =================
Parsed the raw pack JSON directly (not via the program's reported counts) and computed with shapely:
- Lot 1 (BBL 4073340001) shares 99.9765 ft with the subject (within 0.01 ft of 99.98). CONFIRMED.
- Lot 11 (BBL 4073340011) shares 101.7090 ft with the subject south line (~101.71). CONFIRMED.
- Lot 61 (BBL 4073340061) shares 2.2244 ft with the subject south line (~2.22). CONFIRMED.
- Subject lot 70 edge lengths: 99.98 / 103.88 / 99.98 / 101.71 / 2.22 ft — matches the page-3 drawing labels (103.88, 99.98, 99.98) and the "101.71 ft" south-line label.
- Subject EPSG:2263 bbox (1048788.63, 216310.44, 1048911.58, 216431.10) = exactly the window-sizing bbox in MANIFEST (±400 / ±1000 padding). CONFIRMED.
- DCM widths from the raw recording: Northern Boulevard "100"→100, 215 Place "60"→60, 215 Street "60"→60. Also 219 Street "Unknown"→null, 42 Avenue ">90"→null, Bell Boulevard "80-100"→null. All match D-052. CONFIRMED.
- The test that asserts these (test_independent_window_check, test_width_text_is_kept_verbatim_from_the_source) reads them from the recorded pack via the real connectors, not from a retyped program run.

================= CHECK 3: PARTIAL DATA (I ran the report builder myself) =================
Drove app.drawings.report.build_report_html on the benchmark results with: no map document; each layer not_available (tax_lots / streets / building_footprints); a 1.0.0 document; a moved outline (0.5 ft). All six page types in every case; no exception in any case; the "Where is the lot?" sheet always present (never a blank sheet).
- no map document: location sheet prints one line ("The surroundings are not shown for this property…"); constraints sheet shows today's lot-only plan. CORRECT (S6).
- streets not_available: all drawings fail → available=False → one line + lot-only plan. CORRECT.
- 1.0.0 document: one line + lot-only plan. CORRECT.
- moved outline: one-outline check fails → one line + lot-only plan; two outlines never drawn together. CORRECT (S2).
- tax_lots not_available (real provider reason "Neighbouring tax lots could not be retrieved from the city tax map for this area."): the location sheet still draws the neighbourhood map, but the constraints sheet prints that reason line and draws NO site plan — it does NOT fall back to today's lot-only plan. DEVIATION → C3.
- building_footprints not_available (real reason "No building-footprint features were provided for this lot."): same deviation → C3.
Good news within C3: the production reason strings are plain English (no snake_case leak; whole-report visible-text snake_case scan = []). The "could not be retrieved" snake_case I first saw was from my synthetic reason string, not the product.

================= CHECK 4: PAGES (from print-w22d/report.pdf, pdftotext -layout + pdfinfo) =================
pdfinfo: 8 A4 pages (594.96 x 841.92 pt), Chromium/Skia, title "215-16 NORTHERN BOULEVARD, Queens".
- No page holds only a lone line or 1-3 rows. Page 8 is the full 6-row status-label key with its heading (moved whole). The scenario sheet keeps the apartment estimate with its schedule. OK.
- No full-size drawing printed twice: page 1 = compact summary site plan; page 2 = full-width neighbourhood map + compact block close-up; page 3 = the one full-size site plan among surroundings. The site context plan appears as summary (p1) and report (p3) frames — different frames, not the same full-size drawing twice. OK.
- No dataset id, no doubled date, no "via NYC Open Data", no "photo"/"Street View" wording. The only "aerial/photograph" hit is the scope-list "Not yet: … Aerial and street photographs" (exactly as Y9 requires). Each source edit date appears once per caption. Confirmed in both report.pdf text AND the raw report.html as the website received it (no 5zhs/2jue, no Street_NM/Streetwidth/ZONEDIST/EPSG/FeatureServer/OwnerName, no <img>, no snake_case in visible text, 6 report-page divs).
- Scope list consistent with what is printed: "In this report: … Context maps" (context maps ARE printed, pages 1-3) and "Not yet: … Aerial and street photographs" (not printed). CONSISTENT.

================= CHECK 5: MUTATIONS (one at a time, in the scratch copy, reverted; restores verified byte-identical) =================
M1 window keeps the subject lot among neighbours → CAUGHT: test_mappluto_window_arcgis (AssertionError 201==200).
M2 mapped-width parser reads "60-75" as 60 → CAUGHT: test_map_context_window (assert 60 is None).
M3 provider ignores the live flag (bypass the gate) → NOT CAUGHT (test still passed). Root cause: _assemble swallows the boom fetcher's error and returns None. → C1.
M4 schema version enum drops 1.1.0 → CAUGHT: test_map_context_contract (enum ['1.0.0'] != ['1.0.0','1.1.0']) and test_map_context_window.
M5 street engine skips subtracting the first tax lot → CAUGHT: test_street_areas (street area overlaps a tax lot by 6400 sq ft).
M6 edge-sharing-neighbour labelling returns every neighbour → CAUGHT: test_site_context_plan (lot_number set != {Lot 70, Lot 1, Lot 11, Lot 61}).
M7 one-outline check tolerance 0.01→1.0 ft → CAUGHT: test_location_sheet (test_s2_tolerance_is_one_hundredth_of_a_foot).
M8 not-placed line reworded → CAUGHT: test_location_sheet (test_s3_not_yet_placed).
M9 mapped-width regex widened to accept "80-100" → CAUGHT: test_map_context_window (ValueError float('80-100')).
Result: 9 mutations, 8 caught, 1 survivor (M3) — the survivor is itself the basis of C1.

================= CHECK 6: FOCUSED RUNS (scratch copy, direct exit codes) =================
- ruff on the wave's own touched python (app/api/v1/report_context.py, report_read.py, connectors/mappluto_window_arcgis.py, contracts/map_context.py, drawings/maps, drawings/report, drawings/kit/styles.py, and the wave's test files) → "All checks passed!", exit 0.
- `pytest -q -p no:cacheprovider tests/connectors tests/contracts tests/api tests/spatial tests/drawings tests/cad tests/journey` → 5057 passed, 6 skipped, exit 0 (239 s).
- modularity_check.py --check → could not run in a non-git tar copy ("git ls-files failed", exit 128 — environment artifact, not a defect). I verified file SLOC with the tool's own counter: site_context_plan.py 719 (WARN, under 750/1000), mappluto_window_arcgis.py 583, map_context.py 462, street_areas.py 256, page_location.py 140 — none hard-fails. Producers reported it green in their git worktrees; the control-plane/api CI will enforce at the exact head.
- .github/scripts/validate_contracts.py → "Checked 23 schema file(s); 0 failure(s)", exit 0 (the new map_context valid/invalid fixtures pass/reject correctly).

IMPORTANT ruff note on the full tree: `ruff check .` over the whole scratch tree exits 1 on app/rules/coverage/render_coverage_matrix.py (F841 unused `column_order`, E501 long line). This file is byte-identical to main (blob 193b48751…, unchanged by the wave) and is the KNOWN pre-existing blind spot DB-223: `.gitignore` pattern `coverage/` makes ruff skip app/rules/coverage/ in git-aware mode, so CI (and the producers' git worktrees) never see it, but a non-git copy does. NOT introduced by this wave and NOT a reason to fail these tasks; flagging so the full-tree red is not mistaken for a wave regression.

================= DIRECTIVE / OTHER NOTES =================
- Owner directives are behaviourally addressed: R936/R937 (where is the lot / no reference) → the location sheet + site plan among surroundings; R938 (doesn't look like competitors) → neighbourhood + block + site like the competitor page 4 (the visual-quality-reviewer judges the look); R939 → the plain not-placed line; R940/R551 → no photo now, the figure grid can take a third figure later; R843 → lot-only fallback + limitation line (with the C3 caveat for the partial case). Formal per-requirement verification at the content identity is the directive-compliance-verifier's pass (producer ≠ verifier), not mine.
- S6 pack digests, URLs byte-exact, and .gitattributes `* -text` all verified by hand against MANIFEST.
- The e2e harness (apps/web/e2e/harness/fixture_api.py:825-826) binds get_report_map_context_provider to recorded_pack_provider(benchmark_215_16_northern_window); report-print.flag-on.spec.ts carries location-sheet assertions (title order, ≥2 location SVGs, caption-with-edit-date, no dataset id, no raster image, no photo words). I did not run Playwright (orchestrator's job); the assertions match the printed evidence I verified.

END-OF-REPORT
```

### Return 6 of 8: G4 QA delta review at 6c8c9f7d (delta-w22-qa.md)

```
DELTA GATE REPORT — G4 QA, wave 22. Head 6c8c9f7d526539bc1d5d8ef942d8a3770aba420b on task/wave22-site-context (confirmed `git rev-parse HEAD`; checkout unchanged). Reviewed in a scratch tar copy outside the repos; lanes venv; no server/ports/network; read-only.

1) EACH OF MY CORRECTIONS — FIXED:
- C1 (T154, S5 "no call while off"). services/api/tests/api/test_report_context_provider.py:61-87 now uses a COUNTING spy and asserts calls=={lot:0,window:0,footprints:0,streets:0}. Re-ran my surviving mutation M3 (bypass the flag gate): now CAUGHT (rc=1). FIXED.
- C2 (T154, S6 pack integrity). tests/connectors/test_mappluto_window_arcgis.py:150-177: test_manifest_lists_exactly_the_recorded_files, test_file_bytes_match_manifest_sha256 (parametrized over ALL THREE recordings), test_pack_has_readme_and_byte_exact_gitattributes. The two previously-unguarded recordings (footprints, streets) now hash to MANIFEST. 8 named-tests run → passed. FIXED.
- C3 (T156, builder fallback). services/api/app/drawings/report/builder.py:66-67 now requires `and surroundings.report_plan.is_drawing`. My partial-data probe at this head: tax_lots-unavailable AND building_footprints-unavailable now draw today's lot-only plan on the constraints sheet (constraints_svg=True; previously False); still no exception, 6 page types, "Where is the lot?" present. FIXED.
- C4 (T156, test for C3). tests/drawings/report/test_location_sheet.py::test_c4_constraints_falls_back_to_lot_only_when_a_layer_is_unavailable (parametrized tax_lots, building_footprints) — asserts the lot-only <svg> + "Approximate" tax-map caption, no "Sources:", and the layer reason never reaches the report. PASSED. FIXED.
- Bonus hardening: the recorded-pack loader now refuses paths escaping its folder (report_context.py:303-306).

2) RE-RUN CHECKS AT NEW HEAD (direct exit codes):
- ruff on the wave's touched python INCLUDING the new app/drawings/maps/context_scene.py → "All checks passed!", exit 0.
- pytest -q -p no:cacheprovider tests/connectors tests/contracts tests/api tests/drawings tests/spatial → 4482 passed, 6 skipped, exit 0.
- Page checks on print-w22g/report.pdf (9 A4 pages): no dataset id / "via NYC Open Data" / "Street View" / "last edited" / field names / EPSG / FeatureServer; "aerial/photographs" only under the scope list's "Not yet"; "Context maps" under "In this report" (consistent); no lone-line or near-empty page (smallest, pages 7 and 9, are a full open-items continuation and the provenance + full 6-row status-key); no raster image.
- overflow.cjs (print-w22e) on print-w22g/report.html (headless chromium, file://, no server/port) → {W:688, docW:688, n:0}: zero elements wider than the page; scrollWidth==clientWidth. The wave-21 77% print-shrink (889 vs 688 px) is fixed — the report prints at true size.

3) DID THE DELTA BREAK ANYTHING I PASSED? No. The site_context_plan→context_scene refactor (scope correction 1) is fully covered by the passing maps suite (S1-S8 drawings, determinism, label provenance, no-law-drawn all still green). Modularity IMPROVED: site_context_plan.py 719→509 SLOC, context_scene.py 446 SLOC — both under the 600 WARN threshold (my earlier 719-SLOC WARN observation is resolved). All page/caption/not-placed/no-photo behaviour I passed before remains clean in print-w22g.

4) VERDICTS AT 6c8c9f7d:
- M5-T154: PASS.
- M5-T155: PASS.
- M5-T156: PASS.
No remaining required corrections.

END-OF-REPORT
```

### Return 7 of 8: G5 security review (M5-T154) (return-w22-security.md)

```
GATE REPORT — G5 (security) — Wave 22 site-context — one head / one PR

Task primarily under this gate: M5-T154 (new external window call behind a live switch + the report route's map-context provider). Shared-head security surfaces of M5-T155 (context drawings) and M5-T156 (report) were also checked where the G5 security checklist reaches them (upstream-string escaping, fail-safe, no personal data in the rendered report, no photo). Deep functional/visual correctness of T155/T156 belongs to their own reviewers' gates.

Reviewer: security-reviewer (independent; produced none of this work; AI, not a professional review). Read-only — no writes, no ledger writes, no network, no server/port touched.

HEAD VERIFIED: `git rev-parse HEAD` in /root/project/w-wave20 = 3619744ebba6698cfd699f47d836294bdf979881 on task/wave22-site-context (matches the brief). Base main 9ab3a47e6a55fc75e13140e910f0839541754874. Working tree clean. Product files identical to the orchestrator's print head (brief states the only difference is M5-T155-producer-report.md).

VERDICT
- M5-T154: PASS (no required corrections).
- M5-T155 / M5-T156 (security dimensions only, shared head): PASS.
One advisory, non-blocking observation is recorded at the end (not a required correction).

=====================================================================
EVIDENCE PER G5 CHECK
=====================================================================

CHECK 1 — External calls: fixed official hosts; no URL/host from user input; window from validated geometry; budgets/timeouts/paging caps; no credential/key/account/email. PASS.
- Fixed host: the new connector services/api/app/connectors/mappluto_window_arcgis.py imports SERVICE_ROOT ("https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services"), LAYER_NAME, CRS constants from the pinned parent connector (mappluto_geometry_arcgis.py:182-198) and builds every URL itself (build_metadata_url / build_window_query_url). No host or path comes from a caller.
- No user string in the URL: the query is where=1=1 + a validated numeric envelope + a fixed outFields allowlist + fixed paging params (mappluto_window_arcgis.py:353-379). The BBL is NOT placed in the window URL; it is only normalized (normalize_bbl) and used to exclude the subject from results (fetch_window_lots lines 679-717).
- Window from validated geometry: report_context._subject_bbox (report_context.py:181-195) derives the window only from the subject lot's own EPSG:2263 MapPLUTO outline (rejects any non-2263 CRS → None), then _window() pads it (±400 ft lots/footprints, ±1,000 ft streets). build_window_query_url re-validates the envelope: finite, |coord| ≤ 1e8 ft, xmin<xmax & ymin<ymax, span ≤ MAX_QUERY_SPAN_FT=5000 ft (_validate_envelope lines 324-350), else DisallowedRequestError BEFORE any I/O.
- Budgets/timeouts/paging caps: MAX_PAGE_SIZE=2000, HARD_MAX_PAGES=50, MAX_WINDOW_LOTS=5000 (refused, never truncated), timeout=30s default, interactive callers cap attempts to 1 (INTERACTIVE_MAX_ATTEMPTS). Live fetchers pass interactive=True for the window and footprints (report_context.py:143,150). Paging pathologies (over-page count, repeated OBJECTIDs, zero progress, page ceiling, feature cap) each raise PagingPathologyError (_collect_pages lines 616-649).
- No credential sent: the only request header is {"Accept": "application/json"} (mappluto_window_arcgis.py:415). Keyless public service; no token exists.

CHECK 2 — Privacy: no owner name / personal field requested or stored anywhere. PASS.
- Out-field allowlist is explicit (never "*"): OUT_FIELDS = (OBJECTID, BBL, Block, Lot, Address, Version); OwnerName and every personal field are deliberately absent (mappluto_window_arcgis.py:109). Test tests/connectors/test_mappluto_window_arcgis.py:89,92 asserts "OwnerName" not in OUT_FIELDS and not in the built URL.
- Recorded pack carries only structural fields. Verified the actual bytes: mappluto_window_lots_4073340070_plus400ft.json attribute keys across all 201 features = {Address, BBL, Block, Lot, OBJECTID, Version} (no owner field); DCM streets recording keys are street-name/status/width fields only; building footprints are structural (BIN/BASE_BBL/…). The only "OwnerName"/"email" string hits in the pack are prose NEGATIONS in MANIFEST.json/README.md ("never OwnerName", "no key, account or email address").
- The lot "address" member (tax_lot_entry, schema and builder map_context.py:260-262) is public MapPLUTO tax-map data explicitly sanctioned by ruling Y2 ("address (optional non-empty string)"), not an owner/personal field.
- Rendered report: grep of the printed report.html found no ownername / owner / apikey / token / password / secret / bearer / the owner's email. The report header uses borough/block/lot and a caller-supplied display address, never an owner name.

CHECK 3 — Input validation: BBL validated before any call; provider never raises into the route; a malformed/hostile upstream answer refused or escaped. PASS.
- BBL: the report route post_report delegates the whole flag/gating/BBL/body validation to post_results and returns any non-200 verbatim; the map provider is called ONLY after a 200 (report_read.py:96-104), i.e. after the BBL validated. Defense in depth: the provider re-normalizes the BBL in fetch_lot / fetch_window.
- Provider never raises into the route: double-guarded. (a) report_read._map_context_for wraps the provider call in try/except → None on any exception (report_read.py:70-79); (b) default_report_map_context_provider → _assemble catches every connector failure per-layer and returns a built document or None, never raising (report_context.py:210-264). Reproduced: tests/api/test_report_context_provider.py test_a_refusing_fetcher_makes_only_that_layer_unavailable / test_a_refusing_window_fetcher_… / test_no_subject_outline_gives_none (all pass).
- Hostile upstream refused: the window connector refuses wrong CRS (WrongCRSError, checks wkid 102718/latestWkid 2263 on every non-empty page), ArcGIS error objects delivered with HTTP 200 (UpstreamError), malformed JSON (MalformedResponseError), paging faults (PagingPathologyError) and malformed rings (MalformedGeometryError — refuses the WHOLE query, no partial result). The adapter (drawings/maps/adapter.py _text) rejects XML-illegal characters and odd strings as MapInputError; for the tax_lots/streets layers that refusal propagates to MapContextUnavailable → _assemble returns None (fail-safe to lot-only report), so a hostile string can never render. Reproduced: tests/connectors/test_mappluto_window_arcgis.py + tests/contracts/test_map_context_window.py (20 passed together with the provider tests).
- Odd strings ESCAPED when drawn: every label (street names, width text) goes through drawings/kit/svg.py escape() which XML-escapes & < > " and raises on XML-illegal control chars/surrogates; map labels render via text_element → escape (site_context_plan.py:420-426). The report route's caller-supplied ?address is allow-listed (report_read.py:58 `^[A-Za-z0-9 \-.,'#/&]+$`, max 120 chars) so no tag-injection characters reach the HTML.

CHECK 4 — recorded_pack_provider reads only inside the folder; no path traversal; not reachable from a production request path. PASS (with one advisory).
- Not production-reachable: the only non-test reference to recorded_pack_provider is its own docstring in report_context.py; the sole caller is apps/web/e2e/harness/fixture_api.py (the browser-test harness, which binds it via app.dependency_overrides). The production route report_read.py imports only get_report_map_context_provider → default_report_map_context_provider (the live-gated provider). grep over services/api/app and apps/web/src|app|lib found no production import.
- Reads only plain files, deterministically: _pack_url_map reads MANIFEST.json and serves each recorded body with Path.read_text("utf-8") (report_context.py:297-344). No eval/pickle/exec; no network (a local _transport returns TransportResponse(200, body); _dcm_fetch returns a DcmTransport).
- Advisory (non-blocking, below): the loader joins pack_dir / entry["file"] from the MANIFEST without an explicit containment check.

CHECK 5 — Logging: nothing sensitive logged; LIVE_SPATIAL_PROVIDER_ENABLED off by default. PASS.
- All three new/changed log lines emit only event + typed error CLASS + correlation_id — never str(exc), never BBL/address/URL/upstream text: report_context.py:206 (_log_fail), report_read.py:78 and :107. The window connector has no direct log calls; its transport hooks sanitize the network reason via _safe_repr (200-char cap).
- Switch off by default: live_spatial_provider_enabled() (spatial/live_provider.py:79-87) returns True only for an explicit token {1,true,yes,on}; absent/empty/unknown → False. default_report_map_context_provider returns None with ZERO connector calls when off. Reproduced: tests/api/test_report_context_provider.py::test_flag_off_returns_none_and_makes_no_connector_call wires every fetcher to raise AssertionError and still gets None (passes).

CHECK 6 — Dependencies: no new package. PASS.
- `git diff 9ab3a47e6a55 3619744ebba6 -- services/api/requirements* services/api/pyproject.toml apps/web/package.json apps/web/package-lock.json` is EMPTY (exit 0). shapely 2.0.7 already pinned (ruling Y12). No admission/age-gate review needed.

MODULARITY (handwritten source changed): PASS. `python tools/modularity_check.py --check` = "selected 786 files; failures 0; warnings 33". All 33 warnings are pre-existing files not in this wave (integration.py, breakeven.py, max_envelope.py, three_way_document.py, agent_supervisor/*). New modules (mappluto_window_arcgis.py, report_context.py, site_context_plan.py, street_areas.py, neighbourhood_map.py, block_map.py, page_location.py, map_caption.py) are not flagged; the new window connector is a sibling that imports and never changes the baseline parent connector (forbidden_paths honored).

REPRODUCTION COMMANDS (all run from the clean reviewed checkout; lanes venv; replay-only, no network, PYTHONDONTWRITEBYTECODE=1)
- cd /root/project/w-wave20/services/api && PYTHONDONTWRITEBYTECODE=1 /root/project/lanes-runtime/venv/bin/python -m pytest -q -p no:cacheprovider tests/connectors/test_mappluto_window_arcgis.py tests/api/test_report_context_provider.py tests/contracts/test_map_context_window.py  →  20 passed
- (same) -m pytest -q -p no:cacheprovider tests/api/test_report_read_context.py  →  5 passed
- cd /root/project/w-wave20 && .../python .github/scripts/validate_contracts.py  →  "Checked 23 schema file(s); 0 failure(s)." exit 0
- cd /root/project/w-wave20 && .../python tools/modularity_check.py --check  →  failures 0; warnings 33
- git diff 9ab3a47e6a55 3619744ebba6 -- services/api/requirements* services/api/pyproject.toml apps/web/package*.json  →  empty
- schema additivity: contract_version enum goes ["1.0.0"] → ["1.0.0","1.1.0"]; the three new map_context members (context_window, tax_lots, streets) are OPTIONAL (absent from `required`); both schema copies (packages/contracts/… and services/api/app/_contract_schemas/…) are byte-identical in the diff — every 1.0.0 document stays valid.

ADVISORY OBSERVATION (non-blocking; NOT a required correction)
- A1. report_context.py:297-310 (_pack_url_map): recorded_pack_provider resolves each recorded file as `folder / entry["file"]` from MANIFEST.json with no explicit "stays inside the pack folder" check, so a MANIFEST whose "file" value contained "../.." could read outside the pack. This is not a live vulnerability under the current threat model: recorded_pack_provider is test-harness-only, is never wired into any production request path, and the MANIFEST + pack are trusted in-repo fixtures authored by the task. Recommend (future hardening, not blocking this gate) a containment assert (e.g. resolved path is relative to the pack/base dir) if this entry point is ever exposed beyond the e2e harness.

SUMMARY: All six G5 security checks PASS with reproducible evidence; modularity and dependency gates PASS; one non-blocking hardening advisory. Recommended gate result: PASS for M5-T154 G5 (security), no required corrections.

END-OF-REPORT
```

### Return 8 of 8: G5 delta review at 6c8c9f7d (delta-w22-security.md)

```
DELTA G5 (security) — wave 22 — new head 6c8c9f7d526539bc1d5d8ef942d8a3770aba420b

HEAD VERIFIED: `git rev-parse HEAD` in /root/project/w-wave20 = 6c8c9f7d526539bc1d5d8ef942d8a3770aba420b on task/wave22-site-context. Checkout not modified. Read-only; no server/ports/Playwright touched.

1) MY REQUIRED CORRECTIONS
I returned NONE at 3619744e. My only item was advisory A1 (non-blocking). A1 CONFIRMED APPLIED:
- report_context.py:297-311 new `_resolve_inside(folder, name)` — refuses a non-string/empty/nested name (any "/" or "\"), resolves the path, and asserts `resolved.is_relative_to(folder.resolve())`, raising ValueError otherwise. `_pack_url_map` (report_context.py:324-325) now routes every MANIFEST `file` entry through it. Fail-closed containment; `..`/absolute/nested paths cannot escape the pack.
- Test: tests/api/test_report_context_provider.py::test_recorded_pack_loader_refuses_a_path_escaping_the_pack (parametrized `escaping` cases) — PASS.

2) RE-RUN ON THE CHANGED SECURITY SURFACE (lanes venv, PYTHONDONTWRITEBYTECODE=1, replay-only, direct exit codes)
- cd services/api && pytest -q -p no:cacheprovider tests/connectors/test_mappluto_window_arcgis.py tests/api/test_report_context_provider.py tests/contracts/test_map_context_window.py tests/api/test_report_read_context.py → 33 passed; exit 0.
- Targeted A1 + integrity + call-counting (9 tests) → 9 passed, exit 0. Includes:
  - test_flag_off_returns_none_and_makes_no_connector_call — now a COUNTING spy asserts calls == {lot:0,window:0,footprints:0,streets:0} (strengthens CHECK 5: zero connector calls while the switch is off).
  - test_manifest_lists_exactly_the_recorded_files / test_file_bytes_match_manifest_sha256 / test_pack_has_readme_and_byte_exact_gitattributes — window-pack integrity (S6).

3) DOES THE DELTA BREAK ANYTHING I PASSED? No.
- External calls: no new network. `git diff 3619744e 6c8c9f7d -- services/api/app` adds no urllib/requests/http/socket; report_context.py's only change is the containment helper (fetchers/windows/provider logic unchanged). New module drawings/maps/context_scene.py has zero network imports/calls (grep: none).
- Personal fields: no out-field change, no OwnerName, no new personal field anywhere in the diff.
- New package: `git diff 3619744e 6c8c9f7d -- services/api/requirements* services/api/pyproject.toml apps/web/package*.json` EMPTY (exit 0).
- Unescaped strings: all map label text still routes through text_element→svg.escape (context_scene.py:469,474 are fixed constants "N"/"Grid north"; no upstream text). The one `raw(...)` added — page_location.py:153 `el("figure", raw(drawing.svg or ""))` — embeds a kit-rendered Drawing SVG (from render_neighbourhood_map/render_block_map/render_site_context_plan), i.e. server-produced trusted markup whose internal text is already escaped; captions go through `el(...)` which escapes. No raw upstream string reaches the HTML. The report-route ?address allowlist, live-switch default-off, pinned host, envelope-from-validated-geometry, and fail-safe demotion are all unchanged and still covered by the re-run suites.
- Modularity note: the view/projection/label helpers moved to context_scene.py (M5-T155 scope correction 1) — a decomposition, not growth; no security impact.
- Out of my remit: the page-1 print-overflow fix (scrollWidth<=clientWidth) is a layout matter, not a G5 security check; I did not run Playwright/overflow.cjs per my standing no-Playwright constraint — that evidence belongs to the visual/orchestrator pass.

4) VERDICT AT 6c8c9f7d
- M5-T154: PASS (advisory A1 now closed; no required corrections).
- M5-T155 / M5-T156 (security surfaces, shared head): PASS.

END-OF-REPORT
```
