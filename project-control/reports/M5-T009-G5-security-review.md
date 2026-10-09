# M5-T009 — G5 Security/Privacy Review (independent)

- **Gate:** G5 (security / privacy / fail-safe correctness) — **Verdict:** PASS
- **Reviewer:** security-reviewer (independent; ≠ producer). Reviewed SHA `3b298474`.

Task's point: extract the sanitizer to shared `_json_safety.py` (behavior-neutral) + CLOSE the M5-T007/T008
G5 LOWs — L1 (non-deepcopyable raised) and L2 (cyclic/deep → RecursionError). No blocking findings; no new hole.

## L1 closure — CONFIRMED both consumers, fail-closed, no raise
ranking.py:288-313 (`try copy.deepcopy … except` → typed not-scorable candidate, `_unsafe_marker("undeepcopyable")`,
derive NOT called on the unusable copy); sensitivity.py:311-314 (except → `tried_echo = safe_value`, the already-
computed address-free `_json_safe(tried)` marker). Probes (lock/generator/__deepcopy__-raises via the PUBLIC
entry points): typed marker, no raise, json.dumps(allow_nan=False) OK, `" at 0x"` absent. Multi-bad inputs: no
raise; `_sort_key` reduces the raw value via `_finite_float` so a non-comparable value never reaches a compare.

## L2 closure — CONFIRMED (typed markers, no raise, path-scoped cycle detection)
`_json_safe` uses an explicit `_Frame` stack (not native recursion): cycle via path-scoped `ancestors` id-set →
`cycle` marker; depth via FIXED `_MAX_JSON_SAFE_DEPTH=500` → `max_depth` marker. Self-ref list/dict/mutual →
cycle markers, no RecursionError. DAG (same dict in 3 slots) rendered in full each position (path-scoped, NOT a
global seen-set).

## KEY DoS point — CONFIRMED SAFE, not relocated
Input depth 1000/5000/10000 (list AND dict) → sanitizer never raises, output bounded to 501 container levels,
`json.dumps(result, allow_nan=False)` succeeds. Bound is a fixed constant (no `sys` import); ~440 frames of
caller-stack headroom on 3.11 (wider on 3.12 CI). Hazard eliminated rather than relocated to json.dumps's C
recursion.

## Behavior-neutrality of the security guards — byte-identical
19-case differential (removed recursive sanitizer vs new iterative) → 0 mismatches. Every guard preserved:
int→str ceiling via bit_length≤256; no object-address leak (markers carry type-name/magnitude only, `" at 0x"`
absent everywhere); NaN/Inf/negative/overflow → typed markers; bounded repr 120; deterministic. No secrets/
logging/eval/exec/pickle/network (imports math + typing only). Modularity clean.

## Non-blocking notes (informational, no new hole)
(1) a finite NEGATIVE numeric dict KEY passes through `_safe_key` verbatim (serializes as a JSON string key
"-0.5") — pre-existing, identical in the removed copy, benign/JSON-safe/deterministic. (2) `_json_safe_mapping`
remains exported but is now unused by production (tests only); cycle-safe; could be pruned in a future cleanup.
(3) the 500-bound margin measured on 3.11 (~440-frame headroom); 3.12 CI widens it. None are defects.
