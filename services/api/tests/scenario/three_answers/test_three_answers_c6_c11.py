"""A-05 tests on the 215-16 Northern Blvd benchmark: C-6 (no duplicate options - merge or
explain) and C-11 (no template sentences - every explanation is emitted only when computed
true). Directive D-090.

The benchmark inputs and expected values are reused from
``test_three_answers_benchmark`` (never restated); C-6 builds synthetic multi-option studies
from those same inputs, and C-11 flips each computed condition and proves its sentence moves.
"""

from __future__ import annotations

import json

from app.scenario.three_answers import (
    BuildingDefaults,
    build_status_strip,
    find_duplicate_options,
    generate_results,
    merge_or_explain,
    option_identity_key,
    site_measurement_status_chip,
)
from app.scenario.three_answers.explanations import (
    APPROXIMATE_MEASUREMENTS_CHIP,
    SURVEY_MEASUREMENTS_CHIP,
)

from .test_three_answers_benchmark import _ON, _benchmark_inputs, _generate

# ---------------------------------------------------------------------------
# C-6: no duplicate options (merge or explain)
# ---------------------------------------------------------------------------


def _doc(option_id: str, **overrides) -> dict:
    return generate_results(
        _benchmark_inputs(option_id=option_id, results_id=f"res-{option_id}", **overrides),
        env=_ON,
    ).document


def test_identical_inputs_produce_the_same_building_identity_key() -> None:
    # Two options from identical inputs differ only in ids; the building identity ignores ids.
    a = _doc("opt-a")
    a2 = _doc("opt-a2")
    assert a["option_id"] != a2["option_id"]
    assert a["results_id"] != a2["results_id"]
    assert option_identity_key(a) == option_identity_key(a2)


def test_two_identical_options_are_detected_and_merged() -> None:
    a, a2 = _doc("opt-a"), _doc("opt-a2")
    groups = find_duplicate_options([a, a2])
    assert len(groups) == 1
    assert len(groups[0]) == 2
    record = merge_or_explain(groups[0])
    assert record["action"] == "merge"
    assert record["reason"] == "identical building"
    assert record["surviving_option_id"] == "opt-a"
    assert set(record["merged_option_ids"]) == {"opt-a", "opt-a2"}


def test_options_differing_in_floor_to_floor_are_distinct_and_explained() -> None:
    a = _doc("opt-a")
    b = _doc("opt-b", building_defaults=BuildingDefaults(floor_to_floor_ft=12.0))
    # Distinct buildings: not reported as duplicates.
    assert option_identity_key(a) != option_identity_key(b)
    assert find_duplicate_options([a, b]) == []
    # Explained by field and value - the explanation NAMES floor_to_floor_ft and both values.
    record = merge_or_explain([a, b])
    assert record["action"] == "explain"
    by_field = {d["field"]: d for d in record["differences"]}
    assert "floor_to_floor_ft" in by_field
    values = {v["option_id"]: v["value"] for v in by_field["floor_to_floor_ft"]["values"]}
    assert values == {"opt-a": 10.0, "opt-b": 12.0}


def test_three_options_two_identical_yield_one_merge_group() -> None:
    a = _doc("opt-a")
    a2 = _doc("opt-a2")
    b = _doc("opt-b", building_defaults=BuildingDefaults(floor_to_floor_ft=12.0))
    groups = find_duplicate_options([a, a2, b])
    assert len(groups) == 1
    assert {d["option_id"] for d in groups[0]} == {"opt-a", "opt-a2"}
    assert merge_or_explain(groups[0])["action"] == "merge"


# ---------------------------------------------------------------------------
# C-11: no template sentences (every explanation only when computed true)
# ---------------------------------------------------------------------------


