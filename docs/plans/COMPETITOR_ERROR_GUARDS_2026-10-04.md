# Competitor-error guard check: can our app make the same 20 mistakes? (D-090 source-025, R147-R151)

## Purpose

The owner handed us a competitor's 88-page "Envelope" report for 215-16 Northern Boulevard
(BBL 4073340070, an R6B / C2-2 corner lot) and a list of 20 mistakes found in it. For each
mistake this document records, honestly, whether OUR app can make the same mistake, where it
could happen, what guard stops it, and the test that proves the guard. It is an assessment
plus tests. It changes no production code and no numbers.

The 20 mistakes are the E1 to E20 items the owner listed; each cites a check from the
competitor review (`docs/COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md`, checks
C-1 to C-12). The recorded 215-16 Northern data used by the tests lives in
`services/api/tests/fixtures/benchmark_215_16_northern/`, the benchmark contract fixture
`packages/contracts/fixtures/valid/benchmark_lot/northern_blvd_215_16_queens_4073340070.json`,
and the results fixtures under `packages/contracts/fixtures/valid/results/`.

## The hard rules this check followed (owner, R148)

- The sample PDF is a reference only. It is not committed and was not added.
- No zoning number or rule table was changed. No file under
  `services/api/app/rules/rulesets/*.rule.json`, `docs/research/zr-snapshots/**`,
  `services/api/app/_zr_snapshots/**`, or any numeric engine constant was touched. Every
  question about a number is sent to the reviewer in the "Number questions for the reviewer"
  section below.
- No production code was changed. This work is assessment, tests, and this table only.

## The four status words

- **PREVENTED+TESTED**: our design stops the mistake and an automated test proves it on the
  recorded data (removing or breaking the guard turns the test red).
- **PREVENTED, NO TEST**: our design stops the mistake but no automated test pinned it yet.
  (After this task none remain: the one such item, E2, now has a test.)
- **NOT BUILT YET (task id)**: the surface where the mistake could appear is not built, so the
  mistake cannot occur today; the named queue or PR task will build it, and a pending
  (skipped) test records the assertion to add when it lands.
- **NOT APPLICABLE IN PHASE 1**: the mistake belongs to a feature family out of Phase 1 scope.
  (None of the 20 fall here.)

## The guards table

