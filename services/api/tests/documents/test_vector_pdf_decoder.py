"""Acceptance tests for the concrete vector/embedded-text PDF decoder (M2-T015 unit 3k).

Covers the first :class:`DecoderSeam` implementation (architecture §§3-5, SB-S1):

- a digitally-authored PDF decodes into ordered :class:`DecodedPage` primitives
  carrying device-space vector segments, rects, and embedded text runs;
- every reader/interpreter refusal (malformed structure; a construct outside the
  strict survey subset such as a curve) is returned as a VALUE — the sole element
  of the sequence — never raised, and is recognized by ``pdf_decode_refusal``;
- one refusing page fails the whole decode (no partial, silently-trusted document);
- the decoder structurally satisfies the runtime-checkable ``DecoderSeam`` protocol
  and is a stateless pure function of its bytes.

PDFs are assembled byte-by-byte with real xref offsets, mirroring test_pdf_container.
"""

from __future__ import annotations

import zlib

from app.documents.extraction import DecoderSeam
from app.documents.extraction.pdf_content import PageContent, TextRun, VectorRect, VectorSegment
from app.documents.extraction.pdf_lexer import PdfSyntaxError
from app.documents.extraction.pdf_xref import UnsupportedPdfFeature
from app.documents.extraction.vector_pdf_decoder import (
    DecodedPage,
    VectorPdfDecoder,
    pdf_decode_refusal,
)


