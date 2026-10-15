# R6B - no side yard is required for a residence other than a single- or two-family detached one (ZR 23-335(b)); a commercial overlay removes it for any residential building (ZR 34-232)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6b-side-yard`
- Family: residential_side_yard
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-15)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-335(b) | [23-335(b)](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-335) | 2024-12-05 | 2026-10-07T00:00:00Z | `zr-23-335` | `31b67b9d47eca82cb93e1b06db908b20f1ad7f159c2b4306d78248e5fb02fcf2` |
| 34-232 | [34-232](https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-232) | 2024-12-05 | 2026-10-07T00:00:00Z | `zr-34-232` | `9cf83f8d9c3fa6f594fa3be1e1d65651713c1809254fd08e60e527daa09c61b2` |
| 11-25 | [11-25](https://zr.planning.nyc.gov/entityprint/pdf/node/18433) | 1994-06-29 | 2026-09-13T02:45:00Z | `zr-11-25` | `6843ad22d57d4f59cf422c80b820d1797955c1cecfecf3ee459b68bf139b2b2b` |

## Where it applies

R6B districts: ZR 23-335(b) requires no side yard for a residence other than a single- or two-family detached one (any open area along a side lot line must be at least 5 feet wide); under a commercial overlay ZR 34-232 removes the requirement for any residential building. A single- or two-family detached residence needs two 5-foot side yards under ZR 23-335(a) without the overlay.

## Exceptions and limits

- The detached one- or two-family case (two 5-foot side yards, ZR 23-335(a)) and the 5-foot open-area minimum are read in the engine.
- A special district sends the result for professional review.

## How the program reads it

The engine reads the side yard as a labelled draft (M5-T170): no side yard is required for a residence other than a single- or two-family detached one (ZR 23-335(b)), and a commercial overlay removes the requirement for any residential building (ZR 34-232). A single- or two-family detached residence needs two 5-foot side yards under ZR 23-335(a) without the overlay. Any open area along a side lot line, if provided, must be at least 5 feet wide. A building type that is not stated is never taken as residential-only (the detached case stays a named condition). R6B inherits through ZR 11-25. The expected outcomes are the law text in E13/E14 of record NB-06, not a program run.

## Example

A made-up R6B multi-family residence with a C2-2 overlay (not a real address).

- Inputs: zoning_district = R6B; overlay_present = yes; single_or_two_family_detached = no; special_district_present = no
- Expected answer: side_yard_required = 0
- Basis of the expected answer (reference_case): Record NB-06 reading of ZR 23-335(b) and ZR 34-232: no side yard is required for a residence other than a single- or two-family detached one, and the overlay removes it for any residential building; any open area along a side lot line must be at least 5 feet wide.
- Who prepared the expected answer: worked independently from the captured law text; not checked by a professional
- Answer the program gives: side_yard_required = 0
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r6b_side_yard.rule.json`
- `services/api/app/scenario/three_answers/envelope_constraints.py`

## Tests

- `services/api/tests/scenario/three_answers/test_envelope_constraints.py`

## What the program does today and a test checks

- No side yard is required for a multi-family residence (test: test_side_yard_multi_family_none_required).
- A single- or two-family detached residence without the overlay needs two 5-foot side yards (test: test_side_yard_detached_without_overlay_two_five_foot_yards).
- A detached residence in the overlay needs none (ZR 34-232) (test: test_side_yard_detached_in_overlay_none_required).
- Any open area along a side lot line carries a 5-foot minimum (test: test_side_yard_open_area_minimum_is_five_feet).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- The 5-foot open-area minimum and the detached-residence case are read in the engine, not this draft rule.

## Automated test result

- Status: Not run
- Commit tested: ``
- Date tested: 2026-10-15
- Command: `python -m pytest -q services/api/tests/scenario/three_answers/test_envelope_constraints.py`
- Counts: 
- Evidence: [run log](../evidence/r6b-side-yard.txt)
- Rule file digest tested: `0676ae01704abdff07ec0991f4998f5a9a76766672ac43a2a17f027a26f5ca42`
- Test files tested:
  - `services/api/tests/scenario/three_answers/test_envelope_constraints.py` (`92e99bc79848429a72e9417a963feea9476a451d490c4ff33bc139304ed66c86`)
- A draft extraction: its deterministic DSL suite is not yet written, so the status reads 'Not run'. The law reading it records is exercised in the engine's envelope analysis by the linked tests; a passing result there is a code check, not a human or professional review of the law.

## Gaps

- A side yard is not prohibited; it is optional with a 5-foot open-area minimum.
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

