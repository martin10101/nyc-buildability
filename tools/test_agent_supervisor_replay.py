#!/usr/bin/env python3
"""Replay mode and the historical corpus (D-007 S12, S15 historical replay, S16.8).

The S15 corpus has eight named cases and this file asserts each one BY NAME, so a
case cannot quietly disappear:

    a clean continuation, a review-required correction, a CI failure, a
    stale-SHA/mismatched-review case, an owner-gated stop, M0-T031's accepted
    lifecycle, the B-015 sentinel failure, and the M0-T028 detection-only stop.

It also asserts the three properties that make replay trustworthy at all: it
makes no model call, it writes nothing, and it never rewrites a historical
report. Those are proven from the module source and by pointing the engine at a
read-only copy of the corpus, not by promising.
"""
from __future__ import annotations

import dataclasses
import json
import pathlib
import shutil
import stat
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import replay as rp  # noqa: E402
from tools.agent_supervisor.policy import ZONE_REVIEWER  # noqa: E402

CORPUS = REPO / "tools" / "agent_supervisor" / "replay_corpus"


class ReplayTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.engine = rp.ReplayEngine(repo_root=str(REPO))

    def case(self, case_id: str) -> rp.ReplayCase:
        for candidate in self.engine.load():
            if candidate.case_id == case_id:
                return candidate
        raise AssertionError(f"replay case {case_id!r} is not in the corpus")

    def result(self, case_id: str) -> rp.CaseResult:
        return self.engine.run_case(self.case(case_id))


# --------------------------------------------------------------------------
# The corpus itself
# --------------------------------------------------------------------------


class CorpusTests(ReplayTestBase):
    def test_all_eight_required_cases_are_present(self) -> None:
        present = {case.case_id for case in self.engine.load()}
        self.assertEqual(present, set(rp.REQUIRED_CASE_IDS))
        self.assertEqual(len(rp.REQUIRED_CASE_IDS), 8)

    def test_the_corpus_matches_its_manifest(self) -> None:
        ok, detail = self.engine.check_manifest()
        self.assertTrue(ok, detail)

    def test_an_edited_fixture_is_detected_as_corpus_drift(self) -> None:
        copy = self.tmp / "corpus"
        shutil.copytree(CORPUS, copy)
        target = copy / "clean_continuation.json"
        data = json.loads(target.read_text(encoding="utf-8-sig"))
        data["expected_outcome"] = "halt"
        target.write_text(json.dumps(data), encoding="utf-8")
        engine = rp.ReplayEngine(corpus_dir=copy, repo_root=str(REPO))
        ok, detail = engine.check_manifest()
        self.assertFalse(ok)
        self.assertIn("clean_continuation.json", detail)

    def test_a_removed_fixture_is_detected(self) -> None:
        copy = self.tmp / "corpus"
        shutil.copytree(CORPUS, copy)
        (copy / "ci_failure.json").unlink()
        engine = rp.ReplayEngine(corpus_dir=copy, repo_root=str(REPO))
        ok, detail = engine.check_manifest()
        self.assertFalse(ok)
        self.assertIn("removed=['ci_failure.json']", detail)

    def test_an_added_fixture_is_detected(self) -> None:
        copy = self.tmp / "corpus"
        shutil.copytree(CORPUS, copy)
        (copy / "smuggled.json").write_text(
            json.dumps({"case_id": "smuggled"}), encoding="utf-8")
        engine = rp.ReplayEngine(corpus_dir=copy, repo_root=str(REPO))
        ok, detail = engine.check_manifest()
        self.assertFalse(ok)
        self.assertIn("smuggled.json", detail)

    def test_a_missing_required_case_fails_the_report(self) -> None:
        copy = self.tmp / "corpus"
        shutil.copytree(CORPUS, copy)
        (copy / "b015_sentinel_failure.json").unlink()
        engine = rp.ReplayEngine(corpus_dir=copy, repo_root=str(REPO))
        report = engine.run_all()
        self.assertIn("b015_sentinel_failure", report.missing_required)
        self.assertFalse(report.ok)

    def test_every_case_cites_provenance_that_exists_in_this_checkout(self) -> None:
        self.assertTrue(self.engine.provenance_checkable)
        for case in self.engine.load():
            present, missing = self.engine.verify_provenance(case)
            self.assertEqual(missing, (), f"{case.case_id} cites absent records")
            self.assertTrue(present)

    def test_a_duplicate_case_id_is_refused(self) -> None:
        copy = self.tmp / "corpus"
        shutil.copytree(CORPUS, copy)
        shutil.copyfile(copy / "ci_failure.json", copy / "ci_failure_again.json")
        engine = rp.ReplayEngine(corpus_dir=copy, repo_root=str(REPO))
        with self.assertRaises(rp.ReplayError) as ctx:
            engine.load()
        self.assertEqual(ctx.exception.code, "duplicate_case_id")

    def test_a_case_with_an_unknown_expected_outcome_is_refused(self) -> None:
        with self.assertRaises(rp.ReplayError) as ctx:
            rp.ReplayCase.from_mapping({
                "case_id": "x", "title": "t", "summary": "s", "provenance": [],
                "authority": {}, "checkpoint": {}, "recorded_decision": {},
                "expected_outcome": "probably_fine", "expected_tier": "AUTO",
                "recorded_ledger_outcome": "?"})
        self.assertEqual(ctx.exception.code, "unknown_expected_outcome")

    def test_a_case_with_an_unknown_trust_zone_is_refused(self) -> None:
        with self.assertRaises(rp.ReplayError) as ctx:
            rp.ReplayCase.from_mapping({
                "case_id": "x", "title": "t", "summary": "s", "provenance": [],
                "authority": {}, "checkpoint": {}, "recorded_decision": {},
                "proposed_actions": [{"kind": "read", "origin_zone": "TRUSTED"}],
                "expected_outcome": "continue", "expected_tier": "AUTO",
                "recorded_ledger_outcome": "?"})
        self.assertEqual(ctx.exception.code, "unknown_trust_zone")

    def test_a_case_missing_a_required_field_is_refused_not_skipped(self) -> None:
        with self.assertRaises(rp.ReplayError) as ctx:
            rp.ReplayCase.from_mapping({"case_id": "x"})
        self.assertEqual(ctx.exception.code, "case_missing_fields")

    def test_an_unknown_action_field_is_refused(self) -> None:
        with self.assertRaises(rp.ReplayError) as ctx:
            rp._action_from_mapping({"kind": "read", "confidence": 0.9})
        self.assertEqual(ctx.exception.code, "unknown_action_field")


