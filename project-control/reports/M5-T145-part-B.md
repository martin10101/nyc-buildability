# M5-T145 part B producer report - by-portion lot coverage (ZR 23-362 / ZR 12-10)

Written by the PART B/D builder (an AI agent, role rules-engineer). This is a draft
reading, not professionally reviewed (ADR-007).

## What I built

`services/api/app/scenario/three_answers/lot_coverage_by_portion.py`: one pure
arithmetic module (no file/network access, no clock, no AI). It imports only
`dataclasses`; it imports no other part of this task and no engine file, and nothing
existing imports it (nothing it returns is reachable from a reported result yet).

- `CoverageByPortion` (frozen dataclass): `status` ('available' | 'not_known'),
  `corner_allowed`, `interior_allowed`, `footprint`, `corner_ratio`, `interior_ratio`,
  `formula`, `zr_sections` = ('ZR 23-362', 'ZR 12-10'), `measurement_basis`, `reason`,
  `missing_inputs`, `gap_kind`.
- `permitted_footprint_by_portion(corner_portion_area, interior_portion_area,
  corner_ratio=1.00, interior_ratio=0.80)`:
  - both areas present and non-negative -> status 'available'; `footprint =
    corner x corner_ratio + interior x interior_ratio`; no rounding; the available
    reason is written from the ratios ACTUALLY used (C16a).
  - either area `None` -> status 'not_known', every figure `None`, `missing_inputs` =
    the names of the missing areas, `gap_kind` = None (C12); the reason names which
    inputs are not known and which calculation supplies them, with no guessed cause.
  - a negative area, or a ratio outside 0 to 1 (C16b), -> `ValueError`.

The ratios are the legal figures of ZR 23-362 (capture `zr-23-362`): interior/through
80 percent, corner 100 percent. The 100-foot corner-lot distance (ZR 12-10, capture
`zr-12-10-lot-corner`) is carried as the documented module constant
`CORNER_LOT_DISTANCE_FT` - the value the later wiring step passes to the corner-reach
measurement (PART A). No legal figure or wording is quoted from memory. No returned
text says captured, complies, feasible, validated, verified or legally correct.

## Scenarios and tests

| Scenario | Input state | Expected (basis) | Test name |
|---|---|---|---|
| S9 | corner=0, interior=10,000, 1.00/0.80 | footprint 8,000.00 (made-up-footprint-a: 0.80 x 10,000) | `test_s9_made_up_footprint_a_interior_lot_all_eighty_percent` |
| S10 | corner=9,997.60, interior=390.39 | corner 9,997.60; interior 312.31; footprint 10,309.91 (real-lot-coverage-by-portion reading 13) | `test_s10_real_lot_coverage_by_portion_reading_13` |
| S11 | corner=9,997.46, interior=390.52 | corner 9,997.46; interior 312.42; footprint 10,309.88 (reading 14) | `test_s11_real_lot_coverage_by_portion_reading_14` |
| S12 | corner=5,000, interior=0 | footprint 5,000.00 (ZR 23-362 corner rule; scenario hand arithmetic) | `test_s12_corner_rule_whole_lot_within_corner_portion` |
| S13 | corner=None, interior=None | not_known; gap_kind None; missing_inputs=(corner_portion_area, interior_portion_area) (C12) | `test_s13_missing_portion_areas_not_known` |
| S14 | corner=-1, interior=390.39 | ValueError | `test_s14_negative_area_rejected` |
| C16a | interior_ratio=0.50 | reason says "50 percent", not "80 percent" | `test_c16a_available_text_follows_actual_ratios` |
| C16b | corner_ratio=1.5 / interior_ratio=-0.1 | ValueError | `test_c16b_ratio_out_of_range_rejected` |
| C16c (R147) | the scenarios' inputs | footprint <= corner area + interior area | `test_c16c_footprint_never_exceeds_sum_of_areas` |

Every expected figure is PARSED from `docs/reference-cases/R6B/cases/step-p6-worked.json`
(S9 from `made-up-footprint-a`; S10/S11 from `real-lot-coverage-by-portion`
source_reference) or is the scenario's own hand arithmetic (S12). No figure is retyped
and none comes from a run of the module.

## Expected vs returned (available scenarios)

- S9: corner 0.0, interior 8,000.0, footprint 8,000.0; round -> 8,000.00. MATCH.
- S10: corner 9,997.6, interior 312.312, footprint 10,309.912; round -> 9,997.60 /
  312.31 / 10,309.91. MATCH reading 13 (module keeps full precision - "no rounding";
  the test compares at the reading's 2-decimal precision, exactly equal).
- S11: corner 9,997.46, interior 312.416, footprint 10,309.876; round -> 9,997.46 /
  312.42 / 10,309.88. MATCH reading 14.
- S12: footprint 5,000.0; round -> 5,000.00. MATCH.
- S13: not_known, missing_inputs=(corner_portion_area, interior_portion_area),
  gap_kind None. S14/C16b: ValueError. C16a: "50 percent" in reason. C16c: footprint
  <= sum over all scenario inputs.

## Correction before review

The orchestrator's reading (rulings C12 and C16) was applied before any review, in a
second commit on top of the first:
- C12: a missing input now names NO kind of gap. Added `missing_inputs` (the names of
  all missing inputs); set `gap_kind` to None for the missing-input state; dropped the
  "they need the lot outline measured against the two street lines" cause (the reason
  now names the inputs and the corner-reach measurement that supplies them).
- C16a: the available reason is written from the ratios actually used (percentages
  derived from `corner_ratio`/`interior_ratio`), not a hardcoded 80 percent.
- C16b: a ratio outside 0 to 1 raises `ValueError`.
- C16c (D-090 R147): a new test asserts the footprint never exceeds the sum of the two
  areas over the scenarios' inputs.

Mutation proof for C12 (temporary copy outside the repository, `scratchpad/mut_b/`):
baseline `test_s13_gap_kind_none` passed (exit 0); changing the missing-input branch's
`gap_kind=None` to `gap_kind="a missing fact about the property"` made that test FAIL
(exit 1). A kind given to a missing input goes red. (The earlier footprint +/- mutation
also still goes red.)

## Checks (each with its direct exit code)

- `python -m ruff check` (the 4 files): `All checks passed!` RUFF_EXIT=0
- `python -m pytest .../test_lot_coverage_by_portion.py
  .../test_preliminary_apartment_estimate.py`: 20 passed FOCUS_EXIT=0
- `python -m pytest tests/spatial tests/scenario/three_answers`:
  807 passed, 2 skipped FOLDER_EXIT=0
- `python3 tools/modularity_check.py --check`: failures 0 MOD_EXIT=0
- `python3 scripts/lanes/check_lane_paths.py --coverage`:
  LANE COVERAGE PASS, 9698 files LANE_EXIT=0

All run with `/root/project/lanes-runtime/venv/bin/python`,
`PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider`. The full api suite runs in CI.

## Register and scope (ruling C8)

This task changes no existing file and is imported by none; no reported result changes,
so the zoning-rule review register is NOT changed by this task (its calculation entries
move in the later wiring step, which also adds the guards of backlog row DB-211).

## What I could not settle

Nothing blocking for PART B.
