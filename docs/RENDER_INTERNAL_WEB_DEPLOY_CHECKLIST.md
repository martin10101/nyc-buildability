# Render internal web deploy — owner-executed checklist (D-043)

**Task:** M5-T024 · **Directive:** D-043 (D-043-R001..R004) · **Date authored:** 2026-09-12

This is the exact, **owner-executed** checklist to stand up `apps/web` as an **internal /
unlisted** Render web service on the existing Hobby workspace, pointed at the existing private
`nycdf-api` service. Every dashboard action below is performed or confirmed by the **owner**
(D-043-R003); no agent touches the Render dashboard, and no credential, key, or real service URL
appears in this file — placeholders only (D-043-R002).

Do the steps **in the printed order.** Two orderings are load-bearing and called out inline:
web env vars must be set **before the first build**, and the new web origin must exist **before**
the CORS entry on `nycdf-api`.

---

## 0. Context and preconditions (read first)

- **What already exists.** The Render Blueprint was created 2026-09-11 from branch
  `candidate/D-024-mrl-option-b` on a **Hobby workspace**; `nycdf-api` is LIVE (`starter`, region
  `oregon`, health `/api/v1/health` green), `ENVIRONMENT=staging`, `GEOCLIENT_SUBSCRIPTION_KEY`
  entered. `nycdf-web` was deliberately **withheld** from `render.yaml` (commit `23817a9f`), so it
  does **not** exist yet and is **not** Blueprint-managed. (Source: `docs/MVP_AGENDA.md` §I;
  `render.yaml` note block "3) Next.js frontend web service `nycdf-web` — WITHHELD".)
- **Why now.** D-042 produced the project's first fully green CI at Next.js 15.5.24, satisfying the
  prior "no hosted web deploy before the Next.js RCE fix" restriction (D-043-R001;
  `project-control/directives/D-043-internal-web-deploy/source-001.md`).
- **This is NOT a public launch.** No public listing, marketing, indexing, or removal of the
  internal/dev posture. The visual redesign remains a separate later effort. (D-043-R004.)
- **Honest privacy meaning.** "Private" here means **unlisted URL + feature-flag-gated +
  internal/dev labeling** — it is **NOT secret-proof.** The API has **no authentication**
  (`services/api/app/main.py` module docstring lines 6-11; `docs/MVP_AGENDA.md` §I). See §5 before
  turning the internal flag on for the API.
- **You will create this service by hand in the dashboard, NOT via the Blueprint.** The
  `render.yaml` `nycdf-web` block is still withheld; creating the Blueprint's service would also
  redeploy every other declared service. A hand-created service is **not Blueprint-managed** — see
  the restoration debt and duplicate-service caution in §8.

Placeholders used below (the owner fills each with the real value **in the dashboard only** — never
in a repo file, commit, or chat):

| Placeholder | Meaning |
|---|---|
| `<owner-pastes-private-API-URL>` | the private `nycdf-api` base origin (e.g. its scheme+host, no trailing slash) |
| `<new-web-service-origin>` | the origin Render assigns the new web service, captured in §4 |

---

## 1. Create the web service

Render dashboard → **New** → **Web Service** → connect the `nyc-buildability` repository.
(Repo name source: `docs/MVP_AGENDA.md` §J2. The click-path label is Render UI wording — **[confirm
in the dashboard UI]**.)

Set, in this order:

1. **Repository:** `nyc-buildability`.
2. **Branch:** `candidate/D-024-mrl-option-b`.
   - **Not `main`** — `main` is roughly 900 commits behind and does not carry this work
     (`docs/MVP_AGENDA.md` §J2, "point at branch `candidate/D-024-mrl-option-b`, not `main`").
3. **Root directory:** `apps/web`.
   - Matches the withheld `nycdf-web` block's `rootDir: apps/web` (git history at `23817a9f~1`,
     recovered for this checklist) and the monorepo layout.
4. **Runtime / language:** **Node**.
   - Withheld block `runtime: node`; the frontend is a full SSR Next.js app served as a **Web
     Service** (`docs/research/render-nextjs-previews-2026-07-16.md` §1).
