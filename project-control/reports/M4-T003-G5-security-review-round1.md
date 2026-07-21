# M4-T003 — G5 security-reviewer verbatim return, ROUND 1 (frozen SHA 0e928b5)

VERDICT: FAIL (blocking D1 overflow->inf output HIGH, D2 huge-int crash MEDIUM, D3 container non-finite non-strict-JSON MEDIUM; I1 non-string as_of_date LOW)

---

# Gate Report
- Gate ID: G5 (security & privacy)
- Task: M4-T003 rules-engine correctness hardening
- Reviewer: security-reviewer (independent, read-only)
- Result: FAIL
- Frozen worktree @ 0e928b5, diff base 66d8309. Python 3.11.9. No repo/control mutation.

## Steps executed
- git diff 66d8309..0e928b5 -> 13 files, all under services/api/app/rules/**, services/api/tests/rules/**, or producer report. packages/contracts NONE. Scope clean.
- pytest hardening -> 20 passed; pytest M4-T001 pack -> 36 passed.
- Adversarial probe battery (16 hostile inputs vs r5-residential-far):
  negative/nan/+inf/-inf -> PRR, empty, strict-JSON OK.
  huge_finite_float_1e308 -> conditional, VALUE (inf), strict-JSON OK (but output is inf).
  huge_int_10**400 / 10**309 -> OverflowError CRASH.
  wrong_type str/list/dict, bool_as_number, invalid_enum -> PRR empty OK.
  hostile_str_district_sql -> not_applicable empty OK.
  nonfinite_in_list / nonfinite_in_dict / nested_from_json_1e999 -> PRR empty, strictJSON FAIL:ValueError.
- Overflow probe: evaluate(R5, lot_area=1.2e308) -> conditional, outputs.max_residential_floor_area_sq_ft = inf.
- grep eval/exec/__import__/subprocess/requests/os./open/environ/logging/datetime/time/random/format over app/rules/*.py -> only benign comment text. No dynamic-exec/network/env/logging/wall-clock.

## Defects (reproducible at frozen SHA)
- [HIGH] D1 Multiplication overflow emits fabricated inf OUTPUT in a conditional result (no output-finiteness guard). evaluator._run_computation (114-135) + evaluate step 3 (~485) never check computed values finite. operations._multiply accepts finite floats; round(inf,10)=inf. Repro: evaluate("r5-residential-far", {zoning_district:R5, lot_area_sq_ft:1.2e308, site_class:standard_zoning_lot}) -> coverage conditional, outputs.max_residential_floor_area_sq_ft == inf; trace fails json.dumps(export, allow_nan=False). Same defect class the owner flagged, unbounded at top. Author already uses _is_finite_number for determinations (346-347) but not primary outputs. Remediation: after computation fail closed (PRR, drop outputs) if any step result/output non-finite; and/or declare a sane maximum on lot_area_sq_ft.
- [MEDIUM] D2 Huge-integer input -> uncaught OverflowError (crash) during validation. evaluator.py:246 number=float(value) runs before finiteness check; for int > ~1.8e308 (310+ digit JSON int -> arbitrary-precision int) float() raises OverflowError, propagates out of _validate_inputs->evaluate. Repro: lot_area_sq_ft=10**309. Remediation: wrap float(value) in try/except OverflowError -> invalid out-of-range (fail-closed PRR, no crash).
- [MEDIUM] D3 Fail-closed trace not strict JSON when non-finite float nested in a container input. evaluator.py:225-234 _json_safe/_json_safe_inputs only stringify a TOP-LEVEL float; nested non-finite in list/dict survives into evaluated_inputs and invalid_inputs[].value_seen. Repro: lot_area_sq_ft=[inf] -> PRR (correct) but json.dumps(export, allow_nan=False) raises ValueError. Remediation: make _json_safe recurse into lists/dicts.
- [LOW/info] I1 non-string as_of_date (e.g. int) raises TypeError in is_in_effect comparison (models.py:95-98). as_of_date typed str|None; noted for robustness.

## Property statements
- Fail-closed: PARTIAL, does NOT hold as claimed. Scalar hostile inputs fail closed correctly, non-R5 -> not_applicable correct. But huge int crashes (D2), huge finite reaches computation and fabricates inf (D1), container-nested non-finite -> non-strict-JSON trace (D3).
- Never-Verified: HOLDS (solid). verified_eligible = published AND matching G6; schema+assert_agent_authorable forbid authored published; most_severe only downgrades from conditional. Confirmed by green test_re_s2_* + test_rh_s8_nothing_verified.
- Injection/least-privilege/scope/logging: HOLD. No dynamic exec/network/secret/fs-write/env; additive engine-owned schemas; canonical contracts untouched; change set limited; no sensitive logging. Synthetic fixtures correctly labeled + digest-verified.

## Required rework (blocking for G5 PASS and downstream G6)
Apply D1, D2, D3 remediations with acceptance tests: (a) huge int + huge finite -> PRR, no value, no exception; (b) every fail-closed AND successful trace satisfies json.dumps(export, allow_nan=False); (c) explicit output-finiteness guard. D1 (fabricated value) is priority.

VERDICT: FAIL
