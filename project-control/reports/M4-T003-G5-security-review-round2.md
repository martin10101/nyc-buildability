# Gate Report — G5 (security & privacy), ROUND 2

_Verbatim independent security-reviewer return (transport decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

- Gate ID: G5 (security & privacy) — independent re-gate
- Task: M4-T003 rules-engine correctness hardening
- Reviewer: security-reviewer (independent, read-only)
- Frozen worktree: `.claude/worktrees/M4-T003-hardening` @ HEAD `7051a7bd631d8bdef62807c106267e72f2e73edd` (confirmed)
- Diff reviewed: `846c191..7051a7b` (rework) and cumulative `66d8309..7051a7b` (whole task)
- Environment: Python 3.11.9; ruff clean; no repo/control-plane mutation. All repros run from `services/api`.
- **Result: PASS**

## Scope verification
Rework touched exactly 3 files, all under `services/api`: `app/rules/evaluator.py`, `tests/rules/test_rules_engine_hardening.py`, and new fixture `tests/rules/fixtures/m4t003/rulesets/demo-compliance-optional.rule.json`. Whole-task scope is confined to `services/api/app/rules/**` + `tests/rules/**`. **No `packages/contracts` changes** — canonical contracts untouched. Grep for dynamic-exec / network / filesystem / env / secret / logging sinks in the changed evaluator: NONE (the four `input(` hits are string-literal note text, not the `input()` builtin). Engine remains pure/deterministic with no injection surface.

## Test execution
- `pytest tests/rules/test_rules_engine_hardening.py -q` → **33 passed**
- `pytest tests/rules/ -q` → **69 passed** (no regression in the M4-T001 pack)

## Per-defect verdicts (independently reproduced at 7051a7b)

**D1 [HIGH] overflow fabricates an `inf` OUTPUT — CONFIRMED-FIXED.**
Repro: `evaluate("r5-residential-far", {zoning_district:R5, lot_area_sq_ft:1.2e308, site_class:standard_zoning_lot})` → `coverage=professional_review_required`, `outputs=={}`, `json.dumps(export, allow_nan=False)` = STRICT_JSON_OK, and a deep scan finds **no non-finite float anywhere in the export**. Fix is the output-finiteness guard at evaluator.py:546-557 (step 3a), which fails closed with a visible "non-finite result … (numeric overflow)" note. Confirmed the guard does **not** swallow legitimate finite outputs: `lot_area=5e307` → `conditional`, `max_residential_floor_area_sq_ft=7.5e307` (finite) is still emitted; only true overflow (≥~1e308) trips it.

**D2 [MED] huge int crashes validation — CONFIRMED-FIXED.**
Repro: `lot_area_sq_ft=10**309` → NO crash, `coverage=PRR`, `outputs=={}`, `input_validation.valid=False`, strict-JSON OK. Also probed `10**400` → NO crash, PRR, strict-JSON OK. Fix: `float(value)` wrapped in `try/except OverflowError` in `_invalid_reason` (evaluator.py:259-262) plus `_is_finite_number` swallowing OverflowError (222-228). Confirmed no other unguarded `float()` on user input remains reachable: `operations._nums` `float()` is only reached **after** input validation (a huge int is rejected before computation); the determination `float(left/right)` at line 380 is guarded by an `_is_finite_number` check at line 378 that returns None on overflow.

**D3 [MED] container-nested non-finite → non-strict-JSON trace — CONFIRMED-FIXED.**
Repro: `lot_area_sq_ft=[float('inf')]` → `coverage=PRR`, `outputs=={}`, `json.dumps(export, allow_nan=False)` = STRICT_JSON_OK, no non-finite in export. Also probed dict nesting `{"x":inf}` → PRR, strict-JSON OK. Fix: `_json_safe` now recurses into list/tuple/dict (evaluator.py:239-242).

**as_of_date [LOW] fail-open / TypeError — CONFIRMED-FIXED.**
Repro across `"garbage"`, `"2024/12/05"`, `"2024-13-05"`, `"2024-12-32"`, `"2024-00-10"`, `"2024-12-00"`, `"2024-2-5"`, `""`, and non-string `20240101`: each → `effective_window.in_effect=False`, `coverage=PRR`, no raise, strict-JSON OK. Valid dates still work (`"2024-06-01"` → conditional/in_effect; `None` → no temporal gating, conditional). Fix: `_valid_iso_date` validated **before** `_effective_window`, with an explicit fail-closed early return (evaluator.py:410-456).

## New-regression probes (actively hunted; none blocking)
- **Output-finiteness guard false positives:** none — legit large finite outputs (1e100, 5e307) pass through unchanged.
- **`_valid_iso_date` wrong-reject:** none — all valid `YYYY-MM-DD` dates accepted; `None` correctly bypasses gating.
- **Forbidden anti-patterns NOT introduced:** (a) no hard-coded `lot_area` maximum — the R5 rule JSON declares only `exclusive_minimum: 0`; the `maximum`/`exclusive_maximum` code paths are the generic declared-domain validators. (b) No naive family-wide overlap guard — `registry.load()` rejects only duplicate `rule_id`; `effective_rules()` returns **all** in-effect rules and documents that the caller disambiguates (matches the handoff directive).
- **Strict-JSON invariant holds on the successful R5 trace AND every fail-closed branch:** verified for D1, D2, D3, invalid-as_of, temporal-not-effective, not_applicable, and missing-required traces — all `allow_nan=False`-safe.

## Residual observation (LOW, non-blocking, informational)
`_valid_iso_date` accepts calendar-impossible days (e.g. `2024-02-30`, `2024-11-31`) because it only bounds `1 ≤ day ≤ 31`. This is **not** a fail-open: such well-formed `YYYY-MM-DD` strings still sort lexically and deterministically in `is_in_effect`, produce a real coverage status, fabricate no value, and never crash. It matches the approved rework recipe exactly. A future tightening to true calendar validation (`datetime.date`) would be a nicety, not a security requirement.

## Property statements
- **Fail-closed:** now HOLDS across scalar, huge-finite-overflow, huge-int, container-nested-non-finite, wrong-type, invalid-enum, boundary (`0`), bool-as-number, and malformed/non-string `as_of_date` inputs.
- **Strict-JSON (`allow_nan=False`):** HOLDS on the successful trace and all fail-closed traces.
- **Injection / least-privilege / scope / secrecy / logging:** HOLD — no dynamic exec, network, filesystem-write, env, or secret access; additive engine-owned change; canonical contracts untouched; synthetic fixtures clearly labeled SYNTHETIC.
- **Never-Verified:** unaffected and HOLDS (RH-S8 green; nothing reaches `verified`).

All three round-1 blocking defects (D1/D2/D3) and the LOW as_of item are cleared; no new fail-open path was introduced.

## VERDICT: PASS
