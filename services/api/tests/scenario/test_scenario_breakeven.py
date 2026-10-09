"""Executable acceptance pack AS-1..AS-7 for the deterministic scenario break-even / threshold
finder (task M5-T011).

Offline and deterministic. Each test maps to an acceptance scenario and asserts the
explicit-domain-only, named-variable + named-metric, honest-grid-bracket, verbatim-cap,
total-stable-ordering, monotonicity-honest, fail-closed, read-only, and never-Verified guarantees
the packet requires. Scans are exercised against real scenario documents produced by
``build_scenario`` (the shape the Compare / Evidence UX consumes), plus targeted malformed inputs
that prove the finder's fail-closed guards.
"""

from __future__ import annotations

import copy
import json
import math
import socket
from pathlib import Path

import pytest

from app.scenario import (
    NOT_VERIFIED_DISCLAIMER,
    RECOGNIZED_FACTOR_TYPES,
    THRESHOLD_LABEL,
    DerivedRangeKind,
    ThresholdKind,
    ThresholdResponseMetric,
    ThresholdVariable,
    build_scenario,
    derive_practical_usable_range,
    find_scenario_threshold,
)

from . import _support as S

VAR = ThresholdVariable.UTILIZATION_FACTOR
_SCANNED_KINDS = (ThresholdKind.FOUND, ThresholdKind.ALREADY_MET, ThresholdKind.NO_CROSSING)
_BREAKEVEN_SOURCE = (
    Path(__file__).resolve().parents[2] / "app" / "scenario" / "breakeven.py"
).read_text(encoding="utf-8")


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
    """json.dumps(allow_nan=False) never raises; every emitted number is finite and non-negative
    (the finder emits no signed field - a below-target candidate is meets_target:false, never a
    negative margin)."""
    serialized = json.dumps(result, allow_nan=False)
    for number in _all_numbers(json.loads(serialized)):
        assert math.isfinite(number)
        assert number >= 0


# ---------------------------------------------------------------------------
# Vocabulary consistency: every offerable variable is a factor derive applies.
# ---------------------------------------------------------------------------


def test_variable_vocabulary_is_subset_of_recognized_factor_types():
    assert {v.value for v in ThresholdVariable} <= set(RECOGNIZED_FACTOR_TYPES)


# ---------------------------------------------------------------------------
# AS-1 threshold result: base lineage + per-candidate breakdown + honest bracket.
# ---------------------------------------------------------------------------


def test_as1_found_reports_base_lineage_breakdown_and_honest_bracket():
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]  # 15000.0
    result = find_scenario_threshold(document, VAR, 13000, [0.5, 0.8, 0.9, 1.0])

    assert result["threshold_kind"] == ThresholdKind.FOUND
    assert result["scanned"] is True
    assert result["variable"] == VAR.value == "utilization_factor"
    assert result["response_metric"] == "usable_range_point"
    assert result["target"] == 13000

    # (a) base lineage: scenario identity + bounded (never-Verified) coverage status.
    lineage = result["base_lineage"]
    assert lineage["bbl"] == document["evaluated_input"]["bbl"]
    assert lineage["scenario_kind"] == document["scenario_kind"]
    assert lineage["contract_version"] == document["contract_version"]
    assert lineage["data_completeness"] == document["data_completeness"]
    assert lineage["coverage_status"] == "conditional"

    # (b) per-candidate breakdown echoing derive's metric; canonical cap transported VERBATIM.
    assert result["candidate_count"] == 4
    assert result["derivable_count"] == 4
    metrics = [c["metric_value"] for c in result["candidates"]]
    assert metrics == [7500.0, 12000.0, 13500.0, 15000.0]
    meets = [c["meets_target"] for c in result["candidates"]]
    assert meets == [False, False, True, True]
    for c in result["candidates"]:
        assert c["components"]["canonical_cap_sq_ft"] == cap == 15000.0
        assert c["variable"] == VAR.value
        assert c["response_metric"] == "usable_range_point"

    # (c) FIRST crossing as an HONEST bracketing interval (lower/upper + metrics + direction).
    crossing = result["crossing"]
    assert crossing["lower_candidate"] == 0.8
    assert crossing["lower_metric_value"] == 12000.0
    assert crossing["upper_candidate"] == 0.9
    assert crossing["upper_metric_value"] == 13500.0
    assert crossing["direction"] == "meets_target_ascending"
    assert crossing["target"] == 13000
    assert crossing["grid_adjacent"] is True
    assert result["first_meeting_candidate"] == 0.9
    assert result["crossings_count"] == 1
    assert result["non_monotonic"] is False


