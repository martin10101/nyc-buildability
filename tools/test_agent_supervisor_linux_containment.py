#!/usr/bin/env python3
"""Linux systemd control-group containment proof tests (M0-T177, B-027).

Qualifying evidence: B-027 (reproduced defect); D-091-R001, D-091-R007.

Coverage map (packet acceptance scenarios):

  * POSITIVE   - a valid injected cgroup + `systemctl show` PROVES containment;
                 default_containment_kind() is systemd_cgroup; the container
                 reports systemd_cgroup with verified membership; the start gate
                 accepts.  (scenario 1; "start dispatches"/"cycle proceeds" are in
                 test_agent_supervisor_start_reentry.py and _loop.py.)
  * NEGATIVE   - one test per refusal reason in scenario 2.
  * MUTATION   - each guard is load-bearing (scenario 3); the real-process R1 and
                 the accept-set/own-group unit tests catch the launch/kill guards.
  * R1 / R2    - bounded SINGLE real-process test ids (30 s cap; tearDown SIGKILLs
                 every recorded pid). NEVER run whole on this host.
  * R3         - opt-in, env-gated (NYC_SUP_R3_SYSTEMD=1); a real transient systemd
                 unit. Runs ONLY in Linux CI or an owner-typed step, NEVER here.
"""
from __future__ import annotations

import os
import pathlib
import signal
import subprocess
import sys
import textwrap
import time
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import cli  # noqa: E402
from tools.agent_supervisor import linux_containment as lc  # noqa: E402
from tools.agent_supervisor import process as pc  # noqa: E402

POSIX_ONLY = unittest.skipUnless(os.name != "nt", "POSIX-only containment")

SERVICE_CGROUP_PATH = "/system.slice/nyc-supervisor.service"
VALID_CGROUP = f"0::{SERVICE_CGROUP_PATH}\n"


def _valid_props(pid: int, **overrides: str) -> dict[str, str]:
    props = {
        "KillMode": "control-group",
        "ExitType": "main",
        "MainPID": str(pid),
        "ControlGroup": SERVICE_CGROUP_PATH,
        "SendSIGKILL": "yes",
        "TimeoutStopUSec": "15s",
        "ProtectControlGroups": "yes",
    }
    props.update(overrides)
    return props


def _show_runner(props: dict[str, str], *, code: int = 0, stderr: str = "",
                 drop: tuple[str, ...] = ()):
    """A fake `systemctl show` runner returning KEY=VALUE lines for `props`."""

    def runner(unit: str, requested):
        emitted = {k: v for k, v in props.items() if k not in drop}
        text = "\n".join(f"{k}={v}" for k, v in emitted.items()) + "\n"
        return code, text, stderr

    return runner


def _prove(pid: int = 4321, euid: int = 1000, *, cgroup: str = VALID_CGROUP,
           props: dict[str, str] | None = None, **runner_kwargs) -> lc.ContainmentProof:
    show = _show_runner(props if props is not None else _valid_props(pid), **runner_kwargs)
    return lc.prove_systemd_containment(
        pid=pid, euid=euid, cgroup_reader=lambda: cgroup, show_runner=show)


# --------------------------------------------------------------------------
# POSITIVE
# --------------------------------------------------------------------------


@POSIX_ONLY
class PositiveProofTests(unittest.TestCase):
    def test_a_valid_service_cgroup_and_show_prove_containment(self) -> None:
        proof = _prove()
        self.assertTrue(proof.ok, proof.reason)
        self.assertEqual(proof.kind, pc.CONTAINMENT_SYSTEMD_CGROUP)
        self.assertEqual(proof.cgroup_path, SERVICE_CGROUP_PATH)
        self.assertEqual(proof.unit, "nyc-supervisor.service")

    def test_root_with_protect_control_groups_proves(self) -> None:
        proof = _prove(euid=0)  # ProtectControlGroups=yes is in the valid props
        self.assertTrue(proof.ok, proof.reason)

    def test_mixed_kill_mode_proves(self) -> None:
        proof = _prove(props=_valid_props(4321, KillMode="mixed"))
        self.assertTrue(proof.ok, proof.reason)

    def test_raw_microsecond_timeout_proves(self) -> None:
        proof = _prove(props=_valid_props(4321, TimeoutStopUSec="15000000"))
        self.assertTrue(proof.ok, proof.reason)

    @POSIX_ONLY
    def test_default_containment_kind_is_systemd_cgroup_when_proved(self) -> None:
        self.addCleanup(pc.reset_systemd_containment_cache)
        pc.set_systemd_containment_proof_for_testing(_prove())
        self.assertEqual(pc.default_containment_kind(), pc.CONTAINMENT_SYSTEMD_CGROUP)

    @POSIX_ONLY
    def test_container_reports_systemd_cgroup_and_verifies_membership(self) -> None:
        proof = _prove()
        box = pc.ProcessContainer(posix_proof=proof, membership_check=lambda p, c: True)
        self.assertEqual(box.adopt(1234), pc.CONTAINMENT_SYSTEMD_CGROUP)
        report = box.report()
        self.assertEqual(report.kind, pc.CONTAINMENT_SYSTEMD_CGROUP)
        self.assertTrue(report.verified_in_job)

    @POSIX_ONLY
    def test_start_gate_accepts_a_proved_systemd_host(self) -> None:
        self.addCleanup(pc.reset_systemd_containment_cache)
        pc.set_systemd_containment_proof_for_testing(_prove())
        ok, kind, _ = cli.containment_precondition()
        self.assertTrue(ok)
        self.assertEqual(kind, pc.CONTAINMENT_SYSTEMD_CGROUP)


# --------------------------------------------------------------------------
# NEGATIVE - one refusal reason per test (packet scenario 2)
# --------------------------------------------------------------------------


