"""MapPLUTO per-BBL tax-lot geometry connector - official DCP_GIS ArcGIS
MAPPLUTO feature service (task M2-T009; research
docs/research/pluto-mappluto-2026-07-16.md section 2.5).

Channel: the G1-verified official ArcGIS feature service
``services5.arcgis.com/GfwWNkhOj9bNBqoJ/.../MAPPLUTO/FeatureServer`` (owner
DCP_GIS "NYC DCP Mapping Portal"; layer 0 polygon, 103 fields, serving
release 26v1, maxRecordCount 2000). Per research section 5.2 this channel is
the per-lot query channel; the citywide bulk FileGDB import remains a
separate deferred task (B-001/B-002).

Design commitments (packet safeguards 1-6):

1. IDENTIFIER AND RESULT VALIDATION - every query starts from
   ``app.connectors.bbl.normalize_bbl`` (strict borough/block/lot canonical
   validation BEFORE any network I/O). Returned features are validated as
   corresponding to the requested lot (BBL attribute equality is mandatory;
   BoroCode/Block/Lot component disagreement is surfaced as visible
   identifier conflicts). Zero, one, and multiple returned features are
   each an explicit typed outcome (``no_feature`` / ``single_feature`` /
   ``multiple_features``); multiple features for one BBL is REVIEW REQUIRED,
   never a silent first-pick. Condominium semantics per research section
   2.5: MapPLUTO carries ONE record per condo complex under the billing lot
   (7501-7599); unit lots (1001-6999) have no polygon of their own and this
   connector never claims otherwise.
2. CRS - the authoritative source CRS (EPSG:2263 / wkid 102718, NAD83 New
   York Long Island, US survey feet) is validated from service metadata and
   from every query envelope BEFORE any coordinate is interpreted. A wrong
   CRS is the typed ``wrong_crs`` failure. Area is computed ONLY in the
   validated projected-feet CRS (planar square feet); no code path computes
   area from longitude/latitude degrees - ``analyze_lot_geometry`` and
   ``compute_area_sq_ft`` REFUSE non-authoritative CRS inputs (negative
   tests prove the rejection). No reprojection happens in this module.
3. GEOMETRY VALIDITY TAXONOMY - polygon, multipolygon, holes, empty
   geometry, null geometry, self-intersection, unclosed rings, inverted
   orientation, duplicate vertices, degenerate rings, and
   geometry-collection surprises each map to an explicit typed state:
   assessment ``status`` in {``valid``, ``repaired``, ``invalid_geometry``,
   ``review_required``} with machine-readable ``findings`` codes
   (``null_geometry``, ``empty_geometry``, ``self_intersection``,
   ``unclosed_ring``, ``invalid_orientation``, ``duplicate_vertices``,
   ``degenerate_ring``, ``geometry_collection``, ...).
4. NO SILENT REPAIR - the verbatim original esri geometry digest is ALWAYS
   preserved (plus the raw response-body digest pins the exact transported
   bytes). Whether repair occurred, every repair method applied, and the
   pinned Shapely/GEOS versions are recorded on the assessment. Original
   and repaired/normalized digests are kept SEPARATELY. A repair that
   cannot be safely characterized (unknown validity pathology, inverted
   ring orientation, non-polygonal make_valid output) returns the explicit
   ``review_required`` state. Repaired geometry is never presented as the
   untouched official source.
5. DETERMINISTIC GEOMETRY DIGESTS - ``MPG_CANONICALIZATION_SPEC`` defines
   canonical ordering for rings, holes, and multipolygon members, a fixed
   coordinate precision (0.01 ft), and a fixed serialization; default
   WKB/WKT output is deliberately NOT used (not assumed cross-platform
   canonical). Shapely/GEOS versions are pinned exactly
   (``PINNED_SHAPELY_VERSION`` / ``PINNED_GEOS_VERSION_STRING``) and
   asserted in the test suite; a hardcoded cross-platform anchor digest in
   the tests proves byte-identical reproduction on CI's platform.
6. SPATIAL READINESS - ``classify_spatial_relation`` is a TEST-LEVEL
   diagnostic proving the normalized lot geometry is intersection-ready
   against the M2-T007 district fixtures. Tolerance behavior is explicitly
   named: ``BOUNDARY_TOLERANCE_FT`` = 20.0 ft, from the official source
   statement of plus-or-minus 20 ft horizontal accuracy (zoning-features
   research section 4.3). A result within tolerance of a boundary is typed
   ``boundary_uncertain`` - NEVER silently inside or outside. This is NOT a
   production spatial-intersection engine (out of scope per packet).

TWO-STALENESS RULE (owner directive 2026-07-17): ``source_data_last_edited``
(service ``editingInfo.dataLastEditDate``) is source-dataset freshness
PROVENANCE; it never sets ``served_from_cache`` or ``stale``. The
``staleness`` field describes TRANSPORT/cache fallback only and is stamped
exclusively by ``ResilientMapPlutoGeometryClient`` on cache-hit and
last-known-good serves.

Deterministic code only: no AI, no legal interpretation, no lot-level zoning
assignment, no legal boundary certification. The official DCP disclaimer
applies (informational purposes only; research section 4.7).
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import math
import re
import threading
import time
import uuid
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from random import Random

import shapely
from shapely.geometry import MultiPolygon, Point, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.validation import explain_validity, make_valid

from app.connectors.bbl import (
    NormalizedBBL,
    check_identifier_consistency,
    normalize_bbl,
)

# Reused hardened transport + canonical JSON digest from the accepted M1-T002
# connector (bounded body read, refused redirects, typed transport signals).
# Read-only reuse: pluto_soda.py itself is NOT modified by this task.
from app.connectors.pluto_soda import canonical_json_digest
from app.resilience.breaker import CircuitBreaker
from app.resilience.budget import AnalysisBudget
from app.resilience.cache import TTLCache
from app.resilience.config import ResilienceConfig
from app.resilience.metrics import ResilienceMetrics

# Task M2-T011: hardened transport and the bounded retry engine now come
# from the shared app.resilience.transport module (moved verbatim from the
# accepted M1-T002 implementation this connector previously reused via
# pluto_soda). Connector semantics - error taxonomy, messages, geometry
# gates - stay HERE and reach the engine through standard_retry_hooks.
from app.resilience.transport import (
    Transport,
    TransportResponse,
    jittered_retry_after_delay,
    request_with_retry,
    standard_retry_hooks,
    urllib_transport,
)

__all__ = [
    "BOUNDARY_TOLERANCE_FT",
    "CONDO_BILLING_LOT_MAX",
    "CONDO_BILLING_LOT_MIN",
    "CONDO_UNIT_LOT_MAX",
    "CONDO_UNIT_LOT_MIN",
    "COORD_DECIMALS",
    "CRS_STAMP",
    "EXPECTED_LATEST_WKID",
    "EXPECTED_WKID",
    "LAYER_NAME",
    "MAX_FEATURES_PER_LOT",
    "MPG_CANONICALIZATION_SPEC",
    "OUT_FIELDS",
    "PINNED_GEOS_VERSION_STRING",
    "PINNED_SHAPELY_VERSION",
    "REQUIRED_FIELDS",
    "SERVICE_ROOT",
    "SOURCE_ID",
    "CircuitOpenError",
    "DisallowedRequestError",
    "GeometryAssessment",
    "LotGeometryResult",
    "MapPlutoGeometryConnectorError",
    "MalformedResponseError",
    "MapPlutoLayerMetadata",
    "RateLimitedError",
    "RequestBudgetExceededError",
    "ResilientMapPlutoGeometryClient",
    "ResultMismatchError",
    "SchemaDriftError",
    "SourceTimeoutError",
    "UpstreamError",
    "WrongCRSError",
    "analyze_lot_geometry",
    "build_lot_query_url",
    "build_metadata_url",
    "canonical_to_shapely",
    "classify_spatial_relation",
    "compute_area_sq_ft",
    "fetch_layer_metadata",
    "fetch_lot_geometry",
    "normalized_geometry_digest",
    "raw_body_digest",
    "require_authoritative_crs",
]

logger = logging.getLogger("app.connectors.mappluto_geometry_arcgis")

SOURCE_ID = "nyc-dcp-mappluto-arcgis"

# Pinned official root (research section 2.5 / G1 correction C4: ArcGIS
# Online item verified under owner DCP_GIS, org "NYC DCP Mapping Portal").
# NEVER interpolated from caller input. Same official org root as the
# accepted M2-T007 zoning-features connector.
SERVICE_ROOT = "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services"
LAYER_NAME = "MAPPLUTO"

# Authoritative source CRS (research sections 2.5/4.6: service reports wkid
# 102718 / latestWkid 2263 = EPSG:2263, NAD83 New York Long Island, US
# survey feet). Fixture MPG01 (captured 2026-07-20 UTC) confirms live.
EXPECTED_WKID = 102718
EXPECTED_LATEST_WKID = 2263
CRS_STAMP = {
    "wkid": EXPECTED_WKID,
    "latest_wkid": EXPECTED_LATEST_WKID,
    "authority": "EPSG:2263 (NAD83 / New York Long Island, US survey feet)",
}
EXPECTED_GEOMETRY_TYPE = "esriGeometryPolygon"

# Exactly-pinned geometry library versions this connector's digests are
# proven against (packet safeguard 5). The test suite asserts the runtime
# matches these pins; the dependency files pin shapely==PINNED_SHAPELY_VERSION
# (the official 2.0.7 wheels bundle GEOS 3.11.4 on every platform).
PINNED_SHAPELY_VERSION = "2.0.7"
PINNED_GEOS_VERSION_STRING = "3.11.4"

# Boundary tolerance for spatial classification: the official source states
# plus-or-minus 20 ft horizontal accuracy (zoning-features research section
# 4.3, official nyzd metadata PDF read at G1; MapPLUTO geometry derives from
# the same DTM/DCP production chain). Within this distance of a boundary a
# spatial relation is UNCERTAIN by the source's own accuracy statement.
BOUNDARY_TOLERANCE_FT = 20.0

# Condominium lot-number semantics (research section 2.5, official
# meta_mappluto.pdf verified at G1): unit lots 1001-6999 carry NO MapPLUTO
# polygon; billing lots 7501-7599 carry the merged complex polygon.
CONDO_UNIT_LOT_MIN = 1001
CONDO_UNIT_LOT_MAX = 6999
CONDO_BILLING_LOT_MIN = 7501
CONDO_BILLING_LOT_MAX = 7599

# Canonical-digest coordinate precision: 0.01 ft. Far below the stated
# plus-or-minus 20 ft source accuracy, far above float noise - quantization
# makes the digest deterministic without discarding real precision.
COORD_DECIMALS = 2

# Bounded query parameters (allowlist safeguard). The connector requests an
# explicit field subset - never '*' - and at most MAX_FEATURES_PER_LOT
# features per lot query (a lot with more matches is review-required anyway).
OUT_FIELDS = (
    "OBJECTID",
    "BBL",
    "BoroCode",
    "Borough",
    "Block",
    "Lot",
    "CondoNo",
    "Version",
    "Shape__Area",
    "Shape__Length",
)
MAX_FEATURES_PER_LOT = 10

# Required layer schema subset (live MAPPLUTO layer metadata captured
# 2026-07-20 UTC, fixture MPG01; the test suite cross-checks these constants
# against the fixture so transcription drift fails the build). The live
# layer carries 103 fields; this connector's contract needs exactly these.
REQUIRED_FIELDS: dict[str, str] = {
    "OBJECTID": "esriFieldTypeOID",
    "BBL": "esriFieldTypeDouble",
    "BoroCode": "esriFieldTypeInteger",
    "Borough": "esriFieldTypeString",
    "Block": "esriFieldTypeInteger",
    "Lot": "esriFieldTypeSmallInteger",
    "CondoNo": "esriFieldTypeInteger",
    "Version": "esriFieldTypeString",
    "Shape__Area": "esriFieldTypeDouble",
    "Shape__Length": "esriFieldTypeDouble",
}

# Divergence note threshold between the service's Shape__Area attribute and
# the locally computed planar area (both in EPSG:2263 sq ft). Divergence is
# surfaced as a visible note, never silently reconciled.
SHAPE_AREA_DIVERGENCE_REL = 0.005

# Relative area drift beyond which a make_valid repair is treated as
# uncharacterizable (review_required) instead of an accepted repair.
MAX_REPAIR_AREA_REL_DRIFT = 0.01

MPG_CANONICALIZATION_SPEC = (
    "mappluto-geom-canonical-1: raw_digest is 'sha256:' + lowercase-hex "
    "SHA-256 over the EXACT UTF-8 bytes of the HTTP response body "
    "(byte-preserving, order-sensitive, no parsing). "
    "original_geometry_digest is 'sha256:' + lowercase-hex SHA-256 of the "
    "canonical JSON serialization (object keys sorted lexicographically; "
    "separators ',' ':'; numbers per Python json.dumps defaults) of the "
    "VERBATIM esri geometry object exactly as transported (null preserved). "
    "normalized_geometry_digest is 'sha256:' + lowercase-hex SHA-256 of the "
    "UTF-8 bytes of 'mappluto-geom-canonical-1:' + the compact JSON "
    "serialization (separators ',' ':') of the canonical geometry form: a "
    "list of polygons; each polygon a list of rings (first ring exterior, "
    "remaining rings holes); each ring a list of [x, y] coordinate STRING "
    "pairs. Canonical form rules: coordinates rounded half-even to 0.01 ft "
    "(EPSG:2263 US survey feet) and formatted with exactly two decimals "
    "(negative zero normalized to '0.00'); the closing vertex and "
    "consecutive duplicate vertices (post-quantization) are removed so "
    "rings are OPEN vertex cycles; each ring is rotated so its "
    "lexicographically smallest (x, y) string pair comes first; exterior "
    "rings are oriented counterclockwise and holes clockwise (shoelace on "
    "the quantized coordinates); holes within a polygon are sorted by their "
    "serialized form; polygons within a multipolygon are sorted by their "
    "exterior ring's serialized form. Raw, original, and normalized digests "
    "are kept SEPARATELY: raw pins the transported bytes, original pins the "
    "verbatim source geometry, normalized is the deterministic "
    "cross-platform canonical form (default WKB/WKT is deliberately NOT "
    "used). Geometry library pins: shapely "
    f"{PINNED_SHAPELY_VERSION} / GEOS {PINNED_GEOS_VERSION_STRING}."
)

# Geometry assessment states (packet safeguard 3 taxonomy).
GEOMETRY_VALID = "valid"
GEOMETRY_REPAIRED = "repaired"
GEOMETRY_INVALID = "invalid_geometry"
GEOMETRY_REVIEW_REQUIRED = "review_required"

# Lot query outcomes (packet safeguard 1).
OUTCOME_SINGLE = "single_feature"
OUTCOME_NONE = "no_feature"
OUTCOME_MULTIPLE = "multiple_features"

_SAFE_TEXT_RE = re.compile(r"^[A-Za-z0-9 .,:;'\"()\[\]/_%=-]{1,300}$")
_FIELD_NAME_SAFE_RE = re.compile(r"^[A-Za-z0-9_]{1,64}$")
# Retry-After sanitization moved to app.resilience.transport (M2-T011),
# allowlist and repr()-sanitize policy unchanged.


# ---------------------------------------------------------------------------
# Error taxonomy (aligned with M2-T007/M2-T008 naming; adds the
# geometry-channel states wrong_crs and result_mismatch; the geometry
# VALIDITY taxonomy lives on GeometryAssessment.status, not on exceptions,
# because an invalid official geometry is data to report, not a transport
# failure)
# ---------------------------------------------------------------------------


class MapPlutoGeometryConnectorError(Exception):
    """Base typed connector error. Payloads never contain stack traces,
    headers, or tokens (the service is keyless; no token exists)."""

    error_type = "upstream_error"

    def __init__(
        self,
        message: str,
        *,
        correlation_id: str,
        detail: dict | None = None,
    ):
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


class UpstreamError(MapPlutoGeometryConnectorError):
    """Upstream failure: network failure, 5xx persisted through retries,
    unexpected HTTP status, or an ArcGIS error object (delivered even with
    HTTP 200 - live-verified behavior on the DCP_GIS services)."""

    error_type = "upstream_error"


class MalformedResponseError(MapPlutoGeometryConnectorError):
    """Response body is not the well-formed documented shape. NEVER
    converted into a valid empty result."""

    error_type = "malformed_response"


class SchemaDriftError(MapPlutoGeometryConnectorError):
    """Layer contract changed (missing/renamed/re-typed required field,
    missing objectIdField/maxRecordCount, lost paging capability, layer
    rename). Surfaced for alerting; never silently guessed around."""

    error_type = "schema_drift"


class WrongCRSError(MapPlutoGeometryConnectorError):
    """Spatial reference is not the authoritative EPSG:2263 / wkid 102718.
    Raised BEFORE any coordinate is interpreted; also raised by the area
    functions, proving no degrees-based measurement path exists."""

    error_type = "wrong_crs"


class ResultMismatchError(MapPlutoGeometryConnectorError):
    """The service returned a feature that does not correspond to the
    requested lot (BBL attribute missing, unparseable, or different).
    Returned data is never silently trusted."""

    error_type = "result_mismatch"


class SourceTimeoutError(MapPlutoGeometryConnectorError):
    """Connect/read timeout persisted through the retry budget."""

    error_type = "timeout"


class RateLimitedError(MapPlutoGeometryConnectorError):
    """HTTP 429 persisted through the bounded retry budget."""

    error_type = "rate_limited"


class DisallowedRequestError(MapPlutoGeometryConnectorError):
    """Request refused BEFORE any network I/O (the connector builds every
    URL itself from the pinned root and a validated canonical BBL; it is
    not a general HTTP client)."""

    error_type = "disallowed_request"


class RequestBudgetExceededError(MapPlutoGeometryConnectorError):
    """Per-analysis upstream request budget exhausted (M1-T009
    ``AnalysisBudget``); raised BEFORE further upstream I/O and never
    masked by cache or last-known-good fallback."""

    error_type = "budget_exhausted"


class CircuitOpenError(MapPlutoGeometryConnectorError):
    """Fast rejection while the per-source circuit is open; no upstream
    I/O was performed for this call."""

    error_type = "circuit_open"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _rfc3339(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_text(value: object) -> str:
    if isinstance(value, str) and _SAFE_TEXT_RE.match(value):
        return value
    return repr(value)


def _safe_field_name(value: object) -> str:
    if isinstance(value, str) and _FIELD_NAME_SAFE_RE.match(value):
        return value
    return repr(value)


def raw_body_digest(body: str) -> str:
    """Raw-response digest: exact UTF-8 bytes of the transported body
    (MPG_CANONICALIZATION_SPEC). Order-sensitive by design."""
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def _epoch_ms_to_rfc3339(ms: object) -> str | None:
    if isinstance(ms, bool) or not isinstance(ms, int):
        return None
    try:
        return _rfc3339(datetime.fromtimestamp(ms / 1000.0, UTC))
    except (OverflowError, OSError, ValueError):
        return None


def require_authoritative_crs(crs: object, *, correlation_id: str = "crs-check") -> None:
    """The single CRS gate: every coordinate-interpreting code path calls
    this FIRST. Anything but wkid 102718 / latestWkid 2263 (EPSG:2263,
    projected US survey feet) is the typed ``wrong_crs`` failure - there is
    no code path that measures area or distance in degrees."""
    if (
        isinstance(crs, dict)
        and crs.get("wkid") == EXPECTED_WKID
        and crs.get("latest_wkid", crs.get("latestWkid")) == EXPECTED_LATEST_WKID
    ):
        return
    raise WrongCRSError(
        "spatial reference is not the authoritative EPSG:2263 "
        f"(wkid {EXPECTED_WKID} / latestWkid {EXPECTED_LATEST_WKID}); "
        "coordinates in an unexpected CRS are never interpreted and area "
        "is never computed outside the projected-feet CRS",
        correlation_id=correlation_id,
        detail={"spatial_reference": repr(crs)},
    )


# ---------------------------------------------------------------------------
# Canonical geometry form + digests (packet safeguard 5)
# ---------------------------------------------------------------------------


def _fmt_coord(value: float) -> str:
    quantized = round(float(value), COORD_DECIMALS)
    if quantized == 0.0:
        quantized = 0.0  # normalize negative zero
    return f"{quantized:.2f}"


def _ring_to_open_string_cycle(coords: list) -> list[tuple[str, str]] | None:
    """Quantize a closed ring to an OPEN cycle of (x, y) string pairs:
    closing vertex and consecutive post-quantization duplicates removed.
    Returns None when fewer than 3 distinct vertices survive (degenerate at
    canonical precision)."""
    cycle: list[tuple[str, str]] = []
    for point in coords:
        pair = (_fmt_coord(point[0]), _fmt_coord(point[1]))
        if cycle and pair == cycle[-1]:
            continue
        cycle.append(pair)
    if len(cycle) > 1 and cycle[0] == cycle[-1]:
        cycle.pop()
    if len(set(cycle)) < 3:
        return None
    return cycle


def _shoelace_str(cycle: list[tuple[str, str]]) -> float:
    total = 0.0
    for i, (x1s, y1s) in enumerate(cycle):
        x2s, y2s = cycle[(i + 1) % len(cycle)]
        total += float(x1s) * float(y2s) - float(x2s) * float(y1s)
    return total / 2.0


def _canonical_ring(coords: list, *, is_hole: bool) -> list[list[str]] | None:
    """Canonical ring: quantized open cycle, canonical orientation
    (exterior CCW, hole CW), rotated so the lexicographically smallest
    (x, y) pair comes first. None when degenerate at canonical precision."""
    cycle = _ring_to_open_string_cycle(coords)
    if cycle is None:
        return None
    area2 = _shoelace_str(cycle)
    if area2 == 0.0:
        return None
    is_ccw = area2 > 0.0
    if is_hole == is_ccw:  # exterior must be CCW, hole must be CW
        cycle = list(reversed(cycle))
    pivot = min(range(len(cycle)), key=lambda i: cycle[i])
    cycle = cycle[pivot:] + cycle[:pivot]
    return [[x, y] for x, y in cycle]


def _canonicalize_shapely(geom: BaseGeometry) -> list | None:
    """Canonical form of a shapely Polygon/MultiPolygon per
    MPG_CANONICALIZATION_SPEC: list of polygons, each a list of rings
    (exterior first), coordinates as two-decimal strings."""
    if isinstance(geom, Polygon):
        polygons = [geom]
    elif isinstance(geom, MultiPolygon):
        polygons = list(geom.geoms)
    else:
        return None
    canonical_polygons: list[tuple[str, list]] = []
    for polygon in polygons:
        exterior = _canonical_ring(list(polygon.exterior.coords), is_hole=False)
        if exterior is None:
            return None
        holes = []
        for interior in polygon.interiors:
            hole = _canonical_ring(list(interior.coords), is_hole=True)
            if hole is None:
                return None  # degenerate hole at canonical precision
            holes.append(hole)
        holes.sort(key=lambda ring: json.dumps(ring, separators=(",", ":")))
        sort_key = json.dumps(exterior, separators=(",", ":"))
        canonical_polygons.append((sort_key, [exterior, *holes]))
    canonical_polygons.sort(key=lambda pair: pair[0])
    return [polygon for _, polygon in canonical_polygons]


def normalized_geometry_digest(canonical: list) -> str:
    """Digest of the canonical geometry form (MPG_CANONICALIZATION_SPEC)."""
    payload = "mappluto-geom-canonical-1:" + json.dumps(
        canonical, separators=(",", ":")
    )
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def canonical_to_shapely(canonical: list) -> BaseGeometry:
    """Rebuild a shapely geometry from the canonical form (coordinate
    strings become floats; rings are open cycles - shapely closes them)."""
    polygons = []
    for rings in canonical:
        shell = [(float(x), float(y)) for x, y in rings[0]]
        holes = [[(float(x), float(y)) for x, y in ring] for ring in rings[1:]]
        polygons.append(Polygon(shell, holes))
    if len(polygons) == 1:
        return polygons[0]
    return MultiPolygon(polygons)


def compute_area_sq_ft(geom: BaseGeometry, *, crs: dict, correlation_id: str = "area") -> float:
    """Planar area in square feet - ONLY in the validated EPSG:2263
    projected CRS. Any other CRS (including geographic degrees) is the
    typed ``wrong_crs`` refusal; a degrees-based area path does not exist."""
    require_authoritative_crs(crs, correlation_id=correlation_id)
    return float(geom.area)


# ---------------------------------------------------------------------------
# Geometry structural validation + assessment (packet safeguards 3 + 4)
# ---------------------------------------------------------------------------


@dataclass
class GeometryAssessment:
    """Typed geometry-validity record for one lot feature.

    ``status``: ``valid`` | ``repaired`` | ``invalid_geometry`` |
    ``review_required``. ``findings`` are machine-readable condition codes;
    ``repairs`` records every repair applied (method + detail) - repaired
    geometry is NEVER presented as the untouched official source.
    ``original_geometry_digest`` always pins the verbatim source geometry;
    ``normalized_digest`` (canonical form, possibly post-repair) is kept
    SEPARATELY and is None when no safe canonical geometry exists."""

    status: str
    geometry_kind: str | None  # "polygon" | "multipolygon" | None
    findings: list[str]
    repairs: list[dict]
    original_geometry_digest: str
    normalized_digest: str | None
    canonical_geometry: list | None
    exterior_ring_count: int
    hole_count: int
    vertex_count: int
    area_sq_ft: float | None
    area_crs: dict
    shapely_version: str
    geos_version: str
    digest_canonicalization: str = MPG_CANONICALIZATION_SPEC

    @property
    def repaired(self) -> bool:
        return self.status == GEOMETRY_REPAIRED


def _add_finding(findings: list[str], code: str) -> None:
    if code not in findings:
        findings.append(code)


def _structural_rings(
    geometry: object, findings: list[str], repairs: list[dict]
) -> list[list[list[float]]] | None:
    """Structurally validate the esri geometry object and return closed
    rings of [x, y] floats, applying only the two deterministic,
    fully-characterized structural repairs (ring closure, consecutive
    duplicate removal). Returns None when no polygon interpretation exists;
    the findings list carries the typed reasons."""
    if geometry is None:
        _add_finding(findings, "null_geometry")
        return None
    if not isinstance(geometry, dict):
        _add_finding(findings, "malformed_geometry_object")
        return None
    if "rings" not in geometry:
        if any(key in geometry for key in ("paths", "points", "x", "y")):
            # esriGeometryPolyline/Point payload where the layer contracts
            # polygons: a geometry-collection surprise, typed visibly.
            _add_finding(findings, "geometry_collection")
        else:
            _add_finding(findings, "malformed_geometry_object")
        return None
    rings = geometry["rings"]
    if not isinstance(rings, list):
        _add_finding(findings, "malformed_geometry_object")
        return None
    if not rings:
        _add_finding(findings, "empty_geometry")
        return None
    structural: list[list[list[float]]] = []
    for ring in rings:
        if not isinstance(ring, list) or len(ring) < 2:
            _add_finding(findings, "malformed_geometry_object")
            return None
        points: list[list[float]] = []
        for vertex in ring:
            if (
                not isinstance(vertex, list | tuple)
                or len(vertex) < 2
                or any(
                    isinstance(component, bool)
                    or not isinstance(component, int | float)
                    for component in vertex[:2]
                )
            ):
                _add_finding(findings, "malformed_geometry_object")
                return None
            x, y = float(vertex[0]), float(vertex[1])
            if not (math.isfinite(x) and math.isfinite(y)):
                _add_finding(findings, "nonfinite_coordinate")
                return None
            points.append([x, y])
        # Deterministic structural repair 1: drop exact consecutive
        # duplicate vertices (fully characterized: the vertex cycle is
        # unchanged as a point set and the ring area is unchanged).
        deduped: list[list[float]] = []
        removed = 0
        for point in points:
            if deduped and point == deduped[-1]:
                removed += 1
                continue
            deduped.append(point)
        if removed:
            _add_finding(findings, "duplicate_vertices")
            repairs.append(
                {
                    "method": "drop_consecutive_duplicate_vertices",
                    "detail": f"removed {removed} exact consecutive duplicate vertex(es)",
                }
            )
        # Deterministic structural repair 2: close an open ring by
        # repeating the first vertex (fully characterized: esri rings are
        # closed by contract; the intended cycle is unambiguous).
        if deduped[0] != deduped[-1]:
            _add_finding(findings, "unclosed_ring")
            repairs.append(
                {
                    "method": "ring_closure",
                    "detail": "appended the first vertex to close the ring",
                }
            )
            deduped.append(list(deduped[0]))
        structural.append(deduped)
    return structural


def _shoelace(ring: list[list[float]]) -> float:
    """Signed shoelace area x2 of a CLOSED ring (positive = CCW)."""
    total = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]
        total += x1 * y2 - x2 * y1
    return total / 2.0


_KNOWN_VALIDITY_FRAGMENTS = (
    ("self-intersection", "self_intersection"),
    ("ring self-intersection", "self_intersection"),
    ("duplicate rings", "duplicate_vertices"),
    ("too few points", "degenerate_ring"),
)


def _classify_validity_reason(reason: str, findings: list[str]) -> bool:
    """Map a GEOS explain_validity reason to a taxonomy finding. Returns
    True when the pathology is a KNOWN, characterizable class (repair may
    proceed); False routes the assessment to review_required."""
    lowered = reason.lower()
    for fragment, code in _KNOWN_VALIDITY_FRAGMENTS:
        if fragment in lowered:
            _add_finding(findings, code)
            return True
    if "hole" in lowered or "shell" in lowered or "nested" in lowered:
        _add_finding(findings, "invalid_orientation")
        return False
    _add_finding(findings, f"validity:{_safe_text(reason)}")
    return False


def analyze_lot_geometry(
    esri_geometry: object,
    *,
    crs: dict,
    correlation_id: str = "geometry-analysis",
) -> GeometryAssessment:
    """Assess one esri polygon geometry against the validity taxonomy
    (packet safeguard 3) under the no-silent-repair policy (safeguard 4).

    The CRS gate runs FIRST: coordinates are never interpreted, and area is
    never computed, outside the validated EPSG:2263 projected-feet CRS
    (raises the typed ``wrong_crs`` failure otherwise).

    Pipeline: structural validation (null/empty/collection/non-finite ->
    ``invalid_geometry``) -> deterministic structural repairs (ring
    closure, consecutive-duplicate removal - each recorded) -> esri ring
    role assignment (clockwise = exterior, counterclockwise = hole;
    zero-area rings are degenerate) -> shapely construction -> GEOS
    validity check -> characterized ``make_valid`` repair for KNOWN
    pathologies only (recorded with library versions and area before/after)
    -> canonical form + separate digests. Uncharacterizable topology
    (inverted orientation, hole outside every shell, unknown validity
    pathology, non-polygonal repair output, repair area drift beyond
    {MAX_REPAIR_AREA_REL_DRIFT:.0%}) is the explicit ``review_required``
    state - never a silent fix.
    """
    require_authoritative_crs(crs, correlation_id=correlation_id)
    findings: list[str] = []
    repairs: list[dict] = []
    original_digest = canonical_json_digest(esri_geometry)

    def _result(
        status: str,
        *,
        geometry_kind: str | None = None,
        canonical: list | None = None,
        exterior_ring_count: int = 0,
        hole_count: int = 0,
        vertex_count: int = 0,
        area: float | None = None,
    ) -> GeometryAssessment:
        return GeometryAssessment(
            status=status,
            geometry_kind=geometry_kind,
            findings=findings,
            repairs=repairs,
            original_geometry_digest=original_digest,
            normalized_digest=(
                normalized_geometry_digest(canonical) if canonical is not None else None
            ),
            canonical_geometry=canonical,
            exterior_ring_count=exterior_ring_count,
            hole_count=hole_count,
            vertex_count=vertex_count,
            area_sq_ft=area,
            area_crs=dict(CRS_STAMP),
            shapely_version=shapely.__version__,
            geos_version=shapely.geos_version_string,
        )

    rings = _structural_rings(esri_geometry, findings, repairs)
    if rings is None:
        return _result(GEOMETRY_INVALID)

    # esri ring roles: clockwise (negative shoelace) = exterior,
    # counterclockwise = hole; zero area = degenerate.
    exteriors: list[list[list[float]]] = []
    holes: list[list[list[float]]] = []
    degenerate = 0
    for ring in rings:
        distinct = {tuple(point) for point in ring[:-1]}
        if len(distinct) < 3:
            degenerate += 1
            continue
        area2 = _shoelace(ring)
        if area2 == 0.0:
            hull_area = Polygon([(x, y) for x, y in ring]).convex_hull.area
            if hull_area == 0.0:
                degenerate += 1  # collinear: genuinely zero-extent ring
                continue
            # Zero SIGNED area but non-zero extent: a self-crossing ring
            # whose lobes cancel (classic bowtie). Orientation is
            # meaningless here; treat as an exterior candidate and let the
            # GEOS validity check type the self-intersection downstream.
            exteriors.append(ring)
            continue
        if area2 < 0.0:
            exteriors.append(ring)
        else:
            holes.append(ring)
    if degenerate:
        _add_finding(findings, "degenerate_ring")
        if degenerate == len(rings):
            return _result(GEOMETRY_INVALID)
        # Fully characterized repair: a zero-area ring contributes nothing
        # to the polygonal area; dropping it changes no measurement.
        repairs.append(
            {
                "method": "drop_degenerate_ring",
                "detail": (
                    f"removed {degenerate} zero-area/degenerate ring(s); "
                    "polygonal area unchanged"
                ),
            }
        )
    if not exteriors:
        # Only counterclockwise rings: the esri orientation convention is
        # inverted and the producer's intent (exterior vs hole) cannot be
        # safely characterized. Explicit review_required - never guessed.
        _add_finding(findings, "invalid_orientation")
        return _result(GEOMETRY_REVIEW_REQUIRED)

    shells = [Polygon([(x, y) for x, y in ring]) for ring in exteriors]
    hole_assignment: dict[int, list[list[list[float]]]] = {
        i: [] for i in range(len(shells))
    }
    for hole in holes:
        representative = Point(*Polygon([(x, y) for x, y in hole]).representative_point().coords[0])
        containing = [
            i for i, shell in enumerate(shells) if shell.contains(representative)
        ]
        if not containing:
            _add_finding(findings, "invalid_orientation")
            return _result(GEOMETRY_REVIEW_REQUIRED)
        # Nested shells: assign the hole to the smallest containing shell
        # (deterministic; standard even-odd interpretation).
        best = min(containing, key=lambda i: shells[i].area)
        hole_assignment[best].append(hole)

    polygons = [
        Polygon(
            [(x, y) for x, y in exteriors[i]],
            [[(x, y) for x, y in hole] for hole in hole_assignment[i]],
        )
        for i in range(len(exteriors))
    ]
    geom: BaseGeometry = polygons[0] if len(polygons) == 1 else MultiPolygon(polygons)
    geometry_kind = "polygon" if len(polygons) == 1 else "multipolygon"
    vertex_count = sum(len(ring) - 1 for ring in rings)

    if not geom.is_valid:
        reason = explain_validity(geom)
        characterizable = _classify_validity_reason(reason, findings)
        if not characterizable:
            return _result(
                GEOMETRY_REVIEW_REQUIRED,
                geometry_kind=geometry_kind,
                exterior_ring_count=len(exteriors),
                hole_count=len(holes),
                vertex_count=vertex_count,
            )
        area_before = float(geom.area)
        try:
            repaired_geom = make_valid(geom)
        except Exception:  # GEOS failure: uncharacterizable
            _add_finding(findings, "repair_failed")
            return _result(
                GEOMETRY_REVIEW_REQUIRED,
                geometry_kind=geometry_kind,
                exterior_ring_count=len(exteriors),
                hole_count=len(holes),
                vertex_count=vertex_count,
            )
        dropped_types: list[str] = []
        if repaired_geom.geom_type == "GeometryCollection":
            polygonal = [
                part
                for part in repaired_geom.geoms
                if isinstance(part, Polygon | MultiPolygon)
            ]
            dropped_types = sorted(
                {
                    part.geom_type
                    for part in repaired_geom.geoms
                    if not isinstance(part, Polygon | MultiPolygon)
                }
            )
            merged: list[Polygon] = []
            for part in polygonal:
                merged.extend(
                    part.geoms if isinstance(part, MultiPolygon) else [part]
                )
            if not merged:
                _add_finding(findings, "geometry_collection")
                return _result(
                    GEOMETRY_REVIEW_REQUIRED,
                    geometry_kind=geometry_kind,
                    exterior_ring_count=len(exteriors),
                    hole_count=len(holes),
                    vertex_count=vertex_count,
                )
            repaired_geom = merged[0] if len(merged) == 1 else MultiPolygon(merged)
        if repaired_geom.is_empty or not isinstance(
            repaired_geom, Polygon | MultiPolygon
        ):
            return _result(
                GEOMETRY_REVIEW_REQUIRED,
                geometry_kind=geometry_kind,
                exterior_ring_count=len(exteriors),
                hole_count=len(holes),
                vertex_count=vertex_count,
            )
        area_after = float(repaired_geom.area)
        # A characterizable repair must not silently change the measured
        # area beyond tolerance UNLESS the invalid input's area was itself
        # meaningless (GEOS area of self-intersecting rings is the signed
        # lobe difference); both areas are recorded either way.
        if (
            area_before > 0.0
            and abs(area_after - area_before) / max(area_before, area_after)
            > MAX_REPAIR_AREA_REL_DRIFT
            and "self_intersection" not in findings
        ):
            _add_finding(findings, "repair_area_drift")
            return _result(
                GEOMETRY_REVIEW_REQUIRED,
                geometry_kind=geometry_kind,
                exterior_ring_count=len(exteriors),
                hole_count=len(holes),
                vertex_count=vertex_count,
            )
        repairs.append(
            {
                "method": "shapely_make_valid",
                "detail": (
                    f"GEOS validity reason: {_safe_text(reason)}; "
                    f"area_before_sq_ft={area_before!r}, "
                    f"area_after_sq_ft={area_after!r}"
                    + (
                        f"; dropped non-polygonal parts: {dropped_types}"
                        if dropped_types
                        else ""
                    )
                ),
                "shapely_version": shapely.__version__,
                "geos_version": shapely.geos_version_string,
            }
        )
        geom = repaired_geom
        geometry_kind = "polygon" if isinstance(geom, Polygon) else "multipolygon"

    canonical = _canonicalize_shapely(geom)
    if canonical is None:
        _add_finding(findings, "degenerate_ring")
        return _result(
            GEOMETRY_REVIEW_REQUIRED,
            geometry_kind=geometry_kind,
            exterior_ring_count=len(exteriors),
            hole_count=len(holes),
            vertex_count=vertex_count,
        )
    status = GEOMETRY_REPAIRED if repairs else GEOMETRY_VALID
    final_polygons = [geom] if isinstance(geom, Polygon) else list(geom.geoms)
    return _result(
        status,
        geometry_kind="polygon" if len(final_polygons) == 1 else "multipolygon",
        canonical=canonical,
        exterior_ring_count=len(final_polygons),
        hole_count=sum(len(p.interiors) for p in final_polygons),
        vertex_count=vertex_count,
        area=compute_area_sq_ft(geom, crs=CRS_STAMP, correlation_id=correlation_id),
    )


# ---------------------------------------------------------------------------
# Spatial-readiness classifier (packet safeguard 6 - TEST-level diagnostic)
# ---------------------------------------------------------------------------


def classify_spatial_relation(
    subject_canonical: list,
    reference_canonical: list,
    *,
    tolerance_ft: float = BOUNDARY_TOLERANCE_FT,
) -> dict:
    """TEST-LEVEL diagnostic classifying a lot geometry against a reference
    polygon (e.g. an M2-T007 zoning-district feature), proving the
    normalized geometry is intersection-ready. NOT the production
    spatial-intersection engine (explicitly out of scope per the M2-T009
    packet); no legal zoning assignment is made here.

    Named tolerance behavior: ``tolerance_ft`` defaults to
    ``BOUNDARY_TOLERANCE_FT`` (20 ft), the official source's stated
    plus-or-minus horizontal accuracy. Relations:

    - ``inside``: the subject lies within the reference eroded by the
      tolerance (inside beyond any plausible boundary error).
    - ``outside``: the subject is farther than the tolerance from the
      reference (outside beyond any plausible boundary error).
    - ``split_intersection``: parts of the subject are firmly inside AND
      firmly outside (both beyond tolerance) - a genuine split.
    - ``boundary_uncertain``: everything else (touches, overlaps, or
      containment within the tolerance band). An ambiguous boundary case is
      NEVER silently classified as inside or outside.
    """
    subject = canonical_to_shapely(subject_canonical)
    reference = canonical_to_shapely(reference_canonical)
    eroded = reference.buffer(-tolerance_ft)
    dilated = reference.buffer(tolerance_ft)
    distance_ft = float(subject.distance(reference))
    intersection_area = float(subject.intersection(reference).area)
    if not eroded.is_empty and subject.within(eroded):
        relation = "inside"
    elif distance_ft > tolerance_ft:
        relation = "outside"
    elif (
        subject.intersection(eroded).area > 0.0
        and subject.difference(dilated).area > 0.0
    ):
        relation = "split_intersection"
    else:
        relation = "boundary_uncertain"
    return {
        "relation": relation,
        "tolerance_ft": tolerance_ft,
        "tolerance_basis": (
            "official source states plus-or-minus 20 ft horizontal accuracy "
            "(zoning-features research section 4.3); within-tolerance "
            "results are uncertain by the source's own accuracy statement"
        ),
        "subject_area_sq_ft": float(subject.area),
        "intersection_area_sq_ft": intersection_area,
        "distance_ft": distance_ft,
        "crs": dict(CRS_STAMP),
    }


# ---------------------------------------------------------------------------
# URL construction (all URLs originate here; byte-identical to the fixture
# capture URLs so tests can assert reproduction)
# ---------------------------------------------------------------------------


def build_metadata_url() -> str:
    return f"{SERVICE_ROOT}/{LAYER_NAME}/FeatureServer/0?f=json"


def build_lot_query_url(
    canonical_bbl: str, *, correlation_id: str = "urlbuild"
) -> str:
    """The ONLY query URL this connector emits: an exact-BBL equality
    filter with the bounded out-field set, deterministic ordering, and a
    bounded record count. The BBL segment comes exclusively from
    ``normalize_bbl`` output; callers can never supply URLs, hosts, raw
    where clauses, field lists, or paging values."""
    normalized = normalize_bbl(canonical_bbl)
    if normalized.canonical != canonical_bbl:
        raise DisallowedRequestError(
            "build_lot_query_url requires the canonical 10-digit BBL form",
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
        "&f=json"
    )


# ---------------------------------------------------------------------------
# Transport request with bounded retry. Task M2-T011 (the owner-sequenced
# shared-transport consolidation): the accepted control flow now runs in the
# shared engine (app.resilience.transport.request_with_retry) with the
# M1-T009 jitter/Retry-After delay policy; the connector-specific error
# taxonomy and messages stay here through the RetryHooks seam.
# ---------------------------------------------------------------------------


def _request_with_retry(
    url: str,
    *,
    transport: Transport,
    timeout: float,
    max_attempts: int,
    backoff_base: float,
    backoff_cap: float,
    retry_after_cap: float,
    rng: Random,
    sleep: Callable[[float], None],
    wall_clock: Callable[[], datetime],
    correlation_id: str,
    budget: AnalysisBudget | None,
) -> TransportResponse:
    """Bounded retry on 429/5xx/timeout/network failure ONLY. Non-5xx
    unexpected statuses and every parse or drift condition are never
    retried. One budget unit per upstream ATTEMPT, consumed BEFORE I/O."""

    return request_with_retry(
        url,
        transport=transport,
        headers={"Accept": "application/json"},
        timeout=timeout,
        max_attempts=max_attempts,
        hooks=standard_retry_hooks(
            logger=logger,
            log_label="mappluto_geometry",
            correlation_id=correlation_id,
            url=url,
            sanitize_network_reason=_safe_text,
            rate_limited_error=RateLimitedError,
            rate_limited_message=(
                "official ArcGIS service throttled the request (HTTP 429) and "
                "the retry budget is exhausted"
            ),
            timeout_error=SourceTimeoutError,
            timeout_message="ArcGIS request timed out and the retry budget is exhausted",
            unavailable_error=UpstreamError,
            unavailable_message=(
                "official ArcGIS service unavailable and the retry budget is exhausted"
            ),
            include_reason_kind=True,
            unexpected_status_message=(
                "unexpected HTTP status {status} from the official ArcGIS service"
            ),
            budget_error=RequestBudgetExceededError,
        ),
        compute_delay=jittered_retry_after_delay(
            backoff_base=backoff_base,
            backoff_cap=backoff_cap,
            retry_after_cap=retry_after_cap,
            rng=rng,
            wall_clock=wall_clock,
        ),
        sleep=sleep,
        budget=budget,
    )


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------


def _parse_json_object(body: str, *, url: str, correlation_id: str) -> dict:
    """Parse a response body into a JSON object; classify the ArcGIS
    error-object-with-HTTP-200 as a typed UPSTREAM error, and everything
    unparseable as malformed_response (never a valid empty result)."""
    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise MalformedResponseError(
            "ArcGIS returned HTTP 200 with a body that is not valid JSON; "
            "refusing to interpret it (never an empty result)",
            correlation_id=correlation_id,
            detail={"url": url, "parse_error": type(exc).__name__},
        ) from exc
    if not isinstance(parsed, dict):
        raise MalformedResponseError(
            "ArcGIS response is not a JSON object",
            correlation_id=correlation_id,
            detail={"url": url, "body_type": type(parsed).__name__},
        )
    error = parsed.get("error")
    if error is not None:
        code = error.get("code") if isinstance(error, dict) else None
        message = error.get("message") if isinstance(error, dict) else None
        raise UpstreamError(
            "ArcGIS returned an error object (an error delivered with "
            "HTTP 200 is an upstream error, not data)",
            correlation_id=correlation_id,
            detail={
                "url": url,
                "arcgis_error_code": code if isinstance(code, int) else repr(code),
                "arcgis_error_message": _safe_text(message),
            },
        )
    return parsed


# ---------------------------------------------------------------------------
# Result contracts
# ---------------------------------------------------------------------------


@dataclass
class MapPlutoLayerMetadata:
    """Validated MAPPLUTO layer-0 metadata snapshot with provenance."""

    correlation_id: str
    request_url: str
    retrieved_at: str
    object_id_field: str
    fields: dict[str, str]
    geometry_type: str
    wkid: int
    latest_wkid: int
    max_record_count: int
    supports_pagination: bool
    supports_order_by: bool
    source_data_last_edited_ms: int | None
    source_data_last_edited: str | None
    raw_digest: str
    drift_signals: list[str] = field(default_factory=list)


@dataclass
class LotGeometryResult:
    """Per-BBL lot-geometry result. ``outcome`` is one of
    ``single_feature`` / ``no_feature`` / ``multiple_features`` - always an
    explicit typed state, never a silent first-pick. ``staleness`` is
    transport/cache serve state ONLY (two-staleness rule) and is None on
    every fresh retrieval this module performs; ``source_data_last_edited``
    is source-dataset provenance and never sets staleness."""

    status: str  # always "ok" for well-formed responses
    outcome: str
    review_required: bool
    requested_bbl: str
    borough: int
    block: int
    lot: int
    condo: dict
    identifier_conflicts: list[dict]
    attributes: dict | None
    features: list[dict]
    geometry: GeometryAssessment | None
    area_sq_ft: float | None
    shape_area_attribute_sq_ft: float | None
    exceeded_transfer_limit: bool
    correlation_id: str
    request_url: str
    metadata_request_url: str
    retrieved_at: str
    crs: dict
    source_data_last_edited_ms: int | None
    source_data_last_edited: str | None
    raw_digest: str
    metadata_raw_digest: str
    normalized_digest: str
    digest_canonicalization: str
    shapely_version: str
    geos_version: str
    drift_signals: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    staleness: dict | None = None


# ---------------------------------------------------------------------------
# Public operations (plain, fixture-testable, offline-deterministic)
# ---------------------------------------------------------------------------


def fetch_layer_metadata(
    *,
    transport: Transport = urllib_transport,
    timeout: float = 30.0,
    max_attempts: int = 3,
    backoff_base: float = 0.5,
    backoff_cap: float = 30.0,
    retry_after_cap: float = 120.0,
    rng: Random | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = _utc_now,
    correlation_id: str | None = None,
    budget: AnalysisBudget | None = None,
) -> MapPlutoLayerMetadata:
    """Fetch and VALIDATE MAPPLUTO layer-0 metadata. Typed failures:
    ``wrong_crs`` on a non-authoritative spatial reference (BEFORE any
    coordinate interpretation), ``schema_drift`` on missing objectIdField,
    missing/re-typed required fields, missing/invalid maxRecordCount, lost
    pagination/order-by capability, wrong geometry type, or layer rename.
    Missing editingInfo degrades visibly (drift signal), never silently."""
    correlation_id = correlation_id or uuid.uuid4().hex
    url = build_metadata_url()
    response = _request_with_retry(
        url,
        transport=transport,
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        backoff_cap=backoff_cap,
        retry_after_cap=retry_after_cap,
        rng=rng or Random(),
        sleep=sleep,
        wall_clock=clock,
        correlation_id=correlation_id,
        budget=budget,
    )
    retrieved_at = _rfc3339(clock())
    doc = _parse_json_object(response.body, url=url, correlation_id=correlation_id)
    drift_signals: list[str] = []

    name = doc.get("name")
    if name != LAYER_NAME:
        raise SchemaDriftError(
            "service metadata 'name' does not match the canonical MAPPLUTO layer",
            correlation_id=correlation_id,
            detail={"url": url, "name": _safe_text(name)},
        )

    sr = (
        (doc.get("extent") or {}).get("spatialReference")
        if isinstance(doc.get("extent"), dict)
        else None
    )
    if (
        not isinstance(sr, dict)
        or sr.get("wkid") != EXPECTED_WKID
        or sr.get("latestWkid") != EXPECTED_LATEST_WKID
    ):
        raise WrongCRSError(
            "layer spatial reference is not the authoritative EPSG:2263 "
            f"(wkid {EXPECTED_WKID} / latestWkid {EXPECTED_LATEST_WKID}); "
            "geometry in an unexpected CRS must not be consumed",
            correlation_id=correlation_id,
            detail={"url": url, "spatial_reference": repr(sr)},
        )

    geometry_type = doc.get("geometryType")
    if geometry_type != EXPECTED_GEOMETRY_TYPE:
        raise SchemaDriftError(
            f"geometryType is not {EXPECTED_GEOMETRY_TYPE}",
            correlation_id=correlation_id,
            detail={"url": url, "geometry_type": _safe_text(geometry_type)},
        )

    object_id_field = doc.get("objectIdField")
    if not isinstance(object_id_field, str) or not _FIELD_NAME_SAFE_RE.match(
        object_id_field
    ):
        raise SchemaDriftError(
            "layer metadata has no usable objectIdField; deterministic "
            "ordering cannot be established - refusing to guess",
            correlation_id=correlation_id,
            detail={"url": url, "object_id_field": repr(object_id_field)},
        )

    raw_fields = doc.get("fields")
    if not isinstance(raw_fields, list):
        raise SchemaDriftError(
            "layer metadata has no fields array",
            correlation_id=correlation_id,
            detail={"url": url},
        )
    live_fields: dict[str, str] = {}
    for entry in raw_fields:
        if isinstance(entry, dict) and isinstance(entry.get("name"), str):
            live_fields[entry["name"]] = str(entry.get("type"))
    missing = sorted(set(REQUIRED_FIELDS) - set(live_fields))
    if missing:
        raise SchemaDriftError(
            "required field(s) missing from the live MAPPLUTO schema "
            "(renamed or removed) - never silently guessed",
            correlation_id=correlation_id,
            detail={"url": url, "missing_fields": missing},
        )
    retyped = sorted(
        name
        for name in REQUIRED_FIELDS
        if live_fields[name] != REQUIRED_FIELDS[name]
    )
    if retyped:
        raise SchemaDriftError(
            "required field type(s) changed in the live MAPPLUTO schema",
            correlation_id=correlation_id,
            detail={
                "url": url,
                "retyped": {
                    name: {
                        "expected": REQUIRED_FIELDS[name],
                        "actual": live_fields[name],
                    }
                    for name in retyped
                },
            },
        )
    if object_id_field not in REQUIRED_FIELDS:
        raise SchemaDriftError(
            "objectIdField is not part of the required field contract",
            correlation_id=correlation_id,
            detail={"url": url, "object_id_field": object_id_field},
        )

    max_record_count = doc.get("maxRecordCount")
    if (
        isinstance(max_record_count, bool)
        or not isinstance(max_record_count, int)
        or max_record_count < 1
    ):
        raise SchemaDriftError(
            "maxRecordCount missing or invalid; bounded querying cannot be "
            "planned safely without the official transfer limit",
            correlation_id=correlation_id,
            detail={"url": url, "max_record_count": repr(max_record_count)},
        )

    capabilities = doc.get("advancedQueryCapabilities")
    supports_pagination = bool(
        isinstance(capabilities, dict)
        and capabilities.get("supportsPagination") is True
    )
    supports_order_by = bool(
        isinstance(capabilities, dict) and capabilities.get("supportsOrderBy") is True
    )
    if not supports_pagination or not supports_order_by:
        raise SchemaDriftError(
            "layer no longer advertises supportsPagination/supportsOrderBy; "
            "deterministic ordered queries are impossible - refusing to "
            "fall back to unordered reads",
            correlation_id=correlation_id,
            detail={
                "url": url,
                "supports_pagination": supports_pagination,
                "supports_order_by": supports_order_by,
            },
        )

    editing = doc.get("editingInfo")
    data_last_edited_ms: int | None = None
    if (
        isinstance(editing, dict)
        and not isinstance(editing.get("dataLastEditDate"), bool)
        and isinstance(editing.get("dataLastEditDate"), int)
    ):
        data_last_edited_ms = editing["dataLastEditDate"]
    else:
        # Provenance-only signal: freshness stamp unavailable. Visible
        # degradation, not fatal (the data itself is still validated).
        drift_signals.append("missing_editing_info")
    data_last_edited = _epoch_ms_to_rfc3339(data_last_edited_ms)

    logger.info(
        "mappluto_geometry metadata ok max_record_count=%d data_last_edited=%s "
        "drift_signals=%d correlation_id=%s",
        max_record_count, data_last_edited, len(drift_signals), correlation_id,
    )
    return MapPlutoLayerMetadata(
        correlation_id=correlation_id,
        request_url=url,
        retrieved_at=retrieved_at,
        object_id_field=object_id_field,
        fields=live_fields,
        geometry_type=geometry_type,
        wkid=EXPECTED_WKID,
        latest_wkid=EXPECTED_LATEST_WKID,
        max_record_count=max_record_count,
        supports_pagination=supports_pagination,
        supports_order_by=supports_order_by,
        source_data_last_edited_ms=data_last_edited_ms,
        source_data_last_edited=data_last_edited,
        raw_digest=raw_body_digest(response.body),
        drift_signals=drift_signals,
    )


def _validate_query_envelope(
    doc: dict,
    *,
    url: str,
    object_id_field: str,
    correlation_id: str,
    drift_signals: list[str],
) -> tuple[list[tuple[int, dict]], bool]:
    """Validate a query-response envelope; return ``[(object_id, feature)]``
    in RESPONSE order plus the ``exceededTransferLimit`` flag. A well-formed
    empty ``features`` array is a VALID empty result; every malformed shape
    is a typed failure - never coerced. A non-authoritative response
    spatial reference is the typed ``wrong_crs`` failure BEFORE any
    geometry is interpreted."""
    if "features" not in doc:
        raise MalformedResponseError(
            "query response has no 'features' key; a malformed response is "
            "never a valid empty result",
            correlation_id=correlation_id,
            detail={"url": url, "keys": sorted(map(_safe_text, doc.keys()))},
        )
    features = doc["features"]
    if not isinstance(features, list):
        raise MalformedResponseError(
            "'features' is not a JSON array",
            correlation_id=correlation_id,
            detail={"url": url, "features_type": type(features).__name__},
        )
    response_oid_field = doc.get("objectIdFieldName")
    if isinstance(response_oid_field, str) and response_oid_field != object_id_field:
        raise SchemaDriftError(
            "response objectIdFieldName differs from the validated layer "
            "objectIdField",
            correlation_id=correlation_id,
            detail={
                "url": url,
                "expected": object_id_field,
                "actual": _safe_field_name(response_oid_field),
            },
        )
    sr = doc.get("spatialReference")
    if sr is not None:
        if (
            not isinstance(sr, dict)
            or sr.get("wkid") != EXPECTED_WKID
            or sr.get("latestWkid") != EXPECTED_LATEST_WKID
        ):
            raise WrongCRSError(
                "query response spatial reference is not the authoritative "
                f"EPSG:2263 (wkid {EXPECTED_WKID} / latestWkid "
                f"{EXPECTED_LATEST_WKID}); refusing before geometry "
                "interpretation",
                correlation_id=correlation_id,
                detail={"url": url, "spatial_reference": repr(sr)},
            )
    elif features:
        # Live service includes spatialReference whenever features are
        # present (absent only on empty results, fixture MPG03). Visible
        # degradation; the validated LAYER metadata CRS still governs.
        drift_signals.append("page_missing_spatial_reference")
    extracted: list[tuple[int, dict]] = []
    seen: set[int] = set()
    for index, feature in enumerate(features):
        if not isinstance(feature, dict) or not isinstance(
            feature.get("attributes"), dict
        ):
            raise MalformedResponseError(
                "feature is not an object with an 'attributes' map",
                correlation_id=correlation_id,
                detail={"url": url, "feature_index": index},
            )
        attributes = feature["attributes"]
        oid = attributes.get(object_id_field)
        if isinstance(oid, bool) or not isinstance(oid, int):
            raise MalformedResponseError(
                f"feature attributes lack an integer '{object_id_field}'",
                correlation_id=correlation_id,
                detail={"url": url, "feature_index": index},
            )
        if oid in seen:
            raise MalformedResponseError(
                "response repeats an object id within one bounded query",
                correlation_id=correlation_id,
                detail={"url": url, "object_id": oid},
            )
        seen.add(oid)
        for name in attributes:
            if name not in REQUIRED_FIELDS:
                signal = f"unknown_attribute:{_safe_field_name(name)}"
                if signal not in drift_signals:
                    drift_signals.append(signal)
        extracted.append((oid, feature))
    return extracted, doc.get("exceededTransferLimit") is True


def _attr_bbl_as_int(value: object) -> int | None:
    """Parse the numeric BBL attribute (esriFieldTypeDouble) to an int, or
    None when unparseable. Booleans and non-integral floats are refused."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _condo_classification(normalized: NormalizedBBL, attributes: dict | None) -> dict:
    """Condominium semantics per research section 2.5 (official
    meta_mappluto.pdf, G1-verified): explicit, never a per-unit claim."""
    lot = normalized.lot
    condo_no = attributes.get("CondoNo") if attributes else None
    if CONDO_BILLING_LOT_MIN <= lot <= CONDO_BILLING_LOT_MAX:
        return {
            "classification": "condo_billing_lot",
            "condo_no": condo_no,
            "note": (
                "lot number in the condominium BILLING range (7501-7599): "
                "this polygon represents the entire condominium complex "
                "(base lots merged, FKA behavior per research section 2.5), "
                "NOT any individual unit; per-unit tax-lot polygons do not "
                "exist in MapPLUTO"
            ),
        }
    if CONDO_UNIT_LOT_MIN <= lot <= CONDO_UNIT_LOT_MAX:
        return {
            "classification": "condo_unit_lot_query",
            "condo_no": condo_no,
            "note": (
                "lot number in the condominium UNIT range (1001-6999): "
                "MapPLUTO carries ONE record per condominium complex under "
                "the billing lot, so unit lots have no polygon of their own "
                "(research section 2.5); resolve the billing BBL (e.g. via "
                "Geoclient condominiumBillingBbl) and query that instead"
            ),
        }
    return {
        "classification": "standard_lot",
        "condo_no": condo_no,
        "note": (
            "condominium association indicated by CondoNo despite a lot "
            "number outside the documented unit/billing ranges; semantics "
            "per research section 2.5 apply to the complex record"
            if condo_no is not None
            else None
        ),
    }


