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
import hashlib
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

    # ---- M0-T050 (D-010-R184..R195): dry-run argument-vector fidelity --------
    #
    # SECOND demonstrated pre-activation defect: the owner's ELEVATED -DryRun
    # printed every command as the executable ONLY, with NO arguments. Root
    # cause: Invoke-Step's parameter was named `$Args`, which under Windows
    # PowerShell 5.1 collides with the AUTOMATIC $Args variable, so the bound
    # argument vector was dropped from BOTH the `$shown` display AND the
    # `& $Exe @Args` splat. The fix renames the parameter to `$CommandArgs`.
    #
    # We cannot run the whole script unelevated (the elevation refusal precedes
    # DryRun handling - existing reviewed behavior), so the dry-run contract is
    # proven in two layers: (A) DYNAMIC - extract Invoke-Step from the script via
    # the WinPS 5.1 parser AST, run it with $DryRun=$true and full vectors, and
    # assert the emitted [dry-run] line carries every element; (B) STATIC - parse
    # the AST and assert the real apply-path call sites carry exactly those
    # vectors, so the dynamic replay cannot drift from the script.

    # The EIGHT apply-path (exe, args) vectors, with representative substitutions
    # for $file / $dir / $UnelevatedUser. These MIRROR the script's apply calls
    # and are pinned to the real call sites by test B1 below.
    #
    # M0-T051 (D-010-R199/R207): the sequence now RESETs each target FIRST
    # (`/reset` removes ALL explicit ACEs and re-enables inheritance) BEFORE the
    # existing `/inheritance:r` (which then empties the DACL) and the `/grant:r`
    # trio (which fills it deterministically). Without the /reset a PRE-EXISTING
    # EXPLICIT ACE for an unrelated principal (e.g. NT AUTHORITY\Authenticated
    # Users:(M)) survives both /inheritance:r and /grant:r and leaves the config
    # unelevated-writable.
    _CFG = r"C:\controller\config.toml"
    _DIR = r"C:\controller"
    _USER = r"DESKTOP-ABC\owner"
    APPLY_VECTORS = [
        ("takeown.exe", ["/F", _CFG, "/A"]),
        ("takeown.exe", ["/F", _DIR, "/A"]),
        ("icacls.exe", [_CFG, "/reset"]),
        ("icacls.exe", [_CFG, "/inheritance:r"]),
        ("icacls.exe", [_CFG, "/grant:r",
                        r"BUILTIN\Administrators:(F)",
                        r"NT AUTHORITY\SYSTEM:(F)",
                        r"DESKTOP-ABC\owner:(RX)"]),
        ("icacls.exe", [_DIR, "/reset"]),
        ("icacls.exe", [_DIR, "/inheritance:r"]),
        ("icacls.exe", [_DIR, "/grant:r",
                        r"BUILTIN\Administrators:(OI)(CI)(F)",
                        r"NT AUTHORITY\SYSTEM:(OI)(CI)(F)",
                        r"DESKTOP-ABC\owner:(RX)"]),
    ]

    @staticmethod
    def _ps_single_quote(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    def _dryrun_line(self, script_path, exe, vector):
        """Extract Invoke-Step from `script_path` via the WinPS 5.1 parser AST,
        define it in a scope where $DryRun is $true, invoke it with (exe, vector),
        and return the captured process. Because the dry-run path returns BEFORE
        `& $Exe @CommandArgs`, no external command is ever executed."""
        q = self._ps_single_quote
        ps_arr = "@(" + ",".join(q(v) for v in vector) + ")"
        cmd = (
            "$t=$null;$e=$null;"
            "$ast=[System.Management.Automation.Language.Parser]::ParseFile("
            + q(str(script_path)) + ",[ref]$t,[ref]$e);"
            "$fn=$ast.FindAll({param($n) $n -is "
            "[System.Management.Automation.Language.FunctionDefinitionAst] "
            "-and $n.Name -eq 'Invoke-Step'},$true)[0];"
            "Invoke-Expression $fn.Extent.Text;"
            "$DryRun=$true;"
            "Invoke-Step " + q(exe) + " " + ps_arr + ";"
        )
        return subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True, text=True, timeout=60)

    def _invoke_step_call_sites(self, script_path):
        """Return [(line, [element_texts...]), ...] for every Invoke-Step call in
        the script, extracted via the WinPS 5.1 parser AST (CommandAst)."""
        q = self._ps_single_quote
        cmd = (
            "$t=$null;$e=$null;"
            "$ast=[System.Management.Automation.Language.Parser]::ParseFile("
            + q(str(script_path)) + ",[ref]$t,[ref]$e);"
            "$calls=$ast.FindAll({param($n) $n -is "
            "[System.Management.Automation.Language.CommandAst] "
            "-and $n.GetCommandName() -eq 'Invoke-Step'},$true);"
            "foreach($c in $calls){$parts=@();"
            "foreach($el in $c.CommandElements){"
            "$parts += ($el.Extent.Text -replace \"`r`n\",' ' -replace \"`n\",' ')};"
            "Write-Output ($c.Extent.StartLineNumber.ToString() + '|' + "
            "($parts -join '\\x1f'))}"
        )
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        sites = []
        for raw in proc.stdout.splitlines():
            raw = raw.strip()
            if not raw or "|" not in raw:
                continue
            line, rest = raw.split("|", 1)
            elems = [e.strip() for e in rest.split("\\x1f")]
            sites.append((int(line), elems))
        return sites

    @staticmethod
    def _norm_ws(text: str) -> str:
        return " ".join(text.split())

    @unittest.skipUnless(
        IS_WINDOWS and shutil.which("powershell"),
        "requires Windows PowerShell 5.1 (powershell.exe) for the parser API")
    def test_dryrun_emits_the_full_generic_vector(self) -> None:
        """A1 (R188): a generic full vector survives into the [dry-run] line -
        proving the argument vector is neither dropped nor truncated."""
        vector = ["A", "/flag", "principal:(RX)", "with space:(F)"]
        proc = self._dryrun_line(self.script, "tool.exe", vector)
        out = proc.stdout
        self.assertIn("[dry-run]", out, "no dry-run line; stderr=%r" % proc.stderr)
        for element in vector:
            self.assertIn(element, out,
                          "element %r dropped from dry-run line:\n%s" % (element, out))

    @unittest.skipUnless(
        IS_WINDOWS and shutil.which("powershell"),
        "requires Windows PowerShell 5.1 (powershell.exe) for the parser API")
    def test_dryrun_replays_all_apply_path_vectors(self) -> None:
        """A2 (R188/R195 + M0-T051/R199): replay each of the script's EIGHT
        apply-path vectors and assert the dry-run line carries the FULL vector -
        every path, /F, /A, /reset, /inheritance:r, /grant:r, and every ACL
        principal (owner's minimum)."""
        for exe, vector in self.APPLY_VECTORS:
            proc = self._dryrun_line(self.script, exe, vector)
            out = proc.stdout
            self.assertIn("[dry-run]", out,
                          "no dry-run line for %s; stderr=%r" % (exe, proc.stderr))
            for element in vector:
                self.assertIn(
                    element, out,
                    "element %r dropped for %s vector:\n%s" % (element, exe, out))
        # The union of the eight vectors covers each owner-enumerated token at
        # least once; assert them explicitly against the concatenated transcript.
        all_out = "".join(
            self._dryrun_line(self.script, exe, vector).stdout
            for exe, vector in self.APPLY_VECTORS)
        for token in ["/F", "/A", "/reset", "/inheritance:r", "/grant:r",
                      r"BUILTIN\Administrators:(F)", r"NT AUTHORITY\SYSTEM:(F)",
                      r"BUILTIN\Administrators:(OI)(CI)(F)",
                      r"NT AUTHORITY\SYSTEM:(OI)(CI)(F)",
                      r"DESKTOP-ABC\owner:(RX)"]:
            self.assertIn(token, all_out,
                          "owner-enumerated token %r never appeared" % token)

    @unittest.skipUnless(
        IS_WINDOWS and shutil.which("powershell"),
        "requires Windows PowerShell 5.1 (powershell.exe) for the parser API")
    def test_apply_path_call_sites_carry_full_argument_arrays(self) -> None:
        """B1 (R188 + M0-T051/R199): parse the script AST and assert the EIGHT
        apply-path Invoke-Step call sites carry exactly the expected argument
        arrays (now including the two `/reset` calls), so the dynamic replay in A2
        cannot silently drift from the script's real calls."""
        sites = self._invoke_step_call_sites(self.script)
        # element[0] is 'Invoke-Step', [1] is the exe var, [2] is the arg array.
        arrays = {self._norm_ws(elems[2]) for _line, elems in sites
                  if len(elems) >= 3}
        expected_apply = {
            r'@("/F", $file, "/A")',
            r'@("/F", $dir, "/A")',
            r'@($file, "/reset")',
            r'@($file, "/inheritance:r")',
            (r'@($file, "/grant:r", "BUILTIN\Administrators:(F)", '
             r'"NT AUTHORITY\SYSTEM:(F)", "${UnelevatedUser}:(RX)")'),
            r'@($dir, "/reset")',
            r'@($dir, "/inheritance:r")',
            (r'@($dir, "/grant:r", "BUILTIN\Administrators:(OI)(CI)(F)", '
             r'"NT AUTHORITY\SYSTEM:(OI)(CI)(F)", "${UnelevatedUser}:(RX)")'),
        }
        missing = expected_apply - arrays
        self.assertEqual(missing, set(),
                         "apply-path call-site argument arrays missing/changed: "
                         "%r\nfound: %r" % (missing, sorted(arrays)))
        # The exe for takeown vectors is $Takeown; for icacls vectors it is $Icacls.
        for _line, elems in sites:
            if len(elems) >= 3 and "/F" in elems[2] and "/A" in elems[2]:
                self.assertEqual(elems[1], "$Takeown", elems)

    @unittest.skipUnless(
        IS_WINDOWS and shutil.which("powershell"),
        "requires Windows PowerShell 5.1 (powershell.exe) for the parser API")
    def test_invoke_step_has_no_args_automatic_variable_collision(self) -> None:
        """B2 (R186): the Invoke-Step function must NOT declare or use an $Args
        parameter (the automatic-variable collision), and MUST use $CommandArgs."""
        q = self._ps_single_quote
        cmd = (
            "$t=$null;$e=$null;"
            "$ast=[System.Management.Automation.Language.Parser]::ParseFile("
            + q(str(self.script)) + ",[ref]$t,[ref]$e);"
            "$fn=$ast.FindAll({param($n) $n -is "
            "[System.Management.Automation.Language.FunctionDefinitionAst] "
            "-and $n.Name -eq 'Invoke-Step'},$true)[0];"
            "Write-Output $fn.Extent.Text"
        )
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        body = proc.stdout
        self.assertIn("$CommandArgs", body,
                      "Invoke-Step must use $CommandArgs:\n" + body)
        # Strip PowerShell line comments so the CODE (not the explanatory comment
        # that names the retired $Args defect) is what we assert on.
        import re
        code = "\n".join(re.sub(r"#.*$", "", ln) for ln in body.splitlines())
        # PowerShell variable names are case-insensitive, so $Args and $args are
        # the same automatic variable. Neither may appear in the executable code.
        self.assertIsNone(
            re.search(r"(?i)\$args\b", code),
            "Invoke-Step still references the automatic $Args variable:\n" + body)

    @unittest.skipUnless(
        IS_WINDOWS and shutil.which("powershell") and shutil.which("git"),
        "requires Windows PowerShell 5.1 and git to reconstruct the defective blob")
    def test_dryrun_line_is_red_on_the_defective_merged_content(self) -> None:
        """C (R189): reconstruct the CURRENTLY MERGED defective content (blob
        ca3811cd, git show 1e649a8:...) OUTSIDE the repo, apply the SAME layer-A
        harness, and prove the dry-run line contains ONLY the exe (arguments
        dropped) - i.e. the fidelity assertions above turn RED on the pre-fix
        code. This is the RED-on-defective proof that the new tests are load-bearing."""
        show = subprocess.run(
            ["git", "show",
             "1e649a8:tools/agent_supervisor/harden_controller_config.ps1"],
            capture_output=True, text=True, timeout=60, cwd=str(REPO))
        if show.returncode != 0:
            self.skipTest("defective blob 1e649a8 unreachable: " + show.stderr)
        tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        defective = tmp / "defective_harden.ps1"
        defective.write_text(show.stdout, encoding="utf-8")
        exe, vector = self.APPLY_VECTORS[3]  # the icacls /grant:r file vector
        proc = self._dryrun_line(defective, exe, vector)
        out = proc.stdout
        self.assertIn("[dry-run]", out,
                      "no dry-run line from defective content; stderr=%r" % proc.stderr)
        # RED proof: on the defective content EVERY argument is dropped.
        for element in vector:
            self.assertNotIn(
                element, out,
                "defective content unexpectedly RETAINED %r:\n%s" % (element, out))
        # And the fixed script RETAINS them under the identical harness (GREEN).
        fixed = self._dryrun_line(self.script, exe, vector).stdout
        for element in vector:
            self.assertIn(element, fixed,
                          "fixed script dropped %r:\n%s" % (element, fixed))

    def test_dryrun_completion_wording_cannot_claim_application(self) -> None:
        """D (R190): the dry-run completion path must state NO changes were made
        and must not print the unconditional 'apply complete.' text, while the
        real apply path keeps its 'apply complete.' wording unchanged."""
        import re
        text = self.script.read_text(encoding="utf-8")
        # The completion wording is now branched on $DryRun.
        self.assertRegex(
            text,
            r"if \(\$DryRun\)[\s\S]*?dry run complete\. NO changes were made"
            r"[\s\S]*?\} else \{[\s\S]*?apply complete\.",
            "the completion wording must branch: dry-run says NO changes were "
            "made; the else/apply path keeps 'apply complete.'")
        # Isolate the dry-run branch and prove it cannot claim application.
        m = re.search(r"if \(\$DryRun\) \{([\s\S]*?)\} else \{", text)
        self.assertIsNotNone(m, "dry-run completion branch not found")
        dry_branch = m.group(1)
        self.assertIn("dry run complete", dry_branch)
        self.assertIn("NO changes were made", dry_branch)
        self.assertNotIn("apply complete", dry_branch,
                         "the dry-run branch must never claim application")


