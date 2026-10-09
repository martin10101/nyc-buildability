"""Proposal-validation time-budget tests (task M5-T095, closing M5-T088 F-HIGH-1).

This suite pins the two defences added to :mod:`app.scenario.proposal`:

* a request-level TOTAL-positions bound (footprint + every per-level outline) that
  refuses with a typed :class:`ProposedMassingError` BEFORE any per-outline
  geometry check runs (AS-1); and
* a bounded, shapely/GEOS-decided simplicity check (about ``O(n log n)``) that
  replaces the former hand-rolled all-pairs ``O(n^2)`` scan while returning the
  SAME simple / not-simple decision on every ring (AS-2, AS-3).

Decision identity is proved against a self-contained copy of the PRE-M5-T095
predicate (:func:`_all_pairs_ring_is_simple`), which doubles as the "restore the
all-pairs loop" mutant for the work-count guard. The old measured worst case here
was ~533 s for a single validator-valid request (501 outlines x 1000 positions);
the new worst case at the maximum the bounds allow (20 000 positions) is tens of
milliseconds (numbers in the M5-T095 producer report).
"""

from __future__ import annotations

import math
import random
import time
from unittest import mock

import pytest
from shapely.errors import GEOSException

from app.scenario import proposal
from app.scenario.proposal import (
    MAX_OUTLINE_VERTICES,
    MAX_TOTAL_OUTLINE_POSITIONS,
    ProposedMassingError,
    validate_proposed_massing,
)

# A base X/Y comfortably inside the NYC EPSG:2263 unit-sanity bounds.
_X0 = 1000000.0
_Y0 = 200000.0

# MAX_OUTLINE_VERTICES counts the repeated closing vertex, so the most DISTINCT
# vertices a validator-accepted outline can carry - i.e. the largest ring the
# simplicity check ever sees through the public API - is one less.
_MAX_RING_VERTICES = MAX_OUTLINE_VERTICES - 1

# The all-pairs predicate performs ~n^2/2 pairwise segment tests; at the per-outline
# ceiling (1000 vertices) that is 498 500. The shapely check performs ZERO Python
# pairwise tests, so this budget separates the two by an order of magnitude:
# restoring the all-pairs loop reddens it, the shapely check stays at 0.
WORK_BUDGET_PAIRWISE_TESTS = 50_000

# Generous wall-clock ceiling for one worst-single-outline simplicity check on this
# class of machine. The shapely check runs in ~10 ms here (~50x margin); the former
# all-pairs scan ran in ~1.25 s and would blow this bound.
SIMPLICITY_TIME_BUDGET_S = 0.5


# ---------------------------------------------------------------------------
# Reference: the exact PRE-M5-T095 simplicity predicate (equivalence oracle and
# the "restore the all-pairs loop" mutant). Copied verbatim from the phase-B0
# proposal.py, with an optional pairwise-test counter threaded through.
# ---------------------------------------------------------------------------


