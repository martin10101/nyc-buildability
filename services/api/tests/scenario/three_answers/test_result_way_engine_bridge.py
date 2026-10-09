"""The thin adapter runs the engine and gathers the decision ways beside it (task M5-T134).

Scenarios S1-S11 and S14, each exercised THROUGH the adapter (never re-implementing the decision
module). Expected OUTCOMES come from outside the code under test: task M5-T130's benchmark ways
(work order test H2, quoted beside each test), the merged overlay-support rows named in
``result_way_bridge_overlay``, and the recorded 215-16 Northern pack assembled offline exactly as
tests/scenario/three_answers/test_result_way_bridge.py assembles it. The engine and the decision
module are READ ONLY; this adapter only carries their inputs and sets their results side by side.
"""

from __future__ import annotations

import ast
import http.client
import inspect
import pathlib
import socket

import pytest

from app.contracts.evaluator_inputs import build_evaluator_inputs, build_three_answer_inputs
from app.contracts.study_contracts import validate_results_document
from app.contracts.study_setup_bridge import study_from_study_setup
from app.profile.builder import build_property_profile
from app.scenario.three_answers.engine import ThreeAnswersResult
from app.scenario.three_answers.inputs import ThreeAnswerInputs
from app.scenario.three_answers.result_way_bridge import GatheredResult
from app.scenario.three_answers.result_way_bridge_overlay import OVERLAY_SUPPORT_ROWS
from app.scenario.three_answers.result_way_engine_bridge import (
    EngineResultWays,
    run_engine_and_result_ways,
)
from app.scenario.three_answers.result_way_inputs import (
    KIND_USER_STATEMENT,
    AreaAgreement,
    Conditional,
    Recorded,
    ResultFamily,
    Withheld,
)
from app.spatial.site_geometry import (
    derive_site_geometry,
    lot_outline_from_mappluto,
    street_data_from_pages,
)
from app.spatial.site_geometry.outline import prepare_outline
from tests.api.test_study_read_api import _TEST_ONLY_OPTION
from tests.contracts.test_evaluator_inputs import _benchmark_identity_address
from tests.contracts.test_study_setup_bridge import _OPTION_ID, _REVISION, _northern_setup
from tests.spatial._northern_replay import (
    DCM_ENVELOPE,
    replay_dcm_page,
    replay_lot_geometry,
    replay_pluto,
)

from .test_result_way_facts import _profile as _pluto_profile

_LANE_ON = {"LANE_A_ENABLED": "1"}
_LANE_OFF: dict[str, str] = {}
_COMPUTED_AT = "2026-10-03T00:00:00Z"


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Forbid live network egress at the seams where it happens (the accepted journey-test
    pattern): block http.client's connect choke points and socket.create_connection."""

    def _blocked(*_args, **_kwargs):
        raise AssertionError("network I/O attempted in a recorded-data test")

    monkeypatch.setattr(http.client.HTTPConnection, "connect", _blocked)
    monkeypatch.setattr(http.client.HTTPSConnection, "connect", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)


@pytest.fixture(scope="module")
def benchmark_geom():
    """The recorded benchmark lot's profile, prepared outline and site geometry, built offline
    through the real connectors from the recorded pack (no network) - the SAME offline assembly
    tests/scenario/three_answers/test_result_way_bridge.py uses."""
    lot, _unused = lot_outline_from_mappluto(replay_lot_geometry())
    streets = street_data_from_pages([replay_dcm_page()], envelope=DCM_ENVELOPE)
    geometry = derive_site_geometry(lot, streets)
    prepared, _reason = prepare_outline(lot)
    profile = build_property_profile(replay_pluto())
    return profile, prepared, geometry


def _bare_profile() -> dict:
    """A fetched profile with every map-based column served empty (every recorded condition
    ABSENT: no blanket withhold, no overlay block)."""
    return _pluto_profile({})


def _eval_doc(*, district="R6B", lot_type="corner", area=10075.0) -> dict:
    """A small evaluator-inputs document; a value of None omits that key (not given). The SAME
    shape tests/scenario/three_answers/test_result_way_bridge.py builds."""
    rows = []
    if district is not None:
        rows.append({"key": "zoning_district", "value": district, "fact_id": "f-dist"})
    if lot_type is not None:
        rows.append({"key": "lot_type", "value": lot_type, "fact_id": "f-type"})
    if area is not None:
        rows.append({"key": "lot_area_sq_ft", "value": area, "fact_id": "f-area"})
    return {"inputs": rows}


