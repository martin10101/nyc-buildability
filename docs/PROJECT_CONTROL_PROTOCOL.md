# Project Control Protocol

## Source of truth

Chat transcripts and agent memory are not the project-management source of truth. The source of truth is:

- `project-control/master_plan.json`
- `project-control/state.json`
- `project-control/tasks/*.json`
- `project-control/reports/*.json`
- `project-control/gates/*.json`
- `project-control/checkpoints/*.json`
- `project-control/blockers/*.json`
- Git history and CI/deployment evidence

## Authority rules

- Producer agents may update only their own task progress and create reports.
- Review agents may create gate reports but may not edit implementation.
- Only the orchestrator may accept tasks, alter dependencies, change milestones, or replan the backlog.
- Every status transition must be recorded by `tools/project_control.py` where supported.

## Task packet fields

Every task must define:

- `task_id`
- `title`
- `task_type`
- `milestone_id`
- `objective`
- `business_reason`
- `inputs`
- `outputs`
- `dependencies`
- `allowed_paths`
- `forbidden_paths`
- `acceptance_scenarios`
- `required_gates`
- `producer_agent`
- `reviewer_agents`
- `status`
- `progress_percent`
- `risks`
- `blockers`
- `created_at`
- `updated_at`

## Progress reporting

Progress is evidence-based, not intuition-based.

Use these markers:

- 0% — not started
- 10% — task claimed; scope and dependencies verified
- 20% — acceptance scenarios written
- 40% — core implementation exists
- 60% — producer happy path works
- 75% — all producer scenarios run
- 85% — submitted to independent gate
- 95% — all required independent gates passed
- 100% — orchestrator accepted and integration checkpoint recorded

An agent may never report 100% for its own task.

## Orchestrator re-planning triggers

Replan when:

- A gate fails
- API research contradicts assumptions
- A schema or legal dependency changes
- A task discovers new work
- Two tasks overlap
- A blocker appears or clears
- The critical path changes
- Integration creates regressions
- Project state has not been reconciled in the current session

## Re-planning output

The orchestrator must:

1. Update affected task status and dependencies.
2. Create defect/rework/new tasks.
3. Identify tasks that are newly ready or no longer ready.
4. Reassign agents based on specialization and file scope.
5. Update milestone risk and completion estimate qualitatively.
6. Record a checkpoint explaining why the plan changed.

## Worktree/branch convention

- Branch: `task/<task-id>-<short-name>`
- Worktree: `.claude/worktrees/<task-id>` when Claude-managed worktree isolation is available
- One task per branch
- No direct producer merge to main
- Merge only after required gates pass

## Communication contract

Subagents return a concise summary to the orchestrator and save the complete report in `project-control/reports/`. The orchestrator does not depend on hidden subagent reasoning.
