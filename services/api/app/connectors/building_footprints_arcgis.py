"""NYC building-footprint + roof-height connector - official OTI BUILDING layer
(task M5-T089, D-087-R003; source recon docs/research/building-footprints-source-2026-09.md
and its reviews project-control/reports/M5-T087-G1.md / M5-T087-G3.md).

Channel: the OTI ArcGIS feature service ``BUILDING_view/FeatureServer/0`` (NYC Open Data
``5zhs-2jue``; keyless). Read-only. Returns typed :class:`ContextBuilding` records for the
footprints that intersect a caller-supplied EPSG:2263 envelope or polygon (one lot plus its
neighbours). NOT wired to any route; a later gated packet consumes it.

Contract (each point is proven offline on recorded fixtures):

1. REQUEST - the LONG ArcGIS field names only (G1/G3 finding F1: the shapefile short names such
   as HEIGHTROOF are rejected - recorded as HTTP 200 carrying an ArcGIS error object with code
   400, "'outFields' parameter is invalid"), an explicit out-field allowlist (never ``*``), an
   ``esriSpatialRelIntersects`` filter on a validated EPSG:2263 envelope or closed polygon
   ring (``inSR=2263``), ``outSR=2263``, ``orderByFields=OBJECTID ASC`` and deterministic
   ``resultOffset`` paging under the layer's ``maxRecordCount``.
2. CRS - the layer publishes in Web Mercator (wkid 102100 / 3857). Every non-empty query page
   must come back as wkid 102718 / latestWkid 2263 or it is refused before any coordinate is
   read. The coordinates are the service's reprojection of that publication: display and
   massing grade, not survey grade. MapPLUTO stays the measurement channel.
3. DATUM - HEIGHT_ROOF is "the height of the roof above the ground elevation, not height
   above sea level" (City dictionary; the service's own FGDC metadata says the same).
   GROUND_ELEVATION is carried AS PUBLISHED with the dictionary's NAVD88 label (see
   GROUND_DATUM_BASIS for its caveats and the definition conflict). The massing model is a
   relative z=0 frame, so every record also carries
   ``relative_base_z_ft = ground_elevation - site_ground`` for a caller-supplied site ground
   (G3 finding F2). The site ground is never guessed and a missing ground is never replaced.
4. UNITS - feet is an INFERENCE (research RQ-1): no official per-field unit tag exists for
   HEIGHT_ROOF / GROUND_ELEVATION. Every record carries HEIGHT_UNIT_BASIS saying so.
5. GAPS - HEIGHT_ROOF "zero or NULL mean that this information was not available": a typed
   gap, never a default and never a zero-height box. NULL ground elevation, placeholder
   triangles (FEATURE_CODE 1003), undocumented feature codes, million-BINs, unparseable
   BBLs and condo billing-lot joins (MAPPLUTO_BBL lot 7501-7599, the MapPLUTO connector's
   CONDO_BILLING_LOT_MIN/MAX) are typed gaps or flags on the record.
6. GEOMETRY - FOOTPRINT_GEOMETRY_POLICY below is the written multipart/holes policy. Each
   usable footprint is also classified against the query geometry (within, partial overlap,
   boundary touch only, or disjoint locally), so a party-wall touch is never reported as an
   overlap. Exact planar geometry on published coordinates; no accuracy tolerance applied
   (photogrammetric features are stated as +/- 2 ft).
7. FAIL-CLOSED - transport faults, ArcGIS error objects, malformed JSON, a wrong CRS, schema
   drift, over-page counts and paging pathologies become a typed :class:`FootprintRefusal`
   carrying the failed request's URL, time and body digest. ``fetch_context_buildings``
   never raises.

No cache and no last-known-good serve exist here, so no transport-staleness state exists;
``source_data_last_edited`` is dataset-freshness provenance only. Deterministic code only:
no AI, no legal interpretation.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import urllib.parse
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from random import Random

from shapely.geometry import Polygon, box
from shapely.geometry.base import BaseGeometry

from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.building_footprints_geometry import (
    COORD_ABS_MAX_FT,
    FootprintPart,
    _finite,
    _safe_repr,
    classify_query_relation,
    parse_footprint_geometry,
)
from app.connectors.mappluto_geometry_arcgis import (
    CONDO_BILLING_LOT_MAX,
    CONDO_BILLING_LOT_MIN,
)
from app.connectors.pluto_soda import canonical_json_digest
from app.resilience.budget import AnalysisBudget
from app.resilience.transport import (
    Transport,
    jittered_retry_after_delay,
    request_with_retry,
    sanitize_retry_after,
    standard_retry_hooks,
    urllib_transport,
)

logger = logging.getLogger("app.connectors.building_footprints_arcgis")

SOURCE_ID = "nyc-oti-building-footprints-arcgis"
OPEN_DATA_ID = "5zhs-2jue"
# Pinned official root (recon section 1; same OTI/DOF org as the DTM channel). Never
# interpolated from caller input.
SERVICE_ROOT = "https://services6.arcgis.com/yG5s3afENB5iO9fj/arcgis/rest/services"
SERVICE_NAME = "BUILDING_view"
LAYER_NAME = "BUILDING"
LAYER_URL = f"{SERVICE_ROOT}/{SERVICE_NAME}/FeatureServer/0"

EXPECTED_WKID = 102718
EXPECTED_LATEST_WKID = 2263
CRS_STAMP = {
    "wkid": EXPECTED_WKID,
    "latest_wkid": EXPECTED_LATEST_WKID,
    "authority": "EPSG:2263 (NAD83 / New York Long Island, US survey feet)",
}
# Documented publication CRS (recon section 3; live layer JSON). A change is a visible drift
# signal, never fatal: every query page is CRS-gated on its own.
PUBLICATION_SPATIAL_REFERENCE = {"wkid": 102100, "latestWkid": 3857}
EXPECTED_GEOMETRY_TYPE = "esriGeometryPolygon"
OBJECT_ID_FIELD = "OBJECTID"
SPATIAL_REL = "esriSpatialRelIntersects"

# LONG ArcGIS field names and esri types, pinned from the live layer JSON (fixture
# layer_metadata.json; the tests cross-check). NAME ("not actively maintained") and
# Shape__Area / Shape__Length ("Do not use", Web Mercator) are deliberately not requested.
REQUIRED_FIELDS: dict[str, str] = {
    "OBJECTID": "esriFieldTypeOID",
    "DOITT_ID": "esriFieldTypeInteger",
    "BIN": "esriFieldTypeInteger",
    "BASE_BBL": "esriFieldTypeString",
    "MAPPLUTO_BBL": "esriFieldTypeString",
    "HEIGHT_ROOF": "esriFieldTypeDouble",
    "GROUND_ELEVATION": "esriFieldTypeInteger",
    "CONSTRUCTION_YEAR": "esriFieldTypeInteger",
    "FEATURE_CODE": "esriFieldTypeSmallInteger",
    "GEOM_SOURCE": "esriFieldTypeString",
    "LAST_EDITED_DATE": "esriFieldTypeDate",
    "LAST_STATUS_TYPE": "esriFieldTypeString",
}
OUT_FIELDS = tuple(REQUIRED_FIELDS)

# Documented FEATURE_CODE domain (City dictionary, G1-confirmed).
FEATURE_CODE_LABELS = {
    1000: "Parking",
    1001: "Gas Station Canopy",
    1002: "Storage Tank",
    1003: "Placeholder",
    1004: "Auxiliary Structure",
    1005: "Temporary Structure",
    1006: "Cantilevered Building",
    2100: "Building",
    2110: "Skybridge",
    5100: "Building Under Construction",
    5110: "Garage",
}
PLACEHOLDER_FEATURE_CODE = 1003
# "million BINs" (1000000, 2000000, ...) mark an unassigned/unknown BIN (City dictionary).
MILLION_BINS = frozenset(n * 1_000_000 for n in range(1, 6))

HEIGHT_UNIT = "us_survey_foot"
HEIGHT_UNIT_BASIS = (
    "INFERENCE (research RQ-1), not a published unit: neither the City dictionary nor the "
    "service's FGDC metadata tags a unit on HEIGHT_ROOF or GROUND_ELEVATION. Feet rests on the "
    "US-foot EPSG:2263 source CRS, the dictionary's foot-denominated prose and foot-scale values."
)
HEIGHT_REFERENCE = (
    "HEIGHT_ROOF is the height of the roof above the ground elevation, not height above sea "
    "level (City dictionary); zero or NULL means the information was not available."
)
GROUND_DATUM = "NAVD88"
GROUND_DATUM_BASIS = (
    "As published. City dictionary: NAVD88 'when collected photogrammetrically or from modern "
    "sources'; the datum of older or other-source values is unstated (research RQ-2). The City "
    "dictionary defines GROUND_ELEVATION as the lowest elevation at building ground level; the "
    "service's FGDC metadata defines it as a LiDAR bare-earth value interpolated at the building "
    "centroid. Both definitions stay visible; neither is chosen here."
)

FOOTPRINT_GEOMETRY_POLICY = (
    "building-footprint-geometry-1: esri polygon rings are read verbatim in EPSG:2263 (never "
    "quantized, never repaired). A ring must be a closed list of finite in-bounds [x, y] pairs "
    "with at least 3 distinct vertices and non-zero area. Clockwise rings are exterior parts and "
    "counterclockwise rings are holes (esri convention); each hole belongs to the smallest "
    "exterior that contains it. EVERY exterior becomes its own part, in response order, with its "
    "holes: a multipart footprint is never merged, reduced to one part or dropped, and a hole is "
    "never filled. The record carries 'multipart' / 'has_holes' flags; a consumer that needs one "
    "simple ring (the massing prism builder refuses holes) must refuse or handle them explicitly. "
    "Parts that only touch are kept (flag 'parts_touch'); parts whose interiors overlap make the "
    "geometry review_required. Any malformed ring or invalid part makes the geometry invalid, "
    "and a footprint with no clockwise ring or a hole outside every exterior is review_required; "
    "then no part is offered (nothing is partially kept). In every case the record itself is "
    "still returned with the verbatim esri geometry and its digest: no footprint is ever "
    "silently dropped."
)

# Connector safety policy (engineering bounds, not source facts): a lot-plus-neighbours
# context query stays small. COORD_ABS_MAX_FT (imported from the geometry module) mirrors
# the accepted DCM envelope bound.
MAX_QUERY_SPAN_FT = 5_000.0
MAX_QUERY_POLYGON_VERTICES = 200
MAX_PAGE_SIZE = 2000  # the live layer's maxRecordCount; also capped by the fetched metadata
HARD_MAX_PAGES = 50
MAX_CONTEXT_BUILDINGS = 2000  # beyond this the query is refused, never truncated

# DB-058(b) retention bounds against a hostile/broken official host (G5-A2): a
# lot-plus-neighbours context geometry is tiny, so a single runaway geometry and the
# cumulative page payload are both capped WELL below MAX_RESPONSE_BYTES x HARD_MAX_PAGES.
# Each is a typed ResourceBoundError refusal, raised before the value is retained.
MAX_GEOMETRY_VERTICES = 50_000  # total vertices across ONE feature's rings
MAX_TOTAL_DECODED_BYTES = 64 * 1024 * 1024  # cumulative decoded page bodies across paging

# DB-058(c) interactive posture (G5-A3): an interactive caller may cap upstream attempts
# (fail fast) and pass a wall-clock ``deadline`` checked before each page.
INTERACTIVE_MAX_ATTEMPTS = 1

# DB-058(a) / G5-A1: these record fields are VERBATIM official source text and are NOT
# escaped here (escaping is a render concern - PKT-E/PKT-I). Consumers MUST escape them.
UNTRUSTED_TEXT_FIELDS = ("attributes", "geom_source", "last_status_type")
UNTRUSTED_TEXT_NOTICE = (
    "Verbatim official source text kept for provenance; NOT sanitized or escaped here. "
    "Every report / 3D / web consumer MUST escape these fields on render (PKT-E/PKT-I)."
)


# ---------------------------------------------------------------------------
# Typed errors (internal; the public fetch converts every one into a FootprintRefusal)
# ---------------------------------------------------------------------------


class BuildingFootprintConnectorError(Exception):
    """Base typed error. Payloads never carry stack traces, headers or tokens."""

    error_type = "internal_error"

    def __init__(self, message: str, *, correlation_id: str, detail: dict | None = None):
        super().__init__(message)
        self.message = message
        self.correlation_id = correlation_id
        self.detail = detail or {}


class UpstreamError(BuildingFootprintConnectorError):
    """Network failure, unexpected HTTP status, or an ArcGIS error object (even with HTTP 200)."""

    error_type = "upstream_error"


class MalformedResponseError(BuildingFootprintConnectorError):
    """Body is not the documented shape; never converted into a valid empty result."""

    error_type = "malformed_response"


class SchemaDriftError(BuildingFootprintConnectorError):
    """Layer contract changed (name, geometry type, fields, types, paging capabilities)."""

    error_type = "schema_drift"


class WrongCRSError(BuildingFootprintConnectorError):
    """A query page is not wkid 102718 / latestWkid 2263 (or omits its spatial reference)."""

    error_type = "wrong_crs"


class RateLimitedError(BuildingFootprintConnectorError):
    error_type = "rate_limited"


class SourceTimeoutError(BuildingFootprintConnectorError):
    error_type = "timeout"


class RequestBudgetExceededError(BuildingFootprintConnectorError):
    error_type = "budget_exhausted"


class DisallowedRequestError(BuildingFootprintConnectorError):
    """Caller input refused BEFORE any network I/O."""

    error_type = "disallowed_request"


class PagingPathologyError(BuildingFootprintConnectorError):
    """Over-page count, repeated OBJECTIDs, zero progress, page ceiling or feature cap."""

    error_type = "paging_pathology"


class ResourceBoundError(BuildingFootprintConnectorError):
    """A single geometry exceeds the vertex cap, or the cumulative decoded page bytes
    exceed the ceiling: refused before unbounded retention (DB-058 b / G5-A2)."""

    error_type = "resource_exhausted"


class DeadlineExceededError(BuildingFootprintConnectorError):
    """The caller-supplied wall-clock deadline elapsed before the next page (DB-058 c /
    G5-A3). Caller-side, distinct from an upstream ``timeout``."""

    error_type = "deadline_exceeded"


# ---------------------------------------------------------------------------
# Result contracts
# ---------------------------------------------------------------------------


@dataclass
class ContextBuilding:
    """One official footprint as a typed context building. A ``None`` value always has a
    matching entry in ``gaps``; nothing is defaulted."""

    object_id: int
    doitt_id: int | None
    bin: int | None
    base_bbl: str | None
    mappluto_bbl: str | None
    joins_subject_lot: bool | None
    feature_code: int | None
    feature_code_label: str | None
    height_roof_ft: float | None
    ground_elevation_ft: float | None
    relative_base_z_ft: float | None
    relative_roof_z_ft: float | None
    construction_year: int | None
    geom_source: str | None
    last_edited: str | None
    last_status_type: str | None
    geometry_status: str
    geometry_findings: list[str]
    parts: list[FootprintPart]
    footprint_area_sq_ft: float | None
    query_relation: str | None
    query_overlap_area_sq_ft: float | None
    flags: list[str]
    gaps: list[dict]
    attributes: dict
    original_geometry: object
    original_geometry_digest: str
    height_unit: str = HEIGHT_UNIT
    height_unit_basis: str = HEIGHT_UNIT_BASIS
    height_reference: str = HEIGHT_REFERENCE
    ground_datum: str = GROUND_DATUM
    ground_datum_basis: str = GROUND_DATUM_BASIS
    # DB-058(a) / G5-A1: consumers MUST escape these verbatim source-text fields on render.
    untrusted_text_fields: tuple[str, ...] = UNTRUSTED_TEXT_FIELDS
    untrusted_text_notice: str = UNTRUSTED_TEXT_NOTICE


@dataclass
class FootprintRefusal:
    """Typed refusal with the provenance of the failed request."""

    error_type: str
    message: str
    correlation_id: str
    detail: dict
    request_url: str | None
    retrieved_at: str
    raw_digest: str | None


@dataclass
class ContextBuildingsResult:
    """``status`` ``ok`` (buildings sorted by OBJECTID) or ``refused`` (no buildings; the
    typed ``refusal`` plus whatever provenance was gathered before the failure)."""

    status: str
    buildings: list[ContextBuilding]
    refusal: FootprintRefusal | None
    correlation_id: str
    query: dict | None
    site_ground_elevation_ft: float | None
    subject_bbl: str | None
    metadata_request_url: str | None
    metadata_raw_digest: str | None
    request_urls: list[str]
    raw_digests: list[str]
    retrieved_at: str | None
    source_data_last_edited_ms: int | None
    source_data_last_edited: str | None
    pages_fetched: int
    drift_signals: list[str]
    source_id: str = SOURCE_ID
    open_data_id: str = OPEN_DATA_ID
    layer_url: str = LAYER_URL
    crs: dict = field(default_factory=lambda: dict(CRS_STAMP))
    geometry_policy: str = FOOTPRINT_GEOMETRY_POLICY

    def provenance(self) -> dict:
        """The provenance quintuple: source, request, retrieved_at, dataset last edit, digest."""
        return {
            "source": {"source_id": self.source_id, "open_data_id": self.open_data_id,
                       "layer_url": self.layer_url},
            "request": {"metadata": self.metadata_request_url, "pages": list(self.request_urls)},
            "retrieved_at": self.retrieved_at,
            "source_data_last_edited": self.source_data_last_edited,
            "response_digests": {"metadata": self.metadata_raw_digest,
                                 "pages": list(self.raw_digests)},
        }


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _rfc3339(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _epoch_ms_to_rfc3339(ms: object) -> str | None:
    if isinstance(ms, bool) or not isinstance(ms, int):
        return None
    try:
        return _rfc3339(datetime.fromtimestamp(ms / 1000.0, UTC))
    except (OverflowError, OSError, ValueError):
        return None


def raw_body_digest(body: str) -> str:
    """sha256 over the exact UTF-8 bytes of the transported body."""
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


# DB-058(e) / M5-T089 G3-A1: fields for the findable-but-non-leaky internal-error log.
# The message is a FIXED string (never ``str(exc)``, whose text can echo an upstream body);
# only the exception CLASS - not its message - joins it, and both are neutralized with the
# shared transport sanitizer and length-bounded before they reach the log.
_INTERNAL_ERROR_LOG_MESSAGE = "unexpected internal failure - no data returned"
_LOG_FIELD_MAX = 200

# DB-066(a) + DB-073(a): strip CR/LF, every C0/C1 control character, DEL, AND the U+2028 /
# U+2029 line & paragraph separators OUTRIGHT before the shared allowlist runs. The allowlist
# regex ends in ``$``, which in Python matches BEFORE a trailing newline, so a value like
# ``"Foo\n"`` would otherwise pass through raw and forge a log line; U+2028/U+2029 are Unicode
# line separators that ``str.splitlines()`` (and many renderers) treat as newlines yet are NOT
# C0/C1 controls, so they are added here explicitly (DB-073 (a), M5-T101 G5 L-1). (No
# ``import re`` - the AS-5 import allowlist forbids it - a str.translate table does it.)
_CONTROL_CHAR_DELETE = {c: None for c in [*range(0x20), 0x7F, *range(0x80, 0xA0),
                                          0x2028, 0x2029]}


def _sanitized_bounded(text: str, limit: int = _LOG_FIELD_MAX) -> str:
    """Neutralize an untrusted string for a log line: strip CR/LF and control characters
    outright (DB-066 a), then apply the shared transport sanitizer
    (:func:`app.resilience.transport.sanitize_retry_after`: an allowlist passthrough,
    otherwise ``repr``), then bound the length so a hostile value cannot dump an unbounded
    body. Stripping first closes the allowlist ``$``-before-trailing-newline gap."""
    safe = sanitize_retry_after(text.translate(_CONTROL_CHAR_DELETE))
    return safe if len(safe) <= limit else safe[:limit] + "...(truncated)"


def _safe_correlation_id(raw: object) -> str:
    """DB-058(d) / DB-066(b) / DB-073(a,b): a caller correlation id is UNTRUSTED. Strip CR/LF,
    control characters and the U+2028/U+2029 separators so it can never forge a log line at
    EITHER log site (this connector or the shared transport, which logs it too), THEN bound its
    length to :data:`_LOG_FIELD_MAX` so a hostile caller cannot dump an arbitrarily long id at
    every log site (DB-073 (b), M5-T101 G5 L-2). A missing / non-string / emptied-after-strip id
    becomes a server-generated uuid4 hex - so no raw or unbounded caller value ever reaches a
    log. Bounding at the source also protects ``result.correlation_id`` for a raw-rendering
    consumer (DB-073 (a))."""
    if not isinstance(raw, str):
        return uuid.uuid4().hex
    cleaned = raw.translate(_CONTROL_CHAR_DELETE)
    if not cleaned:
        return uuid.uuid4().hex
    if len(cleaned) <= _LOG_FIELD_MAX:
        return cleaned
    return cleaned[:_LOG_FIELD_MAX] + "...(truncated)"


def _refusal_time(io: _Io) -> str:
    try:
        return _rfc3339(io.clock())
    except Exception:  # an injected clock must not break the fail-closed path
        return _rfc3339(_utc_now())


# ---------------------------------------------------------------------------
# Query validation + URL construction (every URL is built here)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _Query:
    geometry_type: str
    geometry_param: str
    shape: BaseGeometry
    echo: dict


def _coord(value: object, *, what: str, cid: str) -> float:
    number = _finite(value)
    if number is None or abs(number) > COORD_ABS_MAX_FT:
        raise DisallowedRequestError(
            f"{what} must be a finite real number within |{COORD_ABS_MAX_FT:g}| ft",
            correlation_id=cid, detail={"value": _safe_repr(value)})
    return float(f"{number:.4f}")  # the exact value the URL carries


def _check_span(shape: BaseGeometry, cid: str) -> None:
    xmin, ymin, xmax, ymax = shape.bounds
    if max(xmax - xmin, ymax - ymin) > MAX_QUERY_SPAN_FT:
        raise DisallowedRequestError(
            f"query extent exceeds {MAX_QUERY_SPAN_FT:g} ft; a context query covers one lot "
            "and its neighbours", correlation_id=cid, detail={"bounds": list(shape.bounds)})


def _build_query(envelope: object, polygon: object, cid: str) -> _Query:
    if (envelope is None) == (polygon is None):
        raise DisallowedRequestError("exactly one of envelope or polygon is required",
                                     correlation_id=cid)
    if envelope is not None:
        if not isinstance(envelope, list | tuple) or len(envelope) != 4:
            raise DisallowedRequestError("envelope must be (xmin, ymin, xmax, ymax)",
                                         correlation_id=cid,
                                         detail={"envelope": _safe_repr(envelope)})
        xmin, ymin, xmax, ymax = (
            _coord(v, what=f"envelope[{i}]", cid=cid) for i, v in enumerate(envelope))
        if not (xmin < xmax and ymin < ymax):
            raise DisallowedRequestError("envelope must have xmin < xmax and ymin < ymax",
                                         correlation_id=cid,
                                         detail={"envelope": [xmin, ymin, xmax, ymax]})
        shape = box(xmin, ymin, xmax, ymax)
        _check_span(shape, cid)
        return _Query("esriGeometryEnvelope", f"{xmin:.4f},{ymin:.4f},{xmax:.4f},{ymax:.4f}",
                      shape, {"kind": "envelope", "envelope": [xmin, ymin, xmax, ymax]})
    if not isinstance(polygon, list | tuple) or not (
        4 <= len(polygon) <= MAX_QUERY_POLYGON_VERTICES + 1
    ):
        raise DisallowedRequestError(
            f"polygon must be a closed ring of 4..{MAX_QUERY_POLYGON_VERTICES + 1} points",
            correlation_id=cid, detail={"polygon": _safe_repr(polygon)})
    ring: list[list[float]] = []
    for i, point in enumerate(polygon):
        if not isinstance(point, list | tuple) or len(point) != 2:
            raise DisallowedRequestError(f"polygon[{i}] must be an [x, y] pair",
                                         correlation_id=cid)
        ring.append([_coord(point[0], what=f"polygon[{i}].x", cid=cid),
                     _coord(point[1], what=f"polygon[{i}].y", cid=cid)])
    shape = Polygon(ring)
    if ring[0] != ring[-1] or not shape.is_valid or shape.area <= 0.0:
        raise DisallowedRequestError(
            "polygon must be a closed, valid, simple ring with non-zero area",
            correlation_id=cid, detail={"closed": ring[0] == ring[-1]})
    _check_span(shape, cid)
    param = '{"rings":[[' + ",".join(f"[{x:.4f},{y:.4f}]" for x, y in ring) + "]]}"
    return _Query("esriGeometryPolygon", param, shape, {"kind": "polygon", "ring": ring})


def build_metadata_url() -> str:
    return f"{LAYER_URL}?f=json"


def build_query_url(*, envelope: object = None, polygon: object = None, page_size: int,
                    offset: int = 0) -> str:
    """Public view of the ONLY query URL shape this connector emits (the fixture URLs were
    captured with exactly these bytes). Raises DisallowedRequestError on invalid input."""
    _check_page_size(page_size, "urlbuild")
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise DisallowedRequestError("offset must be a non-negative integer",
                                     correlation_id="urlbuild")
    return _query_url(_build_query(envelope, polygon, "urlbuild"), page_size=page_size,
                      offset=offset)


def _query_url(query: _Query, *, page_size: int, offset: int) -> str:
    params = (
        ("where", "1=1"),
        ("geometry", query.geometry_param),
        ("geometryType", query.geometry_type),
        ("inSR", str(EXPECTED_LATEST_WKID)),
        ("spatialRel", SPATIAL_REL),
        ("outFields", ",".join(OUT_FIELDS)),
        ("returnGeometry", "true"),
        ("outSR", str(EXPECTED_LATEST_WKID)),
        ("orderByFields", f"{OBJECT_ID_FIELD} ASC"),
        ("resultRecordCount", str(page_size)),
        ("resultOffset", str(offset)),
        ("f", "json"),
    )
    encoded = urllib.parse.urlencode(params, quote_via=urllib.parse.quote, safe="")
    return f"{LAYER_URL}/query?{encoded}"


# ---------------------------------------------------------------------------
# Transport (the MapPLUTO connector's shared bounded-retry engine) + body parsing
# ---------------------------------------------------------------------------


@dataclass
class _Io:
    transport: Transport
    timeout: float
    max_attempts: int
    backoff_base: float
    backoff_cap: float
    retry_after_cap: float
    rng: Random
    sleep: Callable[[float], None]
    clock: Callable[[], datetime]
    budget: AnalysisBudget | None
    cid: str
    # DB-058(c): optional caller wall-clock deadline, checked before each page.
    deadline: datetime | None = None
    # Provenance of the request in flight (read by the refusal path).
    url: str | None = None
    retrieved_at: str | None = None
    digest: str | None = None

    def get(self, url: str) -> str:
        self.url, self.retrieved_at, self.digest = url, None, None
        response = request_with_retry(
            url,
            transport=self.transport,
            headers={"Accept": "application/json"},
            timeout=self.timeout,
            max_attempts=self.max_attempts,
            hooks=standard_retry_hooks(
                logger=logger, log_label="building_footprints", correlation_id=self.cid,
                url=url, sanitize_network_reason=_safe_repr,
                rate_limited_error=RateLimitedError,
                rate_limited_message="ArcGIS throttled the request (HTTP 429); retries exhausted",
                timeout_error=SourceTimeoutError,
                timeout_message="ArcGIS request timed out; retries exhausted",
                unavailable_error=UpstreamError,
                unavailable_message="official ArcGIS service unavailable; retries exhausted",
                include_reason_kind=True,
                unexpected_status_message="unexpected HTTP status {status} from ArcGIS",
                budget_error=RequestBudgetExceededError,
            ),
            compute_delay=jittered_retry_after_delay(
                backoff_base=self.backoff_base, backoff_cap=self.backoff_cap,
                retry_after_cap=self.retry_after_cap, rng=self.rng, wall_clock=self.clock),
            sleep=self._sleep_within_deadline,
            budget=self.budget,
        )
        self.retrieved_at = _rfc3339(self.clock())
        self.digest = raw_body_digest(response.body)
        return response.body

    def _sleep_within_deadline(self, seconds: float) -> None:
        """DB-073(c): the caller wall-clock deadline is honoured DURING retry backoff too, not
        only at each page top. Before sleeping between attempts, refuse with a typed
        ``deadline_exceeded`` if the deadline is already reached, so a slow host cannot make a
        request overshoot by a full retry budget (M5-T101 G5 T-1). A missing deadline never
        refuses. The raise propagates out of ``request_with_retry`` (the injected sleep is
        called outside its try) into the connector's fail-closed refusal path."""
        _check_deadline(self)
        self.sleep(seconds)


