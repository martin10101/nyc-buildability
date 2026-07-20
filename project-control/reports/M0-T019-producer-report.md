# M0-T019 producer report — Frontend framework security upgrade and permanent npm dependency-admission policy

**Task ID:** M0-T019
**Producer agent:** frontend-engineer
**Status requested:** `awaiting_gate`
**Worktree / branch:** `.claude/worktrees/M0-T019-frontend` / `task/M0-T019-frontend-security`
**Date:** 2026-07-20

This is an AOS section-6 producer packet. No git/npm/gh/project_control commands
were run by the producer (thin-client + ADR-005): the orchestrator regenerates
the lockfile on a CI runner and records all ledger transitions. Nothing under
`apps/web/src/**`, `services/api/**`, tests, or TypeScript settings was changed,
and no `min-release-age-exclude` (or any other exclusion) was added.

---

## 1. Files changed (one-line purpose each)

| File | Change | Purpose |
| --- | --- | --- |
| `apps/web/package.json` | modified | Exact pins `next` 15.5.20, `react` 19.1.2, `react-dom` 19.1.2 (deps), `eslint-config-next` 15.5.20 (dev); new `"overrides": { "postcss": "8.5.10" }`. Other devDeps unchanged. |
| `apps/web/.npmrc` | created | `save-exact=true`, `min-release-age=7` (+ comment: needs npm >= 11.10.0, CI pins 11.18.0). No exclusions. |
| `.github/workflows/ci.yml` | modified | `web` + `web-e2e`: pin npm 11.18.0 after setup-node (version-checked). `web`: BLOCKING audit after `npm ci` (`--audit-level=low` + JSON total==0). Python jobs untouched. |
| `.github/workflows/generate-lockfile.yml` | modified | Pin npm 11.18.0 before lock regeneration so the lock honors `.npmrc` + the postcss override. Stays workflow_dispatch, `--package-lock-only --no-audit --no-fund`, commit-back. |
| `.github/workflows/scheduled-npm-audit.yml` | created | Daily cron (06:41) + PR on web dep artifacts + workflow_dispatch; checkout + setup-node 22 + npm pin + `npm ci --no-audit --no-fund` + the SAME blocking audit. `permissions: contents: read`. |
| `docs/DEPENDENCY_SECURITY_POLICY.md` | created | Permanent cross-ecosystem (npm + Python) policy + owner-only auto-expiring emergency exception. |
| `CLAUDE.md` | appended | New permanent principle 15 pointing at the policy (append-only; existing content unchanged). |
| `project-control/reports/M0-T019-producer-report.md` | created | This report. |

`apps/web/package-lock.json` is intentionally **NOT** edited here — it is
regenerated remotely by the orchestrator (see Section 8).

---

## 2. Verified-facts table (orchestrator-captured 2026-07-20 21:59:44 UTC; used verbatim, not re-verified by producer)

Source: registry.npmjs.org + api.osv.dev + official npm v11 docs.

| package | exact target | published (UTC) | age at verification | advisory (OSV, installed version) | registry |
| --- | --- | --- | --- | --- | --- |
| next | 15.5.20 | 2026-07-01T21:07 | 19.04 days (1,645,000+ s) | NONE | registry.npmjs.org |
| react | 19.1.2 | 2025-12-03T15:32 | 229.27 days | NONE | registry.npmjs.org |
| react-dom | 19.1.2 | 2025-12-03T15:32 | 229.27 days | NONE | registry.npmjs.org |
| eslint-config-next | 15.5.20 | 2026-07-01T21:06 | 19.04 days | NONE | registry.npmjs.org |
| postcss (override) | 8.5.10 | 2026-04-15T14:42 | 96.30 days | NONE | registry.npmjs.org |
| npm (CI tooling) | 11.18.0 | 2026-06-29T16:42 | 21.22 days | NONE | registry.npmjs.org |

All six targets exceed 7 complete days (604800 s); **no emergency age exception
is needed.** `next` latest is 16.2.10 — we intentionally stay on 15.x (Next 16 is
FORBIDDEN). react/react-dom latest is 19.2.7 — we use the reviewed 19.1.2 patch.
npm `min-release-age` was introduced in npm 11.10.0, which is why npm 11.18.0 is
the pinned CI tooling version.

---

## 3. Final `apps/web/package.json`

```json
{
  "name": "@nyc-buildability/web",
  "version": "0.1.0",
  "private": true,
  "description": "Next.js 15 App Router placeholder for the NYC Development Feasibility & Zoning Intelligence Platform",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "next": "15.5.20",
    "react": "19.1.2",
    "react-dom": "19.1.2"
  },
  "devDependencies": {
    "@eslint/eslintrc": "^3.3.1",
    "@playwright/test": "^1.53.0",
    "@testing-library/dom": "^10.4.0",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.3.0",
    "@types/node": "^22.15.0",
    "@types/react": "^19.1.0",
    "@types/react-dom": "^19.1.0",
    "@vitejs/plugin-react": "^4.5.0",
    "eslint": "^9.28.0",
    "eslint-config-next": "15.5.20",
    "jsdom": "^26.1.0",
    "typescript": "^5.8.3",
    "vitest": "^3.2.0"
  },
  "overrides": {
    "postcss": "8.5.10"
  }
}
```

## 4. Final `apps/web/.npmrc`

```
# Dependency-admission enforcement (docs/DEPENDENCY_SECURITY_POLICY.md). min-release-age requires npm >= 11.10.0; CI pins npm 11.18.0 so the lockfile is regenerated honoring these keys.
save-exact=true
min-release-age=7
```

`.npmrc` keys used: `save-exact=true` (Boolean), `min-release-age=7` (Number,
days). No `min-release-age-exclude` entry — no exclusion of any kind was added.

---

## 5. Workflow change diff summary (verbatim key lines)

### `.github/workflows/ci.yml`

**`web` job** — after `setup-node`, added the npm pin; after `npm ci`, added the blocking audit:

```yaml
      - name: Pin npm 11.18.0
        run: |
          npm install -g npm@11.18.0
          test "$(npm --version)" = "11.18.0" || { echo "npm pin failed: $(npm --version) != 11.18.0"; exit 1; }
```
```yaml
      - name: Install dependencies
        run: npm ci --no-audit --no-fund
      - name: Dependency audit — zero advisories incl. dev deps (blocking)
        run: |
          npm audit --audit-level=low
          npm audit --json > "$RUNNER_TEMP/npm-audit.json"
          node -e "const t=require(process.env.RUNNER_TEMP+'/npm-audit.json').metadata.vulnerabilities.total; if(t!==0){console.error('npm audit total vulnerabilities='+t+' (must be 0)');process.exit(1)} console.log('npm audit total vulnerabilities=0')"
```

**`web-e2e` job** — after `setup-node` (before `setup-python`), added the SAME npm pin step. No audit added here (the audit lives in the `web` job and the scheduled workflow); `web-e2e` continues to run vitest + Playwright unchanged. `npm ci --no-audit --no-fund` is unchanged in this job.

`cache-dependency-path: apps/web/package-lock.json` is unchanged in both jobs. **All Python jobs (`api`, `api-lock-verify`, `api-tooling-lock-verify`, `exact-production-install`, `contracts`, `contracts-typegen`, `contracts-schema-bundle`, `control-plane`) are untouched.**

### `.github/workflows/generate-lockfile.yml`

Added the npm pin between `setup-node` and the lock-generation step:

```yaml
      - name: Pin npm 11.18.0
        run: |
          npm install -g npm@11.18.0
          test "$(npm --version)" = "11.18.0" || { echo "npm pin failed: $(npm --version) != 11.18.0"; exit 1; }
      - name: Generate package-lock.json (no node_modules)
        working-directory: apps/web
        run: npm install --package-lock-only --no-audit --no-fund
```

`workflow_dispatch` trigger, `permissions: contents: write`, and the commit-back step are unchanged.

### `.github/workflows/scheduled-npm-audit.yml` (new)

Triggers, permissions, and the audit body:

```yaml
on:
  schedule:
    - cron: "41 6 * * *"
  pull_request:
    paths:
      - "apps/web/package.json"
      - "apps/web/package-lock.json"
      - "apps/web/.npmrc"
      - ".github/workflows/scheduled-npm-audit.yml"
  workflow_dispatch:

permissions:
  contents: read
```
```yaml
      - name: Pin npm 11.18.0
        run: |
          npm install -g npm@11.18.0
          test "$(npm --version)" = "11.18.0" || { echo "npm pin failed: $(npm --version) != 11.18.0"; exit 1; }
      - name: Install dependencies (deterministic; audit is the separate gate)
        run: npm ci --no-audit --no-fund
      - name: Dependency audit — zero advisories incl. dev deps (blocking)
        run: |
          npm audit --audit-level=low
          npm audit --json > "$RUNNER_TEMP/npm-audit.json"
          node -e "const t=require(process.env.RUNNER_TEMP+'/npm-audit.json').metadata.vulnerabilities.total; if(t!==0){console.error('npm audit total vulnerabilities='+t+' (must be 0)');process.exit(1)} console.log('npm audit total vulnerabilities=0')"
```

