# M5-T009 — G0 Intake (orchestrator)

- **Gate:** G0 (intake / readiness) — **Verdict:** PASS — **Reviewer:** orchestrator
- **Task:** M5-T009 — behavior-neutral extraction of the duplicated strict-JSON-safety sanitizer (ranking.py + sensitivity.py → shared `services/api/app/scenario/_json_safety.py`) + closing the G5 L1 (deepcopy) / L2 (cycle/depth) defense-in-depth gaps.

## Readiness
- Bounded scope: new `_json_safety.py` + the 2 consumers (ranking.py, sensitivity.py) + `test_json_safety.py` + own report = 5 allowed_paths. forbidden_paths lock derive.py/builder/models/constants/contract/**__init__.py** + the two existing test files (test_scenario_ranking.py, test_scenario_sensitivity.py must pass UNCHANGED) + packages/contracts/** + api/web/tools.
- `documented_test_commands` = single clean segment `python -m pytest services/api/tests/scenario`.
- 7 executable AS: behavior-neutral byte-identity (existing 49+49 tests pass unchanged), single-source-of-truth de-dup, L1 deepcopy guard, L2 cycle/depth guard, determinism+fail-closed preserved, full regression + modularity (net SLOC reduction), contract-free/offline.
- Rationale: permanent modularity law (CLAUDE.md #16 — consolidate before growing) + explicit G1/G5 reviewer recommendation on M5-T007/T008 (sanitizer duplication flagged, L1/L2 LOWs routed to a shared-sanitizer decomposition). Doing it at 2 consumers is cleaner than after a 3rd/4th feature module re-duplicates it.
- Not G6-blocked (no legal rule); offline (no Supabase/Geoclient); no deferred credentials.
- directive_refs D-038:ALL; appended to R003/R004 applicability; manifest digest resynced (84ab4118) + audit note added; `validate_directive_compliance --check` EXIT=0.
- Gates G0/G1/G3/G4/G5; reviewers code-reviewer/qa-engineer/security-reviewer (all ≠ producer).

Ready to claim and dispatch.
