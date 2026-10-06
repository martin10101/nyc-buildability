# R6B district - minimum base height, maximum base height and maximum building height, standard residences and qualifying affordable or senior housing (ZR 23-432)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6b-height`
- Family: residential_height_setback
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-432 | [23-432](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432) | 2024-12-05 | 2026-09-30T06:49:08Z | `zr-23-432` | `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c` |

## Where it applies

R6B districts (any building).

## Exceptions and limits

- The qualifying-housing heights are shown as a labelled alternative; the program does not decide whether a development qualifies.
- The setback above the base height (ZR 23-433) is not encoded in this rule.
- A commercial overlay is not captured, and a special district sends the result for professional review.

## How the program reads it

The program reports the R6B row of the ZR 23-432 height table: minimum base height 30 feet, maximum base height 45 feet, maximum building height 55 feet for standard residences, and for qualifying housing a maximum base height of 45 feet and maximum building height of 65 feet. R6B heights do not depend on street width.

## Example

A made-up R6B lot with no overlay and no special district (not a real address).

- Inputs: zoning_district = R6B; overlay_present = no; special_district_present = no
- Expected answer: min_base_height = 30; max_base_height = 45; max_building_height = 55; qualifying_max_base_height = 45; qualifying_max_building_height = 65
- Basis of the expected answer (reference_case): Independent reference case, work-order section 9 table A rows L3 and L4 (an AI agent working ZR 23-432 from the sealed capture): R6B base 30 to 45 ft, building 55 ft standard; base 45 ft, building 65 ft qualifying.
- Who prepared the expected answer: worked independently by a sealed-folder AI agent and recomputed by a second agent; not checked by a professional
- Answer the program gives: min_base_height = 30; max_base_height = 45; max_building_height = 55; qualifying_max_base_height = 45; qualifying_max_building_height = 65
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r6b_height.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r6b_far_heights.py`

## What the program does today and a test checks

- Reports all five R6B heights (min base 30, max base 45, building 55 standard; qualifying max base 45, building 65) from the one ZR 23-432 lookup, labelled and conditional, for the benchmark lot (test: test_c1_benchmark_heights_from_the_one_lookup).
- The rule parameters are byte-equal to the ZR 23-432 R6B snapshot row (test: test_rule_parameters_are_byte_equal_to_the_snapshot_rows).
- Is the only rule that emits a height in feet for R6B (test: test_c1_no_other_rule_emits_a_height_for_r6b).
- Attaches the overlay note only when an overlay is mapped, and fails closed on a special district or unattested inputs (test: test_c1_overlay_note_only_when_an_overlay_is_mapped, test_c1_special_district_or_unattested_inputs_fail_closed).
- Is R6B-only, draft/needs_review, lane-A-gated and not effective before 2024-12-05 (test: test_c1_height_rule_is_r6b_only, test_new_rules_are_draft_needs_review_and_lane_a_gated, test_before_the_amendment_date_nothing_is_emitted).
- Records that R6B heights do not depend on street width (test: test_c1_benchmark_heights_from_the_one_lookup).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- The ZR 23-433 setback above the base height is not encoded.
- Commercial overlays are not captured.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r6b_far_heights.py`
- Counts: 32 passed
- Evidence: [run log](../evidence/r6b-height.txt)
- Rule file digest tested: `86507408a473f672cae795b488d308508872822617a01348b978a49a28e4a792`
- Test files tested:
  - `services/api/tests/rules/test_r6b_far_heights.py` (`7e7f505c58155f4dcc6172d78d81f4957a6764d558fb31c0f476b2e0c924daf4`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or any linked test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- The setback above the base height (ZR 23-433) is not computed in this rule.
- The qualifying-housing heights are shown as an alternative, not decided.
- Commercial overlays are not captured; special districts send the result for professional review.
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

