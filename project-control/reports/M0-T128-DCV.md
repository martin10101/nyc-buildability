# M0-T128 - DCV verification report (independent directive-compliance-verifier, read-only) - VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31. VERDICT: ALL 6 applicable rows (R400-R405)
SATISFIED at remediated material de18f27 (tip 7110aec; supervisor content stable to HEAD).
The DCV reproduced the cross_task pack (45) and next_task (18) itself, live re-checked the
preserved journal (PAUSED_RECOVERY/22/53/0) and PR #241 (OPEN untouched), verified the mode
guard first-act placement, the advance-before-select CAS ordering, the eleven-category
eligibility, and the empty diffs over broker/recovery/start_gate/state_machine. Five
non-blocking observations (G2 pending as the normal closing step; next_task.py review_signal;
coverage-altitude honesty; narrow eligible-status set; manifest verified by content identity).
G2 recorded and verification rows written from this report; accept follows.

---VERBATIM-BEGIN---
Both delta reports are genuine independent reproductions corroborating my findings. I now have full coverage of all 6 rows. Here is my DCV record for M0-T128.

---

# DCV REPORT - Task M0-T128 (D-024 Amendment 25, Stage-3 wiring; rows R400-R405)

## VERDICT: **PASS** - ALL 6 applicable requirement rows SATISFIED

**Reviewed identity:** material `de18f27` (remediated). Branch tip HEAD = `7110aec`. Content identity verified: `git diff de18f27 HEAD -- tools/ .github/ docs/CONTROLLER_UPDATE_RUNBOOK.md` is **EMPTY** (commits `de18f27..HEAD` are control-plane: agent-memory + resubmit + G3/G4 delta records). Submit `reviewed_sha a59a3a6` has supervisor content byte-identical to `de18f27` (`git diff a59a3a6 de18f27` over supervisor paths empty). Wiring diff `7576e0d..de18f27` touches only cli.py (+12/-7), next_task.py (+549), and the new cross_task test file (+1126). Producer = `supervisor-wiring-producer` != every reviewer (code-reviewer/qa-engineer/DCV). I judged each row on primary evidence I reproduced.

## Row-by-row verdicts

| Req | Verdict | Primary evidence reproduced |
|---|---|---|
| **R400** (wiring authorization delivered) | SATISFIED | `run_task_queue` at next_task.py:763; wired at **cli.py:3069** (`run = (next_task.run_task_queue(args, checkout, journal, audit, _run_loop) if int(args.max_tasks)>1 or args.packet_queue else _run_loop(...))`) behind `bounded_mode_gate` (cli.py:2918) + the driver's own mode guard. **I reproduced `pytest tools/test_agent_supervisor_cross_task.py` = 45 passed.** Dispatch coverage `CmdStartDispatchTests` (executes the verbatim cli.py:3069 via inspect+ast) and real-journey `LiveRunLoopCrossTaskTests` both present + pass. Driver: complete first task -> CAS advance -> select next eligible -> re-bind isolated worktree -> continue across `--max-tasks` bounded tasks with no owner touch. |
| **R401** (journal/evidence untouched) | SATISFIED | LIVE re-check: journal `PAUSED_RECOVERY`, transitions **22**, effects/outbox/inbox **0**, audit **53**; `wt-m0t107` clean at `796e18f`. New tests use `tempfile.TemporaryDirectory` (cross_task.py:158-162) - temp runtimes only. Driver writes only NEW durable keys (`task_advancement/<id>`, `task_queue/queued_digest/<id>`), never the preserved journal rows. |
| **R402** (gates/fail-closed/budget/audit/isolation/exactly-once maintained) | SATISFIED | Mode guard is the **FIRST act** of run_task_queue (next_task.py:792-803, fail-closed audit+`NextTaskError` before any packet read - G3 confirmed genuinely first). Advance-before-select: `record_advancement` CAS (next_task.py:877) BEFORE the successor's `evaluate_eligibility`. Shared-budget clean-resume (design sec 5A) matches G3's run_budget.py:341-434 analysis; `LiveRunLoopCrossTaskTests` asserts `run_budget_started`x1 + `run_budget_resumed`x1, no `budget_conflict`, `run_closed` COMPLETE->IDLE, empty `pending_effects` (D6). **No broker/recovery/start_gate/state_machine change** in `git diff 7576e0d de18f27` (empty); wiring only references the EXISTING bounded_mode_gate - no R595/allowlist change. Exactly-once preserved: `pytest next_task` = 18 passed; crash matrix genuine reopen. |
| **R403** (window holds) | SATISFIED | PR #241 **OPEN**, updatedAt 2026-08-20 (untouched). No clear-recovery/loop start/live commissioning - proven by the unchanged journal (PAUSED_RECOVERY/22/53/0; a start or clear-recovery would move state/counts). |
| **R404** (ten removal-sensitive families) | SATISFIED | Design sec 9 maps all ten families to test classes, matching R404's list exactly. Spot-verified by collection + read: family 1 `LiveCrossTaskSelectionTests` (2 nodes), family 7 `CrashMatrixTests` (2 - read bodies: genuine `self.reopen()` journal reopen; no double-advance), family 8 `StalePacketTests` (3 - read: CAS-once snapshot survives restart, mid-journey edit -> stale skip), family 9 `NoEligibleWorkTests` (read: all-ineligible -> NO_ELIGIBLE_WORK), family 10 `BetweenTaskIntentTests` (5 nodes: emergency/pause/graceful/budget/no-intent). All in the 45-pass pack; G3/G4 independently confirmed mutation-sensitivity. |
| **R405** (never silently select ineligible) | SATISFIED | `evaluate_eligibility` at next_task.py:551 - **eleven** fail-closed VISIBLE categories, first-failing-check-wins: packet-parse (3 sub-codes packet_unreadable/packet_unparseable/packet_not_object), task_id_mismatch, ineligible_status (only `claimed` eligible), blocked, owner_gated (OWNER_GATE_FIELDS), dependency_unresolved, dependency_unaccepted, worktree_missing, worktree_primary_checkout, binding_*, stale_packet. Each returns a coded+reasoned `EligibilityVerdict(False,...)`; the driver audits `cross_task_candidate_skipped` + `skipped` step (never silent). Category->test coverage: `EligibilitySkipTests` + `Category1SubCodeTests` (collected + pass). |

