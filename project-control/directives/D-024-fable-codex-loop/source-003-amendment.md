# D-024 Amendment 3 — Native Claude Code capability re-baseline campaign (owner instruction 2026-08-26)

Captured: 2026-08-26 UTC by the orchestrator (Fable 5), verbatim from the owner's prompt in the
active session (session_01HfptKuEs3RDxaxsSHJjc7t). Channel: Claude Code interactive session,
owner terminal prompt. Base identity at capture: branch `control/D-024-fable-codex-loop`, HEAD
`05d03a0b830a815b8ed5fa640b5ebf470dbf65b9` == origin tip, tree clean, `/mcp` = "No MCP servers
configured" (owner-run, in-session), Bootstrap Gate 0 PASS (primary cwd IS the worktree root
`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`).
Amends: `source-001.md` (owner directive v4). Requirement IDs assigned: D-024-R139..D-024-R191.

Registry context at capture (reverse trace): M0-T091 ACCEPTED (campaign seq 8, frozen `b2e3b2c`);
M0-T092..M0-T096 all `backlog` (unstarted — surgically amendable per this instruction); no D-024
task claimed or in progress; D-030 (successor capability re-baseline) active — this amendment is
the detailed owner instruction for the re-baseline that D-030 required; its bounded gated ledger
task is created as **M0-T102** (unit A, cites `D-030:ALL`), with **M0-T103** as unit B
(installed/upgraded-version probes + official-updater upgrade). Units C–J receive task IDs at
campaign conversion (an M0-T102 output) — their requirement rows bind M0-T102 (the conversion
duty) plus the existing unstarted packets they govern (unit F → M0-T092; unit G → M0-T094;
unit H → M0-T093, M0-T095; unit I → M0-T096), and are restamped with the new unit task IDs when
those packets are created (manifest audit_log entry per restamp). Accepted work (M0-T086..M0-T091,
M0-T097..M0-T101) is immutable and NOT reopened; no new requirement ID binds to any already-gated
or accepted task.

---VERBATIM-BEGIN---
This is a new owner instruction governing the D-024 Fable–Codex continuous-agent-loop campaign.

Do not claim M0-T092 or any later existing implementation task until this instruction has been durably captured, reconciled, independently verified, and converted into a dependency-ordered re-baseline campaign.

ROLE SEPARATION

Preserve these roles exactly:

1. Fable 5, running inside Claude Code, is the producer that performs engineering work.
2. Codex is the external read-only supervisor, reviewer, sequencer, and loop manager. Codex is not the primary coding producer.
3. The repository ledger, frozen Git identities, requirement records, and accepted verification evidence are durable authority.
4. I am the owner and remain the final authority for activation, security-sensitive changes, dependency admission, protected GitHub effects, and any explicitly owner-gated action.

FIRST: RECONCILE BEFORE WRITING

Work from durable repository evidence rather than this prompt’s assumptions.

1. Verify the live repository root, branch, HEAD, origin, worktree state, and MCP-clean status.
2. Read CLAUDE.md, docs/SESSION_HANDOFF.md, the applicable project-control rules, the D-024 directive and amendments, its requirements and verification records, its campaign-continuity record, and all accepted or active D-024 task packets.
3. Run:
   python tools/project_control.py status
   python -m tools.agent_supervisor.campaign_continuity --status
4. Confirm M0-T091’s real state. If it is not accepted, pushed, clean, and at a safe seam, stop and report BLOCKED. Do not overlap it.
5. Detect any later task already claimed or started. Never duplicate completed or active work.
6. Verify no conflicting writer lease, agent worktree, shell, or uncommitted repository state exists.
7. Report the reconciled identity and READY TO CAPTURE or BLOCKED before proceeding.

OWNER INSTRUCTION

Claude Code has added native functionality that overlaps materially with portions of the original D-024 plan. Re-baseline the unimplemented portion of D-024 so that we reuse supported native Claude Code functionality instead of building duplicate machinery.

