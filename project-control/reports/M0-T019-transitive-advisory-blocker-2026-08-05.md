# M0-T019 — transitive-advisory age blocker + remediation plan (2026-08-05)

**Status: BLOCKED (B-017). Not an Opus-vs-Fable issue, not a build/config defect — a real
dependency-security age condition. Earliest remediation window: 2026-08-06T10:00–10:17Z.**

This report is the executable plan for finalizing M0-T019 once the blocker self-clears. It records
exactly what was found, why the tree cannot be finalized tonight, and the precise morning steps.

---

## 1. What happened

The M0-T019 producer deliverable (branch `control/D-009-depsec-and-m0t019-dispatch`, head `ea5d172`)
carries the reconciled security target in `apps/web/package.json`:

```
next 15.5.21 · react 19.1.2 · react-dom 19.1.2 · eslint-config-next 15.5.21 · overrides.postcss 8.5.23
```

The committed `apps/web/package-lock.json` is intentionally still the pre-patch 15.3.4 tree — the
security-patched lock is regenerated on a CI runner (thin-client: no npm on the owner PC) by
`.github/workflows/generate-lockfile.yml`, which validates the fresh lock (npm ci integrity →
blocking `npm audit` → FE-S9 age gate → FE-S11 npm-CLI advisory) **before** the bot commits it.

I dispatched that workflow on the branch. It **failed closed at the blocking `npm audit` step** —
runs `30974409084` (04:11Z) and `30976237680` (04:49Z), both 2026-08-05 — with **3 HIGH advisories**
in the freshly regenerated full tree. This is exactly the CI-artifact failure the producer report
anticipated ("if on regeneration ANY transitive carries an advisory … surface to the owner; do not
waive"). The gate is behaving correctly.

## 2. The advisories (verified against the npm bulk advisory endpoint)

Source: `POST registry.npmjs.org/-/npm/v1/security/advisories/bulk` — the exact source `npm audit`
consults. Queried 2026-08-05.

### 2a. sharp — HIGH — **fixable tonight via override**
- `sharp <0.35.0` carries inherited libvips CVE-2026-33327/33328/35590/35591 (GHSA-f88m-g3jw-g9cj).
- It is pulled as **next@15.5.21's optionalDependency `sharp: ^0.34.3`**, which caps below 0.35.0 —
  that is why npm's naive `audit fix --force` proposes **next@16 (HARD-PROHIBITED)**.
- Fix without Next 16: a package.json override **`"sharp": "0.35.3"`** (published 2026-07-01T11:28:34.077Z,
  advisory-free, ~35 days old — clears the age gate comfortably). Overrides beat an optionalDependency
  range, so this forces the patched sharp while next stays at 15.5.21.
- The third audit line ("next depends on vulnerable sharp") resolves automatically once sharp is overridden.

### 2b. brace-expansion — HIGH — **THE HARD BLOCKER (every fix is <7 days old)**
- Transitive (eslint/minimatch/glob dev+build tooling and elsewhere). Multiple advisory families;
  combined advisory-free thresholds:

  | line | first advisory-free version | npm publish (UTC) | 7-day clears at (UTC) | age at 2026-08-05 |
  |------|-----------------------------|-------------------|-----------------------|-------------------|
  | 1.x  | **1.1.18** | 2026-07-30T10:17:06.961Z | **2026-08-06T10:17:06.961Z** | ~5.8 days |
  | 2.x  | **2.1.4**  | 2026-07-30T10:15:01.601Z | 2026-08-06T10:15:01.601Z | ~5.8 days |
  | 5.x  | **5.0.9**  | 2026-07-30T10:00:32.762Z | 2026-08-06T10:00:32.762Z | ~5.8 days |

  (The entire 3.x/4.x lines stay vulnerable — GHSA "exponential-time expansion" is vulnerable
  `>=3.0.0 <5.0.7`.)
- **No advisory-free brace-expansion version is ≥7 complete days old.** The FE-S9 age gate requires
  ≥604800 s and has **no exception path by design**; the owner previously **DECLINED** age exceptions
  for M0-T019 (B-013). So the tree cannot be finalized advisory-free-AND-aged until **2026-08-06**.

## 3. Why this is a true STOP tonight (not something to force on Opus)

- It is one of M0-T019's own documented STOP conditions: *"a required fix is <7 days old needing an
  owner exception"* and *"if registry/advisory state has changed, STOP and report — no silent substitution."*
- It is independent of the reviewer model (Opus 4.8 vs Fable 5) and of any build/config change.
- The owner-declined-exception stance + FE-S9's no-exception design mean no paper waiver can pass it.
- Recording M0-T019's G3/G4/G5 now would gate a **non-final** head (the overrides + regenerated lock
  are still owed), so gates are held per the batch sequencing rule ("lockfile CI before gates").

