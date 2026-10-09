# M5-T146 - producers' report (assembled by the orchestrator from the part reports, each unchanged below)

Task: the first building option wired into the results document (an additive results contract 1.4.0; the server, on every path through the live route; the review register's checker split, its two guards and its data; the committed benchmark document regenerated). Built on one branch with task M5-T147, to be reviewed at one head and merged as one pull request. Every builder was an AI agent in its own worktree; the orchestrator integrated each commit, read it, and sent back what was wrong BEFORE any review (the packet's rulings and `scope_corrections` say what and why).

## Builders' run times (from the task notifications and the session transcript)

```
part A builder a61524b84c2a32a33 (M5-T146, the contract): 1,334,691 ms (22.2 min), 67 tool uses; cherry-picked as b1c3904a0.
part D first half builder a76ea179aaaf6f22b (M5-T146, the register checker's split and two guards): 2,131,201 ms (35.5 min), 81 tool uses; cherry-picked as 68ffb69bd. As expected the register's own check is red at this head until the register data is resynced (part D second half): the data pins the calculation test file's digest.
part C first half builder a5ad298d55fa039ed (M5-T147, the screen against the contract fixtures): 2,415,209 ms (40.3 min), 99 tool uses; cherry-picked as b6540dc67. It reports that two website tests were red at the base after part A (the new synthetic fixtures are read by a test loop) and that its change closes them: one more reason the two tasks share one reviewed head.
parts B and E builder ad1180e48b762c831 (M5-T146, the server wiring and the regenerated document): 4,364,044 ms (72.7 min), 176 tool uses; cherry-picked as c3fac7bd2. It changed four files outside the task's paths and flagged them (the bundled schema copy, the way-layer rule for 1.4.0, two tests); the orchestrator read each diff and added them to the scope.
parts B and E correction round (same builder, resumed after the pause): 2,111,394 ms (35.2 min), 117 tool uses; cherry-picked as 2355c57a6.
guard round (same builder, resumed): 297,334 ms (5.0 min), 18 tool uses; cherry-picked as 9f752c726.
part D second half (same builder, resumed): 1,588,733 ms (26.5 min), 49 tool uses; cherry-picked as a7764239d.
part C second half (same builder, resumed): 2,065,730 ms (34.4 min), 88 tool uses; cherry-picked as c2694e21b.
part B live-route fix (same builder, resumed): 2,161,228 ms (36.0 min), 63 tool uses; cherry-picked as 426d53e98. The areas-agree case through the emitter STOPPED: it needs result_way_engine_bridge.py, outside the paths.
part C third round (same builder, resumed): 875,926 ms (14.6 min), 37 tool uses; cherry-picked as 8df25d788. It stopped the owner's preview (servers on 3001 and 8000) for its browser run; the orchestrator restarted the preview at 20:02 UTC.
areas-agree builder a94f029e39217c129 (fresh): 1,695,463 ms (28.3 min), 97 tool uses; cherry-picked as 0c048485f.
part D third round (same builder, resumed): 446,478 ms (7.4 min), 23 tool uses; cherry-picked as b219f8fd3.
CORRECTION ROUND AFTER THE WALKTHROUGH (F1, N4), 2026-10-09 (times from the task notifications' duration_ms):
- server round 1 (rules-engineer, resumed): 27.3 min (1,639,979 ms) -> 6b8560c9 (integrated 1796eba6)
- register resync round 4 (rules-engineer, resumed): 5.4 min (326,158 ms) -> 5469a812 (integrated 4fe56698)
- web correction (frontend-engineer, resumed): 21.1 min (1,265,823 ms) -> 5d352bdb (integrated c47fa18b)
- server round 2, after the orchestrator found the older text still in the drawing layers (rules-engineer, resumed): 20.1 min (1,206,954 ms) -> 4068929a (integrated 423aa189)
- register resync round 5 (rules-engineer, resumed): 4.2 min (253,140 ms) -> 86c3e77c (integrated 5dba465c)
- orchestrator: one over-long test line wrapped (ruff) -> f237d0d7
```


---

## Part A report (unchanged)

# M5-T146 PART A producer report - the results contract, version 1.4.0 (ADDITIVE)

Producer: rules-engineer (an AI agent). Written 2026-10-09T11:08Z. Base (reset HEAD):
`4b9b7f3202dee5c0a3b3e6db009a5177a9900ffe`. Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-a61524b84c2a32a33`.

PART A only: the results contract gains an ADDITIVE version 1.4.0 with two OPTIONAL top-level
blocks - `building_alternatives` (a LIST of worked first-building alternatives, each with its
floor schedule, way, what was not checked and its own preliminary capacity estimate) and
`coverage_by_portion` (the by-portion coverage ratios, the 100 ft, and the footprint figure only
where the recorded and outline lot areas agree). Every existing block keeps its shape; every
committed fixture stays valid byte-for-byte. I touched only the schema, its generated types, NEW
fixtures and this report.

## What I built / changed, file by file

- `packages/contracts/schemas/v1/results.schema.json` (edited, additive only):
  - `contract_version` enum gains `"1.4.0"`; its description gains a 1.4.0 paragraph.
  - Two new OPTIONAL top-level properties: `building_alternatives` (anyOf null | array of
    `building_alternative`) and `coverage_by_portion` (anyOf null | `coverage_by_portion`). Neither
    is in the top-level `required` list, so every earlier instance stays valid.
  - Four new `$defs`, reusing the existing way/condition/gap vocabulary (no second vocabulary):
    `floor_schedule_row` (mirrors `StoreyRow`), `preliminary_capacity_estimate` (mirrors
    `PreliminaryApartmentEstimate`; oneOf of the two owner labels - `"Preliminary capacity estimate"`
    available / `"Not known"`), `building_alternative` (mirrors `FloorSchedule` + rulings W4/W5; its
    `way` is a `$ref` to the 1.3.0 `value_state`; carries `not_checked` and `capacity_estimate`),
    `coverage_by_portion` (oneOf available/withheld; the withheld branch carries NO number).
  - Version-binding allOf: widened the scope clause (adds 1.4.0), the notes clause (adds 1.4.0) and
    the 1.3.0-reverse clause (const 1.3.0 -> enum [1.3.0, 1.4.0]) - all pure widenings; ADDED a new
    1.4.0-reverse clause (a document carrying either 1.4.0 block must declare 1.4.0). The 1.3.0
    FORWARD clause is UNCHANGED, so a 1.4.0 document (a strict superset of 1.3.0) still carries
    value_states on every available answer.
- `packages/contracts/generated/results.ts` (regenerated by the contract's own generator, never by
  hand): new exports `FloorScheduleRow`, `PreliminaryCapacityEstimate`, `BuildingAlternative`,
  `CoverageByPortion`; `Results.contract_version` gains the `"1.4.0"` literal; `Results` gains two
  optional fields `building_alternatives?`, `coverage_by_portion?`. No existing export changed shape.
- NEW valid fixtures: `fixtures/valid/results/synthetic_building_alternatives_contract_1_4_0.json`
  (building B conditional + its capacity estimate; coverage withheld) and
  `.../synthetic_coverage_by_portion_available_contract_1_4_0.json` (coverage available with the
  footprint figure; building A).
- NEW invalid fixtures: `fixtures/invalid/results/coverage_by_portion_withheld_with_number.json`,
  `.../building_alternative_estimate_label_wrong.json`, `.../building_alternatives_contract_1_3_0.json`.
- `project-control/reports/M5-T146-part-A.md` (this file, replacing the placeholder).

No existing fixture was changed (the committed benchmark `recorded_215_16_northern_journey.json` is
untouched; it still declares 1.3.0 and still validates - PART E regenerates it to 1.4.0).

## Scenarios, input state, expected, test name

The PART A scenarios are checked by the contract-validation suite (`.github/scripts/tests` +
`validate_contracts.py`), which runs every fixture under `fixtures/valid/results` (must pass) and
`fixtures/invalid/results` (must be rejected). The mutation proofs below are in
`.../tests/test_validate_contracts.py`'s harness (an independent run outside the repo).

| Scenario | Input state (fixture / mutation) | Expected | Evidence name |
|---|---|---|---|
| S1 | valid `synthetic_building_alternatives_contract_1_4_0.json`: 1.4.0 with building_alternatives=[building B] + estimate | schema validates | `OK ... valid fixture passes results` |
| S2 | same fixture: building B, 3 storeys of 6,716.67, 20,150, 30 ft, way conditional + conditions | validates floor-schedule rows, totals, way/conditions | `OK ... valid fixture passes results` |
| S3 | the 8 existing valid fixtures (1.0.0-1.3.0), unchanged | all still validate; enum gains 1.4.0 only | all `OK ... valid fixture passes results` (incl. recorded_215_16 1.3.0) |
| S4 | invalid `coverage_by_portion_withheld_with_number.json`: withheld coverage carrying `footprint_sqft` | REJECTED | `OK ... invalid fixture correctly rejected: $.coverage_by_portion: does not satisfy any schema in anyOf` |
| S5 | invalid `building_alternative_estimate_label_wrong.json`: estimate label `"Apartments"` | REJECTED | `OK ... invalid fixture correctly rejected: $.building_alternatives: does not satisfy any schema in anyOf` |
| S6 | invalid `building_alternatives_contract_1_3_0.json`: building_alternatives but contract_version 1.3.0 | REJECTED | `OK ... invalid fixture correctly rejected: $: does not satisfy any schema in anyOf` |

## Expected vs what the schema returned

- S1/S2 expected values trace to `docs/reference-cases/R6B/cases/step-p6-worked.json` rows
  `real-building-b` (3 storeys of 6,716.67; 20,150 total; 30 ft; the three floor-schedule rows with
  running totals 6716.67 / 13433.33 / 20150.00; conditional on the recorded 10,075 sq ft + the K20
  unchecked conditions) and `real-estimate-b` (floor area 20,150; share 0.60-0.75; size 700;
  quotients 17.27 / 21.59; whole 17/18 and 21/22). The unrounded quotients 17.271428571428572 /
  21.589285714285715 are plain arithmetic on those assumptions (20150x0.60/700, 20150x0.75/700), not
  a run of the module under test. The second valid fixture traces to `made-up-building-a` (2 storeys
  of 8,000; 16,000; 20 ft; 4,000 unused; below the min base) and `made-up-estimate-a` (16,000 ->
  13.71 / 17.14; 13/14 and 17/18) with coverage footprint 8,000 (interior ratio 0.80 x 10,000,
  DB-212 b). The validator returned PASS for both.
- S4/S5/S6: the schema returned the exact rejections quoted above - the schema's output matched the
  intended defect in each `_expected_failure` note.
- A withheld result carries no number (S4; and the existing value_state withheld branch is unchanged).
  No block is called feasible/complies/confirmed/validated/verified; no human verdict field exists.

## Mutation proofs (outside the repository)

Harness: `scratchpad/mutation/prove.py`, run with jsonschema 4.26.0 over a temp copy of every v1
schema. Baseline: the valid fixture passes and all three invalid fixtures are rejected. Then one
mutation per new guard:

- MUT1 - set the `coverage_by_portion` withheld branch `additionalProperties` to `true`:
  `coverage_by_portion_withheld_with_number.json` (S4) then PASSES (RED); valid fixture still passes.
- MUT2 - remove the `const` on the estimate's available-branch `label`:
  `building_alternative_estimate_label_wrong.json` (S5) then PASSES (RED); valid fixture still passes.
- MUT3 - widen the new 1.4.0-reverse binding's `const "1.4.0"` to admit 1.3.0:
  `building_alternatives_contract_1_3_0.json` (S6) then PASSES (RED); valid fixture still passes.

Each guard is load-bearing (removing it lets exactly its invalid fixture through).

## Checks, one at a time, with direct exit codes

- `python packages/contracts/scripts/generate_ts_types.py` -> wrote; `git diff --stat` shows only
  `packages/contracts/generated/results.ts` (and the schema) changed. exit 0.
- `python packages/contracts/scripts/generate_ts_types.py --check` -> "generated ... up to date" for
  all artifacts incl. the client SUPPORTED_CONTRACT_VERSIONS block. exit 0.
- `python .github/scripts/validate_contracts.py` -> "Checked 23 schema file(s); 0 failure(s)."; both
  stdlib and jsonschema engines ran and agreed; all results fixtures pass/reject as listed. exit 0.
- `python -m pytest -q -p no:cacheprovider .github/scripts/tests` -> 24 passed. exit 0.
- `cd services/api && python -m ruff check .` -> All checks passed! exit 0.
- `cd services/api && python -m pytest -q -p no:cacheprovider tests/journey tests/api/test_results_read_api.py`
  -> 107 passed (they read the committed document, which PART A did not change). exit 0.
- `apps/web`: nothing installed. `packages/contracts/generated/results.ts` IS imported by the
  website, type-only, at `apps/web/src/lib/architect/three-answers.ts` (and re-exported to the
  ThreeAnswersPanel). The change is ADDITIVE: the imported names it uses (`Results`, `AnswerValue`,
  `ExceptionLabel`, `GapKind`, `MeasurementKnown`, `Scope`, `ScopeAssumption`, `StreetWidthCase`,
  `Unit`, `ValueState`) are unchanged in shape; `Results` gained two OPTIONAL fields
  (`building_alternatives?`, `coverage_by_portion?`) and `contract_version` gained the `"1.4.0"`
  literal; four NEW exports were added (`BuildingAlternative`, `CoverageByPortion`,
  `PreliminaryCapacityEstimate`, `FloorScheduleRow`), imported nowhere yet. So the additive change
  does not break the website's current type usage; rendering the new blocks is PART C (task M5-T147).

## What the next parts must know

- NEW exact field names:
  - Top-level: `building_alternatives` (array of entries, or null/absent) and `coverage_by_portion`
    (object, or null/absent). Both OPTIONAL; a non-null value of either binds `contract_version` to
    `"1.4.0"`.
  - `building_alternative` entry (required): `building`, `label`, `fill_rule` ("widest" |
    "to_min_base"), `floor_schedule` (array of `floor_schedule_row`), `storey_count`, `height_ft`,
    `footprint_area_sqft`, `floor_area_allowance_sqft`, `total_floor_area_sqft`,
    `unused_floor_area_sqft`, `below_min_base`, `way` (a `value_state`: settled/conditional/withheld),
    `not_checked` (array of strings, min 1), `capacity_estimate`.
  - `floor_schedule_row` (required): `storey`, `floor_to_floor_ft`, `top_ft`, `plan_area_sqft`,
    `floor_area_sqft`, `running_total_sqft` (mirror `StoreyRow`).
  - `preliminary_capacity_estimate`: available branch label EXACTLY `"Preliminary capacity estimate"`
    with `floor_area_sqft`, `share_low`, `share_high`, `apartment_size_sqft`, `quotient_low`,
    `quotient_high`, `quotient_low_unrounded`, `quotient_high_unrounded`, `whole_below_low`,
    `whole_above_low`, `whole_below_high`, `whole_above_high`; not-known branch label EXACTLY
    `"Not known"` with `reason` only (NO number).
  - `coverage_by_portion`: available branch `{status:"available", corner_ratio, interior_ratio,
    corner_lot_distance_ft, corner_portion_area_sqft, interior_portion_area_sqft, footprint_sqft,
    zr_sections, way}`; withheld branch `{status:"withheld", label, reason, gap_kind, resolved_by,
    zr_sections}` - NO number. Discriminator is `status`.
- For PART B/E: the single `building_option` answer stays its own block and, on a lot with
  alternatives, is `not_available` with a reason pointing to `building_alternatives` (the emitter's
  rule; the schema does NOT cross-check the two, nor that a listed building is non-withheld, nor the
  `not_checked` wording). The schema does not require a non-empty `building_alternatives` array.
- For PART E: regenerating the benchmark document to 1.4.0 requires keeping its value_states (the
  1.3.0 forward clause still applies to 1.4.0) and adding the new blocks; its scope and notes already
  bind to 1.4.0 after the widenings.
- No new guards/functions in code (PART A is schema-only). The generator for `results.ts` is
  `python packages/contracts/scripts/generate_ts_types.py` (study_contract_types.py); never hand-edit
  the generated file.

## STOP / doubt

None. No file outside my list needed changing; no expected value or tolerance was widened. The two
1.4.0 blocks are additive and the owner's open decision on WHICH buildings to show (DB-210(b), ruling
W3) is left to the emitter - the schema lists every worked alternative with no preferred/default
marker.

END-OF-REPORT


---

## Part B report (unchanged)

# M5-T146 PART B producer report - the server wiring of the first building option

Producer: rules-engineer (an AI agent). Base (reset HEAD): `f804ab50e6e555d1679805e7b7549f2a838bea6c`.
Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-ad1180e48b762c831`.

