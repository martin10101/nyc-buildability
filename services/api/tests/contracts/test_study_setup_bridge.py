"""Tests for the study-read -> engine bridge (task C-07 adapter gap; journey plan
docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md link 4, wave 1 item 6; D-090 R109).

``app.contracts.study_setup_bridge.study_from_study_setup`` turns the ``study_setup``
document ``GET /api/v1/properties/{bbl}/study`` returns into a document that validates
against the ``study`` contract, so the already-accepted C-07 adapter
(``build_evaluator_inputs`` / ``build_three_answer_inputs``) and the Lane A engine
(``generate_results``) can consume the live read instead of the hard-coded
``_benchmark_inputs`` site values.

The 215-16 Northern study read is produced OFFLINE, reusing the recorded-fixture
helpers from the accepted study-read tests by import (never restated):
- ``tests.api.test_study_geometry`` serves the read WITH B-03 geometry (PR #390:
  ``lot_type`` corner, per-street frontage facts) and WITHOUT it (``lot_type`` unknown);
- ``tests.api.test_study_read_api._TEST_ONLY_OPTION`` is the test-fixture-synthetic
  option (the backend never invents option inputs; plan M1-06);
- ``tests.contracts.test_evaluator_inputs`` provides the benchmark site-fact helpers
  the accepted C-07 golden test uses.

HONEST LIMIT proven below: with B-03 geometry the live Northern read is a CORNER lot
carrying TWO ``lot_frontage`` facts (one per street). ``build_evaluator_inputs`` fails
closed on that (collapsing several frontages is the combined-outline rule, plan
section 4 'Multi-lot sites', out of C-07's scope and pinned by
``test_evaluator_inputs.test_multi_street_frontage_is_not_guessed``). So the bridge
closes the SHAPE + ``lot_type`` adapter gap, but the live corner read cannot yet run
the engine through the frontage input; the engine-run test below proves the bridged
study IS engine-compatible on a single-frontage fact set (the accepted C-07 golden
path), reproducing the golden allowance.
"""

from __future__ import annotations

import copy

import pytest

from app.api.v1.study_read import get_rate_limiter
from app.config import INTERNAL_STUDY_READ_ENABLED_ENV_VAR
from app.contracts.evaluator_inputs import (
    EvaluatorInputsError,
    build_evaluator_inputs,
    build_three_answer_inputs,
)
from app.contracts.study_contracts import (
    StudyContractError,
    validate_evaluator_inputs_document,
    validate_results_document,
    validate_study_document,
)
from app.contracts.study_setup_bridge import (
    STUDY_CONTRACT_VERSION,
    StudySetupBridgeError,
    study_from_study_setup,
)
from app.scenario.three_answers import generate_results
from app.scenario.three_answers.scope import ASSUMPTION_KEYS
from app.spatial.site_geometry.results import LOT_TYPE_CORNER
from tests.api.test_study_geometry import (
    NORTHERN_BBL,
    _benchmark_geometry,
    _client,
    _geometry_provider,
    _provider,
)
from tests.api.test_study_read_api import _TEST_ONLY_OPTION
from tests.contracts.test_evaluator_inputs import (
    _benchmark_city_facts,
    _benchmark_identity_address,
    _benchmark_value,
    _three_answer_inputs,
)

_OPTION_ID = _TEST_ONLY_OPTION["option_id"]
# Revision 1 (no parent); created_at is a caller input - the bridge invents no timestamp.
_REVISION = {"number": 1, "created_at": "2026-09-30T12:00:00Z", "parent": None}
_LANE_ON = {"LANE_A_ENABLED": "1"}


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """The study-read route's per-caller limiter is process-wide module state; reset it
    around every test so cases do not accumulate stamps into a spurious 429 (the same
    pattern the imported study-read suites use)."""
    get_rate_limiter().reset()
    yield
    get_rate_limiter().reset()


