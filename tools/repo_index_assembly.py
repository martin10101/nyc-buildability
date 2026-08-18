#!/usr/bin/env python3
"""Byte-identical incremental assembly for A2 (M0-T064, D-013-R032/R037/R079).

Reproduces `code_graph.build_graph`'s exported bytes from per-file extraction
*bundles*, so an unchanged file can be REUSED (its `ast.parse` / TS scan skipped)
while the assembled output stays BYTE-IDENTICAL to a clean full rebuild. This is
what makes A2 a real incremental indexer instead of a cache that full-rebuilds on
every edit: on a local content change only the changed files are reparsed
(D-013-R032), and a local change triggers no full rebuild (D-013-R059).

Coupling to the generator's private extraction internals (`_extract_py`,
`_extract_ts`, `_PyIndex`, `_TsResolver`, `_EdgeSet`, `_contract_edges`) is
deliberate and *guarded*: `drive()` runs only against the exact generator/schema
version it was written for (`KNOWN_GENERATOR_VERSION`/`KNOWN_SCHEMA_VERSION`).
Any other version raises `UnknownGeneratorError` and the caller falls back to the
real `code_graph.build_graph` — correctness never depends on this replica silently
staying in sync. The parity test proves `drive()` == `build_graph` byte-for-byte
on the live generator; if the generator is bumped, that test fails until this
module (and the known-version constants) are updated in lock-step.

A "bundle" for a file F is the exact slice of graph output F contributes:
  {"nodes": [...], "import_edges": [...], "contract_edges": [...],
   "externals": [...]}
Every edge F contributes has `from == F` (import edges via `_extract_*`, contract
edges via the `_contract_edges` inner loop), so bundles partition the graph with
no cross-file key collisions and merge back deterministically.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import pathlib
import sys
from typing import Any

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.code_graph import generate as cg  # noqa: E402

# The exact generator this replica reproduces. A mismatch means the generator
# changed and this module has NOT been re-verified against it, so we refuse to
# assemble and let the caller use the real builder (fail-safe, never fail-wrong).
KNOWN_GENERATOR_VERSION = "1.1.0"
KNOWN_SCHEMA_VERSION = "1.0.0"


class UnknownGeneratorError(RuntimeError):
    """Raised when the live generator is not the version this replica verifies."""


def generator_identity() -> str:
    return f"{cg.GENERATOR_VERSION}/{cg.SCHEMA_VERSION}"


def generator_recognized() -> bool:
    return (cg.GENERATOR_VERSION == KNOWN_GENERATOR_VERSION
            and cg.SCHEMA_VERSION == KNOWN_SCHEMA_VERSION)


def _require_known_generator() -> None:
    if not generator_recognized():
        raise UnknownGeneratorError(
            f"generator {generator_identity()} != verified "
            f"{KNOWN_GENERATOR_VERSION}/{KNOWN_SCHEMA_VERSION}")


def config_inputs_version(repo_root: str | os.PathLike[str]) -> str:
    """A digest over the generator's CONFIG_INPUTS (e.g. apps/web/tsconfig.json).

    These files STEER generation -- tsconfig drives TS `@/` alias resolution in
    `_TsResolver` -- but are NOT indexed source files, so A1's snapshot
    fingerprint does not otherwise capture them. Folding this digest into the
    fingerprint the incremental layer uses makes any config-input change (a) move
    the cache key (no stale hit even for a committed tsconfig-only edit) and
    (b) surface as a global invalidator in classify_changes, forcing a full
    rebuild. Without it, a reused TS bundle keeps its old alias-resolved edges and
    the incremental export diverges from a clean full rebuild. Hashes exactly like
    the generator's own `_fingerprint_entry` (CRLF->LF, sha256), so an existing
    vs. absent config input is handled identically to the generator.
    """
    root = str(pathlib.Path(repo_root).resolve())
    h = hashlib.sha256()
    h.update(b"codegraph_config_inputs\x00")
    for rel in cg.CONFIG_INPUTS:
        if os.path.isfile(os.path.join(root, *rel.split("/"))):
            h.update(cg._fingerprint_entry(root, rel))
    return h.hexdigest()


@dataclasses.dataclass
class AssemblyResult:
    export_bytes: bytes
    graph: dict[str, Any]
    meta: dict[str, Any]
    bundles: dict[str, dict[str, Any]]   # rel -> bundle (for the next reuse)
    schema_nodes: list[dict[str, Any]]   # cached for warm reuse (schema set stable)
    input_files: list[str]
    aliases: list[list[str]]
    files_parsed: int
    files_reused: int


# --------------------------------------------------------------------------
# per-file extraction (the parse step this module exists to skip on reuse)
# --------------------------------------------------------------------------

def _read_text(repo_root: str, rel: str) -> str:
    with open(os.path.join(repo_root, *rel.split("/")), "rb") as fh:
        return fh.read().replace(b"\r\n", b"\n").decode("utf-8", errors="replace")


def _edge_dicts(es: "cg._EdgeSet") -> list[dict[str, Any]]:
    # Deterministic slice of one file's edges (sorted by the EdgeSet key).
    return [es._edges[k] for k in sorted(es._edges)]


def _extract_py_bundle(rel: str, text: str, index: "cg._PyIndex") -> dict[str, Any]:
    es = cg._EdgeSet()
    nodes = cg._extract_py(rel, text, index, es)
    return {"nodes": nodes, "import_edges": _edge_dicts(es),
            "externals": sorted(es.externals), "contract_edges": []}


def _extract_ts_bundle(rel: str, text: str, resolver: "cg._TsResolver") -> dict[str, Any]:
    es = cg._EdgeSet()
    nodes = cg._extract_ts(rel, text, resolver, es)
    return {"nodes": nodes, "import_edges": _edge_dicts(es),
            "externals": sorted(es.externals), "contract_edges": []}


def _schema_node(rel: str, text: str) -> dict[str, Any]:
    stem = rel.rsplit("/", 1)[-1][: -len(cg.SCHEMA_SUFFIX)]
    schema_id = ""
    try:
        schema_id = str(json.loads(text).get("$id", "") or "")
    except ValueError:
        pass
    return {"id": rel, "kind": "contract_schema", "path": rel, "stem": stem,
            "schema_id": schema_id, "is_test": cg._is_test_path(rel)}


def _contract_edges_for(rel: str, text: str,
                        schema_nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The contract edges a single file `rel` contributes -- the inner body of
    `code_graph._contract_edges` for one (rel, text). Guarded byte-for-byte by
    `test_contract_partition_matches_real` against the real global pass."""
    es = cg._EdgeSet()
    for schema in schema_nodes:
        if schema["path"] == rel:
            continue
        candidates = [schema["path"].rsplit("/", 1)[-1], schema["stem"]]
        if schema.get("schema_id"):
            candidates.append(schema["schema_id"])
        best: tuple[int, str] | None = None
        for cand in candidates:
            if not cand:
                continue
            idx = text.find(cand)
            if idx != -1 and (best is None or idx < best[0]):
                best = (idx, cand)
        if best is not None:
            line = text.count("\n", 0, best[0]) + 1
            es.add_edge("contract_ref", rel, schema["path"], "derived", line,
                        best[1], "internal")
    return _edge_dicts(es)


