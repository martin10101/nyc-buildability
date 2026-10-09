# Floor-area allowance: floor area ratio x lot area (benchmark lot BBL 4073340070)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading, worked by an AI agent. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice (ADR-007).

- Calculation id: `calc-floor-area-allowance`
- Entry kind: calculation (a combined/arithmetic calculation; no rule file)
- Family: floor_area
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-09)
- Combines rule entries: `r6-r12-residential-far`

## Code identity

An entry with no rule file is fingerprinted by the LF-normalized sha256 of its code module(s). If a module changes and the entry is not revised, the check fails - as a changed rule file is caught for a rule entry.

- Combined code identity: `f20a1f2b02229642e15aa76fbe5e6a18bc3513bb6590d29df0b45139e5d51e76`
- Modules:
  - `services/api/app/scenario/three_answers/answers.py` (`1ebb4595a74df168c1318bc02216781234daf8b181309271bf4ef33644150ab7`)
  - `services/api/app/scenario/three_answers/result_ways.py` (`58788c78183f2c33a59bbae40b98fe27533b5eaa79e30f1fc2a2a94580eebd5c`)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Digest (sha256) |
|---|---|---|---|---|---|
| 23-22 | [23-22](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-22` | `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e` |

## Where it applies

The scenario step that multiplies the R6B standard floor area ratio (2.00, ZR 23-22) by the lot area to report the maximum residential floor area for the benchmark lot, and marks it available-conditional on the recorded-versus-outline lot-area conflict.

## Exceptions and limits

- The qualifying affordable/senior housing floor area is a labelled alternative, not decided.
- A special district or overlay change to the floor area is not applied.
- The recorded lot area (10,075 sq ft) and the tax-map outline area (10,387.99 sq ft) disagree; neither is chosen automatically, and every floor-area figure carries that condition.

## How the program reads it

Floor area = floor area ratio x lot area. For the benchmark R6B lot the engine uses the recorded lot area 10,075 sq ft: 2.00 x 10,075 = 20,150 sq ft, reported as available-conditional (the recorded area conflicts with the outline area; neither is chosen).

## Inputs, units, measurement basis, formula and rounding

- Inputs:
  - zoning_district = R6B
  - lot_area_sq_ft = 10,075 (recorded city record)
  - housing_program = standard_residence
- Units: feet and square feet
- Measurement basis: EPSG:2263 US survey feet for areas measured from the outline; the recorded lot area is the city record (approximate tax map). See the measurement-basis record.
- Formula: max residential floor area = floor area ratio (2.00) x lot area (10,075) = 20,150 sq ft
- Rounding: none - no rounding rule (an exact product)

## Worked example: independent expected versus the program's actual

The benchmark lot 215-16 Northern Boulevard, Queens (BBL 4073340070), R6B, standard residences.

- Inputs: zoning_district = R6B; lot_area_sq_ft = 10075; housing_program = standard_residence
- Expected answer (independent): max_residential_far = 2; max_residential_floor_area_sq_ft = 20150
- Basis of the expected answer (reference_case): real-lot#L1 = 20,150 sq ft (2.00 x 10,075, rounding none); step-p5-worked#floor-area-ratio-made-up-100x100 settles floor area = ratio x lot area (2.00 x 10,000 = 20,000 on the made-up lot); step-p5-worked#floor-area-ratio-definition quotes the ZR 12-10 definition and its 10,000 sq ft / 2.0 example.
- Independent record(s) cited: real-lot#L1, step-p5-worked#floor-area-ratio-made-up-100x100, step-p5-worked#floor-area-ratio-definition
- Who prepared the expected answer: worked independently by sealed-folder AI agents (step P6: two readers) and the earlier reference cases; not checked by a professional
- Program's actual answer: max_residential_far = 2; max_residential_floor_area_sq_ft = 20150
- Standing of the program's answer: available_conditional
- Do they agree? yes - the program's answer matches the independent expected answer

## What the program does today versus what is planned

Implemented and tested:
- The floor area 20,150 sq ft (2.00 x 10,075) is recomputed through the r6-r12-residential-far rule and equals the independent real-lot#L1 (test: test_calc_floor_area_recomputed_matches_independent).
- The document reports the same floor area with the recorded-versus-outline condition (test: test_document_actuals_match_the_recorded_fixture).

In the program but no test checks it:
- (none recorded)

Planned, not built:
- The conflict between the recorded lot area and the outline area is shown, not resolved.

## Automated test result

- Status: Passed
- Code identity tested: `f20a1f2b02229642e15aa76fbe5e6a18bc3513bb6590d29df0b45139e5d51e76`
- Commit tested: `28026c5efbf1ad879b7cb4fbe3f8b36bbd1d153f`
- Date tested: 2026-10-09
- Command: `python -m pytest -q -p no:cacheprovider rules/test_zoning_rule_review_register_calculations.py`
- Counts: 40 passed
- Evidence: [run log](../evidence/calc-floor-area-allowance.txt)
- Test files tested:
  - `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` (`2c3f31d06f8d408c6e5dc9be8ed269a00b92cdd59e4573c6f9960e0712fb2dad`)
- These deterministic tests ran in the build and all passed, bound to the code identity and the test-file digest shown. If a code module or the test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Linked records (linked, not copied)

- docs/measurement-basis/MEASUREMENT_BASIS.md (the measurement basis; linked, not copied)
- services/api/app/rules/coverage/COVERAGE_MATRIX.md (the rule-coverage matrix; linked)
- docs/reference-cases/R6B/cases/real-lot.json (real-lot#L1, independent)
- docs/reference-cases/R6B/cases/step-p5-worked.json (floor-area-ratio rows, independent)

## Code and tests

- `services/api/app/scenario/three_answers/answers.py`
- `services/api/app/scenario/three_answers/result_ways.py`
- `services/api/tests/rules/test_zoning_rule_review_register_calculations.py`

## Legal requirements and chosen design assumptions

| Figure or step | Kind | Quoted captured text (legal) | Capture |
|---|---|---|---|
| Floor area ratio 2.00 for R6B standard residences (ZR 23-22 table) | LEGAL_REQUIREMENT | the maximum #residential# #floor area ratio# shall be as set forth in the following table | `zr-23-22` |
| Floor area = floor area ratio x lot area (ZR 12-10 floor area ratio definition) | LEGAL_REQUIREMENT | "Floor area ratio" is the total #floor area# on a #zoning lot#, divided by the #lot area# of that #zoning lot#. | `zr-12-10-floor-area-ratio` |

## Gaps and unresolved questions

- The recorded-versus-outline lot-area conflict is shown as a condition on every floor-area figure, not resolved; a survey or deed would settle it.

- Coverage gap: Before this entry, the scenario step that turns the rule's floor area ratio into the reported floor area had no register page, though it combines ZR 23-22 with the recorded lot area.

## Human review

- Current verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -
- The verdict is derived from the reviewer's recorded decision and whether it still matches the current code identity, law captures and revision. A verdict is a named human reviewer's own answer; agent reviews are never recorded here.

