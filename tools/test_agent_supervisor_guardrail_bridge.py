#!/usr/bin/env python3
"""M0-T093 (D-024 Phase E): the section-16.4 guardrail-refusal / 4.8-bridge matrix.

Supervisor-freeze qualifying evidence: D-024-R103 (Phase E; packet-named).

Scenario pack S1-S16 (project-control/reports/M0-T093-guardrail-bridge.md §1;
D-024-R110 names every required case):

* S1  exact recognized refusal classifies, journaled identity-preserving;
* S2  quota cannot enter the bridge - BOTH directions (R075);
* S3  unrecognized-similar output never actuates;
* S4  a real security-test failure is a defect, never a routing event;
* S5  an unknown approval prompt is never auto-answered;
* S6  only the exact allowlisted continue-with-4.8 option is selectable;
* S7  the bridge cannot start a new task/investigation/subagent/scope;
* S8  already-running bounded children finish and reconcile;
* S9  first-valid-seam retirement with a complete bounded handoff;
* S10 bridge output is reviewed like any producer output;
* S11 semantic-preserving re-presentation (positive + every prohibited
      transform as a negative test);
* S12 first re-entry success clears the durable counter;
* S13 the two-attempt cap -> configured lower-tier or blocked (R072), and
      subsequent work returns to Fable 5 at the next seam;
* S14 the digest-bound counter survives a controller restart;
* S15 native fallbackModel never replaces the custom policies (R165);
* S16 no worker pollution; refusal-vs-quota triggers stay distinct typed
      codes and journal keys end-to-end (R045/R184).

Plus: the two additive Phase-E states (D-024-R070/R071) with every new edge
walkable and documented, and REAL-`SupervisedLoop` seam tests proving the
record-intent-only divergence and the R075 quota-first ordering.

The recognized-shape corpus is documentation-confidence (verified_live=False
everywhere; the C1 live refusal canary is owner-gated, R192/R197) - these
tests assert that honesty directly.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import guardrail_refusal as gr  # noqa: E402
from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import policy as pol  # noqa: E402
from tools.agent_supervisor import refusal_bridge as rb  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.approved_models import ApprovedModels  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.child_handoff import (  # noqa: E402
    ChildHandoff,
    HandoffError,
    TurnoverCoordinator,
)
from tools.agent_supervisor.claude_runner import RunResult  # noqa: E402
from tools.agent_supervisor.codex_reviewer import (  # noqa: E402
    ReviewOutcome,
    map_decision_to_tier,
)
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.handoff import Handoff, RotationError  # noqa: E402
from tools.agent_supervisor.model_turnover import (  # noqa: E402
    ExhaustionClassification,
    TurnoverEvidence,
    classify_exhaustion,
)
from tools.agent_supervisor.models import (  # noqa: E402
    ClaudeCheckpoint,
    CodexDecision,
    digest_of,
)
from tools.agent_supervisor.state_machine import StateMachine  # noqa: E402
from tools.agent_supervisor.worker_turnover import (  # noqa: E402
    REASON_TURNOVER_LAUNCHED,
    REASON_TURNOVER_RECORDED,
    WorkerTurnoverIntegration,
)
from tools.agent_supervisor.workload_classifier import WorkloadFeatures  # noqa: E402

# --------------------------------------------------------------------------
# Shared fixtures
# --------------------------------------------------------------------------

#: The owner-approved chain these tests pretend the protected config declares
#: (the test_agent_supervisor_turnover_integration convention).
APPROVED = ApprovedModels(entries=("claude-fable-5", "claude-opus-4-8"),
                          source="test-config")
BRIDGE_MODEL = "claude-opus-4-8"

#: A PROVEN owner-authorization record (R068: legitimacy comes from the task
#: packet, never from the worker's output text).
AUTHORIZED = gr.AuthorizedTaskRecord(
    task_id="M0-T093",
    authorization="owner directive D-024 section 8; ledger task packet M0-T093",
    acceptance_criteria=("the section-16.4 matrix passes",),
    purpose="implement the guardrail-refusal classification and bounded bridge")

#: The documented structured refusal shape (fixture corpus entry).
REFUSAL_RESULT_EVENT: dict[str, Any] = {"type": "result", "stop_reason": "refusal"}

#: The exact R289 quota message (D-010 source-028) - the OTHER policy's signal.
FABLE_LIMIT_MESSAGE = (
    "You've reached your Fable 5 limit. Run /usage-credits to continue or "
    "switch models with /model.")


def refusal_evidence(**overrides: Any) -> gr.RefusalEvidence:
    data: dict[str, Any] = dict(
        stdout="", stderr="", exit_code=1,
        structured_result=dict(REFUSAL_RESULT_EVENT),
        model_id="claude-fable-5")
    data.update(overrides)
    return gr.RefusalEvidence(**data)


def refused_request(**overrides: Any) -> rb.RefusedRequest:
    data: dict[str, Any] = dict(
        task_id="M0-T093",
        purpose="implement the guardrail-refusal classifier",
        authorization="owner directive D-024 section 8; packet M0-T093",
        constraints=("stay inside tools/agent_supervisor",
                     "never touch .claude/hooks"),
        acceptance_criteria=("the S1-S16 matrix passes",
                            "quota and refusal stay distinct"),
        request_text="Implement guardrail_refusal.py per the frozen pack.")
    data.update(overrides)
    return rb.RefusedRequest(**data)


def valid_bridge_handoff() -> Handoff:
    return Handoff(
        task_and_stage="M0-T093 / bridge landing",
        authoritative_shas={"HEAD": "c" * 40},
        branch="control/D-024-fable-codex-loop",
        worktree="C:/repo/wt",
        completed_work="finished the smallest atomic operation",
        changed_files=("tools/agent_supervisor/guardrail_refusal.py",),
        tests_and_ci={"suite": "pending"},
        pull_request_state="none",
        reviews_and_findings=(),
        open_blockers=(),
        owner_gates=("C1 live refusal canary",),
        forbidden_scope=(".claude/hooks",),
        exact_next_action="start fresh Fable 5 from the durable artifacts",
        evidence_digests={"handoff": "d" * 64},
    )


class JournalCase(unittest.TestCase):
    """A real durable journal on disk (restart-survival needs the real thing)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.db_path = self.tmp / "journal.sqlite3"
        self.journal = DurableJournal(self.db_path).open()
        self.addCleanup(lambda: self.journal.close())


# --------------------------------------------------------------------------
# S1 - exact recognized refusal
# --------------------------------------------------------------------------


class S1RecognizedRefusalTests(JournalCase):
    def test_corpus_is_loaded_and_honestly_unverified(self) -> None:
        self.assertTrue(gr.RECOGNIZED_SHAPES,
                        "the committed corpus must load")
        for shape in gr.RECOGNIZED_SHAPES:
            self.assertFalse(shape.verified_live,
                             f"{shape.name}: no live capture exists on this "
                             f"build (owner-gated C1); verified_live must be "
                             f"False until then")
        self.assertFalse(gr.REFUSAL_SHAPE_VERIFIED)

    def test_recognized_shape_classifies_as_guardrail_refusal(self) -> None:
        verdict = gr.classify_guardrail_refusal(
            refusal_evidence(), authorized_task=AUTHORIZED)
        self.assertTrue(verdict.is_recognized_refusal)
        self.assertEqual(verdict.condition, gr.CONDITION_RECOGNIZED)
        self.assertEqual(verdict.matched_shape, "structured_stop_reason_refusal")
        self.assertFalse(verdict.shape_verified_live)

    def test_journal_record_preserves_identity_and_criteria(self) -> None:
        verdict = gr.classify_guardrail_refusal(
            refusal_evidence(), authorized_task=AUTHORIZED)
        record = rb.build_refusal_journal_record(
            verdict, AUTHORIZED, request_digest="a" * 64,
            evidence_excerpt="worker output excerpt")
        self.assertEqual(record["task_id"], AUTHORIZED.task_id)
        self.assertEqual(record["authorization"], AUTHORIZED.authorization)
        self.assertEqual(tuple(record["acceptance_criteria"]),
                         AUTHORIZED.acceptance_criteria)
        self.assertEqual(record["request_digest"], "a" * 64)
        self.assertTrue(record["at_utc"])

    def test_journal_record_is_bounded_and_redacted(self) -> None:
        verdict = gr.classify_guardrail_refusal(
            refusal_evidence(), authorized_task=AUTHORIZED)
        record = rb.build_refusal_journal_record(
            verdict, AUTHORIZED, request_digest="a" * 64,
            evidence_excerpt=("x" * 10_000
                              + " api_key=sk-ant-aaaaaaaaaaaaaaaaaaaaaaaa"))
        self.assertLessEqual(len(record["evidence_excerpt"]),
                             rb.MAX_EVIDENCE_EXCERPT_CHARS)
        self.assertNotIn("sk-ant-", json.dumps(record))

    def test_only_a_recognized_refusal_is_journaled_as_one(self) -> None:
        verdict = gr.classify_guardrail_refusal(
            refusal_evidence(structured_result=None),
            authorized_task=AUTHORIZED)
        self.assertFalse(verdict.is_recognized_refusal)
        with self.assertRaises(rb.BridgeError) as caught:
            rb.build_refusal_journal_record(verdict, AUTHORIZED,
                                            request_digest="a" * 64)
        self.assertEqual(caught.exception.code, "not_a_recognized_refusal")


# --------------------------------------------------------------------------
# S2 - quota cannot enter the bridge (BOTH directions, R075)
# --------------------------------------------------------------------------


class S2QuotaSeparationTests(unittest.TestCase):
    #: Quota-side evidence shapes, reusing the model_turnover/claude_runner
    #: pattern set (exact phrase, weekly rejection, typed code, 429 prose).
    QUOTA_EVIDENCE = (
        ("exact_weekly_phrase",
         dict(stdout=FABLE_LIMIT_MESSAGE, structured_result=None)),
        ("weekly_rate_limit_rejection",
         dict(structured_result={"rateLimitType": "seven_day",
                                 "status": "rejected",
                                 "model": "claude-fable-5"})),
        ("typed_quota_code",
         dict(structured_result={"code": "usage_limit_reached",
                                 "model": "claude-fable-5"})),
        ("bare_429_prose",
         dict(stdout="Error 429: rate limited", structured_result=None)),
    )

    def test_quota_evidence_never_classifies_as_refusal(self) -> None:
        for name, fields in self.QUOTA_EVIDENCE:
            with self.subTest(direction="quota->refusal", shape=name):
                verdict = gr.classify_guardrail_refusal(
                    refusal_evidence(**fields), authorized_task=AUTHORIZED)
                self.assertFalse(verdict.is_recognized_refusal)
                self.assertEqual(verdict.condition, gr.CONDITION_QUOTA_POLICY)

    def test_refusal_evidence_never_classifies_as_exhaustion(self) -> None:
        refusal_shapes = (
            ("structured_stop_reason",
             TurnoverEvidence(exit_code=1,
                              structured_result=dict(REFUSAL_RESULT_EVENT),
                              model_id="claude-fable-5")),
            ("refusal_looking_text",
             TurnoverEvidence(stdout="I can't help with that request.",
                              exit_code=1, model_id="claude-fable-5")),
        )
        for name, evidence in refusal_shapes:
            with self.subTest(direction="refusal->quota", shape=name):
                verdict = classify_exhaustion(evidence)
                self.assertIsNot(verdict.classification,
                                 ExhaustionClassification.FABLE_EXHAUSTED)
                self.assertFalse(verdict.should_turn_over)

    def test_recognized_shape_with_limit_wording_is_contradictory(self) -> None:
        verdict = gr.classify_guardrail_refusal(
            refusal_evidence(stdout="you may have hit a quota"),
            authorized_task=AUTHORIZED)
        self.assertIs(verdict.classification,
                      gr.RefusalClassification.AMBIGUOUS_FAIL_CLOSED)
        self.assertEqual(verdict.condition, gr.CONDITION_CONTRADICTORY)


# --------------------------------------------------------------------------
# S3 / S4 / S5 - the negative guards
# --------------------------------------------------------------------------


