#!/usr/bin/env python3
"""M0-T066 Unit C tests: versioned deterministic subsystem/ontology resolver.

Runnable as ``python tools/test_subsystem_resolver.py`` (exit 0 = pass) or under
pytest. Covers the packet's AS-1..AS-6 plus edge cases. Entity/graph fixtures
are hermetic temp trees; the real repository map is exercised read-only.
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

from tools import subsystem_entities as ents  # noqa: E402
from tools import subsystem_resolver as res  # noqa: E402
from tools.context_pack_io import canon_json_bytes  # noqa: E402

RESOLVER_PY = os.path.join(_HERE, "subsystem_resolver.py")


def _write(root: str, rel: str, content: str) -> str:
    p = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(content.encode("utf-8"))
    return p


def _write_map(root: str, rules: list[dict], schema: str = "1.0.0",
               name: str = "fixture_map.json") -> str:
    doc = {"map_schema_version": schema, "map_version": "0.0.1", "rules": rules}
    return _write(root, name, json.dumps(doc, indent=1))


def build_entity_fixture(root: str) -> str:
    """Temp tree with authoritative indexes + mapped source dirs (no git)."""
    os.makedirs(os.path.join(root, "services", "api"), exist_ok=True)
    os.makedirs(os.path.join(root, "tools"), exist_ok=True)
    _write(root, "services/api/x.py", "def x():\n    return 1\n")
    _write(root, "README.md", "# fixture\n")
    _write(root, "project-control/master_plan.json", json.dumps(
        {"milestones": [{"id": "M0"}, {"id": "M1"}]}))
    _write(root, "project-control/tasks/M0-T001.json", json.dumps(
        {"task_id": "M0-T001", "milestone_id": "M0"}))
    _write(root, "project-control/tasks/M0-T002.json", json.dumps(
        {"task_id": "M0-T002", "milestone_id": "M9"}))  # milestone not in plan
    _write(root, "project-control/directives/index.json", json.dumps(
        {"directives": [{"directive_id": "D-900"}]}))
    _write(root, "project-control/directives/D-900-test-directive/requirements.json",
           json.dumps({"requirements": [{"id": "D-900-R001", "text": "t"}]}))
    return _write_map(root, [
        {"subsystem_id": "services/api", "prefix": "services/api"},
        {"subsystem_id": "tools", "prefix": "tools"},
    ])


class AS1ClosedVocabulary(unittest.TestCase):
    def test_real_map_every_id_is_existing_prefix(self) -> None:
        loaded = res.load_map(_ROOT)
        for rule in loaded["map"]["rules"]:
            self.assertEqual(rule["subsystem_id"], rule["prefix"])
            self.assertTrue(os.path.isdir(os.path.join(_ROOT, rule["prefix"])),
                            rule["prefix"])

    def test_free_form_name_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "tools"))
            mp = _write_map(root, [{"subsystem_id": "core-engine", "prefix": "tools"}])
            with self.assertRaises(res.SubsystemMapError) as cm:
                res.load_map(root, mp)
            self.assertEqual(cm.exception.code, "free_form_subsystem_id")

    def test_nonexistent_prefix_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            mp = _write_map(root, [{"subsystem_id": "no/such/dir", "prefix": "no/such/dir"}])
            with self.assertRaises(res.SubsystemMapError) as cm:
                res.load_map(root, mp)
            self.assertEqual(cm.exception.code, "prefix_not_in_tree")

    def test_duplicate_prefix_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "tools"))
            mp = _write_map(root, [
                {"subsystem_id": "tools", "prefix": "tools"},
                {"subsystem_id": "tools", "prefix": "tools"}])
            with self.assertRaises(res.SubsystemMapError) as cm:
                res.load_map(root, mp)
            self.assertEqual(cm.exception.code, "duplicate_rule_prefix")


class AS2VersionedDeterminism(unittest.TestCase):
    def test_two_runs_byte_identical_and_stamped(self) -> None:
        sample = ["tools/code_graph/query.py", "services/api/app/main.py",
                  "README.md", "tools\\subsystem_resolver.py"]
        runs = []
        for _ in range(2):
            loaded = res.load_map(_ROOT)
            runs.append(canon_json_bytes({
                "version": res.version_stamp(loaded),
                "vocabulary": res.vocabulary(loaded),
                "results": [res.resolve_path(p, loaded) for p in sample]}))
        self.assertEqual(runs[0], runs[1])
        stamp = res.version_stamp(res.load_map(_ROOT))
        with open(res.DEFAULT_MAP_PATH, "rb") as fh:
            # CRLF-normalized like the A1 fingerprint: identical digest on
            # Windows (CRLF checkout) and CI (LF checkout).
            expect = hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()
        self.assertEqual(stamp["map_digest"], expect)
        self.assertEqual(stamp["resolver_version"], res.RESOLVER_VERSION)
        self.assertTrue(stamp["map_version"])

    def test_cli_check_passes(self) -> None:
        p = subprocess.run([sys.executable, RESOLVER_PY, "--repo", _ROOT, "check"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["check"], "PASS")


class AS3DerivedParents(unittest.TestCase):
    def test_parents_derived_from_authoritative_facts(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            mp = build_entity_fixture(root)
            loaded = res.load_map(root, mp)
            out = ents.resolve_proposals(
                ents.propose(["services/api/x.py", "M0-T001", "D-900-R001", "D-900", "M0"]),
                root, loaded)
            by_val = {link["value"]: link for link in out["links"]}
            self.assertEqual(by_val["services/api/x.py"]["parents"]["subsystem"],
                             "services/api")
            self.assertEqual(by_val["M0-T001"]["parents"]["milestone"], "M0")
            self.assertEqual(by_val["D-900-R001"]["parents"]["directive"], "D-900")
            self.assertEqual(out["unresolved_links"], [])
            self.assertIn("task_index_digest", out["index_digests"])
            self.assertIn("directive_index_digest", out["index_digests"])

    def test_task_with_unplanned_milestone_is_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            mp = build_entity_fixture(root)
            loaded = res.load_map(root, mp)
            out = ents.resolve_proposals(ents.propose(["M0-T002"]), root, loaded)
            self.assertEqual(out["links"], [])
            self.assertEqual(out["unresolved_links"][0]["reason"],
                             "milestone_not_in_master_plan")


class AS4TwoPass(unittest.TestCase):
    def test_invalid_proposals_land_in_unresolved_with_reasons(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            mp = build_entity_fixture(root)
            loaded = res.load_map(root, mp)
            proposals = ents.propose([
                "M0-T001", "M9-T999", "services/api/x.py", "no/such/file.py",
                "D-900-R001", "D-900-R999", "D-777", "M7",
                {"kind": "symbol", "value": "services/api/x.py"},
                "README.md"])
            out = ents.resolve_proposals(proposals, root, loaded)
            self.assertEqual(len(out["links"]) + len(out["unresolved_links"]),
                             len(proposals))  # nothing silently dropped
            reasons = {u["value"]: u["reason"] for u in out["unresolved_links"]}
            self.assertEqual(reasons["M9-T999"], "unknown_task_id")
            self.assertEqual(reasons["no/such/file.py"], "path_not_in_source_tree")
            self.assertEqual(reasons["D-900-R999"], "unknown_requirement_id")
            self.assertEqual(reasons["D-777"], "unknown_directive_id")
            self.assertEqual(reasons["M7"], "unknown_milestone_id")
            self.assertEqual(reasons["README.md"], "no_matching_subsystem_rule")
            # symbol proposals need the graph; without it: machine-readable reason
            sym = [u for u in out["unresolved_links"] if u["kind"] == "symbol"]
            self.assertEqual(sym[0]["reason"], "graph_not_provided")

    def test_propose_normalizes_and_dedupes_deterministically(self) -> None:
        got = ents.propose(["./tools/x.py", "tools\\x.py", "M0-T001", "M0-T001", "", 7])
        self.assertEqual(got, [
            {"kind": "path", "value": "tools/x.py", "evidence": None},
            {"kind": "task", "value": "M0-T001", "evidence": None}])

    def test_evidence_is_preserved_on_links(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            mp = build_entity_fixture(root)
            loaded = res.load_map(root, mp)
            out = ents.resolve_proposals(ents.propose(
                [{"kind": "task", "value": "M0-T001", "evidence": "report.md#L3"}]),
                root, loaded)
            self.assertEqual(out["links"][0]["evidence"], "report.md#L3")


class AS5HonestGraphKinds(unittest.TestCase):
    def test_reports_actual_kinds_and_no_subsystem_node(self) -> None:
        with tempfile.TemporaryDirectory() as root, \
             tempfile.TemporaryDirectory() as cache:
            env = dict(os.environ)
            env.update({"GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t.t",
                        "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@t.t",
                        "GIT_CONFIG_NOSYSTEM": "1"})
            _write(root, "services/api/app/thing.py", "def thing():\n    return 1\n")
            _write(root, "services/api/app/user.py",
                   "from services.api.app.thing import thing\n\n"
                   "def use():\n    return thing()\n")
            for args in (["init", "-q"], ["add", "-A"],
                         ["commit", "-q", "-m", "baseline"]):
                subprocess.run(["git", *args], cwd=root, env=env, check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            report = res.report_graph_kinds(root, cache_base=cache)
            self.assertIn("py_module", report["node_kinds"])
            self.assertIn("function", report["node_kinds"])
            self.assertIn("import", report["edge_types"])
            self.assertNotIn("subsystem", report["node_kinds"])
            self.assertFalse(report["subsystem_node_kind_in_graph"])
            self.assertTrue(report["export_digest"])


class AS6FailClosed(unittest.TestCase):
    def test_malformed_map_json(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            mp = _write(root, "bad.json", "{not json")
            with self.assertRaises(res.SubsystemMapError) as cm:
                res.load_map(root, mp)
            self.assertEqual(cm.exception.code, "map_malformed_json")

    def test_unknown_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "tools"))
            mp = _write_map(root, [{"subsystem_id": "tools", "prefix": "tools"}],
                            schema="9.9.9")
            with self.assertRaises(res.SubsystemMapError) as cm:
                res.load_map(root, mp)
            self.assertEqual(cm.exception.code, "unknown_map_schema_version")

    def test_missing_map_file(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(res.SubsystemMapError) as cm:
                res.load_map(root, os.path.join(root, "absent.json"))
            self.assertEqual(cm.exception.code, "map_unreadable")

    def test_cli_exits_nonzero_with_error_doc_on_bad_map(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            mp = _write(root, "bad.json", "[]")
            p = subprocess.run(
                [sys.executable, RESOLVER_PY, "--repo", root, "--map", mp, "vocabulary"],
                capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertEqual(json.loads(p.stdout)["error"]["code"], "map_not_object")

    def test_unreadable_master_plan_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            mp = build_entity_fixture(root)
            os.remove(os.path.join(root, "project-control", "master_plan.json"))
            loaded = res.load_map(root, mp)
            with self.assertRaises(ents.EntityIndexError) as cm:
                ents.resolve_proposals(ents.propose(["M0-T001"]), root, loaded)
            self.assertEqual(cm.exception.code, "master_plan_unreadable")

    def test_unreadable_requirements_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            mp = build_entity_fixture(root)
            os.remove(os.path.join(root, "project-control", "directives",
                                   "D-900-test-directive", "requirements.json"))
            loaded = res.load_map(root, mp)
            with self.assertRaises(ents.EntityIndexError) as cm:
                ents.resolve_proposals(ents.propose(["D-900-R001"]), root, loaded)
            self.assertEqual(cm.exception.code, "requirements_unreadable")


class EdgeCases(unittest.TestCase):
    def test_longest_prefix_wins_on_whole_segments(self) -> None:
        loaded = res.load_map(_ROOT)
        self.assertEqual(res.resolve_path("tools/code_graph/query.py", loaded)["subsystem"],
                         "tools/code_graph")
        self.assertEqual(res.resolve_path("tools/context_pack.py", loaded)["subsystem"],
                         "tools")
        # segment boundary: 'toolsandmore' must NOT match the 'tools' prefix
        r = res.resolve_path("toolsandmore/file.py", loaded)
        self.assertFalse(r["resolved"])
        self.assertEqual(r["reason"], "no_matching_subsystem_rule")

    def test_empty_path(self) -> None:
        loaded = res.load_map(_ROOT)
        r = res.resolve_path("  ", loaded)  # whitespace-only stays unresolved
        self.assertFalse(r["resolved"])

    def test_symbol_resolves_against_provided_graph(self) -> None:
        class FakeGraph:
            nodes = {"services/api/x.py": {"kind": "py_module"},
                     "services/api/x.py::x": {"kind": "function"}}
        with tempfile.TemporaryDirectory() as root:
            mp = build_entity_fixture(root)
            loaded = res.load_map(root, mp)
            out = ents.resolve_proposals(ents.propose([
                {"kind": "symbol", "value": "services/api/x.py::x"},
                {"kind": "symbol", "value": "services/api/x.py::missing"},
                "services/api/x.py"]),
                root, loaded, graph_index=FakeGraph())
            links = {link["value"]: link for link in out["links"]}
            self.assertEqual(links["services/api/x.py::x"]["parents"]["graph_node"],
                             "services/api/x.py::x")
            self.assertTrue(links["services/api/x.py"]["graph_indexed"])
            self.assertEqual(out["unresolved_links"][0]["reason"], "symbol_not_in_graph")


if __name__ == "__main__":
    unittest.main()
