"""Unused-floor-area parity DATA stub (queue item B-11; plan section 11b). Pure, offline.

Lane B carries the sourced B-05 existing-floor-area INPUT and reports the unused-floor-area
output as "Not confirmed" (owner wording D-090-R038); it never computes a capacity.
"""

from __future__ import annotations

import pytest

from app.profile.existing_floor_area import (
    ExistingFloorAreaEvidence,
    ExistingFloorAreaResult,
    StatedAssumption,
    resolve_existing_zoning_floor_area,
)
from app.profile.parity.unused_floor_area import (
    NOT_CONFIRMED_LABEL,
    NOT_CONFIRMED_REASON,
    ROLE_NEIGHBOR,
    ROLE_SUBJECT,
    STATUS_NOT_CONFIRMED,
    neighbors_unused_floor_area_data,
    unused_floor_area_data,
)

SUBJECT_BBL = "4073340070"


def _known(bbl: str, value: int) -> ExistingFloorAreaResult:
    evidence = ExistingFloorAreaEvidence(
        assumption=StatedAssumption(
            value_sq_ft=value,
            statement="architect's stated assumption for the test",
            entered_at="2026-10-02T11:00:00Z",
        )
    )
    return resolve_existing_zoning_floor_area(bbl, evidence)


def _unknown(bbl: str) -> ExistingFloorAreaResult:
    return resolve_existing_zoning_floor_area(bbl, ExistingFloorAreaEvidence())


def test_owner_wording_is_exact():
    assert NOT_CONFIRMED_LABEL == "Remaining development capacity: Not confirmed"
    assert NOT_CONFIRMED_REASON == (
        "Needs verified zoning-lot boundaries and existing zoning floor area."
    )


def test_subject_with_known_existing_area_is_not_confirmed_but_carries_the_input():
    data = unused_floor_area_data(_known(SUBJECT_BBL, 20_000))
    assert data.role == ROLE_SUBJECT
    assert data.status == STATUS_NOT_CONFIRMED
    assert data.label == NOT_CONFIRMED_LABEL
    assert data.reason == NOT_CONFIRMED_REASON
    # No capacity number is ever produced here.
    assert not hasattr(data, "value")
    assert not hasattr(data, "unused_floor_area_sq_ft")
    # The sourced B-05 input is carried for the engine.
    inp = data.existing_floor_area_input
    assert inp["known"] is True
    assert inp["value_sq_ft"] == 20_000
    assert inp["unit"] == "square_feet"
    assert inp["measurement"]["rank"] == "assumed"
    assert "20,000 sq ft" in data.detail


def test_subject_without_existing_area_is_not_confirmed_and_names_the_missing_input():
    data = unused_floor_area_data(_unknown(SUBJECT_BBL))
    assert data.status == STATUS_NOT_CONFIRMED
    assert data.label == NOT_CONFIRMED_LABEL
    inp = data.existing_floor_area_input
    assert inp["known"] is False
    assert inp["value_sq_ft"] is None
    assert "not on file" in data.detail
    assert "never" in data.detail.lower()  # never from DOF building area


def test_neighbors_each_not_confirmed_carrying_their_own_input():
    neighbors = [_known("4073340001", 12_000), _unknown("4073340002")]
    out = neighbors_unused_floor_area_data(neighbors)
    assert len(out) == 2
    assert all(d.role == ROLE_NEIGHBOR for d in out)
    assert all(d.status == STATUS_NOT_CONFIRMED for d in out)
    assert out[0].lot_bbl == "4073340001"
    assert out[0].existing_floor_area_input["value_sq_ft"] == 12_000
    assert out[1].lot_bbl == "4073340002"
    assert out[1].existing_floor_area_input["known"] is False


def test_empty_neighbors_is_empty():
    assert neighbors_unused_floor_area_data([]) == ()


def test_missing_lot_bbl_is_refused():
    broken = ExistingFloorAreaResult(
        fact={"value": None}, basis="unknown", basis_label="Unknown — enter",
        reason="x", considered=(),
    )
    with pytest.raises(ValueError):
        unused_floor_area_data(broken)