def _assemble_pdf(bodies, root=b"1 0 R"):
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(bodies, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref_offset = len(out)
    out += b"xref\n0 %d\n" % (len(bodies) + 1) + b"0000000000 65535 f \n"
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root %s >>\n" % (len(bodies) + 1, root)
    out += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(out)


def _stream_body(payload, extra=b""):
    return b"<< /Length %d%s >>\nstream\n" % (len(payload), extra) + payload + b"\nendstream"


def _one_page_pdf(content, page_extra=b" /MediaBox [0 0 612 792]"):
    return _assemble_pdf(
        [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R%s /Contents 4 0 R >>" % page_extra,
            _stream_body(content),
        ]
    )


class TestSuccessfulDecode:
    def test_embedded_text_run_is_decoded(self):
        pdf = _one_page_pdf(b"BT /F1 12 Tf 100 700 Td (survey text) Tj ET")
        primitives = VectorPdfDecoder().decode(pdf)
        assert pdf_decode_refusal(primitives) is None
        assert len(primitives) == 1
        page = primitives[0]
        assert isinstance(page, DecodedPage)
        assert page.index == 0
        assert page.media_box == (0.0, 0.0, 612.0, 792.0)
        assert isinstance(page.content, PageContent)
        assert [run.text for run in page.content.text_runs] == ["survey text"]
        assert isinstance(page.content.text_runs[0], TextRun)

    def test_vector_segments_and_rect_are_decoded(self):
        # A path (m/l) plus a rectangle (re) — the vector-object primitives.
        pdf = _one_page_pdf(b"10 20 m 110 20 l S 5 5 40 30 re f")
        primitives = VectorPdfDecoder().decode(pdf)
        assert pdf_decode_refusal(primitives) is None
        content = primitives[0].content
        assert content.segments == (VectorSegment(10.0, 20.0, 110.0, 20.0),)
        assert content.rects == (VectorRect(5.0, 5.0, 40.0, 30.0),)

    def test_multiple_pages_decode_in_order(self):
        pdf = _assemble_pdf(
            [
                b"<< /Type /Catalog /Pages 2 0 R >>",
                b"<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>",
                b"<< /Type /Page /MediaBox [0 0 200 300] /Contents 5 0 R >>",
                b"<< /Type /Page /MediaBox [0 0 200 300] /Contents 6 0 R >>",
                _stream_body(b"BT /F1 10 Tf 0 0 Td (one) Tj ET"),
                _stream_body(b"BT /F1 10 Tf 0 0 Td (two) Tj ET"),
            ]
        )
        primitives = VectorPdfDecoder().decode(pdf)
        assert pdf_decode_refusal(primitives) is None
        assert [p.index for p in primitives] == [0, 1]
        assert [p.content.text_runs[0].text for p in primitives] == ["one", "two"]

    def test_flate_encoded_content_is_decoded(self):
        payload = b"BT /F1 12 Tf 0 0 Td (compressed) Tj ET"
        body = _stream_body(zlib.compress(payload), extra=b" /Filter /FlateDecode")
        pdf = _assemble_pdf(
            [
                b"<< /Type /Catalog /Pages 2 0 R >>",
                b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
                b"<< /Type /Page /MediaBox [0 0 100 100] /Contents 4 0 R >>",
                body,
            ]
        )
        primitives = VectorPdfDecoder().decode(pdf)
        assert pdf_decode_refusal(primitives) is None
        assert primitives[0].content.text_runs[0].text == "compressed"


class TestFailClosedRefusal:
    def test_curve_operator_is_an_unsupported_feature_refusal(self):
        # A Bezier curve (c) is outside the strict straight-line survey subset.
        pdf = _one_page_pdf(b"10 10 m 20 20 30 30 40 40 c S")
        primitives = VectorPdfDecoder().decode(pdf)
        refusal = pdf_decode_refusal(primitives)
        assert isinstance(refusal, UnsupportedPdfFeature)

    def test_malformed_structure_is_a_syntax_error_refusal(self):
        primitives = VectorPdfDecoder().decode(b"%PDF-1.4\nnot a real pdf")
        refusal = pdf_decode_refusal(primitives)
        assert isinstance(refusal, PdfSyntaxError)

    def test_non_bytes_input_refuses_without_raising(self):
        for bad in (None, "a string", 123, ["bytes"]):
            primitives = VectorPdfDecoder().decode(bad)  # type: ignore[arg-type]
            assert isinstance(pdf_decode_refusal(primitives), PdfSyntaxError)

    def test_one_bad_page_fails_the_whole_decode(self):
        # Page 1 is clean; page 2 uses a curve -> the whole decode is one refusal,
        # never a partial (page-1-only) document.
        pdf = _assemble_pdf(
            [
                b"<< /Type /Catalog /Pages 2 0 R >>",
                b"<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>",
                b"<< /Type /Page /MediaBox [0 0 100 100] /Contents 5 0 R >>",
                b"<< /Type /Page /MediaBox [0 0 100 100] /Contents 6 0 R >>",
                _stream_body(b"BT /F1 10 Tf 0 0 Td (fine) Tj ET"),
                _stream_body(b"0 0 m 1 1 2 2 3 3 c S"),
            ]
        )
        primitives = VectorPdfDecoder().decode(pdf)
        assert isinstance(pdf_decode_refusal(primitives), UnsupportedPdfFeature)
        assert not any(isinstance(item, DecodedPage) for item in primitives)


class TestDecoderContract:
    def test_decoder_satisfies_the_runtime_checkable_seam(self):
        assert isinstance(VectorPdfDecoder(), DecoderSeam)

    def test_decoder_is_stateless_across_calls(self):
        decoder = VectorPdfDecoder()
        pdf = _one_page_pdf(b"BT /F1 12 Tf 0 0 Td (idempotent) Tj ET")
        first = decoder.decode(pdf)
        second = decoder.decode(pdf)
        assert [p.content.text_runs[0].text for p in first] == [
            p.content.text_runs[0].text for p in second
        ]

    def test_refusal_helper_distinguishes_single_page_success_from_refusal(self):
        # A single valid page is length-1 too: the element TYPE, not length, decides.
        ok = VectorPdfDecoder().decode(_one_page_pdf(b"BT /F1 12 Tf 0 0 Td (x) Tj ET"))
        assert len(ok) == 1 and pdf_decode_refusal(ok) is None
        bad = VectorPdfDecoder().decode(b"garbage")
        assert len(bad) == 1 and pdf_decode_refusal(bad) is not None
