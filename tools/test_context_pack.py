#!/usr/bin/env python3
"""Stdlib-only test suite for the bounded context-pack builder (task M0-T043).

Runs against TEMP FIXTURE git repositories only: nothing here depends on the
live repository's composition or the project ledger. Covers the four acceptance
scenarios plus determinism and a drift-lock against the frozen shadow-only
supervisor budget:

  AS-1  (test_as1_*)      -- all Section 12.3 output fields present, everything
                            digested, omitted categories listed, bounds +
                            truncation recorded, role-sufficiency flag.
  AS-2  (test_as2_*)      -- Section 12.2 default exclusions honored and recorded.
  AS-3  (test_as3_*)      -- overflow splits/summarizes deterministically; a
                            material source is never silently truncated (fail-
                            closed path included; AD-046).
  AS-4  (test_as4_*)      -- a reviewer packet carries primary-source hunks
                            sufficient to verify a worker claim, not a summary.
  drift (test_drift_*)    -- budget constants + estimate equal the shadow-only
                            tools/agent_supervisor/review_packet.py.
  det   (test_determinism)-- same repo state + args => byte-identical output.

Run either way (matches tools/test_project_control.py convention):
    python tools/test_context_pack.py        (exit 0 = pass)
    pytest -q tools/test_context_pack.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import context_pack as cp  # noqa: E402

CONTEXT_PACK_PY = os.path.join(_HERE, "context_pack.py")


# --------------------------------------------------------------------------
# fixture helpers
# --------------------------------------------------------------------------


def _write(root: str, relpath: str, content: str) -> None:
    path = os.path.join(root, *relpath.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(content.encode("utf-8"))


def _git(root: str, *args: str) -> None:
    env = dict(os.environ)
    env.update({
        "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "t@example.com",
        "GIT_CONFIG_NOSYSTEM": "1",
    })
    subprocess.run(["git", *args], cwd=root, env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_fixture(root: str, *, task_id: str = "M0-T099",
                  extra_task_fields: dict | None = None) -> None:
    """A minimal but complete fixture repo: git history + project-control tree
    + the default-exclusion decoys (PRD, directives, reports, transcripts,
    unrelated packets, generated artifacts, datasets)."""
    task = {
        "task_id": task_id,
        "title": "Fixture task",
        "objective": "do the fixture thing",
        "allowed_paths": ["services/api/app/thing.py"],
        "outputs": ["services/api/app/thing.py"],
        "inputs": [],
    }
    if extra_task_fields:
        task.update(extra_task_fields)
    _write(root, f"project-control/tasks/{task_id}.json", json.dumps(task, indent=2))
    _write(root, "project-control/tasks/M0-T001.json",
           json.dumps({"task_id": "M0-T001", "title": "UNRELATED packet"}, indent=2))
    _write(root, "project-control/state.json", json.dumps({
        "project_status": "active", "current_milestone": "M0",
        "accepted_tasks": ["M0-T001"], "active_tasks": [task_id],
        "blocked_tasks": [], "failed_gates": [],
    }, indent=2))
    _write(root, "project-control/checkpoints/CP-0001.json",
           json.dumps({"checkpoint_id": "CP-0001", "summary": "early"}, indent=2))
    _write(root, "project-control/checkpoints/CP-0007.json",
           json.dumps({"checkpoint_id": "CP-0007", "summary": "LATEST checkpoint"}, indent=2))
    _write(root, "project-control/blockers/B-042-thing.json", json.dumps({
        "blocker_id": "B-042", "title": "blocks fixture",
        "affects": [f"{task_id} needs a credential"], "status": "open",
    }, indent=2))
    _write(root, "project-control/blockers/B-099-other.json", json.dumps({
        "blocker_id": "B-099", "title": "unrelated", "affects": ["M9-T999"],
    }, indent=2))
    _write(root, "project-control/reports/session-handoff-2026-01-01.json",
           json.dumps({"schema_version": "1", "task_id": task_id, "note": "old handoff"}, indent=2))
    _write(root, "project-control/reports/session-handoff-2026-05-05.json",
           json.dumps({"schema_version": "1", "task_id": task_id, "note": "NEWEST handoff"}, indent=2))
    _write(root, "CLAUDE.md",
           "# CLAUDE.md\n\n## Some earlier section\n\nblah\n\n"
           "## On-demand routing — read only what the task needs\n\n"
           "| Working on… | Read |\n|---|---|\n| Scope | PRD.md |\n\n"
           "## Task routine\n\nnext section\n")
    _write(root, "docs/SESSION_HANDOFF.md", "# Handoff\n\ncurrent block\n")
    # ---- Section 12.2 default-exclusion decoys (must NOT be embedded) ----
    _write(root, "PRD.md", "SECRET_PRD_MARKER whole product requirements doc\n" * 5)
    _write(root, "project-control/directives/D-001/source-001.md",
           "SECRET_DIRECTIVE_MARKER full directive registry\n" * 5)
    _write(root, "project-control/reports/OLD-REPORT-1.md",
           "SECRET_HISTORICAL_REPORT_MARKER\n" * 5)
    _write(root, "transcripts/session-old.txt", "SECRET_TRANSCRIPT_MARKER\n" * 5)
    _write(root, "apps/web/.next/generated.js", "SECRET_GENERATED_ARTIFACT_MARKER\n" * 5)
    _write(root, "data/pluto/all.csv", "SECRET_CITY_DATASET_MARKER\n" * 5)
    # ---- a source file that will receive a tracked change ----
    _write(root, "services/api/app/thing.py", "def thing():\n    return 1\n")
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "baseline")


def run_cli(root: str, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, CONTEXT_PACK_PY, *args],
                          cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def load_meta(out: str) -> dict:
    with open(os.path.join(out, "context.meta.json"), "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


def read_md(out: str) -> str:
    with open(os.path.join(out, "context.md"), "rb") as fh:
        return fh.read().decode("utf-8")


def md_bytes(out: str) -> int:
    return os.path.getsize(os.path.join(out, "context.md"))


def assert_bound_invariant(tc: unittest.TestCase, out: str, returncode: int) -> None:
    """The F1 contract: whenever the process exits 0 (within_bound or summarized),
    the REAL emitted context.md (footer included) must respect the effective byte
    bound. Exit 2 is the fail-closed split path and is exempt (the split report is
    a diagnostic, not the work packet)."""
    meta = load_meta(out)
    emitted = md_bytes(out)
    eff = meta["bounds"]["effective_bound_bytes"]
    if returncode == 0:
        tc.assertLessEqual(
            emitted, eff,
            f"exit 0 but emitted context.md {emitted} B > effective bound {eff} B "
            f"(overflow.resolved={meta['overflow']['resolved']})")
        tc.assertTrue(meta["actuals"]["within_effective_bound"])
        tc.assertIn(meta["overflow"]["resolved"], ("within_bound", "summarized"))
    else:
        tc.assertEqual(returncode, 2)
        tc.assertEqual(meta["overflow"]["resolved"], "split_required")


# --------------------------------------------------------------------------
# AS-1: schema / all Section 12.3 fields
# --------------------------------------------------------------------------


class TestAS1Schema(unittest.TestCase):
    def test_as1_all_1203_fields_present(self):
        with tempfile.TemporaryDirectory() as root:
            build_fixture(root)
            out = os.path.join(root, "out")
            proc = run_cli(root, ["--task", "M0-T099", "--role", "worker",
                                  "--provider", "claude", "--max-bytes", "500000",
                                  "--out", out, "--context-window", "200000"])
            self.assertEqual(proc.returncode, 0, proc.stderr.decode())
            # F1 invariant: an exit-0 packet respects the effective byte bound.
            assert_bound_invariant(self, out, proc.returncode)
            # files exist
            self.assertTrue(os.path.isfile(os.path.join(out, "context.md")))
            self.assertTrue(os.path.isfile(os.path.join(out, "context.meta.json")))
            self.assertTrue(os.path.isdir(os.path.join(out, "evidence")))
            meta = load_meta(out)
            # every included file has a sha256 digest + bytes + tokens
            self.assertTrue(meta["included_files"])
            for f in meta["included_files"]:
                self.assertEqual(len(f["sha256"]), 64)
                self.assertIn("bytes", f)
                self.assertIn("estimated_tokens", f)
                self.assertIn("truncated", f)
                self.assertIn("material", f)
                # the evidence file for each included source exists
                self.assertTrue(os.path.isfile(os.path.join(out, f["evidence_path"])))
            # omitted categories listed
            self.assertTrue(meta["omitted_categories"])
            # graph queries recorded (key present)
            self.assertIn("graph_queries", meta)
            # byte AND token bounds
            b = meta["bounds"]
            for key in ("max_bytes", "target_tokens", "ordinary_ceiling_tokens",
                        "effective_ceiling_tokens", "effective_bound_bytes"):
                self.assertIn(key, b)
            # task id + repo SHA
            self.assertEqual(meta["task_id"], "M0-T099")
            self.assertEqual(len(meta["repo_sha"]), 40)
            # truncation status recorded
            self.assertIn("truncated_any", meta)
            # role sufficiency flag
            self.assertIn("sufficient", meta["sufficiency"])
            self.assertTrue(meta["sufficiency"]["sufficient"])  # worker has task+routing

    def test_as1_digest_matches_evidence_bytes(self):
        with tempfile.TemporaryDirectory() as root:
            build_fixture(root)
            out = os.path.join(root, "out")
            run_cli(root, ["--task", "M0-T099", "--role", "controller",
                           "--provider", "claude", "--max-bytes", "500000", "--out", out])
            meta = load_meta(out)
            import hashlib
            for f in meta["included_files"]:
                with open(os.path.join(out, f["evidence_path"]), "rb") as fh:
                    data = fh.read()
                self.assertEqual(hashlib.sha256(data).hexdigest(), f["sha256"])


# --------------------------------------------------------------------------
# AS-2: default exclusions (Section 12.2)
# --------------------------------------------------------------------------


class TestAS2Exclusions(unittest.TestCase):
    def test_as2_all_eight_categories_recorded(self):
        with tempfile.TemporaryDirectory() as root:
            build_fixture(root)
            out = os.path.join(root, "out")
            run_cli(root, ["--task", "M0-T099", "--role", "worker",
                           "--provider", "claude", "--max-bytes", "500000", "--out", out])
            meta = load_meta(out)
            recorded = {o["category"] for o in meta["omitted_categories"]}
            for cat in ("entire_prd", "entire_directive_registry",
                        "all_historical_reports", "old_session_transcripts",
                        "unrelated_task_packets", "full_generated_artifacts",
                        "full_city_datasets", "whole_code_graph"):
                self.assertIn(cat, recorded, f"missing default exclusion {cat}")
            defaults = {o["category"] for o in meta["omitted_categories"]
                        if o.get("default_exclusion")}
            self.assertEqual(len(defaults), 8)

    def test_as2_decoy_markers_absent_from_packet(self):
        with tempfile.TemporaryDirectory() as root:
            build_fixture(root)
            out = os.path.join(root, "out")
            run_cli(root, ["--task", "M0-T099", "--role", "worker",
                           "--provider", "claude", "--max-bytes", "500000", "--out", out])
            md = read_md(out)
            for marker in ("SECRET_PRD_MARKER", "SECRET_DIRECTIVE_MARKER",
                           "SECRET_HISTORICAL_REPORT_MARKER", "SECRET_TRANSCRIPT_MARKER",
                           "SECRET_GENERATED_ARTIFACT_MARKER", "SECRET_CITY_DATASET_MARKER"):
                self.assertNotIn(marker, md, f"{marker} leaked into the packet")
            # the unrelated task packet's id must not appear as an embedded source
            self.assertNotIn('"task_id": "M0-T001"', md)


# --------------------------------------------------------------------------
# AS-3: overflow (Section 12.4 / AD-046)
# --------------------------------------------------------------------------


class TestAS3Overflow(unittest.TestCase):
    def test_as3_summarize_nonmaterial_log_preserves_original(self):
        with tempfile.TemporaryDirectory() as root:
            build_fixture(root)
            # A large NON-material CI log (reducible) forces overflow at a small bound.
            ci = os.path.join(root, "ci.txt")
            with open(ci, "wb") as fh:
                fh.write(("CI_LINE step passed\n" * 4000).encode("utf-8"))
            out = os.path.join(root, "out")
            proc = run_cli(root, ["--task", "M0-T099", "--role", "worker",
                                  "--provider", "claude", "--max-bytes", "9000",
                                  "--out", out, "--ci-summary", ci])
            self.assertEqual(proc.returncode, 0, proc.stderr.decode())
            meta = load_meta(out)
            self.assertTrue(meta["overflow"]["triggered"])
            self.assertEqual(meta["overflow"]["resolved"], "summarized")
            self.assertTrue(meta["truncated_any"])
            # the CI source is recorded as truncated WITH its original digest+bytes
            trunc = {t["source_id"]: t for t in meta["truncations"]}
            self.assertIn("latest_ci", trunc)
            self.assertEqual(len(trunc["latest_ci"]["original_sha256"]), 64)
            self.assertGreater(trunc["latest_ci"]["original_bytes"],
                               trunc["latest_ci"]["summarized_bytes"])
            # the FULL original is preserved on disk as an exact artifact reference
            art = os.path.join(out, "evidence", trunc["latest_ci"]["artifact"])
            self.assertTrue(os.path.isfile(art))
            with open(art, "rb") as fh:
                self.assertEqual(fh.read().count(b"CI_LINE"), 4000)
            # packet now fits -- and the emitted file (footer included) respects
            # the effective bound (F1: footer-aware enforcement).
            self.assertTrue(meta["actuals"]["within_effective_bound"])
            assert_bound_invariant(self, out, proc.returncode)
            self.assertLessEqual(md_bytes(out), 9000)

    def test_as3_material_never_silently_truncated_failclosed(self):
        with tempfile.TemporaryDirectory() as root:
            build_fixture(root)
            # A large MATERIAL explicit include that cannot be summarized.
            big = os.path.join(root, "big_material.py")
            with open(big, "wb") as fh:
                fh.write(("x = 1  # MATERIAL_LINE\n" * 4000).encode("utf-8"))
            out = os.path.join(root, "out")
            proc = run_cli(root, ["--task", "M0-T099", "--role", "worker",
                                  "--provider", "claude", "--max-bytes", "9000",
                                  "--out", out, "--include", "big_material.py"])
            # fail-closed: non-zero exit, NOT a quietly smaller packet
            self.assertEqual(proc.returncode, 2, proc.stdout.decode())
            meta = load_meta(out)
            self.assertEqual(meta["overflow"]["resolved"], "split_required")
            proposal = meta["overflow"]["split_proposal"]
            self.assertIsNotNone(proposal)
            # the oversize material source is named with its original digest
            oversize_ids = {o["source_id"] for o in proposal["oversize_material_sources"]}
            self.assertIn("include::big_material.py", oversize_ids)
            for o in proposal["oversize_material_sources"]:
                self.assertEqual(len(o["original_sha256"]), 64)
            # the emitted context.md is a split REPORT, not the giant material body
            md = read_md(out)
            self.assertIn("fail-closed", md.lower())
            self.assertLess(md.count("MATERIAL_LINE"), 100)  # body NOT embedded
            # but the full material is preserved as evidence (nothing dropped)
            ev_path = next(f["evidence_path"] for f in meta["included_files"]
                           if f["source_id"] == "include::big_material.py")
            ev = os.path.join(out, ev_path)
            self.assertTrue(os.path.isfile(ev))
            with open(ev, "rb") as fh:
                self.assertEqual(fh.read().count(b"MATERIAL_LINE"), 4000)

    def test_as3_bound_boundary_never_over_bound_exit0(self):
        # F1 regression: sweep bounds just BELOW the natural size (the old
        # footer-blind window). Every result must be either exit-0 with the emitted
        # file inside the bound, or exit-2 fail-closed split -- NEVER exit 0 with an
        # over-bound context.md.
        with tempfile.TemporaryDirectory() as root:
            build_fixture(root)
            base = ["--task", "M0-T099", "--role", "worker", "--provider", "claude"]
            nat_out = os.path.join(root, "nat")
            natp = run_cli(root, base + ["--max-bytes", "500000", "--out", nat_out])
            self.assertEqual(natp.returncode, 0, natp.stderr.decode())
            natural = md_bytes(nat_out)
            self.assertGreater(natural, 0)
            # bounds inside the footer-blind window and well below it
            candidates = sorted({natural - 1, natural - 40, natural - 200,
                                 natural - 900, natural - 1500,
                                 natural // 2, max(200, natural // 4)})
            saw_exit0 = False
            saw_exit2 = False
            for bound in candidates:
                if bound <= 0:
                    continue
                out = os.path.join(root, f"bnd_{bound}")
                proc = run_cli(root, base + ["--max-bytes", str(bound), "--out", out])
                self.assertIn(proc.returncode, (0, 2),
                              f"unexpected exit {proc.returncode} at max_bytes={bound}")
                # the core invariant, at every swept bound
                assert_bound_invariant(self, out, proc.returncode)
                if proc.returncode == 0:
                    saw_exit0 = True
                    # explicit over-bound guard on the raw file size
                    self.assertLessEqual(md_bytes(out), bound,
                                         f"emitted > requested --max-bytes {bound}")
                else:
                    saw_exit2 = True
            # the sweep must exercise the fail-closed path at least once (bounds
            # this far below natural cannot fit the material for this fixture)
            self.assertTrue(saw_exit2, "boundary sweep never hit the fail-closed path")
            del saw_exit0  # exit-0 near the bound is fixture-dependent; not required

    def test_as3_split_proposal_bins_multiple_material_sources(self):
        with tempfile.TemporaryDirectory() as root:
            build_fixture(root)
            # Two material includes, each fits alone but not together under bound.
            for i in (1, 2):
                p = os.path.join(root, f"m{i}.py")
                with open(p, "wb") as fh:
                    fh.write(("y = 1  # PIECE\n" * 500).encode("utf-8"))
            out = os.path.join(root, "out")
            proc = run_cli(root, ["--task", "M0-T099", "--role", "worker",
                                  "--provider", "claude", "--max-bytes", "9000",
                                  "--out", out, "--include", "m1.py", "--include", "m2.py"])
            self.assertEqual(proc.returncode, 2)
            meta = load_meta(out)
            bins = meta["overflow"]["split_proposal"]["sub_packets"]
            self.assertGreaterEqual(len(bins), 2)
            for b in bins:
                self.assertLessEqual(b["bytes"], meta["bounds"]["effective_bound_bytes"])


# --------------------------------------------------------------------------
# AS-4: reviewer packet carries primary-source hunks
# --------------------------------------------------------------------------


class TestAS4ReviewerPrimarySource(unittest.TestCase):
    def test_as4_reviewer_includes_changed_hunks(self):
        with tempfile.TemporaryDirectory() as root:
            build_fixture(root)
            # A worker makes a tracked change; the reviewer must see the HUNK.
            _write(root, "services/api/app/thing.py",
                   "def thing():\n    return 42  # WORKER_ADDED_LINE\n")
            out = os.path.join(root, "out")
            proc = run_cli(root, ["--task", "M0-T099", "--role", "reviewer",
                                  "--provider", "codex", "--max-bytes", "500000", "--out", out])
            self.assertEqual(proc.returncode, 0, proc.stderr.decode())
            meta = load_meta(out)
            # git_diff source present and sufficiency true (primary source available)
            groups = {f["group"] for f in meta["included_files"]}
            self.assertIn("git_diff", groups)
            self.assertTrue(meta["sufficiency"]["sufficient"])
            # the actual changed line appears in the packet (primary source, not a summary)
            md = read_md(out)
            self.assertIn("WORKER_ADDED_LINE", md)
            self.assertIn("+    return 42", md)

    def test_as4_reviewer_insufficient_without_hunks(self):
        with tempfile.TemporaryDirectory() as root:
            build_fixture(root)  # clean tree, no changes to review
            out = os.path.join(root, "out")
            proc = run_cli(root, ["--task", "M0-T099", "--role", "reviewer",
                                  "--provider", "codex", "--max-bytes", "500000", "--out", out])
            self.assertEqual(proc.returncode, 0)
            meta = load_meta(out)
            self.assertFalse(meta["sufficiency"]["sufficient"])
            self.assertIn("primary-source", meta["sufficiency"]["reason"])


# --------------------------------------------------------------------------
# Drift-lock: budget equals the frozen shadow-only supervisor
# --------------------------------------------------------------------------


class TestBudgetDriftLock(unittest.TestCase):
    def _import_review_packet(self):
        # Import the shadow-only module without editing it (read/import allowed).
        sys.path.insert(0, os.path.dirname(_HERE))  # repo root so `tools` is a package
        try:
            from tools.agent_supervisor import review_packet as rp
        except Exception as exc:  # F2/A-4: fail loudly, never skip
            # This module is expected to exist in this repo; the drift-lock is the
            # only guarantee the local budget mirror stays honest. A move/break must
            # break the suite, not silently disarm the lock.
            self.fail(f"drift-lock target tools/agent_supervisor/review_packet.py "
                      f"is not importable ({exc}); the budget mirror can no longer "
                      f"be drift-checked -- fix the import, do not skip")
        return rp

    def test_drift_constants_equal(self):
        rp = self._import_review_packet()
        self.assertEqual(cp.DEFAULT_TARGET_TOKENS, rp.DEFAULT_TARGET_TOKENS)
        self.assertEqual(cp.DEFAULT_ORDINARY_CEILING_TOKENS,
                         rp.DEFAULT_ORDINARY_CEILING_TOKENS)
        self.assertEqual(cp.DEFAULT_RELATIVE_CEILING_RATIO,
                         rp.DEFAULT_RELATIVE_CEILING_RATIO)
        self.assertEqual(cp.DEFAULT_BYTES_PER_TOKEN, rp.DEFAULT_BYTES_PER_TOKEN)

    def test_drift_estimate_equal(self):
        rp = self._import_review_packet()
        budget = rp.ReviewBudget()
        for size in (0, 1, 3, 4, 5, 100, 4001, 128_000, 999_999):
            self.assertEqual(cp.estimate_tokens(size), budget.estimate_tokens(size),
                             f"token estimate diverged at {size} bytes")

    def test_drift_effective_ceiling_equal(self):
        rp = self._import_review_packet()
        budget = rp.ReviewBudget()
        for window in (None, 0, 50_000, 200_000, 1_000_000):
            mine = cp.effective_ceiling_tokens(
                cp.DEFAULT_ORDINARY_CEILING_TOKENS,
                cp.DEFAULT_RELATIVE_CEILING_RATIO, window)
            theirs = budget.effective_ceiling(window)
            self.assertEqual(mine["tokens"], theirs.tokens,
                             f"effective ceiling diverged at window={window}")


# --------------------------------------------------------------------------
# Determinism
# --------------------------------------------------------------------------


class TestDeterminism(unittest.TestCase):
    def test_determinism_byte_identical(self):
        with tempfile.TemporaryDirectory() as root:
            build_fixture(root)
            _write(root, "services/api/app/thing.py",
                   "def thing():\n    return 7\n")
            out_a = os.path.join(root, "a")
            out_b = os.path.join(root, "b")
            common = ["--task", "M0-T099", "--role", "reviewer", "--provider",
                      "claude", "--max-bytes", "500000", "--context-window", "200000"]
            run_cli(root, common + ["--out", out_a])
            run_cli(root, common + ["--out", out_b])
            with open(os.path.join(out_a, "context.md"), "rb") as fh:
                md_a = fh.read()
            with open(os.path.join(out_b, "context.md"), "rb") as fh:
                md_b = fh.read()
            self.assertEqual(md_a, md_b, "context.md not byte-identical")
            with open(os.path.join(out_a, "context.meta.json"), "rb") as fh:
                meta_a = fh.read()
            with open(os.path.join(out_b, "context.meta.json"), "rb") as fh:
                meta_b = fh.read()
            self.assertEqual(meta_a, meta_b, "context.meta.json not byte-identical")

    def test_determinism_byte_identical_summarized_fixpoint(self):
        # Determinism must hold across the new footer-aware fixpoint (F1). The
        # summarized regime is the one that iterates the footer to a fixpoint, so
        # build-twice must still be byte-identical there.
        with tempfile.TemporaryDirectory() as root:
            build_fixture(root)
            ci = os.path.join(root, "ci.txt")
            with open(ci, "wb") as fh:
                fh.write(("CI_LINE step passed\n" * 4000).encode("utf-8"))
            common = ["--task", "M0-T099", "--role", "worker", "--provider",
                      "claude", "--max-bytes", "9000", "--ci-summary", ci]
            out_a = os.path.join(root, "a")
            out_b = os.path.join(root, "b")
            pa = run_cli(root, common + ["--out", out_a])
            pb = run_cli(root, common + ["--out", out_b])
            self.assertEqual(pa.returncode, 0, pa.stderr.decode())
            self.assertEqual(pb.returncode, 0, pb.stderr.decode())
            # confirm we are in the fixpoint (summarized) regime, not trivial
            self.assertEqual(load_meta(out_a)["overflow"]["resolved"], "summarized")
            with open(os.path.join(out_a, "context.md"), "rb") as fh:
                a = fh.read()
            with open(os.path.join(out_b, "context.md"), "rb") as fh:
                b = fh.read()
            self.assertEqual(a, b, "summarized context.md not byte-identical")
            # and the fixpoint result respects the bound (F1 invariant)
            assert_bound_invariant(self, out_a, pa.returncode)


if __name__ == "__main__":
    unittest.main(verbosity=2)
