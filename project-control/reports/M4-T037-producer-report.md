# M4-T037 producer report - step P6: one independent hand-worked example of a first building option

I am an AI agent (rules-engineer), the producer. I wrote files and made one commit in an isolated
worktree; I did not review, accept, push or touch the ledger. Every value in the case comes from the two
independent step-P6 readings and the law captures, never from a program run. I did not read or run
`services/api/app/scenario/**` or `services/api/app/rules/**`.

Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a87fabab0ad2ad2e4`
Reset base (claim-seam head): `c346d5a2c9e48ff04f25f085e6bd1d1fcffe27c4`

## Files written

New:
- `docs/reference-cases/R6B/provenance/return-independent-hand-calculation-13.md` (reading 1, unchanged below a header; digest `b1cf6454749eb1966dac78ed56e49c182b174ae2d36db429f8de157dee5cbbd7`)
- `docs/reference-cases/R6B/provenance/return-independent-hand-calculation-14.md` (reading 2, unchanged below a header; digest `e30eb39ed3acc9528b93cc7a15a95436fc505738af1f91652d7a1f460cb1240c`)
- `docs/reference-cases/R6B/cases/step-p6-worked.json` (30 rows) and `docs/reference-cases/R6B/step-p6-worked.md` (rendered)
- `services/api/tests/rules/reference_cases/r6b_reference_cases_step_p6.py` (291 lines; data pins + guards)
- `services/api/tests/rules/reference_cases/test_r6b_reference_cases_step_p6.py` (step-P6 tests)

Changed:
- `docs/reference-cases/R6B/cases/real-lot.json` (row L15 superseded + a dated change-log entry) and its rendered `real-lot.md`
- (correction commit) `docs/reference-cases/R6B/cases/step-p4-worked.json` (row made-up-100x100-units superseded + a dated change-log entry) and its rendered `step-p4-worked.md`; `test_r6b_reference_cases_step_p4.py` (reads the now-superseded row with allow_superseded=True)
- `docs/reference-cases/R6B/README.md` (the case list, the provenance list, a step-P6 "had / did not have" section)
- `services/api/tests/rules/reference_cases/r6b_reference_cases_lib.py` (CASE_IDS, REQUIRED_BASE_IDS, OPTIONAL_ROW_KEYS += `numbers_block`)
- `services/api/tests/rules/reference_cases/r6b_reference_cases_check.py` (wired in step-P6 reading, not-known, block-and-word guards; 569 lines, under 600)
- `services/api/tests/rules/reference_cases/r6b_reference_cases_render.py` (renders the numbers block; existing pages byte-identical)
- `services/api/tests/rules/reference_cases/test_r6b_reference_cases.py` (CASE_IDS tuple += step-p6-worked)
- `services/api/tests/rules/reference_cases/test_r6b_reference_cases_round2.py` (SUPERSEDED += L15)

## Rows added (30, all in step-p6-worked)

Group 1, minimum base height (5, all value): `min-base-height-plain-r6b`, `min-base-height-overlay`,
`min-base-height-street-wall`, `min-base-height-wide-narrow`, `min-base-height-least-height-or-storeys`.
Group 2, made-up lot (7): `made-up-front-yard` (v), `made-up-side-yard` (v), `made-up-rear-yard` (v),
`made-up-street-wall` (NOT KNOWN), `made-up-footprint-a` (v), `made-up-building-a` (v, building block),
`made-up-building-b` (v, building block).
Group 3, floor schedule (1): `floor-schedule-contents` (v).
Group 4, real lot (7): `real-lot-coverage-by-portion` (NOT KNOWN), `real-lot-recorded-vs-measured-area`
(v), `real-lot-rear-yard-variants` (NOT KNOWN), `real-lot-street-wall` (v), `real-lot-ground-elevations`
(v), `real-building-a` (v, building block, footprint held as both figures), `real-building-b` (v,
building block).
Group 5, estimate + legal ceiling (6): `made-up-estimate-a`, `made-up-estimate-b`, `real-estimate-a`,
`real-estimate-b` (each v, estimate block), `made-up-unit-limit` (v, conditional 29, supersedes the
step-P4 count), `real-unit-limit` (v 29, pinned to real-lot#L6).
Group 6, what is missing / closing (4, all value): `both-readers-did-not-have`, `real-lot-missing-facts`,
`settled-answer-contradicted` (both readings: NONE), `six-steps-closing`.

## Rows changed in existing cases (before -> after)

- `real-lot#L15` (building option, floor plates, floors): kind/value UNCHANGED (not_known / none). ADDED
  `superseded_by = [step-p6-worked#real-building-a, step-p6-worked#real-building-b]` + a dated change-log
  entry. Reason: a corrected reading - one current answer per question; the step-P6 case now holds the
  independent worked example L15's not-known rested on being absent.
