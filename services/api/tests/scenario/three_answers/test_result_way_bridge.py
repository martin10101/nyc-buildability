"""The entry function carries a lot's recorded facts to the decision module (task M5-T130).

Scenarios S1, S3, S5, S6, S7 and readings O15/O17. Expected OUTCOMES come from the work order's
sentences (quoted beside each test, tests H2/H5/H9 at the level of "the engine's caller, given
this lot, decides these ways"), the corner-reach reference row through the loader, and the
recorded files - never from the module under test. The benchmark lot is assembled offline from
the recorded pack exactly as tests/journey/test_215_16_northern_journey.py assembles it.
"""

from __future__ import annotations

import http.client
import inspect
import re
import socket

import pytest

from app.contracts.evaluator_inputs import build_evaluator_inputs
from app.contracts.study_setup_bridge import study_from_study_setup
from app.profile.builder import build_property_profile
from app.scenario.three_answers.result_way_bridge import (
    LARGE_LOT_THRESHOLD,
    adapt_reach,
    compare_lot_area,
    gather_result_ways,
    large_lot_answer,
    read_site_inputs,
)
from app.scenario.three_answers.result_way_facts import gather_recorded_facts
from app.scenario.three_answers.result_way_inputs import (
    KIND_USER_STATEMENT,
    AreaAgreement,
    Checked,
    Conditional,
    LotType,
    Recorded,
    Withheld,
)
from app.scenario.three_answers.result_ways import decide_result_ways
from app.spatial.lot_reach import CornerReach, LotReach, StreetLineReach
from app.spatial.site_geometry import (
    derive_site_geometry,
    lot_outline_from_mappluto,
    refused_site_geometry,
    street_data_from_pages,
)
from app.spatial.site_geometry.labels import tax_map_value, unknown_value
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
from tests.spatial.test_lot_reach import _lot, _street_for_edge, _streets