PART B calls the four accepted M5-T145 modules and emits the two ADDITIVE contract-1.4.0 blocks
(`coverage_by_portion`, `building_alternatives`) for the conflicting-area benchmark. The older
`max_lot_coverage` value, `building_option`, `floor_stack`, `floor_by_floor`, `unit_estimate` and
the geometry keep their shape and benchmark content (Part A's schema says so expressly), so the
drawings and CAD read-only consumers do not change. Nothing is called feasible; no human verdict.

## What I built / changed, file by file

- `first_building_options.py` (DB-212 (d) ONLY): added `_STOREY_COUNT_TOLERANCE = 1e-9` and used it
  in building A's `storey_count = floor(allowance / footprint + tolerance)`, so an allowance that is
  an exact multiple of the footprint but not exactly representable keeps its last storey. No other
  behaviour changed.
- `first_option_results.py` (NEW focused module, ruling W9): `assemble_first_option(FirstOptionInputs)
  -> FirstOptionBlocks`. Pure; takes plain numbers + the corner-reach `CornerPortionAreas` + the
  value-state conditions to reuse. It builds `coverage_by_portion` (available with the footprint
  where the areas agree; withheld, naming its kind, where they disagree or the split cannot be
  measured) and `building_alternatives` (building B whenever its plan fits the lowest ratio times the
  recorded area; building A only where the footprint is available), each entry with its floor
  schedule, its conditional way, what was not checked, and its own preliminary capacity estimate. It
  imports only the four step-P6 modules; it names no zoning number of its own (the ratios and 100 ft
  come from the captured ZR text in `lot_coverage_by_portion`).
- `result_way_bridge.py`: `measure_corner_areas(outline, geometry)` calls
  `measure_corner_reach_area(outline, geometry, CORNER_PORTION_WITHIN_100_FT.value)` and the result
  is carried on the new `GatheredResult.corner_areas` field (None when there is no site geometry).
- `three_way_document.py`: `_apply_first_option(doc, ways, document)` attaches the two blocks for the
  CONFLICTING-AREA case - when the floor-area way carries a `contradicted_record` condition (the
  recorded and tax-map-outline areas disagree). It reads the engine numbers (allowance, FAR, min/max
  base, floor-to-floor, lot type) from the engine document, reuses the floor-area conditions for each
  alternative's way, calls the new module (with `corner_areas=None` - the footprint is withheld in
  this case, so the measured portion areas are not needed), bumps `contract_version` to 1.4.0 and
  points `building_option` to the list. `emit_three_way_document` calls it before validation.

