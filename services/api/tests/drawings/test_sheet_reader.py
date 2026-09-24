"""Acceptance + mutation tests for the architect drawing-sheet reader profile (M5-T083).

Synthetic PDFs are assembled byte-by-byte with real classic-xref offsets (mirroring
tests/documents/test_pdf_container's approach, re-expressed here so nothing under
tests/documents is imported or edited). Coverage maps to the packet's acceptance scenarios:

* AS-1 curves       -> quarter-circle Beziers flattened within a DECLARED tolerance,
                       recorded in the output; mutation: no subdivision reddens.
* AS-2 transforms   -> a 30-degree rotation + a shear map points exactly (1e-9); nested
                       q/Q restores the CTM; mutation: dropping the CTM multiply reddens.
* AS-3 XObjects     -> a Form XObject used twice yields its primitives twice; recursion
                       cycle / over-depth refused; an image is counted, never decoded.
* AS-4 fail-closed  -> encryption, unsupported filters, and every bound return a typed
                       refusal VALUE (no exception); all-or-nothing per document.
* AS-5 isolation    -> covered by the producer report (blob-untouched proof, no consumer,
                       ruff + modularity); a couple of composition smoke checks live here.
"""

from __future__ import annotations

import math
import tracemalloc
import zlib

import pytest

from app.drawings import sheet_reader
from app.drawings.sheet_primitives import (
    SheetDocument,
    SheetImage,
    SheetRefusal,
    flatten_cubic,
)
from app.drawings.sheet_reader import read_sheet, sheet_refusal


# --------------------------------------------------------------------------- PDF builders
def _num(value: float) -> bytes:
    return f"{value:.10f}".encode("ascii")


def _flat(points: tuple[tuple[float, float], ...]) -> list[float]:
    return [coord for point in points for coord in point]


def _pdf(objects: list[bytes], root: bytes = b"1 0 R") -> bytes:
    out = bytearray(b"%PDF-1.7\n")
    offsets: list[int] = []
    for index, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % index + body + b"\nendobj\n"
    xref_offset = len(out)
    size = len(objects) + 1
    out += b"xref\n0 %d\n" % size + b"0000000000 65535 f \n"
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root %s >>\n" % (size, root)
    out += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(out)


def _stream(data: bytes, extra: bytes = b"") -> bytes:
    return b"<< /Length %d%s >>\nstream\n%s\nendstream" % (len(data), extra, data)


def _flate(plain: bytes, extra: bytes = b"") -> bytes:
    return _stream(zlib.compress(plain), b" /Filter /FlateDecode" + extra)


def _one_page(
    content: bytes,
    *,
    resources: bytes = b"",
    media: bytes = b"[0 0 800 600]",
    page_extra: bytes = b"",
    extra_objects: tuple[bytes, ...] = (),
) -> bytes:
    res = b" /Resources %s" % resources if resources else b""
    page = (
        b"<< /Type /Page /Parent 2 0 R /MediaBox %s%s%s /Contents 4 0 R >>"
        % (media, res, page_extra)
    )
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        page,
        _stream(content),
        *extra_objects,
    ]
    return _pdf(objects)


# --------------------------------------------------------------------------------- AS-1
def _quarter_circle_content(radius: float) -> bytes:
    """Four cubic Beziers approximating a quarter circle (0..90 deg) centred at origin."""
    ops = bytearray()
    for step in range(4):
        a0 = math.radians(22.5 * step)
        a1 = math.radians(22.5 * (step + 1))
        p0 = (radius * math.cos(a0), radius * math.sin(a0))
        p3 = (radius * math.cos(a1), radius * math.sin(a1))
        k = (4.0 / 3.0) * math.tan((a1 - a0) / 4.0)
        p1 = (p0[0] - k * radius * math.sin(a0), p0[1] + k * radius * math.cos(a0))
        p2 = (p3[0] + k * radius * math.sin(a1), p3[1] - k * radius * math.cos(a1))
        if step == 0:
            ops += _num(p0[0]) + b" " + _num(p0[1]) + b" m\n"
        for point in (p1, p2, p3):
            ops += _num(point[0]) + b" " + _num(point[1]) + b" "
        ops += b"c\n"
    ops += b"S"
    return bytes(ops)


def _max_circle_deviation(points: tuple[tuple[float, float], ...], radius: float) -> float:
    worst = 0.0
    for point in points:
        worst = max(worst, abs(math.hypot(point[0], point[1]) - radius))
    for a, b in zip(points, points[1:], strict=False):
        mid = ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5)
        worst = max(worst, abs(math.hypot(mid[0], mid[1]) - radius))
    return worst


def test_as1_quarter_circle_flattened_within_declared_tolerance():
    radius, tolerance = 200.0, 0.5
    doc = read_sheet(_one_page(_quarter_circle_content(radius)), flatten_tolerance=tolerance)
    assert isinstance(doc, SheetDocument)
    page = doc.pages[0]
    # the declared tolerance is recorded in the output (page and document)
    assert page.flatten_tolerance == tolerance
    assert doc.flatten_tolerance == tolerance
    points = page.polylines[0].points
    assert len(points) > 5  # subdivided beyond the 4 raw Bezier endpoints
    assert _max_circle_deviation(points, radius) <= tolerance


