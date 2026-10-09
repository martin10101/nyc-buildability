"""Acceptance + mutation tests for the M5-T118 P3 reader features (D-087 PDF-3):

* AS-1 (DB-055 c) per-PAGE operator / path-point / decoded-byte budgets under a bounded
  per-DOCUMENT ceiling: a multi-page fixture whose SUM exceeds the per-page cap now reads (the
  pre-M5-T118 single per-document budget refused it); a page over its budget and a document over
  its ceiling are DISTINCT typed refusals; each per-page reset is load-bearing.
* AS-2 (ISO 32000-1 §8.7.4.2) the ``sh`` shading operator is SKIPPED as non-geometry with a
  disclosed count, never a refusal; removing it from the skip set reddens.
* AS-3 (§8.9.7) inline images (``BI``/``ID``/``EI``) are skipped WITHOUT desynchronizing the
  stream — a determinable-length image and a scanned-length image both skip and the linework after
  them still draws; a length mismatch and an over-scan-cap image are typed refusals; the skip and
  its end-offset are load-bearing (a desync mutant fails safe to a refusal, never a wrong drawing).

Each new guard has a committed consuming-namespace mutation (a ``monkeypatch`` installing a weaker
behavior that flips the assertion); the explicit red/green mutant runs are recorded in
project-control/reports/M5-T118-producer-report.md. Synthetic fixtures only; no network.
"""

from __future__ import annotations

import pytest

from app.drawings import sheet_interpreter, sheet_objects, sheet_reader
from app.drawings.sheet_inline_image import InlineImageSpan
from app.drawings.sheet_primitives import SheetDocument, SheetRefusal
from app.drawings.sheet_reader import read_sheet, sheet_refusal


# --------------------------------------------------------------------------- PDF byte builders
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


def _one_page(content: bytes, *, resources: bytes = b"") -> bytes:
    res = b" /Resources %s" % resources if resources else b""
    return _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600]%s /Contents 4 0 R >>" % res,
        _stream(content),
    ])


def _multi_page(contents: list[bytes]) -> bytes:
    """A classic-xref PDF with one leaf page per element of ``contents`` (page objects at 3, 5,
    7, ... and their content streams at 4, 6, 8, ...)."""
    n = len(contents)
    kids = b" ".join(b"%d 0 R" % (3 + 2 * i) for i in range(n))
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [%s] /Count %d >>" % (kids, n),
    ]
    for i, content in enumerate(contents):
        objects.append(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents %d 0 R >>"
            % (4 + 2 * i)
        )
        objects.append(_stream(content))
    return _pdf(objects)


def _flat(points) -> list[float]:
    return [coord for point in points for coord in point]


# ============================================================ AS-1 per-page budgets + ceilings
def test_as1_multipage_reads_under_per_page_budget(monkeypatch):
    """The per-PAGE operator budget (lowered to 5) lets a 2-page doc whose per-page count is 3
    read, even though the document SUM (6) exceeds that per-page number — the pre-M5-T118 single
    per-DOCUMENT operator budget would have refused on the sum (DB-055 c)."""
    monkeypatch.setattr(sheet_reader, "MAX_CONTENT_OPERATORS", 5)
    pdf = _multi_page([b"0 0 m 1 1 l S", b"2 2 m 3 3 l S"])  # 3 operators (m,l,S) per page
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)
    assert len(doc.pages) == 2
    assert len(doc.pages[0].polylines) == 1 and len(doc.pages[1].polylines) == 1


def test_as1_per_page_operator_reset_is_load_bearing(monkeypatch):
    """REAL: the per-page reset lets the 2-page doc read. MUTANT: begin_page no longer resets, so
    operators accumulate across pages and the second page trips the per-page operator budget."""
    monkeypatch.setattr(sheet_reader, "MAX_CONTENT_OPERATORS", 5)
    pdf = _multi_page([b"0 0 m 1 1 l S", b"2 2 m 3 3 l S"])
    assert isinstance(read_sheet(pdf), SheetDocument)
    monkeypatch.setattr(sheet_reader._SheetInterpreter, "begin_page", lambda self: None)
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "operator count"


