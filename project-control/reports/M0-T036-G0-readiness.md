# M0-T036 — G0 readiness (administrative, orchestrator)

**Task:** D-007 Supervisor Bridge build (Phases 1–5).
**Recorded at:** 2026-08-03, on the dispatch-capture branch (owner dispatch captured as D-007
amendment 1, rows R532–R541, PR #150 queued; build proceeds on the pushed capture per the
established repository-reproducibility practice).

## Readiness checks

1. **Authority.** Owner dispatch of 2026-08-03 (D-007-R540): "M0-T036 is dispatched. Execute
   Phases 1 through 5 … Build it." Phase-boundary and mode prohibitions live (R541: Phase 5 stops
   at the activation decision; limited-auto never enabled). R721 unchanged.
2. **Decisions closed at dispatch:** ADR-005 amendment adopted and noted in the ADR (R532);
   anchoring Option A (R533); controller location = dedicated read-only checkout (R534); probes
   first (R535); standing grants (a)/(b) ACTIVE on the packet (R536/R537).
3. **Packet completeness:** exact allowed/forbidden paths (tools/agent_supervisor/** + tests +
   report + packet), 8 acceptance scenarios, 5 gates (G0/G2/G3/G4/G5), 5 reviewers, every §18
   stop condition, risks incl. split-at-orchestrator-discretion.
4. **Inputs exist at head:** D-007 source-001.md (+ amendment 1); the Phase 0 return
   (M0-T036-PHASE0-return.md) with verified CLI capabilities and the CLI-adapter decision;
   the M0-T028 capsule; ADR-005 with the adopted amendment note.
5. **In-regime:** D-007:ALL, 507 applicable rows at contract + amendment (resolver-derived);
   placeholder verification block present; validator exit 0.
6. **No conflicts:** no open blocker touches the scope; tools/agent_supervisor/ does not exist
   yet (created only by the claimed producer in its worktree); dependency M0-T027 accepted.

**G0: PASS (administrative readiness; not independent review).**
