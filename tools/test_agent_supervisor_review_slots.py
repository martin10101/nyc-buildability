#!/usr/bin/env python3
"""D-091 TW1 (M0-T171): atomic review-or-combine slot reservation.

Acceptance scenarios (packet M0-T171.json), one test class each:

* PRIMARY - two reservations succeed and a third is refused while both are held;
  releasing one lets the next succeed.
* RACE - several REAL processes racing for the last slot never both take it: at
  most the global limit succeed, and in one lane at most the per-lane limit.
* PER-LANE - a lane holding its slot cannot take a second even when the box has a
  free global slot; a different lane can take it.
* FAILURE/RECLAIM - a lock or state-file error refuses (fail closed, no slot); a
  reservation left by a dead process is reclaimed safely and never double-counted.

The race test uses genuinely separate OS processes (``subprocess`` + a file
barrier) so it exercises the cross-process file lock itself, and runs the same way
on POSIX and Windows. No live provider calls anywhere.
"""
from __future__ import annotations

import errno
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import review_slots  # noqa: E402
from tools.agent_supervisor.review_slots import (  # noqa: E402
    Reservation,
    ReviewSlots,
    reservation_owner_alive,
)

# A self-contained worker run as a separate OS process. It spins on a file
# barrier so every racer calls try_reserve at the same moment, records the OUTCOME
# as a reason code, and (if it won) HOLDS the slot until released - so a late racer
# still sees the box full. argv: repo runtime_dir global_limit lane_limit lane
# coord_dir idx barrier_wait_s.
#
# The result is a reason code, never a bare count (M0-T181 / DB-111): "admitted"
# when the slot was taken, "refused:<reason_code>" for a real admission refusal
# (e.g. refused:concurrency_limit_reached when the box/lane is full), and
# "barrier_timeout" when `go` never appeared inside the barrier budget. The barrier
# budget is passed in and is strictly larger than the parent's readiness window, so
# a racer can never abandon the barrier before the parent could gather every ready_*
# and write `go`; an expiry is a genuine hung-parent fault, surfaced loudly by the
# test, never a "0" miscounted as a legitimate refusal (the bug this closes: on a
# loaded 2-vCPU Windows runner an early racer's independent 30 s go-deadline expired
# before the slow sixth racer was ready and `go` was written, so it emitted "0"
# WITHOUT ever calling try_reserve and the test saw 1 winner of 6 instead of 2).
_RACE_WORKER = r"""
import os, sys, time, pathlib
repo, runtime_dir, gl, ll, lane, coord, idx, barrier_s = sys.argv[1:9]
sys.path.insert(0, repo)
from tools.agent_supervisor.review_slots import ReviewSlots
coordp = pathlib.Path(coord)


def _emit(value):
    # Atomic: the parent globs result_* and reads it, so the final name must only
    # appear fully written (a partial read would read a half-written reason code).
    tmp = coordp / ("writing_" + idx)
    tmp.write_text(value)
    os.replace(tmp, coordp / ("result_" + idx))


(coordp / ("ready_" + idx)).write_text("1")
go, release = coordp / "go", coordp / "release"
slots = ReviewSlots(runtime_dir, global_limit=int(gl), lane_limit=int(ll),
                    lock_timeout_s=30.0)
deadline = time.monotonic() + float(barrier_s)
while not go.exists():
    if time.monotonic() > deadline:
        _emit("barrier_timeout"); sys.exit(0)
    time.sleep(0.005)
grant = slots.try_reserve(lane)
_emit("admitted" if grant.admitted else "refused:" + grant.reason_code)
if grant.admitted:
    hold = time.monotonic() + 30
    while not release.exists() and time.monotonic() < hold:
        time.sleep(0.005)
    slots.release(grant.reservation)
"""


def _temp_runtime(case: unittest.TestCase) -> str:
    path = tempfile.mkdtemp(prefix="review-slots-")
    import shutil
    case.addCleanup(shutil.rmtree, path, ignore_errors=True)
    return path


