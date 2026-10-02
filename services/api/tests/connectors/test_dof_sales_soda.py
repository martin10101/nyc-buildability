"""DOF sales connector (queue item B-11; plan section 11b). Offline: every test replays the
recorded Bayside fixtures through a url-routed fake transport; no live call is ever made.

Fixtures and their provenance: ``services/api/tests/fixtures/dof_sales_bayside/`` (+ MANIFEST,
README) and ``docs/research/dof-sales-comparables-2026-10-02.md``.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.connectors.bbl import BBLValidationError
from app.connectors.dof_sales_soda import (
    APP_TOKEN_ENV_VAR,
    RateLimitedError,
    SchemaDriftError,
    SourceUnavailableError,
    build_by_bbl_url,
    build_candidates_url,
    fetch_comparable_candidates,
    fetch_sales_by_bbl,
)
from app.resilience.transport import TransportResponse

PACK = Path(__file__).resolve().parents[1] / "fixtures" / "dof_sales_bayside"
SUBJECT_FILE = "dof_sales_w2pb-icbu_bbl_4073340070.json"
CANDIDATES_FILE = "dof_sales_w2pb-icbu_bayside_22_store_buildings.json"
VINTAGE = "Tue, 09 Jun 2026 18:31:52 GMT"
VINTAGE_HEADERS = {"x-soda2-truth-last-modified": VINTAGE}

SUBJECT_URL = build_by_bbl_url("4073340070", row_limit=50)
CANDIDATES_URL = build_candidates_url("BAYSIDE", "22 STORE BUILDINGS", row_limit=12)

FIXED_CLOCK = lambda: datetime(2026, 10, 2, 11, 0, 0, tzinfo=UTC)  # noqa: E731
FIXED_CORR = "corr-b11-test"


def _body(name: str) -> str:
    return (PACK / name).read_text(encoding="utf-8")


class RoutedTransport:
    """URL-routed fake transport. Records the url and headers of every request; an
    unmapped url raises (so a test proves exactly which url the connector built)."""

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


def _never_called(url: str, headers: dict, timeout: float) -> TransportResponse:
    raise AssertionError(f"transport must not be called; got {url}")


class StatusTransport:
    """Always returns one status (for the retry/error-path tests)."""

    def __init__(self, status: int, body: str = "{}"):
        self.response = TransportResponse(status, body)

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        return self.response


@pytest.fixture(autouse=True)
def _hermetic_app_token(monkeypatch):
    monkeypatch.delenv(APP_TOKEN_ENV_VAR, raising=False)


def _subject_transport() -> RoutedTransport:
    return RoutedTransport(
        {SUBJECT_URL: TransportResponse(200, _body(SUBJECT_FILE), VINTAGE_HEADERS)}
    )


def _candidates_transport() -> RoutedTransport:
    return RoutedTransport(
        {CANDIDATES_URL: TransportResponse(200, _body(CANDIDATES_FILE), VINTAGE_HEADERS)}
    )


# ---------------------------------------------------------------------------
# URL builders match the recorded fixtures byte-for-byte.
# ---------------------------------------------------------------------------
def test_url_builders_match_the_manifest_urls():
    manifest = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))
    by_file = {e["file"]: e for e in manifest["files"]}
    assert by_file[SUBJECT_FILE]["url"] == SUBJECT_URL
    assert by_file[CANDIDATES_FILE]["url"] == CANDIDATES_URL


# ---------------------------------------------------------------------------
# by-BBL: parse, provenance, BBL validation before any network call.
# ---------------------------------------------------------------------------
def test_fetch_by_bbl_parses_the_subject_sale():
    transport = _subject_transport()
    result = fetch_sales_by_bbl(
        "4073340070", transport=transport, row_limit=50, clock=FIXED_CLOCK,
        correlation_id=FIXED_CORR,
    )
    assert transport.requested_urls == [SUBJECT_URL]
    assert len(result.records) == 1
    row = result.records[0]
    assert row.bbl == "4073340070"
    assert row.building_class_category == "22 STORE BUILDINGS"
    assert row.building_class_at_time_of_sale == "K1"
    assert row.gross_square_feet == 5091  # publisher text "5,091" -> int
    assert row.land_square_feet == 10075
    assert row.sale_price == 0
    assert row.sale_date == "2018-01-18"
    assert row.is_cash_sale is False  # $0 transfer, not a market sale
    assert row.has_recorded_size is True


def test_fetch_by_bbl_provenance_is_sourced_and_dated():
    result = fetch_sales_by_bbl(
        "4073340070", transport=_subject_transport(), row_limit=50, clock=FIXED_CLOCK,
        correlation_id=FIXED_CORR,
    )
    prov = result.provenance
    assert prov["source_id"] == "nyc-dof-annualized-sales-soda"
    assert prov["dataset_id"] == "w2pb-icbu"
    assert prov["request_url"] == SUBJECT_URL
    assert prov["retrieved_at"] == "2026-10-02T11:00:00Z"
    assert prov["dataset_last_modified"] == VINTAGE
    assert prov["record_count"] == 1
    assert result.records[0].source["dataset_last_modified"] == VINTAGE


def test_malformed_bbl_raises_before_any_network_call():
    with pytest.raises(BBLValidationError):
        fetch_sales_by_bbl("not-a-bbl", transport=_never_called, correlation_id=FIXED_CORR)


def test_empty_result_is_an_honest_no_sale():
    transport = RoutedTransport({SUBJECT_URL: TransportResponse(200, "[]", VINTAGE_HEADERS)})
    result = fetch_sales_by_bbl(
        "4073340070", transport=transport, row_limit=50, clock=FIXED_CLOCK,
        correlation_id=FIXED_CORR,
    )
    assert result.records == ()
    assert result.provenance["record_count"] == 0


# ---------------------------------------------------------------------------
# candidates: parse the real edge cases (null bbl, $0 transfers, 0 gross sq ft).
# ---------------------------------------------------------------------------
def test_fetch_candidates_parses_all_twelve_rows_with_edge_cases():
    transport = _candidates_transport()
    result = fetch_comparable_candidates(
        "BAYSIDE", "22 STORE BUILDINGS", transport=transport, row_limit=12,
        clock=FIXED_CLOCK, correlation_id=FIXED_CORR,
    )
    assert transport.requested_urls == [CANDIDATES_URL]
    assert len(result.records) == 12
    assert result.unknown_columns == ()  # every served key is a documented column
    # A row with a null/absent bbl is kept as a record with bbl None (never dropped).
    assert any(r.bbl is None for r in result.records)
    # $0 transfers and rows with no recorded gross floor area both appear in the data.
    assert any(r.sale_price == 0 for r in result.records)
    assert any(r.gross_square_feet == 0 and not r.has_recorded_size for r in result.records)
    # Every row shares one sourced, dated provenance.
    assert all(r.source["dataset_last_modified"] == VINTAGE for r in result.records)


def test_candidates_sorted_most_recent_first():
    result = fetch_comparable_candidates(
        "BAYSIDE", "22 STORE BUILDINGS", transport=_candidates_transport(), row_limit=12,
        clock=FIXED_CLOCK, correlation_id=FIXED_CORR,
    )
    dates = [r.sale_date for r in result.records if r.sale_date]
    assert dates == sorted(dates, reverse=True)


def test_blank_candidate_inputs_are_refused():
    with pytest.raises(ValueError):
        fetch_comparable_candidates("", "22 STORE BUILDINGS", transport=_never_called)
    with pytest.raises(ValueError):
        fetch_comparable_candidates("BAYSIDE", "  ", transport=_never_called)


# ---------------------------------------------------------------------------
# App token header (optional, never required, never fabricated).
# ---------------------------------------------------------------------------
def test_app_token_header_sent_only_when_configured(monkeypatch):
    transport = _subject_transport()
    fetch_sales_by_bbl(
        "4073340070", transport=transport, row_limit=50, clock=FIXED_CLOCK,
        correlation_id=FIXED_CORR,
    )
    assert "X-App-Token" not in transport.requested_headers[0]

    monkeypatch.setenv(APP_TOKEN_ENV_VAR, "fixture-token")  # gitleaks:allow - test value
    transport2 = _subject_transport()
    fetch_sales_by_bbl(
        "4073340070", transport=transport2, row_limit=50, clock=FIXED_CLOCK,
        correlation_id=FIXED_CORR,
    )
    assert transport2.requested_headers[0]["X-App-Token"] == "fixture-token"


# ---------------------------------------------------------------------------
# Typed error taxonomy.
# ---------------------------------------------------------------------------
def test_non_json_body_is_schema_drift():
    transport = RoutedTransport({SUBJECT_URL: TransportResponse(200, "<html>oops</html>")})
    with pytest.raises(SchemaDriftError):
        fetch_sales_by_bbl(
            "4073340070", transport=transport, row_limit=50, clock=FIXED_CLOCK,
            correlation_id=FIXED_CORR,
        )


def test_json_object_instead_of_array_is_schema_drift():
    transport = RoutedTransport({SUBJECT_URL: TransportResponse(200, '{"error":true}')})
    with pytest.raises(SchemaDriftError):
        fetch_sales_by_bbl(
            "4073340070", transport=transport, row_limit=50, clock=FIXED_CLOCK,
            correlation_id=FIXED_CORR,
        )


def test_no_such_column_400_is_schema_drift():
    body = json.dumps({"errorCode": "query.soql.no-such-column", "message": "x"})
    transport = RoutedTransport({SUBJECT_URL: TransportResponse(400, body)})
    with pytest.raises(SchemaDriftError):
        fetch_sales_by_bbl(
            "4073340070", transport=transport, row_limit=50, clock=FIXED_CLOCK,
            correlation_id=FIXED_CORR,
        )


def test_other_400_is_source_unavailable():
    body = json.dumps({"errorCode": "query.soql.type-mismatch", "message": "x"})
    transport = RoutedTransport({SUBJECT_URL: TransportResponse(400, body)})
    with pytest.raises(SourceUnavailableError):
        fetch_sales_by_bbl(
            "4073340070", transport=transport, row_limit=50, clock=FIXED_CLOCK,
            correlation_id=FIXED_CORR,
        )


def test_persistent_429_is_rate_limited():
    with pytest.raises(RateLimitedError):
        fetch_sales_by_bbl(
            "4073340070", transport=StatusTransport(429), row_limit=50,
            max_attempts=2, backoff_base=0.0, sleep=lambda _s: None,
            clock=FIXED_CLOCK, correlation_id=FIXED_CORR,
        )


def test_persistent_503_is_source_unavailable():
    with pytest.raises(SourceUnavailableError):
        fetch_sales_by_bbl(
            "4073340070", transport=StatusTransport(503), row_limit=50,
            max_attempts=2, backoff_base=0.0, sleep=lambda _s: None,
            clock=FIXED_CLOCK, correlation_id=FIXED_CORR,
        )