def _northern_setup(monkeypatch, *, geometry: bool) -> dict:
    """The 215-16 Northern study_setup read, produced offline through the route.
    ``geometry`` True injects the recorded B-03 geometry (corner lot_type + frontages);
    False is the pre-geometry read (lot_type unknown, no frontage facts)."""
    monkeypatch.setenv(INTERNAL_STUDY_READ_ENABLED_ENV_VAR, "1")
    provider = (
        _provider(_geometry_provider(_benchmark_geometry())) if geometry else _provider()
    )
    response = _client(provider).get(f"/api/v1/properties/{NORTHERN_BBL}/study")
    assert response.status_code == 200, response.status_code
    return response.json()


def _fact(study: dict, key: str, *, street=None) -> dict:
    """The ONE site fact with this key (and street); the fact VALUES asserted against
    are read from the study document, never retyped as literals."""
    facts = [
        f
        for f in study["site"]["facts"]
        if f["key"] == key and f.get("street") == street
    ]
    assert len(facts) == 1, (key, street, len(facts))
    return facts[0]


def _input(doc: dict, engine_key: str) -> dict:
    return next(r for r in doc["inputs"] if r["key"] == engine_key)


# ---------------------------------------------------------------------------
# (a) The bridge: study_setup -> a document that validates as a study
# ---------------------------------------------------------------------------
def test_bridge_without_geometry_validates_and_carries_facts_verbatim(monkeypatch) -> None:
    setup = _northern_setup(monkeypatch, geometry=False)
    study = study_from_study_setup(
        setup, _TEST_ONLY_OPTION, study_id="study-northern-w1-06", revision=_REVISION
    )
    validate_study_document(study)  # reaching here = the bridge output is contract-valid

    assert study["contract_version"] == STUDY_CONTRACT_VERSION == "1.0.0"
    # The read-only markers are dropped; they are not study fields.
    assert "document_kind" not in study
    assert "bbl" not in study
    # property / lots / lot_selection / site carried VERBATIM, and NOT aliased (pure).
    assert study["property"] == setup["property"]
    assert study["lots"] == setup["lots"]
    assert study["lot_selection"] == setup["lot_selection"]
    assert study["site"] == setup["site"]  # every site fact verbatim, none dropped
    assert study["site"] is not setup["site"]
    # Nothing pre-selected: the one explicit option is the whole option set.
    assert study["options"] == [_TEST_ONLY_OPTION]
    assert study["selected_option_id"] == _OPTION_ID
    # study_id / revision are the caller's explicit inputs, carried unchanged.
    assert study["study_id"] == "study-northern-w1-06"
    assert study["revision"] == _REVISION
    # A live-read bridge is a NEW study, never an export restore.
    assert study["origin"] == {"kind": "new", "export_id": None}


def test_bridge_with_geometry_carries_corner_lot_type_and_both_frontages(monkeypatch) -> None:
    setup = _northern_setup(monkeypatch, geometry=True)
    study = study_from_study_setup(
        setup, _TEST_ONLY_OPTION, study_id="study-northern-geo", revision=_REVISION
    )
    validate_study_document(study)
    assert study["site"] == setup["site"]  # verbatim: both frontages + corner lot_type

    lot_type = _fact(study, "lot_type")
    assert lot_type["value"] == LOT_TYPE_CORNER == "corner"
    assert lot_type["measurement"]["rank"] == "approximate_tax_map"

    frontages = [f for f in study["site"]["facts"] if f["key"] == "lot_frontage"]
    setup_frontages = [f for f in setup["site"]["facts"] if f["key"] == "lot_frontage"]
    assert len(frontages) == 2  # a corner lot: one per street
    assert frontages == setup_frontages  # carried verbatim, ranks untouched


def test_bridge_does_not_mutate_the_read(monkeypatch) -> None:
    setup = _northern_setup(monkeypatch, geometry=True)
    snapshot = copy.deepcopy(setup)
    study_from_study_setup(setup, _TEST_ONLY_OPTION, study_id="s", revision=_REVISION)
    assert setup == snapshot  # the input read is untouched (pure)


def test_unexpected_setup_field_stops_and_is_named(monkeypatch) -> None:
    # A top-level field the study contract cannot carry is NAMED and refused, never
    # silently dropped (requirement a: STOP and report; contract changes are their own PR).
    setup = _northern_setup(monkeypatch, geometry=False)
    setup["frontage_summary"] = {"note": "a field no study field carries"}
    with pytest.raises(StudySetupBridgeError, match="frontage_summary"):
        study_from_study_setup(setup, _TEST_ONLY_OPTION, study_id="s", revision=_REVISION)


