"""Executable acceptance pack AS-1..AS-7 for the deterministic scenario comparison / delta
engine (task M5-T010).

Offline and deterministic. Each test maps to an acceptance scenario and asserts the
explicit-named-sets-only, verbatim-cap, baseline-relative-delta, total-stable-ordering,
fail-closed, read-only, and never-Verified guarantees the packet requires. Comparisons are
exercised against real scenario documents produced by ``build_scenario`` (the shape the Compare
UI consumes), plus targeted malformed inputs that prove comparison's fail-closed guards.
"""

from __future__ import annotations

import copy
import inspect
import json
import math
import socket

import pytest

from app.scenario import (
    COMPARISON_LABEL,
    COMPARISON_METRIC_KEYS,
    NOT_VERIFIED_DISCLAIMER,
    ComparisonKind,
    build_scenario,
    compare_scenario_assumption_sets,
    derive_practical_usable_range,
)
from app.scenario import comparison as comparison_module
from app.scenario.comparison import _metric_delta

from . import _support as S

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _preliminary_document() -> dict:
    """A real PRELIMINARY scenario document (canonical R5 cap = 15000.0)."""
    return build_scenario(S.profile(), S.canonical_rule_evaluation())


def _factor(assumption_type: str, value, *, key: str | None = None) -> dict:
    return {
        "key": key or assumption_type,
        "assumption_type": assumption_type,
        "value": value,
        "unit": "ratio",
        "rationale": "illustrative explicit assumption",
    }


def _named(name: str, assumptions: list) -> dict:
    return {"name": name, "assumptions": assumptions}


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


# Delta fields are the ONLY place a legitimate NEGATIVE number may appear.
_DELTA_KEYS = {"absolute_delta", "percent_delta"}


def _non_delta_numbers(node):
    out = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in _DELTA_KEYS:
                continue
            out.extend(_non_delta_numbers(value))
    elif isinstance(node, list):
        for item in node:
            out.extend(_non_delta_numbers(item))
    elif isinstance(node, int | float) and not isinstance(node, bool):
        out.append(node)
    return out


def _strict_json_safe(result) -> None:
    """json.dumps(allow_nan=False) never raises; every number is finite; and the ONLY negatives
    live in delta fields (no negative-where-invalid)."""
    serialized = json.dumps(result, allow_nan=False)
    loaded = json.loads(serialized)
    for number in _all_numbers(loaded):
        assert math.isfinite(number)
    for number in _non_delta_numbers(loaded):
        assert number >= 0


def _row_by_name(result, name):
    for row in result["sets"]:
        if row["name"] == name:
            return row
    raise AssertionError(f"no comparison row named {name!r}")


# ---------------------------------------------------------------------------
# AS-1 comparison document: per-set derived echo + baseline-relative deltas; verbatim cap.
# ---------------------------------------------------------------------------


def test_as1_comparison_document_shape_and_baseline_relative_deltas():
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    assert cap == 15000.0
    sets = [
        _named("a_raw", []),  # baseline: raw cap 15000
        _named("b_util80", [_factor("utilization_factor", 0.8)]),  # 12000
        _named("c_eff60", [_factor("efficiency_ratio", 0.6)]),  # 9000
    ]
    result = compare_scenario_assumption_sets(document, sets)

    assert result["comparison_kind"] == ComparisonKind.COMPARED
    # (a) base lineage: scenario identity + bounded coverage status.
    lineage = result["base_lineage"]
    assert lineage["bbl"] == document["evaluated_input"]["bbl"]
    assert lineage["scenario_kind"] == document["scenario_kind"]
    assert lineage["contract_version"] == document["contract_version"]
    assert lineage["coverage_status"] == "conditional"
    assert lineage["data_completeness"] == document["data_completeness"]

    # (b) a per-set echo of the derived practical-usable-range obtained by calling derive READ-ONLY.
    for row, assumptions in zip(
        result["sets"],
        [[], [_factor("utilization_factor", 0.8)], [_factor("efficiency_ratio", 0.6)]],
        strict=False,
    ):
        expected = derive_practical_usable_range({**document, "assumptions": assumptions})
        assert row["derived"] == expected
        # The canonical cap is transported VERBATIM (byte-equal to derive's cap echo).
        assert row["metrics"]["canonical_cap_sq_ft"] == expected["canonical_cap_sq_ft"] == cap

    # (c) a baseline-relative delta for each numeric metric: absolute AND percent + breakdown.
    b_util = _row_by_name(result, "b_util80")
    deltas = {d["metric"]: d for d in b_util["metric_deltas"]}
    assert set(deltas) == set(COMPARISON_METRIC_KEYS)
    point = deltas["usable_range_point"]
    assert point["baseline_value"] == 15000.0
    assert point["set_value"] == 12000.0
    assert point["absolute_delta"] == -3000.0
    assert point["percent_delta"] == pytest.approx(-20.0)
    assert point["moved"] is True
    # The canonical cap is invariant across sets (a factor never changes the cap): delta reads 0.
    cap_delta = deltas["canonical_cap_sq_ft"]
    assert cap_delta["absolute_delta"] == 0.0
    assert cap_delta["percent_delta"] == 0.0
    assert cap_delta["moved"] is False


def test_as1_baseline_row_has_all_zero_self_deltas():
    document = _preliminary_document()
    result = compare_scenario_assumption_sets(
        document, [_named("a_raw", []), _named("b_util", [_factor("utilization_factor", 0.7)])]
    )
    baseline = result["sets"][0]
    assert baseline["is_baseline"] is True
    for delta in baseline["metric_deltas"]:
        assert delta["absolute_delta"] == 0.0
        assert delta["percent_delta"] == 0.0
        assert delta["moved"] is False
    assert baseline["changed_from_baseline"] is False


# ---------------------------------------------------------------------------
# AS-2 deterministic + total stable order (documented content key, baseline first).
# ---------------------------------------------------------------------------


def test_as2_byte_identical_across_input_reorderings():
    document = _preliminary_document()
    base = [
        _named("a_raw", []),
        _named("b_util80", [_factor("utilization_factor", 0.8)]),
        _named("c_eff50", [_factor("efficiency_ratio", 0.5)]),
        _named("d_util60", [_factor("utilization_factor", 0.6)]),
    ]
    forward = compare_scenario_assumption_sets(document, copy.deepcopy(base))
    reversed_ = compare_scenario_assumption_sets(document, list(reversed(copy.deepcopy(base))))
    shuffled = compare_scenario_assumption_sets(
        document, [copy.deepcopy(base[i]) for i in (2, 0, 3, 1)]
    )
    assert json.dumps(forward) == json.dumps(reversed_) == json.dumps(shuffled)


def test_as2_baseline_is_smallest_content_key_and_ordered_first():
    document = _preliminary_document()
    # Supplied out of order; the smallest content key ("a_raw") must be the baseline, first.
    sets = [
        _named("z_last", [_factor("utilization_factor", 0.9)]),
        _named("a_raw", []),
        _named("m_mid", [_factor("efficiency_ratio", 0.7)]),
    ]
    result = compare_scenario_assumption_sets(document, sets)
    assert result["baseline_set_name"] == "a_raw"
    assert result["sets"][0]["name"] == "a_raw"
    assert result["sets"][0]["is_baseline"] is True
    # The rest are ordered by content key ascending; only the first is the baseline.
    assert [row["name"] for row in result["sets"]] == ["a_raw", "m_mid", "z_last"]
    assert [row["is_baseline"] for row in result["sets"]] == [True, False, False]


def test_as2_identical_input_is_byte_identical():
    document = _preliminary_document()
    sets = [_named("a", [_factor("utilization_factor", 0.8)]), _named("b", [])]
    first = compare_scenario_assumption_sets(_preliminary_document(), copy.deepcopy(sets))
    second = compare_scenario_assumption_sets(document, copy.deepcopy(sets))
    assert json.dumps(first) == json.dumps(second)


def test_as2_duplicate_named_sets_are_interchangeable_and_stable():
    document = _preliminary_document()
    dup = _named("same", [_factor("utilization_factor", 0.8)])
    sets = [dup, _named("other", []), copy.deepcopy(dup)]
    forward = compare_scenario_assumption_sets(document, copy.deepcopy(sets))
    reordered = compare_scenario_assumption_sets(
        document, [copy.deepcopy(sets[i]) for i in (2, 1, 0)]
    )
    assert json.dumps(forward) == json.dumps(reordered)
    assert forward["set_count"] == 3


