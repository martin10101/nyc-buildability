"""CORS allowlist + security-header middleware tests (task M0-T015, scenario S4).

Proves, per the owner deployment-blocker directive:
- a configured origin is allowed (simple request and preflight),
- a disallowed origin receives no CORS grant (and preflight is rejected),
- wildcard origins combined with credentialed requests are IMPOSSIBLE
  (explicit negative test: startup fails),
- allowed origins are read from the environment (API_CORS_ALLOWED_ORIGINS),
  with deny-all as the unset default,
- baseline security headers are present on API responses.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import (
    API_VERSION,
    CORS_ORIGINS_ENV_VAR,
    SECURITY_HEADERS,
    create_app,
)

ALLOWED_ORIGIN = "https://nycdf-web.onrender.com"
SECOND_ALLOWED_ORIGIN = "https://staging-nycdf-web.onrender.com"
DISALLOWED_ORIGIN = "https://evil.example.com"


def _client(monkeypatch: pytest.MonkeyPatch, origins: str | None) -> TestClient:
    """Build a fresh app with the given env-var value (None = unset)."""
    if origins is None:
        monkeypatch.delenv(CORS_ORIGINS_ENV_VAR, raising=False)
    else:
        monkeypatch.setenv(CORS_ORIGINS_ENV_VAR, origins)
    return TestClient(create_app())


# --- allowed origin -------------------------------------------------------


def test_configured_origin_is_allowed(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client(monkeypatch, f"{ALLOWED_ORIGIN}, {SECOND_ALLOWED_ORIGIN}")
    response = client.get("/api/v1/health", headers={"Origin": ALLOWED_ORIGIN})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"


def test_preflight_for_configured_origin_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client(monkeypatch, ALLOWED_ORIGIN)
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"


# --- disallowed origin ----------------------------------------------------


def test_disallowed_origin_receives_no_cors_grant(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client(monkeypatch, ALLOWED_ORIGIN)
    response = client.get("/api/v1/health", headers={"Origin": DISALLOWED_ORIGIN})
    # The request itself succeeds (non-browser clients are unaffected), but
    # NO Access-Control-Allow-Origin grant is emitted, so browsers block it.
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_preflight_for_disallowed_origin_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client(monkeypatch, ALLOWED_ORIGIN)
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": DISALLOWED_ORIGIN,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


# --- wildcard + credentials is impossible (explicit negative test) --------


@pytest.mark.parametrize(
    "wildcard_value",
    [
        "*",
        " * ",
        f"{ALLOWED_ORIGIN}, *",
        "https://*.example.com",
    ],
)
def test_wildcard_origin_with_credentials_is_impossible(
    monkeypatch: pytest.MonkeyPatch, wildcard_value: str
) -> None:
    monkeypatch.setenv(CORS_ORIGINS_ENV_VAR, wildcard_value)
    with pytest.raises(RuntimeError, match="wildcard origins are forbidden"):
        create_app()


# --- environment-driven configuration ------------------------------------


def test_unset_env_means_no_cross_origin_access(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client(monkeypatch, None)
    response = client.get("/api/v1/health", headers={"Origin": ALLOWED_ORIGIN})
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_empty_env_means_no_cross_origin_access(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client(monkeypatch, "  ")
    response = client.get("/api/v1/health", headers={"Origin": ALLOWED_ORIGIN})
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


# --- security headers -----------------------------------------------------


def test_security_headers_present_on_api_responses(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client(monkeypatch, None)
    response = client.get("/api/v1/health")
    for header, value in SECURITY_HEADERS.items():
        assert response.headers.get(header) == value, header


def test_security_headers_present_on_error_responses(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client(monkeypatch, None)
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    for header, value in SECURITY_HEADERS.items():
        assert response.headers.get(header) == value, header


def test_docs_page_exempt_from_csp_only(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client(monkeypatch, None)
    response = client.get("/docs")
    assert response.status_code == 200
    assert "content-security-policy" not in response.headers
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"


# --- regression -----------------------------------------------------------


def test_health_contract_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client(monkeypatch, None)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": API_VERSION}
    # The unversioned path must still not exist (PRD section 21).
    assert client.get("/health").status_code == 404
