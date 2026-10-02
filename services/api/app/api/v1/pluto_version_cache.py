"""PLUTO published-version probe cache + the study published-version set (lane C, request B-4).

Lane C integration helpers that let study assembly consult Lane B's PLUTO
published-version probe (:func:`app.connectors.pluto_version_probe.fetch_published_version`)
without turning the pure assembly into a network-coupled, once-per-study caller.
Two pieces, both inside the Lane C hot path (``services/api/app/api/**``):

- :class:`CachedVersionProbe` - the GUARD on the otherwise-unguarded probe
  (request B-4 rework 1), a small, process-wide, thread-safe success + negative
  cache over a :data:`VersionProbe`. The published PLUTO release changes at most
  monthly (minor) / quarterly (major) per the PLUTO README release model, so one
  SUCCESSFUL observation is shared for :data:`VERSION_PROBE_TTL_SECONDS`
  (15 minutes) and the tokenless shared city pool is not hit once per study. A
  typed FAILURE opens a short breaker: the stored error is re-raised (the identical
  fail-closed outcome) for :data:`NEGATIVE_CACHE_TTL_SECONDS` (60 s) WITHOUT calling
  the probe, so an NYC Open Data outage cannot make every admitted request re-probe.
  The live probe itself runs with ONE attempt and a 5 s timeout
  (:data:`PROBE_MAX_ATTEMPTS` / :data:`PROBE_TIMEOUT_SECONDS`), since the published
  version is optional and fail-closed is always safe. Bounded to one entry (one
  dataset). The clock is injectable for deterministic tests.
- :func:`published_versions_for_study` - the published-on-record set that feeds
  :func:`app.profile.data_versions.assess_data_versions`. The base is the
  retrievals themselves (:func:`~app.profile.data_versions.published_from_pins`);
  when PLUTO pins are present and a probe is injected (Lane B on), it ALSO consults
  the probe, FAILING CLOSED on any typed probe failure (request B-4 decision: the
  PLUTO pins read ``version_unknown``, never a probe-masked ``current``).

No legal logic and no zoning math. Deterministic apart from the injected probe's
own I/O; a probe failure is caught and surfaced (logged), never propagated, so a
study still assembles on a probe outage (no 5xx because of the probe).
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable, Iterable

from app.connectors.pluto_soda import PlutoConnectorError
from app.connectors.pluto_version_probe import (
    PlutoPublishedVersion,
    fetch_published_version,
)
from app.profile.data_versions import (
    PinnedSource,
    PublishedVersion,
    published_from_pins,
)
from app.profile.pluto_published_version import published_version_from_probe
from app.profile.site_facts import PLUTO_DATASET_NAME

__all__ = [
    "NEGATIVE_CACHE_TTL_SECONDS",
    "PROBE_MAX_ATTEMPTS",
    "PROBE_TIMEOUT_SECONDS",
    "VERSION_PROBE_TTL_SECONDS",
    "CachedVersionProbe",
    "VersionProbe",
    "cached_default_version_probe",
    "default_version_probe",
    "published_versions_for_study",
]

logger = logging.getLogger("app.api.v1.pluto_version_cache")

# A version probe: ``(correlation_id) -> the city's currently published PLUTO
# release``, raising the connector's typed :class:`PlutoConnectorError` on any
# failure (timeout / rate-limited / source unavailable / schema drift). The
# default binds the live ``fetch_published_version``; route tests and the e2e
# harness inject a probe over a routed/fake transport so nothing touches the
# network.
VersionProbe = Callable[[str], PlutoPublishedVersion]

# One SUCCESSFUL probe is shared per process for this long (request B-4). The
# published PLUTO release changes at most monthly / quarterly, so 15 minutes keeps
# a burst of studies to a single freshness observation while staying far fresher
# than the release cadence.
VERSION_PROBE_TTL_SECONDS = 900.0

# A typed probe FAILURE suppresses outbound calls for this long (negative cache /
# breaker, request B-4 rework 1): the published version is OPTIONAL information and
# fail-closed-to-version_unknown is always safe, so repeated outbound probes during
# an NYC Open Data outage are not worth the added latency or shared-pool load.
NEGATIVE_CACHE_TTL_SECONDS = 60.0

# The live probe is called with ONE attempt and a short timeout (request B-4
# rework 1): optional information guarded by the breaker, so it must never add the
# data path's up-to-3-attempt + backoff latency (~31.5 s) to a study assembly.
PROBE_MAX_ATTEMPTS = 1
PROBE_TIMEOUT_SECONDS = 5.0


def default_version_probe(correlation_id: str) -> PlutoPublishedVersion:
    """The LIVE probe: Lane B's :func:`~app.connectors.pluto_version_probe.fetch_published_version`
    with its own transport and typed error taxonomy (the same ones ``fetch_by_bbl``
    uses), but called with ONE attempt and a 5 s timeout (request B-4 rework 1):
    the published version is optional and fail-closed is always safe, so the probe
    never adds the data path's multi-attempt + backoff latency. Outbound-call
    frequency is further bounded by :class:`CachedVersionProbe`'s success + negative
    caches. The study's correlation id is carried into the probe's provenance and
    structured logs."""
    return fetch_published_version(
        correlation_id=correlation_id,
        max_attempts=PROBE_MAX_ATTEMPTS,
        timeout=PROBE_TIMEOUT_SECONDS,
    )


class CachedVersionProbe:
    """Thread-safe, bounded (one entry) success + negative cache over a :data:`VersionProbe`.

    This is the GUARD on the otherwise-unguarded probe (request B-4 rework 1); the
    probe cannot ride the data path's resilient fetcher (that wraps a
    ``(bbl) -> PlutoFetchResult`` shape and lives in Lane B), so the guard lives
    here and bounds outbound-call frequency two ways:

    * success cache: a SUCCESSFUL result is served for ``ttl_seconds`` (15 min), so
      a burst of studies shares one freshness observation;
    * negative cache / breaker: after a typed :class:`PlutoConnectorError` the stored
      error is RE-RAISED (the identical fail-closed outcome) for
      ``negative_ttl_seconds`` (60 s) WITHOUT calling the probe, so an NYC Open Data
      outage cannot make every admitted request re-probe (no multi-attempt latency,
      no shared-pool hammering, no thread-pool exhaustion). After the window a single
      probe is allowed again (half-open); a success clears the negative state and is
      cached for the full 15 min.

    A negative-cache hit is logged once at INFO so the suppression is visible; the
    caller's WARNING fail-closed log (``study_pluto_version_probe_failed``) is
    unchanged because the stored typed error still reaches it. ``clock`` is an
    injectable monotonic-style source for deterministic tests (default
    :func:`time.monotonic`).

    The probe runs OUTSIDE the lock, so a slow probe never serializes all study
    assembly; the lock guards only the tiny read/update of the two single slots.
    """

    def __init__(
        self,
        probe: VersionProbe,
        *,
        ttl_seconds: float = VERSION_PROBE_TTL_SECONDS,
        negative_ttl_seconds: float = NEGATIVE_CACHE_TTL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._probe = probe
        self._ttl = ttl_seconds
        self._negative_ttl = negative_ttl_seconds
        self._clock = clock
        self._lock = threading.Lock()
        self._cached: PlutoPublishedVersion | None = None
        self._stored_at = 0.0
        self._last_error: PlutoConnectorError | None = None
        self._failed_at = 0.0

    def __call__(self, correlation_id: str) -> PlutoPublishedVersion:
        now = self._clock()
        with self._lock:
            if self._cached is not None and now - self._stored_at < self._ttl:
                return self._cached
            last_error = self._last_error
            suppressed = (
                last_error is not None and now - self._failed_at < self._negative_ttl
            )
        if suppressed and last_error is not None:
            # Negative-cache / breaker-open hit: do NOT call the probe. Re-raise the
            # stored typed error so the caller fails closed to version_unknown
            # exactly as on a live failure (outcome unchanged).
            logger.info(
                "study_pluto_version_probe_suppressed correlation_id=%s error_type=%s",
                correlation_id,
                last_error.error_type,
            )
            raise last_error
        try:
            result = self._probe(correlation_id)
        except PlutoConnectorError as exc:
            # Open the breaker: never cache a success; remember the failure so the
            # next NEGATIVE_CACHE_TTL_SECONDS of calls are suppressed.
            with self._lock:
                self._last_error = exc
                self._failed_at = now
            raise
        with self._lock:
            self._cached = result
            self._stored_at = now
            self._last_error = None  # recovery clears the negative state
        return result


def cached_default_version_probe() -> CachedVersionProbe:
    """A process-wide success + negative cache over :func:`default_version_probe`.
    Built once by the live study-inputs provider
    (``study_inputs._live_study_inputs_provider``, itself ``lru_cache``-d), so the
    whole process shares one freshness observation and one breaker."""
    return CachedVersionProbe(default_version_probe)


def published_versions_for_study(
    pins: Iterable[PinnedSource],
    *,
    version_probe: VersionProbe | None,
    correlation_id: str,
) -> tuple[PublishedVersion, ...]:
    """The published-on-record set feeding ``assess_data_versions`` for a study.

    Base = the retrievals themselves (``published_from_pins``). When PLUTO pins are
    present AND a probe is injected (Lane B on), ALSO consult the PLUTO version
    probe (request B-4):

    * success -> ADD the probe's ``PublishedVersion`` (so a lot pinned to an older
      release reads ``out_of_date``, which retrieval-only never could);
    * ANY typed probe failure (timeout / rate-limited / source unavailable / schema
      drift) -> FAIL CLOSED: drop the probe AND the PLUTO self-observations, so the
      PLUTO pins have nothing to compare with and ``assess_source`` returns
      ``version_unknown`` - never a probe-masked ``current``. Other datasets'
      self-observations are kept unchanged. The failure is logged at WARNING with
      the correlation id and the bounded error type (no secrets, no URL/token).

    With no probe (``version_probe is None``) or no PLUTO pins, this is
    retrieval-only (``published_from_pins``), the pre-B-4 behaviour: retrieval-only
    is acceptable only when no probe was attempted BY DESIGN, never as a fallback
    after a probe failed (request B-4).
    """
    pins = tuple(pins)
    self_observations = published_from_pins(pins)
    has_pluto_pin = any(pin.dataset == PLUTO_DATASET_NAME for pin in pins)
    if version_probe is None or not has_pluto_pin:
        return self_observations
    try:
        probe = version_probe(correlation_id)
    except PlutoConnectorError as exc:
        logger.warning(
            "study_pluto_version_probe_failed correlation_id=%s error_type=%s",
            correlation_id,
            exc.error_type,
        )
        return tuple(
            seen for seen in self_observations if seen.dataset != PLUTO_DATASET_NAME
        )
    return (*self_observations, published_version_from_probe(probe))
