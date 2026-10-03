"""Real-app MOUNT posture for the three W5-mounted internal reads
(hidden-issue-flags W2, transit-parking W3, parity W4).

Packet W5 mounts these routers in ``app.main`` self-gated and default off. Each
route's full per-case behaviour (422/429/503/500/contract/matrix) is covered
exhaustively by its own suite over a LOCAL app; THIS suite proves only the MOUNT
posture against the REAL application factory (``app.main.create_app``):

- flag unset, and flag set to a non-true token -> a generic 404 byte-identical to
  an unmounted path (same body, content-type, no X-Correlation-ID), so a disabled
  feature is indistinguishable from a route that does not exist (fail-safe);
- flag on -> the route is reachable (a 200 produced OFFLINE from recorded official
  fixtures through the route's injected provider seam);
- the path is absent from /openapi.json in BOTH states (include_in_schema=False).

Fully offline: the reachable cases override each route's injected provider with a
recorded-fixture provider (the 215-16 Northern PLUTO pack for W2/W3, the Bayside
DOF pack for W4); no network is touched and no fixture data is invented.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import hidden_issue_flags_read as hidden_mod
from app.api.v1 import parity_read as parity_mod
from app.api.v1 import transit_parking_read as transit_mod
from app.api.v1.hidden_issue_flags_inputs import pluto_hidden_issue_flag_inputs_provider
from app.api.v1.transit_parking_read import pluto_transit_parking_provider
from app.config import (
    INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED_ENV_VAR,
    INTERNAL_PARITY_READ_ENABLED_ENV_VAR,
    INTERNAL_TRANSIT_PARKING_READ_ENABLED_ENV_VAR,
    LANE_FLAG_ENV_VARS,
)
from app.connectors.dof_sales_soda import build_by_bbl_url, build_candidates_url
from app.connectors.pluto_soda import TransportResponse as PlutoTransportResponse
from app.connectors.pluto_soda import fetch_by_bbl
from app.main import create_app
from app.resilience.transport import Transport
from app.resilience.transport import TransportResponse as DofTransportResponse

NORTHERN_BBL = "4073340070"
FIXED_CLOCK = lambda: datetime(2026, 9, 30, 12, 0, 0, tzinfo=UTC)  # noqa: E731
LANE_B_ON = {"LANE_B_ENABLED": "1"}
LANE_B_ENV_VAR = LANE_FLAG_ENV_VARS["B"]

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
PLUTO_FIXTURE = FIXTURES / "benchmark_215_16_northern" / "pluto_64uk-42ks_bbl_4073340070.json"
DOF_PACK = FIXTURES / "dof_sales_bayside"
NEIGHBORHOOD = "BAYSIDE"
BUILDING_CLASS = "22 STORE BUILDINGS"

# A structurally-similar path that is NOT mounted (an extra segment beyond the
# single-segment {bbl}), so it hits FastAPI's generic 404 - the byte template a
# flag-off read must be indistinguishable from.
UNMOUNTED_PROBE = f"/api/v1/properties/{NORTHERN_BBL}/__unmounted_probe__"

# (name, request path, OpenAPI path template, flag env var).
HIDDEN = (
    "hidden-issue-flags",
    f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags",
    "/api/v1/properties/{bbl}/hidden-issue-flags",
    INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED_ENV_VAR,
)
TRANSIT = (
    "transit-parking",
    f"/api/v1/properties/{NORTHERN_BBL}/transit-parking",
    "/api/v1/properties/{bbl}/transit-parking",
    INTERNAL_TRANSIT_PARKING_READ_ENABLED_ENV_VAR,
)
PARITY = (
    "parity",
    f"/api/v1/properties/{NORTHERN_BBL}/parity",
    "/api/v1/properties/{bbl}/parity",
    INTERNAL_PARITY_READ_ENABLED_ENV_VAR,
)
ALL_ROUTES = [HIDDEN, TRANSIT, PARITY]


@pytest.fixture(autouse=True)
def _reset_rate_limiters():
    """The per-route limiters are module-level, process-wide state keyed by the
    shared TestClient host; reset them around every test so cases cannot
    accumulate stamps into a spurious 429."""
    for mod in (hidden_mod, transit_mod, parity_mod):
        mod.get_rate_limiter().reset()
    yield
    for mod in (hidden_mod, transit_mod, parity_mod):
        mod.get_rate_limiter().reset()


def _northern_pluto_fetcher(bbl: str, correlation_id: str):
    """Replay the recorded 215-16 Northern PLUTO body through the real connector."""
    body = PLUTO_FIXTURE.read_text(encoding="utf-8")
    return fetch_by_bbl(
        bbl,
        transport=lambda url, headers, timeout: PlutoTransportResponse(200, body),
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        correlation_id=correlation_id,
    )


def _bayside_dof_transport() -> Transport:
    """A routed DOF transport serving the recorded Bayside pack for the exact two
    request urls the route builds, else failing (no live-shaped url is served)."""
    by_bbl_url = build_by_bbl_url(NORTHERN_BBL, row_limit=parity_mod.SUBJECT_SALES_ROW_LIMIT)
    candidates_url = build_candidates_url(
        NEIGHBORHOOD, BUILDING_CLASS, row_limit=parity_mod.CANDIDATE_ROW_LIMIT
    )
    routes = {
        by_bbl_url: (DOF_PACK / "dof_sales_w2pb-icbu_bbl_4073340070.json").read_text(
            encoding="utf-8"
        ),
        candidates_url: (
            DOF_PACK / "dof_sales_w2pb-icbu_bayside_22_store_buildings.json"
        ).read_text(encoding="utf-8"),
    }
    vintage = {"x-soda2-truth-last-modified": "2026-09-01"}

    def transport(url: str, headers: dict, timeout: float) -> DofTransportResponse:
        assert url in routes, f"unexpected url {url!r}"
        return DofTransportResponse(200, routes[url], dict(vintage))

    return transport


# ---------------------------------------------------------------------------
# Flag OFF (unset) -> generic 404 byte-identical to an unmounted path
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name,path,template,env_var", ALL_ROUTES)
def test_flag_unset_is_404_byte_identical_to_unmounted(
    monkeypatch, name, path, template, env_var
) -> None:
    monkeypatch.delenv(env_var, raising=False)
    client = TestClient(create_app())
    unknown = client.get(UNMOUNTED_PROBE)
    response = client.get(path)
    assert response.status_code == unknown.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    # Byte-identical to the unmounted path: same body bytes and content type, and
    # no server-minted correlation id to hint the feature exists.
    assert response.content == unknown.content
    assert response.headers.get("content-type") == unknown.headers.get("content-type")
    assert "X-Correlation-ID" not in response.headers


@pytest.mark.parametrize("name,path,template,env_var", ALL_ROUTES)
@pytest.mark.parametrize("token", ["0", "", "false", "off", "maybe"])
def test_non_true_flag_token_stays_404(monkeypatch, name, path, template, env_var, token) -> None:
    monkeypatch.setenv(env_var, token)
    response = TestClient(create_app()).get(path)
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in response.headers


# ---------------------------------------------------------------------------
# OpenAPI: the path is absent in BOTH states (include_in_schema=False)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name,path,template,env_var", ALL_ROUTES)
def test_path_absent_from_openapi_when_flag_off(
    monkeypatch, name, path, template, env_var
) -> None:
    monkeypatch.delenv(env_var, raising=False)
    spec = TestClient(create_app()).get("/openapi.json").json()
    assert template not in spec["paths"]


@pytest.mark.parametrize("name,path,template,env_var", ALL_ROUTES)
def test_path_absent_from_openapi_when_flag_on(
    monkeypatch, name, path, template, env_var
) -> None:
    monkeypatch.setenv(env_var, "1")
    spec = TestClient(create_app()).get("/openapi.json").json()
    assert template not in spec["paths"]


# ---------------------------------------------------------------------------
# Flag ON -> the route is reachable on the REAL app (200 from recorded fixtures)
# ---------------------------------------------------------------------------
def test_hidden_issue_flags_reachable_when_flag_on(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED_ENV_VAR, "1")
    app = create_app()
    provider = pluto_hidden_issue_flag_inputs_provider(
        _northern_pluto_fetcher, clock=FIXED_CLOCK, env=LANE_B_ON
    )
    app.dependency_overrides[hidden_mod.get_hidden_issue_flag_inputs_provider] = (
        lambda: provider
    )
    response = TestClient(app).get(HIDDEN[1])
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"]
    body = response.json()
    assert set(body) == {"contract_version", "groups"}
    assert body["contract_version"] == "1.0.0"


def test_transit_parking_reachable_when_flag_on(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_TRANSIT_PARKING_READ_ENABLED_ENV_VAR, "1")
    app = create_app()
    provider = pluto_transit_parking_provider(
        _northern_pluto_fetcher, clock=FIXED_CLOCK, env=LANE_B_ON
    )
    app.dependency_overrides[transit_mod.get_transit_parking_provider] = lambda: provider
    response = TestClient(app).get(TRANSIT[1])
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"]
    body = response.json()
    assert body["contract_version"] == "1.1.0"
    assert body["transit_zone"] == "Outer Transit Zone"


def test_parity_reachable_when_flag_on(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_PARITY_READ_ENABLED_ENV_VAR, "1")
    monkeypatch.setenv(LANE_B_ENV_VAR, "1")  # parity data is Lane B behaviour
    app = create_app()
    transport = _bayside_dof_transport()
    app.dependency_overrides[parity_mod.get_dof_transport] = lambda: transport
    response = TestClient(app).get(PARITY[1])
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"]
    body = response.json()
    assert set(body) == {"contract_version", "comparable_sales", "unused_floor_area"}
    assert body["unused_floor_area"]["status"] == "not_confirmed"
