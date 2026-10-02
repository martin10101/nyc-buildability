"""Touching check and combined outline do not depend on lot order (B-07; review #281 B1).

Neighbouring tax lots do not always share corners. A narrower rear lot's corners can sit in
the middle of a deeper lot's rear line, where that lot has no vertex (a T-junction), and the
MapPLUTO adapter measures the verbatim, unrounded ring. These SYNTHETIC lots reproduce the
review's cases: unrounded rings rotated like block 7334 (12.82 degrees), the 0.004 ft
T-junction, and a front lot with a row of narrower rear lots, rotated at random and rounded
to 0.01 ft, in random order. Every lot here truly shares its lines, so every selection must
be offered and measured, with the same answer in every order.
"""

from __future__ import annotations

import math
import random

import pytest
from shapely.geometry import Point, Polygon

from app.spatial.multi_lot_site import (
    COMBINATION_OFFERED,
    SiteLot,
    build_lot_choice,
    derive_multi_lot_site,
)
from app.spatial.multi_lot_site.conform import conform_outlines
from app.spatial.site_geometry import LotOutline

CRS = {"wkid": 102718, "latest_wkid": 2263}
BLOCK_7334_ORIGIN = (1048691.85240746, 216386.032158852)  # lot 1's recorded corner


def lot(n: int, ring) -> SiteLot:
    return SiteLot(f"4073340{n:03d}", LotOutline(tuple(ring), CRS, "synthetic tax-lot"))


def rotated(degrees: float, origin=BLOCK_7334_ORIGIN, digits: int | None = None):
    theta = math.radians(degrees)
    ox, oy = origin

    def point(x: float, y: float):
        px = ox + x * math.cos(theta) - y * math.sin(theta)
        py = oy + x * math.sin(theta) + y * math.cos(theta)
        return (px, py) if digits is None else (round(px, digits), round(py, digits))
    return point


def site_for(lots):
    return derive_multi_lot_site(
        build_lot_choice([x.bbl for x in lots], {x.bbl: x for x in lots}), None, None)


def summary(site):
    """Everything the order must not change."""
    return (site.combination, site.outline, site.geometry, site.lot_area_sum)


def area_sum(lots) -> float:
    return sum(Polygon(x.outline.exterior).area for x in lots)


# ------------------------------------------------------------------ T-junctions (review B1)


@pytest.mark.parametrize("degrees", [12.82, 17.0, 33.3, 45.0])
def test_rear_lot_meeting_mid_line_touches_in_both_orders(degrees):
    r = rotated(degrees)
    front = lot(1, [r(0, 0), r(99.25, 0), r(99.25, 100), r(0, 100)])  # 4 corners, like lot 1
    rear = lot(3, [r(40, 100), r(80, 100), r(80, 200), r(40, 200)])    # corners mid-line
    first, second = site_for([front, rear]), site_for([rear, front])
    assert summary(first) == summary(second)
    assert first.combination.status == COMBINATION_OFFERED
    (shared,) = first.combination.shared_lines
    assert shared.length_ft == 40.0
    assert first.geometry.lot_area.value == pytest.approx(area_sum([front, rear]), abs=0.01)


@pytest.mark.parametrize("offset", [0.0, 0.004])
def test_side_lot_meeting_a_long_line_mid_span_touches_in_both_orders(offset):
    deep = lot(1, ((0, 0), (100, 0), (100, 200), (0, 200)))
    side = lot(2, ((100 + offset, 50), (200, 50), (200, 150), (100 + offset, 150)))
    first, second = site_for([deep, side]), site_for([side, deep])
    assert summary(first) == summary(second)
    assert first.combination.status == COMBINATION_OFFERED
    assert first.combination.shared_lines[0].length_ft == 100.0
    assert first.geometry.lot_area.value == pytest.approx(30000.0, abs=0.5)


def test_conforming_nodes_the_t_junction_and_leaves_a_real_gap_alone():
    r = rotated(12.82)
    front = Polygon([r(0, 0), r(99.25, 0), r(99.25, 100), r(0, 100)])
    rear = Polygon([r(40, 100), r(80, 100), r(80, 200), r(40, 200)])
    away = Polygon([r(40, 100.05), r(80, 100.05), r(80, 200), r(40, 200)])  # 0.05 ft gap
    (cf, cr), refusal = conform_outlines([front, rear])
    assert refusal is None
    assert len(cf.exterior.coords) == len(front.exterior.coords) + 2  # rear corners inserted
    assert cr.equals_exact(rear, 0.0)  # no front vertex lies near the rear lot's lines
    assert set(rear.exterior.coords) & set(cf.exterior.coords) == {r(40, 100), r(80, 100)}
    assert cf.boundary.intersection(cr.boundary).length == pytest.approx(40.0, abs=1e-6)
    (gf, ga), _ = conform_outlines([front, away])
    assert (gf.equals_exact(front, 0.0), ga.equals_exact(away, 0.0)) == (True, True)
    assert gf.distance(ga) == pytest.approx(0.05, abs=1e-6)


# --------------------------------------------- a front lot and a row of narrower rear lots


