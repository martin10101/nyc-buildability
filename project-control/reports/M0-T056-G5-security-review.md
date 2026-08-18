# M0-T056 — G5 security review (VERBATIM reviewer return)

Independent reviewer: `security-reviewer` (read-only; reviewer != producer backend-engineer).
Returned via agent channel; saved verbatim.

---

All relevant tests pass (R595 actuation 16/16; frozen turnover modules 79/79; loop/process/recovery 192 passed, 1 skipped). I have completed independent verification of all six review dimensions. Here is the G5 report.

---

# G5 Security Review — M0-T056 (R595 Production Turnover Actuation)

**Reviewed SHA:** `81960395a6bb90fc359ccb03dd5cac7a1319c847` (HEAD == reviewed SHA, confirmed)
**Branch:** control/session16-codex-golive (worktree session15-acc)
**Reviewer:** independent (read-only); producer ≠ reviewer
**Scope:** highest-stakes gate — wiring the channel that lets the Codex supervisor auto-launch a successor session. Bar: R595 lifts EXACTLY ONE thing (turnover auto-launch actuation), weakens NO other hold.

## Change surface (independently confirmed)
`git diff --name-only 8196039^ 8196039` = exactly 6 files: `worker_turnover.py`, `loop.py`, `cli.py`, `claude_runner.py`, new `tools/test_agent_supervisor_r595_actuation.py`, and the producer report. Diffstat: 997 insertions / 19 deletions.

## Findings against the six required dimensions

**1. Bounded scope — no other hold moved (AS-6 / R348) — PASS.**
- Forbidden paths untouched: no diff under `services/api/**`, `apps/web/**`, `packages/contracts/**`, or any `config.toml` (the `C:/SupervisorController/config.toml` protected path is outside the repo and correctly absent from the tree).
- Zero diff (verified via `git diff --stat`): `os_acl.py`, `config.py`, `push_policy.py`, `github_flow.py`, `process.py`, and the REUSED-UNCHANGED mechanism `turnover_controller.py`, `turnover_adapters.py`, `model_turnover.py`, `recovery.py`. Audit append/immutability (`audit_log.py`) untouched. `process.py` argv/HARD_DENY guards and five-borough/geospatial scope untouched.

**2. Fail-closed actuation — PASS.**
- `worker_turnover.default_actuation_authorization` = `getattr(config, "turnover_actuation_authorized", False) is True` — strict identity, so any non-True value (1, "true", "yes") fails closed (proven by `test_non_true_values_fail_closed`).
- The `turnover_actuation_authorized` config attribute is set in exactly one place (`cli.py:2601`) from `getattr(args, "authorize_turnover_actuation", False)`; the flag is `action="store_true"` (default False, no env/config default). `config.py` has ZERO references to either name — it is NOT a mode default and is NEVER read from the protected controller config. An operator cannot enable live actuation via config/mode alone.
- Orchestrator watchdog: launches ONLY on `verdict.should_turn_over` (grounded `FABLE_EXHAUSTED`). `NOT_EXHAUSTED`/`AMBIGUOUS_FAIL_CLOSED` append `orchestrator_watchdog_no_turnover` and return without touching the launcher; an unreadable `--exhaustion-signal` refuses (exit 1) before any controller is built (`FailClosedTests`, 3 tests green).

**3. Containment / no-duplicate (C1) — PASS.**
- C1 gate `containment_precondition()` admits only `kind == job_object`; anything else, including an unprovable/exception case, returns refuse. Enforced on BOTH layers: `_build_worker_actuation_channel` returns `controller=None` on a non-job_object host, and the watchdog records `orchestrator_watchdog_containment_refused` (`policy_result="REFUSED"`) and never launches.
- Double-layer worker defense verified: even if `--authorize-turnover-actuation` sets `turnover_actuation_authorized=True` on a non-job_object host, `worker_controller` is None, and `WorkerTurnoverIntegration.evaluate` hits its explicit `self._controller is None` branch → record-intent-only, no launch.
- Survivor block: `_child_survivor_predicate` wires M0-T053 `account_for_children`; unreadable child state fails CLOSED to "survivor present" → `BLOCKED_SURVIVOR`, dedup NOT consumed (`NoDuplicateWorkerTests`, incl. registering this live PID as a surviving child).
- Exactly-once: deterministic `event_id` (SHA over `(signal_text, checkout)` / `(run_id, cycle)`), durable `already_actioned`/`mark_actioned` in the frozen hash-chained `HashChainedAuditSink`; a repeat detection returns `SUPPRESSED_DUPLICATE` (`test_second_detection_of_same_exhaustion_launches_nothing`).

