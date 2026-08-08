#!/usr/bin/env python3
"""Codex-reviewer, model-selection and evidence tests (D-007 S2.2, S3, S9, S10, S15).

Covers the Section 15 **model selection** family:

* the configured model is used and RECORDED by the supervisor
* a model outside its own provider's allowlist is refused in every role, even if
  the provider would default to it
* the fallback chain is honoured in order and engaging it is a NOTIFY
* an unavailable model with an empty chain queues an ASK
* the per-role split is enforced: `advisory_model` is refused for
  security-sensitive approvals, external writes, ambiguous-effect recovery, scope
  interpretation, and handoff verification
* per-provider allowlists are independent - a Codex entry never satisfies the
  Claude list or vice versa, and each fallback chain validates against its own
  list only
* editing the runtime selection never trips the controller manifest, while
  editing the immutable config does

and the Section 15 **evidence** family: dirty worktree, detached HEAD, stale
`origin/main`, an unavailable remote, a missing packet, and seeded fake-secret
redaction.

The Codex executable is FAKE throughout - a local Python script that writes a
decision file. No network, no tokens, no real review.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile
import textwrap
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import codex_reviewer as rv  # noqa: E402
from tools.agent_supervisor import evidence as ev  # noqa: E402
from tools.agent_supervisor import policy as pol  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.config import (  # noqa: E402
    ConfigError,
    load_controller_config,
    load_model_selection,
    validate_selection,
)
from tools.agent_supervisor.manifest import generate_manifest, verify_manifest  # noqa: E402
from tools.agent_supervisor.process import ProcessResult  # noqa: E402

# --------------------------------------------------------------------------
# Config fixtures
# --------------------------------------------------------------------------

CONFIG_TOML = """
[codex]
allowed_models = ["codex-primary", "codex-fallback", "codex-cheap"]

[claude]
allowed_models = ["claude-worker"]

[controller]
default_mode = "shadow"

[limits]
max_review_packet_bytes = 262144
"""

SELECTION_TOML = """
[codex]
review_model = "codex-primary"
advisory_model = "codex-cheap"
fallback_models = ["codex-fallback"]

