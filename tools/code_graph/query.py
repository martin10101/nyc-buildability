#!/usr/bin/env python3
"""Bounded, deterministic query CLI over the code-navigation graph (M0-T030).

Trust model: ADVISORY navigation index, never authoritative truth. A query
result points at likely locations; you must READ THE ACTUAL SOURCE before
relying on it (mandatory for legal semantics, security, control plane,
contracts, dependency impact, public interfaces, acceptance/gate decisions).
See tools/code_graph/README.md.

Freshness + integrity: the source fingerprint is recomputed FIRST on every
invocation, and the cached graph.json bytes are verified against the
graph_sha256 recorded in graph.meta.json on EVERY load (M0-T031 hardening).
A stale fingerprint prints "regenerated (stale fingerprint)"; a hash
mismatch, a missing/corrupt/unreadable artifact, or an OSError on either
read prints "regenerated (cache integrity)". With --no-regen the CLI prints
a one-line "STALE (...)" error and exits 3 instead. A stale or altered
graph is NEVER served, and these paths never leak a traceback.

Boundedness: every subcommand emits at most --limit lines (default 40, hard
cap 200) and every result line starts with a repo-relative path (and :line
when known). No subcommand can dump the whole graph. --limit is accepted
both before and after the subcommand; when both are given, the
subcommand-level value wins.

Usage:
  python tools/code_graph/query.py [--repo PATH] [--out DIR] [--no-regen]
      [--limit N] SUBCOMMAND ARGS [--limit N]

Subcommands:
  find <substring>          symbols/files matching a substring
  file <relpath>            summary of one file
  module <dotted-or-path>   summary of one module
  upstream <module|file>    what it imports
  downstream <module|file>  who imports it
  neighbors <node>          both directions
  contracts <stem|file>     contract-schema touchpoints
  path <a> <b>              BFS chain over exact resolved import edges
  impact <file|module>      1..2-hop downstream neighborhood (--depth max 2)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate  # noqa: E402  (stdlib-only sibling module)

DEFAULT_LIMIT = 40
HARD_CAP = 200


# --------------------------------------------------------------------------
# artifact loading with mandatory freshness + integrity check
# --------------------------------------------------------------------------

def _read_cache_attempt(
    meta_path: str, graph_path: str, fingerprint: str
) -> tuple[dict | None, str | None]:
    """(graph, None) when the cache is fresh AND intact, else (None, reason).

    reason is "stale fingerprint" for a source mismatch or a cleanly absent
    artifact (a cold cache was always "stale"), and "cache integrity" for
    everything else: corrupt/unparseable meta or graph, an OSError on either
    read (e.g. the path exists but is not a readable file), a missing
    graph_sha256, or a hash mismatch between meta.graph_sha256 and the actual
    cached graph.json bytes. An altered or unreadable cache is treated
    exactly like a stale one — never served.
    """
    if not os.path.exists(meta_path):
        return None, "stale fingerprint"
    try:
        with open(meta_path, "rb") as fh:
            meta = json.loads(fh.read().decode("utf-8"))
    except (OSError, ValueError):
        return None, "cache integrity"
    if not isinstance(meta, dict):
        return None, "cache integrity"
    if meta.get("source_fingerprint") != fingerprint:
        return None, "stale fingerprint"
    if not os.path.exists(graph_path):
        return None, "stale fingerprint"
    try:
        with open(graph_path, "rb") as fh:
            graph_bytes = fh.read()
    except OSError:
        return None, "cache integrity"
    expected = meta.get("graph_sha256")
    if not expected or hashlib.sha256(graph_bytes).hexdigest() != expected:
        return None, "cache integrity"
    try:
        graph = json.loads(graph_bytes.decode("utf-8"))
    except ValueError:
        return None, "cache integrity"
    if not isinstance(graph, dict):
        return None, "cache integrity"
    return graph, None


def load_graph(repo_root: str, out_dir: str | None, no_regen: bool) -> dict:
    out = out_dir if out_dir else generate.default_out_dir(repo_root)
    fingerprint = generate.compute_source_fingerprint(repo_root)
    meta_path = os.path.join(out, "graph.meta.json")
    graph_path = os.path.join(out, "graph.json")

    graph, reason = _read_cache_attempt(meta_path, graph_path, fingerprint)
    if reason is None:
        return graph
    if no_regen:
        print("STALE (%s): refusing to serve the cached graph" % reason)
        raise SystemExit(3)
    try:
        generate.generate_into(repo_root, out)
    except OSError as exc:
        print("cache regeneration failed (%s): %s" % (reason, exc))
        raise SystemExit(3)
    print("regenerated (%s)" % reason)
    graph, reason = _read_cache_attempt(meta_path, graph_path, fingerprint)
    if reason is not None:
        print("cache unusable even after regeneration (%s)" % reason)
        raise SystemExit(3)
    return graph


class GraphIndex:
    def __init__(self, graph: dict):
        self.nodes = {n["id"]: n for n in graph["nodes"]}
        self.edges = graph["edges"]
        self.out_edges: dict[str, list[dict]] = {}
        self.in_edges: dict[str, list[dict]] = {}
        self.module_map: dict[str, list[str]] = {}
        for e in self.edges:
            self.out_edges.setdefault(e["from"], []).append(e)
            self.in_edges.setdefault(e["to"], []).append(e)
        for n in graph["nodes"]:
            if "module" in n:
                self.module_map.setdefault(n["module"], []).append(n["id"])

    def file_ids(self) -> list[str]:
        return sorted(
            nid
            for nid, n in self.nodes.items()
            if n["kind"] in ("py_module", "ts_module", "contract_schema")
        )


def _norm_arg(s: str) -> str:
    s = s.replace("\\", "/")
    while s.startswith("./"):
        s = s[2:]
    return s.rstrip("/")


def resolve_node(gi: GraphIndex, arg: str) -> str:
    """Resolve a user argument to exactly one node id, or exit 2 with candidates."""
    a = _norm_arg(arg)
    if a in gi.nodes:
        return a
    mods = gi.module_map.get(a, [])
    if len(mods) == 1:
        return mods[0]
    suffix = [nid for nid in gi.file_ids() if nid.endswith("/" + a) or nid == a]
    if len(suffix) == 1:
        return suffix[0]
    sub = [nid for nid in sorted(gi.nodes) if a.lower() in nid.lower()]
    if len(sub) == 1:
        return sub[0]
    pool = mods or suffix or sub
    if pool:
        print("ambiguous node %r; candidates:" % arg)
        for nid in sorted(pool)[:20]:
            print(nid)
        raise SystemExit(2)
    print("node not found: %r" % arg)
    raise SystemExit(2)


# --------------------------------------------------------------------------
# bounded emitter (AS-6)
# --------------------------------------------------------------------------

def emit(lines: list[str], limit: int) -> None:
    cap = min(max(int(limit), 1), HARD_CAP)
    for line in lines[:cap]:
        print(line)
    if len(lines) > cap:
        print("...truncated (%d more)" % (len(lines) - cap))
    if not lines:
        print("(no results)")


def _loc(node: dict) -> str:
    if "line" in node:
        return "%s:%d" % (node["path"], node["line"])
    return node.get("path", node["id"])


def _edge_out_line(e: dict) -> str:
    return "%s:%s -> %s [%s/%s] spec=%s" % (
        e["from"], e["line"], e["to"], e["type"], e["confidence"], e["specifier"]
    )


def _edge_in_line(e: dict) -> str:
    return "%s:%s -> %s [%s/%s] spec=%s" % (
        e["from"], e["line"], e["to"], e["type"], e["confidence"], e["specifier"]
    )


# --------------------------------------------------------------------------
# subcommands
# --------------------------------------------------------------------------

def cmd_find(gi: GraphIndex, needle: str, limit: int) -> None:
    n = needle.lower()
    lines = []
    for nid in sorted(gi.nodes):
        node = gi.nodes[nid]
        hay = nid.lower()
        qual = str(node.get("qualname", "")).lower()
        if n in hay or n in qual:
            if node["kind"] == "external":
                lines.append("external:%s %s" % (node["name"], node["kind"]))
            elif "qualname" in node:
                lines.append("%s %s %s" % (_loc(node), node["kind"],
                                           node["qualname"]))
            else:
                lines.append("%s %s" % (_loc(node), node["kind"]))
    emit(lines, limit)


def cmd_file(gi: GraphIndex, arg: str, limit: int) -> None:
    nid = resolve_node(gi, arg)
    node = gi.nodes[nid]
    path = node.get("path", nid)
    lines = []
    header = "%s kind=%s" % (path, node["kind"])
    if "module" in node:
        header += " module=%s" % node["module"]
    header += " is_test=%s" % str(node.get("is_test", False)).lower()
    lines.append(header)
    out_n = len(gi.out_edges.get(nid, []))
    in_n = len(gi.in_edges.get(nid, []))
    lines.append("%s imports_out=%d imported_by=%d" % (path, out_n, in_n))
    symbols = sorted(
        (n for n in gi.nodes.values()
         if n.get("path") == path and "qualname" in n),
        key=lambda n: (n.get("line", 0), n["id"]),
    )
    for s in symbols:
        lines.append("%s %s %s" % (_loc(s), s["kind"], s["qualname"]))
    emit(lines, limit)


def cmd_upstream(gi: GraphIndex, arg: str, limit: int) -> None:
    nid = resolve_node(gi, arg)
    lines = [_edge_out_line(e) for e in sorted(
        gi.out_edges.get(nid, []),
        key=lambda e: (e["type"], e["to"], e["line"], e["specifier"]),
    )]
    emit(lines, limit)


def cmd_downstream(gi: GraphIndex, arg: str, limit: int) -> None:
    nid = resolve_node(gi, arg)
    lines = [_edge_in_line(e) for e in sorted(
        gi.in_edges.get(nid, []),
        key=lambda e: (e["from"], e["line"], e["type"], e["specifier"]),
    )]
    emit(lines, limit)


def cmd_neighbors(gi: GraphIndex, arg: str, limit: int) -> None:
    nid = resolve_node(gi, arg)
    lines = []
    for e in sorted(gi.out_edges.get(nid, []),
                    key=lambda e: (e["to"], e["line"], e["type"])):
        lines.append(_edge_out_line(e))
    for e in sorted(gi.in_edges.get(nid, []),
                    key=lambda e: (e["from"], e["line"], e["type"])):
        lines.append(_edge_in_line(e))
    emit(lines, limit)


def cmd_contracts(gi: GraphIndex, arg: str, limit: int) -> None:
    a = _norm_arg(arg)
    schema_ids = sorted(
        nid for nid, n in gi.nodes.items()
        if n["kind"] == "contract_schema"
        and (n.get("stem") == a or nid == a or nid.endswith("/" + a))
    )
    lines: list[str] = []
    if schema_ids:
        for sid in schema_ids:
            for e in sorted(gi.in_edges.get(sid, []),
                            key=lambda e: (e["from"], e["line"])):
                if e["type"] == "contract_ref":
                    lines.append(_edge_in_line(e))
    else:
        nid = resolve_node(gi, arg)
        for e in sorted(gi.out_edges.get(nid, []),
                        key=lambda e: (e["to"], e["line"])):
            if e["type"] == "contract_ref":
                lines.append(_edge_out_line(e))
    emit(lines, limit)


def _reliable_adjacency(gi: GraphIndex) -> dict[str, list[tuple[str, dict]]]:
    """Directed adjacency over EXACT-confidence resolved-internal import-ish
    edges only (documented meaning of 'reliable')."""
    adj: dict[str, list[tuple[str, dict]]] = {}
    for e in gi.edges:
        if (
            e["type"] in ("import", "reexport")
            and e["confidence"] == "exact"
            and e["resolution"] == "internal"
        ):
            adj.setdefault(e["from"], []).append((e["to"], e))
    for k in adj:
        adj[k].sort(key=lambda t: t[0])
    return adj


def cmd_path(gi: GraphIndex, a: str, b: str, limit: int) -> None:
    src = resolve_node(gi, a)
    dst = resolve_node(gi, b)
    adj = _reliable_adjacency(gi)
    prev: dict[str, tuple[str, dict]] = {}
    seen = {src}
    frontier = [src]
    found = src == dst
    while frontier and not found:
        nxt = []
        for u in frontier:
            for v, e in adj.get(u, []):
                if v in seen:
                    continue
                seen.add(v)
                prev[v] = (u, e)
                if v == dst:
                    found = True
                    break
                nxt.append(v)
            if found:
                break
        frontier = nxt
    if not found:
        print("no reliable path")
        return
    chain: list[tuple[str, dict]] = []
    cur = dst
    while cur != src:
        u, e = prev[cur]
        chain.append((u, e))
        cur = u
    chain.reverse()
    lines = [
        "%s:%s -> %s [%s/exact]" % (u, e["line"], e["to"], e["type"])
        for u, e in chain
    ]
    if not lines:
        lines = ["%s (source and destination are the same node)" % src]
    emit(lines, limit)


def cmd_impact(gi: GraphIndex, arg: str, depth: int, limit: int) -> None:
    nid = resolve_node(gi, arg)
    depth = min(max(int(depth), 1), 2)
    lines: list[str] = []
    seen = {nid}
    frontier = [nid]
    for d in range(1, depth + 1):
        nxt: list[str] = []
        for target in frontier:
            for e in sorted(gi.in_edges.get(target, []),
                            key=lambda e: (e["from"], e["line"])):
                if e["resolution"] != "internal":
                    continue
                lines.append(
                    "%s:%s depth=%d [%s/%s] -> %s"
                    % (e["from"], e["line"], d, e["type"], e["confidence"],
                       target)
                )
                if e["from"] not in seen:
                    seen.add(e["from"])
                    nxt.append(e["from"])
        frontier = nxt
    emit(lines, limit)


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(
        description="Bounded queries over the advisory code-navigation graph. "
        "Results are likely locations, not truth: read the actual source."
    )
    parser.add_argument("--repo", default=".", help="repository root")
    parser.add_argument("--out", default=None, help="explicit artifact directory")
    parser.add_argument("--no-regen", action="store_true",
                        help="exit 3 with STALE instead of regenerating")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                        help="max output lines (default %d, hard cap %d)"
                        % (DEFAULT_LIMIT, HARD_CAP))
    sub = parser.add_subparsers(dest="command", required=True)

    def add_sub(name: str) -> argparse.ArgumentParser:
        # Each subparser also accepts --limit (M0-T031: the flag works both
        # before AND after the subcommand). A distinct dest keeps argparse
        # from clobbering an already-parsed global value with the subparser
        # default; when both positions are given, the subcommand-level value
        # wins. Default/hard-cap semantics are unchanged (40 / 200).
        p = sub.add_parser(name)
        p.add_argument("--limit", dest="limit_sub", type=int, default=None,
                       help="max output lines (default %d, hard cap %d); "
                       "overrides a pre-subcommand --limit"
                       % (DEFAULT_LIMIT, HARD_CAP))
        return p

    add_sub("find").add_argument("needle")
    add_sub("file").add_argument("target")
    add_sub("module").add_argument("target")
    add_sub("upstream").add_argument("target")
    add_sub("downstream").add_argument("target")
    add_sub("neighbors").add_argument("target")
    add_sub("contracts").add_argument("target")
    p_path = add_sub("path")
    p_path.add_argument("src")
    p_path.add_argument("dst")
    p_impact = add_sub("impact")
    p_impact.add_argument("target")
    p_impact.add_argument("--depth", type=int, default=2,
                          help="downstream hops (1..2, capped at 2)")
    args = parser.parse_args(argv)
    limit = args.limit_sub if args.limit_sub is not None else args.limit

    repo_root = os.path.abspath(args.repo)
    graph = load_graph(repo_root, args.out, args.no_regen)
    gi = GraphIndex(graph)

    if args.command == "find":
        cmd_find(gi, args.needle, limit)
    elif args.command in ("file", "module"):
        cmd_file(gi, args.target, limit)
    elif args.command == "upstream":
        cmd_upstream(gi, args.target, limit)
    elif args.command == "downstream":
        cmd_downstream(gi, args.target, limit)
    elif args.command == "neighbors":
        cmd_neighbors(gi, args.target, limit)
    elif args.command == "contracts":
        cmd_contracts(gi, args.target, limit)
    elif args.command == "path":
        cmd_path(gi, args.src, args.dst, limit)
    elif args.command == "impact":
        cmd_impact(gi, args.target, args.depth, limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
