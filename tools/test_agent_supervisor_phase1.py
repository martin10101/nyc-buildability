#!/usr/bin/env python3
"""Phase 1 tests: config, state machine, journal, manifest, breakers, redaction, CLI.

Stdlib `unittest` only (thin-client / CI safe). No network, no real provider
calls, no credentials. Runtime state always goes to a temp directory - never to
%LOCALAPPDATA% and never inside the repository.

D-007 S15 families covered at Phase-1 depth here:
  state machine        legal/illegal transitions, idempotency, crash-resume,
                       journal crash/corruption/migration/integrity failure
  model selection      per-provider allowlists, cross-provider refusal, chains
  adversarial          controller manifest change detected -> halt;
                       seeded fake secrets never persisted
  circuit breakers     warn vs trip, livelock counters
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import CONTROLLER_VERSION  # noqa: E402
from tools.agent_supervisor import cli  # noqa: E402
from tools.agent_supervisor import config as cfg  # noqa: E402
from tools.agent_supervisor import manifest as mf  # noqa: E402
from tools.agent_supervisor import refusals  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.circuit_breakers import (  # noqa: E402
    OK,
    PER_DAY_COUNTERS,
    TRIP,
    WARN,
    BreakerError,
    CircuitBreakers,
)
from tools.agent_supervisor.durable_state import (  # noqa: E402
    DB_FILENAME,
    DurableJournal,
    JournalError,
    checkout_key,
    runtime_dir_for,
)
from tools.agent_supervisor.models import (  # noqa: E402
    ClaudeCheckpoint,
    CodexDecision,
    ProtocolEnvelope,
    RecordError,
)
from tools.agent_supervisor.redaction import redact_structure, redact_text  # noqa: E402

PACKAGE_ROOT = REPO / "tools" / "agent_supervisor"

VALID_CONFIG = """
[controller]
default_mode = "shadow"

[codex]
allowed_models = ["codex-primary", "codex-backup"]

[claude]
allowed_models = ["claude-worker"]

[limits]
max_claude_turns_per_run = 8
warn_ratio = 0.5
"""

VALID_SELECTION = """
[codex]
review_model = "codex-primary"
advisory_model = ""
fallback_models = ["codex-backup"]

[claude]
model = "claude-worker"
fallback_models = []
"""


def write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class TempCase(unittest.TestCase):
    """Base class giving each test an isolated temp directory."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)


# --------------------------------------------------------------------------
# Configuration (D-007 S3.1)
# --------------------------------------------------------------------------


