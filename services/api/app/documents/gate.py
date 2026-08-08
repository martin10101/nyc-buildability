"""S1 gate controls 1-2: content sniffing + streaming size cap / digest (M2-T015).

First control of the synchronous upload gate (docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md
section 2, S1): the declared filename extension NEVER selects handling — the sniffed
content does (docs/SURVEY_DOCUMENT_FORMAT_POLICY.md principle 5; threats T01/T02). Sniffing
is a fixed-signature comparison over at most ``SNIFF_HEADER_BYTES`` leading bytes, stdlib
only, no heuristics and no third-party detector. Signatures cover exactly the SUPPORTED
rows of the format policy matrix (PDF, TIFF, PNG, JPEG); DXF/DWG are refused upstream by
extension (rows 6-7) and deliberately have no signature here.

Control 2 (``stream_gate``) is the single-pass streaming loop: it consumes the upload in
``stream_chunk_bytes`` reads, enforces ``max_upload_bytes`` the moment the cap is exceeded
(typed ``UploadTooLargeError``, threat T03 — never buffering the whole file, never reading
more than cap + 1 bytes), and hashes the EXACT original bytes into the immutable-original
identity ``sha256:<64 lowercase hex>`` (survey_evidence ``document_digest`` wire format).
Temp spooling, storage, and structural parsing are separate controls in later units.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import BinaryIO, NamedTuple, Union

from app.documents.errors import (
    ExtensionMismatchError,
    UnsupportedExtensionError,
    UploadTooLargeError,
)
from app.documents.limits import DEFAULT_GATE_LIMITS, SNIFF_HEADER_BYTES, GateLimits

__all__ = [
    "EXTENSION_FORMATS",
    "MAGIC_SIGNATURES",
    "SniffResult",
    "StreamGateResult",
    "check_extension_matches",
    "sniff_content",
    "stream_gate",
]

# Fixed magic-number table: (leading-byte signature, canonical format id, media type).
# PDF: ISO 32000 header "%PDF-" (version digits follow the hyphen). PNG: the full 8-byte
# signature. TIFF: little-endian "II*\0" and big-endian "MM\0*". JPEG: SOI + marker
# prefix FF D8 FF. No signature is a prefix of another, so match order is immaterial.
MAGIC_SIGNATURES: tuple[tuple[bytes, str, str], ...] = (
    (b"%PDF-", "pdf", "application/pdf"),
    (b"\x89PNG\r\n\x1a\n", "png", "image/png"),
    (b"II*\x00", "tiff", "image/tiff"),
    (b"MM\x00*", "tiff", "image/tiff"),
    (b"\xff\xd8\xff", "jpeg", "image/jpeg"),
)

# Declared-extension -> canonical format id, for the SUPPORTED policy rows only.
EXTENSION_FORMATS: dict[str, str] = {
    "pdf": "pdf",
    "png": "png",
    "tif": "tiff",
    "tiff": "tiff",
    "jpg": "jpeg",
    "jpeg": "jpeg",
}


@dataclass(frozen=True)
class SniffResult:
    """Outcome of sniffing: canonical format id + media type, or None/None if unknown.

    Carries metadata only — never the inspected bytes — so it is safe to embed in
    typed-error payloads and audit records (threat T11).
    """

    format: Union[str, None]
    media_type: Union[str, None]

    @property
    def recognized(self) -> bool:
        return self.format is not None


def _read_header(data_or_stream: Union[bytes, bytearray, memoryview, BinaryIO]) -> bytes:
    if isinstance(data_or_stream, (bytes, bytearray, memoryview)):
        return bytes(memoryview(data_or_stream)[:SNIFF_HEADER_BYTES])
    read = getattr(data_or_stream, "read", None)
    if read is None:
        raise TypeError(
            "sniff_content expects bytes-like data or a binary stream with read()"
        )
    header = read(SNIFF_HEADER_BYTES)
    if not isinstance(header, bytes):
        raise TypeError("sniff_content requires a binary stream, not a text stream")
    return header


def sniff_content(
    data_or_stream: Union[bytes, bytearray, memoryview, BinaryIO],
) -> SniffResult:
    """Deterministically identify content from at most ``SNIFF_HEADER_BYTES`` leading bytes.

    Accepts bytes-like data or a binary stream; a stream is consumed by exactly one
    ``read(SNIFF_HEADER_BYTES)`` call and is not rewound (the S1 caller owns position).
    Unknown or empty leading bytes yield an unrecognized result — never a guess.
    """
    header = _read_header(data_or_stream)
    for signature, format_id, media_type in MAGIC_SIGNATURES:
        if header.startswith(signature):
            return SniffResult(format=format_id, media_type=media_type)
    return SniffResult(format=None, media_type=None)


def check_extension_matches(declared_ext: str, sniffed: SniffResult) -> str:
    """Require the declared extension and the sniffed content to name the same format.

    Returns the canonical format id on agreement. Raises ``UnsupportedExtensionError``
    when the declared extension is outside the SUPPORTED policy rows, and
    ``ExtensionMismatchError`` when the sniffed content is unrecognized or names a
    different format than the extension declares (executable-renamed-to-.pdf,
    HTML-renamed-to-.tiff — threats T01/T02). Payloads carry metadata only.
    """
    ext = declared_ext.strip().lower()
    if ext.startswith("."):
        ext = ext[1:]
    expected = EXTENSION_FORMATS.get(ext)
    if expected is None:
        raise UnsupportedExtensionError(
            f"declared extension {ext!r} names no supported upload format",
            declared_extension=ext,
            supported_extensions=sorted(EXTENSION_FORMATS),
        )
    if sniffed.format != expected:
        raise ExtensionMismatchError(
            f"declared extension {ext!r} ({expected}) does not match sniffed content "
            f"({sniffed.format if sniffed.recognized else 'unrecognized'})",
            declared_extension=ext,
            declared_format=expected,
            sniffed_format=sniffed.format,
            sniffed_media_type=sniffed.media_type,
        )
    return expected


class StreamGateResult(NamedTuple):
    """Single-pass stream outcome: sniffed type, exact size, immutable-original digest.

    ``digest`` is ``sha256:`` + 64 lowercase hex over the EXACT original bytes — the
    survey_evidence ``document_digest`` wire format (``^sha256:[0-9a-f]{64}$``), the
    content identity of the stored original. Metadata only; never the bytes themselves.
    """

    sniffed: SniffResult
    size_bytes: int
    digest: str


def stream_gate(
    stream: BinaryIO, limits: GateLimits = DEFAULT_GATE_LIMITS
) -> StreamGateResult:
    """Consume an upload stream exactly once: cap, digest, and sniff in a single pass.

    Reads bounded chunks (``limits.stream_chunk_bytes``) and raises the typed
    ``UploadTooLargeError`` the moment more than ``limits.max_upload_bytes`` arrives:
    each read is clamped to the remaining allowance + 1, so at most cap + 1 bytes are
    ever read and at most one chunk is ever held in memory (threat T03). The SHA-256
    digest and the sniff header accumulate over the same pass — no rewind, no second
    read, no whole-file buffer. The oversize payload carries metadata only;
    ``observed_bytes`` is a lower bound because reading stops at the first over-cap byte.
    """
    read = getattr(stream, "read", None)
    if read is None:
        raise TypeError("stream_gate expects a binary stream with read()")
    cap = limits.max_upload_bytes
    hasher = hashlib.sha256()
    size = 0
    header = b""
    while True:
        chunk = read(min(limits.stream_chunk_bytes, cap - size + 1))
        if not isinstance(chunk, bytes):
            raise TypeError("stream_gate requires a binary stream, not a text stream")
        if not chunk:
            break
        size += len(chunk)
        if size > cap:
            raise UploadTooLargeError(
                f"upload exceeds the {cap}-byte cap; rejected at the first over-cap byte",
                max_upload_bytes=cap,
                observed_bytes=size,
            )
        hasher.update(chunk)
        if len(header) < limits.sniff_header_bytes:
            header += chunk[: limits.sniff_header_bytes - len(header)]
    return StreamGateResult(
        sniffed=sniff_content(header),
        size_bytes=size,
        digest=f"sha256:{hasher.hexdigest()}",
    )