# --------------------------------------------------------------------------
# S16.8: the corpus reproduces
# --------------------------------------------------------------------------


class CorpusReproductionTests(ReplayTestBase):
    def test_the_whole_corpus_reproduces(self) -> None:
        report = self.engine.run_all()
        self.assertTrue(report.ok,
                        f"mismatched: {[r.case_id for r in report.mismatches]}")
        self.assertEqual(len(report.results), 8)
        self.assertTrue(report.provenance_checked)
        self.assertTrue(report.provenance_ok)

    def test_clean_continuation_continues_with_no_owner_touch(self) -> None:
        result = self.result("clean_continuation")
        self.assertEqual(result.actual_outcome, rp.OUTCOME_CONTINUE)
        self.assertEqual(result.actual_tier, "AUTO")
        self.assertTrue(result.forwarded)
        self.assertIn("in_scope_file_write", result.reason_codes)
        self.assertIn("documented_test_command", result.reason_codes)

    def test_review_required_correction_revises(self) -> None:
        result = self.result("review_required_correction")
        self.assertEqual(result.actual_outcome, rp.OUTCOME_REVISE)
        self.assertTrue(result.forwarded)
        self.assertNotEqual(result.actual_outcome, rp.OUTCOME_STAGE_COMPLETE)

    def test_ci_failure_never_reports_the_stage_complete(self) -> None:
        result = self.result("ci_failure")
        self.assertEqual(result.actual_outcome, rp.OUTCOME_REVISE)
        self.assertNotEqual(result.actual_outcome, rp.OUTCOME_STAGE_COMPLETE)
        # The checkpoint claimed completion; the deterministic evidence won.
        case = self.case("ci_failure")
        self.assertEqual(case.checkpoint["status"], "UNIT_COMPLETE")
        self.assertEqual(case.checkpoint["ci"]["conclusion"], "failure")

    def test_stale_sha_stops_and_never_merges(self) -> None:
        result = self.result("stale_sha_mismatched_review")
        self.assertEqual(result.actual_outcome, rp.OUTCOME_STOP_FOR_OWNER)
        self.assertFalse(result.forwarded)
        self.assertIn("owner_gate:merge", result.reason_codes)

    def test_owner_gated_stop_refuses_the_out_of_scope_write_and_stops(self) -> None:
        result = self.result("owner_gated_stop")
        self.assertEqual(result.actual_outcome, rp.OUTCOME_STOP_FOR_OWNER)
        self.assertEqual(result.actual_tier, "HARD_DENY")
        self.assertIn("protected_path_mutation", result.reason_codes)

    def test_m0_t031_reaches_stage_complete_but_never_accepts(self) -> None:
        result = self.result("m0_t031_accepted_lifecycle")
        self.assertEqual(result.actual_outcome, rp.OUTCOME_STAGE_COMPLETE)
        self.assertFalse(result.forwarded)
        self.assertIn("owner_gate:task_acceptance", result.reason_codes)
        self.assertEqual(result.actual_tier, "ASK",
                         "COMPLETE reports the STAGE done; acceptance stays an owner gate")

    def test_b015_sentinel_failure_is_a_halt_not_a_shrug(self) -> None:
        result = self.result("b015_sentinel_failure")
        self.assertEqual(result.actual_outcome, rp.OUTCOME_HALT)
        self.assertEqual(result.actual_tier, "HARD_DENY")
        self.assertIn("reviewer_write_attempt", result.reason_codes)
        self.assertFalse(result.forwarded)

    def test_b015_case_really_is_a_reviewer_zone_write(self) -> None:
        case = self.case("b015_sentinel_failure")
        zones = {a.get("origin_zone") for a in case.proposed_actions}
        self.assertEqual(zones, {ZONE_REVIEWER})

    def test_m0_t028_detection_only_stops_for_the_owner(self) -> None:
        result = self.result("m0_t028_detection_only_stop")
        self.assertEqual(result.actual_outcome, rp.OUTCOME_STOP_FOR_OWNER)
        self.assertEqual(result.actual_tier, "ASK")
        self.assertFalse(result.forwarded)

    def test_the_stopping_cases_forward_nothing(self) -> None:
        for case_id in ("stale_sha_mismatched_review", "owner_gated_stop",
                        "m0_t031_accepted_lifecycle", "b015_sentinel_failure",
                        "m0_t028_detection_only_stop"):
            self.assertFalse(self.result(case_id).forwarded, case_id)

    def test_replay_is_deterministic_across_runs(self) -> None:
        first = self.engine.run_all().to_dict()
        second = rp.ReplayEngine(repo_root=str(REPO)).run_all().to_dict()
        self.assertEqual(first, second)

    def test_a_softened_expectation_would_be_caught(self) -> None:
        """Mutation check: weakening B-015 to a continue must FAIL the corpus."""
        copy = self.tmp / "corpus"
        shutil.copytree(CORPUS, copy)
        target = copy / "b015_sentinel_failure.json"
        data = json.loads(target.read_text(encoding="utf-8-sig"))
        data["expected_outcome"] = "continue"
        data["expected_tier"] = "AUTO"
        target.write_text(json.dumps(data), encoding="utf-8")
        engine = rp.ReplayEngine(corpus_dir=copy, repo_root=str(REPO))
        report = engine.run_all()
        self.assertFalse(report.ok)
        self.assertEqual([r.case_id for r in report.mismatches],
                         ["b015_sentinel_failure"])


