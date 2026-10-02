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

import json
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor.review_slots import (  # noqa: E402
    Reservation,
    ReviewSlots,
    reservation_owner_alive,
)

# A self-contained worker run as a separate OS process. It spins on a file
# barrier so every racer calls try_reserve at the same moment, records whether it
# won, and (if it won) HOLDS the slot until released - so a late racer still sees
# the box full. argv: repo runtime_dir global_limit lane_limit lane coord_dir idx
_RACE_WORKER = r"""
import os, sys, time, pathlib
repo, runtime_dir, gl, ll, lane, coord, idx = sys.argv[1:8]
sys.path.insert(0, repo)
from tools.agent_supervisor.review_slots import ReviewSlots
coordp = pathlib.Path(coord)


def _emit(value):
    # Atomic: the parent globs result_* and reads it, so the final name must only
    # appear fully written (a partial read would be an int('') crash in the test).
    tmp = coordp / ("writing_" + idx)
    tmp.write_text(value)
    os.replace(tmp, coordp / ("result_" + idx))


(coordp / ("ready_" + idx)).write_text("1")
go, release = coordp / "go", coordp / "release"
slots = ReviewSlots(runtime_dir, global_limit=int(gl), lane_limit=int(ll),
                    lock_timeout_s=30.0)
deadline = time.monotonic() + 30
while not go.exists():
    if time.monotonic() > deadline:
        _emit("0"); sys.exit(0)
    time.sleep(0.005)
grant = slots.try_reserve(lane)
_emit("1" if grant.admitted else "0")
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


class RaceTests(unittest.TestCase):
    """RACE: real concurrent processes never both take the last slot."""

    def setUp(self) -> None:
        self.dir = _temp_runtime(self)

    def _run_race(self, *, n: int, global_limit: int, lane_limit: int,
                  same_lane: bool) -> int:
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
                    str(global_limit), str(lane_limit), lane, coord, str(idx)]))
            self._wait_for(coordp, "ready_", n)
            (coordp / "go").write_text("1")
            self._wait_for(coordp, "result_", n)
            return sum(int((coordp / f"result_{i}").read_text().strip())
                       for i in range(n))
        finally:
            (coordp / "release").write_text("1")
            for proc in procs:
                try:
                    proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    proc.kill()

    def _wait_for(self, coordp: pathlib.Path, prefix: str, n: int) -> None:
        deadline = time.monotonic() + 60
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
        # A directory at the lock path cannot be O_EXCL-created or read as a holder,
        # so acquisition times out and refuses rather than inventing a slot.
        slots.lock_path.parent.mkdir(parents=True, exist_ok=True)
        slots.lock_path.mkdir()
        grant = slots.try_reserve("lane-a")
        self.assertFalse(grant.admitted)
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


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
