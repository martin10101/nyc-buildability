"""Smoke test for the health endpoint (task M0-T004, scenario S1/S5)."""

from fastapi.testclient import TestClient

from app.main import API_VERSION, app

client = TestClient(app)


def test_health_returns_ok_and_version() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok", "version": API_VERSION}


def test_health_is_versioned_route() -> None:
    # The unversioned path must not exist (PRD section 21: /api/v1 prefix).
    response = client.get("/health")
    assert response.status_code == 404
