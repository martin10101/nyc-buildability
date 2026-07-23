"""Typed vocabulary for the deterministic scenario foundation (task M5-T001).

These enums are the machine-readable states the scenario builder assigns. They
are intentionally small, closed, and string-valued so they serialize straight
into the ``scenario`` contract and stay stable across runs.

Nothing here decides law or computes a value; the builder in
:mod:`app.scenario.builder` assigns these states deterministically from the
already-computed ``property_profile`` and ``rule_evaluation`` documents it
consumes READ-ONLY.
"""

from __future__ import annotations

from enum import Enum


class ConstraintCompleteness(str, Enum):
    """Exactly one state per candidate constraint (proposal section 4).

    - ``KNOWN``: value present from an accepted/authoritative source (e.g. lot
      area from the profile).
    - ``DRAFT``: value from a ``needs_review`` rule (never Verified) - the R5
      ``max_residential_floor_area_sq_ft`` cap.
    - ``MISSING``: no rule family or datum provides it (height, setbacks, yards,
      lot coverage, parking, ...). MUST NOT be inferred; recorded as a gap.
    - ``CONFLICTING``: sources/rules disagree (``data_conflict``). Blocks any
      scenario.
    - ``UNSUPPORTED``: district/rule family not implemented. Visible, no cap.
    - ``PROFESSIONAL_REVIEW_REQUIRED``: spatial uncertainty or fail-safe; no
      definitive value. Blocks any scenario.
    """

    KNOWN = "known"
    DRAFT = "draft"
    MISSING = "missing"
    CONFLICTING = "conflicting"
    UNSUPPORTED = "unsupported"
    PROFESSIONAL_REVIEW_REQUIRED = "professional_review_required"


class ScenarioKind(str, Enum):
    """The typed outcome of a scenario build.

    - ``PRELIMINARY``: a draft zoning-floor-area cap was surfaced from the
      canonical R5 trace (never a buildable envelope).
    - ``NO_SCENARIO``: fail-closed (conflict, professional review, spatial
      uncertainty, malformed/non-finite input, or an absent controlling input);
      no cap is surfaced.
    - ``UNSUPPORTED``: the district/rule family is not implemented; a visible
      stub with reasons and no cap.
    """

    PRELIMINARY = "preliminary"
    NO_SCENARIO = "no_scenario"
    UNSUPPORTED = "unsupported"


class DataCompleteness(str, Enum):
    """The PRD-section-12 data-completeness vocabulary (exactly three values).

    Orthogonal to coverage_status: a scenario can have rule coverage
    (``conditional``) yet be critically data-incomplete (``missing_critical``)
    because the envelope-governing rule families do not exist yet.
    """

    COMPLETE = "complete"
    MISSING_NONCRITICAL = "missing_noncritical"
    MISSING_CRITICAL = "missing_critical"


# Severity ranking so the builder can pick the most-severe completeness across
# constraints deterministically (higher index = more severe).
_COMPLETENESS_SEVERITY = {
    DataCompleteness.COMPLETE: 0,
    DataCompleteness.MISSING_NONCRITICAL: 1,
    DataCompleteness.MISSING_CRITICAL: 2,
}


def most_severe_completeness(values: list[DataCompleteness]) -> DataCompleteness:
    """Return the most-severe data-completeness in ``values`` (deterministic).

    Empty input degrades to ``MISSING_CRITICAL`` fail-closed: an absence of any
    completeness signal is treated as the most cautious state, never as
    ``complete``.
    """
    if not values:
        return DataCompleteness.MISSING_CRITICAL
    return max(values, key=lambda value: _COMPLETENESS_SEVERITY[value])
