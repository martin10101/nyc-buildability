"""Offline replay of the recorded 215-16 Northern WINDOW pack (M5-T154).

The window pack (services/api/tests/fixtures/benchmark_215_16_northern_window/) stores the three
window data responses byte-for-byte with their URLs in MANIFEST.json; the subject lot's per-BBL
geometry and each layer's service metadata are the BASE pack's already-recorded responses
(services/api/tests/fixtures/benchmark_215_16_northern/). These helpers serve those bytes to the
connectors' own fetch/parse code, so no network is touched.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from random import Random

from app.connectors import building_footprints_arcgis as bf
from app.connectors import mappluto_geometry_arcgis as mg
from app.connectors import mappluto_window_arcgis as mw
from app.connectors.dcm_street_centerline_arcgis import DcmTransport
from app.connectors.dcm_street_centerline_geometry import (
    SegmentGeometryQueryResult,
    fetch_street_segment_geometries,
)
from app.resilience.transport import TransportResponse

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
WINDOW_PACK = _FIXTURES / "benchmark_215_16_northern_window"
BASE_PACK = _FIXTURES / "benchmark_215_16_northern"
BBL = "4073340070"

# The windows the pack was recorded for (subject lot bbox at 0.01 ft, padded).
ENV_400 = (1048388.63, 215910.44, 1049311.58, 216831.1)
ENV_1000 = (1047788.63, 215310.44, 1049911.58, 217431.1)

WINDOW_LOTS_FILE = "mappluto_window_lots_4073340070_plus400ft.json"
FOOTPRINTS_FILE = "building_footprints_window_4073340070_plus400ft.json"
STREETS_FILE = "dcm_street_centerline_window_4073340070_plus1000ft.json"

_CLOCK = datetime(2026, 10, 10, 19, 5, 57, tzinfo=UTC)


def _manifest(folder: Path) -> dict:
    files = json.loads((folder / "MANIFEST.json").read_text("utf-8"))["files"]
    return {e["file"]: e for e in files}


_WINDOW_MANIFEST = _manifest(WINDOW_PACK)
_BASE_MANIFEST = _manifest(BASE_PACK)
# URL -> (folder, file); the window pack overrides the base on a collision.
_BY_URL: dict[str, tuple[Path, str]] = {}
for _folder, _mf in ((BASE_PACK, _BASE_MANIFEST), (WINDOW_PACK, _WINDOW_MANIFEST)):
    for _name, _entry in _mf.items():
        _BY_URL[_entry["url"]] = (_folder, _name)


def window_digest(name: str) -> str:
    return "sha256:" + _WINDOW_MANIFEST[name]["sha256"]


def recorded_url(name: str) -> str:
    return _WINDOW_MANIFEST[name]["url"]


def _read(url: str) -> str:
    folder, name = _BY_URL[url]
    return (folder / name).read_bytes().decode("utf-8")


def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
    return TransportResponse(200, _read(url))


def dcm_fetch(url: str, correlation_id: str) -> DcmTransport:
    folder, name = _BY_URL[url]
    entry = _manifest(folder)[name]
    return DcmTransport(url=url, status=200, body=_read(url), retrieved_at=entry["retrieved_at"])


def replay_subject_lot() -> mg.LotGeometryResult:
    return mg.fetch_lot_geometry(BBL, transport=transport, sleep=lambda _s: None,
                                 clock=lambda: _CLOCK, rng=Random(0), correlation_id="w22-replay")


def replay_window_lots(subject_bbl: str = BBL) -> mw.MapPlutoWindowResult:
    return mw.fetch_window_lots(envelope=ENV_400, subject_bbl=subject_bbl, transport=transport,
                                sleep=lambda _s: None, clock=lambda: _CLOCK, rng=Random(0),
                                correlation_id="w22-replay")


def replay_footprints() -> bf.ContextBuildingsResult:
    return bf.fetch_context_buildings(envelope=ENV_400, page_size=2000, transport=transport,
                                      sleep=lambda _s: None, clock=lambda: _CLOCK, rng=Random(0),
                                      correlation_id="w22-replay")


def replay_streets() -> SegmentGeometryQueryResult:
    return fetch_street_segment_geometries(envelope=ENV_1000, fetch=dcm_fetch,
                                           correlation_id="w22-replay")
