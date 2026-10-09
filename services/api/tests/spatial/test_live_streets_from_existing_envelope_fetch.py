"""Live single-lot street data composed from the EXISTING envelope fetch (D-090-R124, Lane B).

Proves that :func:`app.spatial.site_geometry.street_data_for_lot` turns a lot outline into the
same ``StreetData`` the accepted adapter produces, by REUSING the accepted connector stack:
the query URL it builds is byte-identical to the recorded benchmark request, and feeding the
result into ``derive_site_geometry`` yields the SAME ``SiteGeometry`` as the pinned 215-16
Northern benchmark (corner lot; 215 Place / Northern Boulevard frontages). Offline: the fake
fetch serves the recorded pack bytes back through the accepted paged fetch; no network.

Expectations are IMPORTED, never restated: the reference ``SiteGeometry`` is built with the
accepted ``derive_site_geometry_from_sources`` on the same recorded pack, and the street names
come from the benchmark module.
"""

from __future__ import annotations

import json

import pytest

from app.connectors.dcm_street_centerline_arcgis import (
    DcmTransport,
    WrongCRSError,
    build_metadata_url,
    build_segment_query_url,
)
from app.spatial.site_geometry import (
    LotOutline,
    UnusableLotOutlineError,
    city_records_from_pluto,
    derive_site_geometry,
    derive_site_geometry_from_sources,
    lot_outline_from_mappluto,
    street_data_for_lot,
    street_data_from_pages,
    street_envelope_for_lot,
)
from app.spatial.site_geometry.parameters import SEARCH_RADIUS_FT
from app.spatial.site_geometry.results import (
    FRONTAGE_CONFIRMED,
    LOT_TYPE_CORNER,
    STATUS_REFUSED,
)

from ._northern_replay import (
    DCM_ENVELOPE,
    DCM_FILE,
    MANIFEST,
    PACK,
    recorded_dcm_envelope_page,
    replay_dcm_page,
    replay_lot_geometry,
    replay_pluto,
)
from .test_site_geometry_benchmark_215_16_northern import NORTHERN, PLACE

_META_FILE = "dcm_layer_metadata.json"
_CID = "live-streets-test"


def _lot() -> LotOutline:
    lot, refusal = lot_outline_from_mappluto(replay_lot_geometry())
    assert lot is not None, refusal
    return lot


def _pack_transport(name: str) -> DcmTransport:
    entry = MANIFEST[name]
    body = (PACK / name).read_bytes().decode("utf-8")
    return DcmTransport(url=entry["url"], status=200, body=body,
                        retrieved_at=entry["retrieved_at"])


def _recorded_fetch(url: str, correlation_id: str) -> DcmTransport:
    """Serve the recorded DCM metadata + envelope-page bytes by URL -- the accepted paged
    fetch calls this exactly as it would ``default_fetch``, fully offline."""
    for name in (_META_FILE, DCM_FILE):
        transport = _pack_transport(name)
        if url == transport.url:
            return transport
    raise AssertionError(f"the code fetched an unexpected URL: {url}")


# --------------------------------------------------------------------------- envelope / URL


def test_street_envelope_for_lot_matches_the_recorded_envelope_values():
    assert street_envelope_for_lot(_lot()) == DCM_ENVELOPE
    assert SEARCH_RADIUS_FT == 150.0


def test_a_custom_buffer_pads_the_canonical_lot_bounds():
    lot = _lot()
    bare = street_envelope_for_lot(lot, buffer_ft=0.0)
    padded = street_envelope_for_lot(lot, buffer_ft=10.0)
    assert padded == (bare[0] - 10.0, bare[1] - 10.0, bare[2] + 10.0, bare[3] + 10.0)
    # buffer_ft defaults to SEARCH_RADIUS_FT, so the default is the recorded 150-ft envelope.
    assert street_envelope_for_lot(lot) == street_envelope_for_lot(lot, buffer_ft=SEARCH_RADIUS_FT)
    assert bare == pytest.approx((DCM_ENVELOPE[0] + 150.0, DCM_ENVELOPE[1] + 150.0,
                                  DCM_ENVELOPE[2] - 150.0, DCM_ENVELOPE[3] - 150.0))


