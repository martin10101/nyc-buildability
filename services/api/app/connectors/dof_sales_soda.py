"""DOF sales SODA connector - official NYC Open Data dataset ``w2pb-icbu`` (queue item
B-11, plan section 11b "Comparable sales"; Lane B, directive D-090).

The dataset is the DOF "NYC Citywide Annualized Calendar Sales Update" (publisher:
Department of Finance). It is the official record of property sales in New York City;
this connector RETRIEVES those sale rows and maps each one to a typed, sourced, dated
:class:`SaleRecord`. It makes NO product judgement about which rows are "comparable"
(that disclosed selection is ``app.profile.parity.comparable_sales``, a separate pure
module) and it is NEVER a valuation: it computes no price-per-square-foot, no average,
and no estimate. It only reads and normalises the publisher's own fields.

Field names, types and meanings come ONLY from the official dataset metadata recorded in
``docs/research/dof-sales-comparables-2026-10-02.md`` (``/api/views/w2pb-icbu.json``,
retrieved 2026-10-02, with its sha256 and the verbatim column descriptions). No field is
guessed (platform principle 3 / PRD sections 2, 9, 23.2). SODA omits null fields per
record, so an absent key means the value is unknown/absent, never zero and never
fabricated.

Responsibilities:

- ``fetch_sales_by_bbl``: the sale rows recorded for one tax lot (BBL validated BEFORE any
  network call).
- ``fetch_comparable_candidates``: candidate rows for a disclosed query - the same DOF
  ``neighborhood`` and ``building_class_category`` the subject's own recorded sale carries.
  The connector does not decide those inputs; the caller supplies them (the subject's
  recorded values or an owner-chosen pair).
- ``SaleRecord``: one typed, normalised row with its raw row and its provenance.
- Typed error taxonomy (``validation_error`` via :mod:`app.connectors.bbl`,
  ``rate_limited``, ``schema_drift``, ``timeout``, ``source_unavailable``), correlation
  ids, and no stack traces in payloads.
- Bounded retry on 429 / 5xx / timeout / network failure only, through the shared accepted
  retry engine (:mod:`app.resilience.transport`). The ``query.soql.no-such-column`` 400 is
  the schema-drift signature and is never blindly retried.
- Optional ``SOCRATA_APP_TOKEN`` sent as ``X-App-Token``: never required, never logged.

Deterministic code only: no AI, no legal interpretation, no invented values. Eligibility,
valuation and any "remaining capacity" remain out of this layer entirely.
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.parse
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, NoReturn

from app.connectors.bbl import normalize_bbl
from app.resilience.transport import (
    Transport,
    TransportResponse,
    fixed_exponential_delay,
    request_with_retry,
    standard_retry_hooks,
    urllib_transport,
)

__all__ = [
    "APP_TOKEN_ENV_VAR",
    "BASE_URL",
    "BUILDING_CLASS_CATEGORY_FIELD",
    "DATASET_ID",
    "DATASET_NAME",
    "NEIGHBORHOOD_FIELD",
    "SALE_COLUMNS",
    "SOURCE_ID",
    "DofSalesConnectorError",
    "DofSalesResult",
    "RateLimitedError",
    "SaleRecord",
    "SchemaDriftError",
    "SourceTimeoutError",
    "SourceUnavailableError",
    "build_by_bbl_url",
    "build_candidates_url",
    "fetch_comparable_candidates",
    "fetch_sales_by_bbl",
]

logger = logging.getLogger("app.connectors.dof_sales_soda")

SOURCE_ID = "nyc-dof-annualized-sales-soda"
DATASET_ID = "w2pb-icbu"
DATASET_NAME = f"DOF NYC Citywide Annualized Calendar Sales ({DATASET_ID})"
BASE_URL = f"https://data.cityofnewyork.us/resource/{DATASET_ID}.json"
API_VIEWS_URL = f"https://data.cityofnewyork.us/api/views/{DATASET_ID}.json"
APP_TOKEN_ENV_VAR = "SOCRATA_APP_TOKEN"

# Schema-drift failure signature (shared Socrata behaviour; same as pluto_soda / dtm).
SCHEMA_DRIFT_ERROR_CODE = "query.soql.no-such-column"

# The data-vintage header SODA stamps on every response (the dataset's own
# last-modified time, distinct from the HTTP cache header). Recorded verbatim as the
# sale rows' "dated" provenance; app.profile.data_versions can pin it later (B-06).
VINTAGE_HEADER = "x-soda2-truth-last-modified"

NEIGHBORHOOD_FIELD = "neighborhood"
BUILDING_CLASS_CATEGORY_FIELD = "building_class_category"

# The 29 columns the publisher serves, recorded verbatim from the official metadata and the
# X-SODA2-Fields response header (docs/research/dof-sales-comparables-2026-10-02.md). Used to
# flag drift (an unknown key is surfaced, never trusted) - never to fabricate an absent one.
SALE_COLUMNS: frozenset[str] = frozenset({
    "borough", "neighborhood", "building_class_category", "tax_class_as_of_final_roll",
    "block", "lot", "ease_ment", "building_class_as_of_final", "address", "apartment_number",
    "zip_code", "residential_units", "commercial_units", "total_units", "land_square_feet",
    "gross_square_feet", "year_built", "tax_class_at_time_of_sale", "building_class_at_time_of",
    "sale_price", "sale_date", "latitude", "longitude", "community_board", "council_district",
    "bin", "bbl", "census_tract_2020", "nta",
})


# ---------------------------------------------------------------------------
# Typed error taxonomy
# ---------------------------------------------------------------------------
class DofSalesConnectorError(Exception):
    """Base typed connector error."""

    error_type = "source_unavailable"

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


class RateLimitedError(DofSalesConnectorError):
    """HTTP 429 persisted through the bounded retry budget."""

    error_type = "rate_limited"


class SchemaDriftError(DofSalesConnectorError):
    """Dataset contract changed, or a response is not the documented shape. Surfaced for
    alerting; never blindly retried, never guessed around."""

    error_type = "schema_drift"


class SourceTimeoutError(DofSalesConnectorError):
    """Connect/read timeout persisted through the retry budget."""

    error_type = "timeout"


class SourceUnavailableError(DofSalesConnectorError):
    """Network failure, 5xx persisted through retries, or an unexpected HTTP status."""

    error_type = "source_unavailable"


# ---------------------------------------------------------------------------
# Typed record
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SaleRecord:
    """One DOF sale row, normalised, with its raw row and its provenance.

    Every value is the publisher's own field (see the research note); nothing is derived.
    ``land_square_feet`` / ``gross_square_feet`` are the publisher's TEXT fields parsed to
    an int (commas stripped); a blank or unparseable size is ``None`` and a recorded ``0``
    is kept as ``0`` (the selection filter treats a zero/absent size as "size not
    recorded", never as a real zero). ``sale_price`` is the recorded number, kept VERBATIM
    including ``0`` - per the official ``sale_date`` description "A $0 sale price indicates
    that there was a transfer of ownership without a cash consideration", so a $0 row is a
    non-arms-length transfer, not a market sale. ``sale_date`` is the ISO calendar date.

    Attributes:
        bbl: the tax lot (10-digit BBL) when the row carries a well-formed one, else None.
        source: a provenance dict shared by every row of one fetch (source id, dataset id
            and name, the exact request url, retrieved_at, the dataset data vintage).
        raw: the publisher's row verbatim (full provenance; nothing is discarded).
    """

    bbl: str | None
    borough: str | None
    neighborhood: str | None
    block: str | None
    lot: str | None
    address: str | None
    zip_code: str | None
    building_class_category: str | None
    building_class_at_time_of_sale: str | None
    residential_units: int | None
    commercial_units: int | None
    total_units: int | None
    year_built: int | None
    land_square_feet: int | None
    gross_square_feet: int | None
    sale_price: int | None
    sale_date: str | None
    source: dict
    raw: dict

    @property
    def is_cash_sale(self) -> bool:
        """A recorded sale with a positive price (not a $0 non-arms-length transfer and not
        an absent price). The selection filter uses this to exclude $0 transfers."""
        return self.sale_price is not None and self.sale_price > 0

    @property
    def has_recorded_size(self) -> bool:
        """A usable gross square footage (recorded, positive). A recorded 0 or an absent
        value is NOT a usable size (DOF leaves it 0/blank for many lots)."""
        return self.gross_square_feet is not None and self.gross_square_feet > 0


@dataclass(frozen=True)
class DofSalesResult:
    """The outcome of one fetch: the typed rows and the query provenance.

    ``records`` is the full retrieved set in a stable order (sale_date descending, then bbl,
    then the raw row index), never narrowed - selection is a separate disclosed step.
    """

    query_kind: str
    request_url: str
    retrieved_at: str
    dataset_last_modified: str | None
    correlation_id: str
    records: tuple[SaleRecord, ...]
    unknown_columns: tuple[str, ...]
    provenance: dict


# ---------------------------------------------------------------------------
# URL builders (literal, so a recorded-fixture transport can route by exact url)
# ---------------------------------------------------------------------------
def _q(value: str) -> str:
    """Percent-encode one query-string value (spaces -> %20), matching the recorded
    fixture urls byte-for-byte."""
    return urllib.parse.quote(value, safe="")


# Stable server-side order so a live fetch returns the most recent sales first; the parser
# re-sorts deterministically regardless, but this keeps the $limit page meaningful.
_ORDER = "$order=sale_date%20DESC"


def build_by_bbl_url(bbl: str, *, row_limit: int) -> str:
    """The SODA url for every recorded sale of one tax lot."""
    return f"{BASE_URL}?bbl={bbl}&{_ORDER}&$limit={row_limit}"


def build_candidates_url(neighborhood: str, building_class_category: str, *, row_limit: int) -> str:
    """The SODA url for candidate rows sharing one DOF neighborhood and building-class
    category (the disclosed "similar type" query input the caller supplies)."""
    return (
        f"{BASE_URL}?{NEIGHBORHOOD_FIELD}={_q(neighborhood)}"
        f"&{BUILDING_CLASS_CATEGORY_FIELD}={_q(building_class_category)}"
        f"&{_ORDER}&$limit={row_limit}"
    )


# ---------------------------------------------------------------------------
# Normalisation helpers (pure)
# ---------------------------------------------------------------------------
def _text(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _int(value: Any) -> int | None:
    """A SODA number/text parsed to int, or None. Accepts "0", "20", "3700000", "5,091",
    "1234.0"; rejects blanks and non-numeric text. Never raises."""
    text = value.strip().replace(",", "") if isinstance(value, str) else value
    if isinstance(text, bool):
        return None
    if isinstance(text, int):
        return text
    if isinstance(text, float):
        return int(text) if text.is_integer() else None
    if not isinstance(text, str) or not text:
        return None
    try:
        return int(text)
    except ValueError:
        try:
            as_float = float(text)
        except ValueError:
            return None
        return int(as_float) if as_float.is_integer() else None


def _date(value: Any) -> str | None:
    """The ISO calendar date from a SODA floating_timestamp ("2018-01-18T00:00:00.000" ->
    "2018-01-18"), or None."""
    text = _text(value)
    if text is None:
        return None
    return text[:10]


def _row_bbl(value: Any) -> str | None:
    """A well-formed 10-digit BBL from the row's ``bbl`` field, or None (a row may carry a
    blank or malformed bbl - one candidate row does; it is kept as a record with bbl
    None, never dropped and never guessed)."""
    text = _text(value)
    if text is None:
        return None
    try:
        return normalize_bbl(text).canonical
    except ValueError:
        return None


def _to_record(row: dict, source: dict) -> SaleRecord:
    return SaleRecord(
        bbl=_row_bbl(row.get("bbl")),
        borough=_text(row.get("borough")),
        neighborhood=_text(row.get("neighborhood")),
        block=_text(row.get("block")),
        lot=_text(row.get("lot")),
        address=_text(row.get("address")),
        zip_code=_text(row.get("zip_code")),
        building_class_category=_text(row.get("building_class_category")),
        building_class_at_time_of_sale=_text(row.get("building_class_at_time_of")),
        residential_units=_int(row.get("residential_units")),
        commercial_units=_int(row.get("commercial_units")),
        total_units=_int(row.get("total_units")),
        year_built=_int(row.get("year_built")),
        land_square_feet=_int(row.get("land_square_feet")),
        gross_square_feet=_int(row.get("gross_square_feet")),
        sale_price=_int(row.get("sale_price")),
        sale_date=_date(row.get("sale_date")),
        source=source,
        raw=dict(row),
    )


def _sort_key(item: tuple[int, SaleRecord]) -> tuple[str, str, int]:
    index, record = item
    # Most recent first; "" sorts before any date, so undated rows trail (negated via the
    # reverse flag handled by the caller). Stable tie-break by bbl then original index.
    return (record.sale_date or "", record.bbl or "", -index)


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------
def _build_headers(app_token: str | None) -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if app_token:
        headers["X-App-Token"] = app_token
    return headers


def _classify_400(body: str) -> str | None:
    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, ValueError, RecursionError):
        return None
    code = parsed.get("errorCode") if isinstance(parsed, dict) else None
    return code if isinstance(code, str) else None


def _request(
    url: str,
    *,
    transport: Transport,
    app_token: str | None,
    timeout: float,
    max_attempts: int,
    backoff_base: float,
    sleep: Callable[[float], None],
    correlation_id: str,
) -> TransportResponse:
    """Bounded retry on 429/5xx/timeout/network failure only; the no-such-column 400 is
    typed schema drift (never retried) and every other 400 is typed source-unavailable."""

    def _raise_for_unexpected_status(response: TransportResponse) -> NoReturn:
        if response.status == 400:
            error_code = _classify_400(response.body)
            if error_code == SCHEMA_DRIFT_ERROR_CODE:
                raise SchemaDriftError(
                    "SODA rejected a column reference: schema drift signature "
                    f"({SCHEMA_DRIFT_ERROR_CODE})",
                    correlation_id=correlation_id,
                    detail={"http_status": 400, "url": url},
                )
            raise SourceUnavailableError(
                "SODA rejected the request (HTTP 400, not the schema-drift signature)",
                correlation_id=correlation_id,
                detail={"http_status": 400, "url": url},
            )
        raise SourceUnavailableError(
            f"unexpected HTTP status {response.status} from SODA endpoint",
            correlation_id=correlation_id,
            detail={"http_status": response.status, "url": url},
        )

    return request_with_retry(
        url,
        transport=transport,
        headers=_build_headers(app_token),
        timeout=timeout,
        max_attempts=max_attempts,
        hooks=standard_retry_hooks(
            logger=logger,
            log_label="dof_sales_soda",
            correlation_id=correlation_id,
            url=url,
            sanitize_network_reason=lambda reason: reason,
            rate_limited_error=RateLimitedError,
            rate_limited_message=(
                "SODA throttled the request (HTTP 429) and the retry budget is exhausted; "
                "configure SOCRATA_APP_TOKEN to leave the shared tokenless pool"
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


def _parse_rows(body: str, url: str, correlation_id: str) -> list[dict]:
    try:
        records = json.loads(body)
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


def _unknown_columns(rows: list[dict]) -> tuple[str, ...]:
    seen: set[str] = set()
    for row in rows:
        seen.update(row.keys())
    return tuple(sorted(seen - SALE_COLUMNS))


def _fetch(
    url: str,
    *,
    query_kind: str,
    transport: Transport,
    app_token: str | None,
    timeout: float,
    max_attempts: int,
    backoff_base: float,
    sleep: Callable[[float], None],
    clock: Callable[[], datetime],
    correlation_id: str,
) -> DofSalesResult:
    response = _request(
        url,
        transport=transport,
        app_token=app_token,
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        sleep=sleep,
        correlation_id=correlation_id,
    )
    rows = _parse_rows(response.body, url, correlation_id)
    # Stamp retrieved_at AFTER the successful response (the pluto_soda / dtm precedent).
    retrieved_at = clock().strftime("%Y-%m-%dT%H:%M:%SZ")
    vintage = response.headers.get(VINTAGE_HEADER)
    dataset_last_modified = vintage if isinstance(vintage, str) and vintage.strip() else None
    source = {
        "kind": "city_dataset",
        "source_id": SOURCE_ID,
        "dataset_id": DATASET_ID,
        "dataset": DATASET_NAME,
        "request_url": url,
        "retrieved_at": retrieved_at,
        "dataset_last_modified": dataset_last_modified,
    }
    indexed = list(enumerate(_to_record(row, source) for row in rows))
    indexed.sort(key=_sort_key, reverse=True)
    records = tuple(record for _, record in indexed)
    provenance = {
        "source_id": SOURCE_ID,
        "dataset_id": DATASET_ID,
        "dataset": DATASET_NAME,
        "request_url": url,
        "retrieved_at": retrieved_at,
        "dataset_last_modified": dataset_last_modified,
        "query_kind": query_kind,
        "record_count": len(records),
    }
    return DofSalesResult(
        query_kind=query_kind,
        request_url=url,
        retrieved_at=retrieved_at,
        dataset_last_modified=dataset_last_modified,
        correlation_id=correlation_id,
        records=records,
        unknown_columns=_unknown_columns(rows),
        provenance=provenance,
    )


def _resolve_app_token(app_token: str | None) -> str | None:
    return app_token if app_token is not None else (os.environ.get(APP_TOKEN_ENV_VAR) or None)


def fetch_sales_by_bbl(
    bbl: str,
    *,
    transport: Transport = urllib_transport,
    app_token: str | None = None,
    row_limit: int = 50,
    timeout: float = 10.0,
    max_attempts: int = 3,
    backoff_base: float = 0.5,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    correlation_id: str | None = None,
) -> DofSalesResult:
    """Every recorded DOF sale for tax lot ``bbl``.

    The BBL is validated (:func:`app.connectors.bbl.normalize_bbl`) BEFORE any network
    call; a malformed BBL raises ``BBLValidationError`` (``validation_error``) and no
    request is made. An empty result (``records == ()``) is a legitimate no-sale outcome.

    Raises:
        BBLValidationError: ``bbl`` is not a well-formed BBL.
        DofSalesConnectorError: a typed transport/schema failure.
    """
    canonical = normalize_bbl(bbl).canonical
    correlation_id = correlation_id or uuid.uuid4().hex
    url = build_by_bbl_url(canonical, row_limit=row_limit)
    return _fetch(
        url,
        query_kind="bbl",
        transport=transport,
        app_token=_resolve_app_token(app_token),
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        sleep=sleep,
        clock=clock,
        correlation_id=correlation_id,
    )


def fetch_comparable_candidates(
    neighborhood: str,
    building_class_category: str,
    *,
    transport: Transport = urllib_transport,
    app_token: str | None = None,
    row_limit: int = 200,
    timeout: float = 10.0,
    max_attempts: int = 3,
    backoff_base: float = 0.5,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    correlation_id: str | None = None,
) -> DofSalesResult:
    """Candidate sale rows sharing one DOF ``neighborhood`` and ``building_class_category``.

    These two inputs are the disclosed "similar type" query the caller supplies (the
    subject's own recorded values, or an owner-chosen pair). The connector makes no
    judgement about them and does NOT narrow by size - that is the disclosed selection
    step in ``app.profile.parity.comparable_sales``. The result is never a valuation.

    Raises:
        ValueError: ``neighborhood`` or ``building_class_category`` is blank.
        DofSalesConnectorError: a typed transport/schema failure.
    """
    if not isinstance(neighborhood, str) or not neighborhood.strip():
        raise ValueError("neighborhood must be non-empty text")
    if not isinstance(building_class_category, str) or not building_class_category.strip():
        raise ValueError("building_class_category must be non-empty text")
    correlation_id = correlation_id or uuid.uuid4().hex
    url = build_candidates_url(
        neighborhood.strip(), building_class_category.strip(), row_limit=row_limit
    )
    return _fetch(
        url,
        query_kind="neighborhood_building_class",
        transport=transport,
        app_token=_resolve_app_token(app_token),
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        sleep=sleep,
        clock=clock,
        correlation_id=correlation_id,
    )
