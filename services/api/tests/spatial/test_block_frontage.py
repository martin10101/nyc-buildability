"""Unit tests for the block-frontage measure (task M5-T167, S1/S2/S9/S15).

The measure is PURE geometry over the single-lot DCM street window: it finds the two streets
bounding the block along the frontage and measures their separation, inventing nothing. It
holds NO zoning number and applies NO 230-ft threshold (that is the scenario-layer
rear_yard_checks.py). These tests pin: a clean two-sided block gives the separation and the
bounding streets' widths; any failure (no window, no lot location, a missing frontage
centreline, a cross-street on only one side) gives a NOT-KNOWN measure, never a guess (S15);
and a DCM width that is a range or 'Unknown' is never collapsed to one value (DB-260).

Input state, outcome, test (the producer-report input-state table for the measure):
  two opposite cross-streets   -> known; separation + widths -> test_two_bounding_streets_measured
  one side only                -> not known; empty           -> test_one_sided_window_is_not_known
  frontage street not in window-> not known; empty           -> test_missing_frontage_is_not_known
  no street window             -> not known; empty           -> test_no_window_is_not_known
  no lot location              -> not known; empty           -> test_no_lot_point_is_not_known
  nearer vs farther cross-street-> known; nearest chosen -> test_nearest_cross_street_on_each_side
  width '60'/'60-80'/'Unknown'/''/None -> 60.0/None -> test_street_mapped_width_single_number_only
"""

from __future__ import annotations

from app.spatial.site_geometry.block_frontage import (
    BASIS_CENTRELINE,
    measure_block_frontage,
    street_mapped_width_ft,
)
from app.spatial.site_geometry.inputs import StreetCenterline, StreetData

_CRS: dict = {"wkid": 2263}


def _line(key, name, path, width="60", ok=True, oid=1):
    return StreetCenterline(
        street_key=key, street_name=name, object_id=oid, paths=(tuple(path),),
        mapped_width_raw=width, status_ok=ok,
    )


def _data(*centerlines):
    return StreetData(
        centerlines=tuple(centerlines), covered_envelope=(-300.0, -300.0, 300.0, 300.0),
        crs=_CRS, source="test",
    )


# A frontage street along the x-axis; two cross-streets along y at x = -130 and x = +130.
_FRONTAGE = _line("northern", "Northern Boulevard", [(-250.0, 0.0), (250.0, 0.0)], width="100")
_WEST = _line("st215", "215 Street", [(-130.0, -250.0), (-130.0, 250.0)], width="60")
_EAST = _line("pl215", "215 Place", [(130.0, -250.0), (130.0, 250.0)], width="60")


def test_two_bounding_streets_measured() -> None:
    measure = measure_block_frontage(
        "northern", _data(_FRONTAGE, _WEST, _EAST), lot_point=(0.0, 0.0)
    )
    assert measure.known is True
    # 130 ft to each cross-street along the frontage -> a 260 ft block face (centreline basis).
    assert measure.separations == {BASIS_CENTRELINE: 260.0}
    names = {s.street_name for s in measure.bounding_streets}
    assert names == {"215 Street", "215 Place"}
    assert all(s.width_ft == 60.0 for s in measure.bounding_streets)


def test_one_sided_window_is_not_known() -> None:
    # Only one cross-street (west side): the block dimension is not known (S15), not guessed.
    measure = measure_block_frontage("northern", _data(_FRONTAGE, _WEST), lot_point=(0.0, 0.0))
    assert measure.known is False
    assert measure.separations == {}
    assert measure.bounding_streets == ()
    assert "both sides" in measure.reason


def test_missing_frontage_is_not_known() -> None:
    # The frontage street's own centreline is not in the window.
    measure = measure_block_frontage("northern", _data(_WEST, _EAST), lot_point=(0.0, 0.0))
    assert measure.known is False
    assert measure.separations == {}


def test_no_window_is_not_known() -> None:
    assert measure_block_frontage("northern", None, lot_point=(0.0, 0.0)).known is False


def test_no_lot_point_is_not_known() -> None:
    assert measure_block_frontage(
        "northern", _data(_FRONTAGE, _WEST, _EAST), lot_point=None
    ).known is False


def test_nearest_cross_street_on_each_side() -> None:
    # A farther cross-street on the east side must not displace the nearer one.
    far_east = _line("pl216", "216 Place", [(210.0, -250.0), (210.0, 250.0)], width="60", oid=9)
    measure = measure_block_frontage(
        "northern", _data(_FRONTAGE, _WEST, _EAST, far_east), lot_point=(0.0, 0.0)
    )
    assert measure.known is True
    assert measure.separations == {BASIS_CENTRELINE: 260.0}  # the 130-ft east street, not 210
    assert {s.street_name for s in measure.bounding_streets} == {"215 Street", "215 Place"}


def test_parallel_streets_are_not_bounding() -> None:
    # A street PARALLEL to the frontage (another east-west road) is not a bounding cross-street.
    parallel = _line("other", "Other Boulevard", [(-250.0, 80.0), (250.0, 80.0)], oid=7)
    measure = measure_block_frontage(
        "northern", _data(_FRONTAGE, _WEST, _EAST, parallel), lot_point=(0.0, 0.0)
    )
    assert measure.known is True
    assert {s.street_name for s in measure.bounding_streets} == {"215 Street", "215 Place"}


def test_street_mapped_width_single_number_only() -> None:
    assert street_mapped_width_ft("60") == 60.0
    assert street_mapped_width_ft("60-80") is None  # a range is never collapsed (DB-260)
    assert street_mapped_width_ft("Unknown") is None
    assert street_mapped_width_ft("") is None
    assert street_mapped_width_ft(None) is None
    assert street_mapped_width_ft("0") is None  # zero is not a usable width
