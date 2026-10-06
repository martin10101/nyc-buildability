# R1/R2 bare group labels (pitched-roof envelope, ZR 23-421) - maximum perimeter-wall height and maximum ridge/building height

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r1-r2-bare-pitched-height`
- Family: residential_height_setback_r1_r2
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-421 | [23-421](https://zr.planning.nyc.gov/entityprint/pdf/node/18075) | 2024-12-05 | 2026-09-13T02:44:00Z | `zr-23-421-r1-r2` | `1bce881805d9ee4d79253432ad86128b7203f81f2054ff25e1ba8dfb1dad1e8b` |

## Where it applies

Bare R1 and R2 districts (no letter suffix) for a single- or two-family detached, semi-detached or zero-lot-line building. Other districts or building types are reported as not applicable.

## Exceptions and limits

- The sloping-plane setback geometry above the 25 ft wall is not computed; it is recorded as a limitation and sent for professional review.
- A commercial overlay, special district, historic district or large site is not adjusted by the program; when one is present the result is sent for professional review instead of a changed number.
- Nearby transportation infrastructure may raise the height; the program sends that case for professional review.

## How the program reads it

For the pitched-roof building form the program reports the two anchor heights from ZR 23-421: a perimeter wall up to 25 feet above the base plane, and a ridge line up to 35 feet above the base plane. It marks the result for professional review because the actual envelope between those heights is a set of sloping planes the program does not compute.

## Example

A made-up detached house on a bare R1 lot (not a real address).

- Inputs: zoning_district = R1; building_type = detached
- Expected answer: max_perimeter_wall_height = 25; max_building_height = 35
- Basis of the expected answer (law_text): ZR 23-421: 'Perimeter walls are subject to setback regulations at a maximum height above the base plane of 25 feet'; the sloping planes 'meet at a ridge line of 35 feet above the base plane.'
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_perimeter_wall_height = 25; max_building_height = 35
- Result label the program attaches: professional_review_required
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r1_r2_bare_pitched_height.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r1_r2_height_setback.py`

## What the program does today and a test checks

- Reports a 25-foot maximum perimeter-wall height and a 35-foot maximum ridge/building height for a bare R1 or R2 district with a pitched building form, as two separate values (test: test_as1_bare_confident_wall_and_ridge_separate).
- Keeps the result conditional and never verified (test: test_as1_conditional_never_verified_for_every_rule).
- Applies to bare R1/R2 only and is not applicable to any other or unknown district (test: test_nc1_bare_rule_scoped_to_bare_labels_only, test_nc1_unknown_variant_is_unsupported_not_nearest).
- Fails closed to professional review when the building form or district is missing or invalid (test: test_nc4_bare_building_type_unavailable_fails_closed, test_nc4_invalid_building_type_fails_closed, test_nc5_missing_district_fails_closed).
- Escalates to professional review when an overlay, special district, historic district, large site or nearby transportation is present or merely unknown (test: test_nc3_bare_rule_modifier_downgrades, test_nc3_omitted_modifier_flag_is_indeterminate_not_confident).
- Is not effective before 2024-12-05 and is effective on that date (test: test_as3_before_amendment_not_effective, test_as3_on_amendment_date_effective).
- Leaves the sloping-plane setback out of the numeric output and records it as a documented limitation (test: test_nc8_setback_geometry_never_a_numeric_output).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- The sloping-plane envelope between the 25-foot wall and the 35-foot ridge is not computed.
- The base plane the heights are measured from is not determined by the program.
- Overlay, special-district, historic-district, large-site and transportation adjustments are not computed.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r1_r2_height_setback.py`
- Counts: 110 passed
- Evidence: [run log](../evidence/r1-r2-bare-pitched-height.txt)
- Rule file digest tested: `b08d5a1e4825f9c715eb7c54323a05d772a4450e8eb19fa43690d4084046bc24`
- Test files tested:
  - `services/api/tests/rules/test_r1_r2_height_setback.py` (`30e10fe9dd52e85b79c63ee5d811f6d24df42beef3fe341f46ae75ebe1cfd10d`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or any linked test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- The program does not compute the sloping-plane geometry above 25 feet; it reports the 25 ft wall and 35 ft ridge as anchor heights and marks the result for professional review.
- Heights are measured above the base plane, which is itself a separate professional input the program does not determine.
- Overlays, special districts, historic districts, large sites and transportation-infrastructure increases send the result for professional review rather than changing the number.
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

