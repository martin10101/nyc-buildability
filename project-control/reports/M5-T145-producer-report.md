# M5-T145 - producers' report (assembled by the orchestrator from the five part reports, each unchanged below)

Task: the calculation modules of the first building option, one task of five parts. Four builders, each a rules-engineer agent in its own worktree. Parts A, C and B+D were built side by side from the claim head `f2fb2ec1`; the orchestrator read each first commit and sent each builder back ONCE before any review (rulings C12 to C18 in the packet say what and why); part E was built afterwards from the integrated head `2e6dde3ee`. Nothing here is connected to a reported result.

| Part | What | Main file | Commits on the branch |
|---|---|---|---|
| A | the measured area of a corner lot's corner portion | `services/api/app/spatial/corner_reach_area.py` | 48fa796d5 and ae848f24e |
| B | coverage by portion from two measured areas | `services/api/app/scenario/three_answers/lot_coverage_by_portion.py` | 342962533 and 2e6dde3ee (with part D) |
| C | the two buildings of the step-P6 method with their floor schedules | `services/api/app/scenario/three_answers/first_building_options.py` | ca3c3ad3a and ea2580bd4 |
| D | the preliminary apartment estimate's arithmetic | `services/api/app/scenario/three_answers/preliminary_apartment_estimate.py` | 342962533 and 2e6dde3ee (with part B) |
| E | the review register follows the four modules | `services/api/app/rules/review_register/register.json and its rendered pages` | 87d69ec2f |

The builders' run times are in the task's review record. The part reports follow, unchanged; each also stands as its own file `M5-T145-part-<letter>.md`.


---

## Part A report (unchanged)

# M5-T145 PART A producer report - corner-reach area measurement

Builder: rules-engineer (an AI agent). Part A of a four-part packet; this report covers PART A
only. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-ab4c71d79d7bffe04`.
Base: `f2fb2ec1edbe331ce0957ebb591f2374780a6205` (the claim head). No existing file changed; no
other part's file touched.

## Correction before review

A second commit (on top of `51b26bc5e2f9a665bf7bfc6b732eb4b579f157f9`) applies the orchestrator's
three corrections; the geometry is unchanged (the benchmark still lands on reading 13 and within
0.14 sq ft of reading 14):

1. The measurement now names NO kind of gap. The `_GAP` sentence ("This gap is a missing fact
   about the property's geometry.") was removed from every reason and from the docstring; like the
   sibling lot-reach module, this module measures and names no kind.
2. A machine-readable `state` code for every outcome, plus a `frontage_causes` field. `state` is
   one of six `STATE_*` constants (one measured, five distinct unknown states). `frontage_causes`
   is a tuple of `(street name, CAUSE_*)` pairs so a caller can tell a frontage that is not
   confirmed (`CAUSE_NOT_CONFIRMED`) from one that is not straight (`CAUSE_NOT_STRAIGHT`) without
   reading any text. Tests S5-S8 assert the codes; two tests were added (more-than-two streets;
   confirmed-vs-straight cause).
3. Two guards. (a) A distance of zero or less raises `ValueError` (in both the pure function and
   the measure entry). (b) The interior rest is set to zero only when a negative is rounding noise
   (bounded by `1e-6` of the outline area); a larger negative raises `ValueError` instead of being
   hidden. Extracted into `_resolve_rest` so it is unit-tested directly.

## What I built

New module `services/api/app/spatial/corner_reach_area.py` (pure, measurements only; it holds no
legal threshold and names no rule, section or consequence; the distance is passed in by the
caller). It stands beside the sibling lot-reach module (M5-T127) and follows its conventions. It
imports only the existing `site_geometry` package (labels, outline, rays, depth, parameters,
results); it does not import the lot-reach module, the rule engine or the scenario engine. Nothing
in the app imports it yet (asserted by a test).

Two layers:

1. Pure geometry: `area_within_distance_of_both(outline_vertices, line1, line2, distance_ft)
   -> (corner_area, rest_area)`. Each line is `(a point on it, its unit direction)`. The corner
   portion is found by a pure-Python half-plane clip (Sutherland-Hodgman): the outline is clipped
   to the points within `distance_ft` of line 1, then that result to the points within
   `distance_ft` of line 2; the side the lot lies on is chosen by the vertex of largest
   perpendicular offset, so the clip boundary (a line parallel to each street line) is placed
   correctly. Each half-plane is convex, so the clip is exact even for a non-convex outline. The
   corner area is the shoelace of the clipped ring; the rest is the outline's own area minus the
   corner (a tiny negative from rounding is treated as a measured 0.0). No clock, no I/O.
2. Site-geometry layer: `measure_corner_reach_area(outline, geometry, distance_ft)
   -> CornerPortionAreas`, a frozen dataclass of two `SourcedValue` fields (`corner_portion`,
   `interior_portion`), a `state` code and a `frontage_causes` tuple. It finds the two confirmed,
   straight street frontages the same way the sibling module does (frontage status confirmed;
   bend <= `SINGLE_STREET_MAX_BEND_DEG`; a single street line from the length-weighted mean of the
   frontage edges), confirms they meet at a corner (the site-geometry corner relation), then
   measures with the pure function and wraps the two areas in `tax_map_value` (`Approximate - tax
   map`, rounded to 0.01 sq ft).

States, their codes and their plain texts (each unknown is a `SourcedValue` with value `None`,
never a zero; no reason names a kind of gap):

- measured: `STATE_MEASURED`.
- outline refused or missing: `STATE_OUTLINE_REFUSED`; both unknown with the refusal reason.
- no confirmed straight frontage: `STATE_NO_CONFIRMED_STREET`; "... no corner to measure within N
  ft of both street lines: <per-frontage reasons>." (N is the caller's distance, not a constant in
  the source.)
- one confirmed straight frontage: `STATE_ONE_CONFIRMED_STREET`; "Only <street> has a confirmed,
  straight frontage, so there is no corner to measure within N ft of both street lines; the outline
  area is a known number but the corner/interior split is not."
- more than two confirmed straight frontages: `STATE_MORE_THAN_TWO_STREETS`; "More than two streets
  front the lot, so no single corner is measured within N ft of both street lines."
- two confirmed straight frontages that do not meet at a corner: `STATE_NOT_A_CORNER`; "<a> and <b>
  front the lot but do not meet at a corner, so there is no corner to measure within N ft of both
  street lines."

Every frontage that could not seed a street line is recorded in `frontage_causes` as a
`(street name, CAUSE_*)` pair - `CAUSE_NOT_CONFIRMED` for an unconfirmed frontage,
`CAUSE_NOT_STRAIGHT` for a bent one - so the "not confirmed" and "not straight" causes are told
apart by code, not text. The reason texts still name the cause in words too.

No returned text says captured, complies, feasible, validated, verified or legally correct (C7).
No legal figure or wording is quoted inside the module; the distance is caller-passed. The module
does NOT change the zoning-rule review register: no reported result changes in this task (C8).

## Scenarios and tests (one test per scenario)

| Scenario | Input state | Expected (and its source) | State code | Test name |
|---|---|---|---|---|
| S1 | right-angle corner, lot wider than the distance on one street | corner 8,000.00; rest 2,400.00; sum 10,400 (hand arithmetic) | (pure fn) | test_s1_right_angle_corner_lot_wider_than_the_distance |
| S2 | lot wholly inside the distance | corner 4,800.00; rest 0.00 as a MEASURED known value (not unknown) (hand arithmetic + measure path) | STATE_MEASURED | test_s2_lot_wholly_inside_the_distance_has_a_measured_zero_rest |
| S3 | 60-degree corner, longer than the distance on one street | corner 8,000.00 (80 x 100, perpendicular); rest = whole lot (9,006.66) - 8,000 (hand arithmetic) | (pure fn) | test_s3_non_right_angle_corner_distance_is_perpendicular |
| S4 | benchmark lot vs BOTH step-P6 readings | corner within 1.0 of 9,997.60 & 9,997.46; interior within 1.0 of 390.39 & 390.52; sum == 10,387.99 within 0.01 (parsed from step-p6-worked#real-lot-coverage-by-portion) | STATE_MEASURED | test_s4_benchmark_lot_within_tolerance_of_both_readings |
| S5 | no outline (refused) | both unknown (value None) with the refusal reason, never zero | STATE_OUTLINE_REFUSED | test_s5_no_outline_both_areas_unknown_never_zero |
| S6 | one confirmed straight frontage | both unknown: only one street confirmed straight; cause ("First Avenue", CAUSE_NOT_CONFIRMED) | STATE_ONE_CONFIRMED_STREET | test_s6_one_confirmed_straight_frontage_split_unknown |
| S7 | two streets not meeting at a corner (through lot) | both unknown: front the lot but not at a corner | STATE_NOT_A_CORNER | test_s7_two_streets_not_meeting_at_a_corner_split_unknown |
| S8 | a bent frontage | both unknown: the frontage is not straight; cause ("Bend Street", CAUSE_NOT_STRAIGHT) | STATE_NO_CONFIRMED_STREET | test_s8_bent_frontage_split_unknown |
| more-than-two | three confirmed straight frontages | both unknown: more than two streets front the lot | STATE_MORE_THAN_TWO_STREETS | test_more_than_two_confirmed_frontages_split_unknown |
| cause-apart | one unconfirmed frontage vs one bent frontage | the two causes are distinct codes (NOT_CONFIRMED vs NOT_STRAIGHT), told apart without text | (unknown states) | test_cause_tells_not_confirmed_from_not_straight |
| guard-distance | distance of 0.0 and -5.0 | ValueError | (raises) | test_distance_zero_or_less_raises_value_error |
| guard-rest | a rounding-noise negative rest vs a real negative | 0.0 for noise; ValueError for a real negative | (raises) | test_resolve_rest_clamps_rounding_noise_but_raises_a_real_negative |

Hygiene tests (not scenarios): `test_module_names_no_legal_rule_or_threshold` (no "100"/"80"/
"135", no "zr"/"zoning"/"coverage"/"12-10"/"23-362"/"yard", no rule/scenario imports, does not
import the lot-reach module - checked via the parsed import statements, not prose) and
`test_no_app_module_imports_corner_reach_area_yet`. Total: 14 tests in the file.

## Expected figures versus what the module returned

- S1: expected corner 8,000.00 / rest 2,400.00; module 8000.0 / 2400.0 (exact).
- S2: expected corner 4,800.00 / rest 0.00 (known); module 4800.0 / 0.0, interior label
  `Approximate - tax map` (a measured zero, distinct from unknown).
- S3: expected corner 8,000.00 / rest 1,006.66; module 7999.9972 / 1006.6628. The scenario's
  vertex (40, 69.2820) makes the 80-ft side 79.99998 ft long, so the clip is 7999.9972 - which is
  8,000.00 at the 0.01 sq ft output precision; the test tolerance is 0.01 sq ft. A wrong-axis
  measurement is off by thousands (mutation proof below).
- S4 (ruling C5): module corner 9,997.60, interior 390.39, sum 10,387.99.
  - corner gaps: 0.00 sq ft vs reading 13 (9,997.60); 0.14 sq ft vs reading 14 (9,997.46).
  - interior gaps: 0.00 sq ft vs reading 13 (390.39); 0.13 sq ft vs reading 14 (390.52).
  - sum 10,387.99 == the readings' outline area (10,387.99) to 0.01 sq ft.
  - Largest gap to EITHER reading is 0.14 sq ft, well within the 1.0 sq ft tolerance. C5 is
    satisfied; no STOP. The program matches reading 13 exactly and reading 14 within the readers'
    own spread; the tolerance was not widened and no reading figure was changed.
- S5-S8: both areas returned unknown (value None, label `Unknown - enter`) with the plain reasons
  above; never a zero.

## Mutation proofs (on temp copies OUTSIDE the repository)

Each harness reads the committed source, applies one mutation, loads the mutated copy from the
scratchpad (outside the repo) and runs the scenario assertion. All three mutants were killed
(EXIT=0):

1. Measured-geometry branch: change the SECOND clip to use `line1` instead of `line2` (clip one
   axis only). S1 corner becomes 10,400.0 (the whole lot) instead of 8,000.0 ->
   `test_s1_right_angle_corner_lot_wider_than_the_distance` goes RED.
2. Unknown/refusal branch: change the unknown path to return `tax_map_value(0.0, ...)` instead of
   `unknown_value(...)`. S5 `corner_portion.value` becomes 0.0 (label `Approximate - tax map`)
   instead of None -> `test_s5_no_outline_both_areas_unknown_never_zero` goes RED.
3. State codes: make the one-street branch return `STATE_NO_CONFIRMED_STREET` instead of
   `STATE_ONE_CONFIRMED_STREET` (two distinct states now share one code). S6 `state` becomes
   `no_confirmed_straight_frontage` -> `test_s6_one_confirmed_straight_frontage_split_unknown`
   (which asserts `state == STATE_ONE_CONFIRMED_STREET`) goes RED.

## Checks (each with its direct exit code)

All via `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, pytest
`-p no:cacheprovider`. From `services/api`:

