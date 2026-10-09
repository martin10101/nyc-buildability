"""M0-T091 (D-024 Phase C2) — invisible runtime supervision.

Covers the s16.2 supervision cases: observe produces no worker message;
prepare-to-land prevents new scope/children at the controller level; land
sends ONE concise direction (sparse, durable, within the original
authority); high cumulative usage with coherent near-complete progress
reaches its safe seam instead of being killed for crossing a round number;
low usage with repeated speculation triggers review; a forty-minute-
equivalent low-value investigation is landed/denied in ACCELERATED time
(injected clock, no sleeps); platform TaskStop is reserved for emergency
conditions; SDK/CLI hard caps are never routine sizing and the catastrophic
ceiling proves partial-state recovery; scope drift produces an extension
request, unrelated discoveries become backlog entries, a blocking discovery
gets the least costly bounded extension, and Codex approves/denies without
editing code; an active child finishes its bounded contract during parent
landing, a landed child returns a coherent partial handoff, child API
failure is an EXPLICIT state, nested children cannot evade the producer cap
or leases, parent rotation never creates overlapping writers, and a verbose
child transcript stays out of the primary context.

Also proves the M0-T090 carried pre-activation correction bundle at runtime:
G3 MAJOR-1/G5 M2 (word-boundary band-leak guard), G3 MAJOR-2 + MINOR-3 +
G5 M1 (spaced/spelled percent + conserve-synonym coverage), G3 MINOR-4 +
G5 M3 (lease normalization: root/absolute/traversal/dot-segments), G3
MINOR-5 (size-class error-code registry), G5 M4 (LeaseLedger serializes
grants where bare snapshot validation cannot), G5 N1 (worker_text_fields
fails closed on unscannable types), G4 ADV-1 (non-omittable s13 packet
categories), DCV R063 (likely-evidence-sources clause).

Deterministic; no network; installs nothing.

Supervisor-freeze qualifying evidence: D-024-R101.
"""
from __future__ import annotations

import dataclasses

import pytest

from tools.agent_supervisor import child_handoff as ch
from tools.agent_supervisor import extension_gate as eg
from tools.agent_supervisor import lease_runtime as lr
from tools.agent_supervisor import runtime_detectors as rd
from tools.agent_supervisor import runtime_health as rh
from tools.agent_supervisor import startup_overhead as so
from tools.agent_supervisor import subagent_contracts as sc
from tools.agent_supervisor import workload_classifier as wc
from tools.agent_supervisor import workload_sizing as ws


def _envelope(**overrides) -> sc.SupervisionEnvelope:
    values = dict(
        assignment_id="A-001",
        size_class=wc.COHESIVE_SUBAGENT,
        cohesion_rationale="one bounded unit, one ownership boundary, one "
                           "end-to-end proof",
        write_lease_paths=("tools/pkg",),
        telemetry_sources=("sdk_events",),
        telemetry_confidence="sdk-task-cumulative",
        model_context_window=200_000,
    )
    values.update(overrides)
    return sc.SupervisionEnvelope(**values)


def _snapshot(**overrides) -> rh.TelemetrySnapshot:
    values = dict(
        assignment_id="A-001",
        occupancy_fraction=0.30,
        cumulative_tokens=120_000,
        compaction_count=0,
        elapsed_minutes=10.0,
        source="sdk_events",
        confidence="sdk-task-cumulative",
    )
    values.update(overrides)
    return rh.TelemetrySnapshot(**values)


def _assessment(**overrides) -> rh.ProgressAssessment:
    values = dict(verified_progress=True, coherent=True)
    values.update(overrides)
    return rh.ProgressAssessment(**values)


def _request(**overrides) -> eg.ExtensionRequest:
    values = dict(
        assignment_id="A-001",
        proven="the failing case reproduces on the fixture",
        uncertain="whether the cache layer shares the defect",
        why_blocking="the acceptance test cannot pass while the defect "
                     "stands",
        least_costly_next_experiment="run the cache-layer regression pack "
                                     "against the fixture",
        additional_scope="the cache invalidation module",
        likely_evidence_sources=("tools/pkg/cache.py",
                                 "tools/test_cache.py"),
        natural_completion_point="cache regression pack green",
        resume_vs_new=eg.RESUME_THIS_CONTEXT,
        consequences_of_stopping="the defect ships unfixed",
        blocking_kind=eg.NON_BLOCKING,
    )
    values.update(overrides)
    return eg.ExtensionRequest(**values)


def _handoff(**overrides) -> ch.ChildHandoff:
    values = dict(
        assignment_id="C-1",
        parent_task_id="M0-T091",
        outcome=ch.OUTCOME_PARTIAL_LANDED,
        bounded_summary="reproduced the failure; two of three regression "
                        "cases written and green",
        completed="failure reproduction plus two regression cases",
        repository_state="worktree clean at the child branch head",
        verified_evidence=("pytest output for the two cases",),
        open_questions=("third case needs the fixture from the parent",),
        exact_next_action="write the third regression case",
    )
    values.update(overrides)
    return ch.ChildHandoff(**values)


