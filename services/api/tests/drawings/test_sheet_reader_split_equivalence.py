"""Byte-identical equivalence + guard-mutation tests for the M5-T094 reader split.

The architect drawing-sheet reader was split (DB-055 b) into
:mod:`app.drawings.sheet_objects` (object graph + stream decode + budgets + form memo),
:mod:`app.drawings.sheet_interpreter` (the content-stream operator interpreter), and the
compatibility facade :mod:`app.drawings.sheet_reader` (public entry, bounds, backstop,
page-tree driver). This file proves the split changed NO behaviour:

* AS-2 byte-identical: a 63-case corpus (curves, CTM, q/Q, forms incl. cycles/depth,
  images, text, every refusal class, the budgets) is serialized into a canonical,
  order-preserving form; its per-case + overall sha256 digests must equal the GOLDEN
  captured from the PRE-split module (pinned below). The budget cases apply the same
  facade-constant patch the existing suite uses, so they also prove the split still
  threads a patched bound into the running interpreter/decoder. M5-T113 DELIBERATELY revised
  the /DecodeParms golden (DB-076 a): the former single `refuse_decode_parms` refusal case is
  replaced by `decode_parms_png_predictor` (now a drawn success) + `refuse_decode_parms_tiff`
  (TIFF predictor still refused); the other 61 cases stay byte-pinned to the pre-split baseline,
  and their digests are UNCHANGED, so the split-equivalence proof holds for everything the split
  touched. The two revised digests were recaptured from the CURRENT module (M5-T113 report).
* AS-4 each security guard is load-bearing: one mutation per guard (flatten point budget,
  decoded-bytes budget, form depth guard, form cycle guard, top-level backstop, finiteness
  gate) reddens a test.

The 37 pre-existing tests in tests/drawings/test_sheet_reader.py cover the public API and
are asserted UNCHANGED (not edited). The GOLDEN digests here were captured against the
pre-split module BEFORE any edit; see project-control/reports/M5-T094-producer-report.md.
"""

from __future__ import annotations

import hashlib
import math
import zlib

import pytest

from app.drawings import sheet_interpreter, sheet_objects, sheet_reader
from app.drawings.sheet_primitives import (
    SheetDocument,
    SheetImage,
    SheetPage,
    SheetPolyline,
    SheetRefusal,
    SheetTextRun,
)


# ----------------------------------------------------------------- PDF byte builders
def _num(value: float) -> bytes:
    return f"{value:.10f}".encode("ascii")


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


def _flate_png_pred(content: bytes, predictor: int = 12) -> bytes:
    """A content stream flate-compressing ONE PNG-predictor row (filter tag 2 = Up, previous row
    = zeros, so the forward-filtered bytes equal ``content`` and the reader recovers ``content``
    only by stripping the tag byte and un-filtering). The row spans ``len(content)`` columns.
    Tag 2 (not 0) makes the predictor load-bearing: without it the leading tag byte 0x02 is an
    illegal token, so a success here proves the §7.4.4.4 predictor path ran (M5-T113 DB-076 a)."""
    columns = len(content)
    row = bytes([2]) + content  # tag 2 (Up) with a zero previous row leaves the row unchanged
    extra = (
        b" /Filter /FlateDecode /DecodeParms << /Predictor %d /Columns %d >>"
        % (predictor, columns)
    )
    return _stream(zlib.compress(row), extra)


def _flate_tiff_pred(content: bytes) -> bytes:
    """A flate content stream declaring the TIFF predictor (2), which stays a typed refusal."""
    extra = b" /Filter /FlateDecode /DecodeParms << /Predictor 2 /Columns %d >>" % len(content)
    return _stream(zlib.compress(content), extra)


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


def _form_obj(content: bytes, extra: bytes = b"") -> bytes:
    return _stream(content, b" /Type /XObject /Subtype /Form /BBox [0 0 1 1]%s" % extra)


def _flate_form(content: bytes, extra: bytes = b"") -> bytes:
    return _flate(content, b" /Type /XObject /Subtype /Form /BBox [0 0 1 1]%s" % extra)


def _quarter_circle_content(radius: float) -> bytes:
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


_COS = math.cos(math.radians(30.0))
_SIN = math.sin(math.radians(30.0))


# --------------------------------------------------------------- canonical serializer
def _f(value: float) -> str:
    """Deterministic, round-trip float repr (identical across runs of one interpreter)."""
    return repr(float(value))


def _seq(values) -> str:
    return "[" + ",".join(_f(v) for v in values) + "]"


def _point(pt) -> str:
    return "(" + _f(pt[0]) + "," + _f(pt[1]) + ")"


def _polyline(poly: SheetPolyline) -> str:
    pts = ";".join(_point(p) for p in poly.points)
    return f"PL<pts={pts}|closed={poly.closed}|stroked={poly.stroked}|filled={poly.filled}>"


