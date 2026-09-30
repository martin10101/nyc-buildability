#!/usr/bin/env python3
"""Deterministic, stdlib-only code-navigation graph generator (task M0-T030, D-005 V1).

Emits graph.json + graph.meta.json into a cache directory OUTSIDE the
repository. The graph is an ADVISORY navigation index, never authoritative
truth (see tools/code_graph/README.md for the trust model).

Hard properties (acceptance scenarios AS-1..AS-5):
  * Deterministic: two generations over the same inputs are byte-identical.
    All collections are canonically sorted, output is LF-only, and NO
    wall-clock timestamp, username, or absolute path appears in artifacts.
  * Non-self-referential fingerprint: the source fingerprint is computed
    ONLY over the canonical input source files (sorted relpath + sha256 of
    CRLF-normalized bytes). Generated artifacts, excluded trees, and report
    files are never inputs, so the graph can never invalidate itself.
  * Honesty labels: every edge carries confidence in
    {exact, derived, partial, unresolved}. Nothing is guessed: an import
    that cannot be resolved inside the indexed tree is emitted as
    "unresolved" with its raw specifier. V1 emits NO caller/callee edge of
    any kind (owner clarification 1).
  * Stdlib only. No compiler, no third-party parser, no network.

CLI:
  python tools/code_graph/generate.py --repo PATH [--out DIR] [--check]
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

GENERATOR_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0.0"
MODE = "code-only"

ALLOWED_CONFIDENCES = ("exact", "derived", "partial", "unresolved")

# Directory NAMES hard-excluded anywhere in the walk (AS-4). Recorded in meta.
EXCLUDE_DIRS = (
    ".git",
    ".claude",
    "node_modules",
    ".next",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    ".mypy_cache",
    ".ruff_cache",
    "_quarantine",
    "graphify-out",
    ".cache",
)

# Include roots (repo-relative) and the patterns they admit.
INCLUDE_ROOTS = (
    {"root": "services/api", "patterns": ["**/*.py"]},
    {"root": "tools", "patterns": ["**/*.py"]},
    {"root": "apps/web/src", "patterns": ["**/*.ts", "**/*.tsx"]},
    {
        "root": "packages/contracts",
        "patterns": ["**/*.py", "schemas/**/*.schema.json", "generated/*.ts"],
    },
)

# Roots against which dotted Python import specifiers are resolved ("" = repo
# root). Sibling-directory resolution (script dir, mirroring sys.path[0]) is
# tried first; see _PyIndex.resolve().
PY_RESOLUTION_ROOTS = ("services/api", "tools", "packages/contracts", "")

SCHEMA_DIR_PREFIX = "packages/contracts/schemas/"
SCHEMA_SUFFIX = ".schema.json"


# --------------------------------------------------------------------------
# path helpers
# --------------------------------------------------------------------------

def _posix(path: str) -> str:
    return path.replace("\\", "/")


def _is_test_path(relpath: str) -> bool:
    """Task-packet rule: path contains /tests/ or basename test_*.py / *.test.ts*."""
    base = relpath.rsplit("/", 1)[-1]
    if "/tests/" in "/" + relpath + "/":
        return True
    if base.startswith("test_") and base.endswith(".py"):
        return True
    if re.search(r"\.test\.tsx?$", base):
        return True
    return False


def _matches_root(root: str, rel_in_root: str) -> bool:
    if root in ("services/api", "tools"):
        return rel_in_root.endswith(".py")
    if root == "apps/web/src":
        return rel_in_root.endswith((".ts", ".tsx"))
    if root == "packages/contracts":
        if rel_in_root.endswith(".py"):
            return True
        if rel_in_root.startswith("schemas/") and rel_in_root.endswith(SCHEMA_SUFFIX):
            return True
        if rel_in_root.startswith("generated/") and rel_in_root.endswith(".ts"):
            return "/" not in rel_in_root[len("generated/"):]
        return False
    return False


def scan_input_files(repo_root: str) -> list[str]:
    """Sorted repo-relative posix paths of every input source file."""
    found: set[str] = set()
    for spec in INCLUDE_ROOTS:
        root_abs = os.path.join(repo_root, *spec["root"].split("/"))
        if not os.path.isdir(root_abs):
            continue
        for dirpath, dirnames, filenames in os.walk(root_abs, topdown=True):
            dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS)
            for name in sorted(filenames):
                abspath = os.path.join(dirpath, name)
                rel_in_root = _posix(os.path.relpath(abspath, root_abs))
                if _matches_root(spec["root"], rel_in_root):
                    found.add(spec["root"] + "/" + rel_in_root)
    return sorted(found)


# --------------------------------------------------------------------------
# fingerprint (non-self-referential; AS-3)
# --------------------------------------------------------------------------

FINGERPRINT_ALGORITHM = (
    "sha256 over the relpath-sorted sequence of 'relpath\\0sha256(bytes with "
    "b\"\\r\\n\" replaced by b\"\\n\")\\n' for every included input source file; "
    "generated artifacts, excluded directories, and report files are never inputs."
)


def compute_source_fingerprint(repo_root: str, files: list[str] | None = None) -> str:
    if files is None:
        files = scan_input_files(repo_root)
    outer = hashlib.sha256()
    for rel in files:
        with open(os.path.join(repo_root, *rel.split("/")), "rb") as fh:
            data = fh.read().replace(b"\r\n", b"\n")
        inner = hashlib.sha256(data).hexdigest()
        outer.update(rel.encode("utf-8") + b"\0" + inner.encode("ascii") + b"\n")
    return outer.hexdigest()


# --------------------------------------------------------------------------
# Python extraction (ast)
# --------------------------------------------------------------------------

def _py_module_keys(relpath: str) -> list[tuple[str, str]]:
    """(resolution_root, dotted_key) pairs for a python file."""
    keys = []
    no_ext = relpath[: -len(".py")]
    parts = no_ext.split("/")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    for root in PY_RESOLUTION_ROOTS:
        if root == "":
            keys.append(("", ".".join(parts)))
        elif relpath.startswith(root + "/"):
            sub = parts[len(root.split("/")):]
            if sub:
                keys.append((root, ".".join(sub)))
    return keys


class _PyIndex:
    """Resolution index over the indexed python files."""

    def __init__(self, py_files: list[str]):
        self.files = set(py_files)
        self.key_map: dict[str, set[str]] = {}
        self.internal_tops: set[str] = set()
        self.module_attr: dict[str, str] = {}
        for rel in py_files:
            keys = _py_module_keys(rel)
            for _root, key in keys:
                self.key_map.setdefault(key, set()).add(rel)
                self.internal_tops.add(key.split(".")[0])
            # module attr: dotted name under the longest non-root resolution root
            named = [k for r, k in keys if r != ""]
            self.module_attr[rel] = named[0] if named else keys[0][1]

    def path_candidate(self, base_parts: list[str]) -> str | None:
        cand = "/".join(base_parts)
        if cand + ".py" in self.files:
            return cand + ".py"
        if cand + "/__init__.py" in self.files:
            return cand + "/__init__.py"
        return None

    def resolve(self, spec: str, importer_rel: str) -> str | None:
        """Unique internal resolution of an absolute dotted specifier, or None."""
        spec_parts = spec.split(".")
        # 1. sibling/script-dir resolution (mirrors sys.path[0] for scripts)
        importer_dir = importer_rel.rsplit("/", 1)[0] if "/" in importer_rel else ""
        base = (importer_dir.split("/") if importer_dir else []) + spec_parts
        hit = self.path_candidate(base)
        if hit is not None:
            return hit
        # 2. resolution-root keys; ambiguity is NEVER guessed
        hits = self.key_map.get(spec, set())
        if len(hits) == 1:
            return next(iter(hits))
        return None


def _extract_py_symbols(relpath: str, tree: ast.AST, is_test: bool) -> list[dict]:
    symbols: list[dict] = []

    def visit(node: ast.AST, qual: list[str], in_class: bool) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                q = qual + [child.name]
                symbols.append(
                    {
                        "id": relpath + "#" + ".".join(q),
                        "kind": "class",
                        "path": relpath,
                        "line": child.lineno,
                        "qualname": ".".join(q),
                        "confidence": "exact",
                        "is_test": is_test,
                    }
                )
                visit(child, q, True)
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = qual + [child.name]
                symbols.append(
                    {
                        "id": relpath + "#" + ".".join(q),
                        "kind": "method" if in_class else "function",
                        "path": relpath,
                        "line": child.lineno,
                        "qualname": ".".join(q),
                        "confidence": "exact",
                        "is_test": is_test,
                    }
                )
                visit(child, q, False)
            else:
                visit(child, qual, in_class)

    visit(tree, [], False)
    return symbols


def _py_import_edge(edges, index, importer_rel, spec, line, type_="import"):
    """Emit one honesty-labeled edge for an absolute dotted import specifier."""
    resolved = index.resolve(spec, importer_rel)
    if resolved is not None:
        edges.add_edge(
            type_, importer_rel, resolved, "exact", line, spec, "internal"
        )
        return
    top = spec.split(".")[0]
    if top in index.internal_tops:
        # internal-looking but not resolvable inside the indexed tree
        edges.add_edge(
            type_, importer_rel, "unresolved:" + spec, "unresolved", line, spec,
            "unresolved",
        )
    else:
        # external package: the import is an exact syntactic fact, the target
        # merely lives outside the indexed tree.
        edges.add_edge(
            type_, importer_rel, "external:" + top, "exact", line, spec, "external"
        )
        edges.external(top)


def _extract_py(relpath: str, text: str, index: _PyIndex, edges) -> list[dict]:
    is_test = _is_test_path(relpath)
    node: dict = {
        "id": relpath,
        "kind": "py_module",
        "path": relpath,
        "module": index.module_attr[relpath],
        "is_test": is_test,
    }
    try:
        tree = ast.parse(text)
    except SyntaxError:
        node["parse_error"] = True
        return [node]

    symbols = _extract_py_symbols(relpath, tree, is_test)

    pkg_dir = relpath.rsplit("/", 1)[0] if "/" in relpath else ""
    pkg_parts = pkg_dir.split("/") if pkg_dir else []

    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for alias in n.names:
                _py_import_edge(edges, index, relpath, alias.name, n.lineno)
        elif isinstance(n, ast.ImportFrom):
            if n.level and n.level > 0:
                # relative import: resolve against the containing package dir
                up = n.level - 1
                if up > len(pkg_parts):
                    spec = "." * n.level + (n.module or "")
                    edges.add_edge(
                        "import", relpath, "unresolved:" + spec, "unresolved",
                        n.lineno, spec, "unresolved",
                    )
                    continue
                base = pkg_parts[: len(pkg_parts) - up] if up else list(pkg_parts)
                mod_parts = n.module.split(".") if n.module else []
                target = index.path_candidate(base + mod_parts)
                emitted = False
                for alias in n.names:
                    if alias.name == "*":
                        continue
                    sub = index.path_candidate(base + mod_parts + [alias.name])
                    if sub is not None:
                        edges.add_edge(
                            "import", relpath, sub, "exact", n.lineno,
                            "." * n.level + (n.module or "") + "." + alias.name,
                            "internal",
                        )
                        emitted = True
                if target is not None:
                    edges.add_edge(
                        "import", relpath, target, "exact", n.lineno,
                        "." * n.level + (n.module or ""), "internal",
                    )
                elif not emitted:
                    spec = "." * n.level + (n.module or "")
                    edges.add_edge(
                        "import", relpath, "unresolved:" + spec, "unresolved",
                        n.lineno, spec, "unresolved",
                    )
            elif n.module:
                # absolute `from X import a, b`: edge to X; plus edges to X.a
                # when X.a is itself a uniquely indexed module.
                _py_import_edge(edges, index, relpath, n.module, n.lineno)
                for alias in n.names:
                    if alias.name == "*":
                        continue
                    sub = index.resolve(n.module + "." + alias.name, relpath)
                    if sub is not None:
                        edges.add_edge(
                            "import", relpath, sub, "exact", n.lineno,
                            n.module + "." + alias.name, "internal",
                        )
    return [node] + symbols


# --------------------------------------------------------------------------
# TypeScript / TSX extraction (line-based state machine, NO compiler)
# --------------------------------------------------------------------------

_TS_FROM_RE = re.compile(r"""\bfrom\s*(['"])([^'"]+)\1""")
_TS_SIDE_EFFECT_RE = re.compile(r"""^\s*import\s*(['"])([^'"]+)\1""")
_TS_DYNAMIC_RE = re.compile(r"""\bimport\s*\(\s*(['"])([^'"]+)\1\s*\)""")
_TS_EXPORT_DECL_RE = re.compile(
    r"""^\s*export\s+(?:declare\s+)?(?:default\s+)?(?:async\s+)?(?:abstract\s+)?"""
    r"""(const|let|var|function\*?|class|interface|enum|type|namespace)\s+"""
    r"""([A-Za-z_$][\w$]*)"""
)
_TS_EXPORT_DEFAULT_RE = re.compile(r"""^\s*export\s+default\b""")
_TS_EXPORT_BRACE_RE = re.compile(r"""^\s*export\s+(?:type\s+)?\{""")
_TS_STMT_START_RE = re.compile(r"""^\s*(?:import|export)\b""")
_TS_STAR_REEXPORT_RE = re.compile(r"""^\s*export\s+(?:type\s+)?\*""")


def _scrub_ts_comments(lines: list[str]) -> list[tuple[int, str]]:
    """Remove // and /* */ comments (line-level state machine, string-naive:
    a documented blind spot — comment markers inside string literals are
    treated as comments)."""
    out: list[tuple[int, str]] = []
    in_block = False
    for i, raw in enumerate(lines, 1):
        parts: list[str] = []
        j = 0
        while j < len(raw):
            if in_block:
                k = raw.find("*/", j)
                if k == -1:
                    j = len(raw)
                else:
                    in_block = False
                    j = k + 2
            else:
                bc = raw.find("/*", j)
                lc = raw.find("//", j)
                if bc == -1 and lc == -1:
                    parts.append(raw[j:])
                    j = len(raw)
                elif lc != -1 and (bc == -1 or lc < bc):
                    parts.append(raw[j:lc])
                    j = len(raw)
                else:
                    parts.append(raw[j:bc])
                    in_block = True
                    j = bc + 2
        out.append((i, "".join(parts)))
    return out


def _load_ts_aliases(repo_root: str) -> list[list[str]]:
    """[alias_prefix, repo-relative target_prefix] pairs, e.g. ['@/', 'apps/web/src/'].

    Read from apps/web/tsconfig.json (compilerOptions.paths, '*' wildcards);
    falls back to the documented default when the file is absent/unparseable.
    """
    default = [["@/", "apps/web/src/"]]
    cfg = os.path.join(repo_root, "apps", "web", "tsconfig.json")
    try:
        with open(cfg, "rb") as fh:
            raw = fh.read().decode("utf-8", errors="replace")
        # tolerate // comment lines (tsconfig is JSONC)
        raw = "\n".join(
            l for l in raw.split("\n") if not l.lstrip().startswith("//")
        )
        data = json.loads(raw)
        paths = data.get("compilerOptions", {}).get("paths", {})
        aliases: list[list[str]] = []
        for pat, targets in sorted(paths.items()):
            if not pat.endswith("/*") or not targets:
                continue
            target = targets[0]
            if not target.endswith("/*"):
                continue
            tprefix = target[:-1]
            if tprefix.startswith("./"):
                tprefix = tprefix[2:]
            aliases.append([pat[:-1], "apps/web/" + tprefix])
        return aliases or default
    except (OSError, ValueError):
        return default


class _TsResolver:
    _SUFFIXES = ("", ".ts", ".tsx", "/index.ts", "/index.tsx")

    def __init__(self, indexed_files: set[str], aliases: list[list[str]]):
        self.files = indexed_files
        self.aliases = aliases

    def _try(self, base: str) -> str | None:
        base = _posix(os.path.normpath(base))
        for suf in self._SUFFIXES:
            if base + suf in self.files:
                return base + suf
        return None

    def resolve(self, spec: str, importer_rel: str) -> tuple[str | None, bool]:
        """(resolved relpath | None, internal_looking)."""
        for alias_prefix, target_prefix in self.aliases:
            if spec.startswith(alias_prefix):
                return self._try(target_prefix + spec[len(alias_prefix):]), True
        if spec.startswith(("./", "../")):
            importer_dir = importer_rel.rsplit("/", 1)[0]
            return self._try(importer_dir + "/" + spec), True
        if spec.startswith("/"):
            return None, True
        return None, False  # bare specifier: external package


def _ts_external_name(spec: str) -> str:
    if spec.startswith("@"):
        parts = spec.split("/")
        return "/".join(parts[:2]) if len(parts) >= 2 else parts[0]
    return spec.split("/")[0]


def _ts_edge(edges, resolver, importer_rel, spec, line, type_, base_confidence):
    resolved, internal_looking = resolver.resolve(spec, importer_rel)
    if resolved is not None:
        edges.add_edge(type_, importer_rel, resolved, base_confidence, line, spec,
                       "internal")
    elif internal_looking:
        edges.add_edge(type_, importer_rel, "unresolved:" + spec, "unresolved",
                       line, spec, "unresolved")
    else:
        name = _ts_external_name(spec)
        edges.add_edge(type_, importer_rel, "external:" + name, "exact", line,
                       spec, "external")
        edges.external(name)


def _extract_ts(relpath: str, text: str, resolver: _TsResolver, edges) -> list[dict]:
    is_test = _is_test_path(relpath)
    nodes: dict[str, dict] = {
        relpath: {
            "id": relpath,
            "kind": "ts_module",
            "path": relpath,
            "is_test": is_test,
        }
    }

    def add_symbol(name: str, line: int, confidence: str) -> None:
        nid = relpath + "#" + name
        if nid not in nodes:
            nodes[nid] = {
                "id": nid,
                "kind": "ts_symbol",
                "path": relpath,
                "line": line,
                "qualname": name,
                "confidence": confidence,
                "is_test": is_test,
            }

    def parse_brace_names(stmt: str, line: int) -> None:
        m = re.search(r"\{([^}]*)\}", stmt)
        if not m:
            return
        for entry in m.group(1).split(","):
            entry = entry.strip()
            if not entry:
                continue
            entry = re.sub(r"^type\s+", "", entry)
            am = re.match(r"^([A-Za-z_$][\w$]*)(?:\s+as\s+([A-Za-z_$][\w$]*))?$",
                          entry)
            if am:
                add_symbol(am.group(2) or am.group(1), line, "exact")

    scrubbed = _scrub_ts_comments(text.split("\n"))
    buf_start = 0
    buf = ""
    buf_lines = 0

    def flush() -> None:
        nonlocal buf, buf_lines
        buf = ""
        buf_lines = 0

    def process(stmt: str, line: int) -> bool:
        """True when the buffered statement was consumed."""
        stripped = stmt.lstrip()
        m = _TS_FROM_RE.search(stmt)
        if m:
            spec = m.group(2)
            if stripped.startswith("export"):
                if _TS_STAR_REEXPORT_RE.match(stmt):
                    # star re-export: target module is a syntactic fact, the
                    # symbol set is NOT enumerable without a compiler => partial
                    _ts_edge(edges, resolver, relpath, spec, line, "reexport",
                             "partial")
                else:
                    _ts_edge(edges, resolver, relpath, spec, line, "reexport",
                             "exact")
                    parse_brace_names(stmt, line)
            else:
                _ts_edge(edges, resolver, relpath, spec, line, "import", "exact")
            return True
        m = _TS_SIDE_EFFECT_RE.match(stmt)
        if m:
            _ts_edge(edges, resolver, relpath, m.group(2), line, "import", "exact")
            return True
        m = _TS_EXPORT_DECL_RE.match(stmt)
        if m:
            add_symbol(m.group(2), line, "exact")
            return True
        if _TS_EXPORT_BRACE_RE.match(stmt):
            if "}" not in stmt:
                return False  # keep buffering the name list
            parse_brace_names(stmt, line)
            return True
        if _TS_EXPORT_DEFAULT_RE.match(stmt):
            add_symbol("default", line, "exact")
            return True
        return False

    for lineno, line in scrubbed:
        for dm in _TS_DYNAMIC_RE.finditer(line):
            # dynamic import with a literal specifier: extractable, but the
            # load is runtime-conditional => partial by design (README).
            spec = dm.group(2)
            resolved, internal_looking = resolver.resolve(spec, relpath)
            if resolved is not None:
                edges.add_edge("dynamic_import", relpath, resolved, "partial",
                               lineno, spec, "internal")
            elif internal_looking:
                edges.add_edge("dynamic_import", relpath, "unresolved:" + spec,
                               "unresolved", lineno, spec, "unresolved")
            else:
                name = _ts_external_name(spec)
                edges.add_edge("dynamic_import", relpath, "external:" + name,
                               "partial", lineno, spec, "external")
                edges.external(name)
        if not buf:
            if not _TS_STMT_START_RE.match(line):
                continue
            buf_start = lineno
            buf = line
            buf_lines = 1
        else:
            buf += " " + line
            buf_lines += 1
        if process(buf, buf_start):
            flush()
        elif (
            buf.rstrip().endswith(";")
            or buf_lines > 40
            or len(buf) > 4000
        ):
            flush()

    return list(nodes.values())


# --------------------------------------------------------------------------
# contract touchpoints (derived heuristic; README documents the noise)
# --------------------------------------------------------------------------

def _contract_edges(files_text: dict[str, str], schema_nodes: list[dict], edges):
    for rel, text in sorted(files_text.items()):
        for schema in schema_nodes:
            if schema["path"] == rel:
                continue
            candidates = [
                schema["path"].rsplit("/", 1)[-1],  # e.g. property_profile.schema.json
                schema["stem"],                      # e.g. property_profile
            ]
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
                edges.add_edge(
                    "contract_ref", rel, schema["path"], "derived", line,
                    best[1], "internal",
                )


# --------------------------------------------------------------------------
# edge/node collection
# --------------------------------------------------------------------------

class _EdgeSet:
    def __init__(self) -> None:
        self._edges: dict[tuple, dict] = {}
        self.externals: set[str] = set()

    def add_edge(self, type_, frm, to, confidence, line, specifier, resolution):
        if confidence not in ALLOWED_CONFIDENCES:
            raise ValueError("unlabeled edge confidence: %r" % (confidence,))
        key = (type_, frm, to, specifier, line)
        self._edges[key] = {
            "type": type_,
            "from": frm,
            "to": to,
            "confidence": confidence,
            "line": line,
            "specifier": specifier,
            "resolution": resolution,
        }

    def external(self, name: str) -> None:
        self.externals.add(name)

    def sorted_edges(self) -> list[dict]:
        return [self._edges[k] for k in sorted(self._edges)]


def build_graph(repo_root: str) -> tuple[dict, dict, list[str]]:
    """(graph, meta, input_files). Pure function of the input file bytes."""
    input_files = scan_input_files(repo_root)
    files_text: dict[str, str] = {}
    for rel in input_files:
        with open(os.path.join(repo_root, *rel.split("/")), "rb") as fh:
            files_text[rel] = fh.read().replace(b"\r\n", b"\n").decode(
                "utf-8", errors="replace"
            )

    py_files = [f for f in input_files if f.endswith(".py")]
    ts_files = [f for f in input_files if f.endswith((".ts", ".tsx"))]
    schema_files = [
        f
        for f in input_files
        if f.startswith(SCHEMA_DIR_PREFIX) and f.endswith(SCHEMA_SUFFIX)
    ]

    index = _PyIndex(py_files)
    aliases = _load_ts_aliases(repo_root)
    resolver = _TsResolver(set(ts_files), aliases)
    edges = _EdgeSet()
    nodes: dict[str, dict] = {}

    def add_nodes(items: list[dict]) -> None:
        for item in items:
            nodes.setdefault(item["id"], item)

    schema_nodes: list[dict] = []
    for rel in schema_files:
        stem = rel.rsplit("/", 1)[-1][: -len(SCHEMA_SUFFIX)]
        schema_id = ""
        try:
            schema_id = str(json.loads(files_text[rel]).get("$id", "") or "")
        except ValueError:
            pass
        node = {
            "id": rel,
            "kind": "contract_schema",
            "path": rel,
            "stem": stem,
            "schema_id": schema_id,
            "is_test": _is_test_path(rel),
        }
        schema_nodes.append(node)
        add_nodes([node])

    for rel in py_files:
        add_nodes(_extract_py(rel, files_text[rel], index, edges))
    for rel in ts_files:
        add_nodes(_extract_ts(rel, files_text[rel], resolver, edges))

    _contract_edges(files_text, schema_nodes, edges)

    for name in sorted(edges.externals):
        nodes.setdefault(
            "external:" + name,
            {"id": "external:" + name, "kind": "external", "name": name},
        )

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

    fingerprint = compute_source_fingerprint(repo_root, input_files)

    graph = {
        "schema_version": SCHEMA_VERSION,
        "nodes": sorted_nodes,
        "edges": sorted_edges,
    }
    meta = {
        "schema_version": SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "mode": MODE,
        "source_fingerprint": fingerprint,
        "fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "include_roots": [
            {"root": s["root"], "patterns": list(s["patterns"])}
            for s in INCLUDE_ROOTS
        ],
        "exclude_dirs": list(EXCLUDE_DIRS),
        "ts_aliases": aliases,
        "input_file_count": len(input_files),
        "node_counts": node_counts,
        "edge_counts": {
            "by_type": edge_by_type,
            "by_confidence": edge_by_conf,
            "by_language_confidence": by_lang_conf,
        },
    }
    return graph, meta, input_files


