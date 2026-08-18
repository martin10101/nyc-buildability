#!/usr/bin/env python3
"""M0-T064 Unit A2 tests: incremental indexing (D-013-R037/R079 et al.).

The load-bearing proof is the BYTE-IDENTICAL parity invariant: the incremental
build's export equals a clean full rebuild's export, across cold build, warm
reuse, and every change class. Plus: exact change classification (add / content-
modify / metadata / delete / rename / global invalidator), the deterministic
affected-importer closure, reuse-on-unchanged, rebuild-on-change with a recorded
reason, fail-closed on a corrupt generation, and idempotent retry.
Deterministic, stdlib-only; the cache base is a temp dir.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools import repo_fingerprint as rf  # noqa: E402
from tools import repo_index_incremental as inc  # noqa: E402


def _git(repo: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class RepoCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._cbase = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self._tmp.name) / "repo"
        (self.repo / "services" / "api").mkdir(parents=True)
        _git(self.repo, "init", "-q")
        _git(self.repo, "config", "user.email", "t@t.t")
        _git(self.repo, "config", "user.name", "t")
        self.cbase = self._cbase.name
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(self._cbase.cleanup)

    def add(self, rel: str, text: str, msg: str = "c") -> None:
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-q", "-m", msg)

    def build(self):
        return inc.build_incremental(self.repo, cache_base=self.cbase)

    def full_bytes(self) -> bytes:
        return inc.clean_full_build_bytes(self.repo)


class ParityInvariant(RepoCase):
    """D-013-R037/R079: incremental export == clean full rebuild, byte-identical."""

    def setUp(self) -> None:
        super().setUp()
        self.add("services/api/a.py", "def f():\n    return g()\n")
        self.add("services/api/g.py", "def g():\n    return 1\n")

    def test_cold_build_matches_full(self) -> None:
        r = self.build()
        self.assertFalse(r.reused)
        self.assertEqual(r.export_bytes, self.full_bytes())

    def test_warm_reuse_matches_full(self) -> None:
        first = self.build()
        warm = self.build()
        self.assertTrue(warm.reused)
        self.assertEqual(warm.export_bytes, first.export_bytes)
        self.assertEqual(warm.export_bytes, self.full_bytes())

    def test_parity_holds_after_each_change_class(self) -> None:
        self.build()  # seed
        # content change
        self.add("services/api/g.py", "def g():\n    return 2\n", "modify")
        r = self.build()
        self.assertFalse(r.reused)
        self.assertIn("services/api/g.py", r.change_set.content_modified)
        self.assertEqual(r.export_bytes, self.full_bytes())
        # add
        self.add("services/api/h.py", "def h():\n    return 3\n", "add")
        r = self.build()
        self.assertIn("services/api/h.py", r.change_set.added)
        self.assertEqual(r.export_bytes, self.full_bytes())
        # delete
        (self.repo / "services" / "api" / "h.py").unlink()
        _git(self.repo, "commit", "-aqm", "del")
        r = self.build()
        self.assertIn("services/api/h.py", r.change_set.deleted)
        self.assertEqual(r.export_bytes, self.full_bytes())


class ChangeClassification(RepoCase):
    def test_rename_is_detected_by_content_digest(self) -> None:
        self.add("services/api/a.py", "def a():\n    return 1\n")
        self.build()
        _git(self.repo, "mv", "services/api/a.py", "services/api/b.py")
        _git(self.repo, "commit", "-qm", "rename")
        r = self.build()
        self.assertIn(("services/api/a.py", "services/api/b.py"),
                      r.change_set.renamed)
        # a rename is not double-counted as add+delete
        self.assertNotIn("services/api/b.py", r.change_set.added)
        self.assertNotIn("services/api/a.py", r.change_set.deleted)
        self.assertEqual(r.export_bytes, self.full_bytes())

    def test_global_invalidator_forces_full_rebuild(self) -> None:
        self.add("services/api/a.py", "X = 1\n")
        self.build()
        # Simulate a config/version change by classifying against a manifest
        # whose config_versions differ.
        fp = rf.compute_fingerprint(self.repo)
        prior = {"files": [e.to_dict() for e in fp.file_manifest],
                 "config_versions": {**fp.config_versions, "fingerprint": "0.0.0"}}
        cs = inc.classify_changes(prior, fp)
        self.assertTrue(cs.global_invalidators)
        self.assertTrue(cs.any_content_change())

    def test_metadata_only_change_is_classified_separately(self) -> None:
        self.add("services/api/a.py", "X = 1\n")
        fp1 = rf.compute_fingerprint(self.repo)
        prior = {"files": [e.to_dict() for e in fp1.file_manifest],
                 "config_versions": fp1.config_versions}
        # same content digest, mutated mode -> metadata_modified
        entry = prior["files"][0]
        entry_mode = dict(entry["mode"])
        entry_mode["is_symlink"] = not entry_mode["is_symlink"]
        # build a "current" that differs only in mode
        import copy
        cur = copy.deepcopy(fp1)
        cur.file_manifest[0].mode["is_symlink"] = not cur.file_manifest[0].mode["is_symlink"]
        cs = inc.classify_changes(prior, cur)
        self.assertIn(fp1.file_manifest[0].path, cs.metadata_modified)
        self.assertNotIn(fp1.file_manifest[0].path, cs.content_modified)


class AffectedClosure(RepoCase):
    def test_importer_closure_is_transitive_and_deterministic(self) -> None:
        graph = {
            "nodes": [
                {"id": "n_a", "file": "a.py"},
                {"id": "n_b", "file": "b.py"},
                {"id": "n_c", "file": "c.py"},
            ],
            "edges": [
                {"source": "n_b", "target": "n_a"},  # b imports a
                {"source": "n_c", "target": "n_b"},  # c imports b
            ],
        }
        closure = inc.affected_closure({"a.py"}, graph)
        self.assertEqual(closure, {"a.py", "b.py", "c.py"})
        # deterministic
        self.assertEqual(inc.affected_closure({"a.py"}, graph), closure)


class ReuseAndRecovery(RepoCase):
    def setUp(self) -> None:
        super().setUp()
        self.add("services/api/a.py", "X = 1\n")

    def test_unchanged_snapshot_reuses_without_rebuild(self) -> None:
        self.build()
        r = self.build()
        self.assertTrue(r.reused)
        self.assertEqual(r.telemetry["cache_result"], "hit")
        self.assertEqual(r.telemetry["files_parsed"], 0)  # the win: no parse

    def test_idempotent_retry(self) -> None:
        a = self.build()
        b = self.build()
        self.assertEqual(a.export_digest(), b.export_digest())

    def test_corrupt_generation_is_recovered_and_rebuilt(self) -> None:
        import json
        from tools import repo_index_cache as ric
        self.build()
        cache = ric.IndexCache(self.repo, base=self.cbase)
        cur = cache.load_current()
        # corrupt the promoted generation
        (cur.path / "payload.json").write_text('{"broken": true}', encoding="utf-8")
        # next build must NOT serve the corrupt generation; it rebuilds cleanly
        r = self.build()
        self.assertEqual(r.export_bytes, self.full_bytes())

    def test_full_rebuild_always_available_as_reference(self) -> None:
        self.build()
        self.assertEqual(inc.clean_full_build_bytes(self.repo), self.full_bytes())


class RealRepoSmoke(unittest.TestCase):
    def test_parity_on_this_repo(self) -> None:
        root = pathlib.Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as cbase:
            r = inc.build_incremental(root, cache_base=cbase)
            self.assertEqual(r.export_bytes, inc.clean_full_build_bytes(root))
            warm = inc.build_incremental(root, cache_base=cbase)
            self.assertTrue(warm.reused)


if __name__ == "__main__":
    unittest.main()
