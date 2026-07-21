"""Top-level lot intersection composition (advisory 2.3 lot-overall + 2.5 + 2.6).

``compose_lot_intersection`` takes a lot and the district polygons that
intersect it (grouped by zoning-features family) plus the official ZTLDB
assignment, and returns a deterministic :class:`LotIntersectionRecord` of
facts-with-uncertainty. It never collapses an uncertain case into a definitive
assignment and never emits a ``Verified`` label (owner directive item 5).
"""

from __future__ import annotations

import shapely
from shapely import geos_version as _shapely_geos_version

from app.connectors.mappluto_geometry_arcgis import canonical_to_shapely

from .coverage import audit_family
from .crosscheck import crosscheck_ztldb
from .geometry import PAIR_SLIVER_LIKE, assert_geometry_pins, classify_pair
from .models import (
    AUDIT_GAPS_DETECTED,
    AUDIT_OVERLAPS_DETECTED,
    LOT_BOUNDARY_UNCERTAIN,
    LOT_DATA_CONFLICT,
    LOT_INVALID_GEOMETRY_REVIEW,
    LOT_SINGLE_DISTRICT_CONFIDENT,
    LOT_SLIVER_AMBIGUOUS,
    LOT_SPLIT_LOT_CONFIDENT,
    PAIR_INTERIOR_CONFIDENT,
    PAIR_NEAR_BOUNDARY_UNCERTAIN,
    PAIR_SLIVER_AMBIGUOUS,
    PAIR_SPLIT_CONFIDENT,
    XCHK_SET_CONFLICT,
    XCHK_ZTLDB_ABSENT,
    DistrictFeature,
    LotInput,
    LotIntersectionRecord,
)
from .policy import AREA_EPSILON_SQ_FT, policy_snapshot

_BASE_FAMILY = "base_zoning"

# Lot geometry states that cannot enter intersection: no fabricated assignment
# is ever produced from them (SI-S7, SI-S11, advisory 2.6.4/2.6.5).
_NON_INTERSECTABLE_LOT_STATUSES = frozenset(
    {"invalid_geometry", "review_required", "no_feature", "multiple_features"}
)


def _geos_string() -> str:
    return ".".join(str(part) for part in _shapely_geos_version)


def _invalid_lot_record(lot: LotInput, reason: str, policy: dict) -> LotIntersectionRecord:
    return LotIntersectionRecord(
        bbl=lot.bbl,
        lot_overall_class=LOT_INVALID_GEOMETRY_REVIEW,
        pairs=[],
        coverage_audits=[],
        crosscheck=None,
        professional_review_required=True,
        review_reasons=[reason],
        unassigned_area=[],
        overlap_area=[],
        accuracy_records=[lot.accuracy.as_dict()],
        policy=policy,
        provenance=dict(lot.provenance),
        notes=[reason],
    )