class S3UnrecognizedSimilarTests(unittest.TestCase):
    def test_refusal_looking_text_is_held_not_actuated(self) -> None:
        fixture = json.loads(gr.SHAPES_FIXTURE_PATH.read_text(encoding="utf-8"))
        examples = [e["example"] for e in fixture["unrecognized_similar_examples"]]
        self.assertTrue(examples)
        for text in examples:
            with self.subTest(text=text):
                verdict = gr.classify_guardrail_refusal(
                    refusal_evidence(stdout=text, structured_result=None),
                    authorized_task=AUTHORIZED)
                self.assertIs(verdict.classification,
                              gr.RefusalClassification.AMBIGUOUS_FAIL_CLOSED)
                self.assertEqual(verdict.condition,
                                 gr.CONDITION_REFUSAL_UNRECOGNIZED)

    def test_empty_corpus_recognizes_nothing(self) -> None:
        verdict = gr.classify_guardrail_refusal(
            refusal_evidence(), authorized_task=AUTHORIZED, corpus=())
        self.assertFalse(verdict.is_recognized_refusal)

    def test_missing_or_malformed_corpus_file_fails_closed(self) -> None:
        self.assertEqual(gr.load_shape_corpus("Z:/does/not/exist.json"), ())
        with tempfile.TemporaryDirectory() as tmp:
            bad = pathlib.Path(tmp) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            self.assertEqual(gr.load_shape_corpus(bad), ())
            poisoned = pathlib.Path(tmp) / "poisoned.json"
            poisoned.write_text(json.dumps({
                "recognized_shapes": [
                    {"name": "ok", "text_regex": "x"},
                    {"no_name": True},
                ]}), encoding="utf-8")
            self.assertEqual(gr.load_shape_corpus(poisoned), ())

    def test_empty_shape_is_never_a_catch_all(self) -> None:
        shape = gr.RefusalShapeFixture(name="empty")
        self.assertFalse(shape.matches("any text", {"stop_reason": "refusal"}))

    def test_authorization_unproven_never_actuates(self) -> None:
        for record in (None,
                       gr.AuthorizedTaskRecord(task_id="", authorization="x",
                                               acceptance_criteria=("a",)),
                       gr.AuthorizedTaskRecord(task_id="T", authorization="",
                                               acceptance_criteria=("a",)),
                       gr.AuthorizedTaskRecord(task_id="T", authorization="x")):
            with self.subTest(record=record):
                verdict = gr.classify_guardrail_refusal(
                    refusal_evidence(), authorized_task=record)
                self.assertFalse(verdict.is_recognized_refusal)
                self.assertEqual(verdict.condition,
                                 gr.CONDITION_AUTHORIZATION_UNPROVEN)

    def test_unattributable_shape_never_actuates(self) -> None:
        verdict = gr.classify_guardrail_refusal(
            refusal_evidence(model_id="some-other-model"),
            authorized_task=AUTHORIZED)
        self.assertFalse(verdict.is_recognized_refusal)
        self.assertEqual(verdict.condition, gr.CONDITION_NOT_ATTRIBUTABLE)

    def test_no_evidence_is_ambiguous(self) -> None:
        verdict = gr.classify_guardrail_refusal(None, authorized_task=AUTHORIZED)
        self.assertIs(verdict.classification,
                      gr.RefusalClassification.AMBIGUOUS_FAIL_CLOSED)


class S4SecurityDefectTests(unittest.TestCase):
    def test_failing_tests_are_defects_not_routing_events(self) -> None:
        for text in ("AssertionError: expected PASS",
                     "3 tests failed in tools/test_x.py",
                     "security test failed: RLS policy violated",
                     "gitleaks detected a finding",
                     "Traceback (most recent call last):"):
            with self.subTest(text=text):
                verdict = gr.classify_guardrail_refusal(
                    refusal_evidence(stdout=text, structured_result=None),
                    authorized_task=AUTHORIZED)
                self.assertEqual(verdict.classification,
                                 gr.RefusalClassification.NOT_A_REFUSAL)
                self.assertEqual(verdict.condition, gr.CONDITION_SECURITY_DEFECT)

    def test_permission_and_credential_boundaries_are_not_refusals(self) -> None:
        cases = (("Permission denied: cannot write", gr.CONDITION_PERMISSION_DENIED),
                 ("401 Unauthorized: token expired", gr.CONDITION_CREDENTIAL_BOUNDARY))
        for text, condition in cases:
            with self.subTest(text=text):
                verdict = gr.classify_guardrail_refusal(
                    refusal_evidence(stdout=text, structured_result=None),
                    authorized_task=AUTHORIZED)
                self.assertEqual(verdict.classification,
                                 gr.RefusalClassification.NOT_A_REFUSAL)
                self.assertEqual(verdict.condition, condition)


class S5ApprovalPromptTests(unittest.TestCase):
    def test_unknown_approval_prompt_is_never_a_refusal(self) -> None:
        for text in ("Do you want to allow this tool? (y/n)",
                     "Permission request: shell access [y/N]",
                     "waiting for your approval to continue"):
            with self.subTest(text=text):
                verdict = gr.classify_guardrail_refusal(
                    refusal_evidence(stdout=text, structured_result=None),
                    authorized_task=AUTHORIZED)
                self.assertEqual(verdict.classification,
                                 gr.RefusalClassification.NOT_A_REFUSAL)
                self.assertEqual(verdict.condition, gr.CONDITION_APPROVAL_PROMPT)

    def test_non_continuation_options_are_never_selected(self) -> None:
        offered = [
            {"kind": "approval", "label": "Allow shell command"},
            {"kind": "credential-prompt", "label": "Enter API key"},
            {"kind": "destructive-confirmation", "label": "Delete branch?"},
            {"kind": "merge", "label": "Merge PR #241"},
            {"kind": "deployment", "label": "Deploy to production"},
        ]
        choice = rb.continuation_choice(offered, approved=APPROVED,
                                        bridge_model_id=BRIDGE_MODEL)
        self.assertFalse(choice.selected)
        self.assertEqual(choice.reason_code, "exact_option_not_offered")


# --------------------------------------------------------------------------
# S6 - the exact allowlisted continue-with-4.8 option
# --------------------------------------------------------------------------


class S6AllowlistedContinuationTests(unittest.TestCase):
    def test_exact_allowlisted_option_is_the_single_selectable_choice(self) -> None:
        offered = [
            {"kind": "model-continuation", "model_id": BRIDGE_MODEL},
            {"kind": "stop"},
        ]
        choice = rb.continuation_choice(offered, approved=APPROVED,
                                        bridge_model_id=BRIDGE_MODEL)
        self.assertTrue(choice.selected)
        self.assertEqual(choice.option_index, 0)
        self.assertEqual(choice.reason_code, "exact_allowlisted_continuation")

    def test_wrong_model_id_refuses(self) -> None:
        offered = [{"kind": "model-continuation", "model_id": "claude-haiku-4-5"}]
        choice = rb.continuation_choice(offered, approved=APPROVED,
                                        bridge_model_id=BRIDGE_MODEL)
        self.assertFalse(choice.selected)
        self.assertEqual(choice.reason_code, "exact_option_not_offered")

    def test_unlisted_bridge_model_refuses_everything(self) -> None:
        offered = [{"kind": "model-continuation", "model_id": "not-approved"}]
        choice = rb.continuation_choice(
            offered, approved=APPROVED, bridge_model_id="not-approved")
        self.assertFalse(choice.selected)
        self.assertEqual(choice.reason_code, "bridge_model_not_allowlisted")

    def test_ambiguous_duplicate_options_refuse(self) -> None:
        offered = [{"kind": "model-continuation", "model_id": BRIDGE_MODEL},
                   {"kind": "model-continuation", "model_id": BRIDGE_MODEL}]
        choice = rb.continuation_choice(offered, approved=APPROVED,
                                        bridge_model_id=BRIDGE_MODEL)
        self.assertFalse(choice.selected)
        self.assertEqual(choice.reason_code, "ambiguous_options")

    def test_live_actuation_is_double_gated(self) -> None:
        with self.assertRaises(rb.BridgeError) as caught:
            rb.assert_actuation_permitted(shape_verified_live=False,
                                          owner_authorized=True)
        self.assertEqual(caught.exception.code,
                         "actuation_requires_measured_live_shape")
        with self.assertRaises(rb.BridgeError) as caught:
            rb.assert_actuation_permitted(shape_verified_live=True,
                                          owner_authorized=False)
        self.assertEqual(caught.exception.code,
                         "actuation_requires_owner_authorization")


