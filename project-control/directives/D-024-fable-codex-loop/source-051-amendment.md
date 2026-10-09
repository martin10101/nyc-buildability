# D-024 Amendment 51 — Campaign continuation to the earliest safely proven persistent Codex-managed local loop + deficit-convergence policy task (owner directive, 2026-09-03)

- **Directive:** D-024 (fable-codex-loop campaign)
- **Kind:** amendment (append-only; amends source-001.md; follows source-050-amendment.md)
- **Issued by:** owner (interactive session, 2026-09-03 UTC, one message after the M0-T107
  acceptance return; closing instruction "do both" joins the two parts)
- **Context:** M0-T107 accepted (156th) at 9dcbdd09; handoff seq 80 b8856e49; both trees clean;
  M0-T109 claimed (wt-m0t109 @ 1c069571, task/M0-T109-guard-hardening, clean, zero drift on its
  own output paths vs the candidate tip); M0-T108 accepted; campaign_continuity rc 0. The owner
  now (a) assigns the campaign from the accepted first supervised unit to the earliest safely
  proven persistent Codex-managed local loop, with the orchestrator continuing automatically
  through all safe authorized local work (bounded proof runs included) while the PERSISTENT
  loop start and every listed owner-only gate remain owner-typed; and (b) orders one small
  bounded task installing the repeated-failure deficit-convergence policy (exactly two paths).
- **Base identity at capture:** ctl24 `candidate/D-024-mrl-option-b` HEAD
  `b8856e49` (local only), tree clean; origin/main `d8b3899f`; installed controller source
  frozen `3f4cee86`.

## Verbatim owner directive

