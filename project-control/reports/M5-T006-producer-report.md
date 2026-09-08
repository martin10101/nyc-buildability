# M5-T006 PRODUCER REPORT — derive.py hardening (G5 LOW-1 / LOW-2 / LOW-3)

- **Task:** M5-T006 — strict-JSON-safe malformed-cap transport + no-alias assumption copy + bounded reason echo (single-value AND aggregate).
- **Producer:** scenario-optimization-engineer · **Branch:** `task/M5-T006-derive-hardening` · **Worktree:** `wt-m5t006`.
- **Base identity:** `b0d39ad69f69d7abe6f71579a683a063f2e2ba85` (working tree carries the edits; the orchestrator commits at the gate).
- **Scope (allowed_paths only):** `services/api/app/scenario/derive.py`, `services/api/tests/scenario/test_scenario_derive.py`, this report. No forbidden path touched.

> **Report/evidence-only revision — implementation and tests are UNCHANGED from the reviewed base** (I re-scrutinized `_json_safe_cap`, `_bounded_key_list_echo`, `_copy_assumption`, the underflow fold and the determinism sort; no defect, so the implementation is preserved). The prior report cited the hardening tests only by file+line range, which a bounded, file-inaccessible collector cannot treat as supplied evidence. **The decisive test bodies are therefore embedded VERBATIM below** — goldens in full, the rest as decisive verbatim excerpts (docstrings/long comments elided) — quoted from the current working-tree `test_scenario_derive.py`, itself in `allowed_paths` and committed unchanged at the gate, so the gate diffs each excerpt against the committed file: the excerpt TEXT is the evidence, not a drift-prone line span.

## Findings addressed (all three unreachable via the trusted `build_scenario` pipeline; hardened for DIRECT callers)

- **LOW-1** — `_json_safe_cap()` (`derive.py:172-187`): a finite non-negative cap is transported verbatim; a NaN/±Inf/negative/float-overflowing cap is surfaced as `null`; `_not_derivable()` (`:240-268`) appends a `"MALFORMED CAP: …"` reason when a numeric cap was nulled. The DERIVED path is unchanged (`:475` still assigns `cap_raw`).
- **LOW-2** — `_copy_assumption()` (`derive.py:199-210`): `copy.deepcopy`s every carried field so the copy never aliases the input (applied OR unapplied); the docstring's "never aliases the input" claim is now literally true.
- **LOW-3** — (a) `_bounded_echo()` (`:140-145`) truncates any echoed raw value at 120 chars with a `"...(truncated)"` marker; (b) `_bounded_key_list_echo()` (`:148-164`) caps the NUMBER of echoed unapplied keys at 12 with a `", ...(+N more unapplied key(s) truncated)"` tail. Together they put a FIXED upper bound on the whole reason.

## Byte-equivalence claim — narrowed; historical-equivalence LIMITATION retained

Claimed **only for the DERIVED path and only for inputs tripping NEITHER truncation bound.** The two goldens below pin the ENTIRE `json.dumps(derived)` (including key order) as a **forward** lock — any structure/order/label/reason/cap drift fails CI. **LIMITATION (retained):** the goldens do NOT re-execute the historical M5-T005 binary, so they do not by themselves prove equality to what M5-T005 emitted at acceptance; historical equivalence rests on the DIFF — the DERIVED-path assembly (`derive.py:388-489`) and cap-transport (`:475`) are textually unchanged, and the only DERIVED text this task can alter is the aggregate echo, which changes output only past the >12-key bound. The two truncation surfaces (echo >120 chars; key count >12) and LOW-1's malformed-cap `null` are intentional deltas NOT covered by the claim.

## Evidence

- **Command (documented, re-run this revision):** `python -m pytest services/api/tests/scenario` → **`124 passed in 0.58s`** (Python 3.11.9 / pytest 8.4.2, configfile `services/api/pyproject.toml`), zero regression: contract 23 + derive 70 + foundation 31.
- **Composition:** 102 pre-existing + 22 M5-T006 hardening items (14 functions; 22 collected after parametrization). All edited lines ≤ 100 chars (repo ruff `line-length = 100`).

