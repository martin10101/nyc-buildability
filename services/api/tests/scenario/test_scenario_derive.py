"""Executable acceptance pack AS-1..AS-7 for the deterministic practical-usable-
range derivation (task M5-T005).

Offline and deterministic. Each test maps to exactly one acceptance scenario and
asserts the honest-labelling, no-hidden-default, fail-closed, and read-only
guarantees the packet requires. The derivation is exercised against real scenario
documents produced by ``build_scenario`` (the same shape the Compare UI consumes),
plus targeted malformed-assumption variants injected directly to prove derive's own
fail-closed guards.
"""

from __future__ import annotations

import copy
import json
import math

import pytest

from app.scenario import (
    DERIVED_RANGE_LABEL,
    NOT_VERIFIED_DISCLAIMER,
    RECOGNIZED_FACTOR_TYPES,
    DerivedRangeKind,
    build_scenario,
    derive_practical_usable_range,
    validate_scenario_document,
)

from . import _support as S


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _preliminary_document(assumptions=None) -> dict:
    """A real PRELIMINARY scenario document (canonical R5 cap = 15000.0), optionally
    carrying explicitly-declared typed assumptions recorded by the builder."""
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


def _coverage_values(node):
    """Every value stored under a 'coverage_status' key anywhere in a payload."""
    out = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "coverage_status" and isinstance(value, str):
                out.append(value)
            out.extend(_coverage_values(value))
    elif isinstance(node, list):
        for item in node:
            out.extend(_coverage_values(item))
    return out


def _all_strings(node):
    out = []
    if isinstance(node, dict):
        for value in node.values():
            out.extend(_all_strings(value))
    elif isinstance(node, list):
        for item in node:
            out.extend(_all_strings(item))
    elif isinstance(node, str):
        out.append(node)
    return out


def _all_numbers(node):
    out = []
    if isinstance(node, dict):
        for value in node.values():
            out.extend(_all_numbers(value))
    elif isinstance(node, list):
        for item in node:
            out.extend(_all_numbers(item))
    elif isinstance(node, int | float) and not isinstance(node, bool):
        out.append(node)
    return out


# ---------------------------------------------------------------------------
# AS-1 raw-cap passthrough: no assumptions -> range EQUALS the raw draft cap.
# ---------------------------------------------------------------------------


def test_as1_no_assumptions_range_equals_raw_cap_no_hidden_default():
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    assert cap == 15000.0
    assert document["assumptions"] == []

    derived = derive_practical_usable_range(document)

    assert derived["derivable"] is True
    assert derived["derived_kind"] == DerivedRangeKind.DERIVED
    range_ = derived["practical_usable_range"]

    # min == point == max == the RAW cap (no utilization/efficiency/optimization
    # factor silently applied).
    assert range_["min"] == range_["point"] == range_["max"] == cap == 15000.0
    assert derived["factor_product"] == 1.0
    assert derived["applied_factors"] == []

    # The endpoints are the cap VERBATIM (byte-identical), proving no hidden factor.
    assert json.dumps(range_["point"]) == json.dumps(cap)

    # The canonical cap is transported verbatim and byte-identical to the input.
    assert derived["canonical_cap_sq_ft"] == cap
    assert json.dumps(derived["canonical_cap_sq_ft"]) == json.dumps(cap)
    assert document["draft_zoning_floor_area_cap_sq_ft"] == 15000.0


# ---------------------------------------------------------------------------
# AS-2 explicit-factor derivation: range = canonical cap x declared factor(s).
# ---------------------------------------------------------------------------


def test_as2_single_explicit_factor_scales_the_cap():
    document = _preliminary_document(assumptions=[_factor("utilization_factor", 0.8)])
    cap = document["draft_zoning_floor_area_cap_sq_ft"]

    derived = derive_practical_usable_range(document)
    range_ = derived["practical_usable_range"]

    # Deterministic documented function of the CANONICAL cap x the declared factor.
    assert range_["point"] == cap * 0.8
    assert range_["point"] == 12000.0
    assert range_["min"] == range_["max"] == range_["point"]
    assert derived["factor_product"] == 0.8
    assert derived["applied_factors"][0]["assumption_type"] == "utilization_factor"

    # The canonical cap is transported VERBATIM and is NEVER replaced by the range.
    assert derived["canonical_cap_sq_ft"] == cap == 15000.0
    assert document["draft_zoning_floor_area_cap_sq_ft"] == 15000.0


