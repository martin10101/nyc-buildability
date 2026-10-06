"""ONE continuous recorded-data journey for 215-16 Northern Boulevard, Queens (BBL
4073340070), flags off except the Lane A engine gate (D-090-R137; stacked on #417's
R138 address-street assumption and R139 scope auto-fill).

The one primary test chains the whole product path, each link consuming the PREVIOUS
link's output object (no re-typed intermediate literals):

    entry (BBL) -> recorded study read -> bridge -> evaluator inputs -> engine results
    document (contract 1.2.0: scope + the R6B height note) -> exports (site-plan SVG +
    results DXF) -> committed fixture

A second short test proves the REAL address->BBL leg on the Geoclient User Guide
documented example (314 W 100 St -> BBL 1018887502), so the module shows both legs
honestly.

HONEST STATUS of each leg (built / connected / tested / professionally verified):
- Entry, study read, bridge, evaluator inputs, engine, site-plan SVG, results DXF, and
  the web cards render are BUILT, CONNECTED to each other here, and TESTED (this module +
  its committed fixture and snapshots). PROFESSIONALLY VERIFIED: NONE - every rule result
  is a draft (``needs_review``); no number here is a reviewed legal conclusion.

This is a RECORDED-DATA run: the lot facts come from the recorded benchmark pack
(services/api/tests/fixtures/benchmark_215_16_northern), never a live call, and this
module forbids network egress. Entry is by BBL because the lot's address has no recorded
Geoclient capture (the GEOCLIENT_SUBSCRIPTION_KEY is owner-held, Tier D; D-090-R140); the
real address->BBL path is proven on the documented example 314 W 100 St in
tests/api/test_address_resolution_recorded_geoclient.py and exercised again below. No
215-16 address recording is faked. Nothing here claims the estimate complies with the
zoning resolution.
"""

from __future__ import annotations

import http.client
import json
import os
import socket
from pathlib import Path

import pytest

from app.cad.results_dxf import ResultsDxf, render_results_dxf
from app.cad.results_dxf_notes import ascii_text
from app.connectors.geoclient_address import SOURCE_ID, resolve_address
from app.contracts.evaluator_inputs import build_evaluator_inputs, build_three_answer_inputs
from app.contracts.study_contracts import (
    validate_evaluator_inputs_document,
    validate_results_document,
    validate_study_document,
)
from app.contracts.study_setup_bridge import study_from_study_setup
from app.drawings.kit import Drawing, render_site_plan
from app.scenario.three_answers import generate_results
from app.scenario.three_answers.scope import ASSUMPTION_KEYS
from tests.api.test_address_resolution_recorded_geoclient import (
    DUMMY_KEY,
    G01,
    _no_sleep,
    _single_body_transport,
    recorded_request,
)
from tests.api.test_study_geometry import NORTHERN_BBL
from tests.api.test_study_read_api import _TEST_ONLY_OPTION
from tests.contracts.test_evaluator_inputs import (
    _BENCHMARK,
    _benchmark_identity_address,
    _benchmark_value,
)
from tests.contracts.test_study_setup_bridge import (
    _LANE_ON,
    _OPTION_ID,
    _REVISION,
    _fact,
    _input,
    _northern_setup,
)
from tests.drawings.kit.kit_support import parse, pieces

# The exports render with Lane E on (the drawing-kit lane); the engine gate is Lane A.
_KIT_ENV = {"LANE_E_ENABLED": "1"}

# The committed journey fixture is the byte-exact serialization of the engine output below.
# Regenerate it with UPDATE_JOURNEY_FIXTURE=1 and review the diff like code.
_REPO_ROOT = Path(__file__).resolve().parents[4]
_FIXTURE_PATH = (
    _REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "results"
    / "recorded_215_16_northern_journey.json"
)

