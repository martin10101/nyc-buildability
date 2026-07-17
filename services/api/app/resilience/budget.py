"""Per-analysis upstream request budget (task M1-T009 item F, scenario S6).

One ``AnalysisBudget`` instance represents the paid-traffic allowance of ONE
analysis run. A budget unit is consumed per upstream ATTEMPT (every network
call costs quota/money, including retries); cache hits are free by design -
"budget exceeded" means ZERO further upstream calls, not zero further
answers. When the budget is exhausted the fetcher raises the typed
``budget_exceeded`` failure (app.resilience.fetcher.BudgetExceededError)
without any upstream I/O and without last-known-good fallback (an exhausted
budget is a caller-side condition, not an upstream outage - masking it with
stale data would hide misconfiguration).

The analysis-run machinery itself arrives with M2; until then callers (jobs,
future analysis endpoints) construct a budget per logical analysis and pass
it to every fetch of that analysis.
"""

from __future__ import annotations

import threading

__all__ = ["AnalysisBudget"]


class AnalysisBudget:
    """Thread-safe monotonic counter against a fixed maximum."""

    def __init__(self, max_upstream_requests: int, *, analysis_id: str | None = None):
        if not isinstance(max_upstream_requests, int) \
                or isinstance(max_upstream_requests, bool) \
                or max_upstream_requests < 0:
            raise ValueError(
                "max_upstream_requests must be an integer >= 0; got "
                f"{max_upstream_requests!r}"
            )
        self.max_upstream_requests = max_upstream_requests
        self.analysis_id = analysis_id
        self._lock = threading.Lock()
        self._consumed = 0

    @property
    def consumed(self) -> int:
        with self._lock:
            return self._consumed

    @property
    def remaining(self) -> int:
        with self._lock:
            return self.max_upstream_requests - self._consumed

    def try_consume(self) -> bool:
        """Atomically consume one unit; ``False`` when exhausted (the caller
        raises the typed failure - the budget itself stays a pure counter)."""
        with self._lock:
            if self._consumed >= self.max_upstream_requests:
                return False
            self._consumed += 1
            return True
