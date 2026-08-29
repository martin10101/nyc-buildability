#!/usr/bin/env python3
"""M0-T111 (D-024 Amendment 8, unit L): the one-way Telegram sink matrix.

Scenario pack: project-control/reports/M0-T111-telegram-sink.md section 4
(L1-L8). Applicable requirements: R231, R232, R241-R245, R246, R248, R249.

Harness reuse: the unit-G operator-channel base (journal/audit/CLI runner) -
one harness authority, exactly as the unit-K pack did.

No test in this pack ever opens a socket: the real transport is only ever
constructed with an injected fake opener (L6.3), and every delivery test
injects a fake transport. The live send stays an owner-gated exact-command
canary this unit never fires (R245).

Supervisor-freeze qualifying evidence: D-024-R232/R241.
"""
from __future__ import annotations

import json
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import telegram_sink as ts  # noqa: E402
from tools.agent_supervisor.codex_channel import (  # noqa: E402
    ATTENTION_KEY_PREFIX,
)
from tools.agent_supervisor.notifications import (  # noqa: E402
    DELIVERED_KEY,
    QUEUE_KEY,
)
from tools.agent_supervisor.resume_scheduler import (  # noqa: E402
    LIMIT_RECORD_KEY,
)
from tools.test_agent_supervisor_operator_channel import (  # noqa: E402
    OperatorChannelBase,
)

AMENDMENT = (REPO / "project-control" / "directives" /
             "D-024-fable-codex-loop" / "source-008-amendment.md")
OWNER_REPORT = (REPO / "project-control" / "reports" /
                "D-024-amendment-8-owner-report.md")
SINK_SOURCE = (REPO / "tools" / "agent_supervisor" / "telegram_sink.py")
CLI_SOURCE = (REPO / "tools" / "agent_supervisor" / "telegram_sink_cli.py")

#: Deliberately fake sentinels (leak-absence pattern). Never real.
FAKE_TOKEN = "0000000000:FAKE-sentinel-bot-token-for-leak-absence"  # gitleaks:allow secretscan:allow fake sentinel proving credential leak-absence
FAKE_CHAT = "FAKE-chat-id-sentinel-887766"
FAKE_ENV = {ts.TOKEN_ENV: FAKE_TOKEN, ts.CHAT_ID_ENV: FAKE_CHAT}


def fake_transport(*, ok: bool = True, detail: str = "sent (2xx)",
                   fail_first: int = 0, raise_error: Exception | None = None,
                   capture: list | None = None) -> ts.Transport:
    """A transport double: succeeds, fails N times first, or raises."""
    calls = {"n": 0}

    def transport(credentials: ts.Credentials, text: str,
                  timeout: float) -> tuple[bool, str]:
        calls["n"] += 1
        if capture is not None:
            capture.append({"token": credentials.bot_token,
                            "chat_id": credentials.chat_id,
                            "text": text, "timeout": timeout})
        if raise_error is not None:
            raise raise_error
        if calls["n"] <= fail_first:
            return False, "telegram responded with status bucket 5xx"
        return ok, detail

    return transport


class TelegramBase(OperatorChannelBase):
    def sink(self, transport: ts.Transport, **overrides) -> ts.TelegramSink:
        kwargs: dict = dict(env=FAKE_ENV, timeout=5.0)
        kwargs.update(overrides)
        return ts.TelegramSink(transport, **kwargs)

    def notify(self, journal, sink: ts.TelegramSink, *,
               condition: str = "golden_run_complete",
               summary: str = "the two-unit golden run completed cleanly",
               task_id: str = "M0-T111") -> ts.NotifyOutcome:
        return ts.notify_condition(
            journal, self.audit, condition=condition, summary=summary,
            where_to_review="project-control/reports (golden-run evidence)",
            sink=sink, run_id="run-1", task_id=task_id)


