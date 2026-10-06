# R3-2 and R4 districts (flat-roof envelope, ZR 23-422, residences not subject to 23-421) - maximum building height

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r3-2-r4-flat-height`
- Family: residential_height_setback_r3_r4
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-422 | [23-422](https://zr.planning.nyc.gov/article-ii/chapter-3/23-422) | 2024-12-05 | 2026-09-13T00:00:00Z | `zr-23-422-r3-r4` | `0268089074b51d7b2457fa280bb19f5a2ce1c49b708dbb6654f49df78ea61b18` |
| 23-42 | [23-42](https://zr.planning.nyc.gov/article-ii/chapter-3/23-42) | 2024-12-05 | 2026-09-13T00:00:00Z | `zr-23-42` | `3fea4ca54cfee304698506e83f126949863b6a539b2e6de8731a58cfb494070d` |

## Where it applies

R3-2 and R4 districts for a flat-roof building (building types 'attached' or 'other', i.e. residences not using the pitched-roof envelope of ZR 23-421).

## Exceptions and limits

- A commercial overlay, special district, historic district or large site is not adjusted by the program; when one is present the result is sent for professional review instead of a changed number.

## How the program reads it

The program reports a single maximum building height of 35 feet (ZR 23-422) for these flat-roof residences and marks the result for professional review.

## Example

A made-up attached (flat-roof) building on an R4 lot (not a real address).

- Inputs: zoning_district = R4; building_type = attached
- Expected answer: max_building_height = 35
- Basis of the expected answer (law_text): ZR 23-422: 'In the districts indicated, for residences not subject to the provisions of Section 23-421, the maximum building height shall be 35 feet' (R3-2, R4).
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_building_height = 35
- Result label the program attaches: professional_review_required
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r3_2_r4_flat_height.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r3_r4_height.py`
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- Only a single flat building-height cap is given; no base-height / setback split is modelled.
- Overlays, special districts and historic districts send the result for professional review.
- This is a draft extraction awaiting raw-source verification and a qualified-human legal check.

## Human review

- Verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -

