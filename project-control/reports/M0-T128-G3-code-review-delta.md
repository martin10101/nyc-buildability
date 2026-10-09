# M0-T128 - G3 DELTA report (independent code-reviewer, read-only) - VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31, re-verdicting C1/C2 at the remediated identity
de18f27. DELTA VERDICT: PASS - C1 confinement guard verified first/typed/audited with the
enable-mode division correctly documented and mutation-sensitive tests; C2's real cli._run_loop
two-task test reproduces the reviewer's own budget clean-resume analysis exactly (started x1,
resumed x1, no conflict; run_closed between tasks; empty pending_effects across the boundary);
delta regression clean (+22 guard-only lines, cli.py untouched); Pyright hints adjudicated
benign/false-positive; the G4-1 verbatim-extraction approach judged honest and adequate.

---VERBATIM-BEGIN---
Both corrections are genuinely and accurately resolved. The design-record sec 7 correctly states the enable/mode two-half division and honestly retracts the prior incomplete claim; sec 5A documents the shared-budget semantics exactly matching my run_budget.py:341-434 analysis. Here is my delta gate report.

---

# G3 (code-reviewer) DELTA Gate Report - M0-T128 (C1/C2 remediation)

**Task:** M0-T128 - Stage-3 cross-task wiring (D-024 Amendment 25)
**Prior verdict:** PASS with 2 required corrections (C1 gate-confinement, C2 real-path coverage), recorded.
**Reviewed identity:** material `de18f27` (verified stable: `git diff de18f27 HEAD -- tools/ .github/ docs/...` empty; HEAD `1d00e7b`). Delta `git diff 93addac de18f27`.
**Reviewer:** code-reviewer (independent, read-only). Reproduced numbers below are my own.

## DELTA VERDICT: **PASS**

Both blocking corrections are genuinely and accurately resolved with removal-sensitive tests, the design record honestly retracts the prior incomplete claim, and the delta introduces no behavior change outside the corrections. Reproduced: cross_task pack **45 passed**; targeted C1/C2/G4-1 classes **8 passed**; ruff clean; modularity 0 failures.

---

## Correction re-verdicts

### C1 - Envelope confinement - **RESOLVED**
- The guard is **genuinely first**: `mode = str(getattr(args, "mode", "") or "")` / `if mode != "limited-auto": ... raise NextTaskError("cross_task_mode_refused", ...)` at next_task.py:792-802, positioned **before** `primary = str(checkout)`, `max_tasks`, `first_packet = _read_packet_file(...)`, and the successor-snapshot loop (confirmed by diff position). No packet is read, snapshotted, or dispatched on refusal.
- **Typed + audited**: raises `NextTaskError` code `cross_task_mode_refused` and emits a `cross_task_mode_refused` audit row; rides the existing `except (..., next_task.NextTaskError)` arm at cli.py:3070 (**cli.py untouched** in this delta - a report, not a traceback).
- **Enable/mode division correct** (design-record sec 7): `bounded_mode_gate` enforces the owner-**enable** half pre-dispatch (limited-auto without `--owner-enable-bounded-auto` refused by name, pre-existing/verified); the driver enforces the **mode** half. Sec 7 explicitly retracts the prior incomplete "everything sits behind bounded_mode_gate" claim and states the invariant now holds. Accurate.
- **`ModeConfinementTests` (4) removal-sensitive** (judged by binding + reproduced): `_refused(...)` asserts the typed code AND the absence of side effects - `self.dispatched == []`, `queued_digest_key("M0-TB") == ""` (no snapshot), `cross_task_mode_refused` audited, and **`cross_task_dispatch` NOT** audited - for supervised+queue, shadow+max_tasks, and supervised+max_tasks-only; `test_limited_auto_multi_task_proceeds` proves the authorized path still dispatches 2. Reverting the guard makes the three refusal tests dispatch and fail - genuine mutation sensitivity.

