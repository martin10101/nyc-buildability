# D-004 — source-006 (owner amendment 5, verbatim)

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message. Amends `source-001.md`.
Frozen baseline unchanged: `origin/main` = `421265709f81a40e20f3d890609907ed932967dd`.
Head at capture time: `origin/main` = `e5d95b6c58d0d825feb52044d14892035edb9b47` (post PR #119),
reconciled live against GitHub before any write, matching the directive's own expected SHA.
Requirement IDs added by this amendment start at `D-004-R168`; no existing row is edited.
The trailing owner question ("ALSO COFRIM ...") arrived in the same owner message and is preserved
verbatim as part of this capture; it is answered as a return-packet item, not by writing any effort key.

---

OWNER DIRECTIVE — D-004 STEP 3: CORRECT AND EXECUTE M0-T028

Capture this instruction verbatim through `/directive-compliance` before any M0-T028 mutation. Treat it as the explicit owner GO for D-004 Step 3 only.

CURRENT VERIFIED ORIENTATION

A live GitHub check immediately before this directive found:

* `origin/main` advanced through merged PR #119.
* Expected main at this moment:
  `e5d95b6c58d0d825feb52044d14892035edb9b47`
* M0-T031 is accepted as task 49.
* Last checkpoint is CP-0033.
* M0-T028 remains `backlog`, `owner_review_state = PROPOSED`, and has not been claimed or dispatched.
* B-015 remains OPEN.
* M0-T027 remains BLOCKED.
* D-004 Steps 4 and 5 remain unauthorized.
* Graphify remains WAIT.
* Expansion planning, survey work, M0-T019, M0-T025, and all product lanes remain outside this directive.

Do not trust the expected SHA blindly. Reconcile live before acting.

OWNER DECISION

I approve M0-T028, subject to the mandatory packet corrections and staged execution below.

This authorization includes:

1. Append-only capture of this owner decision as the next D-004 amendment.
2. Correction of the M0-T028 task packet before G0 or claim.
3. Execution of D-004 Step 3/M0-T028 only.
4. Diagnosis of B-015 using primary evidence.
5. A prevention fix if the evidence proves the defect is repairable inside M0-T028’s authorized repository surfaces.
6. The already-contracted R100 path-quoting and R101 `.claude/settings.local.json` gitignore ride-alongs.
7. Independent review, protected-main implementation merge, and the required fresh-session end-to-end rerun.
8. Closure of B-015 and acceptance of M0-T028 only if every contracted requirement passes.

This authorization does NOT include:

* D-004 Step 4 or Step 5;
* M0-T029;
* general adoption of Agent Teams;
* producer waves or automatic Agent Teams injection;
* any detection-only substitute if prevention is unavailable;
* M0-T025;
* M0-T019 or PR #64;
* second-wave product tasks;
* Master Expansion Architecture or the six PRDs;
* Mission Control Engineering Map;
* project/control graph;
* NYC Evidence Knowledge Graph;
* Graphify installation or reevaluation;
* product code under M2–M7;
* survey work;
* deployment or hold release;
* any effort setting or effort key.

PHASE 0 — LIVE ORIENTATION AND RECONCILIATION

Before writing:

1. Run:

   `git fetch --all --prune`

   `python tools/project_control.py status`

   `python tools/current_state.py`

2. Reconcile:

   * local main;
   * `origin/main`;
   * open PRs;
   * worktrees;
   * task lifecycle;
   * blockers;
   * current checkpoint;
   * CI;
   * D-004 directive state.

3. Read at minimum:

   * `CLAUDE.md`
   * `docs/SESSION_HANDOFF.md`
   * `.claude/ORCHESTRATION_POLICY.md`
   * `.claude/rules/project-control.md`
   * `project-control/state.json`
   * `project-control/master_plan.json`
   * `project-control/tasks/M0-T027.json`
   * `project-control/tasks/M0-T028.json`
   * `project-control/blockers/B-015-teammate-readonly-guard-bypass.json`
   * D-004 manifest, requirements, verification, and all amendments—especially `source-005-amendment.md`
   * `.claude/hooks/readonly_agent_guard.py`
   * `.claude/settings.json`
   * `.gitignore`
   * `tools/test_readonly_agent_guard.py`
   * the relevant dependency/acceptance enforcement in `tools/project_control.py`

4. Confirm that PR #119 is merged and that main includes it. Do not recreate or refresh the handoff again.

5. Confirm the tracked `.claude/settings.json` contains no permission-prompt-generated `allow` rules, machine-specific absolute paths, effort keys, or unrelated local configuration.

6. Permission-prompt rules belong only in untracked local settings. Never stage them.

7. Use the code graph selectively. Because this task already names its principal files, universal graph-first navigation is inappropriate. Query it only for a concrete dependency or impact question, and verify every useful result in authoritative source.

If main has advanced beyond `e5d95b6`, determine exactly why. Continue only if the advancement is clean, reconciled, and unrelated. Otherwise STOP and report.

PHASE 1 — CORRECT THE M0-T028 PACKET BEFORE DISPATCH

The currently committed M0-T028 packet has a lifecycle deadlock:

* M0-T028 lists M0-T027 as a dependency.
* M0-T027 is blocked until M0-T028 fixes B-015.
* `tools/project_control.py accept` requires every listed dependency to be accepted.
* Therefore M0-T028 cannot ever be accepted as currently written.

Correct this before G0:

1. Remove M0-T027 from M0-T028’s formal `dependencies` array.

2. Preserve M0-T027 as:

   * the source of the pilot evidence;
   * a causal/predecessor relationship in inputs and requirement references;
   * the task affected by B-015;
   * not an acceptance prerequisite.

3. Do not silently replace it with another dependency merely to fill the array. Add an accepted predecessor only if the authoritative project-control model genuinely requires one and primary evidence supports it. Otherwise use an empty dependency list.

4. Explain the correction in the append-only D-004 amendment and in the control-plane PR.

5. Update `owner_review_state` to reflect this explicit owner approval only after the corrected packet matches this directive.

6. Assign the producer only after inspecting the existing agent definitions. Use one qualified producer distinct from every independent reviewer.

7. Do not invent an agent role. Use an existing suitable role.

SENTINEL ACCEPTANCE CLARIFICATION

Resolve another ambiguity in the existing records through the new amendment:

* The direct Write/Edit-tool attempt may remain blocked by tool unavailability because reviewer definitions intentionally do not expose those tools.
* Do not falsely claim that `readonly_agent_guard.py` denied a tool call that the teammate could not invoke.
* The Bash-redirection attempt is the load-bearing PreToolUse test.
* The Bash command must be denied by `readonly_agent_guard.py` itself, with its denial evidence captured.
* The orchestrator must independently run `test -e` for the sentinel and record a non-zero/ABSENT result.
* Tool unavailability for direct Write plus guard denial for Bash plus independent absence verification is the required honest result.

Do not rewrite the original pilot evidence. Its historical FAIL/FAIL/PASS results and sentinel escape remain byte-preserved.

PHASE 2 — CAPTURE AND INTEGRATE THE OWNER DECISION

Create the next append-only D-004 amendment through the normal directive-compliance workflow.

The amendment must record at least:

* explicit owner GO for D-004 Step 3/M0-T028 only;
* the M0-T027/M0-T028 dependency-deadlock correction;
* the sentinel acceptance clarification above;
* the two-session execution boundary;
* no detection-only fallback without a new owner decision;
* no Steps 4 or 5;
* no Agent Teams adoption;
* no effort key anywhere;
* every teammate spawn must carry the explicit model required by D-004;
* Fable 5 for gate-class reviewer teammates;
* Opus 4.8 for producer teammates if a producer teammate is used;
* no machine-specific settings or permission rules in tracked configuration;
* all unrelated holds remain standing.

Append new requirement rows from the next free D-004 requirement ID. Do not edit prior source files or prior requirement rows.

Recompute and validate all directive digests and registry data.

Correct D-004 `affected_tasks` using the canonical directive-compliance process so it honestly identifies M0-T027 and M0-T028 as applicable. Do not create competing manual truth.

Put the directive amendment and corrected pre-dispatch M0-T028 packet through a narrow control-plane PR. Require:

* protected-main workflow;
* directive registry validation;
* project-control validation;
* secret scan;
* exact diff review;
* no product/runtime files;
* no M0-T025 change;
* no effort key;
* no unrelated handoff rewrite.

Merge that control PR only when every required check is green. Then fetch and freeze the new main SHA for implementation.

PHASE 3 — G0 AND ISOLATED IMPLEMENTATION

After the corrected control packet is merged:

1. Run fresh G0 against the corrected packet and newly frozen main SHA.

2. Create a fresh, specifically named M0-T028 worktree and branch from that frozen main.

3. Do not reuse any D-004 pilot branch, prior team, prior task list, or old worktree.

4. Claim M0-T028 through the project-control CLI.

5. Use a single-writer implementation model.

6. Do not use an Agent Teams writing producer while B-015 is still open.

7. A tightly bounded no-Write/Edit diagnostic teammate may be used only when necessary to observe the actual teammate PreToolUse behavior. Every such spawn must use the explicit model required by D-004.

8. Before and after every live teammate probe, run and record a dirt sweep across:

   * primary checkout;
   * M0-T028 worktree;
   * any disposable probe worktree.

9. Any unexpected file outside the deliberately named sentinel path is a STOP condition.

PHASE 4 — PRIMARY-EVIDENCE DIAGNOSIS

Do not begin by guessing a fix.

Capture primary evidence sufficient to distinguish:

* H1: PreToolUse does not invoke this hook for Agent Teams teammates.
* H2: PreToolUse invokes the hook, but the teammate payload lacks the recognized `agent_type`/`agentType` identity or uses a different identity shape.

The evidence must show the actual live teammate payload or an equally primary runtime artifact. A synthetic payload alone is insufficient.

Store only sanitized evidence:

* no usernames;
* no absolute machine paths;
* no session IDs;
* no pane IDs;
* no credentials;
* no private environment values.

The diagnosis report must explicitly reconcile:

* direct Write/Edit tool unavailability worked;
* Bash redirection escaped;
* the hook logic worked on a synthetic known payload;
* Step 2 proved teammate Bash starts in the primary checkout before each call;
* therefore worktree-location assumptions cannot provide confinement.

BRANCHING RULE

If H2 is proven:

* Implement the narrowest identity-resolution/wiring correction inside the already allowed M0-T028 paths.
* Preserve fail-closed behavior for malformed or unparseable payloads.
* Do not weaken any current denial.
* Do not newly block legitimate read-only git commands, GitHub reads, or test commands.

If H1 is proven and PreToolUse prevention cannot be made to fire from within M0-T028’s authorized paths:

* STOP before implementing a detection-only substitute.
* Do not reinterpret the packet.
* Do not close B-015.
* Do not claim M0-T028 is fixed.
* Return a focused owner decision packet describing:

  * primary evidence;
  * why prevention is unavailable;
  * the narrowest detection-only design;
  * residual risk;
  * exact additional paths/authority required;
  * whether Agent Teams adoption should remain rejected.

Detection-only requires a separate owner GO.

PHASE 5 — REQUIRED IMPLEMENTATION AND TESTING

If the fixable H2 path is proven, complete only the contracted work:

1. Guard correction.

2. New regression coverage for the actual teammate payload shape.

3. Existing malformed/unparseable-payload fail-closed test remains passing.

4. Prove no previously denied mutating command becomes allowed.

5. Prove legitimate read-only commands remain allowed.

6. Quote all project-path references in every applicable hook command in `.claude/settings.json`.

7. Prove hook commands resolve when the repository path contains a space.

8. Add `.claude/settings.local.json` to the repository `.gitignore`.

9. Prove with `git check-ignore -v` that the repository `.gitignore`, not merely a machine-global ignore, supplies the match.

10. Correct directive index affected-task data in its proper control-plane layer if not already handled during amendment capture.

11. Run:

* complete read-only-guard test suite;
* project-control tests;
* directive-compliance tests;
* directive validator;
* secret scan;
* full relevant CI;
* containment diff;
* deterministic checks required by the task.

12. Do not touch:

* M0-T025;
* product code;
* prior pilot reports;
* prior D-004 source files;
* unrelated settings;
* CLAUDE.md;
* agent definitions;
* rules;
* deployment files;
* any effort setting.

PHASE 6 — INDEPENDENT REVIEW AND IMPLEMENTATION MERGE

Freeze one exact implementation SHA.

Run all contracted independent reviews against that exact SHA:

* G3 code review;
* G5 security review;
* control-plane verification;
* directive-compliance verification;
* any required G2 self-check through the proper orchestrator-controlled route.

Reviewers must be different from the producer.

Require reviewers to inspect:

* actual H1/H2 evidence;
* identity-resolution logic;
* command-denial regressions;
* read-only-command non-regressions;
* settings path quoting;
* repository gitignore behavior;
* no machine-specific tracked configuration;
* no effort key;
* exact allowed-path containment;
* M0-T025 unchanged;
* historical pilot reports unchanged;
* no product/runtime changes.

Apply no review correction outside the contracted paths.

If a correction changes the reviewed SHA, perform the required bounded delta review before merge.

Merge the implementation through a protected-main PR only when every pre-merge requirement is green.

Do NOT yet:

* close B-015;
* accept M0-T028;
* claim the live teammate sentinel passed;
* create a final checkpoint;
* begin D-004 Step 4;
* adopt Agent Teams.

The merged hook/settings change must be tested in a completely fresh Claude Code session.

PHASE 7 — MANDATORY FRESH-SESSION STOP

After the implementation PR merges:

1. Reconcile main and record the exact merge SHA.

2. Confirm all working trees are clean.

3. Prepare a complete fresh-session resume capsule containing:

   * merged main SHA;
   * M0-T028 task status;
   * implementation PR;
   * reviewed SHA;
   * every gate already completed;
   * exact remaining fresh-session sentinel procedure;
   * exact model requirements;
   * exact forbidden actions;
   * B-015 still OPEN;
   * M0-T027 still BLOCKED;
   * no Step 4/5 authorization.

4. STOP.

5. Tell the owner explicitly that Claude Code must be restarted in a completely fresh session because D-004 forbids testing merged hook/settings behavior in the session that predates the merge.

Do not attempt to simulate freshness inside the existing conversation.

PHASE 8 — FRESH-SESSION END-TO-END VALIDATION

This phase is authorized only after the owner starts the required fresh Claude Code session using the resume capsule.

In that fresh session:

1. Fetch and reconcile the merged implementation SHA.

2. Freeze the then-current accepted main head.

3. Re-run the on-policy reviewer sentinel with the same three reviewer roles required by D-004.

4. Pass an explicit Fable 5 model on every gate-class reviewer teammate spawn.

5. Direct Write/Edit attempt:

   * must remain unavailable/denied;
   * report it honestly as tool-unavailability if that is the enforcement layer.

6. Bash redirection attempt:

   * must be denied by `readonly_agent_guard.py` itself;
   * capture the guard’s denial evidence.

7. The orchestrator independently runs `test -e` against the exact sentinel and records non-zero/ABSENT.

8. Run full dirt sweeps after the test.

9. Confirm no unexpected artifact exists in main or any worktree.

10. Re-run the relevant regression and directive checks.

Only if all of that passes:

* append the required audit evidence to M0-T028’s permitted report surface;
* resolve B-015 through the orchestrator with an audit-log entry citing the merged fix and passing fresh-session sentinel;
* complete remaining independent directive verification;
* accept M0-T028 through the project-control CLI;
* use the next checkpoint only if the established checkpoint policy actually requires one—do not assume or pre-reserve CP-0034;
* clean only the branches/worktrees created by this task.

Do not accept M0-T027 or start its Step 4 merely because the rerun passed. Any M0-T027 lifecycle transition beyond removing the B-015 condition requires reconciliation with its still-unproduced Step-4 evidence and a separate owner authorization.

FINAL RETURN PACKET

Return a concise but complete packet containing:

1. Final main SHA.
2. PR numbers and merge SHAs.
3. Corrected M0-T028 dependency state.
4. D-004 amendment and requirement-row range.
5. Frozen implementation SHA.
6. H1 or H2 result with primary-evidence location.
7. Exact fix.
8. Exact changed-file inventory.
9. Test and CI results.
10. Independent reviewer verdicts.
11. Fresh-session sentinel result.
12. B-015 status and audit entry.
13. M0-T028 lifecycle state.
14. M0-T027 lifecycle state.
15. Current accepted-task count/checkpoint.
16. Confirmation that every unrelated hold remains unchanged.
17. Confirmation of:

    * no M0-T025 change;
    * no effort key;
    * no machine-specific tracked allow rules;
    * no product change;
    * no Agent Teams adoption;
    * no Step 4/5;
    * no Graphify;
    * no expansion work.

STOP CONDITIONS

Stop and report rather than improvise if:

* current main cannot be reconciled;
* the dependency-deadlock correction conflicts with an authoritative rule;
* required changes escape M0-T028’s authorized paths;
* H1 is proven and prevention cannot be implemented;
* a detection-only design would be necessary;
* actual teammate payload evidence cannot be captured safely;
* any permission prompt writes tracked allow rules;
* any effort key appears;
* an expected reviewer model cannot be explicitly selected;
* a sentinel or unexpected file appears outside the bounded test;
* any test, CI check, security review, or directive verification is non-green;
* any prior D-004 source/pilot evidence would need rewriting;
* M0-T025 or product code would need modification;
* freshness would have to be simulated without a truly new session.

Do not begin unrelated work after the return packet.
ALSO COFRIM IF LOWER END WORKERS ARE USING OPUS 4.8 HIGH
