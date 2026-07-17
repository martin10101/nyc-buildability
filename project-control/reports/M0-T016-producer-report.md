# M0-T016 Producer Report — Project-control hardening follow-up

**Task ID:** M0-T016
**Producer:** backend-engineer
**Branch:** task/M0-T016-control-hardening-followup (worktree `.claude/worktrees/M0-T016`)
**Status requested:** `awaiting_gate` (all acceptance scenarios S1–S4 pass; full suite green)

## Scope implemented (exactly the three packet items)

1. **Orchestrator roster prohibition** (packet output 1; closes M0-T014 G5 defect D1).
2. **`--gates` enum validation** (packet output 2; closes D2).
3. **Blocked-task roster precondition** (packet output 3; closes M0-T014 G3 OBS-3).

Nothing else was changed. D3/D4 and remaining OBS items were left in the documented maintenance backlog per the packet.

## Files changed (exact paths)

- `tools/project_control.py` — CLI hardening (validation on WRITE only).
- `tools/test_project_control.py` — new S8 test group + docstring entry; existing groups untouched.
- `project-control/reports/M0-T016-producer-report.md` — this report.

Git status in the worktree (read-only, no git writes performed):

```
 M tools/project_control.py
 M tools/test_project_control.py
```

`project-control/tasks/M0-T007.json` and `M0-T008.json` are NOT in the changed set and were never opened for write. Their `blocked` status is unchanged. The S7 backward-compat test copies the entire real ledger (134 files) into a temp project and asserts it still parses and that ≥21 accepted tasks remain visible — proving no live ledger mutation.

## What changed in `tools/project_control.py`

- New module constant `RESERVED_ORCHESTRATOR = "orchestrator"` with an explanatory comment.
- `new_task()`:
  - `--gates` entries validated against `GATE_IDS` (`G0..G7`); unknown names rejected **before** the task file is written.
  - `orchestrator` rejected if present in `--reviewers`.
- `gate()` INDEPENDENT-gate branch (`G1/G3/G4/G5/G6`): rejects `--reviewer orchestrator` even when a legacy packet lists it in `reviewer_agents`. The G2 `self_check` and G0/G7 administrative branches (which *require* `reviewer == "orchestrator"`) are untouched and still work.
- New helper `invalid_unblock_roster(task)` + enforcement in `progress()`: a `blocked -> <active>` transition (every target except `canceled`) requires a valid roster (real producer that is not `orchestrator`, plus at least one reviewer that is non-empty, not `orchestrator`, and not equal to the producer). `canceled` is exempt; message-only progress (no status change) on a blocked task is never blocked.
- Module docstring TASK LIFECYCLE section documents the blocked-unblock roster precondition (packet required "document AND enforce").

All validation is **on write only**; `accept()` and read paths continue to tolerate legacy stored records (no `role` field, null dependencies, backslash report paths, etc.), verified by S7.

## Exact new bounded-error messages (captured verbatim from the CLI)

**D1 — orchestrator in `--reviewers` (new-task):**
```
Reviewer 'orchestrator' is reserved and may not appear in reviewer_agents: the orchestrator records self_check (G2) and administrative (G0/G7) gates but can never satisfy an independent gate (G1/G3/G4/G5/G6). List an independent reviewer instead.
```

**D1 — orchestrator on an independent gate:**
```
Reviewer 'orchestrator' is reserved and cannot record an independent gate (G3): it records self_check (G2) and administrative (G0/G7) gates only. An independent reviewer (!= producer, listed in reviewer_agents) must record G3.
```

**D2 — unknown `--gates` entry:**
```
Invalid --gates entry(ies): G9, bogus. Allowed gates are G0, G1, G2, G3, G4, G5, G6, G7.
```

**OBS-3 — unblock without a valid roster:**
```
Cannot unblock M9-T901 ('blocked' -> 'in_progress'): reviewer_agents has no usable independent reviewer (must be non-empty and contain a reviewer that is neither 'orchestrator' nor the producer 'backend-x'); amend the packet before unblocking. A blocked task cannot re-enter the workflow until the orchestrator amends its packet with a valid producer and independent-reviewer roster.
```
(Producer-missing and producer-is-orchestrator variants emit the same wrapper with a different clause: "no producer_agent is set…" / "producer_agent is the reserved 'orchestrator'…".)

## Acceptance scenarios → tests

All new tests live in `test_s8_hardening_followup()` (`tools/test_project_control.py`), registered in `ALL_TESTS`.

- **S1 (orchestrator prohibition):**
  - Negative: `orchestrator` alone and mixed into `--reviewers` at new-task → rejected, no task file created.
  - Negative: `--reviewer orchestrator` on each independent gate `G1/G3/G4/G5/G6`, with a legacy packet that rostered `orchestrator` → rejected, no gate record written.
  - Positive: legitimate `--reviewers` authors fine; a real rostered reviewer still passes the independent gate; **orchestrator G2 self_check and G0/G7 administrative gates still succeed** (role assertions `self_check` / `administrative`).
- **S2 (`--gates` enum):**
  - Negative: `G9`, `bogus`, `G0,G9`, `G3,bogus,G4`, `g3`, `G8`, `G10` → each rejected; error names the offending entry and lists `G0`…`G7`; no task file created.
  - Positive: full `G0,G1,G2,G3,G4,G5,G6,G7` accepted and stored unchanged.
