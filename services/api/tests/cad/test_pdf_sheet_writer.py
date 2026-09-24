"""Acceptance tests for the deterministic PDF site-plan sheet writer (M5-T085).

Covers AS-1 structure/determinism (golden sha256 + independently parsed xref
offsets), AS-2 round-trip through the in-repo strict survey reader (exact
segment/rect counts and text runs), AS-3 measurement (dimension strings, chosen
scale, printed units/CRS/grid-north), AS-4 fail-closed refusals + the single
string escaper (with an in-process escaper-bypass mutant), and AS-5 honesty +
scope (the PROPOSED / professional-review stamps, never 'true north').

The strict reader lives in ``app.documents.extraction``. Importing that package
normally pulls in pipeline modules that use Python 3.12 syntax; CI runs 3.12 and
the plain import works. Under a 3.11 developer sandbox that import raises
``SyntaxError`` at an unrelated module, so :func:`_reader` falls back to loading
the SELF-CONTAINED reader subgraph (lexer/objects/xref/container/content) directly
from the same source files -- the identical reader code, without the 3.12-only
pipeline modules.
"""

import hashlib
import importlib.util
import sys
import types
from pathlib import Path

import pytest

from app.cad import pdf_sheet_writer as writer
from app.cad.pdf_sheet_writer import SitePlanInput, render_site_plan_pdf

_GOLDEN_SHA256 = "c38360f9b803299c75dd837ec65de3e3a4dc046a11aa2bcb386fe74aa5312db2"

_READER: types.SimpleNamespace | None = None


def _reader() -> types.SimpleNamespace:
    """Return the strict reader surface, sideloading it under a 3.11 sandbox."""
    global _READER
    if _READER is not None:
        return _READER
    try:
        from app.documents.extraction.pdf_container import PdfDocument, read_pdf_container
        from app.documents.extraction.pdf_content import PageContent, interpret_content
    except SyntaxError:
        read_pdf_container, PdfDocument, interpret_content, PageContent = _sideload()
    _READER = types.SimpleNamespace(
        read_pdf_container=read_pdf_container,
        interpret_content=interpret_content,
        PdfDocument=PdfDocument,
        PageContent=PageContent,
    )
    return _READER