def test_as1_mutation_skipping_subdivision_reddens(monkeypatch):
    """MUTATION (AS-1): a flattener that never subdivides pushes the measured deviation
    above the declared tolerance, so the AS-1 assertion would fail."""
    radius, tolerance = 200.0, 0.5

    def _no_subdivision(p0, p1, p2, p3, tol, out, depth, budget):
        out.append(p3)
        return True

    monkeypatch.setattr(sheet_reader, "_flatten_cubic", _no_subdivision)
    doc = read_sheet(_one_page(_quarter_circle_content(radius)), flatten_tolerance=tolerance)
    assert isinstance(doc, SheetDocument)
    deviation = _max_circle_deviation(doc.pages[0].polylines[0].points, radius)
    assert deviation > tolerance  # mutant detected: the tolerance guard has teeth


# --------------------------------------------------------------------------------- AS-2
_ROT = math.radians(30.0)
_COS, _SIN = math.cos(_ROT), math.sin(_ROT)


def _rotate_then_translate(x: float, y: float, tx: float, ty: float) -> tuple[float, float]:
    return (x * _COS - y * _SIN + tx, x * _SIN + y * _COS + ty)


def _as2_content() -> bytes:
    rot = b"%s %s %s %s 0 0 cm" % (_num(_COS), _num(_SIN), _num(-_SIN), _num(_COS))
    return b"q 1 0 0 1 10 20 cm %s 5 7 m 9 3 l S Q" % rot


def test_as2_rotation_and_translation_compose_exactly():
    doc = read_sheet(_one_page(_as2_content()))
    assert isinstance(doc, SheetDocument)
    points = doc.pages[0].polylines[0].points
    assert points[0] == pytest.approx(_rotate_then_translate(5.0, 7.0, 10.0, 20.0), abs=1e-9)
    assert points[1] == pytest.approx(_rotate_then_translate(9.0, 3.0, 10.0, 20.0), abs=1e-9)


def test_as2_shear_is_supported_and_maps_exactly():
    """The survey profile refuses c!=0 (shear); this profile maps it exactly."""
    shear = 0.4
    content = b"q 1 0 %s 1 0 0 cm 5 7 m 9 3 l S Q" % _num(shear)
    doc = read_sheet(_one_page(content))
    assert isinstance(doc, SheetDocument)  # NOT refused
    points = doc.pages[0].polylines[0].points
    assert points[0] == pytest.approx((5.0 + shear * 7.0, 7.0), abs=1e-9)
    assert points[1] == pytest.approx((9.0 + shear * 3.0, 3.0), abs=1e-9)


def test_as2_nested_q_q_restores_the_ctm():
    content = b"q 1 0 0 1 100 100 cm Q 5 7 m 9 3 l S"
    doc = read_sheet(_one_page(content))
    assert isinstance(doc, SheetDocument)
    points = doc.pages[0].polylines[0].points
    assert points[0] == pytest.approx((5.0, 7.0), abs=1e-9)  # translate popped away
    assert points[1] == pytest.approx((9.0, 3.0), abs=1e-9)


def test_as2_mutation_dropping_ctm_multiply_reddens(monkeypatch):
    """MUTATION (AS-2): a concat that ignores the prior CTM loses the earlier translate,
    so the composed point diverges from the exact rotation+translation."""
    monkeypatch.setattr(sheet_reader, "_concat_matrix", lambda m, ctm: m)
    doc = read_sheet(_one_page(_as2_content()))
    assert isinstance(doc, SheetDocument)
    got = doc.pages[0].polylines[0].points[0]
    expected = _rotate_then_translate(5.0, 7.0, 10.0, 20.0)
    assert got != pytest.approx(expected, abs=1e-6)  # mutant detected


# --------------------------------------------------------------------------------- AS-3
_FORM_LINE = b"0 0 m 1 0 l S"


def _form_obj(content: bytes, extra: bytes = b"") -> bytes:
    return _stream(content, b" /Type /XObject /Subtype /Form /BBox [0 0 1 1]%s" % extra)


def test_as3_form_xobject_used_twice_yields_primitives_twice():
    content = b"q 100 0 0 100 0 0 cm /Fm0 Do Q q 1 0 0 1 200 50 cm /Fm0 Do Q"
    pdf = _one_page(
        content,
        resources=b"<< /XObject << /Fm0 5 0 R >> >>",
        extra_objects=(_form_obj(_FORM_LINE),),
    )
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)
    polylines = doc.pages[0].polylines
    assert len(polylines) == 2  # one per placement
    assert _flat(polylines[0].points) == pytest.approx([0.0, 0.0, 100.0, 0.0])
    assert _flat(polylines[1].points) == pytest.approx([200.0, 50.0, 201.0, 50.0])


