# G3 Code-Review DELTA Gate Report — M4-T003 rework (ROUND 2)

_Verbatim independent code-reviewer return (transport decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

Frozen SHA `7051a7bd631d8bdef62807c106267e72f2e73edd`.

**Verdict: PASS** (0 blocking, 0 required corrections; 2 INFO notes)

Independent, read-only re-gate of the rework delta only. Round-1 G3 PASSed at `0e928b5`; this reviews `git diff 846c191 7051a7b -- services/api`. Worktree HEAD confirmed = `7051a7b`.

## Commands (independently reproduced)
- `python -m ruff check app tests` → **All checks passed!** (exit 0)
- `python -m pytest tests/rules/ -q` → **69 passed** (exit 0)
- `python -m pytest tests/rules/test_rules_engine_hardening.py -k "rh_s9 or rh_s10 or rh_s11 or rh_s12 or rh_s13"` → **13 passed, 20 deselected**
- `python -m pytest -q` (full api) → **659 passed** (646 round-1 + 13 new; no regressions)

## Delta scope (matches contract)
`git diff --stat 846c191 7051a7b` touches exactly three files: `services/api/app/rules/evaluator.py` (+80/-4), new fixture `tests/rules/fixtures/m4t003/rulesets/demo-compliance-optional.rule.json` (+42), and `tests/rules/test_rules_engine_hardening.py` (+130). No canonical contract, `registry.py`, `models.py`, or production R5 rule JSON changed. Additive only.

## Point-by-point verification of the requested sanity checks (all CONFIRMED)

1. **Output-finiteness guard reads real dict keys.** `evaluator.py:546` uses `s["step_id"]` / `s["result"]`. Confirmed against `models.py:110-117` `ComputationStep.as_dict()` (keys `step_id, op, resolved_args, result, note`) and `_run_computation` (`evaluator.py:127-131`) which appends `.as_dict()` results — so `step_traces` is a list of those dicts. Keys are correct. The guard fails closed on ANY non-finite step (conservative, correct — an intermediate overflow correctly invalidates the whole computation). `appl_trace` referenced at line 550 is bound at line 524 on the applicability-passed path; reuse is correct.

2. **`_valid_iso_date` logic + placement.** Regex `^(\d{4})-(\d{2})-(\d{2})$` plus month 1–12, day 1–31 (`evaluator.py:320-330`). `as_of_invalid` is computed at line 410 and the fail-closed early return is at line 447 — before the temporal-gate block at line 458 — so no non-string reaches `RuleDefinition.is_in_effect` (which does `as_of_date < self.effective_from`, a `TypeError` for a non-string). Double-guarded: `effective_window["in_effect"]` is also forced `False` for the invalid case (line 416).

3. **`_json_safe` recursion.** Base case returns non-container values unchanged; recurses list/tuple/dict. Terminates on acyclic JSON-derived inputs; only stringifies non-finite floats via `repr()`, preserving all other values. Tuples become lists (fine for JSON).

4. **`base_notes` defined before use.** Defined at line 421; the new early return references it at line 454. Correct ordering.

5. **No forbidden guards added.** No hard-coded `lot_area` maximum: the `spec.maximum` checks at `evaluator.py:269-274` are the pre-existing generic per-input `InputSpec` domain checker (round-1), not in this delta and not lot-area-specific. No family-wide overlap guard was added — `registry.py` is untouched in the delta; the overlap limitation remains DOCUMENTED (not coded) in `effective_rules` docstring (`registry.py:86-91`: "more than one is an overlapping-window authoring error the caller must surface, never silently pick from").

## Correctness of the D-fixes
- **D1 (overflow output):** guard at 546-557 fails closed to `professional_review_required`, no output emitted, visible note. Verified by RH-S9 (`1.2e308` → PRR, `outputs=={}`, strict-JSON).
- **D2 (huge int):** `_invalid_reason` `float()` wrapped in `OverflowError` → invalid input, no crash. `_is_finite_number` also hardened against `OverflowError`. Verified by RH-S9 huge-int (`10**309` → PRR, `input_validation.valid is False`, no exception).
- **D3 (nested non-finite):** `_json_safe` now recurses containers. Verified by RH-S10 (`[float('inf')]` → PRR, strict-JSON export).
- **I1/R2/L2 (as_of_date):** malformed/non-string fails closed to PRR with `effective_window.in_effect is False`, no lexical mis-gate, no `TypeError`. Verified by RH-S11 (parametrized `garbage`, `2024/12/05`, `2024-13-05`, `2024-12-32`, and non-string `20240101`).

## Trace-shape / contract consistency
`EvaluationTrace` fields unchanged (`models.py:137-157`). Both new early returns build traces via the `_make_trace` closure (line 423), which populates every required field including the additive `input_validation`, `rule_release`, `effective_window`, `determination`. Strict-JSON invariant (`json.dumps(export, allow_nan=False)`) is asserted on both fail-closed traces AND a successful trace (RH-S10 `successful_trace`, RH-S13). Provenance export invariant untouched.

## Test quality
Tests are meaningful, not tautological. RH-S9 asserts the guard-specific note string `"non-finite result"` (produced only by the new guard at line 554) plus `outputs=={}` and strict-JSON — all three would fail if the guard were removed. RH-S11 asserts `effective_window.in_effect is False`, which without the fix would lexically compare `"garbage"` as in-effect. RH-S12 covers the exclusive-minimum-0 boundary, bool-as-number, and negative-proposal→`determination is None` gaps. RH-S13 uses the new synthetic `demo-compliance-optional` fixture to prove an omitted optional operand yields `determination is None` while still computing `max_floor_area_sq_ft == 15000.0` at `conditional` coverage — verified against `_evaluate_determination` (`evaluator.py:369-379`, returns None when an operand is not a finite number). The fixture is properly labeled SYNTHETIC with a `limitations` clause requiring official capture + G6 before use (provenance discipline preserved).

## INFO (non-blocking, no action required)
- **INFO-1:** `_valid_iso_date` accepts calendrically-impossible days (e.g. `2024-02-30`, `2024-04-31`) since it only range-checks day 1–31. This matches the rework spec exactly and is harmless: temporal gating is a lexical string compare, so a syntactically-valid non-existent date still orders correctly, and the fail-closed goal (reject non-ISO/non-string) is met. Cosmetic only.
- **INFO-2:** `_json_safe` has no cycle protection, but all inputs are JSON-derived (acyclic); not reachable in practice.

## Regression
None. Full api suite 659/659 (round-1 646 preserved + 13 new). M4-T002 downstream rebase/re-review remains the correct next step per the handoff.

**VERDICT: PASS**
