"""Acceptance + mutation tests for the PDF 1.5+ cross-reference-stream / object-stream
resolver (M5-T103, D-087 PKT-K / C1).

Synthetic PDF 1.5+ files are assembled byte-by-byte with real cross-reference-stream and
object-stream structures (``/Type /XRef`` with ``/W`` field widths and ``/Index``
subsections; ``/Type /ObjStm`` with ``/N`` / ``/First``), mirroring the shapes verified
against the real corpus in ``docs/research/architect-corpus-reader-trial-2026-09.md``.
Coverage maps to the packet's acceptance scenarios:

* AS-1 resolver     -> entry types 0/1/2, multiple /Index subsections, a /Prev chain (and a
                       /Prev cycle refused), a hybrid /XRefStm file, an object stream holding
                       several objects, and each PNG predictor row filter; a classic-xref
                       file still takes the old path; unsupported features are typed refusals.
* AS-2 guard        -> the absolute inflated-bytes cap, the inflate-ratio guard, the shared
                       document budget, and the /Prev-depth, object-stream-count and /N
                       bounds each redden under an in-process mutation; a zip bomb refuses
                       with bounded memory.
* AS-3 hygiene      -> XObject /name and unsupported-/Filter echoes are _preview-truncated;
                       a resolved page with zero vector geometry is a typed scan-only refusal.
* AS-4/5/6          -> the existing sheet-reader suites (unchanged), the real-corpus run, and
                       the scope/dependency proof live in the producer report.
"""

from __future__ import annotations

import tracemalloc
import zlib

import pytest

from app.drawings import pdf_object_streams, sheet_objects, sheet_reader
from app.drawings.sheet_primitives import SheetDocument, SheetRefusal
from app.drawings.sheet_reader import read_sheet, sheet_refusal

_LINE = b"10 10 m 100 100 l S"  # one stroked polyline
_LINE_V2 = b"50 50 m 60 60 l S"  # a different one stroked polyline (for /Prev override)


# ------------------------------------------------------------------- byte-level builders
def _be(value: int, width: int) -> bytes:
    return value.to_bytes(width, "big")


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def _png_encode(raw: bytes, row_len: int, tag: int, bpp: int = 1) -> bytes:
    """Forward-filter every row with ``tag`` (0=None 1=Sub 2=Up 3=Average 4=Paeth) so the
    resolver's PNG unfilter must reverse it; prepend the per-row filter tag byte."""
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


def _objstm_blob(num: int, members: list[tuple[int, bytes]]) -> bytes:
    payload = bytearray()
    offsets: list[tuple[int, int]] = []
    for onum, body in members:
        offsets.append((onum, len(payload)))
        payload += body + b" "
    header = b"".join(b"%d %d " % (onum, off) for onum, off in offsets)
    first = len(header)
    comp = zlib.compress(header + bytes(payload))
    dictionary = (
        b"<< /Type /ObjStm /N %d /First %d /Length %d /Filter /FlateDecode >>"
        % (len(members), first, len(comp))
    )
    return b"%d 0 obj\n%s\nstream\n%s\nendstream\nendobj\n" % (num, dictionary, comp)


def _xref_stream_blob(
    num: int,
    size: int,
    entries: dict[int, tuple[int, int, int]],
    widths: tuple[int, int, int],
    row_tag: int | None,
    index: list[int] | None,
    extra: bytes,
) -> bytes:
    w0, w1, w2 = widths
    raw = bytearray()
    order = range(size) if index is None else _index_order(index)
    for onum in order:
        entry_type, field2, field3 = entries.get(onum, (0, 0, 0))
        raw += _be(entry_type, w0) + _be(field2, w1) + _be(field3, w2)
    payload = bytes(raw)
    parms = b""
    if row_tag is not None:
        payload = _png_encode(payload, w0 + w1 + w2, row_tag)
        parms = b" /DecodeParms << /Predictor 12 /Columns %d >>" % (w0 + w1 + w2)
    index_kv = b"" if index is None else b" /Index [%s]" % b" ".join(b"%d" % v for v in index)
    comp = zlib.compress(payload)
    dictionary = (
        b"<< /Type /XRef /Size %d /W [%d %d %d] /Root 1 0 R /Length %d /Filter /FlateDecode"
        b"%s%s%s >>" % (size, w0, w1, w2, len(comp), parms, index_kv, extra)
    )
    return b"%d 0 obj\n%s\nstream\n%s\nendstream\nendobj\n" % (num, dictionary, comp)


def _index_order(index: list[int]) -> list[int]:
    order: list[int] = []
    for sub in range(0, len(index), 2):
        order.extend(range(index[sub], index[sub] + index[sub + 1]))
    return order


def _content_obj(num: int, content: bytes, filter_extra: bytes = b"") -> bytes:
    return b"%d 0 obj\n<< /Length %d%s >>\nstream\n%s\nendstream\nendobj\n" % (
        num,
        len(content),
        filter_extra,
        content,
    )