def _text_run(run: SheetTextRun) -> str:
    return (
        f"TR<text={run.text!r}|x={_f(run.x)}|y={_f(run.y)}"
        f"|fs={_f(run.font_size)}|m={_seq(run.matrix)}>"
    )


def _image(img: SheetImage) -> str:
    return (
        f"IM<name={img.name!r}|m={_seq(img.matrix)}|w={img.width}|h={img.height}"
        f"|bpc={img.bits_per_component}|cs={img.color_space!r}>"
    )


def _page(page: SheetPage) -> str:
    parts = [
        f"index={page.index}",
        f"media_box={_seq(page.media_box)}",
        f"user_unit={_f(page.user_unit)}",
        f"flatten_tolerance={_f(page.flatten_tolerance)}",
        "polylines=[" + "|".join(_polyline(p) for p in page.polylines) + "]",
        "text_runs=[" + "|".join(_text_run(t) for t in page.text_runs) + "]",
        "images=[" + "|".join(_image(i) for i in page.images) + "]",
        f"image_count={page.image_count}",
    ]
    return "PAGE{" + ";".join(parts) + "}"


def serialize(result: object) -> bytes:
    """Total, order-preserving canonical form of a read_sheet result."""
    if isinstance(result, SheetRefusal):
        text = (
            f"REFUSAL|reject_code={result.reject_code}|feature={result.feature}"
            f"|detail={result.detail}|origin={result.origin}"
        )
        return text.encode()
    if isinstance(result, SheetDocument):
        head = (
            f"DOCUMENT|flatten_tolerance={_f(result.flatten_tolerance)}"
            f"|pages={len(result.pages)}"
        )
        body = "\n".join(_page(p) for p in result.pages)
        return (head + "\n" + body).encode()
    return f"UNKNOWN|{type(result).__name__}".encode()


