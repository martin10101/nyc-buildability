#!/usr/bin/env python3
"""M0-T063 Unit A1 tests: baseline harness (D-013-R049/R050/R051/R054/R055).

Proves AS-4: the baseline is captured from the EXISTING unmodified code-graph
generator; the committed evidence is bounded and sanitized (digests + counts,
no raw graph, no private absolute path); the external telemetry is append-only
and redacted, with nullable-not-zero fields for unavailable measurements.
Deterministic, stdlib-only; telemetry goes to a temp cache base.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools import repo_index_baseline as bl  # noqa: E402


def _git(repo: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class BaselineCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self._tmp.name) / "repo"
        (self.repo / "services" / "api").mkdir(parents=True)
        _git(self.repo, "init", "-q")
        _git(self.repo, "config", "user.email", "t@t.t")
        _git(self.repo, "config", "user.name", "t")
        (self.repo / "services" / "api" / "m.py").write_text(
            "def f():\n    return g()\n\ndef g():\n    return 1\n",
            encoding="utf-8", newline="\n")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-q", "-m", "seed")
        self.addCleanup(self._tmp.cleanup)


class CaptureFromUnmodifiedGenerator(BaselineCase):
    def test_capture_records_digest_and_counts(self) -> None:
        r = bl.capture_baseline(self.repo)
        s = r.committed_summary()
        self.assertEqual(len(s["export_digest"]), 64)
        self.assertGreaterEqual(s["counts"]["nodes"], 2)  # f and g
        self.assertGreaterEqual(s["counts"]["input_files"], 1)
        self.assertTrue(s["census"]["reconciles"])

    def test_capture_is_deterministic(self) -> None:
        a = bl.capture_baseline(self.repo)
        b = bl.capture_baseline(self.repo)
        self.assertEqual(a.export_digest, b.export_digest)
        self.assertEqual(a.node_count, b.node_count)

    def test_export_digest_tracks_a_content_change(self) -> None:
        before = bl.capture_baseline(self.repo).export_digest
        (self.repo / "services" / "api" / "m.py").write_text(
            "def f():\n    return 42\n", encoding="utf-8", newline="\n")
        _git(self.repo, "commit", "-aqm", "change")
        self.assertNotEqual(before, bl.capture_baseline(self.repo).export_digest)


class CommittedEvidenceIsBoundedAndSanitized(BaselineCase):
    def test_summary_has_no_raw_graph_and_no_absolute_path(self) -> None:
        r = bl.capture_baseline(self.repo)
        summary = r.committed_summary()
        blob = json.dumps(summary)
        # bounded: no 'nodes' array, no 'edges' array embedded
        self.assertNotIn('"nodes": [', blob)
        self.assertNotIn('"edges": [', blob)
        # sanitized: the private absolute repo path never appears
        self.assertNotIn(str(self.repo), blob)
        self.assertNotIn(str(self.repo.resolve()), blob)

    def test_write_committed_evidence_files(self) -> None:
        r = bl.capture_baseline(self.repo)
        with tempfile.TemporaryDirectory() as out:
            jp = pathlib.Path(out) / "evidence.json"
            mp = pathlib.Path(out) / "evidence.md"
            bl.write_committed_evidence(r, jp, mp)
            self.assertIn("export_digest", jp.read_text(encoding="utf-8"))
            self.assertIn("baseline evidence", mp.read_text(encoding="utf-8"))
            self.assertNotIn(str(self.repo), jp.read_text(encoding="utf-8"))


class TelemetryIsRedactedAppendOnlyNullableNotZero(BaselineCase):
    def test_telemetry_appends_outside_the_repo_with_null_measures(self) -> None:
        r = bl.capture_baseline(self.repo)
        with tempfile.TemporaryDirectory() as tbase:
            log = bl.append_telemetry(r, self.repo, run_id="run-1", base=tbase)
            # outside the repo
            self.assertNotIn(str(self.repo.resolve()), str(log.resolve()))
            bl.append_telemetry(r, self.repo, run_id="run-2", base=tbase)
            lines = log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)  # append-only
            rec = json.loads(lines[0])
            # measured-only fields are null, NOT fabricated as zero
            self.assertIsNone(rec["provider_input_tokens"])
            self.assertIsNone(rec["context_window_occupancy"])
            self.assertEqual(rec["kind"], "baseline_full_build")
            # counts that ARE known are present
            self.assertIsInstance(rec["node_count"], int)


class RealRepoBaselineSmoke(unittest.TestCase):
    def test_runs_on_this_repo(self) -> None:
        root = pathlib.Path(__file__).resolve().parent.parent
        r = bl.capture_baseline(root)
        self.assertGreater(r.node_count, 100)
        self.assertTrue(r.census["reconciles"])


if __name__ == "__main__":
    unittest.main()
