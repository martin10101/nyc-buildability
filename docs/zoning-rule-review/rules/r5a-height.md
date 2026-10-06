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
- Basis of the expected answer (law_text): ZR 23-421's pitched-roof envelope covers R5A: perimeter wall maximum 25 feet, ridge line 35 feet above the base plane. This capture's quoted text states the 25-foot and 35-foot values; the enumeration that includes R5A is recorded in this capture's notes and in the sibling R1/R2 and R3/R4 captures, not in the quoted excerpt here.
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

## What the program does today and a test checks

- Reports a 25-foot wall and 35-foot ridge/building height for an R5A pitched building, as two separate values (test: test_as1_r5a_pitched_confident_wall_and_ridge_separate).
- Fails closed to professional review when the building form is not supplied (test: test_nc4_building_type_unavailable_fails_closed).
- Is not applied to R5 or an unknown R5 variant (test: test_nc1_variant_value_not_applied_to_another, test_nc1_unknown_r5_variant_is_unsupported_not_nearest).
- Is needs_review, verified-ineligible and conditional/never verified (test: test_as5_every_family_rule_is_needs_review_and_verified_ineligible, test_as1_conditional_never_verified_for_every_variant).

## In the program but no test checks it

- The rule escalates a commercial overlay, special district or historic district to professional review, but no test found that exercises this escalation for this rule.

## Planned, not built

- The sloping-plane setback geometry above 25 feet is not computed.
- Overlay, special-district and historic-district adjustments are not computed.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r5_height_setback.py`
- Counts: 47 passed
- Evidence: [run log](../evidence/r5a-height.txt)
- Rule file digest tested: `38661a9d39ddf941a493aba1a28853150a043d6bf81f67a3ec996f527c9c8192`
- Test files tested:
  - `services/api/tests/rules/test_r5_height_setback.py` (`93901f9646e17cd9e0b00b86da9af822a099ce0d6e5e2bfe4cc483760de750af`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or any linked test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- The sloping-plane geometry above 25 feet is not computed; the result is marked for professional review.
- Overlays, special districts and historic districts send the result for professional review.
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

