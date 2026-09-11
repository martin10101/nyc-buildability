"""Focused unit pack for the shared strict-JSON-safety sanitizer (task M5-T009).

Covers the extracted sanitizer surface in ``app.scenario._json_safety`` (the single source of
truth that ``ranking`` and ``sensitivity`` both import - AS-2) plus the two defense-in-depth
guards closed in the same change:

* AS-3 L1: a non-deepcopyable assumption value (a lock / generator) supplied to either public
  consumer (``rank_scenario_assumption_sets`` / ``analyze_scenario_sensitivity``) yields a typed
  not-scorable / marker outcome and does NOT raise.
* AS-4 L2: a cyclic (self-referential) value routed through the shared ``_json_safe`` yields a
  typed ``cycle`` marker, and a pathologically-deep acyclic value is BOUNDED to a typed
  ``max_depth`` marker at ``_MAX_JSON_SAFE_DEPTH`` - neither raises ``RecursionError`` (the walk
  uses an explicit traversal stack, not native recursion), and the bounded output stays
  ``json.dumps(..., allow_nan=False)``-safe (an unbounded deep rendering would make ``json.dumps``,
  which recurses per nesting level, itself raise). Acyclic values up to the bound (incl. the
  410-level regressions) still render in full, byte-identically.
* AS-5: ``json.dumps(result, allow_nan=False)`` never raises, no NaN/Inf/negative is emitted, no
  object address leaks, and identical inputs render byte-identically.

Behavior-neutrality of the extraction itself (AS-1) is proven by the UNCHANGED
``test_scenario_ranking.py`` and ``test_scenario_sensitivity.py`` suites still passing; this file
only adds coverage for the shared module and the new guards.

Offline, deterministic, stdlib-only inputs.
"""

from __future__ import annotations

import json
import math
import sys
import threading
from typing import Any

import pytest

from app.scenario import (
    RankingKind,
    RankingObjective,
    SensitivityKind,
    SensitivityVariable,
    analyze_scenario_sensitivity,
    build_scenario,
    rank_scenario_assumption_sets,
)
from app.scenario._json_safety import (
    _MAX_JSON_SAFE_DEPTH,
    _bounded_repr,
    _json_safe,
    _json_safe_mapping,
    _safe_key,
    _safe_scalar_repr,
    _unsafe_key_token,
    _unsafe_marker,
)

from . import _support as S

OBJ = RankingObjective.MAXIMIZE_ILLUSTRATIVE_USABLE_AREA
VAR = SensitivityVariable.UTILIZATION_FACTOR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _preliminary_document() -> dict:
    """A real PRELIMINARY scenario document (canonical R5 cap = 15000.0)."""
    return build_scenario(S.profile(), S.canonical_rule_evaluation())


def _factor(assumption_type: str, value) -> dict:
    return {
        "key": assumption_type,
        "assumption_type": assumption_type,
        "value": value,
        "unit": "ratio",
        "rationale": "illustrative explicit assumption",
    }


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


def _assert_strict_json_safe(value) -> str:
    """json.dumps(allow_nan=False) never raises; no NaN/Inf/negative anywhere; no address leak.
    Returns the serialized string for further assertions."""
    serialized = json.dumps(value, allow_nan=False)
    for number in _all_numbers(json.loads(serialized)):
        assert math.isfinite(number)
        assert number >= 0
    assert " at 0x" not in serialized  # no CPython default object address leaked
    return serialized


# ---------------------------------------------------------------------------
# AS-2: single source of truth + the sanitizer surface (byte-preserving).
# ---------------------------------------------------------------------------


def test_shared_module_is_the_single_source_of_truth():
    """The sanitizer functions live in app.scenario._json_safety, and the two consumers import
    that identical object (no private per-module copy)."""
    import app.scenario.ranking as ranking
    import app.scenario.sensitivity as sensitivity

    assert ranking._json_safe is _json_safe
    assert sensitivity._json_safe is _json_safe
    assert ranking._unsafe_marker is _unsafe_marker


def test_safe_values_pass_through_unchanged():
    value = {"b": [1, 2.5, "s", True, False, None], "a": {"n": 0, "z": 12345}}
    result = _json_safe(value)
    assert result == value
    assert list(result.keys()) == ["b", "a"]  # insertion order preserved


def test_tuple_emits_as_list():
    assert _json_safe((1, 2, 3)) == [1, 2, 3]
    assert _json_safe({"t": (True, "x")}) == {"t": [True, "x"]}


