"""PLUTO SODA connector - official NYC Open Data dataset ``64uk-42ks`` (task M1-T002).

Responsibilities (per accepted M1-T001 research, docs/research/pluto-mappluto-2026-07-16.md):

- ``fetch_by_bbl``: per-BBL retrieval with BBL validation BEFORE any network call.
- Canonical source-fact emission: every fact validates against
  ``packages/contracts/schemas/v1/source_fact.schema.json`` and carries full
  provenance (source id, dataset id, request URL, source field name, raw value,
  normalized value, PLUTO version, retrieval timestamp, per-input vintage dates
  when present).
- Null-omission rule: SODA omits null fields per record. The schema comes ONLY
  from the 108-column inventory captured from ``/api/views/64uk-42ks.json``
  (fixture F08, retrieved 2026-07-16); absent keys mean the fact is
  unknown/absent and are surfaced in ``absent_columns`` - NEVER fabricated.
- Typed error taxonomy: ``validation_error`` (raised by
  :mod:`app.connectors.bbl` before any request), ``no_match`` (a RESULT, not an
  error - condo unit-lot BBLs legitimately return ``[]``), ``rate_limited``,
  ``schema_drift``, ``timeout``, ``source_unavailable``.
- HTTP 400 with errorCode ``query.soql.no-such-column`` is the schema-drift
  signature (M1-T001 G1 finding, fixture F13) and is never blindly retried.
  Other 400s (e.g. ``query.soql.type-mismatch``, fixture F13b) are NOT drift.
- Bounded retry with exponential backoff on 429 / 5xx / timeout / network
  failure only.
- Optional ``SOCRATA_APP_TOKEN`` sent as ``X-App-Token`` header: never
  required, never logged, never present in any error payload (tokenless
  requests share the common IP pool - dev.socrata.com/docs/app-tokens, E7).
- Structured errors and results carry a correlation id; no stack traces in
  payloads.

Deterministic code only: no AI, no legal interpretation, no invented values
(PRD sections 2, 9, 23.2). FAR columns are informational facts, never rule
outputs (research section 4.1).
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import time
import urllib.error
import urllib.request
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.connectors.bbl import (
    BBLValidationError,
    check_identifier_consistency,
    normalize_bbl,
)

__all__ = [
    "BASE_URL",
    "CANONICALIZATION_SPEC",
    "DATASET_ID",
    "MAX_RESPONSE_BYTES",
    "PLUTO_COLUMN_TYPES",
    "PLUTO_COLUMNS",
    "PlutoConnectorError",
    "PlutoFetchResult",
    "RateLimitedError",
    "SchemaDriftError",
    "SourceTimeoutError",
    "SourceUnavailableError",
    "TransportFailure",
    "TransportResponse",
    "TransportTimeout",
    "VERSION_RE",
    "VINTAGE_DATE_COLUMNS",
    "build_fact_key",
    "build_page_url",
    "canonical_json_digest",
    "check_columns_for_drift",
    "fetch_by_bbl",
    "urllib_transport",
]

logger = logging.getLogger("app.connectors.pluto_soda")

SOURCE_ID = "nyc-dcp-pluto-soda"  # source registry record 1 (pluto-mappluto.json)
DATASET_ID = "64uk-42ks"
BASE_URL = "https://data.cityofnewyork.us/resource/64uk-42ks.json"
API_VIEWS_URL = "https://data.cityofnewyork.us/api/views/64uk-42ks.json"
APP_TOKEN_ENV_VAR = "SOCRATA_APP_TOKEN"

# PLUTO release version format, e.g. 26v1 or 26v1.1 (README 26v1 release model).
VERSION_RE = re.compile(r"^\d{2}v\d+(\.\d+)?$")

# Schema-drift failure signature (M1-T001 G1 finding; fixture F13).
SCHEMA_DRIFT_ERROR_CODE = "query.soql.no-such-column"

# G5 F1: bounded response read. Expected per-BBL bodies are ~1.5 KB; anything
# beyond this cap indicates a compromised/misbehaving endpoint and is refused
# instead of exhausting worker memory.
MAX_RESPONSE_BYTES = 10 * 1024 * 1024

# G5 F4: Socrata errorCode values observed officially are dotted lowercase
# tokens (e.g. query.soql.no-such-column). Anything outside this shape is
# repr()-sanitized before being embedded in an error payload so a hostile
# response can never inject control characters into caller logs.
_ERROR_CODE_SAFE_RE = re.compile(r"^[A-Za-z0-9._-]{1,120}$")

# Task M1-T009: Retry-After is untrusted response data. Both RFC 9110 forms
# (delay-seconds and HTTP-date, e.g. "Fri, 17 Jul 2026 08:00:00 GMT") match
# this allowlist and pass through verbatim; anything else is repr()-sanitized
# before entering the typed-error detail (same policy as errorCode above).
# The resilience layer parses the value; unparseable -> jittered backoff.
_RETRY_AFTER_SAFE_RE = re.compile(r"^[A-Za-z0-9,: +\-]{1,64}$")

# Per-input vintage date columns = per-record effective-date bounds
# (research section 4.2, G1 C5). Socrata-typed text; nullable per record (F1v).
VINTAGE_DATE_COLUMNS = (
    "basempdate",
    "dcasdate",
    "edesigdate",
    "landmkdate",
    "masdate",
    "polidate",
    "rpaddate",
    "zoningdate",
)

# Condo lot-number semantics (official meta_mappluto.pdf, verified at M1-T001 G1):
# unit lots 1001-6999, billing lots 7501-7599; PLUTO carries one record per
# condominium complex under the billing BBL (README 26v1, research section 4.4).
CONDO_UNIT_LOT_RANGE = (1001, 6999)
CONDO_BILLING_LOT_RANGE = (7501, 7599)

# ---------------------------------------------------------------------------
# 108-column inventory with official Socrata dataTypeName per column.
# Source: /api/views/64uk-42ks.json columns array, retrieved 2026-07-16
# (fixture F08_api_views_columns_snapshot.json - the test suite cross-checks
# this constant against that fixture, so transcription drift fails the build).
# NEVER infer schema from record keys (SODA omits null fields per record).
# ---------------------------------------------------------------------------
PLUTO_COLUMN_TYPES: dict[str, str] = {
    "borough": "text", "block": "number", "lot": "number", "cd": "number",
    "ct2010": "number", "cb2010": "number", "schooldist": "number",
    "council": "number", "zipcode": "number", "firecomp": "text",
    "policeprct": "number", "healtharea": "number", "sanitboro": "number",
    "sanitsub": "text", "address": "text", "zonedist1": "text",
    "zonedist2": "text", "zonedist3": "text", "zonedist4": "text",
    "overlay1": "text", "overlay2": "text", "spdist1": "text",
    "spdist2": "text", "spdist3": "text", "ltdheight": "text",
    "splitzone": "checkbox", "bldgclass": "text", "landuse": "number",
    "easements": "number", "ownertype": "text", "ownername": "text",
    "lotarea": "number", "bldgarea": "number", "comarea": "number",
    "resarea": "number", "officearea": "number", "retailarea": "number",
    "garagearea": "number", "strgearea": "number", "factryarea": "number",
    "otherarea": "number", "areasource": "number", "numbldgs": "number",
    "numfloors": "number", "unitsres": "number", "unitstotal": "number",
    "lotfront": "number", "lotdepth": "number", "bldgfront": "number",
    "bldgdepth": "number", "ext": "text", "proxcode": "number",
    "irrlotcode": "checkbox", "lottype": "number", "bsmtcode": "number",
    "assessland": "number", "assesstot": "number", "exempttot": "number",
    "yearbuilt": "number", "yearalter1": "number", "yearalter2": "number",
    "histdist": "text", "landmark": "text", "builtfar": "number",
    "residfar": "number", "commfar": "number", "facilfar": "number",
    "affresfar": "number", "mnffar": "number", "borocode": "number",
    "bbl": "number", "condono": "number", "tract2010": "number",
    "xcoord": "number", "ycoord": "number", "latitude": "number",
    "longitude": "number", "zonemap": "text", "zmcode": "checkbox",
    "sanborn": "text", "taxmap": "number", "edesignum": "text",
    "appbbl": "number", "appdate": "calendar_date", "plutomapid": "number",
    "version": "text", "sanitdistrict": "number",
    "healthcenterdistrict": "number", "firm07_flag": "number",
    "pfirm15_flag": "number", "dcpedited": "text", "notes": "text",
    "bct2020": "text", "bctcb2020": "text", "mih_opt1": "checkbox",
    "mih_opt2": "checkbox", "mih_opt3": "checkbox", "mih_opt4": "checkbox",
    "transitzone": "text", "geom": "text", "basempdate": "text",
    "dcasdate": "text", "edesigdate": "text", "landmkdate": "text",
    "masdate": "text", "polidate": "text", "rpaddate": "text",
    "zoningdate": "text",
}
PLUTO_COLUMNS: frozenset[str] = frozenset(PLUTO_COLUMN_TYPES)

# Units per the 26v1 data dictionary (research section 4.1; G1-verified pages
# cited there). Columns not listed are unitless/coded and get units=None.
_SQUARE_FEET = "square feet"
FIELD_UNITS: dict[str, str] = {
    # dictionary p.21/p.22: areas in square feet (BldgArea: condo values are
    # net not gross, and NOT ZR 12-10 zoning floor area - informational fact).
    "lotarea": _SQUARE_FEET, "bldgarea": _SQUARE_FEET, "comarea": _SQUARE_FEET,
    "resarea": _SQUARE_FEET, "officearea": _SQUARE_FEET,
    "retailarea": _SQUARE_FEET, "garagearea": _SQUARE_FEET,
    "strgearea": _SQUARE_FEET, "factryarea": _SQUARE_FEET,
    "otherarea": _SQUARE_FEET,
    # dictionary p.29: frontage/depth measured in feet.
    "lotfront": "feet", "lotdepth": "feet", "bldgfront": "feet",
    "bldgdepth": "feet",
    # dictionary p.33-34: DOF dollar values.
    "assessland": "US dollars", "assesstot": "US dollars",
    "exempttot": "US dollars",
    # dictionary p.39-40: NY-Long Island State Plane (EPSG:2263, US survey feet
    # confirmed on the official ArcGIS service side at G1).
    "xcoord": "US survey feet (NY-Long Island State Plane, EPSG:2263)",
    "ycoord": "US survey feet (NY-Long Island State Plane, EPSG:2263)",
    "latitude": "decimal degrees",
    "longitude": "decimal degrees",
}

# ---------------------------------------------------------------------------
# Canonical digests and fact identity (task M2-T004, owner P1 bullets 2-4).
# ---------------------------------------------------------------------------

# Verbatim canonicalization spec, recorded in every profile's
# reproducibility.digest_canonicalization so a historical report can recompute
# and verify its own digests (self-description pattern of coverage_policy).
CANONICALIZATION_SPEC = (
    "canonical-json-1: a digest is 'sha256:' + lowercase-hex SHA-256 of the "
    "UTF-8 encoding of the canonical JSON serialization of the PARSED value. "
    "Canonical serialization: object keys sorted lexicographically by Unicode "
    "code point; separators ',' and ':' with no insignificant whitespace; "
    "non-ASCII characters preserved as-is (not escaped); no Unicode "
    "normalization applied; numbers serialized by Python json.dumps defaults "
    "(integers verbatim, floats shortest-repr). response_digest covers the "
    "entire parsed HTTP response body; value_digest covers one field's "
    "verbatim original_value. Digesting parsed values makes semantically "
    "identical responses digest equal regardless of source key order or "
    "whitespace, while any value change flips the digest."
)


def canonical_json_digest(value: object) -> str:
    """Deterministic digest of a PARSED JSON value per CANONICALIZATION_SPEC.

    Sensitive to every value change; insensitive to source key order and
    insignificant whitespace (the value is re-serialized canonically before
    hashing). Raw SODA scalar values are strings/booleans, so float
    representation never varies in practice; parsed floats use json.dumps
    shortest-repr, which is deterministic within the platform.
    """
    canonical = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(canonical).hexdigest()}"


def build_fact_key(bbl: str, column: str) -> str:
    """STABLE identity of the logical fact (source, dataset, property, field).

    Survives re-observation and dataset-version changes by construction: it
    deliberately excludes dataset_version, retrieval time, and any event id.
    Distinct from provenance_id (stable only within one dataset version) and
    observation_id (unique per retrieval event).
    """
    return f"fact:{SOURCE_ID}:{DATASET_ID}:{bbl}:{column}"


def _build_observation_id(event_id: str, bbl: str, column: str) -> str:
    """IMMUTABLE identity of one observation of one fact: unique per retrieval
    event (event_id is minted fresh per fetch), never reused or reassigned.
    All facts of one fetch share the event segment, so an evidence viewer can
    group a retrieval's observations without a join table."""
    return f"obs:{event_id}:{bbl}:{column}"


