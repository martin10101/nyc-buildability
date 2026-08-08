#!/usr/bin/env python3
"""M0-T046 SCOPE 3 (D-010-R127/R128) - Windows OS-ACL boundary for the immutable
controller config.

The owner ruled the current single-account writable ACL insufficient for
supervised-auto activation: the unelevated supervisor may READ the controller
config but must not modify/overwrite/delete/rename/replace/change-ACL it, the
parent directory is protected against bypass, and modification requires an
elevated (UAC) owner action, while the fail-closed digest gate is retained.

`os_acl.py` INSPECTS and PROBES that boundary from an unelevated process and emits
a single fail-closed verdict (PROTECTED / NOT_PROTECTED / UNKNOWN). These tests
prove the parser and verdict logic on EVERY reachable state:
  * unit tests over parsed ACL FIXTURES (protected / writable / ambiguous / error
    -> fail-closed), platform-independent;
  * bounded LIVE probes against temp fixtures created here (a writable file ->
    NOT_PROTECTED; an inaccessible/ambiguous state -> fail-closed UNKNOWN), Windows;
  * the doctor posture surface reports the verdict fail-closed without breaking
    shadow mode;
  * the elevated apply script refuses to run unelevated.

The live PROTECTED-state proof against the real owner config happens AFTER the
owner's elevated apply (the orchestrator handles that); an unelevated process
cannot mint an Administrators-owned, UAC-required file, so that state is proven by
fixture here and by the orchestrator post-apply.

Scenario map: AS-3 (parser/verdict fixtures + fail-closed), AS-4 (live probes),
AS-5 (doctor posture surface), AS-6 (elevated script refuses unelevated).
"""
from __future__ import annotations

import contextlib
import ctypes
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import os_acl  # noqa: E402
from tools.agent_supervisor.os_acl import (  # noqa: E402
    NOT_PROTECTED,
    PROTECTED,
    UNKNOWN,
    evaluate_acl_entries,
    evaluate_controller_config_acl,
    evaluate_directory,
    evaluate_file,
    parse_icacls,
    probe_write_open,
)

IS_WINDOWS = sys.platform.startswith("win")


def _is_admin() -> bool:
    if not IS_WINDOWS:
        return os.geteuid() == 0 if hasattr(os, "geteuid") else False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:  # noqa: BLE001
        return False


# A hardened FILE: only Administrators/SYSTEM full; the user is Read+Execute.
PROTECTED_FILE_ICACLS = (
    r"C:\controller\config.toml BUILTIN\Administrators:(F)" "\n"
    r"                          NT AUTHORITY\SYSTEM:(F)" "\n"
    r"                          DESKTOP-ABC\owner:(RX)" "\n"
    "\n"
    "Successfully processed 1 files; Failed processing 0 files\n"
)

# A writable FILE: the user has Modify (the pre-hardening posture).
WRITABLE_FILE_ICACLS = (
    r"C:\controller\config.toml BUILTIN\Administrators:(I)(F)" "\n"
    r"                          NT AUTHORITY\SYSTEM:(I)(F)" "\n"
    r"                          DESKTOP-ABC\owner:(I)(M)" "\n"
    "\n"
    "Successfully processed 1 files; Failed processing 0 files\n"
)

# Granular combined tokens like (M,DC) and an inherit-only dangerous ACE.
COMBINED_TOKENS_ICACLS = (
    r"C:\controller\config.toml BUILTIN\Administrators:(F)" "\n"
    r"                          NT AUTHORITY\SYSTEM:(F)" "\n"
    r"                          DESKTOP-ABC\owner:(M,DC)" "\n"
    "\n"
    "Successfully processed 1 files; Failed processing 0 files\n"
)

# An ACE that only applies to CHILDREN (inherit-only) must NOT count against the
# object itself.
INHERIT_ONLY_DANGEROUS_ICACLS = (
    r"C:\controller\config.toml BUILTIN\Administrators:(F)" "\n"
    r"                          NT AUTHORITY\SYSTEM:(F)" "\n"
    r"                          DESKTOP-ABC\owner:(RX)" "\n"
    r"                          CREATOR OWNER:(IO)(F)" "\n"
    "\n"
    "Successfully processed 1 files; Failed processing 0 files\n"
)