class ConfigTests(TempCase):
    def _files(self, config_text: str = VALID_CONFIG,
               selection_text: str = VALID_SELECTION) -> tuple[pathlib.Path, pathlib.Path]:
        return (write(self.tmp / "config.toml", config_text),
                write(self.tmp / "model_selection.toml", selection_text))

    def test_valid_pair_loads_and_validates(self) -> None:
        config_path, selection_path = self._files()
        config, selection = cfg.load_validated(config_path, selection_path)
        self.assertEqual(config.codex_allowed_models, ("codex-primary", "codex-backup"))
        self.assertEqual(config.claude_allowed_models, ("claude-worker",))
        self.assertEqual(selection.codex.primary, "codex-primary")
        self.assertEqual(selection.codex.chain(), ("codex-primary", "codex-backup"))
        self.assertEqual(len(selection.digest()), 64)
        self.assertEqual(config.limits.max_claude_turns_per_run, 8)

    def test_effort_key_in_controller_config_is_rejected(self) -> None:
        text = VALID_CONFIG + '\n[claude.tuning]\neffort = "high"\n'
        config_path, _ = self._files(config_text=text)
        with self.assertRaises(cfg.ConfigError) as ctx:
            cfg.load_controller_config(config_path)
        self.assertEqual(ctx.exception.code, "effort_key_forbidden")

    def test_effort_key_in_runtime_selection_is_rejected(self) -> None:
        text = VALID_SELECTION + '\nreasoning_effort = "medium"\n'
        _, selection_path = self._files(selection_text=text)
        with self.assertRaises(cfg.ConfigError) as ctx:
            cfg.load_model_selection(selection_path)
        self.assertEqual(ctx.exception.code, "effort_key_forbidden")

    def test_effort_key_at_any_depth_is_rejected(self) -> None:
        text = VALID_CONFIG + '\n[codex.options.nested]\nmodel_effort_level = 3\n'
        config_path, _ = self._files(config_text=text)
        with self.assertRaises(cfg.ConfigError) as ctx:
            cfg.load_controller_config(config_path)
        self.assertEqual(ctx.exception.code, "effort_key_forbidden")

    def test_codex_entry_never_satisfies_the_claude_list(self) -> None:
        selection = VALID_SELECTION.replace('model = "claude-worker"',
                                            'model = "codex-primary"')
        config_path, selection_path = self._files(selection_text=selection)
        config = cfg.load_controller_config(config_path)
        chosen = cfg.load_model_selection(selection_path)
        result = cfg.validate_selection(config, chosen, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("can never satisfy a claude role" in e for e in result.errors),
                        result.errors)

    def test_claude_entry_never_satisfies_the_codex_list(self) -> None:
        selection = VALID_SELECTION.replace('review_model = "codex-primary"',
                                            'review_model = "claude-worker"')
        config_path, selection_path = self._files(selection_text=selection)
        config = cfg.load_controller_config(config_path)
        chosen = cfg.load_model_selection(selection_path)
        result = cfg.validate_selection(config, chosen, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("can never satisfy a codex role" in e for e in result.errors),
                        result.errors)

    def test_fallback_outside_own_allowlist_is_refused(self) -> None:
        selection = VALID_SELECTION.replace('fallback_models = ["codex-backup"]',
                                            'fallback_models = ["codex-unlisted"]')
        config_path, selection_path = self._files(selection_text=selection)
        config = cfg.load_controller_config(config_path)
        chosen = cfg.load_model_selection(selection_path)
        with self.assertRaises(cfg.ConfigError) as ctx:
            cfg.validate_selection(config, chosen)
        self.assertEqual(ctx.exception.code, "selection_rejected")

    def test_empty_allowlist_forbids_explicit_selection(self) -> None:
        config_text = VALID_CONFIG.replace('allowed_models = ["claude-worker"]',
                                           "allowed_models = []")
        config_path, selection_path = self._files(config_text=config_text)
        config = cfg.load_controller_config(config_path)
        chosen = cfg.load_model_selection(selection_path)
        result = cfg.validate_selection(config, chosen, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("allowed_models is empty" in e for e in result.errors),
                        result.errors)

    def test_limited_auto_cannot_come_from_configuration(self) -> None:
        config_text = VALID_CONFIG.replace('default_mode = "shadow"',
                                           'default_mode = "limited-auto"')
        config_path, _ = self._files(config_text=config_text)
        with self.assertRaises(cfg.ConfigError) as ctx:
            cfg.load_controller_config(config_path)
        self.assertEqual(ctx.exception.code, "mode_not_bootable")

    def test_runtime_key_in_controller_config_is_refused(self) -> None:
        config_text = VALID_CONFIG + '\n[selection]\nreview_model = "codex-primary"\n'
        config_path, _ = self._files(config_text=config_text)
        with self.assertRaises(cfg.ConfigError) as ctx:
            cfg.load_controller_config(config_path)
        self.assertEqual(ctx.exception.code, "runtime_key_in_controller_config")

    def test_controller_key_in_runtime_file_is_refused(self) -> None:
        selection_text = VALID_SELECTION + '\n[codex.extra]\nallowed_models = ["x"]\n'
        _, selection_path = self._files(selection_text=selection_text)
        with self.assertRaises(cfg.ConfigError) as ctx:
            cfg.load_model_selection(selection_path)
        self.assertEqual(ctx.exception.code, "controller_key_in_runtime_file")

    def test_each_file_must_parse_as_standalone_toml(self) -> None:
        broken = write(self.tmp / "broken.toml", "[codex\nallowed_models = ")
        with self.assertRaises(cfg.ConfigError) as ctx:
            cfg.load_controller_config(broken)
        self.assertEqual(ctx.exception.code, "invalid_toml")

    def test_unknown_limit_key_fails_closed(self) -> None:
        config_text = VALID_CONFIG + "\nmax_unicorns = 4\n"
        config_path, _ = self._files(config_text=config_text)
        with self.assertRaises(cfg.ConfigError) as ctx:
            cfg.load_controller_config(config_path)
        self.assertEqual(ctx.exception.code, "unknown_limit")

    def test_the_r207_per_day_and_resource_limits_are_configurable(self) -> None:
        config_text = VALID_CONFIG + (
            "max_model_calls_per_day = 500\n"
            "max_external_writes_per_day = 40\n"
            "max_cpu_percent = 80\n"
            "max_memory_bytes = 4294967296\n")
        config_path, _ = self._files(config_text=config_text)
        config = cfg.load_controller_config(config_path)
        self.assertEqual(config.limits.max_model_calls_per_day, 500)
        self.assertEqual(config.limits.max_external_writes_per_day, 40)
        self.assertEqual(config.limits.max_cpu_percent, 80)
        self.assertEqual(config.limits.max_memory_bytes, 4294967296)

    def test_the_r207_limits_have_bounded_fail_closed_defaults(self) -> None:
        limits = cfg.Limits()
        self.assertGreater(limits.max_model_calls_per_day, 0)
        self.assertGreater(limits.max_external_writes_per_day, 0)
        self.assertGreater(limits.max_cpu_percent, 0)
        self.assertGreater(limits.max_memory_bytes, 0)

    def test_a_malformed_r207_limit_fails_closed(self) -> None:
        for bad in ("max_model_calls_per_day = 0\n",
                    "max_external_writes_per_day = -5\n",
                    "max_cpu_percent = 0\n",
                    'max_memory_bytes = "lots"\n'):
            config_text = VALID_CONFIG + bad
            config_path, _ = self._files(config_text=config_text)
            with self.assertRaises(cfg.ConfigError) as ctx:
                cfg.load_controller_config(config_path)
            self.assertEqual(ctx.exception.code, "bad_limit")

    def test_example_config_carries_no_effort_key_and_no_secret(self) -> None:
        example = (PACKAGE_ROOT / "config.example.toml").read_text(encoding="utf-8")
        self.assertNotIn("effort =", example)
        config = cfg.load_controller_config(PACKAGE_ROOT / "config.example.toml")
        self.assertEqual(config.default_mode, "shadow")
        self.assertTrue(all(name.startswith("<") for name in config.codex_allowed_models))


# --------------------------------------------------------------------------
# Runtime location (D-007 S6)
# --------------------------------------------------------------------------