def test_as3_form_self_reference_cycle_is_refused():
    pdf = _one_page(
        b"/Fm0 Do",
        resources=b"<< /XObject << /Fm0 5 0 R >> >>",
        extra_objects=(_form_obj(b"/Fm0 Do"),),
    )
    refusal = sheet_refusal(read_sheet(pdf))
    assert refusal is not None
    assert refusal.feature == "xobject cycle"


def test_as3_form_recursion_depth_bound_is_refused(monkeypatch):
    monkeypatch.setattr(sheet_reader, "MAX_XOBJECT_DEPTH", 1)
    pdf = _one_page(
        b"/FmA Do",
        resources=b"<< /XObject << /FmA 5 0 R /FmB 6 0 R >> >>",
        extra_objects=(_form_obj(b"/FmB Do"), _form_obj(_FORM_LINE)),
    )
    refusal = sheet_refusal(read_sheet(pdf))
    assert refusal is not None
    assert refusal.feature == "xobject recursion"


def test_as3_image_xobject_counted_and_never_decoded():
    # /DCTDecode + non-flate garbage: a decode attempt would fail, proving it is never made.
    image = _stream(
        b"\xff\xd8\xff\xe0not-a-real-jpeg",
        b" /Type /XObject /Subtype /Image /Width 8 /Height 6"
        b" /BitsPerComponent 8 /ColorSpace /DeviceRGB /Filter /DCTDecode",
    )
    pdf = _one_page(
        b"q 50 0 0 40 10 20 cm /Im0 Do Q",
        resources=b"<< /XObject << /Im0 5 0 R >> >>",
        extra_objects=(image,),
    )
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)
    page = doc.pages[0]
    assert page.image_count == 1
    only = page.images[0]
    assert isinstance(only, SheetImage)
    assert (only.name, only.width, only.height, only.bits_per_component) == ("Im0", 8, 6, 8)
    assert only.color_space == "DeviceRGB"
    assert only.matrix == pytest.approx((50.0, 0.0, 0.0, 40.0, 10.0, 20.0))
    assert page.polylines == ()  # an image places no vector geometry


# --------------------------------------------------------------------------------- AS-4
def test_as4_encrypted_document_is_refused_as_value():
    pdf = _one_page(b"5 7 m 9 3 l S")
    pdf = pdf.replace(b"/Root 1 0 R", b"/Root 1 0 R /Encrypt 1 0 R")
    refusal = sheet_refusal(read_sheet(pdf))
    assert refusal is not None
    assert refusal.origin == SheetRefusal.STRICT_READER
    assert refusal.feature == "encryption"


def test_as4_unsupported_content_filter_is_refused():
    body = _stream(b"garbage", b" /Filter /LZWDecode")
    pdf = _pdf(
        [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
            body,
        ]
    )
    refusal = sheet_refusal(read_sheet(pdf))
    assert refusal is not None
    assert refusal.feature == "stream filter"


def test_as4_operator_count_bound_is_refused(monkeypatch):
    monkeypatch.setattr(sheet_reader, "MAX_CONTENT_OPERATORS", 3)
    refusal = sheet_refusal(read_sheet(_one_page(b"q q q q q q Q Q Q Q Q Q")))
    assert refusal is not None
    assert refusal.feature == "operator count"


def test_as4_path_points_bound_is_refused(monkeypatch):
    monkeypatch.setattr(sheet_reader, "MAX_PATH_POINTS", 2)
    refusal = sheet_refusal(read_sheet(_one_page(b"0 0 m 1 1 l 2 2 l 3 3 l 4 4 l S")))
    assert refusal is not None
    assert refusal.feature == "path points"


def test_as4_q_depth_bound_is_refused(monkeypatch):
    monkeypatch.setattr(sheet_reader, "MAX_Q_DEPTH", 2)
    refusal = sheet_refusal(read_sheet(_one_page(b"q q q Q Q Q")))
    assert refusal is not None
    assert refusal.feature == "q depth"


def test_as4_unsupported_operator_is_refused():
    refusal = sheet_refusal(read_sheet(_one_page(b"0 0 1 sc 5 5 sh")))
    assert refusal is not None
    assert refusal.feature == "unsupported operator"


def test_as4_all_or_nothing_second_page_refusal_fails_whole_document():
    good = _stream(b"5 7 m 9 3 l S")
    bad = _stream(b"5 5 sh")  # unsupported operator on page 2
    pdf = _pdf(
        [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R 5 0 R] /Count 2 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
            good,
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 6 0 R >>",
            bad,
        ]
    )
    result = read_sheet(pdf)
    assert isinstance(result, SheetRefusal)  # no partial 1-page document survives
    assert result.feature == "unsupported operator"


def test_as4_non_bytes_input_is_refused():
    refusal = sheet_refusal(read_sheet("not bytes"))  # type: ignore[arg-type]
    assert refusal is not None
    assert refusal.feature == "input"


