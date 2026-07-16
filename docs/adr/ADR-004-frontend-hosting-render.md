# ADR-004: Frontend Hosting on Render — Vercel Dropped

- **Status:** Accepted (owner decision 2026-07-14; recorded per PRD §34 full-product delivery policy)
- **Date:** 2026-07-16 (decision date 2026-07-14 — see `docs/HUMAN_ACTIONS_REQUIRED.md` §3, blocker B-003)
- **Producer:** cloud-architect (task M0-T011)
- **Deciders:** Human project owner (final; this is an owner-approved deviation from PRD §14.1)
- **Related:** ADR-001 (providers — amended by this ADR), ADR-002 (environments — amended), ADR-003 (deployment/rollback — amended, D1 replaced), `render.yaml` (frontend web service added), `docs/DEPLOYMENT_AND_ROLLBACK.md` (§2.1 replaced)
- **Evidence base:** `docs/research/render-nextjs-previews-2026-07-16.md` (orchestrator-captured official Render docs, retrieved 2026-07-16). Every Render factual claim below cites that file ("research file §N") and/or the official URL it captures. Vercel-side facts cite the source tables of ADR-002/ADR-003 (official Vercel docs retrieved 2026-07-14/15).

## Context

PRD §14.1 names **Vercel** as the frontend host ("Next.js web frontend, preview deployments"), and ADR-001/002/003 plus the operator runbook were written on that basis. On **2026-07-14 the project owner directed** that the frontend be served from **Render** instead, preferring a single deployment platform (`docs/HUMAN_ACTIONS_REQUIRED.md` §3: "Owner decision 2026-07-14: prefer serving the frontend from Render instead of Vercel"), which put blocker **B-003 (create Vercel account/project) on hold** pending this ADR. ADR-003 D1 (as amended 2026-07-15) already anticipated this: "If pending decision ADR-004/M0-T011 (drop Vercel; frontend on Render) is approved, this Vercel CLI mechanism is replaced by the same Render deploy-hook mechanism as D2."

Verification question for this ADR: can Render host the SSR Next.js frontend with the same controlled deploy/rollback model as the backend, and what is lost relative to Vercel (chiefly the free per-PR preview deployments)?

Official-doc findings (research file):

