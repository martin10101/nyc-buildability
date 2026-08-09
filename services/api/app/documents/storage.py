"""Immutable, digest-addressed storage for original uploaded documents.

Implements architecture sections 6-7 (docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md):
originals are stored under their ``sha256:<64 hex>`` content digest — never under a
client-supplied filename (threat T07) — are write-once (threat T10), and every read
re-hashes the stored bytes so tamper/corruption surfaces as a typed
``DigestMismatchError``, never silently and never auto-repaired.

B-001 honesty: the production object store for durable originals is DEFERRED under
blocker B-001. ``TempDirStorage`` here is the CI/local implementation only — a plain
directory under a caller-supplied root with no bucket, no credentials, and no network
I/O. Production code binds to the ``OriginalDocumentStorage`` interface; the cloud
implementation lands when B-001 resolves and must make the exists/write pair a single
conditional put (the local exists-then-write is not concurrency-safe and is acceptable
only for single-process CI/local use).
"""

from __future__ import annotations

import hashlib
import re
from abc import ABC, abstractmethod
from pathlib import Path

from app.documents.errors import (
    DigestMismatchError,
    ImmutableOriginalViolationError,
    InvalidDigestKeyError,
    OriginalNotFoundError,
)

__all__ = [
    "ORIGINALS_SUBDIR",
    "OriginalDocumentStorage",
    "TempDirStorage",
]

# Subdirectory of the storage root holding the originals, one file per digest hex.
ORIGINALS_SUBDIR = "originals"

# Wire format of a digest key: lowercase hex only. Anything else — wrong prefix,
# wrong length, uppercase, traversal shapes — is refused before any filesystem use.
_DIGEST_KEY_RE = re.compile(r"sha256:[0-9a-f]{64}\Z")


def _digest_hex_of(key: str) -> str:
    """Validate ``key`` and return its 64-hex body, before any filesystem interaction."""
    if not isinstance(key, str) or _DIGEST_KEY_RE.fullmatch(key) is None:
        raise InvalidDigestKeyError(
            "digest key must be 'sha256:' followed by exactly 64 lowercase hex characters",
            digest_key=key if isinstance(key, str) else repr(key),
        )
    return key.split(":", 1)[1]


def _sha256_key(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


class OriginalDocumentStorage(ABC):
    """Write-once, digest-addressed store for original document bytes.

    Keys are always ``sha256:<64 lowercase hex>`` content digests; implementations
    must refuse malformed keys typed, refuse overwrites typed, and verify the digest
    of the stored bytes on every read.
    """

    @abstractmethod
    def put_original(self, key: str, data: bytes) -> None:
        """Store ``data`` under its digest ``key``; typed refusal on overwrite/mismatch."""

    @abstractmethod
    def get_original(self, key: str) -> bytes:
        """Return the exact original bytes for ``key``, re-verifying their digest."""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """True if an original is stored under ``key``."""


class TempDirStorage(OriginalDocumentStorage):
    """CI/local-only implementation on a plain directory (see module docstring re B-001)."""

    def __init__(self, root: Path | str) -> None:
        self._originals = Path(root) / ORIGINALS_SUBDIR
        self._originals.mkdir(parents=True, exist_ok=True)

    def put_original(self, key: str, data: bytes) -> None:
        path = self._originals / _digest_hex_of(key)
        # Immutability is checked before the data digest: a second put under an
        # existing key is a T10 overwrite attempt regardless of what bytes it carries.
        if path.exists():
            raise ImmutableOriginalViolationError(
                "an original is already stored under this digest; originals are write-once",
                digest=key,
            )
        actual = _sha256_key(data)
        if actual != key:
            raise DigestMismatchError(
                "data does not hash to its digest key; nothing was stored",
                expected_digest=key,
                actual_digest=actual,
                size_bytes=len(data),
            )
        path.write_bytes(data)

    def get_original(self, key: str) -> bytes:
        path = self._originals / _digest_hex_of(key)
        if not path.is_file():
            raise OriginalNotFoundError(
                "no original is stored under this digest",
                digest=key,
            )
        data = path.read_bytes()
        actual = _sha256_key(data)
        if actual != key:
            raise DigestMismatchError(
                "stored bytes no longer hash to their digest key; original is corrupt",
                expected_digest=key,
                actual_digest=actual,
                size_bytes=len(data),
            )
        return data

    def exists(self, key: str) -> bool:
        return (self._originals / _digest_hex_of(key)).is_file()