def _parse_json_object(body: str, *, url: str, cid: str) -> dict:
    try:
        doc = json.loads(body)
    except (ValueError, RecursionError) as exc:
        raise MalformedResponseError("ArcGIS body is not valid JSON", correlation_id=cid,
                                     detail={"url": url, "parse_error": type(exc).__name__}
                                     ) from exc
    if not isinstance(doc, dict):
        raise MalformedResponseError("ArcGIS body is not a JSON object", correlation_id=cid,
                                     detail={"url": url})
    if "error" in doc:
        error = doc["error"] if isinstance(doc["error"], dict) else {}
        raise UpstreamError(
            "ArcGIS returned an error object (an error delivered with HTTP 200 is not data)",
            correlation_id=cid,
            detail={"url": url, "arcgis_error_code": _safe_repr(error.get("code")),
                    "arcgis_error_message": _safe_repr(error.get("message"))})
    return doc


def _validate_metadata(doc: dict, *, url: str, cid: str) -> tuple[int, list[str]]:
    def drift(message: str, **detail: object) -> SchemaDriftError:
        return SchemaDriftError(message, correlation_id=cid, detail={"url": url, **detail})

    if doc.get("name") != LAYER_NAME:
        raise drift("layer name is not BUILDING", name=_safe_repr(doc.get("name")))
    if doc.get("geometryType") != EXPECTED_GEOMETRY_TYPE:
        raise drift("layer geometryType is not esriGeometryPolygon")
    if doc.get("objectIdField") != OBJECT_ID_FIELD:
        raise drift("layer objectIdField is not OBJECTID")
    fields = doc.get("fields")
    if not isinstance(fields, list):
        raise drift("layer metadata has no fields array")
    live = {
        entry["name"]: str(entry.get("type"))
        for entry in fields
        if isinstance(entry, dict) and isinstance(entry.get("name"), str)
    }
    missing = sorted(set(REQUIRED_FIELDS) - set(live))
    retyped = sorted(n for n in REQUIRED_FIELDS if n in live and live[n] != REQUIRED_FIELDS[n])
    if missing or retyped:
        raise drift("required long-name field(s) missing or re-typed", missing=missing,
                    retyped={n: live[n] for n in retyped})
    max_records = doc.get("maxRecordCount")
    if isinstance(max_records, bool) or not isinstance(max_records, int) or max_records < 1:
        raise drift("maxRecordCount missing or invalid", max_record_count=_safe_repr(max_records))
    caps = doc.get("advancedQueryCapabilities")
    if not (isinstance(caps, dict) and caps.get("supportsPagination") is True
            and caps.get("supportsOrderBy") is True):
        raise drift("layer no longer advertises supportsPagination/supportsOrderBy")
    signals: list[str] = []
    extent = doc.get("extent")
    publication_sr = extent.get("spatialReference") if isinstance(extent, dict) else None
    if publication_sr != PUBLICATION_SPATIAL_REFERENCE:
        signals.append("publication_crs_changed")
    return max_records, signals


