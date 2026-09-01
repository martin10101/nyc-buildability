"""M0-T105 (D-024 Amendment 3 unit D): durable event-bus tests.

Scenario IDs (S1-S11) map to the acceptance pack in
``project-control/reports/M0-T105-event-integration.md`` section 1. The C1
live per-event capture is owner-gated (R192/R197) and is NOT exercised here;
the one live row is the version drift tooth, which skips cleanly when
``claude`` is absent.

Supervisor-freeze qualifying evidence: D-024-R155, D-024-R173.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tools.agent_supervisor import event_bus as eb
from tools.agent_supervisor import event_drift as ed
from tools.agent_supervisor import event_stream as es
from tools.agent_supervisor.telemetry_hooks import KNOWN_HOOK_EVENTS
from tools.agent_supervisor.telemetry_journal import TelemetryJournal

FIXTURES = Path(__file__).parent / "agent_supervisor" / "fixtures"
CATALOG_FIXTURE = FIXTURES / "hook_event_catalog_2_1_252.json"
PAYLOADS_FIXTURE = FIXTURES / "hook_event_payloads_v1.json"
STREAM_FIXTURE = FIXTURES / "stream_json_subagent_events_v1.json"
RECORDER = Path(__file__).parents[1] / ".claude" / "hooks" / "supervisor_event_recorder.py"

SESSION_UUID = "0a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d"  # synthetic


def hook_payloads() -> dict[str, dict]:
    data = json.loads(PAYLOADS_FIXTURE.read_text(encoding="utf-8"))
    return {name: entry["payload"] for name, entry in data["payloads"].items()}


def make_bus(tmp_path: Path, **kwargs) -> eb.DurableEventBus:
    return eb.DurableEventBus(tmp_path / "hook_events.jsonl", **kwargs)


# ---------- S1 firing order ------------------------------------------------

def test_s1_firing_order_preserved(tmp_path):
    bus = make_bus(tmp_path)
    sequence = ["SessionStart", "SubagentStart", "PostToolBatch",
                "SubagentStop", "SessionEnd"]
    payloads = hook_payloads()
    for name in sequence:
        assert bus.publish(name, payloads[name]) is not None
    stored = bus.replay().stored_records
    assert [r["attributes"]["event"] for r in stored] == sequence
    bus_sequences = [r["attributes"]["bus_sequence"] for r in stored]
    assert bus_sequences == sorted(bus_sequences)
    assert len(set(bus_sequences)) == len(bus_sequences)
    assert all(r["record_type"] == "lifecycle_hook" for r in stored)


def test_s1_every_required_event_ingests_one_record(tmp_path):
    bus = make_bus(tmp_path)
    payloads = hook_payloads()
    for name, payload in payloads.items():
        record = bus.publish(name, payload)
        assert record is not None, name
        assert record.attributes["event"] == name
        assert record.attributes["known"] is True, name
    assert len(bus.replay().stored_records) == len(payloads)


# ---------- S2 dedup -------------------------------------------------------

def test_s2_duplicate_delivery_is_single_record(tmp_path):
    bus = make_bus(tmp_path)
    payload = hook_payloads()["UserPromptSubmit"]
    first = bus.publish("UserPromptSubmit", payload)
    second = bus.publish("UserPromptSubmit", payload)
    assert first is not None and second is None
    assert bus.duplicates_ignored == 1
    assert len(bus.replay().stored_records) == 1


def test_s2_distinct_payloads_are_distinct_events(tmp_path):
    bus = make_bus(tmp_path)
    payload = dict(hook_payloads()["Notification"])
    assert bus.publish("Notification", payload) is not None
    changed = dict(payload, prompt_id="[UUID-2]")
    assert bus.publish("Notification", changed) is not None
    assert len(bus.replay().stored_records) == 2


def test_s2_idempotency_key_deterministic():
    payload = hook_payloads()["Stop"]
    assert eb.idempotency_key("Stop", payload) == eb.idempotency_key("Stop", dict(payload))
    assert eb.idempotency_key("Stop", payload) != eb.idempotency_key("StopFailure", payload)


# ---------- S3 stream-JSON ingestion --------------------------------------

def stream_fixture() -> dict:
    return json.loads(STREAM_FIXTURE.read_text(encoding="utf-8"))


def test_s3_stream_events_become_typed_records(tmp_path):
    bus = make_bus(tmp_path)
    fixture = stream_fixture()
    published = []
    for row in fixture["lines"]:
        record = bus.publish_stream_line(json.dumps(row["event"]))
        if record is not None:
            published.append(record)
    # 6 fixture lines, one an exact duplicate uuid -> 5 records
    assert len(published) == 5
    assert bus.duplicates_ignored == 1
    assert all(r.record_type == "subagent_stream_event" for r in published)


def test_s3_usage_carries_source_confidence_labels(tmp_path):
    bus = make_bus(tmp_path)
    fixture = stream_fixture()
    by_uuid = {}
    for row in fixture["lines"]:
        record = bus.publish_stream_line(json.dumps(row["event"]))
        if record is not None:
            by_uuid[row["event"]["uuid"]] = record
    step = by_uuid["evt-0002"]
    assert step.measurements["step_input_tokens"].value == 120
    assert step.measurements["step_input_tokens"].label == "provider-exact"
    assert step.task_id == "toolu_dfixture01"  # subagent attribution
    # absent usage -> unknown, never zero (R042)
    absent = by_uuid["evt-0003"]
    assert absent.measurements["step_input_tokens"].is_unknown
    assert absent.measurements["step_input_tokens"].value is None
    # result usage -> final_request_* with the R043 caveat, sdk-cumulative
    result = by_uuid["evt-0004"]
    final = result.measurements["final_request_total_tokens"]
    assert final.value == 1160 and final.label == "sdk-cumulative"
    assert "R043" in final.detail
    # unknown event type recorded honestly
    unknown = by_uuid["evt-0005"]
    assert unknown.attributes["known_type"] is False


def test_s3_forwarded_text_is_reference_never_content(tmp_path):
    bus = make_bus(tmp_path)
    event = stream_fixture()["lines"][1]["event"]
    record = bus.publish_stream_line(json.dumps(event))
    text = event["message"]["content"][0]["text"]
    assert record.attributes["text_chars"] == len(text)
    assert len(record.attributes["text_sha256"]) == 64
    stored = json.dumps(bus.replay().stored_records)
    assert text not in stored


def test_s3_malformed_lines_raise_typed_errors(tmp_path):
    bus = make_bus(tmp_path)
    for bad in stream_fixture()["malformed_lines"]:
        with pytest.raises(es.StreamEventError):
            bus.publish_stream_line(bad)
    with pytest.raises(es.StreamEventError):
        bus.publish_stream_line('["a", "json", "array"]')
    assert bus.publish_stream_line("   \r\n") is None  # blank: no-op, no error
    assert bus.replay().stored_records == ()


def test_s3_statusline_sidecar_stays_primary(tmp_path):
    """R154: stream ingestion never touches a sidecar -- the module has no
    sidecar surface at all, and ingestion creates only the journal files."""
    bus = make_bus(tmp_path)
    for row in stream_fixture()["lines"]:
        bus.publish_stream_line(json.dumps(row["event"]))
    created = {p.name for p in tmp_path.iterdir()}
    assert created == {"hook_events.jsonl"}
    source = (Path(es.__file__)).read_text(encoding="utf-8")
    assert "TelemetrySidecar" not in source


# ---------- S4 redaction ---------------------------------------------------

def test_s4_durable_record_sanitized(tmp_path):
    bus = make_bus(tmp_path)
    payload = {
        "hook_event_name": "UserPromptSubmit",
        "session_id": SESSION_UUID,
        "prompt_id": SESSION_UUID,
        "prompt": "SECRET business plan text that must never persist",
        "transcript_path": "C:\\Users\\realname\\.claude\\projects\\x\\t.jsonl",
        "cwd": "/home/realname/work",
        "api_key": "sk-ant-fake12345678",
    }
    assert bus.publish("UserPromptSubmit", payload) is not None
    stored = json.dumps(bus.replay().stored_records)
    assert "realname" not in stored                      # paths masked
    assert "[HOME]" in stored
    assert "SECRET business plan" not in stored          # prompt withheld
    assert "sk-ant-fake12345678" not in stored           # secret redacted
    assert SESSION_UUID not in stored                    # raw UUID masked
    assert "[SESSION sha256=" in stored


def test_s4_session_mask_stable_for_correlation():
    once = eb.mask_session_value(SESSION_UUID)
    again = eb.mask_session_value(SESSION_UUID)
    assert once == again and SESSION_UUID not in once


def test_s4_nested_uuid_masked_at_any_depth(tmp_path):
    """G4-L2 / G5-LOW-1 / G3-A4 converged round-1 fix: a UUID nested inside
    a list/dict attribute value (or used as a dict key) must not reach the
    durable store raw."""
    bus = make_bus(tmp_path)
    payload = {"hook_event_name": "SubagentStart",
               "session_id": SESSION_UUID,
               "agent_id": {"inner": SESSION_UUID, SESSION_UUID: "as-key"},
               "model": ["primary", SESSION_UUID]}
    assert bus.publish("SubagentStart", payload) is not None
    stored = json.dumps(bus.replay().stored_records)
    assert SESSION_UUID not in stored
    assert stored.count("[SESSION sha256=") >= 4  # value, nested, key, list


# ---------- S5 atomic persistence -----------------------------------------

def test_s5_torn_final_line_never_a_record(tmp_path):
    store = tmp_path / "hook_events.jsonl"
    bus = eb.DurableEventBus(store)
    bus.publish("SessionStart", hook_payloads()["SessionStart"])
    with store.open("a", encoding="utf-8") as handle:
        handle.write('{"schema": "supervisor_telemetry/v1", "record_type": "torn')
    replay = bus.replay()
    assert len(replay.stored_records) == 1
    assert replay.skipped_lines == 1  # counted, never guessed into a record


# ---------- S6 restart-safe replay ----------------------------------------

def test_s6_restart_rebuilds_state_without_double_count(tmp_path):
    store = tmp_path / "hook_events.jsonl"
    payloads = hook_payloads()
    bus = eb.DurableEventBus(store)
    for name in ("SessionStart", "SubagentStart", "TaskCreated",
                 "SubagentStop", "PostToolBatch"):
        bus.publish(name, payloads[name])
    before = bus.replay()
    before_active = bus.registry.active()

    restarted = eb.DurableEventBus(store)  # simulated restart
    after = restarted.replay()
    assert after.stored_records == before.stored_records
    assert restarted.registry.active() == before_active
    assert after.store_duplicates == 0

    # a dedup-keyed event re-delivered AFTER the restart is still a no-op
    assert restarted.publish("SubagentStart", payloads["SubagentStart"]) is None
    assert restarted.duplicates_ignored == 1
    assert len(restarted.replay().stored_records) == len(before.stored_records)

    # ordering continues, never restarts from zero
    record = restarted.publish("SessionEnd", payloads["SessionEnd"])
    assert record.attributes["bus_sequence"] == before.last_sequence + 1


def test_s6_replay_is_pure_reading(tmp_path):
    store = tmp_path / "hook_events.jsonl"
    bus = eb.DurableEventBus(store)
    bus.publish("Notification", hook_payloads()["Notification"])
    size_before = store.stat().st_size
    for _ in range(3):
        bus.replay()
        eb.replay_store(store)
    assert store.stat().st_size == size_before  # no effect re-emission


# ---------- S7 unknown-event ----------------------------------------------

def test_s7_unknown_event_recorded_honestly(tmp_path):
    bus = make_bus(tmp_path)
    record = bus.publish("BrandNewFutureEvent",
                         {"session_id": "[SESSION-D-FIXTURE]",
                          "hook_event_name": "BrandNewFutureEvent"})
    assert record is not None
    assert record.attributes["known"] is False
    assert record.attributes["event"] == "BrandNewFutureEvent"
    stored = bus.replay().stored_records
    assert stored[0]["attributes"]["known"] is False


# ---------- S8 version drift ----------------------------------------------

def test_s8_catalog_fixture_valid_and_masked():
    # M0-T132 re-capture (D-024 Amendment 34): deliberate 2.1.252 admission
    # (M0-T118 precedent). Docs re-fetched 2026-09-01; 2.1.252 is a benign patch
    # bump with the IDENTICAL 33-event set as 2.1.251, so the REAL +2 drift
    # (PreModelSwitch + PostModelSwitch) versus the 2.1.220/2.1.248 baseline
    # carries unchanged. The 2_1_247/2_1_248/2_1_251 catalogs stay committed as
    # history.
    data = ed.load_catalog_fixture()
    assert data["task"] == "M0-T132"
    assert data["claude_version"] == "2.1.252 (Claude Code)"
    assert data["confidence"] == "official-docs"
    assert len(data["events"]) == 33
    whole = CATALOG_FIXTURE.read_text(encoding="utf-8")
    assert "Users" not in whole and "MLFLL" not in whole


def test_s8_recorded_drift_matches_computed_drift():
    data = ed.load_catalog_fixture()
    drift = ed.catalog_drift(data["events"], KNOWN_HOOK_EVENTS)
    recorded = data["drift_vs_2_1_220"]
    assert list(drift.added) == recorded["added"]
    assert list(drift.removed) == recorded["removed"]
    # 2.1.251 is a REAL +2 drift vs the 2.1.220/2.1.248 baseline: the two
    # added model-switch events are reconciled as a FACT the test bites on.
    assert drift.added == ("PostModelSwitch", "PreModelSwitch")
    assert drift.removed == ()
    assert drift.has_drift
    assert drift.describe() == "added: PostModelSwitch, PreModelSwitch"


def test_s8_drift_computation_surfaces_differences():
    drift = ed.catalog_drift(["SessionStart", "NewEvent"],
                             ["SessionStart", "GoneEvent"])
    assert drift.added == ("NewEvent",) and drift.removed == ("GoneEvent",)
    assert drift.has_drift and "NewEvent" in drift.describe()


def test_s8_broken_fixture_refused(tmp_path):
    bad = tmp_path / "catalog.json"
    bad.write_text('{"schema": "hook_event_catalog/v1", "events": []}',
                   encoding="utf-8")
    with pytest.raises(ed.CatalogFixtureError):
        ed.load_catalog_fixture(bad)
    with pytest.raises(ed.CatalogFixtureError):
        ed.load_catalog_fixture(tmp_path / "absent.json")


requires_claude = pytest.mark.skipif(
    shutil.which("claude") is None,
    reason="claude CLI not installed on this runner")


@requires_claude
def test_s8_live_version_matches_catalog_fixture():
    """Drift tooth: RED locally when the installed claude moves past the
    fixture's recorded version without a catalog re-capture (mirrors the
    M0-T104 native-adapter drift tooth)."""
    binary = shutil.which("claude")  # resolved path: no shell, ever
    assert binary is not None  # guaranteed by requires_claude
    out = subprocess.run([binary, "--version"], capture_output=True,
                         text=True, encoding="utf-8", timeout=60)
    installed = out.stdout.strip()
    data = ed.load_catalog_fixture()
    assert installed == data["claude_version"], (
        "installed claude drifted from the committed hook-event catalog "
        "fixture; re-capture the catalog for the new version and re-review")


# ---------- S9 blocking semantics (recorder script) ------------------------

def run_recorder(tmp_path, stdin_text, store=None):
    env = dict(__import__("os").environ)
    env["NYCB_EVENT_STORE_PATH"] = str(store if store is not None
                                       else tmp_path / "store.jsonl")
    return subprocess.run(
        [sys.executable, str(RECORDER)], input=stdin_text,
        capture_output=True, text=True, encoding="utf-8", timeout=120,
        env=env)


def test_s9_recorder_records_and_stays_silent(tmp_path):
    store = tmp_path / "store.jsonl"
    payload = hook_payloads()["SessionStart"]
    result = run_recorder(tmp_path, json.dumps(payload), store=store)
    assert result.returncode == 0
    assert result.stdout == ""  # no context injection, no decision, ever
    stored = TelemetryJournal(store).read_all()
    assert len(stored.records) == 1
    assert stored.records[0]["attributes"]["event"] == "SessionStart"


def test_s9_recorder_failure_fails_closed(tmp_path):
    # malformed JSON: exit 0, nothing recorded, nothing printed
    store = tmp_path / "store.jsonl"
    result = run_recorder(tmp_path, "{not json", store=store)
    assert result.returncode == 0 and result.stdout == ""
    assert not store.exists()
    # unwritable store path: exit 0, session unharmed
    blocked = tmp_path / "blocked"
    blocked.write_text("a file, not a directory", encoding="utf-8")
    result = run_recorder(tmp_path, json.dumps(hook_payloads()["Stop"]),
                          store=blocked / "sub" / "store.jsonl")
    assert result.returncode == 0 and result.stdout == ""


def test_s9_recorder_never_guesses_event_name(tmp_path):
    store = tmp_path / "store.jsonl"
    result = run_recorder(tmp_path, json.dumps({"session_id": "x"}), store=store)
    assert result.returncode == 0 and result.stdout == ""
    assert not store.exists()


def test_s9_recorder_non_ascii_payload_fidelity(tmp_path):
    """G4 round-1 M1 regression: a UTF-8 payload with an emoji and an
    accented path (whose UTF-8 bytes are undefined in cp1252) must be
    recorded with fidelity — never mojibake, never silently dropped."""
    store = tmp_path / "store.jsonl"
    payload = {"hook_event_name": "SubagentStart",
               "session_id": "[SESSION-D-FIXTURE]",
               "agent_type": "reviewer \U0001F680",
               "cwd": "C:\\Users\\x\\projects\\\u00CDsafj\u00F6r\u00F0ur"}
    result = run_recorder(tmp_path, json.dumps(payload, ensure_ascii=False),
                          store=store)
    assert result.returncode == 0 and result.stdout == ""
    stored = TelemetryJournal(store).read_all()
    assert len(stored.records) == 1  # not dropped
    attrs = stored.records[0]["attributes"]
    assert attrs["agent_type"] == "reviewer \U0001F680"  # no mojibake
    assert attrs["cwd"].endswith("\u00CDsafj\u00F6r\u00F0ur")
    assert attrs["cwd"].startswith("[HOME]")  # sanitization still ran


def test_s9_recorder_oversized_stdin_fails_closed(tmp_path):
    """G3 round-1 A5: the oversized-stdin branch, exercised for real."""
    store = tmp_path / "store.jsonl"
    padding = "x" * 1_100_000
    payload = json.dumps({"hook_event_name": "Notification", "pad": padding})
    result = run_recorder(tmp_path, payload, store=store)
    assert result.returncode == 0 and result.stdout == ""
    assert not store.exists()  # over the byte cap: nothing recorded


# ---------- S10 bounded store ----------------------------------------------

def test_s10_registry_bounded_at_bus_level(tmp_path):
    """G4 round-1 A2: the registry bound proven through the bus itself,
    not only via the reused telemetry pack."""
    bus = make_bus(tmp_path, registry_max_entries=2)
    for n in range(5):
        bus.publish("SubagentStart",
                    {"hook_event_name": "SubagentStart",
                     "session_id": "[SESSION-D-FIXTURE]",
                     "agent_id": f"agent-{n}"})
    assert len(bus.registry) <= 2  # oldest evicted, never unbounded


def test_s3_stream_key_content_digest_fallback(tmp_path):
    """G3 round-1 A5: events with no uuid/message.id dedup by canonical
    content digest — identical re-delivery collapses, distinct events do not."""
    bare = {"type": "system", "subtype": "init", "session_id": "[SESSION-D-FIXTURE]"}
    other = dict(bare, subtype="warmup")
    assert es.stream_idempotency_key(bare) == es.stream_idempotency_key(dict(bare))
    assert es.stream_idempotency_key(bare) != es.stream_idempotency_key(other)
    bus = make_bus(tmp_path)
    assert bus.publish_stream_event(bare) is not None
    assert bus.publish_stream_event(dict(bare)) is None  # dedup, no id needed
    assert bus.publish_stream_event(other) is not None
    assert len(bus.replay().stored_records) == 2


def test_s10_seen_keys_bounded(tmp_path):
    bus = make_bus(tmp_path, max_seen_keys=8)
    for n in range(20):
        bus.publish("Notification", {"hook_event_name": "Notification",
                                     "session_id": f"s-{n}"})
    assert len(bus._seen) <= 8
    assert bus.published == 20


def test_s10_journal_rotation_bounds_disk(tmp_path):
    store = tmp_path / "hook_events.jsonl"
    bus = eb.DurableEventBus(store, max_bytes=4096, max_generations=2)
    for n in range(200):
        bus.publish("PostToolBatch", {"hook_event_name": "PostToolBatch",
                                      "session_id": f"s-{n}"})
    files = sorted(p.name for p in tmp_path.iterdir())
    assert set(files) <= {"hook_events.jsonl", "hook_events.jsonl.1",
                          "hook_events.jsonl.2"}
    for name in files:
        assert (tmp_path / name).stat().st_size <= 4096 + 1024


def test_s10_rejects_broken_bounds(tmp_path):
    with pytest.raises(ValueError):
        make_bus(tmp_path, max_seen_keys=0)


def test_s10_failed_append_leaves_event_republishable(tmp_path, monkeypatch):
    """A write failure must NOT remember the dedup key: the event stays
    unrecorded AND re-publishable -- fail closed toward durability, never
    silent loss behind a remembered key."""
    bus = make_bus(tmp_path)
    payload = hook_payloads()["TaskCreated"]

    def boom(_record):
        raise OSError("disk full")

    monkeypatch.setattr(bus._journal, "append", boom)
    with pytest.raises(OSError):
        bus.publish("TaskCreated", payload)
    monkeypatch.undo()
    record = bus.publish("TaskCreated", payload)  # NOT a duplicate
    assert record is not None
    assert record.attributes["bus_sequence"] == 1  # failed attempt rolled back
    assert len(bus.replay().stored_records) == 1


# ---------- S11 hook-script security ---------------------------------------

def test_s11_recorder_is_command_hook_only():
    source = RECORDER.read_text(encoding="utf-8")
    # scan CODE only: the module docstring may legitimately DOCUMENT the
    # no-settings.json/no-blocking guarantees it makes
    module = __import__("ast").parse(source)
    docstring = __import__("ast").get_docstring(module) or ""
    code = source.replace(docstring, "", 1)
    for forbidden in ("urllib", "requests", "http.client", "socket",
                      "subprocess"):
        assert forbidden not in code, forbidden    # command hook, never HTTP
    assert "sys.stdin.read" in code                # payload from stdin
    assert "settings.json" not in code             # no self-registration
    assert "permissionDecision" not in code        # can never gate a session
    assert "additionalContext" not in code         # can never inject context


def test_s11_recorder_embeds_no_tokens():
    source = RECORDER.read_text(encoding="utf-8")
    for shape in ("sk-ant-", "ghp_", "github_pat_", "Bearer ", "xoxb-"):
        assert shape not in source


def test_s11_fixtures_are_masked():
    for fixture in (PAYLOADS_FIXTURE, STREAM_FIXTURE, CATALOG_FIXTURE):
        whole = fixture.read_text(encoding="utf-8")
        for leak in (":\\\\Users\\\\", ":/Users/", "MLFLL"):
            assert leak not in whole, f"{fixture.name}: {leak!r}"


def test_c1_live_fixture_masked_and_replayable():
    """C1 (discharged): the owner-launched 2.1.247 live capture is masked,
    parses as telemetry records, and freezes the measured facts — including
    the cross-process bus_sequence collision observed live (G3-A2)."""
    from tools.agent_supervisor.telemetry_records import TelemetryRecord
    fixture_path = FIXTURES / "hook_events_live_2026-08-27_m0t105_c1.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert data["task"] == "M0-T105"
    assert data["confidence"] == "measured-live"
    assert data["claude_version"] == "2.1.247 (Claude Code)"
    whole = fixture_path.read_text(encoding="utf-8")
    for leak in (":\\\\Users\\\\", ":/Users/", "MLFLL"):
        assert leak not in whole, f"unmasked fragment {leak!r}"
    records = [TelemetryRecord.from_dict(r) for r in data["records"]]
    assert len(records) == 9
    events = [r.attributes["event"] for r in records]
    for required in ("SessionStart", "UserPromptSubmit", "SubagentStart",
                     "SubagentStop", "PostToolBatch", "Stop", "SessionEnd"):
        assert required in events, required
    assert all(r.attributes["known"] is True for r in records)
    assert all(r.session_id.startswith("[SESSION sha256=") for r in records)
    assert "TaskCreated" not in events  # measured: Agent spawn ≠ TaskCreated
    sequences = [r.attributes["bus_sequence"] for r in records]
    assert sequences.count(3) == 2  # live cross-process collision, preserved


def test_s11_unit_d_does_not_touch_guards():
    """Unit D must not modify readonly_agent_guard.py (M0-T108/T109 scope);
    the recorder is a sibling file, never an edit to the guard packs."""
    guard = RECORDER.parent / "readonly_agent_guard.py"
    source = guard.read_text(encoding="utf-8")
    assert "event_bus" not in source and "M0-T105" not in source
