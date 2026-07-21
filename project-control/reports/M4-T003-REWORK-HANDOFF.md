# M4-T003 — rework handoff (G5 FAIL round 1 → apply these fixes, re-freeze, re-gate)

**Status at handoff (2026-07-21):** M4-T003 is at frozen reviewed SHA `0e928b5` (branch
`task/M4-T003-hardening`, off main `f2939d6`, pushed, CI green 12/12). Round-1 independent gates:
**G3 PASS, G4 PASS, G5 FAIL** (blocking). This doc is the exact rework recipe. The worktree is at the
clean reviewed SHA (my in-progress edits were reverted so the next session starts from a clean base).

Gate reports (this branch): `project-control/reports/M4-T003-G3-code-review.md`,
`M4-T003-G4-qa-review.md`, `M4-T003-G5-security-review-round1.md`. Producer report:
`M4-T003-producer-report.md`.

## G5 blocking defects (all reproduced at 0e928b5) — MUST fix before a clean G5

- **D1 [HIGH] — overflow fabricates an `inf` OUTPUT in a `conditional` result.** No output-finiteness
  guard. Repro: `RuleRegistry().load().evaluate("r5-residential-far", {"zoning_district":"R5",
  "lot_area_sq_ft":1.2e308,"site_class":"standard_zoning_lot"})` → `coverage=conditional`,
  `outputs.max_residential_floor_area_sq_ft == inf`; the trace also fails `json.dumps(export,
  allow_nan=False)`. Same defect class as the owner's `-5000 → -7500`, unbounded at the top.
- **D2 [MEDIUM] — huge int crashes validation.** `float(value)` in `_invalid_reason` raises an
  uncaught `OverflowError` for an arbitrary-precision int (e.g. `10**309`). Must fail closed, no crash.
- **D3 [MEDIUM] — container-nested non-finite → non-strict-JSON trace.** `_json_safe` only stringifies
  a top-level float. Repro: `lot_area_sq_ft=[float('inf')]` → correct PRR coverage but
  `json.dumps(export, allow_nan=False)` raises.
- **I1/R2/L2 [LOW, both G3+G4 also flagged] — malformed/non-string `as_of_date` fails OPEN.**
  `is_in_effect` does a lexical compare (`"garbage"` treated in-effect) and a non-string raises
  `TypeError`. Fail closed on a non-ISO `as_of_date`.

## Exact fixes (all in `services/api/app/rules/evaluator.py` unless noted)

### 1. `import re` (top of file, after `import math`)

### 2. Harden `_is_finite_number` + recurse `_json_safe` (D2-defense + D3)
```python
def _is_finite_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:      # int too big to convert to float (e.g. 10**400)
        return False


def _json_safe(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return repr(value)
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    return value
```

### 3. `_invalid_reason` — guard `float()` overflow (D2)
```python
        try:
            number = float(value)
        except OverflowError:
            return "numeric value is out of representable range (too large to use)"
        if not math.isfinite(number):
            return "non-finite number (NaN or infinity) is not a usable value"
```

### 4. ISO `as_of_date` validator (add near `_effective_window`)
```python
_ISO_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")

def _valid_iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    match = _ISO_DATE_RE.match(value)
    if not match:
        return False
    _, month, day = (int(part) for part in match.groups())
    return 1 <= month <= 12 and 1 <= day <= 31
```

### 5. In `evaluate()` — validate `as_of_date` BEFORE `_effective_window` (a non-string would raise in
`is_in_effect`). Replace `effective_window = _effective_window(rule, as_of_date)` with:
```python
    as_of_invalid = as_of_date is not None and not _valid_iso_date(as_of_date)
    if as_of_invalid:
        effective_window = {
            "effective_from": rule.effective_from,
            "effective_to": rule.effective_to,
            "evaluated_as_of": _json_safe(as_of_date),
            "in_effect": False,
        }
    else:
        effective_window = _effective_window(rule, as_of_date)
```
Then, immediately AFTER the `_make_trace` closure def and BEFORE the temporal-gate block, add:
```python
    if as_of_invalid:
        return RuleResult(_make_trace(
            applicability_outcome=False,
            applicability_trace=[{"invalid_as_of_date": True, "value_seen": _json_safe(as_of_date)}],
            coverage_status=cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            data_completeness=cov.COMPLETENESS_COMPLETE,
            notes=base_notes + ["as_of_date is not a valid ISO (YYYY-MM-DD) calendar date; "
                                "temporal effectiveness cannot be determined (fail-closed)"],
        ))
```