def test_as4_invalid_flatten_tolerance_is_refused():
    for bad in (0.0, -1.0, math.inf, math.nan):
        refusal = sheet_refusal(read_sheet(_one_page(b"5 7 m 9 3 l S"), flatten_tolerance=bad))
        assert refusal is not None
        assert refusal.feature == "flatten tolerance"


def test_as4_malformed_header_refused_via_reused_strict_reader():
    refusal = sheet_refusal(read_sheet(b"not a pdf at all"))
    assert refusal is not None
    assert refusal.origin == SheetRefusal.STRICT_READER


# ----------------------------------------------------------------------- composition/units
def test_user_unit_and_media_box_are_disclosed():
    doc = read_sheet(_one_page(b"5 7 m 9 3 l S", page_extra=b" /UserUnit 2.5"))
    assert isinstance(doc, SheetDocument)
    page = doc.pages[0]
    assert page.user_unit == 2.5
    assert page.media_box == (0.0, 0.0, 800.0, 600.0)


def test_fill_and_stroke_painting_is_distinguished():
    doc = read_sheet(_one_page(b"0 0 m 10 0 l 10 10 l h B"))
    assert isinstance(doc, SheetDocument)
    poly = doc.pages[0].polylines[0]
    assert poly.stroked and poly.filled and poly.closed


def test_rotated_text_run_is_placed_and_not_refused():
    """The survey profile refuses a rotated Tm; this profile keeps the run and records its
    origin (Tm x CTM) and matrix so the angle is recoverable."""
    tm = b"%s %s %s %s 100 200 Tm" % (_num(_COS), _num(_SIN), _num(-_SIN), _num(_COS))
    content = b"BT /F1 12 Tf %s (Hi) Tj ET" % tm
    doc = read_sheet(_one_page(content, resources=b"<< /Font << /F1 << >> >> >>"))
    assert isinstance(doc, SheetDocument)  # NOT refused despite rotation
    runs = doc.pages[0].text_runs
    assert len(runs) == 1
    assert runs[0].text == "Hi"
    assert (runs[0].x, runs[0].y) == pytest.approx((100.0, 200.0), abs=1e-9)
    assert runs[0].font_size == 12.0
    assert runs[0].matrix[1] == pytest.approx(_SIN)  # rotation preserved in the matrix


# =============================================================== rework: G5 F1 cluster (D-087)
# Item 1 (G5 F1, BLOCKING): the per-page point budget bounds Bezier flattening WHILE it
# subdivides, so a single degenerate curve can never materialize 2**MAX_FLATTEN_DEPTH points.
def test_flatten_cubic_stops_at_the_point_budget():
    """Direct: a curve whose huge control coords never satisfy cubic_flat fills ONLY up to
    the remaining budget and reports incompletion (never 2**MAX_FLATTEN_DEPTH points)."""
    p0, p1, p2, p3 = (0.0, 0.0), (1e18, 1e18), (2e18, -1e18), (3e18, 0.0)
    out: list[tuple[float, float]] = []
    completed = flatten_cubic(p0, p1, p2, p3, 0.25, out, 0, 1000)
    assert completed is False        # hit the budget before flattening finished
    assert len(out) <= 1000          # bounded to the remaining budget, not 2**24 (~16.8M)


def _big_curve_pdf() -> bytes:
    # huge control coords as plain-decimal tokens (<= 64 bytes, no exponent) that never
    # satisfy the flatness test; a naive flattener would emit 2**MAX_FLATTEN_DEPTH points.
    content = (
        b"0 0 m "
        b"1000000000000000000 1000000000000000000 "
        b"2000000000000000000 -1000000000000000000 "
        b"3000000000000000000 0 c S"
    )
    return _one_page(content)


def test_single_curve_refuses_within_bounded_memory(monkeypatch):
    """Integration: one `c` op with 1e18 control coords refuses with the path-points refusal
    and bounded transient memory (the fix caps it at the remaining budget, not ~1.9 GB)."""
    monkeypatch.setattr(sheet_reader, "MAX_PATH_POINTS", 5000)
    tracemalloc.start()
    try:
        refusal = sheet_refusal(read_sheet(_big_curve_pdf()))
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert refusal is not None
    assert refusal.feature == "path points"
    assert peak < 16 * 1024 * 1024   # bounded; G5 measured ~120 MiB / ~1.9 GB without the fix


# Item 2 (G5 F3): each page's primitives are only that page's (fresh per-page output lists).
def test_each_page_has_only_its_own_primitives():
    page0 = _stream(b"0 0 m 10 10 l S")
    page1 = _stream(b"20 20 m 30 30 l S")
    pdf = _pdf(
        [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R 5 0 R] /Count 2 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
            page0,
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 6 0 R >>",
            page1,
        ]
    )
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)
    assert len(doc.pages) == 2
    assert len(doc.pages[0].polylines) == 1
    assert len(doc.pages[1].polylines) == 1          # NOT 2 (page 0's line must not leak in)
    p0_pts = _flat(doc.pages[0].polylines[0].points)
    p1_pts = _flat(doc.pages[1].polylines[0].points)
    assert p0_pts == pytest.approx([0.0, 0.0, 10.0, 10.0])
    assert p1_pts == pytest.approx([20.0, 20.0, 30.0, 30.0])


