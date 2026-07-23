# M4-T006 — G0 definition-of-ready (administrative)

**Task:** M4-T006 — R5 residential height & setback vertical-envelope draft rule family (per-district;
separate typed constraints; fail-closed).
**Reviewer:** orchestrator (administrative G0). **Result:** PASS (ready to claim).

## Readiness checklist (per `/start-controlled-task`)
- **Requirement identifiers named:** `M4-T006-DRAFT-PROPOSAL.md` (owner-amended §3–§7, §11); PRD §7.2/§9/§12/§13.3; `docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md`; `docs/ACCEPTANCE_SCENARIO_STANDARD.md`; the current official NYC ZR R5-series height/setback sections (producer to identify + verify). ✓
- **Exact evidence files named:** M4-T001 engine/DSL, `r5_residential_far.rule.json` (pattern, read-only), `_zr_snapshots/v1` + `sync_zr_snapshots` mechanism, `property_profile.schema.json` (1.4.0) canonical paths, `rule_evaluation.schema.json` (open outputs). ✓
- **Non-overlapping write scope:** allowed = new ruleset(s), additive DSL schema (if needed), new ZR snapshots, `tests/rules/**`, own reports. Forbidden = evaluator core, the FAR rule, profile/spatial/scenario/api, canonical contracts, apps/web, 3D/UI, yards/lot-coverage/parking. No concurrent task shares these production/schema paths. ✓
- **Acceptance scenarios:** AS-1..AS-6 (per-district confident, provenance fidelity, effective-date boundary, determinism, never-Verified, installed-wheel deployability) + NC-1..NC-7 negative controls (district variant, street-width class, special-district/overlay, building/ground-floor, missing, contradictory, mutually-exclusive rules). ✓
- **Required gates + independent reviewers:** G0 (admin); G2 (self-check, orchestrator-recorded); G3 code-reviewer; G4 qa-engineer; G5 security-reviewer — all distinct from producer `rules-engineer`. **G6** (qualified-human legal) noted as the publication/acceptance boundary — not part of this build, not weakened. ✓
- **Dependency exists:** M4-T001 (merged; awaiting_gate/needs_review). Engineering authorized against needs_review rules (owner directive 2026-07-21); final acceptance gated on genuine G6. ✓
- **Legal-scope guardrails present:** AI extracts / human decides at G6; current-effective-regime-only (no remembered pre-amendment values); genuine-ambiguity STOP→blocker; no invented dimensions; no publish/Verify. ✓
- **CP-0032 not used; no 3D/UI; no hold release; does not wait on B-010.** ✓

Ready to claim.
