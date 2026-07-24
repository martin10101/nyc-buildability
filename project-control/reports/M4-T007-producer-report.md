# M4-T007 producer report — Exact Decimal/legal-units arithmetic and rounding foundation (DF-2)

**Task:** M4-T007 · **Branch:** `task/M4-T007-decimal-legal-arithmetic` · **Frozen base:**
`cc142081336f2dac0854a947694fec33559dcc8a` (post-D-002-consolidation `main`).
**Directive:** D-002 (regime v1.0; `D-002:ALL`). **Blocker addressed:** B-014 / defect DF-2.
**Role:** producer — this file is producer evidence submitted for an INDEPENDENT gate; it does not
accept the task, merge, or change the ledger. No subagents were dispatched (D-002-R003).

---

## 1. What the task required (and where it landed)

Replace binary-float legal math in the rule-evaluation core with exact Decimal/rational computed from
canonical decimal strings; enforce per-rule rounding mode/scale/order and unit consistency; keep
geometry floats isolated behind explicit typed conversions; add property-based, differential, and
adversarial exact-threshold/rounding tests; keep every existing rules test green (no rule-content /
legal-semantics change — G6 territory, out of scope).

Files changed (all inside the allowed scope; no forbidden path touched):

| File | Change |
|---|---|
| `services/api/app/rules/units.py` | **NEW** frozen-interface foundation: exact canonical-decimal construction, per-rule rounding modes, JSON-number boundary, dimensional-unit enforcement. |
| `services/api/app/rules/operations.py` | Rewrote `COMPUTE_OPS` to compute in exact `Fraction`; removed the float `_q`/`_QUANT` determinism-rounding; exact `round` op (documented mode + scale); exact `compare` predicate. |
| `services/api/app/rules/evaluator.py` | Exact step-to-step chaining; float-representability overflow guard; exact compliance determination; unknown-unit fail-closed guard; removed dead `_is_finite_number`. |
| `services/api/tests/rules/test_units_exact.py` | **NEW** 38 tests: units.py foundation. |
| `services/api/tests/rules/test_decimal_legal_arithmetic.py` | **NEW** 26 tests: AS-1..AS-4 engine-level exact math + geometry isolation. |
| `project-control/reports/M4-T007-producer-report.md` | this report. |

No change to `rulesets/**`, the rule DSL schema, `dsl.py`/`lifecycle.py`/`registry.py`/`integration.py`,
canonical contracts, entrypoints, or any lockfile. The engine uses **only the Python standard library**
(`fractions`, `decimal`, `math`, `sys`, `dataclasses`) — no dependency added, so no lockfile/pyproject
edit and no dependency-security admission is needed (First-Wave Contract: "Decimal is stdlib").

## 2. Design (how the exactness guarantee is constructed)

- **Exact rational, not raw Decimal.** The internal legal number type is `fractions.Fraction`, closed
  under `+ − × ÷` for rational inputs — no rounding ever, until a rule explicitly asks. (`Decimal`
  division rounds to a context precision and could still mis-compare at a boundary.)
- **Canonical decimal strings.** `units.to_exact` builds a value from its canonical decimal string, so a
  JSON/float `0.1` becomes exactly `Fraction(1, 10)` — never `Fraction(0.1)` (binary noise). Rejects
  `bool`, `None`, non-finite, malformed strings, unsupported types (fail closed).
- **Comparisons are exact.** The compliance determination, the `compare` predicate, and
  `min`/`max`/`clamp` selection all operate on exact rationals, so an equality/threshold at an exact
  legal boundary (e.g. `0.1 + 0.2 == 0.3`, `0.3 / 0.1 == 3`) resolves deterministically. This is the
  core of B-014 ("compares legal thresholds in binary float").
- **Per-rule rounding is explicit (mode + scale + order).** Intermediates stay exact; rounding happens
  only where a rule places a `round` step, at that step's declared scale (`ndigits`), under a documented
  mode (`DEFAULT_LEGAL_ROUNDING = ROUND_HALF_UP`, round-half-away-from-zero, computed exactly on the
  rational). Order = the explicit step order; the old implicit round-to-10 (`_q`) is gone.
