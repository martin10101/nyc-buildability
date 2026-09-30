"""Thresholds for single-lot site geometry (queue item B-03, plan M1-13 / §4).

These are measurement tolerances, not legal rules and not dataset values. Every result
records them (``parameters_snapshot``). They ALL need sign-off by the reviewer who owns the
site-geometry method; each is listed with what it decides.

THE PREMISE AND ITS LIMIT (stated truthfully). The street-line test assumes a DCM street
center line runs down the middle of the mapped street, so each street line lies half the
mapped width (w/2) from it. Positional error in either source moves that line:

* gap within ``STREET_LINE_MATCH_TOLERANCE_FT`` of w/2: the lot line is read as ON the street.
* gap beyond that but within ``STREET_LINE_UNCERTAINTY_BAND_FT``: the edge is UNCERTAIN. The
  band is not a free choice: it is the accepted spatial policy's positional-uncertainty band
  (app.spatial.policy, owner decision C1 linear sum of the stated source accuracies,
  +/- 20 ft each for the MapPLUTO outline and the DCM center line, both ASSUMED), doubled by
  that policy's sensitivity rule for assumed accuracies (advisory 2.6.7): 2 x (20 + 20) = 80 ft.
* gap beyond the band: read as NO STREET. This is the one place a margin decides a "no":
  a real frontage whose DCM center line is misplaced by more than the band (or whose recorded
  width understates the real width by more than twice the band) would be dropped, and the
  lot type could then read interior or through. No test of the lot's neighbours backs the
  "no street" reading yet (neighbouring-lot corroboration is a later task).

Lot type is stated only when it is the same under every reading of the uncertain edges (each
uncertain edge fronting nothing, or fronting each street it may face); otherwise it is
unknown with a machine-readable reason code.
"""

from __future__ import annotations

from app.spatial.policy import (
    MAPPLUTO_LOT_ACCURACY,
    SENSITIVITY_BAND_MULTIPLIER,
    SourceAccuracy,
    combined_band_ft,
)

__all__ = [
    "CORNER_ANGLE_MAX_DEG",
    "CORNER_ANGLE_MIN_DEG",
    "DCM_CENTERLINE_ACCURACY",
    "DEPTH_AGREEMENT_FT",
    "DEPTH_MIN_SAMPLE_SHARE",
    "ENVELOPE_SLACK_FT",
    "LOT_OUTLINE_ACCURACY",
    "MAX_CENTERLINE_VERTICES",
    "MAX_LOT_TYPE_READINGS",
    "MAX_LOT_VERTICES",
    "MAX_RAY_SEGMENT_TESTS",
    "MAX_SAMPLES_PER_EDGE",
    "METHOD_VERSION",
    "MIN_LOT_AREA_SQ_FT",
    "MIN_SAMPLES_PER_EDGE",
    "MIN_VERTEX_SPACING_FT",
    "PARALLEL_MAX_ANGLE_DEG",
    "REAR_LINE_MAX_ANGLE_DEG",
    "SAMPLE_SPACING_FT",
    "SEARCH_RADIUS_FT",
    "SINGLE_STREET_MAX_BEND_DEG",
    "STREET_ACROSS_ANGLE_DEG",
    "STREET_CROSSES_LOT_MIN_FT",
    "STREET_LINE_MATCH_TOLERANCE_FT",
    "STREET_LINE_UNCERTAINTY_BAND_FT",
    "THROUGH_MIN_NORMAL_ANGLE_DEG",
    "parameters_snapshot",
]

METHOD_VERSION = "site-geometry-2"

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
# 1.2 ft (215 Place). Decides: fronts vs uncertain.
STREET_LINE_MATCH_TOLERANCE_FT = 5.0

# Positional accuracy of the two sources (app.spatial.policy records; both ASSUMED).
LOT_OUTLINE_ACCURACY = MAPPLUTO_LOT_ACCURACY
DCM_CENTERLINE_ACCURACY = SourceAccuracy(
    value_ft=20.0,
    basis="assumed",
    citation=(
        "ASSUMED +/- 20 ft: no positional-accuracy figure is registered for the DCP Digital "
        "City Map street center lines; the value is the documented nyzd figure used by "
        "analogy, exactly as app.spatial.policy does for MapPLUTO. Basis stays 'assumed'."
    ),
    applies_to="nyc-dcp-dcm-street-centerline-arcgis:DCM_Street_Center_Line",
)


