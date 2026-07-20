"""Task M2-T011 consolidation tests: shared transport/retry engine.

TC-S2: exactly ONE retry-loop implementation exists (grep-provable code
shape guard) and all four connectors delegate to it.
TC-S3/TC-S7: the resilience semantics (Retry-After honored exactly,
over-cap honored by NOT retrying, full-jitter bounds, budget consumed
BEFORE each attempt, bounded attempts, typed terminal outcomes, no retry
of unexpected statuses) are exercised DIRECTLY through the shared path,
plus a per-connector fault matrix proving the four public connectors
still produce their accepted typed outcomes through the shared loop.

Deterministic: seeded RNGs, recorded sleeps, fixed clocks, no real I/O.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from random import Random

import pytest

from app.connectors import (
    mappluto_geometry_arcgis,
    pluto_soda,
    zoning_features_arcgis,
    ztldb_soda,
)
from app.resilience.budget import AnalysisBudget
from app.resilience.transport import (
    TransportFailure,
    TransportResponse,
    TransportTimeout,
    fixed_exponential_delay,
    jittered_retry_after_delay,
    request_with_retry,
    standard_retry_hooks,
)

APP_DIR = Path(__file__).resolve().parents[2] / "app"
CONNECTOR_FILES = [
    APP_DIR / "connectors" / "pluto_soda.py",
    APP_DIR / "connectors" / "zoning_features_arcgis.py",
    APP_DIR / "connectors" / "ztldb_soda.py",
    APP_DIR / "connectors" / "mappluto_geometry_arcgis.py",
]
SHARED_FILE = APP_DIR / "resilience" / "transport.py"
LOOP_MARKER = "for attempt in range(1, max_attempts + 1)"

URL = "https://example.official.test/resource?x=1"
FIXED_WALL = lambda: datetime(2026, 7, 20, 12, 0, 0, tzinfo=UTC)  # noqa: E731

logger = logging.getLogger("tests.resilience.transport_shared")


class SentinelError(Exception):
    """Typed sentinel with the shared connector-error signature."""

    def __init__(self, message, *, correlation_id, detail, layer=None):
        super().__init__(message)
        self.message = message
        self.correlation_id = correlation_id
        self.detail = detail
        self.layer = layer


class RateLimitedSentinel(SentinelError):
    pass


class TimeoutSentinel(SentinelError):
    pass


class UnavailableSentinel(SentinelError):
    pass


class BudgetSentinel(SentinelError):
    pass


class FakeTransport:
    """Scripted transport: each entry is a TransportResponse or an exception
    instance to raise. Records every call."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def __call__(self, url, headers, timeout):
        self.calls.append((url, dict(headers), timeout))
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class SleepRecorder:
    def __init__(self):
        self.delays = []

    def __call__(self, seconds):
        self.delays.append(seconds)


def make_hooks(*, sanitize=lambda reason: reason, with_budget=True):
    return standard_retry_hooks(
        logger=logger,
        log_label="shared_test",
        correlation_id="corr-shared",
        url=URL,
        sanitize_network_reason=sanitize,
        rate_limited_error=RateLimitedSentinel,
        rate_limited_message="rate limited terminal",
        timeout_error=TimeoutSentinel,
        timeout_message="timeout terminal",
        unavailable_error=UnavailableSentinel,
        unavailable_message="unavailable terminal",
        include_reason_kind=True,
        unexpected_status_message="unexpected HTTP status {status} from test",
        budget_error=BudgetSentinel if with_budget else None,
    )


def run(transport, *, max_attempts=3, hooks=None, delay=None, sleep=None, budget=None):
    return request_with_retry(
        URL,
        transport=transport,
        headers={"Accept": "application/json"},
        timeout=10.0,
        max_attempts=max_attempts,
        hooks=hooks or make_hooks(),
        compute_delay=delay
        or jittered_retry_after_delay(
            backoff_base=0.5,
            backoff_cap=30.0,
            retry_after_cap=120.0,
            rng=Random(7),
            wall_clock=FIXED_WALL,
        ),
        sleep=sleep or SleepRecorder(),
        budget=budget,
    )


# ---------------------------------------------------------------------------
# TC-S2 - single shared implementation (code-shape regression guard)
# ---------------------------------------------------------------------------


