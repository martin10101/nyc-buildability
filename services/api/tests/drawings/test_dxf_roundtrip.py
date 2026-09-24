"""Committed writer -> reader round trip (M5-T097, D-087 CAD-3; closes DB-057 (h) / the
missing D-087-R006 harness that was previously proven only ad hoc, M5-T081-DCV F2).

The accepted DXF writer (``app.cad.dxf_writer.render_site_plan_dxf``) is used READ-ONLY: its
site-plan output is read back by the strict-subset reader and the HEADER + ENTITIES content is
asserted - the lot and building rings exact and closed, the units read from the header, the
written layers, the per-type entity counts, and the honesty texts. The reader skips the whole
TABLES section, so this test deliberately does NOT pin the TABLES contents or any writer golden
digest (M5-T096 is adding STYLE/VPORT tables to the writer in parallel; that must not break the
round trip). AS-4.
"""

from __future__ import annotations

from app.cad.dxf_writer import (
    CRS_UNITS_NOTE,
    GENERATOR_NOTE,
    LAYER_ANNOTATION,
    LAYER_BUILDING_OUTLINE,
    LAYER_LOT,
    LAYER_MASSING_3D,
    PROPOSED_LABEL,
    render_site_plan_dxf,
)
from app.drawings.dxf_reader import (
    DxfDocument,
    FacePrimitive,
    LinePrimitive,
    PolylinePrimitive,
    TextPrimitive,
    read_dxf,
)

# EPSG:2263-scale (US survey feet) open rings; every coordinate distinct so the perturbation
# probe can target one vertex unambiguously. A simple, positive-area quadrilateral each.
_LOT = ((1000.0, 2000.0), (1500.0, 2100.0), (1400.0, 2600.0), (900.0, 2500.0))
_BUILDING = ((1100.0, 2150.0), (1350.0, 2200.0), (1300.0, 2450.0), (1050.0, 2400.0))
_FLOORS = (12.0, 11.0, 10.0)

_EDGES = len(_BUILDING)
_N_FLOORS = len(_FLOORS)


def _read_site_plan(dxf_text: str) -> DxfDocument:
    result = read_dxf(dxf_text)
    assert isinstance(result, DxfDocument), f"expected a document, got {result!r}"
    return result


def _polys_on(doc: DxfDocument, layer: str) -> list[PolylinePrimitive]:
    return [p for p in doc.primitives if isinstance(p, PolylinePrimitive) and p.layer == layer]


# --------------------------------------------------------------------------- AS-4 round trip


def test_roundtrip_header_units_read_from_writer_output() -> None:
    """HEADER: the writer declares US survey feet (code 21); the reader reads it back from
    the header, never assuming feet, and reports the AutoCAD version string."""
    doc = _read_site_plan(render_site_plan_dxf(_LOT, _BUILDING, _FLOORS))
    assert doc.ok is True
    assert doc.units.code == 21
    assert doc.units.name == "us_survey_feet"
    assert doc.units.source == "header:$INSUNITS"
    assert doc.acad_version == "AC1009"


def test_roundtrip_tables_section_is_skipped_not_pinned() -> None:
    """The reader skips the whole TABLES section (recorded), so the writer growing its TABLES
    (M5-T096 STYLE/VPORT) cannot break the round trip. No ENTITIES type is disclosed-unknown."""
    doc = _read_site_plan(render_site_plan_dxf(_LOT, _BUILDING, _FLOORS))
    assert "TABLES" in doc.skipped_sections
    assert doc.disclosed_unknown == ()


def test_roundtrip_lot_ring_exact_and_closed() -> None:
    """ENTITIES: the lot footprint comes back as exactly one closed polyline whose vertices
    equal the written open ring, in order (exact float equality - the writer's 6-decimal
    format round-trips these values)."""
    doc = _read_site_plan(render_site_plan_dxf(_LOT, _BUILDING, _FLOORS))
    lot_polys = _polys_on(doc, LAYER_LOT)
    assert len(lot_polys) == 1
    (lot,) = lot_polys
    assert lot.closed is True
    assert lot.vertices == _LOT


def test_roundtrip_building_ring_exact_and_closed() -> None:
    doc = _read_site_plan(render_site_plan_dxf(_LOT, _BUILDING, _FLOORS))
    bldg_polys = _polys_on(doc, LAYER_BUILDING_OUTLINE)
    assert len(bldg_polys) == 1
    (bldg,) = bldg_polys
    assert bldg.closed is True
    assert bldg.vertices == _BUILDING


