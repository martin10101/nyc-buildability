# R6B district coverage checklist

What this file is: the measure of "R6B complete". One row per rule-coverage column, per overlay
that can apply to an R6B lot, per lot condition and exception, per scenario type, and per output.
R6B is the first district taken end to end (D-090 step 1, plan section 4.1). One working R6B
example is not R6B coverage (R206); a district is complete only when every row below is either
`supported and tested` or deliberately listed as `unsupported` / `not applicable`.

Date read: 2026-10-05. Source tree: the integration branch as it will be once the eight reviewed
changes waiting to merge on that day are in (read on a local combination of them). Re-read this file
against the integration branch after they merge. Paths below are repo-relative. Nothing here is
professionally reviewed: every R6B rule is `needs_review`, and the highest status any rule carries
in the repo is `implemented_draft`. Results ship under the standing not-professionally-reviewed label
(ADR-007).

Production reality today: every API route that could carry an R6B result is registered behind a
default-off internal flag (`INTERNAL_RULE_EVAL_ENABLED`, `INTERNAL_SCENARIO_ENABLED`,
`LANE_A_ENABLED`, `INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED`, `INTERNAL_TRANSIT_PARKING_READ_ENABLED`,
`SITE_DEFINITION_WRITE_ENABLED`, `LANE_B_ENABLED`) and returns a generic 404 when the flag is
absent, so in production a user sees nothing. The results route that step 1 requires (C-07 / C-08)
is not built. "What the user sees today" below describes what is produced when the engine runs
(flag on); flipping a flag live is an owner switch.

## Out of scope (owner, 2026-10-05, D-090-R210)

The product's goal is simplified feasibility. Two things are not part of "R6B complete" and are never a
row in this file:

- detailed apartment design: apartment-by-apartment layouts, unit plans, room layouts;
- permit-ready plans: construction, filing or permit drawings.

What stays in: feasibility numbers and diagram drawings (the lot, yards, setbacks, floor outlines, a core
shown as a simple block), each labelled a diagram and not for construction. Unit counts come from the rule
arithmetic and are checked against the schedule, not against drawn apartments. Anything that depends on a
layout is labelled unconfirmed (D-090-R196).

## Status legend (exactly one per row)

- `supported and tested`: captured law text, a rule or code, and a test that was run on 2026-10-05 and passed
  are all linked, and the value is carried into the shared results-v1 document builder.
- `drafted, not carried through`: a builder and test exist; the value does not reach a served output.
- `flag only`: read from data and surfaceable; no rule is computed.
- `unsupported`: not built; the reason and what the user sees today are stated.
- `not applicable`: a captured source or product decision says it never yields a number, with the source.

Tests run (from `services/api` of that combined tree, lane A on, no cache):
- `test_r6b_far_heights.py test_r6b_coverage_yard_units.py` -> `120 passed in 1.83s`
- `test_r1_r12_residential_far.py test_r6b_a02b_golden.py test_r6b_other_districts_unchanged.py` -> `28 passed in 4.27s`
- `test_three_answers_benchmark.py test_r6b_envelope_heights.py test_r6b_a02b_consumers_unchanged.py` -> `22 passed in 3.86s`
- `test_three_answers_addons.py` -> `11 passed in 1.94s`

## 1. Rule-coverage columns (every R6B column of the coverage matrix)

Coverage matrix row read at `services/api/app/rules/coverage/COVERAGE_MATRIX.md`
(R6B grid row and detail rows) and `coverage_matrix.json`.

