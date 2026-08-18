# M0-T056 — R595 production actuation (turnover auto-launch LIVE) — Producer Report

**Task:** M0-T056 — R595 activation: live main-orchestrator + worker turnover auto-launch.
**Directive:** D-010 source-030 (R344–R351) + source-031 (R352–R357). **Producer:** backend-engineer.
**Qualifying evidence (supervisor-freeze §2 / AD-093):** the reproduced provider incident D-010
source-028 / R289 (Fable 5 weekly hard-stop, no auto-fallback), plus the owner's explicit R595
activation authorization (source-030) and build directive (source-031).
**Base:** origin/main `0d42953` (carries accepted M0-T054 + M0-T053). **Sandbox:** Python 3.11.9 (Linux).

This task takes the accepted M0-T054 turnover MECHANISM to production actuation. The M0-T054
controller (`turnover_controller.py`), adapters (`turnover_adapters.py`), and detection
(`model_turnover.py`) are **REUSED UNCHANGED** — those three files have ZERO diff. The change is
the minimal glue that lets an owner-authorized channel drive them, plus an orchestrator-layer
watchdog that runs outside the Claude session. Everything remains fail-closed, single-instance,
exactly-once, no-duplicate-workers, audit-linked, and C1-containment-gated.

---

## 1. EXACT files changed / created

| File | In initial allowed_paths? | Change |
|---|---|---|
| `tools/agent_supervisor/worker_turnover.py` | YES | `default_actuation_authorization` now reads the explicit owner signal `turnover_actuation_authorized` (fail-closed); added `ACTUATION_AUTHORIZATION_ATTR`. |
| `tools/agent_supervisor/loop.py` | YES | Added `LoopConfig.turnover_actuation_authorized: bool = False`; folded in the M0-T060 residual (verified_in_job gate on the achieved-job_object branch). |
| `tools/agent_supervisor/cli.py` | YES | Added `--authorize-turnover-actuation` flag; wired the real worker-layer actuation channel when authorized+contained; added the `orchestrator-watchdog` subcommand (`run_orchestrator_watchdog` + `cmd_orchestrator_watchdog`) and helpers. |
| `tools/agent_supervisor/claude_runner.py` | **NO — scope widen requested** | Two lines: `RunResult.containment_verified_in_job: bool = True` + set it from `containment_report.verified_in_job`. Needed to make the M0-T060 loop gate non-inert on Windows. |
| `tools/test_agent_supervisor_r595_actuation.py` | **NO — new file, scope widen requested** | 16 deterministic tests covering AS-1..AS-4 and AS-6. (The task named `test_agent_supervisor_model_turnover.py`; a dedicated module is cleaner and is collected by the `test_agent_supervisor_*` freeze glob.) |
| `project-control/reports/M0-T056-producer-report.md` | YES | This report. |

`turnover_controller.py`, `turnover_adapters.py`, `model_turnover.py`: **NOT changed** (reused
unchanged; `git diff` shows no entry for them). `recovery.py`: **NOT changed** (see §4, M0-T059).

**Orchestrator action requested:** set `allowed_paths` to match the two out-of-initial-scope files
(`claude_runner.py`, `tools/test_agent_supervisor_r595_actuation.py`). No forbidden path was
touched (services/api, apps/web, packages/contracts, `C:/SupervisorController/config.toml` all
untouched — see §5).

---

## 2. Per-acceptance-scenario mapping

