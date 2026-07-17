"""Task M2-T006 scenarios S2/S3: the typed contract-1.3.0 staleness channel.

The resilient fetcher stamps ``result.staleness`` truthfully on every serve
kind, the builder carries it into ``reproducibility.staleness``, and the
served profile passes the M2-T003 boundary validation (which now enforces the
1.3.0 conditionals):

- S2 stale serve: last-known-good emits ``served_from_cache: True, stale:
  True`` with the typed upstream failure, the ORIGINAL retrieval timestamp,
  and the monotonic-clock age - ALONGSIDE the retained human-readable
  ``served_from_last_known_good:`` note.
- S3 fresh/cache serves: a fresh retrieval carries the two-boolean fresh
  marker only (no invented values); a within-TTL cache hit carries the
  explicit ``served_from_cache: True, stale: False`` marker with its own
  per-serve age (M1-T009 G1 finding D2).

Everything offline and deterministic: fixture transports, injected monotonic
and wall clocks (no wall-clock guesses anywhere in the staleness values).
"""

from app.profile.builder import build_property_profile
from app.profile.contract import validate_profile
from app.resilience.config import ResilienceConfig
from app.resilience.fetcher import LKG_NOTE_PREFIX
from tests.resilience.helpers import (
    BBL,
    make_harness,
    ok_response,
    server_error_response,
)


def _config(**overrides) -> ResilienceConfig:
    defaults = {
        "retry_max_attempts": 1,
        "cache_ttl_seconds": 60.0,
        "lkg_max_age_seconds": 3_600.0,
    }
    defaults.update(overrides)
    return ResilienceConfig(**defaults)


# --------------------------------------------------------------------------
# S3 - fresh serve: truthful two-boolean marker, nothing invented
# --------------------------------------------------------------------------


def test_s3_fresh_fetch_carries_no_staleness_record():
    harness = make_harness([ok_response()], config=_config())
    fresh = harness.fetcher(BBL, "corr-1")
    # The fetcher performed a real (fixture) upstream retrieval: no staleness
    # record is attached at this layer.
    assert fresh.staleness is None


def test_s3_fresh_profile_emits_the_fresh_marker_and_validates():
    harness = make_harness([ok_response()], config=_config())
    fresh = harness.fetcher(BBL, "corr-1")
    profile = build_property_profile(fresh, clock=harness.wall)
    # EXACT equality: only the two required booleans - age/error values are
    # never invented for a serve that was not cached (schema absence rule).
    assert profile["reproducibility"]["staleness"] == {
        "served_from_cache": False,
        "stale": False,
    }
    validate_profile(profile)  # 1.3.0 boundary validation must pass


# --------------------------------------------------------------------------
# S3 - within-TTL cache hit: explicit served_from_cache marker (G1 D2)
# --------------------------------------------------------------------------


def test_s3_cache_hit_emits_served_from_cache_with_monotonic_age():
    harness = make_harness([ok_response()], config=_config())
    fresh = harness.fetcher(BBL, "corr-1")
    harness.mono.advance(30.0)  # within the 60 s TTL
    cached = harness.fetcher(BBL, "corr-2")

    assert len(harness.transport.calls) == 1  # zero upstream I/O on the hit
    assert cached.staleness == {
        "served_from_cache": True,
        "stale": False,  # the upstream did NOT fail; this is not a stale serve
        "original_retrieved_at": fresh.retrieved_at,
        "age_seconds": 30.0,  # injected monotonic clock, deterministic
    }
    # Provenance truth unchanged: retrieved_at stays the original retrieval.
    assert cached.retrieved_at == fresh.retrieved_at

    profile = build_property_profile(cached, clock=harness.wall)
    assert profile["reproducibility"]["staleness"] == cached.staleness
    validate_profile(profile)  # cached-serve conditionals satisfied