def test_the_built_query_url_is_byte_identical_to_the_recorded_request():
    built = build_segment_query_url(envelope=street_envelope_for_lot(_lot()))
    recorded_url, _body, _retrieved = recorded_dcm_envelope_page()
    assert built == recorded_url
    assert built == MANIFEST[DCM_FILE]["url"]


# --------------------------------------------------------------------------- composition


def test_street_data_for_lot_equals_the_accepted_adapter_path():
    mine = street_data_for_lot(_lot(), correlation_id=_CID, fetch=_recorded_fetch)
    reference = street_data_from_pages([replay_dcm_page()], envelope=DCM_ENVELOPE)
    assert mine == reference


def test_composition_yields_the_same_site_geometry_as_the_benchmark():
    lot = _lot()
    streets = street_data_for_lot(lot, correlation_id=_CID, fetch=_recorded_fetch)
    mine = derive_site_geometry(lot, streets, city_records_from_pluto(replay_pluto()))
    reference = derive_site_geometry_from_sources(
        replay_lot_geometry(), [replay_dcm_page()], envelope=DCM_ENVELOPE,
        pluto_result=replay_pluto())

    # Same SiteGeometry as the accepted path (lot type, frontages, area, depth, provenance).
    assert mine == reference
    # The material facts the task names, asserted explicitly against the imported reference.
    assert mine.lot_type.kind == reference.lot_type.kind == LOT_TYPE_CORNER
    for street in (PLACE, NORTHERN):
        got, want = mine.frontage(street), reference.frontage(street)
        assert got is not None
        assert got.status == want.status == FRONTAGE_CONFIRMED
        assert got.length.value == want.length.value
        assert got.segment_object_ids == want.segment_object_ids


def test_composition_also_derives_corner_and_frontages_without_city_records():
    # derive_site_geometry with replay_lot_geometry()'s outline alone (the task's phrasing).
    lot = _lot()
    streets = street_data_for_lot(lot, correlation_id=_CID, fetch=_recorded_fetch)
    geometry = derive_site_geometry(lot, streets)
    assert geometry.lot_type.kind == LOT_TYPE_CORNER
    assert geometry.lot_type.streets == (PLACE, NORTHERN)
    for street in (PLACE, NORTHERN):
        assert geometry.frontage(street).status == FRONTAGE_CONFIRMED


# --------------------------------------------------------------------------- fail closed


def test_unusable_non_2263_outline_fails_closed_to_the_refusal_path():
    display_outline = LotOutline(
        _lot().exterior, {"wkid": 4326, "latest_wkid": 4326}, "MapPLUTO display outline")
    with pytest.raises(UnusableLotOutlineError):
        street_envelope_for_lot(display_outline)
    with pytest.raises(UnusableLotOutlineError):
        street_data_for_lot(display_outline, correlation_id=_CID, fetch=_recorded_fetch)
    # The caller routes that typed error to refused_site_geometry (the same outline gate).
    assert derive_site_geometry(display_outline, None).status == STATUS_REFUSED


def test_an_invalid_buffer_fails_closed():
    for bad in (-1.0, float("nan"), float("inf"), True):
        with pytest.raises(UnusableLotOutlineError):
            street_envelope_for_lot(_lot(), buffer_ft=bad)


def test_a_non_2263_geometry_page_is_refused_by_the_accepted_parser():
    url, body, retrieved = recorded_dcm_envelope_page()
    doc = json.loads(body)
    doc["spatialReference"] = {"wkid": 4326, "latestWkid": 4326}
    tampered = json.dumps(doc)

    def fetch(fetch_url: str, correlation_id: str) -> DcmTransport:
        if fetch_url == build_metadata_url():
            return _pack_transport(_META_FILE)
        assert fetch_url == url
        return DcmTransport(url=url, status=200, body=tampered, retrieved_at=retrieved)

    with pytest.raises(WrongCRSError):
        street_data_for_lot(_lot(), correlation_id=_CID, fetch=fetch)
