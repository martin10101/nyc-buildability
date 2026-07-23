_Verbatim independent code-reviewer return (transport entity-decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

# G3 CODE-REVIEW GATE REPORT — M5-T001

**Task:** M5-T001 — Deterministic coverage-aware scenario foundation
**Reviewed SHA:** `e994147` (`e9941471a7d930a499df047537581a648347f498`) on `task/M5-T001-scenario-foundation` (PR #86), base `main` @ `0a61b7d`
**Reviewer role:** independent G3 (code), read-only
**Verdict: PASS**

## Commands run and actual outputs

| Command (cwd) | Result |
|---|---|
| `python -m ruff check .` (`services/api`) | `All checks passed!` |
| `python -m pytest tests/scenario -q` (`services/api`) | `54 passed in 0.31s` |
| `python -m pytest -q` (full `services/api`) | `881 passed in 6.75s` |
| `python packages/contracts/scripts/generate_ts_types.py --check` | profile / rule_evaluation / scenario / client block all `OK ... up to date` |
| `python -m pytest packages/contracts/scripts/tests/test_generate_scenario_ts.py -q` | `5 passed` |
| `git diff --name-only e994147 0a61b7d` | only `services/api/app/scenario/**`, `services/api/tests/scenario/**`, `packages/contracts/{schemas/v1/scenario.schema.json, generated/scenario.ts, fixtures/**/scenario/**, scripts/generate_ts_types.py, scripts/tests/test_generate_scenario_ts.py}`, `services/api/app/_contract_schemas/v1/scenario.schema.json`, and `project-control/**` (orchestrator-written task/state/gate/report). No profile/spatial/rules, `api/v1`, or `apps/web` paths touched. |
| Fixture-genuineness check (fresh `build_scenario` vs committed valid fixtures) | all 4 valid fixtures `MATCH` — not fabricated |

## Verification against the seven required points

1. **Canonical value, not recomputed — PASS.** `builder.py:390` sets `cap_value` from `trace_outputs.get(CAP_OUTPUT_NAME)`; `draft_zoning_floor_area_cap_sq_ft` (`builder.py:321`, `553`) is that trace value. The `far*lot_area` recompute (`builder.py:477`) is only compared, never surfaced. The AS-1 companion test `test_as1_value_comes_from_trace_not_recompute_even_without_far` deletes `max_residential_far`, so no recompute is possible, yet the cap is still surfaced from the trace and `integrity_check.performed is False` — this genuinely proves the value is read, not derived.

2. **Integrity check is verification-only, fails closed — PASS.** `builder.py:479-485`: relative-with-floor tolerance, `math.isfinite(recomputed)` guards overflow-to-inf, disagreement routes to `_no_scenario_integrity` which surfaces `cap_value=None` and withholds both numbers (AS-7 asserts neither `15000` nor `30000` appears). `far_value`/`lot_area`/`cap_value` all pass through finite/positive guards (`_finite_float`, `_positive_finite_float`) so NaN/inf/None cannot reach the comparison or the output.

3. **No envelope inference — PASS.** `_missing_envelope_constraints()` emits every envelope family as `state=missing, value=None`; coverage matrix marks them `missing`/`out_of_scope`. No code path assigns an envelope value. AS-3 asserts height/setbacks/lot-coverage stay `missing` with null value.

4. **Fail-closed decision logic matches §5 — PASS.** Precedence malformed > conflict > professional-review > unsupported > preliminary (`builder.py:433-473`); preliminary requires `family_cov_status=="conditional" AND re_coverage=="conditional"` plus present trace/lot_area/finite cap. All §5 hard-stops covered.

5. **Determinism & strict-JSON — PASS.** Fixed constraint/matrix ordering, assumptions sorted by key, no wall-clock/random imports, no set reaches serialized output (frozensets/set-literals used only for membership). `validate_scenario_document` enforces `json.dumps(..., allow_nan=False)`. AS-8 confirms byte-identical output.

6. **Never `verified` — PASS.** `coverage_status` only ever conditional/data_conflict/professional_review_required/unsupported/not_applicable; `needs_review=True` and `not_verified_disclaimer` on every branch; `assert_scenario_not_verified` + schema `coverage_status_draft` allOf-subset exclude `verified`. AS-9 exhaustive.

7. **Read-only consumption / scope — PASS.** Builder reads only via `.get()`, never mutates inputs (AS-12 proves it), no import-time side effects. Diff confirms forbidden source paths untouched; runtime-bundle byte-identity guarded by a passing contract test; typegen change is purely additive (independent scenario emission, profile/rule_evaluation `.ts` untouched).

## Non-blocking observations (no action required for acceptance)

- N1 `_positive_finite_float` coerces the trace cap to `float` — value-identical to the canonical output but changes representation for an integer cap (e.g. `15000` → `15000.0`). "Verbatim" holds in value; harmless given the finite-guard requirement. (`builder.py:75-80`, `390`)
- N2 The integrity recompute uses the top-level `rule_evaluation.lot_area_sq_ft` rather than the trace's `evaluated_inputs.lot_area_sq_ft`. This is strictly more conservative (a top-level/trace lot-area disagreement also fails closed, as exercised by AS-7). Defensible.
- N3 A `bbl` mismatch between `property_profile.identity.bbl` and `rule_evaluation.evaluated_input.bbl` is treated as a `data_conflict` (`builder.py:400-412`). This is an extra fail-closed guard beyond §5; conservative and consistent with the fail-closed intent.
- N4 `_no_scenario_missing` can carry `coverage_status="conditional"` on a `no_scenario` outcome (coverage carried through from the rule_evaluation while the scenario-layer input is absent). No cross-field schema constraint is violated; honest and acceptable.

No blocking defects found. Correctness, determinism, error handling, contract adherence, provenance propagation, and test quality all meet the spec (DRAFT-PROPOSAL §4–§6, §5a and the AS-1..AS-12 pack). Recommend **PASS**.