@POSIX_ONLY
class NegativeRefusalTests(unittest.TestCase):
    def _refused(self, proof: lc.ContainmentProof, needle: str) -> None:
        self.assertFalse(proof.ok, f"expected a refusal, got ok: {proof.reason}")
        self.assertEqual(proof.kind, pc.CONTAINMENT_PROCESS_GROUP)
        self.assertIn(needle, proof.reason)

    def test_cgroup_v1_or_hybrid_is_refused(self) -> None:
        hybrid = "0::/system.slice/nyc-supervisor.service\n1:name=systemd:/legacy\n"
        self._refused(_prove(cgroup=hybrid), "pure cgroup-v2")

    def test_a_scope_or_user_session_path_is_refused(self) -> None:
        scope = "0::/user.slice/user-0.slice/session-3.scope\n"
        self._refused(_prove(cgroup=scope), "not a systemd .service")

    def test_kill_mode_process_is_refused(self) -> None:
        self._refused(_prove(props=_valid_props(4321, KillMode="process")), "KillMode=")

    def test_kill_mode_none_is_refused(self) -> None:
        self._refused(_prove(props=_valid_props(4321, KillMode="none")), "KillMode=")

    def test_exit_type_cgroup_is_refused(self) -> None:
        self._refused(_prove(props=_valid_props(4321, ExitType="cgroup")), "ExitType=")

    def test_main_pid_mismatch_is_refused(self) -> None:
        props = _valid_props(4321, MainPID="999")  # unit MainPID != our pid 4321
        self._refused(_prove(props=props), "MainPID=999")

    def test_control_group_mismatch_is_refused(self) -> None:
        props = _valid_props(4321, ControlGroup="/system.slice/other.service")
        self._refused(_prove(props=props), "does not match our cgroup")

    def test_send_sigkill_no_is_refused(self) -> None:
        self._refused(_prove(props=_valid_props(4321, SendSIGKILL="no")), "SendSIGKILL=")

    def test_timeout_infinity_is_refused(self) -> None:
        props = _valid_props(4321, TimeoutStopUSec="infinity")
        self._refused(_prove(props=props), "infinite, zero, or unparseable")

    def test_timeout_above_cap_is_refused(self) -> None:
        props = _valid_props(4321, TimeoutStopUSec="90s")  # > 60 s cap
        self._refused(_prove(props=props), "exceeds the")

    def test_timeout_garbled_is_refused(self) -> None:
        props = _valid_props(4321, TimeoutStopUSec="soon-ish")
        self._refused(_prove(props=props), "infinite, zero, or unparseable")

    def test_systemctl_missing_is_refused(self) -> None:
        def explode(unit, props):
            raise FileNotFoundError("systemctl not found")

        proof = lc.prove_systemd_containment(
            pid=4321, euid=1000, cgroup_reader=lambda: VALID_CGROUP, show_runner=explode)
        self._refused(proof, "could not run")

    def test_systemctl_nonzero_is_refused(self) -> None:
        self._refused(_prove(code=5, stderr="Unit not loaded"), "exited 5")

    def test_systemctl_timed_out_is_refused(self) -> None:
        def timed_out(unit, props):
            raise subprocess.TimeoutExpired(cmd="systemctl", timeout=5.0)

        proof = lc.prove_systemd_containment(
            pid=4321, euid=1000, cgroup_reader=lambda: VALID_CGROUP, show_runner=timed_out)
        self._refused(proof, "could not run")

    def test_systemctl_garbled_partial_output_is_refused(self) -> None:
        # Drop ControlGroup from the output -> a partial/garbled unit state.
        self._refused(_prove(drop=("ControlGroup",)), "did not report")

    def test_unreadable_cgroup_is_refused(self) -> None:
        def explode():
            raise PermissionError("no read")

        proof = lc.prove_systemd_containment(
            pid=4321, euid=1000, cgroup_reader=explode, show_runner=_show_runner({}))
        self._refused(proof, "could not be read")

    def test_root_without_protect_control_groups_is_refused(self) -> None:
        props = _valid_props(4321, ProtectControlGroups="no")
        self._refused(_prove(euid=0, props=props), "ProtectControlGroups=yes")

    @POSIX_ONLY
    def test_a_worker_in_a_foreign_cgroup_is_not_verified(self) -> None:
        # Membership fails closed -> the container reports verified_in_job False,
        # which the loop post-cycle gate turns into `containment_unverified`.
        proof = _prove()
        box = pc.ProcessContainer(posix_proof=proof, membership_check=lambda p, c: False)
        box.adopt(1234)
        self.assertFalse(box.report().verified_in_job)

    @POSIX_ONLY
    def test_process_group_host_refuses_at_the_start_gate(self) -> None:
        self.addCleanup(pc.reset_systemd_containment_cache)
        pc.set_systemd_containment_proof_for_testing(
            lc.ContainmentProof.refused("not a service"))
        ok, kind, detail = cli.containment_precondition()
        self.assertFalse(ok)
        self.assertEqual(kind, pc.CONTAINMENT_PROCESS_GROUP)
        self.assertIn("systemd .service", detail)

    def test_taskkill_host_refuses_at_the_start_gate(self) -> None:
        original = cli.default_containment_kind
        cli.default_containment_kind = lambda: pc.CONTAINMENT_TASKKILL  # type: ignore[assignment]
        try:
            ok, kind, _ = cli.containment_precondition()
        finally:
            cli.default_containment_kind = original  # type: ignore[assignment]
        self.assertFalse(ok)
        self.assertEqual(kind, pc.CONTAINMENT_TASKKILL)

    def test_option_like_unit_name_is_passed_through_not_interpreted(self) -> None:
        # G5 NB3: a crafted cgroup yielding an option-like unit (`-x.service`) must
        # be a refusal, and the unit must reach `systemctl show` verbatim (after
        # `--`), never parsed as a flag.
        seen: dict[str, str] = {}

        def runner(unit: str, props):
            seen["unit"] = unit
            return 1, "", "Failed to show -x.service: no such unit"

        proof = lc.prove_systemd_containment(
            pid=1, euid=1000, cgroup_reader=lambda: "0::/system.slice/-x.service\n",
            show_runner=runner)
        self.assertEqual(seen["unit"], "-x.service")
        self.assertFalse(proof.ok)
        self.assertIn("exited 1", proof.reason)


# --------------------------------------------------------------------------
# Parser units (support the negatives above; direct, fast)
# --------------------------------------------------------------------------


@POSIX_ONLY
class ParserTests(unittest.TestCase):
    def test_parse_cgroup_v2_single_service_line(self) -> None:
        self.assertEqual(lc.parse_cgroup_v2_path(VALID_CGROUP), SERVICE_CGROUP_PATH)

    def test_parse_cgroup_v2_rejects_multiple_lines(self) -> None:
        self.assertIsNone(lc.parse_cgroup_v2_path("0::/a\n2:cpu:/b\n"))

    def test_parse_cgroup_v2_rejects_non_zero_prefix(self) -> None:
        self.assertIsNone(lc.parse_cgroup_v2_path("1:name=systemd:/a\n"))

    def test_parse_systemd_usec_forms(self) -> None:
        self.assertEqual(lc.parse_systemd_usec("15s"), 15_000_000)
        self.assertEqual(lc.parse_systemd_usec("1min 30s"), 90_000_000)
        self.assertEqual(lc.parse_systemd_usec("500ms"), 500_000)
        self.assertEqual(lc.parse_systemd_usec("15000000"), 15_000_000)

    def test_parse_systemd_usec_rejects_infinity_zero_and_junk(self) -> None:
        self.assertIsNone(lc.parse_systemd_usec("infinity"))
        self.assertIsNone(lc.parse_systemd_usec("0"))
        self.assertIsNone(lc.parse_systemd_usec(""))
        self.assertIsNone(lc.parse_systemd_usec("15 potatoes"))
        self.assertIsNone(lc.parse_systemd_usec("15s extra"))

    def test_pid_in_service_cgroup_matches_and_fails_closed(self) -> None:
        self.assertTrue(lc.pid_in_service_cgroup(
            1, SERVICE_CGROUP_PATH, reader=lambda: VALID_CGROUP))
        self.assertFalse(lc.pid_in_service_cgroup(
            1, SERVICE_CGROUP_PATH, reader=lambda: "0::/user.slice/other.scope\n"))

        def explode():
            raise FileNotFoundError

        self.assertFalse(lc.pid_in_service_cgroup(1, SERVICE_CGROUP_PATH, reader=explode))

    def test_systemctl_show_argv_puts_unit_after_double_dash(self) -> None:
        # G5 NB3: options precede `--`; the unit is the sole positional after it,
        # so an option-like unit name can never be parsed as a flag.
        argv = lc.systemctl_show_argv("-x.service", lc.SYSTEMCTL_PROPERTIES)
        self.assertIn("--", argv)
        self.assertEqual(argv[-1], "-x.service")
        self.assertLess(argv.index("-p"), argv.index("--"))
        self.assertGreater(len(argv) - 1, argv.index("--"))


# --------------------------------------------------------------------------
# MUTATION - each guard is load-bearing (scenario 3)
# --------------------------------------------------------------------------


@POSIX_ONLY
class MutationGuardTests(unittest.TestCase):
    def test_accept_set_is_exactly_the_two_kill_on_death_kinds(self) -> None:
        # If the accept-set is WIDENED (e.g. to include process_group or taskkill),
        # this equality fails. The loop/start gates all read this one constant.
        self.assertEqual(
            pc.CONTAINMENT_ACCEPT_SET,
            frozenset({pc.CONTAINMENT_JOB_OBJECT, pc.CONTAINMENT_SYSTEMD_CGROUP}))
        self.assertNotIn(pc.CONTAINMENT_PROCESS_GROUP, pc.CONTAINMENT_ACCEPT_SET)
        self.assertNotIn(pc.CONTAINMENT_TASKKILL, pc.CONTAINMENT_ACCEPT_SET)

    def test_main_pid_guard_is_load_bearing(self) -> None:
        # Dropping the MainPID==getpid() check would let a non-main process prove
        # containment; this refusal is the proof the guard is present.
        proof = _prove(props=_valid_props(4321, MainPID="999"))
        self.assertFalse(proof.ok)
        self.assertIn("MainPID=999", proof.reason)

    @POSIX_ONLY
    def test_terminate_process_tree_refuses_to_kill_our_own_group(self) -> None:
        # The own-process-group kill guard: terminate_process_tree must REFUSE to
        # killpg the caller's own group. Remove the guard and killpg would be
        # invoked on our own group (the B-027 self-kill). Inject the pgid lookups
        # and killpg so nothing real is signalled.
        with mock.patch.object(pc.os, "getpgid", return_value=777), \
                mock.patch.object(pc.os, "getpgrp", return_value=777), \
                mock.patch.object(pc.os, "killpg") as killpg:
            with self.assertRaises(pc.ProcessError) as ctx:
                pc.terminate_process_tree(12345)
        self.assertEqual(ctx.exception.code, "refuse_self_group_kill")
        killpg.assert_not_called()

    @POSIX_ONLY
    def test_terminate_process_tree_kills_a_foreign_group(self) -> None:
        # The mirror: a DIFFERENT group (a session-isolated worker) IS killed.
        with mock.patch.object(pc.os, "getpgid", return_value=888), \
                mock.patch.object(pc.os, "getpgrp", return_value=777), \
                mock.patch.object(pc.os, "killpg") as killpg:
            self.assertTrue(pc.terminate_process_tree(12345))
        killpg.assert_called_once_with(888, 9)

    @POSIX_ONLY
    def test_worker_launch_requests_its_own_session(self) -> None:
        # posix_session_kwargs() is the shared "own session" decision the worker
        # and probe launches apply. Removing `**posix_session_kwargs()` from a
        # launch is caught semantically by R1 (worker pgid != harness pgid); this
        # fast test pins the helper's POSIX contract.
        self.assertEqual(pc.posix_session_kwargs(), {"start_new_session": True})


