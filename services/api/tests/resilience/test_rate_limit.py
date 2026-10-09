"""Unit pack for the shared route-side limiter (M5-T111): app/resilience/rate_limit.py.

Fully OFFLINE and deterministic - the clock is injected, the job-slot runner is injected, no
network, no real sleeps beyond short thread hand-offs (and a barrier for the contention tests).
Covers the properties AS-2 (bounded + fail-closed + active-key no-eviction + idle eviction +
the M5-T117 Finding 2 once-per-window sweep bound), AS-3 (principal-over-host key + the M5-T117
Finding 3 non-empty-string principal hygiene + X-Forwarded-For is never trusted) and AS-5 (job
slot held until the thread ends, over-cap typed refusal + the M5-T117 Finding 1 release on a
PRE-START cancel with no leak and no double release). It also proves the threading.Lock in both
primitives under concurrent callers (G4 gap 1). Each property has a reddening mutation; the
mutation RUNS (red/green) are recorded in the producer report (scratch harness, never committed).
"""

from __future__ import annotations

import asyncio
import threading

import pytest

from app.resilience.rate_limit import (
    JobSlots,
    SlidingWindowRateLimiter,
    SlotsExhausted,
    caller_key,
    run_in_job_slot,
)


class _Clock:
    def __init__(self, t: float = 0.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t


def _limiter(*, max_requests=3, window=60.0, max_keys=4, clock=None):
    clock = clock or _Clock()
    return SlidingWindowRateLimiter(
        max_requests=max_requests, window_seconds=window, max_keys=max_keys, clock=clock
    )


class _FakeState:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _FakeClient:
    def __init__(self, host):
        self.host = host


class _FakeRequest:
    def __init__(self, *, principal=None, host=None, headers=None):
        if principal is not None:
            self.state = _FakeState(principal=principal)
        else:
            self.state = _FakeState()
        self.client = _FakeClient(host) if host is not None else None
        # A real Starlette request always carries headers; caller_key must never read them.
        self.headers = dict(headers or {})


# --------------------------------------------------------------------------- basic window


def test_admits_up_to_limit_then_refuses():
    lim = _limiter(max_requests=2, window=10.0)
    assert lim.allow("k") is True
    assert lim.allow("k") is True
    assert lim.allow("k") is False  # third in the window is refused
    # Load-bearing: a larger per-key limit admits the third (proves max_requests drives it).
    lim.max_requests = 100
    assert lim.allow("k") is True


def test_window_slides_and_readmits():
    clock = _Clock(0.0)
    lim = _limiter(max_requests=2, window=10.0, clock=clock)
    assert lim.allow("k") and lim.allow("k")
    assert lim.allow("k") is False
    clock.t = 11.0  # both stamps are now older than the window
    assert lim.allow("k") is True


def test_zero_limit_refuses_every_caller():
    lim = _limiter(max_requests=0)
    assert lim.allow("a") is False
    assert lim.allow("b") is False
    assert lim.active_key_count() == 0  # a refused caller is not tracked


def test_reset_clears_windows():
    lim = _limiter(max_requests=1)
    assert lim.allow("a") is True
    assert lim.active_key_count() == 1
    lim.reset()
    assert lim.active_key_count() == 0
    assert lim.allow("a") is True  # readmitted after reset


# --------------------------------------------------------------------------- AS-2 bounded keys


def test_bounded_keys_fail_closed_and_never_evict_an_active_key():
    """AS-2: the key table never exceeds its ceiling; a NEW caller arriving while the ceiling is
    full of ACTIVE keys is refused (fail-closed); and no active key's history is dropped or
    reset. Mutation (LRU-evict-active): dropping an active key would readmit 'a' below and grow
    past the ceiling - recorded red in the report."""
    lim = _limiter(max_requests=2, window=60.0, max_keys=3)
    assert lim.allow("a") and lim.allow("a")  # 'a' is now AT its per-key limit (2 stamps)
    assert lim.allow("a") is False
    assert lim.allow("b") and lim.allow("c")  # three distinct ACTIVE keys fill the ceiling
    assert lim.active_key_count() == 3

    # A brand-new caller while the ceiling is full of active keys -> refused; no growth.
    assert lim.allow("d") is False
    assert lim.active_key_count() == 3

    # 'a' was neither evicted nor reset: it is still at its per-key limit (a reset would readmit).
    assert lim.allow("a") is False

    # Load-bearing (no-ceiling mutation): a large ceiling admits the new caller.
    lim.max_keys = 1000
    assert lim.allow("d") is True


def test_idle_keys_are_evicted_so_the_ceiling_readmits():
    """AS-2: idle/expired keys are swept when a new caller hits the ceiling, so the table stays
    bounded and readmits once windows expire. Mutation (no sweep): a no-op sweep would leave the
    ceiling full of dead keys and keep refusing 'c' - recorded red in the report."""
    clock = _Clock(0.0)
    lim = _limiter(max_requests=1, window=10.0, max_keys=2, clock=clock)
    assert lim.allow("a") and lim.allow("b")  # ceiling full (2 active keys)
    assert lim.allow("c") is False  # fail-closed while a,b active
    clock.t = 50.0  # a and b windows have expired
    assert lim.allow("c") is True  # the sweep evicts a,b -> c admitted
    assert lim.active_key_count() == 1  # only c remains; the dead keys were dropped


def test_single_key_with_an_empty_window_is_dropped_not_retained():
    clock = _Clock(0.0)
    lim = _limiter(max_requests=1, window=10.0, max_keys=8, clock=clock)
    assert lim.allow("solo") is True
    assert lim.active_key_count() == 1
    clock.t = 100.0  # the only stamp has expired
    assert lim.allow("solo") is True  # window pruned empty, key dropped then re-added
    assert lim.active_key_count() == 1  # never two entries for one caller


# --------------------------------------------------------------------------- AS-3 caller key


def test_caller_key_prefers_principal_over_host():
    req = _FakeRequest(principal="user-42", host="10.0.0.9")
    assert caller_key(req) == "principal:user-42"


def test_two_principals_from_one_host_are_distinct_keys():
    """AS-3: two authenticated principals sharing one host key are counted separately. Mutation
    (host-first): reading the host before the principal collapses them to one key - recorded red
    in the report."""
    a = _FakeRequest(principal="alice", host="10.0.0.9")
    b = _FakeRequest(principal="bob", host="10.0.0.9")
    assert caller_key(a) != caller_key(b)
    lim = _limiter(max_requests=1, max_keys=8)
    assert lim.allow(caller_key(a)) is True
    assert lim.allow(caller_key(b)) is True  # bob is not throttled by alice's request


def test_caller_key_falls_back_to_host_then_unknown():
    assert caller_key(_FakeRequest(host="203.0.113.7")) == "host:203.0.113.7"
    assert caller_key(_FakeRequest()) == "host:unknown"  # no principal, no client
    # A principal and a host never collide: the host bucket is namespaced.
    assert caller_key(_FakeRequest(host="alice")) != caller_key(_FakeRequest(principal="alice"))


# --------------------------------------------------------------------------- AS-5 job slots


def test_over_cap_raises_slots_exhausted():
    slots = JobSlots(max_slots=1)
    assert slots.try_acquire() is True
    with pytest.raises(SlotsExhausted):
        asyncio.run(run_in_job_slot(slots, lambda: "x", timeout=1.0))
    assert slots.in_flight == 1  # the running job kept its one slot; the second was refused


def test_slot_is_released_after_normal_completion():
    slots = JobSlots(max_slots=1)
    result = asyncio.run(run_in_job_slot(slots, lambda: 7, timeout=1.0))
    assert result == 7
    assert slots.in_flight == 0


def test_slot_is_released_when_work_raises():
    slots = JobSlots(max_slots=1)

    def _boom():
        raise RuntimeError("kaboom")

    with pytest.raises(RuntimeError):
        asyncio.run(run_in_job_slot(slots, _boom, timeout=1.0))
    assert slots.in_flight == 0  # released in the thread's finally, even on error


def test_slot_held_until_thread_ends_not_on_await_cancel():
    """AS-5: a job past its deadline keeps its slot until its worker THREAD returns, never when
    the awaiting coroutine is cancelled; over the cap is a typed refusal. Mutation (release on
    cancel): a finally that releases on the coroutine's cancellation would free the slot at the
    deadline - the in_flight==1 assertion reddens - recorded in the report."""
    slots = JobSlots(max_slots=1)
    started = threading.Event()
    may_finish = threading.Event()

    def _blocking_work():
        started.set()
        may_finish.wait(5.0)
        return "done"

    def _abandoning_runner(fn):
        # Run the guarded work in a real background thread; return a coroutine that only sleeps,
        # so wait_for's deadline cancels the AWAIT while the thread keeps running (the route's
        # deadline-abandonment path). DB-088 (g): an EVENT HANDSHAKE - block until the worker has
        # provably entered work() and set `started` - replaces the former 50 ms thread-start
        # window, so when the deadline fires the worker is GUARANTEED running (no wall-clock race:
        # `_guarded` sets its internal started flag BEFORE work() sets this event, so `started`
        # being set implies the run_in_job_slot started flag is already True).
        threading.Thread(target=fn, daemon=True).start()
        assert started.wait(5.0), "worker thread did not start"

        async def _sleep_forever():
            await asyncio.sleep(3600)

        return _sleep_forever()

    async def _scenario():
        with pytest.raises(TimeoutError):
            await run_in_job_slot(
                slots, _blocking_work, timeout=0.05, runner=_abandoning_runner
            )
        assert started.wait(1.0)
        # The await was abandoned at the deadline; the thread still runs -> the slot is held.
        assert slots.in_flight == 1
        # Over the cap while the thread runs -> a typed refusal, not a second thread.
        with pytest.raises(SlotsExhausted):
            await run_in_job_slot(slots, lambda: "x", timeout=1.0, runner=_abandoning_runner)
        # The thread finishes -> the slot is released in its finally.
        may_finish.set()
        for _ in range(500):
            if slots.in_flight == 0:
                break
            await asyncio.sleep(0.01)
        assert slots.in_flight == 0

    asyncio.run(_scenario())


# ------------------------------------------------------- AS-5 Finding 1: pre-start cancel leak


class _CountingJobSlots(JobSlots):
    """A JobSlots that counts real release() calls, to PROVE the slot is released exactly once
    (never twice) on the post-start-timeout path."""

    def __init__(self, *, max_slots: int) -> None:
        super().__init__(max_slots=max_slots)
        self.release_calls = 0

    def release(self) -> None:
        self.release_calls += 1
        super().release()


def _never_starts_runner(fn):
    """Model 'the runner is still waiting for a thread-pool token': never call the worker fn,
    just return a coroutine that sleeps, so wait_for's deadline cancels the await while the
    worker has NOT started (the exact pre-thread-start window of G5 Finding 1)."""

    async def _sleep_forever():
        await asyncio.sleep(3600)

    return _sleep_forever()


def test_pre_start_cancel_releases_the_slot_exactly_once_no_leak():
    """G5 Finding 1: when the deadline cancels the await BEFORE the worker starts (the runner
    still waiting for a thread token, so work() never runs), the acquired slot is released
    exactly once and in_flight returns to 0 - the slot is NOT leaked. Mutation
    (never-release-on-pre-start-cancel): the cancel path stops releasing -> in_flight stays 1 ->
    this reddens (recorded in the report)."""
    slots = JobSlots(max_slots=1)
    ran = {"work": False}

    def _work():
        ran["work"] = True  # pragma: no cover - the worker must never run in this scenario
        return "should-not-run"

    async def _scenario():
        assert slots.in_flight == 0
        with pytest.raises(TimeoutError):
            await run_in_job_slot(slots, _work, timeout=0.02, runner=_never_starts_runner)
        # The worker never ran, and the pre-start cancel path released the acquired slot.
        assert ran["work"] is False
        assert slots.in_flight == 0
        # The slot is genuinely free again: a fresh job can take it (no permanent leak).
        assert slots.try_acquire() is True

    asyncio.run(_scenario())


def test_post_start_cancel_releases_the_slot_exactly_once_no_double():
    """G5 Finding 1: a job cancelled AFTER its worker started is released EXACTLY ONCE - by the
    worker's own finally when the thread returns - and the cancel path must NOT also release
    (no double release). Counts the real release() calls. Mutation
    (release-on-every-cancel): the cancel path releases unconditionally -> the slot frees at the
    deadline while the thread still runs -> the in_flight==1 assertion reddens (recorded)."""
    slots = _CountingJobSlots(max_slots=1)
    started = threading.Event()
    may_finish = threading.Event()

    def _blocking_work():
        started.set()
        may_finish.wait(5.0)
        return "done"

    def _abandoning_runner(fn):
        # DB-088 (g): event handshake (block until the worker has provably started) replaces the
        # 50 ms thread-start window, so the deadline fires only after the worker is running - the
        # post-start cancel path is exercised deterministically, with no wall-clock race.
        threading.Thread(target=fn, daemon=True).start()
        assert started.wait(5.0), "worker thread did not start"

        async def _sleep_forever():
            await asyncio.sleep(3600)

        return _sleep_forever()

    async def _scenario():
        with pytest.raises(TimeoutError):
            await run_in_job_slot(
                slots, _blocking_work, timeout=0.05, runner=_abandoning_runner
            )
        assert started.wait(1.0)
        # Worker started -> the cancel path did NOT release; the slot is still held, unreleased.
        assert slots.in_flight == 1
        assert slots.release_calls == 0
        may_finish.set()
        for _ in range(500):
            if slots.in_flight == 0:
                break
            await asyncio.sleep(0.01)
        # Released exactly once, by the worker's finally; never a second (double) release.
        assert slots.in_flight == 0
        assert slots.release_calls == 1

    asyncio.run(_scenario())


# ------------------------------------------------------- AS-2 Finding 2: bounded full-table sweep


def test_full_table_sweep_runs_at_most_once_per_window():
    """G5 Finding 2: a flood of DISTINCT new keys arriving at a full ceiling triggers the
    O(max_keys x max_requests) expired-key sweep AT MOST ONCE per window, not once per refused
    key, so it cannot serialize every caller behind a full sweep. Counts the real _sweep_expired
    calls. Mutation (sweep-on-every-refused-key): _maybe_sweep sweeps unconditionally -> the
    count grows with the flood -> the 'at most once' assertion reddens (recorded in the report)."""
    clock = _Clock(0.0)
    lim = _limiter(max_requests=1, window=10.0, max_keys=3, clock=clock)
    assert lim.allow("a") and lim.allow("b") and lim.allow("c")  # ceiling full of active keys
    assert lim.active_key_count() == 3

    sweeps = {"n": 0}
    real_sweep = lim._sweep_expired

    def _counting_sweep(now):
        sweeps["n"] += 1
        return real_sweep(now)

    lim._sweep_expired = _counting_sweep  # type: ignore[method-assign]

    # A flood of distinct new keys in the SAME window: all refused (ceiling full of active keys),
    # and the full sweep runs at most once across the whole flood - refused keys are not tracked.
    for i in range(50):
        assert lim.allow(f"flood-{i}") is False
    assert sweeps["n"] <= 1
    assert lim.active_key_count() == 3  # the flood did not grow the table

    # The next window re-opens the throttle: a new refused key sweeps again, now reclaiming the
    # (expired) a/b/c so 'later' is admitted - proving the per-window cadence, not a total block.
    clock.t = 25.0  # a,b,c windows (single stamps at t=0) are now expired
    assert lim.allow("later") is True
    assert sweeps["n"] == 2
    assert lim.active_key_count() == 1  # a,b,c reclaimed; only 'later' remains


# ------------------------------------------------- AS-3 Finding 3: principal hygiene + XFF


def test_empty_or_non_string_principal_falls_back_to_host():
    """G5 Finding 3 / AS-3 / M5-T117 G5 A1 (DB-088 b): the principal keys the caller ONLY when it
    is a string that is NON-EMPTY AFTER STRIPPING whitespace; an empty string, a WHITESPACE-ONLY
    string, or any non-string value falls back to the host key, so a blank/whitespace/malformed
    principal cannot collapse distinct callers into one 'principal:' bucket. Mutations
    (empty-principal-accepted `if principal is not None`; whitespace-principal-keyed
    `and principal` without `.strip()`): "" / "   " -> "principal:..." -> the assertions redden
    (recorded in the report)."""
    # Empty-string principal -> host key, NOT "principal:".
    assert caller_key(_FakeRequest(principal="", host="203.0.113.9")) == "host:203.0.113.9"
    # WHITESPACE-ONLY principal (space, tab, newline, mixed) -> host key, NOT "principal:   "
    # (DB-088 b): a whitespace-only principal is treated as absent, like an empty one.
    for blank in (" ", "   ", "\t", "\n", " \t\n "):
        assert caller_key(_FakeRequest(principal=blank, host="203.0.113.9")) == "host:203.0.113.9"
    # Non-string principals of every stripe -> host key.
    for bad in (0, 0.0, False, [], {}, ("x",), 12345):
        assert caller_key(_FakeRequest(principal=bad, host="203.0.113.9")) == "host:203.0.113.9"
    # A genuine non-empty string principal (even with surrounding whitespace + content) is used.
    assert caller_key(_FakeRequest(principal="user-9", host="203.0.113.9")) == "principal:user-9"
    assert caller_key(_FakeRequest(principal=" u ", host="203.0.113.9")) == "principal: u "


def test_x_forwarded_for_header_never_changes_the_key():
    """G4 gap 2 / AS-3: caller_key derives the key from request.state.principal else the peer
    host ONLY - a caller-supplied X-Forwarded-For header is deliberately NOT trusted (it is
    spoofable; trusting it would let one caller mint unlimited distinct keys and defeat the
    limiter). The key stays host-based for any XFF value. Mutation (trust-XFF): caller_key reads
    the XFF header -> the key changes -> this reddens (recorded in the report)."""
    peer = "203.0.113.5"
    for xff in ("10.9.9.9", "attacker, 10.0.0.1", "not-an-ip", ""):
        req = _FakeRequest(host=peer, headers={"x-forwarded-for": xff, "X-Forwarded-For": xff})
        assert caller_key(req) == f"host:{peer}"
    # With NO client at all, an XFF header cannot conjure a key from thin air either.
    assert caller_key(_FakeRequest(headers={"x-forwarded-for": "10.9.9.9"})) == "host:unknown"


# ------------------------------------------------- G4 gap 1: lock contention (both primitives)


def test_limiter_admits_at_most_max_requests_under_concurrent_callers():
    """G4 gap 1: SlidingWindowRateLimiter.allow() is a lock-guarded read-modify-write, so under
    many concurrent callers on ONE key the admitted total is EXACTLY max_requests, never more.
    Deterministic: a barrier releases all threads together. Mutation (drop the lock) can
    over-admit under this contention - recorded red in the report."""
    lim = SlidingWindowRateLimiter(max_requests=10, window_seconds=1000.0, max_keys=8)
    n = 64
    barrier = threading.Barrier(n)
    results: list[bool] = []
    rlock = threading.Lock()

    def _worker():
        barrier.wait()
        ok = lim.allow("shared")
        with rlock:
            results.append(ok)

    threads = [threading.Thread(target=_worker) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sum(results) == 10  # exactly the cap admitted; the lock prevents over-admission
    assert lim.active_key_count() == 1


def test_job_slots_admit_at_most_max_slots_under_contention():
    """G4 gap 1: JobSlots.try_acquire is lock-guarded, so under many concurrent acquirers the
    admitted total is EXACTLY max_slots, never more. Deterministic via a barrier. Mutation (drop
    the lock) can over-admit - recorded red in the report."""
    slots = JobSlots(max_slots=10)
    n = 64
    barrier = threading.Barrier(n)
    results: list[bool] = []
    rlock = threading.Lock()

    def _worker():
        barrier.wait()
        ok = slots.try_acquire()
        with rlock:
            results.append(ok)

    threads = [threading.Thread(target=_worker) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sum(results) == 10
    assert slots.in_flight == 10


# --------------------------------- DB-088 (a): summed job slots stay under the anyio thread pool


def _anyio_default_thread_pool_tokens() -> int:
    """Read the INSTALLED anyio's default thread-pool capacity LIVE (never assumed). anyio 4.10.0
    builds it in ``AsyncIOBackend.current_default_thread_limiter`` as ``CapacityLimiter(40)``
    (anyio/_backends/_asyncio.py); ``current_default_thread_limiter`` needs a running loop, so
    read ``total_tokens`` inside one."""
    import anyio

    async def _get() -> float:
        return anyio.to_thread.current_default_thread_limiter().total_tokens

    return int(asyncio.run(_get()))


def test_summed_job_slots_stay_under_the_anyio_thread_pool():
    """DB-088 (a) / AS-2: the three D-087 routes' in-flight job-slot caps SUM to strictly LESS than
    anyio's default thread-pool token count, with declared headroom for the app's other run_sync
    users, and the heavier per-slot routes get fewer slots. This test FAILS if the sum ever reaches
    (or exceeds) the pool - the reddening mutation (bump any route's cap so the sum hits the pool)
    is recorded in the report. run_in_threadpool dispatches every job onto this one pool, so a held
    slot must always imply an available (or soon-available) thread token."""
    from app.api.v1.dxf_import_api import DXF_IMPORT_MAX_IN_FLIGHT
    from app.api.v1.export_api import EXPORT_MAX_IN_FLIGHT
    from app.api.v1.scene_api import SCENE_MAX_IN_FLIGHT

    pool = _anyio_default_thread_pool_tokens()
    total = SCENE_MAX_IN_FLIGHT + EXPORT_MAX_IN_FLIGHT + DXF_IMPORT_MAX_IN_FLIGHT
    # STRICTLY under the pool (fails if the sum reaches or exceeds it).
    assert total < pool, f"summed slots {total} must stay under the anyio pool {pool}"
    # Declared headroom (>= 8 tokens) for the app's other run_in_threadpool users.
    assert pool - total >= 8
    # Heavier per-slot routes get fewer slots: dxf-import (20 MiB/slot) <= scene (2 MiB + deep
    # parse) <= export (1 MiB, CPU-bound).
    assert DXF_IMPORT_MAX_IN_FLIGHT <= SCENE_MAX_IN_FLIGHT <= EXPORT_MAX_IN_FLIGHT
