# R6, R7-1, R7-2, R8 residence districts (ZR 23-22 wide-street conditional) - maximum residential floor area ratio (conservative value)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6-r7-r8-wide-street-conditional-far`
- Family: residential_far
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-22 | [23-22](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-22` | `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e` |

## Where it applies

The four ZR 23-22 districts whose FAR depends on wide-street proximity: R6, R7-1, R7-2 and R8. These districts appear twice in the table - a higher value within 100 feet of a wide street and a lower value otherwise.

## Exceptions and limits

- Within 100 feet of a wide street a higher FAR applies (R6 3.00, R7-1/R7-2 4.00, R8 7.20); the program shows this as a labelled alternative and does not make the wide-street determination.
- Lots containing qualifying affordable or senior housing are allowed a higher FAR again; shown as an alternative, not decided.
- The R8 wide-street qualifying value carries a compound footnote (outside a Mandatory Inclusionary Housing area, within 100 feet of a wide street, and containing certain housing); the program does not evaluate it.

## How the program reads it

The program reports the lower (non-wide-street) FAR as the base value and marks the result conditional, because the higher value applies only for the part of the lot within 100 feet of a wide street. For R6 the lower value is 2.20 and the wide-street value is 3.00.

## Example

A made-up 5,000 sq ft R6 lot with standard residences and no wide-street information given (not a real address).

- Inputs: zoning_district = R6; lot_area_sq_ft = 5000; housing_program = standard_residence
- Expected answer: not determined from the captured text (a gap - see below)
- Basis of the expected answer (gap): ZR 23-22 lists R6 twice: 3.00 within 100 feet of a wide street (footnote 1) and 2.20 otherwise. With no wide-street determination in the inputs, the single correct FAR cannot be worked from the captured text - it is 2.20 if the lot is not within 100 feet of a wide street and 3.00 if it is. The program returns the 2.20 base value and marks it conditional.
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_residential_far = 2.2; max_residential_floor_area_sq_ft = 11000
- Result label the program attaches: conditional
- Do they agree? not determined (the expected answer is a gap)

## Code

- `services/api/app/rules/rulesets/r6_r7_r8_wide_street_conditional_far.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r1_r12_residential_far.py`
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- The program cannot settle the FAR without a wide-street determination; it returns the non-wide-street base value and marks the result conditional.
- The wide-street footnote allows a single lot to be split between both values ('or portions thereof'); the program does not compute the split.
- The qualifying-housing values and the R8 compound footnote are not computed.
- This is a draft extraction awaiting raw-source verification and a qualified-human legal check.

## Human review

- Verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -

