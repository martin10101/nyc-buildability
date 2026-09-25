"""Unit pack for the shared route-side limiter (M5-T111): app/resilience/rate_limit.py.

Fully OFFLINE and deterministic - the clock is injected, the job-slot runner is injected, no
network, no real sleeps beyond short thread hand-offs. Covers the properties AS-2 (bounded +
fail-closed + active-key no-eviction + idle eviction), AS-3 (principal-over-host key) and AS-5
(job slot held until the thread ends, over-cap typed refusal). Each property has a reddening
mutation; the mutation RUNS (red/green) are recorded in the producer report (scratch harness,
never committed).
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
    def __init__(self, *, principal=None, host=None):
        if principal is not None:
            self.state = _FakeState(principal=principal)
        else:
            self.state = _FakeState()
        self.client = _FakeClient(host) if host is not None else None


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
        # deadline-abandonment path).
        threading.Thread(target=fn, daemon=True).start()

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
