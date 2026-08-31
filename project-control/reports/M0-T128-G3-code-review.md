# M0-T128 - G3 report (independent code-reviewer, read-only; security lens included) - VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31. VERDICT: PASS with 2 required corrections,
BLOCKING for acceptance per gate-verdict semantics: C1 confine the cross-task driver to the
limited-auto + owner-enable envelope (a supervised --max-tasks>1 start currently reaches it -
low practical risk, but the authorized-envelope invariant fails) with a typed refusal + a
removal-sensitive test; C2 add a real _run_loop-altitude cross-task test (shared-run_id
budget-resume + close-run interaction) and document the per-journey shared-budget semantics.
All other dimensions PASS: eligibility strong (eleven fail-closed visible categories, eligible
set exactly {claimed}, real stale detection), exactly-once/crash genuine (advance-before-select,
journal-reopen tests), security clean (no execution surfaces, safe parsing, no secrets),
certified single-task shape byte-behavior-identical, Pyright hints adjudicated false-positive/
benign. Corrections routed to ONE fresh remediation producer with the G4 verdict.

---VERBATIM-BEGIN---
I have completed the review. Let me confirm the budget-resume path is the clean-resume (no conflict) case for stable run_id/budget, which characterizes the C2 finding accurately.

The `RunBudgetLedger.start()` analysis (run_budget.py:341-434): a second task with the **same** run_id and **same** budget digest takes the resume branch cleanly (no `budget_conflict`); the driver never changes `--checkout` (run_id source) or budget-affecting args, so the digest is stable. The shared budget then bounds the whole journey - coherent but undocumented, and the real `_run_loop` cross-task path is untested (family 1 uses `real_run_one`, not `_run_loop`).

Here is my gate report.

---

# G3 (code-reviewer) Gate Report - M0-T128 (Amendment-25 Stage-3 wiring)

**Task:** M0-T128 - wire the exactly-once next-task machinery into the live limited-auto path (D-024 Amendment 25, R400-R409)
**Reviewed identity:** material `1485c73` (verified stable: `git diff 1485c73 HEAD -- tools/ .github/ docs/...` empty; HEAD `533f43a`). Diff `git diff 7576e0d 1485c73`. In-regime (D-024 ALL).
**Reviewer:** code-reviewer (independent, read-only). Security lens included (roster names security-reviewer for this packet).

## VERDICT: **PASS with 2 required corrections (blocking for acceptance)**

The Stage-3 wiring is thorough, correct across the eligibility/exactly-once/crash/coverage dimensions, and honest in its test split. Two issues must be resolved before acceptance: **C1** - the queue driver is not confined to the authorized limited-auto+owner-enable envelope (a supervised `--max-tasks>1` start reaches it), contradicting the design record's own claim and the R402/R400 authorized path; and **C2** - the real `_run_loop` cross-task path (shared run_id budget resume + D6 on the shared journal) is unexercised and its per-journey budget semantics are undocumented. Reproduced: `cross_task`+`next_task` **53 passed**, ruff clean, modularity 0 failures.

---

## Required corrections (blocking)

**C1 - Confine the cross-task driver to the authorized limited-auto + owner-enable envelope (R400/R402; dimension 2).** `run_task_queue` (next_task.py:763) performs NO `args.mode` / `owner_enable_bounded_auto` check (grep confirms: the only `mode`/`limited` tokens are docstrings and the final-return label at :881). The cmd_start dispatch ternary (cli.py:3069) enters the driver for **any** dispatchable mode when `max_tasks>1 or packet_queue`. `bounded_mode_gate` only refuses *limited-auto-without-enable* before dispatch; it does not confine the driver. Therefore a `--mode supervised --max-tasks 2 --packet-queue q.json` start **reaches the driver** - violating the invariant "a start WITHOUT (owner-enable-bounded-auto AND limited-auto) cannot reach the queue driver." The design record sec 7 claim ("Everything sits behind the pre-existing `bounded_mode_gate`") overstates the confinement. Practical risk is LOW (supervised gates every provider cycle, so no autonomy escape; shadow is inert because `run_reached_complete` is False), but the authorized-envelope invariant does not hold. **Fix:** assert `args.mode == "limited-auto"` in `run_task_queue` (and rely on `bounded_mode_gate` for the enable), refusing multi-task in other modes with a typed refusal - OR explicitly justify and document supervised multi-task as R400/R402-compliant. A removal-sensitive test on the confinement is required.

