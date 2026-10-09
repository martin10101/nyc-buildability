#!/usr/bin/env python3
"""M0-T110 (D-024 Amendment 8, unit K): the Codex discussion channel matrix.

Scenario pack: project-control/reports/M0-T110-codex-channel.md section 4
(K1-K8). Applicable requirements: R231-R240, R246, R248, R249.

Harness reuse: this pack imports the unit-G operator-channel harness
(`OperatorChannelBase`, the answering fake runner, the real-subprocess hook
runner) so the channel is proven under the SAME conventions the accepted
surface was - one harness authority, no divergent fakes.

The owner-typed live zero-context canary stays pending-owner-C1 exactly as
unit G recorded it (R235 honesty); K2 proves the measured block/erase
contract shape and K8 proves the honest-limits statements exist verbatim.

Supervisor-freeze qualifying evidence: D-024-R232/R234.
"""
from __future__ import annotations

import json
import pathlib
import sys
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import codex_channel as cc  # noqa: E402
from tools.agent_supervisor.subagent_contracts import (  # noqa: E402
    assert_worker_text_clean,
)
from tools.test_agent_supervisor_operator_channel import (  # noqa: E402
    HOOK,
    OperatorChannelBase,
    answering_runner,
    run_hook,
)

SKILL = REPO / ".claude" / "skills" / "loop-codex" / "SKILL.md"
SCHEMA = (REPO / "tools" / "agent_supervisor" / "schemas" /
          "codex_discussion_reply.schema.json")
AMENDMENT = (REPO / "project-control" / "directives" /
             "D-024-fable-codex-loop" / "source-008-amendment.md")
OWNER_REPORT = (REPO / "project-control" / "reports" /
                "D-024-amendment-8-owner-report.md")

#: Env that guarantees the hook sees NO provider inputs regardless of the
#: developer shell (empty string = unset for the hook's all-three check).
NO_PROVIDER_ENV = {"SUPERVISOR_CODEX_EXECUTABLE": "",
                   "SUPERVISOR_CONFIG": "",
                   "SUPERVISOR_MODEL_SELECTION": ""}


def good_reply(**overrides) -> dict:
    reply = {"schema_version": "1.0.0",
             "reply": "The rotation seam is healthy; nothing is blocked.",
             "disposition": "ADVICE_ONLY",
             "updated_summary": "Discussed rotation-seam health.",
             "confidence_note": "read from the packet's campaign facts",
             "evidence_refs": ["tools/agent_supervisor/rotation.py",
                               "digest:0d999749"]}
    reply.update(overrides)
    return reply


class CodexChannelBase(OperatorChannelBase):
    """The unit-G harness plus channel-shaped helpers."""

    def setUp(self) -> None:
        super().setUp()
        self._id_counter = iter(range(10_000))

    def turn_kwargs(self, journal, **overrides):
        kwargs = dict(journal=journal, audit=self.audit,
                      executable=sys.executable, checkout=self.checkout,
                      config=self.config, selection=self.selection,
                      window_seconds=30.0,
                      thread_id_factory=lambda: "cxt_" + "a" * 16,
                      message_id_factory=lambda:
                          f"cxm_{next(self._id_counter):016d}")
        kwargs.update(overrides)
        return kwargs

    def continue_kwargs(self, journal, **overrides):
        kwargs = self.turn_kwargs(journal, **overrides)
        kwargs.pop("thread_id_factory", None)
        return kwargs

    def opened_thread(self, journal, *, disposition: str = "ADVICE_ONLY",
                      **overrides) -> cc.TurnOutcome:
        runner = overrides.pop(
            "runner", answering_runner(good_reply(disposition=disposition)))
        outcome = cc.new_thread(
            "How healthy is the current unit?", runner=runner,
            **self.turn_kwargs(journal, **overrides))
        self.assertTrue(outcome.answered, outcome.error_message)
        return outcome


# --------------------------------------------------------------------------
# K1 - the five-subverb surface on the existing CLI (R234)
# --------------------------------------------------------------------------


