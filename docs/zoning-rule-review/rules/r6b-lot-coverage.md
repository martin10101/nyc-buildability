# R6B district - maximum residential lot coverage for corner, interior and through lots (ZR 23-362 paragraph (a), standard lots)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6b-lot-coverage`
- Family: residential_lot_coverage
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

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

The program reports the maximum residential lot coverage from ZR 23-362(a): 100 percent on a corner lot, 80 percent on an interior or through lot. R6B inherits ZR 23-362 through the suffix provision ZR 11-25.

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
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- Only the standard-lot percentages are computed; eligible-site reductions are not.
- For a corner lot the 100 percent applies only to the part within 100 feet of each street line; this rule returns a single percentage and does not compute the corner reach.
- Commercial overlays are not captured; special districts send the result for professional review.
- This is a draft extraction awaiting raw-source verification and a qualified-human legal check.

## Human review

- Verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -

