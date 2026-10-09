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