# A protected DIRECTORY: Administrators/SYSTEM inherit full; user only RX.
PROTECTED_DIR_ICACLS = (
    r"C:\controller BUILTIN\Administrators:(OI)(CI)(F)" "\n"
    r"              NT AUTHORITY\SYSTEM:(OI)(CI)(F)" "\n"
    r"              DESKTOP-ABC\owner:(RX)" "\n"
    "\n"
    "Successfully processed 1 files; Failed processing 0 files\n"
)

# A writable DIRECTORY: the user can add files / delete children.
WRITABLE_DIR_ICACLS = (
    r"C:\controller BUILTIN\Administrators:(OI)(CI)(F)" "\n"
    r"              NT AUTHORITY\SYSTEM:(OI)(CI)(F)" "\n"
    r"              DESKTOP-ABC\owner:(OI)(CI)(M)" "\n"
    "\n"
    "Successfully processed 1 files; Failed processing 0 files\n"
)

EVERYONE_WRITE_ICACLS = (
    r"C:\controller\config.toml BUILTIN\Administrators:(F)" "\n"
    r"                          Everyone:(W)" "\n"
    "\n"
    "Successfully processed 1 files; Failed processing 0 files\n"
)


class ParseTests(unittest.TestCase):
    def test_parses_first_line_path_prefix_and_indented_lines(self) -> None:
        entries, err = parse_icacls(PROTECTED_FILE_ICACLS,
                                    target=r"C:\controller\config.toml")
        self.assertEqual(err, "")
        principals = [e.principal for e in entries]
        self.assertEqual(principals,
                         ["BUILTIN\\Administrators", "NT AUTHORITY\\SYSTEM",
                          "DESKTOP-ABC\\owner"])
        owner = [e for e in entries if e.principal == "DESKTOP-ABC\\owner"][0]
        self.assertIn("RX", owner.rights)

    def test_combined_comma_tokens_are_split(self) -> None:
        entries, _ = parse_icacls(COMBINED_TOKENS_ICACLS,
                                  target=r"C:\controller\config.toml")
        owner = [e for e in entries if e.principal == "DESKTOP-ABC\\owner"][0]
        self.assertIn("M", owner.rights)
        self.assertIn("DC", owner.rights)

    def test_inherit_only_flag_is_recorded(self) -> None:
        entries, _ = parse_icacls(INHERIT_ONLY_DANGEROUS_ICACLS,
                                  target=r"C:\controller\config.toml")
        creator = [e for e in entries if e.principal == "CREATOR OWNER"][0]
        self.assertTrue(creator.inherit_only)

    def test_ambiguous_output_yields_an_error(self) -> None:
        entries, err = parse_icacls("not an icacls listing at all\n",
                                    target=r"C:\controller\config.toml")
        self.assertEqual(entries, [])
        self.assertTrue(err)


