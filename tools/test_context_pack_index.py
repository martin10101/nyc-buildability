#!/usr/bin/env python3
"""M0-T065 Unit B tests: index consumption, adaptive tier, coverage/provenance.

Runnable as ``python tools/test_context_pack_index.py`` (exit 0 = pass) or under
pytest. Fixtures are temp git repos with eligible source under services/api so the
deterministic A1/A2 index has real content; the index cache is a temp dir and the
external telemetry is off, so the suite is hermetic.
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
sys.path.insert(0, _HERE)

import context_pack_budget as budget  # noqa: E402

CONTEXT_PACK_PY = os.path.join(_HERE, "context_pack.py")


def _git(root: str, *args: str) -> None:
    env = dict(os.environ)
    env.update({"GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t.t",
                "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@t.t",
                "GIT_CONFIG_NOSYSTEM": "1"})
    subprocess.run(["git", *args], cwd=root, env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _write(root: str, rel: str, content: str) -> None:
    p = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(content.encode("utf-8"))


def build_fixture(root: str, task_id: str = "M0-T099") -> None:
    task = {"task_id": task_id, "title": "Fixture", "objective": "x",
            "allowed_paths": ["services/api/app/thing.py"],
            "outputs": ["services/api/app/thing.py"], "inputs": []}
    _write(root, f"project-control/tasks/{task_id}.json", json.dumps(task, indent=2))
    _write(root, "project-control/state.json", json.dumps({
        "project_status": "active", "accepted_tasks": [], "active_tasks": [task_id]},
        indent=2))
    _write(root, "CLAUDE.md",
           "# CLAUDE.md\n\n## On-demand routing\n\n| a | b |\n|---|---|\n\n## Next\n")
    # eligible source with an intra-repo import so the graph has an edge
    _write(root, "services/api/app/thing.py", "def thing():\n    return 1\n")
    _write(root, "services/api/app/user.py",
           "from services.api.app.thing import thing\n\ndef use():\n    return thing()\n")
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "baseline")


def run_cli(root: str, args: list[str], cache_base: str) -> subprocess.CompletedProcess:
    full = args + ["--index-cache-base", cache_base, "--no-index-telemetry"]
    return subprocess.run([sys.executable, CONTEXT_PACK_PY, *full],
                          cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def load_meta(out: str) -> dict:
    with open(os.path.join(out, "context.meta.json"), "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


class Case(unittest.TestCase):
    def setUp(self) -> None:
        self._t = tempfile.TemporaryDirectory()
        self._c = tempfile.TemporaryDirectory()
        self.root = self._t.name
        self.cache = self._c.name
        self.addCleanup(self._t.cleanup)
        self.addCleanup(self._c.cleanup)
        build_fixture(self.root)

    def build(self, extra: list[str], out_name: str = "out") -> tuple[dict, int]:
        out = os.path.join(self.root, out_name)
        common = ["--task", "M0-T099", "--role", "worker", "--provider", "claude",
                  "--max-bytes", "500000", "--out", out]
        p = run_cli(self.root, common + extra, self.cache)
        return (load_meta(out) if os.path.exists(os.path.join(out, "context.meta.json"))
                else {}), p.returncode


class AS1_SingleBudget(Case):
    def test_one_total_budget_and_compiler(self) -> None:
        meta, code = self.build([])
        self.assertEqual(code, 0)
        self.assertTrue(meta["budget"]["single_total_budget"])
        self.assertIn("effective_bound_bytes", meta["bounds"])
        # no per-source budget fields on any included source
        for inc in meta["included_files"]:
            self.assertNotIn("budget", inc)
            self.assertNotIn("effective_bound_bytes", inc)
        # exactly one context.md produced
        self.assertTrue(os.path.exists(os.path.join(self.root, "out", "context.md")))


class AS2_NormalTier(Case):
    def test_adaptive_normal_tier_no_override(self) -> None:
        meta, code = self.build([])
        self.assertEqual(code, 0)
        tier = meta["budget"]["tier"]
        self.assertIn(tier["tier"], ("small", "normal"))
        self.assertGreaterEqual(tier["target_tokens"], 5000)
        self.assertLessEqual(tier["target_tokens"], 8000)
        self.assertTrue(tier["hard_ceiling_unchanged"])
        self.assertFalse(meta["budget"]["amendment"]["changes_constants"])
        # the accepted contract numbers are echoed unchanged
        acc = meta["budget"]["amendment"]["accepted_contract"]
        self.assertEqual(acc["target_tokens"], 32000)
        self.assertEqual(acc["ordinary_ceiling_tokens"], 64000)


class AS3_MediumJustification(Case):
    def test_select_tier_withholds_without_justification(self) -> None:
        # unit-level: high breadth, no justification -> medium candidate, target held
        sig = budget.TierSignals(dependency_breadth=20)
        d = budget.select_tier("M0-T099", "worker", sig)
        self.assertEqual(d.tier, "medium")
        self.assertTrue(d.withheld_larger_target)
        self.assertEqual(d.target_tokens, budget.TIER_TARGET_TOKENS["normal"])
        # with justification -> medium target granted, never above the accepted 32K
        d2 = budget.select_tier("M0-T099", "worker",
                                budget.TierSignals(dependency_breadth=20,
                                                   justification="broad dependents"))
        self.assertEqual(d2.tier, "medium")
        self.assertFalse(d2.withheld_larger_target)
        self.assertGreater(d2.target_tokens, budget.TIER_TARGET_TOKENS["normal"])
        self.assertLessEqual(d2.target_tokens, budget.DEFAULT_TARGET_TOKENS)

    def test_cli_explicit_medium_needs_justification(self) -> None:
        meta_a, _ = self.build(["--tier", "medium"], out_name="a")
        self.assertEqual(meta_a["budget"]["tier"]["tier"], "medium")
        self.assertTrue(meta_a["budget"]["tier"]["withheld_larger_target"])
        self.assertEqual(meta_a["budget"]["tier"]["target_tokens"],
                         budget.TIER_TARGET_TOKENS["normal"])
        meta_b, _ = self.build(["--tier", "medium", "--tier-justification", "breadth"],
                               out_name="b")
        self.assertFalse(meta_b["budget"]["tier"]["withheld_larger_target"])
        self.assertLessEqual(meta_b["budget"]["tier"]["target_tokens"],
                             budget.DEFAULT_TARGET_TOKENS)


class AS4_CensusProvenance(Case):
    def test_meta_carries_index_provenance_and_census(self) -> None:
        meta, code = self.build([])
        self.assertEqual(code, 0)
        prov = meta["provenance"]
        self.assertTrue(prov["index_consumed"])
        for key in ("head_sha", "branch", "source_manifest_digest", "export_digest",
                    "versions", "generator_identity", "census", "coverage_mode",
                    "dependency_breadth"):
            self.assertIn(key, prov)
        self.assertTrue(prov["census"]["reconciles"])
        self.assertGreaterEqual(prov["census"]["eligible"], 2)  # thing.py + user.py
        self.assertEqual(prov["coverage_mode"], "census")
        # a code-graph neighborhood + census source are present
        groups = {i["group"] for i in meta["included_files"]}
        self.assertIn("repo_census", groups)


class AS5_RefuseOrSplit(Case):
    def test_material_overflow_fails_closed_with_split(self) -> None:
        big = os.path.join(self.root, "big_material.py")
        with open(big, "wb") as fh:
            fh.write(("# material line\n" * 4000).encode("utf-8"))
        out = os.path.join(self.root, "out")
        p = run_cli(self.root, [
            "--task", "M0-T099", "--role", "worker", "--provider", "claude",
            "--max-bytes", "3000", "--include", big, "--out", out], self.cache)
        self.assertEqual(p.returncode, 2)
        meta = load_meta(out)
        self.assertEqual(meta["overflow"]["resolved"], "split_required")
        self.assertIsNotNone(meta["overflow"]["split_proposal"])
        # the hard ceiling is the accepted min(ordinary, relative); the tier target
        # never relaxed it -- effective bound is <= max_bytes
        self.assertLessEqual(meta["bounds"]["effective_bound_bytes"], 3000)
        # material preserved under evidence/ (never silently dropped)
        ev = os.path.join(out, "evidence")
        self.assertTrue(os.listdir(ev))


class AS6_Determinism(Case):
    def test_build_twice_byte_identical(self) -> None:
        _write(self.root, "services/api/app/thing.py", "def thing():\n    return 9\n")
        m_a, ca = self.build([], out_name="a")
        m_b, cb = self.build([], out_name="b")
        self.assertEqual(ca, 0)
        self.assertEqual(cb, 0)
        with open(os.path.join(self.root, "a", "context.md"), "rb") as fh:
            a_md = fh.read()
        with open(os.path.join(self.root, "b", "context.md"), "rb") as fh:
            b_md = fh.read()
        self.assertEqual(a_md, b_md)
        with open(os.path.join(self.root, "a", "context.meta.json"), "rb") as fh:
            a_meta = fh.read()
        with open(os.path.join(self.root, "b", "context.meta.json"), "rb") as fh:
            b_meta = fh.read()
        self.assertEqual(a_meta, b_meta)


class NoIndexEscapeHatch(Case):
    def test_no_index_degrades_without_crash(self) -> None:
        out = os.path.join(self.root, "out")
        p = run_cli(self.root, [
            "--task", "M0-T099", "--role", "worker", "--provider", "claude",
            "--max-bytes", "500000", "--out", out, "--no-index"], self.cache)
        self.assertEqual(p.returncode, 0)
        meta = load_meta(out)
        self.assertEqual(meta["provenance"]["coverage_mode"], "disabled")
        cats = {o["category"] for o in meta["omitted_categories"]}
        self.assertIn("code_graph", cats)


if __name__ == "__main__":
    unittest.main()
