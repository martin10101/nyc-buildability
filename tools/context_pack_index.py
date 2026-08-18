#!/usr/bin/env python3
"""Context-pack consumption of the deterministic A1/A2 index (M0-T065 Unit B).

Turns the accepted content-addressed index into bounded, deterministic context
sources: (a) a code-graph NEIGHBORHOOD source for the changed/target paths, built
from an IN-PROCESS graph (no subprocess, no cache-rebuild side effect), and (b) a
CENSUS + provenance source (snapshot fingerprint, HEAD/branch/dirty digest,
source-manifest digest, versions, coverage census). The dependency-breadth signal
for the adaptive tier is derived here from the graph's importer edges.

Fail-safe: any index error (not a git tree, cache problem, generator issue)
degrades to a recorded coverage omission -- the pack NEVER crashes and never
silently drops coverage (D-013-R003/R013). No wall-clock value ever enters a
source (determinism): `elapsed_seconds` from the run record is excluded.
"""
from __future__ import annotations

import json
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools import repo_index_incremental as inc  # noqa: E402
from tools.code_graph import query as cgquery  # noqa: E402
from tools.context_pack_io import canon_json_bytes  # noqa: E402

#: Max seed targets turned into neighborhoods (bounded, deterministic order).
MAX_SEEDS = 5

# Provenance fields copied into the DETERMINISTIC pack. Restricted to fields that
# depend only on the INDEXED SOURCE + HEAD, never on transient working-tree noise
# or cache state, so the pack stays byte-identical for the same source state:
#   * EXCLUDED cache-state fields (mode, cache_result, rebuild_reason, files_parsed/
#     reused, affected_dependents, elapsed) -- differ cold vs warm.
#   * EXCLUDED dirty_state_digest + snapshot_fingerprint -- they hash the FULL
#     working-tree porcelain, which includes the pack's own out/ directory when it
#     is written inside the repo, so two builds of the same source diverge. The
#     source identity is captured by source_manifest_digest + export_digest (both
#     over the indexed source only). The volatile snapshot fingerprint + dirty
#     digest are still recorded in the external run-record JSONL (R024), where
#     non-determinism is acceptable.
_PROVENANCE_TELEMETRY_KEYS = (
    "head_sha", "branch", "head_detached", "source_manifest_digest", "versions",
    "generator_identity", "census", "graph_nodes_after", "graph_edges_after",
)


def _norm(target: str) -> str:
    s = target.replace("\\", "/")
    while s.startswith("./"):
        s = s[2:]
    return s.rstrip("/")


def _neighborhood(gi, nid: str, limit: int) -> list[str]:
    """Bounded, deterministic neighborhood lines for one resolved node."""
    cap = max(int(limit), 1)
    out_edges = sorted(gi.out_edges.get(nid, []),
                       key=lambda e: (e["to"], e["type"], e["line"]))
    in_edges = sorted(gi.in_edges.get(nid, []),
                      key=lambda e: (e["from"], e["type"], e["line"]))
    lines = [f"# {nid}",
             f"  out ({len(out_edges)}): depends on",
             *[f"    -> {e['to']} [{e['type']}/{e['confidence']}]" for e in out_edges[:cap]]]
    if len(out_edges) > cap:
        lines.append(f"    ...(+{len(out_edges) - cap} more)")
    lines.append(f"  in ({len(in_edges)}): depended on by")
    lines += [f"    <- {e['from']} [{e['type']}/{e['confidence']}]" for e in in_edges[:cap]]
    if len(in_edges) > cap:
        lines.append(f"    ...(+{len(in_edges) - cap} more)")
    return lines