class K1Surface(CodexChannelBase):
    def test_all_five_subverbs_are_registered_on_the_existing_cli(self) -> None:
        # `codex show` on an unknown id exercises the registered path end to
        # end: a typed refusal, not an argparse error (which would exit 2).
        code, out, _ = self.cli_run("codex", "show", "cxt_missing", "--json")
        self.assertNotEqual(code, 2)
        payload = json.loads(out)
        self.assertEqual(payload["reason_code"], "unknown_thread")
        compact = "".join(
            (REPO / "tools" / "agent_supervisor" /
             "codex_channel_cli.py").read_text(encoding="utf-8").split())
        for verb in ("new", "continue", "show", "promote", "close"):
            self.assertIn(f'add_parser("{verb}"', compact,
                          msg="every subverb is registered")

    def test_new_creates_a_thread_and_returns_reply_and_disposition(self) -> None:
        journal = self.journal()
        try:
            outcome = self.opened_thread(journal)
            self.assertEqual(outcome.thread_id, "cxt_" + "a" * 16)
            self.assertTrue(outcome.message_id.startswith("cxm_"))
            self.assertEqual(outcome.disposition, "ADVICE_ONLY")
            record = cc.show_thread(journal, outcome.thread_id)
            self.assertEqual(record["status"], "open")
            self.assertEqual([m["role"] for m in record["messages"]],
                             ["owner", "codex"])
        finally:
            journal.close()

    def test_continue_appends_to_the_same_thread_with_carried_context(self) -> None:
        journal = self.journal()
        try:
            first = self.opened_thread(journal)
            capture: list = []
            outcome = cc.continue_thread(
                first.thread_id, "And the next seam?",
                runner=answering_runner(good_reply(), capture=capture),
                **self.continue_kwargs(journal))
            self.assertTrue(outcome.answered, outcome.error_message)
            packet = json.loads(capture[0][1]["input_text"])
            self.assertEqual(packet["thread"]["thread_id"], first.thread_id)
            self.assertEqual(packet["thread"]["summary"],
                             "Discussed rotation-seam health.")
            self.assertEqual(len(packet["thread"]["recent_exchanges"]), 2)
            record = cc.show_thread(journal, first.thread_id)
            self.assertEqual(len(record["messages"]), 4)
        finally:
            journal.close()

    def test_show_prints_the_durable_record_without_a_provider_call(self) -> None:
        journal = self.journal()
        try:
            first = self.opened_thread(journal)
        finally:
            journal.close()
        code, out, _ = self.cli_run("codex", "show", first.thread_id)
        self.assertEqual(code, 0)
        self.assertIn(first.thread_id, out)
        self.assertIn("owner", out)
        self.assertIn("(ADVICE_ONLY)", out)

    def test_a_concurrent_thread_write_loses_cleanly_via_cas(self) -> None:
        # The single-winner property (the unit-F CAS convention): a row
        # changed between load and store makes THIS turn fail typed - the
        # concurrent write is never silently overwritten.
        journal = self.journal()
        try:
            first = self.opened_thread(journal)
            inner = answering_runner(good_reply())

            def interloping_runner(argv, **kwargs):
                stored = journal.get_state(
                    cc.THREAD_KEY_PREFIX + first.thread_id)
                stored["summary"] = "changed by a concurrent writer"
                journal.set_state(
                    cc.THREAD_KEY_PREFIX + first.thread_id, stored)
                return inner(argv, **kwargs)

            with self.assertRaises(cc.ChannelError) as ctx:
                cc.continue_thread(first.thread_id, "racing message",
                                   runner=interloping_runner,
                                   **self.continue_kwargs(journal))
            self.assertEqual(ctx.exception.code, "thread_conflict")
            record = cc.show_thread(journal, first.thread_id)
            self.assertEqual(record["summary"],
                             "changed by a concurrent writer")
        finally:
            journal.close()

    def test_close_is_durable_and_continue_after_close_refuses(self) -> None:
        journal = self.journal()
        try:
            first = self.opened_thread(journal)
            closed = cc.close_thread(journal, first.thread_id)
            self.assertFalse(closed["already_closed"])
            again = cc.close_thread(journal, first.thread_id)
            self.assertTrue(again["already_closed"])
            with self.assertRaises(cc.ChannelError) as ctx:
                cc.continue_thread(first.thread_id, "more?",
                                   runner=answering_runner(good_reply()),
                                   **self.continue_kwargs(journal))
            self.assertEqual(ctx.exception.code, "thread_closed")
        finally:
            journal.close()


# --------------------------------------------------------------------------
# K2 - pre-model interception (R233/R235) - real hook subprocess
# --------------------------------------------------------------------------