Do not discard accepted work. Do not rewrite the original directive source. Capture this instruction through the repository’s normal owner-directive amendment process, assign collision-free requirement and task identities, update the requirement-to-test mapping, and preserve full traceability.

This amendment authorizes:

* An evidence-based capability re-baseline.
* Controlled testing of the current stable Claude Code release.
* Updating the user-level Claude Code binary through its official updater only after the pre-update state is durably captured, the worktree is clean, and no unrelated Claude sessions would be disrupted.
* Surgical changes to unstarted D-024 tasks.
* Replacement of redundant custom runtime machinery only after its native replacement passes deterministic and real canaries.
* Use of native Claude Code functionality where verified.
* Creation of a temporarily feature-detected adapter and rollback path during supervised rollout.

This amendment does not authorize:

* Continuous-mode activation.
* Admission of the Claude Agent SDK.
* Enabling new MCP servers or channels.
* Merging or modifying protected or held PRs.
* Silent model substitution outside the existing approved policy.
* Bypassing owner gates.
* Dangerous permission-bypass flags.
* Unbounded fan-out.
* Replacing the repository ledger with Claude session state or messages.

OFFICIAL DOCUMENTATION BASELINE

Review the latest official documentation at execution time, not cached recollection:

* https://code.claude.com/docs/en/changelog
* https://code.claude.com/docs/en/agent-view
* https://code.claude.com/docs/en/goal
* https://code.claude.com/docs/en/hooks
* https://code.claude.com/docs/en/cli-reference
* https://code.claude.com/docs/en/skills
* https://code.claude.com/docs/en/worktrees
* https://code.claude.com/docs/en/workflows
* https://code.claude.com/docs/en/sub-agents
* https://code.claude.com/docs/en/sessions
* https://code.claude.com/docs/en/cross-session-messaging
* https://code.claude.com/docs/en/plugins-reference
* https://code.claude.com/docs/en/statusline
* https://code.claude.com/docs/en/commands
* https://code.claude.com/docs/en/checkpointing
* https://code.claude.com/docs/en/remote-control

The previously recorded installed version is 2.1.220, while official documentation reviewed on 2026-08-26 listed 2.1.246. Treat both as historical evidence. Re-probe the live binary and current official release.

Do not assume a documented feature exists or behaves correctly on the installed Windows version. Every adopted feature requires an installed-version fixture and a real canary.

REQUIRED CAPABILITY MATRIX

Create a durable matrix mapping every remaining D-024 requirement and task to one of these decisions:

1. NATIVE REPLACEMENT — Claude Code provides the behavior; remove or do not build the duplicate.
2. NATIVE WRAPPED — Claude Code supplies the runtime primitive, while D-024 adds durable state, policy, verification, or recovery.
3. CUSTOM REQUIRED — no sufficient native capability exists.
4. OPTIONAL ENHANCEMENT — useful but not required for loop activation.
5. REJECTED OR DEFERRED — inappropriate, experimental, unsafe, or contrary to project policy.

For every decision record:

* Official documentation source.
* Minimum version.
* Installed probe result.
* Confidence level.
* Exact D-024 requirements affected.
* What existing code is reused.
* What new code remains necessary.
* Failure behavior and fallback.
* Unit, fixture, integration, adversarial, and real-canary evidence.
* Removal or deprecation plan for anything made redundant.

NATIVE CAPABILITIES TO EVALUATE

1. `/goal`
   Use it only as the inner continuation mechanism for one bounded Fable assignment with a measurable completion condition. Never use one goal for the entire software campaign. Verify condition-met, impossible, no-progress, background-work check-in, transient-error, unrecoverable-error, resume, and context-pressure behavior.

2. Native background sessions
   Evaluate `claude --bg`, `/background`, Agent View, `claude agents --json`, `attach`, `logs`, `stop`, `respawn`, and daemon status/recovery.

