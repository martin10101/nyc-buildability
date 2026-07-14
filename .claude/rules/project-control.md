---
paths:
  - "project-control/**"
---

The project-control directory is authoritative. Producer agents may create only their own report files and must not run the control CLI. Reviewer agents are read-only: they return report content and a PASS/FAIL/BLOCKED verdict to the orchestrator and never run write-producing commands. All `tools/project_control.py` invocations (new-task, claim, progress, submit, gate, accept, checkpoint) are executed by the main-session orchestrator after validating the underlying evidence. Only the orchestrator may mark tasks accepted, change dependencies, modify the master plan, or unlock tasks. (Process decision ADR-005, 2026-07-14.)
