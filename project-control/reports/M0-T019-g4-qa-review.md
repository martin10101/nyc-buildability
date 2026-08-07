<!-- VERBATIM reviewer return (G4 QA pass, performed by the code-reviewer agent under the QA lens;
recorded reviewer label: code-reviewer, a listed reviewer_agents entry per the gate class rules),
saved unchanged by the orchestrator per the report-preservation rule, 2026-08-07. -->

# PASS 2 — G4 QA REVIEW (M0-T019)

- **Gate ID:** M0-T019-G4 (QA)
- **Task ID:** M0-T019
- **Reviewer:** qa-engineer role (independent; != producer)
- **Reviewed head:** `f2dd11fd10deb6c450365ae7c3c8372a794c4229` on `control/D-009-batch-close`
- **Clean worktree used:** `C:/Users/MLFLL/Downloads/nyc-zoning/orch`; deliverable tree byte-identical to the G3-reviewed head (delta is ledger/reports-only).
- **Result: PASS** (3 non-blocking findings)

## Acceptance criteria reviewed (QA lens)

FE-S9 required failure modes and boundary arithmetic; test determinism/offline-ness; CI wiring of the unit tests + FE-S2/S9/S11 as blocking; scheduled re-audit; generate-lockfile validate-before-commit; regression integrity of the existing web suites; evidence-fixture internal consistency with the committed lock.

## Steps independently executed

1. `node --test apps/web/scripts/tests/dependency_age_gate.test.mjs` → **40 pass / 0 fail** (re-run at reconciled head).
2. Read the full 534-line test file and mapped every test to an FE-S9 failure mode.
3. Read `.github/workflows/ci.yml` (`web`, `web-e2e`, `web-dependency-security` jobs), `scheduled-web-audit.yml`, `generate-lockfile.yml`.
4. Cross-checked the four fixtures under `project-control/reports/m0-t019-fes9-mootness/` against the committed lock entries.

## FE-S9 failure-mode → test coverage matrix (all present)

| Required fail-closed / boundary mode | Test(s) | Status |
|---|---|---|
| 604800 s PASSES (full-second, no day rounding) | "exactly seven days (604800s) passes" | ✔ |
| 604799 s FAILS | "one second under seven days (604799s) fails" (asserts TOO_NEW + reason) | ✔ |
| Integrity mismatch (lock vs registry dist.integrity) | "integrity mismatch fails closed" | ✔ |
| Missing integrity in lock | "missing integrity in lock fails closed" | ✔ |
| Registry lacks dist.integrity | "registry lacking dist.integrity fails closed" | ✔ |
| Unexpected resolved host + look-alike host | "unexpected resolved host…", "look-alike registry host (registry.npmjs.org.evil.com)…" | ✔ |
| Missing / malformed publication timestamp | two dedicated tests | ✔ |
| Registry missing the version → MALFORMED | "registry missing the version fails closed" | ✔ |
| Ambiguous (conflicting integrity AND conflicting resolved) | two dedicated tests | ✔ |
| Registry outage / network error → INFRASTRUCTURE_UNAVAILABLE (never advisory-free) | provider outage, plain throw, utcNow/packument retry-exhaustion (asserts 4 attempts), non-200 → retry | ✔ |
| utcNow missing Date header → fail-closed, NOT retried | "utcNow fails closed (no retry loop)…" (asserts 1 call) | ✔ |
| parseLock structural robustness | non-JSON, no-packages-map, missing version, non-object entry, non-string version | ✔ |
| run() end-to-end aggregation | fails+names too-new package; passes all-valid | ✔ |
| FE-S11 npm CLI advisory (fail-closed, no suppression) | decideNpmCli pass/fail, runNpmCliAdvisory 0/1, unreachable→1, no-version→1 | ✔ |

Coverage is comprehensive: every fail-closed branch enumerated in the FE-S9 acceptance text and the gate header has at least one dedicated negative test, plus positive/boundary and end-to-end paths.

## Test determinism / offline-ness

All tests inject a fixed `now` (`NOW = 2026-08-05T00:00:00Z`) and a synthetic packument provider or fake `request` function; `run()` tests write a temp lock via `mkdtempSync`. No network, no `npm install`, node-builtins + `node:test`/`node:assert` only. Repeatable and hermetic — confirmed by a clean 40/40 local run. ✔

## CI wiring correctness

