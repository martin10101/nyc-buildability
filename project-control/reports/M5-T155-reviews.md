# M5-T155 - independent reviews: G3 one independent code-reviewer; G4 one independent qa-engineer; the visual review by one independent visual-quality-reviewer

First reviewed head: `3619744ebba6698cfd699f47d836294bdf979881`. Corrected head: `6c8c9f7d526539bc1d5d8ef942d8a3770aba420b`. Every reviewer is an AI agent that produced none of the work; this is not a human or professional review. The code review's first return came in two parts; its record joins them unchanged.

**CI:** CI at the corrected head 6c8c9f7d: all 46 checks success (workflow CI runs 38097919683 on the pull request and 38097916934 on the push, including web-e2e (vitest and the whole Playwright suite), the api job, control-plane and the dependency-security jobs; secret-scan and context-budget success).

**The orchestrator's own checks:** The orchestrator printed the report through the real website and route at every round and measured it: at the corrected head 9 A4 pages, no element wider than the printable width (overflow check n = 0), body text and drawing labels at true size (N/print-w22g). The first reviewed head printed shrunk to about 77% because page 1's row was wider than the paper (already true on main); corrected in M5-T156 correction 2.

**Verdicts:** every reviewer PASS at the first head, with required corrections (code: M5-T154-C1; QA: C1 to C4; visual: T155-C1, T156-C1, T156-C2; security: advisory A1); every one applied, and every reviewer PASS at the corrected head. Not run (needs a person): the ten-second test with a real architect and a real screen-reader pass.

The returns follow unchanged.

---

### Return 1 of 6: G3 code review (all three tasks) (return-w22-code.md)

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

### Return 2 of 6: G3 delta review at 6c8c9f7d (delta-w22-code.md)

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

### Return 3 of 6: G4 QA review (all three tasks) (return-w22-qa.md)

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

### Return 4 of 6: G4 QA delta review at 6c8c9f7d (delta-w22-qa.md)

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

### Return 5 of 6: visual review of the printed report (M5-T155, M5-T156) (return-w22-visual.md)