class VerdictLogicTests(unittest.TestCase):
    def _verdict(self, output: str, *, target: str, kind: str) -> str:
        entries, err = parse_icacls(output, target=target)
        self.assertEqual(err, "")
        return evaluate_acl_entries(entries, target=target, kind=kind).state

    def test_protected_file_is_protected(self) -> None:
        self.assertEqual(
            self._verdict(PROTECTED_FILE_ICACLS,
                          target=r"C:\controller\config.toml", kind="file"),
            PROTECTED)

    def test_writable_file_is_not_protected(self) -> None:
        self.assertEqual(
            self._verdict(WRITABLE_FILE_ICACLS,
                          target=r"C:\controller\config.toml", kind="file"),
            NOT_PROTECTED)

    def test_combined_M_DC_token_is_not_protected(self) -> None:
        self.assertEqual(
            self._verdict(COMBINED_TOKENS_ICACLS,
                          target=r"C:\controller\config.toml", kind="file"),
            NOT_PROTECTED)

    def test_inherit_only_dangerous_ace_does_not_defeat_protection(self) -> None:
        self.assertEqual(
            self._verdict(INHERIT_ONLY_DANGEROUS_ICACLS,
                          target=r"C:\controller\config.toml", kind="file"),
            PROTECTED)

    def test_protected_directory_is_protected(self) -> None:
        self.assertEqual(
            self._verdict(PROTECTED_DIR_ICACLS,
                          target=r"C:\controller", kind="directory"),
            PROTECTED)

    def test_writable_directory_is_not_protected(self) -> None:
        self.assertEqual(
            self._verdict(WRITABLE_DIR_ICACLS,
                          target=r"C:\controller", kind="directory"),
            NOT_PROTECTED)

    def test_everyone_write_is_not_protected(self) -> None:
        self.assertEqual(
            self._verdict(EVERYONE_WRITE_ICACLS,
                          target=r"C:\controller\config.toml", kind="file"),
            NOT_PROTECTED)

    def test_unrecognised_token_fails_toward_not_protected(self) -> None:
        """G3 S3-1: the gate is a SAFE-SUBSET allowlist, so an unknown/new right
        token (here `ZZ`) held by an unelevated principal counts as dangerous and
        fails toward NOT_PROTECTED - it can never slip through as 'safe'."""
        unknown = (
            r"C:\controller\config.toml BUILTIN\Administrators:(F)" "\n"
            r"                          NT AUTHORITY\SYSTEM:(F)" "\n"
            r"                          DESKTOP-ABC\owner:(RX,ZZ)" "\n"
            "\n"
            "Successfully processed 1 files; Failed processing 0 files\n"
        )
        self.assertEqual(
            self._verdict(unknown, target=r"C:\controller\config.toml", kind="file"),
            NOT_PROTECTED)


