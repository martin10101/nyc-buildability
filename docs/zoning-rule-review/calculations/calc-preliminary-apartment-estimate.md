# Preliminary apartment estimate: floor area x efficiency share / apartment size (benchmark lot)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading, worked by an AI agent. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice (ADR-007).

- Calculation id: `calc-preliminary-apartment-estimate`
- Entry kind: calculation (a combined/arithmetic calculation; no rule file)
- Family: apartment_estimate
- Applies from: 2024-12-05 (to: no end date)
- Revision: 1 (last changed 2026-10-09)
- Combines rule entries: `r6-r12-residential-far`

## Code identity

An entry with no rule file is fingerprinted by the LF-normalized sha256 of its code module(s). If a module changes and the entry is not revised, the check fails - as a changed rule file is caught for a rule entry.

- Combined code identity: `1274168775754628a8e2d2f19c0033a383beb0bff43c449db02f22be79b561c2`
- Modules:
  - `services/api/app/scenario/three_answers/three_way_document.py` (`7f0ecfed2a410bbe2c1157a23a9791091eefa12e249c178acb00d9910d49fbaf`)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Digest (sha256) |
|---|---|---|---|---|---|
| 23-22 | [23-22](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-22` | `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e` |

## Where it applies

A practical, preliminary estimate of how many apartments might fit: the floor area times a chosen efficiency share, divided by a chosen apartment size. The floor area is the legal maximum (ZR 23-22); the 0.60-0.75 efficiency share and the 700 sq ft apartment size are each a preliminary assumption chosen by the owner, not law. The program does not build this estimate yet (the document reports it not_available, 'not built yet').

## Exceptions and limits

- The apartment size and efficiency share are preliminary assumptions, editable, not legal requirements.
- The estimate is a practical capacity estimate, kept apart from the legal dwelling-unit limit.

## How the program reads it

preliminary apartments = floor area x efficiency share / apartment size. For real building B (20,150 sq ft): at the 0.60 share, 20,150 x 0.60 / 700 = 17.27; at the 0.75 share, 20,150 x 0.75 / 700 = 21.59 (both a preliminary assumption). The program does not build this estimate yet.

## Inputs, units, measurement basis, formula and rounding

- Inputs:
  - floor_area_sq_ft (from the building option)
  - apartment_size_sq_ft = 700 (a preliminary assumption)
  - efficiency_share = 0.60 to 0.75 (a preliminary assumption)
- Units: feet and square feet
- Measurement basis: EPSG:2263 US survey feet for areas measured from the outline; the recorded lot area is the city record (approximate tax map). See the measurement-basis record.
- Formula: preliminary apartments = floor area x efficiency share / 700 (a preliminary assumption; not built)
- Rounding: none to a count in the estimate - the range is shown to two decimals (no rounding rule)

## Worked example: independent expected versus the program's actual

The preliminary apartment estimate for the benchmark lot (design-only; not built).

- Inputs: floor_area_sq_ft = 20150; apartment_size_sq_ft = 700; efficiency_share = 0.60 to 0.75
- Expected answer (independent): none
- Basis of the expected answer (reference_case): step-p6-worked#real-estimate-b: real building B (20,150 sq ft) gives 20,150 x 0.60 / 700 = 17.27 (17-18) and 20,150 x 0.75 / 700 = 21.59 (21-22). real-estimate-a: real building A (about 10,310 sq ft) gives 8.84 (8-9) and 11.05 (11-12). The 0.60-0.75 share and the 700 sq ft apartment size are each a preliminary assumption chosen by the owner.
- Independent record(s) cited: step-p6-worked#real-estimate-a, step-p6-worked#real-estimate-b, step-p6-worked#made-up-estimate-a, step-p6-worked#made-up-estimate-b
- Who prepared the expected answer: worked independently by sealed-folder AI agents (step P6: two readers) and the earlier reference cases; not checked by a professional
- Program's actual answer: none
- Standing of the program's answer: not_built
- What the engine computes (the document withholds it): none
  - The preliminary capacity estimate is not built yet (fixture unit_estimate not_available, reason 'not built yet').
- Do they agree? not determined - a side is withheld/not built, or the two readings differ

## What the program does today versus what is planned

Implemented and tested:
- The document reports the preliminary apartment estimate not_available, 'not built yet' (test: test_document_actuals_match_the_recorded_fixture).

In the program but no test checks it:
- (none recorded)

Planned, not built:
- The preliminary apartment estimate is not built in the program.
- It needs a built building option / floor area to run from.

## Automated test result

- Status: Passed
- Code identity tested: `1274168775754628a8e2d2f19c0033a383beb0bff43c449db02f22be79b561c2`
- Commit tested: `28026c5efbf1ad879b7cb4fbe3f8b36bbd1d153f`
- Date tested: 2026-10-09
- Command: `python -m pytest -q -p no:cacheprovider rules/test_zoning_rule_review_register_calculations.py`
- Counts: 42 passed
- Evidence: [run log](../evidence/calc-preliminary-apartment-estimate.txt)
- Test files tested:
  - `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` (`d29fdf0cc8877fb29d85761e2ac445eef049e70d4439b82fc1a48fc3a92159a0`)
- These deterministic tests ran in the build and all passed, bound to the code identity and the test-file digest shown. If a code module or the test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Linked records (linked, not copied)

- docs/measurement-basis/MEASUREMENT_BASIS.md (the measurement basis; linked, not copied)
- services/api/app/rules/coverage/COVERAGE_MATRIX.md (the rule-coverage matrix; linked)
- docs/reference-cases/R6B/cases/step-p6-worked.json (estimate rows, independent)

## Code and tests

- `services/api/app/scenario/three_answers/three_way_document.py`
- `services/api/tests/rules/test_zoning_rule_review_register_calculations.py`

## Legal requirements and chosen design assumptions

| Figure or step | Kind | Quoted captured text (legal) | Capture |
|---|---|---|---|
| Maximum residential floor area (the dividend) - ZR 23-22 | LEGAL_REQUIREMENT | the maximum #residential# #floor area ratio# shall be as set forth in the following table | `zr-23-22` |
| Apartment size 700 sq ft (a preliminary assumption chosen by the owner) | DESIGN_ASSUMPTION | - | - |
| Efficiency share 0.60 to 0.75 (a preliminary assumption chosen by the owner) | DESIGN_ASSUMPTION | - | - |

## Gaps and unresolved questions

- The preliminary apartment estimate is not built; the measurement-basis record describes the method and is linked here.

- Coverage gap: The preliminary apartment estimate (700 sq ft, 0.60-0.75) is not built; the measurement-basis record describes the method and is now linked from this entry.

## Human review

- Current verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -
- The verdict is derived from the reviewer's recorded decision and whether it still matches the current code identity, law captures and revision. A verdict is a named human reviewer's own answer; agent reviews are never recorded here.

