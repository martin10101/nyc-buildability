# M5-T152 producer report (the builder's return, saved verbatim by the orchestrator)

The builder (geospatial-engineer, an AI agent) returned its report in its reply and did not write this file; the orchestrator saved the reply here word for word, as the brief's "full detail" record. Builder commit `690f1c1de5ae9f3b2be8e14e1e4338525102f2eb` (parent `876d7a2e5fcaea6fb24b51bf0b30aa76f39b97ef`), integrated on `task/wave21-report-redesign` as `6f11d83d5`.

---

I am an AI agent (producer, geospatial-engineer) for M5-T152. Work complete; one commit, not pushed. No producer .md file written (per return-directly instruction) — persist THIS as M5-T152-producer-report.md. Requested status: awaiting_gate.

WORKTREE: /root/project/nyc-buildability/.claude/worktrees/agent-a3b0698e558b2fa62
COMMIT: 690f1c1de5ae9f3b2be8e14e1e4338525102f2eb  PARENT: 876d7a2e5fcaea6fb24b51bf0b30aa76f39b97ef
No STOP. All 26 files within allowed_paths; no forbidden path touched.

FILES: scenario geometry.py (streets), building_option.py + result_way_inputs.py ('achieved'→'scheduled' label), three_way_document.py (add-on reason); kit __init__/furniture/site_plan/massing/section.py (frame='report' + render_floor_stack + legend_flow); maps __init__/layout/location_map/zoning_map.py (frame='report'); register.json + 6 docs/zoning-rule-review md (resync); benchmark json + northern site_plan.svg snapshot; 4 new test files.

STREETS (S1/S8): "215 Place" 99.976 ft; "Northern Boulevard" 103.879 ft; each 2-pt line, street_width_fact_id null, lying exactly on the lot outline (0.00 ft off). Lengths equal the spatial engine's StreetFrontage.length. PATHS WITH frontages: the evidence path (run_engine_and_result_ways_from_evidence threads prepared_outline+site_geometry; build_geometry reads inputs.prepared_outline/site_geometry). PATHS WITHOUT (streets stays []): the direct engine path (no prepared outline/site geometry), any unconfirmed frontage, and the no-outline route (whole geometry not_available).

REPORT FRAMES: site plan 512x412 pt; maps 512x412; massing 512x≤336; floor stack 360x358 — all ≤515.9x425.2 pt (182x150 mm). Smallest label 7.5 pt (scale/caption); every label ≥7 pt. No notes column drawn; map attribution/notes kept reachable as role='note' Labels.

CHANGED SENTENCES (S5): 3, listed here: (1) building_option.py "Achieved zoning floor area (building option)"→"Scheduled…"; (2) result_way_inputs LABELS "Building option: achieved…"→"…scheduled…"; (3) three_way_document ADDON_GAIN "…worked out from building options, which are not known for this lot."→"…it needs a building fitted to the site, and none is fitted yet." No legal figure/value/way/withheld change.

BENCHMARK DIFF: geometry.streets []→2 frontages; the 2 add-on-gain reasons reworded; nothing else (32 ins/3 del).
SNAPSHOT DIFF: northern site_plan.svg +2 lines (the 2 street labels); CAD/DXF snapshots unchanged (DXF does not draw streets).

CHECKS (venv, PYTHONDONTWRITEBYTECODE=1; RC via file, not piped): ruff check . RC0 "All checks passed". pytest tests/drawings tests/cad tests/scenario/three_answers tests/api/test_results_read_api.py tests/journey tests/spatial RC0 → 2408 passed, 8 skipped. render_review_register.py --check RC0 PASSED. sync_contract_schemas.py --check RC0 OK. validate_contracts.py RC0 (23 schemas, 0 fail). modularity_check.py --check RC0 (only pre-existing tools/agent_supervisor warnings). check_lane_paths.py --coverage RC0 (9859 files).

MUTATIONS (scratch copy of services/api+packages outside the repo): (1) _build_streets→return [] → FAILED tests/scenario/three_answers/test_geometry_streets.py::test_s1_streets_carry_the_engine_frontages_on_the_outline. (2) legend_flow label 8→6 pt → FAILED tests/drawings/kit/test_report_frame.py::test_s2_site_plan_report_fits_a4_and_is_legible (10 cases).