class RuntimeLocationTests(TempCase):
    def test_key_is_the_full_canonical_path_not_the_basename(self) -> None:
        a = self.tmp / "parent_a" / "repo"
        b = self.tmp / "parent_b" / "repo"
        a.mkdir(parents=True)
        b.mkdir(parents=True)
        self.assertNotEqual(checkout_key(a), checkout_key(b))
        self.assertEqual(len(checkout_key(a)), 64)

    def test_runtime_dir_is_outside_the_checkout(self) -> None:
        checkout = self.tmp / "checkout"
        checkout.mkdir()
        runtime = runtime_dir_for(checkout, base=self.tmp / "runtime")
        self.assertNotIn(checkout.resolve(), runtime.parents)

    def test_runtime_dir_inside_the_checkout_is_refused(self) -> None:
        checkout = self.tmp / "checkout"
        checkout.mkdir()
        with self.assertRaises(JournalError) as ctx:
            runtime_dir_for(checkout, base=checkout / "state")
        self.assertEqual(ctx.exception.code, "runtime_dir_inside_repo")


# --------------------------------------------------------------------------
# Durable journal (D-007 S6, S7, S13.7)
# --------------------------------------------------------------------------


class JournalTests(TempCase):
    def journal(self, name: str = DB_FILENAME) -> DurableJournal:
        journal = DurableJournal(self.tmp / name).open()
        self.addCleanup(journal.close)
        return journal

    def test_fresh_journal_is_healthy(self) -> None:
        report = self.journal().integrity_check()
        self.assertTrue(report.ok, report.message)
        self.assertIn("sqlite_integrity=ok", report.checks)

    def test_durability_pragmas_are_set(self) -> None:
        journal = self.journal()
        mode = journal.conn.execute("PRAGMA journal_mode").fetchone()[0]
        synchronous = journal.conn.execute("PRAGMA synchronous").fetchone()[0]
        self.assertEqual(mode.lower(), "wal")
        self.assertEqual(int(synchronous), 2)  # 2 == FULL

    def test_state_survives_close_and_reopen(self) -> None:
        journal = self.journal()
        journal.set_state("current_state", sm.CLAUDE_RUNNING)
        journal.close()
        reopened = DurableJournal(self.tmp / DB_FILENAME).open()
        self.addCleanup(reopened.close)
        self.assertEqual(reopened.get_state("current_state"), sm.CLAUDE_RUNNING)

    def test_corrupted_database_is_detected_not_guessed(self) -> None:
        journal = self.journal()
        journal.set_state("k", "v")
        journal.close()
        db_path = self.tmp / DB_FILENAME
        data = bytearray(db_path.read_bytes())
        for offset in range(60, min(len(data), 4096)):
            data[offset] = (data[offset] + 137) % 256
        db_path.write_bytes(bytes(data))

        detected = False
        try:
            broken = DurableJournal(db_path).open()
        except JournalError:
            detected = True
        else:
            self.addCleanup(broken.close)
            detected = not broken.integrity_check().ok
        self.assertTrue(detected, "corruption was neither refused at open nor at check")

    def test_partial_migration_is_refused(self) -> None:
        journal = self.journal()
        journal._meta_set("migration_in_progress", "1")  # simulate a crash mid-migration
        report = journal.integrity_check()
        self.assertFalse(report.ok)
        self.assertEqual(report.code, "partial_migration")

    def test_rolled_back_journal_is_refused(self) -> None:
        journal = self.journal()
        journal.record_transition(state_from=sm.IDLE, state_to=sm.PREFLIGHT,
                                  trigger="start_command", run_id="r1")
        journal.conn.execute("DELETE FROM transitions")  # a rollback to an older state
        report = journal.integrity_check()
        self.assertFalse(report.ok)
        self.assertEqual(report.code, "rolled_back")

    def test_before_and_after_effect_records(self) -> None:
        journal = self.journal()
        journal.record_before_effect(action_id="push-1", effect_type="git_push",
                                     target="task/M0-T036", expected_prior_state="abc",
                                     request_digest="d" * 64)
        self.assertEqual(len(journal.pending_effects()), 1)
        journal.record_after_effect("push-1", resulting_state="def")
        self.assertEqual(journal.pending_effects(), [])
        self.assertEqual(journal.get_effect("push-1").status, "CONFIRMED")

    def test_duplicate_action_id_is_refused(self) -> None:
        journal = self.journal()
        journal.record_before_effect(action_id="a1", effect_type="t", target="x",
                                     expected_prior_state="", request_digest="0" * 64)
        with self.assertRaises(JournalError) as ctx:
            journal.record_before_effect(action_id="a1", effect_type="t", target="x",
                                         expected_prior_state="", request_digest="0" * 64)
        self.assertEqual(ctx.exception.code, "duplicate_action_id")

    def test_after_effect_without_a_before_effect_is_refused(self) -> None:
        journal = self.journal()
        with self.assertRaises(JournalError) as ctx:
            journal.record_after_effect("never-journaled", resulting_state="x")
        self.assertEqual(ctx.exception.code, "no_pending_effect")

    def test_outbox_persists_before_send_and_refuses_duplicates(self) -> None:
        journal = self.journal()
        journal.enqueue_outbound("m1", {"a": 1})
        self.assertEqual(len(journal.unsent_outbound()), 1)
        journal.mark_sent("m1")
        self.assertEqual(journal.unsent_outbound(), [])
        with self.assertRaises(JournalError):
            journal.enqueue_outbound("m1", {"a": 1})

    def test_backup_and_restore_drill(self) -> None:
        journal = self.journal()
        journal.set_state("current_state", sm.COLLECT_EVIDENCE)
        backup = journal.backup_to(self.tmp / "backup" / "journal.bak")
        journal.set_state("current_state", sm.HALTED)
        journal.close()

        DurableJournal.restore_from(backup, self.tmp / DB_FILENAME)
        restored = DurableJournal(self.tmp / DB_FILENAME).open()
        self.addCleanup(restored.close)
        self.assertTrue(restored.integrity_check().ok)
        self.assertEqual(restored.get_state("current_state"), sm.COLLECT_EVIDENCE)


