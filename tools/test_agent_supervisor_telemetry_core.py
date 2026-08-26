"""M0-T088 (D-024 Phase B1): telemetry core + primary-session ingestion tests,
plus the capability-probe hardening bundle carried from the M0-T086 gate round
(G3-minor generic matrix==live cross-check; G4-F1 word-boundary flag matching;
G4-F2 _run failure branches; G4-F3 --out/main/resolve_binaries coverage;
G5-S1 probe_meta home-prefix redaction).

Deterministic; no network; nothing here installs anything (16.1). The D-024
section 16.1 core cases covered: typed records with source/confidence labels;
unknown-never-zero; occupancy vs cumulative separation; complete and
null/missing status payloads; counters/rate-limit/session/transcript fields;
atomic write interrupted before and after rename; sidecar overlap safety;
journal rotation and bounded retention; redaction of credentials, prompts,
user paths, and terminal escape sequences; per-step vs cumulative provider
usage; message-ID dedup; counter reset/regression never looks fresh; no
telemetry path injects model context.

Supervisor-freeze qualifying evidence: D-024-R100.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import threading

import pytest

from tools.agent_supervisor import capability_probe as cp
from tools.agent_supervisor import telemetry_ingest as ti
from tools.agent_supervisor import telemetry_journal as tj
from tools.agent_supervisor import telemetry_records as tr
from tools.agent_supervisor import telemetry_redaction as td

FIXTURES = pathlib.Path(__file__).parent / "agent_supervisor" / "fixtures"
LIVE_FIXTURE = FIXTURES / "capability_probe_live_2026-08-25.json"
MATRIX = FIXTURES / "capability_matrix_v1.json"
NOW = "2026-08-25T12:00:00+00:00"


# ---------- typed records: labels, categories, unknown-never-zero ----------

def test_confidence_vocabulary_is_the_directive_set():
    assert tr.CONFIDENCE_LABELS == (
        "provider-exact", "sdk-task-cumulative", "subagent-status-live",
        "sdk-cumulative", "status-live", "transcript-derived", "estimated",
        "unknown")


def test_measurement_rejects_unknown_label_and_category():
    with pytest.raises(tr.TelemetryRecordError):
        tr.Measurement(value=1, label="vibes", category="cumulative")
    with pytest.raises(tr.TelemetryRecordError):
        tr.Measurement(value=1, label="provider-exact", category="sideways")


def test_missing_usage_is_unknown_never_zero():
    m = tr.Measurement.unknown("cumulative", "nothing observed")
    assert m.value is None and m.label == "unknown" and m.is_unknown
    # a missing value may not hide behind a confident label
    with pytest.raises(tr.TelemetryRecordError):
        tr.Measurement(value=None, label="provider-exact", category="cumulative")
    # and a real number may not claim unknown
    with pytest.raises(tr.TelemetryRecordError):
        tr.Measurement(value=0, label="unknown", category="cumulative")


def test_measurement_rejects_bool_and_negative():
    with pytest.raises(tr.TelemetryRecordError):
        tr.Measurement(value=True, label="status-live", category="occupancy")
    with pytest.raises(tr.TelemetryRecordError):
        tr.Measurement(value=-5, label="status-live", category="occupancy")


def test_occupancy_and_cumulative_never_cross_labelled():
    """R038: a registry name records only under its own category."""
    with pytest.raises(tr.TelemetryRecordError):
        tr.TelemetryRecord(
            record_type="x", timestamp_utc=NOW,
            measurements={"context_used_pct": tr.Measurement(
                value=50, label="status-live", category="cumulative")})
    with pytest.raises(tr.TelemetryRecordError):
        tr.TelemetryRecord(
            record_type="x", timestamp_utc=NOW,
            measurements={"cumulative_input_tokens": tr.Measurement(
                value=10, label="provider-exact", category="occupancy")})


def test_record_round_trip_and_schema_check():
    rec = tr.TelemetryRecord(
        record_type="primary_status_line", timestamp_utc=NOW,
        session_id="s1", measurements={
            "context_used_pct": tr.Measurement(
                value=41.5, label="status-live", category="occupancy")},
        attributes={"model_id": "claude-fable-5"})
    back = tr.TelemetryRecord.from_dict(rec.to_dict())
    assert back == rec
    bad = rec.to_dict()
    bad["schema"] = "other/v9"
    with pytest.raises(tr.TelemetryRecordError):
        tr.TelemetryRecord.from_dict(bad)


# ---------- status-line ingestion (D-024 s5.1 item 3) ----------

def _full_status_payload() -> dict:
    """The documented statusline schema (capability_matrix_v1.json)."""
    return {
        "session_id": "sess-123", "transcript_path": r"C:\Users\me\t.jsonl",
        "cwd": r"C:\Users\me\repo", "version": "2.1.220",
        "model": {"id": "claude-fable-5", "display_name": "Fable 5"},
        "cost": {"total_cost_usd": 1.25, "total_duration_ms": 60000,
                 "total_api_duration_ms": 41000},
        "context_window": {
            "total_input_tokens": 90000, "total_output_tokens": 4000,
            "context_window_size": 200000, "used_percentage": 45.0,
            "remaining_percentage": 55.0,
            "current_usage": {"input_tokens": 88000, "output_tokens": 2000,
                              "cache_creation_input_tokens": 1000,
                              "cache_read_input_tokens": 87000}},
        "exceeds_200k_tokens": False,
        "rate_limits": {"five_hour": {"used_percent": 10},
                        "seven_day": {"used_percent": 30}},
    }


def test_status_line_complete_payload():
    rec = ti.ingest_status_line(_full_status_payload(), now_utc_iso=NOW)
    m = rec.measurements
    assert rec.session_id == "sess-123"
    assert m["context_used_pct"].value == 45.0
    assert m["context_window_tokens"].value == 200000
    assert m["live_cache_read_tokens"].value == 87000
    assert m["cumulative_cost_usd"].value == 1.25
    assert all(v.label == "status-live" for v in m.values())
    assert rec.attributes["rate_limits"]["five_hour"]["used_percent"] == 10
    assert rec.attributes["transcript_path"].endswith("t.jsonl")
    assert rec.attributes["model_id"] == "claude-fable-5"


def test_status_line_occupancy_vs_cumulative_separation():
    """context_window.* is live occupancy; cost.* is session-cumulative."""
    rec = ti.ingest_status_line(_full_status_payload(), now_utc_iso=NOW)
    for name in ("context_total_input_tokens", "context_total_output_tokens",
                 "context_window_tokens", "context_used_pct",
                 "context_remaining_pct", "live_input_tokens",
                 "live_output_tokens", "live_cache_creation_tokens",
                 "live_cache_read_tokens"):
        assert rec.measurements[name].category == "occupancy", name
    for name in ("cumulative_cost_usd", "cumulative_duration_ms",
                 "cumulative_api_duration_ms"):
        assert rec.measurements[name].category == "cumulative", name


def test_status_line_startup_nulls_become_unknown_not_zero():
    """Documented startup shape: current_usage null, percentages null,
    total_* legitimately 0 before the first response (a REPORTED zero)."""
    payload = {
        "session_id": "sess-1",
        "cost": {"total_cost_usd": 0, "total_duration_ms": 0},
        "context_window": {
            "total_input_tokens": 0, "total_output_tokens": 0,
            "context_window_size": 200000, "used_percentage": None,
            "remaining_percentage": None, "current_usage": None},
    }
    rec = ti.ingest_status_line(payload, now_utc_iso=NOW)
    m = rec.measurements
    assert m["context_used_pct"].is_unknown
    assert m["context_remaining_pct"].is_unknown
    assert m["live_input_tokens"].is_unknown
    assert m["live_cache_read_tokens"].is_unknown
    # a reported zero stays a reported zero; it is not upgraded to unknown
    assert m["context_total_input_tokens"].value == 0
    assert m["cumulative_cost_usd"].value == 0
    # absent cost field -> unknown
    assert m["cumulative_api_duration_ms"].is_unknown


def test_status_line_post_compaction_current_usage_null():
    payload = _full_status_payload()
    payload["context_window"]["current_usage"] = None  # after /compact
    rec = ti.ingest_status_line(payload, now_utc_iso=NOW)
    assert rec.measurements["live_input_tokens"].is_unknown
    assert rec.measurements["context_window_tokens"].value == 200000


def test_status_line_non_dict_payload_fails_to_unknown():
    rec = ti.ingest_status_line(None, now_utc_iso=NOW)
    assert rec.measurements["context_used_pct"].is_unknown
    assert "payload_error" in rec.attributes


def test_status_line_malformed_values_become_unknown():
    payload = {"context_window": {"used_percentage": "45%",
                                  "context_window_size": -1,
                                  "total_input_tokens": True}}
    rec = ti.ingest_status_line(payload, now_utc_iso=NOW)
    assert rec.measurements["context_used_pct"].is_unknown
    assert rec.measurements["context_window_tokens"].is_unknown
    assert rec.measurements["context_total_input_tokens"].is_unknown


# ---------- provider usage: per-step vs cumulative, dedup, regressions ------

def _step(inp: int, out: int) -> dict:
    return {"input_tokens": inp, "output_tokens": out,
            "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}


def test_step_sums_and_per_step_record_stay_distinct():
    acc = ti.UsageAccumulator(session_id="s")
    step = acc.ingest_step("msg-1", _step(100, 20), now_utc_iso=NOW)
    acc.ingest_step("msg-2", _step(50, 10), now_utc_iso=NOW)
    assert step is not None
    assert step.record_type == "provider_usage_step"
    # per-step records use the step_* name family (M0-T088 G3 carried fix):
    # a single step's delta never borrows the cumulative_* names
    assert step.measurements["step_input_tokens"].value == 100
    assert step.measurements["step_input_tokens"].label == "provider-exact"
    assert "cumulative_input_tokens" not in step.measurements
    snap = acc.snapshot(now_utc_iso=NOW)
    assert snap.measurements["cumulative_input_tokens"].value == 150
    assert snap.measurements["cumulative_output_tokens"].value == 30
    # reported (platform) totals are a separate name family, still unknown
    assert snap.measurements["reported_cumulative_input_tokens"].is_unknown


def test_message_id_dedup_ignores_replayed_steps():
    acc = ti.UsageAccumulator()
    assert acc.ingest_step("m1", _step(100, 10), now_utc_iso=NOW) is not None
    assert acc.ingest_step("m1", _step(100, 10), now_utc_iso=NOW) is None
    assert acc.duplicates_ignored == 1
    assert acc.snapshot(now_utc_iso=NOW).measurements[
        "cumulative_input_tokens"].value == 100


def test_reported_cumulative_never_merges_with_step_sums():
    acc = ti.UsageAccumulator()
    acc.ingest_step("m1", _step(100, 10), now_utc_iso=NOW)
    acc.ingest_reported_cumulative({"input_tokens": 5000, "output_tokens": 400,
                                    "total_tokens": 5400})
    snap = acc.snapshot(now_utc_iso=NOW)
    assert snap.measurements["cumulative_input_tokens"].value == 100
    assert snap.measurements["reported_cumulative_input_tokens"].value == 5000
    assert snap.measurements["reported_cumulative_input_tokens"].label == \
        "sdk-cumulative"
    assert snap.measurements["cumulative_input_tokens"].label == "provider-exact"


def test_counter_regression_never_looks_fresh():
    """16.1: a reset/regressed platform counter keeps the high-water mark."""
    acc = ti.UsageAccumulator()
    acc.ingest_reported_cumulative({"total_tokens": 900000})
    acc.ingest_reported_cumulative({"total_tokens": 1200})  # reset!
    assert acc.counter_regressions == 1
    snap = acc.snapshot(now_utc_iso=NOW)
    assert snap.measurements["reported_cumulative_total_tokens"].value == 900000
    assert snap.attributes["counter_regressions"] == 1
    assert snap.attributes["reported_latest"]["reported_cumulative_total_tokens"] \
        == 1200


def test_no_usage_observed_snapshot_is_unknown_not_zero():
    snap = ti.UsageAccumulator().snapshot(now_utc_iso=NOW)
    for name, m in snap.measurements.items():
        assert m.is_unknown, f"{name} must be unknown before any observation"


def test_malformed_step_usage_is_unknown_and_counted():
    acc = ti.UsageAccumulator()
    rec = acc.ingest_step("m1", "not-a-dict", now_utc_iso=NOW)
    assert rec is not None
    assert rec.measurements["step_input_tokens"].is_unknown
    acc.ingest_step("m2", _step(10, 1), now_utc_iso=NOW)
    snap = acc.snapshot(now_utc_iso=NOW)
    assert snap.attributes["malformed_steps"] == 1
    assert "lower bound" in snap.measurements["cumulative_input_tokens"].detail


def test_unidentified_steps_still_count_but_are_flagged():
    acc = ti.UsageAccumulator()
    acc.ingest_step(None, _step(40, 4), now_utc_iso=NOW)
    snap = acc.snapshot(now_utc_iso=NOW)
    assert snap.measurements["cumulative_input_tokens"].value == 40
    assert snap.attributes["unidentified_steps"] == 1


# ---------- atomic sidecar (16.1: interrupted before/after rename; overlap) --

def _record(pct: float) -> tr.TelemetryRecord:
    return tr.TelemetryRecord(
        record_type="primary_status_line", timestamp_utc=NOW,
        measurements={"context_used_pct": tr.Measurement(
            value=pct, label="status-live", category="occupancy")})


def test_sidecar_update_read_round_trip(tmp_path):
    side = tj.TelemetrySidecar(tmp_path / "status.json")
    side.update(_record(10.0))
    stored = side.read()
    assert stored is not None
    assert stored["measurements"]["context_used_pct"]["value"] == 10.0


def test_sidecar_interrupted_before_rename_keeps_previous_snapshot(
        tmp_path, monkeypatch):
    side = tj.TelemetrySidecar(tmp_path / "status.json")
    side.update(_record(10.0))

    def exploding_replace(src, dst):
        raise OSError("simulated crash before rename completed")

    monkeypatch.setattr(tj.os, "replace", exploding_replace)
    with pytest.raises(OSError):
        side.update(_record(99.0))
    monkeypatch.undo()
    stored = side.read()
    assert stored is not None
    assert stored["measurements"]["context_used_pct"]["value"] == 10.0


def test_sidecar_interrupted_after_rename_shows_complete_new_snapshot(
        tmp_path):
    """Post-rename crash: the rename already published a complete document;
    a leftover temp file from another writer never corrupts reads."""
    side = tj.TelemetrySidecar(tmp_path / "status.json")
    side.update(_record(10.0))
    side.update(_record(20.0))  # rename done = publish done
    (tmp_path / "status.json.9999.7.tmp").write_text("{torn", encoding="utf-8")
    stored = side.read()
    assert stored is not None
    assert stored["measurements"]["context_used_pct"]["value"] == 20.0


def test_sidecar_overlapping_refreshes_never_tear(tmp_path):
    """16.1: refresh cancellation/overlap does not corrupt the sidecar."""
    side = tj.TelemetrySidecar(tmp_path / "status.json")
    valid = [float(v) for v in range(1, 33)]

    def writer(pct: float) -> None:
        side.update(_record(pct))

    threads = [threading.Thread(target=writer, args=(pct,)) for pct in valid]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    stored = side.read()
    assert stored is not None  # parseable = not torn
    assert stored["measurements"]["context_used_pct"]["value"] in valid


def test_sidecar_bounds_refuse_oversized_snapshot(tmp_path):
    side = tj.TelemetrySidecar(tmp_path / "s.json", max_bytes=512)
    rec = _record(1.0).to_dict()
    rec["attributes"] = {"blob_%d" % i: "x" * 40 for i in range(64)}
    with pytest.raises(tj.TelemetryBoundsError):
        side.update(rec)
    assert side.read() is None  # nothing was written


def test_sidecar_unreadable_reads_as_none_not_zero(tmp_path):
    path = tmp_path / "s.json"
    path.write_text("{not json", encoding="utf-8")
    assert tj.TelemetrySidecar(path).read() is None


# ---------- journal: rotation, bounds, torn lines, redact-first -------------

def test_journal_append_read_round_trip_and_redaction(tmp_path):
    journal = tj.TelemetryJournal(tmp_path / "t.jsonl", fsync=False)
    rec = _record(5.0).to_dict()
    rec["attributes"] = {"api_key": "super-secret-value",
                         "note": "token sk-ant-abcdef1234567890"}
    stored = journal.append(rec)
    assert stored["attributes"]["api_key"] == "[REDACTED:sensitive_key]"
    assert "sk-ant" not in json.dumps(stored)
    assert stored["redaction_count"] >= 2
    result = journal.read_all()
    assert result.skipped_lines == 0
    assert len(result.records) == 1
    assert "sk-ant" not in json.dumps(result.records[0])


def test_journal_rotation_and_bounded_retention(tmp_path):
    path = tmp_path / "t.jsonl"
    journal = tj.TelemetryJournal(path, max_bytes=2048, max_generations=2,
                                  fsync=False)
    for i in range(40):
        journal.append(_record(float(i)))
    assert path.exists()
    gen1 = tmp_path / "t.jsonl.1"
    assert gen1.exists()
    assert not (tmp_path / "t.jsonl.3").exists()  # bounded: nothing beyond .2
    total_bytes = sum(p.stat().st_size for p in tmp_path.iterdir())
    assert total_bytes <= 2048 * 3 + 1024  # active + 2 generations, bounded
    everything = journal.read_all(include_rotated=True)
    assert len(everything.records) < 40  # oldest generations were dropped
    values = [r["measurements"]["context_used_pct"]["value"]
              for r in everything.records]
    assert values == sorted(values)  # oldest-first ordering preserved


def test_journal_torn_final_line_skipped_never_invented(tmp_path):
    path = tmp_path / "t.jsonl"
    journal = tj.TelemetryJournal(path, fsync=False)
    journal.append(_record(1.0))
    with path.open("ab") as handle:  # simulate a crash mid-append
        handle.write(b'{"schema": "supervisor_telemetry/v1", "measurements"')
    result = journal.read_all()
    assert len(result.records) == 1
    assert result.skipped_lines == 1


def test_journal_single_record_over_bound_refused(tmp_path):
    journal = tj.TelemetryJournal(tmp_path / "t.jsonl", max_bytes=512,
                                  fsync=False)
    rec = _record(1.0).to_dict()
    rec["attributes"] = {"blob_%d" % i: "y" * 40 for i in range(64)}
    with pytest.raises(tj.TelemetryBoundsError):
        journal.append(rec)


# ---------- redaction: escapes, credentials, paths, prompts -----------------

def test_terminal_escape_sequences_stripped():
    text = "\x1b[31mred\x1b[0m and \x1b]0;title\x07 and \x1b(B plain\x07"
    clean, count = td.strip_terminal_escapes(text)
    assert "\x1b" not in clean and "\x07" not in clean
    assert count >= 4
    assert "red and" in clean and "plain" in clean


def test_home_prefix_redaction_windows_and_posix():
    for raw, tail in (
            (r"C:\Users\somebody\AppData\Roaming\npm\claude.cmd",
             r"\AppData\Roaming\npm\claude.cmd"),
            ("C:/Users/somebody/.local/bin/claude.EXE",
             "/.local/bin/claude.EXE"),
            ("/home/somebody/.npm-global/bin/codex", "/.npm-global/bin/codex"),
            ("/Users/somebody/Library/x", "/Library/x")):
        masked, n = td.redact_user_paths(raw)
        assert n == 1 and masked == "[HOME]" + tail, masked


def test_sanitize_text_credentials_and_assignment_secrets():
    result = td.sanitize_text(
        "key sk-ant-abc123456789012345 then API_KEY=hunter2-value done")
    assert "sk-ant" not in result.value and "hunter2" not in result.value
    assert result.count >= 2


def test_prompt_like_keys_withheld_as_digest_references():
    result = td.sanitize_structure(
        {"prompt": "the entire worker assignment text",
         "instructions": "do the thing", "status": "running"})
    out = result.value
    assert out["prompt"].startswith("[PROMPT-WITHHELD sha256=")
    assert "worker assignment" not in out["prompt"]
    assert out["instructions"].startswith("[PROMPT-WITHHELD sha256=")
    assert out["status"] == "running"


def test_long_free_text_bounded_with_digest_reference():
    long_text = "A" * 5000
    result = td.sanitize_text(long_text)
    assert len(result.value) < 400
    assert "[TRUNCATED sha256=" in result.value
    assert "chars=5000" in result.value


def test_status_record_transcript_path_masked_at_journal_write(tmp_path):
    rec = ti.ingest_status_line(_full_status_payload(), now_utc_iso=NOW)
    journal = tj.TelemetryJournal(tmp_path / "t.jsonl", fsync=False)
    stored = journal.append(rec)
    assert stored["attributes"]["transcript_path"].startswith("[HOME]")
    assert r"C:\Users" not in json.dumps(stored)


def test_redact_probe_meta_masks_paths_preserves_shape():
    meta = {"generated_at": "2026-08-25T00:00:00+00:00",
            "claude_binaries": [r"C:\Users\me\.local\bin\claude.EXE"],
            "codex_binaries": [], "platform": "win32"}
    out = td.redact_probe_meta(meta)
    assert out["claude_binaries"] == [r"[HOME]\.local\bin\claude.EXE"]
    assert out["platform"] == "win32" and out["codex_binaries"] == []


# ---------- structural: no model-context injection (s5.3 / R044) ------------

def _non_docstring_strings(source: str) -> list[str]:
    """Every string literal that is CODE (not a module/class/function docstring)."""
    import ast
    tree = ast.parse(source)
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                docstrings.add(id(body[0].value))
    return [node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings]


def test_no_telemetry_module_injects_model_context():
    """No telemetry CODE path may add additionalContext or compose a hook
    payload (docstrings may of course NAME the prohibition)."""
    package = pathlib.Path(__file__).parent / "agent_supervisor"
    for name in ("telemetry_records.py", "telemetry_redaction.py",
                 "telemetry_journal.py", "telemetry_ingest.py"):
        source = (package / name).read_text(encoding="utf-8")
        for literal in _non_docstring_strings(source):
            assert "additionalContext" not in literal, name
            assert "hookSpecificOutput" not in literal, name


# ---------- carried hardening: classify_flags word boundaries (G4-F1) -------

def test_classify_flags_word_boundary_no_prefix_capture():
    help_text = "  --print-format <fmt>  choose output\n  execute things\n"
    out = cp.classify_flags(help_text, ["--print", "exec"])
    assert out == {"--print": "not-detected-in-help",
                   "exec": "not-detected-in-help"}


def test_classify_flags_word_boundary_still_finds_real_tokens():
    help_text = ("  -p, --print   print and exit\n"
                 "  codex exec [aliases: e]\n  resume  continue a thread\n")
    out = cp.classify_flags(help_text, ["--print", "exec", "resume"])
    assert out == {"--print": "supported", "exec": "supported",
                   "resume": "supported"}


def test_classify_flags_hyphenated_flags_stay_atomic():
    """--mcp-config must not match inside --strict-mcp-config and the longer
    flag must still match itself."""
    help_text = "  --strict-mcp-config  only use configured servers\n"
    out = cp.classify_flags(help_text, ["--mcp-config", "--strict-mcp-config"])
    assert out == {"--mcp-config": "not-detected-in-help",
                   "--strict-mcp-config": "supported"}


# ---------- carried hardening: _run failure branches (G4-F2) ----------------

def test_run_timeout_degrades_to_unknown(monkeypatch):
    monkeypatch.setattr(cp.shutil, "which", lambda _name: "C:/fake/tool.exe")

    def raise_timeout(*_a, **_k):
        raise subprocess.TimeoutExpired(cmd="tool", timeout=cp.PROBE_TIMEOUT_S)

    monkeypatch.setattr(cp.subprocess, "run", raise_timeout)
    rec = cp._run(["tool", "--version"])
    assert rec["status"] == "unknown"
    assert "timeout" in rec["detail"]


def test_run_oserror_degrades_to_unknown(monkeypatch):
    monkeypatch.setattr(cp.shutil, "which", lambda _name: "C:/fake/tool.cmd")

    def raise_oserror(*_a, **_k):
        raise OSError("broken shim")

    monkeypatch.setattr(cp.subprocess, "run", raise_oserror)
    rec = cp._run(["tool", "--help"])
    assert rec["status"] == "unknown"
    assert "OSError" in rec["detail"]


def test_run_nonzero_exit_degrades_to_unknown(monkeypatch):
    monkeypatch.setattr(cp.shutil, "which", lambda _name: "C:/fake/tool.exe")
    monkeypatch.setattr(
        cp.subprocess, "run",
        lambda *_a, **_k: subprocess.CompletedProcess(
            args=["tool"], returncode=3, stdout="boom\n", stderr=""))
    rec = cp._run(["tool", "--help"])
    assert rec["status"] == "unknown"
    assert rec["exit_code"] == 3
    assert rec["first_line"] == "boom"


# ---------- carried hardening: --out / main / resolve_binaries (G4-F3) ------

def test_main_out_writes_parseable_record(tmp_path):
    out_file = tmp_path / "probe.json"
    assert cp.main(["--out", str(out_file)]) == 0
    record = json.loads(out_file.read_text(encoding="utf-8"))
    assert record["body"]["schema"] == "capability_probe/v1"
    assert "generated_at" in record["probe_meta"]


def test_main_stdout_default(capsys):
    assert cp.main([]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["body"]["schema"] == "capability_probe/v1"


def test_probe_meta_paths_are_home_redacted_live():
    """G5-S1: fresh probe_meta never contains a raw home-directory prefix."""
    meta = cp.build_record()["probe_meta"]
    dumped = json.dumps(meta)
    assert "Users" not in dumped and "/home/" not in dumped
    for path in meta["claude_binaries"] + meta["codex_binaries"]:
        assert path.startswith("[HOME]"), path


def test_resolve_binaries_finds_dual_installs(tmp_path, monkeypatch):
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    (first / "mytool.exe").write_bytes(b"x")
    (second / "mytool.cmd").write_bytes(b"x")
    import os as _os
    monkeypatch.setenv("PATH", f"{first}{_os.pathsep}{second}")
    found = cp.resolve_binaries("mytool")
    lowered = [f.lower() for f in found]
    assert str(first / "mytool.exe").lower() in lowered
    assert str(second / "mytool.cmd").lower() in lowered
    assert len(found) == len(set(lowered))  # case-insensitive dedup held


# ---------- carried hardening: generic matrix==live cross-check (G3) --------

@pytest.fixture(scope="module")
def live() -> dict:
    return json.loads(LIVE_FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def matrix() -> dict:
    return json.loads(MATRIX.read_text(encoding="utf-8"))


def _derive_live_status(cap_id: str, live: dict) -> str:
    """Map a measured-live matrix id to the live fixture's own verdict."""
    body = live["body"]
    claude_flags = body["claude_flags"]
    codex_flags = body["codex_flags"]
    simple = {
        "claude.strict_mcp_config_flag": lambda: claude_flags["--strict-mcp-config"],
        "claude.mcp_config_flag": lambda: claude_flags["--mcp-config"],
        "claude.worktree_flag": lambda: claude_flags["--worktree"],
        "codex.exec_noninteractive": lambda: codex_flags["exec"],
        "codex.sandbox_flag": lambda: codex_flags["--sandbox"],
        "codex.json_event_output": lambda: codex_flags["--json"],
        "codex.output_schema": lambda: codex_flags["--output-schema"],
        "codex.resume_thread": lambda: codex_flags["resume"],
    }
    if cap_id in simple:
        return simple[cap_id]()
    if cap_id == "claude.print_mode_output_format":
        statuses = {claude_flags["--print"], claude_flags["--output-format"]}
        # deterministic on a mixed set (M0-T088 G3 nit): sorted, not pop()
        return ("supported" if statuses == {"supported"}
                else sorted(statuses - {"supported"})[0])
    if cap_id == "claude.dual_install_resolution":
        return ("supported"
                if len(live["probe_meta"]["claude_binaries"]) >= 2 else "unknown")
    if cap_id == "hooks.live_behavior_fixtures":
        facts = {v for k, v in
                 body["interactive_only_capabilities"].items() if k != "note"}
        return "unknown" if facts == {"unknown"} else "mixed"
    raise AssertionError(
        f"measured-live capability {cap_id!r} has no live-fixture mapping; "
        f"extend _derive_live_status so the generic cross-check stays complete")


def test_generic_matrix_equals_live_for_all_measured_entries(matrix, live):
    """G3-minor carried fix: EVERY measured-live entry cross-checks matrix ==
    live generically (equality, not a hand-picked supported-only subset)."""
    measured = [c for c in matrix["capabilities"]
                if c["confidence"] == "measured-live"]
    assert len(measured) >= 10  # the full measured surface, not a sample
    for cap in measured:
        derived = _derive_live_status(cap["id"], live)
        assert cap["status"] == derived, (
            f"matrix says {cap['id']}={cap['status']!r} but the live fixture "
            f"derives {derived!r}")


def test_committed_live_fixture_probe_meta_is_redacted(live):
    """G5-S1: the COMMITTED fixture's probe_meta must carry no home prefix."""
    dumped = json.dumps(live["probe_meta"])
    assert "Users" not in dumped and "/home/" not in dumped
    for path in (live["probe_meta"]["claude_binaries"]
                 + live["probe_meta"]["codex_binaries"]):
        assert path.startswith("[HOME]"), path