def _inputs(
    *, profile=None, outline=None, geometry=None, housing_program="standard_residence", **over
) -> ThreeAnswerInputs:
    """A ThreeAnswerInputs carrying the three objects, with valid required engine fields so the
    engine can run (its output is not the focus of the gather-only scenarios)."""
    fields = dict(
        results_id="res-m5t134", study_id="study-m5t134", option_id="opt-1", revision=1,
        computed_at=_COMPUTED_AT, zoning_district="R6B", lot_area_sq_ft=10075.0, lot_type="corner",
        housing_program=housing_program, overlay_present=False, special_district_present=False,
        within_100_ft_of_street_line_intersection=True,
        street_line_intersection_angle_degrees=90.0, special_density_area=False,
        property_profile=profile, prepared_outline=outline, site_geometry=geometry,
    )
    fields.update(over)
    return ThreeAnswerInputs(**fields)


def _benchmark_inputs(monkeypatch, profile, prepared, geometry) -> tuple[ThreeAnswerInputs, dict]:
    """The benchmark lot's ThreeAnswerInputs (carriers populated) and its evaluator-inputs
    document, built exactly as tests/journey/test_215_16_northern_journey.py builds them."""
    setup = _northern_setup(monkeypatch, geometry=True)
    setup["property"]["address"] = _benchmark_identity_address()
    study = study_from_study_setup(
        setup, _TEST_ONLY_OPTION, study_id="study-m5t134-bench", revision=_REVISION
    )
    doc = build_evaluator_inputs(study, _OPTION_ID)
    inputs = build_three_answer_inputs(
        doc, results_id="res-m5t134-bench", computed_at=_COMPUTED_AT,
        housing_program="standard_residence", overlay_present=True,
        special_district_present=False, within_100_ft_of_street_line_intersection=True,
        street_line_intersection_angle_degrees=90.0, special_density_area=False, study=study,
        property_profile=profile, prepared_outline=prepared, site_geometry=geometry,
    )
    return inputs, doc


def _way(ways, key):
    return next(row.way for row in ways.result_ways() if row.key == key)


_FLOOR_AREA_KEYS = (
    "max_residential_far", "max_residential_floor_area",
    "max_residential_far_qualifying_affordable_or_senior",
    "max_residential_floor_area_qualifying_affordable_or_senior",
)
_HEIGHT_KEYS = (
    "min_base_height", "max_base_height", "max_building_height",
    "min_base_height_qualifying_affordable_or_senior",
    "max_base_height_qualifying_affordable_or_senior",
    "max_building_height_qualifying_affordable_or_senior",
)
_WITHHELD_ON_BENCHMARK = (
    "max_lot_coverage", "rear_yard", "setback_above_base",
    "achieved_zoning_floor_area", "building_floors", "building_height", "floor_plate_area",
    "legal_unit_limit_standard", "legal_unit_limit_qualifying_affordable",
    "legal_unit_limit_qualifying_senior",
)


# --------------------------------------------------------------------------- S1 benchmark
def test_s1_benchmark_carriers_reach_gather_through_adapter(monkeypatch, benchmark_geom):
    """S1 / work order H2. The adapter reaches gather_result_ways with the three objects CARRIED on
    ThreeAnswerInputs and the evaluator-inputs document, runs the real engine, and returns the ways
    BESIDE the engine's ThreeAnswersResult: floor-area figures conditional; height limits
    conditional; coverage withheld with the measured reach in its reason; rear yard, setback,
    building option and unit limits withheld; never a zero."""
    profile, prepared, geometry = benchmark_geom
    inputs, doc = _benchmark_inputs(monkeypatch, profile, prepared, geometry)
    # the carriers are the REAL objects surfaced on the inputs, not passed separately
    assert inputs.property_profile is profile
    assert inputs.prepared_outline is prepared
    assert inputs.site_geometry is geometry

    res = run_engine_and_result_ways(inputs, evaluator_inputs=doc, env=_LANE_ON)
    assert isinstance(res, EngineResultWays)
    # the engine ran beside the ways and emitted a valid results document (unchanged by the carry)
    assert isinstance(res.engine_result, ThreeAnswersResult)
    assert res.engine_result.lane_enabled is True
    validate_results_document(res.engine_result.document)
    assert isinstance(res.gathered, GatheredResult)

    ways = res.gathered.ways
    # the recorded overlay reached the gather from the carried profile
    assert res.gathered.recorded.commercial_overlay.state is Recorded.PRESENT
    assert res.gathered.recorded.commercial_overlay.code == "C2-2"
    # the reach reached the gather from the carried outline + geometry
    reaches = {s.street_name: s.reach.value for s in res.gathered.inputs.reach.street_lines}
    assert reaches["215 Place"] == pytest.approx(103.93, abs=0.01)
    assert res.gathered.inputs.area.recorded_sq_ft == 10075.0
    assert res.gathered.inputs.area.agreement is AreaAgreement.DISAGREES
    # the ways (H2)
    for key in _FLOOR_AREA_KEYS:
        assert isinstance(_way(ways, key), Conditional), key
    for key in _HEIGHT_KEYS:
        assert isinstance(_way(ways, key), Conditional), key
    coverage = _way(ways, "max_lot_coverage")
    assert isinstance(coverage, Withheld)
    assert "103.93 ft" in coverage.reason and "215 Place" in coverage.reason
    for key in _WITHHELD_ON_BENCHMARK:
        assert isinstance(_way(ways, key), Withheld), key
    for row in ways.result_ways():
        assert "value" not in row.way.to_value_state(), row.key  # never a zero
    assert res.gathered.large_lot.met is False  # 10,075 < 30,000


