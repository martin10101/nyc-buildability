# M5-T007 — G5 Security/Privacy Review (independent)

- **Gate:** G5 (security / privacy / fail-safe correctness)
- **Verdict:** PASS
- **Reviewer:** security-reviewer (independent; ≠ producer)
- **Reviewed SHA:** `1f938f4a7b174c0338c0ecdb2ef0c6b14bdba436`

Feature is a pure offline function `rank_scenario_assumption_sets`; no network/auth/storage/external I/O. Consumes accepted `derive_practical_usable_range` read-only. No endpoint/frontend consumer wiring exists (only the module, its facade, and its tests reference the symbol) → zero untrusted ingress today.

## Reproduction
`pytest test_scenario_ranking.py -q` → 49 passed; `pytest services/api/tests/scenario -q` → 173 passed (no regression). Adversarial probes piped to python stdin (no repo writes).

## Findings — no critical/high/medium
1. **Fail-closed completeness — PASS.** Every JSON-expressible input yields a typed outcome, never raises: bad/non-finite objective→INVALID (`_normalize_objective`); non-list container→INVALID; degenerate/absent doc→EMPTY (isinstance guard before .get); malformed set→not-scorable-last via derive guard; NaN/±Inf/negative/overflow value→typed `_unsafe_marker`, json.dumps(allow_nan=False) safe; CPython int→str ceiling (≥4300 digits) as value OR key→magnitude descriptor (bit_length<=256), never decimal-expanded; float(huge_int) OverflowError caught; object repr→type name only; object dict keys→token with #N de-collision; scorer lookup total (validated enum).
2. **Determinism as security — PASS.** Fresh objects across runs → byte-identical (probe). No address/id/transient value leaks; tie-break uses insertion-order json.dumps (not sort_keys); `_sort_key` total order over (int,float,str).
3. **Resource safety — PASS** for the input domain: repr bounded 120 chars; huge int described by magnitude, not expanded. (Unbounded-recursion vectors exist only for non-JSON-reachable inputs — see LOW-2.)
4. **Injection / label integrity — PASS.** objective="verified"→suppressed to None (`_safe_objective_echo`); incoming coverage "verified"(any case)→capped to "conditional" (`_bounded_coverage_status`); coverage never derived from assumption values (a caller cannot up-label via assumption values). Informational: a literal "verified" inside an assumption value/rationale is echoed as the caller's own free text — changes no label/coverage field, cannot up-label; honest echo, not a defect.
5. **No secrets/logging/eval/exec/pickle-import/network — PASS** (grep clean; only stdlib copy/json/math/enum/typing). `copy.deepcopy` uses the pickle protocol internally but imports no pickle and deserializes no untrusted bytes.

Modularity spot-check PASS (673 SLOC < 750 justify; single cohesive responsibility; additive import-stable facade).

## LOW findings (non-blocking; → fast-follow backlog, same posture as prior derive.py LOWs)
- **LOW-1 (SEC-L2):** `copy.deepcopy(assumption_set)` (ranking.py:439) raises uncaught on a non-deepcopyable object (threading.Lock/generator), as value or set member. NOT reachable from a JSON body or explicit UI assumption-set; no current caller; latent equally in accepted `derive.py:_copy_assumption`. Remediation: wrap deepcopy in try/except → typed not-scorable/marker, or document the JSON-shaped/deepcopyable/acyclic precondition.
- **LOW-2 (SEC-L3):** `_json_safe` (ranking.py:273-301) has no cycle/depth guard → RecursionError on a self-referential or ~20000-deep value; `_content_key` json.dumps on a cycle raises ValueError (not the TypeError caught). NOT expressible in JSON; no current caller. Remediation: id()-memo cycle guard and/or max-depth cap returning a typed marker; broaden `_content_key` except to (TypeError, ValueError).

Both LOW require Python-runtime-only objects that cannot originate from the JSON/explicit-input domain and have no current caller → non-blocking, matching the accepted derive.py baseline.