- **Geometry-float isolation.** `units.to_exact` is the single explicit typed conversion from a raw
  (possibly shapely-derived) float onto the legal path. Nothing on the value path consumes a geometry
  float without it.
- **JSON boundary.** Traces render exact values to finite JSON numbers via `units.to_json_number` at the
  trace edge only (schema/`json.dumps(allow_nan=False)` require numbers). This render is the only place a
  legal value meets a float and it feeds NO legal decision. `int` inputs pass through as `int`
  (preserving e.g. `resolved_args == [10000, 1.5]`); Fractions render to `float`.
- **Overflow fails closed.** An exact result can be finite yet too large for a finite JSON number
  (`1.2e308 × 1.5 = 1.8e308`); the representability guard fails closed (professional_review_required, no
  value) rather than emit `inf`.
- **Unit enforcement.** `require_known_unit` rejects an unknown unit; the evaluator fails closed if any
  declared input/output unit is unknown. `Quantity` gives exact unit-aware arithmetic that rejects
  incompatible dimensions (`feet + square_feet`) and cross-unit comparisons.

## 3. Acceptance-scenario evidence (AS-1 … AS-6)

| AS | Evidence |
|---|---|
| **AS-1** no binary-float on the legal value path | `grep 'float(' operations.py` → **none**. `test_as1_every_compute_op_returns_an_exact_fraction`, `test_as1_operations_module_has_no_float_calls_on_value_path`, `test_as1_evaluator_determination_and_computation_use_exact_not_float` (AST scan), `test_as1_run_computation_keeps_outputs_exact`. The only `float(value)` in `evaluator.py` is the input-ADMISSION overflow gate (`_invalid_reason`), not arithmetic. |
| **AS-2** adversarial exact-threshold | `test_as2_addition_equality_at_float_trap_resolves_exactly` (`0.1+0.2==0.3` → pass; float trap asserted), `test_as2_le_boundary_a_naive_float_engine_would_flip`, `test_as2_division_equality_at_float_trap_resolves_exactly` (`0.3/0.1==3`), `test_as2_subtraction_is_exact`, `test_as2_min_max_clamp_select_exactly_at_a_tie`, `test_as2_compliance_at_exact_computed_cap_is_inclusive_pass`, `test_as2_exact_trace_is_json_safe`. |
| **AS-3** differential + property | `test_as3_differential_native_vs_independent_exact_recompute` (400 seeded cases, native evaluator == independent exact recompute), `test_as3_property_floor_area_scales_linearly_with_lot_area` (100 seeded cases; linearity + FAR-cap invariance + monotonicity), `test_as3_far_cap_constant_across_areas`. |
| **AS-4** rounding mode/scale/order + unit enforcement + fail-closed | `test_as4_round_op_uses_documented_half_up_mode`, `test_as4_rounding_order_intermediates_stay_exact_until_an_explicit_round`, `test_as4_round_rejects_non_integer_ndigits`, `test_as4_unknown_unit_fails_closed_no_value`, `test_as4_known_units_are_accepted`, `test_as4_division_by_zero_fails_closed_without_a_value`, `test_as4_non_finite_numeric_input_fails_closed`, `test_as4_overflow_output_representability_fails_closed`; plus `test_units_exact.py` (38 tests). |
| **AS-5** existing rules tests still pass | Baseline `227 passed` → after change `291 passed` (227 unchanged + 64 new). Whole `services/api` suite `992 passed`. No rule-content/legal-semantics change; outputs render identically for existing rules. |
| **AS-6** G0/G2/G3/G4/G5 evidence | this report, §4. |

## 4. Gate evidence

- **G0 (definition-of-ready):** scope, allowed/forbidden paths, and executable acceptance scenarios
  fixed by `project-control/tasks/M4-T007.json` and `M4-T007-CAPSULE.md`; work stayed in scope.
