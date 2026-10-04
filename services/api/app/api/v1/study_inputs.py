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

- :func:`assemble_study_inputs` is the assembly: a ``PlutoFetchResult`` ->
  profile -> B-02 site facts (each carrying B-06's ``source.version_check`` status,
  requests B-3/B-4), and -> a single B-07 :class:`SiteLot` -> lot choice ->
  multi-lot site (through the LANE_B-gated entry). Published-on-record = the
  retrievals themselves PLUS, for PLUTO, the city's currently published release
  from Lane B's version probe (``published_versions_for_study``, request B-4) when
  a probe is injected; on any probe failure the PLUTO pins FAIL CLOSED to
  ``version_unknown``. It performs no I/O itself (the only I/O is the injected
  ``version_probe``, which route tests and the e2e harness drive from recorded
  fixtures), so the route's tests exercise the real B-02/B-07 pipeline offline on a
  recorded PLUTO body. An optional ``selected`` (a sequence of canonical BBLs) is
  passed VERBATIM to B-07's ``derive_multi_lot_site`` for a re-pick; None is the
  default "use all".
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

B-03 geometry (journey wave 1 item 1) and B-05 existing-floor-area evidence (journey
wave 1 item 3) reach assembly through INJECTED providers, as pure data, so assembly
stays I/O-free. Both LIVE defaults bind NOTHING: there is no live envelope-DCM geometry
binding, and there is NO DOB connector under ``app/connectors`` for the existing-floor-
area evidence (a Lane B deliverable). So in production both stay None and the study read
is byte-identical to the pre-wiring slice; tests and the e2e harness inject fixture-
backed providers built from the recorded 215-16 Northern pack through the real B-03/B-05
readers to exercise the seams offline.

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

from app.api.v1.pluto_version_cache import (
    VersionProbe,
    cached_default_version_probe,
    published_versions_for_study,
)
from app.api.v1.study_geometry import thread_site_geometry
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
)
from app.profile.existing_floor_area import ExistingFloorAreaEvidence
from app.profile.fact_version_check import attach_version_check
from app.profile.site_facts import build_site_facts
from app.spatial.multi_lot_site import (
    LotChoice,
    MultiLotSite,
    build_lot_choice,
    derive_multi_lot_site_if_enabled,
    site_lot_from_sources,
)
from app.spatial.site_geometry import SiteGeometry