- **ci.yml `web-dependency-security` (push+PR, blocking):** unit tests (`node --test scripts/tests/*.test.mjs`) → npm ci (FE-S3) → `npm audit --audit-level=low` (FE-S2a) → JSON total==0 (FE-S2b) → FE-S9 committed-lock age gate → FE-S11 npm CLI advisory. Every step is a plain `run:` that fails the job on non-zero exit — no `continue-on-error`, no warning-only. ✔
- **ci.yml `web` / `web-e2e`:** unchanged except the additive npm@11.18.0 pin step; `web` runs lint/typecheck/build, `web-e2e` runs vitest + Playwright against the recorded-official-fixture API. The dependency task added no `apps/web/src/**` change, so regression surface is minimal. ✔
- **scheduled-web-audit.yml:** daily cron (`41 6 * * *`) + PR paths (package.json/lock/.npmrc/gate/tests) + workflow_dispatch, re-running the same blocking suite (unit tests + audit + FE-S9 + FE-S11). ✔
- **generate-lockfile.yml:** regenerates with `--package-lock-only` then **validates before committing** — npm ci + audit low + JSON total==0 + FE-S9 + FE-S11 all precede the commit step; the commit is guarded by `git diff --cached --quiet`. A validation failure means no bot commit (this is exactly why failed run 31211100620 produced no commit and successful run 31211311419 produced bot commit 1d678fd). ✔
- All third-party actions are SHA-pinned. ✔

## Regression coverage

The existing `web` (lint/typecheck/build) and `web-e2e` (vitest + Playwright) suites are structurally intact; only the npm-pin step was inserted. The framework bump (next→15.5.21, react/react-dom 19.1.2, eslint-config-next 15.5.21, postcss/sharp/brace-expansion/js-yaml overrides) is regression-validated by PR #176's 33/33 green checks (orchestrator-supplied CI evidence). These suites cannot be executed in this read-only thin-client sandbox (no node_modules); reliance on the green PR checks is appropriate and noted (Finding 3).

## Evidence-fixture integrity (internal consistency with the committed lock)

| Fixture | Cross-check vs lock | Status |
|---|---|---|
| brace-expansion-packument-excerpt.json | `time["1.1.18"]=2026-07-30T10:17:06.961Z` ↔ lock `node_modules/brace-expansion@1.1.18` (both root + nested, identical integrity) | consistent ✔ |
| sharp-packument-excerpt.json | `time["0.35.3"]=2026-07-01T11:28:34.077Z` ↔ lock `node_modules/sharp@0.35.3` | consistent ✔ |
| bulk-advisory-response.json | `{}` for {brace-expansion@1.1.18, sharp@0.35.3} → advisory-free (D-009-R014) | consistent ✔ |
| js-yaml-remediation-evidence.json | `time["4.3.1"]=2026-07-31T17:39:51.183Z`, `time["4.3.0"]=2026-06-26T22:29:00.874Z`; CVE-2026-59870 affects 4.0.0–4.3.0; `{}` for 4.3.1 ↔ lock `node_modules/js-yaml@4.3.1` | consistent ✔ |

The clearance arithmetic in the fixtures (publish + 604800s) reconciles exactly with the FE-S12 resolution record and the mootness timeline. Capture timestamps are coherent (three at 2026-08-07T19:20:32.535Z, js-yaml at 19:23:57.080Z, ~1 min before the bot lock commit at 19:24:55Z).

## Findings (numbered, with severity)

1. **LOW / observation (not a defect):** The 40 unit tests deliberately do not exercise the *real* committed `package-lock.json` (they use synthetic locks for determinism). The live full-tree age-gate run over the actual lock is a CI-only artifact (the FE-S9 step in ci.yml/scheduled-web-audit/generate-lockfile). This is the correct unit-vs-CI boundary; no rework needed.
2. **LOW / observation:** The four fixtures are partial packument *excerpts* capturing publication age + advisory status only; they do not carry `dist.integrity`. Tarball-integrity verification is covered separately by the committed lock's integrity hashes + `npm ci` in CI, not by these fixtures. Acceptable as age/advisory evidence; worth noting so the fixtures are not mistaken for integrity proof.
3. **LOW / environment:** Existing web regression suites (vitest/Playwright) and the full-tree `npm audit` cannot be reproduced in the read-only thin-client sandbox; this G4 relies on PR #176's 33/33 green checks for those. Recommend the orchestrator retain the PR #176 check run as the QA regression artifact of record. (Also carried forward from G3: js-yaml@4.3.1 cleared the age gate only ~1.75 h before the validated lock commit — a valid but razor-thin margin.)

None of the findings is blocking.

## Reviewer conclusion

**Pass 2 verdict: PASS.** The FE-S9 test suite comprehensively covers the required boundary and fail-closed modes, is deterministic and offline, and is wired as blocking across the push/PR CI, the scheduled re-audit, and the validate-before-commit lockfile workflow. Regression suites are unaffected (no `src/**` change; PR #176 green), and the evidence fixtures are internally consistent with the committed lock. Recommend recording G4 as PASS with the three non-blocking observations above.
