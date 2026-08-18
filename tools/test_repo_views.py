#!/usr/bin/env python3
"""M0-T068 Unit E tests: bounded views, coverage records, truncation, determinism.

Runnable as ``python tools/test_repo_views.py`` (exit 0 = pass) or under
pytest. Fixtures are hermetic temp git repos with a fixture subsystem map and
temp index-cache/memory-store bases.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from tools import repo_views as rv  # noqa: E402
from tools import repo_views_query as rq  # noqa: E402

QUERY_CLI = os.path.join(_HERE, "repo_views_query.py")

_GIT_ENV = {"GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t.t",
            "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@t.t",
            "GIT_CONFIG_NOSYSTEM": "1"}


def _write(root: str, rel: str, content: str) -> str:
    p = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(content.encode("utf-8"))
    return p


def _git(root: str, *args: str) -> None:
    env = dict(os.environ)
    env.update(_GIT_ENV)
    subprocess.run(["git", *args], cwd=root, env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_fixture(root: str) -> str:
    """Git fixture: 3 indexed files with import edges + control-plane indexes.
    Returns the fixture subsystem-map path."""
    _write(root, "services/api/thing.py", "def thing():\n    return 1\n")
    _write(root, "services/api/user.py",
           "from services.api.thing import thing\n\ndef use():\n    return thing()\n")
    _write(root, "services/api/user2.py",
           "from services.api.thing import thing\n\ndef use2():\n    return thing()\n")
    _write(root, "docs/notes.md", "# fixture notes\nline two\nline three\n")
    _write(root, ".claude/agents/qa-engineer.md", "# qa\n")
    _write(root, "project-control/master_plan.json", json.dumps(
        {"milestones": [{"id": "M0"}]}))
    _write(root, "project-control/tasks/M0-T001.json", json.dumps(
        {"task_id": "M0-T001", "title": "Fixture task", "status": "claimed",
         "milestone_id": "M0", "dependencies": [],
         "allowed_paths": ["services/api/thing.py"],
         "directive_refs": [{"directive_id": "D-900", "requirement_ids": "ALL"}]}))
    _write(root, "project-control/directives/index.json", json.dumps(
        {"directives": [{"directive_id": "D-900"}]}))
    _write(root, "project-control/directives/D-900-test/requirements.json",
           json.dumps({"requirements": [{"id": "D-900-R001", "text": "t"}]}))
    map_path = _write(root, "fixture_map.json", json.dumps({
        "map_schema_version": "1.0.0", "map_version": "0.0.1",
        "rules": [{"subsystem_id": "services/api", "prefix": "services/api"},
                  {"subsystem_id": "docs", "prefix": "docs"}]}))
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "baseline")
    return map_path


class Case(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._cache = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        self.cache = self._cache.name
        self.map_path = build_fixture(self.root)
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(self._cache.cleanup)

    def build(self):
        return rv.build_index(self.root, self.cache, self.map_path)


class AS1CoverageModes(Case):
    def test_census_accounts_for_every_eligible_file(self) -> None:
        res, gi, lm = self.build()
        v = rv.census_view(res, gi, lm)
        self.assertEqual(v["coverage_mode"], "census")
        c = v["content"]
        self.assertTrue(c["reconciles"])
        self.assertEqual(c["eligible"], c["indexed"])
        self.assertEqual(c["eligible"], 3)  # the three .py files
        self.assertIn("services/api/thing.py", c["indexed_files"])
        self.assertIn("indexed_files_truncation", c)

    def test_changed_reports_and_refuses_unsupported_base(self) -> None:
        res, _gi, lm = self.build()
        v = rv.changed_view(res, lm)
        self.assertEqual(v["coverage_mode"], "changed")
        self.assertEqual(v["content"]["base"], "prior_cache_generation")
        self.assertIn("change_set", v["content"])
        same = rv.changed_view(res, lm, since_fingerprint=res.snapshot_fingerprint)
        self.assertTrue(same["content"]["no_change_by_identity"])
        with self.assertRaises(rv.ViewsError) as cm:
            rv.changed_view(res, lm, since_fingerprint="0" * 64)
        self.assertEqual(cm.exception.code, "unsupported_base_fingerprint")

    def test_neighborhood_bounded_around_seed(self) -> None:
        res, gi, lm = self.build()
        v = rv.neighborhood_view(res, gi, lm, "services/api/user.py")
        self.assertEqual(v["coverage_mode"], "neighborhood")
        c = v["content"]
        self.assertTrue(c["resolved"])
        self.assertEqual(c["out_edges"][0]["to"], "services/api/thing.py")
        self.assertEqual(c["out_edges"][0]["type"], "import")

    def test_deep_exact_excerpt_with_provenance(self) -> None:
        res, _gi, lm = self.build()
        v = rv.deep_view(res, lm, self.root, "docs/notes.md", 2, 3)
        self.assertEqual(v["coverage_mode"], "deep")
        c = v["content"]
        self.assertEqual(c["excerpt"], ["line two", "line three"])
        self.assertEqual((c["start_line"], c["end_line"]), (2, 3))
        with open(os.path.join(self.root, "docs", "notes.md"), "rb") as fh:
            raw = fh.read()
        self.assertEqual(c["content_digest"],
                         hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest())
        self.assertFalse(c["truncation"]["truncated"])


class AS2CoverageRecord(Case):
    REQUIRED = ("repo_identity", "snapshot_fingerprint", "head_sha", "branch",
                "head_detached", "dirty_state_digest", "source_manifest_digest",
                "export_digest", "census", "versions", "generator_identity",
                "graph_nodes_after", "graph_edges_after", "views_version",
                "query_params", "limits")

    def test_every_view_carries_full_record(self) -> None:
        res, gi, lm = self.build()
        views = [rv.census_view(res, gi, lm),
                 rv.changed_view(res, lm),
                 rv.neighborhood_view(res, gi, lm, "services/api/thing.py"),
                 rv.card_view(res, gi, lm, self.root, "services/api/thing.py"),
                 rv.deep_view(res, lm, self.root, "docs/notes.md", 1, 1)]
        for v in views:
            cov = v["coverage"]
            for key in self.REQUIRED:
                self.assertIn(key, cov, f"{v['view']} missing {key}")
            self.assertIn("ontology", cov["versions"])
            self.assertIn("map_digest", cov["versions"]["ontology"])
            census = cov["census"]
            for key in ("eligible", "indexed", "excluded", "failed", "stale",
                        "reconciles"):
                self.assertIn(key, census)
            self.assertEqual(v["runtime"]["label"], "cache_state_non_identity")
            self.assertIn("cache_result", v["runtime"])

    def test_query_params_and_limits_exact(self) -> None:
        res, gi, lm = self.build()
        v = rv.neighborhood_view(res, gi, lm, "services/api/thing.py",
                                 edge_limit=7)
        self.assertEqual(v["coverage"]["query_params"],
                         {"view": "neighborhood", "seed": "services/api/thing.py"})
        self.assertEqual(v["coverage"]["limits"], {"edge_limit": 7})


class AS3Truncation(Case):
    def test_neighborhood_truncates_with_marker(self) -> None:
        res, gi, lm = self.build()
        v = rv.neighborhood_view(res, gi, lm, "services/api/thing.py",
                                 edge_limit=1)
        c = v["content"]
        self.assertEqual(len(c["in_edges"]), 1)  # user.py + user2.py import it
        self.assertTrue(c["in_truncation"]["truncated"])
        self.assertEqual(c["in_truncation"]["omitted"], 1)

    def test_census_file_list_truncates_with_marker(self) -> None:
        res, gi, lm = self.build()
        v = rv.census_view(res, gi, lm, file_limit=1)
        c = v["content"]
        self.assertEqual(len(c["indexed_files"]), 1)
        self.assertTrue(c["indexed_files_truncation"]["truncated"])
        self.assertEqual(c["indexed_files_truncation"]["omitted"], 2)

    def test_deep_truncates_with_marker(self) -> None:
        res, _gi, lm = self.build()
        v = rv.deep_view(res, lm, self.root, "docs/notes.md", 1, 3, max_lines=1)
        c = v["content"]
        self.assertEqual(len(c["excerpt"]), 1)
        self.assertTrue(c["truncation"]["truncated"])
        self.assertEqual(c["truncation"]["omitted"], 2)


class AS4Honesty(Case):
    def test_unknown_seed_no_answer(self) -> None:
        res, gi, lm = self.build()
        v = rv.card_view(res, gi, lm, self.root, "no/such/file.py")
        self.assertFalse(v["content"]["resolved"])
        self.assertEqual(v["content"]["reason"], "seed_not_in_graph")

    def test_card_kind_and_subsystem_from_resolver(self) -> None:
        res, gi, lm = self.build()
        v = rv.card_view(res, gi, lm, self.root, "services/api/thing.py")
        c = v["content"]
        self.assertEqual(c["kind"], "py_module")  # ACTUAL graph kind (R018)
        self.assertEqual(c["subsystem"]["subsystem"], "services/api")
        self.assertTrue(c["exists_in_tree"])

    def test_unknown_requirement_no_answer(self) -> None:
        out = rq.about_requirement(self.root, "D-900-R999",
                                   cache_base=self.cache, map_path=self.map_path)
        self.assertFalse(out["answer"]["resolved"])
        self.assertEqual(out["answer"]["reason"], "unknown_requirement_id")

    def test_requirement_resolves_with_citing_tasks(self) -> None:
        out = rq.about_requirement(self.root, "D-900-R001",
                                   cache_base=self.cache, map_path=self.map_path)
        self.assertEqual(out["answer"]["directive_id"], "D-900")
        self.assertEqual(out["answer"]["citing_tasks"], ["M0-T001"])

    def test_memory_absent_is_labeled_not_fabricated(self) -> None:
        with tempfile.TemporaryDirectory() as mem_base:
            out = rq.about_task(self.root, "M0-T001", cache_base=self.cache,
                                memory_base=mem_base, map_path=self.map_path)
        mem = out["answer"]["memory"]
        self.assertTrue(mem["advisory"])
        self.assertEqual(mem["status"], "store_empty")
        self.assertEqual(mem["digests"], [])

    def test_memory_digest_surfaces_after_promotion(self) -> None:
        from tools import memory_digest as md
        from tools import memory_graph as mg
        from tools.subsystem_entities import AuthoritativeIndexes
        from tools.subsystem_resolver import load_map, version_stamp
        stamp = version_stamp(load_map(self.root, self.map_path))
        idx = AuthoritativeIndexes.load(self.root).digests()
        doc = {"schema_version": md.DIGEST_SCHEMA_VERSION, "digest_id": "",
               "task_id": "M0-T001", "requirement_ids": ["D-900-R001"],
               "files": [{"path": "services/api/thing.py", "content_digest": None}],
               "agent": "qa-engineer", "outcome": "PASS", "repo_sha": "a" * 40,
               "source_manifest_fingerprint": None, "branch": "b",
               "task_index_digest": idx["task_index_digest"],
               "directive_index_digest": idx["directive_index_digest"],
               "resolver_version": stamp["resolver_version"],
               "map_version": stamp["map_version"],
               "map_digest": stamp["map_digest"],
               "evidence_refs": [], "unresolved_links": [], "advisory_tags": []}
        doc["digest_id"] = md.compute_digest_id(doc)
        with tempfile.TemporaryDirectory() as mem_base:
            mg.promote_digest(doc, self.root, base=mem_base,
                              map_path=self.map_path)
            out = rq.about_file(self.root, "services/api/thing.py",
                                cache_base=self.cache, memory_base=mem_base,
                                map_path=self.map_path)
        mem = out["answer"]["memory"]
        self.assertEqual(mem["status"], "ok")
        self.assertEqual(mem["digests"][0]["task_id"], "M0-T001")
        self.assertEqual(mem["digests"][0]["outcome"], "PASS")

    def test_who_imports(self) -> None:
        out = rq.who_imports(self.root, "services/api/thing.py",
                             cache_base=self.cache, map_path=self.map_path)
        importers = {e["from"] for e in out["answer"]["importers"]}
        self.assertEqual(importers,
                         {"services/api/user.py", "services/api/user2.py"})


class AS5FailClosed(Case):
    def test_index_unavailable_on_non_git_dir(self) -> None:
        with tempfile.TemporaryDirectory() as plain:
            with self.assertRaises(rv.ViewsError) as cm:
                rv.build_index(plain, self.cache, self.map_path)
            self.assertEqual(cm.exception.code, "index_unavailable")

    def test_deep_non_canonical_and_missing_paths(self) -> None:
        res, _gi, lm = self.build()
        with self.assertRaises(rv.ViewsError) as cm:
            rv.deep_view(res, lm, self.root, "docs/../secret.md", 1, 2)
        self.assertEqual(cm.exception.code, "non_canonical_path")
        with self.assertRaises(rv.ViewsError) as cm2:
            rv.deep_view(res, lm, self.root, "docs/absent.md", 1, 2)
        self.assertEqual(cm2.exception.code, "path_not_in_tree")

    def test_unknown_task_fails_closed(self) -> None:
        with self.assertRaises(rv.ViewsError) as cm:
            rq.about_task(self.root, "M0-T999", cache_base=self.cache,
                          map_path=self.map_path)
        self.assertEqual(cm.exception.code, "task_packet_unreadable")

    def test_cli_exit_2_with_error_doc(self) -> None:
        p = subprocess.run(
            [sys.executable, QUERY_CLI, "--repo", self.root,
             "--cache-base", self.cache, "--map", self.map_path,
             "deep", "docs/../secret.md", "1", "2"],
            capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(json.loads(p.stdout)["error"]["code"],
                         "non_canonical_path")


class AS6Determinism(Case):
    def test_cold_vs_warm_deterministic_sections_identical(self) -> None:
        docs = []
        runtimes = []
        for _ in range(2):  # run 1 cold (full build), run 2 warm (cache reuse)
            res, gi, lm = self.build()
            views = [rv.census_view(res, gi, lm),
                     rv.card_view(res, gi, lm, self.root, "services/api/thing.py"),
                     rv.neighborhood_view(res, gi, lm, "services/api/user.py"),
                     rv.deep_view(res, lm, self.root, "docs/notes.md", 1, 2)]
            docs.append(b"".join(rq._det_sections(v) for v in views))
            runtimes.append(views[0]["runtime"]["cache_result"])
        self.assertEqual(docs[0], docs[1])
        self.assertEqual(runtimes, ["miss", "hit"])  # cache state DID differ

    def test_changed_view_is_cache_relative_by_design(self) -> None:
        self.build()  # cold: establishes the prior generation
        res2, _gi2, lm2 = self.build()
        warm = rv.changed_view(res2, lm2)["content"]["change_set"]
        self.assertEqual(warm["content_modified"], [])  # warm no-change: empty
        _write(self.root, "services/api/thing.py",
               "def thing():\n    return 2\n")
        res3, _gi3, lm3 = self.build()
        edited = rv.changed_view(res3, lm3)["content"]["change_set"]
        self.assertEqual(edited["content_modified"], ["services/api/thing.py"])

    def test_cli_check_passes(self) -> None:
        p = subprocess.run(
            [sys.executable, QUERY_CLI, "--repo", self.root,
             "--cache-base", self.cache, "--map", self.map_path, "check"],
            capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["check"], "PASS")


if __name__ == "__main__":
    unittest.main()