class PrimaryReserveReleaseTests(unittest.TestCase):
    """PRIMARY: two succeed, a third is refused while both held, release frees one."""

    def setUp(self) -> None:
        self.dir = _temp_runtime(self)

    def _slots(self) -> ReviewSlots:
        return ReviewSlots(self.dir, global_limit=2, lane_limit=2)

    def test_two_admitted_third_refused_release_frees_one(self) -> None:
        slots = self._slots()
        first = slots.try_reserve("lane-a")
        second = slots.try_reserve("lane-b")
        self.assertTrue(first.admitted)
        self.assertTrue(second.admitted)
        self.assertEqual(len(slots.active()), 2)

        third = slots.try_reserve("lane-c")
        self.assertFalse(third.admitted)
        self.assertEqual(third.reason_code, "concurrency_limit_reached")
        self.assertEqual(third.verdict.scope, "global")
        self.assertIsNone(third.reservation)

        self.assertTrue(slots.release(first.reservation))
        self.assertEqual(len(slots.active()), 1)
        fourth = slots.try_reserve("lane-c")
        self.assertTrue(fourth.admitted)
        self.assertEqual(len(slots.active()), 2)

    def test_context_manager_releases_on_exit(self) -> None:
        slots = self._slots()
        with slots.reserve("lane-a") as grant:
            self.assertTrue(grant.admitted)
            self.assertEqual(len(slots.active()), 1)
        self.assertEqual(len(slots.active()), 0)

    def test_release_is_idempotent(self) -> None:
        slots = self._slots()
        grant = slots.try_reserve("lane-a")
        self.assertTrue(slots.release(grant.reservation))
        self.assertFalse(slots.release(grant.reservation))
        self.assertFalse(slots.release(None))


#: One shared window sizes the whole race so no racer can give up before the
#: parent does (M0-T181 / DB-111). The parent waits ``_RACE_PARENT_WAIT_S`` for
#: each fan-in (all ``ready_*``, then all ``result_*``). The racer's barrier budget
#: is DERIVED from that window and is strictly larger: the parent may spend its full
#: readiness window gathering six slow interpreter starts before it writes ``go``,
#: so a racer must wait for ``go`` at least that long PLUS a lock-serialization
#: allowance (the time for six racers to pass one tiny critical section back to back
#: on a saturated 2-vCPU runner). A barrier expiry inside that budget therefore
#: means a genuinely hung parent - a loud harness fault - never a loaded-but-
#: progressing runner. The old value (an independent 30 s go-deadline, shorter than
#: this 60 s readiness window) WAS the cause: an early racer abandoned the barrier
#: before the slow sixth racer became ready and ``go`` was written.
_RACE_PARENT_WAIT_S = 60.0
_RACE_LOCK_SERIALIZE_ALLOWANCE_S = 30.0
_RACE_BARRIER_WAIT_S = _RACE_PARENT_WAIT_S + _RACE_LOCK_SERIALIZE_ALLOWANCE_S

#: The only admission outcome that is a legitimate non-winner in these races: the
#: box or lane is full. Every OTHER non-admitted outcome (a barrier expiry, a lock
#: timeout, an unreadable/malformed state) is surfaced LOUDLY rather than silently
#: counted as a non-winner, so an under-admission can never again masquerade as a
#: refusal and a real fail-closed defect is never masked.
_RACE_LEGITIMATE_REFUSAL = "refused:concurrency_limit_reached"