def test_non_study_setup_document_is_rejected() -> None:
    with pytest.raises(StudySetupBridgeError, match="not a study-read document"):
        study_from_study_setup(
            {"document_kind": "study"}, _TEST_ONLY_OPTION, study_id="s", revision=_REVISION
        )


def test_missing_carried_subobject_is_rejected(monkeypatch) -> None:
    setup = _northern_setup(monkeypatch, geometry=False)
    del setup["site"]
    with pytest.raises(StudySetupBridgeError, match="missing required sub-object"):
        study_from_study_setup(setup, _TEST_ONLY_OPTION, study_id="s", revision=_REVISION)


def test_top_level_bbl_mismatch_is_rejected(monkeypatch) -> None:
    setup = _northern_setup(monkeypatch, geometry=False)
    setup["bbl"] = "1000010001"  # disagrees with property.bbl
    with pytest.raises(StudySetupBridgeError, match="does not match property.bbl"):
        study_from_study_setup(setup, _TEST_ONLY_OPTION, study_id="s", revision=_REVISION)


def test_option_without_option_id_is_rejected(monkeypatch) -> None:
    setup = _northern_setup(monkeypatch, geometry=False)
    bad_option = {k: v for k, v in _TEST_ONLY_OPTION.items() if k != "option_id"}
    with pytest.raises(StudySetupBridgeError, match="option_id"):
        study_from_study_setup(setup, bad_option, study_id="s", revision=_REVISION)


def test_invalid_revision_fails_the_study_contract(monkeypatch) -> None:
    # The bridge re-validates its output: a revision 2 with no parent violates the study
    # contract oneOf, so the bridge fails closed rather than emitting an invalid study.
    setup = _northern_setup(monkeypatch, geometry=False)
    with pytest.raises(StudyContractError):
        study_from_study_setup(
            setup,
            _TEST_ONLY_OPTION,
            study_id="s",
            revision={"number": 2, "created_at": "2026-09-30T12:00:00Z", "parent": None},
        )


# ---------------------------------------------------------------------------
# (b) The bridged study feeds the C-07 adapter: the live read's sourced facts,
# not the hard-coded _benchmark_inputs, now govern the engine inputs.
# ---------------------------------------------------------------------------
def test_without_geometry_governing_facts_flow_but_unknown_lot_type_fails_closed(
    monkeypatch,
) -> None:
    setup = _northern_setup(monkeypatch, geometry=False)
    study = study_from_study_setup(setup, _TEST_ONLY_OPTION, study_id="s", revision=_REVISION)

    doc = build_evaluator_inputs(study, _OPTION_ID)
    validate_evaluator_inputs_document(doc)
    assert doc["contract_version"] == "1.0.0"  # no existing_building plan

    # Each governing input value/rank comes from the study read's facts (not literals).
    for engine_key, fact_key in (
        ("lot_area_sq_ft", "lot_area"),
        ("lot_depth_ft", "lot_depth"),
        ("zoning_district", "zoning_district"),
    ):
        record = _input(doc, engine_key)
        fact = _fact(study, fact_key)
        assert record["value"] == fact["value"]
        assert record["rank"] == fact["measurement"]["rank"] == "city_records"
        assert record["fact_id"] == fact["fact_id"]
    # lot_area is the recorded 10,075 sq ft city-records value (sanity, from the fact).
    assert _input(doc, "lot_area_sq_ft")["value"] == _fact(study, "lot_area")["value"] == 10075
    # lot_type is unknown without geometry, so it is NOT a governing input.
    assert all(r["key"] != "lot_type" for r in doc["inputs"])

    # The pair fails closed with the existing typed error: the evaluator cannot answer
    # without a known lot_type (never a guess).
    with pytest.raises(EvaluatorInputsError, match="missing required engine input"):
        _three_answer_inputs(doc)


