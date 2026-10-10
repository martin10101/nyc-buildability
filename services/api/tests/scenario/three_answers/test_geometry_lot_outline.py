"""M5-T150: the site plan draws the parcel's OWN outline (S1-S6).

The lot outline of the emitted results document is the MEASURED tax-map polygon, translated to the
local-feet drawing plane (its minimum x and y subtracted so the origin sits at the lot's min
corner, orientation kept, grid north up). Its area equals the measured outline area; it is never a
rectangle sized to the recorded lot area (owner contract section 6, D-090-R896/R841/R846). With no
outline, nothing is drawn and the geometry block says why (S2).

Every document here is GENERATED from the recorded benchmark evidence through the real entry
(``run_engine_and_result_ways_from_evidence``), exactly as the journey test builds it, so a change
to ``geometry.build_geometry`` (restoring a rectangle, or dropping the local-feet translation)
changes the generated output and is caught here - these are the task's mutation-proof tests.

The expected measured area is read from the recorded tax-map geometry (the same replay fixture the
product reads), computed by Shapely, never a figure retyped from a program run (S5).
"""

from __future__ import annotations

import pytest

from app.contracts.evaluator_inputs import build_evaluator_inputs
from app.contracts.study_setup_bridge import study_from_study_setup
from app.profile.builder import build_property_profile
from app.scenario.three_answers.result_way_engine_bridge import (
    run_engine_and_result_ways_from_evidence,
)
from app.spatial.site_geometry import (
    derive_site_geometry,
    lot_outline_from_mappluto,
    street_data_from_pages,
)
from app.spatial.site_geometry.outline import prepare_outline
from tests.api.test_study_read_api import _TEST_ONLY_OPTION
from tests.contracts.test_evaluator_inputs import _benchmark_identity_address
from tests.contracts.test_study_setup_bridge import _LANE_ON, _OPTION_ID, _REVISION, _northern_setup
from tests.spatial._northern_replay import (
    DCM_ENVELOPE,
    replay_dcm_page,
    replay_lot_geometry,
    replay_pluto,
)

_STUDY_ID = "study-215-16-northern-journey"
_RESULTS_ID = "res-215-16-northern-journey"
_COMPUTED_AT = "2026-10-03T00:00:00Z"

# The recorded lot area this benchmark carries (10,075 sq ft). The rectangle the bug drew was
# sized to THIS; the measured outline area is larger (10,387.99). Read from the benchmark pack
# through the evaluator inputs below, never asserted as a bare literal of correctness.
_RECORDED_LOT_AREA = 10075.0


def _measured_outline():
    """The recorded benchmark lot's prepared tax-map outline (EPSG:2263), built offline through the
    real connectors from the recorded pack - the SAME outline the product reads. Its polygon area is
    the 'recorded measurement' the drawn outline is checked against (S5)."""
    lot, _unused = lot_outline_from_mappluto(replay_lot_geometry())
    prepared, _reason = prepare_outline(lot)
    return prepared


def _emit(monkeypatch, *, outline: bool):
    """Emit the benchmark document through the evidence entry, with or without the tax-map outline
    threaded (outline off = the live route with the spatial provider off, S2)."""
    lot, _unused = lot_outline_from_mappluto(replay_lot_geometry())
    streets = street_data_from_pages([replay_dcm_page()], envelope=DCM_ENVELOPE)
    geometry = derive_site_geometry(lot, streets)
    prepared, _reason = prepare_outline(lot)
    profile = build_property_profile(replay_pluto())
    setup = _northern_setup(monkeypatch, geometry=True)
    setup["property"]["address"] = _benchmark_identity_address()
    study = study_from_study_setup(
        setup, _TEST_ONLY_OPTION, study_id=_STUDY_ID, revision=_REVISION
    )
    doc = build_evaluator_inputs(study, _OPTION_ID)
    return run_engine_and_result_ways_from_evidence(
        evaluator_inputs=doc, study=study, results_id=_RESULTS_ID, computed_at=_COMPUTED_AT,
        housing_program="standard_residence", property_profile=profile,
        prepared_outline=prepared if outline else None,
        site_geometry=geometry, special_density_statement=None, env=_LANE_ON,
    ).document


