---
name: loop-ask
description: "Ask the read-only Codex supervisor a bounded question about campaign state; a timeout returns a durable request ID."
argument-hint: "<question>"
disable-model-invocation: true
---

# /loop-ask — thin owner control over the external supervisor (D-024 M0-T094; R083/R158)

User-only (the model may not invoke this). Normally the literal `/loop-ask` input is intercepted
BEFORE the model by `.claude/hooks/loop_command_interceptor.py`, which runs the external
supervisor CLI directly and displays the bounded result - the command and its output never enter
the model transcript. If you (the model) are reading this, interception did NOT fire.

Fallback procedure - exactly one command, nothing else:

1. From the repository root run via Bash (never a shell string with interpolation):
   `python -m tools.agent_supervisor ask "<question>" --codex-executable <path> --config <path> --model-selection <path>`
2. Show its output verbatim (it is already redacted and bounded by the CLI). Add no commentary.
3. State honestly: "this fallback ran inside the model session and consumed context; the
   zero-context paths are the pre-model interception hook or a second terminal running the same
   command."

The three provider inputs must be named explicitly (nothing is discovered from PATH). If they are
not known in this session, print the command above for the owner's second terminal instead of
guessing paths. A timeout prints a durable request id; read it later with `ask --show <id>` or
re-pose with `ask --resubmit <id>` - never a background duplicate (R085/R087).

This is NOT the built-in `/loop` command (no collision; R159). Never substitute `/btw`.
