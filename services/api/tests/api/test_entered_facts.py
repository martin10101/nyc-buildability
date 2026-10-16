"""Architect-entered-fact channel for the results route (task M5-T178; D-094-R103, R285).

The acceptance pack S1-S8 for :mod:`app.api.v1.entered_facts` and its wiring through
``app.api.v1.results_request`` / ``app.api.v1.results_read``: an architect's SURVEY
measurement of a lot value (area, frontage, depth) becomes a ``survey_entered`` site fact
that GOVERNS its engine input and keeps the city fact visible in ``displaced``; a malformed
block is a typed 422 at the body gate; an unplaceable value fails closed to the existing
``lot_conditions_unconfirmed`` 503; and an absent channel leaves the document byte-identical
to the city-record baseline.

Offline and deterministic. The route tests drive the same injected benchmark provider the
sibling wiring tests use (no network); the channel/evaluator tests reuse the proven study and
fact builders from ``tests.contracts.test_evaluator_inputs``.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from app.api.v1.entered_facts import (
    EnteredFact,
    EnteredFactsError,
    merge_entered_facts,
    parse_entered_facts,
)
from app.api.v1.results_request import ResultsRequestError, read_results_request
from app.contracts.evaluator_inputs import build_evaluator_inputs
from app.contracts.study_contracts import validate_study_document
from app.scenario.three_answers import build_status_strip
from tests.api.test_results_read_api import (
    NORTHERN_BBL,
    _no_network,
    app_with,
    benchmark_provider,
)
from tests.contracts.test_evaluator_inputs import (
    _SURVEY,
    _benchmark_city_facts,
    _fact,
    _record,
    _study,
)

_STD = {"housing_program": "standard_residence"}
_RETRIEVED = "2026-10-08T00:00:00Z"
_IDENTITY_FIELDS = ("results_id", "study_id", "option_id", "computed_at")


def _post(provider, body):
    return TestClient(app_with(provider)).post(
        f"/api/v1/properties/{NORTHERN_BBL}/results", json=body
    )


def _blank_identity(doc: dict) -> dict:
    out = json.loads(json.dumps(doc))
    for key in _IDENTITY_FIELDS:
        out[key] = "<id>"
    return out


def _floor_area(doc: dict) -> float:
    fa = doc["answers"]["floor_area_allowance"]
    return next(
        v["value"] for v in fa["values"] if v["key"] == "max_residential_floor_area"
    )


@pytest.fixture
def enabled(monkeypatch):
    from app.config import INTERNAL_RESULTS_ENABLED_ENV_VAR

    monkeypatch.setenv(INTERNAL_RESULTS_ENABLED_ENV_VAR, "1")
    monkeypatch.setenv("LANE_A_ENABLED", "1")
    return monkeypatch


# ===========================================================================
# S1: no entered_facts -> byte-identical to the city-record baseline
# ===========================================================================
@pytest.mark.parametrize("extra", [None, {"entered_facts": None}, {"entered_facts": []}])
def test_s1_absent_channel_is_byte_identical_to_the_city_baseline(enabled, monkeypatch, extra):
    """S1: a body with NO entered_facts (or null, or an empty list) yields a document
    byte-identical (apart from the server-minted id/time fields) to the city-record baseline;
    the status chip stays 'Approximate measurements' and the floor-area answer rests on the
    city lot area (2.00 x 10,075 = 20,150)."""
    _no_network(monkeypatch)
    baseline = _post(benchmark_provider(), dict(_STD)).json()
    body = dict(_STD)
    if extra is not None:
        body.update(extra)
    got = _post(benchmark_provider(), body).json()
    assert _blank_identity(got) == _blank_identity(baseline)
    assert baseline["status_strip"][1] == {"text": "Approximate measurements"}
    assert _floor_area(baseline) == 2.0 * 10075  # the city-record lot area governs


# ===========================================================================
# S2: a survey lot area governs and displaces the city fact (live route)
# ===========================================================================
def test_s2_survey_lot_area_governs_and_recomputes_the_results(enabled, monkeypatch):
    """S2: entered_facts [{input:'lot_area', value:10388, basis:'survey'}] against the benchmark
    whose PLUTO lot area is 10,075 -> the floor-area answer recomputes from the SURVEY value
    (2.00 x 10,388 = 20,776), not the city value, and no answer is relabelled 'City records'."""
    _no_network(monkeypatch)
    body = dict(_STD, entered_facts=[{"input": "lot_area", "value": 10388, "basis": "survey"}])
    response = _post(benchmark_provider(), body)
    assert response.status_code == 200
    doc = response.json()
    assert _floor_area(doc) == 2.0 * 10388  # 20,776: the survey value fed the result
    assert _floor_area(doc) != 2.0 * 10075  # NOT the city value


def test_s2_survey_lot_area_is_the_governing_record_city_in_displaced(enabled, monkeypatch):
    """S2 (channel/evaluator level): the merged study's governing lot_area record is the
    survey_entered fact (value 10,388, source kind survey) and the PLUTO 10,075 fact travels in
    its `displaced`, intact and never overwritten."""
    _no_network(monkeypatch)
    provider = benchmark_provider()
    inputs = provider(NORTHERN_BBL, "ref")
    from app.api.v1.results_request import build_option
    from app.api.v1.study_setup_document import build_study_setup_document
    from app.contracts.study_setup_bridge import study_from_study_setup

    setup = build_study_setup_document(NORTHERN_BBL, inputs)
    req = read_results_request(
        dict(_STD, entered_facts=[{"input": "lot_area", "value": 10388, "basis": "survey"}])
    )
    option = build_option(req, option_id="opt-x")
    study = study_from_study_setup(
        setup, option, study_id="s",
        revision={"number": 1, "created_at": _RETRIEVED, "parent": None},
    )
    merged = merge_entered_facts(study, req.entered_facts, retrieved_at=_RETRIEVED)
    assert len(study["site"]["facts"]) + 1 == len(merged["site"]["facts"])  # study not mutated
    doc = build_evaluator_inputs(merged, "opt-x")
    area = _record(doc, "lot_area_sq_ft")
    assert area["rank"] == "survey_entered"
    assert area["label"] == "Survey (entered)"
    assert area["value"] == 10388.0
    assert area["source_kind"] == "survey"
    assert area["displaced"] == [
        {"fact_id": "4073340070:lot_area", "rank": "city_records",
         "label": "City records", "value": 10075}
    ]


# ===========================================================================
# S3: a survey frontage governs and displaces the recorded frontage
# ===========================================================================
def test_s3_survey_frontage_governs_and_displaces_the_recorded_frontage():
    """S3: on a single-frontage lot a survey lot_frontage governs lot_front_ft and the recorded
    frontage travels in `displaced`, intact; the city fact stays visible."""
    study = _study(_benchmark_city_facts())  # one Northern Boulevard frontage (city_records)
    city_front = _record(build_evaluator_inputs(study, "opt-1"), "lot_front_ft")
    merged = merge_entered_facts(
        study, (EnteredFact(input="lot_frontage", value=105.0, basis="survey"),),
        retrieved_at=_RETRIEVED,
    )
    front = _record(build_evaluator_inputs(merged, "opt-1"), "lot_front_ft")
    assert front["rank"] == "survey_entered"
    assert front["value"] == 105.0
    assert front["source_kind"] == "survey"
    assert {d["fact_id"] for d in front["displaced"]} == {city_front["fact_id"]}
    assert front["displaced"][0]["value"] == city_front["value"]  # city frontage intact


# ===========================================================================
# S4: duplicate input -> 422 at the gate; unplaceable survey value -> 503
# ===========================================================================
def test_s4_duplicate_input_is_422_at_the_body_gate(enabled):
    """S4: the SAME input entered twice is a typed 422 at the body gate (the conflict is visible,
    never a silent pick), and the provider is never reached."""
    calls = []

    def spy(bbl, correlation_id, *, selected=None):
        calls.append(bbl)
        raise AssertionError("provider must not be reached on a refused body")

    body = dict(_STD, entered_facts=[
        {"input": "lot_area", "value": 10, "basis": "survey"},
        {"input": "lot_area", "value": 20, "basis": "survey"},
    ])
    response = _post(spy, body)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "entered_fact_duplicate_input"
    assert detail["field"] == "input"
    assert calls == []


def test_s4_unplaceable_survey_value_fails_closed_to_503(enabled, monkeypatch):
    """S4: a survey lot_frontage against the benchmark CORNER lot (two recorded frontages, so
    which the survey replaces is not settled) fails closed to the existing lot_conditions
    503 - never a guess and never a fabricated document."""
    _no_network(monkeypatch)
    body = dict(_STD, entered_facts=[{"input": "lot_frontage", "value": 101, "basis": "survey"}])
    response = _post(benchmark_provider(), body)
    assert response.status_code == 503
    assert response.json()["state"] == "lot_conditions_unconfirmed"


def test_s4_entered_fact_for_an_input_with_no_recorded_value_fails_closed():
    """S4 (channel level): an entered value for an input the lot has NO recorded value for has
    nothing to sit beside, so the merge raises (fail closed) rather than invent a lone fact."""
    facts = [f for f in _benchmark_city_facts() if f["key"] != "lot_depth"]
    study = _study(facts)
    with pytest.raises(EnteredFactsError, match="cannot be applied"):
        merge_entered_facts(
            study, (EnteredFact(input="lot_depth", value=99.0, basis="survey"),),
            retrieved_at=_RETRIEVED,
        )


# ===========================================================================
# S5: a bare lot fact is still refused; the message names the entered_facts channel
# ===========================================================================
@pytest.mark.parametrize(
    "field,value",
    [("lot_area_sq_ft", 5000), ("lot_type", "corner"), ("bbl", NORTHERN_BBL)],
)
def test_s5_bare_lot_fact_is_still_refused(enabled, field, value):
    """S5: a RAW lot fact in the body is still refused with a typed 422 field_not_accepted
    (T10 preserved); the ONLY way a lot measure enters is the provenance-tagged channel."""
    response = _post(_spy_provider(), dict(_STD, **{field: value}))
    assert response.status_code == 422
    assert response.json()["detail"]["field"] == field


def test_s5_refusal_message_distinguishes_the_entered_facts_channel(enabled):
    """S5: the refusal message now names the accepted entered_facts channel, distinguishing it
    from a bare lot fact (which is still refused)."""
    response = _post(_spy_provider(), dict(_STD, lot_area_sq_ft=5000))
    assert response.status_code == 422
    assert "entered_facts" in response.json()["message"]


def _spy_provider():
    def spy(bbl, correlation_id, *, selected=None):
        raise AssertionError("provider must not be reached on a refused body")

    return spy


# ===========================================================================
# S6: value / basis / input validation (mirrors floor_to_floor_ft)
# ===========================================================================
@pytest.mark.parametrize(
    "block,code",
    [
        ([{"input": "lot_area", "value": 0, "basis": "survey"}], "entered_fact_value_invalid"),
        ([{"input": "lot_area", "value": -5, "basis": "survey"}], "entered_fact_value_invalid"),
        ([{"input": "lot_area", "basis": "survey"}], "entered_fact_value_invalid"),
        ([{"input": "lot_area", "value": "ten", "basis": "survey"}], "entered_fact_value_invalid"),
        ([{"input": "lot_area", "value": 10, "basis": "deed"}], "entered_fact_basis_invalid"),
        ([{"input": "floor_area", "value": 10, "basis": "survey"}], "entered_fact_input_invalid"),
        ([{"input": "lot_area", "value": 10}], "entered_fact_basis_invalid"),
        ([{"value": 10, "basis": "survey"}], "entered_fact_input_invalid"),
        ([{"input": "lot_area", "value": 10, "basis": "survey", "x": 1}],
         "entered_fact_field_not_accepted"),
        ("not-a-list", "entered_facts_invalid"),
        ([5], "entered_fact_invalid"),
    ],
)
def test_s6_bad_block_raises_with_its_specific_code(block, code):
    """S6: each malformed entered_facts shape raises EnteredFactsError with its specific code -
    a non-positive / non-finite / missing / non-numeric value, a basis or input outside the
    closed enums, an unexpected key, a non-list block, a non-object entry."""
    with pytest.raises(EnteredFactsError) as excinfo:
        parse_entered_facts(block)
    assert excinfo.value.code == code


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
def test_s6_non_finite_value_is_422_not_500(enabled, token):
    """S6: a raw JSON NaN/Infinity token in a value is a typed 422 at the body gate (never a
    500), mirroring the floor_to_floor_ft guard."""
    raw = (
        '{"housing_program": "standard_residence", "entered_facts": '
        '[{"input": "lot_area", "value": ' + token + ', "basis": "survey"}]}'
    )
    response = TestClient(app_with(_spy_provider())).post(
        f"/api/v1/properties/{NORTHERN_BBL}/results", content=raw
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "entered_fact_value_invalid"


def test_s6_present_value_is_never_confused_with_an_absent_channel():
    """S6: presence is tested with `in` - a present value of 0 is a value that is then refused,
    never read as an absent channel; an absent channel is the empty tuple."""
    assert read_results_request(dict(_STD)).entered_facts == ()
    assert read_results_request(dict(_STD, entered_facts=None)).entered_facts == ()
    with pytest.raises(ResultsRequestError):
        read_results_request(dict(_STD, entered_facts=[{"input": "lot_area", "value": 0,
                                                        "basis": "survey"}]))


# ===========================================================================
# S7: the merged study and the evaluator inputs validate against their contracts
# ===========================================================================
def test_s7_merged_study_and_evaluator_inputs_validate():
    """S7: the merged study still validates against study.schema.json (the added survey fact
    carries its fact_id, key, value, measurement{survey_entered, 'Survey (entered)'} and a
    source{kind survey, document_ref + statement}); build_evaluator_inputs produces a valid
    document whose governing lot record is survey_entered with the city fact in `displaced`."""
    study = _study(_benchmark_city_facts())
    merged = merge_entered_facts(
        study, (EnteredFact(input="lot_area", value=10388.0, basis="survey"),),
        retrieved_at=_RETRIEVED,
    )
    validate_study_document(merged)  # fails closed if the minted fact is malformed
    survey = next(
        f for f in merged["site"]["facts"]
        if f["key"] == "lot_area" and f["measurement"]["rank"] == "survey_entered"
    )
    assert survey["source"]["kind"] == "survey"
    assert survey["source"]["document_ref"]
    assert survey["source"]["statement"]
    assert survey["measurement"] == {"rank": "survey_entered", "label": "Survey (entered)"}
    doc = build_evaluator_inputs(merged, "opt-1")
    area = _record(doc, "lot_area_sq_ft")
    assert area["rank"] == "survey_entered"
    assert area["displaced"][0]["rank"] == "city_records"


# ===========================================================================
# S8: the weakest governing rank drives the status chip
# ===========================================================================
def _survey_site_fact(key, value, fact_id, *, street=None):
    return _fact(key, value, "survey_entered", fact_id, _SURVEY, street=street)


def test_s8_all_survey_inputs_make_the_survey_measurements_chip():
    """S8: when every governing engine input is survey_entered (the three measures entered by
    survey, beside survey lot_type and district) the channel's survey facts make the weakest
    governing rank survey_entered, so the status chip reads 'Survey measurements'."""
    base = [
        _fact("lot_area", 10075, "city_records", "f-area-city",
              _benchmark_city_facts()[0]["source"]),
        _fact("lot_frontage", 100.76, "city_records", "f-front-city",
              _benchmark_city_facts()[0]["source"], street="Northern Boulevard"),
        _fact("lot_depth", 100.0, "city_records", "f-depth-city",
              _benchmark_city_facts()[0]["source"]),
        _survey_site_fact("lot_type", "corner", "f-type-survey"),
        _survey_site_fact("zoning_district", "R6B", "f-zd-survey"),
    ]
    merged = merge_entered_facts(
        _study(base),
        (
            EnteredFact(input="lot_area", value=10388.0, basis="survey"),
            EnteredFact(input="lot_frontage", value=105.0, basis="survey"),
            EnteredFact(input="lot_depth", value=99.0, basis="survey"),
        ),
        retrieved_at=_RETRIEVED,
    )
    doc = build_evaluator_inputs(merged, "opt-1")
    assert doc["site_measurement_rank"] == "survey_entered"
    assert build_status_strip(doc["site_measurement_rank"])[1] == {"text": "Survey measurements"}


def test_s8_one_survey_value_governs_but_a_city_input_keeps_approximate():
    """S8: a single survey value governs its own input yet a remaining city_records input keeps
    the document-wide chip 'Approximate measurements' (the weakest governing rank wins the
    label; the existing survey-governs-but-does-not-weaken invariant holds)."""
    merged = merge_entered_facts(
        _study(_benchmark_city_facts()),
        (EnteredFact(input="lot_area", value=10388.0, basis="survey"),),
        retrieved_at=_RETRIEVED,
    )
    doc = build_evaluator_inputs(merged, "opt-1")
    assert _record(doc, "lot_area_sq_ft")["rank"] == "survey_entered"  # the survey value governs
    assert doc["site_measurement_rank"] == "city_records"  # the weakest remaining input
    assert build_status_strip(doc["site_measurement_rank"])[1] == {
        "text": "Approximate measurements"
    }
