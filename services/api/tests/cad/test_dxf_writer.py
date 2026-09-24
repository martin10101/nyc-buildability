"""Tests for the zero-dependency DXF site-plan writer (task M5-T081, D-087
CAD-1), scenarios AS-1..AS-5.

Offline and deterministic: no network, no I/O, stdlib + pytest only. A minimal
in-test group-code reader parses the emitted DXF back so the structural
assertions never depend on the writer's own helpers.
"""

import ast
import hashlib
from pathlib import Path

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
# Re-pinned for M5-T096: the TABLES section now emits a VPORT (*ACTIVE) table
# framing the extents and a STYLE (STANDARD) table (order VPORT, LTYPE, LAYER,
# STYLE) in addition to the prior LTYPE + LAYER tables. No HEADER variable, layer,
# entity, refusal or honesty text changed; only the added tables move the bytes.
# Prior golden: 2d8988d6d7338ed606a9a253cb0d3af2fe1c8f5d526cd8750dac769a9025d809.
GOLDEN_SHA256 = "6a8dbd94fd3f5a6e9ddc22bb5712dd10133a1b7701301c59fc7023f495ba127b"


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


def table_order(tables: list[tuple[int, str]]) -> list[str]:
    """Names of the sub-tables in the TABLES section, in file order."""
    return [
        tables[k + 1][1]
        for k in range(len(tables) - 1)
        if tables[k] == (0, "TABLE") and tables[k + 1][0] == 2
    ]


def read_table_records(tables: list[tuple[int, str]], name: str) -> list[list[tuple[int, str]]]:
    """Return each record of the named sub-table as its list of (code, value)
    pairs. A record starts at a ``(0, name)`` pair inside the ``(0,TABLE)/(2,name)
    ... (0,ENDTAB)`` window and runs up to the next ``0`` pair."""
    records: list[list[tuple[int, str]]] = []
    in_table = False
    current: list[tuple[int, str]] | None = None
    i, n = 0, len(tables)
    while i < n:
        code, value = tables[i]
        if code == 0 and value == "TABLE":
            in_table = i + 1 < n and tables[i + 1] == (2, name)
            current = None
        elif code == 0 and value == "ENDTAB":
            if current is not None:
                records.append(current)
                current = None
            in_table = False
        elif in_table and code == 0 and value == name:
            if current is not None:
                records.append(current)
            current = [(code, value)]
        elif in_table and current is not None:
            current.append((code, value))
        i += 1
    return records


def header_extents(pairs: list[tuple[int, str]]) -> tuple[tuple[float, float], tuple[float, float]]:
    """($EXTMIN x, y), ($EXTMAX x, y) read back from the HEADER."""
    def point(var: str) -> tuple[float, float]:
        idx = pairs.index((9, var))
        return float(pairs[idx + 1][1]), float(pairs[idx + 2][1])
    return point("$EXTMIN"), point("$EXTMAX")


def text_style_names(entities: list[tuple[int, str]]) -> list[str]:
    """The style each TEXT entity resolves to: its group-7 value if present, else
    the STANDARD default (DXF Reference, TEXT group 7 default)."""
    styles: list[str] = []
    i, n = 0, len(entities)
    while i < n:
        if entities[i] == (0, "TEXT"):
            style = "STANDARD"
            j = i + 1
            while j < n and entities[j][0] != 0:
                if entities[j][0] == 7:
                    style = entities[j][1]
                j += 1
            styles.append(style)
            i = j
        else:
            i += 1
    return styles


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
    # Assert the HARDCODED literal 21 (US Survey Feet), NOT str(d.INSUNITS_*),
    # which passes for ANY constant value; this externally pins the exact code
    # so a 2-vs-21 regression reddens the suite (G3 F1 / G1).
    assert pairs[idx + 1] == (70, "21")


# --------------------------------------------------------------------------- #
# AS-1 tables: LTYPE, LAYER, STYLE (STANDARD) and VPORT (*ACTIVE) in R12 order,
# with the group codes the DXF Reference gives (M5-T096, closes G1-A2 / DB-057 b).
# --------------------------------------------------------------------------- #

def test_as1_tables_in_r12_reference_order():
    """The four sub-tables appear in the canonical R12 write order VPORT, LTYPE,
    LAYER, STYLE (LTYPE before LAYER because layers reference the linetype)."""
    tables = split_sections(parse_pairs(_render()))["TABLES"]
    assert table_order(tables) == ["VPORT", "LTYPE", "LAYER", "STYLE"]


