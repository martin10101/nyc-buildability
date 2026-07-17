# M2-T005 — G0 Definition-of-Ready Gate

- **Task:** M2-T005 — Confirm/Property a11y announcement + focus management (visual Major D1) and minor visual defects D2-D5 + G3 N1 test hygiene
- **Gate:** G0 (administrative, recorded by orchestrator)
- **Date:** 2026-07-17
- **Session:** 11

## Checklist (docs/GATES_AND_CHECKPOINTS.md G0)

1. **Objective unambiguous:** YES. Packet enumerates the exact defects (Major D1 announcement/focus; Minors D2 disabled styling, D3 bad-param h1, D4 flag duplication, D5 focus-ring contrast; G3 N1 NUL-byte hygiene) with source reports named as inputs. Bounded correction task, not a redesign.
2. **Dependencies accepted:** YES. Sole dependency M2-T002 is `accepted` (30th accepted task, CP-0024, immutable).
3. **File scope exclusive:** YES. `apps/web/**` + own producer report only. Disjoint from M2-T006 (`packages/contracts/**` + `services/api/**`). Neither task may touch `.github/workflows/**`. Overlap check performed this session: no shared files; the only cross-task coupling is CI running the whole repo, handled by the post-first-merge reconciliation procedure (update second branch from main, rerun full CI, prove reviewed-scope diff unchanged).
4. **Inputs and outputs defined:** YES (packet `inputs`/`outputs`).
5. **Acceptance scenarios exist:** YES. S1–S6 in the packet (announcement exactly-once, deterministic focus, minors, hygiene, regression, keyboard-only journey).
6. **Required source documentation available:** YES. `project-control/reports/M2-T002-visual-quality-review.md` (defect table), `project-control/reports/M2-T002-G3-human-journey-review.md` (N1), `docs/ACCEPTANCE_SCENARIO_STANDARD.md` UI pack, `docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md` — all present on main at 2a996a3.
7. **Credentials:** none required (frontend code + CI only). No new blockers.
8. **Required gates assigned:** G0/G2/G3/G4. Independent rosters per packet: human-journey-reviewer (G3), visual-quality-reviewer (G4). Producer: frontend-engineer. Producer ≠ reviewers; orchestrator barred from independent gates.
9. **Execution location and disk:** Implementation in local worktree `.claude/worktrees/M2-T005` (source-only checkout, well under budget; owner PC currently has ~31.9 GB free, far above the 4 GB floor). Heavy execution (npm install, vitest, Playwright e2e) is CI-ONLY on GitHub Actions per standing policy — NO local npm. Persistent artifacts: git (reports + code). No datasets, no local browser binaries.
10. **Cleanup:** worktree and local branch removed after acceptance; no temporary artifacts outside the worktree.

## Storage gate confirmation (docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md)

1. Executes in local source-only worktree + GitHub Actions CI.
2. Expected local usage: < 100 MB (worktree checkout). No node_modules locally.
3. Persistent output routed to GitHub (task branch → PR → main).
4. Owner PC stays far inside budget.
5. Cleanup: `git worktree remove` + branch deletion after acceptance; verified at hygiene step.

## Verdict

**PASS** — task is ready; backlog → ready.
