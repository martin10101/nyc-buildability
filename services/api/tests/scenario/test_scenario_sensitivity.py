"""Executable acceptance pack AS-1..AS-7 for the deterministic single-variable sensitivity /
what-if analysis (task M5-T008).

Offline and deterministic. Each test maps to an acceptance scenario and asserts the
explicit-values-only, named-variable, transparent-breakdown, total-stable-ordering, fail-closed,
read-only, and never-Verified guarantees the packet requires. Points are exercised against real
scenario documents produced by ``build_scenario`` (the shape the Compare/Evidence UX consumes),
plus targeted malformed inputs that prove sensitivity's fail-closed guards.
"""

from __future__ import annotations

import copy
import json
import math

import pytest

from app.scenario import (
    NOT_VERIFIED_DISCLAIMER,
    RECOGNIZED_FACTOR_TYPES,
    SENSITIVITY_LABEL,
    SENSITIVITY_RESPONSE_METRIC,
    SensitivityKind,
    SensitivityVariable,
    analyze_scenario_sensitivity,
    build_scenario,
    derive_practical_usable_range,
)

from . import _support as S

VAR = SensitivityVariable.UTILIZATION_FACTOR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _preliminary_document() -> dict:
    """A real PRELIMINARY scenario document (canonical R5 cap = 15000.0)."""
    return build_scenario(S.profile(), S.canonical_rule_evaluation())


def _coverage_values(node):
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


def _strict_json_safe(result) -> None:
    """No NaN / Inf / negative number anywhere; json.dumps(allow_nan=False) never raises."""
    serialized = json.dumps(result, allow_nan=False)
    for number in _all_numbers(json.loads(serialized)):
        assert math.isfinite(number)
        assert number >= 0


# ---------------------------------------------------------------------------
# Vocabulary consistency: every offerable variable is a factor derive applies.
# ---------------------------------------------------------------------------


def test_variable_vocabulary_is_subset_of_recognized_factor_types():
    assert {v.value for v in SensitivityVariable} <= set(RECOGNIZED_FACTOR_TYPES)


# ---------------------------------------------------------------------------
# AS-1 deterministic, TOTAL, stable ordering (independent of input order/duplication).
# ---------------------------------------------------------------------------


def test_as1_points_ordered_by_tried_value_ascending():
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    result = analyze_scenario_sensitivity(document, VAR, [0.8, 0.5, 1.0, 0.9])

    assert result["sensitivity_kind"] == SensitivityKind.ANALYZED
    tried = [p["value"] for p in result["points"]]
    assert tried == [0.5, 0.8, 0.9, 1.0]
    assert [p["position"] for p in result["points"]] == [1, 2, 3, 4]
    response = [p["response_point"] for p in result["points"]]
    assert response == [cap * 0.5, cap * 0.8, cap * 0.9, cap * 1.0]
    assert response == [7500.0, 12000.0, 13500.0, 15000.0]


def test_as1_byte_identical_across_input_reorderings_and_duplicates():
    """Reordering / duplicating the caller's values must not change the output: a TOTAL
    value-then-content order makes the ordered output a pure function of the multiset of values,
    never of their supplied position."""
    document = _preliminary_document()
    base = [0.5, 0.8, 0.5, 0.9]  # includes a genuine duplicate 0.5
    forward = analyze_scenario_sensitivity(document, VAR, list(base))
    reversed_ = analyze_scenario_sensitivity(document, VAR, list(reversed(base)))
    shuffled = analyze_scenario_sensitivity(document, VAR, [base[i] for i in (2, 0, 3, 1)])

    assert json.dumps(forward) == json.dumps(reversed_) == json.dumps(shuffled)
    tried = [p["value"] for p in forward["points"]]
    assert tried == [0.5, 0.5, 0.8, 0.9]  # duplicates preserved, ordered by value


def test_as1_identical_input_is_byte_identical():
    document = _preliminary_document()
    values = [0.8, 0.6]
    first = analyze_scenario_sensitivity(_preliminary_document(), VAR, list(values))
    second = analyze_scenario_sensitivity(document, VAR, list(values))
    assert json.dumps(first) == json.dumps(second)


# ---------------------------------------------------------------------------
# AS-2 transparent NAMED-variable + NAMED-metric response; no hidden weight.
# ---------------------------------------------------------------------------


