"""Unit tests for S1 gate control 1: content sniffing + extension agreement (M2-T015).

Proves, against docs/SURVEY_DOCUMENT_FORMAT_POLICY.md and the upload threat model:

1. every SUPPORTED-format signature (PDF ``%PDF-``, PNG, TIFF ``II*``/``MM*``, JPEG)
   sniffs to its canonical format and passes ``check_extension_matches`` for every
   extension spelling that declares it (case, leading dot, tif/tiff, jpg/jpeg);
2. mismatched extension/content pairs — including the T01/T02 vectors
   (executable renamed to .pdf, HTML renamed to .tiff) — raise the typed
   ``ExtensionMismatchError`` from the ``errors.py`` hierarchy;
3. unknown, empty, and truncated leading bytes are unrecognized (never guessed) and
   fail the check for any declared extension;
4. sniffing reads at most ``SNIFF_HEADER_BYTES`` from a stream, and typed-error
   payloads carry metadata only — never document bytes.
"""

from __future__ import annotations

import io

import pytest

from app.documents.errors import (
    DocumentIngestionError,
    ExtensionMismatchError,
    UnsupportedExtensionError,
)
from app.documents.gate import (
    EXTENSION_FORMATS,
    MAGIC_SIGNATURES,
    SniffResult,
    check_extension_matches,
    sniff_content,
)
from app.documents.limits import SNIFF_HEADER_BYTES

PDF_BYTES = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"
PNG_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
TIFF_LE_BYTES = b"II*\x00\x08\x00\x00\x00\x0e\x00"
TIFF_BE_BYTES = b"MM\x00*\x00\x00\x00\x08\x00\x0e"
JPEG_BYTES = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01"

EXE_BYTES = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00"  # PE executable header
HTML_BYTES = b"<!DOCTYPE html><html><body>not a survey</body></html>"

MATCHING = [
    (PDF_BYTES, "pdf", "pdf", "application/pdf"),
    (PDF_BYTES, ".pdf", "pdf", "application/pdf"),
    (PDF_BYTES, "PDF", "pdf", "application/pdf"),
    (PNG_BYTES, "png", "png", "image/png"),
    (TIFF_LE_BYTES, "tif", "tiff", "image/tiff"),
    (TIFF_LE_BYTES, "tiff", "tiff", "image/tiff"),
    (TIFF_BE_BYTES, "tiff", "tiff", "image/tiff"),
    (JPEG_BYTES, "jpg", "jpeg", "image/jpeg"),
    (JPEG_BYTES, "jpeg", "jpeg", "image/jpeg"),
]


@pytest.mark.parametrize("data, ext, format_id, media_type", MATCHING)
def test_supported_magic_sniffs_and_matches_declared_extension(data, ext, format_id, media_type):
    sniffed = sniff_content(data)
    assert sniffed == SniffResult(format=format_id, media_type=media_type)
    assert sniffed.recognized
    assert check_extension_matches(ext, sniffed) == format_id


@pytest.mark.parametrize("data, format_id", sorted({(d, f) for d, _, f, _ in MATCHING}))
def test_sniff_accepts_binary_stream_without_rewind(data, format_id):
    stream = io.BytesIO(data + b"\x00" * SNIFF_HEADER_BYTES)
    assert sniff_content(stream).format == format_id
    assert stream.tell() <= SNIFF_HEADER_BYTES


MISMATCHED = [
    (PNG_BYTES, "pdf"),  # image declared as PDF
    (PDF_BYTES, "png"),  # PDF declared as image
    (TIFF_LE_BYTES, "png"),  # recognized, wrong format
    (JPEG_BYTES, "tiff"),
    (EXE_BYTES, "pdf"),  # threat T01: executable renamed to .pdf
    (HTML_BYTES, "tiff"),  # threat T02: HTML renamed to .tiff
    (b"", "png"),  # empty upload
    (b"%PD", "pdf"),  # truncated magic
    (b"\x00\x01\x02\x03", "jpg"),  # unknown magic
]


@pytest.mark.parametrize("data, ext", MISMATCHED)
def test_extension_content_mismatch_raises_typed_error(data, ext):
    sniffed = sniff_content(data)
    with pytest.raises(ExtensionMismatchError) as excinfo:
        check_extension_matches(ext, sniffed)
    err = excinfo.value
    assert isinstance(err, DocumentIngestionError)
    payload = err.to_payload()
    assert payload["reject_code"] == "extension_mismatch"
    assert payload["declared_extension"] == ext
    # Metadata only — no document bytes in any payload value (threat T11).
    assert not any(isinstance(v, (bytes, bytearray)) for v in payload.values())


@pytest.mark.parametrize("data", [b"", b"%PD", b"II*", b"MM", b"\x00" * 64, EXE_BYTES, HTML_BYTES])
def test_unknown_or_empty_magic_is_unrecognized_never_guessed(data):
    sniffed = sniff_content(data)
    assert sniffed == SniffResult(format=None, media_type=None)
    assert not sniffed.recognized


@pytest.mark.parametrize("ext", ["docx", "dxf", "dwg", "", ".", "pdf.exe"])
def test_unsupported_declared_extension_raises_typed_error(ext):
    with pytest.raises(UnsupportedExtensionError) as excinfo:
        check_extension_matches(ext, sniff_content(PDF_BYTES))
    assert excinfo.value.to_payload()["reject_code"] == "unsupported_extension"


def test_signature_table_covers_exactly_the_supported_formats():
    assert {f for _, f, _ in MAGIC_SIGNATURES} == set(EXTENSION_FORMATS.values()) == {
        "pdf",
        "png",
        "tiff",
        "jpeg",
    }
    # Every signature fits the sniff window, and none is a prefix of another.
    sigs = [s for s, _, _ in MAGIC_SIGNATURES]
    assert all(len(s) <= SNIFF_HEADER_BYTES for s in sigs)
    assert not any(a != b and b.startswith(a) for a in sigs for b in sigs)


def test_non_binary_input_is_a_type_error_not_a_typed_rejection():
    with pytest.raises(TypeError):
        sniff_content("not bytes")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        sniff_content(io.StringIO("%PDF-1.7"))  # type: ignore[arg-type]
