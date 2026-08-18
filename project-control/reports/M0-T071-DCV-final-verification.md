VERDICT: PASS

# D-015 / M0-T071 — Independent directive-compliance verification (FINAL)

Verifier: directive-compliance-verifier (independent; producer = orchestrator; read-only run — the verdict below was returned to the orchestrator for recording, and the verifier wrote no control-plane state).

Reviewed head `a997f19bb2f9d3c76d5d08885144de7d4f4f8517` confirmed (`git rev-parse HEAD`); worktree clean (`git status --porcelain` empty). Canonical implementation `e7c7d37745e35c56abb39f854bc14c44d6e87723`; the head adds control-plane evidence only. Material identity over the packet's `allowed_paths` at HEAD, recomputed via `tools.directive_registry.frozen_git_identity`, = `371eb3dac9250537ba5f8bc21d74c20515b292249dfff3406cefa82c4c27f361` — matches the acceptance charge AND the `content_manifest_sha256` recorded on gates G2/G4/G5. The 4 allowed_paths files are byte-identical between `e7c7d37` and `a997f19` (empty diff), so the identity is stable across the control-plane commit. Live `origin/main` = `5c71fe0e08c8717cc20ac232d8bd0d8a328525e1` (unchanged). Source digest `4ec12ddd…` and requirements content digest `9f14636f…` reproduce the manifest values. `python tools/validate_directive_compliance.py --check` → exit 0.

