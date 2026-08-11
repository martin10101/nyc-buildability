# M0-T058 (P1) — Producer Report

**Task:** Supervisor defect-lane fix (D-010 Phase 1). M0-T053 G5 finding 4 / activation-checklist P1.
**Qualifying evidence (supervisor-freeze §2/§3):** a *reproduced defect* — the record-unwritable
REFUSAL path claimed a termination it never verified, so a compound failure (degraded containment +
failed journal write + failed kill) left a LIVE UNRECORDED orphan while raising a reason code that
asserts the worker was terminated; the next `start` then reads SAFE_CHECKPOINT and double-launches
(D-010-R347).
**Baseline:** worktree fast-forwarded (lossless; ancestor→descendant) to integration baseline
`4083d2c` under explicit orchestrator authorization (ADR-005). Python 3.11.9.

## 1. Function and lines changed — before/after behavior

**File:** `tools/agent_supervisor/claude_runner.py`
**Function:** `ClaudeRunner._record_launched_worker(process, container)` (the `except Exception as exc`
block on the `record_launched_child` REFUSAL path).

**Before:** the except block called `container.terminate_all()` and **discarded** its boolean,
swallowed any exception from it, never `wait()`/`poll()`ed the child, then unconditionally raised
`RunnerError('child_record_unwritable', "… the worker was terminated …")`. On the degraded taskkill
fallback `terminate_process_tree` can legitimately return `False` (POSIX `killpg` → `PermissionError`;
Windows `taskkill` returncode ∉ {0,128}), so `terminate_all()` returns `False` and the worker can
still be alive — yet the message asserted it was terminated.

**After:**
1. Captures the boolean: `killed = container.terminate_all()` (defaults `killed=False` if it raises).
2. Adds a BOUNDED reap check: `process.wait(timeout=CHILD_KILL_REAP_SECONDS)` → `reaped=True` on a
   returned exit, `reaped=False` on `subprocess.TimeoutExpired`. Never blocks indefinitely.
3. If the child is verifiably still alive (`not (killed or reaped)`), raises the DISTINCT reason code
   `child_record_unwritable_orphan_live`, whose message HONESTLY states a LIVE ORPHAN may survive.
4. When the kill IS verified (`killed` True OR `reaped` True), keeps raising
   `RunnerError('child_record_unwritable')` exactly as before.

Container release (`container.close()`) and pipe cleanup are preserved unchanged.

New module constant added next to `GRACEFUL_CLOSE_GRACE_SECONDS`:
`CHILD_KILL_REAP_SECONDS = 10.0` (with a docstring explaining the bounded-wait rationale).

## 2. Distinct reason code and where it is consumed

**Introduced:** `child_record_unwritable_orphan_live` (a `RunnerError.code`).

**Consumption:** `RunnerError.code`/`.message` are consumed **generically** — never branched on by the
literal string. Verified across the module: the only prior occurrence of `child_record_unwritable` was
the raise site itself. Downstream, `cli.py` renders `f"{exc.code}: {exc.message}"` to stderr
(lines 1435/1937/1957/1997/2027/2070) and carries `exc.code` into a `reason` field (line 1718);
`loop.py` has no reason-code branch. So the new code flows through the same surfacing machinery with
**no routing change required**: the operator/log now sees `child_record_unwritable_orphan_live` and the
"LIVE ORPHAN may survive" message instead of a false "the worker was terminated".

## 3. Unified-diff summary

```
 tools/agent_supervisor/claude_runner.py |  43 ++++++++++++-
 tools/test_agent_supervisor_runner.py   | 104 ++++++++++++++++++++++++++++++++
 2 files changed, 145 insertions(+), 2 deletions(-)
```

Key hunk (`claude_runner.py`, the except block):
```python
        except Exception as exc:
            killed = False
            try:
                killed = container.terminate_all()
            except Exception:  # pragma: no cover - defensive
                killed = False
            reaped = False
            try:
                process.wait(timeout=CHILD_KILL_REAP_SECONDS)
                reaped = True
            except subprocess.TimeoutExpired:
                reaped = False
            except Exception:  # pragma: no cover - defensive
                reaped = process.poll() is not None
            container.close()
            for pipe in (process.stdin, process.stdout, process.stderr):
                ...
            if not (killed or reaped):
                raise RunnerError(
                    "child_record_unwritable_orphan_live",
                    f"the launched worker (pid {process.pid}) could not be recorded in the "
                    f"durable journal ({exc}) AND its termination could not be verified "
                    f"(terminate_all reported {killed}; the bounded {CHILD_KILL_REAP_SECONDS}s "
                    f"reap wait did not observe the child exit); a LIVE ORPHAN may survive that "
                    f"recovery cannot account for, so the unit refuses") from exc
            raise RunnerError(
                "child_record_unwritable",
                f"the launched worker (pid {process.pid}) could not be recorded in the "
                f"durable journal ({exc}); the worker was terminated and the unit refuses "
                f"rather than run a child that recovery could never account for") from exc
```

Tests (`test_agent_supervisor_runner.py`): added `_FakeKillContainer` (scripted `terminate_all()`
result) and `_FakeKillProcess` (scripted bounded `wait()` → returns vs `TimeoutExpired`, plus
`poll()`), a `_refuse_record` helper that drives `_record_launched_worker` directly with those fakes,
and the three P1 scenarios.

## 4. Freeze-baseline output (full 20-module suite, Python 3.11.9)

```
Ran 1178 tests in 171.534s

OK (skipped=2)
```
Base was 1175 (M0-T039 baseline) + 3 new tests = 1178. ≥1165 satisfied, 0 failures, 2 skipped.

New test names (class `ProductionChildAccountingTests`):
- `test_p1_sc1_verified_kill_keeps_the_original_reason` (P1-SC1)
- `test_p1_sc2_unverified_kill_reports_a_possible_live_orphan` (P1-SC2)
- `test_p1_sc3_the_reap_wait_is_bounded_and_never_hangs` (P1-SC3)

## 5. Non-vacuity (revert-fails → restore-passes)

Guard neutralized (`if not (killed or reaped):` → `if False and not (killed or reaped):`), new tests
kept. Result:
```
FAIL: test_p1_sc2_unverified_kill_reports_a_possible_live_orphan
AssertionError: 'child_record_unwritable' != 'child_record_unwritable_orphan_live'
- child_record_unwritable
+ child_record_unwritable_orphan_live
Ran 3 tests in 0.219s
FAILED (failures=1)
```
SC1 and SC3 still passed with the guard neutralized (they assert the generic code / the bounded-wait
call, which survive the revert) — so SC2 is the scenario that pins the new behavior. Guard restored:
```
Ran 3 tests in 0.019s
OK
```

## 6. Allowed-paths confirmation

`git diff --name-only 4083d2c HEAD`:
```
tools/agent_supervisor/claude_runner.py
tools/test_agent_supervisor_runner.py
project-control/reports/M0-T058-producer-report.md
```
All three are inside `allowed_paths`. (The untracked
`.claude/agent-memory/backend-engineer/verify-worktree-baseline-before-editing.md` is agent memory,
outside project-control, and is NOT staged/committed.)

## 7. Final commit SHA

See the returned summary / `git rev-parse HEAD` (recorded at commit time).