def _xref_pdf(
    *,
    compress: tuple[int, ...] = (),
    row_tag: int | None = None,
    widths: tuple[int, int, int] = (1, 4, 2),
    content: bytes = _LINE,
    content_filter: bytes = b"",
    catalog_extra: bytes = b"",
    page_extra: bytes = b"",
    page_resources: bytes = b"",
    index: list[int] | None = None,
    xref_extra: bytes = b"",
    header: bytes = b"%PDF-1.5\n",
) -> bytes:
    """A single-section PDF 1.5+ file. Objects 1=catalog 2=pages 3=page 4=content; those in
    ``compress`` (subset of {1,2,3}) go into ObjStm 5, the rest are uncompressed type-1."""
    base = {
        1: b"<< /Type /Catalog /Pages 2 0 R" + catalog_extra + b" >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600]"
        + page_resources
        + page_extra
        + b" /Contents 4 0 R >>",
    }
    compressed = [(n, base[n]) for n in (1, 2, 3) if n in compress]
    has_objstm = bool(compressed)
    objstm_num = 5 if has_objstm else None
    xref_num = 6 if has_objstm else 5
    size = xref_num + 1

    body = bytearray(header)
    offsets: dict[int, int] = {}
    for n in (1, 2, 3):
        if n not in compress:
            offsets[n] = len(body)
            body += b"%d 0 obj\n%s\nendobj\n" % (n, base[n])
    offsets[4] = len(body)
    body += _content_obj(4, content, content_filter)
    if has_objstm:
        offsets[objstm_num] = len(body)
        body += _objstm_blob(objstm_num, compressed)

    entries: dict[int, tuple[int, int, int]] = {0: (0, 0, 0)}
    for n in (1, 2, 3):
        if n in compress:
            entries[n] = (2, objstm_num, [c[0] for c in compressed].index(n))
        else:
            entries[n] = (1, offsets[n], 0)
    entries[4] = (1, offsets[4], 0)
    if has_objstm:
        entries[objstm_num] = (1, offsets[objstm_num], 0)
    xref_offset = len(body)
    entries[xref_num] = (1, xref_offset, 0)
    body += _xref_stream_blob(xref_num, size, entries, widths, row_tag, index, xref_extra)
    body += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(body)


def _classic_pdf(content: bytes = _LINE) -> bytes:
    """A classic-xref PDF (the OLD path): objects 1-4, a classic ``xref`` table + trailer."""
    body = bytearray(b"%PDF-1.7\n")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content), content),
    ]
    offsets = []
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body += b"%d 0 obj\n%s\nendobj\n" % (index, obj)
    xref = len(body)
    body += b"xref\n0 5\n0000000000 65535 f \n"
    for off in offsets:
        body += b"%010d 00000 n \n" % off
    body += b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % xref
    return bytes(body)


def _refusal(pdf: bytes) -> SheetRefusal | None:
    return sheet_refusal(read_sheet(pdf))


def _first_polyline_flat(doc: SheetDocument) -> list[float]:
    return [c for p in doc.pages[0].polylines[0].points for c in p]


# ================================================================================== AS-1
def test_placeholder_seed_passes():
    # Non-empty suite guard so the file never trips vitest/pytest "no tests collected".
    assert pdf_object_streams.resolve_object_table is not None


def test_reads_flate_xref_stream():
    # A FlateDecode-compressed cross-reference stream (no PNG predictor). The true no-/Filter
    # (raw) branch is covered by test_reads_raw_no_filter_xref_stream (A4).
    doc = read_sheet(_xref_pdf())
    assert isinstance(doc, SheetDocument)
    assert len(doc.pages) == 1
    assert _first_polyline_flat(doc) == pytest.approx([10.0, 10.0, 100.0, 100.0])


def test_reads_raw_no_filter_xref_stream():
    # The resolver's true no-/Filter decode branch (pdf_object_streams._decode_stream, filt is
    # None): the entry table is stored raw, never Flate-compressed.
    doc = read_sheet(_raw_xref_stream_pdf())
    assert isinstance(doc, SheetDocument)
    assert len(doc.pages) == 1
    assert _first_polyline_flat(doc) == pytest.approx([10.0, 10.0, 100.0, 100.0])


def test_reads_object_stream_entry_types_0_1_2():
    # catalog/pages/page compressed (type-2 in ObjStm) + type-1 content/objstm/xref +
    # a type-0 free object 0: exercises all three entry types through read_sheet.
    doc = read_sheet(_xref_pdf(compress=(1, 2, 3)))
    assert isinstance(doc, SheetDocument)
    assert _first_polyline_flat(doc) == pytest.approx([10.0, 10.0, 100.0, 100.0])


def test_reads_partial_object_stream():
    # only the page tree compressed; catalog stays uncompressed -> mixed type-1/type-2.
    doc = read_sheet(_xref_pdf(compress=(2, 3)))
    assert isinstance(doc, SheetDocument)
    assert len(doc.pages) == 1


def test_multiple_index_subsections():
    # /Index split into three subsections covering 0..6 -> the same object table.
    doc = read_sheet(_xref_pdf(compress=(1, 2, 3), index=[0, 1, 1, 3, 4, 3]))
    assert isinstance(doc, SheetDocument)
    assert _first_polyline_flat(doc) == pytest.approx([10.0, 10.0, 100.0, 100.0])


@pytest.mark.parametrize("tag", [0, 1, 2, 3, 4])
def test_each_png_predictor_row_filter(tag):
    doc = read_sheet(_xref_pdf(compress=(1, 2, 3), row_tag=tag))
    assert isinstance(doc, SheetDocument)
    assert _first_polyline_flat(doc) == pytest.approx([10.0, 10.0, 100.0, 100.0])


def test_narrow_field_widths_default_generation():
    # /W [1 2 1]: a narrow (2-byte) offset field and a 1-byte generation field; w0=1, so the
    # type field IS present (NOT zero-width). The true zero-width /W defaults (type field and
    # field-3) are covered by test_zero_width_type_and_field3_defaults.
    doc = read_sheet(_xref_pdf(compress=(1, 2, 3), widths=(1, 2, 1)))
    assert isinstance(doc, SheetDocument)