# ---------------------------------------------------------------------------
# AS-3 never invents / never Verified; not-comparable non-baseline set is marked, not dropped.
# ---------------------------------------------------------------------------


def test_as3_one_row_per_supplied_set_never_fabricates():
    document = _preliminary_document()
    sets = [
        _named("a", []),
        _named("b", [_factor("utilization_factor", 0.9)]),
        _named("c", [_factor("efficiency_ratio", 0.4)]),
    ]
    result = compare_scenario_assumption_sets(document, sets)
    assert result["set_count"] == len(sets) == 3
    assert len(result["sets"]) == 3


def test_as3_not_derivable_nonbaseline_set_is_marked_not_dropped():
    document = _preliminary_document()
    sets = [
        _named("a_good", []),  # baseline (smallest key), derivable
        # out of (0,1] -> derive fails closed
        _named("z_bad", [_factor("utilization_factor", 1.5)]),
    ]
    result = compare_scenario_assumption_sets(document, sets)
    assert result["comparison_kind"] == ComparisonKind.COMPARED
    assert result["set_count"] == 2
    assert result["comparable_count"] == 1
    bad = _row_by_name(result, "z_bad")
    # Kept in order, flagged not-comparable, NO fabricated metric/delta, carries a reason.
    assert bad["comparable"] is False
    assert bad["metrics"] is None
    assert bad["not_comparable_reason"]
    for delta in bad["metric_deltas"]:
        assert delta["absolute_delta"] is None
        assert delta["percent_delta"] is None
        assert delta["not_computable_reason"]
    _strict_json_safe(result)


