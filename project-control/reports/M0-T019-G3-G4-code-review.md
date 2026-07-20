# M0-T019 — G3 (Independent Walkthrough) + G4 (Integration/Regression) Code Review

**Task:** Frontend framework security upgrade + permanent npm dependency-admission policy
**PR:** #64 · head SHA `3bbb59462bc84815a7550a30698e59fd32ff36ef` · branch `task/M0-T019-frontend-security`
**Reviewer:** code-reviewer (independent; did NOT implement; read-only)
**Worktree reviewed:** `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T019-frontend` (HEAD confirmed = 3bbb594)
**Date:** 2026-07-20

## Summary verdict: **PASS**

All eight acceptance scenarios (FE-S1..FE-S8) are satisfied with reproducible evidence. The exact reviewed versions are pinned in both `package.json` and the regenerated lockfile; the lockfile delta is exactly the upgrade (0 added / 3 removed / 15 changed) with no unrelated rewrite; the audit gate is genuinely blocking and fails closed (independently re-simulated across clean/finding/info-only/malformed shapes); the npm 11.18.0 pin is version-checked in all four workflows; the age policy is enforced fail-closed; the policy doc is self-consistent with the implemented enforcement; and forbidden-path + no-behavior-change compliance is clean. All 12 CI checks are green at the head SHA. I independently re-verified publication ages and OSV advisory status against registry.npmjs.org and api.osv.dev — every claim in the orchestrator-captured evidence holds.

No BLOCKING corrections. Three non-blocking observations for later disposition are listed at the end.

---

## Independent re-verification of source evidence (registry + OSV, re-run 2026-07-20)

| package@version | published (UTC) | age | >=7d | OSV advisories (installed version) |
| --- | --- | --- | --- | --- |
| next@15.5.20 | 2026-07-01T21:07:16Z | 19.05 d | yes | CLEAN |
| react@19.1.2 | 2025-12-03T15:32:12Z | 229.29 d | yes | CLEAN |
| react-dom@19.1.2 | 2025-12-03T15:32:19Z | 229.29 d | yes | CLEAN |
| eslint-config-next@15.5.20 | 2026-07-01T21:06:50Z | 19.05 d | yes | CLEAN |
| postcss@8.5.10 (override) | 2026-04-15T14:42:53Z | 96.32 d | yes | CLEAN |
| npm@11.18.0 (tooling) | 2026-06-29T16:42:20Z | 21.24 d | yes | CLEAN |
| next@15.3.4 (prior) | — | — | — | **23 advisories** incl. CVE-2025-66478 |