**4. Successor integrity — PASS.**
- Successor model hard-pinned to `ALLOWED_SUCCESSOR_MODEL_ID="claude-opus-4-8"` / `ALLOWED_SUCCESSOR_EFFORT="xhigh"` (frozen constants). Controller pre-check refuses any other `requested_model`/`requested_effort` → `INVALID_MODEL_REFUSED`; caller-supplied model is never read into argv/result; launcher fails closed if the runner echoes a non-pinned model. The watchdog builds `TurnoverContext` without overriding model/effort (defaults = the pinned pair); `--current-model` is used only to attribute the exhaustion signal, never as the successor model.
- Argv built by the frozen adapters: worker argv via `claude_runner.build_argv` (emits `--model claude-opus-4-8`, argv-safe-checked); orchestrator argv via `assert_argv_safe(...)` on the injected prefix. `--effort`/`--reasoning-effort` hard-denied by `process.assert_argv_safe` (bare, prefix, and `=`-form) and carried only as env metadata.
- LIMITED-AUTO still refused by name in `LoopConfig.__post_init__` (`test_limited_auto_still_refused_by_name` green). The channel launches only a successor session/unit; it does not self-approve work (producer ≠ approver preserved).

**5. No secret/credential surface — PASS.** No credentials/tokens introduced. Signal-file content is classified but never echoed into log/audit reason strings (verified: no `stdout` interpolation into classifier `reason`); the audit log applies its mandatory redaction pass regardless. `minimal_env` restricts the child environment to an allowlist and never logs values. Successor ids use `os.urandom`. No network path (no SSRF); the signal is a local operator-supplied file read as an argv array (never a shell).

**6. Permissions boundary (R354) — PASS.** The build does NOT widen the auto-mode classifier / accept-allowlist: `os_acl.py` and `config.py` are 0-diff and no settings file is in the 6-file change. The classifier widening (to allow unattended `project_control.py accept` / `git push` / `gh` merge) is surfaced as an explicit owner-only settings change in producer report §7-E, not implemented in code.

## Independent test evidence (Python 3.11.9, this worktree)
- `tools/test_agent_supervisor_r595_actuation.py`: **16 passed** (AS-1..AS-4, AS-6).
- Frozen mechanism (controller, adapters, model_turnover, integration, live_signal): **79 passed**.
- `loop` + `process` + `recovery`: **192 passed, 1 skipped**.
AS-5 (real exhaustion → real successor auto-launch) is correctly deferred to the owner-run isolated Windows job_object proof: the C1 gate hard-refuses on this POSIX sandbox. Production actuation stays off until AS-5 + gates pass; nothing in the build self-activates it.

## Observations (non-blocking; for orchestrator, not security defects)
- **Docstring cosmetic mismatch** in `worker_turnover.py`: the `default_actuation_authorization` docstring prose references `turnover_actuation_authorization` while the operative constant/attribute is `turnover_actuation_authorized`. Code is correct (uses `ACTUATION_AUTHORIZATION_ATTR`); doc-only.
- **allowed_paths reconciliation:** `claude_runner.py` (2-line `verified_in_job` propagation) and the new test module were outside the task's initial `allowed_paths`; producer report §1 requests a scope widen. This is a control-plane/material-identity bookkeeping item for the orchestrator to reconcile before accept — not a security weakness. The `claude_runner.py` change is additive and freeze-safe (field defaults True; the loop's M0-T060 gate stops only on explicit `verified_in_job is False`).

## Conclusion
R595 lifts exactly one thing — the owner-gated turnover auto-launch actuation channel — and every adjacent hold (protected config/ACL, argv/effort hard-deny, LIMITED-AUTO refusal, C1 containment, survivor/no-duplicate, exactly-once audit dedup, model pin, producer≠approver, permissions classifier) is preserved and independently reproduced. Fail-closed on every ambiguous/unauthorized/uncontained path. No forbidden path touched; reused mechanism is byte-for-byte unchanged.

VERDICT: PASS
