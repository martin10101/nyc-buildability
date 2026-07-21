#!/usr/bin/env python3
"""Tests for tools/context_budget_check.py. Stdlib unittest only (thin-client / CI safe)."""
from __future__ import annotations

import contextlib
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
import context_budget_check as m  # noqa: E402


def _run_main(root: pathlib.Path, cfg: dict) -> int:
    """Point the checker at a synthetic tree and run it, swallowing stdout."""
    cfg_path = root / "cfg.json"
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
    old = m.ROOT
    m.ROOT = root
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return m.main(["--config", str(cfg_path)])
    finally:
        m.ROOT = old


BASE_CFG = {
    "eager_token_budget": 6000,
    "handoff_token_budget": 4000,
    "handoff_file": "docs/SESSION_HANDOFF.md",
    "retired_markers": ["retired", "superseded"],
    "retired_section_min_chars": 400,
    "archive_exempt_substring": "docs/archive/",
    "historical_required": [],
    "historical_marker_regex": "HISTORICAL|ARCHIVED",
    "historical_marker_scan_lines": 15,
    "board_status_header_regex": r"\|\s*status\s*\|",
    "board_task_id_regex": r"\bM\d+-T\d+\b",
    "board_min_task_rows": 8,
    "board_scan_globs": ["docs/*.md", "*.md"],
    "board_allowlist": [],
}


def _mktree(root: pathlib.Path, claude="# CLAUDE\n\njust rules.\n", rules=None, handoff="short\n"):
    (root / ".claude" / "rules").mkdir(parents=True, exist_ok=True)
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "CLAUDE.md").write_text(claude, encoding="utf-8")
    (root / "docs" / "SESSION_HANDOFF.md").write_text(handoff, encoding="utf-8")
    for name, body in (rules or {}).items():
        (root / ".claude" / "rules" / name).write_text(body, encoding="utf-8")


class UnitHelpers(unittest.TestCase):
    def test_tokens(self):
        self.assertEqual(m.tokens("abcd"), 1)
        self.assertEqual(m.tokens("abcde"), 2)

    def test_is_unconditional(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            scoped = p / "a.md"
            scoped.write_text("---\npaths:\n  - \"apps/web/**\"\n---\nx\n", encoding="utf-8")
            uncond = p / "b.md"
            uncond.write_text("# just text\nno frontmatter\n", encoding="utf-8")
            self.assertFalse(m.is_unconditional_rule(scoped))
            self.assertTrue(m.is_unconditional_rule(uncond))

    def test_split_sections(self):
        secs = m.split_sections("intro\n# A\na1\n## B\nb1\n")
        self.assertEqual(len(secs), 3)


class Checks(unittest.TestCase):
    def test_real_tree_passes(self):
        r = subprocess.run(
            [sys.executable, str(HERE / "context_budget_check.py")],
            capture_output=True, text=True, cwd=str(REPO),
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_clean_synthetic_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            _mktree(root, rules={"hold.md": "# Active hold\ndo X\n"})
            self.assertEqual(_run_main(root, dict(BASE_CFG)), 0)

    def test_budget_exceeded(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            big = "# Big rule\n" + ("padding line of text " * 2000)  # ~ tens of thousands of chars
            _mktree(root, rules={"big.md": big})
            self.assertEqual(_run_main(root, dict(BASE_CFG)), 1)

    def test_at_import_counted(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "BIG.md").parent.mkdir(parents=True, exist_ok=True)
            _mktree(root, claude="# CLAUDE\n\n- @BIG.md\n")
            (root / "BIG.md").write_text("padding " * 5000, encoding="utf-8")  # huge import
            self.assertEqual(_run_main(root, dict(BASE_CFG)), 1)

    def test_retired_section_flagged_without_archive_link(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            retired = "# Rule\n\n## Old thing RETIRED\n" + ("this is retired narrative. " * 40)
            _mktree(root, rules={"hold.md": retired})
            self.assertEqual(_run_main(root, dict(BASE_CFG)), 1)

    def test_retired_section_ok_with_archive_link(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            retired = (
                "# Rule\n\n## Old thing retired\nSee docs/archive/old.md for the full retired text. "
                + ("short. " * 40)
            )
            _mktree(root, rules={"hold.md": retired})
            self.assertEqual(_run_main(root, dict(BASE_CFG)), 0)

    def test_missing_historical_marker_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            _mktree(root, rules={"hold.md": "# hold\nX\n"})
            (root / "docs" / "STALE.md").write_text("# Stale board\ncurrent status here\n", encoding="utf-8")
            cfg = dict(BASE_CFG)
            cfg["historical_required"] = ["docs/STALE.md"]
            self.assertEqual(_run_main(root, cfg), 1)
            # add the marker -> passes
            (root / "docs" / "STALE.md").write_text("# Stale board\n> HISTORICAL — do not use\n", encoding="utf-8")
            self.assertEqual(_run_main(root, cfg), 0)

    def test_unaccounted_board_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            _mktree(root, rules={"hold.md": "# hold\nX\n"})
            rows = "\n".join(f"| M0-T{i:03d} | accepted |" for i in range(10))
            board = "# Board\n\n| Task | Status |\n|---|---|\n" + rows + "\n"
            (root / "docs" / "BOARD.md").write_text(board, encoding="utf-8")
            self.assertEqual(_run_main(root, dict(BASE_CFG)), 1)
            # allowlisting it -> passes
            cfg = dict(BASE_CFG)
            cfg["board_allowlist"] = ["docs/BOARD.md"]
            self.assertEqual(_run_main(root, cfg), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
