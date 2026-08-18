# M0-T071 — Producer report (G2 self-check evidence)

Producer: orchestrator (single producer per D-015-R018; session 2026-08-18).
Branch `task/M0-T071-nanoid-ghsa-2v37`, worktree `wt-m0t071`, base = origin/main
`5c71fe0e08c8717cc20ac232d8bd0d8a328525e1` (deliberately unstacked from the
control and M0-T070 branches). Directive regime: `D-001:ALL; D-015:ALL`
(resolver `ok: true`, 21 applicable rows, no selective citation).

## What changed (implementation)

Exactly two application lines-of-intent, four physical lines:

1. `apps/web/package-lock.json` — the single `node_modules/nanoid` entry:
   version/resolved/integrity `3.3.17` → `3.3.18` (3 lines). Integrity is the
   registry-published value, fetched independently before the edit and verified
   cryptographically by `npm ci` after it.
2. `apps/web/package.json` — `overrides.nanoid` `3.3.17` → `3.3.18` (1 line).
   Required because the M0-T019 exact-pin policy pins the transitive there;
   `npm ci` fails closed on a lock-only bump (proof in the evidence record).
   This is the policy's pin mechanism, not a direct dependency.

Control plane: D-015 capture (28 requirements, source sha256 `4ec12ddd…`, all
registry files written as LF bytes with digests over those exact bytes — the
D-014 c14 lesson), M0-T071 packet + G0 PASS + claim, this report set.

## What was checked (full detail: M0-T071-dependency-evidence.md)

- Complete dependency-security policy run: deterministic `npm ci` (560 pkgs,
  integrity-verified); `npm audit --audit-level=low` → 0; audit JSON total 0 at
  every severity; authoritative committed-lock age gate PASS
  (`nanoid@3.3.18 age=917698s` > 604800s — **no waiver used**); registry
  integrity verification; npm CLI advisory verification (11.18.0) PASS; age-gate
  deterministic unit tests 40/40.
- Web battery: eslint clean; tsc clean; vitest **287 passed**; `next build`
  success. Playwright E2E not executable in this 3.11 sandbox (harness needs the
  Python 3.12 `app` package); covered by the PR's pinned CI `web-e2e` job.
- Advisory sweep: 3.3.18 affected by zero of the four nanoid GHSA advisories.
- Mechanical churn control (D-015-R015): local-npm `libc` churn fully reverted
  via plain file restore + surgical re-edit; final lock diff is exactly the
  3 nanoid lines; no git reset/clean used anywhere.

## Prohibition self-check

PR #222 and its branch untouched; M0-T070/D-014 untouched (their files exist
only on the other branch; this branch's diff contains none of them); supervisor/
controller untouched; no advisory suppressed/waived/allowlisted (the fix removes
the vulnerability instead); no broad upgrade (every other package version
byte-identical); nothing merged; control/context-intelligence-init not updated;
A1 not restarted.

Independent verification is owed by qa-engineer (G4) and security-reviewer (G5)
in parallel at the frozen implementation commit, plus directive-compliance
verification; this report claims nothing verified.