def test_as1_style_table_defines_standard():
    """A STYLE table defines the STANDARD text style that every TEXT resolves to.
    Mutation: dropping the STYLE table (or its STANDARD entry) empties this list
    and reddens the test (and test_as1_every_text_resolves_to_a_defined_style)."""
    tables = split_sections(parse_pairs(_render()))["TABLES"]
    styles = read_table_records(tables, "STYLE")
    assert len(styles) == 1, "exactly one STYLE record"
    names = [v for c, v in styles[0] if c == 2]
    assert names == ["STANDARD"]
    fields = {c: v for c, v in styles[0] if c not in (0,)}
    # Group codes per the live Autodesk STYLE (DXF) page (see the writer's STYLE
    # constants block): 40 fixed height (0 = per-TEXT), 41 width factor, 50 oblique,
    # 71 generation flags, 42 last height, 3 primary font, 4 bigfont (blank).
    assert fields[40] == "0.000000"     # fixed text height 0 -> height taken per-TEXT
    assert fields[41] == "1.000000"     # width factor
    assert fields[50] == "0.000000"     # oblique angle
    assert fields[71] == "0"            # text-generation flags
    assert fields[3] == "txt"           # primary font file
    assert fields[4] == ""              # bigfont file (blank)


def test_as1_every_text_resolves_to_a_defined_style():
    """Every TEXT entity resolves to a style that the STYLE table defines. The
    entities omit group 7, so they use STANDARD, which the STYLE table now
    provides; dropping the STYLE table leaves the set of defined styles empty."""
    sections = split_sections(parse_pairs(_render()))
    defined = {v for rec in read_table_records(sections["TABLES"], "STYLE")
               for c, v in rec if c == 2}
    used = text_style_names(sections["ENTITIES"])
    assert used, "the drawing has TEXT entities"
    assert set(used) == {"STANDARD"}
    assert set(used) <= defined, f"undefined text style(s): {set(used) - defined}"


def test_as1_vport_active_frames_the_extents():
    """The VPORT table carries one *ACTIVE record whose view centre is the extents
    midpoint and whose framed view (height x aspect) covers the whole drawing.
    Mutation: a VPORT centre that ignores the extents (e.g. fixed 0,0) reddens the
    centre assertions; a view height that no longer covers the extents reddens the
    coverage assertions."""
    pairs = parse_pairs(_render())
    tables = split_sections(pairs)["TABLES"]
    vports = read_table_records(tables, "VPORT")
    assert len(vports) == 1, "exactly one VPORT record"
    names = [v for c, v in vports[0] if c == 2]
    assert names == ["*ACTIVE"]
    rec = {c: v for c, v in vports[0] if c not in (0,)}
    center_x, center_y = float(rec[12]), float(rec[22])
    view_height, aspect = float(rec[40]), float(rec[41])
    # View direction is a plan view (0, 0, 1), target at the origin.
    assert (rec[16], rec[26], rec[36]) == ("0.000000", "0.000000", "1.000000")
    (min_x, min_y), (max_x, max_y) = header_extents(pairs)
    assert center_x == pytest.approx((min_x + max_x) / 2.0, abs=1e-6)
    assert center_y == pytest.approx((min_y + max_y) / 2.0, abs=1e-6)
    assert view_height >= (max_y - min_y)              # vertical coverage
    assert view_height * aspect >= (max_x - min_x)     # horizontal coverage


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


@pytest.mark.parametrize("bad", ["\x00", "\x1b", "é"])
def test_as3_sanitizer_rejects_forbidden_bytes(bad):
    """A CR/LF-only sanitizer would survive test_as3_newline_injection_refused;
    this pins NUL, ESC and a non-ASCII char as typed refusals at the emit choke
    point (allowlist 0x20-0x7E), so weakening the guard to newlines reddens it."""
    doc = DxfDocument(
        layers=d.LAYER_DEFINITIONS,
        texts=[
            TextLabel(
                layer="ANNOTATION",
                position=(0.0, 0.0, 0.0),
                height=1.0,
                text=f"LABEL{bad}X",
            )
        ],
    )
    with pytest.raises(DxfSanitizationError):
        serialize_document(doc)


def test_as3_builder_refuses_over_cap_floor_count_before_allocating():
    """Over-cap floor count is a typed refusal BEFORE any ring/face/line is
    materialized (G5 F1). MAX_FLOORS+1 builds successfully if the pre-check is
    removed (so this test guards the pre-check), and a 10-million-floor request
    refuses in O(1) with no multi-gigabyte allocation."""
    with pytest.raises(DxfValidationError) as exc:
        build_site_plan_document(LOT, BUILDING, [1.0] * (d.MAX_FLOORS + 1))
    assert exc.value.code == "floor_cap_exceeded"
    with pytest.raises(DxfValidationError) as exc2:
        build_site_plan_document(LOT, BUILDING, [1.0] * 10_000_000)
    assert exc2.value.code == "floor_cap_exceeded"


