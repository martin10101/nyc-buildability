#!/usr/bin/env python3
"""Repository fingerprint + per-file source manifest (M0-T063 Unit A1, D-013).

The ONE reusable deterministic fingerprint service (D-013-R026): every other
context-intelligence layer derives its cache keys and staleness checks from
here, never inventing a per-feature digest.

What it produces, deterministically for a given (checkout, snapshot, versions):
  * a stable, versioned CHECKOUT IDENTITY (the accepted canonical-path sha256,
    reused from the supervisor's durable_state - never the folder basename;
    D-013-R027/R078);
  * a per-file SOURCE MANIFEST over the accepted code-graph eligibility roots
    (reused from tools/code_graph; census is NOT widened - D-013-R081), each
    entry carrying a domain-separated content digest and parse-relevant mode
    metadata;
  * a SNAPSHOT FINGERPRINT binding committed AND uncommitted state, HEAD, the
    dirty-state digest, and every version input that changes downstream output
    (D-013-R028);
  * complete CENSUS accounting: eligible / indexed / excluded (grouped reason) /
    failed (grouped reason) / stale (D-013-R023/R024/R025).

Invariants:
  * Canonical serialization: sorted keys, explicit UTF-8, domain-separated
    hashes (D-013-R029). No wall-clock enters any digest.
  * mtime is NEVER proof of unchanged content - it is at most a fast precheck
    followed by a content-digest rule (D-013-R030); this module always hashes
    content and never trusts mtime.
  * An unreadable eligible file is a recorded FAILURE, never a silent skip
    (D-013-R029).
  * Symlinks are recorded and classified, not blindly followed.
"""
from __future__ import annotations

import dataclasses
import hashlib
import os
import pathlib
import subprocess
import unicodedata
from typing import Any

_REPO_TOOLS = pathlib.Path(__file__).resolve().parent
import sys
if str(_REPO_TOOLS.parent) not in sys.path:
    sys.path.insert(0, str(_REPO_TOOLS.parent))

from tools.agent_supervisor.durable_state import (  # noqa: E402
    canonical_checkout_path, checkout_key)
from tools.code_graph import generate as codegraph  # noqa: E402

#: Bumped when this module changes how it hashes or serializes - so a fingerprint
#: produced by an older indexer is detectably incompatible (D-013-R028).
FINGERPRINT_VERSION = "1.0.0"
#: Version of the eligibility/exclusion ruleset (mirrors the accepted code-graph
#: roots; a change here is a fingerprint input, D-013-R028).
ELIGIBILITY_VERSION = "codegraph-1.0.0"

#: The repo identity namespace - a stable label, never the basename. The value
#: is the canonical-path sha256; this string only disambiguates what the hash is.
REPO_IDENTITY_NAMESPACE = "nyc-buildability"


