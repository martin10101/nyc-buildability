"""Acceptance pack for POST /api/v1/outline-bridge (task M5-T065, D-082-R001).

Fully OFFLINE and deterministic. The route is UNMOUNTED in this slice, so every route test
mounts the router in a LOCAL FastAPI app via TestClient and injects the two source-ring seams
through ``app.dependency_overrides`` (no network, no connector call). The route is ALSO
feature-flag gated OFF by default (reuses ``INTERNAL_RULE_EVAL_ENABLED``).

Three test layers cover the three module responsibilities separately:

  * CORRESPONDENCE math (``fit_correspondence`` unit tests): residual is necessary but NOT
    sufficient. A wrong index alignment on a cyclically-shifted ring is recovered correctly;
    a SYMMETRIC parcel produces several equally-good alignments (low residual, NOT unique) and
    is reported as ambiguous; a triangle (3 control points) fits every alignment perfectly and
    is refused (too_few_control_points); mismatched / over-cap / collinear rings raise typed
    reasons. This directly demonstrates that a low-residual fit that is ambiguous or wrong is
    never silently trusted.
  * HTTP handling (route tests): typed, DISTINCT refusals per the (status, state) matrix; an
    ambiguous correspondence emits NO coordinates; correspondence provenance surfaces the chosen
    alignment (winding + offset), the residual, and the margin over the runner-up alignment.
  * CONNECTOR I/O adapters (offline adapter tests): the two production ring providers translate
    the ACCEPTED connector outputs into ParcelRings - source identity, CRS, MULTIPART handling,
    and the typed RingUnavailable faults - verified against the real connector contract types.
"""

from __future__ import annotations

import math

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.outline_bridge import (
    BRIDGE_AMBIGUITY_SEPARATION_FT,
    BRIDGE_MAX_CONTROL_POINTS,
    BRIDGE_MAX_DRAWN_VERTICES,
    BRIDGE_MAX_RMS_RESIDUAL_FT,
    OUTLINE_BRIDGE_STATUS_STATE_MATRIX,
    ParcelRing,
    RingUnavailable,
    _CorrespondenceError,
    _default_authoritative_ring,
    _default_display_ring,
    fit_correspondence,
    get_authoritative_ring_provider,
    get_display_ring_provider,
    router,
)
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR

_URL = "/api/v1/outline-bridge"
_BBL = "1000010010"

# An IRREGULAR quad in "4326" (lng/lat-scale) and its EXACT affine image in 2263 feet:
#   X = 1_000_000 + (u + 74.0) * 1e5 ;  Y = 200_000 + (v - 40.7) * 1e5
# Deliberately asymmetric (no affine self-symmetry) so the forward offset-0 index alignment is
# UNIQUELY the best one and every other alignment leaves a residual far above the ambiguity gap.
# (A symmetric quad — e.g. a kite about a diagonal — admits a SECOND zero-residual alignment and
# is correctly refused as ambiguous; that case is exercised separately by the square fixtures.)
_DISPLAY_PTS = (
    (-74.0, 40.7),
    (-73.99863, 40.70012),
    (-73.99899, 40.70088),
    (-73.9998, 40.70041),
)
_AUTH_PTS = (
    (1_000_000.0, 200_000.0),
    (1_000_137.0, 200_012.0),
    (1_000_101.0, 200_088.0),
    (1_000_020.0, 200_041.0),
)
# Drawn vertices INSIDE the display neighborhood, and their exact 2263 images under the transform.
_DRAWN = [[-73.9998, 40.7001], [-73.9992, 40.7001], [-73.9992, 40.7003]]
_DRAWN_2263 = [(1_000_020.0, 200_010.0), (1_000_080.0, 200_010.0), (1_000_080.0, 200_030.0)]
# A generic valid drawn triangle for tests where the bridge math is not exercised.
_TRI = [[-74.0, 40.7], [-73.99, 40.7], [-73.99, 40.71]]

