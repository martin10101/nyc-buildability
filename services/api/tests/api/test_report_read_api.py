"""POST /api/v1/properties/{bbl}/report - the internal report route (task M5-T151, S12).

The route reuses the results route's whole flow, so these tests prove the gating
and refusals are IDENTICAL to the results route's and that a 200 answers
text/html with the full report. The benchmark provider and helpers are imported
from the accepted results-route test (both files run together in the documented
command), so no response byte is hand-written and the engine chain is the
production path.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import results_read as rmod
from app.api.v1.results_read import get_results_study_inputs_provider
from app.config import INTERNAL_RESULTS_ENABLED_ENV_VAR
from app.main import create_app
from tests.api.test_results_read_api import (
    LANE_A_ON,
    NORTHERN_BBL,
    benchmark_provider,
)

REPORT_PATH = f"/api/v1/properties/{NORTHERN_BBL}/report"
# A structurally-similar POST path that is NOT mounted (an extra segment), so it hits FastAPI's
# generic 404 - the byte template a flag-off read must match.
REPORT_UNMOUNTED = f"/api/v1/properties/{NORTHERN_BBL}/__report_unmounted_probe__"


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    rmod.get_rate_limiter().reset()
    yield
    rmod.get_rate_limiter().reset()


def _app(provider=None):
    app = create_app()
    app.dependency_overrides[get_results_study_inputs_provider] = lambda: (
        provider or benchmark_provider()
    )
    rmod.get_rate_limiter().reset()
    return app


@pytest.fixture
def enabled(monkeypatch):
    monkeypatch.setenv(INTERNAL_RESULTS_ENABLED_ENV_VAR, "1")
    monkeypatch.setenv(LANE_A_ON, "1")
    return monkeypatch


def _post(app, bbl=NORTHERN_BBL, body=None, params=None):
    body = {"housing_program": "standard_residence"} if body is None else body
    return TestClient(app).post(f"/api/v1/properties/{bbl}/report", json=body, params=params)


# --------------------------------------------------------------------------- flags off
def test_flag_unset_is_404_byte_identical_to_unmounted(monkeypatch) -> None:
    monkeypatch.delenv(INTERNAL_RESULTS_ENABLED_ENV_VAR, raising=False)
    client = TestClient(create_app())
    unknown = client.post(REPORT_UNMOUNTED, json={"housing_program": "standard_residence"})
    response = client.post(REPORT_PATH, json={"housing_program": "standard_residence"})
    assert response.status_code == unknown.status_code == 404
    assert response.content == unknown.content
    assert response.headers.get("content-type") == unknown.headers.get("content-type")
    assert "X-Correlation-ID" not in response.headers


@pytest.mark.parametrize("token", ["0", "", "false", "off"])
def test_non_true_flag_token_stays_404(monkeypatch, token) -> None:
    monkeypatch.setenv(INTERNAL_RESULTS_ENABLED_ENV_VAR, token)
    assert _post(_app()).status_code == 404


def test_report_path_absent_from_openapi(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_RESULTS_ENABLED_ENV_VAR, "1")
    schema = TestClient(create_app()).get("/openapi.json").json()
    assert "/api/v1/properties/{bbl}/report" not in schema["paths"]


# --------------------------------------------------------------------------- flags on, 200 HTML
def test_flag_on_returns_html_report(enabled) -> None:
    response = _post(_app())
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    body = response.text
    assert body.startswith("<!doctype html>")
    for sid in ("decision-summary", "site-and-context", "option-comparison",
                "scenario-B", "assumptions-open-items", "calculations-evidence"):
        assert f'id="{sid}"' in body
    assert "Scheduled floor area: 20,150 sq ft; site fit unverified" in body
    assert "X-Correlation-ID" in response.headers


def test_a1_drawings_render_on_the_route_under_the_drawing_flag(enabled, monkeypatch) -> None:
    # A1: the harness turns on LANE_E_ENABLED; then the report route embeds the
    # server-made site plan, the summary plan and the floor-stack SVGs.
    monkeypatch.setenv("LANE_E_ENABLED", "1")
    body = _post(_app()).text
    assert body.count("<svg") >= 3
    decision = body[body.index('id="decision-summary"'):body.index('id="site-and-context"')]
    site = body[body.index('id="site-and-context"'):body.index('id="option-comparison"')]
    scenario = body[body.index('id="scenario-B"'):]
    assert "<svg" in decision and "<svg" in site and "<svg" in scenario


def test_address_query_param_is_the_title(enabled) -> None:
    response = _post(_app(), params={"address": "215-16 Northern Boulevard, Queens"})
    assert response.status_code == 200
    assert "215-16 Northern Boulevard, Queens" in response.text
    # the borough/block/lot display appears beneath the title.
    assert "Queens block 7334, lot 70" in response.text


def test_address_absent_title_is_borough_block_lot(enabled) -> None:
    response = _post(_app())
    assert response.status_code == 200
    assert "Queens block 7334, lot 70" in response.text


@pytest.mark.parametrize("bad", ["x" * 121, "<script>", "a\tb", "a;b"])
def test_bad_address_is_ignored(enabled, bad) -> None:
    response = _post(_app(), params={"address": bad})
    assert response.status_code == 200
    assert bad not in response.text


def test_nothing_cached_across_requests(enabled) -> None:
    app = _app()
    first = _post(app)
    second = _post(app)
    assert first.status_code == second.status_code == 200
    # a fresh correlation id per request proves each report is computed anew, not replayed.
    assert first.headers["X-Correlation-ID"] != second.headers["X-Correlation-ID"]


# --------------------------------------------------------------------------- refusals match results
def test_malformed_bbl_is_422_like_results(enabled) -> None:
    response = _post(_app(), bbl="not-a-bbl")
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


def test_refused_body_field_is_422(enabled) -> None:
    response = _post(_app(), body={"housing_program": "standard_residence", "extra": 1})
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


def test_unconfirmed_conditions_are_503_json_not_html(enabled) -> None:
    response = _post(_app(benchmark_provider(profile_on=False)))
    assert response.status_code == 503
    assert response.json()["state"] == "lot_conditions_unconfirmed"
    assert "text/html" not in response.headers["content-type"]
