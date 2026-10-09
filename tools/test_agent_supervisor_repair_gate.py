#!/usr/bin/env python3
"""Executable proofs for the D-024 Phase G repair gate (sections 16.6 + 16.8).

Supervisor-freeze qualifying evidence: **D-024-R105** (task M0-T095); the
matrices are D-024-R112 (16.6) and D-024-R114 (16.8). SHADOW-ONLY: every proof
runs against frozen records, fakes, and a temporary journal; no test contacts a
real remote or lifts the R595 activation gate.

Prove-first (R018/R114): the `Section168RegisterTests` register maps EVERY named
16.8 case to the file + named test that proves it. Cases already proven by the
existing `github_flow` / `external_effects` / `push_policy` / reviewer packs are
CITED there, not re-implemented; only the unproven cases (E6 PR-create
idempotence, E7 review invalidation, E10/E11 PR classification, E13 freeze
citation, E14 consolidated round) get new tests in this file.
"""
from __future__ import annotations

import pathlib
import re
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import evidence as ev  # noqa: E402
from tools.agent_supervisor import github_flow as gf  # noqa: E402
from tools.agent_supervisor import repair_gate as rg  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.models import canonical_json  # noqa: E402
from tools.agent_supervisor.review_packet import (  # noqa: E402
    PROHIBITED_MARKER_KEYS, guard_packet)

TASK = "M0-T095"
DEFECT = "DF-095-1"
IDENTITY_A = "a" * 12
IDENTITY_B = "b" * 12


def direct_record(**overrides) -> rg.RepairRecord:
    """A sound direct root-cause repair that passes every R076 predicate."""
    base = dict(
        task_id=TASK, defect_id=DEFECT,
        reproduction_ref="tools/test_x.py::test_reproduces_df_095_1",
        root_cause="the parser trusted an unvalidated length field",
        owning_boundary="tools/agent_supervisor/example_parser.py",
        preserved_behavior="valid frames keep parsing byte-identically",
        regression_test_id="tools/test_x.py::test_df_095_1_regression",
        regression_test_exists=True,
        regression_test_references_defect=True,
        regression_failure_condition="fails when the length guard is removed",
        mode=rg.MODE_DIRECT_REPAIR,
        one_authoritative_path=True)
    base.update(overrides)
    return rg.RepairRecord(**base)


def replacement_record(**overrides) -> rg.RepairRecord:
    """A fully proven bounded replacement (removal + unreachability evidence)."""
    base = dict(
        mode=rg.MODE_BOUNDED_REPLACEMENT,
        obsolete_implementation_removed=True,
        dead_callers_removed=True,
        duplicate_fallbacks_removed=True,
        unreachability_evidence=(
            rg.UnreachabilityEvidence(
                "search", "grep -rn old_parse_frame tools/",
                "no matches outside the removed module and its tests"),
            rg.UnreachabilityEvidence(
                "code_graph", "who-consumes old_parse_frame",
                "no remaining consumers")))
    base.update(overrides)
    return direct_record(**base)


def complete_answers(**overrides) -> dict[str, str]:
    answers = {key: f"substantive answer for {key}" for key in rg.CHECKPOINT_QUESTIONS}
    answers.update(overrides)
    return answers


def complete_exception(**overrides) -> rg.CompatibilityException:
    base = dict(
        exception_id="CE-1",
        reason="the v1 payload shape must keep parsing during the migration",
        owner=TASK,
        removal_condition="zero v1 payloads observed for 14 consecutive days",
        telemetry_key="payload_shape_v1_hits",
        removal_task_id="M0-T199",
        removal_deadline="2026-10-01T00:00:00+00:00",
        anti_default_tests=("tools/test_x.py::test_v2_is_the_default_path",))
    base.update(overrides)
    return rg.CompatibilityException(**base)


def green_merge_request(**overrides) -> gf.MergeRequest:
    """A MergeRequest whose ten S5.5 conditions all hold (mirrors the github_flow
    pack's helper; rebuilt here so this file stays import-independent of it)."""
    base = dict(
        task_id=TASK, task_authorized=True, dependency_valid=True,
        changed_paths=("services/api/app.py",),
        task_allowed_paths=("services/api/**",),
        required_checks={"unit": True, "ci": True},
        secret_scan_findings=(), completed_reviews={}, blocking_findings=(),
        is_production_deploy=False, will_record_main_sha=True,
        task_state_transactional=True,
        expected_remote_head="e" * 40, observed_remote_head="e" * 40,
        remote_state_known=True, mergeable=True)
    base.update(overrides)
    return gf.MergeRequest(**base)


# ==========================================================================
# 16.6 T1 - patch-stacking rejection (R076/R078/R112)
# ==========================================================================


