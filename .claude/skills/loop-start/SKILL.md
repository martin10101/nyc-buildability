---
name: loop-start
description: "Start (or idempotently report) the supervised agent loop via the external supervisor CLI. The documented 'Start the agent loop' owner intent (D-024 R035)."
disable-model-invocation: true
---

# /loop-start — thin owner control over the external supervisor (D-024 M0-T094; R083/R158)

User-only (the model may not invoke this). Normally the literal `/loop-start` input is intercepted
BEFORE the model by `.claude/hooks/loop_command_interceptor.py`, which runs the external
supervisor CLI directly and displays the bounded result - the command and its output never enter
the model transcript. If you (the model) are reading this, interception did NOT fire.

Fallback procedure - exactly one command, nothing else:

1. From the repository root run via Bash (never a shell string with interpolation):
   `python -m tools.agent_supervisor start`
2. Show its output verbatim (it is already redacted and bounded by the CLI). Add no commentary.
3. State honestly: "this fallback ran inside the model session and consumed context; the
   zero-context paths are the pre-model interception hook or a second terminal running the same
   command."

'Start the agent loop' = this command (R035). Start is idempotent: a running campaign is
REPORTED, never duplicated, and no duration parameter exists (R027/R036). Without explicitly
named executables/config/task-packet it performs only the safe pre-dispatch sequence and reports.

This is NOT the built-in `/loop` command (no collision; R159). Never substitute `/btw`.
