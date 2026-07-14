# ADR-003: Deployment Pipelines and Rollback Procedures per Service

- **Status:** Proposed (pending G3 gate review)
- **Date:** 2026-07-14
- **Producer:** cloud-architect (task M0-T006)
- **Deciders:** Human project owner (final)
- **Related:** ADR-001 (providers), ADR-002 (environments/promotion), `render.yaml`, operator runbook `docs/DEPLOYMENT_AND_ROLLBACK.md`

## Context

Three deployables (Next.js on Vercel; FastAPI web + workers + cron on Render; Postgres schema on Supabase) have **three different rollback semantics**. A bad release must be reversible per service without guessing platform behavior. All platform claims below cite official docs retrieved 2026-07-14.

## Decision — deployment pipeline per service

### D1. Frontend (Vercel)

- PR/branch push → **preview deployment** automatically; merge to the Vercel production branch (`production`, per ADR-002) → **production deployment**; when it succeeds "Vercel updates your production domains to point to the new deployment" (https://vercel.com/docs/deployments/environments, retrieved 2026-07-14).
- Staging: `main`-tracked environment per ADR-002 (branch-scoped previews pre-Pro; Custom Environment on Pro).

### D2. API, workers, cron (Render)

- All Render services are declared in `render.yaml` (Blueprint) at the repo root (https://render.com/docs/infrastructure-as-code, retrieved 2026-07-14). Pushes to the tracked branch auto-deploy (`autoDeploy: true`; field per https://render.com/docs/blueprint-spec, retrieved 2026-07-14).
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

## Decision — rollback per service

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
- **Cron jobs are not listed as rollback-eligible** in the rollback doc. Policy: to revert a cron job, push a `git revert` to the tracked branch (normal deploy of the previous code). Same fallback applies to any service if the rollback UI is unavailable.
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
1. The GitHub Actions migration job fails → **promotion halts automatically**; Render/Vercel production deploy steps must not proceed (pipeline ordering: migrations first, then services; a failed migration job blocks the dependent deploy jobs).
2. Freeze further deploys; capture the CI log and the current contents of `supabase_migrations.schema_migrations`.
3. Classify: (a) migration never started → fix forward, re-run; (b) partially applied / history desynced → write corrective forward migration, use `migration repair` to realign history, re-run; (c) data corrupted → owner decides restore from daily backup/PITR per step 3 above, then replay ingestion per provenance/replayability requirements (PRD 9/10).
4. Record the incident in the audit log and `project-control/` per `docs/GATES_AND_CHECKPOINTS.md`.
5. Standing prevention: every migration must have run green on staging (identical file, identical order) before prod; migrations are never edited after being applied anywhere — a new file is always created.

## Rollback decision matrix (operator quick reference)

| Symptom | Service | Action | Time to effect |
|---|---|---|---|
| Bad frontend release | Vercel | Instant Rollback to last good deployment; remember auto-assign is disabled afterward | Seconds |
| Bad API/worker release (code) | Render | Dashboard/API "Rollback" to previous deploy (no rebuild) | ~ restart time |
| Bad cron release | Render | `git revert` + push (cron not rollback-eligible) | One build |
| Bad env var change | Render/Vercel | Fix the variable, redeploy (rollbacks do NOT restore env vars on either platform) | One deploy/restart |
| Bad infra change (`render.yaml`) | Render | Revert the `render.yaml` commit, push | One Blueprint sync |
| Failed prod migration | Supabase | Forward fix → repair history if desynced → restore backup/PITR only as last resort | Minutes → hours |
| Bad data (app bug wrote garbage) | Supabase | Prefer targeted forward fix / replay from provenance; PITR restore only if corruption is broad | Hours |

## Consequences

- No service ever requires a schema rollback to recover (D4) — this is the single most important operational property of this ADR.
- Env vars are the shared weak point: **neither Render nor Vercel restores env vars on rollback** (R1/R2). Mitigation: env var changes are treated as deploys — announced, recorded (name + environment, never values) in the ops log, and verified against staging first.
- Forward-only migrations mean an occasional ugly-but-safe corrective migration instead of a clean-looking down file. Accepted.
- Pre-launch staging/dev have no backups (Free plan) — reconstructable by design (ADR-002).
- The operator runbook (`docs/DEPLOYMENT_AND_ROLLBACK.md`) is the executable distillation of this ADR; on conflict, this ADR wins and the runbook must be fixed.

## Sources (all retrieved 2026-07-14)

- https://render.com/docs/rollbacks — rollback eligibility (web/private/worker), skip-build semantics, env-group caveats, config not overwritten
- https://api-docs.render.com/reference/rollback-deploy — rollback via API
- https://render.com/docs/health-checks — 2xx/3xx within 5 s; zero-downtime deploy gating
- https://render.com/docs/infrastructure-as-code and https://render.com/docs/blueprint-spec — Blueprint sync, autoDeploy, sync:false
- https://render.com/docs/cronjobs — UTC schedule evaluation
- https://vercel.com/docs/instant-rollback — routing-layer rollback, eligibility, Hobby limit, env vars unchanged, auto-assign disabled after rollback
- https://vercel.com/docs/deployments/environments — production/preview deployment triggers
- https://supabase.com/docs/guides/deployment/managing-environments — CI migration release flow and secrets
- https://supabase.com/docs/reference/cli/supabase-db-push — applying local migrations to linked remote
- https://supabase.com/docs/reference/cli/supabase-migration-repair — schema_migrations history table; repair semantics
- https://supabase.com/docs/guides/platform/backups — daily backups retention, PITR add-on behavior, restore downtime

Verification method note: retrieved 2026-07-14 via web search against official domains (direct page fetch unavailable in the authoring session). Exact dashboard click-paths not quoted by the sources are marked "confirm at first use" in the runbook rather than guessed.
