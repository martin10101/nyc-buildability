# M0-T060 (P3) — Producer report

**Task:** M0-T053 G5 R4 enforcement half / activation-checklist P3 — make an
ACHIEVED per-cycle containment `!= "job_object"` a fail-closed STOP of the
supervised cycle, not merely an audit line.

**Qualifying evidence (supervisor-freeze §2/§3):** reproduced defect — the
achieved per-cycle containment was only RECORDED on `RunResult.containment` /
the `claude_process_started` transition detail; a cycle that honestly degraded
to taskkill at launch would PROCEED unattended (nobody reads the audit line).
Cited in the task packet (M0-T053 G5 R4 enforcement half; 2026-08-08 pin
criterion 2) and in the commit message.

## 1. Files / functions changed, seam evidence, before/after, recorded reason

### Seam is in-scope (loop.py) — grep evidence
`grep containment|job_object|claude_process_started` over `tools/agent_supervisor`
shows the ACHIEVED per-cycle containment is CONSUMED post-run only in
`tools/agent_supervisor/loop.py` at the `SupervisedLoop.run_cycle`
`claude_process_started` transition:

```
loop.py:1675:                CLAUDE_RUNNING, "claude_process_started",
loop.py:1677:                        "containment": getattr(run_result, "containment", "")})
```

`claude_runner.py` PRODUCES the `RunResult.containment` /
`RunResult.containment_fallback_reason` fields (lines 905-906, 1223-1224);
`process.py` defines `CONTAINMENT_JOB_OBJECT = "job_object"` (line 315) and the
`ProcessContainer.adopt` honest degrade. The `claude_process_started` transition
itself lives in `state_machine.py` (NOT in allowed_paths) — but the transition is
only the RECORD; the post-run EVALUATION/STOP decision is entirely inside
`loop.py:run_cycle`, which IS in allowed_paths. **No edit outside allowed_paths
was required; the scope wall in the packet (`state_machine.py`) was not hit.**

### Functions changed
- `tools/agent_supervisor/loop.py`
  - New import: `from .process import CONTAINMENT_JOB_OBJECT`.
  - `SupervisedLoop.run_cycle`: added a fail-closed containment guard on the
    otherwise-OK path (immediately after the S14 `if checkpoint is None or not
    run_result.ok:` reconciliation block returns, before the
    `CHECKPOINT_RECEIVED` transition).

### Before / after
- **Before:** achieved containment was recorded on the `claude_process_started`
  transition detail (`"containment": ...`) and then IGNORED. A cycle with
  `run_result.containment == "taskkill"` (or any non-`job_object`) and a valid
  checkpoint PROCEEDED normally (forwarded, `result.stopped == ""`).
- **After:** a cycle whose achieved `run_result.containment != "job_object"`
  transitions `CLAUDE_RUNNING -> PAUSED_RECOVERY` (`unsafe_condition`), records a
  synchronous owner touch (`TOUCH_SYNCHRONOUS_STOP`, `reason_code
  = "containment_degraded"`), and returns `stop("containment_degraded", …,
  PAUSED_RECOVERY)`. A cycle reporting `containment == "job_object"` proceeds
  unchanged. The `claude_process_started` record is unchanged.

### Placement decision (ordering / ripple)
The guard is placed on the **otherwise-OK path** (after the S14 checkpoint/effect
reconciliation), NOT immediately after the process-started transition. Rationale:
the pending-effect / `ambiguous_effect` reconciliation (S11.5 / S14 — never retry
a unit with an unproven external effect) is the paramount safety invariant and
must not be masked by the containment stop. A degraded cycle that ALSO failed its
checkpoint still stops (for the checkpoint reason); the containment stop is the
operative reason only on a cycle that would OTHERWISE proceed. This preserves the
invariant "no non-`job_object` cycle ever proceeds unattended" while keeping every
existing stop reason intact. See §4 (ripple) for why the initial pre-reconciliation
placement was corrected.

### Recorded reason string (exact template)
```
the cycle achieved '<achieved>' containment, not job-strength 'job_object': a
child that spawns its own process tree can escape a non-job container, so an
unattended run must fail closed rather than proceed on it (fallback reason: <r>)
```
(`(fallback reason: …)` appended only when `RunResult.containment_fallback_reason`
is non-empty.) The stop `code`/`reason_code` is `containment_degraded`.

## 2. git diff --stat + key hunks

```
 tools/agent_supervisor/loop.py      | 38 +++++++++++++++++++++++++++
 tools/test_agent_supervisor_loop.py | 52 +++++++++++++++++++++++++++++++++++++
 2 files changed, 90 insertions(+)
```