def test_as3_comparison_is_never_verified_and_honestly_labelled():
    document = _preliminary_document()
    result = compare_scenario_assumption_sets(
        document, [_named("a", [_factor("utilization_factor", 0.8)]), _named("b", [])]
    )
    assert "verified" not in _coverage_values(result)
    assert "verified" not in _all_strings(result)
    assert result["coverage_status"] == "conditional"
    assert result["needs_review"] is True
    assert result["not_verified_disclaimer"] == document["not_verified_disclaimer"]
    assert result["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER
    assert result["label"] == COMPARISON_LABEL
    assert "ILLUSTRATIVE" in COMPARISON_LABEL
    assert "NOT Verified" in COMPARISON_LABEL


def test_as3_incoming_verified_coverage_is_capped_to_conditional():
    document = _preliminary_document()
    tampered = copy.deepcopy(document)
    tampered["coverage_status"] = "verified"
    result = compare_scenario_assumption_sets(tampered, [_named("a", []), _named("b", [])])
    assert result["coverage_status"] == "conditional"
    assert result["base_lineage"]["coverage_status"] == "conditional"
    assert "verified" not in _coverage_values(result)


# ---------------------------------------------------------------------------
# AS-4 typed-error + degenerate handling: no unhandled raise.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("sets", [[], [_named("only", [])]])
def test_as4_fewer_than_two_sets_is_invalid(sets):
    document = _preliminary_document()
    result = compare_scenario_assumption_sets(document, sets)
    assert result["comparison_kind"] == ComparisonKind.INVALID
    assert result["sets"] == []
    assert result["invalid_reason"]
    _strict_json_safe(result)


@pytest.mark.parametrize("bad_container", [{"a": 1}, "notalist", 42, 3.0, None, (0.5, 0.8)])
def test_as4_malformed_container_is_invalid(bad_container):
    document = _preliminary_document()
    result = compare_scenario_assumption_sets(document, bad_container)
    assert result["comparison_kind"] == ComparisonKind.INVALID
    assert result["invalid_reason"]
    _strict_json_safe(result)


@pytest.mark.parametrize(
    "rule_evaluation_factory",
    [S.unsupported_rule_evaluation, S.conflict_rule_evaluation, S.missing_lot_area_rule_evaluation],
)
def test_as4_no_cap_document_is_typed_empty_with_reason(rule_evaluation_factory):
    document = build_scenario(S.profile(), rule_evaluation_factory())
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None
    result = compare_scenario_assumption_sets(
        document, [_named("a", []), _named("b", [_factor("utilization_factor", 0.8)])]
    )
    assert result["comparison_kind"] == ComparisonKind.EMPTY
    assert result["sets"] == []
    assert result["empty_reason"]
    assert 15000.0 not in _all_numbers(result)
    _strict_json_safe(result)


def test_as4_not_derivable_baseline_is_invalid():
    document = _preliminary_document()
    # The smallest-content-key set ("aaa_bad") is not derivable -> no baseline -> INVALID.
    sets = [
        _named("aaa_bad", [_factor("utilization_factor", 1.5)]),  # out of domain -> not derivable
        _named("bbb_ok", [_factor("utilization_factor", 0.8)]),
    ]
    result = compare_scenario_assumption_sets(document, sets)
    assert result["comparison_kind"] == ComparisonKind.INVALID
    assert result["sets"] == []
    assert result["baseline_set_name"] is None
    assert result["invalid_reason"]
    _strict_json_safe(result)


def test_as4_degenerate_document_is_typed_no_crash():
    for degenerate in ({}, None, "notadoc", 5):
        result = compare_scenario_assumption_sets(degenerate, [_named("a", []), _named("b", [])])
        # No positive cap -> typed EMPTY; never a crash, always strict-JSON-safe.
        assert result["comparison_kind"] == ComparisonKind.EMPTY
        _strict_json_safe(result)


def test_as4_percent_delta_against_zero_baseline_is_not_computable():
    """Defense-in-depth: a percent delta against a zero baseline metric yields a typed
    not-computable percent marker (no ZeroDivisionError, no Inf/NaN); the absolute delta is
    still reported. A DERIVED baseline is always positive, so this guard is proven directly."""
    zero_delta = _metric_delta("usable_range_point", 0.0, 5.0)
    assert zero_delta["absolute_delta"] == 5.0  # absolute is still computed
    assert zero_delta["percent_delta"] is None
    assert zero_delta["not_computable_reason"]
    assert math.isfinite(zero_delta["absolute_delta"])


@pytest.mark.parametrize("baseline_value", [None, float("nan"), float("inf"), "x"])
def test_as4_absent_or_nonfinite_baseline_metric_is_not_computable(baseline_value):
    delta = _metric_delta("usable_range_point", baseline_value, 5.0)
    assert delta["absolute_delta"] is None
    assert delta["percent_delta"] is None
    assert delta["not_computable_reason"]


# ---------------------------------------------------------------------------
# AS-5 strict-JSON-safe via the SHARED sanitizer.
# ---------------------------------------------------------------------------


def test_as5_output_is_strict_json_safe_with_negatives_only_in_deltas():
    document = _preliminary_document()
    sets = [
        _named("a_raw", []),
        _named("b_util50", [_factor("utilization_factor", 0.5)]),  # 7500 -> negative deltas
        _named("c_bad", [_factor("utilization_factor", 5.0)]),  # not-comparable row
    ]
    result = compare_scenario_assumption_sets(document, sets)
    _strict_json_safe(result)
    # A reduction set produces a genuine NEGATIVE finite delta - preserved, not marked/dropped.
    b_util = _row_by_name(result, "b_util50")
    point = {d["metric"]: d for d in b_util["metric_deltas"]}["usable_range_point"]
    assert point["absolute_delta"] == -7500.0
    assert isinstance(point["absolute_delta"], float)  # a real number, not an unsafe marker dict
    assert point["percent_delta"] == pytest.approx(-50.0)


@pytest.mark.parametrize(
    "bad_value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        -0.5,
        10**400,
        pytest.param(10**5000, id="pow10_5000"),
    ],
)
def test_as5_malformed_assumption_value_is_typed_marker_and_json_safe(bad_value):
    """A malformed assumption VALUE is surfaced through the SHARED sanitizer as a typed, bounded,
    address-free marker (never echoed raw); the set fails closed to a not-comparable row and the
    whole output stays strict-JSON-safe and deterministic run-to-run."""
    document = _preliminary_document()
    tainted = _named("z_tainted", [_factor("utilization_factor", bad_value)])
    sets = [_named("a_good", []), tainted]
    result = compare_scenario_assumption_sets(document, sets)

    assert result["comparison_kind"] == ComparisonKind.COMPARED
    _strict_json_safe(result)
    serialized = json.dumps(result)
    assert "unsafe_value_removed" in serialized  # a typed marker stands in for the raw value
    again = compare_scenario_assumption_sets(_preliminary_document(), copy.deepcopy(sets))
    assert serialized == json.dumps(again)


