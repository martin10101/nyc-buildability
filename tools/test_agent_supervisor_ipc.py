#!/usr/bin/env python3
"""Model-change IPC tests (D-007 Section 15 "model selection", S3.2 rules 2 and 6).

Covers the rule-6 half of that family:

* the controller-owned IPC endpoint REJECTS worker- and reviewer-originated
  requests, including anything descending from their process trees
* a caller failing the OS access-control / isolation check is rejected
* an UNCONFIRMED change is never applied
* a confirmation captured for one change cannot be replayed against another
* the change applies only at a checkpoint boundary and never resets task state
* the complete audit record is written
* a `model_selection.toml` edit OUTSIDE that path is detected, refused, and
  pauses (S4.5)
* editing the runtime selection never trips the controller manifest, while the
  immutable config does live inside it
* `--codex-model` (S3.2 rule 2) goes through the same authenticated path
* a model outside its OWN provider's allowlist is refused

Named-pipe support is PROBED (created and closed) on Windows so the claim in
`NAMED_PIPE_STATUS` is measured rather than asserted.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import model_change_ipc as ipc  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.config import (  # noqa: E402
    load_controller_config,
    load_model_selection,
)
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.manifest import generate_manifest  # noqa: E402

CONFIG_TOML = """
[controller]
default_mode = "shadow"

[codex]
allowed_models = ["codex-primary", "codex-fallback"]

[claude]
allowed_models = ["claude-primary"]
"""

SELECTION_TOML = """
[codex]
review_model = "codex-primary"
advisory_model = ""
fallback_models = ["codex-fallback"]

