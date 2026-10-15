# Illustrative area allocation: residential floor area split into apartment and other area at one stated share (benchmark lot)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading, worked by an AI agent. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice (ADR-007).

- Calculation id: `calc-area-allocation`
- Entry kind: calculation (a combined/arithmetic calculation; no rule file)
- Family: area_allocation
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-15)
- Combines rule entries: `r6-r12-residential-far`

## Code identity

An entry with no rule file is fingerprinted by the LF-normalized sha256 of its code module(s). If a module changes and the entry is not revised, the check fails - as a changed rule file is caught for a rule entry.

- Combined code identity: `e6ceb2b7bab7f979058a42aaa3700029d6260d28ee28950dc2fb104c0c44d0fc`
- Modules:
  - `services/api/app/scenario/three_answers/area_allocation.py` (`c644ec2f243fb95c0e1ca7ced643546039dab21988104e4e63e8f62176c768a4`)
  - `services/api/app/scenario/three_answers/three_way_document.py` (`e880d078ba06e5836fa9ba069cec324178ad73486722cce9627ed03fb9f10e51`)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Digest (sha256) |
|---|---|---|---|---|---|
| 23-22 | [23-22](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-22` | `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e` |

## Where it applies

An illustrative split of a worked building's residential floor area into apartment area and other (core, circulation, walls, services) area at one stated share. The floor area is the legal maximum (ZR 23-22); the 0.60 apartment-area share is a preliminary assumption chosen by the owner (the low end of a 0.60-0.75 range), not law. It is reported for every building alternative that has a floor area, placed or not; its fitted flag follows whether the building is placed.

## Exceptions and limits

- The share is a preliminary assumption, editable; apartment area plus other area equals the total, and the per-storey figures sum to the plate.
- Nothing here is a count of apartments, a room, a core, a wall or a stair position, and nothing is called complies, buildable, optimal or feasible.
- The allocation's other-area total happens to share a numeral with the coverage lower bound (8,060); they are different quantities on different bases and are never summed or equated.

## How the program reads it

apartment area = residential floor area x share; other area = total - apartment. For Building B (20,150 sq ft) at the one stated 0.60 share (a preliminary assumption): apartment 20,150 x 0.60 = 12,090.00 sq ft (4,030.00 per storey), other 20,150 - 12,090 = 8,060.00 sq ft (2,686.67 per storey), total 20,150.00; apartment plus other equals the total and the per-storey figures sum to the plate 6,716.67. The split is built in area_allocation.py and emitted on every alternative through three_way_document.py; its fitted flag is true only when that building's placement is placed (the way-layer rule in results_way_rules.py enforces the same thing).

## Inputs, units, measurement basis, formula and rounding

- Inputs:
  - residential_floor_area_sqft = 20150 (the worked building's floor area)
  - apartment-area share = 0.60 (a preliminary assumption; the low end of 0.60-0.75)
- Units: square feet
- Measurement basis: The residential floor area is the zoning floor area (the estimate's own measure); no physical floor plate (gross-up, exclusions or wall thickness) is worked. See the measurement-basis record.
- Formula: apartment area = residential floor area x 0.60 (a preliminary assumption); other area = total - apartment
- Rounding: round half up to two decimals; apartment + other = total within the display rounding

## Worked example: independent expected versus the program's actual

The illustrative area allocation of the three-storey Building B on the benchmark lot at the one stated 0.60 apartment-area share.

- Inputs: residential_floor_area_sqft = 20150; share = 0.6
- Expected answer (independent): apartment_area_sqft = 12090.00; other_area_sqft = 8060.00; total_sqft = 20150.00
- Basis of the expected answer (reference_case): placement-building-b.json#area-allocation: at the one stated 0.60 apartment-area share, apartment 12,090.00 sq ft (4,030.00 per storey) and other 8,060.00 sq ft (2,686.67 per storey); apartment plus other equals the total 20,150.00 and the per-storey figures sum to the plate 6,716.67. Both step-P8 readings agree. The 0.60 share is a preliminary assumption chosen by the owner.
- Independent record(s) cited: placement-building-b#area-allocation
- Who prepared the expected answer: worked independently by two sealed-folder AI agents (step P8); not checked by a professional
- Program's actual answer: apartment_area_sqft = 12090; other_area_sqft = 8060; total_sqft = 20150
- Standing of the program's answer: available
- Do they agree? yes - the program's answer matches the independent expected answer

## What the program does today versus what is planned

Implemented and tested:
- The document splits every alternative's residential floor area at the one stated share: building_alternatives[0].area_allocation carries apartment 12,090.00, other 8,060.00, total 20,150.00, fitted true, with the fixed conversion statement (test: test_document_actuals_match_the_recorded_fixture).

In the program but no test checks it:
- (none recorded)

Planned, not built:
- The share is shown with the value used but not yet changeable on the screen.

## Automated test result

- Status: Not run
- Code identity tested: ``
- Commit tested: ``
- Date tested: 
- Command: `python -m pytest -q -p no:cacheprovider rules/test_zoning_rule_review_register_calculations.py`
- Counts: 
- Evidence: [run log](../evidence/calc-area-allocation.txt)
- Test files tested:
  - `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` (``)
- This entry is new in M5-T172; its code identity is area_allocation.py and the emitter. The deterministic register tests run in CI; the result is recorded as 'Not run' until a run is bound to this code identity and the test-file digest. A passing result is a code check, not a human or professional review.

## Linked records (linked, not copied)

- docs/measurement-basis/MEASUREMENT_BASIS.md (the measurement basis; linked, not copied)
- docs/reference-cases/R6B/cases/placement-building-b.json (the worked allocation, step P8)

## Code and tests

- `services/api/app/scenario/three_answers/area_allocation.py`
- `services/api/app/scenario/three_answers/three_way_document.py`
- `services/api/tests/rules/test_zoning_rule_review_register_calculations.py`

## Legal requirements and chosen design assumptions

| Figure or step | Kind | Quoted captured text (legal) | Capture |
|---|---|---|---|
| Residential floor area, the total split (the legal maximum, ZR 23-22) | LEGAL_REQUIREMENT | the maximum #residential# #floor area ratio# shall be as set forth in the following table | `zr-23-22` |
| Apartment-area share 0.60 (a preliminary assumption chosen by the owner) | DESIGN_ASSUMPTION | - | - |
| The split is the apartment/other area, not a count of apartments, rooms or walls (a design illustration) | DESIGN_ASSUMPTION | - | - |

## Gaps and unresolved questions

- The share is shown with the value used but not yet changeable on the screen.
- The allocation is an illustration at one stated assumption; it establishes no dwelling-unit count, no net or rentable area, no physical floor plate and no layout.

- Coverage gap: The area allocation is reported for every alternative with a floor area at the one stated 0.60 share (a preliminary assumption); its fitted flag follows the placement; the share is shown but not yet changeable on the screen.

## Human review

- Current verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -
- The verdict is derived from the reviewer's recorded decision and whether it still matches the current code identity, law captures and revision. A verdict is a named human reviewer's own answer; agent reviews are never recorded here.