class _Cfg:
    def __init__(self, raw):
        self.raw = raw


# ---------- band evaluation (s5.4/s5.5, s16.2) ----------

def test_observe_band_produces_no_worker_message():
    evaluation = rh.evaluate_band(_envelope(),
                                  _snapshot(occupancy_fraction=0.60),
                                  _assessment())
    assert evaluation.band == sc.BAND_OBSERVE
    assert evaluation.action == rh.ACTION_EXTERNAL_CHECK
    assert evaluation.worker_message is None
    state = rh.SupervisionState(_envelope())
    assert state.apply(evaluation) is None
    assert not state.landing_directed


def test_normal_band_takes_no_action():
    evaluation = rh.evaluate_band(_envelope(),
                                  _snapshot(occupancy_fraction=0.20),
                                  _assessment())
    assert evaluation.band == sc.BAND_NORMAL
    assert evaluation.action == rh.ACTION_NONE
    assert evaluation.worker_message is None


def test_prepare_to_land_holds_scope_without_worker_message():
    evaluation = rh.evaluate_band(_envelope(),
                                  _snapshot(occupancy_fraction=0.75),
                                  _assessment())
    assert evaluation.band == sc.BAND_PREPARE
    assert evaluation.action == rh.ACTION_HOLD_SCOPE
    assert evaluation.worker_message is None
    state = rh.SupervisionState(_envelope())
    assert state.apply(evaluation) is None
    assert state.scope_held


def test_land_sends_one_concise_direction_exactly_once():
    envelope = _envelope()
    state = rh.SupervisionState(envelope)
    evaluation = rh.evaluate_band(envelope,
                                  _snapshot(occupancy_fraction=0.90),
                                  _assessment(near_complete=False))
    assert evaluation.action == rh.ACTION_SEND_LANDING
    first = state.apply(evaluation, at_minutes=41.0)
    assert first is not None
    assert first.text == rh.LANDING_DIRECTION_TEXT
    # sparse: a repeat evaluation never produces a second message
    assert state.apply(evaluation, at_minutes=42.0) is None
    assert state.landing_record() is first


def test_landing_direction_passes_both_guards_and_carries_no_numbers():
    envelope = _envelope()
    sc.assert_worker_text_clean("landing", rh.LANDING_DIRECTION_TEXT)
    sc.assert_no_envelope_leak(rh.LANDING_DIRECTION_TEXT, envelope)
    assert not any(c.isdigit() for c in rh.LANDING_DIRECTION_TEXT)


def test_high_usage_near_seam_completion_reaches_safe_seam():
    evaluation = rh.evaluate_band(
        _envelope(), _snapshot(occupancy_fraction=0.90,
                               cumulative_tokens=600_000),
        _assessment(near_complete=True))
    assert evaluation.band == sc.BAND_LAND
    assert evaluation.action == rh.ACTION_ALLOW_SEAM
    assert evaluation.worker_message is None


def test_model_losing_thread_is_immediate_quality_signal():
    evaluation = rh.evaluate_band(
        _envelope(), _snapshot(occupancy_fraction=0.30),
        _assessment(model_reports_losing_thread=True))
    assert evaluation.band == sc.BAND_LAND
    assert evaluation.action == rh.ACTION_SEND_LANDING


def test_low_usage_repeated_speculation_triggers_review():
    evaluation = rh.evaluate_band(
        _envelope(), _snapshot(occupancy_fraction=0.15,
                               cumulative_tokens=20_000),
        _assessment(verified_progress=False, no_progress=True))
    assert evaluation.requires_review
    assert evaluation.band == sc.BAND_PREPARE
    assert evaluation.action == rh.ACTION_HOLD_SCOPE


def test_unknown_occupancy_is_conservative_never_normal():
    evaluation = rh.evaluate_band(
        _envelope(), _snapshot(occupancy_fraction=None,
                               confidence="unknown"),
        _assessment())
    assert evaluation.band == sc.BAND_OBSERVE
    assert evaluation.worker_message is None