class FailClosedTests(unittest.TestCase):
    """Every ambiguity/error path yields UNKNOWN, and UNKNOWN never reads protected."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name)
        self.cfg = self.tmp / "config.toml"
        self.cfg.write_text("[controller]\n", encoding="utf-8")

    def test_icacls_error_fails_closed_unknown(self) -> None:
        orig = os_acl._run_icacls
        os_acl._run_icacls = lambda p: ("", "icacls exit 5: access denied")
        try:
            v = evaluate_file(self.cfg)
        finally:
            os_acl._run_icacls = orig
        self.assertEqual(v.state, UNKNOWN)
        self.assertFalse(v.is_protected())

    def test_ambiguous_acl_output_fails_closed_unknown(self) -> None:
        orig = os_acl._run_icacls
        os_acl._run_icacls = lambda p: ("garbage with no ACEs\n", "")
        try:
            v = evaluate_file(self.cfg)
        finally:
            os_acl._run_icacls = orig
        self.assertEqual(v.state, UNKNOWN)
        self.assertFalse(v.is_protected())

    def test_probe_error_on_a_clean_acl_fails_closed_unknown(self) -> None:
        orig_run = os_acl._run_icacls
        orig_probe = os_acl.probe_write_open
        os_acl._run_icacls = lambda p: (PROTECTED_FILE_ICACLS, "")
        os_acl.probe_write_open = lambda p: "error:OSError"
        try:
            v = evaluate_file(self.cfg)
        finally:
            os_acl._run_icacls = orig_run
            os_acl.probe_write_open = orig_probe
        self.assertEqual(v.state, UNKNOWN)
        self.assertFalse(v.is_protected())

    def test_clean_acl_but_writable_probe_is_not_protected(self) -> None:
        """A clean-looking ACL that is nonetheless writable fails to NOT_PROTECTED
        (an active bypass beats a clean ACL - the safer direction)."""
        orig_run = os_acl._run_icacls
        orig_probe = os_acl.probe_write_open
        os_acl._run_icacls = lambda p: (PROTECTED_FILE_ICACLS, "")
        os_acl.probe_write_open = lambda p: "writable"
        try:
            v = evaluate_file(self.cfg)
        finally:
            os_acl._run_icacls = orig_run
            os_acl.probe_write_open = orig_probe
        self.assertEqual(v.state, NOT_PROTECTED)

    def test_missing_file_is_unknown(self) -> None:
        v = evaluate_file(self.tmp / "does_not_exist.toml")
        self.assertEqual(v.state, UNKNOWN)
        self.assertFalse(v.is_protected())

    def test_combined_verdict_protected_requires_both(self) -> None:
        orig = os_acl.evaluate_file
        # file PROTECTED but parent UNKNOWN -> combined UNKNOWN, not protected.
        from tools.agent_supervisor.os_acl import AclVerdict
        os_acl.evaluate_file = lambda p: AclVerdict(PROTECTED, str(p), "file", ())
        orig_dir = os_acl.evaluate_directory
        os_acl.evaluate_directory = lambda p: AclVerdict(UNKNOWN, str(p), "directory", ())
        try:
            v = evaluate_controller_config_acl(self.cfg)
        finally:
            os_acl.evaluate_file = orig
            os_acl.evaluate_directory = orig_dir
        self.assertEqual(v.state, UNKNOWN)
        self.assertFalse(v.is_protected())


class AbsoluteToolPathTests(unittest.TestCase):
    """G5 C1 (MEDIUM M-2): the ACL tools are invoked by ABSOLUTE System32 path, not
    a bare name that CreateProcess could resolve through the attacker-writable CWD."""

    def test_run_icacls_uses_absolute_system32_path(self) -> None:
        captured: dict[str, list[str]] = {}

        class _Result:
            returncode = 0
            stdout = PROTECTED_FILE_ICACLS
            stderr = ""

        orig = os_acl.subprocess.run
        os_acl.subprocess.run = lambda argv, **kw: (
            captured.__setitem__("argv", argv) or _Result())
        try:
            os_acl._run_icacls(pathlib.Path(r"C:\controller\config.toml"))
        finally:
            os_acl.subprocess.run = orig
        argv0 = captured["argv"][0]
        self.assertTrue(os.path.isabs(argv0), argv0)
        self.assertTrue(argv0.lower().replace("/", "\\").endswith(
            r"\system32\icacls.exe"), argv0)
        # It resolves under SystemRoot (default C:\Windows when unset).
        root = os.environ.get("SystemRoot", r"C:\Windows").lower()
        self.assertTrue(argv0.lower().startswith(root), argv0)

    def test_query_owner_uses_absolute_system32_powershell(self) -> None:
        captured: dict[str, list[str]] = {}

        class _Result:
            returncode = 0
            stdout = "BUILTIN\\Administrators\n"
            stderr = ""

        orig = os_acl.subprocess.run
        os_acl.subprocess.run = lambda argv, **kw: (
            captured.__setitem__("argv", argv) or _Result())
        try:
            owner, err = os_acl._query_owner(pathlib.Path(r"C:\controller\config.toml"))
        finally:
            os_acl.subprocess.run = orig
        self.assertEqual(err, "")
        self.assertEqual(owner, "BUILTIN\\Administrators")
        argv0 = captured["argv"][0]
        self.assertTrue(os.path.isabs(argv0), argv0)
        self.assertIn(r"\system32\windowspowershell\v1.0\powershell.exe",
                      argv0.lower().replace("/", "\\"))


class OwnerVerdictTests(unittest.TestCase):
    """G5 L-1: a clean DACL is not proof - the OWNER must be elevated, else the
    owner retains implicit WRITE_DAC and can re-grant write."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.cfg = pathlib.Path(self._tmp.name) / "config.toml"
        self.cfg.write_text("[controller]\n", encoding="utf-8")

    def _protected_output(self) -> str:
        # A clean DACL whose first-line path matches the real target, so the
        # parser strips it correctly and the DACL reads PROTECTED.
        return (
            f"{self.cfg} BUILTIN\\Administrators:(F)\n"
            r"                          NT AUTHORITY\SYSTEM:(F)" "\n"
            r"                          DESKTOP-ABC\owner:(RX)" "\n"
            "\n"
            "Successfully processed 1 files; Failed processing 0 files\n"
        )

    def _evaluate_with(self, owner_result):
        orig_run = os_acl._run_icacls
        orig_probe = os_acl.probe_write_open
        orig_owner = os_acl._query_owner
        orig_platform = sys.platform
        os_acl._run_icacls = lambda p: (self._protected_output(), "")
        os_acl.probe_write_open = lambda p: "denied"
        os_acl._query_owner = lambda p: owner_result
        # evaluate_file guards on sys.platform; force the Windows path.
        os_acl.sys.platform = "win32"
        try:
            return evaluate_file(self.cfg)
        finally:
            os_acl._run_icacls = orig_run
            os_acl.probe_write_open = orig_probe
            os_acl._query_owner = orig_owner
            os_acl.sys.platform = orig_platform

    def test_elevated_owner_plus_clean_dacl_is_protected(self) -> None:
        v = self._evaluate_with(("BUILTIN\\Administrators", ""))
        self.assertEqual(v.state, PROTECTED)
        self.assertTrue(v.is_protected())

    def test_user_owner_plus_clean_dacl_is_not_protected(self) -> None:
        v = self._evaluate_with(("DESKTOP-ABC\\owner", ""))
        self.assertEqual(v.state, NOT_PROTECTED)
        self.assertIn("owner", v.evidence)

    def test_owner_query_error_fails_closed_unknown(self) -> None:
        v = self._evaluate_with(("", "owner query exit 1: access denied"))
        self.assertEqual(v.state, UNKNOWN)
        self.assertFalse(v.is_protected())


