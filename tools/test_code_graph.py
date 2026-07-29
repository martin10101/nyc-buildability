#!/usr/bin/env python3
"""Stdlib-only test suite for the code-navigation index (task M0-T030).

Runs against TEMP FIXTURE repositories only (AS-7): nothing here depends on
the live repository's composition or the project ledger. Covers AS-2..AS-6:
determinism, non-self-referential fingerprint, pollution exclusion, honesty
labels (incl. NO caller/callee edges), resolution correctness (relative py
imports, ts '@/' alias, unresolved never guessed), bounded query output, and
the stale-fingerprint regeneration contract.

Run: python tools/test_code_graph.py   (exit 0 = pass)
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE_GRAPH_DIR = os.path.join(_HERE, "code_graph")
sys.path.insert(0, _CODE_GRAPH_DIR)
import generate  # noqa: E402

GENERATE_PY = os.path.join(_CODE_GRAPH_DIR, "generate.py")
QUERY_PY = os.path.join(_CODE_GRAPH_DIR, "query.py")


def _write(root: str, relpath: str, content: str) -> None:
    path = os.path.join(root, *relpath.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(content.encode("utf-8"))


def build_fixture_repo(root: str) -> None:
    """A tiny py+ts+schema tree exercising every extraction rule."""
    _write(root, "services/api/app/__init__.py", "")
    _write(root, "services/api/app/core.py",
           "import os\n"
           "import fastapi\n"
           "from app.util import helper\n")
    _write(root, "services/api/app/util.py",
           "def helper():\n    return 1\n")
    _write(root, "services/api/app/pkg/__init__.py", "")
    _write(root, "services/api/app/pkg/rel.py",
           "from .sib import thing\n"
           "from ..util import helper\n"
           "from app.nonexistent import gone\n")
    _write(root, "services/api/app/pkg/sib.py",
           "thing = 2\n\n\nclass Widget:\n    def method(self):\n        pass\n")
    _write(root, "services/api/tests/test_core.py",
           "import unittest\n")
    _write(root, "services/api/app/uses_schema.py",
           '"""Validates thing_profile.schema.json fixtures."""\nX = 1\n')
    _write(root, "tools/scriptone.py", "import scripttwo\n")
    _write(root, "tools/scripttwo.py", "VALUE = 3\n")
    _write(root, "apps/web/tsconfig.json",
           json.dumps({"compilerOptions": {"paths": {"@/*": ["./src/*"]}}}))
    _write(root, "apps/web/src/lib/x.ts",
           "export const x = 1;\nexport function fx() { return x; }\n")
    _write(root, "apps/web/src/app/page.tsx",
           "import { x } from '@/lib/x';\n"
           "import React from 'react';\n"
           "import missing from './missing';\n"
           "export default function Page() { return null; }\n")
    _write(root, "apps/web/src/lib/re.ts",
           "export * from './x';\nexport { fx } from './x';\n")
    _write(root, "apps/web/src/lib/dyn.ts",
           "export async function load() {\n"
           "  const m = await import('@/lib/x');\n"
           "  return m;\n"
           "}\n")
    _write(root, "apps/web/src/lib/widget.test.ts",
           "import { x } from '@/lib/x';\nexport const t = x;\n")
    _write(root, "packages/contracts/schemas/v1/thing_profile.schema.json",
           json.dumps({"$id": "https://example.test/thing_profile.schema.json",
                       "title": "Thing"}))
    _write(root, "packages/contracts/generated/thing_profile.ts",
           "export interface ThingProfile { a: string; }\n")


SENTINEL_DIRS = [
    ".claude/worktrees/husk",
    "node_modules/evil",
    "services/api/node_modules/evil",
    "services/api/.next/x",
    "services/api/__pycache__",
    "services/api/.pytest_cache/x",
    "services/api/.venv/lib",
    "tools/dist/x",
    "tools/build/x",
    "apps/web/src/coverage/x",
    ".git/hooks",
]


def plant_sentinels(root: str) -> list[str]:
    planted = []
    for d in SENTINEL_DIRS:
        for name in ("sentinel_%d.py" % len(planted),
                     "sentinel_%d.ts" % (len(planted) + 1)):
            rel = d + "/" + name
            _write(root, rel, "SENTINEL = True\n")
            planted.append(rel)
    return planted


def gen(root: str, out: str) -> dict:
    generate.generate_into(root, out)
    with open(os.path.join(out, "graph.json"), "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


def read_bytes(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def run_query(repo: str, cache: str, *args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["CODEGRAPH_CACHE_DIR"] = cache
    return subprocess.run(
        [sys.executable, QUERY_PY, "--repo", repo] + list(args),
        capture_output=True, text=True, env=env, timeout=120,
    )


class CodeGraphTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="codegraph-test-")
        self.base = self._tmp.name
        self.repo = os.path.join(self.base, "fixture-repo")
        os.makedirs(self.repo)
        build_fixture_repo(self.repo)
        self.cache = os.path.join(self.base, "cache")

    def tearDown(self):
        self._tmp.cleanup()

    def edges(self, graph, **filters):
        found = []
        for e in graph["edges"]:
            if all(e.get(k) == v for k, v in filters.items()):
                found.append(e)
        return found

    # ---- AS-2: determinism -------------------------------------------------

    def test_determinism_two_generations_byte_identical(self):
        out_a = os.path.join(self.base, "outA")
        out_b = os.path.join(self.base, "outB")
        generate.generate_into(self.repo, out_a)
        generate.generate_into(self.repo, out_b)
        for name in ("graph.json", "graph.meta.json"):
            a = read_bytes(os.path.join(out_a, name))
            b = read_bytes(os.path.join(out_b, name))
            self.assertEqual(a, b, "artifact %s not byte-identical" % name)
            self.assertNotIn(b"\r\n", a, "artifact %s not LF-only" % name)

    def test_check_flag_self_proof(self):
        proc = subprocess.run(
            [sys.executable, GENERATE_PY, "--repo", self.repo, "--check"],
            capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("determinism check PASS", proc.stdout)

    # ---- AS-3: non-self-referential fingerprint ----------------------------

    def test_fingerprint_changes_when_input_changes(self):
        fp1 = generate.compute_source_fingerprint(self.repo)
        _write(self.repo, "services/api/app/util.py",
               "def helper():\n    return 2\n")
        fp2 = generate.compute_source_fingerprint(self.repo)
        self.assertNotEqual(fp1, fp2)

    def test_fingerprint_ignores_excluded_dirs_artifacts_and_reports(self):
        fp1 = generate.compute_source_fingerprint(self.repo)
        # excluded trees
        plant_sentinels(self.repo)
        # generated artifacts (outside the repo by design, but also prove an
        # artifact-named file dropped at repo root is not an input)
        out = os.path.join(self.base, "out-fp")
        generate.generate_into(self.repo, out)
        _write(self.repo, "graph.json", '{"junk": true}')
        _write(self.repo, "graph.meta.json", '{"junk": true}')
        # report files
        _write(self.repo, "project-control/reports/some-report.md", "# r\n")
        fp2 = generate.compute_source_fingerprint(self.repo)
        self.assertEqual(fp1, fp2)
        # mutating an artifact in the cache dir does not change it either
        _write(out.replace("\\", "/"), "graph.json", '{"junk": 2}')
        self.assertEqual(fp1, generate.compute_source_fingerprint(self.repo))

    def test_fingerprint_is_crlf_invariant(self):
        fp1 = generate.compute_source_fingerprint(self.repo)
        path = os.path.join(self.repo, "services", "api", "app", "util.py")
        with open(path, "rb") as fh:
            data = fh.read()
        with open(path, "wb") as fh:
            fh.write(data.replace(b"\n", b"\r\n"))
        self.assertEqual(fp1, generate.compute_source_fingerprint(self.repo))

    # ---- AS-4: pollution exclusion -----------------------------------------

    def test_sentinel_files_never_indexed_and_exclusions_recorded(self):
        plant_sentinels(self.repo)
        out = os.path.join(self.base, "out-sent")
        graph = gen(self.repo, out)
        for node in graph["nodes"]:
            self.assertNotIn("sentinel_", node.get("path", node["id"]))
        with open(os.path.join(out, "graph.meta.json"), "rb") as fh:
            meta = json.loads(fh.read().decode("utf-8"))
        self.assertEqual(meta["exclude_dirs"], list(generate.EXCLUDE_DIRS))
        for required in (".git", ".claude", "node_modules", ".next", "dist",
                         "build", "coverage", "__pycache__", ".pytest_cache",
                         ".venv"):
            self.assertIn(required, meta["exclude_dirs"])

    # ---- AS-5: honesty labels ----------------------------------------------

    def test_every_edge_labeled_and_no_caller_callee(self):
        graph = gen(self.repo, os.path.join(self.base, "out-lab"))
        allowed_conf = set(generate.ALLOWED_CONFIDENCES)
        allowed_types = {"import", "reexport", "dynamic_import", "contract_ref"}
        self.assertGreater(len(graph["edges"]), 0)
        for e in graph["edges"]:
            self.assertIn(e.get("confidence"), allowed_conf, e)
            self.assertIn(e.get("type"), allowed_types, e)
            for banned in ("call", "caller", "callee", "invoke"):
                self.assertNotIn(banned, e["type"])
            self.assertIn("from", e)
            self.assertIn("to", e)
            self.assertIn("specifier", e)

    def test_relative_py_imports_resolve_exact(self):
        graph = gen(self.repo, os.path.join(self.base, "out-rel"))
        hits = self.edges(graph, **{"from": "services/api/app/pkg/rel.py",
                                    "to": "services/api/app/pkg/sib.py"})
        self.assertTrue(hits, "from .sib import thing did not resolve")
        self.assertTrue(all(e["confidence"] == "exact" for e in hits))
        hits = self.edges(graph, **{"from": "services/api/app/pkg/rel.py",
                                    "to": "services/api/app/util.py"})
        self.assertTrue(hits, "from ..util import helper did not resolve")

    def test_absolute_py_import_resolves_exact(self):
        graph = gen(self.repo, os.path.join(self.base, "out-abs"))
        hits = self.edges(graph, **{"from": "services/api/app/core.py",
                                    "to": "services/api/app/util.py"})
        self.assertTrue(hits, "from app.util import helper did not resolve")

    def test_sibling_script_import_resolves(self):
        graph = gen(self.repo, os.path.join(self.base, "out-sib"))
        hits = self.edges(graph, **{"from": "tools/scriptone.py",
                                    "to": "tools/scripttwo.py"})
        self.assertTrue(hits, "sibling script import did not resolve")

    def test_unresolved_imports_labeled_never_guessed(self):
        graph = gen(self.repo, os.path.join(self.base, "out-unres"))
        hits = self.edges(graph, **{"from": "services/api/app/pkg/rel.py",
                                    "specifier": "app.nonexistent"})
        self.assertTrue(hits)
        for e in hits:
            self.assertEqual(e["confidence"], "unresolved")
            self.assertEqual(e["to"], "unresolved:app.nonexistent")
        hits = self.edges(graph, **{"from": "apps/web/src/app/page.tsx",
                                    "specifier": "./missing"})
        self.assertTrue(hits)
        for e in hits:
            self.assertEqual(e["confidence"], "unresolved")

    def test_external_imports_labeled_external(self):
        graph = gen(self.repo, os.path.join(self.base, "out-ext"))
        py = self.edges(graph, **{"from": "services/api/app/core.py",
                                  "specifier": "fastapi"})
        self.assertTrue(py)
        self.assertEqual(py[0]["resolution"], "external")
        self.assertEqual(py[0]["to"], "external:fastapi")
        ts = self.edges(graph, **{"from": "apps/web/src/app/page.tsx",
                                  "specifier": "react"})
        self.assertTrue(ts)
        self.assertEqual(ts[0]["resolution"], "external")
        node_ids = {n["id"] for n in graph["nodes"]}
        self.assertIn("external:react", node_ids)
        self.assertIn("external:fastapi", node_ids)

    def test_ts_alias_resolves_exact(self):
        graph = gen(self.repo, os.path.join(self.base, "out-alias"))
        hits = self.edges(graph, **{"from": "apps/web/src/app/page.tsx",
                                    "to": "apps/web/src/lib/x.ts"})
        self.assertTrue(hits, "'@/lib/x' alias did not resolve")
        self.assertEqual(hits[0]["confidence"], "exact")

    def test_ts_star_reexport_partial_named_reexport_exact(self):
        graph = gen(self.repo, os.path.join(self.base, "out-re"))
        star = [e for e in self.edges(graph, type="reexport",
                                      **{"from": "apps/web/src/lib/re.ts"})
                if e["confidence"] == "partial"]
        named = [e for e in self.edges(graph, type="reexport",
                                       **{"from": "apps/web/src/lib/re.ts"})
                 if e["confidence"] == "exact"]
        self.assertEqual(len(star), 1, "export * must be partial")
        self.assertEqual(len(named), 1, "export { fx } from must be exact")

    def test_ts_dynamic_import_partial(self):
        graph = gen(self.repo, os.path.join(self.base, "out-dyn"))
        hits = self.edges(graph, type="dynamic_import",
                          **{"from": "apps/web/src/lib/dyn.ts"})
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["confidence"], "partial")
        self.assertEqual(hits[0]["to"], "apps/web/src/lib/x.ts")

    def test_contract_ref_derived_and_schema_node(self):
        graph = gen(self.repo, os.path.join(self.base, "out-schema"))
        node_ids = {n["id"]: n for n in graph["nodes"]}
        sid = "packages/contracts/schemas/v1/thing_profile.schema.json"
        self.assertIn(sid, node_ids)
        self.assertEqual(node_ids[sid]["kind"], "contract_schema")
        hits = self.edges(graph, type="contract_ref",
                          **{"from": "services/api/app/uses_schema.py",
                             "to": sid})
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["confidence"], "derived")

    def test_is_test_flags(self):
        graph = gen(self.repo, os.path.join(self.base, "out-test"))
        nodes = {n["id"]: n for n in graph["nodes"]}
        self.assertTrue(nodes["services/api/tests/test_core.py"]["is_test"])
        self.assertTrue(nodes["apps/web/src/lib/widget.test.ts"]["is_test"])
        self.assertFalse(nodes["services/api/app/core.py"]["is_test"])

    def test_symbols_extracted_with_lines(self):
        graph = gen(self.repo, os.path.join(self.base, "out-sym"))
        nodes = {n["id"]: n for n in graph["nodes"]}
        widget = nodes["services/api/app/pkg/sib.py#Widget"]
        self.assertEqual(widget["kind"], "class")
        self.assertEqual(widget["line"], 4)
        method = nodes["services/api/app/pkg/sib.py#Widget.method"]
        self.assertEqual(method["kind"], "method")
        ts_fx = nodes["apps/web/src/lib/x.ts#fx"]
        self.assertEqual(ts_fx["kind"], "ts_symbol")
        self.assertEqual(ts_fx["confidence"], "exact")
        page = nodes["apps/web/src/app/page.tsx#Page"]
        self.assertEqual(page["line"], 4)

    def test_artifacts_contain_no_absolute_paths(self):
        out = os.path.join(self.base, "out-noabs")
        gen(self.repo, out)
        for name in ("graph.json", "graph.meta.json"):
            text = read_bytes(os.path.join(out, name)).decode("utf-8")
            self.assertNotIn(self.repo.replace("\\", "/"), text)
            self.assertNotIn(self.repo.replace("\\", "\\\\"), text)

    def test_refuses_to_write_inside_repo(self):
        with self.assertRaises(SystemExit):
            generate.generate_into(self.repo, os.path.join(self.repo, "sub"))

    # ---- AS-6: bounded query + freshness ------------------------------------

    def test_query_limit_and_hard_cap(self):
        # 250 exported consts so an unrestricted dump would exceed the cap
        many = "".join("export const c%d = %d;\n" % (i, i) for i in range(250))
        _write(self.repo, "apps/web/src/lib/many.ts", many)
        proc = run_query(self.repo, self.cache, "--limit", "2", "find", "c")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = [l for l in proc.stdout.strip().split("\n")
                 if not l.startswith("regenerated")]
        self.assertEqual(len(lines), 3)  # 2 results + truncation notice
        self.assertIn("...truncated (", lines[-1])
        # hard cap 200 even when a larger limit is requested
        proc = run_query(self.repo, self.cache, "--limit", "9999", "find", "c")
        lines = [l for l in proc.stdout.strip().split("\n")
                 if not l.startswith("regenerated")]
        self.assertLessEqual(len(lines), 201)
        self.assertIn("...truncated (", lines[-1])

    def test_query_output_lines_start_with_relpath(self):
        run_query(self.repo, self.cache, "find", "x")  # warm cache
        proc = run_query(self.repo, self.cache, "downstream",
                         "apps/web/src/lib/x.ts")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = [l for l in proc.stdout.strip().split("\n")
                 if l and not l.startswith(("regenerated", "...truncated"))]
        self.assertTrue(lines)
        for line in lines:
            self.assertRegex(line, r"^[\w@.\-/]+(:\d+)?[ ]",
                             "line does not start with a repo-relative path: %r"
                             % line)

    def test_stale_fingerprint_auto_regenerates(self):
        proc = run_query(self.repo, self.cache, "find", "helper")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("regenerated (stale fingerprint)", proc.stdout)
        # fresh cache: no regeneration message
        proc = run_query(self.repo, self.cache, "find", "helper")
        self.assertNotIn("regenerated", proc.stdout)
        # edit a source file -> stale -> regenerates and still answers
        _write(self.repo, "services/api/app/util.py",
               "def helper():\n    return 99\n")
        proc = run_query(self.repo, self.cache, "find", "helper")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("regenerated (stale fingerprint)", proc.stdout)

    def test_stale_with_no_regen_exits_3(self):
        run_query(self.repo, self.cache, "find", "helper")  # warm
        _write(self.repo, "services/api/app/util.py",
               "def helper():\n    return 100\n")
        proc = run_query(self.repo, self.cache, "--no-regen", "find", "helper")
        self.assertEqual(proc.returncode, 3)
        self.assertIn("STALE", proc.stdout)

    def test_query_upstream_downstream_contracts_path_impact(self):
        run_query(self.repo, self.cache, "find", "x")  # warm cache
        proc = run_query(self.repo, self.cache, "upstream",
                         "services/api/app/core.py")
        self.assertIn("services/api/app/util.py", proc.stdout)
        proc = run_query(self.repo, self.cache, "contracts", "thing_profile")
        self.assertIn("services/api/app/uses_schema.py", proc.stdout)
        proc = run_query(self.repo, self.cache, "path",
                         "apps/web/src/app/page.tsx", "apps/web/src/lib/x.ts")
        self.assertIn("apps/web/src/lib/x.ts", proc.stdout)
        proc = run_query(self.repo, self.cache, "path",
                         "apps/web/src/lib/x.ts", "services/api/app/core.py")
        self.assertIn("no reliable path", proc.stdout)
        proc = run_query(self.repo, self.cache, "impact",
                         "apps/web/src/lib/x.ts", "--depth", "2")
        self.assertIn("apps/web/src/app/page.tsx", proc.stdout)
        self.assertIn("depth=", proc.stdout)

    # ---- AS-7: stdlib-only imports ------------------------------------------

    def test_generator_query_tests_import_stdlib_only(self):
        local_ok = {"generate", "query"}
        for path in (GENERATE_PY, QUERY_PY, os.path.abspath(__file__)):
            with open(path, "rb") as fh:
                tree = ast.parse(fh.read().decode("utf-8"))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    names = [node.module or ""]
                for name in names:
                    top = name.split(".")[0]
                    self.assertTrue(
                        top in sys.stdlib_module_names or top in local_ok,
                        "non-stdlib import %r in %s" % (name, path),
                    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