def test_prev_chain_newer_entry_wins():
    doc = read_sheet(_prev_pdf())
    assert isinstance(doc, SheetDocument)
    # the updated (newer) content object 4 must win over the base one.
    assert _first_polyline_flat(doc) == pytest.approx([50.0, 50.0, 60.0, 60.0])


def test_prev_cycle_is_refused():
    ref = _refusal(_cycle_pdf())
    assert ref is not None
    assert ref.feature == "xref /Prev cycle"


def test_hybrid_xrefstm_file_reads():
    doc = read_sheet(_hybrid_pdf())
    assert isinstance(doc, SheetDocument)
    assert _first_polyline_flat(doc) == pytest.approx([10.0, 10.0, 100.0, 100.0])


def test_classic_xref_still_takes_old_path():
    # A classic table reads via the strict reader; the resolver is never reached (proven by
    # patching it to explode: a classic read must not call it).
    exploded = {"called": False}

    def _boom(*a, **k):
        exploded["called"] = True
        raise AssertionError("resolver must not run for a classic-xref file")

    import app.drawings.sheet_reader as sr

    original = sr.resolve_object_table
    sr.resolve_object_table = _boom
    try:
        doc = read_sheet(_classic_pdf())
    finally:
        sr.resolve_object_table = original
    assert isinstance(doc, SheetDocument)
    assert exploded["called"] is False


def test_encryption_is_typed_refusal():
    ref = _refusal(_xref_pdf(xref_extra=b" /Encrypt 4 0 R"))
    assert ref is not None
    assert ref.feature == "encryption"


def test_unsupported_predictor_tiff_is_typed_refusal():
    # An xref stream declaring the TIFF predictor (2), which is not implemented.
    pdf = _xref_pdf_with_predictor_value(2)
    ref = _refusal(pdf)
    assert ref is not None
    assert ref.feature == "predictor"
    assert "TIFF" in ref.detail


def test_broken_type1_offset_is_typed_refusal():
    # A type-1 entry whose offset points at a DIFFERENT object's header (a lying offset): the
    # (number, generation) identity check must reject it with the specific "object identity"
    # feature, never silently accept the wrong object (G3/G4 round-1 A4/A5).
    ref = _refusal(_broken_offset_pdf())
    assert ref is not None
    assert ref.origin == SheetRefusal.SHEET_PROFILE
    assert ref.feature == "object identity"


# ================================================================================== AS-2
def test_absolute_inflated_cap_mutation_reddens(monkeypatch):
    pdf = _xref_pdf(compress=(1, 2, 3))
    assert isinstance(read_sheet(pdf), SheetDocument)  # green at the default cap
    monkeypatch.setattr(pdf_object_streams, "MAX_INFLATED_STREAM_BYTES", 4)
    ref = _refusal(pdf)
    assert ref is not None and ref.feature == "inflated bytes cap"


def test_inflate_ratio_mutation_reddens(monkeypatch):
    pdf = _xref_pdf(compress=(1, 2, 3))
    assert isinstance(read_sheet(pdf), SheetDocument)  # green at the default ratio guard
    monkeypatch.setattr(pdf_object_streams, "MAX_INFLATE_RATIO", 0)
    ref = _refusal(pdf)
    assert ref is not None and ref.feature == "inflate ratio"


def test_prev_depth_mutation_reddens(monkeypatch):
    pdf = _prev_pdf()
    assert isinstance(read_sheet(pdf), SheetDocument)
    monkeypatch.setattr(pdf_object_streams, "MAX_PREV_DEPTH", 0)
    ref = _refusal(pdf)
    assert ref is not None and ref.feature == "xref /Prev depth"


def test_object_stream_count_mutation_reddens(monkeypatch):
    pdf = _xref_pdf(compress=(1, 2, 3))
    assert isinstance(read_sheet(pdf), SheetDocument)  # green at the default object-stream cap
    monkeypatch.setattr(pdf_object_streams, "MAX_OBJECT_STREAMS", 0)
    ref = _refusal(pdf)
    assert ref is not None and ref.feature == "object stream count"


def test_objstm_n_mutation_reddens(monkeypatch):
    pdf = _xref_pdf(compress=(1, 2, 3))  # ObjStm with /N 3
    assert isinstance(read_sheet(pdf), SheetDocument)  # green at the default /N cap
    monkeypatch.setattr(pdf_object_streams, "MAX_OBJSTM_OBJECTS", 1)
    ref = _refusal(pdf)
    assert ref is not None and ref.feature == "object stream"
    assert "/N" in ref.detail


def test_shared_document_budget_mutation_reddens(monkeypatch):
    # The resolver charges the SAME document-wide budget the facade owns: shrinking it via
    # the facade constant makes the xref/object-stream decode refuse.
    pdf = _xref_pdf(compress=(1, 2, 3))
    assert isinstance(read_sheet(pdf), SheetDocument)  # green at the default document budget
    monkeypatch.setattr(sheet_reader, "MAX_TOTAL_DECODED_BYTES", 4)
    ref = _refusal(pdf)
    assert ref is not None and ref.feature == "decoded bytes budget"


def test_zip_bomb_refuses_with_bounded_memory(monkeypatch):
    # A tiny cross-reference stream that inflates to 50 MB must refuse having materialized
    # only ~one chunk plus the cap, never the whole 50 MB.
    monkeypatch.setattr(pdf_object_streams, "MAX_INFLATED_STREAM_BYTES", 200_000)
    pdf = _zip_bomb_pdf(50_000_000)
    tracemalloc.start()
    try:
        ref = _refusal(pdf)
        _current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert ref is not None and ref.feature == "inflated bytes cap"
    assert peak < 5_000_000  # far below the 50 MB the bomb would inflate to


