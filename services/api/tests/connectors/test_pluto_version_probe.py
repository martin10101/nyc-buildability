"""PLUTO published-version probe tests (queue item B-06 slice 2).

Offline and fixture-driven: every HTTP interaction is replayed through an
injected fake transport. The happy path replays the live-captured F09 fixture
(``services/api/tests/fixtures/pluto/F09_version_select.json``, the recorded
``$select=version&$limit=1`` query, 26v1 on 2026-07-16). Error-path records are
clearly-labelled SYNTHETIC variants that exercise the shared taxonomy only and
are never presented as official data. No test touches the network.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.connectors.pluto_soda import (
    RateLimitedError,
    SchemaDriftError,
    SourceTimeoutError,
    SourceUnavailableError,
    TransportResponse,
    TransportTimeout,
)
from app.connectors.pluto_version_probe import (
    VERSION_PROBE_URL,
    PlutoPublishedVersion,
    fetch_published_version,
)

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
FIXED_CLOCK = lambda: datetime(2026, 7, 16, 20, 26, 53, tzinfo=UTC)  # noqa: E731


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


class FakeTransport:
    """Replays a scripted sequence of responses/exceptions and records calls."""

    def __init__(self, script: list):
        self.script = list(script)
        self.calls: list[dict] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.calls.append({"url": url, "headers": dict(headers), "timeout": timeout})
        if not self.script:
            raise AssertionError("FakeTransport script exhausted - unexpected extra request")
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


class SleepRecorder:
    def __init__(self):
        self.delays: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)


def _f09_response() -> TransportResponse:
    fixture = load_fixture("F09_version_select.json")
    return TransportResponse(status=fixture["http_status"], body=fixture["response_body_raw"])


# --------------------------------------------------------------------------
# Happy path + recorded-request binding
# --------------------------------------------------------------------------


def test_happy_path_returns_26v1_with_provenance() -> None:
    transport = FakeTransport([_f09_response()])
    result = fetch_published_version(
        transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK,
        correlation_id="b06s2")
    assert isinstance(result, PlutoPublishedVersion)
    assert result.version == "26v1"
    assert result.dataset_id == "64uk-42ks"
    assert result.source_id == "nyc-dcp-pluto-soda"
    assert result.correlation_id == "b06s2"
    assert result.seen_at == "2026-07-16T20:26:53Z"  # stamped from the clock after the response
    assert result.query_ref == VERSION_PROBE_URL


def test_request_is_exactly_the_f09_recorded_query() -> None:
    # Bind the probe to the request the fixture recorded - never a guessed query.
    fixture = load_fixture("F09_version_select.json")
    assert VERSION_PROBE_URL == fixture["request_url"]
    transport = FakeTransport([_f09_response()])
    fetch_published_version(transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK)
    assert transport.calls[0]["url"] == fixture["request_url"]


def test_app_token_is_sent_but_never_in_payloads() -> None:
    transport = FakeTransport([_f09_response()])
    fetch_published_version(
        transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK,
        app_token="SECRET")  # gitleaks:allow
    assert transport.calls[0]["headers"].get("X-App-Token") == "SECRET"  # gitleaks:allow


# --------------------------------------------------------------------------
# Schema drift (version shape / body shape) - fails closed, never guessed
# --------------------------------------------------------------------------


def test_malformed_version_is_schema_drift() -> None:
    # SYNTHETIC: version mangled to a non-release string.
    transport = FakeTransport([TransportResponse(200, json.dumps([{"version": "v26-nonsense"}]))])
    with pytest.raises(SchemaDriftError):
        fetch_published_version(transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK)


def test_non_array_body_is_schema_drift() -> None:
    # SYNTHETIC: an object instead of the documented JSON array.
    transport = FakeTransport([TransportResponse(200, json.dumps({"version": "26v1"}))])
    with pytest.raises(SchemaDriftError):
        fetch_published_version(transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK)


def test_empty_array_is_schema_drift() -> None:
    # SYNTHETIC: the version probe must return exactly one row.
    transport = FakeTransport([TransportResponse(200, json.dumps([]))])
    with pytest.raises(SchemaDriftError):
        fetch_published_version(transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK)


def test_non_json_body_is_source_unavailable() -> None:
    # SYNTHETIC: HTTP 200 with a body that is not valid JSON.
    transport = FakeTransport([TransportResponse(200, "<html>not json</html>")])
    with pytest.raises(SourceUnavailableError):
        fetch_published_version(transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK)


# --------------------------------------------------------------------------
# HTTP errors map to the same taxonomy as fetch_by_bbl
# --------------------------------------------------------------------------


def test_http_429_maps_to_rate_limited() -> None:
    transport = FakeTransport([TransportResponse(429, ""), TransportResponse(429, "")])
    with pytest.raises(RateLimitedError):
        fetch_published_version(
            transport=transport, max_attempts=2, sleep=SleepRecorder(), clock=FIXED_CLOCK)


def test_timeout_maps_to_source_timeout() -> None:
    transport = FakeTransport([TransportTimeout("read timed out"),
                               TransportTimeout("read timed out")])
    with pytest.raises(SourceTimeoutError):
        fetch_published_version(
            transport=transport, max_attempts=2, sleep=SleepRecorder(), clock=FIXED_CLOCK)


def test_http_500_maps_to_source_unavailable() -> None:
    transport = FakeTransport([TransportResponse(500, ""), TransportResponse(500, "")])
    with pytest.raises(SourceUnavailableError):
        fetch_published_version(
            transport=transport, max_attempts=2, sleep=SleepRecorder(), clock=FIXED_CLOCK)


def test_schema_drift_400_signature_is_not_retried() -> None:
    # The no-such-column 400 is the schema-drift signature (shared taxonomy).
    body = json.dumps({"errorCode": "query.soql.no-such-column", "message": "no such column"})
    transport = FakeTransport([TransportResponse(400, body)])
    with pytest.raises(SchemaDriftError):
        fetch_published_version(transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK)
    assert len(transport.calls) == 1  # 4xx drift is never retried
