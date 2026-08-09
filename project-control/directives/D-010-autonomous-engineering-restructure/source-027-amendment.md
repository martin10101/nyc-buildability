# D-010 source-027 — R289 incident: source-026 automatic fallback FAILED (DID-NOT-SWITCH) + bounded turnover-reliability defect (owner, 2026-08-09)

Captured verbatim from the owner's session message (Claude Code interactive session,
2026-08-09, immediately after Fable 5 reached its weekly usage limit and hard-stopped the
session during the M2-T015 unit-3j-1 redispatch). Frozen base SHA
`40c848bdb35c0d96a5f71ec98b94b403e6894c15` (origin/main at capture, = PR #199 merge). This
amendment records the POST-HOC result of the source-026 fallback test (R285-R291) and adds
the owner's recovery + bounded-defect requirements. Typos preserved exactly.

## Context observed before the message (orchestrator, non-authoritative)

- Attached screenshot (preserved at `project-control/reports/D-010-R289-fallback-incident/fable5-limit-hardstop-screenshot.jpg`)
  shows, after the orchestrator's r35 dispatch commands, the message:
  **"You've reached your Fable 5 limit. Run /usage-credits to continue or switch models with /model."**
  No automatic `claude-opus-4-8` successor appeared; product execution stopped.
- Image caption from the owner: **"u didn't start the new module"** (the survey_evidence
  generator unit had not yet produced a committed checkpoint).
- The owner then ran `/model claude-opus-4-8` manually (stdout: "Set model to Opus 4.8 and
  saved as your default for new sessions" / ".claude\settings.json pins Fable 5 — that
  applies on restart"). The current session therefore continues under a MANUAL model switch,
  not an automatic one.

## Verbatim owner text

> OWNER INCIDENT DIRECTIVE — SOURCE-026 AUTOMATIC FALLBACK FAILED
>
> The observed R289 verdict is DID-NOT-SWITCH.
>
> Fable 5 reached its usage limit and displayed:
>
> "You've reached your Fable 5 limit. Run /usage-credits to continue or switch models with /model."
>
> No automatic Opus 4.8 successor appeared and product execution stopped.
>
> Do not claim that the fallback succeeded.
>
> The repository evidence also shows that PR #199 described the settings as "Effective on session restart," but the same existing Fable session continued afterward. Therefore distinguish honestly between:
>
> 1. the fallback configuration possibly not being reloaded because the session was never restarted;
> 2. weekly quota exhaustion possibly not qualifying for Claude Code's built-in fallbackModel behavior;
> 3. the larger architectural gap that no process outside the exhausted main Claude session existed to detect the hard stop and launch an Opus successor.
>
> Proceed now as the manually recovered claude-opus-4-8 xhigh successor already authorized by R286.
>
> First:
>
> - preserve the stopped Fable transcript and failure message as evidence;
> - record the R289 DID-NOT-SWITCH result durably;
> - inspect the current git tree, task branch and runtime journals;
> - preserve any safe partial work created after PR #199;
> - confirm the latest committed M2-T015 checkpoint before continuing;
> - apply R291 through the lawful mutable model-selection path so supervised Claude workers use Opus 4.8 while Fable is exhausted;
> - do not modify the immutable protected configuration;
> - do not touch LIMITED-AUTO authorization.
>
> Then resume and finish M2-T015 units 3j and 3k from the latest safe seam. Do not repeat completed product work.
>
> Create one narrowly bounded reliability-defect task for genuine unattended main-orchestrator model turnover. The required outcome is that an independently live process—not the exhausted Claude session itself—can:
>
> - recognize a structured quota/hard-stop result;
> - preserve the stopped-session evidence;
> - launch exactly one successor session explicitly on claude-opus-4-8 xhigh;
> - load the durable handoff;
> - update the lawful mutable worker-model selection where required;
> - resume from the latest safe checkpoint without duplicate workers or duplicate commits;
> - fail closed if the result is ambiguous.
>
> Include deterministic tests for session-restart configuration loading, quota hard-stop detection, exactly-once successor launch, audit preservation, duplicate prevention and safe failure.
>
> Keep this fix small. Do not redesign the supervisor and do not derail the nearly completed M2-T015 product task. Schedule implementation at the next clean seam, preferably after M2-T015 acceptance and before M2-T016 unless it becomes necessary for safe continuation.
>
> Return:
>
> 1. the durable R289 incident record;
> 2. the exact recovered M2-T015 checkpoint;
> 3. proof that the active orchestrator and supervised worker selection are now Opus 4.8;
> 4. the bounded defect task ID and scheduling;
> 5. confirmation that M2-T015 product work has resumed.

## Capture annotations (orchestrator, non-authoritative)

- "The observed R289 verdict is DID-NOT-SWITCH" is the owner's authoritative post-hoc verdict
  for the source-026 test. R289 is discharged with this result; the R288 pre-registered log
  gets an APPENDED dated verification section (never an edit).
- "manually recovered claude-opus-4-8 xhigh successor already authorized by R286" — the owner
  invokes the R286 orchestrator-continuity authorization; the switch was manual (owner typed
  `/model`), which is exactly the FAILURE CASE the source-026 log pre-registered.
- The three honest distinctions (config-not-reloaded / quota-not-qualifying-for-fallbackModel /
  no-external-successor-process) must all be stated; none may be silently chosen.
- "apply R291 through the lawful mutable model-selection path" = edit ONLY
  `C:/SupervisorController/model_selection.toml` (the mutable worker selection); the protected
  `C:/Program Files/SupervisorConfig/config.toml` and LIMITED-AUTO enablement are untouched.
- The bounded reliability-defect task is NEW work (turnover watchdog); it is small, must not
  redesign the supervisor, and is scheduled at the next clean seam — preferably after M2-T015
  acceptance and before M2-T016, sooner only if required for safe continuation.