def test_as1_over_budget_page_operators_refuses(monkeypatch):
    """A single page over the per-page operator budget is a typed 'operator count' refusal; raising
    the cap (a consuming-namespace mutation) lets the same page read."""
    monkeypatch.setattr(sheet_reader, "MAX_CONTENT_OPERATORS", 2)
    ref = sheet_refusal(read_sheet(_one_page(b"0 0 m 1 1 l S")))  # 3 operators > 2
    assert ref is not None and ref.feature == "operator count"
    assert "over 2 operators" in ref.detail
    monkeypatch.setattr(sheet_reader, "MAX_CONTENT_OPERATORS", 100)
    assert isinstance(read_sheet(_one_page(b"0 0 m 1 1 l S")), SheetDocument)


def test_as1_document_operator_ceiling_refuses(monkeypatch):
    """With the per-page cap high and the document ceiling lowered below the multi-page SUM, the
    refusal is the DISTINCT 'operator ceiling' feature; raising the ceiling lets it read."""
    monkeypatch.setattr(sheet_reader, "MAX_CONTENT_OPERATORS", 1000)   # per page, not hit
    monkeypatch.setattr(sheet_reader, "MAX_DOCUMENT_OPERATORS", 5)     # doc ceiling, hit on page 2
    pdf = _multi_page([b"0 0 m 1 1 l S", b"2 2 m 3 3 l S"])            # 3 + 3 = 6 operators
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "operator ceiling"
    assert "across the document" in ref.detail
    monkeypatch.setattr(sheet_reader, "MAX_DOCUMENT_OPERATORS", 20_000_000)
    assert isinstance(read_sheet(pdf), SheetDocument)


def test_as1_over_budget_page_points_refuses(monkeypatch):
    """A single page over the per-page path-point budget is a typed 'path points' refusal; raising
    the cap lets it read."""
    content = b"0 0 m 1 1 l 2 2 l 3 3 l S"  # 3 line points
    monkeypatch.setattr(sheet_reader, "MAX_PATH_POINTS", 2)
    ref = sheet_refusal(read_sheet(_one_page(content)))
    assert ref is not None and ref.feature == "path points"
    assert "over 2 flattened points" in ref.detail
    monkeypatch.setattr(sheet_reader, "MAX_PATH_POINTS", 100)
    assert isinstance(read_sheet(_one_page(content)), SheetDocument)


def test_as1_document_point_ceiling_refuses(monkeypatch):
    """With the per-page point cap high and the document point ceiling below the SUM, the refusal
    is the DISTINCT 'path point ceiling' feature."""
    monkeypatch.setattr(sheet_reader, "MAX_PATH_POINTS", 1000)          # per page, not hit
    monkeypatch.setattr(sheet_reader, "MAX_DOCUMENT_PATH_POINTS", 3)    # doc ceiling
    pdf = _multi_page([b"0 0 m 1 1 l 2 2 l S", b"0 0 m 1 1 l 2 2 l S"])  # 2 pts/page, 4 total
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "path point ceiling"
    assert "across the document" in ref.detail


def test_as1_over_budget_page_decoded_bytes_refuses(monkeypatch):
    """A single page whose decoded content exceeds the per-page decoded-byte budget is a typed
    'page decoded bytes' refusal; raising the cap lets it read."""
    content = b"0 0 m 10 10 l S"  # > 4 bytes decoded
    monkeypatch.setattr(sheet_reader, "MAX_PAGE_DECODED_BYTES", 4)
    ref = sheet_refusal(read_sheet(_one_page(content)))
    assert ref is not None and ref.feature == "page decoded bytes"
    monkeypatch.setattr(sheet_reader, "MAX_PAGE_DECODED_BYTES", 1_000_000)
    assert isinstance(read_sheet(_one_page(content)), SheetDocument)


def test_as1_page_decoded_bytes_reset_is_load_bearing(monkeypatch):
    """REAL: the per-page decoded budget (20) resets per page, so a 2-page doc of 13-byte pages
    reads even though the sum (26) exceeds 20. MUTANT: the decoder's begin_page no longer resets,
    so page 2 accumulates to 26 and trips the per-page decoded budget."""
    monkeypatch.setattr(sheet_reader, "MAX_PAGE_DECODED_BYTES", 20)
    pdf = _multi_page([b"5 7 m 9 3 l S", b"5 7 m 9 3 l S"])  # 13 raw bytes each
    assert isinstance(read_sheet(pdf), SheetDocument)
    monkeypatch.setattr(sheet_objects._StreamDecoder, "begin_page", lambda self: None)
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "page decoded bytes"


