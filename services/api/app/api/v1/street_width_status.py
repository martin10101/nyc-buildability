"""Unknown street width on ``GET /api/v1/properties/{bbl}/rule-evaluation`` (queue C-04, plan task
M1-06a; plan section 4 "Street widths": "If a width is unknown, the app shows both the
wide-street and narrow-street results side by side, marked 'Needs street width'").

When the route's server-side wide-street provider supplies NO determination (the street width is
unknown - the default today, since the live provider is flag-gated off), the engine evaluates the
ZR 23-22 wide-street-conditional districts on their conservative narrow-street row and names the
wide-street row only as the conditional alternative ``wide_street_far_alternative`` inside the
rule trace. Nothing at the top of the document said the width was unknown, so the narrow value
read as the answer.

This module adds the route-side marking, inside the existing rule_evaluation contract (no new
key, no version change): when an applicable trace applied the engine's own
``wide_street_far_alternative`` exception (the engine's statement that the governing row depends
on the street width) and no determination folded in, one reason starting with the exact label
:data:`NEEDS_STREET_WIDTH_LABEL` is appended to ``reasons``. It names the rule, the narrow-street
case the trace shows, and the wide-street case the exception names, and says neither is the
answer until the width is known. It never computes, selects, or changes a value, a coverage
status or a trace: the legal values stay the engine's.

OFF unless ``LANE_C_ENABLED`` holds an explicit true token (:func:`street_width_marking_enabled`).
The structured both-cases block (one result per wide / narrow case, ``results.street_width_case``)
needs the engine to evaluate both rows and a rule_evaluation contract bump; see the C-04 report.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.config import lane_enabled

__all__ = [
    "NEEDS_STREET_WIDTH_LABEL",
    "WIDE_STREET_ALTERNATIVE_EXCEPTION_ID",
    "mark_unknown_street_width",
    "needs_street_width_reason",
    "street_width_marking_enabled",
]

#: The plan's exact marker (sections 4 and 5a).
NEEDS_STREET_WIDTH_LABEL = "Needs street width"
#: The engine's conditional-alternative exception id on the ZR 23-22 wide-street-conditional rule
#: (``app/rules/rulesets/r6_r7_r8_wide_street_conditional_far.rule.json``). A test pins that the
#: production registry still declares it, so a rename cannot silently switch the marking off.
WIDE_STREET_ALTERNATIVE_EXCEPTION_ID = "wide_street_far_alternative"

_NARROW_OUTPUT = "max_residential_far"


def street_width_marking_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Lane C flag (``LANE_C_ENABLED``): absent / empty / unknown -> off (fail safe)."""
    return lane_enabled("C", env)


def needs_street_width_reason(document: Mapping[str, Any]) -> str | None:
    """The "Needs street width" reason for a serialized rule_evaluation ``document``, or ``None``
    when the result does not depend on an unknown street width: a fail-safe document, a document
    whose wide-street determination folded in (``wide_street`` block present), or no applicable
    trace that applied :data:`WIDE_STREET_ALTERNATIVE_EXCEPTION_ID`."""
    if document.get("fail_safe") is True or "wide_street" in document:
        return None
    evaluations = document.get("evaluations")
    if not isinstance(evaluations, list):
        return None
    for trace in evaluations:
        if isinstance(trace, Mapping) and trace.get("applicability_outcome") is True:
            if _applied_wide_street_alternative(trace):
                return _reason(trace)
    return None


def mark_unknown_street_width(document: dict) -> dict:
    """Return ``document`` with the "Needs street width" reason appended to ``reasons`` when
    :func:`needs_street_width_reason` finds one; otherwise ``document`` unchanged. Call it only
    when the route supplied no wide-street determination. Never mutates the input."""
    reason = needs_street_width_reason(document)
    reasons = document.get("reasons")
    if reason is None or not isinstance(reasons, list) or reason in reasons:
        return document
    return {**document, "reasons": [*reasons, reason]}


def _applied_wide_street_alternative(trace: Mapping[str, Any]) -> bool:
    applied = trace.get("exceptions_applied")
    if not isinstance(applied, list):
        return False
    return any(
        isinstance(exc, Mapping) and exc.get("id") == WIDE_STREET_ALTERNATIVE_EXCEPTION_ID
        for exc in applied
    )


def _reason(trace: Mapping[str, Any]) -> str:
    rule_id = trace.get("rule_id")
    rule = f"rule {rule_id}" if isinstance(rule_id, str) and rule_id else "the applicable rule"
    outputs = trace.get("outputs")
    narrow = outputs.get(_NARROW_OUTPUT) if isinstance(outputs, Mapping) else None
    if isinstance(narrow, int | float) and not isinstance(narrow, bool):
        narrow_case = f"the narrow-street case ({_NARROW_OUTPUT} {narrow}, shown in the trace)"
    else:
        narrow_case = "the narrow-street case shown in the trace"
    return (
        f"{NEEDS_STREET_WIDTH_LABEL}: the street width for this lot is unknown (no wide-street "
        f"determination is available), and {rule} depends on it. Two cases apply: "
        f"{narrow_case} and the wide-street case named in its exception "
        f"{WIDE_STREET_ALTERNATIVE_EXCEPTION_ID}. Neither is the answer until the street width "
        "is known; show both side by side."
    )
