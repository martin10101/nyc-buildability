"""DCM Street Center Line street-width / mapped-street-status connector
(task M4-T015, D-045-R003 B2; pinned research
``project-control/reports/M4-T013-street-width-research.md``).

Channel: the official DCP_GIS ArcGIS feature service
``DCM_Street_Center_Line/FeatureServer/0`` (RECOMMENDED PRIMARY per the
research; the Socrata ``g6zj-tzgn`` companion is the documented-stale
fallback and is NOT queried here - out of scope for this connector). Keyless,
EPSG:2263 native (wkid 102718 / latestWkid 2263), geoJSON-capable, monthly
update cadence per the official metadata (research E3/E5).

CENTRAL OBLIGATION - the authoritative ``Streetwidth`` field is FREE TEXT
(research E7): this module NEVER classifies width itself. Every raw value is
handed VERBATIM to the pure classifier
(:mod:`app.connectors.dcm_street_width_classifier`), which fails closed to
narrow on anything but a mathematically-certain >= 75 ft reading. This module
adds exactly one more fail-closed rule on top: a segment that is not a
CURRENTLY MAPPED street (``Feat_Type`` != ``Mapped_St``) or that carries a
paper-street or record-street flag (``Paper_ST`` = ``Y`` / ``Record_ST`` =
``Y``) NEVER classifies wide, regardless of what the width text says
(``effective_classification``); the classifier's own read of the raw text is
preserved separately and untouched (``width_classification``) so nothing is
silently discarded.

FIELD-DOMAIN HONESTY: ``Feat_Type`` has a documented three-value domain
(``Mapped_St`` / ``Not_mapped`` / ``Former_St``, research E3) and IS used for
the mapped-street override; an unrecognized ``Feat_Type`` value is a typed
schema-drift signal, never coerced into either bucket. ``Feat_status``,
``RoadwayType``, and ``Build_Status`` have NO documented domain (research
OQ-2 - live samples show values like ``Feat_status='Way_on_record'``
co-occurring with ``Record_ST='N'`` on the SAME feature, proving
``Feat_status`` is independent of the ``Record_ST``/``Paper_ST`` flags and
must never be used for override logic); this module surfaces them as plain
typed passthrough strings only, never interpreted.

TRANSPORT POSTURE (S5, mirroring the M5-T020 ``mappluto_lot_outline``
precedent): a single bounded attempt per HTTP request, NO retry loop. A
network failure, a non-200 status, or an ArcGIS error object delivered with
HTTP 200 is a typed FAULT, never data and never silently retried. Paging
(``resultOffset`` + ``exceededTransferLimit``) is a client-driven bounded
loop over that same single-attempt fetch, with loop-safety guarantees
(duplicate-page and zero-progress detection, a hard page-count ceiling) so a
misbehaving upstream can never spin this connector forever.

QUERY DISCIPLINE (thin client, injection-proof): the only two supported
bounded-predicate shapes are (a) an exact ``Borough`` equality (allowlisted
domain) AND/OR an exact ``Street_NM`` equality (safe-text validated, then
SQL-string-literal-escaped), and (b) an exact ``OBJECTID`` equality or a
bounded ``OBJECTID IN (...)`` list. A caller can never supply a raw SQL
fragment, host, or field list; every URL is built here from validated
components only.

NOT in scope (per packet): consumer wiring into the rules/profile/API layers,
Geoclient cross-check, geometry buffer/within-100-ft computation (OQ-4).
Deterministic code only: no AI, no legal interpretation. The official DCP
disclaimer applies (informational purposes only).
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import urllib.parse
import urllib.request
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.connectors.dcm_street_width_classifier import (
    DISPOSITION_NARROW_FAIL_CLOSED,
    DISPOSITION_WIDE,
    WidthClassification,
    classify_street_width,
)

__all__ = [
    "ATTRIBUTION",
    "BOROUGH_DOMAIN",
    "CONTRACT_VERSION",
    "CRS_STAMP",
    "DCP_DISCLAIMER",
    "ENVELOPE_ABS_MAX_FT",
    "ENVELOPE_SPATIAL_REL",
    "EXPECTED_LATEST_WKID",
    "EXPECTED_WKID",
    "FEAT_TYPE_DOMAIN",
    "HARD_MAX_PAGES",
    "MAX_OBJECT_ID_LIST",
    "MAX_RESULT_RECORD_COUNT",
    "OUT_FIELDS",
    "SERVICE_ROOT",
    "SOURCE_ID",
    "DCMConnectorError",
    "DisallowedRequestError",
    "LayerMetadata",
    "MalformedResponseError",
    "PagingPathologyError",
    "SchemaDriftError",
    "StreetSegment",
    "StreetSegmentQueryResult",
    "UpstreamError",
    "WrongCRSError",
    "DcmTransport",
    "build_metadata_url",
    "build_segment_query_url",
    "default_fetch",
    "fetch_layer_metadata",
    "fetch_street_segments",
    "parse_segment_page",
    "raw_body_digest",
]

SOURCE_ID = "nyc-dcp-dcm-street-centerline-arcgis"

# Pinned official root (research section 3.1: ArcGIS Online item
# 9ce5b83f139748f29eb92cdabeb29398, owner DCP_GIS - the same portal/org that
# serves MapPLUTO and the zoning-features layers). NEVER interpolated from
# caller input.
SERVICE_ROOT = "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services"
LAYER_NAME = "DCM_Street_Center_Line"

# Authoritative source CRS (research 3.1/E5: wkid 102718 / latestWkid 2263 =
# EPSG:2263, NAD83 New York Long Island, US survey feet). Live-verified
# 2026-09-13 (this task's own capture, fixtures/dcm_street_centerline/metadata.json).
EXPECTED_WKID = 102718
EXPECTED_LATEST_WKID = 2263
CRS_STAMP = {
    "wkid": EXPECTED_WKID,
    "latest_wkid": EXPECTED_LATEST_WKID,
    "authority": "EPSG:2263 (NAD83 / New York Long Island, US survey feet)",
}
EXPECTED_GEOMETRY_TYPE = "esriGeometryPolyline"

CONTRACT_VERSION = "1.0.0"

# Documented Feat_Type domain (research/registry E3, byte-verified from the
# official metadata PDF). Anything else is a typed schema-drift signal.
FEAT_TYPE_DOMAIN = ("Mapped_St", "Not_mapped", "Former_St")
FEAT_TYPE_MAPPED = "Mapped_St"

# Documented Borough domain (research/registry E3).
BOROUGH_DOMAIN = ("Bronx", "Brooklyn", "CW", "Manhattan", "Queens", "Staten Island")

# Bounded out-field allowlist. The connector requests an explicit field
# subset - never '*'. All 18 documented layer-0 fields except the polyline
# geometry itself (OQ-4 geometry work is out of scope for this task) and the
# OBJECTID/geometry pair that ArcGIS always returns regardless.
OUT_FIELDS = (
    "OBJECTID",
    "Borough",
    "Feat_Type",
    "Feat_status",
    "Street_NM",
    "HonoraryNM",
    "Old_ST_NM",
    "Streetwidth",
    "Route_Type",
    "RoadwayType",
    "Build_Status",
    "Record_ST",
    "Paper_ST",
    "Stair_ST",
    "CCO_ST",
    "Marg_Wharf",
    "Edit_Date",
)

MAX_RESULT_RECORD_COUNT = 2000  # the live layer's own maxRecordCount (E5)
MAX_OBJECT_ID_LIST = 50  # bounded IN(...) list length (thin client)
HARD_MAX_PAGES = 200  # absolute page-loop ceiling regardless of page_size

# Envelope-predicate extent sanity ceiling (M5-T035 / DB-015). A symmetric
# |x|,|y| magnitude bound (US survey feet) that comfortably contains the whole
# EPSG:2263 New York projected domain (real NYC eastings/northings are well
# under ~1.1e6 ft) with wide margin, mirroring the accepted
# wide_street_buffer_engine.EXTENT_ABS_MAX_FT sanity bound. Its job is to refuse
# NON-FINITE (+/-inf/NaN fail the `<=` comparison) and ABSURD magnitudes before
# any network I/O - NOT to geofence to the five boroughs (a tight NYC box would
# wrongly reject legitimate near-boundary lots; the metadata CRS gate already
# refuses any non-EPSG:2263 layer). The envelope is interpreted ONLY in the
# authoritative EPSG:2263 CRS (inSR=2263); there is no reprojection path.
ENVELOPE_ABS_MAX_FT = 5_000_000.0

# The single spatial relationship this connector's envelope predicate emits: an
# intersects test (ZR 23-22 "within 100 feet" candidate gather is a superset of
# an intersects test against the lot-bbox-plus-buffer envelope; the caller does
# the exact geometric proximity downstream). Never a caller-supplied relation.
ENVELOPE_SPATIAL_REL = "esriSpatialRelIntersects"

_SAFE_STREET_NAME_RE = re.compile(r"^[A-Za-z0-9 .,'\-]{1,100}$")
_MAX_BODY_BYTES = 16 * 1024 * 1024  # bounded read; largest observed fixture << 20 KB

ATTRIBUTION = "NYC Department of City Planning (DCP), Digital City Map (DCM) - Street Center Line"
DCP_DISCLAIMER = (
    "This dataset is provided by the Department of City Planning (DCP) for "
    "informational purposes only. DCP does not warranty the completeness, "
    "accuracy, content, or fitness for any particular purpose or use of the "
    "dataset. Digital City Map data changes often and is updated monthly."
)


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _rfc3339(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def raw_body_digest(body: str) -> str:
    """Raw-response digest: exact UTF-8 bytes of the transported body."""
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def _epoch_ms_to_rfc3339(ms: object) -> str | None:
    if isinstance(ms, bool) or not isinstance(ms, int):
        return None
    try:
        return _rfc3339(datetime.fromtimestamp(ms / 1000.0, UTC))
    except (OverflowError, OSError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Typed error taxonomy
# ---------------------------------------------------------------------------


class DCMConnectorError(Exception):
    """Base typed connector error. Payloads never contain stack traces,
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


