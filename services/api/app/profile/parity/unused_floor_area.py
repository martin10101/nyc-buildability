"""Unused-floor-area parity DATA (queue item B-11, plan section 11b "Unused floor area on
the lot"; and neighbours' unused floor area, section 6 Group C; Lane B).

Lane B provides DATA, never a capacity. The amount of floor area still available on a lot
("air rights remaining") is the zoning floor-area allowance (FAR x lot area, plus any
add-ons) MINUS the existing zoning floor area - an allowance and a subtraction that belong
to the rule engine (Lane A), which is OFF. Even with the engine on, the owner's standing
rule (2026-10-01; D-090-R038) is that remaining development capacity and whole-site
capacity read "Not confirmed" until the zoning lot and the existing zoning floor area are
verified, and the zoning-math switch stays off.

So this module computes nothing. For the subject lot and for each neighbour it:

- carries the SOURCED INPUT Lane B can supply - the existing zoning floor area from
  ``app.profile.existing_floor_area`` (queue item B-05: a DOB filing, a certificate of
  occupancy, or a stated assumption; never DOF/PLUTO building area), with its value, unit,
  measurement rank and source; and
- reports the unused-floor-area OUTPUT as "Not confirmed" with the owner-settled reason,
  never a number and never an estimate.

The computed section (when the engine is eventually turned on and verified) lives in
``app.scenario.unused_floor_area`` (Lane A), which this module never calls or duplicates.

Pure, deterministic code: no I/O, no legal logic, no calculation. The inputs are read,
never changed.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.profile.existing_floor_area import ExistingFloorAreaResult

__all__ = [
    "NOT_CONFIRMED_LABEL",
    "NOT_CONFIRMED_REASON",
    "ROLE_NEIGHBOR",
    "ROLE_SUBJECT",
    "STATUS_NOT_CONFIRMED",
    "UnusedFloorAreaData",
    "neighbors_unused_floor_area_data",
    "unused_floor_area_data",
]

STATUS_NOT_CONFIRMED = "not_confirmed"
ROLE_SUBJECT = "subject"
ROLE_NEIGHBOR = "neighbor"

# Owner-settled wording (owner, 2026-10-01; D-090-R038). The two lines appear verbatim on
# every remaining-capacity surface and in the results contract
# (packages/contracts/schemas/v1/results.schema.json). Copied here so the DATA layer reads
# identically to the engine; a test pins both strings.
NOT_CONFIRMED_LABEL = "Remaining development capacity: Not confirmed"
NOT_CONFIRMED_REASON = "Needs verified zoning-lot boundaries and existing zoning floor area."

# Why there is no number here, stated once (plan section 5a: disclosure, not clutter).
_ENGINE_NOTE = (
    "Unused floor area is the zoning floor-area allowance minus the existing zoning floor "
    "area. The allowance and the subtraction are the rule engine's (Lane A), which is off; "
    "this data layer supplies only the existing-floor-area input and never computes a "
    "remaining capacity."
)


@dataclass(frozen=True)
class UnusedFloorAreaData:
    """The unused-floor-area parity data for one lot (the subject or a neighbour).

    Attributes:
        lot_bbl: the tax lot (10-digit BBL).
        role: ``subject`` or ``neighbor``.
        status: always ``not_confirmed`` - this layer never confirms a capacity.
        label: the owner-settled line 1 (:data:`NOT_CONFIRMED_LABEL`).
        reason: the owner-settled line 2 (:data:`NOT_CONFIRMED_REASON`).
        existing_floor_area_input: the SOURCED B-05 input carried for the engine - the
            site_fact ``{value, unit, measurement, source, note}`` plus ``basis`` /
            ``basis_label`` and whether it is known. When the input is unknown it says so
            (value null); the input is never invented.
        detail: the one line shown beside the lot (plan section 5a), stating why there is
            no number and what input is carried.
    """

    lot_bbl: str
    role: str
    status: str
    label: str
    reason: str
    existing_floor_area_input: dict
    detail: str

    def to_dict(self) -> dict:
        return {
            "lot_bbl": self.lot_bbl,
            "role": self.role,
            "status": self.status,
            "label": self.label,
            "reason": self.reason,
            "existing_floor_area_input": self.existing_floor_area_input,
            "detail": self.detail,
        }


def _existing_input(existing: ExistingFloorAreaResult) -> dict:
    """The sourced existing-floor-area input, read from the B-05 result (never computed)."""
    fact = existing.fact
    known = fact.get("value") is not None
    return {
        "known": known,
        "value_sq_ft": fact.get("value"),
        "unit": fact.get("unit"),
        "measurement": fact.get("measurement"),
        "source": fact.get("source"),
        "basis": existing.basis,
        "basis_label": existing.basis_label,
        "note": fact.get("note"),
    }


def _data(existing: ExistingFloorAreaResult, *, role: str) -> UnusedFloorAreaData:
    bbl = existing.fact.get("lot_bbl")
    if not isinstance(bbl, str) or not bbl.strip():
        raise ValueError("the existing-floor-area result has no lot_bbl")
    existing_input = _existing_input(existing)
    if existing_input["known"]:
        input_clause = (
            f"Existing zoning floor area on file: {existing_input['value_sq_ft']:,} sq ft "
            f"({existing.basis_label}). "
        )
    else:
        input_clause = (
            "Existing zoning floor area is not on file (it is needed from a Buildings "
            "Department filing, a certificate of occupancy, or a stated assumption; never "
            "from DOF building area). "
        )
    detail = f"{NOT_CONFIRMED_LABEL}. {NOT_CONFIRMED_REASON} {input_clause}{_ENGINE_NOTE}"
    return UnusedFloorAreaData(
        lot_bbl=bbl,
        role=role,
        status=STATUS_NOT_CONFIRMED,
        label=NOT_CONFIRMED_LABEL,
        reason=NOT_CONFIRMED_REASON,
        existing_floor_area_input=existing_input,
        detail=detail,
    )


def unused_floor_area_data(existing: ExistingFloorAreaResult) -> UnusedFloorAreaData:
    """The subject lot's unused-floor-area parity data.

    ``existing`` is the B-05 existing-floor-area result for the subject lot. The output is
    always ``not_confirmed`` (this layer never computes a capacity); the sourced existing
    floor area is carried as the input for the engine.

    Raises:
        ValueError: the result has no ``lot_bbl``.
    """
    return _data(existing, role=ROLE_SUBJECT)


def neighbors_unused_floor_area_data(
    neighbors: Sequence[ExistingFloorAreaResult],
) -> tuple[UnusedFloorAreaData, ...]:
    """Each neighbour's unused-floor-area parity data (plan section 6 Group C: a neighbour's
    unused floor area is an estimate that depends on an agreement; never in Best
    combination). The same rule applies: ``not_confirmed`` for every neighbour, carrying
    each neighbour's sourced existing-floor-area input. One entry per supplied neighbour,
    in order.

    Raises:
        ValueError: a neighbour result has no ``lot_bbl``.
    """
    return tuple(_data(existing, role=ROLE_NEIGHBOR) for existing in neighbors)
