# M5-T150 - producer's report

The builder (geospatial-engineer, an AI agent) made no report file in its commit; its return is kept here unchanged, saved by the orchestrator from the session transcript (`return-builder-w20-T150.txt`). Its trailing commit 2a956349 (the builder's own memory note under `.claude/agent-memory/`) was NOT integrated.

```
I am an AI agent (geospatial-engineer). M5-T150 producer work is complete.

WORKTREE: /root/project/nyc-buildability/.claude/worktrees/agent-adf52eed992d571ed
TASK COMMIT: 7fd1982cbca362c3b760cf0048ba532f72a69cd3  PARENT: 42fc2ae11e6b90084972e7ca32816cc50b8a085a
Cherry-pick 7fd1982 (the task). A trailing non-task commit 2a9563490 holds only my agent-memory note (.claude/agent-memory/geospatial-engineer/) — drop it from the task PR. `git status` clean.
NOTE on the ledger protocol: per the system reminder forbidding report .md files, I did NOT write project-control/reports/M5-T150-producer-report.md; this return IS the producer report (save it verbatim if the ledger needs the file).

FILES CHANGED (all in allowed_paths): app/scenario/three_answers/{geometry.py, inputs.py, result_way_engine_bridge.py, three_way_document.py}; tests/scenario/three_answers/test_geometry_lot_outline.py (new); tests/api/test_results_read_api.py; packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json; tests/drawings/kit/snapshots/recorded_215_16_northern_journey.site_plan.svg; tests/cad/snapshots/results_dxf/recorded_215_16_northern_journey.dxf; app/rules/review_register/register.json; docs/zoning-rule-review/{HISTORY.md,REGISTER.md,calculations/*.md (3),evidence/*.txt (3)}. result_way_bridge.py was in scope but needed no change.

DESIGN: build_geometry draws the lot outline from inputs.lot_outline (the MEASURED tax-map ring in EPSG:2263, threaded from prepared_outline.vertices in result_way_engine_bridge), translated to local feet (subtract min x/min y). No placement is worked, so envelope+floor_plates are withheld (W5). With no outline the three-way transform (lot_outline_available=False) withholds the WHOLE geometry block (S2). build_geometry keeps a local-feet rectangle FALLBACK only for the direct engine path (no transform) that compare_rows/duplicates read — never a shown document — so no out-of-scope file had to change and S4 holds.

OUTLINE (benchmark 215-16 Northern): 5 vertices (6-point closed ring). Drawn area (shoelace)=10,387.99 sq ft; measured outline area (prepared_outline.polygon.area)=10,387.99; recorded lot area=10,075 (NOT used for the drawing; the old rectangle was 102.30x98.48=10,075). Translation: min x=0, min y=0, max<123 ft; crs local_feet, measurement "Approximate — tax map" unchanged.

NO-OUTLINE PATH: geometry = {status:not_available, reason:"The lot's outline is not available, so no site plan is drawn. The outline comes from the city tax map and was not available for this lot.", reason_kind:missing_input}; no lot_outline key; building B still lists from the recorded area.

BENCHMARK DIFF: only geometry.lot_outline (rectangle -> 5-vertex measured polygon); every other top-level key and geometry sub-key byte-identical. SVG snapshot +11/-9 lines (lot lines + 5 edge-length dimension labels). DXF snapshot +77/-67 (lot polyline + dimension text). The ONLY committed document whose geometry changed is the benchmark; its two snapshots follow it.

SCENARIOS (new tests generate the doc from code so they catch code mutations): S1 test_s1_benchmark_lot_outline_is_the_measured_polygon + test_s1_lot_outline_is_translated_to_local_feet; S5 test_s5_drawn_outline_area_equals_the_recorded_measurement (expected = Shapely area from the recorded replay fixture, not retyped); S2 test_s2_no_outline_draws_nothing_and_says_why + test_results_read_api live-route assertion; S6 test_s6_outline_present_withholds_footprint_scaled_layers. S3 verified: site plan renders; dimension labels are the polygon's own edges (2.22, 101.71, 99.98, 103.88, 99.98 ft).

CHECKS (python=/root/project/lanes-runtime/venv/bin/python, PYTHONDONTWRITEBYTECODE=1):
- services/api `ruff check .` -> All checks passed, exit 0
- services/api `pytest tests/scenario/three_answers tests/api tests/drawings tests/cad tests/journey tests/spatial` -> 3424 passed, 8 skipped, exit 0 (final code+snapshots state)
- render_review_register.py --check -> PASSED, exit 0
- sync_contract_schemas.py --check -> OK byte-identical, exit 0
- .github/scripts/validate_contracts.py -> 23 schemas, 0 failures (the regenerated benchmark validates as results), exit 0
- tools/modularity_check.py --check -> 756 files, 0 failures, 31 pre-existing warnings (three_way_document.py is a warn only, below justify/hard), exit 0
- scripts/lanes/check_lane_paths.py --coverage -> PASS 9810 files, exit 0
- linked register test tests/rules/test_zoning_rule_review_register_calculations.py -> 53 passed, exit 0 (register evidence)

MUTATIONS (scratch copy outside the repo at scratchpad/mutrepo; worktree untouched, baseline 5 passed):
- "rectangle restored" (build_geometry forced to ignore inputs.lot_outline) -> CAUGHT by test_s1_benchmark_lot_outline_is_the_measured_polygon AND test_s5_drawn_outline_area_equals_the_recorded_measurement.
- "translation dropped" (no min subtraction; coords left in EPSG:2263 while labelled local_feet) -> CAUGHT by test_s1_lot_outline_is_translated_to_local_feet.

REGISTER: a calculation entry's CODE IDENTITY changed (the register fingerprints whole module files), so I resynced 3 calc entries exactly as M5-T146 did for a drawing-layer change: new module sha256 (geometry.py, three_way_document.py), recomputed code_identity_sha256, revision bump (calc-lot-coverage-by-portion 5->6; calc-preliminary-apartment-estimate 6->7; calc-first-building-option-complete 6->7), 3 `implementation_changed` history events (seq 30-32, "behaviour unchanged"), automated_tests resynced (status Passed, 53 passed, tested_on 2026-10-10), evidence logs rewritten, Markdown re-rendered with --write. No human verdict entered.

ASSUMPTIONS / LIMITATIONS (for the reviewer):
1. "Translation stated in the geometry's measurement record": implemented via crs="local_feet" (schema-documented: origin at a lot corner, axes parallel to EPSG:2263) + measurement.label "Approximate — tax map". I did NOT add a free-text transform sentence because measurement_known is const {rank,label} and geometry_available is additionalProperties:false — both are schemas I may not change. No STOP was warranted (the existing crs/measurement fields state source+transform honestly and never label local feet as EPSG:2263). The site-plan measurement note (labels.py/site_plan.py are read-only) renders "Lot outline: Approximate — tax map".
2. The real measured parcel has a genuine 2.22 ft sliver edge; its "2.22 ft" dimension label renders at plan scale and MAY read cramped/overlap. Per S3 I report it and did NOT shrink labels (labels.py read-only); please judge it in the UI/CAD walkthrough.
3. register tested_commit is recorded as the base head 42fc2ae1 (informational; the checker does not validate it) — resync it to the integrated commit if your process requires, as M5-T146 did.
4. The full pytest subset (3424 passed) was run at the final code+snapshot state; the later register.json/docs/evidence changes are data/doc-only and were verified independently by --check and the linked calc test (53 passed).

STOP: none triggered. No forbidden path touched; no schema, apps/, rule file, styles.py or journey test changed.

REQUESTED STATUS: awaiting_gate.
END-OF-REPORT

```
