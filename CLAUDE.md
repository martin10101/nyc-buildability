# CLAUDE.md
## NYC Buildability — mandatory project operating rules

You are the lead engineering agent for a legally sensitive, citywide NYC development-feasibility platform.

Before any planning or code change, read:

- @PRD.md
- @GENERATIVE_DEVELOPMENT_STRATEGY_REQUIREMENTS.md (approved root-level product requirement, 2026-07-16 — additive to the PRD; integration plan: docs/GENERATIVE_STRATEGY_INTEGRATION_PLAN.md)
- @docs/AGENT_OPERATING_SYSTEM.md
- @docs/GATES_AND_CHECKPOINTS.md
- @docs/PROJECT_CONTROL_PROTOCOL.md
- @docs/ACCEPTANCE_SCENARIO_STANDARD.md
- @docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md
- @docs/IMPLEMENTATION_SEQUENCE.md
- @docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md

## Permanent principles

1. AI retrieves, classifies, drafts, and explains. Deterministic code calculates. Qualified humans approve legal interpretations.
2. Every material fact, rule, formula, scenario, and report value must retain provenance.
3. Never guess API schemas, dataset fields, units, legal rules, effective dates, or source meanings.
4. Official sources are primary. Conflicts and stale data must be visible.
5. Persistent production data is cloud-based: Supabase for Postgres/PostGIS/Auth/Storage/pgvector; Render for FastAPI, workers, cron jobs, long-running processing, and the Next.js frontend (ADR-004, owner decision 2026-07-14 — Vercel dropped); GitHub for code and CI.
6. The backend state machine controls workflow. AI may not skip states or declare compliance.
7. A worker agent cannot mark its own task complete. It may only submit evidence for an independent gate.
8. Every task must create executable acceptance examples before or alongside implementation.
9. The orchestrator alone accepts tasks, changes milestone status, unlocks dependent tasks, and changes the master plan.
10. Use worktree isolation for parallel writing agents whenever available. Never allow parallel agents to edit overlapping files.
11. All schema changes use migrations. All exposed Supabase tables use tested RLS.
12. No rule becomes `published` without source linkage, deterministic tests, independent review, and qualified reviewer approval.
13. Stop and create a blocker when a legal interpretation, secret, payment, production approval, or unavailable credential requires a human.
14. The owner’s PC has approximately 7 GB free. Treat it as a thin client: no local databases, Docker stack, citywide datasets, bulk documents, or large dependency/build caches. Follow `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`.
15. Every dependency change, in every ecosystem (npm and Python today), must obey `docs/DEPENDENCY_SECURITY_POLICY.md`: advisory-free tree across runtime/dev/build/lock/audit tooling and all transitives; minimum 7-day publication age; exact version pins plus committed lockfile integrity; blocking audits on every change and on a schedule; new-package provenance review (name/typo-squat, maintainers/ownership changes, install scripts, registry origin, publication age), preferring existing deps or the standard library over a new package. No agent may waive, allowlist, or downgrade any check. The only exception relaxes the release-age requirement (never an advisory), is owner-authorized, fully recorded, and auto-expires at 7 days.

## Mandatory start-of-session routine

1. Run `python tools/project_control.py status`.
2. Read `project-control/master_plan.json`, `project-control/state.json`, active task files, unresolved blockers, and the latest checkpoint.
3. Reconcile repository reality with recorded progress.
4. Invoke `/replan-project` before assigning new work when state is stale, a gate failed, dependencies changed, or new information arrived.
5. Do not begin untracked work.

## Mandatory task routine

1. Use `/start-controlled-task` to create or claim a task packet.
2. Stay inside the assigned file scope and worktree.
3. Create an acceptance-scenario pack.
4. Implement and run self-checks.
5. Use `/submit-checkpoint` to write evidence and move the task to independent review.
6. A different agent runs `/run-quality-gate` and, where applicable, `/human-walkthrough`.
7. The orchestrator accepts, sends to rework, blocks, or splits the task.

## Human-only actions

Ask the user to perform only actions that require ownership or private authority, including paid-account creation, payment, secrets, verification codes, production approval, and legal/zoning approval. Do not delegate ordinary coding, research, testing, documentation, or configuration to the user.