class K2Interception(unittest.TestCase):
    def payload(self, prompt: str, event: str = "UserPromptSubmit") -> dict:
        return {"hook_event_name": event, "cwd": str(REPO), "prompt": prompt}

    def test_exact_loop_codex_is_intercepted_blocked_and_erased(self) -> None:
        code, out = run_hook(self.payload("/loop-codex show cxt_nothere"),
                             env_extra=NO_PROVIDER_ENV)
        self.assertEqual(code, 0)
        decision = json.loads(out)
        self.assertEqual(set(decision), {"decision", "reason"})
        self.assertEqual(decision["decision"], "block")
        self.assertIn("unknown_thread", decision["reason"])

    def test_similar_text_passes_through_untouched(self) -> None:
        for prompt in ("loop-codex new hi", "/loop-codexes new hi",
                       "tell me about /loop-codex new hi",
                       "/loop-codex-new hi"):
            code, out = run_hook(self.payload(prompt),
                                 env_extra=NO_PROVIDER_ENV)
            self.assertEqual((code, out), (0, ""), prompt)

    def test_missing_or_unknown_subverb_blocks_with_usage(self) -> None:
        for prompt in ("/loop-codex", "/loop-codex frobnicate x"):
            code, out = run_hook(self.payload(prompt),
                                 env_extra=NO_PROVIDER_ENV)
            self.assertEqual(code, 0, prompt)
            decision = json.loads(out)
            self.assertEqual(decision["decision"], "block")
            self.assertIn("/loop-codex new <question>", decision["reason"])

    def test_new_and_continue_fail_closed_without_provider_inputs(self) -> None:
        for prompt in ("/loop-codex new is the seam healthy?",
                       "/loop-codex continue cxt_abc more detail please"):
            code, out = run_hook(self.payload(prompt),
                                 env_extra=NO_PROVIDER_ENV)
            self.assertEqual(code, 0, prompt)
            decision = json.loads(out)
            self.assertEqual(decision["decision"], "block")
            self.assertIn("SUPERVISOR_CODEX_EXECUTABLE", decision["reason"])
            self.assertIn("Second-terminal path", decision["reason"])
            self.assertIn("codex", decision["reason"])

    def test_id_only_subverbs_execute_without_provider_inputs(self) -> None:
        code, out = run_hook(self.payload("/loop-codex promote cxm_nothere"),
                             env_extra=NO_PROVIDER_ENV)
        self.assertEqual(code, 0)
        decision = json.loads(out)
        self.assertEqual(decision["decision"], "block")
        self.assertIn("unknown_message_id", decision["reason"])

    def test_extra_text_after_an_id_only_subverb_refuses_visibly(self) -> None:
        code, out = run_hook(
            self.payload("/loop-codex close cxt_abc and also stop"),
            env_extra=NO_PROVIDER_ENV)
        self.assertEqual(code, 0)
        decision = json.loads(out)
        self.assertEqual(decision["decision"], "block")
        self.assertIn("exactly one id", decision["reason"])
        self.assertIn("nothing was executed", decision["reason"])

    def test_the_unproven_expansion_event_passes_through_unfaked(self) -> None:
        code, out = run_hook(
            self.payload("/loop-codex show cxt_abc",
                         event="UserPromptExpansion"),
            env_extra=NO_PROVIDER_ENV)
        self.assertEqual((code, out), (0, ""))

    def test_close_executes_without_provider_inputs(self) -> None:
        # G4 MINOR-4: the clean no-provider round trip for `close` itself.
        code, out = run_hook(self.payload("/loop-codex close cxt_nothere"),
                             env_extra=NO_PROVIDER_ENV)
        self.assertEqual(code, 0)
        decision = json.loads(out)
        self.assertEqual(decision["decision"], "block")
        self.assertIn("unknown_thread", decision["reason"])

    def test_an_option_shaped_id_is_refused_before_any_execution(self) -> None:
        # G3 MINOR-1 / G5 ADVISORY-1: ids are data, never options - an
        # option-shaped token is a visible hook refusal, not a downstream
        # argparse surprise.
        for prompt in ("/loop-codex show --checkout=C:/Windows",
                       "/loop-codex promote --help",
                       "/loop-codex close -rf"):
            code, out = run_hook(self.payload(prompt),
                                 env_extra=NO_PROVIDER_ENV)
            self.assertEqual(code, 0, prompt)
            decision = json.loads(out)
            self.assertEqual(decision["decision"], "block")
            self.assertIn("not a cxt_/cxm_ id", decision["reason"])
            self.assertIn("nothing was executed", decision["reason"])

    def test_free_text_rides_behind_the_end_of_options_separator(self) -> None:
        # G4 MINOR-1: exercise the argv-construction line directly (every
        # subprocess test blocks earlier on missing provider env). A message
        # with a leading dash, metacharacters, quotes, and newlines is ONE
        # argv element behind an explicit "--".
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "loop_hook_under_test", str(HOOK))
        hook_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hook_mod)
        env = {"SUPERVISOR_CODEX_EXECUTABLE": "C:/fake/codex.exe",
               "SUPERVISOR_CONFIG": "C:/fake/config.toml",
               "SUPERVISOR_MODEL_SELECTION": "C:/fake/selection.toml"}
        hostile = '-rf; rm -rf / $(whoami) "quoted" line1\nline2'
        with mock.patch.dict("os.environ", env):
            argv, reason = hook_mod._codex_argv(f"new {hostile}")
            self.assertEqual(reason, "")
            self.assertEqual(argv[-2:], ["--", hostile])
            argv, reason = hook_mod._codex_argv(
                f"continue cxt_abc123 {hostile}")
            self.assertEqual(reason, "")
            self.assertEqual(argv[-2:], ["--", hostile])
            self.assertIn("cxt_abc123", argv)
            self.assertLess(argv.index("cxt_abc123"), argv.index("--"))

    def test_no_btw_equivalence_claim_anywhere(self) -> None:
        hook_text = HOOK.read_text(encoding="utf-8")
        skill_text = SKILL.read_text(encoding="utf-8")
        module_text = (REPO / "tools" / "agent_supervisor" /
                       "codex_channel.py").read_text(encoding="utf-8")
        for text, name in ((hook_text, "hook"), (skill_text, "skill"),
                           (module_text, "module")):
            self.assertNotIn("btw-equivalent", text.lower().replace("/", ""),
                             msg=f"{name} must not claim /btw equivalence")
        self.assertIn("QUEUED until the turn ends", skill_text)
        self.assertIn("second terminal", skill_text.lower())