[claude]
model = "claude-primary"
fallback_models = []
"""


class IpcBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = pathlib.Path(self._tmp.name).resolve()
        self.runtime = self.root / "runtime"
        self.worktree = self.root / "worktree"
        self.runtime.mkdir()
        self.worktree.mkdir()

        self.config_path = self.root / "config.toml"
        self.selection_path = self.root / "model_selection.toml"
        self.config_path.write_text(CONFIG_TOML, encoding="utf-8")
        self.selection_path.write_text(SELECTION_TOML, encoding="utf-8")

        self.journal = DurableJournal(self.runtime / "journal.sqlite3").open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.runtime / "audit.jsonl", fsync=False)
        self.config = load_controller_config(self.config_path)
        self.selection = load_model_selection(self.selection_path)

        self.endpoint = ipc.ModelChangeEndpoint(
            journal=self.journal, config=self.config,
            selection_path=self.selection_path, runtime_dir=self.runtime,
            checkout_key="k" * 64, audit=self.audit,
            controller_pid=os.getpid(),
            worker_writable_roots=(str(self.worktree),))
        self.endpoint.record_selection_digest(self.selection.digest())

    def controller_caller(self) -> ipc.Caller:
        return ipc.Caller(pid=os.getpid(), account="owner",
                          channel=self.endpoint.plan.channel)

    def confirming_prompt(self, request: ipc.ModelChangeRequest):
        return lambda message: request.challenge()

    def request_change(self, *, prompt, provider="codex", model="codex-fallback",
                       at_checkpoint=True, caller=None) -> ipc.ChangeOutcome:
        return self.endpoint.request_change(
            caller=caller or self.controller_caller(), provider=provider,
            new_model=model, old_model="codex-primary",
            after_selection_digest=self.selection.digest(), run_id="run-1",
            task_id="M0-T036", prompt=prompt, at_checkpoint_boundary=at_checkpoint)


# --------------------------------------------------------------------------
# The endpoint itself
# --------------------------------------------------------------------------


class EndpointTests(IpcBase):
    def test_the_plan_describes_a_restrictive_channel(self) -> None:
        plan = self.endpoint.plan
        self.assertIn(plan.channel, (ipc.CHANNEL_NAMED_PIPE, ipc.CHANNEL_FILE_ENDPOINT))
        self.assertIn("D:P(", plan.sddl, "the DACL is protected (no inherited ACEs)")
        self.assertIn("(A;;GA;;;SY)", plan.sddl, "SYSTEM is admitted")

    def test_the_display_form_masks_the_account_sid(self) -> None:
        plan = ipc.endpoint_plan(checkout_key="k" * 64, runtime_dir=str(self.runtime))
        redacted = plan.redacted()
        if plan.owner_sid:
            self.assertNotIn(plan.owner_sid, redacted["sddl"])
            self.assertNotIn(plan.owner_sid, str(redacted["owner_sid"]))

    def test_a_file_endpoint_inside_a_worker_root_is_refused(self) -> None:
        with self.assertRaises(ipc.IpcError) as raised:
            ipc.assert_endpoint_isolated(self.worktree / "ipc", (str(self.worktree),))
        self.assertEqual(raised.exception.code, "endpoint_reachable_by_worker")

    def test_an_endpoint_outside_every_worker_root_is_accepted(self) -> None:
        ipc.assert_endpoint_isolated(self.runtime / "ipc", (str(self.worktree),))

    @unittest.skipUnless(os.name == "nt", "named pipes are a Windows transport")
    def test_a_restricted_named_pipe_can_actually_be_created(self) -> None:
        probe = ipc.probe_named_pipe_support(checkout_key="unittestprobe")
        self.assertTrue(probe.supported, probe.detail)
        self.assertIn("SDDL-restricted", probe.detail)
        self.assertNotIn("S-1-5-21-1", probe.detail.replace("S-1-5-21-...", ""),
                         "the full account SID must not appear in the probe detail")

    def test_the_named_pipe_status_states_what_is_deferred(self) -> None:
        self.assertIn("PROVEN", ipc.NAMED_PIPE_STATUS)
        self.assertIn("DEFERRED", ipc.NAMED_PIPE_STATUS)


# --------------------------------------------------------------------------
# Origin denial
# --------------------------------------------------------------------------


class OriginDenialTests(IpcBase):
    def test_a_recorded_worker_pid_is_denied(self) -> None:
        ipc.record_worker_pid(self.journal, os.getpid(), role="worker")
        with self.assertRaises(ipc.IpcError) as raised:
            ipc.assert_caller_allowed(self.controller_caller(), journal=self.journal)
        self.assertEqual(raised.exception.code, "worker_origin_denied")
        self.assertIn("worker", raised.exception.message)

    def test_a_recorded_reviewer_pid_is_denied(self) -> None:
        ipc.record_worker_pid(self.journal, os.getpid(), role="reviewer")
        with self.assertRaises(ipc.IpcError) as raised:
            ipc.assert_caller_allowed(self.controller_caller(), journal=self.journal)
        self.assertEqual(raised.exception.code, "worker_origin_denied")
        self.assertIn("reviewer", raised.exception.message)

    def test_a_descendant_of_a_worker_is_denied_not_just_the_leaf(self) -> None:
        """This process's real parent stands in for a recorded worker."""
        parent = ipc.parent_pid(os.getpid())
        if parent <= 0:
            self.skipTest("this platform did not report a parent pid")
        ipc.record_worker_pid(self.journal, parent, role="worker")
        with self.assertRaises(ipc.IpcError) as raised:
            ipc.assert_caller_allowed(self.controller_caller(), journal=self.journal)
        self.assertEqual(raised.exception.code, "worker_origin_denied")
        self.assertIn("descends from", raised.exception.message)

    def test_the_controller_itself_is_allowed(self) -> None:
        chain = ipc.assert_caller_allowed(self.controller_caller(), journal=self.journal,
                                          controller_pid=os.getpid())
        self.assertIsInstance(chain, tuple)

    def test_an_unrelated_caller_is_denied(self) -> None:
        stranger = ipc.Caller(pid=999999, account="someone")
        with self.assertRaises(ipc.IpcError) as raised:
            ipc.assert_caller_allowed(stranger, journal=self.journal,
                                      controller_pid=os.getpid())
        self.assertEqual(raised.exception.code, "unrelated_caller")
        self.assertIn("NOT automatically owner-authenticated", raised.exception.message)

    def test_a_request_arriving_through_a_worker_path_is_denied(self) -> None:
        caller = ipc.Caller(pid=os.getpid(),
                            arrived_via_path=str(self.worktree / "request.json"))
        with self.assertRaises(ipc.IpcError) as raised:
            ipc.assert_caller_allowed(caller, journal=self.journal,
                                      worker_writable_roots=(str(self.worktree),))
        self.assertEqual(raised.exception.code, "endpoint_reachable_by_worker")

    def test_the_ancestry_walk_is_bounded(self) -> None:
        chain = ipc.ancestry(os.getpid(), max_depth=3)
        self.assertLessEqual(len(chain), 3)

    def test_an_invalid_pid_has_no_parent(self) -> None:
        self.assertEqual(ipc.parent_pid(0), 0)
        self.assertEqual(ipc.parent_pid(-1), 0)