@pytest.mark.parametrize(
    ("value", "kind", "type_name"),
    [
        (float("nan"), "nan", "float"),
        (float("inf"), "infinity", "float"),
        (float("-inf"), "infinity", "float"),
        (-5, "negative", "int"),
        (-0.25, "negative", "float"),
    ],
)
def test_nonfinite_and_negative_numbers_become_typed_markers(value, kind, type_name):
    marker = _json_safe(value)
    assert marker["unsafe_value_removed"] is True
    assert marker["unsafe_kind"] == kind
    assert marker["unsafe_value_type"] == type_name
    assert "unsafe_value_repr" in marker


def test_float_overflowing_int_is_described_by_magnitude_never_decimal_expanded():
    big = 10**400  # float(big) raises OverflowError; bit_length far exceeds the decimal-safe cap
    marker = _json_safe(big)
    assert marker["unsafe_kind"] == "overflow"
    assert marker["unsafe_value_type"] == "int"
    assert marker["unsafe_value_repr"].startswith("int(sign=+, bit_length=")


def test_small_int_repr_is_exact_but_huge_int_is_magnitude():
    assert _safe_scalar_repr(42) == "42"
    assert _safe_scalar_repr(-7) == "-7"
    assert _safe_scalar_repr(2**300).startswith("int(sign=+, bit_length=301")


def test_unsupported_object_marker_carries_type_only_no_repr():
    marker = _json_safe(object())
    assert marker["unsafe_kind"] == "unsupported"
    assert marker["unsafe_value_type"] == "object"
    assert "unsafe_value_repr" not in marker  # no address-bearing repr


def test_bounded_repr_truncates_long_renderings():
    assert _bounded_repr("short") == "short"
    long = "x" * 200
    assert _bounded_repr(long) == "x" * 120 + "...(truncated)"


def test_nonstring_dict_keys_are_made_safe():
    result = _json_safe_mapping({(1, 2): "tuple_key", float("nan"): "nan_key", 5: "int_key"})
    assert result["__unsafe_key__:<tuple>"] == "tuple_key"
    assert result["__unsafe_key__:nan"] == "nan_key"
    assert result[5] == "int_key"  # a finite numeric key passes through verbatim


def test_colliding_rejected_keys_are_de_collided_not_overwritten():
    # Two DISTINCT tuple keys both render to the same token; the second is de-collided.
    result = _json_safe_mapping({(1,): "a", (2,): "b"})
    assert set(result) == {"__unsafe_key__:<tuple>", "__unsafe_key__:<tuple>#1"}
    assert sorted(result.values()) == ["a", "b"]


def test_safe_key_and_unsafe_key_token_are_deterministic():
    assert _safe_key("k") == "k"
    assert _safe_key(None) is None
    assert _safe_key(True) is True
    assert _safe_key(3.5) == 3.5
    assert _unsafe_key_token(object()) == "__unsafe_key__:<object>"
    assert _unsafe_key_token((1,)) == _unsafe_key_token((2,))  # type-only, address-free


# ---------------------------------------------------------------------------
# AS-4: L2 traversal protection - cycle -> typed marker; deep acyclic bounded to a
# typed max_depth marker at _MAX_JSON_SAFE_DEPTH; never RecursionError (explicit
# traversal stack, not native recursion) AND the bounded output stays json.dumps-safe.
# ---------------------------------------------------------------------------


def test_self_referential_list_yields_cycle_marker_not_recursionerror():
    a: list = []
    a.append(a)
    result = _json_safe(a)
    assert result[0]["unsafe_kind"] == "cycle"
    assert result[0]["unsafe_value_type"] == "list"
    _assert_strict_json_safe(result)


def test_self_referential_dict_yields_cycle_marker_not_recursionerror():
    d: dict = {}
    d["self"] = d
    result = _json_safe(d)
    assert result["self"]["unsafe_kind"] == "cycle"
    assert result["self"]["unsafe_value_type"] == "dict"
    _assert_strict_json_safe(result)


def test_mutually_referential_containers_are_bounded():
    left: dict = {}
    right: dict = {"left": left}
    left["right"] = right
    result = _json_safe(left)
    # The ancestor 'left' reached again through right -> a cycle marker; no RecursionError.
    assert result["right"]["left"]["unsafe_kind"] == "cycle"
    _assert_strict_json_safe(result)


def _nested_list_chain(depth: int) -> list:
    """An acyclic list nested ``depth`` levels deep with an empty list at the bottom:
    ``[[[ ... [] ... ]]]``. Built iteratively so the FIXTURE never itself recurses."""
    value: list = []
    for _ in range(depth):
        value = [value]
    return value


