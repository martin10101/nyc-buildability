"""A-04 / D-090-R107 step 2: minimum-base-height compliance note and the qualifying-housing
height triple, on the 215-16 Northern Blvd R6B benchmark.

The FAR-limited R6B sample building is 20 ft tall while the R6B table minimum base height is
30 ft. The sample is KEPT (on a reading of the captured Zoning Resolution text no provision
requires a building to rise to the minimum base height; raising the sample to a 30 ft street
wall would read in a requirement the text does not state - finding note
docs/research/zr-snapshots/notes/2026-10-04-r6b-minimum-base-height-20ft-sample.md); instead a
COMPUTED note records that reading. These tests pin:

  (a) when the built height is below the minimum base height, the building option carries one
      note citing ZR 23-431 / ZR 23-432 / ZR 23-433 and snapshots zr-23-431/432/433;
  (b) red/green: a building that reaches the minimum base height carries NO note - asserting the
      displaced note LIST, not a constant, so the test cannot pass on always-on or always-off code;
  (c) the qualifying-housing heights read as the 30 / 45 / 65 triple (shared 30 ft minimum base),
      beside the standard 30 / 45 / 55 triple, every height from the one ZR 23-432 lookup;
  (d) the results document still validates with the extra qualifying minimum-base-height value;
  (e) DB-119 gap CLOSED (D-090-R132): the computed note now reaches the results document's
      1.2.0 building-option notes slot - the note text and pinned snapshots appear in it
      (the fixture-equality and byte-identity pins live in test_three_answers_notes_emit);
  (f) the research finding note stays in the draft register (owner reviewer audit, D-090-R118):
      no "complies" / "misstate" / "non-compliant" assertion formulation reappears in it.

Expected values come from the benchmark fixture / the loaded rules, never restated (the
_benchmark_inputs / _expected pattern of test_three_answers_benchmark).
"""

from __future__ import annotations

import json
from pathlib import Path

from app.rules.registry import RuleRegistry
from app.scenario.three_answers import validate_results_document
from app.scenario.three_answers.answers import build_allowance, build_envelope
from app.scenario.three_answers.building_option import build_building_option
from app.scenario.three_answers.inputs import MEASUREMENT_ASSUMED

from .test_three_answers_benchmark import _benchmark_inputs, _expected, _generate, _value
from .test_three_answers_shortfall import _allowance, _envelope

_ON = {"LANE_A_ENABLED": "1"}


def _real_building_option(**overrides):
    """The building option built from the real Lane A rule registry on the benchmark inputs,
    plus the envelope it was computed against (for the minimum base height)."""
    inputs = _benchmark_inputs(**overrides)
    reg = RuleRegistry(env=_ON).load()
    measurement = inputs.site_measurement()
    allowance = build_allowance(inputs, reg, measurement)
    envelope = build_envelope(inputs, reg, measurement)
    option = build_building_option(inputs, allowance, envelope, MEASUREMENT_ASSUMED)
    return option, envelope


def test_sample_building_below_min_base_height_carries_compliance_note() -> None:
    option, envelope = _real_building_option()
    comp = option.computation
    assert comp is not None
    # The FAR-limited R6B sample is below the minimum base height (both read from the rules;
    # no golden restated here).
    assert comp.building_height_ft < envelope.min_base_height_ft

    notes = option.compliance_notes
    assert len(notes) == 1
    note = notes[0]
    assert note["zr_sections"] == ["ZR 23-431", "ZR 23-432", "ZR 23-433"]
    assert note["snapshot_ids"] == ["zr-23-431", "zr-23-432", "zr-23-433"]
    assert note["draft"] is True

    # Computed from the real numbers (C-11), not a template: the built height and both base
    # heights it was compared against.
    assert note["computed_from"] == ["building_height", "min_base_height", "max_base_height"]
    vals = {v["name"]: v["value"] for v in note["values"]}
    assert vals["building_height"] == comp.building_height_ft
    assert vals["min_base_height"] == envelope.min_base_height_ft
    assert vals["max_base_height"] == envelope.max_base_height_ft

    # Plain-English reading of the captured text. The note does NOT present the "whichever is
    # less" clause as THE operative R6B rule: it attributes that clause to ZR 23-431 (b)/(c) and
    # separately records that the R6B line-up rule (a) states no minimum height.
    text = note["text"]
    assert "minimum base height" in text and "maximum base height" in text
    assert "setback rule (ZR 23-432, ZR 23-433)" in text
    assert '(ZR 23-431 (b)/(c))' in text and 'whichever is less' in text
    assert "line-up rule (ZR 23-431 (a)) states no minimum height" in text
    # Draft register (O2): a reading of the captured text, not a compliance determination.
    lowered = text.lower()
    assert "draft reading of the captured text" in lowered
    assert "wait for qualified review" in lowered
    assert "complies" not in lowered and "misstate" not in lowered
    # The pinned snapshots are named in the note text as well as the structured field.
    for snapshot_id in ("zr-23-431", "zr-23-432", "zr-23-433"):
        assert snapshot_id in text


