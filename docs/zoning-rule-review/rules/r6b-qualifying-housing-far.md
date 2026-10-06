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
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- The program does not decide whether a development qualifies for the higher FAR.
- This is a draft extraction awaiting raw-source verification and a qualified-human legal check.

## Human review

- Verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -

