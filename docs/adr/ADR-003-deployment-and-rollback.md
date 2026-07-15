# ADR-003: Deployment Pipelines and Rollback Procedures per Service

- **Status:** Proposed (pending G3 gate review)
- **Date:** 2026-07-14 (amended 2026-07-15: deploy-trigger model reworked per owner directive; G3 defect 1)
- **Producer:** cloud-architect (task M0-T006)
- **Deciders:** Human project owner (final)
- **Related:** ADR-001 (providers), ADR-002 (environments/promotion), `render.yaml`, operator runbook `docs/DEPLOYMENT_AND_ROLLBACK.md`

## Context

Three deployables (Next.js on Vercel; FastAPI web + workers + cron on Render; Postgres schema on Supabase) have **three different rollback semantics**. A bad release must be reversible per service without guessing platform behavior. All platform claims below cite official docs retrieved 2026-07-14, except deploy-trigger/deploy-hook/Vercel-CLI claims retrieved 2026-07-15 (dated inline).

## Decision — deployment pipeline per service

### D1. Frontend (Vercel)

- PR/branch push → **preview deployment** automatically (git integration stays enabled for non-production branches). Staging: `main`-tracked environment per ADR-002 (branch-scoped previews pre-Pro; Custom Environment on Pro).
- **Production: automatic git deploys are disabled for the `production` branch** via `git.deploymentEnabled` in `vercel.json` (object form keyed by branch, e.g. `{"git": {"deploymentEnabled": {"production": false}}}`; default is `true`; the deprecated `github.enabled` is not used) — https://vercel.com/docs/project-configuration/git-configuration, retrieved 2026-07-15. **Planned configuration:** `vercel.json` lives in `apps/web`, outside this task's file scope; a tracked follow-up task must add it before the first production deploy.
- The production deployment is executed by the GitHub Actions production deploy workflow (D5) using the Vercel CLI, only after production migrations succeed: `vercel pull --yes --environment=production` → `vercel build --prod` → `vercel deploy --prebuilt` (uploads the previously generated `.vercel/output`; requires `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` as GitHub `production` environment secrets) — https://vercel.com/guides/how-can-i-use-github-actions-with-vercel, retrieved 2026-07-15. When a production deployment succeeds, "Vercel updates your production domains to point to the new deployment" (https://vercel.com/docs/deployments/environments, retrieved 2026-07-14).
- If pending decision ADR-004/M0-T011 (drop Vercel; frontend on Render) is approved, this Vercel CLI mechanism is replaced by the same Render deploy-hook mechanism as D2.

### D2. API, workers, cron (Render)

- All Render services are declared in `render.yaml` (Blueprint) at the repo root (https://render.com/docs/infrastructure-as-code, retrieved 2026-07-14).
- **Production: platform auto-deploy is disabled.** Every production service sets `autoDeployTrigger: off` — the current Blueprint field, which "replaces the deprecated `autoDeploy` field" and takes precedence if both are present; `off` is equivalent to the deprecated `autoDeploy: false`, and the default for new services when the field is omitted is `commit` (https://render.com/docs/blueprint-spec, retrieved 2026-07-15). `off` (not `checksPass`) is required because even a checks-gated platform deploy could not encode the mandatory human-production-approval step (D5).
- Production deploys are triggered by the GitHub Actions production deploy workflow (D5) calling each service's **deploy hook** — a per-service **secret URL** that triggers an on-demand deploy with a single HTTP request; the `ref` query parameter deploys a specific Git commit SHA, so exactly the validated commit deploys; responses: 200 (deploy started), 202 (queued behind a running deploy), 401 (unauthorized); regenerate the hook if compromised (https://render.com/docs/deploy-hooks, retrieved 2026-07-15). Hook URLs are stored only as GitHub `production` environment secrets (ADR-002 §3) — never in Git.
- **Staging: keeps platform auto-deploy** on push to `main` (`autoDeployTrigger: commit`), configured when the staging services are instantiated ([confirm at first use] — ADR-002 verification item 1; a single `render.yaml` cannot carry per-environment trigger values). Concurrent staging deploys during staging migrations are safe because of D4.
- The web service declares `healthCheckPath: /health`. Render "considers a check successful if the instance responds with a 2xx or 3xx status code within five seconds" and uses the endpoint during zero-downtime deploys (https://render.com/docs/health-checks, retrieved 2026-07-14). A deploy whose health check never passes does not replace the running version — this is the first line of rollback defense.
- Cron schedules are declared in the Blueprint and evaluated **in UTC** (https://render.com/docs/cronjobs, retrieved 2026-07-14).

### D3. Database (Supabase)

- Schema changes are **SQL migration files** in `supabase/migrations/`, applied by GitHub Actions with the Supabase CLI (`supabase db push` / migration commands), targeting staging on merge to `main`, then production only during an approved promotion — this is the officially documented multi-environment release flow, using `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`, and the per-environment project ref as CI secrets (https://supabase.com/docs/guides/deployment/managing-environments, https://supabase.com/docs/reference/cli/supabase-db-push — retrieved 2026-07-14).
- Applied migrations are tracked in the remote table `supabase_migrations.schema_migrations`; "after successfully applying a migration, a new row will be inserted into the migration history table" (https://supabase.com/docs/reference/cli/supabase-migration-repair, retrieved 2026-07-14).

### D4. Ordering rule for any release that includes a migration

**Expand → deploy → contract.**
1. Ship additive/backward-compatible schema changes first (new columns nullable/defaulted; no drops/renames in the same release as the code that stops using them).
2. Deploy application code that works with both old and new schema.
3. Remove old schema elements only in a later release, after the code that needed them is gone everywhere.

This guarantees that an **application rollback (Render/Vercel) never requires a schema rollback** — which matters because the database has no cheap undo (see R3).

### D5. Production deploy workflow (GitHub Actions — future implementation task)

The production deploy sequence is enforced by a single GitHub Actions workflow triggered by the push to `production`. **This workflow does not exist yet; it is a tracked follow-up implementation task — nothing in this ADR claims it is implemented.** Its job-dependency chain (`needs:`) is the ONLY mechanism that enforces the ordering below; with platform auto-deploys disabled (D1/D2), no platform-side deploy runs or halts on its own.

Required order, expressed as the workflow's `needs:` chain:

1. `validate-migrations` — database migration validation passes.
2. `migrate-production` (`needs: validate-migrations`) — applies `supabase/migrations/` to `nycdf-prod` (D3) and must complete successfully.
3. Required CI checks pass on the promoted commit (branch protection on `production`).
4. `deploy-render` and `deploy-vercel` (`needs: migrate-production`) — bound to the GitHub `production` environment so **human production approval is recorded** via required reviewers before they run (plan caveat: ADR-002 §5). `deploy-render` calls each service's secret deploy hook with `ref=<validated commit SHA>` (D2); `deploy-vercel` runs the Vercel CLI sequence (D1).

Until this workflow exists, production deploys are performed manually in the same order per the runbook §1.2 — and after a failed migration the operator must NOT trigger any deploy hook or frontend deploy.

### R1. Vercel: Instant Rollback

Official behavior (https://vercel.com/docs/instant-rollback, retrieved 2026-07-14):

- Rollback happens "at the routing layer" by re-pointing domains to an existing deployment — takes effect within seconds, no rebuild.
- Eligibility: deployments **previously aliased to a production domain**. Pro/Enterprise can roll back to any previously-aliased deployment; **Hobby can roll back only to the immediately previous deployment**.
- Environment variables are **not** updated by a rollback — the rolled-back deployment keeps the env state it was built with.
- Cron jobs defined by the app "will be reverted to the state of the rolled back deployment".
- After a rollback, Vercel **turns off auto-assignment of production domains** — new pushes to the production branch will NOT go live until rollback is explicitly ended. The runbook includes this re-enable step.
- Only one rollback can run at a time per project.

### R2. Render: deploy rollback (web + workers), redeploy (cron)

Official behavior (https://render.com/docs/rollbacks, API: https://api-docs.render.com/reference/rollback-deploy — retrieved 2026-07-14):

- Rollback is supported for **web services, private services, and background workers**, from the dashboard (or API), "without needing to rebuild your service" — Render reuses the target deploy's build artifact.
- Because rollbacks **skip the build step**, "any recent changes to environment group variables are not reflected" in the rolled-back artifact; if the target deploy referenced an env group that has since been deleted, "the rollback proceeds without it".
- "Rolling back does not overwrite any of your service's current configuration settings" — config (instance type, env vars, etc.) stays current; only the artifact reverts.
- **Cron jobs are not listed as rollback-eligible** in the rollback doc. Policy: to revert a cron job, push a `git revert` to the tracked branch and deploy it — staging deploys on the push (`autoDeployTrigger: commit`); in production the deploy must then be triggered via the deploy hook or a manual dashboard deploy, because production auto-deploy is off (D2). Same fallback applies to any service if the rollback UI is unavailable.
- Rollback does not revert `render.yaml` infrastructure changes (service topology/plans). Infra changes are reverted by reverting the `render.yaml` commit.

### R3. Supabase: forward-only migrations; backups/PITR as last resort

**Policy: forward-only. No down-migrations are written or maintained.**

Rationale:
- The official Supabase workflow tracks applied migrations in `supabase_migrations.schema_migrations` and provides `supabase migration repair` to mark entries `applied`/`reverted`, but repair "updates the tracking table only — it does not apply or revert any SQL" (https://supabase.com/docs/reference/cli/supabase-migration-repair, retrieved 2026-07-14). There is no supported automatic down-runner in this workflow.
- Down-migrations for data-bearing changes are destructive and would be the least-tested code in the system. The expand→deploy→contract rule (D4) removes the need for them: app-level rollbacks never depend on schema reversal.

Corrective mechanisms, in order:
1. **Roll forward:** write a new corrective migration file; land it through dev → staging → prod like any change (expedited but never skipping staging).
2. **History repair:** if the migration history table and the `supabase/migrations/` directory disagree (e.g., a partially applied push), realign with `supabase migration repair --status applied|reverted <timestamp>` — "marking as `reverted` will delete an existing record from the migration history table while marking as `applied` will insert a new record" (same source). Repair never executes SQL; any real schema fix still requires a forward migration.
3. **Restore (last resort, data loss/downtime accepted):** production runs on Pro with **daily backups (7-day retention)**; optionally the **PITR add-on** ("restore to any chosen point with up to seconds of granularity", requires at least Small compute, and "if you enable PITR, we will no longer take Daily Backups"). Restores make the project temporarily inaccessible — "downtime depends on the size of the database" (https://supabase.com/docs/guides/platform/backups, retrieved 2026-07-14). **Decision:** launch with daily backups; enable PITR before the first paying client or the first > 24h-costly data window, whichever is first (owner decision at launch, G7).

**Failed-migration handling (prod):**
1. The GitHub Actions migration job fails → the deploy jobs do not run **because they are declared with `needs:` on the migration job in the production deploy workflow (D5 — a future implementation task; this job-dependency chain is the only mechanism that enforces the halt)**. Platform auto-deploys are disabled in production (Render `autoDeployTrigger: off`, D2; Vercel git deploys disabled for `production`, D1), so no platform-side deploy proceeds on its own. If deploying manually because the D5 workflow does not exist yet: STOP — trigger no deploy hook and no frontend deploy.
2. Freeze further deploys; capture the CI log and the current contents of `supabase_migrations.schema_migrations`.
3. Classify: (a) migration never started → fix forward, re-run; (b) partially applied / history desynced → write corrective forward migration, use `migration repair` to realign history, re-run; (c) data corrupted → owner decides restore from daily backup/PITR per step 3 above, then replay ingestion per provenance/replayability requirements (PRD 9/10).
4. Record the incident in the audit log and `project-control/` per `docs/GATES_AND_CHECKPOINTS.md`.
5. Standing prevention: every migration must have run green on staging (identical file, identical order) before prod; migrations are never edited after being applied anywhere — a new file is always created.

## Rollback decision matrix (operator quick reference)

| Symptom | Service | Action | Time to effect |
|---|---|---|---|
| Bad frontend release | Vercel | Instant Rollback to last good deployment; remember auto-assign is disabled afterward | Seconds |
| Bad API/worker release (code) | Render | Dashboard/API "Rollback" to previous deploy (no rebuild) | ~ restart time |
| Bad cron release | Render | `git revert` + push, then trigger the deploy (staging: automatic; production: deploy hook/manual — auto-deploy is off) | One build |
| Bad env var change | Render/Vercel | Fix the variable, redeploy (rollbacks do NOT restore env vars on either platform) | One deploy/restart |
| Bad infra change (`render.yaml`) | Render | Revert the `render.yaml` commit, push [confirm at first use: whether Blueprint syncs still apply automatically with `autoDeployTrigger: off`, or must be applied manually] | One Blueprint sync |
| Failed prod migration | Supabase | Forward fix → repair history if desynced → restore backup/PITR only as last resort | Minutes → hours |
| Bad data (app bug wrote garbage) | Supabase | Prefer targeted forward fix / replay from provenance; PITR restore only if corruption is broad | Hours |

## Consequences

- No service ever requires a schema rollback to recover (D4) — this is the single most important operational property of this ADR.
- The migrations-before-deploys ordering in production exists **only** inside the future D5 workflow's `needs:` chain. Until that workflow is implemented, the ordering is procedural (runbook §1.2) and the halt-on-failed-migration property depends on the operator, not on any platform mechanism. Implementing D5 is a tracked follow-up task and a precondition for the first production deploy.
- Env vars are the shared weak point: **neither Render nor Vercel restores env vars on rollback** (R1/R2). Mitigation: env var changes are treated as deploys — announced, recorded (name + environment, never values) in the ops log, and verified against staging first.
- Forward-only migrations mean an occasional ugly-but-safe corrective migration instead of a clean-looking down file. Accepted.
- Pre-launch staging/dev have no backups (Free plan) — reconstructable by design (ADR-002).
- The operator runbook (`docs/DEPLOYMENT_AND_ROLLBACK.md`) is the executable distillation of this ADR; on conflict, this ADR wins and the runbook must be fixed.

## Sources (retrieved 2026-07-14 unless noted)

- https://render.com/docs/rollbacks — rollback eligibility (web/private/worker), skip-build semantics, env-group caveats, config not overwritten
- https://api-docs.render.com/reference/rollback-deploy — rollback via API
- https://render.com/docs/health-checks — 2xx/3xx within 5 s; zero-downtime deploy gating
- https://render.com/docs/infrastructure-as-code — Blueprint model, `render.yaml` at repo root
- https://render.com/docs/blueprint-spec (retrieved 2026-07-15) — `autoDeployTrigger` (`commit`/`checksPass`/`off`) replaces deprecated `autoDeploy` and takes precedence; default `commit` for new services; `sync: false`
- https://render.com/docs/deploy-hooks (retrieved 2026-07-15) — per-service secret deploy-hook URL; `ref` query parameter for a specific commit SHA; 200/202/401 responses; regenerate on compromise
- https://render.com/docs/cronjobs — UTC schedule evaluation
- https://vercel.com/docs/instant-rollback — routing-layer rollback, eligibility, Hobby limit, env vars unchanged, auto-assign disabled after rollback
- https://vercel.com/docs/deployments/environments — production/preview deployment model; production-domain repointing on success
- https://vercel.com/docs/project-configuration/git-configuration (retrieved 2026-07-15) — `git.deploymentEnabled` per-branch disabling of automatic git deploys (default `true`; `github.enabled` deprecated)
- https://vercel.com/guides/how-can-i-use-github-actions-with-vercel (retrieved 2026-07-15) — CI deploy sequence `vercel pull` → `vercel build --prod` → `vercel deploy --prebuilt`; required `VERCEL_TOKEN`/`VERCEL_ORG_ID`/`VERCEL_PROJECT_ID`
- https://supabase.com/docs/guides/deployment/managing-environments — CI migration release flow and secrets
- https://supabase.com/docs/reference/cli/supabase-db-push — applying local migrations to linked remote
- https://supabase.com/docs/reference/cli/supabase-migration-repair — schema_migrations history table; repair semantics
- https://supabase.com/docs/guides/platform/backups — daily backups retention, PITR add-on behavior, restore downtime

Verification method note: retrieved 2026-07-14 via web search against official domains (direct page fetch unavailable in the authoring session). Exact dashboard click-paths not quoted by the sources are marked "confirm at first use" in the runbook rather than guessed.
