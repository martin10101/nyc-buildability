# R1/R2 no-letter-suffix districts (R1-1, R1-2, R2) - section 23-421(g) reference-plane elevation allowance

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r1-r2-reference-plane-23421g`
- Family: residential_height_setback_r1_r2
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-421(g) | [23-421(g)](https://zr.planning.nyc.gov/entityprint/pdf/node/18075) | 2024-12-05 | 2026-09-13T02:44:00Z | `zr-23-421-g` | `52dd8aab6e2a7e53f65c953157b70e899f7be94438d0c3456731ff430c626536` |

## Where it applies

R1 and R2 districts without a letter suffix (R1-1, R1-2, R2), for a detached, semi-detached or zero-lot-line building, where the lot is either at least 9,500 sq ft and 100 ft wide, or has a rear-to-front slope of at least five percent.

## Exceptions and limits

- The 5-ft allowance feeds a sloping-plane geometry the program does not compute; recorded as a limitation.
- Site-specific modifiers are not modelled here.

## How the program reads it

When the lot meets the ZR 23-421(g) trigger, the program reports that the reference plane used for the pitched-envelope rules may sit up to 5 feet above the base plane. This is an allowance that feeds the pitched-plane geometry; it does not change the 25 ft wall or 35 ft ridge caps.

## Example

A made-up 10,000 sq ft, 100 ft wide detached R2 lot (not a real address); it meets the area-and-width trigger.

- Inputs: zoning_district = R2; building_type = detached; lot_area_sqft = 10000; lot_width_ft = 100; rear_wall_slope_percent = 0
- Expected answer: reference_plane_elevation_max_ft = 5
- Basis of the expected answer (law_text): ZR 23-421(g): for R1/R2 without a letter suffix on a lot of at least 9,500 sq ft and 100 ft wide (or a slope of at least five percent), 'the reference plane ... may be located up to five feet above the base plane.'
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: reference_plane_elevation_max_ft = 5
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r1_r2_reference_plane_23421g.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r1_r2_height_setback.py`
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- The 5-ft allowance only feeds the pitched-plane geometry, which the program does not compute.
- This is a draft extraction awaiting raw-source verification and a qualified-human legal check.

## Human review

- Verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -

