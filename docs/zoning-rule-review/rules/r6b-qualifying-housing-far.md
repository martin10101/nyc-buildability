# R6B district - maximum residential floor area ratio with qualifying affordable housing or qualifying senior housing (ZR 23-22 second column), computed as a separately labeled alternative

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6b-qualifying-housing-far`
- Family: residential_far_qualifying_housing
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-22 | [23-22](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-22` | `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e` |

## Where it applies

R6B districts, for a lot containing qualifying affordable housing or qualifying senior housing (not standard residences).

## Exceptions and limits

- Whether a development is qualifying affordable or qualifying senior housing is a separate legal determination the program does not make.
- R6B has no wide-street FAR increase, so none is applied.

## How the program reads it

The program looks up the R6B qualifying FAR of 2.40 (the second column of ZR 23-22) and multiplies it by the lot area to give the largest residential floor area for qualifying housing. It does not decide whether a development qualifies.

## Example

A made-up 5,000 sq ft R6B lot with qualifying affordable housing (not a real address).

- Inputs: zoning_district = R6B; lot_area_sq_ft = 5000; housing_program = qualifying_affordable_housing
- Expected answer: qualifying_max_residential_far = 2.4; qualifying_max_residential_floor_area_sq_ft = 12000
- Basis of the expected answer (law_text): ZR 23-22 table, R6B row: qualifying affordable or senior housing 2.40. 2.40 x 5,000 sq ft = 12,000 sq ft.
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: qualifying_max_residential_far = 2.4; qualifying_max_residential_floor_area_sq_ft = 12000
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r6b_qualifying_housing_far.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r6b_far_heights.py`

## What the program does today and a test checks

- Reports the ZR 23-22 qualifying-housing FAR of 2.40 for R6B as a labelled conditional alternative, giving 24,180 sq ft on the benchmark lot, and never shares a label or family with the standard FAR rule (test: test_c2_benchmark_standard_and_qualifying_allowances, test_c2_the_two_allowances_never_share_a_label_or_family).
- Is not applicable when the housing program is standard residence, and is R6B-only (test: test_c2_standard_program_makes_the_alternative_not_applicable, test_c2_qualifying_rule_is_r6b_only).
- Records that R6B has no wide-street increase (test: test_r6b_has_no_wide_street_increase).
- Fails closed to professional review on a bad lot area, and is draft/needs_review and lane-A-gated (test: test_c2_qualifying_rule_fails_closed_on_bad_lot_area, test_new_rules_are_draft_needs_review_and_lane_a_gated).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- Whether a development qualifies for qualifying affordable or senior housing is a determination the program does not make.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r6b_far_heights.py`
- Counts: 32 passed
- Evidence: [run log](../evidence/r6b-qualifying-housing-far.txt)
- Rule file digest tested: `56e70534c8caff490f6b6a89f51684d371bbb75bc40818a840bdc54bf5f38982`
- Test files tested:
  - `services/api/tests/rules/test_r6b_far_heights.py` (`7e7f505c58155f4dcc6172d78d81f4957a6764d558fb31c0f476b2e0c924daf4`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or any linked test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- The program does not decide whether a development qualifies for the higher FAR.
- This is a draft extraction awaiting raw-source verification and a qualified-human legal check.

## Human review

- Current verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -
- The verdict shown above is derived from the reviewer's recorded decision and whether that decision still matches the current rule file, law captures and revision. A verdict is a named human reviewer's own answer; agent reviews are never recorded here.