# Stable identifiers so the serialized fixture is reproducible (the engine carries them
# through verbatim; they are caller inputs, not computed values).
_STUDY_ID = "study-215-16-northern-journey"
_RESULTS_ID = "res-215-16-northern-journey"
_COMPUTED_AT = "2026-10-03T00:00:00Z"


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Forbid live network egress at the seams where it actually happens (the accepted
    test_address_resolution_recorded_geoclient pattern: block http.client's connect choke
    points and socket.create_connection, never socket construction, which would deadlock
    the anyio portal the study-read TestClient drives). The study read uses recorded
    providers and the address leg a recorded-body transport, so nothing should connect."""

    def _blocked(*_args, **_kwargs):
        raise AssertionError("network I/O attempted in a recorded-data journey test")

    monkeypatch.setattr(http.client.HTTPConnection, "connect", _blocked)
    monkeypatch.setattr(http.client.HTTPSConnection, "connect", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)


def _benchmark_identity_bbl() -> str:
    """The lot's canonical BBL, read from the recorded benchmark pack identity - the
    disclosed BBL the journey enters by, never a test literal."""
    doc = json.loads(_BENCHMARK.read_text("utf-8"))
    return doc["identity"]["bbls"][0]


def test_recorded_journey_entry_bbl_to_results_to_exports_to_fixture(monkeypatch) -> None:
    # 1. ENTRY by the disclosed BBL from the benchmark pack identity. The recorded study
    # read below is keyed on this same lot, so the BBL entry and the read agree.
    entry_bbl = _benchmark_identity_bbl()
    assert entry_bbl == NORTHERN_BBL

    # 2. STUDY READ on recorded data: the recorded corner read carries two per-street
    # frontages and a geometry provider from the recorded benchmark geometry. The recorded
    # BBL-only read's own address is null (owner-key gated); the confirmed-address step
    # supplies the real address (benchmark pack identity), so the corner stop can resolve.
    setup = _northern_setup(monkeypatch, geometry=True)
    setup["property"]["address"] = _benchmark_identity_address()
    study = study_from_study_setup(
        setup, _TEST_ONLY_OPTION, study_id=_STUDY_ID, revision=_REVISION
    )
    validate_study_document(study)
    assert study["property"]["bbl"] == entry_bbl

    # 3. BRIDGE -> evaluator inputs. R138: lot_front_ft is the Northern Boulevard frontage
    # (the address street), read from its own study fact - not guessed. Every value is read
    # from the study fact it came from.
    doc = build_evaluator_inputs(study, _OPTION_ID)
    validate_evaluator_inputs_document(doc)
    northern = _fact(study, "lot_frontage", street="Northern Boulevard")
    place_215 = _fact(study, "lot_frontage", street="215 Place")
    front = _input(doc, "lot_front_ft")
    assert front["value"] == northern["value"]
    assert front["fact_id"] == northern["fact_id"]
    assert front["rank"] == northern["measurement"]["rank"]
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

    # 4. build_three_answer_inputs auto-fills the scope from the bridge (R139: study passed).
    inputs = build_three_answer_inputs(
        doc,
        results_id=_RESULTS_ID,
        computed_at=_COMPUTED_AT,
        housing_program="standard_residence",
        overlay_present=True,  # the C2-2 commercial overlay recorded for this lot
        special_district_present=False,
        within_100_ft_of_street_line_intersection=True,
        street_line_intersection_angle_degrees=90.0,
        special_density_area=False,
        study=study,
    )
    assert inputs.scope_inputs is not None
    assert inputs.lot_front_ft == float(northern["value"])
    assert inputs.lot_type == _fact(study, "lot_type")["value"]

    # 5. ENGINE: the real engine runs end to end with every Lane flag off except Lane A, and
    # emits the scope document, and the R6B height note binds 1.2.0 (#388, #422).
    # It is validated against the bundled results schema.
    result = generate_results(inputs, env=_LANE_ON)
    document = result.document
    validate_results_document(document)
    assert document["contract_version"] == "1.2.0"  # scope + the R6B height note (#388, #422)

    scope = document["scope"]
    assert scope["lot"]["bbl"] == study["property"]["bbl"] == entry_bbl
    emitted = [a["key"] for a in scope["assumptions"]]
    assert set(emitted) == set(ASSUMPTION_KEYS)
    assert len(emitted) == len(set(emitted)) == 12  # PR #417 body: all 12 assumed inputs

    # The front-lot-line assumption is the Northern Boulevard corner disclosure; its value
    # and the other frontage's length are read from the study facts, never retyped.
    front_row = next(a for a in scope["assumptions"] if a["key"] == "lot_front_ft")
    assert front_row["value"] == northern["value"]
    assert front_row["basis"] == northern["measurement"]["rank"]
    assert "Front lot line assumed to be the Northern Boulevard frontage" in front_row[
        "statement"
    ]
    assert place_215["street"] in front_row["statement"]
    assert f"{float(place_215['value']):g}" in front_row["statement"]

    # The golden allowance equals the benchmark pack's recorded value, not a new number.
    allowance = document["answers"]["floor_area_allowance"]
    assert allowance["status"] == "available"
    area = next(v for v in allowance["values"] if v["key"] == "max_residential_floor_area")
    assert area["value"] == _benchmark_value("max_residential_floor_area") == 20150

    # 6. EXPORTS from the SAME document object. The scope label and the front-lot-line
    # assumption statement appear on the site-plan SVG and in the results DXF notes.
    drawing = render_site_plan(document, env=_KIT_ENV)
    assert isinstance(drawing, Drawing)
    sourced = {source: text for source, text, _role in pieces(parse(drawing.svg)) if source}
    assert sourced["/scope/label"] == scope["label"]
    front_idx = emitted.index("lot_front_ft")
    # The kit wraps a long statement across lines; compare the reconstructed sourced piece
    # to the document statement with whitespace collapsed (never a retyped sentence).
    assert sourced[f"/scope/assumptions/{front_idx}/statement"] == " ".join(
        front_row["statement"].split()
    )

    dxf = render_results_dxf(document, env=_KIT_ENV)
    assert isinstance(dxf, ResultsDxf)
    assert ascii_text(scope["label"], "") in dxf.text
    assert ascii_text(front_row["statement"], "") in dxf.text

    # 7. BYTE-DRIFT: the committed fixture is exactly this engine output, serialized the way
    # the other results fixtures are (indent 2, ensure_ascii off, one trailing newline).
    serialized = (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if os.environ.get("UPDATE_JOURNEY_FIXTURE") == "1":
        _FIXTURE_PATH.write_bytes(serialized)
    assert _FIXTURE_PATH.exists(), f"no committed fixture {_FIXTURE_PATH.name}"
    # LF-normalize the checkout copy (a Windows autocrlf checkout smudges CRLF).
    assert serialized == _FIXTURE_PATH.read_bytes().replace(b"\r\n", b"\n")


def test_recorded_address_to_bbl_on_the_documented_example() -> None:
    # The address->BBL leg, proven on the Geoclient User Guide DOCUMENTED EXAMPLE (314 W 100
    # St, Manhattan), through the same REAL connector helper the recorded-Geoclient suite
    # uses, over that suite's recorded response body. 215-16 Northern has no recorded
    # Geoclient capture (owner-key gated, Tier D), so the journey above enters by BBL; this
    # leg shows the real address path works, honestly, on the address it was recorded for.
    req = recorded_request(G01)
    addr = req["address"]
    direct = resolve_address(
        req["house_number"],
        req["street"],
        borough=req["borough"],
        key=DUMMY_KEY,
        transport=_single_body_transport(req["body"]),
        sleep=_no_sleep,
    )
    # The real connector derives the documented-example BBL from the recorded body; it
    # equals the fixture's own field (read, not restated) and the documented 1018887502.
    assert direct.bbl == addr["bbl"] == "1018887502"
    assert direct.provenance["source_id"] == SOURCE_ID  # the real Geoclient connector ran