The upgrade is a genuine security patch: the prior `next@15.3.4` carries 23 OSV advisories (the lockfile's `deprecated` field flags CVE-2025-66478 specifically). The 5 named targets + tooling npm are all advisory-free and comfortably >=7 days. Evidence exactly matches the orchestrator-captured table in the producer report section 2.

---

## Per-acceptance-scenario findings

### FE-S1 — Exact target (package.json + lockfile) — **PASS**
- `apps/web/package.json` (worktree lines 16-18, 31, 36-38): `next` "15.5.20", `react` "19.1.2", `react-dom` "19.1.2", `eslint-config-next` "15.5.20" — all exact strings, no `^`/`~`; `"overrides": { "postcss": "8.5.10" }` present exactly.
- Lockfile root `packages[""].dependencies` = `{next:15.5.20, react:19.1.2, react-dom:19.1.2}`; `node_modules/next` = 15.5.20, `node_modules/react`/`react-dom` = 19.1.2, `node_modules/eslint-config-next` = 15.5.20, `node_modules/postcss` = 8.5.10. Integrity hashes present and match the registry tarball names.
- No Next 16 / canary anywhere: `grep -nE '"(next|react|react-dom|eslint-config-next)":\s*"?(16\.|.*canary|.*-rc)'` returns only (a) `@testing-library/react` 16.3.2 (unrelated dev dep) and (b) Next's `peerDependencies` range strings `19.0.0-rc-de68d2f4-...` (declared ranges, not resolved installs). `15.3.4` occurrences in lock = 0.

### FE-S2 — Audit zero, BLOCKING, dev deps included — **PASS**
- `ci.yml` `web` job (lines 55-59) and `scheduled-npm-audit.yml` (lines 67-72) run two independent blocking layers: `npm audit --audit-level=low` (non-zero exit on any advisory >= low) **and** a node parse that `process.exit(1)` unless `metadata.vulnerabilities.total === 0`.
- Not warning-only: no `|| true`, no `continue-on-error`, no `--ignore`/allowlist anywhere.
- Dev deps in scope: `npm audit` default includes dev deps; `npm ci` installs them (no `--omit=dev`).
- **JSON-check robustness re-simulated offline** (I replicated the exact node one-liner): clean->exit0; one-low->exit1; **info-only->exit1** (strictly stricter than `--audit-level=low`, which would miss info); high/multiple->exit1; **missing `metadata`->TypeError->non-zero exit (fails closed)**; `total:null`->exit1. The gate correctly fails the build on any finding and on a malformed/broken audit.
- Live proof: the `npm audit (web tree, blocking on any finding)` check is **green** on PR #64, confirming the regenerated tree audits to total=0.

### FE-S3 — Deterministic install — **PASS**
- Every web install path is `npm ci --no-audit --no-fund` (`ci.yml` web line 46, web-e2e line 107; `scheduled-npm-audit.yml` line 65). `npm ci` fails on package.json/lock mismatch and verifies integrity hashes.
- The only `--no-audit` usages are immediately followed by the explicit blocking audit (web job + scheduled workflow). `web-e2e` uses `--no-audit` but the audit is single-sourced in the `web` job + scheduled workflow (disclosed assumption; acceptable — the same lock is audited).

### FE-S4 — npm tooling + config — **PASS**
- npm 11.18.0 pinned AND version-checked (`test "$(npm --version)" = "11.18.0" || exit 1`) in all four places: `ci.yml` web (39-42), `ci.yml` web-e2e (87-90), `generate-lockfile.yml` (added before lock gen), `scheduled-npm-audit.yml`. The check genuinely fails the job if the pin didn't take.
- `apps/web/.npmrc`: `save-exact=true` + `min-release-age=7`, no `min-release-age-exclude`. Effective because the lock is regenerated under the pinned npm 11.18.0 (min-release-age introduced npm 11.10.0 — correct per official npm v11 docs).

### FE-S5 — Release-age (delta + per-package dates) — **PASS**
- **Independently computed lockfile delta** (git show main vs head, node-by-node): **0 ADDED / 3 REMOVED / 15 CHANGED.**
  - 15 changed: `next`, `@next/env`, `@next/eslint-plugin-next`, 8x `@next/swc-*`, `eslint-config-next` -> 15.5.20; `react`, `react-dom` -> 19.1.2; `postcss` -> 8.5.10.
  - 3 removed: `@swc/counter`, `busboy`, `streamsearch` — dependencies of next@15.3.4 that next@15.5.20 no longer declares (confirmed in the `node_modules/next` dependency-block diff). Correct pruning.
  - 0 added: no unrelated dependency introduced.
- All 15 changed nodes have `resolved` pointing to registry.npmjs.org and non-empty `integrity`. Spot-checked ages >=7 days and OSV-clean (table above).
- Per-package publication dates + registry URLs recorded in producer report section 2.

### FE-S6 — Full regression — **PASS (CI-authoritative)**
- `gh pr checks 64`: **all 12 checks pass** at head 3bbb594, including `web (lint + typecheck + build)`, `web-e2e (vitest + Playwright)`, `npm audit (web tree)`, and every Python job (`api`, `api-lock-verify`, `api-tooling-lock-verify`, `exact-production-install`, `contracts`, `contracts-typegen`, `contracts-schema-bundle`, `control-plane`) and the secret scan.
- No test or TS-setting weakened; no `apps/web/src/**` change (empty diff — see compliance section). Per thin-client policy I did not re-run npm locally; CI is the authoritative execution environment named in the packet.

### FE-S7 — Scheduled audit — **PASS**
- `scheduled-npm-audit.yml` (new): daily cron `41 6 * * *` (offset from Python `scheduled-audit.yml`'s 06:17 to avoid collision) + `pull_request` on the 4 web dep artifacts + `workflow_dispatch`. Runs the **identical** blocking audit body. `permissions: contents: read` (least privilege). `concurrency` with cancel-in-progress. A newly disclosed advisory against the already-merged lock turns the run red — the intended actionable signal, mirroring the Python pattern.

### FE-S8 — Permanent policy + emergency exception — **PASS**
- `docs/DEPENDENCY_SECURITY_POLICY.md` covers the full owner-specified rule set: advisory-free across runtime/dev/build/lock/audit tooling + all transitives (section 1); 7-day age fail-closed both ecosystems (section 2); exact pins + committed lockfile integrity via `npm ci` / `--require-hashes` (section 3); blocking audits on every change + schedule (section 4); post-merge advisory reopens security work + blocks deploy (section 5); pinned tooling (section 6); new-package provenance review — name/typo-squat, maintainers/ownership changes, install/lifecycle scripts, registry origin, publication age, prefer existing deps/stdlib (section 7); and the emergency exception (relaxes **age only, never an advisory**, owner-authorized, records name+version+reason+approver+UTC timestamp+expiry, auto-expires at 7 days, no wildcard/org-wide/permanent/undocumented, no `min-release-age-exclude`).
- The "Enforcing files" index maps every claim to an actual file, and I verified each npm-side mapping matches the implemented workflows/config. CLAUDE.md principle 15 is a concise, accurate pointer.

---

## Forbidden-path + no-behavior-change compliance — **CONFIRMED**

- `git diff --name-status origin/main...3bbb594`: exactly the 9 allowed files (M ci.yml, M generate-lockfile.yml, A scheduled-npm-audit.yml, M CLAUDE.md, A .npmrc, M package-lock.json, M package.json, A DEPENDENCY_SECURITY_POLICY.md, A producer-report.md). Nothing outside `allowed_paths`.
- `git diff` over `apps/web/src`, `services/api`, test files, `tsconfig.json`, `vitest.config.ts` = **empty**. No application/component/behavior change, no test or TS-settings weakening.
- CLAUDE.md diff = **single appended line** (principle 15); principles 1-14 byte-unchanged -> append-only, principle-15 compliant.
- `package-lock.json` was regenerated on a CI runner (not hand-edited by the producer) — consistent with the delta being a clean npm resolution (integrity hashes, registry URLs, correct transitive pruning).
- No Next 16, no canary, no `npm audit fix --force`, no automated downgrade, no `min-release-age-exclude`/allowlist anywhere.

---

## Non-blocking observations (for later disposition; none block acceptance)

1. **[LOW] Pre-existing nested `vite/node_modules/postcss` @ 8.5.19 is not clamped by the override.** The top-level `"overrides": {"postcss":"8.5.10"}` rewrote next's hoisted postcss (8.4.31->8.5.10) but vite's independently-hoisted nested copy remains 8.5.19. I confirmed via the node-level delta that this copy was **already 8.5.19 on `main` and is untouched by this PR** (not added/changed), so it is not a regression introduced here, and 8.5.19 is OSV-clean and 7.49 days old (passes both the audit gate and min-release-age). The policy doc section 3 describes `overrides` as the mechanism to force a transitive to "a fixed patched version"; in practice a bare override did not produce a single universal postcss version in this tree. Not a security or acceptance issue (both copies are advisory-free and higher-or-equal to the target); worth a future note if a truly uniform postcss pin is ever required.

2. **[INFO] `web-e2e` runs `npm ci --no-audit` without a co-located audit step.** This is a disclosed, deliberate single-sourcing of the audit (web job + scheduled workflow audit the same committed lock). Acceptable; noting only that if `web-e2e` ever diverged to a different lock it would install unaudited. Since `cache-dependency-path` and the lock are identical, there is no divergence today.

3. **[INFO] The `postcss` override relies on the same npm-11.18.0 regeneration path as the age gate.** If a future lock were ever regenerated with npm < 11.10.0, both `min-release-age` and override-under-age semantics would silently not apply. The pin + version-check in `generate-lockfile.yml` is the guard, and no committed workflow can regenerate with an older npm. The producer already discloses this in report section 9. No action needed.

---

## Exact commands run (reproducible)

- `gh pr diff 64` ; `gh pr checks 64` ; `gh pr view 64 --json headRefName,headRefOid,state,mergeable,files` (all 12 checks green; head = 3bbb594; 9 files)
- `git rev-parse HEAD` in worktree -> 3bbb594 (matches)
- `git diff --name-status origin/main...3bbb594` and scoped `git diff` over src/api/tests/tsconfig (empty)
- `git diff origin/main...3bbb594 -- CLAUDE.md | grep '^[+-]'` (single added line)
- Python over `apps/web/package-lock.json`: enumerate all postcss/next/react nodes; root deps/overrides; count 15.5.20 (36) / 15.3.4 (0)
- Python `git show main:... vs 3bbb594:...` node-level lock delta -> 0 added / 3 removed / 15 changed; all resolved = registry.npmjs.org; integrity present on all changed
- `node check.js` — offline simulation of the CI audit JSON gate across clean / one-low / info-only / high / missing-metadata / null-total shapes (fails closed on findings and on malformed input)
- Live `urllib` -> registry.npmjs.org (publication dates/ages) and api.osv.dev (advisories) for the 5 targets + npm 11.18.0 + postcss 8.5.19 + prior next@15.3.4

**Recommendation to orchestrator: record G3 + G4 as PASS.** No blocking corrections. The three observations above are informational/LOW and do not gate acceptance. (Reminder: G5 security-reviewer is a separately required gate for this task and is out of scope for this report.)
