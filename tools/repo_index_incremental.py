#!/usr/bin/env python3
"""Incremental indexing on top of A1 (M0-T064 Unit A2, D-013-R032/R037/R079 et al.).

Two invariants govern this layer:

  * PARITY (load-bearing, D-013-R079/R037): the incremental export is
    BYTE-IDENTICAL to a clean full rebuild for the same snapshot and effective
    versions. Guaranteed by construction and proven by test against the REAL
    `code_graph.build_graph` (an independent reference), never by luck.
  * SELECTIVE REPARSE (D-013-R032/R059): on a local content edit only the
    changed files are reparsed (`ast.parse` / TS scan); a warm no-change run
    reparses zero files; a local change triggers no full rebuild. Delivered by
    `repo_index_assembly.drive`, which reuses per-file extraction *bundles* from
    the prior generation for every unchanged file and reassembles the exact
    generator output.

Rebuild taxonomy (recorded in each run's `mode`/`rebuild_reason`):
  * `reuse`       -- snapshot fingerprint already has a validated generation;
                     the exact prior bytes are returned (no parse at all).
  * `incremental` -- content-only edits; reparse only the changed files, reuse
                     the rest. The dominant "local change" case (D-013-R059).
  * `full`        -- a cold build, a structural change (add/delete/rename, which
                     alters the global resolution index or the schema-node set),
                     or a global invalidator (parser/config/schema/eligibility
                     version). Rebuilt via the same builder; still byte-identical.
                     A structural change is a documented invalidator of the
                     resolution index, so a full rebuild is the deterministically
                     safe closure (D-013-R032 "smallest deterministically proven
                     invalidation closure"); content edits take the minimal path.

Change classification (D-013): added / content_modified / metadata_modified /
deleted / renamed (a delete+add sharing a content digest), plus global
invalidators. mtime is never trusted (A1, D-013-R030). Every generation is
validated before promotion; a corrupt/stale/concurrent state is handled by the
A1 cache's fail-closed rules; retries are idempotent. A full rebuild via the real
generator always remains available as reference and recovery.
"""
from __future__ import annotations

import dataclasses
import json
import os
import pathlib
import sys
import time
from typing import Any

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools import repo_fingerprint as rf  # noqa: E402
from tools import repo_index_assembly as asm  # noqa: E402
from tools import repo_index_cache as ric  # noqa: E402
from tools.code_graph import generate as codegraph  # noqa: E402

INCREMENTAL_SCHEMA = "repo_index_incremental/v2"
RUN_RECORD_SCHEMA = "repo_index_runrecord/v1"
UNIT_ID = "M0-T064"
TELEMETRY_FILENAME = "incremental_telemetry.jsonl"

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

    def is_structural(self) -> bool:
        """A change that alters the global resolution index or schema-node set,
        so unchanged files' edges could re-resolve -> a full rebuild is required
        for a deterministically-safe (byte-identical) result."""
        return bool(self.added or self.deleted or self.renamed
                    or self.global_invalidators)

    def changed_paths(self) -> set[str]:
        paths = set(self.added) | set(self.content_modified) | set(self.deleted)
        for old, new in self.renamed:
            paths.add(old)
            paths.add(new)
        return paths

    def counts(self) -> dict[str, int]:
        return {
            "added": len(self.added),
            "content_modified": len(self.content_modified),
            "metadata_modified": len(self.metadata_modified),
            "deleted": len(self.deleted),
            "renamed": len(self.renamed),
            "global_invalidators": len(self.global_invalidators),
        }

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


def importer_closure(changed: set[str], bundles: dict[str, dict[str, Any]],
                     input_files: list[str]) -> set[str]:
    """Deterministic importer closure over the cached per-file extraction bundles:
    the changed files plus every file that imports (directly or transitively) a
    changed file. An internal import edge resolves `to` a target FILE path, so the
    reverse map is read straight from each bundle's `import_edges` -- the real
    graph shape, not a guessed one.
    """
    input_set = set(input_files)
    importers: dict[str, set[str]] = {}
    for rel, bundle in bundles.items():
        for e in bundle.get("import_edges", []):
            tgt = e.get("to")
            if tgt in input_set and tgt != rel:
                importers.setdefault(tgt, set()).add(rel)
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
    reused: bool                       # True = cache hit (no rebuild at all)
    mode: str                          # "reuse" | "incremental" | "full"
    rebuild_reason: str                # "" on reuse; else why/how it was built
    change_set: ChangeSet
    affected_files: list[str]
    files_parsed: int
    files_reused: int
    nodes_before: int
    edges_before: int
    nodes_after: int
    edges_after: int
    export_bytes: bytes               # the canonical index bytes (parity subject)
    telemetry: dict[str, Any]

    def export_digest(self) -> str:
        return rf.domain_hash("codegraph_export", self.export_bytes)


