# M5-T005 Producer Report — Deterministic practical-usable-range derivation

- **Task:** M5-T005 — Deterministic practical-usable-range derivation from explicit typed assumptions (contract-free service function).
- **Producer agent:** scenario-optimization-engineer (persistent-local-21).
- **Branch:** `task/M5-T005-derive-range`.
- **Submission SHA:** `f08a19339ab8c2c335f4252a60d443794ab66dfb`. The producer does not commit; commits and gate transitions are the orchestrator's (ADR-005). `derive.py` and `test_scenario_derive.py` are therefore **untracked** in the working tree at this SHA and are committed by the orchestrator at the gate — nothing in this report should be read as asserting the report or those files are already committed.
- **Directive regime:** D-038 (ALL).

## This checkpoint — premature-underflow fix

**Defect.** The endpoint was computed as `product = f1·f2·…` (a standalone factor
product) and then `endpoint = cap_float · product`. For extreme factors the *standalone*
product underflows to `0.0` **before** the cap is applied — e.g. `1e-162 · 1e-162 = 1e-324`
flushes to `0.0`, so `endpoint = 15000 · 0.0 = 0.0` was reported as a **successful zero**,
even though `15000 · 1e-162 · 1e-162 ≈ 1.5e-320` is a representable subnormal.

**Fix (surgical; behavior of every non-underflow case is unchanged).** The naive
`cap · product` is still computed first, so every already-covered case keeps its exact,
previously-verified arithmetic. **Only when that naive endpoint is `0.0`** is the endpoint
recomputed by *folding the cap into the running product* (`endpoint = cap; endpoint *=
factor …`), so an intermediate never underflows prematurely and a still-representable
subnormal survives. If the folded endpoint is **still `0.0`** — the cap and every factor
are strictly positive, so the true result is a positive value that is genuinely
unrepresentable — the function returns a typed `not_derivable` outcome with an explicit
reason instead of a silently-successful zero. `factor_product` continues to report the
declared factors' product (it may itself be `0.0` when that standalone product underflows;
the endpoint no longer depends on it).

Canonical-cap transport is unchanged: `canonical_cap_sq_ft` and the no-factor endpoints
still carry the ORIGINAL cap value/type (`cap_raw`); only the arithmetic uses the separate
`cap_float` view. Outcomes remain deterministic.

### Changed arithmetic block (`derive.py`)

```python
    # Endpoints: cap x product(factors); cap VERBATIM when no factor applied.
    if factor_values:
        # factor_product is the product of the declared factors, for provenance. For
        # extreme factors this standalone product can itself underflow to 0.0.
        product = 1.0
        for factor in factor_values:
            product *= factor
        factor_product = product

        # Arithmetic uses the SEPARATE float view; the transported cap (cap_raw) stays
        # exact. The naive `cap x product` can flush a STILL-REPRESENTABLE result to
        # zero when the standalone product underflowed first (e.g. cap x 1e-162 x
        # 1e-162 is a subnormal ~1.5e-320, but 1e-162 x 1e-162 already underflowed to
        # 0.0). Only when that happens, recompute by folding the cap into the running
        # product so no intermediate underflows prematurely; every non-underflow
        # outcome keeps its exact, already-verified arithmetic unchanged.
        endpoint = cap_float * product
        if endpoint == 0.0:
            endpoint = cap_float
            for factor in factor_values:
                endpoint *= factor
        if not math.isfinite(endpoint) or endpoint < 0.0:
            return _invalid_assumption(
                scenario_document,
                (
                    "FAIL-CLOSED: derived endpoint was non-finite or negative; "
                    "no range is derived."
                ),
                cap_raw,
            )
        if endpoint == 0.0:
            # cap and every factor are strictly positive, so the true result is a
            # positive value; if it still underflows to 0.0 folded, it is genuinely
            # unrepresentable -> report that explicitly, never a successful zero.
            return _not_derivable(
                scenario_document,
                (
                    "NOT DERIVABLE: the derived practical-usable-range is a positive "
                    "value too small to represent as a nonzero double (arithmetic "
                    "underflow); no zero range is fabricated and the canonical cap is "
                    "untouched."
                ),
                cap_raw,
            )
    else:
        # No factor -> the cap VERBATIM (original type), so no hidden default AND no
        # silent int->float precision loss can appear.
        endpoint = cap_raw
        factor_product = 1.0
```

### New regression tests (`test_scenario_derive.py`)

