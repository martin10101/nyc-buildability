"""ACRIS index connector (backlog DB-232; task M5-T158; record NB-01). Offline: every test
replays the recorded 215-16 Northern benchmark fixtures through a url-routed fake transport, or
drives a controlled status/timeout transport for the failure paths. No live call is ever made.

Expected values come from the recorded source data and the ACRIS Document Control Codes, never
from a program run. The connector reads INDEX METADATA ONLY and concludes nothing about the
zoning lot (that draft reading is the pure classifier's job).
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.connectors.acris_index_soda import (
    APP_TOKEN_ENV_VAR,
    DOCUMENT_TYPE_DESCRIPTIONS,
    LEGALS_BASE_URL,
    MASTER_BASE_URL,
    MASTER_SELECT,
    IncompleteIndexError,
    PageBudgetExceededError,
    RateLimitedError,
    SchemaDriftError,
    SourceTimeoutError,
    SourceUnavailableError,
    build_good_through_url,
    build_legals_by_documents_url,
    build_legals_by_lot_url,
    build_master_url,
    fetch_zoning_lot_index,
)
from app.connectors.bbl import BBLValidationError
from app.profile.zoning_lot_index import ZoningLotIndexState, classify_zoning_lot_index
from app.resilience.transport import TransportResponse, TransportTimeout

PACK = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern"
NORTHERN_BBL = "4073340070"
FIXED_CLOCK = lambda: datetime(2026, 10, 11, 12, 0, 0, tzinfo=UTC)  # noqa: E731
FIXED_CORR = "corr-t158-test"

Q1_FILE = "acris_index_legals_8h5j-fqxa_lot_4-7334-70.json"
Q2_FILE = "acris_index_master_bnx9-e6tj_subject_docs.json"
Q3_FILE = "acris_index_legals_8h5j-fqxa_zone_decl_cert.json"
Q4_FILE = "acris_index_legals_8h5j-fqxa_good_through.json"
CODES_FILE = "acris_index_doc_control_codes_7isb-wh4c.json"

SUBJECT_IDS = sorted([
    "2018013000919001", "2018013000919002", "2022020201551001", "2022020201551002",
    "2022031600431001", "2024011000700001", "2024011000700002",
])
ZDC_IDS = sorted(["2022020201551001", "2022020201551002", "2022031600431001"])

Q1_URL = build_legals_by_lot_url(4, 7334, 70, limit=1000, offset=0)
Q2_URL = build_master_url(SUBJECT_IDS, limit=1000, offset=0)
Q3_URL = build_legals_by_documents_url(ZDC_IDS, limit=1000, offset=0)
Q4_URL = build_good_through_url()


def _body(name: str) -> str:
    return (PACK / name).read_text(encoding="utf-8")


class RoutedTransport:
    """URL-routed fake transport. Records every requested url; an unmapped url raises."""

    def __init__(self, routes: dict[str, TransportResponse]):
        self.routes = routes
        self.requested_urls: list[str] = []
        self.requested_headers: list[dict] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.requested_urls.append(url)
        self.requested_headers.append(dict(headers))
        if url not in self.routes:
            raise AssertionError(f"unexpected url requested: {url}")
        return self.routes[url]


class StatusTransport:
    """Always returns one status (for the retry/error-path tests)."""

    def __init__(self, status: int, body: str = "[]"):
        self.response = TransportResponse(status, body)

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        return self.response


class TimeoutTransport:
    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        raise TransportTimeout("boom")


def _never_called(url: str, headers: dict, timeout: float) -> TransportResponse:
    raise AssertionError(f"transport must not be called; got {url}")


@pytest.fixture(autouse=True)
def _hermetic_app_token(monkeypatch):
    monkeypatch.delenv(APP_TOKEN_ENV_VAR, raising=False)


def _benchmark_transport() -> RoutedTransport:
    return RoutedTransport({
        Q1_URL: TransportResponse(200, _body(Q1_FILE)),
        Q2_URL: TransportResponse(200, _body(Q2_FILE)),
        Q3_URL: TransportResponse(200, _body(Q3_FILE)),
        Q4_URL: TransportResponse(200, _body(Q4_FILE)),
    })


def _fetch(transport, **kwargs):
    defaults = dict(
        transport=transport, sleep=lambda _s: None, clock=FIXED_CLOCK, correlation_id=FIXED_CORR
    )
    defaults.update(kwargs)
    return fetch_zoning_lot_index(NORTHERN_BBL, **defaults)


# ---------------------------------------------------------------------------
# Benchmark replay: the recorded Northern lot -> OTHER_LOTS_NAMED (S1, S9).
# ---------------------------------------------------------------------------
def test_benchmark_replay_parses_the_three_documents():
    transport = _benchmark_transport()
    result = _fetch(transport)
    assert result.subject_bbl == NORTHERN_BBL
    assert result.as_of_date == "2026-09-30"
    by_type = {d.doc_type: d for d in result.documents}
    assert set(by_type) == {"ZONE", "DECL", "CERT"}
    zone = by_type["ZONE"]
    assert zone.document_id == "2022020201551002"
    assert zone.crfn == "2022000059134"
    assert zone.recorded_datetime == "2022-02-08"
    assert zone.document_date == "2016-08-09"
    assert zone.subject_partial_lot == "E"
    # The ZONE is indexed against both lot 1 and lot 70 on block 7334 (Q3).
    assert {lot.bbl for lot in zone.indexed_lots} == {"4073340001", "4073340070"}
    # Every requested url is the connector's own builder output (and only Legals/Master).
    assert transport.requested_urls == [Q1_URL, Q2_URL, Q3_URL, Q4_URL]


def test_benchmark_replay_classifies_other_lots_named():
    result = _fetch(_benchmark_transport())
    index = classify_zoning_lot_index(result)
    assert index.state is ZoningLotIndexState.OTHER_LOTS_NAMED
    assert [lot.bbl for lot in index.other_same_block_lots] == ["4073340001"]
    assert index.other_block_lots == ()
    assert index.reasons == ("other_same_block_lots",)
    assert [z.crfn for z in index.zone_documents] == ["2022000059134"]
    assert {r.doc_type for r in index.reminder_documents} == {"CERT", "DECL"}
    assert index.as_of_date == "2026-09-30"
    assert index.figures_conditional is True


# ---------------------------------------------------------------------------
# The connector reads metadata only (S9): BBL first, never document_amt / Parties.
# ---------------------------------------------------------------------------
def test_bbl_is_validated_before_any_request():
    with pytest.raises(BBLValidationError):
        fetch_zoning_lot_index("not-a-bbl", transport=_never_called, correlation_id=FIXED_CORR)


def test_no_request_asks_for_document_amt_or_the_parties_dataset():
    transport = _benchmark_transport()
    _fetch(transport)
    assert "document_amt" not in MASTER_SELECT
    for url in transport.requested_urls:
        assert url.startswith((LEGALS_BASE_URL, MASTER_BASE_URL))
        assert "document_amt" not in url
        assert "parties" not in url.lower()
    # The Master request $selects exactly the read columns (no document_amt).
    assert "%24select=" in Q2_URL or "$select=" in Q2_URL


def test_pinned_codes_match_the_recorded_control_codes_copy():
    rows = json.loads(_body(CODES_FILE))
    recorded = {
        r["doc__type"]: r["doc__type_description"]
        for r in rows
        if r.get("doc__type") in DOCUMENT_TYPE_DESCRIPTIONS
    }
    assert recorded == DOCUMENT_TYPE_DESCRIPTIONS
    # The recorded copy is the one NB-01 E3 pins.
    assert hashlib.sha256((PACK / CODES_FILE).read_bytes()).hexdigest() == (
        "518363532df753ac364ce47c5d62dfbdbaf609b598845bfcfe2ec83b9739c625"
    )


def test_malformed_document_id_cannot_enter_a_query():
    with pytest.raises(ValueError):
        build_master_url(["2022020201551002", "x'); DROP"], limit=1000, offset=0)


# ---------------------------------------------------------------------------
# Fail-closed paths (every one maps to the classifier's NOT_READ at the caller).
# ---------------------------------------------------------------------------
def test_timeout_is_source_timeout():
    with pytest.raises(SourceTimeoutError):
        _fetch(TimeoutTransport(), max_attempts=2, backoff_base=0.0)


def test_persistent_503_is_source_unavailable():
    with pytest.raises(SourceUnavailableError):
        _fetch(StatusTransport(503), max_attempts=2, backoff_base=0.0)


def test_persistent_429_is_rate_limited():
    with pytest.raises(RateLimitedError):
        _fetch(StatusTransport(429), max_attempts=2, backoff_base=0.0)


def test_no_such_column_400_is_schema_drift():
    body = json.dumps({"errorCode": "query.soql.no-such-column", "message": "x"})
    with pytest.raises(SchemaDriftError):
        _fetch(RoutedTransport({Q1_URL: TransportResponse(400, body)}))


def test_other_400_is_source_unavailable():
    body = json.dumps({"errorCode": "query.soql.type-mismatch", "message": "x"})
    with pytest.raises(SourceUnavailableError):
        _fetch(RoutedTransport({Q1_URL: TransportResponse(400, body)}))


def test_non_json_body_is_schema_drift():
    with pytest.raises(SchemaDriftError):
        _fetch(RoutedTransport({Q1_URL: TransportResponse(200, "<html>oops</html>")}))


def test_json_object_instead_of_array_is_schema_drift():
    with pytest.raises(SchemaDriftError):
        _fetch(RoutedTransport({Q1_URL: TransportResponse(200, '{"error":true}')}))


def test_missing_required_field_is_schema_drift():
    # A Legals row with no document_id is not the documented shape.
    body = json.dumps([{"borough": "4", "block": "7334", "lot": "70"}])
    with pytest.raises(SchemaDriftError):
        _fetch(RoutedTransport({Q1_URL: TransportResponse(200, body)}))


def test_page_budget_reached_is_fail_closed():
    # A transport that always returns a full page never lets paging terminate.
    full_page = json.dumps([
        {"document_id": "D1", "borough": "4", "block": "7334", "lot": "70", "partial_lot": "E"}
    ])

    def always_full(url, headers, timeout):
        return TransportResponse(200, full_page)

    with pytest.raises(PageBudgetExceededError):
        _fetch(always_full, page_size=1, max_pages=2)


def test_subject_document_without_a_master_row_is_incomplete_index():
    q1_url = build_legals_by_lot_url(4, 7334, 70, limit=1000, offset=0)
    q2_url = build_master_url(["D1"], limit=1000, offset=0)
    q1_body = json.dumps([
        {"document_id": "D1", "borough": "4", "block": "7334", "lot": "70", "partial_lot": "E"}
    ])
    transport = RoutedTransport({
        q1_url: TransportResponse(200, q1_body),
        q2_url: TransportResponse(200, "[]"),  # no Master row for D1
    })
    with pytest.raises(IncompleteIndexError):
        _fetch(transport)


# ---------------------------------------------------------------------------
# URL builders are literal (so recorded fixtures route by exact url).
# ---------------------------------------------------------------------------
def test_url_builders_are_stable_and_scoped():
    assert build_legals_by_lot_url(4, 7334, 70, limit=1000, offset=0) == (
        f"{LEGALS_BASE_URL}?borough=4&block=7334&lot=70"
        "&$order=document_id&$limit=1000&$offset=0"
    )
    assert build_good_through_url() == f"{LEGALS_BASE_URL}?$select=max%28good_through_date%29"
    master = build_master_url(["2022020201551002"], limit=1000, offset=0)
    assert master.startswith(MASTER_BASE_URL)
    assert "document_amt" not in master