def test_with_geometry_closes_the_gap_then_fails_closed_on_corner_frontage(monkeypatch) -> None:
    setup = _northern_setup(monkeypatch, geometry=True)
    study = study_from_study_setup(setup, _TEST_ONLY_OPTION, study_id="s", revision=_REVISION)

    # The lot_type half of the adapter gap is closed: a known corner lot_type, tax-map
    # sourced (PR #390), flows from the study read.
    lot_type = _fact(study, "lot_type")
    assert lot_type["value"] == LOT_TYPE_CORNER == "corner"
    assert lot_type["measurement"]["rank"] == "approximate_tax_map"

    # The SHAPE gap is closed too: build_evaluator_inputs no longer raises the
    # StudyContractError "Additional properties ... ('bbl', 'document_kind')". It now
    # reaches the next, pre-existing C-07 limit and fails closed on the corner lot's two
    # frontages (combined-outline rule, plan section 4; out of scope for C-07) - an
    # EvaluatorInputsError, NOT a StudyContractError.
    with pytest.raises(EvaluatorInputsError, match="resolves to 2 distinct site facts") as exc:
        build_evaluator_inputs(study, _OPTION_ID)
    assert "lot_front_ft" in str(exc.value)


# ---------------------------------------------------------------------------
# (c) The bridged study runs the real engine end to end (single-frontage fact set,
# the accepted C-07 golden path), reproducing the golden allowance.
# ---------------------------------------------------------------------------
def test_bridged_study_runs_the_engine_to_the_golden_allowance(monkeypatch) -> None:
    # The live CORNER read has two frontages (test above); to prove the bridge OUTPUT is
    # engine-compatible end to end, the setup's site facts are the benchmark city facts
    # the accepted C-07 golden test uses (a single Northern Boulevard frontage). The
    # property / lots / lot_selection are the live read's, bridged unchanged.
    live = _northern_setup(monkeypatch, geometry=False)
    setup = {**live, "site": {"facts": _benchmark_city_facts()}}
    study = study_from_study_setup(setup, _TEST_ONLY_OPTION, study_id="s", revision=_REVISION)

    doc = build_evaluator_inputs(study, _OPTION_ID)
    inputs = _three_answer_inputs(doc)
    # Each engine input equals the bridged study's fact value (read from the document).
    assert inputs.lot_area_sq_ft == float(_fact(study, "lot_area")["value"])
    assert inputs.lot_type == _fact(study, "lot_type")["value"]
    assert inputs.lot_front_ft == float(
        _fact(study, "lot_frontage", street="Northern Boulevard")["value"]
    )
    assert inputs.lot_depth_ft == float(_fact(study, "lot_depth")["value"])

    result = generate_results(inputs, env=_LANE_ON)
    validate_results_document(result.document)  # the results document validates
    allowance = result.document["answers"]["floor_area_allowance"]
    assert allowance["status"] == "available"
    area = next(v for v in allowance["values"] if v["key"] == "max_residential_floor_area")
    # The golden allowance already pinned by the A-04 benchmark test, not a new number.
    assert area["value"] == _benchmark_value("max_residential_floor_area") == 20150