class UpstreamError(DCMConnectorError):
    """Network failure, unexpected HTTP status, or an ArcGIS error object
    (delivered even with HTTP 200 - the documented DCP_GIS behavior)."""

    error_type = "upstream_error"


class MalformedResponseError(DCMConnectorError):
    """Response body is not the documented well-formed shape. NEVER
    converted into a valid empty result."""

    error_type = "malformed_response"


class SchemaDriftError(DCMConnectorError):
    """Layer contract changed (missing objectIdField/maxRecordCount, wrong
    geometry type, unrecognized documented-domain value). Surfaced for
    alerting; never silently guessed around."""

    error_type = "schema_drift"


class WrongCRSError(DCMConnectorError):
    """Spatial reference is not the authoritative EPSG:2263 / wkid 102718."""

    error_type = "wrong_crs"


class DisallowedRequestError(DCMConnectorError):
    """Request refused BEFORE any network I/O. This connector builds every
    URL itself from validated components; it is not a general HTTP client."""

    error_type = "disallowed_request"


class PagingPathologyError(DCMConnectorError):
    """A paging loop-safety guarantee was violated (duplicate page,
    zero-progress with exceededTransferLimit, or the page-count ceiling was
    reached). Aborted typed - never an infinite loop, never silent
    truncation or duplication."""

    error_type = "paging_pathology"


