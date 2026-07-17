"""Scenario S5: last-known-good serving with VISIBLE staleness.

Upstream down -> the LKG snapshot is served with the original retrieved_at
and a machine-readable staleness note that travels into the profile's
reproducibility.connector_notes (existing provenance structures; no new
contract field). Never silently fresh. No LKG -> the original typed failure.
LKG payloads still pass the M2-T003 boundary validation.
"""

import pytest

from app.connectors.pluto_soda import SchemaDriftError, SourceUnavailableError
from app.profile.builder import build_property_profile
from app.profile.contract import validate_profile
from app.resilience.config import ResilienceConfig
from app.resilience.fetcher import LKG_NOTE_PREFIX
from tests.resilience.helpers import (
    BBL,
    fixture_response,
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


def test_s5_upstream_down_serves_lkg_with_visible_staleness():
    harness = make_harness([ok_response(), server_error_response()], config=_config())
    fresh = harness.fetcher(BBL, "corr-1")
    original_retrieved_at = fresh.retrieved_at

    harness.mono.advance(120.0)  # cache expired; LKG still young
    harness.wall.advance(120.0)
    stale = harness.fetcher(BBL, "corr-2")

    assert stale.status == "ok"
    assert len(harness.transport.calls) == 2  # the failed refetch attempt
    # Provenance truth: retrieved_at remains the ACTUAL original retrieval.
    assert stale.retrieved_at == original_retrieved_at
    assert all(fact["retrieved_at"] == original_retrieved_at for fact in stale.facts)
    # VISIBLE staleness: stable machine-readable note prefix, original
    # timestamp and age stated. Never silently fresh.
    lkg_notes = [note for note in stale.notes if note.startswith(LKG_NOTE_PREFIX)]
    assert len(lkg_notes) == 1
    assert original_retrieved_at in lkg_notes[0]
    assert "age 120s" in lkg_notes[0]
    assert "source_unavailable" in lkg_notes[0]
    assert "STALE" in lkg_notes[0]
    assert fresh.notes == [n for n in stale.notes if not n.startswith(LKG_NOTE_PREFIX)]
    assert harness.metrics.count("lkg_served") == 1


def test_s5_lkg_profile_passes_m2_t003_boundary_validation():
    harness = make_harness([ok_response(), server_error_response()], config=_config())
    fresh = harness.fetcher(BBL, "corr-1")
    fresh_profile = build_property_profile(fresh, clock=harness.wall)
    harness.mono.advance(120.0)
    stale = harness.fetcher(BBL, "corr-2")

    profile = build_property_profile(stale, clock=harness.wall)
    validate_profile(profile)  # M2-T003 pre-send validation: must not raise

    # The staleness note is visible in the served contract document through
    # the EXISTING reproducibility.connector_notes structure.
    notes = profile["reproducibility"]["connector_notes"]
    assert any(note.startswith(LKG_NOTE_PREFIX) for note in notes)
    assert profile["reproducibility"]["retrieved_at"] == fresh.retrieved_at
    # No phantom missing_inputs from the LKG note (builder maps only its
    # known note prefixes).
    assert profile["missing_inputs"] == fresh_profile["missing_inputs"]


def test_s5_no_lkg_available_raises_the_original_typed_failure():
    harness = make_harness([server_error_response()], config=_config())
    with pytest.raises(SourceUnavailableError):
        harness.fetcher(BBL, "corr-1")
    assert harness.metrics.count("lkg_unavailable") == 1
    assert harness.metrics.count("lkg_served") == 0


def test_s5_lkg_older_than_max_age_is_refused_typed():
    config = _config(cache_ttl_seconds=60.0, lkg_max_age_seconds=600.0)
    harness = make_harness([ok_response(), server_error_response()], config=config)
    harness.fetcher(BBL, "corr-1")
    harness.mono.advance(601.0)  # beyond LKG max age (and cache TTL)
    with pytest.raises(SourceUnavailableError):
        harness.fetcher(BBL, "corr-2")
    assert harness.metrics.count("lkg_too_old") == 1
    assert harness.metrics.count("lkg_served") == 0


def test_s5_schema_drift_is_never_masked_by_lkg():
    harness = make_harness(
        [ok_response(), fixture_response("F13_schema_drift_no_such_column_400.json")],
        config=_config(),
    )
    harness.fetcher(BBL, "corr-1")
    harness.mono.advance(120.0)  # cache expired, LKG present
    with pytest.raises(SchemaDriftError):
        harness.fetcher(BBL, "corr-2")
    assert harness.metrics.count("lkg_served") == 0


def test_s5_breaker_open_fast_reject_serves_lkg_with_circuit_note():
    config = _config(breaker_failure_threshold=1, breaker_cooldown_seconds=60.0)
    harness = make_harness([ok_response(), server_error_response()], config=config)
    harness.fetcher(BBL, "corr-1")
    harness.mono.advance(120.0)  # cache expired

    stale_1 = harness.fetcher(BBL, "corr-2")  # failure -> breaker opens -> LKG
    assert any(note.startswith(LKG_NOTE_PREFIX) for note in stale_1.notes)
    assert harness.fetcher._breaker.state == "open"

    stale_2 = harness.fetcher(BBL, "corr-3")  # fast reject -> LKG again
    assert len(harness.transport.calls) == 2  # ZERO upstream I/O while open
    (note,) = [n for n in stale_2.notes if n.startswith(LKG_NOTE_PREFIX)]
    assert "circuit open" in note
    assert harness.metrics.count("lkg_served") == 2