# ---------------------------------------------------------------------- corpus cases
def _cases() -> list[tuple[str, bytes, float, dict]]:
    """(name, pdf_bytes, flatten_tolerance, patches). Patches are applied to the
    sheet_reader module around the single read_sheet call (default budgets are far too
    large to hit with small inputs, so the budget cases lower them exactly as the
    existing suite does; this also exercises that the split threads the patched value)."""
    D = 0.25  # DEFAULT_FLATTEN_TOLERANCE
    cases: list[tuple[str, bytes, float, dict]] = []
    a = cases.append

    # --- success: geometry
    a(("line", _one_page(b"5 7 m 9 3 l S"), D, {}))
    a(("quarter_circle_tol05", _one_page(_quarter_circle_content(200.0)), 0.5, {}))
    a(("asym_bezier", _one_page(b"0 0 m 1 0 50 40 100 0 c S"), 0.5, {}))
    a(("v_curve", _one_page(b"10 10 m 20 20 30 10 y S"), D, {}))
    a(("y_curve", _one_page(b"10 10 m 20 20 30 10 v S"), D, {}))
    a(("rect_fill", _one_page(b"0 0 100 50 re f"), D, {}))
    a(("rect_fill_stroke_close", _one_page(b"0 0 m 10 0 l 10 10 l h B"), D, {}))
    a(("segment_after_close", _one_page(b"0 0 m 10 0 l 10 10 l h 20 20 l S"), D, {}))
    a(("noop_paint_n", _one_page(b"0 0 m 10 10 l n"), D, {}))
    a(("two_subpaths_one_paint", _one_page(b"0 0 m 5 5 l 10 0 m 15 5 l S"), D, {}))

    # --- success: transforms
    rot = b"%s %s %s %s 0 0 cm" % (_num(_COS), _num(_SIN), _num(-_SIN), _num(_COS))
    a(("ctm_rotate_translate", _one_page(b"q 1 0 0 1 10 20 cm %s 5 7 m 9 3 l S Q" % rot), D, {}))
    a(("ctm_shear", _one_page(b"q 1 0 %s 1 0 0 cm 5 7 m 9 3 l S Q" % _num(0.4)), D, {}))
    a(("nested_q_q_restore", _one_page(b"q 1 0 0 1 100 100 cm Q 5 7 m 9 3 l S"), D, {}))
    a(("mid_path_cm_device", _one_page(b"10 10 m 2 0 0 2 0 0 cm 10 10 20 10 20 20 c S"), D, {}))

    # --- success: text
    a(("text_simple", _one_page(b"BT /F1 12 Tf 100 200 Td (Hi) Tj ET",
                                 resources=b"<< /Font << /F1 << >> >> >>"), D, {}))
    tm = b"%s %s %s %s 100 200 Tm" % (_num(_COS), _num(_SIN), _num(-_SIN), _num(_COS))
    a(("text_rotated_tm", _one_page(b"BT /F1 12 Tf %s (Hi) Tj ET" % tm,
                                    resources=b"<< /Font << /F1 << >> >> >>"), D, {}))
    a(("text_tj_array", _one_page(b"BT /F1 10 Tf 0 0 Td [(A) -20 (B)] TJ ET",
                                  resources=b"<< /Font << /F1 << >> >> >>"), D, {}))
    a(("text_quote_ops", _one_page(b"BT /F1 10 Tf 5 TL 0 0 Td (a) ' 3 4 (b) \" ET",
                                   resources=b"<< /Font << /F1 << >> >> >>"), D, {}))
    a(("text_td_tdd_tstar", _one_page(b"BT /F1 8 Tf 5 TL 1 2 Td (a) Tj 3 4 TD (b) Tj T* (c) Tj ET",
                                      resources=b"<< /Font << /F1 << >> >> >>"), D, {}))
    a(("q_q_font_size", _one_page(b"/F1 10 Tf q /F1 30 Tf BT (A) Tj ET Q BT (B) Tj ET",
                                  resources=b"<< /Font << /F1 << >> >> >>"), D, {}))

    # --- success: forms + images
    a(("form_twice", _one_page(
        b"q 100 0 0 100 0 0 cm /Fm0 Do Q q 1 0 0 1 200 50 cm /Fm0 Do Q",
        resources=b"<< /XObject << /Fm0 5 0 R >> >>",
        extra_objects=(_form_obj(b"0 0 m 1 0 l S"),)), D, {}))
    a(("form_matrix", _one_page(
        b"/Fm0 Do",
        resources=b"<< /XObject << /Fm0 5 0 R >> >>",
        extra_objects=(_form_obj(b"0 0 m 1 1 l S", b" /Matrix [2 0 0 2 5 5]"),)), D, {}))
    a(("form_inherits_text", _one_page(
        b"/F1 14 Tf /Fm0 Do",
        resources=b"<< /Font << /F1 << >> >> /XObject << /Fm0 5 0 R >> >>",
        extra_objects=(_form_obj(b"BT (X) Tj ET"),)), D, {}))
    a(("form_flate", _one_page(
        b" ".join([b"/Fm0 Do"] * 3),
        resources=b"<< /XObject << /Fm0 5 0 R >> >>",
        extra_objects=(_flate_form(b"0 0 m 1 0 l S"),)), D, {}))
    a(("image_counted", _one_page(
        b"q 50 0 0 40 10 20 cm /Im0 Do Q",
        resources=b"<< /XObject << /Im0 5 0 R >> >>",
        extra_objects=(_stream(
            b"\xff\xd8\xff\xe0not-a-real-jpeg",
            b" /Type /XObject /Subtype /Image /Width 8 /Height 6"
            b" /BitsPerComponent 8 /ColorSpace /DeviceRGB /Filter /DCTDecode"),)), D, {}))
    a(("image_missing_dims", _one_page(
        b"/Im0 Do",
        resources=b"<< /XObject << /Im0 5 0 R >> >>",
        extra_objects=(_stream(
            b"raw", b" /Type /XObject /Subtype /Image"),)), D, {}))

    # --- success: content variants
    a(("flate_content", _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
        _flate(b"5 7 m 9 3 l S"),
    ]), D, {}))
    a(("contents_array", _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents [4 0 R 5 0 R] >>",
        _stream(b"0 0 m 10 0 l S"),
        _stream(b"20 20 m 30 30 l S"),
    ]), D, {}))
    a(("inherited_box_res", _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 /MediaBox [0 0 400 300]"
        b" /Resources << /Font << /F1 << >> >> >> >>",
        b"<< /Type /Page /Parent 2 0 R /Contents 4 0 R >>",
        _stream(b"BT /F1 12 Tf 0 0 Td (a) Tj ET"),
    ]), D, {}))
    a(("user_unit_media", _one_page(b"5 7 m 9 3 l S", page_extra=b" /UserUnit 2.5"), D, {}))
    a(("multipage", _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R 5 0 R] /Count 2 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
        _stream(b"0 0 m 10 10 l S"),
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 6 0 R >>",
        _stream(b"20 20 m 30 30 l S"),
    ]), D, {}))
    a(("empty_contents_absent", _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] >>",
    ]), D, {}))

    # --- refusals: strict-reader origin
    a(("refuse_malformed_header", b"not a pdf at all", D, {}))
    encrypted = _one_page(b"5 7 m 9 3 l S").replace(
        b"/Root 1 0 R", b"/Root 1 0 R /Encrypt 1 0 R")
    a(("refuse_encryption", encrypted, D, {}))

    # --- refusals: decode subset
    a(("refuse_filter_lzw", _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
        _stream(b"garbage", b" /Filter /LZWDecode"),
    ]), D, {}))
    # M5-T113 DELIBERATE golden revision (DB-076 a): the pre-M5-T113 corpus had a single
    # `refuse_decode_parms` case that FROZE /DecodeParms as an unconditional "decode parameters"
    # refusal. That behaviour is intentionally changed here: a content stream with /FlateDecode +
    # a §7.4.4.4 PNG predictor now DECODES and draws, while the TIFF predictor (2) stays a typed
    # refusal. The old case is replaced by these two (before -> after recorded in the M5-T113
    # producer report). Every OTHER case below stays byte-pinned to the pre-split golden, so the
    # M5-T094 split-equivalence proof is intact for everything the split actually touched.
    a(("decode_parms_png_predictor", _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
        _flate_png_pred(b"5 7 m 9 3 l S"),
    ]), D, {}))
    a(("refuse_decode_parms_tiff", _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
        _flate_tiff_pred(b"5 7 m 9 3 l S"),
    ]), D, {}))
    a(("refuse_filter_array", _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
        _stream(b"x", b" /Filter [/FlateDecode]"),
    ]), D, {}))

    # --- refusals: profile operator / structure
    # M5-T118 DELIBERATE golden revision: the former probe used `sh`, which is now SKIPPED as
    # non-geometry (a colour shading, §8.7.4.2 — see test_sheet_p3_features.py) rather than
    # refused, so it can no longer stand for an unsupported operator. The case keeps its PURPOSE
    # (proving an out-of-subset operator is a typed "unsupported operator" refusal) with a
    # genuinely out-of-subset token `zz`; its digest and _OVERALL are recaptured below.
    a(("refuse_unsupported_op", _one_page(b"0 0 1 sc 5 5 zz"), D, {}))
    a(("refuse_unsupported_op_long", _one_page(b"Z" * 100_000), D, {}))
    a(("refuse_dangling_operands", _one_page(b"1 2 3"), D, {}))
    a(("refuse_unclosed_text", _one_page(b"BT /F1 12 Tf",
                                         resources=b"<< /Font << /F1 << >> >> >>"), D, {}))
    a(("refuse_unbalanced_q", _one_page(b"q q"), D, {}))
    a(("refuse_unbalanced_Q", _one_page(b"Q"), D, {}))
    a(("refuse_text_before_tf", _one_page(b"BT (x) Tj ET"), D, {}))
    a(("refuse_nested_bt", _one_page(b"BT BT ET ET"), D, {}))
    # M5-T120 (DB-090 i): a post-paint `l` with no current point now OPENS a subpath at its own
    # point (a read, not a refusal), so the former `5 5 l S` refusal probe is replaced by an orphan
    # CURVE, which STAYS a typed "curve with no current point" refusal (the new orphan-lineto READ
    # behaviour + its mutations live in tests/drawings/test_sheet_p4_features.py).
    a(("refuse_curve_no_current", _one_page(b"5 5 10 10 20 20 c S"), D, {}))
    a(("refuse_nested_inline_array", _one_page(b"BT /F1 10 Tf [[ ]] TJ ET",
                                               resources=b"<< /Font << /F1 << >> >> >>"), D, {}))

    # --- refusals: object graph / page tree
    a(("refuse_catalog_no_type", _pdf([
        b"<< /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
        _stream(b"5 7 m 9 3 l S"),
    ]), D, {}))
    a(("refuse_missing_media_box", _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Contents 4 0 R >>",
        _stream(b"5 7 m 9 3 l S"),
    ]), D, {}))
    a(("refuse_bad_media_box", _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800] /Contents 4 0 R >>",
        _stream(b"5 7 m 9 3 l S"),
    ]), D, {}))
    a(("refuse_unresolvable_ref", _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [99 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
        _stream(b"5 7 m 9 3 l S"),
    ]), D, {}))
    a(("refuse_xobject_cycle", _one_page(
        b"/Fm0 Do",
        resources=b"<< /XObject << /Fm0 5 0 R >> >>",
        extra_objects=(_form_obj(b"/Fm0 Do"),)), D, {}))
    a(("refuse_xobject_missing", _one_page(
        b"/Nope Do",
        resources=b"<< /XObject << /Fm0 5 0 R >> >>",
        extra_objects=(_form_obj(b"0 0 m 1 0 l S"),)), D, {}))
    a(("refuse_bad_input_type", None, D, {}))  # sentinel: non-bytes input
    a(("refuse_bad_tolerance", _one_page(b"5 7 m 9 3 l S"), -1.0, {}))
    a(("refuse_nonfinite_coord",
       _one_page(b" ".join([b"%s 0 0 %s 0 0 cm" % (b"1" + b"0" * 39, b"1" + b"0" * 39)] * 10)
                 + b" 1 1 m 2 2 l S"), D, {}))

    # --- refusals: budgets (patched exactly as the existing suite does)
    a(("refuse_operator_count", _one_page(b"q q q q q q Q Q Q Q Q Q"), D,
       {"MAX_CONTENT_OPERATORS": 3}))
    a(("refuse_path_points", _one_page(b"0 0 m 1 1 l 2 2 l 3 3 l 4 4 l S"), D,
       {"MAX_PATH_POINTS": 2}))
    a(("refuse_q_depth", _one_page(b"q q q Q Q Q"), D, {"MAX_Q_DEPTH": 2}))
    a(("refuse_xobject_depth", _one_page(
        b"/FmA Do",
        resources=b"<< /XObject << /FmA 5 0 R /FmB 6 0 R >> >>",
        extra_objects=(_form_obj(b"/FmB Do"), _form_obj(b"0 0 m 1 0 l S"))), D,
       {"MAX_XOBJECT_DEPTH": 1}))
    a(("refuse_decoded_bytes", _one_page(b"5 7 m 9 3 l S"), D,
       {"MAX_TOTAL_DECODED_BYTES": 4}))
    a(("refuse_stream_size", _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
        _stream(b"5 7 m 9 3 l S"),
    ]), D, {"MAX_DECODED_STREAM_BYTES": 4}))

    return cases


