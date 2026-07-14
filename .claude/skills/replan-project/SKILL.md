---
description: Reconciles actual repository evidence with the master plan and redistributes work after gates, blockers, discoveries, or session restarts.
---

1. Run `python tools/project_control.py status`.
2. Inspect git/CI/deployment reality, active reports, gates, blockers, and checkpoints.
3. Mark stale or invalid assumptions.
4. Create rework, defect, research, or split tasks as needed.
5. Recompute ready tasks from dependencies.
6. Assign agents with non-overlapping scopes.
7. Record the plan change and checkpoint.
8. Return a concise critical-path summary.
