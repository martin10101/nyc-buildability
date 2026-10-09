"""MapPLUTO lot-outline transport - DISPLAY-ONLY EPSG:4326 GeoJSON (task
M5-T020, D-040-R001).

A NEW focused transport module that exposes the official NYC DCP MapPLUTO
parcel geometry to a web map (MapLibre GL JS) as an approximate, display-only
outline. It queries the SAME official ArcGIS feature service the accepted
authoritative connector uses (``services/api/app/connectors/mappluto_geometry_arcgis.py``)
but requests ``f=geojson&outSR=4326`` so the service reprojects SERVER-SIDE to
WGS84 longitude/latitude, then transports the result verbatim into a typed,
contract-valid outline envelope.

DISPLAY-ONLY DISCIPLINE (the research's critical constraint, D-040-R001):

- The authoritative EPSG:2263 (US survey feet) connector is BYTE-IMMUTABLE and
  remains the SOLE owner of measurement, canonical geometry digests, and legal
  provenance. This module NEVER edits it and NEVER re-routes it; it only
  IMPORTS its public discipline (``normalize_bbl``, ``SERVICE_ROOT`` /
  ``LAYER_NAME`` / ``OUT_FIELDS`` / ``MAX_FEATURES_PER_LOT`` constants, the
  ``_condo_classification`` semantics, and ``DisallowedRequestError``).
- The transported 4326 geometry carries ``display_only=true``, the source's own
  +/-20 ft accuracy note, and NYC DCP attribution. **No area, dimension, or any
  measurement is EVER computed from these degree coordinates anywhere in this
  module** - the authoritative 2263 path owns measurement.

HONEST TYPED OUTCOMES (mirroring the authoritative connector's vocabulary):

- ``single_lot``       - one feature, a valid Polygon/MultiPolygon outline.
- ``no_outline``       - zero features. A condominium UNIT lot (1001-6999) has
  no polygon of its own (``condo_unit_lot_no_polygon``); any other empty result
  is ``no_feature_for_bbl``. NEVER a fabricated or blank shape.
- ``multiple_features``- more than one feature for one BBL: REVIEW REQUIRED,
  geometry withheld, NEVER a silent first-pick.
- ``invalid_geometry`` - a feature whose geometry is null/empty/non-polygon or
  carries a non-finite coordinate: a typed 200 outcome, never a 500.

Deterministic transport only: no AI, no legal interpretation, no measurement.
The official DCP disclaimer applies (informational purposes only).
"""

from __future__ import annotations

import json
import logging
import math
import urllib.request
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from importlib import resources

from app.connectors.bbl import NormalizedBBL, normalize_bbl

# Read-only reuse of the authoritative connector's PUBLIC discipline. This
# module imports names; it NEVER edits or re-routes that byte-immutable module.
from app.connectors.mappluto_geometry_arcgis import (
    BOUNDARY_TOLERANCE_FT,
    LAYER_NAME,
    MAX_FEATURES_PER_LOT,
    OUT_FIELDS,
    SERVICE_ROOT,
    SOURCE_ID,
    DisallowedRequestError,
    _condo_classification,
)

__all__ = [
    "ACCURACY_NOTE",
    "ATTRIBUTION",
    "CONTRACT_VERSION",
    "CRS_4326",
    "DCP_DISCLAIMER",
    "OUTCOME_INVALID_GEOMETRY",
    "OUTCOME_MULTIPLE",
    "OUTCOME_NO_OUTLINE",
    "OUTCOME_SINGLE",
    "LotOutlineContractError",
    "LotOutlineError",
    "LotOutlineResultMismatchError",
    "LotOutlineTransport",
    "MalformedOutlineResponseError",
    "UnexpectedCRSError",
    "build_lot_outline",
    "build_outline_query_url",
    "default_fetch",
    "parse_lot_outline",
    "validate_lot_geometry_document",
]

logger = logging.getLogger("app.connectors.mappluto_lot_outline")

CONTRACT_VERSION = "1.0.0"
DOCUMENT_KIND = "lot_outline"

# EPSG:4326 (WGS84 lng/lat degrees): the display CRS produced by the service's
# outSR=4326 server-side reprojection. The authoritative source CRS is 2263 and
# stays owned by the immutable connector; this module never interprets 2263.
CRS_4326 = "EPSG:4326"

# Typed outline outcomes (mirroring the authoritative connector's honest
# feature-count vocabulary, mapped to the display-outline surface).
OUTCOME_SINGLE = "single_lot"
OUTCOME_NO_OUTLINE = "no_outline"
OUTCOME_MULTIPLE = "multiple_features"
OUTCOME_INVALID_GEOMETRY = "invalid_geometry"

# no_outline reasons.
_REASON_CONDO_UNIT = "condo_unit_lot_no_polygon"
_REASON_NO_FEATURE = "no_feature_for_bbl"

ACCURACY_NOTE = (
    "This is a DISPLAY-ONLY outline. The official NYC DCP source states "
    f"plus-or-minus {BOUNDARY_TOLERANCE_FT:.0f} ft horizontal accuracy, so the "
    "outline is approximate. No area, dimension, or other measurement is "
    "derived from these EPSG:4326 coordinates; authoritative measurement uses "
    "the EPSG:2263 (US survey feet) path only."
)
ATTRIBUTION = "NYC Department of City Planning (DCP), MapPLUTO"
DCP_DISCLAIMER = (
    "Provided by NYC DCP for informational purposes only; DCP does not warranty "
    "completeness, accuracy, content, or fitness for any particular purpose or "
    "use. This is not a legal boundary survey."
)

