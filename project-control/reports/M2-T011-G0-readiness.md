# G0 Definition-of-Ready — M2-T011 (orchestrator, administrative)

**Task:** Shared connector transport/retry consolidation + canonical source access registry
**Reviewer:** orchestrator (administrative) · **Result:** PASS · **Date:** 2026-07-20

G0 readiness confirmed before dispatch (owner-approved next wave, 2026-07-20):

1. **Objective unambiguous** — packet `project-control/tasks/M2-T011.json`: (1) extract the duplicated transport+retry loop from the four accepted connectors into one shared module preserving all accepted resilience behavior (null hypothesis = behavior unchanged); (2) create `docs/SOURCE_ACCESS_REGISTRY.md` with the owner-mandated per-source fields.
2. **Dependencies** — M2-T009 accepted; all four target connectors accepted and merged. No unmet dependency.
3. **File scope exclusive & disjoint** — allowed paths (connectors, resilience, their tests, docs registry, own report) proven disjoint from the parallel M2-T010 task (packages/contracts, apps/web/src/lib, profile/contract.py docstring, services/api/tests/api). Disjointness recorded in the 2026-07-20 planning control PR (#49). Parallel dispatch authorized.
4. **Inputs/outputs defined** — accepted connector modules, resilience primitives, committed fixture packs, source-registry research drafts. Outputs: shared transport module, registry, tests, producer report.
5. **Acceptance scenarios exist** — TC-S1..TC-S8 in the packet (behavior-unchanged, consolidation proof, resilience-semantics regression, connector-specific semantics, registry completeness, registry verification, fault matrix, CI regression).
6. **Required gates assigned** — G0, G1 (data-contract-verifier), G2 (producer self-check), G3/G4 (code-reviewer), G5 (security-reviewer). Producer ≠ any independent reviewer.
7. **Execution location & disk** — local checkout + GitHub Actions CI; source-only edits; committed fixtures reused; negligible disk footprint; low-storage policy honored (no datasets, no local DB, no bulk downloads).
8. **Cleanup/storage routing** — no durable artifacts on the owner PC; all persistent output is source in Git.

Ready-to-start criteria met. Task dispatched to backend-engineer in isolated worktree.
