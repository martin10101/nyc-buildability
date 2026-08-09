# D-010 source-026 — Foreground-timeout raise + Fable-exhaustion orchestrator fallback test (owner, 2026-08-09)

Captured verbatim from the owner's session message (Claude Code interactive session,
2026-08-09, following the session-9 report on harness background kills and the
10-minute foreground cap; frozen base SHA `f70449d1cc8dc6566b5e79a4c9603326b883a656`).
The owner had just been given the recommendation to raise the foreground Bash timeout
cap via settings. Immediately before this message the owner ran `/context` (334.7k/1M
tokens shown). Typos preserved exactly.

## Verbatim owner text

> raise the foreground timeout cap
> do it 
> also,worth noting fable 5 is at 98% of weekly allowance it will hit 100% probably in middle of your fix or right after this isnthe oprtunity to see if the program will switch to opus 4.8 xhight to take over the main orchestrator job without me needing to tell it(it should pickup the notification from cc and act on it to switch and continue on ) then next week when I get more credits I will tell it to switch main back to fable 5 I wanna know if the program is designed to work lile this and if u can somehow log whats about to happen to see if it did it correctly

## Capture annotations (orchestrator, non-authoritative)

- "raise the foreground timeout cap / do it" authorizes the recommended settings change
  (`BASH_MAX_TIMEOUT_MS` and companion default in the checked-in `.claude/settings.json`
  `env` block) so supervised foreground units get a window larger than 600 s.
- "opus 4.8 xhight" read as `claude-opus-4-8` with `xhigh` effort — identical to the
  standing reviewer-fallback pair (owner 2026-08-05, recorded in the reviewer agent
  files and session memory).
- "take over the main orchestrator job without me needing to tell it" is an
  authorization for orchestrator-role continuity on `claude-opus-4-8` xhigh during the
  Fable 5 exhaustion window, superseding the D-004 `claude-fable-5` settings-model pin
  FOR THAT WINDOW ONLY; the owner's typed switch-back instruction next week reverts it.
- Interpretation surfaced (not silent): "act on it to switch and continue on" is read
  as also covering the supervised-auto WORKER model (mutable
  `C:\SupervisorController\model_selection.toml`), because M2-T015 continuation is
  impossible with a Fable-pinned worker while Fable is exhausted, and the same
  owner-established fallback pair already governs reviewers. This reading is listed as
  its own requirement so the owner can strike it if unintended.
- "log whats about to happen to see if it did it correctly" = pre-registered
  expectation record + post-hoc verification with primary evidence (session transcript
  model IDs, supervisor audit `observed_models`, ledger continuity entries).
