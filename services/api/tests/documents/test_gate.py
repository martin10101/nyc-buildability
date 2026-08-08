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
   payloads carry metadata only — never document bytes;
5. ``stream_gate`` consumes the stream once in bounded chunks, returns the exact size
   and the known-answer ``sha256:`` digest of the EXACT original bytes (stable across
   independent reads), and composes with ``check_extension_matches``;
6. the streaming cap trips typed ``UploadTooLargeError`` at exactly cap + 1 bytes,
   reading no further — never buffering the whole file — and empty input yields a
   deterministic empty-digest result, not a crash.
"""

from __future__ import annotations

import hashlib
import io
import re

import pytest

from app.documents.errors import (
    DocumentIngestionError,
    ExtensionMismatchError,
    UnsupportedExtensionError,
    UploadTooLargeError,
)
from app.documents.gate import (
    EXTENSION_FORMATS,
    MAGIC_SIGNATURES,
    SniffResult,
    StreamGateResult,
    check_extension_matches,
    sniff_content,
    stream_gate,
)
from app.documents.limits import (
    DEFAULT_GATE_LIMITS,
    MAX_UPLOAD_BYTES,
    SNIFF_HEADER_BYTES,
    STREAM_CHUNK_BYTES,
    GateLimits,
)

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


# --------------------------------------------------- control 2: streaming cap + digest

# Small injectable limits prove the enforcement mechanism at exact boundaries without
# allocating 50 MiB fixtures; the reviewed production bounds are asserted verbatim below.
SMALL = GateLimits(max_upload_bytes=8, sniff_header_bytes=8, stream_chunk_bytes=3)

DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")  # survey_evidence document_digest


def known_digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def test_production_limits_are_the_reviewed_constants_verbatim():
    assert DEFAULT_GATE_LIMITS.max_upload_bytes == MAX_UPLOAD_BYTES == 50 * 1024 * 1024
    assert DEFAULT_GATE_LIMITS.stream_chunk_bytes == STREAM_CHUNK_BYTES == 64 * 1024
    assert DEFAULT_GATE_LIMITS.sniff_header_bytes == SNIFF_HEADER_BYTES == 512


@pytest.mark.parametrize("data, ext, format_id", [(PDF_BYTES, "pdf", "pdf"), (PNG_BYTES, "png", "png")])
def test_stream_gate_under_cap_yields_size_digest_and_composable_sniff(data, ext, format_id):
    sniffed, size_bytes, digest = stream_gate(io.BytesIO(data))
    assert size_bytes == len(data)
    assert digest == known_digest(data)
    assert DIGEST_PATTERN.fullmatch(digest)
    # Composes with the 3b-1 control: the same pass's sniff feeds the agreement check.
    assert check_extension_matches(ext, sniffed) == format_id


def test_stream_digest_is_exact_over_chunk_boundaries_and_stable_across_two_reads():
    data = bytes(range(256)) * 5  # 1280 bytes: many 3-byte chunks, not chunk-aligned
    limits = GateLimits(max_upload_bytes=2048, sniff_header_bytes=8, stream_chunk_bytes=3)
    first = stream_gate(io.BytesIO(data), limits)
    second = stream_gate(io.BytesIO(data), limits)
    assert first == second == StreamGateResult(SniffResult(None, None), len(data), known_digest(data))


def test_over_cap_raises_typed_oversize_exactly_at_the_boundary():
    assert stream_gate(io.BytesIO(b"x" * 8), SMALL).size_bytes == 8  # cap itself passes
    with pytest.raises(UploadTooLargeError) as excinfo:
        stream_gate(io.BytesIO(b"x" * 9), SMALL)  # cap + 1 fails
    payload = excinfo.value.to_payload()
    assert payload["reject_code"] == "upload_too_large"
    assert payload["max_upload_bytes"] == 8
    assert payload["observed_bytes"] == 9
    assert not any(isinstance(v, (bytes, bytearray)) for v in payload.values())


def test_over_cap_stops_reading_immediately_without_buffering_whole_stream():
    stream = io.BytesIO(b"x" * 10_000)
    with pytest.raises(UploadTooLargeError):
        stream_gate(stream, SMALL)
    assert stream.tell() <= SMALL.max_upload_bytes + 1  # never read past cap + 1


def test_empty_input_yields_empty_known_digest_and_unrecognized_sniff():
    result = stream_gate(io.BytesIO(b""))
    assert result.size_bytes == 0
    assert result.digest == known_digest(b"")
    assert not result.sniffed.recognized
    with pytest.raises(ExtensionMismatchError):  # empty upload can never pass the gate
        check_extension_matches("pdf", result.sniffed)


def test_stream_gate_rejects_non_binary_input_as_type_error():
    with pytest.raises(TypeError):
        stream_gate(io.StringIO("%PDF-1.7"))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        stream_gate(b"raw bytes are not a stream")  # type: ignore[arg-type]