def test_as5_unserializable_object_value_is_typed_and_json_safe():
    document = _preliminary_document()

    class _Weird:
        pass

    sets = [_named("a_good", []), _named("z", [_factor("utilization_factor", _Weird())])]
    result = compare_scenario_assumption_sets(document, sets)
    assert result["comparison_kind"] == ComparisonKind.COMPARED
    _strict_json_safe(result)  # would raise on a raw object without sanitization
    serialized = json.dumps(result)
    assert "unsafe_value_removed" in serialized
    assert "_Weird" in serialized
    assert " at 0x" not in serialized  # never an address-bearing repr


def test_as5_uses_shared_sanitizer_and_does_not_reimplement_it():
    """AS-5: comparison.py IMPORTS and uses the shared _json_safety sanitizer and does NOT
    define / re-duplicate the sanitizer functions (the duplication M5-T009 removed)."""
    source = inspect.getsource(comparison_module)
    assert "from ._json_safety import _json_safe" in source
    # It does not re-define the shared sanitizer functions locally.
    for banned in ("def _json_safe(", "def _safe_scalar(", "def _unsafe_marker(", "def _safe_key("):
        assert banned not in source
    # The imported symbol is the very object exported by the shared module.
    from app.scenario import _json_safety

    assert comparison_module._json_safe is _json_safety._json_safe


# ---------------------------------------------------------------------------
# AS-6 read-only consumption; no legal recompute; no aliasing.
# ---------------------------------------------------------------------------


def test_as6_inputs_are_byte_unchanged_and_not_aliased():
    document = _preliminary_document()
    sets = [
        _named("a", [_factor("utilization_factor", 0.8)]),
        _named("b", [_factor("efficiency_ratio", 0.5)]),
    ]
    document_before = json.dumps(document)
    sets_before = json.dumps(sets)

    result = compare_scenario_assumption_sets(document, sets)

    assert json.dumps(document) == document_before
    assert json.dumps(sets) == sets_before
    # Mutating the result never reaches back into the caller's input.
    result["sets"][0]["assumption_set"].append({"injected": True})
    assert json.dumps(sets) == sets_before
    assert json.dumps(document) == document_before


def test_as6_consumes_derive_readonly_no_recompute():
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    assumptions = [_factor("utilization_factor", 0.8)]
    result = compare_scenario_assumption_sets(
        document, [_named("a", []), _named("b", assumptions)]
    )
    row = _row_by_name(result, "b")
    # The row's derived breakdown is exactly the accepted derive() output for the same set:
    # comparison CONSUMES derive.py, never recomputes a legal value.
    expected_derived = derive_practical_usable_range({**document, "assumptions": assumptions})
    assert row["derived"] == expected_derived
    assert row["metrics"]["canonical_cap_sq_ft"] == cap
    assert row["metrics"]["usable_range_point"] == cap * 0.8 == 12000.0


# ---------------------------------------------------------------------------
# AS-7 contract-free + offline.
# ---------------------------------------------------------------------------


def test_as7_module_imports_only_allowed_dependencies():
    """comparison.py imports only stdlib + .derive + .constants + ._json_safety (contract-free):
    no builder/models/contract/ranking/sensitivity, no packages.contracts, no
    network/persistence."""
    source = inspect.getsource(comparison_module)
    forbidden = (
        "from .builder",
        "from .models",
        "from .contract",
        "from .ranking",
        "from .sensitivity",
        "packages.contracts",
        "import requests",
        "import httpx",
        "import urllib",
        "import socket",
        "supabase",
        "psycopg",
        "sqlalchemy",
    )
    for token in forbidden:
        assert token not in source, f"comparison.py must not reference {token!r}"
    assert "from .derive import" in source
    assert "from ._json_safety import" in source
    assert "from .constants import" in source


