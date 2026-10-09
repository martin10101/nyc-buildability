"""The drawing kit sits behind the Lane E flag, default OFF (fail safe)."""

from __future__ import annotations

import pytest

from app.drawings.kit import (
    DrawingKitDisabled,
    drawing_kit_enabled,
    render_massing,
    render_site_plan,
)

from .kit_support import CONTRACT_FIXTURES, load

DOC = load(CONTRACT_FIXTURES / "synthetic_all_answers_available.json")


@pytest.mark.parametrize("env", [{}, {"LANE_E_ENABLED": ""}, {"LANE_E_ENABLED": "0"},
                                 {"LANE_E_ENABLED": "false"}, {"LANE_E_ENABLED": "maybe"},
                                 {"LANE_D_ENABLED": "1"}])
def test_off_unless_explicitly_on(env):
    assert not drawing_kit_enabled(env)
    with pytest.raises(DrawingKitDisabled):
        render_site_plan(DOC, env=env)
    with pytest.raises(DrawingKitDisabled):
        render_massing(DOC, env=env)


def test_off_by_default_in_the_process_environment(monkeypatch):
    monkeypatch.delenv("LANE_E_ENABLED", raising=False)
    assert not drawing_kit_enabled()
    with pytest.raises(DrawingKitDisabled):
        render_site_plan(DOC)


@pytest.mark.parametrize("token", ["1", "true", "YES", " on "])
def test_on_with_an_explicit_true_token(token):
    assert drawing_kit_enabled({"LANE_E_ENABLED": token})