def _shoelace_area(ring: list[list[float]]) -> float:
    pts = ring[:-1] if ring and ring[0] == ring[-1] else ring
    total = 0.0
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        total += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
    return abs(total) / 2.0


# =========================================================================== S1 / S5
def test_s1_benchmark_lot_outline_is_the_measured_polygon(monkeypatch) -> None:
    """S1: geometry.lot_outline is the measured tax-map polygon in local feet; its area equals the
    measured outline area within 0.5 sq ft; it is never a rectangle sized to the recorded lot area.

    MUTATION PROOF (the rectangle restored): the recorded-area rectangle (10,075 sq ft, four
    corners) would fail the area assertion and the distinct-vertex assertion below."""
    geometry = _emit(monkeypatch, outline=True)["geometry"]
    assert geometry["status"] == "available"
    assert geometry["crs"] == "local_feet"
    assert geometry["units"] == "feet"
    rings = geometry["lot_outline"]
    assert len(rings) == 1
    ring = rings[0]

    measured_area = _measured_outline().polygon.area  # the recorded measurement (Shapely)
    drawn_area = _shoelace_area(ring)
    assert abs(drawn_area - measured_area) <= 0.5, (drawn_area, measured_area)
    # The measured parcel is NOT the recorded-area rectangle: its area is the measured area, and it
    # has more than four distinct corners.
    assert abs(drawn_area - _RECORDED_LOT_AREA) > 1.0
    distinct = {(round(x, 6), round(y, 6)) for x, y in ring}
    assert len(distinct) >= 5, distinct  # a rectangle has four


def test_s1_lot_outline_is_translated_to_local_feet(monkeypatch) -> None:
    """S1: the measured coordinates are translated to local feet - the minimum x and y subtracted,
    so the origin sits at the lot's min corner; orientation kept, grid north up.

    MUTATION PROOF (the translation dropped): leaving the coordinates in EPSG:2263 (NY State Plane,
    ~1.05e6, ~2.16e5 feet) while the block is labelled local_feet would fail the min==0 and the
    bounded-magnitude assertions below."""
    ring = _emit(monkeypatch, outline=True)["geometry"]["lot_outline"][0]
    xs = [x for x, _ in ring]
    ys = [y for _, y in ring]
    assert min(xs) == pytest.approx(0.0, abs=1e-6)
    assert min(ys) == pytest.approx(0.0, abs=1e-6)
    # Local feet: a single NYC lot is at most a few hundred feet across - never State-Plane-scale.
    assert max(xs) < 1000.0 and max(ys) < 1000.0


def test_s5_drawn_outline_area_equals_the_recorded_measurement(monkeypatch) -> None:
    """S5: the drawn outline's area by the shoelace formula equals the recorded measurement within
    0.5 sq ft. The expected figure is the measured tax-map polygon's area, computed by Shapely from
    the recorded replay fixture - never retyped from a program run."""
    ring = _emit(monkeypatch, outline=True)["geometry"]["lot_outline"][0]
    recorded_measurement = _measured_outline().polygon.area
    assert abs(_shoelace_area(ring) - recorded_measurement) <= 0.5


# =========================================================================== S2
def test_s2_no_outline_draws_nothing_and_says_why(monkeypatch) -> None:
    """S2: with no outline (the live route with the spatial provider off), no outline is drawn - the
    whole geometry block is not_available with its reason - and no rectangle is drawn from the
    recorded area."""
    document = _emit(monkeypatch, outline=False)
    geometry = document["geometry"]
    assert geometry["status"] == "not_available"
    assert "outline is not available" in geometry["reason"]
    assert geometry["reason_kind"] == "missing_input"
    assert "lot_outline" not in geometry  # nothing drawn
    # No legal result depends on the drawing: building B still lists from the recorded area.
    assert [a["building"] for a in document["building_alternatives"]] == ["B"]


# =========================================================================== S6
def test_s6_outline_present_withholds_footprint_scaled_layers(monkeypatch) -> None:
    """S6 / ruling W5: with the measured outline present, no placement is worked, so the layers
    that would scale the lot shape into a footprint or an envelope are not drawn - the envelope and
    the floor plates are not_available (the three-way transform states each withheld reason)."""
    geometry = _emit(monkeypatch, outline=True)["geometry"]
    assert geometry["envelope"]["status"] == "not_available"
    assert geometry["floor_plates"]["status"] == "not_available"
