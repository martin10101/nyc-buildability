"""ZTLDB SODA connector - official NYC Zoning Tax Lot Database ``fdkv-4t4z``
(task M2-T008; research docs/research/zoning-features-ztldb-2026-07-16.md).

The ZTLDB is DCP's tax-lot-level zoning assignment table (DOF Digital Tax
Map lots x NYC GIS Zoning Features under the official 10%/50% assignment
rules), one row per tax lot, 16 columns, served on the NYC Open Data SODA
endpoint at ``data.cityofnewyork.us``.

Design commitments (packet safeguards 1-6):

1. SCHEMA AUTHORITY - the ``/api/views/fdkv-4t4z.json`` columns array is the
   authoritative 16-column inventory (``ZTLDB_COLUMN_TYPES``; fixture ZT08,
   retrieved 2026-07-20). Schema is NEVER inferred from record keys: SODA
   omits blank keys per record (verified live, research Z3). An omitted key
   follows the documented source semantics - blank means "not applicable /
   lot not split further" for the columns where the official dictionary
   documents it - and is never converted into a confirmed null, zero,
   false, or empty value. The four presence states are kept distinct:
   present value, observed explicit null, absent with documented
   not-applicable semantics, and absent without documented semantics.
2. QUERY SAFETY - the BBL is validated by :mod:`app.connectors.bbl` BEFORE
   any URL is built (typed ``BBLValidationError``, no network I/O); page
   parameters are bounds-checked integers; every URL is constructed here
   from the pinned official origin + dataset id; callers can never supply a
   URL, host, dataset id, or raw SoQL fragment. The optional Socrata
   application token comes from the environment (or an explicit argument),
   is sent as a request header only, and never appears in logs, payloads,
   fixtures, or errors.
3. PAGINATION - explicit ``$order=bbl`` + ``$limit``/``$offset`` with
   bounded page sizes and a mandatory page budget even though per-BBL
   results are small; the bounded scan detects duplicate pages, repeated
   records, zero-progress pages, and ordering violations as typed
   ``paging_pathology`` failures (never an infinite loop, never silent
   truncation or duplication). Full-dataset sync (857,951 rows) is OUT of
   scope by owner directive.
4. DOMAIN SEMANTICS - split-lot ordering (``zoning_district_1`` = greatest
   lot-area percentage since 2019-12-31 even if under 10 percent; 2/3/4
   descending) is PRESERVED and documented, never resorted; slash-joined
   special-district values parse into their Appendix A components with the
   official tie semantics retained; ``PARK`` carries the official
   do-not-use-for-open-space caveat; ``zoning_district_1`` is an OPEN value
   set (the official column description allows ZR section numbers for
   selected Queens properties - research G1 C4), so vocabulary checks are
   ADVISORY typed observations, never rejection or coercion. No value is
   ever invented from nearby lots and no conflicting value is ever chosen
   as the winner.
5. SOURCE FRESHNESS GUARD (owner two-staleness rule 2026-07-17) - the
   dataset has NO per-record version column; the only official freshness
   signal is ``rowsUpdatedAt`` on the api/views metadata.
   :func:`fetch_source_freshness` reports the dataset publication age
   against an injected clock as SOURCE freshness (``source_freshness``),
   which is provenance and NEVER sets ``served_from_cache`` or ``stale``.
   The ``staleness`` field describes TRANSPORT/cache serve state only and
   is stamped exclusively by :class:`ResilientZtldbFetcher` on cache-hit
   and last-known-good serves. A freshly downloaded old dataset is an old
   SOURCE dataset served fresh - both truths are carried simultaneously.
6. DETERMINISM - the raw byte digest, the canonical parsed-response digest,
   and the canonical normalized-record digest are kept SEPARATELY per
   ``ZT_CANONICALIZATION_SPEC``; normalization applies canonical ordering
   before digesting, so byte-order differences never change the normalized
   digest while any value change flips it.

Reuse (read-only, per packet): the hardened transport, transport signal
types, and canonical JSON digest come from the accepted
``app.connectors.pluto_soda``; BBL validation from ``app.connectors.bbl``;
resilience primitives from ``app.resilience`` (M1-T009). None of those
modules is modified.

Deterministic code only: no AI, no legal interpretation, no spatial
intersection, no legal zoning adjudication. Cross-source reconciliation
lives in ``app.profile.zoning_crosscheck`` and preserves every observation.
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import os
import re
import threading
import time
import uuid
from collections import OrderedDict
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from random import Random

from app.connectors.bbl import (
    BBLValidationError,
    check_identifier_consistency,
    normalize_bbl,
)

# Reused hardened transport + canonical JSON digest from the accepted
# M1-T002 connector (bounded body read, refused redirects, typed transport
# signals). Read-only reuse: pluto_soda.py itself is NOT modified.
from app.connectors.pluto_soda import canonical_json_digest
from app.resilience.breaker import CircuitBreaker
from app.resilience.budget import AnalysisBudget
from app.resilience.cache import TTLCache
from app.resilience.config import ResilienceConfig
from app.resilience.metrics import ResilienceMetrics

# Task M2-T011: hardened transport and the bounded retry engine now come
# from the shared app.resilience.transport module (moved verbatim from the
# accepted M1-T002 implementation this connector previously reused via
# pluto_soda). Connector semantics - SODA 400 classification, error
# taxonomy, messages - stay HERE and reach the engine through
# standard_retry_hooks.
from app.resilience.transport import (
    Transport,
    TransportResponse,
    jittered_retry_after_delay,
    request_with_retry,
    standard_retry_hooks,
    urllib_transport,
)

__all__ = [
    "API_VIEWS_URL",
    "APPENDIX_C_OVERLAYS",
    "APPENDIX_D_LIMITED_HEIGHT",
    "BASE_URL",
    "DATASET_ID",
    "HARD_MAX_PAGES",
    "MAX_PAGE_LIMIT",
    "NOT_APPLICABLE_WHEN_ABSENT",
    "ORDERED_DISTRICT_COLUMNS",
    "OVERLAY_COLUMNS",
    "PARK_CAVEAT",
    "RECORD_QUERY_LIMIT",
    "SOURCE_ID",
    "SOURCE_STALENESS_THRESHOLD_DAYS",
    "SPECIAL_DISTRICT_COLUMNS",
    "ZTLDB_COLUMNS",
    "ZTLDB_COLUMN_TYPES",
    "ZT_CANONICALIZATION_SPEC",
    "CircuitOpenError",
    "DisallowedRequestError",
    "MalformedResponseError",
    "PagingPathologyError",
    "RateLimitedError",
    "RequestBudgetExceededError",
    "ResilientZtldbFetcher",
    "SchemaDriftError",
    "SourceFreshness",
    "SourceTimeoutError",
    "UpstreamError",
    "ZtldbConnectorError",
    "ZtldbFetchResult",
    "ZtldbScanResult",
    "build_fact_key",
    "build_page_url",
    "build_record_url",
    "check_columns_for_drift",
    "fetch_by_bbl",
    "fetch_source_freshness",
    "raw_body_digest",
    "scan_rows",
]

logger = logging.getLogger("app.connectors.ztldb_soda")

SOURCE_ID = "nyc-dcp-ztldb-soda"  # docs/research/source-registry-drafts/ztldb.json
DATASET_ID = "fdkv-4t4z"
BASE_URL = f"https://data.cityofnewyork.us/resource/{DATASET_ID}.json"
API_VIEWS_URL = f"https://data.cityofnewyork.us/api/views/{DATASET_ID}.json"
APP_TOKEN_ENV_VAR = "SOCRATA_APP_TOKEN"

# Schema-drift failure signature (Socrata platform behavior verified at
# M1-T001 G1 and re-verified live for THIS dataset: fixture ZT10 records the
# actual HTTP 400 + errorCode for a nonexistent column reference).
SCHEMA_DRIFT_ERROR_CODE = "query.soql.no-such-column"

# ---------------------------------------------------------------------------
# Authoritative 16-column inventory with official Socrata dataTypeName per
# column. Source: /api/views/fdkv-4t4z.json columns array, retrieved
# 2026-07-20 (fixture ZT08_api_views_metadata.json - the test suite
# cross-checks this constant against that fixture, so transcription drift
# fails the build). NEVER infer schema from record keys (SODA omits blank
# fields per record - verified live, fixture ZT01).
# ---------------------------------------------------------------------------
ZTLDB_COLUMN_TYPES: dict[str, str] = {
    "borough_code": "number",
    "tax_block": "number",
    "tax_lot": "number",
    "bbl": "number",
    "zoning_district_1": "text",
    "zoning_district_2": "text",
    "zoning_district_3": "text",
    "zoning_district_4": "text",
    "commercial_overlay_1": "text",
    "commercial_overlay_2": "text",
    "special_district_1": "text",
    "special_district_2": "text",
    "special_district_3": "text",
    "limited_height_district": "text",
    "zoning_map_number": "text",
    "zoning_map_code": "text",
}
ZTLDB_COLUMNS: frozenset[str] = frozenset(ZTLDB_COLUMN_TYPES)

_NUMBER_COLUMNS: frozenset[str] = frozenset(
    {"borough_code", "tax_block", "tax_lot", "bbl"}
)

ORDERED_DISTRICT_COLUMNS: tuple[str, ...] = (
    "zoning_district_1", "zoning_district_2",
    "zoning_district_3", "zoning_district_4",
)
OVERLAY_COLUMNS: tuple[str, ...] = ("commercial_overlay_1", "commercial_overlay_2")
SPECIAL_DISTRICT_COLUMNS: tuple[str, ...] = (
    "special_district_1", "special_district_2", "special_district_3",
)

# Columns whose ABSENCE has documented official semantics (ZTLDB data
# dictionary, direct read, research section 4.1): blank zoning_district_2..4
# = "the tax lot is not divided by a zoning boundary line" (not split
# further); blank overlay/special/limited-height = no such feature assigned
# to the lot under the official 10%/50% assignment rules. Absence of any
# OTHER column carries NO documented semantics and is classified
# absent_undocumented - unknown, never fabricated. zoning_district_1 CAN be
# absent live (observed 2026-07-20, e.g. BBL 1000010201 in fixture ZT07b)
# even after the 2019-12-31 always-assign change - surfaced as a typed
# observation, never guessed.
NOT_APPLICABLE_WHEN_ABSENT: frozenset[str] = frozenset(
    {
        "zoning_district_2", "zoning_district_3", "zoning_district_4",
        "commercial_overlay_1", "commercial_overlay_2",
        "special_district_1", "special_district_2", "special_district_3",
        "limited_height_district",
    }
)

_ABSENCE_SEMANTICS: dict[str, str] = {
    "zoning_district_2": (
        "blank = the tax lot is not divided by a zoning boundary line "
        "(official ZTLDB dictionary, field definition)"
    ),
    "zoning_district_3": (
        "blank = the tax lot is not split three ways (official ZTLDB "
        "dictionary, field definition)"
    ),
    "zoning_district_4": (
        "blank = the tax lot is not split four ways (official ZTLDB "
        "dictionary, field definition)"
    ),
    "commercial_overlay_1": (
        "blank = no commercial overlay assigned under the official 10%/50% "
        "assignment rules (ZTLDB dictionary OVERVIEW)"
    ),
    "commercial_overlay_2": (
        "blank = no second commercial overlay assigned (ZTLDB dictionary)"
    ),
    "special_district_1": (
        "blank = no special purpose district assigned at the 10% threshold "
        "(ZTLDB dictionary OVERVIEW)"
    ),
    "special_district_2": "blank = no second special purpose district assigned",
    "special_district_3": "blank = no third special purpose district assigned",
    "limited_height_district": (
        "blank = the lot is not within a limited height district at the 10% "
        "threshold (ZTLDB dictionary OVERVIEW)"
    ),
}

# Advisory value sets (validation is ADVISORY - a typed observation, never
# rejection, coercion, or value invention):
# Appendix C (official dictionary, verbatim value list): C1-1..C1-5,
# C2-1..C2-5.
APPENDIX_C_OVERLAYS: frozenset[str] = frozenset(
    {f"C1-{i}" for i in range(1, 6)} | {f"C2-{i}" for i in range(1, 6)}
)
# Appendix D (official dictionary): LH-1, LH-1A (Upper East Side), LH-2 and
# LH-3 defined but currently unused.
APPENDIX_D_LIMITED_HEIGHT: frozenset[str] = frozenset(
    {"LH-1", "LH-1A", "LH-2", "LH-3"}
)
# Appendix-B SHAPE advisory check for zoning-district values: residential
# (R...), commercial (C...), manufacturing (M..., incl. mixed M/R), BPC,
# PARK. The set is OPEN for zoning_district_1 (ZR section numbers may occur
# per the official Socrata column description - research G1 C4), so a
# non-matching value is an observation only. The live vocabulary probe
# (2026-07-20, bounded group-by: 203 distinct values) matched this shape
# fully.
_APPENDIX_B_SHAPE_RE = re.compile(r"^[RCM][0-9]")
_APPENDIX_B_NAMED: frozenset[str] = frozenset({"PARK", "BPC"})

# Official PARK caveat (ZTLDB dictionary change history, verbatim):
PARK_CAVEAT = (
    "The NYC GIS Zoning Features do not constitute a definitive list of "
    "parks in the city. Lots designated as PARK should not be used to "
    "calculate the amount of open space in an area"
)

_SPLIT_LOT_ORDERING_SEMANTICS = (
    "zoning_district_1 holds the zoning district occupying the GREATEST "
    "percentage of the tax lot's area (since the 2019-12-31 release, even "
    "if the percentage is under 10%); zoning_district_2/3/4 hold the "
    "second/third/fourth greatest. The official column order IS the "
    "ordering semantics and is preserved verbatim - never resorted "
    "(ZTLDB data dictionary, research section 4.1)."
)
_OVERLAY_ORDERING_SEMANTICS = (
    "commercial_overlay_1 = greatest percentage of the lot's area, "
    "commercial_overlay_2 = second greatest (ZTLDB data dictionary); "
    "official order preserved verbatim."
)
_SPECIAL_DISTRICT_TIE_SEMANTICS = (
    "If the greatest percentage is occupied by two special purpose "
    "districts that overlap each other and cover the same percentage of "
    "the lot, the field contains the abbreviation for both special purpose "
    "districts, with the abbreviations separated by '/' (ZTLDB data "
    "dictionary, verbatim rule). Both components are preserved; neither is "
    "chosen as the winner."
)
_ZONING_MAP_BORDER_SEMANTICS = (
    "A code 'Y' indicates that the tax lot may be on the border of two or "
    "more Zoning Maps; zoning_map_number is then one of the potential "
    "zoning maps associated with the tax lot (ZTLDB data dictionary, "
    "verbatim)."
)

# Freshness threshold: the stated cadence is Monthly (dataset description +
# custom fields, research Z2); the accepted registry draft sets the alert at
# age > ~45 days (one missed monthly cycle plus slack). Observed live stall:
# rowsUpdatedAt 2026-04-05 on both 2026-07-16 (research 5.1) and 2026-07-20
# (fixture ZT08) - ~3.5 months.
SOURCE_STALENESS_THRESHOLD_DAYS = 45.0

# Bounded query parameters (safeguards 2-3).
RECORD_QUERY_LIMIT = 10  # per-BBL bound; >1 record for one BBL is drift
MAX_PAGE_LIMIT = 1000
MAX_PAGE_OFFSET = 1_000_000
HARD_MAX_PAGES = 50  # absolute scan ceiling; full-dataset sync is out of scope

# G5-style shape allowlists for untrusted strings embedded in signals or
# error payloads (same repr()-sanitize policy as the accepted connectors).
_ERROR_CODE_SAFE_RE = re.compile(r"^[A-Za-z0-9._-]{1,120}$")
# Retry-After sanitization moved to app.resilience.transport (M2-T011),
# allowlist and repr()-sanitize policy unchanged.
_SAFE_TEXT_RE = re.compile(r"^[A-Za-z0-9 .,:;'()\[\]/_%=+-]{1,120}$")
_COLUMN_NAME_SAFE_RE = re.compile(r"^[A-Za-z0-9_]{1,64}$")

# Verbatim digest spec, self-describing so a historical record can recompute
# and verify its own digests (same pattern as the accepted connectors).
ZT_CANONICALIZATION_SPEC = (
    "zt-canonical-json-1: raw_digest is 'sha256:' + lowercase-hex SHA-256 "
    "over the EXACT UTF-8 bytes of the HTTP response body string "
    "(byte-preserving, order-sensitive, no parsing). response_digest is "
    "'sha256:' + lowercase-hex SHA-256 of the UTF-8 canonical JSON "
    "serialization of the PARSED response body (object keys sorted "
    "lexicographically by Unicode code point; separators ',' and ':'; "
    "non-ASCII preserved; numbers per Python json.dumps defaults) - "
    "insensitive to source key order and whitespace, flipped by any value "
    "change. normalized_digest applies the same canonical serialization to "
    "the normalized record payload {'bbl', 'columns' (present column -> "
    "normalized value), 'absent_not_applicable' (sorted), "
    "'absent_undocumented' (sorted), 'observed_null' (sorted)} - canonical "
    "ordering is applied BEFORE digesting, so the digest is independent of "
    "upstream serialization order. Raw, response, and normalized digests "
    "are kept SEPARATELY."
)


# ---------------------------------------------------------------------------
# Error taxonomy (aligned with the accepted M2-T007 naming; each error_type
# distinct and test-asserted). ``no_record`` is a RESULT status, not an
# error: a well-formed empty array is legitimate official data.
# ---------------------------------------------------------------------------


class ZtldbConnectorError(Exception):
    """Base typed connector error. Payloads never contain stack traces,
    headers, or the app token."""

    error_type = "upstream_error"

    def __init__(
        self, message: str, *, correlation_id: str, detail: dict | None = None
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
            "dataset_id": DATASET_ID,
            "detail": self.detail,
        }


class UpstreamError(ZtldbConnectorError):
    """Upstream failure: network failure, 5xx persisted through retries,
    unexpected HTTP status, or a non-drift HTTP 400 (e.g. the
    query.soql.type-mismatch errorCode - fixture ZT100)."""

    error_type = "upstream_error"


class MalformedResponseError(ZtldbConnectorError):
    """Response body is not the well-formed documented shape (invalid JSON,
    non-array resource body, non-object record). NEVER converted into a
    valid empty result."""

    error_type = "malformed_response"


class SchemaDriftError(ZtldbConnectorError):
    """Dataset contract changed: no-such-column 400 signature, columns-array
    drift (removed/renamed/re-typed column), missing rowsUpdatedAt freshness
    signal, uniqueness violation (two rows for one BBL), or a record whose
    identity cannot be verified. Surfaced for alerting; never blindly
    retried, never guessed around."""

    error_type = "schema_drift"


class SourceTimeoutError(ZtldbConnectorError):
    """Connect/read timeout persisted through the retry budget."""

    error_type = "timeout"


class RateLimitedError(ZtldbConnectorError):
    """HTTP 429 persisted through the bounded retry budget."""

    error_type = "rate_limited"


class DisallowedRequestError(ZtldbConnectorError):
    """Request refused by the bounded-parameter allowlist BEFORE any network
    I/O (out-of-bounds page limit/offset, wrong types). Malformed BBL input
    raises the shared typed ``BBLValidationError`` instead (also before any
    network I/O)."""

    error_type = "disallowed_request"


class PagingPathologyError(ZtldbConnectorError):
    """Paged scan detected upstream misbehavior: ``detail.reason`` is one of
    ``duplicate_page``, ``repeated_record``, ``no_progress``,
    ``unordered_page``, ``page_overflow``, ``page_budget_exhausted``. Never
    an infinite loop, never silent truncation or duplication."""

    error_type = "paging_pathology"


class RequestBudgetExceededError(ZtldbConnectorError):
    """Per-analysis upstream request budget exhausted (M1-T009
    ``AnalysisBudget``); raised BEFORE further upstream I/O and never masked
    by cache or last-known-good fallback."""

    error_type = "budget_exhausted"


class CircuitOpenError(ZtldbConnectorError):
    """Fast rejection while the per-source circuit is open; no upstream I/O
    was performed for this call."""

    error_type = "circuit_open"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _rfc3339(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def raw_body_digest(body: str) -> str:
    """Raw-response digest: exact UTF-8 bytes of the transported body
    (ZT_CANONICALIZATION_SPEC). Order-sensitive by design."""
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def _safe_text(value: object) -> str:
    """Untrusted upstream text passes through only when it matches the
    conservative allowlist; anything else is repr()-sanitized so hostile
    bytes never reach logs or payloads."""
    if isinstance(value, str) and _SAFE_TEXT_RE.match(value):
        return value
    return repr(value)


def _safe_column_name(value: object) -> str:
    if isinstance(value, str) and _COLUMN_NAME_SAFE_RE.match(value):
        return value
    return repr(value)


def _sanitize_error_code(code: str | None) -> str | None:
    if code is None:
        return None
    if _ERROR_CODE_SAFE_RE.match(code):
        return code
    return repr(code)


def _classify_400(body: str) -> str | None:
    """Return the Socrata errorCode of a 400 body when parseable, else
    None (hostile deeply nested JSON classifies as unparseable, never a raw
    RecursionError escaping the typed-error contract)."""
    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, ValueError, RecursionError):
        return None
    if isinstance(parsed, dict):
        code = parsed.get("errorCode")
        if isinstance(code, str):
            return code
    return None


def _build_headers(app_token: str | None) -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if app_token:
        # Optional per the official Socrata app-token model (M1-T001 E7);
        # header only, never logged, never in payloads or fixtures.
        headers["X-App-Token"] = app_token
    return headers


def build_fact_key(bbl: str, column: str) -> str:
    """STABLE identity of the logical fact (source, dataset, property,
    field); survives re-observation and dataset updates by construction."""
    return f"fact:{SOURCE_ID}:{DATASET_ID}:{bbl}:{column}"


def _build_observation_id(event_id: str, bbl: str, column: str) -> str:
    return f"obs:{event_id}:{bbl}:{column}"


# ---------------------------------------------------------------------------
# URL construction (all URLs originate here; the origin and dataset id are
# pinned constants; caller input reaches a URL only as the canonical BBL
# digits or bounds-checked integers)
# ---------------------------------------------------------------------------


def build_record_url(bbl: object) -> str:
    """Per-BBL record URL. Raises typed ``BBLValidationError`` for any
    malformed/injection-shaped input BEFORE construction; only the canonical
    10-digit form ever enters the query string. The query is bounded
    (explicit ``$order`` + ``$limit``) even though the one-row-per-tax-lot
    contract implies a single record."""
    canonical = normalize_bbl(bbl).canonical
    return (
        f"{BASE_URL}?bbl={canonical}"
        f"&%24order=bbl&%24limit={RECORD_QUERY_LIMIT}"
    )


def build_page_url(limit: int, offset: int, *, correlation_id: str = "urlbuild") -> str:
    """Deterministically ordered page URL with bounds-checked parameters."""
    if (
        isinstance(limit, bool)
        or not isinstance(limit, int)
        or not 1 <= limit <= MAX_PAGE_LIMIT
    ):
        raise DisallowedRequestError(
            f"page limit must be an integer in 1..{MAX_PAGE_LIMIT}",
            correlation_id=correlation_id,
            detail={"limit": repr(limit)},
        )
    if (
        isinstance(offset, bool)
        or not isinstance(offset, int)
        or not 0 <= offset <= MAX_PAGE_OFFSET
    ):
        raise DisallowedRequestError(
            f"page offset must be an integer in 0..{MAX_PAGE_OFFSET}",
            correlation_id=correlation_id,
            detail={"offset": repr(offset)},
        )
    return f"{BASE_URL}?%24order=bbl&%24limit={limit}&%24offset={offset}"


# ---------------------------------------------------------------------------
# Transport request with bounded retry (retry authority for the plain
# functions). Task M2-T011: the accepted control flow now runs in the shared
# engine (app.resilience.transport.request_with_retry) with the M1-T009
# jitter/Retry-After delay policy; the SODA-specific 400 classification,
# error taxonomy, and messages stay here through the RetryHooks seam.
# ---------------------------------------------------------------------------


def _request_with_retry(
    url: str,
    *,
    transport: Transport,
    headers: dict[str, str],
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
    """Bounded retry on 429/5xx/timeout/network failure ONLY. The
    no-such-column 400 raises typed ``schema_drift`` (never retried); other
    400s raise typed ``upstream_error``. One budget unit per upstream
    ATTEMPT, consumed BEFORE the I/O."""

    def _raise_for_unexpected_status(response: TransportResponse) -> None:
        if response.status == 400:
            error_code = _classify_400(response.body)
            safe_code = _sanitize_error_code(error_code)
            if error_code == SCHEMA_DRIFT_ERROR_CODE:
                raise SchemaDriftError(
                    "SODA rejected a column reference: schema drift "
                    f"signature ({SCHEMA_DRIFT_ERROR_CODE}) - drift "
                    "evidence, not data",
                    correlation_id=correlation_id,
                    detail={"http_status": 400, "error_code": safe_code, "url": url},
                )
            raise UpstreamError(
                "SODA rejected the request (HTTP 400, not the "
                "schema-drift signature)",
                correlation_id=correlation_id,
                detail={"http_status": 400, "error_code": safe_code, "url": url},
            )
        raise UpstreamError(
            f"unexpected HTTP status {response.status} from the "
            "official SODA endpoint",
            correlation_id=correlation_id,
            detail={"http_status": response.status, "url": url},
        )

    return request_with_retry(
        url,
        transport=transport,
        headers=headers,
        timeout=timeout,
        max_attempts=max_attempts,
        hooks=standard_retry_hooks(
            logger=logger,
            log_label="ztldb_soda",
            correlation_id=correlation_id,
            url=url,
            sanitize_network_reason=_safe_text,
            rate_limited_error=RateLimitedError,
            rate_limited_message=(
                "SODA throttled the request (HTTP 429) and the retry budget is "
                "exhausted; configure the optional Socrata application token to "
                "leave the shared anonymous pool"
            ),
            timeout_error=SourceTimeoutError,
            timeout_message="SODA request timed out and the retry budget is exhausted",
            unavailable_error=UpstreamError,
            unavailable_message=(
                "official SODA endpoint unavailable and the retry budget is exhausted"
            ),
            include_reason_kind=True,
            raise_for_unexpected_status=_raise_for_unexpected_status,
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
# Source freshness guard (safeguard 5) + columns-snapshot drift check
# ---------------------------------------------------------------------------


def check_columns_for_drift(api_views_metadata: dict) -> dict:
    """Compare a live /api/views/fdkv-4t4z.json document against the
    embedded 16-column contract snapshot (fixture ZT08). Returns
    added/removed/type-changed column names."""
    columns = api_views_metadata.get("columns")
    if not isinstance(columns, list):
        return {"error": "metadata document has no columns array"}
    # Only NAMED columns participate in the by-name comparison. A column dict
    # without a string ``fieldName`` cannot be identified and must not become a
    # ``None`` key: M2-T008 G3/G4 D1 - a None key mixed with real column names
    # made the sorted() differences below raise TypeError on doubly-malformed
    # metadata (a column that is a dict but lacks fieldName, alongside a real
    # added/removed column). Such a column is ignored here (it is not a valid,
    # comparable column definition); the by-name drift result is unaffected.
    live = {
        column["fieldName"]: column.get("dataTypeName")
        for column in columns
        if isinstance(column, dict) and isinstance(column.get("fieldName"), str)
    }
    added = sorted(set(live) - ZTLDB_COLUMNS)
    removed = sorted(ZTLDB_COLUMNS - set(live))
    type_changed = sorted(
        name for name in (set(live) & ZTLDB_COLUMNS)
        if live[name] != ZTLDB_COLUMN_TYPES[name]
    )
    return {"added": added, "removed": removed, "type_changed": type_changed}


@dataclass(frozen=True)
class SourceFreshness:
    """SOURCE-DATASET freshness record (owner two-staleness rule
    2026-07-17): describes how old the official dataset publication is,
    measured from ``rowsUpdatedAt`` against the injected clock at check
    time. This is PROVENANCE about the source. It NEVER sets
    ``served_from_cache`` or ``stale`` (those describe the transport/cache
    serve path and are stamped only by :class:`ResilientZtldbFetcher`), and
    a cache/LKG serve never alters these values."""

    request_url: str
    checked_at: str
    rows_updated_at_raw: int
    rows_updated_at: str
    age_days: float
    threshold_days: float
    source_stale_suspected: bool
    version_label: str
    raw_digest: str
    drift_signals: tuple[str, ...] = ()
    policy: str = (
        "source_freshness is SOURCE-dataset publication age (rowsUpdatedAt "
        "vs the check clock). It is independent of transport staleness: a "
        "fresh retrieval of an old dataset is an OLD SOURCE served fresh "
        "(source_stale_suspected may be true while staleness is a fresh "
        "marker), and a cache/LKG serve never changes these values (owner "
        "two-staleness rule 2026-07-17)."
    )

    def to_dict(self) -> dict:
        return asdict(self)


def fetch_source_freshness(
    *,
    transport: Transport = urllib_transport,
    timeout: float = 10.0,
    max_attempts: int = 3,
    backoff_base: float = 0.5,
    backoff_cap: float = 30.0,
    retry_after_cap: float = 120.0,
    rng: Random | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = _utc_now,
    correlation_id: str | None = None,
    app_token: str | None = None,
    budget: AnalysisBudget | None = None,
) -> SourceFreshness:
    """Fetch the dataset metadata and derive the SOURCE freshness record.

    Also validates the authoritative columns array against the 16-column
    contract snapshot: removed or re-typed columns raise typed
    ``schema_drift`` (never guessed around); ADDED columns degrade typed
    (visible drift signals). A missing/invalid ``rowsUpdatedAt`` is typed
    ``schema_drift``: the freshness guard signal may never be silently
    absent (ZTLDB has no other version signal - research section 5.3).
    """
    correlation_id = correlation_id or uuid.uuid4().hex
    if app_token is None:
        app_token = os.environ.get(APP_TOKEN_ENV_VAR) or None
    url = API_VIEWS_URL
    response = _request_with_retry(
        url,
        transport=transport,
        headers=_build_headers(app_token),
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
    checked_at_moment = clock()
    try:
        doc = json.loads(response.body)
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise MalformedResponseError(
            "api/views metadata is not valid JSON",
            correlation_id=correlation_id,
            detail={"url": url, "parse_error": type(exc).__name__},
        ) from exc
    if not isinstance(doc, dict):
        raise MalformedResponseError(
            "api/views metadata is not a JSON object",
            correlation_id=correlation_id,
            detail={"url": url, "body_type": type(doc).__name__},
        )

    diff = check_columns_for_drift(doc)
    if "error" in diff:
        raise SchemaDriftError(
            "api/views metadata has no columns array; the authoritative "
            "schema inventory is unavailable - refusing to infer schema "
            "from record keys",
            correlation_id=correlation_id,
            detail={"url": url},
        )
    if diff["removed"] or diff["type_changed"]:
        raise SchemaDriftError(
            "authoritative columns array drifted from the 16-column "
            "contract (removed/renamed/re-typed) - never silently guessed",
            correlation_id=correlation_id,
            detail={"url": url, **diff},
        )
    drift_signals = tuple(
        f"added_column:{_safe_column_name(name)}" for name in diff["added"]
    )

    rows_updated_raw = doc.get("rowsUpdatedAt")
    if isinstance(rows_updated_raw, bool) or not isinstance(rows_updated_raw, int):
        raise SchemaDriftError(
            "rowsUpdatedAt missing or invalid on the dataset metadata; the "
            "ONLY official freshness signal for this dataset is "
            "unavailable - the freshness guard cannot be silently skipped",
            correlation_id=correlation_id,
            detail={"url": url, "rows_updated_at": repr(rows_updated_raw)},
        )
    try:
        rows_updated_moment = datetime.fromtimestamp(rows_updated_raw, UTC)
    except (OverflowError, OSError, ValueError) as exc:
        raise SchemaDriftError(
            "rowsUpdatedAt is not a usable epoch timestamp",
            correlation_id=correlation_id,
            detail={"url": url, "rows_updated_at": repr(rows_updated_raw)},
        ) from exc
    rows_updated_at = _rfc3339(rows_updated_moment)
    age_days = round(
        (checked_at_moment - rows_updated_moment).total_seconds() / 86400.0, 2
    )
    stale_suspected = age_days > SOURCE_STALENESS_THRESHOLD_DAYS
    if stale_suspected:
        logger.warning(
            "ztldb_soda source freshness: dataset rows last updated %s "
            "(age %.1f days > %.0f-day threshold) correlation_id=%s",
            rows_updated_at, age_days, SOURCE_STALENESS_THRESHOLD_DAYS,
            correlation_id,
        )
    return SourceFreshness(
        request_url=url,
        checked_at=_rfc3339(checked_at_moment),
        rows_updated_at_raw=rows_updated_raw,
        rows_updated_at=rows_updated_at,
        age_days=age_days,
        threshold_days=SOURCE_STALENESS_THRESHOLD_DAYS,
        source_stale_suspected=stale_suspected,
        version_label=f"socrata-rows-{rows_updated_at}",
        raw_digest=raw_body_digest(response.body),
        drift_signals=drift_signals,
    )


# ---------------------------------------------------------------------------
# Result contracts
# ---------------------------------------------------------------------------


@dataclass
class ZtldbFetchResult:
    """Canonical per-BBL fetch result.

    ``status`` is ``ok`` or ``no_record`` (a RESULT: a well-formed empty
    array is legitimate official data - the lot has no ZTLDB row).

    Presence-state separation (safeguard 1): ``facts`` cover PRESENT keys
    (including observed explicit nulls, which also appear in
    ``observations`` as ``observed_null:<column>``); ``absences`` lists
    every absent column with its classification
    (``not_applicable_per_source_semantics`` with the documented dictionary
    semantics, or ``absent_undocumented`` = unknown, never fabricated).

    ``source_freshness`` is the SOURCE-dataset publication-age record;
    ``staleness`` is TRANSPORT/cache serve state only (None on every fresh
    retrieval; stamped exclusively by :class:`ResilientZtldbFetcher`).
    The two dimensions vary independently (owner two-staleness rule).
    """

    status: str  # "ok" | "no_record"
    bbl: str
    correlation_id: str
    request_url: str
    retrieved_at: str
    dataset_version: str
    record_count: int
    facts: list[dict] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)
    drift_signals: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    absences: list[dict] = field(default_factory=list)
    zoning_assignment: dict | None = None
    notes: list[str] = field(default_factory=list)
    no_record_explanation: str | None = None
    raw_digest: str | None = None
    response_digest: str | None = None
    normalized_digest: str | None = None
    digest_canonicalization: str = ZT_CANONICALIZATION_SPEC
    source_freshness: dict | None = None
    staleness: dict | None = None


@dataclass
class ZtldbScanResult:
    """Bounded deterministic multi-page scan result (NOT a full-dataset
    sync - that remains out of scope by owner directive)."""

    status: str  # always "ok" when the scan completes
    correlation_id: str
    page_request_urls: list[str]
    retrieved_at: str
    page_size: int
    page_count: int
    record_count: int
    bbls: list[str]
    records: list[dict]
    page_raw_digests: list[str]
    normalized_digest: str
    digest_canonicalization: str = ZT_CANONICALIZATION_SPEC
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Normalization internals
# ---------------------------------------------------------------------------


def _parse_source_integer(raw: object) -> int | None:
    """Deterministic integer parse for Socrata number-typed columns
    (serialized as JSON strings, possibly with an all-zero decimal tail -
    M1-T001 G1 finding C6). Returns None when unparseable."""
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float):
        return int(raw) if raw.is_integer() else None
    if isinstance(raw, str):
        text = raw.strip()
        if "." in text:
            integer_part, _, fractional = text.partition(".")
            if fractional.strip("0"):
                return None
            text = integer_part
        if text.isdigit():
            return int(text)
    return None


def _normalize_value(
    column: str,
    raw: object,
    drift_signals: list[str],
    observations: list[str],
) -> object:
    """Deterministic per-column normalization based on the official Socrata
    dataTypeName (fixture ZT08). Unparseable values surface as drift signals
    and pass through verbatim - never guessed. An explicit JSON null is the
    distinct OBSERVED-NULL state (never conflated with key omission)."""
    if raw is None:
        observations.append(f"observed_null:{column}")
        return None
    if column == "bbl":
        try:
            return normalize_bbl(raw).canonical
        except BBLValidationError:
            drift_signals.append(f"unparseable_bbl_value:{column}")
            return raw
    if column in _NUMBER_COLUMNS:
        parsed = _parse_source_integer(raw)
        if parsed is None:
            drift_signals.append(f"unparseable_number_value:{column}")
            return raw
        return parsed
    if not isinstance(raw, str):
        drift_signals.append(f"unexpected_text_value:{column}")
        return raw
    return raw  # text: identity, verbatim


def _advisory_vocabulary_observations(
    column: str, value: object, observations: list[str]
) -> None:
    """ADVISORY vocabulary checks (typed observations only - never
    rejection, coercion, or invention). zoning_district_* is an OPEN set
    (research G1 C4: ZR section numbers may occur for selected Queens
    properties); the Appendix C/D sets are the documented dictionary value
    lists. Special-district abbreviations get NO closed-set check: the full
    Appendix A inventory is not transcribed in the accepted research and is
    never guessed."""
    if not isinstance(value, str) or not value:
        return
    if column in ORDERED_DISTRICT_COLUMNS:
        if not _APPENDIX_B_SHAPE_RE.match(value) and value not in _APPENDIX_B_NAMED:
            observations.append(
                f"open_set_vocabulary:{column}:{_safe_text(value)}"
            )
    elif column in OVERLAY_COLUMNS:
        if value not in APPENDIX_C_OVERLAYS:
            observations.append(
                f"outside_documented_vocabulary:{column}:{_safe_text(value)}"
            )
    elif column == "limited_height_district":
        if value not in APPENDIX_D_LIMITED_HEIGHT:
            observations.append(
                f"outside_documented_vocabulary:{column}:{_safe_text(value)}"
            )
    elif column == "zoning_map_code" and value != "Y":
        observations.append(
            f"outside_documented_vocabulary:{column}:{_safe_text(value)}"
        )


def _build_zoning_assignment(
    normalized: Mapping[str, object], observations: list[str]
) -> dict:
    """Deterministic domain-semantics view of the normalized record
    (safeguard 4). Official ordering preserved verbatim; slash ties parsed
    with both components retained; PARK caveat flagged."""
    def _entries(columns: tuple[str, ...]) -> list[dict]:
        entries = []
        for position, column in enumerate(columns, start=1):
            value = normalized.get(column)
            if isinstance(value, str) and value:
                entries.append(
                    {"position": position, "column": column, "value": value}
                )
        return entries

    districts = _entries(ORDERED_DISTRICT_COLUMNS)
    overlays = _entries(OVERLAY_COLUMNS)

    special_districts = []
    for position, column in enumerate(SPECIAL_DISTRICT_COLUMNS, start=1):
        value = normalized.get(column)
        if not (isinstance(value, str) and value):
            continue
        components = value.split("/")
        tie = len(components) > 1
        entry: dict = {
            "position": position,
            "column": column,
            "value": value,  # verbatim, tie representation preserved
            "components": components,
            "tie": tie,
        }
        if tie:
            entry["tie_semantics"] = _SPECIAL_DISTRICT_TIE_SEMANTICS
            observations.append(
                f"special_district_tie:{column}:{_safe_text(value)}"
            )
        special_districts.append(entry)

    park_applies = any(entry["value"] == "PARK" for entry in districts)
    if park_applies:
        observations.append("park_caveat:do_not_use_for_open_space")

    limited_height = normalized.get("limited_height_district")
    map_number = normalized.get("zoning_map_number")
    map_code = normalized.get("zoning_map_code")

    return {
        "zoning_districts": districts,
        "ordering_semantics": _SPLIT_LOT_ORDERING_SEMANTICS,
        "commercial_overlays": overlays,
        "overlay_ordering_semantics": _OVERLAY_ORDERING_SEMANTICS,
        "special_districts": special_districts,
        "limited_height_district": limited_height
        if isinstance(limited_height, str)
        else None,
        "zoning_map": {
            "number": map_number if isinstance(map_number, str) else None,
            "border_code": map_code if isinstance(map_code, str) else None,
            "border_semantics": _ZONING_MAP_BORDER_SEMANTICS,
        },
        "park_caveat": {
            "applies": park_applies,
            "caveat": PARK_CAVEAT,
        },
    }


_IDENTIFIER_FIELD_MAP = {
    "borocode": "borough_code",
    "block": "tax_block",
    "lot": "tax_lot",
}


# ---------------------------------------------------------------------------
# Public per-BBL fetch
# ---------------------------------------------------------------------------


def fetch_by_bbl(
    bbl: object,
    *,
    freshness: SourceFreshness | None = None,
    transport: Transport = urllib_transport,
    timeout: float = 10.0,
    max_attempts: int = 3,
    backoff_base: float = 0.5,
    backoff_cap: float = 30.0,
    retry_after_cap: float = 120.0,
    rng: Random | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = _utc_now,
    correlation_id: str | None = None,
    app_token: str | None = None,
    observation_event_id: str | None = None,
    budget: AnalysisBudget | None = None,
) -> ZtldbFetchResult:
    """Fetch the ZTLDB row for one BBL and emit canonical source facts.

    When ``freshness`` is not injected, the dataset metadata is fetched
    (and validated) FIRST: it supplies the authoritative columns snapshot
    check, the ``rowsUpdatedAt`` source-freshness guard, and the
    ``dataset_version`` label (the dataset has no per-record version
    column, so the official rows-updated timestamp is the version signal -
    research section 5.3).

    Raises:
        BBLValidationError: malformed BBL input; NO network call is made.
        Typed connector errors otherwise; NO partial facts are emitted.

    Returns:
        ZtldbFetchResult with status ``ok`` or ``no_record``.
    """
    correlation_id = correlation_id or uuid.uuid4().hex
    observation_event_id = observation_event_id or uuid.uuid4().hex
    normalized_bbl = normalize_bbl(bbl)  # validation BEFORE any network I/O
    if app_token is None:
        app_token = os.environ.get(APP_TOKEN_ENV_VAR) or None
    rng = rng or Random()

    if freshness is None:
        freshness = fetch_source_freshness(
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
            app_token=app_token,
            budget=budget,
        )

    url = build_record_url(normalized_bbl.canonical)
    logger.info(
        "ztldb_soda fetch_by_bbl bbl=%s url=%s correlation_id=%s token_configured=%s",
        normalized_bbl.canonical, url, correlation_id, bool(app_token),
    )
    response = _request_with_retry(
        url,
        transport=transport,
        headers=_build_headers(app_token),
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
    # Stamp retrieved_at AFTER the successful response (provenance reflects
    # the actual retrieval moment - accepted M1-T002 G3 D3 pattern).
    retrieved_at = _rfc3339(clock())

    try:
        records = json.loads(response.body)
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise MalformedResponseError(
            "SODA returned HTTP 200 with a body that is not valid JSON; "
            "refusing to interpret it (never an empty result)",
            correlation_id=correlation_id,
            detail={"url": url, "parse_error": type(exc).__name__},
        ) from exc
    if not isinstance(records, list):
        raise MalformedResponseError(
            "SODA resource body is not the documented JSON array; a "
            "malformed response is NEVER a valid empty result",
            correlation_id=correlation_id,
            detail={"url": url, "body_type": type(records).__name__},
        )

    raw_digest = raw_body_digest(response.body)
    response_digest = canonical_json_digest(records)

    if len(records) == 0:
        explanation = (
            f"No ZTLDB row exists for BBL {normalized_bbl.canonical} in "
            f"dataset {DATASET_ID} (rows last updated "
            f"{freshness.rows_updated_at}). The BBL is syntactically valid "
            "but matches no tax lot in the current Socrata rows. This is a "
            "typed no-record RESULT from a well-formed empty response, "
            "never an error and never a fabricated record."
        )
        logger.info(
            "ztldb_soda no_record bbl=%s correlation_id=%s",
            normalized_bbl.canonical, correlation_id,
        )
        return ZtldbFetchResult(
            status="no_record",
            bbl=normalized_bbl.canonical,
            correlation_id=correlation_id,
            request_url=url,
            retrieved_at=retrieved_at,
            dataset_version=freshness.version_label,
            record_count=0,
            drift_signals=list(freshness.drift_signals),
            no_record_explanation=explanation,
            raw_digest=raw_digest,
            response_digest=response_digest,
            normalized_digest=canonical_json_digest(
                {"bbl": normalized_bbl.canonical, "no_record": True}
            ),
            source_freshness=freshness.to_dict(),
        )

    if len(records) > 1:
        raise SchemaDriftError(
            f"SODA returned {len(records)} records for a single BBL; the "
            "ZTLDB carries one row per tax lot (dictionary OVERVIEW), so "
            "uniqueness is part of the dataset contract - refusing to pick "
            "one record",
            correlation_id=correlation_id,
            detail={"url": url, "record_count": len(records)},
        )

    record = records[0]
    if not isinstance(record, dict):
        raise MalformedResponseError(
            "SODA record is not a JSON object",
            correlation_id=correlation_id,
            detail={"url": url, "record_type": type(record).__name__},
        )

    drift_signals: list[str] = list(freshness.drift_signals)
    observations: list[str] = []
    record_keys = set(record)
    for column in sorted(record_keys - ZTLDB_COLUMNS):
        # Never infer schema from record keys: unknown columns yield NO
        # facts, only an alerting signal (additive drift is visible).
        drift_signals.append(f"unknown_column:{_safe_column_name(column)}")

    if "bbl" not in record:
        raise SchemaDriftError(
            "record has no bbl value; the record's identity cannot be "
            "verified against the exact-match query",
            correlation_id=correlation_id,
            detail={"url": url},
        )
    try:
        record_bbl = normalize_bbl(record["bbl"]).canonical
    except BBLValidationError as exc:
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
    if record_bbl != normalized_bbl.canonical:
        raise SchemaDriftError(
            "record BBL does not match the exact-match query BBL",
            correlation_id=correlation_id,
            detail={
                "url": url,
                "requested_bbl": normalized_bbl.canonical,
                "record_bbl": record_bbl,
            },
        )

    raw_conflicts = check_identifier_consistency(
        normalized_bbl.canonical,
        borocode=record.get("borough_code"),
        block=record.get("tax_block"),
        lot=record.get("tax_lot"),
    )
    conflicts = [
        {**conflict, "field": _IDENTIFIER_FIELD_MAP[conflict["field"]]}
        for conflict in raw_conflicts
    ]
    conflict_fields = (
        {"bbl"} | {conflict["field"] for conflict in conflicts}
        if conflicts
        else set()
    )

    normalized_values: dict[str, object] = {}
    for column in sorted(record_keys & ZTLDB_COLUMNS):
        value = _normalize_value(
            column, record[column], drift_signals, observations
        )
        normalized_values[column] = value
        _advisory_vocabulary_observations(column, value, observations)

    if "zoning_district_1" not in record_keys:
        # Live-observed state (e.g. BBL 1000010201, fixture ZT07b): a lot
        # covered by no zoning feature has NO zoning_district_1 key even
        # after the 2019-12-31 always-assign change. Absence has no
        # documented semantics - surfaced, never guessed.
        observations.append("zoning_district_1_absent")

    zoning_assignment = _build_zoning_assignment(normalized_values, observations)

    absences: list[dict] = []
    for column in sorted(ZTLDB_COLUMNS - record_keys):
        if column in NOT_APPLICABLE_WHEN_ABSENT:
            absences.append(
                {
                    "column": column,
                    "classification": "not_applicable_per_source_semantics",
                    "semantics": _ABSENCE_SEMANTICS[column],
                }
            )
        else:
            absences.append(
                {
                    "column": column,
                    "classification": "absent_undocumented",
                    "semantics": (
                        "the source omitted this key and documents no blank "
                        "semantics for it; the value is UNKNOWN and is "
                        "never fabricated"
                    ),
                }
            )

    normalized_digest = canonical_json_digest(
        {
            "bbl": normalized_bbl.canonical,
            "columns": normalized_values,
            "absent_not_applicable": sorted(
                entry["column"]
                for entry in absences
                if entry["classification"] == "not_applicable_per_source_semantics"
            ),
            "absent_undocumented": sorted(
                entry["column"]
                for entry in absences
                if entry["classification"] == "absent_undocumented"
            ),
            "observed_null": sorted(
                signal.split(":", 1)[1]
                for signal in observations
                if signal.startswith("observed_null:")
            ),
        }
    )

    notes: list[str] = []
    if zoning_assignment["park_caveat"]["applies"]:
        notes.append(f"park_caveat: {PARK_CAVEAT} (official ZTLDB dictionary).")
    if freshness.source_stale_suspected:
        notes.append(
            "source_freshness: dataset rows last updated "
            f"{freshness.rows_updated_at} ({freshness.age_days} days before "
            "this check; stated cadence Monthly). This retrieval is FRESH "
            "transport of an OLD source publication - source age never "
            "marks the serve as cached or stale (two-staleness rule)."
        )

    facts: list[dict] = []
    for column in sorted(record_keys & ZTLDB_COLUMNS):
        raw_value = record[column]
        facts.append(
            {
                # Deterministic id: same dataset rows-version + BBL + field
                # => same id (idempotent re-observation).
                "provenance_id": (
                    f"ztldb-{DATASET_ID}-{freshness.version_label}-"
                    f"{normalized_bbl.canonical}-{column}"
                ),
                "source_id": SOURCE_ID,
                "original_field_name": column,
                "original_value": raw_value,
                "normalized_value": normalized_values[column],
                "units": None,
                "retrieved_at": retrieved_at,
                # No per-record version column exists; the official
                # rowsUpdatedAt timestamp is the dataset version signal.
                "dataset_version": freshness.version_label,
                "effective_date": None,
                "bbl": normalized_bbl.canonical,
                "confidence": 1.0,
                "user_confirmed_or_overridden": "none",
                "conflict_status": "conflicting"
                if column in conflict_fields
                else "none",
                # Additive provenance extensions (source_fact v1 permits
                # additional keys; required v1 field set above unchanged).
                "dataset_id": DATASET_ID,
                "request_url": url,
                "fact_key": build_fact_key(normalized_bbl.canonical, column),
                "observation_id": _build_observation_id(
                    observation_event_id, normalized_bbl.canonical, column
                ),
                "value_digest": canonical_json_digest(raw_value),
                "response_digest": response_digest,
                "source_rows_updated_at": freshness.rows_updated_at,
            }
        )

    logger.info(
        "ztldb_soda ok bbl=%s facts=%d conflicts=%d drift_signals=%d "
        "observations=%d correlation_id=%s",
        normalized_bbl.canonical, len(facts), len(conflicts),
        len(drift_signals), len(observations), correlation_id,
    )
    return ZtldbFetchResult(
        status="ok",
        bbl=normalized_bbl.canonical,
        correlation_id=correlation_id,
        request_url=url,
        retrieved_at=retrieved_at,
        dataset_version=freshness.version_label,
        record_count=1,
        facts=facts,
        conflicts=conflicts,
        drift_signals=drift_signals,
        observations=observations,
        absences=absences,
        zoning_assignment=zoning_assignment,
        notes=notes,
        raw_digest=raw_digest,
        response_digest=response_digest,
        normalized_digest=normalized_digest,
        source_freshness=freshness.to_dict(),
    )


# ---------------------------------------------------------------------------
# Bounded deterministic scan (safeguard 3; NOT a full-dataset sync)
# ---------------------------------------------------------------------------


def scan_rows(
    *,
    page_size: int,
    max_pages: int,
    transport: Transport = urllib_transport,
    timeout: float = 10.0,
    max_attempts: int = 3,
    backoff_base: float = 0.5,
    backoff_cap: float = 30.0,
    retry_after_cap: float = 120.0,
    rng: Random | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = _utc_now,
    correlation_id: str | None = None,
    app_token: str | None = None,
    budget: AnalysisBudget | None = None,
) -> ZtldbScanResult:
    """Bounded multi-page scan with deterministic ``$order=bbl`` ordering.

    ``max_pages`` is MANDATORY and hard-capped (:data:`HARD_MAX_PAGES`):
    this function exists for bounded verification scans, never for the
    857k-row full sync (out of scope by owner directive). Loop-safety
    guarantees (each violation a typed ``paging_pathology``): byte-identical
    duplicate pages, repeated records across pages, zero-progress pages,
    ordering violations, page overflow, and the page budget. Reaching the
    budget while the upstream may hold more data is an EXPLICIT typed
    failure, never silent truncation.
    """
    correlation_id = correlation_id or uuid.uuid4().hex
    if app_token is None:
        app_token = os.environ.get(APP_TOKEN_ENV_VAR) or None
    rng = rng or Random()
    if (
        isinstance(max_pages, bool)
        or not isinstance(max_pages, int)
        or not 1 <= max_pages <= HARD_MAX_PAGES
    ):
        raise DisallowedRequestError(
            f"max_pages must be an integer in 1..{HARD_MAX_PAGES} (bounded "
            "scan only; full-dataset sync is out of scope)",
            correlation_id=correlation_id,
            detail={"max_pages": repr(max_pages)},
        )
    # build_page_url bounds page_size (limit) itself.

    collected: list[dict] = []
    bbls: list[str] = []
    seen: set[str] = set()
    previous_page_bbls: list[str] | None = None
    page_urls: list[str] = []
    page_digests: list[str] = []
    notes: list[str] = []
    retrieved_at = _rfc3339(clock())
    pages_fetched = 0

    while True:
        if pages_fetched >= max_pages:
            raise PagingPathologyError(
                "page budget exhausted while the upstream may hold more "
                "data; refusing silent truncation (bounded scan only)",
                correlation_id=correlation_id,
                detail={
                    "reason": "page_budget_exhausted",
                    "pages_fetched": pages_fetched,
                    "max_pages": max_pages,
                    "collected": len(collected),
                },
            )
        url = build_page_url(
            page_size, len(collected), correlation_id=correlation_id
        )
        response = _request_with_retry(
            url,
            transport=transport,
            headers=_build_headers(app_token),
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
        retrieved_at = _rfc3339(clock())
        pages_fetched += 1
        page_urls.append(url)
        page_digests.append(raw_body_digest(response.body))
        try:
            rows = json.loads(response.body)
        except (json.JSONDecodeError, ValueError, RecursionError) as exc:
            raise MalformedResponseError(
                "SODA page body is not valid JSON",
                correlation_id=correlation_id,
                detail={"url": url, "parse_error": type(exc).__name__},
            ) from exc
        if not isinstance(rows, list):
            raise MalformedResponseError(
                "SODA page body is not the documented JSON array",
                correlation_id=correlation_id,
                detail={"url": url, "body_type": type(rows).__name__},
            )
        if len(rows) > page_size:
            raise PagingPathologyError(
                "page returned more rows than the requested limit",
                correlation_id=correlation_id,
                detail={
                    "reason": "page_overflow",
                    "url": url,
                    "rows": len(rows),
                    "limit": page_size,
                },
            )
        page_bbls: list[str] = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict) or "bbl" not in row:
                raise MalformedResponseError(
                    "page row is not an object with a bbl value",
                    correlation_id=correlation_id,
                    detail={"url": url, "row_index": index},
                )
            try:
                page_bbls.append(normalize_bbl(row["bbl"]).canonical)
            except BBLValidationError as exc:
                raise SchemaDriftError(
                    "page row bbl cannot be parsed as a canonical BBL",
                    correlation_id=correlation_id,
                    detail={
                        "url": url,
                        "row_index": index,
                        "validation_code": exc.code,
                    },
                ) from exc
        if not rows:
            break  # well-formed end of data
        if page_bbls != sorted(page_bbls) or len(set(page_bbls)) != len(page_bbls):
            raise PagingPathologyError(
                "page ordering violated the deterministic $order=bbl "
                "contract (non-ascending or duplicated within the page); "
                "gap/duplicate detection would be unsound - aborting typed",
                correlation_id=correlation_id,
                detail={"reason": "unordered_page", "url": url},
            )
        if previous_page_bbls is not None and page_bbls == previous_page_bbls:
            raise PagingPathologyError(
                "page is identical to the previous page (upstream returned "
                "the same page twice) - aborting typed, no silent duplication",
                correlation_id=correlation_id,
                detail={"reason": "duplicate_page", "page_index": pages_fetched - 1},
            )
        overlap = sorted(set(page_bbls) & seen)
        if overlap:
            reason = (
                "no_progress"
                if all(value in seen for value in page_bbls)
                else "repeated_record"
            )
            raise PagingPathologyError(
                "page repeats record(s) already extracted from an earlier "
                "page - aborting typed, no silent duplication",
                correlation_id=correlation_id,
                detail={
                    "reason": reason,
                    "page_index": pages_fetched - 1,
                    "repeated_bbls": overlap[:20],
                },
            )
        if bbls and page_bbls[0] <= bbls[-1]:
            raise PagingPathologyError(
                "page starts at or before the previous page's last record; "
                "cross-page ordering is broken - aborting typed",
                correlation_id=correlation_id,
                detail={"reason": "unordered_page", "page_index": pages_fetched - 1},
            )
        seen.update(page_bbls)
        bbls.extend(page_bbls)
        collected.extend(rows)
        previous_page_bbls = page_bbls
        if len(rows) < page_size:
            break  # final short page

    notes.append(
        "bounded_scan: completed at a well-formed short/empty page within "
        "the page budget (this is a bounded verification scan, not a "
        "full-dataset extraction - out of scope by owner directive)."
    )
    normalized_digest = canonical_json_digest(
        sorted(collected, key=lambda row: str(row.get("bbl")))
    )
    logger.info(
        "ztldb_soda scan ok pages=%d records=%d correlation_id=%s",
        pages_fetched, len(collected), correlation_id,
    )
    return ZtldbScanResult(
        status="ok",
        correlation_id=correlation_id,
        page_request_urls=page_urls,
        retrieved_at=retrieved_at,
        page_size=page_size,
        page_count=pages_fetched,
        record_count=len(collected),
        bbls=bbls,
        records=collected,
        page_raw_digests=page_digests,
        normalized_digest=normalized_digest,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Resilient fetcher (M1-T009 primitives composed; no second resilience
# system; mirrors the accepted ResilientPlutoFetcher / M2-T007 client)
# ---------------------------------------------------------------------------


@dataclass
class _LkgEntry:
    stored_at: float
    result: ZtldbFetchResult


def _is_transient(exc: ZtldbConnectorError) -> bool:
    """Transient upstream trouble only: rate limit, timeout, network, 5xx.
    Schema drift, malformed responses, paging pathologies, disallowed
    requests, and non-drift 400s are NOT transient (retrying or serving
    stale data would mask a real contract problem)."""
    if isinstance(exc, RateLimitedError | SourceTimeoutError):
        return True
    if isinstance(exc, UpstreamError):
        status = exc.detail.get("http_status")
        if isinstance(status, int) and not isinstance(status, bool):
            return 500 <= status < 600
        return exc.detail.get("reason_kind") in ("network", "timeout", "server_error")
    return False


class ResilientZtldbFetcher:
    """Callable ``(bbl, correlation_id, *, budget=None) -> ZtldbFetchResult``
    composing cache + circuit breaker + last-known-good + budget from the
    M1-T009 primitives around :func:`fetch_by_bbl`.

    TWO-STALENESS RULE: ``staleness`` is stamped HERE and ONLY here -
    ``{served_from_cache, stale, ...}`` describes the transport/cache serve
    path. ``source_freshness`` (dataset publication age) and
    ``retrieved_at`` are copied verbatim from the original result on every
    serve path and NEVER influence the staleness stamp: an old source
    dataset retrieved fresh is NOT stale; a cache/LKG serve does not alter
    source timestamps.
    """

    def __init__(
        self,
        *,
        config: ResilienceConfig | None = None,
        transport: Transport = urllib_transport,
        timeout: float = 10.0,
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
        return (
            f"{self._config.cache_key_version}:{SOURCE_ID}:{DATASET_ID}:"
            f"bbl={canonical_bbl}"
        )

    def __call__(
        self,
        bbl: object,
        correlation_id: str,
        *,
        budget: AnalysisBudget | None = None,
    ) -> ZtldbFetchResult:
        canonical = normalize_bbl(bbl).canonical  # validation before anything
        key = self._cache_key(canonical)

        hit = self._cache.get_with_age(key)
        if hit is not None:
            cached, age_seconds = hit
            self.metrics.emit("cache_hit", key=key, correlation_id=correlation_id)
            result: ZtldbFetchResult = copy.deepcopy(cached)  # type: ignore[assignment]
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
            result = fetch_by_bbl(
                canonical,
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
        except ZtldbConnectorError as exc:
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
        if result.status == "ok":
            self._store_lkg(key, result)
        self.metrics.emit(
            "fetch_success", status=result.status, correlation_id=correlation_id
        )
        return result

    def _store_lkg(self, key: str, result: ZtldbFetchResult) -> None:
        with self._lkg_lock:
            self._lkg[key] = _LkgEntry(
                stored_at=self._now(), result=copy.deepcopy(result)
            )
            self._lkg.move_to_end(key)
            while len(self._lkg) > self._config.lkg_max_entries:
                self._lkg.popitem(last=False)

    def _serve_lkg_or_raise(
        self, key: str, correlation_id: str, exc: ZtldbConnectorError
    ) -> ZtldbFetchResult:
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
            "source_freshness reflect the original retrieval and the "
            "official dataset publication age (two-staleness rule)."
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