class FingerprintError(Exception):
    """A fingerprint could not be computed (fail closed)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# Domain-separated hashing and canonical serialization (D-013-R029)
# --------------------------------------------------------------------------

def domain_hash(domain: str, *parts: bytes) -> str:
    """SHA-256 over a domain tag then each length-prefixed part.

    Domain separation means a file-content digest can never collide with a
    manifest digest or a path digest even on identical bytes: the domain tag and
    the explicit length framing make the pre-image unambiguous.
    """
    h = hashlib.sha256()
    h.update(domain.encode("utf-8"))
    h.update(b"\x00")
    for part in parts:
        h.update(len(part).to_bytes(8, "big"))
        h.update(part)
    return h.hexdigest()


def canonical_json(obj: Any) -> bytes:
    """Deterministic UTF-8 JSON: sorted keys, no whitespace drift, explicit
    encoding. Used for every digested structure so the bytes are reproducible
    across platforms and Python builds."""
    import json
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("utf-8")


# --------------------------------------------------------------------------
# Git-derived snapshot state
# --------------------------------------------------------------------------

def _git(repo_root: pathlib.Path, *args: str) -> str:
    try:
        out = subprocess.run(["git", "-C", str(repo_root), *args],
                             capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, OSError) as exc:
        raise FingerprintError("git_failed",
                               f"git {' '.join(args)} in {repo_root}: {exc}") from exc
    return out.stdout


@dataclasses.dataclass(frozen=True)
class HeadIdentity:
    sha: str
    branch: str          # symbolic ref short name, or "DETACHED"
    is_detached: bool


def head_identity(repo_root: pathlib.Path) -> HeadIdentity:
    sha = _git(repo_root, "rev-parse", "HEAD").strip()
    ref = _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    detached = ref == "HEAD"
    return HeadIdentity(sha=sha, branch=("DETACHED" if detached else ref),
                        is_detached=detached)


def tracked_files(repo_root: pathlib.Path) -> set[str]:
    """Repo-relative posix paths git currently tracks (committed + staged)."""
    out = _git(repo_root, "ls-files", "-z")
    return {p for p in out.split("\0") if p}


def dirty_paths(repo_root: pathlib.Path) -> dict[str, str]:
    """Repo-relative posix path -> two-char porcelain status for every path with
    a working-tree or index difference (added/modified/deleted/renamed/untracked).
    This is the uncommitted-state input the snapshot fingerprint binds so HEAD
    alone can never stand in for the working tree (D-013-R028)."""
    out = _git(repo_root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    result: dict[str, str] = {}
    tokens = out.split("\0")
    i = 0
    while i < len(tokens):
        entry = tokens[i]
        if not entry:
            i += 1
            continue
        status, path = entry[:2], entry[3:]
        result[path] = status
        # A rename/copy porcelain record is followed by the original path token.
        if status and status[0] in ("R", "C"):
            i += 2
        else:
            i += 1
    return result


# --------------------------------------------------------------------------
# Eligibility + per-file manifest
# --------------------------------------------------------------------------

# Deterministic exclusion reasons, grouped in the census (D-013-R024).
EXCLUDED_UNTRACKED = "untracked"          # eligible pattern but not git-tracked
FAILED_UNREADABLE = "unreadable"
FAILED_SYMLINK_LOOP = "symlink_unresolved"


def eligible_files(repo_root: pathlib.Path) -> list[str]:
    """Accepted code-graph eligible set, sorted. Not widened (D-013-R081)."""
    return sorted(codegraph.scan_input_files(str(repo_root)))


def _file_mode_metadata(abs_path: pathlib.Path) -> dict[str, Any]:
    """Parse-relevant, content-independent metadata (never mtime)."""
    is_symlink = abs_path.is_symlink()
    return {
        "is_symlink": is_symlink,
        # case-fold + Unicode-NFC of the basename, so a case-only or
        # normalization-only rename is a detectable manifest change on any FS.
        "name_nfc": unicodedata.normalize("NFC", abs_path.name),
        "name_casefold": unicodedata.normalize("NFC", abs_path.name).casefold(),
    }


def _hash_content(abs_path: pathlib.Path) -> tuple[str, str]:
    """(raw_digest, lf_digest) for a file's bytes.

    raw_digest is over exact bytes (catches any change incl. line endings).
    lf_digest normalizes CRLF->LF so a pure line-ending flip is distinguishable
    from a content change - both are recorded; downstream decides which it needs.
    Never trusts mtime; always reads bytes (D-013-R030).
    """
    data = abs_path.read_bytes()
    raw = domain_hash("file.raw", data)
    lf = domain_hash("file.lf", data.replace(b"\r\n", b"\n"))
    return raw, lf


@dataclasses.dataclass
class Census:
    eligible: int = 0
    indexed: int = 0
    excluded: dict[str, int] = dataclasses.field(default_factory=dict)
    failed: dict[str, int] = dataclasses.field(default_factory=dict)
    stale: int = 0

    def add_excluded(self, reason: str) -> None:
        self.excluded[reason] = self.excluded.get(reason, 0) + 1

    def add_failed(self, reason: str) -> None:
        self.failed[reason] = self.failed.get(reason, 0) + 1

    def reconciles(self) -> bool:
        """indexed + sum(excluded) + sum(failed) == eligible (D-013 AS-2)."""
        return (self.indexed + sum(self.excluded.values())
                + sum(self.failed.values())) == self.eligible

    def to_dict(self) -> dict[str, Any]:
        return {
            "eligible": self.eligible, "indexed": self.indexed,
            "excluded": dict(sorted(self.excluded.items())),
            "failed": dict(sorted(self.failed.items())),
            "stale": self.stale, "reconciles": self.reconciles(),
        }


@dataclasses.dataclass
class FileEntry:
    path: str                 # repo-relative posix
    raw_digest: str
    lf_digest: str
    size: int
    mode: dict[str, Any]
    tracked: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path, "raw_digest": self.raw_digest,
            "lf_digest": self.lf_digest, "size": self.size,
            "mode": self.mode, "tracked": self.tracked,
        }


@dataclasses.dataclass
class FingerprintResult:
    checkout_identity: str            # sha256 of canonical checkout path
    checkout_path_namespace: str      # the identity namespace label
    head: HeadIdentity
    dirty_state_digest: str
    config_versions: dict[str, str]
    file_manifest: list[FileEntry]
    source_manifest_digest: str
    snapshot_fingerprint: str
    census: Census
    failures: list[dict[str, str]]    # per-file failure records (never silent)

    def to_dict(self) -> dict[str, Any]:
        return {
            "fingerprint_version": FINGERPRINT_VERSION,
            "repo_identity_namespace": self.checkout_path_namespace,
            "checkout_identity": self.checkout_identity,
            "head": {"sha": self.head.sha, "branch": self.head.branch,
                     "detached": self.head.is_detached},
            "dirty_state_digest": self.dirty_state_digest,
            "config_versions": dict(sorted(self.config_versions.items())),
            "source_manifest_digest": self.source_manifest_digest,
            "snapshot_fingerprint": self.snapshot_fingerprint,
            "census": self.census.to_dict(),
            "failures": self.failures,
            "file_count": len(self.file_manifest),
        }

    def manifest_to_dict(self) -> dict[str, Any]:
        """The full per-file manifest (large; separate from the summary)."""
        return {
            "fingerprint_version": FINGERPRINT_VERSION,
            "checkout_identity": self.checkout_identity,
            "snapshot_fingerprint": self.snapshot_fingerprint,
            "files": [e.to_dict() for e in self.file_manifest],
        }


def default_config_versions() -> dict[str, str]:
    """The version inputs that change downstream output; each is a fingerprint
    component so a parser/schema/eligibility bump invalidates caches (R028)."""
    return {
        "fingerprint": FINGERPRINT_VERSION,
        "eligibility": ELIGIBILITY_VERSION,
        "codegraph_schema": codegraph.SCHEMA_VERSION,
    }


def compute_fingerprint(
    repo_root: str | os.PathLike[str],
    *,
    config_versions: dict[str, str] | None = None,
) -> FingerprintResult:
    """Compute the snapshot fingerprint + per-file manifest + census.

    Deterministic for a fixed (checkout content, HEAD, dirty state, versions):
    the same inputs always produce the same snapshot_fingerprint, and any single
    changed input (one file byte, a config version, the dirty state) moves it
    (D-013 AS-1).
    """
    root = pathlib.Path(repo_root).resolve()
    if not (root / ".git").exists():
        raise FingerprintError("not_a_repo", f"{root} is not a git work tree")
    versions = dict(default_config_versions())
    if config_versions:
        versions.update(config_versions)

    identity = checkout_key(root)
    head = head_identity(root)
    tracked = tracked_files(root)
    dirty = dirty_paths(root)

    # Dirty-state digest: the sorted (path,status) set, domain-separated. HEAD +
    # this digest together pin committed AND uncommitted state (R028).
    dirty_digest = domain_hash(
        "dirty", canonical_json(sorted(dirty.items())))

    census = Census()
    entries: list[FileEntry] = []
    failures: list[dict[str, str]] = []

    for rel in eligible_files(root):
        census.eligible += 1
        abs_path = root / rel
        if not abs_path.exists():
            # Eligible per the walk but vanished (race / deleted): a failure,
            # never a silent skip.
            census.add_failed(FAILED_UNREADABLE)
            failures.append({"path": rel, "reason": FAILED_UNREADABLE,
                             "detail": "eligible file not present at hash time"})
            continue
        try:
            mode = _file_mode_metadata(abs_path)
            if mode["is_symlink"] and not abs_path.resolve().exists():
                census.add_failed(FAILED_SYMLINK_LOOP)
                failures.append({"path": rel, "reason": FAILED_SYMLINK_LOOP,
                                 "detail": "symlink does not resolve"})
                continue
            raw, lf = _hash_content(abs_path)
            size = abs_path.stat().st_size
        except OSError as exc:
            census.add_failed(FAILED_UNREADABLE)
            failures.append({"path": rel, "reason": FAILED_UNREADABLE,
                             "detail": exc.__class__.__name__})
            continue
        # MAJOR-1 fix (G3 review): the accepted code-graph generator indexes
        # EVERY filesystem-eligible file, tracked or not. The fingerprint must
        # hash the same set so `snapshot_fingerprint` uniquely determines the
        # generator's output - otherwise a modified-but-untracked source would
        # collide on the fingerprint and A2 would serve a stale index. `tracked`
        # is recorded as metadata (informational + census), never an exclusion;
        # the git dirty-state digest separately binds the uncommitted status.
        entries.append(FileEntry(path=rel, raw_digest=raw, lf_digest=lf,
                                 size=size, mode=mode, tracked=(rel in tracked)))
        census.indexed += 1

    entries.sort(key=lambda e: e.path)
    source_manifest_digest = domain_hash(
        "source_manifest",
        canonical_json([e.to_dict() for e in entries]))

    snapshot_fingerprint = domain_hash(
        "snapshot",
        canonical_json({
            "repo_identity_namespace": REPO_IDENTITY_NAMESPACE,
            "checkout_identity": identity,
            "head_sha": head.sha,
            "head_branch": head.branch,
            "head_detached": head.is_detached,
            "dirty_state_digest": dirty_digest,
            "config_versions": dict(sorted(versions.items())),
            "source_manifest_digest": source_manifest_digest,
        }))

    return FingerprintResult(
        checkout_identity=identity,
        checkout_path_namespace=REPO_IDENTITY_NAMESPACE,
        head=head,
        dirty_state_digest=dirty_digest,
        config_versions=versions,
        file_manifest=entries,
        source_manifest_digest=source_manifest_digest,
        snapshot_fingerprint=snapshot_fingerprint,
        census=census,
        failures=failures,
    )


def canonical_checkout(repo_root: str | os.PathLike[str]) -> str:
    """Public re-export of the accepted canonical checkout path (read-only use of
    the supervisor convention; D-013-R027/R078)."""
    return canonical_checkout_path(repo_root)


if __name__ == "__main__":
    import json
    result = compute_fingerprint(pathlib.Path.cwd())
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
