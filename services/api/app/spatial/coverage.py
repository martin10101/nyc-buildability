"""Per-family coverage audit (owner packet amendment 2026-07-20, invariants).

The invariants this module enforces, verbatim intent:

1. Coverage, gaps, overlaps, and shares are computed WITHIN an explicit source
   layer / feature family, never across families.
2. Cross-family overlap is NOT a topology defect (a base district and a special
   district may legitimately cover the same area) - so this module only ever
   receives one family at a time.
3. Absence of an overlay / special district is NOT "unassigned area".
4. ``unassigned_area`` is emitted ONLY for a family whose declared coverage
   expectation says the area should be covered AND a gap is actually found.
5. ``overlap_area`` is emitted ONLY for unexpected SAME-family overlap.
6. The audit status is INTERNAL (unknown / complete_nonoverlapping /
   gaps_detected / overlaps_detected / not_applicable) and is NOT a published
   profile-contract field.
7. Point shares are never forced to 100%; nothing is renormalized.

Only ``base_zoning`` carries ``expected_full_coverage`` (every lot has a base
zoning district); for every other family the absence of a feature is expected.
"""

from __future__ import annotations

from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from .models import (
    AUDIT_COMPLETE_NONOVERLAPPING,
    AUDIT_GAPS_DETECTED,
    AUDIT_NOT_APPLICABLE,
    AUDIT_OVERLAPS_DETECTED,
    AUDIT_UNKNOWN,
    CoverageAudit,
)
from .policy import AREA_EPSILON_SQ_FT, FAMILY_COVERAGE_EXPECTATION

_AREA_DECIMALS = 4


def audit_family(
    lot_shape: BaseGeometry,
    lot_area_sq_ft: float,
    family: str,
    district_shapes: list[BaseGeometry],
) -> CoverageAudit:
    """Audit one family's coverage of the lot. ``district_shapes`` are the
    shapely polygons of every fetched feature IN THIS FAMILY only."""
    expectation = FAMILY_COVERAGE_EXPECTATION.get(family, "selective_no_gap_expectation")
    expects_full = expectation == "expected_full_coverage"
    count = len(district_shapes)

    if count == 0:
        # No feature of this family intersects the lot. For a selective family
        # that is the normal case (not_applicable). For base zoning we cannot
        # confirm coverage from an empty set - stay ``unknown`` (never fabricate
        # a full-lot gap, which might just be an un-fetched feature).
        status = AUDIT_UNKNOWN if expects_full else AUDIT_NOT_APPLICABLE
        note = (
            "no base-zoning feature provided; coverage undeterminable (not "
            "asserting a gap from an empty set)"
            if expects_full
            else "family has no feature over this lot; absence is expected, not a gap"
        )
        return CoverageAudit(
            family=family,
            status=status,
            coverage_expectation=expectation,
            unassigned_area_sq_ft=None,
            overlap_area_sq_ft=None,
            district_count=0,
            notes=[note],
        )

    # Clip every same-family polygon to the lot (raw, no band) and measure.
    clipped = [d.intersection(lot_shape) for d in district_shapes]
    clipped_areas = [float(c.area) for c in clipped]
    sum_clipped = sum(clipped_areas)
    union = unary_union(clipped)
    covered_area = float(union.area)

    # Same-family overlap: total clipped area minus the (deduplicated) union.
    overlap_area = max(sum_clipped - covered_area, 0.0)
    gap_area = max(float(lot_area_sq_ft) - covered_area, 0.0)

    notes: list = []
    unassigned: float | None = None
    overlap: float | None = None

    # Compute the two quantities INDEPENDENTLY so a simultaneous same-family
    # overlap AND coverage gap both stay explicit - one never suppresses the
    # other (G3 obs 1). ``unassigned`` is emitted only for a family expected to
    # fully cover the lot (invariant 4); ``overlap`` for any same-family overlap.
    has_overlap = overlap_area > AREA_EPSILON_SQ_FT
    has_gap = expects_full and gap_area > AREA_EPSILON_SQ_FT
    if has_overlap:
        overlap = round(overlap_area, _AREA_DECIMALS)
        notes.append("same-family polygon overlap on the lot (not cross-family stacking)")
    if has_gap:
        unassigned = round(gap_area, _AREA_DECIMALS)
        notes.append("base-zoning coverage gap on the lot; area left explicit, never renormalized")

    # Single status field: overlap is the stronger topology signal, so it wins
    # the status label when both are present, but the gap quantity above is still
    # emitted alongside it.
    if has_overlap:
        status = AUDIT_OVERLAPS_DETECTED
    elif has_gap:
        status = AUDIT_GAPS_DETECTED
    elif expects_full:
        status = AUDIT_COMPLETE_NONOVERLAPPING
        notes.append("base-zoning covers the lot with no same-family overlap or gap")
    else:
        # Selective family present with no same-family overlap: legitimate.
        status = AUDIT_NOT_APPLICABLE
        notes.append("selective family present; no same-family overlap; gaps not applicable")

    return CoverageAudit(
        family=family,
        status=status,
        coverage_expectation=expectation,
        unassigned_area_sq_ft=unassigned,
        overlap_area_sq_ft=overlap,
        district_count=count,
        notes=notes,
    )