# ---------------------------------------------------------------------------
# URL construction (injection-proof: every fragment is validated or comes
# from the fixed allowlists above; no caller-supplied SQL is ever embedded)
# ---------------------------------------------------------------------------


def build_metadata_url() -> str:
    return f"{SERVICE_ROOT}/{LAYER_NAME}/FeatureServer/0?f=json"


def _escape_sql_literal(value: str) -> str:
    """Escape a validated safe-text value for embedding as a single-quoted
    SQL string literal (double any embedded single quote - the standard SQL
    escape, applied only AFTER the safe-text allowlist already rejected
    every other character)."""
    return value.replace("'", "''")


def _safe_repr(value: object, *, limit: int = 200) -> str:
    """``repr()`` for a rejection DIAGNOSTIC that can never itself raise and is
    always length-bounded. Python 3.11+ caps int<->str conversion
    (``sys.get_int_max_str_digits``, default 4300 digits); ``repr()`` of an
    oversized integer - or of a list/tuple that CONTAINS one - raises
    ``ValueError``. A ``disallowed_request`` refusal reporting a malformed
    envelope or a predicate conflict must not itself blow up while describing the
    bad input (that would turn a clean typed refusal into an uncaught
    ``ValueError`` before any network I/O), so this degrades to a typed, bounded
    placeholder instead of the raw ``repr``. Normal-sized values are returned
    unchanged (bounded), so existing diagnostics are byte-identical."""
    try:
        text = repr(value)
    except (ValueError, RecursionError):
        return f"<unrepresentable {type(value).__name__}>"
    return text if len(text) <= limit else text[:limit] + "...(truncated)"


def _validate_envelope(
    envelope: object, *, correlation_id: str
) -> tuple[float, float, float, float]:
    """Validate an EPSG:2263 (xmin, ymin, xmax, ymax) envelope BEFORE any
    network I/O. Refused (typed ``disallowed_request``) unless it is a 4-item
    sequence of FINITE real numbers (bools rejected), each within
    :data:`ENVELOPE_ABS_MAX_FT`, with xmin <= xmax and ymin <= ymax. Non-finite
    (+/-inf/NaN) and absurd magnitudes fail closed here - never a silent absurd
    spatial query. There is no reprojection; the values are always EPSG:2263."""
    if not isinstance(envelope, list | tuple) or len(envelope) != 4:
        raise DisallowedRequestError(
            "envelope must be a 4-item (xmin, ymin, xmax, ymax) sequence",
            correlation_id=correlation_id,
            detail={"envelope": _safe_repr(envelope)},
        )
    values: list[float] = []
    for axis, component in zip(("xmin", "ymin", "xmax", "ymax"), envelope, strict=True):
        if isinstance(component, bool) or not isinstance(component, int | float):
            raise DisallowedRequestError(
                f"envelope {axis} must be a real number",
                correlation_id=correlation_id,
                detail={"envelope": _safe_repr(envelope), "axis": axis},
            )
        try:
            value = float(component)
        except OverflowError as exc:
            # An int too large to convert to a float is an ABSURD magnitude - a
            # refused request, never a silent absurd spatial query and never an
            # uncaught OverflowError leaking out. The huge value is deliberately
            # kept OUT of the payload (bounded detail only).
            raise DisallowedRequestError(
                f"envelope {axis} is an absurd magnitude not representable as a "
                "finite EPSG:2263 coordinate",
                correlation_id=correlation_id,
                detail={"axis": axis, "reason": type(exc).__name__},
            ) from exc
        if not math.isfinite(value) or abs(value) > ENVELOPE_ABS_MAX_FT:
            raise DisallowedRequestError(
                f"envelope {axis}={component!r} is non-finite or outside the "
                f"plausible-EPSG:2263 magnitude bound (|value| <= "
                f"{ENVELOPE_ABS_MAX_FT:g} ft)",
                correlation_id=correlation_id,
                detail={
                    "envelope": _safe_repr(envelope),
                    "axis": axis,
                    "bound_ft": ENVELOPE_ABS_MAX_FT,
                },
            )
        values.append(value)
    xmin, ymin, xmax, ymax = values
    if xmin > xmax or ymin > ymax:
        raise DisallowedRequestError(
            "envelope is inverted (requires xmin <= xmax and ymin <= ymax)",
            correlation_id=correlation_id,
            detail={"envelope": [xmin, ymin, xmax, ymax]},
        )
    return xmin, ymin, xmax, ymax