If proven, make the native background session the preferred Fable producer host. Codex must still control sequencing, review, acceptance, and durable campaign state.

Agent View is a research-preview capability. Keep a feature-detected fallback until supervised canaries prove it reliable. Do not run two active process-management systems simultaneously.

3. Structured passive observation
   Evaluate:

* `claude agents --json`
* `--output-format stream-json`
* `--forward-subagent-text`
* `--include-hook-events`
* Deterministic session IDs and names
* Existing statusLine and subagentStatusLine feeds

Codex must observe these feeds outside Fable’s context. Never ask Fable for routine token or status reports. Never place token quotas or context numbers in worker assignments.

4. Hooks as the event bus
   Probe and fixture at least:

* SessionStart and SessionEnd
* UserPromptExpansion
* UserPromptSubmit
* SubagentStart and SubagentStop
* TaskCreated and TaskCompleted
* Stop and StopFailure
* PreCompact and PostCompact
* PostToolBatch
* Notification
* WorktreeCreate and WorktreeRemove
* ConfigChange

Use hooks to record events, enforce completion gates, classify typed failures, and detect safe seams. Avoid transcript polling when a structured native event exists.

Hooks must remain fast, deterministic, sanitized, bounded, and fail closed where security or authority requires it.

5. Native worktree isolation
   Evaluate background-session worktrees, `--worktree`, `isolation: worktree`, WorktreeCreate, WorktreeRemove, and `.worktreeinclude`.

Reuse native physical isolation where proven. Retain the project’s logical writer leases, frozen-identity review, branch policy, cleanup verification, and protection against semantically overlapping work.

6. Dynamic workflows
   Evaluate only for bounded internal fan-out such as:

* Independent read-only reviews.
* Test matrices.
* Codebase audits.
* Repetitive migrations.
* Cross-checking findings.

Use their progress and token visibility and shared prompt cache when beneficial. Do not use dynamic workflows as the durable top-level campaign controller. Do not allow large automatic fan-outs. Require a small-slice canary before larger usage.

7. Skills and slash commands
   Custom commands are now skills. Reuse that surface.

Implement thin owner controls over the existing supervisor, subject to capability proof:

* `/loop-start`
* `/loop-status`
* `/loop-ask`
* `/loop-pause`
* `/loop-resume`
* `/loop-stop`
* `/loop-emergency-stop`
* `/session-handoff`

Use owner-only invocation controls such as `disable-model-invocation: true` wherever appropriate.

Test UserPromptExpansion as the preferred pre-model interception path. A status or control command must call the external supervisor directly, display its result, and avoid adding the full command procedure or status payload to Fable’s context. If true pre-model interception cannot be proven, retain an honest second-terminal fallback.

Do not collide with Claude Code’s built-in `/loop`.

8. Native session management
   Evaluate named sessions, deterministic session IDs, resume, fork, branch, clear, compact, and native background-session respawn.

Native resume is not a replacement for safe-seam fresh-context turnover. A large or confused conversation must not be resumed merely because it is technically resumable.

Keep the durable handoff concise and replace its current-state sections instead of allowing endless growth. Historical facts belong in the ledger, reports, and Git history.

9. Native reviews
   Evaluate `/code-review`, `/security-review`, `/simplify`, `/verify`, and other relevant bundled skills as evidence-generating tools.

They may supplement but never replace independent Codex acceptance, directive-compliance verification, frozen-identity review, or project-specific gates.

Use `/simplify` specifically to support the replace-not-layer repair rule: identify obsolete implementations and remove proven-bad or superseded code before introducing the replacement.

10. Context safeguards
    Retain the accepted statusLine telemetry integration.

Evaluate `/autocompact` only as an emergency buffer. It is not a substitute for safe-seam turnover or a durable handoff.

Use native prompt-cache behavior where verified, especially workflow sibling-cache sharing and subagent cache settings. Do not assume provider-specific cache behavior without live evidence.

