"""M0-T106 (D-024 Amendment 3 unit E): bounded /goal integration tests.

Scenario IDs (S1-S11) map to the acceptance pack in
``project-control/reports/M0-T106-goal-integration.md`` section 1. The C1
live goal canary is owner-gated (R192/R197) and NOT exercised here; every
row below is deterministic (S11's fetch happened at build time and is frozen
in the fixture).

Supervisor-freeze qualifying evidence: D-024-R152, D-024-R174.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.agent_supervisor import event_bus as eb
from tools.agent_supervisor import goal_checkins as gc
from tools.agent_supervisor import goal_contract as gk
from tools.agent_supervisor import goal_outcomes as go

FIXTURES = Path(__file__).parent / "agent_supervisor" / "fixtures"
SEMANTICS_FIXTURE = FIXTURES / "goal_semantics_2_1_247.json"


def semantics() -> dict:
    return json.loads(SEMANTICS_FIXTURE.read_text(encoding="utf-8"))


def good_condition(**overrides) -> gk.GoalCondition:
    kwargs = dict(task_id="M0-T106",
                  end_state="the event-bus test pack passes",
                  stated_check="python -m pytest tools/test_agent_supervisor_event_bus.py exits 0",
                  constraints=("no file outside tools/agent_supervisor is modified",),
                  max_turns=20)
    kwargs.update(overrides)
    return gk.compose_goal_condition(
        kwargs.pop("task_id"), kwargs.pop("end_state"),
        kwargs.pop("stated_check"), **kwargs)


# ---------- S1 condition composition ---------------------------------------

def test_s1_condition_has_all_documented_parts():
    cond = good_condition()
    assert cond.task_id == "M0-T106"
    assert "Prove it:" in cond.text                      # stated check
    assert "stop after 20 turns" in cond.text            # explicit bound
    assert "Constraint:" in cond.text
    assert len(cond.text) <= gk.GOAL_CONDITION_MAX_CHARS


def test_s1_one_task_only():
    with pytest.raises(gk.GoalContractError):
        good_condition(end_state="M0-T092 and M0-T094 both complete")
    with pytest.raises(gk.GoalContractError):
        good_condition(task_id="not-a-task-id")


def test_s1_campaign_scale_refused():
    for phrase in ("the entire campaign is delivered",
                   "every remaining task is accepted",
                   "all remaining tasks pass their gates",
                   # the four G4 round-1 proven-slip phrasings (F5 widening)
                   "finish the milestone",
                   "the rest of the backlog is empty",
                   "wrap up the project",
                   "complete the remaining work"):
        with pytest.raises(gk.GoalContractError):
            good_condition(end_state=phrase)


def test_s1_direct_construction_cannot_drop_the_bound():
    """The turn-bound guard bites even on hand-built conditions: text whose
    bound clause was lost never becomes a GoalCondition object."""
    with pytest.raises(gk.GoalContractError):
        gk.GoalCondition(task_id="M0-T106", end_state="tests pass",
                         stated_check="pytest exits 0", constraints=(),
                         max_turns=20,
                         text="For task M0-T106: tests pass. Prove it: pytest exits 0.")


def test_s1_ceiling_and_required_parts():
    with pytest.raises(gk.GoalContractError):
        good_condition(end_state="x" * gk.GOAL_CONDITION_MAX_CHARS)
    with pytest.raises(gk.GoalContractError):
        good_condition(stated_check="   ")
    with pytest.raises(gk.GoalContractError):
        good_condition(max_turns=0)


# ---------- S2 no token pressure (R045) ------------------------------------

def test_s2_token_pressure_fails_closed():
    for poisoned in ("finish before 50000 tokens are used",
                     "conserve tokens while working",
                     "you have a token budget of 100k",
                     "88% of context remaining"):
        with pytest.raises(Exception) as excinfo:
            good_condition(end_state=f"tests pass; {poisoned}")
        assert "R045" in str(excinfo.value) or "token" in str(excinfo.value).lower()


def test_s2_clean_condition_passes_r045():
    # the validator runs on every construction; a clean condition constructs
    cond = good_condition()
    assert "token" not in cond.text.lower()


def test_s2_token_pressure_via_constraint_fails_closed():
    """G4 round-1 L2 coverage: the poison vector through a CONSTRAINT — the
    validator sees the full composed text, so the constraint path bites."""
    with pytest.raises(Exception):
        good_condition(constraints=("finish within 5000 tokens remaining",))


# ---------- S3 verdict ingestion -------------------------------------------

def test_s3_documented_verdicts_normalize():
    assert go.normalize_verdict("met") == "met"
    assert go.normalize_verdict("Not yet met") == "not_yet_met"
    assert go.normalize_verdict("IMPOSSIBLE") == "impossible"
    assert go.normalize_verdict("achieved") == "met"


def test_s3_unknown_verdict_is_unknown():
    for weird in ("partially met", "", None, 42, "definitely"):
        assert go.normalize_verdict(weird) == "unknown"


# ---------- S4 clearing classes --------------------------------------------

PREFIX = go.CLEARED_WARNING_PREFIX
SUFFIX = go.CLEARED_WARNING_SUFFIX


def test_s4_four_unrecoverable_classes():
    cases = {
        "auth_failure": f"{PREFIX}: an authentication failure occurred. {SUFFIX}",
        "credit_exhausted": f"{PREFIX}: your credit balance is exhausted. {SUFFIX}",
        "context_overflow": f"{PREFIX}: a context overflow that auto-compaction could not clear. {SUFFIX}",
        "model_unavailable": f"{PREFIX}: the model is not available. {SUFFIX}",
    }
    for expected, text in cases.items():
        clearing = go.classify_goal_message(text)
        assert clearing.cleared is True
        assert clearing.clazz == expected, text
        assert clearing.is_unrecoverable


def test_s4_host_managed_auth_stays_active():
    text = f"{PREFIX}: an authentication failure occurred. {SUFFIX}"
    clearing = go.classify_goal_message(text, credentials_host_managed=True)
    assert clearing.cleared is False
    assert clearing.clazz == "auth_failure_host_managed_active"


def test_s4_transient_stays_active():
    for text in ("API error: rate limit exceeded, retrying",
                 "the server is overloaded (529)"):
        clearing = go.classify_goal_message(text)
        assert clearing.cleared is False
        assert clearing.clazz == "transient_error_active"


def test_s3_reason_excerpt_bounded_160():
    """G4 round-1 L2 coverage: the excerpt cap actually bites."""
    long_reason = f"{PREFIX}: " + ("x" * 5000) + f" {SUFFIX}"
    clearing = go.classify_goal_message(long_reason)
    assert len(clearing.reason_excerpt) <= 160


def test_s4_user_clear_and_no_goal_and_unknown():
    assert go.classify_goal_message("Goal cleared: all tests pass").clazz == "cleared_by_user"
    assert go.classify_goal_message("No goal set").clazz == "no_goal"
    unknown = go.classify_goal_message("some novel future message")
    assert unknown.cleared is None and unknown.clazz == "unknown"
    # unrecoverable prefix with an unrecognized cause still clears, honestly
    odd = go.classify_goal_message(f"{PREFIX}: a brand new cause. {SUFFIX}")
    assert odd.cleared is True and odd.clazz == "unknown_unrecoverable"


# ---------- S5 no-progress --------------------------------------------------

def test_s5_no_progress_pause_is_structural_and_goal_stays_set():
    verdict = go.classify_pause(control_returned=True, goal_still_active=True)
    assert verdict == "no_progress_paused"
    # a cleared goal is NOT a pause
    cleared = go.classify_goal_message(
        f"{PREFIX}: the model is not available. {SUFFIX}")
    assert go.classify_pause(control_returned=True, goal_still_active=False,
                             clearing=cleared) == "not_paused_goal_cleared"
    assert go.classify_pause(control_returned=False,
                             goal_still_active=True) == "running"
    assert go.classify_pause(control_returned=True,
                             goal_still_active=False) == "unknown"


# ---------- S6 resume semantics ---------------------------------------------

def test_s6_resume_restores_active_goal_all_routes_on_2_1_247():
    for route in ("continue", "resume-id", "resume-name", "picker"):
        assert go.resume_restores_goal("2.1.247 (Claude Code)", route,
                                       "active") is True


def test_s6_achieved_and_cleared_never_restore():
    for state in ("achieved", "cleared"):
        assert go.resume_restores_goal("2.1.247", "continue", state) is False


def test_s6_pre_2_1_239_picker_excluded_and_unknown_honest():
    assert go.resume_restores_goal("2.1.238", "picker", "active") is False
    assert go.resume_restores_goal("2.1.238", "continue", "active") is True
    assert go.resume_restores_goal("garbled", "picker", "active") is None
    assert go.resume_restores_goal("2.1.247", "continue", "weird") is None


def test_s6_counters_reset_documented():
    assert set(go.RESUME_RESET_COUNTERS) == {
        "turn_count", "timer", "token_spend_baseline"}


# ---------- S7 check-in schedule --------------------------------------------

def test_s7_default_cadence_doubles_capped_at_4x():
    sched = gc.checkin_schedule(installed_version="2.1.247", count=5)
    assert sched.enabled and sched.source == "default"
    # gaps 30, 60, 120, 120, 120 -> offsets 30, 90, 210, 330, 450
    assert sched.due_offsets_minutes == (30, 90, 210, 330, 450)


def test_s7_env_scales_and_zero_disables():
    sched = gc.checkin_schedule(installed_version="2.1.247",
                                env_value="10", count=4)
    assert sched.first_interval_minutes == 10 and sched.source == "env"
    assert sched.due_offsets_minutes == (10, 30, 70, 110)  # gaps 10,20,40,40
    off = gc.checkin_schedule(installed_version="2.1.247", env_value="0")
    assert not off.enabled and off.due_offsets_minutes == ()
    assert off.source == "disabled-env"


def test_s7_malformed_env_fails_visible():
    for bad in ("ten", "-5", "3.5"):
        with pytest.raises(gc.GoalCheckinError):
            gc.checkin_schedule(installed_version="2.1.247", env_value=bad)


def test_s7_version_gates_honest():
    old = gc.checkin_schedule(installed_version="2.1.220")
    assert not old.enabled and old.source == "unavailable-version"
    unparseable = gc.checkin_schedule(installed_version="unknown")
    assert not unparseable.enabled
    assert gc.idle_checkin_cap("2.1.247") == gc.IdleCapVerdict(cap=3, known=True)
    assert gc.idle_checkin_cap("2.1.240") == gc.IdleCapVerdict(cap=None, known=True)
    assert gc.idle_checkin_cap("2.1.235") == gc.IdleCapVerdict(cap=0, known=True)
    # G3-A2/G4-A1 fix: ignorance is now DISTINGUISHABLE from uncapped
    assert gc.idle_checkin_cap("garbled") == gc.IdleCapVerdict(cap=None, known=False)


def test_s7_schedule_count_bounded():
    """G5 round-1 ADV-2: the projection length is capped, fail visible."""
    ok = gc.checkin_schedule(installed_version="2.1.247", count=gc.MAX_SCHEDULE_COUNT)
    assert len(ok.due_offsets_minutes) == gc.MAX_SCHEDULE_COUNT
    with pytest.raises(gc.GoalCheckinError):
        gc.checkin_schedule(installed_version="2.1.247",
                            count=gc.MAX_SCHEDULE_COUNT + 1)


# ---------- S8 check-in ingestion (durable, dedup-keyed) --------------------

def test_s8_checkin_lands_in_durable_bus_with_dedup(tmp_path):
    bus = eb.DurableEventBus(tmp_path / "store.jsonl")
    payload = {"kind": "idle", "sequence": 1, "running_tasks": 2,
               "session_id": "[SESSION-E-FIXTURE]", "goal_active": True}
    first = gc.record_checkin(bus, payload, task_id="M0-T106")
    second = gc.record_checkin(bus, payload, task_id="M0-T106")
    assert first is not None and second is None  # duplicate = counted no-op
    assert bus.duplicates_ignored == 1
    stored = bus.replay().stored_records
    assert len(stored) == 1
    assert stored[0]["record_type"] == "goal_checkin"
    assert stored[0]["attributes"]["kind"] == "idle"
    assert stored[0]["attributes"]["known_kind"] is True


def test_s8_unknown_kind_recorded_honestly(tmp_path):
    bus = eb.DurableEventBus(tmp_path / "store.jsonl")
    record = gc.record_checkin(bus, {"kind": "quantum", "sequence": 9})
    assert record is not None
    assert record.attributes["known_kind"] is False
    malformed = gc.ingest_checkin("not a mapping")
    assert malformed.attributes["known_kind"] is False
    assert malformed.attributes["payload_error"] == "str"


def test_s8_distinct_sequences_both_persist(tmp_path):
    """G4 round-1 M1 regression: two genuinely-distinct check-ins (only the
    sequence differs) BOTH persist; a byte-identical re-delivery dedups."""
    bus = eb.DurableEventBus(tmp_path / "store.jsonl")
    base = {"kind": "idle", "running_tasks": 2,
            "session_id": "[SESSION-E-FIXTURE]", "goal_active": True}
    first = gc.record_checkin(bus, dict(base, sequence=1))
    second = gc.record_checkin(bus, dict(base, sequence=2))
    replay = gc.record_checkin(bus, dict(base, sequence=2))
    assert first is not None and second is not None
    assert replay is None and bus.duplicates_ignored == 1
    assert len(bus.replay().stored_records) == 2


def test_s8_missing_discriminator_fails_visible(tmp_path):
    """G4 round-1 M1 caller contract: no sequence -> typed refusal, never a
    silent collapse."""
    bus = eb.DurableEventBus(tmp_path / "store.jsonl")
    with pytest.raises(gc.GoalCheckinError):
        gc.record_checkin(bus, {"kind": "idle", "running_tasks": 2})
    with pytest.raises(gc.GoalCheckinError):
        gc.record_checkin(bus, "not a mapping")
    assert bus.replay().stored_records == ()


def test_s8_status_snapshots_differing_only_in_measurements_both_persist(tmp_path):
    """G3 round-1 C1 regression: the publish_typed key now digests
    measurements, so two /goal status snapshots that advance only their
    numbers are DISTINCT records; an identical snapshot still dedups."""
    bus = eb.DurableEventBus(tmp_path / "store.jsonl")
    now = "2026-08-27T17:00:00+00:00"
    snap1 = go.ingest_goal_status({"active": True, "turns_evaluated": 3,
                                   "token_spend": 1000}, task_id="M0-T106",
                                  now_utc_iso=now)
    snap2 = go.ingest_goal_status({"active": True, "turns_evaluated": 9,
                                   "token_spend": 5000}, task_id="M0-T106",
                                  now_utc_iso=now)
    assert bus.publish_typed(snap1) is not None
    assert bus.publish_typed(snap2) is not None  # NOT a false-dedup
    assert bus.publish_typed(snap2) is None      # true duplicate collapses
    assert len(bus.replay().stored_records) == 2


def test_s9_spend_survives_durable_store_readable(tmp_path):
    """G5 round-1 ADV-1 regression: goal_spend_tokens (the pattern-safe
    name) survives the sanitize-first journal READABLE — never over-redacted
    to [REDACTED:sensitive_key]."""
    bus = eb.DurableEventBus(tmp_path / "store.jsonl")
    record = go.ingest_goal_status({"active": True, "turns_evaluated": 4,
                                    "token_spend": 12345}, task_id="M0-T106")
    assert bus.publish_typed(record) is not None
    stored = bus.replay().stored_records[0]
    spend = stored["measurements"]["goal_spend_tokens"]
    assert spend["value"] == 12345
    assert "[REDACTED" not in json.dumps(spend)


# ---------- S9 goal-status telemetry (R042) ---------------------------------

def test_s9_status_numbers_labelled():
    record = go.ingest_goal_status(
        {"active": True, "turns_evaluated": 7, "token_spend": 51234,
         "duration": "12m", "last_reason": "tests still failing"},
        task_id="M0-T106")
    turns = record.measurements["goal_turns_evaluated"]
    spend = record.measurements["goal_spend_tokens"]
    assert turns.value == 7 and turns.label == "status-live"
    assert spend.value == 51234 and spend.label == "status-live"
    assert "RESETS on resume" in spend.detail  # never whole-session claim


def test_s9_absent_numbers_unknown_never_zero():
    record = go.ingest_goal_status({"active": True})
    assert record.measurements["goal_turns_evaluated"].is_unknown
    assert record.measurements["goal_spend_tokens"].is_unknown
    malformed = go.ingest_goal_status(None)
    assert malformed.measurements["goal_turns_evaluated"].is_unknown
    for bad in (True, -3, "many"):
        rec = go.ingest_goal_status({"turns_evaluated": bad})
        assert rec.measurements["goal_turns_evaluated"].is_unknown


# ---------- S10 autocompact policy ------------------------------------------

def test_s10_context_overflow_is_turnover_seam():
    overflow = go.classify_goal_message(
        f"{PREFIX}: a context overflow that auto-compaction could not clear. {SUFFIX}")
    assert go.is_turnover_seam_trigger(overflow) is True


def test_s10_other_clearings_are_not_the_seam_trigger():
    other = go.classify_goal_message(
        f"{PREFIX}: your credit balance is exhausted. {SUFFIX}")
    assert go.is_turnover_seam_trigger(other) is False
    transient = go.classify_goal_message("rate limit exceeded")
    assert go.is_turnover_seam_trigger(transient) is False


# ---------- S11 docs drift / fixture reconciliation -------------------------

def test_s11_fixture_valid_and_no_drift_recorded():
    data = semantics()
    assert data["task"] == "M0-T106"
    assert data["confidence"] == "official-docs"
    assert data["drift_vs_m0_t102_snapshot"]["differences"] == []
    whole = SEMANTICS_FIXTURE.read_text(encoding="utf-8")
    assert "Users" not in whole and "MLFLL" not in whole


def test_s11_code_matches_fixture_facts():
    data = semantics()
    assert list(data["verdicts"]) == list(go.VERDICTS)
    assert set(data["unrecoverable_clearing"]["classes"]) == set(
        go.UNRECOVERABLE_CLASSES)
    assert data["unrecoverable_clearing"]["warning_prefix"] == go.CLEARED_WARNING_PREFIX
    assert data["unrecoverable_clearing"]["warning_suffix"] == go.CLEARED_WARNING_SUFFIX
    checkins = data["checkins"]
    assert checkins["min_version"] == gk.CHECKINS_MIN_VERSION
    assert checkins["idle_min_version"] == gk.IDLE_CHECKINS_MIN_VERSION
    assert checkins["idle_cap_min_version"] == gk.IDLE_CHECKIN_CAP_MIN_VERSION
    assert checkins["idle_cap"] == gc.IDLE_CHECKIN_CAP
    assert checkins["first_interval_minutes_default"] == gc.DEFAULT_FIRST_INTERVAL_MINUTES
    assert checkins["env_var"] == gc.CHECKIN_ENV_VAR
    assert data["resume"]["all_routes_min_version"] == gk.RESUME_ALL_ROUTES_MIN_VERSION
    assert set(data["resume"]["counters_reset"]) == set(go.RESUME_RESET_COUNTERS)
    assert data["condition"]["max_chars"] == gk.GOAL_CONDITION_MAX_CHARS
    assert list(data["checkins"]["delivery_kinds"]) == list(gc.CHECKIN_KINDS)


def test_s11_version_helpers():
    assert gk.parse_claude_version("2.1.247 (Claude Code)") == (2, 1, 247)
    assert gk.parse_claude_version("nonsense") is None
    assert gk.version_at_least("2.1.247", "2.1.234") is True
    assert gk.version_at_least("2.1.220", "2.1.234") is False
    assert gk.version_at_least("??", "2.1.234") is None