- **G2 (producer self-check) — commands + outputs (working-dir `services/api`):**
  - `python -m pytest tests/rules -q` → **291 passed**
  - `python -m pytest tests/ -q` → **992 passed** (whole API suite; downstream consumers of the engine — `tests/api/test_rule_evaluation_api.py`, `tests/scenario`, `tests/profile`, `tests/contracts` — unaffected)
  - `python -m ruff check .` → **All checks passed!**
  - AS-1 no-float scan: `grep -n 'float(' app/rules/operations.py` → none.
  G2 permits submission only; it does not accept the task.
- **G3 (independent walkthrough) — evidence map for the reviewer:** exact-math design §2; no
  legal-semantics change (rulesets untouched); back-compat proven by the unchanged 227 prior tests. Reviewer must be a different identity than this producer.
- **G4 (integration & regression):** full offline suite green (992) at frozen base; determinism/byte-identical-trace tests (`test_rh_s8_determinism…`, `test_rules_fh4_temporal_parity`) pass; CI runs `ruff check .` + `pytest -q` in `services/api` (no dependency change).
- **G5 (security & privacy):** pure offline arithmetic; no secrets, network, auth, storage, or user input surface; fail-closed on malformed/non-finite/overflow/unknown-unit inputs (no fabricated value); traces stay strict JSON (`allow_nan=False`).
- **G6 is explicitly NOT engaged:** no rule content, parameter value, or legal semantics changed.

## 5. D-002 producer-requirement compliance (14 applicable PROD ids)

| Req | How satisfied |
|---|---|
| R036 / R037 (modify only allowed paths) | Only the 3 allowed source files + `tests/rules/` + this one report changed; no reserved hotspot touched. |
| R038 (frozen interface, no shared wiring) | `units.py` is a frozen interface; nothing wired into a shared production entrypoint. |
| R039 (stop + interface-change request if a frozen interface must change) | No shared/canonical contract needed changing; none edited. |
| R051 (read CLAUDE.md + packet at start) | Read root `CLAUDE.md`, `M4-T007.json`, capsule, First-Wave Contract, B-014, DF-2, `operations.py`/`evaluator.py` before implementing. |
| R052 (work through without stopping at substeps) | Completed implementation → tests → self-checks in one run. |
| R053 (no merge/accept/replan/other task/worktree) | None performed; producer-only. |
| R054 (no unmerged-sibling read; no shared-contract edit) | Built only on merged `main`; no sibling branch read; no contract edited. |
| R055 (commit+push own branch; one PR) | One branch, one PR against `main` (§6). |
| R056 (detailed evidence in report/CI, not chat) | This report holds the evidence/matrices. |
| R057 (stop only for a real owner/credential/legal/security/destructive/collision) | None encountered. |
| R058/R059/R060 (return format) | Owner return kept ≤500 words / ≤8 bullets; no intermediate-SHA dumps. |

## 6. Contract/interface impact, limitations, next unlocked

- **Interface impact:** additive only. New frozen `units.py`. `operations.COMPUTE_OPS` now return exact
  `Fraction` internally; the trace's external shape is unchanged (JSON numbers; existing outputs render
  identically). No schema/contract/DSL change.
- **Honest limitations:** (a) the DSL does not annotate per-argument units, so the evaluator enforces
  *known* units on declared inputs/outputs and provides `Quantity` for *incompatible*-unit rejection,
  rather than tracking dimensions through every op; (b) `float` appears only at the JSON render boundary
  (no decision) and in the input-admission overflow gate; (c) division-by-zero and malformed compute
  args fail closed by raising `EvaluationError` (no value emitted).
- **Next dependency unlocked:** future M4 rule tasks consume this exact-math foundation once merged;
  B-014 is satisfied at the engineering level (orchestrator resolves the blocker upon acceptance). This
  producer does not self-accept.