## 4. Remediation plan (execute on/after 2026-08-06T10:17:06.961Z)

1. **Confirm posture** at owner morning review: default = WAIT + apply overrides (this plan). Owner
   may direct otherwise.
2. **Producer edit** (frontend-engineer, in-scope path `apps/web/package.json` overrides only):
   ```jsonc
   "overrides": {
     "postcss": "8.5.23",
     "sharp": "0.35.3",
     "brace-expansion": "1.1.18"   // start here (lowest-compat-risk 1.x line); see step 4
   }
   ```
   Update the producer report §2 with the two new overrides' registry-time + advisory-free evidence.
3. **Regenerate the lock via CI** (`Generate web lockfile` on the branch). The job re-runs npm ci +
   blocking audit + FE-S9 age gate + FE-S11 across the whole regenerated tree and only commits if all pass.
4. **Settle the brace-expansion line by CI, not fiat.** A single global `brace-expansion` override
   forces one version on all consumers. If npm ci / build / tests break a consumer that needs a
   different major (e.g. minimatch@9+ expecting ^2.0.1), switch the override to `2.1.4`, or use a
   targeted/nested override per consumer. `npm audit` reported brace-expansion fixable via a
   NON-breaking `npm audit fix`, so a compatible patched set exists; CI identifies the right one.
5. **Trigger full CI** on the branch (the bot's GITHUB_TOKEN push does not trigger downstream CI — use
   an orchestrator commit/empty-commit to run `ci.yml`): web (lint/typecheck/Vitest/production build/
   Playwright) + web-dependency-security (audit-zero + age gate) must be green on the regenerated lock.
6. **Then, and only then**, submit → G2 self-check → G3 (code-reviewer) / G4 (qa-engineer) /
   G5 (security-reviewer) at the finalized head. See §5 for the advisory pre-gate already done.
7. Resolve B-017 with the regenerated-lock CI evidence.

## 5. Advisory pre-gate code review (done tonight, de-risks the morning)

An independent code-reviewer (Opus 4.8 xhigh) reviewed the **stable** source that will NOT change
when the overrides land — the FE-S9/FE-S11 machine gate `dependency_age_gate.mjs` + its tests, the
CI/workflow wiring, package.json/.npmrc, the policy doc, and the CLAUDE.md rule. Result recorded
below (advisory only — the formal G3 runs at the finalized head):

**Pre-gate verdict: PASS-WITH-NITS.** The FE-S9 age-gate script is sound — the 604800 s boundary
(604800 passes / 604799 fails, full-second, no day rounding), the registry-Date clock source, the
integrity+host binding to the official registry, the fail-closed semantics on every error kind, the
distinct infrastructure-unavailable outcome (bounded retries + backoff), the FE-S11 npm-CLI path, and
the blocking CI/scheduled/generate wiring (SHA-pinned actions) are all confirmed correct, with no
allowlist/exception path. No blocking or major defects. Six minor/nit items, each already backstopped
(none block finalization); fold them into the remediation edit since they touch the same allowed paths:
(1) host check is a no-op when a lock entry's `resolved` is explicit-null — integrity match still binds
identity; (2) entries lacking `resolved` are skipped — npm ci is the intended backstop; add a clarifying
comment; (3) the JSON `total==0` step fail-opens if audit metadata is absent — backstopped by the
preceding blocking audit; (4) generate-lockfile pre-commit validation omits the stricter JSON total==0
check ci.yml runs — consider adding for consistency; (5) test-coverage nits (host-slash boundary,
run() aggregation, success paths, parseLock throws) — the load-bearing properties are well covered;
(6) perf: sequential per-entry packument fetches can be slow under a partial outage — correctness
unaffected (still fails closed).

