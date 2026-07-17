"""Route wiring: the production default fetcher is the resilient fetcher
(process-wide instance), while the get_pluto_fetcher dependency-override
seam used by every existing test and the web-e2e harness is unchanged
(scenario S8: the full existing suite stays green alongside these tests).
"""

from app.api.v1.properties import (
    _default_fetcher,
    _default_resilient_fetcher,
    get_pluto_fetcher,
)
from app.resilience.fetcher import ResilientPlutoFetcher


def test_default_dependency_returns_the_seam_callable():
    assert get_pluto_fetcher() is _default_fetcher


def test_default_resilient_fetcher_is_a_process_wide_singleton():
    _default_resilient_fetcher.cache_clear()
    try:
        first = _default_resilient_fetcher()
        second = _default_resilient_fetcher()
        assert isinstance(first, ResilientPlutoFetcher)
        # Same instance: cache/breaker/LKG state is process-wide, so repeated
        # requests share the resilience state (no per-request resets).
        assert first is second
    finally:
        _default_resilient_fetcher.cache_clear()
