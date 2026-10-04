"""Results contract 1.1.0 scope slot (Lane C, D-090-R108).

PR 1 of 4 adds the OPTIONAL top-level ``scope`` object to the results contract
so the headline cards and exported drawings can put the scope beside the
numbers: the "Tax-lot-only estimate" label, the identified lot, the disclosed
assumed corner conditions, and the unconfirmed whole-site / not-confirmed
remaining-capacity statements. This module validates the slot through the
RUNTIME path (``validate_results_document``, the byte-identical bundled
schema) and pins the settled strings so a future fixture or reword cannot
quietly change them:

- the valid scope fixture passes; every pre-slot valid fixture still passes
  (the slot is optional and additive, so 1.0.0 stays valid unchanged);
- each invalid scope fixture is rejected BY THE SCHEMA once its fixture-only
  ``_expected_failure`` annotation is stripped, for exactly its stated defect;
- a non-null scope binds contract_version to 1.1.0 (version binding);
- the two owner-settled strings and the label const are byte-exact, and their
  documented relationship to the engine constants is pinned (D-090-R108: the
  remaining-capacity LABEL carries a final period the engine's display
  constant does not; the two were not reconciled here).
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
from app.scenario.constants import UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT
from app.scenario.three_answers.engine import (
    LOT_SELECTION_STATEMENT,
    REMAINING_NOT_CONFIRMED_REASON,
)

# services/api/tests/contracts/test_*.py -> parents[4] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
RESULTS_VALID = REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "results"
RESULTS_INVALID = REPO_ROOT / "packages" / "contracts" / "fixtures" / "invalid" / "results"
SCOPE_VALID_FIXTURE = RESULTS_VALID / "synthetic_scope_tax_lot_only_northern.json"

SCOPE_LABEL = "Tax-lot-only estimate"
REMAINING_LABEL = "Remaining development capacity: Not confirmed."


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _scope() -> dict:
    return _load(SCOPE_VALID_FIXTURE)["scope"]


# ---------------------------------------------------------------------------
# Positive: the valid scope fixture passes, and every pre-slot fixture still
# passes (the slot is optional and additive).
# ---------------------------------------------------------------------------


def test_valid_scope_fixture_validates() -> None:
    validate_results_document(_load(SCOPE_VALID_FIXTURE))


@pytest.mark.parametrize(
    "fixture",
    sorted(RESULTS_VALID.glob("*.json")),
    ids=lambda p: p.name,
)
def test_every_valid_results_fixture_still_validates(fixture: Path) -> None:
    validate_results_document(_load(fixture))


def test_scope_is_optional_so_1_0_0_stays_valid() -> None:
    """A document with no scope key validates and may declare 1.0.0."""
    doc = _load(SCOPE_VALID_FIXTURE)
    doc.pop("scope")
    doc["contract_version"] = "1.0.0"
    validate_results_document(doc)


def test_scope_may_be_null() -> None:
    doc = _load(SCOPE_VALID_FIXTURE)
    doc["scope"] = None
    doc["contract_version"] = "1.0.0"
    validate_results_document(doc)


# ---------------------------------------------------------------------------
# Negative: each invalid scope fixture is rejected, for its stated defect.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture",
    sorted(RESULTS_INVALID.glob("scope_*.json")),
    ids=lambda p: p.name,
)
def test_invalid_scope_fixture_rejected(fixture: Path) -> None:
    instance = _load(fixture)
    assert FIXTURE_ONLY_KEY in instance, "invalid fixture must document its defect"
    # Strip the fixture-only annotation so the document fails for its real
    # schema defect, not for carrying the annotation.
    instance.pop(FIXTURE_ONLY_KEY)
    with pytest.raises(StudyContractError):
        validate_results_document(instance)


def test_wrong_scope_label_is_the_only_defect() -> None:
    doc = _load(RESULTS_INVALID / "scope_label_wrong.json")
    doc.pop(FIXTURE_ONLY_KEY)
    with pytest.raises(StudyContractError):
        validate_results_document(doc)
    # Fixing ONLY the label makes the whole document valid -> the label is the
    # one and only defect (CODING_RULES: pin the displaced field).
    doc["scope"]["label"] = SCOPE_LABEL
    validate_results_document(doc)


def test_remaining_label_missing_period_is_the_only_defect() -> None:
    doc = _load(RESULTS_INVALID / "scope_remaining_capacity_label_no_period.json")
    doc.pop(FIXTURE_ONLY_KEY)
    assert doc["scope"]["remaining_capacity"]["label"] == REMAINING_LABEL[:-1]
    with pytest.raises(StudyContractError):
        validate_results_document(doc)
    doc["scope"]["remaining_capacity"]["label"] = REMAINING_LABEL
    validate_results_document(doc)


# ---------------------------------------------------------------------------
# Version binding: a non-null scope declares contract_version 1.1.0.
# ---------------------------------------------------------------------------


def test_non_null_scope_requires_1_1_0() -> None:
    doc = _load(SCOPE_VALID_FIXTURE)
    assert doc["contract_version"] == "1.1.0"
    doc["contract_version"] = "1.0.0"
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


# ---------------------------------------------------------------------------
# Settled strings pinned byte-exact, with the documented engine relationship.
# ---------------------------------------------------------------------------


def test_scope_label_and_basis_byte_exact() -> None:
    scope = _scope()
    assert scope["basis"] == "tax_lot_only"
    assert scope["label"] == SCOPE_LABEL


def test_whole_site_statement_equals_lot_selection_statement() -> None:
    scope = _scope()
    assert scope["whole_site"]["status"] == "unconfirmed"
    assert scope["whole_site"]["statement"] == LOT_SELECTION_STATEMENT


def test_remaining_capacity_strings_byte_exact() -> None:
    rc = _scope()["remaining_capacity"]
    assert rc["status"] == "not_confirmed"
    assert rc["label"] == REMAINING_LABEL
    # The reason matches the engine constant exactly (both carry the period).
    assert rc["reason"] == REMAINING_NOT_CONFIRMED_REASON


def test_remaining_label_differs_from_engine_display_constant_by_period() -> None:
    """D-090-R108 byte-difference, pinned: the owner-settled remaining-capacity
    LABEL carries a final period that the engine's display constant does not;
    neither side was changed here. If a future change reconciles them, this
    test fails loudly so the reconciliation is deliberate, not silent."""
    rc_label = _scope()["remaining_capacity"]["label"]
    assert rc_label != UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT
    assert rc_label == UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT + "."


def test_lot_identity_and_assumptions_present() -> None:
    scope = _scope()
    lot = scope["lot"]
    assert lot["bbl"] == "4073340070"
    assert (lot["borough"], lot["block"], lot["lot"]) == ("Queens", "7334", "70")
    assert lot["display"] == "Queens block 7334, lot 70"
    # The assumed corner conditions are disclosed, each with a plain statement.
    keys = {a["key"] for a in scope["assumptions"]}
    assert "lot_type" in keys
    assert all(a["statement"].strip() for a in scope["assumptions"])
    lot_type = next(a for a in scope["assumptions"] if a["key"] == "lot_type")
    assert lot_type["value"] == "corner"
