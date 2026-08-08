# D-010 — source-023 (owner amendment 23, VERBATIM): SUPERVISED-AUTO activation decision + M2-T015/T016 product-proof release

Captured per `.claude/skills/directive-compliance` §1. Channel: owner_message (typed to the
orchestrator on 2026-08-08 as the opening message of a fresh session). Frozen base at capture:
`origin/main` = `7a2ab0af3ec392ee4d8a17928815c91f9eab63e0`.

Requirement IDs added by this amendment start at `D-010-R214`; no existing source file or
requirement row (D-010-R001..R213) is edited. Relationship to source-022: this message contains
the exact owner-typed activation decision line that source-022 ordered returned (R212) and that
R131/R133/R143/R153/R167/R196/R213 held everything behind. The typed line discharges the
owner-decision precondition; the prerequisites themselves are still verified against durable
main-branch evidence before any activation act (R220). Anchors used by requirement rows:
`#session-grounding`, `#pr187-verification`, `#activation-decision`, `#runtime-transition`,
`#pre-product-verification`, `#product-proofs`, `#limited-auto-hold`, `#product-scope`,
`#m0-t047-age-gate`, `#working-rules`, `#reporting`.

## THE DIRECTIVE (verbatim from the owner message, 2026-08-08)

> You are taking over my existing NYC Buildability project in a completely fresh Codex session. The previous session became too long, so do not rely on prior conversational context. Start by reading the current HANDOFF.md in the repository and then ground yourself from the live repository, current main branch, project-control state, D-010 records, accepted tasks, gates, and the most recent merged PRs. Durable repository evidence is authoritative if anything in this message or HANDOFF.md is stale.
>
> Repository: martin10101/nyc-buildability.
>
> I am done with shadow-only operation. I want the supervisor to begin doing the REAL product work under SUPERVISED-AUTO. I am explicitly authorizing that transition, subject only to verification that the already-completed activation prerequisites are durably present on main.
>
> First check the status of PR #187, "PROTECTED live proof + source-022 capture (activation prerequisite closed)." It contains the successful live UNELEVATED controller-config proof. If PR #187 is still completing its normal required-check/merge lifecycle, finish/observe that normal lifecycle first and do not bypass any required check. If it is already merged, verify the proof landed on main. Do not begin another broad audit and do not redesign the supervisor.
>
> The live proof already established that the protected controller config is readable by the ordinary process, its SHA remains:
>
> 29eb765eabce05b81dcbea33fd4d28800479596e9b23fd4d4fa334f6ee7da1cb
>
> and the ACL evaluator reports:
>
> controller_config_acl.protected == true
> controller_config_acl.state == "PROTECTED"
> controller_config_acl.file.state == "PROTECTED"
> controller_config_acl.parent.state == "PROTECTED"
>
> The protected config path is:
>
> C:\Program Files\SupervisorConfig\config.toml
>
> The mutable runtime model-selection file remains:
>
> C:\SupervisorController\model_selection.toml
>
> The final cleared hardening-script blob is:
>
> b6ee6589d93b4cd95283ce6d45c22f7010aba56a
>
> Do not alter the ACLs or reopen the prior hardening work unless genuinely new evidence demonstrates a defect.
>
> Very important distinction: controller.default_mode = "shadow" in the immutable config is intentionally the safe fallback/default and MUST remain unchanged. Do NOT edit config.toml to change that value. What I am authorizing is for the ACTIVE supervisor runtime to come OUT OF SHADOW MODE and operate in the already-implemented SUPERVISED mode. I do not want another shadow rehearsal. I want the real supervised workflow.
>
> This is my explicit owner activation decision:
>
> ACTIVATE SUPERVISED-AUTO — I have read and accept the N-4/N-5/MINOR-2 residuals; proceed per R595/R131.
>
> Treat the sentence immediately above as my owner-issued activation instruction in this new session. Do not ask me to repeat it merely because this is a fresh session.
>
> Before acting on it, verify that PR #187 and the required activation evidence are durably on main. If a prerequisite is actually missing or failing, STOP and tell me exactly what failed. Do not silently weaken a gate.
>
> If all prerequisites are present, record my activation decision durably through the existing D-010/directive-compliance mechanism and use the EXISTING implemented supervisor runtime mechanism to make SUPERVISED-AUTO effective.
>
> Activation is NOT complete merely because an activation record was written. I require proof that the ACTIVE runtime is no longer operating in shadow mode.
>
> Keep:
>
> controller.default_mode = shadow
>
> but require the actual active execution posture for the product task to be:
>
> active runtime mode = supervised
>
> and:
>
> limited-auto = OFF
>
> Do not invent a new activation mechanism or redesign the supervisor. Read the current implementation and use its canonical runtime/start mechanism. Determine the exact command/runtime invocation from the repository rather than guessing.
>
> Before starting the product task, verify and report internally through the normal evidence path that:
>
> the owner activation record is valid;
> the controller ACL is PROTECTED;
> the immutable config SHA is correct;
> the immutable default_mode remains shadow as the safe fallback;
> the ACTIVE supervisor runtime mode is supervised;
> limited-auto remains disabled;
> M2-T015 is released for supervised-auto execution.
>
> If the active runtime still says shadow, DO NOT call activation complete and DO NOT run the product task. Resolve the existing runtime transition correctly first.
>
> Once the ACTIVE supervisor is genuinely running in SUPERVISED mode, stop working on supervisor architecture and immediately return to the actual NYC Buildability product.
>
> The first real supervised-auto product proof is M2-T015.
>
> Execute M2-T015 as a REAL supervised product task, not a simulation and not a shadow rehearsal. The worker should actually perform the authorized bounded product work, with the existing supervisor, reviews, gates, approval/park/resume protections, fail-closed mechanisms, and normal PR lifecycle operating as designed.
>
> Be self-sufficient. Do the investigation, implementation, tests, reviews, required PR work, and normal lifecycle without requiring me to manually copy instructions between agents. Only stop for me when an existing owner-only decision, genuine safety boundary, external credential, unavailable service, or other truly non-delegable dependency requires me.
>
> Do not broaden M2-T015 into unrelated work.
>
> After M2-T015 completes its full required supervised-auto lifecycle successfully, proceed to M2-T016 as supervised-auto product proof #2. Keep M2-T016 sequenced after M2-T015 rather than unnecessarily running both simultaneously.
>
> LIMITED-AUTO IS NOT AUTHORIZED. Successful completion of M2-T015 and M2-T016 does not itself authorize limited-auto. After both product proofs are complete, return the evidence package and wait for a separate future owner decision concerning any broader autonomy promotion.
>
> Also preserve all existing product scope and data. The product remains the five-borough NYC Development Feasibility & Zoning Intelligence Platform: address/BBL to official NYC data, deterministic zoning/legal calculations, development scenarios, provenance/explanations, reports, and later visualization/3D. The architect pilot and actual user-facing product are now the execution priority. Do not fall back into months of supervisor self-improvement.
>
> There is also a separate M0-T047 nanoid advisory age-gate item scheduled for eligibility on/after 2026-08-10T10:39:22Z. Do not bypass its package-age rule and do not let it distract from the current activation and M2-T015 work unless it becomes an actual blocking dependency.
>
> Owner working rules remain: one main orchestrator; bounded internal agents/reviewers are allowed; avoid destructive git operations such as reset/clean or unsafe worktree manipulation; no deletion of important zoning/rules/five-borough data; no broad autonomy redesign; preserve required gates; do not claim something passed unless evidence proves it.
>
> Start now.
>
> Your first job is to read HANDOFF.md and the live control-plane state, verify PR #187/main, process my explicit SUPERVISED-AUTO activation above if the durable prerequisites pass, prove that the ACTIVE runtime has transitioned from shadow to supervised, and then begin the real M2-T015 product work.
>
> Do not give me a long historical recap before working. I already know the history. Proceed autonomously and report back when there is a meaningful result, a genuine blocker requiring me, or the M2-T015 supervised product proof has reached its required owner-visible checkpoint.read The handoff.md

## Capture notes

- The trailing text "read The handoff.md" is preserved verbatim from the owner message.
- The repository name in the message ("martin10101/nyc-buildability") differs from the actual
  origin remote of this checkout; per the message's own rule ("durable repository evidence is
  authoritative if anything in this message ... is stale"), the live origin remote governs.
- The decision line matches character-for-character the line presented to the owner on
  2026-08-08 (docs/SESSION_HANDOFF.md, R131/R212 step): residual set N-4/N-5/MINOR-2, per
  R595/R131.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
