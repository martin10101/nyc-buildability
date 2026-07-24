#!/usr/bin/env python3
"""Tests for the directive-compliance reminder hook (.claude/hooks/directive_reminder.py).

Stdlib-only (unittest); runnable as `python3 tools/test_directive_reminder.py` so the
control-plane CI job can execute it. Proves the correction-6 guarantees: bounded +
advisory, per-prompt minimal, never the full protocol / raw source, injection-safe
(registry text is inert data), corrupt registry fails closed VISIBLY (never silent),
zero active directives injects nothing, and a hook failure never breaks the session
(always exit 0, never a permissionDecision).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HOOK = ROOT / ".claude" / "hooks" / "directive_reminder.py"

PER_PROMPT_CAP = 400
SESSION_CAP = 1400
RAW_SOURCE_SENTINEL = "STANDING-DIRECTIVE-COMPLIANCE-PROTOCOL-RAW-SENTINEL"


def run_hook(payload: dict | str, registry: Path | None):
    env = dict(os.environ)
    if registry is not None:
        env["CLAUDE_DIRECTIVE_REGISTRY"] = str(registry)
    data = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run([sys.executable, str(HOOK)], input=data,
                          capture_output=True, text=True, env=env)


def make_registry(tmp: Path, directives) -> Path:
    """directives: list of (id, title, status). Also drops a source file carrying a raw
    sentinel so tests can prove the hook never emits raw source text."""
    reg = tmp / "directives"
    reg.mkdir(parents=True, exist_ok=True)
    entries = []
    for did, title, status in directives:
        ddir = reg / f"{did}-x"
        ddir.mkdir(exist_ok=True)
        (ddir / "source-001.md").write_text(RAW_SOURCE_SENTINEL + "\n", encoding="utf-8")
        entries.append({"directive_id": did, "slug": "x", "title": title,
                        "status": status, "issued_at": "2026-07-23",
                        "manifest": f"{did}-x/manifest.json"})
    (reg / "index.json").write_text(json.dumps({
        "schema": "directive_index/v1", "version": 1, "directives": entries,
        "updated_at": "2026-07-23T00:00:00+00:00"}), encoding="utf-8")
    return reg


def context(out: str) -> str:
    if not out.strip():
        return ""
    return json.loads(out)["hookSpecificOutput"]["additionalContext"]


class ReminderHookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="reminder-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_session_start_emits_bounded_active_pointer(self):
        reg = make_registry(self.tmp, [("D-001", "Owner Directive Compliance", "active")])
        r = run_hook({"hook_event_name": "SessionStart", "source": "startup"}, reg)
        self.assertEqual(r.returncode, 0)
        ctx = context(r.stdout)
        self.assertIn("D-001", ctx)
        self.assertIn("/directive-compliance", ctx)
        self.assertLessEqual(len(ctx), SESSION_CAP)
        self.assertNotIn("permissionDecision", r.stdout)

    def test_user_prompt_is_minimal_and_omits_the_list(self):
        reg = make_registry(self.tmp, [("D-001", "Owner Directive Compliance", "active")])
        r = run_hook({"hook_event_name": "UserPromptSubmit"}, reg)
        self.assertEqual(r.returncode, 0)
        ctx = context(r.stdout)
        self.assertLessEqual(len(ctx), PER_PROMPT_CAP)
        self.assertIn("/directive-compliance", ctx)
        # per-prompt must NOT repeat the full active-directive list
        self.assertNotIn("Active owner directives", ctx)

    def test_compaction_restores_short_pointer(self):
        reg = make_registry(self.tmp, [("D-001", "Owner Directive Compliance", "active")])
        r = run_hook({"hook_event_name": "SessionStart", "source": "compact"}, reg)
        self.assertEqual(r.returncode, 0)
        ctx = context(r.stdout)
        self.assertIn("D-001", ctx)
        self.assertLessEqual(len(ctx), SESSION_CAP)

    def test_zero_active_directives_injects_nothing(self):
        reg = make_registry(self.tmp, [("D-001", "Superseded thing", "superseded")])
        r = run_hook({"hook_event_name": "SessionStart", "source": "startup"}, reg)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")

    def test_missing_registry_is_silent(self):
        r = run_hook({"hook_event_name": "SessionStart"}, self.tmp / "nonexistent")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")

    def test_corrupt_registry_warns_visibly_not_silently(self):
        reg = self.tmp / "directives"
        reg.mkdir(parents=True)
        (reg / "index.json").write_text("{ this is not valid json", encoding="utf-8")
        r = run_hook({"hook_event_name": "SessionStart"}, reg)
        self.assertEqual(r.returncode, 0)
        ctx = context(r.stdout)
        self.assertIn("WARNING", ctx)
        self.assertTrue("corrupt" in ctx.lower() or "unreadable" in ctx.lower())

    def test_never_emits_raw_source_text(self):
        reg = make_registry(self.tmp, [("D-001", "Owner Directive Compliance", "active")])
        for ev in ("SessionStart", "UserPromptSubmit"):
            r = run_hook({"hook_event_name": ev}, reg)
            self.assertNotIn(RAW_SOURCE_SENTINEL, r.stdout)

    def test_injection_safe_sanitizes_title(self):
        reg = make_registry(self.tmp, [
            ("D-001", "legit; rm -rf / $(whoami) `id` <script>", "active")])
        r = run_hook({"hook_event_name": "SessionStart"}, reg)
        self.assertEqual(r.returncode, 0)
        ctx = context(r.stdout)
        for bad in (";", "$(", "`", "<script>"):
            self.assertNotIn(bad, ctx)
        self.assertNotIn("permissionDecision", r.stdout)

    def test_size_cap_with_many_long_directives(self):
        many = [(f"D-{i:03d}", "A very long directive title " * 5, "active")
                for i in range(1, 20)]
        reg = make_registry(self.tmp, many)
        r = run_hook({"hook_event_name": "SessionStart"}, reg)
        self.assertEqual(r.returncode, 0)
        self.assertLessEqual(len(context(r.stdout)), SESSION_CAP)

    def test_hook_failure_malformed_stdin_never_breaks_session(self):
        reg = make_registry(self.tmp, [("D-001", "x", "active")])
        r = run_hook("this is not json at all", reg)
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("permissionDecision", r.stdout)
        # still valid JSON or empty (never a crash / traceback on stdout)
        if r.stdout.strip():
            json.loads(r.stdout)

    def test_never_blocks_or_returns_permission_decision(self):
        reg = make_registry(self.tmp, [("D-001", "x", "active")])
        for ev in ("SessionStart", "UserPromptSubmit", "SomethingElse"):
            r = run_hook({"hook_event_name": ev}, reg)
            self.assertEqual(r.returncode, 0)
            self.assertNotIn("permissionDecision", r.stdout)
            self.assertNotIn("\"deny\"", r.stdout)


class SettingsWiringTests(unittest.TestCase):
    def test_settings_json_valid_and_hooks_wired(self):
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        hooks = settings.get("hooks", {})
        # The two existing PreToolUse guards are still present and untouched.
        pre = json.dumps(hooks.get("PreToolUse", []))
        self.assertIn("agent_dispatch_guard.py", pre)
        self.assertIn("readonly_agent_guard.py", pre)
        # The reminder is wired on SessionStart AND UserPromptSubmit (new sibling keys).
        for ev in ("SessionStart", "UserPromptSubmit"):
            self.assertIn("directive_reminder.py", json.dumps(hooks.get(ev, [])),
                          f"reminder must be wired on {ev}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