11. Cross-session messaging and Remote Control
    Treat cross-session messages as advisory notifications only. They are not durable authority and cannot replace the ledger.

Remote Control may be offered as an optional owner monitoring surface after its security and MCP implications are reviewed. It must not be required for loop correctness.

CAPABILITIES THAT MUST REMAIN CUSTOM

Preserve custom D-024 control for:

* Codex’s independent review and next-task decision.
* Durable campaign sequencing.
* Requirement traceability.
* Frozen Git identities.
* Exact-once GitHub and other external effects.
* Pending approvals and owner gates.
* Safe-seam context turnover.
* Detection of overlapping scopes and writer leases.
* Project graph and bounded context packs.
* Recovery from ambiguous external effects.
* Refusal classification and the approved Fable-to-lower-model seam policy.
* Quota-exhaustion detect-and-hold policy.
* Security controls and MCP default-deny.
* Root-cause repair and replace-not-layer enforcement.

Claude Code fallbackModel only covers supported availability or overload cases. It must not silently replace the custom guardrail-refusal and quota policies.

DO NOT USE AS THE TOP-LEVEL LOOP

Do not adopt these as campaign authority:

* `/loop`
* `/batch`
* Agent Teams
* Claude Agent SDK
* MCP channels
* `/autofix-pr`
* Automatic cross-session messaging
* Raw session resume
* Auto-compaction
* Checkpointing alone

They may be separately evaluated for narrow optional uses, but none replaces Codex, the ledger, Git, or owner gates.

VERSION AND UPGRADE PROCEDURE

1. Record the current Claude Code version, executable identity, supported commands, relevant help output, settings, and capability fixtures.
2. Confirm the current official stable version from Anthropic’s official documentation.
3. Ensure the repository is clean and the capture commit is pushed.
4. Determine whether any unrelated Claude Code session would be disrupted.
5. Use only Claude Code’s official updater. Do not install a third-party build, SDK, or wrapper.
6. Record the post-update binary identity and version.
7. Recognize that the already-running process may remain on the old binary. Launch disposable child canaries using the new binary.
8. Re-run Bootstrap Gate 0, MCP default-deny, settings validation, statusLine, skills, hooks, and existing accepted test fixtures.
9. If a regression appears, do not work around it silently. Record it and use the supported rollback or fallback path. If no supported safe rollback is available, stop for the owner.
10. Do not activate the new runtime backend merely because the version command succeeded.

IMPLEMENTATION CAMPAIGN

Do not perform this as one enormous coding task. One owner prompt may start the campaign, but the campaign must be decomposed into cohesive, independently reviewable tasks.

At minimum create these dependency-ordered units, adjusted to real component boundaries after mapping:

A. Directive amendment, baseline reconciliation, official-document snapshot, and requirement-to-capability matrix.

B. Installed-version and upgraded-version deterministic capability probes with masked fixtures.

C. Native runtime adapter:

* Feature detection.
* Named and deterministic session identity.
* Native background dispatch.
* `claude agents --json` status ingestion.
* Attach, logs, stop, and respawn support.
* Existing controller fallback.
* Exactly one selected runtime backend per session.

D. Native event integration:

* Hook records.
* Stream-JSON subagent events.
* Deduplication.
* Redaction.
* Atomic persistence.
* Restart-safe replay.
* Unknown and version-drift handling.

E. Bounded `/goal` integration:

* One cohesive task at a time.
* Safe completion condition.
* No-progress handling.
* Background-agent check-ins.
* No worker-visible token pressure.

F. Safe-seam session succession:

* Allow healthy bounded subagents to finish.
* Stop or quarantine stale work.
* Commit and push accepted evidence.
* Generate a bounded replacement handoff.
* Start a genuinely fresh Fable session.
* Recover without duplicate work after interruption.

