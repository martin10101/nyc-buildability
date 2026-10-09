"""M0-T099 (D-024 amendment 2, R129-R138): project statusLine handler tests.

Covers the REAL installed-version fixture (live 2.1.220 capture, R131), the
one-feed contract (sanitized sidecar + compact human row from the same record,
R132), occupancy-vs-cumulative and rate-limit-vs-context separation
(R133/R134), documented nullability (R136), and the structural no-model-
message / no-API-token proof (R135; official note verbatim: "The status line
runs locally and does not consume API tokens" -
https://code.claude.com/docs/en/statusline).

Deterministic; no network; installs nothing.

Supervisor-freeze qualifying evidence: D-024-R100 + D-024-R131/R132.
"""
from __future__ import annotations

import io
import json
import pathlib

from tools.agent_supervisor import telemetry_journal as tj
from tools.agent_supervisor import telemetry_status as tst
from tools.agent_supervisor import telemetry_statusline as tsl

FIXTURES = pathlib.Path(__file__).parent / "agent_supervisor" / "fixtures"
LIVE_FIXTURE = FIXTURES / "statusline_live_2026-08-26.json"
NOW = "2026-08-26T12:00:00+00:00"

DOC_URL = "https://code.claude.com/docs/en/statusline"


def _fixture() -> dict:
    return json.loads(LIVE_FIXTURE.read_text(encoding="utf-8"))


def _startup_payload() -> dict:
    return _fixture()["payloads"]["startup_pre_first_response"]


def _post_payload() -> dict:
    return _fixture()["payloads"]["post_first_response_with_rate_limits"]


# ---------- REAL installed-version fixture (R129/R131) ----------------------

def test_live_fixture_installed_version_proof():
    """R131: the committed fixture is a live 2.1.220 capture, and R129/R138:
    it carries the official doc URL as primary capability evidence."""
    fx = _fixture()
    assert fx["schema"] == "statusline_live_fixture/v1"
    assert fx["doc_url"] == DOC_URL
    proof = fx["installed_version_proof"]
    assert proof["claude_version_output"].startswith("2.1.220")
    assert proof["payload_version_field"] == "2.1.220"
    assert _startup_payload()["version"] == "2.1.220"
    assert _post_payload()["version"] == "2.1.220"
    assert "Live interactive Claude Code 2.1.220" in fx["capture_method"]


def test_live_fixture_masked_no_home_or_username_leak():
    """PUBLIC repo: only [HOME]-masked paths survive in the fixture."""
    text = LIVE_FIXTURE.read_text(encoding="utf-8")
    assert "MLFLL" not in text
    assert "Users" not in text.replace("[HOME]", "")
    assert "[HOME]" in text  # masking actually happened; paths stayed real


def test_live_startup_payload_documented_nullability():
    """R136 against REAL data: current_usage null, percentages null,
    rate_limits absent, total_* == 0 before the first response."""
    payload = _startup_payload()
    assert payload["context_window"]["current_usage"] is None
    assert payload["context_window"]["used_percentage"] is None
    assert "rate_limits" not in payload
    record = tsl.ingest_status_line(payload, now_utc_iso=NOW)
    m = record.measurements
    # absent/null -> unknown, never zero
    assert m["live_input_tokens"].is_unknown
    assert m["context_used_pct"].is_unknown
    assert m["context_remaining_pct"].is_unknown
    # reported zero stays zero (total_* are legitimately 0 pre-first-response)
    assert m["context_total_input_tokens"].value == 0
    assert m["cumulative_cost_usd"].value == 0
    assert m["context_window_tokens"].value == 1000000
    assert "rate_limits" not in record.attributes


def test_live_post_response_payload_real_values_and_axes():
    """The populated real payload: occupancy, cumulative, and rate-limit
    facts land on their own axes (R133/R134)."""
    record = tsl.ingest_status_line(_post_payload(), now_utc_iso=NOW)
    m = record.measurements
    assert m["context_used_pct"].value == 4
    assert m["context_used_pct"].category == "occupancy"
    assert m["context_total_input_tokens"].value == 39075
    assert m["live_cache_creation_tokens"].value == 39073
    assert m["cumulative_cost_usd"].category == "cumulative"
    assert m["cumulative_cost_usd"].value > 0
    limits = record.attributes["rate_limits"]
    assert round(limits["five_hour"]["used_percentage"]) == 29
    assert limits["seven_day"]["used_percentage"] == 33
    assert limits["five_hour"]["resets_at"] is not None
    # rate-limit pressure never becomes a context measurement (R134)
    assert not any(name.startswith("rate_") for name in m)


# ---------- compact human row (R132/R133/R134) ------------------------------

def _segments(row: str) -> list[str]:
    return row.split(" | ")


