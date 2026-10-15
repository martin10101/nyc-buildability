# The first building option's complete calculation: the independent example beside the program, six steps

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading, worked by an AI agent. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice (ADR-007).

- Calculation id: `calc-first-building-option-complete`
- Entry kind: calculation_comparison (a combined/arithmetic calculation; no rule file)
- Family: building_option
- Applies from: 2024-12-05 (to: no end date)
- Revision: 16 (last changed 2026-10-15)
- Combines rule entries: `r6-r12-residential-far`, `r6b-lot-coverage`, `r6b-height`, `r6b-dwelling-units`

## Code identity

An entry with no rule file is fingerprinted by the LF-normalized sha256 of its code module(s). If a module changes and the entry is not revised, the check fails - as a changed rule file is caught for a rule entry.

- Combined code identity: `9eef66b41be720bc8a19aaed2d94be70813c553c0ebbeca0554222c1dba8444f`
- Modules:
  - `services/api/app/scenario/three_answers/result_ways.py` (`ac0747a37bb4c462483041cd8f4b0fffce6ff450af492ff61aee5ca76e7b2af3`)
  - `services/api/app/scenario/three_answers/three_way_document.py` (`3376f7b819ab58d298ff228eaa94f331056f0a024d5e4407d11375e8b4a36b2c`)
  - `services/api/app/spatial/corner_reach_area.py` (`bf6435aeb90b989465be940fbf65d9620c52675347d0b50685812cd0e0aebbcd`)
  - `services/api/app/scenario/three_answers/lot_coverage_by_portion.py` (`8b603fbe53263ba1c70575331ce42287f7acb2dfa73de6aa00f71860d81d9c83`)
  - `services/api/app/scenario/three_answers/first_building_options.py` (`f286eaf3c0f4b4aa726e3eb3922340645e6971bb45cf3ea0143999d4ca394e62`)
  - `services/api/app/scenario/three_answers/preliminary_apartment_estimate.py` (`a0ea51bdfec9b0ad537617ab4e33e63967a8a2c701935a308e0ad899c840bdb1`)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Digest (sha256) |
|---|---|---|---|---|---|
| 23-22 | [23-22](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22) | 2024-12-05 | 2026-09-11T00:00:00Z | `zr-23-22` | `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e` |
| 23-362 | [23-362](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362) | 2024-12-05 | 2026-09-30T07:29:06Z | `zr-23-362` | `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9` |
| 23-432 | [23-432](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432) | 2024-12-05 | 2026-09-30T06:49:08Z | `zr-23-432` | `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c` |
| 23-52 | [23-52](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52) | 2024-12-05 | 2026-09-30T07:29:29Z | `zr-23-52` | `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac` |

## Where it applies

The whole first-building-option calculation for the benchmark lot, set step by step beside an independently worked example: property inputs, footprint, each floor's area and height, total floor area, the applicable legal unit limit (a separate step), and the separate preliminary apartment estimate. Each step links its component calculation entry; the page ends in every disagreement and missing fact.

## Exceptions and limits

- Building B's floor schedule and preliminary estimate are now reported in building_alternatives; building A, the footprint and the single building_option block are withheld or not shown. The component calculation modules (corner_reach_area.py, lot_coverage_by_portion.py, first_building_options.py, preliminary_apartment_estimate.py; M5-T145) are wired through first_option_results.py and three_way_document.py.
- The engine's own compute_building_option method differs from building B's (DB-210).

## How the program reads it

The independent example (step P6, two sealed-folder readers) is set beside the program's actual output step by step. The property inputs agree; building B's floor schedule (3 storeys of 6,716.67 sq ft at 30 ft), total floor area (20,150 sq ft) and preliminary capacity estimate (17.27 to 21.59) are now reported in building_alternatives and match the independent building B, conditional on the recorded lot area. The footprint square-foot figure is withheld because the recorded and tax-map outline lot areas disagree, so building A (which needs the footprint) is not listed - that side of the comparison is missing. The legal unit limit is still withheld (the engine computes 29 internally). The engine's own single-answer building method differs from building B's (DB-210). The document also names, in buildings_not_worked, each building of the method not listed with its plain reason; on the benchmark that is building A (its footprint withheld because the two lot areas disagree). Nothing is called feasible; nothing is resolved here.

## Inputs, units, measurement basis, formula and rounding

- Units: feet and square feet
- Measurement basis: EPSG:2263 US survey feet for areas measured from the outline; the recorded lot area is the city record (approximate tax map). See the measurement-basis record.

## The complete calculation, step by step