# Item 3 (G5 F2): Form content is decoded once per (number, generation) and the document-wide
# decoded-bytes budget is charged by every decode.
def _flate_form(content: bytes, extra: bytes = b"") -> bytes:
    return _flate(content, b" /Type /XObject /Subtype /Form /BBox [0 0 1 1]%s" % extra)


def test_form_flate_content_decoded_once_when_placed_many_times(monkeypatch):
    calls = {"n": 0}
    real_decode = sheet_reader._decode_stream

    def counting(table, stream, interp):
        calls["n"] += 1
        return real_decode(table, stream, interp)

    monkeypatch.setattr(sheet_reader, "_decode_stream", counting)
    pdf = _one_page(
        b" ".join([b"/Fm0 Do"] * 10),
        resources=b"<< /XObject << /Fm0 5 0 R >> >>",
        extra_objects=(_flate_form(_FORM_LINE),),
    )
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)
    assert len(doc.pages[0].polylines) == 10    # each of the 10 placements is interpreted
    assert calls["n"] == 2                       # page content once + form ONCE (not 11)


def test_document_decoded_bytes_budget_is_refused(monkeypatch):
    monkeypatch.setattr(sheet_reader, "MAX_TOTAL_DECODED_BYTES", 4)
    refusal = sheet_refusal(read_sheet(_one_page(b"5 7 m 9 3 l S")))
    assert refusal is not None
    assert refusal.feature == "decoded bytes budget"


# Item 4 (G5 F4): a top-level backstop turns any unexpected exception into a typed refusal.
def test_top_level_backstop_converts_unexpected_exception_to_refusal(monkeypatch):
    def _boom(_table):
        raise RuntimeError("internal boom with attacker detail")

    monkeypatch.setattr(sheet_reader, "_catalog_pages_root", _boom)
    refusal = sheet_refusal(read_sheet(_one_page(b"5 7 m 9 3 l S")))
    assert refusal is not None
    assert refusal.feature == "unexpected error"
    assert "RuntimeError" in refusal.detail                 # only the exception TYPE
    assert "attacker detail" not in refusal.detail          # no content/message leak


# Item 5 (G5 F5): attacker-derived tokens are truncated in the refusal detail.
def test_unsupported_operator_detail_is_truncated():
    refusal = sheet_refusal(read_sheet(_one_page(b"Z" * 100_000)))
    assert refusal is not None
    assert refusal.feature == "unsupported operator"
    assert len(refusal.detail) < 200                        # bounded, not ~100k
    assert "...(truncated)" in refusal.detail


# Item 6 (G5 F6): a non-finite coordinate after CTM math is refused (typed).
def test_non_finite_coordinate_after_ctm_is_refused():
    huge = b"1" + b"0" * 39                                  # 1e39, plain decimal (<64 bytes)
    scale = b"%s 0 0 %s 0 0 cm" % (huge, huge)
    content = b" ".join([scale] * 10) + b" 1 1 m 2 2 l S"    # CTM overflows to inf
    refusal = sheet_refusal(read_sheet(_one_page(content)))
    assert refusal is not None
    assert refusal.feature == "non-finite coordinate"


# Item 7 (G1 F3 / G3 F2): q/Q save+restore text state; a Form inherits the caller's text state.
def test_q_q_saves_and_restores_font_size():
    content = b"/F1 10 Tf q /F1 30 Tf BT (A) Tj ET Q BT (B) Tj ET"
    doc = read_sheet(_one_page(content, resources=b"<< /Font << /F1 << >> >> >>"))
    assert isinstance(doc, SheetDocument)
    runs = doc.pages[0].text_runs
    assert [r.font_size for r in runs] == [30.0, 10.0]      # A at 30 (in q), B at 10 (restored)


def test_form_inherits_caller_text_state():
    form = _form_obj(b"BT (X) Tj ET")                        # form has NO Tf of its own
    pdf = _one_page(
        b"/F1 14 Tf /Fm0 Do",
        resources=b"<< /Font << /F1 << >> >> /XObject << /Fm0 5 0 R >> >>",
        extra_objects=(form,),
    )
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)                    # not refused as "text before Tf"
    runs = doc.pages[0].text_runs
    assert len(runs) == 1
    assert runs[0].text == "X"
    assert runs[0].font_size == 14.0                         # inherited from the caller


