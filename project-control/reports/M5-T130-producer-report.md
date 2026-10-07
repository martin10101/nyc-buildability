# M5-T130 producer report — carry the lot's recorded facts to the decision module

Producer: scenario-optimization-engineer (builder). NEW files only, with the one scope-correction
exception (two guard tests). The emitted results document does not change; nothing under
`services/api/app` imports the new modules except this task's own files. Contract/claim-seam head
reset to `6979d27d96068de2130d2624854cf125117d6032`. Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-a46ef10d91f2dcbda`.

## Files (source-line counts by `wc -l`; all well under the 600 warning threshold)

- `services/api/app/scenario/three_answers/result_way_facts.py` (291) — the recorded city-record
  columns as three-state `Recorded` facts with provenance (reading O14).
- `services/api/app/scenario/three_answers/result_way_bridge.py` (375) — the area comparison (O15),
  the large-lot answer (O17), the reach adaptation, the reading of the evaluator inputs, and the ONE
  entry function `gather_result_ways` that returns the ways beside the gathered facts.
- `services/api/app/scenario/three_answers/result_way_bridge_overlay.py` (102) — the overlay-support
  table (O16), tied by test to the reference rows.
- tests: `test_result_way_facts.py` (159), `test_result_way_bridge.py` (372),
  `test_result_way_bridge_overlay.py` (84).
- the two guard tests, each in its ONE function only:
  `test_result_ways.py::test_only_task_m5_t130_bridge_and_facts_modules_import_the_decision_module`
  and `test_lot_reach.py::test_only_task_m5_t130_bridge_imports_the_module` (renamed; the permitted
  callers are a literal list; the test still fails when any other app file names the module —
  proved by mutations M-F* / the import battery below). Nothing else in either file changed.
- `project-control/reports/M5-T130-producer-report.md` (this file).

`tools/modularity_check.py --check` names none of the new files (exit 0).

## The entry function

`gather_result_ways(*, evaluator_inputs, profile, outline, geometry, housing_kind,
special_density_statement=None) -> GatheredResult`. It gathers the recorded columns (O14), the
reach (via `measure_lot_reach`, adapted), the two area figures (O15), the large-lot answer (O17),
the overlay support (O16), the density from a user's statement (never a fact), builds
`ResultWayInputs`, calls `decide_result_ways`, and returns `GatheredResult(ways, inputs, recorded,
area_statement, large_lot, source_facts, held_back)` — the ways beside the gathered facts and their
provenance (dataset, column, lot id, fetch record; the lot type / district / area with their fact
ids).

## Reading O14 — how "recorded as absent" and "not read" are told apart (with proof)

They CAN be told apart, from the connector's own record of the fetch, which the property profile
carries through. The PLUTO connector (`pluto_soda.fetch_by_bbl`) asks for the whole record and
records in `absent_columns` every one of its 108 known columns the served row omitted (SODA
null-omission); the profile builder carries those omissions, and the shared reader
`read_pluto_value` surfaces a served-empty column as `(None, <the PLUTO fetch's source>, "PLUTO has
no <column> value for this lot.")`. The fetch source is present **only** when a PLUTO fetch is in
the profile's `reproducibility` (`source_id == PLUTO`). So:

- served empty, fetch source present → `Recorded.ABSENT` (wording: the city's records list none —
  never "the lot has none"; work order K10/K18);
- the same sentence with **no** fetch source, or no profile, a failed fetch or no row → `NOT_READ`;
- a served-but-untrusted value (a conflict / duplicate / connector-drift signal) → `NOT_READ`
  (never guessed);
- `splitzone` is a checkbox served explicitly as true/false, so a served `false` is a real recorded
  "not split" → `ABSENT` (exactly as `map_based_rules._split_by_district_line` reads it).

Proof, run offline on the recorded benchmark profile (`build_property_profile(replay_pluto())`):
every map-based column except `overlay1`/`splitzone` is served empty with a live fetch source
(`spdist1/2/3`, `overlay2`, `mih_opt1-4`, `firm07_flag`, `pfirm15_flag`, `landmark`, `histdist` →
`value=None, source=present, problem="PLUTO has no … value for this lot."`); `overlay1="C2-2"`;
`splitzone=false`. The hand-built S2 battery proves all four per-column states (value / served-empty
with source / no fetch source / untrusted) and the three condition states (present / absent / not
read); the mutation M-F1 flips the source test and turns the benchmark's absent columns into
"not read" — caught.

## What the entry function returns for the benchmark lot, result by result (beside work order H2)

Gathered facts: overlay recorded PRESENT (code C2-2); special purpose district, split lot,
inclusionary housing, flood zone, landmark all ABSENT. Reach (measured, equal to the corner-reach
reference row `real-lot-reach`): 99.97 ft (Northern Boulevard), 103.93 ft (215 Place), corner
144.60 ft, angle 89.7°. Two area figures: recorded 10,075 sq ft vs outline 10,387.99 sq ft →
DISAGREE (O15). Large-lot: False (10,075 < 30,000; O17).

| Result | Way (entry function) | H2 expectation | Match |
|---|---|---|---|
| floor-area figures (4 keys) | Conditional (recorded area + the four unchecked conditions) | H1: conditional | yes |
| height limits (6 keys) | Conditional (the four unchecked conditions) | H1: conditional | yes |
| max lot coverage | Withheld; reason carries "103.93 ft from the 215 Place street line" | H2: withheld, reason carries 103.93 ft | yes |
| rear yard | Withheld | H2: withheld | yes (way); reason differs — see held-back #1 |
| setback above base | Withheld ("not covered") | H2: setback "not covered" | yes |
| building option (4 keys) | Withheld | H2: withheld | yes |
| legal unit limits (3) | Withheld | H2: qualifying affordable/senior "not known" | yes |

Never a zero: no way carries a number (asserted — no `value` key in any `to_value_state()`).

## Readings O15–O18 as applied

- **O15 (area tolerance).** No tolerance invented: AGREE only when the outline area, rounded to the
  whole square foot, equals the recorded figure; else DISAGREE; no outline → could-not-compare; no
  recorded area → the outline never stands in (`agreement=None`). The rule is returned as a plain
  statement with its result (`GatheredResult.area_statement`). A wider tolerance needs recorded lots
  to rest on and is owed work (backlog DB-173).
- **O16 (overlay).** A table in app code (`result_way_bridge_overlay`) states per family whether an
  independent reading supports showing it under a C2-2 overlay within R6B, each entry naming the
  current reference row it rests on (floor area ratio, lot coverage → `step-p4-worked`; base/building
  height, setback, dwelling units → `overlay-reading`; rear yard → `step-p4-worked`, NOT supported).
  App code never reads `docs/` at run time; test `test_result_way_bridge_overlay` reads those rows
  through the loader (which refuses a superseded row), asserts each is a value row that says "same as
  plain R6B", and that a family is supported exactly when its row carries no standing condition — the
  rear-yard row carries one reading's caveat, so it is not supported. Any other code or district →
  the caller returns None → the decision module withholds every residential result.
- **O17 (large lot).** Computed from the recorded area against the ONE figure held here from the
  captured text of ZR 23-362 (`LARGE_LOT_THRESHOLD`: 30,000 sq ft, snapshot `zr-23-362`, digest
  `f8370a389…`, quoted words); no recorded area → "not stated". K3 applied as the work order writes
  it (see held-back #2 for the DB-168 caveat).
- **O18 (contradiction not resolved here).** The entry function reads an evaluator-inputs document
  the builders already produced, which fails closed on two sources that disagree at the same rank, so
  this piece never runs on such a conflict.

## L1 — every place a missing value is handled, and what it does

- district None → blanket withhold (missing information); lot type unrecognised/absent → None (held
  back / `no_lot_type` withhold); recorded area None → floor area & unit limit withheld (missing
  information), large-lot "not stated"; outline None → reach None → coverage & rear yard
  `no_outline` withheld, area could-not-compare; geometry None → reach None; each recorded column
  absent-vs-not-read decided by O14 (no truthiness — explicit enum states); density None → "not
  given"; overlay code/district mismatch → None (every residential result withheld). No `if x:` on a
  value that may be unknown; a served checkbox `False` / numeric `0` is a recorded absence, not
  "present" and not a default.

## Input-state table (L2 — state → outcome → test that pins it)

Rewritten from the round-2 sweep (section below). A test is named only if it SUPPLIES that state
and ASSERTS the outcome. Two round-1 lines were overstated (lot type interior/through; the reach's
unknown-preservation) and are corrected here; the tests that now supply those states are named.

| Input | State | Outcome | Test |
|---|---|---|---|
| recorded column | served empty + fetch | ABSENT | test_every_column_served_empty… |
| recorded column | no profile / no fetch source | NOT_READ | test_no_profile…, test_served_empty_without_a_recorded_fetch… |
| recorded column | served value | PRESENT (+ overlay code) | test_recorded_values_are_present… |
| recorded column | served-but-untrusted | NOT_READ | test_a_served_but_untrusted_value…, test_one_untrusted_column… |
| splitzone | false / true | ABSENT / PRESENT | test_split_zone_false… |
| flag column (mih/firm) | false / zero | ABSENT | test_a_falsy_flag_is_absent… |
| area | outline rounds to recorded | AGREES | test_area_rule_s3 |
| area | differ | DISAGREES (both carried) | test_area_rule_s3 |
| area | no outline | COULD_NOT_COMPARE | test_area_rule_s3, test_outline_missing_while_geometry_present |
| area | no recorded area | outline never stands in | test_area_rule_s3, test_missing_inputs… |
| large lot | ≥ / < 30,000 / None | True / False / not stated | test_large_lot_answer_o17 |
| density | None / states-not-in-one / states-in-one | not given / conditional / held back | test_user_statement…, test_density_statement_that_claims_in_one… |
| lot type | corner | CORNER | test_benchmark_lot_s1, test_read_site_inputs_states |
| lot type | interior / through | INTERIOR / THROUGH, nothing held; coverage withheld (K2) | test_interior_and_through_lot_types_are_mapped_f2, test_interior_and_through_lots_withhold_coverage_per_k2_f2 |
| lot type | unrecognised / absent | not given (held back) | test_read_site_inputs_states, test_missing_inputs… |
| reach | known (benchmark) | measured, carried | test_benchmark_lot_s1 |
| reach | unknown street / corner / angle | stays unknown, never a zero | test_adapt_reach_keeps_an_unknown_measurement_unknown_f1 |
| reach | geometry present, a frontage/corner unknown | coverage + rear yard withheld (missing info), no zero | test_unknown_reach_withholds_coverage_and_rear_yard_f1 |
| outline / geometry | outline None, geometry present | area could-not-compare; no street-line reach | test_outline_missing_while_geometry_present |
| outline / geometry | outline present, geometry refused | reach unknown; coverage + rear yard withheld | test_outline_present_while_geometry_refused |
| outline / geometry | both None | reach None; area could-not-compare | test_missing_inputs… (no outline) |
| district | absent | blanket withhold | test_missing_inputs… |
| district | other than R6B (through entry) | every result withheld | test_district_other_than_r6b_withholds_every_result |
| evaluator_inputs | None / no "inputs" key / "inputs" not a list | every value not given | test_evaluator_inputs_shape_states |
| lot area value | not a number | not given | test_non_numeric_lot_area_is_carried_as_not_given |
| K20 conditions | always NOT_CHECKED (no parameter can change) | conditional naming all four | test_benchmark_conditional_names_all_four_unchecked_conditions_f3 |
| overlay support | overlay present, C2-2 within R6B | per-family table consulted | test_benchmark_lot_s1, test_result_way_bridge_overlay |
| overlay support | overlay present, code ≠ C2-2 | None → every residential result withheld | test_overlay_code_other_than_c2_2_withholds_residential_results |
| overlay support | overlay absent / not read | not consulted / blanket | test_missing_inputs… (no profile) |
| overlay code | PRESENT always carries a code | — (PRESENT-without-code cannot arise through the bridge; `_code_of` returns the served value) | n/a — reported, not a bridge branch |
| housing_kind | any / None | pass-through, no branch | test_benchmark_lot_s1 (no distinct branch) |
| texts battery | every returnable text (incl. K20-present) | no internal name / capture claim | test_every_text_a_user_may_see_is_plain… |

## Points the packet / work order did not decide (held back)

1. **Benchmark rear-yard reason.** O16 holds the rear yard NOT supported under a recorded overlay, so
   on the benchmark the overlay-reading-owed withhold fires before the 144.60-ft-beyond-corner reason.
   The WAY matches H2 (withheld); the REASON is "an independent reading of the commercial-overlay
   rear-yard rule … is owed", not the 144.60-ft reach. Flagged for reviewers.
2. **K3 breadth (DB-168).** O17 applies gap K3 as the work order writes it ("30,000 square feet or
   more"); the merged ZR 23-362(b) reading suggests that maximum reaches only eligible sites (ZR
   23-434) and so may not arise for a plain R6B lot. Applied as written, recorded here, no result
   changed on it.
3. **A user's statement that the lot IS in a special density area** has no decided path → held back
   (carried as "not given"); only "not in one" has a path (conditional).
4. **An unrecognised lot-type string** → carried as "not given" (held back), never guessed.
5. **A conversion or a mixed building (K14).** This piece has no fact for it; the piece that emits
   owns it (reading O12 / DB-172 d). The housing kind is passed through unchanged (DB-172 e: it
   changes no result's way).

## Counts

Input states acted on: ~16 clusters (table above), each pinned by a named test. Tests: 25 in the
three new files + the 2 renamed guard tests = 27. Mutation proofs: 8, all caught.

## Checks (DIRECT exit codes; `/root/project/lanes-runtime/venv/bin/python`, `-p no:cacheprovider`,
`PYTHONDONTWRITEBYTECODE=1`, from `services/api` unless noted)

- **a** `python -m ruff check .` → **exit 0** ("All checks passed!").
- **b** `python -m pytest -q tests/scenario/three_answers tests/spatial/test_lot_reach.py` →
  **exit 0**, 169 passed, 2 skipped (both pre-existing skips in
  `test_competitor_error_guards_lane_a.py`). Mine: 25 (the three new files) + the 2 renamed guards.
- **c** `python -m pytest -q tests/contracts tests/journey tests/spatial tests/scenario/three_answers
  tests/rules/reference_cases` → **exit 0**, 1107 passed, 2 skipped, 3 xfailed (the emitted journey
  result, DXF snapshots and every test pinning today's output pass untouched — S8).
- **d** (repo root) `python3 tools/modularity_check.py --check` → **exit 0** (a grep of its output
  for `result_way` returns NOTHING). `python3 scripts/lanes/check_lane_paths.py --coverage` →
  **exit 0**, 9185 files, each owned by one lane.
- **e** the mutation proofs — each a single-line change in a COPY of a module OUTSIDE the repository
  (the repo files are never touched), the pinned behaviour then checked to move. 8/8 CAUGHT:
  M-F1 served-empty→absent distinction; M-F2 present detection; M-F3 untrusted→not-read; M-A1 area
  agree/disagree; M-A2 large-lot threshold; M-D1 density user-statement; M-L1 lot-type mapping;
  M-O1 overlay rear-yard supported flag (breaks the reference-row tie). The two import-guard tests'
  mutation is the rename itself — they still list a literal permitted set and fail on any other app
  file naming the module.
- **f** `git status --porcelain` empty after the commit; `git diff --name-status
  6979d27d… HEAD` = only the allowed paths (the two placeholder app modules replaced, the new
  `result_way_bridge_overlay.py`, the three test files, the two guard tests, this report).

## Doubt

- The benchmark rear-yard reason (held-back #1) is the one place my result's REASON differs from
  H2's prose while the WAY matches; it follows directly from O16 (rear yard not supported under the
  overlay) and the decision module's overlay-first ordering. Reviewers should confirm O16's rear-yard
  reading and that the overlay reason winning first is intended.
- `compare_lot_area` rounds the outline area with Python `round` (banker's rounding at exactly N.5);
  O15 says "rounded to the whole square foot" and the benchmark/tests have no N.5 case, so this does
  not bite, but it is noted.

## Round 2 (G4 FAIL on test coverage; tests and the report only — no module change)

G3 (data-contract) PASSed at head `1ed440c4` and CONFIRMED reading O14 at the root; G4 (QA) FAILed
on two MUST-FIX coverage gaps (F1, F2) with two NOTEs (F3, F4): live branches of the new code were
pinned by no test, proven by silent mutations (the module behaviour was found correct). This round
adds the missing tests and rewrites the input-state table; the three module files and the two guard
tests are byte-unchanged (`git diff --stat daad5efb HEAD -- services/api/app services/api/tests/spatial
services/api/tests/scenario/three_answers/test_result_ways.py` empty). Only `test_result_way_bridge.py`
changed.

Source-line counts now (`wc -l`): app unchanged (facts 291, bridge 375, overlay 102); tests
`test_result_way_facts.py` 159, `test_result_way_bridge.py` 591, `test_result_way_bridge_overlay.py`
84 (all under the 600 **source-line** modularity threshold — `wc -l` counts blanks/comments; the
modularity checker names none of them, exit 0).

Added per finding (name : state pinned):
- **F1 (MUST-FIX) adapt_reach unknown-preservation.** `test_adapt_reach_keeps_an_unknown_measurement_unknown_f1`
  (an unknown street-line reach, an unknown corner reach and an unknown angle each stay None — None
  in, None out; a known one is carried verbatim; packet item (c) quoted) and
  `test_unknown_reach_withholds_coverage_and_rear_yard_f1` (a lot with site geometry present but an
  uncertain frontage, built as `tests/spatial/test_lot_reach.py::test_uncertain_frontage_reach_is_unknown`
  builds it → coverage and rear yard withheld as missing information, never a zero; work order gap
  K12 quoted).
- **F2 (MUST-FIX) interior/through mapping.** `test_interior_and_through_lot_types_are_mapped_f2`
  (read_site_inputs of "interior" → LotType.INTERIOR, of "through" → LotType.THROUGH, nothing held;
  anchored on the LotType member names, not the mapping dict) and
  `test_interior_and_through_lots_withhold_coverage_per_k2_f2` (through gather_result_ways both get
  coverage withheld (ZR 23-363, work owed) with the floor area unchanged — conditional; packet item
  (b) and gap K2 quoted).
- **F3 (NOTE) the four unchecked conditions.** `test_benchmark_conditional_names_all_four_unchecked_conditions_f3`
  (the benchmark floor-area conditional assumption names ALL FOUR conditions — the four names taken
  from gap K20, quoted — and the entry function has NO parameter that could mark one as checked).
- **F4 (NOTE) the texts battery.** `test_every_text_a_user_may_see_is_plain_and_true_s7` extended so
  its battery reaches every returnable text: the PRESENT statements of all six recorded conditions,
  all four area-statement variants (agree / disagree / could-not-compare / no-recorded-area), both
  large-lot statements, plus the decision module's way texts (K20-present included). The battery
  reaches ≥ 40 distinct texts (asserted).

Sweep (point 5) — every input of `gather_result_ways` and the functions it calls, each state it can
take, now has a named test or is reported as not-a-branch: added
`test_evaluator_inputs_shape_states` (None / no "inputs" key / "inputs" not a list → every value not
given), `test_non_numeric_lot_area_is_carried_as_not_given`,
`test_district_other_than_r6b_withholds_every_result`, `test_outline_missing_while_geometry_present`,
`test_outline_present_while_geometry_refused`,
`test_overlay_code_other_than_c2_2_withholds_residential_results`. The one state with no distinct
bridge branch: an overlay recorded PRESENT with no code cannot arise through the bridge (the facts
module's `_code_of` returns the served value whenever the overlay is PRESENT), so it is reported, not
tested here (the decision module pins the code-None path separately). Sweep result: ~26 input-state
clusters; all reach the new code except housing_kind (pass-through) and the overlay-present-no-code
state; the 2 clusters overstated in round 1 (interior/through; the reach's unknown-preservation) are
now genuinely pinned.

Point 7 (a state whose outcome is NOT what the packet/work order says): NONE found. Every swept
state behaved as the packet and the work order state; no module change is proposed or made.

Round-2 mutation proofs (each a single-line change to a COPY outside the repository; the repo files
are never touched; the newly pinned behaviour is checked to move). 7/7 CAUGHT:
- **M9** (reviewer's silent) `waterfront=Checked.NOT_CHECKED` → `Checked.ABSENT` → FAILS
  `test_benchmark_conditional_names_all_four_unchecked_conditions_f3` ("waterfront rules" drops out of
  the assumption). (Round 1 it passed every test.)
- **M10a** (reviewer's silent M10) adapt_reach `ReachValue(line.reach.value)` → `… or 0.0` → FAILS
  `test_adapt_reach_keeps_an_unknown_measurement_unknown_f1` (Street A reach becomes 0.0).
- **M10b** adapt_reach corner `ReachValue(measured.corner.reach.value)` → `… or 0.0` → FAILS the same
  test (corner reach becomes 0.0).
- **M11** (reviewer's silent) drop "interior"/"through" from `_LOT_TYPE_BY_NAME` → FAILS
  `test_interior_and_through_lot_types_are_mapped_f2` (interior → None).
- **M-NEW1** invert the `evaluator_inputs` Mapping guard → FAILS `test_read_site_inputs_states`
  (district → None).
- **M-NEW2** outline-None area branch `else None` → `else 0.0` → FAILS
  `test_outline_missing_while_geometry_present` (agreement becomes DISAGREES, not could-not-compare).
- **M-NEW3** non-numeric area guard admits `str` → FAILS
  `test_non_numeric_lot_area_is_carried_as_not_given` (a string area is no longer not-given).
F4 needs no new mutation: its texts are static strings (no branch); the round-1 F-check already proved
the guard non-vacuous (injecting a forbidden token into a reached text fails it).

Tests: 36 in the three new files (round 1: 25; +11) + the 2 guard tests (unchanged) = 38.

Known limits recorded from the G3 review (no code change):
- **G3 F2** — `result_way_facts._read_column` detects a served-empty column by exact-matching the
  sentence the shared reader emits (`PLUTO has no <column> value for this lot.`). If that reader
  sentence ever changed, a served-empty column would fall to the UNTRUSTED branch → NOT_READ — the
  SAFE direction (it withholds, never over-claims "recorded as absent"). Noted; no change.
- **G3 F4** — `compare_lot_area` uses Python `round` (half-to-even); O15 does not specify the half
  rule and no half-square-foot case occurs, so immaterial (the module computes no zoning number).
- G3 also raised F6 (the claim-head→HEAD diff is contaminated by peer-task commits riding the branch;
  the gate is recorded against this task's own commit) and F7 (minor: `isinstance(area_value,(int,float))`
  admits bool, record-truthiness) — both immaterial; noted for the orchestrator.

Round-2 checks (DIRECT exit codes; lanes venv python, `-p no:cacheprovider`, `PYTHONDONTWRITEBYTECODE=1`,
from `services/api` unless noted):
- **a** `python -m ruff check .` → **exit 0**.
- **b** `python -m pytest -q tests/scenario/three_answers tests/spatial/test_lot_reach.py` →
  **exit 0**, 180 passed, 2 skipped (round 1: 169; +11 new). New this round: 11 (all in
  `test_result_way_bridge.py`).
- **c** (repo root) `python3 tools/modularity_check.py --check` → **exit 0** (grep `result_way` =
  NONE). `python3 scripts/lanes/check_lane_paths.py --coverage` → **exit 0**, 9187 files.
- **d** the 7 round-2 mutations above — all CAUGHT.
- **e** `git status --porcelain` empty after the commit; `git diff --name-status daad5efb HEAD` =
  `test_result_way_bridge.py` and this report only; the module files, the spatial tests and
  `test_result_ways.py` byte-unchanged.
