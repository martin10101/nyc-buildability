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

## What the program does today and a test checks

- Reports that no rear yard is required within 100 feet of a corner where two street lines meet at 135 degrees or less (the benchmark), returning 0 (test: test_benchmark_rear_yard_is_not_required_within_100_ft_of_the_corner).
- Checks the 135-degree boundary and that the waiver does not apply above it (test: test_angle_boundary_is_135_degrees_or_less).
- Does not apply beyond 100 feet and emits nothing there (test: test_beyond_100_ft_the_waiver_does_not_apply_and_nothing_is_emitted).
- Fails closed to professional review on missing geometry or an impossible angle, naming the missing input (test: test_unknown_geometry_means_no_rear_yard_result_with_the_reason, test_an_impossible_angle_fails_closed).
- Is R6B-only, draft/needs_review and lane-A-gated, reached through the ZR 11-25 suffix reading (test: test_rules_are_r6b_only, test_rules_are_draft_needs_review_and_lane_a_gated, test_r6b_is_reached_through_zr_11_25_and_every_rule_says_so).
- Fails closed to professional review on a special district or an unattested special-district flag (test: test_special_district_or_unattested_special_district_fails_closed, test_unattested_overlay_fails_closed).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- The ordinary rear-yard depth beyond 100 feet of the corner (ZR 23-342) is not computed.
- Commercial overlays are not captured.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r6b_coverage_yard_units.py`
- Counts: 88 passed
- Evidence: [run log](../evidence/r6b-rear-yard-corner-waiver.txt)
- Rule file digest tested: `ee909d7e0074490cbd59b2f965fbcda823182c9b57fa2fa94bf26b5d85260da4`
- Test files tested:
  - `services/api/tests/rules/test_r6b_coverage_yard_units.py` (`1e0762436eb031d0e905fe67fd21a0f96ad2acf1ade21b618abacd6e288a2053`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or any linked test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- The waiver only covers the area within 100 feet of the corner; the ordinary rear-yard depth beyond that (ZR 23-342) is not computed here.
- Commercial overlays are not captured; special districts send the result for professional review.
- This is a draft extraction awaiting raw-source verification and a qualified-human legal check.

## Human review

- Current verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -
- The verdict shown above is derived from the reviewer's recorded decision and whether that decision still matches the current rule file, law captures and revision. A verdict is a named human reviewer's own answer; agent reviews are never recorded here.

