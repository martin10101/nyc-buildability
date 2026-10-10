"""MapPLUTO neighbouring-lot WINDOW connector - official DCP_GIS ArcGIS
MAPPLUTO feature service (task M5-T154, D-090-R936/R937).

SIBLING of :mod:`app.connectors.mappluto_geometry_arcgis` (the per-BBL
measurement connector), which this module imports and NEVER changes (that file
is in the modularity size baseline). Where the parent queries ONE lot by BBL,
this module queries every tax lot whose outline intersects an EPSG:2263
``envelope`` around the subject lot (its bounding box plus a padding), so the
report can draw the lot among its neighbours (DB-222).

Design commitments:

1. REQUEST - an explicit out-field allowlist (never ``*``): OBJECTID, BBL,
   Block, Lot, Address, Version. The owner-name field is NEVER requested or
   stored (no personal field). The spatial filter is ``esriSpatialRelIntersects``
   on a validated EPSG:2263 envelope, ``inSR=2263`` / ``outSR=2263``, deterministic
   ``OBJECTID ASC`` ordering and bounded ``resultOffset`` paging.
2. CRS - every non-empty query page must report wkid 102718 / latestWkid 2263
   (EPSG:2263, US survey feet) or it is refused BEFORE any coordinate is read.
   There is no reprojection path.
3. GEOMETRY PRESERVED VERBATIM - each lot's esri polygon rings are read exactly
   as transported (floats preserve the parsed value); they are NEVER quantized,
   repaired or re-oriented (the display/context map keeps the source outline
   unchanged, M5-T154 risk note). A malformed ring refuses the WHOLE query with
   a typed error; no partial result is returned.
4. SUBJECT EXCLUDED - the subject lot (``subject_bbl``) is returned separately on
   the result (:attr:`MapPlutoWindowResult.subject`), NEVER among the
   neighbouring :attr:`MapPlutoWindowResult.lots`. Each neighbour appears once.
5. FAIL BY RAISING - transport faults, ArcGIS error objects, malformed JSON, a
   wrong CRS, schema drift, paging pathologies and malformed geometry each raise
   a typed :class:`MapPlutoWindowConnectorError`; the report provider catches it
   and demotes the layer to ``not_available`` (it never crashes the report).

PROVENANCE - the dataset's own last-edit epoch (service
``editingInfo.dataLastEditDate`` ms) rides on the result for the map document's
per-layer provenance block. Deterministic code only: no AI, no legal
interpretation. The official DCP disclaimer applies (informational only).
"""

from __future__ import annotations

import logging
import time
import urllib.parse
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from math import isfinite
from random import Random

from app.connectors.bbl import BBLValidationError, normalize_bbl

# Read-only reuse of the parent connector's pinned official channel, CRS stamp
# and raw-body digest. The parent module is NOT modified by this task.
from app.connectors.mappluto_geometry_arcgis import (
    CRS_STAMP,
    EXPECTED_LATEST_WKID,
    EXPECTED_WKID,
    LAYER_NAME,
    SERVICE_ROOT,
    SOURCE_ID,
    raw_body_digest,
)
from app.connectors.pluto_soda import canonical_json_digest
from app.resilience.budget import AnalysisBudget
from app.resilience.transport import (
    Transport,
    jittered_retry_after_delay,
    request_with_retry,
    standard_retry_hooks,
    urllib_transport,
)

__all__ = [
    "MAX_PAGE_SIZE",
    "MAX_QUERY_SPAN_FT",
    "MAX_WINDOW_LOTS",
    "OUT_FIELDS",
    "CircuitOpenError",
    "DisallowedRequestError",
    "MalformedGeometryError",
    "MalformedResponseError",
    "MapPlutoWindowConnectorError",
    "MapPlutoWindowResult",
    "PagingPathologyError",
    "RateLimitedError",
    "RequestBudgetExceededError",
    "SchemaDriftError",
    "SourceTimeoutError",
    "UpstreamError",
    "WindowLot",
    "WrongCRSError",
    "build_metadata_url",
    "build_window_query_url",
    "fetch_window_lots",
]