class RaceTests(unittest.TestCase):
    """RACE: real concurrent processes never both take the last slot."""

    def setUp(self) -> None:
        self.dir = _temp_runtime(self)

    def _run_race(self, *, n: int, global_limit: int, lane_limit: int,
                  same_lane: bool) -> int:
        """Run the race and return the number of racers ADMITTED. Any non-slot
        outcome (barrier expiry, lock timeout, unreadable state) fails the test
        loudly with every racer's reason code - it is never counted as a loser."""
        coord = tempfile.mkdtemp(prefix="race-coord-")
        import shutil
        self.addCleanup(shutil.rmtree, coord, ignore_errors=True)
        coordp = pathlib.Path(coord)
        procs: list[subprocess.Popen] = []
        try:
            for idx in range(n):
                lane = "shared" if same_lane else f"lane-{idx}"
                procs.append(subprocess.Popen([
                    sys.executable, "-c", _RACE_WORKER, str(REPO), self.dir,
                    str(global_limit), str(lane_limit), lane, coord, str(idx),
                    str(_RACE_BARRIER_WAIT_S)]))
            self._wait_for(coordp, "ready_", n)
            (coordp / "go").write_text("1")
            self._wait_for(coordp, "result_", n)
            results = [(coordp / f"result_{i}").read_text().strip() for i in range(n)]
            faults = [r for r in results
                      if r != "admitted" and r != _RACE_LEGITIMATE_REFUSAL]
            if faults:
                self.fail(
                    f"race produced a non-slot outcome (barrier/lock/state), not a "
                    f"clean admitted/full result - a loaded-runner barrier expiry or a "
                    f"fail-closed error, NOT a legitimate refusal to be counted as a "
                    f"loser: {results}")
            return sum(1 for r in results if r == "admitted")
        finally:
            (coordp / "release").write_text("1")
            for proc in procs:
                try:
                    proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    proc.kill()

    def _wait_for(self, coordp: pathlib.Path, prefix: str, n: int) -> None:
        deadline = time.monotonic() + _RACE_PARENT_WAIT_S
        while len(list(coordp.glob(prefix + "*"))) < n:
            if time.monotonic() > deadline:
                self.fail(f"only {len(list(coordp.glob(prefix + '*')))}/{n} "
                          f"{prefix}* appeared in time")
            time.sleep(0.01)

    def test_global_last_slot_never_double_taken(self) -> None:
        # 6 racers, distinct lanes, 2 global slots -> exactly 2 win.
        winners = self._run_race(n=6, global_limit=2, lane_limit=1, same_lane=False)
        self.assertEqual(winners, 2)
        self.assertLessEqual(len(ReviewSlots(self.dir).active()), 2)

    def test_per_lane_last_slot_never_double_taken(self) -> None:
        # 6 racers, one shared lane, per-lane limit 1 -> exactly 1 wins.
        winners = self._run_race(n=6, global_limit=5, lane_limit=1, same_lane=True)
        self.assertEqual(winners, 1)


class PerLaneTests(unittest.TestCase):
    """PER-LANE: a lane cannot take a second slot while the box has global room."""

    def setUp(self) -> None:
        self.dir = _temp_runtime(self)

    def test_lane_cap_holds_while_global_has_room(self) -> None:
        slots = ReviewSlots(self.dir, global_limit=2, lane_limit=1)
        first = slots.try_reserve("lane-a")
        self.assertTrue(first.admitted)

        second_same = slots.try_reserve("lane-a")
        self.assertFalse(second_same.admitted)
        self.assertEqual(second_same.reason_code, "concurrency_limit_reached")
        self.assertTrue(second_same.verdict.scope.startswith("lane"))

        other_lane = slots.try_reserve("lane-b")
        self.assertTrue(other_lane.admitted)  # global still had a slot
        self.assertEqual(len(slots.active()), 2)