# ================================================================================== AS-3
def test_xobject_name_echo_is_preview_truncated():
    long_name = "A" * 90
    pdf = _xref_pdf(
        content=b"/" + long_name.encode() + b" Do",
        page_resources=b" /Resources << /XObject << >> >>",
    )
    ref = _refusal(pdf)
    assert ref is not None and ref.feature == "xobject"
    assert "...(truncated)" in ref.detail
    assert long_name not in ref.detail  # the full attacker-controlled name never echoes


def test_unsupported_filter_name_is_preview_truncated():
    long_filter = "Z" * 90
    pdf = _xref_pdf(content=b"garbage", content_filter=b" /Filter /" + long_filter.encode())
    ref = _refusal(pdf)
    assert ref is not None and ref.feature == "stream filter"
    assert "...(truncated)" in ref.detail
    assert long_filter not in ref.detail


def test_scan_only_page_is_typed_refusal():
    # Resolves cleanly (via the new path) but the page paints NO vector geometry (text only):
    # a scan-only typed refusal, never an empty success (DB-055 (l)).
    pdf = _xref_pdf(compress=(1, 2, 3), content=b"BT /F0 12 Tf (label) Tj ET")
    ref = _refusal(pdf)
    assert ref is not None and ref.feature == "scan only"


def test_vector_page_is_not_scan_only():
    # The same shape WITH geometry is a success -> the scan-only gate is geometry-driven.
    doc = read_sheet(_xref_pdf(compress=(1, 2, 3)))
    assert isinstance(doc, SheetDocument)


# ------------------------------------------------------------ /Prev, cycle, hybrid, bomb
def _prev_pdf() -> bytes:
    """A base xref-stream section (objects 1-4 + xref A) plus an incremental update that
    rewrites content object 4 and adds xref B with /Prev -> A. Newer (B) wins for object 4."""
    header = b"%PDF-1.5\n"
    body = bytearray(header)
    base = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
    }
    offsets: dict[int, int] = {}
    for n in (1, 2, 3):
        offsets[n] = len(body)
        body += b"%d 0 obj\n%s\nendobj\n" % (n, base[n])
    offsets[4] = len(body)
    body += _content_obj(4, _LINE)  # base content
    entries_a = {0: (0, 0, 0)}
    for n in (1, 2, 3, 4):
        entries_a[n] = (1, offsets[n], 0)
    xref_a_offset = len(body)
    entries_a[5] = (1, xref_a_offset, 0)
    body += _xref_stream_blob(5, 6, entries_a, (1, 4, 2), None, None, b"")
    # --- incremental update: rewrite object 4, add xref B (/Prev -> A) ---
    new_content_offset = len(body)
    body += _content_obj(4, _LINE_V2)  # newer content, same object number 4
    entries_b = {4: (1, new_content_offset, 0), 6: (1, len(body), 0)}
    xref_b_offset = len(body)
    body += _xref_stream_blob(
        6, 7, entries_b, (1, 4, 2), None, [4, 1, 6, 1], b" /Prev %d" % xref_a_offset
    )
    body += b"startxref\n%d\n%%%%EOF\n" % xref_b_offset
    return bytes(body)


def _cycle_pdf() -> bytes:
    """One xref stream whose /Prev points back to its own byte offset -> a refused cycle."""
    header = b"%PDF-1.5\n"
    body = bytearray(header)
    base = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
    }
    offsets: dict[int, int] = {}
    for n in (1, 2, 3):
        offsets[n] = len(body)
        body += b"%d 0 obj\n%s\nendobj\n" % (n, base[n])
    offsets[4] = len(body)
    body += _content_obj(4, _LINE)
    xref_offset = len(body)
    entries = {0: (0, 0, 0)}
    for n in (1, 2, 3, 4):
        entries[n] = (1, offsets[n], 0)
    entries[5] = (1, xref_offset, 0)
    body += _xref_stream_blob(5, 6, entries, (1, 4, 2), None, None, b" /Prev %d" % xref_offset)
    body += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(body)


def _hybrid_pdf() -> bytes:
    """A §7.5.8.4 hybrid file: startxref -> a classic ``xref`` table (type-1 objects) whose
    trailer names an /XRefStm cross-reference stream carrying the compressed (type-2)
    objects; the page tree lives in an ObjStm."""
    header = b"%PDF-1.5\n"
    body = bytearray(header)
    catalog = b"<< /Type /Catalog /Pages 2 0 R >>"
    pages = b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"
    page = b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>"
    offsets: dict[int, int] = {}
    offsets[1] = len(body)
    body += b"1 0 obj\n%s\nendobj\n" % catalog
    offsets[4] = len(body)
    body += _content_obj(4, _LINE)
    offsets[5] = len(body)  # ObjStm holding objects 2 and 3
    body += _objstm_blob(5, [(2, pages), (3, page)])
    # the /XRefStm cross-reference stream (object 6): only the compressed entries (2, 3)
    xrefstm_offset = len(body)
    stm_entries = {2: (2, 5, 0), 3: (2, 5, 1)}
    body += _xref_stream_blob(6, 7, stm_entries, (1, 4, 2), None, [2, 2], b"")
    # the classic table + trailer (type-1 objects 1, 4, 5, 6; 2 and 3 marked free)
    classic_offset = len(body)
    body += b"xref\n0 7\n0000000000 65535 f \n"
    body += b"%010d 00000 n \n" % offsets[1]
    body += b"0000000000 00000 f \n"
    body += b"0000000000 00000 f \n"
    body += b"%010d 00000 n \n" % offsets[4]
    body += b"%010d 00000 n \n" % offsets[5]
    body += b"%010d 00000 n \n" % xrefstm_offset
    body += b"trailer\n<< /Size 7 /Root 1 0 R /XRefStm %d >>\n" % xrefstm_offset
    body += b"startxref\n%d\n%%%%EOF\n" % classic_offset
    return bytes(body)