def test_taskstop_reserved_for_emergency_conditions():
    # ordinary landing occupancy NEVER escalates to the platform stop
    ordinary = rh.evaluate_band(_envelope(),
                                _snapshot(occupancy_fraction=0.90),
                                _assessment())
    assert ordinary.action != rh.ACTION_EMERGENCY_STOP
    # emergency occupancy IS an imminent platform hard limit
    imminent = rh.evaluate_band(_envelope(),
                                _snapshot(occupancy_fraction=0.96),
                                _assessment())
    assert imminent.band == sc.BAND_EMERGENCY
    assert imminent.action == rh.ACTION_EMERGENCY_STOP
    assert imminent.worker_message is None
    # an owner emergency stop fires even at low counters
    owner = rh.evaluate_band(
        _envelope(), _snapshot(occupancy_fraction=0.20), _assessment(),
        emergency_conditions=("owner-emergency-stop",))
    assert owner.action == rh.ACTION_EMERGENCY_STOP
    with pytest.raises(rh.HealthRuntimeError) as err:
        rh.evaluate_band(_envelope(), _snapshot(), _assessment(),
                         emergency_conditions=("bored",))
    assert err.value.code == "bad_emergency_condition"


def test_snapshot_validation_fail_closed():
    with pytest.raises(rh.HealthRuntimeError) as err:
        _snapshot(source="magic")
    assert err.value.code == "unknown_telemetry_source"
    with pytest.raises(rh.HealthRuntimeError) as err:
        _snapshot(confidence="certain")
    assert err.value.code == "bad_confidence"
    with pytest.raises(rh.HealthRuntimeError) as err:
        _snapshot(occupancy_fraction=1.5)
    assert err.value.code == "bad_occupancy"
    with pytest.raises(rh.HealthRuntimeError) as err:
        _snapshot(cumulative_tokens=-1)
    assert err.value.code == "bad_counter"
    with pytest.raises(rh.HealthRuntimeError) as err:
        _snapshot(turns=True)
    assert err.value.code == "bad_counter"
    with pytest.raises(rh.HealthRuntimeError) as err:
        rh.evaluate_band(_envelope(), _snapshot(assignment_id="OTHER"),
                         _assessment())
    assert err.value.code == "unlinked_records"


def test_bands_calibrated_per_resolved_model_fail_closed():
    cfg = _Cfg({"subagent_model_bands": {
        "claude-x": {"land_occupancy": 0.80}}})
    bands = rh.bands_for_model(cfg, "claude-x")
    assert bands.land_occupancy == 0.80
    # a model without an override falls back to the global table
    assert rh.bands_for_model(cfg, "claude-y") == sc.HealthBands()
    with pytest.raises(rh.HealthRuntimeError) as err:
        rh.bands_for_model(_Cfg({"subagent_model_bands": {
            "claude-x": {"kill_at": 0.5}}}), "claude-x")
    assert err.value.code == "unknown_band_key"
    with pytest.raises(rh.HealthRuntimeError):
        rh.bands_for_model(_Cfg({"subagent_model_bands": "nope"}), "m")


# ---------- catastrophic ceiling, never routine sizing (s5.5, s16.2) ------

def test_platform_caps_rejected_as_routine_sizing():
    with pytest.raises(rh.HealthRuntimeError) as err:
        rh.validate_platform_caps(max_turns=50)
    assert err.value.code == "routine_cap"
    with pytest.raises(rh.HealthRuntimeError) as err:
        rh.validate_platform_caps(max_budget_usd=2.0)
    assert err.value.code == "routine_cap"
    ceiling = rh.CatastrophicCeiling(ceiling_tokens=5_000_000,
                                     normal_range_tokens=800_000)
    assert rh.validate_platform_caps(catastrophic=ceiling) is ceiling


def test_catastrophic_ceiling_must_sit_far_outside_normal_range():
    with pytest.raises(rh.HealthRuntimeError) as err:
        rh.CatastrophicCeiling(ceiling_tokens=2_000_000,
                               normal_range_tokens=800_000)
    assert err.value.code == "bad_ceiling"
    with pytest.raises(rh.HealthRuntimeError):
        rh.CatastrophicCeiling(ceiling_tokens=0, normal_range_tokens=1)


def test_ceiling_fire_produces_partial_state_recovery():
    ceiling = rh.CatastrophicCeiling(ceiling_tokens=4_000_000,
                                     normal_range_tokens=800_000)
    assert rh.ceiling_fired(ceiling, _snapshot()) is None
    assert rh.ceiling_fired(
        ceiling, _snapshot(cumulative_tokens=None)) is None
    recovery = rh.ceiling_fired(
        ceiling, _snapshot(cumulative_tokens=4_100_000))
    assert recovery is not None
    assert recovery.quarantined and not recovery.completed
    assert "quarantine-partial-state" in recovery.steps
    assert "reconcile-write-leases" in recovery.steps
    assert "reconcile-external-effects" in recovery.steps
    with pytest.raises(rh.HealthRuntimeError) as err:
        dataclasses.replace(recovery, completed=True)
    assert err.value.code == "false_completion"


# ---------- detectors on the injected clock (s6.2, s16.2) ----------

def _monitor(**kwargs) -> rd.AssignmentMonitor:
    return rd.AssignmentMonitor("A-001", sc.DetectorPolicy(), **kwargs)


