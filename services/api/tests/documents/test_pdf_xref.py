"""Acceptance tests for the classic xref/trailer reader (M2-T015 unit 3i-3a-3a).

``build_pdf`` assembles a real byte-accurate document: object offsets in
the xref table are computed from where each ``N G obj`` actually lands,
never hand-typed. The builder is deterministic, so a first pass can be
used to learn real offsets and a second pass to lie about them (identity
mismatch) or to point ``startxref`` at an object header (xref-stream
refusal).
"""

from __future__ import annotations

import pytest

import app.documents.extraction.pdf_xref as pdf_xref
from app.documents.extraction.pdf_lexer import PdfName, PdfSyntaxError
from app.documents.extraction.pdf_objects import PdfRef
from app.documents.extraction.pdf_xref import (
    PdfObjectTable,
    UnsupportedPdfFeature,
    read_object_table,
)

CATALOG = b"<< /Type /Catalog /Pages 2 0 R >>"
PAGES = b"<< /Type /Pages /Kids [] /Count 0 >>"

FREE_ENTRY = b"0000000000 65535 f \n"


def build_pdf(
    objects,
    *,
    header=b"%PDF-1.7\n",
    subsections=None,
    include_size=True,
    size=None,
    include_root=True,
    root=b"1 0 R",
    extra_trailer=b"",
    offset_overrides=None,
    entry_overrides=None,
    include_startxref=True,
    startxref_override=None,
):
    """Assemble a PDF from ``{(number, generation): body_bytes}`` with REAL offsets.

    ``subsections`` is a list of ``(start, [object_numbers])``; numbers in a
    subsection are consecutive from ``start``, and a listed number with no
    body in ``objects`` (object 0 included) becomes a free entry. Returns
    ``(data, offsets)`` where ``offsets[number]`` is the true byte offset of
    that object's ``N G obj`` header.
    """
    body = bytearray(header)
    offsets = {}
    generations = {}
    for (number, generation), object_bytes in objects.items():
        offsets[number] = len(body)
        generations[number] = generation
        body += f"{number} {generation} obj\n".encode("ascii")
        body += object_bytes + b"\nendobj\n"

    if subsections is None:
        subsections = [(0, list(range(0, max(offsets) + 1)))]

    xref_offset = len(body)
    xref = bytearray(b"xref\n")
    for start, numbers in subsections:
        xref += f"{start} {len(numbers)}\n".encode("ascii")
        for number in numbers:
            if entry_overrides and number in entry_overrides:
                entry = entry_overrides[number]
            elif number in offsets:
                recorded = offsets[number]
                if offset_overrides and number in offset_overrides:
                    recorded = offset_overrides[number]
                entry = f"{recorded:010d} {generations[number]:05d} n".encode(
                    "ascii"
                ) + b" \n"
            else:
                entry = FREE_ENTRY
            assert len(entry) == 20
            xref += entry

    if size is None:
        size = max(n for _, numbers in subsections for n in numbers) + 1
    trailer_parts = []
    if include_size:
        trailer_parts.append(f"/Size {size}".encode("ascii"))
    if include_root:
        trailer_parts.append(b"/Root " + root)
    tail = bytearray(
        b"trailer\n<< " + b" ".join(trailer_parts) + extra_trailer + b" >>\n"
    )
    if include_startxref:
        recorded_start = (
            xref_offset if startxref_override is None else startxref_override
        )
        tail += b"startxref\n" + str(recorded_start).encode("ascii") + b"\n%%EOF\n"
    return bytes(body + xref + tail), offsets


def base_objects():
    return {(1, 0): CATALOG, (2, 0): PAGES}


def test_valid_table_with_two_subsections():
    objects = {
        (1, 0): CATALOG,
        (2, 0): PAGES,
        (10, 0): b"[ 1 2 3 ]",
        (11, 2): b"42",
    }
    data, _ = build_pdf(objects, subsections=[(0, [0, 1, 2]), (10, [10, 11, 12])])
    table = read_object_table(data)
    assert isinstance(table, PdfObjectTable)
    assert set(table.objects) == {(1, 0), (2, 0), (10, 0), (11, 2)}
    catalog = table.objects[(1, 0)]
    assert catalog[PdfName("Type")] == PdfName("Catalog")
    assert catalog[PdfName("Pages")] == PdfRef(2, 0)
    assert table.objects[(2, 0)][PdfName("Count")] == 0
    assert table.objects[(10, 0)] == [1, 2, 3]
    assert table.objects[(11, 2)] == 42
    assert table.trailer[PdfName("Size")] == 13
    assert table.trailer[PdfName("Root")] == PdfRef(1, 0)


