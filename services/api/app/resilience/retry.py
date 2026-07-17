"""Retry-After parsing and jittered bounded exponential backoff
(task M1-T009 items B/C, scenarios S2/S3).

Grounding (never guessed):

- The official Socrata app-tokens documentation (dev.socrata.com/docs/
  app-tokens; M1-T001 evidence E7, re-cited by the M1-T003/M1-T004 source
  registry drafts) documents ONLY the HTTP 429 status as the throttle
  signal - it documents neither a response body shape nor a ``Retry-After``
  guarantee (fixture F07 notes record this explicitly). Therefore:
  when a 429 carries ``Retry-After``, it is honored EXACTLY per the generic
  HTTP semantics of RFC 9110 section 10.2.3 (delay-seconds or HTTP-date);
  when absent or unparseable, the layer falls back to jittered backoff.
- Backoff is AWS-style "full jitter": ``uniform(0, min(cap, base * 2^(n-1)))``
  drawn from an injected seeded RNG, so retry storms decorrelate while every
  test remains deterministic.

No wall-clock or RNG state is read from the environment: callers inject
``wall_now`` (for HTTP-date arithmetic) and ``rng``.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from random import Random

__all__ = ["backoff_delay", "parse_retry_after"]

# RFC 9110 delay-seconds: a non-negative decimal integer.
_DELAY_SECONDS_RE = re.compile(r"^\d{1,10}$")


def parse_retry_after(
    raw: str | None, *, wall_now: Callable[[], datetime]
) -> float | None:
    """Parse a ``Retry-After`` value into non-negative seconds.

    Supports both RFC 9110 forms:

    - delay-seconds (``"7"``) -> 7.0
    - HTTP-date (``"Fri, 17 Jul 2026 08:00:00 GMT"``) -> seconds between
      the injected ``wall_now()`` and that date, clamped at 0.

    Returns ``None`` for absent/unparseable values (the caller falls back to
    jittered backoff; an untrusted header can never crash the retry engine).
    """
    if raw is None or not isinstance(raw, str):
        return None
    value = raw.strip()
    if not value:
        return None
    if _DELAY_SECONDS_RE.match(value):
        return float(int(value))
    try:
        moment = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if moment is None:
        return None
    if moment.tzinfo is None:
        # RFC 9110: HTTP-dates are always GMT.
        moment = moment.replace(tzinfo=UTC)
    return max(0.0, (moment - wall_now()).total_seconds())


def backoff_delay(
    attempt: int, *, base_seconds: float, cap_seconds: float, rng: Random
) -> float:
    """Full-jitter delay before retry number ``attempt`` (1-based: the delay
    scheduled AFTER the ``attempt``-th failed try).

    ``uniform(0, min(cap, base * 2^(attempt-1)))`` - bounded above by the
    exponential term and the cap, bounded below by 0. Deterministic for a
    seeded ``rng``.
    """
    if attempt < 1:
        raise ValueError("attempt must be >= 1")
    bound = min(cap_seconds, base_seconds * (2 ** (attempt - 1)))
    return rng.uniform(0.0, bound)