# --------------------------------------------------------------------------
# assembly (byte-identical replica of build_graph's merge/meta, lines 723-810)
# --------------------------------------------------------------------------

def _assemble(input_files: list[str], schema_nodes: list[dict[str, Any]],
              bundles: dict[str, dict[str, Any]], aliases: list[list[str]],
              fingerprint: str) -> tuple[dict[str, Any], dict[str, Any]]:
    nodes: dict[str, dict] = {}

    def add_nodes(items: list[dict]) -> None:
        for item in items:
            nodes.setdefault(item["id"], item)

    py_files = [f for f in input_files if f.endswith(".py")]
    ts_files = [f for f in input_files if f.endswith((".ts", ".tsx"))]

    for n in schema_nodes:
        add_nodes([n])

    edges = cg._EdgeSet()

    def _re_add(edge_list: list[dict[str, Any]]) -> None:
        for e in edge_list:
            edges.add_edge(e["type"], e["from"], e["to"], e["confidence"],
                           e["line"], e["specifier"], e["resolution"])

    for rel in py_files:
        b = bundles[rel]
        add_nodes(b["nodes"])
        _re_add(b["import_edges"])
        for name in b["externals"]:
            edges.external(name)
    for rel in ts_files:
        b = bundles[rel]
        add_nodes(b["nodes"])
        _re_add(b["import_edges"])
        for name in b["externals"]:
            edges.external(name)

    # contract edges follow the extraction edges, exactly as build_graph orders
    # them (their keys never collide with import edges -- distinct edge type).
    for rel in input_files:
        _re_add(bundles[rel].get("contract_edges", []))

    for name in sorted(edges.externals):
        nodes.setdefault(
            "external:" + name,
            {"id": "external:" + name, "kind": "external", "name": name})

    sorted_nodes = [nodes[k] for k in sorted(nodes)]
    sorted_edges = edges.sorted_edges()

    node_counts: dict[str, int] = {}
    for n in sorted_nodes:
        node_counts[n["kind"]] = node_counts.get(n["kind"], 0) + 1
    edge_by_type: dict[str, int] = {}
    edge_by_conf: dict[str, int] = {}
    by_lang_conf: dict[str, dict[str, int]] = {}
    for e in sorted_edges:
        edge_by_type[e["type"]] = edge_by_type.get(e["type"], 0) + 1
        edge_by_conf[e["confidence"]] = edge_by_conf.get(e["confidence"], 0) + 1
        frm = e["from"]
        if frm.endswith(".py"):
            lang = "py"
        elif frm.endswith((".ts", ".tsx")):
            lang = "ts"
        else:
            lang = "json"
        bucket = by_lang_conf.setdefault(lang, {})
        bucket[e["confidence"]] = bucket.get(e["confidence"], 0) + 1

    graph = {
        "schema_version": cg.SCHEMA_VERSION,
        "nodes": sorted_nodes,
        "edges": sorted_edges,
    }
    meta = {
        "schema_version": cg.SCHEMA_VERSION,
        "generator_version": cg.GENERATOR_VERSION,
        "mode": cg.MODE,
        "source_fingerprint": fingerprint,
        "fingerprint_algorithm": cg.FINGERPRINT_ALGORITHM,
        "include_roots": [
            {"root": s["root"], "patterns": list(s["patterns"])}
            for s in cg.INCLUDE_ROOTS
        ],
        "exclude_dirs": list(cg.EXCLUDE_DIRS),
        "ts_aliases": aliases,
        "input_file_count": len(input_files),
        "node_counts": node_counts,
        "edge_counts": {
            "by_type": edge_by_type,
            "by_confidence": edge_by_conf,
            "by_language_confidence": by_lang_conf,
        },
    }
    return graph, meta