**C2 - Test the real `_run_loop` cross-task path and document the shared-run_id budget semantics (R400/R402; dimensions 1, 7).** Family 1 (`LiveCrossTaskSelectionTests`, test:287) drives `real_run_one` - a real `SupervisedLoop`+journal+CAS - but **not** `cli._run_loop`. In the real cli path the driver passes the same `args` (hence the same checkout-derived `run_id`, since the commissioning command omits `--run-id`) to every task's `_run_loop`, which each call `budget_ledger.start()`. My analysis of `RunBudgetLedger.start()` (run_budget.py:341-434) shows task 2 takes the clean **resume** branch (stable run_id + budget digest -> no `budget_conflict`), so the owner-set run budget bounds the **whole journey** - coherent, and handled by `between_task_seam`'s `run_budget.exhausted` read, but **undocumented** in the design record and **untested** at the `_run_loop` altitude (along with `plan_close_run` COMPLETE->IDLE and D6 dispatch-intent on the shared journal across tasks). **Fix:** add a real `_run_loop` cross-task test (at least the budget-resume + close-run interaction) and document the per-journey shared-budget semantics - before the R407 live journey relies on this path.

---

## Per-dimension findings

**1. R400 correctness (control-flow traced, not the report):** delivered. `run_task_queue` (next_task.py:763-887): first task runs via `run_one=_run_loop` unchecked (owner-typed); on `run_reached_complete` True (real COMPLETE + last-cycle COMPLETE decision + reviewed checkpoint id, :702-725) it calls `record_advancement` CAS (:855) **before** the next iteration's `between_task_seam`+`evaluate_eligibility` (:820-829) - advance-before-select ordering confirmed. Close-run is performed by the next task's `_run_loop` via the wired `plan_close_run` (cli.py:2687), correct on the shared journal. Per-task launch-seam re-enforcement is doubled: driver `evaluate_eligibility`->`enforce_launch_bindings` (:638) AND `_run_loop`'s runtime backstop. Bounded by `--max-tasks` (default 1, `max(1,int(...))` at :783; bound break :815). PASS (subject to C2's run_id note).

**2. Owner-gate integrity (R402/R403):** the certified single-task path is **byte-behavior-identical** - the ternary is False for defaults (`max_tasks=1, packet_queue=None`) so `_run_loop` is called directly (verified: `DefaultShapeTests`, and the ternary at cli.py:3069). No new activation surface; no R595/broker/allowlist/audit-chain change; the two new flags have safe defaults and are deliberately NOT added to `REQUIRED_START_FLAGS`. **But see C1** - the driver is not confined to limited-auto.