def test_s3_cache_hit_age_is_per_serve_and_cache_entry_is_not_mutated():
    """Each hit stamps ITS OWN age on a deep copy; the stored entry never
    accumulates staleness state (idempotency of the cached snapshot)."""
    harness = make_harness([ok_response()], config=_config())
    harness.fetcher(BBL, "corr-1")
    harness.mono.advance(20.0)
    first_hit = harness.fetcher(BBL, "corr-2")
    harness.mono.advance(25.0)
    second_hit = harness.fetcher(BBL, "corr-3")

    assert first_hit.staleness["age_seconds"] == 20.0
    assert second_hit.staleness["age_seconds"] == 45.0
    assert len(harness.transport.calls) == 1


# --------------------------------------------------------------------------
# S2 - last-known-good serve: typed staleness + retained human note
# --------------------------------------------------------------------------


def test_s2_lkg_serve_emits_typed_staleness_and_retains_the_note():
    harness = make_harness([ok_response(), server_error_response()], config=_config())
    fresh = harness.fetcher(BBL, "corr-1")
    harness.mono.advance(120.0)  # cache expired; LKG still young
    harness.wall.advance(120.0)
    stale = harness.fetcher(BBL, "corr-2")

    # Typed machine-readable channel (contract 1.3.0; G1 D2): every value is
    # this serve's own record - typed upstream failure, ORIGINAL retrieval
    # timestamp, monotonic age. Nothing invented.
    assert stale.staleness == {
        "served_from_cache": True,
        "stale": True,
        "upstream_error_type": "source_unavailable",
        "original_retrieved_at": fresh.retrieved_at,
        "age_seconds": 120.0,
    }
    # The human-readable STALE note is RETAINED alongside the typed object.
    lkg_notes = [note for note in stale.notes if note.startswith(LKG_NOTE_PREFIX)]
    assert len(lkg_notes) == 1
    assert "STALE" in lkg_notes[0]


def test_s2_lkg_profile_carries_staleness_and_passes_boundary_validation():
    harness = make_harness([ok_response(), server_error_response()], config=_config())
    fresh = harness.fetcher(BBL, "corr-1")
    harness.mono.advance(120.0)
    harness.wall.advance(120.0)
    stale = harness.fetcher(BBL, "corr-2")

    profile = build_property_profile(stale, clock=harness.wall)
    validate_profile(profile)  # 1.3.0 conditionals (stale => error type) pass

    staleness = profile["reproducibility"]["staleness"]
    assert staleness["stale"] is True
    assert staleness["upstream_error_type"] == "source_unavailable"
    # Self-consistency the schema documents: original_retrieved_at equals the
    # (never rewritten) reproducibility.retrieved_at.
    assert staleness["original_retrieved_at"] == profile["reproducibility"]["retrieved_at"]
    assert staleness["original_retrieved_at"] == fresh.retrieved_at
    # Both channels present: typed object AND the retained note.
    assert any(
        note.startswith(LKG_NOTE_PREFIX)
        for note in profile["reproducibility"]["connector_notes"]
    )


def test_s2_breaker_open_lkg_serve_is_typed_stale_with_source_unavailable():
    """Circuit-open fast rejects serve LKG with the same typed staleness; the
    upstream_error_type is the documented outward classification
    (CircuitOpenError subclasses SourceUnavailableError - M1-T009)."""
    config = _config(breaker_failure_threshold=1, breaker_cooldown_seconds=60.0)
    harness = make_harness([ok_response(), server_error_response()], config=config)
    harness.fetcher(BBL, "corr-1")
    harness.mono.advance(120.0)  # cache expired

    harness.fetcher(BBL, "corr-2")  # failure -> breaker opens -> LKG
    stale = harness.fetcher(BBL, "corr-3")  # fast reject -> LKG, zero I/O

    assert len(harness.transport.calls) == 2
    assert stale.staleness["served_from_cache"] is True
    assert stale.staleness["stale"] is True
    assert stale.staleness["upstream_error_type"] == "source_unavailable"
    profile = build_property_profile(stale, clock=harness.wall)
    validate_profile(profile)