# Item 8 (G1 F5): after h/close, a segment op with no intervening m begins a new subpath.
def test_segment_after_close_begins_new_subpath():
    content = b"0 0 m 10 0 l 10 10 l h 20 20 l S"
    doc = read_sheet(_one_page(content))
    assert isinstance(doc, SheetDocument)                    # not refused
    polylines = doc.pages[0].polylines
    assert len(polylines) == 2                               # closed triangle + reopened line
    closed = [p for p in polylines if p.closed]
    reopened = [p for p in polylines if not p.closed]
    assert len(closed) == 1 and len(reopened) == 1
    assert reopened[0].points[0] == pytest.approx((0.0, 0.0))   # begins at the subpath start
    assert reopened[0].points[1] == pytest.approx((20.0, 20.0))


# Item 9 (G1 F6 / G3 F3; DB-055 a): the current point is device space, so a mid-path cm cannot
# re-derive a wrong curve start. The regression guard MUST pin the value the bug displaces: the
# curve's FIRST INTERIOR flattened point (points[1]). points[0] (the separately-stored moveto
# point) and points[-1] (= map(*end)) are INVARIANT under the pre-fix revert, so asserting only
# those is vacuous (G4-rework F6 / DCV F3). Under the literal pre-fix revert
# `p0 = _apply_matrix(self._ctm, *self._current)` the curve start jumps and points[1] moves from
# (14.160156, 13.339844) to (23.125, 20.3125) — a real discontinuity that this assertion reddens
# (mutant recorded in the M5-T104 producer report; the production code below is correct).
def test_mid_path_cm_does_not_corrupt_curve_start():
    content = b"10 10 m 2 0 0 2 0 0 cm 10 10 20 10 20 20 c S"
    doc = read_sheet(_one_page(content))
    assert isinstance(doc, SheetDocument)
    points = doc.pages[0].polylines[0].points
    assert points[0] == pytest.approx((10.0, 10.0))         # true previous point, not (20,20)
    # the reopened curve's first INTERIOR point is continuous with the moveto point (device
    # space); the pre-fix revert displaces it to ~(23.12, 20.31) (the value the bug moves).
    assert points[1] == pytest.approx((14.160156, 13.339844), abs=1e-4)
    assert points[-1] == pytest.approx((40.0, 40.0))        # end = apply(scale2, (20,20))


# Item 11 (QA F4): an asymmetric Bezier probe that reddens cubic_flat's `and`->`or` weakening.
def _bezier_point(p0, p1, p2, p3, t):
    mt = 1.0 - t
    return (
        mt * mt * mt * p0[0] + 3 * mt * mt * t * p1[0]
        + 3 * mt * t * t * p2[0] + t * t * t * p3[0],
        mt * mt * mt * p0[1] + 3 * mt * mt * t * p1[1]
        + 3 * mt * t * t * p2[1] + t * t * t * p3[1],
    )


def _dist_point_to_segment(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    seg2 = dx * dx + dy * dy
    if seg2 == 0.0:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / seg2))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def _max_curve_deviation_from_polyline(p0, p1, p2, p3, points, samples=400):
    worst = 0.0
    for i in range(samples + 1):
        cp = _bezier_point(p0, p1, p2, p3, i / samples)
        best = min(
            _dist_point_to_segment(cp, points[j], points[j + 1])
            for j in range(len(points) - 1)
        )
        worst = max(worst, best)
    return worst


def test_asymmetric_bezier_respects_declared_tolerance():
    p0, p1, p2, p3 = (0.0, 0.0), (1.0, 0.0), (50.0, 40.0), (100.0, 0.0)
    tol = 0.5
    doc = read_sheet(_one_page(b"0 0 m 1 0 50 40 100 0 c S"), flatten_tolerance=tol)
    assert isinstance(doc, SheetDocument)
    points = doc.pages[0].polylines[0].points
    dev = _max_curve_deviation_from_polyline(p0, p1, p2, p3, points)
    # real `and` subdivides and hugs the curve; a weakened `or` would emit the straight chord
    # whose deviation from the true curve is ~17.8 (36x the tolerance).
    assert dev <= tol * 1.5


# Item 11 (QA F5): a multi-hop A->B->A Form cycle is refused as an xobject cycle.
def test_multi_hop_form_cycle_is_refused():
    pdf = _one_page(
        b"/FmA Do",
        resources=b"<< /XObject << /FmA 5 0 R /FmB 6 0 R >> >>",
        extra_objects=(_form_obj(b"/FmB Do"), _form_obj(b"/FmA Do")),
    )
    refusal = sheet_refusal(read_sheet(pdf))
    assert refusal is not None
    assert refusal.feature == "xobject cycle"                # not merely the depth bound


# ========================================================= M5-T104: operator coverage (DB-055 i)
# Every operator DB-055 (i) lists (re, v, y, s, f, F, f*, B*, b, b*, n, W, W*, TL, Td, TD, T*, TJ,
# ' and ") is now executed by a test with an asserted outcome, and the packet's original "rotated
# rectangle" (which was really a rotated LINE) is replaced by a TRUE four-edge rectangle under a
# rotated CTM, asserted vertex by vertex. Each test pins a field that a targeted consuming-namespace
# mutant displaces; the mutants and their verbatim red runs are recorded in the M5-T104 producer
# report (project-control/reports/M5-T104-producer-report.md). The committed assertions are the
# durable regression guards; production behaviour is unchanged by this packet.


