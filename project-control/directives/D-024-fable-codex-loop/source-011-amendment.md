# D-024 Amendment 11 — first-run ASK disposition + no-restart-loop rule (owner instruction 2026-08-29)

Captured: 2026-08-29 UTC by the orchestrator (Fable 5), verbatim from the owner's interactive
message (typed in response to the M0-T113 activation-evidence report: first limited-auto cycle
fail-closed at three ASK-held read-only discovery commands, run `run_M0_T107_unitJ` in
`PAUSED_RECOVERY`). Base identity at capture: branch `control/D-024-fable-codex-loop`, HEAD
`f44a6c602b8442cf795d2efc3bca74fadd6667ea` (local == origin; clean tree). Amends:
`source-001.md` (owner directive v4). Requirement IDs assigned: D-024-R268..D-024-R271.

Reconciliation: the deny/clear/restart acts execute inside already-captured authority
(Amendment 9 R253/R254 — the SAME certified start command; PAUSED_RECOVERY exit via the
audited `clear-recovery` + explicit operator start is the documented S11.5 path; ASK answers
are owner touchpoints and the owner has now given them). NEW standing requirements captured
here: the no-repeated-restart rule with the correction-instead path (R270) and the
recertification linkage (R271). No policy loosening, no gate change, no R257 exclusion is
touched. Rows bind to M0-T113 (the activation act in flight).

Forward trace: paragraph 1 sentence 1 ("Deny all three… restart the loop using the same
certified limited-auto start command.") → R268; sentence 2 ("Do not loosen or bypass the
command policy.") → R268; sentence 3 ("Confirm the new run identity…") → R269; paragraph 2
("If routine discovery produces another ASK-stop… Keep that correction separate, preserve
all owner gates, and recertify before resuming autonomous operation if certification is
invalidated.") → R270 (sentences 1–3) and R271 (final clause); the "What should happen
next" list → expected-outcome anchors for R268/R269 (denied, cleared, fresh bounded run,
file-tools preference, checkpoint → automatic Codex review/continuation).

---VERBATIM-BEGIN---
Deny all three stale ASK requests, clear PAUSED_RECOVERY, and restart the loop using the same certified limited-auto start command. Do not loosen or bypass the command policy. Confirm the new run identity, live Fable 5 dispatch, current task, and whether it advances beyond the first checkpoint.

If routine discovery produces another ASK-stop, do not repeatedly restart. Stop safely and propose a bounded control-plane correction that directs workers toward the existing in-scope file tools or explicitly documented safe commands. Keep that correction separate, preserve all owner gates, and recertify before resuming autonomous operation if certification is invalidated.

What should happen next:

The old requests are denied.
Recovery state is cleared.
M0-T107 starts again in a fresh bounded run.
Fable should use its permitted file tools instead of shell commands.
If it reaches a structured checkpoint, Codex can review it and continue the loop automatically.
---VERBATIM-END---