def _bounded_list_chain_depth(node: Any) -> int:
    """Walk a single-child *bounded* list chain iteratively (``json.dumps`` would itself recurse):
    count nested lists until the innermost list is reached, assert that innermost list holds the
    single typed ``max_depth`` marker (a bounded deep value is truncated to a marker, never rendered
    in full), and return the container depth. For any input deeper than the bound this equals
    ``_MAX_JSON_SAFE_DEPTH``."""
    depth = 1
    while isinstance(node, list) and node and isinstance(node[0], list):
        node = node[0]
        depth += 1
    assert isinstance(node, list) and len(node) == 1  # innermost list holds exactly one marker
    marker = node[0]
    assert marker["unsafe_kind"] == "max_depth"
    assert marker["unsafe_value_type"] == "list"
    return depth


def test_acyclic_410_level_list_chain_renders_in_full_byte_identical():
    """REGRESSION (M5-T009 revise): an acyclic list nested 410 levels deep - ABOVE the retired
    ~400-level recursion-budget cutoff that previously truncated it to a ``max_depth`` marker - is
    strict-JSON-representable and must render IN FULL. 'before' = ``json.dumps`` of the untouched
    value (exactly the pre-extraction render, since JSON-safe values pass through unchanged);
    'after' = ``json.dumps(_json_safe(value))``. They are BYTE-IDENTICAL with NO marker: the
    explicit-stack traversal never truncates on depth and never depends on the recursion budget."""
    value = _nested_list_chain(410)
    before = json.dumps(value, ensure_ascii=True)
    after = json.dumps(_json_safe(value), ensure_ascii=True)
    assert after == before  # byte-identical to the previously-successful output
    assert "unsafe_kind" not in after  # no cycle/max_depth/any marker


def test_acyclic_410_level_dict_chain_renders_in_full_byte_identical():
    """REGRESSION (M5-T009 revise): the dict analogue - an acyclic dict nested 410 levels deep,
    above the retired ~400-level cutoff - renders byte-identically to the pre-extraction output,
    with insertion order preserved and NO marker."""
    depth = 410
    value: dict = {"leaf": 0, "tag": "end"}
    for level in range(depth):
        value = {"level": level, "child": value, "sibling": [level, level + 1]}
    before = json.dumps(value, ensure_ascii=True)
    after = json.dumps(_json_safe(value), ensure_ascii=True)
    assert after == before  # byte-identical to the previously-successful output
    assert "unsafe_kind" not in after


def test_pathologically_deep_value_is_bounded_to_marker_and_json_dumps_stays_safe():
    """REGRESSION (M5-T009 revise) - AS-4 + AS-5 reconciled: a pathologically-deep ACYCLIC value
    (5000 levels) routed through ``_json_safe`` (a) does NOT raise ``RecursionError`` while being
    built (the walk is iterative, and the sanitizer never touches the recursion limit), (b) is
    BOUNDED at ``_MAX_JSON_SAFE_DEPTH`` to a typed ``max_depth`` marker - NOT rendered in full - and
    therefore (c) SERIALIZES: ``json.dumps(result, allow_nan=False)``, which itself recurses once
    per nesting level, does NOT raise. A full 5000-level nesting would make that ``json.dumps``
    ``RecursionError`` ('deeply nested containers alone do not make json.dumps safe'), so full depth
    is truncated to a marker exactly as AS-4 requires ('bounded by a documented max depth')."""
    depth = 5000
    value = _nested_list_chain(depth)
    limit_before = sys.getrecursionlimit()
    result = _json_safe(value)  # iterative build: must NOT raise RecursionError
    assert sys.getrecursionlimit() == limit_before  # the sanitizer did not touch the limit
    assert _bounded_list_chain_depth(result) == _MAX_JSON_SAFE_DEPTH  # bounded, not the full 5000
    # The regression the review requires: json.dumps(..., allow_nan=False) on the pathological-depth
    # OUTCOME must NOT raise (it would, unbounded, since json.dumps recurses per nesting level).
    serialized = json.dumps(result, allow_nan=False)
    assert '"unsafe_kind": "max_depth"' in serialized


def test_max_depth_bound_is_a_fixed_constant_not_derived_from_the_recursion_limit():
    """AS-4: the depth bound is a FIXED documented constant (``_MAX_JSON_SAFE_DEPTH``), NOT sized
    from ``sys.getrecursionlimit()`` - the RETIRED guard derived its cutoff from the limit, which
    both truncated previously-successful outputs and went stale. RAISING the recursion limit does
    NOT move the bound (a limit-derived cutoff would grow with the limit), and the iterative
    traversal renders without touching the call stack. The limit is restored in ``finally``."""
    value = _nested_list_chain(2000)
    original_limit = sys.getrecursionlimit()
    try:
        # Raise FAR above both the bound and the structure depth (raising the limit never crashes).
        sys.setrecursionlimit(4000)
        depth_high = _bounded_list_chain_depth(_json_safe(value))
    finally:
        sys.setrecursionlimit(original_limit)
    result_default = _json_safe(value)
    depth_default = _bounded_list_chain_depth(result_default)
    # Same fixed bound under a 4x-higher limit and under the default limit: NOT limit-derived.
    assert depth_high == depth_default == _MAX_JSON_SAFE_DEPTH
    # Bounded output serializes with allow_nan=False (json.dumps recurses per level; the bound keeps
    # it in range) - asserted directly to avoid the recursive _all_numbers walk over a 500-deep
    # value.
    assert '"unsafe_kind": "max_depth"' in json.dumps(result_default, allow_nan=False)


