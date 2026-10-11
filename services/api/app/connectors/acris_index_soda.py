"""ACRIS INDEX metadata connector - official NYC Open Data SODA datasets Real Property
Legals ``8h5j-fqxa`` and Real Property Master ``bnx9-e6tj`` (backlog DB-232; task M5-T158;
record NB-01).

This connector RETRIEVES the recorded-document INDEX for one tax lot - never a document
itself. The scanned instruments are viewer-gated and automation is explicitly prohibited
(``docs/SOURCE_ACCESS_REGISTRY.md`` SS 11.5); only the open-data index metadata is read here.
An index entry does NOT establish an instrument's contents (D-093; NB-01 stays
``access_blocked``): downstream code labels the lot-area figures as conditional drafts and
never concludes what the zoning lot is.

What it reads (metadata only), per the source registry draft
``docs/research/source-registry-drafts/acris-index.json``:

- Q1 Legals ``8h5j-fqxa`` by borough/block/lot: the subject lot's ``document_id`` rows and
  each row's ``partial_lot`` flag (P=partial, E=entire; dataset column description).
- Q2 Master ``bnx9-e6tj`` for those document ids (IN-list chunks of at most
  :data:`MAX_IN_LIST`): ``doc_type``, ``document_date``, ``recorded_datetime``, ``crfn``.
  The request NEVER asks for ``document_amt`` (a ``$select`` without it) and NEVER touches the
  ACRIS Parties dataset (grantor/grantee names).
- Q3 Legals for the ZONE / DECL / CERT document ids only: every lot each such document is
  indexed against (so the classifier can see other lots on the same block).
- Q4 the dataset maximum ``good_through_date`` (the "index up to date through" date).

The three document-type codes are PINNED in code (:data:`DOCUMENT_TYPE_DESCRIPTIONS`) from the
recorded Document Control Codes copy ``7isb-wh4c`` (NB-01 E3); there is NO live codes call. A
contract test checks the pinned descriptions against that recorded copy.

Fail-closed behaviour. The caller treats a raised :class:`AcrisIndexConnectorError` as the
classifier's ``NOT_READ`` state - "the index could not be read", NEVER "none found". The
connector raises (never returns a partial/guessed result) when: a request still fails after the
bounded retry budget; a body is not the documented shape or a required field is missing; the
page budget is reached (refusing silent truncation); or a subject document has no Master row
(so its type is unknown and a zoning-lot description could be missed).

The Master's ``recorded_borough`` is never used (it reads "1" on these Queens documents; NB-01).

Deterministic code only: no AI, no legal interpretation, no invented values. The reading of the
codes against ZR 12-10 is a labelled DRAFT and lives in the pure classifier
(:mod:`app.profile.zoning_lot_index`), not here.
"""

from __future__ import annotations

import json
import logging
import os
import re
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
    "CODES_DATASET_ID",
    "DOCUMENT_TYPE_DESCRIPTIONS",
    "LEGALS_BASE_URL",
    "LEGALS_DATASET_ID",
    "MASTER_BASE_URL",
    "MASTER_DATASET_ID",
    "MASTER_SELECT",
    "MAX_IN_LIST",
    "SOURCE_ID",
    "AcrisDocument",
    "AcrisIndexConnectorError",
    "AcrisLegalLot",
    "AcrisZoningLotIndexResult",
    "IncompleteIndexError",
    "PageBudgetExceededError",
    "RateLimitedError",
    "SchemaDriftError",
    "SourceTimeoutError",
    "SourceUnavailableError",
    "build_good_through_url",
    "build_legals_by_documents_url",
    "build_legals_by_lot_url",
    "build_master_url",
    "fetch_zoning_lot_index",
]

logger = logging.getLogger("app.connectors.acris_index_soda")

SOURCE_ID = "nyc-acris-index-metadata"
LEGALS_DATASET_ID = "8h5j-fqxa"
MASTER_DATASET_ID = "bnx9-e6tj"
CODES_DATASET_ID = "7isb-wh4c"
LEGALS_BASE_URL = f"https://data.cityofnewyork.us/resource/{LEGALS_DATASET_ID}.json"
MASTER_BASE_URL = f"https://data.cityofnewyork.us/resource/{MASTER_DATASET_ID}.json"
APP_TOKEN_ENV_VAR = "SOCRATA_APP_TOKEN"

# Schema-drift failure signature (shared Socrata behaviour; same as dof_sales_soda / pluto).
SCHEMA_DRIFT_ERROR_CODE = "query.soql.no-such-column"

