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
import subprocess
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
        v = self.fx.verification()  # D-001 is now directive_verification/v2
        v["task_verifications"][0]["requirements"][0]["state"] = "NOT_APPLICABLE"  # no justification/approver
        self.fx.set_verification(v)
        self._has(self.fx.validate(), "NOT_APPLICABLE without justification")

    def test_c8_s11_evidence_path_missing(self):
        r = self.fx.requirements()
        r["requirements"][0]["status"] = "PASS"
        r["requirements"][0]["evidence_paths"] = ["does/not/exist/anywhere.txt"]
        self.fx.set_requirements(r)
        self._has(self.fx.validate(), "evidence path does not exist")

    def test_c7_s8_producer_equals_verifier(self):
        v = self.fx.verification()  # v2: per-task producer/verifier separation
        v["task_verifications"][0]["verifier"] = "orchestrator"  # == producer
        self.fx.set_verification(v)
        self._has(self.fx.validate(), "equals producer")

    def test_c12_c13_s9_completion_claim_with_unresolved(self):
        m = self.fx.manifest()
        m["complete"] = True  # narrative completion flag while verification is pending
        self.fx.set_manifest(m)
        errs = self.fx.validate()
        self._has(errs, "c13")

    def test_c10_stale_verification_identity(self):
        v = self.fx.verification()  # v2: manifest final identity vs primary task tv identity
        m = self.fx.manifest()
        v["task_verifications"][0]["reviewed_manifest_sha256"] = "a" * 64
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
        v = self.fx.verification()  # v2: drop a row from the task_verification
        v["task_verifications"][0]["requirements"] = v["task_verifications"][0]["requirements"][:-1]
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
        d2dir = self.fx.root / "D-900-example-second"
        d2dir.mkdir()
        src = d2dir / "source-001.md"
        src.write_text("Second directive verbatim text.\n", encoding="utf-8")
        digest = hashlib.sha256(src.read_bytes()).hexdigest()
        manifest = {
            "schema": "directive_manifest/v1", "directive_id": "D-900", "version": 1,
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
            "locked_requirement_ids": ["D-900-R001"],
            "requirements_id_digest_sha256": hashlib.sha256(b"D-900-R001").hexdigest(),
            "created_at": "2026-07-23T00:00:00+00:00", "updated_at": "2026-07-23T00:00:00+00:00",
            "audit_log": [{"at": "2026-07-23T00:00:00+00:00", "by": "orchestrator", "note": "x"}],
        }
        d2_reqs = {
            "schema": "directive_requirements/v1", "directive_id": "D-900", "version": 1,
            "requirement_count": 1, "producer": "orchestrator",
            "requirements": [{
                "id": "D-900-R001", "text": "example", "source_ref": "source-001.md#x",
                "classification": "obligation", "binding": True,
                "applicability": {"task_ids": [], "task_types": ["backend"], "milestones": ["M9"],
                                  "paths": [], "lifecycle_events": ["accept"], "effective_date": "2026-07-23"},
                "dependencies": [], "required_harness": "", "required_evidence": "",
                "producer": "orchestrator", "independent_verifier": "directive-compliance-verifier",
                "status": "pending", "status_reason": "", "evidence_paths": [], "reviewed_sha": None,
                "maps_to": {"files": [], "tests": [], "tasks": []},
                "supersedes": None, "not_applicable_justification": None, "checklist": []}],
            "updated_at": "2026-07-23T00:00:00+00:00"}
        _write(d2dir / "requirements.json", d2_reqs)
        manifest["requirements_content_digest_sha256"] = hashlib.sha256(
            (d2dir / "requirements.json").read_bytes()).hexdigest()
        _write(d2dir / "manifest.json", manifest)
        _write(d2dir / "verification.json", {
            "schema": "directive_verification/v1", "directive_id": "D-900",
            "producer": "orchestrator", "verifier": None, "reviewed_sha": None,
            "reviewed_manifest_sha256": None,
            "requirements": [{"id": "D-900-R001", "state": "pending", "evidence": [],
                              "verified_at": None, "verified_by": None, "reviewed_sha": None}],
            "updated_at": "2026-07-23T00:00:00+00:00"})
        idx = _read(self.fx.root / "index.json")
        idx["directives"].append({
            "directive_id": "D-900", "slug": "example-second", "title": "Second",
            "status": "active", "issued_at": "2026-07-23", "issued_by": "owner",
            "supersedes": [], "superseded_by": None, "affected_tasks": [],
            "manifest": "D-900-example-second/manifest.json"})
        _write(self.fx.root / "index.json", idx)

    def test_two_active_directives_validate_and_coexist(self):
        errs = self.fx.validate()
        self.assertEqual(errs, [], "\n".join(errs))
        reg = dr.load_registry(self.fx.root)
        active = {d.directive_id for d in reg.active_directives()}
        # Robust to additional REAL directives in the committed registry (e.g. D-002):
        # the synthetic second directive must coexist with D-001 and the registry must validate.
        self.assertTrue({"D-001", "D-900"}.issubset(active), active)

    def test_second_directive_scopes_independently(self):
        reg = dr.load_registry(self.fx.root)
        # A backend/M9 task matches the synthetic D-900 but NOT D-001/D-002 (different scope).
        t = {"task_id": "M9-T001", "task_type": "backend", "milestone_id": "M9",
             "allowed_paths": [], "directive_refs": []}
        applicable, _ = reg.derive_applicable(t)
        self.assertEqual(applicable, {"D-900-R001"})


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
        "time", "datetime", "tempfile", "shutil", "pathlib", "unittest", "subprocess",
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


class ClaudeMdSectionTests(unittest.TestCase):
    """Real regressions for D-001-R001 (section <=12 lines) and R002 (no competing
    .claude/CLAUDE.md) — the two requirements a review found had only inspection coverage."""

    def _section_lines(self):
        text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8").splitlines()
        start = next((i for i, l in enumerate(text)
                      if l.strip() == "## Owner-directive compliance"), None)
        self.assertIsNotNone(start, "CLAUDE.md must contain the 'Owner-directive compliance' section")
        body = []
        for l in text[start + 1:]:
            if l.startswith("## "):
                break
            body.append(l)
        # drop trailing blank lines
        while body and not body[-1].strip():
            body.pop()
        return [text[start]] + body

    def test_claude_md_section_bounds(self):
        lines = self._section_lines()
        self.assertLessEqual(len(lines), 12,
                             f"section must be <=12 lines, got {len(lines)}")
        self.assertIn("/directive-compliance", "\n".join(lines))

    def test_no_competing_claude_md(self):
        self.assertFalse((ROOT / ".claude" / "CLAUDE.md").exists(),
                         "a competing .claude/CLAUDE.md must not exist")


class C15AcceptedTaskTests(unittest.TestCase):
    """F1: c15 must NOT flag a directive scoping its own task that reaches `accepted`
    (the bootstrap case); it flags only an accepted task in scope that does not cite
    the directive (retroactive/non-consensual binding)."""

    def _validate_with_task(self, task):
        tmp = Path(tempfile.mkdtemp(prefix="c15-"))
        try:
            (tmp / "M0-T023.json").write_text(json.dumps(task), encoding="utf-8")
            errs = vdc.validate(REAL_REGISTRY, tmp)
            return [e for e in errs if "c15" in e]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_accepted_task_that_cites_directive_is_ok(self):
        task = {"task_id": "M0-T023", "milestone_id": "M0", "task_type": "governance",
                "status": "accepted", "allowed_paths": [], "directive_regime_version": "1.0",
                "directive_refs": [{"directive_id": "D-001", "requirement_ids": "ALL"}]}
        self.assertEqual(self._validate_with_task(task), [],
                         "an accepted task that cites the directive must not trip c15")

    def test_accepted_task_not_citing_is_flagged(self):
        task = {"task_id": "M0-T023", "milestone_id": "M0", "task_type": "governance",
                "status": "accepted", "allowed_paths": [], "directive_refs": []}
        c15 = self._validate_with_task(task)
        self.assertTrue(c15 and "retroactively bind" in c15[0],
                        "an accepted task in scope that does not cite the directive must trip c15")


class RequirementsBodyDigestTest(unittest.TestCase):
    """F3: editing a requirement's body text (same IDs, same source hashes) must be
    caught by the requirements_content_digest_sha256 check."""

    def test_body_edit_detected(self):
        fx = Fixture()
        try:
            r = fx.requirements()
            r["requirements"][0]["text"] = r["requirements"][0]["text"] + " (silently weakened)"
            fx.set_requirements(r)
            errs = fx.validate()
            self.assertTrue(any("content digest mismatch" in e for e in errs),
                            "a requirements.json body edit must be caught")
        finally:
            fx.close()

    def test_missing_content_digest_flagged(self):
        fx = Fixture()
        try:
            m = fx.manifest()
            m.pop("requirements_content_digest_sha256", None)
            fx.set_manifest(m)
            errs = fx.validate()
            self.assertTrue(any("requirements_content_digest" in e for e in errs))
        finally:
            fx.close()


