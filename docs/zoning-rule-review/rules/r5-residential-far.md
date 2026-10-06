# R5 residence districts - maximum residential floor area ratio (standard zoning lots)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r5-residential-far`
- Family: residential_far
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-21 | [23-21](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-21) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-21` | `b52771e629b6afa9f9a6843a657dbfd143294f721cd757f953792e747a48ad8a` |

## Where it applies

R5 districts (R5A, R5B, R5) of the ZR 23-21 floor-area table. R5D sits in its own row (2.00) and other districts are reported as not applicable.

## Exceptions and limits

- A qualifying residential site is allowed a higher FAR (2.00); the program shows this as a labelled alternative and does not decide whether a site qualifies.
- A Special Purpose District or other overlay may change the floor area; the program does not apply that change.

## How the program reads it

The program looks up the district's standard FAR (1.50 for R5/R5A/R5B) and multiplies it by the lot area to give the largest residential floor area allowed.

## Example

A made-up 4,000 sq ft R5 lot (not a real address).

- Inputs: zoning_district = R5; lot_area_sq_ft = 4000
- Expected answer: max_residential_far = 1.5; max_residential_floor_area_sq_ft = 6000
- Basis of the expected answer (law_text): ZR 23-21 table, row R5A/R5B/R5: standard zoning lots 1.50. 1.50 x 4,000 sq ft = 6,000 sq ft.
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_residential_far = 1.5; max_residential_floor_area_sq_ft = 6000
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r5_residential_far.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_rules_engine.py`
- `services/api/tests/rules/test_r1_r12_residential_far.py`

## What the program does today and a test checks

- Reports max_residential_far = 1.50 and max_residential_floor_area_sq_ft via an identity-then-multiply step for an R5 10,000 sq ft lot, with the full trace (test: test_re_s1_dsl_round_trip_and_full_trace).
- Gives a deterministic, byte-identical trace for the same inputs, with R5D at 2.00 (test: test_re_s8_determinism_same_inputs_identical_trace).
- Is conditional and never verified without a recorded professional approval (test: test_re_s2_draft_rule_never_verified, test_re_s2_verified_only_for_published_with_matching_approval).
- No longer carries the footnote-1 0.60 cap, and its FAR values match the captured ZR 23-21 table (test: test_as9_r5_no_longer_carries_footnote_cap_r1r2r3_does, test_as9_r5_far_values_unchanged_and_match_snapshot).

## In the program but no test checks it

- Evaluating the rule to surface the qualifying-residential-site FAR as a conditional alternative is not exercised for this rule; no test found that exercises this.

## Planned, not built

- Whether a site qualifies for the higher qualifying FAR is a determination the program does not make.
- Special Purpose District and overlay changes to FAR are not applied.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_rules_engine.py tests/rules/test_r1_r12_residential_far.py`
- Counts: 51 passed
- Evidence: [run log](../evidence/r5-residential-far.txt)
- Rule file digest tested: `ca6ccb5286cdbb31c318d9e0ff4342cb7d649fd03be7a79af7ec3521b274b13e`
- Test files tested:
  - `services/api/tests/rules/test_rules_engine.py` (`1098e99b91df603037395d035f7ba47e5b4b6b743048129818d5d9032551bcb7`)
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