def test_entry_crlf_line_end_tolerated():
    objects = base_objects()
    _, offsets = build_pdf(objects)
    crlf_entry = f"{offsets[2]:010d} 00000 n".encode("ascii") + b"\r\n"
    data, _ = build_pdf(objects, entry_overrides={2: crlf_entry})
    table = read_object_table(data)
    assert isinstance(table, PdfObjectTable)
    assert (2, 0) in table.objects


def test_cross_reference_stream_refused():
    objects = base_objects()
    _, offsets = build_pdf(objects)
    data, _ = build_pdf(objects, startxref_override=offsets[1])
    result = read_object_table(data)
    assert isinstance(result, UnsupportedPdfFeature)
    assert result.feature == "cross-reference stream"
    assert result.reject_code == "unsupported_pdf_feature"
    payload = result.to_payload()
    assert payload["reject_code"] == "unsupported_pdf_feature"
    assert payload["feature"] == "cross-reference stream"
    assert payload["detail"]


def test_prev_refused_as_incremental_update_chain():
    data, _ = build_pdf(base_objects(), extra_trailer=b" /Prev 42")
    result = read_object_table(data)
    assert isinstance(result, UnsupportedPdfFeature)
    assert result.feature == "incremental update chain"


def test_xrefstm_refused_as_hybrid_reference_file():
    data, _ = build_pdf(base_objects(), extra_trailer=b" /XRefStm 99")
    result = read_object_table(data)
    assert isinstance(result, UnsupportedPdfFeature)
    assert result.feature == "hybrid-reference file"


def test_encrypt_refused_as_encryption():
    data, _ = build_pdf(base_objects(), extra_trailer=b" /Encrypt 9 0 R")
    result = read_object_table(data)
    assert isinstance(result, UnsupportedPdfFeature)
    assert result.feature == "encryption"


def test_missing_size_refused():
    data, _ = build_pdf(base_objects(), include_size=False)
    result = read_object_table(data)
    assert isinstance(result, PdfSyntaxError)
    assert result.offset == data.index(b"trailer") + len(b"trailer\n")


def test_missing_root_refused():
    data, _ = build_pdf(base_objects(), include_root=False)
    result = read_object_table(data)
    assert isinstance(result, PdfSyntaxError)
    assert result.offset == data.index(b"trailer") + len(b"trailer\n")


def test_malformed_entry_refused_with_entry_offset():
    bad_entry = b"00000000zz 00000 n \n"
    assert len(bad_entry) == 20
    data, _ = build_pdf(base_objects(), entry_overrides={2: bad_entry})
    result = read_object_table(data)
    assert isinstance(result, PdfSyntaxError)
    assert result.offset == data.index(bad_entry)


def test_identity_mismatch_refused_when_entry_lies_about_offset():
    objects = base_objects()
    _, offsets = build_pdf(objects)
    data, _ = build_pdf(objects, offset_overrides={2: offsets[1]})
    result = read_object_table(data)
    assert isinstance(result, PdfSyntaxError)
    assert result.offset == offsets[1]


def test_object_count_bound_refused(monkeypatch):
    objects = {
        (1, 0): CATALOG,
        (2, 0): PAGES,
        (3, 0): b"3",
        (4, 0): b"4",
    }
    data, _ = build_pdf(objects)
    assert isinstance(read_object_table(data), PdfObjectTable)
    monkeypatch.setattr(pdf_xref, "MAX_PDF_OBJECTS", 3)
    result = read_object_table(data)
    assert isinstance(result, UnsupportedPdfFeature)
    assert result.feature == "object count bound"
    assert "MAX_PDF_OBJECTS=3" in result.detail


def test_missing_startxref_refused_at_end_of_data():
    data, _ = build_pdf(base_objects(), include_startxref=False)
    result = read_object_table(data)
    assert isinstance(result, PdfSyntaxError)
    assert result.offset == len(data)


@pytest.mark.parametrize("header", [b"%PDF-2.0\n", b"not a pdf\n"])
def test_wrong_header_refused(header):
    data, _ = build_pdf(base_objects(), header=header)
    result = read_object_table(data)
    assert isinstance(result, PdfSyntaxError)
    assert result.offset == 0