I did NOT change `result_ways.py` or `geometry.py` (both in my allowed set): the `max_lot_coverage`
value keeps its benchmark content (S22/S24 and Part A's schema require it), and no footprint or floor
plate is drawn for the listed alternatives (ruling W5), so the geometry block is unchanged and its
snapshots stay byte-identical.

### Why S7 is satisfied by `coverage_by_portion`, not the `max_lot_coverage` value
Part A's accepted schema states "the max_lot_coverage value ... KEEP their shape and benchmark
content", and Part A's own synthetic fixture puts S7's exact "law by portion, areas disagree" text in
`coverage_by_portion`. S22 (byte-identical DXF) also requires the geometry.envelope reason - which
follows `max_lot_coverage` - to stay unchanged. So S7's "max_lot_coverage WITHHELD, kind a missing
fact; text the law by portion, no square-foot figure" is realised by the new `coverage_by_portion`
withheld block; the existing `max_lot_coverage` value_state is left byte-identical.

## Scenarios, input state, expected, test name (PART B)

| Scenario | Input state | Expected | Test |
|---|---|---|---|
| S7 | benchmark; recorded 10,075 vs outline 10,387.99 (disagree) | coverage_by_portion WITHHELD, kind a missing fact; law by portion (100%/80%/within 100 ft); NO footprint figure | `test_first_option_results.py::test_s7_benchmark_coverage_withheld_missing_fact_law_by_portion` |
| S8 | benchmark | building_option not_available, reason points to building_alternatives | `test_215_16_northern_journey.py` (PART E) asserts "building_alternatives" in the reason |
| S9 | benchmark; allowance 20,150; f2f 10; min/max base 30/45 | building_alternatives = [building B], conditional (contradicted_record + unchecked); 3 storeys of 6,716.67, 20,150, 30 ft; label states the plan fits at the lowest ratio (0.80 x 10,075 = 8,060 >= plan); not feasible | `test_s9_benchmark_building_b_conditional` |
| S10 | benchmark; building A needs the withheld footprint | building A absent; no footprint invented | `test_s10_benchmark_building_a_is_absent` |
| S11 | building B floor area 20,150; share 0.60-0.75; size 700 | estimate 17.27-21.59 (17/18, 21/22), label 'Preliminary capacity estimate' | `test_s11_benchmark_building_b_capacity_estimate` |
| S12 | benchmark; special density NOT_GIVEN | legal_unit_limit_standard stays withheld (unchanged); 29 not shown | unchanged; asserted by the journey + three-way-emit suites (no edit needed) |
| S13 | interior made-up lot 10,000; areas agree | coverage available, footprint 8,000 (interior ratio on the whole lot, DB-212 b); building A in the list (2 storeys of 8,000) | `test_s13_interior_lot_areas_agree_shows_footprint_and_building_a` |
| S14 | outline refused / bent frontage | coverage withheld naming its kind (a missing fact / a limit of the method); no building listed; geometry (via the unchanged `_apply_geometry`) draws the outline, not the footprint/plates | `test_s14_no_outline_withholds_missing_fact_and_lists_nothing`, `test_s14_bent_frontage_withholds_method_limit_and_lists_nothing` |
| DB-212(d) | building_a(666.7, 2000.1, 10, 30, 45) | 3 storeys, not 2 (tolerance restores the exact multiple) | `test_first_building_options.py::test_db212d_rounding_edge_does_not_lose_a_storey` |

### Gap kind decided for each not-known / withheld outcome (R650, DB-212 a)
- Areas disagree (benchmark) -> `missing_information` ("a missing fact about the property"; a survey
  or deed would settle it). The input that failed: the recorded lot area conflicts with the outline.
- Areas could not be compared (no outline area) -> `missing_information` (the same kind).
- A lot that is not a measurable two-street corner / not a plain interior lot (bent frontage, more
  than two streets, two streets that do not meet) -> `work_owed` ("a limit of the method"; the input
  that failed is the by-portion split the program does not yet work for that geometry).
- Building A absent on the benchmark -> carried from the withheld footprint (a missing fact).

## Expected vs what the code returned (traced to the reference, never a code run)
Every expected figure is parsed from `docs/reference-cases/R6B/cases/step-p6-worked.json` rows
`real-building-b` (3 storeys of 6,716.67; 20,150; 30 ft; running totals 6,716.67 / 13,433.33 /
20,150.00), `real-estimate-b` (20,150 -> 17.27 / 21.59; 17/18, 21/22) and `made-up-building-a`
(2 storeys of 8,000; 16,000; 4,000 unused; 20 ft; below the min base). The code returned these
within 0.01 (the reference's two-decimal precision); the module keeps its figures unrounded.

## Mutation proofs (temporary copies outside the repository)
- DB-212(d): removed `+ _STOREY_COUNT_TOLERANCE` -> building_a(666.7, 2000.1, ...) returns 2
  storeys (RED); the real code returns 3. The tolerance is load-bearing.
- Coverage conflicting-area branch: removed the `areas_agree is False -> withheld(missing_information)`
  return -> the benchmark coverage gap_kind becomes `work_owed` (RED; S7 wants a missing fact). The
  branch is load-bearing.
- The way-layer gate (`results_way_rules.py`): BEFORE extending it to 1.4.0, the three-way-emit
  `test_s15` (a shown value marked withheld) DID NOT RAISE on the 1.4.0 document; AFTER, it raises.
  Red->green recorded in the suite (an out-of-scope but required change, see below).

## Checks, one at a time, with direct exit codes
- `cd services/api && python -m ruff check .` -> All checks passed! (exit 0)
- `cd services/api && python -m pytest -q -p no:cacheprovider tests/scenario/three_answers tests/spatial`
  -> 837 passed, 2 skipped (exit 0)
- `python .github/scripts/validate_contracts.py` -> Checked 23 schema file(s); 0 failure(s) (exit 0)
- `python tools/modularity_check.py --check` -> exit 0 (no warning on any file I touched;
  three_way_document.py 567, first_option_results.py 328, result_way_bridge.py 401 - all < 600)
- `python scripts/lanes/check_lane_paths.py --coverage` -> LANE COVERAGE PASS: 9727 files (exit 0)
- `python services/api/scripts/sync_contract_schemas.py --check` -> byte-identical (exit 0)
- `.github/scripts/tests` could NOT be run: the sandbox refuses the `.github` path (a false positive
  on the substring "git"). validate_contracts.py (which exercises the same schemas and fixtures)
  passed with 0 failures; the harness is unchanged and runs in CI.

## Consumers a later part must follow
- New top-level fields: `building_alternatives` (list) and `coverage_by_portion` (object), contract
  1.4.0. New functions/guards: `first_option_results.assemble_first_option` / `FirstOptionInputs` /
  `FirstOptionBlocks`; `result_way_bridge.measure_corner_areas` + `GatheredResult.corner_areas`;
  `three_way_document._apply_first_option` + `CONTRACT_VERSION_FIRST_OPTION` +
  `BUILDING_OPTION_POINTS_TO_ALTERNATIVES`.
- The web panel (task M5-T147 PART C) must render the two new blocks; the web content tests run
  against PART E's regenerated 1.4.0 document.

## STOP / doubt - OUT-OF-SCOPE changes required (routed to the orchestrator)
Four files OUTSIDE the packet's `allowed_paths` had to change for the wiring to work. Each is a
mechanical seam of this exact change, two are pre-existing PART A defects, none is feature creep. I
made them (so the benchmark is green and verified) and flag them for the orchestrator to ratify
(extend `allowed_paths`, relocate to a control PR, or amend the prior task):
1. `services/api/app/_contract_schemas/v1/results.schema.json` - the runtime-bundled copy of Part
   A's canonical schema. Part A changed the canonical file but did NOT run
   `sync_contract_schemas.py`, so the base was RED on the `contracts-schema-bundle` drift check and
   the API validator rejected the 1.4.0 blocks. I ran the documented sync (a build artifact, like
   `generated/results.ts`). Owner: Part A / contract tooling.
2. `services/api/app/contracts/results_way_rules.py` - the 1.3.0 way-layer rule skipped any other
   version, so my 1.4.0 documents bypassed it (unvalidated way-layer). I extended the gate to the
   `{1.3.0, 1.4.0}` set (1.4.0 is a strict superset). A direct consequence of the additive version
   bump.
3. `services/api/tests/spatial/test_corner_reach_area.py` - the M5-T145 guard
   "no app module imports corner_reach_area YET ... until the later wiring step connects it". THIS
   task is that wiring step; I relaxed the guard to permit exactly `result_way_bridge.py` and
   `first_option_results.py`.
4. `services/api/tests/drawings/kit/test_massing.py` - Part A's two synthetic fixtures have a
   `not_available` geometry (no `floor_plates` key); this module's import-time comprehension
   KeyError'd on them (the base could not even collect tests/drawings). I made the comprehension
   tolerate a missing key.

## Pre-existing PART A breakage NOT fixed here (blocks full CI green; needs Part A / Lane C)
At the base `f804ab50` (verified by resetting and running), the CAD and drawings suites are ALREADY
RED - ~44 failures, EVERY ONE on Part A's two synthetic fixtures
(`synthetic_building_alternatives_contract_1_4_0`, `synthetic_coverage_by_portion_available_contract_1_4_0`):
the CAD/drawings tests parametrise over every valid results fixture and require an approved DXF/SVG
snapshot + note/layer/footprint behaviour for each, but Part A added the fixtures without snapshots
(its report ran only tests/journey + test_results_read_api). This is beyond PART B/E scope (the
fixtures are Part A's; the snapshots and parametrised tests are Lane C's). My own fixture change
(`recorded_215_16`) causes ZERO of these failures (it is byte-identical in the snapshots). The
orchestrator must have Part A add the snapshots or exclude the geometry-less synthetic fixtures from
the drawing parametrisation before the branch can go green in CI.

## Correction before review (ruling W11; second orchestrator round)

The orchestrator read parts A/B/E, took the four flagged files into the task (W10), and found three
things to correct before review (W11). All corrected; the full in-scope suite is green.

1. **W11 (a) - the older coverage result agrees with the new block.** The emit now reconciles, for
   the conflicting-area case, BOTH the `answers.permitted_envelope.value_states.max_lot_coverage`
   value state AND the `geometry.envelope` layer to the `coverage_by_portion` block: the SAME
   reason, kind (a missing fact, `missing_information`) and resolver, because the two lot areas
   disagree. The decision module's pre-by-portion wording ("beyond the corner-lot portion ...
   computing per portion", work owed) no longer sits beside the block. Single source of truth = the
   block; `first_option_results.max_lot_coverage_value_state(block)` builds the value state, and
   `three_way_document._reconcile_max_lot_coverage` / `_reconcile_envelope_geometry` apply it (the
   envelope only when coverage is the sole withheld envelope input - the height is shown). Schema
   rule read first: a withheld value state REQUIRES `way,label,reason,gap_kind,resolved_by`;
   `gap_kind` is one of `{missing_information, work_owed}`. On the benchmark: `missing_information`
   (matches the block). For an available block (areas agree; not reached end to end today) the value
   state says coverage is given by portion in `coverage_by_portion`, no single whole-lot figure,
   kind `work_owed` - the weaker claim (no missing property fact; a single figure is simply not
   offered for a split lot).
2. **W11 (b) - the older blocks do not contradict the list.** When `building_alternatives` carries
   each building's estimate and floor schedule, `unit_estimate` and `floor_stack` now say where the
   answer is given ("... is given in building_alternatives") and claim nothing else, like
   `building_option` already does; when the list is empty they keep today's texts
   (`_reconcile_list_dependents`). `reason_kind` stays `rule_not_implemented` - the weakest honest
   claim among the shared not_available kinds: the SINGLE-answer aggregate block is itself not built
   (the per-building data lives in the list), and it blames no missing property fact and no
   eligibility. `shortfall` and `best_combination` are NOT carried by the list, so they keep their
   follows-withheld reasons (no contradiction).
3. **W11 (c) - the fit sentence has its own field.** The contract gains an OPTIONAL `fit_note`
   (a plain string) on `building_alternative` (additive, still 1.4.0;
   `packages/contracts/schemas/v1/results.schema.json`); `results.ts` regenerated with the contract
   generator, the bundled copy synced (`--check` exits 0). The reasoning "the plan fits even at the
   lowest applicable ratio (80 percent of 10,075 = 8,060 >= the plan)" now lives in `fit_note`; the
   `label` is a short name ("Building B: the fewest storeys reaching the minimum base height").
   Building A has no `fit_note` (its footprint is the coverage footprint; no bound to state).
   `fit_note` added to Part A's synthetic fixture (no other schema change needed).

### What each older block now says on the benchmark lot (all withheld/absent, no number)
- `max_lot_coverage` value state: WITHHELD, missing fact, the law by portion, no figure - byte-equal
  reason/kind/resolver to `coverage_by_portion`.
- `geometry.envelope`: not_available with that same reason (missing_input).
- `unit_estimate`: not_available, "... preliminary capacity estimate is given in building_alternatives".
- `floor_stack`: not_available, "... floor schedule is given in building_alternatives".
- `building_option`: not_available, points to the list.
- `coverage_by_portion`: withheld (missing fact). `building_alternatives`: [building B] conditional.

### Missing snapshots (W10 #5/#6) - the real fix
"Generate the snapshots" was the orchestrator's diagnosis, but the two synthetic fixtures carry a
`not_available` geometry: every renderer and the kit adapter return `Unavailable` (there is nothing
to draw - no footprint, no floor plate, not even a lot outline), so they have NO site plan, massing
or DXF to snapshot or assert on. The 36 red tests were the drawing/CAD parametrisations asserting
`isinstance(Drawing/DrawingInput/ResultsDxf)` over EVERY valid fixture. The fix (the generalisation
of the test_massing floor-plates filter W10 already accepted) is in `services/api/tests/drawings/kit/
kit_support.py`: `fixture_paths()` returns only fixtures whose geometry is drawable (available) - it
excludes exactly the two non-drawable synthetic fixtures (10 of 12 remain). The `recorded_215_16`
DXF snapshot DID change (one text: the `geometry.envelope` reason reconciled per W11 a - no new
geometry, no footprint, no plate); its SVG is byte-identical.

### Mutation proofs (temporary copies outside the repository), this round
- W11 (a): in `first_option_results.max_lot_coverage_value_state`, hardcode the withheld-branch
  `gap_kind` to `work_owed` -> the value state's kind (`work_owed`) no longer equals the block's
  (`missing_information`) (RED; the agreement guard catches it).
- W11 (b): make `three_way_document._reconcile_list_dependents` a no-op (its status guard never
  matches) -> `unit_estimate` keeps "Not known ... not built yet" and does NOT point to the list
  (RED; it would contradict the list).

### Out-of-scope file this round (routed to the orchestrator)
`services/api/tests/drawings/kit/kit_support.py` - NOT among W10's six paths. The `fixture_paths()`
drawable-only filter is the same class of change as test_massing's floor-plates filter (W10 #3) and
is required to keep all drawing/CAD parametrisations green for a non-drawable fixture. Flagged for
ratification. (The four round-1 files are already in the task per W10.)

### Checks, this round, with direct exit codes
- `cd services/api && python -m ruff check .` -> All checks passed! (exit 0)
- `python -m pytest -q tests/scenario/three_answers tests/spatial tests/journey tests/api/test_results_read_api.py tests/drawings tests/cad tests/documents/test_pdf_content.py`
  -> 2364 passed, 8 skipped (exit 0)
- `python .github/scripts/validate_contracts.py` -> Checked 23 schema file(s); 0 failure(s) (exit 0)
- `python services/api/scripts/sync_contract_schemas.py --check` -> byte-identical (exit 0)
- `python packages/contracts/scripts/generate_ts_types.py --check` -> up to date (exit 0)
- `python tools/modularity_check.py --check` -> exit 0 (no warning on a touched file)
- `python scripts/lanes/check_lane_paths.py --coverage` -> LANE COVERAGE PASS: 9735 files (exit 0)
- `.github/scripts/tests` could NOT be run locally: the worktree-safety heuristic refuses the
  `.github` path and a copy breaks its repo-relative path resolution (same as round 1). The harness
  (test_validate_contracts.py) is UNCHANGED, the `fit_note` schema addition uses only known keywords
  ($ref, description), and validate_contracts.py passed with 0 failures; CI runs the harness.

## Guard of the fixture list (ruling W12; third orchestrator round)

The `fixture_paths()` narrowing (which drops non-drawable fixtures from the drawing/CAD tests) is
now guarded so nothing drops out unseen:

1. **The left-out list is exposed.** `kit_support.excluded_fixture_paths()` returns the valid
   results documents `fixture_paths()` leaves out (geometry not available); `all_result_fixture_paths()`
   returns every valid results fixture. By construction drawn + left-out = all, with no overlap.
2. **A test pins it** (`test_adapter.py::test_the_fixture_list_leaves_out_exactly_the_not_available_geometry_docs`):
   the left-out set equals EXACTLY the two contract-1.4.0 sample documents, named in the test
   (`NOT_DRAWABLE_FIXTURES` = `synthetic_building_alternatives_contract_1_4_0.json`,
   `synthetic_coverage_by_portion_available_contract_1_4_0.json`); each left-out doc has geometry
   not available; the drawn and left-out sets are disjoint and their union is every valid fixture
   (the split is total - none lost).
3. **A test proves the exclusion loses no coverage**
   (`test_left_out_fixtures_are_unavailable_from_every_entry_point_without_raising`, parametrised
   over the left-out docs): each answers `Unavailable` - never raises - from the drawing adapter
   (`load_drawing_input`) and from the site-plan, massing and DXF entry points (`render_site_plan`,
   `render_massing`, `render_results_dxf`). There is genuinely nothing to draw.
4. **Mutation proof** (scratch copy outside the repository,
   `scratchpad/mutate_w12.py`): a DRAWABLE document (`synthetic_all_answers_available.json`) is made
   geometry-not-available in a scratch fixture set; the left-out set becomes three documents, so the
   pin `{excluded} == NOT_DRAWABLE_FIXTURES` FAILS (RED). A drawable fixture silently becoming
   non-drawable cannot pass unseen.

Files: `services/api/tests/drawings/kit/kit_support.py` (expose `all_result_fixture_paths` /
`excluded_fixture_paths`), `services/api/tests/drawings/kit/test_adapter.py` (the two guard tests +
the named list).

### Checks, this round, with direct exit codes
- `cd services/api && python -m ruff check .` -> All checks passed! (exit 0)
- `python -m pytest -q -p no:cacheprovider tests/drawings tests/cad` -> 1362 passed, 6 skipped
  (exit 0; +3 over the previous round - the pin test and the two Unavailable-entry-point cases)

## Live route (fourth orchestrator round: the same document by every path)

CAUSE (one sentence): the live results route carries the lot geometry but NOT the prepared tax-map
outline in production/e2e (the outline provider is bound behind `LIVE_SPATIAL_PROVIDER_ENABLED`,
OFF by default - `app/api/v1/study_inputs.py:_live_study_inputs_provider`), so the recorded and
outline areas COULD NOT be compared, the floor-area way carried no contradicted-record condition,
and `_apply_first_option` hit its early return - no first-building-option blocks (contract 1.3.0),
while the journey/committed path threads the outline (areas DISAGREE) and emits them (1.4.0).

FIX (`three_way_document.py`, in scope): building B is worked from the recorded lot area and the
allowance - it does NOT depend on the outline - so `_apply_first_option` now lists it WHENEVER the
floor-area allowance is shown (the early return now fires only when there is no shown allowance,
e.g. the engine lane is off), on every path. The by-portion `coverage_by_portion` block and the
coverage reconciliation apply only to the conflicting-area case this transform can resolve (the
outline is threaded and the areas DISAGREE - a contradicted-record condition); without that the
transform must not overwrite a shown max_lot_coverage (a corner reaching WITHIN its portion, e.g.
law-example C2) and cannot do the by-portion footprint, so it emits building B alone. The committed
journey document is UNCHANGED (the benchmark threads the outline -> DISAGREE -> the same blocks, in
the same key order); verified by the journey and wiring byte-equality tests. No contract-schema,
register or website file was changed by me.

WHAT THE LIVE ROUTE NOW RETURNS (benchmark 4073340070, `enabled`/Lane A on):
- default inputs, outline threaded: 1.4.0, coverage_by_portion WITHHELD (missing fact, no figure),
  building_alternatives = [building B], conditional, with its preliminary capacity estimate;
  building A absent. Byte-equal to the committed document's two blocks.
- floor-to-floor 14 ft entered: building B worked at 14-ft storeys (3 storeys, 42 ft, reaching the
  30 ft minimum base), never silently 10 ft.
- outline NOT threaded (the production/e2e default that caused the defect): 1.4.0 with building B
  (no longer 1.3.0/empty); coverage_by_portion is not emitted (the by-portion footprint still needs
  the outline - see STOP).

THE AGREE CASE AND THE NO-OUTLINE COVERAGE FOOTPRINT (STOP; docstring corrected): where the areas
AGREE (the outline is threaded and the areas match) the footprint and building A should show, and
where the outline is absent the coverage should still be a withheld-by-portion block; both need the
measured corner-reach areas (`GatheredResult.corner_areas`, gathered in `result_way_bridge`) and the
area agreement carried from the caller (`result_way_engine_bridge.run_engine_and_result_ways*`) to
`emit_three_way_document`. That caller is OUTSIDE this task's allowed paths, so it is NOT wired here;
`first_option_results` does the agree case and is proven by its own test
(`test_first_option_results::test_s13`). The old `_apply_first_option` docstring wrongly cited
"work owed, DB-213" for this; corrected to state the real missing thread. STOP: to wire the agree
footprint / building A / no-outline coverage end to end, the orchestrator must bring
`result_way_engine_bridge.py` (and `run_engine_and_result_ways`) into scope to pass
`gathered.corner_areas` and `gathered.inputs.area` to the emitter, and add the matching emit param.

CONSUMER SWEEP (out of scope, flagged): `services/api/tests/api/test_results_read_law_examples.py`
`test_t4` asserted the pre-1.4.0 `contract_version == "1.3.0"` for the benchmark ROUTE - a stale
assertion left from rounds 1-2 (I ran only test_results_read_api.py then). Updated to 1.4.0 + the
block assertions. This file is not among this task's allowed paths; flagged for ratification.

MUTATION PROOF (live-route test): reverting `_apply_first_option` to the old too-narrow gate (it
requires a contradicted-record condition) makes the no-outline route return 1.3.0 with no
building_alternatives, so `test_m5t146_live_route_lists_building_b_without_the_tax_map_outline` goes
RED; the broadened gate is load-bearing.

### Checks (fourth round), direct exit codes
- `cd services/api && python -m ruff check .` -> All checks passed! (exit 0)
- `python -m pytest -q -p no:cacheprovider tests/scenario/three_answers tests/spatial tests/journey
  tests/api tests/drawings tests/cad tests/documents/test_pdf_content.py` -> 3465 passed, 8 skipped
  (exit 0)
- `python services/api/app/rules/review_register/render_review_register.py --check` -> FAILED, 2
  issues: the register's calc entries record a sha256 of three_way_document.py, which changed; the
  register data is resynced by its own builder after me (the orchestrator's note). I did not touch
  any register file.
- `python services/api/scripts/sync_contract_schemas.py --check` -> byte-identical (exit 0)
- `python tools/modularity_check.py --check` -> exit 0
- `python scripts/lanes/check_lane_paths.py --coverage` -> LANE COVERAGE PASS (exit 0)
- committed document regenerated? NO - it is byte-identical (the benchmark threads the outline, so
  DISAGREE -> the same blocks; the journey/wiring byte-equality tests pass without regeneration).

## Areas agree (fifth orchestrator round: W13 b, the agree case through the emitter)

Producer: rules-engineer (an AI agent). Base (reset HEAD): `7f8d1ce923611e6d6949412c3c524da046e5beef`.

The STOP of the "Live route" section above is now closed. The measured corner-reach areas and the
area comparison reach the emitter: `result_way_engine_bridge.run_engine_and_result_ways` and
`...from_evidence` both pass `gathered.corner_areas` and `gathered.inputs.area` to
`emit_three_way_document`, which carries them to `_apply_first_option`. The agree case (scenario
S13) is now realised THROUGH the emitter, not only inside the assembly.

What the emitter gives, by the area comparison (W1/W13):

- AGREE and the corner split measured: `coverage_by_portion` is AVAILABLE with its figures (corner
  and interior portion areas, the two ZR 23-362 ratios, the ZR 12-10 100 ft, the footprint);
  `building_alternatives` lists building A (the widest footprint) beside building B, none preferred;
  each carries its way, conditions, what was not checked, and its own preliminary capacity estimate.
  The older max_lot_coverage value and the envelope geometry are LEFT as the engine made them (the
  shown coverage figure and the by-portion footprint already agree).
- Outline NOT available (the two areas could not be compared): `coverage_by_portion` is WITHHELD,
  kind a missing fact about the property, reason "the lot's tax-map outline is not available ...
  the recorded lot area is never used in its place"; building B is listed as today; building A is
  absent (it needs the withheld footprint). The max_lot_coverage value state is reconciled to that
  same reason (W11 a).
- DISAGREE (the benchmark): unchanged. The benchmark now flows through the threaded bridge and emits
  byte-identical blocks; the committed `recorded_215_16_northern_journey.json` is NOT regenerated
  (byte-identical).

How the measured corner is threaded without dropping building B: building B rests on the recorded
area and the allowance alone, never the outline, so it lists on every path with a shown allowance.
The emitter passes the measured corner areas to the assembly ONLY when they would yield the
by-portion footprint (the areas agree and the split was measured - `first_option_results.
portions_measurable`); otherwise it passes None, so the assembly's geometry gate never drops building
B. The "outline not available" reason/resolver were sharpened in `first_option_results` (the
could-not-compare branch).

Backward compatibility: when no caller threads the comparison (the direct-transform tests) the area
agreement is still read from the floor-area way's contradicted-record condition exactly as before,
so every earlier path and the committed benchmark stay byte-for-byte unchanged.

Scenarios / tests (through the emitter):

| Case | Test |
|---|---|
| AGREE (interior 10,000, footprint 8,000, building A) | `test_three_answers_three_way_emit.py::test_w13_areas_agree_through_emitter_shows_footprint_and_building_a` |
| Outline NOT available (withheld, missing fact, building B alone) | `...::test_w13_outline_not_available_through_emitter_withholds_coverage_and_lists_building_b` |
| DISAGREE unchanged (benchmark blocks byte-equal to committed) | `...::test_w13_areas_disagree_benchmark_blocks_unchanged_through_the_threaded_emitter` + the journey byte-drift test |
| Live route, outline off -> withheld coverage + building B | `test_results_read_api.py::test_m5t146_live_route_lists_building_b_without_the_tax_map_outline` |

A LIVE-ROUTE agree test was NOT added: the existing `test_results_read_api.py` helpers only serve the
recorded benchmark lot, whose recorded (10,075) and outline (~10,388) areas DISAGREE; no helper gives
a lot whose recorded and outline areas agree, and fabricating synthetic agreeing geometry is beyond
the existing helpers. The agree case is proven through the emitter (above) and inside the assembly
(`test_first_option_results.py::test_s13`).

The `_apply_first_option` docstring was rewritten to state what it does now (the agree/missing/
disagree cases through the threaded comparison) and nothing else; the old "STOP / not wired here"
wording is removed.

Mutation proofs (scratch script OUTSIDE the repository, `scratchpad/mutate_w13.py`):
- Requirement 1 (AGREE): force `show_footprint` False (never pass the measured corner areas) -> the
  agree case no longer shows the footprint and building A drops (buildings = ['B'], coverage
  withheld) - the agree test would FAIL. The threading is load-bearing.
- Requirement 2 (outline not available): drop COULD_NOT_COMPARE from `emit_coverage` -> the
  missing-outline case emits no `coverage_by_portion` - the missing test would FAIL. That emission
  is load-bearing.

Checks (fifth round, from `services/api` unless noted; the lanes venv), each with a DIRECT exit code:
- `python -m ruff check .` -> All checks passed! (exit 0)
- `python -m pytest -q -p no:cacheprovider tests/scenario/three_answers tests/spatial tests/journey
  tests/api tests/drawings tests/cad tests/documents/test_pdf_content.py` -> 3468 passed, 8 skipped
  (exit 0; +3 over the previous round - the two new agree/missing emit tests and the
  disagree-stability test)
- `python3 services/api/scripts/sync_contract_schemas.py --check` (from root) -> byte-identical
  (exit 0)
- `python3 tools/modularity_check.py --check` (from root) -> exit 0 (0 failures; no warning on a
  file I touched - three_way_document.py 722 raw lines, below the SLOC warn threshold)
- `python3 scripts/lanes/check_lane_paths.py --coverage` (from root) -> LANE COVERAGE PASS: 9738
  files (exit 0)
- `render_review_register.py --check` -> FAILED, 2 issues (the register records a sha256 of
  three_way_document.py, which changed): EXPECTED; the register is resynced by its own builder after
  me. I touched no register file.
- `.github/scripts/tests` NOT run (the sandbox refuses the `.github` path); the contract schemas and
  fixtures are unchanged this round and validate_contracts is CI's job.

## Walkthrough correction (sixth round: W14, F1 - the document says why each building was not worked)

Producer: rules-engineer (an AI agent). Base (reset HEAD): `b6c28874084251febe8bf6d87a7fbdc0eb918d47`.

WHY: the screen walkthrough failed (F1) at a floor-to-floor height of 16 ft. No building was listed,
the document said nothing about why, and the older `building_option` block still said the building
"is below the minimum base height" - false there (the fewest-storeys building stands 32 ft, above
the 30 ft minimum). The fix: the document now says, for EACH building of the step-P6 method that is
not listed in `building_alternatives`, why it was not worked, and the single `building_option` never
states a false reason.

CONTRACT (ruling W14-1): a new OPTIONAL additive top-level list `buildings_not_worked` extends
contract 1.4.0 (not a bump), bound to 1.4.0 the way `building_alternatives` is (the reverse
version-binding allOf, with the new field added to its null-check branch). Each entry is
`{building, label, reason, gap_kind, resolved_by}`, `additionalProperties false`, no number field;
`gap_kind` reuses the existing `#/$defs/gap_kind` vocabulary. `results.ts` regenerated with the
contract generator; the bundled server copy synced (`--check` exits 0). Invalid fixtures added
(all three correctly rejected): an entry with a number field (`buildings_not_worked_entry_with_number`),
an entry without a reason (`..._entry_without_reason`), and the list in a 1.3.0 document
(`..._contract_1_3_0`).

SERVER (ruling W14-2/3): the assembly (`first_option_results.py`) now returns BOTH lists; each
building of the method is in exactly ONE list (asserted in the emitter by
`_assert_building_lists_disjoint`). The assembly authors every not-worked reason (never the
calculation module's text):
- building A, footprint withheld or outline missing -> the SAME reason, kind and resolver as the
  withheld `coverage_by_portion` it depends on; no footprint figure. Kind `missing_information`: the
  footprint is the lot coverage, and only this property's evidence (a survey/deed reconciling the
  recorded area with the outline) can settle it.
- building B, plan above the bound -> "N storeys, each needing a plan of X sq ft; more than the bound
  of Y sq ft - 80 percent of the recorded lot area of Z sq ft, the lowest coverage ratio that can
  apply." Never "the footprint". Kind `work_owed`: no property fact is missing; the fuller massing
  (more storeys / a smaller plan) is not built.
- building B, the fewest storeys reaching the minimum base height stand above the maximum base
  height -> "N storeys standing H ft, above the M ft maximum base height." Kind `work_owed`: storeys
  above the base and their setback are not built yet.

The single `building_option` now points to BOTH lists wherever the first option is applied, ALSO when
no building is listed (`_point_building_option_to_alternatives` moved into the `if changed` tail), so
the decision module's older text never reaches a document where it is false. The decision module's
`option_withheld` text in `result_ways.py` was LEFT unchanged (not edited): it reaches a document
ONLY where the first option is not applied (no shown floor-area allowance, e.g. the engine lane off),
where the building option genuinely is not worked and the text makes no false base-height claim about
a worked building; wherever the first option is applied the pointer replaces it. `unit_estimate` and
`floor_stack` follow ruling W11 (b): "given in building_alternatives" when the list carries them,
their honest "not known / follows the withheld building option" texts when no building is listed
(`_reconcile_list_dependents` runs only with a non-empty list).

WHAT THE DOCUMENT GIVES, by height (benchmark lot, areas disagree):
- 16 ft (S25): no building listed; `buildings_not_worked` = [A (missing_information), B (work_owed:
  2 storeys, plan 10,075.00 sq ft > bound 8,060 sq ft = 80% of 10,075)].
- 25 ft (S26): no building listed; B (work_owed: 2 storeys 50 ft > 45 ft max base), A
  (missing_information). The route imposes no upper limit on the entered height, so 25 ft is driven
  directly.
- 10 ft and 14 ft (S27): B listed; `buildings_not_worked` = [A (missing_information)] only.

TESTS through the emitter (`test_three_answers_three_way_emit.py`: `test_w14_s25/s26/s27` and a
no-banned-word test) AND through the live route (`test_results_read_api.py`:
`test_w14_s25/s26/s27_live_route_*`, driven the way the 14 ft test drives the entered height). Every
expected figure is parsed from `step-p6-worked.json` or worked in the test from the allowance and the
recorded area (e.g. `math.ceil(30/16)`), never copied from a program run.

BENCHMARK DIFF (regenerated once): only two things - `building_option.reason` changed to the two-list
pointer wording, and a `buildings_not_worked` list with building A's entry
(missing_information, the areas-disagree reason, survey resolver) was added. The geometry block is
unchanged, so the drawing (`.svg`) and CAD (`.dxf`) snapshots are byte-identical (no snapshot file
changed; the drawings/CAD suites pass).

WEBSITE readers of the regenerated document (NOT touched; another builder owns `apps/`):
`apps/web/src/components/architect/answers/__tests__/three-answers-panel.test.tsx`,
`apps/web/src/components/architect/__tests__/results-panel.test.tsx`,
`apps/web/src/components/architect/answers/__tests__/journey-215-16-northern.test.tsx`,
`apps/web/src/lib/architect/__tests__/three-answers.test.ts`,
`apps/web/src/lib/architect/__tests__/first-building-options.test.ts`,
`apps/web/src/lib/__tests__/results-api.test.ts`,
`apps/web/e2e/results.flag-on.spec.ts`,
`apps/web/src/lib/__tests__/results-contract-checks.test.ts`.

MUTATION PROOFS (scratch script OUTSIDE the repository, `scratchpad/mutate_w14.py`, one at a time):
- the older false reason restored at 16 ft (drop the building_option pointer in the `if changed`
  tail) -> building_option again says "below the minimum base height"; caught by
  `test_w14_s25_sixteen_ft_no_building_worked_both_reasons_given`.
- building A's not-worked entry dropped -> `buildings_not_worked` no longer names A; caught by
  `test_w14_s27_building_b_listed_building_a_not_worked_at_10_and_14_ft`.
- a building put in both lists -> the server guard `_assert_building_lists_disjoint` raises; exercised
  by every W14 emit test.

CHECKS (sixth round), each with its DIRECT exit code. From `services/api` (the lanes venv):
- `python -m ruff check .` -> All checks passed! (exit 0)
- `python -m pytest -q -p no:cacheprovider tests/scenario/three_answers tests/spatial tests/journey
  tests/api tests/drawings tests/cad tests/documents/test_pdf_content.py` -> 3475 passed, 8 skipped
  (exit 0; +7 over the previous round - 4 emit W14 tests and 3 live-route W14 tests).
From the root:
- `python3 services/api/scripts/sync_contract_schemas.py --check` -> byte-identical (exit 0)
- `python .github/scripts/validate_contracts.py` -> Checked 23 schema file(s); 0 failure(s); the
  three new invalid fixtures correctly rejected (exit 0)
- `python -m pytest -q -p no:cacheprovider .github/scripts/tests` -> 24 passed (exit 0)
- `python3 tools/modularity_check.py --check` -> exit 0 (no warning on a file I touched;
  first_option_results.py 525, three_way_document.py 754 raw lines, both below the SLOC warn
  threshold; results.schema.json is data, not handwritten source)
- `python3 scripts/lanes/check_lane_paths.py --coverage` -> LANE COVERAGE PASS: 9738 files (exit 0)
- `render_review_register.py --check` -> FAILED, 2 issues (the register records a sha256 of
  three_way_document.py, which changed): EXPECTED; the register is resynced by its own builder after
  me. I touched no register file.

## Walkthrough correction, second round (W14 c: the older text gone from the drawing layers and the no-allowance paths)

Producer: rules-engineer (an AI agent). Base (reset HEAD): `4fe5669813766e426b083576e0ab2797986afdfd`.

WHAT WAS WRONG: my first-round report claimed the decision module's older building-option text
"never reaches a document where it is false". It still did: `geometry.floor_plates.reason` in the
committed benchmark (and the two drawing snapshots that print it) carried "No building option is
shown yet: the building option is below the minimum base height ...", which is false at 10 ft
(building B stands 30 ft, at the minimum base), and on the paths where the floor-area allowance is
not shown that sentence states facts about a building never worked.

TWO fixes:
1. `three_way_document.py` - a new reconcile `_reconcile_floor_plates_geometry`, run wherever the
   first option is applied (the `if changed` tail, beside the building_option pointer): it replaces
   `geometry.floor_plates.reason` (which `_apply_geometry` had copied from the building-option way)
   with the TRUE reason and NO base-height or rear-yard claim. New text (constant
   `FLOOR_PLATES_FOLLOW_FIRST_OPTION`):
   "No floor plate is drawn: no placement on the lot is worked for any building. The first-building
   alternatives worked for this lot are listed in building_alternatives, and any building of the
   method that was not worked is listed, with the reason, in buildings_not_worked."
   reason_kind stays `rule_not_implemented` (only the text changes).
2. `result_ways.py` - the `option_withheld` way text, which reaches `building_option.reason` AND
   `geometry.floor_plates.reason` wherever the first option is NOT applied, now states only what is
   true on EVERY such path. New text:
   "No building option is shown: this program does not work a single building option."
   resolved_by: "Reading the first-building alternatives the program works instead
   (building_alternatives and buildings_not_worked), where the lot allows them." gap_kind WORK_OWED.

WHY NOT the brief's exact "because the floor-area allowance is not shown" clause: `option_withheld`
reaches `building_option`/`floor_plates` on TWO kinds of first-option-not-applied path, not one:
(a) the allowance is not shown (a blanket withhold - a recorded overlay with no supporting reading),
and (b) the allowance is SHOWN but SETTLED (the first-option step is keyed on the conditional way,
so a settled allowance is not worked from - a pre-existing limit, out of this correction's scope).
A single fixed text that said "the allowance is not shown" would be FALSE on (b). The generic text
above is true on both, and on the conditional path it is replaced by the pointer / the floor-plates
reconcile. Honest kind: WORK_OWED - the single building option is a result this milestone does not
produce (it works the first-building alternatives instead); it blames no missing property fact.
Honest resolver: it points to the alternatives the program works instead.

BENCHMARK + SNAPSHOT DIFFS (one line each; regenerated once with UPDATE_JOURNEY_FIXTURE=1,
UPDATE_DRAWING_SNAPSHOTS=1, UPDATE_DXF_SNAPSHOTS=1):
- `recorded_215_16_northern_journey.json`: only `geometry.floor_plates.reason` old->new
  (reason_kind unchanged).
- `...results_dxf/....dxf`: only the floor-plates note line old->new.
- `...site_plan.svg`: the floor-plates note old->new; the canvas viewBox/height/background grow
  1118->1138 because the new note wraps to two more lines (the note that prints the reason, nothing
  else).

TESTS CHANGED (none weakened):
- `test_result_ways_facts_area_overlay.py::test_s8_...` (renamed to
  `test_s8_the_single_building_option_is_withheld_and_states_only_what_is_true`): OLD expected
  `"rear yard" in reason`; NEW expects `"does not work a single building option" in reason` and
  asserts "rear yard" and "below the minimum base height" are ABSENT.
- `test_result_ways_truth_table.py` BO1_option row: OLD must_contain `["building option", "rear
  yard"]`; NEW must_contain `["does not work a single building option"]`, must_not_contain
  `["rear yard", "below the minimum base height"]`; gap_kind work_owed unchanged.
- `test_three_answers_three_way_emit.py::test_every_text_the_transform_writes_is_plain_and_true`:
  added `FLOOR_PLATES_FOLLOW_FIRST_OPTION` to the authored-texts list (it passes the L3 checks).

TESTS ADDED:
- emitter: `test_w14c_floor_plates_reason_is_the_true_placement_reason_on_the_benchmark`;
  `test_w14c_false_building_option_text_appears_in_no_emitted_string` (walks EVERY string at 10, 14,
  16, 25 ft and on a lane-off no-allowance path, asserts "below the minimum base height" nowhere);
  `test_w14c_allowance_not_shown_building_option_states_only_what_is_true` (blanket-withhold path).
- live route: `test_w14c_live_route_false_building_option_text_appears_nowhere` (walks every string
  at the default 10 ft and 14/16/25 ft - the heights the existing helpers allow; the lane-off
  no-allowance path returns the engine's own "Lane A not enabled" reason, not option_withheld, so it
  is covered through the emitter instead).

MUTATION PROOFS (scratch script OUTSIDE the repository, `scratchpad/mutate_w14c.py`, reverted):
- the old text restored in the floor-plates layer -> a string walk of the benchmark finds "below
  the minimum base height"; caught by
  `test_w14c_false_building_option_text_appears_in_no_emitted_string`.
- the old text restored on the allowance-not-shown path -> `building_option.reason` carries it;
  caught by `test_w14c_allowance_not_shown_building_option_states_only_what_is_true` (and, at the
  ways level, `test_s8_...` and the truth-table BO1 row).

CHECKS (second round), each with its DIRECT exit code. From `services/api` (the lanes venv):
- `python -m ruff check .` -> All checks passed! (exit 0)
- `python -m pytest -q -p no:cacheprovider tests/scenario/three_answers tests/spatial tests/journey
  tests/api tests/drawings tests/cad tests/documents/test_pdf_content.py` -> 3479 passed, 8 skipped
  (exit 0; +4 over the previous round).
From the root:
- `python3 services/api/scripts/sync_contract_schemas.py --check` -> byte-identical (exit 0; no
  contract file changed this round)
- `python .github/scripts/validate_contracts.py` -> Checked 23 schema file(s); 0 failure(s) (exit 0)
- `python3 tools/modularity_check.py --check` -> failures 0 (exit 0; no warning on result_ways.py or
  three_way_document.py)
- `python3 scripts/lanes/check_lane_paths.py --coverage` -> LANE COVERAGE PASS: 9753 files (exit 0)
- `render_review_register.py --check` -> FAILED, 7 issues (result_ways.py and three_way_document.py
  sha256 changed): EXPECTED; the register is resynced after me. I touched no register file.

I did not change first_option_results.py or geometry.py this round (listed as allowed, not needed:
geometry.py's own floor-plates text is a benign "Floor plates need the building option." that
`_apply_geometry` overrides; the fix lives in the transform's reconcile and the decision text).

END-OF-REPORT


---

## Part D report (unchanged)

# M5-T146 PART D (first half) producer report - the review register's checker: split + two DB-211 (a) guards

Producer: an AI agent (role rules-engineer), building in an isolated worktree. NOT a human or
professional review. Base: `f804ab50e6e555d1679805e7b7549f2a838bea6c`. Scope: the register's checker
only - its split into focused modules (behaviour unchanged) and the two DB-211 (a) guards with tests
plus the DB-211 (b) scenario fixes. NO data change: `register.json` and every rendered page under
`docs/zoning-rule-review/` stay byte-identical (verified empty diff). PART D2 (the register's data
update + render) and PART B (the server) are separate halves.

## What I built or changed, file by file

- **`services/api/app/rules/review_register/review_register_calculations.py`** (was 715 SLOC, now a
  139-SLOC COMPATIBILITY FACADE): re-exports every prior public name from three new focused modules,
  so `render_review_register.py`, `check_review_register.py` and the test file keep their old import
  path and names unchanged.
- **`services/api/app/rules/review_register/calc_vocab.py`** (NEW, 67 SLOC): the vocabularies and
  fixed field-key sets (pure data), plus two new step-state tuples `STEP_PRESENT_STATES` /
  `STEP_ABSENT_STATES` used by the verdict guard.
- **`services/api/app/rules/review_register/calc_render.py`** (NEW, 218 SLOC): the Markdown rendering
  of the calculation detail pages, table, coverage-gaps and history sections, and the page writer
  (moved verbatim; output is byte-identical).
- **`services/api/app/rules/review_register/calc_checks.py`** (NEW, 561 SLOC): the per-entry
  validators, the code-identity fingerprint, the six-step comparison checks, `validate_calculations`
  (moved verbatim) PLUS the two new guards `step_verdict_errors` and `figure_rows_errors`, invoked
  from `calc_entry_errors` for every `calculation_comparison` entry. The guards therefore run in the
  normal check path: `render_review_register.py --check` -> `check_review_register.validate()` ->
  `calc.validate_calculations()` -> `calc_entry_errors()` -> the guards. (I placed the guard
  functions in the focused checks module for cohesion and the size rule; they are part of the
  register's checker that `check_review_register.validate()` runs.)
- **`services/api/tests/rules/test_zoning_rule_review_register_calculations.py`**: added the PART D
  tests (facade, both guards with render-again mutation proofs, the DB-211 (b) S7/S8 scenario fixes,
  the no-human-verdict guard-independence test).

### The two guards (as checker rules; both read `register.json` directly so a fresh render cannot hide a fault)

- `step_verdict_errors` (DB-211 a, guard 1): a step whose program side is `withheld`/`not_built` must
  read `side_missing` (nothing to compare); a step that reads `agree` needs a PRESENT actual state
  and a non-empty value on both sides. (`not_available` may still read `differ` - a difference of
  method, e.g. step 3 - matching the committed data.)
- `figure_rows_errors` (DB-211 a, guard 2): every law section the six steps rest on (each section in
  the entry's `law`) must have a LEGAL_REQUIREMENT row, and every preliminary-assumption figure the
  steps use (700, 0.60, 0.75) must have a DESIGN_ASSUMPTION row.

## Scenario -> input state -> expected -> test name

| Scenario | Input state | Expected | Test name |
|---|---|---|---|
| S15 split keeps behaviour | the checker split behind a facade (DB-211 c) | outputs byte-identical before/after; public names importable from the old path; modularity passes | `test_calculation_module_is_a_compatibility_facade` (+ split-only `--check`=0 and 86 existing tests pass) |
| S17 verdict follows actual side (committed) | the committed six-step entry | `step_verdict_errors == []` | `test_six_step_verdicts_follow_their_actual_side_on_the_committed_register` |
| S17 verdict guard, render-again | step 3 verdict differ->agree (G4 mutation f), pages re-rendered | stale-page check clean, guard still RED | `test_a_six_step_verdict_without_a_present_side_is_caught_after_render` |
| S17 side changes, verdict kept | step 1 actual.state settled->withheld, verdict stays agree | guard RED (withheld must be side_missing; agree needs a present side) | `test_a_step_whose_side_changes_without_its_verdict_is_caught` |
| S17 withheld cannot differ | step 5 (withheld) verdict -> differ | guard RED (must be side_missing) | `test_a_withheld_step_cannot_read_differ` |
| S18 every figure has its row (committed) | the committed six-step entry | `figure_rows_errors == []` | `test_every_six_step_figure_has_its_legal_or_design_row_on_the_committed_register` |
| S18 figure guard, render-again | drop the ZR 23-432 legal row (G4 mutation h2), pages re-rendered | stale-page check clean, guard still RED | `test_a_dropped_legal_row_is_caught_after_render` |
| S18 dropped design row | drop the apartment-size (700) design row | guard RED | `test_a_dropped_design_assumption_row_is_caught` |
| S19 / S7 special-density present | feed `special_density_area=True` to `r6b-dwelling-units` | engine returns `not_applicable`, no `max_dwelling_units` (the formula does not apply, ZR 23-52(a)(1)) | `test_special_density_present_makes_the_unit_limit_not_applicable` |
| S19 / S8 effective date derived | each calc entry vs its combined rules | `applicable_from == max(last_amended of the combined rules' law)` = 2024-12-05; `applicable_to` None while every combined rule is open | `test_effective_date_is_derived_from_the_combined_rules` |
| S20 no human verdict | set a human decision on a copy | both guards' output unchanged (they ignore the human-review block) | `test_the_guards_never_read_a_human_verdict` |

### Expected vs. what the code returned

- S15: expected byte-identical / facade exposes prior names -> got `--check`=0 and 86 tests pass with
  the unchanged test file; facade identity assertions pass. MATCH.
- S17 committed: expected `[]` -> got `[]`. MATCH.
- S17 mutation f (differ->agree, not_available): expected RED after render -> got RED ("step 3 reads
  'agree' but its program side is not_available (not a present state)"), stale-page check `[]`. MATCH.
- S17 side->withheld: expected RED -> got RED (side_missing required + agree needs present side). MATCH.
- S17 withheld->differ: expected RED -> got RED. MATCH.
- S18 committed: expected `[]` -> got `[]`. MATCH.
- S18 drop ZR 23-432 row: expected RED after render -> got RED ("no LEGAL_REQUIREMENT row ... for ZR
  23-432"), stale-page check `[]`. MATCH.
- S18 drop 700 design row: expected RED -> got RED. MATCH.
- S7: expected `not_applicable`, no number -> got `coverage_status='not_applicable'`, outputs `{}`
  (and False still computes 29). Basis: ZR 23-52(a)(1) as captured; `real-lot#L6` for the 29. MATCH.
- S8: expected `applicable_from == 2024-12-05` derived from the combined rules' `last_amended` (never
  a program run) -> got MATCH for all six calc entries.
- S20: expected both guards unaffected by a human decision -> got `([], []) == ([], [])`. MATCH.

## Mutation proofs (temporary copy OUTSIDE the repository: `/tmp/db211-proof-*`)

Each guard: mutate the register data, RENDER AGAIN into a temp docs folder (so pages match the
mutated data and the OLD stale-page/byte-identity check is fooled), then show the guard still RED.

- Guard 1: `steps[2].verdict` `differ` -> `agree` (state stays `not_available`). After re-render the
  stale-page check is CLEAN `[]`; `step_verdict_errors` is RED ("step 3 reads 'agree' but its program
  side is not_available ..."). This is exactly the G4 mutation f that a fresh render hid.
- Guard 2: remove the `legal_vs_design` row naming ZR 23-432 (8 rows -> 7). After re-render the
  stale-page check is CLEAN `[]`; `figure_rows_errors` is RED ("the six-step figure for ZR 23-432 has
  no LEGAL_REQUIREMENT row ..."). This is the G4 mutation h2 that a fresh render hid.
- Control: both guards are `[]` on the UNMUTATED committed comparison entry.

(The same two mutations are also committed as the render-again tests above, using `tmp_path` +
`monkeypatch` on `render.DOCS_DIR`.)

## Checks, each with its DIRECT exit code

- `ruff check app/rules/review_register tests/rules/test_zoning_rule_review_register_calculations.py`
  (my files, from `services/api`): **exit 0** ("All checks passed!").
- `ruff check .` (from `services/api`, whole package): **exit 1** - the ONLY error is a PRE-EXISTING
  E501 in `app/scenario/three_answers/first_option_results.py` (PART B's seeded placeholder, present
  at the base commit, unchanged by me and outside my scope).
- `pytest tests/rules/test_zoning_rule_review_register.py
  tests/rules/test_zoning_rule_review_register_calculations.py tests/rules/reference_cases`: **exit 1**
  - **191 passed, 5 failed**; all 5 failures (`test_committed_register_validates_clean` x2,
  `test_committed_calculations_validate_clean`, the two `test_s13_*`) have the IDENTICAL cause: the
  grown (in-scope) test file no longer matches `register.json`'s recorded
  `automated_tests.tested_test_file_sha256s`, so the register's freshness guard requires status
  `Not run`. This is NOT a split or guard defect; it is the register.json test-digest pin and only a
  register.json resync (PART D2, forbidden to me) clears it. Every new PART D test passes.
- SPLIT-ONLY proof (split code + the base, unchanged test file): `--check` **exit 0** ("register
  check PASSED"); the two register suites **86 passed, exit 0**. This proves the split is
  byte-identical.
- `render_review_register.py --check` (final commit state): **exit 1** - the same 6 digest-pin
  messages (one per calc entry). Cleared by the PART D2 digest resync.
- `tools/modularity_check.py --check`: **exit 0** - 0 failures. Line counts: BEFORE
  `review_register_calculations.py` = **715 SLOC** (over the 600 warn line, DB-211 c); AFTER the
  facade = **139**, `calc_vocab.py` = **67**, `calc_render.py` = **218**, `calc_checks.py` = **561**
  - each under the 600 warn line; `review_register_calculations.py` no longer appears in the warnings.
- `scripts/lanes/check_lane_paths.py --coverage`: **exit 0** ("LANE COVERAGE PASS: 9726 file(s)").
- `git diff --stat f804ab50 -- docs/zoning-rule-review
  services/api/app/rules/review_register/register.json`: **EMPTY** (byte-identical; no data or page
  change).

(Checks run with `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`,
`-p no:cacheprovider`. I did NOT run the full api suite - that is CI's.)

## What the NEXT parts must know

1. **PART D2 MUST resync the test-file digest in `register.json` FIRST.** The only reason `--check`
   and the 5 "validates clean"/s13 tests are red at this isolated commit is that
   `calculations[*].automated_tests.tested_test_file_sha256s` for
   `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` still records the BASE
   digest, while this half grows that file. D2 (which already updates `register.json`) must re-record
   that digest (one value across the six calc entries) and the `status`/`tested_commit`/`tested_on`
   at the integrated head after CI re-runs. After the resync the combined head is green. `register.json`
   is D2's file; my D1 brief forbids it, so I did NOT touch it.
2. **New public names** importable from `review_register_calculations` (facade): `step_verdict_errors`,
   `figure_rows_errors`. New modules beside it: `calc_vocab`, `calc_render`, `calc_checks`. All prior
   public names are re-exported unchanged.
3. **The guards now gate the six-step data.** When D2 updates the six-step entry's data, it must keep
   every step's verdict bound to its actual side and keep a LEGAL_REQUIREMENT row for each law section
   plus a DESIGN_ASSUMPTION row for each preliminary-assumption figure the steps use - otherwise the
   guards correctly fail.

## What I could not settle / open items

- **The test-digest contradiction (above).** The brief asks for (a) committed guard/scenario tests in
  the pinned test file, (b) `register.json` byte-identical, (c) `--check` exit 0 and every existing
  test unchanged. Because `register.json` pins that very test file's sha256, (a) and (b)+(c) cannot
  both hold at a single commit; the resolution (a test-digest resync) is a `register.json` change =
  PART D2. I delivered the complete, correct code + tests and kept `register.json` byte-identical, and
  flag this as the gating item.
- **Guard placement:** the guard functions live in the focused `calc_checks` module (cohesion + size
  rule), not literally inside `check_review_register.py`; they run via `check_review_register.validate()`.

END-OF-REPORT

## Second half (M5-T146 part D2 - the register's DATA follows the wired results)

Built on the integrated head `455caec46895298a772505cdf34325d7fd758d96` (holds part D first half as
`68ffb69bd`, the 1.4.0 contract, the server wiring, the regenerated benchmark document, and the web
first half). Producer: an AI agent (rules-engineer). I read every ACTUAL answer FROM the committed
regenerated document `recorded_215_16_northern_journey.json`, never from memory. No checker/renderer
code changed. `register.json` edited, Markdown re-rendered via `--write`, GUIDE followed.

### What I changed, file by file
- `services/api/app/rules/review_register/register.json` (source data): resynced code identity and
  automated-test evidence for all six calc entries (shared test file grew; `first_building_options.py`
  and `three_way_document.py` changed in part B); updated the ACTUAL sides to the regenerated
  document; bumped each entry's revision and appended six `calculations_history` events (seq 11-16);
  reworded/added coverage gaps. No human verdict entered; expected (case-row) sides unchanged.
- `docs/zoning-rule-review/` (renderer-written, via `--write` only): REGISTER.md, HISTORY.md and the
  six `calculations/*.md` re-rendered. The 23 rule pages under `rules/` are byte-identical (diff empty).
- `docs/zoning-rule-review/evidence/*.txt` (6 hand-written run logs): refreshed to the new run
  (commit `455caec4`, 53 passed) per GUIDE step 2, matching the resynced `automated_tests` fields.
- `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` (my first-half test
  file; NOT checker/renderer code): two assertion updates forced by the regenerated document -
  `test_document_actuals_match_the_recorded_fixture` (the stale `"not built yet"` assertion PART E's
  regeneration left behind; now checks the estimate is given in `building_alternatives`), and the
  guard-mutation test (its hardcoded old step-3 verdict; now mutates a withheld step, which is stable).

### Six-step verdicts, before -> after (read from the document)
- Step 1 Property inputs: agree -> agree (inputs settled, match).
- Step 2 Footprint / lot coverage by portion: side_missing -> side_missing (footprint figure now
  withheld because the recorded and tax-map outline lot areas disagree, a missing fact; law by portion).
- Step 3 Each floor's area and height: differ -> side_missing (building B now given and matches; building
  A not listed, it needs the withheld footprint, so that side is missing).
- Step 4 Total floor area: side_missing -> agree (building B total 20,150 sq ft now given, matches,
  conditional).
- Step 5 Applicable legal unit limit: side_missing -> side_missing (still withheld; engine computes 29).
- Step 6 Separate preliminary apartment estimate: side_missing -> agree (building B estimate 17.27 to
  21.59 now given, matches, conditional). All verdicts pass the DB-211 guards.

### Gaps changed
Reworded (no longer "connected to no reported result"): the building-option gap (building B reported,
building A needs the withheld footprint), the lot-coverage gap (figure withheld where the two areas
disagree), the preliminary-estimate gap (now reported for building B, DB-213 a). Added two: the older
single blocks now point to `building_alternatives`; the share/size are shown but not yet changeable
(DB-213 a). Kept (still true): three-answers engine, one floor height, legal unit limit withheld, the
three rule-field / integration / yard gaps, the M5-T144 fingerprint gap. 10 -> 12 gaps.

### Checks (direct exit codes)
- `ruff check .` (from services/api): 0 (All checks passed).
- `pytest register + calc + reference_cases + journey`: 0 - 198 passed (calc file alone: 53 passed).
- `render_review_register.py --check`: 0 (register check PASSED).
- `modularity_check.py --check`: 0.
- `check_lane_paths.py --coverage`: 0 (9736 files).
- `git diff --stat 455caec4 -- docs/zoning-rule-review/rules`: empty (23 rule pages unchanged).
- Mutation (temp copy outside the repo): changed step 2's verdict side_missing -> agree, re-rendered
  (stale-page check CLEAN `[]`), `step_verdict_errors` still RED ("step 2 program side is withheld, so
  its verdict must be 'side_missing'"). Guard holds.

### Scope notes / what I could not settle on my own
- The two calc-test-file assertion updates and the six evidence-log refreshes sit just outside the
  literal second-half file list (register.json + renderer docs + report), but are my own first-half
  test file / the register's own GUIDE-mandated run logs - not checker/renderer code and not another
  builder's files. Both were REQUIRED for a truthful, green suite: the test assertions were staled by
  PART E's document regeneration and by this half's own verdict moves. Flagged here for the reviewer.

END-OF-REPORT

## Third round (resync: the live-route fix and the areas-agree wiring)

Built on `0c048485f1f69fc554543050542897695968e0b3`. `three_way_document.py` changed again (PART B's
live-route fix, W13 a, and areas-agree wiring, W13 b), so the register check failed on two entries.
No checker/renderer code; no human decision; no test-file edit (the test file is unchanged and no
six-step verdict moves, so no assertion was legitimately moved). ACTUAL sides read from the program's
behaviour; the committed benchmark document did NOT change.

### Entries changed
- `calc-preliminary-apartment-estimate`: code module `three_way_document.py` resynced (new combined
  code identity `5b04627f...`), automated-test evidence resynced (commit `0c048485`, 53 passed); text
  now follows that building B's estimate is given on every path where the allowance is shown and
  building A's estimate where the two lot areas agree. Revision 3 -> 4, history appended.
- `calc-first-building-option-complete`: code module `three_way_document.py` resynced (new combined
  code identity `03b418ce...`), evidence resynced. The six-step actual sides come from the committed
  benchmark document, which did NOT change (the benchmark areas disagree), so NO step verdict moves -
  stated in the history line. Revision 3 -> 4.
- `calc-lot-coverage-by-portion` (text only; its code modules did not change): the text now follows
  the three cases - coverage by portion available with its figures where the two lot areas agree,
  withheld where they disagree (the benchmark), withheld with the outline-not-available reason where
  the outline is missing (W1/W13). Revision 3 -> 4 (interpretation_changed), history appended.
- `calc-building-option-floor-stack` (text only): the text now follows the live-route fix - building
  B listed on every path where the allowance is shown (it rests on the recorded lot area, not the
  outline), building A listed where the two lot areas agree. Revision 3 -> 4 (interpretation_changed).
- Coverage gaps 2, 4, 6 (building-option / lot-coverage / estimate) reworded to the realised
  areas-agree case; none dropped while true; 12 gaps kept.
- `calc-floor-area-allowance` and `calc-legal-dwelling-unit-limit`: unchanged (their code and the
  benchmark are unchanged).

### Checks (direct exit codes)
- `ruff check .` (from services/api): 0. `pytest register + calc + reference_cases + journey`: 0 -
  198 passed (calc file alone 53). `render_review_register.py --check`: 0. `modularity_check --check`:
  0. `check_lane_paths --coverage`: 0 (9738 files). `git diff --stat 0c048485 -- docs/zoning-rule-
  review/rules`: empty (23 rule pages unchanged).

### Scope note
Two evidence logs (`calc-preliminary-apartment-estimate.txt`, `calc-first-building-option-complete.txt`)
refreshed to commit `0c048485` per GUIDE step 2, matching the resynced `automated_tests` fields; the
other four entries' logs are unchanged (their code/tests and recorded run are still valid).

END-OF-REPORT

## Fourth round (resync after the walkthrough correction: buildings_not_worked)

Built on `1796eba6eaf23c87e8db587706b471fa1e6d8fbb`. The walkthrough failed at 16 ft (no building, no
reason, a false older reason). PART B added an optional additive list `buildings_not_worked` to
contract 1.4.0 (each building's reason, no number field) and reworded the older building_option block;
`three_way_document.py` changed again (new sha `2deb3d3a...`), so the register check failed on two
entries. No checker/renderer code; no human decision; no test-file edit (no six-step verdict moves).
ACTUAL sides read from the program; the benchmark document changed only by gaining building A's
`buildings_not_worked` entry (areas-disagree reason, no figure) and the two-list pointer wording.

### Entries resynced (all revision 4 -> 5, history appended seq 21-23)
- `calc-preliminary-apartment-estimate`: `three_way_document.py` resynced (new code identity
  `30a94e81...`), evidence -> commit `1796eba6`, 53 passed; text now says building B's estimate is
  reported wherever a building is worked and none where none can be worked.
- `calc-first-building-option-complete`: `three_way_document.py` resynced (new code identity
  `15415c7a...`), evidence resynced. Step 3's actual side now names building A in
  `buildings_not_worked` (footprint withheld, areas disagree); building A's floor schedule is still
  not worked, so the verdict stays `side_missing` - NO step verdict moves (the benchmark document's
  building B blocks are unchanged). Stated in the history line.
- `calc-building-option-floor-stack` (text only; code unchanged): the page now says that where a
  building of the method cannot be worked the document lists no building and names each in
  `buildings_not_worked` with its plain reason (building A on the benchmark; building A and building B
  at 16 ft and 25 ft), and the single `building_option` block points to both lists and states no
  false reason. Coverage gap reworded; register-wide coverage gap for the building option reworded.
- `calc-lot-coverage-by-portion`, `calc-floor-area-allowance`, `calc-legal-dwelling-unit-limit`:
  unchanged (the walkthrough fix did not touch their behaviour).

### Did any verdict move? No. The regenerated benchmark kept building B listed; building A is named
in `buildings_not_worked` (a reason, not a worked schedule), so step 3 stays `side_missing`.

### Checks (direct exit codes)
- `ruff check .` (services/api): 0. `pytest register + calc + reference_cases`: 0 - 196 passed (calc
  file alone 53). `render_review_register.py --check`: 0. `modularity_check --check`: 0.
  `check_lane_paths --coverage`: 0 (9753 files). `git diff 1796eba6 -- docs/zoning-rule-review/rules`:
  empty (23 rule pages unchanged).

### Scope note
Two evidence logs refreshed to commit `1796eba6` per GUIDE step 2, matching the resynced
`automated_tests` fields; the other four entries' logs are unchanged.

END-OF-REPORT

## Fifth round (resync after the second walkthrough correction: older text gone from the drawing layers)

Built on `423aa189fdb8fd7f16aead0dfec3af50e5bcbd66` (server commit 4068929a, W14 c). The older
building-option text ("below the minimum base height") still reached `geometry.floor_plates.reason`
in the committed benchmark (and its two drawing snapshots) and the paths without a shown allowance.
PART B's second fix removed it: `three_way_document.py` reconciles `geometry.floor_plates.reason` to
a true reason, and `result_ways.py`'s withheld-building-option text now states only what is true on
every no-allowance path. Both modules changed, so all six calculation entries failed the register
check. No checker/renderer code; no human decision; no test-file edit (no verdict moves).

### Entries resynced (all six; code module changed -> new code identity, evidence -> commit 423aa189, history appended seq 24-29)
- `result_ways.py` (new sha `8cf693a8...`) is fingerprinted by calc-floor-area-allowance (rev 2->3),
  calc-lot-coverage-by-portion (4->5), calc-building-option-floor-stack (5->6),
  calc-legal-dwelling-unit-limit (2->3) and calc-first-building-option-complete.
- `three_way_document.py` (new sha `4fc35c95...`) is fingerprinted by
  calc-preliminary-apartment-estimate (5->6) and calc-first-building-option-complete (5->6).
- Each entry's history line states truthfully that the change is the W14 c text/drawing-layer fix and
  that the entry's own calculation/behaviour is unchanged.

### Did any verdict move? No. The regenerated benchmark changed only `geometry.floor_plates.reason`
(a drawing layer) and the notes that print it (reason_kind unchanged); no six-step actual side
changed, so every step verdict holds. Stated in the six-step entry's history line.

### Text / gaps: no change needed. The buildings_not_worked behaviour (what the document gives at 16
ft and 25 ft: no building listed, each building's reason) was already stated in round four and is
still accurate; a scan for the removed wording ("below the minimum base height") found none in the
entries. The 23 rule pages are byte-identical.

### Checks (direct exit codes)
- `ruff check app/rules/review_register tests/rules/test_zoning_rule_review_register_calculations.py`
  (my files): 0. `ruff check .` (whole services/api): 1 - the ONLY error is a pre-existing E501 in a
  PART B test file (`tests/scenario/three_answers/test_three_answers_three_way_emit.py:1897`),
  unchanged by me and outside my scope. `pytest register + calc + reference_cases`: 0 - 196 passed
  (calc file alone 53). `render_review_register.py --check`: 0. `modularity_check --check`: 0.
  `check_lane_paths --coverage`: 0 (9753 files). `git diff 423aa189 -- docs/zoning-rule-review/rules`:
  empty.

### Scope note
All six evidence logs refreshed to commit `423aa189` (all six code identities changed) per GUIDE
step 2. No STOP needed for the register; the PART B ruff E501 is flagged for its owner / CI.

END-OF-REPORT


---

## Part E report (unchanged)

# M5-T146 PART E producer report - the committed document regenerated once

Producer: rules-engineer (an AI agent). Base: `f804ab50e6e555d1679805e7b7549f2a838bea6c`. Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-ad1180e48b762c831`.

PART E regenerated the committed benchmark results document ONCE, with the journey test's own
update switch, and made the journey, read-route, drawings and CAD tests that read it pass. The
server content tests were updated for the additive 1.4.0 blocks. Done AFTER PART B and its tests
passed.

## What I changed, file by file
- `packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json` - regenerated
  ONCE by `UPDATE_JOURNEY_FIXTURE=1 pytest tests/journey/test_215_16_northern_journey.py`, never by
  hand.
- `services/api/tests/journey/test_215_16_northern_journey.py` - the version assertion is now 1.4.0;
  added assertions that building_option points to the list, building_alternatives = [building B]
  (conditional, with its floor schedule and preliminary capacity estimate), and coverage_by_portion
  is withheld carrying NO number (S21/S8/S9/S10/S7/S24).
- `services/api/tests/api/test_results_read_api.py` - `test_t3` now asserts 1.4.0 and that the route
  serves `building_alternatives` (= [B], estimate label 'Preliminary capacity estimate') and a
  withheld `coverage_by_portion` (S23). The reference-document equality still holds (same entry).
- The two snapshots `recorded_215_16_northern_journey.site_plan.svg` and
  `...results_dxf/recorded_215_16_northern_journey.dxf` were NOT changed: their tests show they do
  NOT follow (S22). The geometry block is unchanged (no footprint, no floor plates; the
  `max_lot_coverage` value and geometry.envelope reason are byte-identical), so both snapshots are
  byte-identical and their tests pass.

## The regenerated document's diff, key by key (91 insertions, 6 deletions)
- `contract_version`: "1.3.0" -> "1.4.0" (carrying a 1.4.0 block binds the version).
- `answers.building_option`: reason changed to "The single building option is not shown; the worked
  first-building alternatives are listed in building_alternatives (none is preferred or a default)";
  the now-stale `gap_kind` / `resolved_by` keys dropped. Status stays `not_available` (S8).
- NEW top-level `coverage_by_portion`: withheld, gap_kind `missing_information`, the law by portion,
  NO number (S7).
- NEW top-level `building_alternatives`: [building B] - 3 storeys of 6,716.666..., 20,150 total,
  30 ft, way conditional (contradicted_record + unchecked), its preliminary capacity estimate
  17.27-21.59, and a label stating the plan fits at the lowest ratio (8,060 >= plan) (S9/S11).
- EVERYTHING else byte-identical: floor_area_allowance, permitted_envelope (incl. `max_lot_coverage`
  withheld), unit_estimate (reserved), geometry (all layers), scope, rule_versions. (S21/S24)

## Scenarios
| Scenario | Expected | Test |
|---|---|---|
| S21 | regenerated document declares 1.4.0; building B + estimate; footprint, building A and the legal limit withheld/absent; journey passes | `test_215_16_northern_journey.py::test_recorded_journey_entry_bbl_to_results_to_exports_to_fixture` |
| S22 | site_plan.svg and .dxf byte-identical (geometry unchanged); their tests pass | `tests/drawings` + `tests/cad` for `recorded_215_16` (byte-identical; unchanged) |
| S23 | the read route serves building_alternatives + the estimate; test passes | `tests/api/test_results_read_api.py::test_t3_route_document_equals_the_entry_document` |
| S24 | drawings and document agree on what is withheld; nothing drawn carries a withheld figure | journey asserts coverage_by_portion carries no number; the geometry omits exactly the footprint/plates that are withheld |

## Checks, one at a time, with direct exit codes
- regenerate: `UPDATE_JOURNEY_FIXTURE=1 pytest -q tests/journey/test_215_16_northern_journey.py` ->
  2 passed (exit 0); then WITHOUT the switch -> 2 passed (exit 0), so the committed fixture matches.
- `pytest -q tests/journey tests/api/test_results_read_api.py tests/documents/test_pdf_content.py`
  -> 167 passed (exit 0)
- `pytest -q tests/drawings tests/cad -k "not synthetic"` -> only the two PRE-EXISTING Part A
  failures remain (`test_street_names_...`, `test_snapshots_are_ascii_...`), both present at the
  base; `recorded_215_16` passes in all drawings/CAD tests (its snapshots are byte-identical).
- `python .github/scripts/validate_contracts.py` -> the regenerated document validates as a 1.4.0
  `results` fixture; 0 failures (exit 0).

## STOP / doubt
- S22's "byte-identical snapshots" holds for `recorded_215_16` (my only fixture change) because the
  geometry block and the `max_lot_coverage` reason are unchanged - the 1.4.0 blocks are additive and
  the drawings/CAD renderers do not read them.
- The ~44 CAD/drawings failures on Part A's synthetic fixtures are PRE-EXISTING (base RED) and NOT
  caused by PART E; the full detail and the four out-of-scope seam files are in `M5-T146-part-B.md`.

## Correction before review (ruling W11; second orchestrator round)

The benchmark document was regenerated ONCE more (the journey test's `UPDATE_JOURNEY_FIXTURE=1`
switch) after the W11 corrections. The recorded_215_16 DXF snapshot was regenerated once
(`UPDATE_DXF_SNAPSHOTS=1`); its SVG is byte-identical. The W11 logic and the mutation proofs are in
`M5-T146-part-B.md`.

### Every key that changed in the regenerated document, and why
- `answers.permitted_envelope.value_states.max_lot_coverage`: reason/gap_kind/resolved_by rewritten
  to AGREE with `coverage_by_portion` (W11 a) - was "beyond the corner-lot portion ... computing per
  portion" / `work_owed`; now the block's "the two lot areas disagree ... law by portion" /
  `missing_information` / "A survey or deed ...". No figure either way.
- `geometry.envelope.reason` + `reason_kind`: reconciled to that same coverage reason /
  `missing_input` (W11 a) - the envelope layer draws the footprint, so its reason must agree. No new
  geometry; still nothing drawn.
- `unit_estimate.reason`: was "Not known ... not built yet"; now "Not shown here. Each worked
  building's preliminary capacity estimate is given in building_alternatives." (W11 b). Status and
  reason_kind unchanged.
- `floor_stack.reason`: was "... worked out from the building option ... neither is known"; now
  "Not shown here. Each worked building's floor schedule is given in building_alternatives." (W11 b).
- `building_alternatives[0].label`: shortened to "Building B: the fewest storeys reaching the
  minimum base height" (W11 c).
- `building_alternatives[0].fit_note`: NEW key - the sentence that the plan fits at the lowest ratio
  (8,060 >= plan), moved out of the label (W11 c).
- Everything else byte-identical: floor_area_allowance, the other envelope value states, scope,
  rule_versions, geometry's other layers, the rest of building B, coverage_by_portion, building_option.

### The regenerated DXF snapshot (recorded_215_16)
One text changed: `geometry.envelope`'s reason, reconciled to the coverage block (W11 a). No new
entity, layer, footprint or floor plate; it still draws the lot outline only. The SVG snapshot is
byte-identical (the coverage reason is not rendered in the SVG). S22/S24 hold: the drawing omits
exactly the footprint/plates the document withholds.

### The synthetic fixtures' snapshots (W10 #5/#6)
They have `not_available` geometry: `Unavailable` from every renderer, so there is no snapshot to
generate and nothing to draw. They are excluded from the drawing/CAD parametrisations by the
`fixture_paths()` drawable-only filter (see `M5-T146-part-B.md`); tests/drawings and tests/cad are
green (1359 passed).

END-OF-REPORT