# --------------------------------------------------------------------------
# State machine (D-007 S7)
# --------------------------------------------------------------------------


class StateMachineTests(TempCase):
    def setUp(self) -> None:
        super().setUp()
        self.journal = DurableJournal(self.tmp / DB_FILENAME).open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.tmp / "audit.jsonl", fsync=False)
        self.machine = sm.StateMachine(self.journal, self.audit, run_id="run-1")

    def test_every_named_state_exists(self) -> None:
        for name in (
            "IDLE", "RECOVER_BOOT", "PREFLIGHT", "START_CLAUDE", "CLAUDE_RUNNING",
            "ROTATION_PENDING", "CHECKPOINT_RECEIVED", "COLLECT_EVIDENCE", "CODEX_REVIEW",
            "VALIDATE_DECISION", "POLICY_CHECK", "FORWARD_PROMPT", "WAIT_FOR_OWNER",
            "PAUSED_RECOVERY", "RECONCILE_EXTERNAL_EFFECT", "USAGE_LIMIT_WAIT",
            "SCHEDULED_RESUME", "PREPARE_ROTATION", "VERIFY_HANDOFF", "START_FRESH_SESSION",
            "COMPLETE", "EMERGENCY_STOPPED", "HALTED",
        ):
            self.assertIn(name, sm.STATES)
        # 23 D-007 S7 states + the four D-024 section-3 additions
        # (GRACEFUL_STOPPING, AWAIT_CHILDREN, CODEX_OUTAGE_BACKOFF,
        # NO_ELIGIBLE_WORK) — M0-T092, R029/R033; the additions are covered in
        # tools/test_agent_supervisor_controller_succession.py.
        self.assertEqual(len(sm.STATES), 27)

    def test_every_transition_has_a_documented_trigger(self) -> None:
        for transition in sm.TRANSITIONS:
            self.assertTrue(transition.doc.strip(),
                            f"{transition.state_from}->{transition.state_to} has no doc")
            self.assertIn(transition.state_from, sm.STATES)
            self.assertIn(transition.state_to, sm.STATES)

    def test_legal_transition_applies_and_persists(self) -> None:
        result = self.machine.transition(sm.PREFLIGHT, "start_command")
        self.assertTrue(result.applied)
        self.assertEqual(self.machine.current_state, sm.PREFLIGHT)
        self.assertEqual(self.journal.last_transition().state_to, sm.PREFLIGHT)

    def test_illegal_transition_is_refused(self) -> None:
        with self.assertRaises(sm.IllegalTransitionError):
            self.machine.transition(sm.COMPLETE, "decision_complete")  # IDLE -> COMPLETE
        self.assertEqual(self.machine.current_state, sm.IDLE)

    def test_unknown_state_and_unknown_trigger_are_refused(self) -> None:
        with self.assertRaises(sm.IllegalTransitionError):
            self.machine.transition("NOT_A_STATE", "start_command")
        with self.assertRaises(sm.IllegalTransitionError):
            self.machine.transition(sm.PREFLIGHT, "not_a_trigger")

    def test_repeating_the_same_transition_is_idempotent(self) -> None:
        self.machine.transition(sm.PREFLIGHT, "start_command")
        before = len(self.journal.transitions())
        repeat = self.machine.transition(sm.PREFLIGHT, "start_command")
        self.assertFalse(repeat.applied)
        self.assertEqual(repeat.reason, "idempotent_repeat")
        self.assertEqual(len(self.journal.transitions()), before)

    def test_one_audit_event_per_applied_transition(self) -> None:
        start = self.audit.head_sequence
        self.machine.transition(sm.PREFLIGHT, "start_command")
        self.machine.transition(sm.START_CLAUDE, "preflight_pass")
        self.assertEqual(self.audit.head_sequence - start, 2)
        self.assertTrue(self.audit.verify_chain().ok)

    def test_side_effect_runs_only_after_the_commit(self) -> None:
        observed: list[str] = []

        def side_effect() -> None:
            # By the time the side effect runs the journal must already say PREFLIGHT.
            observed.append(str(self.journal.get_state("current_state")))

        self.machine.transition(sm.PREFLIGHT, "start_command", side_effect=side_effect)
        self.assertEqual(observed, [sm.PREFLIGHT])

    def test_crash_resume_reads_state_from_the_journal(self) -> None:
        self.machine.transition(sm.PREFLIGHT, "start_command")
        self.machine.transition(sm.START_CLAUDE, "preflight_pass")
        self.machine.transition(sm.CLAUDE_RUNNING, "claude_process_started")
        self.journal.close()

        # A brand-new process with no memory of the old one.
        reopened = DurableJournal(self.tmp / DB_FILENAME).open()
        self.addCleanup(reopened.close)
        resumed = sm.StateMachine(reopened, AuditLog(self.tmp / "audit.jsonl", fsync=False),
                                  run_id="run-1")
        self.assertEqual(resumed.current_state, sm.CLAUDE_RUNNING)
        self.assertEqual(resumed.last_trigger, "claude_process_started")
        # And it continues legally from exactly there.
        self.assertTrue(resumed.transition(sm.CHECKPOINT_RECEIVED,
                                           "valid_checkpoint_received").applied)

    def test_no_action_while_blocked(self) -> None:
        self.machine.transition(sm.PREFLIGHT, "start_command")
        self.machine.transition(sm.WAIT_FOR_OWNER, "preflight_requires_owner")
        with self.assertRaises(sm.IllegalTransitionError):
            self.machine.assert_can_act()

    def test_rotation_pending_never_terminates_the_unit(self) -> None:
        """S11.2: crossing a threshold mid-unit flags rotation; it does not stop work."""
        for state, trigger in ((sm.PREFLIGHT, "start_command"),
                               (sm.START_CLAUDE, "preflight_pass"),
                               (sm.CLAUDE_RUNNING, "claude_process_started"),
                               (sm.ROTATION_PENDING, "rotation_threshold_crossed")):
            self.machine.transition(state, trigger)
        # The only non-emergency way out is the unit finishing normally.
        self.assertEqual(sm.legal_targets(sm.ROTATION_PENDING),
                         (sm.CHECKPOINT_RECEIVED, sm.EMERGENCY_STOPPED))


