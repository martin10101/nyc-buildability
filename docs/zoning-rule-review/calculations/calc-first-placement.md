# Illustrative placement of the first building: footprint on the lot and its offsets on two bases (benchmark lot)

GENERATED FILE - do not edit by hand. Produced by `services/api/app/rules/review_register/render_review_register.py` from `register.json`; edit the JSON and re-render. See `GUIDE.md`.

> This is the program's own draft reading, worked by an AI agent. It has not been reviewed by a qualified architect or zoning examiner and is not legal advice (ADR-007).

- Calculation id: `calc-first-placement`
- Entry kind: calculation (a combined/arithmetic calculation; no rule file)
- Family: placement
- Applies from: 2024-12-05 (to: no end date)
- Revision: 2 (last changed 2026-10-15)
- Combines rule entries: `r6-r12-residential-far`, `r6b-lot-coverage`, `r6b-side-yard`

## Code identity

An entry with no rule file is fingerprinted by the LF-normalized sha256 of its code module(s). If a module changes and the entry is not revised, the check fails - as a changed rule file is caught for a rule entry.

- Combined code identity: `cc9626ac951b4c95ba914be5b459b39b3c98a9295fedba793dd0a91b0814bf8d`
- Modules:
  - `services/api/app/scenario/three_answers/placement.py` (`faf552ef10482709ee0fe40221c03ee1cd1d1e1b67f75f4c979d3894b93c8e65`)
  - `services/api/app/scenario/three_answers/three_way_document.py` (`3376f7b819ab58d298ff228eaa94f331056f0a024d5e4407d11375e8b4a36b2c`)
  - `services/api/app/scenario/three_answers/placement_wiring.py` (`8a600b04bd7cfa3ed0d00242b7a9434b3f86c299a848195d5e2cb86ead63c6c9`)
  - `services/api/app/scenario/three_answers/geometry.py` (`d85e1aed33efc9a11ee5f64441d6e2bbfb2e551083c4120dd9b9c49a9e8c9988`)

## Law

| Section | Official link | Last amended | Captured on | Capture id | Digest (sha256) |
|---|---|---|---|---|---|
| 23-322 | [23-322](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-322) |  | 2026-10-07 | `zr-23-322` | `2a5af75847b73f8238936cbc9818eef0b76102e588be741254604d0a2d8c2c3e` |
| 23-335 | [23-335](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-335) |  | 2026-10-07 | `zr-23-335` | `31b67b9d47eca82cb93e1b06db908b20f1ad7f159c2b4306d78248e5fb02fcf2` |
| 23-362 | [23-362](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362) | 2024-12-05 | 2026-09-30T07:29:06Z | `zr-23-362` | `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9` |

## Where it applies

An illustrative placement of the worked first building on the lot: a footprint as wide as the full street frontage and as deep as the plate (the zoning floor area per storey) needs, placed in the corner on the street lines. It is drawn on the printed-tax-map basis; the city-map (GIS) outline is used only as a conflict check, and the two bases are never mixed into one figure. The placement is reported on the first building alternative; where a measure needed to place it is missing it is held back (withheld, with no outline).

## Exceptions and limits

- The placement is an illustration, not a design, a dwelling layout or a finding that the building complies, is buildable or is feasible.
- The printed tax map and the city-map outline disagree (the frontage differs by about 3.12 feet); the conflict is reported and neither basis is chosen - a survey or deed would settle it.
- The plate is zoning floor area per storey; the physical floor plate (gross-up, exclusions, wall thickness) is not checked; the rear yard and the zoning lot stay not known.

## How the program reads it

The footprint is a rectangle as wide as the full Northern Boulevard frontage and as deep as the plate needs: the plan depth is the plate (20,150 / 3 = 6,716.67) divided by the frontage, so on the printed-tax-map basis the depth is 6,716.67 / 100.76 = 66.66 ft and the footprint is 100.76 x 66.66 = 6,716.66 sq ft (reconciled with the plate within half a square foot). On that basis the footprint clears the lot line opposite the frontage by 100 - 66.66 = 33.34 ft and stands on the street lines (ZR 23-322 requires no front yard), leaving a back strip wider than the five feet any open area along a side lot line must keep (ZR 23-335(b)); the footprint is about 66.66 percent of the tax rectangle and the maximum residential lot coverage is read by portion (ZR 23-362: 100 percent corner / 80 percent interior). The city-map outline gives a 103.88 ft frontage, a 64.66 ft plan depth and a 35.31 ft back clearance - carried beside the tax-map figures as a conflict, never mixed. The footprint and offsets are computed in placement.py; three_way_document.py, through the thin placement_wiring.py, emits the placement on the first alternative and geometry.py draws the floor plates within the measured lot outline.

## Inputs, units, measurement basis, formula and rounding

