# R5-series qualifying residential site - alternative maximum base height and building height (section 23-424)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r5-qrs-height`
- Family: residential_height_setback
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-424 | [23-424](https://zr.planning.nyc.gov/article-ii/chapter-3/23-424) | 2024-12-05 | 2026-07-22T00:00:00Z | `zr-23-424` | `1ad17144b64593652e67e49edf7c1006e9c476074ce62d076e9804da844ce506` |
| 23-423 | [23-423](https://zr.planning.nyc.gov/article-ii/chapter-3/23-423) | 2024-12-05 | 2026-07-22T00:00:00Z | `zr-23-423` | `b0b062fbb570ea5bc437572a144eb63f207aa73bdfe8cc612e938f0f3cb72903` |

## Where it applies

R5-series qualifying residential sites (R5, R5A, R5B, R5D) - only when the lot is flagged as a qualifying residential site.

## Exceptions and limits

- The ZR 23-423 setback for this envelope is a separate constraint, not restated here.
- Whether a lot is a qualifying residential site is a separate determination the program cannot make.
- A commercial overlay or special district sends the result for professional review.

## How the program reads it

For a qualifying residential site the program reports the alternative envelope from the ZR 23-424 table: maximum base height 45 feet and maximum building height 55 feet. It marks the result for professional review.

## Example

A made-up R5 lot flagged as a qualifying residential site (not a real address).

- Inputs: zoning_district = R5; qualifying_residential_site = yes
- Expected answer: max_base_height = 45; max_building_height = 55
- Basis of the expected answer (law_text): ZR 23-424 table, row R5 R5A R5B R5D: maximum base height 45, maximum building height 55.
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_base_height = 45; max_building_height = 55
- Result label the program attaches: professional_review_required
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r5_qrs_height.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r5_height_setback.py`
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- Whether a lot qualifies as a qualifying residential site is not decided by the program.
- The ZR 23-423 setback for this envelope is not restated here.
- This is a draft extraction awaiting raw-source verification and a qualified-human legal check.

## Human review

- Verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -

