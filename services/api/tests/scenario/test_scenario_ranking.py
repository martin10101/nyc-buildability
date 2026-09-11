"""Executable acceptance pack AS-1..AS-7 for the deterministic scenario ranking
(task M5-T007).

Offline and deterministic. Each test maps to an acceptance scenario and asserts the
explicit-only, named-objective, transparent-breakdown, total-stable-ordering, fail-closed,
read-only, and never-Verified guarantees the packet requires. Candidates are exercised
against real scenario documents produced by ``build_scenario`` (the shape the Compare UI
consumes), plus targeted malformed inputs that prove ranking's fail-closed guards.
"""

from __future__ import annotations

import copy
import json
import math

import pytest

from app.scenario import (
    NOT_VERIFIED_DISCLAIMER,
    RANKING_LABEL,
    RankingKind,
    RankingObjective,
    build_scenario,
    derive_practical_usable_range,
    rank_scenario_assumption_sets,
)

from . import _support as S

OBJ = RankingObjective.MAXIMIZE_ILLUSTRATIVE_USABLE_AREA


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
# AS-1 deterministic, TOTAL, stable ordering (independent of input order).
# ---------------------------------------------------------------------------


def test_as1_ordering_is_score_descending_with_stable_ranks():
    document = _preliminary_document()
    sets = [
        [_factor("utilization_factor", 0.5)],  # 7500
        [_factor("utilization_factor", 0.8)],  # 12000
        [],  # raw cap 15000
        [_factor("efficiency_ratio", 0.9)],  # 13500
    ]
    result = rank_scenario_assumption_sets(document, OBJ, sets)

    assert result["ranking_kind"] == RankingKind.RANKED
    assert [c["rank"] for c in result["candidates"]] == [1, 2, 3, 4]
    scores = [c["score"] for c in result["candidates"]]
    assert scores == [15000.0, 13500.0, 12000.0, 7500.0]
    # Score is monotonically non-increasing down the ranked list.
    assert scores == sorted(scores, reverse=True)


def test_as1_byte_identical_across_input_reorderings_and_ties():
    """Reordering the caller's assumption-sets (including a genuine score tie) must not
    change the output: a TOTAL content-based tie-break makes the ordered output a pure
    function of the SET of assumption-sets, never of their supplied position."""
    document = _preliminary_document()
    base = [
        [_factor("utilization_factor", 0.5)],  # 7500  (ties with efficiency 0.5)
        [_factor("efficiency_ratio", 0.5)],  # 7500  (tie)
        [],  # 15000
        [_factor("utilization_factor", 0.8)],  # 12000
    ]
    forward = rank_scenario_assumption_sets(document, OBJ, copy.deepcopy(base))
    reversed_ = rank_scenario_assumption_sets(
        document, OBJ, list(reversed(copy.deepcopy(base)))
    )
    shuffled = rank_scenario_assumption_sets(
        document, OBJ, [copy.deepcopy(base[i]) for i in (2, 0, 3, 1)]
    )

    assert json.dumps(forward) == json.dumps(reversed_) == json.dumps(shuffled)
    # The equal-score pair is ordered deterministically and never interleaves the others.
    tied = [c["score"] for c in forward["candidates"]]
    assert tied == [15000.0, 12000.0, 7500.0, 7500.0]


def test_as1_identical_input_is_byte_identical():
    document = _preliminary_document()
    sets = [[_factor("utilization_factor", 0.8)], [_factor("efficiency_ratio", 0.6)]]
    first = rank_scenario_assumption_sets(_preliminary_document(), OBJ, copy.deepcopy(sets))
    second = rank_scenario_assumption_sets(document, OBJ, copy.deepcopy(sets))
    assert json.dumps(first) == json.dumps(second)


def test_as1_equal_score_reordered_key_dicts_are_input_order_independent():
    """Regression: two assumption dicts with IDENTICAL entries in DIFFERENT insertion orders
    score equal (a genuine tie). The tie-break must order them by the EXACT (unsorted)
    serialization each contributes to the output - not a key-sorted canonical form - so
    reversing the candidate list yields BYTE-IDENTICAL output. A key-sorted tie-break
    collapsed both to one key; the stable sort then leaked the caller's input position and
    reversing the input flipped the two echoes in the output."""
    document = _preliminary_document()
    a = {
        "key": "utilization_factor",
        "assumption_type": "utilization_factor",
        "value": 0.5,
        "unit": "ratio",
        "rationale": "explicit",
    }
    b = {  # SAME entries as ``a``, reversed insertion order -> a different emitted echo
        "rationale": "explicit",
        "unit": "ratio",
        "value": 0.5,
        "assumption_type": "utilization_factor",
        "key": "utilization_factor",
    }
    forward = rank_scenario_assumption_sets(document, OBJ, [[a], [b]])
    reversed_ = rank_scenario_assumption_sets(
        document, OBJ, list(reversed([[a], [b]]))
    )

    # Unsorted json.dumps preserves each echoed dict's key order; reversing the candidates
    # must not change a single byte of the ordered output.
    assert json.dumps(forward) == json.dumps(reversed_)
    # Both candidates are the same 7500 score - a real tie broken by emitted content, not
    # by the transient input position.
    assert [c["score"] for c in forward["candidates"]] == [7500.0, 7500.0]


# ---------------------------------------------------------------------------
# AS-2 transparent NAMED-objective score breakdown; no hidden weight.
# ---------------------------------------------------------------------------


def test_as2_named_objective_and_transparent_components():
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    sets = [[_factor("utilization_factor", 0.8)], [_factor("efficiency_ratio", 0.5)], []]
    result = rank_scenario_assumption_sets(document, OBJ, sets)

    # The objective is NAMED on the ranking AND on every candidate (no unnamed "best").
    assert result["objective"] == OBJ.value == "maximize_illustrative_usable_area"
    assert result["objective_label"]
    for candidate in result["candidates"]:
        assert candidate["objective"] == OBJ.value
        components = candidate["score_components"]
        assert components["objective"] == OBJ.value
        # Score is a DOCUMENTED function of already-surfaced numbers only: no hidden weight.
        assert candidate["score"] == components["illustrative_usable_area_sq_ft"]
        assert candidate["score"] == cap * components["factor_product"]
        assert components["canonical_cap_sq_ft"] == cap
        assert "formula" in components

    # rank 1 is the largest usable area (the least-reducing assumption-set: the raw cap).
    assert result["candidates"][0]["score"] == cap == 15000.0


def test_as2_top_candidate_never_travels_without_its_objective():
    document = _preliminary_document()
    result = rank_scenario_assumption_sets(
        document, OBJ, [[_factor("utilization_factor", 0.7)]]
    )
    best = result["candidates"][0]
    assert best["objective"] == OBJ.value
    assert best["objective_label"]
    assert best["score_components"]["objective"] == OBJ.value


# ---------------------------------------------------------------------------
# AS-3 explicit-assumption-only; never fabricates; empty -> raw scenario; not-derivable last.
# ---------------------------------------------------------------------------


def test_as3_ranks_only_supplied_sets_never_fabricates():
    document = _preliminary_document()
    sets = [
        [_factor("utilization_factor", 0.9)],
        [_factor("efficiency_ratio", 0.4)],
        [_factor("utilization_factor", 0.6)],
    ]
    result = rank_scenario_assumption_sets(document, OBJ, sets)
    # Exactly one candidate per supplied set - no invented scenario/assumption/alternative.
    assert result["candidate_count"] == len(sets) == 3
    assert len(result["candidates"]) == 3


@pytest.mark.parametrize("empty", [[], None])
def test_as3_empty_sets_ranks_the_raw_scenario_not_a_fabrication(empty):
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    result = rank_scenario_assumption_sets(document, OBJ, empty)

    assert result["ranking_kind"] == RankingKind.RANKED
    assert result["candidate_count"] == 1
    only = result["candidates"][0]
    # The single candidate is the RAW scenario (no factor applied), never an alternative.
    assert only["scorable"] is True
    assert only["score"] == cap == 15000.0
    assert only["score_components"]["factor_product"] == 1.0
    assert only["assumption_set"] == []


def test_as3_not_derivable_candidate_is_ranked_last_and_flagged():
    document = _preliminary_document()
    sets = [
        [_factor("utilization_factor", 0.8)],  # scorable (12000)
        [_factor("utilization_factor", 1.5)],  # out-of-domain -> derive fails closed
    ]
    result = rank_scenario_assumption_sets(document, OBJ, sets)

    assert result["candidate_count"] == 2
    assert result["scorable_count"] == 1
    scorable, flagged = result["candidates"]
    assert scorable["scorable"] is True and scorable["rank"] == 1
    # The un-derivable set is ranked LAST, carries NO fabricated score, and names a reason.
    assert flagged["scorable"] is False and flagged["rank"] == 2
    assert flagged["score"] is None
    assert flagged["score_components"] is None
    assert flagged["not_scorable_reason"]


# ---------------------------------------------------------------------------
# AS-4 fail-closed on bad input: typed outcome, no crash, strict-JSON-safe.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_objective",
    ["maximize_unicorns", "", None, float("nan"), 3.14, {"k": "v"}, ["x"]],
)
def test_as4_unknown_or_malformed_objective_is_invalid(bad_objective):
    document = _preliminary_document()
    result = rank_scenario_assumption_sets(
        document, bad_objective, [[_factor("utilization_factor", 0.8)]]
    )
    assert result["ranking_kind"] == RankingKind.INVALID
    assert result["ranked"] is False
    assert result["candidates"] == []
    assert result["invalid_reason"]
    # A non-string objective is never echoed (keeps the output strict-JSON-safe).
    if not isinstance(bad_objective, str):
        assert result["objective"] is None
    _strict_json_safe(result)


@pytest.mark.parametrize(
    "rule_evaluation_factory",
    [S.unsupported_rule_evaluation, S.conflict_rule_evaluation, S.missing_lot_area_rule_evaluation],
)
def test_as4_no_cap_document_is_typed_empty_with_reason(rule_evaluation_factory):
    document = build_scenario(S.profile(), rule_evaluation_factory())
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None

    result = rank_scenario_assumption_sets(document, OBJ, [[_factor("utilization_factor", 0.8)]])
    assert result["ranking_kind"] == RankingKind.EMPTY
    assert result["ranked"] is False
    assert result["candidates"] == []
    assert result["empty_reason"]
    # No fabricated candidate/score anywhere.
    assert 15000.0 not in _all_numbers(result)
    _strict_json_safe(result)


@pytest.mark.parametrize("bad_container", [{"a": 1}, "notalist", 42, 3.0])
def test_as4_malformed_assumption_sets_container_is_invalid(bad_container):
    document = _preliminary_document()
    result = rank_scenario_assumption_sets(document, OBJ, bad_container)
    assert result["ranking_kind"] == RankingKind.INVALID
    assert result["candidates"] == []
    assert result["invalid_reason"]
    _strict_json_safe(result)


@pytest.mark.parametrize(
    "bad_set", ["notalist", 7, {"not": "a list"}, [42], [{"malformed": True}, "x"]]
)
def test_as4_malformed_individual_set_is_flagged_not_scorable_no_crash(bad_set):
    """A malformed assumption-set among the list fails closed at the candidate level (derive's
    own guard), never crashes and never gets a fabricated score."""
    document = _preliminary_document()
    result = rank_scenario_assumption_sets(
        document, OBJ, [bad_set, [_factor("utilization_factor", 0.8)]]
    )
    assert result["ranking_kind"] == RankingKind.RANKED
    assert result["candidate_count"] == 2
    flagged = result["candidates"][-1]
    assert flagged["scorable"] is False
    assert flagged["score"] is None
    _strict_json_safe(result)


def test_as4_degenerate_document_is_typed_no_crash():
    for degenerate in ({}, None, "notadoc", 5):
        result = rank_scenario_assumption_sets(
            degenerate, OBJ, [[_factor("utilization_factor", 0.8)]]
        )
        # No positive cap -> typed EMPTY; never a crash, always strict-JSON-safe.
        assert result["ranking_kind"] == RankingKind.EMPTY
        _strict_json_safe(result)


