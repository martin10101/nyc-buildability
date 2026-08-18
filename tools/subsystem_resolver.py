#!/usr/bin/env python3
"""Versioned deterministic subsystem/ontology resolver (M0-T066 Unit C, D-013).

Establishes the ONE closed subsystem vocabulary for memory placement BEFORE any
memory digest may reference it (D-013-R043). The vocabulary is NOT a second
free-form taxonomy (R008): every subsystem id IS an existing repo-relative
directory prefix, enforced structurally at load time — a rule whose id differs
from its prefix, or whose prefix is not a real directory, fails the load.

Resolution is pure deterministic code (R009/R045): ordered longest-prefix match
on whole path segments. A path matching no rule is `unresolved` with a
machine-readable reason, never a guessed bucket. All failures are fail-closed
(R013-style): malformed map, unknown schema version, duplicate/free-form rules,
or a missing map file raise `SubsystemMapError` and the CLI exits nonzero with
a machine-readable error document — never a silent default vocabulary.

Version binding (R028/R044): `version_stamp()` exports resolver_version,
map_schema_version, map_version, and map_digest (sha256 over the exact map
bytes) so downstream fingerprints and Unit D memory digests can bind the
ontology version.

Honest graph kinds (R018): `report_graph_kinds()` enumerates the node/edge
kinds ACTUALLY present in the accepted A1/A2 index export and labels subsystem
as a resolver-layer mapping; it never injects a subsystem node into the graph.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.context_pack_io import canon_json_bytes  # noqa: E402

#: Bound into downstream fingerprints/digests (D-013-R028/R044). Bump on any
#: behavior change to resolution, validation, or output shape.
RESOLVER_VERSION = "1.0.0"

#: Map schema versions this resolver understands. Anything else fails closed.
KNOWN_MAP_SCHEMA_VERSIONS = ("1.0.0",)

DEFAULT_MAP_PATH = pathlib.Path(__file__).resolve().parent / "subsystem_map.json"


class SubsystemMapError(Exception):
    """Fail-closed map/validation error with a machine-readable reason code."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")

    def doc(self) -> dict:
        return {"error": {"code": self.code, "detail": self.detail}}


def norm_path(path: str) -> str:
    """Repo-relative POSIX normalization (matches the index/pack convention)."""
    s = str(path).strip().replace("\\", "/")
    while s.startswith("./"):
        s = s[2:]
    return s.strip("/")


def _validate_rule(rule: object, position: int, repo_root: pathlib.Path) -> str:
    if not isinstance(rule, dict):
        raise SubsystemMapError("rule_not_object", f"rules[{position}] is not an object")
    sid = rule.get("subsystem_id")
    prefix = rule.get("prefix")
    if not isinstance(sid, str) or not isinstance(prefix, str) or not sid or not prefix:
        raise SubsystemMapError(
            "rule_missing_fields",
            f"rules[{position}] needs non-empty string subsystem_id and prefix")
    if sid != prefix:
        # The structural R008 guarantee: an id that is not literally its path
        # prefix would be a free-form taxonomy name.
        raise SubsystemMapError(
            "free_form_subsystem_id",
            f"rules[{position}]: subsystem_id {sid!r} != prefix {prefix!r} "
            "(closed vocabulary requires id == existing path prefix, D-013-R008)")
    if norm_path(prefix) != prefix or ".." in prefix.split("/"):
        raise SubsystemMapError(
            "rule_prefix_not_normalized",
            f"rules[{position}]: prefix {prefix!r} must be a normalized "
            "repo-relative POSIX path without '..'")
    if not (repo_root / prefix).is_dir():
        raise SubsystemMapError(
            "prefix_not_in_tree",
            f"rules[{position}]: prefix {prefix!r} is not an existing directory "
            "under the repository root (vocabulary must be existing paths)")
    return prefix


def load_map(repo_root: str, map_path: str | None = None) -> dict:
    """Load + validate the versioned map; fail closed on ANY defect.

    Returns {"map": <parsed>, "map_digest": sha256 over CRLF-normalized map
    bytes (same convention as the A1 fingerprint, so Windows/CRLF and CI/LF
    checkouts stamp the identical ontology digest), "rules_by_depth":
    prefixes longest-first}.
    """
    root = pathlib.Path(repo_root).resolve()
    path = pathlib.Path(map_path) if map_path else DEFAULT_MAP_PATH
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise SubsystemMapError("map_unreadable", f"{path}: {exc}") from exc
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SubsystemMapError("map_malformed_json", f"{path}: {exc}") from exc
    if not isinstance(doc, dict):
        raise SubsystemMapError("map_not_object", f"{path}: top level is not an object")
    schema = doc.get("map_schema_version")
    if schema not in KNOWN_MAP_SCHEMA_VERSIONS:
        raise SubsystemMapError(
            "unknown_map_schema_version",
            f"{schema!r} not in known {list(KNOWN_MAP_SCHEMA_VERSIONS)}")
    if not isinstance(doc.get("map_version"), str) or not doc["map_version"]:
        raise SubsystemMapError("missing_map_version", "map_version must be a non-empty string")
    rules = doc.get("rules")
    if not isinstance(rules, list) or not rules:
        raise SubsystemMapError("rules_missing", "rules must be a non-empty list")
    seen: set[str] = set()
    prefixes: list[str] = []
    for i, rule in enumerate(rules):
        prefix = _validate_rule(rule, i, root)
        if prefix in seen:
            raise SubsystemMapError("duplicate_rule_prefix", f"duplicate prefix {prefix!r}")
        seen.add(prefix)
        prefixes.append(prefix)
    by_depth = sorted(prefixes, key=lambda p: (-len(p.split("/")), p))
    return {
        "map": doc,
        "map_digest": hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest(),
        "rules_by_depth": by_depth,
    }


