# M0-T040 G0 readiness (administrative)

**Task:** M0-T040 — Phase 2: authority policy simplification — Tier A/B/C/D, ADR-006, policy tests (AD-006..AD-010)
**Recorded by:** orchestrator. **Date:** 2026-08-07 (UTC).

- Packet complete: objective (Section 5 tier model; ADR-006 superseding the ADR-005 merge posture while
  keeping orchestrator-only CLI/git authority; CLAUDE.md + rules updates; D-004-R721 supersession record;
  G6 engineering-vs-publication split per AD-061..AD-063; deterministic tier tests; PRs 143-146 replay),
  clean-glob allowed paths, executable scenarios AS-1..AS-4, directive_refs D-010:ALL (derived applicable
  set = R006..R010 + R061..R063 = 8 rows), gates G0/G2/G3/G5, four independent reviewers rostered.
- Dependencies: M0-T039 **accepted** (count 58, merged to main at `b1a9186`) — dependency-valid.
- Blockers: none reference M0-T040.
- Inputs available on main: D-010 source-001 Sections 5/6/20 + 0A; docs/adr/ (ADR-005); CLAUDE.md;
  .claude/rules/project-control.md; docs/PROJECT_CONTROL_PROTOCOL.md; docs/GATES_AND_CHECKPOINTS.md;
  merge-queue incident history (PRs 143-146, 2026-08-03).
- Governance-path note: CLAUDE.md and .claude/rules/ are governance paths; the task is governance-type
  and cites D-010 (scope.task_types includes governance) → covers_governance passes.
- Producer: backend-engineer (delegated). Reviewers ≠ producer. Forbidden: tools/project_control.py
  (behavioral CLI changes need a dedicated defect-lane task), tools/agent_supervisor/, .github/workflows/.

**G0 result: PASS (ready to claim).**