def test_repeated_commands_hypotheses_test_failures_trigger_no_progress():
    monitor = _monitor()
    for minute in (1.0, 2.0):
        assert monitor.observe(rd.ActivityEvent(
            at_minutes=minute, kind="command", signature="pytest -k x")) == ()
    findings = monitor.observe(rd.ActivityEvent(
        at_minutes=3.0, kind="command", signature="pytest -k x"))
    assert [f.kind for f in findings] == [rd.FINDING_REPEATED]
    assert findings[0].requires == rd.REQUIRES_LANDING_REVIEW

    monitor2 = _monitor()
    cycling: list[rd.DetectorFinding] = []
    for minute in (1.0, 2.0, 3.0):
        cycling.extend(monitor2.observe(rd.ActivityEvent(
            at_minutes=minute, kind="test-run", signature="test_x",
            outcome="failed")))
    assert [f.kind for f in cycling] == [rd.FINDING_CYCLING_TESTS]

    monitor3 = _monitor()
    monitor3.observe(rd.ActivityEvent(at_minutes=1.0, kind="hypothesis",
                                      signature="the cache is stale"))
    monitor3.observe(rd.ActivityEvent(at_minutes=2.0, kind="hypothesis",
                                      signature="the cache is stale"))
    found = monitor3.observe(rd.ActivityEvent(
        at_minutes=3.0, kind="hypothesis", signature="the cache is stale"))
    assert [f.kind for f in found] == [rd.FINDING_REPEATED]


def test_durable_evidence_resets_counters_and_window():
    monitor = _monitor()
    monitor.observe(rd.ActivityEvent(at_minutes=1.0, kind="search",
                                     signature="grep cache"))
    monitor.observe(rd.ActivityEvent(at_minutes=2.0, kind="search",
                                     signature="grep stale"))
    monitor.observe(rd.ActivityEvent(
        at_minutes=3.0, kind="evidence", signature="repro",
        evidence_kind="reproduced-failure"))
    # counter was reset by the durable evidence; two more searches stay quiet
    assert monitor.observe(rd.ActivityEvent(
        at_minutes=4.0, kind="search", signature="grep invalidate")) == ()
    assert monitor.check(22.0) == ()  # window restarts at minute 3
    findings = monitor.check(23.0)
    assert [f.kind for f in findings] == [rd.FINDING_NO_PROGRESS]


def test_text_volume_and_tool_activity_are_not_progress():
    monitor = _monitor()
    for minute in range(1, 20):
        monitor.observe(rd.ActivityEvent(
            at_minutes=float(minute), kind="command",
            signature=f"cmd-{minute}"))
    findings = monitor.check(20.0)
    assert [f.kind for f in findings] == [rd.FINDING_NO_PROGRESS]


def test_forty_minute_equivalent_investigation_landed_in_accelerated_time():
    """s16.2: a forty-minute-equivalent low-value investigation is landed or
    denied in accelerated time — injected minutes, no real waiting."""
    monitor = _monitor()
    all_findings: list[rd.DetectorFinding] = []
    for minute in (5.0, 10.0, 15.0):
        all_findings.extend(monitor.observe(rd.ActivityEvent(
            at_minutes=minute, kind="search",
            signature=f"broad search {minute:g}")))
    all_findings.extend(monitor.check(40.0))
    kinds = {f.kind for f in all_findings}
    assert rd.FINDING_UNBOUNDED_SEARCH in kinds
    assert rd.FINDING_NO_PROGRESS in kinds
    # the merely-interesting extension is denied and deferred
    decision, entry = eg.decide_extension(
        _request(blocking_kind=eg.NON_BLOCKING,
                 why_blocking="it is interesting"),
        findings=tuple(all_findings), at_minutes=40.0)
    assert decision.decision == eg.DECISION_DENY_BACKLOG
    assert entry is not None
    # and the controller lands the assignment: one message, no TaskStop
    evaluation = rh.evaluate_band(
        _envelope(), _snapshot(occupancy_fraction=0.40),
        _assessment(verified_progress=False, no_progress=True,
                    near_complete=False, coherent=False))
    assert evaluation.requires_review
    assert evaluation.action != rh.ACTION_EMERGENCY_STOP


def test_successive_summaries_without_evidence_stall_out():
    monitor = _monitor()
    monitor.observe(rd.ActivityEvent(at_minutes=1.0, kind="summary",
                                     signature="progress summary 1"))
    findings = monitor.observe(rd.ActivityEvent(
        at_minutes=2.0, kind="summary", signature="progress summary 2"))
    assert [f.kind for f in findings] == [rd.FINDING_STALLED_SUMMARIES]


