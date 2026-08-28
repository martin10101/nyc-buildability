---
name: loop-codex
description: "Persistent same-terminal Codex-only discussion channel: new/continue/show/promote/close threads with the read-only Codex supervisor."
argument-hint: "new <question> | continue <thread-id> <message> | show <thread-id> | promote <message-id> | close <thread-id>"
disable-model-invocation: true
---

# /loop-codex — persistent Codex discussion channel (D-024 Amendment 8, M0-T110; R233–R240)

User-only (the model may not invoke this). Normally the literal `/loop-codex` input is intercepted
BEFORE the model by `.claude/hooks/loop_command_interceptor.py`, which runs the external
supervisor CLI directly and displays the bounded result — the command and its output never enter
the model transcript. If you (the model) are reading this, interception did NOT fire.

Fallback procedure — exactly one command, nothing else:

1. From the repository root run via Bash (never a shell string with interpolation):
   `python -m tools.agent_supervisor codex <subverb> [...] --codex-executable <path> --config <path> --model-selection <path>`
   (`show`/`promote`/`close` take no provider inputs.)
2. Show its output verbatim (it is already redacted and bounded by the CLI). Add no commentary.
3. State honestly: "this fallback ran inside the model session and consumed context; the
   zero-context paths are the pre-model interception hook or a second terminal running the same
   command."

Threads persist durably; every turn sends Codex ONLY a bounded summary, recent exchanges, fresh
supervisor/campaign state, and stable evidence references — Codex reads the repository read-only
for anything deeper. Replies carry one disposition (ADVICE_ONLY, QUEUE_NEXT_BOUNDARY,
REVISE_CURRENT_TASK, PROPOSE_NEW_TASK, URGENT_PAUSE, STOP_FOR_OWNER); nothing is actuated or
promoted automatically — `promote` records YOUR approval durably, and scope changes still require
directive/task capture.

Honest limitation (R233): this is an ordinary custom command — submitted while Claude is
responding it is QUEUED until the turn ends. It is NOT `/btw` and is never claimed to be
(no measured equivalence exists). The real-time path while a turn is running is a second
terminal running the same `codex` commands. This is NOT the built-in `/loop` command (R159).