def run_corpus(sr) -> list[tuple[str, bytes]]:
    """Run every case through sr.read_sheet, applying per-case patches around the one
    call, and return ordered (name, canonical_bytes)."""
    out: list[tuple[str, bytes]] = []
    for name, pdf, tol, patches in _cases():
        saved: dict = {}
        for key, value in patches.items():
            saved[key] = getattr(sr, key)
            setattr(sr, key, value)
        try:
            arg = pdf if pdf is not None else "not bytes"
            result = sr.read_sheet(arg, flatten_tolerance=tol)
        finally:
            for key, value in saved.items():
                setattr(sr, key, value)
        out.append((name, serialize(result)))
    return out


def digests(sr) -> list[tuple[str, str]]:
    return [(name, hashlib.sha256(blob).hexdigest()) for name, blob in run_corpus(sr)]


def overall_digest(sr) -> str:
    h = hashlib.sha256()
    for name, blob in run_corpus(sr):
        h.update(name.encode())
        h.update(b"\x00")
        h.update(blob)
        h.update(b"\x00")
    return h.hexdigest()


# GOLDEN: captured from the PRE-split sheet_reader module before any edit (M5-T094); the two
# `*decode_parms*` cases were DELIBERATELY recaptured at M5-T113 (DB-076 a). M5-T118 recaptured
# `refuse_unsupported_op` (its former `sh` probe is now a skipped shading op — DB-055 c/d). M5-T120
# replaced `refuse_l_no_current` (`5 5 l S`, now a READ) with `refuse_curve_no_current` (an orphan
# curve, still a refusal — DB-090 i) and recaptured _OVERALL; the sheet_interpreter path-state split
# (DB-090 c) and the /DP-dictionary + citation changes (DB-090 a/b) changed NO other case digest
# (verified: the only CHANGED case is the deliberate l->curve substitution). All 62 unrevised
# per-case digests are UNCHANGED.
_OVERALL = "264b54168d4317dcbee4802eff2b6b4524f73d0487ab2adcc9465c9bc3b00efd"
_GOLDEN = {
    "asym_bezier": "dcb1a08370e49f494484da30dd28c531020eee8c430616400520862ab8d4018d",
    "contents_array": "feccdc8409a6c869b185c9db02f8473503e03c271e3e015f5d9240afe3a49e39",
    "ctm_rotate_translate": "a1ff5fede3a7f9173dc5778f333a8f42fce0d25506f901a541911640665e4047",
    "ctm_shear": "6f6c0b81d2d1fe464564040627bf0eebc1b6ab8dc1fc7bb09b75974fef34c78b",
    # M5-T113 (DB-076 a): a /FlateDecode + PNG-predictor content stream now DECODES and draws
    # the line (5,7)->(9,3), so its canonical form equals the plain `line` case's.
    "decode_parms_png_predictor":
        "f1b2f8353122b7680f3c43eaa03773396eab071dd39143456846e65e945da6e0",
    "empty_contents_absent": "e936fda65058735ca2668323def79a3f346965745be75afb9a51d7a8559f26d7",
    "flate_content": "f1b2f8353122b7680f3c43eaa03773396eab071dd39143456846e65e945da6e0",
    "form_flate": "553b3239e54c79b18e241c59e795a380435792e2f3c3ad83727cba3ebbfaa379",
    "form_inherits_text": "eab4ece70b1480dfd2a626f0ae5cccb09f22b2d51ab94aca07054a14ad44efd7",
    "form_matrix": "de3c4eef43b9e79417ee76d0f1a871746888919beaa75dd5f5533594ad9c3e62",
    "form_twice": "9a4a7e6609a65a1ab1f7b0bd72d92e37d804d0250ab1779ebf5b9c2e1e997c09",
    "image_counted": "7cf817dffae50b7799b8f475a2ad0b599ae4deb353f760fb1149a87abf81f802",
    "image_missing_dims": "d4e2b4dcf04522943974511f701ba2b8994697e2028505a5ccfd0ae5ee242d4c",
    "inherited_box_res": "1b1a6c92c1b46b75754f629a3ec6963218cfc4a510b49c8ace3f0e70d8fcdd62",
    "line": "f1b2f8353122b7680f3c43eaa03773396eab071dd39143456846e65e945da6e0",
    "mid_path_cm_device": "3ac97dc23e6d5bb611df4169d767106cd89c3d5f751dd31d69eca171ca34dfaa",
    "multipage": "32918b4a10cceef6b1248b3d4f0b3a3aa8750242767df6a2c915ec0fe7ed0877",
    "nested_q_q_restore": "f1b2f8353122b7680f3c43eaa03773396eab071dd39143456846e65e945da6e0",
    "noop_paint_n": "5ee3749701fd64b414f8e93720c3b78b9eb8ad8db649902a6029bafc6fbfc738",
    "q_q_font_size": "67f89586aa6066973010d4a471828c8655be6168dc29f994a1243dac93f7e6b5",
    "quarter_circle_tol05": "5a4b53f45c5b666be1741ff12963053c3c31723b559602c8607542d76ada1402",
    "rect_fill": "15210e5b3b3084d3b3dcd381834201f106372f3b045db9dbf4230d59156d0ac7",
    "rect_fill_stroke_close": "ea093481cb2c76eaf042da606bfab54c0c44bc8a80b57f74a551ce8b373b6b2b",
    "refuse_bad_input_type": "bbe1bed52a85bc90dc536cb1e8e79b9713844c497946d050779ba20380f28ce7",
    "refuse_bad_media_box": "be71e8ca6e07b88b887add265cb9b4b31cca6ce3c96bbde8d4b820e8820add81",
    "refuse_bad_tolerance": "ad1b54a3535f3d8a8c04f7bbc372f3d1369b6af55eeafea8d1397da7c97f0f67",
    "refuse_catalog_no_type": "8a37488d19f12d98774940bdbb77cfe56f97da756460a74f9781b4910575ee65",
    # M5-T120 (DB-090 i): replaces the former `refuse_l_no_current` (`5 5 l S`), which now READS as
    # an orphan-lineto subpath; an orphan CURVE stays a "curve with no current point" refusal.
    "refuse_curve_no_current": "53a90aae3d41353208ade352d13eaabb09f49e70bccf8786a1fe4007df40b965",
    "refuse_dangling_operands": "33270203463528e67ae85880bda46263cd9d03d1c898161e616735fe79f7c2f6",
    # M5-T113 (DB-076 a): the TIFF predictor (2) stays a typed "predictor" refusal (the new
    # "what stays unsupported" golden case; the former unconditional refuse_decode_parms is gone).
    "refuse_decode_parms_tiff":
        "f0c87de8e7d60cfc42304a901dadd438661664811f570926778b6d4788a2b479",
    "refuse_decoded_bytes": "5f8b8a5e8b71f156859585bf6e24f95703561baace05dd7207ef85987a89115e",
    "refuse_encryption": "d46f4bb36448f8090dc8bc773337c14bd6331563c8640271df367cc1192bfc68",
    "refuse_filter_array": "5a9210588a524427a52a2691d9a33d7d486274ea65d79fd2c399fd351e15e9bb",
    "refuse_filter_lzw": "04432e1061622c153de41270d74ac94465a8fd1222ad307fa7da5831d50a6eb6",
    "refuse_malformed_header": "3855b2b5917f029c482e1e94e982938ed52f70bf4b89791d98393f5292b1da89",
    "refuse_missing_media_box": "ee8a73cd995259969303666638effd59cc352c541abb88adf590a60b87181be9",
    "refuse_nested_bt": "d9a885312cff03cc14ddfde1860af08c8db6c9b9961a36e22d59840e7fcbf26e",
    "refuse_nested_inline_array":
        "864478d022a19e11dcb14579757dbd51059d643d786ad0bf056b8caa9ac04289",
    "refuse_nonfinite_coord": "9d73f57ac107da4684aeefba74a0b757192330de7ec389ac61cce63c473f9ca8",
    "refuse_operator_count": "2020b930bd55e9796639edf8992c851c02c0946f29ee0e3336ca8f0ece7ddc7f",
    "refuse_path_points": "ce6ce09369e2dbcb921decfeeee5477020dd804d67cb14336cdb35a1d5c0345e",
    "refuse_q_depth": "d2f3d150c6f47b1955563ecc3c58f4da1148d0d96496128dc18586e0bc604396",
    "refuse_stream_size": "1779f54f6693fae47aa65d362bf6806eda4678c638f1b2b8689792b1f5e4f582",
    "refuse_text_before_tf": "44d0391f805f5a650b5b4ebd6ccdb1d208858b9914c4e74376ed3bd61e5d6607",
    "refuse_unbalanced_Q": "f96940f9d93c2638cad5a7937b8b83db21f7bd37a14ac19fe14eb4e676145553",
    "refuse_unbalanced_q": "c48991f9a5255dac746340193184ab4f93e67c60362bdb43a617680babb152e9",
    "refuse_unclosed_text": "95b072ac6da9b4b93109294313850ef8fc58602e976d54fe8fb0f74cd13fa311",
    "refuse_unresolvable_ref": "dd04e7444ee22a94406a2425bad7a2fdc35c59101f3444c04b72ca230f0e031e",
    # M5-T118: recaptured after the `sh` probe became `zz` (see the corpus-case comment).
    "refuse_unsupported_op": "c4353d678cf4a7f9a54410b12f79c0874208b6ae1677b277fc8a4ac75415cee0",
    "refuse_unsupported_op_long":
        "e5241b3d714963af50c4471472fd98a30f4b1de65b923c85376de3e6c56e26a6",
    "refuse_xobject_cycle": "45df1f0551c6c7318da4c6a553c4b0015fa12a29bcae08aa70241f267d212f1f",
    "refuse_xobject_depth": "1e577241fc7ca5c3a3657a1f8bba510bcc55b42e386874bd230013fdd3469b5a",
    "refuse_xobject_missing": "5f59e7f328a0b84bc5b7198ea145461a01b1bb8d40fcb3a772653b026598f418",
    "segment_after_close": "a5596c6cd7d29ca757d2134b61bd6b60a600264d2576207d99438221f736d104",
    "text_quote_ops": "d33d51a09212cbb11e8f0e2e3520c530e89bc82da8b88bf142a4ab48f0d0c1d3",
    "text_rotated_tm": "88413ec0c37d49cce423276569ab50460c6c0f2b1ce792c3bc10cd63f58857d2",
    "text_simple": "92f57a951e1f74cff39c0819853f7a1908ed232771f0e8accf0a630261aa740a",
    "text_td_tdd_tstar": "d84ca5bc7cf9a9f7746cc43bb0a4405a8218067d2eed173d1381665c91f092f0",
    "text_tj_array": "07e1ed9182de447f43b8ce54ee01675228e4cbb68202136b553876048e56b5d8",
    "two_subpaths_one_paint": "3ead5384ba1bbea8a7d3004a57f2d63fd016c875ce762ffe39625a1dba639c26",
    "user_unit_media": "a032ac0f7b83a6fb6075cf1cf1139c08afbf82fc550ba011bc3c6d8b9c6b9030",
    "v_curve": "49f8ab47e9e3ffaa4f84ac60417c7d90100eba38ee7b14926f322d4fca00e955",
    "y_curve": "ef5dac1966037bb250539b1c10f44dd6104f964026bf52ca6e33b5b893968803",
}