```
VISUAL-QUALITY GATE (G4) — Wave 22 "where is the lot?" — visual review of M5-T155 and M5-T156
Reviewer: visual-quality-reviewer (independent, read-only, AI — not a human/professional review).
Head reviewed: 3619744ebba6698cfd699f47d836294bdf979881 on task/wave22-site-context (confirmed `git rev-parse HEAD`). Base: main 9ab3a47e.
Evidence inspected: I rendered my OWN crops from /root/project/lanes-runtime/owner-docs/session-2026-10-10a/print-w22d/report.pdf (pdftoppm -r 150 and -r 300 color, pdftoppm -gray), read report.html, read the source, and looked at the competitor page 4. I did not rely on producer screenshots.

=====================================================================
VERDICTS
=====================================================================
M5-T155 (context drawings): PASS with 1 required correction (should-fix).
M5-T156 (the report): PASS with 2 required corrections (should-fix).
No blocking defect found: nothing illegible, nothing false, no empty figure frame, no photo, no hard contradiction, labels consistent, none Verified. The owner's core complaint ("rectangle on an angle / no reference to where he is / doesn't look like my competitors", R936–R938) is substantially answered — this is a bespoke, genuine location feature, not a default-template look.

Ten-second test with a person: NOT RUN (I am an AI; no human was shown the pages).

=====================================================================
REQUIRED CORRECTIONS (each blocks acceptance per the PASS-with-corrections convention)
=====================================================================
T155-C1 (should fix) — Subject lot does not read as the subject lot; it is swamped by a grey existing-building hatch. On pages 1 and 3 the subject Lot 70 is drawn as: orange "Subject lot" fill, THEN every building footprint on top (grey vertical hatch, incl. the one covering almost all of Lot 70), THEN only the coral OUTLINE restroked on top. Result: the lot interior reads as a grey building; the orange subject fill survives only as a tiny patch at the lot's south edge. The competitor standard (sample p4 "Property Close-Up") keeps the subject a clean solid coral fill. This also sits awkwardly beside the "No building is placed on this plan yet" line on the same page 3 (a first-time client sees a building drawn on the lot while the text says none is placed — existing vs proposed is not distinguished).
File/line: services/api/app/drawings/maps/site_context_plan.py, `_draw_lots_and_buildings` (~lines 532–549: subject fill 538–539 → buildings 544–548 → `_restroke_subject` 549). Fix: skip (or clip out) building footprints that fall inside the subject lot, OR redraw the subject fill above the buildings, so the subject reads clearly; optionally label the grey as "existing building (city records)" to separate it from "no proposed building placed yet."

T156-C1 (should fix) — Page 8 is a near-empty page. It holds only the 6-row "Status-label key" table in the top ~20%; the rest is blank. Reproducible: `pdftotext -bbox` page 8 — last content text ends at y≈164.6 pt; next text is the footer at y≈826.7 pt; page height 841.9 pt (~78% of the page is empty). This is a regression: in wave 21 the status key shared page 6. The rework-3 "tables ≤8 rows never split" rule (html.py SHORT_TABLE_MAX_ROWS=8) now jumps the whole key to its own page when page 7 lacks room. Owner R930 explicitly flags "pages nearly empty."
File/line: services/api/app/drawings/report/html.py lines 70–90 (no-split threshold) interacting with page_evidence.py / layout.py. Fix: recompose so the status-label key is not orphaned on a near-empty page (keep it on page 7 if it fits, allow it to flow, or combine with the evidence page).

T156-C2 (should fix) — Page 2 "Where is the lot?" does not fill the page and is unbalanced. One large full-width Neighbourhood map on top, then a small Block-close-up THUMBNAIL bottom-left + captions right; the entire lower ~third of the page is blank (last content text y≈559 pt of 841.9 pt). The two figures are very unequal, unlike the competitor's balanced four-panel location grid (R938), and the page reads unfinished.
File/line: services/api/app/drawings/report/page_location.py and layout.py (location-figure grid/spacing). Fix: make the block close-up a co-equal figure and/or use the empty lower third (the grid is designed to take a third figure later), and reduce the empty bottom so the sheet reads as finished and fills the page.

=====================================================================
NON-BLOCKING (cosmetic / carry-over)
=====================================================================
- (cosmetic, page 3) Faint diagonal-pinstripe fill in the outer corners/margins of the site plan is distinct from the plain "Street" fill but is not in the legend; a reader cannot tell what it represents. It does NOT falsely assert "street" (only named gaps carry the plain street fill and a label). Fix: give it a legend entry or leave it neutral white. site_context_plan.py / kit/styles.py.
- (cosmetic, page 3) Labels just below Lot 70 ("Lot 11", "45-12 215 PLACE", "101.71 ft") are crammed together near the lot's bottom edge; readable but tight.
- (cosmetic, carry-over, out of wave-22 scope) Preliminary apartment estimate reads "about 17 to 22 apartments ... 700 sq ft per apartment" on pages 1 and 5, but 20,150/700≈29; the 0.60–0.75 net factor is applied but not shown. This is wave-21 should-fix #1 (readers.py, T151 scope), unchanged — flag as still open, not introduced here.

=====================================================================
EVIDENCE BY BRIEF CHECK
=====================================================================
CHECK 1 — every page (8 A4 pages):
- p1 Decision summary ("What can I potentially build?"): answers table (3 Conditional rows) + compact summary-frame site plan beside them + apartment estimate + important open items + "In this report" scope. Full, not empty. Answer visible at a glance. Good (rework-1 emptiness fixed).
- p2 "Where is the lot?": Neighbourhood map (north-up, street grid, "Subject lot" marker, legend, scale 0/500/1,000 ft) + small Block close-up thumbnail + sources/dates captions. Answers the question but ~1/3 empty and unbalanced (T156-C2).
- p3 "What constrains the design?": lot-area basis + full site plan among surroundings + "No building is placed…" line + constraints table (10 rows, no bad break). Reads as a proper site plan. Subject-lot clarity issue (T155-C1). ~40% empty at bottom but substantial content — acceptable.
- p4 "How do the options compare?": shared limitations, FAR bar chart, 11-option table, worked/not-worked. Fine.
- p5 Scenario sheet (Building B): scheduled line, not-placed sentence, floor-stack figure, floor schedule, what-not-checked, apartment estimate. Fine; bottom half empty but content complete.
- p6 "What remains unresolved…": 11 assumptions + 8-row open-items table. Dense, fine.
- p7 "How was this derived?": inputs/sources, FAR + envelope figures with law links, provenance, "Drawing notes and map attributions" (plain "edited <date>" lines, no ids). Fine.
- p8 Status-label key: 6-row table only — near-empty page (T156-C1).
Legibility: all text legible at A4; smallest drawing labels (edge lengths, "45-12 215 PLACE") read at 7 pt-equivalent; no overlaps or clipped text observed; no bad table breaks.

CHECK 2 — the three context drawings:
- Site context plan (p3) READS as a site plan: coral Lot 70 among neighbours (Lot 1/11/61), named streets drawn as areas with widths (NORTHERN BOULEVARD "100 ft mapped width", 215 STREET / 215 PLACE / 216 STREET "60 ft mapped width", 45 ROAD "50 ft mapped width"), existing building footprints grey, lot edge lengths (103.88 / 99.98 / 99.98 / 101.71 ft), rotated so Northern Blvd is level, grid-north arrow ("Grid north"), scale bar, legend of only drawn kinds, title "Site plan: the lot among its neighbours / Queens, Block 7334, lot 70." Lot reads as a corner lot at Northern Blvd & 215 Place. Only defect: subject fill obscured by building hatch (T155-C1).
- Block close-up (p2): shows the block in its street grid (215 STREET / NORTHERN BOULEVARD / 45 ROAD / 215 PLACE), subject coral-outlined. Legible but small/thumbnail.
- Neighbourhood map (p2): north-up street network (213 St, 214 Pl, 215 St/Pl, 216–219 St, Northern Blvd, Bell Blvd, 42 Ave, 45 Rd/Dr, 46 Ave/Rd) with "Subject lot" marker. Shows where the lot sits in the area. Good.
- No false depiction found: streets confined to the fetched data window; only gaps crossed by a named centre line are labelled as that street; existing buildings are factual. No yard/setback/coverage/proposed-building drawn (Y6 holds).

CHECK 3 — across pages:
- Repeated drawings: site context plan appears compact on p1 and full on p3 (different frames/sizes, intentional per rework); the full-size drawing is printed once (p3). Not a violation.
- Contradictions: none hard. Soft: existing building on subject lot vs "no building placed" (folded into T155-C1).
- Developer words: NONE visible. grep of report.html found no dataset id (no "5zhs-2jue"), no "via NYC Open Data", no terms-of-use, no arcgis URL, no visible BBL number, no OwnerName/OBJECTID/Street_NM/Streetwidth. snake_case tokens (subject_lot, mapped_width_ft, building_footprints…) exist ONLY in SVG attribute/data-source provenance pointers, not in rendered text.
- Six labels, none Verified: status-label key lists Verified/Provisional/Illustrative/Conditional/Pending verification/Unresolved; the Verified row carries "Supported by completed checks and evidence. Not used in this report." Nothing in the report is labelled Verified.
- No photo / no empty frame: only "Aerial and street photographs" appears once, under the scope "Not yet" list; "Context maps" appears once under "In this report" (correct, since maps are printed). No image, no empty figure frame, no "Street View"/"photo"/"aerial" elsewhere (S4 holds).

CHECK 4 — grayscale (pdftoppm -gray, pages 2 and 3): BOTH still read. Kinds are pattern-differentiated (subject = checkerboard, building = vertical hatch, street = light, neighbour = thin outline), so grayscale survives. Caveat tied to T155-C1: in grayscale the subject lot relies mainly on the "Lot 70" text + slightly thicker border, because its fill is still covered by the building hatch — prominence is weak.

CHECK 5 — ten-second-with-a-person test: NOT RUN.

Ruling spot-checks (visual): Y7 captions name sources + dates in plain words (present, p2/p3/p7); Y8 not-placed sentence present on p3 and p5 (the fixed sentence, not spliced); Y9 no photo/empty frame; Y10 page type 2 opens with "Where is the lot?" then "What constrains the design?", six page types, scope list correct; Y5/one-outline — only one lot outline drawn per figure (two outlines never drawn together); Y6 no law geometry drawn; Y13 nothing Verified.

Scope note: wave 22 changed server-side report generation only (apps/web/src/** untouched/forbidden). The interactive web-app perspectives from my standing brief (keyboard, reduced-motion, 3D camera, dropdown/control grouping, layer behavior, evidence sync, tablet) are unchanged by this wave and were NOT re-reviewed. The web report-preview and results screenshots in the evidence render the same server SVG as the PDF and showed no new defects.

Reproduction commands:
- git -C /root/project/w-wave20 rev-parse HEAD
- pdftoppm -r 300 -f 3 -l 3 -png -x 760 -y 880 -W 420 -H 420 .../print-w22d/report.pdf lot70  (shows subject fill under building hatch)
- pdftotext -bbox -f 8 -l 8 .../print-w22d/report.pdf p8.html ; grep yMax (content ends y≈164.6, footer y≈826.7, page 841.9)
- grep for "5zhs-2jue|via nyc open data|OwnerName" in .../print-w22d/report.html → no hits
- Read .../print-w22d/page-1.png … page-8.png and sample-report.pdf page 4.

END-OF-REPORT
```

