"""Lane flags (task M0-T164, D-090): one per lane, absent means off (fail safe).

Also covers the DB-232 / M5-T158 internal zoning-lot-index live-binding flag, which has the
same fail-safe posture as every INTERNAL_* flag.
"""

from __future__ import annotations

import pytest

from app.config import (
    INTERNAL_ZONING_LOT_INDEX_ENABLED_ENV_VAR,
    LANE_FLAG_ENV_VARS,
    internal_zoning_lot_index_enabled,
    lane_enabled,
)


def test_one_flag_per_lane_with_stable_names() -> None:
    assert LANE_FLAG_ENV_VARS == {
        "A": "LANE_A_ENABLED",
        "B": "LANE_B_ENABLED",
        "C": "LANE_C_ENABLED",
        "D": "LANE_D_ENABLED",
        "E": "LANE_E_ENABLED",
    }


@pytest.mark.parametrize("lane", ["A", "B", "C", "D", "E"])
def test_absent_flag_is_off(lane: str) -> None:
    assert lane_enabled(lane, env={}) is False


@pytest.mark.parametrize("raw", ["", "0", "false", "off", "no", "maybe", " "])
def test_non_true_values_are_off(raw: str) -> None:
    assert lane_enabled("A", env={"LANE_A_ENABLED": raw}) is False


@pytest.mark.parametrize("raw", ["1", "true", "TRUE", " yes ", "on"])
def test_explicit_true_tokens_are_on(raw: str) -> None:
    assert lane_enabled("D", env={"LANE_D_ENABLED": raw}) is True


def test_flags_are_independent() -> None:
    env = {"LANE_B_ENABLED": "true"}
    assert lane_enabled("B", env=env) is True
    assert [lane for lane in "ACDE" if lane_enabled(lane, env=env)] == []


def test_unknown_lane_raises() -> None:
    with pytest.raises(ValueError):
        lane_enabled("F", env={})


def test_process_environment_default_is_off(monkeypatch: pytest.MonkeyPatch) -> None:
    for env_var in LANE_FLAG_ENV_VARS.values():
        monkeypatch.delenv(env_var, raising=False)
    assert not any(lane_enabled(lane) for lane in LANE_FLAG_ENV_VARS)


# ---------------------------------------------------------------------------
# DB-232 / M5-T158: the internal zoning-lot-index live-binding flag.
# ---------------------------------------------------------------------------
def test_zoning_lot_index_flag_name_is_stable() -> None:
    assert INTERNAL_ZONING_LOT_INDEX_ENABLED_ENV_VAR == "INTERNAL_ZONING_LOT_INDEX_ENABLED"


def test_zoning_lot_index_flag_absent_is_off() -> None:
    assert internal_zoning_lot_index_enabled(env={}) is False


@pytest.mark.parametrize("raw", ["", "0", "false", "off", "no", "maybe", " "])
def test_zoning_lot_index_flag_non_true_values_are_off(raw: str) -> None:
    assert internal_zoning_lot_index_enabled(
        env={INTERNAL_ZONING_LOT_INDEX_ENABLED_ENV_VAR: raw}
    ) is False


@pytest.mark.parametrize("raw", ["1", "true", "TRUE", " yes ", "on"])
def test_zoning_lot_index_flag_explicit_true_tokens_are_on(raw: str) -> None:
    assert internal_zoning_lot_index_enabled(
        env={INTERNAL_ZONING_LOT_INDEX_ENABLED_ENV_VAR: raw}
    ) is True


def test_zoning_lot_index_flag_process_default_is_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(INTERNAL_ZONING_LOT_INDEX_ENABLED_ENV_VAR, raising=False)
    assert internal_zoning_lot_index_enabled() is False
