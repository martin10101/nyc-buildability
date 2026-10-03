# NYC Buildability rule-coverage matrix (every R district x output x add-on)

GENERATED FILE — do not edit by hand. Produced by `render_coverage_matrix.py` from `coverage_matrix.json`; edit the JSON and re-render.

- Plan: docs/PRODUCT_PLAN_CURRENT_2026-09-28.md M1-03, §5, §6, §12a
- Queue: docs/lanes/queues/A.md A-01
- Directives: D-090
- Lane: A

> Nothing here is reviewed. Every cited rule is status needs_review; the highest status any cell carries is implemented_draft (D-090-R010). No rule math is asserted.

## District list source

Every R district row is the union of the two current-ZR residential FAR tables, which by the Zoning Resolution's own structure enumerate every R district: ZR 23-21 (R1-R5) and ZR 23-22 (R6-R12). No district is listed from memory.

| ZR section | Section title | Table caption | Covers | Districts | Content digest (sha256) |
|---|---|---|---|---:|---|
| 23-21 | Floor Area Regulations for R1 Through R5 Districts | MAXIMUM FLOOR AREA RATIO FOR R1-R5 DISTRICTS | R1 through R5 | 18 | `b52771e629b6afa9f9a6843a657dbfd143294f721cd757f953792e747a48ad8a` |
| 23-22 | Floor Area Regulations for R6 Through R12 Districts | MAXIMUM FLOOR AREA RATIO FOR R6-R12 DISTRICTS | R6 through R12 | 27 | `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e` |
| | | | **total** | **45** | |

- The R1-R5 and R6-R12 FAR tables are disjoint, so every district maps to exactly one source section.
- Height rule r1-r2-bare-pitched-height lists bare 'R1' in its applicability as a family shorthand; the enumerated R1 districts are R1-1, R1-2 and R1-2A per ZR 23-21. Matrix rows follow the FAR-table enumeration, not rule-applicability shorthands.
- Includes City of Yes lettered/contextual districts and the R6-R12 un-suffixed / A / B / D / X variants exactly as the captured tables list them (plan §12a).

## Legend

### Status

| Code | Status | Meaning |
|---|---|---|
| `ID` | implemented_draft | A needs_review rule (or a surfaced conditional alternative in a needs_review rule) exists in the repo for this district x column. Never reviewed. |
| `—` | not_implemented | No rule/exception in the repo covers it and no captured source establishes non-applicability. Default for unknowns. |
| `NA` | not_applicable | A captured source or an explicit product decision establishes the provision does not apply / never yields a computed number. Used only with a cited basis. |
| `NR` | needs_reviewer | Classification requires a qualified reviewer's legal reading; recorded with the reason in notes. |

### Output columns

| Code | Output |
|---|---|
| `FAR` | far |
| `HGT` | heights |
| `SBK` | setbacks |
| `YRD` | yards |
| `COV` | coverage |
| `UNI` | units |

### Add-on columns (plan §6)

| Code | Add-on | Group | Type |
|---|---|---|---|
| `AO1` | Wide-street portion | A | Automatic |
| `AO2` | Corner-lot coverage | A | Automatic |
| `AO3` | Split-district averaging | A | Automatic where the rule applies |
| `AO4` | Zoning floor-area exclusions and permitted obstructions | A | Automatic where the rule applies |
| `AO5` | Qualifying affordable or senior housing (City of Yes) | A | Optional |
| `AO6` | Community facility floor area | A | Optional |
| `AO7` | Choice of bulk rules (Quality Housing vs height factor) | A | Optional |
| `AO8` | Ground-floor commercial space | A | Optional |
| `AO9` | Transfers the rules allow by certification | B | Optional |
| `AO10` | A neighbor's unused floor area | C | Optional; never in Best combination |
| `AO11` | City Planning special permits and authorizations (text maximum) | D1 | Optional; never in Best combination |
| `AO12` | Variances and rezonings | D2 | Opportunity note only |

### Street-width source

| Value | Meaning |
|---|---|
| `dcm_mapped_width` | The rule reads the DCM mapped street width (the mapped width zoning uses). When the width is unknown the engine returns both wide- and narrow-street results (plan §4; D-052). |
| `unknown_then_both_results` | The documented unknown-handling of a dcm_mapped_width rule: when the width is unresolved, both wide- and narrow-street results are shown side by side (plan §4). |
| `not_needed` | The rule does not depend on street width. |
| `null` | No rule exists for the cell, so there is no rule-level street-width source to declare. |

