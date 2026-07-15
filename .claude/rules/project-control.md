---
paths:
  - "project-control/**"
---

The project-control directory is authoritative. Producer agents may create only their own report files and must not run the control CLI. Reviewer agents are read-only: they return report content and a PASS/FAIL/BLOCKED verdict to the orchestrator and never run write-producing commands. All `tools/project_control.py` invocations (new-task, claim, progress, submit, gate, accept, checkpoint) are executed by the main-session orchestrator after validating the underlying evidence. Only the orchestrator may mark tasks accepted, change dependencies, modify the master plan, or unlock tasks. (Process decision ADR-005, 2026-07-14.)

Evidence-capture division of labor (owner directive, 2026-07-15): read-only reviewers produce reports and verdicts; when a reviewer's sandbox cannot execute commands (gh, python, network), the orchestrator captures the executable evidence into committed `project-control/reports/` artifacts and the reviewer verifies the stored evidence instead. A reviewer must not return BLOCKED solely because it cannot execute commands or write to the ledger — it requests orchestrator-captured evidence and verifies it. Gate results are always recorded by the orchestrator.
