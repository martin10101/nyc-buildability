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

### 2a. OPTIONAL — default-on mode for the internal surfaces (D-057, added 2026-09-14)

This step is **optional** and independent of steps 1-3 above; skip it to keep the opt-in-only
behavior (plain `/property` shows only the numeric BBL form, as described in step 1 and §9).

- **Var name:** `INTERNAL_RULE_EVAL_DEFAULT_ON` = `1` — set on the **WEB service only** (do **not**
  set this on `nycdf-api`; it has no effect there).
- **What it does:** with it set to a true token, a plain `/property` request — **no**
  `?ruleeval=on` query param — shows the **full internal flow** (the address front door **and** the
  draft rule-evaluation surface) directly, as long as `INTERNAL_RULE_EVAL_ENABLED` (step 1) is also
  on. Same **true tokens** and same fail-safe rule as step 1 (`1`, `true`, `yes`, `on`,
  case-insensitive, trimmed; absent / empty / unrecognized = **off**, i.e. today's opt-in-only
  behavior, unchanged). Source: `apps/web/src/lib/rule-evaluation.ts`
  (`INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR`, `ruleEvaluationSurfaceEnabled`).
- **Exposure consequence — read this before setting it.** With this var set, **anyone holding the
  web URL sees the full internal flow immediately**, with no query param to type — one fewer privacy
  layer than the opt-in-only default. This is the same exposure posture already disclosed and
  owner-accepted in §5 (unlisted + flag-gated, **not** secret-proof); D-057 records the owner's
  explicit order to make the plain URL work without `?ruleeval=on`
  (`project-control/directives/D-057-ruleeval-default-on/source-001.md`).
- **`?ruleeval=off` remains the kill switch.** Even with this var set, a request that explicitly adds
  `?ruleeval=off` (or any other non-true `ruleeval` value) still forces the surface off for that
  request — the fail-safe kill switch is never weakened by this var.
- **Server-read — no rebuild needed.** Unlike `NEXT_PUBLIC_API_BASE_URL` (step 2, which is
  build-inlined), this var is read per request. Saving it in the dashboard and letting Render
  restart the service (the normal env-var-change restart) is sufficient.

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

## 6a. Two more `nycdf-api` internal flags — live spatial substrate + scenario endpoint (D-059-R004, M5-T033)

These two flags on **`nycdf-api`** were **not** named in earlier revisions of this checklist and are the
subject of the D-059-R004 spatial-failure protocol. Their **code-level fail-safe default is disabled**:
when the variable is **absent** the server behaves as OFF (`services/api/app/spatial/live_provider.py`,
`services/api/app/config.py`). The actual value on any deployed service is **environment-scoped and
owner-visible only** — this checklist never asserts what a deployed service currently carries; §6b is how
you read it. Both follow the **same true-token rule** as `INTERNAL_RULE_EVAL_ENABLED` — accepted true
tokens are `1`, `true`, `yes`, `on` (case-insensitive, trimmed); **absent / empty / any other value =
disabled (fail-safe).** Set them on **`nycdf-api` → Environment**, save, and let Render restart the
service (an env-var change is a deploy).

1. **`LIVE_SPATIAL_PROVIDER_ENABLED`** — gates the **live spatial-substrate composition** behind the
   rule-evaluation endpoint's default provider
   (`services/api/app/spatial/live_provider.py`, `LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR`).
   - **Fail-safe default (absent = disabled):** with it absent the server-side spatial provider returns
     **no substrate** and makes **zero connector calls**, so `GET /api/v1/properties/{bbl}/rule-evaluation`
     fail-safes to `spatial_intersection_absent` / `professional_review_required` for **every** BBL — a
     valid 200 "professional review required" document with **no district**, never a live zoning answer.
   - **This is ONE candidate cause of the recorded live failure — not a confirmed one.** The 2026-09-17
     capture (`project-control/reports/M5-T033-live-capture.md`) saw uniform `spatial_intersection_absent`
     across both D-059 parcels **and** a known-good control, each in ~0.6–0.7 s. A disabled flag produces
     exactly that shape — **but so does a shared connector/network failure** (all three parcels hitting the
     same failing upstream, which can also fail uniformly and fast). Uniformity and latency are therefore
     **suggestive, not decisive**; the flag reading in §6b is what confirms it. To get live spatial
     answers you **must** set this flag to a true token.
   - **Independent of `INTERNAL_RULE_EVAL_ENABLED`.** The rule-eval route must **also** be enabled
     (§6 step 2) for any of this to be reachable at all; this flag only decides whether the *reachable*
     route composes a real substrate or fail-safes to absent. Turning it on makes the API perform live
     ArcGIS/SODA connector calls per request.
   - **Where:** `nycdf-api` → Environment. **Post-restart probe:** see **§6b**.

