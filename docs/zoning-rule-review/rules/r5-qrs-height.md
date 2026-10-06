# R5-series qualifying residential site - alternative maximum base height and building height (section 23-424)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r5-qrs-height`
- Family: residential_height_setback
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-424 | [23-424](https://zr.planning.nyc.gov/article-ii/chapter-3/23-424) | 2024-12-05 | 2026-07-22T00:00:00Z | `zr-23-424` | `1ad17144b64593652e67e49edf7c1006e9c476074ce62d076e9804da844ce506` |
| 23-423 | [23-423](https://zr.planning.nyc.gov/article-ii/chapter-3/23-423) | 2024-12-05 | 2026-07-22T00:00:00Z | `zr-23-423` | `b0b062fbb570ea5bc437572a144eb63f207aa73bdfe8cc612e938f0f3cb72903` |

## Where it applies

R5-series qualifying residential sites (R5, R5A, R5B, R5D) - only when the lot is flagged as a qualifying residential site.

## Exceptions and limits

- The ZR 23-423 setback for this envelope is a separate constraint, not restated here.
- Whether a lot is a qualifying residential site is a separate determination the program cannot make.
- A commercial overlay or special district sends the result for professional review.

## How the program reads it

For a qualifying residential site the program reports the alternative envelope from the ZR 23-424 table: maximum base height 45 feet and maximum building height 55 feet. It marks the result for professional review.

## Example

A made-up R5 lot flagged as a qualifying residential site (not a real address).

- Inputs: zoning_district = R5; qualifying_residential_site = yes
- Expected answer: max_base_height = 45; max_building_height = 55
- Basis of the expected answer (law_text): ZR 23-424 table, row R5 R5A R5B R5D: maximum base height 45, maximum building height 55.
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_base_height = 45; max_building_height = 55
- Result label the program attaches: professional_review_required
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r5_qrs_height.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r5_height_setback.py`

## What the program does today and a test checks

- Fails closed to professional review when the qualifying-residential-site geography is not supplied (test: test_nc4_qualifying_site_geography_unavailable_fails_closed).
- Is reported as a same-family conflict against the base R5 height rule for base and building height, with no value chosen (test: test_nc7_base_and_qrs_rules_conflict_no_value).
- Every family rule, this one included, is needs_review, verified-ineligible and effective from 2024-12-05 (test: test_as5_every_family_rule_is_needs_review_and_verified_ineligible).

## In the program but no test checks it

- The 35-foot base and 35-foot building height this rule reports for a qualifying site are not asserted by a value test in this suite; no test found that exercises the emitted values (the conflict and fail-closed paths are tested instead).

## Planned, not built

- Whether a lot is a qualifying residential site is a determination the program does not make.
- The ZR 23-423 setback is recorded as a limitation, not computed.
- Overlay and special-district adjustments are sent to professional review.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r5_height_setback.py`
- Counts: 47 passed
- Evidence: [run log](../evidence/test_r5_height_setback.txt)
- Rule file digest tested: `f1364c06d5a4239146dd6686bdae8555f6a176fe829c6d9c7e51df5444457b8e`
- Test files tested:
  - `services/api/tests/rules/test_r5_height_setback.py` (`93901f9646e17cd9e0b00b86da9af822a099ce0d6e5e2bfe4cc483760de750af`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or a test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- Whether a lot qualifies as a qualifying residential site is not decided by the program.
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