# ---------------------------------------------------------------------------
# (d) R137/R138/R139 journey: the LIVE corner read (two frontages), with the lot's
# confirmed address, now runs THROUGH the engine - no test-only site facts. The corner
# stop is closed by the address-street assumption; the scope auto-fills from the bridge.
# ---------------------------------------------------------------------------
def test_corner_read_runs_through_the_engine_via_the_address_street_assumption(
    monkeypatch,
) -> None:
    setup = _northern_setup(monkeypatch, geometry=True)
    # The lot's REAL confirmed address (benchmark pack identity.address). The recorded
    # BBL-only read carries address=null because the Geoclient capture is owner-key gated
    # (Tier D); the confirmed-address step supplies this real address. It is NOT a test
    # literal and the site facts are the LIVE corner read's, unchanged.
    setup["property"]["address"] = _benchmark_identity_address()
    study = study_from_study_setup(
        setup, _TEST_ONLY_OPTION, study_id="study-northern-journey", revision=_REVISION
    )

    # R138: the corner stop is closed. lot_front_ft is the Northern Boulevard frontage
    # (the address street), read from its own study fact - not guessed.
    doc = build_evaluator_inputs(study, _OPTION_ID)
    validate_evaluator_inputs_document(doc)
    northern = _fact(study, "lot_frontage", street="Northern Boulevard")
    place_215 = _fact(study, "lot_frontage", street="215 Place")
    front = _input(doc, "lot_front_ft")
    assert front["value"] == northern["value"]  # 103.88 ft, from the fact (not a literal)
    assert front["fact_id"] == northern["fact_id"]
    assert front["rank"] == northern["measurement"]["rank"] == "approximate_tax_map"

    # Every governing value equals the study fact it came from (never a literal).
    for engine_key, fact_key in (
        ("lot_area_sq_ft", "lot_area"),
        ("lot_depth_ft", "lot_depth"),
        ("lot_type", "lot_type"),
        ("zoning_district", "zoning_district"),
    ):
        record = _input(doc, engine_key)
        fact = _fact(study, fact_key)
        assert record["value"] == fact["value"], engine_key
        assert record["fact_id"] == fact["fact_id"], engine_key

    # R139: build_three_answer_inputs auto-fills scope_inputs from the bridge (study passed).
    inputs = build_three_answer_inputs(
        doc,
        results_id="res-northern-journey",
        computed_at="2026-10-03T00:00:00Z",
        housing_program="standard_residence",
        overlay_present=True,  # a commercial overlay (C2-2) is recorded for the lot
        special_district_present=False,
        within_100_ft_of_street_line_intersection=True,
        street_line_intersection_angle_degrees=90.0,
        special_density_area=False,
        study=study,
    )
    assert inputs.scope_inputs is not None
    assert inputs.lot_front_ft == float(northern["value"])  # the address-street frontage
    assert inputs.lot_type == _fact(study, "lot_type")["value"]

    # The engine runs end to end and emits the 1.1.0 scope block.
    result = generate_results(inputs, env=_LANE_ON)
    validate_results_document(result.document)
    out = result.document
    # Scope (1.1.0) plus the R6B minimum-base-height note (1.2.0, #388): a non-empty notes
    # array binds 1.2.0, which admits the scope (#422; DB-129).
    assert out["contract_version"] == "1.2.0"
    scope = out["scope"]
    # The lot identity is derived from the study's BBL (not restated).
    assert scope["lot"]["bbl"] == study["property"]["bbl"]

    # All twelve assumed inputs are disclosed, exactly once each.
    emitted = [a["key"] for a in scope["assumptions"]]
    assert set(emitted) == set(ASSUMPTION_KEYS)
    assert len(emitted) == len(set(emitted)) == 12

    # The front-lot-line assumption is the Northern Boulevard corner disclosure; its value
    # and the other frontage's length come from the study facts, never literals.
    front_row = next(a for a in scope["assumptions"] if a["key"] == "lot_front_ft")
    assert front_row["value"] == northern["value"]  # 103.88 ft
    assert front_row["basis"] == "approximate_tax_map"
    assert "Front lot line assumed to be the Northern Boulevard frontage" in front_row[
        "statement"
    ]
    assert place_215["street"] in front_row["statement"]
    assert f"{float(place_215['value']):g}" in front_row["statement"]  # 99.98, from the fact

    # The sourced bases are honest: lot_type / overlay carry their recorded rank, not a guess.
    lot_type_row = next(a for a in scope["assumptions"] if a["key"] == "lot_type")
    assert lot_type_row["basis"] == _fact(study, "lot_type")["measurement"]["rank"]
    overlay_row = next(a for a in scope["assumptions"] if a["key"] == "overlay_present")
    assert overlay_row["basis"] == _fact(study, "commercial_overlay")["measurement"]["rank"]


def test_corner_read_with_geometry_fails_closed_when_address_names_no_frontage(
    monkeypatch,
) -> None:
    # Geometry present (two frontages) but the confirmed address names NEITHER street:
    # the R138 exception does not fire and the fail-closed corner error stands as today.
    setup = _northern_setup(monkeypatch, geometry=True)
    setup["property"]["address"] = "1 Nowhere Avenue"
    study = study_from_study_setup(setup, _TEST_ONLY_OPTION, study_id="s", revision=_REVISION)
    with pytest.raises(EvaluatorInputsError, match="resolves to 2 distinct site facts"):
        build_evaluator_inputs(study, _OPTION_ID)