def _broken_offset_pdf() -> bytes:
    """A cross-reference stream whose object-3 type-1 entry points at object 1's header (a lying
    offset landing on a REAL but WRONG object), which the identity check must reject with the
    specific "object identity" feature, never a guess."""
    header = b"%PDF-1.5\n"
    body = bytearray(header)
    base = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
    }
    offsets: dict[int, int] = {}
    for n in (1, 2, 3):
        offsets[n] = len(body)
        body += b"%d 0 obj\n%s\nendobj\n" % (n, base[n])
    offsets[4] = len(body)
    body += _content_obj(4, _LINE)
    xref_offset = len(body)
    entries = {0: (0, 0, 0)}
    for n in (1, 2, 4):
        entries[n] = (1, offsets[n], 0)
    entries[3] = (1, offsets[1], 0)  # lying offset -> lands on object 1's header, not object 3
    entries[5] = (1, xref_offset, 0)
    body += _xref_stream_blob(5, 6, entries, (1, 4, 2), None, None, b"")
    body += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(body)


def _xref_pdf_with_predictor_value(predictor_value: int) -> bytes:
    """An xref-stream file whose xref stream declares /Predictor ``predictor_value`` (e.g. 2
    for the unimplemented TIFF predictor) while the entry bytes carry a matching tag byte."""
    header = b"%PDF-1.5\n"
    body = bytearray(header)
    base = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
    }
    offsets: dict[int, int] = {}
    for n in (1, 2, 3):
        offsets[n] = len(body)
        body += b"%d 0 obj\n%s\nendobj\n" % (n, base[n])
    offsets[4] = len(body)
    body += _content_obj(4, _LINE)
    xref_offset = len(body)
    entries = {0: (0, 0, 0)}
    for n in (1, 2, 3, 4):
        entries[n] = (1, offsets[n], 0)
    entries[5] = (1, xref_offset, 0)
    w = (1, 4, 2)
    raw = bytearray()
    for onum in range(6):
        t, f2, f3 = entries.get(onum, (0, 0, 0))
        raw += _be(t, w[0]) + _be(f2, w[1]) + _be(f3, w[2])
    comp = zlib.compress(bytes(raw))
    dictionary = (
        b"<< /Type /XRef /Size 6 /W [1 4 2] /Root 1 0 R /Length %d /Filter /FlateDecode"
        b" /DecodeParms << /Predictor %d /Columns 7 >> >>" % (len(comp), predictor_value)
    )
    body += b"5 0 obj\n%s\nstream\n%s\nendstream\nendobj\n" % (dictionary, comp)
    body += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(body)


def _zip_bomb_pdf(inflated_size: int) -> bytes:
    """A file whose startxref points at an object whose stream is a highly compressible
    /XRef stream that inflates to ``inflated_size`` bytes."""
    header = b"%PDF-1.5\n"
    body = bytearray(header)
    bomb = zlib.compress(b"\x00" * inflated_size)
    xref_offset = len(body)
    dictionary = (
        b"<< /Type /XRef /Size 6 /W [1 4 2] /Root 1 0 R /Length %d /Filter /FlateDecode >>"
        % len(bomb)
    )
    body += b"5 0 obj\n%s\nstream\n%s\nendstream\nendobj\n" % (dictionary, bomb)
    body += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(body)


# =============================================================== ROUND 2 (rework) additions
#
# Consolidated G5/G3/G4/G1 round-1 findings: the predictor memory guard (G5 F1, BLOCKING), the
# incremental object-count bound (G5 F2 = G3 A1 = G1 F3), and the G4 test-adequacy gaps.
# Memory ceilings are calibrated so each guard's regression test is GREEN with the fix and RED
# under the round-1 allocation/collection order (an in-process mutation reddens it).

# Measured (local py3.11, tracemalloc): F1 fix peak ~0.04 MB vs mutation ~50 MB; F2 fix peak
# ~1.1 MB vs mutation ~11 MB. Ceilings sit between fix and mutation with wide margins both ways.
_PREDICTOR_PEAK_CEILING = 4_000_000     # << the 50 MB the pre-fix /Columns buffer allocated
_OBJECT_COUNT_PEAK_CEILING = 4_000_000  # between the bounded fix (~1.1 MB) and whole-chain (~11 MB)
# Cross-phase carry: resolver charge R=211, content charge C=600 (=20*repeat); R+C=811. A budget
# in (max(R,C)=600, R+C=811) refuses only when the seed is carried across the two phases.
_CROSS_PHASE_BUDGET = 700
_CROSS_PHASE_REPEAT = 30                 # content = 20 bytes * repeat (uncompressed, no /Filter)