| Column | Status | Law text (snapshot, section) | Rule or code | Test that proves it | What the user sees today | What is missing |
|---|---|---|---|---|---|---|
| FAR | supported and tested | `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`, 23-22 | `r6_r12_residential_far.rule.json` (R6B=2.0); `r6b_qualifying_housing_far.rule.json` (2.4) | test_r1_r12_residential_far.py; test_r6b_far_heights.py | max residential FAR 2.0, and 2.4 as a qualifying-housing alternative, plus the floor-area number, in the results-v1 document | not reviewed (needs_review, no G6); not served by a mounted route |
| HGT | supported and tested | `zr-23-432.snapshot.json`, 23-432 | `r6b_height.rule.json` (min base 30, max base 45, max bldg 55; qualifying 45/65) | test_r6b_far_heights.py; test_r6b_envelope_heights.py | min base 30 ft, max base 45 ft, max building 55 ft, plus qualifying 45/65 ft alternative | setback depth above base height not modeled (see SBK); not reviewed; not served |
| SBK | unsupported | `zr-23-433.snapshot.json`, 23-433 (captured, no rule) | none; `r6b_height.rule.json` exception `setback_per_23_433_not_encoded` records the gap | none | base and max height but no street-wall setback between them | an R6B setback rule from ZR 23-433 |
| YRD | supported and tested | `zr-23-344.snapshot.json`, 23-344(a); `zr-11-25.snapshot.json`, 11-25 | `r6b_rear_yard_corner_waiver.rule.json` (no rear yard within 100 ft of a corner where two street lines meet at 135 degrees or less) | test_r6b_coverage_yard_units.py | for a qualifying corner, that no rear yard is required within 100 ft of the intersection | the general required rear-yard depth (non-corner case) is not computed; not reviewed; not served |
| COV | supported and tested | `zr-23-362.snapshot.json`, 23-362; `zr-11-25.snapshot.json`, 11-25 | `r6b_lot_coverage.rule.json` (corner 100%, interior 80%, through 80%, standard lots) | test_r6b_coverage_yard_units.py; test_r6b_a02b_golden.py | max residential lot coverage percent by lot type | special interior/through rules not captured; non-standard lots not covered; not reviewed; not served |
| UNI | supported and tested | `zr-23-52.snapshot.json`, 23-52 and 23-52(b); `zr-11-25.snapshot.json`, 11-25 | `r6b_dwelling_units.rule.json` (max residential FA / 680; a fraction of 0.75 or more counts as one) | test_r6b_coverage_yard_units.py | max number of dwelling units | conversions, mixed-factor and qualifying-affordable dividend not computed; senior-housing excluded by applicability; not reviewed; not served |
| AO1 wide-street portion | unsupported | `zr-23-432.snapshot.json` (R6B row has no wide-street footnote); `zr-23-22.snapshot.json` | none for R6B; R6B sits in the flat `r6_r12_residential_far.rule.json` list, not `r6_r7_r8_wide_street_conditional_far.rule.json`; `r6b_height` exception `no_street_width_dependence`; `r6b_qualifying_housing_far` exception `no_wide_street_increase` | none | one FAR and one height, not split by street width | the matrix records this not_implemented and plan section 2.1 lists it as still missing for R6B; whether a wide-street add-on could ever yield an R6B number is not settled by any captured text in the repo: not known |
| AO2 corner-lot coverage | supported and tested | `zr-23-362.snapshot.json`, 23-362; `zr-23-344.snapshot.json`, 23-344(a); `zr-11-25.snapshot.json` | `r6b_lot_coverage.rule.json`; `r6b_rear_yard_corner_waiver.rule.json` | test_r6b_coverage_yard_units.py; test_r6b_a02b_golden.py | corner lots get 100% coverage and the rear-yard waiver | not reviewed; not served |
| AO3 split-district averaging | unsupported | not captured for R6B | none; `splitzone` is read as a flag in `services/api/app/profile/hidden_issue_flags/map_based_rules.py` | none | no split-district averaging; the split flag is read but not wired into results | source capture and an averaging rule |
| AO4 FA exclusions / obstructions | unsupported | not captured | none | none | no floor-area exclusions or permitted obstructions applied | source capture and a rule |
| AO5 qualifying affordable/senior (City of Yes) | supported and tested | `zr-23-22.snapshot.json`, 23-22 (qualifying column); `zr-23-432.snapshot.json`, 23-432 (qualifying heights) | `r6b_qualifying_housing_far.rule.json` (2.4); `r6b_height.rule.json` qualifying outputs (45/65) | test_r6b_far_heights.py; test_three_answers_addons.py | a qualifying-housing FAR 2.4 and heights 45/65 ft as a separately labelled alternative when a qualifying program is selected | whether a development qualifies is a separate determination the rule does not make; not reviewed; not served |
| AO6 community facility FA | unsupported | not captured | none; listed in `services/api/app/scenario/addons/catalogue.py` as not available (rule_not_implemented) | none | not offered | source capture and a rule |
| AO7 choice of bulk rules | unsupported | not resolved; coverage matrix records needs_reviewer (whether a Quality Housing vs height-factor choice applies to R6B is a legal reading, queue A-11) | none; `r6b_height.rule.json` emits one contextual height family with a qualifying alternative, no choice mechanism | none | one contextual height family, no height-factor option | not known until the governing text is captured and read as a labelled draft; then a choice mechanism if it applies |
| AO8 ground-floor commercial | unsupported | not captured | none; catalogue lists it not available (rule_not_implemented) | none | not offered | source capture and a rule |
| AO9 transfers by certification | unsupported | not captured | none; catalogue lists it not available (rule_not_implemented) | none | not offered | source capture and a rule |
| AO10 neighbor's unused FA | unsupported | not captured for R6B | `services/api/app/scenario/unused_floor_area.py` exists but no R6B rule is wired to it | none | not offered | an R6B rule and source capture |
| AO11 special permits / authorizations | unsupported | not captured | none | none | not offered | source capture and a rule (text maximum only) |
| AO12 variances and rezonings | not applicable | coverage matrix (NA for all 45 by product decision); plan section 2.1 | n/a (opportunity note only) | n/a | an opportunity note, never a number | nothing; it is deliberately never a computed number |