### AS-1 (orchestrator layer) — watchdog OUTSIDE the Claude session, exactly-once, audit-linked
Implemented as the `orchestrator-watchdog` CLI subcommand (`cli.cmd_orchestrator_watchdog`) with the
argparse-independent core `cli.run_orchestrator_watchdog`. The OS scheduler (Windows Task Scheduler;
runbook in §7) invokes it on the orchestrator's captured terminal output — a separate process, hence
"outside the Claude session." It CLASSIFIES the captured signal with the frozen
`model_turnover.classify_exhaustion`, and only on a grounded `FABLE_EXHAUSTED` verdict (and only when
the C1 gate passes) drives the frozen `TurnoverController` at `layer=ORCHESTRATOR` to launch **exactly
one** `claude-opus-4-8`/`xhigh` successor. The successor argv carries `--session-role orchestrator`
and `--expected-worker-model claude-opus-4-8`, and the `TurnoverContext` carries the durable
`handoff_reference` (defaulting to the stored VERIFIED handoff digest via `RotationLedger`) and
`safe_checkpoint_id`, so the successor loads the durable handoff + safe checkpoint. **Exactly-once:**
the event id is deterministic in `(signal, checkout)`; a second detection of the SAME exhaustion hits
the controller's durable audit dedup (`mark_actioned`/`already_actioned`) and returns
`SUPPRESSED_DUPLICATE`, launching nothing. **Audit-linked** via `HashChainedAuditSink` over the real
hash-chained `AuditLog`. Tests: `OrchestratorWatchdogTests` (3).

### AS-2 (worker layer) — predicate injected redispatches once; predicate absent = byte-identical
`worker_turnover.default_actuation_authorization` no longer returns an unconditional `False`; it now
returns `getattr(config, "turnover_actuation_authorized", False) is True`. That signal is set on the
loop config ONLY by the `--authorize-turnover-actuation` flag (never a mode default, never from the
protected config). When the owner passes the flag AND the host is job_object-contained,
`cli._build_worker_actuation_channel` builds the **real** M0-T054 controller (adapters + survivor
detector) and injects it, so a confirmed `FABLE_EXHAUSTED` verdict redispatches the SAME bounded unit
on `claude-opus-4-8` exactly once through the controller (proven end-to-end by the pre-existing
`test_agent_supervisor_turnover_integration.py` with an authorized predicate + real adapters). Absent
the flag, `LoopConfig.turnover_actuation_authorized` defaults `False`, `_build_worker_actuation_channel`
returns `None`, and `WorkerTurnoverIntegration(controller=None)` is constructed exactly as today —
**byte-identical** record-intent-only path. Tests: `WorkerActuationPredicateTests` (3),
`WorkerActuationChannelBuildTests` (2); and the unchanged `ModeGatingTests` in the M0-T054 suite still
prove the default gate records intent.

### AS-3 (fail-closed) — NOT_EXHAUSTED / AMBIGUOUS / unreadable never actuate
`run_orchestrator_watchdog` launches ONLY on `verdict.should_turn_over` (i.e. `FABLE_EXHAUSTED`).
`NOT_EXHAUSTED` and `AMBIGUOUS_FAIL_CLOSED` record an `orchestrator_watchdog_no_turnover` audit
refusal and return without touching the launcher. An unreadable signal file makes
`cmd_orchestrator_watchdog` refuse (exit 1) before any controller is built. The detection classifier
itself is unchanged (a bare "limit"/429 stays AMBIGUOUS; a `seven_day` rejection is the one grounded
rate-limit path). Tests: `FailClosedTests` (3).

### AS-4 (no duplicate workers) — surviving recorded child + C1 job-object gate
The controller's `SurvivorPredicate` is wired (`cli._child_survivor_predicate`) to M0-T053 production
child accounting (`recovery.account_for_children`): a surviving recorded child returns
`BLOCKED_SURVIVOR` (no launch), and unreadable child state fails closed to "survivor present." The C1
job-object containment gate (`cli.containment_precondition`, shared source with `doctor`) is checked
before actuation on BOTH layers: the worker channel refuses to wire on a non-job_object host, and the
watchdog records `orchestrator_watchdog_containment_refused` and never launches. Tests:
`NoDuplicateWorkerTests` (2) — one records THIS live process as a surviving child (real start token)
and asserts `BLOCKED_SURVIVOR`; one forces a `process_group` host and asserts refusal.

