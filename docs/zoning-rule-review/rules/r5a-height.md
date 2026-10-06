# R5A district (pitched-roof envelope) - maximum perimeter-wall height and maximum ridge/building height

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r5a-height`
- Family: residential_height_setback
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-421 | [23-421](https://zr.planning.nyc.gov/article-ii/chapter-3/23-421) | 2024-12-05 | 2026-07-22T00:00:00Z | `zr-23-421` | `d561048b812284eb8849d2bd7aec3deee9af4285075dd972f8cb2b1719999287` |

## Where it applies

R5A districts for a detached, semi-detached or zero-lot-line building (the pitched-roof envelope).

## Exceptions and limits

- The sloping-plane setback geometry above the 25 ft wall is not computed.
- A commercial overlay, special district, historic district or large site is not adjusted by the program; when one is present the result is sent for professional review instead of a changed number.

## How the program reads it

The program reports a perimeter wall up to 25 feet and a ridge up to 35 feet above the base plane (ZR 23-421), and marks the result for professional review.

## Example

A made-up detached house on an R5A lot (not a real address).

- Inputs: zoning_district = R5A; building_type = detached
- Expected answer: max_perimeter_wall_height = 25; max_building_height = 35
- Basis of the expected answer (law_text): ZR 23-421 lists R5A among the covered districts: perimeter wall maximum 25 feet, ridge line 35 feet above the base plane.
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_perimeter_wall_height = 25; max_building_height = 35
- Result label the program attaches: professional_review_required
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r5a_height.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r5_height_setback.py`
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- The sloping-plane geometry above 25 feet is not computed; the result is marked for professional review.
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