def version_stamp(loaded: dict) -> dict:
    """The ontology-version binding record (D-013-R028/R044)."""
    return {
        "resolver_version": RESOLVER_VERSION,
        "map_schema_version": loaded["map"]["map_schema_version"],
        "map_version": loaded["map"]["map_version"],
        "map_digest": loaded["map_digest"],
    }


def resolve_path(path: str, loaded: dict) -> dict:
    """Longest-prefix (whole segments) path→subsystem derivation. Pure function.

    Existence of `path` itself is the entity layer's job (two-pass, R046);
    this derives the bucket only, or returns a machine-readable non-answer.
    """
    p = norm_path(path)
    if not p:
        return {"path": p, "resolved": False, "subsystem": None,
                "reason": "empty_path"}
    segs = p.split("/")
    for prefix in loaded["rules_by_depth"]:
        psegs = prefix.split("/")
        if segs[:len(psegs)] == psegs:
            return {"path": p, "resolved": True, "subsystem": prefix, "reason": None}
    return {"path": p, "resolved": False, "subsystem": None,
            "reason": "no_matching_subsystem_rule"}


def vocabulary(loaded: dict) -> dict:
    """The full validated closed vocabulary, deterministic order."""
    return {
        "version": version_stamp(loaded),
        "subsystems": sorted(r["subsystem_id"] for r in loaded["map"]["rules"]),
    }


def report_graph_kinds(repo_root: str, cache_base: str | None = None) -> dict:
    """Enumerate the ACTUAL node/edge kinds in the accepted index (D-013-R018).

    Builds the A1/A2 index in process (read-only consumption; graph bytes are
    never modified) and reports exactly the kinds present. Subsystem is
    explicitly labeled a resolver-layer mapping, never a graph node kind.
    """
    from tools import repo_index_incremental as inc
    res = inc.build_incremental(repo_root, cache_base=cache_base)
    graph = json.loads(res.export_bytes)
    node_kinds: dict[str, int] = {}
    for n in graph.get("nodes", []):
        node_kinds[n.get("kind", "<missing>")] = node_kinds.get(n.get("kind", "<missing>"), 0) + 1
    edge_types: dict[str, int] = {}
    for e in graph.get("edges", []):
        edge_types[e.get("type", "<missing>")] = edge_types.get(e.get("type", "<missing>"), 0) + 1
    return {
        "export_digest": res.export_digest(),
        "node_kinds": {k: node_kinds[k] for k in sorted(node_kinds)},
        "edge_types": {k: edge_types[k] for k in sorted(edge_types)},
        "subsystem_node_kind_in_graph": "subsystem" in node_kinds,
        "statement": ("'subsystem' is a resolver-layer mapping defined by "
                      "tools/subsystem_map.json + tools/subsystem_resolver.py; "
                      "the accepted code graph defines NO subsystem node kind and "
                      "this resolver never injects one (D-013-R018)."),
    }


def _emit(doc: dict) -> None:
    sys.stdout.write(canon_json_bytes(doc).decode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Versioned deterministic subsystem resolver (D-013 Unit C). "
                    "Advisory placement layer; source files remain authoritative.")
    ap.add_argument("--repo", default=str(_ROOT), help="repository root")
    ap.add_argument("--map", default=None, help="override map path (tests only)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_res = sub.add_parser("resolve", help="derive subsystem for repo-relative path(s)")
    p_res.add_argument("paths", nargs="+")
    sub.add_parser("vocabulary", help="print the validated closed vocabulary")
    sub.add_parser("version", help="print the ontology version stamp")
    sub.add_parser("kinds", help="report ACTUAL index node/edge kinds (R018)")
    sub.add_parser("check", help="determinism self-proof (two runs, byte-compare)")
    args = ap.parse_args(argv)

    try:
        loaded = load_map(args.repo, args.map)
    except SubsystemMapError as exc:
        _emit(exc.doc())
        return 2

    if args.cmd == "resolve":
        _emit({"version": version_stamp(loaded),
               "results": [resolve_path(p, loaded) for p in args.paths]})
        return 0
    if args.cmd == "vocabulary":
        _emit(vocabulary(loaded))
        return 0
    if args.cmd == "version":
        _emit(version_stamp(loaded))
        return 0
    if args.cmd == "kinds":
        try:
            _emit(report_graph_kinds(args.repo))
        except Exception as exc:  # fail closed, machine-readable (R013-style)
            _emit({"error": {"code": "index_unavailable",
                             "detail": f"{type(exc).__name__}: {exc}"}})
            return 2
        return 0
    if args.cmd == "check":
        sample = ["services/api/app/main.py", "tools/subsystem_resolver.py",
                  "apps/web/src/lib/api.ts", "README.md", "no/such/dir/x.py"]
        runs = []
        for _ in range(2):
            l2 = load_map(args.repo, args.map)
            runs.append(canon_json_bytes({
                "version": version_stamp(l2),
                "vocabulary": vocabulary(l2),
                "results": [resolve_path(p, l2) for p in sample]}))
        if runs[0] != runs[1]:
            _emit({"error": {"code": "nondeterministic_resolution",
                             "detail": "two identical runs produced different bytes"}})
            return 2
        _emit({"check": "PASS", "bytes": len(runs[0]),
               "version": version_stamp(loaded)})
        return 0
    return 2  # pragma: no cover — argparse enforces the subcommand set


if __name__ == "__main__":
    raise SystemExit(main())
