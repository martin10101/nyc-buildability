# M5-T145 part D producer report - preliminary apartment estimate arithmetic

Written by the PART B/D builder (an AI agent, role rules-engineer). This is a draft
reading, not professionally reviewed (ADR-007).

## What I built

`services/api/app/scenario/three_answers/preliminary_apartment_estimate.py`: one pure
arithmetic module (no file/network access, no clock, no AI). It imports only
`dataclasses`, `decimal` and `math`; it imports no other part of this task and no
engine file, and nothing existing imports it (nothing it returns is reachable from a
reported result yet). It does NOT import PART B.

- `PreliminaryApartmentEstimate` (frozen dataclass): `status`
  ('available' | 'not_known'), `quotient_low`, `quotient_high` (shown to two decimals,
  round half up), `quotient_low_unrounded`, `quotient_high_unrounded` (kept beside -
  ruling C6), `whole_below_low`, `whole_above_low`, `whole_below_high`,
  `whole_above_high` (the whole numbers just below/above each quotient, a range, never a
  single count), `floor_area_sq_ft`, `share_low`, `share_high`, `apartment_size_sq_ft`,
  `formula`, `label`, `reason`, `gap_kind`.
- `preliminary_apartment_estimate(floor_area_sq_ft, share_low=0.60, share_high=0.75,
  apartment_size_sq_ft=700.0)`:
  - `apartment_size_sq_ft <= 0` -> `ValueError`; the estimate never divides by zero.
  - `floor_area_sq_ft` is `None` -> status 'not_known', every figure `None`, `gap_kind`
    = "a missing fact about the property", reason: the estimate needs the proposed
    building's residential floor area (from PART C), which is not known for this lot;
    it stays a preliminary assumption-based estimate. Never a zero, never a default.
  - otherwise -> status 'available'; `quotient = floor_area x share / apartment_size`
    for the low and high share; two decimals (round half up) plus the unrounded
    quotients; `whole_below = floor(unrounded)`, `whole_above = floor(unrounded)+1`.

The dividend is the proposed building's floor area (D-090 R509); the legal maximum and
the legal dwelling-unit limit (`dwelling_units.py`) are kept separate. The share range
0.60-0.75 and the apartment size 700 sq ft are the owner's PRELIMINARY ASSUMPTIONS
(D-090 R540, R541): every returned user text (`label`, `formula`, `reason`) carries the
words "preliminary assumption". No text calls the share/size law, measured, typical or
validated, says approval validates them, or calls the result a legal limit, a ceiling,
a dwelling-unit limit or a count of apartments (rulings C6/C7; D-090 R545, R688, R700).

## Scenarios and tests (one test per scenario)

| Scenario | Input state | Expected (basis) | Test name |
|---|---|---|---|
| S22 | floor=20,150 | low 17.27, high 21.59; whole 17/18 and 21/22 (real-estimate-b) | `test_s22_real_estimate_b` |
| S23 | floor=16,000 | low 13.71, high 17.14; 13/14 and 17/18 (made-up-estimate-a) | `test_s23_made_up_estimate_a` |
| S24 | floor=20,000 | low 17.14, high 21.43; 17/18 and 21/22 (made-up-estimate-b) | `test_s24_made_up_estimate_b` |
| S25 | floor=10,309.91 and 10,309.88 | both low 8.84, high 11.05; 8/9 and 11/12 (real-estimate-a) | `test_s25_real_estimate_a_two_readings_same_two_decimals` |
| S26 | floor=None | not_known; no quotient; gap "a missing fact about the property" | `test_s26_missing_floor_area_not_known` |
| S27 | apartment_size=0 | ValueError | `test_s27_zero_apartment_size_rejected` |
| S28 | floor=20,150 | every text carries "preliminary assumption"; no forbidden wording | `test_s28_labels_and_separation_from_the_legal_limit` |

Every expected figure (floor area, both shares, apartment size, both quotients, the
four whole numbers) is PARSED from the `numbers_block` of the named rows in
`docs/reference-cases/R6B/cases/step-p6-worked.json`; no figure is retyped and none
comes from a run of the module.

## Expected vs returned (available scenarios)

- S22: returned quotient_low 17.27 (unrounded 17.271428...), quotient_high 21.59
  (21.589285...), whole 17/18, 21/22. MATCH real-estimate-b.
- S23: returned 13.71 / 17.14, whole 13/14, 17/18. MATCH made-up-estimate-a.
- S24: returned 17.14 / 21.43, whole 17/18, 21/22. MATCH made-up-estimate-b.
- S25: both floor areas returned 8.84 / 11.05, whole 8/9, 11/12 (the readings' decimal
  difference honoured, not pinned). MATCH real-estimate-a.
- S26: not_known, quotients None, gap "a missing fact about the property"; reason names
  the floor area and carries "preliminary assumption".
- S27: ValueError (no division by zero).
- S28: label/formula/reason each contain "preliminary assumption"; none contains law
  (word-bounded), legal limit, ceiling, dwelling-unit limit, measured, typical,
  validated, approval, captured, complies, feasible, verified or legally correct.

## Mutation proof (temporary copy outside the repository)

In `scratchpad/mut_d/` I copied the module and an S22 test (figures parsed from the
committed case by absolute path).
- Baseline unmutated: 1 passed (exit 0).
- Change: `low_unrounded = floor_area_sq_ft * share_low / apartment_size_sq_ft` ->
  `... * share_low * apartment_size_sq_ft`.
- Result: `test_s22` quotient_low (17.27 -> 8,463,000.0) FAILED (exit 1). The test
  detects the mutation.

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
calculation entries move in the later wiring step).

## What I could not settle

Nothing blocking for PART D. PART D does not import PART C; the proposed building's
floor area is handed in by the later wiring step.
