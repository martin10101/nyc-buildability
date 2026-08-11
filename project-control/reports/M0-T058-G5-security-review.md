# M0-T058 (P1) — G5 security review — VERDICT: PASS

Independent read-only security-reviewer return, preserved verbatim (transport entity-decoding only) per
the report-preservation rule. Reviewer did NOT produce the code. Reviewed at frozen SHA
`7c935f223898c91bfe9cee6e5e37e333de09099e`; deliverable files byte-identical to the committed blob;
Python 3.11.9.

## Environment / safety-guard note
The safety guard tripped: `git rev-parse --show-toplevel` = `.../.claude/worktrees/session15-acc`,
branch = `control/session15-acceptance` — a `control/*` branch, NOT an `agent-`/`worktree-agent-` producer
worktree. Per the guard the reviewer ran **no git writes** (did not execute the authorized
`git reset --hard 7c935f2`, which was unnecessary — HEAD was already exactly `7c935f2`). All activity was
read-only inspection plus pytest/unittest execution; every write attempt was blocked by the read-only guard.
The review substance is valid at the correct content identity (`7c935f2`, files pristine). Parent is
`b678319` (the G0/claim commit); `4083d2c` is its grandparent — a doc discrepancy only, not security-relevant.

## Acceptance criteria reviewed
- **P1-SC1** (verified kill keeps `child_record_unwritable`) — PASS, reproduced.
- **P1-SC2** (unverified kill → DISTINCT `child_record_unwritable_orphan_live`, names a live orphan) — PASS, reproduced (key security assertion).
- **P1-SC3** (bounded wait, never hangs) — PASS, reproduced.
- **P1-SC4** (full freeze suite ≥1165, 0 failures + new tests; non-vacuity) — PASS, reproduced (1178 OK).

## Security analysis — the 5 threat questions (summary)
- **Q1 Does it close the hole?** Yes. Branch table walked: `terminate_all→True` → `child_record_unwritable`;
  `False`+wait-exits → `child_record_unwritable` (reaped confirmed); `False`+TimeoutExpired+alive →
  **`child_record_unwritable_orphan_live`** (the closed hole); `terminate_all raises` → wait decides;
  `wait` other-error → `poll()` fallback. Two raises mutually exclusive; no fall-through reports a possibly-live
  child as terminated except the `killed=True` branch (Q2).
- **Q2 Is `terminate_all()==True` trustworthy proof of death?** Yes on this codebase: Job-object path returns
  True after `_job.close()` with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` + `assert_no_breakaway` (kernel-guaranteed
  synchronous termination); taskkill True == returncode ∈ {0,128}; POSIX True == SIGKILL delivered.
  `terminate_all()` returns False only on the genuinely degraded path — exactly what is now routed through the
  bounded wait and the orphan-live code. The OR does not mask a live child (wait is consulted regardless).
- **Q3 Bounded wait:** `CHILD_KILL_REAP_SECONDS = 10.0`, single finite `wait`, no unbounded block/busy-loop;
  worst-case ~10s added refusal latency. Acceptable.
- **Q4 New surface / injection / leak:** none. f-string interpolates pid(int), killed(bool), timeout(float),
  and `exc` (already interpolated pre-fix). No format-string injection, no new secret exposure. Swallowed
  exceptions confined to defensive spots.
- **Q5 Honesty / fail-closed:** both outcomes `raise` → worker never runs; differ only in the truth told;
  downstream consumption generic (no literal branch). Fail-CLOSED in both cases.

## Non-vacuity
Read-only guard blocked runtime mutation (acceptable per project-control rule; verified against code + captured
evidence, not BLOCKED). Established deterministically: `if not (killed or reaped)` is the SOLE producer of the
distinct code; neutralizing it routes SC2's scenario to the generic code → SC2 necessarily FAILS. Matches the
producer report §5.

## Directive/requirement note
In-regime (`D-010 / ALL`). Full per-requirement D-010 verification is the independent directive-compliance-verifier's
pass in `verification.json` (producer ≠ verifier); not duplicated here.

## Defects
None (critical/high/medium/low). Two informational non-defects:
- **INFO-1 (theoretical residual, non-exploitable):** the `killed=True` branch trusts the kill primitive
  without also requiring `reaped`; the only way to report "terminated" while a child lingers is an
  uninterruptible kernel-teardown (D-state) process, which cannot execute user code and so cannot cause the
  R347 double-run. Requiring `killed AND reaped` would trade this for false orphan-live alarms; the OR is correct.
- **INFO-2 (robustness, extremely unlikely):** if `process.poll()` itself raised inside the wait-generic-except
  fallback, it would propagate as a non-`RunnerError` — still fail-CLOSED (worker not run), just less-specific.
  `Popen.poll()` does not raise in normal operation; `# pragma: no cover`.

## Reviewer conclusion
**PASS.** Correct fail-closed safety control. No residual fail-open path where a possibly-live orphan is
reported as terminated. All four acceptance scenarios reproduced; freeze baseline re-established (1178 OK, 0
failures); scope and supervisor-freeze respected. Closes M0-T053 G5 finding-4 double-launch hole (R347) ahead
of M0-T056. No required rework. (Non-substantive: review executed inside the `control/session15-acceptance`
worktree rather than an `agent-*` worktree, but HEAD was already at `7c935f2` and no writes were made.)