# --------------------------------------------------------------------------
# K3 - the bounded per-turn packet (R236/R237/R238)
# --------------------------------------------------------------------------


class K3BoundedContext(CodexChannelBase):
    def packet_for(self, journal, thread=None, message="hello") -> dict:
        thread = thread or {"thread_id": "cxt_" + "b" * 16, "summary": "",
                            "messages": []}
        return cc.build_turn_packet(journal, checkout=self.checkout,
                                    thread=thread, message=message,
                                    campaigns=[])

    def test_the_packet_carries_exactly_the_r236_set(self) -> None:
        journal = self.journal()
        try:
            packet = self.packet_for(journal)
        finally:
            journal.close()
        self.assertEqual(
            set(packet),
            {"schema_version", "kind", "thread", "message", "campaigns",
             "state", "reference_guidance", "instruction"})
        self.assertEqual(set(packet["thread"]),
                         {"thread_id", "summary", "recent_exchanges"})

    def test_recent_exchanges_are_bounded(self) -> None:
        journal = self.journal()
        try:
            thread = {"thread_id": "cxt_" + "b" * 16, "summary": "s",
                      "messages": [
                          {"message_id": f"cxm_{i:016d}", "role": "owner",
                           "text": f"m{i}", "disposition": ""}
                          for i in range(12)]}
            packet = self.packet_for(journal, thread=thread)
        finally:
            journal.close()
        recents = packet["thread"]["recent_exchanges"]
        self.assertEqual(len(recents), cc.MAX_RECENT_EXCHANGES)
        self.assertEqual(recents[-1]["text"], "m11")

    def test_the_byte_ceiling_trims_visibly_then_fails_closed(self) -> None:
        journal = self.journal()
        try:
            thread = {"thread_id": "cxt_" + "b" * 16, "summary": "s",
                      "messages": [
                          {"message_id": f"cxm_{i:016d}", "role": "owner",
                           "text": "x" * 200, "disposition": ""}
                          for i in range(6)]}
            with mock.patch.object(cc, "MAX_PACKET_BYTES", 10 ** 9):
                full = self.packet_for(journal, thread=thread)
            full_size = len(json.dumps(full, ensure_ascii=False)
                            .encode("utf-8"))
            # A ceiling just below the full size forces dropping at least one
            # exchange (each is ~230 bytes) - visibly.
            with mock.patch.object(cc, "MAX_PACKET_BYTES", full_size - 100):
                packet = self.packet_for(journal, thread=thread)
                self.assertIn("omitted_for_size", packet)
                self.assertTrue(
                    any(o.startswith("exchange:")
                        for o in packet["omitted_for_size"]))
            with mock.patch.object(cc, "MAX_PACKET_BYTES", 400), \
                    self.assertRaises(cc.ChannelError) as ctx:
                self.packet_for(journal, thread=thread, message="y" * 300)
            self.assertEqual(ctx.exception.code, "packet_too_large")
        finally:
            journal.close()

    def test_an_oversized_provider_summary_is_bounded_on_store(self) -> None:
        journal = self.journal()
        try:
            outcome = self.opened_thread(
                journal, runner=answering_runner(
                    good_reply(updated_summary="s" * 10_000)))
            record = cc.show_thread(journal, outcome.thread_id)
            self.assertLessEqual(len(record["summary"]),
                                 cc.MAX_SUMMARY_CHARS)
            self.assertIn("[truncated]", record["summary"])
        finally:
            journal.close()

    def test_an_empty_summary_update_keeps_the_prior_summary(self) -> None:
        journal = self.journal()
        try:
            first = self.opened_thread(journal)
            outcome = cc.continue_thread(
                first.thread_id, "more?",
                runner=answering_runner(good_reply(updated_summary="")),
                **self.continue_kwargs(journal))
            self.assertTrue(outcome.answered)
            record = cc.show_thread(journal, first.thread_id)
            self.assertEqual(record["summary"],
                             "Discussed rotation-seam health.")
        finally:
            journal.close()

    def test_a_full_thread_refuses_continue_with_guidance(self) -> None:
        journal = self.journal()
        try:
            first = self.opened_thread(journal)
            record = cc.show_thread(journal, first.thread_id)
            padded = dict(record)
            padded["messages"] = record["messages"] + [
                {"message_id": f"cxm_pad{i:013d}", "role": "owner",
                 "text": "pad", "disposition": "", "at_utc": ""}
                for i in range(cc.MAX_THREAD_MESSAGES)]
            journal.set_state(cc.THREAD_KEY_PREFIX + first.thread_id, padded)
            with self.assertRaises(cc.ChannelError) as ctx:
                cc.continue_thread(first.thread_id, "one more?",
                                   runner=answering_runner(good_reply()),
                                   **self.continue_kwargs(journal))
            self.assertEqual(ctx.exception.code, "thread_full")
            self.assertIn("new thread", ctx.exception.message)
        finally:
            journal.close()

    def test_stable_reference_guidance_over_bare_line_numbers(self) -> None:
        journal = self.journal()
        try:
            packet = self.packet_for(journal)
        finally:
            journal.close()
        self.assertIn("never bare line numbers", packet["reference_guidance"])
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertIn("never bare line numbers",
                      schema["properties"]["evidence_refs"]["description"])

    def test_the_instruction_is_worker_text_clean_and_scoped(self) -> None:
        journal = self.journal()
        try:
            packet = self.packet_for(journal)
        finally:
            journal.close()
        assert_worker_text_clean("codex_turn_instruction",
                                 packet["instruction"])
        for prohibited in ("full conversation transcript",
                           "whole repository", "full logs"):
            self.assertIn(prohibited, packet["instruction"],
                          msg="the instruction names the prohibited bulk "
                              "content explicitly (R237)")