# ---------------------------------------------------------------------------
# AS-2 deterministic + TOTAL, stable order (independent of input order/duplication).
# ---------------------------------------------------------------------------


def test_as2_byte_identical_across_input_reorderings_and_duplicates():
    document = _preliminary_document()
    base = [0.9, 0.5, 0.8, 0.5, 1.0]  # unsorted, includes a genuine duplicate 0.5
    forward = find_scenario_threshold(document, VAR, 13000, list(base))
    reversed_ = find_scenario_threshold(document, VAR, 13000, list(reversed(base)))
    shuffled = find_scenario_threshold(document, VAR, 13000, [base[i] for i in (2, 0, 4, 1, 3)])

    assert json.dumps(forward) == json.dumps(reversed_) == json.dumps(shuffled)
    values = [c["candidate_value"] for c in forward["candidates"]]
    assert values == [0.5, 0.5, 0.8, 0.9, 1.0]  # ascending by value, duplicates preserved
    assert [c["position"] for c in forward["candidates"]] == [1, 2, 3, 4, 5]


def test_as2_identical_input_is_byte_identical():
    document = _preliminary_document()
    domain = [0.8, 0.5, 1.0]
    first = find_scenario_threshold(_preliminary_document(), VAR, 13000, list(domain))
    second = find_scenario_threshold(document, VAR, 13000, list(domain))
    assert json.dumps(first) == json.dumps(second)


# ---------------------------------------------------------------------------
# AS-3 never invents / never Verified; honest grid bracket (no interpolated derived value).
# ---------------------------------------------------------------------------


