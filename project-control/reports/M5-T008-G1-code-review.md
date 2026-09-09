# M5-T008 — G1 Code Review (independent)

- **Gate:** G1 (code / correctness / maintainability / contracts / provenance)
- **Verdict:** PASS
- **Reviewer:** code-reviewer (independent; ≠ producer scenario-optimization-engineer)
- **Reviewed SHA:** `24780f2683dafd41b895fa2d1668814a19a6b3e4` (parent `1915336e`)

## Scope & boundary integrity — PASS
`git diff --name-only 1915336e..24780f26` = exactly the 4 allowed_paths files (sensitivity.py NEW 705 lines/22 defs, __init__.py additive facade, test_scenario_sensitivity.py NEW 49 items, producer report). derive.py/ranking.py/builder.py/models.py/constants.py/contract.py/packages/contracts/** UNCHANGED, consumed read-only. Contract-free new object.

## Reproduced evidence — PASS
- `pytest services/api/tests/scenario -q` → 222 passed (173 pre-existing + 49 new; 0 regression)
- `--collect-only` sensitivity file → 49 items (25 funcs, parametrized)
- `modularity_check --check` → failures 0; sensitivity.py NOT in warn list (705 SLOC < 750 justify), single cohesive responsibility
- offline: negative grep supabase|geoclient|requests|httpx|socket|urllib|os.environ|getenv|subprocess|open( → no matches; imports copy/json/math/enum/typing/.constants/.derive only

## Independent correctness probe — PASS
Ad-hoc call with malformed mix [10**5000, NaN, Obj(), {Obj():'x'}, -0.5, 0.8, 0.5, 0.8]: total deterministic order (forward==reversed byte-identical, sort_keys); one point per value, duplicates preserved, no drop (point_count=8, derivable=3); json.dumps(allow_nan=False) never raises, no NaN/Inf/negative; huge int → magnitude marker (bit_length, no decimal expansion, avoids int→str ceiling); object → typed unsafe_value_removed marker; object dict-key → deterministic __unsafe_key__ token, no ` at 0x` leak; not-derivable kept in value order (not relocated); empty/None values → single baseline point (is_baseline=True), never fabricated; read-only/no aliasing (inputs byte-unchanged); never Verified (coverage capped conditional, literal `verified` variable → invalid + echo None; needs_review/disclaimer preserved).

## Provenance / AI-boundary — PASS
Each point response_point == canonical_cap × factor_product taken verbatim from derive output (point["derived"] == derive_practical_usable_range(...), asserted AS-6/AS-7). No hidden weights, no recomputed legal values; named variable + metric present on every outcome and point. Sanitizer guards mirror the accepted hardened ranking.py.

## Non-blocking LOW (→ backlog)
- LOW-1: strict-JSON-safety sanitizer (~120 lines: _json_safe/_json_safe_mapping/_safe_key/_safe_scalar_repr/_unsafe_marker/_unsafe_key_token/_bounded_repr) is duplicated from ranking.py. Acknowledged + scope-justified in-source (sensitivity.py:50-54; this task's allowed_paths forbid introducing a shared scenario/_json_safety.py). Recommend a future decomposition task to extract the shared sanitizer. NOT blocking.

No blocking defects.