def compose_lot_intersection(
    lot: LotInput,
    districts: list[DistrictFeature],
    *,
    ztldb_assignment: dict | None = None,
    ztldb_status: str | None = None,
    ztldb_dataset_version: str | None = None,
    ztldb_source_vintage: str | None = None,
    district_source_vintage: str | None = None,
) -> LotIntersectionRecord:
    """Compose the per-lot intersection record. Fails safe: any non-intersectable
    lot geometry returns an ``invalid_geometry_review`` record with no fabricated
    assignment."""
    assert_geometry_pins(shapely.__version__, _geos_string())
    policy = policy_snapshot()

    if (
        lot.canonical_geometry is None
        or lot.review_required
        or lot.geometry_status in _NON_INTERSECTABLE_LOT_STATUSES
    ):
        reason = (
            f"lot geometry not intersectable (status={lot.geometry_status}); "
            "professional review required"
        )
        return _invalid_lot_record(lot, reason, policy)

    lot_shape = canonical_to_shapely(lot.canonical_geometry)
    lot_area = float(lot.area_sq_ft) if lot.area_sq_ft is not None else float(lot_shape.area)

    # Convert each district ONCE; share the shape with coverage. A district
    # whose geometry is not intersectable (invalid/review-required, canonical
    # None) is NEVER silently dropped: it is recorded and feeds review
    # (advisory 2.6.4).
    pairs = []
    family_shapes: dict[str, list] = {}
    invalid_district_reasons: list[str] = []
    for feature in districts:
        if feature.canonical_geometry is None:
            invalid_district_reasons.append(
                f"district geometry not intersectable on {feature.layer}:{feature.label} "
                f"(status={feature.geometry_status}); professional review required (advisory 2.6.4)"
            )
            continue
        shape = canonical_to_shapely(feature.canonical_geometry)
        family_shapes.setdefault(feature.family, []).append(shape)
        pairs.append(
            classify_pair(
                lot_shape,
                lot_area,
                layer=feature.layer,
                family=feature.family,
                district_label=feature.label,
                district_shape=shape,
                lot_accuracy=lot.accuracy,
                district_accuracy=feature.accuracy,
                feature_ref=feature.feature_ref,
            )
        )

    # Resolve internal sliver-like pairs using cross-district context WITHIN the
    # same family (advisory 2.3 sliver_ambiguous definition).
    for i, pair in enumerate(pairs):
        if pair.pair_class != PAIR_SLIVER_LIKE:
            continue
        firm_elsewhere = any(
            other.firm_intersection_sq_ft > AREA_EPSILON_SQ_FT
            for j, other in enumerate(pairs)
            if j != i and other.family == pair.family
        )
        pair.pair_class = PAIR_SLIVER_AMBIGUOUS if firm_elsewhere else PAIR_NEAR_BOUNDARY_UNCERTAIN

    # Per-family coverage audit (internal status; owner amendment invariants).
    coverage_audits = [
        audit_family(lot_shape, lot_area, family, shapes)
        for family, shapes in sorted(family_shapes.items())
    ]

    # Base-zoning geometric ordered set (firm districts) + probable side.
    base_pairs = [p for p in pairs if p.family == _BASE_FAMILY]
    firm_base = [
        p for p in base_pairs if p.pair_class in (PAIR_INTERIOR_CONFIDENT, PAIR_SPLIT_CONFIDENT)
    ]
    firm_base_sorted = sorted(firm_base, key=lambda p: (-p.share_point, p.district_label))
    geometric_ordered = [
        {"label": p.district_label, "share_point": p.share_point} for p in firm_base_sorted
    ]
    overlapping_base = [p for p in base_pairs if p.raw_intersection_sq_ft > AREA_EPSILON_SQ_FT]
    probable_pair = max(
        overlapping_base, key=lambda p: (p.share_point, p.district_label), default=None
    )
    geometric_probable_label = probable_pair.district_label if probable_pair else None

    # Geometric lot-overall class (before ZTLDB), base zoning only.
    n_interior = sum(1 for p in base_pairs if p.pair_class == PAIR_INTERIOR_CONFIDENT)
    n_split = sum(1 for p in base_pairs if p.pair_class == PAIR_SPLIT_CONFIDENT)
    n_near = sum(1 for p in base_pairs if p.pair_class == PAIR_NEAR_BOUNDARY_UNCERTAIN)
    n_sliver = sum(1 for p in base_pairs if p.pair_class == PAIR_SLIVER_AMBIGUOUS)
    firm_count = n_interior + n_split

    if not base_pairs:
        geom_class = LOT_BOUNDARY_UNCERTAIN
    elif n_near > 0:
        geom_class = LOT_BOUNDARY_UNCERTAIN
    elif n_sliver > 0:
        geom_class = LOT_SLIVER_AMBIGUOUS
    elif firm_count >= 2:
        geom_class = LOT_SPLIT_LOT_CONFIDENT
    elif n_interior == 1 and n_split == 0:
        geom_class = LOT_SINGLE_DISTRICT_CONFIDENT
    else:
        # A lone split_confident (lot extends past its only base district) or no
        # firm base district: a base-zoning coverage question, never a clean pick.
        geom_class = LOT_BOUNDARY_UNCERTAIN

    crosscheck = crosscheck_ztldb(
        geometric_ordered=geometric_ordered,
        geometric_probable_label=geometric_probable_label,
        lot_overall_class=geom_class,
        ztldb_assignment=ztldb_assignment,
        ztldb_status=ztldb_status,
        ztldb_dataset_version=ztldb_dataset_version,
        ztldb_source_vintage=ztldb_source_vintage,
        district_source_vintage=district_source_vintage,
    )

    # A ZTLDB set-conflict elevates the lot to data_conflict (never pick a
    # winner). Agreement/ordering only affect the DISPLAY upgrade, never the
    # geometric class - uncertainty is never collapsed.
    lot_overall_class = LOT_DATA_CONFLICT if crosscheck.outcome == XCHK_SET_CONFLICT else geom_class

    review_reasons: list[str] = list(invalid_district_reasons)
    if lot_overall_class in (
        LOT_BOUNDARY_UNCERTAIN,
        LOT_SLIVER_AMBIGUOUS,
        LOT_DATA_CONFLICT,
    ):
        review_reasons.append(f"lot_overall_class={lot_overall_class} (advisory 2.6.1/2.6.2)")
    for pair in pairs:
        if pair.sensitivity_flip:
            review_reasons.append(
                f"sensitivity_flip on {pair.layer}:{pair.district_label}: class flips at "
                "2x band while an assumed accuracy participates (advisory 2.6.7)"
            )
        if pair.band_exceeds_feature_width and pair.raw_intersection_sq_ft > AREA_EPSILON_SQ_FT:
            review_reasons.append(
                f"band_exceeds_feature_width on {pair.layer}:{pair.district_label} "
                "(narrow feature; confidence impossible - advisory 2.6.6)"
            )
        # Fail-safe (G4 F1): the lot-overall class is computed over base zoning
        # only, so a real positional uncertainty on a NON-base family (overlay /
        # special district) would otherwise never reach the review rollup. Any
        # such uncertain pair over material lot area must route to review -
        # advisory 2.6.1 ("if rule sensitivity is unknown at this milestone:
        # always"). Strictly additive; never collapses the pair.
        if (
            pair.family != _BASE_FAMILY
            and pair.pair_class in (PAIR_NEAR_BOUNDARY_UNCERTAIN, PAIR_SLIVER_AMBIGUOUS)
            and pair.raw_intersection_sq_ft > AREA_EPSILON_SQ_FT
        ):
            review_reasons.append(
                f"non-base positional uncertainty on {pair.layer}:{pair.district_label} "
                f"({pair.pair_class}); overlay/special-district applicability requires "
                "professional review (advisory 2.6.1)"
            )
    # Fail-safe (G3 obs 2): an explicit same-family coverage gap or overlap means
    # the assignment is incomplete/inconsistent for that family; route to review
    # rather than leaving it visible-but-unflagged (owner coverage-honesty).
    for ca in coverage_audits:
        if ca.status in (AUDIT_GAPS_DETECTED, AUDIT_OVERLAPS_DETECTED):
            review_reasons.append(
                f"coverage anomaly in {ca.family}: {ca.status}; explicit "
                "unassigned/overlap area requires professional review"
            )
    if (
        crosscheck.outcome == XCHK_ZTLDB_ABSENT
        and lot_overall_class != LOT_SINGLE_DISTRICT_CONFIDENT
    ):
        review_reasons.append(
            "ZTLDB assignment absent and geometry not single_district_confident; "
            "geometry-only result capped at conditional (advisory 2.5)"
        )
    professional_review_required = bool(review_reasons)

    notes: list[str] = []
    if lot_overall_class == LOT_SPLIT_LOT_CONFIDENT:
        notes.append(
            "threshold_sensitivity_unknown: split share ranges must feed M4 rules "
            "as ranges; a threshold inside [share_min, share_max] yields conditional, "
            "never a definitive pass/fail (advisory 2.4/2.6.3)"
        )

    unassigned_area = [
        {
            "family": ca.family,
            "unassigned_area_sq_ft": ca.unassigned_area_sq_ft,
            "audit_status": ca.status,
        }
        for ca in coverage_audits
        if ca.unassigned_area_sq_ft is not None
    ]
    overlap_area = [
        {
            "family": ca.family,
            "overlap_area_sq_ft": ca.overlap_area_sq_ft,
            "audit_status": ca.status,
        }
        for ca in coverage_audits
        if ca.overlap_area_sq_ft is not None
    ]

    accuracy_records = [lot.accuracy.as_dict()]
    seen = {(lot.accuracy.applies_to, lot.accuracy.value_ft, lot.accuracy.basis)}
    for feature in districts:
        key = (feature.accuracy.applies_to, feature.accuracy.value_ft, feature.accuracy.basis)
        if key not in seen:
            seen.add(key)
            accuracy_records.append(feature.accuracy.as_dict())

    provenance = dict(lot.provenance)
    provenance["shapely_version"] = shapely.__version__
    provenance["geos_version"] = _geos_string()

    return LotIntersectionRecord(
        bbl=lot.bbl,
        lot_overall_class=lot_overall_class,
        pairs=pairs,
        coverage_audits=coverage_audits,
        crosscheck=crosscheck,
        professional_review_required=professional_review_required,
        review_reasons=review_reasons,
        unassigned_area=unassigned_area,
        overlap_area=overlap_area,
        accuracy_records=accuracy_records,
        policy=policy,
        provenance=provenance,
        notes=notes,
    )
