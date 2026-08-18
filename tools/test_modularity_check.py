#!/usr/bin/env python3
"""M0-T073 proof tests for the deterministic modularity checker (D-017-R113).

Covers the owner's seven required proofs plus integrity edges. Deterministic,
stdlib-only; every fixture is a real temporary git index so the production
`git ls-files` selection path is exercised.
"""
from __future__ import annotations

import contextlib
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import modularity_check as mc  # noqa: E402

TODAY = "2026-08-18"


def module_text(lines: int) -> str:
    body = "\n".join(f"VALUE_{i} = {i}" for i in range(lines - 1))
    return f'"""One focused module."""\n{body}\n'


class RepoCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self._tmp.name) / "repo"
        (self.repo / "services" / "api").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True,
                       capture_output=True)
        self.baseline = pathlib.Path(self._tmp.name) / "baseline.json"
        self.exceptions = pathlib.Path(self._tmp.name) / "exceptions.json"
        self.addCleanup(self._tmp.cleanup)

    def add(self, rel: str, text: str) -> pathlib.Path:
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        subprocess.run(["git", "-C", str(self.repo), "add", rel], check=True,
                       capture_output=True)
        return path

    def write_baseline(self, entries: dict[str, int], version: int = 1) -> None:
        doc = {"version": version, "files": dict(sorted(entries.items())),
               "baseline_digest": mc.baseline_digest(entries, version)}
        self.baseline.write_text(json.dumps(doc, indent=1) + "\n",
                                 encoding="utf-8", newline="\n")

    def write_exceptions(self, entries: list[dict]) -> None:
        self.exceptions.write_text(
            json.dumps({"exceptions": entries}, indent=1) + "\n",
            encoding="utf-8", newline="\n")

    def run_main(self, *argv: str) -> tuple[int, dict]:
        buf_out, buf_err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            code = mc.main([*argv, "--repo", str(self.repo),
                            "--baseline", str(self.baseline),
                            "--exceptions", str(self.exceptions),
                            "--today", TODAY, "--json"])
        body = buf_out.getvalue().strip() or buf_err.getvalue().strip()
        return code, json.loads(body)

    def file_exception(self, path: str, max_lines: int, *,
                       expires: str = "2026-10-31", **overrides) -> dict:
        entry = {"kind": "file", "path": path, "max_lines": max_lines,
                 "owner": "owner", "reason": "reviewed cohesion justification",
                 "review_evidence": "PR #999 G3 review", "expires": expires}
        entry.update(overrides)
        return entry