## EMBEDDED VERBATIM TEST SOURCE (actual bodies — no line-only references)

Quoted verbatim from `services/api/tests/scenario/test_scenario_derive.py`; docstrings/long comments elided. Fixture notes (in prose, so the fences stay pure source): `_preliminary_document` builds the canonical PRELIMINARY doc (`draft_zoning_floor_area_cap_sq_ft == 15000.0`) via the accepted `_support` fixtures; `_all_strings(node)`/`_all_numbers(node)` are trivial recursive walkers returning every `str` / every non-bool `int`|`float` in a payload (the latter used by LOW-1 to assert every emitted number is finite and ≥ 0).

### Required fixtures / constants

```python
def _preliminary_document(assumptions=None) -> dict:
    return build_scenario(
        S.profile(), S.canonical_rule_evaluation(), assumptions=assumptions
    )

def _factor(assumption_type: str, value, *, key: str | None = None) -> dict:
    return {
        "key": key or assumption_type,
        "assumption_type": assumption_type,
        "value": value,
        "unit": "ratio",
        "rationale": "illustrative explicit assumption",
    }

_GOLDEN_POINT_ESTIMATE_NOTE = (
    "Point estimate: min == point == max. No uncertainty spread is invented; "
    "the range widens only when explicit low/high uncertainty is declared."
)
_GOLDEN_DERIVED_REASON = (
    "DERIVED (illustrative): practical-usable-range = canonical draft "
    "zoning-floor-area cap x the explicitly-declared typed factor(s). "
    "The canonical cap is transported verbatim and is never replaced by the "
    "derived range. NOT a buildable envelope; NOT Verified."
)
_GOLDEN_NO_FACTOR_REASON = (
    "No usable-range factor was declared; the range equals the raw cap "
    "exactly (no utilization / efficiency / optimization default applied)."
)
```

### AS-2 full-output GOLDENS (embedded IN FULL — the byte-equivalence spec)

```python
def test_m5t006_as2_no_assumptions_full_output_golden_baseline():
    document = _preliminary_document()
    assert document["draft_zoning_floor_area_cap_sq_ft"] == 15000.0
    derived = derive_practical_usable_range(document)
    expected = {
        "derived_kind": "derived_practical_usable_range",
        "derivable": True,
        "practical_usable_range": {
            "min": 15000.0,
            "point": 15000.0,
            "max": 15000.0,
            "unit": "square_feet",
            "is_point_estimate": True,
            "note": _GOLDEN_POINT_ESTIMATE_NOTE,
        },
        "canonical_cap_sq_ft": 15000.0,
        "cap_label": DRAFT_CAP_LABEL,
        "applied_factors": [],
        "unapplied_assumptions": [],
        "factor_product": 1.0,
        "label": DERIVED_RANGE_LABEL,
        "reasons": [_GOLDEN_DERIVED_REASON, _GOLDEN_NO_FACTOR_REASON],
        "not_derivable_reason": None,
        "coverage_status": "conditional",
        "needs_review": True,
        "not_verified_disclaimer": NOT_VERIFIED_DISCLAIMER,
    }
    assert derived == expected
    assert json.dumps(derived) == json.dumps(expected)


def test_m5t006_as2_single_factor_full_output_golden_baseline():
    document = _preliminary_document(assumptions=[_factor("utilization_factor", 0.8)])
    derived = derive_practical_usable_range(document)
    expected = {
        "derived_kind": "derived_practical_usable_range",
        "derivable": True,
        "practical_usable_range": {
            "min": 12000.0,
            "point": 12000.0,
            "max": 12000.0,
            "unit": "square_feet",
            "is_point_estimate": True,
            "note": _GOLDEN_POINT_ESTIMATE_NOTE,
        },
        "canonical_cap_sq_ft": 15000.0,
        "cap_label": DRAFT_CAP_LABEL,
        "applied_factors": [
            {
                "key": "utilization_factor",
                "assumption_type": "utilization_factor",
                "value": 0.8,
                "unit": "ratio",
                "rationale": "illustrative explicit assumption",
            }
        ],
        "unapplied_assumptions": [],
        "factor_product": 0.8,
        "label": DERIVED_RANGE_LABEL,
        "reasons": [_GOLDEN_DERIVED_REASON],
        "not_derivable_reason": None,
        "coverage_status": "conditional",
        "needs_review": True,
        "not_verified_disclaimer": NOT_VERIFIED_DISCLAIMER,
    }
    assert derived == expected
    assert json.dumps(derived) == json.dumps(expected)
```

