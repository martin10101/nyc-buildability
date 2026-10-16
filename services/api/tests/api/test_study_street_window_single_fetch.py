"""DB-273 (M5-T203): one shared street-window fetch when the live spatial provider is on.

Offline and deterministic. With ``LIVE_SPATIAL_PROVIDER_ENABLED`` on, the live geometry provider
and the live street-data provider build the SAME street window for a lot in one request. Before this
fix each fetched it independently (twice); the shared fetch wired into
``_live_study_inputs_provider`` makes them transport it ONCE. The flag is off by default, so nothing
live changes.

Scenarios (packet M5-T203):

- S1: flag on, a counting fake street fetch -> the window is fetched once (not twice);
- S2: the merged site geometry and street data equal the two-fetch results, object for object;
- S3: a failing street fetch surfaces the SAME typed result (None) in BOTH providers, and the
  failure is not memoised (each provider still sees it);
- S4: flag off -> no shared fetch is constructed and no fetch can happen (byte-identical path);
- S5 (mutation, recorded in the producer report): removing the sharing re-doubles the fetch, so the
  S1 assertion fails.

Every fetch is driven by the recorded 215-16 Northern pack through the real B-03 connectors; no
network is touched.
"""

from __future__ import annotations

import app.api.v1.properties as properties
import app.api.v1.study_inputs as study_inputs
import app.api.v1.study_live_geometry as study_live_geometry
from app.api.v1.study_inputs import live_street_data_provider
from app.api.v1.study_live_geometry import (
    live_geometry_provider,
    shared_street_window_fetch,
)
from app.connectors.dcm_street_centerline_arcgis import DcmTransport, UpstreamError
from app.spatial.live_provider import LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR
from app.spatial.site_geometry import (
    derive_site_geometry,
    lot_outline_from_mappluto,
    street_data_for_lot,
)
from tests.spatial._northern_replay import DCM_FILE, MANIFEST, PACK, replay_lot_geometry

NORTHERN_BBL = "4073340070"
_CID = "single-fetch-test"
_META_FILE = "dcm_layer_metadata.json"
_WINDOW_FILES = (_META_FILE, DCM_FILE)


# --------------------------------------------------------------------------- offline seams


def _fake_lot(canonical_bbl: str, correlation_id: str):
    """The recorded MapPLUTO lot geometry, replayed through the real connector (its own I/O, not
    shared by DB-273); both providers derive the SAME lot and therefore the SAME street window."""
    return replay_lot_geometry()


def _pack_transport(name: str) -> DcmTransport:
    entry = MANIFEST[name]
    body = (PACK / name).read_bytes().decode("utf-8")
    return DcmTransport(
        url=entry["url"], status=200, body=body, retrieved_at=entry["retrieved_at"]
    )


def _recorded_streets(url: str, correlation_id: str) -> DcmTransport:
    """Serve the recorded DCM metadata + envelope-page bytes by URL -- the accepted paged fetch
    calls this exactly as it would ``default_fetch``, fully offline."""
    for name in _WINDOW_FILES:
        transport = _pack_transport(name)
        if url == transport.url:
            return transport
    raise AssertionError(f"the code fetched an unexpected URL: {url}")


class _CountingFetch:
    """A street-fetch double that records every ``(url, correlation_id)`` asked for and delegates to
    the recorded pack, so a test can count how many times the window is actually transported."""

    def __init__(self, delegate=_recorded_streets) -> None:
        self._delegate = delegate
        self.calls: list[tuple[str, str]] = []

    def __call__(self, url: str, correlation_id: str) -> DcmTransport:
        self.calls.append((url, correlation_id))
        return self._delegate(url, correlation_id)


def _reference_street_data():
    """The StreetData the recorded pack yields through the accepted composition (the two-fetch
    reference each provider builds on its own)."""
    lot, refusal = lot_outline_from_mappluto(replay_lot_geometry())
    assert lot is not None, refusal
    return street_data_for_lot(lot, correlation_id=_CID, fetch=_recorded_streets)


def _reference_geometry():
    """The B-03 SiteGeometry the recorded pack yields with ``city_records=None`` (the same object
    the live geometry provider builds)."""
    lot, refusal = lot_outline_from_mappluto(replay_lot_geometry())
    assert lot is not None, refusal
    streets = street_data_for_lot(lot, correlation_id=_CID, fetch=_recorded_streets)
    return derive_site_geometry(lot, streets, None)


