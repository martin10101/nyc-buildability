#!/usr/bin/env python3
"""M0-T048 (D-010 am.14) - close the G5 C2 residual: bind the forwarded content to
the OPERATOR-NAMED approval digest.

G5 M0-T046 C2 / MEDIUM M-1: the park->approve byte binding rested on a journal-
resident anchor (`prompt_bytes_digest`). An attacker with journal write who rewrote
BOTH the parked `prompt` bytes AND `prompt_bytes_digest` consistently - leaving the
operator-named approval digest untouched - still got altered bytes forwarded under a
valid operator approval (confirmed by the G5 and DCV reports).

The fix (R136/R137): `build_forwarded_prompt` now emits a DETERMINISTIC, timestamp-
free body that is a pure function of exactly the five fields the operator-named
`approval_digest` covers; the `FORWARDED AT:` clock is appended only at forward time
(excluded from the binding) and the volatile packet reference is gone. The parked
record carries the STRUCTURED approved instruction, and approve/resume RECONSTRUCT the
body from it and refuse fail-closed unless it reproduces the operator-named digest.
So the forwarded content is cryptographically bound to operator-covered material, not
to mutable journal fields.

These tests drive the REAL loop (park), the REAL `resume-pending-prompt` CLI (approve),
and the REAL loop again (forward), forging the durable journal between the steps -
exactly the threat. Deterministic, stdlib unittest, no network, no credentials.

Scenario map:
  AS-1 (R138, 7 properties)  <- TwoFieldForgery.test_two_field_forgery_after_approval_*
  AS-1 non-vacuity           <- TwoFieldForgery.test_non_vacuity_pre_fix_checks_pass
  AS-1 approve-path fail-closed <- TwoFieldForgery.test_two_field_forgery_at_approve_*
  R139(a) happy path binds   <- HappyPathBinding.test_happy_path_forwards_once_and_binds
  R139(b) clock-only S13.5    <- ClockInvariant.test_clock_only_change_does_not_invalidate
  R139(c) post-approval tamper<- TwoFieldForgery.test_two_field_forgery_after_approval_*
  R139(d) surfaces unchanged  <- PostureUnchanged.test_shadow_supervised_posture_intact
  AS-6 distinct reason codes  <- FailClosedReasonCodes.*
"""
from __future__ import annotations

import unittest

from tools.agent_supervisor import loop as lp
from tools.agent_supervisor import state_machine as sm
from tools.agent_supervisor.audit_log import AuditLog
from tools.agent_supervisor.loop import LoopError
from tools.test_agent_supervisor_loop import (
    FakeReviewer,
    FakeRunner,
    decision as make_decision,
    outcome,
    run_result,
)
from tools.test_agent_supervisor_park_approve_binding import (
    _CrossProcessHarness,
    covered_pending,
)