### AS-5 (bounded isolated live proof) — BUILT + RUNBOOK; owner runs it on Windows
**Not run here (by design).** AS-5 requires a REAL exhaustion → REAL successor auto-launch on an
ISOLATED non-product runtime whose default containment is `job_object`; the C1 gate HARD-REFUSES on
POSIX (this sandbox is Linux — the P8 "Windows-Job-Object-only" narrowing), so it must run on the
owner's Windows host. The harness is the shipped `orchestrator-watchdog` subcommand + the
`--authorize-turnover-actuation` worker flag; the exact copy-pasteable RUNBOOK is in §7. This is the
single owner touchpoint.

### AS-6 (no other hold moved) — diff-level demonstration
See §5. Only 4 supervisor files + 1 new test + this report changed. No protected config/ACL, command/
path/credential protection, push/GitHub-flow policy, five-borough scope, or history/evidence
prohibition was touched; LIMITED-AUTO stays refused-by-name; the loop still routes every task through
independent gates (producer ≠ approver). Tests: `NoOtherHoldMovedTests` (3).

### AS-7 (freeze baseline) — see §3.

---

## 3. Full-suite pass count + freeze re-establishment (0 failures)

| Invocation | Result |
|---|---|
| `python -m pytest tools/test_agent_supervisor_*.py -q` (includes the new module) | **1525 passed, 2 skipped, 0 failed** (243.72s) |
| `python -m pytest tools/test_agent_supervisor_*.py -q` (before adding my tests) | 1509 passed, 2 skipped, 0 failed |
| `python -m unittest` (the exact M0-T039 20-module baseline) | **Ran 1191 tests, OK (skipped=2), 0 failed** (178.28s) |

The M0-T039 freeze bar is "≥ 1165 tests, 0 failures." The 20-module unittest baseline is **1191/0**
(the modules grew via M0-T053/T054); the full pytest glob is **1525/0** with my 16 new tests. Freeze
re-established, 0 failures. Environment: Python 3.11.9 (the supervisor tests run on 3.11, as expected).

`ruff 0.13.0`: my changed files introduce **zero** new lint findings. The 7 pre-existing F401
unused-import findings in `cli.py`/`loop.py` are on lines I did not touch and are present on base
`0d42953` (verified by `git stash`). CI ruff runs `working-directory: services/api` (`.github/
workflows/ci.yml`), so `tools/agent_supervisor/**` is not CI-ruff-gated regardless.

---

## 4. The two carried G5 residuals

### M0-T060 — gate the achieved job_object branch on `ContainmentReport.verified_in_job` — **FOLDED IN**
The loop's achieved-containment stop (`loop.py`, M0-T053 R4 half) checked the containment KIND string
only. I added a fail-closed strengthening on the otherwise-OK job_object path: a cycle whose
`run_result.containment_verified_in_job is False` now PAUSES (`containment_unverified`) rather than
proceeding on an unverified job assignment. To make it non-inert on Windows I propagated the boolean
through `RunResult` (`claude_runner.py`, 2 lines, from `containment_report.verified_in_job`, which the
process layer already computes via a real `is_process_in_job` probe). **Freeze-safe:** the field
defaults `True` and the guard fires ONLY on an explicit `False`, so every pre-existing test fake (and
every non-Windows cycle, which never reaches the job_object branch) is unchanged — confirmed by the
1191/1525 green runs.

