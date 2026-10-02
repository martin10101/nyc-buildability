#!/usr/bin/env python3
"""D-091 T1 (M0-T165) - the Linux platform seam for the loop controller.

Three deliverables, proven here against every acceptance scenario WITHOUT root and
on any host (CI runs this suite on windows-latest), by injecting the stat/owner
lookup and the platform decision rather than depending on the real OS:

  * `posix_acl` - a POSIX verifier for the protected config with the SAME
    fail-closed verdict shape `os_acl` gives on Windows (OK only for a root-owned,
    not group/world-writable config in a root-owned, not group/world-writable
    parent, no symlinks; UNKNOWN or NOT_PROTECTED otherwise, each with a named
    reason), plus the additive cross-platform dispatcher
    `os_acl.controller_config_acl_verdict`.
  * `platform_paths` - a Linux resolver for the config / runtime / activation
    paths that never returns a Windows path on Linux and leaves Windows unchanged.
  * `process.posix_autoupdater_belt` / `bare_probe_env` /
    `apply_posix_autoupdater_belt` - DISABLE_AUTOUPDATER=1 for the two bare
    version/help probes on Linux, no-op on Windows.

Scenario map (packet acceptance_scenarios):
  primary          -> PosixAclOkTests
  boundary         -> PosixAclBoundaryTests
  missing/ambiguous-> PosixAclUnknownTests
  failure          -> PosixAclSymlinkTests
  regression       -> run the existing tools/test_agent_supervisor_*.py suite (the
                      producer report records the counts); here VerdictShapeParity
                      proves the Linux verdict is the SAME dataclass shape os_acl
                      uses and Windows behavior of the seam is unchanged.
"""
from __future__ import annotations

import os
import pathlib
import stat as stat_module
import sys
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import os_acl  # noqa: E402
from tools.agent_supervisor import platform_paths  # noqa: E402
from tools.agent_supervisor import posix_acl  # noqa: E402
from tools.agent_supervisor import process  # noqa: E402
from tools.agent_supervisor.os_acl import (  # noqa: E402
    NOT_PROTECTED,
    PROTECTED,
    UNKNOWN,
    AclVerdict,
    ControllerConfigAclVerdict,
)


class _FakeStat:
    """The two fields `posix_acl` reads from a stat result. Lets a test mint any
    ownership/mode/symlink state without root and on any platform."""

    def __init__(self, uid: int, mode: int) -> None:
        self.st_uid = uid
        self.st_mode = mode


def _reg(uid: int, perm: int) -> _FakeStat:
    return _FakeStat(uid, stat_module.S_IFREG | perm)


def _dir(uid: int, perm: int) -> _FakeStat:
    return _FakeStat(uid, stat_module.S_IFDIR | perm)


def _lnk(perm: int = 0o777) -> _FakeStat:
    return _FakeStat(0, stat_module.S_IFLNK | perm)


#: A protected config under a protected parent, used as the baseline that each
#: boundary test flips ONE field of (so each clause is proven load-bearing).
CFG = pathlib.Path("/etc/nyc-supervisor/config.toml")
PARENT = CFG.parent


def _lstat_from(mapping: dict) -> "callable":
    """A fake lstat that returns the mapped stat for a known path and raises
    FileNotFoundError otherwise (the real os.lstat contract for a missing path)."""
    def _lstat(path: str) -> _FakeStat:
        key = str(path)
        if key not in mapping:
            raise FileNotFoundError(key)
        return mapping[key]
    return _lstat


def _ok_mapping() -> dict:
    return {str(CFG): _reg(0, 0o444), str(PARENT): _dir(0, 0o755)}