```python
def test_rt6_tiny_factors_do_not_prematurely_underflow_to_zero():
    """RT-6: cap=15000 x two 1e-162 factors -> ~1.5e-320. The standalone factor
    product (1e-324) underflows to 0.0, but folding the cap into the running product
    keeps the endpoint a representable positive subnormal, never a silent zero."""
    document = _preliminary_document()
    assert document["draft_zoning_floor_area_cap_sq_ft"] == 15000.0
    document["assumptions"] = [
        _factor("utilization_factor", 1e-162),
        _factor("efficiency_ratio", 1e-162),
    ]

    derived = derive_practical_usable_range(document)
    range_ = derived["practical_usable_range"]

    assert derived["derivable"] is True
    assert derived["derived_kind"] == DerivedRangeKind.DERIVED
    # The standalone factor product underflowed to 0.0 ...
    assert derived["factor_product"] == 0.0
    # ... yet the endpoint is a positive, representable subnormal ~1.5e-320.
    assert range_["min"] == range_["point"] == range_["max"]
    assert range_["point"] > 0.0
    assert range_["point"] == 15000.0 * 1e-162 * 1e-162
    assert range_["point"] == pytest.approx(1.5e-320, rel=1e-2)
    # strict-JSON safe: no NaN / Inf / negative anywhere.
    for number in _all_numbers(json.loads(json.dumps(derived, allow_nan=False))):
        assert math.isfinite(number) and number >= 0


def test_rt7_genuinely_unrepresentable_product_is_not_a_successful_zero():
    """RT-7: cap=15000 x two 1e-170 factors -> ~1.5e-336, which underflows to 0.0
    even with the cap folded in. The true result is positive, so it is reported as an
    explicit typed 'not derivable', never a successful zero range."""
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    # Guard: the endpoint really does underflow to 0.0 even folded.
    assert cap * 1e-170 * 1e-170 == 0.0
    document["assumptions"] = [
        _factor("utilization_factor", 1e-170),
        _factor("efficiency_ratio", 1e-170),
    ]

    derived = derive_practical_usable_range(document)

    assert derived["derivable"] is False
    assert derived["derived_kind"] == DerivedRangeKind.NOT_DERIVABLE
    assert derived["practical_usable_range"] is None  # no zero range fabricated
    assert derived["not_derivable_reason"], "an explicit reason is named"
    # Canonical cap transported verbatim + untouched.
    assert derived["canonical_cap_sq_ft"] == cap == 15000.0
    assert document["draft_zoning_floor_area_cap_sq_ft"] == 15000.0
```

## What the module does (unchanged design)

Pure, deterministic, OFFLINE `derive_practical_usable_range(scenario_document)` in
`services/api/app/scenario/derive.py`, exported through
`services/api/app/scenario/__init__.py`. It derives an ILLUSTRATIVE
practical-usable-range `{min, point, max}` from a scenario document PLUS its
explicitly-declared typed assumptions, filling the Compare UI's currently-empty
practical-usable-range with an honest, explicit-assumption-only figure.

- **Canonical cap transported verbatim in every outcome.** Every outcome (derived,
  not-derivable, invalid-assumption) carries `canonical_cap_sq_ft` as the ORIGINAL
  `draft_zoning_floor_area_cap_sq_ft` value with its original type (`cap_raw`); the derived
  range never replaces it. A separate `cap_float` view is used for arithmetic only, so an
  integer cap — including one larger than 2⁵³ — is preserved exactly.
- **Endpoints = cap × Π(declared factors)**, computed underflow-safely (above). Recognized
  reduction factors are the closed set `{utilization_factor, efficiency_ratio}`, each in
  `(0, 1]`. With NO declared factor the endpoints are the cap VERBATIM. `min == point ==
  max` — a point estimate; no uncertainty spread is invented.
- **Unrecognized declared assumptions** are surfaced in `unapplied_assumptions` (never
  silently dropped) and NEVER applied.
- **Fail-closed** (typed `invalid_assumption`, no range, cap untouched) on any recognized
  factor that is NaN / ±Inf / negative / zero / `> 1` / non-numeric / bool / absent, on a
  malformed `assumptions` container, and on a non-dictionary entry.
- **Not derivable** (typed `not_derivable`, no range, no fabricated number) when there is
  no positive canonical cap, and now also when the true positive result underflows to an
  unrepresentable value.
- **Never Verified — enforced on every outcome** via `_bounded_coverage_status`;
  `needs_review=True` and `not_verified_disclaimer` preserved. The `DERIVED_RANGE_LABEL`
  states the figure is ILLUSTRATIVE / DERIVED and NOT gross/net/sellable/feasible floor
  area and NOT a buildable envelope.
- **Read-only / contract-free.** The scenario document is consumed READ-ONLY (re-validates
  unchanged). No canonical schema or `builder.py`/`models.py`/`constants.py`/`contract.py`
  edited. The derived object is a NEW, separate shape; factor entries are fresh copies.

## Files changed (scope confined to allowed_paths)

- `services/api/app/scenario/derive.py` — underflow-safe endpoint arithmetic + explicit
  unrepresentable-result outcome; docstrings updated to match.
- `services/api/app/scenario/__init__.py` — unchanged this checkpoint (exports the
  function, label, recognized-factor set, and `DerivedRangeKind`).
- `services/api/tests/scenario/test_scenario_derive.py` — RT-6/RT-7 underflow regression
  added; verbose RT-1..RT-5 docstrings compacted (no assertion changed).