# --------------------------------------------------------------------------
# L1 - the closed condition vocabulary (R241)
# --------------------------------------------------------------------------


class L1Conditions(TelegramBase):
    def test_all_eight_conditions_accepted_with_fixed_risk_classes(self) -> None:
        self.assertEqual(len(ts.CONDITIONS), 8)
        self.assertEqual(set(ts.CONDITION_RISK), set(ts.CONDITIONS))
        journal = self.journal()
        try:
            for i, condition in enumerate(ts.CONDITIONS):
                outcome = self.notify(
                    journal, self.sink(fake_transport()),
                    condition=condition, summary=f"case {i}: {condition}")
                self.assertTrue(outcome.delivered, outcome.detail)
            delivered = journal.get_state(DELIVERED_KEY, [])
            self.assertEqual(len(delivered), 8)
        finally:
            journal.close()

    def test_an_unknown_condition_is_a_typed_refusal(self) -> None:
        journal = self.journal()
        try:
            with self.assertRaises(ts.TelegramError) as ctx:
                self.notify(journal, self.sink(fake_transport()),
                            condition="do_something_new")
            self.assertEqual(ctx.exception.code, "unknown_condition")
            self.assertEqual(journal.get_state(QUEUE_KEY, []), [])
        finally:
            journal.close()

    def test_discovery_finds_exactly_the_durable_sources_read_only(self) -> None:
        journal = self.journal()
        try:
            self.assertEqual(ts.discover_conditions(journal), ())
            journal.set_state(ATTENTION_KEY_PREFIX + "cxm_feedbeef", {
                "disposition": "STOP_FOR_OWNER", "actuated": False,
                "message_id": "cxm_feedbeef"})
            journal.set_state(ATTENTION_KEY_PREFIX + "cxm_handled0", {
                "disposition": "STOP_FOR_OWNER", "actuated": True,
                "message_id": "cxm_handled0"})
            journal.set_state(ATTENTION_KEY_PREFIX + "cxm_paused01", {
                "disposition": "URGENT_PAUSE", "actuated": False,
                "message_id": "cxm_paused01"})
            journal.set_state(LIMIT_RECORD_KEY, {"kind": "usage_limit"})
            before = dict(journal.all_state())
            found = ts.discover_conditions(journal)
            self.assertEqual(sorted(f["condition"] for f in found),
                             ["quota_refusal_hold", "stop_for_owner"])
            stop_rows = [f for f in found
                         if f["condition"] == "stop_for_owner"]
            self.assertEqual([f["reference"] for f in stop_rows],
                             ["cxm_feedbeef"],
                             msg="only the STOP_FOR_OWNER row that is not "
                                 "yet actuated is discovered")
            self.assertEqual(dict(journal.all_state()), before,
                             msg="discovery is read-only")
        finally:
            journal.close()


# --------------------------------------------------------------------------
# L2 - the S13.10 view-only boundary is the ONLY composition path
# --------------------------------------------------------------------------


class L2ViewOnly(TelegramBase):
    def test_leak_shapes_are_refused_not_sent(self) -> None:
        journal = self.journal()
        try:
            cases = (
                "review at https://example.com/auth?token=abc",
                "$ git push --force origin main",
                "```python\nsecret = 1\n```",
            )
            for bad_summary in cases:
                outcome = self.notify(journal, self.sink(fake_transport()),
                                      summary=bad_summary)
                self.assertFalse(outcome.delivered, bad_summary)
                self.assertTrue(outcome.error_code.startswith(
                    "notification_would_leak"), outcome.error_code)
            self.assertEqual(journal.get_state(QUEUE_KEY, []), [])
        finally:
            journal.close()

    def test_the_summary_is_hard_bounded_and_text_redacted(self) -> None:
        journal = self.journal()
        try:
            capture: list = []
            outcome = self.notify(
                journal, self.sink(fake_transport(capture=capture)),
                summary="x" * 2_000)
            self.assertTrue(outcome.delivered)
            sent_text = capture[0]["text"]
            self.assertLess(len(sent_text), 700,
                            msg="outbound text is bounded by the builder")
        finally:
            journal.close()


# --------------------------------------------------------------------------
# L3 - secrets (R243): env-only, never in any artifact
# --------------------------------------------------------------------------


class L3Secrets(TelegramBase):
    def test_missing_env_is_a_typed_skip_item_stays_queued(self) -> None:
        journal = self.journal()
        try:
            sink = self.sink(fake_transport(), env={})
            outcome = self.notify(journal, sink)
            self.assertFalse(outcome.delivered)
            self.assertTrue(outcome.still_queued)
            self.assertIn("telegram_not_configured", outcome.detail)
            self.assertEqual(len(journal.get_state(QUEUE_KEY, [])), 1)
        finally:
            journal.close()

    def test_sentinel_secrets_never_reach_any_stored_or_shown_artifact(
            self) -> None:
        journal = self.journal()
        try:
            outcome = self.notify(journal, self.sink(fake_transport()))
            self.assertTrue(outcome.delivered)
            artifacts = [
                json.dumps(outcome.to_dict()),
                json.dumps(journal.get_state(QUEUE_KEY, [])),
                json.dumps(journal.get_state(DELIVERED_KEY, [])),
                json.dumps(journal.get_state(ts.DEDUP_KEY, [])),
                (self.tmp / "audit.jsonl").read_text(encoding="utf-8"),
            ]
        finally:
            journal.close()
        for text in artifacts:
            self.assertNotIn(FAKE_TOKEN, text)
            self.assertNotIn(FAKE_CHAT, text)

    def test_credential_holder_and_errors_are_secret_free(self) -> None:
        creds = ts.resolve_credentials(FAKE_ENV)
        self.assertNotIn(FAKE_TOKEN, repr(creds))
        self.assertNotIn(FAKE_CHAT, str(creds))
        with self.assertRaises(ts.TelegramError) as ctx:
            ts.resolve_credentials({})
        self.assertNotIn(FAKE_TOKEN, ctx.exception.message)
        journal = self.journal()
        try:
            outcome = self.notify(
                journal,
                self.sink(fake_transport(raise_error=OSError("boom"))))
            self.assertFalse(outcome.delivered)
            self.assertNotIn(FAKE_TOKEN, outcome.detail)
            self.assertNotIn("api.telegram.org", outcome.detail,
                             msg="details never carry the URL (it embeds "
                                 "the token)")
        finally:
            journal.close()

    def test_cli_status_reports_presence_only(self) -> None:
        code, out, _ = self.cli_run("telegram", "status", "--json")
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertIn(payload["configured"], (True, False))
        self.assertNotIn(FAKE_TOKEN, out)
        self.assertNotIn(FAKE_CHAT, out)


# --------------------------------------------------------------------------
# L4 - one-way only (R242)
# --------------------------------------------------------------------------


class L4OneWay(unittest.TestCase):
    @staticmethod
    def functional_text(path: pathlib.Path) -> str:
        """Identifiers + code string literals, EXCLUDING docstrings/comments:
        the honest documentation legitimately NAMES the banned capabilities
        ("no getUpdates, no webhook"), so the scan targets functional source."""
        import ast
        tree = ast.parse(path.read_text(encoding="utf-8"))
        docstrings: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)):
                body = getattr(node, "body", [])
                if body and isinstance(body[0], ast.Expr) and \
                        isinstance(body[0].value, ast.Constant) and \
                        isinstance(body[0].value.value, str):
                    docstrings.add(id(body[0].value))
        parts: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                parts.append(node.id)
            elif isinstance(node, ast.Attribute):
                parts.append(node.attr)
            elif isinstance(node, ast.Constant) and \
                    isinstance(node.value, str) and id(node) not in docstrings:
                parts.append(node.value)
        return "\n".join(parts).lower()

    def test_no_receive_or_command_surface_exists(self) -> None:
        for path in (SINK_SOURCE, CLI_SOURCE):
            functional = self.functional_text(path)
            for forbidden in ("getupdates", "webhook", "setwebhook",
                              "getme", "long_poll", "subprocess", "exec(",
                              "eval("):
                self.assertNotIn(forbidden, functional,
                                 msg=f"{path.name} must not carry {forbidden}")
        cli_source = CLI_SOURCE.read_text(encoding="utf-8")
        self.assertIn("no Telegram approvals, merges, execution", cli_source)
        self.assertIn("sendmessage",
                      self.functional_text(SINK_SOURCE),
                      msg="the transport speaks sendMessage")
        self.assertNotIn("sendmessage", self.functional_text(CLI_SOURCE),
                         msg="only the sink module carries the API method")