# --------------------------------------------------------------------------
# K4 - the closed disposition vocabulary (R239)
# --------------------------------------------------------------------------


class K4Dispositions(CodexChannelBase):
    def test_an_unknown_or_missing_disposition_is_a_typed_failure(self) -> None:
        journal = self.journal()
        try:
            for bad in ({"disposition": "DO_IT_NOW"},
                        {"disposition": ""},):
                outcome = cc.new_thread(
                    "q?", runner=answering_runner(good_reply(**bad)),
                    **self.turn_kwargs(journal))
                self.assertFalse(outcome.answered)
                self.assertEqual(outcome.error_code, "disposition_invalid")
            # Nothing was persisted for the failed turns (no partial rows).
            self.assertEqual(
                [k for k in journal.all_state()
                 if k.startswith(cc.THREAD_KEY_PREFIX)], [])
        finally:
            journal.close()

    def test_each_disposition_produces_exactly_its_decided_effect(self) -> None:
        journal = self.journal()
        try:
            for i, disposition in enumerate(cc.DISPOSITIONS):
                outcome = cc.new_thread(
                    f"case {disposition}?",
                    runner=answering_runner(
                        good_reply(disposition=disposition)),
                    **self.turn_kwargs(
                        journal,
                        thread_id_factory=lambda i=i: f"cxt_{i:016d}"))
                self.assertTrue(outcome.answered, outcome.error_message)
                self.assertEqual(outcome.disposition, disposition)
                self.assertEqual(outcome.guidance,
                                 cc.DISPOSITION_GUIDANCE[disposition])
            state = journal.all_state()
            queue = state.get(cc.BOUNDARY_QUEUE_KEY, [])
            self.assertEqual(len(queue), 1)
            attention = [k for k in state
                         if k.startswith(cc.ATTENTION_KEY_PREFIX)]
            self.assertEqual(len(attention), 2)
            for key in attention:
                self.assertFalse(state[key]["actuated"])
            promotions = [k for k in state
                          if k.startswith(cc.PROMOTION_KEY_PREFIX)]
            self.assertEqual(promotions, [])
        finally:
            journal.close()

    def test_urgent_and_stop_name_the_exact_command_and_actuate_nothing(
            self) -> None:
        journal = self.journal()
        try:
            before = set(journal.all_state())
            outcome = self.opened_thread(journal,
                                         disposition="URGENT_PAUSE")
            self.assertIn("python -m tools.agent_supervisor pause",
                          outcome.guidance)
            self.assertIn("Nothing was paused automatically",
                          outcome.guidance)
            added = set(journal.all_state()) - before
            self.assertTrue(all(k.startswith("codex_channel/")
                                for k in added),
                            msg=f"only channel rows may be written: {added}")
        finally:
            journal.close()

    def test_the_module_imports_no_actuation_surface(self) -> None:
        source = (REPO / "tools" / "agent_supervisor" /
                  "codex_channel.py").read_text(encoding="utf-8")
        for forbidden in ("stop_intent", "repair_gate", "project_control",
                          "github_flow", "external_effects"):
            self.assertNotIn(forbidden, source,
                             msg=f"codex_channel must not touch {forbidden}")

    def test_a_full_boundary_queue_is_a_visible_refusal_not_a_drop(self) -> None:
        journal = self.journal()
        try:
            journal.set_state(cc.BOUNDARY_QUEUE_KEY,
                              [{"pad": i}
                               for i in range(cc.MAX_BOUNDARY_QUEUE)])
            outcome = self.opened_thread(journal,
                                         disposition="QUEUE_NEXT_BOUNDARY")
            self.assertEqual(outcome.queue_result, "queue_full")
            record = cc.show_thread(journal, outcome.thread_id)
            self.assertEqual(len(record["messages"]), 2,
                             msg="the reply itself is still recorded")
            self.assertEqual(
                len(journal.get_state(cc.BOUNDARY_QUEUE_KEY)),
                cc.MAX_BOUNDARY_QUEUE)
        finally:
            journal.close()