class T1PatchStackingTests(unittest.TestCase):
    def test_an_unjustified_layer_around_a_known_bad_path_is_rejected(self) -> None:
        for kind in rg.LAYER_KINDS:
            with self.subTest(kind=kind):
                record = direct_record(added_layers=(
                    rg.AddedLayer(kind, around_known_bad_path=True),))
                evaluation = rg.evaluate_repair(record)
                self.assertFalse(evaluation.accepted)
                self.assertIn("patch_stacking", evaluation.refusal_codes())

    def test_a_justified_layer_is_not_patch_stacking(self) -> None:
        record = direct_record(added_layers=(
            rg.AddedLayer("retry", around_known_bad_path=True,
                          justification="the remote is genuinely flaky; the root "
                                        "cause (bad request shape) is fixed too"),))
        evaluation = rg.evaluate_repair(record)
        self.assertTrue(evaluation.accepted, evaluation.refusal_codes())

    def test_a_layer_not_around_a_known_bad_path_needs_no_justification(self) -> None:
        record = direct_record(added_layers=(
            rg.AddedLayer("flag", around_known_bad_path=False),))
        self.assertTrue(rg.evaluate_repair(record).accepted)


# ==========================================================================
# 16.6 T2 - direct root-cause repair accepted without a forced rewrite
# ==========================================================================


class T2DirectRepairTests(unittest.TestCase):
    def test_a_direct_root_cause_repair_is_accepted_without_a_forced_rewrite(self) -> None:
        evaluation = rg.evaluate_repair(direct_record())
        self.assertTrue(evaluation.accepted, evaluation.refusal_codes())
        proof = {f.name: f for f in evaluation.findings}["replacement_proof"]
        self.assertEqual(proof.reason_code, "direct_repair_mode")
        self.assertIn("no broad rewrite", proof.detail)

    def test_reproduce_first_is_enforced(self) -> None:
        record = direct_record(reproduction_ref="", falsifiable_failure_condition="")
        evaluation = rg.evaluate_repair(record)
        self.assertFalse(evaluation.accepted)
        self.assertIn("defect_not_reproduced", evaluation.refusal_codes())

    def test_a_falsifiable_failure_condition_also_satisfies_reproduce_first(self) -> None:
        record = direct_record(
            reproduction_ref="",
            falsifiable_failure_condition="any frame > 64KiB crashes the parser")
        self.assertTrue(rg.evaluate_repair(record).accepted)

    def test_a_missing_root_cause_or_boundary_is_rejected(self) -> None:
        for overrides in ({"root_cause": ""}, {"owning_boundary": " "}):
            with self.subTest(overrides=overrides):
                evaluation = rg.evaluate_repair(direct_record(**overrides))
                self.assertIn("root_cause_missing", evaluation.refusal_codes())

    def test_uncharacterized_preserved_behavior_is_rejected(self) -> None:
        evaluation = rg.evaluate_repair(direct_record(preserved_behavior=""))
        self.assertIn("preserved_behavior_missing", evaluation.refusal_codes())


# ==========================================================================
# 16.6 T3 - bounded replacement requires removal + unreachability proof
# ==========================================================================


class T3BoundedReplacementTests(unittest.TestCase):
    def test_a_fully_proven_replacement_is_accepted(self) -> None:
        evaluation = rg.evaluate_repair(replacement_record())
        self.assertTrue(evaluation.accepted, evaluation.refusal_codes())

    def test_replacement_without_each_removal_proof_is_rejected(self) -> None:
        for missing in ("obsolete_implementation_removed", "dead_callers_removed",
                        "duplicate_fallbacks_removed"):
            with self.subTest(missing=missing):
                evaluation = rg.evaluate_repair(replacement_record(**{missing: False}))
                self.assertFalse(evaluation.accepted)
                self.assertIn("replacement_unproven", evaluation.refusal_codes())

    def test_replacement_without_unreachability_evidence_is_rejected(self) -> None:
        evaluation = rg.evaluate_repair(replacement_record(unreachability_evidence=()))
        self.assertIn("replacement_unproven", evaluation.refusal_codes())


# ==========================================================================
# 16.6 T4 - recorded stale callers refuse "one authoritative path"
# ==========================================================================


class T4StaleCallerTests(unittest.TestCase):
    def test_reachable_stale_callers_refuse_one_authoritative_path(self) -> None:
        record = replacement_record(
            reachable_stale_callers=("legacy_cli.py:44", "fallback_v1.py:12"))
        evaluation = rg.evaluate_repair(record)
        self.assertFalse(evaluation.accepted)
        refusal = {f.name: f for f in evaluation.findings}["one_authoritative_path"]
        self.assertEqual(refusal.reason_code, "stale_callers_reachable")
        self.assertIn("legacy_cli.py:44", refusal.detail)

    def test_resolved_callers_restore_the_authoritative_path(self) -> None:
        self.assertTrue(rg.evaluate_repair(replacement_record()).accepted)

    def test_an_unconfirmed_authoritative_path_is_rejected(self) -> None:
        evaluation = rg.evaluate_repair(direct_record(one_authoritative_path=False))
        self.assertIn("authoritative_path_unconfirmed", evaluation.refusal_codes())


# ==========================================================================
# 16.6 T5 - the regression test must be bound to the defect
# ==========================================================================


class T5RegressionBindingTests(unittest.TestCase):
    def test_an_unbound_regression_test_is_rejected(self) -> None:
        for overrides in ({"regression_test_id": ""},
                          {"regression_test_exists": False},
                          {"regression_test_references_defect": False},
                          {"regression_failure_condition": ""}):
            with self.subTest(overrides=overrides):
                evaluation = rg.evaluate_repair(direct_record(**overrides))
                self.assertFalse(evaluation.accepted)
                self.assertIn("regression_test_unbound", evaluation.refusal_codes())

    def test_a_bound_regression_test_passes(self) -> None:
        finding = rg.check_regression_test(direct_record())
        self.assertTrue(finding.ok)
        self.assertIn("test_df_095_1_regression", finding.detail)