def test_scope_drift_produces_extension_request_not_silent_continuation():
    monitor = _monitor(lease_paths=("tools/pkg",))
    findings = monitor.observe(rd.ActivityEvent(
        at_minutes=5.0, kind="file-write", signature="edit",
        paths=("tools/other/module.py",)))
    assert [f.kind for f in findings] == [rd.FINDING_SCOPE_DRIFT]
    assert findings[0].requires == rd.REQUIRES_EXTENSION_REVIEW
    # inside the lease: no finding
    assert monitor.observe(rd.ActivityEvent(
        at_minutes=6.0, kind="file-write", signature="edit",
        paths=("tools/pkg/module.py",))) == ()


def test_repeated_corrections_get_outside_decision_without_countdown():
    """s16.2: repeated correction attempts trigger an OUTSIDE no-progress
    decision; the worker is never shown a countdown or counter."""
    monitor = _monitor()
    findings: list[rd.DetectorFinding] = []
    for minute in (1.0, 2.0, 3.0):
        findings.extend(monitor.observe(rd.ActivityEvent(
            at_minutes=minute, kind="command",
            signature="apply the same fix")))
    assert [f.kind for f in findings] == [rd.FINDING_REPEATED]
    finding = findings[0]
    # findings are controller records with NO worker-facing surface
    assert not hasattr(finding, "worker_message")
    field_names = {f.name for f in dataclasses.fields(finding)}
    assert field_names == {"assignment_id", "kind", "detail", "at_minutes",
                           "requires"}


def test_event_validation_fail_closed():
    with pytest.raises(rd.DetectorError) as err:
        rd.ActivityEvent(at_minutes=1.0, kind="magic", signature="x")
    assert err.value.code == "bad_event_kind"
    with pytest.raises(rd.DetectorError) as err:
        rd.ActivityEvent(at_minutes=1.0, kind="evidence", signature="x",
                         evidence_kind="vibes")
    assert err.value.code == "bad_evidence_kind"
    with pytest.raises(rd.DetectorError) as err:
        rd.ActivityEvent(at_minutes=1.0, kind="command", signature="x",
                         evidence_kind="bounded-diff")
    assert err.value.code == "bad_evidence_kind"
    with pytest.raises(rd.DetectorError) as err:
        rd.ActivityEvent(at_minutes=-1.0, kind="command", signature="x")
    assert err.value.code == "bad_clock"


# ---------- extension gate (s6.1, s16.2) ----------

def test_unrelated_discovery_defaults_to_backlog():
    entry = eg.backlog_unrelated_discovery(
        "A-001", "the logging module double-encodes UTF-8", at_minutes=12.0)
    assert entry.created_from == "unrelated-discovery"
    decision, backlog = eg.decide_extension(_request(
        blocking_kind=eg.NON_BLOCKING,
        why_blocking="worth investigating some day"))
    assert decision.decision == eg.DECISION_DENY_BACKLOG
    assert backlog is not None
    assert backlog.created_from == "denied-extension"


def test_blocking_discovery_gets_least_costly_bounded_extension():
    request = _request(blocking_kind="current-acceptance-criterion")
    decision, entry = eg.decide_extension(request)
    assert decision.decision == eg.DECISION_APPROVE
    assert entry is None
    assert decision.bounded_addition == request.least_costly_next_experiment
    assert decision.completion_point == request.natural_completion_point


def test_extension_decision_is_a_record_not_a_code_edit():
    decision, _ = eg.decide_extension(_request(blocking_kind="correctness"))
    for verb in ("apply", "execute", "run", "edit", "write"):
        assert not hasattr(decision, verb)
    with pytest.raises(eg.ExtensionError) as err:
        eg.ExtensionDecision(assignment_id="A-001",
                             decision=eg.DECISION_APPROVE, reasons=())
    assert err.value.code == "unbounded_approval"


def test_extension_request_validation_fail_closed():
    with pytest.raises(eg.ExtensionError) as err:
        _request(proven=" ")
    assert err.value.code == "incomplete_request"
    with pytest.raises(eg.ExtensionError) as err:
        _request(likely_evidence_sources=())
    assert err.value.code == "incomplete_request"
    with pytest.raises(eg.ExtensionError) as err:
        _request(resume_vs_new="whatever")
    assert err.value.code == "bad_resume_choice"
    with pytest.raises(eg.ExtensionError) as err:
        _request(blocking_kind="curiosity")
    assert err.value.code == "bad_blocking_kind"
    with pytest.raises(eg.ExtensionError) as err:
        _request(changed_anything=True)
    assert err.value.code == "missing_checkpoint"


# ---------- lease runtime: serialized grants (G5 M4, s6, s16.2) ----------

