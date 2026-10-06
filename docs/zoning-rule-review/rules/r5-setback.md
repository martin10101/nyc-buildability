# R5 district (flat-roof envelope) - required setback depth above the base height

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r5-setback`
- Family: residential_height_setback
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-423 | [23-423](https://zr.planning.nyc.gov/article-ii/chapter-3/23-423) | 2024-12-05 | 2026-07-22T00:00:00Z | `zr-23-423` | `b0b062fbb570ea5bc437572a144eb63f207aa73bdfe8cc612e938f0f3cb72903` |
| 12-10 | [12-10](https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10) | 2024-12-05 | 2026-09-14T02:15:06Z | `zr-12-10` | `23a9ccad31f1081fd15de94d796c22d540e7e8bcfe986e64c9ba302bf8fa4fde` |
| 23-422 | [23-422](https://zr.planning.nyc.gov/article-ii/chapter-3/23-422) | 2024-12-05 | 2026-07-22T00:00:00Z | `zr-23-422` | `7e910c245bfc4c8f1a65ffdbdaf9b4985b71477338d3173c13f2a77395f0148a` |

## Where it applies

R5 districts, for the setback above the base height of a flat-roof building, keyed by whether the street wall fronts a wide or a narrow street.

## Exceptions and limits

- Other modifications to the ZR 23-423 setback are not resolved; recorded as a limitation.
- A commercial overlay or special district sends the result for professional review.

## How the program reads it

The program reports the required setback depth from ZR 23-423: 10 feet from a street wall on a wide street, 15 feet on a narrow street. It marks the result for professional review.

## Example

A made-up R5 lot with a street wall fronting a wide street (not a real address).

- Inputs: zoning_district = R5; street_width_class = wide
- Expected answer: required_setback_depth = 10
- Basis of the expected answer (law_text): ZR 23-423: 'The depth of the setback shall be at least 10 feet from a street wall fronting on a wide street, and at least 15 feet from a street wall fronting on a narrow street.' Wide street -> 10 feet.
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: required_setback_depth = 10
- Result label the program attaches: professional_review_required
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r5_setback.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r5_height_setback.py`
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- Only the plain 10 ft / 15 ft depth is reported; other ZR 23-423 modifications are not resolved.
- Whether a street is wide or narrow must be supplied; the program does not determine it in this rule.
- Overlays and special districts send the result for professional review.
- This is a draft extraction awaiting raw-source verification and a qualified-human legal check.

## Human review

- Verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -

