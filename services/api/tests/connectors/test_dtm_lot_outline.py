"""Official DOF fixture replay plus explicitly synthetic failure mutations."""

from __future__ import annotations

import copy
import hashlib
import json
import urllib.error
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

from app.connectors import dtm_lot_outline as dtm
from app.connectors.bbl import BBLValidationError
from app.connectors.mappluto_lot_outline import LotOutlineContractError, LotOutlineTransport

FX = Path(__file__).resolve().parents[1] / "fixtures" / "dtm_lot_outline"
MANIFEST = json.loads((FX / "MANIFEST.json").read_text())
BBL = "3022640032"


def fixture_fetch(bbl, correlation_id):
    capture = next(row for row in MANIFEST["captures"] if row["bbl"] == bbl)
    return LotOutlineTransport(
        capture["url"], 200, (FX / capture["file"]).read_text(), capture["retrieved_at"]
    )


def raw_document():
    return json.loads(fixture_fetch(BBL, "test").body)


def build_mutation(doc, *, status=200):
    transport = fixture_fetch(BBL, "test")
    return dtm.build_lot_outline(BBL, fetch=lambda b, c: LotOutlineTransport(
        transport.url, status, json.dumps(doc), transport.retrieved_at
    ))


@pytest.mark.parametrize("bbl", ["3022640032", "3022640033"])
def test_official_base_lot_identity_geometry_and_source_preserved(bbl):
    result = dtm.build_lot_outline(bbl, fetch=fixture_fetch)
    raw = json.loads(fixture_fetch(bbl, "test").body)["features"][0]
    assert result["outcome"] == "single_lot"
    assert result["geometry"] == raw["geometry"]
    assert result["bbl"] == raw["properties"]["BBL"]
    assert result["lot_identity"]["lot"] == int(bbl[-4:])
    assert result["source"]["source_id"] == "nyc-dof-digital-tax-map"
    assert result["source"]["dataset_version"] is None
    assert result["contract_version"] == "1.1.0"
    assert result["display_only"] is True
    assert result["crs"] == "EPSG:4326"
    assert "20 ft" not in result["accuracy_note"]
    assert "Finance" in result["attribution"]
    assert result["condo_classification"]["classification"] == "standard_lot"
    assert "CONDO_FLAG=C" in result["condo_classification"]["note"]
    assert any('"EFFECTIVE_TAX_YEAR":' in note for note in result["notes"])


def test_base_outlines_are_distinct_and_billing_outline_is_not_substituted():
    left = dtm.build_lot_outline("3022640032", fetch=fixture_fetch)
    right = dtm.build_lot_outline("3022640033", fetch=fixture_fetch)
    billing = dtm.build_lot_outline("3022647515", fetch=fixture_fetch)
    assert left["geometry"] != right["geometry"]
    assert billing["outcome"] == "no_outline"
    assert billing["geometry"] is None
    assert billing["no_outline_reason"] == "no_feature_for_bbl"
    assert billing["source"]["source_id"] == dtm.SOURCE_ID


@pytest.mark.parametrize("exceeded", [False, True])
def test_two_matching_features_are_review_required_never_first_pick(exceeded):
    doc = raw_document()
    doc["features"].append(copy.deepcopy(doc["features"][0]))
    doc["exceededTransferLimit"] = exceeded
    result = build_mutation(doc)
    assert result["outcome"] == "multiple_features"
    assert result["feature_count"] == 2
    assert result["review_required"] is True
    assert result["geometry"] is None


@pytest.mark.parametrize("key,value", [
    ("BBL", "3022640033"), ("BBL", 3022640032), ("BBL", None),
    ("BORO", "1"), ("BORO", 3), ("BLOCK", 9999), ("BLOCK", "2264"),
    ("LOT", 33), ("LOT", 32.0), ("LOT", True),
])
def test_identity_mismatches_and_missing_fields_fail_closed(key, value):
    doc = raw_document()
    doc["features"][0]["properties"][key] = value
    with pytest.raises(dtm.DtmOutlineError) as exc:
        build_mutation(doc)
    assert exc.value.error_type == "result_mismatch"
    assert exc.value.to_payload()["source_id"] == dtm.SOURCE_ID


@pytest.mark.parametrize("kind", ["null", "empty", "point", "open", "nan", "range", "bool"])
def test_invalid_geometries_are_typed_and_never_repaired(kind):
    doc = raw_document()
    geom = doc["features"][0]["geometry"]
    if kind == "null":
        doc["features"][0]["geometry"] = None
    elif kind == "empty":
        geom["coordinates"] = []
    elif kind == "point":
        geom["type"] = "Point"
    elif kind == "open":
        geom["coordinates"][0][-1] = [0, 0]
    else:
        geom["coordinates"][0][1][0] = {"nan": float("nan"), "range": 181, "bool": True}[kind]
    result = build_mutation(doc)
    assert result["outcome"] == "invalid_geometry"
    assert result["geometry"] is None


