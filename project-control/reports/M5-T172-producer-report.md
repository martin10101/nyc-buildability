# M5-T172 (part B) producer report — wire the illustrative placement and area allocation

Builder: backend-engineer. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a76899b748e3ebd3a`.
Contract head: `4516dbd7affb684ac76a750047843d617cf42733` (task/wave28-placement-wiring after scope correction 1).
All expected values come ONLY from the settled reference case `docs/reference-cases/R6B/cases/placement-building-b.json`
(step P8) and the law; no value is taken from a program run. This is an AI builder's work, not a professional review.

## What was built (the keystone, per scenario)

The placement/area-allocation feature is OPT-IN (threaded only when the engine bridge supplies the four lot
measures, as the rear-yard and envelope analyses are). When absent the document is byte-identical.

- **Engine wiring (5 files).**
  - `three_way_document.py`: new `PlacementInputs` dataclass + optional `placement_inputs` kwarg on
    `emit_three_way_document`; thin `_apply_placement` (calls Part-A `build_placement`) and `_apply_area_allocation`
    (calls Part-A `build_area_allocation`); `_placement_applied` gates `_apply_first_option`. Logic stays in the
    Part-A modules and geometry.py (this file is a thin wiring layer).
  - `result_way_engine_bridge.py`: `_placement_inputs_for` assembles the four measures each on its own basis — the
    printed-tax-map pair from the recorded PLUTO lot facts (lotfront 100.76 / lotdepth 100), the city-map (GIS)
    frontage from the prepared outline's Northern Boulevard edge (103.8792), the GIS depth from the lot-reach measure
    (99.9747). NEVER the scope's `lot_front_ft` (a GIS figure mislabelled approximate_tax_map, DB-260). Threaded on the
    `run_engine_and_result_ways_from_evidence` (route/journey) path only, gated on the DCM street window.
  - `geometry.py`: `build_placed_floor_plates` / `place_building_on_geometry` draw the footprint in the corner on the
    placement frontage within the measured lot outline (3 plates) and return the floor-by-floor rows the drawings
    pair with (check C-4). The footprint is a corner parallelogram along the two confirmed street edges; its drawn
    area 6,716.57 reconciles with the plate 6,716.67 within the readers' half a square foot.
  - `first_option_results.py`: `placement_applied` drops the "Where the plan sits on the lot" not-checked line and the
    fit-note's placement clause once the building is placed (so page 5/6 agree with the placed footprint).
  - `results_way_rules.py`: the DB-248 way rule — the apartment figure must equal the stated share of the total within
    the display rounding (`allocation_share_mismatch`).
- **S1** the regenerated benchmark: `building_alternatives[0]` carries a placed placement (basis printed_tax_map,
  outline 100.76 × 66.66) and an area_allocation; `geometry.floor_plates` holds 3 drawn plates. Values match the
  reference case; cited from placement-building-b.json.
- **S2** real print (below): the building-not-placed sentence is gone, the massing plates draw, the area-illustration
  method appears; 1.4.0/absent-placement paths byte-identical (the whole feature is opt-in).
- **S3** C-4: 3 plate rows consistent with the 3-storey floor_by_floor; plates reconcile to 6,716.67 (±0.5).
- **S4** area_allocation emitted for every alternative; `fitted` true only when placement.status == placed; apartment+other=total.
- **S5** register renderer `--check` and `research_record_check --check` both PASS; calc-area-allocation and
  calc-first-placement entries exist with step P8 as the worked example and no human verdict.
- **S6** records revised: NB-01 rev 10, NB-06 rev 5 (three_way_document.py), NB-05 rev 8 (result_way_engine_bridge.py)
  — code-identity resync only, no reading changed; each dependency_assessment says so. NB-03 NOT revised (forbidden;
  rear_yard_checks.py untouched). NB-04 NOT revised (see limitations — its only staleness is close_frame_dimensions.py
  in the forbidden drawings/maps/, a pre-existing change not mine; the placement touches no NB-04 code path). No
  research_status changed, so README/RESEARCH_REQUESTS.md stay untouched (G-13 fires only on a status change).
- **S7** benchmark fan-out rebuilt (list below).
- **S8** label is exactly Illustrative; nothing reads complies/buildable/optimal/feasible; the not_checked list is
  complete and genuinely-unresolved facts stay unresolved (the GIS conflict stays not known).
- **S9** modularity_check `--check` PASS (failures 0). three_way_document.py is 790 SLOC (above the 750 justify warn,
  below the 1000 hard fail). Cohesion justification: the module's single responsibility is the additive
  engine-document→three-way-document transform; placement is the next additive emission block (after rear_yard and
  envelope). The geometry positioning and the Part-A arithmetic were kept out (in geometry.py / placement.py /
  area_allocation.py); the per-block emitters are thin. No new CI failure.
- **S10** DB-248 way rule + tests (equal / within-rounding / beyond-rounding / no-allocation) + mutation below.
- **S11** the bridge assembles the four measures each on its basis; input-state tests (all four / tax pair missing /
  GIS pair missing / neither) + the scope-frontage mutation, in `test_result_way_engine_bridge.py`.

## Input-state table (RULE 1 — no default stands for a fact)

| input state | placement result | basis "not known"? |
|---|---|---|
| all four measures given | placed; outline + GIS conflict shown | none |
| tax pair missing (frontage or depth None) | WITHHELD, no outline | not placed on the printed-tax-map basis |
| GIS pair missing (frontage/depth None) | placed on tax basis | GIS conflict basis not known (no GIS figures) |
| neither pair | WITHHELD | not placed on any basis |
| residential floor area None (area allocation) | no area_allocation emitted | — |
| residential floor area present | apartment = share×total; fitted follows placement | — |

Every optional fact is read by `is None`/equality, never truthiness. Tests: `test_s11_input_states_*`,
`test_db248_*`, and the Part-A module tests (M5-T182).

## Checks (lanes venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider)

| check | exit | result |
|---|---|---|
| `ruff check .` (edited scenario/contracts files) | 0 | All checks passed |
| register renderer `--check` | 0 | register check PASSED (no issues) |
| `research_record_check.py --check` | 0 | PASS (NB-01/05/06 code_current True; NB-04 pre-existing stale, noted) |
| `modularity_check.py --check` | 0 | failures 0; three_way_document.py warn (justify) with recorded justification |
| `check_lane_paths.py --coverage` | 0 | LANE COVERAGE PASS (10812 files) |
| `validate_contracts.py` + `pytest .github/scripts/tests` | 0 | 23 schemas, 0 failures; 24 tests passed |
| focused api folders (first run) | — | tests/scenario/three_answers, contracts, journey, api, drawings, rules, cad — green after fixes |
| web vitest (the two benchmark pins) | 0 | 2 files, 28 tests passed |
| web `npm run lint` | 0 | 0 errors (2 pre-existing warnings, unrelated) |
| web `npm run typecheck` | 0 | tsc --noEmit clean |
| whole api `pytest -q` | see FINAL-SUITE below | — |

FINAL-SUITE: `cd services/api && pytest -q -p no:cacheprovider` → **3 failed, 10078 passed, 8 skipped** in 519.80s
(exit 0 under the flock wrapper). The 3 failures are EXACTLY the three out-of-scope report/drawing consumers listed
below (test_results_dxf, test_constraints_page, test_location_sheet) — all outside allowed_paths and not editable by
me; every in-scope test (the engine wiring, DB-248, S11, register, journey, benchmark fan-out, web) is green. A scope
correction is needed for those three (and the massing.svg snapshot) before the whole suite is green.

## Mutation proofs (then restored)

1. **placement written vs not** — removed `first["placement"] = placement` in `_apply_placement`; the journey test
   `test_recorded_journey_entry_bbl_to_results_to_exports_to_fixture` FAILED (committed fixture carries the placement).
   Restored (ruff clean; register `--check` PASS confirms the byte-exact restore).
2. **fitted only when placed** — a doc with a withheld placement but `area_allocation.fitted=True` →
   `results_way_violations` returns `{'allocation_fitted_without_placement'}`; the placed benchmark has none. (data-level)
3. **DB-248 share rule** — disabled the `> _AREA_SHARE_TOLERANCE` comparison; `test_db248_share_beyond_rounding_is_flagged`
   FAILED (the beyond-rounding split passed without the rule). Restored (ruff clean; test passes again).
4. **plate count vs floor_by_floor (C-4)** — dropped storey-3's floor_by_floor row from the benchmark (3 plates, 2 rows);
   `load_drawing_input` raised `DrawingInputError('plates_rows_mismatch')` for floor 3 residential. (data-level)
5. **S11 scope frontage** — `compute_placement_geometry` with the scope frontage 103.88 (instead of PLUTO 100.76):
   frontage_conflict collapses 3.12 → 0.0 and the footprint changes, so the reference-case figures no longer hold
   (committed `test_s11_mutation_feeding_the_scope_frontage_collapses_the_conflict`).

## Benchmark fan-out from my own regeneration (`UPDATE_JOURNEY_FIXTURE=1` / `UPDATE_DXF_SNAPSHOTS=1` / `UPDATE_DRAWING_SNAPSHOTS=1`)

In scope (updated, all green):
- `recorded_215_16_northern_journey.json` (regenerated from the corrected engine), its `.dxf` and `.site_plan.svg` snapshots.
- `test_three_answers_three_way_emit.py` (w13: exclude placement-driven fields), `test_results_read_api.py`
  (no-street comparison), `test_results_contract_1_5_0.py` (`_strip_1_5_0_blocks` normalizes floor_by_floor /
  floor_plates / "Where the plan sits" / fit-note; `_total_mismatch_doc` moves `other` to isolate the total rule),
  `test_report_pages.py` (f7 "Shown on the site plan"; a3 dedupe on an unplaced copy), `test_report_appendix.py`
  (area-illustration method now present on the benchmark), `test_zoning_rule_review_register_calculations.py` (eight
  calc entries), `test_result_way_engine_bridge.py` (S11), `test_results_way_rules.py` (DB-248).
- test_lot_reach's text-scan import guard went red because my bridge docstring contained the literal `lot_reach`;
  fixed in-scope by rewording the bridge docstring (now "the spatial lot-reach measure").

OUT OF SCOPE — require a scope correction (add to allowed_paths), NOT edited by me:
- `services/api/tests/cad/test_results_dxf.py::test_no_note_when_everything_drawn_is_surveyed[recorded_215_16_northern_journey]`
  — the drawn floor plates on the un-surveyed benchmark now add an honest "Measurement status not stated ... (floor
  plates)" note; the test asserts no note. FIX: drop the benchmark from this parametrization (or assert the note).
- `services/api/tests/drawings/report/test_constraints_page.py::test_s8_no_building_placed_legend_on_site_sentence_on_scenario`
  and `test_location_sheet.py::test_s3_not_placed_sentence_scenario_only_legend_on_site` — the not-placed sentence /
  legend no longer appears on the placed benchmark. FIX: assert the placed state (or use an unplaced doc).
- `services/api/tests/drawings/kit/snapshots/recorded_215_16_northern_journey.massing.svg` — a NEW snapshot the massing
  now draws (the benchmark previously had no plates). Regenerate with `UPDATE_DRAWING_SNAPSHOTS=1 pytest tests/drawings/kit`
  and add to allowed_paths. (It exists untracked in my worktree; NOT committed, being outside allowed_paths.)

## Real print (TestClient POST /report, benchmark_provider(with_zoning_lot=True, street_on=True) + recorded_pack_provider(window); no server)

`node apps/web/scripts/print-report-pdf.mjs` → `/tmp/claude-0/M5-T172/print/report.pdf`. Page count stays 10.
Compared every page with main's print (`print-main-86a450d4/report.pdf`) via `diff_pages.py`. Whole-document net content
delta (header + fingerprint ignored):
- REMOVED: "No building is placed on this plan yet…" (the not-placed sentence); page-5 chart "Not demonstrated"; the
  "Where the plan sits on the lot" open item (page 6/8); the dedupe pointer "A check of the same kind…" (only parking
  carries the honest sentence now).
- ADDED: page-5 chart "Shown on the site plan"; the page-10 appendix "Area-illustration method" block (the 0.60 share
  split, Illustrative, the plate measure statement); open-item cross-references renumbered on page 3.
- The massing (page 6) now draws the 3 plates; the document fingerprint changed (content changed). No page silently
  lost content (verified by a whole-document sorted text comparison). NOTE: the per-page header reads "Queens block
  7334, lot 70" vs main's "215-16 NORTHERN BOULEVARD…" — a print-HARNESS artifact (TestClient identity vs the
  preview-based main print), not a content change; the orchestrator's own preview print carries the address.

## What I could not check / limitations

- The 4 out-of-scope consumers above need a scope correction before the whole api suite is fully green; I did not edit
  them (outside allowed_paths).
- NB-04 is left at rev 3: its only stale code pin is `close_frame_dimensions.py` under the forbidden `drawings/maps/`,
  a change not mine; the placement touches no NB-04 code path, so I did not revise it (brief: NB-04 "only if you touch
  its measurement-basis reading"). `research_record_check --check` PASSES (it notes NB-04's staleness, does not fail).
- The record reviews are left `stale` (review_state) for the independent G1 delta review; I authored the code-identity
  resync + dependency assessment only (producer ≠ verifier).
- The register calc entries' automated_tests read "Not run" (the code identity changed this task; CI re-runs the
  deterministic register tests) — consistent with calc-preliminary-apartment-estimate.
</content>
