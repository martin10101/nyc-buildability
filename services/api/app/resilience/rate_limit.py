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
* :class:`JobSlots` + :func:`run_in_job_slot` - a bounded in-flight job cap per route. Once the
  worker has STARTED, its slot is held until the worker THREAD returns, NOT until the awaiting
  coroutine is cancelled at the deadline, so abandoned (deadline-exceeded) threads cannot pile
  up without bound. If the deadline cancels the await BEFORE the worker starts (the runner still
  waiting for a thread-pool token), the slot is released on the cancel path instead - exactly
  once - so it is never leaked (Finding 1). Over the cap raises :class:`SlotsExhausted` for a
  typed refusal.

SLOT COUNT vs THE anyio THREAD POOL (Finding 1 context): ``run_in_threadpool`` dispatches work
onto anyio's default thread pool, whose capacity limiter defaults to 40 tokens (OBSERVED). The
three D-087 routes each cap at ``max_slots=16``, so no single route (16 < 40) can starve the
pool, but their SUM (3 x 16 = 48) EXCEEDS 40. Holding a job slot therefore does NOT imply an
available thread token: under load a slot can be held while its worker still waits for a token,
and if the per-request deadline cancels the await during that wait the worker never starts.
:func:`run_in_job_slot` releases the slot on that pre-start cancel path so those held-but-never-
started slots cannot accumulate to permanent exhaustion. (PKT-H may additionally size the summed
slot caps at or below the pool, or acquire the token with the slot, when it mounts the routes.)
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

    BOUNDED SWEEP (Finding 2): the full-table expired-key sweep is O(max_keys x max_requests)
    under the lock, so running it on EVERY refused new key would let a flood of distinct new
    keys at the ceiling serialize every caller behind a full sweep each. The sweep is therefore
    throttled to AT MOST ONCE PER ``window_seconds`` (:meth:`_maybe_sweep`): the first new key
    at the ceiling in a window sweeps; the rest in that window are refused fail-closed after an
    O(1) ceiling check, and the next window's sweep reclaims any keys whose windows have since
    expired. Reclamation is thus delayed by at most one window - a cost bound, never a
    correctness change (an active key is still never evicted, a new key is still refused when
    the ceiling is full of active keys).

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
        #: Clock time of the last full-table sweep, or ``None`` before any sweep. Guards the
        #: once-per-window throttle in :meth:`_maybe_sweep` (Finding 2). Read/written only under
        #: ``self._lock``.
        self._last_sweep: float | None = None

    def allow(self, key: str) -> bool:
        """Return ``True`` and record the request when the caller is within budget, else
        ``False``. Thread-safe; O(stamps-in-key) plus, only when a NEW key hits the ceiling AND
        a sweep is due (at most once per window), O(keys) for the throttled expired-key sweep."""
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
                self._maybe_sweep(now)
                if len(self._windows) >= self.max_keys:
                    # The ceiling is full of ACTIVE keys (or a sweep was throttled this window):
                    # refuse the new caller (fail-closed).
                    return False
            self._windows[key] = deque((now,))
            return True

    def reset(self) -> None:
        """Test hook: clear all windows. Module state persists across a process; a test that
        does not mount a fresh limiter calls this between cases."""
        with self._lock:
            self._windows.clear()
            self._last_sweep = None

    def active_key_count(self) -> int:
        """The number of distinct tracked keys (diagnostic; used by the bounded-keys tests)."""
        with self._lock:
            return len(self._windows)

    def _prune(self, window: deque[float], now: float) -> None:
        cutoff = now - self.window_seconds
        while window and window[0] <= cutoff:
            window.popleft()

    def _maybe_sweep(self, now: float) -> None:
        """Run the full-table expired-key sweep AT MOST ONCE PER window (Finding 2).

        The sweep is O(max_keys x max_requests) under the lock; running it on every refused new
        key would let a distinct-key flood at the ceiling serialize all callers. This throttle
        runs the first sweep of each window (and the very first ever, when ``_last_sweep`` is
        ``None``) and skips the rest, so the per-call cost of a refused new key stays O(1) after
        the throttle triggers. Correctness is unchanged: skipping a sweep only DELAYS reclaiming
        an expired key by up to one window; an active key is never evicted and a new key is
        still refused fail-closed while the ceiling is full of active keys. Called under
        ``self._lock``."""
        if self._last_sweep is not None and (now - self._last_sweep) < self.window_seconds:
            return
        self._last_sweep = now
        self._sweep_expired(now)

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

    Returns the authenticated principal when the request carries a NON-EMPTY STRING one, else
    the client host. The two are namespaced (``principal:`` vs ``host:``) so a host string can
    never collide with a principal id.

    PRINCIPAL HYGIENE (Finding 3): the principal is used ONLY when ``request.state.principal``
    is a non-empty ``str``. Anything else - no attribute (no auth yet), ``None``, an empty
    string, or a non-string value - falls back to the host key. This closes the case where a
    blank or malformed principal ("" -> "principal:") would silently collapse distinct callers
    into ONE bucket. PKT-H's auth must supply a non-empty, server-authenticated,
    non-caller-influenced id; this helper enforces the non-empty-string half here.

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
    if isinstance(principal, str) and principal:
        return f"principal:{principal}"
    client = getattr(request, "client", None)
    host = getattr(client, "host", None) if client is not None else None
    return f"host:{host or 'unknown'}"


