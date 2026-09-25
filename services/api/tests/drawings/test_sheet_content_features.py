"""Acceptance + mutation tests for the M5-T113 content-stream features (D-087 PDF-2):

* AS-1 (DB-076 a) content/form ``/FlateDecode`` streams with a ``/DecodeParms`` §7.4.4.4 PNG
  predictor (10-15) decode through the REUSED bounded :func:`apply_predictor` and draw; the TIFF
  predictor (2), a predictor without a filter, and out-of-range predictors are typed refusals.
* AS-2 (DB-076 b) ``BDC`` / ``DP`` accept an inline ``<< >>`` marked-content property list
  (§14.6), balanced and depth/length-bounded, drawing nothing themselves; ``BMC`` / ``EMC`` and a
  NAME property-list operand keep working; a single ``<`` hex-string operand still lexes; an
  unbalanced / too-deep / too-long list is a typed refusal.
* AS-3 (DB-076 c, e) the scan-only refusal is REACHABLE through marked content on a resolver-path
  file with no vector geometry; the gate is load-bearing; the two DB-076 (e) inconsistencies are
  DISCLOSED by characterization tests (the label also fires on text-only; image-only succeeds on
  the classic path but refuses on the resolver path) — see the M5-T113 producer report.

Each new guard has a committed consuming-namespace mutation (a ``monkeypatch`` that installs a
weaker behavior and proves the assertion flips); the explicit red/green mutant runs are recorded
in project-control/reports/M5-T113-producer-report.md. Synthetic fixtures only; no network.
"""

from __future__ import annotations

import zlib

import pytest

from app.drawings import sheet_interpreter, sheet_objects, sheet_reader
from app.drawings.sheet_primitives import SheetDocument, SheetImage, SheetRefusal
from app.drawings.sheet_reader import read_sheet, sheet_refusal


# --------------------------------------------------------------------------- classic builders
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
    extra_objects: tuple[bytes, ...] = (),
) -> bytes:
    res = b" /Resources %s" % resources if resources else b""
    page = (
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600]%s /Contents 4 0 R >>" % res
    )
    return _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        page,
        _stream(content),
        *extra_objects,
    ])


def _page_with_content_obj(content_obj: bytes, *, resources: bytes = b"") -> bytes:
    """A one-page PDF whose /Contents object 4 is the PRE-BUILT ``content_obj`` stream (with its
    own /Filter/DecodeParms), rather than a raw content string wrapped by :func:`_one_page`."""
    res = b" /Resources %s" % resources if resources else b""
    return _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600]%s /Contents 4 0 R >>" % res,
        content_obj,
    ])


def _flat(points) -> list[float]:
    return [coord for point in points for coord in point]


# ------------------------------------------------------------------- PNG predictor encoding
def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def _png_encode(raw: bytes, row_len: int, tag: int, bpp: int = 1) -> bytes:
    """Forward-filter every ``row_len``-byte row with ``tag`` (0=None 1=Sub 2=Up 3=Average
    4=Paeth) and prepend the per-row filter tag byte, so the reader's PNG unfilter must reverse
    it (identical construction to the resolver's own predictor corpus)."""
    out = bytearray()
    previous = bytes(row_len)
    for start in range(0, len(raw), row_len):
        row = raw[start : start + row_len]
        out.append(tag)
        enc = bytearray(row_len)
        for i in range(row_len):
            left = row[i - bpp] if i >= bpp else 0
            up = previous[i]
            upper_left = previous[i - bpp] if i >= bpp else 0
            if tag == 0:
                enc[i] = row[i]
            elif tag == 1:
                enc[i] = (row[i] - left) & 0xFF
            elif tag == 2:
                enc[i] = (row[i] - up) & 0xFF
            elif tag == 3:
                enc[i] = (row[i] - ((left + up) >> 1)) & 0xFF
            else:
                enc[i] = (row[i] - _paeth(left, up, upper_left)) & 0xFF
        out += enc
        previous = row
    return bytes(out)


def _flate_png_content(content: bytes, columns: int, tag: int, predictor: int = 12) -> bytes:
    comp = zlib.compress(_png_encode(content, columns, tag))
    extra = (
        b" /Filter /FlateDecode /DecodeParms << /Predictor %d /Columns %d >>"
        % (predictor, columns)
    )
    return _stream(comp, extra)


# ------------------------------------------------------------------ resolver-path builder
def _be(value: int, width: int) -> bytes:
    return value.to_bytes(width, "big")


def _xref_stream_pdf(
    content: bytes, *, resources: bytes = b"", extra_objects: tuple[bytes, ...] = ()
) -> bytes:
    """A minimal PDF 1.5+ file read through the NEW resolver path (``used_resolver`` True):
    objects 1-4 (+ any extra) uncompressed type-1, plus a FlateDecode ``/XRef`` cross-reference
    stream as the last object. ``extra_objects`` are numbered from 5, the xref stream last."""
    res = b" /Resources %s" % resources if resources else b""
    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600]%s /Contents 4 0 R >>" % res,
        4: b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content), content),
    }
    for i, body in enumerate(extra_objects, start=5):
        objects[i] = body
    xref_num = 5 + len(extra_objects)
    size = xref_num + 1
    body = bytearray(b"%PDF-1.5\n")
    offsets: dict[int, int] = {}
    for num in range(1, xref_num):
        offsets[num] = len(body)
        body += b"%d 0 obj\n%s\nendobj\n" % (num, objects[num])
    xref_offset = len(body)
    entries: dict[int, tuple[int, int, int]] = {0: (0, 0, 0), xref_num: (1, xref_offset, 0)}
    for num in range(1, xref_num):
        entries[num] = (1, offsets[num], 0)
    raw = bytearray()
    for onum in range(size):
        entry_type, field2, field3 = entries.get(onum, (0, 0, 0))
        raw += _be(entry_type, 1) + _be(field2, 4) + _be(field3, 2)
    comp = zlib.compress(bytes(raw))
    dictionary = (
        b"<< /Type /XRef /Size %d /W [1 4 2] /Root 1 0 R /Length %d /Filter /FlateDecode >>"
        % (size, len(comp))
    )
    body += b"%d 0 obj\n%s\nstream\n%s\nendstream\nendobj\n" % (xref_num, dictionary, comp)
    body += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(body)


_IMAGE_OBJ = _stream(
    b"\xff\xd8\xff\xe0not-a-real-jpeg",
    b" /Type /XObject /Subtype /Image /Width 8 /Height 6"
    b" /BitsPerComponent 8 /ColorSpace /DeviceRGB /Filter /DCTDecode",
)
_IMAGE_CONTENT = b"q 50 0 0 40 10 20 cm /Im0 Do Q"
_IMAGE_RES = b"<< /XObject << /Im0 5 0 R >> >>"


# ===================================================================== AS-1 predictor streams
@pytest.mark.parametrize("tag", [0, 1, 2, 3, 4])
def test_as1_png_predictor_content_stream_draws(tag):
    """A content stream with /FlateDecode + a §7.4.4.4 PNG predictor (each row filter) decodes
    through the reused apply_predictor and draws the line (0,0)->(10,0)."""
    pdf = _page_with_content_obj(_flate_png_content(b"0 0 m 10 0 l S", columns=7, tag=tag))
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument), tag
    assert _flat(doc.pages[0].polylines[0].points) == pytest.approx([0.0, 0.0, 10.0, 0.0]), tag


def test_as1_predictor_none_passthrough_draws():
    # /Predictor 1 (none) returns the inflated bytes unchanged -> draws.
    pdf = _page_with_content_obj(_flate(b"5 7 m 9 3 l S", b" /DecodeParms << /Predictor 1 >>"))
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)
    assert _flat(doc.pages[0].polylines[0].points) == pytest.approx([5.0, 7.0, 9.0, 3.0])


def test_as1_tiff_predictor_content_stream_refuses():
    obj = _flate(b"5 7 m 9 3 l S", b" /DecodeParms << /Predictor 2 /Columns 13 >>")
    ref = sheet_refusal(read_sheet(_page_with_content_obj(obj)))
    assert ref is not None and ref.feature == "predictor"
    assert "TIFF" in ref.detail


def test_as1_out_of_range_predictor_refuses():
    obj = _flate(b"5 7 m 9 3 l S", b" /DecodeParms << /Predictor 16 /Columns 13 >>")
    ref = sheet_refusal(read_sheet(_page_with_content_obj(obj)))
    assert ref is not None and ref.feature == "predictor"


def test_as1_decode_parms_without_filter_refuses():
    # /DecodeParms is meaningless without a /FlateDecode filter -> typed refusal (never a raw read).
    pdf = _page_with_content_obj(_stream(b"5 7 m 9 3 l S", b" /DecodeParms << /Predictor 12 >>"))
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "decode parameters"


def test_as1_decode_parms_non_dictionary_refuses():
    pdf = _page_with_content_obj(_flate(b"5 7 m 9 3 l S", b" /DecodeParms 5"))
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "decode parameters"