def _row(rng: random.Random, width: float, degrees: float):
    r = rotated(degrees, origin=(1e6, 2e5), digits=2)
    lots = [lot(1, [r(0, 0), r(100, 0), r(100, 100), r(0, 100)])]
    x, n = 0.0, 2
    while x < 100 - 1e-6:
        x2 = min(100.0, x + width)
        if 100.0 - x2 < 1.0:  # no rear lot narrower than 1 ft (33.33 x 3 leaves 0.01 ft)
            x2 = 100.0
        lots.append(lot(n, [r(x, 100), r(x2, 100), r(x2, 200), r(x, 200)]))
        x, n = x2, n + 1
    rng.shuffle(lots)
    return lots


@pytest.mark.parametrize("width", [20, 25, 33.33, 40, 50])
@pytest.mark.parametrize("degrees", [0.0, 12.82, 30.0, 61.7, 89.0])
def test_front_lot_and_rear_row_are_offered_and_measured(width, degrees):
    lots = _row(random.Random(f"{width}-{degrees}"), width, degrees)
    site = site_for(lots)
    assert site.combination.status == COMBINATION_OFFERED
    front_lines = [s.length_ft for s in site.combination.shared_lines
                   if "4073340001" in (s.first_bbl, s.second_bbl)]
    assert sum(front_lines) == pytest.approx(100.0, abs=0.05)
    assert all(s.length_ft == pytest.approx(100.0, abs=0.02)
               for s in site.combination.shared_lines
               if "4073340001" not in (s.first_bbl, s.second_bbl))
    assert site.geometry.lot_area.value == pytest.approx(area_sum(lots), abs=0.6)


def test_three_hundred_random_rows_are_all_offered_whatever_the_order():
    rng = random.Random(1)
    outcomes = {}
    for trial in range(300):
        lots = _row(rng, rng.choice([20, 25, 50]), rng.uniform(0, 90))
        site = site_for(lots)
        key = (site.combination.status, site.geometry is not None)
        outcomes[key] = outcomes.get(key, 0) + 1
        if trial % 25 == 0:  # 12 trials, each re-run in 4 freshly shuffled orders
            for _ in range(4):
                order = rng.sample(lots, len(lots))
                assert summary(site_for(order)) == summary(site)
    assert outcomes == {(COMBINATION_OFFERED, True): 300}


def test_a_lot_narrower_than_the_tolerance_is_refused_with_the_reason():
    # 33.33 ft rear lots leave a 0.01 ft-wide last lot, below what its lines can be matched
    # at: not offered, with that reason (never a false "meet only at a point").
    r = rotated(12.82, origin=(1e6, 2e5), digits=2)
    front = lot(1, [r(0, 0), r(100, 0), r(100, 100), r(0, 100)])
    rear = [lot(n, [r(x, 100), r(x2, 100), r(x2, 200), r(x, 200)])
            for n, (x, x2) in enumerate([(0, 33.33), (33.33, 66.66), (66.66, 99.99),
                                         (99.99, 100.0)], start=2)]
    site = site_for([front, *rear])
    assert site.combination.status == "not_offered"
    assert site.combination.reason == (
        "Lot 5 is narrower than 0.02 ft in places, so its tax-map lines cannot be matched to "
        "its neighbours'. The tax-map lines need review.")
    assert (site.geometry, site.lot_area_sum.value) == (None, None)


def test_swapping_the_lot_numbers_does_not_change_the_measurement():
    # Review #281 r2 N5: the same shapes with their BBLs swapped give the same outline and
    # measurements, so the result rests on the geometry, not on the BBL sort.
    r = rotated(12.82)
    front_ring = [r(0, 0), r(99.25, 0), r(99.25, 100), r(0, 100)]
    rear_ring = [r(40, 100), r(80, 100), r(80, 200), r(40, 200)]
    first = site_for([lot(1, front_ring), lot(3, rear_ring)])
    swapped = site_for([lot(3, front_ring), lot(1, rear_ring)])
    assert first.outline.exterior == swapped.outline.exterior
    for site in (first, swapped):
        assert site.combination.status == COMBINATION_OFFERED
        assert [s.length_ft for s in site.combination.shared_lines] == [40.0]
    assert first.geometry.lot_area == swapped.geometry.lot_area
    assert first.geometry.edges == swapped.geometry.edges


def test_chained_corners_move_further_than_the_tolerance_but_never_join_a_real_gap():
    # Review #281 r2 (d): corners at x = 100, 100.008 and 100.016 chain into one group, so
    # lot C's corner moves 0.016 ft. Lots A and C are 0.016 ft apart and still do not touch.
    a = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
    b = Polygon([(50, 100), (100.008, 100), (100.008, 200), (50, 200)])
    c = Polygon([(100.016, 0), (200, 0), (200, 100), (100.016, 100)])
    (_, _, moved_c), refusal = conform_outlines([a, b, c])
    assert refusal is None
    largest = max(Point(p).distance(Point(q))
                  for p, q in zip(c.exterior.coords, moved_c.exterior.coords, strict=True))
    assert largest == pytest.approx(0.016, abs=1e-9)
    lots = [lot(1, a.exterior.coords[:-1]), lot(2, b.exterior.coords[:-1]),
            lot(3, c.exterior.coords[:-1])]
    pair = site_for([lots[0], lots[2]])
    assert pair.combination.status == "not_offered"
    assert "lots 1 and 3 are 0.016 ft apart" in pair.combination.reason
    assert summary(site_for(lots)) == summary(site_for(lots[::-1]))