# --------------------------------------------------------------------------
# K5 - owner-gated promotion (R240)
# --------------------------------------------------------------------------


class K5Promotion(CodexChannelBase):
    def promoted_message(self, journal) -> str:
        outcome = self.opened_thread(journal,
                                     disposition="PROPOSE_NEW_TASK")
        return outcome.message_id

    def test_promote_records_one_idempotent_durable_row(self) -> None:
        journal = self.journal()
        try:
            message_id = self.promoted_message(journal)
            first = cc.promote_message(journal, self.audit, message_id)
            self.assertFalse(first["already_promoted"])
            self.assertEqual(first["status"], "recorded_awaiting_capture")
            self.assertTrue(first["authorizes_nothing"])
            self.assertIn("/directive-compliance", first["required_next"])
            second = cc.promote_message(journal, self.audit, message_id)
            self.assertTrue(second["already_promoted"])
            rows = [k for k in journal.all_state()
                    if k.startswith(cc.PROMOTION_KEY_PREFIX)]
            self.assertEqual(len(rows), 1)
        finally:
            journal.close()

    def test_unknown_ids_and_non_promotable_messages_refuse(self) -> None:
        journal = self.journal()
        try:
            with self.assertRaises(cc.ChannelError) as ctx:
                cc.promote_message(journal, self.audit, "cxt_wrongprefix")
            self.assertEqual(ctx.exception.code, "not_a_message_id")
            with self.assertRaises(cc.ChannelError) as ctx:
                cc.promote_message(journal, self.audit, "cxm_" + "f" * 16)
            self.assertEqual(ctx.exception.code, "unknown_message_id")
            advice = self.opened_thread(journal, disposition="ADVICE_ONLY")
            with self.assertRaises(cc.ChannelError) as ctx:
                cc.promote_message(journal, self.audit, advice.message_id)
            self.assertEqual(ctx.exception.code, "not_promotable")
        finally:
            journal.close()

    def test_promotion_touches_only_channel_state(self) -> None:
        journal = self.journal()
        try:
            message_id = self.promoted_message(journal)
            before = set(journal.all_state())
            cc.promote_message(journal, self.audit, message_id)
            added = set(journal.all_state()) - before
            self.assertEqual(added,
                             {cc.PROMOTION_KEY_PREFIX + message_id})
        finally:
            journal.close()

    def test_the_promotion_surface_is_owner_typed_by_construction(self) -> None:
        skill_text = SKILL.read_text(encoding="utf-8")
        self.assertIn("disable-model-invocation: true", skill_text)
        self.assertIn("promote", skill_text)


# --------------------------------------------------------------------------
# K6 - bridge security (reused hardening)
# --------------------------------------------------------------------------


