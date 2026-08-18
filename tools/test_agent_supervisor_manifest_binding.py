#!/usr/bin/env python3
"""M0-T072 regression suite: external-config manifest binding (D-017-R037..R053).

Proves the nine D-017-R051 behaviors:
  AS-1 matching external config passes (doctor / verify-controller / start paths);
  AS-2 a one-byte config change fails;
  AS-3 a missing config fails;
  AS-4 a manifest without the required config fails for production dispatch;
  AS-5 a wrong config path fails;
  AS-6 model-selection changes do not invalidate the controller;
  AS-7 no provider call occurs when verification fails;
  AS-8 a stale manifest fails for production dispatch;
  AS-9 the regenerated PowerShell runbook contains no CMD caret continuation and
       no unresolved executable placeholders, and doctor --live remains the only
       intentional bounded live control-response probe.

Deterministic, stdlib-only, no network, no provider contact. Synthetic controller
roots follow the test_agent_supervisor_phase1 fixture conventions; the production
package (PACKAGE_ROOT) is only ever read.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from agent_supervisor import CONTROLLER_VERSION  # noqa: E402
from agent_supervisor import manifest as mf  # noqa: E402
from agent_supervisor.cli import PACKAGE_ROOT, _check_manifest  # noqa: E402

VALID_CONFIG = """\
default_mode = "shadow"

[codex]
allowed_models = ["codex-primary", "codex-backup"]

[claude]
allowed_models = ["claude-opus-4-8"]
"""

VALID_SELECTION = """\
[codex]
model = "codex-primary"

