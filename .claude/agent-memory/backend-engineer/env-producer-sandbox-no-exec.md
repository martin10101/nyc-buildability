---
name: env-producer-sandbox-no-exec
description: Producer sandbox permissions VARY BY SESSION - probe cheaply first; M0/M1-T001 sessions denied all exec, M1-T002 allowed python+pytest+live network but denied rm
metadata:
  type: project
---

Producer-session sandbox capabilities are NOT constant across sessions. Observed history:

- 2026-07-15 (M0-T005, M0-T009) and the M1-T001 producer session: ALL Bash execution of Python denied in every invocation form -> orchestrator evidence-capture rule (ADR-005) applied; see [[sandbox-no-python-exec]].
- 2026-07-16 (M1-T002 producer session): python 3.11.9, pytest 8.4.2, jsonschema 4.26.0, ruff 0.9.9, and curl WITH live network all worked first try; full offline test suite executed locally. Denied instead: `rm -rf` (even for an OS-temp dir) and any compound command containing it. Also: the Bash tool runs git-bash even though the env block claims PowerShell - `Get-ChildItem` etc. fail; use POSIX commands.
- 2026-07-16 (M1-T006 producer session): same full-exec profile as M1-T002 (python/pytest/ruff/git all fine). Gotcha: `/tmp` persistence across Bash calls is UNRELIABLE (one file written to /tmp vanished in the next call while another persisted; /tmp maps to %TEMP% via git-bash) - stage cross-call artifacts inside the worktree instead. Also: task worktrees cut before the orchestrator commits the packet may lack `project-control/tasks/<id>.json`; read it from the main checkout read-only.

**Why:** permission profiles are configured per launch by the orchestrator/owner. Assuming denial forfeits first-hand executable evidence; assuming permission wastes turns on denials.

**How to apply:** at session start run ONE cheap probe (`python --version` plus, if the task needs network, a single tiny curl) before planning around the evidence-capture fallback. Still design all tests offline-deterministic with injectable transports so they run anywhere. If `rm` is denied, disclose pending temp cleanup in the producer report instead of retrying. Local Python is 3.11.9 while services/api pyproject targets >=3.12 - keep code 3.11-compatible so local self-checks work (`datetime.UTC` exists in 3.11).
