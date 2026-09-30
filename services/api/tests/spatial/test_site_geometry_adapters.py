"""Connector-result adapters for site geometry fail closed (queue item B-03).

Starts from the recorded 215-16 Northern Blvd connector results (offline replay) and
changes one thing at a time.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from app.connectors.dcm_street_centerline_arcgis import build_segment_query_url
from app.connectors.mappluto_geometry_arcgis import CRS_STAMP, analyze_lot_geometry
from app.spatial.site_geometry import (
    city_records_from_pluto,
    derive_site_geometry_from_sources,
    lot_outline_from_mappluto,
    street_data_from_pages,
)
from app.spatial.site_geometry.results import STATUS_PARTIAL, STATUS_REFUSED

from ._northern_replay import DCM_ENVELOPE, replay_dcm_page, replay_lot_geometry, replay_pluto


@pytest.fixture(scope="module")
def lot_result():
    return replay_lot_geometry()


@pytest.fixture(scope="module")
def page():
    return replay_dcm_page()


@pytest.fixture(scope="module")
def pluto():
    return replay_pluto()


# --------------------------------------------------------------------------- MapPLUTO outline


def test_recorded_outline_is_adapted_verbatim(lot_result):
    outline, reason = lot_outline_from_mappluto(lot_result)
    assert reason is None
    assert outline.source == "MapPLUTO 26v2 tax-lot"
    assert outline.crs["latest_wkid"] == 2263
    raw_ring = lot_result.features[0]["geometry"]["rings"][0]
    assert [list(p) for p in outline.exterior] == raw_ring
    assert outline.provenance["bbl"] == "4073340070"


def _with_geometry(lot_result, esri):
    assessment = analyze_lot_geometry(esri, crs=dict(CRS_STAMP))
    feature = dict(lot_result.features[0], geometry=esri)
    return replace(lot_result, geometry=assessment, features=[feature])


SQUARE_CW = [[0.0, 0.0], [0.0, 100.0], [100.0, 100.0], [100.0, 0.0], [0.0, 0.0]]
HOLE_CCW = [[25.0, 25.0], [75.0, 25.0], [75.0, 75.0], [25.0, 75.0], [25.0, 25.0]]
OTHER_CW = [[200.0, 0.0], [200.0, 50.0], [250.0, 50.0], [250.0, 0.0], [200.0, 0.0]]


@pytest.mark.parametrize(("change", "fragment"), [
    (lambda r: replace(r, outcome="multiple_features", review_required=True), "review"),
    (lambda r: replace(r, review_required=True), "review"),
    (lambda r: replace(r, geometry=None), "no usable outline"),
    (lambda r: replace(r, geometry=replace(r.geometry, status="invalid_geometry")),
     "not usable (invalid_geometry)"),
    (lambda r: replace(r, geometry=replace(r.geometry, status="repaired",
                                           repairs=[{"method": "shapely_make_valid"}])),
     "changes its shape"),
    (lambda r: _with_geometry(r, {"rings": [SQUARE_CW, HOLE_CCW]}), "has a hole"),
    (lambda r: _with_geometry(r, {"rings": [SQUARE_CW, OTHER_CW]}), "several separate parts"),
], ids=["multiple", "review", "no_geometry", "invalid", "make_valid", "hole", "multipart"])
def test_unusable_outline_is_refused(lot_result, page, pluto, change, fragment):
    changed = change(lot_result)
    outline, reason = lot_outline_from_mappluto(changed)
    assert outline is None and fragment in reason
    result = derive_site_geometry_from_sources(changed, [page], envelope=DCM_ENVELOPE,
                                               pluto_result=pluto)
    assert result.status == STATUS_REFUSED and fragment in result.refusal_reason
    assert result.city_records.lot_area.value == 10075.0


def test_shape_preserving_repair_is_accepted(lot_result):
    repaired = replace(lot_result, geometry=replace(
        lot_result.geometry, status="repaired", repairs=[{"method": "ring_closure"}]))
    outline, reason = lot_outline_from_mappluto(repaired)
    assert reason is None and outline is not None


# --------------------------------------------------------------------------- DCM streets


def test_recorded_street_page_is_adapted(page):
    streets = street_data_from_pages([page], envelope=DCM_ENVELOPE)
    assert streets.incomplete_reasons == ()
    assert streets.crs["latest_wkid"] == 2263
    assert len(streets.centerlines) == 6
    assert all(c.status_ok for c in streets.centerlines)
    keys = sorted({c.street_key for c in streets.centerlines})
    assert keys == ["215 Place", "215 Street", "45 Road", "Northern Boulevard"]


def _page_with_first_entry(page, **segment_changes):
    entry = page.entries[0]
    changed = replace(entry, segment=replace(entry.segment, **segment_changes))
    return replace(page, entries=[changed, *page.entries[1:]])


@pytest.mark.parametrize(("changes", "fragment"), [
    ({"paper_street": "Y"}, "paper_street='Y'"),
    ({"record_street": "Y"}, "record_street='Y'"),
    ({"stair_street": None}, "stair_street=None"),
    ({"feat_type": "Former_St"}, "'Former_St', not a mapped street"),
])
def test_special_street_segments_need_review(page, changes, fragment):
    streets = street_data_from_pages([_page_with_first_entry(page, **changes)],
                                     envelope=DCM_ENVELOPE)
    first = streets.centerlines[0]
    assert first.status_ok is False and fragment in first.status_note


def test_page_not_queried_for_the_stated_area_is_incomplete(page, lot_result):
    by_name = replace(page, request_url=build_segment_query_url(street_name="215 Place"))
    wider = (DCM_ENVELOPE[0] - 50.0, *DCM_ENVELOPE[1:])
    for pages, envelope in (([by_name], DCM_ENVELOPE), ([page], wider)):
        streets = street_data_from_pages(pages, envelope=envelope)
        assert "A street query page was not fetched for the stated area." in \
            streets.incomplete_reasons
    result = derive_site_geometry_from_sources(lot_result, [by_name], envelope=DCM_ENVELOPE)
    assert result.lot_type.kind == "unknown"
    assert "not fetched for the stated area" in result.lot_type.reason


def test_transfer_limited_page_is_incomplete(page, lot_result):
    limited = replace(page, exceeded_transfer_limit=True)
    streets = street_data_from_pages([limited], envelope=DCM_ENVELOPE)
    assert any("transfer limit" in r for r in streets.incomplete_reasons)
    result = derive_site_geometry_from_sources(lot_result, [limited], envelope=DCM_ENVELOPE)
    assert result.status == STATUS_PARTIAL and result.lot_type.kind == "unknown"
    assert all(f.length.value is None for f in result.frontages)


def test_segment_without_geometry_is_incomplete(page):
    entry = page.entries[0]
    broken = replace(entry, status="null_geometry", paths=None, path_count=0, vertex_count=0)
    streets = street_data_from_pages([replace(page, entries=[broken, *page.entries[1:]])],
                                     envelope=DCM_ENVELOPE)
    assert len(streets.centerlines) == 5
    assert any("has no usable geometry" in r for r in streets.incomplete_reasons)


def test_page_in_another_crs_is_not_read(page, lot_result):
    other = replace(page, crs={"wkid": 4326})
    result = derive_site_geometry_from_sources(lot_result, [other], envelope=DCM_ENVELOPE)
    assert result.lot_type.kind == "unknown" and "EPSG:2263" in result.lot_type.reason
    assert result.edges == ()


def test_no_pages_or_no_envelope(lot_result):
    assert street_data_from_pages([], envelope=DCM_ENVELOPE).incomplete_reasons
    result = derive_site_geometry_from_sources(lot_result, None, envelope=None)
    assert result.lot_type.kind == "unknown" and "No city street data" in result.lot_type.reason


# --------------------------------------------------------------------------- PLUTO record


def test_recorded_pluto_values(pluto):
    records = city_records_from_pluto(pluto)
    assert (records.lot_area_sq_ft, records.lot_front_ft, records.lot_depth_ft) == (
        10075.0, 100.76, 100.0)
    assert records.source == "PLUTO 26v2 (64uk-42ks)"
    assert records.provenance["dataset_version"] == "26v2"


def _with_fact(pluto, field, **changes):
    facts = [dict(f, **changes) if f["original_field_name"] == field else f
             for f in pluto.facts]
    return replace(pluto, facts=facts)


@pytest.mark.parametrize("changes", [
    {"normalized_value": 0},
    {"normalized_value": -5},
    {"normalized_value": "10075"},
    {"normalized_value": True},
    {"normalized_value": None},
    {"normalized_value": float("nan")},
    {"units": "feet"},
], ids=["zero", "negative", "text", "bool", "null", "nan", "wrong_unit"])
def test_unusable_pluto_area_is_unknown_never_zero(pluto, changes):
    records = city_records_from_pluto(_with_fact(pluto, "lotarea", **changes))
    assert records.lot_area_sq_ft is None
    assert records.lot_front_ft == 100.76


def test_pluto_no_match_gives_no_values(pluto):
    records = city_records_from_pluto(replace(pluto, status="no_match", facts=[]))
    assert (records.lot_area_sq_ft, records.lot_front_ft, records.lot_depth_ft) == (
        None, None, None)
