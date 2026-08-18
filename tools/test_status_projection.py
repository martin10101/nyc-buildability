#!/usr/bin/env python3
"""M0-T069 Unit F tests: deterministic status projection (R061/R062/R063).

Runnable as ``python tools/test_status_projection.py`` or under pytest.
Fixture is a hermetic temp git repo carrying a miniature control plane with
one D-013-style unit task in each interesting lifecycle state.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from tools import status_projection as sp  # noqa: E402

CLI = os.path.join(_HERE, "status_projection.py")

_GIT_ENV = {"GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t.t",
            "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@t.t",
            "GIT_CONFIG_NOSYSTEM": "1"}


def _write(root: str, rel: str, doc) -> str:
    p = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        if isinstance(doc, str):
            fh.write(doc)
        else:
            json.dump(doc, fh, indent=1)
    return p


def _git(root: str, *args: str) -> str:
    env = dict(os.environ)
    env.update(_GIT_ENV)
    out = subprocess.run(["git", *args], cwd=root, env=env, check=True,
                         capture_output=True, text=True)
    return out.stdout.strip()


def build_fixture(root: str) -> None:
    _write(root, "project-control/master_plan.json",
           {"milestones": [{"id": "M0"}]})
    _write(root, "project-control/directives/index.json",
           {"directives": [{"directive_id": "D-013"}]})
    _write(root, "project-control/directives/"
                 "D-013-context-intelligence-pipeline/requirements.json",
           {"requirements": [{"id": "D-013-R001", "text": "t"}]})
    _write(root, "project-control/directives/"
                 "D-013-context-intelligence-pipeline/verification.json",
           {"task_verifications": [
               {"task_id": "M0-T801",
                "applicable_requirement_ids": ["D-013-R001"],
                "reviewed_sha": "b" * 40},
               {"task_id": "M0-T802", "applicable_requirement_ids": [],
                "reviewed_sha": None}]})
    _write(root, "project-control/tasks/M0-T801.json",
           {"task_id": "M0-T801", "title": "Accepted unit", "milestone_id": "M0",
            "status": "accepted", "dependencies": [],
            "producer_agent": "orchestrator",
            "reviewer_agents": ["code-reviewer"],
            "required_gates": ["G0", "G3"],
            "allowed_paths": ["tools/unit801.py",
                              "project-control/reports/M0-T801-x.md"],
            "accepted_by": "orchestrator", "accepted_at": "2026-08-18T00:00:00Z"})
    _write(root, "project-control/tasks/M0-T802.json",
           {"task_id": "M0-T802", "title": "Rework unit", "milestone_id": "M0",
            "status": "rework", "dependencies": ["M0-T801"],
            "producer_agent": "orchestrator", "reviewer_agents": [],
            "required_gates": ["G0"], "allowed_paths": []})
    _write(root, "project-control/gates/M0-T801-G0.json",
           {"task_id": "M0-T801", "gate_id": "G0", "result": "PASS",
            "reviewer": "orchestrator", "reviewed_sha": "a" * 40})
    _write(root, "project-control/gates/M0-T801-G3.json",
           {"task_id": "M0-T801", "gate_id": "G3", "result": "PASS",
            "reviewer": "code-reviewer", "reviewed_sha": "b" * 40})
    _write(root, "project-control/reports/M0-T801-review-PASS.md", "# PASS\n")
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "fixture")


class Case(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        build_fixture(self.root)
        self.addCleanup(self._tmp.cleanup)


class AS5Projection(Case):
    def test_r063_fields_present_per_node(self) -> None:
        proj = sp.build_projection(self.root)
        self.assertEqual([n["task_id"] for n in proj["nodes"]],
                         ["M0-T801", "M0-T802"])
        n = proj["nodes"][0]
        for key in ("task_id", "requirement_ids", "dependency_ids", "roles",
                    "branch", "reviewed_sha", "implementation_files",
                    "evidence_location", "review_decision_digest",
                    "required_gates", "gates", "status",
                    "accepted_or_blocked_reason", "rollback_point"):
            self.assertIn(key, n)
        self.assertEqual(n["requirement_ids"], ["D-013-R001"])
        self.assertEqual(n["reviewed_sha"], "b" * 40)
        self.assertEqual(n["rollback_point"], "a" * 40)  # the G0 contract SHA
        self.assertEqual(n["implementation_files"], ["tools/unit801.py"])
        self.assertEqual(n["review_decision_digest"]["report"],
                         "project-control/reports/M0-T801-review-PASS.md")
        self.assertTrue(n["review_decision_digest"]["sha256"])

    def test_r062_status_mapping(self) -> None:
        proj = sp.build_projection(self.root)
        by_id = {n["task_id"]: n for n in proj["nodes"]}
        self.assertEqual(by_id["M0-T801"]["status"], "accepted")
        self.assertEqual(by_id["M0-T802"]["status"], "corrections required")
        self.assertIn("accepted by orchestrator",
                      by_id["M0-T801"]["accepted_or_blocked_reason"])

    def test_generating_stamps_and_md_from_same_json(self) -> None:
        proj = sp.build_projection(self.root)
        gen = proj["generated_from"]
        self.assertEqual(gen["repo_sha"], _git(self.root, "rev-parse", "HEAD"))
        self.assertEqual(len(gen["task_index_digest"]), 64)
        self.assertEqual(len(gen["directive_index_digest"]), 64)
        md = sp.render_md(proj)
        self.assertIn("M0-T801", md)
        self.assertIn("mermaid", md)
        self.assertIn("M0-T801 --> M0-T802", md)  # mermaid FROM the same JSON
        self.assertIn("never a source of truth", md)

    def test_nullable_branch_never_fabricated(self) -> None:
        proj = sp.build_projection(self.root)
        self.assertIsNone(proj["nodes"][0]["branch"])


class AS6DeterminismFailClosed(Case):
    def test_two_runs_byte_identical(self) -> None:
        from tools.context_pack_io import canon_json_bytes
        a = canon_json_bytes(sp.build_projection(self.root))
        b = canon_json_bytes(sp.build_projection(self.root))
        self.assertEqual(a, b)

    def test_unreadable_packet_fails_closed(self) -> None:
        os.remove(os.path.join(self.root, "project-control", "tasks",
                               "M0-T801.json"))
        with self.assertRaises(sp.ProjectionError) as cm:
            sp.build_projection(self.root)
        self.assertEqual(cm.exception.code, "task_packet_unreadable")

    def test_error_detail_has_no_absolute_path(self) -> None:
        os.remove(os.path.join(self.root, "project-control", "tasks",
                               "M0-T802.json"))
        with self.assertRaises(sp.ProjectionError) as cm:
            sp.build_projection(self.root)
        self.assertNotIn(self.root, cm.exception.detail)

    def test_cli_generate_and_stale_check(self) -> None:
        out_json = os.path.join(self.root, "proj.json")
        p = subprocess.run(
            [sys.executable, CLI, "--repo", self.root, "generate",
             "--out-json", out_json],
            capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        p2 = subprocess.run(
            [sys.executable, CLI, "--repo", self.root, "check", out_json],
            capture_output=True, text=True)
        self.assertEqual(p2.returncode, 0)
        self.assertFalse(json.loads(p2.stdout)["stale"])
        # move HEAD -> the projection must be marked stale (exit 3)
        _write(self.root, "newfile.txt", "x\n")
        _git(self.root, "add", "newfile.txt")
        _git(self.root, "commit", "-q", "-m", "advance")
        p3 = subprocess.run(
            [sys.executable, CLI, "--repo", self.root, "check", out_json],
            capture_output=True, text=True)
        self.assertEqual(p3.returncode, 3)
        self.assertTrue(json.loads(p3.stdout)["stale"])


if __name__ == "__main__":
    unittest.main()
