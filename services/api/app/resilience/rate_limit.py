"""ONE shared, bounded route-side rate limiter + caller key + in-flight job slots (M5-T111).

The three UNMOUNTED D-087 routes (``scene_api``, ``dxf_import_api``, ``export_api``) each
carried their own hand-rolled stdlib limiter with subtly different eviction rules (a plain
dict that never evicted, an ``OrderedDict`` LRU that could evict an ACTIVE caller, and a
key-ceiling sweep). This module replaces all three with one reviewed primitive so the mount
packet (PKT-H) inherits a single, bounded, fail-closed limiter.

DELIBERATELY a NEW sibling of the connector-resilience package - it does NOT touch, import,
or extend the existing ``app/resilience`` modules (``breaker``/``budget``/``cache``/
``config``/``fetcher``/``metrics``/``retry``/``transport``), which handle UPSTREAM connector
resilience and stay read-only. It is not re-exported from ``app/resilience/__init__`` (that
would pull the connector import graph); the routes import it directly.

What it provides (stdlib only, zero new dependencies):

* :class:`SlidingWindowRateLimiter` - a thread-safe per-caller sliding window with a declared
  key ceiling. Idle/expired keys are evicted; when the table is still full of ACTIVE keys a
  NEW key is REFUSED (fail-closed); an active key's history is never evicted (that would reset
  its window). The clock is injectable so tests advance time deterministically.
* :func:`caller_key` - the per-caller key: the authenticated principal when the request
  carries one, else the client host (with the proxy-collapse limit disclosed below).
* :class:`JobSlots` + :func:`run_in_job_slot` - a bounded in-flight job cap per route. A slot
  is held from job start until the worker THREAD returns, NOT until the awaiting coroutine is
  cancelled at the deadline, so abandoned (deadline-exceeded) threads cannot pile up without
  bound. Over the cap raises :class:`SlotsExhausted` for a typed refusal.
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections import deque
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, TypeVar

from starlette.concurrency import run_in_threadpool

if TYPE_CHECKING:  # pragma: no cover - typing only; the module never hard-depends on Starlette
    from starlette.requests import Request

__all__ = [
    "JobSlots",
    "SlidingWindowRateLimiter",
    "SlotsExhausted",
    "caller_key",
    "run_in_job_slot",
]

_T = TypeVar("_T")


class SlidingWindowRateLimiter:
    """A thread-safe per-caller sliding-window rate limiter, bounded in memory.

    Keeps, per caller key, the monotonic timestamps of recently admitted requests. On each
    :meth:`allow` call the key's window is pruned of stamps older than ``window_seconds``; a
    caller is admitted while it holds fewer than ``max_requests`` live stamps and refused
    otherwise. ``max_requests`` / ``window_seconds`` / ``max_keys`` are public attributes read
    LIVE inside :meth:`allow`, so a test can tighten them on the live instance.

    Memory is bounded two ways, both fail-closed:

    * a key whose window empties is dropped immediately (never retained as a dead entry), and
    * the number of distinct tracked keys never exceeds ``max_keys``. When a NEW key arrives at
      the ceiling, expired-window keys are swept first; if the ceiling is STILL full of ACTIVE
      keys the new key is refused. An active key's live history is never evicted - dropping it
      would silently reset that caller's window and let it exceed its limit.

    The clock is injectable (``clock``); production passes ``time.monotonic`` so a wall-clock
    change cannot widen a window.
    """

    def __init__(
        self,
        *,
        max_requests: int,
        window_seconds: float,
        max_keys: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_keys = max_keys
        self._clock = clock
        self._lock = threading.Lock()
        self._windows: dict[str, deque[float]] = {}

    def allow(self, key: str) -> bool:
        """Return ``True`` and record the request when the caller is within budget, else
        ``False``. Thread-safe; O(stamps-in-key) plus, only when a NEW key hits the ceiling,
        O(keys) for the expired-key sweep."""
        now = self._clock()
        with self._lock:
            window = self._windows.get(key)
            if window is not None:
                self._prune(window, now)
                if not window:
                    # The window emptied: drop the dead key so it is never retained, then
                    # treat the caller as new for the ceiling check below.
                    del self._windows[key]
                    window = None
            # An existing key with a LIVE (nonempty) window: admit iff under the per-key limit.
            if window is not None:
                if len(window) >= self.max_requests:
                    return False
                window.append(now)
                return True
            # A brand-new / fully-expired key. A non-positive limit refuses outright.
            if self.max_requests <= 0:
                return False
            if len(self._windows) >= self.max_keys:
                self._sweep_expired(now)
                if len(self._windows) >= self.max_keys:
                    # The ceiling is full of ACTIVE keys: refuse the new caller (fail-closed).
                    return False
            self._windows[key] = deque((now,))
            return True

    def reset(self) -> None:
        """Test hook: clear all windows. Module state persists across a process; a test that
        does not mount a fresh limiter calls this between cases."""
        with self._lock:
            self._windows.clear()

    def active_key_count(self) -> int:
        """The number of distinct tracked keys (diagnostic; used by the bounded-keys tests)."""
        with self._lock:
            return len(self._windows)

    def _prune(self, window: deque[float], now: float) -> None:
        cutoff = now - self.window_seconds
        while window and window[0] <= cutoff:
            window.popleft()

    def _sweep_expired(self, now: float) -> None:
        """Drop every key whose window is empty after pruning. Only ever removes keys with NO
        live stamps - an active key's history is left intact."""
        for existing in list(self._windows):
            window = self._windows[existing]
            self._prune(window, now)
            if not window:
                del self._windows[existing]


