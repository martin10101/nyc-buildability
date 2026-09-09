# M5-T011 — G1 Code Review DELTA RE-ATTESTATION (verbatim reviewer return) — PASS

Reviewer: **code-reviewer** (independent ≠ producer). Prior PASS at `bbf3267f` (M5-T011-G1.md); re-attested at `14ae88cc82d4630b8f9d9c22b2ca8857532c48f4` after the G5 security fix. Transport entity-decoding applied.

---

# Gate Report (delta re-attestation)

- **Gate ID:** G1 (independent code review) — delta re-attestation
- **Task ID:** M5-T011
- **Reviewer:** code-reviewer (independent; not the producer)
- **Result: PASS**
- **Prior attestation:** PASS at `bbf3267f`. **Re-attested at:** `14ae88cc82d4630b8f9d9c22b2ca8857532c48f4` (verified `git rev-parse HEAD` == new reviewed SHA).

## Delta reviewed
`git diff --numstat bbf3267f..14ae88cc` = exactly 2 files: breakeven.py (+9/−3), test_scenario_breakeven.py (+64/−0). No forbidden path; __init__.py and siblings byte-unchanged.

Production change (`_build_candidate`): removed `import copy`; replaced `generated = [...]; echo = copy.deepcopy(generated)` with a direct `echo = [...]` built from the already-fresh `safe_value = _json_safe(candidate)`. Fixes the G5-BLOCKING uncaught RecursionError on ~500-deep nested candidates (the removed copy.deepcopy was recursive, reintroducing the exact stack-dependence the iterative sanitizer exists to avoid).

## Correctness of the fix (independently verified)
- Redundancy of the removed deepcopy — confirmed. `_json_safe(candidate)` already returns a FRESH, depth-bounded structure that does not alias the caller's input; building `echo` directly from it needs no further copy.
- No new aliasing / mutation risk — confirmed. `derive` consumes assumptions strictly read-only (copies each field via `_copy_assumption`); the emitted `core` is passed through `_json_safe(...)` producing independent fresh output. Independent probe: an 8000-deep input candidate left byte-unchanged.
- Normal numeric behavior byte-identical — confirmed. All 384 previously-passing tests unchanged and green; AS-1/AS-2/AS-3/AS-4/AS-5 assertions untouched.

## Contract-freeness at 14ae88cc
Imports now: __future__ annotations, json, math, enum.Enum, typing.Any + ._json_safety._json_safe, .constants.NOT_VERIFIED_DISCLAIMER, .derive — no `copy`, no forbidden sibling. Only residual `copy` token is in an explanatory comment (line 336). Contract-freeness tighter than before (one fewer stdlib import). Shared sanitizer still used, no re-duplication.

## Steps independently executed
1. `git rev-parse HEAD` → 14ae88cc; `git diff --numstat bbf3267f..14ae88cc` → only the 2 expected files.
2. Read the full production diff + the 4 new deep-nesting tests (600/5000-deep dict+list, parametrized).
3. grep `copy.`/`deepcopy`/`import copy` in breakeven.py → none functional.
4. `python -m pytest tests/scenario -q` → 388 passed in 1.30s (384 + 4 new; 0 regression).
5. Independent 8000-deep probe with mixed domain `[<8000-deep dict>, 0.5, 0.9, 1.0]`: no RecursionError; threshold_kind=FOUND, candidate_count=4, derivable_count=3 (deep candidate typed not-derivable, bucketed after finite numerics); max_depth marker present; normal crossing honest bracket 0.5→0.9 meets_target_ascending; json.dumps(allow_nan=False) did not raise; byte-identical run-to-run; deep input unmutated.

## Reviewer conclusion
The single security/robustness fix at 14ae88cc removes a redundant recursive copy.deepcopy whose only effect was to overflow the recursion limit on deeply-nested candidates. The replacement builds the assumption echo directly from the already-fresh, depth-bounded `_json_safe(candidate)` output; derive consumes assumptions read-only, so no new aliasing or mutation. All previously-verified properties (honest grid-bracket crossing, monotonicity-honest multi-crossing detection, never-Verified lineage, cap-verbatim transport, strict-JSON-safety, contract-freeness) unchanged and re-confirmed; contract-freeness marginally tighter. Suite green at 388/388 (0 regression) with 4 new deep-nesting regression guards + an independent 8000-deep probe. **G1 PASS still holds at 14ae88cc — VERDICT: PASS.** No defects, no rework; the three prior LOW observations unchanged and non-blocking.
