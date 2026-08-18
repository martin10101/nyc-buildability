OVERNIGHT OWNER AUTHORIZATION — COMPLETE CONTEXT-INTELLIGENCE INTEGRATION RUNWAY

You are operating in a fresh Claude Code session. Work continuously through every authorized stage below while the owner is unavailable.

Do not rely on previous conversational memory. Reconstruct all facts from Git, GitHub, task packets, directives, gate records, reports, CI, and durable supervisor state.

This prompt is explicit authorization for the precisely bounded repository operations below. If directive compliance requires capturing it, it may be captured exactly once, verbatim, as one owner instruction. Do not create additional captures from inferred decisions, status messages, tool output, or later casual words such as “continue.”

Use one writer only. You may use sub-agents in parallel for bounded read-only work such as:

- Git/GitHub state verification
- Directive and registry review
- Security review
- QA/test review
- CI monitoring
- Diff inspection

Sub-agents must not make overlapping repository changes. The primary orchestrator remains the sole writer and is responsible for reconciling all results from primary evidence.

KNOWN STARTING STATE

PR #223 / M0-T071:

- PR #223 is MERGED.
- Merge commit: f21eb1fbca3e16d1602a14775c99bb3cac75eb1e.
- origin/main equals f21eb1fbca3e16d1602a14775c99bb3cac75eb1e.
- M0-T071 is accepted.
- D-015 is independently verified.
- nanoid is patched from 3.3.17 to 3.3.18.
- Dependency-security, release-age, registry-integrity, audit, web, E2E, and control-plane checks passed.
- No waiver was used.

Control branch:

- Branch: control/context-intelligence-init.
- Worktree:
  C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\session15-acc
- Expected initial SHA:
  de2f224a7db16405edfc0e2f2f0902f5164819a0
- Contains D-013 and the context-intelligence task runway M0-T063 through M0-T069.
- Does not yet contain the merged M0-T071/D-015 records from main.

PR #222 / M0-T070:

- PR #222 is OPEN.
- Base: control/context-intelligence-init.
- Branch: task/M0-T070-supervisor-authority-repair.
- Worktree:
  C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t070
- Expected initial head:
  09e23162b364034f3e3a771291664cb40bfc5705
- M0-T070 is awaiting_gate at 95%, not accepted.
- It repairs:
  1. production loading of packet-documented baseline/test commands;
  2. revoked approval requests being misleadingly displayed as open.
- D-014 requires final independent verification and acceptance.
- B-019 was created on this branch for the Nano ID vulnerability. The underlying vulnerability has now been fixed by merged PR #223.

A1:

- Task: M0-T063.
- Worktree:
  C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063
- Branch: task/M0-T063-context-index-a1.
- Expected initial SHA:
  de2f224a7db16405edfc0e2f2f0902f5164819a0
- Expected clean.
- Durable supervisor state was PREFLIGHT.
- A1 has not been implemented.
- Do not implement or start A1 during the repository-integration stages.

Live controller:

- Location: C:\SupervisorController
- Currently contains the accepted PR #221 controller, not the PR #222 repair.
- Protected config:
  C:\Program Files\SupervisorConfig\config.toml
- Do not modify, replace, activate, or relax the live controller or protected configuration while the owner is unavailable.

GENERAL OPERATING RULES

1. Work stage by stage in the stated order.
2. Never begin a dependent stage until the preceding stage is committed, pushed, verified, and clean.
3. At every stage, compare local HEAD, remote HEAD, PR HEAD, reviewed identity, and tested identity.
4. Never report success before authoritative GitHub CI finishes.
5. If context becomes large, write a durable bounded checkpoint report, finish the current atomic action, leave all worktrees clean and pushed, and return a precise resumption command. Do not improvise across context loss.
6. Preserve all existing user changes.
7. Never use:
   - git reset;
   - git clean;
   - rebase;
   - force push;
   - destructive checkout;
   - history rewriting;
   - broad file deletion;
   - security suppression;
   - test bypass;
   - advisory waiver.