@unittest.skipUnless(
    IS_WINDOWS and shutil.which("powershell"),
    "requires Windows + PowerShell 5.1 (AST extraction) and icacls")
class HardenExplicitAceStripTests(unittest.TestCase):
    """M0-T051 (D-010-R199..R207): THIRD demonstrated pre-activation defect.

    ROOT CAUSE: `/inheritance:r` strips only INHERITED ACEs and `/grant:r`
    replaces the grant only for the NAMED principals, so a PRE-EXISTING EXPLICIT
    ACE for an UNRELATED principal (the owner's real elevated apply hit an
    explicit `NT AUTHORITY\\Authenticated Users:(M)`) SURVIVES both and leaves the
    immutable config unelevated-writable (doctor: NOT_PROTECTED).

    R199 property: after the apply, the effective FILE and PARENT DACLs must
    contain NO non-elevated principal with any write/modify/delete/rename/replace/
    WriteDAC/WriteOwner right - the apply must not merely replace grants for the
    three intended principals while leaving unrelated explicit ACEs behind.

    FIX (R207, smallest inside the existing icacls path): `/reset` FIRST (removes
    all explicit ACEs, re-enables inheritance), THEN `/inheritance:r` (empties the
    DACL), THEN the three `/grant:r` calls -> a deterministic three-ACE end state
    regardless of any prior explicit ACE.

    UNELEVATED-vs-ELEVATED BOUNDARY (honest): the real script refuses unelevated
    and takeown/A (ownership -> Administrators) needs elevation. So these tests
    extract the apply-path COMMAND SEQUENCE from the script's AST (M0-T050
    technique), assert the takeown commands are PRESENT, and execute the
    DACL-affecting icacls subset against a DISPOSABLE fixture (granting/resetting
    the ACL of one's OWN file needs no elevation). They then assert the DACL
    end-state and the ACE-level verdict `evaluate_acl_entries` on the resulting
    DACL. What ONLY the owner's real elevated run can prove end-to-end: that the
    file's OWNER becomes Administrators (so `evaluate_file`'s owner-elevation check
    and the denied write-open probe pass) - unelevated, the fixture stays
    user-owned and thus user-writable, so `evaluate_file` correctly still reports
    NOT_PROTECTED even though the DACL is exactly the three intended ACEs. The
    ACE-level DACL property (R199) is exactly what these tests prove.
    """

    _ICACLS = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"),
                           "System32", "icacls.exe")
    # NT AUTHORITY\Authenticated Users, well-known SID - the poison principal.
    _AUTH_USERS_SID = "*S-1-5-11"
    _AUTH_USERS_NAMES = ("Authenticated Users", "S-1-5-11")

    def setUp(self) -> None:
        self.script = HERE / "agent_supervisor" / "harden_controller_config.ps1"
        # Disposable fixture OUTSIDE the repo.
        self._tmp = tempfile.mkdtemp(prefix="m0t051_acl_")
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)
        self.fx_dir = pathlib.Path(self._tmp) / "cfgdir"
        self.fx_dir.mkdir()
        self.cfg = self.fx_dir / "config.toml"
        self.cfg.write_text("[controller]\nx=1\n", encoding="utf-8")
        self.user = f"{os.environ.get('USERDOMAIN', '')}\\{os.environ.get('USERNAME', '')}"

    # -- helpers ------------------------------------------------------------

    def _icacls(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([self._ICACLS, *args],
                              capture_output=True, text=True, timeout=60)

    def _poison(self, target: pathlib.Path) -> None:
        """Add an EXPLICIT `Authenticated Users:(M)` ACE (no elevation needed on
        one's own object). This is the owner's real-world starting condition."""
        proc = self._icacls(str(target), "/grant", f"{self._AUTH_USERS_SID}:(M)")
        self.assertEqual(proc.returncode, 0,
                         "could not poison fixture: %s" % (proc.stdout + proc.stderr))

    def _dacl(self, target: pathlib.Path) -> tuple[list, str]:
        proc = self._icacls(str(target))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return parse_icacls(proc.stdout, target=str(target))

    def _principals(self, target: pathlib.Path) -> set[str]:
        entries, err = self._dacl(target)
        self.assertEqual(err, "", "icacls output unparseable for %s" % target)
        return {e.principal for e in entries}

    def _ace_verdict(self, target: pathlib.Path, kind: str) -> str:
        entries, err = self._dacl(target)
        self.assertEqual(err, "", "icacls output unparseable for %s" % target)
        return evaluate_acl_entries(entries, target=str(target), kind=kind).state

    def _poison_present(self, target: pathlib.Path) -> bool:
        entries, _ = self._dacl(target)
        return any(any(n.upper() in e.principal.upper() for n in self._AUTH_USERS_NAMES)
                   for e in entries)

    def _extract_apply_sequence(self, script_path: pathlib.Path):
        """Extract the apply-path command sequence from `script_path` via the
        WinPS 5.1 parser AST, resolving $file/$dir/$UnelevatedUser to the fixture
        and $Icacls/$Takeown to sentinels. Returns
        (takeown_calls, icacls_apply_calls) where each call is a list of concrete
        argument strings (the DACL-affecting icacls subset preserves script
        order). This is the SAME AST technique as the M0-T050 dry-run tests, but
        it EVALUATES the argument-array literal so the concrete argv the script
        would pass is what we replay - the test cannot drift from the script."""
        q = HardenScriptTests._ps_single_quote
        cmd = (
            "$t=$null;$e=$null;"
            "$ast=[System.Management.Automation.Language.Parser]::ParseFile("
            + q(str(script_path)) + ",[ref]$t,[ref]$e);"
            "$file=" + q(str(self.cfg)) + ";"
            "$dir=" + q(str(self.fx_dir)) + ";"
            "$UnelevatedUser=" + q(self.user) + ";"
            "$Icacls='ICACLS';$Takeown='TAKEOWN';"
            "$calls=$ast.FindAll({param($n) $n -is "
            "[System.Management.Automation.Language.CommandAst] "
            "-and $n.GetCommandName() -eq 'Invoke-Step'},$true);"
            "foreach($c in $calls){$els=$c.CommandElements;"
            "if($els.Count -lt 3){continue};"
            "$exe=Invoke-Expression $els[1].Extent.Text;"
            "$arr=@(Invoke-Expression $els[2].Extent.Text);"
            "Write-Output ($exe + '|~|' + ($arr -join '|~|'))}"
        )
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        takeown_calls: list[list[str]] = []
        icacls_apply: list[list[str]] = []
        apply_flags = {"/reset", "/inheritance:r", "/grant:r"}
        for raw in proc.stdout.splitlines():
            raw = raw.rstrip("\r\n")
            if "|~|" not in raw:
                continue
            parts = raw.split("|~|")
            exe, args = parts[0], parts[1:]
            if exe == "TAKEOWN":
                takeown_calls.append(args)
            elif exe == "ICACLS" and apply_flags.intersection(args):
                icacls_apply.append(args)
        return takeown_calls, icacls_apply

    def _run_apply_icacls(self, icacls_apply: list[list[str]]) -> None:
        for args in icacls_apply:
            proc = self._icacls(*args)
            self.assertEqual(proc.returncode, 0,
                             "apply icacls failed for %r: %s"
                             % (args, proc.stdout + proc.stderr))

    # -- tests --------------------------------------------------------------

    def test_adversarial_explicit_ace_is_stripped_file_and_parent(self) -> None:
        """R199/R200 (owner steps 1-5): poison the FILE and PARENT with an
        explicit Authenticated Users:(M), drive the REAL script's apply-path
        icacls subset against the fixture, and prove the poisoned ACE is GONE, the
        DACL is exactly the three intended principals, and the ACE-level verdict
        reports no unelevated-writable principal on BOTH file and parent."""
        self._poison(self.cfg)
        self._poison(self.fx_dir)
        self.assertTrue(self._poison_present(self.cfg), "fixture file not poisoned")
        self.assertTrue(self._poison_present(self.fx_dir), "fixture dir not poisoned")

        takeown_calls, icacls_apply = self._extract_apply_sequence(self.script)
        # The takeown (ownership -> Administrators) commands MUST be present in the
        # sequence, even though we cannot EXECUTE them unelevated.
        self.assertEqual(len(takeown_calls), 2,
                         "expected two takeown commands (file+dir): %r" % takeown_calls)
        for tk in takeown_calls:
            self.assertIn("/F", tk)
            self.assertIn("/A", tk)
        # The DACL-affecting icacls subset: /reset + /inheritance:r + /grant:r for
        # BOTH file and dir = six calls, in script order (/reset first per target).
        self.assertEqual(len(icacls_apply), 6,
                         "expected six apply icacls calls: %r" % icacls_apply)
        self.assertIn("/reset", icacls_apply[0],
                      "the FIRST apply icacls call per target must be /reset: %r"
                      % icacls_apply)

        self._run_apply_icacls(icacls_apply)

        # File: poison gone; exactly the three intended principals; ACE verdict OK.
        self.assertFalse(self._poison_present(self.cfg),
                         "FILE still carries the poisoned Authenticated Users ACE")
        self.assertEqual(self._principals(self.cfg),
                         {"BUILTIN\\Administrators", "NT AUTHORITY\\SYSTEM", self.user},
                         "FILE DACL is not exactly the three intended ACEs")
        self.assertEqual(self._ace_verdict(self.cfg, "file"), PROTECTED,
                         "FILE ACE-level verdict is not PROTECTED")
        # Parent: same.
        self.assertFalse(self._poison_present(self.fx_dir),
                         "PARENT still carries the poisoned Authenticated Users ACE")
        self.assertEqual(self._principals(self.fx_dir),
                         {"BUILTIN\\Administrators", "NT AUTHORITY\\SYSTEM", self.user},
                         "PARENT DACL is not exactly the three intended ACEs")
        self.assertEqual(self._ace_verdict(self.fx_dir, "directory"), PROTECTED,
                         "PARENT ACE-level verdict is not PROTECTED")

    def test_red_on_current_cleared_blob_leaves_poison_effective(self) -> None:
        """R205: the SAME fixture driven through the currently-merged (defective)
        blob 9625514e's apply sequence (git show 33b2e24:...) leaves the poisoned
        Authenticated Users:(M) EFFECTIVE and the ACE verdict NOT_PROTECTED - the
        old sequence FAILS the R199 property; the new sequence REMOVES it."""
        show = subprocess.run(
            ["git", "show",
             "33b2e24:tools/agent_supervisor/harden_controller_config.ps1"],
            capture_output=True, text=True, timeout=60, cwd=str(REPO))
        if show.returncode != 0:
            self.skipTest("defective blob (33b2e24 script) unreachable: " + show.stderr)
        old = pathlib.Path(self._tmp) / "defective_harden.ps1"
        old.write_text(show.stdout, encoding="utf-8")

        # RED: old sequence on a poisoned fixture -> poison SURVIVES.
        self._poison(self.cfg)
        _tk_old, icacls_old = self._extract_apply_sequence(old)
        # The defective sequence has NO /reset - only /inheritance:r + /grant:r.
        self.assertEqual(len(icacls_old), 4,
                         "defective sequence expected four icacls calls: %r" % icacls_old)
        self.assertFalse(any("/reset" in c for c in icacls_old),
                         "defective blob must NOT contain /reset: %r" % icacls_old)
        self._run_apply_icacls(icacls_old)
        self.assertTrue(self._poison_present(self.cfg),
                        "RED expectation broken: defective sequence removed the poison")
        self.assertEqual(self._ace_verdict(self.cfg, "file"), NOT_PROTECTED,
                         "defective sequence must leave the file NOT_PROTECTED")

        # GREEN: the fixed script's sequence on the SAME (now still-poisoned) file
        # removes it and yields exactly the three intended ACEs.
        _tk_new, icacls_new = self._extract_apply_sequence(self.script)
        self.assertTrue(any("/reset" in c for c in icacls_new),
                        "fixed script must contain /reset: %r" % icacls_new)
        self._run_apply_icacls(icacls_new)
        self.assertFalse(self._poison_present(self.cfg),
                         "fixed sequence failed to remove the poison")
        self.assertEqual(self._ace_verdict(self.cfg, "file"), PROTECTED)

    def test_new_sequence_is_idempotent(self) -> None:
        """R204: run the new apply sequence TWICE on the poisoned fixture; the
        end-state DACL is identical both times (file and parent)."""
        self._poison(self.cfg)
        self._poison(self.fx_dir)
        _tk, icacls_apply = self._extract_apply_sequence(self.script)

        self._run_apply_icacls(icacls_apply)
        file_once = self._icacls(str(self.cfg)).stdout
        dir_once = self._icacls(str(self.fx_dir)).stdout

        self._run_apply_icacls(icacls_apply)
        file_twice = self._icacls(str(self.cfg)).stdout
        dir_twice = self._icacls(str(self.fx_dir)).stdout

        self.assertEqual(file_once, file_twice, "FILE DACL not idempotent")
        self.assertEqual(dir_once, dir_twice, "PARENT DACL not idempotent")
        # And still exactly the three intended ACEs after the second run.
        self.assertEqual(self._principals(self.cfg),
                         {"BUILTIN\\Administrators", "NT AUTHORITY\\SYSTEM", self.user})

    def test_new_sequence_preserves_file_contents_byte_for_byte(self) -> None:
        """R202: icacls/takeown NEVER write file CONTENT. The fixture file's bytes
        (and sha256) are identical before and after the apply sequence."""
        before = self.cfg.read_bytes()
        before_hash = hashlib.sha256(before).hexdigest()
        self._poison(self.cfg)
        _tk, icacls_apply = self._extract_apply_sequence(self.script)
        self._run_apply_icacls(icacls_apply)
        after = self.cfg.read_bytes()
        after_hash = hashlib.sha256(after).hexdigest()
        self.assertEqual(before, after, "file CONTENT changed during ACL hardening")
        self.assertEqual(before_hash, after_hash)

    def test_new_sequence_preserves_unelevated_user_read(self) -> None:
        """R201: after the apply the unelevated user retains READ access (RX), so
        the ordinary supervisor can still read the config it must not modify."""
        self._poison(self.cfg)
        _tk, icacls_apply = self._extract_apply_sequence(self.script)
        self._run_apply_icacls(icacls_apply)
        entries, err = self._dacl(self.cfg)
        self.assertEqual(err, "")
        mine = [e for e in entries if e.principal.upper() == self.user.upper()]
        self.assertEqual(len(mine), 1, "the unelevated user must have exactly one ACE")
        self.assertIn("RX", mine[0].rights,
                      "the unelevated user must retain Read+Execute")
        # And still able to actually read the bytes.
        self.assertEqual(self.cfg.read_text(encoding="utf-8"), "[controller]\nx=1\n")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
