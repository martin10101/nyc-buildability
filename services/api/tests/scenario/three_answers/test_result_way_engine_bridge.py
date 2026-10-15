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
from app.scenario.three_answers.placement import build_placement, compute_placement_geometry
from app.scenario.three_answers.result_way_bridge import GatheredResult, gather_result_ways
from app.scenario.three_answers.result_way_bridge_overlay import OVERLAY_SUPPORT_ROWS
from app.scenario.three_answers.result_way_engine_bridge import (
    EngineResultWays,
    _envelope_analysis_for,
    _placement_inputs_for,
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
# M5-T157: the benchmark lot's record places it OUTSIDE both special density areas (Queens cd 411),
# so legal_unit_limit_standard is now a CONDITIONAL ceiling, not withheld.
_WITHHELD_ON_BENCHMARK = (
    "max_lot_coverage", "rear_yard", "setback_above_base",
    "achieved_zoning_floor_area", "building_floors", "building_height", "floor_plate_area",
    "legal_unit_limit_qualifying_affordable", "legal_unit_limit_qualifying_senior",
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
    # M5-T157: the record places the benchmark lot OUTSIDE both special density areas (Queens
    # cd 411), so the legal dwelling-unit limit is a conditional ceiling with the always-present
    # zoning-lot condition - never settled, never the user_statement kind (the record decides).
    unit = _way(ways, "legal_unit_limit_standard")
    assert isinstance(unit, Conditional)
    assert any("zoning lot" in c.assumption for c in unit.conditions)
    assert all(c.kind != KIND_USER_STATEMENT for c in unit.conditions)
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
    """S9 / owner rule R255 / M5-T157 R2. The RECORD decides where it can: the benchmark lot's
    record places it OUTSIDE both special density areas (Queens cd 411), so with an agreeing or no
    statement the legal unit limit is a conditional ceiling on the zoning lot - never the
    user_statement kind - and a disagreeing statement withholds it (a statement never overrides it).
    The
    user-statement path is reached ONLY where the record is NOT KNOWN: a bare profile (no readable
    community district) with a statement that the lot is not in one makes the limit conditional on
    THAT statement; without the statement it is withheld. A statement never enters a fact record."""
    profile, prepared, geometry = benchmark_geom
    bench = _inputs(profile=profile, outline=prepared, geometry=geometry)
    # the record decides on the benchmark: conditional zoning-lot ceiling, never the statement kind
    for stmt in (True, None):
        res = run_engine_and_result_ways(
            bench, evaluator_inputs=_eval_doc(), special_density_statement=stmt, env=_LANE_OFF
        )
        unit = _way(res.gathered.ways, "legal_unit_limit_standard")
        assert isinstance(unit, Conditional)
        assert any("zoning lot" in c.assumption for c in unit.conditions)
        assert all(c.kind != KIND_USER_STATEMENT for c in unit.conditions)
    # a statement that disagrees with the record is withheld, never overrides it
    disagree = run_engine_and_result_ways(
        bench, evaluator_inputs=_eval_doc(), special_density_statement=False, env=_LANE_OFF
    )
    assert isinstance(_way(disagree.gathered.ways, "legal_unit_limit_standard"), Withheld)

    # the user-statement path is reached only where the record is NOT KNOWN (a bare profile: every
    # column served empty, so the community district cannot be read)
    bare = _inputs(profile=_bare_profile(), outline=None, geometry=None)
    with_stmt = run_engine_and_result_ways(
        bare, evaluator_inputs=_eval_doc(), special_density_statement=True, env=_LANE_OFF
    )
    without = run_engine_and_result_ways(
        bare, evaluator_inputs=_eval_doc(), special_density_statement=None, env=_LANE_OFF
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


# ----------------------------------------------------------- F1 (G1): width-fact provenance
def test_envelope_width_facts_cite_the_dcm_street_centerline_not_mappluto(benchmark_geom):
    """G1 F1: the mapped-street-width input facts carry the DCM Street Center Line window's
    provenance (the dataset the widths were MEASURED from) - its source title and the window's
    retrieval date - never the MapPLUTO lot facts (MapPLUTO carries no street-width field). A
    mutation that sourced them from `_mappluto_source(profile)` turns this red."""
    profile, prepared, geometry = benchmark_geom
    streets = street_data_from_pages([replay_dcm_page()], envelope=DCM_ENVELOPE)
    res = run_engine_and_result_ways(
        _inputs(profile=profile, outline=prepared, geometry=geometry, overlay_present=True),
        evaluator_inputs=_eval_doc(), env=_LANE_OFF,
    )
    analysis = _envelope_analysis_for(
        res.gathered, res.engine_result.document,
        street_data=streets, geometry=geometry, profile=profile,
    )
    assert analysis is not None
    width_facts = [f for f in analysis.input_facts if f["key"].startswith("mapped_street_width:")]
    assert width_facts  # both frontages classified, so both widths are emitted
    expected_date = str(streets.provenance["retrieved_at"][0])[:10]
    for fact in width_facts:
        assert fact["source_title"] == streets.source  # DCM Street Center Line, not MapPLUTO
        assert "MapPLUTO" not in fact["source_title"]
        assert fact["source_date"] == expected_date
        assert fact["basis"] == "gis"


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


# --------------------------------------------------------------------------- S11 (placement inputs)
# Scope correction 1 (M5-T172): the bridge assembles the FOUR lot measures an illustrative placement
# rests on, each on its own basis, from the carried objects - the printed-tax-map pair from PLUTO
# lot facts, the city-map (GIS) frontage from the prepared outline edge and the GIS depth from the
# lot-reach measure - never the scope's lot_front_ft (a GIS figure under the approximate_tax_map
# code). build_placement then gives the reference-case figures; a missing measure holds its basis
# back. Expected values are the settled reading placement-building-b.json, never a program run.
def _gathered_for(profile, prepared, geometry):
    return gather_result_ways(
        evaluator_inputs=_eval_doc(), profile=profile, outline=prepared, geometry=geometry,
        housing_kind="standard_residence", special_density_statement=None, zoning_lot_index=None,
    )


def test_s11_bridge_assembles_the_four_measures_each_on_its_basis(benchmark_geom):
    profile, prepared, geometry = benchmark_geom
    streets = street_data_from_pages([replay_dcm_page()], envelope=DCM_ENVELOPE)
    gathered = _gathered_for(profile, prepared, geometry)
    pi = _placement_inputs_for(
        gathered, street_data=streets, outline=prepared, geometry=geometry, profile=profile,
    )
    assert pi is not None
    assert pi.frontage_street_name == "Northern Boulevard"  # the wide street (longest frontage)
    assert pi.tax_frontage_ft == 100.76 and pi.tax_depth_ft == 100  # PLUTO, printed_tax_map
    assert round(pi.gis_frontage_ft, 2) == 103.88  # the prepared outline's NB edge, gis
    assert round(pi.gis_depth_ft, 2) == 99.97  # the NB perpendicular lot-reach measure, gis
    # the scope's lot_front_ft is the GIS frontage mislabelled approximate_tax_map; the tax frontage
    # is NOT taken from it (DB-260): 100.76 != 103.88.
    assert pi.tax_frontage_ft != round(pi.gis_frontage_ft, 2)
    # build_placement on those four measures gives the settled reference-case figures.
    geom = compute_placement_geometry(
        zoning_floor_area_sqft=20150, storeys=3, frontage_ft=pi.tax_frontage_ft,
        lot_depth_ft=pi.tax_depth_ft, gis_frontage_ft=pi.gis_frontage_ft,
        gis_depth_ft=pi.gis_depth_ft,
    )
    assert geom.footprint_sqft == 6716.66  # tax basis, equal to the reference case
    assert geom.tax_back_clearance_ft == 33.34
    assert geom.gis_back_clearance_ft == 35.31  # NOT 33.32 (DB-260)
    assert geom.frontage_conflict_ft == 3.12


def test_s11_input_states_a_missing_measure_holds_its_basis_back():
    base = dict(zoning_floor_area_sqft=20150, storeys=3, frontage_ft=100.76, lot_depth_ft=100,
                gis_frontage_ft=103.88, gis_depth_ft=99.97)
    # all four given -> placed, with the GIS conflict shown.
    placed = build_placement(placed=True, **base)
    assert placed["status"] == "placed"
    assert any(c.get("kind") == "contradicted_record" for c in placed["conditions"])
    # the tax pair missing -> withheld (the building is not placed on the printed-tax-map basis).
    no_tax = build_placement(placed=True, **{**base, "frontage_ft": None})
    assert no_tax["status"] == "withheld" and "outline" not in no_tax
    no_tax_depth = build_placement(placed=True, **{**base, "lot_depth_ft": None})
    assert no_tax_depth["status"] == "withheld"
    # the GIS pair missing -> placed on the tax basis, but no GIS conflict (that basis not known).
    no_gis = build_placement(placed=True, **{**base, "gis_frontage_ft": None, "gis_depth_ft": None})
    assert no_gis["status"] == "placed"
    assert not any(c.get("kind") == "contradicted_record" for c in no_gis["conditions"])
    # neither pair -> withheld (no default stands for a missing measure).
    neither = build_placement(placed=True, zoning_floor_area_sqft=20150, storeys=3,
                              frontage_ft=None, lot_depth_ft=None)
    assert neither["status"] == "withheld"


def test_s11_mutation_feeding_the_scope_frontage_collapses_the_conflict():
    # MUTATION (S11): feeding the scope lot_front_ft (the GIS frontage 103.88) as the tax frontage
    # instead of PLUTO's 100.76 collapses the two-basis conflict - the frontage difference goes to 0
    # - so the reference-case figures (3.12 / 33.34 / 35.31) no longer hold. This is why the bridge
    # must read the tax frontage from PLUTO, not the mislabelled scope.
    good = compute_placement_geometry(zoning_floor_area_sqft=20150, storeys=3, frontage_ft=100.76,
                                      lot_depth_ft=100, gis_frontage_ft=103.88, gis_depth_ft=99.97)
    assert good.frontage_conflict_ft == 3.12
    mutated = compute_placement_geometry(
        zoning_floor_area_sqft=20150, storeys=3, frontage_ft=103.88,
        lot_depth_ft=100, gis_frontage_ft=103.88, gis_depth_ft=99.97)
    assert mutated.frontage_conflict_ft == 0.0  # the conflict collapses; the 3.12 assertion fails
    assert mutated.footprint_sqft != good.footprint_sqft
