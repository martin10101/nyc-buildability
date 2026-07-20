# G5 Security & Privacy Gate Report — M0-T019

**Task:** M0-T019 — Frontend framework security upgrade + permanent npm dependency-admission policy
**PR:** #64, head SHA `3bbb59462bc84815a7550a30698e59fd32ff36ef` (branch `task/M0-T019-frontend-security`)
**Reviewer:** security-reviewer (independent; did NOT implement)
**Gate:** G5 (dependency vulnerabilities, supply-chain integrity, least privilege, secrets, log redaction)
**Date:** 2026-07-20
**Method:** Read-only. Every material claim independently reproduced against `registry.npmjs.org`, `api.osv.dev`, git object hashes (main vs head), and live CI logs. Producer report used only as a checklist, not as evidence.

## Summary verdict: **PASS**

No advisory waiver, no age-gate bypass, no secret exposure, and no weakening of the M0-T020 Python supply-chain controls. All 12 CI checks are green on the head SHA. The blocking npm audit is genuinely fail-closed and verified running on the real regenerated lockfile. The lockfile introduces zero new packages, removes three, and every changed direct/override package's committed integrity hash matches the live registry (no tampering/typosquat). Two non-blocking observations are recorded below for later disposition; neither is a defect and neither blocks acceptance.

---

## Findings by focus area

### 1. Audit is a real, blocking gate — no waiver — CONFIRMED
- **ci.yml `web` job** (lines 55-59) runs, after `npm ci --no-audit --no-fund`: `npm audit --audit-level=low` (non-zero exit on any advisory >= low) **AND** a node one-liner reading `require($RUNNER_TEMP/npm-audit.json).metadata.vulnerabilities.total` with `if(t!==0){...process.exit(1)}`.
- **`metadata.vulnerabilities.total` is the correct field**: in npm's `auditReportVersion: 2` schema (npm v7-v11) this is the aggregate across `info+low+moderate+high+critical`, so it catches `info`-level findings that `--audit-level=low` alone would let pass.
- **Fail-closed under schema drift**: if `metadata.vulnerabilities` were `undefined`, `.total` throws a TypeError -> node exits non-zero -> job fails. If `total` were `undefined`, `undefined !== 0` is `true` -> `process.exit(1)`. The gate cannot silently pass on a non-zero or missing total.
- **scheduled-npm-audit.yml** (lines 68-72) contains the byte-identical blocking audit; `pull_request` on the web dep artifacts (`package.json`, `package-lock.json`, `.npmrc`, the workflow itself) + daily cron `41 6 * * *` + `workflow_dispatch`.
- **No waiver primitives anywhere**: `git grep` over all changed files for `min-release-age-exclude|allowlist|--ignore|ignore-vuln|continue-on-error|audit fix|--force|--omit` returned only three hits, all comments asserting NONE are used. Dev deps are in scope (default `npm audit` behavior).
- **Runtime proof** (ci run 29783447747, web job): `found 0 vulnerabilities` and `npm audit total vulnerabilities=0` — both layers executed and passed on the actual 456-package tree from the regenerated lock.

### 2. Release-age is fail-closed — CONFIRMED
- `apps/web/.npmrc` contains exactly `save-exact=true` and `min-release-age=7`. **No `min-release-age-exclude` or any exclusion** (`grep -i exclude` on `.npmrc` is empty).
- `min-release-age` governs resolution only under npm >= 11.10.0, so **npm 11.18.0 is pinned + version-checked** (`test "$(npm --version)" = "11.18.0" || exit 1`) in every lock-touching job: `web`, `web-e2e` (ci.yml), `generate-lockfile.yml`, `scheduled-npm-audit.yml`.
- **Independent age verification** (registry `.time[ver]`, threshold 604800 s):

  | package | version | published (UTC) | age (days) | >=7d |
  |---|---|---|---|---|
  | next | 15.5.20 | 2026-07-01T21:07:16Z | 19.05 | yes |
  | react | 19.1.2 | 2025-12-03T15:32:12Z | 229.29 | yes |
  | react-dom | 19.1.2 | 2025-12-03T15:32:19Z | 229.29 | yes |
  | eslint-config-next | 15.5.20 | 2026-07-01T21:06:50Z | 19.05 | yes |
  | postcss (override) | 8.5.10 | 2026-04-15T14:42:53Z | 96.32 | yes |
  | npm (CI tooling) | 11.18.0 | 2026-06-29T16:42:20Z | 21.24 | yes |

  All >= 7 complete days; producer's table matches to the minute.

