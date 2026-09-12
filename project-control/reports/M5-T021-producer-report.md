# M5-T021 Producer Report — D-042 Next.js 15.5.24 upgrade + whole-tree advisory sweep

Producer: orchestrator (dependency task; gh workflow dispatch is orchestrator-only authority).
Packet: 9cf2890b (G0 PASS; claim recorded). Cites D-042:D-042-R001 (applicability append,
digest 7fd8d5c2 -> 2a1b8b0c).

## 1. What changed (all inside allowed_paths)

`apps/web/package.json` — six version values, nothing else:

| Entry | Old | New | Why (advisory / registry evidence) |
|---|---|---|---|
| dependencies.next | 15.5.21 | **15.5.24** | D-042-R001 exact pin. Fixes CRITICAL GHSA-p293-qw3h-jr36 + GHSA-2xp9-vwfh-vxw4 (range <15.5.24). Published 2026-08-25T16:14:06Z = 17.3d ≥ 7d. OSV on 15.5.24: none open. |
| devDependencies.vitest | 3.2.7 | **4.1.11** | GHSA-82fw-gwwq-j7x9 (@vitest/mocker path traversal) has NO 3.x fix; 4.1.11 is the minimal fixed version. Published 2026-08-18 = 25d. Major bump — the audit's "fix --force". |
| overrides.sharp | 0.35.3 | **0.35.4** | GHSA-rgj7-g3m4-5g8c (libheif RCE bundle, CRITICAL, published 2026-09-08) — found by the registry research beyond the originally-listed advisories; fixed 0.35.4, published 2026-08-26 = 16.6d. |
| overrides.js-yaml | 4.3.1 | **4.3.2** | GHSA-2883-xcg3-v3hh — the old override force-pinned the vulnerable 4.3.1, BLOCKING its own in-range fix. 4.3.2 published 2026-08-26 = 16.1d. |
| overrides.baseline-browser-mapping | (none) | **2.11.21** | GHSA-w5vr-8v7q-w6rv fixed in 2.11.0, but a free regen resolves 2.11.22/2.11.23 (2d/0d old) which FAIL the age gate — the override pins the newest AGED fixed version (2026-09-03 = 8.3d). |
| overrides.browserslist | (none) | **4.28.9** | GHSA-c83g-rgw3-j3cx + GHSA-73wf-gq98-2v4g fixed in 4.28.7. First workflow run proved `npm install --package-lock-only` PRESERVES existing in-range resolutions, so the vulnerable locked version survived — the override forces the aged fixed 4.28.9 (2026-09-04 = 8.4d). |

`apps/web/package-lock.json` — regenerated and committed BY THE WORKFLOW BOT (d83bcfe5),
+319/−397 lines, 553 package nodes. Resolutions verified post-pull: next 15.5.24,
sharp 0.35.4, js-yaml 4.3.2, vitest 4.1.11, @vitest/mocker 4.1.11, browserslist 4.28.9,
baseline-browser-mapping 2.11.21.

Registry/OSV evidence for every value: `project-control/reports/M5-T021-registry-research.md`
(preserved verbatim researcher deliverable; npm registry .time timestamps + OSV clean-version
queries, accessed 2026-09-12).

## 2. The sanctioned thin-client path, exactly as designed

No npm ran locally (docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md). Two dispatches of
`.github/workflows/generate-lockfile.yml` on `candidate/D-024-mrl-option-b`:

1. **Run 34726060266 — FAILED CLOSED, as designed.** Step 7 (blocking npm audit) found
   browserslist still vulnerable (the preserved-resolution mechanic above); the bot committed
   NOTHING. This is the fail-closed proof chain doing its job — a defective lock cannot land.
2. **Run 34726113984 — SUCCESS end-to-end** after the browserslist override (3cd3b93c):
   npm 11.18.0 pinned → `npm install --package-lock-only` (honoring .npmrc min-release-age=7
   + save-exact) → `npm ci` deterministic install (integrity + lock↔package.json) →
   **blocking `npm audit --audit-level=low` PASS** → **audit JSON total vulnerabilities == 0
   across every severity** → **committed-lockfile release-age gate PASS (fail-closed)** →
   npm CLI advisory check PASS → bot commit d83bcfe5.

**The web tree is advisory-free at every severity for the first time since the Next.js
advisories landed.**

## 3. Scenario status

- S1 exact pin + sweep: table above; `dependencies.next == "15.5.24"` exactly; no 16.x;
  every change advisory-driven with registry timestamp evidence; react/react-dom untouched.
- S2 workflow-proven lock: run 34726113984 SUCCESS (the four-check chain before the bot
  commit); the first run's fail-closed refusal is the negative proof.
- S3 CI green: pending the push of this report (bot pushes do not trigger ci.yml); the run on
  this head is the executable authority — web-dependency-security expected GREEN (the last
  standing red retired), web + web-e2e prove the app + suites on next 15.5.24 / vitest 4.1.11.
- S4 prohibitions: no deploy performed or configured (render.yaml/.github untouched — CI
  evidence will show forbidden paths byte-unchanged); no 16.x; no app-code change; Supabase/G6
  untouched.

## 4. Risks and honest notes

- vitest 3→4 is a major bump; the web-e2e vitest suites on the CI run are the proof they
  survive. If they fail, the vitest pin becomes its own bounded correction (packet risk).
- eslint-config-next stays 15.5.21 (not advisory-named; minimal-diff discipline). If the CI
  web lint job objects to the version skew, that becomes a bounded correction with its own
  age-gate check.
- The audit's literal "7th" entry was inferred (sharp node) — the authoritative fact is the
  workflow's audit JSON total == 0 at the regenerated lock, which subsumes the counting
  question.