def test_as2_names_variable_and_metric_and_transparent_components():
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    result = analyze_scenario_sensitivity(document, VAR, [0.8, 0.5])

    # The variable AND the response metric are NAMED on the response.
    assert result["variable"] == VAR.value == "utilization_factor"
    assert result["variable_label"]
    assert result["response_metric"] == SENSITIVITY_RESPONSE_METRIC
    assert SENSITIVITY_RESPONSE_METRIC == "illustrative_usable_area_sq_ft"
    assert result["response_metric_label"]

    for point in result["points"]:
        # Every point NAMES the varied variable and the metric (no unnamed point).
        assert point["variable"] == VAR.value
        assert point["response_metric"] == SENSITIVITY_RESPONSE_METRIC
        components = point["components"]
        assert components["variable"] == VAR.value
        # The point is a DOCUMENTED function of already-surfaced numbers only: no hidden weight.
        assert point["response_point"] == components["illustrative_usable_area_sq_ft"]
        assert point["response_point"] == cap * components["factor_product"]
        assert components["canonical_cap_sq_ft"] == cap
        assert "formula" in components


def test_as2_no_point_emitted_without_naming_the_variable():
    document = _preliminary_document()
    result = analyze_scenario_sensitivity(document, VAR, [0.7, 1.5, 0.3])
    assert result["points"]
    for point in result["points"]:
        assert point["variable"] == VAR.value
        assert point["variable_label"]


# ---------------------------------------------------------------------------
# AS-3 explicit-values-only; never fabricates; empty -> baseline; not-derivable kept in place.
# ---------------------------------------------------------------------------


def test_as3_one_point_per_supplied_value_never_fabricates():
    document = _preliminary_document()
    values = [0.9, 0.4, 0.6]
    result = analyze_scenario_sensitivity(document, VAR, values)
    # Exactly one point per supplied value - no invented value/scenario/assumption/alternative.
    assert result["point_count"] == len(values) == 3
    assert len(result["points"]) == 3
    assert sorted(p["value"] for p in result["points"]) == [0.4, 0.6, 0.9]


@pytest.mark.parametrize("empty", [[], None])
def test_as3_empty_values_returns_single_baseline_point_not_a_fabrication(empty):
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    result = analyze_scenario_sensitivity(document, VAR, empty)

    assert result["sensitivity_kind"] == SensitivityKind.ANALYZED
    assert result["point_count"] == 1
    only = result["points"][0]
    # The single point is the RAW scenario (no value applied), never a fabricated value.
    assert only["is_baseline"] is True
    assert only["value"] is None
    assert only["derivable"] is True
    assert only["response_point"] == cap == 15000.0
    assert only["components"]["factor_product"] == 1.0
    assert only["assumption_set"] == []


def test_as3_not_derivable_value_is_kept_in_value_order_not_relocated():
    """A value derive rejects (0.0 is out of the (0, 1] factor domain) is flagged not-derivable
    but KEPT IN PLACE by value order (0.0 sorts first) - NOT relocated last. No fabricated point."""
    document = _preliminary_document()
    result = analyze_scenario_sensitivity(document, VAR, [0.5, 0.0, 0.8])

    tried = [p["value"] for p in result["points"]]
    assert tried == [0.0, 0.5, 0.8]  # 0.0 stays FIRST by value order, never moved last
    assert result["point_count"] == 3
    assert result["derivable_count"] == 2
    zero_point = result["points"][0]
    assert zero_point["value"] == 0.0
    assert zero_point["derivable"] is False
    assert zero_point["response_point"] is None
    assert zero_point["components"] is None
    assert zero_point["not_derivable_reason"]


# ---------------------------------------------------------------------------
# AS-4 fail-closed on bad input: typed outcome, no crash, strict-JSON-safe.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_variable",
    ["unknown_variable", "far", "", None, float("nan"), 3.14, {"k": "v"}, ["x"]],
)
def test_as4_unknown_or_malformed_variable_is_invalid(bad_variable):
    document = _preliminary_document()
    result = analyze_scenario_sensitivity(document, bad_variable, [0.8])
    assert result["sensitivity_kind"] == SensitivityKind.INVALID
    assert result["analyzed"] is False
    assert result["points"] == []
    assert result["invalid_reason"]
    if not isinstance(bad_variable, str):
        assert result["variable"] is None
    _strict_json_safe(result)


@pytest.mark.parametrize(
    "rule_evaluation_factory",
    [S.unsupported_rule_evaluation, S.conflict_rule_evaluation, S.missing_lot_area_rule_evaluation],
)
def test_as4_no_cap_document_is_typed_empty_with_reason(rule_evaluation_factory):
    document = build_scenario(S.profile(), rule_evaluation_factory())
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None

    result = analyze_scenario_sensitivity(document, VAR, [0.8])
    assert result["sensitivity_kind"] == SensitivityKind.EMPTY
    assert result["analyzed"] is False
    assert result["points"] == []
    assert result["empty_reason"]
    assert 15000.0 not in _all_numbers(result)
    _strict_json_safe(result)


