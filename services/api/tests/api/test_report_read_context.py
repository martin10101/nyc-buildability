"""POST /api/v1/properties/{bbl}/report with the map-context provider (M5-T156, S7).

The report route asks the injected map-context provider for the SAME lot as the
results body and embeds the surroundings. The recorded 215-16 Northern window pack
(M5-T154) is served through the real connectors, so no response byte is
hand-written. Flags off behave exactly as wave 21 (the default provider is gated
off and returns None); a provider error never fails the report.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import results_read as rmod
from app.api.v1.report_context import get_report_map_context_provider, recorded_pack_provider
from app.api.v1.results_read import get_results_study_inputs_provider
from app.config import INTERNAL_RESULTS_ENABLED_ENV_VAR
from app.main import create_app
from tests.api.test_results_read_api import LANE_A_ON, NORTHERN_BBL, benchmark_provider

_WINDOW_PACK = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern_window"


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    rmod.get_rate_limiter().reset()
    yield
    rmod.get_rate_limiter().reset()


@pytest.fixture
def enabled(monkeypatch):
    monkeypatch.setenv(INTERNAL_RESULTS_ENABLED_ENV_VAR, "1")
    monkeypatch.setenv(LANE_A_ON, "1")
    monkeypatch.setenv("LANE_E_ENABLED", "1")
    return monkeypatch


def _app(map_provider=None):
    app = create_app()
    app.dependency_overrides[get_results_study_inputs_provider] = benchmark_provider
    if map_provider is not None:
        app.dependency_overrides[get_report_map_context_provider] = lambda: map_provider
    rmod.get_rate_limiter().reset()
    return app


def _post(app, bbl=NORTHERN_BBL):
    return TestClient(app).post(
        f"/api/v1/properties/{bbl}/report", json={"housing_program": "standard_residence"}
    )


def test_s7_report_shows_surroundings_with_the_recorded_pack(enabled) -> None:
    response = _post(_app(recorded_pack_provider(_WINDOW_PACK)))
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    body = response.text
    assert "Where is the lot?" in body
    # the location sheet and the site plan among the surroundings carry drawings.
    site = body[body.index('id="site-and-context"'):body.index('id="option-comparison"')]
    assert site.count("<svg") >= 3
    assert "last edited" in body  # captions name their sources' dates
    assert "No building is placed on this plan yet:" in body


def test_s7_provider_is_asked_for_the_same_lot_as_the_body(enabled) -> None:
    seen: list[str] = []

    def recording_provider(bbl: str, correlation_id: str):
        seen.append(bbl)
        return recorded_pack_provider(_WINDOW_PACK)(bbl, correlation_id)

    response = _post(_app(recording_provider))
    assert response.status_code == 200
    assert seen == [NORTHERN_BBL]


def test_s7_provider_error_never_fails_the_report(enabled) -> None:
    def boom(_bbl: str, _correlation_id: str):
        raise RuntimeError("provider exploded")

    response = _post(_app(boom))
    assert response.status_code == 200
    body = response.text
    # the report is produced without surroundings (today's lot-only plan), never an
    # error page; the location sheet prints one short line.
    assert "Where is the lot?" in body
    assert "The surroundings are not shown for this property" in body


def test_s7_default_provider_is_mapless_like_wave_21(enabled) -> None:
    # No override: the default live provider is gated off (no LIVE_SPATIAL flag), so
    # it returns None and the report is mapless - exactly as wave 21.
    response = _post(_app())
    assert response.status_code == 200
    body = response.text
    assert "The surroundings are not shown for this property" in body
    site = body[body.index('id="site-and-context"'):body.index('id="option-comparison"')]
    location = site[site.index("Where is the lot?"):site.index("What constrains the design?")]
    assert "<svg" not in location


def test_s7_flag_off_is_still_404(monkeypatch) -> None:
    monkeypatch.delenv(INTERNAL_RESULTS_ENABLED_ENV_VAR, raising=False)
    response = _post(_app(recorded_pack_provider(_WINDOW_PACK)))
    assert response.status_code == 404