# --------------------------------------------------------------------------
# Confirmation and application
# --------------------------------------------------------------------------


class ConfirmationTests(IpcBase):
    def request(self, **overrides) -> ipc.ModelChangeRequest:
        data = {"provider": "codex", "old_model": "codex-primary",
                "new_model": "codex-fallback", "scope": ipc.SCOPE_PERSISTENT,
                "run_id": "r", "task_id": "t", "before_selection_digest": "x",
                "after_selection_digest": "y"}
        data.update(overrides)
        return ipc.ModelChangeRequest(**data)

    def test_the_display_shows_provider_models_and_digests(self) -> None:
        display = self.request().display()
        for expected in ("provider", "codex", "current model", "requested model",
                         "selection digest before", "selection digest after"):
            self.assertIn(expected, display)

    def test_a_bare_yes_never_confirms(self) -> None:
        request = self.request()
        confirmation = ipc.confirm_interactively(request, prompt=lambda message: "y")
        self.assertFalse(confirmation.confirmed)

    def test_the_challenge_confirms(self) -> None:
        request = self.request()
        confirmation = ipc.confirm_interactively(
            request, prompt=lambda message: request.challenge())
        self.assertTrue(confirmation.confirmed)
        self.assertEqual(confirmation.request_digest, request.digest())

    def test_a_confirmation_for_a_different_change_cannot_be_replayed(self) -> None:
        first = self.request()
        second = self.request(new_model="codex-primary")
        self.assertNotEqual(first.challenge(), second.challenge())
        stolen = ipc.confirm_interactively(first,
                                           prompt=lambda message: first.challenge())
        with self.assertRaises(ipc.IpcError) as raised:
            self.endpoint.apply_change(second, confirmation=stolen,
                                       caller=self.controller_caller())
        self.assertEqual(raised.exception.code, "confirmation_not_bound")

    def test_apply_change_refuses_an_unconfirmed_confirmation(self) -> None:
        request = self.request()
        refused = ipc.confirm_interactively(request, prompt=lambda message: "no")
        with self.assertRaises(ipc.IpcError) as raised:
            self.endpoint.apply_change(request, confirmation=refused,
                                       caller=self.controller_caller())
        self.assertEqual(raised.exception.code, "unconfirmed_change")

    def test_an_unknown_provider_is_refused_at_construction(self) -> None:
        with self.assertRaises(ipc.IpcError):
            self.request(provider="gemini")

    def test_an_empty_model_is_refused_at_construction(self) -> None:
        with self.assertRaises(ipc.IpcError):
            self.request(new_model="")


