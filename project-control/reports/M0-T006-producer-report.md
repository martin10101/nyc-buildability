# Agent Report

- Task ID: M0-T006 — ADRs + Render Blueprint + deploy/rollback procedures
- Agent: cloud-architect (producer)
- Worktree/branch: local, branch `main` (doc-only exclusive file scope per G0 readiness)
- Requested status: awaiting_gate
- Progress percent: 90 (all outputs authored and self-checked; see Known limitations for control-plane command denials)

## Work completed

1. Read task packet, PRD 14/26/32.5/35, `docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md`, `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`, `docs/research/M0-T002-geoclient-address-resolution.md`, `project-control/reports/M0-T006-G0-readiness.json`.
2. Researched official platform documentation (Render, Supabase, Vercel, GitHub) — 11 targeted searches restricted to official domains; retrieval date 2026-07-14 for all claims (method note in Limitations).
3. Authored ADR-001 (cloud architecture + alternatives), ADR-002 (dev/staging/prod separation + promotion rules + prod approval), ADR-003 (deploy pipelines, per-service rollback, forward-only migration policy, failed-migration handling, backups/PITR).
4. Authored `render.yaml` Blueprint: FastAPI web service + background worker + cron placeholder, env vars as `sync: false` references only, zero literal secrets, ADR cross-references in comments.
5. Authored operator runbook `docs/DEPLOYMENT_AND_ROLLBACK.md` distilled from ADR-003.

## Files changed

- `docs/adr/ADR-001-cloud-architecture.md` (new)
- `docs/adr/ADR-002-environment-separation.md` (new)
- `docs/adr/ADR-003-deployment-and-rollback.md` (new)
- `render.yaml` (new, repo root)
- `docs/DEPLOYMENT_AND_ROLLBACK.md` (new)
- `project-control/reports/M0-T006-producer-report.md` (this file)

All within allowed paths; no forbidden path touched. Total added size < 60 KB (well under 1 MB budget).

## Contracts/migrations changed

None (research/documentation task). `render.yaml` declares infrastructure but deploys nothing until a human creates the Blueprint in Render.

## Acceptance scenarios created

None new — bound by packet scenarios S1–S5. Evidence below.

## Commands and tests run

Actual outputs, embedded verbatim:

1. Repo survey (Bash, succeeded):
```
$ wc -l PRD.md docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md docs/research/M0-T002-geoclient-address-resolution.md
 1133 PRD.md
   96 docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md
   86 docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md
  314 docs/research/M0-T002-geoclient-address-resolution.md
 1629 total
$ ls docs/adr
ls: cannot access 'docs/adr': No such file or directory   # confirmed net-new before authoring
```

2. Control-plane claim (DENIED by the session permission system — disclosed, not worked around):
```
$ python tools/project_control.py claim --task-id M0-T006 --agent cloud-architect --worktree local
-> "Permission to use Bash has been denied." (identical denial via PowerShell)
```

3. YAML validation attempt (DENIED — python execution blocked in this session):
```
$ python -c "import yaml; yaml.safe_load(open('render.yaml'))..."
-> "Permission to use Bash has been denied."
```
Fallback performed: manual line-by-line structural review of `render.yaml` (see Expected versus actual results). This substitution is disclosed per the task's G2 instruction ("if not, use ... careful manual check and disclose").

## Expected versus actual results