def test_approximate_measurements_chip_flips_with_the_site_measurement_rank() -> None:
    # Fix-does-not-corrupt: the status-strip measurement chip must be the field the pre-fix bug
    # displaced. With the benchmark default rank (city records) it is approximate; with a survey
    # rank it flips to "Survey measurements" and never says "Approximate measurements". Reverting
    # to the hardcoded literal would keep the survey case on "Approximate measurements".
    default_doc = _generate().document
    strip_texts = [chip["text"] for chip in default_doc["status_strip"]]
    assert APPROXIMATE_MEASUREMENTS_CHIP in strip_texts
    assert SURVEY_MEASUREMENTS_CHIP not in strip_texts

    survey_doc = _generate(site_measurement_rank="survey_entered").document
    survey_texts = [chip["text"] for chip in survey_doc["status_strip"]]
    assert SURVEY_MEASUREMENTS_CHIP in survey_texts
    assert APPROXIMATE_MEASUREMENTS_CHIP not in survey_texts

    # The chip helper is the single source of the flip.
    assert site_measurement_status_chip("survey_entered") == {"text": SURVEY_MEASUREMENTS_CHIP}
    assert site_measurement_status_chip("city_records") == {"text": APPROXIMATE_MEASUREMENTS_CHIP}
    # The strip stays within the schema's 1..3 items and every chip is non-empty.
    assert 1 <= len(survey_doc["status_strip"]) <= 3
    assert all(chip["text"].strip() for chip in survey_doc["status_strip"])
    assert build_status_strip("survey_entered")[1] == {"text": SURVEY_MEASUREMENTS_CHIP}


def test_status_strip_first_item_is_preliminary_zoning_results() -> None:
    """S9 / M5-T144 (owner row D-090-R641): the status line's first item reads the owner's words
    'Preliminary zoning results'. The measurement chip and 'Lots you selected' are unchanged
    (R642: each result keeps its own state; this label changes no result's state). Reverting the
    label to the old 'Zoning maximum' would turn this red."""
    for rank in ("city_records", "survey_entered"):
        strip = build_status_strip(rank)
        assert strip[0] == {"text": "Preliminary zoning results"}
        assert strip[1] == site_measurement_status_chip(rank)  # the measurement chip, unchanged
        assert strip[2] == {"text": "Lots you selected"}  # unchanged
    # it is emitted into the on-path document too
    assert _generate().document["status_strip"][0] == {"text": "Preliminary zoning results"}


def test_rear_yard_waiver_sentence_only_when_the_waiver_is_computed() -> None:
    # Computed true on the benchmark corner lot: the "no rear yard required" sentence appears.
    waived = _generate().document["geometry"]["yards"]
    assert waived["status"] == "available"
    sentence = waived["entries"][0]["reason"]
    assert "No rear yard is required within 100 ft of the corner" in sentence
    # Flip the condition: not within 100 ft of a corner -> the waiver does not resolve, and the
    # "no rear yard required" sentence disappears (replaced by an honest not_available reason).
    not_corner = _generate(within_100_ft_of_street_line_intersection=False).document["geometry"]
    assert not_corner["yards"]["status"] == "not_available"
    assert "No rear yard is required" not in json.dumps(not_corner["yards"])


def test_no_shortfall_sentence_when_the_option_reaches_the_allowance() -> None:
    # On this lot the envelope holds the whole allowance, so no shortfall reason is emitted
    # (C-11): the competitor's "705 sq ft can't be captured" template never appears here.
    doc = _generate().document
    assert doc["shortfall"] == {"status": "none"}
    blob = json.dumps(doc).lower()
    assert "sq ft below the" not in blob  # the shortfall reason's signature phrase


def test_no_untrue_template_sentence_appears_on_the_benchmark() -> None:
    # The exact competitor template sentences C-11 names must never be emitted on this lot
    # (no shortfall, 55 ft limit, no height-cap story loss).
    blob = json.dumps(_generate().document).lower()
    for fragment in (
        "another floor would exceed",
        "can't be captured",
        "exceed the height limit",
        "exceed the 65 ft",
        "exceed the 60 ft",
    ):
        assert fragment not in blob, fragment


def test_fixed_scope_statements_are_present_and_are_standing_scope_notices() -> None:
    # The audit's fixed_scope entries: standing statements about families not built in this
    # slice. Each is always true because the slice never computes that family; C-11 keeps them
    # as not_available / scope notices, never as computed explanations.
    # (best_combination and the add-on completeness line are now COMPUTED by the add-on model
    # merged from A-06, so they left this "not built" list; their honest-value behaviour is
    # covered by tests/scenario/three_answers/test_three_answers_addons.py.)
    doc = _generate().document
    assert doc["remaining_floor_area"]["status"] == "not_available"
    assert doc["existing_building"]["status"] == "not_available"
    assert "not computed in this slice" in doc["existing_building"]["reason"]
    assert doc["geometry"]["setback_lines_per_level"]["status"] == "not_available"
    assert "not encoded in this slice" in doc["geometry"]["setback_lines_per_level"]["reason"]
    assert doc["lot_selection_statement"].startswith("Based on the lots you selected")
