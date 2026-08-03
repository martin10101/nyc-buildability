#!/usr/bin/env python3
"""Audit hash-chain tests (D-007 S13.12, acceptance criterion 12).

The chain is MANDATORY, and S13.12 requires seeded tests proving it detects
tampering, truncation, and reordering. Every one of those three, plus
duplication, digest invalidity, and a corrupt record, has a test here.

The tests operate on the JSONL file on disk - not on in-memory objects - because
the threat is an attacker or a bug editing the FILE.

Stdlib `unittest` only. No network, no credentials.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor.audit_log import (  # noqa: E402
    GENESIS_DIGEST,
    AuditChainError,
    AuditLog,
    compute_record_digest,
)
from tools.agent_supervisor.models import canonical_json  # noqa: E402


class AuditChainTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name)
        self.path = self.tmp / "audit.jsonl"

    def seed(self, count: int = 5) -> AuditLog:
        log = AuditLog(self.path, fsync=False)
        for index in range(count):
            log.append("state_transition", run_id="run-1",
                       state_from="IDLE", state_to="PREFLIGHT",
                       detail={"index": index})
        return log

    def records(self) -> list[dict]:
        return [json.loads(line) for line in
                self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def rewrite(self, records: list[dict]) -> None:
        self.path.write_text(
            "".join(canonical_json(r).decode("utf-8") + "\n" for r in records),
            encoding="utf-8")

    # -- happy path ---------------------------------------------------------

    def test_a_fresh_chain_verifies(self) -> None:
        log = self.seed()
        verification = log.verify_chain()
        self.assertTrue(verification.ok, verification.message)
        self.assertEqual(verification.records_checked, 5)
        self.assertEqual(verification.head_sequence, 5)

    def test_chain_links_are_well_formed(self) -> None:
        self.seed(3)
        records = self.records()
        self.assertEqual(records[0]["prev_digest"], GENESIS_DIGEST)
        self.assertEqual([r["sequence"] for r in records], [1, 2, 3])
        for previous, current in zip(records, records[1:]):
            self.assertEqual(current["prev_digest"], previous["digest"])
        for record in records:
            self.assertEqual(record["digest"], compute_record_digest(record))

    def test_a_reopened_log_continues_the_same_chain(self) -> None:
        first = self.seed(2)
        head = first.head_digest
        second = AuditLog(self.path, fsync=False)
        self.assertEqual(second.head_digest, head)
        self.assertEqual(second.head_sequence, 2)
        second.append("probe", run_id="run-1")
        self.assertTrue(second.verify_chain().ok)
        self.assertEqual(self.records()[2]["prev_digest"], head)

    # -- the three mandated detections --------------------------------------

    def test_tampering_is_detected(self) -> None:
        log = self.seed(4)
        records = self.records()
        records[2]["detail"] = {"index": 99, "note": "quietly edited"}
        self.rewrite(records)
        verification = log.verify_chain()
        self.assertFalse(verification.ok)
        self.assertEqual(verification.code, "digest_mismatch")
        self.assertEqual(verification.failed_sequence, 3)

    def test_truncation_is_detected(self) -> None:
        log = self.seed(5)
        records = self.records()
        self.rewrite(records[:3])          # the last two events removed
        verification = log.verify_chain()
        self.assertFalse(verification.ok)
        self.assertEqual(verification.code, "truncated")
        self.assertIn("head anchor records sequence 5", verification.message)

    def test_reordering_is_detected(self) -> None:
        log = self.seed(4)
        records = self.records()
        records[1], records[2] = records[2], records[1]
        self.rewrite(records)
        verification = log.verify_chain()
        self.assertFalse(verification.ok)
        self.assertEqual(verification.code, "sequence_gap_or_reorder")

    # -- related integrity failures -----------------------------------------

    def test_duplicated_record_is_detected(self) -> None:
        log = self.seed(3)
        records = self.records()
        self.rewrite(records + [records[-1]])
        verification = log.verify_chain()
        self.assertFalse(verification.ok)
        self.assertIn(verification.code, ("duplicate_sequence", "sequence_gap_or_reorder"))

    def test_a_removed_middle_record_breaks_the_chain(self) -> None:
        log = self.seed(4)
        records = self.records()
        del records[1]
        self.rewrite(records)
        verification = log.verify_chain()
        self.assertFalse(verification.ok)
        self.assertEqual(verification.code, "sequence_gap_or_reorder")

    def test_a_relinked_forgery_still_fails_on_its_digest(self) -> None:
        """An attacker who fixes prev_digest but not the record digest is caught."""
        log = self.seed(3)
        records = self.records()
        records[1]["detail"] = {"index": 1, "note": "forged"}
        records[2]["prev_digest"] = records[1]["digest"]  # relink, digest left stale
        self.rewrite(records)
        verification = log.verify_chain()
        self.assertFalse(verification.ok)
        self.assertEqual(verification.code, "digest_mismatch")

    def test_a_fully_recomputed_forgery_is_caught_by_the_head_anchor(self) -> None:
        """Rewriting the whole chain consistently still contradicts the head anchor.

        This is exactly why S13.12 requires an anchor the worker cannot modify.
        The Phase 1 anchor is the sidecar head file; the owner-ruled Option A
        external anchor (a controller-pushed branch) lands in Phase 3.
        """
        log = self.seed(3)
        records = self.records()
        records[1]["detail"] = {"index": 1, "note": "forged"}
        previous = GENESIS_DIGEST
        for record in records:
            record["prev_digest"] = previous
            record["digest"] = compute_record_digest(record)
            previous = record["digest"]
        self.rewrite(records)
        verification = log.verify_chain()
        self.assertFalse(verification.ok)
        self.assertEqual(verification.code, "head_digest_mismatch")

    def test_a_malformed_line_is_reported_not_skipped(self) -> None:
        self.seed(2)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write("{not json}\n")
        log = AuditLog(self.path, fsync=False)
        verification = log.verify_chain()
        self.assertFalse(verification.ok)
        self.assertEqual(verification.code, "malformed_record")
        # A damaged chain is diagnosable but never extended.
        self.assertIsNotNone(log.load_error)
        with self.assertRaises(AuditChainError) as ctx:
            log.append("probe", run_id="r")
        self.assertEqual(ctx.exception.code, "append_to_damaged_chain")

    def test_require_valid_raises_for_recovery_callers(self) -> None:
        log = self.seed(3)
        records = self.records()
        self.rewrite(records[:1])
        with self.assertRaises(AuditChainError) as ctx:
            log.require_valid()
        self.assertEqual(ctx.exception.code, "truncated")

    # -- content rules ------------------------------------------------------

    def test_every_record_carries_the_required_audit_fields(self) -> None:
        self.seed(1)
        record = self.records()[0]
        for field in ("sequence", "timestamp_utc", "event_type", "run_id",
                      "controller_version", "prev_digest", "digest", "state_from",
                      "state_to", "executable_identity", "input_digest", "output_digest",
                      "decision", "policy_result", "error_category", "redaction_count"):
            self.assertIn(field, record)

    def test_redaction_count_is_recorded(self) -> None:
        log = AuditLog(self.path, fsync=False)
        log.append("probe", run_id="r", detail={"blob": "sk-ant-" + "Z" * 40})
        record = self.records()[0]
        self.assertEqual(record["redaction_count"], 1)
        self.assertNotIn("sk-ant-", json.dumps(record))

    def test_head_anchor_tracks_the_head(self) -> None:
        log = self.seed(3)
        anchor = json.loads(log.head_path.read_text(encoding="utf-8"))
        self.assertEqual(anchor["sequence"], 3)
        self.assertEqual(anchor["digest"], log.head_digest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
