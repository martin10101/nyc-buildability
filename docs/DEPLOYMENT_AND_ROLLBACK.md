# Deployment and Rollback Runbook (Operator Guide)

Distilled from `docs/adr/ADR-003-deployment-and-rollback.md` (authoritative on conflict) and `docs/adr/ADR-002-environment-separation.md`. Platform behaviors cite official docs retrieved 2026-07-14 unless otherwise dated. Dashboard click-paths not quoted by official docs are marked **[confirm at first use]** — never guess a destructive action.

## 0. Environment map (from ADR-002)

| Env | Git | Supabase project | Render | Vercel |
|---|---|---|---|---|
| dev | PR branches | `nycdf-dev` (Free) | opt-in PR previews | preview deployments |
| staging | `main` | `nycdf-staging` (Free pre-launch) | staging service copies (project env `staging`) | `main`-tracked env |
| prod | `production` | `nycdf-prod` (Pro) | Blueprint services (project env `production`, protected); `autoDeployTrigger: off` — deploys only via secret deploy hook from the Actions pipeline | production branch; git auto-deploy disabled (`git.deploymentEnabled` — planned `vercel.json` config); CLI deploy from the Actions pipeline |

Deploy order for any release containing a migration: **1) migrations, 2) Render, 3) Vercel.** In production this order is enforced ONLY by the production deploy workflow's `needs:` job chain (ADR-003 D5 — a future implementation task); platform auto-deploys are disabled, so nothing deploys on the push itself. When deploying manually (D5 not yet implemented), YOU are the enforcement: after a failed migration, trigger no deploy hook and no frontend deploy.

---

## 1. Normal deploy

