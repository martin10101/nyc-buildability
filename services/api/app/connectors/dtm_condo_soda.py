"""DOF Digital Tax Map condo billing-BBL -> base-lot-set resolver (M5-T042).

Deterministic, typed, fail-closed resolver that converts a condominium BBL
into the FULL SET of its base land tax lots, so a ``condo -> base-lot`` step
can run BEFORE the zoning-lot lookup. Sole source: the verified DB-002
research record ``docs/research/condo-base-lot-resolution-sources.md``
(retrieved 2026-09-18, raw official responses embedded). This module
implements ONLY that verified path:

- PRIMARY (billing) - DOF DTM "Condominiums" Socrata dataset ``p8u6-a6it``:
  ``condo_billing_bbl`` (the 7501-7599 series) -> one row per
  ``condo_base_bbl`` (text-typed 10-digit BBLs). A billing lot can map to
  MORE THAN ONE base lot (the worked case ``3022647515`` -> {32, 33}); the
  resolver ALWAYS returns the set and NEVER collapses it (research 3.3).
- PRIMARY (unit reverse) - DOF DTM "Condominium Units" dataset
  ``eguu-7ie3``: ``unit_bbl`` (the 1001-6999 series) -> ``condo_base_bbl``
  plus ``condo_key``; the resolver then expands by ``condo_key`` against
  ``p8u6-a6it`` so the returned set is the complete base-lot set, not just
  the one lot the unit sits on (research 4, 7 step 3).
- FALLBACK (condo_key) - :func:`resolve_by_condo_key` covers the 28 condos
  that have a NULL ``condo_billing_bbl`` (research 3.4, 7 step 4a): given a
  ``condo_key`` known from elsewhere, resolve the set directly.

Boundaries (permanent, per the DB-002 research and the M5-T042 packet):

- This module makes NO zoning determination and NEVER collapses a multi-lot
  set to one lot or one zoning answer. When a condo's base lots carry
  different zoning, the condo may span more than one zoning lot - a legal
  construct (ZR 12-10) distinct from a tax lot. That divergent-zoning
  handling is a DOWNSTREAM qualified-human legal surface (research 7 step 6),
  deliberately out of scope here; :data:`DIVERGENT_ZONING_NOTICE` is carried
  on every resolved result to keep that boundary visible.
- PLUTO ``appbbl`` is NEVER a base-lot source: it is single-valued and
  structurally incomplete for multi-lot condos (research 6.1, it returns
  only lot 32 for the two-lot worked case). It may appear only as an
  optional cross-check flag in a later packet - never consulted here.
- The ArcGIS failover (research 5) is a later hardening option and is NOT
  implemented here.

This is a LEAF connector: no property-lookup / ZTLDB pipeline wiring, no
route change - the wiring is its own later packet. Deterministic code only:
no AI, no legal interpretation, no invented values. Every well-formed input
that resolves to nothing returns an honest typed
``condo_base_lot_unresolved`` result - never a fabricated base lot and never
an exception.
"""

from __future__ import annotations

# stdlib json parses responses (no third-party HTTP dependency; the low-storage
# policy forbids new deps - reuse the accepted transport stack).
import json
import logging
import os
import re
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import NoReturn

from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.resilience.transport import (
    Transport,
    TransportResponse,
    fixed_exponential_delay,
    request_with_retry,
    standard_retry_hooks,
    urllib_transport,
)

__all__ = [
    "CONDO_COLUMNS",
    "CONDO_DATASET_ID",
    "DIVERGENT_ZONING_NOTICE",
    "INPUT_KIND_BBL",
    "INPUT_KIND_CONDO_KEY",
    "LOT_CLASS_BILLING",
    "LOT_CLASS_NOT_A_CONDO",
    "LOT_CLASS_UNIT",
    "PATH_BILLING",
    "PATH_CONDO_KEY",
    "PATH_UNIT",
    "RESEARCH_OBSERVED_ROWS_UPDATED_AT",
    "STATUS_NOT_A_CONDO",
    "STATUS_RESOLVED",
    "STATUS_UNRESOLVED",
    "UNIT_COLUMNS",
    "UNIT_DATASET_ID",
    "CondoBaseLotResult",
    "DtmCondoConnectorError",
    "RateLimitedError",
    "SchemaDriftError",
    "SourceTimeoutError",
    "SourceUnavailableError",
    "classify_lot",
    "resolve",
    "resolve_by_condo_key",
]

