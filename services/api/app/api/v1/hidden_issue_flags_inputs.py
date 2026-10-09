"""Inputs seam for the internal §8a hidden-issue-flags read route (lane C, packet W2).

The route (``app.api.v1.hidden_issue_flags_read``) is thin: it shapes and
validates the four §8a flag groups into the W0 ``hidden_issue_flags`` contract
envelope and gates it behind a flag. The DOMAIN inputs it needs - a built
property profile (for the map-based and site-shape-and-street groups' recorded
PLUTO columns) and the B-07 combined ``SiteGeometry`` (for the site-shape group)
- are produced here, through an INJECTED provider so the route's tests run fully
offline on recorded fixtures (the 215-16 Northern benchmark pack). No legal logic
and no zoning math live here: the §8a layer carries NO legal meaning and computes
nothing about the law; a flag only reports what the sourced data already shows,
or says the source is not available ("Check needed", never a guess). Legal
determinations belong to the rule engine (Lane A) and a qualified reviewer at G6,
never here.

Layering mirrors :mod:`app.api.v1.study_inputs` (request D-1 slice 1), so one
seam shape serves both internal reads:

- :func:`assemble_hidden_issue_flag_inputs` is the PURE assembly: a
  ``PlutoFetchResult`` -> profile, and -> a single B-07 ``SiteLot`` -> lot choice
  -> multi-lot site (through the LANE_B-gated entry) -> the combined geometry. It
  performs no I/O. It builds LESS than the study seam (no site facts): the four
  §8a groups read the profile and the geometry directly, and for this slice carry
  no site-fact ``fact_refs`` (existing floor area is not wired - below).
- :func:`pluto_hidden_issue_flag_inputs_provider` turns a PLUTO fetcher (the same
  ``(canonical_bbl, correlation_id) -> PlutoFetchResult`` seam the properties
  route injects) into a :data:`HiddenIssueFlagInputsProvider`. Tests inject a
  fixture fetcher; the DEFAULT provider binds the live resilient fetcher (below).
- :func:`default_hidden_issue_flag_inputs_provider` is the route's default
  dependency: the LIVE PLUTO path through the resilient fetcher the properties
  route uses (:func:`app.api.v1.properties.get_pluto_fetcher`). Tests override the
  dependency so the suite runs fully offline; production keeps the route flag off
  regardless and stays blocked on B-001 auth + the route-local rate limit.

The profile, lot choice and combined geometry are Lane B behaviour, produced only
through ``derive_multi_lot_site_if_enabled`` (the LANE_B_ENABLED gate). When that
gate is off the inputs are unavailable (fail safe), never fabricated.

Slice bounds (documented, not hidden; these are the §8a inputs the groups take
that this seam does NOT supply yet, so the route passes the group default):

- ``existing_floor_area`` is NOT wired (B-05): the existing-building and
  zoning-lot-history groups receive None, so "larger than today" and the recorded
  zoning-lot reminders stay "Check needed" and carry no ``fact_refs`` (B-09 open
  question - slice 4 (a) answered here: this seam DOES pass the B-07 geometry;
  existing floor area is a later slice).
- ``as_of_right_allowance`` is ALWAYS None: the zoning-math engine (Lane A) is off
  in these packets, so no allowance is ever supplied and the existing-building
  "larger than today" item is never decided here.
- ``recorded_documents`` is empty: no ACRIS recorded-document feed is wired in, so
  the zoning-lot-history reminders are "Check needed" (never a verified or
  combined zoning-lot claim).
- ``transit_parking`` is NOT passed (B-10 open question (b) is not decided here),
  so the map-based group emits exactly its nine §8a items, no opt-in tenth zone
  flag.

One tax lot per call (no MapPLUTO outline fetch and no condo base-lot resolution
yet, so a multi-lot or condo input resolves to the single entered lot, and a
condo unit-lot no-match is labelled ``condo`` on the fail-safe 503).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Any

from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.pluto_soda import (
    CONDO_UNIT_LOT_RANGE,
    PlutoConnectorError,
    PlutoFetchResult,
)
from app.profile.builder import build_property_profile
from app.spatial.multi_lot_site import (
    build_lot_choice,
    derive_multi_lot_site_if_enabled,
    site_lot_from_sources,
)
from app.spatial.site_geometry import SiteGeometry

__all__ = [
    "PlutoFetcher",
    "HiddenIssueFlagInputs",
    "HiddenIssueFlagInputsProvider",
    "HiddenIssueFlagInputsUnavailableError",
    "assemble_hidden_issue_flag_inputs",
    "default_hidden_issue_flag_inputs_provider",
    "pluto_hidden_issue_flag_inputs_provider",
]


@dataclass(frozen=True)
class HiddenIssueFlagInputs:
    """The domain inputs the §8a flags route composes into the four flag groups.

    ``bbl`` is the tax lot the groups describe (the PLUTO record's canonical BBL,
    which is also ``profile`` identity, so the groups' own identity checks hold).
    ``profile`` is a built property profile (``app.profile.builder``), read for the
    map-based and site-shape groups' recorded PLUTO columns. ``site_geometry`` is
    the B-07 combined ``SiteGeometry`` for the selected lots (None when B-07 does
    not offer a combination), read by the site-shape-and-street group.
    """

    bbl: str
    profile: Mapping[str, Any]
    site_geometry: SiteGeometry | None = None


class HiddenIssueFlagInputsUnavailableError(Exception):
    """The §8a flag inputs could not be produced (upstream unavailable, the Lane B
    gate is off, or PLUTO holds no record). The route maps this to a bounded
    ``503 inputs_unavailable`` - never a fabricated flag document."""

    def __init__(self, message: str, *, reason: str) -> None:
        super().__init__(message)
        self.reason = reason


# A flag-inputs provider. Injected through FastAPI dependency_overrides so the
# route's tests run offline on recorded fixtures. The call convention is
# ``(canonical_bbl, correlation_id, *, selected=None) -> HiddenIssueFlagInputs``
# (the same shape the study-read seam uses), so one dependency-override pattern
# serves both internal reads. ``Callable[..., HiddenIssueFlagInputs]`` because the
# keyword-only ``selected`` cannot be expressed in ``Callable[[...], ...]``.
HiddenIssueFlagInputsProvider = Callable[..., HiddenIssueFlagInputs]

# (canonical_bbl, correlation_id) -> PlutoFetchResult. The SAME fetcher seam the
# properties and study-read routes inject.
PlutoFetcher = Callable[[str, str], PlutoFetchResult]


def _no_record_reason(bbl: str) -> str:
    """A bounded platform token distinguishing a CONDO unit-lot no-match (resolve
    the condominium BILLING BBL and retry) from a GENERIC no-match, using the
    connector's OWN published condo lot-number range. A lot-NUMBER classification
    (PLUTO carries one record per complex under the billing lot), NOT geometry or
    adjacency. Used only to label the fail-safe 503 for observability; the HTTP
    status is unchanged. Mirrors ``app.api.v1.study_inputs._no_record_reason``."""
    try:
        lot = normalize_bbl(bbl).lot
    except BBLValidationError:
        return "no_match"
    low, high = CONDO_UNIT_LOT_RANGE
    return "condo" if low <= lot <= high else "no_match"


def assemble_hidden_issue_flag_inputs(
    pluto_result: PlutoFetchResult,
    *,
    selected: Sequence[str] | None = None,
    clock: Callable[[], datetime] | None = None,
    env: Mapping[str, str] | None = None,
) -> HiddenIssueFlagInputs:
    """Build :class:`HiddenIssueFlagInputs` from a successful PLUTO fetch (PURE).

    ``selected`` is the lot selection; None is the default "use all". ``env``
    supplies the LANE_B_ENABLED gate (defaults to the process environment).

    Raises:
        HiddenIssueFlagInputsUnavailableError: PLUTO holds no usable single-lot
            record, or the Lane B gate is off (so the combined site is not
            produced). The flag document is withheld, never fabricated.
    """
    if pluto_result.status != "ok":
        # A no-match is a legitimate result (valid BBL, no PLUTO record). A condo
        # UNIT-lot and a plain no-match map to DISTINCT reasons so the fail-safe
        # 503 is observable; both withhold the flags.
        raise HiddenIssueFlagInputsUnavailableError(
            f"PLUTO returned {pluto_result.status!r} for {pluto_result.bbl}; no §8a "
            "flag document is produced (a record is required).",
            reason=_no_record_reason(pluto_result.bbl),
        )
    builder_kwargs = {} if clock is None else {"clock": clock}
    profile = build_property_profile(pluto_result, **builder_kwargs)
    # One tax lot from the PLUTO row (no MapPLUTO outline yet - this slice). B-07's
    # adapter records the absence of an outline; the lot size is the city-recorded
    # area, or unknown (never 0). The lot choice + combined site are the LANE_B-
    # gated entry, so the geometry is produced only when Lane B is on.
    site_lot = site_lot_from_sources(pluto_result.bbl, None, pluto_result)
    choice = build_lot_choice([pluto_result.bbl], {pluto_result.bbl: site_lot})
    site = derive_multi_lot_site_if_enabled(choice, selected, env=env)
    if site is None:
        raise HiddenIssueFlagInputsUnavailableError(
            "the multi-lot site gate (LANE_B_ENABLED) is off, so the combined site is "
            "not produced; the §8a flag document is withheld rather than fabricated.",
            reason="lane_b_disabled",
        )
    return HiddenIssueFlagInputs(
        bbl=pluto_result.bbl,
        profile=profile,
        site_geometry=site.geometry,
    )


def pluto_hidden_issue_flag_inputs_provider(
    fetcher: PlutoFetcher,
    *,
    clock: Callable[[], datetime] | None = None,
    env: Mapping[str, str] | None = None,
) -> HiddenIssueFlagInputsProvider:
    """A :data:`HiddenIssueFlagInputsProvider` over a PLUTO ``fetcher``.

    Fetches the PLUTO record, then assembles the flag inputs. A typed PLUTO
    connector failure or a no-record result becomes
    :class:`HiddenIssueFlagInputsUnavailableError` (the route's bounded 503), never
    a partial or fabricated flag document.
    """

    def provider(
        canonical_bbl: str,
        correlation_id: str,
        *,
        selected: Sequence[str] | None = None,
    ) -> HiddenIssueFlagInputs:
        try:
            result = fetcher(canonical_bbl, correlation_id)
        except PlutoConnectorError as exc:
            raise HiddenIssueFlagInputsUnavailableError(
                "the official PLUTO source could not be reached; the §8a flag document "
                "is withheld and is safe to retry.",
                reason=exc.error_type,
            ) from exc
        return assemble_hidden_issue_flag_inputs(
            result, selected=selected, clock=clock, env=env
        )

    return provider


@lru_cache(maxsize=1)
def _live_hidden_issue_flag_inputs_provider() -> HiddenIssueFlagInputsProvider:
    """The live flag-inputs provider, bound to the SAME resilient PLUTO fetcher the
    properties route uses (:func:`app.api.v1.properties.get_pluto_fetcher` ->
    :func:`app.resilience.fetcher.build_default_resilient_fetcher`): a TTL cache,
    bounded retries with jittered backoff, a per-source circuit breaker and
    last-known-good serving wrap the accepted connector. Built once, LAZILY, so
    importing this module reads no resilience env and makes no network call; the
    first live request builds the process-wide fetcher. The import is local to
    avoid any import-time coupling to the properties route."""
    from app.api.v1.properties import get_pluto_fetcher

    return pluto_hidden_issue_flag_inputs_provider(get_pluto_fetcher())


def default_hidden_issue_flag_inputs_provider(
    canonical_bbl: str,
    correlation_id: str,
    *,
    selected: Sequence[str] | None = None,
) -> HiddenIssueFlagInputs:
    """Route default: the LIVE PLUTO path through the resilient fetcher the
    properties route uses.

    Delegates to :func:`_live_hidden_issue_flag_inputs_provider`, so a real request
    reaches official PLUTO through the connector-resilience layer. Every upstream
    failure still maps to the route's typed 503; a no-match (including a condo
    unit-lot) withholds the flags rather than fabricating them. Tests override the
    dependency so the suite runs fully offline; this live default is never
    exercised on the network in tests.

    The route flag is off in production regardless, and production stays blocked on
    B-001 auth plus the route-local rate limit before any unauthenticated
    live-fetch surface is reachable.
    """
    return _live_hidden_issue_flag_inputs_provider()(
        canonical_bbl, correlation_id, selected=selected
    )
