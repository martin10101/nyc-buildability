# R6B district - maximum residential lot coverage for corner, interior and through lots (ZR 23-362 paragraph (a), standard lots)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6b-lot-coverage`
- Family: residential_lot_coverage
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 2 (last changed 2026-10-08)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-362 | [23-362](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362) | 2024-12-05 | 2026-09-30T07:29:06Z | `zr-23-362` | `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9` |
| 11-25 | [11-25](https://zr.planning.nyc.gov/entityprint/pdf/node/18433) | 1994-06-29 | 2026-09-13T02:45:00Z | `zr-11-25` | `6843ad22d57d4f59cf422c80b820d1797955c1cecfecf3ee459b68bf139b2b2b` |

## Where it applies

R6B districts, standard lots, keyed by lot type (corner, interior or through).

## Exceptions and limits

- Only standard lots are covered; the eligible-site percentages (65 or 50 percent) are not computed.
- Special rules for parts of interior or through lots are not captured.
- A commercial overlay is not captured, and a special district sends the result for professional review.

## How the program reads it

The program reports the maximum residential lot coverage from ZR 23-362(a): 100 percent on a corner lot, 80 percent on an interior or through lot. R6B inherits ZR 23-362 through the suffix provision ZR 11-25. In the results document's three-way form (M5-T136) a corner lot whose recorded outline reaches beyond 100 feet of a street line (as the benchmark lot does) has no single whole-lot coverage figure, so coverage is carried as withheld (not known) there rather than shown as a percentage.

## Example

A made-up interior R6B lot with no overlay and no special district (not a real address).

- Inputs: zoning_district = R6B; lot_type = interior; overlay_present = no; special_district_present = no
- Expected answer: max_residential_lot_coverage_percent = 80
- Basis of the expected answer (reference_case): Independent reference case, work-order section 9 (table B and table A row L5, an AI agent working ZR 23-362(a) and ZR 11-25 from the sealed capture): interior and through lots 80 percent; corner lots 100 percent.
- Who prepared the expected answer: worked independently by a sealed-folder AI agent and recomputed by a second agent; not checked by a professional
- Answer the program gives: max_residential_lot_coverage_percent = 80
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r6b_lot_coverage.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r6b_coverage_yard_units.py`

## What the program does today and a test checks

- Reports 100 percent coverage for a corner lot (the benchmark) and 80 percent for interior or through lots, byte-matched to ZR 23-362(a) (test: test_benchmark_corner_lot_coverage_is_100_percent, test_interior_and_through_lots_are_80_percent_with_the_23_363_note).
- Fails closed to professional review and names the input when the lot type is missing, and rejects an unlisted lot type rather than guessing (test: test_unknown_lot_type_gives_no_coverage_and_names_the_input, test_an_unlisted_lot_type_is_rejected_not_guessed).
- Is R6B-only, draft/needs_review, lane-A-gated and not effective before 2024-12-05 (test: test_rules_are_r6b_only, test_rules_are_draft_needs_review_and_lane_a_gated, test_before_the_amendment_date_nothing_is_emitted).
- Reaches R6B through the ZR 11-25 suffix reading, flagged on every result (test: test_r6b_is_reached_through_zr_11_25_and_every_rule_says_so).
- Fails closed to professional review on a special district or an unattested overlay (test: test_special_district_or_unattested_special_district_fails_closed, test_unattested_overlay_fails_closed).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- Only standard lots are covered; the eligible-site percentages and the special interior/through-lot rules are not computed.
- Commercial overlays are not captured.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r6b_coverage_yard_units.py`
- Counts: 88 passed
- Evidence: [run log](../evidence/r6b-lot-coverage.txt)
- Rule file digest tested: `6d1f5c0adb5a6d3a85a28e57466336a0f83b16e96bb72a46fa6196a6256ce95f`
- Test files tested:
  - `services/api/tests/rules/test_r6b_coverage_yard_units.py` (`1e0762436eb031d0e905fe67fd21a0f96ad2acf1ade21b618abacd6e288a2053`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or any linked test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- Only the standard-lot percentages are computed; eligible-site reductions are not.
- For a corner lot the 100 percent applies only to the part within 100 feet of each street line; this rule returns a single percentage and does not compute the corner reach.
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

