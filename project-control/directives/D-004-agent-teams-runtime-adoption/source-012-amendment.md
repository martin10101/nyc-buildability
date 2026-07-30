# D-004 — source-012 (owner amendment 11, verbatim)

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message. Amends `source-001.md`.
Frozen baseline unchanged: `421265709f81a40e20f3d890609907ed932967dd`.
Head at capture time: `origin/main` = local `main` = `11f3540c602849f4100517f35b7b93eca6742a8d`
(post PR #134), reconciled live against GitHub before any write.

Requirement IDs added by this amendment start at `D-004-R421`; no existing source file or
requirement row is edited.

## Reconciliation of the owner's stated baseline against live state

The owner's GO states an expected head of `208c939dcb9c0afe9f0bb72cc53bc784f2cc2514` (PR #133).
Live head is `11f3540c602849f4100517f35b7b93eca6742a8d` — **one commit further on**, the merge of
PR #134, a docs-only refresh of `docs/SESSION_HANDOFF.md` (1 file, +92/-49) that the owner
requested at the end of the prior session and which the same message's own leading
"Starting message for the next session" block names as its expected head. It changes no
control-plane file, no directive file, and no product file. The difference is therefore recorded
as **non-material** and execution proceeded; it is disclosed here rather than silently absorbed.

Every other value the owner stated was verified live and matched exactly:

| Owner-stated value | Live verification | Match |
|---|---|---|
| PR #132 merged | merge commit `b3018f38f8d715518e5de17c4d87cc7df69079dd` | yes |
| PR #133 merged | merge commit `208c939dcb9c0afe9f0bb72cc53bc784f2cc2514` | yes |
| M0-T033 accepted at 100% | `project-control/tasks/M0-T033.json` status=accepted, progress_percent=100 | yes |
| M0-T027 blocked at 75% | `project-control/tasks/M0-T027.json` status=blocked, progress_percent=75 | yes |
| accepted-task count 53 | `project-control/state.json` accepted_tasks length 53 | yes |
| checkpoint CP-0035 | `project-control/state.json` last_checkpoint | yes |
| D-004 manifest version 11 | `manifest.json` version=11 | yes |
| 420 locked append-only requirement IDs | `requirements.json` 420 rows, validator exit 0 | yes |
| M0-T032 backlog | `project-control/tasks/M0-T032.json` status=backlog | yes |
| M0-T025 backlog | `project-control/tasks/M0-T025.json` status=backlog | yes |
| no M0-T029 task file | `project-control/tasks/` contains no `M0-T029.json` | yes |

## Transmission note (honest record of the received text)

The owner's message arrived as two blocks. The first, headed "Starting message for the next
session", was **truncated mid-word by the transport in six places** (marked `[truncated in
transmission]` below at the exact points where the received text ends). The second block, headed
"GO — EXECUTE M0-T027 PHASES 3 AND 4 ONLY", arrived **complete and unmutilated** and is the
operative authorization. The two blocks agree on every instruction that both express. No
requirement below is derived from a truncated fragment: where a truncated line's completion is
not certain, the corresponding requirement is taken from the complete GO block, which covers all
of the same ground. Nothing was reconstructed, guessed, or filled in.

---

## Block 1 — "Starting message for the next session" (verbatim as received, truncations marked)

Starting message for the next session

Resume NYC Buildability as orchestrator. Reconcile live first (git, GitHub, CI,
project-control), then read docs/SESSION_HANDOFF.md and the M0-T027 progress log.

Expected state, subject to live verification:
- main = origin/main = 11f3540c602849f4100517f35b7b93eca6742a8d
- 53 accepted tasks; checkpoint CP-0035
- M0-T033 accepted (the invalid_unblock_roster guard fix)
- M0-T027 blocked at 75%, evidence complete and merged
- PRs #131-#134 merged
- M0-T029 does not exist; M0-T032 and M0-T025 backlog

If live state differs materially, STOP and report before writing.

The amendment-8 Opus-5 exception (D-004-R307) remains ACTIVE: use explicit Opus 5
for every producer, independent reviewer and verifier, and disclose the actual
model honestly. Write no effort key anywhere; do not touch teamma[truncated in transmission]

AUTHORIZED WORK — M0-T027 Phase 3, then Phase 4. Nothing else.

PHASE 3 — two truth-preserving packet clarifications, and no other material change:
1. AS-1 must no longer demand the obsolete literal total of 128 locked directive
   requirements. Preserve 128 as the contract-time baseline, but
   current append-only total, matching digests, and a green validator. Do not
   rewrite directive history.
2. AS-6 must preserve the historical Step-1 sentinel FAILURE exac[truncated in transmission]
   It may be satisfied only across the owner-sequenced remediation arc, by citing
   the later M0-T028 fresh-session Phase-8 proof of guard denial and independently
   verified sentinel absence. Do not claim the original Step-1 se[truncated in transmission]

PHASE 4 — closeout:
1. Unblock M0-T027 through the normal CLI (the M0-T033 guard admi[truncated in transmission]
   shape alone; confirm that rather than assuming it).
2. Freeze the final closeout identity.
3. Regenerate its evidence map through the canonical resolver. It
   stale — 97 ids recorded vs 150 derived. Do not preserve the old count.
4. Dispatch all required independent reviewers using explicit Opus 5.
5. Preserve every reviewer return verbatim.
6. Run final independent directive verification.
7. Stop on any blocking or ambiguous result.
8. If every gate passes: submit, merge through protected main, ve[truncated in transmission]
   identity, accept through the CLI, and checkpoint only if policy requires it.
9. Clean only branches/worktrees created for this task.

STILL NOT AUTHORIZED: Step 5 / M0-T029; M0-T032; M0-T025; another
teammateDefaultModel or effort changes; legal-rule or predicate-schema follow-ups;
deployment, G6, Graphify, expansion, survey work, or hold releases.

STOP after M0-T027 is either accepted or blocked by a new substantive finding, and
return: final main SHA; PR; task status; accepted count and checkpoint; complete
gate and test results; directive-verification results; changed-fi[truncated in transmission]
confirmation that no unauthorized lane began.

---

## Block 2 — the operative GO (verbatim, complete as received)

GO — EXECUTE M0-T027 PHASES 3 AND 4 ONLY

This is execution confirmation for the already-authorized OPTION B sequence in D-004 source-010. It does not authorize Step 5 or any unrelated work.

LIVE BASELINE

Independently reconcile before writing. Expected current state:

- main = origin/main = 208c939dcb9c0afe9f0bb72cc53bc784f2cc2514
- PR #132 merged
- PR #133 merged
- M0-T033 accepted at 100%
- M0-T027 blocked at 75%
- accepted-task count 53
- checkpoint CP-0035
- D-004 manifest version 11 with 420 currently locked append-only requirement IDs
- M0-T032 backlog
- M0-T025 backlog
- no M0-T029 task file

If anything differs materially, stop before writing and report it.

PRE-FLIGHT REVIEWER-ROSTER CORRECTION

Before Phase 3, correct one administrative roster mismatch:

M0-T027 requires G5, but its current reviewer_agents roster does not include security-reviewer. docs/GATES_AND_CHECKPOINTS.md assigns security/privacy review to security-reviewer, and gate() refuses an independent gate from an identity not listed in reviewer_agents.

I authorize adding exactly:

security-reviewer

to M0-T027 reviewer_agents.

This is a truthful, non-material roster correction solely to make the already-required G5 satisfiable by the proper specialist. reviewer_agents is excluded from MATERIAL_FIELDS. Do not change producer_agent, required_gates, or any other reviewer identity. Record the correction and rationale honestly through the canonical control process.

If this cannot be done without violating an active control-plane rule, stop and report rather than using another reviewer as a substitute.

M0-T027 already has a historical G0 PASS record. Do not overwrite, recreate, backdate, or falsify it. Verify that the existing record remains valid under the stored-history acceptance rules. If final acceptance unexpectedly requires a replacement G0 that current gate() cannot lawfully record, stop and report.

PHASE 3 — ONLY TWO TRUTH-PRESERVING ACCEPTANCE-SCENARIO CLARIFICATIONS

Apply exactly the two clarifications authorized by D-004 source-010.

1. AS-1

Remove the obsolete requirement that the live directive registry contain exactly 128 locked IDs.

Preserve 128 explicitly as the contract-time historical baseline.

The revised scenario must require:

- the current append-only locked-ID total as derived from the live registry;
- matching requirements_id_digest_sha256;
- matching requirements_content_digest_sha256;
- validator exit 0;
- no alteration, deletion, renumbering, or rewriting of prior directive history.

The live global total is currently 420, but do not permanently hard-code 420 as though it can never grow. Verify the current value mechanically at execution time.

2. AS-6

Preserve the original Step-1 sentinel failure exactly as recorded:

- the original Bash-redirection sentinel escaped;
- the original Step-1 result must never be rewritten as a pass;
- the original report and FAIL/FAIL/PASS history remain unchanged.

AS-6 may be satisfied only across the owner-sequenced remediation arc by citing the later M0-T028 fresh-session Phase-8 evidence proving:

- readonly_agent_guard denied the load-bearing Bash-redirection attempt;
- the orchestrator independently verified that the sentinel file did not exist;
- B-015 was resolved only after that fresh-session proof.

Do not claim the original Step-1 test passed.

Make no other material packet change. Do not edit any historical pilot report, committed directive source, locked requirement row, or prior gate record.

Record whether these authorized acceptance-scenario changes alter any packet digest and how the control plane handles that change. Do not backdate anything.

PHASE 4 — COMPLETE M0-T027

After Phase 3 is committed and verified:

1. Unblock M0-T027 through the normal CLI using the corrected M0-T033 guard behavior. No direct status edit.

2. Freeze one exact final closeout identity.

3. Regenerate the M0-T027 evidence map using the canonical resolver.

Keep these numbers separate:

- 128 was the historical global requirement total at contract time.
- 420 is the current global locked total at this live baseline.
- The requirements applicable specifically to M0-T027 must be independently derived by the canonical resolver.

Do not assume the applicable count is 128, 420, or any previously reported number. Stop on unresolved applicability.

4. Run the producer/orchestrator G2 self-check.

5. Dispatch all independent reviewers read-only against the same frozen closeout identity:

- code-reviewer for G3;
- security-reviewer for G5;
- control-plane-verifier for lifecycle and containment;
- directive-compliance-verifier for the complete independently derived requirement set.

Use explicit Opus 5 for every reviewer/verifier under the still-active temporary availability exception. Record the actual model honestly. Do not claim Fable 5.

6. Every reviewer must independently inspect primary evidence rather than relying solely on the producer report. Preserve every reviewer return verbatim.

7. Confirm:

- all three pilot reports remain historically honest;
- B-015 remains resolved;
- AS-1 and AS-6 are satisfied exactly as clarified;
- the M0-T033 guard change is operating normally;
- no reviewer equals the producer;
- every required gate has a lawful PASS record;
- directive verification covers exactly the resolver-derived applicable set;
- validator and contracted test suites exit 0;
- the changed-file set is confined to M0-T027's authorized paths and lifecycle artifacts;
- no unrelated task or product file changed.

8. Stop on any FAIL, BLOCKED, unresolved requirement, ambiguous identity, unexplained diff, non-green CI result, or control-plane refusal. Do not force, bypass, substitute reviewers, or call a red result green.

9. If everything passes:

- submit M0-T027 through the CLI;
- open the protected-main PR;
- verify required CI at the exact PR head;
- merge only when green;
- perform merged-main identity and directive re-verification;
- accept M0-T027 through the CLI;
- create a checkpoint only if current policy requires one;
- clean only branches/worktrees created for this M0-T027 closeout.

The D-001 empty-applicable-set behavior found during M0-T033 acceptance is not part of this task. Do not change accept(), D-001, or directive-resolution behavior under this GO.

STILL NOT AUTHORIZED

- Step 5 or M0-T029
- M0-T032
- M0-T025
- another producer or product wave
- product or legal-rule changes
- predicate-schema follow-up
- teammateDefaultModel changes
- any effort key or effort setting
- hooks, agent definitions, or settings changes
- deployment or hold releases
- G6, Graphify, expansion, survey, or unrelated handoff work

STOP after M0-T027 is either accepted or genuinely blocked by a new substantive finding.

Return:

- final main SHA;
- M0-T027 PR and merge SHA;
- M0-T027 final status;
- accepted-task count and checkpoint;
- exact AS-1 and AS-6 changes;
- reviewer-roster correction and rationale;
- applicable-requirement count derived by the resolver;
- complete G2/G3/G5 and independent-verification results;
- test and CI results;
- changed-file inventory;
- cleanup performed;
- confirmation that every unauthorized item remained untouched;
- refreshed Step-5 packet as a proposal only, not executed.
