"""GIS Zoning Features connector - six canonical DCP_GIS ArcGIS services
(task M2-T007; research docs/research/zoning-features-ztldb-2026-07-16.md).

Layers (all layer 0 of the named FeatureServer under the verified DCP_GIS
org root ``services5.arcgis.com/GfwWNkhOj9bNBqoJ``): ``nyzd`` zoning
districts, ``nyco`` commercial overlays, ``nysp`` special purpose districts,
``nysp_sd`` special purpose subdistricts, ``nylh`` limited height districts,
``nyzma`` zoning map amendments.

Design commitments (packet safeguards 1-6):

1. ENDPOINT ALLOWLISTING - every URL is constructed here from the pinned
   service root and an exact-match layer key; callers can never supply a URL,
   host, service name, or raw where clause. Attribute filters are built from
   a per-layer field allowlist plus a value character allowlist; out-fields
   are validated against the known field inventory. Violations raise the
   typed ``disallowed_request`` error BEFORE any network I/O.
2. METADATA VALIDATION - layer metadata (field inventory, objectIdField,
   spatial reference wkid 102718 / latestWkid 2263, maxRecordCount,
   pagination capabilities, editingInfo.dataLastEditDate) is validated
   against the expected inventory captured live on 2026-07-20 (UTC; fixture pack
   ZF01a-f). Missing/renamed/re-typed fields, wrong CRS, missing
   objectIdField, or missing maxRecordCount fail loudly as typed
   ``schema_drift``; ADDED fields and missing editingInfo degrade typed
   (visible drift signals), never a silent guess.
3. MANDATORY EXPLICIT PAGING - ``extract_layer`` pages every layer with
   deterministic ordering (``orderByFields=<objectIdField> ASC`` +
   ``resultOffset``; both capabilities verified live 2026-07-20, resolving
   research OQ-11), respects ``exceededTransferLimit``, detects repeated
   object IDs, duplicate pages, zero-progress loops, and count mismatches,
   and enforces a bounded page budget. Live counts EXCEED maxRecordCount on
   nysp (95>92), nysp_sd (336>317), nyzma (1414>1292); nylh sits at its cap
   (14=14) - an unpaged request silently truncates (research C3).
4. RESILIENCE - reuses the M1-T009 framework primitives (``TTLCache``,
   ``CircuitBreaker``, ``AnalysisBudget``, ``ResilienceConfig``,
   ``ResilienceMetrics``, ``backoff_delay``, ``parse_retry_after``) composed
   in ``ResilientZoningFeaturesClient``; no second resilience system. An
   ArcGIS error object delivered with HTTP 200 is a typed UPSTREAM error
   (verified live: fixture ZF06 shows HTTP 200 + ``error.code`` 400), never
   data; a malformed response is NEVER a valid empty result.
5. PROVENANCE - every result stamps the official endpoint URLs, layer,
   retrieval timestamp, source edit timestamp (``dataLastEditDate``), CRS,
   and counts. EPSG:2263 is preserved as the authoritative source CRS; NO
   reprojection happens in this module.
6. DETERMINISM - raw-response digests (exact body bytes) and the
   canonical-normalized digest (order-independent, sorted by object id) are
   kept SEPARATELY per ``ZF_CANONICALIZATION_SPEC``.

TWO-STALENESS RULE (owner directive 2026-07-17): ``source_data_last_edited``
is source-dataset freshness PROVENANCE; it never sets ``served_from_cache``
or ``stale``. The ``staleness`` field describes TRANSPORT/cache fallback
only and is stamped exclusively by ``ResilientZoningFeaturesClient`` on
cache-hit and last-known-good serves.

Deterministic code only: no AI, no legal interpretation, no spatial
intersection, no lot-level zoning assignment (official use limitation:
"These features are not intended for determining zoning at the individual
tax lot level" - lot-level work belongs to ZTLDB/PLUTO).
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
from urllib.parse import quote

# Canonical JSON digest reused from the accepted M1-T002 connector.
from app.connectors.pluto_soda import canonical_json_digest
from app.resilience.breaker import CircuitBreaker
from app.resilience.budget import AnalysisBudget
from app.resilience.cache import TTLCache
from app.resilience.config import ResilienceConfig
from app.resilience.metrics import ResilienceMetrics

# Task M2-T011: hardened transport (bounded body read, refused redirects,
# typed transport signals) and the bounded retry engine now come from the
# shared app.resilience.transport module (moved verbatim from the accepted
# M1-T002 implementation this connector previously reused via pluto_soda).
# Connector semantics - error taxonomy, messages, layer tagging - stay HERE
# and reach the shared engine through standard_retry_hooks.
from app.resilience.transport import (
    Transport,
    TransportResponse,
    jittered_retry_after_delay,
    request_with_retry,
    standard_retry_hooks,
    urllib_transport,
)

__all__ = [
    "EXPECTED_LATEST_WKID",
    "EXPECTED_WKID",
    "LAYER_SPECS",
    "SERVICE_ROOT",
    "SOURCE_ID",
    "ZF_CANONICALIZATION_SPEC",
    "CircuitOpenError",
    "DisallowedRequestError",
    "LayerCountResult",
    "LayerExtractResult",
    "LayerMetadata",
    "LayerQueryResult",
    "MalformedResponseError",
    "PagingPathologyError",
    "RateLimitedError",
    "RequestBudgetExceededError",
    "ResilientZoningFeaturesClient",
    "SchemaDriftError",
    "SourceTimeoutError",
    "UpstreamError",
    "ZoningFeaturesConnectorError",
    "build_attribute_where",
    "build_count_url",
    "build_metadata_url",
    "build_query_url",
    "extract_layer",
    "fetch_layer_count",
    "fetch_layer_metadata",
    "query_features",
    "raw_body_digest",
]

logger = logging.getLogger("app.connectors.zoning_features_arcgis")

SOURCE_ID = "nyc-dcp-zoning-features-arcgis"

# Pinned official root (research Z7/Z8: ArcGIS Online items verified under
# owner DCP_GIS). NEVER interpolated from caller input.
SERVICE_ROOT = "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services"

# Authoritative source CRS (research section 4.3; official nyzd metadata:
# NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet, EPSG 2263).
EXPECTED_WKID = 102718
EXPECTED_LATEST_WKID = 2263
CRS_STAMP = {
    "wkid": EXPECTED_WKID,
    "latest_wkid": EXPECTED_LATEST_WKID,
    "authority": "EPSG:2263 (NAD83 / New York Long Island, US survey feet)",
}

EXPECTED_GEOMETRY_TYPE = "esriGeometryPolygon"

# Verbatim digest spec, self-describing so a historical record can recompute
# and verify its own digests (same pattern as pluto CANONICALIZATION_SPEC).
ZF_CANONICALIZATION_SPEC = (
    "zf-canonical-json-1: raw_digest is 'sha256:' + lowercase-hex SHA-256 "
    "over the EXACT UTF-8 bytes of the HTTP response body string "
    "(byte-preserving, order-sensitive, no parsing or reserialization). "
    "normalized_digest is 'sha256:' + lowercase-hex SHA-256 of the UTF-8 "
    "canonical JSON serialization (object keys sorted lexicographically by "
    "Unicode code point; separators ',' and ':'; non-ASCII preserved; "
    "numbers per Python json.dumps defaults) of the normalized feature "
    "list: features sorted ASCENDING by object id, each normalized to "
    "{'object_id': <int>, 'attributes': <verbatim attribute map>, "
    "'geometry': <verbatim esri geometry or null>}. Raw and normalized "
    "digests are kept SEPARATELY: raw pins the exact transported bytes; "
    "normalized is independent of upstream response ordering."
)

# ---------------------------------------------------------------------------
# Layer allowlist. Field inventories are the LIVE layer schemas captured
# 2026-07-20 UTC (fixtures ZF01a-f; the test suite cross-checks these constants
# against the fixtures, so transcription drift fails the build). They match
# the G1-corrected research section 4.2 exactly.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _LayerSpec:
    fields: dict[str, str]  # field name -> esri type (live schema)
    queryable_fields: frozenset[str]  # string attrs allowed in where clauses


LAYER_SPECS: dict[str, _LayerSpec] = {
    "nyzd": _LayerSpec(
        fields={
            "OBJECTID": "esriFieldTypeOID",
            "ZONEDIST": "esriFieldTypeString",
            "Shape__Area": "esriFieldTypeDouble",
            "Shape__Length": "esriFieldTypeDouble",
        },
        queryable_fields=frozenset({"ZONEDIST"}),
    ),
    "nyco": _LayerSpec(
        fields={
            "OBJECTID": "esriFieldTypeOID",
            "OVERLAY": "esriFieldTypeString",
            "Shape__Area": "esriFieldTypeDouble",
            "Shape__Length": "esriFieldTypeDouble",
        },
        queryable_fields=frozenset({"OVERLAY"}),
    ),
    "nysp": _LayerSpec(
        fields={
            "OBJECTID": "esriFieldTypeOID",
            "SDNAME": "esriFieldTypeString",
            "SDLBL": "esriFieldTypeString",
            "Shape__Area": "esriFieldTypeDouble",
            "Shape__Length": "esriFieldTypeDouble",
        },
        queryable_fields=frozenset({"SDNAME", "SDLBL"}),
    ),
    "nysp_sd": _LayerSpec(
        fields={
            "OBJECTID": "esriFieldTypeOID",
            "SPNAME": "esriFieldTypeString",
            "SPLBL": "esriFieldTypeString",
            "SUBDIST": "esriFieldTypeString",
            "SUB_AREA_NM": "esriFieldTypeString",
            "SUBDIST_LBL": "esriFieldTypeString",
            "SUBAREA_LBL": "esriFieldTypeString",
            "SUBAREA_OTR": "esriFieldTypeString",
            "Shape__Area": "esriFieldTypeDouble",
            "Shape__Length": "esriFieldTypeDouble",
        },
        queryable_fields=frozenset({"SPNAME", "SPLBL", "SUBDIST"}),
    ),
    "nylh": _LayerSpec(
        fields={
            "OBJECTID": "esriFieldTypeOID",
            "LHNAME": "esriFieldTypeString",
            "LHLBL": "esriFieldTypeString",
            "Shape__Area": "esriFieldTypeDouble",
            "Shape__Length": "esriFieldTypeDouble",
        },
        queryable_fields=frozenset({"LHNAME", "LHLBL"}),
    ),
    "nyzma": _LayerSpec(
        fields={
            "OBJECTID": "esriFieldTypeOID",
            "EFFECTIVE": "esriFieldTypeDate",
            "STATUS": "esriFieldTypeString",
            "ULURPNO": "esriFieldTypeString",
            "LUCATS": "esriFieldTypeString",
            "PROJECT_NAME": "esriFieldTypeString",
            "Shape__Area": "esriFieldTypeDouble",
            "Shape__Length": "esriFieldTypeDouble",
        },
        queryable_fields=frozenset({"STATUS", "ULURPNO", "LUCATS", "PROJECT_NAME"}),
    ),
}

# Bounded-parameter limits (allowlist safeguard 1).
MAX_RESULT_RECORD_COUNT = 2000  # largest live maxRecordCount (nyzd/nyco)
MAX_RESULT_OFFSET = 1_000_000
MAX_WHERE_VALUE_LENGTH = 120
DEFAULT_PAGE_SLACK = 2  # extra pages beyond ceil(count/page_size)
HARD_MAX_PAGES = 200  # absolute ceiling regardless of caller input

# Safe-shape allowlists for untrusted strings embedded in URLs, drift
# signals, or error payloads (same repr()-sanitize policy as pluto G5 F4).
_FIELD_NAME_SAFE_RE = re.compile(r"^[A-Za-z0-9_]{1,64}$")
_WHERE_VALUE_SAFE_RE = re.compile(r"^[A-Za-z0-9 .,'()/&+-]{1,120}$")
_SAFE_TEXT_RE = re.compile(r"^[A-Za-z0-9 .,:;'\"()\[\]/_%=-]{1,300}$")
# Retry-After sanitization moved to app.resilience.transport (M2-T011),
# allowlist and repr()-sanitize policy unchanged.


# ---------------------------------------------------------------------------
# Error taxonomy (packet requirement: upstream_error, malformed_response,
# schema_drift, budget_exhausted, circuit_open, timeout, rate_limited,
# disallowed_request distinguishable; paging_pathology added for safeguard 3)
# ---------------------------------------------------------------------------


class ZoningFeaturesConnectorError(Exception):
    """Base typed connector error. Payloads never contain stack traces,
    headers, or tokens (the services are keyless; no token exists)."""

    error_type = "upstream_error"

    def __init__(
        self,
        message: str,
        *,
        correlation_id: str,
        layer: str | None = None,
        detail: dict | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.correlation_id = correlation_id
        self.layer = layer
        self.detail = detail or {}

    def to_payload(self) -> dict:
        return {
            "error_type": self.error_type,
            "message": self.message,
            "correlation_id": self.correlation_id,
            "source_id": SOURCE_ID,
            "layer": self.layer,
            "detail": self.detail,
        }


class UpstreamError(ZoningFeaturesConnectorError):
    """Upstream failure: network failure, 5xx persisted through retries,
    unexpected HTTP status, or an ArcGIS error object (even with HTTP 200 -
    live-verified behavior, fixture ZF06)."""

    error_type = "upstream_error"


class MalformedResponseError(ZoningFeaturesConnectorError):
    """Response body is not the well-formed documented shape (invalid JSON,
    missing ``features`` key, non-object feature, missing object id...).
    NEVER converted into a valid empty result."""

    error_type = "malformed_response"


class SchemaDriftError(ZoningFeaturesConnectorError):
    """Layer contract changed (missing/renamed/re-typed field, wrong CRS,
    missing objectIdField/maxRecordCount, lost paging capability). Surfaced
    for alerting; never silently guessed around."""

    error_type = "schema_drift"


class SourceTimeoutError(ZoningFeaturesConnectorError):
    """Connect/read timeout persisted through the retry budget."""

    error_type = "timeout"


class RateLimitedError(ZoningFeaturesConnectorError):
    """HTTP 429 persisted through the bounded retry budget."""

    error_type = "rate_limited"


class DisallowedRequestError(ZoningFeaturesConnectorError):
    """Request refused by the endpoint allowlist BEFORE any network I/O
    (unknown layer, non-allowlisted field, unsafe value, out-of-bounds
    paging parameter). The connector is not a general HTTP client."""

    error_type = "disallowed_request"


class PagingPathologyError(ZoningFeaturesConnectorError):
    """Paged extraction detected upstream misbehavior: ``detail.reason`` is
    one of ``repeated_object_id``, ``duplicate_page``, ``zero_progress``,
    ``page_budget_exhausted``, ``count_mismatch``. Never an infinite loop,
    never silent truncation or duplication."""

    error_type = "paging_pathology"


class RequestBudgetExceededError(ZoningFeaturesConnectorError):
    """Per-analysis upstream request budget exhausted (M1-T009
    ``AnalysisBudget``); raised BEFORE further upstream I/O and never masked
    by cache or last-known-good fallback."""

    error_type = "budget_exhausted"


class CircuitOpenError(ZoningFeaturesConnectorError):
    """Fast rejection while the per-source circuit is open; no upstream I/O
    was performed for this call."""

    error_type = "circuit_open"


# ---------------------------------------------------------------------------
# Sanitizers and small helpers
# ---------------------------------------------------------------------------


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _rfc3339(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_text(value: object) -> str:
    """Untrusted upstream text (error messages/codes, field names) passes
    through only when it matches the conservative allowlist; anything else is
    repr()-sanitized so hostile bytes never reach logs or payloads."""
    if isinstance(value, str) and _SAFE_TEXT_RE.match(value):
        return value
    return repr(value)


def _safe_field_name(value: object) -> str:
    if isinstance(value, str) and _FIELD_NAME_SAFE_RE.match(value):
        return value
    return repr(value)


def raw_body_digest(body: str) -> str:
    """Raw-response digest: exact UTF-8 bytes of the transported body
    (ZF_CANONICALIZATION_SPEC). Order-sensitive by design."""
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def _epoch_ms_to_rfc3339(ms: object) -> str | None:
    if isinstance(ms, bool) or not isinstance(ms, int):
        return None
    try:
        return _rfc3339(datetime.fromtimestamp(ms / 1000.0, UTC))
    except (OverflowError, OSError, ValueError):
        return None


def _require_layer(layer: object, correlation_id: str) -> str:
    """Exact-match allowlist check; the ONLY path from caller input to a URL
    segment. No normalization, no substring tolerance."""
    if isinstance(layer, str) and layer in LAYER_SPECS:
        return layer
    raise DisallowedRequestError(
        "layer is not one of the six allowlisted DCP zoning-features "
        "services (nyzd, nyco, nysp, nysp_sd, nylh, nyzma)",
        correlation_id=correlation_id,
        detail={"layer": repr(layer)},
    )


# ---------------------------------------------------------------------------
# URL construction (all URLs originate here; byte-identical to the fixture
# capture URLs so tests can assert reproduction)
# ---------------------------------------------------------------------------


def build_metadata_url(layer: str, *, correlation_id: str = "urlbuild") -> str:
    layer = _require_layer(layer, correlation_id)
    return f"{SERVICE_ROOT}/{layer}/FeatureServer/0?f=json"


def build_count_url(
    layer: str, where: str = "1=1", *, correlation_id: str = "urlbuild"
) -> str:
    layer = _require_layer(layer, correlation_id)
    _require_known_where(layer, where, correlation_id)
    return (
        f"{SERVICE_ROOT}/{layer}/FeatureServer/0/query"
        f"?where={quote(where, safe='')}&returnCountOnly=true&f=json"
    )


def build_attribute_where(
    layer: str, field_name: str, value: str, *, correlation_id: str = "urlbuild"
) -> str:
    """Bounded equality filter: allowlisted field + character-allowlisted
    value with SQL single quotes escaped by doubling. The ONLY non-trivial
    where clause this connector can emit."""
    layer = _require_layer(layer, correlation_id)
    spec = LAYER_SPECS[layer]
    if not isinstance(field_name, str) or field_name not in spec.queryable_fields:
        raise DisallowedRequestError(
            "field is not in the queryable-attribute allowlist for this layer",
            correlation_id=correlation_id,
            layer=layer,
            detail={
                "field": _safe_field_name(field_name),
                "allowed": sorted(spec.queryable_fields),
            },
        )
    if not isinstance(value, str) or not _WHERE_VALUE_SAFE_RE.match(value):
        raise DisallowedRequestError(
            "attribute value failed the character allowlist "
            "(letters, digits, space, . , ' ( ) / & + - up to "
            f"{MAX_WHERE_VALUE_LENGTH} chars)",
            correlation_id=correlation_id,
            layer=layer,
            detail={"value": repr(value)},
        )
    escaped = value.replace("'", "''")
    return f"{field_name}='{escaped}'"


def _require_known_where(layer: str, where: str, correlation_id: str) -> None:
    """A where clause must be the constant ``1=1`` or reproducible by
    ``build_attribute_where`` (allowlisted field, allowlisted value)."""
    if where == "1=1":
        return
    match = re.fullmatch(r"([A-Za-z0-9_]{1,64})='((?:[^']|'')*)'", where)
    if match:
        field_name, escaped_value = match.group(1), match.group(2)
        value = escaped_value.replace("''", "'")
        spec = LAYER_SPECS[layer]
        if field_name in spec.queryable_fields and _WHERE_VALUE_SAFE_RE.match(value):
            return
    raise DisallowedRequestError(
        "where clause is not a connector-built bounded filter",
        correlation_id=correlation_id,
        layer=layer,
        detail={"where": repr(where)},
    )


def build_query_url(
    layer: str,
    where: str,
    *,
    out_fields: object = "*",
    order_by_field: str = "OBJECTID",
    result_record_count: int,
    result_offset: int,
    correlation_id: str = "urlbuild",
) -> str:
    layer = _require_layer(layer, correlation_id)
    _require_known_where(layer, where, correlation_id)
    spec = LAYER_SPECS[layer]
    if out_fields == "*":
        out_fields_param = "*"
    elif isinstance(out_fields, list | tuple) and out_fields:
        unknown = [f for f in out_fields if f not in spec.fields]
        if unknown:
            raise DisallowedRequestError(
                "outFields contains non-allowlisted field names",
                correlation_id=correlation_id,
                layer=layer,
                detail={"unknown": [_safe_field_name(f) for f in unknown]},
            )
        out_fields_param = ",".join(out_fields)
    else:
        raise DisallowedRequestError(
            "outFields must be '*' or a non-empty list of known field names",
            correlation_id=correlation_id,
            layer=layer,
            detail={"out_fields": repr(out_fields)},
        )
    if (
        not isinstance(order_by_field, str)
        or not _FIELD_NAME_SAFE_RE.match(order_by_field)
        or order_by_field not in spec.fields
    ):
        raise DisallowedRequestError(
            "order-by field must be a known field of the layer",
            correlation_id=correlation_id,
            layer=layer,
            detail={"order_by_field": _safe_field_name(order_by_field)},
        )
    if (
        isinstance(result_record_count, bool)
        or not isinstance(result_record_count, int)
        or not 1 <= result_record_count <= MAX_RESULT_RECORD_COUNT
    ):
        raise DisallowedRequestError(
            f"resultRecordCount must be an integer in 1..{MAX_RESULT_RECORD_COUNT}",
            correlation_id=correlation_id,
            layer=layer,
            detail={"result_record_count": repr(result_record_count)},
        )
    if (
        isinstance(result_offset, bool)
        or not isinstance(result_offset, int)
        or not 0 <= result_offset <= MAX_RESULT_OFFSET
    ):
        raise DisallowedRequestError(
            f"resultOffset must be an integer in 0..{MAX_RESULT_OFFSET}",
            correlation_id=correlation_id,
            layer=layer,
            detail={"result_offset": repr(result_offset)},
        )
    return (
        f"{SERVICE_ROOT}/{layer}/FeatureServer/0/query"
        f"?where={quote(where, safe='')}"
        f"&outFields={out_fields_param}"
        f"&orderByFields={quote(f'{order_by_field} ASC', safe='')}"
        f"&resultRecordCount={result_record_count}"
        f"&resultOffset={result_offset}"
        "&f=json"
    )


# ---------------------------------------------------------------------------
# Transport request with bounded retry (single retry authority for the plain
# functions). Task M2-T011: the accepted control flow now runs in the shared
# engine (app.resilience.transport.request_with_retry) with the M1-T009
# jitter/Retry-After delay policy; the connector-specific error taxonomy,
# messages, and layer tagging stay here through the RetryHooks seam.
# ---------------------------------------------------------------------------


def _request_with_retry(
    url: str,
    *,
    layer: str,
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
    unexpected statuses (including refused 3xx redirects) and every parse or
    drift condition are never retried. One budget unit per upstream ATTEMPT
    (every network call costs quota), consumed BEFORE the I/O."""

    return request_with_retry(
        url,
        transport=transport,
        headers={"Accept": "application/json"},
        timeout=timeout,
        max_attempts=max_attempts,
        hooks=standard_retry_hooks(
            logger=logger,
            log_label="zoning_features",
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
            # Every typed error of this connector carries the layer tag.
            error_kwargs={"layer": layer},
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


def _parse_json_object(
    body: str, *, url: str, layer: str, correlation_id: str
) -> dict:
    """Parse a response body into a JSON object; classify the ArcGIS
    error-object-with-HTTP-200 as a typed UPSTREAM error (live-verified,
    fixture ZF06), and everything unparseable as malformed_response."""
    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise MalformedResponseError(
            "ArcGIS returned HTTP 200 with a body that is not valid JSON; "
            "refusing to interpret it (never an empty result)",
            correlation_id=correlation_id,
            layer=layer,
            detail={"url": url, "parse_error": type(exc).__name__},
        ) from exc
    if not isinstance(parsed, dict):
        raise MalformedResponseError(
            "ArcGIS response is not a JSON object",
            correlation_id=correlation_id,
            layer=layer,
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
            layer=layer,
            detail={
                "url": url,
                "arcgis_error_code": code if isinstance(code, int) else repr(code),
                "arcgis_error_message": _safe_text(message),
            },
        )
    return parsed


def _validate_page_envelope(
    doc: dict,
    *,
    url: str,
    layer: str,
    object_id_field: str,
    correlation_id: str,
    drift_signals: list[str],
) -> tuple[list[tuple[int, dict]], bool]:
    """Validate a query-response envelope; return ``[(object_id, feature)]``
    in RESPONSE order plus the ``exceededTransferLimit`` flag. A well-formed
    empty ``features`` array is a VALID empty page; every malformed shape is
    a typed failure - never coerced."""
    if "features" not in doc:
        raise MalformedResponseError(
            "query response has no 'features' key; a malformed response is "
            "never a valid empty result",
            correlation_id=correlation_id,
            layer=layer,
            detail={"url": url, "keys": sorted(map(_safe_text, doc.keys()))},
        )
    features = doc["features"]
    if not isinstance(features, list):
        raise MalformedResponseError(
            "'features' is not a JSON array",
            correlation_id=correlation_id,
            layer=layer,
            detail={"url": url, "features_type": type(features).__name__},
        )
    response_oid_field = doc.get("objectIdFieldName")
    if isinstance(response_oid_field, str) and response_oid_field != object_id_field:
        raise SchemaDriftError(
            "response objectIdFieldName differs from the validated layer "
            "objectIdField",
            correlation_id=correlation_id,
            layer=layer,
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
            raise SchemaDriftError(
                "query response spatial reference is not the authoritative "
                f"EPSG:2263 (wkid {EXPECTED_WKID} / latestWkid "
                f"{EXPECTED_LATEST_WKID})",
                correlation_id=correlation_id,
                layer=layer,
                detail={"url": url, "spatial_reference": repr(sr)},
            )
    elif features:
        # Live services include spatialReference whenever features are
        # present (absent only on empty results, fixture ZF05). Visible
        # degradation; the validated LAYER metadata CRS still governs.
        drift_signals.append("page_missing_spatial_reference")
    known_fields = LAYER_SPECS[layer].fields
    extracted: list[tuple[int, dict]] = []
    for index, feature in enumerate(features):
        if not isinstance(feature, dict) or not isinstance(
            feature.get("attributes"), dict
        ):
            raise MalformedResponseError(
                "feature is not an object with an 'attributes' map",
                correlation_id=correlation_id,
                layer=layer,
                detail={"url": url, "feature_index": index},
            )
        attributes = feature["attributes"]
        oid = attributes.get(object_id_field)
        if isinstance(oid, bool) or not isinstance(oid, int):
            raise MalformedResponseError(
                f"feature attributes lack an integer '{object_id_field}'",
                correlation_id=correlation_id,
                layer=layer,
                detail={"url": url, "feature_index": index},
            )
        for name in attributes:
            if name not in known_fields:
                signal = f"unknown_attribute:{_safe_field_name(name)}"
                if signal not in drift_signals:
                    drift_signals.append(signal)
        extracted.append((oid, feature))
    exceeded = doc.get("exceededTransferLimit") is True
    return extracted, exceeded


def _normalize_features(
    pairs: list[tuple[int, dict]],
    *,
    layer: str,
    correlation_id: str,
) -> list[dict]:
    """Deterministic normalization per ZF_CANONICALIZATION_SPEC: sort by
    object id, keep attributes and esri geometry VERBATIM (no value
    invention, no reprojection). Duplicate ids are a typed pathology."""
    seen: set[int] = set()
    for oid, _ in pairs:
        if oid in seen:
            raise PagingPathologyError(
                "duplicate object id within the extracted feature set",
                correlation_id=correlation_id,
                layer=layer,
                detail={"reason": "repeated_object_id", "object_id": oid},
            )
        seen.add(oid)
    normalized = [
        {
            "object_id": oid,
            "attributes": feature["attributes"],
            "geometry": feature.get("geometry"),
        }
        for oid, feature in sorted(pairs, key=lambda pair: pair[0])
    ]
    return normalized


# ---------------------------------------------------------------------------
# Result contracts
# ---------------------------------------------------------------------------


@dataclass
class LayerMetadata:
    """Validated layer-0 metadata snapshot with provenance."""

    layer: str
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
class LayerCountResult:
    layer: str
    correlation_id: str
    request_url: str
    retrieved_at: str
    where: str
    count: int
    raw_digest: str


@dataclass
class LayerQueryResult:
    """Bounded attribute-query result. A well-formed empty ``features``
    array is a VALID empty result (``record_count`` 0); ``staleness`` is
    transport/cache serve state ONLY (two-staleness rule) and is None on
    every fresh retrieval this module performs."""

    status: str  # always "ok" for well-formed responses
    layer: str
    correlation_id: str
    request_url: str
    metadata_request_url: str
    retrieved_at: str
    record_count: int
    features: list[dict]
    exceeded_transfer_limit: bool
    object_id_field: str
    geometry_type: str
    crs: dict
    source_data_last_edited_ms: int | None
    source_data_last_edited: str | None
    raw_digest: str
    metadata_raw_digest: str
    normalized_digest: str
    digest_canonicalization: str
    drift_signals: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    staleness: dict | None = None


@dataclass
class LayerExtractResult:
    """Complete paged extraction of one layer with full provenance and the
    SEPARATE raw/normalized digest record."""

    status: str  # always "ok" when extraction completes
    layer: str
    correlation_id: str
    service_url: str
    metadata_request_url: str
    count_request_url: str
    page_request_urls: list[str]
    retrieved_at: str
    object_id_field: str
    geometry_type: str
    crs: dict
    max_record_count: int
    page_size: int
    page_count: int
    expected_count: int
    record_count: int
    features: list[dict]
    source_data_last_edited_ms: int | None
    source_data_last_edited: str | None
    metadata_raw_digest: str
    count_raw_digest: str
    page_raw_digests: list[str]
    normalized_digest: str
    digest_canonicalization: str
    drift_signals: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    staleness: dict | None = None


# ---------------------------------------------------------------------------
# Public operations (plain, fixture-testable, offline-deterministic)
# ---------------------------------------------------------------------------


def fetch_layer_metadata(
    layer: str,
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
) -> LayerMetadata:
    """Fetch and VALIDATE layer-0 metadata (packet safeguard 2). Typed
    ``schema_drift`` on: missing objectIdField, missing/renamed/re-typed
    expected fields, wrong CRS, missing/invalid maxRecordCount, lost
    pagination/order-by capability, wrong geometry type, layer-name
    mismatch. ADDED fields and missing editingInfo are visible drift
    signals (typed degradation), never silent."""
    correlation_id = correlation_id or uuid.uuid4().hex
    layer = _require_layer(layer, correlation_id)
    url = build_metadata_url(layer, correlation_id=correlation_id)
    response = _request_with_retry(
        url,
        layer=layer,
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
    doc = _parse_json_object(
        response.body, url=url, layer=layer, correlation_id=correlation_id
    )
    drift_signals: list[str] = []

    name = doc.get("name")
    if name != layer:
        raise SchemaDriftError(
            "service metadata 'name' does not match the canonical layer name",
            correlation_id=correlation_id,
            layer=layer,
            detail={"url": url, "name": _safe_text(name)},
        )

    object_id_field = doc.get("objectIdField")
    if not isinstance(object_id_field, str) or not object_id_field:
        raise SchemaDriftError(
            "layer metadata has no objectIdField; deterministic paging "
            "order cannot be established - refusing to guess",
            correlation_id=correlation_id,
            layer=layer,
            detail={"url": url, "object_id_field": repr(object_id_field)},
        )
    if not _FIELD_NAME_SAFE_RE.match(object_id_field):
        raise SchemaDriftError(
            "objectIdField failed the field-name allowlist",
            correlation_id=correlation_id,
            layer=layer,
            detail={"url": url, "object_id_field": repr(object_id_field)},
        )

    raw_fields = doc.get("fields")
    if not isinstance(raw_fields, list):
        raise SchemaDriftError(
            "layer metadata has no fields array",
            correlation_id=correlation_id,
            layer=layer,
            detail={"url": url},
        )
    live_fields: dict[str, str] = {}
    for entry in raw_fields:
        if isinstance(entry, dict) and isinstance(entry.get("name"), str):
            live_fields[entry["name"]] = str(entry.get("type"))
    expected = LAYER_SPECS[layer].fields
    missing = sorted(set(expected) - set(live_fields))
    if missing:
        raise SchemaDriftError(
            "expected field(s) missing from the live layer schema "
            "(renamed or removed) - never silently guessed",
            correlation_id=correlation_id,
            layer=layer,
            detail={"url": url, "missing_fields": missing},
        )
    retyped = sorted(
        name for name in expected if live_fields[name] != expected[name]
    )
    if retyped:
        raise SchemaDriftError(
            "field type(s) changed in the live layer schema",
            correlation_id=correlation_id,
            layer=layer,
            detail={
                "url": url,
                "retyped": {
                    name: {"expected": expected[name], "actual": live_fields[name]}
                    for name in retyped
                },
            },
        )
    for added in sorted(set(live_fields) - set(expected)):
        drift_signals.append(f"added_field:{_safe_field_name(added)}")
    if object_id_field not in expected:
        raise SchemaDriftError(
            "objectIdField is not part of the expected field inventory",
            correlation_id=correlation_id,
            layer=layer,
            detail={"url": url, "object_id_field": object_id_field},
        )

    geometry_type = doc.get("geometryType")
    if geometry_type != EXPECTED_GEOMETRY_TYPE:
        raise SchemaDriftError(
            f"geometryType is not {EXPECTED_GEOMETRY_TYPE}",
            correlation_id=correlation_id,
            layer=layer,
            detail={"url": url, "geometry_type": _safe_text(geometry_type)},
        )

    sr = (doc.get("extent") or {}).get("spatialReference") \
        if isinstance(doc.get("extent"), dict) else None
    if (
        not isinstance(sr, dict)
        or sr.get("wkid") != EXPECTED_WKID
        or sr.get("latestWkid") != EXPECTED_LATEST_WKID
    ):
        raise SchemaDriftError(
            "layer spatial reference is not the authoritative EPSG:2263 "
            f"(wkid {EXPECTED_WKID} / latestWkid {EXPECTED_LATEST_WKID}); "
            "geometry in an unexpected CRS must not be consumed",
            correlation_id=correlation_id,
            layer=layer,
            detail={"url": url, "spatial_reference": repr(sr)},
        )

    max_record_count = doc.get("maxRecordCount")
    if (
        isinstance(max_record_count, bool)
        or not isinstance(max_record_count, int)
        or max_record_count < 1
    ):
        raise SchemaDriftError(
            "maxRecordCount missing or invalid; paging cannot be planned "
            "safely without the official transfer limit",
            correlation_id=correlation_id,
            layer=layer,
            detail={"url": url, "max_record_count": repr(max_record_count)},
        )

    capabilities = doc.get("advancedQueryCapabilities")
    supports_pagination = bool(
        isinstance(capabilities, dict) and capabilities.get("supportsPagination") is True
    )
    supports_order_by = bool(
        isinstance(capabilities, dict) and capabilities.get("supportsOrderBy") is True
    )
    if not supports_pagination or not supports_order_by:
        raise SchemaDriftError(
            "layer no longer advertises supportsPagination/supportsOrderBy; "
            "deterministic paged extraction is impossible - refusing to "
            "fall back to unordered reads",
            correlation_id=correlation_id,
            layer=layer,
            detail={
                "url": url,
                "supports_pagination": supports_pagination,
                "supports_order_by": supports_order_by,
            },
        )

    editing = doc.get("editingInfo")
    data_last_edited_ms: int | None = None
    if isinstance(editing, dict) and not isinstance(
        editing.get("dataLastEditDate"), bool
    ) and isinstance(editing.get("dataLastEditDate"), int):
        data_last_edited_ms = editing["dataLastEditDate"]
    else:
        # Provenance-only signal: freshness stamp unavailable. Visible
        # degradation, not fatal (the data itself is still validated).
        drift_signals.append("missing_editing_info")
    data_last_edited = _epoch_ms_to_rfc3339(data_last_edited_ms)

    logger.info(
        "zoning_features metadata ok layer=%s max_record_count=%d "
        "data_last_edited=%s drift_signals=%d correlation_id=%s",
        layer, max_record_count, data_last_edited, len(drift_signals),
        correlation_id,
    )
    return LayerMetadata(
        layer=layer,
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


def fetch_layer_count(
    layer: str,
    *,
    where: str = "1=1",
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
) -> LayerCountResult:
    """returnCountOnly baseline with provenance (scenario ZF-S2)."""
    correlation_id = correlation_id or uuid.uuid4().hex
    layer = _require_layer(layer, correlation_id)
    url = build_count_url(layer, where, correlation_id=correlation_id)
    response = _request_with_retry(
        url,
        layer=layer,
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
    doc = _parse_json_object(
        response.body, url=url, layer=layer, correlation_id=correlation_id
    )
    count = doc.get("count")
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise MalformedResponseError(
            "returnCountOnly response has no non-negative integer 'count'",
            correlation_id=correlation_id,
            layer=layer,
            detail={"url": url, "count": repr(count)},
        )
    return LayerCountResult(
        layer=layer,
        correlation_id=correlation_id,
        request_url=url,
        retrieved_at=retrieved_at,
        where=where,
        count=count,
        raw_digest=raw_body_digest(response.body),
    )


def query_features(
    layer: str,
    field_name: str,
    value: str,
    *,
    result_record_count: int = 1,
    result_offset: int = 0,
    out_fields: object = "*",
    metadata: LayerMetadata | None = None,
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
) -> LayerQueryResult:
    """Bounded attribute equality query (scenario ZF-S3). When ``metadata``
    is not injected it is fetched (and fully validated) first so every
    result carries the source edit timestamp and validated CRS."""
    correlation_id = correlation_id or uuid.uuid4().hex
    layer = _require_layer(layer, correlation_id)
    common = dict(
        transport=transport,
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        backoff_cap=backoff_cap,
        retry_after_cap=retry_after_cap,
        rng=rng or Random(),
        sleep=sleep,
        clock=clock,
        correlation_id=correlation_id,
        budget=budget,
    )
    if metadata is None:
        metadata = fetch_layer_metadata(layer, **common)
    where = build_attribute_where(
        layer, field_name, value, correlation_id=correlation_id
    )
    url = build_query_url(
        layer,
        where,
        out_fields=out_fields,
        order_by_field=metadata.object_id_field,
        result_record_count=result_record_count,
        result_offset=result_offset,
        correlation_id=correlation_id,
    )
    response = _request_with_retry(
        url,
        layer=layer,
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
    doc = _parse_json_object(
        response.body, url=url, layer=layer, correlation_id=correlation_id
    )
    drift_signals = list(metadata.drift_signals)
    pairs, exceeded = _validate_page_envelope(
        doc,
        url=url,
        layer=layer,
        object_id_field=metadata.object_id_field,
        correlation_id=correlation_id,
        drift_signals=drift_signals,
    )
    normalized = _normalize_features(
        pairs, layer=layer, correlation_id=correlation_id
    )
    notes: list[str] = []
    if exceeded:
        notes.append(
            "exceeded_transfer_limit: more matching features exist than the "
            "bounded resultRecordCount returned; this is a bounded query, "
            "not a truncated extraction (use extract_layer for completeness)."
        )
    if not normalized:
        notes.append(
            "empty_result: the official service returned a well-formed "
            "response with zero matching features; this is a valid empty "
            "result, not an error."
        )
    logger.info(
        "zoning_features query ok layer=%s records=%d exceeded=%s "
        "correlation_id=%s",
        layer, len(normalized), exceeded, correlation_id,
    )
    return LayerQueryResult(
        status="ok",
        layer=layer,
        correlation_id=correlation_id,
        request_url=url,
        metadata_request_url=metadata.request_url,
        retrieved_at=retrieved_at,
        record_count=len(normalized),
        features=normalized,
        exceeded_transfer_limit=exceeded,
        object_id_field=metadata.object_id_field,
        geometry_type=metadata.geometry_type,
        crs=dict(CRS_STAMP),
        source_data_last_edited_ms=metadata.source_data_last_edited_ms,
        source_data_last_edited=metadata.source_data_last_edited,
        raw_digest=raw_body_digest(response.body),
        metadata_raw_digest=metadata.raw_digest,
        normalized_digest=canonical_json_digest(normalized),
        digest_canonicalization=ZF_CANONICALIZATION_SPEC,
        drift_signals=drift_signals,
        notes=notes,
    )


def extract_layer(
    layer: str,
    *,
    page_size: int | None = None,
    max_pages: int | None = None,
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
) -> LayerExtractResult:
    """Complete deterministic paged extraction of one layer (safeguard 3).

    Request sequence: metadata -> count -> pages ordered by the validated
    objectIdField ascending with explicit resultOffset. Paging is MANDATORY
    on every layer: live counts exceed maxRecordCount on nysp/nysp_sd/nyzma
    and nylh sits exactly at its cap (research C3), so an unpaged request
    silently truncates.

    Loop-safety guarantees (each violation is a typed ``paging_pathology``):
    repeated object ids across pages, byte-duplicate pages, zero-progress
    responses (empty page with exceededTransferLimit), a bounded page budget
    (``max_pages`` or ceil(count/page_size) + slack, hard-capped), and a
    final count-vs-extracted consistency check. Never an infinite loop,
    never silent truncation or duplication.
    """
    correlation_id = correlation_id or uuid.uuid4().hex
    layer = _require_layer(layer, correlation_id)
    rng = rng or Random()
    request_kwargs = dict(
        layer=layer,
        transport=transport,
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        backoff_cap=backoff_cap,
        retry_after_cap=retry_after_cap,
        rng=rng,
        sleep=sleep,
        wall_clock=clock,
        correlation_id=correlation_id,
        budget=budget,
    )
    metadata = fetch_layer_metadata(
        layer,
        transport=transport,
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        backoff_cap=backoff_cap,
        retry_after_cap=retry_after_cap,
        rng=rng,
        sleep=sleep,
        clock=clock,
        correlation_id=correlation_id,
        budget=budget,
    )
    count_result = fetch_layer_count(
        layer,
        transport=transport,
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        backoff_cap=backoff_cap,
        retry_after_cap=retry_after_cap,
        rng=rng,
        sleep=sleep,
        clock=clock,
        correlation_id=correlation_id,
        budget=budget,
    )
    expected_count = count_result.count

    if page_size is None:
        effective_page_size = metadata.max_record_count
    else:
        if (
            isinstance(page_size, bool)
            or not isinstance(page_size, int)
            or page_size < 1
        ):
            raise DisallowedRequestError(
                "page_size must be an integer >= 1",
                correlation_id=correlation_id,
                layer=layer,
                detail={"page_size": repr(page_size)},
            )
        effective_page_size = min(page_size, metadata.max_record_count)

    computed_budget = (
        math.ceil(expected_count / effective_page_size) + DEFAULT_PAGE_SLACK
        if expected_count > 0
        else 0
    )
    if max_pages is not None and (
        isinstance(max_pages, bool) or not isinstance(max_pages, int) or max_pages < 1
    ):
        raise DisallowedRequestError(
            "max_pages must be an integer >= 1",
            correlation_id=correlation_id,
            layer=layer,
            detail={"max_pages": repr(max_pages)},
        )
    page_budget = min(
        max_pages if max_pages is not None else computed_budget, HARD_MAX_PAGES
    )

    drift_signals = list(metadata.drift_signals)
    notes: list[str] = []
    collected: list[tuple[int, dict]] = []
    seen_oids: set[int] = set()
    previous_page_oids: list[int] | None = None
    page_urls: list[str] = []
    page_digests: list[str] = []
    pages_fetched = 0
    retrieved_at = count_result.retrieved_at

    if expected_count == 0:
        notes.append(
            "empty_layer: official count is 0; no page requests were made. "
            "A well-formed zero count is a valid empty extraction."
        )

    # Loop safety: every iteration either raises typed (page budget,
    # zero-progress, duplicate/repeated ids) or strictly grows ``collected``
    # toward ``expected_count`` / breaks - never an unbounded spin.
    while True:
        if len(collected) >= expected_count:
            break
        if pages_fetched >= page_budget:
            raise PagingPathologyError(
                "page budget exhausted before the extraction completed; "
                "refusing to loop further (never an infinite loop)",
                correlation_id=correlation_id,
                layer=layer,
                detail={
                    "reason": "page_budget_exhausted",
                    "pages_fetched": pages_fetched,
                    "page_budget": page_budget,
                    "collected": len(collected),
                    "expected_count": expected_count,
                },
            )
        url = build_query_url(
            layer,
            "1=1",
            out_fields="*",
            order_by_field=metadata.object_id_field,
            result_record_count=effective_page_size,
            result_offset=len(collected),
            correlation_id=correlation_id,
        )
        response = _request_with_retry(url, **request_kwargs)
        retrieved_at = _rfc3339(clock())
        pages_fetched += 1
        page_urls.append(url)
        page_digests.append(raw_body_digest(response.body))
        doc = _parse_json_object(
            response.body, url=url, layer=layer, correlation_id=correlation_id
        )
        pairs, exceeded = _validate_page_envelope(
            doc,
            url=url,
            layer=layer,
            object_id_field=metadata.object_id_field,
            correlation_id=correlation_id,
            drift_signals=drift_signals,
        )
        page_oids = [oid for oid, _ in pairs]
        if not pairs:
            if exceeded:
                raise PagingPathologyError(
                    "empty page with exceededTransferLimit=true: the "
                    "service reports more data but returns none "
                    "(zero-progress loop) - aborting typed",
                    correlation_id=correlation_id,
                    layer=layer,
                    detail={
                        "reason": "zero_progress",
                        "page_index": pages_fetched - 1,
                        "collected": len(collected),
                        "expected_count": expected_count,
                    },
                )
            break  # well-formed end of data
        if previous_page_oids is not None and page_oids == previous_page_oids:
            raise PagingPathologyError(
                "page is identical to the previous page (upstream returned "
                "the same page twice) - aborting typed, no silent duplication",
                correlation_id=correlation_id,
                layer=layer,
                detail={
                    "reason": "duplicate_page",
                    "page_index": pages_fetched - 1,
                },
            )
        overlap = sorted(set(page_oids) & seen_oids)
        if overlap:
            raise PagingPathologyError(
                "page repeats object id(s) already extracted from an "
                "earlier page - aborting typed, no silent duplication",
                correlation_id=correlation_id,
                layer=layer,
                detail={
                    "reason": "repeated_object_id",
                    "page_index": pages_fetched - 1,
                    "repeated_object_ids": overlap[:20],
                },
            )
        if page_oids != sorted(page_oids):
            signal = f"unordered_page:{pages_fetched - 1}"
            if signal not in drift_signals:
                # Server ignored orderByFields: visible degradation; the
                # final normalization still sorts deterministically.
                drift_signals.append(signal)
        seen_oids.update(page_oids)
        collected.extend(pairs)
        previous_page_oids = page_oids
        if len(pairs) < effective_page_size and not exceeded:
            break  # final short page

    if len(collected) != expected_count:
        raise PagingPathologyError(
            "extracted record total does not equal the official "
            "returnCountOnly baseline - refusing to serve a silently "
            "incomplete or inflated extraction",
            correlation_id=correlation_id,
            layer=layer,
            detail={
                "reason": "count_mismatch",
                "extracted": len(collected),
                "expected_count": expected_count,
                "pages_fetched": pages_fetched,
            },
        )

    normalized = _normalize_features(
        collected, layer=layer, correlation_id=correlation_id
    )
    logger.info(
        "zoning_features extract ok layer=%s records=%d pages=%d "
        "drift_signals=%d correlation_id=%s",
        layer, len(normalized), pages_fetched, len(drift_signals), correlation_id,
    )
    return LayerExtractResult(
        status="ok",
        layer=layer,
        correlation_id=correlation_id,
        service_url=f"{SERVICE_ROOT}/{layer}/FeatureServer",
        metadata_request_url=metadata.request_url,
        count_request_url=count_result.request_url,
        page_request_urls=page_urls,
        retrieved_at=retrieved_at,
        object_id_field=metadata.object_id_field,
        geometry_type=metadata.geometry_type,
        crs=dict(CRS_STAMP),
        max_record_count=metadata.max_record_count,
        page_size=effective_page_size,
        page_count=pages_fetched,
        expected_count=expected_count,
        record_count=len(normalized),
        features=normalized,
        source_data_last_edited_ms=metadata.source_data_last_edited_ms,
        source_data_last_edited=metadata.source_data_last_edited,
        metadata_raw_digest=metadata.raw_digest,
        count_raw_digest=count_result.raw_digest,
        page_raw_digests=page_digests,
        normalized_digest=canonical_json_digest(normalized),
        digest_canonicalization=ZF_CANONICALIZATION_SPEC,
        drift_signals=drift_signals,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Resilient client (M1-T009 primitives composed; no second resilience system)
# ---------------------------------------------------------------------------


@dataclass
class _LkgEntry:
    stored_at: float
    result: LayerExtractResult


def _is_transient(exc: ZoningFeaturesConnectorError) -> bool:
    """Transient upstream trouble only: rate limit, timeout, network, 5xx.
    Schema drift, malformed responses, paging pathologies, disallowed
    requests, and ArcGIS error objects are NOT transient (retrying or
    serving stale data would mask a real contract problem)."""
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


class ResilientZoningFeaturesClient:
    """Cache + circuit breaker + last-known-good + budget composition around
    ``extract_layer``, built ENTIRELY from the M1-T009 primitives
    (``TTLCache``, ``CircuitBreaker``, ``AnalysisBudget``,
    ``ResilienceConfig``, ``ResilienceMetrics``; retry lives in the plain
    functions via ``backoff_delay``/``parse_retry_after``).

    TWO-STALENESS RULE: ``staleness`` is stamped HERE and ONLY here -
    ``{served_from_cache, stale, ...}`` describes the transport/cache serve
    path. ``source_data_last_edited`` (dataLastEditDate provenance) is
    copied verbatim from the original result on every serve path and NEVER
    influences the staleness stamp: an old source dataset retrieved fresh is
    NOT stale; a cache/LKG serve does not alter source timestamps.
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

    def _cache_key(self, layer: str, page_size: int | None) -> str:
        return (
            f"{self._config.cache_key_version}:{SOURCE_ID}:{layer}:extract:"
            f"page_size={page_size}"
        )

    def extract_layer(
        self,
        layer: str,
        *,
        correlation_id: str | None = None,
        budget: AnalysisBudget | None = None,
        page_size: int | None = None,
        max_pages: int | None = None,
    ) -> LayerExtractResult:
        correlation_id = correlation_id or uuid.uuid4().hex
        layer = _require_layer(layer, correlation_id)  # allowlist BEFORE cache
        key = self._cache_key(layer, page_size)

        hit = self._cache.get_with_age(key)
        if hit is not None:
            cached, age_seconds = hit
            self.metrics.emit("cache_hit", key=key, correlation_id=correlation_id)
            result: LayerExtractResult = copy.deepcopy(cached)  # type: ignore[assignment]
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
                layer=layer,
                detail={
                    "circuit": "open",
                    "cooldown_remaining_seconds": self._breaker.cooldown_remaining(),
                },
            )
            return self._serve_lkg_or_raise(key, correlation_id, rejection)

        try:
            result = extract_layer(
                layer,
                page_size=page_size,
                max_pages=max_pages,
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
        except ZoningFeaturesConnectorError as exc:
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

    def _store_lkg(self, key: str, result: LayerExtractResult) -> None:
        with self._lkg_lock:
            self._lkg[key] = _LkgEntry(
                stored_at=self._now(), result=copy.deepcopy(result)
            )
            self._lkg.move_to_end(key)
            while len(self._lkg) > self._config.lkg_max_entries:
                self._lkg.popitem(last=False)

    def _serve_lkg_or_raise(
        self, key: str, correlation_id: str, exc: ZoningFeaturesConnectorError
    ) -> LayerExtractResult:
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
            "official source edit date (two-staleness rule, M2-T007)."
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
