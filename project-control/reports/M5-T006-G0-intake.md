# M5-T006 — G0 intake gate (contracting)

**Result: PASS** (orchestrator intake). Task ready for claim + autonomous build.

## Scope
- **Deliverable:** a fast-follow hardening of the accepted `services/api/app/scenario/derive.py` closing the three G5 LOW findings from the M5-T005 security review — additive, deterministic, offline, contract-free:
  - **LOW-1** strict-JSON-safe malformed-cap transport (finite-guard `canonical_cap_sq_ft` on the fail-closed outcomes; add a strict-JSON-safety test).
  - **LOW-2** no-alias assumption copy (deepcopy value/unit/rationale) + correct the over-claiming docstring.
  - **LOW-3** bounded raw-input echo in reason strings.
- **allowed_paths** (3, exact): `derive.py`, `tests/scenario/test_scenario_derive.py`, own report. `__init__.py` is in **forbidden_paths** (no export change needed).
- **acceptance_scenarios:** AS-1..AS-6 (strict-JSON-safe malformed cap / DERIVED-path unchanged / no-alias / bounded echo / cap-value + never-Verified preserved / determinism + full regression).
- **documented_test_commands:** `python -m pytest services/api/tests/scenario` (closed-profile clean; verified lane 102 tests green).
- **required_gates:** G0,G1,G3,G4,G5; **reviewers:** code-reviewer, qa-engineer, security-reviewer (independent; producer = scenario-optimization-engineer).

## Policy
- **D-038-R003 + R004** applicable (M5-T006 appended per R003's contracted-tasks mechanism; registry validates OK). Depends on the accepted M5-T005.
- Not G6-blocked (no new legal rule); the canonical cap VALUE is never recomputed/relabelled (only its fail-closed transport is finite-guarded); never emits Verified. Closes real review findings before more optimization work builds on derive.py.
