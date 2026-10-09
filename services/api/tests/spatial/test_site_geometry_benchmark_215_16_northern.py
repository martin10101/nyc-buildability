"""Benchmark: site geometry for 215-16 Northern Blvd, Queens (BBL 4073340070).

Queue item B-03 (plan M1-13 data side, §4) on the recorded B-01 pack, replayed offline
through the real connectors. Expected (competitor review §A; fixture README): a corner lot
at Northern Blvd and 215 Place with frontage of about 100 ft on each; the outline area is
compared with the PLUTO lot area and the difference reported.

Stated tolerance: each frontage is within BENCHMARK_FRONTAGE_TOLERANCE_FT (5 ft) of 100 ft.
The recorded DOB filing (A3 440655961) says 100' on 215 Place and 100.76' on Northern Blvd;
the MapPLUTO 26v2 outline measures 99.98 ft and 103.88 ft (README, disagreement 1), so the
tolerance must cover the documented 3.1 ft tax-map difference. The exact outline readings
are pinned separately to 0.01 ft.
"""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from app.spatial.site_geometry import (
    LABEL_CITY_RECORDS,
    LABEL_TAX_MAP,
    LABEL_UNKNOWN,
    LotOutline,
    derive_site_geometry,
    derive_site_geometry_from_sources,
    lot_outline_from_mappluto,
    street_data_from_pages,
)
from app.spatial.site_geometry.parameters import STREET_LINE_UNCERTAINTY_BAND_FT
from app.spatial.site_geometry.results import (
    EDGE_FRONTS,
    EDGE_NO_STREET,
    FRONTAGE_CONFIRMED,
    FRONTAGE_UNCERTAIN,
    RELATION_CORNER,
    STATUS_COMPLETE,
    STATUS_PARTIAL,
    STATUS_REFUSED,
)

from ._northern_replay import (
    DCM_ENVELOPE,
    DCM_FILE,
    PACK,
    manifest_digest,
    replay_dcm_page,
    replay_lot_geometry,
    replay_pluto,
)

BENCHMARK_FRONTAGE_TOLERANCE_FT = 5.0
NORTHERN = "Northern Boulevard"
PLACE = "215 Place"


@pytest.fixture(scope="module")
def result():
    return derive_site_geometry_from_sources(
        replay_lot_geometry(), [replay_dcm_page()], envelope=DCM_ENVELOPE,
        pluto_result=replay_pluto())


def test_corner_lot_on_northern_blvd_and_215_place(result):
    assert result.status == STATUS_COMPLETE
    assert result.lot_type.kind == "corner"
    assert result.lot_type.label == LABEL_TAX_MAP
    assert result.lot_type.reason_code is None
    # No lot line is uncertain, so no reading of one could change the type.
    assert result.lot_type.unconfirmed_lot_lines == ()
    assert result.lot_type.streets == (PLACE, NORTHERN)
    (relation,) = result.lot_type.relations
    assert relation.relation == RELATION_CORNER
    assert relation.angle_deg == pytest.approx(89.7, abs=0.1)


@pytest.mark.parametrize(("street", "outline_ft", "segment", "width"), [
    (NORTHERN, 103.88, 53832, "100"),
    (PLACE, 99.98, 11453, "60"),
])
def test_frontage_per_street(result, street, outline_ft, segment, width):
    frontage = result.frontage(street)
    assert frontage.status == FRONTAGE_CONFIRMED
    assert frontage.length.label == LABEL_TAX_MAP
    assert abs(frontage.length.value - 100.0) <= BENCHMARK_FRONTAGE_TOLERANCE_FT
    assert frontage.length.value == pytest.approx(outline_ft, abs=0.01)
    assert frontage.segment_object_ids == (segment,)
    assert frontage.mapped_width_raw == (width,)
    # README: the lot lines sit about 1 ft off half the mapped width (51.0 / 28.8 ft).
    assert frontage.max_street_line_gap_ft < 1.5


