"""Acceptance tests for the deterministic PDF site-plan sheet writer (M5-T085).

Covers AS-1 structure/determinism (golden sha256 + independently parsed xref
offsets), AS-2 round-trip through the in-repo strict survey reader (exact
segment/rect counts and text runs), AS-3 measurement (dimension strings, chosen
scale, printed units/CRS/grid-north), AS-4 fail-closed refusals + the single
string escaper (with an in-process escaper-bypass mutant), and AS-5 honesty +
scope (the PROPOSED / professional-review stamps, never 'true north').

M5-T091 hardening (DB-053 a-d, sections at the end): H-1 malformed rings/vertices
and any hostile field value are typed refusals, never exceptions; H-2 the number
formatter refuses non-finite values; H-3 caller text is screened for the DXF
writer's claim-class words (set pinned by hardcoded literals) with nothing
emitted; H-4 unbalanced-paren text round-trips exactly through the writer and
the strict reader, with in-process paren-skipping escaper mutants proving the
fixtures have teeth.

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
import math
import numbers
import sys
import types
from decimal import Decimal
from pathlib import Path

import pytest

from app.cad import claim_words, dxf_writer
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
        # DB-059 (d): the non-finite check covers Y, not only X.
        (((0.0, 0.0), (1.0, float("nan")), (1.0, 1.0)), "non_finite_coordinate"),
        (((0.0, 0.0), (1.0, float("inf")), (1.0, 1.0)), "non_finite_coordinate"),
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


# -- M5-T091 H-1 (DB-053 a): malformed input is a typed refusal, never a raise ----

_LOT = ((0.0, 0.0), (30.0, 0.0), (30.0, 100.0), (0.0, 100.0))
_BUILDING = ((5.0, 20.0), (25.0, 20.0), (25.0, 80.0), (5.0, 80.0))


@pytest.mark.parametrize(
    "vertex, code",
    [
        (("a", 0.0), "non_numeric_coordinate"),
        ((0.0, "1.5"), "non_numeric_coordinate"),  # numeric TEXT is refused, never parsed
        ((None, 0.0), "non_numeric_coordinate"),
        ((True, 0.0), "non_numeric_coordinate"),
        ((1j, 0.0), "non_numeric_coordinate"),
        (([1.0], 0.0), "non_numeric_coordinate"),
        ((Decimal("1.5"), 0.0), "non_numeric_coordinate"),
        ((), "invalid_ring"),
        ((1.0,), "invalid_ring"),
        ((1.0, 2.0, 3.0), "invalid_ring"),
        (5, "invalid_ring"),
        (None, "invalid_ring"),
        (1.5, "invalid_ring"),
        ("12", "invalid_ring"),
        (b"\x01\x02", "invalid_ring"),
        ({1.0, 2.0}, "invalid_ring"),
        ({0: 1.0, 1: 2.0}, "invalid_ring"),
        (object(), "invalid_ring"),
        ((10**400, 0.0), "oversize_input"),  # an int beyond the float range
    ],
)
@pytest.mark.parametrize("ring_field, ring", [("lot_ring", _LOT), ("building_ring", _BUILDING)])
def test_malformed_vertex_is_a_typed_refusal_never_raises(ring_field, ring, vertex, code):
    bad_ring = ring[:2] + (vertex,) + ring[3:]
    result = render_site_plan_pdf(_spec(**{ring_field: bad_ring}))
    assert isinstance(result, writer.SitePlanRefusal)
    assert result.reject_code == code


@pytest.mark.parametrize(
    "ring",
    [None, 5, 1.5, "abcd", b"abcd", object(), {"a": 1}, set(_LOT), (p for p in _LOT)],
)
def test_malformed_lot_ring_container_is_a_typed_refusal(ring):
    result = render_site_plan_pdf(_spec(lot_ring=ring))
    assert isinstance(result, writer.SitePlanRefusal)
    assert result.reject_code == "invalid_ring"


def test_list_rings_and_int_coordinates_still_render_identically():
    """Accepted behaviour kept: lists and ints are valid sequences/reals (same bytes)."""
    as_lists = [[int(x), int(y)] for x, y in _LOT]
    assert _rendered(lot_ring=as_lists) == _rendered()


@pytest.mark.parametrize("spec", [None, {"lot_ring": _LOT}, "spec", 5])
def test_non_spec_argument_is_a_typed_refusal(spec):
    result = render_site_plan_pdf(spec)
    assert isinstance(result, writer.SitePlanRefusal)
    assert result.reject_code == "invalid_input"


@pytest.mark.parametrize(
    "field", ["address", "bbl", "generated_at", "generator_version"]
)
@pytest.mark.parametrize("value", [None, 1001230045, b"12 MAIN ST", ["12 MAIN ST"]])
def test_non_string_caller_text_is_a_typed_refusal(field, value):
    result = render_site_plan_pdf(_spec(**{field: value}))
    assert isinstance(result, writer.SitePlanRefusal)
    assert result.reject_code == "invalid_text"
    assert field in result.detail


_HOSTILE_VALUES = (
    None, True, 0, 1.5, float("nan"), "x", b"x", (), [], {}, set(), object(),
    (1.0, 2.0), ((1.0, 2.0),), ((1.0, 2.0), (3.0, 4.0), ("x", 5.0)),
)


@pytest.mark.parametrize(
    "field",
    ["lot_ring", "building_ring", "address", "bbl", "generated_at", "generator_version"],
)
def test_any_hostile_field_value_returns_bytes_or_refusal(field):
    """The docstring's 'never raises on caller data' promise, swept per field."""
    for value in _HOSTILE_VALUES:
        result = render_site_plan_pdf(_spec(**{field: value}))
        assert isinstance(result, (bytes, writer.SitePlanRefusal)), (field, value)


