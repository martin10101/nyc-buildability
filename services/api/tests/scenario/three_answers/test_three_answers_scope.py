"""A-04 scope-beside-the-numbers tests (results contract 1.1.0, directive D-090-R108).

The three-answer generator emits the optional top-level ``scope`` object when its inputs
carry ``scope_inputs``: the 'Tax-lot-only estimate' label, the lot identity derived from the
BBL, the disclosed assumed conditions, and the unconfirmed whole-site / not-confirmed
remaining-capacity statements. These tests prove:

1. the benchmark document's scope equals the #387 fixture's scope object field by field
   (the expected object is read from the fixture, never restated);
2. the document validates against the results-v1 schema (the existing validate path);
3. with no scope_inputs the document carries no scope and declares 1.0.0, byte-identical to
   the pre-R108 shape (red/green);
4. a basis is only ever the one supplied in scope_inputs - the engine computes nothing about
   it (mutate one basis in the inputs and it moves, unchanged, in the output).

Expected scope values and the benchmark inputs are reused from the benchmark module, so no
string is restated here (the pattern of test_three_answers_shortfall.py).
"""

from __future__ import annotations

from dataclasses import replace

from app.scenario.three_answers import generate_results, validate_results_document
from app.scenario.three_answers.scope import DisclosedAssumption

from .test_three_answers_benchmark import (
    _ON,
    _benchmark_inputs,
    _benchmark_scope_inputs,
    _generate,
    _scope_fixture,
)


def test_benchmark_scope_equals_the_387_fixture_object_field_by_field() -> None:
    scope = _generate().document["scope"]
    expected = _scope_fixture()  # the #387 fixture's scope object, read from disk
    # The whole object matches; each field is asserted too so a mismatch names the field.
    assert scope == expected
    assert scope["basis"] == expected["basis"]
    assert scope["label"] == expected["label"]
    assert scope["lot"] == expected["lot"]  # bbl/borough/block/lot/display derived from the BBL
    assert scope["whole_site"] == expected["whole_site"]
    assert scope["remaining_capacity"] == expected["remaining_capacity"]
    assert scope["assumptions"] == expected["assumptions"]


def test_benchmark_scope_document_validates_against_the_results_schema() -> None:
    doc = _generate().document
    # generate_results validated internally; re-run the same public validate path explicitly.
    validate_results_document(doc)
    assert doc["contract_version"] == "1.1.0"


def test_no_scope_inputs_means_no_scope_and_document_stays_1_0_0() -> None:
    with_scope = _generate().document
    assert with_scope["contract_version"] == "1.1.0"
    assert "scope" in with_scope

    # Drop scope_inputs: no scope key, version 1.0.0 (the pre-R108 shape).
    without_scope = generate_results(_benchmark_inputs(scope_inputs=None), env=_ON).document
    assert "scope" not in without_scope
    assert without_scope["contract_version"] == "1.0.0"

    # Byte-identical otherwise: the two documents differ ONLY by the scope key and the version
    # string, so emitting scope changes nothing else (red/green: a stray change fails here).
    stripped = dict(with_scope)
    stripped.pop("scope")
    stripped["contract_version"] = "1.0.0"
    assert stripped == without_scope


def test_basis_comes_only_from_scope_inputs_never_computed() -> None:
    base = next(
        a for a in _generate().document["scope"]["assumptions"] if a["key"] == "lot_type"
    )
    assert base["basis"] == "fixture"  # as supplied by _benchmark_scope_inputs()

    # Mutate ONLY the lot_type disclosure's basis to a different valid enum value. It moves,
    # unchanged, to the output - proving the engine passes the basis through and derives
    # nothing about it. Value, unit and statement (from the real inputs) stay put.
    supplied = _benchmark_scope_inputs()
    mutated = replace(
        supplied,
        lot_type=DisclosedAssumption(basis="city_records", statement=supplied.lot_type.statement),
    )
    doc = generate_results(_benchmark_inputs(scope_inputs=mutated), env=_ON).document
    moved = next(a for a in doc["scope"]["assumptions"] if a["key"] == "lot_type")
    assert moved["basis"] == "city_records"
    assert moved["value"] == base["value"]
    assert moved["unit"] == base["unit"]
    assert moved["statement"] == base["statement"]