# =========================================================== AS-2 byte-identical equivalence
def test_corpus_shape_is_nontrivial():
    """Guard against an accidental all-refuse (or all-success) regression that would make
    the digest comparison vacuous."""
    blobs = dict(run_corpus(sheet_reader))
    assert len(blobs) == 63
    docs = sum(1 for b in blobs.values() if b.startswith(b"DOCUMENT"))
    refs = sum(1 for b in blobs.values() if b.startswith(b"REFUSAL"))
    assert docs >= 25 and refs >= 25


def test_equivalence_overall_digest_matches_pre_split_golden():
    assert overall_digest(sheet_reader) == _OVERALL


def test_equivalence_every_case_matches_pre_split_golden():
    got = dict(digests(sheet_reader))
    assert set(got) == set(_GOLDEN)  # no case added/removed vs the pinned golden
    mismatches = {k: {"got": got[k], "golden": _GOLDEN[k]}
                  for k in _GOLDEN if got[k] != _GOLDEN[k]}
    assert not mismatches, f"byte-divergent cases after the split: {mismatches}"


# =============================================================== AS-4 guards are load-bearing
def _big_curve_pdf() -> bytes:
    # huge control coords (plain decimal, <= 64 bytes, no exponent) that never satisfy the
    # flatness test; a budget-ignoring flattener would emit 2**MAX_FLATTEN_DEPTH points.
    content = (
        b"0 0 m "
        b"1000000000000000000 1000000000000000000 "
        b"2000000000000000000 -1000000000000000000 "
        b"3000000000000000000 0 c S"
    )
    return _one_page(content)