# --------------------------------------------------------------------------
# No model calls, no writes
# --------------------------------------------------------------------------


class InertnessTests(ReplayTestBase):
    def test_the_module_has_no_execution_surface(self) -> None:
        rp.assert_no_execution()   # raises on failure
        source = (REPO / "tools" / "agent_supervisor" / "replay.py").read_text(
            encoding="utf-8")
        for name in rp.EXECUTION_SURFACE_NAMES:
            self.assertEqual(source.count(name), 1,
                             f"{name!r} appears outside the constant tuple")

    def test_the_module_has_no_write_surface(self) -> None:
        rp.assert_no_writes()
        source = (REPO / "tools" / "agent_supervisor" / "replay.py").read_text(
            encoding="utf-8")
        for name in rp.WRITE_SURFACE_NAMES:
            self.assertEqual(source.count(name), 1,
                             f"{name!r} appears outside the constant tuple")

    def test_replay_imports_no_provider_adapter(self) -> None:
        source = (REPO / "tools" / "agent_supervisor" / "replay.py").read_text(
            encoding="utf-8")
        imports = [line for line in source.splitlines()
                   if line.startswith("from .") or line.startswith("import ")]
        for line in imports:
            self.assertNotIn("claude_runner", line)
            self.assertNotIn("process", line)
            self.assertNotIn("preflight", line)

    def test_a_write_under_project_control_is_refused(self) -> None:
        for relative in ("project-control/reports/M0-T031-dcv.md",
                         "project-control/tasks/M0-T031.json",
                         ".github/workflows/ci.yml",
                         ".claude/settings.json"):
            with self.assertRaises(rp.ReplayError) as ctx:
                rp.assert_never_writes(REPO / relative, repo_root=REPO)
            self.assertEqual(ctx.exception.code, "replay_never_writes")

    def test_a_write_outside_the_forbidden_roots_is_allowed_through(self) -> None:
        rp.assert_never_writes(self.tmp / "scratch.txt", repo_root=REPO)
        rp.assert_never_writes(REPO / "tools" / "scratch.txt", repo_root=REPO)

    def test_a_full_run_over_a_READ_ONLY_corpus_succeeds(self) -> None:
        """The strongest available proof: make the corpus unwritable and run."""
        copy = self.tmp / "readonly_corpus"
        shutil.copytree(CORPUS, copy)
        for path in copy.iterdir():
            path.chmod(stat.S_IREAD)
        self.addCleanup(lambda: [p.chmod(stat.S_IWRITE | stat.S_IREAD)
                                 for p in copy.iterdir()])
        report = rp.ReplayEngine(corpus_dir=copy, repo_root=str(REPO)).run_all()
        self.assertTrue(report.ok)

    def test_running_the_corpus_leaves_project_control_byte_identical(self) -> None:
        cited = sorted({c for case in self.engine.load() for c in case.provenance})
        before = {c: (REPO / c).read_bytes() for c in cited}
        self.engine.run_all()
        after = {c: (REPO / c).read_bytes() for c in cited}
        self.assertEqual(before, after,
                         "replay modified a historical record it cited")

    def test_the_report_declares_zero_model_calls_and_zero_writes(self) -> None:
        payload = self.engine.run_all().to_dict()
        self.assertEqual(payload["model_calls"], 0)
        self.assertEqual(payload["writes_to_project_control"], 0)