## 2. Overlays and mapped conditions that can apply to an R6B lot

Read from `services/api/app/profile/hidden_issue_flags/map_based_rules.py` (PLUTO columns) and
`services/api/app/profile/transit_parking.py`. The benchmark R6B lot (215-16 Northern Blvd,
BBL 4073340070) is also a C2-2 corner lot, so the commercial-overlay row is live for it.

| Item | Status | Law text / source | Rule or code | Test that proves it | What the user sees today | What is missing |
|---|---|---|---|---|---|---|
| Commercial overlay on a residential lot | flag only | PLUTO `overlay1`/`overlay2` (field meaning not decoded, surfaced verbatim) | `map_based_rules.py`; route `hidden_issue_flags_read.py` (`INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED` + lane B); rules note it via `commercial_overlay_not_captured` | not run here | a flag naming the overlay code | Article III capture and C-to-R rules; the flag has no results-contract slot yet |
| Flood (FEMA / PFIRM) | flag only | PLUTO `firm07_flag`/`pfirm15_flag`; `docs/research/pluto-firm-flags-2026-10-02.md` | `map_based_rules.py` | not run here | a flag that part of the lot may be in the 1% floodplain; no flood-zone letter, no Appendix G claim | flood-zone letter / base flood elevation dataset and the ZR flood-resilience rules |
| Landmark / historic district | flag only | PLUTO `landmark`/`histdist` | `map_based_rules.py` | not run here | a flag | nothing to compute (an LPC determination, not ZR math); stays a flag, but is not yet wired into results |
| Inclusionary housing (MIH) | flag only | PLUTO `mih_opt1`-`mih_opt4`; ZR Appendix F captured as structure only | `map_based_rules.py` | not run here | a flag | the MIH bonus and requirement rules and the Appendix F area list |
| Special purpose district | flag only | PLUTO `spdist1`-`spdist3` | `map_based_rules.py`; R6B rules escalate to professional_review_required via `special_district_modification` when one is present | not run here | a flag; when present, the R6B height/coverage/yard/units withhold the number and ask for review | the special-district rules (none captured) |
| Waterfront / coastal | unsupported | no source recorded (`map_based_rules.py` returns "Check needed") | none | none | "Check needed" naming the missing source | Article VI chapter 2 capture and rules |
| Transit / parking zone | flag only | `services/api/app/profile/transit_parking.py` | route `transit_parking_read.py` (`INTERNAL_TRANSIT_PARKING_READ_ENABLED` + lane B) | not run here | the transit/parking zone status | parking requirement and exemption rules (none computed) |
| Transit easement / airport height / lot within ~20 ft of a district line | unsupported | no source recorded ("Check needed") | none | none | "Check needed" naming the missing source | source capture and rules |
| Lot split by a district line | flag only | PLUTO `splitzone` (boolean; false is a real "not split") | `map_based_rules.py` | not run here | a flag of whether the lot is split | wiring into results; the averaging rule (see AO3) |

## 3. Lot conditions and exceptions