> Continue the D-024 Fable–Codex autonomy campaign from the newest durable repository state. Do the work now; do not merely give me another plan or status summary.
>
> The expected completed anchor is:
>
> * M0-T107 ACCEPTED as task 156
> * Frozen identity: 7d282011
> * Acceptance record: 9dcbdd09
> * Handoff sequence 80: b8856e49
> * Worker changes committed at 4047c79c
> * Bounded correction committed at 777ef5e4
> * Both trees clean
> * Next campaign unit: M0-T109
> * PR #241 untouched
> * R595/Option-A and R603–R605 remain owner-gated
>
> First reconcile this read-only against live Git, the project-control ledger, campaign continuity, M0-T109’s task contract, and both worktrees. Report all discrepancies together. Do not reset or alter the repository to match these expected values. If the state matches, continue immediately without asking me to say “continue.”
>
> Your assignment is to take the campaign from the accepted first supervised unit to the earliest safely proven persistent Codex-managed local loop.
>
> Execution requirements:
>
> 1. Treat M0-T107 as permanently closed. Do not reopen its accepted findings, rerun journey-m0t107-01, or rerun commissioning canaries without new contradictory evidence.
>
> 2. Put only M0-T109 in the initial queue. Execute M0-T109 exactly under its existing task contract and D-024 requirements. Carry it through implementation, correction, independent G3/G4 review, DCV, acceptance, and durable handoff.
>
> 3. Before beginning, state whether M0-T109 alone can genuinely prove all seven previously defined live-loop facts. Do not stop after stating this. If one task cannot prove them all, identify the minimum sequence of existing real tasks needed and continue through that sequence. Do not invent a sprawling new stabilization campaign merely to manufacture proof.
>
> 4. Across the next two or three real operational tasks, obtain durable evidence for every remaining local-autonomy capability:
>
> * A real Codex REVISE decision automatically returns actionable feedback to Fable.
> * Fable corrects the work and Codex reviews it again without the owner typing “continue.”
> * An accepted task automatically advances to the next ready task.
> * The controller selects that next task from durable repository state.
> * A controlled interruption preserves state.
> * The run resumes correctly from its checkpoint.
> * The foreground owner view accurately shows the task, stage, worker model, Codex verdict, pending owner decision, and final result.
>
> 5. Continue automatically through all safe, authorized local work. Do not interrupt me for routine engineering decisions, ordinary revisions, test failures, independent reviews, task transitions, session rotation, or context compaction. Use fresh model sessions and durable checkpoints rather than allowing one enormous conversation to approach context exhaustion.
>
> 6. Retain all existing safety boundaries:
>
> * Worker model must remain exactly `claude-fable-5`; never substitute Fable 5.1.
> * Codex reviewer must remain `gpt-5.6-sol` unless an already-authorized repository rule says otherwise.
> * Keep the restricted tool surface, fail-closed behavior, bounded subagent accounting, process cleanup, immutable identity checks, and circuit breakers.
> * Bounded read-only subagents may be used for independent tracing or review, but keep one writer for overlapping repository state.
> * Do not weaken a guard to obtain a passing result.
> * Do not change the installed controller, external configuration, model selection, or cwd guard unless an authorized task specifically requires it.
> * Do not impose a fixed overall wall-clock deadline on the persistent loop. Per-turn limits, per-task controls, safety stops, and session rotation must remain.
> * Do not push, create a PR, merge, deploy, use production credentials, or touch PR #241.
> * Do not activate R595/Option-A or decide R603–R605 on my behalf.
>
> 7. If a defect appears, preserve the evidence, reproduce the exact failure, trace the complete causal path, repair one bounded causal cluster, and run the complete affected verification wave once. Do not use repeated live launches as serial defect discovery.
>
> 8. Stop only for a genuine owner-only gate: credentials, payment, production, legal approval, material scope expansion, GitHub activation, an explicit policy choice, or a blocker that cannot safely be resolved inside the accepted directive.
>
> When every required local-autonomy proof passes, do not start the persistent loop on my behalf. Return exactly:
>
> `READY_FOR_PERSISTENT_LOCAL_ACTIVATION`
>
> Then provide:
>
> 1. One exact owner-copyable PowerShell command, generated from the live accepted identities, that starts the durable local Codex-managed loop with no fixed overall wall-clock limit.
> 2. Exact single commands for status, pause, resume, and stop.
> 3. The exact supported method for sending Codex new owner guidance while the loop is running. Do not invent a method; if it is not implemented, identify that clearly.
> 4. A plain-English explanation of what happens after I run the activation command.
> 5. The exact owner-authorization statement required later for R595/Option-A and R603–R605 if I choose to enable the separately proven GitHub push→PR→CI→merge lifecycle.
>
> If the proofs do not converge within the next two or three real tasks, stop with:
>
> `BLOCKED_FOR_PERSISTENT_ACTIVATION`
>
> Return one consolidated blocker list and one architecture-level viability decision. Do not begin another indefinite repair campaign.
>
> Proceed now and keep working until you reach one of those two terminal outcomes or a genuine owner-only gate.
> After M0-T107 is formally accepted, create one small bounded task to add the project’s repeated-failure convergence policy.
>
> Change exactly two paths:
>
> 1. CLAUDE.md
> 2. .claude/skills/deficit-convergence/SKILL.md
>
> Do not modify runtime controller code, tests unrelated to skill discovery, model selection, GitHub configuration, or existing accepted evidence. Do not launch a provider or begin another stabilization campaign.
>
> Add only this concise mandatory trigger to the appropriate CLAUDE.md section:
>
> “For repeated failures, commissioning failures, external CLI/provider incompatibilities, or conflicting evidence, load /deficit-convergence before editing. Do not use live reruns as serial discovery. Produce either verified closure or one consolidated blocker report.”
>
> Create a narrowly triggered deficit-convergence skill containing these 20 rules:
>
> 1. Freeze and preserve canonical evidence before rerunning.
> 2. Reproduce the exact failure before editing.
> 3. Record live repo, worktree, branch, HEAD, status, origin, executable, version, model, and configuration identity.
> 4. Keep controller source, installed controller, control-plane checkout, and worker worktree identities separate.
> 5. Map the complete path from launch input through provider output, review, persistence, and external effects.
> 6. Locate all affected producers, consumers, validators, tests, documentation, and operator commands before changing code.
> 7. Probe real external CLI/provider boundaries early with the smallest safe test.
> 8. Compare behavior against an immutable known-good version or accepted candidate.
> 9. Group symptoms by root cause and distinguish primary, cascading, and NOT-RUN failures.
> 10. Repair the smallest complete causal cluster, not one symptom at a time.
> 11. Keep provider-facing schemas minimal; enforce unsupported constraints inside the controller.
> 12. Treat all model output as untrusted; factual identity must be observed and supplied by the controller.
> 13. Record raw argv, cwd, environment facts, timestamps, exit code, stdout/stderr digests, and process-tree settlement.
> 14. Capture PowerShell $LASTEXITCODE immediately; never let a pipe or later command replace it.
> 15. Use stable typed failure codes and preserve the original provider/runtime error.
> 16. Add positive, negative, and mutation tests that prove each important guard is load-bearing.
> 17. Run focused tests after each causal cluster and the complete affected suite once at the frozen final candidate.
> 18. Use immutable inputs and transactional backup, verification, and rollback for machine-changing operations.
> 19. Parallelize independent read-only tracing where useful, but use one writer for overlapping files and shared state.
> 20. Do not perform another live rerun until the closure matrix is complete; finish with VERIFIED_CLOSED or all remaining blockers together, measured by deficits and exit criteria rather than speculative time estimates.
>
> The skill must state that it does not apply to an ordinary isolated failure with an already-proven cause. It must prohibit turning every normal task into a repo-wide audit.
>
> Validate skill discovery and frontmatter, conduct one independent review of the policy, and commit it once. No provider canary and no program-wide regression campaign.
>
> Return the exact changed files, final skill trigger, validation result, and commit SHA. End with DEFICIT_CONVERGENCE_POLICY_INSTALLED.
>  do both

## Orchestrator interpretation notes (recorded at capture, per D-001 rule 9)

1. **Bounded proof-run authorization.** Item 4's proofs (real REVISE loop-back, auto-advance,
   interruption/resume) require live supervised runs; item 5 orders automatic continuation
   through "all safe, authorized local work" without owner interruption, while the closing
   passage keeps the PERSISTENT loop start owner-typed. Read together: the orchestrator is
   authorized to launch the BOUNDED local proof runs for the identified task sequence
   (superseding, for these runs only, the earlier owner-typed-launch convention of the
   commissioning/journey amendments); the persistent loop start, R595/Option-A, and R603-R605
   remain owner-only.
2. **Terminology.** The anchor line "Frozen identity: 7d282011" names the reviewed COMMIT of
   the M0-T107 verification; the frozen CONTENT identity is
   1bbedd347b5be034d3103f409bb47e849a6c6654928b12d0293539c5e7508e4f. Both live values match.
3. **Two return tokens.** Part B's report section ends with DEFICIT_CONVERGENCE_POLICY_INSTALLED;
   the campaign response ends with the Part-A terminal token. Both appear in the final response,
   each closing its own section, the campaign token last.