# ---------------------------------------------------------------------------
# primary: OK verdict shape
# ---------------------------------------------------------------------------
class PosixAclOkTests(unittest.TestCase):
    def test_root_owned_0444_in_root_owned_0755_is_protected(self) -> None:
        lstat = _lstat_from(_ok_mapping())
        v = posix_acl.evaluate_controller_config_acl(CFG, lstat=lstat, is_posix=True)
        self.assertEqual(v.state, PROTECTED)
        self.assertTrue(v.is_protected())
        self.assertEqual(v.file.state, PROTECTED)
        self.assertEqual(v.parent.state, PROTECTED)

    def test_file_and_directory_verdicts_name_the_reason(self) -> None:
        lstat = _lstat_from(_ok_mapping())
        fv = posix_acl.evaluate_file(CFG, lstat=lstat, is_posix=True)
        dv = posix_acl.evaluate_directory(PARENT, lstat=lstat, is_posix=True)
        self.assertEqual((fv.state, dv.state), (PROTECTED, PROTECTED))
        self.assertTrue(fv.reasons and dv.reasons, "a verdict must carry a reason")
        self.assertEqual(fv.evidence["uid"], 0)
        self.assertEqual(fv.evidence["mode"], "0444")
        self.assertFalse(fv.evidence["is_symlink"])


# ---------------------------------------------------------------------------
# boundary: each insecurity fails closed with a named reason (one field flipped)
# ---------------------------------------------------------------------------
class PosixAclBoundaryTests(unittest.TestCase):
    def _combined(self, mapping: dict) -> ControllerConfigAclVerdict:
        return posix_acl.evaluate_controller_config_acl(
            CFG, lstat=_lstat_from(mapping), is_posix=True)

    def test_group_writable_config_is_not_protected(self) -> None:
        m = _ok_mapping()
        m[str(CFG)] = _reg(0, 0o464)  # only the group-write bit flipped
        v = self._combined(m)
        self.assertEqual(v.state, NOT_PROTECTED)
        self.assertEqual(v.file.state, NOT_PROTECTED)
        self.assertIn("group", v.file.reasons[0])
        self.assertFalse(v.is_protected())

    def test_world_writable_config_is_not_protected(self) -> None:
        m = _ok_mapping()
        m[str(CFG)] = _reg(0, 0o446)  # only the world-write bit flipped
        v = self._combined(m)
        self.assertEqual(v.file.state, NOT_PROTECTED)
        self.assertIn("world", v.file.reasons[0])
        self.assertFalse(v.is_protected())

    def test_non_root_owned_config_is_not_protected(self) -> None:
        m = _ok_mapping()
        m[str(CFG)] = _reg(1000, 0o444)  # same mode, only the owner flipped
        v = self._combined(m)
        self.assertEqual(v.file.state, NOT_PROTECTED)
        self.assertIn("not root", v.file.reasons[0])
        self.assertFalse(v.is_protected())

    def test_writable_parent_directory_is_not_protected(self) -> None:
        m = _ok_mapping()
        m[str(PARENT)] = _dir(0, 0o777)  # file still fine; only the parent flipped
        v = self._combined(m)
        self.assertEqual(v.file.state, PROTECTED)
        self.assertEqual(v.parent.state, NOT_PROTECTED)
        self.assertIn("world", v.parent.reasons[0])
        self.assertEqual(v.state, NOT_PROTECTED)
        self.assertFalse(v.is_protected())

    def test_non_root_owned_parent_is_not_protected(self) -> None:
        m = _ok_mapping()
        m[str(PARENT)] = _dir(1000, 0o755)
        v = self._combined(m)
        self.assertEqual(v.parent.state, NOT_PROTECTED)
        self.assertIn("not root", v.parent.reasons[0])
        self.assertFalse(v.is_protected())


