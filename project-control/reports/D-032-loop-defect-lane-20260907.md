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

## DL-2 recurrence and bounded closure (run persistent-local-07, 2026-09-07 ~06:20Z; orchestrator, /deficit-convergence)

- **Recurrence (2nd occurrence, exact same shape):** run-07 (M0-T152, boot 06:01:34Z, supervisor
  pid 26720, worker pid 23944 / session 6bbc7cd8) ran its unit ~19 min (1 claude run, budget
  `elapsed_high_water` 1135 s), then journal seq 199→200 at 06:20:29Z:
  `checkpoint_field_mismatch: worker-supplied starting_sha='0e067b6a' does not match the
  controller-authoritative value '0e067b6a8dbb6a52ecb02b80a83f6f531010a805'; refusing to
  overwrite` → PAUSED_RECOVERY, supervisor exit 11, `exit_reason=no_valid_checkpoint`.
  Controller behavior CORRECT (fail-closed by design); the loss is again the transport envelope,
  not the work.
- **Causal path completed (certified controller source, read-only):**
  `checkpoint_envelope.enrich_checkpoint` (M0-T133) FILLS an absent/blank envelope field with the
  controller-measured authoritative value and fail-closes on any supplied mismatch;
  `normalize_sha` requires full 40-hex, so an abbreviated sha can never match. The worker-facing
  contract (`prompts/claude_checkpoint.md` + `build_checkpoint_contract`) lists `starting_sha`
  as required and shows `"starting_sha": "..."` without stating the full-40-hex/leave-empty
  rule — the worker filled a short sha both times (run-06 `bb71b2ef`, run-07 `0e067b6a`).
- **Bounded repair (the recorded DL-2 prompt-side lane candidate, no controller change):** the
  CLAIMED `M0-T152.json` packet now carries a CHECKPOINT ENVELOPE CONTRACT note (full 40-hex or
  empty string; both prior refusal reasons forwarded verbatim; applies to all four envelope
  fields), synced byte-identical to the wt-m0t152 copy (packet digest `c2d19690f624a104…`;
  ctl24 commit 6c0ca915, worktree commit 382abf6d).
- **Work preserved:** run-07's worker product (gate_wave.py, test_agent_supervisor_gate_wave.py,
  cli.py/loop.py edits — 1848 insertions) committed on `task/M0-T152-gate-wave-engine` at
  26c973ea (orchestrator commit duty; also required, a dirty worker worktree would fail-close
  the relaunch preflight).
- **Operator actions (dead run only; verbs addressed with `--checkout C:\SupervisorController`
  — the cwd-default addresses the WRONG runtime and reports empty stores, a DL trap):**
  denied stale run-07 ask `5f2a499c-088b…` (Edit `.claude/rules/supervisor-freeze.md`,
  permission_settings class; digest `2a2eeeae…`) — the deny resolves the journal `queued_asks`
  row per M0-T115; `clear-recovery` → PREFLIGHT.
- **The ONE justified rerun (closure-matrix complete before launch):** run-id
  `persistent-local-08`, same command otherwise, cwd wt-controller-src (certified a5886dab).
  Preflight PASS, seq 202 START_CLAUDE at 06:31:45Z, supervisor pid 13352, worker pid 7000.
  Verification of the repair = run-08's own checkpoint passing the envelope contract; watcher
  armed. NOTE for run-08: the worker may legitimately re-ask to edit
  `.claude/rules/supervisor-freeze.md` (in allowed_paths, permission_settings class is never
  baseline-AUTO) — that will pause the run for an operator answer; answer the FRESH ask on its
  own digest, never resurrect the denied one.
- **Lane candidate unchanged:** the durable fix (contract text in the controller's own prompt
  template, and/or prefix acceptance against the known authoritative value) remains a contracted
  follow-up under the supervisor freeze — this packet note is the bounded prompt-side repair the
  lane recorded, applied at the packet layer the orchestrator lawfully controls.
