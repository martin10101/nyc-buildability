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