# ---------------------------------------------------------------------- round-2 fixtures
def _raw_xref_stream_pdf() -> bytes:
    """An xref stream with NO /Filter: the entry table is stored raw, exercising the resolver's
    true no-/Filter decode branch (pdf_object_streams._decode_stream, filt is None)."""
    body = bytearray(b"%PDF-1.5\n")
    base = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
    }
    offsets: dict[int, int] = {}
    for n in (1, 2, 3):
        offsets[n] = len(body)
        body += b"%d 0 obj\n%s\nendobj\n" % (n, base[n])
    offsets[4] = len(body)
    body += _content_obj(4, _LINE)
    xref_offset = len(body)
    entries = {0: (0, 0, 0), 5: (1, xref_offset, 0)}
    for n in (1, 2, 3, 4):
        entries[n] = (1, offsets[n], 0)
    raw = bytearray()
    for onum in range(6):
        t, f2, f3 = entries.get(onum, (0, 0, 0))
        raw += _be(t, 1) + _be(f2, 4) + _be(f3, 2)
    dictionary = b"<< /Type /XRef /Size 6 /W [1 4 2] /Root 1 0 R /Length %d >>" % len(raw)
    body += b"5 0 obj\n%s\nstream\n%s\nendstream\nendobj\n" % (dictionary, bytes(raw))
    body += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(body)


def _zero_width_fields_pdf() -> bytes:
    """An xref stream with /W [0 4 0]: a zero-width type field (defaults to type 1) AND a
    zero-width field-3 (defaults to generation 0), covering both §7.5.8.2 defaults. Objects
    1-5 are uncompressed type-1; /Index [1 5] skips the free object 0."""
    body = bytearray(b"%PDF-1.5\n")
    base = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
    }
    offsets: dict[int, int] = {}
    for n in (1, 2, 3):
        offsets[n] = len(body)
        body += b"%d 0 obj\n%s\nendobj\n" % (n, base[n])
    offsets[4] = len(body)
    body += _content_obj(4, _LINE)
    xref_offset = len(body)
    offsets[5] = xref_offset
    raw = bytearray()
    for onum in range(1, 6):  # /Index [1 5]: only field2 (4 bytes); type and gen are defaulted
        raw += _be(offsets[onum], 4)
    comp = zlib.compress(bytes(raw))
    dictionary = (
        b"<< /Type /XRef /Size 6 /W [0 4 0] /Index [1 5] /Root 1 0 R"
        b" /Length %d /Filter /FlateDecode >>" % len(comp)
    )
    body += b"5 0 obj\n%s\nstream\n%s\nendstream\nendobj\n" % (dictionary, comp)
    body += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(body)


def _xref_stream_bad_filter_pdf(filter_name: bytes) -> bytes:
    """An xref stream declaring an unsupported /Filter (a long name), so the RESOLVER's own
    /Filter echo (pdf_object_streams._decode_stream) must be _preview-truncated (AS-3)."""
    body = bytearray(b"%PDF-1.5\n")
    base = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
    }
    offsets: dict[int, int] = {}
    for n in (1, 2, 3):
        offsets[n] = len(body)
        body += b"%d 0 obj\n%s\nendobj\n" % (n, base[n])
    offsets[4] = len(body)
    body += _content_obj(4, _LINE)
    xref_offset = len(body)
    entries = {0: (0, 0, 0), 5: (1, xref_offset, 0)}
    for n in (1, 2, 3, 4):
        entries[n] = (1, offsets[n], 0)
    raw = bytearray()  # NOT flate-compressed; the bogus /Filter must be refused before decode
    for onum in range(6):
        t, f2, f3 = entries.get(onum, (0, 0, 0))
        raw += _be(t, 1) + _be(f2, 4) + _be(f3, 2)
    dictionary = (
        b"<< /Type /XRef /Size 6 /W [1 4 2] /Root 1 0 R /Length %d /Filter /%s >>"
        % (len(raw), filter_name)
    )
    body += b"5 0 obj\n%s\nstream\n%s\nendstream\nendobj\n" % (dictionary, bytes(raw))
    body += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(body)


def _classic_with_prev_pdf() -> bytes:
    """A classic xref TABLE whose trailer carries /Prev but NO /XRefStm: the strict reader
    refuses 'incremental update chain' and the resolver defers (returns None), so the strict
    refusal must stand unchanged (G3 round-1 A6)."""
    body = bytearray(b"%PDF-1.7\n")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(_LINE), _LINE),
    ]
    offsets = []
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body += b"%d 0 obj\n%s\nendobj\n" % (index, obj)
    xref = len(body)
    body += b"xref\n0 5\n0000000000 65535 f \n"
    for off in offsets:
        body += b"%010d 00000 n \n" % off
    body += b"trailer\n<< /Size 5 /Root 1 0 R /Prev 0 >>\nstartxref\n%d\n%%%%EOF\n" % xref
    return bytes(body)


def _empty_predictor_bomb_pdf(columns: int) -> bytes:
    """The G5 round-1 Finding-1 vector: a cross-reference stream that INFLATES TO EMPTY yet
    declares /DecodeParms with a huge /Columns. The pre-fix predictor allocated a /Columns-sized
    working buffer BEFORE checking the (empty) data; the guarded path returns before row_len."""
    body = bytearray(b"%PDF-1.5\n")
    empty = zlib.compress(b"")  # inflates to b""
    xref_offset = len(body)
    dictionary = (
        b"<< /Type /XRef /Size 0 /W [1 4 2] /Root 1 0 R /Length %d /Filter /FlateDecode"
        b" /DecodeParms << /Predictor 12 /Columns %d >> >>" % (len(empty), columns)
    )
    body += b"5 0 obj\n%s\nstream\n%s\nendstream\nendobj\n" % (dictionary, empty)
    body += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(body)


