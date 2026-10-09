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
  `gap_kind`.
- `permitted_footprint_by_portion(corner_portion_area, interior_portion_area,
  corner_ratio=1.00, interior_ratio=0.80)`:
  - both areas present and non-negative -> status 'available'; `footprint =
    corner x corner_ratio + interior x interior_ratio`; no rounding of any value.
  - either area `None` -> status 'not_known', every figure `None`, `gap_kind` =
    "a missing fact about the property", reason: the two portion areas are not known
    and need the lot outline measured against the two street lines (the corner-reach
    measurement); no footprint. Never a zero, never a default.
  - a negative area -> `ValueError`; no footprint is ever worked from a negative area.

The ratios are the legal figures of ZR 23-362 (capture `zr-23-362`): interior/through
80 percent, corner 100 percent. The 100-foot corner-lot distance (ZR 12-10, capture
`zr-12-10-lot-corner`) is carried as the documented module constant
`CORNER_LOT_DISTANCE_FT` - the value the later wiring step passes to the corner-reach
measurement (PART A); it is not used in this arithmetic. No legal figure or wording is
quoted from memory: 80/100 percent and 100 feet come from the two named captures. No
returned text says captured, complies, feasible, validated, verified or legally
correct (ruling C7).

## Scenarios and tests (one test per scenario)

| Scenario | Input state | Expected (basis) | Test name |
|---|---|---|---|
| S9 | corner=0, interior=10,000, 1.00/0.80 | footprint 8,000.00 (made-up-footprint-a: 0.80 x 10,000) | `test_s9_made_up_footprint_a_interior_lot_all_eighty_percent` |
| S10 | corner=9,997.60, interior=390.39 | corner 9,997.60; interior 312.31; footprint 10,309.91 (real-lot-coverage-by-portion reading 13) | `test_s10_real_lot_coverage_by_portion_reading_13` |
| S11 | corner=9,997.46, interior=390.52 | corner 9,997.46; interior 312.42; footprint 10,309.88 (reading 14) | `test_s11_real_lot_coverage_by_portion_reading_14` |
| S12 | corner=5,000, interior=0 | footprint 5,000.00 (ZR 23-362 corner rule; scenario hand arithmetic) | `test_s12_corner_rule_whole_lot_within_corner_portion` |
| S13 | corner=None, interior=None | not_known; no footprint; gap "a missing fact about the property" | `test_s13_missing_portion_areas_not_known` |
| S14 | corner=-1, interior=390.39 | ValueError | `test_s14_negative_area_rejected` |

Every expected figure is PARSED from `docs/reference-cases/R6B/cases/step-p6-worked.json`
(S9 from row `made-up-footprint-a` expected text "0.80 x 10,000 = 8,000"; S10/S11 from
row `real-lot-coverage-by-portion` source_reference) or is the scenario's own hand
arithmetic (S12: 5,000 x 1.00); no figure is retyped and none comes from a run of the
module.

## Expected vs returned (available scenarios)

- S9: returned corner 0.0, interior 8,000.0, footprint 8,000.0; round(footprint,2)
  == 8,000.00. MATCH.
- S10: returned corner 9,997.6, interior 312.312, footprint 10,309.912;
  round -> 9,997.60 / 312.31 / 10,309.91. MATCH to reading 13 (the module keeps full
  precision - "no rounding"; the test compares at the reading's 2-decimal precision,
  exactly as the reading rounds interior-allowed before summing).
- S11: returned corner 9,997.46, interior 312.416, footprint 10,309.876;
  round -> 9,997.46 / 312.42 / 10,309.88. MATCH to reading 14.
- S12: returned footprint 5,000.0; round -> 5,000.00. MATCH.
- S13/S14: not_known / ValueError as expected.

Decimal note (C5): no benchmark measurement is run in PART B (PART A measures). The
module's difference from the readings is only the display rounding of interior-allowed
(e.g. 312.312 vs the reading's 312.31); round-to-2dp is exactly equal to each
reading's own footprint, so no single figure is pinned and no tolerance is widened.

## Mutation proof (temporary copy outside the repository)

In `scratchpad/mut_b/` I copied the module and a two-case test (S9, S10, reading
figures parsed from the committed case by absolute path).
- Baseline unmutated: 2 passed (exit 0).
- Change: `footprint = corner_allowed + interior_allowed` ->
  `footprint = corner_allowed - interior_allowed`.
- Result: `test_s9` (8,000.00 -> -8,000.0) and `test_s10` (10,309.91 -> 9,685.29)
  both FAILED (exit 1). The tests detect the mutation.

## Checks (each with its direct exit code)

- `python -m ruff check` (the 4 new files): `All checks passed!` EXIT=0
- `python -m pytest tests/scenario/three_answers/test_lot_coverage_by_portion.py
  tests/scenario/three_answers/test_preliminary_apartment_estimate.py`:
  13 passed EXIT=0
- `python -m pytest tests/spatial tests/scenario/three_answers`:
  800 passed, 2 skipped EXIT=0 (every existing test passes unchanged)
- `python3 tools/modularity_check.py --check`: failures 0 EXIT=0 (new file not listed)
- `python3 scripts/lanes/check_lane_paths.py --coverage`:
  LANE COVERAGE PASS, 9698 files EXIT=0

All run with `/root/project/lanes-runtime/venv/bin/python`,
`PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider`. The full api suite was not
run locally; it runs in CI.

## Register and scope (ruling C8)

This task changes no existing file and is imported by none; no reported result
changes, so the zoning-rule review register is NOT changed by this task (its
calculation entries move in the later wiring step, which also adds the guards of
backlog row DB-211).

## What I could not settle

Nothing blocking for PART B. PART B does not import PART A; the real program-vs-reading
measurement gap (C5) is PART A's to confirm.