def test_as7_runs_fully_offline_with_sockets_blocked(monkeypatch):
    """No network I/O on any path: with socket creation hard-blocked, a comparison still
    produces a full COMPARED document."""

    def _blocked(*args, **kwargs):
        raise AssertionError("network access attempted in an offline comparison")

    monkeypatch.setattr(socket, "socket", _blocked)
    document = _preliminary_document()
    result = compare_scenario_assumption_sets(
        document,
        [_named("a", []), _named("b", [_factor("utilization_factor", 0.8)])],
    )
    assert result["comparison_kind"] == ComparisonKind.COMPARED
    _strict_json_safe(result)


def test_as7_output_is_strict_json_safe_on_every_path():
    document = _preliminary_document()
    sets = [
        _named("a_raw", []),
        _named(
            "b_two_factors", [_factor("utilization_factor", 0.8), _factor("efficiency_ratio", 0.5)]
        ),
        _named("c_bad", [_factor("utilization_factor", 1.5)]),  # not-comparable row
        _named("d_note", [_factor("note", 0.9)]),  # unrecognized -> raw cap, still comparable
    ]
    result = compare_scenario_assumption_sets(document, sets)
    assert result["comparison_kind"] == ComparisonKind.COMPARED
    assert result["set_count"] == 4
    _strict_json_safe(result)


# ---------------------------------------------------------------------------
# AS-3/AS-4 (rework): explicitly-supplied assumption LIST enforced at the public boundary.
# A missing / null / non-list `assumptions` is a TYPED not-comparable row (NOT a raw empty set);
# an explicit [] stays valid; absent / non-string names -> None (never fabricated); bare lists ok.
# ---------------------------------------------------------------------------


def _rows_with_name_none(result):
    return [row for row in result["sets"] if row["name"] is None]


def test_rework_missing_assumptions_is_typed_not_comparable_not_raw_empty():
    """A named set with NO `assumptions` key must not silently become the raw scenario: it is a
    typed not-comparable row (kept in order), with no fabricated metric or delta."""
    document = _preliminary_document()
    sets = [
        _named("a_baseline", []),  # explicit [] -> valid raw baseline (smallest content key)
        {"name": "z_missing"},  # NO assumptions key -> typed failure, NOT a raw empty set
    ]
    result = compare_scenario_assumption_sets(document, sets)

    assert result["comparison_kind"] == ComparisonKind.COMPARED
    assert result["set_count"] == 2
    assert result["comparable_count"] == 1  # only the explicit-[] baseline is comparable
    missing = _row_by_name(result, "z_missing")
    assert missing["comparable"] is False
    assert missing["metrics"] is None
    assert missing["not_comparable_reason"]
    assert "missing or null" in missing["not_comparable_reason"]
    # It did NOT become the raw scenario: no derived range, no fabricated deltas.
    assert missing["derived"] is None
    for delta in missing["metric_deltas"]:
        assert delta["absolute_delta"] is None
        assert delta["percent_delta"] is None
        assert delta["not_computable_reason"]
    _strict_json_safe(result)


def test_rework_null_assumptions_is_typed_not_comparable_not_raw_empty():
    """A named set with `assumptions: null` is a typed not-comparable row, never a raw empty set."""
    document = _preliminary_document()
    sets = [
        _named("a_baseline", []),
        {"name": "z_null", "assumptions": None},
    ]
    result = compare_scenario_assumption_sets(document, sets)
    assert result["comparison_kind"] == ComparisonKind.COMPARED
    assert result["comparable_count"] == 1
    row = _row_by_name(result, "z_null")
    assert row["comparable"] is False
    assert row["metrics"] is None
    assert "missing or null" in row["not_comparable_reason"]
    _strict_json_safe(result)


@pytest.mark.parametrize(
    "bad_assumptions", [{"not": "a list"}, "notalist", 42, 3.0, (0.5, 0.8)]
)
def test_rework_nonlist_assumptions_is_typed_not_comparable(bad_assumptions):
    """A named set whose `assumptions` is present but NOT a list is a typed structural failure -
    never passed on to derive as a malformed container."""
    document = _preliminary_document()
    sets = [
        _named("a_baseline", []),
        {"name": "z_malformed", "assumptions": bad_assumptions},
    ]
    result = compare_scenario_assumption_sets(document, sets)
    assert result["comparison_kind"] == ComparisonKind.COMPARED
    assert result["comparable_count"] == 1
    row = _row_by_name(result, "z_malformed")
    assert row["comparable"] is False
    assert row["metrics"] is None
    assert "must be a list" in row["not_comparable_reason"]
    _strict_json_safe(result)


