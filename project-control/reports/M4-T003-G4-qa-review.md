# M4-T003 — G4 qa-engineer verbatim return (frozen SHA 0e928b5)

VERDICT: PASS (no defects; non-blocking test additions G-1..G-6; limitations L-1 overlapping windows, L-2 malformed as_of_date fails open)

---

# Gate Report

- **Gate ID:** M4-T003-G4 (integration & regression)
- **Task ID:** M4-T003 — Rules-engine correctness hardening
- **Reviewer:** qa-engineer (independent; read-only)
- **Producer:** orchestrator (lead-only, rules-engineer role)
- **Result: PASS**
- **Clean worktree:** frozen `.claude/worktrees/M4-T003-hardening` @ `0e928b5` (branch task/M4-T003-hardening; base main f2939d6). git clean (only gitignored __pycache__). Scratch tests ran from scratchpad via sys.path; repo not modified.

## Steps independently executed
| Command | Expected | Observed |
|---|---|---|
| pytest tests/rules/test_rules_engine_hardening.py -v | 20 | 20 passed (RH-S1..S8) |
| pytest tests/rules/test_rules_engine.py -q | 36, no regression | 36 passed |
| pytest -q (full api) | 646 | 646 passed in 14.27s |
| ruff check app tests | clean | All checks passed! |
Plus white-box read of evaluator/dsl/models/registry/coverage/lifecycle/snapshots + both schemas + R5 rule + 3 fixtures; 20-check gap probe + 2 targeted probes (scratchpad only).

## Owner-finding -> proof mapping (all GENUINE, no overstatement)
- negative numeric -> bad value: RH-S1 GENUINE (outputs=={}, PRR, missing_critical, invalid_inputs=[lot_area_sq_ft]; valid still computes 15000).
- NaN/inf: RH-S2 GENUINE (PRR + outputs=={} + strict-JSON export; non-finite fail-closed trace also schema-valid, probe I).
- wrong type / invalid enum; non-R5 still not_applicable: RH-S3 GENUINE (R7 -> not_applicable, input_validation.valid=True — real M4-T001/M4-T002 regression guard).
- misspelled predicate/determination ref: RH-S4 GENUINE (all three raise DSLError at LOAD).
- trace release status: RH-S5 GENUINE (needs_review, verified_eligible=False, pending, deterministic_tests=declared).
- effective-date before/after (the named gap): RH-S6 GENUINE — real 2-version transition incl. half-open boundary 2024-01-01; out-of-window -> not_applicable in_effect=False; effective_rules flips v1->v2. Production R5 effective_from=2024-12-05 actually gates (as_of 2020 -> not_applicable, probe D1).
- genuine applies+fails (the named gap): RH-S7 GENUINE — 20000>15000 real numeric fail, coverage stays conditional (probe K).
- determinism/nothing verified/schema-valid: RH-S8 GENUINE.

Overstatement check (owner's core concern): NONE found. Materially stronger than the criticized prior M4-T001 review; the two named gaps genuinely closed.

## Defects: NONE. Required rework: NONE blocking acceptance.

## Recommended (non-blocking) — test-completeness; behavior verified correct via probes
- G-1 (before G6): determination INDETERMINATE branch untested (_evaluate_determination returns None on non-finite/missing operand). Verified correct (probe G).
- G-2 (before G6): compliance PROPOSAL input invalid untested (-5000/inf -> PRR, outputs=={}, determination None, strict-JSON; probe F).
- G-3: exact exclusive_minimum=0 boundary untested (0 correctly rejected "not greater than exclusive_minimum 0", probe A).
- G-4: integer-type validation branch dead-untested (no integer input in repo; 5 valid, 5.5 rejected, 0 below-min; probe E). maximum/exclusive_maximum also unexercised.
- G-5: add assert that the non-finite fail-closed trace is schema-valid to RH-S2 (probe I).
- G-6: bool-as-number (lot_area_sq_ft=True) rejected as non-numeric (probe B); untested.

## Limitations to surface (design, not defects)
- L-1: overlapping effective windows NOT guarded. registry.effective_rules() returns BOTH versions for overlapping windows (['ovl-a','ovl-b'], probe H); no load-time cross-rule overlap detection, no test. Docstring assigns to caller; evaluate() gates per-rule (no silent mis-eval today; no consumer yet). Recommend a load-time cross-rule overlap check OR a contract test asserting the documented >1 behavior.
- L-2: malformed as_of_date fails OPEN. as_of_date="not-a-date" lexicographically compared -> treated in-effect (conditional). as_of_date is a trusted internal param and is NOT format-validated (rule effective_from/to ARE schema-validated; zero-width/inverted windows ARE rejected at load). Recommend fail-closed ISO-format validation of as_of_date.

Scratch evidence: scratchpad/gap_probe.py (scratchpad only).

VERDICT: PASS — 20/36/646/ruff clean reproduced; all seven owner findings genuinely fixed, no overstatement, no defects. G-1/G-2 before G6/publication; G-3..G-6 + L-1/L-2 strengthening for orchestrator to schedule.