# A SYMMETRIC square (4326) and its exact 2263 image (a 100x100 ft square). Every 90-degree
# rotation and reflection maps the square onto itself, so several index alignments fit with a
# ~0 residual yet map interior points to DIFFERENT places -> genuinely ambiguous.
_SQUARE_4326 = ((-74.0, 40.70), (-73.999, 40.70), (-73.999, 40.701), (-74.0, 40.701))
_SQUARE_2263 = (
    (1_000_000.0, 200_000.0),
    (1_000_100.0, 200_000.0),
    (1_000_100.0, 200_100.0),
    (1_000_000.0, 200_100.0),
)
# A drawn (asymmetric) shape inside the square neighborhood.
_SQUARE_DRAWN = [[-73.9997, 40.7003], [-73.9995, 40.7003], [-73.9996, 40.7007]]

# A triangle ring pair (3 control points): every alignment fits EXACTLY, so the correspondence
# cannot be established from residual and is refused.
_TRI_4326 = ((-74.0, 40.70), (-73.999, 40.70), (-73.9995, 40.701))
_TRI_2263 = ((1_000_000.0, 200_000.0), (1_000_100.0, 200_000.0), (1_000_050.0, 200_100.0))


def _pr(points, crs: str, source_id: str = "s", detail: dict | None = None) -> ParcelRing:
    return ParcelRing(
        points=tuple(points), crs=crs, source_id=source_id, source_detail=detail or {}
    )


def _display_ring(points=_DISPLAY_PTS) -> ParcelRing:
    return ParcelRing(
        points=tuple(points),
        crs="EPSG:4326",
        source_id="nyc-dcp-mappluto-lot-outline",
        source_detail={"outcome": "single_lot", "representation": "lot_outline_display"},
    )


def _auth_ring(points=_AUTH_PTS) -> ParcelRing:
    return ParcelRing(
        points=tuple(points),
        crs="EPSG:2263",
        source_id="nyc-dcp-mappluto-arcgis",
        source_detail={"outcome": "single_feature", "representation": "lot_geometry_authoritative"},
    )


def _build_app(display, auth) -> FastAPI:
    """A local app with the router mounted and both ring seams overridden. A ParcelRing is
    returned; an Exception instance is raised by the seam (fault injection)."""
    app = FastAPI()
    app.include_router(router)

    def _seam(value):
        def provider(_bbl: str, _cid: str):
            if isinstance(value, Exception):
                raise value
            return value

        return lambda: provider

    app.dependency_overrides[get_display_ring_provider] = _seam(display)
    app.dependency_overrides[get_authoritative_ring_provider] = _seam(auth)
    return app


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")

    def _make(display=None, auth=None):
        app = _build_app(
            display if display is not None else _display_ring(),
            auth if auth is not None else _auth_ring(),
        )
        return TestClient(app, raise_server_exceptions=False)

    return _make


# ---------------------------------------------------------------------------
# Correspondence math (unit) — residual is necessary but NOT sufficient.
# ---------------------------------------------------------------------------
def test_fit_correspondence_recovers_unique_forward_alignment():
    corr = fit_correspondence(_pr(_DISPLAY_PTS, "EPSG:4326"), _pr(_AUTH_PTS, "EPSG:2263"))
    assert corr.fit.winding == "forward"
    assert corr.fit.offset == 0
    assert corr.fit.rms_residual == pytest.approx(0.0, abs=1e-3)
    # A non-symmetric quad: the correct alignment beats every other by a wide margin.
    assert corr.separation >= BRIDGE_AMBIGUITY_SEPARATION_FT
    assert corr.candidates_evaluated >= 2


def test_fit_correspondence_recovers_cyclically_shifted_ring():
    # The authoritative ring starts one vertex later (the two official layers need not agree on
    # a start vertex). The search recovers the correct cyclic offset and the SAME transform.
    shifted = _AUTH_PTS[1:] + _AUTH_PTS[:1]
    corr = fit_correspondence(_pr(_DISPLAY_PTS, "EPSG:4326"), _pr(shifted, "EPSG:2263"))
    assert corr.fit.winding == "forward"
    assert corr.fit.offset == 3  # rotating the shifted ring back by 3 restores the true order
    assert corr.fit.rms_residual == pytest.approx(0.0, abs=1e-3)
    assert corr.separation >= BRIDGE_AMBIGUITY_SEPARATION_FT


