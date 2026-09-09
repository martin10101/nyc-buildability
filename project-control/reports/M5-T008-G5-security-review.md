# M5-T008 — G5 Security/Privacy Review (independent)

- **Gate:** G5 (security / privacy / fail-safe correctness)
- **Verdict:** PASS
- **Reviewer:** security-reviewer (independent; ≠ producer)
- **Reviewed SHA:** `24780f2683dafd41b895fa2d1668814a19a6b3e4`

Pure offline function; no network/auth/storage/env/file/subprocess/eval/exec/pickle. Imports copy/json/math/enum/typing/.constants/.derive only (negative grep clean). `git show --stat` = exactly the 4 files; derive.py/ranking.py/builder/models/constants/contract/packages/contracts/** untouched, consumed read-only. `pytest services/api/tests/scenario -q` → 222 passed (173 + 49), 0 regression.

## Findings — no critical/high/medium
1. **Fail-closed completeness — PASS.** Every input path yields a typed outcome, no raise: bad/non-finite variable→INVALID (`_normalize_variable` 365-382); non-str/`verified` variable→echo suppressed None (`_safe_variable_echo` 385-394); non-dict/degenerate/no-cap doc→EMPTY (isinstance-guarded); non-list values→INVALID (654-663); NaN/±Inf/negative/overflow value→typed `_unsafe_marker` fed to derive→not-derivable-in-value-order (`_json_safe` 281-308); non-serializable object→`unsupported` marker (type name only); object/NaN dict key→`__unsafe_key__` token + collision de-dup (311-326), no ` at 0x`; huge int (≥4300 digits)→`_safe_scalar_repr` bit_length descriptor (227-240), never decimal-expanded, float() OverflowError caught. `json.dumps(result, allow_nan=False)` never raises, no NaN/Inf/negative emitted.
2. **Determinism as security — PASS.** Every probe leak=False (no address); two runs with distinct object inputs byte-identical; `_content_key` avoids sort_keys.
3. **Resource safety — PASS** for input domain: no int decimal expansion; repr bounded 120 chars; O(n) in supplied values.
4. **Injection / label integrity — PASS.** `verified` variable→suppressed; incoming coverage `verified`→capped conditional (`_bounded_coverage_status` 332-342); coverage derived only from the scenario document, never from values → cannot up-label via values.
5. **No secrets/logging/eval/exec/pickle-import/network — PASS.**

**Note — stricter than baseline:** sensitivity sanitizes each value via `_json_safe` (line 429) BEFORE building the assumption fed to derive, so derive never repr()s a raw huge int — closing the int→str crash path that ranking.py (ranking.py:439 raw deepcopy→derive) left open. Modularity: 705 SLOC < 750 justify; single cohesive responsibility; additive facade.

## LOW findings (non-blocking; → shared-sanitizer backlog; baseline-consistent, unreachable via JSON)
- **L1 (SEC-L2):** `copy.deepcopy(tried)` (sensitivity.py:483) raises on a non-deepcopyable value (threading.Lock/generator/`__deepcopy__`-raises). Not JSON-representable; no current caller; same pattern as accepted derive.py/ranking.py.
- **L2 (SEC-L3):** `_json_safe` (304-308) has no cycle/depth guard → RecursionError on cyclic/extremely-deep value. Cycles not JSON-representable; the API's `json.loads` rejects nesting at ~depth 1000 before reaching this function (reproduced). Same recursive posture as derive/ranking.
- Suggested remediation (future shared-sanitizer decomposition task, already flagged in-source sensitivity.py:50-54): extract a shared `scenario/_json_safety.py` used by derive.py/ranking.py/sensitivity.py, and in that one bounded change wrap the raw-value deepcopy in try/except + add a depth/seen-set bound to `_json_safe` (closes L1/L2 across all three). Non-blocking.
