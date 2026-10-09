"""Bounded DOF Digital Tax Map outline transport, for display only.

This independent source exposes individual tax-lot polygons omitted by the
MapPLUTO condo-complex representation. It never changes the MapPLUTO default,
derives measurements, joins polygons, or establishes a legal zoning lot.
"""

from __future__ import annotations

import json
import math
import urllib.error
import urllib.request
import uuid
from datetime import UTC, datetime
from urllib.parse import urlencode

from app.connectors.bbl import NormalizedBBL, normalize_bbl
from app.connectors.mappluto_lot_outline import (
    LotOutlineError,
    LotOutlineFetcher,
    LotOutlineTransport,
    validate_lot_geometry_document,
)

SOURCE_ID = "nyc-dof-digital-tax-map"
SERVICE_ROOT = (
    "https://services6.arcgis.com/yG5s3afENB5iO9fj/ArcGIS/rest/services/"
    "DTM_ETL_DAILY_view/FeatureServer"
)
LAYER_NAME = "TAX_LOT_POLYGON (0)"
OUT_FIELDS = (
    "OBJECTID", "BBL", "BORO", "BLOCK", "LOT", "CONDO_FLAG",
    "BILL_BBL_FLAG", "EFFECTIVE_TAX_YEAR",
)
CONTRACT_VERSION = "1.1.0"
ACCURACY_NOTE = (
    "Approximate DOF Digital Tax Map outline for display only. A numerical "
    "horizontal-accuracy tolerance is not established for this source here. "
    "No area, dimension, or measurement is derived from these EPSG:4326 coordinates."
)
ATTRIBUTION = "NYC Department of Finance (DOF), Digital Tax Map"
DISCLAIMER = (
    "DOF Digital Tax Map data is provided for informational purposes and may "
    "not reflect the latest changes in other City systems. This is not a "
    "boundary survey, a zoning-lot determination, or permission to combine parcels."
)
_MAX_BODY_BYTES = 2 * 1024 * 1024


class DtmOutlineError(LotOutlineError):
    """Existing typed route taxonomy with the actual source identified."""

    def __init__(self, error_type: str, message: str, *, correlation_id: str, detail=None):
        super().__init__(message, correlation_id=correlation_id, detail=detail)
        self.error_type = error_type

    def to_payload(self) -> dict:
        return {**super().to_payload(), "source_id": SOURCE_ID}


def build_outline_query_url(canonical_bbl: str) -> str:
    """One canonical BBL, two records to detect ambiguity, fixed source/fields."""
    normalized = normalize_bbl(canonical_bbl)
    if normalized.canonical != canonical_bbl:
        raise ValueError("DTM outline query requires a canonical 10-digit BBL")
    query = urlencode({
        "where": f"BBL='{normalized.canonical}'",
        "outFields": ",".join(OUT_FIELDS),
        "orderByFields": "OBJECTID ASC",
        "resultRecordCount": 2,
        "resultOffset": 0,
        "returnGeometry": "true",
        "f": "geojson",
        "outSR": 4326,
    })
    return f"{SERVICE_ROOT}/0/query?{query}"


