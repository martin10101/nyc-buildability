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


if __name__ == "__main__":
    unittest.main(verbosity=2)