# ---------------------------------------------------------------------------
# missing / ambiguous: UNKNOWN, never read as protected
# ---------------------------------------------------------------------------
class PosixAclUnknownTests(unittest.TestCase):
    def test_missing_config_is_unknown_fail_closed(self) -> None:
        lstat = _lstat_from({str(PARENT): _dir(0, 0o755)})  # file absent
        v = posix_acl.evaluate_controller_config_acl(CFG, lstat=lstat, is_posix=True)
        self.assertEqual(v.file.state, UNKNOWN)
        self.assertIn("does not exist", v.file.reasons[0])
        self.assertFalse(v.is_protected())

    def test_unreadable_owner_is_unknown_fail_closed(self) -> None:
        def _lstat(path: str) -> _FakeStat:
            raise PermissionError("owner/mode unreadable")
        v = posix_acl.evaluate_file(CFG, lstat=_lstat, is_posix=True)
        self.assertEqual(v.state, UNKNOWN)
        self.assertIn("could not be stat", v.reasons[0])
        self.assertFalse(v.is_protected())

    def test_unknown_platform_is_unknown_fail_closed(self) -> None:
        lstat = _lstat_from(_ok_mapping())
        v = posix_acl.evaluate_controller_config_acl(CFG, lstat=lstat, is_posix=False)
        self.assertEqual(v.file.state, UNKNOWN)
        self.assertEqual(v.parent.state, UNKNOWN)
        self.assertEqual(v.state, UNKNOWN)
        self.assertIn("not a POSIX platform", v.file.reasons[0])
        self.assertFalse(v.is_protected())


# ---------------------------------------------------------------------------
# failure: a symlinked config or parent fails closed
# ---------------------------------------------------------------------------
class PosixAclSymlinkTests(unittest.TestCase):
    def test_symlinked_config_is_not_protected(self) -> None:
        m = _ok_mapping()
        m[str(CFG)] = _lnk()
        v = posix_acl.evaluate_controller_config_acl(
            CFG, lstat=_lstat_from(m), is_posix=True)
        self.assertEqual(v.file.state, NOT_PROTECTED)
        self.assertIn("symlink", v.file.reasons[0])
        self.assertTrue(v.file.evidence["is_symlink"])
        self.assertFalse(v.is_protected())

    def test_symlinked_parent_is_not_protected(self) -> None:
        m = _ok_mapping()
        m[str(PARENT)] = _lnk()
        v = posix_acl.evaluate_controller_config_acl(
            CFG, lstat=_lstat_from(m), is_posix=True)
        self.assertEqual(v.parent.state, NOT_PROTECTED)
        self.assertIn("symlink", v.parent.reasons[0])
        self.assertEqual(v.state, NOT_PROTECTED)
        self.assertFalse(v.is_protected())


# ---------------------------------------------------------------------------
# regression / parity: same verdict dataclass shape as os_acl; UNKNOWN safe
# ---------------------------------------------------------------------------
class VerdictShapeParityTests(unittest.TestCase):
    def test_posix_verdict_reuses_the_os_acl_dataclasses(self) -> None:
        v = posix_acl.evaluate_controller_config_acl(
            CFG, lstat=_lstat_from(_ok_mapping()), is_posix=True)
        self.assertIsInstance(v, ControllerConfigAclVerdict)
        self.assertIsInstance(v.file, AclVerdict)
        self.assertIsInstance(v.parent, AclVerdict)

    def test_to_dict_shape_matches_os_acl(self) -> None:
        posix_v = posix_acl.evaluate_controller_config_acl(
            CFG, lstat=_lstat_from(_ok_mapping()), is_posix=True).to_dict()
        self.assertEqual(set(posix_v), {"state", "protected", "file", "parent"})
        self.assertEqual(set(posix_v["file"]),
                         {"state", "target", "kind", "protected", "reasons",
                          "evidence"})

    def test_every_non_protected_verdict_reads_not_protected(self) -> None:
        # The safety-critical invariant: UNKNOWN and NOT_PROTECTED are never
        # is_protected(). Proven across the fail-closed verdict surface.
        cases = [
            posix_acl.evaluate_file(CFG, lstat=_lstat_from({}), is_posix=True),
            posix_acl.evaluate_file(CFG, lstat=_lstat_from(_ok_mapping()),
                                    is_posix=False),
            posix_acl.evaluate_file(CFG, lstat=_lstat_from(
                {str(CFG): _reg(1000, 0o444)}), is_posix=True),
        ]
        for v in cases:
            self.assertFalse(v.is_protected(), v.reasons)


