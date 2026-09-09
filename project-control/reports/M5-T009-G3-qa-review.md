# M5-T009 — G3 QA Review (independent)

- **Gate:** G3 (QA / behavior-neutral regression / adequacy / mutation) — **Verdict:** PASS
- **Reviewer:** qa-engineer (independent; ≠ producer). Reviewed SHA `3b298474` (parent `bacb24a7`).

## Reproduction (counts match)
`pytest services/api/tests/scenario -q` → **252 passed**; `test_json_safety.py` → **30**; frozen
`test_scenario_ranking.py + test_scenario_sensitivity.py` → **98** (49+49, unchanged). 0 regression.
**Empty-diff proof:** `git diff bacb24a7..3b298474 -- <the two frozen test files>` → EMPTY (behavior-neutral
oracle intact). Change touches only allowed paths (AS-7).

## Adequacy of the 30 new tests
Extracted surface now DIRECTLY unit-covered (was only reachable via consumers): scalar repr, key token,
mapping `#N` de-collision, unsafe markers (nan/inf/negative/overflow/unsupported), bounded repr, tuple→list.
Single source of truth proven by object identity: `test_shared_module_is_the_single_source_of_truth` asserts
`ranking._json_safe is _json_safe` and `sensitivity._json_safe is _json_safe`; grep confirms zero residual
defs in either consumer (AS-2). L1 both consumers (Lock/generator → typed marker, ranked last / not-derivable,
no raise). L2: cycle (list/dict/mutual), DAG-not-false-cycle, max_depth marker, fixed-constant bound
(raises the recursion limit 4× — bound doesn't move).

## CRITICAL L2 subtlety — downstream json.dumps depth safety (the exact prior-revision hazard) — COVERED
`test_pathologically_deep_value_is_bounded_to_marker_and_json_dumps_stays_safe`: 5000-level input → sanitizer
does not raise (iterative), output bounded to 500 with `max_depth` marker, then `json.dumps(result,
allow_nan=False)` on the WHOLE output does not raise. Confirmed LOAD-BEARING: with the bound monkeypatched
away, json.dumps of the unbounded 5000-deep output RecursionErrors → the test would FAIL. Real teeth.

## Mutation sense-check (empirical, scratch OUTSIDE repo)
Raw deep json.dumps: 900-deep OK, 1000-deep RecursionError → the 500 bound sits safely below the edge.
Depth bound load-bearing (above). Cycle→marker; DAG both slots rendered equal (no false cycle). Extraction
faithfulness: parent's in-module sanitizer vs new module logic-identical (same constants 120/256, same prefix);
only `_json_safe` changed recursion→stack, equivalent for acyclic in-bound + ADDS safe behavior only.

## Non-blocking notes
NB-1: whole-change net production SLOC +~80 (consumers −239, L2 machinery added) — AS-6's testable clause
(net reduction across ranking.py+sensitivity.py = **−239**) holds; softer objective #6 not literal at whole-change
level. NB-2: reproduced on Python 3.11.9 (repo CI targets 3.12; scenario modules use no 3.12-only syntax).
NB-3: cosmetic report file-size off-by-one (trailing newline). None are functional defects.
