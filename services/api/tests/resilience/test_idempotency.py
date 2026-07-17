"""Scenario S7: retried requests are idempotent; provenance records the
ACTUAL retrieval, never retry artifacts.

The upstream GET has no side effects; the proof obligations here are that a
retried fetch yields exactly one result whose provenance matches a clean
single-attempt success (timestamps from the successful attempt, no attempt
counters in facts), that repeat calls reuse the cache without duplicate
upstream I/O, and that stores hold exactly one entry per key.
"""

from app.connectors.pluto_soda import TransportTimeout
from app.resilience.config import ResilienceConfig
from tests.resilience.helpers import BBL, make_harness, ok_response


def _facts_without_observation_ids(facts: list[dict]) -> list[dict]:
    """observation_id is event-scoped BY CONTRACT (unique per retrieval
    event, M2-T004); every other fact key must be identical across a retried
    and a clean retrieval."""
    return [
        {key: value for key, value in fact.items() if key != "observation_id"}
        for fact in facts
    ]


def test_s7_retried_fetch_equals_clean_fetch_and_records_actual_retrieval():
    config = ResilienceConfig(retry_max_attempts=3)
    retried = make_harness([TransportTimeout("t"), ok_response()], config=config)
    clean = make_harness([ok_response()], config=config)

    retried_result = retried.fetcher(BBL, "corr-same")
    clean_result = clean.fetcher(BBL, "corr-same")

    assert retried_result.status == "ok"
    assert len(retried.transport.calls) == 2  # timeout + success
    assert len(clean.transport.calls) == 1

    # Provenance records the ACTUAL successful retrieval: identical clocks
    # yield identical retrieved_at regardless of how many attempts happened.
    assert retried_result.retrieved_at == clean_result.retrieved_at
    assert _facts_without_observation_ids(retried_result.facts) == \
        _facts_without_observation_ids(clean_result.facts)

    # No retry artifacts leak into provenance or the result.
    for fact in retried_result.facts:
        assert "attempt" not in fact
        assert "attempts" not in fact
        assert "retry" not in str(sorted(fact.keys()))
    assert retried_result.notes == clean_result.notes
    assert retried_result.drift_signals == clean_result.drift_signals


def test_s7_repeat_call_after_retried_success_is_served_from_cache():
    config = ResilienceConfig(retry_max_attempts=3)
    harness = make_harness([TransportTimeout("t"), ok_response()], config=config)
    first = harness.fetcher(BBL, "corr-1")
    second = harness.fetcher(BBL, "corr-2")
    assert len(harness.transport.calls) == 2  # unchanged: cache hit, no dupes
    assert second.facts == first.facts
    assert second.retrieved_at == first.retrieved_at


def test_s7_stores_hold_exactly_one_entry_per_key_after_retries():
    config = ResilienceConfig(retry_max_attempts=3)
    harness = make_harness([TransportTimeout("t"), ok_response()], config=config)
    harness.fetcher(BBL, "corr-1")
    assert len(harness.fetcher._lkg) == 1
    assert len(harness.fetcher._cache) == 1