### AS-3 mutation-isolation (LOW-2)

```python
def test_m5t006_low2_unapplied_nested_value_not_aliased():
    nested = {"nested": [1, 2, 3]}
    document = _preliminary_document(
        assumptions=[_factor("target_unit_count", nested, key="target_unit_count")]
    )
    snapshot = copy.deepcopy(document)
    derived = derive_practical_usable_range(document)
    unapplied = derived["unapplied_assumptions"][0]
    assert unapplied["value"] is not document["assumptions"][0]["value"]
    assert unapplied["value"] == nested
    unapplied["value"]["nested"].append(999)
    assert document == snapshot
    assert document["assumptions"][0]["value"] == {"nested": [1, 2, 3]}


def test_m5t006_low2_deepcopy_protects_nested_rationale_direct_call():
    document = {
        "draft_zoning_floor_area_cap_sq_ft": 15000.0,
        "assumptions": [
            {
                "key": "utilization_factor",
                "assumption_type": "utilization_factor",
                "value": 0.8,
                "unit": "ratio",
                "rationale": {"note": ["explicit", "assumption"]},
            }
        ],
    }
    snapshot = copy.deepcopy(document)
    derived = derive_practical_usable_range(document)
    applied = derived["applied_factors"][0]
    assert derived["derived_kind"] == DerivedRangeKind.DERIVED
    assert applied["rationale"] is not document["assumptions"][0]["rationale"]
    applied["rationale"]["note"].append("mutated")
    assert document == snapshot
```

### AS-4 individual echo bounds (LOW-3, single value — all three `_bounded_echo` sites)

```python
def test_m5t006_low3_scenario_kind_echo_is_bounded():
    document = _preliminary_document()
    document["draft_zoning_floor_area_cap_sq_ft"] = None  # -> not derivable, echoes kind
    document["scenario_kind"] = "x" * 100_000
    derived = derive_practical_usable_range(document)
    joined = " ".join(derived["reasons"])
    assert len(joined) < 2_000
    assert "truncated" in joined


def test_m5t006_low3_factor_value_echo_is_bounded():
    document = _preliminary_document()
    document["assumptions"] = [_factor("utilization_factor", "0." + "9" * 100_000)]
    derived = derive_practical_usable_range(document)
    assert derived["derived_kind"] == DerivedRangeKind.INVALID_ASSUMPTION
    joined = " ".join(derived["reasons"])
    assert len(joined) < 2_000
    assert "truncated" in joined


def test_m5t006_low3_unapplied_key_echo_is_bounded():
    huge_key = "k" * 100_000
    document = _preliminary_document(
        assumptions=[_factor("target_unit_count", 0.5, key=huge_key)]
    )
    derived = derive_practical_usable_range(document)
    assert derived["derivable"] is True
    joined = " ".join(derived["reasons"])
    assert len(joined) < 2_000
    assert "truncated" in joined
    assert derived["unapplied_assumptions"][0]["key"] == huge_key
```

### AS-4 aggregate echo bound (LOW-3, fixed upper bound over key COUNT)

