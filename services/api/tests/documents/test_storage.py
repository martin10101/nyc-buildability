"""Unit tests for the immutable original-document storage abstraction (M2-T015 unit 3c).

Proves, against docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md sections 6-7 and the
upload threat model:

1. put + get round-trips the EXACT original bytes under their ``sha256:`` digest key;
2. retrieval is digest-addressed: each stored original is fetched by its own digest,
   independent of insertion order, and the on-disk name is the digest hex — never a
   client-supplied filename (threat T07);
3. originals are write-once: a second ``put_original`` under an existing key — with
   identical OR different bytes — raises the typed ``ImmutableOriginalViolationError``
   (threat T10) and leaves the stored bytes untouched;
4. ``get_original`` for an unknown digest raises the typed ``OriginalNotFoundError``;
5. every read re-hashes the stored bytes and raises the typed ``DigestMismatchError``
   on tamper/corruption (architecture section 6 — never silent, never auto-repair);
6. malformed digest keys (wrong prefix, uppercase, wrong length, traversal shapes)
   are refused with the typed ``InvalidDigestKeyError`` before any filesystem
   interaction, and typed-error payloads carry metadata only — never document bytes.

Stdlib + pytest ``tmp_path`` only; no bucket, credentials, or network (B-001).
"""

from __future__ import annotations

import hashlib

import pytest

from app.documents.errors import (
    DigestMismatchError,
    DocumentIngestionError,
    ImmutableOriginalViolationError,
    InvalidDigestKeyError,
    OriginalNotFoundError,
    StorageIntegrityError,
)
from app.documents.storage import (
    ORIGINALS_SUBDIR,
    OriginalDocumentStorage,
    TempDirStorage,
)

PDF_BYTES = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n%%EOF\n"
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


def digest_of(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


@pytest.fixture()
def store(tmp_path) -> TempDirStorage:
    return TempDirStorage(tmp_path)


# ------------------------------------------------------------------ round trip


def test_put_get_round_trip_exact_bytes(store: TempDirStorage) -> None:
    key = digest_of(PDF_BYTES)
    assert not store.exists(key)
    store.put_original(key, PDF_BYTES)
    assert store.exists(key)
    assert store.get_original(key) == PDF_BYTES


def test_storage_is_digest_addressed_not_filename_addressed(
    store: TempDirStorage, tmp_path
) -> None:
    key_pdf, key_png = digest_of(PDF_BYTES), digest_of(PNG_BYTES)
    store.put_original(key_pdf, PDF_BYTES)
    store.put_original(key_png, PNG_BYTES)
    # Each original comes back under its own digest, regardless of insertion order.
    assert store.get_original(key_png) == PNG_BYTES
    assert store.get_original(key_pdf) == PDF_BYTES
    # On-disk names are the digest hex only — no client filename ever becomes a path.
    names = sorted(p.name for p in (tmp_path / ORIGINALS_SUBDIR).iterdir())
    assert names == sorted(k.split(":", 1)[1] for k in (key_pdf, key_png))


def test_empty_original_round_trips(store: TempDirStorage) -> None:
    key = digest_of(b"")
    store.put_original(key, b"")
    assert store.get_original(key) == b""


# ------------------------------------------------------------------- write-once


def test_overwrite_existing_key_raises_typed_error(store: TempDirStorage) -> None:
    key = digest_of(PDF_BYTES)
    store.put_original(key, PDF_BYTES)
    # Identical bytes: still refused — write-once means no second write path at all.
    with pytest.raises(ImmutableOriginalViolationError) as excinfo:
        store.put_original(key, PDF_BYTES)
    assert excinfo.value.reject_code == "immutable_original_violation"
    # Different bytes under the same key (T10 tamper shape): refused, store untouched.
    with pytest.raises(ImmutableOriginalViolationError):
        store.put_original(key, b"attacker replacement bytes")
    assert store.get_original(key) == PDF_BYTES


def test_put_refuses_data_that_does_not_hash_to_key(store: TempDirStorage) -> None:
    key = digest_of(PDF_BYTES)
    with pytest.raises(DigestMismatchError):
        store.put_original(key, PNG_BYTES)
    assert not store.exists(key)  # nothing admitted under a lying key


# -------------------------------------------------------------- unknown digest


def test_get_unknown_digest_raises_typed_error(store: TempDirStorage) -> None:
    key = digest_of(b"never stored")
    assert not store.exists(key)
    with pytest.raises(OriginalNotFoundError) as excinfo:
        store.get_original(key)
    assert excinfo.value.reject_code == "original_not_found"
    assert excinfo.value.payload.get("digest") == key


# -------------------------------------------------------- read verifies digest


def test_read_verifies_digest_and_raises_on_corruption(
    store: TempDirStorage, tmp_path
) -> None:
    key = digest_of(PDF_BYTES)
    store.put_original(key, PDF_BYTES)
    stored_file = tmp_path / ORIGINALS_SUBDIR / key.split(":", 1)[1]
    stored_file.write_bytes(b"corrupted on disk")
    with pytest.raises(DigestMismatchError) as excinfo:
        store.get_original(key)
    err = excinfo.value
    assert err.reject_code == "digest_mismatch"
    assert isinstance(err, StorageIntegrityError)
    # Payload is metadata only: digests, never the document bytes.
    payload_text = repr(err.to_payload())
    assert "corrupted on disk" not in payload_text
    assert err.payload["expected_digest"] == key


# ------------------------------------------------------------ digest-key guard


@pytest.mark.parametrize(
    "bad_key",
    [
        "",
        "deadbeef",
        "md5:" + "0" * 64,
        "sha256:" + "0" * 63,
        "sha256:" + "0" * 65,
        "sha256:" + "A" * 64,  # uppercase hex is not the wire format
        "sha256:../../etc/passwd",
        "sha256:..\\..\\windows\\system32",
    ],
)
def test_malformed_digest_keys_refused_before_filesystem(
    store: TempDirStorage, tmp_path, bad_key: str
) -> None:
    for op in (
        lambda: store.put_original(bad_key, b"x"),
        lambda: store.get_original(bad_key),
        lambda: store.exists(bad_key),
    ):
        with pytest.raises(InvalidDigestKeyError) as excinfo:
            op()
        assert excinfo.value.reject_code == "invalid_digest_key"
    # Refused before any filesystem interaction: the store root stayed empty.
    assert list((tmp_path / ORIGINALS_SUBDIR).iterdir()) == []


def test_typed_errors_are_ingestion_errors(store: TempDirStorage) -> None:
    assert isinstance(store, OriginalDocumentStorage)
    for exc in (
        ImmutableOriginalViolationError,
        OriginalNotFoundError,
        DigestMismatchError,
        InvalidDigestKeyError,
    ):
        assert issubclass(exc, DocumentIngestionError)
