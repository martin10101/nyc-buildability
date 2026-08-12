# M0-T056 — G3 code review (VERBATIM reviewer return, at reviewed_sha 8196039)

Independent reviewer: `code-reviewer` (read-only; reviewer != producer backend-engineer).
Returned via agent channel; saved verbatim. NOTE (orchestrator): this review is at `8196039`; findings
B+C are addressed in a rework delta and a delta re-review supersedes this at the reworked identity.
Finding A (P1) is reconciled by the orchestrator as ALREADY CLOSED by M0-T058 (see the orchestrator note
appended at the end).

---

I have completed my independent verification. All key facts are confirmed from source. Let me compose the G3 report.

---

# G3 Code Review — M0-T056 (R595 production turnover actuation)

**Task:** M0-T056 — take the M0-T054 turnover mechanism LIVE (worker + orchestrator layers)
**Reviewed SHA:** `81960395a6bb90fc359ccb03dd5cac7a1319c847` (branch `control/session16-codex-golive`)
**Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/.claude/worktrees/session15-acc`
**Reviewer:** independent (read-only); producer conclusions treated as claims and re-derived from source.
**Method:** diff inspection at the frozen SHA, source re-derivation of every gate, test reproduction on Python 3.11.9.

## Scope / provenance verification

`git show --stat` = exactly 6 files (4 supervisor `.py`, 1 new test, 1 report), 997 insertions. The four REUSED-UNCHANGED modules have empty diffs — verified:
```
git diff 8196039^ 8196039 -- turnover_controller.py turnover_adapters.py model_turnover.py recovery.py
→ all four print nothing (0 diff)
```
So the accepted M0-T054 controller/adapters/detection and M0-T053 `recovery.py` child-accounting are byte-identical to their gated state. AS-6 diff-scope (only supervisor files + test + report; no `config.toml`/`os_acl`/`push_policy`/`github_flow`/geospatial touched) confirmed at the diff level.

## 1. Fail-closed actuation (AS-2 / AS-3) — CONFIRMED

- Predicate defaults False: `worker_turnover.default_actuation_authorization` (worker_turnover.py:99) returns `getattr(config, "turnover_actuation_authorized", False) is True`. Identity `is True` rejects truthy-but-not-True (1, "true") — proven by `test_non_true_values_fail_closed`.
- Only enable path is the explicit flag. `LoopConfig.turnover_actuation_authorized` (loop.py) defaults False; the only setter is cli.py `_run_loop`, `turnover_actuation_authorized=bool(getattr(args,"authorize_turnover_actuation",False))` — read from the CLI flag, never from a mode default and never from the protected controller config.toml. `test_default_config_is_unauthorized_byte_identical` proves shadow/supervised default to unauthorized.
- Flag ABSENT ⇒ byte-identical record-intent-only, via a double gate: `_build_worker_actuation_channel` (cli.py) returns `(None, …)` on the first check when the flag is absent → `WorkerTurnoverIntegration(controller=None)`; and even if the predicate were somehow True, `evaluate()`'s `self._controller is None` branch (worker_turnover.py:240) returns record-intent-only. `test_unauthorized_returns_no_channel_record_intent` confirms `controller is None`.
- NOT_EXHAUSTED / AMBIGUOUS / unreadable never actuate. `run_orchestrator_watchdog` launches only on `verdict.should_turn_over`; otherwise it writes `orchestrator_watchdog_no_turnover` and returns without touching the launcher. `cmd_orchestrator_watchdog` refuses (exit 1) on an unreadable `--exhaustion-signal` before any controller is built. Proven by `FailClosedTests` (NOT_EXHAUSTED / AMBIGUOUS / empty → 0 invocations).

## 2. Exactly-once + no-duplicate (AS-1 / AS-4) — CONFIRMED

Driven through the reused controller (`turnover_controller.py`, 0 diff):
- Exactly-once: watchdog event id is deterministic in `(signal, checkout)` (`_orchestrator_exhaustion_event_id`), worker event id deterministic in `(run_id, cycle)`. A repeat detection hits `already_actioned(event_id)` → `SUPPRESSED_DUPLICATE`; `mark_actioned` is consumed only after a confirmed launch. `test_second_detection_of_same_exhaustion_launches_nothing` → 1 invocation across two calls, `status == suppressed_duplicate`.
- Survivor block: `_child_survivor_predicate` wires to M0-T053 `recovery.account_for_children` (`ChildAccount.surviving`); unreadable child state fails CLOSED to survivor-present (`except Exception: return True`). `test_surviving_recorded_child_refuses_launch` records the live PID with its real start token → `BLOCKED_SURVIVOR`, 0 invocations.
- C1 job-object gate on BOTH layers: `containment_precondition()` (shared `default_containment_kind()` with `doctor`) returns True only for `job_object`, and refuses (incl. exception → "unknown") otherwise. Worker channel refuses to wire; watchdog records `orchestrator_watchdog_containment_refused` and never launches. `test_c1_containment_gate_refuses_on_non_job_object_host` confirms.
- Successor hard-pin: `ALLOWED_SUCCESSOR_MODEL_ID="claude-opus-4-8"`, `ALLOWED_SUCCESSOR_EFFORT="xhigh"` (turnover_controller.py:54-55); `SupervisorLauncher` ignores any caller-supplied model and refuses a mismatched reported model. `test_grounded_exhaustion_launches_exactly_one_opus_successor` / `_opus_argv_carries_orchestrator_role_and_pin` confirm the pin and `--session-role orchestrator`/`--expected-worker-model`.
- The production spawner `make_subprocess_command_runner` records NO child (no `record_launched_child`/`set_state`), so M0-T059's atomic-RMW residual is genuinely not triggered — the producer's "single-recorder invariant intact" claim holds.

## 3. M0-T060 fold-in — CORRECT, freeze-safe

The new stop (loop.py:1803-1820) is placed AFTER the `achieved != CONTAINMENT_JOB_OBJECT` guard (loop.py:1770-1789), so it is reached only on an already-job_object cycle. It reads `getattr(run_result,"containment_verified_in_job",True)` and stops (`containment_unverified`) only on explicit `is False`. `claude_runner.py` propagates `containment_report.verified_in_job` into `RunResult` (default True). Non-Windows cycles never achieve `job_object` containment and stop at the earlier guard, so they never reach this branch; and the True default means every pre-existing RunResult/test-fake proceeds unchanged. No regression path exists. (See finding B below re: test coverage.)

## 4. Pyright triage — both are non-defects, as claimed

- `decision.triggered/reason_code/reason/audit_summary` "unknown on CodexDecision" is a FALSE POSITIVE. At loop.py:1732 `self._worker_turnover` (typed `Any`, loop.py:919) is a `WorkerTurnoverIntegration` whose `evaluate()` returns `WorkerTurnoverDecision` (worker_turnover.py:103), which HAS all four fields (lines 115-122). Pyright mis-attributes to `CodexDecision` (models.py:195) due to the `Any`/reused-name collision in the function scope; runtime is correct and exercised by the 160 passing turnover/loop tests.
- `model_available` `(str)->tuple[bool,str]` vs expected `(str)->bool`: ANNOTATION MISMATCH, not a runtime inconsistency. `make_launch_probe` (claude_runner.py:1618) returns `Callable[[str], tuple[bool,str]]`; the callee `SupervisedLoop._probe_model` (loop.py:1108-1119) explicitly UNPACKS the tuple (`isinstance(raw, tuple) and len(raw)==2 → ModelAvailability(available=bool(raw[0]), reason_code=str(raw[1]))`) and also accepts bare bool and `ModelAvailability`. The loop `__init__` param is annotated narrowly (`Callable[[str],bool]`). This code is PRE-EXISTING (M0-T041) and NOT touched by this commit (the diff line is context only). No runtime bug.

## 5. Freeze (AS-7) — reproduced

```
$ python -m pytest tools/test_agent_supervisor_r595_actuation.py -q
16 passed in 4.87s
$ python -m pytest tools/test_agent_supervisor_turnover_*.py tools/test_agent_supervisor_loop.py -q
160 passed in 24.83s
```
(Python 3.11.9; the new module and turnover/loop suites are 3.11-collectable.) Matches the expected 16. Full 1525-suite freeze is deferred to CI supervisor-bridge per the packet.

## 6. P1 residual — pre-AS-5 prerequisite, NOT a G3 code-correctness defect

The authoritative M0-T036 ACTIVATION-RECORD PIN (2026-08-11, from the M0-T053 G5 PASS) states P1/P2/P3 are "REQUIRED CORRECTIONS BEFORE M0-T056's FIRST LIVE ACTIVATION … They do NOT block M0-T053's acceptance," and "the next task cannot be built on the assumption they are already closed." Assessed against the committed code:
- P2 (remove child by `(pid, start_token)`) — PRESENT in `recovery.py:clear_child_record` (verified).
- P3 (achieved-containment STOP) — PRESENT (loop.py:1770-1789) and strengthened by the M0-T060 fold-in.
- P1 (`claude_runner.terminate_all` discards its boolean, swallows exceptions, no bounded `wait()`, yet asserts termination) — UNCHANGED. The producer explicitly did NOT change it and FLAGGED it (report §4), i.e. it did not assume it closed — consistent with the pin.

**Determination:** P1-unchanged is a pre-AS-5 / first-live-actuation prerequisite (owner + G5 confirm before running the live proof), NOT a defect in the new M0-T056 code. Rationale: the committed code performs no real spawn in any tested/default path — the only real launch is the owner-run AS-5 (runbook §7), which is explicitly gated ("Only AFTER B+C+D and all required gates pass does production actuation flip on"). This carries forward as BLOCKING before AS-5 per the pin; it does not fail G3 code review.

## Findings (corrections, BLOCKING before AS-5 / final acceptance; NOT blocking G3 code correctness)

- **A (carried pin, required before first live actuation):** P1 termination-verification in `claude_runner.py` remains open. Must be closed (capture the `terminate_all` boolean, bounded `process.wait()`, distinct code if still alive) before the owner runs AS-5. Correctly surfaced by the producer.
- **B (weak-test gap):** the M0-T060 `containment_unverified` branch (loop.py:1804) has NO direct regression test — deleting the branch keeps the suite green (same regression-gap pattern the M0-T053 G3 flagged for `terminate_all`). Recommend a direct test: `RunResult(containment="job_object", containment_verified_in_job=False)` → cycle stops with `containment_unverified`. Close before AS-5.
- **C (cosmetic, non-blocking):** worker_turnover.py:88 docstring prose says `turnover_actuation_authorization` where the field/constant is `turnover_actuation_authorized`; the executable constant `ACTUATION_AUTHORIZATION_ATTR="turnover_actuation_authorized"` is correct, so behavior is unaffected.

## Verdict

The new M0-T056 code is correct, fail-closed on every path, hard-pins the opus-4-8/xhigh successor, is exactly-once/survivor-blocked/C1-gated on both layers, reuses the accepted mechanism byte-unchanged, and does not self-activate (only the explicit `--authorize-turnover-actuation` flag and the explicit `orchestrator-watchdog` subcommand enable it). 16 + 160 tests reproduced green. Both pyright items are non-defects as triaged. Findings A and B are pre-AS-5 required corrections (A is already the authoritative pin; do not run the live proof until both are closed and the G5 security review confirms P1); C is cosmetic.

VERDICT: PASS

---

## ORCHESTRATOR RECONCILIATION NOTE (finding A)

Finding A (P1) is reconciled as **ALREADY CLOSED by M0-T058 (accepted session 17, count 79)**. The
M0-T036 checklist P1 references stale line numbers `claude_runner.py:1283-1298` (pre-M0-T058) and was
never marked resolved. The M0-T058 fix is present at `claude_runner.py:1300-1349` on this reviewed tree:
the child-record-write-failure path captures `killed = container.terminate_all()`, performs a bounded
`process.wait(timeout=CHILD_KILL_REAP_SECONDS)` → `reaped`, and raises the DISTINCT
`child_record_unwritable_orphan_live` code iff `not (killed or reaped)` — exactly the P1-required fix
(capture the boolean, bounded wait, distinct code if alive). This IS the double-launch path P1 targeted.
The other `terminate_all()` sites (1114/1198/1522/1561) are graceful shutdowns of RECORDED workers, each
followed by a bounded `process.wait()`, and none asserts a false termination that a double-launch depends
on. A delta re-review confirms P1-closed at the reworked identity; the M0-T036 checklist is updated to mark
P1 resolved by M0-T058. Findings B (add the M0-T060 branch test) and C (docstring) are closed in the rework.