def test_fit_correspondence_recovers_reversed_winding():
    corr = fit_correspondence(
        _pr(_DISPLAY_PTS, "EPSG:4326"), _pr(tuple(reversed(_AUTH_PTS)), "EPSG:2263")
    )
    assert corr.fit.winding == "reversed"
    assert corr.fit.rms_residual == pytest.approx(0.0, abs=1e-3)
    assert corr.separation >= BRIDGE_AMBIGUITY_SEPARATION_FT


def test_fit_correspondence_symmetric_square_is_low_residual_but_ambiguous():
    # THE central proof: the best fit residual is ~0 (a perfect fit exists) yet the
    # correspondence is NOT unique — several 90-degree rotations fit equally well. Residual
    # alone would "accept"; the separation exposes the ambiguity.
    corr = fit_correspondence(_pr(_SQUARE_4326, "EPSG:4326"), _pr(_SQUARE_2263, "EPSG:2263"))
    assert corr.fit.rms_residual == pytest.approx(0.0, abs=1e-3)
    assert corr.separation < BRIDGE_AMBIGUITY_SEPARATION_FT


def test_fit_correspondence_triangle_refuses_too_few_control_points():
    with pytest.raises(_CorrespondenceError) as exc:
        fit_correspondence(_pr(_TRI_4326, "EPSG:4326"), _pr(_TRI_2263, "EPSG:2263"))
    assert exc.value.reason == "too_few_control_points"


def test_fit_correspondence_refuses_too_many_control_points():
    n = BRIDGE_MAX_CONTROL_POINTS + 1
    big_4326 = tuple(
        (
            -74.0 + 0.001 * math.cos(2 * math.pi * k / n),
            40.7 + 0.001 * math.sin(2 * math.pi * k / n),
        )
        for k in range(n)
    )
    big_2263 = tuple(
        (
            1_000_000.0 + 100 * math.cos(2 * math.pi * k / n),
            200_000.0 + 100 * math.sin(2 * math.pi * k / n),
        )
        for k in range(n)
    )
    with pytest.raises(_CorrespondenceError) as exc:
        fit_correspondence(_pr(big_4326, "EPSG:4326"), _pr(big_2263, "EPSG:2263"))
    assert exc.value.reason == "too_many_control_points"


def test_fit_correspondence_vertex_count_mismatch():
    with pytest.raises(_CorrespondenceError) as exc:
        fit_correspondence(
            _pr(_DISPLAY_PTS, "EPSG:4326"),
            _pr(_AUTH_PTS + ((1_000_050.0, 200_050.0),), "EPSG:2263"),
        )
    assert exc.value.reason == "vertex_count_mismatch"


def test_fit_correspondence_collinear_control_points_is_degenerate():
    col_4326 = ((-74.0, 40.7), (-73.999, 40.7), (-73.998, 40.7), (-73.997, 40.7))
    col_2263 = (
        (1_000_000.0, 200_000.0),
        (1_000_100.0, 200_000.0),
        (1_000_200.0, 200_000.0),
        (1_000_300.0, 200_000.0),
    )
    with pytest.raises(_CorrespondenceError) as exc:
        fit_correspondence(_pr(col_4326, "EPSG:4326"), _pr(col_2263, "EPSG:2263"))
    assert exc.value.reason == "degenerate_control_points"


