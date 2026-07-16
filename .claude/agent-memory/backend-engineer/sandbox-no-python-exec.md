---
name: sandbox-no-python-exec
description: STALE AS A UNIVERSAL RULE - some 2026-07-15 producer sessions denied python exec, but M1-T002 (2026-07-16) allowed it; see env-producer-sandbox-no-exec for the probe-first protocol
metadata:
  type: project
---

Historical observation (2026-07-15, M0-T005): that session's producer sandbox permission-denied Bash execution of Python scripts in every form (`python script.py`, absolute path, `python -c`), plus some compound pipelines. Read-only git, `ls`, `rm`, `python --version`, and Grep/Glob/Read/Write worked.

**Superseded as a universal rule:** the M1-T002 producer session (2026-07-16) ran python, pytest, ruff, and live curl without any denial (while `rm` was denied there). Sandbox profiles vary per session.

**How to apply:** do not assume denial or permission - follow the probe-first protocol in [[env-producer-sandbox-no-exec]]. The fallback techniques recorded here (Grep-based static evidence, orchestrator-runnable script lists, recording exact denial text) remain the right playbook FOR sessions where the probe fails.