## 6b. Supply-chain deep verification (owner directive 2026-08-05)

Owner directive (intent): the 7-day rule may yield to a 6-day age if the package is advisory-free AND a deep web search confirms it is not compromised, because npm currently has an active bad-publish problem.

I ran the deep search. **Verdict: the specific fix packages are verified clean; separately, there is an active npm bad-publish incident right now, which is exactly why the age filter is valuable.**

**brace-expansion (1.1.18 / 2.1.4 / 5.0.9) — CLEAN.** Releases are by the legitimate long-time maintainer (@juliangruber) with verified GPG signatures. Its 2026 issues are genuine DoS/ReDoS CVEs (real fixes, not a cover for a bad publish). The fix versions were published 2026-07-30, five days before the current incident, and are not on its affected-package list.

**sharp 0.35.3 — CLEAN.** Released 2026-07-01 by the maintainer (Lovell Fuller), GPG-verified; Snyk lists 0.35.3 as the latest non-vulnerable version.

**Active incident context.** A self-propagating npm publish incident was disclosed 2026-08-04 (one day ago) affecting several hundred package versions, including keyv/flat-cache/file-entry-cache — which sit transitively under the ESLint toolchain this web tree uses. The registry began removing the bad versions the same day. The 7-day age filter (and `.npmrc min-release-age=7` at resolution) already excludes every version from that window, so it is actively protecting this tree; `--ignore-scripts` at install is the recommended neutralizer.

**Decision.** The verified-clean status means the brace-expansion fix meets the owner's 6-day criterion. But acting at 6 days requires editing FE-S9 (the machine gate is hard-set to 7 days with no exception path by owner design 2026-07-23), i.e. reversing a binding, independently-reviewed security control — which I will not do unattended during an active incident. It is also moot tonight: brace-expansion 1.1.18 does not reach even 6 days until 2026-08-05T10:17Z, and the tree still needs the overrides + a full CI regeneration, so nothing installs tonight either way and waiting for the owner's nod costs no time.

- **Option A (recommended): hold to 7 days** — clears naturally 2026-08-06T10:17Z, no gate change, full protection through the incident window; the deep search de-risks it so we proceed confidently at clearance.
- **Option B: 6-day verified path** — I add a scoped, owner-authorized, auto-expiring FE-S9 exception for the three verified-clean versions only, re-gated (G3/G5); a deliberate reviewed change, not a silent weakening.

Regardless of A/B: (i) confirm the regenerated lock excludes the incident-window keyv/flat-cache/file-entry-cache versions (the age filter should already do this); (ii) evaluate scoping `ignore-scripts` in CI — caveat: sharp uses an install script for its native binary, so a blanket setting can break image handling; scope it rather than applying wholesale.

## 6. Knock-on: what this blocks

- **M2-T014** (survey Packet A) is fully gate-complete (G0/G2/G3 PASS + the supplementary
  security-reviewer leg run tonight) but declares M0-T019 as a dependency, so its **acceptance** waits
  on M0-T019 unless the owner elects to accept it independently (it is research-only; its content does
  not depend on the security patch).
- **M2-T015 / M2-T016 / M6-T001** are downstream of M2-T014 acceptance — not dispatchable tonight.
- **Public frontend deployment (B-012)** stays blocked until M0-T019 is accepted.