def test_as2_multiple_factors_multiply_deterministically():
    document = _preliminary_document(
        assumptions=[
            _factor("utilization_factor", 0.8),
            _factor("efficiency_ratio", 0.5),
        ]
    )
    cap = document["draft_zoning_floor_area_cap_sq_ft"]

    derived = derive_practical_usable_range(document)
    range_ = derived["practical_usable_range"]

    assert derived["factor_product"] == 0.8 * 0.5
    assert range_["point"] == cap * (0.8 * 0.5) == 6000.0
    # Both factors surfaced; canonical cap untouched.
    assert {f["assumption_type"] for f in derived["applied_factors"]} == {
        "utilization_factor",
        "efficiency_ratio",
    }
    assert derived["canonical_cap_sq_ft"] == 15000.0


def test_as2_unrecognized_assumption_is_surfaced_but_not_applied():
    """An explicitly-declared assumption that is NOT a recognized usable-range
    factor is surfaced (never silently dropped) and NEVER applied to the range."""
    document = _preliminary_document(
        assumptions=[_factor("target_unit_count", 0.5, key="target_unit_count")]
    )
    cap = document["draft_zoning_floor_area_cap_sq_ft"]

    derived = derive_practical_usable_range(document)

    assert derived["factor_product"] == 1.0
    assert derived["practical_usable_range"]["point"] == cap  # unchanged by it
    assert derived["applied_factors"] == []
    assert [a["key"] for a in derived["unapplied_assumptions"]] == ["target_unit_count"]


# ---------------------------------------------------------------------------
# AS-3 fail-closed on bad factors: no crash, no partial range, cap never mutated.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        -0.5,  # negative
        0,  # zero
        0.0,  # zero float
        1.5,  # out-of-domain (> 1 would exceed the zoning cap)
        "0.8",  # non-numeric
        True,  # bool is not a numeric factor
        None,  # absent value
    ],
)
def test_as3_bad_factor_fails_closed_no_partial_range(bad_value):
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    # Inject the malformed factor directly (build_scenario would drop a non-finite
    # numeric before it reaches the document, so derive's OWN guard is exercised).
    document["assumptions"] = [_factor("utilization_factor", bad_value)]

    derived = derive_practical_usable_range(document)

    assert derived["derivable"] is False
    assert derived["derived_kind"] == DerivedRangeKind.INVALID_ASSUMPTION
    assert derived["practical_usable_range"] is None  # no partial range
    assert derived["reasons"], "a fail-closed outcome must carry a visible reason"

    # Output is strict-JSON safe: no NaN / Inf, and no negative number anywhere.
    serialized = json.dumps(derived, allow_nan=False)
    for number in _all_numbers(json.loads(serialized)):
        assert math.isfinite(number)
        assert number >= 0

    # The canonical cap is never mutated by a fail-closed derivation.
    assert document["draft_zoning_floor_area_cap_sq_ft"] == cap == 15000.0
    assert derived["canonical_cap_sq_ft"] == cap


# ---------------------------------------------------------------------------
# AS-4 no-cap document -> typed 'not derivable', visible reason, no number.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rule_evaluation_factory",
    [
        S.missing_lot_area_rule_evaluation,  # no_scenario, no cap
        S.unsupported_rule_evaluation,  # unsupported, no cap
        S.conflict_rule_evaluation,  # no_scenario (conflict), no cap
    ],
)
def test_as4_no_cap_document_is_not_derivable(rule_evaluation_factory):
    document = build_scenario(S.profile(), rule_evaluation_factory())
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None

    derived = derive_practical_usable_range(document)

    assert derived["derivable"] is False
    assert derived["derived_kind"] == DerivedRangeKind.NOT_DERIVABLE
    assert derived["practical_usable_range"] is None
    assert derived["not_derivable_reason"], "a not-derivable outcome names a reason"
    assert derived["canonical_cap_sq_ft"] is None
    # No fabricated number: no positive floor-area value is invented anywhere.
    assert 15000.0 not in _all_numbers(derived)


