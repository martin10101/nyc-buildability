"""Per-source circuit breaker (task M1-T009 item D, scenario S4).

Classic three-state breaker driven ONLY by the injected monotonic clock:

- ``closed``: calls flow; consecutive FINAL failures are counted; reaching
  ``failure_threshold`` opens the circuit.
- ``open``: calls are rejected fast (no upstream I/O) until
  ``cooldown_seconds`` elapse, then the next ``allow()`` transitions to
  ``half_open`` and admits a trial call.
- ``half_open``: a success closes the circuit (counter reset); a failure
  re-opens it with a fresh cooldown.

Every transition is emitted through the metrics hook
(``breaker_transition`` with from/to/source_id) so the walkthrough can
assert the full state machine. Concurrency note: in ``half_open`` more than
one in-flight trial may be admitted (no single-flight latch); acceptable at
this service's per-BBL call volume and documented rather than hidden.
"""

from __future__ import annotations

import threading
from collections.abc import Callable

from app.resilience.metrics import ResilienceMetrics

__all__ = ["CircuitBreaker"]


class CircuitBreaker:
    def __init__(
        self,
        *,
        source_id: str,
        failure_threshold: int,
        cooldown_seconds: float,
        now: Callable[[], float],
        metrics: ResilienceMetrics | None = None,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if cooldown_seconds <= 0:
            raise ValueError("cooldown_seconds must be positive")
        self._source_id = source_id
        self._failure_threshold = failure_threshold
        self._cooldown = cooldown_seconds
        self._now = now
        self._metrics = metrics
        self._lock = threading.Lock()
        self._state = "closed"
        self._consecutive_failures = 0
        self._opened_at: float | None = None

    @property
    def state(self) -> str:
        with self._lock:
            return self._state

    def allow(self) -> bool:
        """Whether a call may proceed. In ``open``, an elapsed cooldown
        transitions to ``half_open`` and admits the trial call."""
        with self._lock:
            if self._state == "open":
                assert self._opened_at is not None
                if self._now() - self._opened_at >= self._cooldown:
                    self._transition("half_open")
                    return True
                return False
            return True

    def cooldown_remaining(self) -> float:
        with self._lock:
            if self._state != "open" or self._opened_at is None:
                return 0.0
            return max(0.0, self._cooldown - (self._now() - self._opened_at))

    def record_success(self) -> None:
        with self._lock:
            self._consecutive_failures = 0
            if self._state != "closed":
                self._transition("closed")

    def record_failure(self) -> None:
        with self._lock:
            if self._state == "half_open":
                # Failed trial: re-open with a fresh cooldown window.
                self._opened_at = self._now()
                self._transition("open")
                return
            self._consecutive_failures += 1
            if (
                self._state == "closed"
                and self._consecutive_failures >= self._failure_threshold
            ):
                self._opened_at = self._now()
                self._transition("open")

    def _transition(self, new_state: str) -> None:
        """Caller must hold the lock. Emits the transition event."""
        old_state = self._state
        self._state = new_state
        if self._metrics is not None:
            self._metrics.emit(
                "breaker_transition",
                source_id=self._source_id,
                from_state=old_state,
                to_state=new_state,
                consecutive_failures=self._consecutive_failures,
            )
