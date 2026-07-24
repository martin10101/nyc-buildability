# Startup capsule — M3-T001 (producer tab)

**You are a producer, not the controller.** Do not merge, accept, replan the ledger, change another
task, operate another worktree, read/import an unmerged sibling branch, or modify a shared contract.
Commit and push only your assigned branch; open one PR against main when the complete packet is ready.

- **Task / title:** M3-T001 — Legal-source authority hierarchy, corpus scope, coverage matrix, and internal legal-source manifest contract.
- **Branch:** `task/M3-T001-legal-source-authority` · **Expected worktree:** the sibling folder the controller created for you (path in the owner return).
- **Frozen base SHA:** your worktree's initial `HEAD` (run `git rev-parse HEAD`) — the post-D-002-consolidation `main` SHA in the controller's owner return. Start from it.
- **Read before starting:** (1) root `CLAUDE.md`; (2) your packet `project-control/tasks/M3-T001.json` (source of truth); (3) `project-control/reports/FIRST-WAVE-INTEGRATION-CONTRACT.md`; (4) your applicable D-002 requirements (the 14 PROD ids — `project-control/directives/D-002-activate-control-system-first-wave/requirements.json`); (5) your interface/fixture files under `packages/contracts/schemas/v1/`; (6) your latest `M3-T001-*` resume report if any.
- **Directive refs:** D-002 (regime v1.0; cite `D-002:ALL`).
- **Owned interfaces:** `legal_source_manifest.schema.json@v1` (NEW additive internal manifest; deterministic `$id` + version; not a canonical cross-tier contract). **Consumed read-only from main:** existing `docs/SOURCE_ACCESS_REGISTRY.md` rows (byte-unchanged; additive only), M1 registry.
- **Allowed paths:** the 5 docs (`SOURCE_AUTHORITY_POLICY.md`, `LEGAL_CORPUS_COVERAGE_MATRIX.md`, `CONSTRUCTION_CODE_RELEASE_SCOPE.md`, `DOCUMENT_EVIDENCE_POLICY.md`, additive `SOURCE_ACCESS_REGISTRY.md`), `packages/contracts/schemas/v1/legal_source_manifest.schema.json`, `packages/contracts/schemas/v1/fixtures/legal_source_manifest/**`, and your reports `project-control/reports/M3-T001-*.md`.
- **Forbidden paths:** any `services/api/app/**` runtime; the canonical contracts (property_profile/rule_evaluation/coverage_status/scenario/source_fact/analysis_state_transition); `apps/web/**`; `.claude/**` except your own agent-memory; `project-control/**` except your own reports + the B-011 reference; every reserved hotspot in the contract's §6.
- **Dependencies proven accepted:** M1-T001 (accepted). No first-wave sibling dependency.
- **Required tests / harnesses:** executable JSON-schema validation of the positive + negative `legal_source_manifest` fixtures; the benchmark discrepancy findings.
- **Permitted report path:** `project-control/reports/M3-T001-producer-report.md` (+ `M3-T001-architect-benchmark-analysis.md`).
- **Completion condition:** all outputs produced; G0/G1/G2/G3/G4/G5 evidence in your producer report; one PR against main opened; nothing outside allowed paths changed.
- **Stop conditions (return a ≤200-word blocker):** construction-code scope needs owner/B-011 approval; genuine legal ambiguity; any need to touch runtime or a canonical/shared contract (submit an interface-change request — do not edit the shared contract); credential/payment/security-exception/destructive-op/impossible-acceptance.
- **Final return (≤500 words, ≤8 bullets):** task+outcome; PR link+head; what now works; contract/interface impact; tests+review result; blockers/limitations; exact next dependency unlocked (M3-T002 needs accepted M3-T001); whether you are now idle.