| Check | Expected | Actual |
|---|---|---|
| S1 render.yaml structure | web + worker + cron, env refs only | PASS (manual review): top-level keys `previews`, `services`; 3 services (`type: web` nycdf-api / `type: worker` nycdf-worker-jobs / `type: cron` nycdf-cron-source-monitor); every service has name/runtime/rootDir/plan/region/buildCommand/startCommand; cron has quoted `schedule: "0 6 * * *"`; web has `healthCheckPath: /health` |
| S1 no literal secrets | zero secret values | PASS: grep-level review — the ONLY `value:` key in the file is `ENVIRONMENT=production` (non-secret); all 17 other env var entries are `sync: false` |
| S1 YAML syntax | machine-parse | SUBSTITUTED (disclosed): programmatic parse denied by session permissions; manual review found consistent 2-space indentation, quoted strings for values containing `:`/`*`/`$`, space-prefixed inline comments, no tabs, no duplicate keys per mapping. Residual risk recorded for reviewer re-run (G3 reviewer should run `python -c "import yaml,io; yaml.safe_load(io.open('render.yaml',encoding='utf-8'))"`) |
| S2 alternatives | Render vs alternatives, consistent with PRD 14.1 | PASS: ADR-001 records Railway (replaced by decision of record), Fly.io, AWS, Supabase-only Edge Functions (rejected by PRD 14.2 prohibition), microservices-on-Render; decision = PRD 14.1 stack, no deviation |
| S3 environments | concrete Supabase/Render/Vercel/GitHub mapping + promotion rules | PASS: ADR-002 §2 mapping table (nycdf-dev/-staging free projects, nycdf-prod Pro; Render project environments incl. protected prod; Vercel branch model; GitHub environments), §4 promotion rules, §5 prod approval = human owner (G7) incl. honest private-repo enforcement gap |
| S4 rollback per service | Render rollback, Vercel instant rollback, migration policy incl. failure handling | PASS: ADR-003 R1 (Vercel: eligibility, Hobby limit, env vars unchanged, auto-assign disabled after rollback), R2 (Render: web/private/worker eligible, skip-build caveats, cron NOT eligible -> git revert), R3 (forward-only, `migration repair` semantics, 5-step failed-migration procedure, backups/PITR with restore-downtime caveat) |
| S5 provenance | every platform claim cited URL + 2026-07-14 | PASS: source tables in all three ADRs + inline citations in render.yaml comments and runbook; anything not confirmable is marked "confirm at first use" / "requires verification at first setup" instead of guessed |

## Source/API evidence

All retrieved 2026-07-14. Claim → official source:

| # | Claim used in deliverables | Source |
|---|---|---|
| 1 | Blueprint = `render.yaml` at repo root; IaC model | https://render.com/docs/infrastructure-as-code |
| 2 | `sync: false` prompts for value at deploy; ignored on Blueprint update; NOT copied into preview environments; `fromService`/`fromDatabase`/`fromGroup`/`generateValue` exist; `previews.generation: manual|automatic` | https://render.com/docs/blueprint-spec |
| 3 | Rollback: web/private/background workers; skips build; env-group changes not reflected; deleted env group omitted; config not overwritten | https://render.com/docs/rollbacks (API: https://api-docs.render.com/reference/rollback-deploy) |
| 4 | Cron schedules evaluated in UTC; per-minute billing, $1/mo minimum per cron job | https://render.com/docs/cronjobs, https://render.com/pricing |
| 5 | Free web services spin down after 15 min; no free tier for workers/cron | https://render.com/docs/free |
| 6 | Background workers run continuously, no inbound traffic | https://render.com/docs/background-workers |
| 7 | Health checks: 2xx/3xx within 5 s; used for zero-downtime deploys | https://render.com/docs/health-checks |
| 8 | Render projects/environments; protected environments (admin-only destructive changes, admin-only shell); network boundary blocking; env groups scoped to one environment | https://render.com/docs/projects, https://render.com/changelog/project-environment-groups |
| 9 | Preview environments: per-PR, auto-destroy on merge/close, `expireAfterDays`, billed at base rate, manual mode via `[render preview]` in PR title, `previews.plan` | https://render.com/docs/preview-environments |
| 10 | Supabase multi-env: separate staging/prod projects + GitHub Actions + CLI secrets (`SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`, project ref) | https://supabase.com/docs/guides/deployment/managing-environments |
| 11 | Branching requires Pro; preview branches ephemeral; persistent branches for staging/QA; pushes apply ./supabase/migrations | https://supabase.com/docs/guides/deployment/branching |
| 12 | Free plan: 2 active projects; paused after 1 week inactivity; paid orgs not auto-paused | https://supabase.com/pricing, https://supabase.com/docs/guides/platform/free-project-pausing |
| 13 | $10/mo compute credits ≈ one Micro; additional database $0.01344/hour | https://supabase.com/docs/guides/platform/manage-your-usage/compute, https://supabase.com/docs/guides/platform/manage-your-usage/branching |
| 14 | Daily backups Pro/Team/Enterprise (7/14/30 days); PITR add-on (Pro+, ≥ Small compute, replaces daily backups, seconds granularity); restore downtime scales with DB size | https://supabase.com/docs/guides/platform/backups |
| 15 | `supabase_migrations.schema_migrations` history table; `migration repair --status applied|reverted` mutates tracking only, runs no SQL | https://supabase.com/docs/reference/cli/supabase-migration-repair (also https://supabase.com/docs/guides/deployment/database-migrations, https://supabase.com/docs/reference/cli/supabase-db-push) |
| 16 | Vercel: production deploys on push to production branch; previews for all other branches/PRs; Custom Environments Pro/Enterprise with branch tracking; per-branch preview env vars | https://vercel.com/docs/deployments/environments |
| 17 | Instant Rollback: routing layer, seconds; previously-production-aliased deployments only; Hobby = immediately previous only; env vars unchanged; cron reverted with deployment; auto-assign of prod domains disabled after rollback; one at a time | https://vercel.com/docs/instant-rollback |
| 18 | GitHub: required reviewers only for public repos on Free/Pro/Team; environments in private repos need Pro/Team/Enterprise | https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments, https://docs.github.com/actions/deployment/targeting-different-environments/using-environments-for-deployment |