logger = logging.getLogger("app.connectors.dtm_condo_soda")

# --- Dataset identities (research section 2 / 10; DOF attribution) ----------
# source_registry record: docs/research/source-registry-drafts/dtm-condo.json
# (both DTM datasets, landed with the M5-T045 live wiring; DB-029b).
SOURCE_ID = "nyc-dof-dtm-condo-soda"
CONDO_DATASET_ID = "p8u6-a6it"  # DTM Condominiums (billing -> base lot set)
UNIT_DATASET_ID = "eguu-7ie3"  # DTM Condominium Units (unit -> base lot)
CONDO_BASE_URL = f"https://data.cityofnewyork.us/resource/{CONDO_DATASET_ID}.json"
UNIT_BASE_URL = f"https://data.cityofnewyork.us/resource/{UNIT_DATASET_ID}.json"
APP_TOKEN_ENV_VAR = "SOCRATA_APP_TOKEN"

# rowsUpdatedAt observed at DB-002 research retrieval (2026-09-18); provenance
# hint only. Live freshness is a metadata fetch performed by the later wiring
# packet - the resolver records ``None`` unless a caller injects the current
# value (research 3.1 / 4.1; do not assert this is fresh today).
RESEARCH_OBSERVED_ROWS_UPDATED_AT: dict[str, str] = {
    CONDO_DATASET_ID: "2026-09-01T14:05:56Z",
    UNIT_DATASET_ID: "2026-09-01T14:05:41Z",
}

# --- Lot-number classification (research section 7 step 1) ------------------
BILLING_LOT_RANGE = (7501, 7599)
UNIT_LOT_RANGE = (1001, 6999)

LOT_CLASS_BILLING = "billing"
LOT_CLASS_UNIT = "unit"
LOT_CLASS_NOT_A_CONDO = "not_a_condo"

# --- Result status / resolution path vocabularies --------------------------
STATUS_RESOLVED = "resolved"
STATUS_NOT_A_CONDO = "not_a_condo"
STATUS_UNRESOLVED = "condo_base_lot_unresolved"

PATH_BILLING = "billing"
PATH_UNIT = "unit"
PATH_CONDO_KEY = "condo_key"

# --- Input-identity vocabulary (G3 #3 / G4 #5; M5-T044 item f) --------------
# Names what the result's ``input_value`` is, so a condo_key resolution no
# longer overloads a BBL-named field or a filler lot_class. Module-internal
# (this leaf has no consumer): tests and docstrings move together.
INPUT_KIND_BBL = "bbl"
INPUT_KIND_CONDO_KEY = "condo_key"

# --- Schema shape guards (research section 3.2 / 4.1) ----------------------
# Condominiums table: 9 columns; Condominium Units table: 16 columns. The
# suite cross-checks these against the stored fixtures (schema-shape guard,
# research C10). Never infer schema from record keys.
CONDO_COLUMNS: frozenset[str] = frozenset(
    {
        "condo_base_boro",
        "condo_base_block",
        "condo_base_lot",
        "condo_base_bbl",
        "condo_base_bbl_key",
        "condo_key",
        "condo_number",
        "condo_name",
        "condo_billing_bbl",
    }
)
UNIT_COLUMNS: frozenset[str] = frozenset(
    {
        "condo_base_boro",
        "condo_base_block",
        "condo_base_lot",
        "condo_base_bbl",
        "condo_base_bbl_key",
        "condo_key",
        "condo_number",
        "unit_boro",
        "unit_block",
        "unit_lot",
        "unit_bbl",
        "unit_designation",
        "floor_text",
        "model",
        "geometry_type",
        "effective_tax_year",
    }
)

# BBL text shape (research 3.2): the DTM BBL columns are Socrata TEXT, so they
# arrive as clean zero-padded 10-digit strings. The PLUTO number-type decimal
# serialization ("3022640032.00000000") is REJECTED here - a base lot is only
# ever accepted in this exact shape, fail-closed on anything else.
#
# G5 F1/F2 (M5-T044): matched with ``re.ASCII`` + ``.fullmatch`` so the guard
# is anchor-tight. A ``$`` anchor would accept a trailing "\n" and a bare
# ``\d`` would accept Unicode digits (Arabic-Indic etc.); ``re.ASCII`` pins
# ``\d`` to ``[0-9]`` and ``fullmatch`` requires the WHOLE string to match, so
# "3022647515\n", " 3022647515", and Unicode-digit strings all fail closed.
_STRICT_BBL_RE = re.compile(r"\d{10}", re.ASCII)
# condo_key is a 6-digit identifier: condo boro (1 digit) + 5-digit condo
# number (research 3.2 field description). Same re.ASCII + fullmatch guard.
_CONDO_KEY_RE = re.compile(r"\d{6}", re.ASCII)