def test_as4_flatten_point_budget_is_load_bearing(monkeypatch):
    """Guard: the remaining-point budget threaded into flattening. REAL: a never-flat curve
    refuses 'path points'. MUTANT: a flattener that ignores the budget completes with a
    bounded polyline and the read SUCCEEDS -> the budget guard has teeth."""
    monkeypatch.setattr(sheet_reader, "MAX_PATH_POINTS", 5000)
    ref = sheet_reader.sheet_refusal(sheet_reader.read_sheet(_big_curve_pdf()))
    assert ref is not None and ref.feature == "path points"

    def _ignore_budget(p0, p1, p2, p3, tol, out, depth, budget):
        out.append(p3)  # no subdivision, no budget check
        return True

    monkeypatch.setattr(sheet_reader, "_flatten_cubic", _ignore_budget)
    assert isinstance(sheet_reader.read_sheet(_big_curve_pdf()), SheetDocument)


def test_as4_decoded_bytes_budget_is_load_bearing(monkeypatch):
    """Guard: the document-wide decoded-bytes budget. REAL: a page decode over the cap
    refuses 'decoded bytes budget'. MUTANT: a charge that never refuses lets it through."""
    monkeypatch.setattr(sheet_reader, "MAX_TOTAL_DECODED_BYTES", 4)
    ref = sheet_reader.sheet_refusal(sheet_reader.read_sheet(_one_page(b"5 7 m 9 3 l S")))
    assert ref is not None and ref.feature == "decoded bytes budget"

    monkeypatch.setattr(sheet_objects._StreamDecoder, "charge_decoded", lambda self, count: None)
    assert isinstance(sheet_reader.read_sheet(_one_page(b"5 7 m 9 3 l S")), SheetDocument)


