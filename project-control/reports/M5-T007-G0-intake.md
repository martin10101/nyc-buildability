# M5-T007 — G0 intake gate (contracting)

**Result: PASS** (orchestrator intake). Task ready for claim + autonomous build.

## Scope
- **Deliverable:** a pure, deterministic, OFFLINE `ranking.py` that ranks EXPLICIT caller-provided assumption-sets for one scenario document (each run through the accepted `derive_practical_usable_range`) and returns an ORDERED, scored candidate list for the Compare UI's "ranked cards + score breakdown." Named objective (explicit input), stable total tie-break, transparent score components; never invents scenarios/alternatives; never up-labels beyond conditional; never Verified; fail-closed + strict-JSON-safe; contract-free.
- **allowed_paths** (4, exact): `ranking.py` (new), `__init__.py` (export), `tests/scenario/test_scenario_ranking.py` (new), own report. `derive.py`, `builder/models/constants/contract`, `packages/contracts/**` are forbidden (consume derive.py READ-ONLY; the objective enum lives in ranking.py to stay contract-free).
- **acceptance_scenarios:** AS-1..AS-7 (stable ordering / named-objective breakdown / explicit-only never-fabricate / fail-closed / never-Verified / read-only no-legal-recompute / contract-free+offline+regression).
- **documented_test_commands:** `python -m pytest services/api/tests/scenario` (closed-profile; verified lane 124 tests green).
- **required_gates:** G0,G1,G3,G4,G5; **reviewers:** code/qa/security; **producer:** scenario-optimization-engineer.

## Policy
- **D-038-R003 + R004** applicable (M5-T007 appended per R003's contracted-tasks mechanism; registry resynced e6111fbf). Depends on the accepted M5-T006 (and via it M5-T005 derive.py).
- Not G6-blocked (deterministic illustrative math over explicit assumptions; no new legal rule; the canonical cap is transported verbatim, never recomputed; never Verified). AI-boundary: never show "best" without naming the objective; never invent alternatives; scores illustrative from the draft cap only. The next substantial no-creds backend feature under the owner's 2026-09-08 "keep building offline" directive; feeds the parked Compare UI's empty score breakdown.
