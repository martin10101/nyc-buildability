"""M5-T152 (S1, S7, S8): the street frontages the spatial engine matches are carried into
``geometry.streets`` and drawn with their names.

Every document here is GENERATED from the recorded benchmark evidence through the real entry
(``run_engine_and_result_ways_from_evidence``), exactly as the journey test builds it, so a change
to ``geometry._build_streets`` (emptying ``streets`` again) changes the generated output and is
caught here - this is the task's streets mutation proof.

The expected names and frontage lengths are read from the SAME spatial site geometry the product
reads (``StreetFrontage.street_name`` / ``StreetFrontage.length``), never retyped (S8).
"""

from __future__ import annotations

import math

from app.spatial.site_geometry.outline import prepare_outline
from app.spatial.site_geometry.results import FRONTAGE_CONFIRMED
from tests.spatial._northern_replay import (
    DCM_ENVELOPE,
    replay_dcm_page,
    replay_lot_geometry,
)

from .test_geometry_lot_outline import _emit  # the recorded-evidence emitter (outline on/off)

_ON_EDGE_TOL_FT = 0.01


def _site_frontages():
    """The spatial site geometry's confirmed frontages for the benchmark lot, built offline through
    the real connectors from the recorded pack - the SAME objects the product reads."""
    from app.spatial.site_geometry import (
        derive_site_geometry,
        lot_outline_from_mappluto,
        street_data_from_pages,
    )

    lot, _unused = lot_outline_from_mappluto(replay_lot_geometry())
    streets = street_data_from_pages([replay_dcm_page()], envelope=DCM_ENVELOPE)
    geometry = derive_site_geometry(lot, streets)
    prepared, _reason = prepare_outline(lot)
    return [f for f in geometry.frontages if f.status == FRONTAGE_CONFIRMED], prepared


def _polyline_length(line: list[list[float]]) -> float:
    return sum(math.hypot(line[i + 1][0] - line[i][0], line[i + 1][1] - line[i][1])
               for i in range(len(line) - 1))


def _dist_to_boundary(point, ring) -> float:
    best = math.inf
    for a, b in zip(ring, ring[1:], strict=False):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length_sq = dx * dx + dy * dy
        t = max(0.0, min(1.0, ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / length_sq)) \
            if length_sq else 0.0
        best = min(best, math.hypot(point[0] - (a[0] + t * dx), point[1] - (a[1] + t * dy)))
    return best


# =========================================================================== S1 / S8
def test_s1_streets_carry_the_engine_frontages_on_the_outline(monkeypatch) -> None:
    """S1/S8: with the tax-map outline threaded, geometry.streets lists the confirmed frontages the
    spatial engine matched, each with its name, its frontage line on the lot outline (local feet)
    and its (null) street-width fact id; every point lies on an outline edge within 0.01 ft; the
    names are the recorded source's own street names.

    MUTATION PROOF (streets emptied again): _build_streets returning [] would leave streets empty
    and fail the name and non-empty assertions below."""
    geometry = _emit(monkeypatch, outline=True)["geometry"]
    ring = geometry["lot_outline"][0]
    streets = geometry["streets"]
    frontages, _prepared = _site_frontages()

    expected_names = {f.street_name for f in frontages}
    assert expected_names  # the benchmark corner lot has confirmed frontages
    assert {s["street"] for s in streets} == expected_names  # the recorded source's names
    assert len(streets) == len(frontages)

    for street in streets:
        assert set(street) == {"street", "frontage_line", "street_width_fact_id"}
        assert street["street_width_fact_id"] is None  # no street-width figure derived here
        line = street["frontage_line"]
        assert len(line) >= 2
        for point in line:
            assert _dist_to_boundary(point, ring) <= _ON_EDGE_TOL_FT, (street["street"], point)


def test_s8_each_frontage_line_length_matches_the_engine_frontage(monkeypatch) -> None:
    """S8: each drawn frontage line's length equals the spatial engine's own frontage length
    (read from StreetFrontage.length, never retyped) within 0.01 ft."""
    streets = _emit(monkeypatch, outline=True)["geometry"]["streets"]
    frontages, _prepared = _site_frontages()
    by_name = {f.street_name: f for f in frontages}
    for street in streets:
        frontage = by_name[street["street"]]
        assert frontage.length.value is not None
        assert abs(_polyline_length(street["frontage_line"]) - frontage.length.value) <= 0.01


# =========================================================================== S7
def test_s7_no_outline_leaves_streets_absent_and_nothing_invented(monkeypatch) -> None:
    """S7: with no outline (the live route with the spatial provider off), the whole geometry block
    is not_available - no streets are invented, and no frontage is drawn from the recorded area."""
    geometry = _emit(monkeypatch, outline=False)["geometry"]
    assert geometry["status"] == "not_available"
    assert "streets" not in geometry
