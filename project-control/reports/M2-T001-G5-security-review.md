<!--
PROVENANCE: This is the security-reviewer's G5 return for M2-T001, saved VERBATIM by the
orchestrator from the agent-return channel (transport entity-decoding only, per the
report-preservation rule in .claude/rules/project-control.md; the reviewer's one-line
preamble "All evidence gathered. Here is the complete G5 report." and a "---" separator
preceded the report and are omitted as transport framing). Reviewer agent id a9f9b328a72d52531;
review performed read-only against worktree .claude/worktrees/M2-T001 @ dd34c7b.
Saved 2026-07-16 by the orchestrator.
-->
# G5 Security and Privacy Gate Report — M2-T001

- **Task:** M2-T001 — Priority 4: first browser Property screen (real BBL lookup against accepted property-profile API v1.1)
- **Gate:** G5 (security and privacy)
- **Reviewer:** security-reviewer (independent; did not produce the work; read-only — no implementation edits, no git writes, no control-CLI use)
- **Producer:** frontend-engineer
- **Code under review:** worktree `.claude/worktrees/M2-T001`, branch `task/M2-T001-property-screen` @ `dd34c7b`, diff vs base `8b49cad` (47 files, apps/web/** + one additive ci.yml job + producer report; verified via `git diff 8b49cad --stat`)
- **Date:** 2026-07-16
- **Verdict: PASS** — zero Critical/High findings; zero acceptance-blocking findings; three tracked **blocking-before-any-deploy** conditions (C1–C3) and four Low/Info findings. Network was available this session: CI run 29548158336 conclusion re-verified live via `gh` (status `completed`, conclusion `success`, all 5 ci.yml jobs green including `web-e2e`).

## 0. Method

Read-only review of the full diff and every file it touches, grep sweeps for dangerous patterns across `apps/web/src`, `apps/web/e2e`, and configs, lockfile registry/integrity inspection, CI workflow comparison across all three workflows, and confirmation that `render.yaml`, `services/**`, and `packages/**` are byte-identical to base (`git diff 8b49cad -- render.yaml services packages` → empty). One `gh` call succeeded (no failed network calls to report). Nothing was written outside this returned report.

## 1. Checklist verification (evidence per item)

### 1.1 Secrets / bundle — PASS
- Secrets sweep (`service[_-]?role|api[_-]?key|secret|password|token|Bearer |eyJhb|sk-ant|ghp_|AKIA` over `src`, `e2e`, configs, `.env.example`): only documentation prose hits (`.env.example` boundary comments, a code comment in `format.ts:26`, CSS/comment text). No credential material anywhere under `apps/web`.
- The ONLY env var consumed by app code is `process.env.NEXT_PUBLIC_API_BASE_URL` (`src/lib/api.ts:101`), a publishable URL with a local/CI default of `http://127.0.0.1:8000`. `playwright.config.ts` reads only `process.env.CI` (test-only). No other `NEXT_PUBLIC_*` is consumed.
- `apps/web/.env.example` is names-only with the correct PRD §14.3/§17 security-boundary comment (lines 6–19) explicitly prohibiting the service-role key under apps/web with or without the prefix.
- Env files: `git ls-files | grep -i \.env` → only `.env.example` tracked. `.gitignore:56-58` (`.env`, `.env.*`, `!.env.example`) verified effective via `git check-ignore -v` on `apps/web/.env` and `apps/web/.env.local`.
- No Supabase client, no supabase-js dependency, no auth token handling exists in this slice — no service-role exposure surface. The pre-existing SHA-pinned `secret-scan.yml` workflow still covers the repo.

### 1.2 CI job security — PASS
- Workflow-level `permissions: contents: read` (ci.yml:12-13) is inherited by the new `web-e2e` job; the job adds no `permissions:` block, no `secrets.*` references (grep over ci.yml: zero), no trigger changes (`on: push / pull_request` unchanged; no `pull_request_target` anywhere).
- Actions used by `web-e2e`: `actions/checkout@v4`, `actions/setup-node@v4`, `actions/setup-python@v5` (all already used in this file) plus `actions/upload-artifact@v4` — official GitHub-owned, tag-pinned consistently with the rest of the file, but NEW to ci.yml (see F3: the inline comment overstates "only actions already used elsewhere in this file"). No third-party actions added — packet risk item satisfied in substance.
- Artifact upload: `playwright-report/` + `test-results/` only (test outputs — traces/screenshots of fixture data, no secrets in the job environment to leak), `retention-days: 7` (bounded), `if-no-files-found: ignore`.
- Lockfile supply chain: `generate-lockfile.yml` is `workflow_dispatch`-only, `contents: write` scoped to that one utility workflow (not ci.yml), runs `npm install --package-lock-only --no-audit --no-fund` on a GitHub runner and commits as github-actions[bot] to the dispatching branch (matches observed commit 89f4609). No `.npmrc` exists in the repo (`git ls-files | grep -i npmrc` → none), so the default `registry.npmjs.org` applies; CI installs use `npm ci` (strict lockfile match) with `lockfileVersion: 3` and 562 `integrity` hashes.

### 1.3 Dependency surface — PASS
- Runtime `dependencies` UNCHANGED: `package.json` diff shows additions only in `devDependencies` (`@playwright/test`, `@testing-library/{dom,jest-dom,react}`, `@vitejs/plugin-react`, `jsdom`, `vitest`) and two scripts. The production bundle gains no new runtime deps (next/react/react-dom only).
- Lockfile registry audit: `grep "resolved" package-lock.json | grep -v registry.npmjs.org` → **empty**. All packages resolve to registry.npmjs.org with integrity hashes.
- `hasInstallScript` packages: `esbuild`, `fsevents` (×2), `sharp`, `unrs-resolver` — all standard, expected transitive dependencies of vite/next tooling; nothing anomalous.

### 1.4 Injection / rendering — PASS
- `grep -rniE "dangerouslySetInnerHTML|innerHTML|document\.write|eval\(|new Function"` over `src` and `e2e` → **zero hits**. All API-provided text (no_match message `FailureState.tsx:44`, 422 message/code `:58,:60`, missing-inputs reasons, provenance `original_value`/`normalized_value` `ProvenanceDisclosure.tsx:47-49`, conflict values, coverage policy) is rendered exclusively as JSX expression children → React text nodes, auto-escaped.
- Correlation id rendered as a text node inside `<code>` (`FailureState.tsx:22`); `InternalErrorState` deliberately does NOT render the server-provided message at all — fixed generic copy only (`FailureState.tsx:120-139`), and `failures.spec.ts:62-63` asserts no `Traceback`/`RuntimeError` leakage.
- Hostile `request_url`: `urlHost()` (`format.ts:27-33`) parses with `new URL()` inside try/catch, returns `.host` only (garbage → `"unavailable"`, `javascript:` URL → empty host string) and the value is rendered as text — it is **never** used as an `href`. The only anchors in the app are the static internal `<Link href="/property">` (`page.tsx:19`). No mislead/breakout vector.

### 1.5 SSRF / egress — PASS
- Exactly one fetch site in app code (`api.ts:118`): `` `${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(bbl)}` ``. The BBL is validated client-side first (`bbl.ts`: digits-only regex, exact length 10, borough 1–5 — `PropertyLookup.tsx:139-144` blocks the network call on failure) AND `encodeURIComponent`-encoded, so no path traversal or query smuggling even on the deliberate server-422 bypass test path (which still only sends a 10-digit numeric string, e.g. `1000000000`).
- No other egress: `grep "fetch("` in `src` non-test → only api.ts; e2e specs contain no non-localhost URLs (`grep https?:// e2e | grep -v 127.0.0.1|localhost` → empty). No telemetry: `NEXT_TELEMETRY_DISABLED: "1"` set in BOTH `web` (ci.yml:27) and `web-e2e` (ci.yml:56) jobs. (Deploy-time guidance noted in F4.)

### 1.6 Harness containment — PASS
- `apps/web/e2e/harness/fixture_api.py` lives outside `services/**` and imports the **installed** `app` package (`fixture_api.py:56-63`); `git diff 8b49cad -- services` is empty — production API source untouched. The CORSMiddleware and `dependency_overrides` mutations are applied to the in-process app instance only when the harness script itself is executed (Playwright `webServer` command); no production code imports the harness, and it is not part of the installed package or `render.yaml` (untouched).
- CORS scope: `allow_origins` limited to `http://127.0.0.1:3000` / `http://localhost:3000`, `GET` only, `Accept` header only, exposing only `X-Correlation-ID` (`fixture_api.py:158-164`). Binds `127.0.0.1` explicitly (`:170`). No real network egress: transport is fully scripted (`ScriptedTransport`) over committed official fixtures; even backoff sleeps are stubbed (`:149`).
- Production API has **no** CORS configuration (`grep -rn CORS services/api/app` → empty) — confirming the harness middleware cannot exist in a deployed path and sharpening D8 (see C1).

### 1.7 Honesty / exposure conditions — PASS (with tracked conditions C1–C3)
- No deploy configuration added: `render.yaml` diff vs base empty. INTERNAL/DEV banner + PRD §29 disclaimer verified by G3 with visual evidence; no auth claimed anywhere.
- G3 D8 confirmed and sharpened as tracked condition C1 below.

### 1.8 Logging / PII — PASS
- `grep "console\." apps/web/src` → **zero hits** (no payload logging anywhere in production paths).
- `grep -rniE "localStorage|sessionStorage|document\.cookie|indexedDB"` over `src` and `e2e` → **zero hits**; no analyst-entered data persisted client-side (re-verifies G3 §4).
- Failure states show correlation id only; raw exception internals never rendered (1.4 above).

### 1.9 Low-storage / hygiene — PASS
- Nothing heavy written locally by the feature; all installs/builds/browser runs in CI. `.gitignore` covers `node_modules/`, `.next/`, `playwright-report/` (:47), `test-results/` (:48), `__pycache__/` (:6 — verified matching `apps/web/e2e/harness/__pycache__` via `git check-ignore -v`); `eslint.config.mjs` also ignores the two Playwright output dirs. CI artifact retention bounded at 7 days.
- Cross-tenant isolation / RLS: **not applicable in this slice** — no auth, no tenancy, no Supabase, no storage buckets, no uploads, no AI calls are introduced. Prompt-injection surface: none added (no AI in this slice); hostile official-source text is neutralized by React text-node rendering (1.4).

## 2. Findings

**Critical: none. High: none.**

### (a) Blocking for acceptance
**None.**

### (b) Blocking before any deploy (tracked conditions — must be resolved in the future deploy task; B-001/B-002 already prevent deploy today)
- **C1 (Medium, sharpens G3 D8) — CORS/proxy decision.** The production API (`services/api/app`) has no CORS policy (grep-verified empty) and the screen's design is a cross-origin browser fetch (`NEXT_PUBLIC_API_BASE_URL` ≠ page origin). Before ANY real deployment, a reviewed decision is required: either (i) same-origin routing (Next.js rewrite/proxy so the browser never crosses origins) or (ii) an explicit, environment-scoped CORS allowlist added to `services/api` under its own task/gate (services/** was correctly out of scope here). The harness middleware must never be the template copied blindly — it allowlists localhost only.
- **C2 (Medium) — No authentication or rate limiting in front of the screen or the API.** Acceptable ONLY because the slice is INTERNAL/DEV and undeployed (render.yaml untouched, B-001 open). PRD §17 requires auth + rate-limited public endpoints; any deploy task must gate on Supabase Auth integration and API rate limiting before exposure.
- **C3 (Low) — No HTTP security headers configured.** `next.config.ts` is bare (`reactStrictMode` only): no CSP, `frame-ancestors`/`X-Frame-Options`, or `X-Content-Type-Options`. Irrelevant while undeployed; the deploy task should add a reviewed header set. Also set `NEXT_TELEMETRY_DISABLED=1` and an **https** `NEXT_PUBLIC_API_BASE_URL` in the Render service env (the `http://127.0.0.1:8000` default is local/CI-only and safe as a fallback, but production must not rely on it).

### (c) Carry-forwards / informational
- **F1 (Low, pre-existing debt) — Actions are tag-pinned (`@v4`/`@v5`), not SHA-pinned**, in ci.yml and generate-lockfile.yml; `secret-scan.yml` already demonstrates the SHA-pin standard (checkout@11bd719…). Already tracked as the hygiene batch (packet risk item); the new job correctly did not worsen the posture. Carry-forward.
- **F2 (Low) — `generate-lockfile.yml` holds `permissions: contents: write`.** Mitigated: `workflow_dispatch`-only (maintainer-triggered), single-purpose (`--package-lock-only` against registry.npmjs.org, no scripts executed), commits only `apps/web/package-lock.json`. Acceptable; consider deleting or SHA-pinning it in the hygiene batch since its one-shot purpose (M0-T004) is fulfilled.
- **F3 (Info) — Inaccurate ci.yml comment** (line 51: "Uses only actions already used elsewhere in this file"): `actions/upload-artifact@v4` is new to ci.yml. It is official, GitHub-owned, and consistent with existing pinning style — substance complies with the packet ("no unpinned third-party actions"); only the comment overstates. Fix opportunistically; no rework required.
- **F4 (Info) — Bookkeeping:** G2/G3 evidence says "all 6 jobs green"; live `gh run view 29548158336` shows 5 ci.yml jobs (web, web-e2e, api, contracts, control-plane), all `success` — the sixth was presumably the separate secret-scan workflow run. Evidence is green either way; note for orchestrator records only.

## 3. Verdict

**PASS.** The diff introduces no secret material, no injection or SSRF surface, no client-side persistence, no logging of payloads, no runtime dependencies, no deploy exposure, and no weakening of existing CI security posture; the e2e harness is properly contained test infrastructure over committed official fixtures with localhost-only CORS. Cross-tenant/RLS/service-role/upload/prompt-injection controls are structurally not-applicable to this slice and no shortcut was taken that forecloses them. Conditions C1–C3 are **blocking before any deployment task**, not for acceptance of M2-T001; the orchestrator should record them against the future deploy/auth work (alongside B-001/B-002) so they cannot be lost.

*Evidence basis:* `.claude/worktrees/M2-T001` @ dd34c7b full diff vs 8b49cad; `apps/web/src/lib/{api,bbl,format,provenance,missing-inputs,coverage,property-profile}.ts`; `apps/web/src/components/property/*.tsx` (notably `FailureState.tsx`, `ProvenanceDisclosure.tsx`, `PropertyLookup.tsx`); `apps/web/e2e/**` incl. `harness/fixture_api.py`, `helpers.ts`, `playwright.config.ts`; `.github/workflows/{ci,generate-lockfile,secret-scan}.yml`; `apps/web/{package.json,package-lock.json,next.config.ts,eslint.config.mjs,.env.example}`; `.gitignore` + `git check-ignore`; `project-control/tasks/M2-T001.json`; `project-control/reports/M2-T001-G3-review.md`; live `gh run view 29548158336`.
