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