# --------------------------------------------------------------------------
# serialization + output location
# --------------------------------------------------------------------------

def serialize(obj: dict) -> bytes:
    """Canonical LF-only bytes: sort_keys + indent=1 + trailing newline."""
    return (json.dumps(obj, sort_keys=True, indent=1) + "\n").encode("utf-8")


def default_out_dir(repo_root: str) -> str:
    """--out DIR explicit > env CODEGRAPH_CACHE_DIR > platform cache dir.

    The cache is always keyed by the repo-root basename so two checkouts
    never share artifacts.
    """
    basename = os.path.basename(os.path.abspath(repo_root).rstrip("/\\")) or "repo"
    env = os.environ.get("CODEGRAPH_CACHE_DIR")
    if env:
        return os.path.join(env, basename)
    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA")
        if local:
            return os.path.join(local, "nyc-codegraph", basename)
    return os.path.join(os.path.expanduser("~"), ".cache", "nyc-codegraph", basename)


def _assert_outside_repo(out_dir: str, repo_root: str) -> None:
    out_abs = os.path.realpath(os.path.abspath(out_dir))
    repo_abs = os.path.realpath(os.path.abspath(repo_root))
    try:
        common = os.path.commonpath([out_abs, repo_abs])
    except ValueError:
        return  # different drives: definitely outside
    if common == repo_abs:
        raise SystemExit(
            "refusing to write artifacts inside the repository: " + out_dir
        )


