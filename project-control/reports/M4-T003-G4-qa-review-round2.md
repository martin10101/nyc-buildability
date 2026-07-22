# Gate Report — M4-T003 G4 (integration & regression) DELTA re-gate (ROUND 2)

_Verbatim independent qa-engineer return (transport decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

- **Gate ID:** M4-T003-G4 (delta re-gate of the rework increment)
- **Task ID:** M4-T003 — Rules-engine correctness hardening (rework round-1)
- **Reviewer:** qa-engineer (independent; read-only)
- **Frozen SHA:** `7051a7bd631d8bdef62807c106267e72f2e73edd` (worktree HEAD confirmed = `7051a7b`; branch `task/M4-T003-hardening`)
- **Delta reviewed:** `846c191 → 7051a7b`
- **Result: PASS**

## Commands independently executed (from `services/api`)

| Command | Result |
|---|---|
| `python -m pytest tests/rules/ -q` | **69 passed** in 1.52s |
| `python -m pytest -q` (full api) | **659 passed** in 17.45s |
| `python -m pytest tests/rules/test_rules_engine_hardening.py -v` | **33 passed** (20 round-1 RH-S1..S8 + 13 new RH-S9..S13) |
| `python -m ruff check app tests` | All checks passed! |

Count delta is consistent: round-1 was 646 full / 36 base + 20 hardening; +13 new hardening cases → 659 full / 69 rules. No regressions; suite fully green.

## Delta scope (verified)
`git diff 846c191 7051a7b --stat` touches exactly three files: `evaluator.py` (+80/-4), the new fixture `demo-compliance-optional.rule.json` (+42), and `test_rules_engine_hardening.py` (+130). `registry.py` is **untouched** — confirming no naive family-wide overlap guard was slipped in (see L-1 below). The evaluator diff matches the REWORK-HANDOFF recipe line-for-line.

## Required-coverage verification (each item confirmed present, targeted, non-tautological, and regression-meaningful)

- **D1 huge-finite `lot_area=1.2e308` → PRR + `outputs=={}` + strict-JSON** — `test_rh_s9_overflow_output_fails_closed_no_value`. Input is finite/in-domain (passes input validation), `1.2e308 * FAR(1.5)` overflows to `inf`; the new step-3a output-finiteness guard fails closed. Asserts PRR, `outputs=={}`, key absent, `json.dumps(export, allow_nan=False)` succeeds, and note contains "non-finite result". **Regression-meaningful:** pre-fix `evaluate()` had no output guard → would emit `coverage=conditional` with `outputs.max_...==inf`. Targets the guard specifically (not input validation).
- **D2 `10**309` → PRR no-crash** — `test_rh_s9_huge_int_does_not_crash_validation`. Asserts PRR, `outputs=={}`, `input_validation.valid is False`, `lot_area_sq_ft` in `invalid_inputs`, strict-JSON. **Regression-meaningful:** pre-fix `_invalid_reason` did bare `float(value)` → uncaught `OverflowError`; the diff adds the try/except.
- **D3 `[inf]` container → PRR + strict-JSON** — `test_rh_s10_container_nested_nonfinite_stays_strict_json`. A list is a wrong-type input (PRR); the nested `inf` survives into the trace's evaluated inputs. **Regression-meaningful:** pre-fix `_json_safe` only stringified a top-level float, so `json.dumps(export, allow_nan=False)` would raise; the diff makes `_json_safe` recurse into list/tuple/dict.
- **Strict-JSON invariant on a SUCCESS trace** — `test_rh_s10_successful_trace_is_strict_json` (normal R5 export) — and on **each fail-closed trace** — RH-S2 (non-finite input), RH-S9 ×2, RH-S10, RH-S11 ×5 all carry `json.dumps(..., allow_nan=False)`.
- **as_of_date malformed (string variants) + non-string → PRR fail-closed, `in_effect False`** — `test_rh_s11_malformed_as_of_date_fails_closed[garbage|2024/12/05|2024-13-05|2024-12-32]` + `test_rh_s11_non_string_as_of_date_does_not_crash[20240101]`. Asserts PRR, `outputs=={}`, `effective_window.in_effect is False`, strict-JSON. **Regression-meaningful:** pre-fix "garbage" lexically compared > `effective_from 2024-12-05` (with `effective_to=None`) → treated in-effect and computed; a non-string raised `TypeError`. The diff adds `_valid_iso_date` + a pre-temporal-gate fail-closed branch. The malformed-date variants also confirm the validator's month/day range check (`2024-13-05`, `2024-12-32`), not just the regex.
- **`lot_area=0` (exclusive_minimum boundary) → PRR** — `test_rh_s12_zero_lot_area_exclusive_minimum_boundary_fails_closed`. Coverage-gap filler on already-correct validation (exclusive_minimum 0 rejects exactly 0).
- **`lot_area=True` (bool-as-number) → PRR** — `test_rh_s12_bool_as_number_fails_closed`. Asserts PRR + `lot_area_sq_ft` in `invalid_inputs` (Python `bool` is an `int` subclass but rejected).
- **compliance `proposed=-5000` → PRR + `determination is None`** — `test_rh_s12_negative_proposal_fails_closed_no_determination`. Confirms a bad input yields no fabricated pass/fail.
- **Indeterminate determination fixture `demo-compliance-optional.rule.json` (omit proposal → limit computed, determination None, coverage conditional)** — `test_rh_s13_indeterminate_determination_when_proposal_omitted`. The fixture is a faithful copy of `demo-compliance-far` with `proposed_floor_area_sq_ft` made `"required": false`. Asserts the limit **is** computed (`max_floor_area_sq_ft == 15000.0`) **and** `determination is None` **and** `coverage == conditional` simultaneously — a genuine, non-tautological indeterminate check.

## G4-L1 overlapping-effective-window limitation
Correctly **documented, not naively fixed**. `registry.py` is untouched in the delta, and `RuleRegistry.effective_rules` retains the docstring: *"…more than one is an overlapping-window authoring error the caller must surface, never silently pick from."* No load-time family-wide overlap guard was added (which would have been a DEFECT — two rules in a family can legitimately coexist across an overlapping window when distinguished by applicability). This matches the handoff's "Do NOT do" directive.

## Findings (severity-ranked)

No blocking defects. The round-1 non-blocking gaps that were in scope for this rework are now closed:
- **Resolved (were G-1/G-2/G-3/G-6 + L-2):** indeterminate-determination branch (RH-S13), compliance bad-proposal (RH-S12), exclusive_minimum=0 boundary (RH-S12), bool-as-number (RH-S12), and malformed/non-string `as_of_date` now fail **closed** (RH-S11) — the round-1 L-2 fail-open limitation is fixed.

Remaining **non-blocking** observations (no claimed defect left unverified):
- **INFO-1:** Round-1 G-4 (integer-type validation branch, and `maximum`/`exclusive_maximum`) remains unexercised — there is still no integer-typed or upper-bounded input in the repo corpus. Not in this rework's scope; the D1 output guard now covers the practical overflow risk that an upper bound would have addressed.
- **INFO-2:** L-1 has documentation but no contract test asserting the documented ">1 in-effect rules → caller disambiguates" behavior. Optional hardening only; the docstring assigns the contract to the caller and `evaluate()` gates per-rule, so there is no silent mis-evaluation today and no consumer yet.

## Verdict

**PASS.** Independently reproduced: 69 rules / 659 full / ruff clean at frozen `7051a7b`. All D1/D2/D3 and as_of_date defects from the round-1 G5 FAIL are covered by new tests that are genuine (not tautologies), targeted at the exact guard, and regression-meaningful (would fail against the pre-fix code, verifiable from the diff). The round-1 cheap coverage gaps and the indeterminate-determination fixture are added and passing. The G4-L1 overlapping-window limitation is documented, not naively guarded (registry unchanged). INFO-1/INFO-2 are non-blocking.
