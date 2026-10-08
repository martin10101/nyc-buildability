# M5-T136 producer report — emit the results document in its three-way form (contract 1.3.0)

Producer: scenario-optimization-engineer (an AI agent), isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-ab5f6433565668bed`, reset to the claim-seam
head `99647cb66911d468816b90ccbb0e3f77c9b8f61e` before work.

This piece adds ONE new module (`three_way_document.py`) that transforms the engine's assembled
results document plus the decision ways into the contract-1.3.0 three-way document; the adapter
calls it. The engine, `dwelling_units.py`, `geometry.py`, `answers.py`, `building_option.py`, the
decision modules except the adapter, and every schema/copy/generated type stay byte-identical.

## Table (a) — every top-level block of the engine's document and what the transform does

The transform is a pure document→document function. "settled/conditional" shown values keep their
engine value object and get a value_states entry; a "withheld" value is withdrawn from values[] and
recorded as a withheld entry; a block worked out from a withheld result follows it.

| Engine block | Worked out from | Transform behaviour (settled / conditional / withheld) |
|---|---|---|
| contract_version | engine | set to `1.3.0` always |
| results_id/study_id/option_id/revision/computed_at | caller inputs | unchanged |
| out_of_date / out_of_date_reason | engine | unchanged |
| depends_on_fact_ids | engine | unchanged |
| lot_selection_statement / with_approvals_label | engine | unchanged |
| answers.floor_area_allowance | FAR rules × lot area | available: 4 own value ways → value_states; shown kept, withheld withdrawn; the 3 unit limits placed here (R567); standard unit limit gets a value object only when shown (O32). All-own-withheld → whole not_available with resolved_by/gap_kind |
| answers.permitted_envelope | height/coverage/yard rules | available: 6 height ways + coverage way → value_states; coverage withheld → withdrawn; rear_yard + setback placed here (R567), as value_states entries only when withheld |
| answers.building_option | plate × floors | own values all withheld (this milestone) → whole answer not_available (resolved_by/gap_kind); notes dropped with it |
| remaining_floor_area | owner-settled | unchanged ("Not confirmed") |
| shortfall | building option vs allowance | building option withheld → not_available, reason names it |
| addon_gains | two recomputed building options | each gain the engine shows available → not_available, reason names the withheld building option; the four already-not_available keep their own reason |
| best_combination | add-on gains (building options) | building option withheld → not_available, reason names it |
| completeness_line | add-on catalogue | unchanged (not worked from a withheld result) |
| status_strip / notices_count | engine | unchanged |
| floor_by_floor | building option | building option withheld → `[]` |
| floor_stack | building option + coverage | withheld → not_available, reason names both |
| existing_building | task M2-08 | unchanged (already not_available) |
| unit_estimate | the engine's r6b-dwelling-units rule | RESERVED: shared not_available, reason begins "Not known", names the Preliminary capacity estimate, says not built yet; no figure/formula/factor (O28) |
| geometry.lot_outline / streets / crs / units / measurement | recorded outline | unchanged |
| geometry.yards | rear-yard result | rear yard withheld → not_available with that result's reason, never "not required" (O29/DB-189); if the rear yard is shown (e.g. a non-overlay corner C2), the engine's "not_required" layer is kept |
| geometry.setback_lines_per_level | ZR 23-433 | unchanged (engine already not_available, carries no number) |
| geometry.envelope | coverage + height | coverage withheld → not_available with the coverage result's reason |
| geometry.floor_plates | building option | building option withheld → not_available with that result's reason |
| rule_versions / draft / street_width_case / scope | engine | unchanged (scope preserved so the cards still show it) |

No block of the emitted document is left carrying a number worked out from a withheld result
(verified by `test_s5_no_withheld_result_carries_a_number_anywhere`).

## Table (b) — every input state of the emit path, its outcome, and the test id

All in `services/api/tests/scenario/three_answers/test_three_answers_three_way_emit.py` unless noted.

| Input state | Outcome | Test id |
|---|---|---|
| benchmark lot, through the adapter | 1.3.0; floor-area & envelope available with value_states; remaining "Not confirmed"; shown numbers = real-lot.json | `test_s1_benchmark_emits_contract_1_3_0` |
| benchmark: the five standalone results | rear_yard+setback only in envelope value_states; 3 unit limits only in floor-area value_states; none in any values[] | `test_s2_five_results_placed_per_owner_decision` |
| benchmark: coverage | withdrawn from values[]; withheld entry carrying 103.93 ft reach reason | `test_s3_coverage_withdrawn_with_its_reach_reason` |
| benchmark: rear yard + geometry | withheld entry; geometry.yards not_available with the same reason; never "not required" (benchmark reason = overlay reading owed, see question of law) | `test_s4_rear_yard_withheld_not_not_required` |
| non-overlay corner lot, real reach | rear yard withheld with the 144.60 ft reach reason; geometry.yards carries it | `test_s4_rear_yard_reach_reason_carried_on_a_non_overlay_corner_lot` |
| full emitted document scanned | no withheld result's number anywhere; floor_by_floor empty; floor_stack/shortfall/best_combination/add-on gains not_available; 10075/29/100 absent as results | `test_s5_no_withheld_result_carries_a_number_anywhere` (RED proof inline) |
| benchmark: unit_estimate | reserved; no figure/formula/factor; reason begins "Not known"; reason_kind rule_not_implemented; no gap_kind field | `test_s6_unit_estimate_holds_no_legal_figure` (RED proof inline) |
| benchmark: conditional values | each conditional naming K20 + recorded-area; heights never "the maximum for this property"; no "professional review" | `test_s7_conditional_values_name_their_assumptions` |
| user density statement (with / without / contradicting) | with → unit limit conditional naming the statement; without → withheld; contradicting → held back, withheld | `test_s8_user_density_statement_is_conditional_only` |
| made-up interior lot 5,355 sq ft | floor area 10,710 (settled with K20 absent, conditional otherwise); unit limit withheld without density | `test_s9_made_up_interior_lot_shown_floor_area` |
| made-up corner lots C2 / C3 | C2 coverage 100 settled, rear yard shown in geometry; C3 coverage & rear yard withheld; K20-not-checked → conditional | `test_s10_made_up_corner_lot_coverage_from_reach` |
| no site geometry / no profile | only dependents withheld; no profile → all withheld; never a zero | `test_s11_a_fact_not_given_withholds_only_its_dependents` |
| regenerated fixture = adapter output (wiring/unchanged) | byte-for-byte equal | `test_wiring_emits_nothing.py::test_s12_adapter_emits_the_committed_three_way_fixture` |
| regenerated DXF + kit SVG | omit withheld results, say so | cad/drawings snapshot suites + §"line-by-line review" below |
| website reader, conditional + withheld + withheld headline | reason shown, never values[0]; "If <assumption>" shown | web: `three-answers.test.ts` S14 tests; `three-answers-panel.test.tsx` 1.3.0 tests; `journey-215-16-northern.test.tsx` W8 |
| hand-built document showing a withheld key / a number in a withheld entry | refused by the merged way-rule + schema (no new rule) | `test_s15_validator_refuses_a_number_in_a_withheld_result` |
| repo after the change | engine.py byte-identical, never names result_way; inner doc still 1.2.0; only the adapter calls generate_results | `test_s16_nothing_is_activated` |
| register updated, no human verdict | 3 entries re-rendered, every rule still "Not reviewed" | register `--check` + `tests/rules/test_zoning_rule_review_register.py` |
| standard unit limit shown with its formula | interior 5,355 + statement → value object value 16, label prints 10,710 ÷ 680 = 15.75 + factor + rounding; conditional; unit_estimate still reserved; without statement 16 appears nowhere | `test_s19_standard_unit_limit_shown_with_its_formula` |
| engine lane switched off | validates at 1.3.0; no number; no invented way entry; unit_estimate reserved | `test_s20_engine_switched_off_emits_no_number` |
| benchmark overlay (C2-2) tied to reference rows | rear yard withheld (overlay reading owed), other families shown; reads the reference rows AND runs the adapter | `test_s21_overlay_support_tied_to_the_reference_rows_at_the_adapter` |
| every text the transform writes | plain and true, no internal name/phrase | `test_every_text_the_transform_writes_is_plain_and_true` |

## Reference-case source of every expected value a test asserts

- 20,150 / 24,180 sq ft (floor area standard / qualifying) — `real-lot.json` rows L1, L2.
- 30 / 45 / 55 ft and building 65 ft (heights) — `real-lot.json` rows L3, L4.
- 103.93 ft (215 Place reach), 144.60 ft (corner reach) — `corner-reach.json` row `real-lot-reach`.
- interior lot 5,355 → 10,710 sq ft floor area, 16 units — `interior-lots.json` rows P5-floor-area, P5-units.
- C2 coverage 100 percent, "no rear yard required anywhere"; C3 coverage/rear yard not_known — `corner-reach.json` rows C2-coverage, C2-rear-yard, C3-coverage, C3-rear-yard.
- overlay "same as plain R6B" for floor-area ratio, lot coverage, heights, dwelling units; rear yard owed — `overlay-reading.json` + `step-p4-worked.json` (via `result_way_bridge_overlay`).

## Red proofs (step 2) — the green invariants fail on today's (pre-transform) engine document

Run outside the repository (`scratchpad/proofs_test.py`), on the benchmark adapter result:
```
RED PROOF S5 (engine floor_stack available, plate 10075 reappears): available 10075.0
RED PROOF S5 (engine best_combination available): available
RED PROOF S5 (engine addon_gain available count): 2
RED PROOF S6 (engine unit_estimate holds 29 and the formula): 29  20,150 ÷ 680 = 29.63
RED PROOF S3 (engine coverage value 100 shown): [100.0]
RED PROOF S4 (engine geometry.yards not_required): not_required
```
The S5 and S6 tests also carry these red-proof assertions inline (engine doc vs emitted doc).

## Mutation proofs (step 7) — one per newly pinned branch, run outside the repository

Each disables one transform branch at run time (monkeypatch; the repo file is unchanged) and shows
the matching invariant breaks:
```
MUTATION (no reserve)        -> emitted unit_estimate value = 29        (S6 invariant catches it)
MUTATION (no dependents)     -> floor_stack available, 2 floor rows     (S5 invariant catches it)
MUTATION (no geometry follow)-> geometry.yards status "not_required"    (S4 invariant catches it)
```
The withdrawal branch (a withheld value removed from values[]) is caught by the merged way-rule
validator: `test_s15_validator_refuses_a_number_in_a_withheld_result` refuses a shown value marked
withheld and a withheld entry carrying a number — no new validator rule was added.

## Line-by-line review of each regenerated saved file against work-order section 5

- `recorded_215_16_northern_journey.json` (contract 1.3.0): floor-area ratios/areas conditional on
  the recorded-area (K5) and K20 conditions; heights conditional (district limits, never "the
  maximum"); coverage withheld with the 103.93 ft reach (K1/L5); rear yard withheld (overlay reading
  owed on this lot), geometry.yards not_available, never "not required" (K4/L12/DB-189); setback
  withheld/"not covered" (K8/L13); building option whole not_available, floor_by_floor empty,
  floor_stack/shortfall/best_combination/add-on gains not_available (K6/K4/O31); the three unit
  limits withheld (L6 density-area gap, L7/L8 qualifying — K11/K13); unit_estimate reserved (R568);
  remaining_floor_area "Not confirmed"; scope block preserved. Matches section 5's "what the first
  screen can show" exactly.
- `tests/cad/snapshots/results_dxf/recorded_215_16_northern_journey.dxf`: lot-outline layer only; NO
  A-ZONE-ENVL / A-ZONE-YARD / floor-plate layers (grep count 0); the withheld reasons (coverage
  reach, setback, building option) appear as sourced annotation notes. Drawings follow the document.
- `tests/drawings/kit/snapshots/recorded_215_16_northern_journey.site_plan.svg`: lot outline kept;
  yards / setback_lines / floor_plates render as sourced `/geometry/.../reason` notes; NO envelope or
  floor-plate geometry; NO "not required" text.
- `recorded_215_16_northern_journey.massing.svg`: DELETED. The massing renders the envelope / floor
  plates, which are now withheld, so `render_massing` returns Unavailable and the snapshot test
  requires the file to NOT exist. This is the honest regeneration (the building massing is withheld).
  The path is in allowed_paths. NO OTHER snapshot changed (only the three journey-keyed files + this
  deletion); the brief's "stop if another saved file changes" condition did not arise.

## Every text the transform WRITES (pasted; guard-tested)

Authored constants (`three_way_document.py`):
- reserved unit estimate: "Not known. The Preliminary capacity estimate (a practical estimate of how
  many apartments might fit) is not built yet."
- floor stack: "The floor stack is not known: it is worked out from the building option and the lot
  coverage, and neither is known for this lot."
- shortfall: "The gap to the allowance is not known: it is worked out from the building option,
  which is not known for this lot."
- best combination: "The best combination is not known: it is worked out from building options,
  which are not known for this lot."
- add-on gain: "This gain is not known: it is worked out from building options, which are not known
  for this lot."
Built at run time:
- the standard unit-limit value object label, e.g. "Legal dwelling-unit limit, standard residences
  (new all-residential building): 10,710 ÷ 680 = 15.75 (dwelling-unit factor 680 square feet per
  dwelling unit; rounds up only at .75 or more)".
All carried geometry/way reasons come verbatim from the decision module (already guard-tested in
`test_result_ways.py` / `test_result_way_bridge.py`). The guard
`test_every_text_the_transform_writes_is_plain_and_true` checks the authored texts for no gap/reading
id, no task id, no "professional review", no "unsupported", no law-capture claim.

## Tests on optional values (no truthiness on an unknown)

The transform never applies `if x:` to a value that may be unknown. Every optional branch tests an
explicit state: `isinstance(way, Withheld)` (way kind); `answer_ways.whole_answer_not_available is
not None`; `engine_answer.get("status") != "available"`; `coverage_row is not None and
isinstance(coverage_row.way, Withheld)`; `inner.get("status") != "available"` for the inner unit
block; `_rule_version(...) is not None` for the rule-table source; `geometry.get("status") !=
"available"`. A missing engine answer, a missing inner block or a missing rule version is carried as
missing, never read as "no".

## Blocks worked out from CONDITIONAL results shown WITHOUT way entries (for the display piece)

The contract has no value_states slot outside the three answers, so these blocks carry conditional
numbers with no way entry of their own (not repaired here, listed for the display piece):
`completeness_line` (add-on catalogue, not a withheld result); `status_strip`; `scope.assumptions`
(the disclosed design/fact assumptions, e.g. lot depth 100 ft, floor-to-floor 10 ft); `rule_versions`.
On the benchmark these are not worked from a withheld result, so they are carried unchanged.

## Questions of law / fact met (named, not decided)

1. The benchmark rear-yard reason. S4/O29 describe the rear-yard reason as the independent reading
   (144.60 ft from the corner). The merged decision module (read-only this task) blocks the rear
   yard on the recorded C2-2 overlay FIRST, so on the benchmark its reason is "an independent reading
   of the commercial-overlay rear-yard rule for an all-residential building is owed". The transform
   carries the module's reason verbatim (it computes no reading); geometry.yards follows it and is
   never "not required". The 144.60 reach reason IS produced on a non-overlay corner lot with the
   same reach, and the transform carries it there (test
   `test_s4_rear_yard_reach_reason_carried_on_a_non_overlay_corner_lot`). This is a question for the
   reviewers: the honest benchmark reason is the overlay one, not 144.60; I did not edit the module.
2. `unit_estimate` reason_kind. The schema's shared not_available has no gap_kind there; the reserved
   block is `rule_not_implemented` (O28's reading: the estimator is a calculation that does not exist
   yet). Reviewers confirm or correct.
3. Overlay support (reading O16). The rear yard is withheld because the reference reading leaves it
   owed; a legal reading is never a conditional result. No law is decided here.

## What is NOT shown (nothing activated)

No route, no mount, no production switch, no website results panel / client / flag / dashboard tool /
browser journey, no apartment estimator and no Preliminary-capacity-estimate number, no schema /
schema-copy / generated-type change, no render.yaml / config / CI / dependency change, no rule-table
value change, no human verdict in the register. `app/main.py`, `app/config.py`, `render.yaml`
untouched. engine.py never contains `result_way`; its inner document still declares 1.2.0; the only
caller of `generate_results` under `services/api/app` is the one adapter.

## Checks (each with its DIRECT exit code)

| # | Check | Result | Exit |
|---|---|---|---|
| a | `ruff check .` (services/api) | All checks passed | 0 |
| b | `pytest tests/scenario/three_answers` | 324 passed, 2 skipped (base 305+2; +19 new) | 0 |
| c | `pytest tests/journey/test_215_16_northern_journey.py tests/contracts/test_results_three_ways_slot.py` | 50 passed (= base) | 0 |
| c' | `pytest tests/journey tests/contracts` (broader, no regressions) | 559 passed | 0 |
| d | `pytest tests/cad tests/drawings` | 1359 passed, 6 skipped (base 1366+6; fewer parametrized cases because the journey now draws fewer withheld layers — no failures) | 0 |
| e | `tools/modularity_check.py --check` | 725 files, 0 failures, 29 pre-existing warnings (none for the new files) | 0 |
| e | `.github/scripts/validate_contracts.py` | 23 schemas, 0 failures | 0 |
| f | `render_review_register.py --check` (after `--write`) | register check PASSED | 0 |
| f' | `pytest tests/rules/test_zoning_rule_review_register.py` | 44 passed | 0 |
| g | `npm ci` | 314 packages | 0 |
| g | `npm run lint` | 0 errors, 2 pre-existing warnings | 0 |
| g | `npm run typecheck` | tsc clean | 0 |
| g | `npm run test` | 111 files, 2429 tests passed | 0 |
| g | `npm run build` | build succeeded | 0 |
| h | red proofs + mutation proofs (scratchpad) | 4 passed, outputs above | 0 |
| i | `git status --porcelain` / `git diff --name-status` | only the allowed paths (21 files: 20 M + 1 D) | 0 |

The full api suite (`pytest -q`) and the browser e2e (`test:e2e`) are the orchestrator's to run at
the final candidate (not run here).

END-OF-REPORT
