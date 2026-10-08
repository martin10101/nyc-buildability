# M5-T134 producer report — wire the carriers

Producer: scenario-optimization-engineer (builder, an AI agent). Worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-ab4bcde21db64d350`. Contract/claim-seam head
reset to `b416cf0d154400ebf1dcaaabc199da4f4e25bc40`. ONE commit, no push, no ledger command.

Nothing is emitted: the three carriers (the built property profile, the prepared tax-map outline,
the site geometry) are surfaced on the real Python-object path and handed, with the evaluator-inputs
document, to `gather_result_ways` through ONE new thin adapter that returns the ways BESIDE the
engine's result. `engine.py` and the six decision-module files are read only; no schema, fixture or
snapshot changes; no route returns the ways; no production switch is turned on.

## Files changed (all within the 12 allowed paths; `git diff --name-status` = exactly these)

- `services/api/app/api/v1/study_inputs.py` — `StudyInputs` gains three optional, inert carriers
  (`property_profile`, `site_geometry`, `prepared_outline`); `assemble_study_inputs` sets them from
  the values it already holds (the profile local, the `site_geometry` argument, a new
  `prepared_outline` argument); a new `OutlineProvider` seam + `outline_provider` kwarg on
  `pluto_study_inputs_provider`; `_live_study_inputs_provider` binds the live outline provider behind
  the SAME `LIVE_SPATIAL_PROVIDER_ENABLED` flag as geometry.
- `services/api/app/api/v1/study_live_geometry.py` — new `live_outline_provider` (reading O21).
- `services/api/app/scenario/three_answers/inputs.py` — `ThreeAnswerInputs` gains the same three
  optional, inert carriers (typed under `TYPE_CHECKING`; `from __future__ import annotations` keeps
  them unevaluated, so no import cycle).
- `services/api/app/contracts/evaluator_inputs.py` — `build_three_answer_inputs` gains three optional
  args carried VERBATIM onto `ThreeAnswerInputs`.
- `services/api/app/scenario/three_answers/result_way_engine_bridge.py` — the thin adapter
  `run_engine_and_result_ways` and the external wrapper `EngineResultWays` (the ONE new app file that
  names the decision module).
- tests: `test_result_way_engine_bridge.py` (S1-S11, S14, imports), `test_wiring_emits_nothing.py`
  (S13), `test_result_ways.py` (guard: +1 permitted caller), `test_study_geometry.py` (surfacing +
  outline seam), `test_study_inputs_live.py` (live surfacing, seams off in prod),
  `test_evaluator_inputs.py` (carry-through).

None of `inputs.py`, `evaluator_inputs.py`, `study_inputs.py`, `study_live_geometry.py`, `engine.py`
contains the text `result_way` (grep: NONE). The adapter imports only `gather_result_ways` (from
`result_way_bridge`) and the engine's `generate_results`/`ThreeAnswersResult`; it imports nothing
from the api layer and nothing from the lot-reach module (parsed-import test). `tools/modularity_check.py
--check` names none of the changed files.

## The outline seam shape (reading O21) and its five-line justification

Shape: a SECOND optional provider seam. `OutlineProvider = Callable[[str, str], PreparedOutline |
None]`, threaded as the optional `outline_provider` through `pluto_study_inputs_provider` →
`assemble_study_inputs(prepared_outline=...)` → `StudyInputs.prepared_outline`; the live binding
`live_outline_provider()` fetches the MapPLUTO lot, adapts it with the accepted
`lot_outline_from_mappluto`, prepares it with `prepare_outline` (no streets fetch), and fails safe to
None on any typed error.

1. It is purely additive: a new optional keyword argument; the `GeometryProvider` type and signature
   are UNCHANGED, so every existing geometry provider and test double — including those outside my
   allowed paths — keeps working untouched. The alternative "optional second return" would change the
   geometry seam's shape and break those doubles.
2. The outline gets a REAL source by reusing the already-accepted `lot_outline_from_mappluto` +
   `prepare_outline` — the SAME pair the benchmark assembly uses; no new connector is introduced.
3. It is gated OFF in production behind the same `LIVE_SPATIAL_PROVIDER_ENABLED` flag as geometry, so
   the live study read stays byte-identical to the pre-wiring slice and nothing is emitted from it.
4. When no outline is produced the provider returns None and the carrier stays absent (O21); the reach
   then stays unknown and no default stands for a fact (L1).
5. Cost/limitation: when both seams are bound the live path fetches the MapPLUTO lot twice (once per
   seam). Acceptable because the path is off in production and the carriers are inert (nothing emitted),
   and it keeps the geometry seam and its doubles unchanged; noted as a future optimization (a shared
   one-fetch combined provider) that no reviewer verdict needs today.

## The red proof (step 2)

- RED-1: the S1 adapter test, run before the adapter's real content existed (only the seeded
  placeholder), failed at COLLECTION: `ImportError: cannot import name 'EngineResultWays' from
  'app.scenario.three_answers.result_way_engine_bridge'` — `1 error`, pytest exit **4**.
- RED-2: after writing the adapter (which names the decision module) but BEFORE adding it to the
  guard's permitted set, the UNCHANGED import guard
  `test_only_task_m5_t130_bridge_and_facts_modules_import_the_decision_module` FAILED:
  `AssertionError: these modules already reference the result-way module:
  ['…/result_way_engine_bridge.py']` — `1 failed`, pytest exit **1**. Adding exactly that one file to
  the permitted set turned it green; engine.py and the four carrier files still do not name it (grep),
  and the `tests/spatial/test_lot_reach.py` guard is unchanged and still passes.

## The table of input states (state → what is handed to gather_result_ways → test that pins it)

Every state is exercised THROUGH the adapter (the decision-module internals are not re-implemented).

| # | input state | handed to gather_result_ways | test id |
|---|---|---|---|
| S1 | all three carriers populated (benchmark), no statement | profile, outline, geometry, eval doc, housing_kind | test_s1_benchmark_carriers_reach_gather_through_adapter |
| S2 | geometry present, outline absent | outline=None, geometry present | test_s2_geometry_present_outline_absent |
| S3 | geometry absent | outline=None, geometry=None | test_s3_geometry_absent |
| S4 | recorded lot area + outline area | both figures real; area compared; K3 from recorded | test_s4_profile_with_recorded_lot_area |
| S5 | no recorded lot area | recorded None; large-lot not stated; outline never stands in | test_s5_profile_without_recorded_lot_area |
| S6 | profile absent | profile=None → every column not read → all withheld | test_s6_profile_absent |
| S7 | C2-2 overlay present, supported family | overlay PRESENT + support table | test_s7_overlay_present_with_supporting_reference_row |
| S8 | C2-2 overlay present, rear-yard family not supported | overlay PRESENT; rear yard withheld work_owed | test_s8_overlay_present_family_not_supported |
| S9 | user density statement True / None | statement passed as statement, in NO fact record | test_s9_user_density_statement |
| S10 | conversion / mixed building | adapter has NO input for it; building option withheld | test_s10_conversion_or_mixed_building_has_no_input_here |
| S11 | LANE_A off | engine lane-off document; ways gathered beside it | test_s11_lane_switch_off |
| S14 | not-read / not-stated / absent-outline (L1) | each carried as such; dependent way held back | test_s14_no_default_stands_for_a_fact |
| — | adapter imports | only gather + engine; no api, no lot-reach | test_adapter_imports_only_the_decision_entry_and_the_engine |
| — | carriers surfaced on StudyInputs | profile built, geometry carried, outline None; site_facts unchanged | test_assemble_surfaces_the_profile_and_geometry_carriers |
| O21 | outline provider injected / absent | prepared_outline surfaced / None (not fabricated) | test_outline_provider_surfaces_the_prepared_outline_and_none_is_absent |
| — | live default path | profile surfaced; geometry+outline seams OFF in prod | test_default_live_provider_surfaces_the_profile_carrier_inert |
| — | build_three_answer_inputs carry / omit | carriers set verbatim / each None | test_three_answer_inputs_carry_the_scenario_objects_inert |
| S13 | carriers populated, run through generate_results | emitted doc == committed fixture, byte-for-byte | test_s13_carriers_populated_emit_the_identical_document |
| S13 | carriers add no top-level key | no leaked key in the document | test_carriers_add_no_top_level_key_to_the_document |
| S12 | import guard | exactly one new permitted caller; others still offenders | test_only_task_m5_t130_bridge_and_facts_modules_import_the_decision_module |

Every place a missing value is handled (L1): outline None → reach unknown / street_lines empty, area
could-not-compare (S2); geometry None → reach None (S3); recorded area None → large-lot not stated,
outline never stands in (S5); profile None → every recorded column NOT_READ (S6); a user's statement
None → "not given" (S9). No truthiness test reads an unknown as "no"; nothing is invented.

## Byte-identity result (S13)

With the three carriers populated on `ThreeAnswerInputs`, `generate_results(env=LANE_A on)` emits a
document EQUAL to the committed fixture
`packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json` byte-for-byte
(contract 1.2.0; the journey test, the DXF and kit snapshot suites and `test_three_answers_benchmark.py`
pass untouched in check c). No new results fixture is added. The companion test proves the document
gains no top-level key named after a carrier (no leak).

## Mutation proofs (step 5) — each a single-line change in a COPY OUTSIDE the repository

A faithful copy of `services/api` + `packages` was made under the scratchpad (the repo files were
never touched); each mutation moved the pinned behaviour, then was reverted; the copy's baseline is
green again after all reverts (8/8 pinned tests pass). 7/7 CAUGHT:

- **MP1** `assemble_study_inputs` `property_profile=profile` → `None` → FAILS
  `test_assemble_surfaces_the_profile_and_geometry_carriers`.
- **MP2** provider `outline_provider(...)` → `None` (outline never threaded) → FAILS
  `test_outline_provider_surfaces_the_prepared_outline_and_none_is_absent`.
- **MP3** `build_three_answer_inputs` `property_profile=property_profile` → `None` → FAILS
  `test_three_answer_inputs_carry_the_scenario_objects_inert`.
- **MP4** adapter `profile=inputs.property_profile` → `None` → FAILS S1 (overlay no longer PRESENT).
- **MP5** adapter `outline=inputs.prepared_outline` → `None` → FAILS S1 and S4 (reach + outline area lost).
- **MP6** `engine._assemble_document` emits `wired_profile_present` from `inputs.property_profile` →
  FAILS both S13 tests (byte-identity moves the instant the engine reads a carrier).
- **MP7** `engine.py` text references the decision module → the import guard reports engine.py as an
  offender → FAILS the guard (it still bites every non-permitted app file).

## Questions of law met (named, not decided here)

1. Gap-K3 breadth (DB-168): the merged ZR 23-362(b) reading suggests the 30,000-sq-ft large-lot
   maximum may reach only eligible sites and so may not arise for a plain R6B lot. The adapter carries
   the decision module's answer unchanged (it applies K3 as the work order writes it); no result is
   decided or changed here.
2. The benchmark rear-yard reason: reading O16 holds the rear yard NOT supported under a recorded C2-2
   overlay, so the overlay-reading-owed withhold fires (the WAY matches work order H2; the reason is the
   owed overlay reading, not the 144.60-ft-beyond-corner reason). Carried through unchanged; not decided.

These belong to the decision module (M5-T129/T130) and its reviewers; this piece decides no question of
law.

## What is NOT shown (nothing is emitted)

The engine's results document is byte-for-byte unchanged (contract 1.2.0). No route returns the ways;
no screen changes; nothing under `apps/` is touched; no schema, fixture, DXF or kit snapshot changes;
no production switch is turned on. The adapter is called by no route — a later piece (the one that
emits) wires it on the real path.

## Checks (DIRECT exit codes; `/root/project/lanes-runtime/venv/bin/python`,
`PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, from `services/api` unless noted)