2. **`INTERNAL_SCENARIO_ENABLED`** — gates the internal **scenario** endpoint
   `GET /api/v1/properties/{bbl}/scenario` (`services/api/app/api/v1/scenario.py`
   `@router.get("/properties/{bbl}/scenario", include_in_schema=False)` → guard
   `internal_scenario_enabled()`; name in `services/api/app/config.py`,
   `INTERNAL_SCENARIO_ENABLED_ENV_VAR`). Absent = the scenario route returns a generic **`404`
   `{"detail":"Not Found"}`** byte-indistinguishable from an unmounted path (fail-safe) and absent from
   the OpenAPI document — the **same** posture as the rule-eval flag, with a **distinct** name so the two
   internal surfaces are enabled independently (the scenario route is gated by **this** flag only, not by
   `INTERNAL_RULE_EVAL_ENABLED`). Set it to a true token to expose the scenario endpoint. **Where:**
   `nycdf-api` → Environment. **Post-restart probe:** see **§6b** (exact method/path and the web opt-in).

## 6b. OWNER DASHBOARD CHECK — read the live spatial provider flag (the remaining root-cause confirmation, D-059-R004)

The deployed environment is **owner-visible only**, so this reading is the step that turns the recorded
`spatial_intersection_absent` from a *candidate* cause into a *confirmed* one. **The recorded live cause
stays UNCONFIRMED** until the deployed setting is read **for the same deployment the capture ran against**:
the 2026-09-17 capture (`project-control/reports/M5-T033-live-capture.md`) was taken against backend commit
`f0e7d82f`; if `nycdf-api` has been redeployed since, re-capture before concluding. On **`nycdf-api` →
Environment**, read whether **`LIVE_SPATIAL_PROVIDER_ENABLED`** is present and set to a true token.

**What is decisive vs. what is only suggestive.** Two runtime facts are decisive discriminators; two
response-body observations are not:

- **Decisive (read at the runtime boundary):** (1) the **dashboard flag reading** itself (present + true
  token vs. absent/other), and (2) the API's **correlated typed connector log** — the
  `live_spatial_substrate fail_safe event=connector_error error_type=… correlation_id=…` line
  (`services/api/app/spatial/live_provider.py::_fail_safe`), emitted **only** when the flag is on and a
  connector actually failed. Match its `correlation_id` to the response's `X-Correlation-ID`.
- **Suggestive only (read from the response body):** **uniform** `spatial_intersection_absent` across
  parcels and **fast** (~0.6–0.7 s) latency. A disabled flag produces both — **but so does a shared
  connector/network failure** (every parcel hitting the same failing upstream fails uniformly, and can fail
  fast, e.g. a DNS/connection error or an open circuit breaker). Uniformity and latency **narrow** the
  field; they do not prove the flag was off.
- **Absence of a connector-error log does NOT by itself prove flag-off.** The line can be missing in
  several distinct situations — the flag really was off (no live path ran), OR the log was
  filtered / level-gated / not captured, OR the live path failed at a stage that logs a *different* event
  (`no_candidate_districts` / `district_page_partial`), OR a failure occurred outside this module. Read the
  flag value; do not infer it from a missing log.