def test_as3_result_is_never_verified_and_honestly_labelled():
    document = _preliminary_document()
    result = find_scenario_threshold(document, VAR, 13000, [0.5, 0.8, 0.9, 1.0])
    assert "verified" not in _coverage_values(result)
    assert "verified" not in _all_strings(result)
    assert result["coverage_status"] == "conditional"
    assert result["needs_review"] is True
    assert result["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER
    assert result["not_verified_disclaimer"] == document["not_verified_disclaimer"]
    assert result["label"] == THRESHOLD_LABEL
    assert "ILLUSTRATIVE" in THRESHOLD_LABEL
    assert "NOT Verified" in THRESHOLD_LABEL


def test_as3_crossing_is_grid_bracket_and_midpoint_is_labelled_estimate():
    document = _preliminary_document()
    result = find_scenario_threshold(document, VAR, 13000, [0.5, 0.8, 0.9, 1.0])
    crossing = result["crossing"]

    # The reported crossing is the explicit grid BRACKET of two REAL evaluated candidates.
    candidate_values = [c["candidate_value"] for c in result["candidates"]]
    assert crossing["lower_candidate"] in candidate_values
    assert crossing["upper_candidate"] in candidate_values
    assert result["first_meeting_candidate"] in candidate_values

    # Any convenience midpoint is EXPLICITLY an illustrative estimate, never derived/Verified.
    midpoint = crossing["illustrative_bracket_midpoint"]
    assert midpoint["is_estimate"] is True
    assert midpoint["verified"] is False
    assert 0.8 < midpoint["value"] < 0.9
    assert "NOT" in midpoint["note"]


def test_as3_incoming_verified_coverage_is_capped_to_conditional():
    """A scenario must never carry 'verified'; if one somehow does, the finder caps it."""
    document = _preliminary_document()
    tampered = copy.deepcopy(document)
    tampered["coverage_status"] = "verified"
    result = find_scenario_threshold(tampered, VAR, 13000, [0.5, 1.0])
    assert result["coverage_status"] == "conditional"
    assert result["base_lineage"]["coverage_status"] == "conditional"
    assert "verified" not in _coverage_values(result)


# ---------------------------------------------------------------------------
# AS-4 monotonicity-honest + degenerate handling; typed outcomes, no crash.
# ---------------------------------------------------------------------------


def test_as4_target_already_met_at_first_candidate():
    document = _preliminary_document()
    result = find_scenario_threshold(document, VAR, 5000, [0.5, 0.8, 0.9, 1.0])
    # 0.5 -> 7500 >= 5000 already meets the target; no rising threshold to find.
    assert result["threshold_kind"] == ThresholdKind.ALREADY_MET
    assert result["crossing"] is None
    assert result["crossings_count"] == 0
    assert result["non_monotonic"] is False
    assert result["first_meeting_candidate"] == 0.5
    _strict_json_safe(result)


def test_as4_target_never_met_in_domain():
    document = _preliminary_document()
    result = find_scenario_threshold(document, VAR, 20000, [0.5, 0.8, 0.9, 1.0])
    # max metric 15000 < 20000 -> never met anywhere in-domain.
    assert result["threshold_kind"] == ThresholdKind.NO_CROSSING
    assert result["crossing"] is None
    assert result["first_meeting_candidate"] is None
    assert all(c["meets_target"] is False for c in result["candidates"])
    _strict_json_safe(result)


def test_as4_first_crossing_reported_and_flag_honest_false_when_monotonic():
    """derive's metric (cap x factor) is MONOTONIC in the factor, so exactly ONE crossing arises;
    the FIRST crossing is reported and the non_monotonic flag stays honestly False."""
    document = _preliminary_document()
    result = find_scenario_threshold(document, VAR, 13000, [0.5, 0.8, 0.9, 1.0])
    assert result["crossings_count"] == 1
    assert result["non_monotonic"] is False
    assert result["crossing"]["direction"] == "meets_target_ascending"


def test_as4_non_monotonic_multiple_crossings_via_controlled_derive_double(monkeypatch):
    """A CONTROLLED derive test double (derive.py is NOT edited) forces a NON-monotonic response so
    the multi-crossing path is exercised honestly: non_monotonic is set True, EVERY crossing is
    counted, and the FIRST honest bracket carries the endpoint metric values transported VERBATIM
    from the (doubled) derive. The double is installed on the exact name breakeven.py calls, so the
    real derive behavior is untouched; the domain is supplied shuffled to also prove the ascending
    scan order is independent of input order."""
    document = _preliminary_document()
    target = 100.0
    # Candidate value -> forced derived POINT metric: below / above / below / above the target, i.e.
    # THREE honest crossings across the ascending grid (a genuinely non-monotonic response metric).
    forced = {0.2: 50.0, 0.4: 150.0, 0.6: 80.0, 0.8: 200.0}

    def _fake_derive(candidate_document):
        point = forced[candidate_document["assumptions"][0]["value"]]
        return {
            "derived_kind": DerivedRangeKind.DERIVED,
            "derivable": True,
            "practical_usable_range": {
                "min": point,
                "point": point,
                "max": point,
                "unit": "square_feet",
                "is_point_estimate": True,
            },
            "canonical_cap_sq_ft": document["draft_zoning_floor_area_cap_sq_ft"],
            "cap_label": "draft cap (test double)",
            "applied_factors": [],
            "unapplied_assumptions": [],
            "factor_product": point,
            "label": "test-double derived range",
            "reasons": ["test double"],
            "not_derivable_reason": None,
            "coverage_status": "conditional",
            "needs_review": True,
            "not_verified_disclaimer": NOT_VERIFIED_DISCLAIMER,
        }

    monkeypatch.setattr("app.scenario.breakeven.derive_practical_usable_range", _fake_derive)
    result = find_scenario_threshold(document, VAR, target, [0.6, 0.2, 0.8, 0.4])

    # Non-monotonic: EVERY crossing counted; the flag is honestly True; kind is still FOUND.
    assert result["threshold_kind"] == ThresholdKind.FOUND
    assert result["non_monotonic"] is True
    assert result["crossings_count"] == 3
    # Metric sequence (ascending by candidate value) transported VERBATIM from the doubled derive.
    assert [c["metric_value"] for c in result["candidates"]] == [50.0, 150.0, 80.0, 200.0]
    assert [c["meets_target"] for c in result["candidates"]] == [False, True, False, True]
    # The FIRST honest bracket: 0.2 (below) -> 0.4 (meets), ascending, endpoint metrics transported.
    crossing = result["crossing"]
    assert crossing["lower_candidate"] == 0.2
    assert crossing["lower_metric_value"] == 50.0
    assert crossing["upper_candidate"] == 0.4
    assert crossing["upper_metric_value"] == 150.0
    assert crossing["direction"] == "meets_target_ascending"
    assert crossing["grid_adjacent"] is True
    assert result["first_meeting_candidate"] == 0.4
    # A NON-MONOTONIC reason is surfaced so the caller is not misled by the single reported
    # crossing.
    assert any("NON-MONOTONIC" in reason for reason in result["reasons"])
    _strict_json_safe(result)


def test_as4_not_derivable_candidates_kept_in_value_order():
    document = _preliminary_document()
    # 0.0 and 1.5 are outside the (0, 1] factor domain -> derive fails closed -> not-derivable.
    result = find_scenario_threshold(document, VAR, 13000, [0.5, 0.0, 0.9, 1.5])
    values = [c["candidate_value"] for c in result["candidates"]]
    assert values == [0.0, 0.5, 0.9, 1.5]  # ascending by value; nothing dropped
    assert result["candidate_count"] == 4
    assert result["derivable_count"] == 2
    for c in result["candidates"]:
        if c["candidate_value"] in (0.0, 1.5):
            assert c["derivable"] is False
            assert c["metric_value"] is None
            assert c["meets_target"] is None
            assert c["components"] is None
            assert c["not_derivable_reason"]
    assert result["threshold_kind"] == ThresholdKind.FOUND
    _strict_json_safe(result)


@pytest.mark.parametrize(
    "bad_variable",
    ["unknown_variable", "far", "", None, 3.14, {"k": "v"}, ["x"]],
)
def test_as4_unknown_or_malformed_variable_is_invalid(bad_variable):
    document = _preliminary_document()
    result = find_scenario_threshold(document, bad_variable, 13000, [0.5, 0.9])
    assert result["threshold_kind"] == ThresholdKind.INVALID
    assert result["scanned"] is False
    assert result["candidates"] == []
    assert result["invalid_reason"]
    if not isinstance(bad_variable, str):
        assert result["variable"] is None
    _strict_json_safe(result)


def test_as4_literal_verified_variable_is_invalid_and_never_emitted():
    document = _preliminary_document()
    result = find_scenario_threshold(document, "verified", 13000, [0.5, 0.9])
    assert result["threshold_kind"] == ThresholdKind.INVALID
    assert result["variable"] is None
    assert "verified" not in _all_strings(result)
    assert "verified" not in _coverage_values(result)
    _strict_json_safe(result)


@pytest.mark.parametrize(
    "bad_target",
    [None, "abc", float("nan"), float("inf"), float("-inf"), -1, -0.5, True, 10**400],
)
def test_as4_non_numeric_or_negative_target_is_invalid(bad_target):
    document = _preliminary_document()
    result = find_scenario_threshold(document, VAR, bad_target, [0.5, 0.9])
    assert result["threshold_kind"] == ThresholdKind.INVALID
    assert result["candidates"] == []
    assert result["invalid_reason"]
    _strict_json_safe(result)


@pytest.mark.parametrize("bad_domain", [None, "notalist", 42, 3.0, (0.5, 0.9), {"a": 1}, []])
def test_as4_empty_or_malformed_domain_is_invalid(bad_domain):
    document = _preliminary_document()
    result = find_scenario_threshold(document, VAR, 13000, bad_domain)
    assert result["threshold_kind"] == ThresholdKind.INVALID
    assert result["candidates"] == []
    assert result["invalid_reason"]
    _strict_json_safe(result)


def test_as4_unknown_response_metric_is_invalid():
    document = _preliminary_document()
    result = find_scenario_threshold(document, VAR, 13000, [0.5, 0.9], response_metric="bogus")
    assert result["threshold_kind"] == ThresholdKind.INVALID
    assert result["response_metric"] is None
    assert result["invalid_reason"]
    _strict_json_safe(result)


@pytest.mark.parametrize(
    "rule_evaluation_factory",
    [S.unsupported_rule_evaluation, S.conflict_rule_evaluation, S.missing_lot_area_rule_evaluation],
)
def test_as4_no_cap_document_is_typed_empty_with_reason(rule_evaluation_factory):
    document = build_scenario(S.profile(), rule_evaluation_factory())
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None
    result = find_scenario_threshold(document, VAR, 13000, [0.5, 0.9])
    assert result["threshold_kind"] == ThresholdKind.EMPTY
    assert result["scanned"] is False
    assert result["candidates"] == []
    assert result["empty_reason"]
    assert 15000.0 not in _all_numbers(result)
    _strict_json_safe(result)


def test_as4_degenerate_document_is_typed_no_crash():
    for degenerate in ({}, None, "notadoc", 5):
        result = find_scenario_threshold(degenerate, VAR, 13000, [0.5, 0.9])
        # No positive cap -> typed EMPTY; never a crash, always strict-JSON-safe.
        assert result["threshold_kind"] == ThresholdKind.EMPTY
        _strict_json_safe(result)


# ---------------------------------------------------------------------------
# AS-5 strict-JSON-safe + fail-closed via the SHARED sanitizer.
# ---------------------------------------------------------------------------


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
def test_as5_malformed_candidate_flagged_not_derivable_and_json_safe(bad_value):
    """A malformed candidate fails closed at ``derive`` (out-of-domain / non-finite / non-numeric)
    -> a not-derivable row with NO fabricated metric. Its raw value is never echoed raw: it is
    replaced by a typed marker (or, for a JSON-safe scalar, echoed safely), so the output stays
    strict-JSON-safe and deterministic run-to-run."""
    document = _preliminary_document()
    result = find_scenario_threshold(document, VAR, 13000, [bad_value, 0.9])

    assert result["threshold_kind"] in _SCANNED_KINDS
    assert result["candidate_count"] == 2
    assert result["derivable_count"] == 1
    _strict_json_safe(result)

    again = find_scenario_threshold(_preliminary_document(), VAR, 13000, [bad_value, 0.9])
    assert json.dumps(result) == json.dumps(again)


def test_as5_unserializable_candidate_is_typed_and_json_safe():
    document = _preliminary_document()

    class _Weird:
        pass

    result = find_scenario_threshold(document, VAR, 13000, [_Weird(), 0.9])
    assert result["threshold_kind"] in _SCANNED_KINDS
    _strict_json_safe(result)  # would raise on a raw object without sanitization
    serialized = json.dumps(result)
    assert "unsafe_value_removed" in serialized
    assert "_Weird" in serialized
    assert " at 0x" not in serialized


def test_as5_overflow_huge_int_candidate_is_guarded_and_deterministic():
    document = _preliminary_document()
    huge = 10**5000
    result = find_scenario_threshold(document, VAR, 13000, [huge, 0.9])
    _strict_json_safe(result)
    serialized = json.dumps(result)
    assert "unsafe_value_removed" in serialized
    assert "bit_length" in serialized
    assert "0" * 100 not in serialized  # the full decimal expansion never appears
    again = find_scenario_threshold(_preliminary_document(), VAR, 13000, [huge, 0.9])
    assert serialized == json.dumps(again)


def test_as5_uses_shared_sanitizer_not_a_local_duplicate():
    # It IMPORTS the shared sanitizer and does NOT define / re-duplicate the sanitizer functions.
    assert "from ._json_safety import _json_safe" in _BREAKEVEN_SOURCE
    assert "def _json_safe" not in _BREAKEVEN_SOURCE
    assert "def _unsafe_marker" not in _BREAKEVEN_SOURCE
    assert "def _safe_scalar" not in _BREAKEVEN_SOURCE


def _nested_dict(depth: int) -> dict:
    """A dict nested ``depth`` levels deep: ``{'n': {'n': {...}}}``."""
    root: dict = {}
    node = root
    for _ in range(depth):
        child: dict = {}
        node["n"] = child
        node = child
    return root


def _nested_list(depth: int) -> list:
    """A list nested ``depth`` levels deep: ``[[[...]]]``."""
    root: list = []
    node = root
    for _ in range(depth):
        child: list = []
        node.append(child)
        node = child
    return root


@pytest.mark.parametrize(
    "deep_value",
    [
        pytest.param(_nested_dict(600), id="dict_600_deep"),
        pytest.param(_nested_list(600), id="list_600_deep"),
        pytest.param(_nested_dict(5000), id="dict_5000_deep"),
        pytest.param(_nested_list(5000), id="list_5000_deep"),
    ],
)
def test_as5_deeply_nested_candidate_is_bounded_and_json_safe(deep_value):
    """A deeply-nested dict/list candidate must NEVER crash the finder. The shared iterative
    sanitizer bounds nesting to a fixed depth (a typed ``max_depth`` marker for anything deeper)
    BEFORE any recursive Python work touches the value, so the finder yields a typed not-derivable
    row for the nested candidate and ``json.dumps(result, allow_nan=False)`` never raises. This is
    the regression guard for the removed recursive ``copy.deepcopy`` that overflowed the interpreter
    recursion limit on a ~500-deep sanitized candidate (G5 BLOCKING-1 / LOW-1)."""
    document = _preliminary_document()

    # AS-4 "never an unhandled raise": a ~500+-deep candidate previously escaped a RecursionError
    # out of find_scenario_threshold; it must now return a typed scan outcome.
    result = find_scenario_threshold(document, VAR, 13000, [deep_value, 0.9])
    assert result["threshold_kind"] in _SCANNED_KINDS
    assert result["candidate_count"] == 2
    assert result["derivable_count"] == 1  # only the 0.9 candidate derives

    # AS-5 "json.dumps(result, allow_nan=False) never raises for ANY input".
    _strict_json_safe(result)
    serialized = json.dumps(result, allow_nan=False)
    assert "max_depth" in serialized  # the over-deep candidate was bounded, not descended into
    assert "unsafe_value_removed" in serialized

    # The nested candidate is a typed not-derivable row - never a fabricated metric.
    not_derivable = [c for c in result["candidates"] if not c["derivable"]]
    assert len(not_derivable) == 1
    assert not_derivable[0]["not_derivable_reason"]
    assert not_derivable[0]["metric_value"] is None

    # Deterministic run-to-run (byte-identical), like the other AS-5 pathological cases.
    again = find_scenario_threshold(_preliminary_document(), VAR, 13000, [deep_value, 0.9])
    assert serialized == json.dumps(again, allow_nan=False)


# ---------------------------------------------------------------------------
# AS-6 consumes derive READ-ONLY (no recompute); regression is the full suite run.
# ---------------------------------------------------------------------------


def test_as6_consumes_derive_read_only_no_recompute():
    document = _preliminary_document()
    result = find_scenario_threshold(document, VAR, 13000, [0.5, 0.9])
    for c in result["candidates"]:
        expected = derive_practical_usable_range(
            {**document, "assumptions": c["assumption_set"]}
        )
        assert c["derived"] == expected
        assert c["derived_kind"] == expected["derived_kind"]


# ---------------------------------------------------------------------------
# AS-7 contract-free + offline + read-only + strict-JSON-safe on every path.
# ---------------------------------------------------------------------------


def test_as7_inputs_are_byte_unchanged_and_not_aliased():
    document = _preliminary_document()
    domain = [0.8, 0.5, 0.9]
    document_before = json.dumps(document)
    domain_before = json.dumps(domain)

    result = find_scenario_threshold(document, VAR, 13000, domain)

    # Inputs are byte-unchanged after the scan (consumed strictly READ-ONLY).
    assert json.dumps(document) == document_before
    assert json.dumps(domain) == domain_before
    # Mutating the result never reaches back into the caller's input.
    result["candidates"][0]["assumption_set"].append({"injected": True})
    assert json.dumps(domain) == domain_before
    assert json.dumps(document) == document_before


def test_as7_efficiency_ratio_variable_and_metric_selection():
    document = _preliminary_document()
    result = find_scenario_threshold(
        document,
        ThresholdVariable.EFFICIENCY_RATIO,
        13000,
        [0.5, 0.8, 0.9, 1.0],
        response_metric=ThresholdResponseMetric.USABLE_RANGE_MIN,
    )
    assert result["variable"] == "efficiency_ratio"
    assert result["response_metric"] == "usable_range_min"
    # min == point == max in derive (a point estimate), so the crossing bracket is unchanged.
    assert result["crossing"]["lower_candidate"] == 0.8
    assert result["crossing"]["upper_candidate"] == 0.9
    assert result["first_meeting_candidate"] == 0.9


def test_as7_output_is_strict_json_safe_on_mixed_domain():
    document = _preliminary_document()
    domain = [0.8, 1.5, 0.0, -0.5, 0.5, float("nan")]  # a mix of valid + fail-closed values
    result = find_scenario_threshold(document, VAR, 13000, domain)
    assert result["candidate_count"] == 6
    _strict_json_safe(result)


def test_as7_runs_fully_offline_socket_blocked():
    document = _preliminary_document()
    original = socket.socket

    def _blocked(*args, **kwargs):
        raise AssertionError("network access attempted in an offline finder")

    socket.socket = _blocked
    try:
        result = find_scenario_threshold(document, VAR, 13000, [0.5, 0.9])
    finally:
        socket.socket = original
    assert result["threshold_kind"] in _SCANNED_KINDS
    _strict_json_safe(result)


def test_as7_module_imports_are_contract_free():
    # Only stdlib + .derive + .constants + ._json_safety.
    assert "from .derive import" in _BREAKEVEN_SOURCE
    assert "from .constants import" in _BREAKEVEN_SOURCE
    assert "from ._json_safety import" in _BREAKEVEN_SOURCE
    # No forbidden sibling-module imports and no network / persistence deps.
    for forbidden in (
        "from .builder",
        "from .models",
        "from .contract",
        "from .comparison",
        "from .ranking",
        "from .sensitivity",
        "import requests",
        "import httpx",
        "supabase",
    ):
        assert forbidden not in _BREAKEVEN_SOURCE


# ---------------------------------------------------------------------------
# D-059-R003 (M5-T028): THRESHOLD_LABEL must be DERIVED from the rule ACTUALLY
# evaluated, never hardcoded (M5-T027 G3 advisory A1 follow-up). The R6-R12
# family cites ZR 23-22, not the R1-R5 families' 23-21. Exercised for one
# low-density (R5, the canonical fixture) and one higher-density (R6-R12)
# district; expected section numbers are hand-typed literals read directly
# from the real ruleset files (never produced by calling the code under
# test): r5_residential_far.rule.json cites "23-21" and
# r6_r12_residential_far.rule.json cites "23-22".
# ---------------------------------------------------------------------------


def _r6_r12_rule_evaluation() -> dict:
    """A rule_evaluation whose evaluated trace is the REAL r6-r12-residential-far rule
    (section 23-22, R9A's standard-residences FAR 7.52) instead of the canonical fixture's
    r5-residential-far/23-21 trace. Local, independently-maintained copy of
    test_scenario_foundation.py's own helper (that file is outside this task's
    allowed_paths)."""
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


def test_d059_r003_threshold_label_names_the_low_density_section():
    """The low-density (R5) evaluated rule -> the threshold label names ZR 23-21 (hand-typed
    from r5_residential_far.rule.json's own ``section`` citation)."""
    document = _preliminary_document()
    result = find_scenario_threshold(document, VAR, 13000, [0.5, 0.8, 0.9, 1.0])
    assert "(ZR 23-21)" in result["label"]
    assert "23-22" not in result["label"]


def test_d059_r003_threshold_label_names_the_r6_r12_section():
    """An R6-R12 evaluated rule -> the threshold label names ZR 23-22 (hand-typed from
    r6_r12_residential_far.rule.json's own ``section`` citation), NEVER the stale hardcoded
    23-21."""
    document = build_scenario(S.profile(), _r6_r12_rule_evaluation())
    assert document["cap_provenance"]["rule_id"] == "r6-r12-residential-far"
    target = document["draft_zoning_floor_area_cap_sq_ft"] / 2
    result = find_scenario_threshold(document, VAR, target, [0.5, 0.8, 0.9, 1.0])
    assert result["threshold_kind"] in _SCANNED_KINDS
    assert "(ZR 23-22)" in result["label"]
    assert "23-21" not in result["label"]
