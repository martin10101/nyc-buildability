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
from pathlib import Path

import pytest

from app.scenario import (
    DERIVED_RANGE_LABEL,
    DRAFT_CAP_LABEL,
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


# ===========================================================================
# M5-T006 hardening pack (G5 LOW-1 / LOW-2 / LOW-3 fast-follow). These prove
# the defense-in-depth hardening added on top of the accepted M5-T005 derive:
# strict-JSON-safe malformed-cap transport, no-alias assumption copies, and a
# bounded reason echo. They map to the M5-T006 acceptance scenarios AS-1..AS-6.
# ===========================================================================


# --- LOW-1 (AS-1): a malformed cap is surfaced as null, output strict-JSON-safe. ---


@pytest.mark.parametrize(
    "bad_cap",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        -5,  # negative int
        -0.5,  # negative float
        10**400,  # positive but not representable as a finite float
    ],
)
def test_m5t006_low1_malformed_cap_nulled_and_json_safe(bad_cap):
    """AS-1: a NaN/+-Inf/negative/float-overflowing cap injected DIRECTLY yields a
    not_derivable outcome whose canonical_cap_sq_ft is null (never the malformed number);
    json.dumps(out, allow_nan=False) succeeds and no NaN/Inf/negative number appears."""
    document = _preliminary_document()
    document["draft_zoning_floor_area_cap_sq_ft"] = bad_cap

    derived = derive_practical_usable_range(document)

    assert derived["derivable"] is False
    assert derived["derived_kind"] == DerivedRangeKind.NOT_DERIVABLE
    assert derived["practical_usable_range"] is None
    # The malformed cap is surfaced as null, NOT transported verbatim.
    assert derived["canonical_cap_sq_ft"] is None
    # A reason explicitly notes the malformed cap.
    assert any("MALFORMED CAP" in reason for reason in derived["reasons"])

    # Strict-JSON-safe end to end: never raises; no NaN/Inf/negative number anywhere.
    serialized = json.dumps(derived, allow_nan=False)
    for number in _all_numbers(json.loads(serialized)):
        assert math.isfinite(number)
        assert number >= 0


def test_m5t006_low1_direct_call_malformed_document_is_json_safe():
    """AS-1: derive() called DIRECTLY (not via build_scenario) on a bare malformed
    document is still strict-JSON-safe (proves the guarantee does not depend on the
    trusted pipeline)."""
    derived = derive_practical_usable_range(
        {"draft_zoning_floor_area_cap_sq_ft": float("nan")}
    )
    assert derived["derivable"] is False
    assert derived["canonical_cap_sq_ft"] is None
    serialized = json.dumps(derived, allow_nan=False)
    for number in _all_numbers(json.loads(serialized)):
        assert math.isfinite(number) and number >= 0


def test_m5t006_low1_zero_cap_transported_verbatim_not_nulled():
    """AS-1 boundary: a zero cap is finite and non-negative, so it is NOT treated as
    malformed — it is transported verbatim (only NaN/+-Inf/negative/overflow are nulled)."""
    document = _preliminary_document()
    document["draft_zoning_floor_area_cap_sq_ft"] = 0  # not positive -> not_derivable

    derived = derive_practical_usable_range(document)

    assert derived["derivable"] is False
    assert derived["derived_kind"] == DerivedRangeKind.NOT_DERIVABLE
    assert derived["canonical_cap_sq_ft"] == 0  # verbatim, not nulled
    assert not any("MALFORMED CAP" in reason for reason in derived["reasons"])
    json.dumps(derived, allow_nan=False)  # strict-JSON safe


# --- AS-2: the DERIVED-path cap transport is UNCHANGED by the hardening. ---


def test_m5t006_as2_derived_path_cap_transport_unchanged():
    """AS-2: a normal positive-finite build_scenario cap still transports verbatim on the
    DERIVED path; the no-assumptions passthrough is byte-identical to M5-T005 behaviour."""
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    assert cap == 15000.0

    derived = derive_practical_usable_range(document)
    range_ = derived["practical_usable_range"]

    assert derived["derived_kind"] == DerivedRangeKind.DERIVED
    assert derived["canonical_cap_sq_ft"] == cap == 15000.0
    assert json.dumps(derived["canonical_cap_sq_ft"]) == json.dumps(cap)
    assert range_["min"] == range_["point"] == range_["max"] == cap


# --- AS-2 full-output GOLDEN baseline: the ENTIRE DERIVED-path json.dumps output is
# pinned to an explicit expected object, so the hardening is proven to leave the
# ordinary DERIVED path byte-for-byte unchanged (substantiates the report's
# "byte-equivalent to M5-T005" claim for inputs that do not trip the LOW-3 aggregate
# echo bound). The long labels/disclaimer are the module's own published constants; the
# derive-authored strings (note + reasons) are pinned verbatim. ---

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