5. **Node version = 22** (must match CI).
   - CI pins `node-version: 22` in `.github/workflows/ci.yml` (three `setup-node` steps).
     `apps/web/package.json` declares **no** `engines` field, so Render will not infer 22 from the
     repo — you must set it explicitly.
   - **Mechanism — verify in the dashboard UI.** Render documents Node-version pinning on a
     dedicated "Specifying a Node Version" page, but the repo's research capture
     (`docs/research/render-nextjs-previews-2026-07-16.md` §1) records only that the page exists,
     **not** the exact field. Set the Node version to **22** using whichever mechanism the current
     Render UI offers (commonly a `NODE_VERSION` environment variable, or a `.node-version` file;
     the env-var route keeps it visible next to the other env vars in §2). Confirm the build log
     shows Node 22 before relying on the service. **[confirm in the dashboard UI — not evidenced in
     the repo]**
6. **Build command:** `npm ci && npm run build`.
   - Withheld block `buildCommand: "npm ci && npm run build"`; `apps/web/package.json` `build` =
     `next build`; `package-lock.json` is committed, so `npm ci` is deterministic.
7. **Start command:** `npm run start`.
   - Withheld block `startCommand: "npm run start"`; `apps/web/package.json` `start` = `next start`.
   - **$PORT binding:** `next start` listens on the `PORT` environment variable that Render injects,
     so `npm run start` binds `$PORT` automatically. If you prefer an explicit binding, set the
     start command to `npm run start -- -p $PORT`. (Next.js `next start` honors `PORT`;
     **[confirm in the dashboard UI]** that the deploy log shows the app listening on the
     Render-provided port.)