## Summary

| Column | ID | — | NA | NR |
|---|---:|---:|---:|---:|
| `FAR` | 45 | 0 | 0 | 0 |
| `HGT` | 19 | 26 | 0 | 0 |
| `SBK` | 1 | 44 | 0 | 0 |
| `YRD` | 1 | 44 | 0 | 0 |
| `COV` | 1 | 44 | 0 | 0 |
| `UNI` | 1 | 44 | 0 | 0 |
| `AO1` | 4 | 41 | 0 | 0 |
| `AO2` | 1 | 44 | 0 | 0 |
| `AO3` | 0 | 45 | 0 | 0 |
| `AO4` | 0 | 45 | 0 | 0 |
| `AO5` | 45 | 0 | 0 | 0 |
| `AO6` | 0 | 45 | 0 | 0 |
| `AO7` | 0 | 44 | 0 | 1 |
| `AO8` | 0 | 45 | 0 | 0 |
| `AO9` | 0 | 45 | 0 | 0 |
| `AO10` | 0 | 45 | 0 | 0 |
| `AO11` | 0 | 45 | 0 | 0 |
| `AO12` | 0 | 0 | 45 | 0 |
| **total** | **118** | **646** | **45** | **1** |

## Coverage grid (district x column)

| District | FAR | HGT | SBK | YRD | COV | UNI | AO1 | AO2 | AO3 | AO4 | AO5 | AO6 | AO7 | AO8 | AO9 | AO10 | AO11 | AO12 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| R1-2A | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R1-1 | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R1-2 | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R2A | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R2 | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R3A | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R3X | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R3-1 | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R3-2 | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R2X | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R4A | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R4B | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R4 | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R4-1 | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R5A | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R5B | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R5 | ID | ID | ID | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R5D | ID | ID | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R6A | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R6 | ID | — | — | — | — | — | ID | — | — | — | ID | — | — | — | — | — | — | NA |
| R6-1 | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R7B | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R6B | ID | ID | — | ID | ID | ID | — | ID | — | — | ID | — | NR | — | — | — | — | NA |
| R6D | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R6-2 | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R7A | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R7-1 | ID | — | — | — | — | — | ID | — | — | — | ID | — | — | — | — | — | — | NA |
| R7-2 | ID | — | — | — | — | — | ID | — | — | — | ID | — | — | — | — | — | — | NA |
| R7D | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R7X | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R7-3 | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R8A | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R8X | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R8 | ID | — | — | — | — | — | ID | — | — | — | ID | — | — | — | — | — | — | NA |
| R8B | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R9A | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R9 | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R9D | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R9X | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R9-1 | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R10A | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R10X | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R10 | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R11 | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |
| R12 | ID | — | — | — | — | — | — | — | — | — | ID | — | — | — | — | — | — | NA |

## Implemented (draft) cells

Every rule below is status `needs_review`; `implemented_draft` is the ceiling (D-090-R010).

