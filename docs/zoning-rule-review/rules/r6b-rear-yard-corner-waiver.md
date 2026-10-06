# R6B district - no rear yard required within 100 feet of the point of intersection of two street lines intersecting at 135 degrees or less (ZR 23-344 paragraph (a))

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6b-rear-yard-corner-waiver`
- Family: residential_rear_yard_corner_waiver
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-344(a) | [23-344(a)](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344) | 2024-12-05 | 2026-09-30T07:29:17Z | `zr-23-344` | `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007` |
| 11-25 | [11-25](https://zr.planning.nyc.gov/entityprint/pdf/node/18433) | 1994-06-29 | 2026-09-13T02:45:00Z | `zr-11-25` | `6843ad22d57d4f59cf422c80b820d1797955c1cecfecf3ee459b68bf139b2b2b` |

## Where it applies

R6B districts, for the rear-yard waiver near a corner: whether a point is within 100 feet of the intersection of two street lines that meet at 135 degrees or less.

## Exceptions and limits

- The waiver only covers the area within 100 feet of the intersection; it says nothing about the rest of the lot.
- A commercial overlay is not captured, and a special district sends the result for professional review.

## How the program reads it

The program reports that no rear yard is required within 100 feet of the point where two street lines meet at 135 degrees or less (ZR 23-344(a)); within that area the required rear yard is 0. R6B inherits ZR 23-344 through the suffix provision ZR 11-25.

## Example

A made-up R6B corner lot where two street lines meet at about 89.7 degrees, a point within 100 feet of that corner (not a real address).

- Inputs: zoning_district = R6B; within_100_ft_of_street_line_intersection = yes; street_line_intersection_angle_degrees = 89.7; overlay_present = no; special_district_present = no
- Expected answer: rear_yard_required_within_100_ft_of_corner = 0
- Basis of the expected answer (reference_case): Independent reference case, work-order section 9 table A row L12 (an AI agent working ZR 23-344(a) from the sealed capture): no rear yard required within 100 feet of the intersection of two street lines meeting at 135 degrees or less; at 89.7 degrees within 100 feet the required rear yard is 0.
- Who prepared the expected answer: worked independently by a sealed-folder AI agent and recomputed by a second agent; not checked by a professional
- Answer the program gives: rear_yard_required_within_100_ft_of_corner = 0
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r6b_rear_yard_corner_waiver.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r6b_coverage_yard_units.py`
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- The waiver only covers the area within 100 feet of the corner; the ordinary rear-yard depth beyond that (ZR 23-342) is not computed here.
- Commercial overlays are not captured; special districts send the result for professional review.
- This is a draft extraction awaiting raw-source verification and a qualified-human legal check.

## Human review

- Verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -

