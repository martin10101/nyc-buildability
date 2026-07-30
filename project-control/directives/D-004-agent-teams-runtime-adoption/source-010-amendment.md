# D-004 — source-010 (owner amendment 9, verbatim)

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message. Amends `source-001.md`.
Frozen baseline unchanged: `421265709f81a40e20f3d890609907ed932967dd`.
Head at capture time: `origin/main` = local `main` = `1f3fbf18d5e0cfbacb2d8b9da9309a0c03ab8a9b`
(post PR #130), reconciled live against GitHub before any write; ledger verified at 52 accepted,
CP-0035, M0-T027 blocked at 75%, M0-T032 backlog, no `M0-T029.json` and no `M0-T033.json` present
— matching the owner's stated expected state in every particular.

Requirement IDs added by this amendment start at `D-004-R327`; no existing source file or
requirement row is edited. This amendment resolves the owner decision left open by the M0-T027
closeout stop (progress log entry at 75%, `invalid_unblock_roster`): the owner rejects options (a)
and (c) and authorizes option (b). The temporary Opus 5 availability exception (D-004-R307–R312)
remains active and unchanged.

---

Resume NYC Buildability as orchestrator. Reconcile live first, then read the M0-T027 progress log and D-004 amendment 8 (rows R307–R326). M0-T027 is blocked at the unblock-roster guard awaiting my decision; do not start any other work.  OWNER DECISION — OPTION B: NARROW CONTROL-PLANE GUARD FIX, THEN COMPLETE M0-T027

Capture this message verbatim through directive compliance before acting.

I reject option A. Do not assign a false producer to M0-T027.

I reject option C. Do not abandon or administratively route around M0-T027 while its evidence is complete and its remaining blocker is an over-broad lifecycle guard.

I authorize option B: a narrow, independently reviewed correction to invalid_unblock_roster, followed by completion of M0-T027 if every required gate passes.

PHASE 0 — LIVE RECONCILIATION

Expected state, subject to live verification:

- main = origin/main = 1f3fbf18d5e0cfbacb2d8b9da9309a0c03ab8a9b
- PRs #129 and #130 merged
- M0-T027 blocked at 75%
- 52 accepted tasks
- CP-0035
- M0-T032 backlog
- Step 5/M0-T029 unauthorized

If live state differs materially, stop and report before writing.

The temporary Opus-5 availability exception in amendment 8 remains active. Use explicit Opus 5 for every producer, independent reviewer, and verifier, and disclose the actual model honestly.

PHASE 1 — CONTRACT THE GUARD FIX

If M0-T033 remains unused, contract:

M0-T033 — Governance-orchestrator unblock-roster semantics

Use a real existing non-orchestrator producer qualified to modify Python control-plane tooling. Use backend-engineer if live roster inspection confirms it is qualified and distinct from every reviewer.

Required independent reviewers:

- code-reviewer
- security-reviewer
- control-plane-verifier
- directive-compliance-verifier

Required gates:

- G0
- G2
- G3
- G5

The task must cite the applicable governance directives through the canonical resolver.

Authorized implementation paths:

- tools/project_control.py
- tools/test_project_control.py
- docs/GATES_AND_CHECKPOINTS.md only if its invariant must be corrected
- M0-T033's own packet and reports

No other tools, hooks, settings, agent definitions, product files, deployment files, or unrelated control-plane behavior may change.

PHASE 2 — REQUIRED GUARD SEMANTICS

Correct invalid_unblock_roster generally. Do not hard-code M0-T027 and do not add a bypass flag.

Preserve the existing default:

- missing producer remains invalid;
- an ordinary research, engineering, integration, product, or other non-governance task with producer_agent=orchestrator remains invalid;
- empty reviewer roster remains invalid;
- a roster containing only orchestrator remains invalid;
- a roster containing only the producer remains invalid;
- malformed roster data fails closed;
- blocked-to-canceled remains permitted;
- independent-gate enforcement remains unchanged.

Add one narrow valid case:

A blocked task may leave blocked status with producer_agent=orchestrator only when all of the following are true:

1. task_type is exactly governance;
2. the task has at least one required independent gate from G1/G3/G4/G5/G6;
3. reviewer_agents contains at least one usable independent reviewer that is non-empty, not orchestrator, and not the producer;
4. the task remains subject to all existing directive-regime, evidence, gate, submit, verification, and acceptance controls.

The purpose is to recognize the main-session orchestrator as the truthful producer of orchestrator-produced governance evidence when independent review remains structurally possible.

This must not weaken gate(), submit(), accept(), directive verification, evidence identity, or producer-versus-reviewer separation.

MANDATORY REGRESSION TESTS

At minimum prove:

1. Existing non-governance orchestrator-producer rejection remains green.
2. Governance + orchestrator producer + required independent gate + usable reviewer can unblock.
3. Governance + orchestrator producer + no reviewers fails.
4. Governance + orchestrator producer + reviewer only "orchestrator" fails.
5. Governance + orchestrator producer + no independent required gate fails.
6. Malformed reviewer data fails closed without traceback.
7. Normal non-orchestrator producer behavior remains unchanged.
8. Blocked-to-canceled behavior remains unchanged.
9. Independent reviewer cannot equal the producer.
10. Full project-control and directive-compliance suites remain green.

Run M0-T033 through its complete controlled lifecycle. Merge and accept it only after every required independent gate passes at one frozen identity.

Do not touch M0-T027 during the M0-T033 implementation.

PHASE 3 — TRUTH-PRESERVING M0-T027 PACKET CLARIFICATIONS

Only after M0-T033 is merged, accepted, and verified live, return to M0-T027.

I authorize two narrow truth-preserving acceptance-scenario clarifications before its final review:

1. AS-1 must no longer demand the obsolete literal total of 128 locked directive requirements. Preserve 128 as the contract-time baseline, but require the current append-only total, matching digests, and a green validator. Do not rewrite directive history.

2. AS-6 must preserve the historical Step-1 sentinel failure exactly as recorded. It may be satisfied only across the owner-sequenced remediation arc by citing the later M0-T028 fresh-session Phase-8 proof of guard denial and independently verified sentinel absence. Do not claim that the original Step-1 sentinel passed.

Make no other material packet changes.

PHASE 4 — COMPLETE M0-T027

After the guard fix and packet clarifications:

1. Unblock M0-T027 through the normal CLI.
2. Freeze the final closeout identity.
3. Regenerate its evidence map through the canonical resolver; do not manually preserve the old count.
4. Dispatch all required independent reviewers using explicit Opus 5 under amendment 8.
5. Preserve every reviewer return verbatim.
6. Run final independent directive verification.
7. Stop on any blocking or ambiguous result.
8. If every gate passes, submit, merge through protected main, verify the merged identity, accept M0-T027 through the CLI, and checkpoint only if policy requires it.
9. Clean only branches/worktrees created for these two authorized tasks.

STILL NOT AUTHORIZED

- Step 5 or M0-T029
- M0-T032
- another product/producer wave
- teammateDefaultModel changes
- effort settings
- legal-rule or predicate-schema follow-ups
- deployment, G6, Graphify, expansion, survey work, or hold releases
- M0-T025
- unrelated handoff or documentation work

STOP after M0-T027 is either accepted or blocked by a new substantive finding.

Return:

- final main SHA;
- PRs for M0-T033 and M0-T027;
- both task statuses;
- accepted-task count and checkpoint;
- exact guard semantics changed;
- complete test and gate results;
- directive-verification results;
- changed-file lists;
- confirmation that Step 5 and M0-T032 did not begin;
- refreshed proposed Step-5 packet, proposal only.