def test_grant_ledger_serializes_where_snapshot_validation_cannot():
    """G5 M4: two candidates both pass against the SAME empty snapshot, but
    the ledger folds each grant into the active set so the second is
    refused."""
    first = _envelope(assignment_id="W-1", write_lease_paths=("tools/pkg",))
    second = _envelope(assignment_id="W-2",
                       write_lease_paths=("tools/pkg/sub",))
    # the documented snapshot hole: both pass against the same snapshot
    sc.assert_grantable((), first)
    sc.assert_grantable((), second)
    # the runtime ledger closes it
    ledger = lr.LeaseLedger()
    ledger.grant(first)
    with pytest.raises(sc.ContractError) as err:
        ledger.grant(second)
    assert err.value.code == "lease_overlap"


def test_nested_children_cannot_evade_producer_cap_or_leases():
    ledger = lr.LeaseLedger()
    ledger.grant(_envelope(assignment_id="W-1",
                           write_lease_paths=("tools/a",)))
    ledger.grant(_envelope(assignment_id="W-2",
                           write_lease_paths=("tools/b",)))
    ledger.grant(_envelope(assignment_id="W-3",
                           write_lease_paths=("tools/c",)),
                 parent_assignment_id="W-1")
    # a NESTED fourth writer hits the same cap as a top-level one
    with pytest.raises(sc.ContractError) as err:
        ledger.grant(_envelope(assignment_id="W-4",
                               write_lease_paths=("tools/d",)),
                     parent_assignment_id="W-2")
    assert err.value.code == "producer_cap"
    # a nested overlapping lease is refused through the same fold
    ledger.release("W-3")
    with pytest.raises(sc.ContractError) as err:
        ledger.grant(_envelope(assignment_id="W-5",
                               write_lease_paths=("tools/a/sub",)),
                     parent_assignment_id="W-1")
    assert err.value.code == "lease_overlap"


def test_ledger_exactness_duplicate_unknown_parent_and_drain_rules():
    ledger = lr.LeaseLedger()
    parent = _envelope(assignment_id="W-1", write_lease_paths=("tools/a",))
    ledger.grant(parent)
    with pytest.raises(lr.LeaseRuntimeError) as err:
        ledger.grant(parent)
    assert err.value.code == "duplicate_grant"
    with pytest.raises(lr.LeaseRuntimeError) as err:
        ledger.grant(_envelope(assignment_id="W-2",
                               write_lease_paths=("tools/b",)),
                     parent_assignment_id="GHOST")
    assert err.value.code == "unknown_parent"
    ledger.grant(_envelope(assignment_id="W-2",
                           write_lease_paths=("tools/b",)),
                 parent_assignment_id="W-1")
    with pytest.raises(lr.LeaseRuntimeError) as err:
        ledger.release("W-1")
    assert err.value.code == "children_not_drained"
    ledger.release("W-2")
    ledger.release("W-1")
    assert ledger.writer_count() == 0


def test_scope_enforcement_fails_closed():
    ledger = lr.LeaseLedger()
    ledger.grant(_envelope(assignment_id="W-1",
                           write_lease_paths=("tools/pkg",)))
    ledger.assert_write_within_scope("W-1", "tools/pkg/module.py")
    with pytest.raises(lr.LeaseRuntimeError) as err:
        ledger.assert_write_within_scope("W-1", "tools/other/module.py")
    assert err.value.code == "scope_violation"
    with pytest.raises(lr.LeaseRuntimeError) as err:
        ledger.assert_write_within_scope("GHOST", "tools/pkg/module.py")
    assert err.value.code == "unknown_grant"
    reader = _envelope(assignment_id="R-1", write_lease_paths=())
    ledger.grant(reader)
    with pytest.raises(lr.LeaseRuntimeError) as err:
        ledger.assert_write_within_scope("R-1", "tools/pkg/module.py")
    assert err.value.code == "scope_violation"


def test_read_only_agents_do_not_consume_the_producer_cap():
    ledger = lr.LeaseLedger()
    for i in range(5):
        ledger.grant(_envelope(assignment_id=f"R-{i}",
                               write_lease_paths=()))
    ledger.grant(_envelope(assignment_id="W-1",
                           write_lease_paths=("tools/a",)))
    assert ledger.writer_count() == 1


# ---------- child handoffs and turnover draining (s6.3, s16.2) ----------

def test_active_child_finishes_bounded_contract_during_parent_landing():
    coordinator = ch.TurnoverCoordinator("M0-T091")
    coordinator.register_child("C-1")
    coordinator.begin_landing()
    assert coordinator.child_may_continue("C-1", healthy=True)
    assert not coordinator.child_may_continue("C-1", healthy=False)
    assert not coordinator.may_spawn_children()
    with pytest.raises(ch.HandoffError) as err:
        coordinator.register_child("C-2")
    assert err.value.code == "landing_in_progress"


