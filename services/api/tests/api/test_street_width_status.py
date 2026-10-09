"""C-04 / plan task M1-06a (server side): an unknown street width on
``GET /api/v1/properties/{bbl}/rule-evaluation`` is marked "Needs street width" instead of letting
the narrow-street row read as the answer (plan section 4).

Fully offline: the PLUTO fetcher, the spatial substrate and the wide-street provider are the
recorded / typed doubles the accepted rule-evaluation acceptance pack uses (imported helpers, no
test functions). With ``LANE_C_ENABLED`` off every document is byte-identical to before, so no
existing rule-evaluation test changes.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
from fastapi.testclient import TestClient
from referencing import Registry, Resource

from app.api.v1 import street_width_status as sws
from app.main import app
from app.rules import RuleRegistry
from app.rules import coverage as cov
from app.rules.response import validate_rule_evaluation_document
from app.rules.wide_street_wiring import (
    COVERAGE_CONDITIONAL,
    COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
    DETERMINATION_PROFESSIONAL_REVIEW,
    DETERMINATION_WITHIN_WIDE,
    FAR_ROW_NONE,
    FAR_ROW_WIDE_STREET,
)
from tests.api.test_rule_evaluation_api import (
    BBL,
    _wide_street_determination,
    confident_district_substrate,
    enable_flag,
    fixture_response,
    install_fetcher,
    install_substrate,
    install_wide_street_provider,
)

_SCHEMA_DIR = Path(__file__).resolve().parents[4] / "packages" / "contracts" / "schemas" / "v1"
_URL = f"/api/v1/properties/{BBL}/rule-evaluation"
_LANE_C = "LANE_C_ENABLED"
_CONDITIONAL_RULE_ID = "r6-r7-r8-wide-street-conditional-far"


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.delenv(_LANE_C, raising=False)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def canonical_validator():
    resources = []
    for schema_file in sorted(_SCHEMA_DIR.glob("*.schema.json")):
        doc = json.loads(schema_file.read_text(encoding="utf-8"))
        resources.append((doc["$id"], Resource.from_contents(doc)))
    schema = json.loads((_SCHEMA_DIR / "rule_evaluation.schema.json").read_text(encoding="utf-8"))
    return jsonschema.Draft202012Validator(schema, registry=Registry().with_resources(resources))


def _get(client, monkeypatch, *, district: str | None, determination=None) -> dict:
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(None if district is None else confident_district_substrate(district))
    install_wide_street_provider(determination)
    response = client.get(_URL)
    assert response.status_code == 200, response.json()
    return response.json()


def _needs_width(doc: dict) -> list[str]:
    return [r for r in doc["reasons"] if r.startswith(sws.NEEDS_STREET_WIDTH_LABEL)]


def _applicable(doc: dict) -> dict:
    (trace,) = [t for t in doc["evaluations"] if t["applicability_outcome"] is True]
    return trace


# ---------------------------------------------------------------------------
# Drift guard: the engine still declares the exception the marking keys off.
# ---------------------------------------------------------------------------
def test_production_rule_still_declares_the_wide_street_alternative():
    rule = RuleRegistry().load().rule(_CONDITIONAL_RULE_ID)
    ids = {exc.get("id") for exc in rule.exceptions}
    assert sws.WIDE_STREET_ALTERNATIVE_EXCEPTION_ID in ids


def test_marking_is_off_unless_lane_c_flag_is_an_explicit_true_token():
    assert sws.street_width_marking_enabled(env={}) is False
    assert sws.street_width_marking_enabled(env={_LANE_C: "off"}) is False
    assert sws.street_width_marking_enabled(env={_LANE_C: "yes"}) is True


# ---------------------------------------------------------------------------
# Endpoint behaviour
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("district", ["R6", "R7-1", "R8"])
def test_unknown_width_on_a_width_dependent_district_is_marked(
    client, monkeypatch, canonical_validator, district
):
    monkeypatch.setenv(_LANE_C, "1")
    doc = _get(client, monkeypatch, district=district)

    assert list(canonical_validator.iter_errors(doc)) == []
    validate_rule_evaluation_document(doc)  # bundled runtime copy
    assert doc["contract_version"] == "1.2.0"  # in-contract: no new key, no version change
    assert "wide_street" not in doc

    (reason,) = _needs_width(doc)
    trace = _applicable(doc)
    narrow = trace["outputs"]["max_residential_far"]
    assert f"max_residential_far {narrow}" in reason
    assert sws.WIDE_STREET_ALTERNATIVE_EXCEPTION_ID in reason
    assert _CONDITIONAL_RULE_ID in reason
    assert "Neither is the answer" in reason

    # Values, coverage and the trace stay the engine's.
    assert trace["rule_id"] == _CONDITIONAL_RULE_ID
    assert doc["coverage_status"] == cov.COVERAGE_CONDITIONAL
    assert doc["professional_review_required"] is False


def test_flag_off_document_is_byte_identical_and_unmarked(client, monkeypatch):
    off = _get(client, monkeypatch, district="R6")
    assert _needs_width(off) == []
    assert off["reasons"] == []

    monkeypatch.setenv(_LANE_C, "1")
    on = _get(client, monkeypatch, district="R6")
    # The ONLY difference the flag makes is the one appended reason.
    assert {k: v for k, v in on.items() if k != "reasons"} == {
        k: v for k, v in off.items() if k != "reasons"
    }
    assert on["reasons"] == [*off["reasons"], *_needs_width(on)]
    assert len(_needs_width(on)) == 1


def test_known_width_within_wide_is_not_marked(client, monkeypatch, canonical_validator):
    monkeypatch.setenv(_LANE_C, "1")
    within = _wide_street_determination(
        DETERMINATION_WITHIN_WIDE,
        FAR_ROW_WIDE_STREET,
        COVERAGE_CONDITIONAL,
        reason="C-04 fixture: within-100ft determination",
        aggregate_intersects=True,
    )
    doc = _get(client, monkeypatch, district="R6", determination=within)
    assert list(canonical_validator.iter_errors(doc)) == []
    assert doc["wide_street"]["far_row"] == "wide_street_row"
    assert _needs_width(doc) == []


def test_professional_review_determination_is_not_double_marked(client, monkeypatch):
    monkeypatch.setenv(_LANE_C, "1")
    prr = _wide_street_determination(
        DETERMINATION_PROFESSIONAL_REVIEW,
        FAR_ROW_NONE,
        COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
        reason="C-04 fixture: unresolved street width",
    )
    doc = _get(client, monkeypatch, district="R6", determination=prr)
    assert doc["coverage_status"] == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert _needs_width(doc) == []  # the determination already speaks for the width


def test_width_independent_district_is_not_marked(client, monkeypatch):
    monkeypatch.setenv(_LANE_C, "1")
    doc = _get(client, monkeypatch, district="R5")
    assert _needs_width(doc) == []


def test_fail_safe_document_is_not_marked(client, monkeypatch):
    monkeypatch.setenv(_LANE_C, "1")
    doc = _get(client, monkeypatch, district=None)
    assert doc["fail_safe"] is True
    assert _needs_width(doc) == []


# ---------------------------------------------------------------------------
# The pure helper
# ---------------------------------------------------------------------------
def _doc(*, applicable=True, exception_id=sws.WIDE_STREET_ALTERNATIVE_EXCEPTION_ID, **extra):
    trace = {
        "rule_id": "some-rule",
        "applicability_outcome": applicable,
        "outputs": {"max_residential_far": 2.2},
        "exceptions_applied": [{"id": exception_id, "effect": "conditional_alternative"}],
    }
    return {"fail_safe": False, "reasons": ["prior"], "evaluations": [trace], **extra}


def test_helper_marks_once_and_never_mutates_its_input():
    doc = _doc()
    marked = sws.mark_unknown_street_width(doc)
    assert doc["reasons"] == ["prior"]
    assert marked["reasons"][0] == "prior"
    assert marked["reasons"][1].startswith("Needs street width: ")
    assert sws.mark_unknown_street_width(marked) == marked  # idempotent


@pytest.mark.parametrize(
    "doc",
    [
        _doc(applicable=False),
        _doc(exception_id="qualifying_housing"),
        _doc(fail_safe=True),
        _doc(wide_street={"far_row": "standard_row"}),
        {"fail_safe": False, "reasons": [], "evaluations": None},
    ],
)
def test_helper_leaves_width_independent_documents_alone(doc):
    assert sws.needs_street_width_reason(doc) is None
    assert sws.mark_unknown_street_width(doc) is doc