@unittest.skipUnless(IS_WINDOWS, "Windows OS-ACL semantics")
class LiveProbeTests(unittest.TestCase):
    """Bounded live probes against temp fixtures at the trust levels reachable
    unelevated."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name)

    def test_a_writable_temp_file_yields_not_protected(self) -> None:
        cfg = self.tmp / "config.toml"
        cfg.write_text("[controller]\n", encoding="utf-8")
        before = cfg.read_bytes()
        verdict = evaluate_controller_config_acl(cfg)
        # The probe must not have altered the file.
        self.assertEqual(cfg.read_bytes(), before)
        self.assertEqual(verdict.file.evidence.get("write_open_probe"), "writable")
        self.assertEqual(verdict.file.state, NOT_PROTECTED)
        self.assertEqual(verdict.state, NOT_PROTECTED)
        self.assertFalse(verdict.is_protected())

    def test_write_open_probe_is_nondestructive(self) -> None:
        cfg = self.tmp / "config.toml"
        cfg.write_text("keep me\n", encoding="utf-8")
        self.assertEqual(probe_write_open(cfg), "writable")
        self.assertEqual(cfg.read_text(encoding="utf-8"), "keep me\n")

    def test_missing_file_probe_reports_missing(self) -> None:
        self.assertEqual(probe_write_open(self.tmp / "nope.toml"), "error:missing")

    def test_inaccessible_state_is_unknown_fail_closed(self) -> None:
        # An inaccessible/ambiguous state reachable unelevated: a non-existent
        # config yields a fail-closed UNKNOWN (never 'protected').
        verdict = evaluate_controller_config_acl(self.tmp / "ghost.toml")
        self.assertEqual(verdict.file.state, UNKNOWN)
        self.assertFalse(verdict.is_protected())


@unittest.skipUnless(IS_WINDOWS, "doctor ACL posture is a Windows boundary")
class DoctorPostureTests(unittest.TestCase):
    def setUp(self) -> None:
        from tools.agent_supervisor import cli
        self.cli = cli
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name)
        self.repo = self.tmp / "repo"
        (self.repo / "tools").mkdir(parents=True)
        self.cfg = self.tmp / "config.toml"
        self.cfg.write_text(
            "[codex]\nallowed_models=[]\n[claude]\nallowed_models=[]\n"
            "[controller]\ndefault_mode=\"shadow\"\n", encoding="utf-8")

    def _doctor(self, *extra: str) -> tuple[int, dict]:
        out = io.StringIO()
        argv = ["doctor", "--checkout", str(self.repo),
                "--runtime-base", str(self.tmp / "rt"), "--json", *extra]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = self.cli.main(argv)
        return code, json.loads(out.getvalue())

    def test_doctor_reports_not_protected_posture_without_breaking_shadow(self) -> None:
        code, payload = self._doctor("--config", str(self.cfg))
        acl = payload["controller_config_acl"]
        self.assertEqual(acl["state"], NOT_PROTECTED)
        self.assertFalse(acl["protected"])
        # Shadow doctor is NOT broken by an unhardened posture: the pass/fail
        # `ok` is independent of the ACL posture.
        self.assertNotIn("controller_config_acl",
                         [c["check"] for c in payload["checks"]])

    def test_doctor_without_config_reports_skipped_not_protected(self) -> None:
        _code, payload = self._doctor()
        acl = payload["controller_config_acl"]
        self.assertEqual(acl["state"], "SKIPPED")
        self.assertFalse(acl["protected"],
                         "a skipped posture must never read as protected")


class HardenScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.script = HERE / "agent_supervisor" / "harden_controller_config.ps1"

    def test_script_exists_and_declares_the_boundary(self) -> None:
        self.assertTrue(self.script.exists())
        text = self.script.read_text(encoding="utf-8")
        # The load-bearing contract is present.
        self.assertIn("Test-IsElevated", text)
        self.assertIn("/inheritance:r", text)
        self.assertIn(":(RX)", text)
        self.assertIn("-Rollback", text)

    @unittest.skipUnless(
        IS_WINDOWS and shutil.which("powershell"),
        "requires Windows PowerShell 5.1 (powershell.exe) for the parser API")
    def test_script_parses_cleanly_under_windows_powershell_51(self) -> None:
        """M0-T049 (D-010-R174/R177): the elevated hardening script must PARSE
        with zero errors under Windows PowerShell 5.1.

        A demonstrated defect had `"$UnelevatedUser:(M)"` /
        `"$UnelevatedUser:(RX)"` parse the ':' after an interpolated variable as
        a scope/drive qualifier, making the WHOLE file a parse error before any
        ACL change ran. Exit codes cannot catch this: a parse failure ALSO exits
        non-zero, so it masqueraded as the intended "refuses unelevated" refusal
        in test_script_refuses_to_run_unelevated. We must therefore assert on the
        PARSER's error list directly, via the Windows PowerShell 5.1 language
        parser API (powershell.exe, NOT pwsh, so 5.1 tokenizer semantics apply).
        """
        # Ask the WinPS 5.1 parser to parse the file and print the error count
        # plus each error message (line-prefixed) so a failure is diagnosable.
        cmd = (
            "$t=$null;$e=$null;"
            "[System.Management.Automation.Language.Parser]::ParseFile("
            "'" + str(self.script) + "',[ref]$t,[ref]$e)|Out-Null;"
            "Write-Output ('parse_errors=' + $e.Count);"
            "$e|ForEach-Object{Write-Output "
            "($_.Extent.StartLineNumber.ToString() + ': ' + $_.Message)}"
        )
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True, text=True, timeout=60)
        out = proc.stdout.strip()
        self.assertIn("parse_errors=", out,
                      "parser API produced no count; stderr=%r" % proc.stderr)
        first = out.splitlines()[0].strip()
        self.assertEqual(
            first, "parse_errors=0",
            "harden_controller_config.ps1 has PowerShell 5.1 parse errors:\n"
            + out + "\nstderr=" + proc.stderr)

    @unittest.skipUnless(
        IS_WINDOWS and shutil.which("powershell") and not _is_admin(),
        "requires an UNELEVATED Windows shell with powershell")
    def test_script_refuses_to_run_unelevated(self) -> None:
        tmp = pathlib.Path(tempfile.mkdtemp())
        cfg = tmp / "config.toml"
        cfg.write_text("[controller]\n", encoding="utf-8")
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(self.script), "-ConfigPath", str(cfg)],
            capture_output=True, text=True, timeout=60)
        self.assertNotEqual(proc.returncode, 0,
                            "the script must refuse to run unelevated")
        self.assertIn("elevated", (proc.stderr + proc.stdout).lower())
        # The refusal must be the script's OWN elevation refusal, not a parse
        # error masquerading as one (the M0-T049 defect class).
        combined = (proc.stderr + proc.stdout).lower()
        self.assertNotIn("variable reference is not valid", combined,
                         "refusal must not be a parse error")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