def test_rotated_rectangle_via_re_maps_each_vertex():
    """A GENUINE rectangle (`re` -> 4 corners + close) under a 30-degree rotation CTM, asserted
    vertex by vertex. Mutant (report): `sheet_interpreter._apply_matrix` = identity drops the
    rotation and every vertex reddens."""
    rot = b"%s %s %s %s 0 0 cm" % (_num(_COS), _num(_SIN), _num(-_SIN), _num(_COS))
    doc = read_sheet(_one_page(b"q %s 10 20 30 15 re S Q" % rot))
    assert isinstance(doc, SheetDocument)
    poly = doc.pages[0].polylines[0]
    assert poly.closed and poly.stroked and not poly.filled
    assert len(poly.points) == 4                              # four corners (NOT a 2-point line)
    corners = ((10.0, 20.0), (40.0, 20.0), (40.0, 35.0), (10.0, 35.0))  # (x,y),(x+w,y),(+h),(...)
    for got, (cx, cy) in zip(poly.points, corners, strict=True):
        assert got == pytest.approx(_rotate_then_translate(cx, cy, 0.0, 0.0), abs=1e-9)


def test_v_curve_first_control_is_the_current_point():
    """`x2 y2 x3 y3 v`: the FIRST Bezier control point coincides with the current point. Mutant
    (report): dispatching `v` with ctrl1_is_current=False moves the first interior point from
    (21.718750, 19.257812) to ~(17.15, 16.49)."""
    doc = read_sheet(_one_page(b"20 20 m 60 0 60 60 v S"))
    assert isinstance(doc, SheetDocument)
    points = doc.pages[0].polylines[0].points
    assert points[0] == pytest.approx((20.0, 20.0))          # starts at the current point
    assert points[1] == pytest.approx((21.718750, 19.257812), abs=1e-4)  # bows from the current pt
    assert points[-1] == pytest.approx((60.0, 60.0))         # ends at (x3, y3)


def test_y_curve_last_control_is_the_endpoint():
    """`x1 y1 x3 y3 y`: the LAST Bezier control point coincides with the endpoint. Mutant (report):
    dispatching `y` with the second control != endpoint moves the first interior point from
    (4.194336, 7.041016) to ~(6.72, 13.20)."""
    doc = read_sheet(_one_page(b"0 0 m 20 40 80 40 y S"))
    assert isinstance(doc, SheetDocument)
    points = doc.pages[0].polylines[0].points
    assert points[0] == pytest.approx((0.0, 0.0))
    assert points[1] == pytest.approx((4.194336, 7.041016), abs=1e-4)
    assert points[-1] == pytest.approx((80.0, 40.0))         # ends at (x3, y3)


# (stroked, filled, closed) expected for path `0 0 m 10 0 l 10 10 l <word>` (no explicit h).
_PAINT_FLAGS = {
    "S": (True, False, False),
    "s": (True, False, True),       # s = close + stroke
    "f": (False, True, False),
    "F": (False, True, False),      # F is a deprecated alias of f
    "f*": (False, True, False),     # even-odd fill
    "B*": (True, True, False),      # fill + stroke (even-odd)
    "b": (True, True, True),        # close + fill + stroke
    "b*": (True, True, True),       # close + fill + stroke (even-odd)
    "n": (False, False, False),     # no paint (clip/no-op) but geometry is still surfaced
}


def test_all_paint_operators_set_expected_flags():
    """Each accepted painting operator is executed and its (stroked, filled, closed) outcome is
    asserted. Mutants (report): emptying `_PAINT_STROKE` / `_PAINT_FILL` / `_PAINT_CLOSE_FIRST`
    each reddens the stroked / filled / closed facet respectively."""
    for word, (stroked, filled, closed) in _PAINT_FLAGS.items():
        doc = read_sheet(_one_page(b"0 0 m 10 0 l 10 10 l " + word.encode("ascii")))
        assert isinstance(doc, SheetDocument), word
        poly = doc.pages[0].polylines[0]
        assert (poly.stroked, poly.filled, poly.closed) == (stroked, filled, closed), word
        assert _flat(poly.points) == pytest.approx([0.0, 0.0, 10.0, 0.0, 10.0, 10.0]), word


def test_clip_operators_are_ignored_and_keep_the_path():
    """`W` / `W*` are consumed (clipping is not modelled) and DO NOT clear or refuse the path; the
    following paint op still surfaces the geometry. Mutant (report): removing W/W* from `_IGNORED`
    turns each into an 'unsupported operator' refusal."""
    for clip in (b"W", b"W*"):
        doc = read_sheet(_one_page(b"0 0 m 10 0 l 10 10 l " + clip + b" n"))
        assert isinstance(doc, SheetDocument), clip
        polylines = doc.pages[0].polylines
        assert len(polylines) == 1, clip
        assert _flat(polylines[0].points) == pytest.approx([0.0, 0.0, 10.0, 0.0, 10.0, 10.0]), clip


