# M5-T010 — G0 Intake (orchestrator)

- **Gate:** G0 (intake / readiness) — **Verdict:** PASS — **Reviewer:** orchestrator
- **Task:** M5-T010 — deterministic scenario COMPARISON/DELTA engine (new contract-free `services/api/app/scenario/comparison.py`) backing the parked Compare (Step 3) UI.

## Readiness
- Bounded scope: new `comparison.py` + additive facade export in `__init__.py` + `test_scenario_comparison.py` + own report = 4 allowed_paths. forbidden_paths lock derive.py/builder/models/constants/contract/ranking.py/sensitivity.py/**_json_safety.py** (import-only, not edited) + the four existing scenario test files (must stay green unchanged) + packages/contracts/** + profile/rules/spatial/api + apps/web + tools + .claude.
- `documented_test_commands` = single clean segment `python -m pytest services/api/tests/scenario` (closed command profile: no `&&`/`cd`/redirection/quoting).
- 7 executable AS: (1) comparison document = per-set derive echo + baseline-relative absolute+percent deltas per numeric metric, canonical cap verbatim; (2) deterministic total stable order (byte-identical across set orders, baseline first); (3) never invents / never Verified / typed not-comparable marker; (4) typed-error + degenerate handling (<2 sets, malformed metric, zero/None baseline → typed markers, no ZeroDivision/NaN/Inf/raise); (5) strict-JSON-safe via the SHARED `_json_safety.py` (no re-duplication); (6) full regression ≥252 + new tests, modularity_check passes; (7) contract-free + offline (stdlib + .derive + .constants + ._json_safety only, socket-blockable).
- Rationale: D-038-R003 positive product deliverable; the natural optimization-engine increment after ranking (M5-T007) + sensitivity (M5-T008); supplies the deterministic side-by-side comparison the committed-but-parked Compare Step-3 UI (M5-T004) needs. Dogfoods the shared `_json_safety.py` extracted in M5-T009.
- Not G6-blocked (no new legal rule; transports the canonical cap verbatim, never Verified); offline (no Supabase/Geoclient); no deferred credentials (D-038-R004 satisfied by construction).
- directive_refs D-038:ALL; appended to R003/R004 applicability; manifest digest resynced (84ab4118 → 2e904ad6) + audit note added; `validate_directive_compliance --check` EXIT=0.
- Gates G0/G1/G3/G4/G5; reviewers code-reviewer/qa-engineer/security-reviewer (all ≠ producer scenario-optimization-engineer).

Ready to claim and dispatch to the build loop.