def test_m5t006_as2_no_assumptions_full_output_golden_baseline():
    """AS-2: the COMPLETE no-assumptions DERIVED output equals an explicit golden object,
    byte-for-byte (json.dumps identical, including key order). Any drift in the DERIVED
    path — structure, field order, labels, reasons, or the verbatim cap — fails this test,
    substantiating full-output baseline byte-equivalence rather than a per-field spot check."""
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
    # Byte-for-byte (this also pins key ORDER, which value-equality does not).
    assert json.dumps(derived) == json.dumps(expected)


def test_m5t006_as2_single_factor_full_output_golden_baseline():
    """AS-2: the COMPLETE single-recognized-factor DERIVED output equals an explicit golden
    object, byte-for-byte. Proves the factor-derivation path (cap x declared factor, applied
    factor echoed, cap transported verbatim) is unchanged by the hardening."""
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


# --- LOW-2 (AS-3): an unapplied nested-mutable value is never aliased to the input. ---


def test_m5t006_low2_unapplied_nested_value_not_aliased():
    """AS-3: an UNAPPLIED assumption carrying a nested-mutable value yields a derived
    object whose value is a fresh copy (`is` is False); mutating the derived nested value
    never reaches back into the scenario document."""
    nested = {"nested": [1, 2, 3]}
    document = _preliminary_document(
        assumptions=[_factor("target_unit_count", nested, key="target_unit_count")]
    )
    snapshot = copy.deepcopy(document)

    derived = derive_practical_usable_range(document)
    unapplied = derived["unapplied_assumptions"][0]

    # Not the same object as the input, but equal by value.
    assert unapplied["value"] is not document["assumptions"][0]["value"]
    assert unapplied["value"] == nested

    # Mutating the derived nested value never changes the input scenario document.
    unapplied["value"]["nested"].append(999)
    assert document == snapshot
    assert document["assumptions"][0]["value"] == {"nested": [1, 2, 3]}


def test_m5t006_low2_deepcopy_protects_nested_rationale_direct_call():
    """AS-3: derive() is contract-free and may be called DIRECTLY on a document whose
    APPLIED factor carries a nested-mutable rationale (build_scenario coerces rationale to a
    string, but a direct caller need not). _copy_assumption deep-copies every field, so
    mutating the derived copy never reaches back into the input document."""
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

    assert derived["derived_kind"] == DerivedRangeKind.DERIVED  # 0.8 is applied
    # The derived copy is a fresh object, not aliased to the input's nested rationale.
    assert applied["rationale"] is not document["assumptions"][0]["rationale"]
    applied["rationale"]["note"].append("mutated")
    assert document == snapshot  # input document never mutated


# --- LOW-3 (AS-4): raw input echoed into a reason string is length-bounded. ---


def test_m5t006_low3_scenario_kind_echo_is_bounded():
    """AS-4: a pathological 100k-char scenario_kind echoed into the not_derivable reason is
    truncated (with a marker); the reason does not grow unbounded."""
    document = _preliminary_document()
    document["draft_zoning_floor_area_cap_sq_ft"] = None  # -> not derivable, echoes kind
    document["scenario_kind"] = "x" * 100_000

    derived = derive_practical_usable_range(document)

    joined = " ".join(derived["reasons"])
    assert len(joined) < 2_000  # bounded, nowhere near 100k
    assert "truncated" in joined


def test_m5t006_low3_factor_value_echo_is_bounded():
    """AS-4: a 100k-char non-numeric factor value echoed into the fail-closed reason is
    truncated; the reason stays bounded."""
    document = _preliminary_document()
    document["assumptions"] = [_factor("utilization_factor", "0." + "9" * 100_000)]

    derived = derive_practical_usable_range(document)

    assert derived["derived_kind"] == DerivedRangeKind.INVALID_ASSUMPTION
    joined = " ".join(derived["reasons"])
    assert len(joined) < 2_000
    assert "truncated" in joined


def test_m5t006_low3_unapplied_key_echo_is_bounded():
    """AS-4: a 100k-char unapplied-assumption key echoed into the surfaced-but-not-applied
    reason is truncated; the reason stays bounded (the full key still lives in the data
    field, which is legitimate — only the reason echo is bounded)."""
    huge_key = "k" * 100_000
    document = _preliminary_document(
        assumptions=[_factor("target_unit_count", 0.5, key=huge_key)]
    )

    derived = derive_practical_usable_range(document)

    assert derived["derivable"] is True  # unrecognized -> surfaced, range == cap
    joined = " ".join(derived["reasons"])
    assert len(joined) < 2_000
    assert "truncated" in joined
    # The untruncated key remains available in the structured data field.
    assert derived["unapplied_assumptions"][0]["key"] == huge_key