class SlotsExhausted(Exception):
    """Raised by :func:`run_in_job_slot` when a route's in-flight job cap is full. The route
    maps it to a typed capacity refusal (503) rather than starting unbounded work."""


class JobSlots:
    """A bounded counter of in-flight jobs for one route (thread-safe).

    A slot is taken by :meth:`try_acquire` at job start and returned by :meth:`release`. For a
    job whose worker THREAD started, release happens when that thread finishes. Because a
    deadline-exceeded job is only cancelled at the awaiting coroutine (a Python thread cannot be
    force-killed), releasing a STARTED job on thread end - never on its await cancellation - is
    what keeps abandoned threads from piling up: they keep holding their slot, and once
    ``max_slots`` are held every new job is refused until a real thread returns. The one case
    where release follows the CANCEL path instead is a job cancelled BEFORE its worker starts
    (see :func:`run_in_job_slot`); :meth:`release` guards ``> 0`` so a stray release can never
    drive the count negative.
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
    ``slots`` for its whole real lifetime, and releasing that slot EXACTLY ONCE on every path.

    The slot is acquired BEFORE the job starts. Which side releases it is decided by a
    ``started`` flag set inside the worker BEFORE ``work`` runs, so the release happens exactly
    once (Finding 1):

    * Once the worker has STARTED, its own ``finally`` owns the release - it fires when ``work``
      truly returns or raises, never when this coroutine's await is cancelled at the deadline.
      So a started job abandoned by the deadline keeps its slot until its thread ends, and
      abandoned threads cannot accumulate past ``max_slots``.
    * If the deadline (or any other cancellation/failure) unwinds the await BEFORE the worker
      started - the classic case being ``run_in_threadpool`` still waiting for an anyio
      thread-pool token when the summed slot caps exceed the 40-token pool - the worker never
      runs, so the CANCEL path releases the slot instead. Without this the slot would leak
      permanently (its ``finally`` never runs), eventually exhausting the cap for all callers.

    A shared ``released`` flag makes the release idempotent, so the two owners can never
    double-release even under an exotic runner. With production's ``run_in_threadpool``
    (``abandon_on_cancel=False``) the two are already mutually exclusive: on cancellation it
    either never dispatched the worker (started stays False -> cancel-path release) or waited
    for the running thread to finish first (worker ``finally`` already released, started True ->
    cancel path does nothing).

    Raises :class:`SlotsExhausted` immediately when the cap is full (no work is started), and
    propagates ``TimeoutError`` from the deadline and any exception ``work`` raises. ``runner``
    is injectable so tests can model deadline-abandonment deterministically; production uses
    Starlette's threadpool.
    """
    if not slots.try_acquire():
        raise SlotsExhausted

    # One lock-guarded decision of WHO releases the single acquired slot. ``started`` flips True
    # inside the worker before work() runs; ``released`` makes the release fire exactly once.
    _guard = threading.Lock()
    _state = {"started": False, "released": False}

    def _release_once() -> None:
        with _guard:
            if _state["released"]:
                return
            _state["released"] = True
        slots.release()

    def _guarded() -> _T:
        with _guard:
            _state["started"] = True
        try:
            return work()
        finally:
            # The worker started, so it owns the (single, idempotent) release.
            _release_once()

    try:
        return await asyncio.wait_for(runner(_guarded), timeout=timeout)
    except BaseException:
        # The await did not return a value (deadline TimeoutError, cancellation, or a failure
        # raised through the runner). Release HERE only if the worker never started: once work()
        # has begun, the worker's own finally owns and performs the single release.
        with _guard:
            worker_started = _state["started"]
        if not worker_started:
            _release_once()
        raise
