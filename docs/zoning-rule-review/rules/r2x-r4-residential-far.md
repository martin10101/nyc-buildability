# R2X and R4 residence districts (ZR 23-21 rows 2-3) - maximum residential floor area ratio (standard zoning lots)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r2x-r4-residential-far`
- Family: residential_far
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-21 | [23-21](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-21) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-21` | `b52771e629b6afa9f9a6843a657dbfd143294f721cd757f953792e747a48ad8a` |

## Where it applies

R2X and the R4 districts (R2X, R4A, R4B, R4, R4-1) of the ZR 23-21 floor-area table. Any other district is reported as not applicable.

## Exceptions and limits

- A qualifying residential site is allowed a higher FAR (R4 1.50; R2X unchanged at 1.00); the program shows this as a labelled alternative and does not decide whether a site qualifies.
- A Special Purpose District or other overlay may change the floor area; the program does not apply that change.

## How the program reads it

The program looks up the district's standard FAR (1.00 for all of these) and multiplies it by the lot area to give the largest residential floor area allowed.

## Example

A made-up 4,000 sq ft R4 lot (not a real address).

- Inputs: zoning_district = R4; lot_area_sq_ft = 4000
- Expected answer: max_residential_far = 1; max_residential_floor_area_sq_ft = 4000
- Basis of the expected answer (law_text): ZR 23-21 table, row R4A/R4B/R4/R4-1: standard zoning lots 1.00. 1.00 x 4,000 sq ft = 4,000 sq ft.
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_residential_far = 1; max_residential_floor_area_sq_ft = 4000
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r2x_r4_residential_far.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r1_r12_residential_far.py`

## What the program does today and a test checks

- The ZR 23-21 standard FAR of 1.00 for R2X, R4A, R4B, R4 and R4-1 is checked byte-for-byte against the captured table (test: test_as1_flat_rule_values_match_snapshot).
- Does not carry the footnote-1 0.60 single-dwelling-unit cap, which only the first ZR 23-21 row carries (test: test_as4_footnote_1_cap_only_on_first_row_rule).
- The qualifying-residential-site FAR values are checked byte-for-byte against the captured second column (test: test_as1_flat_rule_values_match_snapshot).
- Is draft/needs_review, never verified, and effective from 2024-12-05 (test: test_as7_all_rules_are_draft_and_unapproved, test_as7_no_family_result_is_ever_verified).

## In the program but no test checks it

- The maximum residential floor area (FAR x lot area) is computed by the rule but its number is not asserted by a test for R2X/R4; no test found that exercises this value (the same multiply step is asserted for R5 and for R6-R12).
- Evaluating the rule to surface the qualifying alternative as a conditional alternative is not exercised for this rule; no test found that exercises this.

## Planned, not built

- Whether a site qualifies for the higher qualifying FAR (R4 1.50; R2X unchanged at 1.00) is a determination the program does not make.
- Special Purpose District and overlay changes to FAR are not applied.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r1_r12_residential_far.py`
- Counts: 15 passed
- Evidence: [run log](../evidence/r2x-r4-residential-far.txt)
- Rule file digest tested: `9842c6764d1b27a6f6c8a85cfd43334fcdb5411442585bb0f728828537c7efe4`
- Test files tested:
  - `services/api/tests/rules/test_r1_r12_residential_far.py` (`5f6f2278a72a59c9a0e124613107c15b255b870d256744c57eded000a71b0eca`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or any linked test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- The qualifying-residential-site FAR is shown as an alternative, not computed.
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