- `python -m ruff check app/spatial/corner_reach_area.py tests/spatial/test_corner_reach_area.py`
  -> `All checks passed!` EXIT=0.
- `python -m pytest -q -p no:cacheprovider tests/spatial/test_corner_reach_area.py`
  -> `14 passed` EXIT=0.
- `python -m pytest -q -p no:cacheprovider tests/spatial tests/scenario/three_answers`
  -> `802 passed, 2 skipped` EXIT=0 (every existing test there passes unchanged; the 2 skips are
  pre-existing and unrelated).

From the worktree root:

- `python3 tools/modularity_check.py --check` -> `selected 740 files; failures 0; warnings 31`
  EXIT=0 (corner_reach_area.py is not among the warned files; ~290 SLOC, well under the 600 WARN
  threshold).
- `python3 scripts/lanes/check_lane_paths.py --coverage`
  -> `LANE COVERAGE PASS: 9698 file(s), each owned by exactly one lane.` EXIT=0.

Mutation harnesses: EXIT=0; all three mutants killed (geometry, unknown/zero, state code).

The full api suite was NOT run locally (CI runs it, per the brief).

## What I could not settle

Nothing blocking. One note: the benchmark S4 match (C5) was confirmed by running the module here -
corner/interior match reading 13 exactly and reading 14 within 0.14 sq ft, inside the 1.0 sq ft
tolerance. The tolerance pins no single figure; it requires the program's exact clip within one
hand-reader's spread of BOTH readings.


---

## Part B report (unchanged)

# M5-T145 part B producer report - by-portion lot coverage (ZR 23-362 / ZR 12-10)

Written by the PART B/D builder (an AI agent, role rules-engineer). This is a draft
reading, not professionally reviewed (ADR-007).

## What I built

`services/api/app/scenario/three_answers/lot_coverage_by_portion.py`: one pure
arithmetic module (no file/network access, no clock, no AI). It imports only
`dataclasses`; it imports no other part of this task and no engine file, and nothing
existing imports it (nothing it returns is reachable from a reported result yet).

- `CoverageByPortion` (frozen dataclass): `status` ('available' | 'not_known'),
  `corner_allowed`, `interior_allowed`, `footprint`, `corner_ratio`, `interior_ratio`,
  `formula`, `zr_sections` = ('ZR 23-362', 'ZR 12-10'), `measurement_basis`, `reason`,
  `missing_inputs`, `gap_kind`.
- `permitted_footprint_by_portion(corner_portion_area, interior_portion_area,
  corner_ratio=1.00, interior_ratio=0.80)`:
  - both areas present and non-negative -> status 'available'; `footprint =
    corner x corner_ratio + interior x interior_ratio`; no rounding; the available
    reason is written from the ratios ACTUALLY used (C16a).
  - either area `None` -> status 'not_known', every figure `None`, `missing_inputs` =
    the names of the missing areas, `gap_kind` = None (C12); the reason names which
    inputs are not known and which calculation supplies them, with no guessed cause.
  - a negative area, or a ratio outside 0 to 1 (C16b), -> `ValueError`.

The ratios are the legal figures of ZR 23-362 (capture `zr-23-362`): interior/through
80 percent, corner 100 percent. The 100-foot corner-lot distance (ZR 12-10, capture
`zr-12-10-lot-corner`) is carried as the documented module constant
`CORNER_LOT_DISTANCE_FT` - the value the later wiring step passes to the corner-reach
measurement (PART A). No legal figure or wording is quoted from memory. No returned
text says captured, complies, feasible, validated, verified or legally correct.

## Scenarios and tests

| Scenario | Input state | Expected (basis) | Test name |
|---|---|---|---|
| S9 | corner=0, interior=10,000, 1.00/0.80 | footprint 8,000.00 (made-up-footprint-a: 0.80 x 10,000) | `test_s9_made_up_footprint_a_interior_lot_all_eighty_percent` |
| S10 | corner=9,997.60, interior=390.39 | corner 9,997.60; interior 312.31; footprint 10,309.91 (real-lot-coverage-by-portion reading 13) | `test_s10_real_lot_coverage_by_portion_reading_13` |
| S11 | corner=9,997.46, interior=390.52 | corner 9,997.46; interior 312.42; footprint 10,309.88 (reading 14) | `test_s11_real_lot_coverage_by_portion_reading_14` |
| S12 | corner=5,000, interior=0 | footprint 5,000.00 (ZR 23-362 corner rule; scenario hand arithmetic) | `test_s12_corner_rule_whole_lot_within_corner_portion` |
| S13 | corner=None, interior=None | not_known; gap_kind None; missing_inputs=(corner_portion_area, interior_portion_area) (C12) | `test_s13_missing_portion_areas_not_known` |
| S14 | corner=-1, interior=390.39 | ValueError | `test_s14_negative_area_rejected` |
| C16a | interior_ratio=0.50 | reason says "50 percent", not "80 percent" | `test_c16a_available_text_follows_actual_ratios` |
| C16b | corner_ratio=1.5 / interior_ratio=-0.1 | ValueError | `test_c16b_ratio_out_of_range_rejected` |
| C16c (R147) | the scenarios' inputs | footprint <= corner area + interior area | `test_c16c_footprint_never_exceeds_sum_of_areas` |

