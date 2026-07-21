"""M2-T013 production spatial-intersection engine.

Determines which zoning districts (and overlays / special districts) cover which
portions of a tax lot, with an explicit positional-uncertainty model and honest
coverage accounting. Emits deterministic facts-with-uncertainty only - it never
labels a result ``Verified`` (that is an M4 published-rule + G6 professional
outcome) and never collapses an uncertain boundary into a definitive assignment.

Policy is the owner-approved advisory (C1 linear-sum band, C2 conditional-only
ZTLDB upgrade, C3 no sliver suppression, C4 point+range shares) plus the
coverage-family invariants; see ``policy.py`` and
``project-control/reports/M2-T013-geospatial-policy-advisory.md``.
"""

from __future__ import annotations

from .adapter import (
    compose_from_connectors,
    district_features_from_layer_result,
    district_vintage_from_layer_result,
    lot_input_from_result,
    ztldb_inputs_from_result,
)
from .engine import compose_lot_intersection
from .geometry import assert_geometry_pins, classify_pair
from .models import (
    CoverageAudit,
    CrossCheckOutcome,
    DistrictFeature,
    LotInput,
    LotIntersectionRecord,
    PairIntersection,
)
from .policy import POLICY_VERSION, SourceAccuracy, combined_band_ft, policy_snapshot

__all__ = [
    "POLICY_VERSION",
    "SourceAccuracy",
    "combined_band_ft",
    "policy_snapshot",
    "DistrictFeature",
    "LotInput",
    "PairIntersection",
    "CoverageAudit",
    "CrossCheckOutcome",
    "LotIntersectionRecord",
    "classify_pair",
    "assert_geometry_pins",
    "compose_lot_intersection",
    "compose_from_connectors",
    "lot_input_from_result",
    "district_features_from_layer_result",
    "ztldb_inputs_from_result",
    "district_vintage_from_layer_result",
]