# ================================================================================ AS-2 shading
def test_as2_sh_skipped_with_count():
    """`sh` (§8.7.4.2) paints a colour shading, not linework: it is skipped with a disclosed count
    and the surrounding geometry still draws."""
    doc = read_sheet(_one_page(b"0 0 m 10 10 l S /Sh0 sh 20 20 m 30 30 l S"))
    assert isinstance(doc, SheetDocument)
    assert len(doc.pages[0].polylines) == 2       # both lines draw; the shading paints nothing
    assert doc.pages[0].shading_skips == 1
    assert doc.shading_skips == 1


def test_as2_two_sh_counted():
    doc = read_sheet(_one_page(b"/Sh0 sh /Sh1 sh 0 0 m 1 1 l S"))
    assert isinstance(doc, SheetDocument)
    assert doc.pages[0].shading_skips == 2 and len(doc.pages[0].polylines) == 1


def test_as2_sh_skip_is_load_bearing(monkeypatch):
    """REAL: `sh` is skipped -> the document reads. MUTANT: `sh` removed from the skip set falls
    through to the unsupported-operator refusal (proving the skip, not a no-op, accepts it)."""
    pdf = _one_page(b"0 0 m 10 10 l S /Sh0 sh")
    assert isinstance(read_sheet(pdf), SheetDocument)
    monkeypatch.setattr(sheet_interpreter, "_SKIP_SHADING", frozenset())
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "unsupported operator"


# =========================================================================== AS-3 inline images
def _inline(dict_part: bytes, data: bytes) -> bytes:
    """A ``BI <dict> ID <data> EI`` inline image (a single whitespace after ID per §8.9.7)."""
    return b"BI " + dict_part + b" ID " + data + b" EI"


def test_as3_inline_image_determinable_length_skipped_line_after_draws():
    """An UNFILTERED inline image with known geometry (2x2, DeviceGray, 8bpc -> 4 data bytes) is
    skipped by computed length; the line AFTER it still draws (no desync)."""
    img = _inline(b"/W 2 /H 2 /CS /G /BPC 8", bytes([1, 2, 3, 4]))
    doc = read_sheet(_one_page(b"q " + img + b" Q 0 0 m 10 10 l S"))
    assert isinstance(doc, SheetDocument)
    assert doc.pages[0].inline_image_skips == 1
    assert doc.inline_image_skips == 1
    assert len(doc.pages[0].polylines) == 1
    assert _flat(doc.pages[0].polylines[0].points) == pytest.approx([0.0, 0.0, 10.0, 10.0])


def test_as3_inline_image_image_mask_determinable():
    """An image mask (/IM true) is 1 component at 1 bit: 8x1 -> ceil(8*1*1/8)=1 byte -> skipped."""
    img = _inline(b"/W 8 /H 1 /IM true", bytes([0xAB]))
    doc = read_sheet(_one_page(img + b" 0 0 m 1 1 l S"))
    assert isinstance(doc, SheetDocument)
    assert doc.pages[0].inline_image_skips == 1 and len(doc.pages[0].polylines) == 1


def test_as3_inline_image_scanned_length_skipped():
    """A FILTERED inline image (/F /Fl) has no computable length, so the reader scans for a
    whitespace-delimited EI under the byte cap; the line after still draws."""
    img = _inline(b"/W 2 /H 2 /CS /G /F /Fl", bytes([0x9C, 0x01, 0x02]))
    doc = read_sheet(_one_page(b"q " + img + b" Q 5 5 m 6 6 l S"))
    assert isinstance(doc, SheetDocument)
    assert doc.pages[0].inline_image_skips == 1
    assert len(doc.pages[0].polylines) == 1
    assert _flat(doc.pages[0].polylines[0].points) == pytest.approx([5.0, 5.0, 6.0, 6.0])


