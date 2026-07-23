"""Fixed, human-reviewed strings and tables for the scenario foundation
(task M5-T001).

Every value here is a CONSTANT the deterministic builder emits verbatim - no
value is computed, inferred, or defaulted at runtime. Keeping them in one place
makes the honest-labelling guarantees auditable and keeps the builder logic
free of prose.
"""

from __future__ import annotations

from .models import DataCompleteness

# The scenario contract version this builder emits (a published value in the
# closed scenario.schema.json contract_version enum).
SCENARIO_CONTRACT_VERSION = "1.0.0"

# The single canonical trace output the cap is taken from - NEVER recomputed
# here, only surfaced (proposal sections 1-2, 5).
CAP_OUTPUT_NAME = "max_residential_floor_area_sq_ft"
FAR_OUTPUT_NAME = "max_residential_far"

# The only rule family this foundation surfaces a cap for.
RESIDENTIAL_FAR_FAMILY = "residential_far"

# The mandatory label attached to a surfaced cap (proposal section 5.4). It is
# attached to the value so the cap can never travel without its honest framing.
DRAFT_CAP_LABEL = (
    "DRAFT maximum residential ZONING-FLOOR-AREA CAP under ZR 23-21. NOT gross, "
    "net, sellable, or feasible floor area; NOT a buildable envelope. Height, "
    "stories, setbacks, yards, lot coverage, open space, parking, and "
    "street-wall constraints are UNKNOWN (see coverage matrix). Draft rule "
    "(needs_review); requires professional review; NOT Verified."
)

# The permanent honest disclaimer stamped on every scenario, regardless of kind.
NOT_VERIFIED_DISCLAIMER = (
    "DRAFT scenario - not a Verified determination. Assembled by deterministic "
    "code from a needs_review draft rule evaluation (pending raw-HTML source "
    "verification and G6 qualified-human legal approval, PRD sections 10-12). It "
    "must never be presented, stored, or consumed as Verified; coverage tops out "
    "at conditional."
)

# The documented tolerance for the VERIFICATION-ONLY integrity check
# (proposal section 5 step 5). Relative-with-floor so both tiny and large caps
# are compared sensibly. The surfaced value is ALWAYS the canonical trace value;
# this only decides whether to fail closed.
INTEGRITY_TOLERANCE = 1e-6
INTEGRITY_METHOD = "abs(recomputed - canonical) <= tolerance * max(1, abs(canonical))"

# Coverage-status vocabulary narrowed to exclude 'verified' (mirrors the
# rule_evaluation contract). A scenario is never Verified.
DRAFT_COVERAGE_VALUES = (
    "conditional",
    "professional_review_required",
    "data_conflict",
    "unsupported",
    "not_applicable",
)

# Fail-safe discriminators (rule_evaluation.fail_safe_reason) that signal a
# CONFLICT vs a PROFESSIONAL-REVIEW stop.
CONFLICT_FAIL_SAFE_REASONS = frozenset({"data_conflict", "rule_conflict"})
PROFESSIONAL_REVIEW_FAIL_SAFE_REASONS = frozenset(
    {
        "spatial_intersection_absent",
        "spatial_context_incomplete",
        "geometry_uncertain",
        "inconsistent_confident_geometry",
    }
)

# ---------------------------------------------------------------------------
# Envelope constraint families that DO NOT EXIST as a rule today. Each is
# emitted with state MISSING and MUST NOT be inferred. The tuple order is the
# deterministic emission order (after residential_far_cap, lot_area,
# zoning_district). blocks_envelope drives both the coverage matrix flag and the
# per-constraint data-completeness (a hard blocker is missing_critical).
# ---------------------------------------------------------------------------
# (key, governs, blocks_buildable_envelope)
MISSING_ENVELOPE_CONSTRAINTS = (
    ("height_limit", "max height / story count", True),
    ("setbacks_yards", "front / side / rear yard buildable footprint", True),
    ("lot_coverage_open_space", "footprint <-> FAR interaction", True),
    ("street_wall_base_height", "lower-massing form", True),
    ("parking_loading", "ground/cellar program", False),
    ("use_group_overlay", "permitted use mix", False),
    ("special_districts_overlays", "modifications to base rules", True),
    ("density_bonuses", "FAR bonus (e.g. inclusionary housing)", False),
)


def completeness_for_blocking(blocks_envelope: bool) -> DataCompleteness:
    """A hard envelope blocker that is missing is critically incomplete; an
    other missing family is non-critical. Deterministic, no inference."""
    return (
        DataCompleteness.MISSING_CRITICAL
        if blocks_envelope
        else DataCompleteness.MISSING_NONCRITICAL
    )


# ---------------------------------------------------------------------------
# The rule-coverage dependency matrix (proposal section 7), emitted verbatim on
# every scenario. Only the first row exists today; everything else is MISSING or
# out of scope and MUST NOT be inferred.
# ---------------------------------------------------------------------------
# (constraint_family, governs, rule_status_today, blocks_buildable_envelope)
COVERAGE_MATRIX = (
    (
        "residential_far_cap",
        "draft max residential zoning floor area (R5)",
        "draft",
        False,
    ),
    ("height_limit", "max height / sky-exposure plane", "missing", True),
    ("setbacks_yards", "front / side / rear yard setbacks", "missing", True),
    ("lot_coverage_open_space", "lot coverage / open-space ratio", "missing", True),
    ("street_wall_base_height", "street wall / base height", "missing", True),
    ("parking_loading", "parking / loading", "missing", False),
    ("use_group_overlay", "use group / commercial overlay", "missing", False),
    (
        "special_districts_overlays",
        "special districts / mapped overlays",
        "missing",
        True,
    ),
    ("density_bonuses", "density bonuses (e.g. inclusionary housing)", "missing", False),
    (
        "higher_density_bulk_tower",
        "higher-density bulk / tower massing (non-R5)",
        "out_of_scope",
        False,
    ),
    (
        "gross_to_net_efficiency_yield",
        "gross-to-net / efficiency, unit count, constructability",
        "out_of_scope",
        False,
    ),
)


def coverage_matrix_rows() -> list[dict]:
    """Materialize the coverage matrix as contract rows (fresh list each call so
    a caller can never mutate the module constant)."""
    return [
        {
            "constraint_family": family,
            "governs": governs,
            "rule_status_today": status,
            "blocks_buildable_envelope": blocks,
        }
        for family, governs, status, blocks in COVERAGE_MATRIX
    ]