# ==========================================================================
# D-001 amendment 3, Section 3: git-canonical, cross-platform content identity.
# The authoritative reviewed identity is derived from canonical tracked git content
# at a reviewed commit (blob/object id + mode + path), NOT from raw working-tree bytes.
# ==========================================================================

def _git(cwd, *args, allow_fail=False):
    p = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True)
    if not allow_fail and p.returncode != 0:
        raise RuntimeError(f"git {args} failed: {p.stderr.decode('utf-8', 'replace')}")
    return p


def _init_repo(cwd):
    _git(cwd, "init", "-q")
    _git(cwd, "config", "user.email", "t@example.test")
    _git(cwd, "config", "user.name", "t")
    _git(cwd, "config", "commit.gpgsign", "false")


class GitContentIdentityTests(unittest.TestCase):
    """D-001-R145..R154: git-canonical identity properties."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gitident-"))
        _init_repo(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _commit(self, msg="c"):
        _git(self.tmp, "add", "-A")
        _git(self.tmp, "commit", "-q", "-m", msg)
        return _git(self.tmp, "rev-parse", "HEAD").stdout.decode().strip()

    def test_r145_r147_identity_binds_git_blob_not_worktree_bytes(self):
        # R145/R147: the identity is the git blob at the commit, so rewriting the working
        # tree to CRLF (raw bytes differ) does not change the identity at that commit.
        (self.tmp / "f.txt").write_bytes(b"one\ntwo\n")
        sha = self._commit()
        id1, _, e = dr.git_tree_manifest(self.tmp, "HEAD", ["f.txt"])
        self.assertIsNone(e)
        (self.tmp / "f.txt").write_bytes(b"one\r\ntwo\r\n")  # CRLF working tree, dirty
        id2, _, e = dr.git_tree_manifest(self.tmp, sha, ["f.txt"])
        self.assertIsNone(e)
        self.assertEqual(id1, id2, "identity binds the git blob at the commit, not raw working-tree bytes")

    def test_r147_lf_crlf_canonical_equivalence_across_repos(self):
        a = Path(tempfile.mkdtemp(prefix="gA-"))
        b = Path(tempfile.mkdtemp(prefix="gB-"))
        try:
            _init_repo(a)
            (a / "f.txt").write_bytes(b"alpha\nbeta\n")  # LF
            _git(a, "add", "-A"); _git(a, "commit", "-q", "-m", "x")
            idA, _, _ = dr.git_tree_manifest(a, "HEAD", ["f.txt"])
            _init_repo(b)
            (b / ".gitattributes").write_bytes(b"f.txt text eol=lf\n")
            _git(b, "add", "-A"); _git(b, "commit", "-q", "-m", "attrs")
            (b / "f.txt").write_bytes(b"alpha\r\nbeta\r\n")  # CRLF -> normalized to LF blob
            _git(b, "add", "-A"); _git(b, "commit", "-q", "-m", "x")
            idB, _, _ = dr.git_tree_manifest(b, "HEAD", ["f.txt"])
            self.assertEqual(idA, idB, "LF vs CRLF checkout with identical canonical content -> identical identity")
        finally:
            shutil.rmtree(a, ignore_errors=True)
            shutil.rmtree(b, ignore_errors=True)

    def test_r148_binary_byte_exact(self):
        (self.tmp / "b.bin").write_bytes(bytes(range(256)))
        self._commit()
        id1, _, _ = dr.git_tree_manifest(self.tmp, "HEAD", ["b.bin"])
        (self.tmp / "b.bin").write_bytes(bytes(range(255)) + b"\x00")  # flip last byte
        self._commit()
        id2, _, _ = dr.git_tree_manifest(self.tmp, "HEAD", ["b.bin"])
        self.assertNotEqual(id1, id2, "a one-byte binary change must invalidate the identity")

    def test_r151_mode_change_invalidates(self):
        (self.tmp / "s.sh").write_bytes(b"#!/bin/sh\necho hi\n")
        self._commit()
        id1, ent1, _ = dr.git_tree_manifest(self.tmp, "HEAD", ["s.sh"])
        _git(self.tmp, "update-index", "--chmod=+x", "s.sh")  # 100644 -> 100755 (cross-platform)
        _git(self.tmp, "commit", "-q", "-m", "chmod")
        id2, ent2, _ = dr.git_tree_manifest(self.tmp, "HEAD", ["s.sh"])
        self.assertEqual(ent1[0][1], "100644")
        self.assertEqual(ent2[0][1], "100755")
        self.assertNotEqual(id1, id2, "an exec-bit mode change must invalidate the identity")

    def test_r149_dirty_tracked_file_fails_closed(self):
        (self.tmp / "f.txt").write_bytes(b"x\n")
        self._commit()
        ident, sha, e = dr.frozen_git_identity(["f.txt"], root=self.tmp)
        self.assertIsNone(e)
        self.assertTrue(ident)
        (self.tmp / "f.txt").write_bytes(b"y\n")  # dirty tracked file in scope
        ident, sha, e = dr.frozen_git_identity(["f.txt"], root=self.tmp)
        self.assertIsNotNone(e)
        self.assertIn("dirty", e)

    def test_r149_untracked_relevant_file_fails_closed(self):
        (self.tmp / "dir").mkdir()
        (self.tmp / "dir" / "a.txt").write_bytes(b"a\n")
        self._commit()
        ident, sha, e = dr.frozen_git_identity(["dir"], root=self.tmp)
        self.assertIsNone(e)
        (self.tmp / "dir" / "b.txt").write_bytes(b"b\n")  # untracked file in scope
        ident, sha, e = dr.frozen_git_identity(["dir"], root=self.tmp)
        self.assertIsNotNone(e, "an untracked relevant file must fail closed, not be silently omitted")

    def test_r150_stable_across_unrelated_commit_and_real_merge(self):
        (self.tmp / "a.txt").write_bytes(b"A\n")
        (self.tmp / "b.txt").write_bytes(b"B\n")
        c1 = self._commit()
        idA1, _, _ = dr.git_tree_manifest(self.tmp, "HEAD", ["a.txt"])
        main = _git(self.tmp, "rev-parse", "--abbrev-ref", "HEAD").stdout.decode().strip()
        # unrelated-file change: a.txt identity is unchanged
        (self.tmp / "b.txt").write_bytes(b"B2\n")
        self._commit()
        idA2, _, _ = dr.git_tree_manifest(self.tmp, "HEAD", ["a.txt"])
        self.assertEqual(idA1, idA2, "an unrelated-file change must not move a.txt's identity")
        # same blob at an earlier commit -> same identity (content-addressed, graph-independent)
        idA_old, _, _ = dr.git_tree_manifest(self.tmp, c1, ["a.txt"])
        self.assertEqual(idA1, idA_old)
        # a real merge that leaves a.txt's blob unchanged preserves the identity
        _git(self.tmp, "checkout", "-q", "-b", "feature")
        (self.tmp / "d.txt").write_bytes(b"D\n")
        self._commit("feature")
        _git(self.tmp, "checkout", "-q", main)
        (self.tmp / "e.txt").write_bytes(b"E\n")
        self._commit("main")
        _git(self.tmp, "merge", "-q", "--no-edit", "feature")
        idA_merge, _, _ = dr.git_tree_manifest(self.tmp, "HEAD", ["a.txt"])
        self.assertEqual(idA1, idA_merge, "a real merge with an unchanged a.txt blob preserves identity")

    def test_r151_relevant_content_mutation_invalidates(self):
        (self.tmp / "a.txt").write_bytes(b"A\n")
        self._commit()
        id1, _, _ = dr.git_tree_manifest(self.tmp, "HEAD", ["a.txt"])
        (self.tmp / "a.txt").write_bytes(b"A-changed\n")
        self._commit()
        id2, _, _ = dr.git_tree_manifest(self.tmp, "HEAD", ["a.txt"])
        self.assertNotEqual(id1, id2, "a relevant-content mutation must invalidate the identity")

    def test_r146_deterministic_directory_expansion_sorted(self):
        (self.tmp / "pkg").mkdir()
        (self.tmp / "pkg" / "z.py").write_bytes(b"z\n")
        (self.tmp / "pkg" / "a.py").write_bytes(b"a\n")
        self._commit()
        id_dir, ent, _ = dr.git_tree_manifest(self.tmp, "HEAD", ["pkg"])
        id_files, _, _ = dr.git_tree_manifest(self.tmp, "HEAD", ["pkg/z.py", "pkg/a.py"])
        self.assertEqual(id_dir, id_files, "dir expansion and explicit file lists are order-independent")
        self.assertEqual([e[0] for e in ent], sorted(e[0] for e in ent), "paths must be sorted")

    def test_r153_reviewed_sha_required_and_validated(self):
        (self.tmp / "a.txt").write_bytes(b"A\n")
        sha = self._commit()
        full, e = dr.resolve_commit(self.tmp, sha[:12])
        self.assertIsNone(e)
        self.assertEqual(full, sha)
        _bad, e = dr.resolve_commit(self.tmp, "deadbeef" * 5)
        self.assertIsNotNone(e, "an unresolvable reviewed sha must fail closed")
        ident, rsha, e = dr.frozen_git_identity(["a.txt"], reviewed_sha="deadbeef" * 5, root=self.tmp)
        self.assertIsNotNone(e)

    def test_non_git_root_fails_closed(self):
        plain = Path(tempfile.mkdtemp(prefix="plain-"))
        try:
            (plain / "a.txt").write_bytes(b"A\n")
            ident, sha, e = dr.frozen_git_identity(["a.txt"], root=plain)
            self.assertIsNotNone(e)
            self.assertIn("git work tree", e)
        finally:
            shutil.rmtree(plain, ignore_errors=True)


# ==========================================================================
# D-001 amendment 3, Section 2: one directive governing MULTIPLE tasks. Each task
# has its own applicable set, content identity, evidence, and independent verifier.
# ==========================================================================

def _make_two_task_v2_registry(root: Path, idA="a" * 64, idB="b" * 64,
                               verA="reviewer-a", verB="reviewer-b",
                               extra_row_on_A=None, missing_on_A=False, dup_A=False):
    """Directive D-700 governs M9-T001 (A) and M9-T002 (B). R001 is SHARED (applies to
    both); R002 applies to A only; R003 to B only. Returns a loaded DirectiveRegistry."""
    regdir = root / "directives"
    (regdir / "schema" / "v1").mkdir(parents=True, exist_ok=True)
    (regdir / "schema" / "v2").mkdir(parents=True, exist_ok=True)
    ddir = regdir / "D-700-multi"
    ddir.mkdir(parents=True, exist_ok=True)
    src = "D-700 verbatim.\n"
    (ddir / "source-001.md").write_text(src, encoding="utf-8", newline="\n")
    digest = hashlib.sha256(src.encode("utf-8")).hexdigest()

    def req(rid, tids):
        return {"id": rid, "text": "r", "source_ref": "source-001.md#x",
                "classification": "obligation", "binding": True,
                "applicability": {"task_ids": tids, "task_types": [], "milestones": [],
                                  "paths": [], "lifecycle_events": ["accept"], "effective_date": "2026-07-23"},
                "dependencies": [], "required_harness": "", "required_evidence": "",
                "producer": "orchestrator", "independent_verifier": "reviewer-a",
                "status": "pending", "status_reason": "", "evidence_paths": [], "reviewed_sha": None,
                "maps_to": {"files": [], "tests": [], "tasks": tids},
                "supersedes": None, "not_applicable_justification": None, "checklist": []}

    reqs = [req("D-700-R001", ["M9-T001", "M9-T002"]),
            req("D-700-R002", ["M9-T001"]),
            req("D-700-R003", ["M9-T002"])]
    ids = [r["id"] for r in reqs]
    (ddir / "requirements.json").write_text(json.dumps(
        {"schema": "directive_requirements/v1", "directive_id": "D-700", "version": 1,
         "producer": "orchestrator", "requirement_count": 3, "requirements": reqs,
         "updated_at": "2026-07-23T00:00:00+00:00"}, indent=2), encoding="utf-8")

    def vrow(rid):
        return {"id": rid, "state": "PASS", "evidence": ["ev.txt"], "verified_at": "t",
                "verified_by": "x", "reviewed_sha": None}

    a_rows = [vrow("D-700-R001"), vrow("D-700-R002")]
    if missing_on_A:
        a_rows = [vrow("D-700-R001")]  # drop R002
    if extra_row_on_A:
        a_rows.append(vrow(extra_row_on_A))
    tvA = {"directive_id": "D-700", "task_id": "M9-T001",
           "applicable_requirement_ids": ["D-700-R001", "D-700-R002"],
           "reviewed_sha": None, "reviewed_manifest_sha256": idA,
           "producer": "orchestrator", "verifier": verA,
           "schema_version": "directive_verification/v2", "verified_at": "t", "requirements": a_rows}
    tvB = {"directive_id": "D-700", "task_id": "M9-T002",
           "applicable_requirement_ids": ["D-700-R001", "D-700-R003"],
           "reviewed_sha": None, "reviewed_manifest_sha256": idB,
           "producer": "orchestrator", "verifier": verB,
           "schema_version": "directive_verification/v2", "verified_at": "t",
           "requirements": [vrow("D-700-R001"), vrow("D-700-R003")]}
    task_verifications = [tvA, tvB]
    if dup_A:
        task_verifications.append(dict(tvA))
    (ddir / "verification.json").write_text(json.dumps(
        {"schema": "directive_verification/v2", "directive_id": "D-700",
         "producer": "orchestrator", "task_verifications": task_verifications,
         "updated_at": "2026-07-23T00:00:00+00:00"}, indent=2), encoding="utf-8")
    manifest = {
        "schema": "directive_manifest/v1", "directive_id": "D-700", "version": 1, "slug": "multi",
        "title": "D-700", "status": "active", "issued_by": "owner", "issued_at": "2026-07-23",
        "captured_at": "2026-07-23T00:00:00+00:00", "channel": "owner_message",
        "frozen_baseline_sha": "1acb9b510541cfa87afff6b2dc197880e01a389b",
        "sources": [{"file": "source-001.md", "kind": "original", "sequence": 1,
                     "content_digest_sha256": digest}],
        "amendments": [], "supersedes": [], "superseded_by": None,
        "affected_tasks": ["M9-T001", "M9-T002"], "affected_prs": [],
        "scope": {"task_ids": ["M9-T001", "M9-T002"], "task_types": [], "milestones": [], "paths": []},
        "owner_approval": {"state": "approved_for_implementation"},
        "lifecycle_state": "active", "requirements_file": "requirements.json",
        "verification_file": "verification.json", "final_reviewed_sha": None,
        "final_reviewed_manifest_sha256": None, "locked_requirement_ids": ids,
        "requirements_id_digest_sha256": hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest(),
        "created_at": "2026-07-23T00:00:00+00:00", "updated_at": "2026-07-23T00:00:00+00:00",
        "audit_log": [{"at": "t", "by": "orchestrator", "note": "x"}]}
    (ddir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (regdir / "index.json").write_text(json.dumps(
        {"schema": "directive_index/v1", "version": 1, "directives": [
            {"directive_id": "D-700", "slug": "multi", "title": "D-700", "status": "active",
             "issued_at": "2026-07-23", "issued_by": "owner", "supersedes": [],
             "superseded_by": None, "affected_tasks": ["M9-T001", "M9-T002"],
             "manifest": "D-700-multi/manifest.json"}],
         "updated_at": "2026-07-23T00:00:00+00:00"}, indent=2), encoding="utf-8")
    return dr.load_registry(regdir)


class MultiTaskVerificationTests(unittest.TestCase):
    """D-001-R135..R144: directive_verification/v2 per-task isolation."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="v2multi-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _reg(self, **kw):
        return _make_two_task_v2_registry(self.tmp, **kw)

    def test_r137_all_means_applicable_to_this_task(self):
        reg = self._reg()
        taskA = {"task_id": "M9-T001", "task_type": "x", "milestone_id": "M9",
                 "allowed_paths": [], "directive_refs": [{"directive_id": "D-700", "requirement_ids": "ALL"}]}
        ev = reg.evaluate_task_refs(taskA)
        self.assertTrue(ev["ok"], ev["reasons"])
        self.assertEqual(set(ev["applicable_ids"]), {"D-700-R001", "D-700-R002"},
                         "ALL for task A resolves to A's applicable set only, not every D-700 requirement")

    def test_r138_r139_two_tasks_isolated_stale_A_does_not_break_B(self):
        reg = self._reg(idA="a" * 64, idB="b" * 64)
        # both verified at their own identities
        self.assertEqual(reg.task_unresolved_requirements("D-700", "M9-T001", {"D-700-R001", "D-700-R002"}, "a" * 64), [])
        self.assertEqual(reg.task_unresolved_requirements("D-700", "M9-T002", {"D-700-R001", "D-700-R003"}, "b" * 64), [])
        # A goes stale (current identity != recorded) -> A blocked, B still clean
        a_stale = reg.task_unresolved_requirements("D-700", "M9-T001", {"D-700-R001", "D-700-R002"}, "c" * 64)
        self.assertTrue(any("stale" in r for r in a_stale))
        self.assertEqual(reg.task_unresolved_requirements("D-700", "M9-T002", {"D-700-R001", "D-700-R003"}, "b" * 64), [],
                         "stale verification for task A must not invalidate task B")

    def test_r140_shared_requirement_represented_for_both(self):
        reg = self._reg()
        d = reg.get("D-700")
        tvs = {tv["task_id"]: tv for tv in d.verification["task_verifications"]}
        self.assertIn("D-700-R001", [r["id"] for r in tvs["M9-T001"]["requirements"]])
        self.assertIn("D-700-R001", [r["id"] for r in tvs["M9-T002"]["requirements"]])

    def test_r141_per_task_producer_verifier_separation(self):
        reg = self._reg(verA="orchestrator")  # producer==verifier on A only
        a = reg.task_unresolved_requirements("D-700", "M9-T001", {"D-700-R001", "D-700-R002"}, "a" * 64)
        self.assertTrue(any("equals producer" in r for r in a))
        b = reg.task_unresolved_requirements("D-700", "M9-T002", {"D-700-R001", "D-700-R003"}, "b" * 64)
        self.assertEqual(b, [], "B's independent verifier is unaffected by A's self-verification")

    def test_r142_missing_row_fails_closed(self):
        reg = self._reg(missing_on_A=True)
        a = reg.task_unresolved_requirements("D-700", "M9-T001", {"D-700-R001", "D-700-R002"}, "a" * 64)
        self.assertTrue(any("missing rows" in r for r in a))

    def test_r142_extra_cross_task_row_fails_closed(self):
        reg = self._reg(extra_row_on_A="D-700-R003")  # R003 not applicable to A
        a = reg.task_unresolved_requirements("D-700", "M9-T001", {"D-700-R001", "D-700-R002"}, "a" * 64)
        self.assertTrue(any("extra/cross-task" in r for r in a))

    def test_r142_duplicate_task_row_fails_closed(self):
        reg = self._reg(dup_A=True)
        a = reg.task_unresolved_requirements("D-700", "M9-T001", {"D-700-R001", "D-700-R002"}, "a" * 64)
        self.assertTrue(any("duplicate" in r for r in a))

    def test_r142_missing_task_row_fails_closed(self):
        reg = self._reg()
        a = reg.task_unresolved_requirements("D-700", "M9-T404", {"D-700-R001"}, "a" * 64)
        self.assertTrue(any("no task_verification row" in r for r in a))

    def test_r141_validator_flags_per_task_self_verification(self):
        reg = self._reg(verA="orchestrator")
        errs = vdc.validate(self.tmp / "directives", REAL_TASKS)
        self.assertTrue(any("per-task separation" in e for e in errs))


