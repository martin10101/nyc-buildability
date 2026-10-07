# Wave 5 (2026-10-07) - concurrency record for three pieces built at the same time

Written by the orchestrator before any builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Owner messages 107 and 108 of 2026-10-07 (D-090 source-052, rows R494 to R497): several independent parts at once, about five helpers, never on the same file. Bounds as recorded: at most five helpers at once, at most three building and at most four reviewing; heavy test runs one at a time; merges one at a time, in order; nothing built on unmerged work.

**One branch.** The three tasks ride on one branch, `task/wave5-facts-validators-captures` (worktree `/root/project/w-wave5`), from the integration head `596c034f`, the merge of task M0-T183. That merge commit's tree is identical to the head of its pull request, on which all 48 checks were green; the integration branch's own run on the merge commit was still in progress when this branch was made, and the orchestrator reads it as complete and successful BEFORE any builder's commit is integrated (recorded in the wave's progress entries). The orchestrator alone runs the ledger, git and the registry there. Each builder works in a worktree of its own and makes one commit per round, which the orchestrator cherry-picks.

**Order.** Merged so far of the work order's Part 0: the lot-reach measurements; contract 1.3.0; the module that decides how each result appears (nothing calls it). This wave: (1) carry the lot's recorded facts to that module, in new files, without changing what the engine emits; (2) the validators refuse the 1.3.0 documents the schema cannot refuse; (3) further law-text captures. After it: the piece that lets the engine's inputs be "not given", calls the decision in the real path and emits 1.3.0, with the regenerated saved results and drawings and the review-register entries; then the website's display.

## The pieces

| | M5-T130 | M5-T131 | M4-T033 |
|---|---|---|---|
| What | Carry the recorded facts to the decision module; new files only | The two results validators refuse what the schema cannot | Further law-text captures (source text only) |
| Depends on | M5-T127, M5-T129, M4-T032: accepted and merged | M5-T128: accepted and merged | M4-T031: accepted and merged |
| Depends on another piece of this wave | no | no | no |
| Builder | `scenario-optimization-engineer` | `backend-engineer` | `legal-corpus-engineer` |
| Files it may write | `services/api/app/scenario/three_answers/result_way_facts.py`, `result_way_bridge.py`, `result_way_bridge_*.py` (new); `services/api/tests/scenario/three_answers/test_result_way_facts.py`, `test_result_way_bridge.py`, `test_result_way_bridge_*.py` (new); ONE test function in each of two existing guard tests (`tests/scenario/three_answers/test_result_ways.py`, `tests/spatial/test_lot_reach.py`: the "nothing calls it yet" proofs); its report | `services/api/app/contracts/results_way_rules.py` (new); `services/api/app/scenario/three_answers/contract.py`, `services/api/app/contracts/study_contracts.py` (one call each); `services/api/tests/contracts/test_results_way_rules.py` (new); ONE test function of the existing guard `tests/contracts/test_contract_serializers.py` (the set of that folder's modules); its report | new files under `docs/research/zr-snapshots/v1/` and `services/api/app/_zr_snapshots/v1/`; `services/api/tests/rules/test_zr_snapshot_bundle.py` only if it lists ids; its report |
| Files it only reads | the decision modules; the engine's callers; the profile rules; the connectors; the spatial modules; the recorded benchmark pack; the reference cases through the loader | the schema; the fixtures; `test_results_three_ways_slot.py` | the existing captures; the two step-P4 readings |
| Forbidden | every existing file under `services/api/app/**`; every existing test; `packages/**`; `apps/**`; `docs/**` | `packages/**`; every other app file; every existing test | every existing capture; reference cases; rules; register |
| Gates | G0, G2, G3, G4 | G0, G2, G3, G4 | G0, G2, G3, G4 |
| Reviewers | `data-contract-verifier` (G3) and `qa-engineer` (G4): ADR-006 Tier B, "Scenario calculation" | a second `data-contract-verifier` agent (G3 and G4): Tier B, "Contract/schema: data contract + compatibility" | a third `data-contract-verifier` agent (G3 and G4) |
| Rule check | 7 rows | 2 rows | 1 row |

## Files shared between pieces

- **Written by more than one piece: none.** CORRECTED AT THE CLAIM SEAM, before any builder was started (the orchestrator's own run of `tests/contracts` at the claim head failed one existing guard test): M5-T130's new modules live in `services/api/app/scenario/three_answers/` and its tests in `services/api/tests/scenario/three_answers/`; M5-T131 alone writes in `services/api/app/contracts/` and `services/api/tests/contracts/`. Both write in the folder `services/api/app/scenario/three_answers/`, each only files of its own name: M5-T130 `result_way_facts.py` and `result_way_bridge*.py`; M5-T131 the one call in `contract.py`. Three existing guard tests are changed, each by one piece only and in one test function only: the two "nothing calls it yet" proofs by M5-T130 (it is the first caller of the decision module and of the lot-reach module); the list of the contracts folder's modules by M5-T131.
- **Read by one piece while another writes nearby:** M5-T130 reads reference rows through the loader; no piece of this wave writes the reference cases. M5-T130's tests may validate way objects against the bundled schema, which no piece changes. M5-T131 changes what the validators refuse for a 1.3.0 DOCUMENT; M5-T130 emits no document. **Watch at integration:** after all commits are on the branch the orchestrator runs `tests/contracts`, `tests/scenario/three_answers`, `tests/journey` and `tests/rules` together.
- **Written by the orchestrator only:** `project-control/**` and `docs/DISCOVERY_BACKLOG.md`.
- **Shared test surface:** the full `services/api` suite covers all three. It is run once, by the orchestrator alone, on the branch after all commits are integrated. Before any push the repository's contract validator is run (no schema changes are expected).

## Limits kept

- Helpers at the same time: at most five; at most three building; at most four reviewing. Planned peak: three builders, then up to four reviewers as the builders finish.
- Producer and reviewer are different agents for every piece.
- Every review names the exact head it reviewed. A commit to a piece's files after its review voids that review. A failed review is recorded as failed, in the task's progress log and in its review record, and the piece goes back to its builder.
- One pull request for the wave, merged by the fail-closed step on a fully green run.

## Stop conditions

- A builder's commit touches a file outside its own allowed paths: that commit is not integrated; the piece goes back to its builder.
- M5-T130 cannot be built without editing an existing file: the builder stops and reports.
- M5-T130's builder cannot tell "asked for and served empty" from "not read" in the recorded data: every such column is "not read"; nobody guesses.
- M5-T131 would refuse a fixture that is valid today: the builder stops and reports.
- A piece fails its review and cannot be corrected quickly: it is taken off the branch before the wave's freeze so that it does not hold the others.
- Any Tier D matter (a secret, a payment, production): stop and tell the owner.

## Merge order

The wave merges as one pull request after all three tasks are accepted. If one piece is taken out, the others merge first.
