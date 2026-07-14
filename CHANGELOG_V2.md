# Version 2 — Full Production Agent-Control Update

## Changed

- Replaced Railway with Render throughout the architecture.
- Removed accelerated/prototype delivery framing.
- Added the crisp four-stage user flow and deterministic analysis state machine.
- Added one canonical property-profile contract requirement.
- Added bounded AI-task rules so AI cannot control the entire legal/data workflow in one prompt.

## Added

- Agent operating system modeled after a construction-management hierarchy.
- Producer/reviewer separation: agents cannot approve their own work.
- G0–G7 readiness, source, self-check, human-walkthrough, integration, security, legal, and release gates.
- Mandatory executable acceptance-scenario packs for connectors, GIS, legal rules, optimization, UI, and AI pipelines.
- File-based project control plane for milestones, tasks, reports, gates, checkpoints, and blockers.
- `tools/project_control.py` for deterministic claims, progress, submissions, gates, acceptance, checkpoints, and status.
- Claude Code skills for bootstrapping, controlled tasks, checkpoints, source verification, independent gates, human walkthroughs, replanning, and status.
- New independent reviewer agents: data-contract verifier, human-journey reviewer, and progress auditor.
- Worktree-isolation and continuous orchestrator replanning policies.
- Full-production milestone sequence through citywide data, legal corpus, rules, scenario optimization, release, and Revit integration.

## Tested

A complete temporary task lifecycle was executed successfully through readiness, production, submission, independent gates, and orchestrator-only acceptance. The final ZIP archive passed integrity testing.