def _fetch_layer_metadata(io: _Io, result: ContextBuildingsResult) -> int:
    """Fetch and validate layer 0 metadata into ``result``'s provenance (raises the typed
    errors above); returns the layer's maxRecordCount."""
    url = build_metadata_url()
    body = io.get(url)
    result.metadata_request_url, result.metadata_raw_digest = url, raw_body_digest(body)
    result.retrieved_at = io.retrieved_at
    doc = _parse_json_object(body, url=url, cid=io.cid)
    max_records, signals = _validate_metadata(doc, url=url, cid=io.cid)
    editing = doc.get("editingInfo")
    last_edit = editing.get("dataLastEditDate") if isinstance(editing, dict) else None
    if isinstance(last_edit, bool) or not isinstance(last_edit, int):
        last_edit = None
        signals.append("missing_editing_info")
    result.source_data_last_edited_ms = last_edit
    result.source_data_last_edited = _epoch_ms_to_rfc3339(last_edit)
    result.drift_signals.extend(signals)
    return max_records


def _geometry_vertex_count(esri: object) -> int:
    """DB-058(b): total vertices across all rings of an esri polygon geometry. A
    non-polygon / malformed shape counts 0 - it carries no retention risk and is typed
    downstream as an invalid geometry, never a resource refusal."""
    if not isinstance(esri, dict):
        return 0
    rings = esri.get("rings")
    if not isinstance(rings, list):
        return 0
    return sum(len(r) for r in rings if isinstance(r, list))