| Reading on `nycdf-api` | Meaning | Expected live behavior |
|---|---|---|
| `LIVE_SPATIAL_PROVIDER_ENABLED` **absent, empty, or any non-true value** (`0`, `false`, `off`, `maybe`, …) | Live spatial path **DISABLED** (fail-safe default). One code-contract-consistent candidate for the uniform failure captured 2026-09-17 — **not ranked above** a shared connector/network failure, which produces the same uniform-and-fast shape; the discriminators above (the flag reading and the correlated typed logs), not this response signature, decide between them | **Every** BBL (including the control `1008350041`) returns `spatial_intersection_absent` / `professional_review_required` fast, with no district and **no `connector_error` log line**. **Fix:** set it to `1`, save, let Render restart, then run the probes below. |
| `LIVE_SPATIAL_PROVIDER_ENABLED` = **`1` / `true` / `yes` / `on`** | Live spatial path **ENABLED** | A **successful connector request is not by itself a real district**: the live path still returns `spatial_intersection_absent` when the data returned is not valid/sufficient (empty official assignment, transfer-limited page) or the engine cannot confidently compose a single-district substrate. A real district appears only when the connectors succeed **and** return sufficient data **and** the engine composes a confident substrate; a parcel whose connectors fail returns `spatial_intersection_absent` **and** emits a typed `connector_error` log line (its `correlation_id` matching the response `X-Correlation-ID`). If **all** parcels — including the control — are still uniformly absent while this reads true, the **disabled-flag branch is excluded for the observed runtime**; the remaining cause is **not established from absence alone** — do **not** infer a connector/network failure from the uniform absence. Confirm it only from **correlated typed evidence** (a matching `connector_error` line, or another typed event), and do not re-deploy blindly. |

- **Enabling the flag and still seeing failure does NOT disprove an earlier disabled flag.** If you set
  the flag true, restart, and the control still returns absent, the **disabled-flag branch is excluded for
  the observed runtime** — but that continued absence does **not** by itself establish any particular
  remaining cause. It does **not** prove a second, separate connector problem: a connector/network failure
  is only one possibility; insufficient or invalid official data (empty assignment) and a substrate the
  engine cannot confidently compose produce the same absent body on the enabled path. The remaining
  enabled-path cause is established **only from correlated typed evidence** (a matching `connector_error`
  line, or another typed event such as `no_candidate_districts` / `district_page_partial`), never inferred
  from the uniform absence. Separately — and preserved unchanged — the dashboard reading tells you the
  flag's current state; it does not retroactively rule the flag in or out as the historical cause. Confirm
  the historical cause only by pairing the captured deployment (commit `f0e7d82f`) with its own env reading.

**Post-restart verification probes (after setting `LIVE_SPATIAL_PROVIDER_ENABLED` true).** All are direct
API requests against `<nycdf-api-origin>`; each internal route is gated by its own env flag and is
`include_in_schema=False` (never in the OpenAPI doc):

1. **Rule-evaluation (control parcel):**
   `GET <nycdf-api-origin>/api/v1/properties/1008350041/rule-evaluation`
   (`services/api/app/api/v1/rule_evaluation.py`
   `@router.get("/properties/{bbl}/rule-evaluation", include_in_schema=False)`, gated by
   `INTERNAL_RULE_EVAL_ENABLED`). **Before:** `fail_safe_reason` = `spatial_intersection_absent`, no
   district. **After (flag true + connectors succeed and return sufficient data):** the control
   resolves to a real district (`fail_safe_reason` ≠ `spatial_intersection_absent`). Still absent after
   the restart ⇒ the disabled-flag branch is excluded for this runtime; the remaining cause requires
   correlated typed evidence (read the typed connector logs) — do not infer a connector problem from the
   absent body alone.
2. **Scenario endpoint:**
   `GET <nycdf-api-origin>/api/v1/properties/{bbl}/scenario`
   (`services/api/app/api/v1/scenario.py`
   `@router.get("/properties/{bbl}/scenario", include_in_schema=False)`, gated by
   `INTERNAL_SCENARIO_ENABLED` via `internal_scenario_enabled()`). **Required opt-in:** set
   `INTERNAL_SCENARIO_ENABLED` to a true token on `nycdf-api` first — otherwise the route returns the
   generic `404 {"detail":"Not Found"}`. With the flag on, the request returns a **200 `scenario` @ 1.0.0
   document** (a no-scenario / professional-review outcome is still a normal 200, not an error; its spatial
   substrate comes from the same provider, so it shares the `spatial_intersection_absent` fail-safe when the
   spatial flag is off). **Web opt-in:** if probing through `nycdf-web` rather than the API directly, the
   internal web surfaces additionally require the per-request `?ruleeval=on` query param plus the web env
   flag (§9).