def test_rework_explicit_empty_list_remains_valid_raw_scenario():
    """RETAINED behavior: an explicitly-supplied [] is a valid raw-scenario set (derivable), and it
    is distinct from a missing/null assumptions (which is not-comparable)."""
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    result = compare_scenario_assumption_sets(
        document,
        [_named("a_raw", []), _named("b_util", [_factor("utilization_factor", 0.8)])],
    )
    assert result["comparison_kind"] == ComparisonKind.COMPARED
    assert result["comparable_count"] == 2
    raw = _row_by_name(result, "a_raw")
    assert raw["comparable"] is True
    assert raw["metrics"]["usable_range_point"] == cap == 15000.0  # explicit [] -> raw cap
    _strict_json_safe(result)


def test_rework_missing_and_explicit_empty_diverge():
    """The corrected boundary: an EXPLICIT [] is comparable while a MISSING assumptions is not -
    directly proving a missing/null assumptions is no longer coerced into a raw empty set."""
    document = _preliminary_document()
    result = compare_scenario_assumption_sets(
        document, [_named("a_explicit_empty", []), {"name": "b_missing"}]
    )
    explicit = _row_by_name(result, "a_explicit_empty")
    missing = _row_by_name(result, "b_missing")
    assert explicit["comparable"] is True
    assert missing["comparable"] is False


def test_rework_absent_name_is_none_and_still_comparable():
    """A named-set dict with NO `name` key surfaces name None (never fabricated); an explicit
    assumptions list still derives, so the set is comparable."""
    document = _preliminary_document()
    sets = [
        {"assumptions": []},  # no name -> None; explicit [] -> comparable raw set
        _named("b_util", [_factor("utilization_factor", 0.8)]),
    ]
    result = compare_scenario_assumption_sets(document, sets)
    assert result["comparison_kind"] == ComparisonKind.COMPARED
    assert result["comparable_count"] == 2
    unnamed = _rows_with_name_none(result)
    assert len(unnamed) == 1
    assert unnamed[0]["name"] is None
    assert unnamed[0]["comparable"] is True
    _strict_json_safe(result)


def test_rework_nonstring_name_is_none_not_fabricated():
    """A non-string `name` (e.g. an int) is surfaced as None - identity is never fabricated - and
    an explicit assumptions list still derives."""
    document = _preliminary_document()
    sets = [
        {"name": 123, "assumptions": []},  # non-string name -> None
        _named("b_util", [_factor("utilization_factor", 0.8)]),
    ]
    result = compare_scenario_assumption_sets(document, sets)
    assert result["comparison_kind"] == ComparisonKind.COMPARED
    unnamed = _rows_with_name_none(result)
    assert len(unnamed) == 1
    assert unnamed[0]["name"] is None
    assert unnamed[0]["comparable"] is True
    _strict_json_safe(result)


def test_rework_bare_list_entries_are_unnamed_comparable_sets():
    """A bare assumptions list (not wrapped in a named dict) is accepted as an unnamed set: name
    None, derived from those assumptions."""
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    sets = [
        [],  # bare empty list -> unnamed raw set (smallest content key -> baseline)
        [_factor("utilization_factor", 0.8)],  # bare list with a factor -> unnamed set
    ]
    result = compare_scenario_assumption_sets(document, sets)
    assert result["comparison_kind"] == ComparisonKind.COMPARED
    assert result["set_count"] == 2
    assert result["comparable_count"] == 2
    unnamed = _rows_with_name_none(result)
    assert len(unnamed) == 2
    assert all(row["comparable"] for row in unnamed)
    baseline = result["sets"][0]
    assert baseline["name"] is None
    assert baseline["metrics"]["usable_range_point"] == cap == 15000.0
    _strict_json_safe(result)