| Step | What | Independent expected | Program actual (standing) | Verdict |
|---|---|---|---|---|
| 1 | Property inputs | R6B; overlay C2-2; corner lot; recorded lot area 10,075 sq ft vs tax-map outline 10,387.99 sq ft (both shown, neither chosen); 10-ft floor-to-floor (a preliminary assumption) (real-lot#L9, real-lot#L10, step-p6-worked#real-lot-recorded-vs-measured-area) | R6B; overlay C2-2 present; corner; recorded 10,075 vs outline 10,387.99 (shown as a condition, neither chosen); 10-ft floor-to-floor default [settled] | agree |
| 2 | Footprint / lot coverage by portion | no single whole-lot figure: corner portion about 9,997.5 sq ft at 100% plus interior strip about 390 sq ft at 80%, footprint about 10,310 sq ft (the two readings differ in the decimals) (step-p6-worked#real-lot-coverage-by-portion) | withheld - no footprint square-foot figure: the recorded lot area (10,075 sq ft) and the tax-map outline area (10,387.99 sq ft) disagree; the law is given by portion (corner 100% within 100 ft, interior 80%) [withheld] | a side is missing |
| 3 | Each floor's area and height | real building A: 1 storey about 10,310 sq ft at 10 ft (below the 30 ft minimum base); real building B: 3 storeys of 6,716.67 sq ft at 30 ft (step-p6-worked#real-building-a, step-p6-worked#real-building-b) | building B: 3 storeys of 6,716.67 sq ft at 30 ft (conditional on the recorded lot area), matching the independent building B; building A is named in buildings_not_worked (its footprint is withheld because the two lot areas disagree), not worked [available_conditional] | a side is missing |
| 4 | Total floor area | real building B total 20,150 sq ft (the whole allowance used); made-up building B total 20,000 sq ft (step-p6-worked#real-building-b) | building B total 20,150 sq ft (the whole allowance used), conditional on the recorded lot area [available_conditional] | agree |
| 5 | Applicable legal unit limit | 29 dwelling units (20,150 / 680 = 29.63 -> 29) (real-lot#L6, step-p6-worked#real-unit-limit) | 29 dwelling units, shown as a conditional ceiling - the record places the lot outside both special density areas (ZR 12-10), so 20,150 / 680 = 29.63 -> 29 is shown conditional on the zoning lot [conditional] | agree |
| 6 | Separate preliminary apartment estimate | real building B: 20,150 x 0.60 / 700 = 17.27 (17-18) and x 0.75 / 700 = 21.59 (21-22); the 0.60-0.75 share and 700 sq ft size are each a preliminary assumption (step-p6-worked#real-estimate-b) | building B: 20,150 x 0.60 / 700 = 17.27 and x 0.75 / 700 = 21.59, labelled 'Preliminary capacity estimate', conditional; the 0.60-0.75 share and 700 sq ft size are each a preliminary assumption, shown but not yet changeable (DB-213 a) [available_conditional] | agree |

### Step 1: Property inputs

- Component: `calc-floor-area-allowance`
- Independent expected answer: R6B; overlay C2-2; corner lot; recorded lot area 10,075 sq ft vs tax-map outline 10,387.99 sq ft (both shown, neither chosen); 10-ft floor-to-floor (a preliminary assumption)
- Program's actual answer and standing: R6B; overlay C2-2 present; corner; recorded 10,075 vs outline 10,387.99 (shown as a condition, neither chosen); 10-ft floor-to-floor default (settled; source: fixture scope/answers (recorded results document))
- Verdict: agree
- Both readings use the recorded 10,075 for the floor area and measure the outline at 10,387.99 - the same inputs the program uses.

### Step 2: Footprint / lot coverage by portion

- Component: `calc-lot-coverage-by-portion`
- Independent expected answer: no single whole-lot figure: corner portion about 9,997.5 sq ft at 100% plus interior strip about 390 sq ft at 80%, footprint about 10,310 sq ft (the two readings differ in the decimals)
- Program's actual answer and standing: withheld - no footprint square-foot figure: the recorded lot area (10,075 sq ft) and the tax-map outline area (10,387.99 sq ft) disagree; the law is given by portion (corner 100% within 100 ft, interior 80%) (withheld; source: fixture permitted_envelope.max_lot_coverage)
- Verdict: side_missing
- The program withholds the footprint as a square-foot figure because the two lot areas disagree (a missing fact about the property); the independent example works the by-portion footprint (about 10,310 sq ft).

### Step 3: Each floor's area and height

- Component: `calc-building-option-floor-stack`
- Independent expected answer: real building A: 1 storey about 10,310 sq ft at 10 ft (below the 30 ft minimum base); real building B: 3 storeys of 6,716.67 sq ft at 30 ft
- Program's actual answer and standing: building B: 3 storeys of 6,716.67 sq ft at 30 ft (conditional on the recorded lot area), matching the independent building B; building A is named in buildings_not_worked (its footprint is withheld because the two lot areas disagree), not worked (available_conditional; source: fixture building_alternatives[0] (building B); building A in buildings_not_worked; building_option points to both lists)
- Verdict: side_missing
- The program now gives building B's floor schedule, matching the independent building B; building A, which the independent example also works, is named in buildings_not_worked with its areas-disagree reason (no figure) but is not worked, so that side of the comparison is still missing. No verdict moves.

### Step 4: Total floor area

- Component: `calc-building-option-floor-stack`
- Independent expected answer: real building B total 20,150 sq ft (the whole allowance used); made-up building B total 20,000 sq ft
- Program's actual answer and standing: building B total 20,150 sq ft (the whole allowance used), conditional on the recorded lot area (available_conditional; source: fixture building_alternatives[0].total_floor_area_sqft)
- Verdict: agree
- The program's building B uses the whole 20,150 sq ft floor-area maximum, matching the independent building B's total; the standing is conditional on the recorded lot area.

### Step 5: Applicable legal unit limit

- Component: `calc-legal-dwelling-unit-limit`
- Independent expected answer: 29 dwelling units (20,150 / 680 = 29.63 -> 29)
- Program's actual answer and standing: 29 dwelling units, shown as a conditional ceiling - the record places the lot outside both special density areas (ZR 12-10), so 20,150 / 680 = 29.63 -> 29 is shown conditional on the zoning lot (conditional; source: fixture legal_unit_limit_standard; engine r6b-dwelling-units rule)
- Verdict: agree
- The engine's arithmetic (29) matches the independent 29, and the document now shows it as a conditional ceiling because the record places the lot outside both special density areas (ZR 12-10); the standing condition names the zoning lot (the record is per tax lot).

### Step 6: Separate preliminary apartment estimate

- Component: `calc-preliminary-apartment-estimate`
- Independent expected answer: real building B: 20,150 x 0.60 / 700 = 17.27 (17-18) and x 0.75 / 700 = 21.59 (21-22); the 0.60-0.75 share and 700 sq ft size are each a preliminary assumption
- Program's actual answer and standing: building B: 20,150 x 0.60 / 700 = 17.27 and x 0.75 / 700 = 21.59, labelled 'Preliminary capacity estimate', conditional; the 0.60-0.75 share and 700 sq ft size are each a preliminary assumption, shown but not yet changeable (DB-213 a) (available_conditional; source: fixture building_alternatives[0].capacity_estimate)
- Verdict: agree
- The program now gives building B's preliminary capacity estimate, matching the independent example; it is kept separate from the legal unit limit, conditional, with the share and size preliminary assumptions shown but not yet changeable (DB-213 a).

## Every disagreement and missing fact (and what would settle it)

Disagreements:
- [a design assumption that differs] The engine's own single-answer building method (compute_building_option: one uniform widest plate to a partial top floor; on the made-up lot 3 floors of 8,000/8,000/4,000 = 20,000 sq ft at 30 ft) differs from building B's method (first_building_options: the fewest storeys reaching the 30 ft minimum base height, 3 storeys of 6,716.67 sq ft). Which building the first option shows is the owner's pending decision. Backlog row DB-210. Not resolved here. - would be settled by: The building-option generator's design and the owner's choice on which building to show (DB-210 point b).
- [a missing fact about the property] (program result(s): max_lot_coverage) The recorded lot area 10,075 sq ft and the tax-map outline area 10,387.99 sq ft disagree (about 313 sq ft). The footprint is not shown as a square-foot figure because the outline's area is a drawing measure, never used in a zoning calculation in its place; the law is given by portion. Because the footprint is withheld, building A (the widest footprint) is not worked and is named in buildings_not_worked with the areas-disagree reason (no figure). (max_lot_coverage gap_kind missing_information.) - would be settled by: A survey or deed dimensions reconciling the recorded lot area with the tax-map outline; DB-210 point a.
- [a missing fact about the property] The two independent readings differ in the decimals of the real lot's footprint (corner 9,997.60 vs 9,997.46; strip 390.39 vs 390.52; total 10,309.91 vs 10,309.88); both figures are held, no single figure. - would be settled by: A surveyed outline.

Missing facts:
- [code not built] (program result(s): building_option, floor_stack, unit_estimate) The single-answer building option, floor stack and unit estimate are not shown as single results (reason_kind rule_not_implemented); each worked building's floor schedule and preliminary estimate are given in building_alternatives, where building B is listed (3 storeys of 6,716.67 sq ft, 20,150 sq ft, 30 ft, conditional) with its estimate (17.27 to 21.59). The engine's own single-answer generator is not built. - would be settled by: Building the single-answer generators, or the owner's choice to report the list (DB-210 point b).
- [a missing fact about the property] (program result(s): rear_yard) The rear yard beyond the corner, the adjoining lot-line types, the neighbouring street walls and the ground elevations are not known (step-p6#real-lot-missing-facts); the program's rear_yard gap_kind is missing_information. - would be settled by: A survey, a deed, or a record of the neighbouring lots and buildings.

## What the program does today versus what is planned

Implemented and tested:
- The page shows six steps in order and ends with the disagreements and missing facts, naming DB-210 (test: test_six_step_page_has_six_steps_and_closing_names_db210).

In the program but no test checks it:
- The regenerated document reports building B (floor schedule, total and estimate) in building_alternatives; the six-step actual sides are read from that document (the server content tests assert the document).

Planned, not built:
- Building A and the footprint square-foot figure wait on a survey or deed reconciling the recorded and tax-map outline lot areas; the legal unit limit waits on the special-density display; the owner's choice on which building to show is pending (DB-210).

## Automated test result

- Status: Not run
- Code identity tested: `61b79b2dcc2446fcdc38ba374b4fd74644d9d1dd151f9dd8355068d28a37c1a4`
- Commit tested: `10e5c55d1a02f6f18a5c6a2bdc16f01b05751312`
- Date tested: 2026-10-11
- Command: `python -m pytest -q -p no:cacheprovider rules/test_zoning_rule_review_register_calculations.py`
- Counts: 53 passed
- Evidence: [run log](../evidence/calc-first-building-option-complete.txt)
- Test files tested:
  - `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` (`7cd2f3e7e1648bdc666369761d3df9283b1e0a3756b01b6e6916cbb6878f085f`)
- These deterministic tests ran in the build and all passed, bound to the code identity and the test-file digest shown. If a code module or the test file changes, the checker shows 'Not run' until the tests are run again. A passing result is a code check, not a human or professional review of the law.

## Linked records (linked, not copied)

- docs/measurement-basis/MEASUREMENT_BASIS.md (the measurement basis; linked, not copied)
- services/api/app/rules/coverage/COVERAGE_MATRIX.md (the rule-coverage matrix; linked)
- docs/reference-cases/R6B/cases/step-p6-worked.json (the six-step independent example)
- docs/DISCOVERY_BACKLOG.md (DB-210)
- docs/zoning-rule-review/calculations/calc-floor-area-allowance.md (the component entries)

## Code and tests

- `services/api/app/scenario/three_answers/result_ways.py`
- `services/api/app/scenario/three_answers/three_way_document.py`
- `services/api/app/spatial/corner_reach_area.py`
- `services/api/app/scenario/three_answers/lot_coverage_by_portion.py`
- `services/api/app/scenario/three_answers/first_building_options.py`
- `services/api/app/scenario/three_answers/preliminary_apartment_estimate.py`
- `services/api/tests/rules/test_zoning_rule_review_register_calculations.py`

## Legal requirements and chosen design assumptions

| Figure or step | Kind | Quoted captured text (legal) | Capture |
|---|---|---|---|
| Floor area ratio 2.00 / maximum floor area (ZR 23-22) | LEGAL_REQUIREMENT | the maximum #residential# #floor area ratio# shall be as set forth in the following table | `zr-23-22` |
| Interior/through 80%, corner 100% lot coverage (ZR 23-362) | LEGAL_REQUIREMENT | the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent. | `zr-23-362` |
| R6B heights 30/45/55 ft (ZR 23-432) | LEGAL_REQUIREMENT | the minimum base height, maximum base height, and maximum #building# height shall be as set forth in the following table | `zr-23-432` |
| max dwelling units = maximum floor area / factor (ZR 23-52) | LEGAL_REQUIREMENT | the maximum number of #dwelling units# permitted shall be determined by dividing the maximum #residential# #floor area# permitted on the #zoning lot# by the applicable #dwelling unit# factor | `zr-23-52` |
| 10-ft floor-to-floor height (a chosen design assumption) | DESIGN_ASSUMPTION | - | - |
| Same-plan uniform-plate stack, and which building the first option shows (DB-210; a chosen design assumption, the owner's pending decision) | DESIGN_ASSUMPTION | - | - |
| Apartment size 700 sq ft (a preliminary assumption) | DESIGN_ASSUMPTION | - | - |
| Efficiency share 0.60 to 0.75 (a preliminary assumption) | DESIGN_ASSUMPTION | - | - |

## Gaps and unresolved questions

- Building A and the footprint figure are withheld because the recorded and tax-map outline lot areas disagree; the legal unit limit is withheld; the method difference (DB-210) and the area conflict are shown, not resolved.
- The engine's own single-answer building method differs from building B's (DB-210).

- Coverage gap: No single register page compared the first building option to an independent worked example before this entry; it does so across the six steps and states what each step still owes.

## Human review

- Current verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -
- The verdict is derived from the reviewer's recorded decision and whether it still matches the current code identity, law captures and revision. A verdict is a named human reviewer's own answer; agent reviews are never recorded here.