## Discrepancies / observations (all NON-BLOCKING)

1. **G2 self-check gate not yet recorded.** `required_gates=[G0,G2,G3,G4]`; G0/G3/G4 PASS are on file (G3/G4 as delta reports; both reviewed at `de18f27` supervisor content - G3 `reviewed_sha 1d00e7b`, G4 `bef57c5`, both content-identical to `de18f27`). No `M0-T128-G2.json` yet - the G2 self-check + this DCV are the closing orchestrator-recorded steps before `accept()`, which the CLI enforces. Normal in-flight state, not a producer defect.
2. **next_task.py modularity (review_signal, non-blocking).** The module grew to ~691-712 SLOC - above WARN 600, below JUSTIFY 750, well below HARD 1000; `modularity_check --check` = **0 failures**. Design sec 11 discloses this honestly; the packet directed placement in next_task.py (no new module in allowed_paths). The diff is cohesive (all cross-task selection/eligibility/queue/driver logic in the packet's designated home). Both G3 and G4 flagged it non-blocking; a focused extraction is advisable on next growth.
3. **Real-loop coverage altitude (design sec 12-1, honest limitation).** `LiveRunLoopCrossTaskTests` drives the real `cli._run_loop` + real `SupervisedLoop` + real journal + real CAS/close-run/D6 with only the PROVIDER (ClaudeRunner/CodexReviewer) faked; the full `cmd_start` entry-to-3069 gauntlet needs live auth/capability-manifest probes (golden-run altitude). Legitimately out of a wiring task's scope under R403 (no live commissioning); the full seven-fact live proof is the separate R406/R407 step.
4. **Eligible-status set is narrow (`{"claimed"}`, design sec 12-2).** A conscious documented default (constant `ELIGIBLE_STATUSES`); widening needs one edit if a future campaign uses a different vocabulary. Design note, not a defect.
5. **Manifest note:** I verified the submit content identity (reviewed_sha `a59a3a6` supervisor content == `de18f27`, empty diff) rather than recomputing the orchestrator-produced `content_manifest_sha256` byte-for-byte; the reviewed content identity is sound and stable to HEAD.

## Exact commands run (read-only)

- `git rev-parse HEAD` (`7110aec`); `git diff de18f27 HEAD -- tools/ .github/ docs/CONTROLLER_UPDATE_RUNBOOK.md` (empty); `git diff a59a3a6 de18f27 -- <supervisor paths>` (empty); `git diff --stat 7576e0d de18f27 ...`; `git diff --stat 7576e0d de18f27 -- broker.py recovery.py start_gate.py state_machine.py` (empty); `git log --oneline de18f27..HEAD`.
- `python -m pytest tools/test_agent_supervisor_cross_task.py -q` -> **45 passed**; `... --collect-only` for family nodes; `pytest test_agent_supervisor_next_task.py` -> **18 passed**.
- `python tools/modularity_check.py --check` -> 0 failures (next_task.py review_signal warning).
- Read-only sqlite (`mode=ro&immutable=1`): PAUSED_RECOVERY/22/0; `wc -l audit.jsonl`=53; `git -C wt-m0t107 status` clean; `gh pr view 241` -> OPEN/2026-08-20.
- `Read` of source-025-amendment.md, requirements R400-R405, task packet, submit record, design-record (sec 3/5A/7/9/12), next_task.py:551-882 (evaluate_eligibility + run_task_queue), cross_task.py:584-703 (crash/stale/no-eligible bodies), G3-delta + G4-delta gate reports; `grep` of the wiring diff for R595/allowlist tokens (only EXISTING bounded_mode_gate references) and temp-runtime usage.

No writes outside my agent-memory scope; no `project_control.py`/git-write/`gh`-write/supervisor-write verb; the live journal was opened read-only only.

**Recommendation to orchestrator:** record this DCV as **PASS** for the 6-row applicable set (R400-R405) into `verification.json`; then record the pending **G2** self-check before `accept()`. The Stage-3 wiring is DCV-complete at material `de18f27`: the exactly-once next-task machinery is now live behind the existing bounded-mode owner gate + a first-act mode guard, eleven-category fail-closed eligibility, ten removal-sensitive families, journal/evidence and PR #241 untouched. Relevant paths (absolute):
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\next_task.py` (evaluate_eligibility:551, run_task_queue:763), `...\cli.py:3069`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_cross_task.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T128-{design-record.md,G3-code-review-delta.md,G4-qa-review-delta.md}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-024-fable-codex-loop\source-025-amendment.md`
- `C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\33dfa57d...\` (preserved journal, read-only); `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t107` (clean at 796e18f)
---VERBATIM-END---