def gather_index_sources(repo: str, targets: list[str], graph_limit: int,
                         index_opts: dict) -> dict:
    """Build the code-graph neighborhood + census sources from the A1/A2 index.

    Returns {"sources": [Source-like], "omissions": [...], "graph_queries": [...],
    "provenance": {...}}. Imports the Source type lazily to avoid an import cycle
    with context_pack_sources.
    """
    from tools.context_pack_sources import Source

    result = {"sources": [], "omissions": [], "graph_queries": [],
              "provenance": {"index_consumed": False, "coverage_mode": "none",
                             "dependency_breadth": 0, "changed_targets": len(targets)}}

    if index_opts.get("no_index"):
        result["omissions"].append({
            "category": "code_graph", "default_exclusion": False,
            "reason": "index consumption disabled (--no-index); degraded to diff/routing "
                      "coverage only (fail-safe, coverage recorded not silently dropped)"})
        result["provenance"]["coverage_mode"] = "disabled"
        return result

    try:
        res = inc.build_incremental(
            repo,
            cache_base=index_opts.get("cache_base"),
            run_id=index_opts.get("run_id"),
            persist_telemetry=bool(index_opts.get("persist_telemetry", False)))
        graph = json.loads(res.export_bytes)
        gi = cgquery.GraphIndex(graph)
        export_digest = res.export_digest()
    except Exception as exc:  # fail-safe: never crash the pack on an index error
        result["omissions"].append({
            "category": "code_graph", "default_exclusion": False,
            "reason": f"deterministic index unavailable ({type(exc).__name__}); "
                      f"degraded to diff/routing coverage only (fail-safe)"})
        result["provenance"]["coverage_mode"] = "index_error"
        return result

    # ---- neighborhoods for the bounded seed set --------------------------------
    seeds = [t for t in targets if t][:MAX_SEEDS]
    graph_lines: list[str] = []
    dependents: set[str] = set()
    for seed in seeds:
        a = _norm(seed)
        resolved = a in gi.nodes
        out_n = len(gi.out_edges.get(a, [])) if resolved else 0
        in_edges = gi.in_edges.get(a, []) if resolved else []
        in_n = len(in_edges)
        if resolved:
            dependents.update(e["from"] for e in in_edges)
            graph_lines.extend(_neighborhood(gi, a, graph_limit))
            graph_lines.append("")
        result["graph_queries"].append({
            "subcommand": "neighborhood", "seed": seed, "resolved": resolved,
            "resolved_id": a if resolved else None, "limit": graph_limit,
            "out_edges": out_n, "in_edges": in_n,
            "export_digest": export_digest})
    if not seeds:
        result["omissions"].append({
            "category": "code_graph_no_targets", "default_exclusion": False,
            "reason": "no changed paths or task outputs to seed bounded graph neighborhoods"})

    if graph_lines:
        header = ("Advisory only: the code graph (from the deterministic A1/A2 index) "
                  "points at likely locations; the source excerpts below, not these "
                  "hints, are authoritative.\n\n")
        result["sources"].append(Source(
            "code_graph", "code_graph", 40, "Code-graph neighborhoods (bounded, from index)",
            "code_graph", "tools/repo_index_incremental.py", "text",
            header + "\n".join(graph_lines)))

    # ---- provenance + census (material) ----------------------------------------
    tele = res.telemetry or {}
    # dependency_breadth is derived ONLY from the graph (source-deterministic);
    # the cache-dependent affected_dependents is NOT added (it would vary cold vs warm).
    provenance = {k: tele.get(k) for k in _PROVENANCE_TELEMETRY_KEYS}
    provenance["export_digest"] = export_digest
    provenance["index_consumed"] = True
    provenance["dependency_breadth"] = len(dependents)
    provenance["changed_targets"] = len(targets)
    census = (tele.get("census") or {})
    provenance["coverage_mode"] = "census" if census.get("reconciles") else "changed"
    # The full (volatile) snapshot fingerprint + dirty digest live only in the
    # external run-record; the deterministic pack cannot embed them (see note above).
    provenance["snapshot_identity_in_external_run_record"] = True
    result["provenance"] = provenance

    census_doc = {
        "export_digest": export_digest,
        "head_sha": tele.get("head_sha"), "branch": tele.get("branch"),
        "source_manifest_digest": tele.get("source_manifest_digest"),
        "versions": tele.get("versions"),
        "generator_identity": tele.get("generator_identity"),
        "graph_nodes": tele.get("graph_nodes_after"),
        "graph_edges": tele.get("graph_edges_after"),
        "census": census,
        "dependency_breadth": provenance["dependency_breadth"],
        "coverage_mode": provenance["coverage_mode"],
    }
    result["sources"].append(Source(
        "repo_census", "repo_census", 45, "Repository census + index provenance",
        "repo_census", "tools/repo_fingerprint.py", "json",
        canon_json_bytes(census_doc).decode("utf-8")))
    return result