def test_as4_degenerate_empty_document_is_not_derivable_not_crash():
    derived = derive_practical_usable_range({})
    assert derived["derivable"] is False
    assert derived["derived_kind"] == DerivedRangeKind.NOT_DERIVABLE
    assert derived["practical_usable_range"] is None


# ---------------------------------------------------------------------------
# AS-5 determinism: identical input -> byte-identical derived output.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "assumptions",
    [
        None,
        [_factor("utilization_factor", 0.8)],
        [_factor("efficiency_ratio", 0.75), _factor("utilization_factor", 0.9)],
        [_factor("target_unit_count", 0.5, key="target_unit_count")],
    ],
)
def test_as5_identical_input_yields_byte_identical_output(assumptions):
    first = derive_practical_usable_range(_preliminary_document(assumptions=assumptions))
    second = derive_practical_usable_range(
        _preliminary_document(assumptions=assumptions)
    )
    assert json.dumps(first) == json.dumps(second)


def test_as5_factor_order_does_not_change_output():
    """Declared-assumption order must not change the derived output (deterministic
    sort of applied factors)."""
    forward = derive_practical_usable_range(
        _preliminary_document(
            assumptions=[
                _factor("utilization_factor", 0.8),
                _factor("efficiency_ratio", 0.5),
            ]
        )
    )
    reversed_ = derive_practical_usable_range(
        _preliminary_document(
            assumptions=[
                _factor("efficiency_ratio", 0.5),
                _factor("utilization_factor", 0.8),
            ]
        )
    )
    assert json.dumps(forward) == json.dumps(reversed_)