def build_segment_query_url(
    *,
    borough: str | None = None,
    street_name: str | None = None,
    object_id: int | None = None,
    object_id_in: list[int] | None = None,
    envelope: tuple[float, float, float, float] | None = None,
    result_record_count: int = MAX_RESULT_RECORD_COUNT,
    result_offset: int = 0,
    correlation_id: str = "urlbuild",
) -> str:
    """Build the ONE query URL shape this connector emits: a bounded predicate
    over a validated allowlist (Borough / Street_NM / OBJECTID) OR an EPSG:2263
    envelope-intersects spatial predicate, the bounded out-field set,
    deterministic ordering, and a bounded page window. Exactly one predicate
    style may be used per call: (borough and/or street_name) XOR (object_id) XOR
    (object_id_in) XOR (envelope). A caller can never supply raw SQL, a host, an
    unbounded field list, or an arbitrary spatial relation - the envelope is
    validated and always interpreted as EPSG:2263 intersects (returnGeometry
    stays the layer default TRUE so the geometry sibling can read paths)."""
    predicate_styles = [
        bool(borough or street_name),
        object_id is not None,
        object_id_in is not None,
        envelope is not None,
    ]
    if sum(predicate_styles) != 1:
        raise DisallowedRequestError(
            "exactly one predicate style is required: (borough/street_name) "
            "XOR object_id XOR object_id_in XOR envelope",
            correlation_id=correlation_id,
            detail={
                "borough": _safe_repr(borough),
                "street_name": _safe_repr(street_name),
                "object_id": _safe_repr(object_id),
                "object_id_in": _safe_repr(object_id_in),
                "envelope": _safe_repr(envelope),
            },
        )

    clauses: list[str] = []
    spatial_params = ""
    if envelope is not None:
        xmin, ymin, xmax, ymax = _validate_envelope(envelope, correlation_id=correlation_id)
        # A spatial predicate still needs a WHERE; a constant-true clause keeps
        # the where-builder uniform while the envelope does the selection.
        clauses.append("1=1")
        geometry = f"{xmin:.4f},{ymin:.4f},{xmax:.4f},{ymax:.4f}"
        spatial_params = (
            f"&geometry={urllib.parse.quote(geometry, safe='')}"
            "&geometryType=esriGeometryEnvelope"
            "&inSR=2263"
            f"&spatialRel={ENVELOPE_SPATIAL_REL}"
        )
    elif borough or street_name:
        if borough is not None:
            if borough not in BOROUGH_DOMAIN:
                raise DisallowedRequestError(
                    "borough must be one of the documented domain values",
                    correlation_id=correlation_id,
                    detail={"borough": _safe_repr(borough), "domain": list(BOROUGH_DOMAIN)},
                )
            clauses.append(f"Borough='{_escape_sql_literal(borough)}'")
        if street_name is not None:
            if not _SAFE_STREET_NAME_RE.match(street_name):
                raise DisallowedRequestError(
                    "street_name failed the safe-text allowlist",
                    correlation_id=correlation_id,
                    detail={"street_name": _safe_repr(street_name)},
                )
            clauses.append(f"Street_NM='{_escape_sql_literal(street_name)}'")
    elif object_id is not None:
        if isinstance(object_id, bool) or not isinstance(object_id, int) or object_id < 1:
            raise DisallowedRequestError(
                "object_id must be a positive integer",
                correlation_id=correlation_id,
                detail={"object_id": _safe_repr(object_id)},
            )
        clauses.append(f"OBJECTID={object_id}")
    else:
        assert object_id_in is not None  # noqa: S101 - checked by predicate_styles above
        if (
            not isinstance(object_id_in, list)
            or not object_id_in
            or len(object_id_in) > MAX_OBJECT_ID_LIST
            or any(isinstance(v, bool) or not isinstance(v, int) or v < 1 for v in object_id_in)
        ):
            raise DisallowedRequestError(
                f"object_id_in must be a non-empty list of at most "
                f"{MAX_OBJECT_ID_LIST} positive integers",
                correlation_id=correlation_id,
                detail={"object_id_in": _safe_repr(object_id_in)},
            )
        ids = ",".join(str(v) for v in object_id_in)
        clauses.append(f"OBJECTID IN ({ids})")

    if (
        isinstance(result_record_count, bool)
        or not isinstance(result_record_count, int)
        or not 1 <= result_record_count <= MAX_RESULT_RECORD_COUNT
    ):
        raise DisallowedRequestError(
            f"result_record_count must be an integer in 1..{MAX_RESULT_RECORD_COUNT}",
            correlation_id=correlation_id,
            detail={"result_record_count": _safe_repr(result_record_count)},
        )
    if isinstance(result_offset, bool) or not isinstance(result_offset, int) or result_offset < 0:
        raise DisallowedRequestError(
            "result_offset must be a non-negative integer",
            correlation_id=correlation_id,
            detail={"result_offset": _safe_repr(result_offset)},
        )

    where = " AND ".join(clauses)
    out_fields = ",".join(OUT_FIELDS)
    return (
        f"{SERVICE_ROOT}/{LAYER_NAME}/FeatureServer/0/query"
        f"?where={urllib.parse.quote(where, safe='')}"
        f"{spatial_params}"
        f"&outFields={out_fields}"
        "&orderByFields=OBJECTID%20ASC"
        f"&resultRecordCount={result_record_count}&resultOffset={result_offset}"
        "&outSR=2263&f=json"
    )