The dashboard flag reading remains the authoritative confirmation; completing M4-T020 / B4 (the
wide-street work) does **not** by itself fix this — the live provider has its own flag and failure
conditions and does not use the street-centerline module (D-059-R004).

---

## 6c. `nycdf-api` internal flag — live wide-street determination (M5-T035, DB-015)

This flag is **separate** from `LIVE_SPATIAL_PROVIDER_ENABLED` (§6a) and gates the **live
wide-street-determination composition** behind the rule-evaluation endpoint's default wide-street
provider. Its **code-level fail-safe default is disabled**: when the variable is **absent** the
server-side wide-street provider returns **no determination** and makes **zero connector calls**
(`services/api/app/spatial/wide_street_live_provider.py`,
`live_wide_street_provider_enabled` / `default_live_wide_street_determination`). Set it on
**`nycdf-api` → Environment**, save, and let Render restart the service (an env-var change is a deploy).

1. **`LIVE_WIDE_STREET_PROVIDER_ENABLED`** — gates the live wide-street path.
   - **Same true-token rule** as `INTERNAL_RULE_EVAL_ENABLED`: accepted true tokens are `1`, `true`,
     `yes`, `on` (case-insensitive, trimmed); **absent / empty / any other value = disabled
     (fail-safe)** (`wide_street_live_provider.py`, `_TRUE_TOKENS`).
   - **Fail-safe default (absent = disabled):** with it absent the wide-street provider returns
     `None` with **zero** connector calls, so `GET /api/v1/properties/{bbl}/rule-evaluation` behaves
     **byte-identically to before this flag existed** — the conservative conditional-FAR row governs
     and **no wide-street FAR bonus is granted** for any BBL. This is an honest fail-safe, not a live
     answer.
   - **Flag reading + typed logs decide, never the response shape alone.** Exactly like the spatial
     provider (§6b): a response that shows no wide-street bonus is produced by BOTH the flag being off
     **and** any live failure/insufficiency (connector error, transfer-limited page, zero DCM segments
     in the queried envelope, an unattested legal precondition), because the wide-street stack **never
     fabricates** a within-100ft answer and fails safe to the conservative row or professional review.
     The response body therefore cannot distinguish flag-off from a live failure. What **does**: the
     dashboard flag reading, and the provider's payload-only typed log line
     (`live_wide_street fail_safe event=… error_type=… correlation_id=…`,
     `wide_street_live_provider.py::_fail_safe`) — matched to the response `X-Correlation-ID`. Read the
     flag value; do not infer it from the response body.
   - **Independent of `INTERNAL_RULE_EVAL_ENABLED` and of `LIVE_SPATIAL_PROVIDER_ENABLED`.** The
     rule-eval route must **also** be enabled (§6 step 2) for any of this to be reachable; this flag
     only decides whether the *reachable* route composes a live wide-street determination or returns
     `None`. Turning it on makes the API perform live DCM/MapPLUTO ArcGIS connector calls per request.
   - **Honest scope (DRAFT / D-045-R009).** Even enabled, the wide-street rows stay
     `needs_review` DRAFT pending G6 qualified-human approval; a live within-100ft determination is
     never a Verified result. The current accepted stack does not implement the ZR 12-10 named-street
     override table, so a lot with a wide-disposed segment resolves to **professional review**, not a
     guessed higher FAR (honest fail-safe). **Where:** `nycdf-api` → Environment.

## 6d. `nycdf-api` runtime pin — `PYTHON_VERSION` (DB-004; geometry determinism)

Set **`PYTHON_VERSION` = `3.12.11`** on **`nycdf-api` → Environment** (a specific patch on the **3.12**
line CI builds and tests against). This is **load-bearing** for the wide-street geometry engine:

- **Why pin the interpreter.** The B4 buffer engine asserts an exact shapely / GEOS build at import
  (`services/api/app/connectors/wide_street_buffer_engine.py`, `PINNED_SHAPELY_VERSION` = `2.0.7`,
  `PINNED_GEOS_VERSION_STRING` = `3.11.4`; the assertions at module import fail closed on any drift).
  On the pinned 3.12 line, `pip` installs the prebuilt shapely 2.0.7 manylinux **wheel** (which bundles
  GEOS 3.11.4), so the pin holds and geometry output stays reproducible.
- **What goes wrong unpinned (DB-004 / run-38, recorded — not re-verified in this task).** Render
  drifted to a newer Python (3.14) for which **no matching shapely 2.0.7 wheel exists**, forcing a
  source build against a **different** system GEOS; the engine's import-time GEOS pin then refuses
  (fail-closed), and the wide-street path cannot load. Pinning `PYTHON_VERSION` to the CI-tested 3.12
  line keeps Render on the interpreter the wheel targets.
- **Evidence.** CI pins `python-version: "3.12"` in `.github/workflows/ci.yml`; `services/api/pyproject.toml`
  declares `requires-python = ">=3.12"`; `render.yaml` compiles requirements with `--python-version 3.12`.
  The exact patch `3.12.11` is a concrete, current 3.12 patch chosen so Render does not silently float
  onto a newer minor. **[confirm the exact `PYTHON_VERSION` mechanism/label in the dashboard UI]** — the
  env-var route keeps it visible next to the other `nycdf-api` env vars.

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
**`<new-web-service-origin>/property?ruleeval=on`** — **unless** you opted into §2a's optional
`INTERNAL_RULE_EVAL_DEFAULT_ON` var, in which case the plain URL already shows the full flow.

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
| §2a: optional `INTERNAL_RULE_EVAL_DEFAULT_ON` var, same true-token rule, server-read, kill switch survives, exposure consequence | `apps/web/src/lib/rule-evaluation.ts` (`INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR`, `ruleEvaluationSurfaceEnabled`); `project-control/directives/D-057-ruleeval-default-on/source-001.md` (owner-accepted exposure tradeoff) |
| §6a/§6b: `LIVE_SPATIAL_PROVIDER_ENABLED` name + true tokens + fail-safe (unset → None, zero connector calls → uniform `spatial_intersection_absent`); flag independent of the rule-eval flag | `services/api/app/spatial/live_provider.py` (`LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR`, `_TRUE_TOKENS`, `default_live_substrate`); `services/api/app/rules/integration.py` (`FAILSAFE_SPATIAL_ABSENT`) |
| §6a: `INTERNAL_SCENARIO_ENABLED` name + true tokens + fail-safe 404 + GET `/properties/{bbl}/scenario` path, gated by this flag only (not the rule-eval flag) | `services/api/app/api/v1/scenario.py` (`@router.get("/properties/{bbl}/scenario", include_in_schema=False)`, `internal_scenario_enabled()` guard); `services/api/app/config.py` (`INTERNAL_SCENARIO_ENABLED_ENV_VAR`, `internal_scenario_enabled`, `_TRUE_TOKENS`) |
| §6b: recorded uniform live failure across both D-059 parcels + control in ~0.6–0.7 s is a CANDIDATE cause, UNCONFIRMED until the deployed flag is read for the captured deployment (commit `f0e7d82f`); uniformity + latency are suggestive, the flag reading + typed connector logs are decisive; response body cannot distinguish flag-off from connector failure; M4-T020/B4 alone does not fix it | `project-control/reports/M5-T033-live-capture.md`; `services/api/app/spatial/live_provider.py::_fail_safe`; `project-control/directives/D-059-mvp-review-dependable-answers/requirements.json` (D-059-R004) |

**Items marked [confirm in the dashboard UI]** are Render UI specifics not fixed by repo evidence:
the New-Web-Service click-path labels, the exact Node-version mechanism, the `$PORT` listen
confirmation in the deploy log, and the Auto Sync toggle label. Verify each against the live Render
dashboard; do not assume wording.