def test_as4_form_depth_guard_is_load_bearing(monkeypatch):
    """Guard: the Form XObject recursion-depth bound. REAL: a nesting past the bound refuses
    'xobject recursion'. MUTANT: a placement that resets its depth defeats the bound (the
    nesting is acyclic, so it terminates as a document)."""
    pdf = _one_page(
        b"/FmA Do",
        resources=b"<< /XObject << /FmA 5 0 R /FmB 6 0 R >> >>",
        extra_objects=(_form_obj(b"/FmB Do"), _form_obj(b"0 0 m 1 0 l S")),
    )
    monkeypatch.setattr(sheet_reader, "MAX_XOBJECT_DEPTH", 1)
    ref = sheet_reader.sheet_refusal(sheet_reader.read_sheet(pdf))
    assert ref is not None and ref.feature == "xobject recursion"

    real_place = sheet_interpreter._StreamRun._place_form

    def _no_depth_guard(self, name, stream, ref_key):
        self._depth = -100  # defeat the depth comparison (acyclic input still terminates)
        return real_place(self, name, stream, ref_key)

    monkeypatch.setattr(sheet_interpreter._StreamRun, "_place_form", _no_depth_guard)
    assert isinstance(sheet_reader.read_sheet(pdf), SheetDocument)


def test_as4_form_cycle_guard_is_load_bearing(monkeypatch):
    """Guard: the Form XObject cycle refusal. REAL: a self-referencing form refuses
    'xobject cycle'. MUTANT: a placement that forgets its ancestor set stops detecting the
    cycle and instead trips the depth bound -> the feature is no longer 'xobject cycle'."""
    pdf = _one_page(
        b"/Fm0 Do",
        resources=b"<< /XObject << /Fm0 5 0 R >> >>",
        extra_objects=(_form_obj(b"/Fm0 Do"),),
    )
    ref = sheet_reader.sheet_refusal(sheet_reader.read_sheet(pdf))
    assert ref is not None and ref.feature == "xobject cycle"

    real_place = sheet_interpreter._StreamRun._place_form

    def _no_cycle_guard(self, name, stream, ref_key):
        self._stack = frozenset()  # forget ancestors -> cycle undetected
        return real_place(self, name, stream, ref_key)

    monkeypatch.setattr(sheet_interpreter._StreamRun, "_place_form", _no_cycle_guard)
    ref2 = sheet_reader.sheet_refusal(sheet_reader.read_sheet(pdf))
    assert ref2 is not None and ref2.feature != "xobject cycle"