### C2 - Real `_run_loop` cross-task coverage + documented budget semantics - **RESOLVED**
- `LiveRunLoopCrossTaskTests::test_two_task_journey_through_real_run_loop` (test:947) **genuinely reaches the REAL `cli._run_loop`**: `LiveLoopBase.patch_providers` monkeypatches **only** `cli.ClaudeRunner`/`cli.CodexReviewer`; everything else in `_run_loop` runs for real (config/model_selection load, launch-seam binding, `RunBudgetLedger.start()`, `plan_close_run`, the real `SupervisedLoop` with D6). It calls `nt.run_task_queue(args, ..., cli._run_loop)`.
- Asserts exactly the C2 concerns: `run_budget_started` **x1** + `run_budget_resumed` **x1** + **no** `budget_conflict`/`run_budget_refused` (the clean shared-run_id resume), a `run_closed` **COMPLETE->IDLE** state_transition on the shared journal between tasks, and `journal.pending_effects()` **empty** across the boundary (D6). This reproduces my run_budget.py:341-434 analysis (same run_id + stable budget digest -> resume branch, never conflict).
- Design-record **sec 5A** documents the per-journey shared-budget semantics accurately: shared run_id (driver re-binds only task_packet/worktree/branch/repo), clean resume vs conflict-only-on-different-bounds, between-task `run_budget.exhausted` backstop, shared-journal close-run, and D6 reconciliation - all matching the code and the test.

## Delta regression - clean
- next_task.py **+22 lines (guard only)**, prepended to `run_task_queue`; cli.py untouched. The guard is purely additive: for limited-auto it passes and the body runs unchanged (all existing families still pass, 45 total); for the certified single-task default (`max_tasks=1, packet_queue=None`) the driver is never entered (cli ternary -> `_run_loop` directly), so the guard never executes - byte-behavior-identical. No behavior change outside the correction.
- **Pyright hints adjudicated:** next_task.py:711 is the `if not isinstance(run, Mapping): return ...` defensive guard in `run_reached_complete` - the same benign class as :451 (the `return` is "unreachable" only because the param type-hint assumes a Mapping; correct fail-closed validation of a runtime `run` dict). next_task.py:794 is the mode-guard body (`_audit(...)`) - **proven reachable** by the 4 passing `ModeConfinementTests`, so any "unreachable" hint there is a false positive. ruff clean; no F401/real dead code.

## G4-required-correction #1 (verbatim cli.py:3069 via inspect+ast) - honest and adequate
`CmdStartDispatchTests` extracts the **verbatim** `run = (...)` ternary from `cmd_start`'s own source (inspect.getsource + ast, self-guarded by `test_the_extracted_line_is_the_real_dispatch_expression` asserting both branches + `max_tasks` + `packet_queue`) and `exec`s it for both branches: multi-task routes to `run_task_queue` with the real `cli._run_loop` injected as `run_one`; the default calls `_run_loop` directly. This closes the exact inline-re-implementation gap G4 named in `DefaultShapeTests` by exercising the **real dispatch bytes**, while honestly documenting why full `cmd_start` is impractical in a focused unit test (its live-revalidation gauntlet - `auth`/`cli_capability_manifest` probes - needs a launched provider + live capability manifest, golden-run altitude). The `exec` of extracted source is test-only, guarded, and well-justified. **Adequate, not a gap.**

## Reproduced commands / numbers (read-only)
- `pytest tools/test_agent_supervisor_cross_task.py -q` -> **45 passed**
- `pytest ...::ModeConfinementTests ...::LiveRunLoopCrossTaskTests ...::CmdStartDispatchTests -q` -> **8 passed**
- `ruff check tools/agent_supervisor/next_task.py` -> **All checks passed**
- `modularity_check.py --check` -> selected 335 files; **failures 0** (next_task.py remains a non-blocking `review_signal` warning - unchanged justification; split advisable on next growth)
- `git diff ... next_task.py` (guard-only, first-position); `sed -n 709-713;792-796` (Pyright sites)

---

**Requested gate result: PASS.** My two prior blocking corrections are resolved with reproducible, removal-sensitive evidence at material identity `de18f27`: C1's confinement guard is first/typed/audited with the enable-mode division correctly documented, and C2's real-`cli._run_loop` cross-task test proves the clean shared-run_id budget resume + close-run + D6 exactly as analyzed. Delta regression is clean and the G4-#1 dispatch-line approach is adequate. I made no writes outside `.claude/agent-memory/code-reviewer/` and ran no `project_control.py`/git-write/`gh`/supervisor write verb.
---VERBATIM-END---