def _schema_content_changed(cs: ChangeSet) -> bool:
    def is_schema(p: str) -> bool:
        return (p.startswith(codegraph.SCHEMA_DIR_PREFIX)
                and p.endswith(codegraph.SCHEMA_SUFFIX))
    return any(is_schema(p) for p in cs.content_modified)


def _graph_counts(graph: dict[str, Any]) -> tuple[int, int]:
    return len(graph.get("nodes", [])), len(graph.get("edges", []))


def _payload_from_assembly(res: "asm.AssemblyResult",
                           fp: rf.FingerprintResult) -> dict[str, Any]:
    n, e = _graph_counts(res.graph)
    return {
        "export": res.export_bytes.decode("utf-8"),
        "manifest": fp.manifest_to_dict(),
        "config_versions": fp.config_versions,
        "input_files": res.input_files,
        "schema_nodes": res.schema_nodes,
        "bundles": res.bundles,
        "generator_identity": asm.generator_identity(),
        "counts": {"nodes": n, "edges": e},
    }


def _full_via_generator(root: pathlib.Path) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    """Fail-safe full build through the REAL generator (used only when the live
    generator is not the version the assembly replica verifies). No reusable
    bundles are produced, so the next build is also a full rebuild until the
    replica is updated -- correctness before speed."""
    graph, meta, input_files = codegraph.build_graph(str(root))
    export = codegraph.serialize(graph)
    n, e = _graph_counts(graph)
    payload = {
        "export": export.decode("utf-8"),
        "manifest": None,           # filled by caller (needs the fingerprint)
        "input_files": input_files,
        "generator_identity": asm.generator_identity(),
        "counts": {"nodes": n, "edges": e},
    }
    return export, payload, {"nodes": n, "edges": e}


def _fingerprint(root: pathlib.Path) -> rf.FingerprintResult:
    """A1's snapshot fingerprint, extended with the generator's CONFIG_INPUTS
    digest (e.g. apps/web/tsconfig.json). tsconfig steers TS alias resolution but
    is not an indexed file, so without this a tsconfig change would neither move
    the cache key nor register as an invalidator -- and a reused TS bundle would
    keep stale alias-resolved edges (byte divergence). Folding it in makes such a
    change a global invalidator that forces a full rebuild."""
    return rf.compute_fingerprint(
        root, config_versions={"codegraph_config_inputs":
                               asm.config_inputs_version(root)})


