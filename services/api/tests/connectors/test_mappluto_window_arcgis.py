"""M5-T154 S1/S2: the MapPLUTO neighbouring-lot WINDOW connector.

Offline replay of the recorded 215-16 Northern window pack through the real connector; no
network. S1 proves the window returns each neighbour once with its BBL and verbatim EPSG:2263
outline, the subject excluded, and the request URL byte-identical to the MANIFEST and free of any
owner-name field. S2 proves a wrong CRS, an ArcGIS error object, a paging fault and a malformed
ring are each refused with the connector's typed error and no partial result.
"""

from __future__ import annotations

from datetime import UTC, datetime
from random import Random

import pytest

from app.connectors import mappluto_window_arcgis as mw
from app.resilience.transport import TransportResponse
from tests.spatial._northern_window_replay import (
    BBL,
    ENV_400,
    WINDOW_LOTS_FILE,
    recorded_url,
    replay_window_lots,
    window_digest,
)
from tests.spatial._northern_window_replay import (
    transport as replay_transport,
)

_CLOCK = datetime(2026, 10, 10, 19, 5, 57, tzinfo=UTC)


def _fetch_with_query_body(query_body: str):
    """Fetch with the real recorded MapPLUTO metadata but a CRAFTED window page."""
    meta_url = mw.build_metadata_url()
    meta_body = replay_transport(meta_url, {}, 30.0).body
    query_url = mw.build_window_query_url(ENV_400)

    def transport(url, headers, timeout):
        if url == meta_url:
            return TransportResponse(200, meta_body)
        if url == query_url:
            return TransportResponse(200, query_body)
        raise AssertionError(f"unexpected url {url}")

    return mw.fetch_window_lots(
        envelope=ENV_400, subject_bbl=BBL, transport=transport, sleep=lambda _s: None,
        clock=lambda: _CLOCK, rng=Random(0), correlation_id="s2")


# ---------------------------------------------------------------------------
# S1 - neighbouring lots in a window
# ---------------------------------------------------------------------------


def test_window_returns_each_neighbour_once_in_2263():
    result = replay_window_lots()
    assert result.status == "ok"
    assert len(result.lots) == 200
    bbls = [lot.bbl for lot in result.lots]
    assert len(set(bbls)) == len(bbls), "each neighbouring lot is returned once"
    assert all(len(b) == 10 and b.isdigit() for b in bbls)
    assert result.crs["latest_wkid"] == 2263
    for lot in result.lots:
        assert lot.outline and all(len(ring) >= 4 for ring in lot.outline)
        assert all(isinstance(x, float) and isinstance(y, float)
                   for ring in lot.outline for x, y in ring)


def test_subject_lot_is_not_among_the_neighbours():
    result = replay_window_lots()
    assert BBL not in [lot.bbl for lot in result.lots]
    assert result.subject is not None and result.subject.bbl == BBL


def test_request_url_is_byte_identical_to_the_manifest():
    built = mw.build_window_query_url(ENV_400)
    assert built == recorded_url(WINDOW_LOTS_FILE)
    result = replay_window_lots()
    assert result.request_urls[0] == recorded_url(WINDOW_LOTS_FILE)
    assert result.raw_digests[0] == window_digest(WINDOW_LOTS_FILE)


def test_request_never_asks_for_an_owner_name():
    """MUTATION PROOF 1: adding the owner-name field to the request changes the
    out-field set and the byte-exact URL, so this test fails. No personal field
    is ever requested or stored."""
    assert "OwnerName" not in mw.OUT_FIELDS
    assert not any("owner" in field.lower() for field in mw.OUT_FIELDS)
    url = mw.build_window_query_url(ENV_400)
    assert "OwnerName" not in url and "Owner" not in url
    # the out-field set is exactly the six identity/outline fields, nothing more
    assert set(mw.OUT_FIELDS) == {"OBJECTID", "BBL", "Block", "Lot", "Address", "Version"}
    # and no returned lot object carries an owner attribute
    for lot in replay_window_lots().lots:
        assert not hasattr(lot, "owner_name")


# ---------------------------------------------------------------------------
# S2 - the connector refuses bad answers (typed error, no partial result)
# ---------------------------------------------------------------------------

_GOOD_SR = '"spatialReference":{"wkid":102718,"latestWkid":2263}'


def test_wrong_crs_is_refused():
    body = ('{"geometryType":"esriGeometryPolygon",'
            '"spatialReference":{"wkid":4326,"latestWkid":4326},'
            '"features":[{"attributes":{"OBJECTID":1,"BBL":4073340001},'
            '"geometry":{"rings":[[[0,0],[1,0],[1,1],[0,0]]]}}]}')
    with pytest.raises(mw.WrongCRSError):
        _fetch_with_query_body(body)


def test_arcgis_error_object_is_refused():
    body = '{"error":{"code":400,"message":"Invalid or missing input parameters."}}'
    with pytest.raises(mw.UpstreamError):
        _fetch_with_query_body(body)


def test_paging_fault_is_refused():
    body = ('{"geometryType":"esriGeometryPolygon",' + _GOOD_SR
            + ',"features":[],"exceededTransferLimit":true}')
    with pytest.raises(mw.PagingPathologyError):
        _fetch_with_query_body(body)


def test_malformed_ring_is_refused_whole():
    body = ('{"geometryType":"esriGeometryPolygon",' + _GOOD_SR
            + ',"features":[{"attributes":{"OBJECTID":5,"BBL":4073340002},'
            '"geometry":{"rings":[[[0,0],[1,0],["x","y"],[0,0]]]}}]}')
    with pytest.raises(mw.MalformedGeometryError):
        _fetch_with_query_body(body)
