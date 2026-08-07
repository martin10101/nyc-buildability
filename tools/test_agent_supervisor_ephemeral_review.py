#!/usr/bin/env python3
"""Ephemeral-review loop tests: AS-1..AS-5, AD-027/083/084/087/088 (M0-T042).

The Codex executable is FAKE throughout - a local Python script that writes a
decision file and emits a `--json` usage event. No network, no tokens, no real
review.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import textwrap
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import codex_reviewer as rv  # noqa: E402
from tools.agent_supervisor import ephemeral_review as er  # noqa: E402
from tools.agent_supervisor import evidence as ev  # noqa: E402
from tools.agent_supervisor import review_cadence as rc  # noqa: E402
from tools.agent_supervisor import review_packet as rp  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.config import (  # noqa: E402
    load_controller_config, load_model_selection)
from tools.agent_supervisor.models import USAGE_UNKNOWN  # noqa: E402

CONFIG_TOML = """
[codex]
allowed_models = ["codex-primary", "codex-fallback"]
[claude]
allowed_models = ["claude-worker"]
[controller]
default_mode = "shadow"
"""
SELECTION_TOML = """
[codex]
review_model = "codex-primary"
advisory_model = "codex-fallback"
fallback_models = ["codex-fallback"]
[claude]
model = "claude-worker"
fallback_models = []
"""

FAKE_CODEX = textwrap.dedent('''
    """FAKE codex CLI for ephemeral-review tests. Read-only, no network."""
    import json, os, pathlib, sys
    ARGV = sys.argv[1:]
    def flag(name):
        return ARGV[ARGV.index(name) + 1] if name in ARGV else ""
    raw = sys.stdin.read()
    try:
        packet = json.loads(raw or "{}")
    except Exception:
        packet = {}
    output_path = flag("--output-last-message")
    model = flag("-m")
    task_id = str(packet.get("task_id", ""))
    checkpoint_id = str(packet.get("checkpoint_id", ""))
    decision = {
        "schema_version": "1.0.0",
        "decision": os.environ.get("FAKE_DECISION", "CONTINUE"),
        "reviewed_task_id": task_id, "reviewed_checkpoint_id": checkpoint_id,
        "verified_repo_head": "b" * 40, "verified_origin_main": "c" * 40,
        "model_used": model, "next_claude_prompt": "proceed with the next unit",
        "verified_facts": [{"packet_bytes": len(raw)}],
        "evidence_refs": [
            {"path": "project-control/tasks/" + task_id + ".json"},
            {"path": "services/api/app/rules/engine.py"}],
        "blocking_findings": [], "reason_codes": [], "unverified_claims": [],
        "owner_question": "", "rotation_reason": "",
    }
    pathlib.Path(output_path).write_text(json.dumps(decision), encoding="utf-8")
    sys.stdout.write(json.dumps(
        {"type": "token_count",
         "usage": {"input_tokens": 1200, "output_tokens": 300}}) + "\\n")
''')


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        (self.tmp / "config.toml").write_text(CONFIG_TOML, encoding="utf-8")
        (self.tmp / "model_selection.toml").write_text(SELECTION_TOML, encoding="utf-8")
        self.config = load_controller_config(self.tmp / "config.toml")
        self.selection = load_model_selection(self.tmp / "model_selection.toml")
        self.schema = (REPO / "tools" / "agent_supervisor" / "schemas"
                       / "codex_decision.schema.json")
        self.fake = self.tmp / "fake_codex.py"
        self.fake.write_text(FAKE_CODEX, encoding="utf-8")
        self.audit = AuditLog(self.tmp / "audit.jsonl", fsync=False)

    def reviewer(self):
        script = str(self.fake)
        def runner(argv, **kwargs):
            from tools.agent_supervisor.process import run as real_run
            child_env = dict(kwargs.pop("env", {}) or {})
            child_env.setdefault("PYTHONIOENCODING", "utf-8")
            return real_run([argv[0], script, *argv[1:]], env=child_env, **kwargs)
        return rv.CodexReviewer(
            sys.executable, repo=str(self.tmp), schema_path=str(self.schema),
            config=self.config, selection=self.selection, audit=self.audit,
            run_id="run-1", max_attempts=3, timeout_seconds=60.0, runner=runner)

    def packet(self, checkpoint_id="cp-1", summary="did the thing"):
        result = ev.build_packet(run_id="run-1", task_id="M0-T042",
                                 checkpoint_id=checkpoint_id,
                                 checkpoint={"status": "UNIT_COMPLETE", "summary": summary})
        self.assertTrue(result.ok, result.reason)
        return result.packet.to_dict()


class RecordingReviewer:
    """A reviewer that must NEVER run (refusal paths); records if it is called."""
    def __init__(self):
        self.calls = 0
    def review(self, packet, **kwargs):
        self.calls += 1
        raise AssertionError("the reviewer must not run on a refused packet")


# ---- AS-1: end-to-end fresh ephemeral review + durable record --------------
class AS1EndToEnd(Base):
    def test_fresh_process_returns_a_decision_and_a_durable_record(self):
        journal = er.ReviewJournal(self.tmp / "reviews.jsonl", fsync=False)
        record = er.conduct_ephemeral_review(
            self.reviewer(), self.packet(), reviewed_task_id="M0-T042",
            reviewed_checkpoint_id="cp-1", budget=rp.ReviewBudget(),
            model_context_window=400000, run_id="run-1",
            packet_source_paths=["project-control/tasks/M0-T042.json"],
            journal=journal)
        self.assertTrue(record.ok, record.error_message)
        self.assertEqual(record.decision_value, "CONTINUE")
        self.assertEqual(record.role, er.REVIEWER_ROLE)
        self.assertEqual(record.model_used, "codex-primary")
        self.assertEqual(len(record.evidence_refs), 2)
        # 0A.1 item 7: decision, evidence refs, model identity, usage, digest.
        self.assertIsInstance(record.usage_telemetry, dict)
        self.assertEqual(record.usage_telemetry.get("total_tokens"), 1500)
        self.assertTrue(record.packet_digest)
        self.assertTrue(record.record_digest)
        self.assertTrue(er.verify_record(record.to_dict()))
        # Durability: the record round-trips and verifies from disk.
        rows = journal.load()
        self.assertEqual(len(rows), 1)
        self.assertTrue(journal.verify())
        # AD-087: engine.py was reopened (not in packet), tasks/*.json was not.
        reopened = {r["path"] for r in record.reopened_sources}
        self.assertIn("services/api/app/rules/engine.py", reopened)
        self.assertNotIn("project-control/tasks/M0-T042.json", reopened)

    def test_a_second_review_shares_no_state_with_the_first(self):
        reviewer = self.reviewer()
        first = er.conduct_ephemeral_review(
            reviewer, self.packet("cp-1", "short"), reviewed_task_id="M0-T042",
            reviewed_checkpoint_id="cp-1", budget=rp.ReviewBudget(),
            model_context_window=400000)
        second = er.conduct_ephemeral_review(
            reviewer, self.packet("cp-2", "a materially longer second summary here"),
            reviewed_task_id="M0-T042", reviewed_checkpoint_id="cp-2",
            budget=rp.ReviewBudget(), model_context_window=400000, prior_record=first)
        self.assertNotEqual(first.packet_digest, second.packet_digest)
        self.assertTrue(second.independence["fresh_process_per_review"])
        self.assertFalse(second.independence["shares_conversation_state"])
        self.assertTrue(second.independence["distinct_from_prior"])
        self.assertEqual(second.independence["prior_packet_digest"], first.packet_digest)
        # Each fresh process saw only its own packet (no carried conversation).
        self.assertNotEqual(first.decision["verified_facts"][0]["packet_bytes"],
                            second.decision["verified_facts"][0]["packet_bytes"])

    def test_a_tampered_record_fails_verification(self):
        record = er.conduct_ephemeral_review(
            self.reviewer(), self.packet(), reviewed_task_id="M0-T042",
            reviewed_checkpoint_id="cp-1", budget=rp.ReviewBudget(),
            model_context_window=400000)
        data = record.to_dict()
        self.assertTrue(er.verify_record(data))
        data["model_used"] = "some-other-model"
        self.assertFalse(er.verify_record(data))


# ---- AS-2: 0A.4 packet-budget enforcement ----------------------------------
class AS2Budget(Base):
    def test_effective_ceiling_is_the_lower_of_ordinary_and_relative(self):
        b = rp.ReviewBudget()
        self.assertEqual(b.effective_ceiling(None).tokens, 64000)          # window unknown
        self.assertEqual(b.effective_ceiling(400000).tokens, 64000)        # 20%=80k -> ordinary
        self.assertEqual(b.effective_ceiling(200000).tokens, 40000)        # 20%=40k -> relative
        self.assertEqual(b.effective_ceiling(200000).basis, "relative_model_window")
        self.assertEqual(b.estimate_tokens(400000), 100000)

    def test_an_oversized_packet_is_refused_with_guidance_and_no_review(self):
        rev = RecordingReviewer()
        record = er.conduct_ephemeral_review(
            rev, self.packet(), reviewed_task_id="M0-T042",
            reviewed_checkpoint_id="cp-1", budget=rp.ReviewBudget(),
            model_context_window=100)  # 20% of 100 = 20 tokens -> 80-byte ceiling
        self.assertEqual(rev.calls, 0)
        self.assertFalse(record.ok)
        self.assertEqual(record.error_code, "packet_over_budget")
        self.assertFalse(record.budget["within_ceiling"])
        self.assertTrue(record.budget["guidance"])          # split/summarize guidance
        self.assertEqual(record.budget["effective_ceiling"]["tokens"], 20)
        # Nothing silently omitted: omissions/truncations are recorded explicitly.
        self.assertIn("included_sources", record.budget)

    def test_assessment_records_the_required_fields(self):
        a = rp.assess_packet_budget(
            size_bytes=4000, included_sources=["git", "claude_checkpoint"],
            budget=rp.ReviewBudget(), model_context_window=400000,
            omissions=[{"collector": "reports", "error_category": "missing"}],
            truncated_sections=["git.diff_summary"])
        self.assertEqual(a.estimated_tokens, 1000)
        self.assertTrue(a.within_ceiling and a.within_target)
        self.assertEqual(a.included_sources, ("git", "claude_checkpoint"))
        self.assertEqual(a.truncated_sections, ("git.diff_summary",))
        self.assertEqual(len(a.omissions), 1)
        self.assertEqual(a.guidance, ())

    def test_bad_budget_config_fails_closed(self):
        with self.assertRaises(rp.BudgetError):
            rp.ReviewBudget(target_tokens=70000)           # target > ordinary ceiling
        with self.assertRaises(rp.BudgetError):
            rp.ReviewBudget.from_mapping({"bogus": 1})


# ---- AS-3: AD-083 prohibited-content guard ---------------------------------
class AS3Guard(Base):
    def test_each_prohibited_category_is_rejected(self):
        cases = {
            "full_transcript": {"sections": {"transcript": "the whole chat"}},
            "full_directive_registry": {"sections": {"directive_registry": "all of it"}},
            "all_historical_reports": {"sections": {"all_reports": "every report"}},
            "whole_repository": {"sections": {"whole_repository": "the entire tree"}},
        }
        for category, packet in cases.items():
            with self.subTest(category=category):
                result = rp.guard_packet(packet, current_task_id="M0-T042")
                self.assertTrue(result.rejected)
                self.assertEqual(result.findings[0].category, category)
                self.assertIsNone(result.packet)

    def test_unrelated_task_packets_are_detected_by_correlation(self):
        packet = {"sections": {"task_packets": [{"task_id": "M0-T099", "x": 1}]}}
        result = rp.guard_packet(packet, current_task_id="M0-T042")
        self.assertTrue(result.rejected)
        self.assertEqual(result.findings[0].category, "unrelated_task_packets")

    def test_a_clean_bounded_packet_passes(self):
        result = rp.guard_packet(self.packet(), current_task_id="M0-T042")
        self.assertTrue(result.ok)
        self.assertEqual(result.findings, ())

    def test_strip_mode_removes_the_section_and_records_the_removal(self):
        packet = {"sections": {"git": {"head": "x"}, "transcript": "chat"}}
        result = rp.guard_packet(packet, current_task_id="M0-T042", strip=True)
        self.assertTrue(result.ok)
        self.assertNotIn("transcript", result.packet["sections"])
        self.assertIn("git", result.packet["sections"])
        self.assertEqual(result.findings[0].action, "stripped")

    def test_strip_mode_keeps_the_related_packet_and_drops_the_unrelated_one(self):
        # Duty 6: the `kept` filter in _apply_strip uses a double negative; a mixed
        # list must provably KEEP the related packet and DROP the unrelated one.
        packet = {"sections": {"task_packets": [
            {"task_id": "M0-T042", "keep": True},
            {"task_id": "M0-T099", "drop": True}]}}
        result = rp.guard_packet(packet, current_task_id="M0-T042", strip=True)
        self.assertTrue(result.ok)
        kept = result.packet["sections"]["task_packets"]
        self.assertEqual([p["task_id"] for p in kept], ["M0-T042"])
        self.assertTrue(all(p["task_id"] != "M0-T099" for p in kept))
        self.assertTrue(any(f.category == "unrelated_task_packets"
                            and f.action == "stripped" for f in result.findings))

    def test_strip_mode_drops_task_packets_when_none_are_related(self):
        # When the only packet is unrelated, `kept` is empty and the whole
        # `task_packets` section is removed rather than left as an empty list.
        packet = {"sections": {"task_packets": [{"task_id": "M0-T099", "x": 1}]}}
        result = rp.guard_packet(packet, current_task_id="M0-T042", strip=True)
        self.assertTrue(result.ok)
        self.assertNotIn("task_packets", result.packet["sections"])

    def test_conduct_refuses_a_prohibited_packet_without_running_the_reviewer(self):
        rev = RecordingReviewer()
        record = er.conduct_ephemeral_review(
            rev, {"sections": {"whole_repository": "x"}}, reviewed_task_id="M0-T042",
            reviewed_checkpoint_id="cp", budget=rp.ReviewBudget(),
            model_context_window=None)
        self.assertEqual(rev.calls, 0)
        self.assertEqual(record.error_code, "prohibited_content")
        self.assertTrue(any(f["category"] == "whole_repository"
                            for f in record.guard_findings))


# ---- AS-4: 0A.3 review-cadence policy --------------------------------------
class AS4Cadence(unittest.TestCase):
    def test_every_meaningful_trigger_warrants_a_review(self):
        for trigger in rc.REVIEW_TRIGGERS:
            field = rc._TRIGGER_FIELD[trigger]
            decision = rc.decide_review(rc.CheckpointSignals(**{field: True}))
            self.assertTrue(decision.review)
            self.assertIn(trigger, decision.triggers)

    def test_a_passing_deterministic_check_alone_does_not(self):
        decision = rc.decide_review(rc.CheckpointSignals(only_deterministic_pass=True))
        self.assertFalse(decision.review)
        self.assertEqual(decision.triggers, ())
        self.assertIn("deterministic", decision.reason)

    def test_a_trigger_beats_a_coincident_deterministic_pass(self):
        decision = rc.decide_review(
            rc.CheckpointSignals(unit_complete=True, only_deterministic_pass=True))
        self.assertTrue(decision.review)
        self.assertIn("unit_complete", decision.triggers)

    def test_no_signal_is_no_review(self):
        self.assertFalse(rc.decide_review(rc.CheckpointSignals()).review)


# ---- AS-5: root AGENTS.md ---------------------------------------------------
class AS5AgentsMd(unittest.TestCase):
    TOPICS = ("mission", "authoritative", "session", "guess", "deterministic",
              "borough", "path", "evidence", "autonomy", "stop", "routing",
              "code graph", "context", "checkpoint")

    def test_agents_md_exists_and_covers_the_11_1_topics(self):
        agents = (REPO / "AGENTS.md").read_text(encoding="utf-8-sig").lower()
        for topic in self.TOPICS:
            self.assertIn(topic, agents, f"AGENTS.md is missing topic: {topic}")

    def test_agents_md_does_not_duplicate_claude_md_wholesale(self):
        agents = (REPO / "AGENTS.md").read_text(encoding="utf-8-sig")
        claude = (REPO / "CLAUDE.md").read_text(encoding="utf-8-sig")
        self.assertLess(len(agents.encode("utf-8")), len(claude.encode("utf-8")))
        self.assertLess(len(agents.splitlines()), 120)          # genuinely short
        a_lines = {l.strip() for l in agents.splitlines() if len(l.strip()) >= 40}
        c_lines = {l.strip() for l in claude.splitlines() if len(l.strip()) >= 40}
        self.assertLessEqual(len(a_lines & c_lines), 2, a_lines & c_lines)


# ---- AD-088: role honesty; AD-084 usage parse ------------------------------
class RolesAndUsage(Base):
    def test_worker_role_is_never_activated_by_the_loop(self):
        with self.assertRaises(er.EphemeralReviewError) as ctx:
            er.conduct_ephemeral_review(
                RecordingReviewer(), {"sections": {}}, reviewed_task_id="M0-T042",
                reviewed_checkpoint_id="cp", budget=rp.ReviewBudget(),
                model_context_window=None, role="worker")
        self.assertEqual(ctx.exception.code, "role_not_activatable")

    def test_worker_fallback_is_a_recorded_exception(self):
        record = er.record_worker_fallback(
            run_id="run-1", reviewed_task_id="M0-T042", reviewed_checkpoint_id="cp",
            note="Claude quota-limited; Codex wrote under authorized 0A.5 scope")
        self.assertEqual(record.role, er.WORKER_ROLE)
        self.assertEqual(record.error_code, "worker_fallback_recorded")
        self.assertTrue(er.verify_record(record.to_dict()))

    def test_usage_parse_sums_tokens_and_stays_unknown_when_absent(self):
        u = rv.parse_usage_telemetry(
            '{"type":"token_count","usage":{"input_tokens":10,"output_tokens":4}}')
        self.assertEqual(u["total_tokens"], 14)
        u2 = rv.parse_usage_telemetry(
            '{"usage":{"input_tokens":10,"output_tokens":4,"total_tokens":14}}')
        self.assertEqual(u2["total_tokens"], 14)                # no double-count
        self.assertEqual(rv.parse_usage_telemetry("no json at all"), USAGE_UNKNOWN)


if __name__ == "__main__":
    unittest.main()
