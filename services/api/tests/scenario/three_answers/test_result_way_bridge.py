"""The entry function carries a lot's recorded facts to the decision module (task M5-T130).

Scenarios S1, S3, S5, S6, S7 and readings O15/O17. Expected OUTCOMES come from the work order's
sentences (quoted beside each test, tests H2/H5/H9 at the level of "the engine's caller, given
this lot, decides these ways"), the corner-reach reference row through the loader, and the
recorded files - never from the module under test. The benchmark lot is assembled offline from
the recorded pack exactly as tests/journey/test_215_16_northern_journey.py assembles it.
"""

from __future__ import annotations

import http.client
import re
import socket

import pytest

from app.contracts.evaluator_inputs import build_evaluator_inputs
from app.contracts.study_setup_bridge import study_from_study_setup
from app.profile.builder import build_property_profile
from app.scenario.three_answers.result_way_bridge import (
    LARGE_LOT_THRESHOLD,
    compare_lot_area,
    gather_result_ways,
    large_lot_answer,
    read_site_inputs,
)
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


def test_every_text_a_user_may_see_is_plain_and_true_s7(benchmark_geom):
    """S7 / rule L3: no returned text names a gap or reading number, an internal word, or a
    claim about which law text is captured. The battery reaches the decision module's texts,
    including the branch 'one condition without a data source is recorded as present'
    (backlog DB-172 a), which the entry function never produces on its own."""
    profile, prepared, geometry = benchmark_geom
    base = dict(profile=profile, outline=prepared, geometry=geometry,
                housing_kind="standard_residence")
    results = [
        gather_result_ways(evaluator_inputs=_eval_doc(), **base),
        gather_result_ways(evaluator_inputs=_eval_doc(), special_density_statement=True, **base),
        gather_result_ways(evaluator_inputs=_eval_doc(district=None), **base),
        gather_result_ways(evaluator_inputs=_eval_doc(area=None), **base),
        gather_result_ways(evaluator_inputs=_eval_doc(lot_type=None), **base),
        gather_result_ways(
            evaluator_inputs=_eval_doc(), profile=None, outline=prepared, geometry=geometry,
            housing_kind="standard_residence"),
    ]
    texts: list[str] = []
    for res in results:
        texts.extend(_texts_of(res))
    # the one condition with no data source recorded as present (DB-172 a): only the decision
    # module produces this text, so reach it directly over a wide battery.
    texts.extend(_way_texts(decide_result_ways(plain_inputs(waterfront=Checked.PRESENT))))
    texts.extend(_way_texts(decide_result_ways(plain_inputs(airport_height=Checked.PRESENT))))
    texts.extend(_way_texts(decide_result_ways(plain_inputs(
        commercial_overlay=Recorded.PRESENT, commercial_overlay_code="C2-2",
        overlay_support=support_all(False)))))
    for text in texts:
        low = text.lower()
        for token in _FORBIDDEN:
            assert token not in low, (token, text)
        assert not _ID_RE.search(text), text