# ---------------------------------------------------------------------------
# Transport seam (injected for offline tests; bounded, single-attempt -
# mirrors the M5-T020 ``mappluto_lot_outline`` no-retry posture, S5)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DcmTransport:
    """Raw transport result for one bounded query: the exact URL requested,
    the HTTP status, the verbatim response body text, and the retrieval
    timestamp (RFC 3339, file-write-time per the M2-T021 correction)."""

    url: str
    status: int
    body: str
    retrieved_at: str


def default_fetch(url: str, correlation_id: str) -> DcmTransport:
    """Live transport (production default): a single bounded, no-retry
    keyless GET. Tests inject a fetcher that reads recorded fixture bytes
    instead, so the whole suite runs OFFLINE."""
    req = urllib.request.Request(  # noqa: S310 - URL is built exclusively by build_*_url
        url, headers={"Accept": "application/json"}, method="GET"
    )
    retrieved_at = _rfc3339(_utc_now())
    try:
        with urllib.request.urlopen(req, timeout=30.0) as response:  # noqa: S310
            status = int(response.status)
            body = response.read(_MAX_BODY_BYTES + 1)
    except OSError as exc:
        # Mirrors the M5-T020 bounded no-retry posture (S5): a single
        # attempt, no retry loop. This covers network failure, connect/read
        # timeout, and any non-2xx HTTP status (urllib raises HTTPError -
        # an OSError subclass - for those); the ArcGIS service's documented
        # failure shape for a QUERY error is an HTTP-200 body carrying an
        # 'error' object, handled separately in _parse_json_object, never
        # here.
        raise UpstreamError(
            "official DCM ArcGIS service was unreachable",
            correlation_id=correlation_id,
            detail={"url": url, "reason_kind": type(exc).__name__},
        ) from exc
    if len(body) > _MAX_BODY_BYTES:
        raise MalformedResponseError(
            "response body exceeded the bounded read ceiling",
            correlation_id=correlation_id,
            detail={"url": url, "limit_bytes": _MAX_BODY_BYTES},
        )
    return DcmTransport(
        url=url,
        status=status,
        body=body.decode("utf-8", errors="replace"),
        retrieved_at=retrieved_at,
    )


# ---------------------------------------------------------------------------
# Response parsing helpers
# ---------------------------------------------------------------------------


def _parse_json_object(body: str, *, url: str, correlation_id: str) -> dict:
    """Parse a response body; classify the ArcGIS error-object-with-HTTP-200
    as a typed UPSTREAM error, and anything unparseable as
    malformed_response (never a valid empty result)."""
    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise MalformedResponseError(
            "ArcGIS returned a body that is not valid JSON; refusing to "
            "interpret it (never an empty result)",
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
                "arcgis_error_message": str(message)[:300] if message is not None else None,
            },
        )
    return parsed


def _as_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _as_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


# ---------------------------------------------------------------------------
# Layer metadata (freshness pin + schema-drift guard)
# ---------------------------------------------------------------------------


@dataclass
class LayerMetadata:
    """Validated layer-0 metadata snapshot with provenance."""

    correlation_id: str
    request_url: str
    retrieved_at: str
    object_id_field: str
    geometry_type: str
    wkid: int
    latest_wkid: int
    max_record_count: int
    source_data_last_edited_ms: int | None
    source_data_last_edited: str | None
    raw_digest: str
    drift_signals: list[str] = field(default_factory=list)