- **SSR Next.js runs as a Render web service.** Render's official guide deploys "a full Next.js app with server-side logic" as a **Web Service** (language Node; build `yarn; yarn build`, npm equivalents fine; start `yarn start`); a Static Site is only for Next.js static export (research file §1; https://render.com/docs/deploy-nextjs-app, retrieved 2026-07-16).
- **Multi-service preview environments are Pro-gated.** "Preview environments require a Pro plan or higher"; preview resources "are billed just like regular Render services and are prorated by the second", with cost controls (`previews.plan`, `previews.numInstances`, `previews.expireAfterDays`) and auto-destroy on PR merge/close. `sync: false` env vars are **not** copied into preview environments (research file §2; https://render.com/docs/preview-environments, retrieved 2026-07-16).
- **Single-service "service previews" exist** as a separately documented, lower-cost option (research file §2 pointer to https://render.com/docs/service-previews). Their plan-gating and exact billing were **not captured** in the research file and must be verified against that URL before any enablement — no claim is made here.
- **Blueprint mechanics.** `runtime: node` for native Node web services; `autoDeployTrigger` allowed values `"commit"`, `"checksPass"`, `"off"` (default `commit` if omitted); the value `"off"` **must be YAML-quoted** because bare `off` is a YAML-1.1 boolean (research file §3; https://render.com/docs/blueprint-spec, retrieved 2026-07-16).
- **Build-cache caveat (optimization only).** Render does not persist `.next/cache` between builds by default; a custom build script can save/restore it via the persisted `$XDG_CACHE_HOME` (research file §1). Noted as a later optimization; not a requirement for first deploy.

## Decision

1. **The Next.js frontend (`apps/web`) is served from a Render web service** (`nycdf-web`, `runtime: node`, `rootDir: apps/web`), declared additively in `render.yaml` alongside the API/worker/cron services (research file §1/§3). **Vercel is dropped from the architecture**; no Vercel account, project, `vercel.json`, or `VERCEL_*` secret is created.
2. **The frontend inherits the exact backend deploy model** (ADR-003 D2/D5): production sets `autoDeployTrigger: "off"` (quoted — research file §3) and deploys only via its secret deploy hook from the future GitHub Actions production deploy workflow, after migrations succeed and human approval is recorded; the staging copy keeps `autoDeployTrigger: commit` from `main`, like every other staging service (ADR-002 §4.2).
3. **Frontend rollback uses Render deploy rollback** (dashboard/API, no rebuild — ADR-003 R2 semantics now govern the frontend too; ADR-003 R1 is amended accordingly). Vercel Instant Rollback is no longer part of the architecture.
4. **Frontend env vars stay publishable-only** on the frontend service (`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` per `apps/web/.env.example`); the service-role key and all privileged credentials remain forbidden anywhere under the frontend (PRD §17).

## Trade-offs: Vercel vs Render web service

| Dimension | Vercel (prior plan) | Render web service (this decision) | Basis |
|---|---|---|---|
| SSR Next.js support | First-class (git-integrated) | **Equivalent**: official guide deploys full SSR Next.js as a web service | research file §1 |
| Per-PR preview deployments | Free on Hobby, automatic per PR (ADR-002 source: vercel.com/docs/deployments/environments, retrieved 2026-07-14) | **Lost at $0**: preview environments require a **Pro plan or higher**; preview resources billed like regular services, prorated by the second. Single-service previews exist but are unverified for plan/cost | research file §2 |
| Edge network / global CDN | Vercel's edge-network delivery (prior ADR basis) | No equivalent claim made for a Render web service — the research file contains no edge/CDN statement, so **this benefit is treated as lost**. Accepted: NYC-focused, auth-gated analyst application, not a public content site | research file (absence); ADR-002 sources |
| Production rollback | Instant Rollback at the routing layer, seconds, but Hobby limited to the immediately previous deployment; auto-assign disabled after rollback (ADR-003 R1 sources) | Deploy rollback without rebuild, ~service restart time; no Hobby-style eligibility cliff; same mechanism as API/worker (render.com/docs/rollbacks, retrieved 2026-07-14 — ADR-003 R2) | ADR-003 R1/R2 |
| Deploy control (Actions-gated prod) | Required disabling git deploys via `vercel.json` + a separate Vercel CLI pipeline + 3 extra CI secrets (`VERCEL_TOKEN`/`ORG_ID`/`PROJECT_ID`) | **Identical mechanism as the backend**: `autoDeployTrigger: "off"` + secret deploy hook from the same workflow; zero new mechanisms | ADR-003 D2/D5; research file §3 |
| Operations | Three dashboards (Supabase, Render, Vercel) + GitHub; two frontend/backed rollback semantics; two secret stores for deploy credentials | **Two dashboards** (Supabase, Render) + GitHub; one rollback semantic for all app services; one deploy-hook pattern; fewer secrets | ADR-001 consequences (amended) |
| Cost floor | Frontend $0 on Vercel Hobby | Free Render web services spin down after 15 min of inactivity (render.com/docs/free, retrieved 2026-07-14) — unacceptable for a client-facing app at launch, so the production frontend is declared `plan: starter`: **one new paid instance per instantiated environment** (prod at launch; staging when instantiated). ADR-002 §6 cost sequencing absorbs this; nothing is billed by this ADR itself | ADR-001 sources; ADR-002 §6 |
| Build speed | Vercel-managed build caching | `.next/cache` not persisted by default; optional `$XDG_CACHE_HOME` build-script workaround later | research file §1 |

## Preview strategy (explicit decision)

Options evaluated, with cost basis from the research file:

- **(a) Multi-service preview environments** — per-PR copies of all Blueprint services. Requires **Pro plan or higher**; preview resources billed like regular services, prorated by the second (research file §2). Exact Pro plan pricing was not captured in the research file; it must be read from https://render.com/pricing by the owner before any upgrade. Most capability, highest and plan-gated cost; also `sync: false` secrets do not propagate to previews, requiring a separate preview env-group workflow (research file §2).
- **(b) Frontend-only service previews** — single-service previews for `nycdf-web` (https://render.com/docs/service-previews, via research file §2). Documented as the lower-cost single-service option, but plan-gating and billing were not captured; **must be verified against the official page before enablement**.
- **(c) No previews initially** — $0; PR review relies on CI (lint/typecheck/build already run in GitHub Actions) plus staging verification on `main`, which is already the acceptance path for every task (ADR-002 §4.2).

**Decision: (c) — no frontend previews initially**, with a planned re-evaluation of **(b)** when sustained frontend UI work begins (M2 Property/Confirm screens), and **(a)** only if the workspace independently moves to a Pro plan. Rationale: `apps/web` is a placeholder until M2, so previews currently review nothing of value; preview loss is the single largest cost of dropping Vercel and is accepted consciously rather than paid for pre-emptively; the existing Blueprint `previews.generation: manual` block stays opt-in-only and — because preview environments are Pro-gated (research file §2) — creates nothing and bills nothing on the current plan.

> **HUMAN ACTION (billing) — flagged, not executed:** enabling option (a) requires a Render Pro upgrade, and option (b) may have plan/billing implications (unverified). Neither is enabled by this task; any enablement is an owner billing decision recorded via `docs/HUMAN_ACTIONS_REQUIRED.md` at the time it is proposed. This task performs **no** Render account operations and **no** purchases.

## PRD deviation (explicit)

PRD §14.1 names Vercel as a required provider ("Vercel — Use for: Next.js web frontend, preview deployments"), and PRD §26/§30 reference it. This ADR records an **owner-approved architectural deviation** from PRD §14.1, made by the project owner on 2026-07-14, and documents it per PRD §34 (full-product delivery policy: no hidden divergence) — the same standard ADR-001 applied when rejecting Railway. All other PRD §14.1 provider assignments (Supabase, Render, GitHub) are unchanged. PRD text itself is not edited by this task; this ADR is the deviation record of authority.

## Consequences

Positive:
- One deployment platform for every application service; one Blueprint, one deploy-hook mechanism, one rollback semantic, one dashboard fewer.
- The production frontend is now governed by the identical Actions-gated deploy chain as the backend (migrations → checks → human approval → deploy hooks), removing the Vercel-specific pipeline branch (old ADR-003 D1), the planned `vercel.json` follow-up task, and the `VERCEL_TOKEN`/`VERCEL_ORG_ID`/`VERCEL_PROJECT_ID` secrets.
- B-003 (Vercel account) can be closed: this ADR supersedes the Vercel plan (orchestrator action after acceptance).

Negative / accepted costs:
- **Free per-PR frontend previews are lost** (Vercel's strongest feature for this project). Mitigated by CI + staging verification; re-evaluated at M2 per the preview strategy above.
- **Edge-network delivery is not claimed** on Render; accepted for an auth-gated, NYC-focused analyst tool.
- **New paid instance** for a warm production frontend (`starter`) at launch, and for staging when instantiated (free tier spins down after 15 min). Absorbed into ADR-002 §6 cost sequencing.
- Rollback takes ~service-restart time instead of Vercel's seconds-level routing-layer switch; identical to the API's accepted rollback profile.
- Builds do not benefit from `.next/cache` by default (research file §1); optional build-script optimization deferred.

## Rollback path (returning to Vercel later, if evidence justifies it)

The frontend remains a standard Next.js app with no Render-specific code, so reverting is a configuration exercise, fully documented in git history:

1. Reopen B-003: owner creates the Vercel account/project (human action).
2. Restore the superseded ADR-003 D1 mechanism (preserved in git history and in the superseded-marked source rows): `vercel.json` with `git.deploymentEnabled: {"production": false}`, Vercel CLI deploy job (`vercel pull` → `vercel build --prod` → `vercel deploy --prebuilt`), and the three `VERCEL_*` GitHub `production` environment secrets.
3. Remove the `nycdf-web` service from `render.yaml` (additive block; removal does not touch the API/worker/cron definitions) and delete the Render service.
4. Reverse the ADR-001/002/003/runbook amendments by a new ADR superseding this one.

No data migration is involved at any point: the frontend is stateless; all persistent data stays in Supabase (PRD §14.3).

## Sources

| Claim | Source |
|---|---|
| SSR Next.js = Render web service; Node; build/start commands; static export = static site | `docs/research/render-nextjs-previews-2026-07-16.md` §1 (https://render.com/docs/deploy-nextjs-app, retrieved 2026-07-16) |
| `.next/cache` not persisted by default; `$XDG_CACHE_HOME` workaround | research file §1 (same page) |
| Preview environments require Pro plan or higher; billed like regular services, prorated by the second; cost controls; `sync: false` not copied; auto-destroy on merge/close | research file §2 (https://render.com/docs/preview-environments, retrieved 2026-07-16) |
| Service previews exist as single-service option (plan/billing NOT verified) | research file §2 pointer (https://render.com/docs/service-previews — verify before enablement) |
| `runtime: node`; `autoDeployTrigger` values `"commit"`/`"checksPass"`/`"off"`, default `commit`; `"off"` must be YAML-quoted (bare `off` is YAML-1.1 boolean) | research file §3 (https://render.com/docs/blueprint-spec, retrieved 2026-07-16) |
| Free web services spin down after 15 min of inactivity | https://render.com/docs/free, retrieved 2026-07-14 (ADR-001 sources) |
| Render deploy rollback: no rebuild, web services eligible, env-group caveats | https://render.com/docs/rollbacks, retrieved 2026-07-14 (ADR-003 R2) |
| Vercel prior-plan facts (free Hobby previews, Instant Rollback semantics, CLI pipeline, `git.deploymentEnabled`) | ADR-002/ADR-003 source tables (official Vercel docs, retrieved 2026-07-14/15) — retained as historical basis only |
| Owner decision and B-003 hold | `docs/HUMAN_ACTIONS_REQUIRED.md` §3 (2026-07-14) |
