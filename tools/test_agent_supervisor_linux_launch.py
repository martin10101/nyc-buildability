#!/usr/bin/env python3
"""M0-T166 (D-091 T2): Linux launcher + bash shell-routing harness + the three
M0-T165 call-site wirings.

Every packet acceptance scenario is proven here with NO live provider call: the
launcher is driven through injected fake gate/start commands and a fake claude
binary, and the bare-probe env wiring is proven by capturing the env handed to a
patched `subprocess.run` (the real executable is never launched). The bash harness
and its mutants run as real `bash` processes (the discipline they pin is a bash
fact), but they only run `python3 -c 'sys.exit(...)'`, never a provider.

Scenario map:
  * primary  -> BashHarnessTests.test_harness_passes_on_this_server
  * boundary -> BashHarnessTests.test_each_mutant_is_detected
  * missing  -> LauncherFailClosedTests.test_missing_claude_binary / _unset_required_env
  * failure  -> LauncherGateTests (gate refuses; never pushes/merges/starts a live run)
  * wiring   -> LaunchPathSelectionTests + DoctorPostureWiringTests + BareProbeEnvTests
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from tools.agent_supervisor import (
    capability_probe,
    launch_seam,
    native_runtime,
    os_acl,
)

HERE = Path(__file__).resolve().parent
LINUX_DIR = HERE / "agent_supervisor" / "linux"
LAUNCHER = LINUX_DIR / "launch.sh"
SYSTEMD_TEMPLATE = LINUX_DIR / "nyc-supervisor.service.template"
SH_TESTS = LINUX_DIR / "sh_tests"
RUN_SH_TESTS = SH_TESTS / "run_sh_tests.sh"
MUTANTS = SH_TESTS / "mutants"


def _fake_claude(dir_path: Path) -> Path:
    """An executable stand-in for the claude binary (never a provider)."""
    exe = dir_path / "claude"
    exe.write_text("#!/bin/sh\necho fake-claude\n", encoding="utf-8")
    exe.chmod(0o755)
    return exe


def _run_launcher(env_overrides: dict[str, str]) -> subprocess.CompletedProcess:
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
    env.update(env_overrides)
    return subprocess.run(  # noqa: S603 - fixed argv head, injected fakes only
        ["bash", str(LAUNCHER)], env=env, capture_output=True, text=True,
        timeout=60, check=False)


# --------------------------------------------------------------------------
# primary + boundary: the bash shell-routing harness
# --------------------------------------------------------------------------
class BashHarnessTests(unittest.TestCase):
    def test_harness_passes_on_this_server(self) -> None:
        """primary: the bash harness runs the same shell-routing cases as
        ps_tests (raw-exit discipline + mutant detection + doc tooth) and passes."""
        for name in ("harness.sh", "run_sh_tests.sh", "test_raw_exit.sh",
                     "test_mutants_detected.sh", "test_doc_check.sh"):
            self.assertTrue((SH_TESTS / name).exists(), f"missing {name}")
        proc = subprocess.run(  # noqa: S603
            ["bash", str(RUN_SH_TESTS)], capture_output=True, text=True,
            timeout=120, check=False)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("test file(s) passed", proc.stdout)

    def _mutant_exit(self, name: str) -> int:
        return subprocess.run(  # noqa: S603
            ["bash", str(MUTANTS / name)], capture_output=True, text=True,
            timeout=60, check=False).returncode

    def test_each_mutant_is_detected(self) -> None:
        """boundary: each mutant loses or fakes the raw 7 (the harness goes red
        if it used a mutant's discipline), and the mutant-detection test is green."""
        # The lie each mutant tells (proving the real harness rule is load-bearing).
        self.assertEqual(self._mutant_exit("mutant_pipe_tee.sh"), 0)
        self.assertEqual(self._mutant_exit("mutant_dollar_q.sh"), 0)
        self.assertEqual(self._mutant_exit("mutant_grep_pipe.sh"), 1)
        detect = subprocess.run(  # noqa: S603
            ["bash", str(SH_TESTS / "test_mutants_detected.sh")],
            capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(detect.returncode, 0, detect.stdout + detect.stderr)
        self.assertNotIn("ASSERT-FAIL", detect.stdout)

    def test_harness_fails_closed_on_a_missing_command(self) -> None:
        """A command that never launches has NO verdict and is never ok."""
        proc = subprocess.run(  # noqa: S603
            ["bash", str(SH_TESTS / "test_raw_exit.sh")],
            capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("no_exit_code_fail_closed", (SH_TESTS / "harness.sh").read_text())


# --------------------------------------------------------------------------
# missing/ambiguous: the launcher fails closed before any provider contact
# --------------------------------------------------------------------------
class LauncherFailClosedTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.recorder = self.tmp / "started"
        self.start_cmd = f"touch {self.recorder}"

    def test_missing_claude_binary_fails_closed(self) -> None:
        proc = _run_launcher({
            "NYC_SUP_CLAUDE_BIN": str(self.tmp / "no-such-claude"),
            "NYC_SUP_GATE_CMD": "true",
            "NYC_SUP_START_CMD": self.start_cmd})
        self.assertEqual(proc.returncode, 3, proc.stderr)
        self.assertFalse(self.recorder.exists(),
                         "the start command must not run when the binary is missing")
        self.assertIn("failing closed before any provider contact", proc.stderr)

    def test_unset_required_env_fails_closed(self) -> None:
        exe = _fake_claude(self.tmp)
        proc = _run_launcher({
            "NYC_SUP_CLAUDE_BIN": str(exe),
            "NYC_SUP_GATE_CMD": "true",
            "NYC_SUP_START_CMD": self.start_cmd,
            "NYC_SUP_REQUIRED_ENV": "NYC_SUP_TEST_TOKEN"})  # token deliberately unset
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertFalse(self.recorder.exists(),
                         "the start command must not run when a required env is unset")
        self.assertIn("NYC_SUP_TEST_TOKEN", proc.stderr)


# --------------------------------------------------------------------------
# failure: the launcher refuses when the start gate refuses, and never pushes,
# merges, or starts a live run
# --------------------------------------------------------------------------
class LauncherGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.exe = _fake_claude(self.tmp)
        self.recorder = self.tmp / "started"
        self.start_cmd = f"touch {self.recorder}"

    def test_launcher_refuses_when_gate_refuses(self) -> None:
        proc = _run_launcher({
            "NYC_SUP_CLAUDE_BIN": str(self.exe),
            "NYC_SUP_GATE_CMD": "false",  # the start gate refuses
            "NYC_SUP_START_CMD": self.start_cmd})
        self.assertEqual(proc.returncode, 5, proc.stderr)
        self.assertFalse(self.recorder.exists(),
                         "a refused gate must NOT reach the start command")
        self.assertIn("the start gate refused", proc.stderr)

    def test_launcher_starts_only_through_a_passing_gate(self) -> None:
        proc = _run_launcher({
            "NYC_SUP_CLAUDE_BIN": str(self.exe),
            "NYC_SUP_GATE_CMD": "true",  # the start gate passes
            "NYC_SUP_START_CMD": self.start_cmd})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(self.recorder.exists(),
                        "a passing gate must reach the injected start command")

    def test_launcher_has_no_push_merge_or_live_run(self) -> None:
        """The launcher adds no git push/merge and no live run of its own: no
        executable (non-comment) line names git, push, or merge."""
        body = LAUNCHER.read_text(encoding="utf-8")
        exec_lines = [ln for ln in body.splitlines()
                      if ln.strip() and not ln.lstrip().startswith("#")]
        joined = "\n".join(exec_lines)
        for forbidden in ("git ", "push", "merge"):
            self.assertNotIn(forbidden, joined,
                             f"the launcher must not contain {forbidden!r}")

    def test_systemd_unit_is_an_uninstalled_template(self) -> None:
        text = SYSTEMD_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("TEMPLATE", text)
        self.assertIn("Restart=no", text)
        # No actual [Install] SECTION header (comment prose may mention it), so a
        # stray `systemctl enable` has no target.
        headers = [ln.strip() for ln in text.splitlines()
                   if ln.strip() and not ln.lstrip().startswith("#")]
        self.assertNotIn("[Install]", headers,
                         "a template with no [Install] section cannot be auto-enabled")
        self.assertIn("DISABLE_AUTOUPDATER=1", text)


# --------------------------------------------------------------------------
# wiring: launch_seam platform selection
# --------------------------------------------------------------------------
class LaunchPathSelectionTests(unittest.TestCase):
    def test_posix_selects_the_bash_launch_path(self) -> None:
        sel = launch_seam.select_launch_path("posix")
        self.assertEqual(sel.platform, "posix")
        self.assertEqual(sel.launcher, launch_seam.POSIX_LAUNCHER)
        self.assertEqual(sel.systemd_unit_template,
                         launch_seam.POSIX_SYSTEMD_UNIT_TEMPLATE)
        self.assertEqual(sel.shell_routing_harness,
                         launch_seam.POSIX_SHELL_ROUTING_HARNESS)
        repo_root = HERE.parent
        for rel in (sel.launcher, sel.systemd_unit_template, sel.shell_routing_harness):
            self.assertTrue((repo_root / rel).exists(), rel)

    def test_windows_keeps_the_powershell_path_with_no_systemd(self) -> None:
        sel = launch_seam.select_launch_path("nt")
        self.assertEqual(sel.platform, "windows")
        self.assertEqual(sel.launcher, launch_seam.WINDOWS_LAUNCH_RUNBOOK)
        self.assertEqual(sel.shell_routing_harness,
                         launch_seam.WINDOWS_SHELL_ROUTING_HARNESS)
        self.assertEqual(sel.systemd_unit_template, "")


# --------------------------------------------------------------------------
# wiring: cli doctor posture uses the cross-platform ACL verdict
# --------------------------------------------------------------------------
class DoctorPostureWiringTests(unittest.TestCase):
    def test_verdict_dispatches_windows_to_the_windows_entry(self) -> None:
        sentinel = object()
        with mock.patch.object(os_acl.os, "name", "nt"), \
             mock.patch.object(os_acl, "evaluate_controller_config_acl",
                               return_value=sentinel) as win:
            got = os_acl.controller_config_acl_verdict("C:/x/config.toml")
        self.assertIs(got, sentinel)
        win.assert_called_once()

    def test_verdict_dispatches_posix_to_posix_acl(self) -> None:
        from tools.agent_supervisor import posix_acl
        sentinel = object()
        with mock.patch.object(os_acl.os, "name", "posix"), \
             mock.patch.object(posix_acl, "evaluate_controller_config_acl",
                               return_value=sentinel) as px:
            got = os_acl.controller_config_acl_verdict("/etc/x/config.toml")
        self.assertIs(got, sentinel)
        px.assert_called_once()

    def test_doctor_posture_reports_the_posix_verdict_on_linux(self) -> None:
        """On Linux the swapped doctor posture reports the POSIX boundary verdict
        (NOT_PROTECTED for a world-writable parent) - a verdict the Windows-only
        entry can NEVER produce off Windows (it fails closed to UNKNOWN there),
        so this proves the call-site swap routed to the cross-platform verdict."""
        from tools.agent_supervisor import cli
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        os.chmod(tmp, 0o777)  # world-writable parent -> posix verdict NOT_PROTECTED
        cfg = tmp / "config.toml"
        cfg.write_text("[controller]\ndefault_mode=\"shadow\"\n", encoding="utf-8")
        payload = cli._controller_config_acl_posture(str(cfg))
        self.assertEqual(payload["state"], os_acl.NOT_PROTECTED, payload)
        self.assertFalse(payload["protected"])


# --------------------------------------------------------------------------
# wiring: the two bare version/help probes carry the belt on Linux, env=None on
# Windows
# --------------------------------------------------------------------------
def _fake_proc(**_kw) -> types.SimpleNamespace:
    return types.SimpleNamespace(stdout="2.1.0\n", stderr="", returncode=0)


class BareProbeEnvTests(unittest.TestCase):
    def test_capability_probe_carries_belt_on_linux(self) -> None:
        captured: dict[str, object] = {}

        def fake_run(cmd, **kwargs):
            captured["env"] = kwargs.get("env")
            return _fake_proc()

        with mock.patch.object(capability_probe.os, "name", "posix"), \
             mock.patch.object(capability_probe.shutil, "which",
                               return_value="/fake/claude"), \
             mock.patch.object(capability_probe.subprocess, "run", fake_run):
            capability_probe._run(["claude", "--version"])
        env = captured["env"]
        self.assertIsNotNone(env, "a POSIX bare probe must carry an explicit env")
        self.assertEqual(env.get("DISABLE_AUTOUPDATER"), "1")

    def test_capability_probe_env_none_on_windows(self) -> None:
        captured: dict[str, object] = {"env": "unset"}

        def fake_run(cmd, **kwargs):
            captured["env"] = kwargs.get("env")
            return _fake_proc()

        with mock.patch.object(capability_probe.os, "name", "nt"), \
             mock.patch.object(capability_probe.shutil, "which",
                               return_value="C:/fake/claude.exe"), \
             mock.patch.object(capability_probe.subprocess, "run", fake_run):
            capability_probe._run(["claude", "--version"])
        self.assertIsNone(captured["env"], "Windows must keep env=None (unchanged)")

    def test_native_runtime_carries_belt_on_linux(self) -> None:
        captured: dict[str, object] = {}

        def fake_run(cmd, **kwargs):
            captured["env"] = kwargs.get("env")
            return _fake_proc()

        with mock.patch.object(native_runtime.os, "name", "posix"), \
             mock.patch.object(native_runtime.shutil, "which",
                               return_value="/fake/claude"), \
             mock.patch.object(native_runtime.subprocess, "run", fake_run):
            native_runtime.run_command(("claude", "--version"))
        env = captured["env"]
        self.assertIsNotNone(env)
        self.assertEqual(env.get("DISABLE_AUTOUPDATER"), "1")

    def test_native_runtime_env_none_on_windows(self) -> None:
        captured: dict[str, object] = {"env": "unset"}

        def fake_run(cmd, **kwargs):
            captured["env"] = kwargs.get("env")
            return _fake_proc()

        with mock.patch.object(native_runtime.os, "name", "nt"), \
             mock.patch.object(native_runtime.shutil, "which",
                               return_value="C:/fake/claude.exe"), \
             mock.patch.object(native_runtime.subprocess, "run", fake_run):
            native_runtime.run_command(("claude", "--version"))
        self.assertIsNone(captured["env"], "Windows must keep env=None (unchanged)")

    def test_native_runtime_honours_an_explicit_env_unchanged(self) -> None:
        """An explicit caller env (the dispatch path) is honoured as-is on POSIX -
        the belt is only added when the probe passed no env."""
        captured: dict[str, object] = {}

        def fake_run(cmd, **kwargs):
            captured["env"] = kwargs.get("env")
            return _fake_proc()

        with mock.patch.object(native_runtime.os, "name", "posix"), \
             mock.patch.object(native_runtime.shutil, "which",
                               return_value="/fake/claude"), \
             mock.patch.object(native_runtime.subprocess, "run", fake_run):
            native_runtime.run_command(("claude", "--help"), env={"FOO": "bar"})
        env = captured["env"]
        self.assertEqual(env, {"FOO": "bar"})
        self.assertNotIn("DISABLE_AUTOUPDATER", env)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(not unittest.main(exit=False).result.wasSuccessful())
