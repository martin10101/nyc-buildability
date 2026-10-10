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
    BEST_COMBINATION_FOLLOWS_WITHHELD_BUILDING_OPTION,
    FLOOR_STACK_FOLLOWS_WITHHELD_BUILDING_OPTION,
    SHORTFALL_FOLLOWS_WITHHELD_BUILDING_OPTION,
)

from .test_three_answers_benchmark import _generate, _value

# Every reason that follows a withheld single building option (shortfall, best combination, floor
# stack, add-on gain) must name what is actually missing - a building fitted to the site - and must
# never say a building option is 'not known' for this lot while building B is worked (rework 2 B1).
_FOLLOWS_WITHHELD_REASONS = (
    SHORTFALL_FOLLOWS_WITHHELD_BUILDING_OPTION,
    BEST_COMBINATION_FOLLOWS_WITHHELD_BUILDING_OPTION,
    FLOOR_STACK_FOLLOWS_WITHHELD_BUILDING_OPTION,
    ADDON_GAIN_FOLLOWS_WITHHELD_BUILDING_OPTION,
)


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


def test_s5_no_follows_withheld_reason_says_building_options_not_known() -> None:
    """S5 / rework 2 (B1): the shortfall, best-combination, floor-stack and add-on-gain reasons each
    name what is actually missing (a building fitted to the site) and NONE says a building option is
    'not known for this lot' - correcting the best combination's stale sentence shown on the report
    while building B is worked. Reverting any constant to the 'building option(s) ... not known'
    wording fails this test (the B1 mutation proof)."""
    for reason in _FOLLOWS_WITHHELD_REASONS:
        assert "fitted to the site" in reason, reason
        assert "not known for this lot" not in reason, reason
        assert "building option" not in reason.lower(), reason


def test_s5_benchmark_document_has_no_stale_building_option_sentence() -> None:
    """S5 / rework 2 (B1): the committed benchmark three-way document (building B worked) carries no
    user-facing reason saying a building option is 'not known for this lot'; its shortfall and best
    combination reasons name the missing site fit."""
    import json
    from pathlib import Path

    repo = Path(__file__).resolve().parents[5]
    fixture = (repo / "packages" / "contracts" / "fixtures" / "valid" / "results"
               / "recorded_215_16_northern_journey.json")
    document = json.loads(fixture.read_text(encoding="utf-8"))
    text = json.dumps(document)
    assert "building option, which is not known for this lot" not in text
    assert "building options, which are not known for this lot" not in text
    assert "fitted to the site" in document["shortfall"]["reason"]
    assert "fitted to the site" in document["best_combination"]["reason"]