# ==========================================================================
# 16.6 T6 - CompatibilityException: one typed refusal per missing field
# ==========================================================================


class T6CompatibilityFieldTests(unittest.TestCase):
    def test_each_missing_field_produces_its_own_typed_refusal(self) -> None:
        for field, code in rg.COMPATIBILITY_REQUIRED_FIELDS.items():
            blank = () if field == "anti_default_tests" else ""
            with self.subTest(field=field):
                findings = rg.evaluate_compatibility_exception(
                    complete_exception(**{field: blank}))
                self.assertEqual([f.reason_code for f in findings], [code])
                self.assertFalse(findings[0].ok)

    def test_a_complete_exception_yields_a_single_ok(self) -> None:
        findings = rg.evaluate_compatibility_exception(complete_exception())
        self.assertEqual([f.reason_code for f in findings], ["compatibility_complete"])
        self.assertTrue(findings[0].ok)

    def test_multiple_missing_fields_each_get_a_refusal(self) -> None:
        findings = rg.evaluate_compatibility_exception(
            complete_exception(reason="", telemetry_key=""))
        self.assertEqual(sorted(f.reason_code for f in findings),
                         ["missing_reason", "missing_telemetry_key"])

    def test_an_unidentifiable_exception_is_malformed(self) -> None:
        with self.assertRaises(rg.RepairGateError) as ctx:
            complete_exception(exception_id=" ")
        self.assertEqual(ctx.exception.code, "missing_exception_id")


# ==========================================================================
# 16.6 T7 - an expired compatibility exception BLOCKS acceptance
# ==========================================================================


class T7ExpiryTests(unittest.TestCase):
    def test_an_iso_deadline_compares_against_the_injected_now(self) -> None:
        exc = complete_exception(removal_deadline="2026-10-01T00:00:00+00:00")
        self.assertFalse(rg.compatibility_expired(
            exc, now_utc="2026-09-30T23:59:59+00:00"))
        self.assertTrue(rg.compatibility_expired(
            exc, now_utc="2026-10-01T00:00:00+00:00"))

    def test_a_milestone_deadline_consumes_the_injected_fact(self) -> None:
        exc = complete_exception(removal_deadline="M4-complete")
        self.assertFalse(rg.compatibility_expired(exc, milestone_reached=False))
        self.assertTrue(rg.compatibility_expired(exc, milestone_reached=True))

    def test_a_missing_expiry_fact_fails_closed(self) -> None:
        for exc, kwargs in (
                (complete_exception(), {}),  # ISO deadline, no now_utc
                (complete_exception(removal_deadline="M4-complete"), {})):
            with self.subTest(deadline=exc.removal_deadline):
                with self.assertRaises(rg.RepairGateError) as ctx:
                    rg.compatibility_expired(exc, **kwargs)
                self.assertEqual(ctx.exception.code, "expiry_fact_missing")

    def test_an_expired_exception_blocks_acceptance(self) -> None:
        gate = rg.evaluate_acceptance(
            [complete_exception()], now_utc="2026-11-01T00:00:00+00:00")
        self.assertTrue(gate.blocked)
        self.assertEqual(gate.expired_exception_ids, ("CE-1",))
        self.assertIn("expiry blocks", gate.detail)

    def test_a_current_exception_does_not_block(self) -> None:
        gate = rg.evaluate_acceptance(
            [complete_exception()], now_utc="2026-09-01T00:00:00+00:00")
        self.assertFalse(gate.blocked)

    def test_an_undecidable_expiry_blocks_fail_closed(self) -> None:
        exc = complete_exception(removal_deadline="M4-complete")
        gate = rg.evaluate_acceptance([exc])  # no milestone fact injected
        self.assertTrue(gate.blocked)
        self.assertIn("CE-1", gate.expired_exception_ids)

    def test_milestone_facts_are_injected_per_exception_id(self) -> None:
        reached = complete_exception(exception_id="CE-done",
                                     removal_deadline="M4-complete")
        pending = complete_exception(exception_id="CE-open",
                                     removal_deadline="M5-complete")
        gate = rg.evaluate_acceptance(
            [reached, pending],
            milestone_reached_by_id={"CE-done": True, "CE-open": False})
        self.assertTrue(gate.blocked)
        self.assertEqual(gate.expired_exception_ids, ("CE-done",))


# ==========================================================================
# 16.6 T8 - unrelated working code is preserved
# ==========================================================================


class T8UnrelatedDeletionTests(unittest.TestCase):
    def test_deleting_unrelated_working_code_is_refused(self) -> None:
        evaluation = rg.evaluate_repair(direct_record(
            unrelated_deletions=("services/api/healthz.py",)))
        self.assertFalse(evaluation.accepted)
        self.assertIn("unrelated_working_code_deleted", evaluation.refusal_codes())

    def test_a_fix_with_no_unrelated_deletion_passes(self) -> None:
        self.assertTrue(rg.check_no_unrelated_deletion(direct_record()).ok)


