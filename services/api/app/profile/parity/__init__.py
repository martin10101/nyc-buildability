"""Competitive-parity DATA for plan section 11b (queue item B-11; Lane B).

Data only, never a capacity or a valuation (plan section 11b; owner standing rule
2026-10-01 / D-090-R038). Two slices so far:

- ``comparable_sales``: a disclosed selection of recorded DOF sales "of similar type and
  size" (the connector is ``app.connectors.dof_sales_soda``); never presented as a
  valuation.
- ``unused_floor_area``: the sourced existing-floor-area INPUT (from B-05) for the subject
  lot and for neighbours, with the unused-floor-area output reported "Not confirmed" - the
  allowance and the subtraction belong to the rule engine (Lane A), which is off.

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
from app.profile.parity.unused_floor_area import (
    UnusedFloorAreaData,
    neighbors_unused_floor_area_data,
    unused_floor_area_data,
)

__all__ = [
    "ComparableSalesResult",
    "SelectionCriteria",
    "SubjectSpec",
    "UnusedFloorAreaData",
    "neighbors_unused_floor_area_data",
    "select_comparables",
    "subject_spec_from_record",
    "unused_floor_area_data",
]
