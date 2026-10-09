# M5-T009 — G1 Code Review (independent)

- **Gate:** G1 (code / correctness / behavior-neutrality / modularity) — **Verdict:** PASS
- **Reviewer:** code-reviewer (independent; ≠ producer). Reviewed SHA `3b298474` (parent `bacb24a7`).

## Priority aliasing check (flagged by an earlier reviewer) — RESOLVED, benign
Pre-change sensitivity.py used TWO independent `copy.deepcopy(tried)`; refactor uses one shared `tried_echo`
assigned to both `value` (sensitivity.py:368) and `components["tried_value"]` (:346). Benign: the entire core
dict is passed through a single `_json_safe(...)` (sensitivity.py:364), which builds FRESH containers at every
position with a PATH-SCOPED ancestor set (_json_safety.py:283-307) — the two fields sit at non-overlapping
traversal paths, so each renders to an independent fresh container (no two-field alias, no false cycle).
Probe: `out["value"] is out["components"]["tried_value"]` → False; output never aliases input; mutating one
field does not affect the other; input dict byte-unchanged. No aliasing/mutation hazard.

## Behavior-neutrality — byte-identical
Helpers (_bounded_repr/_safe_scalar_repr/_unsafe_marker/_unsafe_key_token/_safe_key) byte-identical to the
deleted copies; scalar branch extracted verbatim; `_json_safe` rewritten recursive→iterative (the L2 change).
25-case differential vs a reference of the OLD recursive logic → byte-identical. The 98 forbidden-file tests
pass unchanged. The ONLY new outputs are ones the old sanitizer could not produce (cycle → old raised
RecursionError; depth>500 → old raised near ~480) — never a previously-successful output.

## L1 / L2 — correct, deterministic, both consumers
L1: non-deepcopyable value (Lock/generator/__deepcopy__-raises) → typed marker, no raise, in BOTH
ranking (`_build_candidate` L1 block :288-311) and sensitivity (`_build_point`). L2: self-ref list/dict →
`cycle` marker; 5000-deep → `max_depth` marker at exactly depth 500 with json.dumps(allow_nan=False)
succeeding; shared-but-acyclic DAG renders in full (no false cycle); `_MAX_JSON_SAFE_DEPTH=500` a fixed
constant (no sys import).

## Scope / modularity
`git diff --name-status bacb24a7 3b298474` = exactly the 5 allowed files; forbidden test files + boundary
files (derive/__init__/builder/models/constants/contract, packages/contracts/**) EMPTY diff. Public API of
both consumers unchanged (`ranking._json_safe` still resolves via re-import). `modularity_check --check` →
failures 0; no warning on any scenario file. `_json_safety.py` = 318 lines; both consumers smaller.

## Reproduced
`pytest services/api/tests/scenario -q` → 252 passed; `pytest test_scenario_ranking.py test_scenario_sensitivity.py -q` → 98 passed (unchanged).

## Non-blocking transparency note
Raw production SLOC is net **+77** (364 ins / 287 del across the 3 scenario files) — NOT a strict reduction,
because the same commit bundles the required L1/L2 hardening (iterative traversal, cycle detection, max_depth
bound) + provenance docstrings with the de-dup. The de-dup objective (AS-6 single source of truth) is
genuinely met: 7 sanitizer defs now have ONE definition site, ZERO in either consumer. No blocking defects.
