"""The results ``scope`` printed on the site plan (owner directive D-090-R108,
"put the scope beside the numbers"; results contract 1.1.0).

The scope lines appear on the drawing of a document that carries a scope and are
absent from one that does not; every printed figure and settled string is read
from the results document (never restated here), and the kit's own heading and
key names carry no legal claim. The non-scope fixtures' snapshots stay
byte-identical - enforced by ``test_snapshots.py`` (only the scope fixture's two
snapshots change in this task).
"""

from __future__ import annotations

import copy

import pytest

from app.drawings.kit import Drawing, render_massing, render_site_plan
from app.drawings.kit.errors import DrawingInputError
from app.drawings.kit.labels import format_number
from app.drawings.kit.scope import (
    ASSUMED_CONDITIONS_HEADING,
    ASSUMPTION_KEY_NAMES,
    FLAG_WORDS,
    assumption_value_word,
    load_scope,
)

from .kit_support import (
    CONTRACT_FIXTURES,
    ENV_ON,
    label_problems,
    load,
    numbers_not_in_input,
    parse,
    pieces,
    resolve,
)

SCOPE = CONTRACT_FIXTURES / "synthetic_scope_tax_lot_only_northern.json"
NO_SCOPE = CONTRACT_FIXTURES / "synthetic_all_answers_available.json"


def _norm(text: str) -> str:
    return " ".join(text.split())


def _sourced(svg: str) -> dict[str, str]:
    return {source: text for source, text, _ in pieces(parse(svg)) if source}


def test_site_plan_prints_the_scope_strings_read_from_the_document():
    doc = load(SCOPE)
    drawing = render_site_plan(doc, env=ENV_ON)
    assert isinstance(drawing, Drawing)
    got = _sourced(drawing.svg)
    # The label, the tax lot and the two owner-settled strings, byte-exact and
    # read straight from the document (never restated in this test).
    for pointer in ("/scope/label", "/scope/lot/display", "/scope/whole_site/statement",
                    "/scope/remaining_capacity/label", "/scope/remaining_capacity/reason"):
        assert got[pointer] == _norm(resolve(doc, pointer))
    # Every assumption row the document carries is printed, in document order (the
    # expected set is derived from the fixture, never a hand-maintained list).
    assumptions = doc["scope"]["assumptions"]
    printed_keys = [text for src, text, _ in pieces(parse(drawing.svg))
                    if src and src.startswith("/scope/assumptions/") and src.endswith("/key")]
    assert printed_keys == [ASSUMPTION_KEY_NAMES[a["key"]] for a in assumptions]
    # Each assumption row: a plain-words key (the kit's vocabulary, keyed by the
    # document key), the value (+ unit), the basis and the statement.
    for i, assumption in enumerate(assumptions):
        base = f"/scope/assumptions/{i}"
        assert got[f"{base}/key"] == ASSUMPTION_KEY_NAMES[assumption["key"]]
        assert got[f"{base}/basis"] == assumption["basis"]
        assert got[f"{base}/statement"] == _norm(assumption["statement"])
        value = assumption["value"]
        if isinstance(value, bool):
            assert got[f"{base}/value"] == FLAG_WORDS[value]
        elif isinstance(value, (int, float)):
            assert got[f"{base}/value"] == format_number(float(value))
        else:  # a code-like string: its fixed plain word, else printed verbatim
            word = assumption_value_word(assumption["key"], value) or value
            assert got[f"{base}/value"] == word
        if assumption["unit"] is not None:
            assert got[f"{base}/unit"] == assumption["unit"]


def test_code_like_values_print_the_plain_word_not_the_code():
    # The two code-like values in the fixture print the kit's fixed plain word, so the
    # drawing says the same word as the results card (#398 review F3); the raw engine
    # code never reaches the drawing.
    doc = load(SCOPE)
    drawing = render_site_plan(doc, env=ENV_ON)
    got = _sourced(drawing.svg)
    by_key = {a["key"]: i for i, a in enumerate(doc["scope"]["assumptions"])}
    assert got[f"/scope/assumptions/{by_key['housing_program']}/value"] == "standard residence"
    assert got[f"/scope/assumptions/{by_key['site_measurement_rank']}/value"] == "city records"
    assert "standard_residence" not in drawing.svg
    assert "city_records" not in drawing.svg


def test_an_unknown_assumption_key_fails_closed():
    # The key vocabulary fails closed: a key the kit has no plain-words name for is
    # refused, never guessed (unchanged by the 7 new keys).
    scope = copy.deepcopy(load(SCOPE)["scope"])
    scope["assumptions"][0]["key"] = "not_a_real_assumption_key"
    with pytest.raises(DrawingInputError) as caught:
        load_scope(scope)
    assert caught.value.code == "scope_assumption_key_unknown"


def test_the_assumed_conditions_heading_is_present_and_claims_nothing():
    drawing = render_site_plan(load(SCOPE), env=ENV_ON)
    headings = [text for source, text, role in pieces(parse(drawing.svg))
                if role == "note" and source is None]
    assert ASSUMED_CONDITIONS_HEADING in headings


def test_every_printed_scope_piece_is_traceable_to_the_document():
    doc = load(SCOPE)
    drawing = render_site_plan(doc, env=ENV_ON)
    assert label_problems(drawing.svg, doc) == []
    assert numbers_not_in_input(drawing.svg, doc) == []


def test_a_document_without_scope_draws_no_scope_lines():
    doc = load(NO_SCOPE)
    assert doc.get("scope") is None
    drawing = render_site_plan(doc, env=ENV_ON)
    assert isinstance(drawing, Drawing)
    assert not [s for s, _, _ in pieces(parse(drawing.svg)) if s and s.startswith("/scope")]
    assert ASSUMED_CONDITIONS_HEADING not in drawing.svg


def test_the_scope_fixture_draws_no_massing():
    # Its building option is not available, so there is no massing (and no massing
    # snapshot); the scope shows on the site plan instead.
    assert isinstance(render_site_plan(load(SCOPE), env=ENV_ON), Drawing)
    assert not isinstance(render_massing(load(SCOPE), env=ENV_ON), Drawing)
