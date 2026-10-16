"""Drawn-content manifest (M5-T173 part B4; H4 design; audit 2026-10-15c section 3).

A data field is not proof a drawing was rendered. :class:`DrawnManifest` records
ONLY what the report actually drew, derived from the rendered
:class:`~app.drawings.report.drawings_embed.Embedded` values - never from a results
field and never computed here. Every zoning figure stays in the shared result model;
this module carries booleans and one state word so each visible "drawn"/"shown"/
"placed" claim can read rendered content instead of a hard-coded constant.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .drawings_embed import Embedded

__all__ = ["DrawnManifest", "build_manifest"]

# The kit style kind the page-4 building footprint is drawn in (kit/styles.py and
# maps/placed_footprint.py, M5-T173 part B1). The site plan "draws the footprint"
# only when it actually drew this kind. This literal is the cross-part contract
# (part W's integration test pins it equal to the kit style kind).
_FOOTPRINT_KIND = "illustrative_footprint"

# The area kernel's own SVG ``data-role`` names (kit/area_allocation.py). The state
# is 'zones' when the two fitted-zone roles were drawn, 'bar' when the two
# proportional-bar roles were, else None. These literals are the other cross-part
# contract with the kernel.
_ZONE_ROLES = ("area_zone_apartment", "area_zone_other")
_BAR_ROLES = ("area_bar_apartment", "area_bar_other")


@dataclass(frozen=True)
class DrawnManifest:
    """What the report actually drew, read from the rendered drawings only.

    Booleans and one state word; no results field and no arithmetic. Every figure
    (share, areas, heights, measurement bases) stays in the shared result model and
    is read through the readers, never here.
    """

    site_plan_drawn: bool
    site_plan_draws_footprint: bool
    section_drawn: bool
    area_illustration_state: str | None  # 'zones', 'bar' or None


def _is_drawing(embedded: Embedded | None) -> bool:
    return embedded is not None and embedded.is_drawing


def _svg_has_roles(svg: str | None, roles: Sequence[str]) -> bool:
    """True when the SVG text carries every one of ``roles`` as a ``data-role``."""
    if not svg:
        return False
    return all(f'data-role="{role}"' in svg for role in roles)


def _area_illustration_state(illustrations: Sequence[Embedded]) -> str | None:
    """'zones' / 'bar' from the first drawn illustration's own SVG data-roles, else
    None (a short line, a refused kernel, or no illustration are all not-drawn)."""
    for illustration in illustrations:
        if not _is_drawing(illustration):
            continue
        if _svg_has_roles(illustration.svg, _ZONE_ROLES):
            return "zones"
        if _svg_has_roles(illustration.svg, _BAR_ROLES):
            return "bar"
    return None


def build_manifest(
    *,
    site_plan: Embedded | None,
    area_illustrations: Sequence[Embedded] = (),
    sections: Sequence[Embedded] = (),
) -> DrawnManifest:
    """Build the manifest from the rendered Embedded values only.

    ``site_plan`` is the page-4 site plan (a map close frame or the kit fallback);
    the footprint flag reads its ``kinds_drawn``. ``area_illustrations`` are the
    per-building area illustrations and ``sections`` the floor-stack sections; the
    area state reads the embedded SVG's own data-roles. No results field is read and
    no figure is computed here.
    """
    site_drawn = _is_drawing(site_plan)
    footprint = site_drawn and _FOOTPRINT_KIND in site_plan.kinds_drawn
    return DrawnManifest(
        site_plan_drawn=site_drawn,
        site_plan_draws_footprint=footprint,
        section_drawn=any(_is_drawing(section) for section in sections),
        area_illustration_state=_area_illustration_state(area_illustrations),
    )
