"""Parity and value checks for the generated presentation-token module.

The single source is ``docs/design/presentation-tokens.json`` (task M5-T148
part A). The module ``app.drawings.kit.presentation_tokens`` is generated from
it by ``apps/web/scripts/presentation-tokens.mjs``. These tests read the JSON
directly and compare it with the module, so a changed JSON value that was not
regenerated fails here as well as in the Node parity test.
"""

import json
from pathlib import Path

from app.drawings.kit import presentation_tokens

GROUPS = ("color", "spacing", "control", "radius", "font", "type", "status")
_REPO_ROOT = Path(__file__).resolve().parents[4]
_JSON_PATH = _REPO_ROOT / "docs" / "design" / "presentation-tokens.json"
_FONT_STACK = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"


def _load_json_subset() -> dict:
    raw = json.loads(_JSON_PATH.read_text(encoding="utf-8"))
    return {group: raw[group] for group in GROUPS}


def test_module_mirrors_the_json_source() -> None:
    assert presentation_tokens.TOKENS == _load_json_subset()


def test_changed_json_colour_without_regeneration_fails() -> None:
    drifted = _load_json_subset()
    drifted["color"]["ink"] = "#000000"
    assert drifted != presentation_tokens.TOKENS


def test_contract_section_5_values() -> None:
    tokens = presentation_tokens.TOKENS
    assert list(tokens["spacing"].values()) == [4, 8, 12, 16, 24, 32, 48]
    assert len(tokens["color"]) == 9
    assert tokens["color"]["ink"] == "#182B3A"
    assert tokens["color"]["caution-surface"] == "#FBF4E7"
    assert tokens["control"]["height"] == 44
    assert tokens["control"]["radius"] == 6
    assert tokens["radius"]["panel"] == 8
    assert tokens["font"]["family"] == _FONT_STACK


def test_font_token_equals_the_application_stack() -> None:
    layout_path = _REPO_ROOT / "apps" / "web" / "src" / "app" / "layout.tsx"
    layout = layout_path.read_text(encoding="utf-8")
    stack = presentation_tokens.TOKENS["font"]["family"]
    assert "fontFamily:" in layout
    assert f'"{stack}"' in layout


def test_status_words_are_settled_conditional_not_known_no_verified() -> None:
    status = presentation_tokens.TOKENS["status"]
    assert status["settled"]["marker"] is False
    assert status["conditional"]["marker"] is True
    assert status["conditional"]["color_role"] == "secondary"
    assert status["not-known"]["marker"] is True
    assert "verified" not in status


def test_module_lines_stay_within_100_chars() -> None:
    module_path = Path(presentation_tokens.__file__)
    for line in module_path.read_text(encoding="utf-8").splitlines():
        assert len(line) <= 100