# --------------------------------------------------------------------------
# S7 / S8 / S9 - the mechanically restricted bridge
# --------------------------------------------------------------------------


def child_handoff(assignment_id: str = "child-1") -> ChildHandoff:
    return ChildHandoff(
        assignment_id=assignment_id, parent_task_id="M0-T093",
        outcome="partial-landed", bounded_summary="landed at its seam",
        completed="the bounded sub-step",
        repository_state="clean at " + "c" * 40,
        exact_next_action="parent reconciles")


class S7BridgeRestrictionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.coordinator = TurnoverCoordinator("M0-T093")

    def test_permitted_operations_are_exactly_the_r070_four(self) -> None:
        bridge = rb.BridgeRestrictions(self.coordinator)
        for op in rb.PERMITTED_BRIDGE_OPERATIONS:
            self.assertEqual(bridge.authorize(op), op)
        self.assertEqual(bridge.performed, rb.PERMITTED_BRIDGE_OPERATIONS)

    def test_forbidden_operations_refuse_with_typed_error(self) -> None:
        bridge = rb.BridgeRestrictions(self.coordinator)
        for op in rb.FORBIDDEN_BRIDGE_OPERATIONS:
            with self.subTest(op=op):
                with self.assertRaises(rb.BridgeError) as caught:
                    bridge.authorize(op)
                self.assertEqual(caught.exception.code, "bridge_scope_forbidden")

    def test_unknown_operations_fail_closed(self) -> None:
        bridge = rb.BridgeRestrictions(self.coordinator)
        with self.assertRaises(rb.BridgeError) as caught:
            bridge.authorize("refactor-the-world")
        self.assertEqual(caught.exception.code, "bridge_unknown_operation")

    def test_bridge_never_spawns_children(self) -> None:
        bridge = rb.BridgeRestrictions(self.coordinator)
        self.assertFalse(bridge.may_spawn_children())
        with self.assertRaises(HandoffError) as caught:
            self.coordinator.register_child("new-child")
        self.assertEqual(caught.exception.code, "landing_in_progress")


class S8BoundedChildrenTests(unittest.TestCase):
    def test_existing_children_finish_and_reconcile(self) -> None:
        coordinator = TurnoverCoordinator("M0-T093")
        coordinator.register_child("child-1")
        coordinator.register_child("child-2")
        bridge = rb.BridgeRestrictions(coordinator)
        self.assertEqual(set(bridge.unreconciled_children()),
                         {"child-1", "child-2"})
        bridge.collect_child(child_handoff("child-1"))
        bridge.collect_child(child_handoff("child-2"))
        self.assertEqual(bridge.unreconciled_children(), ())


class S9SeamRetirementTests(unittest.TestCase):
    def test_retirement_requires_reconciled_children(self) -> None:
        coordinator = TurnoverCoordinator("M0-T093")
        coordinator.register_child("child-1")
        bridge = rb.BridgeRestrictions(coordinator)
        with self.assertRaises(rb.BridgeError) as caught:
            bridge.retire(valid_bridge_handoff())
        self.assertEqual(caught.exception.code, "children_unreconciled")

    def test_retirement_lands_once_and_never_continues(self) -> None:
        bridge = rb.BridgeRestrictions(TurnoverCoordinator("M0-T093"))
        outcome = bridge.retire(valid_bridge_handoff())
        self.assertTrue(outcome["retired"])
        self.assertIn("fresh Fable 5", outcome["successor_policy"])
        self.assertTrue(bridge.retired)
        for op in rb.PERMITTED_BRIDGE_OPERATIONS:
            with self.subTest(op=op):
                with self.assertRaises(rb.BridgeError) as caught:
                    bridge.authorize(op)
                self.assertEqual(caught.exception.code, "bridge_retired")

    def test_fresh_fable_receives_a_complete_bounded_handoff(self) -> None:
        bridge = rb.BridgeRestrictions(TurnoverCoordinator("M0-T093"))
        incomplete = valid_bridge_handoff()
        broken = Handoff.from_dict({**incomplete.to_dict(),
                                    "exact_next_action": ""})
        with self.assertRaises(RotationError):
            bridge.retire(broken)


# --------------------------------------------------------------------------
# S10 - bridge output is reviewed like any producer output
# --------------------------------------------------------------------------


class S10BridgeOutputReviewTests(unittest.TestCase):
    def test_completion_is_never_acceptance(self) -> None:
        disposition, reason = rb.bridge_output_disposition(None)
        self.assertEqual(disposition, rb.DISPOSITION_REVIEW_REQUIRED)
        self.assertIn("never auto-accepted", reason)

    def test_only_an_independent_pass_accepts(self) -> None:
        disposition, _ = rb.bridge_output_disposition({"verdict": "PASS"})
        self.assertEqual(disposition, rb.DISPOSITION_ACCEPTED_BY_REVIEW)

    def test_defective_output_is_rejected(self) -> None:
        for verdict in ("FAIL", "BLOCKED"):
            with self.subTest(verdict=verdict):
                disposition, _ = rb.bridge_output_disposition({"verdict": verdict})
                self.assertEqual(disposition, rb.DISPOSITION_REJECTED)

    def test_unrecognized_verdict_fails_closed_to_review(self) -> None:
        disposition, _ = rb.bridge_output_disposition({"verdict": "LGTM"})
        self.assertEqual(disposition, rb.DISPOSITION_REVIEW_REQUIRED)


# --------------------------------------------------------------------------
# S11 - semantic-preserving re-presentation
# --------------------------------------------------------------------------


