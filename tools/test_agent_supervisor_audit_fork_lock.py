#!/usr/bin/env python3
"""M0-T046 SCOPE 2 (D-010-R125/R126) - emergency-stop audit-fork regression lock.

M0-T045 G4 MATERIAL FINDING: the `emergency-stop` command and the main loop can
write CONCURRENT audit sequence numbers (observed: duplicate seq 12/13, both
sharing prev_digest - a fork). `verify_chain()` fails `duplicate_sequence`; the
recovery surface reports `audit_chain_ok: false`.

The owner ACKNOWLEDGED (verbatim, source-012-amendment.md):
  "I acknowledge that an emergency stop may leave the audit log forked/unappendable
   until repaired, provided the system fails closed, does not silently repair or
   hide the fork, clearly records the condition, and refuses unsafe continuation."

This regression test LOCKS exactly those four conditions on a deterministically
constructed forked-chain shape (no real-process race). Before the M0-T046 fix an
append SUCCEEDED on a forked chain (verify reported the fork, but the log was
still extended); the fix detects the duplicate at open, sets load_error, and
refuses the append while keeping verify_chain honest.

  Condition (1) - the fork is deterministically REPORTED  -> test_1_*
  Condition (2) - FAIL CLOSED                             -> test_2_*
  Condition (3) - NO silent repair or hiding              -> test_3_*
  Condition (4) - clearly recorded + continuation REFUSED -> test_4_*, test_4_surface_*
                  until an EXPLICIT repair                -> test_4_repair_*

Scenario map: AS-2 <- this whole module. Stdlib unittest; no network/credentials.
"""
from __future__ import annotations

import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor.audit_log import (  # noqa: E402
    AuditChainError,
    AuditLog,
    compute_record_digest,
)
from tools.agent_supervisor.models import canonical_json  # noqa: E402


