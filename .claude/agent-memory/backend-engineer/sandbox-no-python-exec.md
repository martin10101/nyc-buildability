---
name: sandbox-no-python-exec
description: Producer sandbox denies executing Python scripts (any invocation form); plan G2 evidence via orchestrator capture + ripgrep-equivalent static checks
metadata:
  type: project
---

The backend-engineer producer sandbox in this project permission-denies Bash execution of Python scripts in every form (`python script.py`, absolute path, `python -c`/runpy), and also denies some compound pipelines (e.g. `... | wc -l` chained with grep). Read-only `git` commands, `ls`, `rm`, `python --version`, and the dedicated Grep/Glob/Read/Write tools work fine.

**Why:** Observed 2026-07-15 during M0-T005 (secret scanner). Four invocation forms denied; per ADR-005 brief this forces requested status `blocked` with exact denials recorded, and the orchestrator captures executable G2 evidence itself.

**How to apply:** When a task requires running a script for self-checks, do not burn attempts: (1) build static evidence with the Grep tool using the identical regexes/assertions, (2) write the exact orchestrator command list with expected outputs into the producer report, (3) record the exact denial text, (4) request `blocked` (or note the gap) instead of claiming executed evidence. Single-purpose read-only git commands are the reliable way to capture status/diff evidence.