def test_as1_predictor_stream_shares_the_document_decoded_budget(monkeypatch):
    # The inflated bytes are charged against the document-wide budget BEFORE the predictor runs.
    monkeypatch.setattr(sheet_reader, "MAX_TOTAL_DECODED_BYTES", 4)
    pdf = _page_with_content_obj(_flate_png_content(b"0 0 m 10 0 l S", 7, 2))
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "decoded bytes budget"


def test_as1_predictor_acceptance_is_load_bearing(monkeypatch):
    """REAL: the predictor content stream draws. MUTANT: apply_predictor refuses (the
    pre-M5-T113 '/DecodeParms unsupported' behavior) -> the SAME stream now refuses."""
    pdf = _page_with_content_obj(_flate_png_content(b"0 0 m 10 0 l S", columns=7, tag=2))
    assert isinstance(read_sheet(pdf), SheetDocument)

    def _refuse_predictor(data, parms, *, absolute_cap):
        return sheet_objects._refuse("decode parameters", "mutant: /DecodeParms unsupported")

    monkeypatch.setattr(sheet_objects, "apply_predictor", _refuse_predictor)
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "decode parameters"


# ======================================================================= AS-2 marked content
def test_as2_bdc_inline_dict_draws_geometry_inside():
    pdf = _one_page(b"/OC << /MCID 0 >> BDC 5 7 m 9 3 l S EMC")
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)
    assert _flat(doc.pages[0].polylines[0].points) == pytest.approx([5.0, 7.0, 9.0, 3.0])


def test_as2_dp_inline_dict_draws_and_points_nothing():
    # DP (marked-content point with a property list) consumes its inline dict and paints nothing;
    # the surrounding geometry still draws.
    pdf = _one_page(b"0 0 m 10 10 l S /P << /MCID 1 /Metadata (x) >> DP")
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)
    assert len(doc.pages[0].polylines) == 1
    assert _flat(doc.pages[0].polylines[0].points) == pytest.approx([0.0, 0.0, 10.0, 10.0])


def test_as2_nested_inline_dict_and_array_draws():
    pdf = _one_page(b"/OC << /A << /B [1 2 (s) <4A>] >> /C true >> BDC 5 7 m 9 3 l S EMC")
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)
    assert _flat(doc.pages[0].polylines[0].points) == pytest.approx([5.0, 7.0, 9.0, 3.0])


def test_as2_bmc_and_name_property_list_still_work():
    # BMC (no property list) and BDC with a NAME property-list operand both keep working.
    pdf = _one_page(b"/Span BMC 0 0 m 1 1 l S EMC /OC /MC0 BDC 2 2 m 3 3 l S EMC")
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)
    assert len(doc.pages[0].polylines) == 2


def test_as2_hex_string_operand_still_lexes():
    # A single '<' (a hex-string operand) must NOT be swallowed by the '<<' marked-content path.
    pdf = _one_page(b"BT /F1 12 Tf 10 20 Td <48656C6C6F> Tj ET",
                    resources=b"<< /Font << /F1 << >> >> >>")
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)
    assert doc.pages[0].text_runs[0].text == "Hello"


def test_as2_unbalanced_inline_dict_refuses():
    pdf = _one_page(b"/OC << /MCID 0 BDC 5 7 m 9 3 l S EMC")  # the '<<' is never closed
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "marked-content dictionary"


def test_as2_inline_dict_wrong_position_is_refused():
    # A property list that is not consumed by BDC/DP is a typed dangling-operand refusal, never a
    # silent success.
    pdf = _one_page(b"<< /K 1 >> f")
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "dangling operands"


def test_as2_inline_dict_acceptance_is_load_bearing(monkeypatch):
    """REAL: BDC with an inline dict draws. MUTANT: read_inline_dict refuses every inline dict
    -> the SAME stream refuses 'marked-content dictionary'."""
    pdf = _one_page(b"/OC << /MCID 0 >> BDC 5 7 m 9 3 l S EMC")
    assert isinstance(read_sheet(pdf), SheetDocument)

    def _refuse_dicts(data, start, *, max_depth, max_bytes):
        return sheet_objects._refuse("marked-content dictionary", "mutant refuses inline dicts")

    monkeypatch.setattr(sheet_interpreter, "read_inline_dict", _refuse_dicts)
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "marked-content dictionary"


def test_as2_depth_cap_is_load_bearing(monkeypatch):
    """REAL: a depth-2 nested property list draws under the default cap. MUTANT: the cap lowered
    to 1 makes it refuse -> the depth guard has teeth."""
    pdf = _one_page(b"/OC << /A << /B 1 >> >> BDC 5 7 m 9 3 l S EMC")
    assert isinstance(read_sheet(pdf), SheetDocument)
    monkeypatch.setattr(sheet_reader, "MAX_MARKED_CONTENT_DEPTH", 1)
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "marked-content dictionary"
    assert "depth" in ref.detail


