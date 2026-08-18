VERDICT: PASS

# G4 Independent QA Gate Report — M0-T071 (nanoid 3.3.17 → 3.3.18, GHSA-2v37-7h3g-55p8, D-015)

Reviewer: qa-engineer (read-only). Worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t071`. Frozen reviewed SHA: `e7c7d37745e35c56abb39f854bc14c44d6e87723` (verified == expected; base `5c71fe0e08c8717cc20ac232d8bd0d8a328525e1` verified). Toolchain: node v22.18.0, npm 11.4.2. All producer claims treated as unverified and re-derived from primary evidence.

## Frozen-head verification
`git -C wt-m0t071 rev-parse HEAD` → `e7c7d37...` ✓ ; `git rev-parse origin/main` → `5c71fe0...` ✓. Proceeded (not BLOCKED).

## Findings (by severity)

### Blocking defects
None.

### Low-severity / documentation observations
- **L1 — stale acceptance-scenario text.** `project-control/tasks/M0-T071.json` AS-1 asserts "package.json unchanged" and AS-6 asserts "only apps/web/package-lock.json (nanoid entry) + control-plane files change." Both predate the documented pre-submit contract correction that added the required `overrides.nanoid` line to `apps/web/package.json`. The controlling contract fields (`allowed_paths` now includes `apps/web/package.json`; `forbidden_paths` no longer lists it) and the objective correctly reflect the correction. Substance is met — the override is the exact-pin mechanism, not a direct dependency (D-015-R012 honored). Documentation nit only; recommend the orchestrator note the scenario-text/contract skew.
- **L2 — stale G0 report.** `project-control/reports/M0-T071-G0-contract-review.md` lines 21-22 still state "package.json and .npmrc are explicitly forbidden," describing the pre-correction contract. Same staleness class as L1; the corrected task packet governs. Non-blocking.
- **Informational.** Every npm invocation prints `npm warn Unknown project config "min-release-age"` (originates in the unchanged/forbidden `apps/web/.npmrc`). Pre-existing, unrelated to this task, non-blocking.

### Scope observations (non-defect)
- Working-tree shows uncommitted `project-control/state.json` and `project-control/tasks/M0-T071.json` (control-plane lifecycle bookkeeping) plus untracked `next-env.d.ts`, `tsconfig.tsbuildinfo`, `M0-T071-evidence-map.json`, `M0-T071.json`. None touch `apps/web` implementation files, which are clean at the frozen SHA. Review evaluates committed `e7c7d37`; implementation identity intact.
- R019 (commit/push/PR/wait) and R028 (return `NANOID_REPAIR_PR_READY`) are forward-looking orchestrator duties executed after this gate — not verifiable at the frozen commit, not QA-blocking. Reconciliation reqs R003–R009 bind the `D-015-BOOTSTRAP` sentinel (not the M0-T071 accept set) and verify at directive verification. The formal per-requirement directive verdict (`verification.json` fill) is owned by the separate `directive-compliance-verifier` (producer ≠ verifier); this G4 covers the technical/QA dimension.

## Explicit answers to the five review questions

**(1) Is the diff exactly minimal? — YES.**
`git diff 5c71fe0..e7c7d37 -- apps/` = exactly 4 lines: `apps/web/package-lock.json` the single `node_modules/nanoid` entry (version/resolved/integrity, lines 6238-6240) and `apps/web/package.json` `overrides.nanoid` (line 43). Grep confirms exactly one `node_modules/nanoid` entry in the lock. `dependencies`/`devDependencies` gained nothing (nanoid absent from both). No other package version, `resolved`, or `integrity` changed anywhere in the lock. Full changed-file set base→head = the 2 implementation files + `project-control/*` control-plane only; no `.github/`, `services/`, `.npmrc`, supervisor, PR #222 branch, or M0-T070/D-014 files. The single override change is provably part of the minimum: I reproduced `npm ci` on lock@3.3.18 + overrides@3.3.17 → `EUSAGE … Missing: nanoid@3.3.17 from lock file` (the M0-T019 exact-pin requires override/lock lockstep).

**(2) Do version/resolved/integrity match the registry? — YES.**
Lock: `3.3.18`, `https://registry.npmjs.org/nanoid/-/nanoid-3.3.18.tgz`, `sha512-DTg4MJbGMWkfi6VZFdNt2/caMbQy4Ou+Op/hJQvGEWcnVfoA1QA+xzRKAzw9jD6+GVOOeYr/mIcuDSdug6F6+w==`. Read-only fetch of `registry.npmjs.org/nanoid/3.3.18` returns byte-identical tarball URL and integrity. `npm ci` (560 packages) cryptographically verified the tarball against this hash with no error.

**(3) Do the age gate, CLI advisory, and audit reproduce green? — YES.**
- `node scripts/dependency_age_gate.mjs package-lock.json` → RESULT: PASS; `nanoid@3.3.18 uploaded=2026-08-07T16:41:05.696Z age=918353s (10.63d)` (> 604800s). Registry `time["3.3.18"]` independently confirmed 2026-08-07T16:41:05.696Z.
- `node scripts/dependency_age_gate.mjs --npm-cli-advisory 11.18.0` → PASS (no advisory affects npm@11.18.0).
- `node --test scripts/tests/*.test.mjs` → 40/40 pass.
- `npm ci --no-audit --no-fund` → 560 packages, integrity-verified; installed `require('nanoid/package.json').version` = 3.3.18.
- `npm audit --audit-level=low` → found 0 vulnerabilities (exit 0); `npm audit --json` `metadata.vulnerabilities` = `{info:0,low:0,moderate:0,high:0,critical:0,total:0}`.
- Web battery: `npm run test` (vitest) 287 passed / 22 files; `npm run typecheck` clean (exit 0); `npm run lint` clean (exit 0). E2E (Playwright) not runnable in this sandbox (harness needs the Python 3.12 `app` package; established M2-T015 constraint) — CI `web-e2e` covers it.

**(4) Is every producer claim evidence-backed? — YES (within QA scope), independently reproduced.**
- BEFORE failure: reconstructed base state (5c71fe0 package.json + lock, nanoid 3.3.17) in scratch, `npm ci` + `npm audit --audit-level=low` → "1 high severity vulnerability … nanoid <3.3.18 … GHSA-2v37-7h3g-55p8," audit exit code 1 (this is the failing CI condition / B-019). AFTER: 0 at every severity.
- Age > 604800s: reproduced 918353s via the authoritative repo mechanism; no waiver record exists and the gate passes on merit (not via waiver).
- No unrelated changes: confirmed by the name-only and content diffs.
- Advisory scope: OSV `GHSA-2v37-7h3g-55p8` (CVE-2026-67213, "custom generators can loop indefinitely when size is zero") affects nanoid `[0, 3.3.18)` — fixed 3.3.18; 3.3.18 affected by none. Matches the directive/task facts.
No producer claim within QA scope was found unbacked. (Forward-looking R019/R028 PR/return items are orchestrator duties outside this gate.)

**(5) Any regression risk? — NONE identified.**
nanoid 3.3.17→3.3.18 is a semver patch whose sole change is the security fix (infinite-loop guard when generator size is zero). nanoid is never imported in app source (grep of `apps/web` excluding node_modules matches only package.json/package-lock.json) — it is used purely transitively via postcss. postcss 8.5.23 declares `"nanoid": "^3.3.16"`, which admits 3.3.18, and generates identifiers with fixed positive sizes, so the patched zero-size code path is unreachable in this app. No API surface consumed by the web app changes. Full unit suite (287), typecheck, and lint remain green post-bump.

## Verdict
**PASS.** The implementation is the exact, minimal, registry-verified transitive bump to nanoid 3.3.18; the dependency-security policy suite (age gate, npm-CLI advisory, deterministic install, zero-vulnerability audit at every severity, age-gate unit tests) and the web unit/typecheck/lint battery reproduce green; the D-015 acceptance points (before-failure, after-zero, age > 604800s, no waiver, no unrelated changes) are independently reproduced; and the change carries no regression surface. Only low-severity documentation-staleness observations (L1/L2) remain, which do not affect the substance and are for orchestrator note.