@pytest.mark.parametrize("doc,error", [
    ([], "malformed_response"), ({"error": {"code": 429}}, "upstream_error"),
    ({"type": "FeatureCollection", "features": None}, "malformed_response"),
    ({"type": "FeatureCollection", "features": [None]}, "malformed_response"),
    ({"type": "FeatureCollection", "features": [], "crs": None}, "wrong_crs"),
    ({"type": "FeatureCollection", "features": [],
      "crs": {"properties": {"name": "EPSG:3857"}}}, "wrong_crs"),
    ({"type": "FeatureCollection", "features": [],
      "exceededTransferLimit": True}, "malformed_response"),
])
def test_faults_remain_faults_instead_of_empty_or_successful_outlines(doc, error):
    with pytest.raises(dtm.DtmOutlineError) as exc:
        build_mutation(doc)
    assert exc.value.error_type == error


@pytest.mark.parametrize("status", [429, 503])
def test_http_error_status_remains_upstream_error(status):
    with pytest.raises(dtm.DtmOutlineError) as exc:
        build_mutation(raw_document(), status=status)
    assert exc.value.error_type == "upstream_error"
    assert exc.value.detail["status"] == status


def test_query_is_one_exact_canonical_bbl_with_fixed_projection_and_cap():
    query = parse_qs(urlparse(dtm.build_outline_query_url(BBL)).query)
    assert query["where"] == ["BBL='3022640032'"]
    assert query["resultRecordCount"] == ["2"]
    assert query["resultOffset"] == ["0"]
    assert query["returnGeometry"] == ["true"]
    assert query["f"] == ["geojson"]
    assert query["outSR"] == ["4326"]
    assert query["outFields"] == [",".join(dtm.OUT_FIELDS)]
    assert urlparse(dtm.build_outline_query_url(BBL)).netloc == "services6.arcgis.com"


def test_invalid_bbl_is_rejected_before_transport():
    def forbidden(*args):
        pytest.fail("invalid BBL must not reach transport")
    with pytest.raises(BBLValidationError):
        dtm.build_lot_outline("3022640032' OR 1=1", fetch=forbidden)


def test_source_url_mismatch_is_never_relabeled_as_dof():
    t = fixture_fetch(BBL, "test")
    with pytest.raises(dtm.DtmOutlineError) as exc:
        dtm.build_lot_outline(BBL, fetch=lambda b, c: LotOutlineTransport(
            "https://example.com/shape", t.status, t.body, t.retrieved_at
        ))
    assert exc.value.error_type == "result_mismatch"


def test_live_http_429_and_body_ceiling_are_bounded(monkeypatch):
    def rate_limit(*args, **kwargs):
        raise urllib.error.HTTPError("redacted", 429, "rate limited", {}, None)
    monkeypatch.setattr(dtm.urllib.request, "urlopen", rate_limit)
    with pytest.raises(dtm.DtmOutlineError) as exc:
        dtm.default_fetch(BBL, "test")
    assert exc.value.detail == {"status": 429}

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self, limit):
            assert limit == dtm._MAX_BODY_BYTES + 1
            return b"x" * limit

    monkeypatch.setattr(dtm.urllib.request, "urlopen", lambda *a, **k: Response())
    with pytest.raises(dtm.DtmOutlineError) as exc:
        dtm.default_fetch(BBL, "test")
    assert exc.value.error_type == "malformed_response"


def test_official_capture_hashes_and_urls_are_reproducible():
    for capture in [*MANIFEST["captures"], MANIFEST["metadata_capture"]]:
        assert hashlib.sha256((FX / capture["file"]).read_bytes()).hexdigest() == capture["sha256"]
        if "bbl" in capture:
            assert capture["url"] == dtm.build_outline_query_url(capture["bbl"])


def test_dof_source_cannot_be_emitted_under_old_contract_version():
    result = dtm.build_lot_outline(BBL, fetch=fixture_fetch)
    result["contract_version"] = "1.0.0"
    with pytest.raises(LotOutlineContractError):
        dtm.validate_lot_geometry_document(result)


@pytest.mark.parametrize("borough", ["1", "2", "3", "4", "5"])
def test_synthetic_identity_case_supports_each_borough_without_claiming_live_coverage(borough):
    # Synthetic identity mutation; these coordinates remain Brooklyn fixture data.
    bbl = borough + BBL[1:]
    doc = raw_document()
    doc["features"][0]["properties"].update(BBL=bbl, BORO=borough)
    result = dtm.build_lot_outline(bbl, fetch=lambda b, c: LotOutlineTransport(
        dtm.build_outline_query_url(b), 200, json.dumps(doc), "2026-09-26T20:00:00Z"
    ))
    assert result["bbl"] == bbl
    assert result["lot_identity"]["boro_code"] == int(borough)


def test_synthetic_multipolygon_holes_and_absent_crs_are_transported_verbatim():
    doc = raw_document()
    del doc["crs"]  # GeoJSON absent-CRS convention is WGS84, never 3857.
    polygon = doc["features"][0]["geometry"]["coordinates"]
    # Structural transport case only, not a topology/survey-validity claim.
    polygon.append(copy.deepcopy(polygon[0]))
    geometry = {"type": "MultiPolygon", "coordinates": [polygon]}
    doc["features"][0]["geometry"] = geometry
    result = build_mutation(doc)
    assert result["outcome"] == "single_lot"
    assert result["geometry"] == geometry