# ---------------------------------------------------------------------------
# os_acl cross-platform dispatcher (additive; existing os_acl functions untouched)
# ---------------------------------------------------------------------------
class ControllerConfigAclDispatchTests(unittest.TestCase):
    """The additive cross-platform dispatcher routes by platform. Routing is proven
    by replacing the delegate target with a sentinel (so neither pathlib nor a real
    stat runs under a forced os.name), then a real-host integration check."""

    def _sentinel(self) -> ControllerConfigAclVerdict:
        return ControllerConfigAclVerdict(
            UNKNOWN,
            AclVerdict(UNKNOWN, "f", "file", ()),
            AclVerdict(UNKNOWN, "p", "directory", ()))

    def test_posix_branch_routes_to_posix_acl(self) -> None:
        sentinel = self._sentinel()
        with mock.patch.object(os_acl.os, "name", "posix"), \
                mock.patch.object(posix_acl, "evaluate_controller_config_acl",
                                  return_value=sentinel) as posix_entry:
            got = os_acl.controller_config_acl_verdict(CFG)
        posix_entry.assert_called_once_with(CFG)
        self.assertIs(got, sentinel)

    def test_non_posix_branch_routes_to_windows_entry(self) -> None:
        sentinel = self._sentinel()
        with mock.patch.object(os_acl.os, "name", "nt"), \
                mock.patch.object(os_acl, "evaluate_controller_config_acl",
                                  return_value=sentinel) as win_entry:
            got = os_acl.controller_config_acl_verdict(CFG)
        win_entry.assert_called_once_with(CFG)
        self.assertIs(got, sentinel)

    @unittest.skipUnless(os.name == "posix", "real POSIX host")
    def test_real_posix_host_produces_a_posix_verdict(self) -> None:
        got = os_acl.controller_config_acl_verdict(CFG)
        self.assertEqual(got, posix_acl.evaluate_controller_config_acl(CFG))
        self.assertIsInstance(got, ControllerConfigAclVerdict)


# ---------------------------------------------------------------------------
# platform_paths: a Linux resolver that never emits a Windows path on Linux
# ---------------------------------------------------------------------------
class PlatformPathsTests(unittest.TestCase):
    def test_posix_config_path_is_etc_and_has_no_windows_marker(self) -> None:
        p = platform_paths.default_config_path(os_name="posix")
        self.assertEqual(
            p, pathlib.Path(platform_paths.POSIX_CONFIG_DIR)
            / platform_paths.CONFIG_FILENAME)
        self.assertNotIn(platform_paths.WINDOWS_CONFIG_DIR_NAME, p.parts)
        self.assertIn("nyc-supervisor", p.parts)

    def test_windows_config_path_uses_program_files(self) -> None:
        p = platform_paths.default_config_path(
            os_name="nt", environ={"ProgramFiles": r"C:\Program Files"})
        self.assertEqual(
            p, pathlib.Path(r"C:\Program Files")
            / platform_paths.WINDOWS_CONFIG_DIR_NAME
            / platform_paths.CONFIG_FILENAME)

    def test_posix_activation_dir_prefers_xdg_config_home(self) -> None:
        p = platform_paths.default_activation_dir(
            os_name="posix", environ={"XDG_CONFIG_HOME": "/x/cfg"})
        self.assertEqual(
            p, pathlib.Path("/x/cfg") / platform_paths.POSIX_APP_DIR_NAME
            / platform_paths.ACTIVATION_SUBDIR)

    def test_posix_activation_dir_falls_back_to_dot_config(self) -> None:
        p = platform_paths.default_activation_dir(
            os_name="posix", environ={"HOME": "/home/u"})
        self.assertEqual(
            p, pathlib.Path("/home/u") / ".config"
            / platform_paths.POSIX_APP_DIR_NAME / platform_paths.ACTIVATION_SUBDIR)

    def test_windows_activation_dir_uses_localappdata(self) -> None:
        p = platform_paths.default_activation_dir(
            os_name="nt", environ={"LOCALAPPDATA": r"C:\Users\x\AppData\Local"})
        self.assertIn(platform_paths.ACTIVATION_SUBDIR, p.parts)
        self.assertIn("NYCBuildabilitySupervisor", p.parts)

    def test_windows_activation_dir_without_localappdata_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            platform_paths.default_activation_dir(os_name="nt", environ={})

    def test_manifest_path_is_inside_activation_dir(self) -> None:
        env = {"XDG_CONFIG_HOME": "/x/cfg"}
        manifest = platform_paths.default_manifest_path(os_name="posix", environ=env)
        act = platform_paths.default_activation_dir(os_name="posix", environ=env)
        self.assertEqual(manifest.parent, act)
        self.assertEqual(manifest.name, "controller_manifest.json")

    def test_runtime_base_dir_delegates_to_durable_state(self) -> None:
        from tools.agent_supervisor import durable_state
        self.assertEqual(platform_paths.runtime_base_dir(),
                         durable_state.runtime_base_dir())


