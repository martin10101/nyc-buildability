# M0-T130 G2 self-check (producer: orchestrator-defect-runner)

Recorded 2026-08-31 at commit `20bfa449` (implementation landing; supervisor tree moved
`b3921009...` -> `37020c37...`). Full design + coverage narrative:
`M0-T130-reserved-turn-fix.md` (committed alongside the change).

- **Green:** runner pack `tools/test_agent_supervisor_runner.py` **78 passed** (74
  baseline + 4 new `ReservedTurnDeliveryTests` nodes; 1 test repurposed IN PLACE to the
  fixed semantics — the pre-fix two-results assertion was the defect's own behavior).
- **Whole supervisor suite** (every `tools/test_agent_supervisor*.py`, one process):
  **3,039 passed, 2 skipped, 0 failed** in 256.5s. Baseline reconciliation: 3,035
  (M0-T129 certification) + 4 new = 3,039; no test file removed.
- **Red-on-mutant:** launch-time writes temporarily restored ->
  `test_an_absorbing_cli_never_sees_an_early_second_prompt` FAILED with the live shape
  (`missing_checkpoint` after the merged result) — 1 failed / 3 passed — mutant
  reverted, pack green again. The fix, not the fixture, carries the behavior.
- **Teeth:** `ruff check` clean on both touched files; `modularity_check --check` 0
  failures (claude_runner.py baseline-tracked, +~45 SLOC, single responsibility
  unchanged); `supervisor_command_doc_check.py` exit 0 (no command shape changed).
- **Scope:** the diff touches exactly the three allowed paths; no journal key, flag,
  schema, broker, or loop/turn_budget change; journal untouched (PAUSED_RECOVERY,
  transitions 26); wt-m0t107 `c5c6ff7` / wt-m0t109 `1c06957` clean; PR #241 untouched.
- **Honest residuals** (disclosed for G3/G4): CLI max-turns semantics across a second
  written turn unmeasured (either semantic strictly improves on the absorbed shape;
  worst case lands in the fast honest-failure path); the absorption fixture is a fake
  reproducing the journey-3 measured behavior, not a recorded live-CLI capture.