- `project-control/reports/M5-T005-producer-report.md` — this report.

No forbidden path touched (`packages/contracts/**`, `builder.py`, `models.py`,
`constants.py`, `contract.py`, profile/rules/spatial/api, `apps/web/**`, `tools/**`).

## Acceptance-scenario → test mapping

| AS/RT | Requirement | Test(s) |
|----|-------------|---------|
| AS-1 | raw-cap passthrough, no hidden default; cap byte-identical | `test_as1_no_assumptions_range_equals_raw_cap_no_hidden_default` |
| AS-2 | explicit-factor derivation (cap × factors), cap transported verbatim | `test_as2_single_explicit_factor_scales_the_cap`, `test_as2_multiple_factors_multiply_deterministically`, `test_as2_unrecognized_assumption_is_surfaced_but_not_applied` |
| AS-3 | fail-closed on NaN/Inf/negative/zero/non-numeric/out-of-domain; no partial range; cap never mutated | `test_as3_bad_factor_fails_closed_no_partial_range` (10 params) |
| AS-4 | no-cap document → typed not-derivable, visible reason, no fabricated number | `test_as4_no_cap_document_is_not_derivable` (3 factories), `test_as4_degenerate_empty_document_is_not_derivable_not_crash` |
| AS-5 | determinism: byte-identical output; order-independent | `test_as5_identical_input_yields_byte_identical_output` (4 params), `test_as5_factor_order_does_not_change_output` |
| AS-6 | never-Verified; honest labelling; needs_review + disclaimer lineage | `test_as6_derived_is_never_verified_and_honestly_labelled` (2 params) |
| AS-7 | contract-free, read-only, re-validates unchanged, offline | `test_as7_input_consumed_read_only_and_revalidates_unchanged`, `test_as7_derived_object_does_not_alias_input_assumptions`, `test_recognized_factor_types_are_the_documented_closed_set` |
| RT-1 | integer cap serialized verbatim (no silent int→float coercion), no factor | `test_rt1_integer_cap_transported_and_serialized_verbatim_no_factor` |
| RT-2 | precision-sensitive integer cap (> 2⁵³) preserved exactly | `test_rt2_precision_sensitive_integer_cap_no_silent_precision_loss` |
| RT-3 | malformed `assumptions` container (non-list) fails closed, cap verbatim | `test_rt3_malformed_assumptions_container_fails_closed` (5 params) |
| RT-4 | non-dictionary assumption entry fails closed, no partial application | `test_rt4_non_dict_assumption_entry_fails_closed` (6 params) |
| RT-5 | incoming `verified` coverage capped to `conditional` on success AND failure | `test_rt5_incoming_verified_coverage_capped_on_successful_outcome` (3 params), `..._on_not_derivable_outcome`, `..._on_invalid_assumption_outcome` |
| RT-6 | tiny factors (cap=15000 × two 1e-162) → positive subnormal ~1.5e-320, no premature underflow to zero | `test_rt6_tiny_factors_do_not_prematurely_underflow_to_zero` |
| RT-7 | genuinely unrepresentable positive result (cap=15000 × two 1e-170) → typed not-derivable, never a successful zero | `test_rt7_genuinely_unrepresentable_product_is_not_a_successful_zero` |

## Evidence — documented test command

Command (exact, packet-documented): `python -m pytest services/api/tests/scenario`

```
platform win32 -- Python 3.11.9, pytest-8.4.2, pluggy-1.6.0
rootdir: C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t005\services\api
configfile: pyproject.toml
plugins: anyio-4.10.0, beartype-0.2.0, cov-6.0.0
collected 102 items

services\api\tests\scenario\test_scenario_contract.py .................. (23)
services\api\tests\scenario\test_scenario_derive.py ................................................ (48)
services\api\tests\scenario\test_scenario_foundation.py ............................... (31)

============================= 102 passed in 0.72s ==============================
```

102 scenario tests pass (48 derive tests = the AS-1..AS-7 pack + the RT-1..RT-7 regression
cases, up from 100/46 before this checkpoint; 54 pre-existing contract/foundation tests,
none broken). Offline: no Supabase, no Geoclient, no network — a pure function over
fixtures. The targeted `-k "rt6 or rt7"` variant is not a packet-documented command, so it
was held by the broker and not run; the full documented run above (collection 100→102)
confirms both new tests were collected and passed.

## Notes for the gate

- `derive.py` is **396 lines** (up from 363; the endpoint block and two docstring bullets),
  single responsibility (one derivation + its guards), comfortably under the modularity
  warn threshold (600). The modularity checker is not a packet-documented command, so it
  was not run under the tool-discipline constraint; the size/cohesion is stated here for
  the reviewer.
- Not a new legal rule (pure derived math over an already-surfaced draft cap), so not
  G6-acceptance-blocked; coverage tops out at `conditional`.