### Return 6 of 6: visual delta review at 6c8c9f7d (delta-w22-visual.md)

```
DELTA VISUAL GATE (G4) — Wave 22, head 6c8c9f7d526539bc1d5d8ef942d8a3770aba420b (confirmed `git rev-parse HEAD`), task/wave22-site-context. Reviewer: visual-quality-reviewer (independent, read-only, AI). Covers M5-T155, M5-T156. I rendered print-w22g pages myself and measured; I did not rely on producer screenshots.

1) MY REQUIRED CORRECTIONS — all FIXED:

T155-C1 (subject lot obscured by building hatch) — FIXED.
- Evidence: site_context_plan.py:273,285 — existing buildings on the subject lot now drawn as a DASHED outline, with the subject's coral fill drawn ABOVE them; kit/styles.py:179 adds legend ShapeStyle "Existing building (city records)". Test: tests/drawings/maps/test_site_context_plan.py:76 test_t155_c1_subject_fill_reads_above_the_existing_building.
- Pages: Lot 70 now reads as a coral-filled subject on page 1 (summary frame), page 2 (block close-up), page 3 (full site plan); legend distinguishes "Existing building (city records)" (dashed) from neighbours' "Building footprint" (grey). The old grey-covered-lot look and its soft contradiction with "No building is placed…" are gone.

T156-C1 (page 8 near-empty, lone status-key table) — FIXED.
- Report is now 9 pages. The last page (page 9) carries Provenance + "Drawing notes and map attributions" + the 6-row Status-label key together — not a lone table on an ~80%-empty page. Tall tables break with repeated headers (open-items p6→p7); short tables stay whole.

T156-C2 (page 2 unbalanced, ~1/3 empty) — FIXED.
- Page 2 now stacks two CO-EQUAL wide maps (Neighbourhood on top, Block close-up below), each with title, legend, scale bar and caption; the block close-up is a full-width figure with Lot 70 coral-filled and prominent; the page fills with no large empty bottom. Test: tests/drawings/report/test_location_sheet.py:120 test_location_page_layout_two_co_equal_wide_maps.

2) MY CHECKS AT THIS HEAD (read-only, direct exit codes):
- Overflow: node print-w22e/overflow.cjs on print-w22g/report.html → {W:688, docW:688, n:0, first:[]}, exit 0. Nothing wider than the page; the wave-21 77% print-shrink is gone — report prints TRUE size (e2e scrollWidth<=clientWidth asserted at report-print.flag-on.spec.ts:275-277).
- Fonts (authoritative SVG/CSS font-size, now true size): smallest drawing label = 7.50pt (>=7pt OK); smallest body/CSS text = 8pt (>=8pt OK). pdftotext -bbox ink-heights corroborate (min box-h 4.16pt on p3 is a 7.5pt short-glyph word like "ft"/digits, not a sub-7pt font).
- Dev words: grep of report.html → none (no 5zhs-2jue, no "via NYC Open Data", no URL/OwnerName/OBJECTID/Street_NM/Streetwidth/BBL in visible text). Verified appears only in the key row "…Not used in this report." Photo/aerial only as "Aerial and street photographs" under scope "Not yet". No photo, no empty frame.

3) REGRESSIONS: none. True-size printing makes legibility BETTER, not worse. New page 7 is a header-repeating open-items continuation (~60% trailing whitespace) — allowed table break, not a lone-line/near-empty page; minor cosmetic only. Carry-over (not this wave): apartment estimate "about 17 to 22 apartments … 700 sq ft" on pages 1 and 5 vs 20,150/700≈29 — unchanged, readers.py, T151 scope.

4) VERDICTS at 6c8c9f7d:
- M5-T155 (context drawings): PASS.
- M5-T156 (the report): PASS.

END-OF-REPORT
```