def test_as3_inline_image_array_filter_value_scanned():
    """An array-valued /Filter (Table 93 abbreviations) is parsed for balance and forces the EI
    scan (a filter is present); the image is skipped and the line after draws."""
    img = _inline(b"/W 2 /H 2 /CS /G /F [/Fl]", bytes([0x9C, 0x01]))
    doc = read_sheet(_one_page(img + b" 0 0 m 1 1 l S"))
    assert isinstance(doc, SheetDocument)
    assert doc.pages[0].inline_image_skips == 1 and len(doc.pages[0].polylines) == 1


def test_as3_inline_image_length_mismatch_refuses():
    """A determinable length (4 bytes) that does NOT land on a whitespace-delimited EI is a typed
    refusal — the reader never guesses past a desync."""
    img = _inline(b"/W 2 /H 2 /CS /G /BPC 8", bytes([1, 2]) + b" EI 0 0 m 1 1 l S")
    ref = sheet_refusal(read_sheet(_one_page(b"q " + img + b" Q")))
    assert ref is not None and ref.feature == "inline image"


def test_as3_inline_image_over_scan_cap_refuses(monkeypatch):
    """A filtered inline image whose data exceeds the (lowered) scan cap before any EI is a typed
    refusal, never an unbounded scan."""
    monkeypatch.setattr(sheet_reader, "MAX_INLINE_IMAGE_DATA_BYTES", 4)
    img = _inline(b"/W 2 /H 2 /CS /G /F /Fl", bytes([1, 2, 3, 4, 5, 6, 7, 8]))
    ref = sheet_refusal(read_sheet(_one_page(b"q " + img + b" Q")))
    assert ref is not None and ref.feature == "inline image"


def test_as3_inline_image_no_id_marker_refuses():
    """A ``BI`` with no ``ID`` before the stream ends is a typed refusal (never a runaway scan)."""
    ref = sheet_refusal(read_sheet(_one_page(b"BI /W 2 /H 2 /CS /G /BPC 8")))
    assert ref is not None and ref.feature == "inline image"


def test_as3_inline_image_skip_is_load_bearing(monkeypatch):
    """REAL: the inline image is skipped and the document reads. MUTANT: skip_inline_image refuses
    every inline image -> the whole document refuses (the pre-M5-T118 DB-055 d behaviour)."""
    img = _inline(b"/W 2 /H 2 /CS /G /BPC 8", bytes([1, 2, 3, 4]))
    pdf = _one_page(b"q " + img + b" Q 0 0 m 10 10 l S")
    assert isinstance(read_sheet(pdf), SheetDocument)

    def _refuse_bi(data, start, *, max_dict_bytes, max_data_scan_bytes):
        return sheet_objects._refuse("inline image", "mutant refuses inline images")

    monkeypatch.setattr(sheet_interpreter, "skip_inline_image", _refuse_bi)
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "inline image"


def test_as3_inline_image_end_offset_desync_fails_safe(monkeypatch):
    """REAL: the correct end offset resumes past EI so the line after draws exactly. MUTANT: a skip
    that under-consumes (resumes at the dictionary) desynchronizes, so the sample bytes are
    mis-lexed into a REFUSAL — never a silently wrong drawing."""
    img = _inline(b"/W 2 /H 2 /CS /G /BPC 8", bytes([1, 2, 3, 4]))
    pdf = _one_page(b"q " + img + b" Q 0 0 m 10 10 l S")
    real = read_sheet(pdf)
    assert isinstance(real, SheetDocument)
    assert _flat(real.pages[0].polylines[0].points) == pytest.approx([0.0, 0.0, 10.0, 10.0])

    real_skip = sheet_interpreter.skip_inline_image

    def _short(data, start, *, max_dict_bytes, max_data_scan_bytes):
        span = real_skip(
            data, start, max_dict_bytes=max_dict_bytes, max_data_scan_bytes=max_data_scan_bytes
        )
        if isinstance(span, InlineImageSpan):
            return InlineImageSpan(start, span.determinable, span.data_length)  # under-consume
        return span

    monkeypatch.setattr(sheet_interpreter, "skip_inline_image", _short)
    assert isinstance(read_sheet(pdf), SheetRefusal)
