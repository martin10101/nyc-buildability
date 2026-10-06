# R4B district (flat-roof envelope, ZR 23-422) - maximum building height

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r4b-height`
- Family: residential_height_setback_r3_r4
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-422 | [23-422](https://zr.planning.nyc.gov/article-ii/chapter-3/23-422) | 2024-12-05 | 2026-09-13T00:00:00Z | `zr-23-422-r3-r4` | `0268089074b51d7b2457fa280bb19f5a2ce1c49b708dbb6654f49df78ea61b18` |

## Where it applies

R4B districts (any building; R4B has no pitched-roof counterpart).

## Exceptions and limits

- A commercial overlay, special district, historic district or large site is not adjusted by the program; when one is present the result is sent for professional review instead of a changed number.

## How the program reads it

The program reports a single maximum building height of 25 feet (ZR 23-422) for R4B and marks the result for professional review.

## Example

A made-up R4B lot (not a real address).

- Inputs: zoning_district = R4B
- Expected answer: max_building_height = 25
- Basis of the expected answer (law_text): ZR 23-422: 'R4B ... the maximum building height shall be 25 feet.'
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_building_height = 25
- Result label the program attaches: professional_review_required
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r4b_height.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r3_r4_height.py`

## What the program does today and a test checks

- Reports a single 25-foot maximum building height for R4B and invents no base-height value (test: test_as1_r4b_confident_building_height_only).
- Keeps the R4B 25-foot cap distinct from the R3-2/R4 35-foot cap; neither rule fires for the other's district (test: test_nc2_r4b_25_never_merges_with_r3_2_r4_35).
- Is applicable to R4B only and not to foreign or unknown districts (test: test_nc1_r4b_rule_scoped_to_r4b_only).
- Fails closed to professional review on a missing district, and escalates on an overlay, special district or historic district (test: test_nc5_missing_district_fails_closed, test_nc3_flat_modifier_downgrades_to_professional_review).
- Loads from the packaged registry and evaluates to the 25-foot value (test: test_as6_family_loads_from_default_packaged_registry).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- Overlay, special-district and historic-district adjustments are not computed; the result is sent to professional review.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r3_r4_height.py`
- Counts: 90 passed
- Evidence: [run log](../evidence/test_r3_r4_height.txt)
- Rule file digest tested: `320c6d53feb8e6e74618ca31663f4d57414cecf8b32930c1d4b1f7d807576c3e`
- Test files tested:
  - `services/api/tests/rules/test_r3_r4_height.py` (`155e064f1aad76181651c81027d9851cc4897e9affc184e0d53b08e492420595`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or a test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- Only a single flat building-height cap is given; no base-height / setback split is modelled.
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