def generate_into(repo_root: str, out_dir: str) -> dict:
    _assert_outside_repo(out_dir, repo_root)
    graph, meta, _ = build_graph(repo_root)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "graph.json"), "wb") as fh:
        fh.write(serialize(graph))
    with open(os.path.join(out_dir, "graph.meta.json"), "wb") as fh:
        fh.write(serialize(meta))
    return meta


def run_check(repo_root: str) -> int:
    """Determinism self-proof: two FRESH generations must be byte-identical.

    Never consults a committed or cached artifact.
    """
    dir_a = tempfile.mkdtemp(prefix="codegraph-check-a-")
    dir_b = tempfile.mkdtemp(prefix="codegraph-check-b-")
    try:
        meta = generate_into(repo_root, dir_a)
        generate_into(repo_root, dir_b)
        ok = True
        for name in ("graph.json", "graph.meta.json"):
            with open(os.path.join(dir_a, name), "rb") as fh:
                a = fh.read()
            with open(os.path.join(dir_b, name), "rb") as fh:
                b = fh.read()
            if a != b:
                ok = False
                print("DETERMINISM FAILURE: %s differs between generations" % name)
        if ok:
            print(
                "determinism check PASS: 2 generations byte-identical "
                "(%d input files, fingerprint %s)"
                % (meta["input_file_count"], meta["source_fingerprint"][:16])
            )
            return 0
        return 1
    finally:
        shutil.rmtree(dir_a, ignore_errors=True)
        shutil.rmtree(dir_b, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(
        description="Deterministic stdlib-only code-navigation graph generator "
        "(advisory index; see tools/code_graph/README.md)."
    )
    parser.add_argument("--repo", required=True, help="repository root to index")
    parser.add_argument("--out", default=None, help="explicit artifact directory")
    parser.add_argument(
        "--check",
        action="store_true",
        help="determinism self-proof: two fresh generations must be byte-identical",
    )
    args = parser.parse_args(argv)

    repo_root = os.path.abspath(args.repo)
    if not os.path.isdir(repo_root):
        print("not a directory: %s" % repo_root)
        return 2

    if args.check:
        return run_check(repo_root)

    out_dir = args.out if args.out else default_out_dir(repo_root)
    meta = generate_into(repo_root, out_dir)
    print(
        "generated graph.json + graph.meta.json (%d input files, %d nodes, %d edges) -> %s"
        % (
            meta["input_file_count"],
            sum(meta["node_counts"].values()),
            sum(meta["edge_counts"]["by_type"].values()),
            out_dir,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