def fetch_layer_metadata(
    *,
    fetch: Callable[[str, str], DcmTransport] = default_fetch,
    correlation_id: str | None = None,
) -> LayerMetadata:
    """Fetch and VALIDATE layer-0 metadata. Typed failures: ``wrong_crs`` on
    a non-authoritative spatial reference (BEFORE any coordinate is
    interpreted downstream), ``schema_drift`` on a missing objectIdField,
    missing/invalid maxRecordCount, or wrong geometry type. Missing
    ``editingInfo`` degrades visibly (drift signal), never silently."""
    correlation_id = correlation_id or uuid.uuid4().hex
    url = build_metadata_url()
    transport = fetch(url, correlation_id)
    if transport.status != 200:
        raise UpstreamError(
            "unexpected HTTP status from the official DCM ArcGIS service",
            correlation_id=correlation_id,
            detail={"url": url, "status": transport.status},
        )
    doc = _parse_json_object(transport.body, url=url, correlation_id=correlation_id)
    drift_signals: list[str] = []

    name = doc.get("name")
    if name != LAYER_NAME:
        raise SchemaDriftError(
            "service metadata 'name' does not match the canonical DCM layer",
            correlation_id=correlation_id,
            detail={"url": url, "name": repr(name)[:200]},
        )

    geometry_type = doc.get("geometryType")
    if geometry_type != EXPECTED_GEOMETRY_TYPE:
        raise SchemaDriftError(
            "layer geometryType is not the documented polyline type",
            correlation_id=correlation_id,
            detail={"url": url, "geometry_type": repr(geometry_type)[:200]},
        )

    sr = doc.get("spatialReference")
    if not isinstance(sr, dict) or sr.get("wkid") != EXPECTED_WKID:
        raise WrongCRSError(
            "spatial reference is not the authoritative EPSG:2263 "
            f"(wkid {EXPECTED_WKID})",
            correlation_id=correlation_id,
            detail={"url": url, "spatial_reference": repr(sr)[:200]},
        )
    latest_wkid = sr.get("latestWkid", EXPECTED_LATEST_WKID)

    object_id_field = doc.get("objectIdField")
    if not isinstance(object_id_field, str) or not object_id_field:
        raise SchemaDriftError(
            "layer metadata is missing objectIdField",
            correlation_id=correlation_id,
            detail={"url": url},
        )

    max_record_count = doc.get("maxRecordCount")
    if (
        isinstance(max_record_count, bool)
        or not isinstance(max_record_count, int)
        or max_record_count < 1
    ):
        raise SchemaDriftError(
            "layer metadata is missing a valid maxRecordCount",
            correlation_id=correlation_id,
            detail={"url": url, "max_record_count": repr(max_record_count)},
        )

    editing = doc.get("editingInfo")
    data_last_edited_ms: int | None = None
    raw_edit_date = editing.get("dataLastEditDate") if isinstance(editing, dict) else None
    if isinstance(raw_edit_date, int) and not isinstance(raw_edit_date, bool):
        data_last_edited_ms = raw_edit_date
    else:
        drift_signals.append(
            "missing_or_invalid_editing_info: dataLastEditDate freshness pin "
            "is unavailable; freshness cannot be characterized this call"
        )

    return LayerMetadata(
        correlation_id=correlation_id,
        request_url=url,
        retrieved_at=transport.retrieved_at,
        object_id_field=object_id_field,
        geometry_type=geometry_type,
        wkid=EXPECTED_WKID,
        latest_wkid=latest_wkid,
        max_record_count=max_record_count,
        source_data_last_edited_ms=data_last_edited_ms,
        source_data_last_edited=_epoch_ms_to_rfc3339(data_last_edited_ms),
        raw_digest=raw_body_digest(transport.body),
        drift_signals=drift_signals,
    )


# ---------------------------------------------------------------------------
# Per-segment typed envelope (the connector's core contribution: raw text
# verbatim + pure-classifier read + mapped-street override, kept separate)
# ---------------------------------------------------------------------------


@dataclass
class StreetSegment:
    """One typed DCM street-center-line segment. ``width_classification`` is
    the pure classifier's read of the raw text ALONE (never touched by
    mapped-street status). ``effective_classification`` applies the one
    additional fail-closed rule this connector owns: a segment that is not a
    currently mapped street, or that is flagged paper/record, NEVER
    classifies wide - ``override_reason`` is populated exactly when that
    rule changed the outcome, and is ``None`` otherwise (including when the
    raw text was already narrow)."""

    object_id: int | None
    borough: str | None
    street_name: str | None
    honorary_name: str | None
    old_street_name: str | None
    route_type: str | None
    streetwidth_raw: str | None
    width_classification: WidthClassification
    feat_type: str | None
    feat_type_recognized: bool
    feat_status: str | None
    roadway_type: str | None
    build_status: str | None
    record_street: str | None
    paper_street: str | None
    stair_street: str | None
    cco_street: str | None
    marginal_wharf: str | None
    edit_date_ms: int | None
    is_mapped_street: bool
    effective_disposition: str
    effective_review_required: bool
    override_reason: str | None


def _mapped_street_override(
    feat_type: str | None,
    record_street: str | None,
    paper_street: str | None,
    width_classification: WidthClassification,
) -> tuple[bool, bool, str, bool, str | None]:
    """Apply the mapped-street fail-closed rule on top of the pure
    classifier's disposition. Returns (feat_type_recognized,
    is_mapped_street, effective_disposition, effective_review_required,
    override_reason)."""
    feat_type_recognized = feat_type in FEAT_TYPE_DOMAIN
    is_mapped = feat_type == FEAT_TYPE_MAPPED
    is_paper = paper_street == "Y"
    is_record = record_street == "Y"

    if width_classification.disposition != DISPOSITION_WIDE:
        # Already narrow (confidently or fail-closed): the override cannot
        # make it MORE permissive, so nothing changes.
        return (
            feat_type_recognized,
            is_mapped and not is_paper and not is_record,
            width_classification.disposition,
            width_classification.review_required,
            None,
        )

    if is_mapped and not is_paper and not is_record and feat_type_recognized:
        return (feat_type_recognized, True, DISPOSITION_WIDE, False, None)

    if not feat_type_recognized:
        reason = (
            f"Feat_Type value {feat_type!r} is not in the documented domain "
            f"{FEAT_TYPE_DOMAIN}; a wide disposition is never granted on an "
            "unrecognized mapped-street status (schema drift, fail closed)."
        )
    elif is_paper:
        reason = (
            "segment is flagged Paper_ST='Y' (a paper street); wide is "
            "never granted on a paper street regardless of the width text."
        )
    elif is_record:
        reason = (
            "segment is flagged Record_ST='Y' (a record street); wide is "
            "never granted on a record street regardless of the width text."
        )
    else:
        reason = (
            f"Feat_Type={feat_type!r} is not '{FEAT_TYPE_MAPPED}' (not a "
            "currently mapped street); wide is never granted on an unmapped "
            "or former street regardless of the width text."
        )
    return (feat_type_recognized, False, DISPOSITION_NARROW_FAIL_CLOSED, True, reason)