- **a** `python -m ruff check .` → **exit 0** ("All checks passed!").
- **b** `python -m pytest -q -p no:cacheprovider tests/scenario/three_answers` → **exit 0**, **305
  passed, 2 skipped** (claim head: 290 passed, 2 skipped; +15 new: 13 adapter + 2 byte-identity).
- **c** `python -m pytest -q -p no:cacheprovider tests/api/test_study_inputs_live.py
  tests/api/test_study_geometry.py tests/contracts tests/journey tests/spatial/test_lot_reach.py
  tests/cad tests/drawings` → **exit 0**, **1955 passed, 6 skipped** (the journey byte-identity, the
  DXF/kit snapshots and both import guards pass; the lot_reach guard is unchanged).
- **d** (repo root) `python3 tools/modularity_check.py --check` → **exit 0**; names none of the changed
  files (the warnings are pre-existing files: breakeven.py, max_envelope.py, tools/agent_supervisor/*).
- **e** the red proof (RED-1 exit 4, RED-2 exit 1) and the 7 mutation proofs (all CAUGHT, each pinned
  test exit 1; revert baseline exit 0) — above.
- **f** `git status --porcelain` and `git diff --name-status b416cf0d… HEAD` after the commit: exactly
  the 11 code/test files above plus this report; no forbidden path.

## Assumptions, limitations, doubt

- Outline seam: the second-provider shape means the live binding fetches the MapPLUTO lot twice when
  both seams are bound (off in production, inert); recorded as a future optimization, not a blocker.
- The S4/S7/S8 overlay outcomes are tied to the merged rows via `result_way_bridge_overlay.OVERLAY_SUPPORT_ROWS`
  (app code), not by re-reading the reference-case files, to avoid colliding with the other builder
  working later under `services/api/tests/rules/reference_cases/`; the existing
  `test_result_way_bridge_overlay.py` already ties those rows to the reference files.
- The adapter forwards an optional `registry`/`env` to `generate_results` (env controls the lane); it
  imports `RuleRegistry` only under `TYPE_CHECKING`, so its sole runtime imports are the decision entry
  and the engine result type.
