"""Results contract scope + notes version binding (Lane C, D-090-R132/R137; DB-129).

The results contract has two version-binding ``allOf`` clauses. Before the
widening the SCOPE clause pinned a non-null ``scope`` to const ``1.1.0`` while
the NOTES clause pins a non-empty building-option ``notes`` array to const
``1.2.0``. A document carrying BOTH was therefore unsatisfiable: no single
``contract_version`` could satisfy both clauses, yet the scope emitter (PR #405)
and the notes emitter (PR #388) both fire on the R6B 215-16 Northern path.

D-090-R132/R137 widens the scope clause to the enum ``["1.1.0", "1.2.0"]`` -
1.2.0 is a strict superset of 1.1.0 (scope allowed AND notes allowed) - so a
scope-plus-notes document is valid at 1.2.0, while the notes clause is unchanged
(a non-empty notes array still binds const 1.2.0) and every earlier document
stays valid. These tests run the RUNTIME validator the engine uses
(``validate_results_document``, the byte-identical bundled schema).
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

# services/api/tests/contracts/test_*.py -> parents[4] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
RESULTS_VALID = REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "results"
RESULTS_INVALID = REPO_ROOT / "packages" / "contracts" / "fixtures" / "invalid" / "results"
SCOPE_AND_NOTES_VALID = RESULTS_VALID / "synthetic_scope_and_notes_contract_1_2_0.json"
SCOPE_ONLY_VALID = RESULTS_VALID / "synthetic_scope_tax_lot_only_northern.json"
SCOPE_AND_NOTES_INVALID = RESULTS_INVALID / "scope_and_notes_contract_1_1_0.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _has_scope(doc: dict) -> bool:
    return doc.get("scope") is not None


def _has_notes(doc: dict) -> bool:
    return bool(doc["answers"]["building_option"].get("notes"))


# ---------------------------------------------------------------------------
# (i) scope + notes TOGETHER validate at 1.2.0 (the DB-129 defect is fixed).
# ---------------------------------------------------------------------------


def test_scope_and_notes_validate_at_1_2_0() -> None:
    doc = _load(SCOPE_AND_NOTES_VALID)
    assert doc["contract_version"] == "1.2.0"
    assert _has_scope(doc) and _has_notes(doc), "fixture must carry BOTH a scope and a note"
    validate_results_document(doc)


# ---------------------------------------------------------------------------
# (ii) the SAME document at 1.1.0 fails, and the NOTES binding is the one defect.
# ---------------------------------------------------------------------------


def test_scope_and_notes_at_1_1_0_fails_on_the_notes_binding_only() -> None:
    doc = _load(SCOPE_AND_NOTES_VALID)
    doc["contract_version"] = "1.1.0"
    with pytest.raises(StudyContractError):
        validate_results_document(doc)
    # Emptying the notes (keeping the non-null scope) makes it valid at 1.1.0:
    # the widened scope clause accepts 1.1.0, so the notes binding was the one
    # and only defect (CODING_RULES: pin the displaced field).
    doc["answers"]["building_option"]["notes"] = []
    validate_results_document(doc)


# ---------------------------------------------------------------------------
# (iii) scope-only at 1.2.0 validates (the widened enum admits a scope at 1.2.0).
# ---------------------------------------------------------------------------


def test_scope_only_validates_at_1_2_0() -> None:
    doc = _load(SCOPE_AND_NOTES_VALID)
    doc["answers"]["building_option"].pop("notes")
    assert _has_scope(doc) and not _has_notes(doc)
    validate_results_document(doc)
    # The committed scope-only fixture (declared 1.1.0) also validates at 1.2.0.
    scope_only = _load(SCOPE_ONLY_VALID)
    assert scope_only["contract_version"] == "1.1.0" and _has_scope(scope_only)
    scope_only["contract_version"] = "1.2.0"
    validate_results_document(scope_only)


# ---------------------------------------------------------------------------
# (iv) scope-only at 1.0.0 still fails (a non-null scope never admits 1.0.0).
# ---------------------------------------------------------------------------


def test_scope_only_at_1_0_0_still_fails() -> None:
    doc = _load(SCOPE_AND_NOTES_VALID)
    doc["answers"]["building_option"].pop("notes")
    doc["contract_version"] = "1.0.0"
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


# ---------------------------------------------------------------------------
# The committed invalid fixture fails for its one stated defect (notes binding),
# and fixing ONLY the version to 1.2.0 makes the whole document valid.
# ---------------------------------------------------------------------------


def test_invalid_scope_and_notes_fixture_rejected_then_fixed_by_version_only() -> None:
    doc = _load(SCOPE_AND_NOTES_INVALID)
    assert FIXTURE_ONLY_KEY in doc, "invalid fixture must document its defect"
    doc.pop(FIXTURE_ONLY_KEY)
    assert doc["contract_version"] == "1.1.0"
    assert _has_scope(doc) and _has_notes(doc)
    with pytest.raises(StudyContractError):
        validate_results_document(doc)
    doc["contract_version"] = "1.2.0"
    validate_results_document(doc)