# ---------------------------------------------------------------------------
# AS-2 / AS-3 — the happy path: correspondence honesty + sub-inch residual.
# ---------------------------------------------------------------------------
def test_bridges_drawn_outline_to_2263_with_correspondence_provenance(client):
    resp = client().post(_URL, json={"bbl": _BBL, "drawn_vertices": _DRAWN})
    assert resp.status_code == 200
    body = resp.json()
    assert body["document_kind"] == "outline_bridge"
    assert body["srid"] == 2263
    assert body["bbl"] == _BBL
    # The drawn 4326 vertices map through the recovered affine to their exact 2263 images.
    got = [(v["x"], v["y"]) for v in body["vertices"]]
    for (gx, gy), (ex, ey) in zip(got, _DRAWN_2263, strict=True):
        assert gx == pytest.approx(ex, abs=1e-3)
        assert gy == pytest.approx(ey, abs=1e-3)
    corr = body["correspondence"]
    assert corr["method"] == "affine_least_squares_2d"
    assert corr["alignment"] == "forward+offset0"
    assert corr["alignment_winding"] == "forward"
    assert corr["alignment_offset"] == 0
    assert corr["control_point_count"] == 4
    assert corr["candidates_evaluated"] >= 2
    assert corr["rms_residual_ft"] == pytest.approx(0.0, abs=1e-3)
    assert corr["residual_bound_ft"] == BRIDGE_MAX_RMS_RESIDUAL_FT
    # The uniqueness evidence is disclosed: a clear margin over the runner-up alignment.
    assert corr["alignment_separation_min_ft"] == BRIDGE_AMBIGUITY_SEPARATION_FT
    assert corr["alignment_separation_ft"] >= BRIDGE_AMBIGUITY_SEPARATION_FT
    assert corr["runner_up_rms_residual_ft"] is None or corr["runner_up_rms_residual_ft"] > 0
    assert corr["source_display_ring"]["source_id"] == "nyc-dcp-mappluto-lot-outline"
    assert corr["source_display_ring"]["crs"] == "EPSG:4326"
    assert corr["source_display_ring"]["representation"] == "lot_outline_display"
    assert corr["source_authoritative_ring"]["source_id"] == "nyc-dcp-mappluto-arcgis"
    assert corr["source_authoritative_ring"]["crs"] == "EPSG:2263"
    assert corr["source_authoritative_ring"]["representation"] == "lot_geometry_authoritative"
    assert "not a survey" in body["disclosure"] and "not a city record" in body["disclosure"]
    assert "low residual alone does not" in body["disclosure"]
    assert resp.headers["X-Correlation-ID"]


