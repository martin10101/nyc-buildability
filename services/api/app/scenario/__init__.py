"""Deterministic, coverage-aware scenario FOUNDATION (task M5-T001).

Service-layer only (no endpoint in this slice). Consumes ``property_profile``
(1.4.0) and ``rule_evaluation`` (1.0.0) documents READ-ONLY and assembles a
typed, provenance-preserving ``scenario`` document that surfaces the canonical
draft residential zoning-floor-area cap without performing any independent legal
calculation, inferring any envelope constraint, or ever being Verified.

Public API:

- :func:`build_scenario` - the deterministic builder.
- :func:`derive_practical_usable_range` - the contract-free, offline derivation of
  an illustrative practical-usable-range (min/point/max) from a scenario document
  plus its explicitly-declared typed assumptions (task M5-T005). It transports the
  canonical cap verbatim, never Verified.
- :func:`validate_scenario_document` / :class:`ScenarioContractError` - strict
  offline validation against the bundled canonical schema.
- :class:`ConstraintCompleteness`, :class:`ScenarioKind`, :class:`DataCompleteness`
  - the typed vocabulary.
- Constants (labels, disclaimer, contract version) for callers and tests.
"""

from __future__ import annotations

from .builder import build_scenario
from .constants import (
    CAP_OUTPUT_NAME,
    DRAFT_CAP_LABEL,
    NOT_VERIFIED_DISCLAIMER,
    SCENARIO_CONTRACT_VERSION,
)
from .contract import (
    ScenarioContractError,
    assert_scenario_not_verified,
    validate_scenario_document,
)
from .derive import (
    DERIVED_RANGE_LABEL,
    RECOGNIZED_FACTOR_TYPES,
    DerivedRangeKind,
    derive_practical_usable_range,
)
from .models import ConstraintCompleteness, DataCompleteness, ScenarioKind
from .ranking import (
    RANKING_LABEL,
    RankingKind,
    RankingObjective,
    rank_scenario_assumption_sets,
)
from .sensitivity import (
    SENSITIVITY_LABEL,
    SENSITIVITY_RESPONSE_METRIC,
    SensitivityKind,
    SensitivityVariable,
    analyze_scenario_sensitivity,
)

__all__ = [
    "CAP_OUTPUT_NAME",
    "DERIVED_RANGE_LABEL",
    "ConstraintCompleteness",
    "DataCompleteness",
    "DRAFT_CAP_LABEL",
    "DerivedRangeKind",
    "NOT_VERIFIED_DISCLAIMER",
    "RANKING_LABEL",
    "RECOGNIZED_FACTOR_TYPES",
    "SCENARIO_CONTRACT_VERSION",
    "SENSITIVITY_LABEL",
    "SENSITIVITY_RESPONSE_METRIC",
    "RankingKind",
    "RankingObjective",
    "ScenarioContractError",
    "ScenarioKind",
    "SensitivityKind",
    "SensitivityVariable",
    "analyze_scenario_sensitivity",
    "assert_scenario_not_verified",
    "build_scenario",
    "derive_practical_usable_range",
    "rank_scenario_assumption_sets",
    "validate_scenario_document",
]