# --------------------------------------------------------------------------
# Controller manifest (D-007 S13.1)
# --------------------------------------------------------------------------


class ManifestTests(TempCase):
    def _controller(self) -> pathlib.Path:
        root = self.tmp / "controller"
        (root / "schemas").mkdir(parents=True)
        (root / "prompts").mkdir(parents=True)
        write(root / "policy.py", "RULES = 1\n")
        write(root / "schemas" / "a.json", "{}\n")
        write(root / "prompts" / "p.md", "prompt\n")
        write(root / "config.toml", VALID_CONFIG)
        return root

    def test_generate_and_verify_round_trip(self) -> None:
        root = self._controller()
        manifest = mf.generate_manifest(root)
        self.assertIn("policy.py", manifest["files"])
        self.assertIn("schemas/a.json", manifest["files"])
        self.assertIn("config.toml", manifest["files"])
        self.assertTrue(mf.verify_manifest(root, manifest).ok)

    def test_a_changed_controller_file_halts(self) -> None:
        root = self._controller()
        manifest = mf.generate_manifest(root)
        write(root / "policy.py", "RULES = 2  # tampered\n")
        verification = mf.verify_manifest(root, manifest)
        self.assertFalse(verification.ok)
        self.assertEqual(verification.changed, ("policy.py",))
        with self.assertRaises(mf.ManifestError):
            mf.require_verified(root, manifest)

    def test_a_deleted_and_an_added_file_are_both_detected(self) -> None:
        root = self._controller()
        manifest = mf.generate_manifest(root)
        (root / "policy.py").unlink()
        write(root / "extra.py", "x = 1\n")
        verification = mf.verify_manifest(root, manifest)
        self.assertEqual(verification.missing, ("policy.py",))
        self.assertEqual(verification.unexpected, ("extra.py",))

    def test_model_selection_is_outside_the_manifest(self) -> None:
        """S3.1: editing the runtime selection must NEVER invalidate the controller."""
        root = self._controller()
        write(root / mf.MODEL_SELECTION_FILENAME, VALID_SELECTION)
        manifest = mf.generate_manifest(root)
        self.assertNotIn(mf.MODEL_SELECTION_FILENAME, manifest["files"])
        write(root / mf.MODEL_SELECTION_FILENAME,
              VALID_SELECTION.replace("codex-primary", "codex-backup"))
        self.assertTrue(mf.verify_manifest(root, manifest).ok)
        # ...while editing the immutable config DOES invalidate it.
        write(root / "config.toml", VALID_CONFIG + "\n# changed\n")
        self.assertFalse(mf.verify_manifest(root, manifest).ok)

    def test_offering_model_selection_as_a_covered_file_is_refused(self) -> None:
        root = self._controller()
        selection = write(root / mf.MODEL_SELECTION_FILENAME, VALID_SELECTION)
        with self.assertRaises(mf.ManifestError) as ctx:
            mf.generate_manifest(root,
                                 extra_files=[(mf.MODEL_SELECTION_FILENAME, selection)])
        self.assertEqual(ctx.exception.code, "excluded_file_offered")

    def test_real_package_manifest_covers_the_supervisor(self) -> None:
        manifest = mf.generate_manifest(PACKAGE_ROOT)
        files = manifest["files"]
        for expected in ("cli.py", "config.py", "state_machine.py", "audit_log.py",
                         "schemas/claude_checkpoint.schema.json",
                         "prompts/codex_review.md", "config.example.toml"):
            self.assertIn(expected, files)
        self.assertNotIn(mf.MODEL_SELECTION_FILENAME, files)
        self.assertEqual(manifest["controller_version"], CONTROLLER_VERSION)


# --------------------------------------------------------------------------
# Circuit breakers (D-007 S13.8)
# --------------------------------------------------------------------------