| District | Column | Rule ids | Tests | ZR sections | Street-width source |
|---|---|---|---|---|---|
| R1-2A | `FAR` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R1-2A | `HGT` | `r1-r2-qrs-height`, `r1-r2-suffix-variants-pitched-height` | services/api/tests/rules/test_r1_r2_height_setback.py | 23-424, 23-423, 11-25, 23-421, 23-21 | `not_needed` |
| R1-2A | `AO5` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R1-1 | `FAR` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R1-1 | `HGT` | `r1-r2-qrs-height`, `r1-r2-reference-plane-23421g`, `r1-r2-suffix-variants-pitched-height` | services/api/tests/rules/test_r1_r2_height_setback.py | 23-424, 23-423, 23-421(g), 11-25, 23-421, 23-21 | `not_needed` |
| R1-1 | `AO5` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R1-2 | `FAR` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R1-2 | `HGT` | `r1-r2-qrs-height`, `r1-r2-reference-plane-23421g`, `r1-r2-suffix-variants-pitched-height` | services/api/tests/rules/test_r1_r2_height_setback.py | 23-424, 23-423, 23-421(g), 11-25, 23-421, 23-21 | `not_needed` |
| R1-2 | `AO5` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R2A | `FAR` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R2A | `HGT` | `r1-r2-qrs-height`, `r1-r2-suffix-variants-pitched-height` | services/api/tests/rules/test_r1_r2_height_setback.py | 23-424, 23-423, 11-25, 23-421, 23-21 | `not_needed` |
| R2A | `AO5` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R2 | `FAR` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R2 | `HGT` | `r1-r2-bare-pitched-height`, `r1-r2-qrs-height`, `r1-r2-reference-plane-23421g` | services/api/tests/rules/test_r1_r2_height_setback.py | 23-421, 23-424, 23-423, 23-421(g) | `not_needed` |
| R2 | `AO5` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R3A | `FAR` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R3A | `HGT` | `r3-r4-pitched-height` | services/api/tests/rules/test_r3_r4_height.py | 23-421, 23-42 | `not_needed` |
| R3A | `AO5` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R3X | `FAR` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R3X | `HGT` | `r3-r4-pitched-height` | services/api/tests/rules/test_r3_r4_height.py | 23-421, 23-42 | `not_needed` |
| R3X | `AO5` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R3-1 | `FAR` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R3-1 | `HGT` | `r3-r4-pitched-height` | services/api/tests/rules/test_r3_r4_height.py | 23-421, 23-42 | `not_needed` |
| R3-1 | `AO5` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R3-2 | `FAR` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R3-2 | `HGT` | `r3-2-r4-flat-height`, `r3-r4-pitched-height` | services/api/tests/rules/test_r3_r4_height.py | 23-422, 23-42, 23-421 | `not_needed` |
| R3-2 | `AO5` | `r1-r2-r3-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R2X | `FAR` | `r2x-r4-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R2X | `HGT` | `r1-r2-qrs-height`, `r1-r2-suffix-variants-pitched-height` | services/api/tests/rules/test_r1_r2_height_setback.py | 23-424, 23-423, 11-25, 23-421, 23-21 | `not_needed` |
| R2X | `AO5` | `r2x-r4-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R4A | `FAR` | `r2x-r4-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R4A | `HGT` | `r3-r4-pitched-height` | services/api/tests/rules/test_r3_r4_height.py | 23-421, 23-42 | `not_needed` |
| R4A | `AO5` | `r2x-r4-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R4B | `FAR` | `r2x-r4-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R4B | `HGT` | `r4b-height` | services/api/tests/rules/test_r3_r4_height.py | 23-422 | `not_needed` |
| R4B | `AO5` | `r2x-r4-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R4 | `FAR` | `r2x-r4-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R4 | `HGT` | `r3-2-r4-flat-height`, `r3-r4-pitched-height` | services/api/tests/rules/test_r3_r4_height.py | 23-422, 23-42, 23-421 | `not_needed` |
| R4 | `AO5` | `r2x-r4-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R4-1 | `FAR` | `r2x-r4-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R4-1 | `HGT` | `r3-r4-pitched-height` | services/api/tests/rules/test_r3_r4_height.py | 23-421, 23-42 | `not_needed` |
| R4-1 | `AO5` | `r2x-r4-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-21 | `not_needed` |
| R5A | `FAR` | `r5-residential-far` | services/api/tests/rules/test_rules_engine.py | 23-21 | `not_needed` |
| R5A | `HGT` | `r5-qrs-height`, `r5a-height` | services/api/tests/rules/test_r5_height_setback.py | 23-424, 23-423, 23-421 | `not_needed` |
| R5A | `AO5` | `r5-residential-far` | services/api/tests/rules/test_rules_engine.py | 23-21 | `not_needed` |
| R5B | `FAR` | `r5-residential-far` | services/api/tests/rules/test_rules_engine.py | 23-21 | `not_needed` |
| R5B | `HGT` | `r5-qrs-height`, `r5b-height` | services/api/tests/rules/test_r5_height_setback.py | 23-424, 23-423, 23-422 | `not_needed` |
| R5B | `AO5` | `r5-residential-far` | services/api/tests/rules/test_rules_engine.py | 23-21 | `not_needed` |
| R5 | `FAR` | `r5-residential-far` | services/api/tests/rules/test_rules_engine.py | 23-21 | `not_needed` |
| R5 | `HGT` | `r5-height`, `r5-qrs-height` | services/api/tests/rules/test_r5_height_setback.py | 23-422, 23-424, 23-423 | `not_needed` |
| R5 | `SBK` | `r5-setback` | services/api/tests/rules/test_r5_height_setback.py | 23-423, 12-10, 23-422 | `dcm_mapped_width` |
| R5 | `AO5` | `r5-residential-far` | services/api/tests/rules/test_rules_engine.py | 23-21 | `not_needed` |
| R5D | `FAR` | `r5-residential-far` | services/api/tests/rules/test_rules_engine.py | 23-21 | `not_needed` |
| R5D | `HGT` | `r5-qrs-height`, `r5d-height` | services/api/tests/rules/test_r5_height_setback.py | 23-424, 23-423, 23-422 | `not_needed` |
| R5D | `AO5` | `r5-residential-far` | services/api/tests/rules/test_rules_engine.py | 23-21 | `not_needed` |
| R6A | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R6A | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R6 | `FAR` | `r6-r7-r8-wide-street-conditional-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `dcm_mapped_width` |
| R6 | `AO1` | `r6-r7-r8-wide-street-conditional-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `dcm_mapped_width` |
| R6 | `AO5` | `r6-r7-r8-wide-street-conditional-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `dcm_mapped_width` |
| R6-1 | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R6-1 | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R7B | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R7B | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R6B | `FAR` | `r6-r12-residential-far`, `r6b-qualifying-housing-far` | services/api/tests/rules/test_r1_r12_residential_far.py<br>services/api/tests/rules/test_r6b_far_heights.py | 23-22 | `not_needed` |
| R6B | `HGT` | `r6b-height` | services/api/tests/rules/test_r6b_far_heights.py | 23-432 | `not_needed` |
| R6B | `YRD` | `r6b-rear-yard-corner-waiver` | services/api/tests/rules/test_r6b_coverage_yard_units.py | 23-344(a), 11-25 | `not_needed` |
| R6B | `COV` | `r6b-lot-coverage` | services/api/tests/rules/test_r6b_coverage_yard_units.py | 23-362, 11-25 | `not_needed` |
| R6B | `UNI` | `r6b-dwelling-units` | services/api/tests/rules/test_r6b_coverage_yard_units.py | 23-52, 23-52(b), 11-25 | `not_needed` |
| R6B | `AO2` | `r6b-lot-coverage`, `r6b-rear-yard-corner-waiver` | services/api/tests/rules/test_r6b_coverage_yard_units.py | 23-362, 11-25, 23-344(a) | `not_needed` |
| R6B | `AO5` | `r6b-qualifying-housing-far` | services/api/tests/rules/test_r6b_far_heights.py | 23-22 | `not_needed` |
| R6D | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R6D | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R6-2 | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R6-2 | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R7A | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R7A | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R7-1 | `FAR` | `r6-r7-r8-wide-street-conditional-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `dcm_mapped_width` |
| R7-1 | `AO1` | `r6-r7-r8-wide-street-conditional-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `dcm_mapped_width` |
| R7-1 | `AO5` | `r6-r7-r8-wide-street-conditional-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `dcm_mapped_width` |
| R7-2 | `FAR` | `r6-r7-r8-wide-street-conditional-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `dcm_mapped_width` |
| R7-2 | `AO1` | `r6-r7-r8-wide-street-conditional-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `dcm_mapped_width` |
| R7-2 | `AO5` | `r6-r7-r8-wide-street-conditional-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `dcm_mapped_width` |
| R7D | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R7D | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R7X | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R7X | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R7-3 | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R7-3 | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R8A | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R8A | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R8X | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R8X | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R8 | `FAR` | `r6-r7-r8-wide-street-conditional-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `dcm_mapped_width` |
| R8 | `AO1` | `r6-r7-r8-wide-street-conditional-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `dcm_mapped_width` |
| R8 | `AO5` | `r6-r7-r8-wide-street-conditional-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `dcm_mapped_width` |
| R8B | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R8B | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R9A | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R9A | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R9 | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R9 | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R9D | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R9D | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R9X | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R9X | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R9-1 | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R9-1 | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R10A | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R10A | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R10X | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R10X | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R10 | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R10 | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R11 | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R11 | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R12 | `FAR` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |
| R12 | `AO5` | `r6-r12-residential-far` | services/api/tests/rules/test_r1_r12_residential_far.py | 23-22 | `not_needed` |

## Needs-reviewer cells

| District | Column | Reason |
|---|---|---|
| R6B | `AO7` | R6B is a contextual (Quality Housing) district; r6b-height emits one contextual height family with a qualifying-housing alternative. Whether a 'Quality Housing vs height factor' choice applies to R6B (contextual districts typically mandate Quality Housing) is a qualified-reviewer legal determination (queue A-11). No choice mechanism implemented. |

## Not-applicable cells

45 cell(s) across column(s) `AO12`. See each cell's `notes` in `coverage_matrix.json` for the cited basis.