The daily cron is offset to 06:41 UTC, distinct from the Python `scheduled-audit.yml` cron (06:17 UTC), so the two do not collide at the top of the hour. `working-directory: apps/web` is the job default; the npm pin step runs a global install so it is directory-independent.

---

## 6. Acceptance scenarios FE-S1..FE-S8

| Scenario | How it is satisfied |
| --- | --- |
| **FE-S1** exact target | `package.json` carries `next` 15.5.20, `react`/`react-dom` 19.1.2, `eslint-config-next` 15.5.20 as exact strings, plus `overrides.postcss` 8.5.10; `.npmrc save-exact=true`. No Next 16 / canary anywhere. The regenerated lockfile (CI runner) will carry these exact versions and the postcss override; the orchestrator confirms them in the lock delta. |
| **FE-S2** audit zero (BLOCKING) | `web` job runs `npm audit --audit-level=low` **and** the JSON `metadata.vulnerabilities.total == 0` check; the step exits non-zero on any finding. `npm ci` is `--no-audit` (deterministic) and the explicit blocking audit follows it. Dev deps are in scope (default npm audit behavior). CI-verified on the runner after the lock is regenerated. |
| **FE-S3** deterministic install | Every web install is `npm ci` (fails on package.json/lock mismatch; verifies integrity hashes). The only `--no-audit` usages are immediately followed by the explicit blocking audit (`web` job and scheduled workflow). CI-verified. |
| **FE-S4** npm tooling + config | npm 11.18.0 is installed and version-checked in `web`, `web-e2e`, `generate-lockfile`, and `scheduled-npm-audit` (the step fails if `npm --version` != 11.18.0). `.npmrc` sets `min-release-age=7` + `save-exact=true`; effective because the lock is regenerated under npm 11.18.0. |
| **FE-S5** release-age | All six changed/overridden/tooling targets are >= 7 days old (Section 2 table: 19.04–229.27 days; npm 21.22 days). `min-release-age=7` enforces this fail-closed for the whole transitive tree at lock-regeneration time. Per-package publication dates + registry source recorded above. |
| **FE-S6** full regression | Runs on the CI runner after lock regeneration: `web` (npm ci → blocking audit → lint → typecheck → build) and `web-e2e` (npm ci → vitest → build → Playwright journeys). No test or TS setting was weakened; no `apps/web/src/**` change. Secret scan / existing jobs remain. CI-verified by the orchestrator/reviewers. |
| **FE-S7** scheduled audit | `scheduled-npm-audit.yml` re-audits the committed tree daily + on PRs touching the web dep artifacts + on demand; a finding turns the run red (JSON total==0 gate), matching the Python `scheduled-audit.yml` visibility pattern. |
| **FE-S8** permanent policy | `docs/DEPENDENCY_SECURITY_POLICY.md` states the full rule set (advisory-free across runtime/dev/build/lock/audit tooling + transitives; 7-day age; exact pins + lockfile integrity; blocking audits on every change + schedule; no agent waiver/allowlist/ignore/warning-only; post-merge advisory reopens security work + blocks deploy; new-package provenance review of name/typo-squat, maintainers/ownership changes, install/lifecycle scripts, registry origin, publication age; prefer existing deps/stdlib) AND the emergency exception (age-only, never an advisory, owner-authorized, records package+version+reason+approver+timestamp+expiry, auto-expires at 7 days, no wildcard/org-wide/permanent/undocumented). `CLAUDE.md` principle 15 is the concise pointer. |

---

## 7. Assumptions / defaults

- **Blocking-audit placement:** put the blocking audit in the existing `web` job (right after `npm ci`) rather than a new dedicated job — the contract explicitly allows either; the `web` job already installs the web tree, so this avoids a redundant install. The scheduled workflow provides the independent, schedule-driven copy.
- **`web-e2e` gets the npm pin but not a second audit:** the audit is intentionally single-sourced (the `web` job + the scheduled workflow) to avoid a redundant ~identical audit; `web-e2e` still needs the pin so its `npm ci` resolves under `.npmrc`.
- **Cron offset 06:41 UTC** chosen to avoid colliding with the Python audit's 06:17 UTC and the top-of-hour scheduler surge; any non-colliding offset minute is acceptable.
- **JSON total check uses `metadata.vulnerabilities.total`** — the documented aggregate across all severities in `npm audit --json` (npm v11), so it catches `info`-level findings that `--audit-level=low` alone would let pass. Written to `$RUNNER_TEMP` (not the workspace) to avoid polluting the tree the lint/build steps see.
- The other `apps/web` devDependencies were left exactly as-is (ranged), per the contract; `save-exact` only affects future `npm install <pkg>` additions, and the committed lockfile already freezes the full transitive tree.

