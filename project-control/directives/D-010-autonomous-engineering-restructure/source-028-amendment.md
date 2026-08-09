# D-010 source-028 — PRIORITY CORRECTION: implement/test/prove TRUE automatic Fable→Opus turnover as M0-T054 NOW, before M2-T015 3k (owner, 2026-08-09)

Captured verbatim from the owner's mid-turn message (2026-08-09), correcting and re-sequencing
source-027: M0-T054 is promoted from BACKLOG to an **immediate blocking dependency** of M2-T015
unit 3k, and the narrow protected-config allowlist addition (add `claude-opus-4-8`) is authorized,
narrowly superseding R297 for that exact change only. Frozen base SHA
`7cd3273dde65e8cabbe3dfa163833513985bb841` (origin/main at capture). Typos preserved exactly.

## Verbatim owner text

> pOWNER PRIORITY CORRECTION — IMPLEMENT TRUE AUTOMATIC FABLE-TO-OPUS TURNOVER NOW
>
> I am clarifying and changing the sequencing of my previous instruction.
>
> The automatic Fable 5 to Opus 4.8 turnover must now be IMPLEMENTED, TESTED AND ACTIVATED as M0-T054 before M2-T015 unit 3k continues.
>
> Do not merely document, schedule or describe it again.
>
> The previous instruction scheduling M0-T054 after M2-T015 acceptance is superseded. M0-T054 is now an immediate blocking dependency because M2-T015 itself cannot finish while Fable 5 is exhausted and the supervised worker cannot lawfully select Opus 4.8.
>
> INTENDED USER EXPERIENCE
>
> When Fable 5 becomes unavailable because its usage allowance, credits or applicable quota are exhausted while work is running:
>
> 1. I must not need to notice the message.
> 2. I must not need to type "/model".
> 3. I must not need to paste a recovery prompt.
> 4. A process outside the exhausted Claude session must detect the event.
> 5. It must automatically start exactly one successor using the full model identifier "claude-opus-4-8".
> 6. The successor must run at xhigh effort.
> 7. It must load the latest durable handoff, journal and safe product checkpoint.
> 8. It must continue the unfinished task without repeating completed work, creating duplicate workers or producing duplicate commits.
> 9. The turnover must be durable across the relevant terminal/session boundary.
> 10. If exact continuation of the same Claude session is technically and safely supported, use it. Otherwise launch a new successor session and restore continuity from durable evidence. The requirement is uninterrupted autonomous work—not a false claim that the same provider process survived.
>
> ARCHITECTURE REQUIREMENT
>
> The exhausted Claude session cannot be responsible for detecting and repairing its own exhaustion.
>
> Implement the turnover decision in an independently live deterministic controller, watchdog or existing verified launcher path outside the Claude process.
>
> Do not rely solely on:
>
> - Claude Code’s built-in "fallbackModel";
> - the exhausted session reading its own final UI message;
> - the exhausted session typing "/model";
> - model reasoning to classify the event;
> - an owner being present.
>
> The built-in fallbackModel already failed during the live R289 incident and cannot be treated as the durable solution.
>
> DETECTION REQUIREMENTS
>
> Recognize only grounded, typed Fable-unavailability signals, including the exact observed weekly-limit hard stop:
>
> “You've reached your Fable 5 limit. Run /usage-credits to continue or switch models with /model.”
>
> Use structured process output, exit results and provider/CLI evidence where available.
>
> Do not treat ordinary coding failures, permission denials, malformed checkpoints, network ambiguity or unknown errors as model exhaustion.
>
> Unknown or contradictory evidence must fail closed and preserve evidence rather than guessing.
>
> TURNOVER REQUIREMENTS
>
> For a confirmed Fable 5 exhaustion event:
>
> - acquire the existing single-instance/continuation lock;
> - preserve the stopped process output and journal;
> - prove that no surviving Fable worker or competing orchestrator remains;
> - record the exact last safe checkpoint;
> - select only "claude-opus-4-8";
> - launch exactly one Opus 4.8 xhigh successor;
> - load the current SESSION_HANDOFF and relevant task/controller state;
> - resume the unfinished task from the correct safe seam;
> - maintain an audit record connecting the stopped Fable execution to the Opus successor;
> - prevent repeated turnover if the same exhaustion event is observed more than once;
> - prevent duplicate workers, duplicate commits and duplicate external effects;
> - stop safely if Opus 4.8 is also unavailable.
>
> Do not select Opus 5, Sonnet or another model without a separate owner decision.
>
> COVER BOTH EXECUTION LAYERS
>
> The implementation must address both:
>
> 1. Main orchestrator exhaustion:
>    the independently live launcher/watchdog starts or resumes the Opus 4.8 orchestrator with the durable handoff.
>
> 2. Supervised worker exhaustion:
>    the controller records the failed Fable worker, verifies no child survives and redispatches the same bounded unit exactly once on Opus 4.8 from its safe starting checkpoint.
>
> PROTECTED MODEL AUTHORIZATION
>
> I authorize one narrow protected-config change required for this implementation:
>
> Add exactly ""claude-opus-4-8"" to "[claude].allowed_models" in:
>
> C:\Program Files\SupervisorConfig\config.toml
>
> This supersedes R297 only for that exact allowlist addition. No other protected configuration value may change.
>
> Keep:
>
> - "controller.default_mode = "shadow"";
> - active authorized runtime = supervised;
> - LIMITED-AUTO unauthorized and off;
> - Codex model configuration unchanged;
> - all command, filesystem, credential and approval protections unchanged.
>
> Use the existing tested protected-config update and DACL-hardening procedure.
>
> Before any live protected-file modification:
>
> 1. Capture this directive durably.
> 2. Prepare the exact before/after configuration diff.
> 3. Prove that only the one allowlist value changes.
> 4. Calculate and record the proposed new SHA-256.
> 5. Run the existing full-vector dry-run.
> 6. Return one exact elevated command for me to paste.
> 7. Stop for my elevated application.
>
> Do not ask me to hand-edit TOML, reconstruct commands or run arbitrary recursive "icacls" instructions.
>
> After I perform the elevated apply, require the full unelevated doctor proof:
>
> - exact configuration content matches the staged file;
> - SHA-256 matches the new recorded value;
> - protected file ACL state = PROTECTED;
> - protected parent ACL state = PROTECTED;
> - intended three-principal DACLs remain;
> - config remains readable;
> - mutable model_selection.toml remains writable;
> - explicit "claude-opus-4-8" selection is accepted;
> - default mode remains shadow;
> - active runtime authorization remains supervised;
> - LIMITED-AUTO remains off.
>
> Stop if any proof fails.
>
> TESTING REQUIREMENTS
>
> M0-T054 must include deterministic executable tests for:
>
> - exact Fable quota-message classification;
> - structured quota/usage-limit result classification;
> - normal Fable completion producing no turnover;
> - ordinary worker failure producing no turnover;
> - permission denial producing no turnover;
> - unknown/ambiguous failure stopping safely;
> - configuration reload after a protected allowlist change;
> - exactly-one Opus successor launch;
> - correct full model identifier "claude-opus-4-8";
> - xhigh effort selection;
> - handoff and checkpoint restoration;
> - audit linkage between Fable and Opus executions;
> - single-instance locking;
> - duplicate-event suppression;
> - duplicate-worker prevention;
> - duplicate-commit/external-effect prevention;
> - surviving-child detection;
> - Opus-unavailable safe failure;
> - process restart/reboot recovery where supported by the existing launcher;
> - supervised worker redispatch on Opus;
> - main-orchestrator successor startup on Opus.
>
> Use controlled fake-provider/process fixtures first. Then perform one bounded live proof using the currently exhausted Fable state on an isolated non-product runtime. The live proof must not duplicate M2-T015 work or mutate production data.
>
> A successful proof must demonstrate:
>
> Fable launch/probe
> → grounded weekly-limit hard stop detected
> → Fable process accounted for
> → exactly one Opus 4.8 xhigh successor launched
> → durable handoff loaded
> → safe checkpoint identified
> → continuation action reached
> → no owner "/model" or recovery prompt required.
>
> Do not claim success from unit tests alone. Do not claim mid-session continuity merely because Opus can be selected manually.
>
> SCOPE AND SEQUENCING
>
> Keep M0-T054 narrowly limited to model-exhaustion detection, lawful model authorization, exactly-once successor launch and safe continuation.
>
> Do not redesign the supervisor.
>
> Do not expand LIMITED-AUTO.
>
> Do not reopen unrelated ACL, controller or infrastructure work.
>
> Do not lose or repeat the completed M2-T015 work at task commit "1e4125c".
>
> Sequence:
>
> 1. Capture this owner directive.
> 2. Move M0-T054 from BACKLOG to the appropriate active/blocked-for-owner state.
> 3. Implement and test everything possible without the protected-file apply.
> 4. Stage the one protected allowlist change and return the exact elevated command.
> 5. After my apply, run the full protection/selection proof.
> 6. Complete the bounded live Fable-to-Opus turnover proof.
> 7. Run M0-T054’s required independent reviews, gates and acceptance.
> 8. Resume M2-T015 unit 3k automatically on Opus 4.8.
> 9. Complete M2-T015’s tests, reviews, PR and acceptance.
> 10. Continue to M2-T016 under supervised-auto. LIMITED-AUTO remains off.
>
> RETURN BEFORE ASKING FOR ANY NEW PRODUCT DECISION
>
> Return:
>
> 1. the exact M0-T054 implementation files;
> 2. its test results;
> 3. the deterministic and live turnover evidence;
> 4. the new protected-config SHA and doctor proof;
> 5. proof of the actual Opus 4.8 successor model;
> 6. proof that no duplicate worker/commit occurred;
> 7. proof that M2-T015 resumed from its correct checkpoint;
> 8. any genuine remaining blocker requiring owner authority.
>
> This is an implementation order, not another request to create a future task.

## Capture annotations (orchestrator, non-authoritative)

- Supersedes the source-027 R302 scheduling (M0-T054 "after M2-T015 acceptance"): M0-T054 is now
  an IMMEDIATE BLOCKING dependency of M2-T015 unit 3k.
- Re-authorizes and re-scopes the same protected allowlist addition as source-027's owner-decision
  message; still narrowly supersedes R297 for exactly `claude-opus-4-8` in `[claude].allowed_models`.
- The turnover controller is a supervisor-lane change under `.claude/rules/supervisor-freeze.md`;
  qualifying evidence (AD-093) = the reproduced R289 defect + the inability to complete authorized
  product task M2-T015 unit 3k. Standard gates (G0/G2/G3/G5); SHADOW-ONLY, LIMITED-AUTO OFF unchanged.
- "ACTIVATED" here = the turnover watchdog is live/proven, NOT any expansion of LIMITED-AUTO or the
  R595 activation path, both of which remain unchanged.