def test_picks_the_reversed_alignment_when_windings_differ(client):
    # Same parcel, authoritative ring wound the OTHER way -> the reversed alignment fits.
    resp = client(auth=_auth_ring(tuple(reversed(_AUTH_PTS)))).post(
        _URL, json={"bbl": _BBL, "drawn_vertices": _DRAWN}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["correspondence"]["alignment_winding"] == "reversed"
    # The reversed same-parcel ring bridges to the SAME 2263 images.
    got = [(v["x"], v["y"]) for v in body["vertices"]]
    for (gx, gy), (ex, ey) in zip(got, _DRAWN_2263, strict=True):
        assert gx == pytest.approx(ex, abs=1e-3)
        assert gy == pytest.approx(ey, abs=1e-3)


def test_cyclically_shifted_authoritative_ring_bridges_correctly(client):
    # The two official layers start at different vertices; the drawn shape still bridges to the
    # correct 2263 coordinates and the chosen offset is disclosed.
    shifted = _AUTH_PTS[1:] + _AUTH_PTS[:1]
    resp = client(auth=_auth_ring(shifted)).post(_URL, json={"bbl": _BBL, "drawn_vertices": _DRAWN})
    assert resp.status_code == 200
    body = resp.json()
    assert body["correspondence"]["alignment_winding"] == "forward"
    assert body["correspondence"]["alignment_offset"] == 3
    got = [(v["x"], v["y"]) for v in body["vertices"]]
    for (gx, gy), (ex, ey) in zip(got, _DRAWN_2263, strict=True):
        assert gx == pytest.approx(ex, abs=1e-3)
        assert gy == pytest.approx(ey, abs=1e-3)


# ---------------------------------------------------------------------------
# Typed, DISTINCT refusals (AS-5 server side). An ambiguous or incorrect
# low-residual fit is REFUSED and emits NO coordinates.
# ---------------------------------------------------------------------------
def test_symmetric_parcel_refuses_ambiguous_and_emits_no_coordinates(client):
    resp = client(display=_display_ring(_SQUARE_4326), auth=_auth_ring(_SQUARE_2263)).post(
        _URL, json={"bbl": _BBL, "drawn_vertices": _SQUARE_DRAWN}
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["state"] == "correspondence_unavailable"
    assert body["reason"] == "ambiguous_correspondence"
    # The fit residual was low, but no bridged coordinates were produced.
    assert "vertices" not in body


def test_triangle_rings_refuse_too_few_control_points_and_emit_no_coordinates(client):
    resp = client(display=_display_ring(_TRI_4326), auth=_auth_ring(_TRI_2263)).post(
        _URL, json={"bbl": _BBL, "drawn_vertices": _SQUARE_DRAWN}
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["state"] == "correspondence_unavailable"
    assert body["reason"] == "too_few_control_points"
    assert "vertices" not in body


def test_residual_over_bound_refuses_typed(client):
    # A ring pair with equal counts but NO affine relationship -> large residual, refused.
    display = _display_ring(((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)))
    auth = _auth_ring(((0.0, 0.0), (100.0, 0.0), (200.0, 200.0), (0.0, 100.0)))
    resp = client(display=display, auth=auth).post(
        _URL, json={"bbl": _BBL, "drawn_vertices": [[0.2, 0.2], [0.8, 0.2], [0.8, 0.8]]}
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["state"] == "residual_too_high"
    assert body["rms_residual_ft"] > BRIDGE_MAX_RMS_RESIDUAL_FT
    assert body["residual_bound_ft"] == BRIDGE_MAX_RMS_RESIDUAL_FT
    assert "vertices" not in body


def test_out_of_neighborhood_vertex_refuses_distinctly(client):
    # Good rings, but one drawn vertex is far from the lot -> DISTINCT from a residual refusal.
    drawn = [[-73.9998, 40.7001], [-73.9992, 40.7001], [-70.0, 45.0]]
    resp = client().post(_URL, json={"bbl": _BBL, "drawn_vertices": drawn})
    assert resp.status_code == 422
    assert resp.json()["state"] == "out_of_neighborhood"


def test_vertex_count_mismatch_is_correspondence_unavailable(client):
    auth = _auth_ring(_AUTH_PTS + ((1_000_050.0, 200_050.0),))
    resp = client(auth=auth).post(_URL, json={"bbl": _BBL, "drawn_vertices": _DRAWN})
    assert resp.status_code == 422
    body = resp.json()
    assert body["state"] == "correspondence_unavailable"
    assert body["reason"] == "vertex_count_mismatch"


def test_collinear_control_points_is_correspondence_unavailable(client):
    display = _display_ring(((-74.0, 40.7), (-73.999, 40.7), (-73.998, 40.7), (-73.997, 40.7)))
    auth = _auth_ring(
        (
            (1_000_000.0, 200_000.0),
            (1_000_100.0, 200_000.0),
            (1_000_200.0, 200_000.0),
            (1_000_300.0, 200_000.0),
        )
    )
    drawn = [[-73.9995, 40.7], [-73.999, 40.7], [-73.9985, 40.7]]
    resp = client(display=display, auth=auth).post(
        _URL, json={"bbl": _BBL, "drawn_vertices": drawn}
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["state"] == "correspondence_unavailable"
    assert body["reason"] == "degenerate_control_points"


@pytest.mark.parametrize(
    "drawn, reason",
    [
        ([[-73.9998, 40.7001], [-73.9992, 40.7001]], "too_few_vertices"),
        ([[-73.9998, 40.7001], [-73.9992, 40.7001], [None, 40.7]], "vertex_non_finite"),
        ([[-73.9998, 40.7001], [-73.9992, 40.7001], "nope"], "vertex_non_finite"),
    ],
)
def test_invalid_drawn_vertices_refuse_with_reason(client, drawn, reason):
    resp = client().post(_URL, json={"bbl": _BBL, "drawn_vertices": drawn})
    assert resp.status_code == 422
    body = resp.json()
    assert body["state"] == "invalid_request"
    assert body["reason"] == reason


def test_over_cap_drawn_vertices_refuse(client):
    drawn = [[-74.0 + i * 1e-9, 40.7] for i in range(BRIDGE_MAX_DRAWN_VERTICES + 1)]
    resp = client().post(_URL, json={"bbl": _BBL, "drawn_vertices": drawn})
    assert resp.status_code == 422
    body = resp.json()
    assert body["state"] == "invalid_request"
    assert body["reason"] == "over_cap"


def test_bad_bbl_and_bad_srid_refuse(client):
    bad_bbl = client().post(_URL, json={"bbl": "not-a-bbl", "drawn_vertices": _TRI})
    assert bad_bbl.status_code == 422 and bad_bbl.json()["reason"] == "bbl_invalid"
    bad_srid = client().post(_URL, json={"bbl": _BBL, "srid": 2263, "drawn_vertices": _TRI})
    assert bad_srid.status_code == 422 and bad_srid.json()["reason"] == "srid_unsupported"


def test_malformed_body_refuses(client):
    resp = client().post(_URL, content=b"{not json", headers={"content-type": "application/json"})
    assert resp.status_code == 422
    assert resp.json()["reason"] == "not_json"


def test_connector_fault_is_source_unavailable(client):
    fault = RingUnavailable("upstream down", source_id="nyc-dcp-mappluto-lot-outline")
    resp = client(display=fault).post(_URL, json={"bbl": _BBL, "drawn_vertices": _DRAWN})
    assert resp.status_code == 502
    body = resp.json()
    assert body["state"] == "source_unavailable"
    assert body["source_id"] == "nyc-dcp-mappluto-lot-outline"


def test_oversized_body_is_payload_too_large(client):
    resp = client().post(
        _URL, json={"bbl": _BBL, "drawn_vertices": _DRAWN, "pad": "x" * 300_000}
    )
    assert resp.status_code == 413
    assert resp.json()["state"] == "payload_too_large"


# ---------------------------------------------------------------------------
# Posture proofs: flag-off sentinel, UNMOUNTED, documented matrix.
# ---------------------------------------------------------------------------
def test_flag_off_returns_generic_404(monkeypatch):
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    app = _build_app(_display_ring(), _auth_ring())
    with TestClient(app, raise_server_exceptions=False) as tc:
        resp = tc.post(_URL, json={"bbl": _BBL, "drawn_vertices": _TRI})
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in resp.headers


def test_router_is_not_mounted_on_the_real_app():
    # UNMOUNTED (main.py untouched): the production app carries no outline-bridge route.
    from app.main import app as real_app

    paths = {getattr(r, "path", None) for r in real_app.routes}
    assert _URL not in paths


def test_documented_status_state_matrix():
    assert (200, None) in OUTLINE_BRIDGE_STATUS_STATE_MATRIX
    assert (404, None) in OUTLINE_BRIDGE_STATUS_STATE_MATRIX
    assert (422, "residual_too_high") in OUTLINE_BRIDGE_STATUS_STATE_MATRIX
    assert (422, "out_of_neighborhood") in OUTLINE_BRIDGE_STATUS_STATE_MATRIX
    assert (422, "correspondence_unavailable") in OUTLINE_BRIDGE_STATUS_STATE_MATRIX
    assert (502, "source_unavailable") in OUTLINE_BRIDGE_STATUS_STATE_MATRIX


# ---------------------------------------------------------------------------
# Offline production-adapter tests. These exercise the DEFAULT ring providers
# against the real accepted connector contracts (no network). The MapPLUTO
# geometry connector imports shapely, and the lot-outline connector imports it
# transitively, so both groups importorskip it (they RUN in CI where it is
# installed; they SKIP on a thin-client without it).
# ---------------------------------------------------------------------------
def _polygon_4326(coords):
    return {"type": "Polygon", "coordinates": [coords]}


def test_default_display_ring_single_lot_polygon(monkeypatch):
    lo = pytest.importorskip("app.connectors.mappluto_lot_outline")
    ring_coords = [
        [-74.0, 40.7], [-73.999, 40.7], [-73.999, 40.701], [-74.0, 40.701], [-74.0, 40.7]
    ]

    def fake(bbl, *, correlation_id=None):
        return {
            "outcome": "single_lot",
            "geometry": _polygon_4326(ring_coords),
            "source": {"dataset_version": "25v1.1"},
        }

    monkeypatch.setattr(lo, "build_lot_outline", fake)
    ring = _default_display_ring(_BBL, "cid")
    assert ring.crs == "EPSG:4326"
    assert ring.source_id == lo.SOURCE_ID  # the honest (shared) official source identity
    assert ring.source_detail["representation"] == "lot_outline_display"
    assert ring.source_detail["dataset_version"] == "25v1.1"
    assert len(ring.points) == 4  # the duplicate closing vertex is dropped
    assert ring.points[0] == (-74.0, 40.7)


def test_default_display_ring_multipolygon_uses_first_polygon(monkeypatch):
    # MULTIPART behavior (e.g. a condo merged outline): the first polygon's exterior ring is used.
    lo = pytest.importorskip("app.connectors.mappluto_lot_outline")
    poly_a = [[-74.0, 40.7], [-73.999, 40.7], [-73.999, 40.701], [-74.0, 40.701]]
    poly_b = [[-75.0, 41.0], [-74.999, 41.0], [-74.999, 41.001], [-75.0, 41.001]]

    def fake(bbl, *, correlation_id=None):
        return {
            "outcome": "single_lot",
            "geometry": {"type": "MultiPolygon", "coordinates": [[poly_a], [poly_b]]},
            "source": {"dataset_version": "25v1.1"},
        }

    monkeypatch.setattr(lo, "build_lot_outline", fake)
    ring = _default_display_ring(_BBL, "cid")
    assert ring.points[0] == (-74.0, 40.7)  # from the FIRST polygon
    assert len(ring.points) == 4


def test_default_display_ring_non_single_outcome_is_ring_unavailable(monkeypatch):
    lo = pytest.importorskip("app.connectors.mappluto_lot_outline")

    def fake(bbl, *, correlation_id=None):
        return {"outcome": "multiple_features", "geometry": None, "source": {}}

    monkeypatch.setattr(lo, "build_lot_outline", fake)
    with pytest.raises(RingUnavailable) as exc:
        _default_display_ring(_BBL, "cid")
    assert exc.value.source_id == lo.SOURCE_ID


def test_default_display_ring_connector_fault_is_ring_unavailable(monkeypatch):
    lo = pytest.importorskip("app.connectors.mappluto_lot_outline")

    def boom(bbl, *, correlation_id=None):
        raise lo.LotOutlineError("upstream down", correlation_id="cid")

    monkeypatch.setattr(lo, "build_lot_outline", boom)
    with pytest.raises(RingUnavailable) as exc:
        _default_display_ring(_BBL, "cid")
    assert exc.value.source_id == lo.SOURCE_ID


def test_default_display_ring_unusable_geometry_is_ring_unavailable(monkeypatch):
    lo = pytest.importorskip("app.connectors.mappluto_lot_outline")

    def fake(bbl, *, correlation_id=None):
        return {
            "outcome": "single_lot",
            "geometry": {"type": "Point", "coordinates": [0, 0]},
            "source": {},
        }

    monkeypatch.setattr(lo, "build_lot_outline", fake)
    with pytest.raises(RingUnavailable):
        _default_display_ring(_BBL, "cid")


def _make_assessment(mpg, canonical_geometry, normalized_digest="sha256:auth"):
    return mpg.GeometryAssessment(
        status="valid",
        geometry_kind="polygon",
        findings=[],
        repairs=[],
        original_geometry_digest="sha256:orig",
        normalized_digest=normalized_digest,
        canonical_geometry=canonical_geometry,
        exterior_ring_count=1,
        hole_count=0,
        vertex_count=4,
        area_sq_ft=5000.0,
        area_crs={},
        shapely_version="2.0.7",
        geos_version="3.11.4",
    )


def _make_result(mpg, outcome, geometry):
    return mpg.LotGeometryResult(
        status="ok",
        outcome=outcome,
        review_required=False,
        requested_bbl=_BBL,
        borough=1,
        block=1,
        lot=10,
        condo={},
        identifier_conflicts=[],
        attributes=None,
        features=[],
        geometry=geometry,
        area_sq_ft=5000.0,
        shape_area_attribute_sq_ft=None,
        exceeded_transfer_limit=False,
        correlation_id="cid",
        request_url="https://example/query",
        metadata_request_url="https://example/meta",
        retrieved_at="2026-01-01T00:00:00Z",
        crs={"srid": 2263},
        source_data_last_edited_ms=None,
        source_data_last_edited=None,
        raw_digest="sha256:raw",
        metadata_raw_digest="sha256:meta",
        normalized_digest="sha256:norm",
        digest_canonicalization="spec",
        shapely_version="2.0.7",
        geos_version="3.11.4",
    )


_AUTH_POLY_A = [
    [["1000000", "200000"], ["1000100", "200000"], ["1000100", "200050"], ["1000000", "200050"]]
]
_AUTH_POLY_B = [
    [["2000000", "300000"], ["2000100", "300000"], ["2000100", "300050"], ["2000000", "300050"]]
]


def test_default_authoritative_ring_single_feature(monkeypatch):
    mpg = pytest.importorskip("app.connectors.mappluto_geometry_arcgis")
    assessment = _make_assessment(mpg, [_AUTH_POLY_A])
    monkeypatch.setattr(
        mpg,
        "fetch_lot_geometry",
        lambda bbl, *, correlation_id=None: _make_result(mpg, mpg.OUTCOME_SINGLE, assessment),
    )
    ring = _default_authoritative_ring(_BBL, "cid")
    assert ring.crs == "EPSG:2263"
    assert ring.source_id == mpg.SOURCE_ID
    assert ring.source_detail["representation"] == "lot_geometry_authoritative"
    assert ring.source_detail["normalized_digest"] == "sha256:auth"
    assert ring.points[0] == (1_000_000.0, 200_000.0)
    assert len(ring.points) == 4


def test_default_authoritative_ring_multipart_uses_first_polygon(monkeypatch):
    mpg = pytest.importorskip("app.connectors.mappluto_geometry_arcgis")
    assessment = _make_assessment(mpg, [_AUTH_POLY_A, _AUTH_POLY_B])
    monkeypatch.setattr(
        mpg,
        "fetch_lot_geometry",
        lambda bbl, *, correlation_id=None: _make_result(mpg, mpg.OUTCOME_SINGLE, assessment),
    )
    ring = _default_authoritative_ring(_BBL, "cid")
    assert ring.points[0] == (1_000_000.0, 200_000.0)  # from the FIRST polygon
    assert len(ring.points) == 4


def test_default_authoritative_ring_connector_error_is_ring_unavailable(monkeypatch):
    mpg = pytest.importorskip("app.connectors.mappluto_geometry_arcgis")

    def boom(bbl, *, correlation_id=None):
        raise mpg.MapPlutoGeometryConnectorError("upstream", correlation_id="cid")

    monkeypatch.setattr(mpg, "fetch_lot_geometry", boom)
    with pytest.raises(RingUnavailable) as exc:
        _default_authoritative_ring(_BBL, "cid")
    assert exc.value.source_id == mpg.SOURCE_ID


def test_default_authoritative_ring_non_single_outcome_is_ring_unavailable(monkeypatch):
    mpg = pytest.importorskip("app.connectors.mappluto_geometry_arcgis")
    assessment = _make_assessment(mpg, [_AUTH_POLY_A])
    monkeypatch.setattr(
        mpg,
        "fetch_lot_geometry",
        lambda bbl, *, correlation_id=None: _make_result(mpg, "multiple_features", assessment),
    )
    with pytest.raises(RingUnavailable) as exc:
        _default_authoritative_ring(_BBL, "cid")
    assert exc.value.source_id == mpg.SOURCE_ID


def test_default_authoritative_ring_missing_canonical_geometry_is_ring_unavailable(monkeypatch):
    mpg = pytest.importorskip("app.connectors.mappluto_geometry_arcgis")
    assessment = _make_assessment(mpg, None)
    monkeypatch.setattr(
        mpg,
        "fetch_lot_geometry",
        lambda bbl, *, correlation_id=None: _make_result(mpg, mpg.OUTCOME_SINGLE, assessment),
    )
    with pytest.raises(RingUnavailable):
        _default_authoritative_ring(_BBL, "cid")
