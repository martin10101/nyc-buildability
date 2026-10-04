"""Offline replay of the recorded 215-16 Northern Blvd pack through the real connectors.

The pack (services/api/tests/fixtures/benchmark_215_16_northern/, queue item B-01) stores
each official response byte-for-byte with its URL in MANIFEST.json. These helpers serve
those bytes to the connectors' own fetch/parse code, so no network is touched.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from random import Random

from app.connectors import mappluto_geometry_arcgis, pluto_soda
from app.connectors.dcm_street_centerline_arcgis import DcmTransport
from app.connectors.dcm_street_centerline_geometry import (
    SegmentGeometryPage,
    parse_segment_geometry_page,
)
from app.resilience.transport import TransportResponse

PACK = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern"
MANIFEST = {entry["file"]: entry
            for entry in json.loads((PACK / "MANIFEST.json").read_text("utf-8"))["files"]}
BBL = "4073340070"
DCM_FILE = "dcm_street_centerline_lot_envelope_4073340070.json"
# MapPLUTO lot bounds (0.01 ft) padded by 150 ft: the recorded DCM query envelope
# (tests/connectors/test_benchmark_215_16_northern_fixtures.py DCM_ENVELOPE).
DCM_ENVELOPE = (1048638.63, 216160.44, 1049061.58, 216581.1)
_CLOCK = datetime(2026, 9, 30, 6, 20, tzinfo=UTC)
_BY_URL = {entry["url"]: name for name, entry in MANIFEST.items()}


def manifest_digest(name: str) -> str:
    return "sha256:" + MANIFEST[name]["sha256"]


def _transport(url: str, headers: dict, timeout: float) -> TransportResponse:
    return TransportResponse(200, (PACK / _BY_URL[url]).read_bytes().decode("utf-8"))


def replay_lot_geometry() -> mappluto_geometry_arcgis.LotGeometryResult:
    return mappluto_geometry_arcgis.fetch_lot_geometry(
        BBL, transport=_transport, sleep=lambda _s: None, clock=lambda: _CLOCK,
        rng=Random(0), correlation_id="b03-benchmark")


def replay_pluto() -> pluto_soda.PlutoFetchResult:
    return pluto_soda.fetch_by_bbl(
        BBL, transport=_transport, sleep=lambda _s: None, clock=lambda: _CLOCK,
        correlation_id="b03-benchmark", observation_event_id="b03-benchmark")


def replay_dcm_page() -> SegmentGeometryPage:
    entry = MANIFEST[DCM_FILE]
    body = (PACK / DCM_FILE).read_bytes().decode("utf-8")
    transport = DcmTransport(url=entry["url"], status=200, body=body,
                             retrieved_at=entry["retrieved_at"])
    return parse_segment_geometry_page(transport, correlation_id="b03-benchmark")


def recorded_dcm_envelope_page() -> tuple[str, str, str]:
    """The recorded DCM envelope-page as ``(url, body_text, retrieved_at)`` -- the raw bytes a
    live-streets composition test serves back through the accepted fetch seam, so the URL the
    code builds can be checked against the recorded one."""
    entry = MANIFEST[DCM_FILE]
    return entry["url"], (PACK / DCM_FILE).read_bytes().decode("utf-8"), entry["retrieved_at"]
