---
name: supervisor-run-loop-and-cmdstart-test-altitude
description: How to unit-test the agent_supervisor start dispatch path - real cli._run_loop harness, the cmd_start gauntlet ceiling, and the exec-real-source-line pattern
metadata:
  type: project
---

Testing the `tools/agent_supervisor` start/dispatch path (learned wiring M0-T128 cross-task driver).

**Driving the REAL `cli._run_loop` with a faked provider (no subprocess).** `_run_loop`
builds the runner/reviewer FROM the controller config, so: supply a real `config.toml`
+ `model_selection.toml` (minimal shape needs `[codex]`/`[claude]` `allowed_models`,
`[controller] default_mode`, `[model_chain] orchestrator_preference`, `[limits]`), then
monkeypatch `cli.ClaudeRunner` and `cli.CodexReviewer` to factories returning COMPLETE-
returning fakes. Key the fake to the task via `config.cwd` (ClaudeRunner) / `repo`
(CodexReviewer) -> normcase path -> (task_id, branch), so ONE factory serves every task
in a journey. The fake runner MUST provide `executable_identity()` (called by _run_loop
at ~cli.py:2819 before the worker-actuation channel) plus `.config`, `.run_unit`. The
real `SupervisedLoop` then runs to COMPLETE with these fakes (EvidenceCollector fails
closed to unknown facts on a non-git worktree - no git repo needed). This proves the
_run_loop WRAPPER: shared-run_id `RunBudgetLedger.start()` clean-resume (task2 emits
`run_budget_resumed`, never `budget_conflict`), `plan_close_run` COMPLETE->IDLE on the
shared journal (a `state_transition` with `policy_result=run_closed`), and D6
`record/reconcile_dispatch_intent` across the boundary (`journal.pending_effects()` empty).

**Full `cli.cmd_start` (via cli.main) is golden-run altitude, NOT unit-testable cheaply.**
Its live_revalidation/recover_boot gauntlet requires the `auth` and
`cli_capability_manifest` probes to pass, which need a REAL launched provider process
(`script_as_executable` + a fake claude script emitting a stream-json checkpoint) and a
live capability manifest. A bare `cli.main(["start",...])` with a dummy executable
refuses at recover_boot: `revalidation failed for ['auth','cli_capability_manifest']`
(UNSAFE_OR_DRIFTED). `test_agent_supervisor_model_chain.py` CrashResumeTests is the
precedent that does the full spawn.

**Testing an inline dispatch expression without refactoring (the cli.py:3069 ternary).**
When production law forbids growing a net-zero file (cli.py 2953/2953) so you can't
extract the line into a testable helper: extract the VERBATIM expression from the
function's own source with `inspect.getsource` + `ast` (walk for the `run = <IfExp>`
assign, `ast.get_source_segment`), then `exec(compile(seg,...))` in a namespace with the
real `next_task`, a spy `_run_loop`, and real args. A spy wrapping `nt.run_task_queue`
captures the injected `run_one` to assert `is cli._run_loop`. This "provably executes the
real line" (regressions in condition/args change the executed bytes) and is materially
different from the inline re-implementation a gate will reject. See [[agent-supervisor-rotation-and-model-machinery]].