# ==========================================================================
# 16.6 T9 - the closed R078 checkpoint-question set + disposition
# ==========================================================================


class T9CheckpointTests(unittest.TestCase):
    def test_the_question_set_is_the_closed_r078_list(self) -> None:
        self.assertEqual(rg.CHECKPOINT_QUESTIONS, (
            "root_cause", "old_logic_removed_or_covered", "one_authoritative_path",
            "failing_if_removed_test", "wrapper_justification",
            "retained_behavior_removal_plan"))

    def test_each_missing_question_refuses_mechanically(self) -> None:
        for key in rg.CHECKPOINT_QUESTIONS:
            answers = complete_answers()
            answers.pop(key)
            with self.subTest(missing=key):
                verdict = rg.evaluate_checkpoint_answers(answers)
                self.assertEqual(verdict.outcome, rg.CHECKPOINT_REFUSED)
                self.assertEqual(verdict.missing_questions, (key,))

    def test_a_blank_answer_counts_as_missing(self) -> None:
        verdict = rg.evaluate_checkpoint_answers(complete_answers(root_cause="   "))
        self.assertEqual(verdict.missing_questions, ("root_cause",))

    def test_an_unknown_question_key_is_refused(self) -> None:
        verdict = rg.evaluate_checkpoint_answers(
            complete_answers(own_invented_question="yes"))
        self.assertEqual(verdict.outcome, rg.CHECKPOINT_REFUSED)
        self.assertEqual(verdict.unknown_questions, ("own_invented_question",))

    def test_complete_answers_yield_the_typed_complete_outcome(self) -> None:
        verdict = rg.evaluate_checkpoint_answers(complete_answers())
        self.assertTrue(verdict.complete)
        self.assertEqual(verdict.outcome, rg.CHECKPOINT_ANSWERS_COMPLETE)

    def test_complete_answers_never_auto_accept(self) -> None:
        verdict = rg.evaluate_checkpoint_answers(complete_answers())
        disposition, detail = rg.repair_gate_disposition(verdict, None)
        self.assertEqual(disposition, rg.DISPOSITION_REVIEW_REQUIRED)
        self.assertIn("never acceptance", detail)

    def test_an_independent_pass_accepts_and_fail_rejects(self) -> None:
        verdict = rg.evaluate_checkpoint_answers(complete_answers())
        self.assertEqual(rg.repair_gate_disposition(verdict, {"verdict": "PASS"})[0],
                         rg.DISPOSITION_ACCEPTED_BY_REVIEW)
        for bad in ("FAIL", "BLOCKED"):
            self.assertEqual(rg.repair_gate_disposition(verdict, {"verdict": bad})[0],
                             rg.DISPOSITION_REJECTED)

    def test_an_unrecognized_verdict_fails_closed_to_review_required(self) -> None:
        verdict = rg.evaluate_checkpoint_answers(complete_answers())
        self.assertEqual(rg.repair_gate_disposition(verdict, {"verdict": "MAYBE"})[0],
                         rg.DISPOSITION_REVIEW_REQUIRED)

    def test_incomplete_answers_reject_even_with_a_pass_verdict(self) -> None:
        verdict = rg.evaluate_checkpoint_answers({})
        disposition, _ = rg.repair_gate_disposition(verdict, {"verdict": "PASS"})
        self.assertEqual(disposition, rg.DISPOSITION_REJECTED)


# ==========================================================================
# Structural - closed vocabularies fail closed at construction
# ==========================================================================


class RecordShapeTests(unittest.TestCase):
    def test_an_unknown_repair_mode_is_malformed(self) -> None:
        with self.assertRaises(rg.RepairGateError) as ctx:
            direct_record(mode="hotfix")
        self.assertEqual(ctx.exception.code, "unknown_repair_mode")

    def test_an_unknown_layer_kind_is_malformed(self) -> None:
        with self.assertRaises(rg.RepairGateError) as ctx:
            rg.AddedLayer("shim", around_known_bad_path=True)
        self.assertEqual(ctx.exception.code, "unknown_layer_kind")

    def test_an_unknown_evidence_tool_is_malformed(self) -> None:
        with self.assertRaises(rg.RepairGateError) as ctx:
            rg.UnreachabilityEvidence("intuition", "q", "f")
        self.assertEqual(ctx.exception.code, "unknown_evidence_tool")

    def test_blank_evidence_proves_nothing(self) -> None:
        with self.assertRaises(rg.RepairGateError) as ctx:
            rg.UnreachabilityEvidence("search", "  ", "finding")
        self.assertEqual(ctx.exception.code, "empty_evidence")

    def test_a_record_without_identity_is_malformed(self) -> None:
        with self.assertRaises(rg.RepairGateError):
            direct_record(task_id="")

    def test_the_record_digest_binds_content(self) -> None:
        a, b = direct_record(), direct_record(root_cause="a different cause")
        self.assertEqual(a.record_digest(), direct_record().record_digest())
        self.assertNotEqual(a.record_digest(), b.record_digest())


# ==========================================================================
# 16.8 E6 (gap case) - a duplicate PR create is idempotent
# ==========================================================================