def test_as4_top_level_backstop_is_load_bearing(monkeypatch):
    """Guard: the read_sheet try/except that turns any unexpected error into a refusal VALUE.
    REAL: an internal RuntimeError becomes an 'unexpected error' refusal. MUTANT: bypassing the
    backstop (calling _read_sheet directly) lets the exception propagate."""
    def _boom(_table):
        raise RuntimeError("internal boom with attacker detail")

    monkeypatch.setattr(sheet_reader, "_catalog_pages_root", _boom)
    ref = sheet_reader.sheet_refusal(sheet_reader.read_sheet(_one_page(b"5 7 m 9 3 l S")))
    assert ref is not None and ref.feature == "unexpected error"
    assert "attacker detail" not in ref.detail  # only the exception TYPE leaks

    with pytest.raises(RuntimeError):  # without the backstop the value contract is lost
        sheet_reader._read_sheet(_one_page(b"5 7 m 9 3 l S"), flatten_tolerance=0.25)


def test_as4_finiteness_gate_is_load_bearing(monkeypatch):
    """Guard: the non-finite coordinate refusal after CTM math. REAL: a CTM that overflows to
    inf refuses 'non-finite coordinate'. MUTANT: a finiteness check that always passes admits
    the inf coordinate as a document."""
    content = (
        b" ".join([b"%s 0 0 %s 0 0 cm" % (b"1" + b"0" * 39, b"1" + b"0" * 39)] * 10)
        + b" 1 1 m 2 2 l S"
    )
    pdf = _one_page(content)
    ref = sheet_reader.sheet_refusal(sheet_reader.read_sheet(pdf))
    assert ref is not None and ref.feature == "non-finite coordinate"

    monkeypatch.setattr(sheet_interpreter, "_is_finite_point", lambda p: True)
    assert isinstance(sheet_reader.read_sheet(pdf), SheetDocument)