# Bounded body read: an outline for one lot is small; the largest observed live
# capture (Governors Island, a highly detailed multipolygon) is ~120 KB, so a
# 16 MB ceiling is generous while still bounding a hostile/unbounded body.
_MAX_BODY_BYTES = 16 * 1024 * 1024


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _rfc3339(when: datetime) -> str:
    return when.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Typed error taxonomy (transport/parse FAULTS only; the four honest outline
# outcomes are NORMAL results, never errors)
# ---------------------------------------------------------------------------


class LotOutlineError(Exception):
    """Base typed transport error. Payloads never contain stack traces,
    headers, or tokens (the service is keyless; no token exists)."""

    error_type = "upstream_error"

    def __init__(self, message: str, *, correlation_id: str, detail: dict | None = None):
        super().__init__(message)
        self.message = message
        self.correlation_id = correlation_id
        self.detail = detail or {}

    def to_payload(self) -> dict:
        return {
            "error_type": self.error_type,
            "message": self.message,
            "correlation_id": self.correlation_id,
            "source_id": SOURCE_ID,
            "detail": self.detail,
        }


class MalformedOutlineResponseError(LotOutlineError):
    """Response body is not a well-formed GeoJSON FeatureCollection. NEVER
    converted into a valid empty outline."""

    error_type = "malformed_response"


class UnexpectedCRSError(LotOutlineError):
    """The response CRS member is not EPSG:4326 even though outSR=4326 was
    requested; no coordinate is transported until the display CRS is confirmed."""

    error_type = "wrong_crs"


class LotOutlineResultMismatchError(LotOutlineError):
    """The returned feature's BBL attribute does not correspond to the requested
    lot; returned data is never silently trusted."""

    error_type = "result_mismatch"


class LotOutlineContractError(LotOutlineError):
    """The assembled outline envelope failed strict validation against the
    bundled canonical schema - an internal defect, never emitted as a 200."""

    error_type = "internal_contract_error"

    def __init__(self, message: str, *, correlation_id: str, location: str) -> None:
        super().__init__(message, correlation_id=correlation_id, detail={"location": location})
        self.location = location


# ---------------------------------------------------------------------------
# Transport seam (injected for offline tests; the M5-T003/M5-T013 pattern)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LotOutlineTransport:
    """Raw transport result for one bounded outline query: the exact URL
    requested, the HTTP status, the verbatim response body text, and the
    retrieval timestamp (RFC 3339). The fetcher builds the URL and stamps the
    timestamp, so URL and retrieval provenance are FACTS of the real request."""

    url: str
    status: int
    body: str
    retrieved_at: str


def build_outline_query_url(canonical_bbl: str, *, correlation_id: str = "urlbuild") -> str:
    """The ONLY query URL this module emits: an exact-BBL equality filter with
    the SAME bounded out-field set and record cap as the authoritative
    connector, plus ``f=geojson&outSR=4326`` for the display reprojection. The
    BBL segment comes EXCLUSIVELY from ``normalize_bbl`` output; a caller can
    never supply URLs, hosts, raw where clauses, field lists, or paging values
    (injection-proof by construction - mirrors ``build_lot_query_url``)."""
    normalized = normalize_bbl(canonical_bbl)
    if normalized.canonical != canonical_bbl:
        raise DisallowedRequestError(
            "build_outline_query_url requires the canonical 10-digit BBL form",
            correlation_id=correlation_id,
            detail={"value": repr(canonical_bbl)},
        )
    out_fields = "%2C".join(OUT_FIELDS)
    return (
        f"{SERVICE_ROOT}/{LAYER_NAME}/FeatureServer/0/query"
        f"?where=BBL%3D{int(normalized.canonical)}"
        f"&outFields={out_fields}"
        "&orderByFields=OBJECTID%20ASC"
        f"&resultRecordCount={MAX_FEATURES_PER_LOT}&resultOffset=0"
        "&f=geojson&outSR=4326"
    )


def default_fetch(canonical_bbl: str, correlation_id: str) -> LotOutlineTransport:
    """Live transport (production default): a plain keyless GET of the bounded
    outline query with a bounded body read. Tests inject a fetcher that reads
    recorded fixture bytes instead, so the whole suite runs OFFLINE."""
    url = build_outline_query_url(canonical_bbl, correlation_id=correlation_id)
    req = urllib.request.Request(  # noqa: S310 - URL is built from a validated canonical BBL only
        url, headers={"Accept": "application/json"}, method="GET"
    )
    retrieved_at = _rfc3339(_utc_now())
    try:
        with urllib.request.urlopen(req, timeout=30.0) as response:  # noqa: S310
            status = int(response.status)
            body = response.read(_MAX_BODY_BYTES + 1)
    except OSError as exc:
        raise LotOutlineError(
            "official ArcGIS service was unreachable",
            correlation_id=correlation_id,
            detail={"reason_kind": type(exc).__name__},
        ) from exc
    if len(body) > _MAX_BODY_BYTES:
        raise MalformedOutlineResponseError(
            "response body exceeded the bounded read ceiling",
            correlation_id=correlation_id,
            detail={"limit_bytes": _MAX_BODY_BYTES},
        )
    return LotOutlineTransport(
        url=url, status=status, body=body.decode("utf-8", errors="replace"),
        retrieved_at=retrieved_at,
    )


# ---------------------------------------------------------------------------
# Geometry transport validation (STRUCTURAL only - NEVER measurement)
# ---------------------------------------------------------------------------


def _finite_position(pos: object) -> bool:
    return (
        isinstance(pos, list)
        and len(pos) == 2
        and all(
            isinstance(c, (int, float)) and not isinstance(c, bool) and math.isfinite(c)
            for c in pos
        )
    )


def _ring_ok(ring: object) -> bool:
    return isinstance(ring, list) and len(ring) >= 4 and all(_finite_position(p) for p in ring)


def _polygon_ok(coords: object) -> bool:
    return isinstance(coords, list) and len(coords) >= 1 and all(_ring_ok(r) for r in coords)


def _transportable_geometry(geom: object) -> bool:
    """True only for a structurally sound Polygon/MultiPolygon with finite
    lng/lat coordinates. This is a TRANSPORT check (is this drawable?), NOT a
    topology/validity assessment and NEVER a measurement - topology and area
    belong to the authoritative 2263 connector."""
    if not isinstance(geom, dict):
        return False
    gtype = geom.get("type")
    coords = geom.get("coordinates")
    if gtype == "Polygon":
        return _polygon_ok(coords)
    if gtype == "MultiPolygon":
        return isinstance(coords, list) and len(coords) >= 1 and all(_polygon_ok(p) for p in coords)
    return False


def _as_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _lot_identity(props: dict) -> dict:
    return {
        "boro_code": _as_int(props.get("BoroCode")),
        "borough": props.get("Borough") if isinstance(props.get("Borough"), str) else None,
        "block": _as_int(props.get("Block")),
        "lot": _as_int(props.get("Lot")),
        "condo_no": _as_int(props.get("CondoNo")),
    }


# ---------------------------------------------------------------------------
# Response parsing -> typed display-only envelope
# ---------------------------------------------------------------------------


def _assert_crs_4326(doc: dict, *, url: str, correlation_id: str) -> None:
    crs = doc.get("crs")
    name = None
    if isinstance(crs, dict):
        props = crs.get("properties")
        if isinstance(props, dict):
            name = props.get("name")
    # Some servers omit the CRS member on a geojson response and imply the
    # requested outSR; a PRESENT-but-different CRS is the only unsafe case.
    if name is not None and name != CRS_4326:
        raise UnexpectedCRSError(
            "official service returned a CRS other than the requested EPSG:4326",
            correlation_id=correlation_id,
            detail={"url": url, "crs_name": str(name)[:64]},
        )


def _condo_block(normalized: NormalizedBBL, props: dict | None) -> dict:
    """Mirror the authoritative connector's condo semantics VERBATIM (import,
    never fork), reshaped to the closed condo_classification contract fields."""
    classified = _condo_classification(normalized, props)
    return {
        "classification": classified["classification"],
        "condo_no": _as_int(classified.get("condo_no")),
        "note": classified.get("note"),
    }


def parse_lot_outline(
    transport: LotOutlineTransport, *, normalized: NormalizedBBL, correlation_id: str
) -> dict:
    """Parse a recorded/live ``f=geojson&outSR=4326`` response into a typed,
    display-only outline envelope. Raises a typed FAULT only for genuine
    transport/parse failures; the four honest outcomes are NORMAL results."""
    if transport.status != 200:
        raise LotOutlineError(
            "unexpected HTTP status from the official ArcGIS service",
            correlation_id=correlation_id,
            detail={"url": transport.url, "status": transport.status},
        )
    try:
        doc = json.loads(transport.body)
    except ValueError as exc:
        raise MalformedOutlineResponseError(
            "response body is not parseable JSON",
            correlation_id=correlation_id,
            detail={"url": transport.url},
        ) from exc
    if not isinstance(doc, dict):
        raise MalformedOutlineResponseError(
            "response JSON is not an object",
            correlation_id=correlation_id,
            detail={"url": transport.url},
        )
    if doc.get("type") != "FeatureCollection":
        # ArcGIS can deliver an error object even with HTTP 200.
        if isinstance(doc.get("error"), dict):
            raise LotOutlineError(
                "official ArcGIS service returned an error object",
                correlation_id=correlation_id,
                detail={"url": transport.url},
            )
        raise MalformedOutlineResponseError(
            "response is not a GeoJSON FeatureCollection",
            correlation_id=correlation_id,
            detail={"url": transport.url},
        )
    _assert_crs_4326(doc, url=transport.url, correlation_id=correlation_id)
    features = doc.get("features")
    if not isinstance(features, list):
        raise MalformedOutlineResponseError(
            "FeatureCollection has no features array",
            correlation_id=correlation_id,
            detail={"url": transport.url},
        )

    feature_count = len(features)
    notes: list[str] = []
    geometry: dict | None = None
    outcome = OUTCOME_SINGLE
    review_required = False
    no_outline_reason: str | None = None
    lot_identity: dict | None = None
    dataset_version: str | None = None
    condo = _condo_block(normalized, None)

    if feature_count == 0:
        outcome = OUTCOME_NO_OUTLINE
        if condo["classification"] == "condo_unit_lot_query":
            no_outline_reason = _REASON_CONDO_UNIT
            notes.append(condo["note"] or "condominium unit lot has no polygon")
        else:
            no_outline_reason = _REASON_NO_FEATURE
            notes.append(
                "no_outline: the official service returned a well-formed response "
                "with zero features for this BBL. This is a typed outcome, never "
                "an error and never a fabricated shape."
            )
    elif feature_count > 1:
        outcome = OUTCOME_MULTIPLE
        review_required = True
        notes.append(
            f"multiple_features: {feature_count} features were returned for one "
            "BBL. This is REVIEW REQUIRED; no outline is drawn and the module "
            "never silently picks the first feature."
        )
    else:
        feature = features[0]
        props = feature.get("properties") if isinstance(feature.get("properties"), dict) else {}
        geom = feature.get("geometry")
        attr_bbl = _as_int(props.get("BBL"))
        if attr_bbl is not None and str(attr_bbl) != normalized.canonical:
            raise LotOutlineResultMismatchError(
                "returned feature does not correspond to the requested lot",
                correlation_id=correlation_id,
                detail={
                    "url": transport.url,
                    "requested_bbl": normalized.canonical,
                    "returned_bbl": repr(props.get("BBL")),
                },
            )
        condo = _condo_block(normalized, props)
        if _transportable_geometry(geom):
            outcome = OUTCOME_SINGLE
            geometry = geom
            lot_identity = _lot_identity(props)
            version = props.get("Version")
            dataset_version = version if isinstance(version, str) and version else None
            if condo["classification"] == "condo_billing_lot":
                notes.append(condo["note"] or "condominium billing lot: merged complex outline")
        else:
            outcome = OUTCOME_INVALID_GEOMETRY
            notes.append(
                "invalid_geometry: the returned feature carries a null, empty, "
                "non-polygon, or non-finite geometry. No outline is drawn; this "
                "is a typed outcome, never a fabricated shape."
            )

    envelope = {
        "contract_version": CONTRACT_VERSION,
        "document_kind": DOCUMENT_KIND,
        "bbl": normalized.canonical,
        "outcome": outcome,
        "display_only": True,
        "crs": CRS_4326,
        "geometry": geometry,
        "feature_count": feature_count,
        "review_required": review_required,
        "no_outline_reason": no_outline_reason,
        "condo_classification": condo,
        "lot_identity": lot_identity,
        "source": {
            "source_id": SOURCE_ID,
            "service_root": SERVICE_ROOT,
            "layer": LAYER_NAME,
            "endpoint": transport.url,
            "dataset_version": dataset_version,
            "retrieved_at": transport.retrieved_at,
        },
        "accuracy_note": ACCURACY_NOTE,
        "attribution": ATTRIBUTION,
        "disclaimer": DCP_DISCLAIMER,
        "notes": notes,
    }
    return envelope


# ---------------------------------------------------------------------------
# Strict contract validation (mirrors app.scenario.contract; the bundled schema
# works from a non-editable install via importlib.resources)
# ---------------------------------------------------------------------------

_SCHEMA_PACKAGE = "app._contract_schemas.v1"
_REGISTRY_SCHEMA_FILES = ("lot_geometry.schema.json", "common.schema.json")


def _load_bundled_schema(name: str) -> dict:
    text = resources.files(_SCHEMA_PACKAGE).joinpath(name).read_text(encoding="utf-8")
    return json.loads(text)


@lru_cache(maxsize=1)
def _validator():
    import jsonschema

    docs = [_load_bundled_schema(name) for name in _REGISTRY_SCHEMA_FILES]
    schema = docs[0]
    try:
        from referencing import Registry, Resource

        registry = Registry().with_resources(
            [(doc["$id"], Resource.from_contents(doc)) for doc in docs]
        )
        return jsonschema.Draft202012Validator(schema, registry=registry)
    except ImportError:  # pragma: no cover - legacy runners only
        resolver = jsonschema.RefResolver(
            base_uri=schema["$id"],
            referrer=schema,
            store={doc["$id"]: doc for doc in docs},
        )
        return jsonschema.Draft202012Validator(schema, resolver=resolver)


def validate_lot_geometry_document(document: dict, *, correlation_id: str = "validate") -> None:
    """Validate an outline envelope against the bundled ``lot_geometry`` schema
    strictly, before it can be emitted. Fails closed on any NaN/Infinity numeric
    (strict JSON must never carry one) and on any schema defect. Raises
    :class:`LotOutlineContractError` so an invalid 200 is impossible."""
    try:
        json.dumps(document, allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise LotOutlineContractError(
            f"outline document is not strict-JSON serializable: {exc}",
            correlation_id=correlation_id,
            location="<root>",
        ) from exc

    validator = _validator()
    errors = sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise LotOutlineContractError(
            f"outline document failed canonical schema validation at {location}: "
            f"{first.message}",
            correlation_id=correlation_id,
            location=location,
        )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

LotOutlineFetcher = Callable[[str, str], LotOutlineTransport]


def build_lot_outline(
    bbl: object,
    *,
    fetch: LotOutlineFetcher = default_fetch,
    correlation_id: str | None = None,
) -> dict:
    """Fetch and transport the display-only 4326 lot outline for one BBL.

    ``bbl`` is validated via ``normalize_bbl`` BEFORE any I/O
    (``BBLValidationError`` propagates for malformed input). ``fetch`` is the
    injected transport seam ((canonical_bbl, correlation_id) -> transport); the
    default performs a live keyless GET, tests inject recorded fixtures. The
    assembled envelope is strictly contract-validated before return."""
    correlation_id = correlation_id or uuid.uuid4().hex
    normalized = normalize_bbl(bbl)
    transport = fetch(normalized.canonical, correlation_id)
    envelope = parse_lot_outline(
        transport, normalized=normalized, correlation_id=correlation_id
    )
    validate_lot_geometry_document(envelope, correlation_id=correlation_id)
    return envelope
