"""Study-inputs seam for the internal study-read route (lane C, request D-1 slice 1).

The route (``app.api.v1.study_read``) is thin: it shapes and validates a contract
``study setup`` document and gates it behind a flag. The DOMAIN inputs it needs -
B-07's lot choice and the derived multi-lot site, and B-02/B-03's site facts -
are produced here, through an INJECTED provider so the route's tests run fully
offline on recorded fixtures (the 215-16 Northern benchmark pack). No legal logic
and no zoning math live here: the lot choice, the combination check with its
reason, and the site facts all come VERBATIM from the accepted B-07/B-02
producers (``app.spatial.multi_lot_site`` / ``app.profile.site_facts``); this
module only carries them.

Layering:

- :func:`assemble_study_inputs` is the PURE assembly: a ``PlutoFetchResult`` ->
  profile -> B-02 site facts (each carrying B-06's ``source.version_check`` status,
  request B-3; published versions = the retrievals themselves), and -> a single
  B-07 :class:`SiteLot` -> lot choice -> multi-lot site (through the LANE_B-gated
  entry). It performs no I/O, so the route's tests exercise the real B-02/B-07
  pipeline on a recorded PLUTO body. An optional ``selected`` (a sequence of
  canonical BBLs) is passed VERBATIM to B-07's ``derive_multi_lot_site`` for a
  re-pick; None is the default "use all".
- :func:`pluto_study_inputs_provider` turns a PLUTO fetcher (the same
  ``(canonical_bbl, correlation_id) -> PlutoFetchResult`` seam the properties
  route injects) into a :data:`StudyInputsProvider`. Tests inject a fixture
  fetcher; the DEFAULT provider binds the live resilient fetcher (below).
- :func:`default_study_inputs_provider` is the route's default dependency. It is
  now the LIVE PLUTO path (slice 2, NB1): it binds
  :func:`pluto_study_inputs_provider` to the resilient fetcher the properties
  route uses (:func:`app.resilience.fetcher.build_default_resilient_fetcher` via
  :func:`app.api.v1.properties.get_pluto_fetcher`). Tests override the dependency
  so the suite runs fully offline; production keeps the route flag off regardless
  and stays blocked on B-001 auth + the route-local rate limit (NB1/NB2).

Lot choice and multi-lot site are Lane B behaviour, so they are produced only
through ``derive_multi_lot_site_if_enabled`` (the LANE_B_ENABLED gate). When that
gate is off the inputs are unavailable (fail safe), never fabricated.

Slice bounds (documented, not hidden): one tax lot per call (no MapPLUTO outline
fetch and no condo base-lot resolution yet, so a multi-lot or condo input
resolves to the single entered lot, and a condo unit-lot no-match is labelled
``condo`` on the fail-safe 503); no street data, so frontage/street-width facts
are not added here; ``address`` is null (BBL-only) until the address-confirm step
supplies the confirmed address. These are later slices.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache

from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.pluto_soda import (
    CONDO_UNIT_LOT_RANGE,
    PlutoConnectorError,
    PlutoFetchResult,
)
from app.profile.builder import build_property_profile
from app.profile.data_versions import (
    assess_data_versions,
    pins_from_site_facts,
    published_from_pins,
)
from app.profile.fact_version_check import attach_version_check
from app.profile.site_facts import build_site_facts
from app.spatial.multi_lot_site import (
    LotChoice,
    MultiLotSite,
    build_lot_choice,
    derive_multi_lot_site_if_enabled,
    site_lot_from_sources,
)

__all__ = [
    "PlutoFetcher",
    "StudyInputs",
    "StudyInputsProvider",
    "StudyInputsUnavailableError",
    "assemble_study_inputs",
    "default_study_inputs_provider",
    "pluto_study_inputs_provider",
]


@dataclass(frozen=True)
class StudyInputs:
    """The domain inputs the study-read route composes into a study setup.

    ``lot_choice`` and ``site`` are the accepted B-07 result objects (the lot
    choice and the derived multi-lot site for the DEFAULT "use all" selection).
    ``site_facts`` are B-02 ``site_fact`` documents, each carrying the B-06
    ``source.version_check`` status for its source (contract 1.1.0, request B-3;
    a fact whose source has no dataset version stays 1.0.0 with no key).
    ``address`` is the confirmed address, or None when the property was reached
    by BBL only.
    """

    lot_choice: LotChoice
    site: MultiLotSite
    site_facts: tuple[dict, ...]
    address: str | None = None


class StudyInputsUnavailableError(Exception):
    """The study inputs could not be produced (upstream unavailable, the Lane B
    gate is off, or the live fetch shell is not wired yet). The route maps this
    to a bounded ``503 inputs_unavailable`` - never a fabricated study."""

    def __init__(self, message: str, *, reason: str) -> None:
        super().__init__(message)
        self.reason = reason


# A study-inputs provider. Injected through FastAPI dependency_overrides so the
# route's tests run offline on recorded fixtures. The call convention is
# ``(canonical_bbl, correlation_id, *, selected=None) -> StudyInputs``: the
# route passes ``selected`` ONLY on a re-pick (keyword, a list of canonical
# BBLs), so a provider that only serves the default "use all" selection keeps
# the two-positional-argument shape. ``Callable[..., StudyInputs]`` because the
# keyword-only ``selected`` cannot be expressed in ``Callable[[...], ...]``.
StudyInputsProvider = Callable[..., StudyInputs]


def _no_record_reason(bbl: str) -> str:
    """A bounded platform token distinguishing a CONDO unit-lot no-match (resolve
    the condominium BILLING BBL and retry) from a GENERIC no-match, using the
    connector's OWN published condo lot-number range. This is a lot-NUMBER
    classification (PLUTO carries one record per complex under the billing lot),
    NOT geometry or adjacency. Used only to label the fail-safe 503 for
    observability; the HTTP status is unchanged."""
    try:
        lot = normalize_bbl(bbl).lot
    except BBLValidationError:
        return "no_match"
    low, high = CONDO_UNIT_LOT_RANGE
    return "condo" if low <= lot <= high else "no_match"

# (canonical_bbl, correlation_id) -> PlutoFetchResult. The SAME fetcher seam the
# properties route injects; the live resilient fetcher is wired in a later slice.
PlutoFetcher = Callable[[str, str], PlutoFetchResult]


def assemble_study_inputs(
    pluto_result: PlutoFetchResult,
    *,
    selected: Sequence[str] | None = None,
    clock: Callable[[], datetime] | None = None,
    env: Mapping[str, str] | None = None,
    address: str | None = None,
) -> StudyInputs:
    """Build :class:`StudyInputs` from a successful PLUTO fetch result (PURE).

    ``selected`` is the lot selection; None is the default "use all". ``env``
    supplies the LANE_B_ENABLED gate (defaults to the process environment).

    Raises:
        StudyInputsUnavailableError: the Lane B gate is off (so the lot choice is
            not produced), or the fetch result is not a usable single-lot record.
    """
    if pluto_result.status != "ok":
        # A no-match is a legitimate result (the BBL is valid but PLUTO holds no
        # record). A condo UNIT-lot and a plain no-match are mapped to DISTINCT
        # reasons so the fail-safe 503 is observable; both withhold the study.
        raise StudyInputsUnavailableError(
            f"PLUTO returned {pluto_result.status!r} for {pluto_result.bbl}; no study "
            "setup is produced (a record is required).",
            reason=_no_record_reason(pluto_result.bbl),
        )
    builder_kwargs = {} if clock is None else {"clock": clock}
    profile = build_property_profile(pluto_result, **builder_kwargs)
    site_fact_set = build_site_facts(profile)
    # Attach each source's version status (B-06's "Out of date" rule) to the facts it
    # covers, so the status travels with the fact to Lane D/E and export_record.sources
    # (request docs/lanes/requests/B-3.md). Published versions are the retrievals
    # themselves (published_from_pins): a study is assembled per request with no durable
    # store yet, so "current" means "the newest version on record as of this retrieval",
    # and the assessor's reason names the retrieval time so that scope is explicit. A
    # version probe (e.g. PLUTO F09) that grows the published-on-record set is a later
    # slice. The bridge is pure: a fact whose source has no dataset version stays 1.0.0
    # with no version_check; references are not contract facts and carry none.
    pins = pins_from_site_facts(site_fact_set.facts)
    report = assess_data_versions(pins, published_from_pins(pins))
    site_facts = attach_version_check(site_fact_set.facts, report)
    # One tax lot from the PLUTO row (no MapPLUTO outline yet - slice 1). B-07's
    # adapter records the absence of an outline; the lot size is the city-recorded
    # area, or unknown (never 0).
    site_lot = site_lot_from_sources(pluto_result.bbl, None, pluto_result)
    choice = build_lot_choice([pluto_result.bbl], {pluto_result.bbl: site_lot})
    site = derive_multi_lot_site_if_enabled(choice, selected, env=env)
    if site is None:
        raise StudyInputsUnavailableError(
            "the multi-lot site gate (LANE_B_ENABLED) is off, so the lot choice is not "
            "produced; the study setup is withheld rather than fabricated.",
            reason="lane_b_disabled",
        )
    return StudyInputs(
        lot_choice=choice,
        site=site,
        site_facts=site_facts,
        address=address,
    )


def pluto_study_inputs_provider(
    fetcher: PlutoFetcher,
    *,
    clock: Callable[[], datetime] | None = None,
    env: Mapping[str, str] | None = None,
) -> StudyInputsProvider:
    """A :data:`StudyInputsProvider` over a PLUTO ``fetcher``.

    Fetches the PLUTO record, then assembles the study inputs. A typed PLUTO
    connector failure or a no-record result becomes
    :class:`StudyInputsUnavailableError` (the route's bounded 503), never a
    partial or fabricated study.
    """

    def provider(
        canonical_bbl: str,
        correlation_id: str,
        *,
        selected: Sequence[str] | None = None,
    ) -> StudyInputs:
        try:
            result = fetcher(canonical_bbl, correlation_id)
        except PlutoConnectorError as exc:
            raise StudyInputsUnavailableError(
                "the official PLUTO source could not be reached; the study setup is "
                "withheld and is safe to retry.",
                reason=exc.error_type,
            ) from exc
        return assemble_study_inputs(result, selected=selected, clock=clock, env=env)

    return provider


@lru_cache(maxsize=1)
def _live_study_inputs_provider() -> StudyInputsProvider:
    """The live study-inputs provider, bound to the SAME resilient PLUTO fetcher
    the properties route uses (:func:`app.api.v1.properties.get_pluto_fetcher` ->
    :func:`app.resilience.fetcher.build_default_resilient_fetcher`): a TTL cache,
    bounded retries with jittered backoff, a per-source circuit breaker and
    last-known-good serving wrap the accepted connector (NB1). Built once,
    LAZILY, so importing this module reads no resilience env and makes no network
    call; the first live request builds the process-wide fetcher, and the whole
    process shares its cache/breaker/LKG state. The import is local to avoid any
    import-time coupling to the properties route."""
    from app.api.v1.properties import get_pluto_fetcher

    return pluto_study_inputs_provider(get_pluto_fetcher())


def default_study_inputs_provider(
    canonical_bbl: str,
    correlation_id: str,
    *,
    selected: Sequence[str] | None = None,
) -> StudyInputs:
    """Route default (slice 2, NB1): the LIVE PLUTO path through the resilient
    fetcher the properties route uses.

    Delegates to :func:`_live_study_inputs_provider`, so a real request reaches
    official PLUTO through the connector-resilience layer (timeout, bounded
    retries, circuit breaker, last-known-good). Every upstream failure still maps
    to the route's typed 503; a no-match (including a condo unit-lot) withholds
    the study rather than fabricating one. Tests override the dependency so the
    suite runs fully offline; this live default is never exercised on the
    network in tests (the live binding is proven offline by injecting a transport
    in ``tests/api/test_study_inputs_live.py``).

    The route flag is off in production regardless, and production stays blocked
    on B-001 auth plus the route-local rate limit (NB1/NB2) before any
    unauthenticated live-fetch surface is reachable.
    """
    return _live_study_inputs_provider()(canonical_bbl, correlation_id, selected=selected)
