"""Tests for the zero-dependency DXF site-plan writer (task M5-T081, D-087
CAD-1), scenarios AS-1..AS-5.

Offline and deterministic: no network, no I/O, stdlib + pytest only. A minimal
in-test group-code reader parses the emitted DXF back so the structural
assertions never depend on the writer's own helpers.
"""

import hashlib
import re

import pytest

from app.cad import dxf_writer as d
from app.cad.dxf_writer import (
    CLAIM_CLASS_WORDS,
    CRS_UNITS_NOTE,
    PROPOSED_LABEL,
    DxfDocument,
    DxfSanitizationError,
    DxfValidationError,
    Ring,
    TextLabel,
    build_site_plan_document,
    render_site_plan_dxf,
    serialize_document,
)

# --------------------------------------------------------------------------- #
# Shared fixture: a rectangular lot, an L-shaped building (6 vertices), 3 floors.
# EPSG:2263 US survey feet. This exact fixture pins the golden digest below.
# --------------------------------------------------------------------------- #

LOT = [(1000.0, 2000.0), (1100.0, 2000.0), (1100.0, 2080.0), (1000.0, 2080.0)]
BUILDING = [
    (1010.0, 2010.0),
    (1060.0, 2010.0),
    (1060.0, 2040.0),
    (1090.0, 2040.0),
    (1090.0, 2070.0),
    (1010.0, 2070.0),
]
FLOOR_HEIGHTS = [12.0, 11.0, 10.0]

# Golden digest of render_site_plan_dxf(LOT, BUILDING, FLOOR_HEIGHTS) as ASCII
# bytes. Regenerate ONLY on a deliberate format change (re-anchor + CI green).
GOLDEN_SHA256 = "dbef79e1fd68508541a874ad5948a0384d08b8124f7c57122422706466d2ff11"


def _render() -> str:
    return render_site_plan_dxf(LOT, BUILDING, FLOOR_HEIGHTS)


# --------------------------------------------------------------------------- #
# Minimal group-code reader (independent of the writer internals).
# --------------------------------------------------------------------------- #

def parse_pairs(text: str) -> list[tuple[int, str]]:
    """Parse ASCII DXF into (code, value) pairs, asserting strict alternation."""
    lines = text.split("\n")
    assert lines and lines[-1] == "", "DXF must end with a trailing newline"
    lines.pop()  # drop the empty trailing element
    assert len(lines) % 2 == 0, "group-code stream is not strictly alternating"
    pairs: list[tuple[int, str]] = []
    for i in range(0, len(lines), 2):
        code_line, value = lines[i], lines[i + 1]
        assert code_line.lstrip("-").isdigit(), f"bad group code line {code_line!r}"
        pairs.append((int(code_line), value))
    return pairs


def split_sections(pairs: list[tuple[int, str]]) -> dict[str, list[tuple[int, str]]]:
    """Return {section_name: inner_pairs} and assert HEADER/TABLES/ENTITIES
    order plus the terminating 0/EOF."""
    sections: dict[str, list[tuple[int, str]]] = {}
    order: list[str] = []
    i, n = 0, len(pairs)
    while i < n:
        code, value = pairs[i]
        if (code, value) == (0, "SECTION"):
            assert pairs[i + 1][0] == 2, "SECTION must be followed by a 2/name pair"
            name = pairs[i + 1][1]
            inner: list[tuple[int, str]] = []
            j = i + 2
            while j < n and pairs[j] != (0, "ENDSEC"):
                inner.append(pairs[j])
                j += 1
            assert j < n, f"section {name} missing ENDSEC"
            sections[name] = inner
            order.append(name)
            i = j + 1
        elif (code, value) == (0, "EOF"):
            assert i == n - 1, "0/EOF must be the final pair"
            i += 1
        else:  # pragma: no cover - defensive
            i += 1
    assert order == ["HEADER", "TABLES", "ENTITIES"], order
    return sections


