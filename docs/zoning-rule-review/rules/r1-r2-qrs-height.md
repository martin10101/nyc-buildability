# R1/R2-series qualifying residential site - alternative maximum base height and building height (section 23-424)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r1-r2-qrs-height`
- Family: residential_height_setback_r1_r2
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-424 | [23-424](https://zr.planning.nyc.gov/entityprint/pdf/node/22770) | 2024-12-05 | 2026-09-13T02:45:00Z | `zr-23-424-r1-r2` | `336ba2cbbe73689e8b24caf3b3d8bb396eaee5d3b8a89b018328213801c798cc` |
| 23-423 | [23-423](https://zr.planning.nyc.gov/article-ii/chapter-3/23-423) | 2024-12-05 | 2026-07-22T00:00:00Z | `zr-23-423` | `b0b062fbb570ea5bc437572a144eb63f207aa73bdfe8cc612e938f0f3cb72903` |

## Where it applies

R1/R2-series qualifying residential sites (R1-1, R1-2, R1-2A, R2, R2A, R2X) - only when the lot is flagged as a qualifying residential site.

## Exceptions and limits

- The ZR 23-423 setback for this envelope is a separate street-width-based constraint, not restated here.
- Whether a lot is a qualifying residential site is a separate legal/geographic determination the program cannot make; without it the rule sends the case for professional review.
- A commercial overlay or special district sends the result for professional review.

## How the program reads it

For a qualifying residential site the program reports the alternative envelope from the ZR 23-424 table: maximum base height 35 feet and maximum building height 35 feet. It marks the result for professional review, and this alternative competes with the base-district height rule rather than silently overriding it.

## Example

A made-up R2A lot flagged as a qualifying residential site (not a real address).

- Inputs: zoning_district = R2A; qualifying_residential_site = yes
- Expected answer: max_base_height = 35; max_building_height = 35
- Basis of the expected answer (law_text): ZR 23-424 table, row R1-1/R1-2/R1-2A/R2/R2A/R2X/R3-1/R3-2/R3A/R3X: maximum base height 35, maximum height of buildings 35.
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_base_height = 35; max_building_height = 35
- Result label the program attaches: professional_review_required
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r1_r2_qrs_height.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r1_r2_height_setback.py`

## What the program does today and a test checks

- Reports a 35-foot maximum base height and a 35-foot maximum building height for an R1/R2-series qualifying residential site (test: test_as1_qrs_confident_base_and_building_height).
- Keeps the result conditional and never verified (test: test_as1_conditional_never_verified_for_every_rule).
- Fails closed to professional review when the qualifying-site flag is missing (test: test_nc5_qrs_missing_qualifying_flag_fails_closed).
- Escalates to professional review on a commercial overlay or special district (test: test_nc3_qrs_modifier_downgrades).
- Is not applicable to foreign districts even with the qualifying flag set (test: test_nc1_qrs_rule_never_matches_foreign_districts).
- Is reported as a same-family conflict against the base envelope rules for building height, with no single value chosen (test: test_nc7_qrs_and_suffix_variant_rules_conflict_no_value, test_nc7_qrs_and_bare_rule_conflict_no_value).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- Whether a lot is a qualifying residential site is a determination the program does not make.
- The ZR 23-423 setback for this envelope is not computed.
- Overlay and special-district adjustments are not computed.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r1_r2_height_setback.py`
- Counts: 110 passed
- Evidence: [run log](../evidence/r1-r2-qrs-height.txt)
- Rule file digest tested: `f1571d89989823974211668a29802806fefc26ece611cbe7ba3fab9b80e36a26`
- Test files tested:
  - `services/api/tests/rules/test_r1_r2_height_setback.py` (`30e10fe9dd52e85b79c63ee5d811f6d24df42beef3fe341f46ae75ebe1cfd10d`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or any linked test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- Whether a lot qualifies as a qualifying residential site is not decided by the program.
- This alternative competes with the base-district height rule; the program surfaces the conflict rather than picking one.
- The ZR 23-423 setback for this envelope is not restated here.
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