def test_only_the_two_street_sides_front_a_street(result):
    verdicts = sorted(e.verdict for e in result.edges)
    assert verdicts == [EDGE_FRONTS, EDGE_FRONTS, EDGE_NO_STREET, EDGE_NO_STREET, EDGE_NO_STREET]
    assert all(e.reason_codes == () for e in result.edges)
    assert result.street_crossings == ()


def test_west_side_is_clear_of_215_street_beyond_the_uncertainty_band():
    # The west lot line looks at 215 Street (DCM 3134, width 60): its street line is about
    # 97 ft away, beyond the 80 ft band, so the west side reads "no street" on that band.
    streets = street_data_from_pages([replay_dcm_page()], envelope=DCM_ENVELOPE)
    moved = tuple(
        c if c.street_key != "215 Street" else replace(
            c, paths=tuple(tuple((x + 20.0, y) for x, y in path) for path in c.paths))
        for c in streets.centerlines)
    lot, _ = lot_outline_from_mappluto(replay_lot_geometry())
    nearer = derive_site_geometry(lot, replace(streets, centerlines=moved))
    assert STREET_LINE_UNCERTAINTY_BAND_FT == 80.0
    # 20 ft closer (about 77 ft): the west side becomes uncertain, but the lot is a corner
    # lot under either reading, so the type stays corner and the frontage list stays open.
    assert nearer.lot_type.kind == "corner"
    assert len(nearer.lot_type.unconfirmed_lot_lines) == 1
    assert nearer.status == STATUS_PARTIAL
    assert nearer.frontage("215 Street").status == FRONTAGE_UNCERTAIN


def test_area_checked_against_pluto_and_difference_reported(result):
    assert result.lot_area.value == pytest.approx(10387.99, abs=0.01)
    assert result.lot_area.label == LABEL_TAX_MAP
    assert result.lot_area.rank == "approximate_tax_map"
    assert result.city_records.lot_area.rank == "city_records"
    assert result.lot_depth.rank == "unknown"
    recorded = result.city_records.lot_area
    assert (recorded.value, recorded.label) == (10075.0, LABEL_CITY_RECORDS)
    check = result.area_check
    assert check.difference_sq_ft == pytest.approx(312.99, abs=0.01)
    assert check.difference_pct == pytest.approx(3.11, abs=0.01)
    assert check.statement in result.notes


def test_depth_per_street_and_no_single_corner_depth(result):
    northern = result.frontage(NORTHERN).depth
    place = result.frontage(PLACE).depth
    assert northern.mean.value == pytest.approx(99.97, abs=0.05)
    assert place.mean.value == pytest.approx(103.9, abs=0.05)
    # Straight back to the rear lot line only: the corners are not square to 0.3 degrees,
    # so points right beside a corner would otherwise exit through the side lot line.
    assert northern.minimum.value >= 99.9 and place.minimum.value >= 103.8
    assert northern.mean.label == place.mean.label == LABEL_TAX_MAP
    assert result.lot_depth.value is None and result.lot_depth.label == LABEL_UNKNOWN
    assert result.city_records.lot_depth.value == 100.0
    assert result.city_records.lot_front.value == 100.76


def test_provenance_pins_the_recorded_bytes(result):
    lot = result.provenance["lot_outline"]
    assert lot["dataset_version"] == "26v2"
    assert lot["raw_digest"] == manifest_digest("mappluto_lot_4073340070_epsg2263.json")
    streets = result.provenance["streets"]
    assert streets["raw_digests"] == [manifest_digest(DCM_FILE)]
    assert streets["envelope"] == list(DCM_ENVELOPE)
    assert result.provenance["city_records"]["dataset_version"] == "26v2"


def test_display_outline_in_degrees_is_never_measured():
    doc = json.loads((PACK / "mappluto_lot_outline_4073340070_epsg4326.geojson").read_text())
    geometry = doc["features"][0]["geometry"]
    assert geometry["type"] == "Polygon"
    ring = geometry["coordinates"][0]
    outline = LotOutline(tuple(tuple(p) for p in ring), {"wkid": 4326, "latest_wkid": 4326},
                         "MapPLUTO display outline")
    refused = derive_site_geometry(outline, None)
    assert refused.status == STATUS_REFUSED
    assert refused.lot_area.value is None