def fetch_lot_geometry(
    bbl: object,
    *,
    metadata: MapPlutoLayerMetadata | None = None,
    transport: Transport = urllib_transport,
    timeout: float = 30.0,
    max_attempts: int = 3,
    backoff_base: float = 0.5,
    backoff_cap: float = 30.0,
    retry_after_cap: float = 120.0,
    rng: Random | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = _utc_now,
    correlation_id: str | None = None,
    budget: AnalysisBudget | None = None,
) -> LotGeometryResult:
    """Fetch the official tax-lot geometry for one BBL (packet safeguards
    1-5). ``bbl`` is validated via ``normalize_bbl`` BEFORE any I/O
    (``BBLValidationError`` propagates for malformed input). When
    ``metadata`` is not injected it is fetched (and fully validated,
    including the CRS gate) first."""
    correlation_id = correlation_id or uuid.uuid4().hex
    normalized = normalize_bbl(bbl)
    common = dict(
        transport=transport,
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        backoff_cap=backoff_cap,
        retry_after_cap=retry_after_cap,
        rng=rng or Random(),
        sleep=sleep,
        correlation_id=correlation_id,
        budget=budget,
    )
    if metadata is None:
        metadata = fetch_layer_metadata(clock=clock, **common)
    url = build_lot_query_url(normalized.canonical, correlation_id=correlation_id)
    response = _request_with_retry(
        url,
        transport=transport,
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        backoff_cap=backoff_cap,
        retry_after_cap=retry_after_cap,
        rng=common["rng"],
        sleep=sleep,
        wall_clock=clock,
        correlation_id=correlation_id,
        budget=budget,
    )
    retrieved_at = _rfc3339(clock())
    doc = _parse_json_object(response.body, url=url, correlation_id=correlation_id)
    drift_signals = list(metadata.drift_signals)
    pairs, exceeded = _validate_query_envelope(
        doc,
        url=url,
        object_id_field=metadata.object_id_field,
        correlation_id=correlation_id,
        drift_signals=drift_signals,
    )
    pairs.sort(key=lambda pair: pair[0])
    normalized_features = [
        {
            "object_id": oid,
            "attributes": feature["attributes"],
            "geometry": feature.get("geometry"),
        }
        for oid, feature in pairs
    ]
    notes: list[str] = []
    identifier_conflicts: list[dict] = []
    attributes: dict | None = None
    assessment: GeometryAssessment | None = None
    area_sq_ft: float | None = None
    shape_area_attr: float | None = None
    review_required = False

    if not pairs:
        outcome = OUTCOME_NONE
        condo = _condo_classification(normalized, None)
        notes.append(
            "no_feature: the official service returned a well-formed "
            "response with zero features for this BBL. This is an explicit "
            "typed outcome, never an error and never a guessed geometry."
        )
        if condo["classification"] == "condo_unit_lot_query":
            notes.append(condo["note"])
    elif len(pairs) > 1 or (len(pairs) == MAX_FEATURES_PER_LOT and exceeded):
        outcome = OUTCOME_MULTIPLE
        review_required = True
        condo = _condo_classification(normalized, None)
        notes.append(
            f"multiple_features: {len(pairs)} features"
            + (" (more exist beyond the bounded record count)" if exceeded else "")
            + " were returned for one BBL. This is a typed REVIEW-REQUIRED "
            "state; the connector never silently picks the first feature."
        )
    else:
        outcome = OUTCOME_SINGLE
        oid, feature = pairs[0]
        attributes = feature["attributes"]
        attr_bbl = _attr_bbl_as_int(attributes.get("BBL"))
        if attr_bbl is None or str(attr_bbl) != normalized.canonical:
            raise ResultMismatchError(
                "returned feature does not correspond to the requested lot "
                "(BBL attribute missing, unparseable, or different); "
                "returned data is never silently trusted",
                correlation_id=correlation_id,
                detail={
                    "url": url,
                    "requested_bbl": normalized.canonical,
                    "returned_bbl": repr(attributes.get("BBL")),
                    "object_id": oid,
                },
            )
        identifier_conflicts = check_identifier_consistency(
            normalized.canonical,
            borocode=attributes.get("BoroCode"),
            block=attributes.get("Block"),
            lot=attributes.get("Lot"),
        )
        if identifier_conflicts:
            review_required = True
            notes.append(
                "identifier_conflict: the feature's BoroCode/Block/Lot "
                "component(s) disagree with the BBL-derived values; both "
                "values are surfaced verbatim and nothing is resolved here "
                "(PRD section 9: conflicts stay visible)."
            )
        condo = _condo_classification(normalized, attributes)
        if condo["classification"] == "condo_billing_lot":
            notes.append(condo["note"])
        elif condo["classification"] == "condo_unit_lot_query":
            drift_signals.append("condo_unit_lot_with_polygon")
            notes.append(
                "unexpected: a condominium UNIT-range lot returned its own "
                "polygon, contradicting the documented one-record-per-"
                "complex semantics (research section 2.5); surfaced "
                "visibly for review."
            )
            review_required = True
        assessment = analyze_lot_geometry(
            feature.get("geometry"), crs=dict(CRS_STAMP), correlation_id=correlation_id
        )
        if assessment.status == GEOMETRY_REVIEW_REQUIRED:
            review_required = True
        area_sq_ft = assessment.area_sq_ft
        raw_shape_area = attributes.get("Shape__Area")
        if isinstance(raw_shape_area, int | float) and not isinstance(
            raw_shape_area, bool
        ):
            shape_area_attr = float(raw_shape_area)
        if (
            area_sq_ft is not None
            and shape_area_attr is not None
            and shape_area_attr > 0.0
            and abs(area_sq_ft - shape_area_attr) / shape_area_attr
            > SHAPE_AREA_DIVERGENCE_REL
        ):
            notes.append(
                "shape_area_divergence: locally computed planar area "
                f"({area_sq_ft!r} sq ft, EPSG:2263) differs from the "
                f"service's Shape__Area attribute ({shape_area_attr!r}) by "
                f"more than {SHAPE_AREA_DIVERGENCE_REL:.1%}; both values "
                "are surfaced, neither is silently preferred."
            )
        if assessment.repaired:
            notes.append(
                "repaired_geometry: the official geometry required repair "
                f"(methods: {[r['method'] for r in assessment.repairs]}); "
                "the verbatim original digest is preserved separately and "
                "this geometry is NOT the untouched official source."
            )
        elif assessment.status != GEOMETRY_VALID:
            notes.append(
                f"geometry_status={assessment.status}: findings "
                f"{assessment.findings}; no usable canonical geometry is "
                "published for this lot without review."
            )

    logger.info(
        "mappluto_geometry lot ok bbl=%s outcome=%s review_required=%s "
        "correlation_id=%s",
        normalized.canonical, outcome, review_required, correlation_id,
    )
    return LotGeometryResult(
        status="ok",
        outcome=outcome,
        review_required=review_required,
        requested_bbl=normalized.canonical,
        borough=normalized.borough,
        block=normalized.block,
        lot=normalized.lot,
        condo=condo,
        identifier_conflicts=identifier_conflicts,
        attributes=attributes,
        features=normalized_features,
        geometry=assessment,
        area_sq_ft=area_sq_ft,
        shape_area_attribute_sq_ft=shape_area_attr,
        exceeded_transfer_limit=exceeded,
        correlation_id=correlation_id,
        request_url=url,
        metadata_request_url=metadata.request_url,
        retrieved_at=retrieved_at,
        crs=dict(CRS_STAMP),
        source_data_last_edited_ms=metadata.source_data_last_edited_ms,
        source_data_last_edited=metadata.source_data_last_edited,
        raw_digest=raw_body_digest(response.body),
        metadata_raw_digest=metadata.raw_digest,
        normalized_digest=canonical_json_digest(normalized_features),
        digest_canonicalization=MPG_CANONICALIZATION_SPEC,
        shapely_version=shapely.__version__,
        geos_version=shapely.geos_version_string,
        drift_signals=drift_signals,
        notes=notes,
        staleness=None,
    )