**3. Eligibility (R405):** `evaluate_eligibility` (next_task.py:551-651) - eleven categories, cheapest-first, first-failure-wins, each returning a stable `code`+`reason`; the driver audits `cross_task_candidate_skipped` and records a `skipped` step (:830-834) - never silent. Eligible-status set is **exactly `{"claimed"}`** (:393). Owner-gate fields, blockers, dependency-acceptance (reads each dep's own packet `status=="accepted"`, so advancement!=acceptance), worktree-missing/primary-checkout/binding, and stale-content are all fail-closed. Stale detection is real: CAS-once digest snapshot at queue-read (:519-531, :796) vs a re-read at selection (:573, :645); a mid-journey edit reads stale and the snapshot survives a restart (`StalePacketTests`). No path can silently select owner-gated/blocked/stale work. PASS (strong).

**4. Exactly-once / crash (R402):** advance-before-select confirmed; genuine journal reopen tests - `CrashMatrixTests::test_crash_BEFORE_advancement...` (incomplete->nothing advanced->`reopen()`->re-run advances once) and `...AFTER_advancement_before_dispatch...` (`record_advancement`->`reopen()`->advanced task skipped as `already_advanced`, next selected, no double-advance). Duplicate provider output loses the CAS (`newly_recorded=False`). PASS.

**5. Security surfaces:** no command execution anywhere - `--packet-queue` is `read_text`+`json.loads` (:472-486), packets `read_bytes`+`json.loads` (:499-511); no `subprocess`/`eval`/shell. Owner-supplied paths (`packet_path`/`worktree`/`repo`) are constrained by eligibility (`worktree_missing`, `worktree_primary_checkout`, `enforce_launch_bindings`) before becoming the worker cwd (Popen `shell=False`). `--max-tasks` is argparse `int` + `max(1,...)`. New durable keys `task_queue/queued_digest/<id>` hold only a sha256 string; audit rows carry task_id/worktree(abs path, public repo)/code/reason - no secrets/tokens/PII. Minor: `_audit` (:654-661) swallows all exceptions best-effort, but skip visibility is also carried in `TaskQueueResult.steps`, so "never silent" holds via the result. PASS.

**6. Scope / quality:** all changed files within allowed_paths (cli.py, next_task.py, `test_agent_supervisor_cross_task.py`, reports). Modularity: next_task.py grew to 691 SLOC - a `review_signal` **warning** (above 600, below 750), 0 failures; the module is cohesive (cross-task decision logic: close-run, advancement, selection, eligibility, driver) and the design record sec 11 justifies placement (packet-designated home; a new module is outside allowed_paths) - acceptable but near the justify threshold, split advisable next growth. **Pyright hints adjudicated:** the flagged `hashlib`/`json`/`os`/`pathlib`/`Mapping` imports are **all used** (511/477/627/472/449 etc.) - false positive, and ruff is clean (no F401). The next_task.py:451 "unreachable" hint is a **benign defensive `isinstance` check** on untrusted JSON input (Pyright deems it unreachable only because the param is type-hinted `Mapping`; the runtime guard is correct fail-closed validation). PASS.

**7. Coverage honesty (dimension 7):** the split is **honest and adequate**. Family 1 drives the REAL `SupervisedLoop`+`StateMachine`+journal+`plan_close_run`+`record_advancement` with only runner/reviewer faked (`real_run_one`, test:207-244) - genuine integration, asserting real dispatch order + real CAS advancement + COMPLETE. Families 2-10 use a scripted `run_one` that exercises the **real** driver mechanisms (eligibility codes, between-task seam, staleness, crash reopen, dedup) - the scripted callback is the provider-loop seam, not the driver; each family asserts a real mechanism, none tests only the harness. Removal-sensitivity holds. The only altitude gap is the real `_run_loop` cross-task path (**C2**).

## Reproduced commands / numbers (read-only)
- `pytest tools/test_agent_supervisor_cross_task.py tools/test_agent_supervisor_next_task.py -q` -> **53 passed**
- `ruff check tools/agent_supervisor/next_task.py tools/agent_supervisor/cli.py` -> **All checks passed**
- `modularity_check.py --report` -> next_task.py `review_signal` warning; **0 failures** overall
- import-usage grep (all five flagged imports used); `sed -n 448,452p` (line 451 defensive check); `git grep` (advancement machinery zero external callers before this task; driver has no mode gate)

---

**Requested gate result: PASS with 2 required corrections (C1 gate-confinement, C2 real-path coverage + documented budget semantics), both BLOCKING for acceptance.** The wiring correctly delivers R400 cross-task selection/advancement with fail-closed eligibility (R405) and genuine exactly-once/crash safety (R402); the single owner-gate gap (C1) is narrow and fixable with a mode assertion, and C2 is a coverage/documentation obligation before the R407 live journey. I made no writes outside `.claude/agent-memory/code-reviewer/` and ran no `project_control.py`/git-write/`gh`/supervisor write verb.
---VERBATIM-END---
