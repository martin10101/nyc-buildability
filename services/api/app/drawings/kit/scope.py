"""The results document's ``scope`` block, laid out for the drawings
(owner directive D-090-R108, "put the scope beside the numbers"; results
contract 1.1.0).

When a results document carries a non-null ``scope`` the site plan (and the
massing sheet, when it draws) and the DXF notes layer print the scope beside
the figures: the estimate label, the tax lot it is for, the assumed conditions,
the whole-site statement and the two owner-settled remaining-capacity strings.

Every printed FIGURE and settled string is read from the results document and
carries the JSON pointer it came from (check C-4). The only text the kit adds
of its own is the ``Assumed conditions`` heading and the short plain-words name
of each assumption key (:data:`ASSUMPTION_KEY_NAMES`) and the flag words
(:data:`FLAG_WORDS`); those are a fixed presentation vocabulary - like the
drawing kit's yard-kind names - validated against the document's machine value,
never a legal claim and never a figure.

This module builds a document-agnostic, ordered list of :class:`ScopePart`
lines (:class:`ScopeView`). The site plan and massing turn each line into a
drawing ``Note``; the results DXF turns each line into an annotation line. Both
render the SAME lines, so the SVG and the DXF say the same thing.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .errors import DrawingInputError
from .labels import format_number
from .svg import xml_illegal

__all__ = [
    "ASSUMED_CONDITIONS_HEADING",
    "ASSUMPTION_KEY_NAMES",
    "FLAG_WORDS",
    "ScopePart",
    "ScopeView",
    "load_scope",
]

#: Plain-words name of each assumption ``key`` the emitter uses (D-090-R108
#: schema examples). A fixed presentation vocabulary - like the kit's yard-kind
#: names - validated against the document key by the C-4 checker; an unknown key
#: fails closed (the kit never invents a name for a key it does not know).
ASSUMPTION_KEY_NAMES: dict[str, str] = {
    "lot_type": "Lot type",
    "within_100_ft_of_street_line_intersection": "Within 100 ft of a street-line intersection",
    "street_line_intersection_angle_degrees": "Street-line intersection angle",
    "housing_program": "Housing program",
    "floor_to_floor_ft": "Floor-to-floor height",
}

#: Plain words for a boolean assumption value (the schema's ``value`` may be a
#: flag). Validated against the document boolean by the C-4 checker.
FLAG_WORDS: dict[bool, str] = {True: "Yes", False: "No"}

ASSUMED_CONDITIONS_HEADING = "Assumed conditions"


@dataclass(frozen=True)
class ScopePart:
    """One run of a scope line: its printed ``text`` and, when the text is a
    figure or settled string READ from the results, the JSON pointer ``source``
    it came from. ``mine`` marks the kit's own presentation words (the heading,
    the plain key name, the flag word) - screened for claim words on the DXF and
    never carrying a figure traced to the results."""

    text: str
    source: str | None
    mine: bool


@dataclass(frozen=True)
class ScopeView:
    """The scope block rendered as ordered lines, each a tuple of parts. The
    drawings turn each line into one note/annotation line, in order."""

    lines: tuple[tuple[ScopePart, ...], ...]


def _printed(value: str, pointer: str) -> None:
    """Refuse a results string the drawings cannot print as well-formed XML."""
    if xml_illegal(value):
        raise DrawingInputError("scope_invalid_text", "scope text carries a character XML forbids",
                                location=pointer)


def _doc(value: str, pointer: str) -> ScopePart:
    """A part whose text is read straight from the results at ``pointer``."""
    _printed(value, pointer)
    return ScopePart(value, pointer, mine=False)


def _value_parts(value, unit, base: str) -> list[ScopePart]:
    """The ``value + unit`` parts of one assumption, in that order. A boolean is
    shown as a flag word; a number is formatted like every other drawn number;
    a string is printed as given. The unit, when present, follows the value."""
    if isinstance(value, bool):
        parts = [ScopePart(FLAG_WORDS[value], f"{base}/value", mine=True)]
    elif isinstance(value, (int, float)):
        parts = [ScopePart(format_number(float(value)), f"{base}/value", mine=False)]
    else:
        parts = [_doc(str(value), f"{base}/value")]
    if unit is not None:
        parts.append(_doc(str(unit), f"{base}/unit"))
    return parts


def _assumption_line(raw: Mapping, index: int) -> tuple[ScopePart, ...]:
    base = f"/scope/assumptions/{index}"
    key = raw["key"]
    name = ASSUMPTION_KEY_NAMES.get(key)
    if name is None:
        raise DrawingInputError("scope_assumption_key_unknown",
                                f"no plain-words name for assumption key {key!r}",
                                location=f"{base}/key")
    return (
        ScopePart(name, f"{base}/key", mine=True),
        *_value_parts(raw["value"], raw["unit"], base),
        _doc(str(raw["basis"]), f"{base}/basis"),
        _doc(str(raw["statement"]), f"{base}/statement"),
    )


def load_scope(raw: Mapping | None) -> ScopeView | None:
    """Build the drawable scope from the results' ``scope`` block (already
    schema-validated by the adapter), or ``None`` when the document carries no
    scope. Fails closed on an unknown assumption key or XML-illegal text."""
    if raw is None:
        return None
    lot = raw["lot"]
    whole = raw["whole_site"]
    remaining = raw["remaining_capacity"]
    lines: list[tuple[ScopePart, ...]] = [
        (_doc(str(raw["label"]), "/scope/label"),),
        (_doc(str(lot["display"]), "/scope/lot/display"),),
        (ScopePart(ASSUMED_CONDITIONS_HEADING, None, mine=True),),
    ]
    lines += [_assumption_line(a, i) for i, a in enumerate(raw["assumptions"])]
    lines += [
        (_doc(str(whole["statement"]), "/scope/whole_site/statement"),),
        (_doc(str(remaining["label"]), "/scope/remaining_capacity/label"),),
        (_doc(str(remaining["reason"]), "/scope/remaining_capacity/reason"),),
    ]
    return ScopeView(tuple(lines))