def _object_count_chain_pdf(streams: int, per: int) -> bytes:
    """A /Prev chain of ``streams`` cross-reference streams, each declaring ``per`` DISTINCT
    type-1 entries at distinct object numbers. Without the incremental object-count bound the
    merged map WOULD accumulate ``streams * per`` entries before _materialize refuses; the fix
    refuses inside collection. Entry offsets are bogus (0) — the file always refuses before any
    object is materialized. Built oldest-first so each /Prev points at an already-known offset."""
    body = bytearray(b"%PDF-1.5\n")
    size = streams * per + streams + 10
    prev = None
    for j in range(streams):
        base = j * per + 1  # distinct object numbers per stream
        entries = {onum: (1, 0, 0) for onum in range(base, base + per)}
        off = len(body)
        extra = b"" if prev is None else b" /Prev %d" % prev
        body += _xref_stream_blob(900000 + j, size, entries, (1, 4, 2), None, [base, per], extra)
        prev = off
    body += b"startxref\n%d\n%%%%EOF\n" % prev  # startxref -> newest (last-built) stream
    return bytes(body)


def _cross_phase_pdf(content_repeat: int) -> bytes:
    """A compress=(1,2,3) file: the resolver decodes the ObjStm + xref stream (charging bytes);
    the long UNCOMPRESSED content (object 4, no /Filter) is decoded LATER against the SAME
    document budget (AS-2 cross-phase carry)."""
    content = b"10 10 m 100 100 l S " * content_repeat
    return _xref_pdf(compress=(1, 2, 3), content=content)


