"""Wording and labels (rulings X4, X5, X6, X11).

ONE place for: the six status labels and how a document value maps to one of them
(X4); the result wording the report must and must not use (X5); the standing
label (X11, ADR-007). The page modules ask this module for a label or a phrase;
they never choose their own words for a result.
"""

from __future__ import annotations

from collections.abc import Mapping

__all__ = [
    "CONDITIONAL",
    "FORBIDDEN_RESULT_WORDS",
    "ILLUSTRATIVE",
    "PENDING_VERIFICATION",
    "PROVISIONAL",
    "SIX_LABELS",
    "SIX_LABEL_DEFINITIONS",
    "STANDING_LABEL",
    "UNRESOLVED",
    "VERIFIED",
    "label_for_answer_status",
    "label_for_value_state",
    "label_for_way",
    "scheduled_floor_area_line",
]

VERIFIED = "Verified"
PROVISIONAL = "Provisional"
ILLUSTRATIVE = "Illustrative"
CONDITIONAL = "Conditional"
PENDING_VERIFICATION = "Pending verification"
UNRESOLVED = "Unresolved"

#: The six labels, in the owner's order (rows R779 to R799). Verified is listed
#: so the key can define it; nothing in the report is given the Verified label
#: (question C1 open, X4/X11).
SIX_LABELS = (
    VERIFIED,
    PROVISIONAL,
    ILLUSTRATIVE,
    CONDITIONAL,
    PENDING_VERIFICATION,
    UNRESOLVED,
)

#: One definition per label for the status-label key on the evidence page, word
#: for word from D-090 row R783. This is the ONLY place the word "Verified" is
#: used; its row says it is not used in this report (F11).
SIX_LABEL_DEFINITIONS = (
    (VERIFIED, "Supported by completed checks and evidence. Not used in this report."),
    (PROVISIONAL, "Prepared but subject to confirmation or revision."),
    (ILLUSTRATIVE, "Included to demonstrate a possible arrangement or test case."),
    (CONDITIONAL, "Dependent on stated assumptions or future checks."),
    (PENDING_VERIFICATION, "Awaiting a specific review, measurement, approval, or calculation."),
    (UNRESOLVED,
     "Not capable of supporting a conclusion because necessary information or checks are "
     "unavailable."),
)

#: The standing label (ADR-007, rows R164 and R165). Shown once, compactly.
STANDING_LABEL = (
    "Preliminary zoning results: a labelled, unreviewed draft. Each figure carries its "
    "source in the Zoning Resolution. Professional review is advisory."
)

#: Words the report must never use for a result, anywhere (X5). Compared
#: case-insensitively by the tests.
FORBIDDEN_RESULT_WORDS = (
    "achieved",
    "no allowance left unused",
    "optimal",
    "compliant",
    "feasible",
    "preferred",
    "recommended",
)


def label_for_way(way: object) -> str:
    """Map a value's ``way`` object (``{"way": "conditional"|"settled"|...}``) to
    a label. A conditional value or a worked building whose way is conditional is
    Conditional; a settled value is Provisional; a withheld way defers to its gap
    kind through :func:`label_for_value_state`."""
    if isinstance(way, Mapping):
        return _from_way_token(way.get("way"), way.get("gap_kind"))
    if isinstance(way, str):
        return _from_way_token(way, None)
    return PENDING_VERIFICATION


def label_for_value_state(state: Mapping) -> str:
    """Label for one ``value_states`` entry. A withheld value is Unresolved when
    its gap is missing information, otherwise Pending verification (awaiting a
    rule, a check or a calculation)."""
    return _from_way_token(state.get("way"), state.get("gap_kind"))


def _from_way_token(way: object, gap_kind: object) -> str:
    if way == "settled":
        return PROVISIONAL
    if way == "conditional":
        return CONDITIONAL
    if way == "withheld":
        return UNRESOLVED if gap_kind == "missing_information" else PENDING_VERIFICATION
    return PENDING_VERIFICATION


def label_for_answer_status(status: object, reason_kind: object) -> str:
    """Label for a whole answer or sub-result that is ``not_available``. A missing
    input is Unresolved; anything awaiting a rule or calculation is Pending
    verification."""
    if status == "available":
        return PROVISIONAL
    if reason_kind == "missing_input":
        return UNRESOLVED
    return PENDING_VERIFICATION


def scheduled_floor_area_line(area_text: str) -> str:
    """The exact scheduled-floor-area wording (X5). ``area_text`` is the already
    formatted figure read from the document (for example ``"20,150"``)."""
    return f"Scheduled floor area: {area_text} sq ft; site fit unverified"