### 1.1 To staging
1. Merge the approved PR into `main` (green CI required).
2. GitHub Actions applies new files in `supabase/migrations/` to `nycdf-staging` via Supabase CLI (secrets: `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`, staging project ref — per https://supabase.com/docs/guides/deployment/managing-environments, retrieved 2026-07-14).
3. Render staging services auto-deploy from `main` (`autoDeployTrigger: commit`, configured at staging instantiation — [confirm at first use], ADR-002 "Items requiring verification" item 1); the Vercel staging environment auto-deploys from `main` via git integration (automatic deploys stay enabled for non-production branches).
4. Verify: `/health` returns 200 on the staging API; run the release's acceptance scenarios against staging.

### 1.2 To production (human approval required — G7)
1. Owner reviews the staging verification evidence and approves (G7). **No agent may perform this step.**
2. Tag the approved `main` commit: `release-YYYYMMDD-N`.
3. Fast-forward `production` to that commit and push. **Nothing deploys on this push by itself** — platform auto-deploys are disabled in production (ADR-003 D1/D2).
4. The production deploy workflow (ADR-003 D5 — a future implementation task; until it exists, perform these steps manually in this exact order and stop at the first failure) enforces via its `needs:` job chain: migration validation passes → migrations against `nycdf-prod` complete successfully → required CI checks pass on the promoted commit → human production approval recorded (GitHub `production` environment required reviewers, where the plan allows — ADR-002 §5) → Render production deploy via each service's secret deploy hook with `ref=<release commit SHA>` (https://render.com/docs/deploy-hooks, retrieved 2026-07-15; health-check gated: 2xx/3xx within 5 s per https://render.com/docs/health-checks, retrieved 2026-07-14) → Vercel production deploy via CLI: `vercel pull --yes --environment=production` → `vercel build --prod` → `vercel deploy --prebuilt` (https://vercel.com/guides/how-can-i-use-github-actions-with-vercel, retrieved 2026-07-15).
5. Verify: API `/health`; one smoke analysis run; frontend loads against prod API; check Sentry/logs for new errors.
6. Record the release in the ops log (tag, migration IDs, verifier).

### 1.3 Env var changes are deploys
Rollbacks do **not** restore env vars on Render or Vercel (ADR-003 R1/R2). Therefore: announce the change, record variable **name + environment (never the value)** in the ops log, apply to staging first, verify, then prod.

---

## 2. Rollback procedures

### 2.1 Frontend (Vercel Instant Rollback)
Use when: bad frontend release in production.
1. Vercel dashboard → project → select the last known-good production deployment → **Instant Rollback** [confirm at first use]. Takes effect in seconds at the routing layer (https://vercel.com/docs/instant-rollback, retrieved 2026-07-14).
2. Eligibility: only deployments previously aliased to production. On Hobby you can only roll back to the **immediately previous** deployment; Pro/Enterprise any previously-aliased one (same source).
3. **IMPORTANT:** after rollback, Vercel disables auto-assignment of production domains — new pushes to `production` will NOT go live until you end the rollback/promote a new deployment (same source). Do not forget this step after shipping the fix.
4. Env vars are unchanged by the rollback (same source) — if the incident was env-var-caused, fix the variable and redeploy instead.

### 2.2 API / background worker (Render rollback)
Use when: bad code release of `nycdf-api` or `nycdf-worker-jobs`.
1. Render dashboard → service → Deploys → previous successful deploy → **Rollback** [confirm at first use]; also available via API (https://api-docs.render.com/reference/rollback-deploy, retrieved 2026-07-14). No rebuild — the old artifact is reused (https://render.com/docs/rollbacks, retrieved 2026-07-14).
2. Caveats (same source): env-group changes since that deploy are NOT reflected; a deleted env group is silently omitted; current service configuration is kept.
3. Verify `/health` and a smoke request; then fix forward on `main`.

### 2.3 Cron job (no rollback support — redeploy)
Cron jobs are not listed as rollback-eligible (https://render.com/docs/rollbacks lists web, private, worker — retrieved 2026-07-14).
1. `git revert` the offending commit on the tracked branch, push, then deploy: staging redeploys automatically on the push; in production trigger the cron service's deploy hook (or a manual dashboard deploy) — production auto-deploy is off (ADR-003 D2).
2. If the next scheduled run must be prevented immediately: suspend the cron service in the Render dashboard [confirm at first use].

### 2.4 Infrastructure change (`render.yaml`)
Service rollback does not revert Blueprint/topology changes. Revert the `render.yaml` commit and push; verify the Blueprint sync result in the dashboard [confirm at first use: whether Blueprint syncs still apply automatically with `autoDeployTrigger: off`, or must be applied manually].

### 2.5 Database — failed or bad migration (Supabase)
Policy: **forward-only; never write down-migrations; never edit an applied migration file** (ADR-003 R3).

Failed migration in prod pipeline:
1. The dependent deploy jobs do not run because they are declared with `needs:` on the migration job in the production deploy workflow (ADR-003 D5 — a future implementation task; this `needs:` chain is the ONLY mechanism that enforces the halt). Platform auto-deploys are disabled in production, so no deploy proceeds on its own. **If deploying manually (D5 workflow not yet implemented): STOP — trigger no deploy hook and no frontend deploy.** Do not re-run blindly.
2. Capture: CI log + contents of `supabase_migrations.schema_migrations` on `nycdf-prod`.
3. Classify and act:
   - **Not applied at all** → fix the SQL in a NEW migration file, land via `main` → staging → prod.
   - **Partially applied / history desynced** → write a corrective forward migration; realign history with `supabase migration repair --status applied|reverted <timestamp>` (updates tracking table only, executes no SQL — https://supabase.com/docs/reference/cli/supabase-migration-repair, retrieved 2026-07-14); re-run the pipeline.
   - **Data corrupted** → escalate to owner for restore decision (2.6).
4. Log the incident; add a regression check to staging verification.

### 2.6 Database — restore (last resort; owner approval required)
1. Prod (`nycdf-prod`, Pro plan) has daily backups with 7-day retention; if the PITR add-on is enabled, restore to a point with seconds-level granularity instead (PITR replaces daily backups) — https://supabase.com/docs/guides/platform/backups, retrieved 2026-07-14.
2. The project is **inaccessible during restore**; downtime grows with DB size (same source). Announce downtime first.
3. Supabase dashboard → Database → Backups → choose backup/point → review → confirm [confirm at first use].
4. After restore: replay ingestion for the lost window from source provenance (PRD 9/10); verify row counts and latest `analysis_runs` integrity; re-enable deploys.

---

## 3. Decision matrix (which procedure)

| Symptom | Procedure |
|---|---|
| Bad frontend release | 2.1 |
| Bad API/worker code release | 2.2 |
| Bad cron behavior | 2.3 |
| Wrong/missing env var | fix var + redeploy (1.3) — never a platform rollback |
| Bad `render.yaml` change | 2.4 |
| Migration failed in CI | 2.5 |
| Broad data corruption | 2.6 |

## 4. Standing rules

- Staging is the rehearsal: nothing reaches prod that did not run identically on staging (migrations included).
- Expand → deploy → contract (ADR-003 D4): app rollbacks must never require schema rollbacks.
- Free Supabase projects pause after 1 week of inactivity (https://supabase.com/docs/guides/platform/free-project-pausing, retrieved 2026-07-14): if `nycdf-dev`/`nycdf-staging` are paused, unpause from the dashboard before deploying [confirm at first use].
- Every incident and every prod promotion is recorded (who, what, when, evidence links).