__all__ = [
    "ExistingFloorAreaProvider",
    "GeometryProvider",
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

# (canonical_bbl, correlation_id) -> B-03 SiteGeometry, or None when no usable
# geometry is available for this lot (the facts then stay unknown, exactly as
# before). The INJECTED geometry seam (journey wave 1 item 1): tests and the e2e
# harness bind a fixture-backed provider; the LIVE default binds NOTHING here
# (see _live_study_inputs_provider for why), so geometry stays None in production
# and the study read is byte-identical to the pre-geometry slice.
GeometryProvider = Callable[[str, str], "SiteGeometry | None"]

# (canonical_bbl, correlation_id) -> B-05 ExistingFloorAreaEvidence, or None when no
# DOB-filing / certificate / stated-assumption evidence is available for this lot (the
# existing_zoning_floor_area fact then stays unknown, exactly as before). The INJECTED
# existing-floor-area seam (journey wave 1 item 3): tests and the e2e harness bind a
# fixture-backed provider built from the benchmark pack's recorded DOB responses through
# B-05's own readers; the LIVE default binds NOTHING here, because there is NO DOB
# connector under app/connectors (see _live_study_inputs_provider), so the evidence
# stays None in production and the study read's existing_zoning_floor_area fact is
# byte-identical to the pre-wiring slice. The evidence is pure DATA (an
# ExistingFloorAreaEvidence); the fetch that builds it is the provider's I/O, never the
# route's or assembly's.
ExistingFloorAreaProvider = Callable[[str, str], "ExistingFloorAreaEvidence | None"]


def _existing_evidence(
    provider: ExistingFloorAreaProvider | None,
    canonical_bbl: str,
    correlation_id: str,
) -> ExistingFloorAreaEvidence | None:
    """Call the injected existing-floor-area provider (journey wave 1 item 3) and
    return its B-05 evidence, or None when no provider is bound (the live default).

    A provider that cannot produce VALID evidence -- a B-05 validation error while
    building the evidence (``ValueError``/``TypeError``, e.g. a recorded row refused by
    B-05's readers), or a returned value that is not an
    :class:`~app.profile.existing_floor_area.ExistingFloorAreaEvidence` -- is the route's
    fail-safe unavailability: it raises :class:`StudyInputsUnavailableError`, which the
    route maps to a bounded ``503``. Nothing is ever fabricated, and a malformed-evidence
    fetch is never a generic ``500``. Mirrors the PLUTO-connector failure mapping."""
    if provider is None:
        return None
    try:
        evidence = provider(canonical_bbl, correlation_id)
    except (ValueError, TypeError) as exc:
        raise StudyInputsUnavailableError(
            "the existing floor-area evidence could not be produced for this lot; the "
            "study setup is withheld rather than fabricated and is safe to retry.",
            reason="existing_floor_area_unavailable",
        ) from exc
    if evidence is not None and not isinstance(evidence, ExistingFloorAreaEvidence):
        raise StudyInputsUnavailableError(
            "the existing floor-area evidence provider returned a malformed value; the "
            "study setup is withheld rather than fabricated and is safe to retry.",
            reason="existing_floor_area_malformed",
        )
    return evidence


def assemble_study_inputs(
    pluto_result: PlutoFetchResult,
    *,
    selected: Sequence[str] | None = None,
    clock: Callable[[], datetime] | None = None,
    env: Mapping[str, str] | None = None,
    address: str | None = None,
    version_probe: VersionProbe | None = None,
    correlation_id: str | None = None,
    site_geometry: SiteGeometry | None = None,
    existing_floor_area: ExistingFloorAreaEvidence | None = None,
) -> StudyInputs:
    """Build :class:`StudyInputs` from a successful PLUTO fetch result.

    ``selected`` is the lot selection; None is the default "use all". ``env``
    supplies the LANE_B_ENABLED gate (defaults to the process environment).
    ``version_probe`` is the injectable PLUTO published-version probe (request
    B-4): when present and Lane B is on, the city's currently published release is
    consulted so a lot pinned to an older release reads ``out_of_date``, and any
    probe failure fails CLOSED to ``version_unknown`` for the PLUTO pins. When None
    (no probe by design) the published-on-record set is retrieval-only, as before.
    The only I/O this function performs is that injected probe; ``correlation_id``
    ties the probe's provenance and logs to the request.

    ``site_geometry`` is an already-derived B-03 :class:`SiteGeometry` for this lot
    (journey wave 1 item 1), passed in as pure DATA so this function stays I/O-free
    -- the fetch that produces it happens in the provider, never here. When given,
    :func:`app.api.v1.study_geometry.thread_site_geometry` threads it onto the site
    facts AFTER the B-06 version-check bridge: the ``lot_type`` fact carries B-03's
    geometric type, per-street ``lot_frontage`` facts are added, and ``lot_depth``
    is replaced only when B-03 gives a single depth. When None (the default, and
    the live default) the facts are byte-identical to the pre-geometry slice.

    ``existing_floor_area`` is the B-05
    :class:`~app.profile.existing_floor_area.ExistingFloorAreaEvidence` for this lot
    (journey wave 1 item 3), passed in as pure DATA (so this function stays I/O-free)
    straight into :func:`app.profile.site_facts.build_site_facts`. B-05 resolves it to
    the ``existing_zoning_floor_area`` fact -- a sourced value when a completed DOB
    filing / certificate / stated assumption gives one, or an honest unknown with the
    considered figures and its reason attached when it does not (the recorded 215-16
    Northern lot is unknown: the DOB figure may cover the whole zoning lot). No figure
    is ever invented, and city building area (PLUTO/DOF) is never used for it. When None
    (the default, and the live default) the ``existing_zoning_floor_area`` fact is the
    unknown fact B-05 emits for no evidence -- byte-identical to the pre-wiring slice.

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
    site_fact_set = build_site_facts(profile, existing_floor_area=existing_floor_area)
    # One tax lot from the PLUTO row (no MapPLUTO outline yet - slice 1). B-07's
    # adapter records the absence of an outline; the lot size is the city-recorded
    # area, or unknown (never 0). Lot choice and multi-lot site are Lane B
    # behaviour, so derive FIRST: when the LANE_B gate is off the study is withheld
    # (fail safe) BEFORE any version probe is attempted - the probe (a network call)
    # runs only when Lane B is enabled (request B-4).
    site_lot = site_lot_from_sources(pluto_result.bbl, None, pluto_result)
    choice = build_lot_choice([pluto_result.bbl], {pluto_result.bbl: site_lot})
    site = derive_multi_lot_site_if_enabled(choice, selected, env=env)
    if site is None:
        raise StudyInputsUnavailableError(
            "the multi-lot site gate (LANE_B_ENABLED) is off, so the lot choice is not "
            "produced; the study setup is withheld rather than fabricated.",
            reason="lane_b_disabled",
        )
    # Attach each source's version status (B-06's "Out of date" rule) to the facts it
    # covers, so the status travels with the fact to Lane D/E and export_record.sources
    # (requests B-3/B-4). Published-on-record = the retrievals themselves PLUS, for the
    # PLUTO dataset, the city's currently published release from Lane B's version probe
    # (published_versions_for_study). Retrieval-only can only ever read "current"
    # (nothing newer than the pin is on record); the probe grows the published set so a
    # lot pinned to an older PLUTO release reads "out of date". On ANY typed probe
    # failure the study fails CLOSED: the PLUTO pins read "version unknown", never a
    # probe-masked "current" (request B-4). The bridge is pure: a fact whose source has
    # no dataset version stays 1.0.0 with no version_check; references carry none.
    pins = pins_from_site_facts(site_fact_set.facts)
    published = published_versions_for_study(
        pins, version_probe=version_probe, correlation_id=correlation_id or ""
    )
    report = assess_data_versions(pins, published)
    site_facts = attach_version_check(site_fact_set.facts, report)
    # Thread B-03 geometry (journey wave 1 item 1) AFTER the version-check bridge:
    # the PLUTO facts keep their version_check; the added/replaced tax-map facts
    # carry none (they are not a versioned city dataset here). None -> unchanged.
    if site_geometry is not None:
        site_facts = thread_site_geometry(site_facts, site_geometry)
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
    version_probe: VersionProbe | None = None,
    geometry_provider: GeometryProvider | None = None,
    existing_floor_area_provider: ExistingFloorAreaProvider | None = None,
) -> StudyInputsProvider:
    """A :data:`StudyInputsProvider` over a PLUTO ``fetcher``.

    Fetches the PLUTO record, then assembles the study inputs. A typed PLUTO
    connector failure or a no-record result becomes
    :class:`StudyInputsUnavailableError` (the route's bounded 503), never a
    partial or fabricated study. ``version_probe`` is threaded to
    :func:`assemble_study_inputs` (request B-4): the live provider binds the
    cached live probe; tests and the e2e harness inject a probe over a routed
    fixture transport so nothing touches the network.

    ``geometry_provider`` is the INJECTED B-03 geometry seam (journey wave 1 item
    1): when given, it is called ``(canonical_bbl, correlation_id) -> SiteGeometry
    | None`` and its result is passed to :func:`assemble_study_inputs` as pure data
    (so assembly stays I/O-free). None (the default, and the live default) means no
    geometry is threaded and the facts are byte-identical to the pre-geometry
    slice. A geometry fetch is the provider's I/O, never the route's or assembly's.

    ``existing_floor_area_provider`` is the INJECTED B-05 existing-floor-area seam
    (journey wave 1 item 3): when given, it is called ``(canonical_bbl,
    correlation_id) -> ExistingFloorAreaEvidence | None`` and its result is passed to
    :func:`assemble_study_inputs` as pure data. A provider that cannot produce valid
    evidence maps to :class:`StudyInputsUnavailableError` (the route's bounded 503, fail
    safe) via :func:`_existing_evidence`, never a fabricated figure or a generic 500.
    None (the default, and the live default) means no evidence is threaded and the
    ``existing_zoning_floor_area`` fact is byte-identical to the pre-wiring slice. The
    evidence fetch is the provider's I/O, never the route's or assembly's.
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
        site_geometry = (
            geometry_provider(canonical_bbl, correlation_id)
            if geometry_provider is not None
            else None
        )
        existing_floor_area = _existing_evidence(
            existing_floor_area_provider, canonical_bbl, correlation_id
        )
        return assemble_study_inputs(
            result,
            selected=selected,
            clock=clock,
            env=env,
            version_probe=version_probe,
            correlation_id=correlation_id,
            site_geometry=site_geometry,
            existing_floor_area=existing_floor_area,
        )

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
    import-time coupling to the properties route.

    It also binds the process-wide cached PLUTO version probe
    (``cached_default_version_probe``, request B-4): built once here (this provider
    is ``lru_cache``-d), so a burst of studies shares one freshness observation and
    the city API is not hit once per study. No probe call happens here - the cache
    is cold until the first study assembles.

    It binds NO live geometry provider (journey wave 1 item 1). The B-03 engine
    needs BOTH a live lot outline AND the City Map street center lines queried for
    the lot's ENVELOPE. A live MapPLUTO lot-outline fetch exists
    (``app.connectors.mappluto_geometry_arcgis.fetch_lot_geometry``), but there is
    NO existing live binding that produces the envelope-intersects DCM geometry
    PAGES ``app.spatial.site_geometry.street_data_from_pages`` requires: the
    accepted geometry fetch (``dcm_street_centerline_geometry.
    fetch_street_segment_geometries``) supports only borough / street_name /
    object_id predicates, and a non-envelope page fails that adapter's coverage
    check closed (the lot type then reads unknown). Rather than invent a connector,
    this default binds nothing live, so geometry stays None and the live study read
    is byte-identical to the pre-geometry slice. Tests and the e2e harness inject a
    fixture-backed geometry provider to exercise the seam offline.

    It binds NO live existing-floor-area provider either (journey wave 1 item 3). There
    is NO DOB connector under ``app/connectors``: the only DOB datasets with a zoning
    floor-area column (DOB BIS job filings ``ic3t-wcy2`` and the certificate datasets
    ``pkdm-hqz6`` / ``bs8b-p36w``) have no connector / source_registry record / fixtures
    / contract tests yet -- that connector is a Lane B deliverable. Rather than invent
    one, this default binds nothing live, so the existing-floor-area evidence stays None
    and the live study read's ``existing_zoning_floor_area`` fact is byte-identical to
    the pre-wiring slice (the unknown fact B-05 emits for no evidence). Tests and the
    e2e harness inject a fixture-backed evidence provider built from the recorded
    benchmark pack (through B-05's own readers) to exercise the seam offline."""
    from app.api.v1.properties import get_pluto_fetcher

    return pluto_study_inputs_provider(
        get_pluto_fetcher(), version_probe=cached_default_version_probe()
    )


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