def default_fetch(canonical_bbl: str, correlation_id: str) -> LotOutlineTransport:
    """One keyless request; no paging, silent failover, or unbounded retries."""
    url = build_outline_query_url(canonical_bbl)
    request = urllib.request.Request(  # noqa: S310 - fixed host and canonical BBL only
        url, headers={"Accept": "application/json"}, method="GET"
    )
    retrieved_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        with urllib.request.urlopen(request, timeout=20.0) as response:  # noqa: S310
            status = int(response.status)
            body = response.read(_MAX_BODY_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise DtmOutlineError(
            "upstream_error", "official DOF tax-map service rejected the request",
            correlation_id=correlation_id, detail={"status": exc.code},
        ) from exc
    except OSError as exc:
        raise DtmOutlineError(
            "upstream_error", "official DOF tax-map service was unreachable",
            correlation_id=correlation_id, detail={"reason_kind": type(exc).__name__},
        ) from exc
    if len(body) > _MAX_BODY_BYTES:
        raise DtmOutlineError(
            "malformed_response", "DOF response exceeded the bounded read ceiling",
            correlation_id=correlation_id, detail={"limit_bytes": _MAX_BODY_BYTES},
        )
    return LotOutlineTransport(url, status, body.decode("utf-8", errors="replace"), retrieved_at)


def _read_collection(transport: LotOutlineTransport, correlation_id: str) -> list:
    if transport.status != 200:
        raise DtmOutlineError(
            "upstream_error", "unexpected HTTP status from the DOF tax-map service",
            correlation_id=correlation_id, detail={"status": transport.status},
        )
    try:
        doc = json.loads(transport.body)
    except ValueError as exc:
        raise DtmOutlineError(
            "malformed_response", "DOF response is not parseable JSON",
            correlation_id=correlation_id,
        ) from exc
    if isinstance(doc, dict) and isinstance(doc.get("error"), dict):
        raise DtmOutlineError(
            "upstream_error", "official DOF tax-map service returned an error object",
            correlation_id=correlation_id,
        )
    if not isinstance(doc, dict) or doc.get("type") != "FeatureCollection":
        raise DtmOutlineError(
            "malformed_response", "DOF response is not a GeoJSON FeatureCollection",
            correlation_id=correlation_id,
        )
    # Absent CRS follows GeoJSON's WGS84 convention; any present CRS must match.
    if "crs" in doc and doc["crs"] != {
        "type": "name", "properties": {"name": "EPSG:4326"}
    }:
        raise DtmOutlineError(
            "wrong_crs", "DOF response CRS does not match requested EPSG:4326",
            correlation_id=correlation_id,
        )
    features = doc.get("features")
    if not isinstance(features, list) or len(features) > 2:
        raise DtmOutlineError(
            "malformed_response", "DOF response violates the bounded feature array",
            correlation_id=correlation_id,
        )
    if doc.get("exceededTransferLimit") not in (None, False) and len(features) < 2:
        raise DtmOutlineError(
            "malformed_response", "DOF response is truncated; no complete lot can be drawn",
            correlation_id=correlation_id,
        )
    return features


def _check_identity(feature: object, normalized: NormalizedBBL, correlation_id: str) -> dict:
    if not isinstance(feature, dict) or feature.get("type") != "Feature":
        raise DtmOutlineError(
            "malformed_response", "DOF feature is malformed", correlation_id=correlation_id
        )
    props = feature.get("properties")
    expected = {
        "BBL": normalized.canonical, "BORO": normalized.canonical[0],
        "BLOCK": int(normalized.canonical[1:6]), "LOT": int(normalized.canonical[6:]),
    }
    # Missing identities, coercions, and conflicting component fields all fail closed.
    if not isinstance(props, dict) or any(
        type(props.get(key)) is not type(value) or props.get(key) != value
        for key, value in expected.items()
    ):
        raise DtmOutlineError(
            "result_mismatch", "DOF BBL and borough/block/lot do not match the requested lot",
            correlation_id=correlation_id, detail={"requested_bbl": normalized.canonical},
        )
    return props


def _ring_ok(ring: object) -> bool:
    return (
        isinstance(ring, list) and len(ring) >= 4 and ring[0] == ring[-1]
        and all(
            isinstance(pos, list) and len(pos) == 2
            and all(
                isinstance(value, (int, float)) and not isinstance(value, bool)
                and math.isfinite(value) and abs(value) <= limit
                for value, limit in zip(pos, (180, 90), strict=True)
            )
            for pos in ring
        )
    )


def _geometry_ok(geometry: object) -> bool:
    """Structural drawing check only; never repairs or measures coordinates."""
    if not isinstance(geometry, dict) or set(geometry) != {"type", "coordinates"}:
        return False
    coords = geometry["coordinates"]
    polygons = [coords] if geometry["type"] == "Polygon" else coords
    return (
        geometry["type"] in ("Polygon", "MultiPolygon")
        and isinstance(polygons, list) and len(polygons) > 0
        and all(
            isinstance(polygon, list) and len(polygon) > 0
            and all(_ring_ok(ring) for ring in polygon)
            for polygon in polygons
        )
    )


def parse_lot_outline(
    transport: LotOutlineTransport, *, normalized: NormalizedBBL, correlation_id: str
) -> dict:
    if transport.url != build_outline_query_url(normalized.canonical):
        raise DtmOutlineError(
            "result_mismatch", "DOF transport URL does not match the bounded request",
            correlation_id=correlation_id,
        )
    features = _read_collection(transport, correlation_id)
    properties = [_check_identity(feature, normalized, correlation_id) for feature in features]
    count = len(features)
    geometry = None
    identity = None
    notes = [
        "Exact requested DOF tax-lot identity only; no zoning-lot boundary, merger, "
        "buildable envelope, or development-rights determination is established.",
        "The source does not expose a dataset release version in this response. "
        "EFFECTIVE_TAX_YEAR is a source attribute, not a dataset release or freshness date.",
    ]
    condo_note = None
    if count == 0:
        outcome = "no_outline"
        notes.append("DOF TAX_LOT_POLYGON returned no feature for this exact BBL.")
    elif count > 1:
        outcome = "multiple_features"
        notes.append("Multiple DOF features match this BBL; review required, geometry withheld.")
    else:
        props = properties[0]
        raw_fields = {key: props.get(key) for key in OUT_FIELDS}
        notes.append("DOF source attributes: " + json.dumps(raw_fields, sort_keys=True))
        if props.get("CONDO_FLAG") == "C":
            condo_note = (
                "DOF CONDO_FLAG=C on this exact tax-lot polygon. This may be a condo base "
                "parcel; it is not classified as a unit or the whole complex from this flag."
            )
            notes.append(condo_note)
        if _geometry_ok(features[0].get("geometry")):
            outcome = "single_lot"
            geometry = features[0]["geometry"]
            identity = {
                "boro_code": int(props["BORO"]), "borough": None,
                "block": props["BLOCK"], "lot": props["LOT"], "condo_no": None,
            }
        else:
            outcome = "invalid_geometry"
            notes.append("Null, empty, open, non-polygon, or invalid coordinate geometry withheld.")
    return {
        "contract_version": CONTRACT_VERSION, "document_kind": "lot_outline",
        "bbl": normalized.canonical, "outcome": outcome,
        "display_only": True, "crs": "EPSG:4326", "geometry": geometry,
        "feature_count": count, "review_required": count > 1,
        "no_outline_reason": "no_feature_for_bbl" if count == 0 else None,
        "condo_classification": {
            "classification": "standard_lot", "condo_no": None, "note": condo_note,
        },
        "lot_identity": identity,
        "source": {
            "source_id": SOURCE_ID, "service_root": SERVICE_ROOT, "layer": LAYER_NAME,
            "endpoint": transport.url, "dataset_version": None,
            "retrieved_at": transport.retrieved_at,
        },
        "accuracy_note": ACCURACY_NOTE, "attribution": ATTRIBUTION,
        "disclaimer": DISCLAIMER, "notes": notes,
    }


def build_lot_outline(
    bbl: object, *, fetch: LotOutlineFetcher = default_fetch, correlation_id: str | None = None
) -> dict:
    correlation_id = correlation_id or uuid.uuid4().hex
    normalized = normalize_bbl(bbl)
    envelope = parse_lot_outline(
        fetch(normalized.canonical, correlation_id),
        normalized=normalized, correlation_id=correlation_id,
    )
    validate_lot_geometry_document(envelope, correlation_id=correlation_id)
    return envelope
