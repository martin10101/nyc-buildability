"""Scenario S3: jittered bounded exponential backoff with a max-retry cap.

Deterministic: delays come from an injected seeded RNG and are asserted both
exactly (seed replay) and distributionally (spread across seeds). No real
sleeps ever run (the recorder captures the schedule).
"""

from random import Random

import pytest

from app.connectors.pluto_soda import (
    SchemaDriftError,
    SourceTimeoutError,
    SourceUnavailableError,
    TransportTimeout,
)
from app.resilience.config import ResilienceConfig
from app.resilience.retry import backoff_delay
from tests.resilience.helpers import (
    BBL,
    DEFAULT_SEED,
    fixture_response,
    make_harness,
    ok_response,
    server_error_response,
)


def test_s3_backoff_sequence_matches_seed_replay_exactly():
    config = ResilienceConfig(
        retry_max_attempts=3, backoff_base_seconds=0.5, backoff_cap_seconds=30.0
    )
    harness = make_harness(
        [server_error_response(), server_error_response(), ok_response()],
        config=config,
    )
    result = harness.fetcher(BBL, "corr-1")
    assert result.status == "ok"
    assert len(harness.transport.calls) == 3

    # Exact replay of the same seeded RNG: full jitter uniform(0, base*2^(n-1)).
    replay = Random(DEFAULT_SEED)
    expected = [replay.uniform(0.0, 0.5), replay.uniform(0.0, 1.0)]
    assert harness.sleeps.delays == expected
    assert all(delay > 0.0 for delay in harness.sleeps.delays)


def test_s3_jitter_produces_spread_across_seeds_within_bounds():
    first_delays = []
    for seed in range(20):
        config = ResilienceConfig(retry_max_attempts=2)
        harness = make_harness(
            [server_error_response(), ok_response()], config=config, seed=seed
        )
        harness.fetcher(BBL, "corr")
        (delay,) = harness.sleeps.delays
        assert 0.0 <= delay <= 0.5  # bound for the first retry
        first_delays.append(delay)
    # Jitter is real: the 20 deterministic samples are not one constant.
    assert len(set(first_delays)) >= 15
    assert max(first_delays) - min(first_delays) > 0.1


def test_s3_backoff_bound_is_capped():
    rng = Random(1)
    for attempt in range(1, 12):
        delay = backoff_delay(
            attempt, base_seconds=10.0, cap_seconds=12.0, rng=rng
        )
        bound = min(12.0, 10.0 * (2 ** (attempt - 1)))
        assert 0.0 <= delay <= bound
        if attempt >= 2:
            assert delay <= 12.0  # exponential term is capped, always


def test_s3_max_retry_cap_respected_then_typed_failure():
    config = ResilienceConfig(retry_max_attempts=3)
    harness = make_harness(
        [server_error_response()] * 3, config=config
    )
    with pytest.raises(SourceUnavailableError):
        harness.fetcher(BBL, "corr-1")
    assert len(harness.transport.calls) == 3  # exactly max_attempts, never more
    assert len(harness.sleeps.delays) == 2  # no sleep after the final failure


def test_s3_timeouts_are_retried_with_backoff():
    config = ResilienceConfig(retry_max_attempts=3)
    harness = make_harness(
        [TransportTimeout("t"), TransportTimeout("t"), TransportTimeout("t")],
        config=config,
    )
    with pytest.raises(SourceTimeoutError):
        harness.fetcher(BBL, "corr-1")
    assert len(harness.transport.calls) == 3
    assert len(harness.sleeps.delays) == 2


def test_s3_schema_drift_is_never_retried():
    harness = make_harness(
        [fixture_response("F13_schema_drift_no_such_column_400.json")]
    )
    with pytest.raises(SchemaDriftError):
        harness.fetcher(BBL, "corr-1")
    assert len(harness.transport.calls) == 1
    assert harness.sleeps.delays == []


def test_s3_non_drift_400_is_never_retried():
    harness = make_harness(
        [fixture_response("F13b_non_drift_400_type_mismatch.json")]
    )
    with pytest.raises(SourceUnavailableError) as excinfo:
        harness.fetcher(BBL, "corr-1")
    assert excinfo.value.detail.get("http_status") == 400
    assert len(harness.transport.calls) == 1
    assert harness.sleeps.delays == []