# --------------------------------------------------------------- round-2 in-process mutations
def _apply_predictor_round1(data, parms, *, absolute_cap):
    """Round-1 (pre-fix) allocation order: derive row_len from /Columns and call the REAL PNG
    unfilter (which allocates bytearray(row_len)) WITHOUT the empty-data / bound guard, so the
    predictor memory-bound test reddens under this mutation."""
    columns = sheet_objects._parm_int(parms, sheet_objects._COLUMNS_KEY, 1)
    colors = sheet_objects._parm_int(parms, sheet_objects._COLORS_KEY, 1)
    bpc = sheet_objects._parm_int(parms, sheet_objects._BPC_KEY, 8)
    row_len = (columns * colors * bpc + 7) // 8
    return sheet_objects._png_unfilter(data, row_len, max(1, (colors * bpc + 7) // 8))


def _merge_no_bound(entries_map, seen, entries, *, max_distinct, max_objects):
    """Round-1 (pre-fix) merge: accumulate the whole /Prev chain with NO incremental bound, so
    the object-count refusal falls back to the post-collection check in _materialize and the
    object-count memory-bound test reddens under this mutation."""
    for number, entry_type, field2, field3 in entries:
        if number in seen:
            continue
        seen.add(number)
        if entry_type in (1, 2):
            entries_map[number] = (entry_type, field2, field3)
    return None


# ============================================================ G5 F1 — predictor memory guard
def test_predictor_empty_inflate_is_memory_bounded():
    # BLOCKING G5 round-1 Finding 1: an empty-inflating xref stream with a huge /Columns must
    # NOT allocate a /Columns-sized buffer. Through resolve_object_table AND read_sheet the peak
    # stays tiny and the outcome is a typed value (never a crash / MemoryError).
    pdf = _empty_predictor_bomb_pdf(columns=50_000_000)
    tracemalloc.start()
    try:
        resolved = pdf_object_streams.resolve_object_table(
            pdf, max_total_decoded_bytes=sheet_reader.MAX_TOTAL_DECODED_BYTES
        )
        _c, peak_resolve = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert isinstance(resolved, (pdf_object_streams.ResolvedTable, SheetRefusal))
    assert peak_resolve < _PREDICTOR_PEAK_CEILING

    tracemalloc.start()
    try:
        ref = _refusal(pdf)
        _c, peak_read = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert ref is not None  # a typed refusal VALUE (no catalog), never a crash
    assert peak_read < _PREDICTOR_PEAK_CEILING


def test_predictor_buffer_guard_is_load_bearing(monkeypatch):
    # Restore the round-1 allocation order (buffer sized by /Columns BEFORE the empty/bound
    # check): the memory-bound test reddens — the peak balloons to ~/Columns bytes.
    monkeypatch.setattr(pdf_object_streams, "apply_predictor", _apply_predictor_round1)
    pdf = _empty_predictor_bomb_pdf(columns=50_000_000)
    tracemalloc.start()
    try:
        _refusal(pdf)
        _c, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert peak > _PREDICTOR_PEAK_CEILING  # the pre-fix code materialized the full /Columns buffer


def test_predictor_oversized_row_is_typed_refusal():
    # A predicted row longer than the absolute cap is a typed "predictor" refusal (defence for
    # the working buffer), never an allocation.
    ref = sheet_objects.apply_predictor(
        b"\x00" * 12,
        {sheet_objects._PREDICTOR_KEY: 12, sheet_objects._COLUMNS_KEY: 100},
        absolute_cap=5,
    )
    assert isinstance(ref, SheetRefusal) and ref.feature == "predictor"


def test_predictor_invalid_bpc_is_typed_refusal():
    # /BitsPerComponent outside the §7.4.4.4 set {1,2,4,8,16} is a typed "predictor" refusal.
    ref = sheet_objects.apply_predictor(
        b"\x00" * 8,
        {
            sheet_objects._PREDICTOR_KEY: 12,
            sheet_objects._BPC_KEY: 3,
            sheet_objects._COLUMNS_KEY: 1,
        },
        absolute_cap=1_000,
    )
    assert isinstance(ref, SheetRefusal) and ref.feature == "predictor"
    assert "BitsPerComponent" in ref.detail


def test_predictor_empty_data_returns_without_geometry():
    # Empty data returns b"" without touching row_len even when /Columns is enormous.
    result = sheet_objects.apply_predictor(
        b"",
        {sheet_objects._PREDICTOR_KEY: 12, sheet_objects._COLUMNS_KEY: 10**9},
        absolute_cap=8_388_608,
    )
    assert result == b""


# ================================================= G5 F2 / G3 A1 / G1 F3 — object-count bound
def test_object_count_bound_is_memory_bounded():
    # G5 round-1 Finding 2: a /Prev chain that WOULD accumulate tens of thousands of entries
    # refuses INSIDE collection with the "object count bound" feature and bounded memory.
    pdf = _object_count_chain_pdf(streams=33, per=2000)
    tracemalloc.start()
    try:
        ref = _refusal(pdf)
        _c, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert ref is not None and ref.feature == "object count bound"
    assert peak < _OBJECT_COUNT_PEAK_CEILING


def test_object_count_bound_incremental_is_load_bearing(monkeypatch):
    # Move the check back after collection (round-1: bound only in _materialize): the whole
    # chain is merged first, so the peak balloons past the ceiling although the file still
    # refuses (later) with the same feature.
    monkeypatch.setattr(pdf_object_streams, "merge_stream_entries", _merge_no_bound)
    pdf = _object_count_chain_pdf(streams=33, per=2000)
    tracemalloc.start()
    try:
        ref = _refusal(pdf)
        _c, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert ref is not None and ref.feature == "object count bound"
    assert peak > _OBJECT_COUNT_PEAK_CEILING


# ========================================================= G4 A1 [W10] — cross-phase budget
def test_cross_phase_budget_carry(monkeypatch):
    # The resolver's charged-bytes seed feeds the content decoder. With a document budget each
    # phase fits under but whose SUM they exceed, the content phase refuses.
    monkeypatch.setattr(sheet_reader, "MAX_TOTAL_DECODED_BYTES", _CROSS_PHASE_BUDGET)
    ref = _refusal(_cross_phase_pdf(_CROSS_PHASE_REPEAT))
    assert ref is not None and ref.feature == "decoded bytes budget"


def test_cross_phase_budget_carry_is_load_bearing(monkeypatch):
    # Drop the resolver's charged-bytes seed: the content phase alone fits, so the joint-budget
    # refusal disappears (the document reads, or refuses for a different reason).
    monkeypatch.setattr(sheet_reader, "MAX_TOTAL_DECODED_BYTES", _CROSS_PHASE_BUDGET)
    real = pdf_object_streams.resolve_object_table

    def _no_seed(data, *, max_total_decoded_bytes):
        result = real(data, max_total_decoded_bytes=max_total_decoded_bytes)
        if isinstance(result, pdf_object_streams.ResolvedTable):
            return pdf_object_streams.ResolvedTable(table=result.table, decoded_bytes=0)
        return result

    monkeypatch.setattr(sheet_reader, "resolve_object_table", _no_seed)
    ref = sheet_refusal(read_sheet(_cross_phase_pdf(_CROSS_PHASE_REPEAT)))
    assert ref is None or ref.feature != "decoded bytes budget"


# ============================================================ G4 A2/A3/A4 + G3 A6 coverage
def test_zero_width_type_and_field3_defaults():
    # /W [0 4 0]: the type field defaults to 1 and field-3 (generation) defaults to 0 (§7.5.8.2).
    doc = read_sheet(_zero_width_fields_pdf())
    assert isinstance(doc, SheetDocument)
    assert _first_polyline_flat(doc) == pytest.approx([10.0, 10.0, 100.0, 100.0])


def test_resolver_filter_echo_is_preview_truncated():
    # The RESOLVER's own /Filter echo (pdf_object_streams._decode_stream) is _preview-truncated
    # — a distinct echo site from the content-stream one (test_unsupported_filter_name_is_...)
    # and the XObject ones. All XObject /name echoes route through the SAME _preview helper.
    long_filter = "Q" * 90
    ref = _refusal(_xref_stream_bad_filter_pdf(long_filter.encode()))
    assert ref is not None and ref.feature == "stream filter"
    assert "...(truncated)" in ref.detail
    assert long_filter not in ref.detail


def test_xobject_no_resources_name_echo_is_preview_truncated():
    # A SECOND XObject /name echo site (Do with no /Resources) confirming the uniform _preview
    # helper truncates at every site (the first is covered by
    # test_xobject_name_echo_is_preview_truncated).
    long_name = "B" * 90
    ref = _refusal(_xref_pdf(content=b"/" + long_name.encode() + b" Do"))
    assert ref is not None and ref.feature == "xobject"
    assert "...(truncated)" in ref.detail
    assert long_name not in ref.detail


def test_classic_prev_without_xrefstm_returns_strict_refusal():
    # G3 round-1 A6: a classic xref table with trailer /Prev and no /XRefStm still returns the
    # strict "incremental update chain" refusal unchanged (the resolver defers).
    ref = _refusal(_classic_with_prev_pdf())
    assert ref is not None
    assert ref.origin == SheetRefusal.STRICT_READER
    assert ref.feature == "incremental update chain"


def test_decode_budget_charge_refuses_before_incrementing():
    # DB-064(d): _DecodeBudget.charge refuses BEFORE incrementing, so the total never overshoots.
    budget = pdf_object_streams._DecodeBudget(cap=10)
    assert budget.charge(6) is None and budget.used == 6
    ref = budget.charge(5)  # 6 + 5 = 11 > 10
    assert isinstance(ref, SheetRefusal) and ref.feature == "decoded bytes budget"
    assert budget.used == 6  # NOT incremented on refusal (no overshoot)