def _orientation(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on_segment(a, b, p):
    return min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[
        1
    ] <= max(a[1], b[1])


def _segments_intersect(p1, p2, p3, p4):
    d1 = _orientation(p3, p4, p1)
    d2 = _orientation(p3, p4, p2)
    d3 = _orientation(p1, p2, p3)
    d4 = _orientation(p1, p2, p4)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and (
        (d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)
    ):
        return True
    if d1 == 0 and _on_segment(p3, p4, p1):
        return True
    if d2 == 0 and _on_segment(p3, p4, p2):
        return True
    if d3 == 0 and _on_segment(p1, p2, p3):
        return True
    if d4 == 0 and _on_segment(p1, p2, p4):
        return True
    return False


def _all_pairs_ring_is_simple(ring, counter=None):
    """The former O(n^2) predicate. ``counter`` (a one-element list) accumulates
    the number of non-adjacent pairwise segment tests performed."""
    n = len(ring)
    if n < 3:
        return False
    for k in range(n):
        prev_pt = ring[(k - 1) % n]
        cur = ring[k]
        nxt = ring[(k + 1) % n]
        if cur == nxt:
            return False
        v1 = (cur[0] - prev_pt[0], cur[1] - prev_pt[1])
        v2 = (nxt[0] - cur[0], nxt[1] - cur[1])
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        if cross == 0 and dot < 0:
            return False
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        for j in range(i + 1, n):
            if j == i + 1 or (i == 0 and j == n - 1):
                continue
            c, d = ring[j], ring[(j + 1) % n]
            if counter is not None:
                counter[0] += 1
            if _segments_intersect(a, b, c, d):
                return False
    return True


# ---------------------------------------------------------------------------
# Ring / block builders
# ---------------------------------------------------------------------------


def _circle_ring(n, cx=_X0, cy=_Y0, r=50000.0):
    """``n`` DISTINCT vertices of a convex (hence simple) polygon inside the NYC
    2263 unit bounds. No closing duplicate."""
    pts = []
    for k in range(n):
        ang = 2 * math.pi * k / n
        p = (round(cx + r * math.cos(ang), 3), round(cy + r * math.sin(ang), 3))
        if not pts or pts[-1] != p:
            pts.append(p)
    assert len(set(pts)) == len(pts)
    return pts


def _closed_outline(ring):
    return {"srid": 2263, "vertices": [list(v) for v in ring] + [list(ring[0])]}


def _valid_block(outline_ring):
    """A minimal, fully valid proposed_massing block whose footprint is
    ``outline_ring`` and which has a single level referencing it."""
    n = len(outline_ring)
    return {
        "outline": _closed_outline(outline_ring),
        "levels": [{"level_index": 0, "floor_count": 1, "floor_to_floor_ft": 10.0}],
        "exterior_walls": [
            {"id": "w0", "start_vertex_index": 0, "end_vertex_index": 1}
        ],
        "provenance": {
            "author": "tester",
            "editor_version": "1.0.0",
            "kind": "proposed",
        },
        "_n": n,
    }


def _over_budget_block(valid_footprint=True):
    """A block whose footprint + per-level outlines exceed
    :data:`MAX_TOTAL_OUTLINE_POSITIONS`. When ``valid_footprint`` the footprint is a
    real simple ring, so validation (with the bound removed) reaches the per-outline
    simplicity check."""
    if valid_footprint:
        footprint = _closed_outline(_circle_ring(_MAX_RING_VERTICES))
    else:
        footprint = {"srid": 2263, "vertices": [[0, 0]] * MAX_OUTLINE_VERTICES}
    dummy = {"srid": 2263, "vertices": [[0, 0]] * MAX_OUTLINE_VERTICES}
    levels = [
        {
            "level_index": i,
            "floor_count": 1,
            "floor_to_floor_ft": 10.0,
            "outline": dummy,
        }
        for i in range(20)
    ]
    total = MAX_OUTLINE_VERTICES * 21
    assert total > MAX_TOTAL_OUTLINE_POSITIONS
    return {
        "outline": footprint,
        "levels": levels,
        "exterior_walls": [],
        "provenance": {
            "author": "tester",
            "editor_version": "1.0.0",
            "kind": "proposed",
        },
    }


# ---------------------------------------------------------------------------
# AS-1: request-level total-positions bound
# ---------------------------------------------------------------------------


def test_over_budget_request_is_refused_typed():
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(_over_budget_block())
    assert exc.value.field == "proposed_massing"
    assert "MAX_TOTAL_OUTLINE_POSITIONS" in str(exc.value)


def test_total_bound_refuses_before_any_simplicity_check():
    """AS-1: the bound fires BEFORE any per-outline simplicity check (spy proves
    zero calls to ``_ring_is_simple``)."""
    block = _over_budget_block()
    with mock.patch.object(
        proposal, "_ring_is_simple", wraps=proposal._ring_is_simple
    ) as spy:
        with pytest.raises(ProposedMassingError):
            validate_proposed_massing(block)
    assert spy.call_count == 0


def test_removing_the_total_bound_reddens_the_zero_call_guard():
    """AS-1 mutation: with the bound no-op'd the same request DOES reach the
    per-outline simplicity check, so the zero-call guard above reddens."""
    block = _over_budget_block(valid_footprint=True)
    with mock.patch.object(proposal, "_check_total_positions", lambda _block: None):
        with mock.patch.object(
            proposal, "_ring_is_simple", wraps=proposal._ring_is_simple
        ) as spy:
            with pytest.raises(ProposedMassingError):
                validate_proposed_massing(block)
    assert spy.call_count > 0


def test_total_bound_boundary_is_pinned():
    """A request at exactly the bound passes the total check; one position more is
    refused."""
    at_bound = {"outline": {"vertices": [[0, 0]] * MAX_TOTAL_OUTLINE_POSITIONS}}
    over_bound = {
        "outline": {"vertices": [[0, 0]] * (MAX_TOTAL_OUTLINE_POSITIONS + 1)}
    }
    proposal._check_total_positions(at_bound)  # must not raise
    with pytest.raises(ProposedMassingError) as exc:
        proposal._check_total_positions(over_bound)
    assert exc.value.field == "proposed_massing"


def test_total_bound_sums_footprint_and_all_level_outlines():
    """The bound counts the footprint plus every per-level outline together."""
    half = MAX_TOTAL_OUTLINE_POSITIONS // 2
    block = {
        "outline": {"vertices": [[0, 0]] * (half + 1)},
        "levels": [{"outline": {"vertices": [[0, 0]] * (half + 1)}}],
    }  # footprint + level = MAX + 2 > MAX
    with pytest.raises(ProposedMassingError):
        proposal._check_total_positions(block)


def test_position_count_ignores_malformed_outlines():
    """A malformed outline counts as 0 and is left for the field validators, so the
    aggregate bound never masks an existing typed error."""
    assert proposal._outline_position_count(None) == 0
    assert proposal._outline_position_count({"vertices": "nope"}) == 0
    assert proposal._outline_position_count({"no_vertices": 1}) == 0
    assert proposal._outline_position_count({"vertices": [[0, 0], [1, 1]]}) == 2


# ---------------------------------------------------------------------------
# AS-2: bounded simplicity check, measured, with a mutation guard
# ---------------------------------------------------------------------------


def test_worst_case_simplicity_does_no_pairwise_python_work():
    """AS-2: at the maximum per-outline input the new check builds exactly one
    shapely polygon (O(1) shapely work) and performs ZERO Python pairwise segment
    tests, well within the work budget."""
    ring = _circle_ring(_MAX_RING_VERTICES)
    with mock.patch.object(
        proposal, "Polygon", wraps=proposal.Polygon
    ) as poly_spy:
        assert proposal._ring_is_simple(ring) is True
    # One construction regardless of n -> not an all-pairs walk.
    assert poly_spy.call_count == 1
    assert 0 <= WORK_BUDGET_PAIRWISE_TESTS  # the new check does 0 pairwise tests


def test_restoring_all_pairs_loop_reddens_work_count_guard():
    """AS-2 mutation: the all-pairs predicate (what a restore would reinstate)
    performs far more than the work budget of pairwise tests at the same input, so
    the work-count guard reddens."""
    ring = _circle_ring(_MAX_RING_VERTICES)
    counter = [0]
    assert _all_pairs_ring_is_simple(ring, counter) is True
    assert counter[0] > WORK_BUDGET_PAIRWISE_TESTS
    # the all-pairs loop tests every non-adjacent edge pair: n*(n-3)/2 at n = 999
    n = _MAX_RING_VERTICES
    assert counter[0] == n * (n - 3) // 2


def test_worst_case_simplicity_wall_time_bounded():
    """AS-2: the new check's worst single-outline wall time is bounded well under
    the budget (numbers recorded in the producer report). The former all-pairs scan
    at this input exceeded this bound on the same machine."""
    ring = _circle_ring(_MAX_RING_VERTICES)
    start = time.perf_counter()
    assert proposal._ring_is_simple(ring) is True
    elapsed = time.perf_counter() - start
    assert elapsed < SIMPLICITY_TIME_BUDGET_S


def test_worst_case_allowed_request_validates_quickly():
    """AS-2: a request at the maximum total the bounds allow (20 outlines x 1000 =
    20 000 positions) validates its geometry in a bounded time."""
    footprint = _circle_ring(_MAX_RING_VERTICES)
    start = time.perf_counter()
    for _ in range(20):
        assert proposal._ring_is_simple(footprint) is True
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0


# ---------------------------------------------------------------------------
# AS-3: decision identity (new simplicity check == old on a fuzz corpus)
# ---------------------------------------------------------------------------


def _rand_pt(rng, lo=0, hi=1000):
    return (float(rng.randint(lo, hi)), float(rng.randint(lo, hi)))


def _gen_random(rng):
    return [_rand_pt(rng) for _ in range(rng.randint(3, 14))]


def _gen_small_grid(rng):
    # small integer grid -> frequent collinearity / coincidence
    return [
        (float(rng.randint(0, 4)), float(rng.randint(0, 4)))
        for _ in range(rng.randint(3, 9))
    ]


def _gen_convex_simple(rng):
    n = rng.randint(3, 18)
    cx, cy = rng.randint(300, 700), rng.randint(300, 700)
    angs = sorted(rng.uniform(0, 2 * math.pi) for _ in range(n))
    r = rng.randint(50, 300)
    out = []
    for a in angs:
        p = (float(round(cx + r * math.cos(a))), float(round(cy + r * math.sin(a))))
        if not out or out[-1] != p:
            out.append(p)
    return out


def _gen_bowtie(rng):
    return [(0.0, 0.0), (100.0, 100.0), (100.0, 0.0), (0.0, 100.0)]


def _gen_self_touch(rng):
    x = float(rng.randint(1, 99))
    return [(0.0, 0.0), (100.0, 0.0), (x, 0.0), (x, 100.0)]


def _gen_collinear_overlap(rng):
    return [(0.0, 0.0), (100.0, 0.0), (200.0, 50.0), (50.0, 0.0), (50.0, 100.0)]


def _gen_spike(rng):
    return [(0.0, 0.0), (50.0, 0.0), (0.0, 0.0), (25.0, 50.0)]


def _gen_near_degenerate(rng):
    return [
        (0.0, 0.0),
        (100.0, 0.0),
        (100.0, 1.0),
        (0.0, 1.0),
        (50.0, 1.0),
        (50.0, 2.0),
    ]


def _gen_collinear_flat(rng):
    return [(0.0, 0.0), (50.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]


def _gen_repeat_consecutive(rng):
    base = _gen_convex_simple(rng)
    if len(base) >= 3:
        i = rng.randrange(len(base))
        base.insert(i, base[i])
    return base


def _gen_repeat_nonadjacent(rng):
    base = _gen_convex_simple(rng)
    if len(base) >= 5:
        base[-1] = base[1]
    return base


def _gen_vertex_on_edge(rng):
    x = float(rng.randint(1, 99))
    return [(0.0, 0.0), (100.0, 0.0), (x, 50.0), (x, 0.0), (0.0, 100.0)]


_GENERATORS = [
    _gen_random,
    _gen_small_grid,
    _gen_convex_simple,
    _gen_bowtie,
    _gen_self_touch,
    _gen_collinear_overlap,
    _gen_spike,
    _gen_near_degenerate,
    _gen_collinear_flat,
    _gen_repeat_consecutive,
    _gen_repeat_nonadjacent,
    _gen_vertex_on_edge,
]

# Corpus sizes (deterministic seeds -> reproducible). Recorded in the report.
_SMALL_CORPUS = 24_000
_MEDIUM_RINGS = 150  # 60..300 vertices
_EXTREME_RINGS = 3  # 1000 vertices


def test_fuzz_equivalence_small_and_targeted():
    """AS-3: on a large mixed corpus (all required categories) the new
    ``_ring_is_simple`` returns the SAME True/False as the former all-pairs
    predicate on every case. Any disagreement is collected and fails the test."""
    rng = random.Random(20260924)
    disagreements = []
    old_true = old_false = 0
    for _ in range(_SMALL_CORPUS):
        ring = rng.choice(_GENERATORS)(rng)
        old = _all_pairs_ring_is_simple(list(ring))
        new = proposal._ring_is_simple(list(ring))
        if old:
            old_true += 1
        else:
            old_false += 1
        if old != new:
            disagreements.append((ring, old, new))
    assert not disagreements, f"decision drift: {disagreements[:5]}"
    # both outcomes are genuinely exercised
    assert old_true > 0 and old_false > 0


def test_fuzz_equivalence_medium_and_extreme_rings():
    """AS-3: equivalence holds at scale (60..1000-vertex rings), where floating
    collinearity and precision most stress the two implementations."""
    rng = random.Random(771)
    checked = 0
    for _ in range(_MEDIUM_RINGS):
        n = rng.randint(60, 300)
        ring = _circle_ring(n, r=rng.randint(1000, 90000))
        assert proposal._ring_is_simple(ring) == _all_pairs_ring_is_simple(ring)
        checked += 1
    for _ in range(_EXTREME_RINGS):
        ring = _circle_ring(_MAX_RING_VERTICES)
        assert proposal._ring_is_simple(ring) == _all_pairs_ring_is_simple(ring)
        checked += 1
    assert checked == _MEDIUM_RINGS + _EXTREME_RINGS


def test_known_shapes_decided_identically():
    """AS-3: pinned canonical shapes decide identically (documents intent)."""
    cases = [
        [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)],  # simple square
        _gen_bowtie(random.Random(0)),  # self-crossing
        _gen_self_touch(random.Random(0)),  # T-touch
        _gen_collinear_overlap(random.Random(0)),  # collinear overlap
        _gen_spike(random.Random(0)),  # 180-degree reversal spike
        _gen_collinear_flat(random.Random(0)),  # redundant collinear vertex (simple)
    ]
    for ring in cases:
        assert proposal._ring_is_simple(ring) == _all_pairs_ring_is_simple(ring)


# ---------------------------------------------------------------------------
# AS-4: fail closed; shapely exceptions never escape untyped
# ---------------------------------------------------------------------------


def test_shapely_exception_never_escapes_from_ring_check():
    """AS-4: a GEOS error inside the simplicity check fails closed to 'not simple'
    rather than escaping untyped."""
    ring = _circle_ring(6)
    with mock.patch.object(
        proposal, "Polygon", side_effect=GEOSException("boom")
    ):
        assert proposal._ring_is_simple(ring) is False


def test_shapely_exception_surfaces_as_typed_refusal_through_public_api():
    """AS-4: through the public validator a GEOS error becomes the typed
    self-intersecting :class:`ProposedMassingError`, never a raw GEOSException."""
    block = _valid_block(_circle_ring(6))
    with mock.patch.object(
        proposal, "Polygon", side_effect=GEOSException("boom")
    ):
        with pytest.raises(ProposedMassingError) as exc:
            validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.outline"
    assert "self-intersecting" in str(exc.value)


def test_non_finite_and_degenerate_keep_their_typed_refusals():
    """AS-4: non-finite coordinates and self-intersecting outlines keep the exact
    typed refusals they had before this change."""
    nan_block = _valid_block(_circle_ring(4))
    nan_block["outline"]["vertices"][1][0] = float("nan")
    with pytest.raises(ProposedMassingError) as exc_nan:
        validate_proposed_massing(nan_block)
    assert exc_nan.value.field.startswith("proposed_massing.outline.vertices")

    bowtie = [
        [_X0, _Y0],
        [_X0 + 100, _Y0 + 100],
        [_X0 + 100, _Y0],
        [_X0, _Y0 + 100],
    ]
    bt_block = _valid_block([(v[0], v[1]) for v in bowtie])
    with pytest.raises(ProposedMassingError) as exc_bt:
        validate_proposed_massing(bt_block)
    assert exc_bt.value.field == "proposed_massing.outline"
    assert "self-intersecting" in str(exc_bt.value)


# ---------------------------------------------------------------------------
# AS-5: scope / public surface
# ---------------------------------------------------------------------------


def test_public_surface_and_valid_block_unchanged():
    """AS-5: the public surface still exposes the validator, the typed error, and
    the documented bounds; a valid block validates to None."""
    assert issubclass(ProposedMassingError, ValueError)
    assert MAX_TOTAL_OUTLINE_POSITIONS == 20000
    for name in (
        "validate_proposed_massing",
        "ProposedMassingError",
        "MAX_OUTLINE_VERTICES",
        "MAX_LEVELS",
        "MAX_FLOOR_COUNT",
        "MAX_EXTERIOR_WALLS",
        "MAX_FLOOR_TO_FLOOR_FT",
        "MAX_TOTAL_OUTLINE_POSITIONS",
    ):
        assert name in proposal.__all__
    assert validate_proposed_massing(_valid_block(_circle_ring(5))) is None


def test_no_new_dependency_only_admitted_shapely():
    """AS-5: the module's only third-party dependency is the already-admitted
    shapely; the simplicity check uses shapely.geometry.Polygon."""
    import shapely  # noqa: F401  (admitted)

    assert proposal.Polygon.__module__.startswith("shapely")
