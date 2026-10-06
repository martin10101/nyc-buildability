# R1/R2 no-letter-suffix districts (R1-1, R1-2, R2) - section 23-421(g) reference-plane elevation allowance

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r1-r2-reference-plane-23421g`
- Family: residential_height_setback_r1_r2
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-421(g) | [23-421(g)](https://zr.planning.nyc.gov/entityprint/pdf/node/18075) | 2024-12-05 | 2026-09-13T02:44:00Z | `zr-23-421-g` | `52dd8aab6e2a7e53f65c953157b70e899f7be94438d0c3456731ff430c626536` |

## Where it applies

R1 and R2 districts without a letter suffix (R1-1, R1-2, R2), for a detached, semi-detached or zero-lot-line building, where the lot is either at least 9,500 sq ft and 100 ft wide, or has a rear-to-front slope of at least five percent.

## Exceptions and limits

- The 5-ft allowance feeds a sloping-plane geometry the program does not compute; recorded as a limitation.
- Site-specific modifiers are not modelled here.

## How the program reads it

When the lot meets the ZR 23-421(g) trigger, the program reports that the reference plane used for the pitched-envelope rules may sit up to 5 feet above the base plane. This is an allowance that feeds the pitched-plane geometry; it does not change the 25 ft wall or 35 ft ridge caps.

## Example

A made-up 10,000 sq ft, 100 ft wide detached R2 lot (not a real address); it meets the area-and-width trigger.

- Inputs: zoning_district = R2; building_type = detached; lot_area_sqft = 10000; lot_width_ft = 100; rear_wall_slope_percent = 0
- Expected answer: reference_plane_elevation_max_ft = 5
- Basis of the expected answer (law_text): ZR 23-421(g): for R1/R2 without a letter suffix on a lot of at least 9,500 sq ft and 100 ft wide (or a slope of at least five percent), 'the reference plane ... may be located up to five feet above the base plane.'
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: reference_plane_elevation_max_ft = 5
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r1_r2_reference_plane_23421g.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r1_r2_height_setback.py`

## What the program does today and a test checks

- Reports a 5-foot reference-plane elevation allowance when the lot meets the area-and-width path (at least 9,500 sq ft and 100 ft wide) or the slope path (at least 5 percent) (test: test_as1_reference_plane_g_confident_when_area_and_width_satisfy, test_as1_reference_plane_g_confident_when_slope_satisfies).
- Checks the exact trigger boundaries (9,500 / 100 / 5 percent) and returns not applicable just below them (test: test_nc8_trigger_boundary_values).
- Excludes the letter-suffix districts (R1-2A, R2A, R2X) and bare R1 even with a satisfying trigger, and admits the no-suffix members R1-1, R1-2, R2 (test: test_nc2_letter_suffix_and_bare_r1_excluded_from_reference_plane, test_nc2_no_letter_suffix_members_eligible).
- Fails closed to professional review when any one of the three geometry inputs, or the building form, is missing (test: test_nc5_reference_plane_missing_any_single_geometry_input_fails_closed, test_nc4_reference_plane_building_type_unavailable_fails_closed).
- Is complementary to the envelope rules and never a same-family conflict (test: test_nc7_reference_plane_rule_never_conflicts_with_envelope_rules).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- The reference plane feeds the sloping-plane geometry, which the program does not compute.
- Site-specific modifiers are not modelled in this rule.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r1_r2_height_setback.py`
- Counts: 110 passed
- Evidence: [run log](../evidence/test_r1_r2_height_setback.txt)
- Rule file digest tested: `39632cfe424a48fbf68c9553e31658b823743a208eb4bbd403fd8ee661e003fa`
- Test files tested:
  - `services/api/tests/rules/test_r1_r2_height_setback.py` (`30e10fe9dd52e85b79c63ee5d811f6d24df42beef3fe341f46ae75ebe1cfd10d`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or a test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- The 5-ft allowance only feeds the pitched-plane geometry, which the program does not compute.
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

