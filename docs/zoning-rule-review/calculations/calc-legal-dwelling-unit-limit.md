# Legal dwelling-unit limit: maximum floor area / 680, rounding up at .75 (benchmark lot)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading, worked by an AI agent. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice (ADR-007).

- Calculation id: `calc-legal-dwelling-unit-limit`
- Entry kind: calculation (a combined/arithmetic calculation; no rule file)
- Family: dwelling_units
- Applies from: 2024-12-05 (to: no end date)
- Revision: 4 (last changed 2026-10-11)
- Combines rule entries: `r6b-dwelling-units`

## Code identity

An entry with no rule file is fingerprinted by the LF-normalized sha256 of its code module(s). If a module changes and the entry is not revised, the check fails - as a changed rule file is caught for a rule entry.

- Combined code identity: `ec3a1792694fab76797f606be8b777c615100a8c02f578aa191511829d36db43`
- Modules:
  - `services/api/app/scenario/three_answers/dwelling_units.py` (`57abec65ce2e2ad961fefcc995c5c41d62e760dc46111ab6df1f0050e16d2c8a`)
  - `services/api/app/scenario/three_answers/result_ways.py` (`09d0009d2245dd9558d4a678fc675d2a2707b674d7e832818475590d43af9a72`)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Digest (sha256) |