def test_row_from_live_post_payload():
    payload = _post_payload()
    record = tsl.ingest_status_line(payload, now_utc_iso=NOW)
    row = tsl.format_status_row(record, payload)
    assert row == ("Fable 5 xhigh | ctx 4% of 1.0M | sess $0.78 1m | "
                   "5h 29% 7d 33% | v2.1.220")


def test_row_startup_unknowns_render_as_question_never_zero():
    payload = _startup_payload()
    record = tsl.ingest_status_line(payload, now_utc_iso=NOW)
    row = tsl.format_status_row(record, payload)
    ctx = next(s for s in _segments(row) if s.startswith("ctx"))
    assert ctx.startswith("ctx ?")
    assert "0%" not in ctx  # unknown occupancy is ?, never 0
    assert "limits ?" in row  # absent rate_limits block is ?, never 0
    assert "$0.00" in row  # reported zero cost stays zero (real fact)


def test_row_axes_never_borrow_each_other():
    """R133/R134: distinctive numbers stay inside their own segment."""
    payload = {
        "model": {"display_name": "TestModel"},
        "version": "2.1.220",
        "context_window": {"used_percentage": 7,
                           "context_window_size": 200000},
        "cost": {"total_cost_usd": 55.0, "total_duration_ms": 600000},
        "rate_limits": {"five_hour": {"used_percentage": 91,
                                      "resets_at": 1787721600}},
    }
    record = tsl.ingest_status_line(payload, now_utc_iso=NOW)
    segments = _segments(tsl.format_status_row(record, payload))
    ctx = next(s for s in segments if s.startswith("ctx"))
    sess = next(s for s in segments if s.startswith("sess"))
    rate = next(s for s in segments if s.startswith("5h"))
    assert "7%" in ctx and "55" not in ctx and "91" not in ctx
    assert "$55.00" in sess and "7%" not in sess and "91" not in sess
    assert "91%" in rate and "7%" not in rate and "55" not in rate


def test_row_rate_limit_windows_independently_absent():
    """Documented: each window can be absent on its own (R136/R134)."""
    base = {"context_window": {"used_percentage": 10},
            "rate_limits": {"seven_day": {"used_percentage": 12,
                                          "resets_at": 1787878800}}}
    record = tsl.ingest_status_line(base, now_utc_iso=NOW)
    row = tsl.format_status_row(record, base)
    assert "7d 12%" in row
    assert "5h" not in row


def test_row_never_leaks_paths_or_session_identity():
    payload = _post_payload()
    record = tsl.ingest_status_line(payload, now_utc_iso=NOW)
    row = tsl.format_status_row(record, payload)
    assert "[HOME]" not in row and "\\" not in row and "/" not in row
    assert payload["session_id"] not in row
    assert "transcript" not in row


def test_row_effort_shown_only_when_reported():
    payload = {"model": {"display_name": "SomeModel"}}
    record = tsl.ingest_status_line(payload, now_utc_iso=NOW)
    row = tsl.format_status_row(record, payload)
    assert row.startswith("SomeModel |")
    missing = tsl.format_status_row(
        tsl.ingest_status_line({}, now_utc_iso=NOW), {})
    assert missing.startswith("model ?")


# ---------- one feed: sidecar + row from the same record (R132) -------------

def test_handler_writes_sanitized_sidecar_and_returns_row(tmp_path):
    sidecar = tj.TelemetrySidecar(tmp_path / "primary.json")
    _record, stored, row = tsl.handle_status_line(
        _post_payload(), sidecar=sidecar, now_utc_iso=NOW)
    assert row.startswith("Fable 5")
    assert stored["record_type"] == "primary_status_line"
    assert stored["measurements"]["context_used_pct"]["value"] == 4
    assert sidecar.read() == stored  # what was returned is what persisted


def test_handler_sidecar_masks_home_paths(tmp_path):
    payload = {"transcript_path": r"C:\Users\testuser\.claude\p\t.jsonl",
               "cwd": r"C:\Users\testuser\proj",
               "context_window": {"used_percentage": 3}}
    sidecar = tj.TelemetrySidecar(tmp_path / "primary.json")
    _record, stored, _row = tsl.handle_status_line(
        payload, sidecar=sidecar, now_utc_iso=NOW)
    text = json.dumps(stored)
    assert "testuser" not in text
    assert stored["attributes"]["transcript_path"].startswith("[HOME]")


def test_one_feed_read_back_by_shadow_status(tmp_path):
    """Codex/controller monitoring reads the SAME sidecar the row came from."""
    path = tmp_path / "primary.json"
    _record, stored, _row = tsl.handle_status_line(
        _post_payload(), sidecar=tj.TelemetrySidecar(path), now_utc_iso=NOW)
    status = tst.read_only_status(sidecar_paths={"primary": str(path)},
                                  now_utc_iso=NOW)
    assert status["sidecars"]["primary"] == stored


