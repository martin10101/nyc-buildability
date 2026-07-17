"""Bounded TTL response cache with versioned keys (task M1-T009 item A).

Deterministic: time comes ONLY from the injected monotonic ``now`` callable
(never ``time.time`` internally), so expiry is clock-controlled in tests.
Memory-bounded: at most ``max_entries`` live entries; the least recently
used entry is evicted first (a worker process can never grow the cache
without limit - low-storage/bounded-memory discipline).

Key versioning: callers embed a cache-key version segment (config
``cache_key_version``) in every key, so changing the key schema or the
cached value shape invalidates all prior entries by construction.
"""

from __future__ import annotations

import threading
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass

from app.resilience.metrics import ResilienceMetrics

__all__ = ["TTLCache"]


@dataclass
class _Entry:
    stored_at: float
    value: object


class TTLCache:
    """Thread-safe LRU cache with a single TTL for all entries."""

    def __init__(
        self,
        *,
        ttl_seconds: float,
        max_entries: int,
        now: Callable[[], float],
        metrics: ResilienceMetrics | None = None,
    ) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        self._ttl = ttl_seconds
        self._max_entries = max_entries
        self._now = now
        self._metrics = metrics
        self._lock = threading.Lock()
        self._entries: OrderedDict[str, _Entry] = OrderedDict()

    def get(self, key: str) -> object | None:
        """Return the live value for ``key`` or ``None`` (absent/expired).

        Expired entries are removed on observation; the caller decides how to
        count hits/misses (the fetcher emits ``cache_hit``/``cache_miss``).
        """
        hit = self.get_with_age(key)
        return None if hit is None else hit[0]

    def get_with_age(self, key: str) -> tuple[object, float] | None:
        """Return ``(value, age_seconds)`` for a live entry or ``None``.

        ADDITIVE accessor (task M2-T006): the contract-1.3.0 typed
        ``reproducibility.staleness`` object must state the served snapshot's
        age on cache-hit serves, so the cache exposes the age it already
        computes for expiry. Same semantics as ``get`` (expired entries
        removed on observation, LRU order refreshed); the age comes from the
        injected monotonic ``now`` callable - deterministic in tests, never a
        wall-clock guess.
        """
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            age = self._now() - entry.stored_at
            if age > self._ttl:
                del self._entries[key]
                if self._metrics is not None:
                    self._metrics.emit("cache_expired", key=key, age_seconds=age)
                return None
            self._entries.move_to_end(key)
            return entry.value, age

    def put(self, key: str, value: object) -> None:
        with self._lock:
            self._entries[key] = _Entry(stored_at=self._now(), value=value)
            self._entries.move_to_end(key)
            while len(self._entries) > self._max_entries:
                evicted_key, _ = self._entries.popitem(last=False)
                if self._metrics is not None:
                    self._metrics.emit("cache_evicted", key=evicted_key)

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)
