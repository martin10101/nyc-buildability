# M5-T001 — G0 definition-of-ready (administrative)

**Task:** M5-T001 — deterministic coverage-aware scenario foundation (consume canonical draft
zoning-floor-area cap; no independent legal calc; no envelope inference).
**Reviewer:** orchestrator (administrative G0). **Result:** PASS (ready to claim).

## Readiness checklist (per `/start-controlled-task`)
- **Requirement identifiers named:** PRD §7.2, §9, §12, §13/§13.1–§13.4;
  `docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md`; `docs/ACCEPTANCE_SCENARIO_STANDARD.md`. ✓
- **Exact evidence files named (read-only):** `property_profile.schema.json` (1.4.0),
  `rule_evaluation.schema.json` (1.0.0), `coverage_status.schema.json`,
  `rules/rulesets/r5_residential_far.rule.json`,
  `fixtures/valid/rule_evaluation/supported_family_draft.json`, and the authoritative spec
  `project-control/reports/M5-T001-DRAFT-PROPOSAL.md`. ✓
- **Non-overlapping write scope:** allowed `services/api/app/scenario/**`,
  `services/api/tests/scenario/**`, new additive `packages/contracts/schemas/v1/scenario.schema.json`
  (+ generated/fixtures), own producer report. Forbidden: profile/spatial/rule engines, existing
  canonical contracts, `api/v1/**`, `apps/web/**`, 3D/UI, other ledger paths. No concurrent task
  shares these production/schema paths. ✓
- **Acceptance scenarios:** AS-1..AS-12 (primary confident cap, unsupported, missing, spatial
  uncertainty, rule conflict, malformed/non-finite, integrity-disagreement fail-closed, deterministic
  ordering, never-Verified, provenance+completeness, explicit-assumption-only variation, regression). ✓
- **Required gates + independent reviewers:** G0 (admin); G1 data-contract-verifier; G3 code-reviewer;
  G4 qa-engineer; G5 security-reviewer — all distinct from producer `scenario-optimization-engineer`. ✓
- **Dependencies exist:** M4-T005, M4-T002 (merged draft), M2-T012, M2-T013 (accepted). M5 engineering
  authorized against merged draft/needs_review M4 without treating M4 accepted; final acceptance
  remains gated on genuine G6 legal approval of M4-T001 (dependency-accepted precondition) — not
  weakened; B-010 is not a blocker here. ✓
- **Control-model check:** `new-task` accepted M5-T001 against unaccepted-but-merged M4 dependencies
  (dependency-*acceptance* is enforced only on `accept`, precondition #4). No stop-condition triggered. ✓
- **CP-0032 not used; UI/3D excluded from this slice.** ✓

Ready to claim.