- **S3 (blocked-task roster precondition):**
  - Negative: blocked task with empty roster cannot go to `backlog/ready/in_progress/awaiting_gate` (status stays `blocked`); producer==orchestrator, reviewer==producer, and reviewer==only-orchestrator are all invalid rosters.
  - Positive: `blocked -> canceled` always allowed; after a valid roster amendment the unblock (`blocked -> in_progress`) works; message-only progress on a blocked task is never blocked.
  - Real M0-T007/M0-T008 untouched (proved by the change set + S7 ledger-copy parse).
- **S4 (suite green + no retro-rejection of history):** full existing suite (9 groups) preserved and green; S7 (unchanged) copies the real ledger and confirms legacy records still parse and still satisfy `accept()`; S8 adds an explicit message-only-progress-on-blocked assertion proving the roster precondition does not retro-reject a no-status-change write.

## Commands run + full output (expected vs actual)

**Baseline (before changes), expected all-green:**
```
$ python tools/test_project_control.py
OK: original 15-check workflow preserved
OK: S1 ... OK: S7 backward compatibility (134 real ledger files parse; ...)
OK: docs honesty ...
OK: all 9 project-control test groups passed
```
Actual: 9 groups passed (baseline confirmed green in this session; full exec + network available).

**After changes, expected 10 groups green:**
```
$ python tools/test_project_control.py
OK: original 15-check workflow preserved
OK: S1 transition enum (legal chain passes; every prohibited jump rejected)
OK: S2 accept preconditions (status, gates, dependencies, blockers)
OK: S3 gate classes (independent/self_check/administrative; no bypass)
OK: S4 containment (task ids, report paths, gate ids, checkpoint ids)
OK: S5 atomic writes (concurrent invocations, interrupted write, serialization failure)
OK: S6 spoofing attempts all rejected
OK: S7 backward compatibility (134 real ledger files parse; legacy records accepted; validation is write-time only)
OK: S8 hardening follow-up (orchestrator roster prohibition, --gates enum, blocked-task roster precondition)
OK: docs honesty (--agent disclaimed in --help and module docstring)
OK: all 10 project-control test groups passed
```
Actual: **matches exactly — 10 groups, all passed.**

Bounded-error messages were additionally captured verbatim by driving the CLI against a disposable temp ledger (output reproduced in the section above). Expected: each rejection returns non-zero and prints the bounded message. Actual: matched.

## Assumptions and defaults

- "Valid roster" for the unblock precondition = non-empty producer ≠ `orchestrator` AND ≥1 reviewer that is non-empty, ≠ `orchestrator`, and ≠ producer. This mirrors the existing independent-gate rule (`gate()` already requires a rostered reviewer ≠ producer), so an unblocked task is guaranteed to have at least one reviewer that can actually satisfy its independent gates. If the reviewer intends a stricter notion (e.g. cross-checking against `required_gates`), that would be a scope change.
- `blocked -> canceled` is intentionally exempt: abandoning a blocked task must never be gated on roster quality.
- Message-only `progress` (no `--status`, or `--status` equal to current) on a blocked task is intentionally NOT gated (it is not an unblock), preserving the ability to log notes/percent on a blocked task.
- `progress` is the sole exit from `blocked` (verified: `claim` requires ready/rework; `submit` requires claimed/in_progress/self_check/rework; `gate` PASS effects act only on backlog/rework/awaiting_gate, BLOCKED only sets blocked). So enforcing in `progress()` fully closes the unblock path.

## Known limitations

- Identity remains procedural, not cryptographic (unchanged by this task): `--reviewer`/`--agent` are caller-provided labels. The orchestrator prohibition is a string-equality integrity rail on the reserved label `orchestrator`, consistent with the existing enforcement model documented in the module docstring.
- The prohibition matches the exact literal `orchestrator`; it does not attempt to catch look-alike labels (e.g. `orchestrator-2`). This matches D1's remediation scope (reserve the one reserved identity) and the existing gate-class rules that key on the same literal.

## Security / provenance impact

This is **control-plane authority hardening**. It strengthens producer/independent-reviewer separation (the core integrity property of the gate system): the orchestrator can no longer be recorded as an independent reviewer at author time or at gate time, a mistyped gate id can no longer author a task whose required gate set is permanently unsatisfiable, and a blocked task with a degenerate roster can no longer silently re-enter the workflow and later be gated by a non-existent/self reviewer. No secrets, network calls, or persistent data are involved; all changes are pure-stdlib validation on write. Backward compatibility is preserved (S7): no stored ledger record is retro-rejected.

## New risks / dependencies

- None introduced. The unblock precondition adds a gate on an already-rare transition; the S8 positive tests confirm legitimate unblock still works after a normal packet amendment.
- Follow-up dependency for the orchestrator (not this task): M0-T007 and M0-T008 will now require a packet roster amendment (producer + independent reviewer) before they can leave `blocked`. This is the intended enforcement; their status was deliberately left unchanged here.

## Recommended next tasks

1. G3 (code-reviewer) + G4 integration/regression gate on this change (packet-required gates: G0, G2, G3, G4).
2. Orchestrator: when M0-T007/M0-T008 are next scheduled, amend their packets with valid producer + independent-reviewer rosters (now enforced) before unblocking.
3. Optional maintenance backlog (unchanged scope): D3/D4 and remaining OBS items from M0-T014.

## Report path

`project-control/reports/M0-T016-producer-report.md`