# ---------------------------------------------------------------------------
# process: DISABLE_AUTOUPDATER belt for the bare probes on Linux, no-op on Windows
# ---------------------------------------------------------------------------
class AutoupdaterBeltTests(unittest.TestCase):
    def test_belt_is_set_on_posix(self) -> None:
        self.assertEqual(process.posix_autoupdater_belt(os_name="posix"),
                         {"DISABLE_AUTOUPDATER": "1"})

    def test_belt_is_empty_on_windows(self) -> None:
        self.assertEqual(process.posix_autoupdater_belt(os_name="nt"), {})

    def test_bare_probe_env_keeps_parent_env_and_adds_belt_on_posix(self) -> None:
        env = process.bare_probe_env({"PATH": "/usr/bin"}, os_name="posix")
        self.assertEqual(env["PATH"], "/usr/bin")
        self.assertEqual(env["DISABLE_AUTOUPDATER"], "1")

    def test_bare_probe_env_adds_no_belt_on_windows(self) -> None:
        env = process.bare_probe_env({"PATH": r"C:\bin"}, os_name="nt")
        self.assertNotIn("DISABLE_AUTOUPDATER", env)
        self.assertEqual(env["PATH"], r"C:\bin")

    def test_bare_probe_env_forced_value_wins_over_conflicting_parent(self) -> None:
        env = process.bare_probe_env({"DISABLE_AUTOUPDATER": "0"}, os_name="posix")
        self.assertEqual(env["DISABLE_AUTOUPDATER"], "1")

    def test_apply_belt_mutates_posix_environ_and_returns_true(self) -> None:
        fake: dict[str, str] = {}
        applied = process.apply_posix_autoupdater_belt(fake, os_name="posix")
        self.assertTrue(applied)
        self.assertEqual(fake["DISABLE_AUTOUPDATER"], "1")

    def test_apply_belt_is_noop_on_windows(self) -> None:
        fake: dict[str, str] = {}
        applied = process.apply_posix_autoupdater_belt(fake, os_name="nt")
        self.assertFalse(applied)
        self.assertNotIn("DISABLE_AUTOUPDATER", fake)

    def test_apply_belt_forces_value_over_conflicting_existing(self) -> None:
        fake = {"DISABLE_AUTOUPDATER": "0"}
        process.apply_posix_autoupdater_belt(fake, os_name="posix")
        self.assertEqual(fake["DISABLE_AUTOUPDATER"], "1")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