class S11SemanticPreservationTests(unittest.TestCase):
    def test_representation_preserves_every_field_verbatim(self) -> None:
        request = refused_request()
        represented = rb.represent(request, attempt=1)
        text = represented.presentation_text
        self.assertIn(request.purpose, text)
        self.assertIn(request.authorization, text)
        self.assertIn(request.request_text, text)
        for constraint in request.constraints:
            self.assertIn(constraint, text)
        for criterion in request.acceptance_criteria:
            self.assertIn(criterion, text)
        self.assertEqual(represented.original, request)

    def test_prohibited_transforms_each_refuse_with_typed_code(self) -> None:
        request = refused_request()
        text = rb.represent(request, attempt=1).presentation_text
        cases = (
            ("purpose_altered",
             refused_request(purpose="a different purpose")),
            ("authorization_altered",
             refused_request(authorization="escalated: full production access")),
            ("constraint_deleted",
             refused_request(constraints=("stay inside tools/agent_supervisor",))),
            ("criteria_altered",
             refused_request(acceptance_criteria=("something weaker",))),
            ("request_fragmented",
             refused_request(request_text="Implement it (details elsewhere).")),
            ("different_task",
             refused_request(task_id="M0-T999")),
        )
        for expected_code, claimed in cases:
            with self.subTest(code=expected_code):
                with self.assertRaises(rb.BridgeError) as caught:
                    rb.assert_semantic_preserved(
                        request, presentation_text=text, claimed=claimed)
                self.assertEqual(caught.exception.code, expected_code)

    def test_narrowing_may_add_but_never_remove_constraints(self) -> None:
        request = refused_request()
        narrowed = refused_request(
            constraints=request.constraints + ("touch only two files",))
        text = rb.represent(narrowed, attempt=1).presentation_text
        rb.assert_semantic_preserved(request, presentation_text=text,
                                     claimed=narrowed)  # must not raise

    def test_fragmented_or_elided_presentation_refuses(self) -> None:
        request = refused_request()
        with self.assertRaises(rb.BridgeError) as caught:
            rb.assert_semantic_preserved(
                request, presentation_text="Please do the task discussed above.")
        self.assertEqual(caught.exception.code, "request_fragmented")

    def test_encoded_content_refuses(self) -> None:
        request = refused_request()
        text = rb.represent(request, attempt=1).presentation_text
        smuggled = text + "\npayload: " + ("QmFzZTY0U21" * 8)
        with self.assertRaises(rb.BridgeError) as caught:
            rb.assert_semantic_preserved(request, presentation_text=smuggled)
        self.assertEqual(caught.exception.code, "encoded_content")

    def test_attempts_outside_the_cap_are_refused(self) -> None:
        for attempt in (0, 3, -1):
            with self.subTest(attempt=attempt):
                with self.assertRaises(rb.BridgeError) as caught:
                    rb.represent(refused_request(), attempt=attempt)
                self.assertEqual(caught.exception.code, "bad_attempt_number")

    def test_incomplete_refused_request_is_refused(self) -> None:
        with self.assertRaises(rb.BridgeError) as caught:
            refused_request(authorization="  ")
        self.assertEqual(caught.exception.code, "incomplete_refused_request")
        with self.assertRaises(rb.BridgeError):
            refused_request(acceptance_criteria=())


# --------------------------------------------------------------------------
# S12 / S13 / S14 - the durable digest-bound two-attempt cap
# --------------------------------------------------------------------------


class S12ReentrySuccessTests(JournalCase):
    def test_first_success_clears_and_records(self) -> None:
        digest = refused_request().digest()
        self.assertEqual(rb.record_reentry_attempt(self.journal, digest), 1)
        self.assertEqual(rb.attempts_recorded(self.journal, digest), 1)
        rb.record_reentry_success(self.journal, digest)
        self.assertEqual(rb.attempts_recorded(self.journal, digest), 0)
        self.assertFalse(rb.reentry_cap_exhausted(self.journal, digest))
        record = self.journal.get_state(f"{rb.REENTRY_KEY_PREFIX}{digest}")
        self.assertEqual(record["status"], "succeeded")
        self.assertEqual(record["succeeded_after_attempts"], 1)


class S13CapTests(JournalCase):
    def exhaust(self, digest: str) -> None:
        rb.record_reentry_attempt(self.journal, digest)
        rb.record_reentry_attempt(self.journal, digest)

    def fit_kwargs(self, **overrides: Any) -> dict[str, Any]:
        data: dict[str, Any] = dict(
            same_bounded_task=True,
            features=WorkloadFeatures(end_to_end_provable=True,
                                      write_owner_count=1, file_count=3),
            resolved_model=BRIDGE_MODEL,
            model_context_window=200_000,
            packet_target_tokens=8_000,
            demonstrated_capable=True,
            approved=APPROVED)
        data.update(overrides)
        return data

    def test_third_attempt_is_refused_no_ping_pong(self) -> None:
        digest = refused_request().digest()
        self.exhaust(digest)
        self.assertTrue(rb.reentry_cap_exhausted(self.journal, digest))
        with self.assertRaises(rb.BridgeError) as caught:
            rb.record_reentry_attempt(self.journal, digest)
        self.assertEqual(caught.exception.code, "reentry_cap_exhausted")

    def test_lower_tier_only_reachable_after_the_cap(self) -> None:
        digest = refused_request().digest()
        rb.record_reentry_attempt(self.journal, digest)  # only one attempt
        with self.assertRaises(rb.BridgeError) as caught:
            rb.decide_after_cap(self.journal, digest, **self.fit_kwargs())
        self.assertEqual(caught.exception.code, "cap_not_exhausted")

    def test_configured_lower_tier_continues_the_same_task(self) -> None:
        digest = refused_request().digest()
        self.exhaust(digest)
        decision = rb.decide_after_cap(self.journal, digest, **self.fit_kwargs())
        self.assertEqual(decision.decision, rb.DECISION_CONTINUE_LOWER_TIER)
        self.assertTrue(decision.returns_to_fable_at_next_seam)
        self.assertIn("owner-gated", decision.reason)

    def test_higher_precedence_policy_conflict_blocks_and_cites(self) -> None:
        digest = refused_request().digest()
        self.exhaust(digest)
        decision = rb.decide_after_cap(
            self.journal, digest,
            **self.fit_kwargs(higher_precedence_conflict=
                              "D-XXX forbids lower-tier continuation on "
                              "legal-rule tasks"))
        self.assertEqual(decision.decision, rb.DECISION_BLOCKED)
        self.assertIn("D-XXX forbids", decision.reason)
        self.assertIn("owner", decision.reason)

    def test_a_different_task_is_refused_outright(self) -> None:
        digest = refused_request().digest()
        self.exhaust(digest)
        with self.assertRaises(rb.BridgeError) as caught:
            rb.decide_after_cap(self.journal, digest,
                                **self.fit_kwargs(same_bounded_task=False))
        self.assertEqual(caught.exception.code, "different_task_forbidden")

    def test_conservative_blocks(self) -> None:
        digest = refused_request().digest()
        self.exhaust(digest)
        blocked_cases = (
            ("lower_tier_not_allowlisted",
             self.fit_kwargs(resolved_model="unapproved-model")),
            ("workload_features_missing", self.fit_kwargs(features=None)),
            ("workload_not_continuable",
             self.fit_kwargs(features=WorkloadFeatures(graph_stale=True))),
            ("window_unknown",
             self.fit_kwargs(model_context_window=None)),
            ("capability_undemonstrated",
             self.fit_kwargs(demonstrated_capable=False)),
        )
        for expected_code, kwargs in blocked_cases:
            with self.subTest(code=expected_code):
                decision = rb.decide_after_cap(self.journal, digest, **kwargs)
                self.assertEqual(decision.decision, rb.DECISION_BLOCKED)
                self.assertEqual(decision.reason_code, expected_code)

    def test_subsequent_work_returns_to_fable_at_next_seam(self) -> None:
        self.assertEqual(rb.next_seam_model(fable_model="claude-fable-5"),
                         "claude-fable-5")
        self.assertEqual(
            rb.next_seam_model(fable_model="claude-fable-5",
                               explicit_policy_model="claude-opus-4-8"),
            "claude-opus-4-8")
        with self.assertRaises(rb.BridgeError):
            rb.next_seam_model(fable_model="  ")


