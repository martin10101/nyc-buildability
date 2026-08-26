"""M0-T089 (D-024 Phase B2): subagent telemetry breadth tests — subagentStatusLine
ingestion, SDK task events (feature-detected, SDK absent-by-policy), lifecycle
hooks + identity registry, transcript-derived fallback, read-only shadow
status — plus the carried M0-T088 gate-round bundle (G5-S2 cross-fixture
home-prefix assertion; G4-Adv2 prompt-subtree withholding; G4-Adv1
never-observed-field unknown; G3-minor step_* naming; helper determinism).

Deterministic; no network; installs nothing (the Agent SDK stays absent and
its path cleanly skips — 16.1). Transcript shapes are proven against the
installed runtime (assistant message.id+usage and system/compact_boundary
compactMetadata.preTokens measured live on Claude Code 2.1.220, 2026-08-25).

Supervisor-freeze qualifying evidence: D-024-R100.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from tools.agent_supervisor import telemetry_hooks as th
from tools.agent_supervisor import telemetry_ingest as ti
from tools.agent_supervisor import telemetry_journal as tj
from tools.agent_supervisor import telemetry_redaction as td
from tools.agent_supervisor import telemetry_sdk as ts
from tools.agent_supervisor import telemetry_status as tst
from tools.agent_supervisor import telemetry_subagent as tsub
from tools.agent_supervisor import telemetry_transcript as ttr

FIXTURES = pathlib.Path(__file__).parent / "agent_supervisor" / "fixtures"
NOW = "2026-08-25T12:00:00+00:00"


# ---------- subagentStatusLine ingestion (16.1 multi-task payloads) ----------

def _multi_task_payload() -> dict:
    """Documented refresh-tick shape (capability_matrix_v1.json,
    claude.subagentStatusLine; official docs, fetched 2026-08-25)."""
    return {
        "session_id": "sess-parent",
        "tasks": [
            {"id": "task-1", "name": "reviewer", "type": "code-reviewer",
             "status": "running", "description": "review the diff",
             "label": "G3", "startTime": "2026-08-25T11:00:00Z",
             "model": "claude-fable-5", "effort": "high",
             "contextWindowSize": 200000, "tokenCount": 51000,
             "tokenSamples": [10000, 30000, 51000], "cwd": "C:/w1"},
            {"id": "task-2", "name": "qa", "type": "qa-engineer",
             "status": "running", "description": "run the suite",
             "startTime": "2026-08-25T11:01:00Z",
             "contextWindowSize": 200000, "tokenCount": 8000, "cwd": "C:/w2"},
            {"id": "task-3", "name": "starting", "type": "general-purpose",
             "status": "pending", "description": "model not resolved yet",
             "startTime": "2026-08-25T11:02:00Z"},
        ],
    }


def test_subagent_multi_task_payload_one_record_per_row():
    records = tsub.ingest_subagent_status(_multi_task_payload(), now_utc_iso=NOW)
    assert [r.task_id for r in records] == ["task-1", "task-2", "task-3"]
    first = records[0]
    assert first.session_id == "sess-parent"
    assert first.measurements["subagent_token_count"].value == 51000
    assert first.measurements["subagent_token_count"].label == \
        "subagent-status-live"
    assert first.measurements["subagent_token_count"].category == "occupancy"
    assert first.measurements["subagent_context_window_tokens"].value == 200000
    assert first.attributes["model"] == "claude-fable-5"
    assert first.attributes["status"] == "running"


def test_subagent_unresolved_model_fields_absent_become_unknown():
    """model/contextWindowSize are OMITTED until the model resolves
    (>=2.1.205 docs note); tokenCount may be absent too — unknown, not zero."""
    records = tsub.ingest_subagent_status(_multi_task_payload(), now_utc_iso=NOW)
    pending = records[2]
    assert "model" not in pending.attributes
    assert pending.measurements["subagent_token_count"].is_unknown
    assert pending.measurements["subagent_context_window_tokens"].is_unknown


def test_subagent_token_samples_trend_only_never_a_measurement():
    records = tsub.ingest_subagent_status(_multi_task_payload(), now_utc_iso=NOW)
    first = records[0]
    assert first.attributes["tokenSamples"] == [10000, 30000, 51000]
    assert "trend" in first.attributes["tokenSamples_note"]
    assert not any("sample" in name for name in first.measurements)


def test_subagent_malformed_payload_fails_to_unknown():
    for bad in (None, "text", 42, {"tasks": "not-a-list"}):
        records = tsub.ingest_subagent_status(bad, now_utc_iso=NOW)
        assert len(records) == 1
        assert records[0].measurements["subagent_token_count"].is_unknown
        assert "payload_error" in records[0].attributes


def test_subagent_malformed_row_and_bool_counts_fail_to_unknown():
    payload = {"tasks": ["not-a-dict",
                         {"id": "t", "tokenCount": True,
                          "contextWindowSize": -5}]}
    records = tsub.ingest_subagent_status(payload, now_utc_iso=NOW)
    assert records[0].measurements["subagent_token_count"].is_unknown
    assert records[1].measurements["subagent_token_count"].is_unknown
    assert records[1].measurements["subagent_context_window_tokens"].is_unknown


def test_subagent_empty_tick_records_zero_tasks_honestly():
    records = tsub.ingest_subagent_status({"tasks": []}, now_utc_iso=NOW)
    assert len(records) == 1
    assert records[0].attributes == {"tasks": 0}
    assert records[0].measurements["subagent_token_count"].is_unknown


def test_subagent_sidecar_snapshot_is_compact_and_atomic(tmp_path):
    """16.1: the refresh path updates a bounded atomic sidecar quickly."""
    records = tsub.ingest_subagent_status(_multi_task_payload(), now_utc_iso=NOW)
    snapshot = tsub.sidecar_snapshot(records, now_utc_iso=NOW)
    assert snapshot["schema"] == "subagent_sidecar/v1"
    assert [row["task_id"] for row in snapshot["tasks"]] == \
        ["task-1", "task-2", "task-3"]
    side = tj.TelemetrySidecar(tmp_path / "subagents.json")
    stored = side.update(snapshot)
    assert side.read() == stored
    assert (tmp_path / "subagents.json").stat().st_size < 4096  # compact


# ---------- SDK task events (feature-detected; SDK absent-by-policy) --------

def test_sdk_stays_absent_and_probe_has_no_side_effects():
    """16.1: an unadmitted SDK cleanly skips; the suite installs nothing.
    (If an owner-authorized admission ever lands, this test is updated by
    that task — absence is the CURRENT policy per capability_matrix_v1.)"""
    import sys
    assert ts.sdk_available() is False
    assert not any(m in sys.modules for m in ts.SDK_MODULE_CANDIDATES)


def test_sdk_progress_events_accumulate_high_water():
    tracker = ts.SdkTaskTracker()
    tracker.ingest_event({"type": "task_started", "task_id": "t1",
                          "description": "unit"}, now_utc_iso=NOW)
    rec = tracker.ingest_event(
        {"type": "task_progress", "task_id": "t1", "total_tokens": 1000,
         "tool_uses": 3, "duration_ms": 4000, "last_tool_name": "Read"},
        now_utc_iso=NOW)
    assert rec.measurements["sdk_task_total_tokens"].value == 1000
    assert rec.measurements["sdk_task_total_tokens"].label == \
        "sdk-task-cumulative"
    rec2 = tracker.ingest_event(
        {"type": "task_progress", "task_id": "t1", "total_tokens": 5000,
         "tool_uses": 9, "duration_ms": 9000}, now_utc_iso=NOW)
    assert rec2.measurements["sdk_task_total_tokens"].value == 5000
    assert tracker.high_water("t1")["sdk_task_total_tokens"] == 5000


def test_sdk_duplicate_progress_never_double_counts():
    tracker = ts.SdkTaskTracker()
    tracker.ingest_event({"type": "task_progress", "task_id": "t1",
                          "total_tokens": 700}, now_utc_iso=NOW)
    rec = tracker.ingest_event({"type": "task_progress", "task_id": "t1",
                                "total_tokens": 700}, now_utc_iso=NOW)
    assert rec.measurements["sdk_task_total_tokens"].value == 700
    assert rec.attributes["duplicates"] == 1


def test_sdk_progress_regression_keeps_high_water_never_fresh():
    tracker = ts.SdkTaskTracker()
    tracker.ingest_event({"type": "task_progress", "task_id": "t1",
                          "total_tokens": 900000}, now_utc_iso=NOW)
    rec = tracker.ingest_event({"type": "task_progress", "task_id": "t1",
                                "total_tokens": 100}, now_utc_iso=NOW)
    assert rec.measurements["sdk_task_total_tokens"].value == 900000
    assert rec.attributes["regressions"] == 1


def test_sdk_final_result_never_assumed_cumulative():
    """R043 proof: completion usage records as final_request_*, while the
    cumulative claim stays with the progress high-water."""
    tracker = ts.SdkTaskTracker()
    tracker.ingest_event({"type": "task_progress", "task_id": "t1",
                          "total_tokens": 250000}, now_utc_iso=NOW)
    done = tracker.ingest_event(
        {"type": "task_completed", "task_id": "t1",
         "usage": {"input_tokens": 1200, "output_tokens": 300}},
        now_utc_iso=NOW)
    assert done.measurements["final_request_input_tokens"].value == 1200
    assert "FINAL API request only" in \
        done.measurements["final_request_input_tokens"].detail
    assert done.measurements["sdk_task_total_tokens"].value == 250000


def test_sdk_out_of_order_completion_tolerated():
    tracker = ts.SdkTaskTracker()
    done = tracker.ingest_event({"type": "task_completed", "task_id": "t9"},
                                now_utc_iso=NOW)
    assert done.measurements["sdk_task_total_tokens"].is_unknown
    late = tracker.ingest_event({"type": "task_progress", "task_id": "t9",
                                 "total_tokens": 400}, now_utc_iso=NOW)
    assert late.measurements["sdk_task_total_tokens"].value == 400


def test_sdk_fully_duplicated_event_counts_one_duplicate():
    """M0-T089 G3 minor#2 carried fix (red/green): duplicates/regressions
    count EVENTS, not fields — a fully repeated 3-field progress event is ONE
    duplicate (the old per-field counting reported 3)."""
    tracker = ts.SdkTaskTracker()
    tracker.ingest_event({"type": "task_progress", "task_id": "t1",
                          "total_tokens": 700, "tool_uses": 2,
                          "duration_ms": 1000}, now_utc_iso=NOW)
    rec = tracker.ingest_event({"type": "task_progress", "task_id": "t1",
                                "total_tokens": 700, "tool_uses": 2,
                                "duration_ms": 1000}, now_utc_iso=NOW)
    assert rec.attributes["duplicates"] == 1
    regressed = tracker.ingest_event(
        {"type": "task_progress", "task_id": "t1", "total_tokens": 10,
         "tool_uses": 1, "duration_ms": 5}, now_utc_iso=NOW)
    assert regressed.attributes["regressions"] == 1


def test_sdk_tracker_bounded_eviction_prefers_completed():
    """M0-T089 G5-M1 carried fix (red/green): the per-task dict is bounded;
    a completed entry evicts before any active one, and evictions count."""
    tracker = ts.SdkTaskTracker(max_tasks=2)
    tracker.ingest_event({"type": "task_progress", "task_id": "t1",
                          "total_tokens": 100}, now_utc_iso=NOW)
    tracker.ingest_event({"type": "task_progress", "task_id": "t2",
                          "total_tokens": 200}, now_utc_iso=NOW)
    tracker.ingest_event({"type": "task_completed", "task_id": "t1"},
                         now_utc_iso=NOW)
    tracker.ingest_event({"type": "task_progress", "task_id": "t3",
                          "total_tokens": 300}, now_utc_iso=NOW)
    assert tracker.high_water("t1") == {}  # completed t1 evicted first
    assert tracker.high_water("t2")["sdk_task_total_tokens"] == 200
    assert tracker.high_water("t3")["sdk_task_total_tokens"] == 300
    assert tracker.evicted_tasks == 1
    tracker.ingest_event({"type": "task_progress", "task_id": "t4",
                          "total_tokens": 400}, now_utc_iso=NOW)
    assert tracker.evicted_tasks == 2  # no completed left: oldest (t2) went
    assert tracker.high_water("t2") == {}
    assert tracker.high_water("t4")["sdk_task_total_tokens"] == 400


def test_sdk_final_request_detail_directs_name_based_selection():
    """M0-T089 G3 nit#3 carried fix: the final_request detail warns a reader
    off label-based filtering (sdk-cumulative is the nearest fixed label)."""
    tracker = ts.SdkTaskTracker()
    done = tracker.ingest_event(
        {"type": "task_completed", "task_id": "t1",
         "usage": {"input_tokens": 10, "output_tokens": 5}}, now_utc_iso=NOW)
    detail = done.measurements["final_request_input_tokens"].detail
    assert "never by label" in detail
    assert done.measurements["final_request_input_tokens"].label == \
        "sdk-cumulative"


def test_sdk_malformed_and_unknown_events_fail_to_unknown():
    tracker = ts.SdkTaskTracker()
    bad = tracker.ingest_event("nonsense", now_utc_iso=NOW)
    assert bad.measurements["sdk_task_total_tokens"].is_unknown
    weird = tracker.ingest_event({"type": "task_teleported", "task_id": "t1"},
                                 now_utc_iso=NOW)
    assert weird.attributes["known"] is False
    assert weird.measurements["sdk_task_total_tokens"].is_unknown
    partial = tracker.ingest_event({"type": "task_progress", "task_id": "t1",
                                    "total_tokens": "many"}, now_utc_iso=NOW)
    assert partial.measurements["sdk_task_total_tokens"].is_unknown


# ---------- lifecycle hooks + subagent identity registry --------------------

def test_hook_event_set_matches_documented_31():
    assert len(th.KNOWN_HOOK_EVENTS) == 31
    for required in ("SessionStart", "SessionEnd", "SubagentStart",
                     "SubagentStop", "TaskCreated", "TaskCompleted",
                     "PostToolBatch", "PreCompact", "PostCompact", "Stop",
                     "StopFailure", "FileChanged", "PermissionRequest"):
        assert required in th.KNOWN_HOOK_EVENTS, required


def test_hook_ingest_known_and_unknown_events():
    rec = th.ingest_hook_event(
        "SubagentStart", {"session_id": "s1", "task_id": "t1",
                          "agent_type": "qa-engineer"}, now_utc_iso=NOW)
    assert rec.attributes["known"] is True
    assert rec.task_id == "t1" and rec.session_id == "s1"
    assert rec.measurements == {}  # hooks carry identity, never invented usage
    future = th.ingest_hook_event("BrandNewEvent2030", {}, now_utc_iso=NOW)
    assert future.attributes["known"] is False
    junk = th.ingest_hook_event(None, "not-a-dict", now_utc_iso=NOW)
    assert junk.attributes["known"] is False
    assert "payload_error" in junk.attributes


def test_subagent_registry_lifecycle():
    reg = th.SubagentRegistry()
    reg.observe(th.ingest_hook_event(
        "SubagentStart", {"task_id": "t1", "agent_type": "qa-engineer",
                          "session_id": "s"}, now_utc_iso=NOW))
    assert [e["task_id"] for e in reg.active()] == ["t1"]
    assert reg.get("t1")["agent_type"] == "qa-engineer"
    reg.observe(th.ingest_hook_event("SubagentStop", {"task_id": "t1"},
                                     now_utc_iso=NOW))
    assert reg.active() == ()
    assert reg.get("t1")["state"] == "closed"


def test_subagent_registry_bounded_eviction_prefers_closed():
    reg = th.SubagentRegistry(max_entries=3)
    for i in range(3):
        reg.observe(th.ingest_hook_event(
            "TaskCreated", {"task_id": f"t{i}"}, now_utc_iso=NOW))
    reg.observe(th.ingest_hook_event("TaskCompleted", {"task_id": "t0"},
                                     now_utc_iso=NOW))
    reg.observe(th.ingest_hook_event("TaskCreated", {"task_id": "t3"},
                                     now_utc_iso=NOW))
    assert len(reg) == 3
    assert reg.get("t0") is None  # closed entry evicted first
    assert {e["task_id"] for e in reg.active()} == {"t1", "t2", "t3"}


def test_registry_ignores_non_hook_records():
    reg = th.SubagentRegistry()
    reg.observe(ti.ingest_status_line({}, now_utc_iso=NOW))
    assert len(reg) == 0


# ---------- transcript-derived fallback (16.1) ------------------------------

def _assistant_line(msg_id: str, inp: int, out: int, session: str = "sess-A") -> str:
    """Shape measured live on Claude Code 2.1.220 (2026-08-25)."""
    return json.dumps({
        "type": "assistant", "sessionId": session,
        "message": {"id": msg_id, "role": "assistant",
                    "usage": {"input_tokens": inp, "output_tokens": out,
                              "cache_creation_input_tokens": 0,
                              "cache_read_input_tokens": inp - 100,
                              "service_tier": "standard"}}})


def _compact_line(pre: int, post: int, session: str = "sess-A") -> str:
    return json.dumps({
        "type": "system", "subtype": "compact_boundary", "sessionId": session,
        "compactMetadata": {"preTokens": pre, "postTokens": post,
                            "cumulativeDroppedTokens": pre - post,
                            "trigger": "auto"}})


def test_transcript_derivation_sums_and_labels():
    lines = [_assistant_line("m1", 1000, 50), _assistant_line("m2", 2000, 70),
             json.dumps({"type": "user", "sessionId": "sess-A"})]
    rec = ttr.derive_from_transcript_lines(lines, runtime_version="2.1.220",
                                           now_utc_iso=NOW)
    m = rec.measurements
    assert m["transcript_input_tokens"].value == 3000
    assert m["transcript_output_tokens"].value == 120
    assert m["transcript_input_tokens"].label == "transcript-derived"
    # M0-T089 G3 nit#5 carried fix: the old `... or True` here was dead and
    # checked the wrong string — the transcript detail ALWAYS declares itself
    # a conservative lower bound, never a provider statement; assert that.
    assert "conservative lower bound" in m["transcript_input_tokens"].detail
    assert "not a provider statement" in m["transcript_input_tokens"].detail
    assert rec.attributes["unknown_line_types"] == {"user": 1}
    assert rec.attributes["runtime_version"] == "2.1.220"


def test_transcript_duplicate_message_ids_deduplicated():
    lines = [_assistant_line("m1", 1000, 50), _assistant_line("m1", 1000, 50)]
    rec = ttr.derive_from_transcript_lines(lines, now_utc_iso=NOW)
    assert rec.measurements["transcript_input_tokens"].value == 1000
    assert rec.attributes["duplicates_ignored"] == 1


def test_transcript_fragmented_lines_skipped_never_invented():
    lines = [_assistant_line("m1", 500, 20),
             '{"type": "assistant", "sessionId": "sess-A", "message"',  # torn
             "", "not json at all"]
    rec = ttr.derive_from_transcript_lines(lines, now_utc_iso=NOW)
    assert rec.measurements["transcript_input_tokens"].value == 500
    assert rec.attributes["torn_or_malformed_lines"] == 2


def test_transcript_compact_boundary_pre_tokens_captured():
    lines = [_assistant_line("m1", 150000, 900), _compact_line(180000, 12000),
             _assistant_line("m2", 20000, 400)]
    rec = ttr.derive_from_transcript_lines(lines, now_utc_iso=NOW)
    assert rec.measurements["compaction_count"].value == 1
    assert rec.measurements["compaction_pre_tokens_total"].value == 180000
    assert rec.attributes["compactions"][0]["trigger"] == "auto"


def test_transcript_multiple_compactions_and_resumption():
    lines = [_assistant_line("m1", 100, 10, "sess-A"),
             _compact_line(150000, 9000, "sess-A"),
             _assistant_line("m2", 200, 20, "sess-A"),
             _compact_line(160000, 8000, "sess-B"),
             _assistant_line("m3", 300, 30, "sess-B")]
    rec = ttr.derive_from_transcript_lines(lines, now_utc_iso=NOW)
    assert rec.measurements["compaction_count"].value == 2
    assert rec.measurements["compaction_pre_tokens_total"].value == 310000
    assert rec.attributes["session_ids_seen"] == 2
    assert rec.attributes["resumed_session"] is True
    # counter-reset immunity: sums only grow across the resumption
    assert rec.measurements["transcript_input_tokens"].value == 600


def test_transcript_empty_is_unknown_not_zero():
    rec = ttr.derive_from_transcript_lines([], now_utc_iso=NOW)
    assert rec.measurements["transcript_input_tokens"].is_unknown
    assert rec.measurements["compaction_pre_tokens_total"].is_unknown
    assert rec.measurements["compaction_count"].value == 0  # observed fact


def test_transcript_malformed_compact_metadata_fails_to_unknown():
    lines = [json.dumps({"type": "system", "subtype": "compact_boundary",
                         "sessionId": "s", "compactMetadata": {"preTokens": "big"}})]
    rec = ttr.derive_from_transcript_lines(lines, now_utc_iso=NOW)
    assert rec.measurements["compaction_count"].value == 1
    assert rec.measurements["compaction_pre_tokens_total"].is_unknown


def test_transcript_compaction_details_bounded_totals_exact():
    """M0-T089 G5-M2 carried fix (red/green): the retained compaction detail
    list is capped while the COUNT and preTokens SUM stay exact, and the
    truncation is counted, never silent."""
    lines = [_compact_line(10, 5) for _ in range(ttr.MAX_COMPACTION_DETAILS + 44)]
    rec = ttr.derive_from_transcript_lines(lines, now_utc_iso=NOW)
    total = ttr.MAX_COMPACTION_DETAILS + 44
    assert rec.measurements["compaction_count"].value == total
    assert rec.measurements["compaction_pre_tokens_total"].value == 10 * total
    assert len(rec.attributes["compactions"]) == ttr.MAX_COMPACTION_DETAILS
    assert rec.attributes["compactions_truncated"] == 44


def test_transcript_unknown_type_keys_bounded_counts_preserved():
    """G5-M2: distinct unknown-type KEYS are capped; overflow lands in one
    counted bucket so no observation disappears."""
    lines = [json.dumps({"type": f"weird_{n}", "sessionId": "s"})
             for n in range(ttr.MAX_UNKNOWN_TYPE_KEYS + 6)]
    rec = ttr.derive_from_transcript_lines(lines, now_utc_iso=NOW)
    unknown = rec.attributes["unknown_line_types"]
    assert len(unknown) == ttr.MAX_UNKNOWN_TYPE_KEYS + 1
    assert unknown["<other>"] == 6
    assert sum(unknown.values()) == ttr.MAX_UNKNOWN_TYPE_KEYS + 6


def test_transcript_session_ids_bounded_overflow_counted():
    """G5-M2: the distinct-session-id list is capped; beyond it, events with
    unrecognized ids are counted (a lower bound, never a silent drop)."""
    lines = [json.dumps({"type": "user", "sessionId": f"sess-{n}"})
             for n in range(ttr.MAX_SESSION_IDS + 6)]
    rec = ttr.derive_from_transcript_lines(lines, now_utc_iso=NOW)
    assert rec.attributes["session_ids_seen"] == ttr.MAX_SESSION_IDS
    assert rec.attributes["session_id_overflow_events"] == 6
    assert rec.attributes["resumed_session"] is True


def test_transcript_post_tokens_and_trigger_narrowed():
    """M0-T089 G5-N2 carried fix (red/green): postTokens narrows exactly like
    preTokens (bool/negative/non-numeric -> None) and trigger stores only
    strings — malformed shapes can no longer ride along raw."""
    bad = json.dumps({"type": "system", "subtype": "compact_boundary",
                      "sessionId": "s",
                      "compactMetadata": {"preTokens": 100, "postTokens": "weird",
                                          "trigger": 123}})
    good = json.dumps({"type": "system", "subtype": "compact_boundary",
                       "sessionId": "s",
                       "compactMetadata": {"preTokens": 200, "postTokens": 50,
                                           "trigger": "auto"}})
    rec = ttr.derive_from_transcript_lines([bad, good], now_utc_iso=NOW)
    first, second = rec.attributes["compactions"]
    assert first["post_tokens"] is None and first["trigger"] is None
    assert second["post_tokens"] == 50 and second["trigger"] == "auto"


def test_subagent_window_detail_not_paired_with_itself():
    """M0-T089 G3 nit#4 carried fix: the contextWindowSize measurement calls
    itself the denominator of the live view; only tokenCount claims the
    documented pairing."""
    records = tsub.ingest_subagent_status(_multi_task_payload(),
                                          now_utc_iso=NOW)
    m = records[0].measurements
    assert "pairing" in m["subagent_token_count"].detail
    assert "denominator" in m["subagent_context_window_tokens"].detail
    assert "pairing" not in m["subagent_context_window_tokens"].detail


# ---------- read-only shadow status (actuation off) -------------------------

def test_read_only_status_assembles_without_writing(tmp_path):
    side_path = tmp_path / "primary.json"
    journal_path = tmp_path / "journal.jsonl"
    tj.TelemetrySidecar(side_path).update(
        ti.ingest_status_line({"session_id": "s1"}, now_utc_iso=NOW))
    journal = tj.TelemetryJournal(journal_path, fsync=False)
    journal.append(ti.ingest_status_line({"session_id": "s1"}, now_utc_iso=NOW))
    before = sorted(p.name for p in tmp_path.iterdir())
    status = tst.read_only_status(
        sidecar_paths={"primary": str(side_path)},
        journal_path=str(journal_path), now_utc_iso=NOW)
    after = sorted(p.name for p in tmp_path.iterdir())
    assert before == after  # read-only: no file created or removed
    assert status["actuation"].startswith("off")
    assert status["sidecars"]["primary"]["session_id"] == "s1"
    assert status["journal"]["records_total"] == 1
    assert status["journal"]["skipped_lines"] == 0


def test_read_only_status_missing_artifacts_report_null_not_zero(tmp_path):
    status = tst.read_only_status(
        sidecar_paths={"primary": str(tmp_path / "absent.json")},
        journal_path=str(tmp_path / "absent.jsonl"), now_utc_iso=NOW)
    assert status["sidecars"]["primary"] is None
    assert status["journal"]["records_total"] == 0


def test_status_main_prints_json_and_stays_read_only(tmp_path, capsys):
    assert tst.main(["--journal", str(tmp_path / "none.jsonl")]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["schema"] == "telemetry_shadow_status/v1"
    assert not (tmp_path / "none.jsonl").exists()


def test_compare_with_manual_is_opt_in_diagnostic():
    payload = {"session_id": "s",
               "context_window": {"used_percentage": 45.0,
                                  "context_window_size": 200000}}
    pipeline = ti.ingest_status_line(payload, now_utc_iso=NOW)
    report = tst.compare_with_manual(pipeline, payload, now_utc_iso=NOW)
    assert report["all_agree"] is True
    drifted = ti.ingest_status_line(
        {"session_id": "s", "context_window": {"used_percentage": 60.0,
                                               "context_window_size": 200000}},
        now_utc_iso=NOW)
    report2 = tst.compare_with_manual(drifted, payload, now_utc_iso=NOW)
    assert report2["all_agree"] is False  # disagreement reported, not raised
    assert report2["fields"]["context_used_pct"]["agree"] is False


def test_no_b2_module_injects_model_context():
    """Same structural duty as B1 (R037/R044), over the five B2 modules."""
    import ast
    package = pathlib.Path(__file__).parent / "agent_supervisor"
    for name in ("telemetry_subagent.py", "telemetry_hooks.py",
                 "telemetry_sdk.py", "telemetry_transcript.py",
                 "telemetry_status.py"):
        tree = ast.parse((package / name).read_text(encoding="utf-8"))
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
                assert "additionalContext" not in node.value, name
                assert "hookSpecificOutput" not in node.value, name


# ---------- carried M0-T088 bundle ------------------------------------------

def test_prompt_like_list_and_dict_values_withheld_wholesale():
    """G4-Adv2 red/green: non-scalar prompt values collapse to one digest."""
    result = td.sanitize_structure({
        "conversation": ["hello secret worker text", "second message"],
        "prompt": {"role": "user", "content": "the entire assignment"},
        "status": "running"})
    out = result.value
    assert isinstance(out["conversation"], str)
    assert out["conversation"].startswith("[PROMPT-WITHHELD sha256=")
    assert "secret worker" not in json.dumps(out)
    assert isinstance(out["prompt"], str)
    assert out["prompt"].startswith("[PROMPT-WITHHELD sha256=")
    assert "assignment" not in json.dumps(out)
    assert out["status"] == "running"
    # empty containers keep their honest shape (nothing to leak)
    kept = td.sanitize_structure({"prompt": [], "instructions": {}}).value
    assert kept == {"prompt": [], "instructions": {}}


def test_never_observed_step_field_is_unknown_not_zero():
    """G4-Adv1 red/green: a usage field never present in ANY step is unknown."""
    acc = ti.UsageAccumulator()
    acc.ingest_step("m1", {"input_tokens": 10, "output_tokens": 2},
                    now_utc_iso=NOW)
    snap = acc.snapshot(now_utc_iso=NOW)
    assert snap.measurements["cumulative_input_tokens"].value == 10
    assert snap.measurements["cumulative_cache_read_tokens"].is_unknown
    assert "never present" in \
        snap.measurements["cumulative_cache_read_tokens"].detail


def test_per_step_records_use_step_name_family():
    """G3-minor red/green: provider_usage_step never borrows cumulative_*."""
    acc = ti.UsageAccumulator()
    rec = acc.ingest_step("m1", {"input_tokens": 5, "output_tokens": 1},
                          now_utc_iso=NOW)
    assert set(rec.measurements) == {
        "step_input_tokens", "step_output_tokens",
        "step_cache_creation_tokens", "step_cache_read_tokens"}
    snap = acc.snapshot(now_utc_iso=NOW)
    assert all(name.startswith(("cumulative_", "reported_"))
               for name in snap.measurements)


def test_transcript_label_flows_through_accumulator():
    acc = ti.UsageAccumulator(step_label="transcript-derived")
    acc.ingest_step("m1", {"input_tokens": 7}, now_utc_iso=NOW)
    snap = acc.snapshot(now_utc_iso=NOW)
    assert snap.measurements["cumulative_input_tokens"].label == \
        "transcript-derived"
    with pytest.raises(ValueError):
        ti.UsageAccumulator(step_label="unknown")
    with pytest.raises(ValueError):
        ti.UsageAccumulator(step_label="vibes")


def test_all_committed_fixtures_free_of_home_prefixes():
    """G5-S2 closure: NO committed agent_supervisor fixture carries a real
    home-directory prefix — the exposure CLASS is closed, not one file."""
    fixtures = sorted(FIXTURES.glob("*.json"))
    assert fixtures, "fixture directory unexpectedly empty"
    import re
    pattern = re.compile(r"(?i)(?:[A-Z]:[\\/]+Users[\\/]+|/(?:home|Users)/)"
                         r"(?!name\b)[^\\/\s\"',;:\]\[]+")
    for path in fixtures:
        text = path.read_text(encoding="utf-8")
        hits = pattern.findall(text)
        assert not hits, f"{path.name} leaks a home prefix: {hits[:3]}"


def test_matrix_binary_notes_are_masked():
    matrix = json.loads((FIXTURES / "capability_matrix_v1.json")
                        .read_text(encoding="utf-8"))
    assert matrix["installed"]["claude_binary_note"].startswith(
        "dual install: [HOME]/")
    assert "MLFLL" not in json.dumps(matrix)