[claude]
model = ""
"""

RUNBOOK = REPO_ROOT / "docs" / "CONTROLLER_UPDATE_RUNBOOK.md"


def write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


class TempCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def controller_root(self) -> pathlib.Path:
        """A synthetic controller package WITHOUT an in-tree config.toml."""
        root = self.tmp / "controller"
        (root / "schemas").mkdir(parents=True)
        write(root / "policy.py", "RULES = 1\n")
        write(root / "schemas" / "a.json", "{}\n")
        write(root / "config.example.toml", VALID_CONFIG)
        return root

    def external_config(self, text: str = VALID_CONFIG) -> pathlib.Path:
        """The active immutable config, OUTSIDE the package tree."""
        return write(self.tmp / "protected" / "config.toml", text)

    def recorded_manifest(self, root: pathlib.Path,
                          config: pathlib.Path) -> dict:
        return mf.generate_manifest(
            root, extra_files=((mf.CONFIG_LOGICAL_NAME, config),))


class ExternalConfigBindingTests(TempCase):
    """AS-1, AS-2, AS-3, AS-5, AS-6, AS-8 at the manifest layer."""

    def test_as1_matching_external_config_passes(self) -> None:
        root = self.controller_root()
        config = self.external_config()
        manifest = self.recorded_manifest(root, config)
        self.assertIn(mf.CONFIG_LOGICAL_NAME, manifest["files"])
        verification = mf.verify_manifest_with_config(root, manifest, config)
        self.assertTrue(verification.ok, verification.message)
        self.assertEqual(verification.reason_code, "")

    def test_as1_absolute_config_path_never_leaks_into_the_manifest(self) -> None:
        root = self.controller_root()
        config = self.external_config()
        manifest = self.recorded_manifest(root, config)
        serialized = json.dumps(manifest)
        self.assertNotIn(str(config.parent).replace("\\", "\\\\"), serialized)
        self.assertNotIn(config.parent.as_posix(), serialized)
        self.assertNotIn("protected", serialized)  # the private directory name

    def test_as2_one_byte_config_change_fails(self) -> None:
        root = self.controller_root()
        config = self.external_config()
        manifest = self.recorded_manifest(root, config)
        write(config, VALID_CONFIG[:-1] + "#")  # same length, one byte differs
        verification = mf.verify_manifest_with_config(root, manifest, config)
        self.assertFalse(verification.ok)
        self.assertIn(mf.CONFIG_LOGICAL_NAME, verification.changed)

    def test_as3_missing_config_fails(self) -> None:
        root = self.controller_root()
        config = self.external_config()
        manifest = self.recorded_manifest(root, config)
        config.unlink()
        verification = mf.verify_manifest_with_config(root, manifest, config)
        self.assertFalse(verification.ok)
        self.assertIn(mf.CONFIG_LOGICAL_NAME, verification.missing)

    def test_as3_no_config_path_fails_closed(self) -> None:
        root = self.controller_root()
        config = self.external_config()
        manifest = self.recorded_manifest(root, config)
        verification = mf.verify_manifest_with_config(root, manifest, None)
        self.assertFalse(verification.ok)
        self.assertEqual(verification.reason_code, "config_path_missing")

    def test_as4_manifest_without_config_entry_fails(self) -> None:
        root = self.controller_root()
        config = self.external_config()
        unbound = mf.generate_manifest(root)  # no extra_files: no config binding
        verification = mf.verify_manifest_with_config(root, unbound, config)
        self.assertFalse(verification.ok)
        self.assertEqual(verification.reason_code, "manifest_missing_config")

    def test_as5_wrong_config_path_fails(self) -> None:
        root = self.controller_root()
        config = self.external_config()
        manifest = self.recorded_manifest(root, config)
        other = write(self.tmp / "elsewhere" / "config.toml",
                      VALID_CONFIG + "\n# a different file\n")
        verification = mf.verify_manifest_with_config(root, manifest, other)
        self.assertFalse(verification.ok)
        self.assertIn(mf.CONFIG_LOGICAL_NAME, verification.changed)

    def test_as6_model_selection_change_never_invalidates(self) -> None:
        root = self.controller_root()
        config = self.external_config()
        write(root / mf.MODEL_SELECTION_FILENAME, VALID_SELECTION)
        manifest = self.recorded_manifest(root, config)
        self.assertNotIn(mf.MODEL_SELECTION_FILENAME, manifest["files"])
        write(root / mf.MODEL_SELECTION_FILENAME,
              VALID_SELECTION.replace("codex-primary", "codex-backup"))
        self.assertTrue(mf.verify_manifest_with_config(root, manifest, config).ok)

    def test_as8_wrong_controller_version_is_stale(self) -> None:
        root = self.controller_root()
        config = self.external_config()
        manifest = mf.generate_manifest(
            root, extra_files=((mf.CONFIG_LOGICAL_NAME, config),),
            controller_version="0.0.0-obsolete")
        verification = mf.verify_manifest_with_config(root, manifest, config)
        self.assertFalse(verification.ok)
        self.assertEqual(verification.reason_code, "manifest_stale")

    def test_as8_edited_manifest_is_stale(self) -> None:
        root = self.controller_root()
        config = self.external_config()
        manifest = self.recorded_manifest(root, config)
        manifest["files"]["policy.py"] = "0" * 64  # edited after recording
        verification = mf.verify_manifest_with_config(root, manifest, config)
        self.assertFalse(verification.ok)
        self.assertEqual(verification.reason_code, "manifest_stale")

    def test_in_package_config_duplicate_is_refused(self) -> None:
        root = self.controller_root()
        config = self.external_config()
        manifest = self.recorded_manifest(root, config)
        write(root / mf.CONFIG_LOGICAL_NAME, VALID_CONFIG)  # D-017-R048 violation
        verification = mf.verify_manifest_with_config(root, manifest, config)
        self.assertFalse(verification.ok)
        self.assertEqual(verification.reason_code, "config_duplicated_in_package")

    def test_stale_check_is_deterministic_and_fresh_manifest_passes_it(self) -> None:
        root = self.controller_root()
        config = self.external_config()
        manifest = self.recorded_manifest(root, config)
        self.assertEqual(mf.manifest_is_stale(manifest), "")
        self.assertNotEqual(
            mf.manifest_is_stale(manifest, running_controller_version="9.9.9"), "")


class DoctorPathTests(TempCase):
    """AS-1/AS-2 through the doctor check over the REAL package (read-only)."""

    def _real_package_manifest(self, config: pathlib.Path) -> pathlib.Path:
        manifest = mf.generate_manifest(
            PACKAGE_ROOT, extra_files=((mf.CONFIG_LOGICAL_NAME, config),))
        return mf.write_manifest(manifest, self.tmp / "controller_manifest.json")

    def test_doctor_verifies_the_external_config_binding(self) -> None:
        config = self.external_config()
        manifest_path = self._real_package_manifest(config)
        check = _check_manifest(str(manifest_path), str(config))
        self.assertTrue(check.ok, check.detail)
        self.assertIn(mf.CONFIG_LOGICAL_NAME, check.detail)

    def test_doctor_fails_on_config_drift(self) -> None:
        config = self.external_config()
        manifest_path = self._real_package_manifest(config)
        write(config, VALID_CONFIG + "\n# drift\n")
        check = _check_manifest(str(manifest_path), str(config))
        self.assertFalse(check.ok)
        self.assertIn(mf.CONFIG_LOGICAL_NAME, check.detail)

    def test_doctor_with_manifest_but_no_config_fails_closed(self) -> None:
        config = self.external_config()
        manifest_path = self._real_package_manifest(config)
        check = _check_manifest(str(manifest_path), None)
        self.assertFalse(check.ok)
        self.assertIn("config_path_missing", check.detail)

    def test_doctor_without_manifest_says_nothing_was_verified(self) -> None:
        check = _check_manifest(None, None)
        self.assertTrue(check.ok)  # informational, but must not claim verification
        self.assertIn("NOTHING was verified", check.detail)


class CliProductionPathTests(TempCase):
    """AS-1, AS-4, AS-7 through the real CLI (subprocess; the production path)."""

    def _run_cli(self, *argv: str) -> tuple[int, dict]:
        proc = subprocess.run(
            [sys.executable, "-m", "tools.agent_supervisor", *argv, "--json"],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120)
        body = proc.stdout.strip() or proc.stderr.strip()
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"raw": body}
        return proc.returncode, payload

    def test_verify_controller_passes_with_bound_manifest_and_config(self) -> None:
        config = self.external_config()
        manifest = mf.generate_manifest(
            PACKAGE_ROOT, extra_files=((mf.CONFIG_LOGICAL_NAME, config),))
        manifest_path = mf.write_manifest(manifest, self.tmp / "m.json")
        code, payload = self._run_cli("verify-controller",
                                      "--manifest", str(manifest_path),
                                      "--config", str(config))
        self.assertEqual(code, 0, payload)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["config_bound"])

    def test_verify_controller_without_manifest_fails_closed(self) -> None:
        code, payload = self._run_cli("verify-controller")
        self.assertEqual(code, 1)
        self.assertFalse(payload.get("ok", True))

    def test_verify_controller_detects_config_drift(self) -> None:
        config = self.external_config()
        manifest = mf.generate_manifest(
            PACKAGE_ROOT, extra_files=((mf.CONFIG_LOGICAL_NAME, config),))
        manifest_path = mf.write_manifest(manifest, self.tmp / "m.json")
        write(config, VALID_CONFIG + "\n# drift\n")
        code, payload = self._run_cli("verify-controller",
                                      "--manifest", str(manifest_path),
                                      "--config", str(config))
        self.assertEqual(code, 1)
        self.assertFalse(payload["ok"])

    def test_record_manifest_round_trip(self) -> None:
        config = self.external_config()
        out = self.tmp / "recorded" / "controller_manifest.json"
        code, payload = self._run_cli("record-manifest",
                                      "--config", str(config),
                                      "--out", str(out))
        self.assertEqual(code, 0, payload)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["config_bound_as"], mf.CONFIG_LOGICAL_NAME)
        recorded = json.loads(out.read_text(encoding="utf-8"))
        self.assertIn(mf.CONFIG_LOGICAL_NAME, recorded["files"])
        self.assertNotIn(mf.MODEL_SELECTION_FILENAME, recorded["files"])
        serialized = out.read_text(encoding="utf-8")
        self.assertNotIn("protected", serialized)  # absolute private path never leaks

    def _start_args(self, manifest_path: pathlib.Path,
                    config: pathlib.Path) -> tuple[list[str], pathlib.Path]:
        """Full explicit inputs with sentinel-writing fake executables."""
        checkout = self.tmp / "checkout"
        checkout.mkdir(exist_ok=True)
        runtime_base = self.tmp / "runtime"
        sentinel = self.tmp / "provider_was_called.sentinel"
        if os.name == "nt":
            fake = write(self.tmp / "fake_provider.cmd",
                         f"@echo off\necho touched > \"{sentinel}\"\n")
        else:
            fake = write(self.tmp / "fake_provider.sh",
                         f"#!/bin/sh\ntouch '{sentinel}'\n")
            fake.chmod(0o755)
        packet = write(self.tmp / "packet.json", json.dumps({
            "task_id": "M0-T072-TEST", "status": "claimed",
            "documented_test_commands": []}))
        selection = write(self.tmp / "model_selection.toml", VALID_SELECTION)
        argv = ["start", "--mode", "shadow",
                "--checkout", str(checkout),
                "--runtime-base", str(runtime_base),
                "--manifest", str(manifest_path),
                "--claude-executable", str(fake),
                "--codex-executable", str(fake),
                "--task-packet", str(packet),
                "--config", str(config),
                "--model-selection", str(selection)]
        return argv, sentinel

    def test_as4_start_refuses_manifest_without_config_binding(self) -> None:
        config = self.external_config()
        unbound = mf.generate_manifest(PACKAGE_ROOT)  # omits config.toml
        manifest_path = mf.write_manifest(unbound, self.tmp / "unbound.json")
        argv, sentinel = self._start_args(manifest_path, config)
        code, payload = self._run_cli(*argv)
        self.assertFalse(payload.get("dispatched", True), payload)
        self.assertEqual(payload.get("provider_calls_made"), 0)
        self.assertEqual(payload["manifest_binding"]["reason_code"],
                         "manifest_missing_config")
        self.assertFalse(sentinel.exists(), "provider executable was invoked")
        self.assertNotEqual(code, 0)

    def test_as7_no_provider_call_on_config_drift(self) -> None:
        config = self.external_config()
        manifest = mf.generate_manifest(
            PACKAGE_ROOT, extra_files=((mf.CONFIG_LOGICAL_NAME, config),))
        manifest_path = mf.write_manifest(manifest, self.tmp / "m.json")
        write(config, VALID_CONFIG + "\n# drift after recording\n")
        argv, sentinel = self._start_args(manifest_path, config)
        code, payload = self._run_cli(*argv)
        self.assertFalse(payload.get("dispatched", True), payload)
        self.assertEqual(payload.get("provider_calls_made"), 0)
        self.assertFalse(payload["manifest_binding"]["ok"])
        self.assertFalse(sentinel.exists(), "provider executable was invoked")

    def test_start_without_manifest_is_a_missing_required_input(self) -> None:
        config = self.external_config()
        manifest = mf.generate_manifest(
            PACKAGE_ROOT, extra_files=((mf.CONFIG_LOGICAL_NAME, config),))
        manifest_path = mf.write_manifest(manifest, self.tmp / "m.json")
        argv, sentinel = self._start_args(manifest_path, config)
        i = argv.index("--manifest")
        del argv[i:i + 2]
        code, payload = self._run_cli(*argv)
        self.assertFalse(payload.get("dispatched", True), payload)
        self.assertIn("--manifest", payload.get("missing_inputs", []))
        self.assertEqual(payload["manifest_binding"]["reason_code"],
                         "not_established")
        self.assertFalse(sentinel.exists())


class RunbookHygieneTests(unittest.TestCase):
    """AS-9: the regenerated runbook is PowerShell-native and placeholder-free."""

    def setUp(self) -> None:
        self.assertTrue(RUNBOOK.is_file(),
                        f"regenerated runbook missing: {RUNBOOK}")
        self.text = RUNBOOK.read_text(encoding="utf-8")

    def test_no_cmd_caret_continuation(self) -> None:
        in_fence = False
        offenders = []
        for n, line in enumerate(self.text.splitlines(), start=1):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence and line.rstrip().endswith("^"):
                offenders.append(n)
        self.assertEqual(offenders, [],
                         f"CMD caret continuation inside code fences at lines {offenders}")

    def test_no_unresolved_executable_placeholders(self) -> None:
        for pattern in ("<exact", "<path", "<your", "<fill", "<insert", "<codex-cli"):
            self.assertNotIn(pattern, self.text.lower(),
                             f"unresolved placeholder {pattern!r} in runbook")

    def test_doctor_live_is_the_only_live_probe(self) -> None:
        self.assertIn("doctor --live", self.text)
        # `start` must never be described as the control-response probe.
        for m in re.finditer(r"probe", self.text, flags=re.IGNORECASE):
            window = self.text[max(0, m.start() - 200):m.end() + 200]
            self.assertNotIn("start` as the probe", window)

    def test_runbook_uses_the_recorded_binding_commands(self) -> None:
        self.assertIn("record-manifest", self.text)
        self.assertIn("verify-controller", self.text)
        self.assertIn("--config", self.text)


if __name__ == "__main__":
    unittest.main()