| id | status | primary evidence (reproduced) |
|---|---|---|
| D-015-R001 | PASS | Lock diff `node_modules/nanoid` 3.3.17→3.3.18; verifier reran `scripts/dependency_age_gate.mjs package-lock.json` → `PASS nanoid@3.3.18 uploaded=2026-08-07T16:41:05.696Z age=919738s` (> 604800s); no waiver artifact anywhere in `git diff --name-only 5c71fe0..a997f19`. |
| D-015-R002 | PASS | Name-only diff contains no `M0-T070.json`/PR#222 file; `M0-T071.json` absent on `5c71fe0` and `de2f224` (newly created); PR #222 head still `09e23162…` OPEN. |
| D-015-R003 | PASS | Live `git ls-remote origin main` = `5c71fe0…`; `merge-base(5c71fe0,a997f19)` = `5c71fe0`; manifest `frozen_baseline_sha` matches. |
| D-015-R004 | PASS | `wt-m0t070 HEAD:…/B-019-….json` exists, `status:"open"`, nanoid 3.3.17 / GHSA-2v37-7h3g-55p8; BEFORE integrity `sha512-xQLf0A3…` matches the lock's pre-image. |
| D-015-R005 | PASS | Committed lock `node_modules/postcss` (8.5.23) requires `"nanoid":"^3.3.16"`; exactly one `node_modules/nanoid` entry (grep count = 1). |
| D-015-R006 | PASS | Authoritative age-gate rerun → PASS, registry `uploaded=2026-08-07T16:41:05.696Z`, age 919738s. |
| D-015-R007 | PASS | CI `web-dependency-security` SUCCESS on head `a997f19` (33/33 checks SUCCESS); advisory range `<3.3.18` patched by 3.3.18; G4/G5 independently reproduced audit `total:0`. |
| D-015-R008 | PASS | `M0-T071.json` absent on `5c71fe0` and `de2f224`; `M0-T070.json` present on its branch → M0-T071 was next free ID. |
| D-015-R009 | PASS | `merge-base(origin/main,HEAD)` = `5c71fe0`; linear 2-commit history on `task/M0-T071-nanoid-ghsa-2v37`. |
| D-015-R010 | PASS | Lock diff: version/resolved/integrity updated; single nanoid entry. |
| D-015-R011 | PASS | Lock diff exactly 3 lines; integrity `sha512-DTg4MJbGMWkfi6VZFdNt2/…` verified (age-gate integrity check; G5 byte-for-byte tarball+registry match). |
| D-015-R012 | PASS | `git show e7c7d37:apps/web/package.json`: no nanoid in dependencies/devDependencies; only `overrides.nanoid` (exact-pin mechanism). |
| D-015-R013 | PASS | Only 2 implementation files in the full diff; every other lock entry byte-identical. |
| D-015-R014 | PASS | Final lock diff = exactly the 3 nanoid lines — the multi-entry rewrite shape of an unrestricted `npm audit fix` is absent. |
| D-015-R015 | PASS | No unrelated churn in the committed diff (libc churn reverted); worktree clean; no reset/clean residue. |
| D-015-R016 | PASS | Verifier reran age gate + CLI advisory PASS; G4 independently reran npm ci (560 pkgs), audit 0/total 0, vitest 287, tsc/eslint clean; CI `web`, `web-e2e`, `web-dependency-security`, `exact-production-install` all SUCCESS (E2E covered in CI). |
| D-015-R017 | PASS | `M0-T071-dependency-evidence.md` committed at `e7c7d37`: before-failure / after-zero / age 917698s>604800s / no waiver / no unrelated changes. |
| D-015-R018 | PASS | Gate records: G4 `qa-engineer`, G5 `security-reviewer`, both independent at `reviewed_sha e7c7d37` / manifest `371eb3d…`, both PASS, parallel (07:53:22 / 07:56:36); single producer orchestrator. |
| D-015-R019 | PASS | Commit `e7c7d37` pushed; PR #223 base `main`, OPEN; `gh pr checks 223` = 33 rows, all SUCCESS. |
| D-015-R020 | PASS | `gh pr view 222`: head `09e23162…`, OPEN, mergedAt null — branch untouched. |
| D-015-R021 | PASS | Full name-only diff has no `M0-T070.json` and no `D-014-*` file. |
| D-015-R022 | PASS | Diff grep for `agent_supervisor`/controller paths → NONE. |
| D-015-R023 | PASS | `.npmrc` byte-identical; no waiver/allowlist/suppression file in diff; advisory removed by upgrade; CI audit green on merit. |
| D-015-R024 | PASS | Single-package bump; every other package version byte-identical. |
| D-015-R025 | PASS | PR #223 mergedAt null (OPEN); PR #222 mergedAt null (OPEN); `origin/main` still `5c71fe0`. |
| D-015-R026 | PASS | `origin/control/context-intelligence-init` tip = `de2f224`; no M0-T071 commit in its history. |
| D-015-R027 | PASS | `wt-m0t063 HEAD` = `de2f224`, clean — A1 untouched, not restarted. |
| D-015-R028 | PASS | `M0-T071-return-report.md` committed at `a997f19`: `NANOID_REPAIR_PR_READY` with all 11 required items present. |

## Applicable sets
21 M0-T071-bound rows (R001, R002, R010–R028) + 7 sentinel-only rows (R003–R009), confirmed by reading `requirements.json` applicability.

## Totals
**28 PASS / 0 FAIL / 0 UNVERIFIABLE.**

## Harness outputs (independently executed)
- `python tools/validate_directive_compliance.py --check` → exit 0
- `python tools/test_directive_compliance.py` → 120 tests OK, exit 0
- `python tools/test_project_control.py` → all 23 groups passed, exit 0
- `python tools/test_directive_reminder.py` → 12 tests OK, exit 0
- `node scripts/dependency_age_gate.mjs package-lock.json` → RESULT PASS (nanoid@3.3.18 age 919738s)
- `node scripts/dependency_age_gate.mjs --npm-cli-advisory 11.18.0` → RESULT PASS

## Discrepancies between producer claims and primary evidence
None material. Notes: (1) age figures differ across runs (917698s / 918353s / 918482s / 919738s) — expected monotonic wall-clock drift, all > 604800s. (2) Non-blocking documentation skew (G4 L1/L2, disclosed in the return report §8): the packet's AS-1/AS-6 text and two G0-report lines predate the pre-submit contract correction that added the `overrides.nanoid` line; the governing packet fields and objective correctly reflect the correction; substance satisfies D-015-R012. Not a compliance defect; no requirement verdict affected.
