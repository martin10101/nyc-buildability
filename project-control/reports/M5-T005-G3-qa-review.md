# G3 QA GATE REPORT — M5-T005 (practical-usable-range derivation)

_Reviewer-returned content, preserved verbatim (transport entity-decoding only). Reviewer: qa-engineer (independent, read-only, producer ≠ reviewer)._

**Verdict: PASS**

**Reviewed identity (confirmed):** branch `task/M5-T005-derive-range`, worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t005`, `HEAD == cdd7165d3fef6b43ca72f48f6bd5427cce0e2103` ✓ (matches). Working tree clean.

**Files under test:** `services/api/app/scenario/derive.py` (new, 395 lines), `services/api/tests/scenario/test_scenario_derive.py` (new, 607 lines). Commit touches exactly 4 files: producer report, `app/scenario/__init__.py` (+14, facade export only), `derive.py`, and the test file. No edits to builder/models/constants/contract.

## Reproduced test counts

- `python -m pytest tests/scenario -q` → **102 passed, 0 failed** (0.47s).
- `python -m pytest tests/scenario/test_scenario_derive.py -q` → **48 passed, 0 failed** (0.30s); 48 collected.

Note on the packet's "expected 54": the scenario dir now holds `test_scenario_contract.py` + `test_scenario_foundation.py` (pre-existing = 54) plus the new `test_scenario_derive.py` (48) = 102. The "54" was the pre-existing count; the packet expectation is stale, not a defect — the new pack is 48 and the full suite is green.

## Per-acceptance-scenario coverage

| AS | Judgment | Evidence |
|----|----------|----------|
| AS-1 raw-cap passthrough | **Covered** | `test_as1...` asserts min==point==max==cap==15000.0, `factor_product==1.0`, `applied_factors==[]`, `json.dumps(point)==json.dumps(cap)` (byte-identical), canonical cap byte-identical, input cap untouched. |
| AS-2 explicit-factor derivation | **Covered** | single (0.8→12000.0), multiple (0.8×0.5→6000.0), unrecognized-surfaced-not-applied; cap transported verbatim (==15000), never replaced. |
| AS-3 fail-closed on bad factors | **Covered** | Parametrized NaN/+Inf/−Inf/negative/zero(int+float)/out-of-domain(1.5)/non-numeric string/bool/None → `derivable False`, no partial range, reason present, `json.dumps(allow_nan=False)` + every number finite & ≥0, cap untouched. |
| AS-4 no-cap document | **Covered** | 3 no-cap rule-evals (no_scenario/missing-lot-area, unsupported, conflict) + degenerate `{}` → not_derivable, range None, reason named, canonical_cap None, no fabricated 15000. |
| AS-5 determinism | **Covered** | Parametrized byte-identical `json.dumps` equality across 4 assumption shapes + factor-order independence. |
| AS-6 never-Verified + honest labelling | **Covered** | No `verified` in any coverage value or string value; `coverage_status=='conditional'`; needs_review True; disclaimer preserved; label is illustrative/derived, explicitly NOT gross/net/sellable/feasible/buildable; range keys locked to the 6 expected. |
| AS-7 contract-free + read-only + offline | **Covered** | Input byte-unchanged + re-validates against canonical schema, derived is a separate object with no cap key, no-alias mutation test. Offline independently verified (no network imports in scenario package; `_support` reads a local committed fixture). Contract-free confirmed by diff. |

## Reviewer-flagged underflow edge case — fully covered (no gap)

- **RT-6** (`test_rt6_tiny_factors_do_not_prematurely_underflow_to_zero`): cap × two `1e-162` factors. Asserts `derivable True`, `factor_product==0.0` (standalone product underflowed), and endpoint `> 0.0` == a representable subnormal ~1.5e-320. Independently reproduced: standalone `1e-162*1e-162 == 0.0` and naive `cap*prod == 0.0`, but the folded running product yields `1.5e-320` (finite, positive). So a subnormal-but-representable result is NOT reported as a successful 0.0.
- **RT-7** (`test_rt7_genuinely_unrepresentable_product_is_not_a_successful_zero`): cap × two `1e-170` factors. Reproduced `cap*1e-170*1e-170 == 0.0` even folded → asserts `derivable False`, `not_derivable`, `practical_usable_range is None`. A genuinely-unrepresentable positive returns not_derivable, never a zero range.

Both cases are present and load-bearing.

## Boundaries actually asserted (mutation-verified, not smoke)

Copied `derive.py` into scratchpad (read-only; frozen worktree untouched) and confirmed each key assertion catches its mutant:
- Remove underflow-fold → RT-6 flips to `derivable False` — **caught**.
- Hidden 0.85 default when no factor → AS-1 point becomes 12750.0 — **caught**.
- Never-Verified cap removed → RT-5 sees `verified` — **caught**.
- Silently skip a non-dict entry → RT-4 sees `derivable True, applied=1` — **caught**.

## Regression / other checks

- Modularity: `python tools/modularity_check.py --check` → **0 failures**, 14 warnings, none on the M5-T005 files.
- RT-1/RT-2 additionally prove integer and >2^53 caps are transported/serialized verbatim (no silent int→float coercion); RT-3/RT-4 prove malformed containers and non-dict entries fail closed with no partial application.

## Minor observations (non-blocking, not defects)

1. The defensive branch `if not math.isfinite(endpoint) or endpoint < 0.0` (derive.py:315-323) is unreachable through the public API (cap is positive-finite, factors are in (0,1], so the product is in (0,1] and the endpoint is always positive-finite). Belt-and-suspenders code; untested but acceptable.
2. No explicit test of the valid inclusive upper boundary `factor == 1.0` (accepted) — the invalid `>1` (1.5) and `0.0` boundaries are covered. Completeness nit only.
3. Factor-applied path with an integer cap yields a float endpoint (expected — arithmetic) while `canonical_cap_sq_ft` transports the int via the same `cap_raw` path RT-1/RT-2 verify; not exercised as a combined case, but the transport path is identical.

**Conclusion:** All 7 acceptance scenarios are covered with real boundary assertions (mutation-confirmed load-bearing), the reviewer-flagged underflow edge is fully covered by RT-6/RT-7 with independently reproduced math, offline/read-only/contract-free hold, and the suite reproduces green (102/102 dir; 48/48 pack). **PASS.**