### 6. Output finiteness guard (D1) — in `evaluate()`, right AFTER
`step_traces, outputs = _run_computation(rule, inputs)`:
```python
    nonfinite_steps = [s["step_id"] for s in step_traces if not _is_finite_number(s["result"])]
    if nonfinite_steps:
        return RuleResult(_make_trace(
            applicability_outcome=True,
            applicability_trace=[appl_trace],
            coverage_status=cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            data_completeness=cov.COMPLETENESS_COMPLETE,
            notes=base_notes + [f"computation produced a non-finite result in step(s) "
                                f"{nonfinite_steps} (numeric overflow); no value emitted (fail-closed)"],
        ))
```
Do NOT add a hard-coded `maximum` on `lot_area_sq_ft` (no defensible NYC-lot ceiling without source);
the output guard is the correct general fix.

## Tests to add (`services/api/tests/rules/test_rules_engine_hardening.py`)
- **D1:** huge finite `lot_area_sq_ft=1.2e308` → coverage `professional_review_required`, `outputs=={}`,
  and `json.dumps(export, allow_nan=False)` succeeds.
- **D2:** `lot_area_sq_ft=10**309` → PRR, `outputs=={}`, **no exception**.
- **D3:** `lot_area_sq_ft=[float('inf')]` → PRR and `json.dumps(export, allow_nan=False)` succeeds.
- **Strict-JSON invariant:** assert `json.dumps(export, allow_nan=False)` on BOTH a successful R5 trace
  and each fail-closed trace (fold into RH-S2 + a new RH-S9).
- **as_of_date:** `"garbage"`, `"2024/12/05"`, and a non-string (e.g. `20240101`) → PRR fail-closed,
  `effective_window.in_effect is False`.
- **G4 cheap gaps:** `lot_area_sq_ft=0` (exclusive_minimum boundary) → PRR; `lot_area_sq_ft=True`
  (bool-as-number) → PRR; compliance `proposed_floor_area_sq_ft=-5000` → PRR + `determination is None`.
- **G-1 indeterminate determination:** add a small synthetic fixture
  `tests/rules/fixtures/m4t003/rulesets/demo-compliance-optional.rule.json` identical to
  `demo-compliance-far` but with `proposed_floor_area_sq_ft` OPTIONAL (`"required": false`); omitting it
  → rule computes the limit, `determination is None`, coverage `conditional`.

## Do NOT do (G4-L1 — overlapping effective windows)
Do **not** add a naive family-wide overlap guard in `registry.load()` — two rules in one family can
legitimately coexist with overlapping windows when distinguished by applicability (e.g. different
districts). Document it as a known limitation; a precise guard needs a future `rule_series` grouping
(same-applicability temporal versions). Optionally add a contract test asserting the documented
"`effective_rules` returns all in-effect rules; the caller disambiguates" behavior.

## After applying
1. `ruff check app tests` clean; `pytest tests/rules/ -q`; `pytest -q` (full api, expect ~646 + new).
2. Commit on `task/M4-T003-hardening`; **re-freeze** the new SHA; push; confirm CI green (12/12).
3. Re-dispatch gates at the new SHA: **G5 mandatory** (must clear its 3 defects); **G3 + G4** for the
   delta. Reviewers are independent, read-only; orchestrator records verdicts.
4. Return the consolidated evidence packet (M4-T003 + M4-T002) to the owner BEFORE any merge.

## Then (owner-authorized integration order — do NOT merge without owner authorization)
1. M4-T003 clean-gated → owner merge to main.
2. **Rebase M4-T002** (`task/M4-T002-integration` @ `f25dbff`, its own 3 gates PASS) onto the corrected
   engine → re-validate (RI-S1..S8 + C1-C3) → owner merge/integrate. Its non-blocking follow-ups: apply
   G5 LOW-1 (`isinstance`-list guards) + LOW-2 (`math.isfinite` in `_positive_number`) — now redundant
   with the engine-level D-fixes but still good defense in the integration layer — and remove the
   vestigial `verified_status_present` field (G3-F2).