def test_m5t006_low3_many_unapplied_keys_reason_has_fixed_upper_bound():
    """AS-4 (aggregate bound): MANY distinct unapplied-assumption keys must not bloat the
    reason. Each key is already per-value length-bounded, but without an aggregate bound N
    short keys would still concatenate into an ~N*len reason (a 20k-key list -> ~360k-char
    reason). The aggregate echo caps the NUMBER of keys echoed with an explicit truncation
    marker, so the COMPLETE reason has a FIXED upper bound independent of how many
    assumptions are declared, while the full key set stays available in the structured
    unapplied_assumptions data (only the reason echo is bounded)."""

    def _derive_with(n):
        keys = [f"unapplied-{i:06d}" for i in range(n)]
        document = _preliminary_document(
            assumptions=[_factor("target_unit_count", 0.5, key=k) for k in keys]
        )
        return derive_practical_usable_range(document), keys

    fixed_reason_bound = 2_000  # nowhere near an unbounded N*len(key) echo (~360k for 20k)
    small_n, large_n = 64, 20_000
    small, small_keys = _derive_with(small_n)
    large, large_keys = _derive_with(large_n)

    for derived, keys in ((small, small_keys), (large, large_keys)):
        assert derived["derivable"] is True  # unrecognized -> surfaced, range == cap
        reason = next(r for r in derived["reasons"] if "surfaced but NOT applied" in r)
        # The complete reason (and the whole joined reason block) is bounded.
        assert len(reason) < fixed_reason_bound
        assert len(" ".join(derived["reasons"])) < fixed_reason_bound
        # An explicit truncation marker stands in for the omitted tail.
        assert "truncated" in reason
        assert "more unapplied key(s) truncated" in reason
        # Not every key is echoed: the last-sorted key is omitted from the reason ...
        assert keys[-1] not in reason
        # ... but the FULL, untruncated key set remains in the structured data field.
        assert [a["key"] for a in derived["unapplied_assumptions"]] == sorted(keys)

    # The bound is FIXED, not merely small: a ~300x larger key count changes the reason
    # length only by the digit-count of the remainder marker (a handful of chars).
    small_reason = next(r for r in small["reasons"] if "surfaced but NOT applied" in r)
    large_reason = next(r for r in large["reasons"] if "surfaced but NOT applied" in r)
    assert abs(len(large_reason) - len(small_reason)) <= 8


# --- AS-5 / AS-6: never-Verified preserved + determinism with the hardening. ---


def test_m5t006_as5_never_verified_preserved_on_malformed_cap():
    """AS-5: even a malformed-cap not_derivable outcome carries no 'verified' value and
    preserves the needs_review + not_verified_disclaimer lineage."""
    document = _preliminary_document()
    document["coverage_status"] = "verified"
    document["draft_zoning_floor_area_cap_sq_ft"] = float("-inf")

    derived = derive_practical_usable_range(document)

    assert "verified" not in _all_strings(derived)
    assert derived["coverage_status"] == "conditional"
    assert derived["needs_review"] is True
    assert derived["not_verified_disclaimer"] == document["not_verified_disclaimer"]


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
    """AS-6: identical (hardened) input -> byte-identical output across the hardened paths
    (malformed cap, bounded kind echo, single bounded unapplied-key echo, and the aggregate
    many-key bounded echo)."""
    first = _preliminary_document()
    mutate(first)
    second = _preliminary_document()
    mutate(second)
    assert json.dumps(derive_practical_usable_range(first)) == json.dumps(
        derive_practical_usable_range(second)
    )


# ---------------------------------------------------------------------------
# D-059-R003 (M5-T028): DERIVED_RANGE_LABEL must be DERIVED from the rule
# ACTUALLY evaluated, never hardcoded (M5-T027 G3 advisory A1 follow-up). The
# R6-R12 family cites ZR 23-22, not the R1-R5 families' 23-21. Exercised for
# one low-density (R5, the canonical fixture) and one higher-density (R6-R12)
# district; expected section numbers are hand-typed literals read directly
# from the real ruleset files (never produced by calling the code under
# test): services/api/app/rules/rulesets/r5_residential_far.rule.json cites
# "23-21" and r6_r12_residential_far.rule.json cites "23-22".
# ---------------------------------------------------------------------------


