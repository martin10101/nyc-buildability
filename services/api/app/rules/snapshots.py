"""Section-level Zoning Resolution source snapshots (M4-T001).

A snapshot is a small, section-level extract of the official ZR captured with
the SAME provenance discipline the future M3 corpus will use: request URL,
retrieval timestamp, the section's own ``Last Amended`` date, a document-currency
note, a verbatim excerpt, and a content digest. Snapshots live under
``docs/research/zr-snapshots/v1/`` (declared in docs/RULES_ENGINE_ARCHITECTURE.md)
so M3 can adopt the same layout rather than fight it.

Nothing here is a Verified legal statement. Snapshots carry an
``extraction_status`` and an explicit ``raw_html_verified`` flag; a snapshot
captured via AI-summarized markdown (not raw HTML bytes) is a *drafted
candidate* pending raw-HTML verification and G6 professional approval before any
rule citing it may be published.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

# PRODUCTION-SAFE default snapshot resolution (M4-T005 phase 2b).
#
# The canonical source of authority for the ZR section snapshots is
# ``docs/research/zr-snapshots/v1/*.snapshot.json`` (declared in
# docs/RULES_ENGINE_ARCHITECTURE.md). But the API is deployed/tested as an
# INSTALLED wheel (``pip install ./services/api`` in web-e2e CI and every
# production image), where ``app/`` lives in site-packages with NO sibling
# ``docs/`` directory. The former repo-relative
# ``Path(__file__).parents[4] / "docs/..."`` walk therefore resolved to a
# non-existent path and ``SnapshotStore.load`` raised ``SnapshotError`` on first
# use, 500-ing the rule-evaluation endpoint.
#
# So the snapshots are shipped as PACKAGE DATA under ``app/_zr_snapshots/v1/``
# (byte-identical build artifacts kept in sync by
# services/api/scripts/sync_zr_snapshots.py) and resolved via
# ``importlib.resources`` — which works identically from a source tree and from
# a non-editable install. We PREFER the packaged copy so source and installed
# behave identically, and fall back to the repo ``docs`` path for source-only
# runs where the bundle is somehow unavailable. An explicit
# ``SnapshotStore(directory=...)`` override (used throughout the test suite)
# bypasses this default entirely and is unaffected.
_PACKAGED_SNAPSHOT_PACKAGE = "app._zr_snapshots.v1"

# Repo docs source, relative to the repo root (this file is
# services/api/app/rules/snapshots.py -> parents[4] is the repo root). Kept as a
# fallback for source-only runs; NOT the primary resolution in an install.
_REPO_ROOT = Path(__file__).resolve().parents[4]
_DOCS_SNAPSHOT_DIR = _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"


def _resolve_default_snapshot_dir() -> Path:
    """Return the default snapshot directory, preferring the PACKAGED location
    (works in a non-editable install) and falling back to the repo docs source.

    ``importlib.resources.files`` on a normally-installed (unzipped) package —
    which is how the API wheel is installed (``pip install --no-deps .``) —
    yields a concrete filesystem path, so ``SnapshotStore``'s Path-based
    ``glob``/``is_dir`` continue to work unchanged. If the package is not
    importable, is not a real filesystem directory (e.g. a zipimport
    traversable), or carries no snapshot files, we fall back to the docs source.
    """
    try:
        packaged = resources.files(_PACKAGED_SNAPSHOT_PACKAGE)
        packaged_path = Path(os.fspath(packaged))
    except (ModuleNotFoundError, TypeError, ValueError, OSError):
        return _DOCS_SNAPSHOT_DIR
    if packaged_path.is_dir() and any(packaged_path.glob("*.snapshot.json")):
        return packaged_path
    return _DOCS_SNAPSHOT_DIR


DEFAULT_SNAPSHOT_DIR = _resolve_default_snapshot_dir()


class SnapshotError(RuntimeError):
    """Raised when a snapshot is missing, malformed, or fails digest check."""


@dataclass(frozen=True)
class SectionSnapshot:
    snapshot_id: str
    section_number: str
    section_title: str
    section_last_amended: str | None
    request_url: str
    retrieved_at: str
    raw_html_verified: bool
    extraction_status: str
    content_digest_sha256: str
    verbatim_excerpt: str
    document_currency_banner: str | None
    raw: dict

    def provenance(self) -> dict:
        """The immutable provenance block a citing rule/trace must carry. A
        material rule value can never be exported without this (PRD section 19):
        the evaluator refuses to build a result whose citation lacks it."""
        return {
            "snapshot_id": self.snapshot_id,
            "source_id": self.raw.get("source", {}).get("source_id"),
            "official_channel": self.raw.get("source", {}).get("official_channel"),
            "request_url": self.request_url,
            "retrieved_at": self.retrieved_at,
            "section_number": self.section_number,
            "section_title": self.section_title,
            "section_last_amended": self.section_last_amended,
            "document_currency_banner": self.document_currency_banner,
            "content_digest_sha256": self.content_digest_sha256,
            "raw_html_verified": self.raw_html_verified,
            "extraction_status": self.extraction_status,
        }


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_snapshot_file(path: Path) -> SectionSnapshot:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"snapshot {path} is unreadable: {exc}") from exc

    excerpt = raw.get("verbatim_excerpt")
    if not isinstance(excerpt, str) or not excerpt:
        raise SnapshotError(f"snapshot {path} has no verbatim_excerpt")
    stored = raw.get("content_digest_sha256")
    actual = _digest(excerpt)
    if stored != actual:
        # Tamper-evidence: the stored digest must match the excerpt bytes.
        raise SnapshotError(
            f"snapshot {raw.get('snapshot_id')}: content_digest_sha256 mismatch "
            f"(stored {stored!r} != sha256(excerpt) {actual!r})"
        )
    source = raw.get("source", {})
    return SectionSnapshot(
        snapshot_id=raw["snapshot_id"],
        section_number=raw.get("section_number", ""),
        section_title=raw.get("section_title", ""),
        section_last_amended=source.get("section_last_amended"),
        request_url=source.get("request_url", ""),
        retrieved_at=source.get("retrieved_at", ""),
        raw_html_verified=bool(source.get("raw_html_verified", False)),
        extraction_status=raw.get("extraction_status", "extracted_draft"),
        content_digest_sha256=actual,
        verbatim_excerpt=excerpt,
        document_currency_banner=source.get("document_currency_banner"),
        raw=raw,
    )


class SnapshotStore:
    """Loads and indexes every ``*.snapshot.json`` under a directory by id."""

    def __init__(self, directory: Path | None = None):
        self.directory = Path(directory) if directory else DEFAULT_SNAPSHOT_DIR
        self._by_id: dict[str, SectionSnapshot] = {}
        self._loaded = False

    def load(self) -> SnapshotStore:
        self._by_id.clear()
        if not self.directory.is_dir():
            raise SnapshotError(f"snapshot directory not found: {self.directory}")
        for path in sorted(self.directory.glob("*.snapshot.json")):
            snap = load_snapshot_file(path)
            if snap.snapshot_id in self._by_id:
                raise SnapshotError(f"duplicate snapshot_id {snap.snapshot_id!r}")
            self._by_id[snap.snapshot_id] = snap
        self._loaded = True
        return self

    def get(self, snapshot_id: str) -> SectionSnapshot:
        if not self._loaded:
            self.load()
        if snapshot_id not in self._by_id:
            raise SnapshotError(f"unknown snapshot_id {snapshot_id!r}")
        return self._by_id[snapshot_id]

    def ids(self) -> list[str]:
        if not self._loaded:
            self.load()
        return sorted(self._by_id)
