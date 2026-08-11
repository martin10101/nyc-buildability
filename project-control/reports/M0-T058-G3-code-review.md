# M0-T058 (P1) — G3 code review — VERDICT: PASS

Independent read-only code-reviewer return, preserved verbatim (transport entity-decoding only) per the
report-preservation rule. Reviewer did NOT produce the code. Reviewed commit
`7c935f223898c91bfe9cee6e5e37e333de09099e` (parent `b678319`; code diff base `b678319`, integration base
`4083d2c`). Python 3.11.9.

## VERDICT: PASS
(one non-blocking acceptance dependency and one process anomaly noted; no code defects)

## Process anomaly — wrong-cwd (SAFETY GUARD tripped; handled safely)
Reviewer cwd was NOT an agent worktree: toplevel = `.../.claude/worktrees/session15-acc`, branch =
`control/session15-acceptance` (the guard's explicit STOP case). HEAD was already at the reviewed SHA
`7c935f2`, and this control worktree holds live uncommitted orchestrator acceptance bookkeeping
(`state.json`, `M0-T058.json`, untracked `M0-T058-G2.json`, `M0-T058-G2-selfcheck.md`,
`M0-T058-evidence-map.json`). Reviewer ran **zero git writes** (the authorized `git reset --hard` here would
have destroyed that uncommitted state). Entire review completed read-only at the correct reviewed identity.

## Scope check — PASS
Producer commit `7c935f2` (`b678319..7c935f2`) touches exactly the three `allowed_paths`
(`tools/agent_supervisor/claude_runner.py`, `tools/test_agent_supervisor_runner.py`,
`project-control/reports/M0-T058-producer-report.md`). No forbidden path touched.

## Findings table
| # | Severity | Location | Finding |
|---|----------|----------|---------|
| 1 | PASS (info) | `claude_runner.py:1297-1301` | `killed = container.terminate_all()` captured; defaults False if it raises. |
| 2 | PASS (info) | `claude_runner.py:1305-1312` | Bounded reap correct: wait→reaped=True; TimeoutExpired→False; other Exception→`reaped = process.poll() is not None`. Non-blocking. |
| 3 | PASS (info) | `claude_runner.py:1320-1332` | Guard fires only when kill unverified AND no observed exit; message truthful ("may survive"/"could not be verified"), reports actual `killed` and the bound. |
| 4 | PASS (info) | `claude_runner.py:1333-1337` | Verified-kill path still raises original `child_record_unwritable`; "the worker was terminated" now only reached when termination verified. Both raises reachable, mutually exclusive; no dead code. |
| 5 | PASS (info) | `CHILD_KILL_REAP_SECONDS = 10.0` (line 269) | Finite, named constant with rationale; wait cannot hang. 10s reasonable. |
| 6 | PASS (info) | repo-wide grep | `child_record_unwritable` appears ONLY at the two raise sites + test assertions; no consumer branches on the literal (only `f"{exc.code}: {exc.message}"` formatting). New sibling code cannot break routing. |
| 7 | PASS (info) | freeze §3 | Qualifying evidence cited in both packet and commit; smallest durable set; no redesign. |
| 8 | PASS (info) | tests | Fakes exercise the intended record-unwritable branch (journal.set_state raises OSError). SC1 covers both verified sub-paths; SC2 covers unverified→distinct code + "LIVE ORPHAN" + assertNotEqual to old code; SC3 asserts the wait is called once with a finite positive non-None timeout == the constant. |
| 9 | INFO (non-blocking, acceptance dependency) | packet `directive_refs: D-010 ALL` | In-regime: acceptance additionally requires the independent directive-compliance verification (`verification.json`, producer ≠ verifier) at the reviewed identity. Outside G3 code scope. |
| 10 | INFO (non-blocking) | `claude_runner.py:1311-1312` | The `poll()` fallback could itself propagate if `poll()` raised (extreme edge, `# pragma: no cover`); strictly better than the pre-fix no-wait. Acceptable. |

## Reproduced test counts
- 3 new P1 tests: `Ran 3 tests ... OK`.
- Full 20-module freeze suite (exact command from `M0-T039-supervisor-freeze.md`): **`Ran 1178 tests` → `OK (skipped=2)`, 0 failures.** ≥1165 satisfied. SC4 met.

## Non-vacuity: HELD
Read-only source proof (sandbox blocks exec/writes; not returned BLOCKED per evidence-capture rule): at base
`4083d2c` the except block unconditionally raises `child_record_unwritable`; `orphan_live` occurrences = 0. The
added guard at HEAD is the SOLE producer of `child_record_unwritable_orphan_live`; SC2 passes only at HEAD and
would necessarily fail (all three assertions) against base/neutralized behavior. Consistent with producer report §5.

## Regression: PASS
No behavior change outside the record-unwritable refusal except block; happy path and `_settle_worker_record`
untouched. Full suite green (1178, 0 failures). Freeze baseline re-established.

## Bottom line
Correct, honest, minimal fix closing the R347 double-launch residual. **PASS.** No required code corrections.
Before recording acceptance, ensure the in-regime D-010 directive-compliance `verification.json` (independent
verifier) is in place (finding #9) — an acceptance precondition, not a G3 code defect.