class _PrRunner:
    """A minimal recording runner: only the PR-create surface is needed here."""

    def __init__(self) -> None:
        self.prs: list[str] = []

    def create_pull_request(self, *, task_id: str, head: str, base: str,
                            title: str) -> str:
        ref = f"pr/{len(self.prs) + 1}"
        self.prs.append(ref)
        return ref


class E6DuplicatePrCreateTests(unittest.TestCase):
    def test_a_duplicate_pr_create_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            journal = DurableJournal(pathlib.Path(tmp) / "j.sqlite3").open()
            try:
                flow = gf.GitHubFlow(gf.shadow_effects_journal(journal),
                                     _PrRunner(), task_id=TASK)
                first = flow.create_pull_request(
                    head="task/M0-T095", base="main", title=TASK)
                again = flow.create_pull_request(
                    head="task/M0-T095", base="main", title=TASK)
                self.assertTrue(first.performed)
                self.assertFalse(again.performed)
                self.assertEqual(again.reason_code, "already_created")
                self.assertEqual(again.resulting_state, first.resulting_state)
                self.assertEqual(len(flow.runner.prs), 1,
                                 "the second create must not reach the runner")
            finally:
                journal.close()


# ==========================================================================
# 16.8 E7 (gap case) - an identity change invalidates the prior review
# ==========================================================================


class E7ReviewValidityTests(unittest.TestCase):
    def test_an_identity_change_invalidates_the_prior_review(self) -> None:
        validity = rg.review_still_valid(review_identity=IDENTITY_A,
                                         live_identity=IDENTITY_B)
        self.assertFalse(validity.valid)
        self.assertEqual(validity.reason_code, "identity_changed_re_review_required")

    def test_an_unchanged_identity_keeps_the_review_valid(self) -> None:
        validity = rg.review_still_valid(review_identity=IDENTITY_A,
                                         live_identity=IDENTITY_A)
        self.assertTrue(validity.valid)

    def test_a_blank_identity_fails_closed(self) -> None:
        for review, live in (("", IDENTITY_A), (IDENTITY_A, " "), ("", "")):
            with self.subTest(review=review, live=live):
                validity = rg.review_still_valid(review_identity=review,
                                                 live_identity=live)
                self.assertFalse(validity.valid)
                self.assertEqual(validity.reason_code, "identity_unknown")


# ==========================================================================
# 16.8 E10 - a pre-existing PR is never merged without owner authority
# ==========================================================================


class E10PreExistingPrTests(unittest.TestCase):
    def test_a_pre_existing_pr_carries_no_actions(self) -> None:
        classification = rg.classify_pr(rg.PRSnapshot(
            number=99, opened_by_task_id="M5-T002", current_task_id=TASK))
        self.assertEqual(classification.pr_class, rg.PR_CLASS_PRE_EXISTING)
        self.assertEqual(classification.allowed_actions, ())
        self.assertIn("owner authorization", classification.detail)

    def test_pr_241_is_classified_as_deliberately_unmerged(self) -> None:
        classification = rg.classify_pr(rg.PRSnapshot(
            number=241, opened_by_task_id="M5-T002", current_task_id=TASK,
            owner_hold=True))
        self.assertEqual(classification.pr_class, rg.PR_CLASS_EXPECTED_OPEN)
        self.assertEqual(classification.allowed_actions, ())

    def test_the_existing_flow_refuses_an_unauthorized_merge(self) -> None:
        # Cross-proof against the EXISTING S5.5 gate: a pre-existing PR is not
        # task-authorized, so github_flow refuses the merge independently of the
        # classification layer (defense in depth with test_agent_supervisor_
        # github_flow.py::test_merge_refuses_when_not_authorized).
        evaluation = gf.evaluate_merge(green_merge_request(task_authorized=False))
        self.assertFalse(evaluation.eligible)
        self.assertIn("not_authorized_or_dependency_invalid",
                      evaluation.refusal_codes())


# ==========================================================================
# 16.8 E11 - the closed PR classification vocabulary; snapshots are effect-free
# ==========================================================================


