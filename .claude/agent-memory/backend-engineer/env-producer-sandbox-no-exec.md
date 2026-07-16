---
name: env-producer-sandbox-no-exec
description: Producer worktree sandboxes deny ALL Bash execution (even `python script.py`); plan for orchestrator-captured evidence from the start
metadata:
  type: project
---

In this project's producer worktree sandboxes, the Bash tool is permission-denied for every invocation tried (inline `python -c`, `python <script>` with absolute path, compound `cd; python`). Observed 2026-07-15 during M0-T009.

**Why:** Harness permission policy for producer agents; consistent with the 2026-07-15 owner directive in `.claude/rules/project-control.md` (orchestrator captures executable evidence when a sandbox cannot run commands).

**How to apply:** Do not budget G2 time around running self-checks locally. Instead: (1) make every self-check a committed, argument-free script the orchestrator can run verbatim; (2) design validators so expected-failure cases are exercised by the NORMAL run (e.g. `fixtures/invalid/` directories the script expects to fail), so one command captures positive and negative evidence; (3) desk-check code paths by hand and record exact expected outputs in the producer report; (4) record the verbatim denial once and stop retrying. Grep/Glob/Read still work for read-only verification (ripgrep supports `\x{2019}`-style unicode escapes for byte-level checks).