Every expected figure is PARSED from `docs/reference-cases/R6B/cases/step-p6-worked.json`
(S9 from `made-up-footprint-a`; S10/S11 from `real-lot-coverage-by-portion`
source_reference) or is the scenario's own hand arithmetic (S12). No figure is retyped
and none comes from a run of the module.

## Expected vs returned (available scenarios)

- S9: corner 0.0, interior 8,000.0, footprint 8,000.0; round -> 8,000.00. MATCH.
- S10: corner 9,997.6, interior 312.312, footprint 10,309.912; round -> 9,997.60 /
  312.31 / 10,309.91. MATCH reading 13 (module keeps full precision - "no rounding";
  the test compares at the reading's 2-decimal precision, exactly equal).
- S11: corner 9,997.46, interior 312.416, footprint 10,309.876; round -> 9,997.46 /
  312.42 / 10,309.88. MATCH reading 14.
- S12: footprint 5,000.0; round -> 5,000.00. MATCH.
- S13: not_known, missing_inputs=(corner_portion_area, interior_portion_area),
  gap_kind None. S14/C16b: ValueError. C16a: "50 percent" in reason. C16c: footprint
  <= sum over all scenario inputs.

## Correction before review

The orchestrator's reading (rulings C12 and C16) was applied before any review, in a
second commit on top of the first:
- C12: a missing input now names NO kind of gap. Added `missing_inputs` (the names of
  all missing inputs); set `gap_kind` to None for the missing-input state; dropped the
  "they need the lot outline measured against the two street lines" cause (the reason
  now names the inputs and the corner-reach measurement that supplies them).
- C16a: the available reason is written from the ratios actually used (percentages
  derived from `corner_ratio`/`interior_ratio`), not a hardcoded 80 percent.
- C16b: a ratio outside 0 to 1 raises `ValueError`.
- C16c (D-090 R147): a new test asserts the footprint never exceeds the sum of the two
  areas over the scenarios' inputs.

Mutation proof for C12 (temporary copy outside the repository, `scratchpad/mut_b/`):
baseline `test_s13_gap_kind_none` passed (exit 0); changing the missing-input branch's
`gap_kind=None` to `gap_kind="a missing fact about the property"` made that test FAIL
(exit 1). A kind given to a missing input goes red. (The earlier footprint +/- mutation
also still goes red.)

## Checks (each with its direct exit code)

- `python -m ruff check` (the 4 files): `All checks passed!` RUFF_EXIT=0
- `python -m pytest .../test_lot_coverage_by_portion.py
  .../test_preliminary_apartment_estimate.py`: 20 passed FOCUS_EXIT=0
- `python -m pytest tests/spatial tests/scenario/three_answers`:
  807 passed, 2 skipped FOLDER_EXIT=0
- `python3 tools/modularity_check.py --check`: failures 0 MOD_EXIT=0
- `python3 scripts/lanes/check_lane_paths.py --coverage`:
  LANE COVERAGE PASS, 9698 files LANE_EXIT=0

All run with `/root/project/lanes-runtime/venv/bin/python`,
`PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider`. The full api suite runs in CI.

## Register and scope (ruling C8)

This task changes no existing file and is imported by none; no reported result changes,
so the zoning-rule review register is NOT changed by this task (its calculation entries
move in the later wiring step, which also adds the guards of backlog row DB-211).

## What I could not settle

Nothing blocking for PART B.


---

## Part C report (unchanged)

# M5-T145 PART C producer report — the two step-P6 buildings as pure functions

Produced by an AI agent (role rules-engineer), builder 2 of three. Pure calculation modules
for the first building option; nothing reachable from a reported result. Base/claim head
`f2fb2ec1edbe331ce0957ebb591f2374780a6205`.

## What I built

`services/api/app/scenario/three_answers/first_building_options.py` — pure, typed, no file,
network or clock access. Imports only `math` and `dataclasses`; imports no other part of the
packet and no engine file (it does NOT import or change `building_option.py`, the engine's
own stacker, which is a different method).

Types (frozen dataclasses):
- `StoreyRow` — `storey`, `floor_to_floor_ft`, `top_ft`, `plan_area_sqft`, `floor_area_sqft`,
  `running_total_sqft` (square feet; heights feet above the base plane).
- `FloorSchedule` — `building` ("A"/"B"), `fill_rule`, `status`, `reason`,
  `footprint_area_sqft`, `floor_area_allowance_sqft`, `storeys`, `storey_count`, `height_ft`,
  `total_floor_area_sqft`, `unused_floor_area_sqft`, `below_min_base`, `missing_inputs`
  (ruling C12), `gap_kind`.

Functions (the maximum building height is NOT an input — ruling C13: no storey above the
maximum base height is worked, so it could decide nothing):
- `building_a(footprint_area, floor_area_allowance, floor_to_floor_ft, min_base_ft,
  max_base_ft)` — the WIDEST footprint stacked to the floor-area maximum
  (`storey_count = floor(allowance / footprint)`), every storey the same footprint plan.
- `building_b(footprint_area, floor_area_allowance, floor_to_floor_ft, min_base_ft,
  max_base_ft)` — the FEWEST storeys reaching the minimum base height
  (`storey_count = ceil(min_base / floor_to_floor)`), the whole allowance spread evenly
  (`plan = allowance / storeys`), every storey the same plan. The footprint is a REQUIRED
  input of building B too (ruling C1): the plan must fit within it.

ONE-HEIGHT LIMIT (D-090 R542, "10 ft residential floors and 15 ft shop ground floors as
starting assumptions", editable): this module works ONE floor-to-floor height for every
storey, so a 15 ft shop ground floor (R542) is not worked here. The floor-to-floor height
stays a named design assumption in every returned text.

States and their texts:
- `status = "available"` — a worked floor schedule. The `reason` is a plain summary that
  NAMES the same-plan stack and the floor-to-floor height as design assumptions, not rules of
  law, and states `below_min_base` as a plain height fact only (no legal conclusion drawn —
  ruling C3).
- `status = "not_known"`, MISSING INPUT (ruling C12) — every figure `None`, `storeys = ()`,
  `gap_kind` is `None`, and `missing_inputs` lists the names of ALL inputs that are not known
  (not only the first). The plain text names what is not known and says no reason why (S20
  footprint; S21 allowance; the C12 test names both). Never a zero, never a default.
- `status = "not_known"`, METHOD'S OWN LIMIT — `gap_kind = "code not built"` (a building B
  plan that would not fit the footprint S29; a building A stack that would pass the maximum
  base height S30; a first full-footprint storey that already passes the allowance).
- An impossible numeric input (zero or negative footprint/allowance/height) raises
  `ValueError`; `None` (a missing input) is handled first and is not an error.

No returned text says captured, complies, feasible, validated, verified or legally correct.
Rulings honoured: C1 (footprint required for both buildings; plan must fit; S16/S19/S20/S29),
C2 (no storey above the maximum base height; S30), C3 (`below_min_base` a plain fact),
C12 (a missing input names no kind of gap; `missing_inputs` lists all; the text asserts no
cause), C13 (`max_building_ft` removed — it is not an input), C14/C17 (the 10 ft is the
owner's R542 starting assumption; the one-height limit is stated), C7 (plain texts; the
method's own-limit gap kind named), C8 (no existing file changed or importing this module; the
zoning-rule review register is NOT changed by this task because no reported result changes —
the register's calculation entries move in the wiring step, which also adds the DB-211 guards).
PART C decides nothing about which building an option shows (DB-210 (b), the owner's open
decision).

## Scenarios and tests (one test per scenario)

| Scenario | Input state | Expected (source) | Test name |
|---|---|---|---|
| S15 | footprint 8,000; allowance 20,000; f2f 10; min 30; max 45/55 | A: 2 storeys of 8,000, total 16,000, unused 4,000, height 20, below min base (made-up-building-a numbers_block) | `test_s15_made_up_building_a` |
| S16 | footprint 8,000; allowance 20,000 | B: 3 storeys of 6,666.67, total 20,000, unused 0, height 30, not below (made-up-building-b) | `test_s16_made_up_building_b` |
| S17 | footprint 10,309.91; allowance 20,150 | A: 1 storey, total 10,309.91, unused 9,840.09, height 10, below (real-building-a reading1) | `test_s17_real_building_a_reading13` |
| S18 | footprint 10,309.88; allowance 20,150 | A: 1 storey, total 10,309.88, unused 9,840.12, height 10, below (real-building-a reading2) | `test_s18_real_building_a_reading14` |
| S19 | footprint 10,309.91 and 10,309.88; allowance 20,150 | B: 3 storeys of 6,716.67, total 20,150, unused 0, height 30; same under both readings (real-building-b) | `test_s19_real_building_b_both_readings` |
| S20 | footprint None; allowance 20,150 | both not_known, `gap_kind` None, `missing_inputs`=("footprint_area",); no figure | `test_s20_missing_footprint_both_not_known` |
| S21 | footprint 8,000; allowance None | both not_known, `gap_kind` None, `missing_inputs`=("floor_area_allowance",); no "not available for this lot" | `test_s21_missing_floor_area_allowance_both_not_known` |
| C12 | footprint None; allowance None | both not_known, `gap_kind` None, `missing_inputs`=("footprint_area","floor_area_allowance") | `test_c12_missing_footprint_and_allowance_lists_both` |
| S29 | footprint 5,000; allowance 20,000 | B not_known (code not built: plan 6,666.67 > 5,000); A still worked | `test_s29_building_b_plan_would_not_fit_footprint` |
| S30 | footprint 2,000; allowance 20,000 | A not_known (code not built: 10 storeys, 100 ft > 45 ft max base) | `test_s30_building_a_stack_passes_max_base_height` |

Every EXPECTED value is parsed from `docs/reference-cases/R6B/cases/step-p6-worked.json`
numbers_block (never retyped, never from a module run). The settled envelope input the
scenarios state (max base 45) is passed as an input; the maximum building height is not an
input (ruling C13). Tolerance 0.01 sq ft = the reference's two-decimal precision; the module
keeps figures unrounded. `below_min_base` is asserted as the parsed
`height_ft < min_base_height_ft`.

## Expected vs returned (module run, for evidence only — never a test oracle)

| Scenario | Expected (reference) | Returned |
|---|---|---|
| S15 A | n2 h20 plans 8000,8000 rt 8000,16000 tot 16000 unused 4000 below=T | n2 h20 plans 8000,8000 rt 8000,16000 tot 16000 unused 4000 below=True |
| S16 B | n3 h30 plan 6666.67 rt 6666.67,13333.33,20000 tot 20000 unused 0 below=F | n3 h30 plans 6666.67× rt 6666.67,13333.33,20000.0 tot 20000 unused 0 below=False |
| S17 A | n1 h10 tot 10309.91 unused 9840.09 below=T | n1 h10 tot 10309.91 unused 9840.09 below=True |
| S18 A | n1 h10 tot 10309.88 unused 9840.12 below=T | n1 h10 tot 10309.88 unused 9840.12 below=True |
| S19 B (both) | n3 h30 plan 6716.67 rt 6716.67,13433.33,20150 tot 20150 unused 0 below=F | identical for 10309.91 and 10309.88 footprints |
| S20 A/B | not_known, no figure | not_known gap_kind None missing_inputs ("footprint_area",) storeys () |
| S21 A/B | not_known, no default | not_known gap_kind None missing_inputs ("floor_area_allowance",) |
| C12 A/B | not_known, both names | not_known gap_kind None missing_inputs ("footprint_area","floor_area_allowance") |
| S29 B / A | B not_known (code not built); A worked | B not_known gap "code not built"; A available n4 h40 tot 20000 |
| S30 A | not_known (code not built) | not_known gap "code not built" storeys () |

## Mutation proofs (temporary copy outside the repository)

Mutations applied to a copied module under the scratchpad (`…/scratchpad/mut/app/…`); the
repo file was never mutated. The harness imports the mutated `app` package and parses the real
case file. Baseline (clean copy): passed. Re-run this round against the corrected module.

| # | Branch mutated | Change | Test that went red |
|---|---|---|---|
| 1 | building A fill rule | `floor(` → `ceil(` the allowance/footprint division | `test_s15…` FAILED `assert 3 == 2` (storey_count) |
| 3 | building A max-base guard (C2) | disable `if height_ft > max_base_ft` | `test_s30…` FAILED (returned available, not not_known) |
| 4 | building B plan-fit guard (C1) | disable `if plan_area > footprint_area` | `test_s29…` FAILED (returned available, not not_known) |
| 5 | missing-input no-kind (C12, the new branch) | set `gap_kind=GAP_CODE_NOT_BUILT` for a missing input | `test_s20…` FAILED (`gap_kind` was not None) |

## Checks (each with its direct exit code)

| Check (from `services/api` unless noted) | Exit |
|---|---|
| `python -m ruff check` first_building_options.py + its test | 0 (All checks passed!) |
| `pytest -q -p no:cacheprovider tests/scenario/three_answers/test_first_building_options.py` | 0 (10 passed) |
| `pytest -q -p no:cacheprovider tests/spatial tests/scenario/three_answers` | 0 (798 passed, 2 skipped) |
| `python3 tools/modularity_check.py --check` (worktree root) | 0 (740 files; failures 0; my module not among the 31 pre-existing warnings) |
| `python3 scripts/lanes/check_lane_paths.py --coverage` (worktree root) | 0 (9698 files, each owned by one lane) |

Did NOT run the full api suite (CI's job).

## Correction before review

Three corrections from the orchestrator's reading, applied on top of commit 27271fa in one
more commit (same three files):
- C12 — a missing input names NO kind of gap. A not-known state caused by a missing input now
  sets `gap_kind = None` and lists every missing input in a new `missing_inputs` field; its
  plain text names what is not known and asserts no cause (the phrases "from the measured lot
  outline and the two street lines" and "not available for this lot" are removed). Only the
  method's own limit (S29, S30, a first storey that already passes the allowance) keeps
  `gap_kind = "code not built"`. Tests S20 and S21 now assert `gap_kind is None` and the exact
  `missing_inputs`; a new test `test_c12_missing_footprint_and_allowance_lists_both` checks
  both names are listed when both are missing.
- C13 — `max_building_ft` removed from both functions and from every test call; the docstring
  says the maximum building height is not used because no storey above the maximum base height
  is worked.
- C14/C17 — the docstring names D-090 row R542 as the source of the 10 ft starting assumption
  and states the one-height limit (one floor-to-floor height for every storey, so a 15 ft shop
  ground floor is not worked here). The returned texts keep calling the height a design
  assumption.

## What I could not settle

Nothing blocking. One note: building A `storey_count` uses `math.floor`, exact for the
scenario inputs (20000/8000, 20150/10309.91, 20000/2000); I added no float epsilon so as not
to change behaviour at an exact-integer boundary (none of the scenarios sit on one).


---

## Part D report (unchanged)

# M5-T145 part D producer report - preliminary apartment estimate arithmetic

Written by the PART B/D builder (an AI agent, role rules-engineer). This is a draft
reading, not professionally reviewed (ADR-007).

## What I built

`services/api/app/scenario/three_answers/preliminary_apartment_estimate.py`: one pure
arithmetic module (no file/network access, no clock, no AI). It imports only
`dataclasses`, `decimal` and `math`; it imports no other part of this task and no
engine file, and nothing existing imports it. It does NOT import PART B.

- `PreliminaryApartmentEstimate` (frozen dataclass): `status`
  ('available' | 'not_known'), `quotient_low`, `quotient_high` (two decimals, round
  half up), `quotient_low_unrounded`, `quotient_high_unrounded`, `whole_below_low`,
  `whole_above_low`, `whole_below_high`, `whole_above_high` (below = floor, above =
  ceiling of each quotient), `floor_area_sq_ft`, `share_low`, `share_high`,
  `apartment_size_sq_ft`, `formula`, `label`, `reason`, `missing_inputs`, `gap_kind`.
- `preliminary_apartment_estimate(floor_area_sq_ft, share_low=0.60, share_high=0.75,
  apartment_size_sq_ft=700.0)`:
  - available -> `quotient = floor_area x share / apartment_size` for each share; two
    decimals plus the unrounded quotients; `whole_below = floor`, `whole_above = ceil`.
    `label` = exactly "Preliminary capacity estimate" (C15a).
  - `floor_area_sq_ft` is `None` -> status 'not_known', every figure `None`,
    `missing_inputs` = ("floor_area_sq_ft",), `gap_kind` = None (C12), `label` = exactly
    "Not known" (C15a); the reason names the missing floor area and the building option
    (PART C) that supplies it, with no guessed cause.
  - `apartment_size_sq_ft <= 0`, a share outside 0 to 1, a low share above the high
    share, or a negative floor area -> `ValueError` (C15d); never divides by zero.

The dividend is the proposed building's floor area (D-090 R509); the legal maximum and
the legal dwelling-unit limit (`dwelling_units.py`) are kept separate. The share range
and the apartment size are the owner's PRELIMINARY ASSUMPTIONS (D-090 R540, R541): the
label is the owner's own words and does NOT carry "preliminary assumption"; every OTHER
text that names the share or apartment size (`formula`, `reason`) carries "preliminary
assumption" and the owner's descriptions (the share is an unvalidated sensitivity range
the user can change; 700 sq ft is a chosen starting apartment size on the HPD
measurement basis the user can change). No text calls the share/size law, measured,
typical, realistic, expected or validated, or calls the result a legal limit, a ceiling,
a dwelling-unit limit or a count (C15b; D-090 R545, R688, R700).

## Scenarios and tests

| Scenario | Input state | Expected (basis) | Test name |
|---|---|---|---|
| S22 | floor=20,150 | low 17.27, high 21.59; 17/18 and 21/22 (real-estimate-b) | `test_s22_real_estimate_b` |
| S23 | floor=16,000 | low 13.71, high 17.14; 13/14 and 17/18 (made-up-estimate-a) | `test_s23_made_up_estimate_a` |
| S24 | floor=20,000 | low 17.14, high 21.43; 17/18 and 21/22 (made-up-estimate-b) | `test_s24_made_up_estimate_b` |
| S25 | floor=10,309.91 and 10,309.88 | both low 8.84, high 11.05; 8/9 and 11/12 (real-estimate-a) | `test_s25_real_estimate_a_two_readings_same_two_decimals` |
| S26 | floor=None | not_known; gap_kind None; missing_inputs=(floor_area_sq_ft,); label "Not known" (C12) | `test_s26_missing_floor_area_not_known` |
| S27 | apartment_size=0 | ValueError | `test_s27_zero_apartment_size_rejected` |
| S28 | floor=20,150 | label "Preliminary capacity estimate"; other texts carry "preliminary assumption" + owner descriptions; no forbidden wording (C15a/b) | `test_s28_labels_and_separation_from_the_legal_limit` |
| C15c | floor=14,000, 0.50/0.75 | low 10.00 (below 10, above 10), high 15.00 (below 15, above 15) | `test_c15c_exact_whole_quotient_above_equals_below` |
| C15d | floor=-1 | ValueError | `test_c15d_negative_floor_area_rejected` |
| C15d | share_high=1.5 | ValueError | `test_c15d_share_outside_0_to_1_rejected` |
| C15d | share_low=0.80 > share_high=0.60 | ValueError | `test_c15d_low_share_above_high_share_rejected` |

Every expected figure for S22-S25 is PARSED from the `numbers_block` of the named rows
in `docs/reference-cases/R6B/cases/step-p6-worked.json`; no figure is retyped and none
comes from a run of the module. C15c uses values exact in binary floating point.

## Expected vs returned (available scenarios)

- S22: 17.27 / 21.59, whole 17/18, 21/22. MATCH real-estimate-b.
- S23: 13.71 / 17.14, whole 13/14, 17/18. MATCH made-up-estimate-a.
- S24: 17.14 / 21.43, whole 17/18, 21/22. MATCH made-up-estimate-b.
- S25: both floor areas 8.84 / 11.05, whole 8/9, 11/12. MATCH real-estimate-a.
- S26: not_known, missing_inputs=(floor_area_sq_ft,), gap_kind None, label "Not known".
- S27/C15d: ValueError. S28: label exact; formula/reason carry the labels + descriptions;
  no forbidden wording. C15c: 10.00 (10/10) and 15.00 (15/15) - ceiling equals floor for
  an exact whole quotient.

## Correction before review

The orchestrator's reading (rulings C12 and C15) was applied before any review, in a
second commit on top of the first:
- C12: a missing input now names NO kind of gap. Added `missing_inputs` =
  ("floor_area_sq_ft",); set `gap_kind` to None; the reason names the missing floor area
  and the building option (PART C) that supplies it, with no guessed cause.
- C15a: `label` is the owner's own words - exactly "Preliminary capacity estimate" when
  available and exactly "Not known" when not; the label does not carry "preliminary
  assumption".
- C15b: every other text that names the share or apartment size carries "preliminary
  assumption" and the owner's descriptions (sensitivity range / HPD measurement basis;
  the user can change), written from the values actually used.
- C15c: `whole_above_*` is the CEILING; an exact whole quotient has the same number
  below and above.
- C15d: negative floor area, a share outside 0 to 1, and a low share above the high
  share each raise `ValueError` (one test each), beside the existing zero-apartment-size
  guard.

Mutation proof for the label (temporary copy outside the repository,
`scratchpad/mut_d/`): baseline `test_label_available` / `test_label_not_known` passed
(exit 0); changing the available label from "Preliminary capacity estimate" to any other
value made `test_label_available` FAIL (exit 1). Any other label goes red.

## Checks (each with its direct exit code)

- `python -m ruff check` (the 4 files): `All checks passed!` RUFF_EXIT=0
- `python -m pytest .../test_lot_coverage_by_portion.py
  .../test_preliminary_apartment_estimate.py`: 20 passed FOCUS_EXIT=0
- `python -m pytest tests/spatial tests/scenario/three_answers`:
  807 passed, 2 skipped FOLDER_EXIT=0
- `python3 tools/modularity_check.py --check`: failures 0 MOD_EXIT=0
- `python3 scripts/lanes/check_lane_paths.py --coverage`:
  LANE COVERAGE PASS, 9698 files LANE_EXIT=0

All run with `/root/project/lanes-runtime/venv/bin/python`,
`PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider`. The full api suite runs in CI.

## Register and scope (ruling C8)

This task changes no existing file and is imported by none; no reported result changes,
so the zoning-rule review register is NOT changed by this task.

## What I could not settle

Nothing blocking for PART D.


---

## Part E report (unchanged)

# M5-T145 PART E producer report - the review register follows the four new calculation modules

Written by the PART E builder (an AI agent, role rules-engineer). This is a draft reading, not
professionally reviewed (ADR-007). I changed only the register's SOURCE DATA and rendered its pages
by its own process (`render_review_register.py --write`); I wrote no renderer or checker code, moved
no verdict, and touched no human-review field. Base/contract head
`2e6dde3ee15a1d3ff742701c5637bc2f3e1ff0ae`.

## The four new modules (M5-T145 parts A-D, already on the branch)

- A `services/api/app/spatial/corner_reach_area.py` - measures the corner-lot / interior-lot area split.
- B `services/api/app/scenario/three_answers/lot_coverage_by_portion.py` - applies the 100%/80% ratios.
- C `services/api/app/scenario/three_answers/first_building_options.py` - the two step-P6 buildings.
- D `services/api/app/scenario/three_answers/preliminary_apartment_estimate.py` - the estimate arithmetic.

Each exists as a pure module, is imported by nothing, and is connected to no reported result. The
committed results document (`recorded_215_16_northern_journey.json`) is UNCHANGED, so the program's
actual answer on every step is unchanged (withheld / not built). The journey test confirms this.

## Entry by entry (six calculation entries; S31 names four)

CHANGED (on the new-module path; revision 1 -> 2, one history event each, the new module(s) added to
`code_modules` so their identity is fingerprinted, automated_tests re-recorded at the new code
identity):

- `calc-lot-coverage-by-portion` (+A, +B; code identity d13b7093...). interpretation / exceptions /
  behaviour.planned / coverage_gap reworded: the by-portion split is now built as two pure modules
  but connected to no reported result; the engine still withholds `max_lot_coverage`.
- `calc-building-option-floor-stack` (+C; b76885b3...). Reworded: the two step-P6 buildings are built
  as a pure module, connected to no reported result; the engine's own generator is not built; the
  one-floor-to-floor-height limit (R542) stated.
- `calc-preliminary-apartment-estimate` (+D; fad72467...). Reworded: the estimate is built as a pure
  module, connected to no reported result; the document still reports it not built.
- `calc-first-building-option-complete` (+A,+B,+C,+D; dc2b0950...). interpretation / exceptions /
  behaviour / gaps and the "code not built" closing row reworded to say the component modules now
  exist but are wired to nothing; every one of the six step verdicts is UNCHANGED; the closing kind
  stays "code not built" (it must match the program's own gap_kind, which did not change); DB-210
  still named.

NOT CHANGED substantively (off the new-module path - no new module implements them, no narrative or
revision change): `calc-floor-area-allowance`, `calc-legal-dwelling-unit-limit`. Their recorded
test-file digest was resynced only because the ONE shared linked test file had an assertion moved
(see below); no revision moved and no history line was added for them.

## Coverage gaps before -> after (register-wide list)

9 gaps -> 10 gaps; none dropped. Reworded the three on-path gaps (building-option, lot-coverage,
preliminary-estimate) from "not built" to "built as a pure module but connected to no reported
result". Added one NEW gap the new modules open: part C works one floor-to-floor height for every
storey (R542 10 ft), so a 15 ft shop ground floor is not worked. The three-answers-engine gap
(index 0) and the M5-T144 gap (both required by the checker) are unchanged.

## History lines appended (calculations_history, seq 7-10, all 2026-10-09, implementation_changed)

7 calc-lot-coverage-by-portion rev 2; 8 calc-building-option-floor-stack rev 2; 9
calc-preliminary-apartment-estimate rev 2; 10 calc-first-building-option-complete rev 2. No earlier
line (seq 1-6) changed.

## Test-file assertion changed (one; S32)

`test_calculations_history_is_append_only_and_separate` pinned the history length to the number of
calculations (`== list(range(1, len(CALCS) + 1))`). Appending revision-2 history events legitimately
grows the history past one-per-entry, so I changed that single assertion to the real invariant: the
seq is contiguous from 1 to `len(calculations_history)`. No other assertion changed; the renderer and
checker are untouched. Because all six calc entries link this one file, editing it forced a
test-file-digest resync on all six `automated_tests` blocks (new digest
eb029a9a...); the four changed entries absorb it in their revision bump, the two off-path entries get
the digest-only resync. Without the resync the checker would demand their status read "Not run".

## S33 mutation (temporary copy OUTSIDE the repository)

Copied the worktree (minus .git) to the scratchpad; baseline `--check` PASSED. Appended one comment
line to `first_building_options.py` in the copy; `--check` FAILED with 2 issues, each naming the
changed module: "calc-building-option-floor-stack: code module .../first_building_options.py content
changed (sha256 8a9a8d02... != recorded 26a92c40...); the register must be updated in the same change
(new revision, history event)" and the same for calc-first-building-option-complete. The committed
register `--check` passes (exit 0). The drift is caught and names the module, as S31/S33 require.

## Checks (each with its direct exit code)

All via `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, pytest
`-p no:cacheprovider`.

- (services/api) `python -m ruff check .` -> All checks passed! RUFF_EXIT=0
- (services/api) `pytest ... test_zoning_rule_review_register.py test_zoning_rule_review_register_calculations.py tests/rules/reference_cases tests/journey` -> 187 passed, 1 warning EXIT=0
- (worktree root) `render_review_register.py --check` -> register check PASSED (no issues) CHECK_EXIT=0
- (worktree root) `tools/modularity_check.py --check` -> failures 0 (pre-existing warnings only, none my files) MOD_EXIT=0
- (worktree root) `scripts/lanes/check_lane_paths.py --coverage` -> LANE COVERAGE PASS, 9699 files LANE_EXIT=0
- (worktree root) `git diff --stat 2e6dde3e -- docs/zoning-rule-review/rules` -> empty (the 23 rule pages byte-identical) EXIT=0
- S33 temp-copy `--check`: baseline PASS (exit 0); after one-byte mutation FAIL naming the module (exit 1).

The full api suite was NOT run locally (CI runs it).

## Scope / what I could not settle

Files changed: register.json; the 2 rendered index pages (REGISTER.md, HISTORY.md); the 6
calculations/*.md pages and 6 evidence/*.txt logs (produced/updated by the register's process); the
one test assertion. No module, no renderer/checker code, no rule entry or page, no results fixture,
no reference case touched; every entry still reads "Not reviewed". Nothing blocking.
