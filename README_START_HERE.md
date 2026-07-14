# NYC Buildability — Full Production Claude Build Pack

This repository pack is an operating system for Claude Code to build the complete NYC Development Feasibility and Zoning Intelligence Platform.

## Included

- Full citywide product PRD
- Supabase + Render + Vercel + GitHub architecture
- Crisp four-stage analyst flow and deterministic analysis state machine
- Project subagents with isolated responsibilities
- Skills for task control, checkpoints, source verification, independent gates, human walkthroughs, status, and replanning
- File-based project control plane
- Deterministic task/gate CLI
- Acceptance-scenario standards for APIs, GIS, rules, AI, optimization, UI, security, and reports
- Independent reviewer model where producers cannot approve their own work


## Critical local-storage constraint

The owner’s PC has only about **7 GB free**. Do not set up the full development environment on that PC. Use it only as a thin client.

Preferred working model:

- Claude Code and dependency-heavy work in GitHub Codespaces or another remote development machine
- Builds/tests in GitHub Actions
- Persistent data and files in Supabase
- Processing and workers on Render
- Frontend deployments on Vercel

Do not install Docker Desktop, local Supabase/PostgreSQL, citywide NYC datasets, or large package/build caches on the owner’s PC. Read `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md` before bootstrapping.

## First use

1. Extract the pack into the root of a new private GitHub repository.
2. Install/start Claude Code from the repository root.
3. Run `/doctor` to inspect configuration when available.
4. Give Claude this instruction:

```text
Read CLAUDE.md and every file it imports, especially docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md. This is a full-production build. The owner’s PC has only about 7 GB free, so treat it as a thin client and perform dependency-heavy development, builds, testing, data imports, and processing in approved cloud environments. Run /bootstrap-project, reconcile the project-control state, and use the orchestrator. Do not write application code until M0 has precise task packets, acceptance scenarios, exclusive file scopes, and G0 readiness. Every producer must submit evidence; independent agents must rerun human-style gates; only the orchestrator may accept work and unlock dependencies. Continuously replan from gate results and blockers.
```

5. Claude should run:

```bash
python tools/project_control.py init
python tools/project_control.py status
```

6. You personally provide paid accounts, credentials, verification codes, production approvals, pilot/validation property information, and qualified legal/zoning approvals when requested.

## Cloud services

- Supabase: Postgres/PostGIS/Auth/Storage/pgvector
- Render: FastAPI Web Service, background workers, cron jobs, one-off processing
- Vercel: Next.js frontend
- GitHub: source control and CI

## Important completion rule

A worker agent may never mark its own work complete. It submits an evidence report. A separate reviewer reproduces the work from acceptance criteria and records a gate result. Only the orchestrator may mark a task accepted.
