"""Floor-stack section SVG from ONE worked building's floor schedule (task M5-T152, ruling X9 b).

Draws a worked building as a vertical section: one band per scheduled storey, the height axis to
scale, each band labelled with its floor-to-floor height and the top height of the storey, read
STRAIGHT from the schedule (no number is typed; every number drawn is a schedule figure). The
minimum base height line is drawn only where the document gives it (a ``to_min_base`` building
reaches the minimum base height at its building height); the maximum height line only if the
document carries one (the building alternative carries none, so it is not drawn). The caption says
the section is drawn from the schedule with no placement on the lot - it is an illustrative
schedule drawing, not a site plan: nothing here sits the building on the lot.

The storey bands are a QUIET NEUTRAL from the shared presentation tokens (``COLOR['selected']``),
not a use colour: the section shows a schedule, not a use, so no colour literal and no use tint is
spent on it. Report frame only (the report's scenario sheet): no notes column; sized for A4 (at most
182 mm wide by 150 mm high); every label at least 7 pt at that size. Gated behind the Lane E flag
like the other renderers.
"""

from __future__ import annotations

from collections.abc import Mapping

from .errors import DrawingInputError
from .model import Drawing, Unavailable
from .presentation_tokens import COLOR
from .sheet import Sheet
from .styles import TYPOGRAPHY
from .svg import element, num, polyline_data, svg_document, text_element

__all__ = ["REPORT_MAX_H_PT", "REPORT_MAX_W_PT", "draw_floor_stack"]

# A4 at 14 mm margins leaves 182 mm x ... usable; a report drawing is at most 182 mm wide by 150 mm
# high (ruling X9). 1 user unit = 1 pt (1/72 in); 182 mm = 515.91 pt, 150 mm = 425.20 pt.
REPORT_MAX_W_PT = 515.9
REPORT_MAX_H_PT = 425.2

_CANVAS_W = 360.0
_STACK_X0 = 150.0  # left edge of the storey bands
_STACK_W = 150.0  # band width (a section is not to scale horizontally)
_AXIS_X = _STACK_X0 - 8.0  # the height-axis labels sit left of the stack
_STACK_TOP = 44.0  # top of the stack region; leaves room above for the minimum-base label
_STACK_H = 300.0  # the stack fills this many points in height
_CAPTION_GAP = 18.0

# Shared tokens (no colour literal): a quiet neutral band, a medium outline, a dark grade line, a
# quiet reference colour for the minimum-base line, a faint axis tick.
_BAND_FILL = COLOR["selected"]
_BAND_STROKE = COLOR["supporting"]
_GRADE_STROKE = COLOR["ink"]
_REFERENCE_STROKE = COLOR["action"]
_AXIS_STROKE = COLOR["divider"]

_CAPTION = "Drawn from the floor schedule; no placement on the lot."


def _rows(alternative: Mapping) -> list[dict]:
    schedule = alternative.get("floor_schedule")
    if not isinstance(schedule, list) or not schedule:
        return []
    return [row for row in schedule if isinstance(row, Mapping)]


def _num_ft(value: object) -> str:
    """A schedule height as feet, two decimals trailing-zero-trimmed - the kit's number format."""
    text = f"{float(value):,.2f}".rstrip("0").rstrip(".")
    return f"{text or '0'} ft"