from .test_result_way_facts import _profile as _pluto_profile
from .test_result_ways_lib import assert_figures_in_row, plain_inputs, support_all


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Forbid live network egress at the seams where it happens (the accepted journey-test
    pattern): block http.client's connect choke points and socket.create_connection, never
    socket construction (which would deadlock the anyio portal the study read drives)."""

    def _blocked(*_args, **_kwargs):
        raise AssertionError("network I/O attempted in a recorded-data test")

    monkeypatch.setattr(http.client.HTTPConnection, "connect", _blocked)
    monkeypatch.setattr(http.client.HTTPSConnection, "connect", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)


@pytest.fixture(scope="module")
def benchmark_geom():
    """The recorded benchmark lot's profile, prepared outline and site geometry, built offline
    through the real connectors from the recorded pack (no network)."""
    lot, _unused = lot_outline_from_mappluto(replay_lot_geometry())
    streets = street_data_from_pages([replay_dcm_page()], envelope=DCM_ENVELOPE)
    geometry = derive_site_geometry(lot, streets)
    prepared, _reason = prepare_outline(lot)
    profile = build_property_profile(replay_pluto())
    return profile, prepared, geometry


def _benchmark_eval_doc(monkeypatch) -> dict:
    """The evaluator-inputs document for the benchmark lot, built exactly as the journey test
    builds it (the lot type, district and recorded lot area as sourced facts)."""
    setup = _northern_setup(monkeypatch, geometry=True)
    setup["property"]["address"] = _benchmark_identity_address()
    study = study_from_study_setup(
        setup, _TEST_ONLY_OPTION, study_id="study-m5t130-bench", revision=_REVISION
    )
    return build_evaluator_inputs(study, _OPTION_ID)


def _eval_doc(*, district="R6B", lot_type="corner", area=10075.0) -> dict:
    """A small evaluator-inputs document; a value of None omits that key (not given)."""
    rows = []
    if district is not None:
        rows.append({"key": "zoning_district", "value": district, "fact_id": "f-dist"})
    if lot_type is not None:
        rows.append({"key": "lot_type", "value": lot_type, "fact_id": "f-type"})
    if area is not None:
        rows.append({"key": "lot_area_sq_ft", "value": area, "fact_id": "f-area"})
    return {"inputs": rows}


def _way(ways, key):
    return next(row.way for row in ways.result_ways() if row.key == key)


def _bare_profile() -> dict:
    """A fetched profile with every map-based column served empty (so every recorded condition
    is ABSENT: no blanket withhold, no overlay block)."""
    return _pluto_profile({})


def _corner_with_uncertain_frontage():
    """A lot whose site geometry is present but one frontage reach is unknown, built the way
    tests/spatial/test_lot_reach.py::test_uncertain_frontage_reach_is_unknown builds it (the
    First Avenue centre line is 16 ft off, so that frontage is not confirmed and its reach, and
    the corner, are unknown). Returns (prepared outline, geometry)."""
    points = [(0.0, 0.0), (25.0, 0.0), (25.0, 100.0), (0.0, 100.0)]
    main = _street_for_edge("Main Street", (0.0, 0.0), (25.0, 0.0))
    first = _street_for_edge("First Avenue", (0.0, 100.0), (0.0, 0.0), "80", extra_offset=16.0)
    lot = _lot(points)
    geometry = derive_site_geometry(lot, _streets(main, first))
    prepared, _reason = prepare_outline(lot)
    return prepared, geometry


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
def test_benchmark_lot_s1(monkeypatch, benchmark_geom):
    """S1 / work order H2. The entry function, given the recorded benchmark lot and no user
    statement, decides: floor-area figures conditional; height limits conditional; coverage
    withheld with its reason carrying the measured reach (103.93 ft from the 215 Place street
    line); rear yard, setback, building option and unit limits withheld; never a zero."""
    profile, prepared, geometry = benchmark_geom
    doc = _benchmark_eval_doc(monkeypatch)
    res = gather_result_ways(
        evaluator_inputs=doc, profile=profile, outline=prepared, geometry=geometry,
        housing_kind="standard_residence",
    )
    # the gathered recorded facts (S1): overlay present (C2-2); split absent; the rest absent
    assert res.recorded.commercial_overlay.state is Recorded.PRESENT
    assert res.recorded.commercial_overlay.code == "C2-2"
    assert res.recorded.split_by_district_line.state is Recorded.ABSENT
    assert res.recorded.special_purpose_district.state is Recorded.ABSENT
    assert res.recorded.inclusionary_housing_area.state is Recorded.ABSENT
    assert res.recorded.flood_zone.state is Recorded.ABSENT
    assert res.recorded.landmark_or_historic.state is Recorded.ABSENT
    assert res.inputs.lot_type is LotType.CORNER
    # the reach is measured, and equals the corner-reach reference row (parsed, not the module)
    assert_figures_in_row("real-lot-reach", "99.97", "103.93", "144.60")
    reaches = {s.street_name: s.reach.value for s in res.inputs.reach.street_lines}
    assert reaches["Northern Boulevard"] == pytest.approx(99.97, abs=0.01)
    assert reaches["215 Place"] == pytest.approx(103.93, abs=0.01)
    assert res.inputs.reach.corner.reach.value == pytest.approx(144.60, abs=0.01)
    # the two area figures disagree (reading O15): recorded 10,075; outline ~10,388
    assert res.inputs.area.recorded_sq_ft == 10075.0
    assert res.inputs.area.agreement is AreaAgreement.DISAGREES
    # the ways (H2)
    for key in _FLOOR_AREA_KEYS:
        assert isinstance(_way(res.ways, key), Conditional), key
    for key in _HEIGHT_KEYS:
        assert isinstance(_way(res.ways, key), Conditional), key
    coverage = _way(res.ways, "max_lot_coverage")
    assert isinstance(coverage, Withheld)
    assert "103.93 ft" in coverage.reason and "215 Place" in coverage.reason
    for key in _WITHHELD_ON_BENCHMARK:
        assert isinstance(_way(res.ways, key), Withheld), key
    # never a zero: no way carries a number
    for row in res.ways.result_ways():
        assert "value" not in row.way.to_value_state(), row.key
    # the large-lot answer: below the threshold (10,075 < 30,000)
    assert res.large_lot.met is False


# --------------------------------------------------------------------------- S3 the area rule
def test_area_rule_s3():
    """S3 / reading O15: agree only when the outline area rounds to the recorded figure;
    otherwise disagree with both figures carried; could not be compared with no outline; with no
    recorded area the outline's area never stands in."""
    agree, _stmt = compare_lot_area(10075.0, 10075.4)
    assert agree.agreement is AreaAgreement.AGREES
    assert agree.outline_sq_ft == 10075.4

    disagree, stmt = compare_lot_area(10075.0, 10388.0)
    assert disagree.agreement is AreaAgreement.DISAGREES
    assert "10,075" in stmt and "10,388" in stmt  # both figures carried

    no_outline, stmt2 = compare_lot_area(10075.0, None)
    assert no_outline.agreement is AreaAgreement.COULD_NOT_COMPARE
    assert "could not be compared" in stmt2

    no_area, stmt3 = compare_lot_area(None, 10388.0)
    assert no_area.recorded_sq_ft is None and no_area.agreement is None
    assert "never used in its place" in stmt3


