# Building-option floor stack: footprint, each floor's area and height, total floor area (benchmark lot)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading, worked by an AI agent. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice (ADR-007).

- Calculation id: `calc-building-option-floor-stack`
- Entry kind: calculation (a combined/arithmetic calculation; no rule file)
- Family: building_option
- Applies from: 2024-12-05 (to: no end date)
- Revision: 3 (last changed 2026-10-09)
- Combines rule entries: `r6-r12-residential-far`, `r6b-height`

## Code identity

An entry with no rule file is fingerprinted by the LF-normalized sha256 of its code module(s). If a module changes and the entry is not revised, the check fails - as a changed rule file is caught for a rule entry.

- Combined code identity: `157835f933103f36ca3ead00f99d3c77e98706f980ab87eb4840650051d3936f`
- Modules:
  - `services/api/app/scenario/three_answers/building_option.py` (`57ce8a88deede0edb505a63188082fd27dadc37b6eda5ac0de051619465789b1`)
  - `services/api/app/scenario/three_answers/result_ways.py` (`58788c78183f2c33a59bbae40b98fe27533b5eaa79e30f1fc2a2a94580eebd5c`)
  - `services/api/app/scenario/three_answers/first_building_options.py` (`f286eaf3c0f4b4aa726e3eb3922340645e6971bb45cf3ea0143999d4ca394e62`)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Digest (sha256) |