def test_child_landing_returns_one_instruction_and_partial_handoff():
    coordinator = ch.TurnoverCoordinator("M0-T091")
    coordinator.register_child("C-1")
    instruction = coordinator.land_child("C-1")
    assert instruction == rh.LANDING_DIRECTION_TEXT
    assert coordinator.land_child("C-1") is None  # sparse
    handoff = _handoff()
    coordinator.record_child_handoff(handoff)
    assert coordinator.unreconciled_children() == ()
    assert coordinator.handoff_for("C-1") is handoff


def test_child_api_failure_is_an_explicit_state():
    failed = _handoff(outcome=ch.OUTCOME_FAILED_API,
                      api_error="provider returned 529 after 3 retries",
                      completed="", repository_state="",
                      exact_next_action="")
    assert failed.outcome == ch.OUTCOME_FAILED_API
    with pytest.raises(ch.HandoffError) as err:
        _handoff(outcome=ch.OUTCOME_FAILED_API, api_error="  ",
                 completed="", repository_state="", exact_next_action="")
    assert err.value.code == "missing_api_error"


def test_handoff_validation_fail_closed():
    with pytest.raises(ch.HandoffError) as err:
        _handoff(outcome="vanished")
    assert err.value.code == "bad_outcome"
    with pytest.raises(ch.HandoffError) as err:
        _handoff(exact_next_action=" ")
    assert err.value.code == "incomplete_handoff"
    with pytest.raises(ch.HandoffError) as err:
        _handoff(bounded_summary=" ")
    assert err.value.code == "missing_summary"


def test_verbose_child_transcript_stays_out_of_primary_context():
    bounded = _handoff(bounded_summary="x" * ch.MAX_SUMMARY_CHARS)
    assert len(bounded.bounded_summary) == ch.MAX_SUMMARY_CHARS
    with pytest.raises(ch.HandoffError) as err:
        _handoff(bounded_summary="x" * (ch.MAX_SUMMARY_CHARS + 1))
    assert err.value.code == "transcript_not_summary"


def test_parent_rotation_never_creates_overlapping_writers():
    ledger = lr.LeaseLedger()
    coordinator = ch.TurnoverCoordinator("M0-T091")
    coordinator.register_child("C-1")
    ledger.grant(_envelope(assignment_id="C-1",
                           write_lease_paths=("tools/pkg",)))
    # the successor may orient read-only at any time...
    assert coordinator.successor_may_orient_read_only()
    # ...but gains no write authority while the child is unreconciled
    assert not coordinator.successor_may_dispatch_writes(
        ledger, external_effects_reconciled=True)
    coordinator.record_child_handoff(_handoff())
    # still refused: the child's write lease is live in the ledger
    assert not coordinator.successor_may_dispatch_writes(
        ledger, external_effects_reconciled=True)
    ledger.release("C-1")
    assert not coordinator.successor_may_dispatch_writes(
        ledger, external_effects_reconciled=False)
    assert coordinator.successor_may_dispatch_writes(
        ledger, external_effects_reconciled=True)


# ---------- carried correction bundle regressions (M0-T090 gates) ----------

def test_leak_guard_word_boundary_passes_common_english():
    """G3 MAJOR-1 / G5 M2: 'landing', 'island', 'England', 'observe the
    failing test' are ordinary engineering English, not band leaks."""
    envelope = _envelope()
    for text in (
            "Repair the landing page hero section.",
            "Observe the failing test and record the traceback.",
            "Add the island lookup for the England dataset.",
            "The flatland renderer misplaces landmarks.",
    ):
        sc.assert_no_envelope_leak(text, envelope)


def test_leak_guard_still_catches_band_vocabulary():
    envelope = _envelope()
    for text in (
            "finish the step; band prepare_to_land is close",
            "you should prepare to land now",
            "emergency stop is next",
            "the observe band is active",
            "health band land was reached",
    ):
        with pytest.raises(sc.ContractError) as err:
            sc.assert_no_envelope_leak(text, envelope)
        assert err.value.code == "envelope_leak"


def test_leak_guard_catches_spaced_and_spelled_percent_thresholds():
    """G3 MINOR-3 / G5 M1: a band threshold cannot leak by reformatting."""
    envelope = _envelope()
    for text in ("you are at 70 % now", "70 percent of context used",
                 "occupancy 0.7 reached", "85% consumed"):
        with pytest.raises(sc.ContractError) as err:
            sc.assert_no_envelope_leak(text, envelope)
        assert err.value.code == "envelope_leak"


@pytest.mark.parametrize("phrase", [
    "Keep it under 70 % if you can.",
    "Use about 70 percent of context.",
    "Please save tokens where possible.",
    "Be economical with the budget.",
    "Be frugal with your context.",
    "Spare the tokens for later.",
])
def test_quota_guard_catches_paraphrased_pressure(phrase):
    """G3 MAJOR-2 / G5 M1: spaced percent, spelled percent, and
    conserve-synonym pressure are the same prohibited rationing."""
    with pytest.raises(sc.ContractError) as err:
        sc.assert_worker_text_clean("probe", phrase)
    assert err.value.code == "quota_language"


