# R5 district (flat-roof envelope) - maximum base height and maximum building height

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r5-height`
- Family: residential_height_setback
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-422 | [23-422](https://zr.planning.nyc.gov/article-ii/chapter-3/23-422) | 2024-12-05 | 2026-07-22T00:00:00Z | `zr-23-422` | `7e910c245bfc4c8f1a65ffdbdaf9b4985b71477338d3173c13f2a77395f0148a` |

## Where it applies

Bare R5 districts (no letter suffix), any building.

## Exceptions and limits

- No minimum base height is stated for R5; recorded as a limitation.
- A commercial overlay, special district, historic district or large site is not adjusted by the program; when one is present the result is sent for professional review instead of a changed number.

## How the program reads it

The program reports a maximum base height of 35 feet and a maximum building height of 45 feet (ZR 23-422), and marks the result for professional review. A setback above the base height is governed by a separate rule.

## Example

A made-up bare R5 lot (not a real address).

- Inputs: zoning_district = R5
- Expected answer: max_base_height = 35; max_building_height = 45
- Basis of the expected answer (law_text): ZR 23-422: 'except R5 Districts with a letter suffix, the maximum base height shall be 35 feet, and the maximum building height shall be 45 feet.'
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_base_height = 35; max_building_height = 45
- Result label the program attaches: professional_review_required
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r5_height.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r5_height_setback.py`

## What the program does today and a test checks

- Reports a 35-foot maximum base height and a 45-foot maximum building height for R5 as two separate values, and records the absence of a minimum base height as a documented limitation (test: test_as1_r5_height_confident_base_and_building_separate).
- Every emitted dimension traces to a snapshot citation with a provenance digest (test: test_as2_every_emitted_dimension_traces_to_snapshot_provenance).
- Is not applied to R5A/R5B/R5D or an unknown R5 variant (test: test_nc1_variant_value_not_applied_to_another, test_nc1_unknown_r5_variant_is_unsupported_not_nearest).
- Escalates to professional review on an overlay, special district or historic district, and fails closed on a missing district (test: test_nc3_overlay_or_special_district_downgrades_never_silent_base, test_nc3_historic_district_downgrades, test_nc5_missing_district_fails_closed).
- Is reported as a same-family conflict against the qualifying-site rule, with no value chosen (test: test_nc7_base_and_qrs_rules_conflict_no_value).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- A minimum base height is not computed; the rule reports only the maximum base and building heights.
- Overlay, special-district, historic-district and large-site adjustments are not computed.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r5_height_setback.py`
- Counts: 47 passed
- Evidence: [run log](../evidence/r5-height.txt)
- Rule file digest tested: `30eab3ebe05c2415c5666e515c420d86761714d20035625d5914df9e3294db0f`
- Test files tested:
  - `services/api/tests/rules/test_r5_height_setback.py` (`93901f9646e17cd9e0b00b86da9af822a099ce0d6e5e2bfe4cc483760de750af`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or any linked test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- The setback above the base height is in a separate rule (ZR 23-423), not combined here.
- Overlays, special districts, historic districts and large sites send the result for professional review.
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

