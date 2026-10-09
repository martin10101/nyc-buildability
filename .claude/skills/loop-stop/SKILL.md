---
name: loop-stop
description: "Graceful stop: finish only the smallest safe atomic unit already underway, land it, then stop (durable before acknowledgment)."
argument-hint: "[reason]"
disable-model-invocation: true
---

# /loop-stop — thin owner control over the external supervisor (D-024 M0-T094; R083/R158)

User-only (the model may not invoke this). Normally the literal `/loop-stop` input is intercepted
BEFORE the model by `.claude/hooks/loop_command_interceptor.py`, which runs the external
supervisor CLI directly and displays the bounded result - the command and its output never enter
the model transcript. If you (the model) are reading this, interception did NOT fire.

Fallback procedure - exactly one command, nothing else:

1. From the repository root run via Bash (never a shell string with interpolation):
   `python -m tools.agent_supervisor graceful-stop`
2. Show its output verbatim (it is already redacted and bounded by the CLI). Add no commentary.
3. State honestly: "this fallback ran inside the model session and consumed context; the
   zero-context paths are the pre-model interception hook or a second terminal running the same
   command."

This is the R034 'graceful stop after next safe checkpoint'. The immediate hard stop is
`python -m tools.agent_supervisor stop`; the strongest is /loop-emergency-stop. Precedence:
emergency > graceful > pause (unit-F stop_intent). Clear with `graceful-stop --clear`.

This is NOT the built-in `/loop` command (no collision; R159). Never substitute `/btw`.