def test_text_line_moves_place_runs_with_leading():
    """Td / TD / T* / TL are executed and each run's origin is asserted (CTM identity). TD sets the
    leading from -ty; TL sets it explicitly; T* moves down by the current leading. Mutant (report):
    `sheet_reader._concat_matrix` = (lambda m, ctm: m) drops the accumulated text line matrix, so
    every run after the first reddens."""
    content = b"BT /F1 12 Tf 100 700 Td (A) Tj 0 -20 TD (B) Tj T* (C) Tj 14 TL T* (D) Tj ET"
    doc = read_sheet(_one_page(content, resources=b"<< /Font << /F1 << >> >> >>"))
    assert isinstance(doc, SheetDocument)
    runs = doc.pages[0].text_runs
    assert [(r.text, r.x, r.y) for r in runs] == [
        ("A", pytest.approx(100.0), pytest.approx(700.0)),   # Td 100 700
        ("B", pytest.approx(100.0), pytest.approx(680.0)),   # TD 0 -20 (leading := 20)
        ("C", pytest.approx(100.0), pytest.approx(660.0)),   # T* down by leading 20
        ("D", pytest.approx(100.0), pytest.approx(646.0)),   # TL 14 then T* down by 14
    ]


def test_text_show_TJ_quote_and_dquote_operators():
    """TJ (array show, numeric kerning ignored for the modelled origin), ' (next line + show) and
    " (aw ac string, next line + show) are executed with asserted text and origins. Mutant (report):
    `sheet_reader._concat_matrix` = (lambda m, ctm: m) reddens the moved origins."""
    content = b"BT /F1 10 Tf 10 TL 50 500 Td 0 -30 Td [(X) -250 (Y)] TJ (P) ' 1 2 (Q) \" ET"
    doc = read_sheet(_one_page(content, resources=b"<< /Font << /F1 << >> >> >>"))
    assert isinstance(doc, SheetDocument)
    runs = doc.pages[0].text_runs
    assert [(r.text, r.x, r.y) for r in runs] == [
        ("XY", pytest.approx(50.0), pytest.approx(470.0)),   # TJ joins pieces, skips the -250
        ("P", pytest.approx(50.0), pytest.approx(460.0)),    # ' = T* (down 10) + show
        ("Q", pytest.approx(50.0), pytest.approx(450.0)),    # " = T* (down 10) + show (aw/ac skip)
    ]


# ============================================================= M5-T104: budget semantics (DB-064)
def test_two_distinct_form_xobjects_decode_and_place():
    """DB-064 (a): two DISTINCT Form XObjects both decode and place correctly, so a wrong-key form
    memo (two forms sharing one decoded body) is detectable. Mutant (report): memoizing
    `_StreamDecoder.decode_form` under a CONSTANT key makes FmB reuse FmA's bytes, so the second
    polyline becomes (100,0)->(105,0) instead of (100,0)->(100,9)."""
    pdf = _pdf(
        [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600]"
            b" /Resources << /XObject << /FmA 5 0 R /FmB 6 0 R >> >> /Contents 4 0 R >>",
            _stream(b"q /FmA Do Q q 1 0 0 1 100 0 cm /FmB Do Q"),
            _form_obj(b"0 0 m 5 0 l S"),      # FmA: horizontal segment to (5, 0)
            _form_obj(b"0 0 m 0 9 l S"),      # FmB: vertical segment to (0, 9)
        ]
    )
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)
    polylines = doc.pages[0].polylines
    assert len(polylines) == 2
    assert _flat(polylines[0].points) == pytest.approx([0.0, 0.0, 5.0, 0.0])       # FmA at origin
    assert _flat(polylines[1].points) == pytest.approx([100.0, 0.0, 100.0, 9.0])   # FmB, DISTINCT


def test_multi_stream_document_decoded_bytes_budget_is_per_document(monkeypatch):
    """DB-064 (b): a /Contents array of streams that are EACH under the per-stream cap but whose
    decoded bytes SUM over the (patched) document total is refused, exercising the per-DOCUMENT
    accumulation. Mutant (report): charging `_StreamDecoder.charge_decoded` per-stream (each 13 <
    20) never refuses, so no SheetRefusal is produced."""
    monkeypatch.setattr(sheet_reader, "MAX_TOTAL_DECODED_BYTES", 20)  # each stream 13 B; sum 26 B
    stream = _stream(b"5 7 m 9 3 l S")                                # 13 raw bytes, no /Filter
    pdf = _pdf(
        [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents [4 0 R 5 0 R] >>",
            stream,
            stream,
        ]
    )
    refusal = sheet_refusal(read_sheet(pdf))
    assert refusal is not None
    assert refusal.feature == "decoded bytes budget"
