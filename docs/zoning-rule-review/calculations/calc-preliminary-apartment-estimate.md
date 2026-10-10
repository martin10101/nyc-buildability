# Preliminary apartment estimate: floor area x efficiency share / apartment size (benchmark lot)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading, worked by an AI agent. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice (ADR-007).

- Calculation id: `calc-preliminary-apartment-estimate`
- Entry kind: calculation (a combined/arithmetic calculation; no rule file)
- Family: apartment_estimate
- Applies from: 2024-12-05 (to: no end date)
- Revision: 9 (last changed 2026-10-10)
- Combines rule entries: `r6-r12-residential-far`

## Code identity

An entry with no rule file is fingerprinted by the LF-normalized sha256 of its code module(s). If a module changes and the entry is not revised, the check fails - as a changed rule file is caught for a rule entry.

- Combined code identity: `64dc8306dcf1e7dd32135800359257baeeb7f2e758f25d04ff6f08c6ada5d1c1`
- Modules:
  - `services/api/app/scenario/three_answers/three_way_document.py` (`003a7e61b9fb983c9a20ebeb8b492f84165ef473956deb5a612cb52b6e4f62c8`)
  - `services/api/app/scenario/three_answers/preliminary_apartment_estimate.py` (`a0ea51bdfec9b0ad537617ab4e33e63967a8a2c701935a308e0ad899c840bdb1`)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Digest (sha256) |
