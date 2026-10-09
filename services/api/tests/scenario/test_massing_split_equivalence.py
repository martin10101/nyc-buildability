"""M5-T112 (DB-079 a, b): golden equivalence across the massing_model split.

These digests were captured from the facade at the M5-T112 claim seam (275ef85f), BEFORE
the guards / triangulation / mesh split, over a fixed corpus: the existing test inputs plus
concave (L / U / comb / multi-level), a generated option, and the refusal cases (footprint
outside lot, too-few-vertex lot, NaN, over-cap vertices, non-positive height, out-of-NYC
lot, keyhole self-intersection, near-overflow lot, footprint and level-outline big-int
overflow, no-candidate). Successes are pinned by ``content_hash`` (sha256 over the canonical
as_dict JSON); refusals by ``(reason, field, message)``.

The split moved code without changing behaviour: every one of these matches after the split
EXCEPT the single intended DB-079 (b) change - the level-outline big-int overflow now names
``proposed_massing.levels[0].outline`` instead of the blanket ``proposed_massing.outline``
(the footprint-overflow case still names ``proposed_massing.outline``). See
``test_db079b_level_outline_overflow_names_the_level_field`` for the before -> after.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from app.scenario.massing_model import (
    MassingModelError,
    build_from_generated_option,
    build_massing_model,
)

# ---------------------------------------------------------------------------
# Corpus fixtures (EPSG:2263 US survey feet, inside the NYC bounds).
# ---------------------------------------------------------------------------

LOT_RING = [[1000000.0, 200000.0], [1000100.0, 200000.0],
            [1000100.0, 200120.0], [1000000.0, 200120.0]]
RECT = [[1000010.0, 200010.0], [1000050.0, 200010.0],
        [1000050.0, 200070.0], [1000010.0, 200070.0]]
LSHAPE = [[1000010.0, 200010.0], [1000070.0, 200010.0], [1000070.0, 200040.0],
          [1000040.0, 200040.0], [1000040.0, 200080.0], [1000010.0, 200080.0]]
USHAPE = [[1000010.0, 200010.0], [1000090.0, 200010.0], [1000090.0, 200100.0],
          [1000070.0, 200100.0], [1000070.0, 200040.0], [1000030.0, 200040.0],
          [1000030.0, 200100.0], [1000010.0, 200100.0]]
COMB = [[1000010.0, 200010.0], [1000090.0, 200010.0], [1000090.0, 200100.0],
        [1000075.0, 200100.0], [1000075.0, 200030.0], [1000058.0, 200030.0],
        [1000058.0, 200100.0], [1000042.0, 200100.0], [1000042.0, 200030.0],
        [1000025.0, 200030.0], [1000025.0, 200100.0], [1000010.0, 200100.0]]
FIVE = [12.0, 11.0, 13.0, 10.0, 14.0]


def _walls(n):
    return [{"id": f"W{i}", "start_vertex_index": i, "end_vertex_index": (i + 1) % n}
            for i in range(n)]


def _outline(v):
    return {"srid": 2263, "vertices": v + [v[0]]}


def _prov():
    return {"author": "test-architect", "editor_version": "test-1", "kind": "proposed"}


def _block(v, levels=None):
    return {
        "outline": _outline(v),
        "levels": levels if levels is not None else [
            {"level_index": 0, "floor_count": 1, "floor_to_floor_ft": 12.0}],
        "exterior_walls": _walls(len(v)),
        "provenance": _prov(),
    }


def _five_block():
    return {
        "outline": _outline(RECT),
        "levels": [{"level_index": i, "floor_count": 1, "floor_to_floor_ft": h}
                   for i, h in enumerate(FIVE)],
        "exterior_walls": _walls(4),
        "provenance": _prov(),
    }


def _digest_dict(d) -> str:
    canon = json.dumps(d, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _multi_level_block():
    return _block(RECT, levels=[
        {"level_index": i, "floor_count": 2, "floor_to_floor_ft": 10.0,
         "outline": _outline(LSHAPE)} for i in range(3)])


def _generated_option():
    candidate = {**_block(RECT), "provenance": {
        "author": "max-envelope-generator", "editor_version": "m5-t064-slice1",
        "kind": "proposed"}}
    return build_from_generated_option(
        lot_ring=LOT_RING,
        max_envelope={"candidate": candidate, "candidate_placement": {"status": "fitted"}})


# Golden content-hashes captured at the claim seam (byte-identical after the split).
GOLD_SUCCESS = {
    "rect": ("sha256:b7fa9862a0bb23885e7d7d71dae4a2d448a6ca4720f29a7b6bf68b4227c5133b",
             lambda: build_massing_model(lot_ring=LOT_RING, proposed_massing=_block(RECT))),
    "lshape": ("sha256:f9c731b974135e5c0641eda7bc2d8aa1bae3ae8d9e84d7b40bf7c8f7e781a963",
               lambda: build_massing_model(lot_ring=LOT_RING, proposed_massing=_block(LSHAPE))),
    "ushape": ("sha256:ff30bf8d2838286d79914518790ddcd7d7471732272bb690adacd723bead7582",
               lambda: build_massing_model(lot_ring=LOT_RING, proposed_massing=_block(USHAPE))),
    "comb": ("sha256:f5c661e6cca349fbb1e1105f6df842c7349d23ef34ab3a216d42444e7b343d60",
             lambda: build_massing_model(lot_ring=LOT_RING, proposed_massing=_block(COMB))),
    "five_floor": ("sha256:e23b5cbcca6ea7defee4b04c6bac51a94d4c26b5e643e2af923d29d1c248a6c5",
                   lambda: build_massing_model(lot_ring=LOT_RING, proposed_massing=_five_block())),
    "multi_level_shared_outline": (
        "sha256:6185b4e892b35a1a4d91be3fde4a5642a87dc2aa622d48d2246a6fe60ab6ea59",
        lambda: build_massing_model(lot_ring=LOT_RING, proposed_massing=_multi_level_block())),
    "generated_option": (
        "sha256:67ae9323a4a6d4eb6c7497294ac310b62082a451b0cbab56e3a4b431ae64efad",
        _generated_option),
}


@pytest.mark.parametrize("name", sorted(GOLD_SUCCESS))
def test_success_content_hash_byte_identical_after_split(name):
    golden, build = GOLD_SUCCESS[name]
    assert build().content_hash() == golden


# --- refusal corpus: (reason, field, message) pinned at the claim seam ------

_OVERFLOW_MSG = ("proposed_massing carries a coordinate beyond the finite float range "
                 "(a non-finite magnitude); it is refused, never truncated")
_LVL_OVER = _block(RECT, levels=[
    {"level_index": 0, "floor_count": 1, "floor_to_floor_ft": 12.0,
     "outline": _outline([[10 ** 400, 200010.0], [1000050.0, 200010.0],
                          [1000050.0, 200070.0], [1000010.0, 200070.0]])}])
_FOOT_OVER = {**_block(RECT), "outline": _outline(
    [[10 ** 400, 200010.0], [1000050.0, 200010.0],
     [1000050.0, 200070.0], [1000010.0, 200070.0]])}

GOLD_REFUSAL = {
    "footprint_outside_lot": (
        ("footprint_outside_lot", "proposed_massing.levels[0].outline",
         "level 0 footprint lies outside the lot beyond 1e-06 ft; it is refused, never clipped"),
        lambda: build_massing_model(lot_ring=LOT_RING, proposed_massing={
            **_block(RECT), "outline": _outline([[x + 200.0, y] for x, y in RECT])})),
    "lot_too_few_vertices": (
        ("invalid_source", "lot_ring", "lot_ring needs at least 3 distinct vertices; got 1"),
        lambda: build_massing_model(lot_ring=[[1000000.0, 200000.0]],
                                    proposed_massing=_block(RECT))),
    "non_finite_nan_lot": (
        ("non_finite", "lot_ring[1]",
         "lot_ring[1] must be a finite [x, y] pair; got [nan, 200000.0]"),
        lambda: build_massing_model(
            lot_ring=[[1000000.0, 200000.0], [float("nan"), 200000.0], [1000100.0, 200120.0]],
            proposed_massing=_block(RECT))),
    "over_cap_vertices": (
        ("over_cap_vertices", "lot_ring", "lot_ring has 1005 vertices, over the cap 1000"),
        lambda: build_massing_model(
            lot_ring=[[1000000.0 + i * 1e-3, 200000.0] for i in range(1005)],
            proposed_massing=_block(RECT))),
    "non_positive_height": (
        ("invalid_source", "proposed_massing.levels[0].floor_to_floor_ft",
         "proposed_massing failed B0 contract validation: ProposedMassingError("
         "'proposed_massing.levels[0].floor_to_floor_ft must be strictly positive; got 0.0')"),
        lambda: build_massing_model(lot_ring=LOT_RING, proposed_massing={
            **_block(RECT),
            "levels": [{"level_index": 0, "floor_count": 1, "floor_to_floor_ft": 0.0}]})),
    "lot_out_of_nyc_bounds_4326": (
        ("lot_ring_out_of_nyc_bounds", "lot_ring",
         "lot_ring vertex (-73.99, 40.7) is outside plausible NYC EPSG:2263 bounds "
         "([900000.0, 1100000.0] x [100000.0, 300000.0] US survey feet) - likely a "
         "wrong-unit or wrong-CRS lot; it is refused, never mislabelled"),
        lambda: build_massing_model(
            lot_ring=[[-73.99, 40.70], [-73.98, 40.70], [-73.98, 40.71], [-73.99, 40.71]],
            proposed_massing=_block(RECT))),
    "keyhole_self_intersection": (
        ("self_intersection", "lot_ring",
         "lot_ring has a duplicate vertex other than the closing vertex"),
        lambda: build_massing_model(
            lot_ring=[[1000000.0 + x, 200000.0 + y] for x, y in [
                (0, 0), (100, 0), (100, 120), (0, 120), (0, 60),
                (40, 60), (40, 80), (60, 80), (60, 40), (40, 40), (40, 60), (0, 60)]],
            proposed_massing=_block(RECT))),
    "near_overflow_lot_1e154": (
        ("coordinate_out_of_range", "lot_ring[0]",
         "lot_ring[0] exceeds the coordinate magnitude bound 100000000 ft"),
        lambda: build_massing_model(
            lot_ring=[[-1e154, -1e154], [1e154, -1e154], [1e154, 1e154], [-1e154, 1e154]],
            proposed_massing=_block(RECT))),
    "no_generated_candidate": (
        ("no_generated_candidate", "max_envelope.candidate",
         "max_envelope emitted no candidate footprint (an explicit typed placement gap); "
         "no generated option can be built. 'the rules-derived footprint exceeds the lot'"),
        lambda: build_from_generated_option(lot_ring=LOT_RING, max_envelope={
            "candidate": None,
            "candidate_placement": {"status": "footprint_exceeds_lot",
                                    "detail": "the rules-derived footprint exceeds the lot"}})),
    # footprint big-int overflow: UNCHANGED label (proposed_massing.outline).
    "footprint_overflow_bigint": (
        ("non_finite", "proposed_massing.outline", _OVERFLOW_MSG),
        lambda: build_massing_model(lot_ring=LOT_RING, proposed_massing=_FOOT_OVER)),
    # level-outline big-int overflow: the ONE intended change (DB-079 b) - now the level field.
    "level_outline_overflow_bigint": (
        ("non_finite", "proposed_massing.levels[0].outline", _OVERFLOW_MSG),
        lambda: build_massing_model(lot_ring=LOT_RING, proposed_massing=_LVL_OVER)),
}


@pytest.mark.parametrize("name", sorted(GOLD_REFUSAL))
def test_refusal_reason_field_message_pinned(name):
    (reason, field, message), call = GOLD_REFUSAL[name]
    with pytest.raises(MassingModelError) as exc:
        call()
    assert exc.value.reason == reason
    assert exc.value.field == field
    assert str(exc.value) == message


def test_db079b_level_outline_overflow_names_the_level_field():
    """DB-079 (b): the B0 OverflowError arm names the REAL outline. A big-int coordinate in
    a LEVEL outline (footprint valid) now fails closed as non_finite naming
    proposed_massing.levels[0].outline. Under the OLD blanket label the arm hardcoded
    'proposed_massing.outline', so this assertion reddens that pre-fix behaviour."""
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=LOT_RING, proposed_massing=_LVL_OVER)
    assert exc.value.reason == "non_finite"
    assert exc.value.field == "proposed_massing.levels[0].outline"
    # The footprint-overflow case is unchanged, so the fix is specific, not a blanket rename.
    with pytest.raises(MassingModelError) as exc_foot:
        build_massing_model(lot_ring=LOT_RING, proposed_massing=_FOOT_OVER)
    assert exc_foot.value.field == "proposed_massing.outline"
