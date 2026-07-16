# Research capture — Render Next.js hosting + preview environments + blueprint fields

- **Captured by:** orchestrator (WebFetch, official Render docs), 2026-07-16
- **Purpose:** input evidence for M0-T011 / ADR-004 (drop Vercel; serve Next.js from Render — owner decision 2026-07-14). Producer must cite this file, not memory. Summarizer-mediated fetches: quotes below are as returned by the fetch tool against the official pages; the ADR producer should treat any load-bearing ambiguity as a point to re-verify against the same URLs.

## 1. `https://render.com/docs/deploy-nextjs-app` (retrieved 2026-07-16)

- Service-type split: **Web Service** for "a full Next.js app with server-side logic" (SSR); **Static Site** for Next.js "static export".
- Web service: language Node; build `yarn; yarn build` (npm equivalents fine); start `yarn start`. Node version pinning documented separately ("Specifying a Node Version").
- Build caching: "Render services do not persist this directory [.next/cache], which means builds do not benefit from the cache by default." Render persists `$XDG_CACHE_HOME` between builds; a custom build script can restore/save `.next/cache` there.
- No explicit page statements on pricing-tier limitations for SSR.

## 2. `https://render.com/docs/preview-environments` (retrieved 2026-07-16)

- **"Preview environments require a Pro plan or higher."** (Cost consideration for the ADR: Vercel previews were free-tier; Render multi-service preview environments are Pro-gated. Single-service **service previews** are documented separately at `/docs/service-previews` — the ADR should evaluate service previews for the web service as the low-cost option.)
- Enablement via Blueprint `previews.generation`: `manual` (previews only when PR title contains `[render preview]`) or `automatic` (every PR; `[skip preview]` etc. to skip). Deprecated `previewsEnabled: true` = automatic.
- "A preview environment creates new instances of the services and datastores defined in your Blueprint. These instances do not copy any data from existing services."
- Env vars: `previewValue` overrides per-variable; **`sync: false` placeholders are NOT copied to preview environments**; separate dashboard env group recommended for preview secrets.
- Cost controls: `previews.plan`, `previews.numInstances`, `previewPlan` (databases), `previews.expireAfterDays` auto-expiry; "Preview resources are billed just like regular Render services and are prorated by the second."
- Lifecycle: auto-destroyed when the PR merges/closes; "View deployment" link in the PR.

## 3. `https://render.com/docs/blueprint-spec` (retrieved 2026-07-16)

- `runtime: node` for native Node web services.
- **`autoDeployTrigger`** (replaces deprecated `autoDeploy`): allowed values `"commit"`, `"checksPass"`, `"off"`; **default is `commit` if omitted**. The `"off"` value MUST be quoted in YAML (bare `off` is YAML-1.1 boolean false) — confirms the M0-T006 G3 R1 recommendation.
- `previews.generation: manual|automatic` replaces deprecated `pullRequestPreviewsEnabled`.
- `buildCommand` + `startCommand` required for non-Docker services; `envVars` with `sync: false` (prompt for secret) or `generateValue: true`.

## Implications the ADR-004 producer must weigh (not conclusions)

1. SSR Next.js = a second Render **web service** in render.yaml with `autoDeployTrigger: "off"` in production, per the accepted M0-T006 deploy model (Actions-gated deploys only).
2. Preview strategy decision: (a) Pro-plan preview environments, (b) single-service service previews for the frontend only, or (c) no previews initially — cost/benefit belongs in the ADR trade-off table (this was Vercel's strongest feature).
3. Build-cache script is an optimization, not a requirement — note it, don't block on it.
4. `sync: false` secrets not propagating to previews affects any future preview strategy for the API service.
