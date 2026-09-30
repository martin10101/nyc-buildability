"""Engineering thresholds for single-lot site geometry (queue item B-03, plan M1-13 / §4).

These are measurement tolerances, not legal rules and not dataset values. Every result
records them (``parameters_snapshot``) so a reviewer can see exactly what was applied.
Each one is chosen so that doubt produces "unknown", never a guess.

The street-line test relies on one stated premise: a DCM street center line runs down the
middle of the mapped street, so each street line lies half the mapped width from it. Where
that premise fails (an asymmetric or irregular street), the measured gap falls outside the
match tolerance and the edge is reported as uncertain - it is never forced either way.
"""

from __future__ import annotations

__all__ = [
    "CORNER_ANGLE_MAX_DEG",
    "CORNER_ANGLE_MIN_DEG",
    "DEPTH_AGREEMENT_FT",
    "DEPTH_MIN_SAMPLE_SHARE",
    "ENVELOPE_SLACK_FT",
    "MAX_CENTERLINE_VERTICES",
    "MAX_LOT_VERTICES",
    "MAX_SAMPLES_PER_EDGE",
    "METHOD_VERSION",
    "MIN_LOT_AREA_SQ_FT",
    "MIN_SAMPLES_PER_EDGE",
    "MIN_VERTEX_SPACING_FT",
    "NOT_FRONTING_MARGIN_FT",
    "PARALLEL_MAX_ANGLE_DEG",
    "REAR_LINE_MAX_ANGLE_DEG",
    "SAMPLE_SPACING_FT",
    "SEARCH_RADIUS_FT",
    "SINGLE_STREET_MAX_BEND_DEG",
    "STREET_ACROSS_ANGLE_DEG",
    "STREET_CROSSES_LOT_MIN_FT",
    "STREET_LINE_MATCH_TOLERANCE_FT",
    "THROUGH_MIN_NORMAL_ANGLE_DEG",
    "parameters_snapshot",
]

METHOD_VERSION = "site-geometry-1"

# Sampling along each outline edge: one ray per SAMPLE_SPACING_FT, never fewer than
# MIN_SAMPLES_PER_EDGE, never more than MAX_SAMPLES_PER_EDGE (bounded work).
SAMPLE_SPACING_FT = 1.0
MIN_SAMPLES_PER_EDGE = 3
MAX_SAMPLES_PER_EDGE = 400

# How far outward from a lot line a street center line is looked for. Equal to the padding
# of the DCM query envelope used by app.spatial.wide_street_live_provider and recorded for
# the benchmark (lot bounds + 150 ft); the street data must cover at least this much.
SEARCH_RADIUS_FT = 150.0
ENVELOPE_SLACK_FT = 0.01

# A lot line is ON a street line when its distance from the center line is within this of
# half the mapped width. The benchmark lot's measured gaps are 1.0 ft (Northern Blvd) and
# 1.2 ft (215 Place).
STREET_LINE_MATCH_TOLERANCE_FT = 5.0

# A lot line is clearly NOT on a street when the nearest center line outward is more than
# this beyond the street line. Between the two tolerances the edge is uncertain.
NOT_FRONTING_MARGIN_FT = 15.0

# A street center line must run within this angle of the lot line to count as the street
# that line faces. Beyond STREET_ACROSS_ANGLE_DEG the street runs across the view, not along
# the lot line (e.g. a side lot line near a street corner): that point is clear. In between
# the point is uncertain.
PARALLEL_MAX_ANGLE_DEG = 15.0
STREET_ACROSS_ANGLE_DEG = 45.0

# Lot type (geometric classification from the outline; not a ZR 12-10 determination):
# a corner is two streets whose frontage lines meet at a lot corner with an interior angle
# inside this clear-corner range; outside it the type is unknown and needs review.
CORNER_ANGLE_MIN_DEG = 60.0
CORNER_ANGLE_MAX_DEG = 120.0
# A through lot fronts two streets on opposite sides: their outward directions differ by at
# least this angle (180 = exactly opposite).
THROUGH_MIN_NORMAL_ANGLE_DEG = 150.0
# Frontage on one street must be straight within this angle; a bending frontage (curved or
# turning street) leaves lot type and depth unknown.
SINGLE_STREET_MAX_BEND_DEG = 15.0

# Depth is measured straight back from the frontage to a REAR lot line: one running within
# this angle of the frontage. A sample whose ray leaves through a side lot line (e.g. right
# next to a corner that is not exactly square) is skipped; if fewer than
# DEPTH_MIN_SAMPLE_SHARE of the samples reach a rear line, the depth stays unknown.
REAR_LINE_MAX_ANGLE_DEG = 45.0
DEPTH_MIN_SAMPLE_SHARE = 0.5
# Through lot: depths measured from each street must agree within this to give one depth.
DEPTH_AGREEMENT_FT = 1.0

# Outline sanity and bounded work.
MIN_VERTEX_SPACING_FT = 0.01
MIN_LOT_AREA_SQ_FT = 1.0
MAX_LOT_VERTICES = 2000
MAX_CENTERLINE_VERTICES = 20000

# A center line running more than this far inside the lot means a mapped street crosses it.
STREET_CROSSES_LOT_MIN_FT = 0.5


def parameters_snapshot() -> dict[str, float | int | str]:
    """Every threshold in force, recorded on each result."""
    return {
        "method_version": METHOD_VERSION,
        "sample_spacing_ft": SAMPLE_SPACING_FT,
        "min_samples_per_edge": MIN_SAMPLES_PER_EDGE,
        "max_samples_per_edge": MAX_SAMPLES_PER_EDGE,
        "search_radius_ft": SEARCH_RADIUS_FT,
        "street_line_match_tolerance_ft": STREET_LINE_MATCH_TOLERANCE_FT,
        "not_fronting_margin_ft": NOT_FRONTING_MARGIN_FT,
        "parallel_max_angle_deg": PARALLEL_MAX_ANGLE_DEG,
        "street_across_angle_deg": STREET_ACROSS_ANGLE_DEG,
        "corner_angle_min_deg": CORNER_ANGLE_MIN_DEG,
        "corner_angle_max_deg": CORNER_ANGLE_MAX_DEG,
        "through_min_normal_angle_deg": THROUGH_MIN_NORMAL_ANGLE_DEG,
        "single_street_max_bend_deg": SINGLE_STREET_MAX_BEND_DEG,
        "rear_line_max_angle_deg": REAR_LINE_MAX_ANGLE_DEG,
        "depth_min_sample_share": DEPTH_MIN_SAMPLE_SHARE,
        "depth_agreement_ft": DEPTH_AGREEMENT_FT,
        "min_lot_area_sq_ft": MIN_LOT_AREA_SQ_FT,
        "street_crosses_lot_min_ft": STREET_CROSSES_LOT_MIN_FT,
    }
