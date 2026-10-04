"""The results ``scope`` printed on the DXF notes layer (owner directive
D-090-R108; results contract 1.1.0).

The DXF notes carry the SAME scope lines as the site plan: the estimate label,
the tax lot, the assumed conditions, the whole-site statement and the two
owner-settled strings - every figure and settled string read from the results
document, folded to the DXF's ASCII (the whole-site em dash becomes a hyphen).
A document without a scope carries no scope notes. The non-scope fixtures'
DXF snapshots stay byte-identical (enforced by ``test_results_dxf_snapshots.py``).
"""

from __future__ import annotations

from app.cad.results_dxf_notes import ascii_text
from app.drawings.kit.scope import ASSUMED_CONDITIONS_HEADING, ASSUMPTION_KEY_NAMES

from ..drawings.kit.kit_support import resolve
from .results_dxf_support import CONTRACT_FIXTURES, load, render

SCOPE = CONTRACT_FIXTURES / "synthetic_scope_tax_lot_only_northern.json"
NO_SCOPE = CONTRACT_FIXTURES / "synthetic_all_answers_available.json"


def test_dxf_notes_carry_the_scope_strings_read_from_the_document():
    doc = load(SCOPE)
    result = render(doc)
    notes = [n for n in result.notes if n.role == "scope"]
    assert notes
    text = "\n".join(n.text for n in notes)
    for pointer in ("/scope/label", "/scope/lot/display",
                    "/scope/remaining_capacity/label", "/scope/remaining_capacity/reason"):
        assert resolve(doc, pointer) in text
    # The whole-site statement's em dash folds to ASCII on the DXF.
    assert ascii_text(resolve(doc, "/scope/whole_site/statement"), "") in text
    for i, assumption in enumerate(doc["scope"]["assumptions"]):
        assert ASSUMPTION_KEY_NAMES[assumption["key"]] in text
        assert resolve(doc, f"/scope/assumptions/{i}/statement") in text
        assert resolve(doc, f"/scope/assumptions/{i}/basis") in text
    # Every scope note names, in ``sources``, the document pointer of each figure
    # or settled string it prints; only the kit's heading has none.
    assert [n.text for n in notes if not n.sources] == [ASSUMED_CONDITIONS_HEADING]
    assert all(n.sources for n in notes if n.text != ASSUMED_CONDITIONS_HEADING)
    assert result.text.isascii() and "\r" not in result.text


def test_a_document_without_scope_carries_no_scope_notes():
    doc = load(NO_SCOPE)
    assert doc.get("scope") is None
    result = render(doc)
    assert not [n for n in result.notes if n.role == "scope"]
    assert ASSUMED_CONDITIONS_HEADING not in result.text