class FailureAndReclaimTests(unittest.TestCase):
    """FAILURE/RECLAIM: errors fail closed; a dead owner is reclaimed, not double-counted."""

    def setUp(self) -> None:
        self.dir = _temp_runtime(self)

    def _plant(self, reservations: list[dict]) -> ReviewSlots:
        slots = ReviewSlots(self.dir, global_limit=2, lane_limit=1)
        slots.state_path.parent.mkdir(parents=True, exist_ok=True)
        slots.state_path.write_text(json.dumps(
            {"schema_version": "1.0.0", "reservations": reservations}))
        return slots

    def test_corrupt_state_file_fails_closed(self) -> None:
        slots = ReviewSlots(self.dir, global_limit=2, lane_limit=1)
        slots.state_path.parent.mkdir(parents=True, exist_ok=True)
        slots.state_path.write_text("{ this is not json")
        grant = slots.try_reserve("lane-a")
        self.assertFalse(grant.admitted)
        self.assertEqual(grant.reason_code, "slot_state_unreadable")
        self.assertIsNone(grant.reservation)

    def test_non_record_state_file_fails_closed(self) -> None:
        slots = ReviewSlots(self.dir, global_limit=2, lane_limit=1)
        slots.state_path.parent.mkdir(parents=True, exist_ok=True)
        slots.state_path.write_text(json.dumps(["not", "a", "record"]))
        grant = slots.try_reserve("lane-a")
        self.assertFalse(grant.admitted)
        self.assertEqual(grant.reason_code, "slot_state_unreadable")

    def test_lock_error_fails_closed(self) -> None:
        slots = ReviewSlots(self.dir, global_limit=2, lane_limit=1, lock_timeout_s=0.2,
                            lock_poll_s=0.01)
        # A directory at the lock path can never be O_EXCL-created and can never be
        # read as a holder, so no slot can be invented -- it only ever fails closed.
        # After M0-T176 both OS families land on the SAME refusal code by different
        # internal paths, so one assertion pins both platforms:
        #   * POSIX: os.open(O_CREAT|O_EXCL) on a directory raises FileExistsError;
        #     the holder read of the directory fails, so it is never "stale", and the
        #     wait runs to the deadline -> slot_lock_timeout.
        #   * Windows (nt): the same call raises PermissionError; the delete-pending
        #     busy-wait treats it as busy (never a takeover) and also runs to the
        #     deadline -> slot_lock_timeout (was slot_lock_error before M0-T176).
        slots.lock_path.parent.mkdir(parents=True, exist_ok=True)
        slots.lock_path.mkdir()
        grant = slots.try_reserve("lane-a")
        self.assertFalse(grant.admitted)
        self.assertIsNone(grant.reservation)
        self.assertEqual(grant.reason_code, "slot_lock_timeout")

    def test_reused_pid_reservation_is_reclaimed(self) -> None:
        # Same (live) pid but a start-token that does not match this process ->
        # the original owner is gone (pid reused). It must be pruned, not counted.
        import os
        planted = {"reservation_id": "ghost", "pid": os.getpid(),
                   "start_token": "not-the-real-token", "lane": "lane-a",
                   "acquired_at_utc": "2026-10-02T00:00:00.000Z"}
        slots = self._plant([planted])
        self.assertFalse(reservation_owner_alive(Reservation.from_dict(planted)))
        self.assertEqual(len(slots.active()), 0)  # reclaimed on read

        first = slots.try_reserve("lane-a")
        self.assertTrue(first.admitted)
        # Never double-counted: the one live slot, and the ghost is gone from disk.
        self.assertEqual(len(slots.active()), 1)
        on_disk = json.loads(slots.state_path.read_text())
        ids = [r["reservation_id"] for r in on_disk["reservations"]]
        self.assertNotIn("ghost", ids)

    def test_invalid_pid_reservation_is_reclaimed(self) -> None:
        planted = {"reservation_id": "bad-pid", "pid": -1, "start_token": "",
                   "lane": "lane-a", "acquired_at_utc": "2026-10-02T00:00:00.000Z"}
        slots = self._plant([planted])
        self.assertEqual(len(slots.active()), 0)

    def test_malformed_reservation_entry_fails_closed(self) -> None:
        slots = self._plant([{"pid": 123}])  # missing reservation_id/lane
        grant = slots.try_reserve("lane-a")
        self.assertFalse(grant.admitted)
        self.assertEqual(grant.reason_code, "slot_state_unreadable")

    def test_dead_process_reservation_is_reclaimed(self) -> None:
        # A real child reserves the only slot then exits WITHOUT releasing it
        # (a crash). The next reservation must reclaim the dead slot, and the box
        # must never hold two.
        coord = tempfile.mkdtemp(prefix="dead-coord-")
        import shutil
        self.addCleanup(shutil.rmtree, coord, ignore_errors=True)
        crasher = (
            "import sys, pathlib; repo, rd, coord = sys.argv[1:4];"
            " sys.path.insert(0, repo);"
            " from tools.agent_supervisor.review_slots import ReviewSlots;"
            " g = ReviewSlots(rd, global_limit=1, lane_limit=1).try_reserve('x');"
            " pathlib.Path(coord, 'done').write_text('1' if g.admitted else '0');"
            " sys.exit(0)")
        proc = subprocess.run([sys.executable, "-c", crasher, str(REPO), self.dir, coord],
                              timeout=30)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual((pathlib.Path(coord) / "done").read_text(), "1")

        slots = ReviewSlots(self.dir, global_limit=1, lane_limit=1)
        # The dead child's reservation is on disk but its owner is gone.
        raw = json.loads(slots.state_path.read_text())["reservations"]
        self.assertEqual(len(raw), 1)
        grant = slots.try_reserve("x")
        self.assertTrue(grant.admitted)  # reclaimed the dead slot
        self.assertEqual(len(slots.active()), 1)  # never two


