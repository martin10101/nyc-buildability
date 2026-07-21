"""Typed records for the M2-T013 spatial-intersection engine.

These are engine-internal dataclasses (facts-with-uncertainty), NOT a published
profile contract. M2-T012 integrates a selected subset into the canonical
profile in one 1.4.0 update; this module MUST NOT define or mutate any contract
schema. Nothing here ever carries a ``verified`` status - ``Verified`` is
exclusively an M4-rule + G6-human outcome (owner directive item 5).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .policy import SourceAccuracy

# ---------------------------------------------------------------------------
# Pair classification vocabulary (advisory 2.3). No value here is ever a legal
# zoning determination; these are geometric facts-with-uncertainty.
# ---------------------------------------------------------------------------
PAIR_INTERIOR_CONFIDENT = "interior_confident"
PAIR_EXTERIOR_CONFIDENT = "exterior_confident"
PAIR_SPLIT_CONFIDENT = "split_confident"
PAIR_NEAR_BOUNDARY_UNCERTAIN = "near_boundary_uncertain"
PAIR_SLIVER_AMBIGUOUS = "sliver_ambiguous"

# Lot-overall vocabulary (advisory 2.3).
LOT_SINGLE_DISTRICT_CONFIDENT = "single_district_confident"
LOT_SPLIT_LOT_CONFIDENT = "split_lot_confident"
LOT_BOUNDARY_UNCERTAIN = "boundary_uncertain"
LOT_SLIVER_AMBIGUOUS = "sliver_ambiguous"
LOT_DATA_CONFLICT = "data_conflict"
LOT_INVALID_GEOMETRY_REVIEW = "invalid_geometry_review"

# Coverage-audit status vocabulary (owner amendment invariant 6). INTERNAL - it
# is deliberately NOT a published profile-contract field.
AUDIT_UNKNOWN = "unknown"
AUDIT_COMPLETE_NONOVERLAPPING = "complete_nonoverlapping"
AUDIT_GAPS_DETECTED = "gaps_detected"
AUDIT_OVERLAPS_DETECTED = "overlaps_detected"
AUDIT_NOT_APPLICABLE = "not_applicable"

# ZTLDB cross-check outcomes (advisory 2.5).
XCHK_AGREEMENT = "agreement"
XCHK_ORDERING_DISAGREEMENT = "ordering_disagreement"
XCHK_SET_CONFLICT = "set_conflict"
XCHK_ZTLDB_ABSENT = "ztldb_absent"
XCHK_NOT_APPLICABLE = "not_applicable"

# The single honest coverage note stamped on every record. There is no
# ``verified`` value anywhere in this engine by construction (SI-CF5/SI-S9).
FACTS_WITH_UNCERTAINTY_NOTE = (
    "facts_with_uncertainty; not a Verified zoning determination "
    "(Verified requires an M4 published rule and G6 professional approval)"
)


@dataclass(frozen=True)
class DistrictFeature:
    """One district/overlay/special-district polygon from a zoning-features
    layer, canonicalized to EPSG:2263 by the adapter. Consumed read-only."""

    layer: str  # nyzd|nyco|nysp|nysp_sd|nylh|nyzma
    family: str
    label: str  # e.g. "R5", "C1-4", special-district label
    canonical_geometry: (
        list | None
    )  # canonical polygon list (EPSG:2263); None when not intersectable
    accuracy: SourceAccuracy
    geometry_status: str = "valid"  # valid|repaired|invalid_geometry|review_required
    feature_ref: dict = field(default_factory=dict)  # provenance (layer, oid, digest)


@dataclass(frozen=True)
class LotInput:
    """Lot geometry + provenance consumed read-only from a MapPLUTO
    ``LotGeometryResult`` (via the adapter). ``canonical_geometry`` is None when
    no safe canonical form exists (invalid geometry / no feature)."""

    bbl: str
    canonical_geometry: list | None
    area_sq_ft: float | None
    accuracy: SourceAccuracy
    geometry_status: (
        str  # valid|repaired|invalid_geometry|review_required|no_feature|multiple_features
    )
    review_required: bool
    provenance: dict = field(default_factory=dict)


@dataclass
class PairIntersection:
    """Deterministic (lot, district) intersection record. Exact geometric
    results are stored regardless of class (advisory 2.3): the class is an
    interpretation, the numbers are the facts."""

    layer: str
    family: str
    district_label: str
    pair_class: str
    # Exact geometric facts (always present):
    raw_intersection_sq_ft: float
    firm_intersection_sq_ft: float  # lot ∩ erode(district, band)
    dilated_intersection_sq_ft: float  # lot ∩ dilate(district, band)
    distance_ft: float
    lot_area_sq_ft: float
    # Share ranges of lot area (advisory 2.4), never renormalized:
    share_min: float
    share_point: float
    share_max: float
    minor_portion: bool
    # Band + provenance:
    band_ft: float
    combination_rule: str
    lot_accuracy: dict
    district_accuracy: dict
    accuracy_basis_assumed: bool
    band_exceeds_feature_width: bool  # erode(district, band) empty
    sensitivity_flip: bool  # class changes at 2x band while an assumed accuracy participates
    feature_ref: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class CoverageAudit:
    """INTERNAL per-family coverage diagnostic (owner amendment invariant 6).
    NOT a published profile-contract field. Computed WITHIN a single family;
    never across families (invariants 1, 2)."""

    family: str
    status: str
    coverage_expectation: str
    unassigned_area_sq_ft: float | None
    overlap_area_sq_ft: float | None
    district_count: int
    notes: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class CrossCheckOutcome:
    """ZTLDB cross-check result (advisory 2.5). ZTLDB is the primary official
    lot-level assignment source for the district SET and ORDER; geometry is the
    only source of percentages. Neither alone yields a confident assignment and
    NOTHING here is ever labelled Verified (owner amendment invariant 9)."""

    outcome: str
    ztldb_ordered_districts: list  # [{position, label}]
    geometric_ordered_districts: list  # [{label, share_point}]
    possible_vintage_skew: bool
    ztldb_dataset_version: str | None
    # C2: ZTLDB agreement upgrades a geometrically uncertain DISPLAYED result to
    # conditional AT MOST - never confident/verified.
    display_upgrade: str  # "none" | "conditional"
    vintage_comparison: str
    notes: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class LotIntersectionRecord:
    """Top-level per-lot intersection record: the deterministic, reproducible
    facts-with-uncertainty substrate M2-T012 later integrates and M4 rules later
    consume. No field is ever ``verified``."""

    bbl: str
    lot_overall_class: str
    pairs: list  # list[PairIntersection]
    coverage_audits: list  # list[CoverageAudit] (internal status)
    crosscheck: CrossCheckOutcome | None
    professional_review_required: bool
    review_reasons: list
    unassigned_area: list  # per-family explicit; never renormalized away
    overlap_area: list  # per-family, same-family only; never cross-family
    accuracy_records: list  # list[dict] every input accuracy stamped
    policy: dict
    provenance: dict
    coverage_note: str = FACTS_WITH_UNCERTAINTY_NOTE
    notes: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "bbl": self.bbl,
            "lot_overall_class": self.lot_overall_class,
            "pairs": [p.as_dict() for p in self.pairs],
            "coverage_audits": [c.as_dict() for c in self.coverage_audits],
            "crosscheck": self.crosscheck.as_dict() if self.crosscheck else None,
            "professional_review_required": self.professional_review_required,
            "review_reasons": list(self.review_reasons),
            "unassigned_area": list(self.unassigned_area),
            "overlap_area": list(self.overlap_area),
            "accuracy_records": list(self.accuracy_records),
            "policy": dict(self.policy),
            "provenance": dict(self.provenance),
            "coverage_note": self.coverage_note,
            "notes": list(self.notes),
        }
