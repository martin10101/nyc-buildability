"""Named S1 limits for the survey / official-document ingestion module.

Every bound here is an **initial bound** from the limits table of
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md section 5: a named constant, proven by a
fixture, confirmed with the G0 disk/execution budget, and changed only through review —
never tuned silently and never set by AI. Worker-side limits (pages, pixels,
decompression, RSS, timeouts, scavenging) belong to later M2-T015 units and are
deliberately absent until the section-5 parser isolation boundary exists.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "DEFAULT_GATE_LIMITS",
    "DISPLAY_FILENAME_MAX_CHARS",
    "MAX_UPLOAD_BYTES",
    "SNIFF_HEADER_BYTES",
    "STREAM_CHUNK_BYTES",
    "GateLimits",
]

# Architecture section 5 limits table: MAX_UPLOAD_BYTES = 50 MiB, stream-enforced at S1
# before durable storage (threat T03).
MAX_UPLOAD_BYTES = 50 * 1024 * 1024

# Bytes of the received prefix compared against fixed magic numbers (sniffing.py). Large
# enough for every signature this module knows, including the ASCII-DXF heuristic window;
# nothing beyond this prefix is inspected at S1 (structural validation is S2, worker-side,
# isolation-gated).
SNIFF_HEADER_BYTES = 512

# Chunk size for the S1 streaming loop (cap enforcement + digest + spool).
STREAM_CHUNK_BYTES = 64 * 1024

# Display-filename truncation bound (filenames are metadata only — threat T07).
DISPLAY_FILENAME_MAX_CHARS = 255


@dataclass(frozen=True)
class GateLimits:
    """Injectable limit set for the S1 gate.

    Production callers use :data:`DEFAULT_GATE_LIMITS`, built from the reviewed named
    constants above. Tests construct small instances to prove the enforcement mechanism
    at exact boundaries without allocating 50 MiB fixtures; doing so never changes the
    reviewed production bounds, which are asserted verbatim by the test suite.
    """

    max_upload_bytes: int = MAX_UPLOAD_BYTES
    sniff_header_bytes: int = SNIFF_HEADER_BYTES
    stream_chunk_bytes: int = STREAM_CHUNK_BYTES

    def __post_init__(self) -> None:
        if self.max_upload_bytes < 1:
            raise ValueError("max_upload_bytes must be >= 1")
        if self.sniff_header_bytes < 1:
            raise ValueError("sniff_header_bytes must be >= 1")
        if self.stream_chunk_bytes < 1:
            raise ValueError("stream_chunk_bytes must be >= 1")


DEFAULT_GATE_LIMITS = GateLimits()
