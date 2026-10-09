# R6B district - maximum number of dwelling units: maximum residential floor area / 680, a fraction of three-quarters or more counting as one unit (ZR 23-52 paragraph (b))

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6b-dwelling-units`
- Family: residential_dwelling_units
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 2 (last changed 2026-10-08)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-52 | [23-52](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52) | 2024-12-05 | 2026-09-30T07:29:29Z | `zr-23-52` | `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac` |
| 23-52(b) | [23-52(b)](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52) | 2024-12-05 | 2026-09-30T07:29:29Z | `zr-23-52` | `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac` |
| 11-25 | [11-25](https://zr.planning.nyc.gov/entityprint/pdf/node/18433) | 1994-06-29 | 2026-09-13T02:45:00Z | `zr-11-25` | `6843ad22d57d4f59cf422c80b820d1797955c1cecfecf3ee459b68bf139b2b2b` |

## Where it applies

R6B districts, for a building with multiple dwelling residences, where there is no special density area and the housing is not qualifying senior housing (those have no dwelling-unit factor).

## Exceptions and limits

- Qualifying senior housing, special density areas and conversions have no dwelling-unit factor; the rule does not apply to them.
- The qualifying-affordable-housing dividend uses a different floor-area basis that the program sends for professional review.
- A special district sends the result for professional review.

## How the program reads it

The program divides the maximum residential floor area by the dwelling-unit factor of 680 (ZR 23-52(b)) to get a dwelling-unit count, then rounds: a remaining fraction of three-quarters or more counts as one unit, otherwise it is dropped. R6B inherits ZR 23-52 through the suffix provision ZR 11-25. In the results document's three-way form (M5-T136) this legal dwelling-unit limit is carried beside the floor-area answer as a value-state: it is shown with its formula when the lot's special-density-area answer is given, and withheld (not known) otherwise; the preliminary apartment-capacity estimate is kept as a separate reserved block that carries no legal figure.

## Example

A made-up R6B case: a 5,000 sq ft lot with 10,000 sq ft of residential floor area (not a real address).

- Inputs: zoning_district = R6B; max_residential_floor_area_sq_ft = 10000; housing_program = standard_residence; special_density_area = no; special_district_present = no
- Expected answer: dwelling_units_before_rounding = 14.705882352941176; max_dwelling_units = 14
- Basis of the expected answer (reference_case): Independent reference case, work-order section 9 table B row P1 (an AI agent working ZR 23-52(b) from the sealed capture): factor 680; 10,000 / 680 = 14.71; a fraction below three-quarters is dropped, so 14.
- Who prepared the expected answer: worked independently by a sealed-folder AI agent and recomputed by a second agent; not checked by a professional
- Answer the program gives: dwelling_units_before_rounding = 14.705882352941176; max_dwelling_units = 14
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r6b_dwelling_units.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r6b_coverage_yard_units.py`

## What the program does today and a test checks

- Divides the maximum residential floor area by 680 and rounds up only at a fraction of three-quarters or more, giving 29 units for the benchmark 20,150 sq ft lot, with the formula carried in the trace (test: test_c12_benchmark_units_29_with_the_formula).
- Rounds correctly across the three-quarters boundary over a range of floor areas (test: test_units_round_up_only_at_three_quarters).
- Is the only rule in the registry that emits a dwelling-unit output for R6B (test: test_units_are_one_place_across_the_registry).
- Returns no estimate for qualifying senior housing or a special density area (no factor applies), and sends qualifying affordable housing to professional review (test: test_qualifying_senior_housing_has_no_factor, test_special_density_area_has_no_factor, test_qualifying_affordable_is_computed_but_sent_to_review).
- Fails closed to professional review on a missing or invalid floor area, program or special-density flag (test: test_unknown_program_area_or_floor_area_gives_no_estimate, test_units_fail_closed_on_a_bad_floor_area).
- Reaches R6B through the ZR 11-25 suffix reading, flagged on every result (test: test_r6b_is_reached_through_zr_11_25_and_every_rule_says_so).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- Conversions and mixed-factor applicability are not computed.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r6b_coverage_yard_units.py`
- Counts: 88 passed
- Evidence: [run log](../evidence/r6b-dwelling-units.txt)
- Rule file digest tested: `404179f2c2aab9c25826c59c92c4715fe0647a8f552cb1e385c72ccc7cb7ef02`
- Test files tested:
  - `services/api/tests/rules/test_r6b_coverage_yard_units.py` (`1e0762436eb031d0e905fe67fd21a0f96ad2acf1ade21b618abacd6e288a2053`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or any linked test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- The qualifying-affordable dividend, qualifying senior housing and conversions are not computed.
- The rule takes the maximum residential floor area as an input; it does not itself check the density-area or unit-mix facts a real determination needs.
- Special districts send the result for professional review.
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

