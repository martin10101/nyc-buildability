# M5-T005 — G0 intake gate (contracting)

**Result: PASS** (orchestrator intake). Task ready for claim + autonomous build.

## Scope is well-formed and bounded
- **Deliverable:** a pure, deterministic, OFFLINE service function `derive.py` that derives an
  illustrative practical-usable-range (min/point/max) from a preliminary scenario document + its
  explicitly-declared typed assumptions — **contract-free** (new module + `__init__.py` export only),
  never mutating/recomputing the canonical `draft_zoning_floor_area_cap_sq_ft`, never inferring a
  missing envelope constraint, never emitting `verified`.
- **allowed_paths** (4, exact files — narrow, no `**` that would expose read-only templates):
  `services/api/app/scenario/derive.py`, `.../scenario/__init__.py`,
  `services/api/tests/scenario/test_scenario_derive.py`, own producer report.
- **forbidden_paths** lock the read-only consume surface: `builder.py/models.py/constants.py/contract.py`,
  `packages/contracts/**`, profile/rules/spatial/api, `apps/web/**`, `tools/**`.
- **acceptance_scenarios:** AS-1..AS-7 (raw-cap passthrough / explicit-factor derivation / fail-closed
  on bad factors / no-cap document / determinism / never-Verified honesty / contract-free+offline).
- **documented_test_commands:** `python -m pytest services/api/tests/scenario` — verified to run clean
  from repo root (54 existing scenario tests pass, 0.34s), closed command-profile compliant (single
  segment, no `&&`/`cd`/redirection/quoting).
- **required_gates:** G0,G1,G3,G4,G5 (backend deterministic; no G6 — no new legal rule; no frontend gates).
- **reviewer_agents:** code-reviewer, qa-engineer, security-reviewer (independent; producer =
  scenario-optimization-engineer).

## Policy compliance
- **D-038-R003** (product engineering, scenario/optimization increment) and **D-038-R004**
  (no Supabase/Geoclient — offline fixtures/public-connector only) — M5-T005 appended to both
  requirements' applicability per R003's contracted-tasks mechanism; directive registry validates OK.
- **Acceptance is NOT G6-blocked** (pure derived math over explicit assumptions, no legal interpretation),
  unlike the M5-T001 foundation — this is the acceptable no-creds backend work the owner chose 2026-09-08
  while M5-T004 UI acceptance is parked.
- AI-boundary discipline (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md): deterministic code calculates; the
  canonical cap is transported verbatim and never replaced; no hidden utilization/optimization default;
  explicit typed assumptions only; needs_review + not_verified_disclaimer preserved.