| Item | Status | Law text (snapshot, section) | Rule or code | Test that proves it | What the user sees today | What is missing |
|---|---|---|---|---|---|---|
| Interior lot | supported and tested | `zr-23-362.snapshot.json`, 23-362 | `r6b_lot_coverage.rule.json` (interior 80%) | test_r6b_coverage_yard_units.py | 80% residential lot coverage | special interior-lot rules not captured; not reviewed; not served |
| Corner lot | supported and tested | `zr-23-362.snapshot.json`, 23-362; `zr-23-344.snapshot.json`, 23-344(a) | `r6b_lot_coverage.rule.json` (100%); `r6b_rear_yard_corner_waiver.rule.json` | test_r6b_coverage_yard_units.py; test_r6b_a02b_golden.py | 100% coverage and no rear yard within 100 ft of the corner | not reviewed; not served |
| Through lot | supported and tested | `zr-23-362.snapshot.json`, 23-362 | `r6b_lot_coverage.rule.json` (through 80%) | test_r6b_coverage_yard_units.py | 80% residential lot coverage | special through-lot rules not captured; not reviewed; not served |
| Small / narrow lot | unsupported | not captured | none; `r6b_lot_coverage.rule.json` exception `standard_lots_only` records the gap | none | standard-lot coverage is applied regardless of lot size | the small/narrow-lot provisions |
| Wide vs narrow street and the 100-ft rule | not applicable | `zr-23-432.snapshot.json`, 23-432 (R6B row has no wide-street footnote); coverage matrix street-width source is `not_needed` on every captured (implemented_draft) R6B cell (the not_implemented cells carry null) | `r6b_height.rule.json` exception `no_street_width_dependence` | test_r6b_far_heights.py (asserts the single height set) | one FAR and one height, not split by street width | nothing for R6B's captured rows (see AO1 for the unresolved add-on question) |
| Lot split by a district boundary | unsupported | not captured | `splitzone` flag read in `map_based_rules.py`; no averaging rule | none | the split flag is read but not wired into results; no averaging | the averaging rule and source capture (see AO3) |
| Existing building kept or enlarged | unsupported | not captured as a scenario | `services/api/app/profile/existing_floor_area/` reads or withholds existing zoning floor area (fail-closed); no keep-vs-enlarge rule | none for the scenario | existing floor area shown or withheld with citations; no enlargement allowance computed against it | a keep / enlarge scenario (see section 4) |
| Condo / multi-lot | unsupported | not captured as a zoning-lot computation | read route `condo_records.py` and write route `site_definition.py` (default-off `SITE_DEFINITION_WRITE_ENABLED`) exist | none for the computation | condo records or a defined multi-lot site, if the flags are on; no zoning-lot-level number | the zoning-lot assembly and averaging computation |

## 4. Scenario types

| Item | Status | Law text / basis | Rule or code | Test that proves it | What the user sees today | What is missing |
|---|---|---|---|---|---|---|
| New building (allowance, envelope, building option) | supported and tested | the R6B rules in section 1 | `services/api/app/scenario/three_answers/engine.py` (`generate_results`); `services/api/app/scenario/max_envelope.py` | test_three_answers_benchmark.py; test_r6b_envelope_heights.py | for the R6B benchmark lot: the floor-area allowance, the permitted envelope, a building option with its floor stack and unit estimate, and one geometry block | the engine is library-only; not called by any mounted route; not reviewed |
| Keep / partial rebuild / full rebuild | unsupported | not captured as a scenario | `existing_floor_area/` reads existing zoning floor area only; no keep-vs-rebuild comparison | none | a new-building allowance only | a keep / partial / full-rebuild comparison |
| Add-on and bonus selection | supported and tested | plan section 6 catalogue | `services/api/app/scenario/addons/catalogue.py`; `addons/recalculation.py` | test_three_answers_addons.py | AO5 qualifying-housing produces an alternative; AO2 is automatic; other programs are listed "not available", never a number | the AO6 / AO8 / AO9 rules |
| Lot split | unsupported | not captured | `site_definition.py` multi-lot write route (default-off); no split-district averaging (AO3) | none | a defined multi-lot site, if the flag is on; no averaging | the averaging rule (see AO3) |
| Proposal editor (proposed-massing checks) | supported and tested | the R6B rules in section 1 | `services/api/app/scenario/proposal.py` (validation); `services/api/app/rules/proposal_checks.py`; routes `proposal_checks_api.py` and `proposal_validation.py` (mounted behind `INTERNAL_RULE_EVAL_ENABLED`) | test_r6b_envelope_heights.py (a 60 ft proposal fails the 55 ft standard via the proposal check) | with the flag on, a PASS / FAIL / COULD_NOT_CHECK report against the R6B rules | the editor UI is web and is not verified in this environment; the checks are only as broad as the R6B rules (SBK and others are missing) |

## 5. Outputs: does an R6B result reach each one today