# --------------------------------------------------------------------------
# R1 / R2 - bounded SINGLE real-process test ids (name carries "RealProcess" so
# the suite's `-k "not RealProcess"` filter excludes them; run only by id here).
# --------------------------------------------------------------------------

R1_FAKE_WORKER = textwrap.dedent('''
    import os, time
    out = os.environ["R1_OUT"]
    with open(out, "w") as fh:
        fh.write("%d %d\\n" % (os.getpid(), os.getpgrp()))
        fh.flush()
    time.sleep(600)
''')

R1_HARNESS = textwrap.dedent('''
    import os, pathlib, sys
    repo, outdir = sys.argv[1], pathlib.Path(sys.argv[2])
    sys.path.insert(0, repo)
    from tools.agent_supervisor import claude_runner as cr
    (outdir / "harness_pgid").write_text("%d %d\\n" % (os.getpid(), os.getpgrp()))
    fake = str(outdir / "fake_worker.py")
    _orig = cr.build_argv
    cr.build_argv = lambda cfg: [_orig(cfg)[0], fake, *_orig(cfg)[1:]]
    cfg = cr.RunnerConfig(executable=sys.executable, max_turns=2, timeout_seconds=2.0,
                          cwd=str(outdir), extra_env={"R1_OUT": str(outdir / "worker_pgid")})
    try:
        result = cr.ClaudeRunner(cfg).run_unit("do the unit")
        (outdir / "harness_done").write_text("timed_out=%s\\n" % result.timed_out)
    except BaseException as exc:  # noqa: BLE001 - record then re-raise for the test
        (outdir / "harness_error").write_text(repr(exc))
        raise
''')

R2_GRANDCHILD = textwrap.dedent('''
    import os, time
    open(os.environ["R2_GC_OUT"], "w").write("%d\\n" % os.getpid())
    open(os.environ["R2_GC_STARTED"], "w").write("1")
    time.sleep(600)
''')

R2_WORKER = textwrap.dedent('''
    import os, subprocess, sys, time
    open(os.environ["R2_W_OUT"], "w").write("%d\\n" % os.getpid())
    subprocess.Popen([sys.executable, sys.argv[1]])  # grandchild, in the worker session
    time.sleep(600)
''')

R2_HARNESS = textwrap.dedent('''
    import os, subprocess, sys, time
    open(os.environ["R2_H_OUT"], "w").write("%d\\n" % os.getpid())
    # the worker runs in its OWN session (setsid) -> it and its grandchild are NOT
    # in the harness process group, so a group-kill of the harness cannot reap them
    subprocess.Popen([sys.executable, sys.argv[1], sys.argv[2]], start_new_session=True)
    time.sleep(600)
''')


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