## 8. What the orchestrator must do remotely

1. **Regenerate `apps/web/package-lock.json`** on a CI runner (dispatch `generate-lockfile.yml`, now pinned to npm 11.18.0) so the lock reflects `next` 15.5.20 / `react` 19.1.2 / `react-dom` 19.1.2 / `eslint-config-next` 15.5.20 and the `postcss` 8.5.10 override, with `min-release-age=7` honored across the transitive tree.
2. **After the lock lands, complete the transitive lockfile-delta inventory** (which transitive versions changed vs. the prior lock) and confirm on the CI runner: `npm ci` reproduces the committed lock; the blocking audit prints `npm audit total vulnerabilities=0`; lint/typecheck/build and the vitest + Playwright journeys pass. These are the CI-verified halves of FE-S2/FE-S3/FE-S6 that cannot run on the thin-client PC.
3. Record all ledger transitions (progress/submit) and integrate git per ADR-005.

The transitive lockfile delta, `npm ci` reproducibility proof, and the audit-zero JSON are produced by the CI runner after step 1 — they are not available to the producer, who cannot run npm locally.

## 9. Known limitations

- The producer could not execute `npm ci`, `npm audit`, `npm run build`, or the Playwright suite locally (thin-client + ADR-005); FE-S2/FE-S3/FE-S6/FE-S7 correctness is asserted by construction and must be confirmed by the CI runner. This is expected and by design.
- `min-release-age` enforcement is effective only when the lock is regenerated (or install resolves) under npm >= 11.10.0; the pinned npm 11.18.0 in `generate-lockfile.yml` guarantees this for regeneration. If a lock were ever regenerated with an older npm (not possible through the committed workflows), the age gate would silently not apply — the pin + version-check step is the guard.
- npm's audit database and OSV can disclose a new advisory against an already-pinned version at any time; the scheduled workflow (FE-S7) is exactly the mechanism that surfaces that, per policy Section 5.

## 10. Security / provenance notes

- All six targets are advisory-free against the installed version and >= 7 days old (Section 2, orchestrator-captured from registry.npmjs.org + api.osv.dev). No emergency exception invoked.
- The audit is genuinely blocking: two independent failure paths (`--audit-level=low` non-zero exit; JSON `total != 0` process.exit(1)). No `--ignore`, no allowlist, no warning-only step, no `npm audit fix --force`, anywhere.
- The npm pin steps download `npm@11.18.0` from the npm registry on GitHub-hosted runners only (never the owner PC). No secrets are referenced by any changed workflow; `scheduled-npm-audit.yml` runs with `permissions: contents: read` (least privilege). `generate-lockfile.yml` keeps `contents: write` solely for its existing commit-back, unchanged.
- No `apps/web/src/**`, `services/api/**`, test, or TypeScript-setting change; no `min-release-age-exclude` or any exclusion added; Next 16 and canaries excluded.

## 11. Recommended reviewer focus (G3 code-reviewer + G5 security-reviewer)

1. **Lockfile delta (post-regeneration):** confirm the regenerated `package-lock.json` carries exactly the five target versions + postcss 8.5.10 override and no Next 16 / canary; review the transitive delta the orchestrator inventories.
2. **Audit enforcement is truly blocking:** verify both the `--audit-level=low` and the JSON `total==0` paths fail the job, in both the `web` job and `scheduled-npm-audit.yml`; confirm no allowlist/ignore/warning-only crept in.
3. **Age policy:** confirm `.npmrc min-release-age=7` with no exclusion, and that npm 11.18.0 is pinned + version-checked everywhere a lock is generated or installed.
4. **Workflow npm-download paths:** confirm the npm pin runs only on GitHub-hosted runners, references no secrets, and does not touch the owner PC; `scheduled-npm-audit.yml` least-privilege `contents: read`.
5. **Policy doc:** confirm `docs/DEPENDENCY_SECURITY_POLICY.md` is internally consistent with the implemented enforcement and covers the full FE-S8 rule set + the narrow owner-only auto-expiring exception; `CLAUDE.md` principle 15 is an accurate pointer.
6. **Forbidden-path compliance:** confirm no change to `apps/web/src/**`, `services/api/**`, tests, or TS settings, and that `package-lock.json` was NOT hand-edited by the producer.