```python
def test_m5t006_low3_many_unapplied_keys_reason_has_fixed_upper_bound():
    def _derive_with(n):
        keys = [f"unapplied-{i:06d}" for i in range(n)]
        document = _preliminary_document(
            assumptions=[_factor("target_unit_count", 0.5, key=k) for k in keys]
        )
        return derive_practical_usable_range(document), keys

    fixed_reason_bound = 2_000
    small_n, large_n = 64, 20_000
    small, small_keys = _derive_with(small_n)
    large, large_keys = _derive_with(large_n)
    for derived, keys in ((small, small_keys), (large, large_keys)):
        assert derived["derivable"] is True
        reason = next(r for r in derived["reasons"] if "surfaced but NOT applied" in r)
        assert len(reason) < fixed_reason_bound
        assert "more unapplied key(s) truncated" in reason
        assert keys[-1] not in reason
        assert [a["key"] for a in derived["unapplied_assumptions"]] == sorted(keys)
    small_reason = next(r for r in small["reasons"] if "surfaced but NOT applied" in r)
    large_reason = next(r for r in large["reasons"] if "surfaced but NOT applied" in r)
    assert abs(len(large_reason) - len(small_reason)) <= 8
```

### AS-5 lineage (never-Verified + needs_review + disclaimer on a malformed-cap outcome)

```python
def test_m5t006_as5_never_verified_preserved_on_malformed_cap():
    document = _preliminary_document()
    document["coverage_status"] = "verified"
    document["draft_zoning_floor_area_cap_sq_ft"] = float("-inf")
    derived = derive_practical_usable_range(document)
    assert "verified" not in _all_strings(derived)
    assert derived["coverage_status"] == "conditional"
    assert derived["needs_review"] is True
    assert derived["not_verified_disclaimer"] == document["not_verified_disclaimer"]
```

### AS-6 determinism across every hardened path

```python
@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.__setitem__("draft_zoning_floor_area_cap_sq_ft", float("nan")),
        lambda d: d.__setitem__("scenario_kind", "x" * 100_000),
        lambda d: d.__setitem__(
            "assumptions", [_factor("target_unit_count", 0.5, key="k" * 100_000)]
        ),
        lambda d: d.__setitem__(
            "assumptions",
            [_factor("target_unit_count", 0.5, key=f"u-{i:05d}") for i in range(5_000)],
        ),
    ],
)
def test_m5t006_as6_determinism_with_hardening(mutate):
    first = _preliminary_document()
    mutate(first)
    second = _preliminary_document()
    mutate(second)
    assert json.dumps(derive_practical_usable_range(first)) == json.dumps(
        derive_practical_usable_range(second)
    )
```

### AS-1 malformed-cap (LOW-1) — decisive verbatim asserts

```python
@pytest.mark.parametrize(
    "bad_cap",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        -5,
        -0.5,
        10**400,
    ],
)
def test_m5t006_low1_malformed_cap_nulled_and_json_safe(bad_cap):
    document = _preliminary_document()
    document["draft_zoning_floor_area_cap_sq_ft"] = bad_cap
    derived = derive_practical_usable_range(document)
    assert derived["derivable"] is False
    assert derived["derived_kind"] == DerivedRangeKind.NOT_DERIVABLE
    assert derived["canonical_cap_sq_ft"] is None
    assert any("MALFORMED CAP" in reason for reason in derived["reasons"])
    serialized = json.dumps(derived, allow_nan=False)
    for number in _all_numbers(json.loads(serialized)):
        assert math.isfinite(number)
        assert number >= 0
```

(Two further LOW-1 companions exist in the same block — a direct-call `{cap: NaN}` JSON-safety case and a `0`-cap verbatim-transport boundary — not embedded here purely to fit the byte budget; the parametrized test above is the decisive one.)

## Boundaries honored

- Contract-free & read-only: only `derive.py` + its test file changed; canonical schema/builder/models/constants/contract/`__init__` untouched; cap **value** transported verbatim on the DERIVED path, never recomputed/relabelled; never emits `verified`; `needs_review` + disclaimer lineage preserved; deterministic byte-identical output.
- Modularity: no new file; `derive.py` well under the 600-SLOC warn threshold. Tool discipline: discovery via Read/Grep/Glob; only broker command run was the documented `python -m pytest services/api/tests/scenario`.