def _check_deadline(io: _Io) -> None:
    """DB-058(c): stop paging with a typed refusal once the caller wall-clock deadline is
    reached. A missing deadline never refuses. The injected clock is authoritative."""
    if io.deadline is not None and io.clock() >= io.deadline:
        raise DeadlineExceededError(
            "caller wall-clock deadline reached before the next page",
            correlation_id=io.cid, detail={"reason": "deadline_exceeded",
                                           "deadline": _rfc3339(io.deadline)})


def _parse_page(body: str, *, url: str, cid: str, page_size: int,
                drift_signals: list[str]) -> tuple[list[tuple[int, dict]], bool]:
    doc = _parse_json_object(body, url=url, cid=cid)
    features = doc.get("features")
    if not isinstance(features, list):
        raise MalformedResponseError("query response has no 'features' array",
                                     correlation_id=cid, detail={"url": url})
    if len(features) > page_size:
        raise PagingPathologyError(
            "page holds more features than the requested resultRecordCount",
            correlation_id=cid,
            detail={"url": url, "reason": "over_page_count", "returned": len(features),
                    "requested": page_size})
    sr = doc.get("spatialReference")
    if (features or sr is not None) and not (
        isinstance(sr, dict) and sr.get("wkid") == EXPECTED_WKID
        and sr.get("latestWkid") == EXPECTED_LATEST_WKID
    ):
        raise WrongCRSError(
            "query page is not wkid 102718 / latestWkid 2263; no coordinate is read",
            correlation_id=cid, detail={"url": url, "spatial_reference": _safe_repr(sr)})
    if doc.get("geometryType", EXPECTED_GEOMETRY_TYPE) != EXPECTED_GEOMETRY_TYPE:
        raise SchemaDriftError("query page geometryType is not esriGeometryPolygon",
                               correlation_id=cid, detail={"url": url})
    if doc.get("objectIdFieldName", OBJECT_ID_FIELD) != OBJECT_ID_FIELD:
        raise SchemaDriftError("query page objectIdFieldName is not OBJECTID",
                               correlation_id=cid, detail={"url": url})
    page: list[tuple[int, dict]] = []
    for index, feature in enumerate(features):
        attrs = feature.get("attributes") if isinstance(feature, dict) else None
        oid = attrs.get(OBJECT_ID_FIELD) if isinstance(attrs, dict) else None
        if isinstance(oid, bool) or not isinstance(oid, int):
            raise MalformedResponseError("feature lacks an attributes map with integer OBJECTID",
                                         correlation_id=cid,
                                         detail={"url": url, "feature_index": index})
        vertices = _geometry_vertex_count(feature.get("geometry"))
        if vertices > MAX_GEOMETRY_VERTICES:  # DB-058(b): before the geometry is retained
            raise ResourceBoundError(
                "a single footprint geometry exceeds the vertex cap; refused before retention",
                correlation_id=cid,
                detail={"url": url, "reason": "geometry_vertex_cap", "vertices": vertices,
                        "max_vertices": MAX_GEOMETRY_VERTICES})
        for name in attrs:
            signal = f"unknown_attribute:{_safe_repr(name, 64)}"
            if name not in REQUIRED_FIELDS and signal not in drift_signals:
                drift_signals.append(signal)
        page.append((oid, feature))
    return page, doc.get("exceededTransferLimit") is True