# --------------------------------------------------------------------------- O17 the large lot
def test_large_lot_answer_o17():
    """Reading O17: the recorded area against the one captured figure; no recorded area -> not
    stated. Gap K3's figure is 30,000 sq ft, held once with its capture id."""
    assert large_lot_answer(30000.0).met is True
    assert large_lot_answer(29999.0).met is False
    assert large_lot_answer(None).met is None
    assert "not stated" in large_lot_answer(None).statement
    assert LARGE_LOT_THRESHOLD.capture_snapshot_id == "zr-23-362"
    assert LARGE_LOT_THRESHOLD.value == 30000.0
    assert "30,000 square feet" in LARGE_LOT_THRESHOLD.captured_words


# --------------------------------------------------------------------------- S5 a user's statement
def test_user_statement_is_not_a_fact_s5(benchmark_geom):
    """S5 / work order H9: a user's statement that the lot is not in a special density area makes
    the legal unit limit a conditional result naming that statement; without it the result is
    withheld; the statement appears in NO recorded fact."""
    profile, prepared, geometry = benchmark_geom
    doc = _eval_doc()
    with_stmt = gather_result_ways(
        evaluator_inputs=doc, profile=profile, outline=prepared, geometry=geometry,
        housing_kind="standard_residence", special_density_statement=True,
    )
    without = gather_result_ways(
        evaluator_inputs=doc, profile=profile, outline=prepared, geometry=geometry,
        housing_kind="standard_residence", special_density_statement=None,
    )
    unit = _way(with_stmt.ways, "legal_unit_limit_standard")
    assert isinstance(unit, Conditional)
    assert any(c.kind == KIND_USER_STATEMENT for c in unit.conditions)
    assert isinstance(_way(without.ways, "legal_unit_limit_standard"), Withheld)
    # the statement is never stored as a recorded fact
    for fact in with_stmt.recorded.facts():
        assert "density" not in fact.statement.lower()
        assert "states" not in fact.statement.lower()