# Schema-drift 400 signature (Socrata platform behavior; same as the accepted
# pluto_soda / ztldb_soda connectors).
SCHEMA_DRIFT_ERROR_CODE = "query.soql.no-such-column"
# M5-T045 rider (G5 F-consistency): matched with re.ASCII + .fullmatch like the
# BBL / condo_key guards, so a code carrying a trailing newline or a Unicode
# character fails the safe check and is repr()'d rather than logged verbatim.
# ($-anchored .match used to accept a trailing "\n".)
_ERROR_CODE_SAFE_RE = re.compile(r"[A-Za-z0-9._-]{1,120}", re.ASCII)

DIVERGENT_ZONING_NOTICE = (
    "This resolver returns the full SET of base tax lots and makes NO zoning "
    "determination. If the base lots carry different zoning districts or "
    "overlays the condominium may span more than one zoning lot (ZR 12-10, a "
    "legal construct distinct from a tax lot); that determination is a "
    "downstream qualified-human legal surface and is never auto-collapsed "
    "here (DB-002 research section 7 step 6)."
)


# ---------------------------------------------------------------------------
# Error taxonomy (mirrors the accepted SODA connectors; payloads never carry
# stack traces, headers, or the app token).
# ---------------------------------------------------------------------------
class DtmCondoConnectorError(Exception):
    """Base typed connector error."""

    error_type = "source_unavailable"

    def __init__(
        self, message: str, *, correlation_id: str, detail: dict | None = None
    ) -> None:
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


class RateLimitedError(DtmCondoConnectorError):
    """HTTP 429 persisted through the bounded retry budget."""

    error_type = "rate_limited"


class SchemaDriftError(DtmCondoConnectorError):
    """Dataset contract changed, or a load-bearing field is missing or in an
    unexpected shape (e.g. a base BBL that is not 10 digits). Surfaced for
    alerting; never blindly retried, never guessed around."""

    error_type = "schema_drift"


class SourceTimeoutError(DtmCondoConnectorError):
    """Connect/read timeout persisted through the retry budget."""

    error_type = "timeout"


class SourceUnavailableError(DtmCondoConnectorError):
    """Network failure, 5xx persisted through retries, or an unexpected
    non-drift HTTP status."""

    error_type = "source_unavailable"


# ---------------------------------------------------------------------------
# Result contract
# ---------------------------------------------------------------------------
@dataclass
class CondoBaseLotResult:
    """Typed resolver result. ``base_bbls`` is the FULL SET of base tax lots
    (sorted, deduplicated) and is never collapsed to one lot; it is populated
    only when ``status == 'resolved'``.

    ``status`` is one of :data:`STATUS_RESOLVED`, :data:`STATUS_NOT_A_CONDO`
    (a non-condo lot number - zero lookups performed), or
    :data:`STATUS_UNRESOLVED` (a well-formed condo BBL that matched no data
    or whose fallbacks were exhausted - an honest no-result, never a
    fabricated lot).

    ``provenance`` records one entry per SODA query actually performed
    (dataset id, request URL, retrieval timestamp, record count, and
    ``rows_updated_at`` when the caller supplies live dataset freshness).

    ``input_value`` is the resolver input verbatim and ``input_kind`` names
    what it is (:data:`INPUT_KIND_BBL` for :func:`resolve`,
    :data:`INPUT_KIND_CONDO_KEY` for :func:`resolve_by_condo_key`) so a
    condo_key resolution never masquerades as a BBL (G3 #3 / G4 #5).
    ``lot_class`` is the input BBL's lot class and is ``None`` for a condo_key
    input, which has no lot number.
    """

    status: str
    input_value: str
    lot_class: str | None
    correlation_id: str
    retrieved_at: str
    input_kind: str = INPUT_KIND_BBL
    resolution_path: str | None = None
    base_bbls: list[str] = field(default_factory=list)
    condo_number: str | None = None
    condo_key: str | None = None
    provenance: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    divergent_zoning_notice: str = DIVERGENT_ZONING_NOTICE


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _utc_now() -> datetime:
    return datetime.now(UTC)


