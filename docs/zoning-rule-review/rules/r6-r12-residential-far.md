# R6 through R12 residence districts (flat ZR 23-22 rows) - maximum residential floor area ratio (standard residences)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6-r12-residential-far`
- Family: residential_far
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-22 | [23-22](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-22` | `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e` |

## Where it applies

The R6 through R12 districts whose standard FAR is a single table lookup in ZR 23-22 (for example R6A, R6B, R6D, R7A, R8A, R9, R10, R11, R12). The four districts that the table conditions on wide-street proximity (R6, R7-1, R7-2, R8) are handled by a separate rule and are reported here as not applicable.

## Exceptions and limits

- Lots containing qualifying affordable housing or qualifying senior housing are allowed a higher FAR (the table's second column); the program shows this as a labelled alternative and does not decide whether a development qualifies.
- A Special Purpose District or other overlay may change the floor area; the program does not apply that change.

## How the program reads it

The program looks up the district's standard-residences FAR and multiplies it by the lot area to give the largest residential floor area allowed. For R6B the standard FAR is 2.00.

## Example

A made-up 5,000 sq ft R6B lot with standard residences (not a real address).

- Inputs: zoning_district = R6B; lot_area_sq_ft = 5000; housing_program = standard_residence
- Expected answer: max_residential_far = 2; max_residential_floor_area_sq_ft = 10000
- Basis of the expected answer (law_text): ZR 23-22 table, R6B row: standard residences 2.00. 2.00 x 5,000 sq ft = 10,000 sq ft.
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_residential_far = 2; max_residential_floor_area_sq_ft = 10000
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r6_r12_residential_far.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r1_r12_residential_far.py`

## What the program does today and a test checks

- The ZR 23-22 standard residential FAR (2.00 for R6B) is checked byte-for-byte against the captured table, and the benchmark R6B lot yields 20,150 sq ft (test: test_as1_flat_rule_values_match_snapshot, test_c2_benchmark_standard_and_qualifying_allowances).
- Multiplies the FAR by the lot area to report the maximum residential floor area for the benchmark lot (test: test_c2_benchmark_standard_and_qualifying_allowances).
- Is draft/needs_review, never verified, and effective from 2024-12-05 (test: test_as7_all_rules_are_draft_and_unapproved, test_as7_no_family_result_is_ever_verified).
- Covers exactly the ZR 23-21/23-22 districts, with none claimed twice or invented (test: test_as2_every_snapshot_district_is_covered_or_excluded).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- Whether a site qualifies for the higher qualifying-housing FAR is a determination the program does not make (it is a separate labelled rule).
- Special Purpose District and overlay changes to FAR are not applied.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r1_r12_residential_far.py`
- Counts: 15 passed
- Evidence: [run log](../evidence/test_r1_r12_residential_far.txt)
- Rule file digest tested: `6338d2fae4a85f50161e44af4373d5cf1c3b91e83700d64b8c804fb87e4e4cce`
- Test files tested:
  - `services/api/tests/rules/test_r1_r12_residential_far.py` (`5f6f2278a72a59c9a0e124613107c15b255b870d256744c57eded000a71b0eca`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or a test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- The qualifying-housing FAR (the table's second column) is shown as an alternative, not computed.
- Special Purpose District and overlay changes are not applied.
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

