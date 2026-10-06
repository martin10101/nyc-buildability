# R6B district - maximum number of dwelling units: maximum residential floor area / 680, a fraction of three-quarters or more counting as one unit (ZR 23-52 paragraph (b))

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6b-dwelling-units`
- Family: residential_dwelling_units
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-52 | [23-52](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52) | 2024-12-05 | 2026-09-30T07:29:29Z | `zr-23-52` | `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac` |
| 23-52(b) | [23-52(b)](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52) | 2024-12-05 | 2026-09-30T07:29:29Z | `zr-23-52` | `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac` |
| 11-25 | [11-25](https://zr.planning.nyc.gov/entityprint/pdf/node/18433) | 1994-06-29 | 2026-09-13T02:45:00Z | `zr-11-25` | `6843ad22d57d4f59cf422c80b820d1797955c1cecfecf3ee459b68bf139b2b2b` |

## Where it applies

R6B districts, for a building with multiple dwelling residences, where there is no special density area and the housing is not qualifying senior housing (those have no dwelling-unit factor).

## Exceptions and limits

- Qualifying senior housing, special density areas and conversions have no dwelling-unit factor; the rule does not apply to them.
- The qualifying-affordable-housing dividend uses a different floor-area basis that the program sends for professional review.
- A special district sends the result for professional review.

## How the program reads it

The program divides the maximum residential floor area by the dwelling-unit factor of 680 (ZR 23-52(b)) to get a dwelling-unit count, then rounds: a remaining fraction of three-quarters or more counts as one unit, otherwise it is dropped. R6B inherits ZR 23-52 through the suffix provision ZR 11-25.

## Example

A made-up R6B case: a 5,000 sq ft lot with 10,000 sq ft of residential floor area (not a real address).

- Inputs: zoning_district = R6B; max_residential_floor_area_sq_ft = 10000; housing_program = standard_residence; special_density_area = no; special_district_present = no
- Expected answer: dwelling_units_before_rounding = 14.705882352941176; max_dwelling_units = 14
- Basis of the expected answer (reference_case): Independent reference case, work-order section 9 table B row P1 (an AI agent working ZR 23-52(b) from the sealed capture): factor 680; 10,000 / 680 = 14.71; a fraction below three-quarters is dropped, so 14.
- Who prepared the expected answer: worked independently by a sealed-folder AI agent and recomputed by a second agent; not checked by a professional
- Answer the program gives: dwelling_units_before_rounding = 14.705882352941176; max_dwelling_units = 14
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r6b_dwelling_units.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r6b_coverage_yard_units.py`
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- The qualifying-affordable dividend, qualifying senior housing and conversions are not computed.
- The rule takes the maximum residential floor area as an input; it does not itself check the density-area or unit-mix facts a real determination needs.
- Special districts send the result for professional review.
- This is a draft extraction awaiting raw-source verification and a qualified-human legal check.

## Human review

- Verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -

