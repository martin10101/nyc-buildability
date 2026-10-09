"""M0-T134 / D-024 Amendment 39 R511 (C3 core): complete executable-chain identity.

Proves: a COMPLETE sha256 with no size/mtime cache; full wrapper->runtime->entrypoint
chain binding; and the load-bearing mutant - a replacement that PRESERVES the byte
size and RESTORES the mtime is still rejected (a size/mtime cache would have missed
it). Plus updater-disablement and runtime model/version checks.
"""

import os
import pathlib
import tempfile
import unittest

from tools.agent_supervisor.mrl_exec_identity import (
    assert_updater_disabled,
    bind_executable_chain,
    sha256_file_complete,
    verify_executable_chain,
    verify_runtime_reported,
)
from tools.agent_supervisor.mrl_worker_result import ContractError


class ExecIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.d = pathlib.Path(self._tmp.name)
        self.wrapper = self.d / "claude.cmd"
        self.runtime = self.d / "node.exe"
        self.entry = self.d / "cli.js"
        self.wrapper.write_bytes(b"@echo off\nnode cli.js\n")
        self.runtime.write_bytes(b"RUNTIME-BYTES-v1")
        self.entry.write_bytes(b"console.log('claude');")
        self.links = [("wrapper", str(self.wrapper)), ("runtime", str(self.runtime)),
                      ("entrypoint", str(self.entry))]

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_complete_hash_distinguishes_same_size_content(self) -> None:
        a = self.d / "a"
        b = self.d / "b"
        a.write_bytes(b"AAAA")
        b.write_bytes(b"BBBB")  # same size, different bytes
        self.assertNotEqual(sha256_file_complete(a)[0], sha256_file_complete(b)[0])

    def test_bind_chain_has_all_links(self) -> None:
        identity = bind_executable_chain(self.links)
        self.assertEqual([link.role for link in identity.chain],
                         ["wrapper", "runtime", "entrypoint"])
        self.assertEqual(len(identity.combined_sha256), 64)

    def test_missing_link_fails_closed(self) -> None:
        with self.assertRaises(ContractError):
            bind_executable_chain([("runtime", str(self.d / "does-not-exist"))])

    def test_empty_chain_fails_closed(self) -> None:
        with self.assertRaises(ContractError):
            bind_executable_chain([])

    def test_verify_matches_pinned(self) -> None:
        pinned = bind_executable_chain(self.links).combined_sha256
        self.assertEqual(verify_executable_chain(self.links, pinned).combined_sha256, pinned)

    def test_same_size_restored_mtime_replacement_still_rejected(self) -> None:
        # R511 load-bearing mutant.
        pinned = bind_executable_chain(self.links).combined_sha256
        stat = os.stat(self.runtime)
        original = self.runtime.read_bytes()
        replacement = b"RUNTIME-BYTES-v2"  # SAME length as v1, different content
        self.assertEqual(len(replacement), len(original))
        self.runtime.write_bytes(replacement)
        os.utime(self.runtime, (stat.st_atime, stat.st_mtime))  # restore mtime
        # a size/mtime cache would say "unchanged"; the complete hash must still reject
        with self.assertRaises(ContractError):
            verify_executable_chain(self.links, pinned)

    def test_reordering_changes_identity(self) -> None:
        forward = bind_executable_chain(self.links).combined_sha256
        reversed_ = bind_executable_chain(list(reversed(self.links))).combined_sha256
        self.assertNotEqual(forward, reversed_)


class UpdaterAndRuntimeTests(unittest.TestCase):
    def test_updater_disabled_ok(self) -> None:
        assert_updater_disabled({"DISABLE_AUTOUPDATER": "1"})

    def test_missing_disable_autoupdater_fails(self) -> None:
        with self.assertRaises(ContractError):
            assert_updater_disabled({})
        with self.assertRaises(ContractError):
            assert_updater_disabled({"DISABLE_AUTOUPDATER": "0"})

    def test_disable_updates_prohibited(self) -> None:  # R280
        with self.assertRaises(ContractError):
            assert_updater_disabled({"DISABLE_AUTOUPDATER": "1", "DISABLE_UPDATES": "1"})

    def test_runtime_identity_match_and_mismatch(self) -> None:
        verify_runtime_reported("claude-opus-4-8", "2.1.252", "claude-opus-4-8", "2.1.252")
        with self.assertRaises(ContractError):
            verify_runtime_reported("claude-opus-4-8", "2.1.252", "claude-fable-5", "2.1.252")
        with self.assertRaises(ContractError):
            verify_runtime_reported("claude-opus-4-8", "2.1.252", "claude-opus-4-8", "2.1.251")
        with self.assertRaises(ContractError):
            verify_runtime_reported("claude-opus-4-8", "2.1.252", "", "2.1.252")
        with self.assertRaises(ContractError):  # empty observed version also fails closed
            verify_runtime_reported("claude-opus-4-8", "2.1.252", "claude-opus-4-8", "")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