def build_incremental(repo_root: str | os.PathLike[str], *,
                      cache_base: str | os.PathLike[str] | None = None,
                      run_id: str | None = None,
                      persist_telemetry: bool = True,
                      ) -> IncrementalResult:
    """Build (or reuse) the index for the current snapshot, guaranteeing parity.

    Reuse when the snapshot fingerprint already has a validated generation;
    otherwise classify against the prior generation and either selectively
    reparse (content-only edits) or full-rebuild (structural / invalidator /
    cold / unknown-generator), always producing bytes byte-identical to a clean
    full rebuild.
    """
    root = pathlib.Path(repo_root).resolve()
    started = time.time()
    fp = _fingerprint(root)
    cache = ric.IndexCache(root, base=cache_base)
    cache.recover()

    # ---- cache hit: an already-validated generation for this exact snapshot ----
    hit = cache.load_fingerprint(fp.snapshot_fingerprint)
    if hit is not None:
        payload = hit.load_payload()
        export_bytes = payload["export"].encode("utf-8")
        n, e = (payload.get("counts", {}).get("nodes", 0),
                payload.get("counts", {}).get("edges", 0))
        res = IncrementalResult(
            schema=INCREMENTAL_SCHEMA, snapshot_fingerprint=fp.snapshot_fingerprint,
            reused=True, mode="reuse", rebuild_reason="",
            change_set=ChangeSet(), affected_files=[],
            files_parsed=0, files_reused=fp.census.indexed,
            nodes_before=n, edges_before=e, nodes_after=n, edges_after=e,
            export_bytes=export_bytes, telemetry={})
        return _finish(res, fp, cache, started, run_id, persist_telemetry)

    # ---- miss: classify against the previous current generation (if any) ----
    prior = cache.load_current()
    change_set = ChangeSet()
    prior_payload: dict[str, Any] | None = None
    prior_bundles: dict[str, dict[str, Any]] = {}
    nodes_before = edges_before = 0
    if prior is not None:
        prior_payload = prior.load_payload()
        # the stored manifest omits config_versions (kept as a sibling field);
        # merge it back so version invalidators are detected, not spuriously
        # fired against an empty prior version set.
        prior_manifest = dict(prior_payload.get("manifest") or {})
        prior_manifest.setdefault("config_versions",
                                  prior_payload.get("config_versions") or {})
        change_set = classify_changes(prior_manifest, fp)
        prior_bundles = prior_payload.get("bundles") or {}
        nodes_before = prior_payload.get("counts", {}).get("nodes", 0)
        edges_before = prior_payload.get("counts", {}).get("edges", 0)

    input_files_now = codegraph.scan_input_files(str(root))

    # ---- fast path: content-only edits, verified generator, reusable bundles ----
    can_incremental = (
        prior_payload is not None
        and asm.generator_recognized()
        and prior_payload.get("generator_identity") == asm.generator_identity()
        and bool(prior_bundles)
        and not change_set.is_structural()
        and not _schema_content_changed(change_set)
        and change_set.any_content_change()
        and input_files_now == prior_payload.get("input_files"))

    if can_incremental:
        changed = frozenset(change_set.content_modified)
        res_asm = asm.drive(
            root, prior_bundles=prior_bundles,
            prior_schema_nodes=prior_payload.get("schema_nodes"),
            changed=changed, input_files=input_files_now)
        export_bytes = res_asm.export_bytes
        affected = importer_closure(change_set.changed_paths(), prior_bundles,
                                    input_files_now)
        reason = (f"incremental: reparsed {res_asm.files_parsed} of "
                  f"{len(input_files_now)} files")
        payload = _payload_from_assembly(res_asm, fp)
        cache.write_generation(fp.snapshot_fingerprint, payload)
        n, e = _graph_counts(res_asm.graph)
        res = IncrementalResult(
            schema=INCREMENTAL_SCHEMA, snapshot_fingerprint=fp.snapshot_fingerprint,
            reused=False, mode="incremental", rebuild_reason=reason,
            change_set=change_set, affected_files=sorted(affected),
            files_parsed=res_asm.files_parsed, files_reused=res_asm.files_reused,
            nodes_before=nodes_before, edges_before=edges_before,
            nodes_after=n, edges_after=e,
            export_bytes=export_bytes, telemetry={})
        return _finish(res, fp, cache, started, run_id, persist_telemetry)

    # ---- full rebuild (cold / structural / invalidator / unknown generator) ----
    if not asm.generator_recognized():
        # the most actionable signal: an unrecognized generator disables every
        # future incremental build until the assembly replica is updated.
        reason = f"full: unrecognized generator {asm.generator_identity()}"
    elif prior_payload is None:
        reason = "full: cold build (no prior generation)"
    elif change_set.global_invalidators:
        reason = "full: global_invalidator: " + ", ".join(change_set.global_invalidators)
    elif change_set.is_structural():
        reason = ("full: structural change (add/delete/rename alters the "
                  "resolution index): " + json.dumps(change_set.counts(),
                                                      sort_keys=True))
    elif _schema_content_changed(change_set):
        reason = "full: schema-node set changed"
    else:
        reason = "full: rebuild"

    affected = (importer_closure(change_set.changed_paths(), prior_bundles,
                                 input_files_now) if prior_bundles else set())

    if asm.generator_recognized():
        res_asm = asm.drive(root)   # cold drive: byte-identical, yields bundles
        export_bytes = res_asm.export_bytes
        payload = _payload_from_assembly(res_asm, fp)
        files_parsed, files_reused = res_asm.files_parsed, res_asm.files_reused
        n, e = _graph_counts(res_asm.graph)
    else:
        export_bytes, payload, cnt = _full_via_generator(root)
        payload["manifest"] = fp.manifest_to_dict()
        payload["config_versions"] = fp.config_versions
        files_parsed, files_reused = fp.census.indexed, 0
        n, e = cnt["nodes"], cnt["edges"]

    cache.write_generation(fp.snapshot_fingerprint, payload)
    res = IncrementalResult(
        schema=INCREMENTAL_SCHEMA, snapshot_fingerprint=fp.snapshot_fingerprint,
        reused=False, mode="full", rebuild_reason=reason,
        change_set=change_set, affected_files=sorted(affected),
        files_parsed=files_parsed, files_reused=files_reused,
        nodes_before=nodes_before, edges_before=edges_before,
        nodes_after=n, edges_after=e,
        export_bytes=export_bytes, telemetry={})
    return _finish(res, fp, cache, started, run_id, persist_telemetry)