class TwoFieldForgery(_CrossProcessHarness):
    """AS-1 (R138): the two-field journal forgery the C2 residual described must fail
    closed, at BOTH the approve step and the resume/forward step."""

    def _forge_two_fields(self, record: dict, marker: str) -> dict:
        """Rewrite BOTH the prompt AND its byte anchor consistently, leaving the
        operator-named digest AND the structured instruction untouched."""
        evil = record["prompt"] + marker
        forged = dict(record)
        forged["prompt"] = evil
        forged["prompt_bytes_digest"] = lp.digest_of(evil)  # self-consistent
        return forged

    def test_non_vacuity_pre_fix_checks_pass(self) -> None:
        """NON-VACUITY: the forged record satisfies EVERY pre-fix acceptance predicate
        (the M0-T046 anchor check and the operator-digest match), so the pre-fix code
        WOULD have approved and forwarded the injected bytes. Only the new
        reconstruction-from-covered-instruction check refuses."""
        parked = self._park_real()
        operator_digest = parked["digest"]
        forged = self._forge_two_fields(parked, "\nSILENTLY INJECTED\n")

        # Pre-fix predicate 1 (M0-T046 CLI/anchor): digest_of(prompt) == anchor.
        self.assertEqual(lp.digest_of(forged["prompt"]),
                         forged["prompt_bytes_digest"],
                         "the two forged fields are self-consistent: the M0-T046 byte "
                         "anchor check would PASS on the pre-fix code")
        # Pre-fix predicate 2 (CLI): supplied operator digest == recorded digest.
        self.assertEqual(operator_digest, forged["digest"],
                         "the operator-named digest is untouched: the CLI operator "
                         "match would PASS on the pre-fix code")
        # => pre-fix, approved_digest would have been re-hashed from the evil bytes
        #    (digest_of(evil)) and the injection forwarded. Post-fix, the body is
        #    RECONSTRUCTED from the covered instruction and never contains the marker.
        self.assertNotIn("SILENTLY INJECTED",
                         lp.build_forwarded_prompt(**parked["approved_instruction"]),
                         "the reconstruction from operator-covered material can never "
                         "carry the injected bytes")

        # Post-fix: the same forgery is refused fail-closed.
        self._set_pending(forged)
        code, _out, err = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", operator_digest)
        self.assertEqual(code, 1, "post-fix refuses the two-field forgery")
        self.assertIn("operator-named approval digest", err)

    def test_two_field_forgery_at_approve_is_refused_fail_closed(self) -> None:
        """AS-1 properties 1-5,7 on the APPROVE path: fail closed, no state change,
        record not approved, and a sealed hash-chained refusal whose chain verifies."""
        parked = self._park_real()                       # (1) authentic approval
        operator_digest = parked["digest"]
        forged = self._forge_two_fields(parked, "\nINJECTED AT APPROVE\n")  # (2)
        self._set_pending(forged)

        code, _out, err = self.run_cli(                  # (3)(4) attempt approval
            "resume-pending-prompt", "--approve-prompt-digest", operator_digest)
        self.assertEqual(code, 1, "(5) fail closed")     # (5)

        self.assertEqual(self._state(), sm.WAIT_FOR_OWNER, "no state change")
        record = self._pending()
        self.assertFalse(record.get("approved"), "the record is not approved")

        events = self._audit_events()                    # (7) sealed refusal
        refusals = [e for e in events
                    if e["event_type"] == "operator_resume_pending_prompt_refused"]
        self.assertEqual(len(refusals), 1)
        self.assertEqual(refusals[0]["decision"], "refuse")
        self.assertEqual(refusals[0]["detail"]["reason"], "pending_prompt_tampered")
        audit = AuditLog(self.runtime_dir / "audit.jsonl", fsync=False)
        self.assertTrue(audit.verify_chain().ok,
                        "the sealed refusal keeps the audit chain valid")

    def test_two_field_forgery_after_approval_is_refused_no_provider(self) -> None:
        """AS-1 properties 4-7 / R139(c) on the RESUME/FORWARD path: a two-field
        forgery of the APPROVED record is caught at resume; a fresh loop refuses,
        contacts NO provider, and the audit chain still verifies."""
        parked = self._park_real()
        operator_digest = parked["digest"]

        code, _out, _err = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", operator_digest)
        self.assertEqual(code, 0)
        approved = self._pending()
        self.assertEqual(approved.get("approved_digest"), operator_digest)

        forged = self._forge_two_fields(approved, "\nPOST-APPROVAL INJECTION\n")
        self._set_pending(forged)

        j3 = self._open()
        loop3 = self._build_loop(
            j3, runner=FakeRunner(run_result()), reviewer=FakeReviewer(outcome()),
            approval_gate=lambda _d, _p: True, max_cycles=1)
        with self.assertRaises(LoopError) as ctx:
            loop3.run("ignored - read from journal")
        self.assertEqual(ctx.exception.code, "forwarded_prompt_unavailable")  # (4)(5)
        self.assertEqual(loop3.provider_calls, 0, "(6) no provider call on a refusal")
        j3.close()
        audit = AuditLog(self.runtime_dir / "audit.jsonl", fsync=False)
        self.assertTrue(audit.verify_chain().ok)                              # (7)


class HappyPathBinding(_CrossProcessHarness):
    def test_happy_path_forwards_once_and_binds(self) -> None:
        """R139(a): an authentic approval forwards exactly once, and the forwarded
        bytes verify against the approval-covered binding (the operator digest is the
        approval_digest of the reconstructable instruction)."""
        parked = self._park_real()
        operator_digest = parked["digest"]
        instruction = parked["approved_instruction"]
        # The binding is operator-covered: the operator digest IS the approval_digest of
        # the instruction, and the forwarded body is that instruction's reconstruction.
        self.assertEqual(lp.approval_digest(**instruction), operator_digest)
        self.assertEqual(lp.build_forwarded_prompt(**instruction), parked["prompt"])

        code, _out, _err = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", operator_digest)
        self.assertEqual(code, 0)
        self.assertEqual(self._state(), sm.FORWARD_PROMPT)

        j3 = self._open()
        complete = outcome(make_decision(decision="COMPLETE", next_claude_prompt="",
                                         evidence_refs=[{"path": "report.md"}]))
        loop3 = self._build_loop(
            j3, runner=FakeRunner(run_result(), run_result()),
            reviewer=FakeReviewer(complete), approval_gate=lambda _d, _p: True,
            max_cycles=2)
        run = loop3.run("ignored - read from journal")
        rows = self._outbox_rows(run.forwarded_message_ids[0])
        j3.close()

        self.assertEqual(len(run.forwarded_message_ids), 1, "forwards exactly once")
        forwarded = rows[0]["payload"]["prompt"]
        body, sep, _ = forwarded.partition("FORWARDED AT: ")
        self.assertTrue(sep, "the forward-time clock stamp is present")
        self.assertEqual(body, lp.build_forwarded_prompt(**instruction),
                         "the forwarded body verifies against the approval-covered "
                         "reconstruction; only the clock is appended")

    def _outbox_rows(self, message_id: str) -> list[dict]:
        import json
        j = self._open()
        try:
            rows = j.conn.execute(
                "SELECT envelope FROM outbox WHERE message_id = ?",
                (message_id,)).fetchall()
        finally:
            j.close()
        return [json.loads(r["envelope"]) for r in rows]