logger = logging.getLogger("app.connectors.mappluto_window_arcgis")

# Dataset id for the per-layer provenance block (the queried layer).
DATASET_ID = f"{LAYER_NAME}/FeatureServer/0"
EXPECTED_GEOMETRY_TYPE = "esriGeometryPolygon"
OBJECT_ID_FIELD = "OBJECTID"
SPATIAL_REL = "esriSpatialRelIntersects"

# Out-field allowlist. OwnerName (and every other personal field) is DELIBERATELY
# absent and is never requested or stored (S1). BBL is served as a double.
OUT_FIELDS = ("OBJECTID", "BBL", "Block", "Lot", "Address", "Version")
# The esri field types these fields must still carry (schema-drift gate).
REQUIRED_FIELDS: dict[str, str] = {
    "OBJECTID": "esriFieldTypeOID",
    "BBL": "esriFieldTypeDouble",
    "Block": "esriFieldTypeInteger",
    "Lot": "esriFieldTypeSmallInteger",
    "Address": "esriFieldTypeString",
    "Version": "esriFieldTypeString",
}

# Engineering bounds (not source facts): a lot-plus-neighbours window stays small.
MAX_QUERY_SPAN_FT = 5_000.0
COORD_ABS_MAX_FT = 1.0e8
MAX_PAGE_SIZE = 2000
HARD_MAX_PAGES = 50
MAX_WINDOW_LOTS = 5000  # beyond this the query is refused, never truncated

INTERACTIVE_MAX_ATTEMPTS = 1


# ---------------------------------------------------------------------------
# Typed error taxonomy (aligned with the parent connector's names)
# ---------------------------------------------------------------------------


class MapPlutoWindowConnectorError(Exception):
    """Base typed connector error. Payloads never contain stack traces,
    headers or tokens (the service is keyless; no token exists)."""

    error_type = "upstream_error"

    def __init__(self, message: str, *, correlation_id: str, detail: dict | None = None) -> None:
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


class UpstreamError(MapPlutoWindowConnectorError):
    """Network failure, unexpected HTTP status, or an ArcGIS error object
    (an error delivered even with HTTP 200 is an upstream error, not data)."""

    error_type = "upstream_error"


class MalformedResponseError(MapPlutoWindowConnectorError):
    """Body is not the documented shape; never converted into an empty result."""

    error_type = "malformed_response"


class SchemaDriftError(MapPlutoWindowConnectorError):
    """Layer contract changed (name, geometry type, fields, types, paging caps)."""

    error_type = "schema_drift"


class WrongCRSError(MapPlutoWindowConnectorError):
    """A query page is not wkid 102718 / latestWkid 2263; no coordinate is read."""

    error_type = "wrong_crs"


class MalformedGeometryError(MapPlutoWindowConnectorError):
    """A feature's esri polygon rings are malformed. Refuses the WHOLE query; no
    partial result is returned (the context outline is never partially salvaged)."""

    error_type = "malformed_geometry"


class RateLimitedError(MapPlutoWindowConnectorError):
    error_type = "rate_limited"


class SourceTimeoutError(MapPlutoWindowConnectorError):
    error_type = "timeout"


class RequestBudgetExceededError(MapPlutoWindowConnectorError):
    error_type = "budget_exhausted"


class CircuitOpenError(MapPlutoWindowConnectorError):
    error_type = "circuit_open"


class DisallowedRequestError(MapPlutoWindowConnectorError):
    """Caller input refused BEFORE any network I/O (the connector builds every
    URL itself from the pinned root and a validated envelope)."""

    error_type = "disallowed_request"


class PagingPathologyError(MapPlutoWindowConnectorError):
    """Over-page count, repeated OBJECTIDs, zero progress, page ceiling or the
    window lot cap. Never a silent truncation."""

    error_type = "paging_pathology"