def _uncertainty_band_ft() -> float:
    band = combined_band_ft(LOT_OUTLINE_ACCURACY, DCM_CENTERLINE_ACCURACY)
    assumed = "assumed" in (LOT_OUTLINE_ACCURACY.basis, DCM_CENTERLINE_ACCURACY.basis)
    return band * SENSITIVITY_BAND_MULTIPLIER if assumed else band


# A street line up to this far beyond the lot line cannot be ruled out as the street the lot
# line is on (80 ft today). Decides: uncertain vs no street. See the module docstring.
STREET_LINE_UNCERTAINTY_BAND_FT = _uncertainty_band_ft()

# A street center line must run within PARALLEL_MAX_ANGLE_DEG of the lot line to count as
# the street that line is on. Beyond STREET_ACROSS_ANGLE_DEG the street runs across the view,
# not along the lot line (e.g. a side lot line near a street corner): positional error moves
# a line, it does not turn it by that much, so that point is clear. In between: uncertain.
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
# At most this many readings of the uncertain edges are compared; beyond it: unknown.
MAX_LOT_TYPE_READINGS = 64

# Depth is measured straight back from the frontage to a REAR lot line: one running within
# this angle of the frontage. A sample whose ray leaves through a side lot line (e.g. right
# next to a corner that is not exactly square) is skipped; if fewer than
# DEPTH_MIN_SAMPLE_SHARE of the samples reach a rear line, the depth stays unknown.
REAR_LINE_MAX_ANGLE_DEG = 45.0
DEPTH_MIN_SAMPLE_SHARE = 0.5
# Through lot: depths measured from each street must agree within this to give one depth.
DEPTH_AGREEMENT_FT = 1.0

# Outline sanity and bounded work. MAX_RAY_SEGMENT_TESTS caps the ray x segment tests (about
# a second of pure-Python work); larger inputs are refused, never run unbounded.
MIN_VERTEX_SPACING_FT = 0.01
MIN_LOT_AREA_SQ_FT = 1.0
MAX_LOT_VERTICES = 2000
MAX_CENTERLINE_VERTICES = 20000
MAX_RAY_SEGMENT_TESTS = 2_000_000

# A center line running more than this far inside the lot means a mapped street crosses it.
STREET_CROSSES_LOT_MIN_FT = 0.5


def parameters_snapshot() -> dict[str, object]:
    """Every threshold in force, recorded on each result."""
    return {
        "method_version": METHOD_VERSION,
        "sample_spacing_ft": SAMPLE_SPACING_FT,
        "min_samples_per_edge": MIN_SAMPLES_PER_EDGE,
        "max_samples_per_edge": MAX_SAMPLES_PER_EDGE,
        "search_radius_ft": SEARCH_RADIUS_FT,
        "street_line_match_tolerance_ft": STREET_LINE_MATCH_TOLERANCE_FT,
        "street_line_uncertainty_band_ft": STREET_LINE_UNCERTAINTY_BAND_FT,
        "lot_outline_accuracy": LOT_OUTLINE_ACCURACY.as_dict(),
        "dcm_centerline_accuracy": DCM_CENTERLINE_ACCURACY.as_dict(),
        "sensitivity_band_multiplier": SENSITIVITY_BAND_MULTIPLIER,
        "parallel_max_angle_deg": PARALLEL_MAX_ANGLE_DEG,
        "street_across_angle_deg": STREET_ACROSS_ANGLE_DEG,
        "corner_angle_min_deg": CORNER_ANGLE_MIN_DEG,
        "corner_angle_max_deg": CORNER_ANGLE_MAX_DEG,
        "through_min_normal_angle_deg": THROUGH_MIN_NORMAL_ANGLE_DEG,
        "single_street_max_bend_deg": SINGLE_STREET_MAX_BEND_DEG,
        "max_lot_type_readings": MAX_LOT_TYPE_READINGS,
        "rear_line_max_angle_deg": REAR_LINE_MAX_ANGLE_DEG,
        "depth_min_sample_share": DEPTH_MIN_SAMPLE_SHARE,
        "depth_agreement_ft": DEPTH_AGREEMENT_FT,
        "min_lot_area_sq_ft": MIN_LOT_AREA_SQ_FT,
        "max_ray_segment_tests": MAX_RAY_SEGMENT_TESTS,
        "street_crosses_lot_min_ft": STREET_CROSSES_LOT_MIN_FT,
    }