class _ForkFixture(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name)
        self.path = self.tmp / "audit.jsonl"

    def _seed(self, count: int = 5) -> AuditLog:
        log = AuditLog(self.path, fsync=False)
        for index in range(count):
            log.append("state_transition", run_id="run-estop",
                       state_from="IDLE", state_to="PREFLIGHT",
                       detail={"index": index})
        return log

    def _records(self) -> list[dict]:
        return [json.loads(line) for line in
                self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _write(self, records: list[dict]) -> None:
        self.path.write_text(
            "".join(canonical_json(r).decode("utf-8") + "\n" for r in records),
            encoding="utf-8")

    def _fork(self) -> list[dict]:
        """Reproduce the estop fork: a second record re-using the tail sequence and
        SHARING its prev_digest (the concurrent-writer shape), internally
        well-formed (its own digest recomputed) so only the DUPLICATE gives it
        away - exactly the observed seq 12/13 fork."""
        self._seed(5)
        records = self._records()
        tail = records[-1]
        forked = dict(tail)
        forked["run_id"] = "emergency-stop"
        forked["event_type"] = "emergency_stop"
        forked["detail"] = {"reason": "operator `emergency-stop`"}
        # Same sequence, same prev_digest -> a genuine fork, not a reorder.
        forked["prev_digest"] = tail["prev_digest"]
        forked["digest"] = compute_record_digest(forked)
        records.append(forked)
        self._write(records)
        return records


class ForkIsReported(_ForkFixture):
    def test_1_verify_chain_reports_duplicate_sequence(self) -> None:
        """(1) The fork is surfaced deterministically as duplicate_sequence."""
        self._fork()
        log = AuditLog(self.path, fsync=False)
        verification = log.verify_chain()
        self.assertFalse(verification.ok)
        self.assertEqual(verification.code, "duplicate_sequence")
        self.assertEqual(verification.failed_sequence, 5)

    def test_1_non_adjacent_duplicate_is_also_detected(self) -> None:
        """G3 S2-1: a duplicate that is NOT adjacent to its twin (an EARLIER
        sequence re-appearing after later records) is still caught - verify_chain
        reports it, the reopened log records a load_error, and append refuses. The
        `seen`-set check spans the whole file, not just neighbours."""
        self._seed(5)
        records = self._records()
        dup = dict(records[1])  # sequence 2, re-appended after sequence 5
        dup["detail"] = {"note": "non-adjacent duplicate"}
        dup["digest"] = compute_record_digest(dup)
        records.append(dup)
        self._write(records)

        log = AuditLog(self.path, fsync=False)
        verification = log.verify_chain()
        self.assertFalse(verification.ok)
        self.assertEqual(verification.code, "duplicate_sequence")
        self.assertEqual(verification.failed_sequence, 2)
        self.assertIsNotNone(log.load_error)
        self.assertEqual(log.load_error.code, "duplicate_sequence")
        with self.assertRaises(AuditChainError) as ctx:
            log.append("probe", run_id="run-estop")
        self.assertEqual(ctx.exception.code, "append_to_damaged_chain")


class FailsClosed(_ForkFixture):
    def test_2_reopen_records_a_load_error_and_append_refuses(self) -> None:
        """(2) Fail closed: reopening a forked log records a load_error and REFUSES
        to append onto it (before the fix, the append succeeded)."""
        self._fork()
        log = AuditLog(self.path, fsync=False)
        self.assertIsNotNone(log.load_error)
        self.assertEqual(log.load_error.code, "duplicate_sequence")
        with self.assertRaises(AuditChainError) as ctx:
            log.append("post_estop_event", run_id="run-estop")
        self.assertEqual(ctx.exception.code, "append_to_damaged_chain")


class NoSilentRepairOrHiding(_ForkFixture):
    def test_3_a_refused_append_neither_repairs_nor_hides_the_fork(self) -> None:
        """(3) No silent repair or hiding: a refused append leaves the file bytes
        UNCHANGED and verify_chain STILL reports the same fork afterwards."""
        self._fork()
        before = self.path.read_bytes()
        log = AuditLog(self.path, fsync=False)
        with self.assertRaises(AuditChainError):
            log.append("post_estop_event", run_id="run-estop")
        after = self.path.read_bytes()
        self.assertEqual(before, after,
                         "a refused append must not write, truncate, or repair the log")
        # The fork is still openly reported - not silently healed or masked.
        self.assertEqual(log.verify_chain().code, "duplicate_sequence")


class ContinuationRefusedUntilRepair(_ForkFixture):
    def test_4_continuation_on_a_forked_chain_is_refused(self) -> None:
        """(4a) Unsafe continuation is refused: every append onto the forked chain
        fails closed."""
        self._fork()
        log = AuditLog(self.path, fsync=False)
        for event in ("a", "b"):
            with self.assertRaises(AuditChainError) as ctx:
                log.append(event, run_id="run-estop")
            self.assertEqual(ctx.exception.code, "append_to_damaged_chain")

    def test_4_surface_recovery_status_reports_audit_chain_ok_false(self) -> None:
        """(4b) The condition is CLEARLY RECORDED on the activation-relevant surface:
        the real `recovery-status` / `status` CLI reports audit_chain_ok:false and
        exits non-zero on a forked chain."""
        from tools.agent_supervisor import cli
        from tools.agent_supervisor.durable_state import (
            DB_FILENAME,
            DurableJournal,
            runtime_dir_for,
        )

        repo = self.tmp / "repo"
        (repo / "tools").mkdir(parents=True)
        runtime = self.tmp / "runtime"
        runtime_dir = runtime_dir_for(repo, base=str(runtime))
        # A minimal but real journal so the surface can open the runtime.
        DurableJournal(runtime_dir / DB_FILENAME).open().close()
        # Plant the forked audit log at the runtime's audit path.
        self.path = runtime_dir / "audit.jsonl"
        self._fork()

        def run(*args: str) -> tuple[int, dict]:
            out = io.StringIO()
            argv = [*args, "--checkout", str(repo), "--runtime-base", str(runtime),
                    "--json"]
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = cli.main(list(argv))
            return code, json.loads(out.getvalue())

        code, payload = run("recovery-status")
        self.assertFalse(payload["audit_chain_ok"],
                         "recovery-status must report the fork, not hide it")

        code_s, payload_s = run("status")
        self.assertFalse(payload_s["audit_chain_ok"])
        self.assertNotEqual(code_s, 0,
                            "status exits non-zero when the audit chain is forked")

    def test_4_repair_an_explicit_repair_restores_appendability(self) -> None:
        """(4c) 'until repaired': after an EXPLICIT repair (removing the duplicate
        fork record), a reopened log has no load_error and appends again. Nothing
        auto-heals - the repair is a deliberate, external act."""
        records = self._fork()
        # Still forked: refuses.
        self.assertIsNotNone(AuditLog(self.path, fsync=False).load_error)
        # EXPLICIT repair: drop the duplicate fork record, keep the contiguous tail.
        repaired = records[:-1]
        self._write(repaired)
        log = AuditLog(self.path, fsync=False)
        self.assertIsNone(log.load_error, "a repaired chain opens cleanly")
        record = log.append("post_repair_event", run_id="run-estop")
        self.assertEqual(record.sequence, len(repaired) + 1)
        self.assertTrue(log.verify_chain().ok,
                        "the repaired-and-extended chain verifies")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