def draw_floor_stack(alternative: Mapping) -> Drawing | Unavailable:
    """The floor-stack section for one worked building (report frame), or ``Unavailable`` when the
    alternative carries no floor schedule to draw."""
    rows = _rows(alternative)
    if not rows:
        return Unavailable("floor_stack", "The building has no floor schedule to draw.",
                           "missing_input", "/floor_schedule")

    tops = [float(row["top_ft"]) for row in rows]
    max_top = max(tops)
    if max_top <= 0.0:
        raise DrawingInputError("floor_stack_degenerate", "the schedule has no positive height",
                                location="/floor_schedule")
    k = _STACK_H / max_top  # points per foot (height axis to scale)
    grade_y = _STACK_TOP + _STACK_H

    def y_of(ft: float) -> float:
        return grade_y - ft * k

    sheet = Sheet()
    size = TYPOGRAPHY.label_pt  # 8 pt >= 7 pt at the printed size

    # Grade line.
    sheet.parts.append(element("path", [
        ("d", polyline_data([(_AXIS_X - 2.0, grade_y), (_STACK_X0 + _STACK_W + 2.0, grade_y)])),
        ("fill", "none"), ("stroke", _GRADE_STROKE), ("stroke-width", 1.0)]))
    sheet.label([(_STACK_X0 + _STACK_W + 6.0, grade_y + size * 0.35, 0.0)], "Grade", size=size,
                source=None, role="floor_stack_grade")

    for row in rows:
        storey = int(row["storey"])
        top_ft = float(row["top_ft"])
        ff = float(row["floor_to_floor_ft"])
        y_top, y_bot = y_of(top_ft), y_of(top_ft - ff)
        sheet.parts.append(element("path", [
            ("d", f"M{num(_STACK_X0)} {num(y_top)} L{num(_STACK_X0 + _STACK_W)} {num(y_top)} "
                  f"L{num(_STACK_X0 + _STACK_W)} {num(y_bot)} L{num(_STACK_X0)} {num(y_bot)} Z"),
            ("fill", _BAND_FILL), ("fill-rule", "evenodd"), ("stroke", _BAND_STROKE),
            ("stroke-width", 0.75), ("data-storey", storey)]))
        # The storey number and its floor-to-floor height, inside the band or to its right.
        mid = (y_top + y_bot) / 2.0 + size * 0.35
        sheet.label(
            [(_STACK_X0 + 6.0, mid, 0.0), (_STACK_X0 + _STACK_W + 6.0, mid, 0.0)],
            f"Storey {storey}", size=size, source=f"/floor_schedule/storey/{storey}",
            role="floor_stack_storey")
        sheet.label(
            [(_STACK_X0 + _STACK_W / 2.0, mid + size + 1.0, 0.0),
             (_STACK_X0 + _STACK_W / 2.0, mid, 0.0)],
            _num_ft(ff), size=size, source=f"/floor_schedule/floor_to_floor_ft/{storey}",
            role="floor_stack_ff", anchor="middle")
        # The top height of the storey, on the left height axis (clear of the stack and any line).
        sheet.parts.append(element("path", [
            ("d", polyline_data([(_AXIS_X - 2.0, y_top), (_STACK_X0, y_top)])),
            ("fill", "none"), ("stroke", _AXIS_STROKE), ("stroke-width", 0.4)]))
        sheet.label([(_AXIS_X - 4.0, y_top + size * 0.35, 0.0)], _num_ft(top_ft), size=size,
                    source=f"/floor_schedule/top_ft/{storey}", role="floor_stack_top",
                    anchor="end")

    # The minimum base height line: drawn only where the document gives it - a 'to_min_base'
    # building reaches the minimum base height at its building height (the top of its last storey, a
    # schedule figure). It starts clear of the left height-axis labels, and its label reads in full
    # ABOVE the line (clear of the line and of the top-height label). No maximum height line: the
    # alternative carries none, so none is drawn.
    if alternative.get("fill_rule") == "to_min_base":
        y = y_of(max_top)
        sheet.parts.append(element("path", [
            ("d", polyline_data([(_STACK_X0 - 6.0, y), (_STACK_X0 + _STACK_W + 2.0, y)])),
            ("fill", "none"), ("stroke", _REFERENCE_STROKE), ("stroke-width", 1.0),
            ("stroke-dasharray", "4.00 2.00")]))
        sheet.label([(_STACK_X0, y - 7.0, 0.0)], "Minimum base height", size=size,
                    source=None, role="floor_stack_min_base")

    caption_y = grade_y + _CAPTION_GAP
    sheet.parts.append(text_element(_STACK_X0 - 14.0, caption_y, _CAPTION,
                                    size=TYPOGRAPHY.note_pt, source=None, role="caption"))
    height = min(REPORT_MAX_H_PT, caption_y + 14.0)
    svg = svg_document(width=_CANVAS_W, height=height, drawing="floor_stack",
                       title="Floor-stack section", defs="", body=sheet.parts)
    return Drawing("floor_stack", svg, tuple(sheet.labels), tuple(sheet.kinds))