# --------------------------------------------------------------------------
# L5 - bounded retries, dedup, failure isolation (R244)
# --------------------------------------------------------------------------


class L5Isolation(TelegramBase):
    def test_all_attempts_fail_bounded_then_queued_never_raises(self) -> None:
        journal = self.journal()
        try:
            calls: list = []
            sink = self.sink(fake_transport(fail_first=99, capture=calls))
            outcome = self.notify(journal, sink)
            self.assertFalse(outcome.delivered)
            self.assertTrue(outcome.still_queued)
            self.assertEqual(outcome.attempts, ts.MAX_DELIVERY_ATTEMPTS)
            self.assertEqual(len(calls), ts.MAX_DELIVERY_ATTEMPTS)
            self.assertEqual(len(journal.get_state(QUEUE_KEY, [])), 1)
        finally:
            journal.close()

    def test_a_raising_transport_is_contained(self) -> None:
        journal = self.journal()
        try:
            outcome = self.notify(
                journal,
                self.sink(fake_transport(raise_error=TimeoutError())))
            self.assertFalse(outcome.delivered)
            self.assertIn("TimeoutError", outcome.detail)
            self.assertTrue(outcome.still_queued)
        finally:
            journal.close()

    def test_success_after_a_failure_delivers_and_dequeues(self) -> None:
        journal = self.journal()
        try:
            outcome = self.notify(journal,
                                  self.sink(fake_transport(fail_first=1)))
            self.assertTrue(outcome.delivered)
            self.assertEqual(outcome.attempts, 2)
            self.assertEqual(journal.get_state(QUEUE_KEY, []), [])
        finally:
            journal.close()

    def test_exact_duplicates_are_visibly_deduplicated(self) -> None:
        journal = self.journal()
        try:
            first = self.notify(journal, self.sink(fake_transport()))
            self.assertTrue(first.delivered)
            second = self.notify(journal, self.sink(fake_transport()))
            self.assertTrue(second.deduplicated)
            self.assertFalse(second.delivered)
            self.assertEqual(len(journal.get_state(DELIVERED_KEY, [])), 1)
            changed = self.notify(journal, self.sink(fake_transport()),
                                  summary="a DIFFERENT durable fact")
            self.assertTrue(changed.delivered)
        finally:
            journal.close()

    def test_the_dedup_register_is_fifo_bounded(self) -> None:
        journal = self.journal()
        try:
            for i in range(ts.DEDUP_MAX_ENTRIES + 5):
                ts._dedup_record(journal, f"digest-{i}")
            entries = journal.get_state(ts.DEDUP_KEY, [])
            self.assertEqual(len(entries), ts.DEDUP_MAX_ENTRIES)
            self.assertEqual(entries[0]["digest"], "digest-5")
        finally:
            journal.close()

    def test_no_telegram_path_can_pause_the_run(self) -> None:
        # Structural: unit_can_proceed=True rides every deliver call, so
        # run_must_pause can never be set by this sink.
        source = SINK_SOURCE.read_text(encoding="utf-8")
        self.assertIn("unit_can_proceed=True", source)
        self.assertNotIn("unit_can_proceed=False", source)
        journal = self.journal()
        try:
            sink = self.sink(fake_transport(fail_first=99))
            outcome = self.notify(journal, sink,
                                  condition="unrecovered_controller_failure",
                                  summary="controller down and unrecovered")
            self.assertFalse(outcome.delivered)
            lines = [json.loads(line) for line in
                     (self.tmp / "audit.jsonl").read_text(encoding="utf-8")
                     .splitlines() if line.strip()]
            failures = [e for e in lines
                        if e.get("event_type") == "notification_delivery_failed"]
            self.assertTrue(failures)
            self.assertIs(failures[-1]["detail"]["run_must_pause"], False)
        finally:
            journal.close()


