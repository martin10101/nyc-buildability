# Lot coverage by portion: corner-lot portion 100% plus interior strip 80% (benchmark lot)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading, worked by an AI agent. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice (ADR-007).

- Calculation id: `calc-lot-coverage-by-portion`
- Entry kind: calculation (a combined/arithmetic calculation; no rule file)
- Family: lot_coverage
- Applies from: 2024-12-05 (to: no end date)
- Revision: 2 (last changed 2026-10-09)
- Combines rule entries: `r6b-lot-coverage`

## Code identity

An entry with no rule file is fingerprinted by the LF-normalized sha256 of its code module(s). If a module changes and the entry is not revised, the check fails - as a changed rule file is caught for a rule entry.

- Combined code identity: `d13b7093ca2aeab414e54c073b060262f97a4be2749adc8ff47d931eec86214b`
- Modules:
  - `services/api/app/scenario/three_answers/result_ways.py` (`58788c78183f2c33a59bbae40b98fe27533b5eaa79e30f1fc2a2a94580eebd5c`)
  - `services/api/app/scenario/three_answers/geometry.py` (`c44b2490469b4b1f9760d540bf0a13d2c847767672379d4a1275b1755d778589`)
  - `services/api/app/spatial/corner_reach_area.py` (`bf6435aeb90b989465be940fbf65d9620c52675347d0b50685812cd0e0aebbcd`)
  - `services/api/app/scenario/three_answers/lot_coverage_by_portion.py` (`8b603fbe53263ba1c70575331ce42287f7acb2dfa73de6aa00f71860d81d9c83`)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Digest (sha256) |
|---|---|---|---|---|---|
| 23-362 | [23-362](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362) | 2024-12-05 | 2026-09-30T07:29:06Z | `zr-23-362` | `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9` |

## Where it applies

The by-portion lot coverage a corner lot takes when part of it lies beyond 100 ft of a street line: the corner-lot portion at 100% (ZR 23-362) plus the remaining interior-lot strip at 80%. The benchmark lot reaches 103.93 ft from the 215 Place line, so no single whole-lot figure applies and the engine withholds max_lot_coverage.

## Exceptions and limits

- r6b-lot-coverage covers only the flat 80% interior rule; the corner 100% by-portion split is now built as pure modules (corner_reach_area.py, lot_coverage_by_portion.py; M5-T145) but is connected to no reported result.
- The corner-lot portion is the part within 100 ft of each intersecting street line (ZR 12-10).

## How the program reads it

The engine withholds max_lot_coverage for the benchmark lot because the lot reaches beyond the corner-lot portion, so there is no single whole-lot coverage figure. Coverage by portion (corner 100% + interior strip 80%) is now built as two pure modules - services/api/app/spatial/corner_reach_area.py measures the corner-lot and interior-lot area split and services/api/app/scenario/three_answers/lot_coverage_by_portion.py applies the corner 100% and interior 80% ratios (ZR 23-362), both added by M5-T145 - but they are connected to no reported result and nothing imports them, so the program's answer is unchanged (max_lot_coverage still withheld).

## Inputs, units, measurement basis, formula and rounding

- Inputs:
  - zoning_district = R6B
  - lot_type = corner
  - within_100_ft_of_street_line_intersection = false (reaches 103.93 ft from 215 Place)
- Units: feet and square feet
- Measurement basis: EPSG:2263 US survey feet for areas measured from the outline; the recorded lot area is the city record (approximate tax map). See the measurement-basis record.
- Formula: footprint allowed = corner-lot portion x 100% + interior strip x 80% (by portion; not built in the program)
- Rounding: none - no rounding rule

## Worked example: independent expected versus the program's actual

The benchmark corner lot, lot coverage by portion.

