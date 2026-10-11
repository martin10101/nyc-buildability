"""M5-T154 S5/S8: the report's map-context provider gating and harness binding.

All offline: the live fetchers are replaced with replay-backed doubles, so no network is touched.
S5 proves the provider returns None (no call) with the live flag off, a document with it on, and
demotes ONLY a refusing layer to not_available without raising. S8 proves the recorded-pack harness
entry point returns the same document as the direct build.
"""

from __future__ import annotations

import json

import pytest

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
    # A COUNTING spy on every fetcher proves ZERO calls while the switch is off
    # (a raising double would be swallowed by _assemble and prove nothing); the
    # spies return valid replayed values, so only the call COUNT can fail.
    monkeypatch.delenv(_ENV, raising=False)
    calls = {"lot": 0, "window": 0, "footprints": 0, "streets": 0}

    def _lot(bbl, cid):
        calls["lot"] += 1
        return replay_subject_lot()

    def _window(env, subject_bbl, cid):
        calls["window"] += 1
        return replay_window_lots(subject_bbl=subject_bbl)

    def _footprints(env, cid):
        calls["footprints"] += 1
        return replay_footprints()

    def _streets(env, cid):
        calls["streets"] += 1
        return replay_streets()

    monkeypatch.setattr(rc, "_LIVE_FETCHERS", rc.ReportMapFetchers(
        fetch_lot=_lot, fetch_window=_window, fetch_footprints=_footprints, fetch_streets=_streets))
    assert rc.default_report_map_context_provider(BBL, "s5-off") is None
    assert calls == {"lot": 0, "window": 0, "footprints": 0, "streets": 0}, calls


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


# ---------------------------------------------------------------------------
# G5 A1 - the recorded-pack loader never reads outside its pack folder
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("escaping", ["../escape.json", "sub/deep.json", "/etc/passwd"])
def test_recorded_pack_loader_refuses_a_path_escaping_the_pack(tmp_path, escaping):
    pack = tmp_path / "win"
    pack.mkdir()
    base = tmp_path / "base"
    base.mkdir()
    (pack / "MANIFEST.json").write_text(
        json.dumps({"files": [{"file": escaping, "url": "https://example.invalid/q",
                               "retrieved_at": "2026-10-10T19:05:57Z"}]}),
        encoding="utf-8")
    with pytest.raises(ValueError):
        rc.recorded_pack_provider(pack, base_pack_dir=base)
