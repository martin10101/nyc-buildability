# D-024 Amendment 9 — R187/R595 limited-auto activation authorization (owner instruction 2026-08-29)

Captured: 2026-08-29 UTC by the orchestrator (Fable 5), verbatim from the owner's interactive
message (channel: Claude Code interactive session, typed by the owner immediately after the
orchestrator presented the R187/R595 activation package at campaign seq 27). Base identity at
capture: branch `control/D-024-fable-codex-loop`, HEAD `00484a58e561a017bfd3712f76970fcc36c8142c`
(local == origin; clean tree; CI 20/20 green on acceptance tip `88b909d`). Amends: `source-001.md`
(owner directive v4). Requirement IDs assigned: D-024-R250..D-024-R260.

Reconciliation (recorded before any activation step):

- **This is the owner-gated R595 activation act itself** — the act sections 18/R187/R595 and the
  presented activation package reserved to the owner. Preconditions verified at capture: M0-T112
  accepted (R247 satisfied); the package was PRESENTED (seq 27) before this authorization; the
  authorization arrived in the owner's own typed words in the interactive session.
- **Supersession scope (explicit and narrow):** the standing "no continuous-mode activation"
  restriction rows (D-024 §18 posture; Amendment 3 R146's activation clause as restated by R248)
  are SATISFIED-BY-OWNER-ACT for exactly this authorization: `limited-auto` mode via the certified
  item-3 start command with the explicit per-launch `--owner-enable-bounded-auto`. Every OTHER
  prohibition in R146/R248 (Agent SDK, MCP servers, PR #241, global settings, owner boundaries)
  remains fully in force, and the amendment's own exclusion list (R257) re-affirms the remaining
  owner gates, including autostart-across-reboots and the live 4.8 bridge (shadow-only).
- **New tasks:** rows bind to NEW ledger task M0-T113 (activation act + first-loop operation
  proof); the residual-carry decision (R258) additionally binds M0-T114 (tracked follow-up,
  owner-scheduled, re-triggers R247 when executed).

Forward trace: preamble sentence ("Yes—authorize it as `limited-auto` …") + "I explicitly
authorize…" line → R250; "Durably record…" bullet → R251; "Run the complete activation
preflight…" bullet → R252; "Execute the exact certified start command…" bullet → R253; "Start
the loop now if—and only if—…" bullet → R254; "Codex may continuously select…" sentence 1 →
R255, sentence 2 ("…must continue to fail closed") → R256; "This authorization does not
include…" paragraph incl. "Keep the 4.8 bridge shadow-only." → R257; "Do not modify certified
supervisor code… Carry the nonblocking residuals…" paragraph → R258; "If any activation
precondition differs… stop and report the exact mismatch." paragraph → R259; "After starting,
prove operation beyond process launch and report:" + numbered items 1–7 → R260; trailing
paragraph ("This starts autonomous operation now… separate authorization.") → scope
clarification anchoring R250 (stops at protected owner decisions persist) and R257 (reboot
autostart remains separately owner-gated).

---VERBATIM-BEGIN---
Yes—authorize it as `limited-auto`, which is this project’s full bounded autonomous mode. Paste this to Claude Code:

> I explicitly authorize R187/R595 activation of the continuous Codex supervisor loop in `limited-auto` mode.
>
> You are authorized to:
>
> * Durably record this owner authorization.
> * Run the complete activation preflight against the certified package and current repository state.
> * Execute the exact certified start command from activation-package item 3, including `--mode limited-auto` and `--owner-enable-bounded-auto`.
> * Start the loop now if—and only if—the repository is clean, the certified identity and configuration match, and all required gates pass.
>
> Codex may continuously select bounded tasks from the durable campaign record, direct Fable to perform them, review and validate the results, and advance the campaign under the already-certified commit/push and exactly-once policies. Refusals, quota exhaustion, ambiguous effects, crashes, and rotations must continue to fail closed.
>
> This authorization does not include autostart across reboots, PR #241, production deployment, credentials, payments, legal decisions, OS-ACL changes, the C1 live-interception canary, Telegram live-send testing, natural-event graduation or live actuation of the 4.8 bridge, or fixing the three certification residuals. Those remain separately owner-gated. Keep the 4.8 bridge shadow-only.
>
> Do not modify certified supervisor code before activation. Carry the nonblocking residuals as tracked follow-up work.
>
> If any activation precondition differs from the certified package, do not improvise or partially activate; stop and report the exact mismatch.
>
> After starting, prove operation beyond process launch and report:
>
> 1. activation record and effective mode;
> 2. controller PID/session/run identity;
> 3. selected campaign task;
> 4. evidence of the first bounded dispatch;
> 5. status, pause, graceful-stop, and emergency-stop commands;
> 6. Telegram notification state;
> 7. whether anything is awaiting owner approval.

This starts autonomous operation now, but it will still stop at protected owner decisions. It also will not automatically restart after a computer reboot—that remains a separate authorization.
---VERBATIM-END---
