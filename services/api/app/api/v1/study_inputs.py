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

Layering (slice 1):

- :func:`assemble_study_inputs` is the PURE assembly: a ``PlutoFetchResult`` ->
  profile -> B-02 site facts, and -> a single B-07 :class:`SiteLot` -> lot choice
  -> multi-lot site (through the LANE_B-gated entry). It performs no I/O, so the
  route's tests exercise the real B-02/B-07 pipeline on a recorded PLUTO body.
- :func:`pluto_study_inputs_provider` turns a PLUTO fetcher (the same
  ``(canonical_bbl, correlation_id) -> PlutoFetchResult`` seam the properties
  route injects) into a :data:`StudyInputsProvider`. Tests inject a fixture
  fetcher; the live resilient fetcher is wired in a LATER slice.
- :func:`default_study_inputs_provider` is the route's default dependency. It
  raises :class:`StudyInputsUnavailableError` because the live fetch shell is
  deferred to a later slice (slice 2, alongside the e2e harness); production
  keeps the route flag off regardless. Tests override the dependency.

Lot choice and multi-lot site are Lane B behaviour, so they are produced only
through ``derive_multi_lot_site_if_enabled`` (the LANE_B_ENABLED gate). When that
gate is off the inputs are unavailable (fail safe), never fabricated.

Slice-1 bounds (documented, not hidden): one tax lot per call (no MapPLUTO
outline fetch and no condo base-lot resolution yet, so a multi-lot or condo input
resolves to the single entered lot); no street data, so frontage/street-width
facts are not added here; ``address`` is null (BBL-only) until the address-confirm
step supplies the confirmed address. These are later slices.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from app.connectors.pluto_soda import PlutoConnectorError, PlutoFetchResult
from app.profile.builder import build_property_profile
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
    ``site_facts`` are B-02 ``site_fact`` v1 documents, carried verbatim.
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


# (canonical_bbl, correlation_id) -> StudyInputs. Injected through FastAPI
# dependency_overrides so the route's tests run offline on recorded fixtures.
StudyInputsProvider = Callable[[str, str], StudyInputs]

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
        raise StudyInputsUnavailableError(
            f"PLUTO returned {pluto_result.status!r} for {pluto_result.bbl}; no study "
            "setup is produced (a record is required).",
            reason="no_record",
        )
    builder_kwargs = {} if clock is None else {"clock": clock}
    profile = build_property_profile(pluto_result, **builder_kwargs)
    site_fact_set = build_site_facts(profile)
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
        site_facts=tuple(site_fact_set.facts),
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

    def provider(canonical_bbl: str, correlation_id: str) -> StudyInputs:
        try:
            result = fetcher(canonical_bbl, correlation_id)
        except PlutoConnectorError as exc:
            raise StudyInputsUnavailableError(
                "the official PLUTO source could not be reached; the study setup is "
                "withheld and is safe to retry.",
                reason=exc.error_type,
            ) from exc
        return assemble_study_inputs(result, clock=clock, env=env)

    return provider


def default_study_inputs_provider(canonical_bbl: str, correlation_id: str) -> StudyInputs:
    """Route default: the live PLUTO-fetch shell is wired in a later slice.

    Slice 1 ships the route, the injected seam, and the offline-tested pure
    assembly; binding :func:`pluto_study_inputs_provider` to the live resilient
    fetcher is the next slice (with the e2e harness). Until then the default
    fails safe, so no study is ever fabricated. The route flag is off in
    production regardless.
    """
    del canonical_bbl, correlation_id
    raise StudyInputsUnavailableError(
        "the live study-inputs pipeline is not wired in this slice; inputs are served "
        "through the injected provider (request D-1 slice 2). Slice 2 binds "
        "pluto_study_inputs_provider to the resilient PLUTO fetcher the properties route "
        "uses (app.resilience.fetcher.build_default_resilient_fetcher).",
        reason="live_fetch_not_configured",
    )