class S14RestartSurvivalTests(JournalCase):
    def test_counter_survives_a_controller_restart(self) -> None:
        digest = refused_request().digest()
        self.assertEqual(rb.record_reentry_attempt(self.journal, digest), 1)
        self.journal.close()

        reopened = DurableJournal(self.db_path).open()
        try:
            # The SAME refused request (same digest) continues at attempt 2 -
            # the count is digest-bound and durable, never reset by a restart.
            self.assertEqual(rb.attempts_recorded(reopened, digest), 1)
            self.assertEqual(rb.record_reentry_attempt(reopened, digest), 2)
            self.assertTrue(rb.reentry_cap_exhausted(reopened, digest))
            # A DIFFERENT request has its own untouched counter.
            other = refused_request(request_text="another request").digest()
            self.assertEqual(rb.attempts_recorded(reopened, other), 0)
        finally:
            reopened.close()
        self.journal = DurableJournal(self.db_path).open()  # for teardown


# --------------------------------------------------------------------------
# S15 - fallbackModel never replaces the custom policies
# --------------------------------------------------------------------------


class S15FallbackModelBoundaryTests(unittest.TestCase):
    def test_native_fallback_scope_is_fixed_regardless_of_config(self) -> None:
        for configured in (True, False):
            with self.subTest(configured=configured):
                scope = rb.fallback_model_scope(configured)
                self.assertEqual(scope["native_fallback_configured"], configured)
                self.assertFalse(scope["native_fallback_governs_guardrail_refusals"])
                self.assertFalse(scope["native_fallback_governs_quota_exhaustion"])
                self.assertIn("availability/overload", scope["native_fallback_scope"])


# --------------------------------------------------------------------------
# S16 - hygiene + distinct typed triggers end-to-end
# --------------------------------------------------------------------------


class S16HygieneAndDistinctnessTests(JournalCase):
    def test_bridge_texts_carry_no_worker_pressure_language(self) -> None:
        from tools.agent_supervisor.subagent_contracts import (
            assert_worker_text_clean,
        )
        represented = rb.represent(refused_request(), attempt=1)
        assert_worker_text_clean("re-presentation",
                                 represented.presentation_text)
        verdict = gr.classify_guardrail_refusal(
            refusal_evidence(), authorized_task=AUTHORIZED)
        record = rb.build_refusal_journal_record(
            verdict, AUTHORIZED, request_digest="a" * 64)
        assert_worker_text_clean("refusal_record", json.dumps(record))

    def test_refusal_and_quota_codes_are_disjoint(self) -> None:
        refusal_codes = {
            rb.REASON_REFUSAL_RECORDED,
            gr.CONDITION_RECOGNIZED, gr.CONDITION_QUOTA_POLICY,
            gr.CONDITION_REFUSAL_UNRECOGNIZED, gr.CONDITION_CONTRADICTORY,
        }
        quota_codes = {
            REASON_TURNOVER_LAUNCHED, REASON_TURNOVER_RECORDED,
            "quota_exhausted",
            ExhaustionClassification.FABLE_EXHAUSTED.value,
        }
        self.assertFalse(refusal_codes & quota_codes)

    def test_refusal_journal_keys_are_their_own_namespace(self) -> None:
        self.assertTrue(rb.REFUSAL_RECORD_KEY_PREFIX.startswith("guardrail_"))
        self.assertTrue(rb.REENTRY_KEY_PREFIX.startswith("guardrail_"))
        self.assertNotEqual(rb.REFUSAL_RECORD_KEY_PREFIX, rb.REENTRY_KEY_PREFIX)

    def test_status_facts_report_unknown_never_zero(self) -> None:
        facts = rb.refusal_status_facts(self.journal)
        self.assertEqual(facts[0]["label"], "last_recognized_refusal_digest")
        self.assertEqual(facts[0]["value"], "none-recorded")
        self.journal.set_state(rb.LAST_REFUSAL_KEY, "a" * 64)
        facts = rb.refusal_status_facts(self.journal)
        by_label = {f["label"]: f["value"] for f in facts}
        self.assertEqual(by_label["reentry_attempts_for_last_refusal"],
                         "none-recorded")


# --------------------------------------------------------------------------
# The additive Phase-E states (R070/R071; the unit-F worked pattern)
# --------------------------------------------------------------------------


