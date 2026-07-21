"""Coverage + data-completeness vocabulary for rule results (PRD section 12).

These mirror the canonical ``coverage_status`` contract
(packages/contracts/schemas/v1/coverage_status.schema.json) - the SAME six
coverage statuses and three completeness statuses - so a rule result labels
itself with exactly the vocabulary the rest of the platform already speaks. The
values are duplicated here (not imported from the contract) because this engine
module must not depend on the contract bundle; a test asserts the two lists stay
identical so drift is caught.

The load-bearing invariant (owner directive item 5): ``verified`` is NEVER
produced by evaluating a draft rule. It is reachable only for a ``published``
rule whose G6 approval is attached at evaluation time. Everything an agent-run
evaluation can emit tops out at ``conditional``.
"""

from __future__ import annotations

# Coverage statuses (PRD section 12; identical to the canonical enum).
COVERAGE_VERIFIED = "verified"
COVERAGE_CONDITIONAL = "conditional"
COVERAGE_PROFESSIONAL_REVIEW_REQUIRED = "professional_review_required"
COVERAGE_DATA_CONFLICT = "data_conflict"
COVERAGE_UNSUPPORTED = "unsupported"
COVERAGE_NOT_APPLICABLE = "not_applicable"

COVERAGE_STATUSES = (
    COVERAGE_VERIFIED,
    COVERAGE_CONDITIONAL,
    COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
    COVERAGE_DATA_CONFLICT,
    COVERAGE_UNSUPPORTED,
    COVERAGE_NOT_APPLICABLE,
)

# Data-completeness statuses (PRD section 12 companion; identical to the
# canonical $defs/data_completeness enum).
COMPLETENESS_COMPLETE = "complete"
COMPLETENESS_MISSING_NONCRITICAL = "missing_noncritical"
COMPLETENESS_MISSING_CRITICAL = "missing_critical"

COMPLETENESS_STATUSES = (
    COMPLETENESS_COMPLETE,
    COMPLETENESS_MISSING_NONCRITICAL,
    COMPLETENESS_MISSING_CRITICAL,
)

# Severity ordering used only to take the MOST severe (least-confident) status
# when several apply. ``verified`` is intentionally the least severe; a downgrade
# can only move away from it, never toward it, for a draft rule.
_SEVERITY = {
    COVERAGE_VERIFIED: 0,
    COVERAGE_CONDITIONAL: 1,
    COVERAGE_NOT_APPLICABLE: 2,
    COVERAGE_UNSUPPORTED: 3,
    COVERAGE_PROFESSIONAL_REVIEW_REQUIRED: 4,
    COVERAGE_DATA_CONFLICT: 5,
}


def most_severe(*statuses: str) -> str:
    """Return the least-confident (highest-severity) coverage status supplied."""
    chosen = COVERAGE_VERIFIED
    for status in statuses:
        if status is None:
            continue
        if _SEVERITY[status] > _SEVERITY[chosen]:
            chosen = status
    return chosen
