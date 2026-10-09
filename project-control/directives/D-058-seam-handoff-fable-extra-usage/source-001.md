# D-058 source-001 (original, verbatim) — owner directive via /session-handoff reason, 2026-09-14

Capture head: `89de37946a3ad3f8c542c03bbe70183742f048a9` (branch `candidate/D-024-mrl-option-b`).
Frozen origin/main baseline: `d8b3899f61efa6620e18a26541ced96020f5bef9`.
Captured by the orchestrator session while executing the owner's /session-handoff invocation
(D-054 precedent: a handoff reason carrying instructions is captured verbatim).

## owner-message-verbatim

> finish up at a seam let thee codex loop stay alive make sure to add the knowlge we learnd
> from this seasen in the right md files like we designd make sure the loop uses the extra
> useig fable (reg weekly just got used up)

## capture-context

- "finish up at a seam" = land the session per /session-handoff: reconcile every in-flight
  agent, commit only completed work, replace docs/SESSION_HANDOFF.md, push.
- "let thee codex loop stay alive" = the D-053 loop operation CONTINUES shift after shift.
  Live fact at capture: run persistent-local-34 had ALREADY closed on its own, benignly, at
  unit completion (audit seq 845 claude_unit_completed; seq 846 checkpoint refused on the
  known-benign worktree-field mismatch; work verified green and committed by the orchestrator
  at wt-m4t020 d7766b8d). "Stay alive" therefore means: the successor relaunches the loop on
  the next packet per the recorded per-task pattern (scratchpad/relaunch_m4t020.ps1 template;
  fresh run-id), with the D-053 posture unchanged (no auto-accept/merge, R595 shadow).
- "add the knowlge we learnd from this seasen in the right md files like we designd" = the
  D-054 two-tier system: append program-wide pointers to .claude/rules/PROGRAM_KNOWLEDGE.md
  (eager-budget-capped) and keep docs/WORKING_KNOWLEDGE.md current (prune-or-promote).
- "make sure the loop uses the extra useig fable (reg weekly just got used up)" = the owner
  states the REGULAR weekly Fable quota is now exhausted and AUTHORIZES continued
  claude-fable-5 operation through the account's EXTRA USAGE for the loop worker (and the
  D-055 reviewer set). Consequence: the model_selection.toml fable-5 pin STAYS — no
  D-036-R002-style opus manual actuation this cycle. The D-036/D-055 fallback chain
  (["claude-opus-4-8"] on reason_code quota_exhausted) remains armed ONLY as the last resort
  if extra usage also hard-stops; a hard stop under this directive is a fallback event, not a
  reason to flip the pin. Enabling/limiting extra usage itself is an owner account setting.