class WindowsSharingViolationTests(unittest.TestCase):
    """WINDOWS DELETE-PENDING: a sharing-violation PermissionError on the lock
    create is a transient 'busy', not a terminal refusal (M0-T176).

    On windows-latest, ``os.open(O_CREAT|O_EXCL)`` can raise ``PermissionError``
    (ERROR_ACCESS_DENIED) while a just-released lock file is delete-pending because a
    racer still has it open for a short liveness read. ``acquire`` must wait through
    that to the deadline exactly like ``FileExistsError`` and refuse only at the
    timeout (``slot_lock_timeout``) -- never a one-shot ``slot_lock_error`` and never
    an over-admission. POSIX never produces this for ``O_EXCL``, so a PermissionError
    there stays a genuine fault that refuses at once. Every case is injected
    deterministically on BOTH hosts by patching ``review_slots._is_windows`` (the
    platform seam) and ``os.open`` -- no real Windows-only syscall is ever made, so
    these run identically everywhere. (``_is_windows`` is patched, not the global
    ``os.name``: setting ``os.name='nt'`` would make ``pathlib`` build ``WindowsPath``
    and raise on POSIX, so the seam isolates just the platform read.)
    """

    def setUp(self) -> None:
        self.dir = _temp_runtime(self)

    @staticmethod
    def _failing_open(error: OSError, *, fail_times: int):
        """A stand-in for ``os.open`` that raises ``error`` on the first
        ``fail_times`` lock creates, then delegates to the real ``os.open``.

        Returns ``(fake_open, state)``; ``state['calls']`` counts invocations so a
        test can prove it retried (waited) or refused one-shot. A huge ``fail_times``
        models a fault that never clears.
        """
        real_open = os.open
        state = {"calls": 0}

        def fake_open(path, flags, *args, **kwargs):  # type: ignore[no-untyped-def]
            state["calls"] += 1
            if state["calls"] <= fail_times:
                raise error
            return real_open(path, flags, *args, **kwargs)

        return fake_open, state

    def test_transient_permission_error_waits_then_succeeds_as_nt(self) -> None:
        # Fail the O_EXCL create twice with a Windows delete-pending PermissionError,
        # then let it succeed: the reservation WAITS and is then granted (no refusal).
        fake_open, state = self._failing_open(
            PermissionError(errno.EACCES, "delete pending"), fail_times=2)
        slots = ReviewSlots(self.dir, global_limit=2, lane_limit=1,
                            lock_timeout_s=5.0, lock_poll_s=0.001)
        with mock.patch.object(review_slots, "_is_windows", lambda: True), \
                mock.patch.object(review_slots.os, "open", fake_open):
            grant = slots.try_reserve("lane-a")
        self.assertTrue(grant.admitted)
        self.assertIsNotNone(grant.reservation)
        self.assertEqual(state["calls"], 3)  # 2 busy retries + 1 success
        self.assertEqual(len(slots.active()), 1)  # exactly one slot, never lost

    def test_persistent_permission_error_times_out_as_nt(self) -> None:
        # A delete-pending PermissionError that never clears must refuse at the
        # deadline with slot_lock_timeout -- admitted False, no reservation.
        fake_open, state = self._failing_open(
            PermissionError(errno.EACCES, "delete pending"), fail_times=10 ** 9)
        slots = ReviewSlots(self.dir, global_limit=2, lane_limit=1,
                            lock_timeout_s=0.2, lock_poll_s=0.01)
        with mock.patch.object(review_slots, "_is_windows", lambda: True), \
                mock.patch.object(review_slots.os, "open", fake_open):
            grant = slots.try_reserve("lane-a")
        self.assertFalse(grant.admitted)
        self.assertEqual(grant.reason_code, "slot_lock_timeout")
        self.assertIsNone(grant.reservation)
        self.assertGreater(state["calls"], 1)  # it retried; not a one-shot refusal

    def test_non_sharing_oserror_fails_closed_immediately(self) -> None:
        # An OSError that is NOT a sharing violation (EIO) is a real fault: refuse at
        # once with slot_lock_error on BOTH platforms -- no wait, no timeout.
        self.assertNotIsInstance(  # pin that EIO is a plain OSError, not a subclass
            OSError(errno.EIO, "x"), (PermissionError, FileExistsError))
        for on_windows in (False, True):
            with self.subTest(os_name="nt" if on_windows else "posix"):
                slots = ReviewSlots(_temp_runtime(self), global_limit=2, lane_limit=1,
                                    lock_timeout_s=5.0, lock_poll_s=0.01)
                fake_open, state = self._failing_open(
                    OSError(errno.EIO, "simulated I/O error"), fail_times=10 ** 9)
                with mock.patch.object(review_slots, "_is_windows",
                                       lambda ow=on_windows: ow), \
                        mock.patch.object(review_slots.os, "open", fake_open):
                    grant = slots.try_reserve("lane-a")
                self.assertFalse(grant.admitted)
                self.assertEqual(grant.reason_code, "slot_lock_error")
                self.assertIsNone(grant.reservation)
                self.assertEqual(state["calls"], 1)  # immediate, no retry/wait

    def test_permission_error_on_posix_fails_closed_immediately(self) -> None:
        # POSIX O_EXCL never yields a delete-pending PermissionError; a real one is a
        # genuine permission fault, so POSIX still refuses at once (unchanged).
        fake_open, state = self._failing_open(
            PermissionError(errno.EACCES, "real permission fault"), fail_times=10 ** 9)
        slots = ReviewSlots(_temp_runtime(self), global_limit=2, lane_limit=1,
                            lock_timeout_s=5.0, lock_poll_s=0.01)
        with mock.patch.object(review_slots, "_is_windows", lambda: False), \
                mock.patch.object(review_slots.os, "open", fake_open):
            grant = slots.try_reserve("lane-a")
        self.assertFalse(grant.admitted)
        self.assertEqual(grant.reason_code, "slot_lock_error")
        self.assertIsNone(grant.reservation)
        self.assertEqual(state["calls"], 1)  # no wait on POSIX


