# G4 Gate Report — M0-T004 "Monorepo skeleton + GitHub Actions CI"

**Gate:** G4 (integration and regression)
**Reviewer:** qa-engineer (independent; producer was backend-engineer)
**Date:** 2026-07-15
**Process:** two-pass. Pass 1 verified merge integrity, contracts, no-duplicates, migrations N/A, low-storage, idempotency/perf N/A, but returned BLOCKED because the reviewer sandbox could not execute gh/python (denials recorded). Per owner directive 2026-07-15 (now in `.claude/rules/project-control.md`), the orchestrator captured executable evidence into committed artifacts and pass 2 verified the stored evidence.

## Verdict: PASS

## Summary (pass 2)

Both open items from the prior G4 pass are closed by orchestrator-captured, committed evidence. The stored `gh run view` capture for run 29455862963 shows a completed, successful post-merge CI run on `main` at SHA `b90984f...`, with all four required jobs green, and the git ref log proves that SHA is a direct descendant of merge commit `1c1eee3` and an ancestor of the current `main` tip (`41ab47d`). The regression artifact records the project-control workflow regression suite passing, corroborated independently by the successful `control-plane` CI job in the same run. Combined with pass 1's already-verified findings (true --no-ff merge, full skeleton tree, validated contracts, no duplicates, low-storage compliance), G4 is satisfied for the M0-T004 skeleton stage.

## Verification table (pass 2)

| # | Check | Expected | Actual | Evidence |
|---|-------|----------|--------|----------|
| 1a | CI run status/conclusion | completed / success | `"status":"completed"`, `"conclusion":"success"` | `project-control/reports/M0-T004-main-ci-evidence.json` |
| 1b | Branch of CI run | main | `"headBranch":"main"` | same file |
| 1c | All 4 jobs succeed | contracts, control-plane, web, api all success | "contracts (JSON Schema validation)", "control-plane (workflow regression test, ADR-005)", "web (lint + typecheck + build)", "api (ruff + pytest)" — each `status:completed`, `conclusion:success`; every step success; job URLs all under run 29455862963 | same file |
| 2a | Evidence SHA on main | `b90984f...` ancestor of current main | Reflog chain (each entry's old-SHA = prior new-SHA, no resets): `1c1eee3 → b90984f → adda8c6 → 41ab47d`; `refs/heads/main` = `41ab47d8232e...` | `.git/logs/refs/heads/main` lines 11–14; `.git/refs/heads/main` |
| 2b | Evidence SHA contains merge 1c1eee3 | `1c1eee3` ancestor of `b90984f` | `b90984f` is the immediate child of `1c1eee3` (reflog line 12); line 11 confirms `1c1eee3` is the `task/M0-T004-monorepo-ci` merge onto main | `.git/logs/refs/heads/main` |
| 3 | Regression suite passed | "OK: all project-control workflow regressions passed" | Exact string present (sole line of file); corroborated by the successful "Run project-control regression test" step in CI job 87488771688 | `project-control/reports/M0-T004-control-plane-regression.txt`; evidence JSON |
| 4 | Evidence files committed | committed to main | Commit `adda8c6` "M0-T004 G4 unblock: orchestrator-captured CI + regression evidence; reviewer evidence-capture rule"; files present in clean main checkout | `.git/logs/refs/heads/main` line 13 |

## Pass 1 checklist (independently verified 2026-07-15, carried forward)

- Merge integrity: `git log -1 --format=%P 1c1eee3` → parents `ca34fd4`, `a0d8f3a` (true --no-ff merge of task branch head). Main tree contains apps/web, services/api, packages/contracts/schemas/v1 (3 schemas), supabase/migrations/.gitkeep, .github/workflows/ci.yml (4 jobs). **PASS**
- Contract compatibility: all 3 v1 schemas well-formed JSON with `$schema`/`$id`/`title`/`description`; CI contracts job deterministic on this tree. **PASS**
- No duplicate/contradictory implementations: only ci.yml + generate-lockfile.yml (dispatch-only utility); single skeleton per app/service. **PASS**
- Migrations: none (.gitkeep only) — forward/rollback **N/A**.
- Low-storage: `git diff --stat ca34fd4..1c1eee3` → 22 files, 6,269 insertions, all text; no node_modules/.next/venv anywhere; reviewer worktree clean. **PASS**
- Job idempotency / performance budgets: **N/A** at skeleton stage (stated explicitly, not silently deferred).

## Discrepancies / limitations

1. No functional discrepancies; evidence JSON headSha, branch, job set, and conclusions match the claimed state exactly.
2. Sandbox limitation (not a defect): pass-2 reviewer could not execute even git read commands; substituted authoritative verification from `.git/logs/refs/heads/main` (append-only ref log, strict linear ancestry, no resets/rebases). Exact denial recorded: "Permission to use Bash has been denied".
3. Minor: the CI evidence JSON does not embed the run ID field itself, but all four job URLs are of the form `.../actions/runs/29455862963/job/...`, tying the capture to the claimed run.
4. Process finding PF-1 from pass 1 (reviewer evidence-access gap) is resolved by the owner's evidence-capture directive of 2026-07-15, recorded in `.claude/rules/project-control.md`.
