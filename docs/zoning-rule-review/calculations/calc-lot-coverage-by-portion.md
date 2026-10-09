# Lot coverage by portion: corner-lot portion 100% plus interior strip 80% (benchmark lot)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading, worked by an AI agent. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice (ADR-007).

- Calculation id: `calc-lot-coverage-by-portion`
- Entry kind: calculation (a combined/arithmetic calculation; no rule file)
- Family: lot_coverage
- Applies from: 2024-12-05 (to: no end date)
- Revision: 5 (last changed 2026-10-09)
- Combines rule entries: `r6b-lot-coverage`

## Code identity

An entry with no rule file is fingerprinted by the LF-normalized sha256 of its code module(s). If a module changes and the entry is not revised, the check fails - as a changed rule file is caught for a rule entry.

- Combined code identity: `28e4895b8be3505aa0d66335f6ad711cdec1644e4708f2ad097457f967ba1594`
- Modules:
  - `services/api/app/scenario/three_answers/result_ways.py` (`8cf693a8c05da8349f4ec2277fe31e161211e6979b55f843f2965d20691b490f`)
  - `services/api/app/scenario/three_answers/geometry.py` (`c44b2490469b4b1f9760d540bf0a13d2c847767672379d4a1275b1755d778589`)
  - `services/api/app/spatial/corner_reach_area.py` (`bf6435aeb90b989465be940fbf65d9620c52675347d0b50685812cd0e0aebbcd`)
  - `services/api/app/scenario/three_answers/lot_coverage_by_portion.py` (`8b603fbe53263ba1c70575331ce42287f7acb2dfa73de6aa00f71860d81d9c83`)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Digest (sha256) |
|---|---|---|---|---|---|
| 23-362 | [23-362](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362) | 2024-12-05 | 2026-09-30T07:29:06Z | `zr-23-362` | `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9` |

## Where it applies

The by-portion lot coverage a corner lot takes: the corner-lot portion at 100% (ZR 23-362) plus the remaining interior-lot strip at 80%. Reported through the emitter by how the recorded lot area and the tax-map outline area compare - available with its figures where they agree, withheld where they disagree (the benchmark lot), and withheld (the outline not available) where the lot's tax-map outline is missing.

## Exceptions and limits

- The footprint square-foot figure is shown where the recorded lot area and the tax-map outline area agree; it is withheld where they disagree (the benchmark) and withheld, the outline not available, where the outline is missing (rulings W1, W13).
- The corner-lot portion is the part within 100 ft of each intersecting street line (ZR 12-10).
- The outline's area is a drawing measure and is never used in a zoning calculation in place of the recorded lot area.

## How the program reads it

The program reports lot coverage by portion through the emitter, by how the recorded lot area and the tax-map outline area compare. Where they AGREE (the outline is threaded and the corner split is measured) coverage by portion is available with its figures - the corner and interior portion areas, the two ZR 23-362 ratios (corner 100%, interior 80%), the ZR 12-10 100 ft, and the footprint. Where they DISAGREE (the benchmark lot) the footprint is withheld as a square-foot figure, because the outline's area is a drawing measure, never used in a zoning calculation in its place (ruling W1; gap_kind a missing fact about the property), and the law is given by portion without a figure. Where the lot's tax-map outline is NOT available the coverage is withheld with the reason that the outline is not available (a missing fact about the property), never computed from the recorded area (W13). The by-portion measurement (corner_reach_area.py, lot_coverage_by_portion.py; M5-T145) is wired through first_option_results.py, three_way_document.py and result_way_engine_bridge.py.

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
- On the benchmark lot the document withholds max_lot_coverage as a square-foot figure and gives the law by portion, its gap_kind a missing fact about the property because the recorded and tax-map outline lot areas disagree (test: test_document_actuals_match_the_recorded_fixture).

In the program but no test checks it:
- The agree case (coverage by portion available with its figures) and the outline-not-available case (withheld) are realised through the emitter and proven by the server-side tests (test_three_answers_three_way_emit.py::test_w13_*, test_first_option_results.py::test_s13); no register-side test asserts them.

Planned, not built:
- A live-route test with a lot whose recorded and outline areas agree was not added (no existing helper serves such a lot); the agree case is proven through the emitter.
- No footprint is drawn on the benchmark because the figure is withheld.

## Automated test result

- Status: Passed
- Code identity tested: `28e4895b8be3505aa0d66335f6ad711cdec1644e4708f2ad097457f967ba1594`
- Commit tested: `423aa189fdb8fd7f16aead0dfec3af50e5bcbd66`
- Date tested: 2026-10-09
- Command: `python -m pytest -q -p no:cacheprovider rules/test_zoning_rule_review_register_calculations.py`
- Counts: 53 passed
- Evidence: [run log](../evidence/calc-lot-coverage-by-portion.txt)
- Test files tested:
  - `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` (`2d18e4127768d26950baa29f27937bd6fc07dc1ff6560ba80e049599d31accf0`)
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

- On the benchmark lot the recorded lot area (10,075 sq ft) and the tax-map outline area (10,387.99 sq ft) disagree by about 313 sq ft; the footprint square-foot figure is withheld until a survey or deed reconciles them.
- The two step-P6 readings differ in the decimals of the measured areas, so the expected side holds both figures and no single figure is recorded.

- Coverage gap: Coverage by portion is wired through the emitter: available with its figures where the recorded and tax-map outline lot areas agree, withheld where they disagree (the benchmark), and withheld with the outline-not-available reason where the outline is missing. r6b-lot-coverage covers only the flat 80% interior rule.

## Human review

- Current verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -
- The verdict is derived from the reviewer's recorded decision and whether it still matches the current code identity, law captures and revision. A verdict is a named human reviewer's own answer; agent reviews are never recorded here.