class GatedChangeTests(IpcBase):
    def test_an_unconfirmed_change_is_never_applied(self) -> None:
        outcome = self.request_change(prompt=lambda message: "y")
        self.assertFalse(outcome.applied)
        self.assertEqual(outcome.reason_code, "unconfirmed")
        self.assertIsNone(self.journal.get_state(ipc.RUN_OVERRIDE_KEY))

    def test_a_confirmed_change_off_a_checkpoint_boundary_is_held(self) -> None:
        captured: dict = {}

        def prompt(message: str) -> str:
            captured["message"] = message
            return message.split("token to proceed: ")[1].split("\n")[0].strip()

        outcome = self.request_change(prompt=prompt, at_checkpoint=False)
        self.assertFalse(outcome.applied)
        self.assertEqual(outcome.reason_code, "not_at_checkpoint_boundary")

    def test_a_confirmed_change_at_a_checkpoint_boundary_applies(self) -> None:
        def prompt(message: str) -> str:
            return message.split("token to proceed: ")[1].split("\n")[0].strip()

        outcome = self.request_change(prompt=prompt)
        self.assertTrue(outcome.applied)
        self.assertEqual(outcome.reason_code, "applied")

    def test_the_audit_record_is_complete(self) -> None:
        def prompt(message: str) -> str:
            return message.split("token to proceed: ")[1].split("\n")[0].strip()

        outcome = self.request_change(prompt=prompt)
        record = outcome.audit_record
        for field in ("caller", "channel", "confirmation", "provider", "old_model",
                      "new_model", "before_selection_digest", "after_selection_digest",
                      "run_id", "task_id", "request_digest"):
            self.assertIn(field, record, f"the audit record omits {field}")
        self.assertTrue(record["confirmation"]["confirmed"])
        events = [json.loads(line) for line in
                  (self.runtime / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertTrue(any(e["event_type"] == "model_change_applied" for e in events))

    def test_a_change_never_resets_task_state(self) -> None:
        self.journal.set_state("current_state", "CHECKPOINT_RECEIVED")
        self.journal.set_state("rotation_pending", True)

        def prompt(message: str) -> str:
            return message.split("token to proceed: ")[1].split("\n")[0].strip()

        self.request_change(prompt=prompt)
        self.assertEqual(self.journal.get_state("current_state"), "CHECKPOINT_RECEIVED")
        self.assertTrue(self.journal.get_state("rotation_pending"))

    def test_a_model_outside_its_own_allowlist_is_refused(self) -> None:
        with self.assertRaises(ipc.IpcError) as raised:
            self.request_change(prompt=lambda m: "y", model="claude-primary")
        self.assertEqual(raised.exception.code, "model_not_allowlisted")

    def test_a_claude_entry_never_satisfies_the_codex_list(self) -> None:
        request = ipc.ModelChangeRequest(
            provider="codex", old_model="", new_model="claude-primary",
            scope=ipc.SCOPE_PERSISTENT, run_id="r", task_id="t",
            before_selection_digest="x", after_selection_digest="y")
        with self.assertRaises(ipc.IpcError):
            ipc.assert_allowlisted(request, self.config)

    def test_a_worker_originated_change_is_denied_before_anything_else(self) -> None:
        ipc.record_worker_pid(self.journal, os.getpid(), role="worker")
        with self.assertRaises(ipc.IpcError) as raised:
            self.request_change(prompt=lambda m: "y")
        self.assertEqual(raised.exception.code, "worker_origin_denied")


# --------------------------------------------------------------------------
# The --codex-model per-run override (rule 2)
# --------------------------------------------------------------------------


class RunOverrideTests(IpcBase):
    def prompt(self, message: str) -> str:
        return message.split("token to proceed: ")[1].split("\n")[0].strip()

    def test_the_override_goes_through_the_same_authenticated_path(self) -> None:
        outcome = self.endpoint.request_run_override(
            caller=self.controller_caller(), provider="codex", model="codex-fallback",
            current_model="codex-primary", run_id="run-1", task_id="M0-T036",
            prompt=self.prompt)
        self.assertTrue(outcome.applied)
        self.assertEqual(self.endpoint.active_run_override("codex", "run-1"),
                         "codex-fallback")

    def test_an_unconfirmed_override_is_not_installed(self) -> None:
        outcome = self.endpoint.request_run_override(
            caller=self.controller_caller(), provider="codex", model="codex-fallback",
            current_model="codex-primary", run_id="run-1", task_id="t",
            prompt=lambda message: "yes")
        self.assertFalse(outcome.applied)
        self.assertEqual(self.endpoint.active_run_override("codex", "run-1"), "")

    def test_an_override_is_scoped_to_its_own_run(self) -> None:
        self.endpoint.request_run_override(
            caller=self.controller_caller(), provider="codex", model="codex-fallback",
            current_model="codex-primary", run_id="run-1", task_id="t",
            prompt=self.prompt)
        self.assertEqual(self.endpoint.active_run_override("codex", "run-2"), "")
        self.assertEqual(self.endpoint.active_run_override("claude", "run-1"), "")

    def test_an_override_outside_the_allowlist_is_refused(self) -> None:
        with self.assertRaises(ipc.IpcError):
            self.endpoint.request_run_override(
                caller=self.controller_caller(), provider="codex",
                model="some-other-model", current_model="codex-primary", run_id="r",
                task_id="t", prompt=self.prompt)

    def test_the_override_is_recorded_in_every_decision_record(self) -> None:
        fields = ipc.decision_record_fields(model_used="codex-fallback",
                                            override_active=True,
                                            selection_digest="d" * 64)
        self.assertTrue(fields["single_run_override_active"])
        self.assertEqual(fields["model_used"], "codex-fallback")
        self.assertEqual(fields["model_selection_digest"], "d" * 64)

    def test_clearing_the_override_removes_it(self) -> None:
        self.endpoint.request_run_override(
            caller=self.controller_caller(), provider="codex", model="codex-fallback",
            current_model="codex-primary", run_id="run-1", task_id="t",
            prompt=self.prompt)
        self.endpoint.clear_run_override()
        self.assertEqual(self.endpoint.active_run_override("codex", "run-1"), "")


# --------------------------------------------------------------------------
# Out-of-band tampering and the manifest boundary
# --------------------------------------------------------------------------


class OutOfBandTests(IpcBase):
    def test_an_unchanged_selection_is_not_tampering(self) -> None:
        self.assertFalse(self.endpoint.check_tampering().detected)

    def test_an_edit_outside_the_authenticated_path_is_detected_and_pauses(self) -> None:
        self.selection_path.write_text(
            SELECTION_TOML.replace("codex-primary", "codex-fallback"), encoding="utf-8")
        verdict = self.endpoint.check_tampering()
        self.assertTrue(verdict.detected)
        self.assertEqual(verdict.reason_code, "out_of_band_model_selection_change")
        self.assertTrue(verdict.synchronous_stop)

    def test_a_change_request_refuses_while_tampering_stands(self) -> None:
        self.selection_path.write_text(
            SELECTION_TOML.replace("codex-primary", "codex-fallback"), encoding="utf-8")
        outcome = self.request_change(prompt=lambda m: "y")
        self.assertFalse(outcome.applied)
        self.assertEqual(outcome.reason_code, "out_of_band_model_selection_change")

    def test_no_baseline_is_not_tampering(self) -> None:
        verdict = ipc.detect_out_of_band_change(recorded_digest="", current_digest="x")
        self.assertFalse(verdict.detected)

    def test_the_runtime_selection_is_outside_the_controller_manifest(self) -> None:
        manifest = generate_manifest(REPO / "tools" / "agent_supervisor")
        ok, detail = ipc.manifest_unaffected(manifest)
        self.assertTrue(ok, detail)
        self.assertIn("never invalidates the controller", detail)

    def test_a_manifest_covering_the_runtime_selection_would_be_rejected(self) -> None:
        ok, detail = ipc.manifest_unaffected({"files": {"model_selection.toml": "d"}})
        self.assertFalse(ok)
        self.assertIn("explicitly forbids", detail)

    def test_a_runtime_model_change_does_not_alter_the_manifest_digest(self) -> None:
        package = REPO / "tools" / "agent_supervisor"
        before = generate_manifest(package)["manifest_digest"]
        # The runtime selection lives outside the package and is excluded anyway;
        # writing it must not move the controller's digest.
        self.selection_path.write_text(SELECTION_TOML + "\n# edited\n", encoding="utf-8")
        after = generate_manifest(package)["manifest_digest"]
        self.assertEqual(before, after)


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