[claude]
model = "claude-worker"
fallback_models = []
"""

# --------------------------------------------------------------------------
# The fake codex executable
# --------------------------------------------------------------------------

FAKE_CODEX = textwrap.dedent('''
    """FAKE codex CLI. Writes one decision file. Read-only, no network."""
    import json, os, pathlib, sys, time

    MODE = os.environ.get("FAKE_CODEX_MODE", "normal")
    ARGV = sys.argv[1:]

    def flag(name):
        return ARGV[ARGV.index(name) + 1] if name in ARGV else ""

    packet = sys.stdin.read()
    output_path = flag("--output-last-message")
    model = flag("-m")

    counter_path = os.environ.get("FAKE_COUNTER", "")
    attempt = 1
    if counter_path:
        previous = pathlib.Path(counter_path)
        attempt = int(previous.read_text()) + 1 if previous.exists() else 1
        previous.write_text(str(attempt))

    if MODE == "timeout":
        time.sleep(600)

    decision = {
        "schema_version": "1.0.0", "decision": os.environ.get("FAKE_DECISION",
                                                              "CONTINUE"),
        "reviewed_task_id": "M0-T036", "reviewed_checkpoint_id": "cp-1",
        "verified_repo_head": "b" * 40, "verified_origin_main": "c" * 40,
        "model_used": model,
        "next_claude_prompt": "proceed with the next authorized unit",
        "verified_facts": [{"argv": ARGV, "packet_bytes": len(packet),
                            "attempt": attempt}],
        "evidence_refs": [{"path": "project-control/tasks/M0-T036.json"}],
        "blocking_findings": [], "reason_codes": [], "unverified_claims": [],
        "owner_question": "", "rotation_reason": "",
    }

    if MODE == "stop_for_owner":
        decision.update({"decision": "STOP_FOR_OWNER", "next_claude_prompt": "",
                         "owner_question": "Merge PR #151?"})
    if MODE == "stop_synchronous":
        decision.update({"decision": "STOP_FOR_OWNER", "next_claude_prompt": "",
                         "owner_question": "A second writer touched the checkout.",
                         "reason_codes": ["unexplained_concurrent_writer"]})
    if MODE == "halt":
        decision.update({"decision": "HALT_UNSAFE", "next_claude_prompt": "",
                         "blocking_findings": [{"finding": "controller digest changed"}]})
    if MODE == "rotate":
        decision.update({"decision": "ROTATE_SESSION", "next_claude_prompt": "",
                         "rotation_reason": "context pressure at a safe checkpoint"})
    if MODE == "complete":
        decision.update({"decision": "COMPLETE", "next_claude_prompt": ""})
    if MODE == "unknown_field":
        decision["confidence"] = 0.99
    if MODE == "missing_prompt":
        decision["next_claude_prompt"] = ""
    if MODE == "wrong_checkpoint":
        decision["reviewed_checkpoint_id"] = "cp-999"
    if MODE == "lies_about_model":
        decision["model_used"] = "some-other-model"
    if MODE == "not_json":
        pathlib.Path(output_path).write_text("I could not produce JSON, sorry.")
        raise SystemExit(0)
    if MODE == "invalid_then_valid" and attempt == 1:
        decision["confidence"] = 0.5
    if MODE == "always_invalid":
        decision["confidence"] = 0.5
    if MODE == "no_file":
        raise SystemExit(0)
    if MODE == "provider_rejected":
        # The live shadow-pilot signature: the provider's strict structured-
        # output validator rejects the schema (HTTP 400), the stream carries a
        # turn.failed event, no last-message file is written, and the child
        # exits 1.
        message = os.environ.get(
            "FAKE_PROVIDER_ERROR",
            "Invalid schema for response_format 'codex_output_schema': "
            "In context=(), 'allOf' is not permitted.")
        sys.stdout.write(json.dumps(
            {"type": "turn.failed", "error": {"message": message}}) + "\\n")
        raise SystemExit(1)

    pathlib.Path(output_path).write_text(json.dumps(decision), encoding="utf-8")
    sys.stdout.write(json.dumps({"event": "codex_done", "model": model}) + "\\n")
''')


class ReviewerTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.config_path = self.tmp / "config.toml"
        self.config_path.write_text(CONFIG_TOML, encoding="utf-8")
        self.selection_path = self.tmp / "model_selection.toml"
        self.selection_path.write_text(SELECTION_TOML, encoding="utf-8")
        self.config = load_controller_config(self.config_path)
        self.selection = load_model_selection(self.selection_path)
        self.schema = (REPO / "tools" / "agent_supervisor" / "schemas" /
                       "codex_decision.schema.json")
        self.fake = self.tmp / "fake_codex.py"
        self.fake.write_text(FAKE_CODEX, encoding="utf-8")
        self.audit = AuditLog(self.tmp / "audit.jsonl", fsync=False)

    def reviewer(self, *, mode: str = "normal", availability=None,
                 max_attempts: int = 3, counter: str = "",
                 extra_env: dict | None = None) -> rv.CodexReviewer:
        """A reviewer whose argv is `<python> <fake script> exec ...`."""
        env = {"FAKE_CODEX_MODE": mode}
        if counter:
            env["FAKE_COUNTER"] = counter
        env.update(extra_env or {})
        script = str(self.fake)

        def runner(argv, **kwargs):
            from tools.agent_supervisor.process import run as real_run

            child_env = dict(kwargs.pop("env", {}) or {})
            child_env.update(env)
            child_env.setdefault("PYTHONIOENCODING", "utf-8")
            return real_run([argv[0], script, *argv[1:]], env=child_env, **kwargs)

        return rv.CodexReviewer(
            sys.executable, repo=str(self.tmp), schema_path=str(self.schema),
            config=self.config, selection=self.selection, audit=self.audit,
            run_id="run-1", max_attempts=max_attempts, timeout_seconds=60.0,
            availability=availability, runner=runner)

    @staticmethod
    def packet() -> dict:
        return {"packet_version": "1.0.0", "task_id": "M0-T036",
                "checkpoint_id": "cp-1", "sections": {"git": {"head": "b" * 40}}}


# --------------------------------------------------------------------------
# argv
# --------------------------------------------------------------------------


class ReviewerArgvTests(ReviewerTestBase):
    def test_the_s2_2_shape_is_built_exactly(self) -> None:
        argv = rv.build_argv("codex", repo="/repo", model="codex-primary",
                             schema_path="/s.json", output_path="/o.json")
        self.assertEqual(argv[:2], ["codex", "exec"])
        self.assertEqual(argv[argv.index("-C") + 1], "/repo")
        self.assertEqual(argv[argv.index("-m") + 1], "codex-primary")
        self.assertEqual(argv[argv.index("--sandbox") + 1], "read-only")
        for flag in rv.REQUIRED_FLAGS:
            self.assertIn(flag, argv)
        self.assertEqual(argv[-1], "-")

    def test_a_writable_sandbox_is_refused(self) -> None:
        for sandbox in ("workspace-write", "danger-full-access", ""):
            with self.subTest(sandbox=sandbox):
                with self.assertRaises(rv.ReviewError) as ctx:
                    rv.build_argv("codex", repo="/r", model="m", schema_path="/s",
                                  output_path="/o", sandbox=sandbox)
                self.assertEqual(ctx.exception.code, "reviewer_must_be_read_only")

    def test_a_review_without_a_resolved_model_is_refused(self) -> None:
        with self.assertRaises(rv.ReviewError) as ctx:
            rv.build_argv("codex", repo="/r", model="", schema_path="/s",
                          output_path="/o")
        self.assertEqual(ctx.exception.code, "no_model")

    def test_no_session_or_approval_flag_is_ever_passed(self) -> None:
        argv = rv.build_argv("codex", repo="/r", model="m", schema_path="/s",
                             output_path="/o")
        for flag in ("--resume", "--continue", "--ask-for-approval", "--full-auto"):
            self.assertNotIn(flag, argv)

    def test_the_fake_receives_the_exact_argv(self) -> None:
        outcome = self.reviewer().review(self.packet(), expected_task_id="M0-T036",
                                         expected_checkpoint_id="cp-1")
        self.assertTrue(outcome.ok, outcome.error_message)
        argv = outcome.decision.verified_facts[0]["argv"]
        self.assertIn("--ephemeral", argv)
        self.assertIn("--ignore-user-config", argv)
        self.assertIn("--strict-config", argv)
        self.assertEqual(argv[argv.index("--sandbox") + 1], "read-only")

    def test_the_packet_travels_on_stdin(self) -> None:
        outcome = self.reviewer().review(self.packet())
        self.assertGreater(outcome.decision.verified_facts[0]["packet_bytes"], 10)


# --------------------------------------------------------------------------
# Decision validation (S9)
# --------------------------------------------------------------------------


class DecisionValidationTests(ReviewerTestBase):
    def test_all_six_decisions_validate_with_their_required_fields(self) -> None:
        cases = {
            "normal": "CONTINUE",
            "stop_for_owner": "STOP_FOR_OWNER",
            "halt": "HALT_UNSAFE",
            "rotate": "ROTATE_SESSION",
            "complete": "COMPLETE",
        }
        for mode, expected in cases.items():
            with self.subTest(mode=mode):
                outcome = self.reviewer(mode=mode).review(self.packet())
                self.assertTrue(outcome.ok, outcome.error_message)
                self.assertEqual(outcome.decision.decision, expected)

    def test_a_revise_decision_needs_a_prompt(self) -> None:
        outcome = self.reviewer(mode="missing_prompt",
                                extra_env={"FAKE_DECISION": "REVISE"},
                                max_attempts=1).review(self.packet())
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.error_code, "missing_next_prompt")

    def test_an_unknown_field_is_rejected(self) -> None:
        outcome = self.reviewer(mode="unknown_field", max_attempts=1).review(
            self.packet())
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.error_code, "unknown_fields")

    def test_a_wrongly_correlated_decision_is_rejected(self) -> None:
        outcome = self.reviewer(mode="wrong_checkpoint", max_attempts=1).review(
            self.packet(), expected_task_id="M0-T036", expected_checkpoint_id="cp-1")
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.error_code, "decision_correlation_mismatch")

    def test_non_json_output_is_rejected(self) -> None:
        outcome = self.reviewer(mode="not_json", max_attempts=1).review(self.packet())
        self.assertFalse(outcome.ok)

    def test_a_missing_decision_file_is_rejected(self) -> None:
        outcome = self.reviewer(mode="no_file", max_attempts=1).review(self.packet())
        self.assertFalse(outcome.ok)

    def test_a_bounded_retry_succeeds_and_is_a_notify(self) -> None:
        counter = str(self.tmp / "counter.txt")
        outcome = self.reviewer(mode="invalid_then_valid", counter=counter,
                                max_attempts=3).review(self.packet())
        self.assertTrue(outcome.ok, outcome.error_message)
        self.assertEqual(outcome.attempts, 2)
        self.assertIn("schema_retry_succeeded", outcome.notify_events)

    def test_repeated_invalid_output_halts_rather_than_forwarding(self) -> None:
        outcome = self.reviewer(mode="always_invalid", max_attempts=3).review(
            self.packet())
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.attempts, 3)
        self.assertIsNone(outcome.decision)
        self.assertEqual(outcome.tier.tier, pol.ASK)

    def test_the_supervisor_records_the_model_not_the_models_claim(self) -> None:
        outcome = self.reviewer(mode="lies_about_model").review(self.packet())
        self.assertTrue(outcome.ok, outcome.error_message)
        self.assertEqual(outcome.model_used, "codex-primary")
        self.assertEqual(outcome.decision.model_used, "codex-primary")
        self.assertIn("some-other-model", outcome.model_self_report_mismatch)

    def test_every_review_records_the_selection_digest(self) -> None:
        outcome = self.reviewer().review(self.packet())
        self.assertEqual(outcome.selection_digest, self.selection.digest())
        record = self.audit.read_all()[-1]
        self.assertEqual(record["detail"]["model_used"], "codex-primary")
        self.assertEqual(record["detail"]["model_selection_digest"],
                         self.selection.digest())


# --------------------------------------------------------------------------
# Provider-rejection surfacing (shadow-pilot run 5 defect)
# --------------------------------------------------------------------------


class ProviderRejectionTests(ReviewerTestBase):
    """A provider-rejected turn is never misreported as a missing file."""

    def invalid_output_records(self) -> list[dict]:
        return [record for record in self.audit.read_all()
                if record["event_type"] == "codex_review_invalid_output"]

    def test_a_turn_failed_stream_is_reported_as_provider_rejected(self) -> None:
        outcome = self.reviewer(mode="provider_rejected", max_attempts=1).review(
            self.packet())
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.error_code, "provider_rejected_request")
        self.assertEqual(outcome.returncode, 1)
        self.assertIn("'allOf' is not permitted", outcome.error_message)
        self.assertIn("returncode 1", outcome.error_message)

    def test_the_attempt_audit_carries_the_reason_and_returncode(self) -> None:
        self.reviewer(mode="provider_rejected", max_attempts=1).review(self.packet())
        record = self.invalid_output_records()[-1]
        self.assertEqual(record["error_category"], "provider_rejected_request")
        self.assertEqual(record["detail"]["returncode"], 1)
        self.assertIn("Invalid schema for response_format",
                      record["detail"]["message"])

    def test_a_genuinely_absent_file_stays_missing_decision_file(self) -> None:
        outcome = self.reviewer(mode="no_file", max_attempts=1).review(self.packet())
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.error_code, "missing_decision_file")
        self.assertEqual(outcome.returncode, 0)
        record = self.invalid_output_records()[-1]
        self.assertEqual(record["error_category"], "missing_decision_file")
        self.assertEqual(record["detail"]["returncode"], 0)

    def test_the_provider_reason_is_redacted_before_error_and_audit(self) -> None:
        seeded = "schema rejected; header carried ghp_FAKESEEDEDGITHUBTOKEN0000"
        outcome = self.reviewer(
            mode="provider_rejected", max_attempts=1,
            extra_env={"FAKE_PROVIDER_ERROR": seeded}).review(self.packet())
        self.assertEqual(outcome.error_code, "provider_rejected_request")
        self.assertNotIn("ghp_FAKESEEDEDGITHUBTOKEN0000", outcome.error_message)
        self.assertIn("[REDACTED:", outcome.error_message)
        body = json.dumps(self.invalid_output_records()[-1])
        self.assertNotIn("ghp_FAKESEEDEDGITHUBTOKEN0000", body)

    def test_the_provider_reason_is_bounded_never_a_packet_echo(self) -> None:
        seeded = "x" * 50_000
        outcome = self.reviewer(
            mode="provider_rejected", max_attempts=1,
            extra_env={"FAKE_PROVIDER_ERROR": seeded}).review(self.packet())
        self.assertLess(len(outcome.error_message), 2000)
        self.assertIn("TRUNCATED", outcome.error_message)

    def test_scanning_helper_ignores_healthy_streams(self) -> None:
        healthy = ('{"type":"turn.started"}\n'
                   'not json at all\n'
                   '{"type":"item.completed","item":{"text":"ok"}}\n')
        self.assertEqual(rv.provider_failure_reason(healthy), "")
        failed = healthy + ('{"type":"turn.failed","error":'
                            '{"message":"boom"}}\n')
        self.assertEqual(rv.provider_failure_reason(failed), "boom")


# --------------------------------------------------------------------------
# Strict provider schema subset (regression guard)
# --------------------------------------------------------------------------


class SchemaStrictSubsetTests(unittest.TestCase):
    """The decision schema must stay inside the provider strict subset.

    The live provider rejected the old schema with: "Invalid schema for
    response_format 'codex_output_schema': In context=(), 'allOf' is not
    permitted." No composition/conditional keyword may reappear at any depth.
    """

    FORBIDDEN = ("allOf", "anyOf", "oneOf", "if", "then", "else", "not",
                 "patternProperties")

    @classmethod
    def setUpClass(cls) -> None:
        path = (REPO / "tools" / "agent_supervisor" / "schemas" /
                "codex_decision.schema.json")
        cls.schema = json.loads(path.read_text(encoding="utf-8"))

    def walk(self, node, path="", in_properties=False):
        """Yield (path, key, value) for every dict key outside property-name maps."""
        if isinstance(node, dict):
            for key, value in node.items():
                if not in_properties:
                    yield f"{path}/{key}", key, value
                yield from self.walk(value, f"{path}/{key}",
                                     in_properties=(key == "properties"
                                                    and not in_properties))
        elif isinstance(node, list):
            for index, item in enumerate(node):
                yield from self.walk(item, f"{path}[{index}]", False)

    def test_no_forbidden_keyword_at_any_depth(self) -> None:
        offenders = [where for where, key, _value in self.walk(self.schema)
                     if key in self.FORBIDDEN]
        self.assertEqual(offenders, [])

    def test_every_object_schema_is_closed_and_fully_required(self) -> None:
        # OpenAI strict subset: every object sets additionalProperties false
        # and lists every property in required.
        objects = [(where, value) for where, key, value in self.walk(self.schema)
                   if key in ("items",)] + [("", self.schema)]
        for where, node in objects:
            if not (isinstance(node, dict) and node.get("type") == "object"):
                continue
            with self.subTest(where=where or "<root>"):
                self.assertIs(node.get("additionalProperties"), False)
                self.assertEqual(sorted(node.get("required", [])),
                                 sorted(node.get("properties", {})))

    def test_the_original_seven_fields_remain_required(self) -> None:
        self.assertLessEqual(
            {"schema_version", "decision", "reviewed_task_id",
             "reviewed_checkpoint_id", "verified_repo_head",
             "verified_origin_main", "model_used"},
            set(self.schema["required"]))

    def test_the_decision_enum_is_unchanged(self) -> None:
        self.assertEqual(
            self.schema["properties"]["decision"]["enum"],
            ["CONTINUE", "REVISE", "STOP_FOR_OWNER", "ROTATE_SESSION",
             "COMPLETE", "HALT_UNSAFE"])


# --------------------------------------------------------------------------
# Constraints moved from the old schema's allOf/types into validate_decision
# --------------------------------------------------------------------------


class FlattenedConstraintTests(unittest.TestCase):
    """Every constraint only the old schema enforced now lives in code."""

    @staticmethod
    def payload(**overrides) -> dict:
        base = {
            "schema_version": "1.0.0", "decision": "CONTINUE",
            "reviewed_task_id": "M0-T036", "reviewed_checkpoint_id": "cp-1",
            "verified_repo_head": "b" * 40, "verified_origin_main": "c" * 40,
            "model_used": "codex-primary",
            "next_claude_prompt": "proceed with the next authorized unit",
        }
        base.update(overrides)
        return base

    def reject(self, code: str, **overrides) -> None:
        with self.assertRaises(rv.ReviewError) as ctx:
            rv.validate_decision(self.payload(**overrides))
        self.assertEqual(ctx.exception.code, code)

    def test_string_fields_reject_non_strings(self) -> None:
        for field in rv.DECISION_STRING_FIELDS:
            for bad in (123, ["x"], {"x": 1}, None, True):
                with self.subTest(field=field, bad=bad):
                    self.reject("wrong_field_type", **{field: bad})

    def test_object_list_fields_reject_non_lists_and_non_object_items(self) -> None:
        for field in rv.DECISION_OBJECT_LIST_FIELDS:
            for bad in ("not-a-list", {"fact": "x"}, [["nested"]],
                        [{"fact": "ok"}, "loose string"], [3]):
                with self.subTest(field=field, bad=bad):
                    self.reject("wrong_field_type", **{field: bad})

    def test_reason_codes_items_must_be_strings(self) -> None:
        for bad in ("code", [{"code": "x"}], [1], ["ok", 2]):
            with self.subTest(bad=bad):
                self.reject("wrong_field_type", reason_codes=bad)

    def test_valid_list_shapes_still_pass(self) -> None:
        decision = rv.validate_decision(self.payload(
            verified_facts=[{"fact": "tests reproduced"}],
            unverified_claims=[{"claim": "done", "why": "no CI evidence"}],
            blocking_findings=[], reason_codes=["ci_green"],
            evidence_refs=[{"path": "project-control/tasks/M0-T036.json"}]))
        self.assertEqual(decision.decision, "CONTINUE")

    def test_reviewed_task_id_must_be_nonempty(self) -> None:
        self.reject("empty_required_field", reviewed_task_id="")

    def test_reviewed_checkpoint_id_must_be_nonempty(self) -> None:
        self.reject("empty_required_field", reviewed_checkpoint_id="")

    def test_stop_for_owner_rejects_even_a_whitespace_prompt(self) -> None:
        # The old schema said `const: ""`; `.strip()` alone would let " " by.
        self.reject("prompt_with_stop", decision="STOP_FOR_OWNER",
                    owner_question="Merge?", next_claude_prompt=" ")

    def test_every_per_decision_required_field_is_still_enforced(self) -> None:
        cases = [
            ("missing_next_prompt", {"decision": "CONTINUE",
                                     "next_claude_prompt": ""}),
            ("missing_next_prompt", {"decision": "REVISE",
                                     "next_claude_prompt": ""}),
            ("missing_owner_question", {"decision": "STOP_FOR_OWNER",
                                        "next_claude_prompt": "",
                                        "owner_question": ""}),
            ("missing_rotation_reason", {"decision": "ROTATE_SESSION",
                                         "next_claude_prompt": ""}),
            ("missing_completion_evidence", {"decision": "COMPLETE",
                                             "next_claude_prompt": ""}),
            ("missing_halt_reason", {"decision": "HALT_UNSAFE",
                                     "next_claude_prompt": ""}),
        ]
        for code, overrides in cases:
            with self.subTest(code=code):
                self.reject(code, **overrides)

    def test_unknown_fields_and_bad_decisions_are_still_rejected(self) -> None:
        self.reject("unknown_fields", confidence=0.99)
        self.reject("bad_decision", decision="APPROVE")


# --------------------------------------------------------------------------
# Tier mapping (S9)
# --------------------------------------------------------------------------


class TierMappingTests(ReviewerTestBase):
    def test_stop_for_owner_queues_by_default(self) -> None:
        outcome = self.reviewer(mode="stop_for_owner").review(self.packet())
        self.assertEqual(outcome.tier.tier, pol.ASK)
        self.assertFalse(outcome.tier.synchronous_stop)

    def test_stop_for_owner_citing_section_4_5_pauses(self) -> None:
        outcome = self.reviewer(mode="stop_synchronous").review(self.packet())
        self.assertEqual(outcome.tier.tier, pol.ASK)
        self.assertTrue(outcome.tier.synchronous_stop)

    def test_halt_unsafe_always_pauses(self) -> None:
        outcome = self.reviewer(mode="halt").review(self.packet())
        self.assertTrue(outcome.tier.synchronous_stop)

    def test_complete_never_merges_or_accepts(self) -> None:
        outcome = self.reviewer(mode="complete").review(self.packet())
        self.assertEqual(outcome.tier.tier, pol.NOTIFY)
        self.assertIn("never merges or accepts", outcome.tier.reason)

    def test_a_forwarded_prompt_carries_the_five_required_elements(self) -> None:
        outcome = self.reviewer().review(self.packet())
        prompt = rv.build_forwarded_prompt(
            task_id="M0-T036", stage="phase-2",
            allowed_paths=("tools/agent_supervisor/**",),
            requested_action=outcome.decision.next_claude_prompt,
            stop_conditions=("allowed paths must expand",))
        for fragment in ("TASK: M0-T036", "AUTHORIZED STAGE: phase-2",
                         "PERMITTED PATHS", "REQUESTED ACTION", "STOP CONDITIONS",
                         "claude_checkpoint.schema.json"):
            self.assertIn(fragment, prompt)
        # M0-T048: the bound body is deterministic - no volatile FORWARDED AT clock
        # (appended only at forward time) and no volatile packet reference.
        self.assertNotIn("FORWARDED AT", prompt)

    def test_a_decision_with_no_prompt_cannot_be_forwarded(self) -> None:
        outcome = self.reviewer(mode="stop_for_owner").review(self.packet())
        with self.assertRaises(rv.ReviewError):
            rv.build_forwarded_prompt(
                task_id="t", stage="s", allowed_paths=(),
                requested_action=outcome.decision.next_claude_prompt,
                stop_conditions=())


# --------------------------------------------------------------------------
# Model selection (S3)
# --------------------------------------------------------------------------


class ModelSelectionTests(ReviewerTestBase):
    def test_the_configured_model_is_used_and_recorded(self) -> None:
        resolution = pol.resolve_model("codex", config=self.config,
                                       selection=self.selection)
        self.assertEqual(resolution.model, "codex-primary")
        self.assertEqual(resolution.tier, pol.AUTO)
        outcome = self.reviewer().review(self.packet())
        self.assertEqual(outcome.decision.verified_facts[0]["argv"][
            outcome.decision.verified_facts[0]["argv"].index("-m") + 1],
            "codex-primary")

    def test_an_unlisted_model_is_refused_in_every_role(self) -> None:
        self.selection_path.write_text(
            SELECTION_TOML.replace('review_model = "codex-primary"',
                                   'review_model = "codex-not-approved"'),
            encoding="utf-8")
        selection = load_model_selection(self.selection_path)
        resolution = pol.resolve_model("codex", config=self.config, selection=selection)
        self.assertEqual(resolution.tier, pol.ASK)
        self.assertEqual(resolution.reason_code, "model_not_allowlisted")
        self.assertEqual(resolution.model, "")

    def test_an_unlisted_model_is_refused_even_when_the_provider_defaults_to_it(
            self) -> None:
        # Availability says "yes, this model exists and the provider would use it".
        self.selection_path.write_text(
            SELECTION_TOML.replace('review_model = "codex-primary"',
                                   'review_model = "provider-default-model"'),
            encoding="utf-8")
        selection = load_model_selection(self.selection_path)
        resolution = pol.resolve_model("codex", config=self.config, selection=selection,
                                       availability=lambda _m: True)
        self.assertEqual(resolution.tier, pol.ASK)

    def test_the_fallback_chain_is_honoured_in_order_with_a_notify(self) -> None:
        resolution = pol.resolve_model(
            "codex", config=self.config, selection=self.selection,
            availability=lambda model: model == "codex-fallback")
        self.assertEqual(resolution.model, "codex-fallback")
        self.assertEqual(resolution.tier, pol.NOTIFY)
        self.assertTrue(resolution.fallback_engaged)
        self.assertEqual(resolution.attempted, ("codex-primary", "codex-fallback"))

    def test_engaging_a_fallback_is_reported_as_a_notify_event(self) -> None:
        reviewer = self.reviewer(availability=lambda m: m == "codex-fallback")
        outcome = reviewer.review(self.packet())
        self.assertIn("model_fallback_engaged", outcome.notify_events)
        self.assertEqual(outcome.model_used, "codex-fallback")

    def test_an_exhausted_chain_queues_an_ask_and_holds(self) -> None:
        resolution = pol.resolve_model("codex", config=self.config,
                                       selection=self.selection,
                                       availability=lambda _m: False)
        self.assertEqual(resolution.tier, pol.ASK)
        self.assertEqual(resolution.reason_code, "chain_exhausted")
        self.assertEqual(resolution.model, "")

        outcome = self.reviewer(availability=lambda _m: False).review(self.packet())
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.error_code, "chain_exhausted")
        self.assertEqual(outcome.tier.tier, pol.ASK)

    def test_an_empty_allowlist_means_the_account_default_only(self) -> None:
        config_path = self.tmp / "empty.toml"
        config_path.write_text(CONFIG_TOML.replace(
            'allowed_models = ["claude-worker"]', "allowed_models = []"),
            encoding="utf-8")
        config = load_controller_config(config_path)
        selection_path = self.tmp / "empty_selection.toml"
        selection_path.write_text(SELECTION_TOML.replace(
            'model = "claude-worker"', 'model = ""'), encoding="utf-8")
        selection = load_model_selection(selection_path)
        resolution = pol.resolve_model("claude", config=config, selection=selection)
        self.assertEqual(resolution.model, "")
        self.assertEqual(resolution.tier, pol.AUTO)
        self.assertEqual(resolution.reason_code, "account_default")

    def test_per_provider_lists_are_never_cross_satisfied(self) -> None:
        self.selection_path.write_text(
            SELECTION_TOML.replace('review_model = "codex-primary"',
                                   'review_model = "claude-worker"'),
            encoding="utf-8")
        selection = load_model_selection(self.selection_path)
        result = validate_selection(self.config, selection, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("can never satisfy" in error for error in result.errors))
        resolution = pol.resolve_model("codex", config=self.config, selection=selection)
        self.assertEqual(resolution.reason_code, "model_not_allowlisted")

    def test_a_claude_fallback_validates_against_the_claude_list_only(self) -> None:
        self.selection_path.write_text(
            SELECTION_TOML.replace("[claude]\nmodel = \"claude-worker\"\n"
                                   "fallback_models = []",
                                   "[claude]\nmodel = \"claude-worker\"\n"
                                   "fallback_models = [\"codex-fallback\"]"),
            encoding="utf-8")
        selection = load_model_selection(self.selection_path)
        result = validate_selection(self.config, selection, raise_on_error=False)
        self.assertFalse(result.ok)

    def test_the_advisory_model_is_refused_for_every_reserved_purpose(self) -> None:
        for purpose in sorted(pol.ADVISORY_FORBIDDEN_PURPOSES):
            with self.subTest(purpose=purpose):
                with self.assertRaises(pol.PolicyError) as ctx:
                    pol.assert_advisory_allowed(purpose)
                self.assertEqual(ctx.exception.code, "advisory_model_forbidden")

    def test_the_advisory_model_serves_only_low_stakes_purposes(self) -> None:
        for purpose in sorted(pol.ADVISORY_ALLOWED_PURPOSES):
            with self.subTest(purpose=purpose):
                resolution = pol.resolve_model("codex", config=self.config,
                                               selection=self.selection,
                                               role="advisory", purpose=purpose)
                self.assertEqual(resolution.model, "codex-cheap")

    def test_an_unknown_advisory_purpose_is_refused(self) -> None:
        with self.assertRaises(pol.PolicyError) as ctx:
            pol.assert_advisory_allowed("something_new")
        self.assertEqual(ctx.exception.code, "unknown_advisory_purpose")

    def test_handoff_verification_uses_the_review_model(self) -> None:
        with self.assertRaises(pol.PolicyError):
            self.reviewer().resolve(role="advisory", purpose="handoff_verification")
        resolution = self.reviewer().resolve(role="primary",
                                             purpose="handoff_verification")
        self.assertEqual(resolution.model, "codex-primary")

    def test_an_unknown_provider_or_role_is_refused(self) -> None:
        with self.assertRaises(pol.PolicyError):
            pol.resolve_model("gemini", config=self.config, selection=self.selection)
        with self.assertRaises(pol.PolicyError):
            pol.resolve_model("codex", config=self.config, selection=self.selection,
                              role="whatever")

    def test_an_effort_key_is_refused_in_either_file(self) -> None:
        for body, path in ((CONFIG_TOML + '\n[codex.tuning]\neffort = "high"\n',
                            self.tmp / "bad_config.toml"),
                           (SELECTION_TOML + '\nreasoning_effort = "high"\n',
                            self.tmp / "bad_selection.toml")):
            with self.subTest(path=path.name):
                path.write_text(body, encoding="utf-8")
                loader = (load_controller_config if "config" in path.name
                          else load_model_selection)
                with self.assertRaises(ConfigError) as ctx:
                    loader(path)
                self.assertEqual(ctx.exception.code, "effort_key_forbidden")

    def test_no_effort_flag_reaches_the_reviewer_argv(self) -> None:
        outcome = self.reviewer().review(self.packet())
        argv = outcome.decision.verified_facts[0]["argv"]
        self.assertFalse([a for a in argv if "effort" in a.lower()])

    def test_the_runtime_selection_is_outside_the_controller_manifest(self) -> None:
        package = REPO / "tools" / "agent_supervisor"
        manifest = generate_manifest(package)
        covered = set(manifest["files"])
        self.assertIn("policy.py", covered)
        self.assertNotIn("model_selection.toml", covered)
        self.assertTrue(verify_manifest(package, manifest).ok)

    def test_a_single_run_model_override_uses_the_authenticated_path(self) -> None:
        # S3.2 rule 2: `--codex-model` must pass the same authenticated
        # model-change path as rule 6 (controller-owned IPC, OS access control,
        # interactive owner confirmation).
        # Phase 2 asserted that path did not exist yet and that no override was
        # exposed. Phase 3 BUILDS it, so the assertion inverts: the commands are
        # implemented, and the single-run override is reachable only through
        # `ModelChangeEndpoint.request_run_override`, which runs every rule-6 gate.
        # The behavioural proof lives in tools/test_agent_supervisor_ipc.py
        # (RunOverrideTests); this test pins that no WEAKER path appeared.
        from tools.agent_supervisor import cli
        from tools.agent_supervisor import model_change_ipc as ipc

        self.assertNotIn("set-codex-model", cli.DEFERRED_COMMANDS)
        self.assertNotIn("set-claude-model", cli.DEFERRED_COMMANDS)
        self.assertTrue(hasattr(ipc.ModelChangeEndpoint, "request_run_override"))
        # The override never bypasses the gated path: it delegates to it.
        import inspect

        source = inspect.getsource(ipc.ModelChangeEndpoint.request_run_override)
        self.assertIn("self.request_change(", source)
        # The reviewer adapter itself still exposes no override of its own.
        self.assertNotIn("--codex-model", inspect.getsource(rv.build_argv))


# --------------------------------------------------------------------------
# Evidence (S10)
# --------------------------------------------------------------------------


def fake_process(stdout: str = "", returncode: int = 0, stderr: str = "",
                 timed_out: bool = False):
    def runner(argv, **kwargs):
        return ProcessResult(argv=tuple(argv), returncode=returncode, stdout=stdout,
                             stderr=stderr, duration_seconds=0.01,
                             timed_out=timed_out)
    return runner


def scripted_process(script: dict):
    """Map a git subcommand to a (returncode, stdout[, stderr]) tuple."""
    def runner(argv, **kwargs):
        key = next((token for token in argv[1:] if not token.startswith("-")), "")
        entry = tuple(script.get(key, (0, "", "")))
        code, out = entry[0], entry[1]
        err = entry[2] if len(entry) > 2 else ""
        return ProcessResult(argv=tuple(argv), returncode=code, stdout=out, stderr=err,
                             duration_seconds=0.01)
    return runner


class EvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = pathlib.Path(self._tmp.name).resolve()
        (self.root / "project-control" / "tasks").mkdir(parents=True)
        (self.root / "project-control" / "tasks" / "M0-T036.json").write_text(
            json.dumps({"task_id": "M0-T036"}), encoding="utf-8")

    def collector(self, runner=None, **kwargs) -> ev.EvidenceCollector:
        return ev.EvidenceCollector(repo_root=str(self.root),
                                    runner=runner or fake_process("ok"), **kwargs)

    def test_only_enumerated_read_only_git_commands_are_allowed(self) -> None:
        for tail in (("status", "--porcelain"), ("rev-parse", "HEAD"),
                     ("diff", "--stat"), ("worktree", "list")):
            with self.subTest(tail=tail):
                ev.assert_read_only_git(tail)
        for tail in (("commit", "-m", "x"), ("push",), ("checkout", "main"),
                     ("clean", "-fdx"), ("-C", "/elsewhere", "status"),
                     ("diff", "--ext-diff")):
            with self.subTest(tail=tail):
                with self.assertRaises(ev.EvidenceError):
                    ev.assert_read_only_git(tail)

    def test_the_collector_never_uses_dash_capital_c_or_a_pager(self) -> None:
        seen: list[tuple[str, ...]] = []

        def recording(argv, **kwargs):
            seen.append(tuple(argv))
            return ProcessResult(argv=tuple(argv), returncode=0, stdout="x", stderr="",
                                 duration_seconds=0.0)

        self.collector(recording).collect_git_facts()
        self.assertTrue(seen)
        for argv in seen:
            self.assertIn("--no-pager", argv)
            self.assertNotIn("-C", argv)

    def test_a_dirty_worktree_is_reported_as_a_fact(self) -> None:
        facts = self.collector(scripted_process({
            "status": (0, " M tools/agent_supervisor/policy.py\n?? new.py\n"),
        })).collect_git_facts()
        self.assertTrue(facts["porcelain_status"].ok)
        self.assertIn("?? new.py", facts["porcelain_status"].value)

    def test_a_detached_head_is_a_fact_not_a_collection_failure(self) -> None:
        facts = self.collector(scripted_process({
            "symbolic-ref": (1, "", "fatal: ref HEAD is not a symbolic ref"),
        })).collect_git_facts()
        self.assertTrue(facts["detached"].ok)
        self.assertIs(facts["detached"].value, True)

    def test_a_stale_or_missing_origin_main_is_recorded_as_a_failure(self) -> None:
        facts = self.collector(scripted_process({
            "rev-parse": (128, "", "fatal: ambiguous argument 'origin/main'"),
        })).collect_git_facts()
        self.assertFalse(facts["origin_main"].ok)
        self.assertTrue(facts["origin_main"].error_category.startswith("exit_"))

    def test_remote_reads_are_refused_unless_configured(self) -> None:
        result = self.collector().refresh_remote()
        self.assertFalse(result.ok)
        self.assertEqual(result.error_category, "not_configured")
        allowed = self.collector(allow_remote_reads=True).refresh_remote()
        self.assertTrue(allowed.ok)

    def test_a_timeout_is_never_reported_as_success(self) -> None:
        result = self.collector(fake_process(timed_out=True)).git(
            "status", ("status", "--porcelain"))
        self.assertFalse(result.ok)
        self.assertEqual(result.error_category, "timeout")

    def test_reading_outside_the_repository_is_refused(self) -> None:
        result = self.collector().read_file("../outside.txt")
        self.assertFalse(result.ok)
        self.assertEqual(result.error_category, "outside_repository")

    def test_a_missing_packet_is_an_explicit_failure(self) -> None:
        result = self.collector().read_file("project-control/tasks/NOPE.json")
        self.assertFalse(result.ok)
        self.assertEqual(result.error_category, "missing_file")
        built = ev.build_packet(run_id="r", task_id="t", checkpoint_id="c",
                                checkpoint=None, task_packet=result)
        self.assertTrue(built.ok)
        self.assertEqual(
            sorted(f["collector"] for f in built.packet.failed_collections),
            ["claude_checkpoint", "task_packet.file"])

    def test_truncation_is_always_explicit(self) -> None:
        text, truncated = ev.bound_text("z" * 5000, 100)
        self.assertTrue(truncated)
        self.assertIn("TRUNCATED", text)
        self.assertIn("5000 bytes", text)

    def test_a_packet_carries_summaries_and_digests_not_the_repository(self) -> None:
        collector = self.collector(scripted_process({"status": (0, "clean\n")}))
        built = ev.build_packet(
            run_id="r", task_id="M0-T036", checkpoint_id="cp-1",
            checkpoint={"schema_version": "1.0.0", "checkpoint_id": "cp-1",
                        "summary": "did the thing"},
            git_facts=collector.collect_git_facts(),
            task_packet={"task_id": "M0-T036"},
            directive_refs=("D-007",))
        self.assertTrue(built.ok)
        packet = built.packet
        self.assertTrue(packet.packet_digest)
        self.assertIn("git", packet.sections)
        self.assertIn("UNTRUSTED", packet.sections["claude_checkpoint"]["note"])
        health = ev.packet_health(packet)
        self.assertIn("not the repository", health["warning"])

    def test_an_oversized_packet_stops_for_the_owner(self) -> None:
        built = ev.build_packet(run_id="r", task_id="t", checkpoint_id="c",
                                checkpoint={"schema_version": "1", "checkpoint_id": "c"},
                                extra_sections={"huge": "q" * 20000},
                                max_packet_bytes=2048)
        self.assertFalse(built.ok)
        self.assertEqual(built.stop, ev.STOP_FOR_OWNER)
        self.assertIn("never silently omitted", built.reason)

    def test_a_seeded_fake_secret_is_redacted_before_the_packet(self) -> None:
        # The first seeded line embeds an inventory-name assignment. It is a
        # DELIBERATELY FAKE seeded fixture, and it is assembled at runtime
        # from fragments rather than written as one literal so that the
        # repository's secret scanner does not match a fake credential in
        # these bytes. That keeps the scanner maximally sensitive: no inline
        # scanner-suppression directive is used here or anywhere else in this
        # repository. The assembled value is byte-for-byte the string the
        # assertions need.
        seeded = ("export ANTHROPIC_API" + "_KEY=sk-ant-FAKESEEDEDKEY0000000000\n"
                  "ghp_FAKESEEDEDGITHUBTOKEN0000\n"
                  "machine-owner-token: not-a-real-token")
        built = ev.build_packet(
            run_id="r", task_id="t", checkpoint_id="c",
            checkpoint={"schema_version": "1", "checkpoint_id": "c",
                        "summary": seeded},
            extra_sections={"logs": seeded},
            never_send=("not-a-real-token",))
        self.assertTrue(built.ok)
        body = json.dumps(built.packet.to_dict())
        self.assertNotIn("sk-ant-FAKESEEDEDKEY0000000000", body)
        self.assertNotIn("ghp_FAKESEEDEDGITHUBTOKEN0000", body)
        self.assertNotIn("not-a-real-token", body)
        self.assertGreater(built.packet.redaction_count, 0)
        self.assertIn("REDACTED", body)

    def test_project_control_collection_marks_a_missing_tool(self) -> None:
        results = self.collector().collect_project_control()
        self.assertFalse(results["project_control_status"].ok)
        self.assertEqual(results["project_control_status"].error_category,
                         "missing_tool")

    def test_the_real_repository_packet_builds_within_bounds(self) -> None:
        collector = ev.EvidenceCollector(repo_root=str(REPO))
        packet_file = collector.read_file("project-control/tasks/M0-T036.json")
        built = ev.build_packet(
            run_id="r", task_id="M0-T036", checkpoint_id="cp-1", checkpoint=None,
            task_packet=packet_file, directive_refs=("D-007",))
        self.assertTrue(built.ok)
        self.assertLess(built.packet.size_bytes, ev.DEFAULT_PACKET_BYTES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
