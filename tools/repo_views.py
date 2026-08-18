#!/usr/bin/env python3
"""Bounded repository-intelligence views (M0-T068 Unit E, D-013-R023/R024).

Five deterministic view builders over the accepted A1/A2 index, the accepted
code graph, and the accepted Unit C ontology — all consumed read-only:

  census        — every eligible file accounted for as indexed or
                  excluded/failed with per-reason groups (R023 census mode).
  changed       — this run's deterministic change classification against the
                  prior cache generation; an unsupported stated base
                  fingerprint REFUSES (never a guessed diff).
  neighborhood  — bounded in/out dependency edges around a named seed.
  card          — a bounded file/symbol card (kind, subsystem via the
                  versioned Unit C resolver, bounded edges, tree existence).
  deep          — an exact bounded source excerpt with content digest and
                  line provenance.

Every view carries ONE machine-readable coverage record (R024) built by a
single builder: repository identity, snapshot fingerprint, HEAD/branch/dirty
digest, census counts with per-reason groups, indexer/schema/config versions
plus the Unit C ontology stamp, source-manifest/export digests, and the EXACT
query parameters and result limits. Cache hit/miss and rebuild fields live in
a SEPARATE section labeled non-identity cache state, so the deterministic
sections stay byte-identical across cold and warm cache runs.

Views feed the ONE context compiler (R039): they return bounded structured
data and never assemble a prompt, budget, or capacity-filling content. All
truncation is explicit (machine-readable markers, R003). Fail closed (R013):
an unavailable index, a non-canonical deep path, or an out-of-tree path
refuses with a machine-readable error.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.memory_digest import is_canonical_repo_path  # noqa: E402
from tools.subsystem_resolver import (  # noqa: E402
    load_map, norm_path, resolve_path, version_stamp)

VIEWS_VERSION = "1.0.0"

#: Telemetry keys copied into the DETERMINISTIC coverage section. Excludes
#: run_id/elapsed/estimated_tokens/provider_tokens and every cache-state field.
_DETERMINISTIC_KEYS = (
    "repo_identity", "snapshot_fingerprint", "head_sha", "head_detached",
    "branch", "dirty_state_digest", "source_manifest_digest", "census",
    "versions", "generator_identity", "graph_nodes_after", "graph_edges_after",
)

#: Telemetry keys for the SEPARATE non-identity cache-state section (R024
#: requires cache hit/miss + reparse counts; they differ cold vs warm, so they
#: are carried outside the byte-identity sections, explicitly labeled).
_CACHE_STATE_KEYS = ("mode", "cache_result", "rebuild_reason", "files_parsed",
                     "files_reused", "affected_dependents")


class ViewsError(Exception):
    """Fail-closed view error with a machine-readable code."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")

    def doc(self) -> dict:
        return {"error": {"code": self.code, "detail": self.detail}}


def build_index(repo_root: str, cache_base: str | None = None,
                map_path: str | None = None):
    """(result, graph_index, loaded_map) or fail closed — never a partial view."""
    import json as _json

    from tools import repo_index_incremental as inc
    from tools.code_graph import query as cgquery
    try:
        res = inc.build_incremental(repo_root, cache_base=cache_base,
                                    persist_telemetry=False)
        gi = cgquery.GraphIndex(_json.loads(res.export_bytes))
    except ViewsError:
        raise
    except Exception as exc:
        raise ViewsError("index_unavailable",
                         f"{type(exc).__name__}: {exc}") from exc
    try:
        loaded_map = load_map(repo_root, map_path)
    except Exception as exc:
        raise ViewsError("ontology_unavailable",
                         f"{type(exc).__name__}: {exc}") from exc
    return res, gi, loaded_map


