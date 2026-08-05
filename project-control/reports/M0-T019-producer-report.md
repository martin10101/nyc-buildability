# M0-T019 Producer Report — Frontend framework security upgrade + permanent dependency-security policy

- Task: M0-T019 (frontend). Producer agent: frontend-engineer.
- Authorization: governance directive D-009 (owner-activated 2026-08-04), fresh full-scope build.
- Worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/t19`; branch `task/M0-T019-frontend-security-v2`
  based on frozen main `d5d9b506c8be63eafd00ad92bd2d3dab2012d067`.
- Producer CANNOT self-approve. This is evidence for independent G3 (code-reviewer) + G5
  (security-reviewer) gates.

---

## 1. What changed (files)

| File | Change |
|---|---|
| `apps/web/package.json` | Exact pins: `next 15.5.21`, `react 19.1.2`, `react-dom 19.1.2`, `eslint-config-next 15.5.21`. ALL devDeps converted range→exact (FE-S10) at their currently-resolved versions. Added `"overrides": { "postcss": "8.5.23" }`. Added `depage` / `depage:test` scripts. |
| `apps/web/.npmrc` | NEW. `min-release-age=7`, `save-exact=true`, `package-lock=true`. Documented as resolver-time defence-in-depth, NOT the committed-lock gate. |
| `apps/web/scripts/dependency_age_gate.mjs` | NEW. Node-ESM, node-builtins-only, fail-closed committed-lockfile age gate (FE-S9) + npm CLI advisory verification (FE-S11). Injectable clock + network for deterministic tests. Bounded retries + backoff; distinct `infrastructure_unavailable` outcome. |
| `apps/web/scripts/tests/dependency_age_gate.test.mjs` | NEW. 32 deterministic offline unit tests (node built-in runner). |
| `.github/workflows/ci.yml` | `web` + `web-e2e` jobs pin `npm@11.18.0`. NEW `web-dependency-security` job (FE-S2/S3/S4/S9/S11), blocking on push+PR. |
| `.github/workflows/generate-lockfile.yml` | Pins `npm@11.18.0`; regenerates lock honouring overrides+.npmrc; VALIDATES (npm ci + audit + age gate + CLI advisory) before the bot commits. This is how the patched lock is produced without a local install. |
| `.github/workflows/scheduled-web-audit.yml` | NEW. Daily + PR-path re-audit (FE-S7): npm audit + committed-lock age gate + npm CLI advisory, all blocking/fail-closed. |
| `docs/DEPENDENCY_SECURITY_POLICY.md` | NEW. Full permanent policy (FE-S8) incl. the four-layer distinction (FE-S11) and the age-only emergency exception. |
| `CLAUDE.md` | Appended concise permanent principle #15 (D-009-authorized). |

NO change under `apps/web/src/**`. No test/TS weakening. No forbidden path touched. Next 16 /
canary / preview NOT used anywhere.

---

## 2. Re-verification against the live npm registry (as required by the packet)

Verified at implementation time (2026-08-05 UTC) via the official npm registry packument `time`
maps and the npm bulk advisory endpoint (`/-/npm/v1/security/advisories/bulk` — the exact source
`npm audit` consults).

### 2a. Directly changed / overridden packages — advisory + age

| Package | Version | npm publish timestamp (UTC) | Age at 2026-08-05 | Advisory (bulk endpoint) |
|---|---|---|---|---|
| next | 15.5.21 | 2026-07-21T15:59:32.231Z | 14.49 d | none |
| react | 19.1.2 | 2025-12-03T15:32:12.347Z | 244.5 d | none |
| react-dom | 19.1.2 | 2025-12-03T15:32:19.778Z | 244.5 d | none |
| eslint-config-next | 15.5.21 | 2026-07-21T15:59:04.475Z | 14.49 d | none |
| postcss (override) | **8.5.23** | 2026-07-24T17:05:13.876Z | 11.45 d | none |
| npm (CLI tooling) | 11.18.0 | 2026-06-29T16:42:20.148Z | ~36 d | none |

All ≥ 7 complete days old (≥ 604800 s) and advisory-free.

### 2b. DEVIATION from the packet — postcss override 8.5.10 → 8.5.23 (REQUIRED, recorded)

The packet directed `overrides.postcss == 8.5.10` but explicitly required re-verification. The
bulk advisory endpoint reports **postcss 8.5.10 is NOT advisory-free**:

- GHSA-6g55-p6wh-862q (HIGH, CVSS 7.5) — affects `<= 8.5.11`
- GHSA-r28c-9q8g-f849 (HIGH, CVSS 7.5) — affects `<= 8.5.17`
- GHSA-fxqj-rqcc-2cmp (MODERATE) — affects `<= 8.5.22`

The minimum advisory-free postcss is **8.5.23** (fixes all three). 8.5.23 is also ≥ 7 days old.
I did NOT pick 8.5.24 (2026-07-28, clears 7 d ~2026-08-04T09:41Z — too close) or 8.5.25
(2026-07-29, clears 7 d 2026-08-05T13:01Z — would FAIL the age gate as of now). **8.5.23 is the
correct, advisory-free, comfortably-aged choice.** This is an advisory-driven correction, not a
waiver — using 8.5.10 would have made `npm audit` red. Flagged for G5.

### 2c. Exact devDependency pins (FE-S10) — pinned to currently-resolved versions

Each pinned to the version already resolved at the frozen-main lockfile root; each re-verified
≥ 7 days old at 2026-08-05:

`@eslint/eslintrc 3.3.6` (25.3d), `@playwright/test 1.61.1` (42.3d), `@testing-library/dom 10.4.1`
(373.6d), `@testing-library/jest-dom 6.9.1` (307.3d), `@testing-library/react 16.3.2` (197.7d),
`@types/node 22.20.1` (27.9d), `@types/react 19.2.17` (60.3d), `@types/react-dom 19.2.3` (266.0d),
`@vitejs/plugin-react 4.7.0` (383.0d), `eslint 9.39.5` (25.3d), `jsdom 26.1.0` (478.7d),
`typescript 5.9.3` (308.3d), `vitest 3.2.7` (29.9d).

### Transitive-advisory override remediation (2026-08-05)

Blocker B-017 (`project-control/reports/M0-T019-transitive-advisory-blocker-2026-08-05.md`)
recorded that the CI-regenerated full tree failed the blocking `npm audit` on 3 HIGH advisories
from two transitive lines (`sharp` under `next`'s optionalDependency, and `brace-expansion` under
the eslint/minimatch/glob tooling). This applies that report's §4 plan at source by adding two
exact-pin overrides to `apps/web/package.json`, so the fresh lock resolves the patched versions
without pulling `next@16` (hard-prohibited):

| Override | Version | npm publish (UTC) | Age gate | Provenance (B-017 §2 / §6b) |
|---|---|---|---|---|
| `sharp` | **0.35.3** | 2026-07-01T11:28:34.077Z | ~35 d — clears 604800s comfortably | Advisory-free (Snyk lists 0.35.3 as latest non-vulnerable); released by maintainer Lovell Fuller, GPG-verified. Overrides `next@15.5.21`'s `sharp: ^0.34.3` optionalDependency, which capped below the patched 0.35.0 line (inherited libvips CVE-2026-33327/33328/35590/35591, GHSA-f88m-g3jw-g9cj). |
| `brace-expansion` | **1.1.18** | 2026-07-30T10:17:06.961Z | first advisory-free 1.x; clears 604800s at **2026-08-06T10:17:06.961Z** | Legitimate long-time maintainer @juliangruber, GPG-verified. Verified clean vs the active 2026-08-04 npm bad-publish incident (its 2026 issues are genuine DoS/ReDoS CVEs, not a cover for a bad publish; published 5 days before the incident and not on its affected list). |

**Applied at source now; lockfile + any age-threshold change DEFERRED to the owner.** The overrides
are written into `package.json` only. The lockfile is NOT regenerated here, so no under-age package
is installed by this change. `brace-expansion 1.1.18` does not clear the 7-day FE-S9 age gate until
2026-08-06T10:17:06.961Z; the regeneration via `generate-lockfile.yml` (which re-runs `npm ci` +
blocking audit + FE-S9 age gate + FE-S11) and any FE-S9 A/B age decision (B-017 §6b Option A hold-to-7-days
vs Option B 6-day verified path) are the **owner's pending decision** and are not taken in this edit.
The FE-S9 machine threshold remains 604800s with no exception/allowlist path added.

---

## 3. Local self-checks run (Node runtime only — no npm, disk-safe)

- `node --test scripts/tests/dependency_age_gate.test.mjs` → **32 passed / 0 failed** (boundary
  604800 PASS / 604799 FAIL; integrity/host/timestamp/ambiguous fail-closed branches; retry
  exhaustion → `INFRASTRUCTURE_UNAVAILABLE`; FE-S11 advisory decision + fail-closed).
- Live path smoke (real registry): registry UTC clock read from `Date` header; real
  `next@15.5.21` integrity MATCH → PASS; tampered integrity → `INTEGRITY_MISMATCH`; scoped
  `@types/node` packument fetch OK.
- Live FE-S11: `node scripts/dependency_age_gate.mjs --npm-cli-advisory 11.18.0` → PASS, exit 0.
- `parseLock` on the real committed lock: 553 unique registry packages enumerated; 0 missing
  integrity, 0 unexpected host, 0 ambiguous.
- `node --check` clean on module + tests.
- All three workflow YAMLs parse (`yaml.safe_load`).

---

## 4. Lockfile / CI approach — HOW the patched lock is produced without a local install

Thin-client constraint: the owner PC (~7 GB) CANNOT run `npm install`, so I could not regenerate
`apps/web/package-lock.json` locally, and hand-editing it is exactly the attack FE-S9 defends
against (correct integrity hashes cannot be computed offline). The committed lock on this branch
is therefore STILL the pre-patch 15.3.4 tree.

**Required CI round-trip (orchestrator-run; authoritative):**
1. Dispatch `.github/workflows/generate-lockfile.yml` on this branch. It pins `npm@11.18.0`,
   runs `npm install --package-lock-only` (honouring `overrides.postcss=8.5.23` + `.npmrc`
   min-release-age), then VALIDATES the fresh lock (npm ci integrity, blocking `npm audit`,
   committed-lock age gate, npm CLI advisory) BEFORE the bot commits it. The bot pushes the
   regenerated lock to the branch.
2. Normal push CI then runs `web`, `web-e2e`, and `web-dependency-security` on the regenerated
   lock; `scheduled-web-audit` covers the ongoing schedule.

**What awaits that CI run (cannot be produced locally):**
- The regenerated `package-lock.json` at the 15.5.21 / 19.1.2 / postcss-8.5.23 tree (FE-S1).
- The FULL-tree `npm audit` zero-findings JSON over all ~550+ transitive packages (FE-S2). Local
  evidence covers the changed/overridden packages + npm CLI via the same advisory source; the
  complete transitive audit is a CI artifact.
- The FE-S10 zero-resolution-change proof (diff of regenerated resolved versions vs. the exact
  pins; the security bump intentionally changes next/react/react-dom/eslint-config-next/postcss —
  any OTHER drift must STOP-and-report; that diff is only observable post-regeneration).
- The full-lockfile live run of `dependency_age_gate.mjs package-lock.json` over the regenerated
  tree (FE-S9 end-to-end).

---

## 5. FE-S1..FE-S11 status

| Scenario | Status | Notes |
|---|---|---|
| FE-S1 exact target + lock | **needs-CI** | package.json pinned exactly; lock regenerated + validated by generate-lockfile.yml on CI (no local install possible). No Next 16/canary/preview. postcss override = 8.5.23 (see §2b). |
| FE-S2 blocking audit (JSON total==0) | **needs-CI** (design done) | `web-dependency-security` + generate-lockfile + scheduled-web-audit run `npm audit --audit-level=low` AND JSON total==0. Changed packages verified advisory-free locally; full-tree audit is the CI artifact. |
| FE-S3 deterministic install | **needs-CI** (design done) | `npm ci --no-audit` then explicit blocking audit; integrity+lock↔manifest verified. |
| FE-S4 npm tooling + config | **done (config) / needs-CI (effective proof)** | `npm@11.18.0` pinned in all web jobs + verified (`npm -v` check); `.npmrc` min-release-age=7 + save-exact=true committed. |
| FE-S5 release-age, no exception | **done (evidence) / needs-CI (full tree)** | All changed/pinned packages ≥7 d with registry timestamps (§2). B-013 age threshold (2026-07-28) long passed; no exception path exists in FE-S9. |
| FE-S6 full regression | **needs-CI** | web/web-e2e (lint, typecheck, vitest, Next build, Playwright) run on the regenerated lock. |
| FE-S7 scheduled audit | **done** | `scheduled-web-audit.yml` (daily + PR paths + dispatch); failure path is a red blocking run. |
| FE-S8 permanent policy | **done** | `docs/DEPENDENCY_SECURITY_POLICY.md` full ruleset incl. provenance review + age-only emergency exception; CLAUDE.md pointer added. |
| FE-S9 committed-lock age gate | **done (logic+tests) / needs-CI (live full run)** | `dependency_age_gate.mjs` fail-closed, no allowlist; 604800/604799 boundary + all fail-closed branches unit-tested; live path smoke-proven. |
| FE-S10 exact direct pins | **done (pins) / needs-CI (zero-drift proof)** | Every direct dep+devDep exact = resolved version; zero-resolution-change confirmable only on CI regeneration. |
| FE-S11 npm CLI advisory verification | **done** | In-file `--npm-cli-advisory`; npm@11.18.0 advisory-free (live PASS); wired into ci + scheduled + generate-lockfile; policy §2 distinguishes the four layers. |

---

## 6. Assumptions, limitations, STOP conditions

- **Deviation (recorded, not a waiver):** postcss override 8.5.10 → 8.5.23 because 8.5.10 carries
  two HIGH + one MODERATE advisory (§2b). This is the packet-mandated re-verification outcome.
- **No STOP condition hit** that blocks the build: an advisory-free, ≥7-day compatible tree
  EXISTS at the chosen versions; no <7-day fix is required; no gate is skipped/downgraded/
  warning-only/allowlisted; no test weakening; no forbidden path; no production credential.
- **Cannot self-verify the full tree locally** (thin-client). The complete `npm audit` zero-JSON,
  the regenerated lock, and the FE-S10 zero-drift diff are produced by the CI round-trip in §4.
  If, on regeneration, ANY transitive package is <7 days old or carries an advisory, the age gate
  / npm audit will FAIL CLOSED in CI — surface to the owner; do not waive.
- The bulk advisory endpoint is the same source `npm audit` uses; a new advisory disclosed after
  this report would be caught by `web-dependency-security` / `scheduled-web-audit` (that is the
  intended post-merge behaviour, §4 of the policy).

Requested status: **awaiting_gate** (G3 + G5), with the §4 CI lockfile round-trip to be run by the
orchestrator so FE-S1/S2/S3/S6/S10 produce their CI artifacts on the regenerated lock.