class K6Security(CodexChannelBase):
    def test_empty_oversized_and_non_text_messages_refuse_typed(self) -> None:
        journal = self.journal()
        try:
            cases = (("", "empty_question"),
                     ("x" * 5_000, "question_too_large"),
                     (12345, "question_not_text"),
                     (None, "question_not_text"))
            for text, code in cases:
                with self.assertRaises(cc.ChannelError) as ctx:
                    cc.new_thread(text,
                                  runner=answering_runner(good_reply()),
                                  **self.turn_kwargs(journal))
                self.assertEqual(ctx.exception.code, code)
        finally:
            journal.close()

    def test_a_secret_inside_the_reply_is_redacted_before_store_and_display(
            self) -> None:
        # G4 MINOR-3: the INBOUND direction - a hostile/careless provider
        # reply carrying a secret-looking string never reaches the stored
        # thread or the displayed outcome unredacted.
        journal = self.journal()
        try:
            secret = "ghp_ZYXWVUTSRQPONMLKJIHGFEDCBA9876543210ab"  # gitleaks:allow secretscan:allow fake token proving inbound redaction, leak-absence test
            outcome = self.opened_thread(
                journal, runner=answering_runner(good_reply(
                    reply=f"the token is {secret} - rotate it",
                    updated_summary=f"summary leaks {secret} too")))
            self.assertNotIn(secret, outcome.reply)
            record = cc.show_thread(journal, outcome.thread_id)
            self.assertNotIn(secret, json.dumps(record))
        finally:
            journal.close()

    def test_control_sequences_and_secrets_never_reach_the_packet(self) -> None:
        journal = self.journal()
        try:
            capture: list = []
            outcome = cc.new_thread(
                "check \x1b[31mthis\x1b[0m token "
                "ghp_0123456789abcdefghijklmnopqrstuvwxyzAB",  # secretscan:allow fake token proving redaction, leak-absence test
                runner=answering_runner(good_reply(), capture=capture),
                **self.turn_kwargs(journal))
            self.assertTrue(outcome.answered, outcome.error_message)
            self.assertGreater(outcome.redactions, 0)
            packet_text = capture[0][1]["input_text"]
            self.assertNotIn("\x1b", packet_text)
            self.assertNotIn("ghp_0123456789", packet_text)
        finally:
            journal.close()

    def test_identity_and_tamper_refusals(self) -> None:
        journal = self.journal()
        try:
            foreign = self.tmp / "elsewhere"
            foreign.mkdir()
            with self.assertRaises(cc.ChannelError) as ctx:
                cc.new_thread("q?", runner=answering_runner(good_reply()),
                              **self.turn_kwargs(journal, checkout=foreign))
            self.assertEqual(ctx.exception.code, "identity_mismatch")
            record_path = (self.checkout / "project-control" / "campaigns" /
                           "D-024-fable-codex-loop.json")
            record_path.write_text("{\"schema\": \"nope\"}", encoding="utf-8")
            with self.assertRaises(cc.ChannelError) as ctx:
                cc.new_thread("q?", runner=answering_runner(good_reply()),
                              **self.turn_kwargs(journal))
            self.assertEqual(ctx.exception.code, "campaign_record_invalid")
        finally:
            journal.close()

    def test_the_turn_rides_the_hardened_read_only_argv(self) -> None:
        journal = self.journal()
        try:
            capture: list = []
            self.opened_thread(journal, runner=answering_runner(
                good_reply(), capture=capture))
            argv = capture[0][0]
            self.assertIn("exec", argv)
            self.assertIn("--sandbox", argv)
            self.assertEqual(argv[argv.index("--sandbox") + 1], "read-only")
            schema_arg = argv[argv.index("--output-schema") + 1]
            self.assertTrue(schema_arg.endswith(
                "codex_discussion_reply.schema.json"))
        finally:
            journal.close()

    def test_a_timeout_terminates_the_tree_and_keeps_the_owner_message(
            self) -> None:
        journal = self.journal()
        try:
            outcome = cc.new_thread(
                "slow question?",
                runner=answering_runner(None, timed_out=True),
                **self.turn_kwargs(journal))
            self.assertFalse(outcome.answered)
            self.assertTrue(outcome.timed_out)
            self.assertTrue(outcome.tree_terminated)
            record = cc.show_thread(journal, outcome.thread_id)
            self.assertEqual([m["role"] for m in record["messages"]],
                             ["owner"])
        finally:
            journal.close()

    def test_malformed_replies_are_typed_never_echoed(self) -> None:
        journal = self.journal()
        try:
            outcome = cc.new_thread(
                "q?", runner=answering_runner({"reply": ""}),
                **self.turn_kwargs(journal))
            self.assertFalse(outcome.answered)
            self.assertEqual(outcome.error_code, "reply_empty")
            self.assertEqual(outcome.reply, "")
        finally:
            journal.close()

    def test_the_audit_trail_is_privacy_bounded(self) -> None:
        journal = self.journal()
        try:
            self.opened_thread(journal)
        finally:
            journal.close()
        audit_text = (self.tmp / "audit.jsonl").read_text(encoding="utf-8")
        self.assertIn("codex_channel_turn", audit_text)
        self.assertIn("reply_digest", audit_text)
        self.assertNotIn("rotation seam is healthy", audit_text)
        self.assertNotIn("How healthy is the current unit", audit_text)


# --------------------------------------------------------------------------
# K7 - the user-only skill
# --------------------------------------------------------------------------