# --------------------------------------------------------------------------- S6 missing inputs
def test_missing_inputs_one_at_a_time_s6(benchmark_geom):
    """S6 / work order H5: each missing input is carried as not given / not read and never
    filled; the results that depend on it are withheld and the others are unchanged."""
    profile, prepared, geometry = benchmark_geom
    base = dict(profile=profile, outline=prepared, geometry=geometry,
                housing_kind="standard_residence")

    # no district -> every result withheld (a missing district blankets the lot)
    no_district = gather_result_ways(evaluator_inputs=_eval_doc(district=None), **base)
    assert all(isinstance(r.way, Withheld) for r in no_district.ways.result_ways())

    # no lot type -> coverage and rear yard withheld; the floor area is unchanged (conditional)
    no_type = gather_result_ways(evaluator_inputs=_eval_doc(lot_type=None), **base)
    assert no_type.inputs.lot_type is None
    assert isinstance(_way(no_type.ways, "max_lot_coverage"), Withheld)
    assert isinstance(_way(no_type.ways, "rear_yard"), Withheld)
    assert isinstance(_way(no_type.ways, "max_residential_far"), Conditional)

    # no recorded area -> the floor area and unit limit withheld; the large-lot answer not stated
    no_area = gather_result_ways(evaluator_inputs=_eval_doc(area=None), **base)
    assert no_area.inputs.area.recorded_sq_ft is None
    assert isinstance(_way(no_area.ways, "max_residential_far"), Withheld)
    assert no_area.large_lot.met is None

    # no outline -> coverage and rear yard withheld (no reach); the floor area unchanged
    no_outline = gather_result_ways(
        evaluator_inputs=_eval_doc(), profile=profile, outline=None, geometry=None,
        housing_kind="standard_residence",
    )
    assert no_outline.inputs.reach is None
    assert no_outline.inputs.area.agreement is AreaAgreement.COULD_NOT_COMPARE
    assert isinstance(_way(no_outline.ways, "max_lot_coverage"), Withheld)
    assert isinstance(_way(no_outline.ways, "max_residential_far"), Conditional)

    # no profile -> every recorded column not read -> every result withheld
    no_profile = gather_result_ways(
        evaluator_inputs=_eval_doc(), profile=None, outline=prepared, geometry=geometry,
        housing_kind="standard_residence",
    )
    assert no_profile.recorded.special_purpose_district.state is Recorded.NOT_READ
    assert all(isinstance(r.way, Withheld) for r in no_profile.ways.result_ways())


def test_read_site_inputs_states():
    """read_site_inputs carries a missing key as not given and an unrecognised lot type as not
    given (held back), never a default."""
    district, lot_type, area, facts, held = read_site_inputs(_eval_doc())
    assert district == "R6B" and lot_type is LotType.CORNER and area == 10075.0
    assert {f.name for f in facts} == {"zoning district", "lot type", "recorded lot area"}
    assert next(f for f in facts if f.name == "recorded lot area").fact_id == "f-area"

    empty_district, empty_type, empty_area, _facts, _held = read_site_inputs({"inputs": []})
    assert empty_district is None and empty_type is None and empty_area is None

    _d, odd_type, _a, _f, odd_held = read_site_inputs(
        {"inputs": [{"key": "lot_type", "value": "flag", "fact_id": "x"}]})
    assert odd_type is None and odd_held  # an unrecognised lot type is held back, not guessed


def test_density_statement_that_claims_in_one_is_held_back(benchmark_geom):
    """A user's statement that the lot IS in a special density area has no decided path, so it is
    held back and carried as not given (never guessed into a result)."""
    profile, prepared, geometry = benchmark_geom
    res = gather_result_ways(
        evaluator_inputs=_eval_doc(), profile=profile, outline=prepared, geometry=geometry,
        housing_kind="standard_residence", special_density_statement=False,
    )
    assert res.held_back
    assert isinstance(_way(res.ways, "legal_unit_limit_standard"), Withheld)


# --------------------------------------------------------------------------- S7 texts are plain
_FORBIDDEN = (
    "not captured", "uncaptured", "is captured", "milestone", "reference case", "caller",
    "gap-", "gap k", "packet", "work order", "orchestrator",
)
_ID_RE = re.compile(r"\b[KO]\d+\b")


def _texts_of(res) -> list[str]:
    texts = [f.statement for f in res.recorded.facts()]
    texts.append(res.area_statement)
    texts.append(res.large_lot.statement)
    texts.extend(_way_texts(res.ways))
    return texts


def _way_texts(ways) -> list[str]:
    texts: list[str] = []
    for row in ways.result_ways():
        way = row.way
        if isinstance(way, Withheld):
            texts.extend([way.label, way.reason, way.resolved_by])
        elif isinstance(way, Conditional):
            for cond in way.conditions:
                texts.extend([cond.assumption, cond.settled_by])
    for answer in (ways.floor_area_allowance, ways.permitted_envelope, ways.building_option):
        na = answer.whole_answer_not_available
        if na is not None:
            texts.extend([na.reason, na.resolved_by])
    return texts