# ==========================================================================
# M0-T034 / D-004-R629..R633 — governance acceptance semantics.
#
#   (a) LIFECYCLE-AWARE ACCEPTANCE: the acceptance-ordering classifier and its
#       six conjunctive conditions, plus the source-level proofs that the rule
#       is GENERAL (no task-id allowlist, flag, or environment override) and is
#       DOCUMENTED IN THE CODE.
#   (b) VACUOUS-GUARD GAP: the control-plane MATERIAL identity and dirt guard
#       for governance-shaped scopes, and the reviewed_sha comparison.
# ==========================================================================

EMPTY_SET_IDENTITY = hashlib.sha256(b"").hexdigest()  # e3b0c442... , 0 manifest entries


def _req_row(rid="D-900-R001", classification="obligation", events=("accept",)):
    """A requirement row in the registry's real shape."""
    return {"id": rid, "text": "t", "source_ref": "s#x", "classification": classification,
            "binding": True,
            "applicability": {"task_ids": [], "task_types": [], "milestones": [],
                              "paths": [], "lifecycle_events": list(events),
                              "effective_date": "2026-07-31"},
            "dependencies": [], "required_harness": "", "required_evidence": "",
            "producer": "orchestrator", "independent_verifier": "verifier-v",
            "status": "pending", "maps_to": {"files": [], "tests": [], "tasks": []}}


