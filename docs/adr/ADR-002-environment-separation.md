# ADR-002: Environment Separation — dev / staging / prod

- **Status:** Proposed (pending G3 gate review)
- **Date:** 2026-07-14 (amended 2026-07-15: deploy-trigger model reworked per owner directive; G3 defects 2-5. Amended 2026-07-16 per ADR-004: frontend moved from Vercel to a Render web service `nycdf-web` — owner decision 2026-07-14; all Vercel mappings replaced below)
- **Producer:** cloud-architect (task M0-T006; ADR-004 amendments by task M0-T011)
- **Deciders:** Human project owner (final)
- **Related:** ADR-001 (providers), ADR-003 (deployment and rollback), ADR-004 (frontend hosting on Render), `render.yaml`

## Context

PRD Phase 0 requires "Dev/staging/production environments" and "Secret management" (PRD 26). Government data ingestion, legal-rule releases, and client analyses must never be tested against production data. Costs must stay near zero until launch (PRD 35; `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`). Environment separation must therefore use each provider's cheapest *safe* mechanism, based on official platform behavior only.

Key researched platform facts (all retrieved 2026-07-14):

- **Supabase — separate projects vs branches.** The official multi-environment guide supports "separate development, staging, and production environments" driven by "Database Migrations and GitHub Actions to automatically test and release schema changes to staging and production projects" (https://supabase.com/docs/guides/deployment/managing-environments). Branching (preview branches per PR, persistent branches for staging/QA) **requires the Pro Plan** (https://supabase.com/docs/guides/deployment/branching). Free plan allows **2 active projects**, and "Free projects are paused after 1 week of inactivity" (https://supabase.com/pricing, https://supabase.com/docs/guides/platform/free-project-pausing). Paid orgs include $10/mo compute credits (~one Micro instance); each additional always-on database costs $0.01344/hour (~$10/mo) (https://supabase.com/docs/guides/platform/manage-your-usage/compute, https://supabase.com/docs/guides/platform/manage-your-usage/branching).
- **Supabase — backups are plan-gated.** Daily backups exist on Pro/Team/Enterprise only (7/14/30 days retention); PITR is a Pro+ add-on (https://supabase.com/docs/guides/platform/backups). Production therefore cannot remain on the Free plan at launch.
- **Render — projects/environments.** Render lets you "organize your services by their application and environment (such as staging or production)", supports **protected environments** ("only your workspace's admins can make potentially destructive changes"; shell access restricted to Admins), can **block private-network traffic across an environment boundary**, and can scope an environment group (shared env vars/secrets) to a single project environment to "protect against accidentally connecting a staging service to a production database" (https://render.com/docs/projects, https://render.com/changelog/project-environment-groups — retrieved 2026-07-14).
- **Render — preview environments.** Blueprint `previews.generation: manual | automatic` creates per-PR copies of Blueprint services; Render "automatically destroys them when the original pull request is merged or closed"; `previews.expireAfterDays` adds inactivity expiry; previews are billed at the same rate as the base service and can use a smaller `previews.plan`; **`sync: false` env vars are not included in preview environments** (https://render.com/docs/preview-environments, https://render.com/docs/blueprint-spec — retrieved 2026-07-14).
- **Vercel — environments.** *(Superseded 2026-07-16 per ADR-004 — Vercel dropped; bullet retained for provenance only.)* Production deployments trigger on push/merge to the production branch; every other branch/PR gets a preview deployment; env vars can be scoped per environment and per Git branch for previews; **Custom Environments (e.g., a long-lived `staging`) require Pro or Enterprise** and support branch tracking (https://vercel.com/docs/deployments/environments — retrieved 2026-07-14).
- **GitHub — environment protection is plan-gated for private repos.** "If you are on a GitHub Free, GitHub Pro, or GitHub Team plan, required reviewers are only available for public repositories." Access to environments/environment secrets in private repos needs Pro/Team/Enterprise (https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments, https://docs.github.com/actions/deployment/targeting-different-environments/using-environments-for-deployment — retrieved 2026-07-14).

## Decision

### 1. Git branch model (drives everything else)

- `main` — integration branch; always releasable; deploys **staging**.
- `production` — protected release branch; fast-forwarded from `main` only during an approved promotion; deploys **production**.
- Feature branches + PRs into `main` — deploy **dev previews**.

### 2. Concrete environment mapping

| Environment | Supabase | Render (API/worker/cron) | Frontend (Render web service — amended 2026-07-16 per ADR-004; previously Vercel) | GitHub |
|---|---|---|---|---|
| **dev** | Free project `nycdf-dev` (Free-org slot 1). Accepts destructive experiments and seeded/mock data. | No always-on dev services. Per-PR **preview environments** with `previews.generation: manual` (opt-in per PR) to avoid surprise billing; `previews.expireAfterDays` set. | **No frontend previews initially** (ADR-004 preview strategy: preview environments are Pro-gated; frontend-only service previews re-evaluated at M2). PR review relies on CI + staging. | PRs into `main`; GitHub environment `dev` for CI-only secrets (dev Supabase URL/keys). |
| **staging** | Free project `nycdf-staging` (Free-org slot 2) pre-launch; migrations auto-applied from `main`. Post-Pro-upgrade, MAY be replaced by a **persistent branch** of the prod project (Pro feature) — separate-project remains the default. | Staging copies of the Blueprint services, grouped in a Render **project environment** `staging` with an environment group scoped to staging only. Created from the `main` branch. | Staging copy of `nycdf-web` (same Blueprint), in the same Render project environment `staging`; auto-deploys from `main` (`autoDeployTrigger: commit`) like every other staging service. | GitHub environment `staging`: staging secrets; auto-deploy jobs (migrations) run here on merge to `main`. |
| **prod** | **Pro** project `nycdf-prod` from launch (daily backups; PITR add-on decision at launch — ADR-003). | Production Blueprint services (`render.yaml` on `production` branch), grouped in Render project environment `production`, marked **protected**, with private-network isolation enabled and a prod-only environment group. Platform auto-deploy **disabled** (`autoDeployTrigger: "off"`); deploys are triggered only by the Actions deploy workflow via each service's secret deploy hook (ADR-003 D2/D5). | `nycdf-web` production Blueprint service, in the same protected `production` project environment, `autoDeployTrigger: "off"`; deploys only via its secret deploy hook from the same Actions workflow (ADR-003 D1 as amended by ADR-004 — identical mechanism to the API). | GitHub environment `production`: prod secrets; deployment jobs gated (see promotion rules). |

Naming convention: `nycdf-<env>` for Supabase projects and Render services (e.g., `nycdf-api-staging`, `nycdf-api` for prod).

### 3. Secret placement (no secret exists in Git, ever)

| Secret | Lives in |
|---|---|
| Supabase service-role key, DB URL (per env) | Render env vars/env groups (scoped per project environment) **only**. Not duplicated to GitHub: the official migration CI flow needs only the CLI secrets in the row below, and no current workflow needs the service-role key. |
| Supabase anon/publishable key + URL (per env) | Render env vars on the frontend web service `nycdf-web` (`NEXT_PUBLIC_*`, `sync: false` references in `render.yaml`), scoped per project environment — publishable values only per `apps/web/.env.example` (amended 2026-07-16 per ADR-004; previously Vercel env vars) |
| `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`, project ref per env (for CLI migrations in CI) | GitHub environment secrets (`staging`, `production`) — per the official Supabase CI workflow (https://supabase.com/docs/guides/deployment/managing-environments, retrieved 2026-07-14) |
| Render deploy hook URL (one per production service, **including the frontend `nycdf-web`** — ADR-004) | GitHub `production` environment secrets **only**. A deploy hook is a per-service **secret URL**; provide it only to trusted systems and regenerate it if compromised (https://render.com/docs/deploy-hooks, retrieved 2026-07-15). Never in Git. |
| ~~`VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`~~ | **Removed 2026-07-16 per ADR-004** (Vercel dropped; these secrets are never created). Row retained so the removal is visible. |
| Geoclient subscription key, Anthropic API key, Sentry DSN | Render env vars (`sync: false` references in `render.yaml`); duplicated to GitHub environment secrets only if CI needs them |

Non-secret but environment-scoped: the `ENVIRONMENT` variable is declared `sync: false` in `render.yaml` and its value (`staging` or `production`) is entered per Render environment at Blueprint/service creation, so a single Blueprint file serves both environments without hard-coding an environment name.

### 4. Promotion rules

1. **feature → dev:** open PR to `main`. CI runs lint/tests. No frontend preview by default (ADR-004 preview strategy — amended 2026-07-16; previously Vercel preview auto-deploys); Render preview environments only when explicitly requested (manual generation, and Pro-plan-gated — research file §2 via ADR-004). Schema changes ride as new files in `supabase/migrations/` (forward-only, ADR-003).
2. **dev → staging:** merge PR to `main` (requires PR review + green CI). GitHub Actions then applies new migrations to `nycdf-staging` (Supabase CLI, `staging` environment secrets). **Staging keeps platform auto-deploy:** Render staging services — including the frontend staging copy of `nycdf-web` (amended 2026-07-16 per ADR-004; previously the Vercel staging environment) — deploy on commit to `main` (`autoDeployTrigger: commit`, configured when the staging services are instantiated — [confirm at first use], verification item 1 below). Staging deploys therefore run concurrently with staging migrations; this is acceptable because the expand→deploy→contract rule (ADR-003 D4) keeps old code compatible with new schema. Producers verify acceptance scenarios against staging.
3. **staging → prod:** **human-only promotion (gate G7).** The project owner (a human, not an agent) approves; the mechanical step is a fast-forward of `production` to the approved `main` commit (tagged `release-YYYYMMDD-N`). **Nothing deploys on that push by itself** — platform auto-deploys are disabled in production (Render `autoDeployTrigger: "off"` on every production service, including the frontend `nycdf-web` — amended 2026-07-16 per ADR-004). The push starts the **production deploy workflow** (GitHub Actions — a future implementation task; it does not exist yet), whose job-dependency chain (`needs:`) enforces, in order: (a) migration validation passes; (b) migrations against `nycdf-prod` complete successfully (GitHub `production` environment); (c) required CI checks pass on the promoted commit; (d) human production approval is recorded (GitHub environment required reviewers, where the plan allows — §5). Only then do the deploy jobs trigger the Render production deploys via each service's secret deploy hook with `ref=<validated commit SHA>` (https://render.com/docs/deploy-hooks, retrieved 2026-07-15) — the frontend `nycdf-web` uses the same deploy-hook mechanism (ADR-003 D1 as amended by ADR-004; the former Vercel CLI step is removed). Order and verification steps are in ADR-003/runbook.
4. **No skipping:** nothing reaches `production` except via `main` → staging verification. Hotfixes follow the same path (fix on `main`, verify on staging, promote).

### 5. Who approves prod

The **human project owner** approves every production promotion (G7 in `docs/GATES_AND_CHECKPOINTS.md`). Technical enforcement, honestly stated:

- If the repo is **public** (or the org is on GitHub Enterprise), configure the GitHub `production` environment with **required reviewers** = owner, so the migration/deploy jobs pause for human approval (plan limitation source: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments, retrieved 2026-07-14).
- If the repo is **private on a Free/Pro/Team plan**, required reviewers are unavailable; enforcement is: (a) `production` branch push restricted to the owner, (b) Render production project environment marked **protected** (admin-only destructive changes), (c) the G7 process gate. This residual gap is recorded as a risk; revisit if the plan changes.

### 6. Cost sequencing (upgrade triggers)

| Trigger | Action |
|---|---|
| Start (now) | Supabase: 2 free projects (`nycdf-dev`, `nycdf-staging`); Render: nothing deployed or free web services for smoke tests only; no frontend previews (ADR-004); total ≈ $0 |
| First persistent worker/cron needed (M1+ ingestion) | Render paid instances for worker/cron in staging only (no free tier for workers/cron — https://render.com/docs/free, retrieved 2026-07-14) |
| Production launch prep | Create `nycdf-prod` on Supabase **Pro** (backups); Render production services on paid plans — **now including the frontend web service `nycdf-web` on `starter`** (free web services spin down after 15 min — https://render.com/docs/free, retrieved 2026-07-14); re-evaluate the ADR-004 preview strategy (Render preview environments are Pro-gated) (amended 2026-07-16 per ADR-004; previously "consider Vercel Pro") |
| Post-launch | Decide PITR add-on (ADR-003 §backups); optionally replace staging project with a persistent branch of prod (Pro branching) if migration-fidelity issues appear |

Watch item: free Supabase projects pause after 1 week of inactivity (https://supabase.com/docs/guides/platform/free-project-pausing, retrieved 2026-07-14) — normal development and CI activity is the only keep-warm mechanism for `nycdf-dev`/`nycdf-staging`; no dedicated keep-warm service is deployed (a cron would carry a $1/month-minimum cost per job with no free tier). If a project pauses, unpause it from the dashboard per the runbook before deploying.

## Consequences

- Three fully isolated blast radii for data; production data never reachable from dev/staging services (enforced by per-environment secrets scoping + Render environment-scoped env groups + network boundary blocking).
- Slight duplication: migrations run three times (dev/staging/prod) — this is the point: staging is the migration rehearsal (ADR-003).
- Free-tier staging has **no backups** pre-launch (Free plan has no daily backups — https://supabase.com/docs/guides/platform/backups, retrieved 2026-07-14). Acceptable: staging data is reconstructable from migrations + ingestion replays (PRD provenance/replayability requirements).
- The private-repo approval gap (§5) is a documented risk owned by the human owner.

## Items requiring verification at first setup (not guessed; flagged)

1. Render: exact mechanism to instantiate a second set of Blueprint services from a different branch (`main` for staging vs `production` for prod) — Blueprint-per-branch behavior must be confirmed against https://render.com/docs/infrastructure-as-code during Phase 0 setup; fallback is dashboard-created staging services mirroring `render.yaml`.
2. Render: valid `region` values for the Blueprint (`render.yaml` currently pins `oregon`; confirm against https://render.com/docs/regions).
3. ~~Vercel: whether Hobby-plan branch-scoped preview env vars fully cover the staging need until Pro.~~ **Withdrawn 2026-07-16 per ADR-004** (Vercel dropped). Replacement item: Render service previews (https://render.com/docs/service-previews) — plan-gating and billing must be verified against that page before any preview enablement for `nycdf-web` (ADR-004 preview strategy, option b).

## Sources (retrieved 2026-07-14 unless noted)

- https://supabase.com/docs/guides/deployment/managing-environments — separate projects + GitHub Actions migration flow, CI secrets
- https://supabase.com/docs/guides/deployment/branching — Pro-plan requirement; preview vs persistent branches
- https://supabase.com/pricing and https://supabase.com/docs/guides/platform/free-project-pausing — 2 active free projects; 1-week inactivity pausing
- https://supabase.com/docs/guides/platform/manage-your-usage/compute and https://supabase.com/docs/guides/platform/manage-your-usage/branching — $10/mo compute credits; $0.01344/hour additional database
- https://supabase.com/docs/guides/platform/backups — backups/PITR plan gating
- https://render.com/docs/projects and https://render.com/changelog/project-environment-groups — project environments, protected environments, network boundary, scoped env groups
- https://render.com/docs/preview-environments and https://render.com/docs/blueprint-spec — previews generation/expiry/billing; sync:false exclusion from previews
- https://render.com/docs/free — free-tier limits (spin-down; no free workers/cron)
- https://vercel.com/docs/deployments/environments — production/preview model; Custom Environments on Pro/Enterprise; branch tracking *(superseded 2026-07-16 per ADR-004; retained for provenance only)*
- https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments and https://docs.github.com/actions/deployment/targeting-different-environments/using-environments-for-deployment — environment protection plan limits
- https://render.com/docs/blueprint-spec (retrieved 2026-07-15) — `autoDeployTrigger` field (`commit` / `checksPass` / `off`); replaces the deprecated `autoDeploy` and takes precedence if both present; default `commit` for new services
- https://render.com/docs/deploy-hooks (retrieved 2026-07-15) — per-service secret deploy-hook URL; `ref` query parameter deploys a specific commit SHA; regenerate on compromise
- https://vercel.com/guides/how-can-i-use-github-actions-with-vercel (retrieved 2026-07-15) — CI-driven deploys via Vercel CLI *(superseded 2026-07-16 per ADR-004; retained for provenance and for the ADR-004 rollback path)*
- https://vercel.com/docs/project-configuration/git-configuration (retrieved 2026-07-15) — `git.deploymentEnabled` per-branch git-deploy disabling *(superseded 2026-07-16 per ADR-004; retained for provenance and for the ADR-004 rollback path)*
- `docs/research/render-nextjs-previews-2026-07-16.md` (retrieved 2026-07-16) — SSR Next.js as a Render web service; preview environments Pro-gated, billed like regular services; service-previews pointer; `autoDeployTrigger` `"off"` quoting (added 2026-07-16 per ADR-004)