def caller_key(request: Request) -> str:
    """The per-caller rate-limit key.

    Returns the authenticated principal when the request carries one, else the client host.
    The two are namespaced (``principal:`` vs ``host:``) so a host string can never collide
    with a principal id.

    PRINCIPAL SOURCE: PKT-H (the mount packet) adds authentication; its auth dependency /
    middleware sets ``request.state.principal`` to the authenticated principal id. This helper
    reads exactly that attribute, so keying flips from host to principal the moment auth lands
    with NO further change here. Until then no principal is present and the host is used.

    PROXY-COLLAPSE LIMIT (DB-080 (b), DB-081 (a), DB-082 (b)): while the key is the host,
    every caller behind Render's shared proxy presents the SAME peer address, so host-keying
    collapses them to one bucket - one caller can exhaust the shared budget and starve the
    rest. ``X-Forwarded-For`` is deliberately NOT trusted here (a client can spoof it, which
    would let an attacker mint unlimited distinct keys and defeat the limiter). The real
    per-caller isolation is the authenticated principal, which is why this route family stays
    UNMOUNTED until PKT-H supplies auth.
    """
    principal = getattr(getattr(request, "state", None), "principal", None)
    if principal is not None:
        return f"principal:{principal}"
    client = getattr(request, "client", None)
    host = getattr(client, "host", None) if client is not None else None
    return f"host:{host or 'unknown'}"


class SlotsExhausted(Exception):
    """Raised by :func:`run_in_job_slot` when a route's in-flight job cap is full. The route
    maps it to a typed capacity refusal (503) rather than starting unbounded work."""


class JobSlots:
    """A bounded counter of in-flight jobs for one route (thread-safe).

    A slot is taken by :meth:`try_acquire` at job start and returned by :meth:`release` when
    the worker THREAD finishes. Because a deadline-exceeded job is only cancelled at the
    awaiting coroutine (a Python thread cannot be force-killed), releasing on thread end -
    never on await cancellation - is what keeps abandoned threads from piling up: they keep
    holding their slot, and once ``max_slots`` are held every new job is refused until a real
    thread returns.
    """

    def __init__(self, *, max_slots: int) -> None:
        self.max_slots = max_slots
        self._lock = threading.Lock()
        self._in_flight = 0

    def try_acquire(self) -> bool:
        with self._lock:
            if self._in_flight >= self.max_slots:
                return False
            self._in_flight += 1
            return True

    def release(self) -> None:
        with self._lock:
            if self._in_flight > 0:
                self._in_flight -= 1

    @property
    def in_flight(self) -> int:
        with self._lock:
            return self._in_flight

    def reset(self) -> None:
        """Test hook: clear the in-flight count (a fresh app per test does not share state,
        but a shared-instance test resets between cases)."""
        with self._lock:
            self._in_flight = 0


async def run_in_job_slot(
    slots: JobSlots,
    work: Callable[[], _T],
    *,
    timeout: float,
    runner: Callable[[Callable[[], _T]], Awaitable[_T]] = run_in_threadpool,
) -> _T:
    """Run ``work`` off the event loop under a per-request ``timeout``, holding one of
    ``slots`` for its whole real lifetime.

    The slot is acquired BEFORE the job starts and released ONLY inside the worker thread's
    ``finally`` (i.e. when ``work`` truly returns or raises) - never when this coroutine's
    await is cancelled at the deadline. So a job abandoned by the deadline keeps its slot until
    its thread ends, and abandoned threads cannot accumulate past ``max_slots``.

    Raises :class:`SlotsExhausted` immediately when the cap is full (no work is started), and
    propagates ``TimeoutError`` from the deadline and any exception ``work`` raises. ``runner``
    is injectable so tests can model deadline-abandonment deterministically; production uses
    Starlette's threadpool.
    """
    if not slots.try_acquire():
        raise SlotsExhausted

    def _guarded() -> _T:
        try:
            return work()
        finally:
            slots.release()

    # No release on this coroutine's cancellation: the release lives in _guarded, bound to the
    # thread's completion. wait_for cancels the AWAIT at the deadline; the thread keeps its slot.
    return await asyncio.wait_for(runner(_guarded), timeout=timeout)
