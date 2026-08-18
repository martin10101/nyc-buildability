OWNER AUTHORIZATION — BOUNDED SUPERVISOR REPAIR

We attempted to dispatch D-013 Unit A1, ledger task M0-T063, through the accepted supervised Codex/Claude loop.

The run failed closed before modifying the A1 repository:

- run_id: run_M0_T063_A1
- controller: 0.4.0-phase4
- final state was PAUSED_RECOVERY
- Claude requested three Bash commands
- all three were classified ASK because they were neither enumerated read-only Git commands nor packet-documented test commands
- Claude exited return code 1 without a structured checkpoint
- no Codex review occurred
- the A1 worktree remained completely clean at de2f224a7db16405edfc0e2f2f0902f5164819a0
- the owner subsequently ran revoke-all and clear-recovery
- revoke-all reported revoked=3
- current runtime state is PREFLIGHT
- pending-approvals must now report count=0
- status still misleadingly lists the three revoked requests under open_asks

This prompt explicitly authorizes a separate, bounded control-plane repair. It does NOT authorize restarting M0-T063, modifying its implementation files, merging, activating a replacement controller, changing protected configuration, or weakening the permission policy.

FIRST: perform read-only reconciliation.

1. Verify the current branch, HEAD, worktree cleanliness, origin/main, open PRs, ledger state, and the existing reserved M0-T063 through M0-T069 tasks.
2. Inspect the accepted implementation of:
   - tools/agent_supervisor/cli.py
   - tools/agent_supervisor/policy.py
   - tools/agent_supervisor/broker.py
   - tools/agent_supervisor/durable_state.py
   - related tests and schemas
3. Confirm or disprove these two suspected defects from source:
   A. TaskAuthority.from_packet supports documented_test_commands as an argument, but the production _run_loop construction does not supply packet commands.
   B. revoke-all revokes approval records, but status.open_asks reads unanswered queued_asks independently, causing revoked requests to remain displayed as open.
4. Inspect M0-T063.json and confirm whether it currently provides a validated command-authority field.
5. Reconcile the next valid ledger task ID. M0-T063 through M0-T069 are already allocated; do not guess or reuse an ID.
6. Determine the correct branch base and stacking relationship without mixing unrelated changes into an existing PR.

If either suspected defect is disproved, stop and report the exact evidence. Do not implement a speculative fix.

IF CONFIRMED: create one separate supervisor-corrective task, worktree, and branch following the repository’s existing control-plane process.

Authorized scope:

- Create the required incident evidence and bounded task packet.
- If directive compliance requires a new source, this entire prompt may be captured exactly once as the owner instruction. Do not treat a later word such as “continue” as authorization or as another directive.
- Implement the repair only in the new corrective worktree.
- Run the applicable tests and independent gates.
- Commit, push, and open a PR.
- Stop before merge or runtime activation and return the PR, commit SHA, gates, and activation instructions.

Required acceptance behavior:

AS-1. Define one canonical, closed, schema-validated task-packet field for documented baseline/test commands.

AS-2. Production _run_loop must load the validated commands and pass them into TaskAuthority.

AS-3. Command authorization must be deterministic and fail closed. Empty values, wrong types, shell chaining, substitution, redirection, unexpected metacharacters, and malformed commands must not gain AUTO authority.

AS-4. A command matching an explicitly documented and validated command shape may receive the existing documented-test AUTO classification.

AS-5. A changed executable, changed arguments, appended command, undocumented command, or command outside the task authority remains ASK or HARD_DENY under existing policy.

AS-6. Do not create a general Bash allowlist, broad executable grant, settings-file bypass, or automatic “always allow” behavior.

AS-7. Add a production-wiring regression test proving that packet commands reach the authority used by the real loop—not only a direct TaskAuthority unit test.

AS-8. Correct approval/status reconciliation so revoke-all cannot leave revoked requests represented as currently open actionable requests. Historical audit evidence must remain preserved.

AS-9. Add tests proving:
- pending request appears as pending/open;
- revoke-all revokes it;
- pending-approvals returns zero afterward;
- status no longer represents it as an actionable open request, or explicitly labels it revoked history;
- audit and journal integrity remain valid.

AS-10. Add a fixture representing the exact M0-T063 baseline/test-command need and prove the intended command is authorized while altered and injected variants are not.

AS-11. Run the full supervisor, directive-compliance, and project-control suites required by the verified task gate profile.

AS-12. Produce before/after evidence covering classification, checkpoint progression, and any token/runtime measurement available from a bounded fixture. Do not repeat the costly real A1 run as part of this repair.

Prohibitions:

1. Do not touch C:\Program Files\SupervisorConfig\config.toml.
2. Do not touch C:\SupervisorController\model_selection.toml.
3. Do not mutate or delete the existing A1 runtime SQLite database.
4. Do not modify the A1 worktree or start M0-T063.
5. Do not weaken fail-closed behavior or broaden general Bash authority.
6. Do not merge, activate, or replace C:\SupervisorController.
7. Do not use git reset, git clean, force push, or destructive cleanup.
8. Do not combine this repair with Units A1–F implementation.

Rollback must be the removal/reversion of only the corrective branch and worktree before merge. Existing A1 and runtime evidence must remain intact.

After implementation and gates, return:

SUPERVISOR_REPAIR_PR_READY

Include:
- reconciled task ID;
- branch and worktree;
- exact files changed;
- root cause confirmed;
- before/after test evidence;
- commit SHA and PR URL;
- gate results;
- remaining risks;
- exact owner-controlled merge and controller-update commands.

Do not restart A1.
