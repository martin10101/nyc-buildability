# R6, R7-1, R7-2, R8 residence districts (ZR 23-22 wide-street conditional) - maximum residential floor area ratio (conservative value)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6-r7-r8-wide-street-conditional-far`
- Family: residential_far
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-22 | [23-22](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-22` | `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e` |

## Where it applies

The four ZR 23-22 districts whose FAR depends on wide-street proximity: R6, R7-1, R7-2 and R8. These districts appear twice in the table - a higher value within 100 feet of a wide street and a lower value otherwise.

## Exceptions and limits

- Within 100 feet of a wide street a higher FAR applies (R6 3.00, R7-1/R7-2 4.00, R8 7.20); the program shows this as a labelled alternative and does not make the wide-street determination.
- Lots containing qualifying affordable or senior housing are allowed a higher FAR again; shown as an alternative, not decided.
- The R8 wide-street qualifying value carries a compound footnote (outside a Mandatory Inclusionary Housing area, within 100 feet of a wide street, and containing certain housing); the program does not evaluate it.

## How the program reads it

The program reports the lower (non-wide-street) FAR as the base value and marks the result conditional, because the higher value applies only for the part of the lot within 100 feet of a wide street. For R6 the lower value is 2.20 and the wide-street value is 3.00.

## Example

A made-up 5,000 sq ft R6 lot with standard residences and no wide-street information given (not a real address).

- Inputs: zoning_district = R6; lot_area_sq_ft = 5000; housing_program = standard_residence
- Expected answer: not determined from the captured text (a gap - see below)
- Basis of the expected answer (gap): ZR 23-22 lists R6 twice: 3.00 within 100 feet of a wide street (footnote 1) and 2.20 otherwise. With no wide-street determination in the inputs, the single correct FAR cannot be worked from the captured text - it is 2.20 if the lot is not within 100 feet of a wide street and 3.00 if it is. The program returns the 2.20 base value and marks it conditional.
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_residential_far = 2.2; max_residential_floor_area_sq_ft = 11000
- Result label the program attaches: conditional
- Do they agree? not determined (the expected answer is a gap)

## Code

- `services/api/app/rules/rulesets/r6_r7_r8_wide_street_conditional_far.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r1_r12_residential_far.py`
- `services/api/tests/rules/test_r6b_far_heights.py`

## What the program does today and a test checks

- Returns the conservative (non-wide-street) FAR for R6, R7-1, R7-2 and R8, never the higher wide-street value, and surfaces the higher value only as a labelled conditional alternative (test: test_as3_conditional_districts_return_conservative_value).
- Proves the higher value is the ZR 23-22 footnote-1 wide-street row, and byte-checks the R8 footnote-2 qualifying value (8.64) against the snapshot (test: test_as3_higher_value_is_the_wide_street_footnote_row, test_as1_conditional_rule_values_match_snapshot).
- Is not applicable to R6B (which has no wide-street increase) (test: test_r6b_has_no_wide_street_increase).
- Is draft/needs_review and never verified (test: test_as7_all_rules_are_draft_and_unapproved, test_as7_no_family_result_is_ever_verified).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- The wide-street determination is not made by this rule, so which FAR applies cannot be settled from it alone.
- The ZR 23-22 split of one lot between two FAR values ('or portions thereof') is not computed.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r1_r12_residential_far.py tests/rules/test_r6b_far_heights.py`
- Counts: 47 passed
- Evidence: [run log](../evidence/r6-r7-r8-wide-street-conditional-far.txt)
- Rule file digest tested: `a33e50f3015bb50c43720ad8bf9c58bf14b4ebd52ac8c1aa721c638b40533463`
- Test files tested:
  - `services/api/tests/rules/test_r1_r12_residential_far.py` (`5f6f2278a72a59c9a0e124613107c15b255b870d256744c57eded000a71b0eca`)
  - `services/api/tests/rules/test_r6b_far_heights.py` (`7e7f505c58155f4dcc6172d78d81f4957a6764d558fb31c0f476b2e0c924daf4`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or any linked test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- The program cannot settle the FAR without a wide-street determination; it returns the non-wide-street base value and marks the result conditional.
- The wide-street footnote allows a single lot to be split between both values ('or portions thereof'); the program does not compute the split.
- The qualifying-housing values and the R8 compound footnote are not computed.
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