VISUAL (S7): no SVG rasterizer installed (rsvg/inkscape/convert/cairosvg/Pillow absent) and no server started, so inspection was structural (parsed SVG). Regenerated sheet snapshot: 2 street labels beside their frontages, 5 edge dimensions (incl. 99.98/103.88 ft matching frontages), lot outline, legend, north. Report site plan: no note role, same dimensions+street names, north+scale+legend 'Lot line', ≥8 pt. Floor stack B: 3 storey bands, Storey 1/2/3, floor-to-floor 10 ft, tops 10/20/30 ft, 'Minimum base height' line (to_min_base only), 'Grade', caption "Drawn from the floor schedule; no placement on the lot."

ASSUMPTIONS/LIMITATIONS: register automated_tests.status set 'Not run' for the 4 affected calc entries (code identity drifted; CI re-runs; behaviour unchanged). Floor stack min-base line drawn only for fill_rule=='to_min_base'; no max-height line (the alternative carries none). Kit fixtures' placeholder "Achieved zoning floor area" answer-value labels left as-is (never drawn; not engine output). Massing report keeps the floor table (schedule info); only notes dropped.
END-OF-REPORT

---

## Rework 1 (the builder's return, saved verbatim by the orchestrator)

Builder commit `ee8021c8d9b225c0a8fda1e497a8131bd3434f02` (parent `bff2ef7c303d7793134565bf8ff9e0562c8d1069`), integrated as `347d5218`. The findings it answers: `/root/project/lanes-runtime/owner-docs/session-2026-10-10a/rework-w21-T152-1.md` (K1 to K4).

AI agent, M5-T152 rework 1 done. One commit, not pushed. Rasterised every changed drawing with the installed Playwright Chromium (no server/port).

COMMIT ee8021c8d9b225c0a8fda1e497a8131bd3434f02  PARENT bff2ef7c303d7793134565bf8ff9e0562c8d1069
Files (allowed paths only): kit/section.py, kit/site_plan.py, 10 kit site_plan snapshots, new tests/drawings/kit/test_report_frame_rework1.py. No tracked calc module changed, so the review register is unchanged.

K1 (rasterised floor stack): storey bands are now a quiet neutral token (COLOR['selected'], no colour literal), not yellow; "Minimum base height" reads IN FULL above the dashed line, clear of it; the "30 ft" top label sits left of the line and no longer touches it; Grade line + caption kept; every label >=7.5 pt.
K2 (rasterised site plan, report + sheet): "2.22 ft" now sits below its short edge on a short leader, clear of "101.71 ft" and the corner; all dimensions clear of ticks/lines (two-pass placement reserves every tick and line; short edges step out with a leader).
K3 (rasterised summary): 238x224 pt (<=85 mm); lot outline, street names, frontage lengths only (2, not every edge), north arrow + scale bar; no legend, no notes; labels >=8 pt; default/report frames unchanged.
K4 (rasterised report): a caption "Lot outline: Approximate - tax map" under the plan, sourced to /geometry/measurement/label, no field words.

CHECKS (direct RC): ruff . RC0. pytest tests/drawings tests/cad tests/scenario/three_answers tests/api/test_results_read_api.py tests/journey tests/spatial RC0 -> 2451 passed, 8 skipped. register --check RC0 PASSED. sync_contract_schemas --check RC0. validate_contracts RC0 (23 schemas, 0 fail). modularity --check RC0 (0 failures). lane coverage RC0 (9879 files).

MUTATION (scratch copy outside the repo): reverting the K2 recompose (no tick/line reservation, no short-edge handling) -> tests/drawings/kit/test_report_frame_rework1.py::test_k2_no_label_touches_a_dimension_tick_or_line FAILS on 10 fixtures (the present overlap, incl. the benchmark "2.22 ft"). A self-contained in-repo mutation also ships: test_k2_mutation_a_label_on_a_dimension_line_is_caught.
END-OF-REPORT