@pytest.mark.parametrize("bad_container", [{"a": 1}, "notalist", 42, 3.0, (0.5, 0.8)])
def test_as4_malformed_values_container_is_invalid(bad_container):
    document = _preliminary_document()
    result = analyze_scenario_sensitivity(document, VAR, bad_container)
    assert result["sensitivity_kind"] == SensitivityKind.INVALID
    assert result["points"] == []
    assert result["invalid_reason"]
    _strict_json_safe(result)


def test_as4_degenerate_document_is_typed_no_crash():
    for degenerate in ({}, None, "notadoc", 5):
        result = analyze_scenario_sensitivity(degenerate, VAR, [0.8])
        # No positive cap -> typed EMPTY; never a crash, always strict-JSON-safe.
        assert result["sensitivity_kind"] == SensitivityKind.EMPTY
        _strict_json_safe(result)


@pytest.mark.parametrize(
    "bad_value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        -0.5,
        -1,
        10**400,
        "abc",
        None,
        True,
        pytest.param(10**5000, id="pow10_5000"),
        pytest.param(-(10**5000), id="neg_pow10_5000"),
    ],
)
def test_as4_malformed_value_flagged_not_derivable_and_json_safe(bad_value):
    """A malformed tried value fails closed at ``derive`` (out-of-domain / non-finite /
    non-numeric) -> a not-derivable point with NO fabricated response. Its raw value is never
    echoed raw: it is replaced by a typed marker (or, for a JSON-safe scalar, echoed safely), so
    the output stays strict-JSON-safe and deterministic run-to-run."""
    document = _preliminary_document()
    values = [bad_value, 0.8]
    result = analyze_scenario_sensitivity(document, VAR, values)

    assert result["sensitivity_kind"] == SensitivityKind.ANALYZED
    assert result["point_count"] == 2
    _strict_json_safe(result)

    derivable = [p for p in result["points"] if p["derivable"]]
    not_derivable = [p for p in result["points"] if not p["derivable"]]
    assert len(derivable) == 1 and derivable[0]["value"] == 0.8
    assert len(not_derivable) == 1
    assert not_derivable[0]["response_point"] is None
    assert not_derivable[0]["components"] is None
    assert not_derivable[0]["not_derivable_reason"]

    # Deterministic even with the malformed value.
    again = analyze_scenario_sensitivity(_preliminary_document(), VAR, [bad_value, 0.8])
    assert json.dumps(result) == json.dumps(again)


def test_as4_unserializable_object_value_is_typed_and_json_safe():
    """A non-JSON-serializable object as a tried value must not make the output un-serializable:
    it is replaced by a typed marker that surfaces only its deterministic type name."""
    document = _preliminary_document()

    class _Weird:
        pass

    result = analyze_scenario_sensitivity(document, VAR, [_Weird()])
    assert result["sensitivity_kind"] == SensitivityKind.ANALYZED
    _strict_json_safe(result)  # would raise on a raw object without sanitization
    serialized = json.dumps(result)
    assert "unsafe_value_removed" in serialized
    assert "_Weird" in serialized


def test_as4_overflow_huge_int_value_is_guarded_and_deterministic():
    """A tried value of 10**5000 (a ~5001-digit integer that exceeds CPython's int->str ceiling
    and would raise ``ValueError`` if decimal-expanded). The marker must describe it by magnitude
    (bit length), keeping the output typed, strict-JSON-safe, byte-bounded, and deterministic."""
    document = _preliminary_document()
    huge = 10**5000
    values = [huge, 0.8]
    result = analyze_scenario_sensitivity(document, VAR, values)

    assert result["sensitivity_kind"] == SensitivityKind.ANALYZED
    assert result["point_count"] == 2
    _strict_json_safe(result)
    serialized = json.dumps(result)
    assert "unsafe_value_removed" in serialized
    assert "bit_length" in serialized
    assert "0" * 100 not in serialized  # the full decimal expansion never appears
    again = analyze_scenario_sensitivity(_preliminary_document(), VAR, [huge, 0.8])
    assert serialized == json.dumps(again)


def test_as4_object_dict_key_value_is_typed_and_deterministic():
    """A tried value that is a dict keyed by an ordinary object must not be rendered through its
    address-bearing ``repr`` (non-JSON-safe AND non-deterministic): the sanitizer replaces the key
    with a deterministic typed token, keeping the output ANALYZED, strict-JSON-safe, and
    byte-identical run-to-run."""
    document = _preliminary_document()

    class _ObjKey:
        pass

    def _values():
        return [{_ObjKey(): "nested"}, 0.8]

    result = analyze_scenario_sensitivity(document, VAR, _values())
    assert result["sensitivity_kind"] == SensitivityKind.ANALYZED
    assert result["point_count"] == 2
    _strict_json_safe(result)
    serialized = json.dumps(result)
    assert "__unsafe_key__" in serialized
    assert "_ObjKey" in serialized
    assert " at 0x" not in serialized
    again = analyze_scenario_sensitivity(_preliminary_document(), VAR, _values())
    assert serialized == json.dumps(again)