Gap findings read at `docs/plans/ACCURATE_FEASIBILITY_REPORT_GAP_PLAN_2026-10-04.md` and
`docs/plans/CITYWIDE_ONE_AT_A_TIME_PLAN_2026-10-05.md` section 2.8. Router mounts read at
`services/api/app/main.py`.

| Output | Status | Builder / schema | Route and flag | Test that proves it | What the user sees today | What is missing |
|---|---|---|---|---|---|---|
| Results document (results-v1) | drafted, not carried through | `three_answers/engine.py` builds a results-v1 doc; schema `packages/contracts/schemas/v1/results.schema.json` | `generate_results` is called by no mounted route (grep of `app/api` and `main.py` returned nothing) | test_three_answers_benchmark.py | nothing: no route serves it | the results route (plan step 1, C-07 / C-08) |
| Website results | drafted, not carried through | `apps/web/src/components/architect/answers/ThreeAnswersPanel.tsx`, `AnswerCard.tsx`, `ResultsStatusStrip.tsx`, `ScopeSummary.tsx`, `DevelopmentLimits.tsx` | fed by the results route, which is not mounted | web tests exist but were not run here (thin client; no npm locally) | components exist; no real R6B result reaches them | the results route and the emitter (gap plan notes #405 open); web behavior is unverified here |
| Drawings (SVG) | drafted, not carried through | SVG kit `services/api/app/drawings/kit/` (svg.py, site_plan.py) and maps `services/api/app/drawings/maps/` | no SVG route is mounted in `main.py`; gap plan: maps renderers are not connected to a results document | not run here | nothing from a result | wiring an R6B result into the kit and a route |
| DXF (AutoCAD opens) | drafted, not carried through | `services/api/app/cad/results_dxf.py` and `cad/dxf_writer.py`; service `cad/export_service.py` (format dxf) | `api/v1/export_api.py` ships UNMOUNTED (not imported in `main.py`); tests mount it on a fresh app | not run here (tests/cad/test_export_api.py exists) | nothing: the export route is not in the app | the PKT-H mount seam |
| Report or PDF | unsupported | single-sheet site-plan PDF writer `cad/pdf_sheet_writer.py` only; `report_model.schema.json` exists but nothing builds a report_model | no `/reports` route is mounted (gap plan: only a comment); the site-plan PDF is behind the unmounted export route | none | nothing | a report_model builder, a `/reports` route, a multi-page report PDF, and the owner's PDF-converter choice (E-02) |
| Spreadsheet | unsupported | none; `report_model.schema.json` names Excel as a target but no writer exists (gap plan: grep for openpyxl / to_excel / .xlsx returned nothing) | none | none | nothing | an Excel/CSV writer |

## Counts per status

Across all 46 rows (18 rule columns, 9 overlays, 8 lot conditions, 5 scenarios, 6 outputs):

| Status | Count |
|---|---|
| supported and tested | 13 |
| drafted, not carried through | 4 |
| flag only | 7 |
| unsupported | 20 |
| not applicable | 2 |

## R6B is complete when

R6B is complete when every row below is either made `supported and tested` or deliberately recorded
as `unsupported` / `not applicable` with its reason, the outputs carry the standing label and the
per-stat law links, and a different agent has reviewed this checklist against the tests (R205 to
R209). The two `not applicable` rows (AO12; wide vs narrow street for R6B) are settled and do not
block. The rows not yet `supported and tested` are:

- Rule columns: SBK, AO1, AO3, AO4, AO6, AO7, AO8, AO9, AO10, AO11.
- Overlays: a decision on each flag-only item (commercial overlay, flood, landmark, MIH, special
  purpose district, transit/parking zone, lot-split flag) between staying a flag and becoming a rule;
  and capture plus rules for waterfront/coastal and the transit-easement/airport/proximity group.
- Lot conditions: small/narrow lot, lot split by a boundary, existing building kept or enlarged, condo/multi-lot.
- Scenarios: keep / partial / full rebuild, lot split.
- Outputs: the results route (results document and website results), the SVG drawings wired to a
  result, the DXF mount seam, the report_model builder plus `/reports` route plus report PDF, and a spreadsheet writer.

AO1 and AO7: the program is not sure whether they apply to R6B (see their rows). Until the captured
law text settles each one they stay `unsupported` and the outputs say "not known"; this is an open
question recorded here, not a request for professional review (D-090-R164).