# ---------------------------------------------------------------------------
# Attribute typing (typed gaps and flags, never defaults)
# ---------------------------------------------------------------------------


def _gap(gaps: list[dict], name: str, code: str, raw: object) -> None:
    gaps.append({"field": name, "code": code, "raw": _safe_repr(raw)})


def _int_attr(attrs: dict, name: str, gaps: list[dict]) -> int | None:
    value = attrs.get(name)
    if value is None:
        _gap(gaps, name, "missing", value)
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        _gap(gaps, name, "malformed", value)
        return None
    return value


def _text_attr(attrs: dict, name: str, gaps: list[dict]) -> str | None:
    value = attrs.get(name)
    if isinstance(value, str) and value.strip():
        return value
    _gap(gaps, name, "missing" if value is None or value == "" else "malformed", value)
    return None


def _bbl_attr(attrs: dict, name: str, gaps: list[dict]) -> str | None:
    value = attrs.get(name)
    if value is None:
        _gap(gaps, name, "missing", value)
        return None
    try:
        if not isinstance(value, str):
            raise BBLValidationError("non_string", "BBL attribute is not text", value)
        return normalize_bbl(value).canonical
    except BBLValidationError:
        _gap(gaps, name, "unparseable_bbl", value)
        return None


def _height_attr(attrs: dict, gaps: list[dict]) -> float | None:
    value = attrs.get("HEIGHT_ROOF")
    number = _finite(value)
    if value is None:
        code = "height_roof_null_not_available"
    elif number is None:
        code = "height_roof_malformed"
    elif number == 0.0:
        code = "height_roof_zero_not_available"
    elif number < 0.0:
        code = "height_roof_negative"
    else:
        return number
    _gap(gaps, "HEIGHT_ROOF", code, value)
    return None


