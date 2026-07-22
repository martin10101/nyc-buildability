# M4-T003 — G3 code-reviewer verbatim return (frozen SHA 0e928b5)

VERDICT: PASS (2 non-blocking LOW: R1 overflow->inf on success path, R2 as_of_date fails open; F1 INFO forward-compat)

---

# G3 Code-Review Gate Report — M4-T003 (rules-engine correctness hardening)

Reviewed SHA (frozen): 0e928b5 on task/M4-T003-hardening (base main f2939d6; lead-start 66d8309; impl 0e928b5). Independent read-only reviewer.
Verdict: PASS — 2 non-blocking hardening recs (R1,R2) + 1 forward-compat note (F1). No required/blocking corrections.

## Commands (independently reproduced): Python 3.11.9, pytest 8.4.2, jsonschema 4.26.0, shapely 2.0.7
- ruff check app tests -> All checks passed! (exit 0)
- pytest tests/rules/test_rules_engine_hardening.py -v -> 20 passed (RH-S1..S8)
- pytest tests/rules/test_rules_engine.py -q -> 36 passed
- pytest -q (full) -> 646 passed in 4.96s

## Scope/contract
Impl diff 66d8309..0e928b5 touches ONLY app/rules/** + tests/rules/** + producer report. Canonical packages/contracts untouched (only coverage_status.schema.json, unchanged); no cross-tier consumer imports the engine trace schema/evaluator. Additive rule_definition schema (required[] unchanged; new fields optional); rear_yard_demo still validates. RE-S5 holds (no R5/family token in 8 guarded engine files). Determinism: no datetime/now/time in app/rules; as_of_date caller-supplied.

## Fix-by-fix (all CORRECT)
- Fix 1 fail-closed input validation (_invalid_reason/_validate_inputs): negative, NaN/inf, wrong type, bad enum, bool-as-number all fail closed (PRR, outputs=={}, no crash); valid computes; non-finite stringified so fail-closed trace strict-JSON; validation before computation. Probes: lot_area=True -> PRR; zoning_district=123 -> PRR, applicability False, no crash.
- Fix 2 predicate/determination ref validation at LOAD: recurses all/any/not for applicability AND every exception condition; determination left+right checked; after schema-validate. Complete, no branch missed.
- Fix 3 rule_release on every trace; verified_eligible false for draft; DSL forbids published; probe: needs_review + matching G6Approval still conditional, verified_eligible False. No bypass.
- Fix 4 temporal versioning (is_in_effect, effective_rules): half-open [from,to) ISO compare; boundary date -> new version; out-of-window -> not_applicable no value; as_of=None no gating. Caller cannot get value from not-in-effect rule.
- Fix 5 compliance determination: pass/fail on success path only; None when none/indeterminate; does NOT touch coverage; cannot fabricate an output.
- R5 semantic change (enum removed, scope via applicability): correct; R7/C1-4 stay not_applicable; param_select keys match applicability set; only R5 is production. exclusive_minimum:0 + effective_from:2024-12-05 defensible.

## Non-blocking findings
- R1 LOW: computation OVERFLOW yields inf on the SUCCESS path. lot_area_sq_ft=1.3e308 (finite, passes validation) -> max_residential_floor_area_sq_ft=inf, coverage=conditional, input_validation.valid=True; that trace contains real inf so json.dumps(export, allow_nan=False) would fail. Outside fix 1's invalid-INPUT clause; needs a physically-impossible input (Earth ~5.5e15 sq ft) so unreachable by any acceptance scenario. Producer report phrase "never a negative/NaN/inf result" holds for invalid inputs, not valid-input overflow. Fix: declare a sane maximum on lot_area_sq_ft and/or a post-computation finiteness guard that fails closed. Not blocking.
- R2 LOW: as_of_date not ISO-format-validated; malformed date silently mis-gates. is_in_effect("garbage")->True, is_in_effect("2024/12/05")->True (lexical not date). In scope as_of is always well-formed ISO. Fix: validate ^\d{4}-\d{2}-\d{2}$ and fail closed. Not blocking.
- F1 INFO: evaluation_trace schema tightened required[] (input_validation, rule_release, effective_window, determination). Safe today (engine-owned, single producer, no external consumer, no persisted old traces). If ever promoted to packages/contracts, pair with a version bump.

## Regression: none (M4-T001 36/36; full 646/646). M4-T002 RI-S6 dependency (non-R5 -> not_applicable) preserved + tested here; M4-T002 rebase/re-review remains the correct downstream step.

VERDICT: PASS
