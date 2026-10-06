# R1/R2 suffixed districts (R1-1, R1-2, R1-2A, R2A, R2X) - pitched-roof envelope: maximum perimeter-wall height and maximum ridge/building height

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading of the law. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice.

- Rule id: `r1-r2-suffix-variants-pitched-height`
- Family: residential_height_setback_r1_r2
- Rule version: 0.1.0-draft
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-06)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Content digest (sha256) |
|---|---|---|---|---|---|
| 11-25 | [11-25](https://zr.planning.nyc.gov/entityprint/pdf/node/18433) | 1994-06-29 | 2026-09-13T02:45:00Z | `zr-11-25` | `6843ad22d57d4f59cf422c80b820d1797955c1cecfecf3ee459b68bf139b2b2b` |
| 23-421 | [23-421](https://zr.planning.nyc.gov/entityprint/pdf/node/18075) | 2024-12-05 | 2026-09-13T02:44:00Z | `zr-23-421-r1-r2` | `1bce881805d9ee4d79253432ad86128b7203f81f2054ff25e1ba8dfb1dad1e8b` |
| 23-21 | [23-21](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-21) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-21` | `b52771e629b6afa9f9a6843a657dbfd143294f721cd757f953792e747a48ad8a` |

## Where it applies

The suffixed R1/R2 districts (R1-1, R1-2, R1-2A, R2A, R2X) for a detached, semi-detached or zero-lot-line building. Bare R1/R2 are handled by a separate rule.

## Exceptions and limits

- Applying the pitched envelope to these suffixed districts rests on ZR 11-25 (suffix inheritance), not on an express provision naming them; the program records this as an owner-decision limitation.
- The sloping-plane setback geometry above the 25 ft wall is not computed.
- A commercial overlay, special district, historic district or large site is not adjusted by the program; when one is present the result is sent for professional review instead of a changed number.

## How the program reads it

The program reports the same 25 ft wall and 35 ft ridge anchor heights as the bare R1/R2 pitched rule, applying them to the suffixed districts through the ZR 11-25 suffix-inheritance provision, and marks the result for professional review.

## Example

A made-up detached house on an R2A lot (not a real address).

- Inputs: zoning_district = R2A; building_type = detached
- Expected answer: max_perimeter_wall_height = 25; max_building_height = 35
- Basis of the expected answer (law_text): ZR 23-421 caps (perimeter wall 25 ft, ridge 35 ft above the base plane), reached for the suffixed R2A district through ZR 11-25: 'All regulations applicable to a district designation shall be applicable to such district designation appended with a suffix, except as otherwise set forth in express provisions.'
- Who prepared the expected answer: worked by an AI agent from the captured text; not checked by a professional
- Answer the program gives: max_perimeter_wall_height = 25; max_building_height = 35
- Result label the program attaches: professional_review_required
- Do they agree? yes - the program's answer matches the expected answer

## Code

- `services/api/app/rules/rulesets/r1_r2_suffix_variants_pitched_height.rule.json`
- `services/api/app/rules/evaluator.py`
- `services/api/app/rules/registry.py`

## Tests

- `services/api/tests/rules/test_r1_r2_height_setback.py`

## What the program does today and a test checks

- Reports the same 25-foot wall / 35-foot ridge envelope for R1-1, R1-2, R1-2A, R2A and R2X, reached through the ZR 11-25 suffix reading (test: test_as1_suffix_variant_confident_wall_and_ridge_separate).
- Cites 11-25 as owner-decision provenance in addition to 23-421, which the bare rule does not (test: test_as1_bare_and_suffix_rules_cite_distinct_provenance).
- Records R2X's distinct 23-21 FAR row as a floor-area-only note that does not change the height, and omits that note for other variants (test: test_as1_r2x_far_row_documented_as_floor_area_only).
- Is not applicable to bare or foreign districts (test: test_nc1_suffix_variant_rule_never_matches_bare_or_foreign).
- Fails closed to professional review on a missing building form, and escalates on an overlay, special district, historic district, large site or transportation (test: test_nc4_suffix_variant_building_type_unavailable_fails_closed, test_nc3_suffix_variant_rule_modifier_downgrades).

## In the program but no test checks it

- (none recorded)

## Planned, not built

- The sloping-plane setback geometry is not computed.
- Overlay, special-district, historic-district, large-site and transportation adjustments are not computed.

## Automated test result

- Status: Passed
- Commit tested: `52e3d8a461cf08577273c82f802b85433f6f1ec3`
- Date tested: 2026-10-06
- Command: `python -m pytest -q tests/rules/test_r1_r2_height_setback.py`
- Counts: 110 passed
- Evidence: [run log](../evidence/r1-r2-suffix-variants-pitched-height.txt)
- Rule file digest tested: `f4f840be26eb17a78b0b935d24df2a5367c495d9f9990a916db5a6418ee43dd3`
- Test files tested:
  - `services/api/tests/rules/test_r1_r2_height_setback.py` (`30e10fe9dd52e85b79c63ee5d811f6d24df42beef3fe341f46ae75ebe1cfd10d`)
- These deterministic tests ran in the build and all passed; the status is the recorded result at the commit shown, bound to the rule-file and test-file digests. If the rule file or any linked test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Gaps

- Reading the pitched envelope onto the suffixed districts is an owner decision via ZR 11-25, not an express provision; a reviewer should confirm it.
- The sloping-plane geometry above 25 feet is not computed; the result is marked for professional review.
- Overlays, special districts, historic districts, large sites and transportation-infrastructure increases send the result for professional review.
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

