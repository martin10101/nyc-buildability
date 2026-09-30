"""GET /api/v1/build-info (queue C-02, plan M1-02).

Proves the route returns ONLY the deployed commit, the API version and a fixed allowlist of
boolean flags: unset env -> "unknown" + every flag false; explicit true tokens -> true; no
raw env value, secret or unlisted variable ever reaches the response; the shape is stable;
the allowlist and its parsing cannot drift from the modules that own each flag.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import config
from app.api.v1 import dxf_import_api, site_definition
from app.api.v1.build_info import (
    COMMIT_ENV_VARS,
    FLAG_ENV_VARS,
    UNKNOWN_COMMIT,
    build_info_payload,
)
from app.api.v1.build_info import router as build_info_router
from app.main import API_VERSION, SECURITY_HEADERS, create_app
from app.spatial import live_provider, wide_street_live_provider

URL = "/api/v1/build-info"
SHA_40 = "0127fef0" + "3a4f8c54" * 4

# Pinned literally: changing the allowlist must be a reviewed edit here too.
EXPECTED_FLAGS = [
    "INTERNAL_RULE_EVAL_ENABLED",
    "INTERNAL_SCENARIO_ENABLED",
    "SITE_DEFINITION_WRITE_ENABLED",
    "DXF_IMPORT_ENABLED",
    "LIVE_SPATIAL_PROVIDER_ENABLED",
    "LIVE_WIDE_STREET_PROVIDER_ENABLED",
    "LANE_A_ENABLED",
    "LANE_B_ENABLED",
    "LANE_C_ENABLED",
    "LANE_D_ENABLED",
    "LANE_E_ENABLED",
]

TRUE_TOKENS = ["1", "true", "TRUE", " yes ", "On"]
FALSE_TOKENS = ["", "0", "false", "off", "no", "maybe", "enabled", "2", "tru"]

# Values that must never be echoed. Names are real (render.yaml / CODE_MAP §4) or made up.
SECRET_ENV = {
    "SUPABASE_SERVICE_ROLE_KEY": "svc-role-SECRET-5f2e1d",  # gitleaks:allow
    "SUPABASE_DB_URL": "postgres://admin:pw-SECRET-77@db.example:5432/app",  # gitleaks:allow
    "ANTHROPIC_API_KEY": "sk-ant-SECRET-a1b2c3",  # gitleaks:allow
    "GEOCLIENT_SUBSCRIPTION_KEY": "geo-SECRET-9x8y7z",  # gitleaks:allow
    "SOCRATA_APP_TOKEN": "soda-SECRET-q1w2e3",  # gitleaks:allow
    "SENTRY_DSN": "https://SECRET-key@o0.ingest.example/1",  # gitleaks:allow
    "INTERNAL_UNLISTED_ENABLED": "true",
    "LANE_Z_ENABLED": "true",
    "RENDER_SERVICE_ID": "srv-SECRET-d0e1f2",  # gitleaks:allow
}


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    for name in (*COMMIT_ENV_VARS, *FLAG_ENV_VARS):
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def _get(monkeypatch: pytest.MonkeyPatch, **env: str) -> dict:
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    response = TestClient(create_app()).get(URL)
    assert response.status_code == 200
    return response.json()


# --- defaults and shape ------------------------------------------------------------------


def test_unset_env_reports_unknown_commit_and_every_flag_false(clean_env) -> None:
    assert _get(clean_env) == {
        "commit": UNKNOWN_COMMIT,
        "version": API_VERSION,
        "flags": {name: False for name in EXPECTED_FLAGS},
    }


def test_response_shape_is_stable(clean_env) -> None:
    body = _get(clean_env, INTERNAL_SCENARIO_ENABLED="true", RENDER_GIT_COMMIT=SHA_40)
    assert list(body) == ["commit", "version", "flags"]
    assert isinstance(body["commit"], str)
    assert isinstance(body["version"], str)
    assert list(body["flags"]) == EXPECTED_FLAGS
    assert all(type(value) is bool for value in body["flags"].values())
    assert list(FLAG_ENV_VARS) == EXPECTED_FLAGS
    assert COMMIT_ENV_VARS == ("RENDER_GIT_COMMIT", "GIT_COMMIT_SHA")


def test_version_matches_health(clean_env) -> None:
    client = TestClient(create_app())
    health = client.get("/api/v1/health").json()
    assert client.get(URL).json()["version"] == health["version"] == API_VERSION


def test_version_is_read_from_the_serving_app() -> None:
    application = FastAPI(version="9.9.9")
    application.include_router(build_info_router)
    assert TestClient(application).get(URL).json()["version"] == "9.9.9"


# --- flags ---------------------------------------------------------------------------------


@pytest.mark.parametrize("name", EXPECTED_FLAGS)
def test_each_flag_set_true_reports_only_that_flag_true(clean_env, name) -> None:
    flags = _get(clean_env, **{name: "true"})["flags"]
    assert flags == {other: other == name for other in EXPECTED_FLAGS}


@pytest.mark.parametrize("token", TRUE_TOKENS)
def test_true_tokens_report_true(clean_env, token) -> None:
    flags = _get(clean_env, **{name: token for name in EXPECTED_FLAGS})["flags"]
    assert flags == {name: True for name in EXPECTED_FLAGS}


@pytest.mark.parametrize("token", FALSE_TOKENS)
def test_other_values_report_false(clean_env, token) -> None:
    flags = _get(clean_env, **{name: token for name in EXPECTED_FLAGS})["flags"]
    assert flags == {name: False for name in EXPECTED_FLAGS}


# --- commit --------------------------------------------------------------------------------


def test_render_commit_is_reported(clean_env) -> None:
    assert _get(clean_env, RENDER_GIT_COMMIT=SHA_40)["commit"] == SHA_40


def test_generic_commit_is_the_fallback(clean_env) -> None:
    assert _get(clean_env, GIT_COMMIT_SHA=SHA_40)["commit"] == SHA_40


def test_render_commit_wins_over_generic(clean_env) -> None:
    body = _get(clean_env, RENDER_GIT_COMMIT=SHA_40, GIT_COMMIT_SHA="abcdef1")
    assert body["commit"] == SHA_40


def test_invalid_render_commit_falls_back_to_generic(clean_env) -> None:
    body = _get(clean_env, RENDER_GIT_COMMIT="main", GIT_COMMIT_SHA=SHA_40)
    assert body["commit"] == SHA_40


def test_commit_is_normalized(clean_env) -> None:
    assert _get(clean_env, RENDER_GIT_COMMIT=f"  {SHA_40.upper()}\n")["commit"] == SHA_40


@pytest.mark.parametrize(
    "value",
    [
        "",
        "main",
        "abc123",  # shorter than 7
        "g" * 40,  # not hex
        "a" * 65,  # longer than a SHA-256 id
        f"{SHA_40};echo pwned",
        "sk-ant-SECRET-a1b2c3",  # gitleaks:allow
    ],
)
def test_non_sha_commit_values_read_unknown_and_are_never_echoed(clean_env, value) -> None:
    clean_env.setenv("RENDER_GIT_COMMIT", value)
    clean_env.setenv("GIT_COMMIT_SHA", value)
    response = TestClient(create_app()).get(URL)
    assert response.json()["commit"] == UNKNOWN_COMMIT
    if value:
        assert value not in response.text


# --- nothing but the allowlist -------------------------------------------------------------


def test_secret_and_unlisted_env_vars_never_appear(clean_env) -> None:
    for name, value in SECRET_ENV.items():
        clean_env.setenv(name, value)
    # A secret-looking value in an allowlisted flag is reported only as a boolean.
    clean_env.setenv("INTERNAL_RULE_EVAL_ENABLED", "hunter2-SECRET")  # gitleaks:allow
    response = TestClient(create_app()).get(URL)
    assert response.status_code == 200
    for name, value in SECRET_ENV.items():
        assert name not in response.text
        assert value not in response.text
    assert "SECRET" not in response.text
    assert list(response.json()["flags"]) == EXPECTED_FLAGS
    assert response.json()["flags"]["INTERNAL_RULE_EVAL_ENABLED"] is False


def test_query_string_cannot_select_other_variables(clean_env) -> None:
    clean_env.setenv("SUPABASE_SERVICE_ROLE_KEY", SECRET_ENV["SUPABASE_SERVICE_ROLE_KEY"])
    client = TestClient(create_app())
    plain = client.get(URL)
    probed = client.get(URL, params={"flag": "SUPABASE_SERVICE_ROLE_KEY", "name": "SENTRY_DSN"})
    assert probed.status_code == 200
    assert probed.json() == plain.json()
    assert "SECRET" not in probed.text


class _RecordingEnv(Mapping[str, str]):
    """Records every key looked up; refuses enumeration so the payload cannot scan env."""

    def __init__(self, values: dict[str, str]) -> None:
        self._values = values
        self.looked_up: list[str] = []

    def __getitem__(self, key: str) -> str:
        self.looked_up.append(key)
        return self._values[key]

    def __iter__(self) -> Iterator[str]:
        raise AssertionError("build-info must not enumerate the environment")

    def __len__(self) -> int:
        raise AssertionError("build-info must not enumerate the environment")


def test_only_allowlisted_variables_are_read() -> None:
    env = _RecordingEnv({**SECRET_ENV, "LANE_C_ENABLED": "1"})
    payload = build_info_payload("0.0.0", env=env)
    assert set(env.looked_up) <= set(COMMIT_ENV_VARS) | set(FLAG_ENV_VARS)
    assert payload["flags"]["LANE_C_ENABLED"] is True


# --- HTTP posture --------------------------------------------------------------------------


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_only_get_is_served(clean_env, method) -> None:
    response = getattr(TestClient(create_app()), method)(URL)
    assert response.status_code == 405


def test_security_headers_present(clean_env) -> None:
    response = TestClient(create_app()).get(URL)
    for header, value in SECURITY_HEADERS.items():
        assert response.headers[header] == value


# --- no drift from the modules that own each flag --------------------------------------------

_OWNER_READERS = {
    config.INTERNAL_RULE_EVAL_ENABLED_ENV_VAR: config.internal_rule_eval_enabled,
    config.INTERNAL_SCENARIO_ENABLED_ENV_VAR: config.internal_scenario_enabled,
    site_definition.SITE_DEFINITION_WRITE_ENABLED_ENV_VAR: (
        site_definition.site_definition_write_enabled
    ),
    dxf_import_api.DXF_IMPORT_ENABLED_ENV_VAR: dxf_import_api.dxf_import_enabled,
    live_provider.LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR: (
        live_provider.live_spatial_provider_enabled
    ),
    wide_street_live_provider.LIVE_WIDE_STREET_PROVIDER_ENABLED_ENV_VAR: (
        wide_street_live_provider.live_wide_street_provider_enabled
    ),
}


def test_owner_flag_names_are_all_allowlisted() -> None:
    assert set(_OWNER_READERS) <= set(FLAG_ENV_VARS)
    # Lane flags land in app.config with M0-T164; once present they must all be reported.
    lane_env_vars = getattr(config, "LANE_FLAG_ENV_VARS", None)
    if lane_env_vars is not None:
        assert set(lane_env_vars.values()) <= set(FLAG_ENV_VARS)


@pytest.mark.parametrize("token", [None, *TRUE_TOKENS, *FALSE_TOKENS])
def test_build_info_agrees_with_every_owner_reader(token) -> None:
    for name, reader in _OWNER_READERS.items():
        env = {} if token is None else {name: token}
        assert build_info_payload("0.0.0", env=env)["flags"][name] is reader(env=env), name