def read_polylines(entities: list[tuple[int, str]]) -> list[dict]:
    """Extract POLYLINE entities with their VERTEX (x, y) points and closed flag."""
    polylines: list[dict] = []
    i, n = 0, len(entities)
    current: dict | None = None
    while i < n:
        code, value = entities[i]
        if (code, value) == (0, "POLYLINE"):
            current = {"layer": None, "closed": None, "vertices": []}
            # scan header pairs up to the first VERTEX/SEQEND
            j = i + 1
            while j < n and entities[j][0] != 0:
                c, v = entities[j]
                if c == 8:
                    current["layer"] = v
                elif c == 70:
                    current["closed"] = bool(int(v) & 1)
                j += 1
            i = j
        elif (code, value) == (0, "VERTEX") and current is not None:
            x = y = None
            j = i + 1
            while j < n and entities[j][0] != 0:
                c, v = entities[j]
                if c == 10:
                    x = float(v)
                elif c == 20:
                    y = float(v)
                j += 1
            current["vertices"].append((x, y))
            i = j
        elif (code, value) == (0, "SEQEND"):
            assert current is not None
            polylines.append(current)
            current = None
            i += 1
        else:
            i += 1
    return polylines


def entity_type_counts(entities: list[tuple[int, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for code, value in entities:
        if code == 0:
            counts[value] = counts.get(value, 0) + 1
    return counts


# --------------------------------------------------------------------------- #
# AS-1 structure: alternation, section order, in-test round-trip, golden digest.
# --------------------------------------------------------------------------- #

def test_as1_structure_parses_and_sections_in_order():
    text = _render()
    assert text.isascii(), "output must be ASCII"
    pairs = parse_pairs(text)  # asserts strict alternation
    sections = split_sections(pairs)  # asserts HEADER/TABLES/ENTITIES + EOF
    header = dict(
        (pairs[k][1], pairs[k + 1]) for k in range(len(pairs) - 1) if pairs[k][0] == 9
    )
    assert header["$ACADVER"] == (1, "AC1009")
    assert "$INSUNITS" in header
    assert sections["ENTITIES"], "ENTITIES section is non-empty"


def test_as1_golden_digest_is_byte_stable():
    a = _render().encode("ascii")
    b = _render().encode("ascii")
    assert a == b, "identical inputs must give byte-identical output"
    assert hashlib.sha256(a).hexdigest() == GOLDEN_SHA256


# --------------------------------------------------------------------------- #
# AS-2 site-plan content: layers, closed outlines, 3DFACE count, round-trip.
# --------------------------------------------------------------------------- #

def test_as2_layers_present_exactly():
    sections = split_sections(parse_pairs(_render()))
    tables = sections["TABLES"]
    layer_names = [
        tables[k + 1][1]
        for k in range(len(tables) - 1)
        if tables[k] == (0, "LAYER") and tables[k + 1][0] == 2
    ]
    assert set(layer_names) == {"LOT", "BUILDING_OUTLINE", "MASSING_3D", "ANNOTATION"}


def test_as2_face_count_equals_edges_times_floors():
    sections = split_sections(parse_pairs(_render()))
    counts = entity_type_counts(sections["ENTITIES"])
    assert counts["3DFACE"] == len(BUILDING) * len(FLOOR_HEIGHTS)
    # POLYLINE = lot + building + one massing ring per band boundary (floors+1).
    assert counts["POLYLINE"] == 2 + (len(FLOOR_HEIGHTS) + 1)
    assert counts["LINE"] == len(BUILDING)  # one vertical corner line per vertex
    assert counts["TEXT"] == 3


def test_as2_outlines_closed_and_coordinates_round_trip():
    sections = split_sections(parse_pairs(_render()))
    polylines = read_polylines(sections["ENTITIES"])
    assert polylines, "at least one polyline emitted"
    assert all(p["closed"] for p in polylines), "every outline polyline is closed"
    building_polys = [p for p in polylines if p["layer"] == "BUILDING_OUTLINE"]
    assert len(building_polys) == 1
    assert building_polys[0]["vertices"] == BUILDING  # exact round-trip
    lot_polys = [p for p in polylines if p["layer"] == "LOT"]
    assert lot_polys[0]["vertices"] == LOT


def test_as2_header_declares_drawing_unit():
    pairs = parse_pairs(_render())
    idx = pairs.index((9, "$INSUNITS"))
    assert pairs[idx + 1] == (70, str(d.INSUNITS_FEET))  # 2 = feet


# --------------------------------------------------------------------------- #
# AS-3 fail-closed + injection.
# --------------------------------------------------------------------------- #

def test_as3_non_finite_coordinate_refused():
    with pytest.raises(DxfValidationError) as exc:
        build_site_plan_document(
            [(0.0, 0.0), (float("inf"), 0.0), (1.0, 1.0)], BUILDING, FLOOR_HEIGHTS
        )
    assert exc.value.code == "non_finite_coordinate"


def test_as3_degenerate_ring_refused():
    with pytest.raises(DxfValidationError) as exc:
        build_site_plan_document(
            [(0.0, 0.0), (1.0, 0.0)], BUILDING, FLOOR_HEIGHTS  # < 3 vertices
        )
    assert exc.value.code == "degenerate_ring"


def test_as3_collinear_ring_refused():
    with pytest.raises(DxfValidationError) as exc:
        build_site_plan_document(
            [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)], BUILDING, FLOOR_HEIGHTS  # zero area
        )
    assert exc.value.code == "degenerate_ring"


def test_as3_invalid_layer_name_refused():
    ring = Ring("lot outline", tuple(LOT), 0.0)  # space is illegal in an R12 name
    with pytest.raises(DxfValidationError) as exc:
        ring.validate()
    assert exc.value.code == "invalid_layer_name"


def test_as3_over_cap_entity_count_refused(monkeypatch):
    monkeypatch.setattr(d, "MAX_ENTITIES", 2)
    with pytest.raises(DxfValidationError) as exc:
        build_site_plan_document(LOT, BUILDING, FLOOR_HEIGHTS)
    assert exc.value.code == "entity_cap_exceeded"


def _injected_document() -> DxfDocument:
    """A document whose annotation text carries a CR/LF injection attempt."""
    return DxfDocument(
        layers=d.LAYER_DEFINITIONS,
        texts=[
            TextLabel(
                layer="ANNOTATION",
                position=(0.0, 0.0, 0.0),
                height=1.0,
                text="INJECT\n0\nSECTION\n2\nENTITIES",
            )
        ],
    )


def test_as3_newline_injection_refused():
    """Named mutation test: bypassing the sanitizer reddens THIS test."""
    with pytest.raises(DxfSanitizationError):
        serialize_document(_injected_document())


def test_as3_no_partial_output_on_refusal():
    # A refusal returns nothing; there is no partially-written string to leak.
    try:
        serialize_document(_injected_document())
    except DxfSanitizationError:
        return
    pytest.fail("expected a sanitization refusal")


def test_as3_sanitizer_guard_is_necessary(monkeypatch):
    """Demonstrates the guard is load-bearing: with the sanitizer neutered the
    injected newline forges spurious group-code lines instead of being refused."""
    monkeypatch.setattr(d, "_sanitize_value", lambda value, *, field: value)
    text = serialize_document(_injected_document())
    # Under the mutant the injection is NOT refused and corrupts the stream.
    assert "\nINJECT\n0\nSECTION\n" in "\n" + text


# --------------------------------------------------------------------------- #
# AS-4 honesty.
# --------------------------------------------------------------------------- #

def test_as4_annotation_carries_required_labels():
    text = _render()
    assert PROPOSED_LABEL in text
    assert CRS_UNITS_NOTE in text
    assert "EPSG:2263" in text
    assert "US SURVEY FEET" in text


def test_as4_no_claim_class_words_anywhere():
    upper = _render().upper()
    for word in CLAIM_CLASS_WORDS:
        assert word not in upper, f"claim-class word leaked: {word}"
    # Spot-check words the honesty directive names explicitly.
    for banned in ("PERMITTED", "APPROVED", "MAXIMUM ALLOWED"):
        assert banned not in upper


# --------------------------------------------------------------------------- #
# AS-5 scope: stdlib only, deterministic import surface.
# --------------------------------------------------------------------------- #

def test_as5_module_imports_stdlib_only():
    src = open(d.__file__, encoding="utf-8").read()
    third_party = re.findall(
        r"^\s*(?:from|import)\s+(shapely|numpy|pydantic|fastapi|requests|httpx)",
        src,
        re.MULTILINE,
    )
    assert third_party == [], f"unexpected third-party import: {third_party}"