# --------------------------------------------------------------------------
# L6 - the owner-gated live send (R245)
# --------------------------------------------------------------------------


class L6OwnerGatedCanary(TelegramBase):
    def test_the_real_transport_is_owner_gated(self) -> None:
        with self.assertRaises(ts.TelegramError) as ctx:
            ts.build_real_transport()
        self.assertEqual(ctx.exception.code, "live_send_owner_gated")
        self.assertIn(ts.LIVE_CANARY_COMMAND, ctx.exception.message)
        self.assertIn("D-024-R245", ctx.exception.message)

    def test_cli_canary_refuses_without_the_owner_flag(self) -> None:
        code, out, _ = self.cli_run("telegram", "canary", "--json")
        self.assertNotEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["reason_code"], "live_send_owner_gated")
        self.assertIn(ts.LIVE_CANARY_COMMAND, payload["message"])

    def test_authorized_transport_shape_without_a_socket(self) -> None:
        captured: dict = {}

        class FakeResponse:
            status = 200

        def fake_opener(request, timeout=None):
            captured["url"] = request.full_url
            captured["body"] = request.data.decode("utf-8")
            captured["timeout"] = timeout
            return FakeResponse()

        transport = ts.build_real_transport(live_send_authorized=True,
                                            opener=fake_opener)
        ok, detail = transport(ts.Credentials(FAKE_TOKEN, FAKE_CHAT),
                               "canary text", 5.0)
        self.assertTrue(ok)
        self.assertIn("2xx", detail)
        self.assertTrue(captured["url"].startswith(
            f"https://api.telegram.org/bot{FAKE_TOKEN}/sendMessage"))
        self.assertIn("chat_id=", captured["body"])
        self.assertEqual(captured["timeout"], 5.0)

    def test_a_non_2xx_status_is_a_bucketed_failure(self) -> None:
        class FakeResponse:
            status = 502

        transport = ts.build_real_transport(
            live_send_authorized=True,
            opener=lambda request, timeout=None: FakeResponse())
        ok, detail = transport(ts.Credentials(FAKE_TOKEN, FAKE_CHAT), "t", 5.0)
        self.assertFalse(ok)
        self.assertIn("5xx", detail)
        self.assertNotIn(FAKE_TOKEN, detail)


# --------------------------------------------------------------------------
# L7 - the CLI surface
# --------------------------------------------------------------------------


class L7Cli(TelegramBase):
    def test_status_is_registered_and_redacted(self) -> None:
        code, out, _ = self.cli_run("telegram", "status")
        self.assertEqual(code, 0)
        self.assertIn("one-way only", out)
        self.assertIn("presence only", out)
        self.assertIn(ts.LIVE_CANARY_COMMAND, out)


# --------------------------------------------------------------------------
# L8 - the executable requirement register (R249 pattern)
# --------------------------------------------------------------------------