Key hunk (loop.py `run_cycle`, on the OK path):
```python
        achieved = str(getattr(run_result, "containment", "") or "")
        if achieved != CONTAINMENT_JOB_OBJECT:
            fallback = str(getattr(run_result, "containment_fallback_reason", "") or "")
            containment_reason = (
                f"the cycle achieved {achieved or 'unknown'!r} containment, not "
                f"job-strength {CONTAINMENT_JOB_OBJECT!r}: a child that spawns its "
                f"own process tree can escape a non-job container, so an unattended "
                f"run must fail closed rather than proceed on it")
            if fallback:
                containment_reason += f" (fallback reason: {fallback})"
            self.machine.transition(
                PAUSED_RECOVERY, "unsafe_condition",
                detail={"cycle": cycle, "reason": "containment_degraded",
                        "containment": achieved,
                        "containment_fallback_reason": fallback})
            touches.append(self._touch(
                TOUCH_SYNCHRONOUS_STOP, reason_code="containment_degraded",
                reason=containment_reason, cycle=cycle,
                basis="M0-T053 G5 R4 achieved-containment enforcement (2026-08-08 "
                      "pin criterion 2; S13.2 / S13.12 invariants 10-11)"))
            return stop("containment_degraded", containment_reason, PAUSED_RECOVERY)
```
Plus the import `from .process import CONTAINMENT_JOB_OBJECT`.

New tests (`tools/test_agent_supervisor_loop.py`, class `AchievedContainmentTests`):
- `test_P3_SC1_job_object_containment_proceeds_normally` (P3-SC1)
- `test_P3_SC2_degraded_containment_stops_with_a_recorded_reason` (P3-SC2)
- `test_process_group_containment_also_fails_closed` (extra: any non-`job_object`
  kind fails closed).

## 3. Freeze-baseline output + full-pytest parity

### 20-module unittest freeze-baseline (Python 3.11.9)
```
Ran 1191 tests in 81.220s

OK (skipped=2)
```
(1188 base + 3 new = 1191; >= 1165 required; 0 failures; 2 skipped.)

### Full 36-module pytest parity (CI supervisor-bridge)
```
1509 passed, 2 skipped in 112.80s (0:01:52)
```
0 failures.

`python --version` → `Python 3.11.9`.

## 4. Non-vacuity revert/restore evidence + ripple correction

### Ripple correction (disclosed, not silently widened)
The FIRST placement (immediately after the `claude_process_started` transition,
before the S14 reconciliation) rippled ONE test in another module:
```
FAIL: test_the_loop_refuses_to_retry_a_unit_with_a_pending_effect
      (tools.test_agent_supervisor_adversarial.DuplicateEffectTests)
AssertionError: 'containment_degraded' != 'ambiguous_effect'
```
That test constructs a `RunResult` with NO containment set (defaults to `""`) plus
a timeout + pending external effect and expects `ambiguous_effect`. The
pre-reconciliation guard preempted the paramount ambiguous-effect stop. I did NOT
edit the adversarial test. Instead I moved the guard onto the otherwise-OK path
(within loop.py, my scope), which PRESERVES the adversarial test's original
expectation naturally. Re-run of `test_agent_supervisor_loop` +
`test_agent_supervisor_adversarial`: `Ran 199 tests ... OK`.

### Non-vacuity (guard neutralized: `if False and achieved != …`)
With the STOP guard neutralized and the new tests kept, P3-SC2 (and the
process_group test) FAIL:
```
FAIL: test_P3_SC2_degraded_containment_stops_with_a_recorded_reason
AssertionError: '' != 'containment_degraded'
FAIL: test_process_group_containment_also_fails_closed
AssertionError: '' != 'containment_degraded'
Ran 3 tests in 0.294s
FAILED (failures=2)
```
(P3-SC1 still passes — a `job_object` cycle proceeds either way, proving the test
is not vacuously green.) Guard restored; `AchievedContainmentTests` re-run:
`Ran 3 tests ... OK`. Non-vacuity: **YES**.

## 5. git diff --name-only 20b82ea HEAD (within allowed_paths)

```
project-control/reports/M0-T060-producer-report.md
tools/agent_supervisor/loop.py
tools/test_agent_supervisor_loop.py
```
All within allowed_paths. `claude_runner.py` was inspected but not modified (the
RunResult fields it produces were sufficient).

## 6. git rev-parse HEAD

(recorded post-commit below)
