<!-- Verbatim reviewer return (agent-return channel; agentId a0996e1f783dc472f, security-reviewer, 2026-07-17). Saved by the orchestrator per the report-preservation rule. Verdict: G4 PASS (one LOW non-blocking observation OBS-1 for the hardening backlog). -->

# G4 Gate Report — M0-T016 (Project-Control CLI Hardening Follow-up)

**Task:** M0-T016 — orchestrator-roster prohibition, `--gates` enum validation, blocked-task roster precondition
**Reviewer:** security-reviewer (independent G4, control-plane authority lens) — did NOT produce this work
**Worktree:** `.claude/worktrees/M0-T016/` · branch `task/M0-T016-control-hardening-followup` · HEAD `debe698`
**Method:** Read packet S1–S4, read full diff of both changed files, ran the full suite in-worktree, ran 6 adversarial bypass probes directly against a disposable CLI instance. Read-only per ADR-005; no ledger/git/gh writes.

---

## Integration / Regression findings

**Full suite: PASS (10/10 groups).** Ran `python tools/test_project_control.py` in the worktree:
```
OK: original 15-check workflow preserved
OK: S1 transition enum (legal chain passes; every prohibited jump rejected)
OK: S2 accept preconditions (status, gates, dependencies, blockers)
OK: S3 gate classes (independent/self_check/administrative; no bypass)
OK: S4 containment (task ids, report paths, gate ids, checkpoint ids)
OK: S5 atomic writes (concurrent invocations, interrupted write, serialization failure)
OK: S6 spoofing attempts all rejected
OK: S7 backward compatibility (134 real ledger files parse; legacy records accepted; validation is write-time only)
OK: S8 hardening follow-up (orchestrator roster prohibition, --gates enum, blocked-task roster precondition)
OK: docs honesty
OK: all 10 project-control test groups passed
```
- The pre-existing 9 groups all still pass → **no regression**. The new S8 hardening group and the S7 real-ledger backward-compat group both pass.
- **No retro-rejection confirmed.** S7 copies the real 134-file ledger; all parse, the 21+ accepted tasks remain visible, legacy gate records without a `role` field still satisfy `accept()`, and a message-only progress on a copied real task succeeds. I independently confirmed that a message-only / same-status progress on a `blocked` task with an empty roster is NOT tripped by the new roster rail (`rc=0`) — validation is write-transition-only.
- **Scope: clean.** `git diff 7087ee1..debe698` touches exactly the three allowed paths (`tools/project_control.py` +82, `tools/test_project_control.py` +167, `project-control/reports/M0-T016-producer-report.md` +143). No file under `project-control/tasks/` was touched — **M0-T007.json / M0-T008.json are byte-unchanged** (forbidden paths respected; their `blocked` status is not altered, matching the packet's "documented + enforced precondition, no status change" requirement).
- **No new dependencies, no network, pure stdlib.** Imports unchanged (`argparse, datetime, json, os, re, sys, tempfile, time`, pathlib). Grep for `socket|urllib|requests|http|subprocess|eval(|exec(|os.system|popen|__import__|pickle` → NONE. No secrets in the diff.

## Authority / Security findings

- **Independent-gate bypass via `orchestrator` (primary rail): CLOSED for the literal identity.** I forced a legacy packet with `reviewer_agents=["orchestrator","rev-a"]` and tried `--reviewer orchestrator` on G1/G3/G4/G5/G6 → all rejected ("reserved"), no gate record written. A real rostered reviewer (`rev-a`) still passes. `new_task --reviewers` containing `orchestrator` (alone or mixed) is rejected and the task file is not created.
- **Self-approval prevention: intact.** Producer==reviewer (case-identical) still rejected at `gate()` and at `accept()`; a hand-forged `self_check`/`administrative` role record can never satisfy an independent gate at accept-time (S3 covers this and it passed).
- **Least authority / no over-blocking: confirmed.** The orchestrator's legitimate G2 `self_check` and G0/G7 `administrative` paths STILL WORK (rc=0, correct roles recorded) — the new prohibition did not break positive paths.
- **Bounded errors / no info leak: confirmed.** The `--gates` rejection echoes only the caller's own offending tokens plus the fixed 8-item enum (e.g. `Invalid --gates entry(ies): G9, SECRET_KEY_ABC, ../etc/passwd. Allowed gates are G0..G7.`). No secrets, no unbounded internal state, no filesystem paths are used from the offending input — it is reflected caller input only.
- **`--gates` enum + blocked-roster edges: correct.** Whitespace/empty/trailing-comma gate entries (` G3`, `G3 `, `,G3`, `G3,`, `G3,,G4`) all rejected; full `G0..G7` accepted and stored unchanged. Blocked→active without a usable roster rejected with an "amend" message; `blocked→canceled` always allowed; unblock works after packet amendment.

### Defect — OBS-1 (LOW, non-blocking): authority rails are case/whitespace-sensitive literal equality

Adversarial probe (Probe 6, variant B): a task with `producer_agent="Orchestrator"`, G3 recorded by reviewer `ORCHESTRATOR`, and G0 by real `orchestrator` was **ACCEPTED end-to-end**. Case-variants (`Orchestrator`, `ORCHESTRATOR`) and leading-whitespace (` orchestrator`) slip both the new reserved-identity rail and the pre-existing `producer==reviewer` rail (I also confirmed `Backend-X` reviewer passes on a `backend-x` task).

**Assessment — not blocking:**
1. This is a **pre-existing property of the M0-T014 gate-class model**, not introduced by M0-T016. The `producer==reviewer` rail has always been literal `==`. M0-T016's new rail deliberately matches that model.
2. The packet objective explicitly scopes it: "a string-equality rail on the literal `orchestrator` [that] does NOT catch look-alikes (e.g. `orchestrator-2`)." Case/whitespace variants are the same class of disclosed look-alike.
3. Identity is procedural, not cryptographic (ADR-005): only the main-session orchestrator runs the CLI, and agent names come from a fixed orchestrator-controlled roster — a case-variant would have to be deliberately authored by the orchestrator into a packet, which is out of the threat model this rail defends.

**Remediation (optional hardening backlog, not required for this gate):** normalize with `.strip().casefold()` at the three comparison sites (`RESERVED_ORCHESTRATOR` checks in `new_task`/`gate`/`invalid_unblock_roster`, and the `producer==reviewer` checks in `gate`/`accept`) for cheap defense-in-depth. If any future task re-frames these rails as a *security boundary* rather than a procedural integrity rail, this observation escalates to HIGH and becomes in-scope.

---

## Verdict

All four acceptance scenarios (S1–S4) are satisfied: orchestrator rejected as independent reviewer on write while its self_check/admin paths survive (S1); `--gates` enum validated with bounded errors (S2); blocked-roster precondition enforced with amend-then-unblock working and M0-T007/T008 untouched (S3); full suite + backward-compat green with no retro-rejection (S4). Scope clean, forbidden paths untouched, pure stdlib, no leaks. The single finding is a disclosed, pre-existing, procedurally-mitigated LOW observation for the hardening backlog — it does not block.

`G4: PASS`