def test_rework_missing_assumptions_baseline_is_typed_invalid():
    """When the smallest-content-key set is a missing-assumptions (structural not-comparable) row,
    it is the baseline and the whole comparison fails closed to a typed INVALID - never a raise and
    never a fabricated raw baseline."""
    document = _preliminary_document()
    sets = [
        {"name": "aaa_missing"},  # smallest content key, structural not-comparable -> baseline
        _named("bbb_ok", [_factor("utilization_factor", 0.8)]),
    ]
    result = compare_scenario_assumption_sets(document, sets)
    assert result["comparison_kind"] == ComparisonKind.INVALID
    assert result["sets"] == []
    assert result["baseline_set_name"] is None
    assert result["invalid_reason"]
    _strict_json_safe(result)


# ---------------------------------------------------------------------------
# AS-3 (rework): the canonical NOT_VERIFIED_DISCLAIMER is stamped on EVERY public outcome,
# regardless of an empty / whitespace / arbitrary / missing / non-string input document
# disclaimer. A caller can never suppress or replace the honesty warning on a contract-free,
# never-Verified comparison.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "tampered_disclaimer",
    ["", "   ", "\t\n", "trust me, this is verified", "OK", None, 123, 4.5, True, {"x": 1}, ["a"]],
)
def test_rework_public_compared_outcome_always_carries_canonical_disclaimer(tampered_disclaimer):
    """Every COMPARED outcome carries the canonical NOT_VERIFIED_DISCLAIMER verbatim even when the
    input document's disclaimer is empty, whitespace-only, arbitrary, or a non-string: the honesty
    warning is stamped by the comparison, never taken (and never suppressible) from the input."""
    document = _preliminary_document()
    tampered = copy.deepcopy(document)
    tampered["not_verified_disclaimer"] = tampered_disclaimer
    result = compare_scenario_assumption_sets(
        tampered, [_named("a", []), _named("b", [_factor("utilization_factor", 0.8)])]
    )
    assert result["comparison_kind"] == ComparisonKind.COMPARED
    assert result["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER
    assert result["not_verified_disclaimer"]  # a non-empty honest warning always survives
    # The tampered input value never leaks into the output (only the canonical disclaimer appears).
    _strict_json_safe(result)


def test_rework_missing_disclaimer_key_still_carries_canonical_disclaimer():
    """A document with NO ``not_verified_disclaimer`` key at all still yields the canonical
    disclaimer on the COMPARED outcome (never an absent / null warning)."""
    document = _preliminary_document()
    tampered = copy.deepcopy(document)
    tampered.pop("not_verified_disclaimer", None)
    result = compare_scenario_assumption_sets(
        tampered, [_named("a", []), _named("b", [_factor("utilization_factor", 0.8)])]
    )
    assert result["comparison_kind"] == ComparisonKind.COMPARED
    assert result["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER
    _strict_json_safe(result)


@pytest.mark.parametrize(
    "sets_input, expected_kind",
    [
        ([], ComparisonKind.INVALID),  # fewer than two sets
        ([_named("only", [])], ComparisonKind.INVALID),  # one set
        ("notalist", ComparisonKind.INVALID),  # malformed container
    ],
)
def test_rework_invalid_outcomes_also_carry_canonical_disclaimer(sets_input, expected_kind):
    """Not just COMPARED: the typed INVALID degenerate outcomes ALSO stamp the canonical disclaimer,
    even when the input document's disclaimer is empty. (Every public outcome, not only the happy
    path.)"""
    document = _preliminary_document()
    tampered = copy.deepcopy(document)
    tampered["not_verified_disclaimer"] = ""  # empty input disclaimer
    result = compare_scenario_assumption_sets(tampered, sets_input)
    assert result["comparison_kind"] == expected_kind
    assert result["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER
    _strict_json_safe(result)


def test_rework_empty_outcome_carries_canonical_disclaimer():
    """The typed EMPTY outcome (a document that surfaces no positive cap) carries the canonical
    disclaimer even when the input document's disclaimer is empty."""
    document = build_scenario(S.profile(), S.unsupported_rule_evaluation())
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None
    tampered = copy.deepcopy(document)
    tampered["not_verified_disclaimer"] = ""
    result = compare_scenario_assumption_sets(
        tampered, [_named("a", []), _named("b", [_factor("utilization_factor", 0.8)])]
    )
    assert result["comparison_kind"] == ComparisonKind.EMPTY
    assert result["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER
    _strict_json_safe(result)
