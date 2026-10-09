"""A-04 / D-090-R132: the engine emits the COMPUTED minimum-base-height note into the results
document's 1.2.0 building-option ``notes`` slot (DB-119 gap closed).

``generate_results`` now carries ``BuildingOptionResult.compliance_notes`` into
``answers.building_option.notes`` mapped to the contract's ``building_option_note`` shape, and
declares ``contract_version`` 1.2.0 when the slot is non-empty. These tests pin:

  (a) the R6B 215-16 Northern benchmark (the case the note fires on) emits a notes slot that
      EQUALS the committed Northern fixture's ``notes`` (loaded from the fixture file, never
      re-typed), declares 1.2.0, and the document validates against the schema;
  (b) a case with no computed note carries no notes slot and the pre-change 1.0.0 version, and
      is byte-identical to today's output - the emitter is purely additive (stripping the slot
      and the version bump from the with-note document reproduces the no-note document exactly);
  (c) mutation proof: reverting the emitter (the mapping returns []) drops the slot and the
      1.2.0 version, so (a) cannot pass on dead code.

Requirement d (contract): if the fixture's note disagrees in any field with what the engine
computes, (a) fails loudly here - the fixture is NOT edited to match.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.scenario.three_answers import validate_results_document

from .test_three_answers_benchmark import _generate

# services/api/tests/scenario/three_answers/ -> parents[5] is the repo root.
_FIXTURE = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
    / "synthetic_building_option_min_base_height_note_northern.json"
)

# compliance_notes is called by build_building_option under this name; patch it there.
_COMPLIANCE_NOTES = "app.scenario.three_answers.building_option.compliance_notes"
# The engine imports the mapper into its own namespace; patch it there.
_ENGINE_MAPPER = "app.scenario.three_answers.engine.map_building_option_notes"


def _fixture_notes() -> list[dict]:
    doc = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    return doc["answers"]["building_option"]["notes"]


def test_r6b_sample_emits_the_fixture_note_and_binds_1_2_0() -> None:
    doc = _generate().document
    option = doc["answers"]["building_option"]
    # The emitted notes slot equals the committed fixture's notes, field for field (requirement
    # d: a disagreement fails here; the fixture is not edited to match).
    assert option["notes"] == _fixture_notes()
    assert doc["contract_version"] == "1.2.0"
    # The non-empty slot keeps the document schema-valid (generate_results validated it; this
    # re-validates explicitly as a belt).
    validate_results_document(doc)


def test_no_note_case_is_byte_identical_to_the_pre_change_output(monkeypatch) -> None:
    with_note = _generate().document
    assert with_note["answers"]["building_option"].get("notes")  # the R6B note is present
    assert with_note["contract_version"] == "1.2.0"

    # Drive the no-note case: the engine computes no note (as when the built street wall already
    # reaches the minimum base height). The output must then match today's 1.0.0 document.
    monkeypatch.setattr(_COMPLIANCE_NOTES, lambda *args, **kwargs: ())
    noteless = _generate().document
    assert "notes" not in noteless["answers"]["building_option"]
    # The benchmark inputs carry scope_inputs (#405), so the noteless document is the 1.1.0
    # scope-only shape; without a scope it would be 1.0.0. The note raises either to 1.2.0.
    scope_only_version = "1.1.0" if "scope" in noteless else "1.0.0"
    assert noteless["contract_version"] == scope_only_version

    # Byte-identity: the ONLY change the emitter makes is the additive slot plus the version.
    stripped = json.loads(json.dumps(with_note))
    del stripped["answers"]["building_option"]["notes"]
    stripped["contract_version"] = scope_only_version
    assert json.dumps(stripped, sort_keys=True) == json.dumps(noteless, sort_keys=True)


def test_mutation_reverting_the_emitter_drops_the_notes_slot(monkeypatch) -> None:
    # Red/green: revert the emitter (the mapping returns []). The document then carries no notes
    # slot and the 1.0.0 version, so test (a)'s fixture-equality and 1.2.0 assertions cannot
    # pass on dead code.
    monkeypatch.setattr(_ENGINE_MAPPER, lambda notes: [])
    doc = _generate().document
    assert "notes" not in doc["answers"]["building_option"]
    assert doc["contract_version"] == ("1.1.0" if "scope" in doc else "1.0.0")