class E11ClassificationTests(unittest.TestCase):
    def test_the_pr_classification_vocabulary_is_closed(self) -> None:
        self.assertEqual(rg.PR_CLASSES, (
            rg.PR_CLASS_TASK, rg.PR_CLASS_PRE_EXISTING,
            rg.PR_CLASS_EXPECTED_OPEN, rg.PR_CLASS_STALE))

    def test_an_owner_hold_wins_over_task_ownership(self) -> None:
        classification = rg.classify_pr(rg.PRSnapshot(
            number=7, opened_by_task_id=TASK, current_task_id=TASK, owner_hold=True))
        self.assertEqual(classification.pr_class, rg.PR_CLASS_EXPECTED_OPEN)
        self.assertEqual(classification.allowed_actions, ())

    def test_the_current_tasks_pr_routes_only_through_github_flow(self) -> None:
        classification = rg.classify_pr(rg.PRSnapshot(
            number=8, opened_by_task_id=TASK, current_task_id=TASK))
        self.assertEqual(classification.pr_class, rg.PR_CLASS_TASK)
        self.assertEqual(classification.allowed_actions,
                         (rg.ACTION_EVALUATE_VIA_GITHUB_FLOW,))

    def test_a_long_inactive_foreign_pr_is_flagged_stale_not_actioned(self) -> None:
        classification = rg.classify_pr(rg.PRSnapshot(
            number=9, opened_by_task_id="M2-T001", current_task_id=TASK,
            days_since_update=45))
        self.assertEqual(classification.pr_class, rg.PR_CLASS_STALE)
        self.assertEqual(classification.allowed_actions, ())
        self.assertIn("never silently closed", classification.detail)

    def test_an_unknown_age_never_makes_a_pr_stale(self) -> None:
        classification = rg.classify_pr(rg.PRSnapshot(
            number=10, opened_by_task_id="M2-T001", current_task_id=TASK,
            days_since_update=None))
        self.assertEqual(classification.pr_class, rg.PR_CLASS_PRE_EXISTING)

    def test_every_classification_is_effect_free(self) -> None:
        snapshots = (
            rg.PRSnapshot(number=1, opened_by_task_id=TASK, current_task_id=TASK),
            rg.PRSnapshot(number=2, opened_by_task_id="", current_task_id=TASK),
            rg.PRSnapshot(number=3, opened_by_task_id="x", current_task_id=TASK,
                          owner_hold=True),
            rg.PRSnapshot(number=4, opened_by_task_id="x", current_task_id=TASK,
                          days_since_update=400))
        for snapshot in snapshots:
            with self.subTest(number=snapshot.number):
                self.assertTrue(rg.classify_pr(snapshot).effect_free)

    def test_a_malformed_snapshot_is_refused(self) -> None:
        with self.assertRaises(rg.RepairGateError):
            rg.PRSnapshot(number=0, opened_by_task_id="", current_task_id=TASK)
        with self.assertRaises(rg.RepairGateError):
            rg.PRSnapshot(number=5, opened_by_task_id="", current_task_id=" ")


# ==========================================================================
# 16.8 E13 (gap case) - the supervisor-freeze citation fixture
# ==========================================================================


class E13FreezeCitationTests(unittest.TestCase):
    SUPERVISOR_PATH = "tools/agent_supervisor/repair_gate.py"

    def test_an_uncited_supervisor_change_record_is_rejected(self) -> None:
        findings = rg.validate_freeze_citation(rg.SupervisorChangeRecord(
            touched_paths=(self.SUPERVISOR_PATH,),
            packet_citation="a change we felt like making",
            commit_message="improve the supervisor"))
        codes = sorted(f.reason_code for f in findings)
        self.assertEqual(codes, ["missing_freeze_citation_commit",
                                 "missing_freeze_citation_packet"])
        self.assertTrue(all(not f.ok for f in findings))

    def test_a_packet_only_citation_still_fails_the_commit_side(self) -> None:
        findings = rg.validate_freeze_citation(rg.SupervisorChangeRecord(
            touched_paths=(self.SUPERVISOR_PATH,),
            packet_citation="qualifying evidence: D-024-R105",
            commit_message="improve the supervisor"))
        self.assertEqual([f.reason_code for f in findings],
                         ["missing_freeze_citation_commit"])

    def test_a_fully_cited_record_passes(self) -> None:
        findings = rg.validate_freeze_citation(rg.SupervisorChangeRecord(
            touched_paths=(self.SUPERVISOR_PATH,),
            packet_citation="qualifying evidence: D-024-R105",
            commit_message="M0-T095 repair gate (D-024-R105)"))
        self.assertEqual([f.reason_code for f in findings],
                         ["freeze_citation_present"])
        self.assertTrue(findings[0].ok)

    def test_a_non_supervisor_change_owes_no_citation(self) -> None:
        findings = rg.validate_freeze_citation(rg.SupervisorChangeRecord(
            touched_paths=("services/api/app.py",)))
        self.assertEqual([f.reason_code for f in findings], ["no_supervisor_path"])

    def test_supervisor_paths_are_recognized_with_backslashes_too(self) -> None:
        self.assertTrue(rg.touches_supervisor(
            (r"tools\agent_supervisor\loop.py",)))
        self.assertFalse(rg.touches_supervisor(("docs/readme.md",)))


# ==========================================================================
# 16.8 E14 (gap case) - one consolidated correction round, no drip-feeding
# ==========================================================================