def coverage_record(res, loaded_map, query_params: dict, limits: dict) -> dict:
    """The single R024 coverage-record builder used by EVERY view."""
    tele = res.telemetry or {}
    det = {k: tele.get(k) for k in _DETERMINISTIC_KEYS}
    det["export_digest"] = res.export_digest()
    det["versions"] = dict(det.get("versions") or {})
    det["versions"]["ontology"] = version_stamp(loaded_map)
    det["views_version"] = VIEWS_VERSION
    det["query_params"] = query_params
    det["limits"] = limits
    return det


def cache_state(res) -> dict:
    tele = res.telemetry or {}
    state = {k: tele.get(k) for k in _CACHE_STATE_KEYS}
    state["label"] = "cache_state_non_identity"
    return state


def _truncate(items: list, limit: int) -> tuple[list, dict]:
    """Bounded slice + explicit machine-readable truncation marker (R003)."""
    kept = items[:max(int(limit), 0)]
    return kept, {"limit": limit, "returned": len(kept),
                  "omitted": max(len(items) - len(kept), 0),
                  "truncated": len(items) > len(kept)}


def census_view(res, gi, loaded_map, *, file_limit: int = 100) -> dict:
    """R023 census: every eligible file accounted for; bounded enumeration."""
    census = (res.telemetry or {}).get("census") or {}
    files, marker = _truncate(gi.file_ids(), file_limit)
    return {
        "view": "census", "coverage_mode": "census",
        "content": {
            "eligible": census.get("eligible"), "indexed": census.get("indexed"),
            "excluded_by_reason": census.get("excluded"),
            "failed_by_reason": census.get("failed"),
            "stale": census.get("stale"), "reconciles": census.get("reconciles"),
            "indexed_files": files, "indexed_files_truncation": marker,
        },
        "coverage": coverage_record(res, loaded_map,
                                    {"view": "census"}, {"file_limit": file_limit}),
        "runtime": cache_state(res),
    }


def changed_view(res, loaded_map, *, since_fingerprint: str | None = None) -> dict:
    """R023 changed: this run's deterministic classification vs the prior
    cache generation. A stated base OTHER than the current snapshot refuses —
    the view never fabricates a diff against a base it cannot reconstruct."""
    if since_fingerprint is not None and since_fingerprint != res.snapshot_fingerprint:
        raise ViewsError(
            "unsupported_base_fingerprint",
            "the changed view can only report against the prior cache "
            "generation of this checkout (or confirm no-change against the "
            "current snapshot fingerprint); arbitrary historical bases are "
            "not reconstructible and are never guessed")
    identical = since_fingerprint == res.snapshot_fingerprint
    cs = res.change_set.to_dict()
    return {
        "view": "changed", "coverage_mode": "changed",
        "content": {
            "base": ("stated_fingerprint_is_current_snapshot" if identical
                     else "prior_cache_generation"),
            "no_change_by_identity": identical,
            "change_set": ({k: [] if isinstance(v, list) else v
                            for k, v in cs.items()} if identical else cs),
        },
        "coverage": coverage_record(
            res, loaded_map,
            {"view": "changed", "since_fingerprint": since_fingerprint}, {}),
        "runtime": cache_state(res),
    }


def _edges(gi, nid: str, direction: str, limit: int) -> tuple[list, dict]:
    src = gi.out_edges if direction == "out" else gi.in_edges
    key = "to" if direction == "out" else "from"
    edges = sorted(src.get(nid, []),
                   key=lambda e: (e[key], e["type"], e.get("line") or 0))
    rows = [{key: e[key], "type": e["type"], "confidence": e["confidence"],
             "line": e.get("line")} for e in edges]
    return _truncate(rows, limit)


def _subsystem_of(node_id: str, loaded_map) -> dict:
    """Subsystem ONLY via the versioned Unit C resolver (R045); honest miss."""
    r = resolve_path(node_id, loaded_map)
    return {"subsystem": r["subsystem"], "resolved": r["resolved"],
            "reason": r["reason"]}