### 3. Provenance / integrity — CONFIRMED
- Independent lockfile analysis (lockfileVersion 3, 559 resolved entries):
  - **Newly-added package names: NONE** — no new maintainer, lifecycle-script, or typosquat surface entered the tree.
  - **Removed names: exactly `@swc/counter`, `busboy`, `streamsearch`** (3 removed = surface reduction; dropped by next 15.5.20).
  - **All 559 `resolved` URLs are on `https://registry.npmjs.org/`** — no mirror, no unexpected host.
  - **Every resolved entry carries a `sha512-` integrity hash** — none missing.
- **Anti-forgery cross-check (strongest evidence)**: for all 5 changed direct/override packages, the committed lockfile `integrity` equals the **live registry** `versions[ver].dist.integrity` — `next`, `react`, `react-dom`, `eslint-config-next`, `postcss` all `committed_integrity_matches_registry=True`. The lock was not hand-forged against a malicious tarball.
- **OSV** (`api.osv.dev/v1/query`, npm ecosystem, exact versions): all 5 return **no advisories**. Note: the old lock's `postcss 8.4.31` carries the ReDoS advisory GHSA-7fh5-64p2-3v2j; the override to 8.5.10 clears it.
- Lockfile delta = 15 changed / 0 added / 3 removed, exactly as stated.

### 4. Emergency-exception safety (policy doc) — CONFIRMED
`docs/DEPENDENCY_SECURITY_POLICY.md` "Emergency exception" section is unambiguous: it "may relax ONLY the 7-day release-age requirement (Section 2). It may **never** relax an advisory (Section 1): a version carrying a known advisory affecting the installed version is never admitted, emergency or not." It is owner-authorized only, fully recorded (name+version, reason, approver, UTC timestamp, expiry), auto-expires at 7 days, and explicitly prohibits wildcard/org-wide/permanent/undocumented exceptions and any blanket `min-release-age-exclude`/standing allowlist. The closing line reaffirms "An emergency exception changes nothing about audits." **It cannot be read as permitting an advisory waiver.** Consistent with CLAUDE.md principle 15.

### 5. Least privilege / secrets / logs — CONFIRMED
- **Permissions**: `ci.yml` = `contents: read`; `scheduled-npm-audit.yml` = `contents: read`; `generate-lockfile.yml` = `contents: write`. The single elevated permission is on `generate-lockfile.yml`, justified solely by its git commit-back of the lockfile, and that workflow is `workflow_dispatch`-only (not push/PR-triggered). Runtime log for the scheduled audit confirms `GITHUB_TOKEN Permissions: Contents: read, Metadata: read`.
- **No secrets referenced**: `git grep` for `secrets.*|_TOKEN|password|api_key|env:` across the 3 workflows found only the `NEXT_TELEMETRY_DISABLED: "1"` env blocks. No `NPM_TOKEN`, no registry auth.
- **No credential logging**: the npm pin steps `npm install -g npm@11.18.0` download from the public registry on GitHub-hosted runners only; audit output is `found 0 vulnerabilities` / `total vulnerabilities=0` — no token or credential echoed.
- **`.npmrc` has no embedded credentials**: no `_authToken`, `_auth`, `//host:...@` userinfo, or credentialed `registry=` line — only the two policy keys.
- **secret-scan CI check passed** on the head SHA.

### 6. Preservation of M0-T020 Python supply-chain controls — CONFIRMED
- The PR touches exactly **9 files**; `git diff --name-only origin/main..head` shows **nothing under `services/api/**` or `apps/web/src/**`**.
- **Byte-identical (git-object-hash) between main and head**: `services/api/requirements.txt`, `services/api/requirements-tools.lock`, `services/api/scripts/dependency_age_gate.py`, `.github/workflows/scheduled-audit.yml` (Python), `render.yaml`, `services/api/pyproject.toml`. No weakening of the hash-pinning, dual pip-audit, fail-closed age gate, or lock byte-identity checks.
- The ci.yml diff adds only the npm pin steps (`web` + `web-e2e`) and the blocking npm audit (`web`); all 8 Python/contracts/control-plane jobs have **zero diff lines**. Python CI jobs remain green (`api`, `api-lock-verify`, `api-tooling-lock-verify`, `exact-production-install`, `contracts`, `contracts-typegen`, `contracts-schema-bundle`, `control-plane` all pass).

