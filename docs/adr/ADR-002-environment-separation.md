# ADR-002: Environment Separation — dev / staging / prod

- **Status:** Proposed (pending G3 gate review)
- **Date:** 2026-07-14
- **Producer:** cloud-architect (task M0-T006)
- **Deciders:** Human project owner (final)
- **Related:** ADR-001 (providers), ADR-003 (deployment and rollback), `render.yaml`

## Context

PRD Phase 0 requires "Dev/staging/production environments" and "Secret management" (PRD 26). Government data ingestion, legal-rule releases, and client analyses must never be tested against production data. Costs must stay near zero until launch (PRD 35; `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`). Environment separation must therefore use each provider's cheapest *safe* mechanism, based on official platform behavior only.

Key researched platform facts (all retrieved 2026-07-14):

- **Supabase — separate projects vs branches.** The official multi-environment guide supports "separate development, staging, and production environments" driven by "Database Migrations and GitHub Actions to automatically test and release schema changes to staging and production projects" (https://supabase.com/docs/guides/deployment/managing-environments). Branching (preview branches per PR, persistent branches for staging/QA) **requires the Pro Plan** (https://supabase.com/docs/guides/deployment/branching). Free plan allows **2 active projects**, and "Free projects are paused after 1 week of inactivity" (https://supabase.com/pricing, https://supabase.com/docs/guides/platform/free-project-pausing). Paid orgs include $10/mo compute credits (~one Micro instance); each additional always-on database costs $0.01344/hour (~$10/mo) (https://supabase.com/docs/guides/platform/manage-your-usage/compute, https://supabase.com/docs/guides/platform/manage-your-usage/branching).
- **Supabase — backups are plan-gated.** Daily backups exist on Pro/Team/Enterprise only (7/14/30 days retention); PITR is a Pro+ add-on (https://supabase.com/docs/guides/platform/backups). Production therefore cannot remain on the Free plan at launch.
- **Render — projects/environments.** Render lets you "organize your services by their application and environment (such as staging or production)", supports **protected environments** ("only your workspace's admins can make potentially destructive changes"; shell access restricted to Admins), can **block private-network traffic across an environment boundary**, and can scope an environment group (shared env vars/secrets) to a single project environment to "protect against accidentally connecting a staging service to a production database" (https://render.com/docs/projects, https://render.com/changelog/project-environment-groups — retrieved 2026-07-14).
- **Render — preview environments.** Blueprint `previews.generation: manual | automatic` creates per-PR copies of Blueprint services; Render "automatically destroys them when the original pull request is merged or closed"; `previews.expireAfterDays` adds inactivity expiry; previews are billed at the same rate as the base service and can use a smaller `previews.plan`; **`sync: false` env vars are not included in preview environments** (https://render.com/docs/preview-environments, https://render.com/docs/blueprint-spec — retrieved 2026-07-14).
- **Vercel — environments.** Production deployments trigger on push/merge to the production branch; every other branch/PR gets a preview deployment; env vars can be scoped per environment and per Git branch for previews; **Custom Environments (e.g., a long-lived `staging`) require Pro or Enterprise** and support branch tracking (https://vercel.com/docs/deployments/environments — retrieved 2026-07-14).
- **GitHub — environment protection is plan-gated for private repos.** "If you are on a GitHub Free, GitHub Pro, or GitHub Team plan, required reviewers are only available for public repositories." Access to environments/environment secrets in private repos needs Pro/Team/Enterprise (https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments, https://docs.github.com/actions/deployment/targeting-different-environments/using-environments-for-deployment — retrieved 2026-07-14).

## Decision

### 1. Git branch model (drives everything else)

- `main` — integration branch; always releasable; deploys **staging**.
- `production` — protected release branch; fast-forwarded from `main` only during an approved promotion; deploys **production**.
- Feature branches + PRs into `main` — deploy **dev previews**.

### 2. Concrete environment mapping

| Environment | Supabase | Render | Vercel | GitHub |
|---|---|---|---|---|
| **dev** | Free project `nycdf-dev` (Free-org slot 1). Accepts destructive experiments and seeded/mock data. | No always-on dev services. Per-PR **preview environments** with `previews.generation: manual` (opt-in per PR) to avoid surprise billing; `previews.expireAfterDays` set. | **Preview deployments** per PR/branch (default behavior). | PRs into `main`; GitHub environment `dev` for CI-only secrets (dev Supabase URL/keys). |
| **staging** | Free project `nycdf-staging` (Free-org slot 2) pre-launch; migrations auto-applied from `main`. Post-Pro-upgrade, MAY be replaced by a **persistent branch** of the prod project (Pro feature) — separate-project remains the default. | Staging copies of the Blueprint services, grouped in a Render **project environment** `staging` with an environment group scoped to staging only. Created from the `main` branch. | Pre-Pro: branch-tracked previews of `main` with **branch-scoped env vars** pointing at staging Supabase. Post-Pro: a **Custom Environment** `staging` tracking `main`. | GitHub environment `staging`: staging secrets; auto-deploy jobs (migrations) run here on merge to `main`. |
| **prod** | **Pro** project `nycdf-prod` from launch (daily backups; PITR add-on decision at launch — ADR-003). | Production Blueprint services (`render.yaml` on `production` branch), grouped in Render project environment `production`, marked **protected**, with private-network isolation enabled and a prod-only environment group. | Production deployments from the `production` branch (set as the Vercel production branch). | GitHub environment `production`: prod secrets; deployment jobs gated (see promotion rules). |

Naming convention: `nycdf-<env>` for Supabase projects and Render services (e.g., `nycdf-api-staging`, `nycdf-api` for prod).

### 3. Secret placement (no secret exists in Git, ever)

| Secret | Lives in |
|---|---|
| Supabase service-role key, DB URL (per env) | Render env vars/env groups (scoped per project environment) + GitHub environment secrets (for migration CI) |
| Supabase anon/publishable key + URL (per env) | Vercel env vars scoped to the matching Vercel environment/branch |
| `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`, project ref per env (for CLI migrations in CI) | GitHub environment secrets (`staging`, `production`) — per the official Supabase CI workflow (https://supabase.com/docs/guides/deployment/managing-environments, retrieved 2026-07-14) |
| Geoclient subscription key, Anthropic API key, Sentry DSN | Render env vars (`sync: false` references in `render.yaml`); duplicated to GitHub environment secrets only if CI needs them |

### 4. Promotion rules

1. **feature → dev:** open PR to `main`. CI runs lint/tests. Vercel preview auto-deploys; Render preview only when explicitly requested (manual generation). Schema changes ride as new files in `supabase/migrations/` (forward-only, ADR-003).
2. **dev → staging:** merge PR to `main` (requires PR review + green CI). GitHub Actions then applies new migrations to `nycdf-staging` (Supabase CLI, `staging` environment secrets) and Render/Vercel staging auto-deploy from `main`. Producers verify acceptance scenarios against staging.
3. **staging → prod:** **human-only promotion (gate G7).** The project owner (a human, not an agent) approves; the mechanical step is a fast-forward of `production` to the approved `main` commit (tagged `release-YYYYMMDD-N`). That push triggers: migrations against `nycdf-prod` (GitHub `production` environment), Render production deploy, Vercel production deploy. Order and verification steps are in ADR-003/runbook.
4. **No skipping:** nothing reaches `production` except via `main` → staging verification. Hotfixes follow the same path (fix on `main`, verify on staging, promote).

### 5. Who approves prod

The **human project owner** approves every production promotion (G7 in `docs/GATES_AND_CHECKPOINTS.md`). Technical enforcement, honestly stated:

- If the repo is **public** (or the org is on GitHub Enterprise), configure the GitHub `production` environment with **required reviewers** = owner, so the migration/deploy jobs pause for human approval (plan limitation source: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments, retrieved 2026-07-14).
- If the repo is **private on a Free/Pro/Team plan**, required reviewers are unavailable; enforcement is: (a) `production` branch push restricted to the owner, (b) Render production project environment marked **protected** (admin-only destructive changes), (c) the G7 process gate. This residual gap is recorded as a risk; revisit if the plan changes.

### 6. Cost sequencing (upgrade triggers)

| Trigger | Action |
|---|---|
| Start (now) | Supabase: 2 free projects (`nycdf-dev`, `nycdf-staging`); Render: nothing deployed or free web service for smoke tests only; Vercel Hobby; total ≈ $0 |
| First persistent worker/cron needed (M1+ ingestion) | Render paid instances for worker/cron in staging only (no free tier for workers/cron — https://render.com/docs/free, retrieved 2026-07-14) |
| Production launch prep | Create `nycdf-prod` on Supabase **Pro** (backups); Render production services on paid plans; consider Vercel Pro (Custom Environments, broader Instant Rollback eligibility — ADR-003) |
| Post-launch | Decide PITR add-on (ADR-003 §backups); optionally replace staging project with a persistent branch of prod (Pro branching) if migration-fidelity issues appear |

Watch item: free Supabase projects pause after 1 week of inactivity (https://supabase.com/docs/guides/platform/free-project-pausing, retrieved 2026-07-14) — the staging smoke-test cron (see `render.yaml` comments) and normal development activity keep `nycdf-dev`/`nycdf-staging` warm; unpausing via dashboard is in the runbook.

## Consequences

- Three fully isolated blast radii for data; production data never reachable from dev/staging services (enforced by per-environment secrets scoping + Render environment-scoped env groups + network boundary blocking).
- Slight duplication: migrations run three times (dev/staging/prod) — this is the point: staging is the migration rehearsal (ADR-003).
- Free-tier staging has **no backups** pre-launch (Free plan has no daily backups — https://supabase.com/docs/guides/platform/backups, retrieved 2026-07-14). Acceptable: staging data is reconstructable from migrations + ingestion replays (PRD provenance/replayability requirements).
- The private-repo approval gap (§5) is a documented risk owned by the human owner.

## Items requiring verification at first setup (not guessed; flagged)

1. Render: exact mechanism to instantiate a second set of Blueprint services from a different branch (`main` for staging vs `production` for prod) — Blueprint-per-branch behavior must be confirmed against https://render.com/docs/infrastructure-as-code during Phase 0 setup; fallback is dashboard-created staging services mirroring `render.yaml`.
2. Render: valid `region` values for the Blueprint (`render.yaml` currently pins `oregon`; confirm against https://render.com/docs/regions).
3. Vercel: whether Hobby-plan branch-scoped preview env vars fully cover the staging need until Pro (confirm against https://vercel.com/docs/environment-variables when wiring `apps/web`).

## Sources (all retrieved 2026-07-14)

- https://supabase.com/docs/guides/deployment/managing-environments — separate projects + GitHub Actions migration flow, CI secrets
- https://supabase.com/docs/guides/deployment/branching — Pro-plan requirement; preview vs persistent branches
- https://supabase.com/pricing and https://supabase.com/docs/guides/platform/free-project-pausing — 2 active free projects; 1-week inactivity pausing
- https://supabase.com/docs/guides/platform/manage-your-usage/compute and https://supabase.com/docs/guides/platform/manage-your-usage/branching — $10/mo compute credits; $0.01344/hour additional database
- https://supabase.com/docs/guides/platform/backups — backups/PITR plan gating
- https://render.com/docs/projects and https://render.com/changelog/project-environment-groups — project environments, protected environments, network boundary, scoped env groups
- https://render.com/docs/preview-environments and https://render.com/docs/blueprint-spec — previews generation/expiry/billing; sync:false exclusion from previews
- https://render.com/docs/free — free-tier limits (spin-down; no free workers/cron)
- https://vercel.com/docs/deployments/environments — production/preview model; Custom Environments on Pro/Enterprise; branch tracking
- https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments and https://docs.github.com/actions/deployment/targeting-different-environments/using-environments-for-deployment — environment protection plan limits