@POSIX_ONLY
class LinuxContainmentRealProcessTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self._pids: list[int] = []

    def tearDown(self) -> None:
        for pid in self._pids:
            for killer in (lambda p: os.killpg(os.getpgid(p), signal.SIGKILL),
                           lambda p: os.kill(p, signal.SIGKILL)):
                try:
                    killer(pid)
                except Exception:
                    pass

    def test_R1_timeout_kill_spares_the_harness_and_worker_has_its_own_group(self) -> None:
        (self.tmp / "fake_worker.py").write_text(R1_FAKE_WORKER, encoding="utf-8")
        harness = self.tmp / "harness.py"
        harness.write_text(R1_HARNESS, encoding="utf-8")
        proc = subprocess.Popen(  # noqa: S603
            [sys.executable, str(harness), str(REPO), str(self.tmp)],
            start_new_session=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self._pids.append(proc.pid)
        try:
            _out, err = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            _out, err = proc.communicate()
            self.fail(f"harness did not finish within 30 s; stderr={err}")
        # The harness exited NORMALLY: a -9 (SIGKILL) would mean the worker-group
        # kill hit the harness's own group -> start_new_session missing on the
        # worker launch (the B-027 self-kill).
        err_file = self.tmp / "harness_error"
        self.assertEqual(proc.returncode, 0,
                         f"harness exited {proc.returncode}; stderr={err}; "
                         f"error={err_file.read_text() if err_file.exists() else ''}")
        self.assertTrue((self.tmp / "harness_done").exists(), err)
        harness_pgid = int((self.tmp / "harness_pgid").read_text().split()[1])
        worker_pid, worker_pgid = (
            int(x) for x in (self.tmp / "worker_pgid").read_text().split())
        self._pids.append(worker_pid)
        self.assertNotEqual(worker_pgid, harness_pgid,
                            "the worker shares the harness process group -> not session-isolated")

    def test_R2_group_kill_of_harness_leaves_a_setsid_grandchild_alive(self) -> None:
        (self.tmp / "r2_gc.py").write_text(R2_GRANDCHILD, encoding="utf-8")
        (self.tmp / "r2_worker.py").write_text(R2_WORKER, encoding="utf-8")
        (self.tmp / "r2_harness.py").write_text(R2_HARNESS, encoding="utf-8")
        env = dict(os.environ,
                   R2_H_OUT=str(self.tmp / "h_pid"), R2_W_OUT=str(self.tmp / "w_pid"),
                   R2_GC_OUT=str(self.tmp / "gc_pid"), R2_GC_STARTED=str(self.tmp / "gc_started"))
        proc = subprocess.Popen(  # noqa: S603
            [sys.executable, str(self.tmp / "r2_harness.py"),
             str(self.tmp / "r2_worker.py"), str(self.tmp / "r2_gc.py")],
            start_new_session=True, env=env)
        self._pids.append(proc.pid)
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not (self.tmp / "gc_started").exists():
            time.sleep(0.05)
        self.assertTrue((self.tmp / "gc_started").exists(), "the grandchild never started")
        gc_pid = int((self.tmp / "gc_pid").read_text().strip())
        w_pid = int((self.tmp / "w_pid").read_text().strip())
        self._pids.extend([gc_pid, w_pid])
        # Process-group containment: kill the harness's OWN group (what an external
        # kill of a process-group-contained supervisor would reap).
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        time.sleep(1.0)
        # The setsid grandchild survives -> process_group is NOT sufficient for an
        # externally killed supervisor, which is exactly why it is not accepted.
        self.assertTrue(_pid_alive(gc_pid),
                        "the setsid grandchild did not survive the harness group kill")


# --------------------------------------------------------------------------
# R3 - opt-in, env-gated real transient systemd unit. CI / owner-typed ONLY.
# --------------------------------------------------------------------------


@POSIX_ONLY
@unittest.skipUnless(os.environ.get("NYC_SUP_R3_SYSTEMD") == "1",
                     "R3 real-unit proof is opt-in (set NYC_SUP_R3_SYSTEMD=1 in Linux CI "
                     "or an owner-typed step); NEVER run by an agent on this host")
class R3RealSystemdUnitTests(unittest.TestCase):
    # The child-code strings are built by CONCATENATION with repr(gc_src), never
    # %-formatting: the worker/grandchild source text itself contains `'%d' %
    # os.getpid()`, so an outer `% gc_src` would bind that inner `%d` and raise
    # `TypeError: %d format: a real number is required, not str` (CI diagnostic,
    # rework 3). The inner `'%d' % os.getpid()` is evaluated at the child's OWN
    # runtime, where os.getpid() is an int.
    R3_HELPER = textwrap.dedent('''
        import os, subprocess, sys, time
        d = sys.argv[1]
        open(os.path.join(d, "main_pid"), "w").write(str(os.getpid()) + "\\n")
        gc_src = (
            "import os,sys,time\\n"
            "open(sys.argv[1]+'/gc_pid','w').write(str(os.getpid()))\\n"
            "open(sys.argv[1]+'/gc_started','w').write('1')\\n"
            "time.sleep(600)\\n")
        worker_src = (
            "import os,subprocess,sys,time\\n"
            "open(sys.argv[1]+'/worker_pid','w').write(str(os.getpid()))\\n"
            "subprocess.Popen([sys.executable,'-c'," + repr(gc_src) + ",sys.argv[1]])\\n"
            "time.sleep(600)\\n")
        subprocess.Popen([sys.executable, "-c", worker_src, d], start_new_session=True)
        time.sleep(600)
    ''')

    def _sudo(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(["sudo", "-n", *args], capture_output=True, text=True,
                              timeout=30, check=check)

    def _show_value(self, unit: str, prop: str) -> str:
        return self._sudo("systemctl", "show", unit, "-p", prop, "--value",
                          check=False).stdout.strip()

    def _diag(self, unit: str, work: pathlib.Path) -> str:
        """Self-explaining diagnostics appended to any R3 failure (bounded,
        check=False) so a CI failure explains itself in one round."""
        status = self._sudo("systemctl", "status", unit, "--no-pager", "-l", check=False)
        jlog = self._sudo("journalctl", "-u", unit, "--no-pager", "-n", "50", check=False)
        listing = sorted(p.name for p in work.iterdir()) if work.exists() else "<gone>"
        return (f"\n--- systemctl status {unit} ---\n{status.stdout}{status.stderr}"
                f"\n--- journalctl -u {unit} -n 50 ---\n{jlog.stdout}{jlog.stderr}"
                f"\n--- workdir {work} ---\n{listing}")

    def _unit_interpreter(self) -> tuple[str, list[str]]:
        """An interpreter + systemd-run `--setenv` args that work in a CLEAN unit
        environment. The helper is stdlib-only, so prefer the system
        `/usr/bin/python3`; otherwise fall back to this runner's interpreter
        (e.g. actions/setup-python under /opt/hostedtoolcache, whose shared
        libpython is found via LD_LIBRARY_PATH that a clean unit would drop) and
        carry LD_LIBRARY_PATH / PYTHONHOME into the unit."""
        if os.path.exists("/usr/bin/python3"):
            return "/usr/bin/python3", []
        setenv: list[str] = []
        for name in ("LD_LIBRARY_PATH", "PYTHONHOME"):
            value = os.environ.get(name)
            if value:
                setenv.append(f"--setenv={name}={value}")
        return sys.executable, setenv

    def test_R3_kill_of_main_pid_reaps_the_whole_control_group(self) -> None:
        import shutil
        import tempfile

        self.assertTrue(shutil.which("systemd-run"),
                        "NYC_SUP_R3_SYSTEMD=1 but systemd-run is not available")
        work = pathlib.Path(tempfile.mkdtemp(prefix="nyc-r3-")).resolve()
        work.chmod(0o777)
        helper = work / "r3_helper.py"
        helper.write_text(self.R3_HELPER, encoding="utf-8")
        unit = f"nyc-sup-r3-{os.urandom(6).hex()}"
        self.addCleanup(lambda: self._sudo("systemctl", "reset-failed", unit, check=False))
        self.addCleanup(lambda: self._sudo("systemctl", "stop", unit, check=False))
        interpreter, setenv = self._unit_interpreter()
        self._sudo(
            "systemd-run", f"--unit={unit}", "--collect",
            "--property=KillMode=control-group", "--property=ExitType=main",
            "--property=SendSIGKILL=yes", "--property=TimeoutStopSec=15s",
            "--property=ProtectControlGroups=yes",
            *setenv,
            interpreter, str(helper), str(work))
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not (work / "gc_started").exists():
            time.sleep(0.1)
        self.assertTrue((work / "gc_started").exists(),
                        "the unit's grandchild never started" + self._diag(unit, work))
        # MainPID can read 0 for a moment after start; wait (bounded) for it to settle.
        main_pid = 0
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            try:
                main_pid = int(self._show_value(unit, "MainPID") or "0")
            except ValueError:
                main_pid = 0
            if main_pid > 0:
                break
            time.sleep(0.2)
        self.assertGreater(main_pid, 0,
                           "the unit MainPID never became non-zero" + self._diag(unit, work))
        worker_pid = int((work / "worker_pid").read_text().strip())
        gc_pid = int((work / "gc_pid").read_text().strip())
        self._sudo("kill", "-9", str(main_pid))
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and (_pid_alive(worker_pid) or _pid_alive(gc_pid)):
            time.sleep(0.2)
        self.assertFalse(_pid_alive(worker_pid),
                         "the worker outlived the control-group teardown" + self._diag(unit, work))
        self.assertFalse(_pid_alive(gc_pid),
                         "the grandchild outlived the control-group teardown" + self._diag(unit, work))
        cgroup = self._show_value(unit, "ControlGroup")
        self.assertEqual(cgroup, "",
                         f"the control group was not emptied: {cgroup!r}" + self._diag(unit, work))


if __name__ == "__main__":
    unittest.main(verbosity=2)
