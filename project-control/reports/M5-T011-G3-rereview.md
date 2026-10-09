# M5-T011 — G3 QA DELTA RE-ATTESTATION (verbatim reviewer return) — PASS

Reviewer: **qa-engineer** (independent ≠ producer). Prior PASS at `bbf3267f` (M5-T011-G3.md); re-attested at `14ae88cc82d4630b8f9d9c22b2ca8857532c48f4` after the G5 security fix. Content verified by blob hash (breakeven.py `beef0ffd…`, test `a7d38793…`, __init__.py `0f188f11…` unchanged). Transport entity-decoding applied.

---

# GATE REPORT (DELTA RE-ATTESTATION) — M5-T011 at reviewed SHA 14ae88cc

**Reviewer:** qa-engineer (independent; NOT the producer). **Prior PASS:** bbf3267f. **This attestation:** 14ae88cc (candidate HEAD, ctl24).

`git diff --stat bbf3267f 14ae88cc -- services/api` = exactly 2 files (breakeven.py, test file). ctl24 working-tree files hash-match the 14ae88cc blobs (no drift).

## VERDICT: PASS

## Delta reviewed
- Source (`_build_candidate`): removed `import copy`; `echo = copy.deepcopy(generated)` replaced by direct construction from the fresh `_json_safe(candidate)` output — removes the sole recursive, interpreter-stack-dependent path. Verified the accepted-and-frozen `_json_safety.py` (M5-T009, forbidden path, untouched) walks with an explicit heap stack (not native recursion) and bounds nesting to `_MAX_JSON_SAFE_DEPTH=500`, substituting a typed `max_depth` marker past that — so `safe_value` handed to `derive` is already depth-bounded and never overflows.
- Test: added `test_as5_deeply_nested_candidate_is_bounded_and_json_safe` (4 params: dict & list nested 600 and 5000 deep).

## Reproduced (frozen 14ae88cc, Python 3.11.9 / pytest 8.4.2)
- `python -m pytest tests/scenario -q` → 388 passed (+4 over prior 384). 0 regressions.
- `python -m pytest tests/scenario/test_scenario_breakeven.py -q` → 65 passed (61 prior + 4 new).
- New test verbose: all 4 params PASS (dict_600, list_600, dict_5000, list_5000).
- `python tools/modularity_check.py --check` → failures 0; warnings 15 (breakeven.py soft review_signal).

## New-test adequacy (all three criteria)
- Typed marker / never-raise (AS-4): asserts threshold_kind in _SCANNED_KINDS, candidate_count==2, derivable_count==1, one typed not-derivable row with non-empty not_derivable_reason and metric_value is None.
- json.dumps(allow_nan=False) never raises (AS-5): runs _strict_json_safe(result) + explicit json.dumps(allow_nan=False); asserts "max_depth"/"unsafe_value_removed" appear (over-deep candidate bounded, not descended into).
- Determinism: asserts serialized == json.dumps(again, allow_nan=False) on a second independent build.

## RED→GREEN proof (in-process; no tracked file mutated)
- GREEN (frozen fix): `find_scenario_threshold(doc, VAR, 13000, [nested_dict(600), 0.9])` → target_already_met, candidate_count 2, derivable_count 1.
- RED (removed copy.deepcopy re-introduced): the same call raises RecursionError that escapes find_scenario_threshold — the new test genuinely fails without the fix. Fix is load-bearing, not test theater.

## Prior findings — carry-over
- AS→test mapping: still holds (no prior test removed/weakened; delta additive + redundant-copy removal). 384 prior tests still pass.
- Mutation-sensitivity (a/b/c/d1/e = CAUGHT; d2 boundary = MISSED): unchanged — the five mutation-target lines are present verbatim in functions the delta did not touch.

## Open LOW findings (none blocking)
- LOW-1 (original, STILL OPEN): the non_monotonic boundary is pinned only at 1 crossing (False) and 3 crossings (True); a `>=2`→`>=3` mutation still survives (no 2-crossing test). The rework addressed the distinct RecursionError item, NOT this. My LOW-1 remains open and need not block.
- LOW-2 (advisory): breakeven.py grew ~9 lines (~785); single cohesive responsibility, modularity review_signal warning (not a failure).
- LOW-3 (very low): AS-3 "verified" absence uses exact full-string membership; meaningful never-Verified paths covered by coverage-status capping + _coverage_values.

**Requested gate result: G3 = PASS at 14ae88cc** (LOW-1/LOW-2/LOW-3 non-blocking).
