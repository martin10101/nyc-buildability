# M0-T059 (P2) — Producer report

Defect: M0-T053 G5 finding 5 / activation-checklist P2 — `clear_child_record` wipes the WHOLE
`CHILD_PROCESSES_KEY`, so a settle clears records it did not create. Latent with a single recorder,
but fails OPEN on the no-duplicate-workers invariant (D-010-R347) the moment a second child is
recorded (e.g. M0-T056's successor-launch seam): one worker's clean exit erases a live successor's
record.

Lane: supervisor defect-only maintenance (`.claude/rules/supervisor-freeze.md`). Qualifying evidence
(section 2): a reproduced fail-OPEN defect cited in M0-T053 G5 finding 5 + the P2 activation-checklist item.

## SAFETY GUARD
- toplevel: `.../.claude/worktrees/agent-adc6ed6abd1e09e86` (contains `.claude/worktrees/agent-`) OK
- branch: `worktree-agent-adc6ed6abd1e09e86` (starts with `worktree-agent-`) OK
- Re-based to P1 baseline `9239cc3` (lossless forward reset from `7cc1fed`); sanity
  `python -m unittest tools.test_agent_supervisor_recovery tools.test_agent_supervisor_runner` => `Ran 126 ... OK`.

## 1. Functions / behavior changed

### tools/agent_supervisor/recovery.py
- `clear_child_record(journal)` -> `clear_child_record(journal, *, pid: int, start_token: str = "")`.
  - Before: `journal.set_state(CHILD_PROCESSES_KEY, [])` — wiped ALL recorded children.
  - After: reads the recorded list and writes back everything EXCEPT the single entry whose
    `pid` AND `start_token` both match; every other recorded child (notably a live successor under a
    different pid) survives. A differing `start_token` = a reused pid = left untouched.
- New helper `recorded_start_token_for(journal, pid) -> str`: returns the `start_token` recorded
  for `pid` (`""` if not recorded). Needed because the launch-time token (process creation stamp)
  cannot be re-derived from an exited pid — the durable record is the only faithful source at settle
  time. Uses the same `Mapping`/`get_state(CHILD_PROCESSES_KEY, [])` idiom as `account_for_children`.

### tools/agent_supervisor/claude_runner.py  (only `_settle_worker_record` + its recovery import)
- Import (~line 68) extended to also import `recorded_start_token_for` from `.recovery`.
- `_settle_worker_record(self, process)` — signature UNCHANGED (still takes only `process`, so the
  runner test `_settle_worker_record(_NeverReaped())` is unaffected). Body now, on a verified exit:
  ```
  start_token = recorded_start_token_for(self.journal, process.pid)
  clear_child_record(self.journal, pid=process.pid, start_token=start_token)
  ```
  It recovers the exact token it journaled at launch and clears precisely its own `(pid, start_token)`
  entry. The early returns (journal is None; `process.poll() is None`) are unchanged — an unreaped
  child still keeps its record.

How the caller supplies pid + start_token: `pid` from `process.pid`; `start_token` looked up from the
durable record via `recorded_start_token_for` (re-derivation from an exited pid returns `""` and would
mis-match the recorded token, so the journal is the source).

## 2. git diff --stat + name-only

```
 tools/agent_supervisor/claude_runner.py | 15 +++++++++--
 tools/agent_supervisor/recovery.py      | 36 ++++++++++++++++++++++++--
 tools/test_agent_supervisor_recovery.py | 46 ++++++++++++++++++++++++++++++++-
 3 files changed, 92 insertions(+), 5 deletions(-)
```

Key hunk (recovery.py):
```python
def clear_child_record(journal: Any, *, pid: int, start_token: str = "") -> None:
    recorded = journal.get_state(CHILD_PROCESSES_KEY, []) or []
    remaining = [
        entry for entry in recorded
        if not (isinstance(entry, Mapping)
                and int(entry.get("pid", 0) or 0) == pid
                and str(entry.get("start_token", "")) == start_token)
    ]
    journal.set_state(CHILD_PROCESSES_KEY, remaining)
```

## 3. Freeze-baseline output + new test names

Full 20-module suite from the worktree (Python 3.11.9):
```
Ran 1181 tests in 87.963s

OK (skipped=2)
```
(1178 baseline + 3 new; >=1165 required; 0 failures; 2 skipped.)

New tests in `tools/test_agent_supervisor_recovery.py` (class `ChildAccountingTests`):
- `test_p2_sc1_settling_one_child_leaves_a_second_recorded_child` (P2-SC1)
- `test_p2_sc2_settling_an_unrecorded_pid_is_a_no_op` (P2-SC2)
- `test_p2_sc3_a_reused_pid_with_a_different_start_token_is_not_cleared` (P2-SC3)
- (existing `test_clearing_the_record_empties_it` updated to the new keyword signature)

## 4. Non-vacuity (revert / restore)

Temporarily reverted the guard to the whole-key wipe (`journal.set_state(CHILD_PROCESSES_KEY, [])`),
new tests kept. `python -m unittest tools.test_agent_supervisor_recovery.ChildAccountingTests`:
```
FAIL: test_p2_sc1... AssertionError: Lists differ: [] != [202]
FAIL: test_p2_sc2... AssertionError: Lists differ: [] != [303]
FAIL: test_p2_sc3... AssertionError: Lists differ: [] != [404]
Ran 7 tests in 0.332s
FAILED (failures=3)
```
Guard restored; re-ran => `Ran 7 ... OK`. The new tests genuinely bind the fix.

## 5. Changed files vs baseline

`git diff --name-only 9239cc3 HEAD`:
```
tools/agent_supervisor/claude_runner.py
tools/agent_supervisor/recovery.py
tools/test_agent_supervisor_recovery.py
```
All within allowed_paths (report is the fourth allowed path).

## 6. HEAD sha
Recorded post-commit by the orchestrator. Pre-commit worktree HEAD = `9239cc3` (baseline);
the three files above are staged for the M0-T059 commit.

---

## LIMITATION / SCOPE WALL (requires orchestrator action) — companion edit outside allowed_paths

`tools/test_agent_supervisor_start_reentry.py` is OUTSIDE my allowed_paths and it BREAKS under the
new signature. That file (`ContainmentGateTests.test_the_dispatched_run_records_and_clears_the_child_in_production`)
monkeypatches the module global with a 1-arg spy:

```python
def spy_clear(journal):
    cleared.append(True)
    real_clear(journal)
...
cr.clear_child_record = spy_clear
```

It runs the CLI in-process (`self.cli.main(...)`), so the production settle path now calls
`spy_clear(self.journal, pid=..., start_token=...)`. Confirmed failure at baseline+fix:
```
TypeError: ...spy_clear() got an unexpected keyword argument 'pid'
...
Ran 16 tests in 1.394s
FAILED (errors=1)
```
This file is NOT in the 20-module freeze list, so the freeze baseline stays green, but the file WILL
fail under `unittest discover` / CI. The task premise ("_settle_worker_record is the SOLE caller")
missed this test spy.

Minimal companion fix (2 lines, signature-tolerant spy — after which the test PASSES because a single
child still ends with an empty record and `cleared` is called once):
```python
def spy_clear(journal, **kwargs):
    cleared.append(True)
    real_clear(journal, **kwargs)
```

Requested action: either (a) expand M0-T059 allowed_paths to include
`tools/test_agent_supervisor_start_reentry.py` so I apply the 2-line spy fix, or (b) the orchestrator
dispatches/applies it. I did NOT edit that file (out of scope). No other repo caller of
`clear_child_record` exists (grep over `tools/`): production `claude_runner._settle_worker_record`,
the recovery test (updated), and this start_reentry spy.

---

## COMPANION FIX APPLIED (allowed_paths amended by orchestrator 2026-08-11)

Orchestrator amended M0-T059 allowed_paths to include `tools/test_agent_supervisor_start_reentry.py`.
Applied the minimal 2-line signature-tolerant spy:
```python
def spy_clear(journal, **kwargs):
    cleared.append(True)
    real_clear(journal, **kwargs)
```
Evidence:
- `python -m unittest tools.test_agent_supervisor_start_reentry` => `Ran 16 ... OK` (was `FAILED (errors=1)`).
- FULL supervisor pytest `python -m pytest tools/test_agent_supervisor_*.py -q` => `1499 passed, 2 skipped in 116.28s` (0 failures).
- 20-module freeze baseline re-run => `Ran 1181 ... OK (skipped=2)`.

`git diff --name-only 9239cc3 HEAD` now: recovery.py, claude_runner.py, test_agent_supervisor_recovery.py,
test_agent_supervisor_start_reentry.py, M0-T059-producer-report.md — all within the amended allowed_paths.
