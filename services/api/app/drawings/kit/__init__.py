"""Drawing kit v0 (task E-01, plan section 5c, M1-27): server-made vector SVG
drawings from the results contract's geometry block.

Public entry points (behind the Lane E flag ``LANE_E_ENABLED``, default off):

* :func:`render_site_plan` - lot lines with computed dimensions, footprint by
  use, hatched yards, setback lines, street names, north arrow, scale bar,
  generated legend, notes read from the results;
* :func:`render_massing` - axonometric massing of the floor plates.

Both validate the results document first (:mod:`.adapter`, fail closed) and
are pure and deterministic: the same results give byte-identical SVG. Each
returns a :class:`Drawing` (SVG text, every printed label with its source in
the results, kinds drawn) or :class:`Unavailable` carrying the results' own
reason. The shared look lives in :mod:`.styles` (the drawing style table).
The section drawing (E-01b) is not built here.
"""

from __future__ import annotations

from collections.abc import Mapping

from .adapter import load_drawing_input
from .errors import DrawingInputError
from .flag import DrawingKitDisabled, drawing_kit_enabled
from .massing import draw_massing
from .model import Drawing, DrawingInput, Label, Unavailable
from .site_plan import draw_site_plan
from .styles import STYLE_TABLE, style_for, style_table_as_dict

__all__ = [
    "STYLE_TABLE",
    "Drawing",
    "DrawingInput",
    "DrawingInputError",
    "DrawingKitDisabled",
    "Label",
    "Unavailable",
    "drawing_kit_enabled",
    "load_drawing_input",
    "render_massing",
    "render_site_plan",
    "style_for",
    "style_table_as_dict",
]


def _input(results: Mapping, drawing: str, env: Mapping[str, str] | None):
    if not drawing_kit_enabled(env):
        raise DrawingKitDisabled("the drawing kit is off (LANE_E_ENABLED is not set)")
    data = load_drawing_input(results)
    if isinstance(data, Unavailable):
        return Unavailable(drawing, data.reason, data.reason_kind, f"{data.source}/reason")
    return data


def render_site_plan(
    results: Mapping, *, env: Mapping[str, str] | None = None
) -> Drawing | Unavailable:
    data = _input(results, "site_plan", env)
    return data if isinstance(data, Unavailable) else draw_site_plan(data)


def render_massing(
    results: Mapping, *, env: Mapping[str, str] | None = None
) -> Drawing | Unavailable:
    data = _input(results, "massing", env)
    return data if isinstance(data, Unavailable) else draw_massing(data)