# --------------------------------------------------------------------------- S2 outline absent
def test_s2_geometry_present_outline_absent(benchmark_geom):
    """S2 / reading O21: geometry present, no prepared outline. The outline is passed as absent, the
    reach has no street lines (stays unknown) and every reach-dependent way is withheld; the area
    could not be compared; nothing is invented."""
    _profile, _prepared, geometry = benchmark_geom
    inputs = _inputs(profile=_bare_profile(), outline=None, geometry=geometry)
    res = run_engine_and_result_ways(inputs, evaluator_inputs=_eval_doc(), env=_LANE_OFF)
    assert inputs.prepared_outline is None
    assert res.gathered.inputs.reach.street_lines == ()
    assert res.gathered.inputs.area.agreement is AreaAgreement.COULD_NOT_COMPARE
    assert isinstance(_way(res.gathered.ways, "max_lot_coverage"), Withheld)
    assert isinstance(_way(res.gathered.ways, "rear_yard"), Withheld)


# --------------------------------------------------------------------------- S3 geometry absent
def test_s3_geometry_absent():
    """S3: no site geometry at all. The reach is None and every reach-dependent way is withheld."""
    inputs = _inputs(profile=_bare_profile(), outline=None, geometry=None)
    res = run_engine_and_result_ways(inputs, evaluator_inputs=_eval_doc(), env=_LANE_OFF)
    assert inputs.site_geometry is None
    assert res.gathered.inputs.reach is None
    assert isinstance(_way(res.gathered.ways, "max_lot_coverage"), Withheld)
    assert isinstance(_way(res.gathered.ways, "rear_yard"), Withheld)


# --------------------------------------------------------------------------- S4 recorded lot area
def test_s4_profile_with_recorded_lot_area(benchmark_geom):
    """S4: a recorded lot area and an outline area. The area comparison runs on the two real figures
    and the gap-K3 large-lot answer is computed from the recorded area (10,075 < 30,000)."""
    profile, prepared, geometry = benchmark_geom
    inputs = _inputs(profile=profile, outline=prepared, geometry=geometry)
    res = run_engine_and_result_ways(
        inputs, evaluator_inputs=_eval_doc(area=10075.0), env=_LANE_OFF
    )
    assert res.gathered.inputs.area.recorded_sq_ft == 10075.0
    assert res.gathered.inputs.area.outline_sq_ft is not None  # the outline area was computed
    assert res.gathered.inputs.area.agreement is AreaAgreement.DISAGREES
    assert res.gathered.large_lot.met is False  # computed from the recorded area


# --------------------------------------------------------------------------- S5 no recorded area
def test_s5_profile_without_recorded_lot_area(benchmark_geom):
    """S5 / O25 (c): no recorded lot area. The large-lot answer is 'not stated' and the outline area
    never stands in for the recorded figure, even though an outline is present."""
    profile, prepared, geometry = benchmark_geom
    inputs = _inputs(profile=profile, outline=prepared, geometry=geometry)
    res = run_engine_and_result_ways(inputs, evaluator_inputs=_eval_doc(area=None), env=_LANE_OFF)
    assert res.gathered.inputs.area.recorded_sq_ft is None
    assert res.gathered.large_lot.met is None
    assert "not stated" in res.gathered.large_lot.statement
    assert "never used in its place" in res.gathered.area_statement


