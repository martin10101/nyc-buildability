#!/usr/bin/env python3
"""Bounded, deterministic query CLI over the code-navigation graph (M0-T030).

Trust model: ADVISORY navigation index, never authoritative truth. A query
result points at likely locations; you must READ THE ACTUAL SOURCE before
relying on it (mandatory for legal semantics, security, control plane,
contracts, dependency impact, public interfaces, acceptance/gate decisions).
See tools/code_graph/README.md.

Freshness: the source fingerprint is recomputed FIRST on every invocation.
On mismatch the graph is regenerated in-process (one line printed:
"regenerated (stale fingerprint)"); with --no-regen the CLI prints "STALE"
and exits 3. A stale graph never answers silently.

Boundedness: every subcommand emits at most --limit lines (default 40, hard
cap 200) and every result line starts with a repo-relative path (and :line
when known). No subcommand can dump the whole graph.

Usage:
  python tools/code_graph/query.py [--repo PATH] [--out DIR] [--no-regen]
      [--limit N] SUBCOMMAND ARGS

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
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate  # noqa: E402  (stdlib-only sibling module)

DEFAULT_LIMIT = 40
HARD_CAP = 200


# --------------------------------------------------------------------------
# artifact loading with mandatory freshness check
# --------------------------------------------------------------------------

def load_graph(repo_root: str, out_dir: str | None, no_regen: bool) -> dict:
    out = out_dir if out_dir else generate.default_out_dir(repo_root)
    fingerprint = generate.compute_source_fingerprint(repo_root)
    meta_path = os.path.join(out, "graph.meta.json")
    graph_path = os.path.join(out, "graph.json")
    stale = True
    if os.path.isfile(meta_path) and os.path.isfile(graph_path):
        try:
            with open(meta_path, "rb") as fh:
                meta = generate.json.loads(fh.read().decode("utf-8"))
            stale = meta.get("source_fingerprint") != fingerprint
        except ValueError:
            stale = True
    if stale:
        if no_regen:
            print("STALE")
            raise SystemExit(3)
        generate.generate_into(repo_root, out)
        print("regenerated (stale fingerprint)")
    with open(graph_path, "rb") as fh:
        return generate.json.loads(fh.read().decode("utf-8"))


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
    sub.add_parser("find").add_argument("needle")
    sub.add_parser("file").add_argument("target")
    sub.add_parser("module").add_argument("target")
    sub.add_parser("upstream").add_argument("target")
    sub.add_parser("downstream").add_argument("target")
    sub.add_parser("neighbors").add_argument("target")
    sub.add_parser("contracts").add_argument("target")
    p_path = sub.add_parser("path")
    p_path.add_argument("src")
    p_path.add_argument("dst")
    p_impact = sub.add_parser("impact")
    p_impact.add_argument("target")
    p_impact.add_argument("--depth", type=int, default=2,
                          help="downstream hops (1..2, capped at 2)")
    args = parser.parse_args(argv)

    repo_root = os.path.abspath(args.repo)
    graph = load_graph(repo_root, args.out, args.no_regen)
    gi = GraphIndex(graph)

    if args.command == "find":
        cmd_find(gi, args.needle, args.limit)
    elif args.command in ("file", "module"):
        cmd_file(gi, args.target, args.limit)
    elif args.command == "upstream":
        cmd_upstream(gi, args.target, args.limit)
    elif args.command == "downstream":
        cmd_downstream(gi, args.target, args.limit)
    elif args.command == "neighbors":
        cmd_neighbors(gi, args.target, args.limit)
    elif args.command == "contracts":
        cmd_contracts(gi, args.target, args.limit)
    elif args.command == "path":
        cmd_path(gi, args.src, args.dst, args.limit)
    elif args.command == "impact":
        cmd_impact(gi, args.target, args.depth, args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