# The three zoning-lot document-type codes, PINNED from the recorded Document Control Codes
# copy 7isb-wh4c (NB-01 E3). Only ZONE's description names a zoning lot; the draft classifier
# reads that against ZR 12-10. There is no live codes call; a contract test checks these three
# against the recorded copy fixture.
DOCUMENT_TYPE_DESCRIPTIONS: dict[str, str] = {
    "ZONE": "ZONING LOT DESCRIPTION",
    "DECL": "DECLARATION",
    "CERT": "CERTIFICATE",
}

# Master columns the connector reads. document_amt is DELIBERATELY ABSENT: the $select never
# requests it, and the Parties dataset (names) is never queried at all.
MASTER_SELECT = "document_id,doc_type,document_date,recorded_datetime,crfn,good_through_date"

# At most this many document ids per IN-list request (bounded query; registry governance).
MAX_IN_LIST = 50

# A document id is a plain ACRIS identifier (digits, or a BK_/FT_ prefixed id). Validated
# BEFORE it is placed inside a $where IN-list so a malformed id can never alter the query.
_DOCUMENT_ID_RE = re.compile(r"^[A-Za-z0-9_]{1,64}$")


# ---------------------------------------------------------------------------
# Typed error taxonomy (every one is fail-closed -> the classifier's NOT_READ)
# ---------------------------------------------------------------------------
class AcrisIndexConnectorError(Exception):
    """Base typed connector error. Any instance means the index could not be read in full;
    the caller fails closed to the ``NOT_READ`` state, never ``NONE_FOUND``."""

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


class RateLimitedError(AcrisIndexConnectorError):
    """HTTP 429 persisted through the bounded retry budget."""

    error_type = "rate_limited"


class SchemaDriftError(AcrisIndexConnectorError):
    """Dataset contract changed, a response is not the documented shape, or a required field is
    missing. Surfaced for alerting; never blindly retried, never guessed around."""

    error_type = "schema_drift"


class SourceTimeoutError(AcrisIndexConnectorError):
    """Connect/read timeout persisted through the retry budget."""

    error_type = "timeout"


class SourceUnavailableError(AcrisIndexConnectorError):
    """Network failure, 5xx persisted through retries, or an unexpected HTTP status."""

    error_type = "source_unavailable"


class PageBudgetExceededError(AcrisIndexConnectorError):
    """The page budget was reached while the upstream may hold more rows. Refusing silent
    truncation is itself a fail-closed signal (the lot's documents are read in full or not at
    all)."""

    error_type = "page_budget_exhausted"


class IncompleteIndexError(AcrisIndexConnectorError):
    """A subject document returned by Legals has no Master row, so its document type is unknown
    and a zoning-lot description could be missed. Fail closed rather than classify on a partial
    index."""

    error_type = "incomplete_index"


# ---------------------------------------------------------------------------
# Typed records (index metadata only)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AcrisLegalLot:
    """One Legals index row: a lot a document is indexed against."""

    borough: str
    block: str
    lot: str
    partial_lot: str | None  # "P" (partial) or "E" (entire); dataset column description

    @property
    def bbl(self) -> str | None:
        """The canonical 10-digit BBL for this lot, or None when the components are not a
        well-formed BBL (never guessed)."""
        try:
            from app.connectors.bbl import bbl_from_components

            return bbl_from_components(self.borough, self.block, self.lot)
        except Exception:  # noqa: BLE001 - a malformed row yields no bbl, never a raise here
            return None


@dataclass(frozen=True)
class AcrisDocument:
    """One recorded document from the subject lot's index, enriched with its type (Master) and
    every lot it is indexed against (Legals Q3). ``document_amt`` is never read."""

    document_id: str
    doc_type: str | None
    document_date: str | None  # ISO calendar date, or None
    recorded_datetime: str | None  # ISO calendar date, or None
    crfn: str | None  # City Register file number, or None
    subject_partial_lot: str | None  # the subject lot's partial_lot flag on this document
    indexed_lots: tuple[AcrisLegalLot, ...]  # every lot the document is indexed against (Q3)


@dataclass(frozen=True)
class AcrisZoningLotIndexResult:
    """The recorded-document index read for one subject tax lot.

    ``documents`` holds the subject's ZONE / DECL / CERT documents only (the zoning-lot-relevant
    types); other recorded documents (deeds, mortgages, ...) are intentionally not carried.
    ``as_of_date`` is the dataset's maximum ``good_through_date`` (the "index up to date
    through" date). The classifier reads this result; the connector concludes nothing.
    """

    subject_bbl: str
    subject_borough: str
    subject_block: str
    subject_lot: str
    documents: tuple[AcrisDocument, ...]
    as_of_date: str | None
    correlation_id: str
    provenance: dict