class ClockInvariant(unittest.TestCase):
    """R139(b) / R137: the S13.5 clock invariant is preserved - only the clock varies
    between renders, and the clock is excluded from the binding."""

    def test_clock_only_change_does_not_invalidate_the_approval(self) -> None:
        instruction = covered_pending()["approved_instruction"]
        body = lp.build_forwarded_prompt(**instruction)
        # Two forward-time stamps differ only in the clock.
        stamped_a = lp.stamp_forwarded_at(body)
        stamped_b = lp.stamp_forwarded_at(body)
        self.assertTrue(stamped_a.startswith(body) and stamped_b.startswith(body))
        # The operator-named approval digest is computed from the instruction, not the
        # stamped bytes, so it is identical across renders (executable S13.5).
        self.assertEqual(lp.approval_digest(**instruction),
                         lp.approval_digest(**instruction))
        # And the binding verification accepts regardless of any clock, because it
        # reconstructs the timestamp-free body and never inspects the stamp.
        operator_digest = lp.approval_digest(**instruction)
        returned = lp.verify_covered_instruction(
            instruction, operator_digest, body, lp.digest_of(body))
        self.assertEqual(returned, body,
                         "verification binds the timestamp-free body; the clock is "
                         "outside the binding entirely")


class PostureUnchanged(unittest.TestCase):
    """R139(d): the fix touches no authority / forwarding-guard / activation surface.
    Behavioural backstop for the grep-proof recorded in the producer report."""

    def test_shadow_supervised_posture_intact(self) -> None:
        self.assertFalse(lp.LoopConfig(mode="shadow", task_id="t", stage="s").forwards,
                         "shadow still forwards nothing")
        self.assertTrue(
            lp.LoopConfig(mode="supervised", task_id="t", stage="s").forwards,
            "supervised still forwards under approval")


class FailClosedReasonCodes(_CrossProcessHarness):
    """AS-6: old-shape / missing / malformed binding material each refuse fail-closed
    with DISTINCT reason codes, and a byte tamper is a distinct code again."""

    def _resume_and_reason(self, record: dict) -> tuple[int, str]:
        self._park_real()               # establish WAIT_FOR_OWNER via the real loop
        self._set_pending(record)       # then overwrite with the record under test
        code, _out, _err = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", record["digest"])
        refusals = [e for e in self._audit_events()
                    if e["event_type"] == "operator_resume_pending_prompt_refused"]
        return code, (refusals[-1]["detail"]["reason"] if refusals else "")

    def test_old_shape_missing_instruction_refuses_uncovered(self) -> None:
        record = covered_pending()
        record.pop("approved_instruction")            # pre-binding old shape
        code, reason = self._resume_and_reason(record)
        self.assertEqual(code, 1)
        self.assertEqual(reason, "pending_prompt_uncovered")

    def test_malformed_instruction_refuses_uncovered(self) -> None:
        record = covered_pending()
        record["approved_instruction"] = dict(record["approved_instruction"])
        del record["approved_instruction"]["stop_conditions"]   # missing key
        code, reason = self._resume_and_reason(record)
        self.assertEqual(code, 1)
        self.assertEqual(reason, "pending_prompt_uncovered")

    def test_instruction_not_reproducing_operator_digest_refuses_uncovered(self) -> None:
        record = covered_pending()
        # Tamper a COVERED field in the instruction: approval_digest no longer matches
        # the (unchanged) operator-named digest -> uncovered.
        record["approved_instruction"] = dict(record["approved_instruction"])
        record["approved_instruction"]["requested_action"] = "do something ELSE"
        code, reason = self._resume_and_reason(record)
        self.assertEqual(code, 1)
        self.assertEqual(reason, "pending_prompt_uncovered")

    def test_byte_anchor_tamper_refuses_tampered(self) -> None:
        record = covered_pending()
        evil = record["prompt"] + "\nINJECTED\n"
        record["prompt"] = evil
        record["prompt_bytes_digest"] = lp.digest_of(evil)  # consistent two-field forge
        code, reason = self._resume_and_reason(record)
        self.assertEqual(code, 1)
        self.assertEqual(reason, "pending_prompt_tampered")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