class E14ConsolidatedRoundTests(unittest.TestCase):
    def test_a_consolidated_single_round_is_the_valid_shape(self) -> None:
        result = rg.evaluate_correction_round(
            review_identity=IDENTITY_A,
            finding_ids=("G3-1", "G4-2", "G5-1"),
            correction_identities=(IDENTITY_B, IDENTITY_B, IDENTITY_B))
        self.assertTrue(result.ok)
        self.assertEqual(result.reason_code, "consolidated_round")
        self.assertEqual(result.re_review_identity, IDENTITY_B)
        self.assertIn("re-review", result.detail)

    def test_drip_feeding_per_finding_identity_churn_is_refused(self) -> None:
        result = rg.evaluate_correction_round(
            review_identity=IDENTITY_A,
            finding_ids=("G3-1", "G4-2"),
            correction_identities=("c" * 12, "d" * 12))
        self.assertFalse(result.ok)
        self.assertEqual(result.reason_code, "drip_feeding")

    def test_a_round_that_does_not_move_the_identity_is_refused(self) -> None:
        result = rg.evaluate_correction_round(
            review_identity=IDENTITY_A, finding_ids=("G3-1",),
            correction_identities=(IDENTITY_A,))
        self.assertFalse(result.ok)
        self.assertEqual(result.reason_code, "correction_did_not_move_identity")

    def test_unaddressed_findings_leave_the_round_incomplete(self) -> None:
        result = rg.evaluate_correction_round(
            review_identity=IDENTITY_A, finding_ids=("G3-1",),
            correction_identities=())
        self.assertFalse(result.ok)
        self.assertEqual(result.reason_code, "findings_unaddressed")

    def test_no_findings_needs_no_round(self) -> None:
        result = rg.evaluate_correction_round(
            review_identity=IDENTITY_A, finding_ids=(), correction_identities=())
        self.assertTrue(result.ok)
        self.assertEqual(result.re_review_identity, IDENTITY_A)

    def test_a_blank_review_identity_fails_closed(self) -> None:
        result = rg.evaluate_correction_round(
            review_identity=" ", finding_ids=("G3-1",),
            correction_identities=(IDENTITY_B,))
        self.assertFalse(result.ok)
        self.assertEqual(result.reason_code, "identity_unknown")


# ==========================================================================
# Thin review-packet wiring (record-only)
# ==========================================================================


class CheckpointSectionWiringTests(unittest.TestCase):
    def section(self, **answer_overrides) -> dict:
        record = direct_record()
        answers = complete_answers(**answer_overrides)
        return rg.checkpoint_section(
            record=record, answers=answers,
            evaluation=rg.evaluate_repair(record),
            checkpoint=rg.evaluate_checkpoint_answers(answers))

    def test_the_section_is_bounded_serializable_and_digest_bound(self) -> None:
        section = self.section()
        canonical_json(section)  # must serialize deterministically
        self.assertEqual(section["record_digest"], direct_record().record_digest())
        self.assertEqual(section["checkpoint_outcome"],
                         rg.CHECKPOINT_ANSWERS_COMPLETE)
        self.assertEqual(sorted(section["answers"]),
                         sorted(rg.CHECKPOINT_QUESTIONS))
        self.assertTrue(section["repair_accepted"])

    def test_answers_are_routed_through_redaction(self) -> None:
        secret = "ghp_" + "E" * 36
        section = self.section(root_cause=f"the token {secret} leaked")
        self.assertNotIn(secret, canonical_json(section).decode("utf-8"))
        self.assertIn("[REDACTED", section["answers"]["root_cause"])

    def test_the_section_key_collides_with_no_prohibited_marker(self) -> None:
        for names in PROHIBITED_MARKER_KEYS.values():
            self.assertNotIn(rg.REPAIR_GATE_SECTION_KEY.lower(), names)

    def test_the_content_guard_admits_a_packet_carrying_the_section(self) -> None:
        result = guard_packet(
            {"sections": {rg.REPAIR_GATE_SECTION_KEY: self.section()}},
            current_task_id=TASK)
        self.assertTrue(result.ok, [f.to_dict() for f in result.findings])

    def test_build_packet_carries_the_section_to_review(self) -> None:
        result = ev.build_packet(
            run_id="run-1", task_id=TASK, checkpoint_id="cp-1", checkpoint=None,
            extra_sections={rg.REPAIR_GATE_SECTION_KEY: self.section()})
        self.assertTrue(result.ok, result.reason)
        packet = result.packet
        self.assertIn(rg.REPAIR_GATE_SECTION_KEY, packet.sections)
        self.assertTrue(packet.packet_digest)
        self.assertEqual(
            packet.sections[rg.REPAIR_GATE_SECTION_KEY]["record_digest"],
            direct_record().record_digest())


# ==========================================================================
# Meta - the 16.6 and 16.8 registers (prove-first mapping tables)
# ==========================================================================


def _test_names_in(filename: str) -> set[str]:
    source = (HERE / filename).read_text(encoding="utf-8")
    return set(re.findall(r"def (test_\w+)", source))


class Section166RegisterTests(unittest.TestCase):
    #: 16.6 case -> a test-name fragment in THIS file that proves it (R112).
    SECTION_16_6: dict[str, str] = {
        "T1_wrapper_around_defective_path_rejected":
            "an_unjustified_layer_around_a_known_bad_path_is_rejected",
        "T2_direct_repair_accepted_without_forced_rewrite":
            "a_direct_root_cause_repair_is_accepted_without_a_forced_rewrite",
        "T3_bounded_replacement_removes_old_reachable_logic":
            "replacement_without_each_removal_proof_is_rejected",
        "T4_search_graph_catches_stale_callers":
            "reachable_stale_callers_refuse_one_authoritative_path",
        "T5_regression_test_fails_if_fix_removed":
            "an_unbound_regression_test_is_rejected",
        "T6_compatibility_exception_requires_every_field":
            "each_missing_field_produces_its_own_typed_refusal",
        "T7_expired_compatibility_path_blocks_acceptance":
            "an_expired_exception_blocks_acceptance",
        "T8_unrelated_working_code_preserved":
            "deleting_unrelated_working_code_is_refused",
        "T9_checkpoint_questions_answered_at_review":
            "each_missing_question_refuses_mechanically",
    }

    def test_every_16_6_case_has_a_named_test_here(self) -> None:
        names = _test_names_in(pathlib.Path(__file__).name)
        for case, fragment in self.SECTION_16_6.items():
            self.assertTrue(any(fragment in name for name in names),
                            f"no test covers 16.6 case {case!r}")

    def test_the_16_6_register_lists_all_nine_cases(self) -> None:
        self.assertEqual(len(self.SECTION_16_6), 9)