def neighborhood_view(res, gi, loaded_map, seed: str, *, edge_limit: int = 25) -> dict:
    nid = norm_path(seed)
    if nid not in gi.nodes:
        content = {"seed": seed, "resolved": False,
                   "reason": "seed_not_in_graph"}
    else:
        out_rows, out_marker = _edges(gi, nid, "out", edge_limit)
        in_rows, in_marker = _edges(gi, nid, "in", edge_limit)
        content = {
            "seed": seed, "resolved": True, "node_id": nid,
            "node_kind": gi.nodes[nid].get("kind"),
            "subsystem": _subsystem_of(nid, loaded_map),
            "out_edges": out_rows, "out_truncation": out_marker,
            "in_edges": in_rows, "in_truncation": in_marker,
        }
    return {
        "view": "neighborhood", "coverage_mode": "neighborhood", "content": content,
        "coverage": coverage_record(res, loaded_map,
                                    {"view": "neighborhood", "seed": seed},
                                    {"edge_limit": edge_limit}),
        "runtime": cache_state(res),
    }


def card_view(res, gi, loaded_map, repo_root: str, seed: str,
              *, edge_limit: int = 10) -> dict:
    nid = norm_path(seed)
    node = gi.nodes.get(nid)
    if node is None:
        content = {"seed": seed, "resolved": False,
                   "reason": "seed_not_in_graph"}
    else:
        out_rows, out_marker = _edges(gi, nid, "out", edge_limit)
        in_rows, in_marker = _edges(gi, nid, "in", edge_limit)
        content = {
            "seed": seed, "resolved": True, "node_id": nid,
            "kind": node.get("kind"), "name": node.get("name"),
            "module": node.get("module"), "line": node.get("line"),
            "is_test": node.get("is_test"),
            "exists_in_tree": (pathlib.Path(repo_root) / nid).exists(),
            "subsystem": _subsystem_of(nid, loaded_map),
            "out_edge_count": len(gi.out_edges.get(nid, [])),
            "in_edge_count": len(gi.in_edges.get(nid, [])),
            "out_edges": out_rows, "out_truncation": out_marker,
            "in_edges": in_rows, "in_truncation": in_marker,
        }
    return {
        "view": "card", "coverage_mode": "neighborhood", "content": content,
        "coverage": coverage_record(res, loaded_map,
                                    {"view": "card", "seed": seed},
                                    {"edge_limit": edge_limit}),
        "runtime": cache_state(res),
    }


def deep_view(res, loaded_map, repo_root: str, path: str, start: int, end: int,
              *, max_lines: int = 200) -> dict:
    """R023 deep: reopen ONE authoritative source, exact and bounded."""
    p = norm_path(path)
    if not is_canonical_repo_path(p):
        raise ViewsError("non_canonical_path",
                         f"{path!r} is not a canonical repo-relative path")
    fs_path = pathlib.Path(repo_root) / p
    if not fs_path.is_file():
        raise ViewsError("path_not_in_tree", f"{p!r} is not a file in the tree")
    try:
        raw = fs_path.read_bytes()
    except OSError as exc:
        raise ViewsError("source_unreadable", f"{p}: {exc}") from exc
    lines = raw.decode("utf-8", errors="replace").splitlines()
    start = max(int(start), 1)
    end = min(int(end), len(lines))
    requested = max(end - start + 1, 0)
    kept = lines[start - 1:start - 1 + min(requested, max_lines)]
    return {
        "view": "deep", "coverage_mode": "deep",
        "content": {
            "path": p, "start_line": start,
            "end_line": start + len(kept) - 1 if kept else start,
            "total_lines": len(lines),
            "content_digest": hashlib.sha256(
                raw.replace(b"\r\n", b"\n")).hexdigest(),
            "excerpt": kept,
            "truncation": {"limit": max_lines, "returned": len(kept),
                           "omitted": max(requested - len(kept), 0),
                           "truncated": requested > len(kept)},
        },
        "coverage": coverage_record(
            res, loaded_map,
            {"view": "deep", "path": p, "start": start, "end": end},
            {"max_lines": max_lines}),
        "runtime": cache_state(res),
    }