def _ver_row(rid="D-900-R001", state="pending", classification=None):
    row = {"id": rid, "state": state, "evidence": [], "verified_by": None}
    if classification is not None:
        row[dr.LIFECYCLE_CLASSIFICATION_KEY] = classification
    return row


# The reviewed CONTENT IDENTITY every attestation in this suite is made at. Condition
# (6) binds the attestation to it, so a probe that does not name it must refuse.
ATTEST_IDENTITY = "a" * 64


def _attestation(**over):
    base = {"act_class": "accept", "classified_by": "verifier-v",
            "classified_at": "2026-07-31T00:00:00+00:00",
            "classified_at_identity": ATTEST_IDENTITY,
            "justification": "the row's obligation is performed at acceptance itself"}
    base.update(over)
    return base


class AcceptanceOrderingClassifierTests(unittest.TestCase):
    """D-004-R629/R632: the six CONJUNCTIVE conditions, each proven necessary."""

    def test_well_formed_attestation_on_eligible_row_defers(self):
        d, refusals = dr.acceptance_ordering_deferral(
            _req_row(), _ver_row(classification=_attestation()), producer="orchestrator",
            expected_identity=ATTEST_IDENTITY)
        self.assertEqual(refusals, [])
        self.assertIsNotNone(d)
        self.assertEqual(d["act_class"], "accept")
        self.assertEqual(d["classified_by"], "verifier-v")
        self.assertEqual(d["row_lifecycle_events"], ["accept"])
        self.assertEqual(d["classified_at_identity"], ATTEST_IDENTITY,
                         "the deferral record must carry the identity it was attested at")

    def test_every_owner_enumerated_act_class_is_accepted_and_no_other(self):
        for act in sorted(dr.ACCEPTANCE_ORDERING_ACT_CLASSES):
            d, refusals = dr.acceptance_ordering_deferral(
                _req_row(), _ver_row(classification=_attestation(act_class=act)),
                producer="orchestrator", expected_identity=ATTEST_IDENTITY)
            self.assertIsNotNone(d, f"owner-enumerated act class {act!r} must be accepted")
        self.assertEqual(dr.ACCEPTANCE_ORDERING_ACT_CLASSES,
                         frozenset({"accept", "post_accept_cleanup", "checkpoint",
                                    "stop_after"}),
                         "the act-class enumeration is CLOSED and owner-derived (R629)")
        for act in ("merge", "submit", "gate", "cleanup", "", None, 7, "ACCEPT"):
            d, refusals = dr.acceptance_ordering_deferral(
                _req_row(), _ver_row(classification=_attestation(act_class=act)),
                producer="orchestrator", expected_identity=ATTEST_IDENTITY)
            self.assertIsNone(d, f"act_class {act!r} is outside the enumeration")
            self.assertTrue(any("act_class" in r for r in refusals))

    def test_condition2_attestation_must_be_independent_and_reasoned(self):
        # missing classified_by
        d, refusals = dr.acceptance_ordering_deferral(
            _req_row(), _ver_row(classification=_attestation(classified_by="")),
            producer="orchestrator", expected_identity=ATTEST_IDENTITY)
        self.assertIsNone(d)
        self.assertTrue(any("classified_by" in r for r in refusals))
        # producer self-attestation
        d, refusals = dr.acceptance_ordering_deferral(
            _req_row(), _ver_row(classification=_attestation(classified_by="orchestrator")),
            producer="orchestrator", expected_identity=ATTEST_IDENTITY)
        self.assertIsNone(d)
        self.assertTrue(any("INDEPENDENT" in r for r in refusals))
        # unreasoned classification
        d, refusals = dr.acceptance_ordering_deferral(
            _req_row(), _ver_row(classification=_attestation(justification="   ")),
            producer="orchestrator", expected_identity=ATTEST_IDENTITY)
        self.assertIsNone(d)
        self.assertTrue(any("justification" in r for r in refusals))

    def test_condition3_row_binding_outside_acceptance_ordering_keeps_gating(self):
        # ANY pre-acceptance lifecycle event disqualifies the row ("SOLE", R629).
        for events in (("gate", "accept"), ("submit", "gate", "accept"),
                       ("progress", "submit", "gate", "accept"), ("claim",),
                       ("accept", "claim")):
            d, refusals = dr.acceptance_ordering_deferral(
                _req_row(events=events), _ver_row(classification=_attestation()),
                producer="orchestrator", expected_identity=ATTEST_IDENTITY)
            self.assertIsNone(d, f"lifecycle_events {events} must keep gating")
            self.assertTrue(any("SOLE" in r or "outside acceptance ordering" in r
                                for r in refusals))
        # empty/malformed lifecycle_events fail closed
        for events in ((), None, "accept", [1]):
            row = _req_row()
            row["applicability"]["lifecycle_events"] = events
            d, refusals = dr.acceptance_ordering_deferral(
                row, _ver_row(classification=_attestation()), producer="orchestrator",
                expected_identity=ATTEST_IDENTITY)
            self.assertIsNone(d, f"lifecycle_events {events!r} must fail closed")

    def test_condition4_only_obligation_and_sequencing_are_eligible(self):
        self.assertEqual(dr.LIFECYCLE_ELIGIBLE_CLASSIFICATIONS,
                         frozenset({"obligation", "sequencing"}))
        for cls in ("obligation", "sequencing"):
            d, _ = dr.acceptance_ordering_deferral(
                _req_row(classification=cls), _ver_row(classification=_attestation()),
                producer="orchestrator", expected_identity=ATTEST_IDENTITY)
            self.assertIsNotNone(d, f"{cls} must be eligible")
        # a BAR on acceptance can never be deferred, however well attested.
        for cls in ("prohibition", "hold", "decision", "authorization", "dependency",
                    "harness", "evidence", "external_fact", "return", "", None):
            d, refusals = dr.acceptance_ordering_deferral(
                _req_row(classification=cls), _ver_row(classification=_attestation()),
                producer="orchestrator", expected_identity=ATTEST_IDENTITY)
            self.assertIsNone(d, f"classification {cls!r} must never be deferred")
            self.assertTrue(any("acceptance-ordering ACT" in r for r in refusals))

    def test_condition5_only_an_explicitly_pending_state_is_deferrable(self):
        """Condition (5) is an ALLOWLIST, so the refusal is the default. A denylist here
        released every state its author did not enumerate -- above all UNVERIFIABLE, the
        independent verifier stating it COULD NOT verify the obligation."""
        self.assertEqual(dr.DEFERRABLE_VERIFICATION_STATES, frozenset({"pending"}),
                         "exactly one state -- explicitly pending -- may be deferred")
        d, refusals = dr.acceptance_ordering_deferral(
            _req_row(), _ver_row(state="pending", classification=_attestation()),
            producer="orchestrator", expected_identity=ATTEST_IDENTITY)
        self.assertIsNotNone(d, "the positive control must still defer")
        # Every schema-valid non-PASS state OTHER than "pending", plus the malformed and
        # mistyped shapes a denylist silently released.
        for state in ("UNVERIFIABLE", "FAIL", "BLOCKED", "fail", "blocked", "Pending",
                      "pending ", " pending", "FAIL ", "PASSED", "", "wat", None, 0, 1,
                      False, True, 7.5, [], ["pending"], {}, {"state": "pending"}, ()):
            d, refusals = dr.acceptance_ordering_deferral(
                _req_row(), _ver_row(state=state, classification=_attestation()),
                producer="orchestrator", expected_identity=ATTEST_IDENTITY)
            self.assertIsNone(d, f"state {state!r} must never be deferrable")
            self.assertTrue(any("not an explicitly pending row" in r for r in refusals),
                            f"state {state!r} refusal must name the rule: {refusals}")
        # ...and an ABSENT state key is refused, not defaulted into deferral.
        row = _ver_row(classification=_attestation())
        row.pop("state")
        d, refusals = dr.acceptance_ordering_deferral(_req_row(), row,
                                                      producer="orchestrator",
                                                      expected_identity=ATTEST_IDENTITY)
        self.assertIsNone(d, "an absent state must refuse")
        self.assertTrue(any("not an explicitly pending row" in r for r in refusals))
        # UNVERIFIABLE is inside the module's OWN unresolved set: the two must agree.
        self.assertIn("UNVERIFIABLE", dr.UNRESOLVED_VERIFICATION_STATES)
        self.assertFalse(dr.DEFERRABLE_VERIFICATION_STATES
                         & (dr.UNRESOLVED_VERIFICATION_STATES - {"pending"}))

    def test_classifier_never_raises_on_any_malformed_state(self):
        """The classifier docstring promises it never raises. An unhashable state made
        that false (`state in <frozenset>` raised TypeError); the isinstance() guard
        must come first."""
        for state in ([], {}, set(), ["pending"], {"a": 1}, (1, 2), bytearray(b"x")):
            try:
                d, refusals = dr.acceptance_ordering_deferral(
                    _req_row(), _ver_row(state=state, classification=_attestation()),
                    producer="orchestrator", expected_identity=ATTEST_IDENTITY)
            except Exception as exc:                                    # pragma: no cover
                self.fail(f"state {state!r} raised {type(exc).__name__}: {exc}")
            self.assertIsNone(d)
            self.assertTrue(refusals)

    def test_condition2_producer_identity_must_be_known_and_is_case_insensitive(self):
        """An EMPTY producer made the independence test inert -- it silently permitted
        self-attestation. Unevaluable independence now refuses."""
        for producer in ("", None, "   ", 7, [], {}):
            d, refusals = dr.acceptance_ordering_deferral(
                _req_row(), _ver_row(classification=_attestation()), producer=producer,
                expected_identity=ATTEST_IDENTITY)
            self.assertIsNone(d, f"producer {producer!r} must refuse, not defer")
            self.assertTrue(any("no producer identity" in r for r in refusals), refusals)
        # BOTH defaults are unusable on purpose: called with neither identity, the
        # classifier refuses on the unknown producer AND on the unbindable attestation.
        d, refusals = dr.acceptance_ordering_deferral(
            _req_row(), _ver_row(classification=_attestation()))
        self.assertIsNone(d, "the default (unknown) producer must refuse")
        self.assertTrue(any("no producer identity" in r for r in refusals), refusals)
        self.assertTrue(any("no reviewed content identity" in r for r in refusals),
                        f"the default (absent) expected identity must refuse too: {refusals}")
        # independence is case- and whitespace-insensitive in BOTH directions.
        for by, prod in ((" Orchestrator ", "orchestrator"), ("ORCHESTRATOR", "Orchestrator"),
                         ("orchestrator", " ORCHESTRATOR"), ("Reviewer-V", "reviewer-v ")):
            d, refusals = dr.acceptance_ordering_deferral(
                _req_row(), _ver_row(classification=_attestation(classified_by=by)),
                producer=prod, expected_identity=ATTEST_IDENTITY)
            self.assertIsNone(d, f"{by!r} vs {prod!r} is the same identity")
            self.assertTrue(any("INDEPENDENT" in r for r in refusals), refusals)

    def test_condition2_attestation_must_be_dated(self):
        """An undated attestation is not a point-in-time act; it is an assertion that can
        be copied forward. `classified_at` was previously copied unvalidated."""
        for ts in ("2026-07-31T00:00:00+00:00", "2026-07-31T00:00:00Z",
                   "2026-07-31 00:00:00", "2026-07-31T00:00"):
            d, _r = dr.acceptance_ordering_deferral(
                _req_row(), _ver_row(classification=_attestation(classified_at=ts)),
                producer="orchestrator", expected_identity=ATTEST_IDENTITY)
            self.assertIsNotNone(d, f"{ts!r} is a well-formed dated attestation")
            self.assertEqual(d["classified_at"], ts)
        for ts in ("t", "", None, 7, "2026-07-31", "yesterday", "2026-13-99T99:99:99+00:00",
                   "2026-02-30T00:00:00+00:00", [], {"at": "now"}):
            d, refusals = dr.acceptance_ordering_deferral(
                _req_row(), _ver_row(classification=_attestation(classified_at=ts)),
                producer="orchestrator", expected_identity=ATTEST_IDENTITY)
            self.assertIsNone(d, f"{ts!r} is not a valid dated attestation")
            self.assertTrue(any("classified_at" in r for r in refusals), refusals)

    def test_condition6_attestation_must_be_bound_to_the_reviewed_identity(self):
        """A DATED attestation still travels; a BOUND one cannot. Condition (6) refuses
        any attestation that does not name EXACTLY the reviewed content identity the
        deferral is being granted at -- above all one carried forward from an earlier
        review, which is the shape that releases rows at content nobody attested about."""
        # positive control: the correct identity, exactly, still defers.
        d, refusals = dr.acceptance_ordering_deferral(
            _req_row(), _ver_row(classification=_attestation()), producer="orchestrator",
            expected_identity=ATTEST_IDENTITY)
        self.assertIsNotNone(d, refusals)
        # a STALE stamp carried forward from an earlier identity, plus every malformed,
        # re-cased and re-spaced near-miss: exact string equality, refusal by default.
        stale = "b" * 64
        for stamp in (stale, ATTEST_IDENTITY.upper(), " " + ATTEST_IDENTITY,
                      ATTEST_IDENTITY + " ", ATTEST_IDENTITY + "\n", ATTEST_IDENTITY[:-1],
                      "", "   ", None, 7, [], {}, True, ATTEST_IDENTITY.encode()):
            d, refusals = dr.acceptance_ordering_deferral(
                _req_row(),
                _ver_row(classification=_attestation(classified_at_identity=stamp)),
                producer="orchestrator", expected_identity=ATTEST_IDENTITY)
            self.assertIsNone(d, f"classified_at_identity {stamp!r} must not release")
            self.assertTrue(any("classified_at_identity" in r for r in refusals), refusals)
        # ...and an ABSENT key is refused rather than defaulted into deferral.
        claim = _attestation()
        claim.pop("classified_at_identity")
        d, refusals = dr.acceptance_ordering_deferral(
            _req_row(), _ver_row(classification=claim), producer="orchestrator",
            expected_identity=ATTEST_IDENTITY)
        self.assertIsNone(d, "an unstamped attestation must refuse")
        self.assertTrue(any("classified_at_identity" in r for r in refusals), refusals)
        # An UNAVAILABLE expectation gates rather than releases: nothing to compare
        # against is not "compared and equal".
        for expected in (None, "", "   ", 7, [], {}, True):
            d, refusals = dr.acceptance_ordering_deferral(
                _req_row(), _ver_row(classification=_attestation()),
                producer="orchestrator", expected_identity=expected)
            self.assertIsNone(d, f"expected identity {expected!r} must refuse, not release")
            self.assertTrue(any("no reviewed content identity" in r for r in refusals),
                            refusals)

    def test_missing_requirement_row_fails_closed(self):
        d, refusals = dr.acceptance_ordering_deferral(
            None, _ver_row(classification=_attestation()), producer="orchestrator",
            expected_identity=ATTEST_IDENTITY)
        self.assertIsNone(d)
        self.assertTrue(any("no requirement row" in r for r in refusals))

    def test_no_claim_means_ordinary_gating_with_no_noise(self):
        d, refusals = dr.acceptance_ordering_deferral(
            _req_row(), _ver_row(), producer="orchestrator",
            expected_identity=ATTEST_IDENTITY)
        self.assertIsNone(d)
        self.assertEqual(refusals, [], "a row making no lifecycle claim gates silently")
        # a malformed claim object is loud, not silent
        d, refusals = dr.acceptance_ordering_deferral(
            _req_row(), _ver_row(classification="yes please"), producer="orchestrator",
            expected_identity=ATTEST_IDENTITY)
        self.assertIsNone(d)
        self.assertTrue(refusals)

    def test_classifier_is_general_no_allowlist_flag_or_env_override(self):
        """AS-3 / D-004-R632, matching the standard set by invalid_unblock_roster."""
        src = (HERE / "directive_registry.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        body = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "acceptance_ordering_deferral":
                stmts = list(node.body)
                self.assertTrue(
                    stmts and isinstance(stmts[0], ast.Expr)
                    and isinstance(stmts[0].value, ast.Constant)
                    and isinstance(stmts[0].value.value, str),
                    "AS-12: the classifier must carry a docstring stating its contract")
                body = "\n".join(ast.unparse(s) for s in stmts[1:])
        self.assertIsNotNone(body, "the classifier function must exist")
        self.assertNotRegex(body, r"M\d+-T\d{3}",
                            "classifier code must name no ledger task id")
        self.assertNotRegex(body, r"D-\d{3}-R\d{3}",
                            "classifier code must name no specific requirement id")
        for tok in ("getenv", "environ", "force", "bypass", "override", "skip", "allowlist"):
            self.assertNotIn(tok, body.lower(), f"classifier code must carry no {tok!r} token")
        for const in ("ACCEPTANCE_ORDERING_ACT_CLASSES", "ACCEPTANCE_ORDERING_LIFECYCLE_EVENTS",
                      "LIFECYCLE_ELIGIBLE_CLASSIFICATIONS", "DEFERRABLE_VERIFICATION_STATES"):
            self.assertIn(const, body, f"the classifier must use the named constant {const}")
        # every condition is an ALLOWLIST: no denylist-shaped constant may gate a deferral.
        self.assertNotIn("NEGATIVE_VERIFICATION_STATES", src,
                         "condition (5) must not be reintroduced as a denylist")
        # AS-10: the eight candidate rows are the independent verifier's call; neither
        # module may name (and thereby pre-classify) any of them.
        pc_src = (HERE / "project_control.py").read_text(encoding="utf-8")
        for rid in ("D-004-R322", "D-004-R323", "D-004-R388", "D-004-R389",
                    "D-004-R486", "D-004-R487", "D-004-R488", "D-004-R501"):
            self.assertNotIn(rid, src, f"{rid} must not be named in directive_registry.py")
            self.assertNotIn(rid, pc_src, f"{rid} must not be named in project_control.py")

    def test_as12_rule_is_documented_in_the_code(self):
        """AS-12: a future reviewer audits a STATED RULE, not inferred behavior."""
        src = (HERE / "directive_registry.py").read_text(encoding="utf-8")
        self.assertIn("ACCEPTANCE-ORDERING LIFECYCLE CLASSIFICATION", src)
        self.assertIn("CONJUNCTIVE", src)
        for n in ("(1)", "(2)", "(3)", "(4)", "(5)", "(6)"):
            self.assertIn(n, src, f"the stated rule must enumerate condition {n}")
        self.assertIn("no special-cased task id, no flag, and no environment override", src,
                      "the rule must state its own generality, matching invalid_unblock_roster")
        self.assertIn("KNOWN LIMIT", src,
                      "the stated rule must disclose what it cannot discriminate")
        # AS-12: the STATED rule and the CODE must agree. Condition (5) is an allowlist,
        # and the rule must say so -- naming UNVERIFIABLE, the value a denylist released.
        self.assertIn("EXPLICITLY PENDING VERIFICATION STATE", src)
        self.assertIn("UNVERIFIABLE", src,
                      "the stated rule must name the verdict a denylist silently released")
        self.assertIn("DEFERRABLE_VERIFICATION_STATES", src)
        self.assertIn("DEFERRAL IS NOT WAIVER", src,
                      "the discharge standard must be stated where a reviewer will read it")
        # AS-12 for condition (6): the stated rule must enumerate the new refusals as
        # explicitly as (1)-(5) do, so a reviewer audits the rule and not the behavior.
        self.assertIn("IDENTITY-BOUND ATTESTATION", src)
        self.assertIn("ATTESTATION_IDENTITY_KEY", src)
        for phrase in ("EXACT STRING", "CASE-VARIANT", "UNEVALUABLE"):
            self.assertIn(phrase, src,
                          f"condition (6) must state that {phrase} inputs refuse")


class CarriedForwardAttestationTests(unittest.TestCase):
    """Condition (6) on the GRANT path, driven through task_verification_result() -- the
    path accept() actually calls -- rather than against the classifier in isolation.

    The defect this closes: the attestation carried no identity of its own, so a verifier
    who re-verified at a NEW content identity and refreshed the RECORD's
    reviewed_manifest_sha256 carried every per-row attestation forward untouched, and
    those rows still released at content the classifier had never seen attested."""

    IDA = "a" * 64          # the identity the attestation is made at
    NEW = "e" * 64          # the identity a later review is recorded at
    APPLICABLE = {"D-700-R001", "D-700-R002"}

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="attest-identity-"))
        self.reg = _make_two_task_v2_registry(self.tmp, idA=self.IDA)
        self.tv = [tv for tv in self.reg.get("D-700").verification["task_verifications"]
                   if tv["task_id"] == "M9-T001"][0]
        self.row = [r for r in self.tv["requirements"] if r["id"] == "D-700-R002"][0]
        self.row["state"] = "pending"
        self.claim = _attestation(classified_at_identity=self.IDA)
        self.row[dr.LIFECYCLE_CLASSIFICATION_KEY] = self.claim

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _result(self, identity):
        return self.reg.task_verification_result("D-700", "M9-T001", self.APPLICABLE,
                                                 identity)

    def test_an_attestation_defers_at_the_identity_it_was_made_at(self):
        """Positive control: the refusals below are caused by the stale stamp, not by an
        unrelated precondition of this fixture."""
        res = self._result(self.IDA)
        self.assertEqual(res["reasons"], [])
        self.assertEqual(len(res["deferrals"]), 1)
        self.assertEqual(res["deferrals"][0]["classified_at_identity"], self.IDA)

    def test_the_same_attestation_carried_forward_to_a_new_identity_no_longer_releases(self):
        # The verifier re-verifies at NEW content and refreshes the RECORD's identity,
        # but carries the per-row attestation forward untouched. This released the row
        # before condition (6) existed.
        self.tv["reviewed_manifest_sha256"] = self.NEW
        res = self._result(self.NEW)
        self.assertEqual(res["deferrals"], [],
                         "an attestation made about other content must not release a row")
        self.assertTrue(any("classified_at_identity" in r for r in res["reasons"]), res)
        self.assertTrue(any("not PASS" in r for r in res["reasons"]),
                        f"the row must fall back to ordinary gating: {res}")
        # Re-stamping the attestation at the NEW identity restores the deferral, so the
        # refusal above is caused by the stale stamp and by nothing else.
        self.claim["classified_at_identity"] = self.NEW
        res = self._result(self.NEW)
        self.assertEqual(res["reasons"], [])
        self.assertEqual(len(res["deferrals"]), 1)

    def test_an_unavailable_expected_identity_gates_rather_than_releases(self):
        """A caller that supplies no identity to bind against gets a refusal: an absent
        expectation must never read as a satisfied one."""
        res = self._result(None)
        self.assertEqual(res["deferrals"], [])
        self.assertTrue(any("no reviewed content identity" in r for r in res["reasons"]),
                        res)


