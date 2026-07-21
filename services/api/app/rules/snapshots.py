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
from dataclasses import dataclass
from pathlib import Path

# docs/research/zr-snapshots/v1 resolved relative to the repo root (this file is
# services/api/app/rules/snapshots.py -> parents[4] is the repo root).
_REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SNAPSHOT_DIR = _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"


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
