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
  `total_floor_area_sqft`, `unused_floor_area_sqft`, `below_min_base`, `gap_kind`.

Functions:
- `building_a(footprint_area, floor_area_allowance, floor_to_floor_ft, min_base_ft,
  max_base_ft, max_building_ft)` — the WIDEST footprint stacked to the floor-area maximum
  (`storey_count = floor(allowance / footprint)`), every storey the same footprint plan.
- `building_b(footprint_area, floor_area_allowance, floor_to_floor_ft, min_base_ft,
  max_base_ft, max_building_ft)` — the FEWEST storeys reaching the minimum base height
  (`storey_count = ceil(min_base / floor_to_floor)`), the whole allowance spread evenly
  (`plan = allowance / storeys`), every storey the same plan. The footprint is a REQUIRED
  input of building B too (ruling C1): the plan must fit within it.

States and their texts:
- `status = "available"` — a worked floor schedule. The `reason` is a plain summary that
  NAMES the same-plan stack and the floor-to-floor height as design assumptions, not rules of
  law, and states `below_min_base` as a plain height fact only (no legal conclusion drawn —
  ruling C3).
- `status = "not_known"` — every figure `None`, `storeys = ()`, and `gap_kind` names the kind
  (ruling C7): `"a missing fact about the property"` (a missing footprint S20, or a missing
  floor-area allowance S21 — "not available for this lot") or `"code not built"` (a building B
  plan that would not fit the footprint S29; a building A stack that would pass the maximum
  base height S30). A missing input gives a not-known state, never a zero and never a default.
- An impossible numeric input (zero or negative footprint/allowance/height) raises
  `ValueError`; `None` (a missing fact) is handled first and is not an error.

No returned text says captured, complies, feasible, validated, verified or legally correct.
Rulings honoured: C1 (footprint required for both buildings; plan must fit; S16/S19/S20/S29),
C2 (no storey above the maximum base height; S30), C3 (`below_min_base` a plain fact),
C7 (plain texts; gap kind named), C8 (no existing file changed or importing this module; the
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
| S20 | footprint None; allowance 20,150 | both not_known, gap = a missing fact about the property; no figure | `test_s20_missing_footprint_both_not_known` |
| S21 | footprint 8,000; allowance None | both not_known, "allowance … not available for this lot" | `test_s21_missing_floor_area_allowance_both_not_known` |
| S29 | footprint 5,000; allowance 20,000 | B not_known (code not built: plan 6,666.67 > 5,000); A still worked | `test_s29_building_b_plan_would_not_fit_footprint` |
| S30 | footprint 2,000; allowance 20,000 | A not_known (code not built: 10 storeys, 100 ft > 45 ft max base) | `test_s30_building_a_stack_passes_max_base_height` |

Every EXPECTED value is parsed from `docs/reference-cases/R6B/cases/step-p6-worked.json`
numbers_block (never retyped, never from a module run). Settled envelope inputs the scenarios
state (max base 45, max building 55) are passed as inputs. Tolerance 0.01 sq ft = the
reference's two-decimal precision; the module keeps figures unrounded. `below_min_base` is
asserted as the parsed `height_ft < min_base_height_ft`.

## Expected vs returned (module run, for evidence only — never a test oracle)

| Scenario | Expected (reference) | Returned |
|---|---|---|
| S15 A | n2 h20 plans 8000,8000 rt 8000,16000 tot 16000 unused 4000 below=T | n2 h20 plans 8000,8000 rt 8000,16000 tot 16000 unused 4000 below=True |
| S16 B | n3 h30 plan 6666.67 rt 6666.67,13333.33,20000 tot 20000 unused 0 below=F | n3 h30 plans 6666.67× rt 6666.67,13333.33,20000.0 tot 20000 unused 0 below=False |
| S17 A | n1 h10 tot 10309.91 unused 9840.09 below=T | n1 h10 tot 10309.91 unused 9840.09 below=True |
| S18 A | n1 h10 tot 10309.88 unused 9840.12 below=T | n1 h10 tot 10309.88 unused 9840.12 below=True |
| S19 B (both) | n3 h30 plan 6716.67 rt 6716.67,13433.33,20150 tot 20150 unused 0 below=F | identical for 10309.91 and 10309.88 footprints |
| S20 A/B | not_known, no figure | not_known gap "a missing fact about the property" storeys () |
| S21 A/B | not_known, no default | not_known gap "a missing fact about the property" ("not available for this lot") |
| S29 B / A | B not_known (code not built); A worked | B not_known gap "code not built"; A available n4 h40 tot 20000 |
| S30 A | not_known (code not built) | not_known gap "code not built" storeys () |

## Mutation proofs (temporary copy outside the repository)

Mutations applied to a copied module under the scratchpad (`…/scratchpad/mut/app/…`); the
repo file was never mutated. The harness imports the mutated `app` package and parses the real
case file. Baseline (clean copy): 4 passed.

| # | Branch mutated | Change | Test that went red |
|---|---|---|---|
| 1 | building A fill rule | `floor(` → `ceil(` the allowance/footprint division | `test_s15…` FAILED `assert 3 == 2` (storey_count) |
| 2 | missing-footprint not-known | return an available zero schedule instead of `_not_known` | `test_s20…` FAILED (`available` != `not_known`) |
| 3 | building A max-base guard (C2) | disable `if height_ft > max_base_ft` | `test_s30…` FAILED (returned available, not not_known) |
| 4 | building B plan-fit guard (C1) | disable `if plan_area > footprint_area` | `test_s29…` FAILED (returned available, not not_known) |

## Checks (each with its direct exit code)

| Check (from `services/api` unless noted) | Exit |
|---|---|
| `python -m ruff check` first_building_options.py + its test | 0 (All checks passed!) |
| `pytest -q -p no:cacheprovider tests/scenario/three_answers/test_first_building_options.py` | 0 (9 passed) |
| `pytest -q -p no:cacheprovider tests/spatial tests/scenario/three_answers` | 0 (797 passed, 2 skipped) |
| `python3 tools/modularity_check.py --check` (worktree root) | 0 (740 files; failures 0; my module not among the 31 pre-existing warnings) |
| `python3 scripts/lanes/check_lane_paths.py --coverage` (worktree root) | 0 (9698 files, each owned by one lane) |

Did NOT run the full api suite (CI's job).

## What I could not settle

Nothing blocking. Two notes: (1) building A `storey_count` uses `math.floor`, exact for the
scenario inputs (20000/8000, 20150/10309.91, 20000/2000); I added no float epsilon so as not
to change behaviour at an exact-integer boundary (none of the scenarios sit on one). (2) The
floor-area allowance (S21) is classified as "a missing fact about the property" (the lot's
maximum residential floor area is a property-derived quantity); its plain text carries the
scenario's "not available for this lot" wording.
