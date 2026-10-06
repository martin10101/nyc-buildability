# R2X and R4 residence districts (ZR 23-21 rows 2-3) - maximum residential floor area ratio (standard zoning lots)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r2x-r4-residential-far`
- Family: residential_far
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-21 | [23-21](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-21) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-21` | `b52771e629b6afa9f9a6843a657dbfd143294f721cd757f953792e747a48ad8a` |

## Where it applies

R2X and the R4 districts (R2X, R4A, R4B, R4, R4-1) of the ZR 23-21 floor-area table. Any other district is reported as not applicable.

## Exceptions and limits

- A qualifying residential site is allowed a higher FAR (1.50 in R4, 1.00 in R2X); the program shows this as a labelled alternative and does not decide whether a site qualifies.
- A Special Purpose District or other overlay may change the floor area; the program does not apply that change.

## How the program reads it

The program looks up the district's standard FAR (1.00 for all of these) and multiplies it by the lot area to give the largest residential floor area allowed.

## Example

A made-up 4,000 sq ft R4 lot (not a real address).

- Inputs: zoning_district = R4; lot_area_sq_ft = 4000
- Expected answer: max_residential_far = 1; max_residential_floor_area_sq_ft = 4000
- Basis of the expected answer (law_text): ZR 23-21 table, row R4A/R4B/R4/R4-1: standard zoning lots 1.00. 1.00 x 4,000 sq ft = 4,000 sq ft.
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_residential_far = 1; max_residential_floor_area_sq_ft = 4000
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r2x_r4_residential_far.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r1_r12_residential_far.py`
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- The qualifying-residential-site FAR is shown as an alternative, not computed.
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