def _run_both_providers(fetch_streets, *, cid: str = _CID):
    """Run the geometry provider then the street-data provider for one lot/request -- the order
    ``pluto_study_inputs_provider`` calls them -- sharing one ``fetch_streets`` between them."""
    geometry = live_geometry_provider(fetch_lot=_fake_lot, fetch_streets=fetch_streets)(
        NORTHERN_BBL, cid
    )
    streets = live_street_data_provider(fetch_lot=_fake_lot, fetch_streets=fetch_streets)(
        NORTHERN_BBL, cid
    )
    return geometry, streets


# --------------------------------------------------------------------------- S1


def test_window_is_fetched_once_when_both_providers_share_the_fetch() -> None:
    # Baseline: ONE provider transports the whole window (metadata + envelope page) once each.
    baseline = _CountingFetch()
    live_street_data_provider(fetch_lot=_fake_lot, fetch_streets=baseline)(NORTHERN_BBL, _CID)
    per_window = len(baseline.calls)
    assert per_window >= 2  # at least the metadata URL and one envelope page
    assert len(set(baseline.calls)) == per_window  # each URL fetched once in a single window

    # Shared fetch: both providers run in one request, but the window is transported ONCE.
    counting = _CountingFetch()
    shared = shared_street_window_fetch(counting)
    _run_both_providers(shared)
    assert len(counting.calls) == per_window  # one window fetch, not two
    assert sorted(counting.calls) == sorted(baseline.calls)  # the same URLs, each once
    assert len(set(counting.calls)) == len(counting.calls)  # no URL transported twice

    # Contrast: WITHOUT sharing (each provider its own fetch), the window is transported twice.
    unshared = _CountingFetch()
    _run_both_providers(unshared)
    assert len(unshared.calls) == 2 * per_window


# --------------------------------------------------------------------------- S2


def test_shared_fetch_results_equal_the_two_fetch_results() -> None:
    shared = shared_street_window_fetch(_CountingFetch())
    geometry, streets = _run_both_providers(shared)
    # Equal to the accepted composition reference (lot type, frontages, depth, provenance; window).
    assert geometry == _reference_geometry()
    assert streets == _reference_street_data()
    # And equal, object for object, to the un-shared (two-fetch) results: sharing only removes the
    # duplicate transport, it never changes a derived value.
    unshared_geometry, unshared_streets = _run_both_providers(_recorded_streets)
    assert geometry == unshared_geometry
    assert streets == unshared_streets


# --------------------------------------------------------------------------- S3


def test_a_failing_shared_fetch_surfaces_the_same_result_in_both_providers() -> None:
    def _raising_streets(url: str, correlation_id: str) -> DcmTransport:
        raise UpstreamError(
            "official DCM ArcGIS service was unreachable (test)", correlation_id=correlation_id
        )

    counting = _CountingFetch(delegate=_raising_streets)
    shared = shared_street_window_fetch(counting)
    geometry = live_geometry_provider(fetch_lot=_fake_lot, fetch_streets=shared)(
        NORTHERN_BBL, _CID
    )
    streets = live_street_data_provider(fetch_lot=_fake_lot, fetch_streets=shared)(
        NORTHERN_BBL, _CID
    )
    # Both providers fail closed to None (no usable window), exactly as the two-fetch behaviour.
    assert geometry is None
    assert streets is None
    # A raised failure is NOT memoised: BOTH providers reached the failing fetch independently.
    assert len(counting.calls) == 2


# --------------------------------------------------------------------------- S4


def test_flag_off_builds_no_shared_window_fetch(monkeypatch) -> None:
    # Only BUILD the live provider (no invocation, so no network): a lightweight PLUTO fetcher and
    # version probe stand in, since neither is called when the provider is merely constructed.
    monkeypatch.setattr(properties, "get_pluto_fetcher", lambda: (lambda bbl, cid: None))
    monkeypatch.setattr(study_inputs, "cached_default_version_probe", lambda: None)

    built: list[tuple] = []
    real = study_live_geometry.shared_street_window_fetch

    def spy(*args, **kwargs):
        built.append((args, kwargs))
        return real(*args, **kwargs)

    monkeypatch.setattr(study_live_geometry, "shared_street_window_fetch", spy)

    # Flag OFF (production default): the live spatial providers are not bound, so no shared
    # street-window fetch is constructed and no fetch can happen.
    monkeypatch.delenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, raising=False)
    study_inputs._live_study_inputs_provider.cache_clear()
    try:
        study_inputs._live_study_inputs_provider()
    finally:
        study_inputs._live_study_inputs_provider.cache_clear()
    assert built == []

    # Flag ON: exactly ONE shared fetch is constructed (handed to BOTH providers).
    monkeypatch.setenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, "1")
    study_inputs._live_study_inputs_provider.cache_clear()
    try:
        study_inputs._live_study_inputs_provider()
    finally:
        study_inputs._live_study_inputs_provider.cache_clear()
    assert len(built) == 1