class ReleaseLockRemovalTests(unittest.TestCase):
    """RELEASE REMOVAL (M0-T184): a normal ``_SlotLock.release()`` must leave the
    lock file GONE even when a concurrent short liveness read briefly blocks the
    removal on Windows.

    The CI defect (jobs 112160344138 / 112164492630 / 112181006630, windows-latest):
    ``release()`` issued ONE ``self.path.unlink()`` inside ``contextlib.suppress``.
    On Windows CPython opens a file for reading WITHOUT ``FILE_SHARE_DELETE``, so
    while another racer's ``_read_holder`` has the lock file open, the holder's
    ``unlink`` raises ``PermissionError`` (ERROR_ACCESS_DENIED). That error was
    swallowed, so the lock file stayed on disk owned by a STILL-LIVE admitted racer.
    No contender may take over a live holder, so every other racer waited out its
    full 30 s lock timeout -> ``refused:slot_lock_timeout``. The fix makes the
    removal a bounded retry derived from the lock's own timeout/poll (the reader's
    handle is short-lived), still never touching a foreign lock_id, and surfaces a
    removal that cannot complete rather than swallowing it silently.
    """

    def setUp(self) -> None:
        self.dir = _temp_runtime(self)

    @staticmethod
    def _failing_unlink(error: OSError, *, fail_times: int):
        """A stand-in for ``pathlib.Path.unlink`` that raises ``error`` on the first
        ``fail_times`` removals, then delegates to the real ``unlink``.

        Returns ``(fake_unlink, state)``; ``state['calls']`` counts invocations so a
        test can prove the removal retried (waited) rather than giving up after one
        swallowed failure. A huge ``fail_times`` models a removal that never clears.
        Host-independent: it injects the Windows delete-pending failure on any OS, so
        the transient/never-clears behaviour is pinned deterministically everywhere
        (the real Win32 sharing fact is pinned separately by the two nt-only tests).
        """
        real_unlink = pathlib.Path.unlink
        state = {"calls": 0}

        def fake_unlink(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            state["calls"] += 1
            if state["calls"] <= fail_times:
                raise error
            return real_unlink(self, *args, **kwargs)

        return fake_unlink, state

    def _lock(self, name: str, *, start_token: str = "tok",
              timeout_s: float = 5.0, poll_s: float = 0.001) -> review_slots._SlotLock:
        path = pathlib.Path(self.dir) / name
        return review_slots._SlotLock(path, pid=os.getpid(), start_token=start_token,
                                      timeout_s=timeout_s, poll_s=poll_s)

    def test_release_retries_transient_removal_failure_then_succeeds(self) -> None:
        # S5(i), host-independent. The removal fails three times with the Windows
        # delete-pending error and then succeeds: after release() the lock file is
        # GONE and the next acquire takes it promptly. RED against the pre-repair
        # release (one swallowed unlink leaves the file on disk; state['calls']==1).
        lock = self._lock("transient.lock")
        lock.acquire()
        self.assertTrue(lock.path.exists())
        fake_unlink, state = self._failing_unlink(
            PermissionError(errno.EACCES, "delete pending"), fail_times=3)
        with mock.patch.object(pathlib.Path, "unlink", fake_unlink):
            lock.release()
        self.assertFalse(lock.path.exists())  # removed after the transient failures
        self.assertGreaterEqual(state["calls"], 4)  # 3 busy retries + 1 success
        # The freed lock is takeable at once by the next acquirer:
        nxt = self._lock("transient.lock", start_token="tok-2")
        nxt.acquire()
        self.assertTrue(nxt.path.exists())
        nxt.release()
        self.assertFalse(nxt.path.exists())

    @unittest.skipUnless(
        os.name == "nt",
        "Windows-only platform fact: on POSIX unlink of a file that another handle "
        "has open succeeds (no mandatory sharing lock), so the mechanism cannot be "
        "exercised there. This pins the Win32 behaviour the slot_lock_timeout cause "
        "rests on; it is DEMONSTRATED on windows-latest, never assumed from memory.")
    def test_windows_open_reader_blocks_unlink_platform_fact(self) -> None:
        # S3: deleting a file that another handle - opened exactly the way
        # _read_holder opens it (read_text -> open(mode='r', encoding='utf-8')) -
        # still has open raises PermissionError, and the blocked unlink leaves the
        # file on disk. This is candidate (a)'s mechanism, proven on the platform.
        path = pathlib.Path(self.dir) / "platform.lock"
        path.write_text("holder", encoding="utf-8")
        reader = path.open("r", encoding="utf-8")  # the way _read_holder opens it
        try:
            with self.assertRaises(PermissionError):
                path.unlink()
            self.assertTrue(path.exists())  # the blocked unlink left the file on disk
        finally:
            reader.close()
        path.unlink()  # once the short reader handle closes, the removal succeeds
        self.assertFalse(path.exists())

    @unittest.skipUnless(
        os.name == "nt",
        "Windows-only real-handle test: it depends on the Win32 sharing fact above "
        "(an open reader without delete-sharing blocks unlink), which POSIX does not "
        "have. RED on windows-latest before the repair (the single swallowed unlink "
        "leaves the lock file on disk); GREEN after it (the bounded retry removes the "
        "lock once the reader's short handle closes).")
    def test_windows_release_removes_lock_despite_concurrent_reader(self) -> None:
        # S5(v): a second REAL handle holds the lock file open briefly while
        # release() runs; afterwards the lock file is gone. No os.open/unlink
        # patching - a genuine concurrent handle on the real platform.
        import threading
        lock = self._lock("realhandle.lock", timeout_s=5.0, poll_s=0.005)
        lock.acquire()
        self.assertTrue(lock.path.exists())
        reader = lock.path.open("r", encoding="utf-8")  # another racer's short read
        closed = threading.Event()

        def _close_soon() -> None:
            time.sleep(0.1)
            reader.close()
            closed.set()

        thread = threading.Thread(target=_close_soon)
        thread.start()
        try:
            lock.release()
        finally:
            if not closed.is_set():
                reader.close()
            thread.join(timeout=5)
        self.assertFalse(lock.path.exists())  # removed once the short handle closed

    def test_release_that_never_clears_is_bounded_failclosed_and_observable(self) -> None:
        # S5(ii), host-independent. A removal that NEVER succeeds must be bounded by
        # the lock's own timeout, fail closed (our lock stays on disk; no contender
        # over-admits on a guess), and be observable (typed release_error + an ERROR
        # log), never silently swallowed. release() must not raise.
        lock = self._lock("stuck.lock", timeout_s=0.2, poll_s=0.01)
        lock.acquire()
        fake_unlink, state = self._failing_unlink(
            PermissionError(errno.EACCES, "delete pending"), fail_times=10 ** 9)
        start = time.monotonic()
        with mock.patch.object(pathlib.Path, "unlink", fake_unlink), \
                self.assertLogs(review_slots.logger, level="ERROR") as logs:
            lock.release()
        elapsed = time.monotonic() - start
        self.assertLess(elapsed, 3.0)  # bounded, not an unbounded loop
        self.assertGreater(state["calls"], 1)  # it retried (waited), not one-shot
        self.assertTrue(lock.path.exists())  # fail closed: our lock is not removed
        self.assertIsNotNone(lock.release_error)
        self.assertEqual(lock.release_error.code, "slot_lock_release_failed")
        self.assertTrue(any("slot_lock_release_failed" in line for line in logs.output))
        lock.path.unlink()  # real unlink (patch gone) so teardown is clean

    def test_release_never_removes_a_foreign_lock_id(self) -> None:
        # S5(iii), host-independent. A lock file carrying a DIFFERENT lock_id (another
        # process's live lock) is never removed, and a correct decline is not a
        # failure (release_error stays None).
        path = pathlib.Path(self.dir) / "foreign.lock"
        owner = self._lock("foreign.lock", start_token="owner")
        owner.acquire()  # writes a real lock file carrying owner._lock_id
        owner_bytes = path.read_bytes()
        intruder = self._lock("foreign.lock", start_token="intruder", timeout_s=0.2)
        # intruder never acquired, so its _lock_id ('') != the on-disk owner lock_id.
        intruder.release()
        self.assertTrue(path.exists())  # untouched
        self.assertEqual(path.read_bytes(), owner_bytes)  # byte-identical, not forged
        self.assertIsNone(intruder.release_error)  # a correct decline, not a failure
        owner.release()  # the real owner removes it cleanly
        self.assertFalse(path.exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
