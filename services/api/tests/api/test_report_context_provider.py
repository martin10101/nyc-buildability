"""M5-T154 S5/S8: the report's map-context provider gating and harness binding.

All offline: the live fetchers are replaced with replay-backed doubles, so no network is touched.
S5 proves the provider returns None (no call) with the live flag off, a document with it on, and
demotes ONLY a refusing layer to not_available without raising. S8 proves the recorded-pack harness
entry point returns the same document as the direct build.
"""

from __future__ import annotations

from app.api.v1 import report_context as rc
from app.connectors import mappluto_window_arcgis as mw
from app.contracts.map_context import build_report_map_context
from app.contracts.study_contracts import validate_map_context_document
from tests.spatial._northern_window_replay import (
    BBL,
    ENV_400,
    ENV_1000,
    WINDOW_PACK,
    replay_footprints,
    replay_streets,
    replay_subject_lot,
    replay_window_lots,
)

_ENV = "LIVE_SPATIAL_PROVIDER_ENABLED"


def _replay_fetchers(**overrides) -> rc.ReportMapFetchers:
    base = {
        "fetch_lot": lambda bbl, cid: replay_subject_lot(),
        "fetch_window": lambda env, subject_bbl, cid: replay_window_lots(subject_bbl=subject_bbl),
        "fetch_footprints": lambda env, cid: replay_footprints(),
        "fetch_streets": lambda env, cid: replay_streets(),
    }
    base.update(overrides)
    return rc.ReportMapFetchers(**base)


def _direct_document() -> dict:
    return build_report_map_context(
        replay_subject_lot(),
        context_window=ENV_400,
        tax_lots=replay_window_lots(),
        footprints=replay_footprints(),
        streets=replay_streets(),
        streets_window=ENV_1000,
        notes=rc.DEFAULT_REPORT_MAP_NOTES,
    )


# ---------------------------------------------------------------------------
# S5 - provider gating
# ---------------------------------------------------------------------------


def test_flag_off_returns_none_and_makes_no_connector_call(monkeypatch):
    monkeypatch.delenv(_ENV, raising=False)

    def _boom(*_args, **_kwargs):
        raise AssertionError("no connector call may happen while the flag is off")

    monkeypatch.setattr(rc, "_LIVE_FETCHERS", _replay_fetchers(
        fetch_lot=_boom, fetch_window=_boom, fetch_footprints=_boom, fetch_streets=_boom))
    assert rc.default_report_map_context_provider(BBL, "s5-off") is None


def test_flag_on_with_replayed_fetchers_returns_the_document(monkeypatch):
    monkeypatch.setenv(_ENV, "1")
    monkeypatch.setattr(rc, "_LIVE_FETCHERS", _replay_fetchers())
    doc = rc.default_report_map_context_provider(BBL, "s5-on")
    assert doc is not None and doc["contract_version"] == "1.1.0"
    validate_map_context_document(doc)


def test_a_refusing_fetcher_makes_only_that_layer_unavailable():
    def _streets_refuse(_env, _cid):
        raise RuntimeError("upstream down")

    doc = rc._assemble(BBL, "s5-streets", _replay_fetchers(fetch_streets=_streets_refuse),
                       rc.DEFAULT_REPORT_MAP_NOTES)
    assert doc is not None
    validate_map_context_document(doc)
    mc = doc["map_context"]
    assert mc["streets"]["status"] == "not_available"
    assert mc["streets"]["reason"] == rc._STREETS_REFUSED
    assert mc["tax_lots"]["status"] == "available"
    assert mc["building_footprints"]["status"] == "available"


def test_a_refusing_window_fetcher_makes_only_tax_lots_unavailable():
    def _window_refuse(_env, _subject_bbl, _cid):
        raise mw.UpstreamError("arcgis error object", correlation_id="x")

    doc = rc._assemble(BBL, "s5-lots", _replay_fetchers(fetch_window=_window_refuse),
                       rc.DEFAULT_REPORT_MAP_NOTES)
    assert doc is not None
    validate_map_context_document(doc)
    mc = doc["map_context"]
    assert mc["tax_lots"]["status"] == "not_available"
    assert mc["tax_lots"]["reason"] == rc._TAX_LOTS_REFUSED
    assert mc["streets"]["status"] == "available"


def test_no_subject_outline_gives_none():
    def _subject_refuse(_bbl, _cid):
        raise mw.UpstreamError("mappluto down", correlation_id="x")

    doc = rc._assemble(BBL, "s5-nosubject", _replay_fetchers(fetch_lot=_subject_refuse),
                       rc.DEFAULT_REPORT_MAP_NOTES)
    assert doc is None


# ---------------------------------------------------------------------------
# S8 - harness binding
# ---------------------------------------------------------------------------


def test_recorded_pack_provider_returns_the_same_document():
    provider = rc.recorded_pack_provider(WINDOW_PACK)
    harness_doc = provider(BBL, "s8")
    assert harness_doc is not None
    validate_map_context_document(harness_doc)
    assert harness_doc == _direct_document()
