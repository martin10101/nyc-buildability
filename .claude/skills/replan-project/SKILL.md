---
description: Reconciles actual repository evidence with the master plan and redistributes work after gates, blockers, discoveries, or session restarts.
---

1. Run `python tools/project_control.py status`.
2. Inspect git/CI/deployment reality, active reports, gates, blockers, and checkpoints.
3. If this replan is triggered by new owner information, a correction, a PR-review amendment, or a "fix everything" request, **first** invoke `/directive-compliance` to capture it as a durable directive/amendment (stable ID, verbatim source, hash) **before** changing anything. Every resulting plan edit, rework/defect/split task, and master-plan change must cite that directive's requirement IDs.
4. Mark stale or invalid assumptions.
5. Create rework, defect, research, or split tasks as needed.
6. Recompute ready tasks from dependencies.
7. Assign agents with non-overlapping scopes.
8. Record the plan change and checkpoint.
9. Return a concise critical-path summary.