_PRESENT_PROFILE_COLUMNS = {
    "spdist1": "MX-1", "overlay1": "C2-2", "splitzone": True,
    "mih_opt1": True, "firm07_flag": 1, "landmark": "An Individual Landmark",
}


def _all_returnable_texts(benchmark_geom) -> list[str]:
    """Every text the entry function can return, reaching the families the round-1 battery
    missed (F4): the PRESENT statements of all six recorded conditions; the AGREES and
    could-not-compare area statements; both large-lot statements; and the decision module's way
    texts, including the K20-present branch (DB-172 a) the entry function never produces."""
    profile, prepared, geometry = benchmark_geom
    base = dict(profile=profile, outline=prepared, geometry=geometry,
                housing_kind="standard_residence")
    texts: list[str] = []
    # way texts over a wide entry-function battery (ABSENT / NOT_READ fact statements included)
    for res in (
        gather_result_ways(evaluator_inputs=_eval_doc(), **base),
        gather_result_ways(evaluator_inputs=_eval_doc(), special_density_statement=True, **base),
        gather_result_ways(evaluator_inputs=_eval_doc(district=None), **base),
        gather_result_ways(evaluator_inputs=_eval_doc(area=None), **base),
        gather_result_ways(evaluator_inputs=_eval_doc(lot_type=None), **base),
        gather_result_ways(evaluator_inputs=_eval_doc(), profile=None, outline=prepared,
                           geometry=geometry, housing_kind="standard_residence"),
    ):
        texts.extend(_texts_of(res))
    # F4: the PRESENT statements of all six recorded conditions
    for fact in gather_recorded_facts(_pluto_profile(_PRESENT_PROFILE_COLUMNS)).facts():
        texts.append(fact.statement)
    # F4: every area statement variant and both large-lot statements
    texts.append(compare_lot_area(10075.0, 10075.4)[1])      # AGREES
    texts.append(compare_lot_area(10075.0, 10388.0)[1])      # DISAGREES
    texts.append(compare_lot_area(10075.0, None)[1])         # could-not-compare
    texts.append(compare_lot_area(None, 10388.0)[1])         # no recorded area
    texts.append(large_lot_answer(10075.0).statement)        # below
    texts.append(large_lot_answer(None).statement)           # not stated
    # DB-172 a: one condition with no data source recorded as present (decision module only)
    texts.extend(_way_texts(decide_result_ways(plain_inputs(waterfront=Checked.PRESENT))))
    texts.extend(_way_texts(decide_result_ways(plain_inputs(airport_height=Checked.PRESENT))))
    texts.extend(_way_texts(decide_result_ways(plain_inputs(
        commercial_overlay=Recorded.PRESENT, commercial_overlay_code="C2-2",
        overlay_support=support_all(False)))))
    return texts


def test_every_text_a_user_may_see_is_plain_and_true_s7(benchmark_geom):
    """S7 / rule L3: no returned text names a gap or reading number, an internal word, or a
    claim about which law text is captured. The battery reaches EVERY returnable text family
    (F4): all six conditions' PRESENT/ABSENT/NOT_READ statements, all four area-statement
    variants, both large-lot statements, and the decision module's way texts including the
    'one condition without a data source is recorded as present' branch (DB-172 a)."""
    texts = _all_returnable_texts(benchmark_geom)
    assert len(set(texts)) >= 40, len(set(texts))  # the battery reaches a wide spread of texts
    for text in texts:
        low = text.lower()
        for token in _FORBIDDEN:
            assert token not in low, (token, text)
        assert not _ID_RE.search(text), text


# --------------------------------------------------------------------------- F1 unknown reach
def test_adapt_reach_keeps_an_unknown_measurement_unknown_f1():
    """Packet item (c): 'an unknown measurement stays unknown with its reason'. adapt_reach
    carries a None measurement through as None (None in, None out) and never a zero. The
    expected outcome is the measure function's own unknown result, not this code."""
    measured = LotReach(
        street_lines=(
            StreetLineReach("A", "Street A", unknown_value("ft", "the frontage is not straight")),
            StreetLineReach("B", "Street B", tax_map_value(50.0, "ft", "a measured frontage")),
        ),
        corner=CornerReach(None, None, unknown_value("degrees", "no corner point"), None,
                           unknown_value("ft", "no corner point")),
    )
    adapted = adapt_reach(measured)
    reaches = {s.street_name: s.reach.value for s in adapted.street_lines}
    assert reaches["Street A"] is None          # (a) an unknown street-line reach stays unknown
    assert reaches["Street B"] == 50.0          # a known one is carried verbatim
    assert adapted.corner.reach.value is None   # (b) an unknown corner reach stays unknown
    assert adapted.corner.angle.value is None   # (c) an unknown angle stays unknown