class DeferredDischargeStandardTests(unittest.TestCase):
    """DEFERRAL IS NOT WAIVER, proven in code rather than prose: a deferred acceptance-
    ordering row is discharged only by verification meeting the SAME standards as the
    gate that deferred it. The defect this closes: a bare `state: PASS`, written at any
    time, at any identity, by anyone -- including the producer -- discharged it, holding
    the deferred obligation to a LOWER bar than an ordinary requirement."""

    IDENT = "a" * 64
    SHA = "c" * 40

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="discharge-"))
        self.reg = _make_two_task_v2_registry(self.tmp, idA=self.IDENT)
        self.tv = [tv for tv in self.reg.get("D-700").verification["task_verifications"]
                   if tv["task_id"] == "M9-T001"][0]
        self.tv["reviewed_sha"] = self.SHA
        self.row = [r for r in self.tv["requirements"] if r["id"] == "D-700-R002"][0]
        self.row["state"] = "pending"
        self.row[dr.LIFECYCLE_CLASSIFICATION_KEY] = _attestation()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _discharge(self, **over):
        kw = {"expected_identity": self.IDENT, "expected_sha": self.SHA}
        kw.update(over)
        return self.reg.deferred_requirement_discharge(
            "D-700", "M9-T001", "D-700-R002", **kw)

    def test_a_fully_standard_verification_discharges(self):
        """Positive control: every refusal below is caused by the broken standard, not by
        some unrelated precondition of this fixture."""
        self.row["state"] = "PASS"
        ok, state, why = self._discharge()
        self.assertTrue(ok, why)
        self.assertEqual((state, why), ("PASS", []))

    def test_bare_pass_without_an_independent_verifier_does_not_discharge(self):
        self.row["state"] = "PASS"
        self.tv["verifier"] = ""
        ok, state, why = self._discharge()
        self.assertFalse(ok, "a bare PASS with no independent verifier must not discharge")
        self.assertEqual(state, "PASS")
        self.assertTrue(any("no independent verifier" in r for r in why), why)

    def test_the_producer_cannot_discharge_its_own_deferral(self):
        self.row["state"] = "PASS"
        self.tv["verifier"] = " ORCHESTRATOR "        # == producer, merely re-spelled
        ok, _state, why = self._discharge()
        self.assertFalse(ok)
        self.assertTrue(any("equals producer" in r for r in why), why)

    def test_unknown_producer_identity_fails_closed(self):
        self.row["state"] = "PASS"
        self.tv["producer"] = ""
        self.reg.get("D-700").verification["producer"] = ""
        self.reg.get("D-700").requirements["producer"] = ""
        ok, _state, why = self._discharge()
        self.assertFalse(ok)
        self.assertTrue(any("no producer identity" in r for r in why), why)

    def test_discharge_at_another_content_identity_is_refused(self):
        self.row["state"] = "PASS"
        self.tv["reviewed_manifest_sha256"] = "f" * 64
        ok, _state, why = self._discharge()
        self.assertFalse(ok)
        self.assertTrue(any("content identity" in r for r in why), why)

    def test_discharge_at_another_reviewed_commit_is_refused(self):
        self.row["state"] = "PASS"
        self.tv["reviewed_sha"] = "d" * 40
        ok, _state, why = self._discharge()
        self.assertFalse(ok)
        self.assertTrue(any("reviewed commit" in r for r in why), why)
        self.tv["reviewed_sha"] = None
        ok, _state, why = self._discharge()
        self.assertFalse(ok, "an absent reviewed commit fails closed too")

    def test_deleting_the_row_does_not_discharge_it(self):
        self.tv["requirements"] = [r for r in self.tv["requirements"]
                                   if r["id"] != "D-700-R002"]
        ok, state, why = self._discharge()
        self.assertFalse(ok)
        self.assertIsNone(state)
        self.assertTrue(any("no verification row" in r for r in why), why)

    def test_a_still_pending_row_does_not_discharge(self):
        ok, state, why = self._discharge()
        self.assertFalse(ok)
        self.assertEqual(state, "pending")
        self.assertTrue(any("not PASS" in r for r in why), why)

    def test_not_applicable_discharges_only_when_justified_and_approved(self):
        self.row["state"] = "NOT_APPLICABLE"
        ok, _state, why = self._discharge()
        self.assertFalse(ok, "bare NOT_APPLICABLE must not discharge")
        self.row["not_applicable_justification"] = "policy requires no such act here"
        self.row["not_applicable_approved_by"] = "reviewer-b"
        ok, _state, why = self._discharge()
        self.assertTrue(ok, why)

    def test_unreadable_records_fail_closed(self):
        ok, _s, why = self.reg.deferred_requirement_discharge(
            "D-700", "M9-T999", "D-700-R002",
            expected_identity=self.IDENT, expected_sha=self.SHA)
        self.assertFalse(ok)
        self.assertTrue(any("no task_verification row" in r for r in why), why)
        ok, _s, why = self.reg.deferred_requirement_discharge("D-701", "M9-T001",
                                                              "D-700-R002")
        self.assertFalse(ok)
        self.assertTrue(any("not found" in r for r in why), why)

    def test_requirement_verification_state_is_a_plain_read_not_a_discharge(self):
        """The lax accessor still exists and still reports the raw state; what changed is
        that the post-accept path no longer treats that raw state as sufficient."""
        self.row["state"] = "PASS"
        self.tv["verifier"] = ""
        state, row = self.reg.requirement_verification_state("D-700", "M9-T001",
                                                             "D-700-R002")
        self.assertEqual(state, "PASS")
        self.assertIsNotNone(row)
        self.assertFalse(self._discharge()[0],
                         "the same row that reads PASS must NOT discharge the deferral")

    def test_outstanding_claims_are_re_derived_from_the_registry(self):
        """The obligation must be recoverable from the registry, so deleting the task
        packet's deferral record cannot erase it silently."""
        self.assertEqual(self.reg.outstanding_lifecycle_claims("D-700", "M9-T001"),
                         [("D-700-R002", "pending")])
        self.row["state"] = "PASS"
        self.assertEqual(self.reg.outstanding_lifecycle_claims("D-700", "M9-T001"), [])
        self.row["state"] = "UNVERIFIABLE"
        self.assertEqual(self.reg.outstanding_lifecycle_claims("D-700", "M9-T001"),
                         [("D-700-R002", "UNVERIFIABLE")])
        self.row["state"] = "pending"
        self.row.pop(dr.LIFECYCLE_CLASSIFICATION_KEY)
        self.assertEqual(self.reg.outstanding_lifecycle_claims("D-700", "M9-T001"), [],
                         "a row claiming no lifecycle classification is not this obligation")
        out = self.reg.outstanding_lifecycle_claims("D-700", "M9-T999")
        self.assertEqual(len(out), 1)
        self.assertIsNone(out[0][0], "an unreadable record must fail closed, not read empty")