# --------------------------------------------------------------------------
# Failure modes
# --------------------------------------------------------------------------


class CaseFailureTests(ReplayTestBase):
    def test_a_checkpoint_that_no_longer_validates_is_reported_not_ignored(self) -> None:
        case = self.case("clean_continuation")
        broken = dict(case.checkpoint)
        broken["status"] = "PROBABLY_FINE"
        mutated = dataclasses.replace(case, checkpoint=broken)
        result = self.engine.run_case(mutated)
        self.assertIn("checkpoint_invalid", result.reason_codes)
        self.assertFalse(result.matched)

    def test_a_decision_correlated_to_the_wrong_checkpoint_is_caught(self) -> None:
        case = self.case("clean_continuation")
        wrong = dict(case.recorded_decision)
        wrong["reviewed_checkpoint_id"] = "cp-999"
        mutated = dataclasses.replace(case, recorded_decision=wrong)
        result = self.engine.run_case(mutated)
        self.assertIn("decision_invalid", result.reason_codes)
        self.assertIn("does not validate", result.detail)

    def test_a_missing_corpus_directory_raises(self) -> None:
        engine = rp.ReplayEngine(corpus_dir=self.tmp / "nope", repo_root=str(REPO))
        with self.assertRaises(rp.ReplayError) as ctx:
            engine.load()
        self.assertEqual(ctx.exception.code, "corpus_missing")

    def test_a_non_json_case_file_raises_by_name(self) -> None:
        copy = self.tmp / "corpus"
        copy.mkdir()
        (copy / "broken.json").write_text("{not json", encoding="utf-8")
        engine = rp.ReplayEngine(corpus_dir=copy, repo_root=str(REPO))
        with self.assertRaises(rp.ReplayError) as ctx:
            engine.load()
        self.assertEqual(ctx.exception.code, "case_not_json")

    def test_running_one_case_by_id_works(self) -> None:
        report = self.engine.run_all(only=["b015_sentinel_failure"])
        self.assertEqual(len(report.results), 1)
        self.assertEqual(report.results[0].case_id, "b015_sentinel_failure")


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