def test_unknown_reach_withholds_coverage_and_rear_yard_f1():
    """Work order gap K12 ('No outline: withheld'): a lot whose site geometry is present but a
    frontage/corner is not measured gives coverage and the rear yard withheld as missing
    information, and never a zero. The geometry is built as the lot-reach suite builds its
    uncertain-frontage case."""
    prepared, geometry = _corner_with_uncertain_frontage()
    res = gather_result_ways(
        evaluator_inputs=_eval_doc(lot_type="corner"), profile=_bare_profile(),
        outline=prepared, geometry=geometry, housing_kind="standard_residence",
    )
    # the uncertain frontage's reach is carried through as unknown, never a zero
    reaches = {s.street_name: s.reach.value for s in res.inputs.reach.street_lines}
    assert reaches["First Avenue"] is None
    assert res.inputs.reach.corner.reach.value is None
    coverage = _way(res.ways, "max_lot_coverage")
    rear_yard = _way(res.ways, "rear_yard")
    assert isinstance(coverage, Withheld) and coverage.gap_kind == "missing_information"
    assert isinstance(rear_yard, Withheld) and rear_yard.gap_kind == "missing_information"
    for row in res.ways.result_ways():
        assert "value" not in row.way.to_value_state(), row.key  # never a zero


# --------------------------------------------------------------------------- F2 interior/through
def test_interior_and_through_lot_types_are_mapped_f2():
    """Packet item (b): the lot type is carried from the evaluator inputs. 'interior' and
    'through' map to their lot types and nothing is held back; the LotType member names are the
    independent anchor (not the mapping dict)."""
    _d, interior, _a, _f, held_i = read_site_inputs(_eval_doc(lot_type="interior"))
    assert interior is LotType.INTERIOR and held_i == ()
    _d, through, _a, _f, held_t = read_site_inputs(_eval_doc(lot_type="through"))
    assert through is LotType.THROUGH and held_t == ()


def test_interior_and_through_lots_withhold_coverage_per_k2_f2():
    """Work order gap K2 ('Withheld until 23-363 is captured and read'): an interior lot and a
    through lot get coverage withheld; the other results are unchanged (the floor area stays
    conditional, as for a corner lot)."""
    base = dict(profile=_bare_profile(), outline=None, geometry=None,
                housing_kind="standard_residence")
    for name in ("interior", "through"):
        res = gather_result_ways(evaluator_inputs=_eval_doc(lot_type=name), **base)
        coverage = _way(res.ways, "max_lot_coverage")
        assert isinstance(coverage, Withheld), name
        assert "ZR 23-363" in coverage.reason and coverage.gap_kind == "work_owed", name
        # the other results are unchanged: the floor area is still conditional
        assert isinstance(_way(res.ways, "max_residential_far"), Conditional), name


# --------------------------------------------------------------------------- F3 four conditions
# The four conditions without a data source, named in work order gap K20 (quoted, not read from
# the code): 'waterfront rules, airport height limits, transit easements, a lot close to a
# district line'.
_K20_CONDITION_NAMES = (
    "waterfront rules", "airport height limits", "transit easements",
    "a lot close to a district line",
)