class CircuitBreakerTests(unittest.TestCase):
    def breakers(self, **overrides: object) -> CircuitBreakers:
        limits = cfg.Limits(**overrides)  # type: ignore[arg-type]
        return CircuitBreakers(limits)

    def test_counter_warns_then_trips(self) -> None:
        breakers = self.breakers(max_consecutive_hard_denies=4, warn_ratio=0.5)
        self.assertEqual(breakers.record("consecutive_hard_denies").verdict, OK)
        self.assertEqual(breakers.record("consecutive_hard_denies").verdict, WARN)
        self.assertEqual(breakers.record("consecutive_hard_denies").verdict, WARN)
        verdict = breakers.record("consecutive_hard_denies")
        self.assertEqual(verdict.verdict, TRIP)
        self.assertTrue(verdict.tripped)
        self.assertIn("synchronous pause", verdict.message)

    def test_progress_resets_the_livelock_counters(self) -> None:
        breakers = self.breakers(max_consecutive_no_progress=2)
        breakers.record("consecutive_no_progress")
        breakers.record_progress()
        self.assertEqual(breakers.value("consecutive_no_progress"), 0)

    def test_unknown_breaker_names_raise(self) -> None:
        breakers = self.breakers()
        with self.assertRaises(BreakerError):
            breakers.record("max_unicorns")
        with self.assertRaises(BreakerError):
            breakers.gauge("temperature", 1)

    def test_gauges_trip_on_ceiling_and_floor(self) -> None:
        breakers = self.breakers(max_processes=10, min_free_disk_bytes=1000)
        self.assertEqual(breakers.gauge("process_count", 10).verdict, TRIP)
        self.assertEqual(breakers.gauge("process_count", 1).verdict, OK)
        self.assertEqual(breakers.gauge("free_disk_bytes", 900).verdict, TRIP)
        self.assertEqual(breakers.gauge("free_disk_bytes", 10 ** 9).verdict, OK)

    def test_tripped_reports_every_tripped_counter(self) -> None:
        breakers = self.breakers(max_restart_attempts=1)
        breakers.record("restart_attempts")
        self.assertEqual([v.name for v in breakers.tripped()], ["restart_attempts"])

    # -- D-007-R207 completion: per-day caps + CPU/memory gauges --------------

    def test_per_day_model_call_cap_warns_then_trips(self) -> None:
        breakers = self.breakers(max_model_calls_per_day=4, warn_ratio=0.5)
        day = "2026-08-05"
        self.assertEqual(breakers.record_daily("model_calls_per_day", day).verdict, OK)
        self.assertEqual(breakers.record_daily("model_calls_per_day", day).verdict, WARN)
        self.assertEqual(breakers.record_daily("model_calls_per_day", day).verdict, WARN)
        verdict = breakers.record_daily("model_calls_per_day", day)
        self.assertEqual(verdict.verdict, TRIP)
        self.assertTrue(verdict.tripped)

    def test_per_day_external_write_cap_trips_at_its_bound(self) -> None:
        breakers = self.breakers(max_external_writes_per_day=2)
        day = "2026-08-05"
        self.assertFalse(breakers.record_daily("external_writes_per_day", day).tripped)
        self.assertTrue(breakers.record_daily("external_writes_per_day", day).tripped)

    def test_a_new_day_resets_the_per_day_counters(self) -> None:
        breakers = self.breakers(max_model_calls_per_day=2)
        breakers.record_daily("model_calls_per_day", "2026-08-05")
        self.assertTrue(
            breakers.record_daily("model_calls_per_day", "2026-08-05").tripped)
        verdict = breakers.record_daily("model_calls_per_day", "2026-08-06")
        self.assertEqual(breakers.value("model_calls_per_day"), 1)
        self.assertFalse(verdict.tripped)

    def test_a_per_day_tick_without_a_date_fails_closed(self) -> None:
        breakers = self.breakers()
        with self.assertRaises(BreakerError):
            breakers.record_daily("model_calls_per_day", "")

    def test_record_daily_refuses_a_non_per_day_counter(self) -> None:
        breakers = self.breakers()
        with self.assertRaises(BreakerError):
            breakers.record_daily("restart_attempts", "2026-08-05")
        self.assertEqual(
            PER_DAY_COUNTERS,
            frozenset({"model_calls_per_day", "external_writes_per_day"}))

    def test_cpu_and_memory_gauges_trip_on_their_ceiling(self) -> None:
        breakers = self.breakers(max_cpu_percent=90, max_memory_bytes=1000, warn_ratio=0.5)
        self.assertEqual(breakers.gauge("cpu_percent", 90).verdict, TRIP)
        self.assertEqual(breakers.gauge("cpu_percent", 60).verdict, WARN)
        self.assertEqual(breakers.gauge("cpu_percent", 10).verdict, OK)
        self.assertEqual(breakers.gauge("memory_bytes", 1000).verdict, TRIP)
        self.assertEqual(breakers.gauge("memory_bytes", 10).verdict, OK)


# --------------------------------------------------------------------------
# Redaction (D-007 S13.9)
# --------------------------------------------------------------------------

FAKE_SECRETS = {
    "anthropic": "sk-ant-" + "A" * 40,
    "openai": "sk-proj-" + "B" * 40,
    "github": "ghp_" + "C" * 36,
    "aws": "AKIA" + "D" * 16,
    "slack": "xoxb-" + "1" * 20,
    "bearer": "Bearer " + "E" * 40,
}


class RedactionTests(TempCase):
    def test_every_seeded_secret_class_is_masked(self) -> None:
        for label, secret in FAKE_SECRETS.items():
            result = redact_text(f"prefix {secret} suffix")
            self.assertNotIn(secret, result.value, f"{label} survived redaction")
            self.assertGreaterEqual(result.count, 1)

    def test_sensitive_keys_are_masked_whatever_the_value_looks_like(self) -> None:
        result = redact_structure({"api_key": "plain-not-matching-any-pattern",
                                   "nested": {"password": "hunter2"},
                                   "safe": "keep me"})
        self.assertNotIn("plain-not-matching-any-pattern", json.dumps(result.value))
        self.assertNotIn("hunter2", json.dumps(result.value))
        self.assertEqual(result.value["safe"], "keep me")
        self.assertEqual(result.count, 2)

    def test_extra_never_send_literals_are_removed(self) -> None:
        result = redact_text("token is banana-value", extra_literals=["banana-value"])
        self.assertNotIn("banana-value", result.value)
        self.assertIn("never_send", result.labels)

    def test_seeded_secrets_never_reach_the_audit_log_on_disk(self) -> None:
        log = AuditLog(self.tmp / "audit.jsonl", fsync=False)
        log.append("probe", run_id="r1",
                   detail={"note": f"key={FAKE_SECRETS['anthropic']}",
                           "nested": {"authorization": FAKE_SECRETS["bearer"]}},
                   never_send=("machine-specific-literal",))
        raw = (self.tmp / "audit.jsonl").read_text(encoding="utf-8")
        for secret in FAKE_SECRETS.values():
            self.assertNotIn(secret, raw)
        self.assertIn("REDACTED", raw)
        record = json.loads(raw.strip())
        self.assertGreaterEqual(record["redaction_count"], 1)

    def test_empty_sensitive_values_keep_their_shape(self) -> None:
        result = redact_structure({"token": "", "secret": None})
        self.assertEqual(result.value, {"token": "", "secret": None})
        self.assertEqual(result.count, 0)