## Assumptions and defaults

1. Git model: `main` = staging, `production` = prod release branch (ADR-002 §1) — chosen to make human-gated promotion mechanical; owner may substitute tags-only promotion.
2. Render region `oregon` chosen arbitrarily for co-location; flagged for confirmation against https://render.com/docs/regions before first deploy.
3. `services/api` layout, build tool, and worker/cron entrypoints do not exist yet; all build/start commands in `render.yaml` are marked `[PLACEHOLDER]` and must be reconciled by the services producer before Blueprint creation.
4. Environment variable set (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_DB_URL, GEOCLIENT_SUBSCRIPTION_KEY, ANTHROPIC_API_KEY, SENTRY_DSN) is the minimal initial set inferred from PRD 14/17/23 and M0-T002; it will grow.
5. Naming convention `nycdf-*` assumed acceptable.

## Known limitations

1. **Control-plane commands denied:** `python tools/project_control.py claim/progress/submit` were blocked by the session permission system (Bash AND PowerShell). The task record in `project-control/tasks/M0-T006.json` therefore still shows its pre-task state; the orchestrator must run claim/progress/submit on my behalf. I did NOT modify the task file directly (forbidden path).
2. **Programmatic YAML validation not run** (python execution denied). Manual structural review performed and documented above; G3 reviewer should run the one-line PyYAML parse as independent verification.
3. **Research method:** WebFetch (direct page retrieval) was denied in this session; official-domain-restricted web search summaries of the official pages were used instead. Every claim traces to the cited official URL, but exact page wording was not always independently quoted. Items where this mattered were downgraded to "confirm at first use/setup" flags in ADR-002 §"Items requiring verification", render.yaml comments, and the runbook — no platform behavior was guessed.
4. Specifically NOT verified (flagged, not claimed): Blueprint-per-branch instantiation mechanics for the staging service copies (ADR-002 verification item 1); full valid `region` list; exact dashboard click-paths for Vercel rollback, Render rollback/suspend, Supabase restore and unpause; whether `supabase db push` wraps each migration in a transaction (treated as unknown — failed-migration procedure does not depend on it).
5. Costs cited only where officially documented; no total monthly cost estimate is asserted.

## Security and provenance impact

- Zero secrets in Git: `render.yaml` uses `sync: false` exclusively for sensitive vars; ADR-002 §3 defines the single home for each secret class; PRD 17 service-role-key rule restated in file comments.
- Environment isolation design (separate Supabase projects, Render protected environment + network boundary, scoped env groups) prevents staging→prod data access by construction.
- Every platform-behavior claim carries provenance (URL + retrieval date) per S5.

## New risks/dependencies

1. **R: private-repo approval gap** — required reviewers unavailable for private repos on non-Enterprise plans; prod promotion enforcement is partly procedural (ADR-002 §5). Owner accepts or makes repo public/upgrades plan.
2. **R: render.yaml placeholders** — Blueprint must not be deployed until `services/api` exists and commands are reconciled (marked in-file).
3. **D: services/api producer** must expose `/health` and the worker/cron entrypoints named in `render.yaml` (or update the file in a follow-up task).
4. **R: free-project pausing** — dev/staging Supabase projects pause after 1 week inactivity; runbook §4 covers unpausing.

## Recommended next tasks

1. Follow-up verification task at Phase-0 cloud setup: confirm the four "confirm at first use" items (Blueprint branch mechanics, region list, dashboard click-paths, db push transaction behavior) with live accounts and update ADR-002/003 + runbook.
2. services/api scaffolding task: create `/health`, worker and source-monitor entrypoints; reconcile `render.yaml` placeholders (requires edit rights on both scopes or a coordinated pair of tasks).
3. CI task (owned by .github producer): GitHub Actions migration workflow per ADR-003 D3 with `staging`/`production` GitHub environments.
4. Owner human actions (candidate for docs/HUMAN_ACTIONS_REQUIRED.md by its owner): create Supabase projects, Render Blueprint, Vercel project; decide PITR add-on timing at launch (ADR-003 R3).
