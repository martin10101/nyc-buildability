---
description: Creates or claims a tightly scoped tracked task with acceptance scenarios and gate requirements. Use before any implementation or research work.
---

1. Read project state and dependencies.
2. Confirm the task is `ready` and has no unresolved blockers.
3. Confirm exclusive file scope and worktree/branch.
4. Ensure the task packet includes acceptance scenarios from `docs/ACCEPTANCE_SCENARIO_STANDARD.md`.
5. Claim through `python tools/project_control.py claim ...`.
6. Update progress to 10%, then 20% only after scenarios are recorded.
7. Do not perform untracked work.