def test_as3_coordinate_magnitude_bound_refused():
    """A finite but astronomically large coordinate is a typed refusal at the
    numeric choke point (mirrors the PDF writer's 1e8 bound), not a ~300-digit
    token that would confuse AutoCAD."""
    big = d.MAX_COORD_ABS * 10.0
    with pytest.raises(DxfValidationError) as exc:
        render_site_plan_dxf(
            [(0.0, 0.0), (big, 0.0), (big, big), (0.0, big)],
            BUILDING,
            FLOOR_HEIGHTS,
        )
    assert exc.value.code == "coordinate_out_of_range"


# --------------------------------------------------------------------------- #
# AS-4 honesty.
# --------------------------------------------------------------------------- #

def test_as4_annotation_carries_required_labels():
    text = _render()
    # Pin the exact honesty strings as HARDCODED literals in the SERIALIZED
    # output (mirrors the pdf_sheet_writer honesty tests). Asserting
    # `PROPOSED_LABEL in text` would ship green even if the constant were
    # weakened, so assert the literal bytes AND pin the constants themselves.
    assert "PROPOSED - NOT A CITY RECORD" in text
    assert "COORDINATES: EPSG:2263 NAD83 NY LONG ISLAND - US SURVEY FEET" in text
    assert PROPOSED_LABEL == "PROPOSED - NOT A CITY RECORD"
    assert CRS_UNITS_NOTE == "COORDINATES: EPSG:2263 NAD83 NY LONG ISLAND - US SURVEY FEET"


def test_as4_no_claim_class_words_anywhere():
    upper = _render().upper()
    for word in CLAIM_CLASS_WORDS:
        assert word not in upper, f"claim-class word leaked: {word}"
    # Spot-check words the honesty directive names explicitly.
    for banned in ("PERMITTED", "APPROVED", "MAXIMUM ALLOWED"):
        assert banned not in upper


def test_as4_claim_word_guard_is_load_bearing(monkeypatch):
    """Feed a claim word through the builder's _assert_no_claim_words path: a
    barred word in ANY annotation message is a typed refusal, never emitted.
    Neutering _assert_no_claim_words (or dropping the word) reddens this test."""
    monkeypatch.setattr(d, "GENERATOR_NOTE", "APPROVED MAXIMUM ALLOWED BUILDING")
    with pytest.raises(DxfValidationError) as exc:
        build_site_plan_document(LOT, BUILDING, FLOOR_HEIGHTS)
    assert exc.value.code == "claim_class_word"


def test_as4_claim_class_words_are_the_expected_set():
    """Pin the full barred-word set as a hardcoded literal so dropping a word
    (weakening the guard) reddens this test rather than shipping green."""
    assert CLAIM_CLASS_WORDS == (
        "PERMITTED",
        "APPROVED",
        "CERTIFIED",
        "COMPLIANT",
        "LAWFUL",
        "LEGAL",
        "ENTITLEMENT",
        "GUARANTEED",
        "MAXIMUM ALLOWED",
        "AS OF RIGHT",
        "AS-OF-RIGHT",
    )


# --------------------------------------------------------------------------- #
# AS-4 import allowlist: only __future__, math, collections.abc and dataclasses
# may be imported (widens the former stdlib-only test into an allowlist, so a
# DWG-library / json / any-other import reddens it - DB-057 f).
# --------------------------------------------------------------------------- #

#: The ONLY modules dxf_writer.py may import (the module has no self-imports).
IMPORT_ALLOWLIST = frozenset({"__future__", "math", "collections.abc", "dataclasses"})


def _imported_modules(source: str) -> set[str]:
    """Every module named by an ``import`` / ``from ... import`` in ``source``."""
    modules: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None and node.level == 0:
            modules.add(node.module)
    return modules


def test_as4_module_import_allowlist():
    imported = _imported_modules(Path(d.__file__).read_text(encoding="utf-8"))
    outside = imported - IMPORT_ALLOWLIST
    assert not outside, f"imports outside the allowlist: {sorted(outside)}"
    # Non-vacuous: the module really does import each allowlisted stdlib name, so
    # a test that stopped seeing imports at all would fail too.
    missing = IMPORT_ALLOWLIST - imported
    assert not missing, f"missing allowlisted import(s): {sorted(missing)}"


def test_as4_allowlist_is_load_bearing():
    """The allowlist catches an out-of-allowlist import: parsing the module source
    with `import json` prepended yields `json`, which the allowlist rejects
    (mirrors the AS-4 mutation 'adding import json reddens it')."""
    mutated = "import json\n" + Path(d.__file__).read_text(encoding="utf-8")
    assert _imported_modules(mutated) - IMPORT_ALLOWLIST == {"json"}
