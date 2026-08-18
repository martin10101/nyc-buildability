#!/usr/bin/env python3
"""Incremental indexing on top of A1 (M0-T064 Unit A2, D-013-R037/R079 et al.).

The parity invariant is the load-bearing contract: the incremental build's
exported bytes are BYTE-IDENTICAL to a clean full rebuild for the same snapshot
and effective versions (D-013-R079; enforced by test). It is guaranteed by
construction, not by luck:

  * the snapshot fingerprint (A1) always hashes file CONTENT - mtime is never
    trusted (D-013-R030), so the reuse decision can never be fooled by a
    restored mtime;
  * on an UNCHANGED snapshot the validated cached generation is returned
    verbatim - the exact bytes of a prior full build (cache hit; the win is
    skipping the expensive parse/resolve, not re-serializing);
  * on a CHANGED snapshot the index is produced by the SAME full builder
    (`code_graph.build_graph`) the clean rebuild uses, so the output matches by
    construction; the incremental layer additionally derives the exact change
    set and the deterministically affected importer closure and reports them
    (telemetry + future partial-parse optimization), and forces a full rebuild
    on any GLOBAL invalidator (parser/config/schema/eligibility change) with a
    recorded reason.

Change classification (D-013): added / content_modified / metadata_modified /
deleted / renamed (a delete+add sharing a content digest), plus global
invalidators. Every generation is validated before promotion; a corrupt/stale/
concurrent state is handled by the A1 cache's fail-closed rules; retries are
idempotent. A full rebuild always remains available as reference and recovery.
"""
from __future__ import annotations

import dataclasses
import os
import pathlib
import sys
import time
from typing import Any

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools import repo_fingerprint as rf  # noqa: E402
from tools import repo_index_cache as ric  # noqa: E402
from tools.code_graph import generate as codegraph  # noqa: E402

INCREMENTAL_SCHEMA = "repo_index_incremental/v1"

# Change classes (D-013).
ADDED = "added"
CONTENT_MODIFIED = "content_modified"
METADATA_MODIFIED = "metadata_modified"
DELETED = "deleted"
RENAMED = "renamed"


@dataclasses.dataclass
class ChangeSet:
    added: list[str] = dataclasses.field(default_factory=list)
    content_modified: list[str] = dataclasses.field(default_factory=list)
    metadata_modified: list[str] = dataclasses.field(default_factory=list)
    deleted: list[str] = dataclasses.field(default_factory=list)
    renamed: list[tuple[str, str]] = dataclasses.field(default_factory=list)
    global_invalidators: list[str] = dataclasses.field(default_factory=list)

    def any_content_change(self) -> bool:
        return bool(self.added or self.content_modified or self.deleted
                    or self.renamed or self.global_invalidators)

    def changed_paths(self) -> set[str]:
        paths = set(self.added) | set(self.content_modified) | set(self.deleted)
        for old, new in self.renamed:
            paths.add(old)
            paths.add(new)
        return paths

    def to_dict(self) -> dict[str, Any]:
        return {
            "added": sorted(self.added),
            "content_modified": sorted(self.content_modified),
            "metadata_modified": sorted(self.metadata_modified),
            "deleted": sorted(self.deleted),
            "renamed": sorted(self.renamed),
            "global_invalidators": sorted(self.global_invalidators),
        }