# ---------------------------------------------------------------------------
# Result contracts
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WindowLot:
    """One tax lot in the window: identity plus its verbatim EPSG:2263 outline.

    ``outline`` is the feature's esri polygon rings exactly as transported
    (exterior ring first, then the source's remaining rings); it is never
    quantized, repaired or re-oriented. No owner name or any personal field is
    carried."""

    object_id: int
    bbl: str
    block: int | None
    lot: int | None
    address: str | None
    version: str | None
    outline: list[list[list[float]]]
    original_geometry_digest: str


@dataclass
class MapPlutoWindowResult:
    """Window query result. ``lots`` are the neighbouring tax lots (the subject
    is excluded and carried separately on ``subject``); each lot appears once.
    ``source_data_last_edited`` is dataset-freshness provenance only."""

    status: str  # always "ok" (failures raise)
    subject: WindowLot | None
    lots: list[WindowLot]
    subject_bbl: str
    envelope: tuple[float, float, float, float]
    correlation_id: str
    metadata_request_url: str
    request_urls: list[str]
    raw_digests: list[str]
    metadata_raw_digest: str
    retrieved_at: str
    source_data_last_edited_ms: int | None
    source_data_last_edited: str | None
    pages_fetched: int
    drift_signals: list[str] = field(default_factory=list)
    source_id: str = SOURCE_ID
    dataset_id: str = DATASET_ID
    crs: dict = field(default_factory=lambda: dict(CRS_STAMP))

    def provenance(self) -> dict:
        """The provenance quintuple: source, request, retrieved_at, dataset last
        edit, digest (the first query page is the drawn-features source)."""
        return {
            "source": {"source_id": self.source_id, "dataset_id": self.dataset_id,
                       "service_root": SERVICE_ROOT},
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


def _safe_repr(value: object, limit: int = 200) -> str:
    return repr(value)[:limit]


def _finite(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    number = float(value)
    return number if isfinite(number) else None


# ---------------------------------------------------------------------------
# URL construction (every URL is built here, byte-identical to the recording)
# ---------------------------------------------------------------------------


def build_metadata_url() -> str:
    return f"{SERVICE_ROOT}/{LAYER_NAME}/FeatureServer/0?f=json"


def _validate_envelope(
    envelope: object, *, correlation_id: str
) -> tuple[float, float, float, float]:
    if not isinstance(envelope, list | tuple) or len(envelope) != 4:
        raise DisallowedRequestError(
            "envelope must be a 4-item (xmin, ymin, xmax, ymax) sequence",
            correlation_id=correlation_id, detail={"envelope": _safe_repr(envelope)})
    values: list[float] = []
    for axis, component in zip(("xmin", "ymin", "xmax", "ymax"), envelope, strict=True):
        number = _finite(component)
        if number is None or abs(number) > COORD_ABS_MAX_FT:
            raise DisallowedRequestError(
                f"envelope {axis} must be a finite EPSG:2263 coordinate within "
                f"|{COORD_ABS_MAX_FT:g}| ft", correlation_id=correlation_id,
                detail={"axis": axis, "value": _safe_repr(component)})
        values.append(float(f"{number:.4f}"))
    xmin, ymin, xmax, ymax = values
    if not (xmin < xmax and ymin < ymax):
        raise DisallowedRequestError(
            "envelope must have xmin < xmax and ymin < ymax",
            correlation_id=correlation_id, detail={"envelope": [xmin, ymin, xmax, ymax]})
    if max(xmax - xmin, ymax - ymin) > MAX_QUERY_SPAN_FT:
        raise DisallowedRequestError(
            f"query extent exceeds {MAX_QUERY_SPAN_FT:g} ft; a window covers one lot "
            "and its neighbours", correlation_id=correlation_id,
            detail={"envelope": [xmin, ymin, xmax, ymax]})
    return xmin, ymin, xmax, ymax


def build_window_query_url(
    envelope: object, *, page_size: int = MAX_PAGE_SIZE, offset: int = 0,
    correlation_id: str = "urlbuild",
) -> str:
    """The ONLY query URL shape this connector emits. The out-field set never
    includes an owner name. Raises :class:`DisallowedRequestError` on bad input."""
    xmin, ymin, xmax, ymax = _validate_envelope(envelope, correlation_id=correlation_id)
    _check_page_size(page_size, correlation_id)
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise DisallowedRequestError("offset must be a non-negative integer",
                                     correlation_id=correlation_id)
    params = (
        ("where", "1=1"),
        ("geometry", f"{xmin:.4f},{ymin:.4f},{xmax:.4f},{ymax:.4f}"),
        ("geometryType", "esriGeometryEnvelope"),
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
    return f"{SERVICE_ROOT}/{LAYER_NAME}/FeatureServer/0/query?{encoded}"


def _check_page_size(page_size: object, correlation_id: str) -> None:
    if isinstance(page_size, bool) or not isinstance(page_size, int) or not (
        1 <= page_size <= MAX_PAGE_SIZE
    ):
        raise DisallowedRequestError(f"page_size must be an integer in 1..{MAX_PAGE_SIZE}",
                                     correlation_id=correlation_id,
                                     detail={"value": _safe_repr(page_size)})


# ---------------------------------------------------------------------------
# Transport (the shared bounded-retry engine) + parsing
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
    retrieved_at: str | None = None

    def get(self, url: str) -> str:
        response = request_with_retry(
            url,
            transport=self.transport,
            headers={"Accept": "application/json"},
            timeout=self.timeout,
            max_attempts=self.max_attempts,
            hooks=standard_retry_hooks(
                logger=logger, log_label="mappluto_window", correlation_id=self.cid, url=url,
                sanitize_network_reason=_safe_repr,
                rate_limited_error=RateLimitedError,
                rate_limited_message=("official ArcGIS service throttled the request "
                                      "(HTTP 429) and the retry budget is exhausted"),
                timeout_error=SourceTimeoutError,
                timeout_message="ArcGIS request timed out and the retry budget is exhausted",
                unavailable_error=UpstreamError,
                unavailable_message=("official ArcGIS service unavailable and the retry "
                                     "budget is exhausted"),
                include_reason_kind=True,
                unexpected_status_message=("unexpected HTTP status {status} from the "
                                           "official ArcGIS service"),
                budget_error=RequestBudgetExceededError,
            ),
            compute_delay=jittered_retry_after_delay(
                backoff_base=self.backoff_base, backoff_cap=self.backoff_cap,
                retry_after_cap=self.retry_after_cap, rng=self.rng, wall_clock=self.clock),
            sleep=self.sleep,
            budget=self.budget,
        )
        self.retrieved_at = _rfc3339(self.clock())
        return response.body


def _parse_json_object(body: str, *, url: str, cid: str) -> dict:
    import json

    try:
        doc = json.loads(body)
    except (ValueError, RecursionError) as exc:
        raise MalformedResponseError(
            "ArcGIS returned a body that is not valid JSON; refusing to interpret it",
            correlation_id=cid, detail={"url": url, "parse_error": type(exc).__name__}) from exc
    if not isinstance(doc, dict):
        raise MalformedResponseError("ArcGIS response is not a JSON object",
                                     correlation_id=cid, detail={"url": url})
    error = doc.get("error")
    if error is not None:
        code = error.get("code") if isinstance(error, dict) else None
        message = error.get("message") if isinstance(error, dict) else None
        raise UpstreamError(
            "ArcGIS returned an error object (an error delivered with HTTP 200 is an "
            "upstream error, not data)", correlation_id=cid,
            detail={"url": url, "arcgis_error_code": code if isinstance(code, int) else repr(code),
                    "arcgis_error_message": _safe_repr(message)})
    return doc


def _validate_metadata(doc: dict, *, url: str, cid: str) -> tuple[int, int | None, list[str]]:
    def drift(message: str, **detail: object) -> SchemaDriftError:
        return SchemaDriftError(message, correlation_id=cid, detail={"url": url, **detail})

    if doc.get("name") != LAYER_NAME:
        raise drift("service metadata 'name' is not the canonical MAPPLUTO layer",
                    name=_safe_repr(doc.get("name")))
    if doc.get("geometryType") != EXPECTED_GEOMETRY_TYPE:
        raise drift("layer geometryType is not esriGeometryPolygon")
    if doc.get("objectIdField") != OBJECT_ID_FIELD:
        raise drift("layer objectIdField is not OBJECTID")
    fields = doc.get("fields")
    if not isinstance(fields, list):
        raise drift("layer metadata has no fields array")
    live = {entry["name"]: str(entry.get("type")) for entry in fields
            if isinstance(entry, dict) and isinstance(entry.get("name"), str)}
    missing = sorted(set(REQUIRED_FIELDS) - set(live))
    retyped = sorted(n for n in REQUIRED_FIELDS if n in live and live[n] != REQUIRED_FIELDS[n])
    if missing or retyped:
        raise drift("required field(s) missing or re-typed", missing=missing,
                    retyped={n: live[n] for n in retyped})
    max_records = doc.get("maxRecordCount")
    if isinstance(max_records, bool) or not isinstance(max_records, int) or max_records < 1:
        raise drift("maxRecordCount missing or invalid", max_record_count=_safe_repr(max_records))
    editing = doc.get("editingInfo")
    last_edit = editing.get("dataLastEditDate") if isinstance(editing, dict) else None
    signals: list[str] = []
    if isinstance(last_edit, bool) or not isinstance(last_edit, int):
        last_edit = None
        signals.append("missing_editing_info")
    return max_records, last_edit, signals


def _window_polygon(esri: object, *, cid: str, oid: object) -> list[list[list[float]]]:
    """Validate and return the feature's esri polygon rings VERBATIM (floats
    preserve the parsed value). A malformed ring refuses the whole query."""
    if not isinstance(esri, dict) or "rings" not in esri:
        raise MalformedGeometryError(
            "feature geometry is not an esri polygon (no 'rings')",
            correlation_id=cid, detail={"object_id": _safe_repr(oid)})
    rings = esri["rings"]
    if not isinstance(rings, list) or not rings:
        raise MalformedGeometryError("feature geometry has no rings",
                                     correlation_id=cid, detail={"object_id": _safe_repr(oid)})
    out: list[list[list[float]]] = []
    for ring in rings:
        if not isinstance(ring, list) or len(ring) < 4:
            raise MalformedGeometryError(
                "a polygon ring is not a closed list of at least 4 vertices",
                correlation_id=cid, detail={"object_id": _safe_repr(oid)})
        points: list[list[float]] = []
        for vertex in ring:
            if not isinstance(vertex, list | tuple) or len(vertex) < 2:
                raise MalformedGeometryError("a ring vertex is not an [x, y] pair",
                                             correlation_id=cid,
                                             detail={"object_id": _safe_repr(oid)})
            x, y = _finite(vertex[0]), _finite(vertex[1])
            if x is None or y is None:
                raise MalformedGeometryError("a ring vertex is non-numeric or non-finite",
                                             correlation_id=cid,
                                             detail={"object_id": _safe_repr(oid)})
            points.append([x, y])
        if points[0] != points[-1]:
            raise MalformedGeometryError("a polygon ring is not closed (first != last vertex)",
                                         correlation_id=cid, detail={"object_id": _safe_repr(oid)})
        out.append(points)
    return out


def _int_attr(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _str_attr(value: object) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _bbl_from_double(value: object, *, cid: str, oid: object) -> str:
    number = _finite(value)
    if number is None:
        raise MalformedResponseError("feature carries no numeric BBL",
                                     correlation_id=cid, detail={"object_id": _safe_repr(oid)})
    try:
        return normalize_bbl(str(int(round(number)))).canonical
    except BBLValidationError as exc:
        raise MalformedResponseError("feature BBL is not a valid 10-digit BBL",
                                     correlation_id=cid,
                                     detail={"object_id": _safe_repr(oid), "code": exc.code}
                                     ) from exc


def _build_lot(feature: dict, *, cid: str) -> WindowLot:
    attrs = feature.get("attributes") if isinstance(feature, dict) else None
    oid = attrs.get(OBJECT_ID_FIELD) if isinstance(attrs, dict) else None
    if isinstance(oid, bool) or not isinstance(oid, int):
        raise MalformedResponseError("feature lacks an attributes map with integer OBJECTID",
                                     correlation_id=cid, detail={"feature": _safe_repr(feature)})
    outline = _window_polygon(feature.get("geometry"), cid=cid, oid=oid)
    return WindowLot(
        object_id=oid,
        bbl=_bbl_from_double(attrs.get("BBL"), cid=cid, oid=oid),
        block=_int_attr(attrs.get("Block")),
        lot=_int_attr(attrs.get("Lot")),
        address=_str_attr(attrs.get("Address")),
        version=_str_attr(attrs.get("Version")),
        outline=outline,
        original_geometry_digest=canonical_json_digest(feature.get("geometry")),
    )


def _parse_page(
    body: str, *, url: str, cid: str, page_size: int
) -> tuple[list[tuple[int, dict]], bool]:
    doc = _parse_json_object(body, url=url, cid=cid)
    features = doc.get("features")
    if not isinstance(features, list):
        raise MalformedResponseError("query response has no 'features' array",
                                     correlation_id=cid, detail={"url": url})
    if len(features) > page_size:
        raise PagingPathologyError(
            "page holds more features than the requested resultRecordCount",
            correlation_id=cid, detail={"url": url, "reason": "over_page_count",
                                        "returned": len(features), "requested": page_size})
    sr = doc.get("spatialReference")
    if (features or sr is not None) and not (
        isinstance(sr, dict) and sr.get("wkid") == EXPECTED_WKID
        and sr.get("latestWkid") == EXPECTED_LATEST_WKID
    ):
        raise WrongCRSError("query page is not wkid 102718 / latestWkid 2263; no coordinate "
                            "is read", correlation_id=cid,
                            detail={"url": url, "spatial_reference": _safe_repr(sr)})
    if doc.get("geometryType", EXPECTED_GEOMETRY_TYPE) != EXPECTED_GEOMETRY_TYPE:
        raise SchemaDriftError("query page geometryType is not esriGeometryPolygon",
                               correlation_id=cid, detail={"url": url})
    page: list[tuple[int, dict]] = []
    for index, feature in enumerate(features):
        attrs = feature.get("attributes") if isinstance(feature, dict) else None
        oid = attrs.get(OBJECT_ID_FIELD) if isinstance(attrs, dict) else None
        if isinstance(oid, bool) or not isinstance(oid, int):
            raise MalformedResponseError("feature lacks an attributes map with integer OBJECTID",
                                         correlation_id=cid,
                                         detail={"url": url, "feature_index": index})
        page.append((oid, feature))
    return page, doc.get("exceededTransferLimit") is True


def _collect_pages(io: _Io, envelope: tuple[float, float, float, float], size: int,
                   result: MapPlutoWindowResult) -> list[tuple[int, dict]]:
    collected: list[tuple[int, dict]] = []
    seen: set[int] = set()
    while True:
        if result.pages_fetched >= HARD_MAX_PAGES:
            raise PagingPathologyError("page ceiling reached; refusing to loop further",
                                       correlation_id=io.cid,
                                       detail={"reason": "page_ceiling",
                                               "pages": result.pages_fetched})
        url = build_window_query_url(envelope, page_size=size, offset=len(collected),
                                     correlation_id=io.cid)
        body = io.get(url)
        result.pages_fetched += 1
        result.request_urls.append(url)
        result.raw_digests.append(raw_body_digest(body))
        result.retrieved_at = io.retrieved_at
        page, exceeded = _parse_page(body, url=url, cid=io.cid, page_size=size)
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
        if len(collected) > MAX_WINDOW_LOTS:
            raise PagingPathologyError(
                f"more than {MAX_WINDOW_LOTS} lots in the window; refused, never truncated",
                correlation_id=io.cid, detail={"reason": "over_feature_cap", "url": url})
        if not exceeded:
            return collected


def fetch_window_lots(
    *,
    envelope: tuple[float, float, float, float],
    subject_bbl: str,
    page_size: int | None = None,
    transport: Transport = urllib_transport,
    timeout: float = 30.0,
    max_attempts: int = 3,
    interactive: bool = False,
    backoff_base: float = 0.5,
    backoff_cap: float = 30.0,
    retry_after_cap: float = 120.0,
    rng: Random | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = _utc_now,
    correlation_id: str | None = None,
    budget: AnalysisBudget | None = None,
) -> MapPlutoWindowResult:
    """Fetch every MAPPLUTO tax lot whose outline intersects ``envelope``
    (EPSG:2263 ``(xmin, ymin, xmax, ymax)``), returning the neighbours (subject
    excluded) and the subject lot separately. Metadata is fetched and validated
    before any page. RAISES a typed :class:`MapPlutoWindowConnectorError` on any
    transport fault, ArcGIS error object, wrong CRS, schema drift, paging
    pathology or malformed geometry; never returns a partial result.

    ``subject_bbl`` is the canonical 10-digit BBL of the subject lot. Interactive
    callers pass ``interactive=True`` to cap upstream attempts (fail fast)."""
    cid = correlation_id or uuid.uuid4().hex
    try:
        subject = normalize_bbl(subject_bbl).canonical
    except BBLValidationError as exc:
        raise DisallowedRequestError("subject_bbl is not a valid BBL", correlation_id=cid,
                                     detail={"code": exc.code}) from exc
    checked_envelope = _validate_envelope(envelope, correlation_id=cid)
    if page_size is not None:
        _check_page_size(page_size, cid)
    effective_attempts = (min(max_attempts, INTERACTIVE_MAX_ATTEMPTS)
                          if interactive else max_attempts)
    io = _Io(transport, timeout, effective_attempts, backoff_base, backoff_cap, retry_after_cap,
             rng or Random(), sleep, clock, budget, cid)

    meta_url = build_metadata_url()
    meta_body = io.get(meta_url)
    meta_doc = _parse_json_object(meta_body, url=meta_url, cid=cid)
    max_records, last_edit_ms, drift = _validate_metadata(meta_doc, url=meta_url, cid=cid)
    result = MapPlutoWindowResult(
        status="ok", subject=None, lots=[], subject_bbl=subject, envelope=checked_envelope,
        correlation_id=cid, metadata_request_url=meta_url, request_urls=[], raw_digests=[],
        metadata_raw_digest=raw_body_digest(meta_body), retrieved_at=io.retrieved_at or "",
        source_data_last_edited_ms=last_edit_ms,
        source_data_last_edited=_epoch_ms_to_rfc3339(last_edit_ms),
        pages_fetched=0, drift_signals=drift)

    size = min(page_size or MAX_PAGE_SIZE, max_records)
    collected = _collect_pages(io, checked_envelope, size, result)
    result.retrieved_at = io.retrieved_at or result.retrieved_at

    neighbours: list[WindowLot] = []
    for _oid, feature in sorted(collected, key=lambda pair: pair[0]):
        lot = _build_lot(feature, cid=cid)
        if lot.bbl == subject:
            if result.subject is None:
                result.subject = lot
            continue
        neighbours.append(lot)
    result.lots = neighbours
    return result