def test_as4_mixed_key_dict_entry_does_not_crash_the_tie_break():
    """A pathological assumption entry whose dict has non-comparable (mixed-type) keys must not
    crash the deterministic content-based tie-break; it fails closed to a stable repr key."""
    document = _preliminary_document()
    sets = [[{1: "x", "y": 2}], [_factor("utilization_factor", 0.8)]]
    result = rank_scenario_assumption_sets(document, OBJ, sets)
    assert result["ranking_kind"] == RankingKind.RANKED
    assert result["candidate_count"] == 2
    _strict_json_safe(result)
    # Deterministic even with the pathological key.
    again = rank_scenario_assumption_sets(_preliminary_document(), OBJ, copy.deepcopy(sets))
    assert json.dumps(result) == json.dumps(again)


@pytest.mark.parametrize(
    "bad_value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        -0.5,
        -1,
        10**400,
        # Explicit ids: pytest's own id generation does str(val), which would itself trip
        # CPython's int->str ceiling for these, so they must not be bare parametrize values.
        pytest.param(10**5000, id="pow10_5000"),
        pytest.param(-(10**5000), id="neg_pow10_5000"),
    ],
)
def test_as4_malformed_assumption_value_is_typed_and_json_safe(bad_value):
    """A malformed VALUE on an (unrecognized) explicit assumption is surfaced through derive's
    unapplied list AND echoed by ranking. The ranking output must stay strict-JSON-safe - the
    raw NaN/+-Inf/negative/float-overflowing value is replaced by a TYPED marker, never echoed
    raw - and stay deterministic run-to-run. (An unrecognized type keeps the candidate
    scorable via the raw-cap path, so the malformed value rides through BOTH the echoed
    assumption-set and the transported ``derived.unapplied_assumptions``.)"""
    document = _preliminary_document()
    tainted = {
        "key": "note",
        "assumption_type": "note",  # unrecognized -> surfaced but NOT applied
        "value": bad_value,
        "unit": "ratio",
        "rationale": "explicit but malformed value",
    }
    sets = [[tainted], [_factor("utilization_factor", 0.8)]]
    result = rank_scenario_assumption_sets(document, OBJ, sets)

    assert result["ranking_kind"] == RankingKind.RANKED
    assert result["candidate_count"] == 2
    # Strict-JSON-safe: no NaN/Inf/negative/overflowing number survives anywhere.
    _strict_json_safe(result)
    # The raw unsafe value is NOWHERE in the output; a typed marker stands in for it.
    assert "unsafe_value_removed" in json.dumps(result)
    # Deterministic even with the malformed value.
    again = rank_scenario_assumption_sets(_preliminary_document(), OBJ, copy.deepcopy(sets))
    assert json.dumps(result) == json.dumps(again)


def test_as4_unsupported_object_assumption_value_is_typed_and_json_safe():
    """A non-JSON-serializable object as an explicit assumption value must not make the output
    un-serializable: it is replaced by a typed marker that surfaces only its deterministic
    type name (never an address-bearing repr), so json.dumps never raises."""
    document = _preliminary_document()

    class _Weird:
        pass

    tainted = {
        "key": "note",
        "assumption_type": "note",
        "value": _Weird(),
        "unit": "ratio",
        "rationale": "explicit but unserializable value",
    }
    result = rank_scenario_assumption_sets(document, OBJ, [[tainted]])

    assert result["ranking_kind"] == RankingKind.RANKED
    _strict_json_safe(result)  # would raise on a raw object without sanitization
    serialized = json.dumps(result)
    assert "unsafe_value_removed" in serialized
    # The marker surfaces the type name for provenance, not a raw address-bearing repr.
    assert "_Weird" in serialized