# ---------------------------------------------------------------------------
# URL builders (literal, so a recorded-fixture transport can route by exact url)
# ---------------------------------------------------------------------------
def _q(value: str) -> str:
    """Percent-encode one query-string value, matching the recorded fixture urls."""
    return urllib.parse.quote(value, safe="")


def _validate_document_ids(document_ids: list[str]) -> None:
    for document_id in document_ids:
        if not isinstance(document_id, str) or not _DOCUMENT_ID_RE.match(document_id):
            raise ValueError(f"malformed ACRIS document id: {document_id!r}")


def build_legals_by_lot_url(
    borough: int | str, block: int | str, lot: int | str, *, limit: int, offset: int
) -> str:
    """Q1: every Legals row for the subject tax lot, stably ordered for paging."""
    return (
        f"{LEGALS_BASE_URL}?borough={borough}&block={block}&lot={lot}"
        f"&$order=document_id&$limit={limit}&$offset={offset}"
    )


def build_master_url(document_ids: list[str], *, limit: int, offset: int) -> str:
    """Q2: Master rows for ``document_ids`` (one IN-list chunk), ``$select``ing only the read
    columns so ``document_amt`` is never requested."""
    _validate_document_ids(document_ids)
    where = "document_id in(" + ",".join(f"'{d}'" for d in document_ids) + ")"
    return (
        f"{MASTER_BASE_URL}?$where={_q(where)}&$select={_q(MASTER_SELECT)}"
        f"&$order=document_id&$limit={limit}&$offset={offset}"
    )


def build_legals_by_documents_url(document_ids: list[str], *, limit: int, offset: int) -> str:
    """Q3: every Legals row (so every lot) for the given document ids (one IN-list chunk)."""
    _validate_document_ids(document_ids)
    where = "document_id in(" + ",".join(f"'{d}'" for d in document_ids) + ")"
    return (
        f"{LEGALS_BASE_URL}?$where={_q(where)}"
        f"&$order=document_id,lot&$limit={limit}&$offset={offset}"
    )


def build_good_through_url() -> str:
    """Q4: the dataset maximum ``good_through_date`` (the index "up to date through" date)."""
    return f"{LEGALS_BASE_URL}?$select={_q('max(good_through_date)')}"


# ---------------------------------------------------------------------------
# Normalisation helpers (pure)
# ---------------------------------------------------------------------------
def _text(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _date(value: Any) -> str | None:
    """The ISO calendar date from a SODA floating_timestamp
    ("2022-02-08T00:00:00.000" -> "2022-02-08"), or None."""
    text = _text(value)
    return text[:10] if text is not None else None


def _required_text(row: dict, key: str, url: str, correlation_id: str) -> str:
    value = _text(row.get(key))
    if value is None:
        raise SchemaDriftError(
            f"ACRIS row is missing the required field {key!r}",
            correlation_id=correlation_id,
            detail={"url": url, "field": key},
        )
    return value


# ---------------------------------------------------------------------------
# Transport + paging
# ---------------------------------------------------------------------------
def _build_headers(app_token: str | None) -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if app_token:
        headers["X-App-Token"] = app_token
    return headers


def _resolve_app_token(app_token: str | None) -> str | None:
    return app_token if app_token is not None else (os.environ.get(APP_TOKEN_ENV_VAR) or None)


def _classify_400(body: str) -> str | None:
    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, ValueError, RecursionError):
        return None
    code = parsed.get("errorCode") if isinstance(parsed, dict) else None
    return code if isinstance(code, str) else None


@dataclass(frozen=True)
class _FetchConfig:
    transport: Transport
    app_token: str | None
    timeout: float
    max_attempts: int
    backoff_base: float
    page_size: int
    max_pages: int
    sleep: Callable[[float], None]
    correlation_id: str


def _request(url: str, cfg: _FetchConfig) -> TransportResponse:
    def _raise_for_unexpected_status(response: TransportResponse) -> NoReturn:
        if response.status == 400:
            error_code = _classify_400(response.body)
            if error_code == SCHEMA_DRIFT_ERROR_CODE:
                raise SchemaDriftError(
                    "SODA rejected a column reference: schema drift signature "
                    f"({SCHEMA_DRIFT_ERROR_CODE})",
                    correlation_id=cfg.correlation_id,
                    detail={"http_status": 400, "url": url},
                )
            raise SourceUnavailableError(
                "SODA rejected the request (HTTP 400, not the schema-drift signature)",
                correlation_id=cfg.correlation_id,
                detail={"http_status": 400, "url": url},
            )
        raise SourceUnavailableError(
            f"unexpected HTTP status {response.status} from SODA endpoint",
            correlation_id=cfg.correlation_id,
            detail={"http_status": response.status, "url": url},
        )

    return request_with_retry(
        url,
        transport=cfg.transport,
        headers=_build_headers(cfg.app_token),
        timeout=cfg.timeout,
        max_attempts=cfg.max_attempts,
        hooks=standard_retry_hooks(
            logger=logger,
            log_label="acris_index_soda",
            correlation_id=cfg.correlation_id,
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
        compute_delay=fixed_exponential_delay(cfg.backoff_base),
        sleep=cfg.sleep,
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


def _fetch_all_pages(
    build_url: Callable[[int, int], str], cfg: _FetchConfig, *, requested_urls: list[str]
) -> list[dict]:
    """Page through one query with ``$limit``/``$offset`` until a short page ends it; fail
    closed (:class:`PageBudgetExceededError`) if the page budget is reached first."""
    rows: list[dict] = []
    for page in range(cfg.max_pages):
        url = build_url(cfg.page_size, page * cfg.page_size)
        requested_urls.append(url)
        response = _request(url, cfg)
        page_rows = _parse_rows(response.body, url, cfg.correlation_id)
        rows.extend(page_rows)
        if len(page_rows) < cfg.page_size:
            return rows
    raise PageBudgetExceededError(
        "ACRIS page budget reached while more rows may remain; refusing silent truncation",
        correlation_id=cfg.correlation_id,
        detail={"max_pages": cfg.max_pages, "page_size": cfg.page_size, "collected": len(rows)},
    )


def _chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def _fetch_by_document_ids(
    document_ids: list[str],
    build_url: Callable[[list[str], int, int], str],
    cfg: _FetchConfig,
    *,
    requested_urls: list[str],
) -> list[dict]:
    """Fetch rows for ``document_ids`` in IN-list chunks of at most :data:`MAX_IN_LIST`."""
    rows: list[dict] = []
    for chunk in _chunks(document_ids, MAX_IN_LIST):
        rows.extend(
            _fetch_all_pages(
                lambda limit, offset, chunk=chunk: build_url(chunk, limit, offset),
                cfg,
                requested_urls=requested_urls,
            )
        )
    return rows


# ---------------------------------------------------------------------------
# Fetch orchestration (Q1 -> Q2 -> Q3 -> Q4)
# ---------------------------------------------------------------------------
def fetch_zoning_lot_index(
    bbl: str,
    *,
    transport: Transport = urllib_transport,
    app_token: str | None = None,
    timeout: float = 10.0,
    max_attempts: int = 3,
    backoff_base: float = 0.5,
    page_size: int = 1000,
    max_pages: int = 20,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    correlation_id: str | None = None,
) -> AcrisZoningLotIndexResult:
    """Read the ACRIS index for the subject tax lot and return its ZONE/DECL/CERT documents.

    The BBL is validated (:func:`app.connectors.bbl.normalize_bbl`) BEFORE any network call; a
    malformed BBL raises ``BBLValidationError`` (``validation_error``) and no request is made.

    Raises:
        BBLValidationError: ``bbl`` is not a well-formed BBL.
        AcrisIndexConnectorError: any fail-closed condition (see the module docstring). The
            caller maps every such error to the classifier's ``NOT_READ`` state.
    """
    normalized = normalize_bbl(bbl)
    correlation_id = correlation_id or uuid.uuid4().hex
    cfg = _FetchConfig(
        transport=transport,
        app_token=_resolve_app_token(app_token),
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        page_size=page_size,
        max_pages=max_pages,
        sleep=sleep,
        correlation_id=correlation_id,
    )
    borough, block, lot = normalized.borough, normalized.block, normalized.lot
    requested_urls: list[str] = []

    # Q1: the subject lot's documents.
    legals_rows = _fetch_all_pages(
        lambda limit, offset: build_legals_by_lot_url(
            borough, block, lot, limit=limit, offset=offset
        ),
        cfg,
        requested_urls=requested_urls,
    )
    subject_partial: dict[str, str | None] = {}
    for row in legals_rows:
        document_id = _required_text(row, "document_id", LEGALS_BASE_URL, correlation_id)
        # One row per (document, lot); for the subject lot there is one row per document.
        subject_partial[document_id] = _text(row.get("partial_lot"))
    subject_document_ids = sorted(subject_partial)

    # Q2: the Master rows for every subject document (fail closed if any is missing).
    master_rows = (
        _fetch_by_document_ids(
            subject_document_ids, _master_url, cfg, requested_urls=requested_urls
        )
        if subject_document_ids
        else []
    )
    master_by_id: dict[str, dict] = {}
    for row in master_rows:
        document_id = _required_text(row, "document_id", MASTER_BASE_URL, correlation_id)
        master_by_id[document_id] = row
    missing = [d for d in subject_document_ids if d not in master_by_id]
    if missing:
        raise IncompleteIndexError(
            "a subject document has no Master row; the document type is unknown",
            correlation_id=correlation_id,
            detail={"missing_document_ids": missing},
        )

    # Keep only the zoning-lot-relevant types (ZONE / DECL / CERT).
    relevant_ids = [
        document_id
        for document_id in subject_document_ids
        if _required_text(master_by_id[document_id], "doc_type", MASTER_BASE_URL, correlation_id)
        in DOCUMENT_TYPE_DESCRIPTIONS
    ]

    # Q3: every lot each relevant document is indexed against.
    lots_by_document: dict[str, list[AcrisLegalLot]] = {d: [] for d in relevant_ids}
    if relevant_ids:
        q3_rows = _fetch_by_document_ids(
            relevant_ids, _legals_by_documents_url, cfg, requested_urls=requested_urls
        )
        for row in q3_rows:
            document_id = _required_text(row, "document_id", LEGALS_BASE_URL, correlation_id)
            if document_id not in lots_by_document:
                continue
            lots_by_document[document_id].append(
                AcrisLegalLot(
                    borough=_required_text(row, "borough", LEGALS_BASE_URL, correlation_id),
                    block=_required_text(row, "block", LEGALS_BASE_URL, correlation_id),
                    lot=_required_text(row, "lot", LEGALS_BASE_URL, correlation_id),
                    partial_lot=_text(row.get("partial_lot")),
                )
            )

    # Q4: the index "up to date through" date (informational; a missing value is not fatal).
    as_of_date = _fetch_good_through(cfg, requested_urls=requested_urls)

    documents = tuple(
        AcrisDocument(
            document_id=document_id,
            doc_type=_text(master_by_id[document_id].get("doc_type")),
            document_date=_date(master_by_id[document_id].get("document_date")),
            recorded_datetime=_date(master_by_id[document_id].get("recorded_datetime")),
            crfn=_text(master_by_id[document_id].get("crfn")),
            subject_partial_lot=subject_partial.get(document_id),
            indexed_lots=tuple(lots_by_document.get(document_id, ())),
        )
        for document_id in relevant_ids
    )
    retrieved_at = clock().strftime("%Y-%m-%dT%H:%M:%SZ")
    provenance = {
        "source_id": SOURCE_ID,
        "legals_dataset_id": LEGALS_DATASET_ID,
        "master_dataset_id": MASTER_DATASET_ID,
        "retrieved_at": retrieved_at,
        "request_urls": tuple(requested_urls),
        "subject_document_count": len(subject_document_ids),
        "relevant_document_count": len(documents),
    }
    return AcrisZoningLotIndexResult(
        subject_bbl=normalized.canonical,
        subject_borough=str(borough),
        subject_block=str(block),
        subject_lot=str(lot),
        documents=documents,
        as_of_date=as_of_date,
        correlation_id=correlation_id,
        provenance=provenance,
    )


def _master_url(document_ids: list[str], limit: int, offset: int) -> str:
    return build_master_url(document_ids, limit=limit, offset=offset)


def _legals_by_documents_url(document_ids: list[str], limit: int, offset: int) -> str:
    return build_legals_by_documents_url(document_ids, limit=limit, offset=offset)


def _fetch_good_through(cfg: _FetchConfig, *, requested_urls: list[str]) -> str | None:
    url = build_good_through_url()
    requested_urls.append(url)
    response = _request(url, cfg)
    rows = _parse_rows(response.body, url, cfg.correlation_id)
    if not rows:
        return None
    return _date(rows[0].get("max_good_through_date"))