def test_compliance_note_absent_when_building_reaches_min_base_height() -> None:
    # Red/green through the SAME wiring, varying only the floor plate so the computed height
    # crosses the minimum base height. The note LIST is the displaced field (empty vs one note),
    # never a constant - reverting the height condition in the engine would break one side.
    inputs = _benchmark_inputs()
    env_full = _envelope(1.0)  # full-plate corner lot: a 2-floor, 20 ft building
    env_small = _envelope(0.2)  # a smaller plate forces >= 3 floors at 10 ft per floor
    min_base = env_full.min_base_height_ft

    below = build_building_option(inputs, _allowance(20150.0), env_full, MEASUREMENT_ASSUMED)
    assert below.computation.building_height_ft < min_base
    assert len(below.compliance_notes) == 1

    reaches = build_building_option(inputs, _allowance(20150.0), env_small, MEASUREMENT_ASSUMED)
    assert reaches.computation.floors_built >= 3
    assert reaches.computation.building_height_ft >= min_base
    # The displaced field itself: emptied when the street wall already meets the base.
    assert reaches.compliance_notes == ()
    assert below.compliance_notes != reaches.compliance_notes


def test_qualifying_heights_surface_as_the_30_45_65_triple() -> None:
    envelope = _generate().document["answers"]["permitted_envelope"]
    assert envelope["status"] == "available"

    std_min = _value(envelope, "min_base_height")
    std_max_base = _value(envelope, "max_base_height")
    std_max_bldg = _value(envelope, "max_building_height")
    q_min = _value(envelope, "min_base_height_qualifying_affordable_or_senior")
    q_max_base = _value(envelope, "max_base_height_qualifying_affordable_or_senior")
    q_max_bldg = _value(envelope, "max_building_height_qualifying_affordable_or_senior")

    # The minimum base height is the SAME column for both cases (shared 30 ft).
    assert q_min["value"] == std_min["value"] == _expected("min_base_height")
    # Standard triple 30 / 45 / 55.
    assert std_max_base["value"] == _expected("max_base_height")
    assert std_max_bldg["value"] == _expected("max_building_height")
    # Qualifying triple 30 / 45 / 65.
    assert q_max_base["value"] == _expected("max_base_height_qualifying_affordable_or_senior")
    assert q_max_bldg["value"] == _expected("max_building_height_qualifying_affordable_or_senior")

    # Every height - including the shared qualifying minimum - comes from the one ZR 23-432 lookup.
    for value in (std_min, std_max_base, std_max_bldg, q_min, q_max_base, q_max_bldg):
        assert value["zr_sections"] == ["ZR 23-432"]
        assert value["unit"] == "feet"


def test_results_document_still_validates_with_the_qualifying_min_base_value() -> None:
    # generate_results validates internally; re-validate explicitly to pin that the extra
    # qualifying minimum-base-height value keeps the document schema-valid.
    doc = _generate().document
    validate_results_document(doc)  # raises on any defect

    value = _value(
        doc["answers"]["permitted_envelope"], "min_base_height_qualifying_affordable_or_senior"
    )
    # A well-formed answer_value inside the closed envelope answer shape (no extra keys).
    assert set(value) == {
        "key",
        "label",
        "value",
        "unit",
        "zr_sections",
        "sources",
        "exception_label",
    }


def test_compliance_note_is_emitted_into_the_results_document() -> None:
    """DB-119 gap CLOSED (D-090-R132): the computed minimum-base-height note now reaches the
    results document's 1.2.0 building-option notes slot, shown beside the heights instead of
    being dropped before the document.

    The inverse of the former "dropped" pin (which this replaces per its own instruction to
    update when the Lane C results slot lands): the note travels on
    answers.building_option.notes, carrying the engine's computed text verbatim, and the
    computed text, a distinctive fragment and the pinned snapshot ids now appear in the
    serialized document. The fixture-equality and byte-identity pins live in
    test_three_answers_notes_emit.
    """
    # The engine computes a real note here (the 20 ft sample is below the 30 ft minimum base
    # height) - capture it so the presence assertions below are meaningful, not vacuous.
    option, _envelope = _real_building_option()
    assert len(option.compliance_notes) == 1
    note_text = option.compliance_notes[0]["text"]

    # The schema-validated document that generate_results returns carries the note in its slot.
    doc = _generate().document
    notes = doc["answers"]["building_option"]["notes"]
    assert len(notes) == 1
    assert notes[0]["text"] == note_text  # the engine's computed text, carried verbatim
    assert doc["contract_version"] == "1.2.0"  # a non-empty notes slot binds 1.2.0

    # The note reaches the serialized document too (the former pin asserted it was absent). A
    # distinctive fragment and the snapshot ids it cites are now present (quote-free fragments;
    # the full text is proved verbatim by the structured equality above).
    serialized = json.dumps(doc)
    assert "No captured provision requires the building to rise to it" in serialized
    assert "zr-23-431" in serialized


def test_research_finding_note_stays_in_the_draft_register() -> None:
    """The research finding note must read as a DRAFT reading of the captured text, never a
    compliance determination (owner reviewer audit, D-090-R118). This extends the production-note
    guard (above) to the finding note file: the flagged assertion formulations must not reappear,
    and the draft-register language the finding must keep is present.
    """
    note_path = (
        Path(__file__).resolve().parents[5]
        / "docs"
        / "research"
        / "zr-snapshots"
        / "notes"
        / "2026-10-04-r6b-minimum-base-height-20ft-sample.md"
    )
    lowered = note_path.read_text("utf-8").lower()
    assert "complies" not in lowered
    assert "misstate" not in lowered
    assert "non-compliant" not in lowered
    # The draft register the finding must keep.
    assert "a reading of the captured text" in lowered
    assert "does not establish the site's compliance" in lowered