def _ground_attr(attrs: dict, gaps: list[dict], flags: list[str]) -> float | None:
    value = attrs.get("GROUND_ELEVATION")
    number = _finite(value)
    if number is None:
        _gap(gaps, "GROUND_ELEVATION", "missing" if value is None else "malformed", value)
        return None
    if number == 0.0:
        # Zero is not documented as "not available" for this field; kept, never guessed.
        flags.append("ground_elevation_zero_unverified")
    return number


def _build_building(oid: int, feature: dict, *, query: _Query, site_ground: float | None,
                    subject_bbl: str | None) -> ContextBuilding:
    attrs = feature["attributes"]
    gaps: list[dict] = []
    flags: list[str] = []
    doitt_id = _int_attr(attrs, "DOITT_ID", gaps)
    bin_number = _int_attr(attrs, "BIN", gaps)
    if bin_number in MILLION_BINS:
        flags.append("bin_unassigned_million_bin")
    base_bbl = _bbl_attr(attrs, "BASE_BBL", gaps)
    mappluto_bbl = _bbl_attr(attrs, "MAPPLUTO_BBL", gaps)
    if mappluto_bbl and CONDO_BILLING_LOT_MIN <= int(mappluto_bbl[6:]) <= CONDO_BILLING_LOT_MAX:
        flags.append("condo_billing_lot_join")  # joins the whole complex, never one unit
    if base_bbl and mappluto_bbl and base_bbl != mappluto_bbl:
        flags.append("mappluto_bbl_differs_from_base_bbl")
    joins_subject = None if subject_bbl is None or mappluto_bbl is None else (
        mappluto_bbl == subject_bbl)
    if subject_bbl and base_bbl == subject_bbl and mappluto_bbl not in (None, subject_bbl):
        flags.append("base_bbl_is_subject_but_mappluto_bbl_differs")
    feature_code = _int_attr(attrs, "FEATURE_CODE", gaps)
    label = FEATURE_CODE_LABELS.get(feature_code) if feature_code is not None else None
    if feature_code == PLACEHOLDER_FEATURE_CODE:
        _gap(gaps, "FEATURE_CODE", "placeholder_geometry_not_building_outline", feature_code)
    elif feature_code is not None and label is None:
        _gap(gaps, "FEATURE_CODE", "undocumented_feature_code", feature_code)
    height = _height_attr(attrs, gaps)
    ground = _ground_attr(attrs, gaps, flags)
    if site_ground is None:
        _gap(gaps, "site_ground_elevation_ft", "site_ground_not_supplied", None)
    relative_base = None if ground is None or site_ground is None else ground - site_ground
    relative_roof = None if relative_base is None or height is None else relative_base + height
    year = _int_attr(attrs, "CONSTRUCTION_YEAR", gaps)
    if year == 0:
        _gap(gaps, "CONSTRUCTION_YEAR", "zero_not_available", year)
        year = None
    last_edited_ms = attrs.get("LAST_EDITED_DATE")
    last_edited = _epoch_ms_to_rfc3339(last_edited_ms)
    if last_edited is None:
        _gap(gaps, "LAST_EDITED_DATE", "missing_or_malformed", last_edited_ms)
    esri = feature.get("geometry")
    status, findings, parts, geometry_flags = parse_footprint_geometry(esri)
    flags.extend(geometry_flags)
    relation, overlap = (None, None)
    if parts:
        relation, overlap = classify_query_relation(parts, query.shape)
        if relation == "disjoint_locally":
            flags.append("server_local_relation_disagreement")
    return ContextBuilding(
        object_id=oid, doitt_id=doitt_id, bin=bin_number, base_bbl=base_bbl,
        mappluto_bbl=mappluto_bbl, joins_subject_lot=joins_subject, feature_code=feature_code,
        feature_code_label=label, height_roof_ft=height, ground_elevation_ft=ground,
        relative_base_z_ft=relative_base, relative_roof_z_ft=relative_roof,
        construction_year=year, geom_source=_text_attr(attrs, "GEOM_SOURCE", gaps),
        last_edited=last_edited, last_status_type=_text_attr(attrs, "LAST_STATUS_TYPE", gaps),
        geometry_status=status, geometry_findings=findings, parts=parts,
        footprint_area_sq_ft=sum(p.area_sq_ft for p in parts) if parts else None,
        query_relation=relation, query_overlap_area_sq_ft=overlap, flags=flags, gaps=gaps,
        attributes=dict(attrs), original_geometry=esri,
        original_geometry_digest=canonical_json_digest(esri),
        untrusted_text_fields=UNTRUSTED_TEXT_FIELDS)