| E-id | Mistake | Where our app could make it | Our guard (file + test) | Status | Evidence |
|---|---|---|---|---|---|
| E1 | Heights from more than one source; wrong R6B limits (C-1) | `scenario/three_answers/answers.py` `build_envelope` could read heights from more than one rule | Every height comes from the one ZR 23-432 lookup (`r6b_height.rule.json`), surfaced with `zr_sections == ["ZR 23-432"]` | PREVENTED+TESTED | `tests/scenario/three_answers/test_three_answers_benchmark.py::test_envelope_heights_come_from_one_zr_23_432_lookup` |
| E2 | A wide-street FAR bonus shown for R6B (page 3) | `scenario/three_answers/answers.py` `build_allowance`; the FAR rule tables | R6B is absent from the wide-street-conditional FAR district table (`r6_r7_r8_wide_street_conditional_far.rule.json`), and `r6b_qualifying_housing_far.rule.json` carries the `no_wide_street_increase` documented limitation; the computed allowance surfaces only standard/qualifying FAR, no bonus key | PREVENTED+TESTED | `tests/scenario/three_answers/test_competitor_error_guards_lane_a.py::test_e2_r6b_is_not_in_the_wide_street_conditional_far_district_table`, `::test_e2_r6b_qualifying_rule_states_no_wide_street_increase`, `::test_e2_r6b_allowance_shows_no_wide_street_bonus_value` (CI run: the PR's api job) |
| E3 | A law citation that is not in the current ZR (C-7) | Any rule in `app/rules/rulesets/*.rule.json` could cite a section we have not captured | `app/rules/dsl.py` resolves every `citation_ref` against the captured snapshot store (raises if missing), and `test_rule_citation_digest` binds each quote to the snapshot digest; the bundle is kept byte-identical to the captured ZR | PREVENTED+TESTED | `tests/rules/test_rule_citation_digest.py::test_s1_every_committed_rule_still_validates_and_loads`, `tests/rules/test_zr_snapshot_bundle.py::test_every_bundled_snapshot_is_byte_identical_to_canonical` |
| E4 | Stale data shown as current (C-7) | `profile/data_versions.py` could mark an out-of-date source current | The version rule fails closed: a newer published version marks "Out of date"; an unknown version is never "current" | PREVENTED+TESTED | `tests/profile/test_data_versions.py::test_the_competitor_reports_pluto_24v4_is_out_of_date`, `::test_benchmark_sources_show_their_pinned_versions_and_are_current` |
| E5 | Allowance (24,180 / 20,150) muddled with the fitting building (C-2) | `scenario/three_answers/building_option.py` could report the fitting building as the allowance | The allowance (standard and qualifying) is a separate answer; the building option carries its own `achieved_zoning_floor_area`; the shortfall compares the two | PREVENTED+TESTED | `tests/scenario/three_answers/test_three_answers_benchmark.py::test_building_option_reconciles_to_plate_times_floors`, `tests/scenario/three_answers/test_three_answers_shortfall.py::test_shortfall_flips_between_wide_and_tight_envelope_via_the_wiring` |
| E6 | A shortfall reason that is template text, not computed (C-11) | `building_option.py` `shortfall_reason` | The reason is emitted only when the option is strictly below the allowance, and it names the real constraints with the actual numbers compared | PREVENTED+TESTED | `tests/scenario/three_answers/test_three_answers_shortfall.py::test_red_shortfall_present_with_true_reason_when_envelope_too_small`, `::test_green_no_shortfall_when_envelope_holds_allowance` |
| E7 | Existing building size not shown; no flag when it exceeds the allowance (C-3) | `profile/existing_floor_area/`, `profile/hidden_issue_flags/existing_building.py` | Existing zoning floor area is shown or honestly "Check needed"; when it exceeds the as-of-right allowance the one verbatim flag fires | PREVENTED+TESTED | `tests/profile/test_hidden_issue_flags.py::test_larger_flags_when_existing_exceeds_the_as_of_right_allowance`, `::test_larger_check_needed_when_floor_area_unknown_carries_the_b05_reason` |
| E8 | Zoning lot treated as the tax lot; recorded zoning-lot docs ignored (C-9) | `scenario/three_answers/engine.py` statement; `profile/hidden_issue_flags/zoning_lot_history.py` | The results carry "Based on the lots you selected - the app does not verify the zoning lot"; recorded zoning-lot documents and DOB zoning-lot mentions are surfaced as reminder flags | PREVENTED+TESTED | `tests/profile/test_zoning_lot_history_flags.py::test_benchmark_lot_70_reminds_from_the_recorded_dob_mention_and_acris_metadata`, `tests/scenario/three_answers/test_three_answers_benchmark.py::test_remaining_capacity_is_never_a_number` |
| E9 | Lot split pieces not checked each with its own lot type; subdivision not stated (C-10) | No split-lot scenario exists; `three_answers` evaluates one lot | None yet; A-13 will evaluate each resulting lot with its own lot type and state the subdivision | NOT BUILT YET (A-13) | `tests/scenario/three_answers/test_competitor_error_guards_lane_a.py::test_e9_split_lot_evaluates_each_piece_with_its_own_lot_type` (skipped, pending A-13) |
| E10 | A footprint larger than the lot (C-4) | `drawings/kit/adapter.py` `_check_within_lot` on plates, envelope, yards | Every plate, envelope tier and yard outline must lie inside the lot outline (independent geometry check); anything outside fails closed | PREVENTED+TESTED | `tests/drawings/kit/test_adapter.py::test_invalid_input_fails_closed[plate_outside_lot-9]`, `::test_plate_through_a_lot_notch_fails_closed` |
| E11 | Drawings reused as templates, not generated per option (C-4) | `drawings/kit/site_plan.py`, `massing.py` | Each drawing is a pure function of its own results document; across many generated documents every printed number is read from that document and every footprint stays in that lot | PREVENTED+TESTED | `tests/drawings/kit/test_properties.py` (property suite over many generated results, each drawing matched to its own document) |
| E12 | Unit count stated differently in different places (C-12) | `scenario/three_answers/dwelling_units.py` | The unit estimate is one results block with its formula, factor and rounding rule; no other block restates a unit number | PREVENTED+TESTED | `tests/scenario/three_answers/test_three_answers_benchmark.py::test_unit_estimate_in_one_place_with_formula` |
| E13 | Elevator/core text that contradicts the drawings (C-5) | No elevator/building-core producer exists | None yet; the E-06 consistency sweep over a rendered report (needs the building-core producer and E-04) will catch it | NOT BUILT YET (E-06) | `tests/drawings/test_competitor_error_guards_lane_e.py::test_e13_elevator_and_core_statements_match_the_drawings` (skipped, pending E-06) |
| E14 | Ground-floor use in the drawing differs from the option's use (C-4) | `drawings/kit/consistency.py` `check_plates_match_rows` | Each floor plate's use and area must match the floor-by-floor table (same floors, same uses, same areas); a use mismatch fails closed | PREVENTED+TESTED | `tests/drawings/kit/test_adapter.py::test_invalid_input_fails_closed[plates_rows_mismatch-13]` (the `use` -> commercial case) |
| E15 | A label inside a picture not read from the results (C-4) | `drawings/kit/labels.py`, `scope.py`, `site_plan.py` | Every printed number must be a value or geometry edge of the results document; every scope string carries its JSON pointer; an unsourced number fails the C-4 checker | PREVENTED+TESTED | `tests/drawings/kit/test_scope.py::test_every_printed_scope_piece_is_traceable_to_the_document`, `tests/drawings/kit/test_properties.py` (numbers_not_in_input == []) |
| E16 | Parking/transit rule applied differently per option (C-8) | `profile/transit_parking.py` | The transit-zone classification is read once from one PLUTO source; every option reads that one value, so it cannot differ | PREVENTED+TESTED | `tests/profile/test_transit_parking.py::test_one_source_applied_identically_to_every_option` |
| E17 | Flood statements that contradict each other (C-5) | `profile/hidden_issue_flags/map_based_rules.py` `_flood` | The flood status is one flag from one FEMA/PLUTO source, stated once; there is no second flood surface to disagree with it. (A cross-page sweep over a multi-page report, E-06, is future defense-in-depth.) | PREVENTED+TESTED | `tests/profile/test_map_based_rules.py::test_present_flood_flag_states_the_verified_floodplain_meaning_no_zone_letter`, `::test_benchmark_check_needed_items_name_their_missing_source` |
| E18 | Copy-paste options with mismatched heights/floors (C-5, C-6) | No multi-option report is produced over the Northern path | None yet; the E-06 consistency sweep over a rendered multi-option report (needs E-04) will catch it | NOT BUILT YET (E-06) | `tests/drawings/test_competitor_error_guards_lane_e.py::test_e18_no_copy_paste_options_with_mismatched_heights_or_floors` (skipped, pending E-06) |
| E19 | Identical buildings neither merged nor explained (C-6) | No no-duplicate-options guard is merged | None yet; A-05 (PR #369, reviewed PASS, not merged) merges or explains two options with the same building | NOT BUILT YET (A-05, PR #369) | `tests/scenario/three_answers/test_competitor_error_guards_lane_a.py::test_e19_identical_building_options_are_merged_or_explained` (skipped, pending A-05) |
| E20 | More than one footprint value per option on a page (C-5) | `scenario/three_answers/geometry.py`, `drawings/kit/site_plan.py` | There is one geometry block (one lot outline, one coverage-limited footprint) per option; the drawing prints only values from that block, so a second footprint number cannot appear | PREVENTED+TESTED | `tests/drawings/kit/test_properties.py` (every footprint inside its lot, numbers_not_in_input == []), `tests/drawings/kit/test_scope.py::test_every_printed_scope_piece_is_traceable_to_the_document` |

Counts: PREVENTED+TESTED 16; PREVENTED, NO TEST 0; NOT BUILT YET 4 (E9 A-13, E13 E-06,
E18 E-06, E19 A-05 PR #369); NOT APPLICABLE IN PHASE 1 0.

## Where our own app makes the same mistake today

None found. Every mistake that could appear on a surface we have built is prevented and
tested, and the four not-built items cannot produce the mistake because the surface does not
exist. Two honest caveats that are NOT any of the 20 mistakes but a reviewer should know:

- The three-answer geometry draws the lot as an axis-aligned rectangle equal in area to the
  recorded tax-lot area (`scenario/three_answers/geometry.py`), labelled "Approximate
  measurements" and "tax-lot-only estimate". This is a disclosed approximation of the parcel
  shape, not the competitor's E10 mistake: the footprint is coverage-scaled and always inside
  that rectangle, and the real parcel polygon is Lane B site geometry.
- On the benchmark path several non-site engine inputs (overlay present, within-100-ft of a
  corner, intersection angle, floor-to-floor height) are hard-coded in the test inputs and
  surfaced as named assumptions, not as sourced facts. They are honest assumptions today, not
  unsourced numbers shown as fact (the C-07 live feed will replace them); the reviewer should
  confirm this is acceptable for the first accurate report.

## Number questions for the reviewer

I changed no number and decided no legal reading. These questions about numbers go to the
reviewer and to G6:

1. E2 / FAR: confirm R6B genuinely has no within-100-ft-of-a-wide-street FAR increase in the
   current ZR 23-22 (footnote 1 scope), so excluding R6B from the wide-street table is right.
2. E1 / heights: confirm the ZR 23-432 R6B row values our snapshot captured (30 / 45 / 55,
   and 45 / 65 with qualifying affordable or senior housing) are the current table values.
3. E12 / units: confirm the dwelling-unit factor (680 sq ft per unit) and the three-quarter
   rounding rule used for R6B are current and correct.
4. E7 / existing building: the competitor states 54,488 sq ft existing (FAR about 5.41). Our
   existing zoning floor area reads "unknown" (no DOB rows wired). Decide whether and from
   which DOB or certificate-of-occupancy record the existing zoning floor area for lot 70
   should be sourced so the "larger than today's allowance" flag can fire.
5. E8 / E9 / zoning lot: the competitor states DOB shows lot 70 and lot 1 as one zoning lot.
   Our app only flags recorded documents and never verifies. Confirm the zoning-lot
   composition and any split evaluation stay a qualified-professional determination.

## DB-122 existence appendix (searches behind every "we have no X" claim)

Run from the repository root at the task head.

- E9 split-lot evaluation: `git grep -In "evaluate_lot_split\|lot_split\|subdivision_required\|split_lot" -- services/api/app` returned only `split_lot_confident` (a base-zoning positional-uncertainty CLASS in `property_profile.schema.json`, `rules/integration.py`, `spatial/models.py`), never a lot-SUBDIVISION evaluation. No feature evaluates a split lot with each piece's own lot type.
- E13 elevator / building-core producer: `git grep -Iin "elevator\|building_core\|building core\|core_producer" -- services/api/app/scenario services/api/app/drawings services/api/app/cad` returned nothing. No elevator or building-core producer exists.
- E18 / E19 multi-option report, cross-page sweep, duplicate-option guard: `git grep -Iin "consistency_sweep\|no_duplicate_option\|merge_identical\|dedupe_option\|render_report" -- services/api/app` returned nothing. No consistency sweep, no duplicate-option merge/explain guard, and no multi-page report renderer are present (A-05 / PR #369 is reviewed but not merged; E-04 report builder and E-06 sweep are not built; the gap-plan DB-122 appendix records the same for the report route and builder).