# --------------------------------------------------------------------------- S6 profile absent
def test_s6_profile_absent(benchmark_geom):
    """S6: no profile carried. Every recorded city-record column is 'not read' and every result is
    withheld; a column that was not read is never taken as none."""
    _profile, prepared, geometry = benchmark_geom
    inputs = _inputs(profile=None, outline=prepared, geometry=geometry)
    res = run_engine_and_result_ways(inputs, evaluator_inputs=_eval_doc(), env=_LANE_OFF)
    assert inputs.property_profile is None
    assert res.gathered.recorded.special_purpose_district.state is Recorded.NOT_READ
    assert res.gathered.recorded.commercial_overlay.state is Recorded.NOT_READ
    assert all(isinstance(r.way, Withheld) for r in res.gathered.ways.result_ways())


# --------------------------------------------------------------------------- S7 overlay supported
def _overlay_support_row(family: ResultFamily):
    return next(row for row in OVERLAY_SUPPORT_ROWS if row.family is family)


def test_s7_overlay_present_with_supporting_reference_row():
    """S7 / O25 (b): a recorded C2-2 overlay in R6B. The floor-area family is SUPPORTED by the
    merged reference rows (result_way_bridge_overlay), so its result is not withheld for the overlay
    (it stays conditional). The outcome is tied to the merged rows, not restated here."""
    # tied to the merged rows: the floor-area family's row is supported
    assert _overlay_support_row(ResultFamily.FLOOR_AREA).supported is True
    inputs = _inputs(profile=_pluto_profile({"overlay1": "C2-2"}), outline=None, geometry=None)
    res = run_engine_and_result_ways(inputs, evaluator_inputs=_eval_doc(), env=_LANE_OFF)
    assert res.gathered.recorded.commercial_overlay.state is Recorded.PRESENT
    assert res.gathered.recorded.commercial_overlay.code == "C2-2"
    assert isinstance(_way(res.gathered.ways, "max_residential_far"), Conditional)


# ------------------------------------------------- S8 overlay no longer blocks the rear yard
def test_s8_overlay_present_rear_yard_no_longer_blocked_by_the_overlay():
    """S8 / O25 (b), M5-T144 ruling C1: the rear-yard family is now SUPPORTED by the merged rows
    (the step-P5 row zr-34-23-page resolves the step-P4 completeness caveat), so a recorded C2-2
    overlay no longer blocks the rear yard. It is then withheld by the plain R6B rules instead:
    here, with no outline or site geometry, it is withheld for a missing property fact (missing
    information), and the reason does NOT name the overlay. Tied to the rear-yard row."""
    row = _overlay_support_row(ResultFamily.REAR_YARD)
    assert row.supported is True  # tied to the merged rear-yard row (now supported)
    inputs = _inputs(profile=_pluto_profile({"overlay1": "C2-2"}), outline=None, geometry=None)
    res = run_engine_and_result_ways(inputs, evaluator_inputs=_eval_doc(), env=_LANE_OFF)
    rear = _way(res.gathered.ways, "rear_yard")
    assert isinstance(rear, Withheld)
    assert rear.gap_kind == "missing_information"
    assert "overlay" not in rear.reason.lower()


# --------------------------------------------------------------------------- S9 density statement
def test_s9_user_density_statement(benchmark_geom):
    """S9 / owner rule R255: a user's statement that the lot is NOT in a special density area makes
    the legal unit limit conditional on that statement and appears in NO gathered fact record;
    without the statement the unit limit is withheld."""
    profile, prepared, geometry = benchmark_geom
    inputs = _inputs(profile=profile, outline=prepared, geometry=geometry)
    with_stmt = run_engine_and_result_ways(
        inputs, evaluator_inputs=_eval_doc(), special_density_statement=True, env=_LANE_OFF
    )
    without = run_engine_and_result_ways(
        inputs, evaluator_inputs=_eval_doc(), special_density_statement=None, env=_LANE_OFF
    )
    unit = _way(with_stmt.gathered.ways, "legal_unit_limit_standard")
    assert isinstance(unit, Conditional)
    assert any(c.kind == KIND_USER_STATEMENT for c in unit.conditions)
    assert isinstance(_way(without.gathered.ways, "legal_unit_limit_standard"), Withheld)
    for fact in with_stmt.gathered.recorded.facts():
        assert "density" not in fact.statement.lower()