### 7. Cross-tenant / RLS / upload / SSRF — N/A (stated explicitly)
This task changes only frontend dependency pins, npm config, CI workflows, and policy documentation. There is no request-handling code, no tenant-scoped data path, no storage access, no file upload, and no outbound-URL construction in the changed set. RLS/cross-tenant isolation, private-storage, upload controls, SSRF/injection defenses, and prompt-injection defenses are **not in scope** for M0-T019 and were not exercised. (The npm pin does fetch `npm@11.18.0` and the age gate/audit reach the registry, but only over the fixed public `registry.npmjs.org` host on CI runners — no user- or lock-derived host is constructed here.)

---

## Security defects
**None.** (No critical / high / medium / low defects.)

## Non-blocking observations (for later disposition, not required for this gate)
- **O-1 (informational, defense-in-depth):** The blocking npm audit depends on `npm audit` reaching the npm advisory registry at run time. A registry outage during CI would make `npm audit` error (fail-closed -> red run, which is the safe direction), but it is a network dependency. The scheduled workflow already re-audits daily, so a transient miss is self-healing. No action needed; noted for operational awareness.
- **O-2 (informational):** `min-release-age` is enforced only at lock **regeneration/resolution** time under the pinned npm >= 11.10.0; a lockfile regenerated with an older npm would silently skip the age gate. This path is closed by the version-checked 11.18.0 pin in `generate-lockfile.yml` (the only committed regeneration path). The producer disclosed this in report section 9. No action needed.

## Explicit confirmations
- **No advisory waiver**: no `--ignore`, `ignore-vuln`, allowlist, `audit fix --force`, `--omit`, warning-only downgrade, or `min-release-age-exclude` anywhere; policy forbids advisory waiver even under emergency exception. Confirmed by grep + policy read.
- **No age-gate bypass**: `min-release-age=7` present, no exclusion; npm 11.18.0 pinned + version-checked in all four lock-touching jobs; all 6 versions independently verified >= 7 days.
- **No secret exposure**: no secret references, no embedded credentials in `.npmrc`, no token logging; secret-scan CI green.
- **No weakening of M0-T020**: all Python supply-chain files byte-identical (git-object hashes); Python CI jobs unchanged and green.

## Commands run (exact)
```
gh pr view 64 --json number,title,headRefName,headRefOid,baseRefName,state,mergeable,mergeStateStatus
gh pr checks 64
gh pr diff 64 --name-only
git fetch origin main
git diff origin/main..3bbb594 -- .github/workflows/ci.yml
git diff origin/main 3bbb594 --name-only -- .github/
git diff --name-only origin/main 3bbb594
git diff --stat origin/main 3bbb594 -- .github/workflows/scheduled-audit.yml
git diff origin/main 3bbb594 -- apps/web/package-lock.json | grep -E '^[+-]\s*"(version|resolved)"'
git diff origin/main 3bbb594 -- CLAUDE.md
git grep -niE "min-release-age-exclude|allowlist|--ignore|ignore-vuln|continue-on-error|audit fix|--force|--omit" 3bbb594 -- <changed files>
git grep -niE "secrets\.|GITHUB_TOKEN|_TOKEN|password|api[_-]?key|env:" 3bbb594 -- <3 workflows>
git show 3bbb594:apps/web/.npmrc ; git show 3bbb594:apps/web/package.json ; git show 3bbb594:.github/workflows/{ci,scheduled-npm-audit,generate-lockfile}.yml
git rev-parse origin/main:<pyfile>  vs  3bbb594:<pyfile>   # byte-identity of 6 Python files
# Python (urllib/json) against registry.npmjs.org: .time[ver] age + dist.integrity + dist-tags for next/react/react-dom/eslint-config-next/postcss/npm
# Python (urllib/json) POST api.osv.dev/v1/query {ecosystem:npm,name,version} for the 5 packages
# Python lockfile analysis: distinct names head vs main, added/removed, resolved-host + sha512 audit over 559 entries, committed-integrity vs live-registry for 5 changed packages
gh run view 29783447747 --log   # web job: found 0 vulnerabilities + total vulnerabilities=0
gh run view 29783447760 --log   # scheduled npm audit job: GITHUB_TOKEN Contents: read
gh run view 29783447780 --log   # secret scan
```

**Recommendation to orchestrator:** Record G5 = **PASS** for M0-T019. No blocking corrections. Observations O-1 and O-2 are informational and require no rework.
