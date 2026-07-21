# M2-T012 — G0 Readiness

**Task:** M2-T012 Profile integration of wave connectors + spatial results (single contract 1.4.0 update)
**Recorded by:** orchestrator (lead session) · **Date:** 2026-07-21
**Branch:** `task/M2-T012-profile` · **Worktree:** `.claude/worktrees/M2-T012-profile` · **Base:** `6f9d603` (origin/main; includes accepted M2-T013)

## Objective (narrow)
Integrate, in ONE coordinated contract **1.4.0** update via the accepted M2-T010 tooling:
(1) zoning-features citywide facts (M2-T007) + per-BBL MapPLUTO geometry facts (M2-T009) into the canonical profile with full provenance;
(2) the accepted **M2-T013** spatial-intersection records (exact geometry results, boundary distances, uncertainty classes, split-lot share ranges, professional-review flags) into the profile **without collapsing uncertainty**;
(3) extend the PLUTO/ZTLDB/zoning-features cross-check to include the geometric assignment as a fourth evidence stream (disagreements surface through the existing conflict shape);
(4) publish 1.4.0 through the M2-T010 derivation (client + backend declarations derive automatically; drift tests prove detection);
(5) fold in the enumerated carried LOW-defect fixes/options.

## Readiness checklist
- **Dependencies:** M2-T010 ✅, M2-T011 ✅, **M2-T013 ✅ (accepted + merged at 6f9d603)** — all accepted. Consumes M2-T013 output `app/spatial/` (LotIntersectionRecord etc.) read-only.
- **File scope (exclusive):** `services/api/app/profile/**`, `packages/contracts/**` (1.4.0 via M2-T010 tooling), `services/api/app/_contract_schemas/**` (via sync tooling only), `apps/web/src/lib/**` (derived declarations), tests; connector/resilience touches ONLY for the enumerated carried defects (each disclosed). Disjoint from any other active task.
- **Constraint:** additive-only contract evolution; 1.0.0–1.3.0 payloads must continue to validate; NO uncertainty-collapsing simplification; NO 1.5.0.
- **Acceptance scenarios:** PI-S1..PI-S8 (packet) — primary, uncertainty-preservation, conflict, back-compat, drift tooling, carried defects, missing-data, regression.
- **Required gates:** G0, G1, G2, G3, G4, G5 — reviewers data-contract-verifier, code-reviewer, security-reviewer (all ≠ producer). Dispatched once, at a frozen candidate, with tight ≤50k packets.
- **Execution:** local checkout + CI; negligible disk footprint. No large/persistent local artifacts.

## STOP conditions
Any non-additive schema need; any uncertainty-collapsing request; any 1.5.0 temptation; credentials; production deployment.

**G0 verdict:** PASS (readiness). Implementation begins lead-only per owner directive 2026-07-21.
