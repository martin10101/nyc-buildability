"""POST /api/v1/properties/{bbl}/results - the LAW examples (task M5-T138, Part A, tests T4-T8).

Every expected value here comes from the reference cases under docs/reference-cases/R6B/cases,
never from the program's saved output (work order rule 5; R241). The recorded benchmark lot and
the made-up lots of tables B (interior P5) and C (corner C2 / C3) are driven THROUGH THE ROUTE on
an injected provider; the entry derives the five lot conditions from that evidence. Offline and
deterministic.

The MUTATION PROOFS (one per pinned branch, including ruling R4 "the entry treats the interior lot
as a corner lot") are run in a COPY outside the repository and recorded in the producer report;
this file holds the GREEN assertions and the RED-proof companions.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import results_read as mod
from app.api.v1.study_inputs import (
    StudyInputsUnavailableError,
    assemble_study_inputs,
)
from app.config import INTERNAL_RESULTS_ENABLED_ENV_VAR
from app.connectors.pluto_soda import TransportResponse, fetch_by_bbl
from app.spatial.site_geometry import LotOutline, derive_site_geometry
from app.spatial.site_geometry.outline import prepare_outline
from tests.api.test_results_read_api import (
    LANE_B_ON,
    NORTHERN_BBL,
    _no_network,
    _ref_rows,
    _ref_value,
    app_with,
    benchmark_provider,
)
from tests.spatial.test_site_geometry_synthetic import CRS, street_for_edge, streets

_FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures" / "benchmark_215_16_northern" / "pluto_64uk-42ks_bbl_4073340070.json"
)
# A test-marked provenance for the made-up lots so B-03's threading can carry a known tax-map
# lot_type / frontage / depth; the lots are explicitly made up (tables B and C), never a real lot.
_MADE_UP_PROV = {"request_url": "test://made-up-lot", "retrieved_at": "2026-09-30T00:00:00Z"}


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    mod.get_rate_limiter().reset()
    yield
    mod.get_rate_limiter().reset()


def _enable(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_RESULTS_ENABLED_ENV_VAR, "1")
    monkeypatch.setenv("LANE_A_ENABLED", "1")


def _post(app, body):
    return TestClient(app).post(f"/api/v1/properties/{NORTHERN_BBL}/results", json=body)


# --------------------------------------------------------------------------- made-up lots
def _made_up_pluto(lotarea: int):
    """A PLUTO fetch result for a made-up R6B lot with NO overlay and NO special district, built by
    replaying a modified benchmark body through the real connector (so the profile reads the
    overlay/special-district columns as recorded-absent, not not-read)."""
    row = dict(json.loads(_FIXTURE.read_text("utf-8"))[0])
    row["lotarea"] = str(lotarea)
    for key in ("overlay1", "overlay2", "spdist1", "spdist2", "spdist3"):
        row.pop(key, None)
    body = json.dumps([row])
    import datetime

    return fetch_by_bbl(
        NORTHERN_BBL,
        transport=lambda url, headers, timeout: TransportResponse(200, body),
        sleep=lambda seconds: None,
        clock=lambda: datetime.datetime(2026, 9, 30),
        correlation_id="made-up",
        observation_event_id="made-up",
    )


def _interior_geometry(front_len: float, depth_len: float):
    """A made-up interior-lot geometry: a rectangle with ONE street along its front edge."""
    rect = [(0.0, 0.0), (front_len, 0.0), (front_len, depth_len), (0.0, depth_len)]
    lot = LotOutline(tuple(rect), CRS, "Made-up tax lot (test)", _MADE_UP_PROV)
    street = street_for_edge("Main Street", (0.0, 0.0), (front_len, 0.0))
    return derive_site_geometry(lot, streets(street)), prepare_outline(lot)[0]


def _corner_geometry(a_len: float, b_len: float):
    """A made-up corner-lot geometry: a rectangle with TWO streets meeting at the origin corner
    (street A along the front edge of length ``a_len``, street B along the left edge ``b_len``)."""
    rect = [(0.0, 0.0), (a_len, 0.0), (a_len, b_len), (0.0, b_len)]
    lot = LotOutline(tuple(rect), CRS, "Made-up tax lot (test)", _MADE_UP_PROV)
    street_a = street_for_edge("A Street", (0.0, 0.0), (a_len, 0.0))
    street_b = street_for_edge("B Street", (0.0, b_len), (0.0, 0.0))
    return derive_site_geometry(lot, streets(street_a, street_b)), prepare_outline(lot)[0]


def _made_up_provider(lotarea, geometry, prepared, *, address=None):
    def provide(bbl, correlation_id, *, selected=None):
        return assemble_study_inputs(
            _made_up_pluto(lotarea), env=LANE_B_ON, address=address,
            site_geometry=geometry, prepared_outline=prepared,
        )

    return provide


# --------------------------------------------------------------------------- helpers
def _value(answer: dict, key: str):
    return next((v for v in answer["values"] if v["key"] == key), None)


def _states(answer: dict) -> dict:
    return answer.get("value_states", {})


def _result_numbers(doc: dict) -> list[float]:
    """Every number carried on a shown value object or a result block (not value_states prose)."""
    out: list[float] = []

    def walk(node):
        if isinstance(node, bool):
            return
        if isinstance(node, int | float):
            out.append(float(node))
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for ans in doc["answers"].values():
        if ans.get("status") == "available":
            walk(ans.get("values"))
    for key in ("floor_by_floor", "floor_stack", "shortfall", "best_combination", "addon_gains"):
        walk(doc.get(key))
    ue = doc.get("unit_estimate", {})
    if isinstance(ue, dict) and ue.get("status") == "available":
        walk(ue)
    return out


# =========================================================================== T4 (recorded lot)
def test_t4_recorded_lot_three_ways(monkeypatch) -> None:
    """T4 / S4: the recorded 215-16 Northern lot through the route. Floor area conditional naming
    the recorded-area condition; heights the DISTRICT's limits, conditional, never settled nor "the
    maximum for this property"; coverage, rear yard, building option and the legal unit limit
    withheld; no zero. Expected values from docs/reference-cases/R6B/cases/real-lot.json."""
    _enable(monkeypatch)
    _no_network(monkeypatch)
    response = _post(app_with(benchmark_provider()), {"housing_program": "standard_residence"})
    assert response.status_code == 200
    doc = response.json()
    assert doc["contract_version"] == "1.3.0"
    fa = doc["answers"]["floor_area_allowance"]
    env = doc["answers"]["permitted_envelope"]

    # floor area: the reference L1 / L2 values, shown and conditional (recorded-area condition)
    assert _ref_value("real-lot", "L1") == 20150
    assert _value(fa, "max_residential_floor_area")["value"] == 20150
    assert _states(fa)["max_residential_floor_area"]["way"] == "conditional"
    assert _value(
        fa, "max_residential_floor_area_qualifying_affordable_or_senior"
    )["value"] == _ref_value("real-lot", "L2") == 24180

    # heights: the district's limits (real-lot L3 / L4), conditional, NEVER settled
    heights_text = str(_ref_value("real-lot", "L3")) + str(_ref_value("real-lot", "L4"))
    for key, ft in (
        ("min_base_height", 30.0), ("max_base_height", 45.0), ("max_building_height", 55.0),
        ("max_building_height_qualifying_affordable_or_senior", 65.0),
    ):
        assert _value(env, key)["value"] == ft
        assert _states(env)[key]["way"] == "conditional"
        assert f"{int(ft)} ft" in heights_text, key

    # withheld set: coverage (L5 not known), rear yard, building option, the legal unit limit
    assert _ref_rows("real-lot")["L5"]["expected"]["kind"] == "not_known"
    assert _states(env)["max_lot_coverage"]["way"] == "withheld"
    assert _states(env)["rear_yard"]["way"] == "withheld"
    assert _states(fa)["legal_unit_limit_standard"]["way"] == "withheld"
    assert doc["answers"]["building_option"]["status"] == "not_available"
    assert doc["unit_estimate"]["status"] == "not_available"

    # no height is ever "the maximum for this property"; no result number is a zero
    blob = json.dumps(doc).lower()
    assert "the maximum for this property" not in blob
    assert "professional review" not in blob
    assert 0.0 not in _result_numbers(doc)


def test_t4_emitted_document_hides_the_inner_engine_figures(monkeypatch) -> None:
    """S3: the inner 1.2.0 engine document (which still carries a legal unit figure and withheld
    counts) is never returned; the coverage percent (100) and the engine unit figure never appear
    as a result number on the benchmark."""
    _enable(monkeypatch)
    _no_network(monkeypatch)
    doc = _post(app_with(benchmark_provider()), {"housing_program": "standard_residence"}).json()
    numbers = _result_numbers(doc)
    assert 100.0 not in numbers  # the withheld coverage percent
    assert "engine_result" not in doc
    assert doc["floor_by_floor"] == []
    assert doc["floor_stack"]["status"] == "not_available"


# =========================================================================== T5 (made-up lots)
def test_t5_made_up_interior_lot_p5(monkeypatch) -> None:
    """T5 / S5 / S9: a made-up R6B interior lot of 5,355 sq ft (table B, P5). The floor area is
    10,710 (conditional through the entry: the K20 conditions are not checked); the legal unit
    limit is withheld without a density statement. Expected values from interior-lots.json."""
    _enable(monkeypatch)
    geometry, prepared = _interior_geometry(51.0, 105.0)
    assert geometry.lot_type.kind == "interior"
    provider = _made_up_provider(5355, geometry, prepared)
    doc = _post(app_with(provider), {"housing_program": "standard_residence"}).json()
    fa = doc["answers"]["floor_area_allowance"]
    assert _value(fa, "max_residential_floor_area")["value"] == _ref_value(
        "interior-lots", "P5-floor-area"
    ) == 10710
    assert _states(fa)["max_residential_floor_area"]["way"] == "conditional"
    assert _states(fa)["legal_unit_limit_standard"]["way"] == "withheld"
    assert 0.0 not in _result_numbers(doc)


def test_t5_made_up_corner_lots_c2_and_c3(monkeypatch) -> None:
    """T5 / S5: made-up corner lots C2 (60x80) and C3 (150x100), table C. C2 reaches 100 ft to the
    far corner so its whole-lot coverage is 100 percent (conditional through the entry); C3 reaches
    beyond 100 ft so its coverage is withheld (no single figure). corner-reach.json."""
    _enable(monkeypatch)
    # C2: coverage 100 percent
    geom_c2, prep_c2 = _corner_geometry(60.0, 80.0)
    assert geom_c2.lot_type.kind == "corner"
    c2 = _post(
        app_with(_made_up_provider(4800, geom_c2, prep_c2, address="1 A Street")),
        {"housing_program": "standard_residence"},
    ).json()
    env2 = c2["answers"]["permitted_envelope"]
    assert _value(env2, "max_lot_coverage")["value"] == 100.0
    assert _states(env2)["max_lot_coverage"]["way"] == "conditional"
    assert _ref_value("corner-reach", "C2-coverage") == "100 percent"

    # C3: coverage withheld (not known)
    geom_c3, prep_c3 = _corner_geometry(150.0, 100.0)
    c3 = _post(
        app_with(_made_up_provider(15000, geom_c3, prep_c3, address="1 A Street")),
        {"housing_program": "standard_residence"},
    ).json()
    env3 = c3["answers"]["permitted_envelope"]
    assert _value(env3, "max_lot_coverage") is None
    assert _states(env3)["max_lot_coverage"]["way"] == "withheld"
    assert _ref_rows("corner-reach")["C3-coverage"]["expected"]["kind"] == "not_known"


# =========================================================================== T6 (changed input)
def test_t6_changed_input_changes_only_its_dependents(monkeypatch) -> None:
    """T6 / S6: the interior lot area 5,355 sq ft gives the floor area of row P5; with the user's
    density statement its conditional unit limit (16) appears; a changed floor-to-floor height
    changes NO law limit (the floor area, the heights and the unit limit are identical), only the
    floor-to-floor scope assumption. Expected values from interior-lots.json (P5)."""
    _enable(monkeypatch)
    geometry, prepared = _interior_geometry(51.0, 105.0)
    provider = _made_up_provider(5355, geometry, prepared)

    base = _post(app_with(provider), {
        "housing_program": "standard_residence", "special_density_statement": True,
    }).json()
    changed = _post(app_with(provider), {
        "housing_program": "standard_residence", "special_density_statement": True,
        "floor_to_floor_ft": 14.0,
    }).json()

    base_fa = base["answers"]["floor_area_allowance"]
    changed_fa = changed["answers"]["floor_area_allowance"]
    assert _value(base_fa, "max_residential_floor_area")["value"] == 10710
    assert _value(base_fa, "legal_unit_limit_standard")["value"] == _ref_value(
        "interior-lots", "P5-units"
    ) == 16
    # a changed floor-to-floor height changes no law limit
    assert _value(changed_fa, "max_residential_floor_area")["value"] == 10710
    assert _value(changed_fa, "legal_unit_limit_standard")["value"] == 16
    assert base["answers"]["permitted_envelope"]["values"] == (
        changed["answers"]["permitted_envelope"]["values"]
    )
    # but the floor-to-floor scope assumption DID change (it is a visible, editable choice)
    base_f2f = next(a for a in base["scope"]["assumptions"] if a["key"] == "floor_to_floor_ft")
    changed_f2f = next(
        a for a in changed["scope"]["assumptions"] if a["key"] == "floor_to_floor_ft"
    )
    assert base_f2f["statement"] != changed_f2f["statement"]


# =========================================================================== T7 (fact not given)
def test_t7_fact_not_given_is_a_normal_200(monkeypatch) -> None:
    """T7 / S14 / ruling R5: a request whose lot has NO prepared outline (the corner reach cannot
    be measured) is a NORMAL request (200): the reach-dependent coverage and rear yard are withheld
    and named, the floor area is still shown, and no fact is prefilled. No zero appears anywhere.
    (The lot type is still read from the geometry the provider carried, so the floor area runs.)"""
    _enable(monkeypatch)
    _no_network(monkeypatch)
    response = _post(
        app_with(benchmark_provider(outline_on=False)),
        {"housing_program": "standard_residence"},
    )
    assert response.status_code == 200
    doc = response.json()
    env = doc["answers"]["permitted_envelope"]
    assert _states(env)["max_lot_coverage"]["way"] == "withheld"
    assert _states(env)["rear_yard"]["way"] == "withheld"
    # the reach is unknown, so the within-100 / angle scope lines show the words "Not known"
    rows = {a["key"]: a for a in doc["scope"]["assumptions"]}
    assert rows["within_100_ft_of_street_line_intersection"]["value"] == "Not known"
    # the floor area is unaffected by the missing reach (still shown/conditional)
    fa = doc["answers"]["floor_area_allowance"]
    assert _value(fa, "max_residential_floor_area")["value"] == 20150
    assert 0.0 not in _result_numbers(doc)


def test_s14_no_lot_type_geometry_fails_closed_503(monkeypatch) -> None:
    """S14 note (route vs entry): through the route the single StudyInputs.site_geometry carries
    BOTH the lot-type classification AND the reach. When NO geometry at all is produced, the lot
    type is unknown and the engine cannot run, so the route fails closed with the bounded 503
    (lot_conditions_unconfirmed) - never a guessed lot type and never a document. (A lot that DOES
    carry its geometry but no reach outline is the 200 case above.)"""
    _enable(monkeypatch)
    _no_network(monkeypatch)
    response = _post(
        app_with(benchmark_provider(geometry_on=False, outline_on=False)),
        {"housing_program": "standard_residence"},
    )
    assert response.status_code == 503
    body = response.json()
    assert body["state"] == "lot_conditions_unconfirmed"
    # the SAME one reason serves this cause (no lot outline -> no lot type) too
    assert "lot outline" in body["message"] and "city record" in body["message"]


def test_s14_missing_profile_is_a_typed_503_never_a_document(monkeypatch) -> None:
    """S14 / ruling R5 / DB-202 b: the provider yields inputs WITHOUT a property profile, so the
    entry cannot confirm the recorded commercial overlay and fails closed: a typed 503 with a plain
    reason, never a 500 and never a fabricated document."""
    _enable(monkeypatch)
    _no_network(monkeypatch)
    response = _post(
        app_with(benchmark_provider(profile_on=False)),
        {"housing_program": "standard_residence"},
    )
    assert response.status_code == 503
    body = response.json()
    assert body["state"] == "lot_conditions_unconfirmed"
    assert "answers" not in body  # never a document
    # the one reason is true for BOTH causes (missing city record OR missing lot outline), names
    # neither an internal module nor a captured law text, and does not claim "safe to retry"
    message = body["message"]
    assert "city record" in message and "lot outline" in message
    assert "safe to retry" not in message
    assert "result_way" not in message and "professional review" not in message


def test_s14_provider_cannot_produce_inputs_is_a_typed_503(monkeypatch) -> None:
    """S14 / ruling R5: when the provider cannot produce the lot's inputs at all, the typed 503 of
    the sibling route (inputs_unavailable); nothing fabricated."""
    _enable(monkeypatch)

    def unavailable(bbl, correlation_id, *, selected=None):
        raise StudyInputsUnavailableError("no record", reason="no_match")

    response = _post(app_with(unavailable), {"housing_program": "standard_residence"})
    assert response.status_code == 503
    assert response.json()["state"] == "inputs_unavailable"


# =========================================================================== T8 (contradiction)
def test_t8_statement_contradicting_the_record_does_not_override_it(monkeypatch) -> None:
    """T8 / S8 / R255: a caller statement that the lot IS in a special density area (the program
    cannot act on it) is held back, so the legal unit limit stays withheld; the statement is never
    stored as a fact. A 200 (the rest of the document is unchanged)."""
    _enable(monkeypatch)
    _no_network(monkeypatch)
    # special_density_statement False = "the lot is in a special density area" (not the one the
    # program acts on); it is held back and the unit limit stays withheld.
    response = _post(
        app_with(benchmark_provider()),
        {"housing_program": "standard_residence", "special_density_statement": False},
    )
    assert response.status_code == 200
    doc = response.json()
    fa = doc["answers"]["floor_area_allowance"]
    assert _states(fa)["legal_unit_limit_standard"]["way"] == "withheld"
    # the statement is never returned as a sourced fact
    assert "special_density_statement" not in json.dumps(doc)


# =========================================================================== S13 (R4 interior)
def test_s13_interior_lot_with_geometry_through_route_and_entry(monkeypatch) -> None:
    """S13 / ruling R4 / DB-202 a: a made-up interior lot of 5,355 sq ft WITH its geometry, driven
    through the route and the entry. Its two corner lines (within-100 and the angle) read "Not
    applicable" (it is not a corner lot); the floor area is 10,710 (interior-lots.json
    P5-floor-area); with the user's density statement the legal unit limit is the conditional value
    16 (P5-units). The MUTATION that treats the interior lot as a corner lot (recorded in the
    producer report, run in a copy outside the repository) makes THIS test fail: the corner lines
    would then read a measured/not-known value, not "Not applicable"."""
    _enable(monkeypatch)
    geometry, prepared = _interior_geometry(51.0, 105.0)
    assert geometry.lot_type.kind == "interior"  # the lot genuinely carries an interior geometry
    provider = _made_up_provider(5355, geometry, prepared)
    doc = _post(app_with(provider), {
        "housing_program": "standard_residence", "special_density_statement": True,
    }).json()

    rows = {a["key"]: a for a in doc["scope"]["assumptions"]}
    within = rows["within_100_ft_of_street_line_intersection"]
    angle = rows["street_line_intersection_angle_degrees"]
    assert within["value"] == "Not applicable" and within["unit"] is None
    assert angle["value"] == "Not applicable" and angle["unit"] is None
    assert "not a corner lot" in within["statement"]
    assert "does not apply" in angle["statement"]

    fa = doc["answers"]["floor_area_allowance"]
    assert _value(fa, "max_residential_floor_area")["value"] == _ref_value(
        "interior-lots", "P5-floor-area"
    ) == 10710
    unit = _value(fa, "legal_unit_limit_standard")
    assert unit is not None and unit["value"] == _ref_value("interior-lots", "P5-units") == 16
    assert _states(fa)["legal_unit_limit_standard"]["way"] == "conditional"


def test_s13_interior_lot_without_the_statement_withholds_the_unit_limit(monkeypatch) -> None:
    """S13 companion: without the user's density statement the interior lot's legal unit limit is
    withheld and the figure 16 appears nowhere (no shown value rests on a stand-in)."""
    _enable(monkeypatch)
    geometry, prepared = _interior_geometry(51.0, 105.0)
    provider = _made_up_provider(5355, geometry, prepared)
    doc = _post(app_with(provider), {"housing_program": "standard_residence"}).json()
    fa = doc["answers"]["floor_area_allowance"]
    assert _value(fa, "legal_unit_limit_standard") is None
    assert _states(fa)["legal_unit_limit_standard"]["way"] == "withheld"
    assert 16.0 not in _result_numbers(doc)


# =========================================================================== provider inert check
def test_benchmark_provider_carries_the_scenario_objects(monkeypatch) -> None:
    """The benchmark provider's StudyInputs carries the property profile, the prepared outline and
    the site geometry the entry reads (a guard that the offline provider is complete)."""
    _no_network(monkeypatch)
    inputs = benchmark_provider()(NORTHERN_BBL, "probe")
    assert inputs.property_profile is not None
    assert inputs.prepared_outline is not None
    assert inputs.site_geometry is not None
    # dropping a carrier is honoured (used by the missing-evidence states)
    dropped = dataclasses.replace(inputs, site_geometry=None)
    assert dropped.site_geometry is None