8. A permission-classifier denial is a stop condition for that action. Do not work around it.
9. If one stage becomes blocked, do not continue into dependent stages. Perform safe read-only diagnosis and complete any genuinely independent read-only work.
10. Do not manufacture PASS evidence or accept producer assertions as independent verification.

STAGE 0 — COMPLETE READ-ONLY RECONCILIATION

Before any mutation:

1. Fetch all remotes.
2. Verify:
   - origin/main;
   - control/context-intelligence-init;
   - task/M0-T070-supervisor-authority-repair;
   - task/M0-T063-context-index-a1.
3. Verify all three relevant worktrees are clean.
4. Verify PR #223 is merged at f21eb1f.
5. Verify PR #222 remains open and obtain its live base, head, mergeability, checks, and changed files.
6. Inspect:
   - D-013;
   - D-014;
   - D-015;
   - M0-T063 through M0-T071;
   - B-019;
   - project-control/state.json;
   - project-control/directives/index.json;
   - the final M0-T070 and M0-T071 reports.
7. Verify A1 files, branch, worktree, and runtime have not changed.
8. Verify C:\SupervisorController and protected configuration read-only. Do not change them.
9. Produce a reconciliation matrix showing:
   - live fact;
   - expected fact;
   - PASS/STOP;
   - source of evidence.
10. Stop immediately if a material identity or worktree condition differs unexpectedly.

STAGE 1 — SYNCHRONIZE SECURED MAIN INTO THE CONTROL BRANCH

In session15-acc:

1. Merge origin/main at f21eb1f into control/context-intelligence-init using a normal non-destructive merge.
2. Do not rebase or rewrite either history.
3. Resolve conflicts semantically as a union.

Required semantic outcome:

- Preserve D-013 and M0-T063 through M0-T069.
- Preserve accepted D-015 and M0-T071 from main.
- Preserve every earlier directive and task.
- directives/index.json must contain every valid directive D-001 through D-015 exactly once.
- project-control/state.json must contain the union of valid tasks and an accepted count of 86 before M0-T070 acceptance.
- D-015 verification and final reviewed identity must remain accepted and unchanged.
- Do not silently select “ours” or “theirs” for registry or state files.
- Explain every resolved conflict and the semantic result.

Run all required checks, including:

- python tools/validate_directive_compliance.py --check
- python tools/test_directive_compliance.py
- python tools/test_project_control.py
- registry/state consistency checks
- any applicable product-map or control-plane validators

Then:

1. Confirm the worktree is clean except for the intended merge result.
2. Commit the integration merge.
3. Push control/context-intelligence-init.
4. Verify local HEAD equals origin/control/context-intelligence-init.
5. Re-run the critical validators on the pushed commit.
6. Record the synchronized control-branch SHA.

STAGE 2 — RECONCILE PR #222 WITH ITS UPDATED BASE

In wt-m0t070:

1. Fetch the newly synchronized control branch.
2. Merge origin/control/context-intelligence-init into task/M0-T070-supervisor-authority-repair using a normal merge.
3. Resolve conflicts as the union of D-013, D-014, and D-015.
4. Preserve the accepted M0-T071 records from main.
5. Do not alter the Nano ID implementation.
6. Do not modify apps/web/package.json or package-lock.json.
7. Verify the M0-T070 supervisor implementation files remain byte-identical to the independently gated material identity unless a genuine base-integration change requires review.
8. If implementation material changes for any reason, invalidate stale gates and obtain fresh independent review. Never rely on an old gate after a material change.

Resolve B-019 only after reproducing all these facts:

- PR #223 is merged.
- origin/main contains nanoid 3.3.18.
- npm audit reports zero vulnerabilities.
- the repository age gate passes without waiver.
- dependency-security is green.
- the package integrity matches the accepted lock.
- PR #222 does not introduce or modify the dependency.

Update B-019 to resolved with direct evidence. Do not delete its history.

Run:

- M0-T070 command-authority tests
- full supervisor test suite
- project-control tests
- directive-compliance tests
- validate_directive_compliance.py --check
- appropriate security and registry checks

Then:

1. Commit the base reconciliation and B-019 resolution.
2. Push the PR #222 branch.
3. Verify local branch equals remote.
4. Wait for all PR #222 GitHub workflows.
5. Do not proceed unless every required workflow is completed successfully.

STAGE 3 — FINAL M0-T070 GATES, DIRECTIVE VERIFICATION, AND ACCEPTANCE

After PR #222 is fully green:

1. Establish the final canonical material identity.
2. Confirm G0/G2/G3/G5 apply to that exact material.
3. If the identity differs materially, rerun the affected gates using fresh independent reviewers.
4. Run a fresh directive-compliance-verifier.
5. The verifier must be independent from the producer.
6. Resolve the complete applicable D-014 requirement set:
   - M0-T070-bound requirements;
   - D-014-BOOTSTRAP sentinel requirements;
   - reconciliation amendment requirements.
7. Use primary evidence for every PASS.
8. Mark genuine failures or unverifiable requirements honestly.
9. Run the acceptance precondition resolver.
10. Require zero blocking reasons and zero improper deferrals.
11. Accept M0-T070 through the repository-prescribed command only if every condition genuinely passes.

Required post-acceptance state:

- M0-T070 status = accepted.
- M0-T070 progress = 100%.
- Accepted ledger count = 87 exactly.
- D-014 verification is complete.
- D-014 final reviewed identity is recorded.
- B-019 is resolved.
- No duplicate task or acceptance record exists.
- Directive registry validation passes.
- A1 remains untouched.

Commit and push the acceptance records. Then wait for every GitHub workflow on the final acceptance HEAD. Require all green.

STAGE 4 — MERGE PR #222 INTO THE CONTROL BRANCH

The owner explicitly authorizes merging PR #222 only if all the following are simultaneously true:

- PR #222 is open and mergeable.
- M0-T070 is accepted.
- Accepted count is 87.
- D-014 verification is complete.
- B-019 is resolved.
- Reviewed material equals final material under the repository’s canonical identity rule.
- Every required GitHub check on the final HEAD is successful.
- No unresolved discussion, blocker, permission issue, or security finding remains.
- PR base equals the synchronized control branch.
- No protected config, controller-runtime, A1, or unrelated application files appear in the PR diff.

If all conditions pass:

1. Merge PR #222 using the repository’s normal merge strategy.
2. Do not enable auto-merge.
3. Fetch the remote.
4. Verify PR #222 state = MERGED.
5. Record its merge commit.
6. Verify origin/control/context-intelligence-init equals the expected merge result.
7. Run the critical control-plane validators on the merged control branch.

If GitHub or the permission classifier denies the merge, do not bypass it. Preserve the fully ready state and return the exact owner command.

STAGE 5 — INTEGRATE THE COMPLETED CONTROL BRANCH INTO MAIN

After PR #222 is merged into the control branch:

1. Determine whether an existing control-branch-to-main PR exists.
2. If none exists, open one using the repository’s established integration format.
3. Confirm the diff contains:
   - D-013 context-intelligence bootstrap;
   - M0-T063 through M0-T069 task runway;
   - accepted M0-T070 supervisor repair;
   - no duplicate D-015/M0-T071 changes already present on main;
   - no unintended application changes.
4. Resolve registry/state comparisons as the union of D-001 through D-015.
5. Run the full required CI and independent integration checks.
6. Require every GitHub check to finish successfully.
7. Verify accepted count remains 87.
8. Verify main’s accepted M0-T071 records are not duplicated or regressed.
9. Verify the control branch does not undo nanoid 3.3.18.

The owner explicitly authorizes merging this control integration PR into main only if:

- all checks are green;
- it is mergeable and current with main;
- accepted task and directive identities are valid;
- no security or scope blocker remains;
- the diff is exactly the intended control/context/supervisor integration;
- no protected local controller action is bundled into it.

If authorized conditions pass:

1. Merge with the normal merge strategy.
2. Fetch origin.
3. Verify the PR is MERGED.
4. Verify origin/main equals the new integration merge.
5. Run post-merge validation read-only.
6. Record the resulting main SHA.

If permission is denied, do not bypass it; return the exact owner command.

STAGE 6 — PREPARE THE M0-T063 COMMAND-AUTHORITY PACKET

Only after the supervisor repair and D-013 runway are present on origin/main:

1. Inspect the accepted M0-T070 schema and exact M0-T063 fixture.
2. Inspect M0-T063’s baseline and test obligations.
3. Determine every exact baseline/test command A1 genuinely requires.
4. Do not guess commands.
5. Do not use wildcards, shell chaining, substitution, redirection, broad executable patterns, or a general Bash grant.
6. Use the canonical documented_test_commands field.
7. Include only exact, validated command shapes required by M0-T063.
8. Ensure malformed or altered variants remain ASK/HARD_DENY.
9. Follow the existing task-amendment/reverification process.
10. Re-run M0-T063 G0 or other packet gates if the control plane requires them after packet amendment.
11. Do not implement A1.
12. Do not start the supervisor.

Create a dedicated, minimal branch/worktree if required by repository policy. Do not mix this packet amendment into an already merged branch.

Run:

- schema validation
- production authority-loading tests
- exact command-classification tests
- directive compliance
- project-control validation
- required CI

If the task-packet amendment becomes fully verified and its PR is green, the owner authorizes merging that narrowly scoped packet amendment into main using the normal strategy. If any ambiguity exists over command authority, stop instead of broadening it.

After merge, synchronize the existing A1 task branch/worktree with the accepted main state using only a normal non-destructive merge. Do not implement or run A1.

Required result:

- M0-T063 task packet contains the exact accepted documented commands.
- A1 worktree is clean.
- A1 branch includes the accepted controller contract and task packet.
- A1 remains unstarted.
- Supervisor runtime database remains intact.

STAGE 7 — PREPARE, BUT DO NOT EXECUTE, THE LIVE CONTROLLER UPDATE

Perform read-only inspection of:

- accepted origin/main supervisor tree;
- C:\SupervisorController;
- C:\Program Files\SupervisorConfig\config.toml;
- controller manifest;
- model_selection.toml;
- ACL posture;
- current runtime status;
- A1 durable state.

Produce a precise controller-update package and owner runbook containing:

1. Current controller SHA/version.
2. New accepted supervisor SHA/version.
3. Exact files added, changed, or removed.
4. Backup destination and rollback procedure.
5. Manifest regeneration and verification commands.
6. Protected-config hash verification.
7. ACL verification.
8. Model-selection verification.
9. Stop/update/start sequence.
10. Post-update doctor command.
11. Live control-response verification.
12. A1 status/recovery verification.
13. Exact supervised A1 start command.
14. Expected owner approval touchpoints.
15. Exact rollback triggers.

Do not:

- copy files into C:\SupervisorController;
- change protected config;
- change model selection;
- regenerate the live manifest;
- stop or restart the live controller;
- clear or delete runtime state;
- start A1.

Those actions require the owner to be awake and present.

FINAL RETURN

Continue until:

A. all authorized repository integration work is complete; or
B. a real stop condition prevents safe progress.

Return one of:

OVERNIGHT_RUNWAY_COMPLETE

Include:

- PR #222 final state and merge commit;
- control integration PR and merge commit;
- final origin/main SHA;
- accepted task count;
- D-013/D-014/D-015 registry status;
- B-019 status;
- M0-T063 packet-amendment PR/merge status;
- A1 branch/worktree SHA and cleanliness;
- every test and CI result;
- exact controller-update runbook;
- exact A1 start command;
- remaining owner actions, in order.

Or:

OVERNIGHT_RUNWAY_BLOCKED

Include:

- completed stages;
- exact blocked stage;
- exact evidence and reason;
- all local/remote SHAs;
- worktree cleanliness;
- actions not taken;
- safest next command for the owner.

Do not claim completion while CI is running.
Do not merge anything unless every explicit condition above is satisfied.
Do not modify the live controller.
Do not start A1.