def _schema_files(input_files: list[str]) -> list[str]:
    return [f for f in input_files
            if f.startswith(cg.SCHEMA_DIR_PREFIX) and f.endswith(cg.SCHEMA_SUFFIX)]


def drive(repo_root: str | os.PathLike[str], *,
          prior_bundles: dict[str, dict[str, Any]] | None = None,
          prior_schema_nodes: list[dict[str, Any]] | None = None,
          changed: frozenset[str] = frozenset(),
          input_files: list[str] | None = None) -> AssemblyResult:
    """Assemble the index, reusing `prior_bundles` for files not in `changed`.

    A cold build passes no prior; every file is extracted. A warm build passes
    the prior generation's bundles + schema nodes and the set of content-changed
    files; only those are reparsed. The caller MUST guarantee that the reuse
    preconditions hold (no add/delete/rename, no schema change, no global
    invalidator) so the resolution index and schema-node set are unchanged --
    the invariant that makes a reused bundle still exact.
    """
    _require_known_generator()
    root = str(pathlib.Path(repo_root).resolve())
    files = list(input_files) if input_files is not None else cg.scan_input_files(root)

    py_files = [f for f in files if f.endswith(".py")]
    ts_files = [f for f in files if f.endswith((".ts", ".tsx"))]
    index = cg._PyIndex(py_files)
    aliases = cg._load_ts_aliases(root)
    resolver = cg._TsResolver(set(ts_files), aliases)

    cold = prior_bundles is None
    prior_bundles = prior_bundles or {}

    # schema nodes: rebuild on a cold pass; on a warm pass the schema set is
    # unchanged (precondition) so the prior nodes are reused verbatim.
    schema_files = _schema_files(files)
    if cold or prior_schema_nodes is None:
        schema_nodes = [_schema_node(rel, _read_text(root, rel))
                        for rel in schema_files]
    else:
        schema_nodes = prior_schema_nodes

    bundles: dict[str, dict[str, Any]] = {}
    files_parsed = 0
    files_reused = 0

    for rel in files:
        reuse = (not cold) and (rel not in changed) and (rel in prior_bundles)
        if reuse:
            bundles[rel] = prior_bundles[rel]
            files_reused += 1
            continue
        text = _read_text(root, rel)
        if rel.endswith(".py"):
            b = _extract_py_bundle(rel, text, index)
            files_parsed += 1
        elif rel.endswith((".ts", ".tsx")):
            b = _extract_ts_bundle(rel, text, resolver)
            files_parsed += 1
        else:
            b = {"nodes": [], "import_edges": [], "externals": [],
                 "contract_edges": []}
        b["contract_edges"] = _contract_edges_for(rel, text, schema_nodes)
        bundles[rel] = b

    fingerprint = cg.compute_source_fingerprint(root, files)
    graph, meta = _assemble(files, schema_nodes, bundles, aliases, fingerprint)
    export_bytes = cg.serialize(graph)
    return AssemblyResult(
        export_bytes=export_bytes, graph=graph, meta=meta, bundles=bundles,
        schema_nodes=schema_nodes, input_files=files, aliases=aliases,
        files_parsed=files_parsed, files_reused=files_reused)
