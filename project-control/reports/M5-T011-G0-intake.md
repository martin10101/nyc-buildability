# M5-T011 — G0 Intake (orchestrator)

- **Gate:** G0 (intake / readiness) — **Verdict:** PASS — **Reviewer:** orchestrator
- **Task:** M5-T011 — deterministic scenario BREAK-EVEN / THRESHOLD finder (new contract-free `services/api/app/scenario/breakeven.py`) completing the offline optimization toolkit.

## Readiness
- Bounded scope: new `breakeven.py` + additive facade export in `__init__.py` + `test_scenario_breakeven.py` + own report = 4 allowed_paths. forbidden_paths lock derive/builder/models/constants/contract/ranking/sensitivity/**comparison.py**/**_json_safety.py** (import-only, not edited) + the five existing scenario test files (must stay green unchanged) + packages/contracts/** + profile/rules/spatial/api + apps/web + tools + .claude.
- `documented_test_commands` = single clean segment `python -m pytest services/api/tests/scenario` (closed command profile).
- 7 executable AS: (1) threshold result = per-candidate derive echo + first crossing as an HONEST grid bracket (lower/upper values + metrics + direction), cap verbatim; (2) deterministic total stable order; (3) never invents / never Verified / no interpolated invented crossing; (4) monotonicity-honest + degenerate (already-met / no-crossing-in-domain / non-monotonic flag / unknown var / bad target / empty domain / not-derivable → typed markers, no raise/ZeroDivision/NaN/Inf); (5) strict-JSON-safe via the SHARED `_json_safety.py`; (6) full regression ≥323 + new tests, modularity passes; (7) contract-free + offline.
- Rationale: D-038-R003 product deliverable completing the optimization toolkit (derive → sensitivity → ranking → comparison → break-even/threshold). A concrete analyst query ("minimum X to reach target Y"). Consumes accepted derive.py READ-ONLY; dogfoods shared `_json_safety.py`.
- Design guard (honesty): report the explicit grid bracket, do NOT present an interpolated sub-grid crossing as a derived fact; do NOT assume monotonicity (flag multiple crossings). This is the key correctness boundary reviewers must probe.
- Not G6-blocked (no new legal rule; cap verbatim, never Verified); offline (no Supabase/Geoclient); no deferred credentials (D-038-R004 by construction).
- directive_refs D-038:ALL; appended to R003/R004 applicability; manifest digest resynced (2e904ad6 → 37035a7d) + audit note added; `validate_directive_compliance --check` EXIT 0.
- Gates G0/G1/G3/G4/G5; reviewers code-reviewer/qa-engineer/security-reviewer (all ≠ producer scenario-optimization-engineer).

Ready to claim and dispatch to the build loop.
