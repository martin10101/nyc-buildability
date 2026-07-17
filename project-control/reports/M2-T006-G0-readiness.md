# M2-T006 — G0 Definition-of-Ready Gate

- **Task:** M2-T006 — Property-profile contract 1.3.0 (additive): reproducibility.staleness object, correlation_id description refresh, open-schema key documentation
- **Gate:** G0 (administrative, recorded by orchestrator)
- **Date:** 2026-07-17
- **Session:** 11

## Checklist (docs/GATES_AND_CHECKPOINTS.md G0)

1. **Objective unambiguous:** YES. Additive 1.3.0 bump with three enumerated changes: (1) typed `reproducibility.staleness` object (`served_from_cache`, `stale`, `upstream_error_type`, `original_retrieved_at`, `age_seconds`) per M1-T009 G1 D1/D2; (2) refreshed `correlation_id` description; (3) documented open-schema derivation/mapped-feature keys per M2-T002 G3 N3. Typegen regeneration, atomic declared-vs-emitted move to 1.3.0, 1.2.0 compatibility preserved.
2. **Dependencies accepted:** YES. M2-T003 (contract/typegen pipeline) and M1-T009 (resilience/LKG convention) are both `accepted` and immutable.
3. **File scope exclusive:** YES. `packages/contracts/**` + `services/api/**` + own producer report. Disjoint from M2-T005 (`apps/web/**`). `apps/web/**` is explicitly FORBIDDEN — if the additive change would require client edits, producer must stop and report for a follow-up packet. `.github/workflows/**` forbidden (typegen/bundle jobs must pass unchanged). Cross-task coupling limited to whole-repo CI; handled by the post-first-merge reconciliation procedure.
4. **Inputs and outputs defined:** YES (packet `inputs`/`outputs`).
5. **Acceptance scenarios exist:** YES. S1–S7 (schema validity + byte-identical typegen, stale serve emission, fresh serve truthfulness, atomic version enforcement, 1.2.0 compatibility, correlation_id description accuracy, full regression).
6. **Required source documentation available:** YES. `project-control/reports/M1-T009-G1-data-contract-review.md` (D1/D2 verbatim), `project-control/reports/M2-T002-G3-human-journey-review.md` (N3), `packages/contracts/schemas/v1/property_profile.schema.json` at 1.2.0, generated types, `services/api/app/resilience/**` — all present on main at 2a996a3.
7. **Credentials:** none required. B-001 no-deploy stands; CI-only proof. No new blockers.
8. **Required gates assigned:** G0/G1/G2/G3/G4. Independent rosters per packet: data-contract-verifier (G1), code-reviewer (G3); G4 integration evidence reviewed independently per roster. Producer: backend-engineer. Producer ≠ reviewers; orchestrator barred from independent gates.
9. **Execution location and disk:** Implementation in local worktree `.claude/worktrees/M2-T006` (source-only checkout). Python/pytest for services/api may run locally ONLY if the existing environment already supports it without heavy installs; otherwise CI-only. Node typegen is CI-ONLY (no local npm). Owner PC currently ~31.9 GB free, far above the 4 GB floor. Persistent artifacts: git.
10. **Cleanup:** worktree and local branch removed after acceptance.

## Storage gate confirmation (docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md)

1. Executes in local source-only worktree + GitHub Actions CI.
2. Expected local usage: < 100 MB.
3. Persistent output routed to GitHub.
4. Owner PC stays far inside budget.
5. Cleanup: `git worktree remove` + branch deletion after acceptance.

## Risks acknowledged

- Atomicity: schema, builder declared-version, and tests move in ONE task PR (packet risk 1).
- `age_seconds` uses the M1-T009 injected-clock discipline — no wall-clock in deterministic tests (packet risk 2).

## Verdict

**PASS** — task is ready; backlog → ready.