# ---------------------------------------------------------------------------
# Resilient client (M1-T009 primitives composed; no second resilience system)
# ---------------------------------------------------------------------------


@dataclass
class _LkgEntry:
    stored_at: float
    result: LotGeometryResult


def _is_transient(exc: MapPlutoGeometryConnectorError) -> bool:
    """Transient upstream trouble only: rate limit, timeout, network, 5xx.
    Schema drift, wrong CRS, malformed responses, result mismatches, and
    disallowed requests are NOT transient (retrying or serving stale data
    would mask a real contract problem)."""
    if isinstance(exc, RateLimitedError | SourceTimeoutError):
        return True
    if isinstance(exc, UpstreamError):
        status = exc.detail.get("http_status")
        if isinstance(status, int) and not isinstance(status, bool):
            return 500 <= status < 600
        if "arcgis_error_code" in exc.detail:
            return False
        return exc.detail.get("reason_kind") in ("network", "timeout", "server_error")
    return False


class ResilientMapPlutoGeometryClient:
    """Cache + circuit breaker + last-known-good + budget composition
    around ``fetch_lot_geometry``, built ENTIRELY from the M1-T009
    primitives (``TTLCache``, ``CircuitBreaker``, ``AnalysisBudget``,
    ``ResilienceConfig``, ``ResilienceMetrics``; retry lives in the plain
    functions via ``backoff_delay``/``parse_retry_after``).

    TWO-STALENESS RULE: ``staleness`` is stamped HERE and ONLY here -
    ``{served_from_cache, stale, ...}`` describes the transport/cache serve
    path. ``source_data_last_edited`` (dataLastEditDate provenance) is
    copied verbatim from the original result on every serve path and NEVER
    influences the staleness stamp: an old source dataset retrieved fresh
    is NOT stale; a cache/LKG serve does not alter source timestamps.
    """

    def __init__(
        self,
        *,
        config: ResilienceConfig | None = None,
        transport: Transport = urllib_transport,
        timeout: float = 30.0,
        now: Callable[[], float] = time.monotonic,
        wall_clock: Callable[[], datetime] = _utc_now,
        sleep: Callable[[float], None] = time.sleep,
        rng: Random | None = None,
        metrics: ResilienceMetrics | None = None,
    ) -> None:
        self._config = config or ResilienceConfig()
        self._transport = transport
        self._timeout = timeout
        self._now = now
        self._wall_clock = wall_clock
        self._sleep = sleep
        self._rng = rng or Random()
        self.metrics = metrics or ResilienceMetrics()
        self._cache = TTLCache(
            ttl_seconds=self._config.cache_ttl_seconds,
            max_entries=self._config.cache_max_entries,
            now=now,
            metrics=self.metrics,
        )
        self._breaker = CircuitBreaker(
            source_id=SOURCE_ID,
            failure_threshold=self._config.breaker_failure_threshold,
            cooldown_seconds=self._config.breaker_cooldown_seconds,
            now=now,
            metrics=self.metrics,
        )
        self._lkg_lock = threading.Lock()
        self._lkg: OrderedDict[str, _LkgEntry] = OrderedDict()

    def _cache_key(self, canonical_bbl: str) -> str:
        return f"{self._config.cache_key_version}:{SOURCE_ID}:lot:{canonical_bbl}"

    def fetch_lot_geometry(
        self,
        bbl: object,
        *,
        correlation_id: str | None = None,
        budget: AnalysisBudget | None = None,
    ) -> LotGeometryResult:
        correlation_id = correlation_id or uuid.uuid4().hex
        normalized = normalize_bbl(bbl)  # validation BEFORE cache and network
        key = self._cache_key(normalized.canonical)

        hit = self._cache.get_with_age(key)
        if hit is not None:
            cached, age_seconds = hit
            self.metrics.emit("cache_hit", key=key, correlation_id=correlation_id)
            result: LotGeometryResult = copy.deepcopy(cached)  # type: ignore[assignment]
            result.staleness = {
                "served_from_cache": True,
                "stale": False,
                "original_retrieved_at": result.retrieved_at,
                "age_seconds": age_seconds,
            }
            return result
        self.metrics.emit("cache_miss", key=key, correlation_id=correlation_id)

        if not self._breaker.allow():
            self.metrics.emit(
                "breaker_fast_reject",
                source_id=SOURCE_ID,
                cooldown_remaining_seconds=self._breaker.cooldown_remaining(),
                correlation_id=correlation_id,
            )
            rejection = CircuitOpenError(
                "circuit breaker is open for this source; the upstream call "
                "was rejected without network I/O",
                correlation_id=correlation_id,
                detail={
                    "circuit": "open",
                    "cooldown_remaining_seconds": self._breaker.cooldown_remaining(),
                },
            )
            return self._serve_lkg_or_raise(key, correlation_id, rejection)

        try:
            result = fetch_lot_geometry(
                normalized.canonical,
                transport=self._transport,
                timeout=self._timeout,
                max_attempts=self._config.retry_max_attempts,
                backoff_base=self._config.backoff_base_seconds,
                backoff_cap=self._config.backoff_cap_seconds,
                retry_after_cap=self._config.retry_after_max_wait_seconds,
                rng=self._rng,
                sleep=self._sleep,
                clock=self._wall_clock,
                correlation_id=correlation_id,
                budget=budget,
            )
        except RequestBudgetExceededError:
            raise  # caller-side condition; never masked by LKG
        except MapPlutoGeometryConnectorError as exc:
            self.metrics.emit(
                "fetch_failure",
                error_type=exc.error_type,
                correlation_id=correlation_id,
            )
            if _is_transient(exc):
                self._breaker.record_failure()
                return self._serve_lkg_or_raise(key, correlation_id, exc)
            raise

        self._breaker.record_success()
        self._cache.put(key, copy.deepcopy(result))
        self.metrics.emit("cache_store", key=key, correlation_id=correlation_id)
        self._store_lkg(key, result)
        self.metrics.emit(
            "fetch_success", status=result.status, correlation_id=correlation_id
        )
        return result

    def _store_lkg(self, key: str, result: LotGeometryResult) -> None:
        with self._lkg_lock:
            self._lkg[key] = _LkgEntry(
                stored_at=self._now(), result=copy.deepcopy(result)
            )
            self._lkg.move_to_end(key)
            while len(self._lkg) > self._config.lkg_max_entries:
                self._lkg.popitem(last=False)

    def _serve_lkg_or_raise(
        self, key: str, correlation_id: str, exc: MapPlutoGeometryConnectorError
    ) -> LotGeometryResult:
        with self._lkg_lock:
            entry = self._lkg.get(key)
        if entry is None:
            self.metrics.emit("lkg_unavailable", key=key, correlation_id=correlation_id)
            raise exc
        age_seconds = self._now() - entry.stored_at
        if age_seconds > self._config.lkg_max_age_seconds:
            self.metrics.emit(
                "lkg_too_old",
                key=key,
                age_seconds=age_seconds,
                max_age_seconds=self._config.lkg_max_age_seconds,
                correlation_id=correlation_id,
            )
            raise exc
        result = copy.deepcopy(entry.result)
        circuit_open = bool(exc.detail.get("circuit") == "open")
        note = (
            "served_from_last_known_good: upstream failure "
            f"({exc.error_type}{', circuit open' if circuit_open else ''}) "
            f"at {_rfc3339(self._wall_clock())}; serving the last-known-good "
            f"official snapshot retrieved at {result.retrieved_at} "
            f"(age {age_seconds:.0f}s at serve time). This response is STALE "
            "cached data, not a fresh retrieval; retrieved_at and "
            "source_data_last_edited reflect the original retrieval and the "
            "official source edit date (two-staleness rule)."
        )
        result.notes = [*result.notes, note]
        result.staleness = {
            "served_from_cache": True,
            "stale": True,
            "upstream_error_type": exc.error_type,
            "original_retrieved_at": result.retrieved_at,
            "age_seconds": age_seconds,
        }
        self.metrics.emit(
            "lkg_served",
            key=key,
            age_seconds=age_seconds,
            upstream_error_type=exc.error_type,
            correlation_id=correlation_id,
        )
        return result
