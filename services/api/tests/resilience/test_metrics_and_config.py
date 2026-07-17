"""Item H (metrics/log hooks) and configuration surface tests.

Structured, secret-free observability: breaker state, cache hit ratio, and
budget consumption are countable; no hook event ever carries the app token
or header material. Config: documented defaults, env injection, loud
failure on invalid values.
"""

import json
import logging

import pytest

from app.resilience.budget import AnalysisBudget
from app.resilience.config import ResilienceConfig
from app.resilience.metrics import ResilienceMetrics, logging_metrics_hook
from tests.resilience.helpers import (
    BBL,
    make_harness,
    ok_response,
    server_error_response,
)


def test_metrics_counters_and_hit_ratio():
    metrics = ResilienceMetrics(hook=lambda event, fields: None)
    assert metrics.cache_hit_ratio() is None
    metrics.emit("cache_miss", key="k")
    metrics.emit("cache_hit", key="k")
    metrics.emit("cache_hit", key="k")
    assert metrics.count("cache_hit") == 2
    assert metrics.cache_hit_ratio() == 2 / 3
    assert metrics.snapshot() == {"cache_hit": 2, "cache_miss": 1}


def test_logging_hook_emits_single_json_escaped_line(caplog):
    with caplog.at_level(logging.INFO, logger="app.resilience.metrics"):
        logging_metrics_hook("test_event", {"hostile": "a\r\nb", "n": 1})
    (record,) = caplog.records
    message = record.getMessage()
    assert "test_event" in message
    # json.dumps escaping: the hostile value cannot break the log line.
    assert "\n" not in message and "\r" not in message
    assert '"a\\r\\nb"' in message


def test_no_secret_material_in_any_metrics_event():
    secret = "SECRET-TOKEN-M1T009"
    harness = make_harness(
        [server_error_response(), ok_response()],
        config=ResilienceConfig(retry_max_attempts=2),
        fetch_kwargs={"app_token": secret},
    )
    harness.fetcher(BBL, "corr-1", budget=AnalysisBudget(5, analysis_id="a1"))
    assert len(harness.hook.events) > 0
    serialized = json.dumps(harness.hook.events, default=str)
    assert secret not in serialized
    assert "x-app-token" not in serialized.lower()


def test_config_defaults_are_documented_values():
    config = ResilienceConfig()
    assert config.cache_ttl_seconds == 900.0
    assert config.cache_key_version == "v1"
    assert config.retry_max_attempts == 3
    assert config.backoff_base_seconds == 0.5
    assert config.backoff_cap_seconds == 30.0
    assert config.retry_after_max_wait_seconds == 120.0
    assert config.breaker_failure_threshold == 5
    assert config.breaker_cooldown_seconds == 60.0
    assert config.lkg_max_age_seconds == 86_400.0
    assert config.cache_max_entries == 10_000
    assert config.lkg_max_entries == 10_000


def test_config_from_env_overrides_and_defaults():
    environ = {
        "RESILIENCE_CACHE_TTL_SECONDS": "120.5",
        "RESILIENCE_RETRY_MAX_ATTEMPTS": "5",
        "RESILIENCE_CACHE_KEY_VERSION": "v2",
    }
    config = ResilienceConfig.from_env(environ)
    assert config.cache_ttl_seconds == 120.5
    assert config.retry_max_attempts == 5
    assert config.cache_key_version == "v2"
    assert config.breaker_failure_threshold == 5  # untouched default


@pytest.mark.parametrize(
    "environ",
    [
        {"RESILIENCE_CACHE_TTL_SECONDS": "not-a-number"},
        {"RESILIENCE_RETRY_MAX_ATTEMPTS": "2.5"},
        {"RESILIENCE_CACHE_TTL_SECONDS": "-30"},
        {"RESILIENCE_BREAKER_FAILURE_THRESHOLD": "0"},
    ],
)
def test_config_from_env_fails_loudly_on_invalid_values(environ):
    with pytest.raises(RuntimeError):
        ResilienceConfig.from_env(environ)


def test_config_direct_validation():
    with pytest.raises(ValueError):
        ResilienceConfig(cache_ttl_seconds=0)
    with pytest.raises(ValueError):
        ResilienceConfig(retry_max_attempts=0)
    with pytest.raises(ValueError):
        ResilienceConfig(cache_key_version="")