# ---------------------------------------------------------------------------
# Public operation
# ---------------------------------------------------------------------------


def _check_page_size(page_size: object, cid: str) -> None:
    if isinstance(page_size, bool) or not isinstance(page_size, int) or not (
        1 <= page_size <= MAX_PAGE_SIZE
    ):
        raise DisallowedRequestError(f"page_size must be an integer in 1..{MAX_PAGE_SIZE}",
                                     correlation_id=cid, detail={"value": _safe_repr(page_size)})


def _validate_inputs(site_ground: object, subject_bbl: object, page_size: object,
                     cid: str) -> tuple[float | None, str | None]:
    ground = _finite(site_ground)
    if site_ground is not None and ground is None:
        raise DisallowedRequestError("site_ground_elevation_ft must be a finite number or None",
                                     correlation_id=cid, detail={"value": _safe_repr(site_ground)})
    subject = None
    if subject_bbl is not None:
        try:
            subject = normalize_bbl(subject_bbl).canonical
        except BBLValidationError as exc:
            raise DisallowedRequestError("subject_bbl is not a valid BBL", correlation_id=cid,
                                         detail={"code": exc.code}) from exc
    if page_size is not None:
        _check_page_size(page_size, cid)
    return ground, subject


def _validate_deadline(deadline: object, cid: str) -> None:
    """DB-073(d): a caller ``deadline`` must be a TIMEZONE-AWARE datetime. A tz-naive datetime
    would raise ``TypeError`` when compared against the tz-aware clock in :func:`_check_deadline`
    and surface as a generic ``internal_error``; refuse it up front as a typed
    ``disallowed_request`` (before any I/O), naming the fault (M5-T101 G3 A2). ``None`` never
    refuses."""
    if deadline is None:
        return
    if (not isinstance(deadline, datetime) or deadline.tzinfo is None
            or deadline.utcoffset() is None):
        raise DisallowedRequestError(
            "deadline must be a timezone-aware datetime; a tz-naive value is refused, never "
            "compared", correlation_id=cid,
            detail={"reason": "tz_naive_deadline", "value": _safe_repr(deadline)})


