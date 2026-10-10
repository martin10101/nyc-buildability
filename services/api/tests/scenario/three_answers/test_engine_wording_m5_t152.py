"""M5-T152 (S5): the engine's user-facing wording no longer overstates or contradicts.

- No user-facing label says 'achieved' (a schedule is 'scheduled floor area', not 'achieved').
- Each add-on gain's reason states what is actually missing - a gain needs a building fitted to the
  site, and none is fitted yet - and never says building options are 'not known for this lot' while
  a building (building B) is worked.

The building-option label is checked on a GENERATED document where the building option is available
(the synthetic benchmark of ``test_three_answers_benchmark``), so reverting building_option.py's
label to 'Achieved ...' fails this test (the S5 mutation proof for the label).
"""

from __future__ import annotations

from app.scenario.three_answers.result_way_inputs import LABELS
from app.scenario.three_answers.three_way_document import (
    ADDON_GAIN_FOLLOWS_WITHHELD_BUILDING_OPTION,
)

from .test_three_answers_benchmark import _generate, _value


def test_s5_building_option_label_is_scheduled_not_achieved() -> None:
    """S5: the building option's floor-area value is labelled 'scheduled', never 'achieved', both
    on the engine's emitted value and in the merged-decision label table."""
    option = _generate().document["answers"]["building_option"]
    assert option["status"] == "available"
    value = _value(option, "achieved_zoning_floor_area")
    assert "achieved" not in value["label"].lower()
    assert "scheduled" in value["label"].lower()

    table_label = LABELS["achieved_zoning_floor_area"]
    assert "achieved" not in table_label.lower()
    assert "scheduled" in table_label.lower()

    # No label in the whole merged-decision table says 'achieved'.
    assert not [lbl for lbl in LABELS.values() if "achieved" in lbl.lower()]


def test_s5_addon_gain_reason_names_the_missing_fit_not_unknown_options() -> None:
    """S5: an add-on gain's reason says a building must be fitted to the site and none is yet; it
    never claims building options are not known for this lot (building B is worked)."""
    reason = ADDON_GAIN_FOLLOWS_WITHHELD_BUILDING_OPTION
    assert "fitted to the site" in reason
    assert "none is fitted" in reason
    assert "not known for this lot" not in reason
    assert "building options" not in reason.lower()