# -- M5-T091 H-2 (DB-053 b): the number formatter refuses non-finite values -------


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_number_formatter_refuses_non_finite(value):
    with pytest.raises(writer._RenderRefused) as caught:
        writer._num(value)
    assert caught.value.refusal.reject_code == "non_finite_value"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
@pytest.mark.parametrize("constant", ["_TITLE_FONT_PT", "_SHEET_W"])
def test_non_finite_drawing_number_is_a_typed_refusal_not_a_token(
    monkeypatch, constant, value
):
    """Forced past the ring checks, a non-finite number returns a refusal, no bytes."""
    monkeypatch.setattr(writer, constant, value)
    result = render_site_plan_pdf(_spec())
    assert isinstance(result, writer.SitePlanRefusal)
    assert result.reject_code == "non_finite_value"


def test_number_formatter_unchanged_for_finite_values():
    assert writer._num(12.0) == "12"
    assert writer._num(1.23456) == "1.235"
    assert writer._num(-0.0) == "0"
    assert writer._num(-0.0001) == "0"
    assert writer._num(-7.5) == "-7.5"


# -- M5-T091 H-3 (DB-053 c): claim-class screen on caller text --------------------

# HARDCODED on purpose (a by-value import would make the pin tautological).
_PINNED_CLAIM_WORDS = (
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
_TEXT_FIELDS = ("address", "bbl", "generated_at", "generator_version")


@pytest.fixture
def build_calls(monkeypatch):
    """Record every content-stream build, so a refusal can prove nothing was drawn."""
    calls: list[object] = []
    real = writer._build_content

    def spy(*args, **kwargs):
        calls.append(args)
        return real(*args, **kwargs)

    monkeypatch.setattr(writer, "_build_content", spy)
    return calls


def test_claim_word_set_is_the_dxf_writers_pinned_set():
    # M5-T102: one canonical list lives in app.cad.claim_words; the PDF and DXF
    # writers both alias it, so all three share one identity-equal vocabulary.
    assert writer.CLAIM_CLASS_WORDS is claim_words.CLAIM_CLASS_WORDS
    assert dxf_writer.CLAIM_CLASS_WORDS is claim_words.CLAIM_CLASS_WORDS
    assert writer.CLAIM_CLASS_WORDS is dxf_writer.CLAIM_CLASS_WORDS  # one vocabulary
    assert tuple(writer.CLAIM_CLASS_WORDS) == _PINNED_CLAIM_WORDS
    # the PDF writer screens via the shared function, not a local matcher.
    assert writer.contains_claim_word is claim_words.contains_claim_word
    assert not hasattr(writer, "_claim_key")


def test_as2_removing_the_title_block_screen_lets_claim_word_through(monkeypatch, build_calls):
    """AS-2 mutation (in-process, consuming namespace): with the shared screen
    neutered in the pdf_sheet_writer namespace, a claim word in the title-block
    address is NO LONGER refused and reaches the sheet - so the title-block screen
    is genuinely load-bearing (DB-053 (c))."""
    result = render_site_plan_pdf(_spec(address="12 maximum allowed st"))
    assert isinstance(result, writer.SitePlanRefusal)  # real screen refuses it
    assert result.reject_code == "claim_class_word"
    assert build_calls == []  # nothing drawn on the refusal

    monkeypatch.setattr(writer, "contains_claim_word", lambda *texts: None)
    mutated = render_site_plan_pdf(_spec(address="12 maximum allowed st"))
    assert isinstance(mutated, bytes)  # the claim word now slips through -> renders


@pytest.mark.parametrize("word", _PINNED_CLAIM_WORDS)
@pytest.mark.parametrize("field", _TEXT_FIELDS)
def test_claim_word_in_caller_text_is_refused_nothing_emitted(build_calls, field, word):
    text = f"12 {word.lower()} st"
    result = render_site_plan_pdf(_spec(**{field: text}))
    assert isinstance(result, writer.SitePlanRefusal)
    assert result.reject_code == "claim_class_word"
    assert field in result.detail
    assert text not in result.detail  # the caller's text is never echoed
    assert build_calls == []


@pytest.mark.parametrize(
    "address",
    [
        "12 AS_OF_RIGHT ST",
        "12 maximum  allowed ave",
        "12 As.Of.Right PL",
        "12 MAXIMUM\tALLOWED ST",
        "12 Pre-Approved Way",
        "AS ſOF RIGHT",  # prints as 'AS ?OF RIGHT': the printed form is screened too
    ],
)
def test_claim_word_separator_variants_are_refused(build_calls, address):
    result = render_site_plan_pdf(_spec(address=address))
    assert isinstance(result, writer.SitePlanRefusal)
    assert result.reject_code == "claim_class_word"
    assert build_calls == []


@pytest.mark.parametrize("address", ["12 MAIN ST", "12 PERMIT ST", "1 LEGACY PL"])
def test_clean_caller_text_still_renders(build_calls, address):
    assert isinstance(render_site_plan_pdf(_spec(address=address)), bytes)
    assert len(build_calls) == 1  # the spy is live, so the refusal checks are not vacuous


# -- M5-T091 H-4 (DB-053 d): unbalanced parens round-trip exactly ------------------

_UNBALANCED_TEXTS = (
    "12 MAIN ST (REAR",
    "12 MAIN ST REAR)",
    "(",
    ")",
    ")(",
    "((",
    "a)b(c",
    "12 MAIN ST \\",
    "\\(",
    "\\)",
    "12 MAIN ST \\ (REAR",  # DB-053 (d): unbalanced '(' AND a backslash together
    "\\)a(\\",             # backslashes wrapping an unbalanced ')...(' run
)


@pytest.mark.parametrize("text", _UNBALANCED_TEXTS)
@pytest.mark.parametrize("field, prefix", [("address", "SITE: "), ("bbl", "BBL: ")])
def test_unbalanced_parens_round_trip_through_writer_and_reader(field, prefix, text):
    reader = _reader()
    doc = reader.read_pdf_container(_rendered(**{field: text}))
    assert isinstance(doc, reader.PdfDocument)
    page = reader.interpret_content(doc.pages[0].content)
    assert isinstance(page, reader.PageContent)
    assert [run.text for run in page.text_runs].count(f"{prefix}{text}") == 1


def _escaper_skipping(skipped: str):
    """An idiomatic weakening: sanitise + escape, but forget the chars in ``skipped``."""

    def mutant(text: str) -> str:
        return "".join(
            "\\" + ch if ch in "()\\" and ch not in skipped else ch
            for ch in writer._ascii_sanitise(text)
        )

    return mutant


@pytest.mark.parametrize(
    "skipped, text",
    [("(", "12 MAIN ST (REAR"), (")", "12 MAIN ST REAR)"), ("()", "12 MAIN ST (REAR")],
)
def test_paren_skipping_escaper_mutant_breaks_unbalanced_roundtrip(monkeypatch, skipped, text):
    """The unbalanced fixtures see an escaper that forgets a lone paren (G4 EB survivor)."""
    reader = _reader()
    monkeypatch.setattr(writer, "_escape_pdf_text", _escaper_skipping(skipped))
    mutant_pdf = render_site_plan_pdf(_spec(address=text))
    assert isinstance(mutant_pdf, bytes)
    doc = reader.read_pdf_container(mutant_pdf)
    page = (
        reader.interpret_content(doc.pages[0].content)
        if isinstance(doc, reader.PdfDocument)
        else doc
    )
    faithful = isinstance(page, reader.PageContent) and any(
        run.text == f"SITE: {text}" for run in page.text_runs
    )
    assert not faithful


# -- M5-T105 AS-1 (DB-059 a): every caller text field is length-bounded -------------


@pytest.mark.parametrize("field", _TEXT_FIELDS)
def test_over_long_caller_text_is_refused_nothing_drawn(build_calls, field):
    """An over-cap field is a typed refusal that NAMES the field, returned BEFORE any
    rendering (no partial output), and never echoes the caller's text (DB-059 a)."""
    over_long = "A" * (writer._MAX_TEXT_CHARS + 1)
    result = render_site_plan_pdf(_spec(**{field: over_long}))
    assert isinstance(result, writer.SitePlanRefusal)
    assert result.reject_code == "text_too_long"
    assert field in result.detail
    assert over_long not in result.detail  # the caller's text is never echoed
    assert build_calls == []  # nothing drawn on the refusal


@pytest.mark.parametrize("field", _TEXT_FIELDS)
def test_exactly_at_cap_caller_text_still_renders(field):
    """The bound is inclusive: exactly _MAX_TEXT_CHARS characters renders bytes."""
    at_cap = "A" * writer._MAX_TEXT_CHARS
    assert len(at_cap) == writer._MAX_TEXT_CHARS
    assert isinstance(render_site_plan_pdf(_spec(**{field: at_cap})), bytes)


@pytest.mark.parametrize("field", _TEXT_FIELDS)
def test_length_cap_is_load_bearing_for_every_field(monkeypatch, field):
    """AS-1 mutation (in-process, consuming namespace): neuter the shared length cap
    and the over-long field slips through to a rendered sheet - so the one shared
    check genuinely bounds EVERY caller field."""
    over_long = "A" * (writer._MAX_TEXT_CHARS + 1)
    assert isinstance(
        render_site_plan_pdf(_spec(**{field: over_long})), writer.SitePlanRefusal
    )
    monkeypatch.setattr(writer, "_MAX_TEXT_CHARS", 10**9)
    assert isinstance(render_site_plan_pdf(_spec(**{field: over_long})), bytes)


def test_length_cap_precedes_the_claim_word_screen(build_calls):
    """Length is bounded before the separator-collapsing claim screen, so an over-cap
    value that also contains a claim word refuses as text_too_long (and the screen
    never runs on the huge string)."""
    over_and_claim = ("maximum allowed " * 20)[: writer._MAX_TEXT_CHARS + 5]
    assert len(over_and_claim) > writer._MAX_TEXT_CHARS
    result = render_site_plan_pdf(_spec(address=over_and_claim))
    assert isinstance(result, writer.SitePlanRefusal)
    assert result.reject_code == "text_too_long"  # length wins over the claim word
    assert build_calls == []


def test_length_cap_does_not_change_valid_output():
    """Adding the cap leaves valid, in-bounds output byte-identical (guards AS-4)."""
    assert hashlib.sha256(_rendered()).hexdigest() == _GOLDEN_SHA256


# -- M5-T105 AS-2 (DB-053 b): honest non-finite raise/return contract ---------------


def test_public_api_converts_internal_raise_to_a_returned_refusal(monkeypatch):
    """Forced past the ring checks, a non-finite drawing number makes _num RAISE the
    private carrier mid-render, and render_site_plan_pdf RETURNS a typed refusal - it
    never lets the exception escape (DB-053 b honest contract)."""
    monkeypatch.setattr(writer, "_TITLE_FONT_PT", float("nan"))
    result = render_site_plan_pdf(_spec())
    assert isinstance(result, writer.SitePlanRefusal)  # returned, not raised
    assert result.reject_code == "non_finite_value"


def test_boundary_conversion_is_load_bearing_raise_path_reddens(monkeypatch):
    """AS-2 mutation (in-process, consuming namespace): re-introduce the raise path
    by replacing the boundary _finish with one that does NOT catch _RenderRefused.
    The public API then RAISES instead of returning - proving the single boundary
    catch is what upholds the never-raise contract."""
    monkeypatch.setattr(writer, "_TITLE_FONT_PT", float("nan"))
    # real boundary: returns a refusal, no exception escapes
    assert isinstance(render_site_plan_pdf(_spec()), writer.SitePlanRefusal)

    def _finish_without_catch(spec, lot, building, feet_per_inch, to_device):
        content = writer._build_content(spec, lot, building, feet_per_inch, to_device)
        return writer._assemble_pdf(content)

    monkeypatch.setattr(writer, "_finish", _finish_without_catch)
    with pytest.raises(writer._RenderRefused):
        render_site_plan_pdf(_spec())


# -- M5-T105 AS-2 (DB-059 d): the vertex finiteness check covers Y, not only X -------


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
@pytest.mark.parametrize(
    "ring_field, ring", [("lot_ring", _LOT), ("building_ring", _BUILDING)]
)
def test_y_only_non_finite_vertex_is_non_finite_coordinate(ring_field, ring, bad):
    """DB-059 (d): a vertex whose Y (not X) is non-finite refuses with the SPECIFIC
    non_finite_coordinate code through the public API, never an exception."""
    bad_ring = ring[:1] + ((ring[1][0], bad),) + ring[2:]
    result = render_site_plan_pdf(_spec(**{ring_field: bad_ring}))
    assert isinstance(result, writer.SitePlanRefusal)
    assert result.reject_code == "non_finite_coordinate"


def _coerce_vertex_x_only_finite(vertex, label):
    """EX2 weakening (the M5-T091 G4 survivor): check finiteness of X but NOT Y."""
    if not writer._is_sequence(vertex) or len(vertex) != 2:
        return writer.SitePlanRefusal("invalid_ring", f"{label} ring vertex is not a pair")
    for value in vertex:
        if isinstance(value, bool) or not isinstance(value, numbers.Real):
            return writer.SitePlanRefusal(
                "non_numeric_coordinate", f"{label} ring has a non-numeric coordinate"
            )
    try:
        x, y = float(vertex[0]), float(vertex[1])
    except OverflowError:
        return writer.SitePlanRefusal("oversize_input", f"{label} ring coordinate too big")
    if not math.isfinite(x):  # the Y finiteness check is DROPPED - the EX2 mutant
        return writer.SitePlanRefusal(
            "non_finite_coordinate", f"{label} ring has a non-finite coordinate"
        )
    if abs(x) > writer._MAX_COORD_ABS or abs(y) > writer._MAX_COORD_ABS:
        return writer.SitePlanRefusal("oversize_input", f"{label} ring coordinate too big")
    return (x, y)


@pytest.mark.parametrize("bad", [float("nan"), float("inf")])
def test_y_only_finiteness_check_is_load_bearing(monkeypatch, bad):
    """AS-2 mutation (in-process, consuming namespace): with the Y half of the
    finiteness check dropped, a Y-only non-finite vertex is no longer caught as
    non_finite_coordinate - it slips past _coerce_vertex and is caught downstream
    under a DIFFERENT code, so the y-only probe reddens. Still a typed refusal (never
    raises), which is why the code assertion - not just isinstance - has teeth."""
    y_bad = _LOT[:1] + ((_LOT[1][0], bad),) + _LOT[2:]
    real = render_site_plan_pdf(_spec(lot_ring=y_bad, building_ring=None))
    assert isinstance(real, writer.SitePlanRefusal)
    assert real.reject_code == "non_finite_coordinate"

    monkeypatch.setattr(writer, "_coerce_vertex", _coerce_vertex_x_only_finite)
    mutant = render_site_plan_pdf(_spec(lot_ring=y_bad, building_ring=None))
    assert isinstance(mutant, writer.SitePlanRefusal)  # still typed, never raises
    assert mutant.reject_code != "non_finite_coordinate"  # but not the Y-specific code
