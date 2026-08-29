#!/usr/bin/env python3
"""Fake-process harness and process-control tests (D-007 S13, S15).

This is the Phase 1 fake-executable harness the later phases build their
integration tests on. It writes FAKE `claude` and `codex` executables (temp
Python scripts run with the current interpreter) that emit the supervisor's own
protocol envelopes. There are NO real provider calls, NO tokens, and NO network
here.

S15 "parsing and processes" items covered: argv-array-only invocation with proof
of no shell interpolation, hostile prompt text (quotes, pipes, redirects,
metacharacters), paths with spaces, interleaved stderr, output flood, nonzero
exit, timeout with Windows child-tree cleanup, and the fake-executable round
trip for both providers.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile
import textwrap
import time
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import CONTROLLER_VERSION  # noqa: E402
from tools.agent_supervisor import process as pc  # noqa: E402
from tools.agent_supervisor import protocol as pr  # noqa: E402
from tools.agent_supervisor.models import CodexDecision, digest_of  # noqa: E402

# --------------------------------------------------------------------------
# Fake executables
# --------------------------------------------------------------------------

FAKE_CLAUDE = textwrap.dedent('''
    """FAKE claude worker. Emits protocol envelopes. No network, no tokens."""
    import hashlib, json, os, sys, time

    def digest(obj):
        return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                         ensure_ascii=False).encode("utf-8")).hexdigest()

    def envelope(seq, payload, payload_type="claude_checkpoint"):
        return {
            "protocol_version": "PROTOCOL", "schema_version": "SCHEMA",
            "message_id": "msg_fake_%d" % seq, "correlation_id": "corr-1",
            "sequence": seq, "run_id": "run-1", "task_id": "M0-T036",
            "payload_type": payload_type, "created_at_utc": "2026-08-03T00:00:00.000Z",
            "producer": "claude", "producer_version": "fake-2.1.220",
            "payload_digest": digest(payload), "payload": payload,
        }

    mode = os.environ.get("FAKE_MODE", "normal")
    argv = sys.argv[1:]

    if mode == "hang":
        time.sleep(600)
    if mode == "stderr_noise":
        sys.stderr.write("fake stderr banner\\n"); sys.stderr.flush()
    if mode == "flood":
        for i in range(1, 201):
            sys.stdout.write(json.dumps(envelope(i, {"unit": i})) + "\\n")
        sys.stdout.flush(); raise SystemExit(0)

    payload = {
        "schema_version": "SCHEMA", "run_id": "run-1", "checkpoint_id": "cp-1",
        "task_id": "M0-T036", "claude_session_id": "sess-1", "status": "UNIT_COMPLETE",
        "summary": "fake unit complete", "starting_sha": "a" * 40, "current_sha": "b" * 40,
        "branch": "task/M0-T036-supervisor-bridge", "worktree": "/fake/worktree",
        "proposed_next_action": "await review", "usage": "unknown",
        "context_pressure": "unknown", "commands_run": [{"argv": argv, "exit_code": 0}],
    }
    sys.stdout.write("banner line that is not json\\n")
    sys.stdout.write(json.dumps(envelope(1, payload)) + "\\n")
    sys.stdout.flush()
    if mode == "nonzero":
        raise SystemExit(3)
''')

FAKE_CODEX = textwrap.dedent('''
    """FAKE codex reviewer. Emits one decision envelope. Read-only, no network."""
    import hashlib, json, os, sys

    def digest(obj):
        return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                         ensure_ascii=False).encode("utf-8")).hexdigest()

    stdin_text = sys.stdin.read() if not sys.stdin.isatty() else ""
    payload = {
        "schema_version": "SCHEMA", "decision": os.environ.get("FAKE_DECISION", "CONTINUE"),
        "reviewed_task_id": "M0-T036", "reviewed_checkpoint_id": "cp-1",
        "verified_repo_head": "b" * 40, "verified_origin_main": "c" * 40,
        "model_used": "fake-codex-model",
        "next_claude_prompt": "proceed with the next authorized unit",
        "verified_facts": [{"fact": "packet bytes received", "len": len(stdin_text)}],
        "evidence_refs": [{"path": "project-control/tasks/M0-T036.json"}],
    }
    envelope = {
        "protocol_version": "PROTOCOL", "schema_version": "SCHEMA",
        "message_id": "msg_codex_1", "correlation_id": "corr-1", "sequence": 1,
        "run_id": "run-1", "task_id": "M0-T036", "payload_type": "codex_decision",
        "created_at_utc": "2026-08-03T00:00:00.000Z", "producer": "codex",
        "producer_version": "fake-0.146.0", "payload_digest": digest(payload),
        "payload": payload,
    }
    sys.stdout.write(json.dumps(envelope) + "\\n")
''')

FAKE_TREE_PARENT = textwrap.dedent('''
    """Spawns a grandchild, then sleeps. Used to prove process-TREE termination."""
    import pathlib, subprocess, sys, time

    marker_dir = pathlib.Path(sys.argv[1])
    grandchild = marker_dir / "grandchild.py"
    grandchild.write_text(
        "import pathlib, sys, time\\n"
        "d = pathlib.Path(sys.argv[1])\\n"
        "(d / 'grandchild_started').write_text('1')\\n"
        "time.sleep(30)\\n"
        "(d / 'grandchild_finished').write_text('1')\\n",
        encoding="utf-8")
    subprocess.Popen([sys.executable, str(grandchild), str(marker_dir)])
    (marker_dir / "parent_started").write_text("1")
    time.sleep(30)
    (marker_dir / "parent_finished").write_text("1")
''')


def materialize(directory: pathlib.Path, name: str, source: str) -> pathlib.Path:
    """Write a fake executable, substituting the live protocol/schema versions."""
    from tools.agent_supervisor import PROTOCOL_VERSION, SCHEMA_VERSION

    path = directory / name
    path.write_text(
        source.replace("PROTOCOL", PROTOCOL_VERSION).replace("SCHEMA", SCHEMA_VERSION),
        encoding="utf-8")
    return path


def wait_for(path: pathlib.Path, timeout: float = 15.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            return True
        time.sleep(0.05)
    return False


class ProcessTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name)

    def env(self, **extra: str) -> dict[str, str]:
        return pc.minimal_env(extra)

    def parse(self, result: pc.ProcessResult) -> list:
        reader = pr.EnvelopeReader()
        envelopes = list(reader.feed(result.stdout))
        envelopes.extend(reader.close())
        return envelopes


# --------------------------------------------------------------------------
# Argument safety
# --------------------------------------------------------------------------


class ArgvSafetyTests(unittest.TestCase):
    def test_a_command_string_is_never_accepted(self) -> None:
        with self.assertRaises(pc.ProcessError) as ctx:
            pc.assert_argv_safe("echo hello && rm -rf /")
        self.assertEqual(ctx.exception.code, "argv_not_a_list")

    def test_empty_and_non_string_argv_are_refused(self) -> None:
        with self.assertRaises(pc.ProcessError):
            pc.assert_argv_safe([])
        with self.assertRaises(pc.ProcessError) as ctx:
            pc.assert_argv_safe(["exe", 42])
        self.assertEqual(ctx.exception.code, "argv_not_string")

    def test_embedded_nul_is_refused(self) -> None:
        with self.assertRaises(pc.ProcessError) as ctx:
            pc.assert_argv_safe(["exe", "a\x00b"])
        self.assertEqual(ctx.exception.code, "argv_nul")

    def test_every_bypass_flag_is_hard_denied(self) -> None:
        for flag in sorted(pc.HARD_DENY_ARGUMENTS):
            with self.assertRaises(pc.HardDenyError) as ctx:
                pc.assert_argv_safe(["claude", flag])
            self.assertEqual(ctx.exception.argument, flag)

    def test_bypass_flags_are_denied_case_insensitively(self) -> None:
        with self.assertRaises(pc.HardDenyError):
            pc.assert_argv_safe(["claude", "--DANGEROUSLY-SKIP-PERMISSIONS"])

    def test_effort_flags_are_denied(self) -> None:
        for flag in ("--effort", "--effort=high", "--reasoning-effort",
                     "--reasoning-effort=low"):
            with self.assertRaises(pc.HardDenyError) as ctx:
                pc.assert_argv_safe(["claude", flag])
            self.assertIn("permanently prohibited", ctx.exception.reason)

    def test_ordinary_arguments_pass_through_unchanged(self) -> None:
        argv = ["claude", "-p", "--output-format", "stream-json", "--max-turns", "1"]
        self.assertEqual(pc.assert_argv_safe(argv), argv)


# --------------------------------------------------------------------------
# Environment hygiene
# --------------------------------------------------------------------------


class EnvironmentTests(unittest.TestCase):
    def test_minimal_env_drops_ambient_credentials(self) -> None:
        os.environ["FAKE_SUPERVISOR_TOKEN"] = "sk-ant-" + "Q" * 40
        self.addCleanup(os.environ.pop, "FAKE_SUPERVISOR_TOKEN", None)
        env = pc.minimal_env()
        self.assertNotIn("FAKE_SUPERVISOR_TOKEN", env)
        self.assertTrue(any(key.upper() == "PATH" for key in env))

    def test_explicit_extras_are_honoured(self) -> None:
        env = pc.minimal_env({"FAKE_MODE": "normal"})
        self.assertEqual(env["FAKE_MODE"], "normal")

    def test_minimal_env_does_not_inject_the_claude_autoupdater_control(self) -> None:
        # D-024-R278 (M0-T117): DISABLE_AUTOUPDATER=1 is CLAUDE-scoped and lives in
        # `claude_child_env`. The shared `minimal_env` - which codex children also
        # use - must never add it, or the control would leak into codex (AS-5).
        os.environ.pop("DISABLE_AUTOUPDATER", None)
        self.assertNotIn("DISABLE_AUTOUPDATER", pc.minimal_env())
        self.assertNotIn("DISABLE_AUTOUPDATER", pc.minimal_env({"FAKE_MODE": "x"}))

    def test_claude_child_env_forces_the_autoupdater_control(self) -> None:
        # The claude-scoped helper adds exactly the forced pair on top of
        # minimal_env, and a conflicting extra_env cannot win (forced pair wins).
        os.environ.pop("DISABLE_AUTOUPDATER", None)
        self.assertEqual(pc.claude_child_env()["DISABLE_AUTOUPDATER"], "1")
        self.assertEqual(
            pc.claude_child_env({"DISABLE_AUTOUPDATER": "0"})["DISABLE_AUTOUPDATER"], "1")


# --------------------------------------------------------------------------
# Executable resolution and identity
# --------------------------------------------------------------------------


class ExecutableTests(ProcessTestCase):
    def test_repo_local_shadowing_is_refused(self) -> None:
        repo = self.tmp / "repo"
        bin_dir = repo / "bin"
        bin_dir.mkdir(parents=True)
        name = "fakegit.exe" if os.name == "nt" else "fakegit"
        (bin_dir / name).write_text("#!/bin/sh\necho shadowed\n", encoding="utf-8")
        (bin_dir / name).chmod(0o755)
        with self.assertRaises(pc.ProcessError) as ctx:
            pc.resolve_executable("fakegit", repo_root=repo, search_path=str(bin_dir))
        self.assertEqual(ctx.exception.code, "repo_local_shadowing")

    def test_missing_executable_is_reported(self) -> None:
        with self.assertRaises(pc.ProcessError) as ctx:
            pc.resolve_executable("definitely-not-installed-xyz",
                                  search_path=str(self.tmp))
        self.assertEqual(ctx.exception.code, "executable_not_found")

    def test_identity_records_a_full_digest_for_small_files(self) -> None:
        target = self.tmp / "small.bin"
        target.write_bytes(b"hello")
        identity = pc.executable_identity(target)
        self.assertEqual(identity.digest_kind, "sha256")
        self.assertEqual(identity.size_bytes, 5)
        self.assertEqual(len(identity.digest), 64)

    def test_current_interpreter_is_resolvable(self) -> None:
        identity = pc.executable_identity(sys.executable, name="python")
        self.assertEqual(identity.name, "python")
        self.assertIn(identity.digest_kind, ("sha256", "sha256_head+size"))


# --------------------------------------------------------------------------
# Fake worker / reviewer round trips
# --------------------------------------------------------------------------


class FakeExecutableTests(ProcessTestCase):
    def test_fake_claude_checkpoint_round_trip(self) -> None:
        script = materialize(self.tmp, "fake_claude.py", FAKE_CLAUDE)
        result = pc.run(pc.python_argv(script, "-p", "--max-turns", "1"),
                        env=self.env(FAKE_MODE="normal"), timeout=60)
        self.assertTrue(result.ok, result.stderr)
        envelopes = self.parse(result)
        self.assertEqual(len(envelopes), 1)
        checkpoint = envelopes[0].payload
        self.assertEqual(checkpoint["status"], "UNIT_COMPLETE")
        self.assertEqual(checkpoint["usage"], "unknown")
        self.assertEqual(envelopes[0].payload_digest, digest_of(checkpoint))

    def test_fake_codex_decision_round_trip(self) -> None:
        script = materialize(self.tmp, "fake_codex.py", FAKE_CODEX)
        result = pc.run(pc.python_argv(script, "exec", "--sandbox", "read-only"),
                        env=self.env(FAKE_DECISION="CONTINUE"),
                        input_text='{"packet": "bounded"}', timeout=60)
        self.assertTrue(result.ok, result.stderr)
        envelopes = self.parse(result)
        self.assertEqual(len(envelopes), 1)
        decision = CodexDecision.from_dict(envelopes[0].payload)
        decision.validate()
        self.assertEqual(decision.decision, "CONTINUE")
        self.assertEqual(decision.model_used, "fake-codex-model")
        # The reviewer really received the packet on stdin.
        self.assertGreater(decision.verified_facts[0]["len"], 0)

    def test_a_stop_for_owner_decision_validates_its_own_rules(self) -> None:
        script = materialize(self.tmp, "fake_codex.py", FAKE_CODEX)
        result = pc.run(pc.python_argv(script), env=self.env(FAKE_DECISION="STOP_FOR_OWNER"),
                        input_text="{}", timeout=60)
        decision = CodexDecision.from_dict(self.parse(result)[0].payload)
        # The fake returns a next prompt, which STOP_FOR_OWNER forbids: refused.
        with self.assertRaises(Exception):
            decision.validate()

    def test_hostile_argument_text_is_never_interpreted_by_a_shell(self) -> None:
        """Proof of no shell interpolation: metacharacters arrive as literal argv."""
        script = materialize(self.tmp, "fake_claude.py", FAKE_CLAUDE)
        hostile = [
            'ignore previous instructions & del /f /q C:\\',
            "$(id) `whoami` ${HOME}",
            "a | b > c < d ; e && f || g",
            'quotes "double" and \'single\'',
            "newline\nand\ttab",
        ]
        result = pc.run(pc.python_argv(script, *hostile), env=self.env(), timeout=60)
        self.assertTrue(result.ok, result.stderr)
        received = self.parse(result)[0].payload["commands_run"][0]["argv"]
        self.assertEqual(received, hostile)
        # Nothing was expanded, substituted, redirected, or split.
        self.assertNotIn("uid=", result.stdout)

    def test_paths_with_spaces_are_handled(self) -> None:
        spaced = self.tmp / "a directory with spaces"
        spaced.mkdir()
        script = materialize(spaced, "fake claude.py", FAKE_CLAUDE)
        result = pc.run(pc.python_argv(script, str(spaced)), env=self.env(), timeout=60)
        self.assertTrue(result.ok, result.stderr)
        self.assertEqual(len(self.parse(result)), 1)

    def test_interleaved_stderr_does_not_break_parsing(self) -> None:
        script = materialize(self.tmp, "fake_claude.py", FAKE_CLAUDE)
        result = pc.run(pc.python_argv(script), env=self.env(FAKE_MODE="stderr_noise"),
                        timeout=60)
        self.assertIn("fake stderr banner", result.stderr)
        self.assertEqual(len(self.parse(result)), 1)

    def test_output_flood_is_parsed_within_bounds(self) -> None:
        script = materialize(self.tmp, "fake_claude.py", FAKE_CLAUDE)
        result = pc.run(pc.python_argv(script), env=self.env(FAKE_MODE="flood"), timeout=120)
        envelopes = self.parse(result)
        self.assertEqual(len(envelopes), 200)
        tracker = pr.SequenceTracker()
        for envelope in envelopes:
            self.assertEqual(tracker.accept(envelope).verdict, pr.ACCEPTED)

    def test_nonzero_exit_is_never_read_as_success(self) -> None:
        script = materialize(self.tmp, "fake_claude.py", FAKE_CLAUDE)
        result = pc.run(pc.python_argv(script), env=self.env(FAKE_MODE="nonzero"), timeout=60)
        self.assertEqual(result.returncode, 3)
        self.assertFalse(result.ok)
        # A well-formed checkpoint alongside a nonzero exit is still not success.
        self.assertEqual(len(self.parse(result)), 1)


class CaptureBoundTests(ProcessTestCase):
    """G5 M0-T042 I-3: child stdout capture is bounded, with a visible marker."""

    def test_oversized_stdout_is_capped_with_a_structured_marker(self) -> None:
        # A child that floods stdout with 100k characters.
        result = pc.run(
            [sys.executable, "-c", "import sys; sys.stdout.write('x' * 100000)"],
            env=self.env(), timeout=60, max_capture_bytes=1000)
        self.assertTrue(result.stdout_truncated)
        # Retained bytes are bounded to the cap plus the (bounded) marker, never
        # the full 100k, and the truncation is never silent.
        self.assertLess(len(result.stdout), 100000)
        self.assertTrue(result.stdout.startswith("x" * 1000))
        self.assertIn("[STDOUT TRUNCATED", result.stdout)
        self.assertIn("retained 1000 of 100000", result.stdout)

    def test_output_within_the_cap_is_untouched_and_not_flagged(self) -> None:
        result = pc.run(
            [sys.executable, "-c", "import sys; sys.stdout.write('hello')"],
            env=self.env(), timeout=60, max_capture_bytes=1000)
        self.assertFalse(result.stdout_truncated)
        self.assertEqual(result.stdout, "hello")
        self.assertNotIn("TRUNCATED", result.stdout)


# --------------------------------------------------------------------------
# Timeouts and process-tree termination
# --------------------------------------------------------------------------


class TimeoutAndTreeTests(ProcessTestCase):
    def test_timeout_terminates_and_is_not_success(self) -> None:
        script = materialize(self.tmp, "fake_claude.py", FAKE_CLAUDE)
        started = time.monotonic()
        result = pc.run(pc.python_argv(script), env=self.env(FAKE_MODE="hang"), timeout=2)
        elapsed = time.monotonic() - started
        self.assertTrue(result.timed_out)
        self.assertFalse(result.ok)
        self.assertLess(elapsed, 60, "the timeout did not bound the run")

    def test_process_tree_termination_kills_descendants(self) -> None:
        markers = self.tmp / "markers"
        markers.mkdir()
        script = materialize(self.tmp, "tree_parent.py", FAKE_TREE_PARENT)

        import subprocess

        popen_kwargs: dict[str, object] = {"shell": False}
        if os.name != "nt":
            popen_kwargs["start_new_session"] = True
        parent = subprocess.Popen(  # noqa: S603 - argv array, shell=False
            pc.python_argv(script, str(markers)), **popen_kwargs)  # type: ignore[arg-type]
        self.addCleanup(lambda: parent.poll() is None and parent.kill())

        self.assertTrue(wait_for(markers / "grandchild_started"),
                        "the grandchild never started; the test proves nothing")
        self.assertTrue(pc.terminate_process_tree(parent.pid))

        time.sleep(3)
        self.assertFalse((markers / "grandchild_finished").exists(),
                         "the grandchild survived termination of its parent's tree")
        self.assertFalse((markers / "parent_finished").exists())

    @unittest.skipUnless(os.name == "nt", "Job Objects are Windows-only")
    def test_job_object_kill_on_close_contains_a_child(self) -> None:
        self.assertTrue(pc.job_objects_available())
        markers = self.tmp / "job_markers"
        markers.mkdir()
        script = materialize(self.tmp, "tree_parent.py", FAKE_TREE_PARENT)

        import subprocess

        job = pc.WindowsJobObject()
        child = subprocess.Popen(  # noqa: S603 - argv array, shell=False
            pc.python_argv(script, str(markers)), shell=False)
        self.addCleanup(lambda: child.poll() is None and child.kill())
        try:
            job.assign_pid(child.pid)
            self.assertTrue(wait_for(markers / "parent_started"))
        finally:
            job.close()  # kill-on-close

        time.sleep(3)
        self.assertFalse((markers / "parent_finished").exists(),
                         "the job object did not terminate its assigned process")

    @unittest.skipIf(os.name == "nt", "POSIX-only guard")
    def test_job_objects_report_unavailable_off_windows(self) -> None:
        self.assertFalse(pc.job_objects_available())
        with self.assertRaises(pc.ProcessError):
            pc.WindowsJobObject()


class ProcessResultTests(unittest.TestCase):
    def test_result_carries_the_exact_argv_it_ran(self) -> None:
        result = pc.run([sys.executable, "-c", "print('ok')"], timeout=60)
        self.assertEqual(result.argv[0], sys.executable)
        self.assertIn("ok", result.stdout)
        self.assertTrue(result.ok)

    def test_controller_version_matches_the_declared_phase(self) -> None:
        # Phase 2 update: the assertion was `endswith("phase1")`. The controller
        # version is embedded in the manifest, in every audit record, and in the
        # durable journal, so a Phase 2 build reporting "phase1" would be a false
        # provenance claim. The check is now tied to the declared PHASE instead of
        # to a frozen string, so it stays true across later phases.
        from tools.agent_supervisor import PHASE

        self.assertRegex(CONTROLLER_VERSION, r"^\d+\.\d+\.\d+-phase\d+$")
        self.assertTrue(CONTROLLER_VERSION.endswith(f"phase{PHASE}"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
