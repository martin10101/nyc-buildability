"""Planar geometry used to validate and draw outlines (task E-01)."""

from __future__ import annotations

from app.drawings.kit import geometry as geo

SQUARE = ((0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0))
ELL = ((0.0, 0.0), (6.0, 0.0), (6.0, 3.0), (3.0, 3.0), (3.0, 7.0), (0.0, 7.0), (0.0, 0.0))


def test_signed_area_and_orientation():
    assert geo.signed_area(SQUARE) == 100.0
    assert geo.signed_area(tuple(reversed(SQUARE))) == -100.0
    assert geo.signed_area(ELL) == 30.0


def test_simple_rings():
    assert geo.is_simple(SQUARE)
    assert geo.is_simple(ELL)
    bow_tie = ((0.0, 0.0), (10.0, 10.0), (10.0, 0.0), (0.0, 10.0), (0.0, 0.0))
    assert not geo.is_simple(bow_tie)
    fold_back = ((0.0, 0.0), (10.0, 0.0), (5.0, 0.0), (0.0, 10.0), (0.0, 0.0))
    assert not geo.is_simple(fold_back)
    repeated = ((0.0, 0.0), (10.0, 0.0), (10.0, 0.0), (0.0, 10.0), (0.0, 0.0))
    assert not geo.is_simple(repeated)


def test_point_location():
    assert geo.point_location((5.0, 5.0), SQUARE) == "inside"
    assert geo.point_location((10.0, 5.0), SQUARE) == "boundary"
    assert geo.point_location((11.0, 5.0), SQUARE) == "outside"
    assert geo.point_location((5.0, 5.0), ELL) == "outside"  # in the notch


def test_ring_within_handles_concave_outer():
    inside = ((0.0, 0.0), (6.0, 0.0), (6.0, 3.0), (0.0, 3.0), (0.0, 0.0))
    assert geo.ring_within(inside, ELL)
    across_notch = ((1.0, 2.0), (5.0, 2.0), (5.0, 5.0), (1.0, 5.0), (1.0, 2.0))
    assert not geo.ring_within(across_notch, ELL)
    assert geo.ring_within(SQUARE, SQUARE)  # touching the boundary is allowed


def test_outward_normal_points_away_from_interior():
    assert geo.outward_normal((0.0, 0.0), (10.0, 0.0), geo.signed_area(SQUARE)) == (0.0, -1.0)
    ccw_area = geo.signed_area(tuple(reversed(SQUARE)))
    assert geo.outward_normal((10.0, 0.0), (0.0, 0.0), ccw_area) == (-0.0, -1.0)


def test_centroid_and_bbox():
    assert geo.centroid(SQUARE) == (5.0, 5.0)
    assert geo.bbox(ELL) == (0.0, 0.0, 6.0, 7.0)


NOTCHED_LOT = ((0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (6.0, 10.0), (6.0, 5.0), (5.0, 2.0),
               (4.0, 5.0), (4.0, 10.0), (0.0, 10.0), (0.0, 0.0))


def test_ring_within_sees_a_notch_touching_only_at_vertices():
    """Review probe: the plate's edge y=5 passes through the notch's vertices
    (4,5) and (6,5); (5, 2.5) is inside the plate and outside the lot."""
    plate = ((0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (8.0, 5.0), (0.0, 5.0), (0.0, 0.0))
    assert geo.point_location((5.0, 2.5), plate) == "inside"
    assert geo.point_location((5.0, 2.5), NOTCHED_LOT) == "outside"
    assert not geo.ring_within(plate, NOTCHED_LOT)
    below_notch = ((0.0, 0.0), (10.0, 0.0), (10.0, 2.0), (0.0, 2.0), (0.0, 0.0))
    assert geo.ring_within(below_notch, NOTCHED_LOT)  # touches the notch tip only


def test_split_probes_cut_edges_at_the_other_rings_vertices():
    probes = geo.split_probes(((0.0, 0.0), (10.0, 0.0), (10.0, 1.0), (0.0, 1.0), (0.0, 0.0)),
                              ((4.0, 0.0), (6.0, 0.0), (5.0, -1.0), (4.0, 0.0)))
    assert (5.0, 0.0) in probes and (2.0, 0.0) in probes and (8.0, 0.0) in probes


def test_interiors_overlap():
    assert geo.interiors_overlap(SQUARE, SQUARE)
    inner = ((2.0, 2.0), (4.0, 2.0), (4.0, 4.0), (2.0, 4.0), (2.0, 2.0))
    assert geo.interiors_overlap(SQUARE, inner) and geo.interiors_overlap(inner, SQUARE)
    beside = ((10.0, 0.0), (20.0, 0.0), (20.0, 10.0), (10.0, 10.0), (10.0, 0.0))
    assert not geo.interiors_overlap(SQUARE, beside)  # shares an edge only
