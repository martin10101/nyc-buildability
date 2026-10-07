# M5-T129 producer report - decide how each result appears (settled, conditional, withheld)

Producer: scenario-optimization-engineer (builder). Role: build a PURE decision module in NEW
files that nothing calls yet; it computes no zoning number. Contract/claim-seam head reset to:
`5f8b78ce452b4a214cceeb314372f6968373acf6`. Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-a0f3c57f1810681dc`.

Files (all NEW / placeholder-replacing; no existing file changed):
- `services/api/app/scenario/three_answers/result_way_inputs.py` - the records: input records
  (enums + `ResultWayInputs`), the reach records (mirroring M5-T127, NOT importing it), the two
  legal measures of reading O9, the result vocabulary (keys, labels, gap/condition kinds) and
  the way (output) records.
- `services/api/app/scenario/three_answers/result_ways.py` - the decision logic and the ONE
  public function; re-exports the records (a compatibility facade), so its public interface is
  complete.
- `services/api/tests/scenario/three_answers/test_result_ways_lib.py` - shared test builders
  (reads the reach rows through the loader; no test functions).
- `test_result_ways.py` (invariants: S7, S9, H7), `test_result_ways_benchmark.py` (S1, S6),
  `test_result_ways_corner_interior.py` (S2, S3), `test_result_ways_facts_area_overlay.py`
  (S4, S5, S8).

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
- **O4** recorded area with no outline to compare -> conditional on the recorded figure (never
  settled); no recorded area -> withheld; outline never substituted: `_area_condition`,
  `_floor_area_way`, `_unit_standard_way`.
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
3. **`AreaAgreement.COULD_NOT_COMPARE` condition kind.** The work order makes it conditional on the
   recorded figure (O4, section 6) but section 0 lists only three conditional kinds, none of which
   is "could not be compared". The module uses `contradicted_record` (the only recorded-figure
   kind) with honest wording ("the tax-map outline area could not be computed to compare it").
   Reviewers to confirm the kind choice.
4. **Commercial overlay NOT read.** The work order names the not-read rule for the special-district
   column (K10) but not explicitly for the overlay column. The module WITHHOLDS every residential
   result as missing information (K10 generalised + section 10 / R240: a column not read is never
   taken as 'none'). Listed for reviewer confirmation.

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

- New focused modules only; no existing file grows. `result_way_inputs.py` = 409 SLOC;
  `result_ways.py` = 664 SLOC. The input records, reach records, two legal measures, result
  vocabulary and way records were extracted into `result_way_inputs.py` and the tests split into
  four files to keep each under the thresholds.
- `result_ways.py` sits in the 600-750 band (WARNING, not the hard limit; the modularity check
  passes, failures 0). **Cohesion justification:** it is one responsibility - decide the way of
  each result - and `allowed_paths` for this task permits exactly two app modules
  (`result_ways.py`, `result_way_inputs.py`), so it cannot be split into a third module without
  leaving scope; everything that is data/record has already been moved to the records module, and
  the remaining lines are decision logic plus the per-result reason / resolved_by text the contract
  requires. Flagged for the reviewers.

## Checks (DIRECT exit codes)

- **a** `python -m ruff check .` (from services/api): **exit 0** - All checks passed.
- **b** `python -m pytest -q -p no:cacheprovider tests/scenario/three_answers`: **exit 0** - 98
  passed, 2 skipped (both pre-existing skips in test_competitor_error_guards_lane_a.py, unrelated).
- **c** `python -m pytest -q -p no:cacheprovider tests/contracts tests/spatial
  tests/rules/reference_cases`: **exit 0** - 943 passed, 3 xfailed. (Confirms the existing
  `tests/spatial/test_lot_reach.py::test_nothing_imports_the_module_yet` still passes - the module
  does NOT import or name `lot_reach`, which is why it defines its own reach records.)
- **d** `python3 tools/modularity_check.py --check` (repo root): **exit 0** - failures 0, 30
  warnings (incl. the `result_ways.py` warn-band signal above). `python3
  scripts/lanes/check_lane_paths.py --coverage`: **exit 0** - 9127 files, each owned by one lane.
- **e** two mutation proofs, run against a mutated COPY outside the repository (a pytest plugin
  injects the mutant under the real module name; the repo files are never touched):
  - (1) make a not-checked K20 condition count as checked (`_is_unchecked` -> False): **exit 1**,
    13 failed. Meaningful behavioural failures: test_s6_not_checked_makes_every_zoning_result_
    conditional_not_settled, test_s1a/test_s1b, test_h3_c1/test_h3_c2, test_h4_interior...,
    test_h9_statement..., test_s5_figures_that_agree..., test_s8_supported... (conditional results
    became settled). (3 further failures are incidental: the invariant tests read the module via
    `rw.__file__`, which the injection points at the scratchpad copy.)
  - (2) make a result that depends on a withheld result be shown (`_building_option_withheld` ->
    False): **exit 1**, 6 failed. Meaningful: test_s8_a_dependent_result_names_what_it_depends_on,
    test_s1a, test_s1b (building option became available). (3 incidental, as above.)
- **f** `git status --porcelain` and `git diff --name-status <contract-head> HEAD` - run after the
  single commit; the result (only the allowed paths, all added except the report which replaces a
  placeholder; working tree clean) is reported in the producer return.

## Assumptions, limitations, doubts

- The gap-kind mapping (O1) and the dual-kind gaps (K1/K4/K11 = "owed; question" -> work_owed) are
  the orchestrator's reading, named in the code; the M5-T128 illustrative document used
  `missing_information` for the coverage example - that document is not the decision and O1 governs
  here. Reviewers to confirm.
- The four O10 combinations above are withheld, never guessed; they are the open questions.
- `result_ways.py` is in the modularity warning band (664 SLOC) for the reason recorded above; a
  reviewer decision on whether a path-exact exception or a different split is wanted.
- No reason, assumption, resolved_by or settled_by text contains "professional review" (H7/K7),
  proven by a test over every emitted way and a source scan.