# --------------------------------------------------------------------------- S10 conversion / mixed
def test_s10_conversion_or_mixed_building_has_no_input_here(benchmark_geom):
    """S10 / O25 (d): a conversion or mixed building is withheld and this piece has NO input that
    changes it - the adapter carries no conversion / mixed-building parameter, and the building
    option stays withheld."""
    params = set(inspect.signature(run_engine_and_result_ways).parameters)
    assert not (params & {"conversion", "mixed_building", "existing_building"})
    profile, prepared, geometry = benchmark_geom
    inputs = _inputs(profile=profile, outline=prepared, geometry=geometry)
    res = run_engine_and_result_ways(inputs, evaluator_inputs=_eval_doc(), env=_LANE_OFF)
    for key in ("achieved_zoning_floor_area", "building_floors", "building_height"):
        assert isinstance(_way(res.gathered.ways, key), Withheld), key


# --------------------------------------------------------------------------- S11 lane off
def test_s11_lane_switch_off(benchmark_geom):
    """S11: with LANE_A off the engine emits its lane-off document unchanged and the adapter returns
    the gathered ways beside it; no production switch is turned on."""
    profile, prepared, geometry = benchmark_geom
    inputs = _inputs(profile=profile, outline=prepared, geometry=geometry)
    res = run_engine_and_result_ways(inputs, evaluator_inputs=_eval_doc(), env=_LANE_OFF)
    assert res.engine_result.lane_enabled is False
    answers = res.engine_result.document["answers"]
    assert answers["floor_area_allowance"]["status"] == "not_available"
    # the ways are still gathered beside the lane-off document
    assert res.gathered.ways.result_ways()


# --------------------------------------------------------------------- S14 no default for a fact
def test_s14_no_default_stands_for_a_fact(benchmark_geom):
    """S14 / L1: each not-read / not-stated / absent-outline state is carried as such and holds back
    its dependent way; no unknown is read as 'no'."""
    profile, prepared, geometry = benchmark_geom
    # absent outline -> reach unknown (no street lines), coverage withheld
    r_outline = run_engine_and_result_ways(
        _inputs(profile=_bare_profile(), outline=None, geometry=geometry),
        evaluator_inputs=_eval_doc(), env=_LANE_OFF,
    )
    assert r_outline.gathered.inputs.reach.street_lines == ()
    # not-stated area -> large lot None, never 0
    r_area = run_engine_and_result_ways(
        _inputs(profile=profile, outline=prepared, geometry=geometry),
        evaluator_inputs=_eval_doc(area=None), env=_LANE_OFF,
    )
    assert r_area.gathered.inputs.area.recorded_sq_ft is None
    assert r_area.gathered.large_lot.met is None
    # not-read profile -> conditions not read
    r_profile = run_engine_and_result_ways(
        _inputs(profile=None, outline=prepared, geometry=geometry),
        evaluator_inputs=_eval_doc(), env=_LANE_OFF,
    )
    assert r_profile.gathered.recorded.flood_zone.state is Recorded.NOT_READ


# --------------------------------------------------------------------------- the adapter's imports
def _runtime_import_targets() -> set[str]:
    """Every module an import STATEMENT of the adapter names at runtime (TYPE_CHECKING-only imports
    excluded), read from the parsed source - not from a text search (the docstring mentions both the
    api layer and lot_reach to say it does NOT import them)."""
    import app.scenario.three_answers.result_way_engine_bridge as adapter

    tree = ast.parse(pathlib.Path(adapter.__file__).read_text(encoding="utf-8"))

    def _in_type_checking(node: ast.AST) -> bool:
        for parent in ast.walk(tree):
            if isinstance(parent, ast.If) and getattr(parent.test, "id", None) == "TYPE_CHECKING":
                if node in ast.walk(parent):
                    return True
        return False

    targets: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and not _in_type_checking(node):
            targets.add("." * node.level + node.module)
        elif isinstance(node, ast.Import) and not _in_type_checking(node):
            targets.update(alias.name for alias in node.names)
    return targets


def test_adapter_imports_only_the_decision_entry_and_the_engine():
    """O22 / S12: the adapter imports nothing from the api layer and nothing from lot_reach at
    runtime - it imports only gather_result_ways (from result_way_bridge) and the engine's result
    type (plus its own inputs). Checked from the parsed import statements, not a text search."""
    targets = _runtime_import_targets()
    assert not any(t.startswith("app.api") for t in targets), targets
    assert not any("lot_reach" in t for t in targets), targets
    # it DOES import the decision entry and the engine's result type
    assert ".result_way_bridge" in targets
    assert ".engine" in targets
