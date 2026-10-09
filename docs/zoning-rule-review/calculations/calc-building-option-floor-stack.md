# Building-option floor stack: footprint, each floor's area and height, total floor area (benchmark lot)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading, worked by an AI agent. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice (ADR-007).

- Calculation id: `calc-building-option-floor-stack`
- Entry kind: calculation (a combined/arithmetic calculation; no rule file)
- Family: building_option
- Applies from: 2024-12-05 (to: no end date)
- Revision: 2 (last changed 2026-10-09)
- Combines rule entries: `r6-r12-residential-far`, `r6b-height`

## Code identity

An entry with no rule file is fingerprinted by the LF-normalized sha256 of its code module(s). If a module changes and the entry is not revised, the check fails - as a changed rule file is caught for a rule entry.

- Combined code identity: `b76885b3b64f02bb9994acfdaab2c73a704e83311f2af13e582e496f3ee039b2`
- Modules:
  - `services/api/app/scenario/three_answers/building_option.py` (`57ce8a88deede0edb505a63188082fd27dadc37b6eda5ac0de051619465789b1`)
  - `services/api/app/scenario/three_answers/result_ways.py` (`58788c78183f2c33a59bbae40b98fe27533b5eaa79e30f1fc2a2a94580eebd5c`)
  - `services/api/app/scenario/three_answers/first_building_options.py` (`26a92c402f816da31c90937e1850cd77f8dcf76afe9823812b40c59bc755330a`)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Digest (sha256) |
|---|---|---|---|---|---|
| 23-22 | [23-22](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-22` | `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e` |
| 23-432 | [23-432](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432) | 2024-12-05 | 2026-09-30T06:49:08Z | `zr-23-432` | `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c` |

## Where it applies

The building-option floor stack: a footprint stacked floor by floor to a total floor area and a building height. The engine's method (compute_building_option) stacks one uniform widest plate (lot area x lot coverage) to the height limit and caps at the floor-area allowance, with a partial top floor. For the benchmark lot the document withholds the building option (coverage withheld, the sample building is below the minimum base height, and no reference case had been run).

## Exceptions and limits

- The engine needs the lot coverage, which is withheld for the benchmark lot, so no footprint is produced.
- The building option is withheld unconditionally this milestone (result_ways._building_option_withheld).
- The method differs from the independent example's two buildings (DB-210); those two buildings are now built as a pure module (first_building_options.py, M5-T145) connected to no reported result.

## How the program reads it

The engine stacks one uniform widest plate to the height limit, capping at the floor-area allowance with a partial top floor. The independent example instead works two buildings: the widest footprint in whole storeys to the floor-area maximum (building A) and the fewest storeys reaching the 30 ft minimum base height (building B); these two buildings are now built as a pure module (services/api/app/scenario/three_answers/first_building_options.py, M5-T145), but it is connected to no reported result and nothing imports it. This is a difference of method (DB-210); the engine's result on the benchmark lot is withheld because coverage is withheld, so the program's answer is unchanged. The module works one floor-to-floor height for every storey (the owner's 10 ft starting assumption, R542), so a 15 ft shop ground floor is not worked.

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
- The document withholds the building option (test: test_document_actuals_match_the_recorded_fixture).

In the program but no test checks it:
- (none recorded)

Planned, not built:
- The engine's own building-option generator and floor schedule are not built for the benchmark lot; the two step-P6 buildings exist as a pure module (first_building_options.py, M5-T145) but are connected to no reported result, and the wiring that would feed them a footprint and report a building is not built.
- One floor-to-floor height is worked for every storey (R542 10 ft), so a 15 ft shop ground floor is not worked.
- Which building the first option shows is the owner's pending decision (DB-210).

## Automated test result

- Status: Passed
- Code identity tested: `b76885b3b64f02bb9994acfdaab2c73a704e83311f2af13e582e496f3ee039b2`
- Commit tested: `2e6dde3ee15a1d3ff742701c5637bc2f3e1ff0ae`
- Date tested: 2026-10-09
- Command: `python -m pytest -q -p no:cacheprovider rules/test_zoning_rule_review_register_calculations.py`
- Counts: 42 passed
- Evidence: [run log](../evidence/calc-building-option-floor-stack.txt)
- Test files tested:
  - `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` (`eb029a9a077f4eabcb9a795153603cdea55c749a6e0906707eb61253c5a9d5e2`)
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

- The engine's method (one uniform widest plate to a partial top floor) differs from the independent example's two buildings; recorded as a design assumption that differs (DB-210).
- The two step-P6 readings differ in the decimals of the real lot's footprint; both figures are held, no single figure.

- Coverage gap: The building-option / floor-stack calculation is withheld in the program and uncompared; the two step-P6 buildings are built as a pure module (first_building_options.py, M5-T145) but connected to no reported result, and the engine's own generator is not built.

## Human review

- Current verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -
- The verdict is derived from the reviewer's recorded decision and whether it still matches the current code identity, law captures and revision. A verdict is a named human reviewer's own answer; agent reviews are never recorded here.