def _build_segment(attributes: dict) -> StreetSegment:
    streetwidth_raw = _as_str(attributes.get("Streetwidth"))
    width_classification = classify_street_width(attributes.get("Streetwidth"))
    feat_type = _as_str(attributes.get("Feat_Type"))
    record_street = _as_str(attributes.get("Record_ST"))
    paper_street = _as_str(attributes.get("Paper_ST"))
    (
        feat_type_recognized,
        is_mapped_street,
        effective_disposition,
        effective_review_required,
        override_reason,
    ) = _mapped_street_override(feat_type, record_street, paper_street, width_classification)

    return StreetSegment(
        object_id=_as_int(attributes.get("OBJECTID")),
        borough=_as_str(attributes.get("Borough")),
        street_name=_as_str(attributes.get("Street_NM")),
        honorary_name=_as_str(attributes.get("HonoraryNM")),
        old_street_name=_as_str(attributes.get("Old_ST_NM")),
        route_type=_as_str(attributes.get("Route_Type")),
        streetwidth_raw=streetwidth_raw,
        width_classification=width_classification,
        feat_type=feat_type,
        feat_type_recognized=feat_type_recognized,
        feat_status=_as_str(attributes.get("Feat_status")),
        roadway_type=_as_str(attributes.get("RoadwayType")),
        build_status=_as_str(attributes.get("Build_Status")),
        record_street=record_street,
        paper_street=paper_street,
        stair_street=_as_str(attributes.get("Stair_ST")),
        cco_street=_as_str(attributes.get("CCO_ST")),
        marginal_wharf=_as_str(attributes.get("Marg_Wharf")),
        edit_date_ms=_as_int(attributes.get("Edit_Date")),
        is_mapped_street=is_mapped_street,
        effective_disposition=effective_disposition,
        effective_review_required=effective_review_required,
        override_reason=override_reason,
    )


def parse_segment_page(
    transport: DcmTransport, *, correlation_id: str
) -> tuple[list[StreetSegment], bool]:
    """Parse one query response page into typed segments plus the
    ``exceededTransferLimit`` flag. A well-formed empty ``features`` list is
    a normal (possibly final) page, never an error."""
    if transport.status != 200:
        raise UpstreamError(
            "unexpected HTTP status from the official DCM ArcGIS service",
            correlation_id=correlation_id,
            detail={"url": transport.url, "status": transport.status},
        )
    doc = _parse_json_object(transport.body, url=transport.url, correlation_id=correlation_id)
    features = doc.get("features")
    if not isinstance(features, list):
        raise MalformedResponseError(
            "query response has no features array",
            correlation_id=correlation_id,
            detail={"url": transport.url},
        )
    segments: list[StreetSegment] = []
    for feature in features:
        if not isinstance(feature, dict) or not isinstance(feature.get("attributes"), dict):
            raise MalformedResponseError(
                "a feature in the response is missing a well-formed "
                "attributes object",
                correlation_id=correlation_id,
                detail={"url": transport.url},
            )
        segments.append(_build_segment(feature["attributes"]))
    exceeded = doc.get("exceededTransferLimit") is True
    return segments, exceeded


# ---------------------------------------------------------------------------
# Paged public entry point
# ---------------------------------------------------------------------------


@dataclass
class StreetSegmentQueryResult:
    """Complete result of one bounded, possibly-paged segment query."""

    segments: list[StreetSegment]
    exceeded_transfer_limit_on_last_page: bool
    pages_fetched: int
    page_urls: list[str]
    correlation_id: str
    source_id: str
    service_root: str
    layer: str
    retrieved_at: str
    source_data_last_edited_ms: int | None
    source_data_last_edited: str | None
    metadata_request_url: str
    raw_digests: list[str]
    drift_signals: list[str]
    attribution: str = ATTRIBUTION
    disclaimer: str = DCP_DISCLAIMER


