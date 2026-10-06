# R6B district - minimum base height, maximum base height and maximum building height, standard residences and qualifying affordable or senior housing (ZR 23-432)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r6b-height`
- Family: residential_height_setback
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 23-432 | [23-432](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432) | 2024-12-05 | 2026-09-30T06:49:08Z | `zr-23-432` | `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c` |

## Where it applies

R6B districts (any building).

## Exceptions and limits

- The qualifying-housing heights are shown as a labelled alternative; the program does not decide whether a development qualifies.
- The setback above the base height (ZR 23-433) is not encoded in this rule.
- A commercial overlay is not captured, and a special district sends the result for professional review.

## How the program reads it

The program reports the R6B row of the ZR 23-432 height table: minimum base height 30 feet, maximum base height 45 feet, maximum building height 55 feet for standard residences, and for qualifying housing a maximum base height of 45 feet and maximum building height of 65 feet. R6B heights do not depend on street width.

## Example

A made-up R6B lot with no overlay and no special district (not a real address).

- Inputs: zoning_district = R6B; overlay_present = no; special_district_present = no
- Expected answer: min_base_height = 30; max_base_height = 45; max_building_height = 55; qualifying_max_base_height = 45; qualifying_max_building_height = 65
- Basis of the expected answer (reference_case): Independent reference case, work-order section 9 table A rows L3 and L4 (an AI agent working ZR 23-432 from the sealed capture): R6B base 30 to 45 ft, building 55 ft standard; base 45 ft, building 65 ft qualifying.
- Who prepared the expected answer: worked independently by a sealed-folder AI agent and recomputed by a second agent; not checked by a professional
- Answer the program gives: min_base_height = 30; max_base_height = 45; max_building_height = 55; qualifying_max_base_height = 45; qualifying_max_building_height = 65
- Result label the program attaches: conditional
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r6b_height.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r6b_far_heights.py`
- These deterministic tests run in the build. The build fails if they fail, so this register never ships with them failing. A green build is a code check, not a human review of the law.

## Gaps

- The setback above the base height (ZR 23-433) is not computed in this rule.
- The qualifying-housing heights are shown as an alternative, not decided.
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

