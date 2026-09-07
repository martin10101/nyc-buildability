# D-032 loop defect lane — run persistent-local-06 findings (2026-09-07, orchestrator)

Two reproduced defects from tonight's run, recorded with durable evidence for the
loop-improvement lane (supervisor-freeze AD-093 qualifying evidence class:
reproduced defect / measured usage problem). No controller code was changed for
either; both are candidates for future contracted tasks.

## DL-1: queue file duplicating the owner-typed first task starves successors

- **Symptom:** run-06 (owner boot 04:04Z) completed M0-T025, recorded its
  advancement (audit seq 53), then exited WITHOUT dispatching M0-T149 —
  stop reason `max_tasks_reached`.
- **Cause (traced, not guessed):** `run_task_queue`
  (`tools/agent_supervisor/next_task.py:806-841`) takes task 1 from the
  owner-typed `--task-packet` and treats every `--packet-queue` entry as a
  SUCCESSOR; an already-advanced entry "counts toward the bound" (line 830).
  Queue v3 (`project-control/campaigns/D-032-product-queue-v3.json`) listed
  M0-T025 as BOTH the first queue entry and the `--task-packet` task, so after
  advancement the duplicate consumed the second `--max-tasks 2` slot. With that
  file shape task 2 was unreachable at any relaunch.
- **Repair used tonight:** successors-only queue v3b (commit 207191db) +
  relaunch same run-id → M0-T149 dispatched `successor=true` (audit seq 58).
- **Lane candidate:** either (a) `load_task_queue` refuses/dedupes a queue entry
  whose task_id equals the `--task-packet` task, or (b) the queue-authoring
  convention (successors only) is enforced by a validator. Fail-closed refusal
  preferred over silent dedupe.

## DL-2: worker checkpoint refused for abbreviated starting_sha

- **Symptom:** relaunch boot 04:37Z; the M0-T149 unit ran to completion
  (562 events, returncode 0, model claude-fable-5, 8 in-scope writes, 7
  documented-test approvals) but the run stopped at
  `PAUSED_RECOVERY/no_valid_checkpoint` (exit 11).
- **Cause (journal transitions seq 196, verbatim):** `checkpoint_field_mismatch:
  worker-supplied starting_sha='bb71b2ef' does not match the
  controller-authoritative value 'bb71b2ef261686bcfa8193ef6971fa5f56319f0b';
  refusing to overwrite` — the worker abbreviated the sha; the contract check is
  exact string equality. Fail-closed behavior is correct; the loss is one unit's
  transport envelope, not its work.
- **Disposition tonight:** the completed producer work in `wt-m0t149` proceeds
  through the standard orchestrator gate wave (frozen candidate ed04c4bb); no
  live re-run was used for discovery (deficit-convergence rule).
- **Lane candidate:** the forwarded checkpoint contract should state FULL
  40-hex sha explicitly (prompt-side), and/or the validator may accept an
  unambiguous prefix of the authoritative sha it already knows (comparison
  against a known value — not a loosening of trust). Either way the failure
  reason should be forwarded into the next unit's prompt on relaunch so the
  worker can self-correct.

## Run-06 outcome summary (for R754 and the campaign record)

| Fact | Evidence |
|---|---|
| Acceptance-class verdict via live astra | audit seq 49: `codex_review_decision` COMPLETE, gpt-6-astra, M0-T025 |
| Multi-task successor dispatch | audit seq 58: `cross_task_dispatch` successor=true, M0-T149 |
| Committed foreground launch transcript | `project-control/reports/D-024-R754-run06-relaunch-transcript.txt` (commit 3618caee) |
| Durable run budget across resumes | audit seq 61: resumes=5, same `run_budget/persistent-local-06` |
| Fail-closed unattended stop | transcript + journal seq 196 (PAUSED_RECOVERY, exit 11) |

The journal remains in PAUSED_RECOVERY; `clear-recovery` (audited) is required
before the next start against this checkout, and per the M0-T149 producer
report's recertification note the changed controller subtree requires R247
recert + reinstall before the NEW code is ever installed (the currently
installed certified controller a5886dab is unaffected).

*Correction (2026-09-07, per the R754 closure DCV provenance note): the
completing checkpoint the chain records at seq 51/53 is
`M0-T025-2026-09-07-handoff-unit-01` (the cycle-2 unit), not
`M0-T025-persistent-local-06-u01-cp1` (the cycle-1 checkpoint, seq 34) named
in this report's earlier prose and in the queue-v3b authority text. The chain
is authoritative; the prose naming above is superseded by this note.*