def clean_full_build_bytes(repo_root: str | os.PathLike[str]) -> bytes:
    """A clean full rebuild's canonical bytes via the REAL generator - the
    INDEPENDENT parity reference the incremental output must match."""
    graph, _, _ = codegraph.build_graph(str(pathlib.Path(repo_root).resolve()))
    return codegraph.serialize(graph)


# --------------------------------------------------------------------------
# run record (D-013-R024/R052) + external append-only telemetry (D-013-R050)
# --------------------------------------------------------------------------

def _run_record(res: IncrementalResult, fp: rf.FingerprintResult, *,
                run_id: str | None, elapsed_seconds: float) -> dict[str, Any]:
    """The minimum machine-readable run record (D-013-R024/R052). Deterministic
    content except `elapsed_seconds`, which is permitted ONLY in the external
    runtime record and never enters a byte-identity artifact. Redacted: identity
    is a sha, never an absolute path; no prompts/transcripts; bounded counts."""
    return {
        "schema": RUN_RECORD_SCHEMA,
        "run_id": run_id,
        "unit_id": UNIT_ID,
        "role": "orchestrator",
        "repo_identity": fp.checkout_identity,
        "head_sha": fp.head.sha,
        "branch": fp.head.branch,
        "head_detached": fp.head.is_detached,
        "dirty_state_digest": fp.dirty_state_digest,
        "source_manifest_digest": fp.source_manifest_digest,
        "snapshot_fingerprint": fp.snapshot_fingerprint,
        "versions": dict(sorted(fp.config_versions.items())),
        "generator_identity": asm.generator_identity(),
        "census": fp.census.to_dict(),
        "change_set": res.change_set.counts(),
        "mode": res.mode,
        "cache_result": "hit" if res.reused else "miss",
        "rebuild_reason": res.rebuild_reason,
        "files_examined": fp.census.eligible,
        "files_parsed": res.files_parsed,
        "files_reused": res.files_reused,
        "affected_dependents": len(res.affected_files),
        "graph_nodes_before": res.nodes_before,
        "graph_edges_before": res.edges_before,
        "graph_nodes_after": res.nodes_after,
        "graph_edges_after": res.edges_after,
        "export_digest": res.export_digest(),
        # measured-only fields are null when not applicable, NEVER fabricated:
        "estimated_tokens": None,
        "provider_tokens": None,
        "elapsed_seconds": elapsed_seconds,
    }


def append_run_record(record: dict[str, Any], cache: ric.IndexCache) -> pathlib.Path:
    """Append one redacted run record to the external, per-checkout, append-only
    JSONL telemetry log (D-013-R050). Lives outside the repo, never committed."""
    log = cache.root / TELEMETRY_FILENAME
    # Bounded/rotated retention (M0-T075, D-018-R036): the log stays outside
    # the repo and can no longer grow without bound.
    ric.append_jsonl_rotated(log, record)
    return log


def _finish(res: IncrementalResult, fp: rf.FingerprintResult,
            cache: ric.IndexCache, started: float, run_id: str | None,
            persist_telemetry: bool) -> IncrementalResult:
    record = _run_record(res, fp, run_id=run_id,
                         elapsed_seconds=time.time() - started)
    res.telemetry = record
    if persist_telemetry:
        try:
            append_run_record(record, cache)
        except OSError:
            pass  # telemetry is best-effort; a build never fails on logging
    # REAL bounded generation retention (M0-T075, D-018-R035): keep the current
    # generation plus rollback generations; best-effort, never fails a build.
    try:
        cache.prune(keep=3)
    except (OSError, ric.CacheError):
        pass
    return res


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=str(pathlib.Path.cwd()))
    ap.add_argument("--cache-base", default=None)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--no-telemetry", action="store_true")
    args = ap.parse_args()
    r = build_incremental(args.repo, cache_base=args.cache_base,
                          run_id=args.run_id,
                          persist_telemetry=not args.no_telemetry)
    print(json.dumps({
        "snapshot_fingerprint": r.snapshot_fingerprint,
        "mode": r.mode, "reused": r.reused, "rebuild_reason": r.rebuild_reason,
        "export_digest": r.export_digest(),
        "files_parsed": r.files_parsed, "files_reused": r.files_reused,
        "change_set": r.change_set.to_dict(),
        "affected_files": len(r.affected_files),
        "graph": {"nodes": r.nodes_after, "edges": r.edges_after},
        "telemetry": r.telemetry,
    }, indent=2))
