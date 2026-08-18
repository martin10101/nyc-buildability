# M0-T071 — Dependency-security evidence: nanoid 3.3.17 → 3.3.18 (D-015, closes B-019)

Regression/evidence record required by D-015-R017. Producer: orchestrator. Branch
`task/M0-T071-nanoid-ghsa-2v37`, worktree `wt-m0t071`, base = origin/main
`5c71fe0e08c8717cc20ac232d8bd0d8a328525e1`. Local toolchain: node v22.18.0,
npm 11.4.2 (CI pins npm 11.18.0 and re-runs every check below).

## BEFORE (committed state on origin/main — the failure being repaired)

- `apps/web/package-lock.json` `node_modules/nanoid`:
  `"version": "3.3.17", "resolved": ".../nanoid-3.3.17.tgz",
  "integrity": "sha512-xQLf0A3HOMlgHq0n247/LRuAOYmB7dXJ/DvAxGvsSBij45XtBSmQycu+F8ODbHwns/XyFZagyL1+J0Offw1E0g=="`
- `apps/web/package.json` `overrides.nanoid = "3.3.17"` (the M0-T019 FE-S10 exact-pin).
- Blocking advisory: GHSA-2v37-7h3g-55p8 (**high** — "custom generators can loop
  indefinitely when size is zero"), `nanoid <3.3.18`, dependency path
  `postcss (^3.3.16) → nanoid` (sole dependent; single lock instance).
- Observed failure: CI `web-dependency-security` job red on every branch
  (e.g. run 32108527309 job 95622881295 and the PR #222 re-run job 95628542178):
  `npm audit --audit-level=low` → "1 high severity vulnerability". Recorded as
  blocker **B-019** (on the M0-T070 branch).

## AFTER (this branch)

- `apps/web/package-lock.json` `node_modules/nanoid`:
  `"version": "3.3.18", "resolved": ".../nanoid-3.3.18.tgz",
  "integrity": "sha512-DTg4MJbGMWkfi6VZFdNt2/caMbQy4Ou+Op/hJQvGEWcnVfoA1QA+xzRKAzw9jD6+GVOOeYr/mIcuDSdug6F6+w=="`
  — integrity independently fetched from `registry.npmjs.org/nanoid` versions
  metadata BEFORE the edit and byte-identical to it; `npm ci` then
  cryptographically verified the tarball against this hash on install.
- `apps/web/package.json` `overrides.nanoid = "3.3.18"`.

## Why the override line is part of the minimum change (fail-closed proof)

A lock-only bump was attempted first. `npm ci` refused it: `EUSAGE … Missing:
nanoid@3.3.17 from lock file` — because the repo's own exact-pin policy
(M0-T019) pins the transitive in `package.json` `overrides`. The override IS the
policy's exact-pin mechanism; it is **not** a direct application dependency
(`dependencies`/`devDependencies` contain no nanoid — D-015-R012 honored). The
task contract was corrected pre-submit to include exactly that one line.

## Full diff (every file changed vs origin/main)

| file | change |
|---|---|
| `apps/web/package-lock.json` | 3 lines: the single `node_modules/nanoid` entry (version / resolved / integrity) |
| `apps/web/package.json` | 1 line: `overrides.nanoid` `3.3.17` → `3.3.18` |
| `project-control/…` | D-015 capture (28 reqs), M0-T071 packet + G0 + state, this report set (control plane only) |

**No unrelated package version changed** — the lock diff is exactly the 3 nanoid
lines. Note on mechanical churn (D-015-R015): the initial
`npm update nanoid --package-lock-only` under local npm 11.4.2 also stripped 79
lines of `"libc"` metadata written by CI's npm 11.18.0; that churn was fully
reverted by restoring the pristine lock bytes from HEAD via a plain file write
(no git reset/clean/restore invoked) and re-applying the bump as a surgical
3-line edit asserted to match exactly one occurrence.

## Publication age (no waiver)

- Registry `time["3.3.18"]` = **2026-08-07T16:41:05.696Z** (matches the owner's
  verified release date of August 7, 2026).
- Authoritative repository mechanism `scripts/dependency_age_gate.mjs
  package-lock.json` on the updated lock:
  `PASS nanoid@3.3.18 uploaded=2026-08-07T16:41:05.696Z age=917698s (10.62d)` —
  **917,698 s > 604,800 s**.
- **NO waiver was requested, authorized, or used.** No waiver record exists.

## Advisory results (every severity)

- `npm audit --audit-level=low` (dev deps included): **found 0 vulnerabilities**.
- `npm audit --json` `metadata.vulnerabilities`:
  `{"info":0,"low":0,"moderate":0,"high":0,"critical":0,"total":0}`.
- All four GHSA advisories affecting nanoid were checked against 3.3.18 in the
  GitHub advisory database — GHSA-2v37-7h3g-55p8 (<3.3.18 — patched BY this version),
  GHSA-28wg-ghj8-5hjv (<3.3.16), GHSA-mwcw-c2x4-8c55 (<3.3.8),
  GHSA-qrpm-p2h7-hrv2 (≥3.0.0 <3.1.31) — **3.3.18 affected by none**.
- npm CLI advisory verification: `dependency_age_gate.mjs --npm-cli-advisory
  11.18.0` → `PASS — no advisory affects npm@11.18.0`.

## Policy run + web battery (local, this worktree)

| check | result |
|---|---|
| deterministic install `npm ci --no-audit --no-fund` | 560 packages, integrity-verified, clean |
| `npm audit --audit-level=low` | 0 vulnerabilities |
| audit JSON total | 0 at every severity |
| committed-lock release-age gate | PASS (every package ≥ 7 days, integrity-verified) |
| npm CLI advisory (pinned 11.18.0) | PASS |
| age-gate deterministic unit tests (`node --test scripts/tests`) | 40/40 pass |
| `npm run lint` (eslint) | clean |
| `npm run typecheck` (tsc --noEmit) | clean |
| `npm run test` (vitest) | **287 passed** |
| `npm run build` (next build) | success |
| `npm run test:e2e` (Playwright) | **not executable in this sandbox**: the harness webServer (`e2e/harness/fixture_api.py`) requires the installed `app` package from `services/api`, which needs Python 3.12 (this sandbox is 3.11 — the established M2-T015 constraint). E2E evidence is the PR's pinned CI `web-e2e` job (vitest + Playwright vs the recorded-official-fixture API), reported with the final check results. |
| installed resolution check | `require('nanoid/package.json').version` → **3.3.18** |

`node_modules` was created only inside `wt-m0t071` for this policy run and is
removed after evidence capture (thin-client policy); it is untracked and fully
reproducible via `npm ci`.