class L8RequirementRegister(TelegramBase):
    def test_R231_the_amendment_is_captured_verbatim(self) -> None:
        text = AMENDMENT.read_text(encoding="utf-8")
        self.assertIn("---VERBATIM-BEGIN---", text)
        self.assertIn("TELEGRAM REQUIREMENTS", text)

    def test_R232_the_pre_activation_hold_is_recorded(self) -> None:
        record = json.loads(
            (REPO / "project-control" / "campaigns" /
             "D-024-fable-codex-loop.json").read_text(encoding="utf-8"))
        joined = " ".join(record["restrictions"])
        for needle in ("M0-T111", "M0-T112", "R187"):
            self.assertIn(needle, joined)

    def test_R241_the_bounded_sink_covers_exactly_the_eight(self) -> None:
        verbatim = AMENDMENT.read_text(encoding="utf-8")
        # The amendment's eight bullet conditions all map into CONDITIONS.
        for owner_words, condition in (
                ("STOP_FOR_OWNER", "stop_for_owner"),
                ("approval waiting", "approval_waiting"),
                ("circuit-breaker/open stuck state", "breaker_open_stuck"),
                ("repeated CI failure", "repeated_ci_failure"),
                ("unrecovered controller/session failure",
                 "unrecovered_controller_failure"),
                ("quota/refusal hold", "quota_refusal_hold"),
                ("golden-run completion", "golden_run_complete"),
                ("campaign completion", "campaign_complete")):
            self.assertIn(owner_words, verbatim)
            self.assertIn(condition, ts.CONDITIONS)
        self.assertEqual(len(ts.CONDITIONS), 8)

    def test_R242_one_way_only(self) -> None:
        L4OneWay("test_no_receive_or_command_surface_exists").run()
        self.assertIn("no Telegram approvals, merges, execution",
                      " ".join(CLI_SOURCE.read_text(encoding="utf-8")
                               .split()))

    def test_R243_secrets_only_in_the_local_mechanism(self) -> None:
        source = SINK_SOURCE.read_text(encoding="utf-8")
        self.assertIn('TOKEN_ENV = "SUPERVISOR_TELEGRAM_BOT_TOKEN"', source)
        self.assertNotIn("open(", source.replace("open_url", "").replace(
            "opener", ""), msg="credentials come from env, never a file")
        L3Secrets("test_sentinel_secrets_never_reach_any_stored_or_shown_"
                  "artifact").run()

    def test_R244_redaction_retries_dedup_isolation(self) -> None:
        for test in ("test_all_attempts_fail_bounded_then_queued_never_raises",
                     "test_a_raising_transport_is_contained",
                     "test_exact_duplicates_are_visibly_deduplicated",
                     "test_no_telegram_path_can_pause_the_run"):
            self.assertTrue(hasattr(L5Isolation, test), test)

    def test_R245_live_send_owner_gated(self) -> None:
        with self.assertRaises(ts.TelegramError):
            ts.build_real_transport()
        self.assertIn("--live-canary-authorized-by-owner",
                      CLI_SOURCE.read_text(encoding="utf-8"))

    def test_R246_the_bounded_task_sequence_is_captured_durably(self) -> None:
        for task_id in ("M0-T110", "M0-T111", "M0-T112"):
            self.assertTrue(
                (REPO / "project-control" / "tasks" /
                 f"{task_id}.json").exists(), task_id)

    def test_R248_no_prohibited_surface(self) -> None:
        for path in (SINK_SOURCE, CLI_SOURCE):
            source = path.read_text(encoding="utf-8").lower()
            for forbidden in ("settings.json", "mcp", "agent_dispatch_guard",
                              "readonly_agent_guard", "requests",
                              "aiohttp", "httpx"):
                self.assertNotIn(forbidden, source,
                                 msg=f"{path.name} must not touch {forbidden}")

    def test_R249_the_first_report_answers_the_five_items(self) -> None:
        text = OWNER_REPORT.read_text(encoding="utf-8")
        for heading in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5."):
            self.assertIn(heading, text)


if __name__ == "__main__":
    unittest.main()
