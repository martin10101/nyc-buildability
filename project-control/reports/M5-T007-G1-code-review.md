# M5-T007 — G1 Code Review (independent)

- **Gate:** G1 (code / correctness / maintainability / contracts / provenance)
- **Verdict:** PASS
- **Reviewer:** code-reviewer (independent; ≠ producer scenario-optimization-engineer)
- **Reviewed SHA:** `1f938f4a7b174c0338c0ecdb2ef0c6b14bdba436` (parent `8f1b049d`)
- **Task:** M5-T007 deterministic scenario ranking/scoring

## Scope & boundary integrity — PASS
`git diff --name-only 8f1b049d..1f938f4a` = exactly the 4 allowed_paths files (ranking.py NEW, __init__.py facade +10 additive, test_scenario_ranking.py NEW, producer report). Targeted diff of derive.py/builder.py/models.py/constants.py/contract.py/packages/contracts/** → no output (all UNCHANGED, consumed read-only). Facade change purely additive; public interface stable. Contract-free new object; never emits literal `verified`.

## Tests & tooling (reproduced) — PASS
- `pytest test_scenario_ranking.py -q` → 49 passed
- `pytest services/api/tests/scenario -q` → 173 passed (0 regression)
- `python tools/modularity_check.py --check` → 361 files selected, failures 0; ranking.py (673 physical, docstring-dense) NOT in warn list; single cohesive responsibility.

## Correctness — PASS
Total deterministic sort key `(0/1 scorable, -score|0.0, content_key)` — no cross-type compare, no None in path; 1-based ranks post-sort; not-scorable ranked LAST with score=None + named reason (no fabricated score). Content-based tie-break (`_content_key`, sort_keys deliberately NOT used). Independently confirmed all 24 permutations of a 4-set batch (incl. a genuine tie) → byte-identical output.

## Fail-closed + strict-JSON-safe sanitizer (D1/D2) — PASS
D1 huge-int: `_safe_scalar_repr` gates int on bit_length<=256 before repr; larger → magnitude descriptor; `_json_safe` catches float() OverflowError. Reproduced 10**5000: no crash, bit_length present, no decimal expansion, byte-identical. D2 object dict-key: `_safe_key`→`_unsafe_key_token` (type name only, never address repr); `_json_safe_mapping` de-collides distinct rejected keys with #N. Reproduced fresh _ObjKey per call: byte-identical, `" at 0x"` absent. Mixed batch (NaN/±inf/-5/1.5/[]): json.dumps(allow_nan=False) succeeds, every number finite ≥0; coverage capped to conditional; objective="verified" fails closed and is never echoed.

## Provenance / AI-boundary — PASS
Scores = already-surfaced derived point (canonical_cap × factor_product); score_components names objective/cap/factor_product/formula, no hidden weight, no recomputed legal value. Full derived provenance embedded per candidate; needs_review + not_verified_disclaimer preserved end-to-end. Inputs deep-copied, byte-unchanged, un-aliased.

## Non-blocking LOWs (→ backlog, not blocking)
- LOW-1: cosmetic — the "no explicit assumption-sets supplied" reasons-string is appended for None/[] but not when a caller passes `[[]]` explicitly (identical single raw candidate either way; candidates/scores/determinism unaffected).
- LOW-2: producer-report doc nit — cites test file "639 lines" vs actual 638.

No blocking defects.