def test_quota_guard_still_accepts_plain_engineering_language():
    for phrase in (
            "Save and test what is coherent before returning.",
            "Fix the economical-mode renderer.",
            "The budget module parses fiscal years.",
    ):
        sc.assert_worker_text_clean("probe", phrase)


def test_root_lease_rejected_not_dodged():
    """G3 MINOR-4: a root lease used to normalize to '' and overlap
    nothing; now it is refused outright."""
    with pytest.raises(sc.ContractError) as err:
        sc.validate_envelope(_envelope(write_lease_paths=("/",)))
    assert err.value.code == "bad_lease_path"
    ledger = lr.LeaseLedger()
    with pytest.raises(sc.ContractError) as err:
        ledger.grant(_envelope(write_lease_paths=("/",)))
    assert err.value.code == "bad_lease_path"


def test_lease_paths_normalize_dot_segments_and_reject_traversal():
    """G5 M3: './pkg' and 'pkg/./sub' can no longer dodge overlap;
    absolute and traversal paths are refused."""
    assert sc._scopes_overlap(("./pkg",), ("pkg",)) is not None
    assert sc._scopes_overlap(("pkg/./sub",), ("pkg/sub",)) is not None
    for bad in ("pkg/../other", "/abs/path", "C:\\abs\\path", "..", "  "):
        with pytest.raises(sc.ContractError) as err:
            sc.validate_envelope(_envelope(write_lease_paths=(bad,)))
        assert err.value.code == "bad_lease_path"


def test_size_class_error_codes_registered_consistently():
    """G3 MINOR-5: both pinned error surfaces are registered in ONE closed
    set, so callers treat an invalid size class as one condition."""
    with pytest.raises(sc.ContractError) as err:
        sc.validate_envelope(_envelope(size_class="huge"))
    assert err.value.code in wc.SIZE_CLASS_ERROR_CODES
    with pytest.raises(wc.WorkloadError) as err:
        so.StartupObservation(assignment_id="A", size_class="huge")
    assert err.value.code in wc.SIZE_CLASS_ERROR_CODES
    assert set(wc.SIZE_CLASS_ERROR_CODES) == {"bad_declared_class",
                                              "bad_size_class"}


def test_worker_text_fields_fail_closed_on_unscannable_types():
    """G5 N1: a worker-facing field the guard cannot scan is refused, never
    silently skipped."""
    assignment = dataclasses.replace(
        sc.WorkerAssignment(
            assignment_id="A-001", parent_task_id="M0-T091",
            exact_change="do the bounded thing",
            necessity="required by the accepted task",
            role=sc.ROLE_READ_ONLY,
            deliverable_schema="a bounded report",
            acceptance_criteria=("the report answers the question",)),
        required_evidence=({"a": 1},))
    with pytest.raises(sc.ContractError) as err:
        assignment.worker_text_fields()
    assert err.value.code == "unscannable_field"
    broken = dataclasses.replace(assignment, required_evidence=(),
                                 checkpoints=None)
    with pytest.raises(sc.ContractError) as err:
        broken.worker_text_fields()
    assert err.value.code == "unscannable_field"
    # the bool flag stays explicitly scannable-exempt
    fine = dataclasses.replace(assignment, required_evidence=())
    names = [name for name, _ in fine.worker_text_fields()]
    assert "checkpoint_commit_allowed" not in names


def test_extension_protocol_carries_likely_evidence_sources():
    """DCV R063 advisory: the s6.1 'likely evidence sources' clause is in
    the default worker extension protocol."""
    assert "likely evidence sources" in sc.DEFAULT_EXTENSION_PROTOCOL


def test_mandatory_packet_categories_cannot_be_omitted():
    """G4 ADV-1: the bounded task, authority/prohibitions, and return
    schema are never omittable; role-dependent categories still are."""
    hood = ws.GraphNeighborhood(seed_path="tools/a.py",
                                files=("tools/a.py",))
    signals = ws.tier_signals(hood)
    for category in ws.NON_OMITTABLE_CATEGORIES:
        with pytest.raises(ws.SizingError) as err:
            ws.packet_plan(assignment_id="A-1", role="reviewer",
                           neighborhood=hood, signals=signals,
                           omissions=((category, "a justification"),))
        assert err.value.code == "non_omittable_category"
    plan = ws.packet_plan(
        assignment_id="A-1", role="reviewer", neighborhood=hood,
        signals=signals,
        omissions=(("known_decisions_and_risks",
                    "reviewer reconstructs decisions from durable "
                    "evidence"),))
    assert plan.sufficient
    assert "known_decisions_and_risks" not in plan.included
