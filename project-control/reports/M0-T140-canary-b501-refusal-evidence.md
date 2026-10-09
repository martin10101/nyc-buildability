# M0-T140 — preserved evidence: failed live canary run of 2026-09-02 (owner-typed)

Preserves the owner-reported result of the first live run of the assembled M0-T136 ten-item
canary block (D-024 Amendment 43, R647). Nothing here is a PASS claim; the run stopped safely
before provider contact and Steps C–E never ran.

## Owner-reported result (verbatim from the directive, source-043-amendment.md)

> * canary-b5-01 returned the expected safety exit 11;
> * but it refused on `task_authority`, not the intended `launch_manifest_mismatch / clean_status`;
> * M0-T136 is already accepted, so it cannot serve as an executable canary task;
> * the controller entered PAUSED_RECOVERY;
> * no provider was contacted;
> * Steps C–E were not run.

## Orchestrator-observed corroboration (read-only, 2026-09-02, post-failure)

- Controller audit log (`%LOCALAPPDATA%\NYCBuildabilitySupervisor\9aca707563cfe6e2cdeeee99e5d153951936dc46edac131889c37c2a9f713b6a\audit.jsonl`)
  grew from head sequence 12 (pre-canary preflight) to 13. Record 13, verbatim fields:
  `event_type` `recover_boot`, `policy_result` `UNSAFE_OR_DRIFTED`,
  `detail.next_state` `PAUSED_RECOVERY`, `detail.reason_code` `unsafe_or_drifted`,
  `detail.resume_permitted` false, `timestamp_utc` `2026-09-02T17:54:45.492Z`,
  `digest` `a0efdd2314c8be396a0aacfe1ee39207527d40566b50a07a518181633a5f830b`,
  `prev_digest` `dba29932fefa8b43ee49b456f781ef85abb30be7647cc8454b005d2c17767efc`.
- Durable journal state at observation time: `status --checkout C:\SupervisorController`
  reports state **COMPLETE** (transitions 9, audit chain ok head 13);
  `recovery-status` reports COMPLETE, no emergency stop, no manual pause, autostart
  permitted, 0 surviving children, 0 pending effects. The PAUSED_RECOVERY the owner saw was
  the refused start's announced `next_state`; the durable journal did not remain parked.
  The corrected script therefore treats PAUSED_RECOVERY **conditionally** (canonical
  §9a `clear-recovery` only when `recovery-status` actually reports PAUSED_RECOVERY —
  the command refuses from any other state) and never assumes either state.
- No `mrl\` run directory exists under the controller runtime dir: no `one_shot_unit.json`
  for canary-b5-01 or canary-b5-02 — **no provider contact**, corroborating the owner report.
- Task worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`: `CANARY-UNTRACKED.txt` absent,
  `git status --porcelain` empty, HEAD `21e67bb053e48881b9d883e84028ff58846a7b66` (R646).

## Root cause (traced, R648)

`tools/agent_supervisor/probe_control_plane.py::probe_task_authority` confers working
authority only when the task packet AND the ledger record at
`project-control/tasks/<task_id>.json` agree on task_id and status, the status is in
`WORKING_STATUSES = {claimed, in_progress, awaiting_gate}`, and no OPEN blocker names the
task. The canary launch manifest bound `--task-packet ...\tasks\M0-T136.json`; M0-T136 is
`accepted` (2026-09-02T04:30Z) → `task_not_active` → recover_boot classification
UNSAFE_OR_DRIFTED → typed exit 11 before any provider contact. The accepted canary package
predates M0-T136's acceptance; acceptance is immutable (never reopened), so the correction
is a dedicated claimed execution vehicle: **M0-T140** (this task).

## Canonical recovery procedure (traced, R648)

`docs/CONTROLLER_UPDATE_RUNBOOK.md` §9a: leaving PAUSED_RECOVERY is the explicit audited
owner act `python -m tools.agent_supervisor clear-recovery --checkout <checkout>` — one
fail-closed command that clears no flag, resets no budget, dispatches nothing, and refuses
from any state other than PAUSED_RECOVERY. The corrected script runs it only when
`recovery-status` for `C:\SupervisorController` actually reports PAUSED_RECOVERY (checked
before the b5-01 refusal probe and again before the b5-02 one-shot), and otherwise proceeds
without touching runtime state. Runtime state is never deleted or hand-edited (R654).
