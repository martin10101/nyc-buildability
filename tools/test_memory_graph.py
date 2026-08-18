#!/usr/bin/env python3
"""M0-T067 Unit D tests: closed-schema digests, grounding, quarantine, promotion.

Runnable as ``python tools/test_memory_graph.py`` (exit 0 = pass) or under
pytest. Every fixture is a hermetic temp tree: fixture project-control indexes,
a fixture subsystem map, and a temp external store base. Crash points are
injected by patching the store's atomic-promotion primitive.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from tools import memory_digest as md  # noqa: E402
from tools import memory_graph as mg  # noqa: E402
from tools import repo_index_cache as ric  # noqa: E402
from tools import subsystem_resolver as res  # noqa: E402


def _write(root: str, rel: str, content: str) -> str:
    p = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(content.encode("utf-8"))
    return p


def build_fixture(root: str) -> str:
    """Fixture repo tree: mapped dirs, agents roster, control-plane indexes.
    Returns the fixture map path."""
    _write(root, "services/api/x.py", "def x():\n    return 1\n")
    _write(root, "services/api/other.py", "def o():\n    return 2\n")
    _write(root, "docs/OUTSIDE.md", "# outside task scope\n")
    _write(root, ".claude/agents/qa-engineer.md", "# qa\n")
    _write(root, ".claude/agents/code-reviewer.md", "# cr\n")
    _write(root, "project-control/master_plan.json", json.dumps(
        {"milestones": [{"id": "M0"}]}))
    _write(root, "project-control/tasks/M0-T001.json", json.dumps(
        {"task_id": "M0-T001", "milestone_id": "M0",
         "allowed_paths": ["services/api/x.py"],
         "directive_refs": [{"directive_id": "D-900", "requirement_ids": "ALL"}]}))
    _write(root, "project-control/directives/index.json", json.dumps(
        {"directives": [{"directive_id": "D-900"}, {"directive_id": "D-901"}]}))
    _write(root, "project-control/directives/D-900-test/requirements.json",
           json.dumps({"requirements": [{"id": "D-900-R001", "text": "t"}]}))
    _write(root, "project-control/directives/D-901-other/requirements.json",
           json.dumps({"requirements": [{"id": "D-901-R001", "text": "t"}]}))
    return _write(root, "fixture_map.json", json.dumps({
        "map_schema_version": "1.0.0", "map_version": "0.0.1",
        "rules": [{"subsystem_id": "services/api", "prefix": "services/api"},
                  {"subsystem_id": "docs", "prefix": "docs"}]}))


def make_digest(root: str, map_path: str, **overrides) -> dict:
    """A fully valid digest for the fixture; overrides applied then id restamped
    (pass restamp_id=False to keep a deliberately wrong id)."""
    from tools.subsystem_entities import AuthoritativeIndexes
    restamp = overrides.pop("restamp_id", True)
    stamp = res.version_stamp(res.load_map(root, map_path))
    idx = AuthoritativeIndexes.load(root).digests()
    doc = {
        "schema_version": md.DIGEST_SCHEMA_VERSION,
        "digest_id": "",
        "task_id": "M0-T001",
        "requirement_ids": ["D-900-R001"],
        "files": [{"path": "services/api/x.py", "content_digest": None}],
        "agent": "qa-engineer",
        "outcome": "PASS",
        "repo_sha": "a" * 40,
        "source_manifest_fingerprint": None,
        "branch": "task/M0-T001-fixture",
        "task_index_digest": idx["task_index_digest"],
        "directive_index_digest": idx["directive_index_digest"],
        "resolver_version": stamp["resolver_version"],
        "map_version": stamp["map_version"],
        "map_digest": stamp["map_digest"],
        "evidence_refs": ["project-control/reports/M0-T001-report.md"],
        "unresolved_links": [],
        "advisory_tags": ["fixture-tag"],
    }
    doc.update(overrides)
    if restamp:
        doc["digest_id"] = md.compute_digest_id(doc)
    return doc


class Case(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._store = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        self.base = self._store.name
        self.map_path = build_fixture(self.root)
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(self._store.cleanup)

    def promote(self, doc, **kw):
        kw.setdefault("base", self.base)
        kw.setdefault("map_path", self.map_path)
        return mg.promote_digest(doc, self.root, **kw)


class AS1ClosedSchema(Case):
    def test_valid_digest_validates(self) -> None:
        doc = make_digest(self.root, self.map_path)
        self.assertIs(md.validate_digest(doc, self.root), doc)

    def test_unknown_field_refuses(self) -> None:
        doc = make_digest(self.root, self.map_path, extra_field="x")
        with self.assertRaises(md.DigestSchemaError) as cm:
            md.validate_digest(doc, self.root)
        self.assertEqual(cm.exception.code, "closed_schema_violation")

    def test_missing_required_field_refuses(self) -> None:
        doc = make_digest(self.root, self.map_path)
        del doc["branch"]
        with self.assertRaises(md.DigestSchemaError) as cm:
            md.validate_digest(doc, self.root)
        self.assertEqual(cm.exception.code, "missing_required_field")

    def test_agent_outside_allowlist_refuses(self) -> None:
        doc = make_digest(self.root, self.map_path, agent="not-an-agent")
        with self.assertRaises(md.DigestSchemaError) as cm:
            md.validate_digest(doc, self.root)
        self.assertEqual(cm.exception.code, "agent_not_in_allowlist")

    def test_outcome_outside_enum_refuses(self) -> None:
        doc = make_digest(self.root, self.map_path, outcome="MAYBE")
        with self.assertRaises(md.DigestSchemaError) as cm:
            md.validate_digest(doc, self.root)
        self.assertEqual(cm.exception.code, "outcome_not_in_enum")

    def test_digest_id_mismatch_refuses(self) -> None:
        doc = make_digest(self.root, self.map_path)
        doc["digest_id"] = "0" * 64
        with self.assertRaises(md.DigestSchemaError) as cm:
            md.validate_digest(doc, self.root)
        self.assertEqual(cm.exception.code, "digest_id_mismatch")

    def test_allowlist_derived_from_repo_facts(self) -> None:
        allow = md.agent_allowlist(self.root)
        self.assertEqual(allow, ["code-reviewer", "orchestrator", "qa-engineer"])

    def test_oversize_note_refuses(self) -> None:
        doc = make_digest(self.root, self.map_path, note="x" * 2001)
        with self.assertRaises(md.DigestSchemaError) as cm:
            md.validate_digest(doc, self.root)
        self.assertEqual(cm.exception.code, "note_too_long")


class AS2DerivedParents(Case):
    def test_promotion_derives_all_parents(self) -> None:
        out = self.promote(make_digest(self.root, self.map_path))
        self.assertEqual(out["status"], "promoted")
        store = mg.memory_store(self.root, base=self.base)
        payload = store.load_current().load_payload()
        node = payload["nodes"][out["digest_id"]]
        links = {(li["kind"], li["value"]): li for li in node["structural_links"]}
        self.assertEqual(links[("task", "M0-T001")]["parents"]["milestone"], "M0")
        self.assertEqual(links[("requirement", "D-900-R001")]["parents"]["directive"],
                         "D-900")
        self.assertEqual(links[("path", "services/api/x.py")]["parents"]["subsystem"],
                         "services/api")
        self.assertEqual(node["ontology"]["resolver_version"], res.RESOLVER_VERSION)
        self.assertIn("task_index_digest", node["index_digests"])
        self.assertEqual(node["quarantined_links"], [])

    def test_same_digest_same_state_is_byte_deterministic(self) -> None:
        doc = make_digest(self.root, self.map_path)
        with tempfile.TemporaryDirectory() as b2:
            a = self.promote(doc)
            b = mg.promote_digest(doc, self.root, base=b2, map_path=self.map_path)
        self.assertEqual(a["generation_fingerprint"], b["generation_fingerprint"])


class AS3GroundingQuarantine(Case):
    def test_existing_but_ungrounded_file_and_unknown_requirement(self) -> None:
        doc = make_digest(
            self.root, self.map_path,
            files=[{"path": "services/api/x.py", "content_digest": None},
                   {"path": "docs/OUTSIDE.md", "content_digest": None}],
            requirement_ids=["D-900-R001", "D-900-R999"])
        out = self.promote(doc)
        self.assertEqual(out["status"], "promoted")
        payload = mg.memory_store(self.root, base=self.base).load_current().load_payload()
        node = payload["nodes"][out["digest_id"]]
        reasons = {(q["kind"], q["value"]): q["reason"]
                   for q in node["quarantined_links"]}
        # docs/OUTSIDE.md EXISTS in the tree but is outside task scope/diff/evidence
        self.assertEqual(reasons[("path", "docs/OUTSIDE.md")], "ungrounded_file_link")
        self.assertEqual(reasons[("requirement", "D-900-R999")],
                         "unknown_requirement_id")
        struct = {(li["kind"], li["value"]) for li in node["structural_links"]}
        self.assertNotIn(("path", "docs/OUTSIDE.md"), struct)
        self.assertNotIn(("requirement", "D-900-R999"), struct)

    def test_requirement_of_uncited_directive_is_ungrounded(self) -> None:
        doc = make_digest(self.root, self.map_path,
                          requirement_ids=["D-900-R001", "D-901-R001"])
        out = self.promote(doc)
        payload = mg.memory_store(self.root, base=self.base).load_current().load_payload()
        node = payload["nodes"][out["digest_id"]]
        reasons = {q["value"]: q["reason"] for q in node["quarantined_links"]}
        # D-901-R001 EXISTS in the registry but M0-T001 does not cite D-901
        self.assertEqual(reasons["D-901-R001"], "ungrounded_requirement_link")

    def test_stale_file_digest_quarantined(self) -> None:
        import hashlib
        wrong = hashlib.sha256(b"not the real content").hexdigest()
        doc = make_digest(self.root, self.map_path,
                          files=[{"path": "services/api/x.py",
                                  "content_digest": wrong}])
        out = self.promote(doc)
        payload = mg.memory_store(self.root, base=self.base).load_current().load_payload()
        node = payload["nodes"][out["digest_id"]]
        self.assertEqual(node["quarantined_links"][0]["reason"], "stale_file_link")

    def test_stale_ontology_quarantines_whole_digest(self) -> None:
        doc = make_digest(self.root, self.map_path, map_digest="0" * 64)
        out = self.promote(doc)
        self.assertEqual(out["status"], "quarantined")
        self.assertEqual(out["reasons"][0]["reason"], "stale_ontology_version")
        store = mg.memory_store(self.root, base=self.base)
        self.assertIsNone(store.load_current())  # never entered the graph
        qfile = store.root / "digest-quarantine" / f"{doc['digest_id']}.json"
        self.assertTrue(qfile.exists())

    def test_diff_grounding_admits_file(self) -> None:
        doc = make_digest(self.root, self.map_path,
                          files=[{"path": "services/api/other.py",
                                  "content_digest": None}])
        out = self.promote(doc, diff_files=["services/api/other.py"])
        payload = mg.memory_store(self.root, base=self.base).load_current().load_payload()
        node = payload["nodes"][out["digest_id"]]
        link = [li for li in node["structural_links"] if li["kind"] == "path"][0]
        self.assertEqual(link["grounding_basis"], "diff")


class AS4AtomicIdempotentReplay(Case):
    def test_double_promotion_idempotent(self) -> None:
        doc = make_digest(self.root, self.map_path)
        a = self.promote(doc)
        b = self.promote(doc)
        self.assertEqual(a["status"], "promoted")
        self.assertEqual(b["status"], "already_promoted")
        self.assertEqual(a["generation_fingerprint"], b["generation_fingerprint"])
        payload = mg.memory_store(self.root, base=self.base).load_current().load_payload()
        self.assertEqual(len(payload["nodes"]), 1)

    def test_crash_before_atomic_promotion_then_replay(self) -> None:
        doc = make_digest(self.root, self.map_path)
        real_replace = os.replace
        with mock.patch.object(ric.os, "replace",
                               side_effect=OSError("injected crash")):
            with self.assertRaises(OSError):
                self.promote(doc)
        # prior state (empty store) intact: no half-written current generation
        store = mg.memory_store(self.root, base=self.base)
        self.assertIsNone(store.load_current())
        # replay completes cleanly to the same state a clean run produces
        out = self.promote(doc)
        self.assertEqual(out["status"], "promoted")
        with tempfile.TemporaryDirectory() as b2:
            clean = mg.promote_digest(doc, self.root, base=b2, map_path=self.map_path)
        self.assertEqual(out["generation_fingerprint"],
                         clean["generation_fingerprint"])
        self.assertIs(os.replace, real_replace)  # patch fully unwound

    def test_conflicting_content_same_id_fails_closed(self) -> None:
        # diff_files is promotion CONTEXT, not digest content: the same
        # digest_id promoted under a different grounding outcome is a conflict.
        doc = make_digest(self.root, self.map_path,
                          files=[{"path": "services/api/other.py",
                                  "content_digest": None}])
        self.promote(doc, diff_files=["services/api/other.py"])  # grounded
        with self.assertRaises(mg.MemoryGraphError) as cm:
            self.promote(doc)  # same id; link now ungrounded -> different node
        self.assertEqual(cm.exception.code, "digest_id_conflict")


class AS5AdvisorySeparation(Case):
    def test_invalid_tag_discarded_digest_promotes(self) -> None:
        doc = make_digest(self.root, self.map_path,
                          advisory_tags=["good-tag", "bad\x00tag"])
        out = self.promote(doc)
        self.assertEqual(out["status"], "promoted")  # never quarantined for a tag
        payload = mg.memory_store(self.root, base=self.base).load_current().load_payload()
        node = payload["nodes"][out["digest_id"]]
        self.assertEqual(node["advisory_tags"], ["good-tag"])
        self.assertEqual(node["discarded_advisory_tags"][0]["reason"],
                         "advisory_tag_control_chars")
        # advisory tags are leaves: never inside structural_links
        for li in node["structural_links"]:
            self.assertNotIn("advisory", li["kind"])


class AS6ConcurrencyAndStorage(Case):
    def test_held_lock_refuses_safely(self) -> None:
        doc = make_digest(self.root, self.map_path)
        store = mg.memory_store(self.root, base=self.base)
        lock = ric.SingleWriterLock(store.root)
        lock.acquire()  # a live concurrent writer (our own pid)
        try:
            with self.assertRaises(ric.CacheError) as cm:
                self.promote(doc)
            self.assertEqual(cm.exception.code, "concurrent_writer")
            self.assertIsNone(store.load_current())  # nothing corrupted
        finally:
            lock.release()
        self.assertEqual(self.promote(doc)["status"], "promoted")

    def test_store_inside_repo_refuses(self) -> None:
        doc = make_digest(self.root, self.map_path)
        with self.assertRaises(ric.CacheError) as cm:
            self.promote(doc, base=os.path.join(self.root, "sneaky-cache"))
        self.assertEqual(cm.exception.code, "cache_inside_repo")


class B1PathTraversalRegression(Case):
    """G3 round-1 blocking defect B1: non-canonical files[].path admitted an
    out-of-repo structural link via '..' traversal + substring evidence match."""

    def test_non_canonical_file_paths_refuse_at_schema(self) -> None:
        for bad in ("services/api/../../../secret.txt", "C:/Users/x/secret.txt",
                    "..", "a//b", "a\\b", "./a", "/abs/path", "a/./b"):
            doc = make_digest(self.root, self.map_path,
                              files=[{"path": bad, "content_digest": None}])
            with self.assertRaises(md.DigestSchemaError) as cm:
                md.validate_digest(doc, self.root)
            self.assertEqual(cm.exception.code, "file_path_not_canonical", bad)

    def test_reviewer_probe_traversal_digest_never_promotes(self) -> None:
        # Reproduce the round-1 exploit shape: a REAL file outside the repo
        # root, claimed via a '..' path and self-referencing evidence.
        with tempfile.TemporaryDirectory() as outer:
            repo = os.path.join(outer, "repo")
            os.makedirs(repo)
            map_path = build_fixture(repo)
            _write(outer, "secret.txt", "outside the repository\n")
            evil = "services/api/../../../secret.txt"
            doc = make_digest(repo, map_path,
                              files=[{"path": evil, "content_digest": None}],
                              evidence_refs=[evil])
            with self.assertRaises(md.DigestSchemaError) as cm:
                mg.promote_digest(doc, repo, base=self.base, map_path=map_path)
            self.assertEqual(cm.exception.code, "file_path_not_canonical")
            self.assertIsNone(mg.memory_store(repo, base=self.base).load_current())

    def test_grounding_refuses_non_canonical_defense_in_depth(self) -> None:
        from tools import memory_grounding as grd
        facts = grd.grounding_facts(self.root, "M0-T001")
        g = grd.ground_file_link("services/api/../../../secret.txt", facts,
                                 [], ["services/api/../../../secret.txt"], [])
        self.assertFalse(g["grounded"])
        self.assertEqual(g["reason"], "non_canonical_path")

    def test_evidence_substring_no_longer_grounds(self) -> None:
        # round-1 O1/B1: a mere MENTION inside an evidence ref must not ground.
        doc = make_digest(self.root, self.map_path,
                          files=[{"path": "services/api/other.py",
                                  "content_digest": None}],
                          evidence_refs=["see services/api/other.py.bak notes"])
        out = self.promote(doc)
        payload = mg.memory_store(self.root, base=self.base).load_current().load_payload()
        node = payload["nodes"][out["digest_id"]]
        self.assertEqual(node["quarantined_links"][0]["reason"], "ungrounded_file_link")

    def test_evidence_exact_match_still_grounds(self) -> None:
        doc = make_digest(self.root, self.map_path,
                          files=[{"path": "services/api/other.py",
                                  "content_digest": None}],
                          evidence_refs=["services/api/other.py"])
        out = self.promote(doc)
        payload = mg.memory_store(self.root, base=self.base).load_current().load_payload()
        node = payload["nodes"][out["digest_id"]]
        link = [li for li in node["structural_links"] if li["kind"] == "path"][0]
        self.assertEqual(link["grounding_basis"], "evidence_ref")


class O4UnicodeControlTags(Case):
    def test_del_and_format_chars_discarded(self) -> None:
        doc = make_digest(self.root, self.map_path,
                          advisory_tags=["ok-tag", "bad\x7ftag", "zw\u200bj"])
        out = self.promote(doc)
        self.assertEqual(out["status"], "promoted")
        payload = mg.memory_store(self.root, base=self.base).load_current().load_payload()
        node = payload["nodes"][out["digest_id"]]
        self.assertEqual(node["advisory_tags"], ["ok-tag"])
        reasons = {d["reason"] for d in node["discarded_advisory_tags"]}
        self.assertEqual(reasons, {"advisory_tag_control_chars"})
        self.assertEqual(len(node["discarded_advisory_tags"]), 2)


class EdgeCases(Case):
    def test_unresolved_task_quarantines_digest(self) -> None:
        doc = make_digest(self.root, self.map_path, task_id="M0-T999")
        out = self.promote(doc)
        self.assertEqual(out["status"], "quarantined")
        self.assertEqual(out["reasons"][0]["reason"], "digest_task_unresolved")

    def test_cli_promote_and_show(self) -> None:
        import subprocess
        doc = make_digest(self.root, self.map_path)
        digest_file = _write(self.root, "digest.json", json.dumps(doc))
        cli = os.path.join(_HERE, "memory_graph.py")
        p = subprocess.run(
            [sys.executable, cli, "--repo", self.root, "--base", self.base,
             "--map", self.map_path, "promote", digest_file],
            capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["status"], "promoted")
        p2 = subprocess.run(
            [sys.executable, cli, "--repo", self.root, "--base", self.base, "show"],
            capture_output=True, text=True)
        self.assertEqual(json.loads(p2.stdout)["nodes"], 1)

    def test_cli_rejects_malformed_digest(self) -> None:
        import subprocess
        digest_file = _write(self.root, "bad.json", json.dumps({"nope": 1}))
        cli = os.path.join(_HERE, "memory_graph.py")
        p = subprocess.run(
            [sys.executable, cli, "--repo", self.root, "--base", self.base,
             "--map", self.map_path, "promote", digest_file],
            capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn("error", json.loads(p.stdout))

    def test_second_digest_extends_graph(self) -> None:
        d1 = make_digest(self.root, self.map_path)
        d2 = make_digest(self.root, self.map_path, outcome="INFO")
        self.promote(d1)
        out = self.promote(d2)
        self.assertEqual(out["nodes"], 2)


if __name__ == "__main__":
    unittest.main()
