"""Scenario S2: ``Retry-After`` on HTTP 429 is honored EXACTLY.

Clock-controlled proof: the recorded sleep sequence is exactly the header
value (both RFC 9110 forms), with no early retry, no jitter, and a bounded
maximum wait. Grounding: the official Socrata docs specify only the 429
status (fixture F07 notes), so Retry-After is honored per generic RFC 9110
semantics when present and never assumed.
"""

import pytest

from app.connectors.pluto_soda import RateLimitedError, fetch_by_bbl
from app.resilience.config import ResilienceConfig
from app.resilience.retry import parse_retry_after
from tests.resilience.helpers import (
    BBL,
    FakeTransport,
    FakeWallClock,
    SleepRecorder,
    make_harness,
    ok_response,
    rate_limited_response,
)


def test_s2_delay_seconds_form_honored_exactly_no_early_retry():
    harness = make_harness(
        [rate_limited_response(headers={"retry-after": "7"}), ok_response()]
    )
    result = harness.fetcher(BBL, "corr-1")
    assert result.status == "ok"
    assert len(harness.transport.calls) == 2
    # EXACT honoring: the one and only wait is 7.0 seconds - not jittered,
    # not scaled, not preempted by an earlier attempt.
    assert harness.sleeps.delays == [7.0]
    assert harness.metrics.count("retry_after_honored") == 1
    assert harness.metrics.count("retry_scheduled") == 0


def test_s2_http_date_form_honored_exactly_against_injected_clock():
    # Injected wall clock: 2026-07-17T12:00:00Z; header date 30s later.
    harness = make_harness(
        [
            rate_limited_response(
                headers={"retry-after": "Fri, 17 Jul 2026 12:00:30 GMT"}
            ),
            ok_response(),
        ]
    )
    result = harness.fetcher(BBL, "corr-1")
    assert result.status == "ok"
    assert harness.sleeps.delays == [30.0]


def test_s2_http_date_in_the_past_clamps_to_zero_wait():
    harness = make_harness(
        [
            rate_limited_response(
                headers={"retry-after": "Fri, 17 Jul 2026 11:59:00 GMT"}
            ),
            ok_response(),
        ]
    )
    harness.fetcher(BBL, "corr-1")
    assert harness.sleeps.delays == [0.0]


def test_s2_retry_after_beyond_cap_fails_typed_without_waiting():
    config = ResilienceConfig(retry_after_max_wait_seconds=120.0)
    harness = make_harness(
        [rate_limited_response(headers={"retry-after": "600"})], config=config
    )
    with pytest.raises(RateLimitedError):
        harness.fetcher(BBL, "corr-1")
    assert harness.sleeps.delays == []  # never blocks the thread
    assert len(harness.transport.calls) == 1
    assert harness.metrics.count("retry_after_exceeds_cap") == 1


def test_s2_missing_or_malformed_retry_after_falls_back_to_jittered_backoff():
    config = ResilienceConfig(backoff_base_seconds=0.5, backoff_cap_seconds=30.0)
    for headers in (None, {"retry-after": "soon"}, {"retry-after": ""}):
        harness = make_harness(
            [rate_limited_response(headers=headers), ok_response()], config=config
        )
        harness.fetcher(BBL, "corr-1")
        assert harness.metrics.count("retry_scheduled") == 1
        assert harness.metrics.count("retry_after_honored") == 0
        (delay,) = harness.sleeps.delays
        assert 0.0 <= delay <= 0.5  # first-retry full-jitter bound


def test_connector_surfaces_sanitized_retry_after_detail_case_insensitively():
    # Uppercase header name; single attempt so the typed error surfaces.
    transport = FakeTransport([rate_limited_response(headers={"Retry-After": "5"})])
    with pytest.raises(RateLimitedError) as excinfo:
        fetch_by_bbl(
            BBL,
            transport=transport,
            max_attempts=1,
            sleep=SleepRecorder(),
            clock=FakeWallClock(),
            app_token=None,
        )
    assert excinfo.value.detail["retry_after"] == "5"


def test_connector_repr_sanitizes_hostile_retry_after_header():
    hostile = "5\r\nX-Injected: log-poison"
    transport = FakeTransport([rate_limited_response(headers={"retry-after": hostile})])
    with pytest.raises(RateLimitedError) as excinfo:
        fetch_by_bbl(
            BBL,
            transport=transport,
            max_attempts=1,
            sleep=SleepRecorder(),
            clock=FakeWallClock(),
            app_token=None,
        )
    detail = excinfo.value.detail["retry_after"]
    assert detail == repr(hostile)
    assert "\r" not in detail and "\n" not in detail


def test_parse_retry_after_rejects_garbage_without_raising():
    wall = FakeWallClock()
    for raw in (None, "", "  ", "soon", "-5", "5.5", "99999999999", "Fri, 32 Jul"):
        assert parse_retry_after(raw, wall_now=wall) is None
    assert parse_retry_after("0", wall_now=wall) == 0.0
    assert parse_retry_after(" 12 ", wall_now=wall) == 12.0
