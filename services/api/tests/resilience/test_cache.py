"""Scenario S1: response caching with TTL and versioned cache keys.

A second identical request within TTL is served from cache (transport call
count proves ZERO upstream hits); expiry refetches; keys are versioned;
the cache is memory-bounded (LRU eviction); hit/miss metrics are emitted.
"""

from app.connectors.pluto_soda import DATASET_ID, SOURCE_ID
from app.resilience.cache import TTLCache
from app.resilience.config import ResilienceConfig
from tests.resilience.helpers import (
    BBL,
    FakeMonotonic,
    make_harness,
    no_match_response,
    ok_response,
)


def test_s1_second_identical_request_within_ttl_hits_cache_not_upstream():
    harness = make_harness([ok_response()])  # ONE scripted response only
    first = harness.fetcher(BBL, "corr-1")
    assert first.status == "ok"
    assert len(harness.transport.calls) == 1

    second = harness.fetcher(BBL, "corr-2")
    # Transport call count is the proof: no upstream hit for the second call.
    assert len(harness.transport.calls) == 1
    assert second.status == "ok"
    assert second.facts == first.facts
    assert second.retrieved_at == first.retrieved_at  # provenance unchanged
    # Deep copy: the cached entry can never be mutated through a response.
    assert second is not first
    assert second.facts[0] is not first.facts[0]

    assert harness.metrics.count("cache_miss") == 1
    assert harness.metrics.count("cache_hit") == 1
    assert harness.metrics.cache_hit_ratio() == 0.5


def test_s1_ttl_expiry_refetches_upstream():
    config = ResilienceConfig(cache_ttl_seconds=300.0)
    harness = make_harness([ok_response(), ok_response()], config=config)
    harness.fetcher(BBL, "corr-1")
    harness.mono.advance(301.0)  # beyond TTL - clock-controlled, no sleeps
    harness.fetcher(BBL, "corr-2")
    assert len(harness.transport.calls) == 2
    assert harness.metrics.count("cache_expired") == 1
    assert harness.metrics.count("cache_hit") == 0


def test_s1_request_within_ttl_boundary_still_served_from_cache():
    config = ResilienceConfig(cache_ttl_seconds=300.0)
    harness = make_harness([ok_response()], config=config)
    harness.fetcher(BBL, "corr-1")
    harness.mono.advance(300.0)  # exactly TTL: age == ttl is still live
    harness.fetcher(BBL, "corr-2")
    assert len(harness.transport.calls) == 1


def test_s1_cache_key_is_versioned_and_carries_source_identity():
    config = ResilienceConfig(cache_key_version="v7-test")
    harness = make_harness([], config=config)
    key = harness.fetcher._cache_key(BBL)
    assert key.startswith("v7-test:")
    assert SOURCE_ID in key
    assert DATASET_ID in key
    assert f"bbl={BBL}" in key
    # A different key version can never collide with v7-test entries.
    other = make_harness([], config=ResilienceConfig(cache_key_version="v8-test"))
    assert other.fetcher._cache_key(BBL) != key


def test_s1_no_match_results_are_cached_too():
    harness = make_harness([no_match_response()])
    first = harness.fetcher(BBL, "corr-1")
    second = harness.fetcher(BBL, "corr-2")
    assert first.status == "no_match"
    assert second.status == "no_match"
    assert len(harness.transport.calls) == 1


def test_s1_cache_is_memory_bounded_with_lru_eviction():
    config = ResilienceConfig(cache_max_entries=2)
    harness = make_harness(
        [no_match_response(), no_match_response(), no_match_response()],
        config=config,
    )
    for bbl in ("1000010100", "2000010001", "3000010001"):
        harness.fetcher(bbl, "corr")
    assert harness.metrics.count("cache_evicted") == 1
    evicted = harness.hook.of("cache_evicted")[0]["key"]
    assert "bbl=1000010100" in evicted  # least recently used goes first


def test_ttl_cache_unit_expiry_and_eviction_are_clock_driven():
    mono = FakeMonotonic()
    cache = TTLCache(ttl_seconds=10.0, max_entries=2, now=mono)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    cache.put("c", 3)  # evicts the LRU entry ("b": "a" was touched above)
    assert cache.get("b") is None
    assert cache.get("a") == 1
    mono.advance(11.0)
    assert cache.get("a") is None  # expired on observation
    assert len(cache) == 1  # only "c" remains recorded
