"""Acceptance tests for pdf_container (M2-T015 unit 3i-3a-3b).

Every fixture is assembled byte-by-byte with real xref offsets computed
from the actual object positions, mirroring the test_pdf_xref helper
style. Valid documents must yield exact pages; every refusal must be the
specific named PdfSyntaxError / UnsupportedPdfFeature value, asserted on
its message so a refusal from the wrong layer cannot pass spuriously.
"""

import zlib

from app.documents.extraction import pdf_container
from app.documents.extraction.pdf_container import (
    PdfDocument,
    PdfPage,
    read_pdf_container,
)
from app.documents.extraction.pdf_lexer import PdfSyntaxError
from app.documents.extraction.pdf_xref import UnsupportedPdfFeature


def _assemble_pdf(bodies, root=b"1 0 R"):
    """Build a classic-xref PDF: object N (generation 0) is bodies[N-1].

    Offsets in the xref table are the real byte positions of each
    ``N 0 obj`` header; the startxref offset is the real position of the
    ``xref`` keyword.
    """
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(bodies, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number
        out += body
        out += b"\nendobj\n"
    xref_offset = len(out)
    out += b"xref\n0 %d\n" % (len(bodies) + 1)
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root %s >>\n" % (len(bodies) + 1, root)
    out += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(out)


def _stream_body(payload, extra=b""):
    """A stream object body with an exact direct /Length plus optional dict entries."""
    return b"<< /Length %d%s >>\nstream\n" % (len(payload), extra) + payload + b"\nendstream"


def _flate_body(plain, extra=b""):
    return _stream_body(zlib.compress(plain), extra=b" /Filter /FlateDecode" + extra)


def _one_page_pdf(content_object_body, page_extra=b" /MediaBox [0 0 612 792]"):
    """Catalog(1) -> Pages(2) -> Page(3) -> content stream(4)."""
    return _assemble_pdf(
        [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R%s /Contents 4 0 R >>" % page_extra,
            content_object_body,
        ]
    )


# --- valid documents -------------------------------------------------------


def test_single_page_raw_content():
    payload = b"BT (hello survey) Tj ET"
    document = read_pdf_container(_one_page_pdf(_stream_body(payload)))
    assert isinstance(document, PdfDocument)
    assert document.pages == (
        PdfPage(index=0, media_box=(0.0, 0.0, 612.0, 792.0), content=payload),
    )


def test_two_pages_flate_decode():
    first = b"q 1 0 0 1 0 0 cm Q" * 4
    second = b"BT (page two) Tj ET"
    document = read_pdf_container(
        _assemble_pdf(
            [
                b"<< /Type /Catalog /Pages 2 0 R >>",
                b"<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>",
                b"<< /Type /Page /MediaBox [0 0 200 300] /Contents 5 0 R >>",
                b"<< /Type /Page /MediaBox [0 0 200 300] /Contents 6 0 R >>",
                _flate_body(first),
                _flate_body(second),
            ]
        )
    )
    assert isinstance(document, PdfDocument)
    assert [page.index for page in document.pages] == [0, 1]
    assert [page.content for page in document.pages] == [first, second]


def test_nested_kids_depth_first_order():
    document = read_pdf_container(
        _assemble_pdf(
            [
                b"<< /Type /Catalog /Pages 2 0 R >>",
                b"<< /Type /Pages /Kids [3 0 R 6 0 R] /MediaBox [0 0 100 100] >>",
                b"<< /Type /Pages /Kids [4 0 R 5 0 R] >>",
                b"<< /Type /Page /Contents 7 0 R >>",
                b"<< /Type /Page /Contents 8 0 R >>",
                b"<< /Type /Page /Contents 9 0 R >>",
                _stream_body(b"first"),
                _stream_body(b"second"),
                _stream_body(b"third"),
            ]
        )
    )
    assert isinstance(document, PdfDocument)
    assert [page.content for page in document.pages] == [b"first", b"second", b"third"]
    assert [page.index for page in document.pages] == [0, 1, 2]


def test_inherited_media_box_and_leaf_override():
    document = read_pdf_container(
        _assemble_pdf(
            [
                b"<< /Type /Catalog /Pages 2 0 R >>",
                b"<< /Type /Pages /Kids [3 0 R 4 0 R] /MediaBox [0 0 300 400] >>",
                b"<< /Type /Page >>",
                b"<< /Type /Page /MediaBox [0 0 50 60] >>",
            ]
        )
    )
    assert isinstance(document, PdfDocument)
    inheriting, overriding = document.pages
    assert inheriting.media_box == (0.0, 0.0, 300.0, 400.0)
    assert inheriting.content == b""  # absent /Contents is empty bytes
    assert overriding.media_box == (0.0, 0.0, 50.0, 60.0)


def test_contents_array_concatenated_with_newline():
    document = read_pdf_container(
        _assemble_pdf(
            [
                b"<< /Type /Catalog /Pages 2 0 R >>",
                b"<< /Type /Pages /Kids [3 0 R] >>",
                b"<< /Type /Page /MediaBox [0 0 10 10] /Contents [4 0 R 5 0 R] >>",
                _stream_body(b"q Q"),
                _flate_body(b"BT ET"),
            ]
        )
    )
    assert isinstance(document, PdfDocument)
    assert document.pages[0].content == b"q Q\nBT ET"


# --- structural refusals ---------------------------------------------------


def test_unresolvable_reference_is_refused():
    result = read_pdf_container(
        _assemble_pdf([b"<< /Type /Catalog /Pages 9 0 R >>"])
    )
    assert isinstance(result, PdfSyntaxError)
    assert "unresolvable reference" in result.found
    assert "9 0" in result.found


def test_reference_cycle_is_refused():
    result = read_pdf_container(
        _assemble_pdf(
            [
                b"<< /Type /Catalog /Pages 2 0 R >>",
                b"3 0 R",
                b"2 0 R",
            ]
        )
    )
    assert isinstance(result, PdfSyntaxError)
    assert "reference cycle" in result.found


def test_page_tree_cycle_is_refused():
    result = read_pdf_container(
        _assemble_pdf(
            [
                b"<< /Type /Catalog /Pages 2 0 R >>",
                b"<< /Type /Pages /Kids [3 0 R] >>",
                b"<< /Type /Pages /Kids [2 0 R] >>",
            ]
        )
    )
    assert isinstance(result, PdfSyntaxError)
    assert "page tree cycle" in result.found


def test_page_count_bound_is_refused(monkeypatch):
    monkeypatch.setattr(pdf_container, "MAX_PAGE_COUNT", 1)
    result = read_pdf_container(
        _assemble_pdf(
            [
                b"<< /Type /Catalog /Pages 2 0 R >>",
                b"<< /Type /Pages /Kids [3 0 R 4 0 R] /MediaBox [0 0 10 10] >>",
                b"<< /Type /Page >>",
                b"<< /Type /Page >>",
            ]
        )
    )
    assert isinstance(result, UnsupportedPdfFeature)
    assert result.feature == "page count bound"


def test_bad_media_box_shapes_are_refused():
    bad_boxes = [
        b"[0 0 612]",  # three elements
        b"[0 0 612 792 5]",  # five elements
        b"[0 0 (x) 792]",  # non-numeric element
        b"612",  # not an array at all
    ]
    for bad in bad_boxes:
        result = read_pdf_container(
            _one_page_pdf(_stream_body(b"q Q"), page_extra=b" /MediaBox " + bad)
        )
        assert isinstance(result, PdfSyntaxError), bad
        assert "/MediaBox" in result.expected, bad


def test_missing_media_box_everywhere_is_refused():
    result = read_pdf_container(
        _assemble_pdf(
            [
                b"<< /Type /Catalog /Pages 2 0 R >>",
                b"<< /Type /Pages /Kids [3 0 R] >>",
                b"<< /Type /Page >>",
            ]
        )
    )
    assert isinstance(result, PdfSyntaxError)
    assert "missing MediaBox" in result.found


def test_non_page_leaf_type_is_refused():
    result = read_pdf_container(
        _assemble_pdf(
            [
                b"<< /Type /Catalog /Pages 2 0 R >>",
                b"<< /Type /Pages /Kids [3 0 R] /MediaBox [0 0 10 10] >>",
                b"<< /Type /Font >>",
            ]
        )
    )
    assert isinstance(result, PdfSyntaxError)
    assert "/Pages or /Page" in result.expected


# --- stream-decode refusals ------------------------------------------------


def test_unknown_filter_name_is_refused():
    result = read_pdf_container(
        _one_page_pdf(_stream_body(b"opaque", extra=b" /Filter /LZWDecode"))
    )
    assert isinstance(result, UnsupportedPdfFeature)
    assert result.feature == "stream filter"
    assert "LZWDecode" in result.detail


def test_filter_array_is_refused():
    result = read_pdf_container(
        _one_page_pdf(
            _stream_body(zlib.compress(b"x"), extra=b" /Filter [/FlateDecode]")
        )
    )
    assert isinstance(result, UnsupportedPdfFeature)
    assert result.feature == "stream filter array"


def test_decode_parms_is_refused():
    result = read_pdf_container(
        _one_page_pdf(
            _flate_body(b"q Q", extra=b" /DecodeParms << /Predictor 12 >>")
        )
    )
    assert isinstance(result, UnsupportedPdfFeature)
    assert result.feature == "decode parameters"


def test_corrupt_flate_stream_is_refused():
    result = read_pdf_container(
        _one_page_pdf(
            _stream_body(b"this is not deflate data", extra=b" /Filter /FlateDecode")
        )
    )
    assert isinstance(result, UnsupportedPdfFeature)
    assert result.feature == "corrupt flate stream"


def test_flate_output_bound_is_refused(monkeypatch):
    monkeypatch.setattr(pdf_container, "MAX_DECODED_STREAM_BYTES", 16)
    result = read_pdf_container(_one_page_pdf(_flate_body(b"A" * 1000)))
    assert isinstance(result, UnsupportedPdfFeature)
    assert result.feature == "flate output bound"
