# R3/R4-series districts (pitched-roof envelope, ZR 23-421) - maximum perimeter-wall height and maximum ridge/building height

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r3-r4-pitched-height`
- Family: residential_height_setback_r3_r4
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-421 | [23-421](https://zr.planning.nyc.gov/article-ii/chapter-3/23-421) | 2024-12-05 | 2026-09-13T00:00:00Z | `zr-23-421-r3-r4` | `68e4d147a351188ce0df06d8609b1c3766c76776e0a87482e04ac2cc9459e046` |
| 23-42 | [23-42](https://zr.planning.nyc.gov/article-ii/chapter-3/23-42) | 2024-12-05 | 2026-09-13T00:00:00Z | `zr-23-42` | `3fea4ca54cfee304698506e83f126949863b6a539b2e6de8731a58cfb494070d` |

## Where it applies

R3 and R4 districts listed for the pitched-roof envelope (R3A, R3X, R3-1, R3-2, R4, R4-1, R4A) for a detached, semi-detached or zero-lot-line building.

## Exceptions and limits

- The sloping-plane setback geometry above the 25 ft wall is not computed.
- A commercial overlay, special district, historic district or large site is not adjusted by the program; when one is present the result is sent for professional review instead of a changed number.

## How the program reads it

For the pitched-roof building form the program reports a perimeter wall up to 25 feet and a ridge up to 35 feet above the base plane (ZR 23-421), and marks the result for professional review because the sloping planes between them are not computed.

## Example

A made-up detached house on an R3A lot (not a real address).

- Inputs: zoning_district = R3A; building_type = detached
- Expected answer: max_perimeter_wall_height = 25; max_building_height = 35
- Basis of the expected answer (law_text): ZR 23-421 lists R3A among the covered districts: perimeter wall maximum 25 feet, ridge line 35 feet above the base plane.
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_perimeter_wall_height = 25; max_building_height = 35
- Result label the program attaches: professional_review_required
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r3_r4_pitched_height.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r3_r4_height.py`
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- The sloping-plane geometry above 25 feet is not computed; the result is marked for professional review.
- Heights are measured above the base plane, a separate professional input.
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