# ---------------------------------------------------------------------------
# Error taxonomy
# ---------------------------------------------------------------------------

class PlutoConnectorError(Exception):
    """Base typed connector error. Payloads never contain stack traces,
    headers, or the app token."""

    error_type = "source_unavailable"

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
            "dataset_id": DATASET_ID,
            "detail": self.detail,
        }


class RateLimitedError(PlutoConnectorError):
    """HTTP 429 persisted through the bounded retry budget."""

    error_type = "rate_limited"


class SchemaDriftError(PlutoConnectorError):
    """Dataset contract changed (no-such-column 400, malformed version,
    unexpected body shape). Surfaced for alerting; never blindly retried."""

    error_type = "schema_drift"


class SourceTimeoutError(PlutoConnectorError):
    """Connect/read timeout persisted through the retry budget."""

    error_type = "timeout"


class SourceUnavailableError(PlutoConnectorError):
    """Network failure, 5xx persisted through retries, or an unexpected
    non-drift HTTP status."""

    error_type = "source_unavailable"


# ---------------------------------------------------------------------------
# Transport abstraction (injectable so all tests run offline)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TransportResponse:
    """Transport-level response.

    ``headers`` (task M1-T009, ADDITIVE with a default so every existing
    fixture transport keeps constructing ``TransportResponse(status, body)``
    unchanged): response headers with LOWERCASE keys - transports normalize
    on capture. Used only to surface the RFC 9110 ``Retry-After`` value of a
    429 into the typed error detail for the resilience layer; header values
    are never logged and never appear in payloads unsanitized.
    """

    status: int
    body: str
    headers: Mapping[str, str] = field(default_factory=dict)