# ---------------------------------------------------------------------------
# AS-6 never-Verified + honest labelling; needs_review + disclaimer lineage.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "assumptions",
    [None, [_factor("utilization_factor", 0.8)]],
)
def test_as6_derived_is_never_verified_and_honestly_labelled(assumptions):
    document = _preliminary_document(assumptions=assumptions)
    derived = derive_practical_usable_range(document)

    # No coverage_status anywhere is 'verified', and no field VALUE equals 'verified'.
    assert "verified" not in _coverage_values(derived)
    assert "verified" not in _all_strings(derived)
    assert derived["coverage_status"] == "conditional"

    # needs_review + not_verified_disclaimer lineage preserved end-to-end.
    assert derived["needs_review"] is True
    assert derived["not_verified_disclaimer"] == document["not_verified_disclaimer"]
    assert derived["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER

    # Honest label: illustrative/derived, explicitly NOT gross/net/sellable/feasible
    # area and NOT a buildable envelope.
    assert derived["label"] == DERIVED_RANGE_LABEL
    assert "ILLUSTRATIVE DERIVED" in derived["label"]
    assert "NOT gross, net, sellable, or feasible floor area" in derived["label"]
    assert "NOT a buildable envelope" in derived["label"]
    # The range object never claims to be a buildable/feasible/sellable figure.
    assert "buildable" not in derived["practical_usable_range"]
    assert set(derived["practical_usable_range"]) == {
        "min",
        "point",
        "max",
        "unit",
        "is_point_estimate",
        "note",
    }


# ---------------------------------------------------------------------------
# AS-7 contract-free + read-only + offline: input consumed READ-ONLY and
# re-validates unchanged; derived object is a NEW, separate object.
# ---------------------------------------------------------------------------


def test_as7_input_consumed_read_only_and_revalidates_unchanged():
    document = _preliminary_document(assumptions=[_factor("utilization_factor", 0.8)])
    validate_scenario_document(document)  # valid BEFORE derivation
    snapshot = copy.deepcopy(document)

    derived = derive_practical_usable_range(document)

    # Read-only: the scenario document is byte-for-byte unchanged.
    assert document == snapshot
    assert json.dumps(document) == json.dumps(snapshot)
    # And it still re-validates unchanged against the canonical schema.
    validate_scenario_document(document)

    # Contract-free: the derived object is a NEW, separate object (never the doc).
    assert derived is not document
    assert "draft_zoning_floor_area_cap_sq_ft" not in derived  # its own shape


def test_as7_derived_object_does_not_alias_input_assumptions():
    """Mutating the derived object's factor list must never reach back into the
    scenario document (fresh copies, not aliases)."""
    document = _preliminary_document(assumptions=[_factor("utilization_factor", 0.8)])
    snapshot = copy.deepcopy(document)

    derived = derive_practical_usable_range(document)
    derived["applied_factors"][0]["value"] = 0.1  # mutate the OUTPUT

    assert document == snapshot  # input untouched


def test_recognized_factor_types_are_the_documented_closed_set():
    assert RECOGNIZED_FACTOR_TYPES == frozenset(
        {"utilization_factor", "efficiency_ratio"}
    )


# ---------------------------------------------------------------------------
# RT-1..RT-5 regression pack (revision): verbatim canonical cap in every
# outcome (no silent int->float coercion / precision loss), malformed
# assumptions containers + non-dictionary entries fail closed, and the
# never-Verified coverage boundary on successful AND unsuccessful outcomes.
# ---------------------------------------------------------------------------


def test_rt1_integer_cap_transported_and_serialized_verbatim_no_factor():
    """RT-1: an INTEGER canonical cap is transported and emitted as the EXACT integer
    (never a coerced 15000.0 float) when no factor is applied."""
    document = _preliminary_document()
    document["draft_zoning_floor_area_cap_sq_ft"] = 15000  # integer cap (injected)

    derived = derive_practical_usable_range(document)
    range_ = derived["practical_usable_range"]

    assert derived["derivable"] is True
    assert derived["derived_kind"] == DerivedRangeKind.DERIVED

    # Endpoints + canonical cap are the exact integer, not a coerced float.
    assert range_["min"] == range_["point"] == range_["max"] == 15000
    assert isinstance(range_["point"], int) and not isinstance(range_["point"], bool)
    assert isinstance(derived["canonical_cap_sq_ft"], int)
    assert derived["factor_product"] == 1.0

    # Byte-identical JSON: an int serializes as "15000", a float as "15000.0".
    assert json.dumps(range_["point"]) == json.dumps(15000) == "15000"
    assert json.dumps(derived["canonical_cap_sq_ft"]) == "15000"


def test_rt2_precision_sensitive_integer_cap_no_silent_precision_loss():
    """RT-2: a cap larger than 2**53 is transported and emitted EXACTLY, never routed
    through a lossy float (only the arithmetic path may convert to float)."""
    precise = 9007199254740993  # 2**53 + 1; float(precise) drops the low bit
    # Guards: the lossy float path WOULD differ from the exact integer.
    assert float(precise) != precise
    assert int(float(precise)) == 9007199254740992

    document = _preliminary_document()
    document["draft_zoning_floor_area_cap_sq_ft"] = precise

    derived = derive_practical_usable_range(document)
    range_ = derived["practical_usable_range"]

    assert derived["derivable"] is True
    # Exact integer preserved end-to-end (canonical cap + all endpoints).
    assert derived["canonical_cap_sq_ft"] == precise
    assert range_["min"] == range_["point"] == range_["max"] == precise
    # The endpoint is the exact int, NOT the coerced (lossy) float(precise).
    assert range_["point"] != float(precise)
    assert json.dumps(derived["canonical_cap_sq_ft"]) == "9007199254740993"
    assert json.dumps(range_["point"]) == "9007199254740993"


@pytest.mark.parametrize(
    "container",
    [
        {"utilization_factor": 0.8},  # a dict, not a list
        "utilization_factor",  # a string
        0.8,  # a float
        7,  # an int
        True,  # a bool
    ],
)
def test_rt3_malformed_assumptions_container_fails_closed(container):
    """RT-3: a present-but-non-list ``assumptions`` container fails closed with a typed
    outcome and NO range; the canonical cap is transported verbatim and never mutated."""
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    document["assumptions"] = container  # malformed: not a list

    derived = derive_practical_usable_range(document)

    assert derived["derivable"] is False
    assert derived["derived_kind"] == DerivedRangeKind.INVALID_ASSUMPTION
    assert derived["practical_usable_range"] is None  # no partial range
    assert derived["reasons"], "a fail-closed outcome must carry a visible reason"

    # Canonical cap transported verbatim + untouched; output strict-JSON safe.
    assert derived["canonical_cap_sq_ft"] == cap == 15000.0
    assert document["draft_zoning_floor_area_cap_sq_ft"] == 15000.0
    for number in _all_numbers(json.loads(json.dumps(derived, allow_nan=False))):
        assert math.isfinite(number) and number >= 0


@pytest.mark.parametrize(
    "bad_entry",
    ["utilization_factor", 0.8, 7, True, None, ["nested"]],
)
def test_rt4_non_dict_assumption_entry_fails_closed(bad_entry):
    """RT-4: a non-dict entry anywhere in the list fails closed with NO range; a
    well-formed factor ahead of it is NOT partially applied."""
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    document["assumptions"] = [_factor("utilization_factor", 0.8), bad_entry]

    derived = derive_practical_usable_range(document)

    assert derived["derivable"] is False
    assert derived["derived_kind"] == DerivedRangeKind.INVALID_ASSUMPTION
    assert derived["practical_usable_range"] is None
    assert derived["applied_factors"] == []  # no partial application leaks
    assert derived["reasons"]
    assert derived["canonical_cap_sq_ft"] == cap == 15000.0
    assert document["draft_zoning_floor_area_cap_sq_ft"] == 15000.0
    json.dumps(derived, allow_nan=False)  # strict-JSON safe


@pytest.mark.parametrize("verified_variant", ["verified", "Verified", "VERIFIED"])
def test_rt5_incoming_verified_coverage_capped_on_successful_outcome(verified_variant):
    """RT-5 (success): a defensive incoming 'verified' coverage_status NEVER passes
    through to a successful derived outcome; it is capped to 'conditional'."""
    document = _preliminary_document(assumptions=[_factor("utilization_factor", 0.8)])
    document["coverage_status"] = verified_variant

    derived = derive_practical_usable_range(document)

    assert derived["derivable"] is True  # successful outcome
    assert derived["coverage_status"] == "conditional"
    assert "verified" not in _coverage_values(derived)
    assert all(v.lower() != "verified" for v in _coverage_values(derived))


def test_rt5_incoming_verified_coverage_capped_on_not_derivable_outcome():
    """RT-5 (failure): the never-Verified boundary also holds on a not-derivable
    outcome (no cap)."""
    document = _preliminary_document()
    document["coverage_status"] = "verified"
    document["draft_zoning_floor_area_cap_sq_ft"] = None  # -> not derivable

    derived = derive_practical_usable_range(document)

    assert derived["derivable"] is False
    assert derived["derived_kind"] == DerivedRangeKind.NOT_DERIVABLE
    assert derived["coverage_status"] == "conditional"
    assert all(v.lower() != "verified" for v in _coverage_values(derived))


def test_rt5_incoming_verified_coverage_capped_on_invalid_assumption_outcome():
    """RT-5 (failure): the never-Verified boundary also holds on an
    invalid-assumption outcome (out-of-domain factor)."""
    document = _preliminary_document()
    document["coverage_status"] = "verified"
    document["assumptions"] = [_factor("utilization_factor", 1.5)]  # out of domain

    derived = derive_practical_usable_range(document)

    assert derived["derivable"] is False
    assert derived["derived_kind"] == DerivedRangeKind.INVALID_ASSUMPTION
    assert derived["coverage_status"] == "conditional"
    assert all(v.lower() != "verified" for v in _coverage_values(derived))


# ---------------------------------------------------------------------------
# RT-6, RT-7 underflow regression: cap x factors must not prematurely flush a
# still-representable subnormal to zero, and a genuinely unrepresentable
# positive result must be reported explicitly (never a successful zero).
# ---------------------------------------------------------------------------


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
