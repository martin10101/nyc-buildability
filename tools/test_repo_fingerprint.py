#!/usr/bin/env python3
"""M0-T063 Unit A1 tests: repository fingerprint + per-file manifest (D-013).

Proves AS-1 (fingerprint determinism + per-input sensitivity), AS-2 (census
accounting is complete and reconciles; an unreadable eligible file is a recorded
failure), and AS-5 (mtime is never proof). Deterministic, stdlib-only; every
fixture is a real temporary git repo so the production git-derived paths run.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools import repo_fingerprint as rf  # noqa: E402


def _git(repo: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True)


class RepoCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self._tmp.name) / "repo"
        (self.repo / "services" / "api").mkdir(parents=True)
        _git(self.repo, "init", "-q")
        _git(self.repo, "config", "user.email", "t@t.t")
        _git(self.repo, "config", "user.name", "t")
        self.addCleanup(self._tmp.cleanup)

    def add(self, rel: str, text: str, commit: bool = True) -> pathlib.Path:
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
        _git(self.repo, "add", rel)
        if commit:
            _git(self.repo, "commit", "-q", "-m", f"add {rel}")
        return p

    def fp(self, **kw):
        return rf.compute_fingerprint(self.repo, **kw)


class DeterminismAndSensitivity(RepoCase):
    """AS-1: two unchanged runs are byte-identical; each isolated change moves
    the snapshot fingerprint."""

    def setUp(self) -> None:
        super().setUp()
        self.add("services/api/a.py", "X = 1\n")
        self.add("tools/b.py", "Y = 2\n")

    def test_two_unchanged_runs_are_identical(self) -> None:
        a, b = self.fp(), self.fp()
        self.assertEqual(a.snapshot_fingerprint, b.snapshot_fingerprint)
        self.assertEqual(json.dumps(a.manifest_to_dict(), sort_keys=True),
                         json.dumps(b.manifest_to_dict(), sort_keys=True))

    def test_one_file_byte_moves_the_fingerprint(self) -> None:
        before = self.fp().snapshot_fingerprint
        self.add("services/api/a.py", "X = 2\n")  # one byte
        self.assertNotEqual(before, self.fp().snapshot_fingerprint)

    def test_a_config_version_moves_the_fingerprint(self) -> None:
        before = self.fp().snapshot_fingerprint
        after = self.fp(config_versions={"parser": "9.9.9"}).snapshot_fingerprint
        self.assertNotEqual(before, after)

    def test_dirty_state_moves_the_fingerprint(self) -> None:
        before = self.fp().snapshot_fingerprint
        (self.repo / "services" / "api" / "a.py").write_text(
            "X = 1\n# dirty\n", encoding="utf-8", newline="\n")  # uncommitted
        self.assertNotEqual(before, self.fp().snapshot_fingerprint)

    def test_head_move_changes_the_fingerprint(self) -> None:
        before = self.fp().snapshot_fingerprint
        self.add("tools/c.py", "Z = 3\n")  # new commit -> new HEAD + new file
        self.assertNotEqual(before, self.fp().snapshot_fingerprint)

    def test_hashes_are_domain_separated(self) -> None:
        # identical bytes under two domains never collide
        self.assertNotEqual(rf.domain_hash("a", b"x"), rf.domain_hash("b", b"x"))
        # length framing prevents concatenation ambiguity
        self.assertNotEqual(rf.domain_hash("d", b"ab", b"c"),
                            rf.domain_hash("d", b"a", b"bc"))

    def test_manifest_is_canonically_serialized(self) -> None:
        r = self.fp()
        paths = [e.path for e in r.file_manifest]
        self.assertEqual(paths, sorted(paths))
        # canonical_json is stable and sorted
        self.assertEqual(rf.canonical_json({"b": 1, "a": 2}),
                         b'{"a":2,"b":1}')


class CensusAccounting(RepoCase):
    """AS-2: every eligible file is indexed or explicitly excluded/failed; the
    counts reconcile; an unreadable eligible file is a recorded failure."""

    def test_counts_reconcile(self) -> None:
        self.add("services/api/a.py", "X = 1\n")
        self.add("tools/b.py", "Y = 2\n")
        c = self.fp().census
        self.assertTrue(c.reconciles())
        self.assertEqual(c.indexed, 2)

    def test_untracked_eligible_file_is_indexed_and_flagged(self) -> None:
        # MAJOR-1 (G3 review): the generator indexes untracked eligible files,
        # so the fingerprint must too - hash their content, flag tracked=False.
        self.add("services/api/a.py", "X = 1\n")
        (self.repo / "tools").mkdir(parents=True, exist_ok=True)
        (self.repo / "tools" / "u.py").write_text("U = 1\n", encoding="utf-8")
        r = self.fp()
        self.assertTrue(r.census.reconciles())
        entry = next(e for e in r.file_manifest if e.path == "tools/u.py")
        self.assertFalse(entry.tracked)          # flagged as untracked
        self.assertEqual(len(entry.raw_digest), 64)  # but its content IS hashed
        self.assertEqual(r.census.excluded, {})  # no untracked-exclusion

    def test_untracked_content_change_moves_the_fingerprint(self) -> None:
        # The MAJOR-1 collision the fix closes: two different untracked contents
        # MUST NOT share a snapshot fingerprint.
        self.add("services/api/a.py", "X = 1\n")
        (self.repo / "tools").mkdir(parents=True, exist_ok=True)
        u = self.repo / "tools" / "u.py"
        u.write_text("U = 1\n", encoding="utf-8")
        fpA = self.fp().snapshot_fingerprint
        u.write_text("U = 999\n", encoding="utf-8")  # untracked content changes
        self.assertNotEqual(fpA, self.fp().snapshot_fingerprint)

    def test_excluded_directory_is_not_eligible(self) -> None:
        self.add("services/api/a.py", "X = 1\n")
        # a __pycache__ file is in an excluded dir -> not eligible at all
        (self.repo / "tools" / "__pycache__").mkdir(parents=True)
        (self.repo / "tools" / "__pycache__" / "x.py").write_text("junk\n")
        c = self.fp().census
        self.assertEqual(c.eligible, 1)  # only a.py
        self.assertTrue(c.reconciles())

    def test_unreadable_eligible_file_is_a_recorded_failure(self) -> None:
        self.add("services/api/a.py", "X = 1\n")
        self.add("tools/b.py", "Y = 2\n")
        # Make b.py an eligible-but-unreadable entry by replacing it with a path
        # that vanishes between the walk and the hash: simulate via a broken
        # symlink (eligible name, does not resolve).
        target = self.repo / "tools" / "b.py"
        target.unlink()
        try:
            os.symlink(self.repo / "tools" / "nonexistent.py", target)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this host")
        _git(self.repo, "add", "tools/b.py")
        r = self.fp()
        # b.py is eligible and tracked but does not resolve -> a recorded failure,
        # never a silent skip.
        reasons = {f["path"]: f["reason"] for f in r.failures}
        self.assertIn("tools/b.py", reasons)
        self.assertTrue(r.census.failed)
        self.assertTrue(r.census.reconciles())


class MtimeNeverProof(RepoCase):
    """AS-5: a content change whose mtime is restored is still detected."""

    def test_content_change_with_restored_mtime_is_detected(self) -> None:
        p = self.add("services/api/a.py", "X = 1\n")
        st = p.stat()
        before = self.fp()
        before_digest = next(e.raw_digest for e in before.file_manifest
                             if e.path == "services/api/a.py")
        # change content, then restore the original (atime, mtime)
        p.write_text("X = 999\n", encoding="utf-8", newline="\n")
        os.utime(p, (st.st_atime, st.st_mtime))
        after = self.fp()
        after_digest = next(e.raw_digest for e in after.file_manifest
                            if e.path == "services/api/a.py")
        self.assertNotEqual(before_digest, after_digest,
                            "content digest must change even when mtime is restored")
        self.assertNotEqual(before.snapshot_fingerprint,
                            after.snapshot_fingerprint)


class CheckoutIdentity(RepoCase):
    def test_identity_is_the_canonical_path_sha_not_the_basename(self) -> None:
        self.add("services/api/a.py", "X = 1\n")
        r = self.fp()
        self.assertEqual(len(r.checkout_identity), 64)  # sha256 hex
        # identity depends on the full canonical path, not the folder name
        self.assertEqual(r.checkout_identity, rf.checkout_key(self.repo))


class RealRepoSmoke(unittest.TestCase):
    def test_runs_on_this_repo_and_reconciles(self) -> None:
        root = pathlib.Path(__file__).resolve().parent.parent
        r = rf.compute_fingerprint(root)
        self.assertTrue(r.census.reconciles())
        self.assertGreater(r.census.indexed, 100)
        self.assertEqual(len(r.snapshot_fingerprint), 64)


if __name__ == "__main__":
    unittest.main()