# ---------------------------------------------------------------------------
# AS-5 never up-labels / never Verified; needs_review + disclaimer preserved.
# ---------------------------------------------------------------------------


def test_as5_response_is_never_verified_and_honestly_labelled():
    document = _preliminary_document()
    result = analyze_scenario_sensitivity(document, VAR, [0.8, 0.5])
    assert "verified" not in _coverage_values(result)
    assert "verified" not in _all_strings(result)
    assert result["coverage_status"] == "conditional"
    assert result["needs_review"] is True
    assert result["not_verified_disclaimer"] == document["not_verified_disclaimer"]
    assert result["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER
    assert result["label"] == SENSITIVITY_LABEL
    assert "ILLUSTRATIVE" in SENSITIVITY_LABEL
    assert "NOT Verified" in SENSITIVITY_LABEL


def test_as5_incoming_verified_coverage_is_capped_to_conditional():
    """A scenario must never carry 'verified'; if one somehow does, sensitivity caps it."""
    document = _preliminary_document()
    tampered = copy.deepcopy(document)
    tampered["coverage_status"] = "verified"
    result = analyze_scenario_sensitivity(tampered, VAR, [])
    assert result["coverage_status"] == "conditional"
    assert "verified" not in _coverage_values(result)


def test_as5_literal_verified_variable_is_invalid_and_never_emitted():
    """A caller passing the LITERAL variable 'verified' must fail closed AND never inject the
    never-Verified token into the output: the invalid-variable echo is sanitized to None."""
    document = _preliminary_document()
    result = analyze_scenario_sensitivity(document, "verified", [0.8])
    assert result["sensitivity_kind"] == SensitivityKind.INVALID
    assert result["analyzed"] is False
    assert result["points"] == []
    assert result["invalid_reason"]
    assert result["variable"] is None
    assert "verified" not in _all_strings(result)
    assert "verified" not in _coverage_values(result)
    _strict_json_safe(result)


# ---------------------------------------------------------------------------
# AS-6 read-only consumption; no legal recompute; no aliasing.
# ---------------------------------------------------------------------------


def test_as6_inputs_are_byte_unchanged_and_not_aliased():
    document = _preliminary_document()
    values = [0.8, 0.5]
    document_before = json.dumps(document)
    values_before = json.dumps(values)

    result = analyze_scenario_sensitivity(document, VAR, values)

    # Inputs are byte-unchanged after analysis (consumed strictly READ-ONLY).
    assert json.dumps(document) == document_before
    assert json.dumps(values) == values_before
    # Mutating the result never reaches back into the caller's input.
    result["points"][0]["assumption_set"].append({"injected": True})
    assert json.dumps(values) == values_before
    assert json.dumps(document) == document_before


def test_as6_point_uses_only_surfaced_numbers_no_recompute():
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    result = analyze_scenario_sensitivity(document, VAR, [0.8])
    point = result["points"][0]

    # The point's transparent breakdown is exactly the accepted derive() output for the same
    # explicit single-assumption set: sensitivity CONSUMES derive.py, never recomputes a value.
    expected_derived = derive_practical_usable_range(
        {**document, "assumptions": point["assumption_set"]}
    )
    assert point["derived"] == expected_derived
    assert point["components"]["canonical_cap_sq_ft"] == cap
    assert point["response_point"] == cap * 0.8 == 12000.0


# ---------------------------------------------------------------------------
# AS-7 contract-free + offline + strict-JSON-safe on every path.
# ---------------------------------------------------------------------------


def test_as7_response_output_is_strict_json_safe():
    document = _preliminary_document()
    values = [0.8, 1.5, 0.0, -0.5, 0.5]  # a mix of valid + fail-closed values
    result = analyze_scenario_sensitivity(document, VAR, values)
    assert result["point_count"] == 5
    _strict_json_safe(result)


def test_as7_consumes_derive_breakdown_for_every_derivable_point():
    document = _preliminary_document()
    result = analyze_scenario_sensitivity(document, VAR, [0.8, 0.5])
    for point in result["points"]:
        expected = derive_practical_usable_range(
            {**document, "assumptions": point["assumption_set"]}
        )
        assert point["derived"] == expected
        assert point["derived_kind"] == expected["derived_kind"]


def test_as7_efficiency_ratio_variable_also_works():
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    result = analyze_scenario_sensitivity(
        document, SensitivityVariable.EFFICIENCY_RATIO, [0.9, 0.6]
    )
    assert result["variable"] == "efficiency_ratio"
    tried = [p["value"] for p in result["points"]]
    assert tried == [0.6, 0.9]
    assert [p["response_point"] for p in result["points"]] == [cap * 0.6, cap * 0.9]