class TransportTimeout(Exception):
    """Raised by a transport on connect/read timeout."""


class TransportFailure(Exception):
    """Raised by a transport when the network/DNS/TLS layer fails.
    The message must already be free of secrets."""


Transport = Callable[[str, dict[str, str], float], TransportResponse]


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """G5 F3: refuse ALL HTTP redirects. urllib's default redirect handler
    re-sends request headers - including X-App-Token - to the redirect
    target, so an open redirect on the pinned official host could exfiltrate
    the token cross-host. Returning None makes urlopen raise HTTPError(3xx),
    which the transport converts into a plain TransportResponse; the caller
    then classifies the 3xx as source_unavailable. The token never follows
    any redirect, same-host or cross-host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ARG002
        return None


# Module-level opener WITHOUT redirect following (G5 F3). build_opener
# replaces the default HTTPRedirectHandler with our subclass.
_OPENER = urllib.request.build_opener(_NoRedirectHandler)


def _lowercase_headers(message: object) -> dict[str, str]:
    """Task M1-T009: capture RESPONSE headers with lowercase keys for the
    TransportResponse headers contract. Response headers are server data
    (never the request's X-App-Token); they stay out of logs and payloads
    except the sanitized Retry-After detail."""
    if message is None:
        return {}
    try:
        items = message.items()  # type: ignore[attr-defined]
    except AttributeError:
        return {}
    return {str(name).lower(): str(value) for name, value in items}


def _bounded_read(stream: object) -> str:
    """G5 F1: read at most MAX_RESPONSE_BYTES; refuse oversize bodies with a
    typed transport failure instead of an unbounded read + json.loads."""
    data = stream.read(MAX_RESPONSE_BYTES + 1)  # type: ignore[attr-defined]
    if len(data) > MAX_RESPONSE_BYTES:
        raise TransportFailure(
            f"response body exceeded {MAX_RESPONSE_BYTES} bytes; refusing unbounded read"
        )
    return data.decode("utf-8", errors="replace")


def urllib_transport(url: str, headers: dict[str, str], timeout: float) -> TransportResponse:
    """Default stdlib transport (no third-party HTTP dependency; low-storage
    policy). Translates urllib failures into transport-level signals.
    Hardened per M1-T002 G5: bounded body read (F1) and no redirect
    following (F3)."""
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with _OPENER.open(request, timeout=timeout) as response:  # noqa: S310
            return TransportResponse(
                status=response.status,
                body=_bounded_read(response),
                # getattr: headers stay optional so response doubles without
                # a headers attribute (tests) keep working - headers are an
                # additive capture, never a required transport capability.
                headers=_lowercase_headers(getattr(response, "headers", None)),
            )
    except urllib.error.HTTPError as exc:
        # Includes refused 3xx redirects (F3): status passes through and the
        # caller maps it to a typed error; no request is ever re-issued.
        body = _bounded_read(exc)
        return TransportResponse(
            status=exc.code,
            body=body,
            headers=_lowercase_headers(getattr(exc, "headers", None)),
        )
    except TimeoutError as exc:  # socket.timeout is an alias since Python 3.10
        raise TransportTimeout(f"timeout after {timeout}s") from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise TransportTimeout(f"timeout after {timeout}s") from exc
        raise TransportFailure(f"network failure: {type(exc.reason).__name__}") from exc


# ---------------------------------------------------------------------------
# Result contract
# ---------------------------------------------------------------------------

@dataclass
class PlutoFetchResult:
    """Canonical fetch result. ``facts`` entries validate against
    source_fact.schema.json v1; ``no_match`` is a legitimate result status.

    ``response_digest`` (task M2-T004): canonical-json-1 digest of the ENTIRE
    parsed response body (also present for ``no_match``, where it digests the
    empty array - the snapshot that proved the absence is itself evidence).

    ``staleness`` (task M2-T006, ADDITIVE with a default so every existing
    construction stays unchanged): the contract-1.3.0 typed serve-freshness
    record. ``None`` on every fresh retrieval this connector performs (the
    builder then emits the fresh marker ``{served_from_cache: false, stale:
    false}``); the RESILIENCE layer (app.resilience.fetcher) sets it on
    cache-hit and last-known-good serves, copying values verbatim from its
    own serve record - never invented here. No field mapping, normalization,
    or provenance behavior of this connector changes.
    """

    status: str  # "ok" | "no_match"
    bbl: str
    correlation_id: str
    request_url: str
    retrieved_at: str
    dataset_version: str | None
    record_count: int
    facts: list[dict] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)
    drift_signals: list[str] = field(default_factory=list)
    absent_columns: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    no_match_explanation: str | None = None
    response_digest: str | None = None
    staleness: dict | None = None


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _utc_now() -> datetime:
    return datetime.now(UTC)


def _rfc3339(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_headers(app_token: str | None) -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if app_token:
        # Optional per the official app-token model (E7); never logged and
        # never included in error payloads.
        headers["X-App-Token"] = app_token
    return headers


def _classify_400(body: str) -> str | None:
    """Return the Socrata errorCode of a 400 body when parseable, else None.

    G5 F2: hostile deeply nested JSON makes json.loads raise RecursionError;
    that must classify as unparseable (None), never escape as a raw stack.
    """
    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, ValueError, RecursionError):
        return None
    if isinstance(parsed, dict):
        code = parsed.get("errorCode")
        if isinstance(code, str):
            return code
    return None


def _sanitize_retry_after(raw: str) -> str:
    """Task M1-T009: pass through RFC 9110-shaped Retry-After values
    verbatim; repr()-sanitize anything else (untrusted header data)."""
    if _RETRY_AFTER_SAFE_RE.match(raw):
        return raw
    return repr(raw)


def _get_retry_after(headers: Mapping[str, str]) -> str | None:
    """Case-insensitive Retry-After lookup (transports normalize to
    lowercase keys; this stays defensive for injected test transports)."""
    for name, value in headers.items():
        if name.lower() == "retry-after" and isinstance(value, str):
            return value
    return None


def _sanitize_error_code(code: str | None) -> str | None:
    """G5 F4: errorCode is untrusted response data. Official codes match the
    dotted-token allowlist and pass through verbatim; anything else (control
    characters, CRLF log-injection payloads, oversized strings) is
    repr()-sanitized, consistent with version_raw/record_bbl_raw handling."""
    if code is None:
        return None
    if _ERROR_CODE_SAFE_RE.match(code):
        return code
    return repr(code)


def _request_with_retry(
    url: str,
    *,
    transport: Transport,
    headers: dict[str, str],
    timeout: float,
    max_attempts: int,
    backoff_base: float,
    sleep: Callable[[float], None],
    correlation_id: str,
) -> TransportResponse:
    """Bounded retry on 429/5xx/timeout/network failure only. Schema drift
    and other 4xx are never retried."""
    last_kind: str | None = None
    last_detail: dict = {}
    for attempt in range(1, max_attempts + 1):
        try:
            response = transport(url, headers, timeout)
        except TransportTimeout:
            last_kind, last_detail = "timeout", {"attempts": attempt}
            logger.warning(
                "pluto_soda timeout url=%s attempt=%d correlation_id=%s",
                url, attempt, correlation_id,
            )
        except TransportFailure as exc:
            last_kind = "network"
            last_detail = {"attempts": attempt, "reason": str(exc)}
            logger.warning(
                "pluto_soda network failure url=%s attempt=%d correlation_id=%s",
                url, attempt, correlation_id,
            )
        else:
            if response.status == 200:
                return response
            if response.status == 429:
                last_kind, last_detail = "rate_limited", {"attempts": attempt}
                # Task M1-T009: surface the (sanitized) Retry-After value in
                # the typed-error detail so the resilience layer can honor it
                # exactly (RFC 9110 section 10.2.3). The official Socrata
                # docs specify only the 429 status (fixture F07), so the
                # header is OPTIONAL input, never a guessed guarantee.
                retry_after_raw = _get_retry_after(response.headers)
                if retry_after_raw is not None:
                    last_detail["retry_after"] = _sanitize_retry_after(retry_after_raw)
                logger.warning(
                    "pluto_soda throttled (429) url=%s attempt=%d correlation_id=%s",
                    url, attempt, correlation_id,
                )
            elif response.status == 400:
                error_code = _classify_400(response.body)
                safe_code = _sanitize_error_code(error_code)  # G5 F4
                if error_code == SCHEMA_DRIFT_ERROR_CODE:
                    raise SchemaDriftError(
                        "SODA rejected a column reference: schema drift signature "
                        f"({SCHEMA_DRIFT_ERROR_CODE})",
                        correlation_id=correlation_id,
                        detail={"http_status": 400, "error_code": safe_code, "url": url},
                    )
                raise SourceUnavailableError(
                    "SODA rejected the request (HTTP 400, not the schema-drift signature)",
                    correlation_id=correlation_id,
                    detail={"http_status": 400, "error_code": safe_code, "url": url},
                )
            elif 500 <= response.status < 600:
                last_kind = "server_error"
                last_detail = {"attempts": attempt, "http_status": response.status}
                logger.warning(
                    "pluto_soda server error %d url=%s attempt=%d correlation_id=%s",
                    response.status, url, attempt, correlation_id,
                )
            else:
                raise SourceUnavailableError(
                    f"unexpected HTTP status {response.status} from SODA endpoint",
                    correlation_id=correlation_id,
                    detail={"http_status": response.status, "url": url},
                )
        if attempt < max_attempts:
            sleep(backoff_base * (2 ** (attempt - 1)))

    detail = {**last_detail, "url": url, "max_attempts": max_attempts}
    if last_kind == "rate_limited":
        raise RateLimitedError(
            "SODA throttled the request (HTTP 429) and the retry budget is exhausted; "
            "configure SOCRATA_APP_TOKEN to leave the shared tokenless pool",
            correlation_id=correlation_id,
            detail=detail,
        )
    if last_kind == "timeout":
        raise SourceTimeoutError(
            "SODA request timed out and the retry budget is exhausted",
            correlation_id=correlation_id,
            detail=detail,
        )
    raise SourceUnavailableError(
        "SODA endpoint unavailable and the retry budget is exhausted",
        correlation_id=correlation_id,
        detail=detail,
    )


def _normalize_value(column: str, raw: object, drift_signals: list[str]) -> object:
    """Deterministic per-column normalization based on the official Socrata
    dataTypeName (fixture F08). Unparseable values are surfaced as drift
    signals and passed through verbatim - never guessed."""
    column_type = PLUTO_COLUMN_TYPES[column]
    if raw is None:
        return None
    if column_type == "checkbox":
        if isinstance(raw, bool):
            return raw
        drift_signals.append(f"unexpected_checkbox_value:{column}")
        return raw
    if column in ("bbl", "appbbl"):
        try:
            return normalize_bbl(raw).canonical
        except BBLValidationError:
            drift_signals.append(f"unparseable_bbl_value:{column}")
            return raw
    if column_type == "number":
        if isinstance(raw, bool):
            drift_signals.append(f"unexpected_number_value:{column}")
            return raw
        if isinstance(raw, int | float):
            number = float(raw)
        elif isinstance(raw, str):
            try:
                number = float(raw)
            except ValueError:
                drift_signals.append(f"unparseable_number_value:{column}")
                return raw
        else:
            drift_signals.append(f"unexpected_number_value:{column}")
            return raw
        if not math.isfinite(number):
            # G3 D2: "NaN"/"Infinity" strings parse via float() but are not
            # usable numeric facts (json.dumps would emit non-RFC-8259 output
            # that strict downstream parsers reject). Surface as drift and
            # preserve the verbatim raw value - never guessed.
            drift_signals.append(f"non_finite_number_value:{column}")
            return raw
        return int(number) if number.is_integer() else number
    if column_type == "calendar_date":
        if isinstance(raw, str) and re.match(r"^\d{4}-\d{2}-\d{2}", raw):
            return raw[:10]
        drift_signals.append(f"unparseable_calendar_date:{column}")
        return raw
    # text: identity, verbatim.
    return raw


def _condo_explanation(lot: int) -> str | None:
    low, high = CONDO_UNIT_LOT_RANGE
    if low <= lot <= high:
        return (
            f"Lot {lot} is in the condominium unit-lot range {low}-{high}. PLUTO carries "
            "one record per condominium complex under the BILLING lot "
            f"({CONDO_BILLING_LOT_RANGE[0]}-{CONDO_BILLING_LOT_RANGE[1]}, or the lowest "
            "lot in the block when unassigned); resolve the billing BBL (e.g. Geoclient "
            "condominiumBillingBbl) and retry (PLUTO README 26v1; research section 4.4)."
        )
    return None


def _parse_positive_number(raw: object) -> float | None:
    try:
        value = float(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return value


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_by_bbl(
    bbl: object,
    *,
    transport: Transport = urllib_transport,
    timeout: float = 10.0,
    max_attempts: int = 3,
    backoff_base: float = 0.5,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = _utc_now,
    correlation_id: str | None = None,
    app_token: str | None = None,
    observation_event_id: str | None = None,
) -> PlutoFetchResult:
    """Fetch the PLUTO record for one BBL and emit canonical source facts.

    Args (M2-T004 addition):
        observation_event_id: identity of THIS retrieval event, minted fresh
            (uuid4) when not injected. Deliberately separate from
            correlation_id: a caller-supplied correlation id may legitimately
            span several fetches (e.g. a future batch endpoint), while the
            event id is unique per fetch so every ``observation_id`` stays
            immutable and never collides. Injectable for deterministic tests.

    Raises:
        BBLValidationError: malformed BBL input; NO network call is made.
        RateLimitedError / SchemaDriftError / SourceTimeoutError /
        SourceUnavailableError: typed failures; NO partial facts are emitted.

    Returns:
        PlutoFetchResult with status "ok" (facts populated) or "no_match"
        (empty official response - a legitimate result, e.g. condo unit lots).
    """
    correlation_id = correlation_id or uuid.uuid4().hex
    observation_event_id = observation_event_id or uuid.uuid4().hex
    normalized = normalize_bbl(bbl)  # validation_error before any network I/O
    if app_token is None:
        app_token = os.environ.get(APP_TOKEN_ENV_VAR) or None

    url = f"{BASE_URL}?bbl={normalized.canonical}"
    logger.info(
        "pluto_soda fetch_by_bbl bbl=%s url=%s correlation_id=%s token_configured=%s",
        normalized.canonical, url, correlation_id, bool(app_token),
    )

    response = _request_with_retry(
        url,
        transport=transport,
        headers=_build_headers(app_token),
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        sleep=sleep,
        correlation_id=correlation_id,
    )
    # G3 D3: stamp retrieved_at AFTER the successful response so the
    # provenance timestamp reflects the actual retrieval moment (a
    # pre-request stamp could precede retrieval by ~30s across retries).
    retrieved_at = _rfc3339(clock())

    try:
        records = json.loads(response.body)
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        # G5 F2: RecursionError (hostile deeply nested JSON) must surface as
        # the same typed error as any other unparseable body - never a raw
        # stack escaping the typed-error contract.
        raise SourceUnavailableError(
            "SODA returned HTTP 200 with a body that is not valid JSON",
            correlation_id=correlation_id,
            detail={"url": url, "parse_error": type(exc).__name__},
        ) from exc
    if not isinstance(records, list):
        raise SchemaDriftError(
            "SODA resource endpoint no longer returns a JSON array",
            correlation_id=correlation_id,
            detail={"url": url, "body_type": type(records).__name__},
        )

    # M2-T004: canonical digest of the ENTIRE parsed response body, computed
    # BEFORE any normalization touches derived copies (the parsed object is
    # never mutated). Deterministic across byte-different but semantically
    # identical responses; flipped by any value change.
    response_digest = canonical_json_digest(records)

    if len(records) == 0:
        explanation = _condo_explanation(normalized.lot) or (
            f"No PLUTO record exists for BBL {normalized.canonical} in dataset "
            f"{DATASET_ID}. The BBL is syntactically valid but matches no tax lot "
            "in the current PLUTO release (or the lot is represented under a "
            "different BBL, e.g. after merger - see appbbl semantics)."
        )
        logger.info(
            "pluto_soda no_match bbl=%s correlation_id=%s",
            normalized.canonical, correlation_id,
        )
        return PlutoFetchResult(
            status="no_match",
            bbl=normalized.canonical,
            correlation_id=correlation_id,
            request_url=url,
            retrieved_at=retrieved_at,
            dataset_version=None,
            record_count=0,
            no_match_explanation=explanation,
            response_digest=response_digest,
        )

    if len(records) > 1:
        raise SchemaDriftError(
            f"SODA returned {len(records)} records for a single BBL; PLUTO carries "
            "one record per tax lot / condo complex, so uniqueness is part of the "
            "dataset contract",
            correlation_id=correlation_id,
            detail={"url": url, "record_count": len(records)},
        )

    record = records[0]
    if not isinstance(record, dict):
        raise SchemaDriftError(
            "SODA record is not a JSON object",
            correlation_id=correlation_id,
            detail={"url": url, "record_type": type(record).__name__},
        )

    drift_signals: list[str] = []
    record_keys = set(record)
    unknown_columns = sorted(record_keys - PLUTO_COLUMNS)
    for column in unknown_columns:
        # Never infer schema from record keys: unknown columns yield NO facts,
        # only an alerting signal (additive drift is visible, not fatal).
        drift_signals.append(f"unknown_column:{column}")

    version_raw = record.get("version")
    if not isinstance(version_raw, str) or not VERSION_RE.match(version_raw):
        raise SchemaDriftError(
            "PLUTO version field missing or malformed on the returned record; "
            "provenance cannot be recorded without a valid release version",
            correlation_id=correlation_id,
            detail={"url": url, "version_raw": repr(version_raw)},
        )

    record_bbl: str | None = None
    if "bbl" in record:
        try:
            record_bbl = normalize_bbl(record["bbl"]).canonical
        except BBLValidationError as exc:
            # G3 D1: an unparseable record-level bbl is SOURCE-SHAPE drift.
            # validation_error is reserved for caller input rejected BEFORE
            # any network call; corrupted/drifted source data must surface on
            # the schema-drift signal path instead.
            raise SchemaDriftError(
                "record-level bbl value cannot be parsed as a canonical BBL; "
                "classifying as schema drift (source record shape), not a "
                "caller validation error",
                correlation_id=correlation_id,
                detail={
                    "url": url,
                    "record_bbl_raw": repr(record["bbl"]),
                    "validation_code": exc.code,
                },
            ) from exc
    if record_bbl != normalized.canonical:
        raise SchemaDriftError(
            "record BBL does not match the exact-match query BBL",
            correlation_id=correlation_id,
            detail={
                "url": url,
                "requested_bbl": normalized.canonical,
                "record_bbl": record_bbl,
            },
        )

    conflicts = check_identifier_consistency(
        normalized.canonical,
        borocode=record.get("borocode"),
        block=record.get("block"),
        lot=record.get("lot"),
    )
    conflict_fields = {"bbl"} | {c["field"] for c in conflicts} if conflicts else set()

    vintages = {
        column: record[column] for column in VINTAGE_DATE_COLUMNS if column in record
    }

    notes: list[str] = []
    numbldgs = _parse_positive_number(record.get("numbldgs"))
    if "numfloors" not in record and numbldgs is not None and numbldgs > 0:
        # Dictionary p.28: NumFloors null with NumBldgs > 0 = "not available".
        notes.append(
            "numfloors_not_available: NumFloors is null while NumBldgs > 0; per the "
            "26v1 data dictionary p.28 the number of floors is NOT AVAILABLE for "
            "this tax lot (unknown, never zero, never fabricated)."
        )
    if "yearbuilt" not in record or _parse_positive_number(record.get("yearbuilt")) == 0:
        # G1 C1 (mirrors the numfloors pattern): dictionary p.34-35 - a
        # YearBuilt of 0 (or null) means the year built is UNKNOWN. Never
        # assert 0 as a confident construction year.
        notes.append(
            "yearbuilt_unknown: YearBuilt is 0 or absent; per the 26v1 data "
            "dictionary p.34-35 a 0/null YearBuilt means the year built is "
            "UNKNOWN for this tax lot (never the year 0, never fabricated)."
        )

    facts: list[dict] = []
    for column in sorted(record_keys & PLUTO_COLUMNS):
        raw_value = record[column]
        normalized_value = _normalize_value(column, raw_value, drift_signals)
        if (
            column == "yearbuilt"
            and not isinstance(normalized_value, bool)
            and normalized_value == 0
        ):
            # G1 C1: dictionary p.34-35 - YearBuilt 0 means UNKNOWN. The raw
            # "0" stays verbatim in original_value; the normalized value is
            # explicitly None (unknown), paired with the yearbuilt_unknown
            # note above - never a confident year 0.
            normalized_value = None
        fact = {
            # Deterministic key: same dataset version + BBL + field => same id
            # (idempotency, scenario S6).
            "provenance_id": f"pluto-{DATASET_ID}-{version_raw}-{normalized.canonical}-{column}",
            "source_id": SOURCE_ID,
            "original_field_name": column,
            "original_value": raw_value,
            "normalized_value": normalized_value,
            "units": FIELD_UNITS.get(column),
            "retrieved_at": retrieved_at,
            "dataset_version": version_raw,
            # Per-fact effective dates are NOT published per column; the
            # per-input vintage dates below are the official effective-date
            # bounds (README 26v1 DATES OF DATA). No field->input mapping is
            # published, so effective_date stays explicitly null (never guessed).
            "effective_date": None,
            "bbl": normalized.canonical,
            "confidence": 1.0,
            "user_confirmed_or_overridden": "none",
            "conflict_status": "conflicting" if column in conflict_fields else "none",
            # Additive provenance extensions (source_fact v1 permits additional
            # keys; the required v1 field set above is complete and unchanged).
            "dataset_id": DATASET_ID,
            "request_url": url,
            "input_vintages": vintages,
            # M2-T004 fact identity + snapshot lineage (source_fact contract
            # optional keys, emitted unconditionally by this connector):
            # fact_key is STABLE across re-observations AND dataset versions;
            # observation_id is IMMUTABLE and unique per retrieval event; the
            # digests pin this observation to exact content. Lineage chain:
            # observation_id -> dataset_version (source version) ->
            # request_url + retrieved_at (request) -> response_digest (body).
            "fact_key": build_fact_key(normalized.canonical, column),
            "observation_id": _build_observation_id(
                observation_event_id, normalized.canonical, column
            ),
            "value_digest": canonical_json_digest(raw_value),
            "response_digest": response_digest,
        }
        facts.append(fact)

    absent_columns = sorted(PLUTO_COLUMNS - record_keys)
    logger.info(
        "pluto_soda ok bbl=%s version=%s facts=%d conflicts=%d drift_signals=%d "
        "correlation_id=%s",
        normalized.canonical, version_raw, len(facts), len(conflicts),
        len(drift_signals), correlation_id,
    )
    return PlutoFetchResult(
        status="ok",
        bbl=normalized.canonical,
        correlation_id=correlation_id,
        request_url=url,
        retrieved_at=retrieved_at,
        dataset_version=version_raw,
        record_count=1,
        facts=facts,
        conflicts=conflicts,
        drift_signals=drift_signals,
        absent_columns=absent_columns,
        notes=notes,
        response_digest=response_digest,
    )


def build_page_url(limit: int, offset: int) -> str:
    """Stable-ordered pagination URL ($order=bbl) for future bulk/scan use.

    Fixtures F06a/F06b prove ordering stability and no dupes/gaps across the
    page boundary. Citywide import remains the M2 bulk task (F11 out of scope).
    """
    if limit < 1 or offset < 0:
        raise ValueError("limit must be >= 1 and offset >= 0")
    return f"{BASE_URL}?$order=bbl&$limit={limit}&$offset={offset}"


def check_columns_for_drift(api_views_metadata: dict) -> dict:
    """Compare a live /api/views/64uk-42ks.json document against the embedded
    108-column contract snapshot (fixture F08). Returns added/removed/type-
    changed column names for the scheduled drift monitor."""
    columns = api_views_metadata.get("columns")
    if not isinstance(columns, list):
        return {"error": "metadata document has no columns array"}
    live = {
        column.get("fieldName"): column.get("dataTypeName")
        for column in columns
        if isinstance(column, dict)
    }
    added = sorted(set(live) - PLUTO_COLUMNS)
    removed = sorted(PLUTO_COLUMNS - set(live))
    type_changed = sorted(
        name for name in (set(live) & PLUTO_COLUMNS)
        if live[name] != PLUTO_COLUMN_TYPES[name]
    )
    return {"added": added, "removed": removed, "type_changed": type_changed}