def test_as2_byte_cap_is_load_bearing(monkeypatch):
    """REAL: a small property list draws under the default byte cap. MUTANT: the cap lowered to 4
    bytes makes it refuse -> the length guard has teeth."""
    pdf = _one_page(b"/OC << /MCID 0 >> BDC 5 7 m 9 3 l S EMC")
    assert isinstance(read_sheet(pdf), SheetDocument)
    monkeypatch.setattr(sheet_reader, "MAX_MARKED_CONTENT_BYTES", 4)
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "marked-content dictionary"
    assert "bytes" in ref.detail


# ============================================================ AS-3 scan-only (reachable + honest)
def test_as3_marked_content_with_geometry_draws_on_resolver_path():
    # Proof that (b) lets a marked-content page PARSE on the resolver path instead of refusing at
    # its '<<': the geometry inside the marked-content sequence draws.
    doc = read_sheet(_xref_stream_pdf(b"/OC << /MCID 0 >> BDC 10 10 m 100 100 l S EMC"))
    assert isinstance(doc, SheetDocument)
    assert _flat(doc.pages[0].polylines[0].points) == pytest.approx([10.0, 10.0, 100.0, 100.0])


def test_as3_scan_only_reachable_through_marked_content():
    # The same marked-content wrapper with NO vector geometry now REACHES the scan-only gate
    # (before (b) it refused at '<<'); a resolver-path page with zero linework is scan-only.
    ref = sheet_refusal(read_sheet(_xref_stream_pdf(b"/OC << /MCID 0 >> BDC EMC")))
    assert ref is not None
    assert ref.feature == "scan only"
    assert ref.origin == SheetRefusal.SHEET_PROFILE


def test_as3_scan_only_gate_is_load_bearing(monkeypatch):
    """REAL: a zero-geometry resolver page refuses 'scan only'. MUTANT: defeating the gate lets it
    'succeed' with an empty page set -> the gate is load-bearing (DB-076 c)."""
    pdf = _xref_stream_pdf(b"/OC << /MCID 0 >> BDC EMC")
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "scan only"
    monkeypatch.setattr(sheet_reader, "_scan_only_refusal", lambda pages, *, used_resolver: None)
    assert isinstance(read_sheet(pdf), SheetDocument)


def test_as3_scan_only_reaches_a_real_raster_page():
    # A resolver-path page whose only content is an image XObject (a scan) refuses 'scan only'.
    pdf = _xref_stream_pdf(_IMAGE_CONTENT, resources=_IMAGE_RES, extra_objects=(_IMAGE_OBJ,))
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "scan only"


# --- DB-076 (e) DISCLOSED inconsistencies (characterization; see the M5-T113 producer report) ---
def test_disclosed_scan_only_label_also_fires_on_text_only():
    # DB-076 (e) #1: the "scan only" LABEL also fires on a text-only resolver page. The feature is
    # pinned to "scan only" by the read-only test_pdf_object_streams suite, so this packet
    # DISCLOSES rather than relabels; the refusal detail names the text-only case honestly.
    ref = sheet_refusal(read_sheet(_xref_stream_pdf(b"BT /F0 12 Tf (label) Tj ET")))
    assert ref is not None and ref.feature == "scan only"
    assert "text-only" in ref.detail


def test_disclosed_image_only_classic_succeeds_but_resolver_refuses():
    # DB-076 (e) #2: an image-only page SUCCEEDS on the classic path (the gate is resolver-scoped)
    # but REFUSES on the resolver path. Disclosed, not fixed: real corpus files are all PDF 1.5+
    # (resolver path), so the asymmetry never affects them (see the producer report).
    classic_pdf = _one_page(_IMAGE_CONTENT, resources=_IMAGE_RES, extra_objects=(_IMAGE_OBJ,))
    classic = read_sheet(classic_pdf)
    assert isinstance(classic, SheetDocument)
    assert classic.pages[0].image_count == 1
    assert isinstance(classic.pages[0].images[0], SheetImage)
    assert classic.pages[0].polylines == ()

    resolver_pdf = _xref_stream_pdf(
        _IMAGE_CONTENT, resources=_IMAGE_RES, extra_objects=(_IMAGE_OBJ,)
    )
    resolver = sheet_refusal(read_sheet(resolver_pdf))
    assert resolver is not None and resolver.feature == "scan only"