def test_benchmark_conditional_names_all_four_unchecked_conditions_f3(benchmark_geom):
    """Reading (e) / gap K20: the four conditions with no data source are 'not checked', always.
    The benchmark's floor-area conditional assumption names ALL FOUR, and the entry function has
    no parameter that could mark one as checked."""
    profile, prepared, geometry = benchmark_geom
    res = gather_result_ways(
        evaluator_inputs=_eval_doc(), profile=profile, outline=prepared, geometry=geometry,
        housing_kind="standard_residence",
    )
    far = _way(res.ways, "max_residential_far")
    assert isinstance(far, Conditional)
    assumptions = " ".join(c.assumption for c in far.conditions)
    for name in _K20_CONDITION_NAMES:
        assert name in assumptions, name
    # no parameter of the entry function can mark one of the four as checked
    params = set(inspect.signature(gather_result_ways).parameters)
    assert not (params & {"waterfront", "airport_height", "transit_easement",
                          "near_district_line"})


# --------------------------------------------------------------------------- sweep (point 5)
def test_evaluator_inputs_shape_states():
    """read_site_inputs reaches its shape guards: a non-mapping, a mapping with no 'inputs' key,
    and an 'inputs' that is not a list all give every value not given (never a default)."""
    for doc in (None, {}, {"inputs": "not a list"}, {"inputs": {"key": "x"}}):
        district, lot_type, area, _facts, _held = read_site_inputs(doc)
        assert district is None and lot_type is None and area is None, doc


def test_non_numeric_lot_area_is_carried_as_not_given():
    """A lot_area value that is not a number is carried as not given (never coerced)."""
    doc = {"inputs": [{"key": "lot_area_sq_ft", "value": "10075", "fact_id": "a"}]}
    _d, _t, area, _f, _h = read_site_inputs(doc)
    assert area is None


def test_district_other_than_r6b_withholds_every_result(benchmark_geom):
    """A district other than R6B, carried through the entry function, leaves every result
    withheld (the rules of another district are owed)."""
    profile, prepared, geometry = benchmark_geom
    res = gather_result_ways(
        evaluator_inputs=_eval_doc(district="R5"), profile=_bare_profile(),
        outline=prepared, geometry=geometry, housing_kind="standard_residence",
    )
    assert all(isinstance(r.way, Withheld) for r in res.ways.result_ways())


def test_outline_missing_while_geometry_present():
    """Outline None while geometry is present: the outline area cannot be computed (O15
    could-not-compare) and the reach has no street lines, so coverage is withheld."""
    _prepared, geometry = _corner_with_uncertain_frontage()
    res = gather_result_ways(
        evaluator_inputs=_eval_doc(lot_type="corner"), profile=_bare_profile(),
        outline=None, geometry=geometry, housing_kind="standard_residence",
    )
    assert res.inputs.area.agreement is AreaAgreement.COULD_NOT_COMPARE
    assert res.inputs.reach.street_lines == ()
    assert isinstance(_way(res.ways, "max_lot_coverage"), Withheld)


def test_outline_present_while_geometry_refused():
    """Outline present but the site geometry refused: measure_lot_reach gives no reach, so the
    reach is carried as unknown and coverage/rear yard are withheld (never a zero)."""
    prepared, _geometry = _corner_with_uncertain_frontage()
    refused = refused_site_geometry("the recorded outline was refused for this lot")
    res = gather_result_ways(
        evaluator_inputs=_eval_doc(lot_type="corner"), profile=_bare_profile(),
        outline=prepared, geometry=refused, housing_kind="standard_residence",
    )
    assert res.inputs.reach.street_lines == ()
    assert isinstance(_way(res.ways, "max_lot_coverage"), Withheld)
    assert isinstance(_way(res.ways, "rear_yard"), Withheld)


def test_overlay_code_other_than_c2_2_withholds_residential_results():
    """An overlay recorded present with a code this table does not speak for (not C2-2) leaves
    every residential result withheld (O16: the caller states no support for it)."""
    res = gather_result_ways(
        evaluator_inputs=_eval_doc(), profile=_pluto_profile({"overlay1": "C1-1"}),
        outline=None, geometry=None, housing_kind="standard_residence",
    )
    assert res.recorded.commercial_overlay.state is Recorded.PRESENT
    assert res.recorded.commercial_overlay.code == "C1-1"
    assert isinstance(_way(res.ways, "max_residential_far"), Withheld)
    assert isinstance(_way(res.ways, "min_base_height"), Withheld)
