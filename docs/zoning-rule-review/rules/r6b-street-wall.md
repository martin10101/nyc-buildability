# R6B with a commercial overlay - the street wall sits within 8 feet of the street line (ZR 35-631(b), via ZR 35-63)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6b-street-wall`
- Family: residential_street_wall
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-15)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 35-631(b) | [35-631(b)](https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631) | 2024-12-05 | 2026-10-07T00:00:00Z | `zr-35-631` | `816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9` |
| 35-63 | [35-63](https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-63) | 2024-12-05 | 2026-10-07T00:00:00Z | `zr-35-63` | `77ff1923e3d3607202964541eb29e714b7cbaa9ab6dde7ddd9ccfbbd032ebe72` |
| 23-431 | [23-431](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-431) | 2024-12-05 | 2026-10-04T00:00:00Z | `zr-23-431` | `fb2d094dd06ce10b406485932357a39384a357db92a0a1670b56091c36698c69` |
| 11-25 | [11-25](https://zr.planning.nyc.gov/entityprint/pdf/node/18433) | 1994-06-29 | 2026-09-13T02:45:00Z | `zr-11-25` | `6843ad22d57d4f59cf422c80b820d1797955c1cecfecf3ee459b68bf139b2b2b` |

## Where it applies

R6B districts with a commercial overlay: ZR 35-63 sends the street-wall location to ZR 35-631, whose paragraph (a) is limited to R8-R12 districts in the Manhattan Core, so for this R6B lot paragraph (b) governs - at least 70 percent of the aggregate street-wall width within 8 feet of each street line. Without the overlay the plain-R6B rule ZR 23-431(b) applies (8 feet on a wide-street frontage, 10 feet on a narrow one); that per-frontage reading is in the engine, not this draft rule.

## Exceptions and limits

- Only the overlay 8-foot distance is recorded here; the plain-R6B 8-wide / 10-narrow asymmetry (D-051) is read in the engine.
- A commercial overlay is assumed; a special district sends the result for professional review.

## How the program reads it

The engine reads the street-wall location as a labelled draft (M5-T170): under a commercial overlay the street wall sits within 8 feet of each street line (ZR 35-631(b), reached by 35-63 for a mixed building via 35-01 and for an all-residential one via 34-11 and 34-24(b)(1)); without the overlay ZR 23-431(b) applies 8 feet on a wide-street frontage and 10 feet on a narrow one (the D-051 asymmetry, never collapsed). R6B inherits ZR 23 and 35 through the suffix provision ZR 11-25. The reading is conditional on the block's prevailing street-wall frontage and the operative street line, which a mapped width does not fix, so the constraint line (street_wall_band) is not_established on the benchmark. The expected outcomes are the R6B reference case (overlay-reading.json row street-wall-location), not a program run.

## Example

A made-up R6B corner lot with a C2-2 overlay, both frontages fronting a street (not a real address).

- Inputs: zoning_district = R6B; overlay_present = yes; special_district_present = no
- Expected answer: street_wall_max_distance_from_street_line_ft = 8
- Basis of the expected answer (reference_case): Independent reference case overlay-reading.json row street-wall-location (two AI readings of the sealed step-P2 captures): the overlay changes the street-wall rule to ZR 35-631(b), at least 70 percent of the aggregate street-wall width within 8 feet of the street line. The final street-wall line is not fixed (prevailing frontage and the operative street line unrecorded).
- Who prepared the expected answer: worked independently by sealed-folder AI readers; not checked by a professional
- Answer the program gives: street_wall_max_distance_from_street_line_ft = 8
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r6b_street_wall.rule.json`
- `services/api/app/scenario/three_answers/envelope_constraints.py`

## Tests

- `services/api/tests/scenario/three_answers/test_envelope_constraints.py`

## What the program does today and a test checks

- The street wall always applies and is a conditional reading (prevailing frontage, operative street line) (test: test_street_wall_always_applies_and_is_conditional).
- Under a commercial overlay the street wall sits within 8 feet of each frontage for a residential-only and a mixed building (test: test_street_wall_overlay_is_eight_feet_each_frontage_for_both_building_types).
- Without the overlay it is 8 feet on a wide frontage and 10 feet on a narrow one, never collapsed (test: test_street_wall_no_overlay_is_eight_wide_ten_narrow_never_collapsed).
- An unknown-width frontage without the overlay shows no distance, never narrow by default (test: test_street_wall_no_overlay_unknown_width_shows_no_distance_never_narrow).
- When the overlay was not read the distance is withheld with the dependency named (test: test_street_wall_overlay_not_read_withholds_the_distance).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- The prevailing-street-wall-frontage adjacency test (ZR 35-631 closing clause / 23-431(a)) is not computed.
- The operative street-line position is not fixed from a mapped width.

## Automated test result

- Status: Not run
- Commit tested: ``
- Date tested: 2026-10-15
- Command: `python -m pytest -q services/api/tests/scenario/three_answers/test_envelope_constraints.py`
- Counts: 
- Evidence: [run log](../evidence/r6b-street-wall.txt)
- Rule file digest tested: `2caa1c1e4b7c960126b95b26c750f57782f1fbfd9c292a42cc5bffeaba2af242`
- Test files tested:
  - `services/api/tests/scenario/three_answers/test_envelope_constraints.py` (`92e99bc79848429a72e9417a963feea9476a451d490c4ff33bc139304ed66c86`)
- A draft extraction: its deterministic DSL suite is not yet written, so the status reads 'Not run'. The law reading it records is exercised in the engine's envelope analysis by the linked tests; a passing result there is a code check, not a human or professional review of the law.

## Gaps

- The exact street-wall position within paragraph (b) is conditional on the prevailing street-wall frontage and the operative street line.
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