class K7Skill(unittest.TestCase):
    def test_the_skill_exists_user_only_thin_and_honest(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("disable-model-invocation: true", text)
        self.assertLess(len(text.splitlines()), 60)
        self.assertIn("intercepted", text)
        self.assertIn("consumed context", text)
        self.assertIn("exactly one command", text)
        self.assertIn("NOT the built-in `/loop`", text)


# --------------------------------------------------------------------------
# K8 - the executable requirement register (R249 pattern)
# --------------------------------------------------------------------------


class K8RequirementRegister(CodexChannelBase):
    """One executable row per applicable Amendment-8 requirement."""

    def test_R231_the_amendment_is_captured_verbatim(self) -> None:
        text = AMENDMENT.read_text(encoding="utf-8")
        self.assertIn("---VERBATIM-BEGIN---", text)
        self.assertIn("---VERBATIM-END---", text)
        self.assertIn("D-024-R231..D-024-R249", text)

    def test_R232_the_pre_activation_hold_is_recorded_in_the_campaign(
            self) -> None:
        record = json.loads(
            (REPO / "project-control" / "campaigns" /
             "D-024-fable-codex-loop.json").read_text(encoding="utf-8"))
        joined = " ".join(record["restrictions"])
        for needle in ("M0-T110", "M0-T111", "M0-T112", "R187"):
            self.assertIn(needle, joined)

    def test_R233_honest_interception_limits(self) -> None:
        K2Interception("test_no_btw_equivalence_claim_anywhere").run()
        skill_text = SKILL.read_text(encoding="utf-8")
        self.assertIn("QUEUED until the turn ends", skill_text)

    def test_R234_the_five_subverb_surface_exists(self) -> None:
        compact = "".join(
            (REPO / "tools" / "agent_supervisor" /
             "codex_channel_cli.py").read_text(encoding="utf-8").split())
        for subverb in ("new", "continue", "show", "promote", "close"):
            self.assertIn(f'add_parser("{subverb}"', compact)
        _, out, _ = self.cli_run("codex", "show", "cxt_missing", "--json")
        self.assertEqual(json.loads(out)["reason_code"], "unknown_thread")

    def test_R235_blocked_and_erased_before_the_model(self) -> None:
        code, out = run_hook({"hook_event_name": "UserPromptSubmit",
                              "cwd": str(REPO),
                              "prompt": "/loop-codex show cxt_x"},
                             env_extra=NO_PROVIDER_ENV)
        self.assertEqual(code, 0)
        self.assertEqual(set(json.loads(out)), {"decision", "reason"})

    def test_R236_the_turn_context_is_exactly_the_bounded_set(self) -> None:
        journal = self.journal()
        try:
            packet = cc.build_turn_packet(
                journal, checkout=self.checkout,
                thread={"thread_id": "cxt_" + "c" * 16, "summary": "",
                        "messages": []},
                message="m", campaigns=[])
        finally:
            journal.close()
        self.assertEqual(
            set(packet),
            {"schema_version", "kind", "thread", "message", "campaigns",
             "state", "reference_guidance", "instruction"})

    def test_R237_no_bulk_content_and_a_hard_ceiling(self) -> None:
        source = (REPO / "tools" / "agent_supervisor" /
                  "codex_channel.py").read_text(encoding="utf-8")
        self.assertIn("MAX_PACKET_BYTES", source)
        self.assertIn("packet_too_large", source)
        for reuse in ("sanitize_question", "validate_identity",
                      "redact_structure", "build_argv", "minimal_env"):
            self.assertIn(reuse, source)

    def test_R238_stable_references_preferred(self) -> None:
        K3BoundedContext(
            "test_stable_reference_guidance_over_bare_line_numbers").run()
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertIn("commit SHAs",
                      schema["properties"]["evidence_refs"]["description"])

    def test_R239_closed_dispositions_and_no_automatic_change(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(tuple(schema["properties"]["disposition"]["enum"]),
                         cc.DISPOSITIONS)
        self.assertEqual(len(cc.DISPOSITIONS), 6)

    def test_R240_promotion_is_owner_gated_and_captures_nothing_itself(
            self) -> None:
        journal = self.journal()
        try:
            message_id = self.opened_thread(
                journal, disposition="PROPOSE_NEW_TASK").message_id
            row = cc.promote_message(journal, self.audit, message_id)
            self.assertTrue(row["authorizes_nothing"])
            self.assertIn("D-024-R240", row["required_next"])
        finally:
            journal.close()

    def test_R246_the_bounded_task_sequence_is_captured_durably(self) -> None:
        for task_id in ("M0-T110", "M0-T111", "M0-T112"):
            self.assertTrue(
                (REPO / "project-control" / "tasks" /
                 f"{task_id}.json").exists(), task_id)

    def test_R248_the_unit_touches_no_prohibited_surface(self) -> None:
        for module in ("codex_channel.py", "codex_channel_cli.py"):
            source = (REPO / "tools" / "agent_supervisor" /
                      module).read_text(encoding="utf-8")
            for forbidden in ("settings.json", "mcp", "urllib", "requests",
                              "socket", "agent_dispatch_guard",
                              "readonly_agent_guard"):
                self.assertNotIn(forbidden, source.lower(),
                                 msg=f"{module} must not touch {forbidden}")

    def test_R249_the_first_report_answers_the_five_items(self) -> None:
        text = OWNER_REPORT.read_text(encoding="utf-8")
        for heading in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5."):
            self.assertIn(heading, text)


if __name__ == "__main__":
    unittest.main()
