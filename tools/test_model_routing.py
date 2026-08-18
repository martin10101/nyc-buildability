#!/usr/bin/env python3
"""M0-T074 CI tests for deterministic model routing (D-017-R114..R123).

Proves (D-017-R122): simple tasks stay inexpensive; critical tasks cannot be
routed to weaker models; an unauthorized model, self-selected model, unrecorded
fallback, or ungrounded complexity classification is impossible. Stdlib-only.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import model_routing as mr  # noqa: E402

CORPUS = pathlib.Path(__file__).resolve().parent / "model_routing_corpus.json"

PERMITTED = {
    "config_path_sha256": "f" * 64,
    "codex": ["gpt-5.6-sol", "gpt-5.6-terra"],
    "claude": ["claude-opus-4-8"],
}

PROTECTED_CONFIG_TEXT = """\
default_mode = "shadow"

[codex]
allowed_models = ["gpt-5.6-sol", "gpt-5.6-terra"]

[claude]
allowed_models = ["claude-opus-4-8"]
"""


class FrozenCorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.corpus = json.loads(CORPUS.read_text(encoding="utf-8"))

    def test_every_case_classifies_and_routes_as_frozen(self) -> None:
        for case in self.corpus["cases"]:
            with self.subTest(case=case["id"]):
                signals = mr.Signals(**{
                    k: (tuple(v) if isinstance(v, list) else v)
                    for k, v in case["signals"].items()})
                band, determining = mr.classify(signals)
                self.assertEqual(band, case["expected_band"])
                self.assertTrue(determining, "classification must cite signals")
                decision = mr.route(case["id"], "codex", signals, PERMITTED)
                self.assertEqual(decision["chosen_model"], case["expected_codex"])

    def test_simple_tasks_stay_inexpensive(self) -> None:
        cheap = [c for c in self.corpus["cases"] if c["expected_band"] == "LOW"]
        self.assertGreaterEqual(len(cheap), 3)
        for case in cheap:
            self.assertEqual(case["expected_codex"], "gpt-5.6-terra")

    def test_critical_tasks_always_take_the_strongest(self) -> None:
        hard = [c for c in self.corpus["cases"]
                if c["expected_band"] in ("HIGH", "CRITICAL")]
        self.assertGreaterEqual(len(hard), 6)
        for case in hard:
            self.assertEqual(case["expected_codex"], "gpt-5.6-sol")


class GroundedClassificationTests(unittest.TestCase):
    def test_every_band_cites_determining_signals(self) -> None:
        for signals, expected in [
            (mr.Signals(), "LOW"),
            (mr.Signals(files_affected=2), "MEDIUM"),
            (mr.Signals(subsystems_affected=2), "HIGH"),
            (mr.Signals(destructive_operations=True), "CRITICAL"),
        ]:
            band, determining = mr.classify(signals)
            self.assertEqual(band, expected)
            self.assertTrue(determining)

    def test_signals_are_typed_and_closed(self) -> None:
        with self.assertRaises(TypeError):
            mr.Signals(vibes="high")  # unknown signal = ungrounded = refused

    def test_ambiguity_raises_never_lowers(self) -> None:
        band, _ = mr.classify(mr.Signals(ambiguity_or_missing_evidence=True))
        self.assertEqual(band, "MEDIUM")
        band, _ = mr.classify(mr.Signals(subsystems_affected=3,
                                         ambiguity_or_missing_evidence=True))
        self.assertEqual(band, "HIGH")  # HIGH is not promoted by ambiguity, never lowered

    def test_final_acceptance_role_is_critical(self) -> None:
        band, det = mr.classify(mr.Signals(required_reviewer_roles=("final-acceptance",)))
        self.assertEqual(band, "CRITICAL")


class AllowlistBoundaryTests(unittest.TestCase):
    def test_unauthorized_model_cannot_be_chosen(self) -> None:
        decision = mr.route("T", "codex", mr.Signals(), PERMITTED)
        self.assertIn(decision["chosen_model"], PERMITTED["codex"])
        with self.assertRaises(mr.RoutingError):
            mr.route("T", "codex", mr.Signals(),
                     {"codex": [], "claude": [], "config_path_sha256": "0" * 64})

    def test_no_self_selection_api_exists(self) -> None:
        import inspect
        params = inspect.signature(mr.route).parameters
        self.assertNotIn("model", params)
        self.assertNotIn("preferred_model", params)
        self.assertNotIn("override", params)

    def test_unknown_model_ordering_fails_closed(self) -> None:
        with self.assertRaises(mr.RoutingError) as ctx:
            mr.route("T", "codex", mr.Signals(),
                     {"codex": ["gpt-9-mystery"], "claude": [],
                      "config_path_sha256": "0" * 64})
        self.assertIn("never guess", str(ctx.exception))

    def test_single_claude_model_reports_adaptive_unavailable(self) -> None:
        decision = mr.route("T", "claude",
                            mr.Signals(subsystems_affected=3), PERMITTED)
        self.assertFalse(decision["adaptive_available"])
        self.assertEqual(decision["chosen_model"], "claude-opus-4-8")
        self.assertIn("UNAVAILABLE", decision["selection_reason"])
        self.assertIn("not pretending", decision["selection_reason"])

    def test_strongest_reviewer_roles_get_the_strongest_model(self) -> None:
        for role in ("security-reviewer", "directive-compliance-verifier"):
            decision = mr.route("T", "codex", mr.Signals(), PERMITTED, role=role)
            self.assertEqual(decision["chosen_model"], "gpt-5.6-sol", role)

    def test_permitted_evidence_is_recorded(self) -> None:
        decision = mr.route("T", "codex", mr.Signals(), PERMITTED)
        evidence = decision["permitted_models_evidence"]
        self.assertEqual(evidence["config_path_sha256"], "f" * 64)
        self.assertEqual(sorted(evidence["allowlist"]),
                         sorted(PERMITTED["codex"]))


class EscalationAndFallbackTests(unittest.TestCase):
    def test_failed_low_escalates_one_level_with_reason(self) -> None:
        decision = mr.route("T", "codex", mr.Signals(), PERMITTED)
        escalated = mr.escalate_after_failure(decision, "unit failed twice on "
                                              "formatting edge case", PERMITTED)
        self.assertEqual(escalated["complexity_band"], "MEDIUM")
        self.assertEqual(escalated["escalation"]["from_band"], "LOW")
        self.assertTrue(escalated["escalation"]["reason"])

    def test_high_and_critical_never_rerouted(self) -> None:
        for signals in (mr.Signals(subsystems_affected=2),
                        mr.Signals(security_or_authorization_impact=True)):
            decision = mr.route("T", "codex", signals, PERMITTED)
            with self.assertRaises(mr.RoutingError) as ctx:
                mr.escalate_after_failure(decision, "trying", PERMITTED)
            self.assertIn("not silently downgraded", str(ctx.exception))

    def test_escalation_without_reason_refused(self) -> None:
        decision = mr.route("T", "codex", mr.Signals(), PERMITTED)
        with self.assertRaises(mr.RoutingError):
            mr.escalate_after_failure(decision, "   ", PERMITTED)

    def test_quota_fallback_is_separate_and_recorded(self) -> None:
        record = mr.record_quota_fallback("T", "codex", "gpt-5.6-sol",
                                          "gpt-5.6-terra", "sol quota exhausted",
                                          PERMITTED)
        self.assertEqual(record["kind"], "quota_fallback")
        self.assertNotEqual(record["kind"], "routing_decision")
        with self.assertRaises(mr.RoutingError):
            mr.record_quota_fallback("T", "codex", "gpt-5.6-sol",
                                     "gpt-uncleared", "quota", PERMITTED)
        with self.assertRaises(mr.RoutingError):
            mr.record_quota_fallback("T", "codex", "gpt-5.6-sol",
                                     "gpt-5.6-terra", "", PERMITTED)


class RecordAndEvidenceTests(unittest.TestCase):
    def test_decision_record_fields_and_null_telemetry(self) -> None:
        decision = mr.route("M0-T999", "codex", mr.Signals(files_affected=2),
                            PERMITTED, estimated_context_tokens=42_000)
        for field in ("task_id", "complexity_band", "determining_signals",
                      "chosen_model", "permitted_models_evidence",
                      "quota_fallback", "estimated_context_tokens", "result",
                      "telemetry"):
            self.assertIn(field, decision)
        self.assertIsNone(decision["telemetry"]["input_tokens"])  # never zero
        self.assertIsNone(decision["result"])
        done = mr.finalize(decision, result="COMPLETE",
                           telemetry={"input_tokens": 12345, "cost": None})
        self.assertEqual(done["telemetry"]["input_tokens"], 12345)
        self.assertIsNone(done["telemetry"]["cost"])

    def test_append_decision_jsonl_outside_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "runtime" / "model_routing.jsonl"
            a = mr.route("T1", "codex", mr.Signals(), PERMITTED)
            b = mr.route("T2", "codex", mr.Signals(subsystems_affected=2), PERMITTED)
            mr.append_decision(a, path)
            mr.append_decision(b, path)
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)  # append-only
            self.assertEqual(json.loads(lines[0])["task_id"], "T1")

    def test_permitted_models_load_from_protected_config_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = pathlib.Path(tmp) / "config.toml"
            cfg.write_text(PROTECTED_CONFIG_TEXT, encoding="utf-8", newline="\n")
            permitted = mr.load_permitted_models(cfg)
            self.assertEqual(permitted["claude"], ["claude-opus-4-8"])
            self.assertEqual(sorted(permitted["codex"]),
                             ["gpt-5.6-sol", "gpt-5.6-terra"])
            self.assertEqual(len(permitted["config_path_sha256"]), 64)

    def test_router_never_writes_config_or_selection(self) -> None:
        source = (pathlib.Path(__file__).parent / "model_routing.py").read_text(
            encoding="utf-8")
        for needle in ("write_text", "open(", ".unlink", "shutil"):
            occurrences = [ln for ln in source.splitlines()
                           if needle in ln and "model_routing.jsonl" not in ln
                           and "append" not in ln and '"""' not in ln
                           and "#" != ln.strip()[:1]]
            filtered = [ln for ln in occurrences
                        if "config" in ln.lower() or "selection" in ln.lower()]
            self.assertEqual(filtered, [],
                             f"router appears to write config/selection: {filtered}")


if __name__ == "__main__":
    unittest.main()