def _sideload():
    """Load the reader subgraph from source without the 3.12-only pipeline __init__."""
    base = Path(writer.__file__).resolve().parents[1] / "documents" / "extraction"
    pkg = "app.documents.extraction"
    for name in ("app.documents", pkg):
        if name not in sys.modules or getattr(sys.modules[name], "__file__", None):
            module = types.ModuleType(name)
            module.__path__ = []
            sys.modules[name] = module
    sys.modules["app"].documents = sys.modules["app.documents"]
    sys.modules["app.documents"].extraction = sys.modules[pkg]
    for name in ("pdf_lexer", "pdf_objects", "pdf_xref", "pdf_container", "pdf_content"):
        full = f"{pkg}.{name}"
        spec = importlib.util.spec_from_file_location(full, base / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        module.__package__ = pkg
        sys.modules[full] = module
        setattr(sys.modules[pkg], name, module)
        spec.loader.exec_module(module)
    container = sys.modules[f"{pkg}.pdf_container"]
    content = sys.modules[f"{pkg}.pdf_content"]
    return (
        container.read_pdf_container,
        container.PdfDocument,
        content.interpret_content,
        content.PageContent,
    )


def _spec(**overrides) -> SitePlanInput:
    base = {
        "lot_ring": ((0.0, 0.0), (30.0, 0.0), (30.0, 100.0), (0.0, 100.0)),
        "building_ring": ((5.0, 20.0), (25.0, 20.0), (25.0, 80.0), (5.0, 80.0)),
        "address": "12 MAIN ST",
        "bbl": "1-00123-0045",
        "generated_at": "2026-09-24T00:00:00Z",
        "generator_version": "site-plan-writer/1.0.0",
    }
    base.update(overrides)
    return SitePlanInput(**base)


def _rendered(**overrides) -> bytes:
    pdf = render_site_plan_pdf(_spec(**overrides))
    assert isinstance(pdf, bytes)
    return pdf


# -- AS-1: structure + determinism ---------------------------------------------


def test_valid_pdf_structure_markers():
    pdf = _rendered()
    assert pdf.startswith(b"%PDF-1.4\n")
    assert pdf.endswith(b"%%EOF")
    assert b"\nxref\n" in pdf
    assert b"\ntrailer\n" in pdf
    assert b"\nstartxref\n" in pdf
    assert b"/Root 1 0 R" in pdf


def test_deterministic_bytes_no_clock():
    assert _rendered() == _rendered()


def test_golden_sha256():
    assert hashlib.sha256(_rendered()).hexdigest() == _GOLDEN_SHA256


def test_xref_offsets_point_at_object_headers():
    """Independently parse the classic xref table; each offset must locate 'N 0 obj'."""
    pdf = _rendered()
    start = pdf.rfind(b"startxref")
    xref_offset = int(pdf[start + len(b"startxref"):].split(b"%%EOF")[0].strip())
    assert pdf[xref_offset:xref_offset + 4] == b"xref"
    header = pdf[xref_offset:].split(b"\n", 2)
    first, count = (int(v) for v in header[1].split())
    assert first == 0
    entries_blob = pdf[xref_offset + len(header[0]) + 1 + len(header[1]) + 1:]
    for i in range(count):
        entry = entries_blob[i * 20:i * 20 + 20]
        offset = int(entry[0:10])
        in_use = entry[17:18] == b"n"
        if in_use:
            assert pdf[offset:offset + len(f"{i} 0 obj".encode())] == f"{i} 0 obj".encode()


# -- AS-2: round-trip through the in-repo strict reader -------------------------


def test_roundtrip_reader_accepts_and_counts():
    reader = _reader()
    pdf = _rendered()
    doc = reader.read_pdf_container(pdf)
    assert isinstance(doc, reader.PdfDocument)
    assert len(doc.pages) == 1
    page = reader.interpret_content(doc.pages[0].content)
    assert isinstance(page, reader.PageContent)

    lot_n, bld_n = 4, 4
    expected_segments = (
        lot_n + bld_n + writer._SCALE_BAR_SEGMENTS + writer._NORTH_ARROW_SEGMENTS
    )
    expected_texts = (
        lot_n + bld_n + writer._SCALE_BAR_LABELS
        + writer._NORTH_ARROW_LABELS + writer._TITLE_BLOCK_LINES
    )
    assert len(page.segments) == expected_segments
    assert len(page.rects) == writer._SHEET_RECTS
    assert len(page.text_runs) == expected_texts


# -- AS-3: measurement ----------------------------------------------------------


def test_dimension_strings_from_2263_feet():
    reader = _reader()
    doc = reader.read_pdf_container(_rendered())
    page = reader.interpret_content(doc.pages[0].content)
    texts = [run.text for run in page.text_runs]
    for expected in ("30.00", "100.00", "20.00", "60.00"):
        assert texts.count(expected) >= 1


def test_choose_scale_fits_sheet():
    # 30 x 100 ft fits at 1in=20ft (tightest standard scale that fits the sheet).
    assert writer.choose_scale(30.0, 100.0) == 20.0
    assert writer.choose_scale(1.0, 1.0) == writer.SCALE_CANDIDATES_FT_PER_IN[0]


def test_units_crs_scale_and_grid_north_printed():
    reader = _reader()
    doc = reader.read_pdf_container(_rendered())
    page = reader.interpret_content(doc.pages[0].content)
    joined = "\n".join(run.text for run in page.text_runs)
    assert "US survey feet" in joined
    assert "EPSG:2263" in joined
    assert "Scale: 1 in = 20 ft" in joined
    assert "grid north" in joined


# -- AS-4: fail-closed refusals + the single escaper ---------------------------


@pytest.mark.parametrize(
    "ring, code",
    [
        (((0.0, 0.0), (1.0, 0.0)), "invalid_ring"),
        (((0.0, 0.0), (float("nan"), 0.0), (1.0, 1.0)), "non_finite_coordinate"),
        (((0.0, 0.0), (float("inf"), 0.0), (1.0, 1.0)), "non_finite_coordinate"),
        (((0.0, 0.0), (2.0e8, 0.0), (2.0e8, 1.0)), "oversize_input"),
    ],
)
def test_invalid_rings_are_typed_refusals(ring, code):
    result = render_site_plan_pdf(_spec(lot_ring=ring, building_ring=None))
    assert isinstance(result, writer.SitePlanRefusal)
    assert result.reject_code == code


def test_too_many_vertices_refused():
    big = tuple((float(i), float(i % 5)) for i in range(writer._MAX_RING_VERTICES + 1))
    result = render_site_plan_pdf(_spec(lot_ring=big, building_ring=None))
    assert isinstance(result, writer.SitePlanRefusal)
    assert result.reject_code == "oversize_input"


def test_geometry_larger_than_any_scale_refused():
    huge = ((0.0, 0.0), (300000.0, 0.0), (300000.0, 900000.0), (0.0, 900000.0))
    result = render_site_plan_pdf(_spec(lot_ring=huge, building_ring=None))
    assert isinstance(result, writer.SitePlanRefusal)
    assert result.reject_code == "oversize_input"


def test_special_characters_round_trip_through_escaper():
    reader = _reader()
    address = r"12 MAIN ST \ (REAR)"
    doc = reader.read_pdf_container(_rendered(address=address))
    page = reader.interpret_content(doc.pages[0].content)
    assert isinstance(page, reader.PageContent)
    assert any(run.text == f"SITE: {address}" for run in page.text_runs)


def test_escaper_bypass_mutant_reddens_roundtrip(monkeypatch):
    """Bypassing the single escaper must break the content round-trip (mutation guard)."""
    reader = _reader()
    address = r"12 MAIN ST \ (REAR)"

    # Baseline: the real escaper yields interpretable content.
    good = reader.interpret_content(
        reader.read_pdf_container(_rendered(address=address)).pages[0].content
    )
    assert isinstance(good, reader.PageContent)

    # Mutant: ASCII-sanitise only, no ( ) \ escaping -> unbalanced literal string.
    monkeypatch.setattr(
        writer,
        "_escape_pdf_text",
        lambda text: "".join(c if 0x20 <= ord(c) <= 0x7E else "?" for c in text),
    )
    mutant_pdf = render_site_plan_pdf(_spec(address=address))
    assert isinstance(mutant_pdf, bytes)
    mutant_doc = reader.read_pdf_container(mutant_pdf)
    assert isinstance(mutant_doc, reader.PdfDocument)  # container still well-formed
    mutant_content = reader.interpret_content(mutant_doc.pages[0].content)
    assert not isinstance(mutant_content, reader.PageContent)  # content now refused


def test_xref_offset_corruption_is_detected(monkeypatch):
    """Corrupting one recorded xref offset must make the strict reader refuse."""
    reader = _reader()
    pdf = _rendered()
    xref_offset = pdf.rfind(b"\nxref\n") + 1
    header = pdf[xref_offset:].split(b"\n", 2)
    entries_start = xref_offset + len(header[0]) + 1 + len(header[1]) + 1
    first_in_use = entries_start + 20  # entry index 1 (object 0 is the free entry)
    corrupt = bytearray(pdf)
    corrupt[first_in_use:first_in_use + 10] = b"0000009999"
    result = reader.read_pdf_container(bytes(corrupt))
    assert not isinstance(result, reader.PdfDocument)


# -- AS-5: honesty + scope ------------------------------------------------------


def test_proposed_and_professional_review_stamps_always_present():
    reader = _reader()
    doc = reader.read_pdf_container(_rendered(building_ring=None))
    page = reader.interpret_content(doc.pages[0].content)
    texts = [run.text for run in page.text_runs]
    assert "PROPOSED - NOT A CITY RECORD" in texts
    assert "Not for construction - professional review required" in texts


def test_never_claims_true_north():
    reader = _reader()
    doc = reader.read_pdf_container(_rendered())
    page = reader.interpret_content(doc.pages[0].content)
    joined = "\n".join(run.text for run in page.text_runs).lower()
    assert "true north" not in joined
    assert "grid n (epsg:2263)" in joined.lower()