|---|---|---|---|---|---|
| 23-22 | [23-22](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-22` | `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e` |

## Where it applies

A practical, preliminary estimate of how many apartments might fit: the floor area times a chosen efficiency share, divided by a chosen apartment size. The floor area is the legal maximum (ZR 23-22); the 0.60-0.75 efficiency share and the 700 sq ft apartment size are each a preliminary assumption chosen by the owner, not law. The estimate is reported for each worked building in building_alternatives: building B where a building is worked (17.27 to 21.59 on the benchmark), building A where the two lot areas agree. Where no building is worked, no estimate is given and the single unit_estimate block points to the lists.

## Exceptions and limits

- The apartment size and efficiency share are preliminary assumptions, editable; they are shown with the values used but are not yet changeable on the screen (backlog row DB-213 a).
- The estimate is a practical capacity estimate, kept apart from the legal dwelling-unit limit.
- The single unit_estimate block is not shown; each worked building's estimate is given in building_alternatives - building B on every path, building A where the two lot areas agree.

## How the program reads it

preliminary apartments = floor area x efficiency share / apartment size. For building B (20,150 sq ft): at the 0.60 share, 20,150 x 0.60 / 700 = 17.27; at the 0.75 share, 20,150 x 0.75 / 700 = 21.59 (two decimals), labelled 'Preliminary capacity estimate', conditional on the recorded lot area. Building B's estimate is reported wherever building B is listed (a building is worked); building A's estimate is given where the two lot areas agree. Where no building can be worked (for example at 16 ft or 25 ft), no estimate is given and the single unit_estimate block points to building_alternatives and buildings_not_worked. The 0.60-0.75 share and the 700 sq ft size are each a preliminary assumption, shown with the values used but not yet changeable on the screen (DB-213 a). The arithmetic is built in preliminary_apartment_estimate.py (M5-T145) and reported per worked building through three_way_document.py; the single unit_estimate block is not shown and points to the lists.

## Inputs, units, measurement basis, formula and rounding

- Inputs:
  - floor_area_sq_ft (from the building option)
  - apartment_size_sq_ft = 700 (a preliminary assumption)
  - efficiency_share = 0.60 to 0.75 (a preliminary assumption)
- Units: feet and square feet
- Measurement basis: EPSG:2263 US survey feet for areas measured from the outline; the recorded lot area is the city record (approximate tax map). See the measurement-basis record.
- Formula: preliminary apartments = floor area x efficiency share / 700 (a preliminary assumption; built as a pure module, M5-T145, connected to no reported result)
- Rounding: none to a count in the estimate - the range is shown to two decimals (no rounding rule)

## Worked example: independent expected versus the program's actual

The preliminary apartment estimate for the benchmark lot: reported for building B (17.27 to 21.59, conditional); building A's estimate is not given because building A needs the withheld footprint figure.

- Inputs: floor_area_sq_ft = 20150; apartment_size_sq_ft = 700; efficiency_share = 0.60 to 0.75
- Expected answer (independent): none
- Basis of the expected answer (reference_case): step-p6-worked#real-estimate-b: real building B (20,150 sq ft) gives 20,150 x 0.60 / 700 = 17.27 (17-18) and 20,150 x 0.75 / 700 = 21.59 (21-22). real-estimate-a: real building A (about 10,310 sq ft) gives 8.84 (8-9) and 11.05 (11-12). The 0.60-0.75 share and the 700 sq ft apartment size are each a preliminary assumption chosen by the owner.
- Independent record(s) cited: step-p6-worked#real-estimate-a, step-p6-worked#real-estimate-b, step-p6-worked#made-up-estimate-a, step-p6-worked#made-up-estimate-b
- Who prepared the expected answer: worked independently by sealed-folder AI agents (step P6: two readers) and the earlier reference cases; not checked by a professional
- Program's actual answer: quotient_low = 17.27; quotient_high = 21.59
- Standing of the program's answer: available_conditional
- Do they agree? not determined - a side is withheld/not built, or the two readings differ

## What the program does today versus what is planned

Implemented and tested:
- The document gives building B's preliminary capacity estimate in building_alternatives (17.27 to 21.59, labelled 'Preliminary capacity estimate') and the single unit_estimate block points there (test: test_document_actuals_match_the_recorded_fixture).

In the program but no test checks it:
- (none recorded)

Planned, not built:
- The share and size are shown with the values used but not yet changeable on the screen (DB-213 a).
- Building A's estimate is given only where the two lot areas agree; on the benchmark they disagree, so it is not given.

## Automated test result

- Status: Not run
- Code identity tested: `9b1a85a7dc90864bad1b4f796d69e55502d8c8370088995d190b23db98c38be2`
- Commit tested: `42fc2ae11e6b90084972e7ca32816cc50b8a085a`
- Date tested: 2026-10-10
- Command: `python -m pytest -q -p no:cacheprovider rules/test_zoning_rule_review_register_calculations.py`
- Counts: 53 passed
- Evidence: [run log](../evidence/calc-preliminary-apartment-estimate.txt)
- Test files tested:
  - `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` (`2d18e4127768d26950baa29f27937bd6fc07dc1ff6560ba80e049599d31accf0`)
- These deterministic tests ran in the build and all passed, bound to the code identity and the test-file digest shown. If a code module or the test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Linked records (linked, not copied)

- docs/measurement-basis/MEASUREMENT_BASIS.md (the measurement basis; linked, not copied)
- services/api/app/rules/coverage/COVERAGE_MATRIX.md (the rule-coverage matrix; linked)
- docs/reference-cases/R6B/cases/step-p6-worked.json (estimate rows, independent)

## Code and tests

- `services/api/app/scenario/three_answers/three_way_document.py`
- `services/api/app/scenario/three_answers/preliminary_apartment_estimate.py`
- `services/api/tests/rules/test_zoning_rule_review_register_calculations.py`

## Legal requirements and chosen design assumptions

| Figure or step | Kind | Quoted captured text (legal) | Capture |
|---|---|---|---|
| Maximum residential floor area (the dividend) - ZR 23-22 | LEGAL_REQUIREMENT | the maximum #residential# #floor area ratio# shall be as set forth in the following table | `zr-23-22` |
| Apartment size 700 sq ft (a preliminary assumption chosen by the owner) | DESIGN_ASSUMPTION | - | - |
| Efficiency share 0.60 to 0.75 (a preliminary assumption chosen by the owner) | DESIGN_ASSUMPTION | - | - |

## Gaps and unresolved questions

- Building A's preliminary estimate is given only where the two lot areas agree; on the benchmark they disagree, so it is not given.
- The share and apartment size are shown but not yet changeable on the screen (DB-213 a); the measurement-basis record describes the method and is linked here.

- Coverage gap: The preliminary apartment estimate is reported for building B where a building is worked (17.27 to 21.59 on the benchmark, conditional); building A's estimate is given where the two lot areas agree; where no building is worked, no estimate is given; the share and size are shown but not yet changeable on the screen (DB-213 a).

## Human review

- Current verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -
- The verdict is derived from the reviewer's recorded decision and whether it still matches the current code identity, law captures and revision. A verdict is a named human reviewer's own answer; agent reviews are never recorded here.