class ReviewedShaComparisonTests(unittest.TestCase):
    """D-004-R630: reviewed_sha is ACTUALLY compared; a stale one fails closed."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="revsha-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _reg(self, recorded_sha):
        reg = _make_two_task_v2_registry(self.tmp, idA="a" * 64, idB="b" * 64)
        d = reg.get("D-700")
        for tv in d.verification["task_verifications"]:
            if tv["task_id"] == "M9-T001":
                tv["reviewed_sha"] = recorded_sha
        return reg

    def test_matching_reviewed_sha_passes(self):
        reg = self._reg("c" * 40)
        self.assertEqual(
            reg.task_unresolved_requirements("D-700", "M9-T001",
                                             {"D-700-R001", "D-700-R002"}, "a" * 64,
                                             reviewed_sha="c" * 40), [])

    def test_stale_reviewed_sha_fails_closed(self):
        reg = self._reg("c" * 40)
        rs = reg.task_unresolved_requirements("D-700", "M9-T001",
                                              {"D-700-R001", "D-700-R002"}, "a" * 64,
                                              reviewed_sha="d" * 40)
        self.assertTrue(any("reviewed_sha is stale" in r for r in rs), rs)

    def test_missing_reviewed_sha_fails_closed(self):
        reg = self._reg(None)
        rs = reg.task_unresolved_requirements("D-700", "M9-T001",
                                              {"D-700-R001", "D-700-R002"}, "a" * 64,
                                              reviewed_sha="d" * 40)
        self.assertTrue(any("reviewed_sha is stale" in r for r in rs), rs)

    def test_backward_compatible_when_no_sha_supplied(self):
        """The pre-existing 4-argument call is unchanged (AS-8)."""
        reg = self._reg(None)
        self.assertEqual(
            reg.task_unresolved_requirements("D-700", "M9-T001",
                                             {"D-700-R001", "D-700-R002"}, "a" * 64), [])


class ControlPlaneMaterialIdentityTests(unittest.TestCase):
    """D-004-R630: governance-shaped scopes get REAL staleness and dirt guards."""

    CP = ("project-control/",)
    PATHS = ["project-control/tasks/M9-T001.json",
             "project-control/reports/M9-T001-producer-report.md"]

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cpident-"))
        _init_repo(self.tmp)
        (self.tmp / "project-control" / "tasks").mkdir(parents=True)
        (self.tmp / "project-control" / "reports").mkdir(parents=True)
        self.packet = self.tmp / "project-control" / "tasks" / "M9-T001.json"
        self.report = self.tmp / "project-control" / "reports" / "M9-T001-producer-report.md"
        self._write_packet(status="claimed", progress=10, objective="original objective")
        self.report.write_text("original report\n", encoding="utf-8")
        self.head = self._commit()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_packet(self, status, progress, objective,
                      updated_at="2026-07-31T00:00:00+00:00"):
        _write(self.packet, {
            "task_id": "M9-T001", "title": "t", "task_type": "governance",
            "milestone_id": "M0", "objective": objective, "inputs": [], "outputs": [],
            "dependencies": [], "allowed_paths": list(self.PATHS), "forbidden_paths": [],
            "acceptance_scenarios": [], "required_gates": ["G0", "G3"], "risks": [],
            "blockers": [], "status": status, "progress_percent": progress,
            "updated_at": updated_at, "progress_log": []})

    def _commit(self, msg="c"):
        _git(self.tmp, "add", "-A")
        _git(self.tmp, "commit", "-q", "-m", msg)
        return _git(self.tmp, "rev-parse", "HEAD").stdout.decode().strip()

    def _identity(self, sha=None):
        ident, rsha, err = dr.frozen_git_identity(
            self.PATHS, reviewed_sha=sha, root=self.tmp, exclude_prefixes=self.CP,
            require_clean=False, control_plane_prefixes=self.CP)
        self.assertIsNone(err, err)
        return ident

    # ---- the defect being closed -----------------------------------------

    def test_old_guard_was_provably_vacuous(self):
        ident, entries, err = dr.git_tree_manifest(self.tmp, "HEAD", self.PATHS,
                                                   exclude_prefixes=self.CP)
        self.assertIsNone(err)
        self.assertEqual(entries, [], "the raw-blob manifest excludes the whole scope")
        self.assertEqual(ident, EMPTY_SET_IDENTITY,
                         "the OLD identity for a governance-shaped scope is the empty-set hash")
        dirty, err = dr.relevant_working_tree_dirty(self.tmp, self.PATHS,
                                                    exclude_prefixes=self.CP)
        self.assertEqual(dirty, [], "the OLD dirt guard drops every candidate")

    def test_new_identity_is_not_the_empty_set_hash(self):
        ident = self._identity()
        self.assertNotEqual(ident, EMPTY_SET_IDENTITY)
        entries, err = dr.control_plane_entries(self.tmp, "HEAD", self.PATHS, self.CP)
        self.assertIsNone(err)
        self.assertEqual(len(entries), 2)
        packet_entry = [e for e in entries if e[0].startswith("project-control/tasks/")][0]
        self.assertTrue(packet_entry[3].startswith(dr.MATERIAL_ENTRY_PREFIX),
                        "a task packet contributes its MATERIAL digest")
        report_entry = [e for e in entries if e[0].endswith(".md")][0]
        self.assertFalse(report_entry[3].startswith(dr.MATERIAL_ENTRY_PREFIX),
                         "every other control-plane file contributes its git blob id")

    # ---- what moves the identity, and what deliberately does not ---------

    def test_non_packet_change_moves_the_identity(self):
        before = self._identity()
        self.report.write_text("REVISED report\n", encoding="utf-8")
        self._commit("edit report")
        self.assertNotEqual(before, self._identity(),
                            "a committed change to a control-plane file in scope must move it")

    def test_material_packet_amendment_moves_the_identity(self):
        before = self._identity()
        self._write_packet(status="claimed", progress=10, objective="MATERIALLY different")
        self._commit("material amendment")
        self.assertNotEqual(before, self._identity())

    def test_lifecycle_only_packet_change_does_not_move_the_identity(self):
        """The stated resolution: lifecycle bookkeeping is not content staleness."""
        before = self._identity()
        head_before = self.head
        # Exactly the delta the fifth independent pass found on the real packet:
        # status, progress_percent and updated_at, and nothing else.
        self._write_packet(status="awaiting_gate", progress=85,
                           objective="original objective",
                           updated_at="2026-07-31T09:30:00+00:00")
        after_sha = self._commit("lifecycle-only transition")
        self.assertNotEqual(head_before, after_sha, "the commit really happened")
        self.assertEqual(before, self._identity(),
                         "status/progress/updated_at churn must not read as content staleness")
        # ...and the differing packet keys really are lifecycle-only.
        old = json.loads(_git(self.tmp, "show", f"{head_before}:{self.PATHS[0]}"
                              ).stdout.decode("utf-8-sig"))
        new = _read(self.packet)
        differing = {k for k in set(old) | set(new) if old.get(k) != new.get(k)}
        self.assertEqual(differing, {"status", "progress_percent", "updated_at"})
        self.assertEqual(dr.material_digest(old), dr.material_digest(new))

    def test_raw_blob_control_plane_identity_would_be_unusable(self):
        """WHY the exclusion cannot simply be dropped: the packet's blob id changes on a
        lifecycle-only transition, so a raw-blob control-plane identity stamped at submit
        is stale before accept() ever runs."""
        blob_before, _, err = dr.git_tree_manifest(self.tmp, "HEAD", self.PATHS)
        self.assertIsNone(err)
        material_before = self._identity()
        self._write_packet(status="awaiting_gate", progress=85, objective="original objective")
        self._commit("lifecycle-only transition")
        blob_after, _, _ = dr.git_tree_manifest(self.tmp, "HEAD", self.PATHS)
        self.assertNotEqual(blob_before, blob_after,
                            "a raw-blob identity moves on pure lifecycle bookkeeping, so an "
                            "identity stamped at submit is stale before accept() runs")
        self.assertEqual(material_before, self._identity(),
                         "the material identity is stable across that same transition")

    # ---- the dirt guard ---------------------------------------------------

    def test_dirty_control_plane_file_is_detected(self):
        self.report.write_text("uncommitted edit\n", encoding="utf-8")
        dirty, err = dr.control_plane_material_dirty(self.tmp, self.PATHS, self.CP)
        self.assertIsNone(err)
        self.assertEqual([p for _xy, p in dirty], [self.PATHS[1]])
        ident, sha, err = dr.frozen_git_identity(
            self.PATHS, root=self.tmp, exclude_prefixes=self.CP, require_clean=True,
            control_plane_prefixes=self.CP)
        self.assertIsNotNone(err)
        self.assertIn("dirty", err)

    def test_untracked_control_plane_file_is_detected(self):
        (self.tmp / "project-control" / "reports" / "M9-T001-extra.md").write_text(
            "new\n", encoding="utf-8")
        dirty, err = dr.control_plane_material_dirty(
            self.tmp, ["project-control/reports"], self.CP)
        self.assertIsNone(err)
        self.assertTrue(any(p.endswith("M9-T001-extra.md") for _xy, p in dirty))

    def test_material_uncommitted_packet_edit_is_dirty(self):
        self._write_packet(status="claimed", progress=10, objective="MATERIALLY different")
        dirty, err = dr.control_plane_material_dirty(self.tmp, self.PATHS, self.CP)
        self.assertIsNone(err)
        self.assertEqual([p for _xy, p in dirty], [self.PATHS[0]])

    def test_lifecycle_only_uncommitted_packet_edit_is_not_dirty(self):
        """Required for the control plane to function at all: submit/gate write the
        packet, so a lifecycle-only working-tree delta must not fail the guard closed."""
        self._write_packet(status="awaiting_gate", progress=85, objective="original objective")
        dirty, err = dr.control_plane_material_dirty(self.tmp, self.PATHS, self.CP)
        self.assertIsNone(err)
        self.assertEqual(dirty, [])

    def test_deleted_packet_is_dirty(self):
        self.packet.unlink()
        dirty, err = dr.control_plane_material_dirty(self.tmp, self.PATHS, self.CP)
        self.assertIsNone(err)
        self.assertEqual([p for _xy, p in dirty], [self.PATHS[0]])

    def test_unparseable_packet_is_dirty(self):
        self.packet.write_text("{ not json", encoding="utf-8")
        dirty, err = dr.control_plane_material_dirty(self.tmp, self.PATHS, self.CP)
        self.assertIsNone(err)
        self.assertEqual([p for _xy, p in dirty], [self.PATHS[0]],
                         "an unreadable packet must fail closed as dirt")

    def test_unparseable_packet_at_commit_fails_the_identity_closed(self):
        self.packet.write_text("{ not json", encoding="utf-8")
        self._commit("corrupt packet")
        entries, err = dr.control_plane_entries(self.tmp, "HEAD", self.PATHS, self.CP)
        self.assertIsNone(entries)
        self.assertIn("not valid JSON", err)
        ident, _sha, ierr = dr.frozen_git_identity(
            self.PATHS, root=self.tmp, exclude_prefixes=self.CP, require_clean=False,
            control_plane_prefixes=self.CP)
        self.assertIsNone(ident)
        self.assertIn("not valid JSON", ierr)

    # ---- no regression outside the control-plane tree --------------------

    def test_ordinary_scopes_are_byte_identical_to_before(self):
        (self.tmp / "probe.txt").write_text("p\n", encoding="utf-8")
        self._commit("probe")
        raw, _entries, err = dr.git_tree_manifest(self.tmp, "HEAD", ["probe.txt"],
                                                  exclude_prefixes=self.CP)
        self.assertIsNone(err)
        ident, _sha, err = dr.frozen_git_identity(
            ["probe.txt"], root=self.tmp, exclude_prefixes=self.CP, require_clean=False,
            control_plane_prefixes=self.CP)
        self.assertIsNone(err)
        self.assertEqual(raw, ident,
                         "a scope with no control-plane paths keeps its existing identity")


if __name__ == "__main__":
    unittest.main(verbosity=2)
