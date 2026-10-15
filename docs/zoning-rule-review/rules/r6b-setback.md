# R6B - a setback above the maximum base height (ZR 23-433; 35-632(a) under a commercial overlay): at least 10 feet from a wide-street wall and 15 feet from a narrow-street wall

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6b-setback`
- Family: residential_setback_above_base
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-15)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-433 | [23-433](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-433) | 2024-12-05 | 2026-10-04T00:00:00Z | `zr-23-433` | `4fecf4d26719a00ed0eaeb1e0e7e714f891e7fff154ded306b04e29167ef1afe` |
| 23-432 | [23-432](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432) | 2024-12-05 | 2026-09-30T00:00:00Z | `zr-23-432` | `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c` |
| 35-632(a) | [35-632(a)](https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-632) | 2024-12-05 | 2026-10-07T00:00:00Z | `zr-35-632` | `8105cc331eee4ed882e04466814928f6047618f5ba66a260f5c415a29630ad10` |
| 11-25 | [11-25](https://zr.planning.nyc.gov/entityprint/pdf/node/18433) | 1994-06-29 | 2026-09-13T02:45:00Z | `zr-11-25` | `6843ad22d57d4f59cf422c80b820d1797955c1cecfecf3ee459b68bf139b2b2b` |

## Where it applies

R6B districts: a setback is required only for the part of a building street wall that exceeds the maximum base height (45 feet for R6B standard residences, ZR 23-432); ZR 23-433 then requires at least 10 feet from a wide-street wall and 15 feet from a narrow-street wall. Under a commercial overlay the same depths are reached through ZR 35-632(a). ZR 23-433(a) to (d) may reduce the depths.

## Exceptions and limits

- No setback is required at or below the maximum base height; the benchmark 30-foot option triggers none.
- ZR 23-433(a) to (d) modifications and the per-frontage wide/narrow depth are read in the engine; a special district sends the result for professional review.

## How the program reads it

The engine reads the setback above the base as a labelled draft (M5-T170): it is triggered only where the building street wall rises strictly above the 45-foot maximum base height (ZR 23-432); where triggered, ZR 23-433 requires at least 10 feet from a wide-street wall and 15 feet from a narrow-street wall (35-632(a) under the overlay). The per-frontage wide/narrow class comes from the accepted D-052 classifier; a frontage whose width is unresolved or unknown withholds its depth (never narrow by default, D-051). The benchmark three-storey 30-foot option equals the minimum base height and triggers no setback, so the row is not_applicable and carries the 10/15-foot depths as values with a condition naming the above-45-foot trigger. ZR 23-433(a) to (d) may reduce the depths. R6B inherits through ZR 11-25. The expected outcomes are overlay-reading.json row setback-above-base, not a program run.

## Example

A made-up R6B lot with a C2-2 overlay and a building street wall that rises above the 45-foot maximum base height (not a real address).

- Inputs: zoning_district = R6B; overlay_present = yes; street_wall_exceeds_max_base_height = yes; special_district_present = no
- Expected answer: setback_depth_from_wide_street_wall_ft = 10
- Basis of the expected answer (reference_case): Independent reference case overlay-reading.json row setback-above-base: at least 10 feet above the maximum base height on the wide street and 15 feet on the narrow street, via ZR 35-632(a) to ZR 23-433; the overlay does not change the depths.
- Who prepared the expected answer: worked independently by sealed-folder AI readers; not checked by a professional
- Answer the program gives: setback_depth_from_wide_street_wall_ft = 10
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r6b_setback.rule.json`
- `services/api/app/scenario/three_answers/envelope_constraints.py`

## Tests

- `services/api/tests/scenario/three_answers/test_envelope_constraints.py`

## What the program does today and a test checks

- The setback is triggered only strictly above the 45-foot maximum base height; 30, 44.99 and 45.00 feet trigger none and 45.01 and 50 feet trigger it (test: test_setback_trigger_table_strict_above_the_maximum_base_height).
- Where triggered the depths are 10 feet on a wide-street frontage and 15 feet on a narrow one (test: test_setback_depths_are_ten_wide_fifteen_narrow_cited).
- At or below the maximum base height the row is not_applicable and carries the depths as values with the above-base condition (test: test_setback_not_applicable_carries_the_depths_and_the_above_base_condition).
- The per-frontage wide/narrow class drives the depth through the accepted D-052 classifier; an unresolved or unknown width withholds the depth, never narrow by default (test: test_per_frontage_width_class_drives_the_setback_depth).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- The ZR 23-433(a) to (d) depth modifications are not computed.
- The setback geometry on the lot is not drawn (the line is not_established).

## Automated test result

- Status: Not run
- Commit tested: ``
- Date tested: 2026-10-15
- Command: `python -m pytest -q services/api/tests/scenario/three_answers/test_envelope_constraints.py`
- Counts: 
- Evidence: [run log](../evidence/r6b-setback.txt)
- Rule file digest tested: `1f7df4f0b10e024b9ced6928e54467e31d8543ce20c349fb552ab37a17a0d185`
- Test files tested:
  - `services/api/tests/scenario/three_answers/test_envelope_constraints.py` (`92e99bc79848429a72e9417a963feea9476a451d490c4ff33bc139304ed66c86`)
- A draft extraction: its deterministic DSL suite is not yet written, so the status reads 'Not run'. The law reading it records is exercised in the engine's envelope analysis by the linked tests; a passing result there is a code check, not a human or professional review of the law.

## Gaps

- ZR 23-433(a) to (d) may reduce the depths; not computed here.
- A draft extraction awaiting raw-source verification and a qualified-human legal check.

## Human review

- Current verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -
- The verdict shown above is derived from the reviewer's recorded decision and whether that decision still matches the current rule file, law captures and revision. A verdict is a named human reviewer's own answer; agent reviews are never recorded here.

