# R5B district (flat-roof envelope) - maximum building height

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r5b-height`
- Family: residential_height_setback
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-422 | [23-422](https://zr.planning.nyc.gov/article-ii/chapter-3/23-422) | 2024-12-05 | 2026-07-22T00:00:00Z | `zr-23-422` | `7e910c245bfc4c8f1a65ffdbdaf9b4985b71477338d3173c13f2a77395f0148a` |

## Where it applies

R5B districts (any building).

## Exceptions and limits

- A commercial overlay, special district, historic district or large site is not adjusted by the program; when one is present the result is sent for professional review instead of a changed number.

## How the program reads it

The program reports a single maximum building height of 35 feet (ZR 23-422) for R5B and marks the result for professional review.

## Example

A made-up R5B lot (not a real address).

- Inputs: zoning_district = R5B
- Expected answer: max_building_height = 35
- Basis of the expected answer (law_text): ZR 23-422: R5B maximum building height 35 feet (no base-height / setback split stated).
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_building_height = 35
- Result label the program attaches: professional_review_required
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r5b_height.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r5_height_setback.py`

## What the program does today and a test checks

- Reports a single 35-foot maximum building height for R5B (test: test_as1_r5b_confident_building_height_only).
- Is not applied to R5 or an unknown R5 variant (test: test_nc1_variant_value_not_applied_to_another, test_nc1_unknown_r5_variant_is_unsupported_not_nearest).
- Is needs_review, verified-ineligible, conditional/never verified and not effective before 2024-12-05 (test: test_as5_every_family_rule_is_needs_review_and_verified_ineligible, test_as3_before_amendment_not_effective).

## In the program but no test checks it

- The rule escalates a commercial overlay, special district or historic district to professional review, but no test found that exercises this escalation for this rule.

## Planned, not built

- No base-height or setback split is modelled for R5B.
- Overlay, special-district and historic-district adjustments are not computed.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r5_height_setback.py`
- Counts: 47 passed
- Evidence: [run log](../evidence/r5b-height.txt)
- Rule file digest tested: `3a22a04911e94465669731768a6ea1cf5167de69a8c9132cd93baf183a44cc74`
- Test files tested:
  - `services/api/tests/rules/test_r5_height_setback.py` (`93901f9646e17cd9e0b00b86da9af822a099ce0d6e5e2bfe4cc483760de750af`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or any linked test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- Only a single flat building-height cap is given; no base-height / setback split is modelled.
- The R5B-to-35-foot mapping is assigned by the researcher from the ZR 23-422 capture's table row; the capture's quoted sentence is a generic 'in the district indicated' statement, so the statement-to-district mapping is unconfirmed.
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