class PhaseEStateMachineTests(JournalCase):
    def setUp(self) -> None:
        super().setUp()
        self.audit = AuditLog(self.tmp / "audit.jsonl", fsync=False)

    def machine(self) -> StateMachine:
        return StateMachine(self.journal, self.audit, run_id="run-h1")

    def test_the_two_phase_e_states_exist_and_are_not_blocking_or_terminal(self) -> None:
        for state in (sm.GUARDRAIL_BRIDGE, sm.REPRESENT_FABLE):
            self.assertIn(state, sm.STATES)
            self.assertNotIn(state, sm.BLOCKING_STATES)
            self.assertNotIn(state, sm.TERMINAL_STATES)
        # 27 at unit F (M0-T092) + GUARDRAIL_BRIDGE + REPRESENT_FABLE
        # (M0-T093, D-024-R070/R071/R103).
        self.assertEqual(len(sm.STATES), 29)

    def test_every_new_edge_is_walkable_and_documented(self) -> None:
        new_states = {sm.GUARDRAIL_BRIDGE, sm.REPRESENT_FABLE}
        edges = [t for t in sm.TRANSITIONS
                 if t.state_from in new_states or t.state_to in new_states]
        self.assertGreaterEqual(len(edges), 11)
        for transition in edges:
            with self.subTest(edge=f"{transition.state_from}->{transition.state_to}"):
                self.assertTrue(transition.doc.strip())
                self.journal.set_state(sm.STATE_KEY, transition.state_from)
                self.journal.set_state(sm.LAST_TRIGGER_KEY, "")
                result = self.machine().transition(transition.state_to,
                                                   transition.trigger)
                self.assertTrue(result.applied)

    def test_new_states_have_exit_edges_and_refuse_illegal_entry(self) -> None:
        for state in (sm.GUARDRAIL_BRIDGE, sm.REPRESENT_FABLE):
            self.assertTrue(sm.legal_targets(state),
                            f"{state} would strand the journal with no exit")
            with self.subTest(state=state):
                with self.assertRaises(sm.IllegalTransitionError):
                    self.machine().transition(state, "owner_emergency_stop")

    def test_the_activated_refusal_path_is_walkable_end_to_end(self) -> None:
        """The full R070/R071 journey through the table: refusal -> bridge ->
        seam -> fresh session -> re-present -> (accept | repeat | cap)."""
        machine = self.machine()
        self.journal.set_state(sm.STATE_KEY, sm.CLAUDE_RUNNING)
        machine.transition(sm.GUARDRAIL_BRIDGE, "guardrail_refusal_recognized")
        machine.transition(sm.PREPARE_ROTATION, "bridge_first_seam_reached")
        machine.transition(sm.VERIFY_HANDOFF, "handoff_generated")
        machine.transition(sm.START_FRESH_SESSION, "handoff_verified")
        machine.transition(sm.REPRESENT_FABLE, "represent_refused_request")
        machine.transition(sm.CLAUDE_RUNNING, "representation_accepted")
        # Second refusal within the cap loops through ONE more bridge.
        machine.transition(sm.GUARDRAIL_BRIDGE, "guardrail_refusal_recognized")
        machine.transition(sm.PREPARE_ROTATION, "bridge_first_seam_reached")
        machine.transition(sm.VERIFY_HANDOFF, "handoff_generated")
        machine.transition(sm.START_FRESH_SESSION, "handoff_verified")
        machine.transition(sm.REPRESENT_FABLE, "represent_refused_request")
        machine.transition(sm.WAIT_FOR_OWNER, "refusal_cap_blocked")


# --------------------------------------------------------------------------
# Loop seam tests: the REAL SupervisedLoop diverges record-intent-only
# (mirrors the test_agent_supervisor_turnover_integration harness)
# --------------------------------------------------------------------------


def checkpoint(**overrides: Any) -> ClaudeCheckpoint:
    data: dict[str, Any] = dict(
        schema_version="1.0.0", run_id="run-guardrail", checkpoint_id="cp-1",
        task_id="M0-T093", claude_session_id="sess-1", status="UNIT_COMPLETE",
        summary="unit complete", starting_sha="a" * 40, current_sha="b" * 40,
        branch="task/M0-T093-guardrail", worktree="/repo/wt",
        proposed_next_action="continue", usage="unknown",
        context_pressure="unknown")
    data.update(overrides)
    return ClaudeCheckpoint(**data)


def decision(**overrides: Any) -> CodexDecision:
    data: dict[str, Any] = dict(
        schema_version="1.0.0", decision="CONTINUE", reviewed_task_id="M0-T093",
        reviewed_checkpoint_id="cp-1", verified_repo_head="b" * 40,
        verified_origin_main="a" * 40, model_used="fake-review-model",
        next_claude_prompt="Do the next bounded unit.")
    data.update(overrides)
    return CodexDecision(**data)


def review_outcome() -> ReviewOutcome:
    actual = decision()
    return ReviewOutcome(decision=actual, model_used="fake-review-model",
                         selection_digest="sel", attempts=1,
                         decision_digest=digest_of(actual.to_dict()),
                         tier=map_decision_to_tier(actual))


class FakeRunner:
    def __init__(self, *results: RunResult, model: str = "") -> None:
        self.results = list(results)
        self.prompts: list[str] = []
        from tools.agent_supervisor.claude_runner import RunnerConfig
        self.config = RunnerConfig(executable="fake-claude", model=model,
                                   expected_model=model)

    def with_model(self, model: str) -> "FakeRunner":
        clone = FakeRunner(*self.results, model=model)
        clone.prompts = self.prompts
        return clone

    def run_unit(self, prompt: str, **_kwargs: Any) -> RunResult:
        self.prompts.append(prompt)
        return self.results[min(len(self.prompts) - 1, len(self.results) - 1)]


class FakeReviewer:
    def __init__(self, outcome: ReviewOutcome) -> None:
        self.outcome = outcome

    def review(self, packet: Any, **_kwargs: Any) -> ReviewOutcome:
        return self.outcome


def refusal_failed_result() -> RunResult:
    """A failed unit whose stream carries the typed refusal result event."""
    return RunResult(
        argv=("fake",), returncode=1, duration_seconds=0.1,
        session_id="sess-fable", checkpoint=None,
        checkpoint_error="the worker exited without a valid checkpoint",
        containment="job_object",
        raw_events=(dict(REFUSAL_RESULT_EVENT),))


def ordinary_failed_result(stderr: str) -> RunResult:
    return RunResult(
        argv=("fake",), returncode=1, duration_seconds=0.1,
        session_id="sess-fable", checkpoint=None,
        checkpoint_error="the worker exited without a valid checkpoint",
        stderr_tail=stderr, containment="job_object")


class LoopSeamTestBase(JournalCase):
    def setUp(self) -> None:
        super().setUp()
        self.repo = self.tmp / "repo"
        (self.repo / "tools").mkdir(parents=True)
        self.audit = AuditLog(self.tmp / "audit.jsonl", fsync=False)
        self.run_id = "run-guardrail"
        self.machine = StateMachine(self.journal, self.audit, self.run_id)
        self.authority = pol.TaskAuthority.from_packet(
            {"task_id": "M0-T093",
             "allowed_paths": ["tools/agent_supervisor/**"],
             "forbidden_paths": [".github/**"], "status": "in_progress"},
            repo_root=str(self.repo), worktree=str(self.repo),
            branch="task/M0-T093-guardrail", stage="phase4")

    def integration(self) -> rb.GuardrailBridgeIntegration:
        return rb.GuardrailBridgeIntegration(journal=self.journal,
                                             authorized_task=AUTHORIZED)

    def build(self, *, runner: Any, guardrail_bridge: Any,
              worker_turnover: Any = None) -> lp.SupervisedLoop:
        return lp.SupervisedLoop(
            config=lp.LoopConfig(mode="supervised", task_id="M0-T093",
                                 stage="phase4",
                                 allowed_paths=self.authority.allowed_paths,
                                 max_cycles=4, owner_touch_budget=4),
            journal=self.journal, audit=self.audit, machine=self.machine,
            authority=self.authority, runner=runner,
            reviewer=FakeReviewer(review_outcome()), run_id=self.run_id,
            pinned_model="claude-fable-5",
            worker_turnover=worker_turnover,
            guardrail_bridge=guardrail_bridge)

    def at_preflight(self) -> None:
        self.machine.transition(sm.PREFLIGHT, "start_command")


