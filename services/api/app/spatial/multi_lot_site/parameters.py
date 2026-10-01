"""Thresholds for multi-lot site math (queue item B-07, plan M2-05 and §4 "Multi-lot sites").

These are measurement tolerances, not legal rules and not dataset values. Every result
records them (``parameters_snapshot``) and they need sign-off by the reviewer who owns the
site-geometry method. The single-lot thresholds (frontage, lot type, depth) are B-03's
(``app.spatial.site_geometry.parameters``) and apply unchanged to the combined outline.

What "touching" means here (stated; not a Zoning Resolution determination):

* Two lots touch when they share a lot line at least ``MIN_SHARED_LINE_FT`` long, measured
  on the outlines after ``conform.py`` matched them to each other, in BBL order and
  independent of the order they were given in. Conforming does two things, both within
  ``SHARED_LINE_TOLERANCE_FT``: vertices of different lots that lie within it of each other
  move to one point (the lowest of the group, joined transitively); and a lot's line is
  given a new vertex wherever another lot's vertex lies within it of that line, so a
  T-junction (one lot's corner on the middle of another lot's line) counts at its true
  length.
* Lots that meet only at a point, or along less than ``MIN_SHARED_LINE_FT``, do not touch.
* Lots further apart than ``SHARED_LINE_TOLERANCE_FT`` do not touch; the gap is reported.
  Such a gap is never closed: there is no buffering, and a vertex only ever moves onto
  another lot's vertex or line that is within the tolerance of it.
* Outlines that overlap by more than ``OVERLAP_TOLERANCE_SQ_FT`` are a tax-map conflict:
  the combined outline is not built, the combination is not offered and the overlap is the
  reason.
"""

from __future__ import annotations

from app.connectors.mappluto_geometry_arcgis import COORD_DECIMALS

__all__ = [
    "MAX_SELECTED_LOTS",
    "METHOD_VERSION",
    "MIN_SHARED_LINE_FT",
    "OVERLAP_TOLERANCE_SQ_FT",
    "SHARED_LINE_TOLERANCE_FT",
    "parameters_snapshot",
]

METHOD_VERSION = "multi-lot-site-2"

# Two lot lines count as one shared line when they lie within this distance of each other:
# the MapPLUTO connector's canonical coordinate precision (COORD_DECIMALS = 2, so 0.01 ft).
# Block 7334 lots 1 and 70 share their two corners exactly (0.0 ft apart). Neighbours do not
# always share corners: a narrower rear lot's corners can sit mid-line on a deeper lot that
# has no vertex there (a T-junction), and outlines can be rounded independently. Conforming
# (conform.py) handles both within this distance. Decides: touching vs a gap.
SHARED_LINE_TOLERANCE_FT = 10.0 ** -COORD_DECIMALS

# A shared line shorter than this is a point contact, not touching. Decides: touching vs
# meeting only at a corner. A corner contact measures 0 ft; 1 ft is far above the 0.01 ft
# tolerance and far below any lot line a building could use.
MIN_SHARED_LINE_FT = 1.0

# Overlap between two selected outlines that is ignored when they are combined: the same
# smallest measurable area B-03 uses for a lot (MIN_LOT_AREA_SQ_FT). Above it the tax-map
# outlines conflict and the combined outline is not built.
OVERLAP_TOLERANCE_SQ_FT = 1.0

# Bounded work: every pair of selected lots is compared, so a selection is capped. A larger
# selection is refused, never run unbounded.
MAX_SELECTED_LOTS = 100


def parameters_snapshot() -> dict[str, object]:
    """Every multi-lot threshold in force, recorded on each result."""
    return {
        "method_version": METHOD_VERSION,
        "shared_line_tolerance_ft": SHARED_LINE_TOLERANCE_FT,
        "min_shared_line_ft": MIN_SHARED_LINE_FT,
        "overlap_tolerance_sq_ft": OVERLAP_TOLERANCE_SQ_FT,
        "max_selected_lots": MAX_SELECTED_LOTS,
    }
