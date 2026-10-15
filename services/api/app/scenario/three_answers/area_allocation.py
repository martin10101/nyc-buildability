"""The illustrative area allocation of a worked building - the pure split of its residential floor
area into apartment area and other area at one stated share (contract 1.5.0 $defs.area_allocation).

This is the SCENARIO layer and a self-contained module (it mirrors rear_yard_checks.py and
placement.py): no I/O, no clock, no AI, and it imports NOTHING from three_way_document.py,
geometry.py, first_option_results.py or envelope_constraints.py. It applies ONE stated share to the
building's residential floor area - the same measure the preliminary apartment estimate uses - and
splits a total into apartment area and other area, carrying the fixed conversion statement so the
plate is never read as a physical floor plate.

THREE RULES (result-deciding). (1) No default stands for a fact: a missing residential floor area
holds the allocation back (returns None, so the alternative carries no allocation); the share is a
STATED design assumption (the low end of the owner's 60-to-75-percent range), not a measurement,
and whether the allocation's zones draw inside a placed footprint follows the placement's status,
read by equality (``== "placed"``), never a truthiness test on an optional fact. (2) Apartment area
plus other area equals the total, and the per-storey figures sum to the plate; the share stays
within the contract's 0.60-0.75 bound or the builder fails closed. (3) The share is an assumption,
not a measurement; nothing is a count of apartments, a room, a core, a wall or a stair, and nothing
is called complies, buildable, optimal or feasible.

Every number here comes only from the stated residential floor area, the stated share and the
arithmetic below, never from a program run; the agreement of two independent AI readings is not
proof. The coverage lower bound (0.80 of the recorded lot area) is a DIFFERENT quantity on a
different basis that happens to share a numeral with the other-area total; this module never emits,
sums or equates it - that figure belongs to the lot-coverage reading, not here.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

__all__ = [
    "AREA_MEASURE",
    "ILLUSTRATIVE_LABEL",
    "PLATE_CONVERSION_STATEMENT",
    "SHARE_MAX",
    "SHARE_MIN",
    "STATED_APARTMENT_SHARE",
    "build_area_allocation",
    "per_storey_area",
]

# The contract-1.5.0 consts, byte-exact with results.schema.json (the same values placement.py
# carries); a test pins each against the schema so a reworded const is caught.
ILLUSTRATIVE_LABEL = "Illustrative"
AREA_MEASURE = "residential_floor_area"
PLATE_CONVERSION_STATEMENT = (
    "plate = zoning floor area per storey; no gross-up, exclusions or "
    "wall-thickness conversion worked"
)

# The one stated share: the low end of the owner's existing 60-to-75-percent apartment-area
# assumption (the preliminary estimate's share_low = 0.60; design contract R091). An assumption the
# owner can change, not a measurement. The schema bounds a share to 0.60-0.75.
STATED_APARTMENT_SHARE = 0.60
SHARE_MIN = 0.60
SHARE_MAX = 0.75


def _round2(value: float) -> float:
    """Round half up to two decimals (the reading's round_half_up_2dp), as a float."""
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def per_storey_area(total_sqft: float | None, storeys: int | None) -> float | None:
    """A total area divided evenly across the storeys, rounded half up to two decimals. A missing
    total or storey count holds the figure back (returns None); a non-positive storey count fails
    closed. The apartment and other per-storey figures from this helper sum to the plate."""
    if total_sqft is None or storeys is None:
        return None
    if storeys <= 0:
        raise ValueError(f"storeys must be positive, got {storeys!r}")
    return _round2(total_sqft / storeys)


def build_area_allocation(
    *,
    residential_floor_area_sqft: float | None,
    placement_status: str | None = None,
    share: float = STATED_APARTMENT_SHARE,
) -> dict | None:
    """Build an area_allocation dict (contract 1.5.0 $defs.area_allocation), or None.

    It applies ``share`` to the building's RESIDENTIAL FLOOR AREA and splits it into apartment area
    and other area (other = total - apartment, so apartment + other = total exactly), carrying the
    fixed label, the area measure and the conversion statement. ``fitted`` is True only when the
    building's placement is ``placed`` (so an allocation zones inside a footprint only when one is
    placed; the cross-key rule in results_way_rules.py enforces the same thing on the whole
    document). A missing residential floor area holds the allocation back (returns None); a share
    outside the contract's 0.60-0.75 bound fails closed. Emitted for every alternative that has a
    residential floor area, placed or not; the per-storey figures come from :func:`per_storey_area`.
    """
    if residential_floor_area_sqft is None:
        return None
    if not SHARE_MIN <= share <= SHARE_MAX:
        raise ValueError(
            f"a share must be within {SHARE_MIN}-{SHARE_MAX} (the contract bound), got {share!r}"
        )

    apartment_total = _round2(residential_floor_area_sqft * share)
    other_total = _round2(residential_floor_area_sqft - apartment_total)
    total = _round2(residential_floor_area_sqft)
    fitted = placement_status == "placed"

    return {
        "label": ILLUSTRATIVE_LABEL,
        "share": share,
        "measure": AREA_MEASURE,
        "conversion_statement": PLATE_CONVERSION_STATEMENT,
        "apartment_area_sqft": apartment_total,
        "other_area_sqft": other_total,
        "total_sqft": total,
        "fitted": fitted,
    }