- Inputs:
  - zoning_floor_area_sqft = 20150 (the worked building's floor area)
  - storeys = 3
  - printed-tax-map frontage 100.76 ft and depth 100 ft (PLUTO lotfront/lotdepth)
  - city-map (GIS) frontage 103.88 ft and depth 99.97 ft (conflict check only)
- Units: feet and square feet
- Measurement basis: The placement is on the printed-tax-map basis (PLUTO lotfront/lotdepth); the city-map (GIS) frontage and depth (EPSG:2263 US survey feet, measured from the prepared outline and the lot-reach measure) are a conflict check only. See the measurement-basis record; the two bases are never mixed in one figure.
- Formula: plan depth = plate / frontage; footprint = plan depth x frontage; back clearance = depth - plan depth; the GIS figures are computed the same way as a conflict check
- Rounding: round half up to two decimals; the footprint reconciles with the plate within half a square foot (no single figure is forced)

## Worked example: independent expected versus the program's actual

The illustrative placement of the three-storey Building B on the benchmark lot (215-16 Northern Boulevard): the footprint on the printed-tax-map basis reconciled with the plate, its offsets, and the city-map outline carried beside it as a conflict.

- Inputs: zoning_floor_area_sqft = 20150; storeys = 3; tax_frontage_ft = 100.76; tax_depth_ft = 100; gis_frontage_ft = 103.88; gis_depth_ft = 99.97
- Expected answer (independent): none
- Basis of the expected answer (reference_case): placement-building-b.json: the plate is 6,716.67 (plate); the footprint on the printed-tax-map basis is 100.76 x 66.66 = 6,716.66, 0.01 under the plate (footprint-tax-map); the placement clears the back lot line by 33.34 ft and stands on the street lines (placement-tax-map); the city-map outline gives 103.88 ft frontage, 64.66 ft plan depth and 35.31 ft back clearance (+1.97), a conflict the readers leave unresolved (gis-conflict-check, not known as a single figure); the maximum lot coverage is read by portion, 100 percent corner / 80 percent interior (lot-coverage-max). Both step-P8 readings agree on the tax-map figures; the GIS conflict stays not known.
- Independent record(s) cited: placement-building-b#plate, placement-building-b#footprint-tax-map, placement-building-b#placement-tax-map, placement-building-b#gis-conflict-check, placement-building-b#lot-coverage-max
- Who prepared the expected answer: worked independently by two sealed-folder AI agents (step P8); not checked by a professional
- Program's actual answer: plan_depth_ft = 66.66; footprint_sqft = 6716.66; tax_back_clearance_ft = 33.34; gis_back_clearance_ft = 35.31; frontage_conflict_ft = 3.12
- Standing of the program's answer: available_conditional
- What the engine computes (the document withholds it): none
  - The program places the footprint on the printed-tax-map basis and carries the city-map figures beside it as a conflict, exactly as the two readings do; the two bases are never mixed and neither is chosen, so the placement stays conditional.
- Do they agree? not determined - a side is withheld/not built, or the two readings differ

## What the program does today versus what is planned

Implemented and tested:
- The document places the first building alternative: building_alternatives[0].placement is a placed placement with the footprint outline, the printed-tax-map basis, the checks and the conditions; geometry.floor_plates draws three plates within the lot outline (test: test_document_actuals_match_the_recorded_fixture).

In the program but no test checks it:
- (none recorded)

Planned, not built:
- The dimensioned footprint, section and offsets are drawn on the scenario sheet by a later task; this entry records the placement data the sheet reads.

## Automated test result

- Status: Not run
- Code identity tested: ``
- Commit tested: ``
- Date tested: 
- Command: `python -m pytest -q -p no:cacheprovider rules/test_zoning_rule_review_register_calculations.py`
- Counts: 
- Evidence: [run log](../evidence/calc-first-placement.txt)
- Test files tested:
  - `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` (``)
- Its code identity is the four modules that compute (placement.py), emit (three_way_document.py through the thin placement_wiring.py) and draw (geometry.py) the placement. The deterministic register tests run in CI; the result is recorded as 'Not run' until a run is bound to this code identity and the test-file digest. A passing result is a code check, not a human or professional review of the law.

## Linked records (linked, not copied)

- docs/measurement-basis/MEASUREMENT_BASIS.md (the measurement basis; linked, not copied)
- docs/research/evidence-records/NB-04-lot-dimensions-basis.json (the four-measure basis)
- docs/reference-cases/R6B/cases/placement-building-b.json (the worked placement, step P8)

## Code and tests

- `services/api/app/scenario/three_answers/placement.py`
- `services/api/app/scenario/three_answers/three_way_document.py`
- `services/api/app/scenario/three_answers/placement_wiring.py`
- `services/api/app/scenario/three_answers/geometry.py`
- `services/api/tests/rules/test_zoning_rule_review_register_calculations.py`

## Legal requirements and chosen design assumptions

| Figure or step | Kind | Quoted captured text (legal) | Capture |
|---|---|---|---|
| Plan depth and footprint from the plate and the frontage (the footprint outline) | DESIGN_ASSUMPTION | - | - |
| The footprint stands on the street lines - no front yard required (ZR 23-322) | LEGAL_REQUIREMENT | In the districts indicated, no #front yard# requirements shall apply. | `zr-23-322` |
| A side open area must be at least five feet wide (ZR 23-335) | LEGAL_REQUIREMENT | for #zoning lots# containing all other types of #residences#, no #side yards# shall be required. | `zr-23-335` |
| Maximum residential lot coverage by portion (ZR 23-362) | LEGAL_REQUIREMENT | the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent. | `zr-23-362` |
| The city-map (GIS) outline is a conflict check only, never mixed with the printed-tax-map figure | DESIGN_ASSUMPTION | - | - |

## Gaps and unresolved questions

- The whole-lot coverage stays not known as a single figure (the recorded, tax-map and city-map areas conflict); the placement records the bases side by side and chooses neither.
- The rear yard, the zoning lot and the physical floor plate stay not checked; the dimensioned sheet is drawn by a later task.

- Coverage gap: The placement is reported on the first building alternative on the printed-tax-map basis with the city-map outline a conflict check; the whole-lot coverage, the rear yard, the zoning lot and the physical floor plate stay not known or not checked.

## Human review

- Current verdict: Not reviewed
- Reviewer name: -
- Reviewer role: -
- Review date: -
- Revision reviewed: -
- Conditions reviewed: -
- Comments: -
- The verdict is derived from the reviewer's recorded decision and whether it still matches the current code identity, law captures and revision. A verdict is a named human reviewer's own answer; agent reviews are never recorded here.

