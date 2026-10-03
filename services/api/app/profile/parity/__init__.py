"""Competitive-parity DATA for plan section 11b (queue item B-11; Lane B).

Data only, never a capacity or a valuation (plan section 11b; owner standing rule
2026-10-01 / D-090-R038). Two slices so far:

- ``comparable_sales``: a disclosed selection of recorded DOF sales "of similar type and
  size" (the connector is ``app.connectors.dof_sales_soda``); never presented as a
  valuation.
- ``unused_floor_area``: the sourced existing-floor-area INPUT (from B-05) for the subject
  lot and for neighbours, with the unused-floor-area output reported "Not confirmed" - the
  allowance and the subtraction belong to the rule engine (Lane A), which is off.
- ``neighbor_floor_area`` (B-11 slice 2): captures each neighbour's existing zoning floor
  area through the B-05 source order (certificate > DOB filing > stated assumption; never
  DOF/PLUTO building area) and wires the captured inputs into the ``unused_floor_area``
  carriage. The neighbour set is a documented method (touching lots per B-07 geometry).

Still to come under B-11: 485-x tax-incentive source pointers (eligibility is a legal
interpretation - research pointers and an owner question only, never encoded here).
"""

from app.profile.parity.comparable_sales import (
    ComparableSalesResult,
    SelectionCriteria,
    SubjectSpec,
    select_comparables,
    subject_spec_from_record,
)
from app.profile.parity.neighbor_floor_area import (
    NEIGHBOR_SET_METHOD,
    NeighborEvidence,
    NeighborFloorAreaCapture,
    NeighborFloorAreaCaptureSet,
    capture_neighbor_floor_area,
    capture_neighbors,
    neighbor_parity_data,
)
from app.profile.parity.unused_floor_area import (
    UnusedFloorAreaData,
    neighbors_unused_floor_area_data,
    unused_floor_area_data,
)

__all__ = [
    "NEIGHBOR_SET_METHOD",
    "ComparableSalesResult",
    "NeighborEvidence",
    "NeighborFloorAreaCapture",
    "NeighborFloorAreaCaptureSet",
    "SelectionCriteria",
    "SubjectSpec",
    "UnusedFloorAreaData",
    "capture_neighbor_floor_area",
    "capture_neighbors",
    "neighbor_parity_data",
    "neighbors_unused_floor_area_data",
    "select_comparables",
    "subject_spec_from_record",
    "unused_floor_area_data",
]