def test_s2_retry_loop_exists_only_in_shared_module():
    for path in CONNECTOR_FILES:
        source = path.read_text(encoding="utf-8")
        assert LOOP_MARKER not in source, f"duplicated retry loop in {path.name}"
        assert "request_with_retry(" in source, (
            f"{path.name} no longer delegates to the shared engine"
        )
    shared = SHARED_FILE.read_text(encoding="utf-8")
    assert shared.count(LOOP_MARKER) == 1


def test_s2_all_four_wrappers_use_the_shared_symbols():
    for module in (pluto_soda, zoning_features_arcgis, ztldb_soda,
                   mappluto_geometry_arcgis):
        assert module.request_with_retry.__module__ == "app.resilience.transport"
        assert module.standard_retry_hooks.__module__ == "app.resilience.transport"


# ---------------------------------------------------------------------------
# TC-S3 - resilience semantics through the shared path
# ---------------------------------------------------------------------------


def test_s3_retry_after_delay_seconds_honored_exactly():
    transport = FakeTransport(
        [TransportResponse(429, "", {"retry-after": "7"}), TransportResponse(200, "[]")]
    )
    sleeps = SleepRecorder()
    response = run(transport, sleep=sleeps)
    assert response.status == 200
    assert sleeps.delays == [7.0]  # honored EXACTLY - no jitter, no scaling
    assert len(transport.calls) == 2


def test_s3_retry_after_http_date_honored_via_injected_wall_clock():
    transport = FakeTransport(
        [
            TransportResponse(
                429, "", {"retry-after": "Mon, 20 Jul 2026 12:00:30 GMT"}
            ),
            TransportResponse(200, "[]"),
        ]
    )
    sleeps = SleepRecorder()
    run(transport, sleep=sleeps)
    assert sleeps.delays == [30.0]


def test_s3_retry_after_beyond_cap_stops_retrying_typed():
    transport = FakeTransport([TransportResponse(429, "", {"retry-after": "999"})])
    sleeps = SleepRecorder()
    with pytest.raises(RateLimitedSentinel) as excinfo:
        run(transport, sleep=sleeps)
    # Honored by NOT retrying: one attempt, zero sleeps, typed terminal.
    assert len(transport.calls) == 1
    assert sleeps.delays == []
    assert excinfo.value.detail["attempts"] == 1
    assert excinfo.value.detail["retry_after"] == "999"
    assert excinfo.value.detail["max_attempts"] == 3
    assert excinfo.value.detail["url"] == URL


def test_s3_unparseable_retry_after_falls_back_to_seeded_jitter():
    transport = FakeTransport(
        [TransportResponse(429, "", {"retry-after": "soon\x00"}), TransportResponse(200, "[]")]
    )
    sleeps = SleepRecorder()
    run(transport, sleep=sleeps)
    expected = Random(7).uniform(0.0, 0.5)  # full jitter, first retry bound
    assert sleeps.delays == [expected]


def test_s3_jitter_bounds_and_seed_replay_for_5xx():
    transport = FakeTransport(
        [TransportResponse(500, ""), TransportResponse(503, ""), TransportResponse(200, "[]")]
    )
    sleeps = SleepRecorder()
    run(transport, sleep=sleeps)
    replay = Random(7)
    assert sleeps.delays == [replay.uniform(0.0, 0.5), replay.uniform(0.0, 1.0)]
    assert all(0.0 <= d <= 1.0 for d in sleeps.delays)


def test_s3_fixed_exponential_delay_matches_legacy_pluto_sequence():
    transport = FakeTransport(
        [TransportResponse(500, ""), TransportResponse(500, ""), TransportResponse(200, "[]")]
    )
    sleeps = SleepRecorder()
    run(transport, delay=fixed_exponential_delay(0.5), sleep=sleeps)
    assert sleeps.delays == [0.5, 1.0]  # base * 2^(n-1), no jitter


def test_s3_budget_unit_consumed_before_every_attempt():
    budget = AnalysisBudget(2, analysis_id="an-1")
    transport = FakeTransport([TransportTimeout("t"), TransportTimeout("t")])
    with pytest.raises(BudgetSentinel) as excinfo:
        run(transport, budget=budget)
    # Attempts 1 and 2 consumed the whole budget; attempt 3 was refused
    # BEFORE any upstream I/O.
    assert len(transport.calls) == 2
    assert budget.consumed == 2
    assert excinfo.value.detail == {
        "max_upstream_requests": 2,
        "consumed": 2,
        "analysis_id": "an-1",
    }


def test_s3_timeout_exhaustion_is_typed_with_attempt_count():
    transport = FakeTransport([TransportTimeout("t")] * 3)
    sleeps = SleepRecorder()
    with pytest.raises(TimeoutSentinel) as excinfo:
        run(transport, sleep=sleeps)
    assert len(transport.calls) == 3
    assert len(sleeps.delays) == 2  # never sleeps after the final failure
    assert excinfo.value.detail["attempts"] == 3


def test_s3_network_reason_passes_through_injected_sanitizer():
    transport = FakeTransport([TransportFailure("bad\x00reason")] * 3)
    with pytest.raises(UnavailableSentinel) as excinfo:
        run(transport, hooks=make_hooks(sanitize=repr))
    assert excinfo.value.detail["reason"] == repr("bad\x00reason")
    assert excinfo.value.detail["reason_kind"] == "network"


# ---------------------------------------------------------------------------
# TC-S7 - fault matrix through the shared path
# ---------------------------------------------------------------------------


def test_s7_unexpected_status_is_never_retried():
    transport = FakeTransport([TransportResponse(302, "")])
    sleeps = SleepRecorder()
    with pytest.raises(UnavailableSentinel) as excinfo:
        run(transport, sleep=sleeps)
    assert len(transport.calls) == 1
    assert sleeps.delays == []
    assert excinfo.value.detail == {"http_status": 302, "url": URL}
    assert "unexpected HTTP status 302" in excinfo.value.message


def test_s7_429_burst_exhausts_budgeted_attempts_then_typed():
    transport = FakeTransport([TransportResponse(429, "")] * 3)
    sleeps = SleepRecorder()
    with pytest.raises(RateLimitedSentinel) as excinfo:
        run(transport, sleep=sleeps)
    assert len(transport.calls) == 3
    assert len(sleeps.delays) == 2
    assert excinfo.value.detail["attempts"] == 3
    assert excinfo.value.detail["max_attempts"] == 3


@pytest.mark.parametrize(
    ("fault", "expected_error_type"),
    [
        (TransportTimeout("t"), "timeout"),
        (TransportResponse(429, "", {"retry-after": "999999"}), "rate_limited"),
        (TransportResponse(503, "upstream sad"), None),  # per-connector name
    ],
    ids=["timeout", "429_over_cap", "5xx_burst"],
)
def test_s7_connector_fault_matrix_same_typed_outcomes(fault, expected_error_type):
    """The four public connectors produce their ACCEPTED typed outcomes for
    the same transport faults through the shared loop (fixture-driven
    comparison; the per-connector 5xx terminal differs by accepted taxonomy:
    pluto_soda source_unavailable vs M2-wave upstream_error)."""
    script = [fault] * 3 if isinstance(fault, TransportTimeout) else [fault] * 3
    cases = [
        (
            lambda t: pluto_soda.fetch_by_bbl(
                "1000477501", transport=t, sleep=lambda s: None,
                correlation_id="corr-p",
            ),
            pluto_soda.PlutoConnectorError,
            "source_unavailable",
        ),
        (
            lambda t: ztldb_soda.fetch_by_bbl(
                "1000477501", transport=t, sleep=lambda s: None, rng=Random(1),
                correlation_id="corr-z",
            ),
            ztldb_soda.ZtldbConnectorError,
            "upstream_error",
        ),
        (
            lambda t: zoning_features_arcgis.fetch_layer_metadata(
                "nyzd", transport=t, sleep=lambda s: None, rng=Random(1),
                correlation_id="corr-f",
            ),
            zoning_features_arcgis.ZoningFeaturesConnectorError,
            "upstream_error",
        ),
        (
            lambda t: mappluto_geometry_arcgis.fetch_layer_metadata(
                transport=t, sleep=lambda s: None, rng=Random(1),
                correlation_id="corr-m",
            ),
            mappluto_geometry_arcgis.MapPlutoGeometryConnectorError,
            "upstream_error",
        ),
    ]
    for call, base_error, unavailable_type in cases:
        transport = FakeTransport(list(script))
        with pytest.raises(base_error) as excinfo:
            call(transport)
        expected = expected_error_type or unavailable_type
        assert excinfo.value.error_type == expected, (
            f"{base_error.__module__}: expected {expected}, "
            f"got {excinfo.value.error_type}"
        )
        # 429 with an over-cap Retry-After stops after one attempt in the
        # M2-wave connectors (M1-T009 policy); pluto's legacy policy records
        # the header but never waits on it, so it retries the full budget.
        assert 1 <= len(transport.calls) <= 3
