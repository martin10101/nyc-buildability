# GATE REPORT — M5-T005 (G1 independent code review)

_Reviewer-returned content, preserved verbatim (transport entity-decoding only). Reviewer: code-reviewer (independent, read-only, producer ≠ reviewer)._

- **Task:** M5-T005 — Deterministic practical-usable-range derivation from explicit typed assumptions (contract-free service function)
- **Reviewed identity:** branch `task/M5-T005-derive-range` @ `cdd7165d3fef6b43ca72f48f6bd5427cce0e2103` (verified `git rev-parse HEAD` == cdd7165d; worktree clean, no porcelain output)
- **Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t005`
- **Reviewer:** read-only, producer ≠ reviewer
- **Verdict: PASS**

## Reproduced evidence

- `cd C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t005/services/api && python -m pytest tests/scenario -q` → **102 passed in 0.55s** (observed count).
  - Note on the "expect 54" in the task: 54 is the *pre-existing* contract+foundation subset (23 + 31). The suite now carries **48 new derive tests** on top → 102 total, all passing. `python -m pytest tests/scenario/test_scenario_derive.py -q` → **48 passed**. No regressions in the pre-existing 54.
- `git show --stat cdd7165d` and a diff scoped to forbidden paths confirm the commit touches only: `derive.py` (+395), `__init__.py` (+14), `test_scenario_derive.py` (+607), `M5-T005-producer-report.md` (+241). **builder.py / models.py / constants.py / contract.py / packages/contracts/** are untouched.
- `python tools/modularity_check.py --check` → **failures 0**; derive.py (395 lines, single responsibility) is not flagged.
- Independent behavioral harness (calling `derive_practical_usable_range` directly) reproduced every hard boundary — results inline below.

## Hard-boundary verification

1. **Contract-free** — PASS. Scoped diff proves only derive.py + __init__.py under `app/scenario/`; no canonical schema or contract module edited. `__init__.py` only *adds* exports (`DERIVED_RANGE_LABEL`, `RECOGNIZED_FACTOR_TYPES`, `DerivedRangeKind`, `derive_practical_usable_range`); no existing export changed.
2. **Cap transported verbatim, never up-labelled** — PASS. `cap_raw` (original value/type) is carried as `canonical_cap_sq_ft` on *every* outcome and is the endpoint verbatim when no factor applies; a separate `cap_float` view is used for arithmetic only. Independently confirmed an integer cap survives as `int` (not coerced `15000.0`), and RT-2 preserves `2**53+1` exactly. `DERIVED_RANGE_LABEL` (derive.py:71–77) explicitly negates gross/net/sellable/feasible/buildable and Verified; `coverage_status` can never be `verified` (derive.py:135–143), reproduced: incoming `VERIFIED` → `conditional`.
3. **No hidden default** — PASS. No assumptions ⇒ `endpoint = cap_raw` verbatim, `factor_product == 1.0`, `applied_factors == []` (derive.py:338–342). Reproduced directly.
4. **Fail-closed + underflow fix** — PASS. Malformed/non-finite/negative/zero/`>1`/non-numeric/bool factors, non-list `assumptions`, and non-dict entries all return a typed `invalid_assumption`/`not_derivable` with a visible reason, no crash, no NaN/Inf/negative (JSON `allow_nan=False` safe). The underflow fix (derive.py:295–337) is **correct for its safety goal**: the naive `cap_float * product` is computed first (all normal cases keep their prior arithmetic); only on an exact `0.0` is the endpoint recomputed by folding the cap into the running product (the multiplication order that keeps intermediates largest, since every factor ∈ (0,1]); if it is *still* `0.0` the true value is provably positive-but-unrepresentable and the function returns `not_derivable` — never a silent zero. Reproduced: cap=15000 × two `1e-162` → positive subnormal `1.5e-320` (derivable); cap=15000 × two `1e-170` → `not_derivable`, `practical_usable_range=None`, cap intact.
5. **Deterministic** — PASS. Applied factors + values are co-sorted by `(assumption_type, key)` and reasons/labels emit in fixed order; reproduced byte-identical JSON for reordered-but-equal inputs.

## Non-blocking observations (no rework required)

- **derive.py:301 / 389** `factor_product` can legitimately be `0.0` on a *successful* `DERIVED` outcome (RT-6) when the standalone factor product underflows even though the folded endpoint is a positive subnormal. This is documented and the endpoint (not `factor_product`) is authoritative, but a downstream consumer that reads `factor_product` instead of the endpoint could misread it. Provenance oddity only.
- **derive.py:159–187** `_invalid_assumption` reuses `_not_derivable`, so an `invalid_assumption` outcome also carries a populated `not_derivable_reason` field (in addition to `reasons`). Harmless naming overlap; both fields are visible and tested.
- **derive.py:310–312** The fold is triggered only when the naive endpoint is *exactly* `0.0`. If a standalone factor product underflows to a *nonzero subnormal* (not exactly 0.0), the naive — marginally less precise — path is retained. This never yields a silent zero, NaN, Inf, or sign error; it only affects deep-subnormal magnitudes reachable solely by factors far outside the realistic (0,1] zoning range. Consistent with the producer's stated scope ("every non-underflow case unchanged") and acceptable for an explicitly illustrative figure.
- **Test-count expectation:** the task's "expect 54" understates the current suite; actual is 102 (48 derive + 54 pre-existing). Flagged for transparency; not a defect.

## AI-boundary / provenance discipline

Deterministic code calculates; nothing is invented or up-labelled. Point estimate (`min==point==max`) with no fabricated uncertainty band; `needs_review=True` and `not_verified_disclaimer` lineage preserved on every outcome; not a new legal rule (illustrative math over an already-surfaced draft cap), so not G6-blocked. Code matches the producer report's claims (underflow block and RT-6/RT-7 tests are byte-consistent with the report excerpts).

**Recommended gate result: PASS.**