|---|---|---|---|---|---|
| 23-22 | [23-22](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-22` | `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e` |
| 23-432 | [23-432](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432) | 2024-12-05 | 2026-09-30T06:49:08Z | `zr-23-432` | `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c` |

## Where it applies

The building-option floor stack: a footprint stacked floor by floor to a total floor area and a building height. The engine's compute_building_option method stacks one uniform widest plate (lot area x lot coverage) to the height limit and caps at the floor-area allowance, with a partial top floor. For the benchmark lot the single building_option block is not shown; building B is reported as a worked alternative in building_alternatives (3 storeys of 6,716.67 sq ft at 30 ft, conditional), and building A is not listed because it needs the withheld footprint figure.

## Exceptions and limits

- Building B is reported in building_alternatives (conditional on the recorded lot area); building A is not listed because it needs the footprint square-foot figure, which is withheld where the two lot areas disagree.
- The single building_option block is not shown; it points to the worked alternatives in building_alternatives.
- The engine's own compute_building_option method (one uniform widest plate to a partial top floor) differs from the independent example's two buildings (DB-210); building B is built by first_building_options.py (the fewest storeys reaching the minimum base height), which matches the independent building B.

## How the program reads it

The document reports building B as a worked alternative in building_alternatives: 3 storeys of 6,716.67 sq ft to the 30 ft minimum base height, using the whole 20,150 sq ft floor-area allowance, conditional on the recorded lot area of 10,075 sq ft. Building B is built by first_building_options.py (the fewest storeys reaching the minimum base height; M5-T145), which matches the independent example's building B. Building A (the widest footprint in whole storeys) is not listed because it needs the footprint square-foot figure, which is withheld where the recorded and tax-map outline lot areas disagree. The single building_option block is not shown and points to the list. The engine's own compute_building_option method (one uniform widest plate to a partial top floor) is a different method (DB-210) and is set beside the independent two buildings in the worked example below; the module works one floor-to-floor height for every storey (the owner's 10 ft starting assumption, R542), so a 15 ft shop ground floor is not worked.

## Inputs, units, measurement basis, formula and rounding

- Inputs:
  - allowance_sf (maximum residential floor area)
  - plate_sf (lot area x lot coverage)
  - max_building_height_ft (R6B 55 ft)
  - floor_to_floor_ft = 10 (a chosen design assumption)
  - made-up demonstration: allowance 20,000; plate 8,000 (10,000 x 80%); height 55; f2f 10
- Units: feet and square feet
- Measurement basis: EPSG:2263 US survey feet for areas measured from the outline; the recorded lot area is the city record (approximate tax map). See the measurement-basis record.
- Formula: floors that fit = floor(height limit / floor-to-floor); floors built = ceil(allowance / plate) capped at the floors that fit; building height = floors built x floor-to-floor (engine method; a uniform widest plate, partial top floor)
- Rounding: floor division for the floors that fit and ceiling for the floors to reach the allowance; the top floor may be partial (engine's exact-fraction arithmetic)

## Worked example: independent expected versus the program's actual

The first building option's floor stack: the engine's method on the made-up interior lot beside the independent example; the benchmark program side is withheld.

- Inputs: allowance_sf = 20000; plate_sf = 8000; max_building_height_ft = 55; floor_to_floor_ft = 10
- Expected answer (independent): none
- Basis of the expected answer (reference_case): step-p6-worked: made-up building A = 2 storeys of 8,000 = 16,000 sq ft, 20 ft, 4,000 sq ft unused; made-up building B = 3 storeys of 6,666.67 = 20,000 sq ft, 30 ft. Real building A = 1 storey about 10,310 sq ft, 10 ft (below the 30 ft minimum base); real building B = 3 storeys of 6,716.67 = 20,150 sq ft, 30 ft. The independent method offers two buildings; the engine does not.
- Independent record(s) cited: step-p6-worked#made-up-footprint-a, step-p6-worked#made-up-building-a, step-p6-worked#made-up-building-b, step-p6-worked#real-building-a, step-p6-worked#real-building-b
- Who prepared the expected answer: worked independently by sealed-folder AI agents (step P6: two readers) and the earlier reference cases; not checked by a professional
- Program's actual answer: none
- Standing of the program's answer: not_available
- What the engine computes (the document withholds it): engine_floors_built = 3; engine_achieved_sf = 20000; engine_building_height_ft = 30; engine_top_floor_sf = 4000
  - On the made-up interior lot (allowance 20,000; plate 8,000; height 55 ft; f2f 10) the engine's compute_building_option returns 3 floors (8,000 + 8,000 + 4,000) = 20,000 sq ft at 30 ft - one uniform widest plate with a partial top floor. For the benchmark lot the document withholds the building option (coverage withheld). The independent example instead offers two buildings; this is a difference of method (DB-210).
- Do they agree? not determined - a side is withheld/not built, or the two readings differ

## What the program does today versus what is planned

Implemented and tested:
- On the made-up interior lot (allowance 20,000; plate 8,000 = 10,000 x 80%; height limit 55 ft; 10 ft floor-to-floor) the engine's compute_building_option returns 3 floors (8,000 + 8,000 + 4,000) = 20,000 sq ft at 30 ft, which differs from the independent two buildings (test: test_engine_sample_stack_differs_from_independent_two_buildings).
- The single building_option block is not shown in the document (test: test_document_actuals_match_the_recorded_fixture).

In the program but no test checks it:
- The regenerated document lists building B in building_alternatives (3 storeys of 6,716.67 sq ft at 30 ft, conditional); no register test asserts the list's floor schedule (the server content tests do).

Planned, not built:
- Building A is not worked because the footprint square-foot figure is withheld where the two lot areas disagree.
- The engine's own single-answer building-option generator (compute_building_option) is not reported; it is set beside the independent example only in the worked example below.
- One floor-to-floor height is worked for every storey (R542 10 ft), so a 15 ft shop ground floor is not worked.
- Which building the first option shows is the owner's pending decision (DB-210).

## Automated test result

- Status: Passed
- Code identity tested: `157835f933103f36ca3ead00f99d3c77e98706f980ab87eb4840650051d3936f`
- Commit tested: `455caec46895298a772505cdf34325d7fd758d96`
- Date tested: 2026-10-09
- Command: `python -m pytest -q -p no:cacheprovider rules/test_zoning_rule_review_register_calculations.py`
- Counts: 53 passed
- Evidence: [run log](../evidence/calc-building-option-floor-stack.txt)
- Test files tested:
  - `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` (`2d18e4127768d26950baa29f27937bd6fc07dc1ff6560ba80e049599d31accf0`)
- These deterministic tests ran in the build and all passed, bound to the code identity and the test-file digest shown. If a code module or the test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Linked records (linked, not copied)

- docs/measurement-basis/MEASUREMENT_BASIS.md (the measurement basis; linked, not copied)
- services/api/app/rules/coverage/COVERAGE_MATRIX.md (the rule-coverage matrix; linked)
- docs/reference-cases/R6B/cases/step-p6-worked.json (building A/B, independent)
- docs/DISCOVERY_BACKLOG.md (DB-210, the method difference and the owner's pending decision)

## Code and tests

- `services/api/app/scenario/three_answers/building_option.py`
- `services/api/app/scenario/three_answers/result_ways.py`
- `services/api/app/scenario/three_answers/first_building_options.py`
- `services/api/tests/rules/test_zoning_rule_review_register_calculations.py`

## Legal requirements and chosen design assumptions

| Figure or step | Kind | Quoted captured text (legal) | Capture |
|---|---|---|---|
| R6B heights: minimum base 30 ft, maximum base 45 ft, maximum building 55 ft (ZR 23-432) | LEGAL_REQUIREMENT | the minimum base height, maximum base height, and maximum #building# height shall be as set forth in the following table | `zr-23-432` |
| Setback above the maximum base height (ZR 23-432) | LEGAL_REQUIREMENT | For portions of a #building# #street wall# that exceed the maximum base height, a setback shall be provided | `zr-23-432` |
| Floor area ratio 2.00 / maximum floor area as the stack's cap (ZR 23-22) | LEGAL_REQUIREMENT | the maximum #residential# #floor area ratio# shall be as set forth in the following table | `zr-23-22` |
| 10-ft floor-to-floor height (a chosen design assumption, the owner's starting value) | DESIGN_ASSUMPTION | - | - |
| Same-plan uniform-plate stack, and which building the first option shows: a chosen design assumption, not law (DB-210; the owner's pending decision) | DESIGN_ASSUMPTION | - | - |

## Gaps and unresolved questions

- The engine's own compute_building_option method (one uniform widest plate to a partial top floor) differs from building B's method (the fewest storeys reaching the minimum base height); recorded as a design assumption that differs (DB-210).
- Building A is not listed because the footprint square-foot figure is withheld (the recorded and tax-map outline lot areas disagree).
- The two step-P6 readings differ in the decimals of the real lot's footprint; both figures are held, no single figure.

- Coverage gap: Building B is reported as a worked alternative (conditional); building A needs the withheld footprint figure and is not listed; the single building_option block is not shown; the engine's own single-answer generator is not built, and its method differs from building B's (DB-210).

## Human review

- Current verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -
- The verdict is derived from the reviewer's recorded decision and whether it still matches the current code identity, law captures and revision. A verdict is a named human reviewer's own answer; agent reviews are never recorded here.