- `step-p4-worked#made-up-100x100-units` (correction commit): kind/value UNCHANGED (value "29 ...
  conditionally"). ADDED `superseded_by = [step-p6-worked#made-up-unit-limit]` + a dated change-log
  entry. Reason: a corrected reading - one current answer per question; the new made-up-unit-limit row
  gives the current answer for the same made-up 100x100 lot. No guard forbids moving it (it is not in
  step_p4.MUST_STAY_NOT_KNOWN or any pinned set).
- `step-p6-worked#made-up-unit-limit` (correction commit): changed from an unconditional value `29` to a
  conditional value that (a) states 29 with its arithmetic (20,000/680 -> 29), (b) says the step-P4
  row's first condition (the floor-area-ratio definition) is now settled by
  step-p5-worked#floor-area-ratio-made-up-100x100 (both step-P6 readers were given it as settled), and
  (c) says the step-P4 row's second condition - reading 10's "multiple dwelling residences" term - was
  "not read by reading 13 / 14" (the definition was in the step-P6 folder but neither reading read it)
  and still stands, so the 29 holds subject to the building being a multiple dwelling residence.
- `step-p6-worked#real-unit-limit` (correction commit): value stays `29`; its quantity and
  does-not-establish now say plainly it RESTATES `real-lot#L6` (which stays current, NOT superseded, for
  other tasks) for step 5 of the six-step comparison, and a test pins its figure to the live value of L6.
- No other existing row's expected value or kind changed. `real-lot#L5`, `corner-reach#real-lot-coverage`,
  the four `corner-reach` reach rows, and every other step-P1..P5 row are byte-unchanged (reach rows
  verified by a pinned content digest `e708d886...`).

## Point-6 candidates (one current answer per question) - decisions

- `real-lot#L15` (building option, floor plates, floors): SUPERSEDED by step-p6-worked#real-building-a
  and #real-building-b. The step-P6 case gives the current (clearly conditional) worked example; L15
  stays not_known as the historical record.
- `step-p4-worked#made-up-100x100-units` (made-up lot dwelling-unit count): SUPERSEDED by
  step-p6-worked#made-up-unit-limit (correction commit). The two rows gave 29 for the same made-up lot,
  one conditional and one unconditional; the new row carries the current, still-conditional 29 (second
  condition unresolved) and the older row is kept as the historical record.
- `step-p6-worked#real-unit-limit` vs `real-lot#L6` (real lot dwelling-unit ceiling): L6 KEPT current,
  NOT superseded (other tasks read it). real-unit-limit is made a mechanical restatement of L6 (value =
  L6's live value, pinned by a test), so the two can never disagree.
- `real-lot#L5` (maximum lot coverage): KEPT not_known, NOT superseded. The two readings read the
  coverage by portion but measured different corner-portion and interior-strip areas (9,997.60 / 390.39
  vs 9,997.46 / 390.52), so they do not work the two portions to the same areas; the whole-lot figure
  stays not known (also pinned by step_p3.PINNED_COVERAGE_ROWS).
- `corner-reach#real-lot-coverage` (whole-lot coverage): KEPT not_known, NOT superseded - same reason.

## What the readings say on the minimum base height (recorded)

YES - a building wholly below the 30 ft minimum base height is permitted in plain R6B and in a C2-2
overlay mapped within R6B, by ZR 23-436(e) ("shall not apply to #buildings# ... that are #developed# or
#enlarged# and do not exceed such minimum base heights") and the "whichever is less" of ZR 23-431(b) /
35-631(b). Both readings agree on the same words. Reading 14 adds that the defined term "developed" was
not in the folder, so the exemption rests on the ordinary reading of a newly built building as developed
(recorded in the value/does-not-establish naming reading 14). The street wall need rise only to the
building's own height; its horizontal place is not settled (prevailing frontage). No captured provision
sets a least height or least number of storeys (a rule outside the folder is not ruled out).

## Buildings' main figures as recorded

- Made-up A (widest): 2 storeys, 8,000 sq ft/floor, 16,000 total, 4,000 unused, 20 ft (below min base).
- Made-up B (to min base): 3 storeys, 6,666.67 sq ft/floor (= 20,000/3), 20,000 total, 0 unused, 30 ft.
- Real A (widest): 1 storey, footprint 10,309.91 (reading 13) / 10,309.88 (reading 14), 10 ft (below min
  base), unused 9,840.09 / 9,840.12 - both figures held, no single figure.
- Real B (to min base): 3 storeys, 6,716.67 sq ft/floor (= 20,150/3), 20,150 total, 0 unused, 30 ft,
  about 103.9 x 64.66 ft; identical under every variant.
- Estimates (0.60/0.75 shares, 700 sq ft apartment, 2 dp): made-up A 13.71/17.14, made-up B 17.14/21.43,
  real A 8.84/11.05 (same to 2 dp for both readers' floor areas), real B 17.27/21.59. Legal dwelling-unit
  ceiling 29 on each lot (made-up 20,000/680; real = settled real-lot#L6).

## Point-by-point comparison of the two readings

Differences (recorded as both figures / not known, never a single value):
1. Real-lot corner-portion area: reading 13 = 9,997.60 sq ft, reading 14 = 9,997.46 sq ft.
2. Real-lot interior strip: reading 13 = 390.39 sq ft (allows 312.31), reading 14 = 390.52 (allows 312.42).
3. Real building-A footprint allowed: reading 13 = 10,309.91, reading 14 = 10,309.88 (0.03 sq ft apart);
   building A's one-storey floor area and its unused figure follow and are held as both, not smoothed.
4. Rear-yard-beyond-corner variant LABELS: reading 13 labels "V1 = neighbour side lot line -> no rear
   yard, V2 = neighbour rear lot line -> 20 ft"; reading 14 labels these V1/V2 in the OPPOSITE order.
   The two variants' CONTENT agrees; the row records them by content, not by the V1/V2 labels.
5. Real building-A reduced-footprint estimate: reading 13 worked a reduced-footprint variant (about
   10,246 sq ft -> 8.78/10.98); reading 14 did not compute a separate reduced estimate (noted the
   variant is slightly less). The estimate row records the no-rear-yard footprint (8.84/11.05, both
   agree) and says the rear-yard variant lowers it and stays not known.
6. Far-west geometry (which side-lot-line portion is beyond 100 ft): both readings carry the earlier
   readers' dispute (reading 13 finds the whole lot within 100 ft of Northern Boulevard, agreeing with
   the settled reading 12, and notes the earlier reading 11's ~101-ft sliver). Held as a known dispute.

Answers one reading holds subject to a text or a fact the other does not:
- Min base height: reading 14 holds the permit subject to the undefined term "developed" (ordinary
  reading supports); reading 13 does not flag it. Recorded in `min-base-height-plain-r6b`, naming reading 14.
- 215 Place street wall: both readings raise ZR 35-633(b) (mandatory also along 215 Place if a Commercial
  District is mapped along the entire block frontage) as not known; recorded in `real-lot-street-wall`,
  stated in the value, and both agree it does not change the widest footprint.

## What stays "not known", with its kind of gap

- `made-up-street-wall`: the required street-wall place. KIND: a missing fact about the property (the
  neighbouring buildings' street-wall widths; from a record of the neighbouring buildings). The stated
  neighbours sit at exactly 35 ft and do not "exceed 35 feet", so they are not eligible under ZR
  23-431(a) - a limit of the example, not a finding about any property.
- `real-lot-coverage-by-portion`: the single whole-lot coverage figure. KIND: the corner/interior split
  is read, but the exact areas rest on each reader's own measurement of the outline, which differ; a
  surveyed outline would settle them.
- `real-lot-rear-yard-variants`: the rear yard beyond the corner area. KIND: a missing fact about the
  property (the adjoining zoning lots' lot-line types; from a survey, a deed or a record of the
  neighbouring lots).
- Base-plane datum (named in `real-lot-ground-elevations`): stays not known at step-p3-worked#base-plane-real-lot. KIND: a missing fact about the property (ground / curb / grade elevations; from a survey).

## Missing facts about the real lot, with the variant each selects (both readings)

- Adjoining zoning lots' lot-line types -> selects the rear yard beyond the corner (a neighbour's rear
  lot line gives a 20 ft rear yard, a neighbour's side lot line gives none).
- Neighbouring buildings' street-wall widths/distances -> whether a prevailing street wall frontage
  exists (optional; does not change the widest footprint).
- Ground / curb / grade elevations -> the base-plane datum (the absolute heights, not the relative ones).
- The far-west geometry (which side-lot-line portion is beyond 100 ft) -> which deemed-rear-lot-line
  segment arises (a dispute carried from the earlier readers).

## Texts the two readings name as not had (list for the orchestrator)

Both readings (on the case's `both-readers-did-not-have` list): section / pointing words / answer awaiting:
- ZR 12-10 "street wall line level" (base-plane definition "between #curb level# and #street wall line
  level#") -> the real lot's base-plane datum stays not known.
- base-plane adjoining final-grade / ground elevations ("average elevation of the final grade adjoining
  the #building#") -> the real lot's base-plane datum stays not known.
- ZR 23-434 (height and setback modifications for eligible sites) -> not relied on; no eligible-site
  figure used.
- ZR 23-435 (towers) -> not relied on; no tower figure used.
- ZR 12-10 "outer court" (ZR 23-431(b)/35-631 recess clause) -> affects only recess geometry, not the
  simple walls worked.
Named by ONE reading only (NOT on the "both" list, recorded here for the orchestrator): "developed"
definition, ZR 23-341, "rear wall line level"/"building segment"/"abutting buildings", Mandatory
Inclusionary Housing / UAP footnote terms, "street setback line" (reading 14); ZR 23-311/23-312/23-413
obstructions (reading 13).

Settled answer a reader found a text to contradict: NONE (both readings). Recorded in
`settled-answer-contradicted`.

## Per-input-state test table (state -> expected -> test name)

| Input state | Expected | Test name |
|---|---|---|
| The two readings saved unchanged | present, digest-pinned, END-OF-REPORT, from sealed folder | test_the_two_step_p6_readings_are_present_unchanged |
| A reading edited | caught (digest changed) | test_a_changed_step_p6_reading_is_caught |
| The committed case | validates clean end to end | test_step_p6_case_validates_clean |
| Every row | names both readings 13 and 14 | test_step_p6_rows_name_both_readings |
| Q1 minimum base height | value on both readings (permitted; whichever is less; no least height) | test_minimum_base_height_rows_are_values_on_both_readings |
| Rows the readings do not jointly settle | not known, with a kind of gap | test_step_p6_not_known_rows_with_a_kind_of_gap |
| A not-known row given a value | refused | test_a_step_p6_value_where_the_readings_differ_is_refused |
| A changed law quote | caught, naming the row | test_a_changed_law_quote_in_a_step_p6_row_is_caught |
| Every building/estimate block | recomputes clean from its own inputs | test_building_blocks_recompute_clean |
| Storey tables | sum to the total; total + unused = maximum | test_every_storey_table_sums_to_its_total_and_total_plus_unused_is_the_maximum |
| Building A | plan area x storeys = floor area | test_plan_area_times_storeys_equals_building_a_floor_area |
| Building B | plan area = maximum / storeys | test_building_b_plan_area_is_the_maximum_divided_by_its_storeys |
| Real building A | both footprints held; each gives one storey | test_real_building_a_holds_both_readers_footprints_and_both_give_one_storey |
| A changed storey floor area | arithmetic fails | test_a_changed_storey_floor_area_makes_the_arithmetic_fail |
| Estimate four figures | follow from the floor area (recomputed) | test_estimate_four_figures_follow_from_the_floor_area |
| Real estimate A (floor area differs) | both floor areas give the same two-decimal quotients | test_real_estimate_a_both_floor_areas_give_the_same_two_decimal_quotients |
| A changed estimate figure | its test fails | test_a_changed_estimate_figure_makes_its_test_fail |
| Made-up legal ceiling | current conditional 29; supersedes the step-P4 count | test_made_up_unit_ceiling_is_the_current_conditional_29_superseding_step_p4 |
| Real legal ceiling | 29, pinned to the live value of real-lot#L6; L6 stays current | test_real_unit_ceiling_is_pinned_to_the_live_value_of_real_lot_L6 |
| Real ceiling figure that differs from L6 | fails the pin | test_a_real_unit_figure_that_differs_from_L6_fails_the_pin |
| Building row without point-5 words | refused | test_a_building_row_without_the_point5_words_is_refused |
| Estimate row calling figures validated | refused | test_an_estimate_row_calling_its_figures_validated_is_refused |
| Estimate row share lacks 'preliminary assumption' | refused | test_an_estimate_row_whose_share_lacks_preliminary_assumption_is_refused |
| A building figure marked as neither | refused | test_a_building_figure_marked_as_neither_is_refused |
| An assumption marked a legal requirement | refused | test_an_assumption_marked_as_a_legal_requirement_is_refused |
| L15 | superseded; targets current | test_l15_is_superseded_by_the_step_p6_building_rows_and_targets_are_current |
| Reach rows | byte-stable (pinned digest) | test_the_reach_rows_are_byte_stable |

## Checks (each run one at a time; direct exit code captured with echo $?; re-run after the correction commit)

- a. `python -m ruff check .` (from services/api): **exit 0** ("All checks passed!").
- b. `python -m pytest -q -p no:cacheprovider tests/rules/reference_cases tests/spatial/test_lot_reach.py tests/scenario/three_answers/test_result_way_bridge_overlay.py`: **exit 0** - 118 passed.
- c. `python tests/rules/reference_cases/r6b_reference_cases_render.py --check`: **exit 0** ("reference-case check PASSED (no issues)").
- d. `python3 tools/modularity_check.py --check` (repo root): **exit 0** (735 files; failures 0; 30 pre-existing warnings, none on the new files). `python3 scripts/lanes/check_lane_paths.py --coverage`: **exit 0** ("LANE COVERAGE PASS").
- e. Mutation proofs in a temporary copy OUTSIDE the repository (`/tmp/m4t037-mut*/`): **exit 0** - all PASS and the committed file still validates clean: (1) a changed quoted law phrase makes the citation check fail and names the row; (2) a row given a value where the two readings differ is refused; (3) a changed storey floor area makes the arithmetic fail; (4) a changed estimate figure makes its test fail; (5) the point-5 words removed from a building row make the test fail; (6, correction commit) a real-unit-limit figure (30) that differs from the live value of real-lot#L6 (29) fails the pin, and the committed figure equals L6.

Not run (per the brief and CLAUDE rules): the full api suite (CI runs it on the pushed head); any
`services/api/app/scenario/**` or `services/api/app/rules/**` code.

## Assumptions and limitations (disclosed)

- The whole case is a draft reading of the law by two AI helpers, not professionally reviewed; nothing
  reads as "complies", "feasible" or "legally correct"; no human verdict is entered.
- `real-unit-limit` restates `real-lot#L6` (29) for step 5 of the six-step comparison and does NOT
  supersede L6 (other tasks read it). Per the orchestrator's correction, the restatement is now
  mechanical: its figure is pinned by a test to the live value of L6, with a mutation proof that a
  differing figure fails, so the two can never disagree. The made-up lot's ceiling, by contrast, is a
  genuinely new current answer, so the older step-P4 conditional count is superseded (correction commit).
- The `numbers_block` row shape is a new optional row key (added to OPTIONAL_ROW_KEYS), carrying the six
  steps as numbers for the later program-vs-independent comparison (owner rows R687/R688/R690). Where the
  two readings differ on a figure it holds both, each named by its reading.
- I did not run the journey/scenario tests that need the engine (test_215_16_northern_journey,
  test_three_answers_three_way_emit, test_results_read_law_examples, test_engine_conditions): they read
  only real-lot rows L1-L5 and the corner-reach reach rows, none of which I changed in value or kind; CI
  runs them on the pushed head.

Requested status: awaiting_gate (G2 self-check done above; G3 data-contract-verifier and G4 qa-engineer
are the independent gates).

END-OF-REPORT