def fetch_street_segments(
    *,
    borough: str | None = None,
    street_name: str | None = None,
    object_id: int | None = None,
    object_id_in: list[int] | None = None,
    envelope: tuple[float, float, float, float] | None = None,
    page_size: int = MAX_RESULT_RECORD_COUNT,
    max_pages: int | None = None,
    fetch: Callable[[str, str], DcmTransport] = default_fetch,
    correlation_id: str | None = None,
) -> StreetSegmentQueryResult:
    """Fetch a bounded set of street-center-line segments matching exactly
    one predicate style (Borough/Street_NM, OBJECTID, OBJECTID IN, or an
    EPSG:2263 envelope-intersects spatial predicate - M5-T035/DB-015), paging
    deterministically via ``resultOffset`` and honoring
    ``exceededTransferLimit``. Loop-safety guarantees: repeated OBJECTIDs across
    pages or a byte-identical repeated page raise the typed ``paging_pathology``
    fault; a hard page-count ceiling (:data:`HARD_MAX_PAGES`, or the caller's
    ``max_pages`` if smaller) is never exceeded. Metadata is fetched first so
    the freshness pin and schema-drift guard run before any segment data is
    trusted. The envelope predicate preserves every one of these guards - it
    changes only the selection, never the transport, paging, CRS, or
    freshness/drift discipline; an invalid/non-finite/absurd envelope is
    refused BEFORE any network I/O (typed ``disallowed_request``)."""
    correlation_id = correlation_id or uuid.uuid4().hex

    page_budget = min(max_pages, HARD_MAX_PAGES) if max_pages is not None else HARD_MAX_PAGES
    if isinstance(page_budget, bool) or not isinstance(page_budget, int) or page_budget < 1:
        raise DisallowedRequestError(
            "max_pages must be a positive integer",
            correlation_id=correlation_id,
            detail={"max_pages": _safe_repr(max_pages)},
        )

    # Validate the ENTIRE request - predicate style, envelope extent-sanity, and
    # the page window - BEFORE any network I/O, the metadata fetch included. An
    # invalid/non-finite/absurd envelope or malformed predicate is refused with a
    # typed disallowed_request without ever contacting the service (M5-T035: a bad
    # request must not first spend a metadata round-trip). This first-page URL
    # (resultOffset=0) is reused verbatim as the loop's first fetch below.
    # Metadata-first discipline is UNCHANGED: fetch_layer_metadata still runs
    # before any segment page is parsed, so the freshness pin + schema-drift + CRS
    # guard still gate every segment the loop trusts.
    first_page_url = build_segment_query_url(
        borough=borough,
        street_name=street_name,
        object_id=object_id,
        object_id_in=object_id_in,
        envelope=envelope,
        result_record_count=page_size,
        result_offset=0,
        correlation_id=correlation_id,
    )

    metadata = fetch_layer_metadata(fetch=fetch, correlation_id=correlation_id)

    segments: list[StreetSegment] = []
    seen_object_ids: set[int] = set()
    previous_page_object_ids: list[int | None] | None = None
    page_urls: list[str] = []
    raw_digests: list[str] = []
    drift_signals = list(metadata.drift_signals)
    pages_fetched = 0
    exceeded_on_last_page = False
    retrieved_at = metadata.retrieved_at

    while True:
        if pages_fetched >= page_budget:
            raise PagingPathologyError(
                "page budget exhausted before the extraction completed; "
                "refusing to loop further (never an infinite loop)",
                correlation_id=correlation_id,
                detail={
                    "reason": "page_budget_exhausted",
                    "pages_fetched": pages_fetched,
                    "page_budget": page_budget,
                    "collected": len(segments),
                },
            )
        # The first page's URL was already built (and the whole request validated)
        # before the metadata fetch; reuse it verbatim. Later pages advance the
        # deterministic resultOffset.
        url = (
            first_page_url
            if pages_fetched == 0
            else build_segment_query_url(
                borough=borough,
                street_name=street_name,
                object_id=object_id,
                object_id_in=object_id_in,
                envelope=envelope,
                result_record_count=page_size,
                result_offset=len(segments),
                correlation_id=correlation_id,
            )
        )
        transport = fetch(url, correlation_id)
        retrieved_at = transport.retrieved_at
        pages_fetched += 1
        page_urls.append(url)
        raw_digests.append(raw_body_digest(transport.body))
        page_segments, exceeded = parse_segment_page(transport, correlation_id=correlation_id)
        exceeded_on_last_page = exceeded
        page_object_ids = [seg.object_id for seg in page_segments]

        if not page_segments:
            if exceeded:
                raise PagingPathologyError(
                    "empty page with exceededTransferLimit=true: the "
                    "service reports more data but returned none "
                    "(zero-progress loop) - aborting typed",
                    correlation_id=correlation_id,
                    detail={
                        "reason": "zero_progress",
                        "page_index": pages_fetched - 1,
                        "collected": len(segments),
                    },
                )
            break  # well-formed end of data

        if previous_page_object_ids is not None and page_object_ids == previous_page_object_ids:
            raise PagingPathologyError(
                "page is identical to the previous page (upstream returned "
                "the same page twice) - aborting typed, no silent duplication",
                correlation_id=correlation_id,
                detail={"reason": "duplicate_page", "page_index": pages_fetched - 1},
            )
        overlap = sorted(
            {oid for oid in page_object_ids if oid is not None} & seen_object_ids
        )
        if overlap:
            raise PagingPathologyError(
                "page repeats OBJECTID(s) already extracted from an earlier "
                "page - aborting typed, no silent duplication",
                correlation_id=correlation_id,
                detail={
                    "reason": "repeated_object_ids",
                    "page_index": pages_fetched - 1,
                    "object_ids": overlap,
                },
            )

        segments.extend(page_segments)
        seen_object_ids.update(oid for oid in page_object_ids if oid is not None)
        previous_page_object_ids = page_object_ids

        if not exceeded:
            break  # well-formed end of data (no more pages signalled)

    return StreetSegmentQueryResult(
        segments=segments,
        exceeded_transfer_limit_on_last_page=exceeded_on_last_page,
        pages_fetched=pages_fetched,
        page_urls=page_urls,
        correlation_id=correlation_id,
        source_id=SOURCE_ID,
        service_root=SERVICE_ROOT,
        layer=LAYER_NAME,
        retrieved_at=retrieved_at,
        source_data_last_edited_ms=metadata.source_data_last_edited_ms,
        source_data_last_edited=metadata.source_data_last_edited,
        metadata_request_url=metadata.request_url,
        raw_digests=raw_digests,
        drift_signals=drift_signals,
    )
