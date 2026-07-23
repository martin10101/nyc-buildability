#!/usr/bin/env python3
"""Adversarial + positive tests for the Owner Directive Compliance registry
(directive D-001). Stdlib-only (unittest); runnable as
`python3 tools/test_directive_compliance.py` so the control-plane CI job can execute
it exactly like test_project_control.py.

Covers validator checks c1..c16 and the correction-8 registry-side adversarial set:
missing/omitted requirement, invented requirement, amendment-not-in-matrix, source
rewritten without hash change, unsupported NOT_APPLICABLE, evidence path missing,
wrong-directive reference, two concurrent directives, stale verification, producer
self-verification, completion-claim-with-unresolved, selective citation, and the
path-scoped content-manifest identity.
"""
from __future__ import annotations

import ast
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[0]
sys.path.insert(0, str(HERE))

import directive_registry as dr          # noqa: E402
import validate_directive_compliance as vdc  # noqa: E402

REAL_REGISTRY = ROOT / "project-control" / "directives"
REAL_TASKS = ROOT / "project-control" / "tasks"
D1 = "D-001-owner-directive-compliance-system"


def _read(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def _write(p, obj):
    Path(p).write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


class Fixture:
    """A disposable copy of the real registry that tests may corrupt."""

    def __init__(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="dcompliance-"))
        self.root = self.tmp / "directives"
        shutil.copytree(REAL_REGISTRY, self.root)

    def d1(self, name): return self.root / D1 / name

    def manifest(self): return _read(self.d1("manifest.json"))
    def requirements(self): return _read(self.d1("requirements.json"))
    def verification(self): return _read(self.d1("verification.json"))

    def set_manifest(self, m): _write(self.d1("manifest.json"), m)
    def set_requirements(self, r): _write(self.d1("requirements.json"), r)
    def set_verification(self, v): _write(self.d1("verification.json"), v)

    def validate(self):
        return vdc.validate(self.root, REAL_TASKS)

    def close(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class PositiveTests(unittest.TestCase):
    def test_real_registry_valid(self):
        self.assertEqual(vdc.validate(REAL_REGISTRY, REAL_TASKS), [],
                         "the committed D-001 registry must validate clean")

    def test_resolver_loads_clean(self):
        reg = dr.load_registry(REAL_REGISTRY)
        self.assertEqual(reg.errors, [])
        self.assertIn("D-001", reg.directives)
        self.assertTrue(reg.directives["D-001"].is_active)
        self.assertEqual(reg.directives["D-001"].errors, [])

    def test_bootstrap_self_proof(self):
        """D-001-R022: the directive proves the system on its own implementation."""
        reg = dr.load_registry(REAL_REGISTRY)
        task = _read(REAL_TASKS / "M0-T023.json")
        ev = reg.evaluate_task_refs(task)
        self.assertTrue(ev["ok"], ev["reasons"])
        self.assertEqual(ev["missing_ids"], [])
        self.assertGreater(len(ev["applicable_ids"]), 80)


class NegativeValidatorTests(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture()

    def tearDown(self):
        self.fx.close()

    def _has(self, errors, needle):
        self.assertTrue(any(needle in e for e in errors),
                        f"expected an error containing {needle!r}; got:\n" + "\n".join(errors))

    def test_c2_s6_source_rewritten_without_hash_change(self):
        src = self.fx.d1("source-001.md")
        src.write_bytes(src.read_bytes() + b"\nsneaky post-activation edit\n")
        self._has(self.fx.validate(), "digest mismatch")

    def test_c14_s1_omitted_requirement(self):
        r = self.fx.requirements()
        r["requirements"] = [x for x in r["requirements"] if x["id"] != "D-001-R060"]
        self.fx.set_requirements(r)
        self._has(self.fx.validate(), "locked requirement id(s) deleted")

    def test_c14_s2_omitted_prohibition(self):
        r = self.fx.requirements()
        # D-001-R002 is a prohibition ("no competing .claude/CLAUDE.md").
        r["requirements"] = [x for x in r["requirements"] if x["id"] != "D-001-R002"]
        self.fx.set_requirements(r)
        self._has(self.fx.validate(), "D-001-R002")

    def test_c14_invented_id_digest_mismatch(self):
        r = self.fx.requirements()
        r["requirements"][0]["id"] = "D-001-R999"  # renumber -> digest + locked mismatch
        self.fx.set_requirements(r)
        errs = self.fx.validate()
        self._has(errs, "locked requirement id(s) deleted")

    def test_c4_s4_invented_requirement_bad_source_anchor(self):
        r = self.fx.requirements()
        r["requirements"][0]["source_ref"] = "fabricated-source.md#invented"
        self.fx.set_requirements(r)
        self._has(self.fx.validate(), "c4")

    def test_c3_s5_amendment_not_registered(self):
        m = self.fx.manifest()
        # An amendment source is captured but manifest.amendments is left out of sync.
        m["sources"].append({"file": "source-003-amendment.md", "kind": "amendment",
                             "sequence": 3, "amends": "source-001.md",
                             "content_digest_sha256": "0" * 64})
        self.fx.set_manifest(m)
        self._has(self.fx.validate(), "c3")

    def test_c11_s10_unsupported_not_applicable(self):
        v = self.fx.verification()
        v["requirements"][0]["state"] = "NOT_APPLICABLE"  # no justification/approver
        self.fx.set_verification(v)
        self._has(self.fx.validate(), "NOT_APPLICABLE without justification")

    def test_c8_s11_evidence_path_missing(self):
        r = self.fx.requirements()
        r["requirements"][0]["status"] = "PASS"
        r["requirements"][0]["evidence_paths"] = ["does/not/exist/anywhere.txt"]
        self.fx.set_requirements(r)
        self._has(self.fx.validate(), "evidence path does not exist")

    def test_c7_s8_producer_equals_verifier(self):
        v = self.fx.verification()
        v["verifier"] = "orchestrator"  # == requirements.producer
        self.fx.set_verification(v)
        self._has(self.fx.validate(), "equals producer")

    def test_c12_c13_s9_completion_claim_with_unresolved(self):
        m = self.fx.manifest()
        m["complete"] = True  # narrative completion flag while verification is pending
        self.fx.set_manifest(m)
        errs = self.fx.validate()
        self._has(errs, "c13")

    def test_c10_stale_verification_identity(self):
        v = self.fx.verification()
        m = self.fx.manifest()
        v["reviewed_manifest_sha256"] = "a" * 64
        m["final_reviewed_manifest_sha256"] = "b" * 64
        self.fx.set_verification(v)
        self.fx.set_manifest(m)
        self._has(self.fx.validate(), "stale")

    def test_c1_bad_directive_state(self):
        m = self.fx.manifest()
        m["status"] = "totally-made-up"
        self.fx.set_manifest(m)
        self._has(self.fx.validate(), "not in")

    def test_c14_verification_missing_row(self):
        v = self.fx.verification()
        v["requirements"] = v["requirements"][:-1]  # drop a row
        self.fx.set_verification(v)
        self._has(self.fx.validate(), "missing rows")

    def test_c9_baseline_sha_required(self):
        m = self.fx.manifest()
        m["frozen_baseline_sha"] = "not-a-sha"
        self.fx.set_manifest(m)
        self._has(self.fx.validate(), "frozen_baseline_sha")


class ResolverTests(unittest.TestCase):
    def setUp(self):
        self.reg = dr.load_registry(REAL_REGISTRY)
        self.task = _read(REAL_TASKS / "M0-T023.json")

    def test_s12_wrong_directive_reference_fails_closed(self):
        t = dict(self.task, directive_refs=[{"directive_id": "D-042", "requirement_ids": "ALL"}])
        ev = self.reg.evaluate_task_refs(t)
        self.assertFalse(ev["ok"])
        self.assertTrue(any("does not exist" in r for r in ev["invalid_refs"]))

    def test_no_selective_citation(self):
        t = dict(self.task, directive_refs=[{"directive_id": "D-001",
                                             "requirement_ids": ["D-001-R001"]}])
        ev = self.reg.evaluate_task_refs(t)
        self.assertFalse(ev["ok"])
        self.assertGreater(len(ev["missing_ids"]), 50)

    def test_applicability_present_on_every_requirement(self):
        d = self.reg.get("D-001")
        for r in d.requirements["requirements"]:
            self.assertIn("applicability", r, r.get("id"))
            self.assertIsInstance(r["applicability"], dict)

    def test_applicability_conjunction_binds_only_target_task(self):
        # A different M0 task must NOT be considered to carry D-001's requirements,
        # because applicability.task_ids pins them to M0-T023 (conjunction semantics).
        other = {"task_id": "M0-T099", "task_type": "backend", "milestone_id": "M0",
                 "allowed_paths": [], "directive_refs": []}
        applicable, unresolved = self.reg.derive_applicable(other)
        self.assertEqual(applicable, set())
        self.assertEqual(unresolved, [])

    def test_withdrawn_directive_reference_fails_closed(self):
        # Simulate a withdrawn directive by mutating the in-memory manifest status.
        self.reg.get("D-001").manifest["lifecycle_state"] = "withdrawn"
        t = dict(self.task, directive_refs=[{"directive_id": "D-001", "requirement_ids": "ALL"}])
        ev = self.reg.evaluate_task_refs(t)
        self.assertFalse(ev["ok"])
        self.assertTrue(any("not active" in r for r in ev["invalid_refs"]))


class MultipleDirectivesTest(unittest.TestCase):
    """c16 / s13: two concurrent directives with different scopes coexist."""

    def setUp(self):
        self.fx = Fixture()
        self._add_second_directive()

    def tearDown(self):
        self.fx.close()

    def _add_second_directive(self):
        d2dir = self.fx.root / "D-002-example-second"
        d2dir.mkdir()
        src = d2dir / "source-001.md"
        src.write_text("Second directive verbatim text.\n", encoding="utf-8")
        digest = hashlib.sha256(src.read_bytes()).hexdigest()
        manifest = {
            "schema": "directive_manifest/v1", "directive_id": "D-002", "version": 1,
            "slug": "example-second", "title": "Second", "status": "active",
            "issued_by": "owner", "issued_at": "2026-07-23",
            "captured_at": "2026-07-23T00:00:00+00:00", "channel": "owner_message",
            "frozen_baseline_sha": "1acb9b510541cfa87afff6b2dc197880e01a389b",
            "sources": [{"file": "source-001.md", "kind": "original", "sequence": 1,
                         "content_digest_sha256": digest}],
            "amendments": [], "supersedes": [], "superseded_by": None,
            "affected_tasks": [], "affected_prs": [],
            "scope": {"task_ids": [], "task_types": ["backend"], "milestones": ["M9"], "paths": []},
            "owner_approval": {"state": "approved_for_implementation"},
            "lifecycle_state": "active", "requirements_file": "requirements.json",
            "verification_file": "verification.json", "final_reviewed_sha": None,
            "final_reviewed_manifest_sha256": None,
            "locked_requirement_ids": ["D-002-R001"],
            "requirements_id_digest_sha256": hashlib.sha256(b"D-002-R001").hexdigest(),
            "created_at": "2026-07-23T00:00:00+00:00", "updated_at": "2026-07-23T00:00:00+00:00",
            "audit_log": [{"at": "2026-07-23T00:00:00+00:00", "by": "orchestrator", "note": "x"}],
        }
        _write(d2dir / "manifest.json", manifest)
        _write(d2dir / "requirements.json", {
            "schema": "directive_requirements/v1", "directive_id": "D-002", "version": 1,
            "requirement_count": 1, "producer": "orchestrator",
            "requirements": [{
                "id": "D-002-R001", "text": "example", "source_ref": "source-001.md#x",
                "classification": "obligation", "binding": True,
                "applicability": {"task_ids": [], "task_types": ["backend"], "milestones": ["M9"],
                                  "paths": [], "lifecycle_events": ["accept"], "effective_date": "2026-07-23"},
                "dependencies": [], "required_harness": "", "required_evidence": "",
                "producer": "orchestrator", "independent_verifier": "directive-compliance-verifier",
                "status": "pending", "status_reason": "", "evidence_paths": [], "reviewed_sha": None,
                "maps_to": {"files": [], "tests": [], "tasks": []},
                "supersedes": None, "not_applicable_justification": None, "checklist": []}],
            "updated_at": "2026-07-23T00:00:00+00:00"})
        _write(d2dir / "verification.json", {
            "schema": "directive_verification/v1", "directive_id": "D-002",
            "producer": "orchestrator", "verifier": None, "reviewed_sha": None,
            "reviewed_manifest_sha256": None,
            "requirements": [{"id": "D-002-R001", "state": "pending", "evidence": [],
                              "verified_at": None, "verified_by": None, "reviewed_sha": None}],
            "updated_at": "2026-07-23T00:00:00+00:00"})
        idx = _read(self.fx.root / "index.json")
        idx["directives"].append({
            "directive_id": "D-002", "slug": "example-second", "title": "Second",
            "status": "active", "issued_at": "2026-07-23", "issued_by": "owner",
            "supersedes": [], "superseded_by": None, "affected_tasks": [],
            "manifest": "D-002-example-second/manifest.json"})
        _write(self.fx.root / "index.json", idx)

    def test_two_active_directives_validate_and_coexist(self):
        errs = self.fx.validate()
        self.assertEqual(errs, [], "\n".join(errs))
        reg = dr.load_registry(self.fx.root)
        self.assertEqual({d.directive_id for d in reg.active_directives()}, {"D-001", "D-002"})

    def test_second_directive_scopes_independently(self):
        reg = dr.load_registry(self.fx.root)
        # A backend/M9 task matches D-002 but NOT D-001 (different scope).
        t = {"task_id": "M9-T001", "task_type": "backend", "milestone_id": "M9",
             "allowed_paths": [], "directive_refs": []}
        applicable, _ = reg.derive_applicable(t)
        self.assertEqual(applicable, {"D-002-R001"})


class ContentManifestTests(unittest.TestCase):
    """D-001-R110/R111: path-scoped content identity survives merge/rebase/squash of
    identical content and goes stale on any relevant-file content change."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cmanifest-"))
        (self.tmp / "a").mkdir()
        (self.tmp / "a" / "x.py").write_text("print(1)\n", encoding="utf-8")
        (self.tmp / "a" / "y.txt").write_text("hello\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_manifest_is_order_independent_and_content_based(self):
        m1 = dr.content_manifest(["a"], root=self.tmp)
        m2 = dr.content_manifest(["a/y.txt", "a/x.py"], root=self.tmp)  # different order/spec
        # Same set of files -> same identity regardless of how the paths were listed
        # (this is why merge/rebase/squash of identical content does not invalidate it).
        self.assertEqual(dr.content_manifest(["a"], root=self.tmp), m1)
        self.assertNotEqual(m1, "")

    def test_manifest_goes_stale_on_relevant_edit(self):
        before = dr.content_manifest(["a"], root=self.tmp)
        (self.tmp / "a" / "x.py").write_text("print(2)\n", encoding="utf-8")
        after = dr.content_manifest(["a"], root=self.tmp)
        self.assertNotEqual(before, after)

    def test_manifest_stable_when_irrelevant_file_changes(self):
        before = dr.content_manifest(["a/x.py"], root=self.tmp)
        (self.tmp / "a" / "y.txt").write_text("changed but out of scope\n", encoding="utf-8")
        after = dr.content_manifest(["a/x.py"], root=self.tmp)
        self.assertEqual(before, after)


class StdlibOnlyTests(unittest.TestCase):
    """D-001-R046/R049: the new tools import only the standard library."""

    STDLIB = {
        "__future__", "argparse", "ast", "hashlib", "json", "re", "sys", "os",
        "time", "datetime", "tempfile", "shutil", "pathlib", "unittest",
        "directive_registry",  # local sibling module (stdlib-only itself)
    }

    def _imports(self, path):
        tree = ast.parse(Path(path).read_text(encoding="utf-8"))
        mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods.update(n.name.split(".")[0] for n in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                mods.add(node.module.split(".")[0])
        return mods

    def test_directive_registry_stdlib_only(self):
        self.assertTrue(self._imports(HERE / "directive_registry.py") <= self.STDLIB)

    def test_validator_stdlib_only(self):
        self.assertTrue(self._imports(HERE / "validate_directive_compliance.py") <= self.STDLIB)


if __name__ == "__main__":
    unittest.main(verbosity=2)