- Inputs: zoning_district = R6B; lot_type = corner; within_100_ft_of_street_line_intersection = no
- Expected answer (independent): none
- Basis of the expected answer (reference_case): step-p6-worked#real-lot-coverage-by-portion: not known as a single whole-lot figure. Corner-lot portion (100%): reading 13 = 9,997.60 sq ft, reading 14 = 9,997.46 sq ft. Interior strip (80%): reading 13 = 390.39 sq ft (allowing 312.31), reading 14 = 390.52 sq ft (allowing 312.42). Footprint allowed about 10,310 sq ft (reading 13 10,309.91, reading 14 10,309.88). The readings differ in the decimals, so both are held; real-lot#L5 keeps the whole-lot figure not known.
- Independent record(s) cited: step-p6-worked#real-lot-coverage-by-portion, real-lot#L5
- Who prepared the expected answer: worked independently by sealed-folder AI agents (step P6: two readers) and the earlier reference cases; not checked by a professional
- Program's actual answer: none
- Standing of the program's answer: withheld
- Do they agree? not determined - a side is withheld/not built, or the two readings differ

## What the program does today versus what is planned

Implemented and tested:
- The document withholds max_lot_coverage with the by-portion reason (test: test_document_actuals_match_the_recorded_fixture).

In the program but no test checks it:
- (none recorded)

Planned, not built:
- The by-portion coverage modules exist (corner_reach_area.py, lot_coverage_by_portion.py; M5-T145) but are connected to no reported result; the wiring that would feed them a measured outline and the two street lines and report a footprint is not built.
- No footprint is drawn because the coverage is withheld.

## Automated test result

- Status: Passed
- Code identity tested: `d13b7093ca2aeab414e54c073b060262f97a4be2749adc8ff47d931eec86214b`
- Commit tested: `2e6dde3ee15a1d3ff742701c5637bc2f3e1ff0ae`
- Date tested: 2026-10-09
- Command: `python -m pytest -q -p no:cacheprovider rules/test_zoning_rule_review_register_calculations.py`
- Counts: 42 passed
- Evidence: [run log](../evidence/calc-lot-coverage-by-portion.txt)
- Test files tested:
  - `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` (`eb029a9a077f4eabcb9a795153603cdea55c749a6e0906707eb61253c5a9d5e2`)
- These deterministic tests ran in the build and all passed, bound to the code identity and the test-file digest shown. If a code module or the test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Linked records (linked, not copied)

- docs/measurement-basis/MEASUREMENT_BASIS.md (the measurement basis; linked, not copied)
- services/api/app/rules/coverage/COVERAGE_MATRIX.md (the rule-coverage matrix; linked)
- docs/reference-cases/R6B/cases/step-p6-worked.json (coverage by portion, independent)
- docs/reference-cases/R6B/cases/real-lot.json (real-lot#L5, independent)

## Code and tests

- `services/api/app/scenario/three_answers/result_ways.py`
- `services/api/app/scenario/three_answers/geometry.py`
- `services/api/app/spatial/corner_reach_area.py`
- `services/api/app/scenario/three_answers/lot_coverage_by_portion.py`
- `services/api/tests/rules/test_zoning_rule_review_register_calculations.py`

## Legal requirements and chosen design assumptions

| Figure or step | Kind | Quoted captured text (legal) | Capture |
|---|---|---|---|
| Interior/through lots 80%, corner lots 100% (ZR 23-362) | LEGAL_REQUIREMENT | the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent. | `zr-23-362` |
| The corner-lot portion is within 100 ft of each intersecting street line (ZR 12-10) | LEGAL_REQUIREMENT | A "corner lot" is either a #zoning lot# bounded entirely by #streets# | `zr-12-10-lot-corner` |

## Gaps and unresolved questions

- The two step-P6 readings differ in the decimals of the measured areas, so the expected side holds both figures and no single figure is recorded.
- The whole-lot coverage stays not known (real-lot#L5; corner-reach#real-lot-coverage).

- Coverage gap: Lot coverage by portion for a corner lot (corner 100% + interior strip 80%) is built as pure modules (corner_reach_area.py, lot_coverage_by_portion.py; M5-T145) but is connected to no reported result; r6b-lot-coverage covers only the flat 80% rule and the engine still withholds the whole-lot figure.

## Human review

- Current verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -
- The verdict is derived from the reviewer's recorded decision and whether it still matches the current code identity, law captures and revision. A verdict is a named human reviewer's own answer; agent reviews are never recorded here.