def test_as4_overflow_huge_int_assumption_value_is_guarded_and_deterministic():
    """Regression: an unrecognized explicit assumption whose VALUE is 10**5000 (a 16610-bit
    integer whose full decimal expansion, at ~5001 digits, exceeds CPython's int->str
    conversion ceiling and would raise ``ValueError``). The overflow marker must NOT
    decimal-expand it: it is described by magnitude (bit length), so the output stays a typed
    RANKED outcome, strict-JSON-safe, byte-bounded, and byte-identical run-to-run - never an
    unguarded decimal ``repr`` that crashes the sanitizer."""
    document = _preliminary_document()
    huge = 10**5000  # decimal repr would exceed the int->str ceiling and raise ValueError
    tainted = {
        "key": "note",
        "assumption_type": "note",  # unrecognized -> surfaced but NOT applied, candidate scorable
        "value": huge,
        "unit": "ratio",
        "rationale": "explicit but astronomically large value",
    }
    sets = [[tainted], [_factor("utilization_factor", 0.8)]]
    result = rank_scenario_assumption_sets(document, OBJ, sets)

    # Typed outcome, no crash: the huge int rides through both the echo and derived breakdown.
    assert result["ranking_kind"] == RankingKind.RANKED
    assert result["candidate_count"] == 2
    # Strict-JSON-safe: no NaN/Inf/negative/overflowing number survives anywhere.
    _strict_json_safe(result)
    serialized = json.dumps(result)
    # A typed marker stands in for the raw value; it is DESCRIBED by magnitude, not expanded.
    assert "unsafe_value_removed" in serialized
    assert "bit_length" in serialized
    # The full 5001-digit decimal expansion never appears (that would be unbounded + would have
    # required the very ValueError-raising conversion the guard avoids).
    assert "0" * 100 not in serialized
    # Repeated call is byte-identical (deterministic even with the pathological value).
    again = rank_scenario_assumption_sets(_preliminary_document(), OBJ, copy.deepcopy(sets))
    assert serialized == json.dumps(again)


def test_as4_object_dict_key_assumption_value_is_typed_and_deterministic():
    """Regression: an unrecognized explicit assumption whose VALUE is a dict keyed by an
    ORDINARY OBJECT (not a JSON-safe key). The key must NOT be rendered through its
    address-bearing ``repr`` (``<... at 0x...>``): that is non-JSON-safe context AND embeds a
    transient object id, breaking byte-identical determinism. The sanitizer must replace it
    with a deterministic typed token, keeping the output RANKED, strict-JSON-safe, and
    byte-identical run-to-run."""
    document = _preliminary_document()

    class _ObjKey:
        pass

    def _sets():
        tainted = {
            "key": "note",
            "assumption_type": "note",  # unrecognized -> surfaced but NOT applied
            "value": {_ObjKey(): "nested"},  # an ordinary object as a dict KEY
            "unit": "ratio",
            "rationale": "explicit but unserializable dict key",
        }
        return [[tainted], [_factor("utilization_factor", 0.8)]]

    result = rank_scenario_assumption_sets(document, OBJ, _sets())

    # Typed outcome, no crash; would raise on a raw object key without sanitization.
    assert result["ranking_kind"] == RankingKind.RANKED
    assert result["candidate_count"] == 2
    _strict_json_safe(result)
    serialized = json.dumps(result)
    # The object key is replaced by a deterministic typed token that names the type only ...
    assert "__unsafe_key__" in serialized
    assert "_ObjKey" in serialized
    # ... and NEVER an address-bearing repr (which would be non-deterministic run-to-run).
    assert " at 0x" not in serialized
    # A FRESH object each call still yields byte-identical output (type-only, no id leaked).
    again = rank_scenario_assumption_sets(_preliminary_document(), OBJ, _sets())
    assert serialized == json.dumps(again)


# ---------------------------------------------------------------------------
# AS-5 never up-labels / never Verified; needs_review + disclaimer preserved.
# ---------------------------------------------------------------------------


