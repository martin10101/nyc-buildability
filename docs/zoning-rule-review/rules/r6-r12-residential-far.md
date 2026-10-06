# R6 through R12 residence districts (flat ZR 23-22 rows) - maximum residential floor area ratio (standard residences)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6-r12-residential-far`
- Family: residential_far
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-22 | [23-22](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-22` | `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e` |

## Where it applies

The R6 through R12 districts whose standard FAR is a single table lookup in ZR 23-22 (for example R6A, R6B, R6D, R7A, R8A, R9, R10, R11, R12). The four districts that the table conditions on wide-street proximity (R6, R7-1, R7-2, R8) are handled by a separate rule and are reported here as not applicable.

## Exceptions and limits

- Lots containing qualifying affordable housing or qualifying senior housing are allowed a higher FAR (the table's second column); the program shows this as a labelled alternative and does not decide whether a development qualifies.
- A Special Purpose District or other overlay may change the floor area; the program does not apply that change.

## How the program reads it

The program looks up the district's standard-residences FAR and multiplies it by the lot area to give the largest residential floor area allowed. For R6B the standard FAR is 2.00.

## Example

A made-up 5,000 sq ft R6B lot with standard residences (not a real address).

- Inputs: zoning_district = R6B; lot_area_sq_ft = 5000; housing_program = standard_residence
- Expected answer: max_residential_far = 2; max_residential_floor_area_sq_ft = 10000
- Basis of the expected answer (law_text): ZR 23-22 table, R6B row: standard residences 2.00. 2.00 x 5,000 sq ft = 10,000 sq ft.
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_residential_far = 2; max_residential_floor_area_sq_ft = 10000
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r6_r12_residential_far.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r1_r12_residential_far.py`
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- The qualifying-housing FAR (the table's second column) is shown as an alternative, not computed.
- Special Purpose District and overlay changes are not applied.
- This is a draft extraction awaiting raw-source verification and a qualified-human legal check.

## Human review

- Verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -

