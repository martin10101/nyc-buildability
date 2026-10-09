# M5-T008 — G0 Intake (orchestrator)

- **Gate:** G0 (intake / readiness)
- **Verdict:** PASS
- **Reviewer:** orchestrator
- **Task:** M5-T008 — deterministic single-assumption sensitivity/what-if analysis (contract-free; consumes derive.py READ-ONLY).

## Readiness checks
- Scope is tightly bounded and product (M5 optimization-engine depth): new module `services/api/app/scenario/sensitivity.py` + its `__init__.py` export + `test_scenario_sensitivity.py` + own producer report — 4 allowed_paths only; forbidden_paths lock builder/models/constants/contract/derive/ranking + packages/contracts/** + api/web/tools.
- `documented_test_commands` = single clean segment `python -m pytest services/api/tests/scenario` (closed command profile, M0-T149).
- 7 executable acceptance scenarios AS-1..AS-7 (determinism, named-variable transparency, explicit-only/never-fabricate, fail-closed strict-JSON-safe, never-Verified, read-only/no-recompute, contract-free/offline/full-regression).
- Not G6-blocked: deterministic illustrative math over explicit assumptions, no new legal rule; offline (no Supabase/Geoclient/network), no deferred credentials.
- directive_refs D-038:ALL; M5-T008 appended to D-038 R003/R004 applicability; manifest requirements digest resynced; `validate_directive_compliance --check` EXIT=0.
- Required gates G0/G1/G3/G4/G5; reviewer roster code-reviewer/qa-engineer/security-reviewer (all ≠ producer scenario-optimization-engineer).

Ready to claim and dispatch.