class Section168RegisterTests(unittest.TestCase):
    """The R018 prove-first register: every named 16.8 case -> (file, test).

    Existing proofs are CITED (their pack already runs in CI); only the gap cases
    point at this file. The register test verifies each citation against the
    cited file's actual source, so a renamed or deleted proof breaks the build.
    """

    THIS = "test_agent_supervisor_repair_gate.py"
    FLOW = "test_agent_supervisor_github_flow.py"
    POLICY = "test_agent_supervisor_policy.py"

    #: 16.8 case -> ((file, test-name fragment), ...) - every listed proof must exist.
    SECTION_16_8: dict[str, tuple[tuple[str, str], ...]] = {
        "E1_branch_base_head_identity": (
            (FLOW, "a_push_to_the_wrong_task_branch_is_denied"),
            (FLOW, "a_remote_identity_mismatch_is_denied"),
            (FLOW, "pr_creation_works_and_is_journaled")),
        "E2_protected_default_branch_write_rejected": (
            (FLOW, "direct_main_push_is_hard_denied"),
            (FLOW, "force_push_is_hard_denied"),
            (POLICY, "push_to_main_and_force_push_are_denied_and_continue")),
        "E3_overlapping_worktree_writer_rejected": (
            ("test_agent_supervisor_bounded_contracts.py",
             "overlapping_write_scopes_cannot_both_obtain_leases"),
            ("test_agent_supervisor_runtime_supervision.py",
             "parent_rotation_never_creates_overlapping_writers")),
        "E4_commit_push_after_required_checks": (
            (POLICY, "authority_gating"),
            (FLOW, "merge_refuses_on_a_failing_required_check")),
        "E5_remote_success_local_timeout_reconciled": (
            (FLOW, "crash_mid_push_leaves_a_pending_effect_reconciled_not_retried"),
            (FLOW, "reconciling_a_proven_merge_confirms_it_without_duplication"),
            (FLOW, "a_second_merge_attempt_on_a_pending_effect_does_not_re_fire")),
        "E6_duplicate_pr_comment_update_idempotent": (
            (FLOW, "a_confirmed_push_is_not_pushed_again"),
            (FLOW, "a_repeated_begin_after_a_crash_reuses_the_same_action_id"),
            (THIS, "a_duplicate_pr_create_is_idempotent")),
        "E7_frozen_identity_change_invalidates_review": (
            (THIS, "an_identity_change_invalidates_the_prior_review"),),
        "E8_no_credentials_anywhere": (
            (FLOW, "a_raw_secret_in_findings_is_refused"),
            (FLOW, "condition_logging_is_routed_through_redaction"),
            (POLICY, "a_secret_scan_finding_stops_synchronously")),
        "E9_codex_cannot_stage_commit_push_merge": (
            ("test_agent_supervisor_reviewer.py",
             "only_enumerated_read_only_git_commands_are_allowed"),),
        "E10_pre_existing_prs_never_merged": (
            (FLOW, "merge_refuses_when_not_authorized"),
            (THIS, "a_pre_existing_pr_carries_no_actions"),
            (THIS, "pr_241_is_classified_as_deliberately_unmerged")),
        "E11_held_stale_prs_classified_separately": (
            (THIS, "the_pr_classification_vocabulary_is_closed"),
            (THIS, "a_long_inactive_foreign_pr_is_flagged_stale_not_actioned"),
            (THIS, "every_classification_is_effect_free")),
        "E12_failed_required_checks_block": (
            (FLOW, "merge_refuses_on_a_failing_required_check"),
            (FLOW, "merge_refuses_when_no_required_check_ran")),
        "E13_supervisor_freeze_citation_fixture": (
            (THIS, "an_uncited_supervisor_change_record_is_rejected"),),
        "E14_consolidated_single_correction_round": (
            (THIS, "a_consolidated_single_round_is_the_valid_shape"),
            (THIS, "drip_feeding_per_finding_identity_churn_is_refused")),
    }

    def test_every_16_8_case_maps_to_a_real_named_test(self) -> None:
        names_by_file: dict[str, set[str]] = {}
        for case, proofs in self.SECTION_16_8.items():
            for filename, fragment in proofs:
                if filename not in names_by_file:
                    names_by_file[filename] = _test_names_in(filename)
                self.assertTrue(
                    any(fragment in name for name in names_by_file[filename]),
                    f"16.8 case {case!r} cites {filename}::{fragment}, but no such "
                    f"test exists - the prove-first mapping is stale")

    def test_the_16_8_register_lists_all_fourteen_cases(self) -> None:
        self.assertEqual(len(self.SECTION_16_8), 14)


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
