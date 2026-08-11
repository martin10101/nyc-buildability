# M0-T059 (P2) — G3 code review — VERDICT: PASS

Independent read-only code-reviewer return, preserved verbatim (transport decoding only). Reviewer did NOT
produce the code. Reviewed frozen SHA `9c01612560d16a8019a9b0b801009791d18ed40f` (baseline `9239cc3`
post-P1-accept). Supervisor defect-only lane. Python 3.11.9.

## VERDICT: PASS (no blocking defects; two INFO non-blockers)

## Scope verification
`git diff 9239cc3 9c01612 --stat` over the 5 files = exactly the deliverable (`recovery.py` +36/-2,
`claude_runner.py` +15/-2, `test_agent_supervisor_recovery.py` +46/-1, `test_agent_supervisor_start_reentry.py`
2 lines, producer report). All within amended allowed_paths. Interleaved M0-T061 (P6) commits touch none of the
5 P2 deliverables — reviewed diff cleanly isolated. **start_reentry.py is ONLY the 2-line spy companion fix**
(`spy_clear(journal)`→`spy_clear(journal, **kwargs)`; `real_clear(journal)`→`real_clear(journal, **kwargs)`);
assertions unchanged.

## Findings
| # | Severity | Location | Finding |
|---|----------|----------|---------|
| 1 | PASS | recovery.py:190-208 | Filter correct & robust: keeps every entry except `Mapping AND int(pid or 0)==pid AND str(token,"")==start_token`; identical idiom to `account_for_children`. Non-matching / non-Mapping entries preserved — fail-closed (never drops a record it can't positively identify). |
| 2 | PASS | recovery.py:211-223 | `recorded_start_token_for` consistent with the write path (`record_launched_child` writes pid/role/start_token/launched_at); returns first matching pid's token, "" if unrecorded; "" round-trips safely with the clear default (SC2 no-op). |
| 3 | PASS | claude_runner.py:1359-1364 | Caller correct: journal-None + `poll() is None` guards preserved → clears ONLY on verified exit; token lookup happens BEFORE clear (record still exists); import adds only `recorded_start_token_for`. |
| 4 | PASS | start_reentry.py:494-496 | Spy fix minimal & faithful (**kwargs forwarding required; delegates to real fn; C2 assertions untouched). |
| 5 | PASS | test_recovery.py:441-485 | Tests non-vacuous, honest fakes (real SQLite DurableJournal + real record/clear). |
| 6 | INFO (non-blocking) | producer report / commit msgs | Recorded counts stale/undercounted: report/commits say 1181/1499 vs reviewed identity's actual **1188/1506** (−7 = the P6 tests absent from the producer's worktree). Documentation only; reviewed tree exceeds recorded and matches orchestrator evidence; freeze baseline satisfied. |
| 7 | INFO (non-blocking) | recovery.py:205 | A non-numeric-string pid would raise ValueError in int() — pre-existing `account_for_children` idiom; write path only emits int pids; corrupt journal caught upstream. No regression. |

## Reproduced evidence (read-only, Python 3.11.9, HEAD 9c01612)
- Targeted P2 tests → 4 passed, 54 deselected.
- 20-module freeze (exact M0-T039 list): **Ran 1188 tests … OK (skipped=2)**, 0 failures (≥1165).
- Full supervisor suite `pytest tools/test_agent_supervisor_*.py -q` → **1506 passed, 2 skipped**, 0 failures (incl start_reentry).
- **Non-vacuity (independent source proof):** re-ran SC1/SC2/SC3 vs REAL clear and a whole-key-wipe revert →
  REAL survivors `[202]/[303]/[404]` intact; REVERT `[]/[]/[]` all three FAIL. Confirms the tests pin the fix.

## R347 fail-open assessment
Pre-M0-T059 whole-key wipe: any single settle erased EVERY recorded child → once a second child is recorded
(M0-T056 successor-launch seam), one worker's clean exit deletes a live successor's record → fail-OPEN on the
no-duplicate-workers invariant. The fix confines the clear to the settling unit's own `(pid, start_token)`; SC1
pins that a second recorded child survives. **Fail-open closed** ahead of M0-T056.

## Governance
Supervisor-freeze §3 (qualifying evidence cited in packet + commit `87360e6`) and §4 (baseline re-established
1188 ≥ 1165, 0 failures) satisfied. Only production caller of `clear_child_record` is `_settle_worker_record`.
**VERDICT: PASS** — findings #6/#7 informational, not corrections.