def _manifest_index(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {e["path"]: e for e in entries}


def classify_changes(prior_manifest: dict[str, Any],
                     current: rf.FingerprintResult) -> ChangeSet:
    """Derive the exact change set between a cached manifest and the current one.

    `metadata_modified` = same content digest, different parse-relevant mode
    (e.g. symlink flag / case). `renamed` = a deleted path and an added path that
    share a raw content digest (deterministic pairing by sorted content digest).
    Global invalidators (parser/config/schema/eligibility version change) are
    detected from the config-version set and force a full rebuild.
    """
    prior_files = _manifest_index(prior_manifest.get("files", []))
    cur_files = _manifest_index([e.to_dict() for e in current.file_manifest])

    cs = ChangeSet()
    # global invalidators: any config version that changed
    prior_versions = prior_manifest.get("config_versions", {})
    for key, val in current.config_versions.items():
        if prior_versions.get(key) != val:
            cs.global_invalidators.append(f"{key}:{prior_versions.get(key)}->{val}")

    prior_paths = set(prior_files)
    cur_paths = set(cur_files)
    for path in sorted(cur_paths - prior_paths):
        cs.added.append(path)
    for path in sorted(prior_paths - cur_paths):
        cs.deleted.append(path)
    for path in sorted(cur_paths & prior_paths):
        p, c = prior_files[path], cur_files[path]
        if p.get("raw_digest") != c.get("raw_digest"):
            cs.content_modified.append(path)
        elif p.get("mode") != c.get("mode"):
            cs.metadata_modified.append(path)

    # rename detection: pair a deleted + added with the same raw content digest
    del_by_digest: dict[str, list[str]] = {}
    for path in cs.deleted:
        del_by_digest.setdefault(prior_files[path]["raw_digest"], []).append(path)
    renamed_added: set[str] = set()
    renamed_deleted: set[str] = set()
    for path in cs.added:
        digest = cur_files[path]["raw_digest"]
        candidates = del_by_digest.get(digest)
        if candidates:
            old = sorted(candidates)[0]
            if old not in renamed_deleted:
                cs.renamed.append((old, path))
                renamed_added.add(path)
                renamed_deleted.add(old)
    cs.added = [p for p in cs.added if p not in renamed_added]
    cs.deleted = [p for p in cs.deleted if p not in renamed_deleted]
    return cs


def affected_closure(changed: set[str], graph: dict[str, Any]) -> set[str]:
    """Deterministic importer closure: the changed files plus every file that,
    per the cached code-graph edges, imports (directly or transitively) a
    changed file. Used to report the minimal re-index scope (D-013).
    """
    # Build a reverse edge map: target-file -> {source-files that depend on it}.
    node_file = {n.get("id"): n.get("file") for n in graph.get("nodes", [])
                 if n.get("file")}
    importers: dict[str, set[str]] = {}
    for e in graph.get("edges", []):
        src_file = node_file.get(e.get("source"))
        dst_file = node_file.get(e.get("target"))
        if src_file and dst_file and src_file != dst_file:
            importers.setdefault(dst_file, set()).add(src_file)
    closure = set(changed)
    frontier = set(changed)
    while frontier:
        nxt: set[str] = set()
        for f in frontier:
            for dep in importers.get(f, ()):
                if dep not in closure:
                    closure.add(dep)
                    nxt.add(dep)
        frontier = nxt
    return closure


@dataclasses.dataclass
class IncrementalResult:
    schema: str
    snapshot_fingerprint: str
    reused: bool                       # True = cache hit (no rebuild)
    rebuild_reason: str                # "" on reuse; else why a full build ran
    change_set: ChangeSet
    affected_files: list[str]
    export_bytes: bytes               # the canonical index bytes (parity subject)
    telemetry: dict[str, Any]

    def export_digest(self) -> str:
        return rf.domain_hash("codegraph_export", self.export_bytes)


def _full_build_bytes(repo_root: pathlib.Path) -> tuple[bytes, dict[str, Any]]:
    graph, meta, _ = codegraph.build_graph(str(repo_root))
    return codegraph.serialize(graph), {"graph": graph, "meta": meta}


def build_incremental(repo_root: str | os.PathLike[str], *,
                      cache_base: str | os.PathLike[str] | None = None,
                      ) -> IncrementalResult:
    """Build (or reuse) the index for the current snapshot, guaranteeing parity.

    Returns the canonical export bytes plus a run record. Reuse when the current
    snapshot fingerprint already has a validated cached generation; otherwise a
    full rebuild (parity-safe), with the change set + affected closure computed
    from the prior generation when one exists.
    """
    root = pathlib.Path(repo_root).resolve()
    started = time.time()
    fp = rf.compute_fingerprint(root)
    cache = ric.IndexCache(root, base=cache_base)
    cache.recover()

    # cache hit: an already-validated generation for this exact snapshot
    hit = cache.load_fingerprint(fp.snapshot_fingerprint)
    if hit is not None:
        payload = hit.load_payload()
        export_bytes = payload["export"].encode("utf-8")
        return IncrementalResult(
            schema=INCREMENTAL_SCHEMA,
            snapshot_fingerprint=fp.snapshot_fingerprint,
            reused=True, rebuild_reason="",
            change_set=ChangeSet(), affected_files=[],
            export_bytes=export_bytes,
            telemetry=_telemetry(fp, reused=True, reason="",
                                 files_hashed=fp.census.indexed,
                                 files_parsed=0, files_reused=fp.census.indexed,
                                 affected=0, elapsed=time.time() - started))

    # miss: classify against the previous current generation (if any), rebuild
    prior = cache.load_current()
    change_set = ChangeSet()
    affected: set[str] = set()
    if prior is not None:
        prior_payload = prior.load_payload()
        prior_manifest = prior_payload.get("manifest", {})
        change_set = classify_changes(prior_manifest, fp)
        prior_graph = prior_payload.get("graph", {"nodes": [], "edges": []})
        affected = affected_closure(change_set.changed_paths(), prior_graph)
        reason = ("global_invalidator: " + ", ".join(change_set.global_invalidators)
                  if change_set.global_invalidators
                  else f"content_change: {len(change_set.changed_paths())} files")
    else:
        reason = "cold_build: no prior generation"

    export_bytes, built = _full_build_bytes(root)
    payload = {
        "export": export_bytes.decode("utf-8"),
        "manifest": fp.manifest_to_dict(),
        "config_versions": fp.config_versions,
        "graph": built["graph"],
    }
    cache.write_generation(fp.snapshot_fingerprint, payload)
    return IncrementalResult(
        schema=INCREMENTAL_SCHEMA,
        snapshot_fingerprint=fp.snapshot_fingerprint,
        reused=False, rebuild_reason=reason,
        change_set=change_set, affected_files=sorted(affected),
        export_bytes=export_bytes,
        telemetry=_telemetry(fp, reused=False, reason=reason,
                             files_hashed=fp.census.indexed,
                             files_parsed=fp.census.indexed,
                             files_reused=0, affected=len(affected),
                             elapsed=time.time() - started))


def clean_full_build_bytes(repo_root: str | os.PathLike[str]) -> bytes:
    """A clean full rebuild's canonical bytes - the parity reference."""
    return _full_build_bytes(pathlib.Path(repo_root).resolve())[0]


def _telemetry(fp: rf.FingerprintResult, *, reused: bool, reason: str,
               files_hashed: int, files_parsed: int, files_reused: int,
               affected: int, elapsed: float) -> dict[str, Any]:
    return {
        "schema": INCREMENTAL_SCHEMA,
        "snapshot_fingerprint": fp.snapshot_fingerprint,
        "cache_result": "hit" if reused else "miss",
        "rebuild_reason": reason,
        "files_examined": fp.census.eligible,
        "files_hashed": files_hashed,
        "files_parsed": files_parsed,
        "files_reused": files_reused,
        "affected_dependents": affected,
        "elapsed_seconds": elapsed,
        # provider/token measures are not applicable to a deterministic build:
        "estimated_tokens": None,
    }


if __name__ == "__main__":
    import argparse
    import json
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=str(pathlib.Path.cwd()))
    ap.add_argument("--cache-base", default=None)
    args = ap.parse_args()
    r = build_incremental(args.repo, cache_base=args.cache_base)
    print(json.dumps({
        "snapshot_fingerprint": r.snapshot_fingerprint,
        "reused": r.reused, "rebuild_reason": r.rebuild_reason,
        "export_digest": r.export_digest(),
        "change_set": r.change_set.to_dict(),
        "affected_files": len(r.affected_files),
        "telemetry": r.telemetry,
    }, indent=2))