def test_shared_but_acyclic_reference_is_not_a_false_cycle():
    """Path-scoped seen-set: the SAME dict in two sibling slots (a DAG, not a cycle) is emitted
    in full at each position - the guarantee that keeps every JSON-representable input
    byte-identical to the pre-guard sanitizer."""
    shared = {"k": 1, "n": [2, 3]}
    result = _json_safe([shared, shared, {"nested": shared}])
    assert result == [
        {"k": 1, "n": [2, 3]},
        {"k": 1, "n": [2, 3]},
        {"nested": {"k": 1, "n": [2, 3]}},
    ]


# ---------------------------------------------------------------------------
# AS-5: determinism + fail-closed preserved.
# ---------------------------------------------------------------------------


def test_identical_inputs_render_byte_identically():
    value = {"z": [float("nan"), 1, {"q": object()}], "a": (True, -3, "s")}
    first = json.dumps(_json_safe(value), ensure_ascii=True)
    second = json.dumps(_json_safe(value), ensure_ascii=True)
    assert first == second


def test_no_object_address_leaks_through_any_marker():
    serialized = _assert_strict_json_safe(
        _json_safe({"obj": object(), "fn": len, "key_obj": {object(): 1}})
    )
    assert " at 0x" not in serialized


# ---------------------------------------------------------------------------
# AS-3: L1 deepcopy guard closed for BOTH consumers (typed outcome, no raise).
# ---------------------------------------------------------------------------


def _one_generator():
    yield 1


def test_ranking_l1_non_deepcopyable_value_yields_not_scorable_candidate():
    document = _preliminary_document()
    lock_set = [_factor("utilization_factor", threading.Lock())]
    # Was: copy.deepcopy(assumption_set) raised TypeError and crashed the ranking.
    result = rank_scenario_assumption_sets(document, OBJ, [lock_set])

    assert result["ranking_kind"] == RankingKind.RANKED
    assert result["candidate_count"] == 1
    assert result["scorable_count"] == 0
    candidate = result["candidates"][0]
    assert candidate["scorable"] is False
    assert candidate["score"] is None
    assert candidate["assumption_set"]["unsafe_kind"] == "undeepcopyable"
    _assert_strict_json_safe(result)


def test_ranking_l1_generator_value_does_not_raise():
    document = _preliminary_document()
    gen_set = [_factor("utilization_factor", _one_generator())]
    result = rank_scenario_assumption_sets(document, OBJ, [gen_set])
    assert result["candidates"][0]["scorable"] is False
    _assert_strict_json_safe(result)


def test_ranking_l1_good_and_bad_sets_together_bad_ranked_last():
    document = _preliminary_document()
    good = [_factor("utilization_factor", 0.8)]  # 12000
    bad = [_factor("utilization_factor", threading.Lock())]
    result = rank_scenario_assumption_sets(document, OBJ, [bad, good])
    assert result["candidate_count"] == 2
    assert result["scorable_count"] == 1
    # scorable candidate ranks first; the non-deepcopyable one is flagged not-scorable, ranked last.
    assert result["candidates"][0]["scorable"] is True
    assert result["candidates"][-1]["scorable"] is False
    _assert_strict_json_safe(result)


def test_sensitivity_l1_non_deepcopyable_value_yields_marker_point_no_raise():
    document = _preliminary_document()
    # Was: copy.deepcopy(tried) raised TypeError and crashed the analysis.
    result = analyze_scenario_sensitivity(document, VAR, [threading.Lock()])

    assert result["sensitivity_kind"] == SensitivityKind.ANALYZED
    assert result["point_count"] == 1
    point = result["points"][0]
    assert point["derivable"] is False
    # The echoed value is a typed, address-free marker, never the raw lock.
    assert isinstance(point["value"], dict)
    assert point["value"]["unsafe_value_removed"] is True
    _assert_strict_json_safe(result)


def test_sensitivity_l1_generator_value_does_not_raise():
    document = _preliminary_document()
    result = analyze_scenario_sensitivity(document, VAR, [_one_generator()])
    assert result["point_count"] == 1
    assert result["points"][0]["derivable"] is False
    _assert_strict_json_safe(result)
