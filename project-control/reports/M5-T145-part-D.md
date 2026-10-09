# M5-T145 part D producer report - preliminary apartment estimate arithmetic

Written by the PART B/D builder (an AI agent, role rules-engineer). This is a draft
reading, not professionally reviewed (ADR-007).

## What I built

`services/api/app/scenario/three_answers/preliminary_apartment_estimate.py`: one pure
arithmetic module (no file/network access, no clock, no AI). It imports only
`dataclasses`, `decimal` and `math`; it imports no other part of this task and no
engine file, and nothing existing imports it. It does NOT import PART B.

- `PreliminaryApartmentEstimate` (frozen dataclass): `status`
  ('available' | 'not_known'), `quotient_low`, `quotient_high` (two decimals, round
  half up), `quotient_low_unrounded`, `quotient_high_unrounded`, `whole_below_low`,
  `whole_above_low`, `whole_below_high`, `whole_above_high` (below = floor, above =
  ceiling of each quotient), `floor_area_sq_ft`, `share_low`, `share_high`,
  `apartment_size_sq_ft`, `formula`, `label`, `reason`, `missing_inputs`, `gap_kind`.
- `preliminary_apartment_estimate(floor_area_sq_ft, share_low=0.60, share_high=0.75,
  apartment_size_sq_ft=700.0)`:
  - available -> `quotient = floor_area x share / apartment_size` for each share; two
    decimals plus the unrounded quotients; `whole_below = floor`, `whole_above = ceil`.
    `label` = exactly "Preliminary capacity estimate" (C15a).
  - `floor_area_sq_ft` is `None` -> status 'not_known', every figure `None`,
    `missing_inputs` = ("floor_area_sq_ft",), `gap_kind` = None (C12), `label` = exactly
    "Not known" (C15a); the reason names the missing floor area and the building option
    (PART C) that supplies it, with no guessed cause.
  - `apartment_size_sq_ft <= 0`, a share outside 0 to 1, a low share above the high
    share, or a negative floor area -> `ValueError` (C15d); never divides by zero.

The dividend is the proposed building's floor area (D-090 R509); the legal maximum and
the legal dwelling-unit limit (`dwelling_units.py`) are kept separate. The share range
and the apartment size are the owner's PRELIMINARY ASSUMPTIONS (D-090 R540, R541): the
label is the owner's own words and does NOT carry "preliminary assumption"; every OTHER
text that names the share or apartment size (`formula`, `reason`) carries "preliminary
assumption" and the owner's descriptions (the share is an unvalidated sensitivity range
the user can change; 700 sq ft is a chosen starting apartment size on the HPD
measurement basis the user can change). No text calls the share/size law, measured,
typical, realistic, expected or validated, or calls the result a legal limit, a ceiling,
a dwelling-unit limit or a count (C15b; D-090 R545, R688, R700).

## Scenarios and tests

| Scenario | Input state | Expected (basis) | Test name |
|---|---|---|---|
| S22 | floor=20,150 | low 17.27, high 21.59; 17/18 and 21/22 (real-estimate-b) | `test_s22_real_estimate_b` |
| S23 | floor=16,000 | low 13.71, high 17.14; 13/14 and 17/18 (made-up-estimate-a) | `test_s23_made_up_estimate_a` |
| S24 | floor=20,000 | low 17.14, high 21.43; 17/18 and 21/22 (made-up-estimate-b) | `test_s24_made_up_estimate_b` |
| S25 | floor=10,309.91 and 10,309.88 | both low 8.84, high 11.05; 8/9 and 11/12 (real-estimate-a) | `test_s25_real_estimate_a_two_readings_same_two_decimals` |
| S26 | floor=None | not_known; gap_kind None; missing_inputs=(floor_area_sq_ft,); label "Not known" (C12) | `test_s26_missing_floor_area_not_known` |
| S27 | apartment_size=0 | ValueError | `test_s27_zero_apartment_size_rejected` |
| S28 | floor=20,150 | label "Preliminary capacity estimate"; other texts carry "preliminary assumption" + owner descriptions; no forbidden wording (C15a/b) | `test_s28_labels_and_separation_from_the_legal_limit` |
| C15c | floor=14,000, 0.50/0.75 | low 10.00 (below 10, above 10), high 15.00 (below 15, above 15) | `test_c15c_exact_whole_quotient_above_equals_below` |
| C15d | floor=-1 | ValueError | `test_c15d_negative_floor_area_rejected` |
| C15d | share_high=1.5 | ValueError | `test_c15d_share_outside_0_to_1_rejected` |
| C15d | share_low=0.80 > share_high=0.60 | ValueError | `test_c15d_low_share_above_high_share_rejected` |

Every expected figure for S22-S25 is PARSED from the `numbers_block` of the named rows
in `docs/reference-cases/R6B/cases/step-p6-worked.json`; no figure is retyped and none
comes from a run of the module. C15c uses values exact in binary floating point.

## Expected vs returned (available scenarios)

- S22: 17.27 / 21.59, whole 17/18, 21/22. MATCH real-estimate-b.
- S23: 13.71 / 17.14, whole 13/14, 17/18. MATCH made-up-estimate-a.
- S24: 17.14 / 21.43, whole 17/18, 21/22. MATCH made-up-estimate-b.
- S25: both floor areas 8.84 / 11.05, whole 8/9, 11/12. MATCH real-estimate-a.
- S26: not_known, missing_inputs=(floor_area_sq_ft,), gap_kind None, label "Not known".
- S27/C15d: ValueError. S28: label exact; formula/reason carry the labels + descriptions;
  no forbidden wording. C15c: 10.00 (10/10) and 15.00 (15/15) - ceiling equals floor for
  an exact whole quotient.

## Correction before review

The orchestrator's reading (rulings C12 and C15) was applied before any review, in a
second commit on top of the first:
- C12: a missing input now names NO kind of gap. Added `missing_inputs` =
  ("floor_area_sq_ft",); set `gap_kind` to None; the reason names the missing floor area
  and the building option (PART C) that supplies it, with no guessed cause.
- C15a: `label` is the owner's own words - exactly "Preliminary capacity estimate" when
  available and exactly "Not known" when not; the label does not carry "preliminary
  assumption".
- C15b: every other text that names the share or apartment size carries "preliminary
  assumption" and the owner's descriptions (sensitivity range / HPD measurement basis;
  the user can change), written from the values actually used.
- C15c: `whole_above_*` is the CEILING; an exact whole quotient has the same number
  below and above.
- C15d: negative floor area, a share outside 0 to 1, and a low share above the high
  share each raise `ValueError` (one test each), beside the existing zero-apartment-size
  guard.

Mutation proof for the label (temporary copy outside the repository,
`scratchpad/mut_d/`): baseline `test_label_available` / `test_label_not_known` passed
(exit 0); changing the available label from "Preliminary capacity estimate" to any other
value made `test_label_available` FAIL (exit 1). Any other label goes red.

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
so the zoning-rule review register is NOT changed by this task.

## What I could not settle

Nothing blocking for PART D.