# --------------------------------------------------------------------------
# Records and schema consistency (D-007 S8.3, S9)
# --------------------------------------------------------------------------


class RecordTests(unittest.TestCase):
    def checkpoint(self, **overrides: object) -> ClaudeCheckpoint:
        base = dict(schema_version="1.0.0", run_id="r", checkpoint_id="c", task_id="t",
                    claude_session_id="s", status="UNIT_COMPLETE", summary="did a thing",
                    starting_sha="a", current_sha="b", branch="task/x", worktree="/w",
                    proposed_next_action="next")
        base.update(overrides)
        return ClaudeCheckpoint(**base)  # type: ignore[arg-type]

    def test_missing_usage_is_unknown_never_zero(self) -> None:
        self.checkpoint().validate()
        with self.assertRaises(RecordError) as ctx:
            self.checkpoint(usage=0).validate()
        self.assertEqual(ctx.exception.code, "usage_zeroed")

    def test_unknown_fields_are_rejected(self) -> None:
        data = self.checkpoint().to_dict()
        data["surprise"] = 1
        with self.assertRaises(RecordError) as ctx:
            ClaudeCheckpoint.from_dict(data)
        self.assertEqual(ctx.exception.code, "unknown_fields")

    def test_decision_validation_rules(self) -> None:
        def decision(**over: object) -> CodexDecision:
            base = dict(schema_version="1.0.0", decision="CONTINUE", reviewed_task_id="t",
                        reviewed_checkpoint_id="c", verified_repo_head="a",
                        verified_origin_main="b", model_used="codex-primary",
                        next_claude_prompt="do the next thing")
            base.update(over)
            return CodexDecision(**base)  # type: ignore[arg-type]

        decision().validate()
        with self.assertRaises(RecordError):
            decision(next_claude_prompt="").validate()
        with self.assertRaises(RecordError):
            decision(decision="STOP_FOR_OWNER", owner_question="").validate()
        with self.assertRaises(RecordError):
            # STOP_FOR_OWNER must carry no executable next prompt.
            decision(decision="STOP_FOR_OWNER", owner_question="q?",
                     next_claude_prompt="go").validate()
        with self.assertRaises(RecordError):
            decision(decision="COMPLETE", next_claude_prompt="").validate()
        with self.assertRaises(RecordError):
            decision(decision="HALT_UNSAFE", next_claude_prompt="").validate()
        decision(decision="ROTATE_SESSION", rotation_reason="context pressure").validate()

    def test_schema_required_lists_match_the_dataclasses(self) -> None:
        pairs = [
            ("claude_checkpoint.schema.json", ClaudeCheckpoint),
            ("codex_decision.schema.json", CodexDecision),
            ("protocol_envelope.schema.json", ProtocolEnvelope),
        ]
        for filename, record_cls in pairs:
            schema = json.loads(
                (PACKAGE_ROOT / "schemas" / filename).read_text(encoding="utf-8"))
            required = set(schema["required"])
            declared = set(record_cls.field_names())
            self.assertTrue(required <= declared,
                            f"{filename} requires fields the dataclass lacks: "
                            f"{sorted(required - declared)}")
            self.assertTrue(set(schema["properties"]) <= declared,
                            f"{filename} documents unknown properties: "
                            f"{sorted(set(schema['properties']) - declared)}")


# --------------------------------------------------------------------------
# CLI (D-007 S12.1)
# --------------------------------------------------------------------------


