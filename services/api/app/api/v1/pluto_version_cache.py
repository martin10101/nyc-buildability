"""PLUTO published-version probe cache + the study published-version set (lane C, request B-4).

Lane C integration helpers that let study assembly consult Lane B's PLUTO
published-version probe (:func:`app.connectors.pluto_version_probe.fetch_published_version`)
without turning the pure assembly into a network-coupled, once-per-study caller.
Two pieces, both inside the Lane C hot path (``services/api/app/api/**``):

- :class:`CachedVersionProbe` - a small, process-wide, thread-safe TTL cache over
  a :data:`VersionProbe`. The published PLUTO release changes at most monthly
  (minor) / quarterly (major) per the PLUTO README release model, while a burst of
  studies may assemble many times, so one SUCCESSFUL observation is shared for
  :data:`VERSION_PROBE_TTL_SECONDS` (15 minutes) and the tokenless shared city
  pool is not hit once per study (polite shared-pool use). A FAILURE is never
  cached, so a transient outage never pins an absent observation and the next
  study re-probes. Bounded to one entry (one dataset). The clock is injectable for
  deterministic tests.
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


def default_version_probe(correlation_id: str) -> PlutoPublishedVersion:
    """The LIVE probe: Lane B's :func:`~app.connectors.pluto_version_probe.fetch_published_version`
    with its own transport, bounded retry and typed error taxonomy (the same ones
    ``fetch_by_bbl`` uses). The study's correlation id is carried into the probe's
    provenance and structured logs."""
    return fetch_published_version(correlation_id=correlation_id)


class CachedVersionProbe:
    """Thread-safe, bounded (one entry) TTL cache over a :data:`VersionProbe`.

    Only a SUCCESSFUL result is cached, for ``ttl_seconds``. A failure re-raises
    and is never stored, so the next call re-probes - a transient outage never pins
    an absent/stale observation (request B-4). ``clock`` is an injectable
    monotonic-style source for deterministic tests (default :func:`time.monotonic`).

    The probe runs OUTSIDE the lock, so a slow network probe never serializes all
    study assembly; a cold/expired-cache burst may issue a few concurrent probes
    (acceptable - politeness is "one per process per 15 min", not strict
    single-flight). The lock guards only the tiny read/update of the single slot.
    """

    def __init__(
        self,
        probe: VersionProbe,
        *,
        ttl_seconds: float = VERSION_PROBE_TTL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._probe = probe
        self._ttl = ttl_seconds
        self._clock = clock
        self._lock = threading.Lock()
        self._cached: PlutoPublishedVersion | None = None
        self._stored_at = 0.0

    def __call__(self, correlation_id: str) -> PlutoPublishedVersion:
        now = self._clock()
        with self._lock:
            if self._cached is not None and now - self._stored_at < self._ttl:
                return self._cached
        # Failures propagate here and are NEVER stored (fail-closed cache).
        result = self._probe(correlation_id)
        with self._lock:
            self._cached = result
            self._stored_at = now
        return result


def cached_default_version_probe() -> CachedVersionProbe:
    """A process-wide TTL cache over :func:`default_version_probe`. Built once by
    the live study-inputs provider (``study_inputs._live_study_inputs_provider``,
    itself ``lru_cache``-d), so the whole process shares one freshness
    observation."""
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
