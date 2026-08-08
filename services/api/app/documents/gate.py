"""S1 gate control 1: deterministic content sniffing from leading bytes (M2-T015).

First control of the synchronous upload gate (docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md
section 2, S1): the declared filename extension NEVER selects handling — the sniffed
content does (docs/SURVEY_DOCUMENT_FORMAT_POLICY.md principle 5; threats T01/T02). Sniffing
is a fixed-signature comparison over at most ``SNIFF_HEADER_BYTES`` leading bytes, stdlib
only, no heuristics and no third-party detector. Signatures cover exactly the SUPPORTED
rows of the format policy matrix (PDF, TIFF, PNG, JPEG); DXF/DWG are refused upstream by
extension (rows 6-7) and deliberately have no signature here.

This module is ONLY the sniff + extension/content agreement check. Size caps, digests,
temp spooling, storage, and structural parsing are separate controls in later units.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO, Union

from app.documents.errors import ExtensionMismatchError, UnsupportedExtensionError
from app.documents.limits import SNIFF_HEADER_BYTES

__all__ = [
    "EXTENSION_FORMATS",
    "MAGIC_SIGNATURES",
    "SniffResult",
    "check_extension_matches",
    "sniff_content",
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