def test_as5_ranking_is_never_verified_and_honestly_labelled():
    document = _preliminary_document()
    result = rank_scenario_assumption_sets(
        document, OBJ, [[_factor("utilization_factor", 0.8)], []]
    )
    # No coverage_status anywhere is 'verified'; no field VALUE equals 'verified'.
    assert "verified" not in _coverage_values(result)
    assert "verified" not in _all_strings(result)
    assert result["coverage_status"] == "conditional"
    # needs_review + not_verified_disclaimer lineage preserved end-to-end.
    assert result["needs_review"] is True
    assert result["not_verified_disclaimer"] == document["not_verified_disclaimer"]
    assert result["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER
    # Honest, illustrative label (never a Verified/feasible ranking).
    assert result["label"] == RANKING_LABEL
    assert "ILLUSTRATIVE" in RANKING_LABEL
    assert "NOT Verified" in RANKING_LABEL


def test_as5_incoming_verified_coverage_is_capped_to_conditional():
    """A scenario must never carry 'verified'; if one somehow does, the ranking caps it."""
    document = _preliminary_document()
    tampered = copy.deepcopy(document)
    tampered["coverage_status"] = "verified"
    result = rank_scenario_assumption_sets(tampered, OBJ, [])
    assert result["coverage_status"] == "conditional"
    assert "verified" not in _coverage_values(result)


def test_as5_literal_verified_objective_is_invalid_and_never_emitted():
    """A caller passing the LITERAL objective 'verified' must fail closed AND never inject the
    never-Verified token into the output: the invalid-objective echo is sanitized to None, so
    the 'verified' token appears in no field anywhere (objective, coverage, or any string)."""
    document = _preliminary_document()
    result = rank_scenario_assumption_sets(
        document, "verified", [[_factor("utilization_factor", 0.8)]]
    )
    assert result["ranking_kind"] == RankingKind.INVALID
    assert result["ranked"] is False
    assert result["candidates"] == []
    assert result["invalid_reason"]
    # The 'verified' token is never echoed - not as the objective, not anywhere.
    assert result["objective"] is None
    assert "verified" not in _all_strings(result)
    assert "verified" not in _coverage_values(result)
    _strict_json_safe(result)


# ---------------------------------------------------------------------------
# AS-6 read-only consumption; no legal recompute; no aliasing.
# ---------------------------------------------------------------------------


def test_as6_inputs_are_byte_unchanged_and_not_aliased():
    document = _preliminary_document()
    sets = [[_factor("utilization_factor", 0.8)], [_factor("efficiency_ratio", 0.5)]]
    document_before = json.dumps(document)
    sets_before = json.dumps(sets)

    result = rank_scenario_assumption_sets(document, OBJ, sets)

    # Inputs are byte-unchanged after ranking (consumed strictly READ-ONLY).
    assert json.dumps(document) == document_before
    assert json.dumps(sets) == sets_before
    # Each echoed assumption-set is a DEEP COPY: equal in content, never the same object.
    echoes = [candidate["assumption_set"] for candidate in result["candidates"]]
    for original in sets:
        assert all(echo is not original for echo in echoes)
    # Mutating the result never reaches back into the caller's input.
    result["candidates"][0]["assumption_set"].append({"injected": True})
    assert json.dumps(sets) == sets_before


def test_as6_score_uses_only_surfaced_numbers_no_recompute():
    document = _preliminary_document()
    cap = document["draft_zoning_floor_area_cap_sq_ft"]
    assumption_set = [_factor("utilization_factor", 0.8)]
    result = rank_scenario_assumption_sets(document, OBJ, [assumption_set])
    candidate = result["candidates"][0]

    # The candidate's transparent breakdown is exactly the accepted derive() output for the
    # same explicit assumption-set: ranking CONSUMES derive.py, never recomputes a legal value.
    expected_derived = derive_practical_usable_range(
        {**document, "assumptions": assumption_set}
    )
    assert candidate["derived"] == expected_derived
    # The canonical cap in the breakdown is the document's cap transported verbatim.
    assert candidate["score_components"]["canonical_cap_sq_ft"] == cap
    assert candidate["score"] == cap * 0.8 == 12000.0


# ---------------------------------------------------------------------------
# AS-7 contract-free + offline + strict-JSON-safe on every path.
# ---------------------------------------------------------------------------


def test_as7_ranked_output_is_strict_json_safe():
    document = _preliminary_document()
    sets = [
        [_factor("utilization_factor", 0.8), _factor("efficiency_ratio", 0.5)],
        [_factor("utilization_factor", 1.5)],  # fails closed -> flagged, no fabricated score
        [],
    ]
    result = rank_scenario_assumption_sets(document, OBJ, sets)
    _strict_json_safe(result)


def test_as7_ranking_consumes_derive_breakdown_for_every_candidate():
    document = _preliminary_document()
    sets = [[_factor("utilization_factor", 0.8)], [], [_factor("efficiency_ratio", 0.5)]]
    result = rank_scenario_assumption_sets(document, OBJ, sets)
    for candidate in result["candidates"]:
        expected = derive_practical_usable_range(
            {**document, "assumptions": candidate["assumption_set"]}
        )
        assert candidate["derived"] == expected
        assert candidate["derived_kind"] == expected["derived_kind"]