def _r6_r12_rule_evaluation() -> dict:
    """A rule_evaluation whose evaluated trace is the REAL r6-r12-residential-far rule
    (rules/rulesets/r6_r12_residential_far.rule.json: rule_id, citation section 23-22, R9A's
    standard-residences FAR 7.52) instead of the canonical fixture's r5-residential-far/23-21
    trace - built by editing a deep copy so every OTHER field (provenance wiring, bbl, etc.)
    stays the same shape the rule engine actually emits. Mirrors
    test_scenario_foundation.py's own ``_r6_r12_rule_evaluation`` helper (that file is outside
    this task's allowed_paths, so this is a local, independently-maintained copy)."""
    rule_evaluation = S.canonical_rule_evaluation()
    trace = rule_evaluation["evaluations"][0]
    far = 7.52
    lot_area = trace["evaluated_inputs"]["lot_area_sq_ft"]
    trace["rule_id"] = "r6-r12-residential-far"
    trace["evaluated_inputs"]["zoning_district"] = "R9A"
    trace["applicability_trace"][0]["detail"]["values"] = ["R9A"]
    trace["applicability_trace"][0]["detail"]["value_seen"] = "R9A"
    trace["computation_steps"][0]["resolved_args"] = [far]
    trace["computation_steps"][0]["result"] = far
    trace["computation_steps"][1]["resolved_args"] = [lot_area, far]
    trace["computation_steps"][1]["result"] = lot_area * far
    trace["outputs"] = {
        "max_residential_far": far,
        "max_residential_floor_area_sq_ft": lot_area * far,
    }
    citation_provenance = dict(trace["citations"][0]["provenance"])
    citation_provenance.update(
        snapshot_id="zr-23-22",
        request_url="https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22",
        section_number="23-22",
        section_title="Maximum Floor Area Ratio for R6 Through R12 Districts",
    )
    trace["citations"] = [
        {
            "snapshot_id": "zr-23-22",
            "section": "23-22",
            "quote": (
                "MAXIMUM FLOOR AREA RATIO FOR R6-R12 DISTRICTS. Separate maximum "
                "residential floor area ratios are set forth for zoning lots "
                "containing standard residences and zoning lots containing "
                "qualifying affordable housing or qualifying senior housing."
            ),
            "last_amended": "2024-12-05",
            "provenance": citation_provenance,
        }
    ]
    rule_evaluation["zoning_district"] = "R9A"
    rule_evaluation["family_coverage"]["rule_ids"] = ["r6-r12-residential-far"]
    for candidate in rule_evaluation["spatial_uncertainty"]["base_district_candidates"]:
        candidate["district_label"] = "R9A"
    return rule_evaluation


def test_d059_r003_derived_range_label_names_the_low_density_section():
    """S1: a low-density (R5) evaluated rule -> the derived label names ZR 23-21 (hand-typed
    from r5_residential_far.rule.json's own ``section`` citation)."""
    document = _preliminary_document()
    derived = derive_practical_usable_range(document)
    assert "(ZR 23-21)" in derived["label"]
    assert "23-22" not in derived["label"]


def test_d059_r003_derived_range_label_names_the_r6_r12_section():
    """S1: an R6-R12 evaluated rule -> the derived label names ZR 23-22 (hand-typed from
    r6_r12_residential_far.rule.json's own ``section`` citation), NEVER the stale hardcoded
    23-21."""
    rule_evaluation = _r6_r12_rule_evaluation()
    document = build_scenario(S.profile(), rule_evaluation)
    assert document["cap_provenance"]["rule_id"] == "r6-r12-residential-far"

    derived = derive_practical_usable_range(document)
    assert derived["derived_kind"] == DerivedRangeKind.DERIVED
    assert "(ZR 23-22)" in derived["label"]
    assert "23-21" not in derived["label"]


def test_d059_r003_derived_range_label_is_generic_with_no_cap_provenance():
    """S1: when no rule context reaches the builder (a no-cap outcome), the label states the
    section GENERICALLY - it never defaults to 23-21 (or any other specific section)."""
    document = build_scenario(S.profile(), S.unsupported_rule_evaluation())
    assert document["cap_provenance"] is None

    derived = derive_practical_usable_range(document)
    assert derived["derived_kind"] == DerivedRangeKind.NOT_DERIVABLE
    assert "23-21" not in derived["label"]
    assert "23-22" not in derived["label"]
    assert "cap_provenance.citations" in derived["label"]


def test_d059_r003_no_residual_hardcoded_zr_23_21_across_the_five_modules():
    """S2: none of the five live-wired scenario-analysis modules (derive / breakeven /
    comparison / ranking / sensitivity) may hardcode the literal 'ZR 23-21' phrase in their
    SOURCE TEXT - the section reference must be derived from the actually-evaluated rule (or
    stated generically). Reading the source directly (not just exercising a runtime path)
    catches a regression that reintroduces the literal phrase even in code a particular test
    run does not happen to execute."""
    package_root = Path(__file__).resolve().parents[2] / "app" / "scenario"
    for name in ("derive.py", "breakeven.py", "comparison.py", "ranking.py", "sensitivity.py"):
        source = (package_root / name).read_text(encoding="utf-8")
        assert "ZR 23-21" not in source, (
            f"{name} still hardcodes the literal 'ZR 23-21' phrase; the section reference "
            "must be derived from the actually-evaluated rule (D-059-R003)."
        )