def _rfc3339(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_headers(app_token: str | None) -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if app_token:
        # Optional per the official Socrata app-token model (research 8.9);
        # header only, never logged, never in payloads or errors.
        headers["X-App-Token"] = app_token
    return headers


def _classify_400(body: str) -> str | None:
    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, ValueError, RecursionError):
        return None
    if isinstance(parsed, dict):
        code = parsed.get("errorCode")
        if isinstance(code, str):
            return code
    return None


def _sanitize_error_code(code: str | None) -> str | None:
    if code is None:
        return None
    # M5-T045 rider (G5 F-consistency): .fullmatch, NOT .match, so a code that
    # is safe only as a PREFIX (e.g. "no-such-column\n<injected>") fails the
    # guard and is repr()'d rather than logged verbatim - the same anchor-tight
    # posture the BBL / condo_key guards already use.
    if _ERROR_CODE_SAFE_RE.fullmatch(code):
        return code
    return repr(code)


def _limit_suffix(row_limit: int | None, *, correlation_id: str) -> str:
    """M5-T045 rider (optional $limit defense-in-depth): append a SODA ``$limit``
    to a keyed lookup so a drift that changes a key column's meaning cannot
    return an unbounded page. Off by default (``None`` -> byte-identical URLs);
    a caller opts in with a positive int. A non-positive / non-int value fails
    closed rather than silently omitting the cap."""
    if row_limit is None:
        return ""
    if not isinstance(row_limit, int) or isinstance(row_limit, bool) or row_limit <= 0:
        raise SchemaDriftError(
            "row_limit must be a positive int when supplied",
            correlation_id=correlation_id,
            detail={"row_limit": repr(row_limit)},
        )
    return f"&$limit={row_limit}"


def classify_lot(bbl: str) -> str:
    """Classify a canonical 10-digit BBL by its four-digit lot number
    (research section 7 step 1): billing (7501-7599), unit (1001-6999), or
    not-a-condo. Raises :class:`BBLValidationError` for any input that is not
    an exact 10 ASCII-digit string (fail-closed shape guard - the resolver's
    contract input is a 10-digit BBL string). The error carries the documented
    ``non_numeric`` code (G3 #2 / M5-T044 item e; ``bbl.py`` vocabulary), never
    an ad-hoc one."""
    if not isinstance(bbl, str) or not _STRICT_BBL_RE.fullmatch(bbl):
        raise BBLValidationError(
            "non_numeric",
            "resolver input must be an exact 10 ASCII-digit BBL string "
            f"([0-9]{{10}}); got {bbl!r}",
            bbl,
        )
    # normalize_bbl re-validates borough/block/lot ranges (defense in depth).
    normalized = normalize_bbl(bbl)
    lot = normalized.lot
    if BILLING_LOT_RANGE[0] <= lot <= BILLING_LOT_RANGE[1]:
        return LOT_CLASS_BILLING
    if UNIT_LOT_RANGE[0] <= lot <= UNIT_LOT_RANGE[1]:
        return LOT_CLASS_UNIT
    return LOT_CLASS_NOT_A_CONDO


def _request(
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
    """Bounded retry on 429/5xx/timeout/network failure only; the
    no-such-column 400 is typed schema drift (never retried) and every other
    400 is typed source-unavailable. Reuses the shared accepted retry
    engine."""

    def _raise_for_unexpected_status(response: TransportResponse) -> NoReturn:
        if response.status == 400:
            error_code = _classify_400(response.body)
            safe_code = _sanitize_error_code(error_code)
            if error_code == SCHEMA_DRIFT_ERROR_CODE:
                raise SchemaDriftError(
                    "SODA rejected a column reference: schema drift signature "
                    f"({SCHEMA_DRIFT_ERROR_CODE})",
                    correlation_id=correlation_id,
                    detail={"http_status": 400, "error_code": safe_code, "url": url},
                )
            raise SourceUnavailableError(
                "SODA rejected the request (HTTP 400, not the schema-drift "
                "signature)",
                correlation_id=correlation_id,
                detail={"http_status": 400, "error_code": safe_code, "url": url},
            )
        raise SourceUnavailableError(
            f"unexpected HTTP status {response.status} from SODA endpoint",
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
            log_label="dtm_condo_soda",
            correlation_id=correlation_id,
            url=url,
            sanitize_network_reason=lambda reason: reason,
            rate_limited_error=RateLimitedError,
            rate_limited_message=(
                "SODA throttled the request (HTTP 429) and the retry budget is "
                "exhausted; configure SOCRATA_APP_TOKEN to leave the shared "
                "tokenless pool"
            ),
            timeout_error=SourceTimeoutError,
            timeout_message="SODA request timed out and the retry budget is exhausted",
            unavailable_error=SourceUnavailableError,
            unavailable_message="SODA endpoint unavailable and the retry budget is exhausted",
            include_reason_kind=False,
            raise_for_unexpected_status=_raise_for_unexpected_status,
        ),
        compute_delay=fixed_exponential_delay(backoff_base),
        sleep=sleep,
    )


def _fetch_rows(
    url: str,
    *,
    transport: Transport,
    timeout: float,
    max_attempts: int,
    backoff_base: float,
    sleep: Callable[[float], None],
    app_token: str | None,
    correlation_id: str,
) -> list[dict]:
    """Fetch and parse one SODA resource query into a list of record dicts.
    A well-formed empty array is a legitimate no-match RESULT and is returned
    as ``[]``. Anything that is not a JSON array of objects is typed schema
    drift - never silently coerced into an empty result."""
    response = _request(
        url,
        transport=transport,
        headers=_build_headers(app_token),
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        sleep=sleep,
        correlation_id=correlation_id,
    )
    try:
        records = json.loads(response.body)
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise SchemaDriftError(
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
    for record in records:
        if not isinstance(record, dict):
            raise SchemaDriftError(
                "SODA record is not a JSON object",
                correlation_id=correlation_id,
                detail={"url": url, "record_type": type(record).__name__},
            )
    return records


def _collect_base_lots(
    records: list[dict],
    *,
    url: str,
    allowed_columns: frozenset[str],
    correlation_id: str,
    notes: list[str],
) -> tuple[set[str], str | None, str | None]:
    """Extract the base-lot set plus condo identifiers from resource rows,
    fail-closed on any drift. Every ``condo_base_bbl`` must match the exact 10
    ASCII-digit shape (``re.ASCII`` + ``fullmatch``, research 3.2 / C7; G5 F2):
    the PLUTO-style decimal serialization, a Unicode-digit value, and a
    trailing-newline value all raise :class:`SchemaDriftError`. Unknown columns
    are recorded as an advisory note, never trusted for values."""
    base_bbls: set[str] = set()
    condo_numbers: set[str] = set()
    condo_keys: set[str] = set()
    for record in records:
        unknown = set(record) - allowed_columns
        if unknown:
            notes.append(f"unknown_columns:{','.join(sorted(unknown))}")
        base = record.get("condo_base_bbl")
        if not isinstance(base, str) or not _STRICT_BBL_RE.fullmatch(base):
            raise SchemaDriftError(
                "condo_base_bbl is missing or not an exact 10 ASCII-digit "
                "string (the PLUTO-style decimal serialization, a Unicode-digit "
                "value, and a trailing-newline value are all rejected)",
                correlation_id=correlation_id,
                detail={"url": url, "condo_base_bbl": repr(base)},
            )
        base_bbls.add(base)
        number = record.get("condo_number")
        if isinstance(number, str) and number:
            condo_numbers.add(number)
        key = record.get("condo_key")
        if isinstance(key, str) and key:
            condo_keys.add(key)
    if len(condo_numbers) > 1:
        notes.append(f"multiple_condo_numbers:{','.join(sorted(condo_numbers))}")
    if len(condo_keys) > 1:
        notes.append(f"multiple_condo_keys:{','.join(sorted(condo_keys))}")
    condo_number = next(iter(condo_numbers)) if len(condo_numbers) == 1 else None
    condo_key = next(iter(condo_keys)) if len(condo_keys) == 1 else None
    return base_bbls, condo_number, condo_key


def _provenance_entry(
    *,
    dataset_id: str,
    url: str,
    retrieved_at: str,
    record_count: int,
    query_kind: str,
    dataset_rows_updated_at: dict[str, str] | None,
) -> dict:
    rows_updated_at = (
        dataset_rows_updated_at.get(dataset_id) if dataset_rows_updated_at else None
    )
    return {
        "dataset_id": dataset_id,
        "query_kind": query_kind,
        "request_url": url,
        "retrieved_at": retrieved_at,
        "record_count": record_count,
        # rowsUpdatedAt is a live metadata fetch (research 3.1); None here
        # unless the caller injects the current value. Never fabricated.
        "rows_updated_at": rows_updated_at,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def resolve(
    bbl: str,
    *,
    transport: Transport = urllib_transport,
    timeout: float = 10.0,
    max_attempts: int = 3,
    backoff_base: float = 0.5,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = _utc_now,
    correlation_id: str | None = None,
    app_token: str | None = None,
    dataset_rows_updated_at: dict[str, str] | None = None,
    row_limit: int | None = None,
) -> CondoBaseLotResult:
    """Resolve a condominium BBL to the FULL SET of its base land tax lots.

    Classifies the input by lot number, then follows the verified DB-002 path:
    a billing BBL (7501-7599) resolves against ``p8u6-a6it``; a unit BBL
    (1001-6999) resolves against ``eguu-7ie3`` and is expanded by
    ``condo_key`` so the returned set is complete; any other lot number is
    :data:`STATUS_NOT_A_CONDO` with zero lookups.

    Deterministic: the same input (with a fixed clock/correlation id) always
    yields the same result. A well-formed condo BBL that matches nothing
    yields :data:`STATUS_UNRESOLVED` - never a fabricated lot, never an
    exception. A malformed BBL shape fails closed via
    :class:`BBLValidationError` before any network I/O.
    """
    correlation_id = correlation_id or uuid.uuid4().hex
    if app_token is None:
        app_token = os.environ.get(APP_TOKEN_ENV_VAR) or None
    lot_class = classify_lot(bbl)  # fail-closed shape guard, before any I/O

    if lot_class == LOT_CLASS_NOT_A_CONDO:
        return CondoBaseLotResult(
            status=STATUS_NOT_A_CONDO,
            input_value=bbl,
            input_kind=INPUT_KIND_BBL,
            lot_class=lot_class,
            correlation_id=correlation_id,
            # No query is issued on this branch, so retrieved_at is stamped at
            # classification time (there is no response to wait for).
            retrieved_at=_rfc3339(clock()),
            notes=[
                "lot number is outside the condo billing (7501-7599) and unit "
                "(1001-6999) ranges; no condo resolution is performed and no "
                "lookup is issued (research section 7 step 1)."
            ],
        )

    # G5 F1: interpolate the CANONICAL normalized value into every URL, never
    # the raw input. classify_lot already accepts only an exact 10 ASCII-digit
    # string, so raw == canonical for any accepted input; this makes that
    # invariant explicit and keeps a non-canonical value from ever reaching the
    # transport.
    canonical_bbl = normalize_bbl(bbl).canonical
    fetch_kwargs = {
        "transport": transport,
        "timeout": timeout,
        "max_attempts": max_attempts,
        "backoff_base": backoff_base,
        "sleep": sleep,
        "app_token": app_token,
        "correlation_id": correlation_id,
    }
    notes: list[str] = []
    provenance: list[dict] = []
    limit = _limit_suffix(row_limit, correlation_id=correlation_id)

    if lot_class == LOT_CLASS_BILLING:
        url = f"{CONDO_BASE_URL}?condo_billing_bbl={canonical_bbl}{limit}"
        records = _fetch_rows(url, **fetch_kwargs)
        # G3 #1: stamp retrieved_at AFTER the successful response, per query
        # (the pluto_soda precedent) - a pre-request stamp could precede actual
        # retrieval across retries.
        retrieved_at = _rfc3339(clock())
        provenance.append(
            _provenance_entry(
                dataset_id=CONDO_DATASET_ID,
                url=url,
                retrieved_at=retrieved_at,
                record_count=len(records),
                query_kind="condo_billing_bbl",
                dataset_rows_updated_at=dataset_rows_updated_at,
            )
        )
        base_bbls, condo_number, condo_key = _collect_base_lots(
            records,
            url=url,
            allowed_columns=CONDO_COLUMNS,
            correlation_id=correlation_id,
            notes=notes,
        )
        if not base_bbls:
            # No condo_key is available from an empty billing response, so the
            # condo_key fallback (research 7 step 4a) cannot run here.
            return _unresolved(
                bbl, lot_class, correlation_id, retrieved_at, provenance,
                notes
                + [
                    "billing-BBL query returned no rows; with no condo_key "
                    "available the condo_key fallback cannot run - honest "
                    "unresolved result (never a fabricated base lot)."
                ],
            )
        return _resolved(
            bbl, lot_class, PATH_BILLING, base_bbls, condo_number, condo_key,
            correlation_id, retrieved_at, provenance, notes,
        )

    # Unit lot: reverse-resolve, then expand by condo_key for the full set.
    unit_url = f"{UNIT_BASE_URL}?unit_bbl={canonical_bbl}{limit}"
    unit_records = _fetch_rows(unit_url, **fetch_kwargs)
    retrieved_at = _rfc3339(clock())  # G3 #1: post-response stamp for the unit query
    provenance.append(
        _provenance_entry(
            dataset_id=UNIT_DATASET_ID,
            url=unit_url,
            retrieved_at=retrieved_at,
            record_count=len(unit_records),
            query_kind="unit_bbl",
            dataset_rows_updated_at=dataset_rows_updated_at,
        )
    )
    unit_bases, condo_number, condo_key = _collect_base_lots(
        unit_records,
        url=unit_url,
        allowed_columns=UNIT_COLUMNS,
        correlation_id=correlation_id,
        notes=notes,
    )
    if not unit_bases:
        return _unresolved(
            bbl, lot_class, correlation_id, retrieved_at, provenance,
            notes
            + [
                "unit-BBL query returned no rows - honest unresolved result "
                "(never a fabricated base lot)."
            ],
        )
    base_bbls = set(unit_bases)
    if condo_key is not None:
        # G5 F1: the condo_key came from the unit response, so guard its shape
        # before it is interpolated into the expansion URL (response-side, the
        # same fail-closed posture as the condo_base_bbl guard).
        if not _CONDO_KEY_RE.fullmatch(condo_key):
            raise SchemaDriftError(
                "condo_key on the unit response is not an exact 6 ASCII-digit "
                "string; refusing to interpolate it into an expansion query",
                correlation_id=correlation_id,
                detail={"url": unit_url, "condo_key": repr(condo_key)},
            )
        # Expand to the complete base-lot set so a multi-lot condo is never
        # collapsed to the single lot the unit sits on (research 7 step 3).
        expand_url = f"{CONDO_BASE_URL}?condo_key={condo_key}{limit}"
        expand_records = _fetch_rows(expand_url, **fetch_kwargs)
        # G3 #1: the expansion query gets its OWN post-response timestamp, so a
        # two-query resolve carries two distinct retrieved_at values.
        retrieved_at = _rfc3339(clock())
        provenance.append(
            _provenance_entry(
                dataset_id=CONDO_DATASET_ID,
                url=expand_url,
                retrieved_at=retrieved_at,
                record_count=len(expand_records),
                query_kind="condo_key_expansion",
                dataset_rows_updated_at=dataset_rows_updated_at,
            )
        )
        expand_bases, expand_number, _expand_key = _collect_base_lots(
            expand_records,
            url=expand_url,
            allowed_columns=CONDO_COLUMNS,
            correlation_id=correlation_id,
            notes=notes,
        )
        base_bbls |= expand_bases
        condo_number = condo_number or expand_number
        notes.append(
            "unit direct base lot(s) "
            f"{sorted(unit_bases)} expanded by condo_key={condo_key} to the "
            f"full base-lot set {sorted(base_bbls)}."
        )
    else:
        notes.append(
            "no condo_key on the unit row; returning the unit's direct base "
            "lot(s) without condo_key expansion (the set may be incomplete "
            "for a multi-lot condo - surfaced, never guessed)."
        )
    return _resolved(
        bbl, lot_class, PATH_UNIT, base_bbls, condo_number, condo_key,
        correlation_id, retrieved_at, provenance, notes,
    )


def resolve_by_condo_key(
    condo_key: str,
    *,
    transport: Transport = urllib_transport,
    timeout: float = 10.0,
    max_attempts: int = 3,
    backoff_base: float = 0.5,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = _utc_now,
    correlation_id: str | None = None,
    app_token: str | None = None,
    dataset_rows_updated_at: dict[str, str] | None = None,
    row_limit: int | None = None,
) -> CondoBaseLotResult:
    """Resolve the full base-lot set directly from a ``condo_key`` (research
    section 7 step 4a). This is the fallback for the 28 condos that carry a
    NULL ``condo_billing_bbl`` and therefore cannot be reached by the
    billing-BBL path - a caller that already holds the condo_key (e.g. from
    the units table or an external identifier) resolves the set here.

    ``condo_key`` must be the 6-digit identifier (condo boro + 5-digit condo
    number); any other shape fails closed via :class:`BBLValidationError`. An
    empty result is an honest :data:`STATUS_UNRESOLVED`, never a fabricated
    lot.
    """
    correlation_id = correlation_id or uuid.uuid4().hex
    if app_token is None:
        app_token = os.environ.get(APP_TOKEN_ENV_VAR) or None
    if not isinstance(condo_key, str) or not _CONDO_KEY_RE.fullmatch(condo_key):
        raise BBLValidationError(
            "invalid_component",
            "condo_key must be the 6 ASCII-digit identifier (condo boro + "
            f"5-digit condo number, [0-9]{{6}}); got {condo_key!r}",
            condo_key,
        )
    notes: list[str] = []
    provenance: list[dict] = []
    limit = _limit_suffix(row_limit, correlation_id=correlation_id)
    url = f"{CONDO_BASE_URL}?condo_key={condo_key}{limit}"
    records = _fetch_rows(
        url,
        transport=transport,
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        sleep=sleep,
        app_token=app_token,
        correlation_id=correlation_id,
    )
    # [ORCH-CORRECTED per M5-T044-G3 F1] retrieved_at is stamped AFTER the
    # successful fetch (the pluto post-response precedent), mirroring resolve().
    retrieved_at = _rfc3339(clock())
    provenance.append(
        _provenance_entry(
            dataset_id=CONDO_DATASET_ID,
            url=url,
            retrieved_at=retrieved_at,
            record_count=len(records),
            query_kind="condo_key",
            dataset_rows_updated_at=dataset_rows_updated_at,
        )
    )
    base_bbls, condo_number, resolved_key = _collect_base_lots(
        records,
        url=url,
        allowed_columns=CONDO_COLUMNS,
        correlation_id=correlation_id,
        notes=notes,
    )
    if not base_bbls:
        return CondoBaseLotResult(
            status=STATUS_UNRESOLVED,
            # G3 #3 / G4 #5: honest input identity - a condo_key input carries
            # input_kind=condo_key and lot_class=None (it has no lot number),
            # never an overloaded input_bbl / not_a_condo filler.
            input_value=condo_key,
            input_kind=INPUT_KIND_CONDO_KEY,
            lot_class=None,
            resolution_path=None,
            correlation_id=correlation_id,
            retrieved_at=retrieved_at,
            provenance=provenance,
            notes=notes
            + [
                "condo_key query returned no rows - honest unresolved result "
                "(never a fabricated base lot)."
            ],
        )
    return CondoBaseLotResult(
        status=STATUS_RESOLVED,
        input_value=condo_key,
        input_kind=INPUT_KIND_CONDO_KEY,
        lot_class=None,
        resolution_path=PATH_CONDO_KEY,
        base_bbls=sorted(base_bbls),
        condo_number=condo_number,
        condo_key=resolved_key or condo_key,
        correlation_id=correlation_id,
        retrieved_at=retrieved_at,
        provenance=provenance,
        notes=notes,
    )


def _resolved(
    input_value: str,
    lot_class: str,
    path: str,
    base_bbls: set[str],
    condo_number: str | None,
    condo_key: str | None,
    correlation_id: str,
    retrieved_at: str,
    provenance: list[dict],
    notes: list[str],
) -> CondoBaseLotResult:
    if len(base_bbls) > 1:
        notes.append(
            f"multi-lot condo: {len(base_bbls)} base lots resolved; the full "
            "set is returned and never collapsed."
        )
    return CondoBaseLotResult(
        status=STATUS_RESOLVED,
        input_value=input_value,
        input_kind=INPUT_KIND_BBL,
        lot_class=lot_class,
        resolution_path=path,
        base_bbls=sorted(base_bbls),
        condo_number=condo_number,
        condo_key=condo_key,
        correlation_id=correlation_id,
        retrieved_at=retrieved_at,
        provenance=provenance,
        notes=notes,
    )


def _unresolved(
    input_value: str,
    lot_class: str,
    correlation_id: str,
    retrieved_at: str,
    provenance: list[dict],
    notes: list[str],
) -> CondoBaseLotResult:
    return CondoBaseLotResult(
        status=STATUS_UNRESOLVED,
        input_value=input_value,
        input_kind=INPUT_KIND_BBL,
        lot_class=lot_class,
        resolution_path=None,
        correlation_id=correlation_id,
        retrieved_at=retrieved_at,
        provenance=provenance,
        notes=notes,
    )
