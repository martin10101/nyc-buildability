"""Results contract 1.2.0 building-option notes slot (Lane C, D-090-R132).

This PR adds the OPTIONAL additive ``notes`` array to the building-option
answer only, so the engine's COMPUTED minimum-base-height note can be carried
into the results document and shown beside the heights instead of being dropped
before the document (DB-119). This module validates the slot through the RUNTIME
path (``validate_results_document``, the byte-identical bundled schema) and pins:

- the valid notes fixture passes; every pre-slot valid fixture still passes
  (the slot is optional and additive, so 1.0.0 / 1.1.0 stay valid unchanged);
- notes is optional: absent, null or empty are all valid and leave the
  contract version unconstrained;
- a NON-EMPTY notes array binds contract_version to 1.2.0 (version binding,
  both directions);
- each invalid notes fixture is rejected BY THE SCHEMA, for exactly its stated
  one defect (draft false; notes present with 1.1.0), red/green;
- the note is never a legal determination: ``draft`` is const true, ``register``
  is the fixed draft-register string, ``kind`` is the closed enum, and the text
  carries no compliance ("complies" / "non-compliant" / "misstate") wording;
- the fixture's note TEXT equals the engine's computed note for the benchmark
  numbers, imported from the Lane A engine helper and never restated here (the
  helper rides on PR #388, held by the owner, D-090-R125; this one check skips
  until #388 merges and then proves the fixture carries the real engine text).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.contracts.study_contracts import (
    FIXTURE_ONLY_KEY,
    StudyContractError,
    validate_results_document,
)
from app.scenario.three_answers import compute_building_option

# The Lane A minimum-base-height note helper (PR #388, D-090-R107) is NOT on the
# candidate base yet (owner hold, D-090-R125). Import it when present so the
# note-text equality check runs the moment #388 merges; skip it otherwise.
try:  # pragma: no cover - exercised both ways across the #388 merge boundary
    from app.scenario.three_answers.building_option import (
        compliance_notes as _engine_compliance_notes,
    )
except ImportError:  # pragma: no cover
    _engine_compliance_notes = None

# services/api/tests/contracts/test_*.py -> parents[4] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
RESULTS_VALID = REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "results"
RESULTS_INVALID = REPO_ROOT / "packages" / "contracts" / "fixtures" / "invalid" / "results"
NOTES_VALID_FIXTURE = RESULTS_VALID / "synthetic_building_option_min_base_height_note_northern.json"

REGISTER_CONST = "draft reading of the captured text"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _note() -> dict:
    return _load(NOTES_VALID_FIXTURE)["answers"]["building_option"]["notes"][0]


# ---------------------------------------------------------------------------
# Positive: the valid notes fixture passes, and every pre-slot fixture still
# passes (the slot is optional and additive).
# ---------------------------------------------------------------------------


def test_valid_notes_fixture_validates() -> None:
    validate_results_document(_load(NOTES_VALID_FIXTURE))


@pytest.mark.parametrize(
    "fixture",
    sorted(RESULTS_VALID.glob("*.json")),
    ids=lambda p: p.name,
)
def test_every_valid_results_fixture_still_validates(fixture: Path) -> None:
    validate_results_document(_load(fixture))


def test_notes_absent_so_1_0_0_stays_valid() -> None:
    """A document with no notes key validates and may declare 1.0.0 (additive)."""
    doc = _load(NOTES_VALID_FIXTURE)
    doc["answers"]["building_option"].pop("notes")
    doc["contract_version"] = "1.0.0"
    validate_results_document(doc)


def test_notes_may_be_null() -> None:
    doc = _load(NOTES_VALID_FIXTURE)
    doc["answers"]["building_option"]["notes"] = None
    doc["contract_version"] = "1.0.0"
    validate_results_document(doc)


def test_empty_notes_array_leaves_version_unconstrained() -> None:
    """An EMPTY notes array carries no note, so it does not bind 1.2.0."""
    doc = _load(NOTES_VALID_FIXTURE)
    doc["answers"]["building_option"]["notes"] = []
    doc["contract_version"] = "1.1.0"
    validate_results_document(doc)


# ---------------------------------------------------------------------------
# Version binding: a NON-EMPTY notes array declares contract_version 1.2.0.
# ---------------------------------------------------------------------------


def test_non_empty_notes_requires_1_2_0() -> None:
    doc = _load(NOTES_VALID_FIXTURE)
    assert doc["contract_version"] == "1.2.0"
    assert doc["answers"]["building_option"]["notes"], "fixture must carry a note"
    for stale in ("1.0.0", "1.1.0"):
        doc["contract_version"] = stale
        with pytest.raises(StudyContractError):
            validate_results_document(doc)


# ---------------------------------------------------------------------------
# Negative: each invalid notes fixture is rejected, for its one stated defect.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture",
    sorted(RESULTS_INVALID.glob("notes_*.json")),
    ids=lambda p: p.name,
)
def test_invalid_notes_fixture_rejected(fixture: Path) -> None:
    instance = _load(fixture)
    assert FIXTURE_ONLY_KEY in instance, "invalid fixture must document its defect"
    instance.pop(FIXTURE_ONLY_KEY)
    with pytest.raises(StudyContractError):
        validate_results_document(instance)


def test_draft_false_is_the_only_defect() -> None:
    doc = _load(RESULTS_INVALID / "notes_draft_false.json")
    doc.pop(FIXTURE_ONLY_KEY)
    assert doc["answers"]["building_option"]["notes"][0]["draft"] is False
    with pytest.raises(StudyContractError):
        validate_results_document(doc)
    # Restoring ONLY draft=true makes the whole document valid -> draft is the
    # one and only defect (CODING_RULES: pin the displaced field).
    doc["answers"]["building_option"]["notes"][0]["draft"] = True
    validate_results_document(doc)


def test_notes_with_1_1_0_is_the_only_defect() -> None:
    doc = _load(RESULTS_INVALID / "notes_present_contract_1_1_0.json")
    doc.pop(FIXTURE_ONLY_KEY)
    assert doc["contract_version"] == "1.1.0"
    assert doc["answers"]["building_option"]["notes"], "fixture must carry a note"
    with pytest.raises(StudyContractError):
        validate_results_document(doc)
    # Fixing ONLY the version to 1.2.0 makes the whole document valid.
    doc["contract_version"] = "1.2.0"
    validate_results_document(doc)


# ---------------------------------------------------------------------------
# The note is a DRAFT reading, never a legal determination (the not-free guard).
# ---------------------------------------------------------------------------


def test_note_draft_is_const_true() -> None:
    note = _note()
    assert note["draft"] is True
    doc = _load(NOTES_VALID_FIXTURE)
    doc["answers"]["building_option"]["notes"][0]["draft"] = True  # const true accepted
    validate_results_document(doc)
    doc["answers"]["building_option"]["notes"][0]["draft"] = False  # false refused
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


def test_note_register_const_byte_exact() -> None:
    assert _note()["register"] == REGISTER_CONST
    doc = _load(NOTES_VALID_FIXTURE)
    doc["answers"]["building_option"]["notes"][0]["register"] = "reviewed reading"
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


def test_note_kind_is_a_closed_enum() -> None:
    assert _note()["kind"] == "minimum_base_height"
    doc = _load(NOTES_VALID_FIXTURE)
    doc["answers"]["building_option"]["notes"][0]["kind"] = "maximum_base_height"
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


def test_note_text_carries_no_compliance_determination() -> None:
    """D-090-R118: a draft reading never asserts compliance."""
    lowered = _note()["text"].lower()
    assert "complies" not in lowered
    assert "non-compliant" not in lowered
    assert "misstate" not in lowered
    assert "draft reading of the captured text" in lowered
    assert "wait for qualified review" in lowered


# ---------------------------------------------------------------------------
# The fixture's note TEXT equals the engine's computed note (never restated).
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    _engine_compliance_notes is None,
    reason="Lane A compliance_notes() helper rides on PR #388 (owner hold D-090-R125); "
    "this equality check activates automatically once #388 merges into candidate.",
)
def test_fixture_note_text_equals_engine_computed_note() -> None:
    """The fixture carries the REAL engine note, not hand-typed prose. Rebuild the
    benchmark building option from the fixture's own numbers via the engine's pure
    computation, call the Lane A note helper, and assert the fixture TEXT and values
    equal what the engine computed (import the helper; never restate the text)."""
    doc = _load(NOTES_VALID_FIXTURE)
    option = doc["answers"]["building_option"]
    values = {v["key"]: v["value"] for v in option["values"]}
    envelope = {v["key"]: v["value"] for v in doc["answers"]["permitted_envelope"]["values"]}
    ftf = doc["floor_by_floor"][0]["height_ft"]

    comp = compute_building_option(
        allowance_sf=values["achieved_zoning_floor_area"],
        plate_sf=values["floor_plate_area"],
        max_building_height_ft=envelope["max_building_height"],
        floor_to_floor_ft=ftf,
    )
    assert comp is not None
    engine_notes = _engine_compliance_notes(
        comp, envelope["min_base_height"], envelope["max_base_height"]
    )
    assert len(engine_notes) == 1
    engine_note = engine_notes[0]

    fixture_note = option["notes"][0]
    assert fixture_note["text"] == engine_note["text"]
    # The slot reshapes the engine note's values ARRAY into an object keyed by name;
    # the numbers must be the same ones the engine computed.
    assert fixture_note["values"] == {v["name"]: v["value"] for v in engine_note["values"]}
    assert fixture_note["computed_from"] == list(engine_note["computed_from"])
    assert fixture_note["zr_sections"] == list(engine_note["zr_sections"])
    assert fixture_note["snapshot_ids"] == list(engine_note["snapshot_ids"])
