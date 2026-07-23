"""Deterministic, coverage-aware scenario FOUNDATION (task M5-T001).

Service-layer only (no endpoint in this slice). Consumes ``property_profile``
(1.4.0) and ``rule_evaluation`` (1.0.0) documents READ-ONLY and assembles a
typed, provenance-preserving ``scenario`` document that surfaces the canonical
draft residential zoning-floor-area cap without performing any independent legal
calculation, inferring any envelope constraint, or ever being Verified.

Public API:

- :func:`build_scenario` - the deterministic builder.
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
from .models import ConstraintCompleteness, DataCompleteness, ScenarioKind

__all__ = [
    "CAP_OUTPUT_NAME",
    "ConstraintCompleteness",
    "DataCompleteness",
    "DRAFT_CAP_LABEL",
    "NOT_VERIFIED_DISCLAIMER",
    "SCENARIO_CONTRACT_VERSION",
    "ScenarioContractError",
    "ScenarioKind",
    "assert_scenario_not_verified",
    "build_scenario",
    "validate_scenario_document",
]