class ProofTests(RepoCase):
    def test_1_normal_focused_module_passes(self) -> None:
        self.add("services/api/focused.py", module_text(300))
        self.write_baseline({})
        code, payload = self.run_main("--check")
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["failures"], [])

    def test_2_new_unjustifiably_oversized_module_fails(self) -> None:
        self.add("services/api/giant.py", module_text(1100))
        self.write_baseline({})
        code, payload = self.run_main("--check")
        self.assertEqual(code, 1)
        kinds = {f["kind"]: f for f in payload["failures"]}
        self.assertIn("new_oversized", kinds)
        self.assertEqual(kinds["new_oversized"]["path"], "services/api/giant.py")

    def test_3_growth_of_grandfathered_oversized_file_fails(self) -> None:
        self.add("services/api/legacy.py", module_text(900))
        self.write_baseline({"services/api/legacy.py": 800})  # limit 800+80=880
        code, payload = self.run_main("--check")
        self.assertEqual(code, 1)
        kinds = {f["kind"] for f in payload["failures"]}
        self.assertIn("baseline_growth", kinds)

    def test_3b_ungrown_grandfathered_file_passes(self) -> None:
        self.add("services/api/legacy.py", module_text(850))
        self.write_baseline({"services/api/legacy.py": 800})  # within 880
        code, payload = self.run_main("--check")
        self.assertEqual(code, 0, payload)

    def test_4_excluded_generated_file_does_not_fail(self) -> None:
        self.add("packages/contracts/generated/big.py", module_text(3000))
        self.add("services/api/migrations/0001_huge.py", module_text(3000))
        self.add("apps/web/src/lib/data.test.ts", "export const x = 1\n" * 2000)
        self.write_baseline({})
        code, payload = self.run_main("--check")
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["selected_files"], 0)

    def test_5_valid_exception_is_narrow_and_temporary(self) -> None:
        self.add("services/api/justified.py", module_text(1100))
        self.write_baseline({})
        self.write_exceptions([self.file_exception("services/api/justified.py", 1200)])
        code, payload = self.run_main("--check")
        self.assertEqual(code, 0, payload)
        # ...and the ceiling is real: growth past max_lines fails.
        self.add("services/api/justified.py", module_text(1300))
        code, payload = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("exception_exceeded", {f["kind"] for f in payload["failures"]})

    def test_6_expired_exception_fails(self) -> None:
        self.add("services/api/justified.py", module_text(1100))
        self.write_baseline({})
        self.write_exceptions([self.file_exception("services/api/justified.py", 1200,
                                                   expires="2026-08-17")])
        code, payload = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("EXPIRED", payload["error"])

    def test_6b_broadened_exception_fails(self) -> None:
        self.add("services/api/justified.py", module_text(1100))
        self.write_baseline({})
        self.write_exceptions([self.file_exception("services/api/*.py", 1200)])
        code, payload = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("broadened", payload["error"])

    def test_6c_incorrectly_targeted_exception_fails(self) -> None:
        self.add("services/api/real.py", module_text(100))
        self.write_baseline({})
        self.write_exceptions([self.file_exception("services/api/no_such.py", 1200)])
        code, payload = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("not a selected handwritten production file", payload["error"])

    def test_7_regeneration_cannot_silently_erase_debt(self) -> None:
        self.add("services/api/legacy.py", module_text(1500))
        self.write_baseline({"services/api/legacy.py": 1400})
        # (a) no approval -> refused
        code, payload = self.run_main("--regenerate-baseline",
                                      "--approval-id", "nope")
        self.assertEqual(code, 1)
        self.assertIn("cannot be casually regenerated", payload["error"])
        # (b) with approval: the still-oversized entry PERSISTS and never grows
        self.write_exceptions([{
            "kind": "baseline-regeneration", "approval_id": "APPROVED-1",
            "for_version": 2,
            "owner": "owner", "reason": "reviewed", "review_evidence": "PR #999",
            "expires": "2026-09-30"}])
        code, payload = self.run_main("--regenerate-baseline",
                                      "--approval-id", "APPROVED-1")
        self.assertEqual(code, 0, payload)
        regenerated = json.loads(self.baseline.read_text(encoding="utf-8"))
        self.assertEqual(regenerated["files"]["services/api/legacy.py"], 1400,
                         "regeneration must carry debt forward at the recorded "
                         "(smaller) size, not launder growth in")
        # (c) an EDITED baseline (digest mismatch) fails the check closed
        regenerated["files"]["services/api/legacy.py"] = 99999
        self.baseline.write_text(json.dumps(regenerated), encoding="utf-8",
                                 newline="\n")
        code, payload = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("baseline_digest mismatch", payload["error"])

    def test_7b_expired_regeneration_approval_is_refused_but_inert_for_check(self) -> None:
        self.add("services/api/ok.py", module_text(100))
        self.write_baseline({})
        self.write_exceptions([{
            "kind": "baseline-regeneration", "approval_id": "OLD-1",
            "for_version": 1,
            "owner": "owner", "reason": "used up", "review_evidence": "PR #900",
            "expires": "2026-01-01"}])
        code, payload = self.run_main("--regenerate-baseline",
                                      "--approval-id", "OLD-1")
        self.assertEqual(code, 1)
        code, payload = self.run_main("--check")
        self.assertEqual(code, 0, payload)  # inert for --check

    def test_6d_malformed_exceptions_fail_closed(self) -> None:
        """G3-F6: malformed entries are structured CheckError refusals."""
        self.add("services/api/justified.py", module_text(1100))
        self.write_baseline({})
        cases = [
            ([{"kind": "file", "path": "services/api/justified.py",
               "max_lines": 1150, "reason": "r", "review_evidence": "e",
               "expires": "2026-10-01"}], "missing required field 'owner'"),
            ([self.file_exception("services/api/justified.py", 1150,
                                  expires="31-12-2026")], "bad expires date"),
            ([{**self.file_exception("services/api/justified.py", 1150),
               "max_lines": -5}], "positive int max_lines"),
            (["just a string"], "entry must be an object"),
        ]
        for entries, needle in cases:
            self.write_exceptions(entries)
            code, payload = self.run_main("--check")
            self.assertEqual(code, 1, payload)
            self.assertIn(needle, payload["error"])

    def test_6e_duplicate_exception_fails_closed(self) -> None:
        self.add("services/api/justified.py", module_text(1100))
        self.write_baseline({})
        self.write_exceptions([
            self.file_exception("services/api/justified.py", 1150),
            self.file_exception("services/api/justified.py", 1180),
        ])
        code, payload = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("duplicate exception", payload["error"])

    def test_6f_horizon_and_breadth_bounds(self) -> None:
        """G5 SEC-MINOR-4: 'temporary' and 'narrow' are machine-enforced."""
        self.add("services/api/justified.py", module_text(1100))
        self.write_baseline({})
        self.write_exceptions([self.file_exception("services/api/justified.py",
                                                   1150, expires="2027-08-18")])
        code, payload = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("temporary horizon", payload["error"])
        self.write_exceptions([self.file_exception("services/api/justified.py",
                                                   10 ** 9)])
        code, payload = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("exception_too_broad",
                      {f["kind"] for f in payload["failures"]})

    def test_7c_regeneration_approval_is_single_use(self) -> None:
        """G5 SEC-MINOR-2: an approval binds to the ONE version it produces."""
        self.add("services/api/legacy.py", module_text(1500))
        self.write_exceptions([{
            "kind": "baseline-regeneration", "approval_id": "ONCE-1",
            "for_version": 1, "owner": "owner", "reason": "adoption",
            "review_evidence": "PR #999", "expires": "2026-09-30"}])
        code, payload = self.run_main("--regenerate-baseline",
                                      "--approval-id", "ONCE-1")
        self.assertEqual(code, 0, payload)
        # A second regeneration would produce v2; the v1-bound approval refuses.
        code, payload = self.run_main("--regenerate-baseline",
                                      "--approval-id", "ONCE-1")
        self.assertEqual(code, 1)
        self.assertIn("bound to version 2", payload["error"])

    def test_ts_inline_block_comments_are_counted_correctly(self) -> None:
        """G4-C2: code sharing a line with a block comment still counts."""
        block = ("/* start\n"
                 "   still block */ const b = 2;\n"
                 "/* one */ const c = 3;\n"
                 "const d = 4; // tail comment\n"
                 "// only comment\n"
                 "/* whole-line comment */\n")
        self.add("apps/web/src/lib/counted.ts", block * 400)
        self.write_baseline({})
        code, payload = self.run_main("--check")
        # 3 counted lines per block x 400 = 1200 SLOC -> new_oversized
        self.assertEqual(code, 1, payload)
        kinds = {f["kind"]: f for f in payload["failures"]}
        self.assertIn("new_oversized", kinds)
        self.assertEqual(kinds["new_oversized"]["sloc"], 1200)

    def test_r1_unterminated_block_scan_warns_not_silently_undercounts(self) -> None:
        """G3-R1: /* inside a string literal is surfaced, not silently swallowed."""
        # A real-world Vite pattern: /* is inside a string, no */ follows.
        self.add("apps/web/src/lib/glob.ts",
                 'const mods = import.meta.glob("./modules/*.ts");\n'
                 + "export const x = 1;\n" * 700)
        self.write_baseline({})
        code, payload = self.run_main("--check")
        kinds = {w["kind"] for w in payload["warnings"]}
        self.assertIn("sloc_scan_uncertain", kinds)

    def test_r2_refactoring_a_file_down_does_not_trip_too_broad(self) -> None:
        """G3-R2: exception breadth is judged against the recorded review size,
        so shrinking a file toward its split target never breaks CI."""
        self.add("services/api/big.py", module_text(1100))
        self.write_baseline({})
        # Reviewed when the file was 1100; ceiling 1200 = one growth step.
        exc = self.file_exception("services/api/big.py", 1200)
        exc["baseline_sloc"] = 1100
        self.write_exceptions([exc])
        self.assertEqual(self.run_main("--check")[0], 0)
        # Refactor it DOWN to 700 - must still pass, not trip exception_too_broad.
        self.add("services/api/big.py", module_text(700))
        code, payload = self.run_main("--check")
        self.assertEqual(code, 0, payload)
        self.assertNotIn("exception_too_broad",
                         {f["kind"] for f in payload["failures"]})

    def test_missing_baseline_fails_closed(self) -> None:
        self.add("services/api/ok.py", module_text(100))
        code, payload = self.run_main("--check")
        self.assertEqual(code, 1)
        self.assertIn("baseline missing", payload["error"])

    def test_warnings_do_not_fail_and_report_never_fails(self) -> None:
        self.add("services/api/warm.py", module_text(700))
        self.write_baseline({})
        code, payload = self.run_main("--check")
        self.assertEqual(code, 0, payload)
        self.assertIn("review_signal", {w["kind"] for w in payload["warnings"]})
        self.add("services/api/giant.py", module_text(1100))
        code, payload = self.run_main("--report")
        self.assertEqual(code, 0)  # report mode never gates...
        self.assertTrue(payload["failures"],
                        "...but it must still SURFACE the violation (G3-F10)")

    def test_output_is_deterministic(self) -> None:
        self.add("services/api/b.py", module_text(650))
        self.add("services/api/a.py", module_text(700))
        self.write_baseline({})
        _, first = self.run_main("--check")
        _, second = self.run_main("--check")
        self.assertEqual(first, second)
        paths = [w["path"] for w in first["warnings"]]
        self.assertEqual(paths, sorted(paths))

    def test_sloc_ignores_blank_and_comment_only_lines(self) -> None:
        text = '"""Doc."""\n' + "# comment\n\n" * 500 + "X = 1\n"
        self.add("services/api/comments.py", text)
        self.write_baseline({})
        code, payload = self.run_main("--check")
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["warnings"], [])  # ~502 physical, ~2 SLOC


class RealRepoTests(unittest.TestCase):
    """The committed baseline and exceptions verify against the real repository."""

    def test_committed_check_passes(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(pathlib.Path(__file__).parent / "modularity_check.py"),
             "--check", "--json"],
            capture_output=True, text=True, timeout=300)
        payload = json.loads(proc.stdout or proc.stderr)
        self.assertEqual(proc.returncode, 0,
                         [f for f in payload.get("failures", [])] or payload.get("error"))

    def test_committed_baseline_integrity(self) -> None:
        version, entries = mc.load_baseline(mc.BASELINE_PATH)
        self.assertGreaterEqual(version, 1)
        self.assertTrue(entries, "the initial legacy-debt register must not be empty")
        self.assertIn("tools/agent_supervisor/cli.py", entries)


if __name__ == "__main__":
    unittest.main()