### M0-T059 — atomic read-modify-write in `clear_child_record`/`recorded_start_token_for` — **NOT TRIGGERED; recommended follow-up (out of scope)**
This residual is explicitly conditional ("**if** you add a concurrent recorder settling the same
pid"). My design deliberately adds **no** concurrent recorder to `recovery.CHILD_PROCESSES_KEY`: the
worker-layer successor is launched through the M0-T054 adapters' `make_subprocess_command_runner`
(which records no child), and the orchestrator watchdog likewise records no child — exactly-once rests
on the durable audit dedup + single-instance lock, not on a second child recorder. So the single-
recorder invariant is intact and the non-atomic `get_state`→`set_state` in `recovery.py` is NOT
activated by M0-T056. `recovery.py` is outside allowed_paths and I left it byte-unchanged.
**Recommendation:** if a future task DOES add a second concurrent recorder, harden
`record_launched_child`/`clear_child_record`/`recorded_start_token_for` with an atomic RMW (a single
journal transaction) before that recorder ships — track as the standalone M0-T059. (Note: the
by-`(pid, start_token)` removal that M0-T053 G5 pin P2 required is already present in `recovery.py`.)

**Note on the other M0-T053 pin residuals (P1, P3, P4–P8):** these are "required before first live
actuation" (i.e. before the owner runs AS-5). P3 (achieved-containment STOP) is present in `loop.py`
and is now strengthened by the M0-T060 fold. P1 (`claude_runner.terminate_all` boolean/`wait`) lives
in `claude_runner.py`; I did not change the termination path (out of the minimal-surface scope for
this build) — flagged so the gate/owner can confirm it before AS-5. P6 (silent-reviewer =
fail-closed) is a review-process control for the gate wave, not producer code.

---

## 5. AS-6 — "no other hold moved" diff summary

`git diff --stat HEAD` (plus one untracked test + this report):

```
 tools/agent_supervisor/claude_runner.py   |   8 +   (RunResult field + 1 assignment)
 tools/agent_supervisor/cli.py             | 323 +++   (flag + watchdog subcommand + channel builder)
 tools/agent_supervisor/loop.py            |  38 ++    (LoopConfig field + M0-T060 gate)
 tools/agent_supervisor/worker_turnover.py |  38 +     (predicate reads explicit owner signal)
 tools/test_agent_supervisor_r595_actuation.py   (new, 16 tests)
 project-control/reports/M0-T056-producer-report.md (new)
```

What is demonstrably **unchanged** (holds NOT weakened):

- **Protected config / ACLs:** no change to `os_acl.py`, `config.py`, or `C:/SupervisorController/
  config.toml` (forbidden path, untouched). The actuation authorization is a per-run CLI flag on the
  loop config, NOT a protected-config field.
- **Command/path/credential protections:** `process.assert_argv_safe` / `HARD_DENY_ARGUMENTS` /
  breakaway guards untouched; the successor argv is built by the frozen adapters (still argv-safe-
  checked; `--effort` still hard-denied, carried as env metadata).
- **LIMITED-AUTO:** still refused by name in `LoopConfig.__post_init__` and `cmd_start`
  (unchanged) — proven by `test_limited_auto_still_refused_by_name`.
- **Push / GitHub-flow / five-borough / history-rewrite / evidence-deletion:** `push_policy.py`,
  `github_flow.py`, geospatial scope, and audit-append/immutability are untouched.
- **Producer ≠ approver:** the loop still routes tasks through independent gates; the actuation
  channel only launches a *successor session/unit*, it does not self-approve any work. The successor
  model is hard-pinned to `claude-opus-4-8`/`xhigh` (frozen constants; anything else is
  `INVALID_MODEL_REFUSED`).

The R595 scope is exactly what source-030 authorized: the turnover auto-launch actuation channel, and
nothing broader.

---

## 6. Worktree + commit

- **Agent worktree (absolute):** `C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/.claude/worktrees/agent-a30aa314dc99c1fd3`
- **Base HEAD:** `0d42953f1225135a88dc208e2c3256f06b96199e`
- **Commit SHA:** returned to the orchestrator in the final message (this report is committed in the
  same commit; work committed in the worktree, not pushed).

---

## 7. AS-5 RUNBOOK — owner-run isolated live proof (Windows, job_object host)

Run these on the **owner's Windows host** on an ISOLATED, non-product checkout/runtime (touch no
production data, no M2-T015 artifacts). Preconditions: `doctor` reports `containment_default: ok,
job_object` (criterion 1 — read as `kind == job_object`, per pin P7), and the elevated protected-
config ACL apply has been done. Use a throwaway `--runtime-base` and a scratch `--checkout`.