|---|---|---|---|---|---|
| 23-52 | [23-52](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52) | 2024-12-05 | 2026-09-30T07:29:29Z | `zr-23-52` | `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac` |
| 23-52(b) | [23-52(b)](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52) | 2024-12-05 | 2026-09-30T07:29:29Z | `zr-23-52` | `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac` |
| 11-25 | [11-25](https://zr.planning.nyc.gov/entityprint/pdf/node/18433) | 1994-06-29 | 2026-09-13T02:45:00Z | `zr-11-25` | `6843ad22d57d4f59cf422c80b820d1797955c1cecfecf3ee459b68bf139b2b2b` |

## Where it applies

The legal ceiling on dwelling units: the maximum residential floor area divided by the ZR 23-52(b) factor 680, with the fraction counted as one unit only at three-quarters or more. For the benchmark lot the record (Queens community district 411) places it OUTSIDE both special density areas (ZR 12-10 / 23-52(a)(1)), so the engine computes 20,150 / 680 = 29.63 -> 29 and the document shows it as a CONDITIONAL ceiling - never settled - with an always-present condition that the city's record is per tax lot while the limit is set on the zoning lot.

## Exceptions and limits

- In a special density area the dwelling-unit formula does not apply (ZR 23-52(a)(1)). The program reads the special density area from the city's record (ZR 12-10: the Manhattan Core is Manhattan Community Districts 1-8; the Special Downtown Brooklyn District is the letters "DB"); a lot recorded outside both areas shows the limit as a conditional ceiling, a lot recorded inside one withholds it, and a record that cannot be read (or that disagrees with a statement) withholds it.
- Qualifying senior housing has no factor (ZR 23-52(a)(2)); qualifying affordable housing is a separate labelled limit.

## How the program reads it

max dwelling units = maximum residential floor area / 680; a fraction of .75 or more counts as one unit, otherwise it is dropped. The engine computes 20,150 / 680 = 29.63 -> 29 through the r6b-dwelling-units rule, and the document now shows it as a conditional ceiling because the record places the lot outside both special density areas; it stays conditional on the zoning lot (the record is per tax lot).

## Inputs, units, measurement basis, formula and rounding

- Inputs:
  - zoning_district = R6B
  - max_residential_floor_area_sq_ft = 20,150
  - housing_program = standard_residence
  - special_density_area = not known
  - special_district_present = false
- Units: feet and square feet
- Measurement basis: EPSG:2263 US survey feet for areas measured from the outline; the recorded lot area is the city record (approximate tax map). See the measurement-basis record.
- Formula: max dwelling units = 20,150 / 680 = 29.63 -> 29 (fraction below .75 dropped)
- Rounding: a fraction of three-quarters (.75) or more counts as one dwelling unit; otherwise dropped (ZR 23-52(b))

## Worked example: independent expected versus the program's actual

The benchmark lot's legal dwelling-unit ceiling.

- Inputs: zoning_district = R6B; max_residential_floor_area_sq_ft = 20150; housing_program = standard_residence; special_density_area = no; special_district_present = no
- Expected answer (independent): max_dwelling_units = 29
- Basis of the expected answer (reference_case): real-lot#L6 = 29 (20,150 / 680 = 29.63; the fraction below .75 is dropped); step-p6-worked#real-unit-limit restates 29 as the current answer for step 5 of the six-step comparison.
- Independent record(s) cited: real-lot#L6, step-p6-worked#real-unit-limit
- Who prepared the expected answer: worked independently by sealed-folder AI agents (step P6: two readers) and the earlier reference cases; not checked by a professional
- Program's actual answer: max_dwelling_units = 29
- Standing of the program's answer: conditional
- What the engine computes (the document withholds it): dwelling_units_before_rounding = 29.63235294117647; max_dwelling_units = 29
  - The engine computes 29 through the r6b-dwelling-units rule (20,150 / 680 = 29.63 -> 29) and the document now SHOWS it as a conditional ceiling (fixture legal_unit_limit_standard way=conditional) because the record (Queens cd 411) places the lot outside both special density areas (ZR 12-10: step-p3#manhattan-core 'not in the Manhattan Core'; step-p3#special-downtown-brooklyn-district 'outside ... on the recorded facts'). The always-present condition names the zoning lot (the record is per tax lot). The independent reference reads the same 29.
- Do they agree? yes - the program's answer matches the independent expected answer

## What the program does today versus what is planned

Implemented and tested:
- The limit 29 (20,150 / 680 = 29.63 -> 29) is recomputed through the r6b-dwelling-units rule and equals the independent real-lot#L6 and step-p6-worked#real-unit-limit (test: test_calc_unit_limit_engine_computes_29_document_shows_a_conditional_ceiling).
- The document shows legal_unit_limit_standard as a conditional ceiling with the zoning-lot condition (test: test_calc_unit_limit_engine_computes_29_document_shows_a_conditional_ceiling, test_document_actuals_match_the_recorded_fixture).

In the program but no test checks it:
- (none recorded)

Planned, not built:
- How the legal dwelling-unit limit is shown for a lot recorded INSIDE a special density area is not built (the formula does not apply there, ZR 23-52(a)(1)); nor are the conversion, mixed-building and qualifying affordable / senior cases.

## Automated test result

- Status: Passed
- Code identity tested: `ec3a1792694fab76797f606be8b777c615100a8c02f578aa191511829d36db43`
- Commit tested: `d46369705676eee33b1882f637c545cf444c4ae8`
- Date tested: 2026-10-11
- Command: `python -m pytest -q -p no:cacheprovider rules/test_zoning_rule_review_register_calculations.py`
- Counts: 53 passed
- Evidence: [run log](../evidence/calc-legal-dwelling-unit-limit.txt)
- Test files tested:
  - `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` (`a793a9c6ca9b119fbf866c071885d17b3f8b9dc2126f4eeb597af6f518491d7e`)
- These deterministic tests ran in the build and all passed, bound to the code identity and the test-file digest shown. If a code module or the test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Linked records (linked, not copied)

- docs/measurement-basis/MEASUREMENT_BASIS.md (the measurement basis; linked, not copied)
- services/api/app/rules/coverage/COVERAGE_MATRIX.md (the rule-coverage matrix; linked)
- docs/reference-cases/R6B/cases/real-lot.json (real-lot#L6, independent)
- docs/reference-cases/R6B/cases/step-p6-worked.json (real-unit-limit, independent)
- docs/reference-cases/R6B/cases/step-p3-worked.json (special-density status, independent)
- docs/reference-cases/R6B/cases/step-p1-worked.json (special-density-areas-list, independent)

## Code and tests

- `services/api/app/scenario/three_answers/dwelling_units.py`
- `services/api/app/scenario/three_answers/result_ways.py`
- `services/api/tests/rules/test_zoning_rule_review_register_calculations.py`

## Legal requirements and chosen design assumptions

| Figure or step | Kind | Quoted captured text (legal) | Capture |
|---|---|---|---|
| max dwelling units = maximum residential floor area / dwelling-unit factor (ZR 23-52) | LEGAL_REQUIREMENT | the maximum number of #dwelling units# permitted shall be determined by dividing the maximum #residential# #floor area# permitted on the #zoning lot# by the applicable #dwelling unit# factor | `zr-23-52` |
| Special density areas have no dwelling-unit factor, so the formula does not apply there (ZR 23-52(a)(1)) | LEGAL_REQUIREMENT | #developments# or #enlargements# of #residences# in #special density areas# | `zr-23-52` |
| The engine's factor 680 and the .75 rounding come from the r6b-dwelling-units rule parameters, which quote ZR 23-52(b); the factor and rounding are a legal requirement carried by that rule entry, not a design choice | DESIGN_ASSUMPTION | - | - |

## Gaps and unresolved questions

- The limit is shown as a conditional ceiling for a lot recorded outside both special density areas; a lot recorded inside one, a record that cannot be read, a conversion or a mixed building, and the qualifying affordable / senior cases are not shown. PLUTO lists a special purpose district only where it covers at least 10% of the tax lot, so a sliver can read as none; the record is per tax lot while the law asks about the zoning lot (the standing condition).

- Coverage gap: The legal dwelling-unit limit is shown as a conditional ceiling from the recorded special-density area (ZR 12-10) for a lot outside both areas; the inside-one, unreadable-record, conversion, mixed-building and qualifying-housing cases remain, with the zoning-lot vs tax-lot and 10%-sliver caveats carried in the condition.

## Human review

- Current verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -
- The verdict is derived from the reviewer's recorded decision and whether it still matches the current code identity, law captures and revision. A verdict is a named human reviewer's own answer; agent reviews are never recorded here.