G. Thin slash-command/operator interface using skills and UserPromptExpansion.

H. Remaining refusal bridge, root-cause repair gate, exact-once GitHub effects, and graph-regression requirements that native Claude Code does not replace.

I. Shadow-mode, supervised-mode, crash/restart, and golden-run activation campaign.

J. After the local loop passes its golden run, prepare a separate portability plan for a generic Claude Code plugin containing reusable skills, agents, hooks, and adapters. Keep NYC-specific graph, ledger, security policy, profiles, and product rules in this repository. Portability work must not block the local loop’s activation.

REPLACE-NOT-LAYER RULE

Never merely bolt a native path beside a redundant custom implementation and leave both indefinitely.

For every replaced component:

1. Prove the native behavior.
2. Identify the exact old responsibility.
3. Introduce one bounded adapter if necessary.
4. Run old-versus-new parity and failure tests.
5. Select only one active backend.
6. Remove or clearly deprecate unreachable redundant code in a separate reviewed change.
7. Preserve rollback only for the supervised rollout period.
8. Record when the fallback can be removed.

Never delete accepted code solely because official documentation claims an equivalent feature exists.

MANDATORY TESTING

Use deterministic fixtures, accelerated counters, simulated failures, disposable branches/worktrees, and real low-risk canaries. Do not burn hundreds of thousands of tokens merely to prove a threshold.

Required proof includes:

* Windows-native behavior.
* Exact installed-version behavior.
* Strict MCP default-deny remains effective.
* StatusLine and telemetry do not leak user paths, secrets, session data intended to be masked, or credentials.
* Native background dispatch, status, completion, blocked-input, failure, stop, and respawn.
* Supervisor restart with no duplicate producer.
* Unexpected producer-process exit.
* Worktree creation, isolation, retention, and cleanup.
* `/goal` met, impossible, stalled, interrupted, resumed, and background-work behavior.
* Hook firing order and blocking semantics.
* UserPromptExpansion zero-model-context proof or truthful fallback.
* Subagent start, progress, completion, stale work, and natural landing.
* No routine polling messages inserted into Fable context.
* No token quotas exposed in worker assignments.
* Concurrent independent work and overlapping-scope rejection.
* Session rotation at a safe seam.
* Handoff boundedness and successor reconstruction from durable state alone.
* Refusal and quota triggers remain distinct.
* GitHub effects are idempotent and exactly once.
* Crash between local commit and push.
* Crash after push but before local acknowledgment.
* Stale ledger and stale handoff reconciliation.
* Graph and context-pack regression coverage.
* Existing project suite remains green.
* Independent security, QA, control-plane, and directive-compliance review at the same frozen identity.
* Mutation tests demonstrating that important gates fail when deliberately broken.

GOLDEN RUN

Before activation, perform one low-risk real campaign task proving this complete sequence:

1. Codex reads the durable campaign.
2. Codex selects one bounded task.
3. Codex launches a named Fable producer through the selected native runtime backend.
4. Fable works toward a bounded goal.
5. Subagents are structurally sized and passively observed.
6. Context and health are monitored without interrupting workers.
7. Work lands at a safe seam.
8. Tests and independent reviews run.
9. Codex accepts, revises, rotates, holds, or rejects based on evidence.
10. Git and GitHub effects occur exactly once.
11. A fresh successor reconstructs state without conversation-only knowledge.
12. The campaign advances to the correct next task.
13. Pause, status, ask, resume, stop, and emergency-stop behave correctly.
14. A simulated crash recovers without duplicated work.
15. No protected owner gate is crossed.

Continuous mode remains disabled after the golden run until I explicitly authorize activation.

CAMPAIGN EXECUTION AND TRACKING

After the amendment and task campaign are accepted:

* Work through the dependency-ordered tasks automatically.
* Claim only one cohesive writer task at a time unless independent worktrees and non-overlapping scopes are proven.
* Keep the campaign-continuity record and requirement verification current.
* Use fresh producer contexts by default.
* Let healthy bounded reviewers and subagents finish naturally at turnover.
* Do not allow any single agent to expand its assignment indefinitely.
* Do not place arbitrary token ceilings in worker prompts.
* At each accepted checkpoint, commit, push, validate, and advance durable NEXT state.
* If context turnover is needed before automatic succession is ready, use `/session-handoff`, stop cleanly, and give me the exact successor command and prompt.
* Continue without waiting for me between ordinary accepted tasks.
* Stop only for an actual owner gate, unsafe ambiguity, unsupported version transition, dependency admission, protected external effect, or contradiction that cannot be resolved from durable evidence.

INITIAL DELIVERABLE BEFORE IMPLEMENTATION

Before changing runtime implementation, return a concise owner report containing:

1. Reconciled repository and campaign identity.
2. Current and target Claude Code versions.
3. The completed native-reuse matrix.
4. Which unstarted D-024 tasks change.
5. Which accepted components remain untouched.
6. What native features replace custom work.
7. What remains custom.
8. The revised task sequence.
9. Upgrade and rollback plan.
10. Test and golden-run plan.
11. Any true owner decision required.

After recording and independently validating that report and amendment, proceed with the campaign unless an explicit owner gate is reached.
---VERBATIM-END---

## Capture annex (orchestrator, not owner text)

- **Reconciliation performed before this capture** (owner section "FIRST: RECONCILE BEFORE
  WRITING", all seven steps): root `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`; branch
  `control/D-024-fable-codex-loop`; HEAD `05d03a0` == `origin/control/D-024-fable-codex-loop`
  after fetch; `git status --porcelain` empty; `/mcp` = no MCP servers (owner-run in-session);
  ledger 113 accepted / M0-T091 `accepted` at acceptance commit `4de29c2`, checkpoint
  `CP-D024-M0-T091`, seam commit `b2e3b2c` pushed; campaign record seq 8 NEXT = D-030
  re-baseline FIRST; no D-024 task claimed/started after M0-T091 (M0-T092..T096 backlog);
  no writer lease active; the only foreign worktrees are the FIVE stale pack-repo agent
  worktrees already flagged owner-visible in campaign seq 8 (outside this checkout; purge is
  classifier-denied for sessions and remains an owner action; none holds this repo's lease);
  M0-T080 (`in_progress`) belongs to the D-023 lane, not this campaign. READY TO CAPTURE was
  reported before this file was written.
- **Live version probe at capture:** `claude --version` = `2.1.220 (Claude Code)`; binary
  `C:\Users\MLFLL\.local\bin\claude.exe`. The owner-cited docs-listed `2.1.246` and the recorded
  `2.1.220` are BOTH historical evidence (D-024-R148); unit A/B re-probe live at execution time.
- **D-030 relationship:** this amendment is the owner's detailed instruction for the capability
  re-baseline D-030 required. M0-T102 (unit A) is the D-030 "bounded gated ledger task (new
  M0-T1xx id)"; it cites `D-030:ALL` and discharges D-030 at its acceptance. D-030 rows are not
  modified.
- **Sequencing preserved:** D-024-R139 holds M0-T092..M0-T096 claims until capture + independent
  verification + campaign conversion are complete. The M0-T091 carried advisory bundle (G5 L1-L5,
  G3 NIT-1/2, G4 ADV-1; campaign seq 8) folds into the first runtime/activation unit that touches
  those guards (expected unit C/D successor of M0-T092), unchanged by this amendment.
- **Standing restrictions unchanged and restated by the owner text:** never merge PR #241 or any
  pre-existing/protected/held PR; continuous-mode activation stays owner-gated (D-024 §18, R595
  path); no Agent SDK admission; no new MCP servers/channels; MCP default-deny; no
  permission-bypass flags; no worker-visible token quotas (R045); ledger is authority, never
  Claude session state.
