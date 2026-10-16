"""The STANDARD-case height-limit lines of a results document, read for the floor-stack section
(task M5-T192, part B2 of M5-T173).

A pure READER: it reads the three standard height limits the document already carries in
``answers.permitted_envelope`` (minimum base height, maximum base height, maximum building height)
and hands them to the section renderer as lines to draw. It computes NOTHING, compares nothing with
the building, reads no qualifying-housing value and reads nothing from ``envelope_rows`` (those
carry the street-wall, setback and side-yard states, not heights). A missing or malformed entry
drops that one line; ``None`` when none survive, so the section never draws a default or a guess.

Each :class:`LegalLine` keeps the document's own label and ZR sections and the JSON pointer of the
value it was read from, so every line drawn on the section traces back to the results document.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass

__all__ = ["LegalLine", "STANDARD_HEIGHT_KEYS", "section_legal_lines"]

# The three STANDARD-case limits of ZR 23-432, in the order they stack from grade. The
# qualifying affordable/senior keys are deliberately NOT here: they are a different case and are not
# drawn for the standard building.
STANDARD_HEIGHT_KEYS: tuple[str, ...] = (
    "min_base_height",
    "max_base_height",
    "max_building_height",
)


@dataclass(frozen=True)
class LegalLine:
    """One height limit to draw as a dashed reference line on the section.

    ``value_ft`` is the document's own number in feet; ``label`` and ``zr_sections`` are the
    document's own; ``source`` is the RFC 6901 pointer of the value in the results document, so the
    printed line carries its provenance (checks C-4 / C-5)."""

    key: str
    label: str
    value_ft: float
    zr_sections: tuple[str, ...]
    source: str


def _finite_non_negative(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
        and value >= 0.0
    )


def section_legal_lines(results: Mapping) -> tuple[LegalLine, ...] | None:
    """The standard height-limit lines from ``results.answers.permitted_envelope``, or ``None`` when
    the answer is not available or no standard height survives. Nothing is computed or defaulted."""
    answers = results.get("answers")
    if not isinstance(answers, Mapping):
        return None
    envelope = answers.get("permitted_envelope")
    if not isinstance(envelope, Mapping) or envelope.get("status") != "available":
        return None
    values = envelope.get("values")
    if not isinstance(values, list):
        return None

    wanted = set(STANDARD_HEIGHT_KEYS)
    lines: list[LegalLine] = []
    for index, entry in enumerate(values):
        if not isinstance(entry, Mapping):
            continue
        key = entry.get("key")
        if key not in wanted:
            continue
        if entry.get("unit") != "feet":
            continue
        value = entry.get("value")
        if not _finite_non_negative(value):
            continue
        label = entry.get("label")
        if not isinstance(label, str) or not label.strip():
            continue
        zr = entry.get("zr_sections")
        zr_sections = tuple(z for z in zr if isinstance(z, str)) if isinstance(zr, list) else ()
        lines.append(
            LegalLine(
                key=key,
                label=label,
                value_ft=float(value),
                zr_sections=zr_sections,
                source=f"/answers/permitted_envelope/values/{index}/value",
            )
        )
    if not lines:
        return None
    order = {key: position for position, key in enumerate(STANDARD_HEIGHT_KEYS)}
    lines.sort(key=lambda line: order[line.key])
    return tuple(lines)