**A. Confirm the host is job_object-contained (C1 criterion 1):**
```
python -m tools.agent_supervisor doctor --json --checkout <SCRATCH_CHECKOUT> ^
  --config <ISOLATED_CONFIG> --model-selection <ISOLATED_SELECTION>
# require: "containment_default": { "ok": true, "kind": "job_object" }
```

**B. Worker-layer live proof (real Fable exhaustion → real opus-4-8 redispatch, no owner /model):**
Run a bounded supervised unit on the exhausted Fable account WITH the explicit authorization:
```
python -m tools.agent_supervisor start --mode supervised ^
  --checkout <SCRATCH_CHECKOUT> --runtime-base <SCRATCH_RUNTIME> ^
  --config <ISOLATED_CONFIG> --model-selection <ISOLATED_SELECTION> ^
  --claude-executable <CLAUDE_EXE> --codex-executable <CODEX_EXE> ^
  --task-packet <ISOLATED_PACKET> --worktree <SCRATCH_WORKTREE> --branch <SCRATCH_BRANCH> ^
  --max-cycles 1 --authorize-turnover-actuation --json
```
Expected: the confirmed Fable weekly-limit hard stop drives the WORKER-layer controller to launch
exactly one `claude-opus-4-8` successor for the SAME unit; capture the JSON payload + the audit log
lines (`fable_to_opus_turnover`, the `fable_turnover_event_actioned` dedup marker). Re-running the
same unit must show `SUPPRESSED_DUPLICATE` (exactly-once). Omitting `--authorize-turnover-actuation`
must show record-intent-only (`fable_exhaustion_turnover_recorded`, no launch).

**C. Orchestrator-layer live proof (watchdog outside the session, real successor auto-launch):**
Capture the exhausted Fable orchestrator's terminal output, then run the watchdog:
```
:: 1. run the Fable orchestrator, capturing its stream-json output to a file
claude.exe --model claude-fable-5 -p "..." --output-format stream-json --verbose > <SIGNAL_FILE> 2>&1
:: 2. the watchdog classifies it and auto-launches exactly one opus-4-8 successor
python -m tools.agent_supervisor orchestrator-watchdog --json ^
  --checkout <SCRATCH_CHECKOUT> --runtime-base <SCRATCH_RUNTIME> ^
  --exhaustion-signal <SIGNAL_FILE> ^
  --orchestrator-launcher-arg python --orchestrator-launcher-arg -m ^
  --orchestrator-launcher-arg tools.agent_supervisor --orchestrator-launcher-arg start ^
  --safe-checkpoint-id <SAFE_CP_ID>
```
Expected: `"launched": true`, `"successor_model_id": "claude-opus-4-8"`, an `event_id` and
`audit_record_id`; a second run on the SAME `<SIGNAL_FILE>` shows
`"status": "suppressed_duplicate"`, `"launched": false` (exactly-once). No owner `/model` step.

**D. Wire the watchdog to run unattended (outside the Claude session):** register the step-C command
as a Windows Task Scheduler task via the existing `autostart-plan` → `install-autostart` owner-
approved path (do NOT hand-edit schtasks). Capture the sealed evidence directory
(`M0-T056-live-proof/`) with the JSON payloads, audit excerpts, and a SHA-256 manifest.

**E. PERMISSIONS for a fully unattended loop (owner-only, do not bypass):** for the supervisor to
run the control commands without a per-command prompt, the owner must widen the auto-mode classifier
to allow `python tools/project_control.py accept`, `git push`, and `gh` merge. That is the owner's
explicit settings change (source-031 PERMISSIONS) — surfaced here in plain English; the agent never
bypasses the classifier. Until then the orchestrator performs Tier-A actions manually.

Only AFTER B+C+D pass on the isolated runtime and all required gates (G0/G2/G3/G5 + independent DCV)
pass does production actuation flip on. Nothing in this build self-activates it.