def test_handler_optional_journal_appends(tmp_path):
    journal = tj.TelemetryJournal(tmp_path / "j.jsonl", fsync=False)
    tsl.handle_status_line(_post_payload(),
                           sidecar=tj.TelemetrySidecar(tmp_path / "s.json"),
                           journal=journal, now_utc_iso=NOW)
    result = journal.read_all()
    assert len(result.records) == 1
    assert result.records[0]["record_type"] == "primary_status_line"


def test_non_dict_payload_still_updates_the_one_feed(tmp_path):
    """Even a torn payload refreshes the sidecar with an all-unknown record —
    absence of telemetry is itself a finding, never a silent skip."""
    sidecar = tj.TelemetrySidecar(tmp_path / "primary.json")
    record, stored, row = tsl.handle_status_line(
        None, sidecar=sidecar, now_utc_iso=NOW)
    assert record.measurements["context_used_pct"].is_unknown
    assert stored["attributes"]["payload_error"].startswith("expected object")
    assert "ctx ?" in row


# ---------- CLI entry point (degrade, never crash) --------------------------

def test_main_reads_stdin_writes_row_and_sidecar(tmp_path):
    side = tmp_path / "primary.json"
    out = io.StringIO()
    code = tsl.main(["--sidecar", str(side)],
                    stdin=io.StringIO(json.dumps(_post_payload())),
                    stdout=out)
    assert code == 0
    assert out.getvalue().strip().startswith("Fable 5")
    assert side.exists()
    assert tj.TelemetrySidecar(side).read()["record_type"] == \
        "primary_status_line"


def test_main_garbage_stdin_degrades_to_unknown_row(tmp_path):
    side = tmp_path / "primary.json"
    out = io.StringIO()
    code = tsl.main(["--sidecar", str(side)],
                    stdin=io.StringIO("this is {{{ not json"),
                    stdout=out)
    assert code == 0
    assert "ctx ?" in out.getvalue()
    assert side.exists()  # the feed still refreshed (all-unknown record)


def test_main_handler_error_prints_degraded_row_exit_zero(tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("a file where a directory is needed", encoding="utf-8")
    out = io.StringIO()
    code = tsl.main(["--sidecar", str(blocker / "sub" / "s.json")],
                    stdin=io.StringIO(json.dumps(_post_payload())),
                    stdout=out)
    assert code == 0
    row = out.getvalue()
    assert "telemetry ?" in row and "handler error" in row
    # only the exception TYPE is shown (messages can carry paths)
    assert str(tmp_path) not in row


def test_main_journal_flag_appends(tmp_path):
    side, journal = tmp_path / "s.json", tmp_path / "j.jsonl"
    code = tsl.main(["--sidecar", str(side), "--journal", str(journal)],
                    stdin=io.StringIO(json.dumps(_startup_payload())),
                    stdout=io.StringIO())
    assert code == 0
    assert len(tj.TelemetryJournal(journal).read_all().records) == 1


def test_default_sidecar_path_is_documented_runtime_local():
    assert tsl.DEFAULT_SIDECAR_PATH == ".claude/telemetry/statusline_sidecar.json"


# ---------- R135: no model messages, no API tokens (structural proof) -------

def test_statusline_module_no_model_context_injection():
    """Same structural duty as B1/B2 (R037/R044/R135), over the handler."""
    import ast
    source = (pathlib.Path(__file__).parent / "agent_supervisor" /
              "telemetry_statusline.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                docstrings.add(id(body[0].value))
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in docstrings):
            assert "additionalContext" not in node.value
            assert "hookSpecificOutput" not in node.value


def test_statusline_module_no_network_or_process_imports():
    """R135: the handler runs locally — no sockets, HTTP, or subprocesses."""
    import ast
    source = (pathlib.Path(__file__).parent / "agent_supervisor" /
              "telemetry_statusline.py").read_text(encoding="utf-8")
    forbidden = {"socket", "urllib", "http", "requests", "httpx",
                 "subprocess", "asyncio"}
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names = {alias.name.split(".")[0] for alias in node.names}
            assert not (names & forbidden), names
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root not in forbidden, node.module


def test_official_no_token_note_recorded_in_module_and_fixture():
    """R135/R138 anchor: the official note + doc URL travel with the code."""
    source = (pathlib.Path(__file__).parent / "agent_supervisor" /
              "telemetry_statusline.py").read_text(encoding="utf-8")
    assert DOC_URL in source
    assert "does not consume API tokens" in source
    assert _fixture()["doc_url"] == DOC_URL