class CliTests(TempCase):
    def setUp(self) -> None:
        super().setUp()
        self.checkout = self.tmp / "checkout"
        self.checkout.mkdir()
        self.base = self.tmp / "runtime"

    def _common(self) -> list[str]:
        return ["--checkout", str(self.checkout), "--runtime-base", str(self.base)]

    def test_doctor_passes_on_a_clean_environment(self) -> None:
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["doctor", *self._common(), "--json"])
        self.assertEqual(code, 0)

    def test_doctor_human_output_is_readable(self) -> None:
        import contextlib
        import io

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            cli.main(["doctor", *self._common()])
        text = buffer.getvalue()
        self.assertIn("overall: PASS", text)
        # M0-T079: the bounded mode EXISTS now, so `doctor` says what is true -
        # implemented, off by default, and enabled only per launch by the owner.
        self.assertIn("limited-auto: IMPLEMENTED and OFF by default", text)
        self.assertIn("exit codes:", text)
        # C7 (G4 F1): the contract names the reserved codes too, so a caller
        # is never left to infer what 0 and 1 mean.
        self.assertIn("ok=0", text)
        self.assertIn("legacy_halt=1", text)
        self.assertIn("refused_mode=16", text)

    def test_doctor_reports_every_phase1_check(self) -> None:
        import contextlib
        import io

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            cli.main(["doctor", *self._common(), "--json"])
        payload = json.loads(buffer.getvalue())
        names = {check["check"] for check in payload["checks"]}
        for expected in ("python_version", "schemas_present", "prompts_present",
                         "state_machine", "protocol_roundtrip", "hard_deny_enforced",
                         "circuit_breakers", "controller_manifest", "runtime_dir",
                         "journal_integrity", "audit_chain"):
            self.assertIn(expected, names)
        self.assertTrue(payload["ok"])
        self.assertIn("IMPLEMENTED and OFF by default", payload["limited_auto"])
        # The machine-readable refusal contract is part of the doctor report.
        outcomes = {row["outcome"] for row in payload["refusal_contract"]}
        self.assertEqual(outcomes, set(refusals.OUTCOMES))

    def test_doctor_checks_the_timezone_database(self) -> None:
        """V1.1 correction F-5: tzdata is a checked setup dependency."""
        import contextlib
        import io

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = cli.main(["doctor", *self._common(), "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        checks = {c["check"]: c for c in payload["checks"]}
        self.assertIn("timezone_database", checks)
        self.assertTrue(checks["timezone_database"]["ok"])
        self.assertIn("America/New_York", checks["timezone_database"]["detail"])

    def test_a_missing_timezone_database_fails_doctor_closed(self) -> None:
        """V1.1 correction F-5: a fresh machine without tzdata fails at SETUP,
        with a message that names tzdata - not at its first scheduled wake."""
        import contextlib
        import io
        import zoneinfo as real_zoneinfo
        from unittest import mock

        class _BrokenZoneInfo:
            ZoneInfoNotFoundError = real_zoneinfo.ZoneInfoNotFoundError

            @staticmethod
            def ZoneInfo(name):  # noqa: N802 - mirrors the stdlib name
                raise real_zoneinfo.ZoneInfoNotFoundError(f"no time zone found: {name}")

        buffer = io.StringIO()
        with mock.patch.object(cli, "zoneinfo", _BrokenZoneInfo), \
                contextlib.redirect_stdout(buffer):
            code = cli.main(["doctor", *self._common(), "--json"])
        self.assertEqual(code, 1, "an unresolvable timezone database must fail doctor")
        payload = json.loads(buffer.getvalue())
        checks = {c["check"]: c for c in payload["checks"]}
        self.assertFalse(checks["timezone_database"]["ok"])
        self.assertIn("tzdata", checks["timezone_database"]["detail"])
        self.assertIn("first wake", checks["timezone_database"]["detail"])

    def test_doctor_validates_supplied_configuration(self) -> None:
        import contextlib
        import io

        config_path = write(self.tmp / "config.toml", VALID_CONFIG)
        selection_path = write(self.tmp / "model_selection.toml", VALID_SELECTION)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = cli.main(["doctor", *self._common(), "--json",
                             "--config", str(config_path),
                             "--model-selection", str(selection_path)])
        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        names = {c["check"]: c for c in payload["checks"]}
        self.assertTrue(names["model_selection_allowlists"]["ok"])

    def test_doctor_fails_on_a_cross_provider_selection(self) -> None:
        import contextlib
        import io

        config_path = write(self.tmp / "config.toml", VALID_CONFIG)
        bad = VALID_SELECTION.replace('review_model = "codex-primary"',
                                      'review_model = "claude-worker"')
        selection_path = write(self.tmp / "model_selection.toml", bad)
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["doctor", *self._common(), "--json",
                             "--config", str(config_path),
                             "--model-selection", str(selection_path)])
        self.assertEqual(code, 1)

    def test_status_runs_read_only(self) -> None:
        import contextlib
        import io

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = cli.main(["status", *self._common(), "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["current_state"], sm.IDLE)
        self.assertFalse(payload["limited_auto_enabled"])

    def test_no_s12_1_command_is_deferred(self) -> None:
        # Phase 2 update: `pending-approvals` and `verify-controller` became
        # implemented. Phase 3 update: `pause`, `emergency-stop`, `start`,
        # `export-handoff`, and `recovery-status` did too.
        # Phase 4 update: `replay` is implemented, so DEFERRED_COMMANDS is EMPTY
        # and this test inverts - it now pins that nothing is deferred, and that
        # the refusal path still exists so a future command cannot be wired to a
        # silent no-op.
        self.assertEqual(cli.DEFERRED_COMMANDS, {},
                         "every S12.1 command is implemented in phase 4; a newly "
                         "deferred command must be justified here")
        namespace = argparse.Namespace(command="some-future-command")
        with self.assertRaises(NotImplementedError) as ctx:
            cli.cmd_deferred(namespace)
        self.assertIn("not implemented", str(ctx.exception).lower())

    def test_replay_runs_the_corpus_without_any_model_call(self) -> None:
        code = cli.main(["replay", *self._common(), "--json"])
        self.assertEqual(code, 0)

    def test_limited_auto_is_refused_by_name(self) -> None:
        """M0-T079: refused exactly as before, reported as a structured outcome."""
        import contextlib
        import io

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = cli.main(["start", *self._common(), "--mode", "limited-auto"])
        self.assertEqual(code, refusals.EXIT_CODES[refusals.REFUSED_MODE])
        message = stderr.getvalue()
        self.assertIn("limited-auto is DISABLED", message)
        self.assertIn("explicit owner activation", message)
        self.assertNotIn("Traceback", message)

    def test_every_s12_1_command_is_wired(self) -> None:
        parser = cli.build_parser()
        actions = [a for a in parser._actions if hasattr(a, "choices") and a.choices]
        wired = set(actions[0].choices)
        for command in (
            "doctor", "replay", "start", "status", "pause", "resume", "stop",
            "emergency-stop", "verify-controller", "recovery-status", "schedule-status",
            "cancel-scheduled-resume", "autostart-plan", "install-autostart",
            "uninstall-autostart", "pending-approvals", "approve-once", "deny",
            "revoke-all", "set-codex-model", "set-claude-model", "export-handoff",
        ):
            self.assertIn(command, wired)


if __name__ == "__main__":
    unittest.main(verbosity=2)
