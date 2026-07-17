"""Shared deterministic harness for the M1-T009 resilience tests.

Everything is offline and clock/RNG-injected: fixture transports from the
accepted M1-T002 pack, a fake monotonic clock, a fake wall clock, a sleep
recorder (NO real sleeps anywhere), a seeded RNG, and a recording metrics
hook. No test touches the network (scenario S8).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from random import Random
from types import SimpleNamespace

from app.connectors.pluto_soda import TransportResponse
from app.resilience.config import ResilienceConfig
from app.resilience.fetcher import ResilientPlutoFetcher
from app.resilience.metrics import ResilienceMetrics

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"

# BBL of the F01 live-captured record (Governors Island area).
BBL = "1000010100"

DEFAULT_SEED = 20260717


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def fixture_response(name: str, headers: dict[str, str] | None = None) -> TransportResponse:
    fixture = load_fixture(name)
    return TransportResponse(
        status=fixture["http_status"],
        body=fixture["response_body_raw"],
        headers=headers or {},
    )


def ok_response() -> TransportResponse:
    return fixture_response("F01_single_lot_normal.json")


def rate_limited_response(headers: dict[str, str] | None = None) -> TransportResponse:
    """F07: official docs specify ONLY the 429 status; body is empty."""
    return fixture_response("F07_rate_limit_429_synthetic.json", headers=headers)


def server_error_response() -> TransportResponse:
    return TransportResponse(status=500, body="upstream unavailable")


def no_match_response() -> TransportResponse:
    return TransportResponse(status=200, body="[]")


class FakeTransport:
    """Replays a scripted sequence of responses/exceptions and records calls
    (same pattern as the accepted connector suite)."""

    def __init__(self, script: list):
        self.script = list(script)
        self.calls: list[dict] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.calls.append({"url": url, "headers": dict(headers), "timeout": timeout})
        if not self.script:
            raise AssertionError("FakeTransport script exhausted - unexpected extra request")
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


class SleepRecorder:
    def __init__(self):
        self.delays: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)


class FakeMonotonic:
    def __init__(self, start: float = 1_000.0):
        self.value = start

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


class FakeWallClock:
    def __init__(self, start: datetime | None = None):
        self.value = start or datetime(2026, 7, 17, 12, 0, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += timedelta(seconds=seconds)


class RecordingHook:
    """Metrics hook capturing (event, fields) tuples for assertions."""

    def __init__(self):
        self.events: list[tuple[str, dict]] = []

    def __call__(self, event: str, fields: dict) -> None:
        self.events.append((event, dict(fields)))

    def of(self, event: str) -> list[dict]:
        return [fields for name, fields in self.events if name == event]


def make_harness(
    script: list,
    *,
    config: ResilienceConfig | None = None,
    seed: int = DEFAULT_SEED,
    fetch_kwargs: dict | None = None,
) -> SimpleNamespace:
    """Build a fully injected ResilientPlutoFetcher over a scripted transport."""
    transport = FakeTransport(script)
    mono = FakeMonotonic()
    wall = FakeWallClock()
    sleeps = SleepRecorder()
    hook = RecordingHook()
    metrics = ResilienceMetrics(hook)
    kwargs = {"transport": transport, "clock": wall, "app_token": None}
    kwargs.update(fetch_kwargs or {})
    fetcher = ResilientPlutoFetcher(
        config=config or ResilienceConfig(),
        now=mono,
        wall_clock=wall,
        sleep=sleeps,
        rng=Random(seed),
        metrics=metrics,
        fetch_kwargs=kwargs,
    )
    return SimpleNamespace(
        fetcher=fetcher,
        transport=transport,
        mono=mono,
        wall=wall,
        sleeps=sleeps,
        metrics=metrics,
        hook=hook,
    )
