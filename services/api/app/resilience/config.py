"""Resilience configuration (task M1-T009).

Every threshold is injectable for deterministic tests and configurable per
deployment through ``RESILIENCE_*`` environment variables. Invalid values
fail LOUDLY at startup (same policy as ``app.main._parse_allowed_origins``):
a misconfigured deploy must fail health checks rather than silently run with
guessed resilience behavior.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, fields

__all__ = ["ResilienceConfig"]

_ENV_PREFIX = "RESILIENCE_"


@dataclass(frozen=True)
class ResilienceConfig:
    """Closed set of resilience tunables with production defaults.

    Defaults rationale (documented, not guessed):

    - ``cache_ttl_seconds`` 900: PLUTO releases change quarterly/minor
      (README 26v1 release model); a 15-minute per-BBL response cache cannot
      hide a release while cutting repeat paid traffic. ``retrieved_at``
      provenance always shows the actual retrieval moment.
    - ``retry_max_attempts`` 3 / ``backoff_base_seconds`` 0.5 mirror the
      accepted M1-T002 connector budget; ``backoff_cap_seconds`` bounds the
      exponential term; jitter is full-jitter uniform (see retry.py).
    - ``retry_after_max_wait_seconds``: an upstream ``Retry-After`` larger
      than this is honored by NOT retrying (typed rate_limited failure
      immediately) - the platform never blocks a request thread for minutes.
    - ``breaker_failure_threshold``/``breaker_cooldown_seconds``: consecutive
      FINAL fetch failures (post-retry) open the per-source circuit; while
      open, calls fast-fail (or serve last-known-good) without upstream I/O.
    - ``lkg_max_age_seconds`` 86400: a last-known-good snapshot older than
      24h is refused (typed failure) rather than served - bounded staleness.
    - ``*_max_entries``: hard memory bounds; oldest entries are evicted (the
      cache/LKG stores can never grow without limit in a worker process).
    """

    cache_ttl_seconds: float = 900.0
    cache_key_version: str = "v1"
    cache_max_entries: int = 10_000
    retry_max_attempts: int = 3
    backoff_base_seconds: float = 0.5
    backoff_cap_seconds: float = 30.0
    retry_after_max_wait_seconds: float = 120.0
    breaker_failure_threshold: int = 5
    breaker_cooldown_seconds: float = 60.0
    lkg_max_age_seconds: float = 86_400.0
    lkg_max_entries: int = 10_000

    def __post_init__(self) -> None:
        positive_floats = (
            "cache_ttl_seconds",
            "backoff_base_seconds",
            "backoff_cap_seconds",
            "retry_after_max_wait_seconds",
            "breaker_cooldown_seconds",
            "lkg_max_age_seconds",
        )
        for name in positive_floats:
            value = getattr(self, name)
            if not isinstance(value, int | float) or isinstance(value, bool) \
                    or not value > 0:
                raise ValueError(f"{name} must be a positive number; got {value!r}")
        positive_ints = (
            "cache_max_entries",
            "retry_max_attempts",
            "breaker_failure_threshold",
            "lkg_max_entries",
        )
        for name in positive_ints:
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValueError(f"{name} must be an integer >= 1; got {value!r}")
        if not self.cache_key_version or not isinstance(self.cache_key_version, str):
            raise ValueError("cache_key_version must be a non-empty string")

    @classmethod
    def from_env(cls, environ: Mapping[str, str] = os.environ) -> ResilienceConfig:
        """Build a config from ``RESILIENCE_<UPPERCASE_FIELD>`` variables.

        Unset variables keep the documented defaults. Unparseable or invalid
        values raise ``RuntimeError`` at startup (loud failure, never a
        silent fallback that changes production behavior).
        """
        values: dict[str, object] = {}
        for spec in fields(cls):
            raw = environ.get(f"{_ENV_PREFIX}{spec.name.upper()}")
            if raw is None or raw == "":
                continue
            if spec.type in ("float", float):
                try:
                    values[spec.name] = float(raw)
                except ValueError as exc:
                    raise RuntimeError(
                        f"{_ENV_PREFIX}{spec.name.upper()} must be a number; "
                        f"got {raw!r}"
                    ) from exc
            elif spec.type in ("int", int):
                try:
                    values[spec.name] = int(raw)
                except ValueError as exc:
                    raise RuntimeError(
                        f"{_ENV_PREFIX}{spec.name.upper()} must be an integer; "
                        f"got {raw!r}"
                    ) from exc
            else:
                values[spec.name] = raw
        try:
            return cls(**values)  # type: ignore[arg-type]
        except ValueError as exc:
            raise RuntimeError(f"invalid resilience configuration: {exc}") from exc
