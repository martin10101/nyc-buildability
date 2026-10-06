# R5 district (flat-roof envelope) - maximum base height and maximum building height

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r5-height`
- Family: residential_height_setback
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-422 | [23-422](https://zr.planning.nyc.gov/article-ii/chapter-3/23-422) | 2024-12-05 | 2026-07-22T00:00:00Z | `zr-23-422` | `7e910c245bfc4c8f1a65ffdbdaf9b4985b71477338d3173c13f2a77395f0148a` |

## Where it applies

Bare R5 districts (no letter suffix), any building.

## Exceptions and limits

- No minimum base height is stated for R5; recorded as a limitation.
- A commercial overlay, special district, historic district or large site is not adjusted by the program; when one is present the result is sent for professional review instead of a changed number.

## How the program reads it

The program reports a maximum base height of 35 feet and a maximum building height of 45 feet (ZR 23-422), and marks the result for professional review. A setback above the base height is governed by a separate rule.

## Example

A made-up bare R5 lot (not a real address).

- Inputs: zoning_district = R5
- Expected answer: max_base_height = 35; max_building_height = 45
- Basis of the expected answer (law_text): ZR 23-422: 'except R5 Districts with a letter suffix, the maximum base height shall be 35 feet, and the maximum building height shall be 45 feet.'
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_base_height = 35; max_building_height = 45
- Result label the program attaches: professional_review_required
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r5_height.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r5_height_setback.py`
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- The setback above the base height is in a separate rule (ZR 23-423), not combined here.
- Overlays, special districts, historic districts and large sites send the result for professional review.
- This is a draft extraction awaiting raw-source verification and a qualified-human legal check.

## Human review

- Verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -

