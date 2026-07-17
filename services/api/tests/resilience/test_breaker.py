"""Scenario S4: per-source circuit breaker - every transition tested.

closed -> open at the configured consecutive-failure threshold; open rejects
fast (transport call count proves zero upstream I/O); open -> half_open
after the clock-controlled cooldown; half_open -> closed on success;
half_open -> open on a failed trial. Transitions are asserted from the
structured metrics events.
"""

import pytest

from app.connectors.pluto_soda import SchemaDriftError, SourceUnavailableError
from app.resilience.breaker import CircuitBreaker
from app.resilience.config import ResilienceConfig
from app.resilience.fetcher import CircuitOpenError
from app.resilience.metrics import ResilienceMetrics
from tests.resilience.helpers import (
    BBL,
    FakeMonotonic,
    RecordingHook,
    fixture_response,
    make_harness,
    ok_response,
    server_error_response,
)


def _config() -> ResilienceConfig:
    return ResilienceConfig(
        retry_max_attempts=1,  # one upstream attempt per call for clarity
        breaker_failure_threshold=3,
        breaker_cooldown_seconds=60.0,
    )


def _transitions(hook: RecordingHook) -> list[tuple[str, str]]:
    return [
        (fields["from_state"], fields["to_state"])
        for fields in hook.of("breaker_transition")
    ]


def test_s4_full_state_machine_open_halfopen_reopen_halfopen_close():
    script = [
        server_error_response(),  # failure 1 (closed)
        server_error_response(),  # failure 2 (closed)
        server_error_response(),  # failure 3 -> opens
        # 4th call: rejected fast, NO transport entry
        server_error_response(),  # 5th call: half-open trial fails -> re-open
        ok_response(),  # 7th call: half-open trial succeeds -> closed
    ]
    harness = make_harness(script, config=_config())

    for attempt in ("corr-1", "corr-2", "corr-3"):
        with pytest.raises(SourceUnavailableError):
            harness.fetcher(BBL, attempt)
    assert len(harness.transport.calls) == 3
    assert _transitions(harness.hook) == [("closed", "open")]

    # Open: fast rejection with zero upstream I/O and a typed error whose
    # outward error_type keeps the documented route mapping.
    with pytest.raises(CircuitOpenError) as excinfo:
        harness.fetcher(BBL, "corr-4")
    assert len(harness.transport.calls) == 3  # NO new transport call
    assert excinfo.value.error_type == "source_unavailable"
    assert excinfo.value.detail["circuit"] == "open"
    assert excinfo.value.detail["cooldown_remaining_seconds"] > 0
    assert harness.metrics.count("breaker_fast_reject") == 1

    # Cooldown elapses (clock-controlled): next call is the half-open trial.
    harness.mono.advance(60.0)
    with pytest.raises(SourceUnavailableError):
        harness.fetcher(BBL, "corr-5")
    assert len(harness.transport.calls) == 4  # the trial DID go upstream
    assert _transitions(harness.hook) == [
        ("closed", "open"),
        ("open", "half_open"),
        ("half_open", "open"),  # failed trial re-opens with fresh cooldown
    ]

    # Still open within the fresh cooldown: fast reject again.
    harness.mono.advance(30.0)
    with pytest.raises(CircuitOpenError):
        harness.fetcher(BBL, "corr-6")
    assert len(harness.transport.calls) == 4

    # Second cooldown elapses; successful trial closes the circuit.
    harness.mono.advance(30.0)
    result = harness.fetcher(BBL, "corr-7")
    assert result.status == "ok"
    assert _transitions(harness.hook) == [
        ("closed", "open"),
        ("open", "half_open"),
        ("half_open", "open"),
        ("open", "half_open"),
        ("half_open", "closed"),
    ]
    assert harness.fetcher._breaker.state == "closed"


def test_s4_success_resets_the_consecutive_failure_count():
    script = [
        server_error_response(),
        server_error_response(),
        ok_response(),  # resets the count before the threshold is reached
        server_error_response(),
        server_error_response(),
    ]
    config = _config()
    harness = make_harness(script, config=config)
    for corr in ("c1", "c2"):
        with pytest.raises(SourceUnavailableError):
            harness.fetcher(BBL, corr)
    assert harness.fetcher(BBL, "c3").status == "ok"
    harness.mono.advance(config.cache_ttl_seconds + 1)  # expire the cache
    for corr in ("c4", "c5"):
        # The c3 success stored a last-known-good snapshot, so these upstream
        # failures serve STALE data (scenario S5) while still counting as
        # breaker failures - the breaker sees the upstream truth.
        stale = harness.fetcher(BBL, corr)
        assert any(note.startswith("served_from_last_known_good:")
                   for note in stale.notes)
    assert len(harness.transport.calls) == 5
    # 2 + 2 failures with a success between: threshold 3 never reached.
    assert _transitions(harness.hook) == []
    assert harness.fetcher._breaker.state == "closed"


def test_s4_schema_drift_does_not_trip_the_breaker():
    script = [fixture_response("F13_schema_drift_no_such_column_400.json")] * 3
    harness = make_harness(script, config=_config())
    for corr in ("c1", "c2", "c3"):
        with pytest.raises(SchemaDriftError):
            harness.fetcher(BBL, corr)
    # Drift is dataset-contract breakage, not an outage: circuit stays closed.
    assert harness.fetcher._breaker.state == "closed"
    assert _transitions(harness.hook) == []


def test_s4_breaker_unit_cooldown_remaining_and_allow():
    mono = FakeMonotonic()
    hook = RecordingHook()
    breaker = CircuitBreaker(
        source_id="test-source",
        failure_threshold=2,
        cooldown_seconds=10.0,
        now=mono,
        metrics=ResilienceMetrics(hook),
    )
    assert breaker.allow() and breaker.state == "closed"
    breaker.record_failure()
    assert breaker.state == "closed"
    breaker.record_failure()
    assert breaker.state == "open"
    assert breaker.allow() is False
    assert breaker.cooldown_remaining() == 10.0
    mono.advance(4.0)
    assert breaker.cooldown_remaining() == 6.0
    assert breaker.allow() is False
    mono.advance(6.0)
    assert breaker.allow() is True  # transitions to half_open
    assert breaker.state == "half_open"
    breaker.record_success()
    assert breaker.state == "closed"
    assert breaker.cooldown_remaining() == 0.0