def test_roundtrip_layers_and_entity_counts_as_written() -> None:
    """Layer names and per-type entity counts match what the writer emitted: LOT + building
    outline (1 polyline each), one MASSING_3D band polyline per elevation (floors + 1), one
    3DFACE wall per building edge per floor, one vertical LINE per building corner, and the
    three ANNOTATION honesty labels."""
    doc = _read_site_plan(render_site_plan_dxf(_LOT, _BUILDING, _FLOORS))

    assert len(_polys_on(doc, LAYER_LOT)) == 1
    assert len(_polys_on(doc, LAYER_BUILDING_OUTLINE)) == 1
    # Massing wireframe: one closed outline polyline at each band elevation (floors + 1).
    assert len(_polys_on(doc, LAYER_MASSING_3D)) == _N_FLOORS + 1

    faces = [p for p in doc.primitives if isinstance(p, FacePrimitive)]
    assert len(faces) == _EDGES * _N_FLOORS
    assert all(f.layer == LAYER_MASSING_3D for f in faces)

    lines = [p for p in doc.primitives if isinstance(p, LinePrimitive)]
    assert len(lines) == _EDGES
    assert all(ln.layer == LAYER_MASSING_3D for ln in lines)

    texts = [p for p in doc.primitives if isinstance(p, TextPrimitive)]
    assert all(t.layer == LAYER_ANNOTATION for t in texts)

    # Total ENTITIES-section entities (parsed + disclosed): all types accounted for.
    expected_entities = (
        (2 + (_N_FLOORS + 1))  # LOT + BUILDING_OUTLINE + massing band polylines
        + (_EDGES * _N_FLOORS)  # 3DFACE wall quads
        + _EDGES  # vertical corner LINEs
        + len(texts)  # annotation labels
    )
    assert doc.entity_count == expected_entities


def test_roundtrip_honesty_texts_present() -> None:
    """The fixed provenance/honesty labels survive the round trip verbatim on the annotation
    layer (D-073-R006 / D-083 vocabulary)."""
    doc = _read_site_plan(render_site_plan_dxf(_LOT, _BUILDING, _FLOORS))
    texts = {p.text for p in doc.primitives if isinstance(p, TextPrimitive)}
    assert PROPOSED_LABEL in texts
    assert CRS_UNITS_NOTE in texts
    assert GENERATOR_NOTE in texts


# ------------------------------------------------------ AS-4 MUTATION: perturb a ring vertex


def test_mutation_roundtrip_perturbed_lot_vertex_reddens() -> None:
    """MUTATION (AS-4): perturbing one lot-ring vertex in the writer OUTPUT changes the ring
    the reader reads back, so the exact-ring assertion in
    ``test_roundtrip_lot_ring_exact_and_closed`` has teeth. We bump the lot polyline's first
    vertex X by a whole foot in the serialized text, re-read, and confirm the round-trip lot
    ring is no longer equal to the written ring (and that only that one coordinate moved)."""
    dxf_text = render_site_plan_dxf(_LOT, _BUILDING, _FLOORS)

    # Locate the LOT ring's first VERTEX x value in the serialized stream. The writer emits
    # LF-terminated group-code lines; this marker is the first LOT vertex's group-10 pair.
    marker = "0\nVERTEX\n8\nLOT\n10\n"
    start = dxf_text.find(marker)
    assert start != -1, "expected a LOT VERTEX in the writer output"
    val_start = start + len(marker)
    val_end = dxf_text.index("\n", val_start)
    original_x = dxf_text[val_start:val_end]
    assert float(original_x) == _LOT[0][0]

    perturbed_x = f"{_LOT[0][0] + 1.0:.6f}"
    perturbed = dxf_text[:val_start] + perturbed_x + dxf_text[val_end:]
    assert perturbed != dxf_text

    doc = _read_site_plan(perturbed)
    (lot,) = _polys_on(doc, LAYER_LOT)
    # The exact-ring assertion would now FAIL: the first vertex moved by one foot.
    assert lot.vertices != _LOT
    assert lot.vertices[0] == (_LOT[0][0] + 1.0, _LOT[0][1])
    # Every other vertex is unchanged, so the difference is exactly the perturbation.
    assert lot.vertices[1:] == _LOT[1:]
