# M5-T129 producer report - decide how each result appears (settled, conditional, withheld)

Producer: scenario-optimization-engineer (builder). Role: build a PURE decision module in NEW
files that nothing calls yet; it computes no zoning number. Contract/claim-seam head reset to:
`5f8b78ce452b4a214cceeb314372f6968373acf6`. Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-a0f3c57f1810681dc`.

## Round 2 (before any review; one commit on top of 85bca681)

Two orchestrator points, both scope corrections: (1) SIZE - `result_ways.py` was 664 source
lines; the allowed paths now also permit `result_way_*.py`, so the cross-result rules were
split into a new module `result_way_conditions.py`. After the split every new file is under the
600-line warning threshold and `tools/modularity_check.py --check` names none of them. (2) The
condition kind for "could not be compared" (open question 3) is completed as reading O4:
`unchecked_condition`, not `contradicted_record` (nothing contradicts the figure; the
comparison was not made). No other behaviour changed; the other three open questions stand.

Files (all NEW / placeholder-replacing; no existing file changed), with source-line counts as
`tools/modularity_check.py` counts them:
- `services/api/app/scenario/three_answers/result_way_inputs.py` (409 SLOC) - the records:
  input records (enums + `ResultWayInputs`), the reach records (mirroring M5-T127, NOT importing
  it), the two legal measures of reading O9, the result vocabulary (keys, labels, gap/condition
  kinds) and the way (output) records.
- `services/api/app/scenario/three_answers/result_way_conditions.py` (292 SLOC; NEW in round 2)
  - the cross-result rules: the K20 unchecked condition, the area condition (reading O4), the
  blanket withholding, the commercial-overlay block and the shared withhold builders and reach
  helpers. Imported only by `result_ways.py`; it computes no zoning number and holds no table of
  what a reading supports.
- `services/api/app/scenario/three_answers/result_ways.py` (448 SLOC) - the per-result deciders,
  the assembly and the ONE public function `decide_result_ways`; imports the records and the
  cross-result rules, and re-exports the records (a compatibility facade), so its public
  interface is unchanged (every test import still resolves).
- `services/api/tests/scenario/three_answers/test_result_ways_lib.py` - shared test builders
  (reads the reach rows through the loader; no test functions).
- `test_result_ways.py` (invariants: S7, S9, H7), `test_result_ways_benchmark.py` (S1, S6),
  `test_result_ways_corner_interior.py` (S2, S3), `test_result_ways_facts_area_overlay.py`
  (S4, S5, S8).

## Round 3 (G4 FAIL on test completeness; one commit on top of f8cd19af)

G3 (data-contract) PASSed with five advisory notes; G4 (QA) FAILed: the module's behaviour was
found correct by BOTH reviews, but several input states the module acts on were pinned by NO
test, and three single-line regressions passed silently (mutations M8, M10, M11). This round
adds the missing tests, applies two orchestrator readings (O11, O12) and the G3 notes, and
re-runs the three silent mutations to prove the new tests bite. No behaviour of the already-
correct paths changed except the two readings below.

Source-line counts now (tools/modularity_check.py): app `result_ways.py` 448, `result_way_inputs.py`
413, `result_way_conditions.py` 320; tests `test_result_ways.py` 211, `_lib.py` 121,
`_benchmark.py` 119, `_corner_interior.py` 86, `_facts_area_overlay.py` 135, `_input_states.py`
126 (NEW). Every file under the 600 warning threshold; the check names none of them.

What was added/changed per finding:
- G4-F1 inclusionary: `test_f1_inclusionary_present_withholds_floor_area_work_owed`,
  `test_f1_inclusionary_not_read_withholds_floor_area_missing_information` (K19; O7).
- G4-F2 flood: `test_f2_flood_present_withholds_heights_work_owed`,
  `test_f2_flood_not_read_withholds_heights_missing_information` (K19; O7).
- G4-F3 density in one: `test_f3_density_evidence_in_one_withholds_the_unit_limit` (K11).
- EVIDENCE_NOT_IN_ONE: `test_density_evidence_not_in_one_is_withheld_as_work_owed_o10` (K11; O10).
- G4-F4 overlay not read: `test_f4_overlay_not_read_withholds_every_residential_result_missing_information`
  (section 10 / K10 generalised; G3 confirmed the behaviour).
- G4-F5 large lot: `test_f5_large_lot_threshold_withholds_coverage_work_owed` (K3; O8).
- G4-F6 not-available reason_kind: `test_an_answer_is_not_available_only_when_every_value_is_withheld`
  now asserts gap_kind/reason_kind for a work-owed case (K20 present -> rule_not_implemented) AND a
  missing-information case (special-district not read -> missing_input).
- G4-F7: (a) `test_f7a_landmark_changes_no_result` (PRESENT and NOT_READ give an identical
  ResultWays to ABSENT; K19); (b) `test_f7b_through_lot_withholds_coverage_and_rear_yard`;
  (c) `test_f7c_setback_reason_says_not_covered` (K8).
- G4-F8: `test_decides_every_result_the_packet_lists` now compares against a LITERAL 20-key set
  (`_PACKET_RESULT_KEYS`) written from the packet objective, not the module's constants.
- G3-F1 (reading O11): `test_o11_district_not_given_withholds_every_result_missing_information`,
  `test_o11_district_not_r6b_withholds_every_result_work_owed`.
- G3-F3 (reading O12): `test_o12_standard_unit_label_carries_the_k14_words`.
- G3-F4: inline `(O3)` marker at the building-option rear-yard dependency, `(O8)` at the large-lot
  coverage branch (result_ways.py).
- G3-F5: explicit None-agreement branch in `result_way_conditions.area_condition` (conditional,
  never settled, kind unchecked_condition), pinned by
  `test_g3f5_agreement_none_with_a_recorded_area_is_conditional_unchecked_never_settled`.
- G3-F2: no change (the could-not-compare kind stays unchecked_condition, reading O4).

Readings applied this round (marked in code and here as the orchestrator's):
- **O11 THE DISTRICT** (in `result_way_conditions.blanket_withhold`, checked first with the other
  blanket conditions). `district=None` -> EVERY result withheld, missing_information, reason: the
  zoning district was not given and it comes from the city's zoning record. `district` other than
  the work order's scope -> EVERY result withheld, work_owed, reason: the rules connected so far are
  R6B's and this district's are owed. The scope string "R6B" is held once as the named constant
  `WORK_ORDER_DISTRICT` (a comment says it is the work order's scope, not a zoning number; the ast
  no-zoning-number test still passes - "R6B" is a string). `housing_kind` is unchanged (a design
  choice, carried for the wording).
- **O12 GAP K14** (in `result_way_inputs.LABELS`). The standard unit limit's label now reads
  "Legal dwelling-unit limit, standard residences (new all-residential building)". The module has
  no input for a conversion or a mixed building; that case stays with the piece that wires it in.

Decision table addition for the district (reading O11): district -> EVERY result -> withheld;
None = missing_information, not-R6B = work_owed.

Open combinations now: **closed** - could-not-compare kind (O4, round 2); special-density
EVIDENCE_NOT_IN_ONE (now pinned, withheld work_owed per O10); the district (O11). **Remaining
open** - only the housing kind not given (a design choice carried for the wording; it changes no
way this milestone). The overlay-column-not-read behaviour is now tested (G4-F4) and was confirmed
by G3.

The three silent mutations, re-run against a copy OUTSIDE the repository (the generic injector
plugin loads the mutant under its real module name; the repo is never touched):
- M8 (overlay NOT_READ treated as absent): now **1 failed** - test_f4_overlay_not_read... CAUGHT.
- M10 (not-available reason_kind mapping swapped): now **2 failed** -
  test_an_answer_is_not_available_only_when_every_value_is_withheld[floor_area_allowance|permitted_envelope].
  CAUGHT.
- M11 (condition_withhold returns None): now **4 failed** - test_f1 (PRESENT, NOT_READ) and test_f2
  (PRESENT, NOT_READ). CAUGHT.

Checks (DIRECT exit codes, round 3): a `ruff check .` = 0 (pass). b `pytest tests/scenario/three_answers`
= 0, 113 passed + 2 pre-existing skips (was 98; 15 new tests, all in `test_result_ways_input_states.py`).
c `pytest tests/contracts tests/spatial` = 0, 887 passed, 3 xfailed. d `modularity_check --check` = 0
(failures 0, 29 warnings; `grep result_way` over the output = NONE); `check_lane_paths --coverage` = 0
(9133 files). e the three mutation re-runs above (M8/M10/M11 all caught). f git status empty after the
commit; `git diff --name-status f8cd19af HEAD` = only allowed paths.

## Round 4 (G4 re-review closed F1-F8; FAILed on one unpinned state: the lot type not given)

TESTS ONLY; the three module files are byte-unchanged (`git diff --stat 319806c9 HEAD -- services/api/app`
empty). G3 passed the module again at this content, so no behaviour changes. This round adds the
F9 test, audits EVERY field and state of the inputs, adds a test for every acted-on state that
no test pinned, and proves each new test bites with a mutation outside the repository.

Source-line counts: app unchanged (result_ways.py 448, result_way_inputs.py 413,
result_way_conditions.py 320); tests test_result_ways.py 211, _lib.py 121, _benchmark.py 119,
_corner_interior.py 86, _facts_area_overlay.py 135, _input_states.py 239. All under 600.

Tests added (name : state pinned), all in `test_result_ways_input_states.py`:
- `test_f9_lot_type_not_given_withholds_coverage_and_rear_yard_only` : lot_type=None (F9; H5 /
  section 4 item 3; a missing input leaves dependent results "not known"). Asserts coverage and
  rear yard withheld missing_information "lot type is not given", every other result unchanged.
- `test_housing_kind_not_given_changes_no_result` : housing_kind=None (a design choice carried
  for the wording; identical ResultWays to a kind given).
- `test_large_lot_threshold_met_none_is_not_a_large_lot` : large_lot_threshold_met=None (falsy;
  same path as False; the caller states the K3 comparison - O8/O5).
- `test_street_line_reach_unknown_withholds_coverage_missing_information` : a street-line reach
  unknown (K12).
- `test_corner_reach_unknown_withholds_rear_yard_missing_information` : the corner reach unknown.
- `test_corner_angle_unknown_withholds_rear_yard_missing_information` : the corner angle unknown.
- `test_corner_angle_above_135_withholds_rear_yard_work_owed` : angle > 135 deg (O9 / ZR 23-344).
- `test_disagree_with_no_outline_figure_uses_the_fallback_wording` : area DISAGREES + outline None.
- `test_overlay_code_present_appears_in_the_reason` : commercial_overlay_code present.
- `test_overlay_code_none_with_overlay_present_still_withholds_without_a_code` : code None.
- `test_overlay_not_supported_without_reading_owed_uses_the_fallback_reading` : OverlayResultSupport
  not supported with no reading_owed (the fallback owed-reading).
- `test_each_k20_condition_present_withholds_every_result[waterfront|airport_height|transit_easement|near_district_line]`
  : each of the four K20 conditions recorded PRESENT (O6; the two the earlier tests did not use).

Every input state and the test that pins it (field : state -> outcome -> test / note):
- district: None -> blanket missing_info -> test_o11_district_not_given; "R6B" -> proceed ->
  every passing test; other -> blanket work_owed -> test_o11_district_not_r6b.
- lot_type: CORNER -> reach-based -> H3 tests; INTERIOR -> coverage K2 / rear yard withheld ->
  test_h4_interior_coverage, test_h9...; THROUGH -> same -> test_f7b; None -> no_lot_type -> test_f9.
- housing_kind: any / None -> no branch (does not act) -> test_housing_kind_not_given.
- area.recorded_sq_ft: None -> withheld missing_info -> test_h5_no_lot_area, test_s5_no_recorded_area;
  value -> proceed -> many.
- area.agreement: AGREES -> no condition -> test_s5_figures_that_agree; DISAGREES -> contradicted_record
  -> test_s5_figures_that_disagree; COULD_NOT_COMPARE -> unchecked_condition (O4) ->
  test_s5_figure_that_could_not_be_compared; None -> unchecked_condition (G3-F5) -> test_g3f5_agreement_none.
- area.outline_sq_ft: present + DISAGREES -> names the figure -> test_s5_figures_that_disagree;
  None + DISAGREES -> "another" -> test_disagree_with_no_outline; otherwise unused (does not act).
- reach: None -> no_outline -> test_h5_no_outline; present -> used.
- reach.street_lines: a reach unknown -> coverage no_outline -> test_street_line_reach_unknown;
  all known -> compared -> H3.
- reach.corner.reach: unknown -> rear yard no_outline -> test_corner_reach_unknown; >100 ->
  withheld work_owed -> test_s1b (144.60), test_h3_c1 (107.70); <=100 -> within -> test_h3_c2.
- reach.corner.angle: unknown -> rear yard no_outline -> test_corner_angle_unknown; >135 ->
  withheld work_owed -> test_corner_angle_above_135; <=135 -> within -> H3.
- special_purpose_district: PRESENT -> blanket work_owed -> test_s6_recorded_special_district;
  NOT_READ -> blanket missing_info -> test_h5_special_district_column_not_read, F6; ABSENT -> none.
- split_by_district_line: PRESENT -> blanket work_owed -> test_h5_recorded_special_district_or_split;
  NOT_READ -> blanket missing_info -> test_h5_split_lot_record_not_read; ABSENT -> none.
- commercial_overlay: ABSENT -> without overlay -> plain tests; PRESENT -> per family -> S1/S8;
  NOT_READ -> every residential missing_info -> test_f4_overlay_not_read.
- commercial_overlay_code: present -> "(code)" in reason -> test_overlay_code_present; None ->
  no code -> test_overlay_code_none.
- inclusionary_housing_area: PRESENT -> floor area work_owed -> test_f1 (present); NOT_READ ->
  missing_info -> test_f1 (not_read); ABSENT -> none.
- flood_zone: PRESENT -> heights work_owed -> test_f2 (present); NOT_READ -> missing_info ->
  test_f2 (not_read); ABSENT -> none.
- landmark_or_historic: PRESENT / NOT_READ / ABSENT -> changes no zoning result (does not act) ->
  test_f7a_landmark.
- waterfront / airport_height / transit_easement / near_district_line (x4): NOT_CHECKED ->
  unchecked_condition -> S6 not-checked; ABSENT -> drops -> S6 all-absent, H3; PRESENT -> blanket
  work_owed -> test_each_k20_condition_present[each].
- special_density: NOT_GIVEN -> withheld work_owed -> test_h4_h9; EVIDENCE_NOT_IN_ONE -> withheld
  work_owed -> test_density_evidence_not_in_one; EVIDENCE_IN_ONE -> withheld work_owed -> test_f3;
  USER_STATEMENT_NOT_IN_ONE -> conditional user_statement -> test_h9_user_statement.
- large_lot_threshold_met: True -> coverage work_owed -> test_f5; False -> no K3 -> base; None ->
  falsy, same path as False (does not act distinctly) -> test_large_lot_threshold_met_none.
- overlay_support: None (overlay present) -> every residential withheld ->
  test_s1_recorded_overlay_with_no_support; all True -> supported -> test_s1b; all/partial False ->
  not supported -> test_s1a; per family -> test_s8_*. supported True/False -> S1a/S8; reading_owed
  given -> used -> test_s8_not_supported; "" -> fallback -> test_overlay_not_supported_without_reading_owed;
  zr_sections given -> set -> test_s8_not_supported; () -> omitted -> S7 battery.

Table summary: ~44 input states across the 21 fields/record-fields; the module acts on ~38 of
them (housing_kind, every landmark state, large_lot None-vs-False, and the outline figure outside
the DISAGREES path create no distinct branch); 13 acted-on states were unpinned before this round
and are now pinned (the rest were pinned in rounds 1-3). No state was found whose outcome differs
from the work order or the readings (point 5): see the one standing observation below.

Mutations (each a single change in a copy OUTSIDE the repository; the repo is never touched):
- MA no_lot_type -> Settled (the reviewer's F9 probe): 1 failed - test_f9_lot_type_not_given...
- MC no_outline -> Settled: 4 failed - test_h5_no_outline (existing) + test_street_line_reach_unknown,
  test_corner_reach_unknown, test_corner_angle_unknown.
- MD rear-yard angle check always passes (within_angle=True): 1 meaningful fail -
  test_corner_angle_above_135 (plus the 3 invariant tests that read result_ways via rw.__file__,
  an injection artifact of mutating result_ways itself).
- MB area DISAGREES "another" fallback changed: 1 failed - test_disagree_with_no_outline...
- MF overlay code never in the reason: 1 failed - test_overlay_code_present...
- ME overlay not-supported fallback owed-reading removed: 1 failed -
  test_overlay_not_supported_without_reading_owed...
- MG K20-present detection disabled: 7 failed, incl. the new
  test_each_k20_condition_present[transit_easement|near_district_line] (the two previously untested).

Point 5 (states whose outcome is NOT what the work order / readings say): NONE requiring a module
change. One standing observation (already flagged round 1, G3-passed, module unchanged by design):
`large_lot_threshold_met=None` is treated as "not a large lot" (K3 not applied), the same as
False - the module holds no 30,000 threshold and the caller states the K3 comparison (O8/O5), so an
unset flag is not a large lot; the wiring piece must set it from the recorded area. Reported, not
changed.

Checks (DIRECT exit codes, round 4): a `ruff check .` = 0. b `pytest tests/scenario/three_answers`
= 0, 128 passed + 2 pre-existing skips (was 113; 15 new test items, all in `_input_states.py`).
c `modularity_check --check` = 0 (failures 0, 29 warnings; `grep result_way` = NONE);
`check_lane_paths --coverage` = 0 (9134 files). d the seven mutations above (each caught). e git
status empty after the commit; `git diff --name-status 319806c9 HEAD` = test files and the report
only; `git diff --stat 319806c9 HEAD -- services/api/app` empty.

## Round 5 (reading O13: the large-lot question of gap K3 not stated -> coverage withheld)

The producer's round-4 standing observation became an orchestrator ruling. Reading O13 (marked
in `result_ways._coverage_way` and here): `large_lot_threshold_met` is a fact the caller states;
None is "not stated", not "no". The module used to read None as falsy and could show a corner
lot's coverage as settled without knowing whether the lot is a large lot - a default standing for
a fact, which the packet forbids ("never filled by a default"). Now None -> coverage WITHHELD,
missing_information.

Source-line counts: `result_ways.py` 462 (was 448; +14 for the branch), `result_way_inputs.py`
413, `result_way_conditions.py` 320 (unchanged); tests `test_result_ways.py` 211,
`_input_states.py` 267, others <= 135. All under 600. No new numeric literal: the ast
no-zoning-number test still passes with literals == {100.0, 135.0} (the O13 reason is a string
and, like the existing K3 reason, does not write "30,000").

The branch and where it sits: in `_coverage_way`, a new `if inp.large_lot_threshold_met is None:`
placed AFTER the blanket rules, the lot-type-not-given check, the interior/through check and the
reach check, and just before the K20/shown tail. So the more fundamental reasons still win (a
blanket, a missing lot type, an interior/through lot, or a reach beyond the corner portion
withholds for its own reason first); the O13 gap fires only when coverage would otherwise be
shown. `True` is unchanged (withheld, work_owed, before the lot-type check, as today); `False` is
decided as today. No other result changes.

Test: `test_o13_large_lot_not_stated_withholds_coverage_missing_information` (replaces the round-4
`..._none_is_not_a_large_lot`): None -> coverage withheld, missing_information, the reason names
what was not stated ("was not stated", "recorded lot area"); False -> coverage shown; and every
OTHER result is identical between None and False (asserted field by field). Quotes the packet
("never filled by a default") and reading O13. The `True` test (`test_f5_large_lot_...`) stays.
The round-4 input-state table row for `large_lot_threshold_met` is updated: None now ACTS
(coverage withheld missing_information -> this test).

Point 3 - every other place a None / empty / missing entry is read by truthiness, and what it
does:
- `result_ways._coverage_way` `if inp.large_lot_threshold_met:` (+ the new `is None` branch) -
  FIXED this round; True unchanged, None now explicit withheld, False decided.
- `result_way_conditions.overlay_block` `(inp.overlay_support or {}).get(family)` then
  `if support is None:` -> a None mapping OR a family missing from the mapping -> WITHHELD "no
  independent reading" (SAFE, never shown). Pinned: test_s1_recorded_overlay_with_no_support (None
  mapping) and the NEW test_overlay_present_with_a_family_missing_from_the_mapping_is_withheld.
- `result_way_conditions.overlay_block` `code = f" (...)" if inp.commercial_overlay_code else ""`
  -> None code -> no code text; the overlay result is still withheld (presentation only). Pinned:
  test_overlay_code_none_with_overlay_present...
- `result_way_conditions.overlay_block` `owed = support.reading_owed or (...)` -> empty -> fallback
  owed-reading text; still withheld (presentation only). Pinned:
  test_overlay_not_supported_without_reading_owed...
- `result_way_conditions.area_condition` `outline ... if area.outline_sq_ft is not None else
  "another"` -> None outline -> "another" in the DISAGREES wording (presentation only). Pinned:
  test_disagree_with_no_outline...
- Everywhere else a missing/unknown/None fact is treated as WITHHELD or by an explicit
  `is None` / enum check, never as "no": area recorded None (the floor-area/unit deciders withhold
  before area_condition is called), area agreement None (explicit G3-F5 branch), street_reaches_within
  (None/empty/unknown reach -> no_outline withheld), _rear_yard_way (corner/reach/angle None ->
  no_outline withheld), _unit_standard_way (area None -> withheld), blanket_withhold (district None ->
  explicit withheld), condition_withhold (explicit Recorded enum). Found: only `large_lot_threshold_met`
  None let a result be shown on a not-given fact (now fixed); the overlay missing-family case was
  already safe (withheld) and is now pinned. Nothing else reported.

Mutation (a copy OUTSIDE the repository; the repo is never touched): the O13 branch neutered so
None falls through to "not large" again -> 1 meaningful fail,
test_o13_large_lot_not_stated_withholds_coverage_missing_information (plus the 3 invariant tests
that read result_ways via rw.__file__, an injection artifact of mutating result_ways itself).

Checks (DIRECT exit codes, round 5): a `ruff check .` = 0. b `pytest tests/scenario/three_answers`
= 0, 129 passed + 2 pre-existing skips (round 4 was 128; the None test was replaced and one
overlay-missing-family test added). c `pytest tests/contracts tests/spatial` = 0, 887 passed, 3
xfailed. d `modularity_check --check` = 0 (failures 0, 29 warnings; `grep result_way` = NONE);
`check_lane_paths --coverage` = 0 (9134 files). e the mutation above (caught). f git status empty
after the commit; `git diff --name-status 0943f5de HEAD` = the three-answers test files and the
report.

## Interface

Input records (`result_way_inputs.py`): `ResultWayInputs` holds `district`, `lot_type`
(`LotType`), `housing_kind`, `area` (`LotAreaFigures`: recorded sq ft, `AreaAgreement`, outline
sq ft - both figures for WORDING only, never a calculation), `reach`
(`ReachMeasurements`/`StreetReach`/`CornerReach`/`ReachValue` - a value or unknown, mirroring
lot-reach; `None` = no outline), the recorded conditions each `Recorded`
(`NOT_READ`/`ABSENT`/`PRESENT`): special purpose district, split lot, commercial overlay (+code),
inclusionary housing, flood zone, landmark/historic; the four no-data-source conditions each
`Checked` (`NOT_CHECKED`/`ABSENT`/`PRESENT`): waterfront, airport height, transit easement, near
a district line; `special_density` (`DensityKnowledge`); `large_lot_threshold_met`
(bool|None - the caller states the gap-K3 comparison, the module holds no area number); and
`overlay_support` (`Mapping[ResultFamily, OverlayResultSupport]` - the caller states per family
whether an independent overlay reading supports showing it, reading O5).

Way records: `Settled` (`{"way":"settled"}`); `Conditional(conditions: tuple[Condition,...])`
where `Condition(kind, assumption, settled_by)`; `Withheld(label, reason, gap_kind, resolved_by,
zr_sections)`; and `WholeAnswerNotAvailable(reason, reason_kind, gap_kind, resolved_by)` for an
answer whose every value is withheld. `ResultWays` carries the three answers (`AnswerWays`) plus
the five standalone results (rear yard, setback, the three unit limits).

Public function: `decide_result_ways(inp: ResultWayInputs) -> ResultWays`. Pure and
deterministic: no I/O, clock, randomness, rule evaluation or zoning number.

## Decision table (one line per gap and affected result)

| Gap | Results | Way in this milestone | gap_kind (O1) | Work-order sentence |
|---|---|---|---|---|
| K1 | max_lot_coverage (corner) | shown (settled if K20 absent, else conditional) when whole lot <=100 ft from each street line; else WITHHELD (reason carries the reach) | work_owed | "100 percent only when the recorded outline shows the whole lot within 100 ft of each street line ... Otherwise withheld." (S5 K1) |
| K2 | max_lot_coverage (interior/through) | WITHHELD until ZR 23-363 is read | work_owed | "Withheld until 23-363 is captured and read (step P1)." (K2) |
| K3 | max_lot_coverage (large lot) | WITHHELD when the caller states the lot meets the threshold | work_owed | "Withheld for lots of 30,000 sq ft or more." (K3; applied per O8) |
| K4 | rear_yard; building_option, floor_plate_area, floors | rear yard shown when whole lot <=100 ft of the corner point AND angle <=135 deg; else WITHHELD; footprint-dependent results WITHHELD | work_owed | "'No rear yard required' for the whole lot only when the whole lot is within 100 ft of the corner point ... Otherwise the rear yard is withheld, and so is everything that needs a footprint" (K4) |
| K5 | floor-area keys; unit limit | conditional on the recorded figure (never settled) when figures disagree / could-not-compare; no area condition when they agree | missing_information | "Where the figures disagree beyond the stated tolerance, every result that needs the area is conditional, never settled." (K5, section 6) |
| K6 | building_option (4 keys) | WITHHELD (answer not available) | work_owed | "Withheld: no building option is shown in this milestone." (K6) |
| K7 | (all reasons) | no reason contains "professional review"; a test rejects it | closed here | "a test rejects that phrase." (K7) |
| K8 | setback_above_base; floors above base | setback WITHHELD "not covered"; heights unaffected | work_owed | "The setback is withheld as 'not covered' ... The height limits themselves are table values and are not affected." (K8) |
| K9 | every residential result (overlay recorded) | supported -> decided as without overlay; not supported / none stated -> WITHHELD naming the owed reading | work_owed | "On a lot with a recorded overlay every residential result is withheld until the governing sections are captured and read independently." (K9) |
| K10 | every result | recorded present -> WITHHELD (owed); not read -> WITHHELD (missing info); absent -> stated as a fact | work_owed / missing_information | "One recorded: every result is withheld (owed). Not read: every result is withheld; a column that was not read is never taken as 'none'." (K10) |
| K11 | legal_unit_limit_standard | WITHHELD without evidence; conditional (user_statement) when the user states not-in-one; never settled | work_owed | "Without evidence the legal unit limit is withheld. If the user states ... conditional ... never settled." (K11) |
| K12 | max_lot_coverage, rear_yard | WITHHELD when the reach is not measured (no outline) | missing_information | "No outline: withheld." (K12) |
| K13 | unit qualifying affordable/senior | affordable WITHHELD; senior WITHHELD "not set by this formula" | work_owed | "Withheld for qualifying affordable housing; for qualifying senior housing 'not set by this formula'." (K13) |
| K14 | unit limit | labelled "standard residences"; other cases withheld | work_owed | "The limit is labelled 'new all-residential building'. Other cases are withheld." (K14) |
| K15 | (coverage, units, rear yard cite both sections) | supported via ZR 11-25 | closed here | "The result cites both sections." (K15) |
| K16 | floor-area composition | FAR allowance shown; gross/net composition WITHHELD (not shown this milestone) | work_owed | "What counts toward floor area is withheld as 'not covered'; no gross or net area is shown" (K16) |
| K17 | heights -> floors | height limits shown as table values; floors withheld (K6/K8) | work_owed (question) | "The height limits are shown as the table's limits. Anything that turns height into floors is withheld" (K17) |
| K18 | every result | recorded split -> WITHHELD; not read -> WITHHELD; not split -> stated as a fact | work_owed / missing_information | "Recorded 'split': every result is withheld. Not read: every result is withheld." (K18) |
| K19 | inclusionary->floor area; flood->heights; landmark->none | recorded present -> the results it can change WITHHELD; not read -> WITHHELD (missing info); landmark changes no zoning number | work_owed / missing_information | "Where one is recorded, the results it can change are withheld ... A landmark ... changes no zoning number" (K19, O7) |
| K20 | every zoning result | not checked -> conditional naming the conditions; one present -> every zoning result WITHHELD; all absent -> that part removed (heights then settled) | work_owed | "it is conditional, 'If none of these applies to this lot (not checked): ...' ... A result that cannot be supported even on that assumption is withheld." (K20) |

## Readings O1-O10 and where each is used

- **O1** gap-kind mapping: `result_way_inputs.REASON_KIND_BY_GAP` and every `Withheld.gap_kind`:
  information->missing_information; owed/question/"owed; question"->work_owed; evidence->missing
  information when a recorded fact was not read (K10/K18/K19 not-read, inclusionary/flood not-read),
  work_owed when a recorded condition cannot be handled (special district/split/inclusionary/flood
  present).
- **O2** withheld wins over conditional; conditions add up: `_blanket_withhold` withholds every
  result (special district/split present-or-not-read, a K20 condition present), a user's statement
  included; a shown value carries both the area and K20 conditions (`_floor_area_way`).
- **O3** a result computed from a withheld result is withheld and names it; from a conditional it
  carries the conditions: `building_option` (footprint from the withheld rear yard) is always
  withheld and names the rear yard; the floor-area/unit conditions add up.
- **O4** (COMPLETED round 2) recorded area the outline could not be compared with -> conditional
  on the recorded figure, kind `unchecked_condition` (the comparison was not made; nothing
  contradicts it, so `contradicted_record` does not fit); figures that DISAGREE stay
  `contradicted_record`; no recorded area -> withheld; outline never substituted. In
  `result_way_conditions.area_condition`, `result_ways._floor_area_way`, `_unit_standard_way`.
- **O5** overlay: the caller states per family whether a reading supports it; the module holds NO
  table: `_overlay_block` + `OverlayResultSupport`. A test scans the source for overlay-chapter
  section numbers (none present).
- **O6** one no-data-source condition present -> every zoning result withheld: `_blanket_withhold`.
- **O7** inclusionary/flood/landmark not read -> the results it can change withheld as missing
  information: `_condition_withhold`.
- **O8** K3 applied as written (coverage withheld for a large lot) though the merged step-P3 reading
  suggests the different maximum does not reach R6B: `_coverage_way` honours
  `large_lot_threshold_met`; this report records the note and changes nothing.
- **O9** the two legal measures (100 feet, 135 degrees), each with its capture id (below):
  `CORNER_PORTION_WITHIN_100_FT`, `REAR_YARD_WAIVER_WITHIN_100_FT`,
  `REAR_YARD_WAIVER_MAX_ANGLE_135_DEG`; used by `_coverage_way` and `_rear_yard_way`.
- **O10** anything the work order and these readings do not decide is withheld as work owed and
  listed below.

## Combinations left withheld under O10 (open questions for the reviewers)

1. **Special density area recorded as evidence that the lot is NOT in one.** The work order gives a
   way only for "not given" (withheld), "evidence it is in one" (withheld), and "user statement
   not in one" (conditional). It gives no settled/conditional path for recorded evidence of
   ABSENCE ("No source exists" for a special density area). The module WITHHOLDS the standard unit
   limit (work_owed) for `DensityKnowledge.EVIDENCE_NOT_IN_ONE` and lists it here. Reviewers to
   confirm or direct.
2. **`district` not given / `housing_kind` not given.** These are carried for wording and change no
   way in this milestone (one-district milestone, R6B; `housing_kind` is a design choice, rule 2).
   A district-less lot is not decided by the work order; the module does not specially withhold on
   it. Listed for reviewer confirmation.
3. **Commercial overlay NOT read.** The work order names the not-read rule for the special-district
   column (K10) but not explicitly for the overlay column. The module WITHHOLDS every residential
   result as missing information (K10 generalised + section 10 / R240: a column not read is never
   taken as 'none'). Listed for reviewer confirmation.

RESOLVED in round 2 (was open question 3): the `AreaAgreement.COULD_NOT_COMPARE` condition kind is
now `unchecked_condition` by the orchestrator's completed reading O4 (the comparison was not made;
nothing contradicts the figure). The test `test_s5_figure_that_could_not_be_compared_is_an_
unchecked_condition_o4` quotes both the reading and the contract's description of the kinds.

## The two legal measures (reading O9) with their capture ids

- **100 feet** - corner-lot portion (coverage, K1): snapshot `zr-12-10-lot-corner`, content digest
  `86b686b683e4ed37531319130ee49dc99a3cba3acbd41c27da2bccb2eb686a58`; captured words: "The portion
  of such zoning lot subject to the regulations for corner lots is that portion bounded by the
  intersecting street line and lines parallel to and 100 feet from each intersecting street line."
  Comparison: the whole lot is within 100 feet of each intersecting street line.
- **100 feet** - rear-yard waiver (K4): snapshot `zr-23-344`, content digest
  `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`; captured words: "no rear yard
  shall be required within 100 feet of the point of intersection of two street lines intersecting
  at an angle of 135 degrees or less." Comparison: the whole lot is within 100 feet of the point
  where the two street lines meet.
- **135 degrees** - rear-yard waiver angle (K4): same `zr-23-344` capture and words. Comparison:
  the two street lines meet at an angle of 135 degrees or less.

A test proves the ONLY numeric literals in both module files are `100.0` and `135.0` (ast scan).

## Where each test's expected outcome comes from (never the module)

- The WAY of each result is read from the work order's sentences, quoted beside each test
  (S1/H1/H2, S2/H3, S3/H4/H9, S4/H5, S5/H6+section 6, S6/H11, S7/H7, S8).
- The reach MEASUREMENTS are read through the loader from the four reach rows of
  `docs/reference-cases/R6B/cases/corner-reach.json` (`real-lot-reach`, `C1-reach`, `C2-reach`,
  `C3-reach`); the helper asserts every reach figure it uses against the loaded row's prose. No
  other reference row is read (the sibling task may supersede rows). The made-up lots' dimensions
  come from the work order's table C; the benchmark area figures (10,075 / 10,388 sq ft) and the
  corner angle (89.7 deg) come from the work order (L1/K5/L9).
- S7: each way object is validated against `$defs/value_state` (and whole-answer not-available
  against `$defs/answer_not_available`) of the BUNDLED schema via `jsonschema` over the repository
  registry.

## Modularity answers

- New focused modules only; no existing file grows. After the round-2 split EVERY file is under
  the 600-line warning threshold as `tools/modularity_check.py` counts source lines:
  `result_way_inputs.py` = 409 SLOC, `result_way_conditions.py` = 292 SLOC, `result_ways.py` =
  448 SLOC; the four test files are each well under the threshold.
- `tools/modularity_check.py --check` prints NO warning for any of these files (failures 0; a
  `grep result_way` over its output returns nothing). The split follows a real responsibility
  seam: the records (inputs, measures, vocabulary, way records) in `result_way_inputs.py`; the
  cross-result rules (K20/area/blanket/overlay + shared builders) in `result_way_conditions.py`;
  the per-result deciders and the public function in `result_ways.py`. `result_ways.py` re-exports
  the records so every test import still resolves (a compatibility facade).

## Checks (DIRECT exit codes; round-2 re-run)

- **a** `python -m ruff check .` (from services/api): **exit 0** - All checks passed.
- **b** `python -m pytest -q -p no:cacheprovider tests/scenario/three_answers`: **exit 0** - 98
  passed, 2 skipped (both pre-existing skips in test_competitor_error_guards_lane_a.py, unrelated).
- **c** `python -m pytest -q -p no:cacheprovider tests/contracts tests/spatial`: **exit 0** - 887
  passed, 3 xfailed. (tests/rules/reference_cases NOT run in this worktree per the round-2
  instruction; another task changed those files on the branch. Confirms the existing
  `tests/spatial/test_lot_reach.py::test_nothing_imports_the_module_yet` still passes - no module
  names `lot_reach`, which is why the reach records are the module's own.)
- **d** `python3 tools/modularity_check.py --check` (repo root): **exit 0** - failures 0, 29
  warnings; `grep result_way` over the output returns NOTHING (no warning names any of the three
  modules). `python3 scripts/lanes/check_lane_paths.py --coverage`: **exit 0** - 9132 files, each
  owned by one lane.
- **e (round 1, recorded for the history)** two mutation proofs against a mutated COPY outside the
  repository (a pytest plugin injects the mutant; the repo files are never touched): (1) a
  not-checked K20 condition counted as checked -> exit 1 (conditional results became settled, S1/
  S6/H3/H4/H9/S5/S8 failed); (2) a withheld-dependent building option shown -> exit 1 (S8-dependent
  /S1 failed). Round 2 did not re-run the mutation proofs (check e this round is git status/diff).
- **f** `git status --porcelain` empty after the commit and `git diff --name-status 85bca681 HEAD`
  shows only the allowed paths - reported in the producer return.

## Assumptions, limitations, doubts

- The gap-kind mapping (O1) and the dual-kind gaps (K1/K4/K11 = "owed; question" -> work_owed) are
  the orchestrator's reading, named in the code; the M5-T128 illustrative document used
  `missing_information` for the coverage example - that document is not the decision and O1 governs
  here. Reviewers to confirm.
- Three O10 combinations stay open (special-density evidence-not-in-one; district/housing-kind not
  given; overlay column not read); the fourth (could-not-compare kind) is resolved as reading O4.
- No reason, assumption, resolved_by or settled_by text contains "professional review" (H7/K7),
  proven by a test over every emitted way and a source scan across all three module files.
