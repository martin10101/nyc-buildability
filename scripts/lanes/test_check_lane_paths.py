#!/usr/bin/env python3
"""Tests for scripts/lanes/check_lane_paths.py (task M0-T164). Stdlib unittest only.

Run: python3 scripts/lanes/test_check_lane_paths.py
"""

from __future__ import annotations

import contextlib
import io
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_lane_paths as clp  # noqa: E402

REAL = clp.Ownership.load(clp.DEFAULT_OWNERSHIP)


def run_main(*argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = clp.main(list(argv))
    return code, out.getvalue()


class YamlSubsetTests(unittest.TestCase):
    def test_nested_mapping_sequence_and_scalars(self):
        data = clp.parse_yaml_subset(
            "version: 1\n"
            "name: 'quoted # not a comment'\n"
            "lanes:\n"
            "  A:\n"
            "    port: 8101  # trailing comment\n"
            "rules:\n"
            "  - lane: A\n"
            "    globs:\n"
            "      - a/**\n"
            "      - \"*\"\n"
        )
        self.assertEqual(data["version"], 1)
        self.assertEqual(data["name"], "quoted # not a comment")
        self.assertEqual(data["lanes"], {"A": {"port": 8101}})
        self.assertEqual(data["rules"], [{"lane": "A", "globs": ["a/**", "*"]}])

    def test_duplicate_key_rejected(self):
        with self.assertRaises(clp.OwnershipError):
            clp.parse_yaml_subset("a: 1\na: 2\n")

    def test_tab_indentation_rejected(self):
        with self.assertRaises(clp.OwnershipError):
            clp.parse_yaml_subset("a:\n\tb: 1\n")

    def test_bad_indentation_rejected(self):
        with self.assertRaises(clp.OwnershipError):
            clp.parse_yaml_subset("a: 1\n    b: 2\n")


class GlobTests(unittest.TestCase):
    def test_star_stays_in_one_segment(self):
        rx = clp.glob_to_regex("apps/web/src/lib/*-api.ts")
        self.assertTrue(rx.match("apps/web/src/lib/scenario-api.ts"))
        self.assertFalse(rx.match("apps/web/src/lib/architect/max-envelope-api.ts"))

    def test_double_star_crosses_segments(self):
        rx = clp.glob_to_regex("services/api/app/rules/**")
        self.assertTrue(rx.match("services/api/app/rules/rulesets/x.json"))
        self.assertFalse(rx.match("services/api/app/rulesx/y.py"))

    def test_root_star_matches_root_files_only(self):
        rx = clp.glob_to_regex("*")
        self.assertTrue(rx.match("README.md"))
        self.assertFalse(rx.match("docs/README.md"))

    def test_double_star_slash_allows_zero_directories(self):
        rx = clp.glob_to_regex("docs/**/x.md")
        self.assertTrue(rx.match("docs/x.md"))
        self.assertTrue(rx.match("docs/a/b/x.md"))


class OwnershipTests(unittest.TestCase):
    CASES = {
        "services/api/app/rules/registry.py": "A",
        "services/api/app/scenario/unused_floor_area.py": "A",
        "tests/fixtures/residential_validation/23-22.txt": "A",
        "docs/research/zr-snapshots/v1/zr-23-22.json": "A",
        "services/api/app/_zr_snapshots/v1/zr-23-22.json": "A",
        "services/api/app/connectors/pluto_soda.py": "B",
        "services/api/tests/fixtures/dtm_lot_outline/DTM_3022640032.geojson": "B",
        "docs/research/condo-base-lot-resolution-sources.md": "B",
        "services/api/app/main.py": "C",
        "services/api/app/config.py": "C",
        "services/api/app/api/v1/lot_geometry.py": "C",
        "packages/contracts/schemas/v1/scenario.schema.json": "C",
        "apps/web/package.json": "C",
        "apps/web/src/app/layout.tsx": "C",
        "apps/web/src/lib/scenario-api.ts": "C",
        "apps/web/src/lib/architect/parcel-study.ts": "C",
        "apps/web/e2e/harness/fixture_api.py": "C",
        ".github/workflows/ci.yml": "C",
        "project-control/state.json": "C",
        "README.md": "C",
        "docs/lanes/queues/A.md": "C",
        "docs/lanes/OWNERSHIP.yaml": "C",
        "apps/web/src/components/architect/workspace/DashboardEntry.tsx": "D",
        "apps/web/src/app/property/workspace/page.tsx": "D",
        "apps/web/src/lib/format.ts": "D",
        "apps/web/e2e/connected-dashboard.spec.ts": "D",
        "docs/design/ui-cleanup/README.md": "D",
        "services/api/app/cad/dxf_writer.py": "E",
        "services/api/tests/drawings/test_x.py": "E",
        "docs/samples/cad/README.md": "E",
        "docs/lanes/status/A.md": "A",
        "docs/lanes/requests/B-1.md": "B",
        "docs/lanes/status/E.md": "E",
    }

    def test_representative_owners(self):
        for path, lane in self.CASES.items():
            with self.subTest(path=path):
                self.assertEqual(REAL.owner(path), lane)

    def test_unknown_top_level_directory_is_orphan(self):
        self.assertIsNone(REAL.owner("newtopdir/module.py"))
        self.assertEqual(clp.orphans(REAL, ["newtopdir/module.py", "README.md"]),
                         ["newtopdir/module.py"])

    def test_every_tracked_file_has_an_owner(self):
        files = clp.tracked_files()
        self.assertGreater(len(files), 1000)
        self.assertEqual(clp.orphans(REAL, files), [])

    def test_hot_files_resolve_to_lane_c(self):
        data = clp.parse_yaml_subset(clp.DEFAULT_OWNERSHIP.read_text(encoding="utf-8"))
        for glob in data["hot_files"]:
            probe = glob.replace("**", "probe/file.py")
            with self.subTest(glob=glob):
                self.assertEqual(REAL.owner(probe), "C")

    def test_malformed_ownership_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "OWNERSHIP.yaml"
            bad.write_text("lanes:\n  A:\n    name: x\nrules:\n  - lane: A\n    globs:\n"
                           "      - x/**\nintegration_branch: main\n", encoding="utf-8")
            code, out = run_main("--ownership", str(bad), "--coverage", "--files", "x/a")
            self.assertEqual(code, 2)
            self.assertIn("exactly A, B, C, D, E", out)


class BranchCheckTests(unittest.TestCase):
    def test_lane_of_branch(self):
        self.assertEqual(clp.lane_of_branch("lane-a/M5-T130-r6b-far"), "A")
        self.assertEqual(clp.lane_of_branch("LANE-B/x"), "B")
        self.assertIsNone(clp.lane_of_branch("task/M0-T163-brace-expansion"))
        self.assertIsNone(clp.lane_of_branch("lane-f/x"))
        self.assertIsNone(clp.lane_of_branch("lane-a"))
        self.assertIsNone(clp.lane_of_branch("candidate/D-024-mrl-option-b"))

    def test_lane_may_touch_its_own_files_and_status(self):
        code, out = run_main("--branch", "lane-a/x", "--files",
                             "services/api/app/rules/r.py", "docs/lanes/status/A.md",
                             "docs/lanes/requests/A-3.md")
        self.assertEqual(code, 0, out)
        self.assertIn("PASS", out)

    def test_lane_touching_hot_file_fails(self):
        code, out = run_main("--branch", "lane-a/x", "--files",
                             "services/api/app/rules/r.py", "services/api/app/main.py")
        self.assertEqual(code, 1)
        self.assertIn("services/api/app/main.py (owner: C)", out)

    def test_lane_touching_another_lanes_status_fails(self):
        code, out = run_main("--branch", "lane-d/x", "--files", "docs/lanes/status/A.md")
        self.assertEqual(code, 1)
        self.assertIn("owner: A", out)

    def test_orphan_file_on_lane_branch_fails(self):
        code, out = run_main("--branch", "lane-c/x", "--files", "newtopdir/a.py")
        self.assertEqual(code, 1)
        self.assertIn("owner: no owner", out)

    def test_non_lane_branch_is_skipped(self):
        code, out = run_main("--branch", "task/M0-T999-x", "--files", "services/api/app/main.py")
        self.assertEqual(code, 0)
        self.assertIn("SKIPPED", out)

    def test_coverage_flags_orphans(self):
        code, out = run_main("--coverage", "--files", "README.md", "newtopdir/a.py")
        self.assertEqual(code, 1)
        self.assertIn("newtopdir/a.py", out)


class GitDiffTests(unittest.TestCase):
    """changed_files() against a throwaway repository (no network, fetch=False)."""

    def _git(self, repo: Path, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                              text=True).stdout

    def test_diff_is_relative_to_merge_base(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._git(repo, "init", "-q", "-b", "base")
            self._git(repo, "config", "user.email", "t@example.invalid")
            self._git(repo, "config", "user.name", "t")
            (repo / "a.txt").write_text("1\n")
            self._git(repo, "add", "a.txt")
            self._git(repo, "commit", "-q", "-m", "base")
            self._git(repo, "switch", "-q", "-c", "lane-a/x")
            (repo / "b.txt").write_text("2\n")
            self._git(repo, "add", "b.txt")
            self._git(repo, "commit", "-q", "-m", "lane")
            # The base moves on after the branch point: its change must NOT count.
            self._git(repo, "switch", "-q", "base")
            (repo / "c.txt").write_text("3\n")
            self._git(repo, "add", "c.txt")
            self._git(repo, "commit", "-q", "-m", "later base")
            self._git(repo, "update-ref", "refs/remotes/origin/base", "HEAD")
            self._git(repo, "switch", "-q", "lane-a/x")
            saved = clp.REPO_ROOT
            clp.REPO_ROOT = repo
            try:
                self.assertEqual(clp.changed_files("base", fetch=False), ["b.txt"])
            finally:
                clp.REPO_ROOT = saved

    # PR #261: the event's base.sha was stale (the base had advanced), so diffing from it
    # counted another lane's newly merged files as this PR's changes.
    LANE_FILE = "scripts/lanes/new_tool.py"                      # lane C
    FOREIGN_FILE = "services/api/app/profile/measurement.py"     # lane B

    def _commit(self, repo: Path, rel: str, text: str, message: str) -> str:
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        self._git(repo, "add", rel)
        self._git(repo, "commit", "-q", "-m", message)
        return self._git(repo, "rev-parse", "HEAD").strip()

    def _pr_merge_repo(self, repo: Path) -> tuple[str, str, str]:
        """Base A; lane-c/x branches from A; another lane's PR then lands on the base (A -> B);
        HEAD is GitHub's merge commit of the PR head onto B (first parent B). Returns
        (A = the stale event base.sha, B = the true base, lane head)."""
        self._git(repo, "init", "-q", "-b", "base")
        self._git(repo, "config", "user.email", "t@example.invalid")
        self._git(repo, "config", "user.name", "t")
        stale = self._commit(repo, "a.txt", "1\n", "base")
        self._git(repo, "switch", "-q", "-c", "lane-c/x")
        lane_head = self._commit(repo, self.LANE_FILE, "x = 1\n", "lane")
        self._git(repo, "switch", "-q", "base")
        true_base = self._commit(repo, self.FOREIGN_FILE, "y = 1\n", "other lane's PR merged")
        self._git(repo, "switch", "-q", "--detach", "base")
        self._git(repo, "merge", "-q", "--no-ff", "-m", "Merge head into base", "lane-c/x")
        return stale, true_base, lane_head

    def _with_root(self, repo: Path):
        saved = clp.REPO_ROOT
        clp.REPO_ROOT = repo
        self.addCleanup(setattr, clp, "REPO_ROOT", saved)

    def test_pr_merge_diffs_against_the_merge_commits_first_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            stale, true_base, lane_head = self._pr_merge_repo(repo)
            self._with_root(repo)
            self.assertEqual(clp.commit_parents("HEAD"), [true_base, lane_head])
            self.assertEqual(clp.merge_first_parent(fetch=False), true_base)
            self.assertEqual(clp.changed_files_vs_merge_parent(fetch=False),
                             (true_base, [self.LANE_FILE]))
            # The defect being fixed: the stale base pulls the other lane's file in.
            stale_diff = self._git(repo, "diff", "--name-only", stale, "HEAD").split()
            self.assertIn(self.FOREIGN_FILE, stale_diff)
            code, out = run_main("--branch", "lane-c/x", "--pr-merge")
            self.assertEqual(code, 0, out)
            self.assertIn(true_base, out)
            self.assertIn("changes 1 file(s)", out)
            self.assertNotIn(self.FOREIGN_FILE, out)

    def test_base_sha_option_is_gone(self):
        # The payload's base.sha must not be usable as the diff base any more.
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            clp.main(["--branch", "lane-c/x", "--base-sha", "0" * 40])

    def test_pr_merge_fails_closed_without_a_two_parent_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._git(repo, "init", "-q", "-b", "base")
            self._git(repo, "config", "user.email", "t@example.invalid")
            self._git(repo, "config", "user.name", "t")
            self._with_root(repo)
            self._commit(repo, "a.txt", "1\n", "root")                  # 0 parents
            with self.assertRaisesRegex(RuntimeError, "0 parent"):
                clp.merge_first_parent(fetch=False)
            self._commit(repo, self.LANE_FILE, "x = 1\n", "plain")       # 1 parent
            with self.assertRaisesRegex(RuntimeError, "1 parent"):
                clp.merge_first_parent(fetch=True)
            code, out = run_main("--branch", "lane-c/x", "--pr-merge", "--fetch")
            self.assertEqual(code, 2, out)
            self.assertIn("LANE PATH CHECK ERROR", out)
            self.assertIn("not GitHub's pull_request merge commit", out)
            for name in ("o1", "o2"):                                     # octopus: 3 parents
                self._git(repo, "switch", "-q", "-c", name, "HEAD~1")
                self._commit(repo, f"{name}.txt", "o\n", name)
            self._git(repo, "switch", "-q", "base")
            self._git(repo, "merge", "-q", "-m", "octopus", "o1", "o2")
            with self.assertRaisesRegex(RuntimeError, "3 parent"):
                clp.merge_first_parent(fetch=False)

    def test_shallow_checkout_fetches_first_parent_at_depth_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dev, origin, ci = tmp_path / "dev", tmp_path / "origin.git", tmp_path / "ci"
            dev.mkdir()
            origin.mkdir()
            _stale, true_base, _head = self._pr_merge_repo(dev)
            self._git(origin, "init", "-q", "--bare", "-b", "base")
            self._git(dev, "push", "-q", str(origin), "base", "HEAD:refs/pull/1/merge")
            # The base moves on again after GitHub built the merge ref.
            self._git(dev, "switch", "-q", "base")
            self._commit(dev, "later.txt", "z\n", "later base")
            self._git(dev, "push", "-q", str(origin), "base")
            # actions/checkout: a depth-1 fetch of the merge ref, nothing else.
            ci.mkdir()
            self._git(ci, "init", "-q")
            self._git(ci, "remote", "add", "origin", origin.as_uri())
            self._git(ci, "fetch", "-q", "--no-tags", "--depth=1", "origin",
                      "+refs/pull/1/merge:refs/remotes/pull/1/merge")
            self._git(ci, "checkout", "-q", "--detach", "refs/remotes/pull/1/merge")
            self._with_root(ci)
            self.assertTrue(clp.is_shallow())
            with self.assertRaisesRegex(RuntimeError, "not present locally"):
                clp.merge_first_parent(fetch=False)
            # An unreachable origin: the fetch fails and the check fails closed.
            self._git(ci, "remote", "set-url", "origin", (tmp_path / "missing.git").as_uri())
            code, out = run_main("--branch", "lane-c/x", "--pr-merge", "--fetch")
            self.assertEqual(code, 2, out)
            self.assertIn("LANE PATH CHECK ERROR", out)
            self._git(ci, "remote", "set-url", "origin", origin.as_uri())
            self.assertEqual(clp.changed_files_vs_merge_parent(fetch=True),
                             (true_base, [self.LANE_FILE]))
            self.assertTrue(clp.is_shallow())
            for commit in ("HEAD", true_base):
                self.assertEqual(self._git(ci, "rev-list", "--count", commit).strip(), "1")

    def test_fetch_keeps_a_full_clone_full(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            origin, work = tmp_path / "origin.git", tmp_path / "work"
            origin.mkdir()
            self._git(origin, "init", "-q", "--bare", "-b", "base")
            self._git(tmp_path, "clone", "-q", str(origin), str(work))
            self._git(work, "config", "user.email", "t@example.invalid")
            self._git(work, "config", "user.name", "t")
            self._git(work, "switch", "-q", "-c", "base")
            for n in range(3):
                (work / f"f{n}.txt").write_text(f"{n}\n")
                self._git(work, "add", f"f{n}.txt")
                self._git(work, "commit", "-q", "-m", f"c{n}")
            self._git(work, "push", "-q", "origin", "base")
            base_sha = self._git(work, "rev-parse", "HEAD").strip()
            self._git(work, "switch", "-q", "-c", "lane-a/x")
            (work / "g.txt").write_text("g\n")
            self._git(work, "add", "g.txt")
            self._git(work, "commit", "-q", "-m", "lane")
            saved = clp.REPO_ROOT
            clp.REPO_ROOT = work
            try:
                self.assertEqual(clp.changed_files("base", fetch=True), ["g.txt"])
                self.assertFalse(clp.is_shallow())
                self.assertEqual(self._git(work, "rev-list", "--count", "HEAD").strip(), "4")
                self._git(work, "switch", "-q", "--detach", "base")
                self._git(work, "merge", "-q", "--no-ff", "-m", "merge", "lane-a/x")
                self.assertEqual(clp.changed_files_vs_merge_parent(fetch=True),
                                 (base_sha, ["g.txt"]))
                self.assertFalse(clp.is_shallow())
            finally:
                clp.REPO_ROOT = saved

    def test_non_c_lane_is_judged_by_the_base_ownership_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._git(repo, "init", "-q", "-b", "base")
            self._git(repo, "config", "user.email", "t@example.invalid")
            self._git(repo, "config", "user.name", "t")
            own = repo / "docs" / "lanes" / "OWNERSHIP.yaml"
            own.parent.mkdir(parents=True)
            real = clp.DEFAULT_OWNERSHIP.read_text(encoding="utf-8")
            own.write_text(real, encoding="utf-8")
            self._git(repo, "add", ".")
            self._git(repo, "commit", "-q", "-m", "base")
            base_sha = self._git(repo, "rev-parse", "HEAD").strip()
            self._git(repo, "switch", "-q", "-c", "lane-a/grab")
            # The lane edits the map to claim main.py, then touches main.py.
            own.write_text(real.replace("      - services/api/app/main.py\n", "", 1)
                           .replace("      - services/api/app/rules/**\n",
                                    "      - services/api/app/rules/**\n"
                                    "      - services/api/app/main.py\n", 1), encoding="utf-8")
            main_py = repo / "services" / "api" / "app" / "main.py"
            main_py.parent.mkdir(parents=True)
            main_py.write_text("x = 1\n")
            self._git(repo, "add", ".")
            self._git(repo, "commit", "-q", "-m", "grab")
            # GitHub's merge commit: the PR head merged onto the base (first parent base_sha).
            self._git(repo, "switch", "-q", "--detach", "base")
            self._git(repo, "merge", "-q", "--no-ff", "-m", "merge", "lane-a/grab")
            saved_root, saved_default = clp.REPO_ROOT, clp.DEFAULT_OWNERSHIP
            clp.REPO_ROOT, clp.DEFAULT_OWNERSHIP = repo, own
            try:
                self.assertEqual(clp.merge_first_parent(fetch=False), base_sha)
                code, out = run_main("--ownership", str(own), "--branch", "lane-a/grab",
                                     "--pr-merge")
            finally:
                clp.REPO_ROOT, clp.DEFAULT_OWNERSHIP = saved_root, saved_default
            self.assertEqual(code, 1, out)
            self.assertIn("services/api/app/main.py (owner: C)", out)


class SetupWorktreesTests(unittest.TestCase):
    SCRIPT = Path(__file__).resolve().parent / "setup_worktrees.sh"

    def test_script_never_pushes(self):
        code_lines = [line for line in self.SCRIPT.read_text(encoding="utf-8").splitlines()
                      if not line.lstrip().startswith("#")]
        self.assertFalse(any(re.search(r"\bpush\b", line) for line in code_lines))

    def test_creates_five_worktrees_with_ports(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            origin = tmp_path / "origin.git"
            work = tmp_path / "main"

            def git(cwd: Path, *args: str) -> None:
                subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)

            origin.mkdir()
            git(origin, "init", "-q", "--bare", "-b", "trunk")
            git(tmp_path, "clone", "-q", str(origin), str(work))
            git(work, "config", "user.email", "t@example.invalid")
            git(work, "config", "user.name", "t")
            git(work, "switch", "-q", "-c", "trunk")
            (work / "README.md").write_text("x\n")
            git(work, "add", "README.md")
            git(work, "commit", "-q", "-m", "init")
            git(work, "push", "-q", "origin", "trunk")
            before = subprocess.run(["git", "rev-parse", "trunk"], cwd=origin, check=True,
                                    capture_output=True, text=True).stdout
            result = subprocess.run(["bash", str(self.SCRIPT), "trunk"], cwd=work,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for n, lane in enumerate("abcde", start=1):
                env = (tmp_path / f"nyc-lane-{lane}" / ".env.local").read_text()
                self.assertIn(f"API_PORT=810{n}", env)
                self.assertIn(f"WEB_PORT=310{n}", env)
                self.assertIn(f"LANE_{lane.upper()}_ENABLED=true", env)
            # A second run leaves everything in place, and origin never moved.
            again = subprocess.run(["bash", str(self.SCRIPT), "trunk"], cwd=work,
                                   capture_output=True, text=True)
            self.assertEqual(again.returncode, 0, again.stderr)
            self.assertIn("left untouched", again.stdout)
            after = subprocess.run(["git", "rev-parse", "trunk"], cwd=origin, check=True,
                                   capture_output=True, text=True).stdout
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main(verbosity=1)
