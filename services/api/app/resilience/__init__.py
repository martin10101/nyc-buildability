"""Pre-paid-traffic connector resilience layer (task M1-T009).

Owner code-audit directive 2026-07-17 section 2.5: response caching,
Retry-After honoring, jittered bounded exponential backoff, per-source
circuit breaker, last-known-good serving with VISIBLE staleness, and
per-analysis request budgets - all deterministic, clock/RNG-injectable, and
implemented at the connector layer behind the existing transport/fetcher
seams so the fixture harness and web-e2e keep working unchanged.

Boundaries honored:

- Deterministic code only; no AI, no legal logic (PRD sections 2, 32.5).
- No contract changes: staleness rides on the EXISTING provenance
  structures (``retrieved_at`` stays the original retrieval moment; a
  machine-readable ``served_from_last_known_good:`` connector note surfaces
  in ``reproducibility.connector_notes``). A first-class contract-visible
  staleness field is a recommended additive follow-up reviewed at G1.
- Official field mappings, provenance semantics, and contract-version logic
  are untouched (they belong to M1-T002/M2-T003/M2-T004).
"""

from app.resilience.breaker import CircuitBreaker
from app.resilience.budget import AnalysisBudget
from app.resilience.cache import TTLCache
from app.resilience.config import ResilienceConfig
from app.resilience.metrics import ResilienceMetrics, logging_metrics_hook
from app.resilience.retry import backoff_delay, parse_retry_after

__all__ = [
    "AnalysisBudget",
    "BudgetExceededError",
    "CircuitBreaker",
    "CircuitOpenError",
    "ResilienceConfig",
    "ResilienceMetrics",
    "ResilientPlutoFetcher",
    "TTLCache",
    "backoff_delay",
    "build_default_resilient_fetcher",
    "logging_metrics_hook",
    "parse_retry_after",
]

# Task M2-T011: the fetcher-composition names are exported LAZILY (PEP 562).
# app.resilience.fetcher imports the pluto_soda connector, and pluto_soda now
# imports app.resilience.transport (the shared transport/retry engine); an
# eager fetcher import here would close that loop into a circular import.
# ``from app.resilience import ResilientPlutoFetcher`` (and the other three
# names) keeps working unchanged through module __getattr__.
_FETCHER_EXPORTS = frozenset(
    {
        "BudgetExceededError",
        "CircuitOpenError",
        "ResilientPlutoFetcher",
        "build_default_resilient_fetcher",
    }
)


def __getattr__(name: str):
    if name in _FETCHER_EXPORTS:
        from app.resilience import fetcher

        return getattr(fetcher, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