def _collect_pages(io: _Io, query: _Query, size: int,
                   result: ContextBuildingsResult) -> list[tuple[int, dict]]:
    """Deterministic resultOffset paging with loop-safety guarantees (every violation is a
    typed paging_pathology: repeated OBJECTIDs, an empty page claiming more data, the page
    ceiling, or more footprints than MAX_CONTEXT_BUILDINGS - never truncation)."""
    collected: list[tuple[int, dict]] = []
    seen: set[int] = set()
    decoded_bytes = 0
    while True:
        _check_deadline(io)  # DB-058(c): caller wall-clock deadline, before each page
        if result.pages_fetched >= HARD_MAX_PAGES:
            raise PagingPathologyError("page ceiling reached; refusing to loop further",
                                       correlation_id=io.cid,
                                       detail={"reason": "page_ceiling",
                                               "pages": result.pages_fetched})
        url = _query_url(query, page_size=size, offset=len(collected))
        body = io.get(url)
        result.pages_fetched += 1
        result.request_urls.append(url)
        result.raw_digests.append(raw_body_digest(body))
        result.retrieved_at = io.retrieved_at
        decoded_bytes += len(body.encode("utf-8"))  # DB-058(b): cumulative retention bound
        if decoded_bytes > MAX_TOTAL_DECODED_BYTES:
            raise ResourceBoundError(
                "cumulative decoded page bytes exceed the ceiling; refused before retention",
                correlation_id=io.cid,
                detail={"url": url, "reason": "cumulative_bytes_ceiling",
                        "decoded_bytes": decoded_bytes, "max_bytes": MAX_TOTAL_DECODED_BYTES})
        page, exceeded = _parse_page(body, url=url, cid=io.cid, page_size=size,
                                     drift_signals=result.drift_signals)
        oids = [oid for oid, _ in page]
        repeated = sorted(set(oids) & seen) or sorted({o for o in oids if oids.count(o) > 1})
        if repeated or (not page and exceeded):
            raise PagingPathologyError(
                "paging made no clean progress (repeated OBJECTIDs or an empty page that "
                "claims more data)", correlation_id=io.cid,
                detail={"url": url, "object_ids": repeated[:20],
                        "reason": "repeated_object_ids" if repeated else "zero_progress"})
        collected.extend(page)
        seen.update(oids)
        if len(collected) > MAX_CONTEXT_BUILDINGS:
            raise PagingPathologyError(
                f"more than {MAX_CONTEXT_BUILDINGS} footprints; refused, never truncated",
                correlation_id=io.cid, detail={"reason": "over_feature_cap", "url": url})
        if not exceeded:
            return collected


def fetch_context_buildings(
    *,
    envelope: object = None,
    polygon: object = None,
    site_ground_elevation_ft: object = None,
    subject_bbl: object = None,
    page_size: int | None = None,
    transport: Transport = urllib_transport,
    timeout: float = 30.0,
    max_attempts: int = 3,
    interactive: bool = False,
    deadline: datetime | None = None,
    backoff_base: float = 0.5,
    backoff_cap: float = 30.0,
    retry_after_cap: float = 120.0,
    rng: Random | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = _utc_now,
    correlation_id: str | None = None,
    budget: AnalysisBudget | None = None,
) -> ContextBuildingsResult:
    """Footprints intersecting an EPSG:2263 ``envelope`` (xmin, ymin, xmax, ymax) or closed
    ``polygon`` ring, as typed context buildings on the relative datum of
    ``site_ground_elevation_ft``. ``subject_bbl`` (optional) marks MapPLUTO joins. Input is
    validated before any I/O; metadata is fetched and validated before any page. Returns
    status ``ok`` or ``refused``; never raises.

    Interactive callers pass ``interactive=True`` to cap upstream attempts at
    ``INTERACTIVE_MAX_ATTEMPTS`` (fail fast, DB-058 c) and may pass a tz-aware wall-clock
    ``deadline`` (``datetime``) that stops paging with a typed ``deadline_exceeded`` refusal,
    checked against ``clock`` before each page. ``correlation_id`` is untrusted: CR/LF and
    control characters are stripped (DB-058 d / DB-066 b) before it reaches any log site."""
    cid = _safe_correlation_id(correlation_id)
    effective_attempts = (
        min(max_attempts, INTERACTIVE_MAX_ATTEMPTS) if interactive else max_attempts)
    io = _Io(transport, timeout, effective_attempts, backoff_base, backoff_cap, retry_after_cap,
             rng or Random(), sleep, clock, budget, cid, deadline=deadline)
    result = ContextBuildingsResult(
        status="ok", buildings=[], refusal=None, correlation_id=cid, query=None,
        site_ground_elevation_ft=None, subject_bbl=None, metadata_request_url=None,
        metadata_raw_digest=None, request_urls=[], raw_digests=[], retrieved_at=None,
        source_data_last_edited_ms=None, source_data_last_edited=None, pages_fetched=0,
        drift_signals=[])
    try:
        site_ground, subject = _validate_inputs(site_ground_elevation_ft, subject_bbl,
                                                page_size, cid)
        _validate_deadline(deadline, cid)  # DB-073(d): tz-naive deadline -> typed refusal
        query = _build_query(envelope, polygon, cid)
        result.query, result.site_ground_elevation_ft, result.subject_bbl = (
            query.echo, site_ground, subject)
        _check_deadline(io)  # DB-073(c): honour the deadline BEFORE the metadata fetch too
        max_records = _fetch_layer_metadata(io, result)
        size = min(page_size or MAX_PAGE_SIZE, max_records)
        collected = _collect_pages(io, query, size, result)
        result.buildings = [
            _build_building(oid, feature, query=query, site_ground=site_ground,
                            subject_bbl=subject)
            for oid, feature in sorted(collected, key=lambda pair: pair[0])
        ]
        return result
    except Exception as exc:  # fail closed: every failure becomes a typed refusal
        if isinstance(exc, BuildingFootprintConnectorError):
            error = exc
        else:
            # DB-058(e) / G3-A1: an UNEXPECTED (non-typed) exception is a genuine bug.
            # Make it findable in production at error level - the exception class and a
            # length-bounded sanitized message (the shared transport's sanitizer), plus
            # the correlation id - WITHOUT ever rendering str(exc): the exception message
            # can echo upstream body text, so only the class name is logged (the returned
            # refusal still carries only that class name - the G5-safe non-disclosure
            # choice). No upstream body text reaches the log and a control character
            # cannot forge a log line.
            logger.error(
                "building_footprints internal_error class=%s message=%s correlation_id=%s",
                _sanitized_bounded(type(exc).__name__),
                _sanitized_bounded(_INTERNAL_ERROR_LOG_MESSAGE), cid)
            error = BuildingFootprintConnectorError(
                "unexpected internal failure; no data is returned", correlation_id=cid,
                detail={"exception": type(exc).__name__})
        result.status, result.buildings = "refused", []
        result.refusal = FootprintRefusal(
            error_type=error.error_type, message=error.message, correlation_id=cid,
            detail=error.detail, request_url=io.url,
            retrieved_at=io.retrieved_at or _refusal_time(io), raw_digest=io.digest)
        return result