class LoopSeamTests(LoopSeamTestBase):
    def test_recognized_refusal_records_intent_and_pauses(self) -> None:
        runner = FakeRunner(refusal_failed_result(), model="claude-fable-5")
        loop = self.build(runner=runner, guardrail_bridge=self.integration())
        self.at_preflight()

        result = loop.run_cycle("do the unit", cycle=1)

        self.assertEqual(result.stopped, rb.REASON_REFUSAL_RECORDED)
        self.assertEqual(result.reached_state, sm.PAUSED_RECOVERY)
        last = self.journal.get_state(rb.LAST_REFUSAL_KEY)
        self.assertTrue(last)
        record = self.journal.get_state(
            f"{rb.REFUSAL_RECORD_KEY_PREFIX}{last}")
        self.assertEqual(record["task_id"], AUTHORIZED.task_id)
        self.assertEqual(record["authorization"], AUTHORIZED.authorization)
        self.assertEqual(record["matched_shape"],
                         "structured_stop_reason_refusal")
        # Record-intent-only: no re-entry attempt was consumed by recording.
        self.assertEqual(rb.attempts_recorded(self.journal, last), 0)

    def test_ordinary_failure_keeps_the_existing_pause(self) -> None:
        runner = FakeRunner(
            ordinary_failed_result("Traceback: ordinary build failure"),
            model="claude-fable-5")
        loop = self.build(runner=runner, guardrail_bridge=self.integration())
        self.at_preflight()

        result = loop.run_cycle("do the unit", cycle=1)

        self.assertEqual(result.stopped, "no_valid_checkpoint")
        self.assertIsNone(self.journal.get_state(rb.LAST_REFUSAL_KEY))

    def test_refusal_looking_text_never_diverges(self) -> None:
        runner = FakeRunner(
            ordinary_failed_result("I can't help with that request."),
            model="claude-fable-5")
        loop = self.build(runner=runner, guardrail_bridge=self.integration())
        self.at_preflight()

        result = loop.run_cycle("do the unit", cycle=1)

        self.assertEqual(result.stopped, "no_valid_checkpoint")
        self.assertIsNone(self.journal.get_state(rb.LAST_REFUSAL_KEY))

    def test_absent_integration_leaves_the_path_unchanged(self) -> None:
        runner = FakeRunner(refusal_failed_result(), model="claude-fable-5")
        loop = self.build(runner=runner, guardrail_bridge=None)
        self.at_preflight()

        result = loop.run_cycle("do the unit", cycle=1)

        self.assertEqual(result.stopped, "no_valid_checkpoint")
        self.assertEqual(result.reached_state, sm.PAUSED_RECOVERY)

    def test_quota_seam_evaluates_first_and_wins_its_signal(self) -> None:
        """R075 ordering: the quota detect-and-hold policy sees a quota signal
        BEFORE the refusal seam; the bridge records nothing for it."""
        runner = FakeRunner(
            ordinary_failed_result(FABLE_LIMIT_MESSAGE),
            model="claude-fable-5")
        loop = self.build(runner=runner,
                          guardrail_bridge=self.integration(),
                          worker_turnover=WorkerTurnoverIntegration())
        self.at_preflight()

        result = loop.run_cycle("do the unit", cycle=1)

        self.assertEqual(result.stopped, REASON_TURNOVER_RECORDED)
        self.assertIsNone(self.journal.get_state(rb.LAST_REFUSAL_KEY))

    def test_refusal_signal_with_both_seams_takes_the_refusal_path(self) -> None:
        runner = FakeRunner(refusal_failed_result(), model="claude-fable-5")
        loop = self.build(runner=runner,
                          guardrail_bridge=self.integration(),
                          worker_turnover=WorkerTurnoverIntegration())
        self.at_preflight()

        result = loop.run_cycle("do the unit", cycle=1)

        self.assertEqual(result.stopped, rb.REASON_REFUSAL_RECORDED)
        self.assertTrue(self.journal.get_state(rb.LAST_REFUSAL_KEY))


class IntegrationEvaluateTests(JournalCase):
    def test_decision_is_never_actuated_and_summary_is_clean(self) -> None:
        integration = rb.GuardrailBridgeIntegration(
            journal=self.journal, authorized_task=AUTHORIZED)
        decision_result = integration.evaluate(
            refusal_failed_result(), current_model="claude-fable-5",
            config=object(), run_id="run-guardrail", cycle=1)
        self.assertTrue(decision_result.triggered)
        self.assertFalse(decision_result.actuated)
        self.assertEqual(decision_result.reason_code,
                         rb.REASON_REFUSAL_RECORDED)
        self.assertEqual(decision_result.audit_summary["guardrail"],
                         "recorded_intent_shadow_only")
        self.assertFalse(decision_result.audit_summary["shape_verified_live"])

    def test_unproven_authorization_never_triggers(self) -> None:
        integration = rb.GuardrailBridgeIntegration(
            journal=self.journal, authorized_task=None)
        decision_result = integration.evaluate(
            refusal_failed_result(), current_model="claude-fable-5",
            config=object(), run_id="run-guardrail", cycle=1)
        self.assertFalse(decision_result.triggered)
        self.assertIsNone(self.journal.get_state(rb.LAST_REFUSAL_KEY))

    def test_rate_limit_rejection_routes_to_the_quota_policy(self) -> None:
        integration = rb.GuardrailBridgeIntegration(
            journal=self.journal, authorized_task=AUTHORIZED)
        result = RunResult(
            argv=("fake",), returncode=1, duration_seconds=0.1,
            session_id="sess-fable", checkpoint=None,
            checkpoint_error="no checkpoint", containment="job_object",
            rate_limit_rejection={"rateLimitType": "seven_day",
                                  "status": "rejected",
                                  "model": "claude-fable-5"})
        decision_result = integration.evaluate(
            result, current_model="claude-fable-5",
            config=object(), run_id="run-guardrail", cycle=1)
        self.assertFalse(decision_result.triggered)
        self.assertEqual(decision_result.verdict.condition,
                         gr.CONDITION_QUOTA_POLICY)


if __name__ == "__main__":
    unittest.main()
