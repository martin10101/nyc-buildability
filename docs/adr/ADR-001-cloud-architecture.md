# ADR-001: Cloud Architecture — Supabase + Render + Vercel + GitHub, Modular Monorepo, One FastAPI Service

- **Status:** Proposed (pending G3 gate review)
- **Date:** 2026-07-14
- **Producer:** cloud-architect (task M0-T006)
- **Deciders:** Human project owner (final), per PRD section 14.1 which mandates the providers
- **Related:** ADR-002 (environment separation), ADR-003 (deployment and rollback), `render.yaml`, `docs/DEPLOYMENT_AND_ROLLBACK.md`

## Context

The PRD requires a cloud-first architecture (PRD 14.1 "Required providers") and explicitly forbids a heavy local stack because the owner's PC has ~7 GB free disk (PRD 35, `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`). The product is a NYC development-feasibility platform with:

- PostGIS-heavy geospatial data, pgvector embeddings, RLS multi-tenancy (PRD 15–17)
- Long-running ingestion/GIS/AI-extraction/scenario jobs that must NOT run in serverless edge functions (PRD 14.2)
- A deterministic backend state machine that controls workflow, not the AI (PRD 32.5)
- A Next.js frontend with preview deployments (PRD 14.1)
- A complexity-containment rule: "Use one modular monorepo and one deployable FastAPI service plus scalable worker processes. Do not create microservices without a demonstrated isolation, scale, or security need." (`docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md`, "Complexity containment")

## Decision

Adopt the provider set mandated by PRD 14.1, with the following concrete shape:

| Concern | Provider | What runs there |
|---|---|---|
| Database (Postgres + PostGIS + pgvector), Auth, RLS, private Storage, migrations, audit | **Supabase** | All persistent data and documents; one project per environment (see ADR-002) |
| Python API + all heavy compute | **Render** | One FastAPI **web service**; **background worker(s)** for ingestion/GIS/AI/scenario jobs; **cron job(s)** for scheduled source monitoring — defined as code in `render.yaml` (Blueprint) |
| Web frontend | **Vercel** | Next.js app; preview deployments per PR; production promotion per ADR-002/003 |
| Source control, CI, secrets for CI, approvals | **GitHub** | Repo, PRs, GitHub Actions (remote builds/tests/migrations), GitHub environments |

Architecture rules:

1. **Modular monorepo.** One repository containing `apps/` (frontend), `services/api` (FastAPI + worker + job entrypoints), `packages/` (shared contracts). Internal modules are separated by versioned contracts (canonical property profile, rule traces, scenarios — PRD 32.3) so they can be extracted later if operational evidence justifies it.
2. **One deployable FastAPI service.** The API is a single Render web service. Workers and cron jobs are separate Render *service instances* built from the **same codebase** (`services/api`) with different start commands — they are not separate microservices. Render defines web services, background workers ("run continuously... they don't receive any incoming network traffic"), and cron jobs as distinct service types (Render service types docs: https://render.com/docs/service-types, https://render.com/docs/background-workers, https://render.com/docs/cronjobs — retrieved 2026-07-14).
3. **No heavy work in Supabase Edge Functions.** PRD 14.2: "Do not run large PDF parsing, GIS imports, full dataset ingestion, or lengthy AI extraction inside Edge Functions." Edge Functions remain permitted only for short authenticated endpoints/webhooks.
4. **Infrastructure as code.** Render resources are declared in `render.yaml` at the repository root ("By default, Render creates a Blueprint using the `render.yaml` file at your repository's root" — https://render.com/docs/infrastructure-as-code, retrieved 2026-07-14). Secrets are never literal in the file: every sensitive env var is declared with `sync: false`, which tells Render to prompt for the value at deploy time so "nothing sensitive lands in Git" (https://render.com/docs/blueprint-spec, retrieved 2026-07-14).
5. **Service-role key only in trusted backends.** Supabase service-role key exists only in Render/GitHub Actions secret stores, never in frontend code (PRD 17).

## Alternatives considered

### Railway (replaced by decision of record)
Railway was considered as a Render substitute for the API/worker tier during early planning and is **replaced by this decision of record**. Rejected because: (a) PRD 14.1 names Render as the required provider for the FastAPI API, workers, AI jobs, and scheduled monitoring — deviating would require a PRD change with owner approval; (b) the project has already validated Render-specific mechanisms this ADR set depends on (Blueprint IaC in Git, native cron/worker service types, dashboard/API deploy rollbacks — sources in ADR-003); (c) switching offers no capability this project needs that Render lacks, while re-validation of platform behavior would cost research and gate time. No official-doc capability claims about Railway are made or relied upon here.

### Fly.io
Machine-level control and global regions are not requirements for this product (single-region NYC-data workload). It would carry the same "not the PRD-mandated provider" deviation cost as Railway, with more infrastructure surface for a solo-owner project to operate. Rejected on PRD-compliance and operational-simplicity grounds; no official-doc claims about Fly.io capabilities are made or relied upon here.

### AWS (ECS/Fargate + RDS + Amplify or equivalent)
Maximum flexibility, maximum operational burden: VPCs, IAM, task definitions, migration tooling, and cost management are all owner-operated. This directly conflicts with the thin-client/low-ops constraint (PRD 35) and the delivery goal of a small number of managed dashboards. Rejected.

### Supabase-only (Edge Functions for compute)
Rejected by explicit PRD prohibition: PRD 14.2 forbids large PDF parsing, GIS imports, dataset ingestion, and lengthy AI extraction in Edge Functions and requires "container workers with resumable jobs" instead.

### Microservices on Render (one service per domain)
Rejected by the complexity-containment rule (`docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md`): contracts keep modules separable inside one FastAPI deployable; extraction happens only on demonstrated isolation/scale/security need.

## Consequences

Positive:
- Matches PRD 14.1 exactly; no deviation to document.
- All heavy compute and storage stay off the owner's PC (PRD 35 satisfied).
- `render.yaml` makes the Render topology reviewable, versioned, and reproducible.
- One codebase for API/worker/cron means one build pipeline and shared contracts.

Negative / accepted costs:
- **Multi-vendor operations:** three dashboards (Supabase, Render, Vercel) plus GitHub; three different rollback semantics — mitigated by ADR-003 and the `docs/DEPLOYMENT_AND_ROLLBACK.md` runbook.
- **Secrets exist in multiple secret stores** (Render env vars, Vercel env vars, GitHub Actions secrets, Supabase config). ADR-002 defines which secret lives where; `sync: false` keeps them out of Git.
- **Cost floor:** Render background workers and cron jobs have no free tier ("there is no free tier for background workers or cron jobs"; free web services "spin down after 15 minutes of inactivity") — https://render.com/docs/free and https://render.com/pricing, retrieved 2026-07-14. Cron jobs bill per-minute with a $1/month minimum per cron job (https://render.com/docs/cronjobs, https://render.com/pricing, retrieved 2026-07-14). ADR-002 sequences paid upgrades.
- Worker scaling is vertical/horizontal within Render service instances; if a workload later needs GPU or very large memory, that becomes a new ADR.

## Sources (platform-behavior claims; all retrieved 2026-07-14)

| Claim | Official source |
|---|---|
| Blueprint = `render.yaml` at repo root, IaC model | https://render.com/docs/infrastructure-as-code |
| `sync: false` env vars prompt at deploy, keep secrets out of Git | https://render.com/docs/blueprint-spec |
| Render service types incl. web, background worker, cron job | https://render.com/docs/service-types |
| Background workers run continuously, receive no inbound traffic | https://render.com/docs/background-workers |
| Cron job billing ($1/mo minimum, per-minute) and UTC schedules | https://render.com/docs/cronjobs, https://render.com/pricing |
| Free plan: web services spin down after 15 min; no free workers/cron | https://render.com/docs/free |
| Vercel preview/production deployment model | https://vercel.com/docs/deployments/environments |
| Supabase multi-environment migration workflow | https://supabase.com/docs/guides/deployment/managing-environments |

Verification method note: pages were retrieved on 2026-07-14 via web search against the official domains (direct page fetch was unavailable in the authoring session). Every claim above traces to the listed official page; anything not confirmable was excluded or marked for verification in ADR-002/003.