8. **Plan — your choice; understand the tradeoff:**
   - **Free (Hobby):** no cost, but the service **spins down after ~15 minutes of inactivity** and
     cold-starts on the next request (`render.yaml` `nycdf-api` plan comment;
     the withheld `nycdf-web` block's plan comment). Fine for an internal/dev demo you can wait a
     few seconds to wake.
   - **Starter (paid):** stays warm. The withheld `nycdf-web` block declared `plan: starter` as the
     client-facing target, but that was for a public launch — **not** this internal deploy. Pick
     what suits an internal demo; this is a billing decision reserved to you.
9. **Region:** `oregon`.
   - Co-locate with `nycdf-api` (`render.yaml` `nycdf-api` `region: oregon`; withheld block
     `region: oregon`).
10. **Health check path:** `/`.
    - The Next.js root page serves as the health endpoint (withheld block `healthCheckPath: /`).
      Render treats a 2xx/3xx within 5 s as healthy.
11. **Auto-deploy:** leave platform auto-deploy **off** for now (this is an internal, manually
    controlled deploy). See §7 for the Blueprint Auto Sync confirmation, which is a separate switch.

**Do not click "Create / Deploy" yet** — set the environment variables in §2 first (§3 explains why).

---

## 2. Set the web-service environment variables — BEFORE the first build

Set these on the **new web service** in the dashboard, **before** you trigger the first build:

1. **`INTERNAL_RULE_EVAL_ENABLED` = `1`**
   - Canonical flag name, verbatim from `apps/web/src/lib/rule-evaluation.ts` line 83
     (`INTERNAL_RULE_EVAL_ENABLED_ENV_VAR = "INTERNAL_RULE_EVAL_ENABLED"`).
   - Accepted **true tokens** are `1`, `true`, `yes`, `on` (case-insensitive, trimmed) —
     `TRUE_TOKENS` at `rule-evaluation.ts` line 79. Any other / absent / empty value = disabled
     (fail-safe).
   - This is a **server-read** variable, deliberately **not** prefixed `NEXT_PUBLIC_`, so Next never
     inlines it into the browser bundle (`rule-evaluation.ts` lines 60-65).
   - **The flag alone does NOT surface anything.** Every internal surface is behind a **two-factor
     gate**: the env flag on **AND** a per-request `?ruleeval=on` opt-in. Both together produce the
     single `ruleEvalEnabled` boolean (`apps/web/src/lib/rule-evaluation.ts` lines 96-103, computed
     in `apps/web/src/app/property/page.tsx` line 30). That one boolean gates **both** the
     **address front door** (`<AddressResolutionScreen />`) **and** the draft rule-evaluation
     surface — the only mount point is `apps/web/src/components/property/PropertyLookup.tsx` line 265.
     So on a plain `/property` request (no `?ruleeval=on`) the page shows **only the numeric BBL
     lookup form — no address field** — even with this env flag set. To use the address flow you
     must open `/property?ruleeval=on` (see §9). Absent / empty / any non-true-token value =
     disabled (fail-safe).
2. **`NEXT_PUBLIC_API_BASE_URL` = `<owner-pastes-private-API-URL>`**
   - The browser calls the API **cross-origin** at this base URL
     (`apps/web/src/lib/api.ts` `apiBaseUrl()`, lines 147-154; `apps/web/src/lib/address-api.ts`).
     Default when unset is `http://127.0.0.1:8000` — a **local** address that will not work in
     production.
   - **BUILD-TIME INLINING (do not skip):** `NEXT_PUBLIC_*` variables are compiled into the public
     browser bundle at **build** time, not read at runtime (`apps/web/.env.example` lines 6-8 and
     27-35). If you set or change this value **after** the first build, the old value (the
     `127.0.0.1` default) stays baked in until you **rebuild / redeploy** the web service
     (`docs/DEPLOYMENT_AND_ROLLBACK.md` §1.3, "Env var changes are deploys"). This is the reason
     §2 precedes the build.
   - Paste only the private API origin. It never enters a repo file, commit, or chat (D-043-R002).
3. **`NEXT_PUBLIC_SUPABASE_URL`** and **`NEXT_PUBLIC_SUPABASE_ANON_KEY`** — **leave blank.**
   - These are declared for the frontend (withheld block; `apps/web/.env.example` lines 21-25) but
     Supabase is still blocked on **B-001** (owner Supabase token; `docs/MVP_AGENDA.md` §I). Nothing
     reads them yet; Supabase-backed features are expected-absent (§9). Only publishable values may
     ever go here — never a service-role key (`apps/web/.env.example` lines 12-16).

---

## 3. Trigger the first build

With §2 complete, create / deploy the service. The build runs `npm ci && npm run build`, inlining
the `NEXT_PUBLIC_API_BASE_URL` you set in §2 into the bundle. Wait for the deploy to reach a healthy
state (root `/` returns 200).

**If you ever change `NEXT_PUBLIC_API_BASE_URL` later, you must redeploy** — a plain env-var save
does not re-inline it (`apps/web/.env.example` lines 32-35; `docs/DEPLOYMENT_AND_ROLLBACK.md` §1.3).

---

## 4. Capture the new web origin

From the new service's page, copy its assigned origin (scheme + host, **no trailing slash**) — call
it `<new-web-service-origin>`. You need it for the CORS entry in §6.

**This origin must exist before §6** — the API blocks all cross-origin access until it is listed
(§6 rationale).

---

## 5. Honest exposure note — READ THIS BEFORE §6

The API has **no authentication** (`services/api/app/main.py` docstring lines 6-11;
`docs/MVP_AGENDA.md` §I). Read this **before** setting the internal flag on `nycdf-api` in §6.
Therefore:

- Turning `INTERNAL_RULE_EVAL_ENABLED` on for `nycdf-api` makes the flag-gated internal routes
  **reachable by anyone who holds the API URL** — the flag is a feature toggle, **not** an access
  control.
- **Unlisted is not secret.** Keeping the web URL and API URL private reduces who stumbles onto
  them; it does **not** protect the endpoints from anyone the URL reaches. This is the directive's
  own framing: private = unlisted + flag-gated + internal/dev labeling, **not secret-proof**
  (`project-control/directives/D-043-internal-web-deploy/source-001.md`; requirements
  D-043-R002/R004).
- Accept this consciously: share the URLs only with people you trust, and keep the internal/dev
  labeling and disclaimers intact (D-043-R001/R004). Real access control arrives with the auth
  layer (blocked on **B-001**), not with this deploy.

---

## 6. Set CORS + the internal flag on `nycdf-api`

On the **existing `nycdf-api`** service (dashboard → `nycdf-api` → Environment):

1. **`API_CORS_ALLOWED_ORIGINS` = `<new-web-service-origin>`**
   - **Exact origin only** — `scheme://host[:port]`, comma-separated for multiple, **no wildcard,
     no trailing slash.** Enforcement is in `services/api/app/main.py`:
     `_parse_allowed_origins` (lines 66-82) **raises at startup** on any entry containing `*`
     (the API allows credentialed requests, so a wildcard is forbidden); an unset / empty value
     means **no cross-origin access is granted** (lines 18-19, 74). A misconfigured value makes the
     service fail to start / fail health checks — deliberate.
   - **Why this is load-bearing:** the browser calls `nycdf-api` cross-origin (§2 step 2). Without
     the exact web origin listed here, every browser request from the web service is blocked and the
     app appears broken even though both services are up (`render.yaml` `nycdf-api`
     `API_CORS_ALLOWED_ORIGINS` comment lines 128-135; `docs/DEPLOYMENT_AND_ROLLBACK.md` reconciliation
     note item 5).
2. **`INTERNAL_RULE_EVAL_ENABLED` = `1`** (same true-token rule as §2 step 1).
   - The API reads the **same** canonical flag to mount / gate its internal
     `/api/v1/properties/{bbl}/rule-evaluation` endpoint (`apps/web/src/lib/rule-evaluation.ts`
     lines 54-65, "the SAME name the API service reads"). With it unset, that endpoint returns a
     generic `404` and the web surface shows an honest "not available in this environment" note.
   - **You already read the exposure consequence in §5** — turning this on makes the flag-gated
     routes reachable by anyone holding the API URL (the API has no auth). Set it knowingly.

Save; Render restarts `nycdf-api`. Confirm `/api/v1/health` returns 200 after the restart.

> **Env-var changes are deploys.** Record the variable **name + environment (never the value)** in
> your ops log and expect a restart (`docs/DEPLOYMENT_AND_ROLLBACK.md` §1.3).

---

## 7. Confirm Blueprint Auto Sync = No

In the Blueprint settings for this workspace, confirm **Auto Sync = No** (a standing owner item,
`docs/MVP_AGENDA.md` §I). With Auto Sync off, Render will not automatically apply future
`render.yaml` changes — which, combined with §8, prevents the withheld `nycdf-web` block (when it is
eventually restored) from silently auto-creating a **second**, Blueprint-managed web service that
collides with the one you created by hand here. **[confirm the exact toggle label in the dashboard
UI]**

---

## 8. `render.yaml` restoration debt + duplicate-service caution (recorded, NOT done here)

- **Restoration owed.** `render.yaml` still omits the `nycdf-web` service block (withheld at commit
  `23817a9f` pending the Next.js RCE fix). The rule is that the change which lands the authorized
  Next.js upgrade **must restore that block in the same change** (`render.yaml` note "3) Next.js
  frontend web service `nycdf-web` — WITHHELD"; `docs/MVP_AGENDA.md` §I). **This checklist does not
  restore it** — that is a separate, later, gated task. (M5-T024 is docs-only; `render.yaml` is
  read-only for this task.)
- **Duplicate-service caution.** The service you create in §1 is created **by hand** and is
  therefore **not Blueprint-managed.** When the `nycdf-web` block is later restored and the
  Blueprint is synced, Render would create a **separate** Blueprint-managed `nycdf-web` service —
  two services for one frontend. The later restoration task must reconcile this (e.g. adopt/import
  the existing service, or name/retire one deliberately) rather than let them collide. Auto Sync =
  No (§7) keeps this from happening silently in the meantime.

---

## 9. End-to-end owner verification

After §1–§7, verify on your own device (D-043-R001 required evidence: "owner confirms the live URL
works on their device").

**FIRST, understand the opt-in URL — read before step 2.** Every internal surface (both the address
front door **and** the draft rule-evaluation surface) is gated by the single `ruleEvalEnabled`
boolean, which requires the env flag on **AND** a per-request `?ruleeval=on` opt-in
(`apps/web/src/lib/rule-evaluation.ts` lines 96-103 → `apps/web/src/app/property/page.tsx` line 30 →
`apps/web/src/components/property/PropertyLookup.tsx` line 265, the only mount of
`<AddressResolutionScreen />`). **Consequence:** a plain `/property` request (no `?ruleeval=on`)
shows **only the numeric BBL lookup form — there is no address field**, even with the env flag set.
That is **expected**, not a broken deploy. To use the address flow you must open
**`<new-web-service-origin>/property?ruleeval=on`**.

1. **Load the web URL** (`<new-web-service-origin>`) — the app loads (root `/` returns 200; health
   posture from §1 step 10). Plain `/property` shows the numeric BBL lookup form; the numeric lookup
   works on its own.
2. **Resolve a real address live** — open **`<new-web-service-origin>/property?ruleeval=on`**; the
   address front door (`<AddressResolutionScreen />`) is now mounted. Enter a real NYC address; it
   resolves end-to-end against the **live** `nycdf-api` (this exercises the cross-origin call from §2
   step 2 and the CORS allowlist from §6 step 1). If the address field is absent, you are on plain
   `/property` — re-open the URL **with** `?ruleeval=on`. If the field is present but the address
   does **not** resolve while the API is up, the most likely cause is a CORS mismatch — re-check that
   `<new-web-service-origin>` in §6 exactly matches the origin from §4 (no trailing slash, correct
   scheme).
3. **Flag-on draft rule-evaluation surface renders** — on that **same** `?ruleeval=on` request, with
   `INTERNAL_RULE_EVAL_ENABLED=1` on **both** services (§2, §6), the draft rule-evaluation surface
   also renders (the same two-factor gate mounts both surfaces;
   `apps/web/src/lib/rule-evaluation.ts` lines 54-77, 96-103;
   `apps/web/src/components/property/PropertyLookup.tsx` line 265). Without `?ruleeval=on`, or with
   the env flag unset, both surfaces stay hidden and the rule-eval endpoint returns a benign `404`
   shown as "not available in this environment" — the expected default, not a failure.

**Expected-absent (do NOT treat as bugs):**

- **All Supabase-backed features** — sign-in / accounts, saved scenarios, and any persistence —
  are absent because **B-001** (Supabase token) is unresolved and the API has no auth
  (`docs/MVP_AGENDA.md` §I; `services/api/app/main.py` docstring). The `NEXT_PUBLIC_SUPABASE_*` vars
  were left blank in §2 step 3 by design.
- **The internal rule-evaluation surface on ordinary requests** — hidden unless `?ruleeval=on` is
  present (§9 step 3); this is the intended default.
- **Any public-launch affordances** — none exist and none are added here (D-043-R004).

---

## 10. Stale-flag-name dashboard check (M5-T019)

If you had **ever** set the **old** flag name `INTERNAL_RULE_EVAL_UI` in any Render dashboard
(on either service), **rename it to `INTERNAL_RULE_EVAL_ENABLED`** (or remove the old name). The old
name was retired when the web flag was unified onto the single canonical
`INTERNAL_RULE_EVAL_ENABLED` (M5-T019 / D-040-R002;
`project-control/reports/M5-T019-producer-report.md` "S4 — OWNER RETURN NOTE", lines 168-183). The
old name is **inert** — a service still carrying only `INTERNAL_RULE_EVAL_UI` behaves as if the flag
were off. For the brand-new web service in §1 there is nothing to rename (it never had the old name);
this check matters only if the old name lingers somewhere from an earlier setup.

---

## Provenance summary (every material claim's source)

| Claim | Source |
|---|---|
| Repo `nyc-buildability`; branch `candidate/D-024-mrl-option-b` not `main`; Hobby workspace; `nycdf-api` live; Auto Sync = No standing item; API has no auth | `docs/MVP_AGENDA.md` §I, §J2 |
| Root dir `apps/web`; runtime node; build `npm ci && npm run build`; start `npm run start`; region oregon; health `/`; plan tradeoff | prior `nycdf-web` block, git history `23817a9f~1:render.yaml` (recovered read-only) |
| `nycdf-api` region oregon, plan/spin-down note, CORS var declared `sync: false` | `render.yaml` (`nycdf-api` service block) |
| `nycdf-web` withheld + restoration owed | `render.yaml` note block "3)"; `docs/MVP_AGENDA.md` §I |
| Canonical flag name + true tokens + server-read (not NEXT_PUBLIC) + two-factor gate | `apps/web/src/lib/rule-evaluation.ts` lines 54-103 |
| `NEXT_PUBLIC_API_BASE_URL` build-time inlining / rebuild rule | `apps/web/.env.example` lines 6-8, 27-35; `docs/DEPLOYMENT_AND_ROLLBACK.md` §1.3 |
| Browser calls API cross-origin; default `127.0.0.1:8000` | `apps/web/src/lib/api.ts` lines 147-154; `apps/web/src/lib/address-api.ts` |
| CORS exact-origin, wildcard rejected at startup, unset = blocked | `services/api/app/main.py` lines 15-23, 66-82, 87, 103 |
| Node version 22 = CI pin; no `engines` field; exact Render mechanism unconfirmed in repo | `.github/workflows/ci.yml` `node-version: 22`; `apps/web/package.json`; `docs/research/render-nextjs-previews-2026-07-16.md` §1 |
| Not-a-public-launch; private = unlisted+flag-gated+labeling, not secret-proof; owner-only dashboard boundary | `project-control/directives/D-043-internal-web-deploy/` source-001.md + requirements.json R001-R004 |
| Stale-flag rename (INTERNAL_RULE_EVAL_UI → …_ENABLED) | `project-control/reports/M5-T019-producer-report.md` lines 168-183 |
| SSR Next.js = Web Service; Node version documented separately | `docs/research/render-nextjs-previews-2026-07-16.md` §1 |

**Items marked [confirm in the dashboard UI]** are Render UI specifics not fixed by repo evidence:
the New-Web-Service click-path labels, the exact Node-version mechanism, the `$PORT` listen
confirmation in the deploy log, and the Auto Sync toggle label. Verify each against the live Render
dashboard; do not assume wording.
