# M0-T017 Producer Report — S7 live-ledger test-data coupling fix

- **Task:** M0-T017 (defect fix; control-plane CI job 87990690868 failed at
  `test_s7_backward_compatibility` with `expected at least one backlog task in the ledger copy`)
- **Producer:** backend-engineer
- **Requested status:** awaiting_gate
- **Branch / worktree:** `task/M0-T017-s7-ledger-coupling` / `.claude/worktrees/M0-T017`
- **Date:** 2026-07-17

## 1. Defect and root cause

S7 copies the REAL `project-control/` ledger into a temp project and then asserted
`assert backlog, "expected at least one backlog task in the ledger copy"` before running its
message-only `progress` probe. Backlog membership is a *mutable live status*: when every task is
claimed, in flight, or terminal (exactly what happened when M2-T002 and M1-T009 were claimed) the
live backlog is legitimately empty and the assertion fails repo-wide. The enforcement code in
`tools/project_control.py` is correct; the coupling was test-data-only.

Live composition at fix time (confirms the repo AS-IS is the regression composition):

```
{'accepted': 27, 'blocked': 2, 'claimed': 2}   # zero backlog tasks
```

## 2. Fix (test-only; no change to project_control.py)

File changed: `tools/test_project_control.py` only (75 insertions, 11 deletions).

Decoupling mechanism:

1. **Synthesis helper** `_synthesize_backlog_exemplar(pc)` (+ `_SYNTHETIC_BACKLOG_ID = "M9-T700"`):
   writes a well-formed, clearly-labeled SYNTHETIC backlog task file into the TEMP ledger copy
   (never the real ledger). Its docstring records why (live backlog can legitimately be empty;
   cites CI job 87990690868).
2. **Probe decoupled from live composition:** `probe_id = backlog[0] if backlog else
   _synthesize_backlog_exemplar(pc)` — a real backlog task is still used when one exists, so the
   original probe semantics are preserved; the exemplar is synthesized only when needed.
3. **Permanent zero-backlog sub-check:** after the first probe, S7 now deletes EVERY
   backlog-status task file from the temp copy (reproducing the exact composition that broke CI),
   asserts `status` still serves the drained ledger with zero backlog tasks, synthesizes the
   exemplar, and proves the message-only progress probe stays green. This runs on every suite
   execution regardless of live composition.
4. **Docstring updates:** module docstring S7 entry documents the stable-invariant policy and the
   synthesis/sub-check; the S7 print line now reports the zero-backlog sub-check.

Everything S7 previously verified is intact and unweakened: full real-ledger parse
(`parsed >= 60`; 145 files today), `status` over the real roster, accepted-count floor
(`>= 21`), message-only progress not retro-rejected, legacy no-role gate records satisfying
`accept`, write-time-only validation.

## 3. Other couplings of the same class — audit result

Scanned the whole suite for dependence on mutable live statuses:

- `REAL_PC` is referenced only in S7 (grep: lines 66, 817, 823, 825). All other groups
  (original workflow, S1–S6, S8, docs-honesty) build fully synthetic temp ledgers via
  `make_temp_project` and copy only `project_control.py` source — no live-data coupling.
- Within S7, the two remaining count assertions are stable invariants, kept deliberately:
  - `parsed >= 60`: ledger files are only ever added (tasks/gates/blockers are never deleted),
    so the floor is monotone-safe.
  - `task_counts.accepted >= 21`: `accepted` is terminal and immutable (proven by S6), so the
    count is monotone non-decreasing.
- No assertion anywhere depends on the existence of a live `claimed`/`in_progress`/`blocked`
  task or on exact live counts. **No other couplings found.**

## 4. Commands run and full output (self-check, G2 evidence)

### (a)+(c) Full suite against the real ledger AS-IS (which is currently zero-backlog — the regression composition) — all 10 groups green

```
> python tools/test_project_control.py
OK: original 15-check workflow preserved
OK: S1 transition enum (legal chain passes; every prohibited jump rejected)
OK: S2 accept preconditions (status, gates, dependencies, blockers)
OK: S3 gate classes (independent/self_check/administrative; no bypass)
OK: S4 containment (task ids, report paths, gate ids, checkpoint ids)
OK: S5 atomic writes (concurrent invocations, interrupted write, serialization failure)
OK: S6 spoofing attempts all rejected
OK: S7 backward compatibility (145 real ledger files parse; legacy records accepted; validation is write-time only; zero-backlog composition survived via synthesized exemplar)
OK: S8 hardening follow-up (orchestrator roster prohibition, --gates enum, blocked-task roster precondition)
OK: docs honesty (--agent disclaimed in --help and module docstring)
OK: all 10 project-control test groups passed
```

### (b) Regression simulation

Two-sided proof:

- The zero-backlog composition is exercised twice on every run: today's real ledger has zero
  backlog tasks (see composition dump above), and the permanent sub-check additionally drains
  the copy and re-proves the synthesis path.
- The opposite branch (live ledger HAS a backlog task → probe uses the real record, then the
  sub-check drains it) was proven with a one-off harness that pointed the test module's
  `REAL_PC` at an augmented temp copy of the real ledger containing an added backlog task
  `M9-T699`:

```
> python -c "<load tools/test_project_control.py; copy real ledger to temp; add backlog task M9-T699; patch m.REAL_PC; m.test_s7_backward_compatibility()>"
OK: S7 backward compatibility (146 real ledger files parse; legacy records accepted; validation is write-time only; zero-backlog composition survived via synthesized exemplar)
OK: backlog-present branch (real backlog task probed, then drained by the zero-backlog sub-check)
```

### File-scope and ledger-integrity check

```
> git status --porcelain
 M tools/test_project_control.py
> git diff --stat
 tools/test_project_control.py | 86 +++++++++++++++++++++++++++++++++++++------
 1 file changed, 75 insertions(+), 11 deletions(-)
```

Only the allowed test file is modified. The real `project-control/` ledger shows no
modifications (all probes ran against disposable temp copies, deleted in `finally` blocks).
`tools/project_control.py` is unchanged (no behavior change; the docstring-only allowance was
not needed — the synthesis rationale lives in the test file).

## 5. Acceptance-scenario mapping

- Primary success: full suite green against real ledger AS-IS — section 4(a).
- Boundary/regression: zero-backlog composition (the CI failure) — real-ledger run + permanent
  sub-check, section 4(b).
- Ambiguous/alternate composition: backlog-present branch proven via augmented-ledger harness.
- Regression of previously working behavior: all prior S7 checks and the other 9 groups
  unweakened and green.

## 6. Assumptions and limitations

- Assumption: ledger files are append-only in practice (tasks/gates/blockers never deleted),
  so the `parsed >= 60` and `accepted >= 21` floors remain stable invariants. If the
  orchestrator ever prunes ledger files, those floors would need revisiting (documented in the
  module docstring's stable-invariant policy).
- Assumption: `M9-T700`/`M9-T699` ids never collide with real ledger ids (real ledger uses
  M0–M7 milestones; the M9 namespace is the suite's established synthetic convention).
- Limitation: the backlog-present branch is exercised in CI only when the live ledger happens
  to contain a backlog task; the one-off augmented-ledger proof above covers it otherwise. The
  probe behavior is identical either way (message-only progress on a backlog-status file).
- No security/provenance impact: test-only change; no schema, contract, or enforcement change.

## 7. Recommended next steps

- Independent gate (G3) re-run of `python tools/test_project_control.py` from a clean checkout
  of `task/M0-T017-s7-ledger-coupling`.
- After integration, confirm the control-plane CI job goes green on main with the current
  zero-backlog ledger.
