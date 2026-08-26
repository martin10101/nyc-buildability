"""M0-T090 (D-024 Phase C1) — bounded subagent contracts + structural
workload sizing.

Covers the s16.2 sizing cases: vague/oversized rejected or split; tiny
targeted work stays in the main session; follow-up resumes a healthy
resumable subagent; an overloaded/confused subagent is not resumed; a fork
only when parent inheritance is beneficial and the parent is clean; one
cohesive unit is not fragmented; oversized work splits at seams; unknown
work gets reconnaissance first; startup packet size / repeated loading /
files reopened / time-to-first-evidence are measured for calibration; a
lower-tier model is selected only when window and demonstrated capability
fit; more than three concurrent producers is rejected; overlapping write
scopes cannot both obtain leases; scope/resource conflicts fail closed —
plus the no-quota-in-worker-prompt proof (D-024-R045) with an INDEPENDENT
scan, and the envelope-leak guard (s6: supervision numbers never reach the
worker). Also discharges the carried M0-T099 advisory G3-M1 (eviction-order
isolation: newer-completed vs older-active) for both SdkTaskTracker and
SubagentRegistry — hosted here because the sibling telemetry pack is outside
this task's allowed paths (placement recorded in the task report).

Deterministic; no network; installs nothing.

Supervisor-freeze qualifying evidence: D-024-R101.
"""
from __future__ import annotations

import re

import pytest

from tools.agent_supervisor import spawn_decision as sd
from tools.agent_supervisor import startup_overhead as so
from tools.agent_supervisor import subagent_contracts as sc
from tools.agent_supervisor import telemetry_hooks as th
from tools.agent_supervisor import telemetry_sdk as ts
from tools.agent_supervisor import workload_classifier as wc
from tools.agent_supervisor import workload_sizing as ws
from tools import context_pack_budget as budget

NOW = "2026-08-26T12:00:00+00:00"


def _assignment(**overrides) -> sc.WorkerAssignment:
    values = dict(
        assignment_id="A-001",
        parent_task_id="M0-T090",
        exact_change="Add the missing eviction-order regression case to the "
                     "tracker test pack and prove it red/green.",
        necessity="Pins accepted eviction behavior against an oldest-first "
                  "regression.",
        role=sc.ROLE_WRITE,
        permitted_paths=("tools/test_example.py",),
        deliverable_schema="unified diff plus the passing pytest output",
        acceptance_criteria=("the new case fails on an oldest-first mutant "
                             "and passes on the accepted implementation",),
    )
    values.update(overrides)
    return sc.WorkerAssignment(**values)


def _envelope(**overrides) -> sc.SupervisionEnvelope:
    values = dict(
        assignment_id="A-001",
        size_class=wc.COHESIVE_SUBAGENT,
        cohesion_rationale="one test file, one ownership boundary, one "
                           "red/green proof",
        write_lease_paths=("tools/test_example.py",),
        telemetry_sources=("sdk_events", "hook_events"),
        telemetry_confidence="sdk-task-cumulative",
        model_context_window=200_000,
    )
    values.update(overrides)
    return sc.SupervisionEnvelope(**values)


# ---------- structural classification (s5.5, s16.2) ----------

def test_vague_assignment_rejected():
    with pytest.raises(sc.ContractError) as err:
        sc.validate_assignment(_assignment(
            exact_change="Investigate and fix everything related to tests."))
    assert err.value.code == "vague_assignment"


def test_empty_exact_change_rejected():
    with pytest.raises(sc.ContractError) as err:
        sc.validate_assignment(_assignment(exact_change="   "))
    assert err.value.code == "vague_assignment"


def test_oversized_cross_boundary_splits_at_seams():
    features = wc.WorkloadFeatures(
        file_count=9, write_owner_count=2, independent_outcome_count=3,
        seam_candidates=("api-connector boundary", "frontend boundary"))
    result = wc.classify_workload(features)
    assert result.work_class == wc.OVERSIZED_SPLIT
    assert result.split_seams == features.seam_candidates
    assert "write_owner_count" in result.features_used
    decision = sd.decide_spawn(result)
    assert decision.decision == sd.DECIDE_SPLIT_FIRST


def test_unknown_work_gets_recon_first():
    result = wc.classify_workload(wc.WorkloadFeatures())
    assert result.work_class == wc.UNKNOWN_RECON
    assert result.reason_code == "no_objective_features"
    decision = sd.decide_spawn(result)
    assert decision.decision == sd.DECIDE_RECON_FIRST


def test_stale_graph_is_reported_never_used():
    result = wc.classify_workload(wc.WorkloadFeatures(
        file_count=3, end_to_end_provable=True, write_owner_count=1,
        graph_stale=True))
    assert result.work_class == wc.UNKNOWN_RECON
    assert result.reason_code == "graph_stale"
    stale = ws.GraphNeighborhood(seed_path="tools/a.py", stale=True,
                                 stale_reason="fingerprint mismatch")
    with pytest.raises(ws.SizingError) as err:
        ws.tier_signals(stale)
    assert err.value.code == "stale_graph"


def test_tiny_targeted_work_stays_in_main_session():
    result = wc.classify_workload(
        wc.WorkloadFeatures(single_small_edit=True, file_count=1))
    assert result.work_class == wc.MAIN_SESSION
    ledger = so.OverheadLedger()
    ledger.record(so.StartupObservation(
        assignment_id="A-h", size_class=wc.COHESIVE_SUBAGENT,
        startup_tokens=18_000, recorded_at_utc=NOW))
    decision = sd.decide_spawn(result, calibration=ledger.calibration())
    assert decision.decision == sd.DECIDE_STAY_MAIN
    assert decision.reason_code == "micro_spawn_churn"


def test_frequent_parent_decisions_stay_main():
    result = wc.classify_workload(wc.WorkloadFeatures(
        file_count=3, requires_frequent_parent_decisions=True))
    assert result.work_class == wc.MAIN_SESSION


def test_cohesive_unit_is_one_subagent_not_fragments():
    result = wc.classify_workload(wc.WorkloadFeatures(
        file_count=5, write_owner_count=1, end_to_end_provable=True))
    assert result.work_class == wc.COHESIVE_SUBAGENT
    decision = sd.decide_spawn(result)
    assert decision.decision == sd.DECIDE_SPAWN_NEW
    assert decision.reason_code == "cohesive_new_unit"


def test_cohesion_unproven_is_never_optimistic():
    result = wc.classify_workload(wc.WorkloadFeatures(
        file_count=6, write_owner_count=1))
    assert result.work_class == wc.UNKNOWN_RECON
    assert result.reason_code == "cohesion_unproven"


def test_declared_class_recorded_and_validated():
    result = wc.classify_workload(wc.WorkloadFeatures(
        declared_class=wc.MAIN_SESSION))
    assert result.work_class == wc.MAIN_SESSION
    assert result.reason_code == "declared_class"
    with pytest.raises(wc.WorkloadError):
        wc.WorkloadFeatures(declared_class="huge")


def test_workload_thresholds_config_fail_closed():
    class Cfg:
        raw = {"subagent_workload": {"oversized_breadth": 30}}
    th_cfg = wc.WorkloadThresholds.from_controller_config(Cfg())
    assert th_cfg.oversized_breadth == 30

    class Bad:
        raw = {"subagent_workload": {"nonsense": 1}}
    with pytest.raises(wc.WorkloadError) as err:
        wc.WorkloadThresholds.from_controller_config(Bad())
    assert err.value.code == "unknown_workload_key"

    class Neg:
        raw = {"subagent_workload": {"oversized_breadth": 0}}
    with pytest.raises(wc.WorkloadError):
        wc.WorkloadThresholds.from_controller_config(Neg())


# ---------- goldilocks resume / fork (s6, s16.2) ----------

def _cohesive() -> wc.WorkloadClassification:
    return wc.classify_workload(wc.WorkloadFeatures(
        file_count=4, write_owner_count=1, end_to_end_provable=True))


def test_followup_resumes_healthy_subagent():
    decision = sd.decide_spawn(_cohesive(), existing=sd.ExistingSubagentHealth(
        assignment_id="A-prev", same_coherent_assignment=True, healthy=True))
    assert decision.decision == sd.DECIDE_RESUME_EXISTING
    assert decision.reason_code == "resume_healthy"


def test_overloaded_subagent_never_resumed_to_save_startup():
    decision = sd.decide_spawn(_cohesive(), existing=sd.ExistingSubagentHealth(
        assignment_id="A-prev", same_coherent_assignment=True, healthy=False,
        overloaded_or_confused=True))
    assert decision.decision == sd.DECIDE_SPAWN_NEW
    assert decision.reason_code == "unhealthy_not_resumed"


def test_unrelated_existing_subagent_is_ignored():
    decision = sd.decide_spawn(_cohesive(), existing=sd.ExistingSubagentHealth(
        assignment_id="A-other", same_coherent_assignment=False, healthy=True))
    assert decision.decision == sd.DECIDE_SPAWN_NEW


def test_fork_only_when_clean_and_beneficial():
    forked = sd.decide_spawn(_cohesive(), parent=sd.ParentContextState(
        context_clean=True, inheritance_beneficial=True))
    assert forked.decision == sd.DECIDE_FORK_PARENT
    bloated = sd.decide_spawn(_cohesive(), parent=sd.ParentContextState(
        context_clean=False, inheritance_beneficial=True))
    assert bloated.decision == sd.DECIDE_SPAWN_NEW
    assert bloated.reason_code == "bloated_parent_not_forked"
    no_benefit = sd.decide_spawn(_cohesive(), parent=sd.ParentContextState(
        context_clean=True, inheritance_beneficial=False))
    assert no_benefit.decision == sd.DECIDE_SPAWN_NEW


# ---------- model routing (s6, s16.2) ----------

def test_lower_tier_model_needs_window_and_demonstrated_capability():
    unknown = sd.model_fit(resolved_model="tier-low",
                           model_context_window=None,
                           packet_target_tokens=8_000,
                           demonstrated_capable=True)
    assert not unknown.ok and unknown.reason_code == "window_unknown"
    small = sd.model_fit(resolved_model="tier-low",
                         model_context_window=16_000,
                         packet_target_tokens=8_000,
                         demonstrated_capable=True)
    assert not small.ok and small.reason_code == "window_too_small"
    undemo = sd.model_fit(resolved_model="tier-low",
                          model_context_window=200_000,
                          packet_target_tokens=8_000,
                          demonstrated_capable=False)
    assert not undemo.ok and undemo.reason_code == "capability_undemonstrated"
    fits = sd.model_fit(resolved_model="tier-low",
                        model_context_window=200_000,
                        packet_target_tokens=8_000,
                        demonstrated_capable=True)
    assert fits.ok


def test_model_fit_rejects_bad_inputs():
    with pytest.raises(sd.SpawnDecisionError):
        sd.model_fit(resolved_model="m", model_context_window=1,
                     packet_target_tokens=0, demonstrated_capable=True)


# ---------- no-quota proof (D-024-R045, s16.2) ----------

#: Independent scan — deliberately NOT the module's own pattern table, so the
#: proof does not trust the guard it is proving.
_INDEPENDENT_QUOTA_SCAN = tuple(re.compile(p, re.IGNORECASE) for p in (
    r"\d[\d,_.]*\s*(?:k|m)?\s*tokens",
    r"tokens?\s+(?:left|remaining)",
    r"token\s+(?:budget|quota|limit)",
    r"conserve",
    r"countdown",
    r"\d{1,3}\s*%",
    r"budget",
))


def test_worker_prompt_contains_no_quota_language():
    prompt = sc.render_worker_prompt(_assignment(), _envelope())
    for pattern in _INDEPENDENT_QUOTA_SCAN:
        assert not pattern.search(prompt), \
            f"worker prompt leaked pressure phrasing: {pattern.pattern}"
    assert "A-001" in prompt and "M0-T090" in prompt


@pytest.mark.parametrize("phrase", [
    "You have 5000 tokens for this work.",
    "Watch your remaining budget while editing.",
    "Please conserve tokens where possible.",
    "A countdown applies to this assignment.",
    "Stay under 20% of your context window.",
    "Your token budget is generous.",
    "Use a maximum spend of two dollars.",
    "About 3.5k tokens should suffice.",
])
def test_quota_language_rejected_fail_closed(phrase):
    with pytest.raises(sc.ContractError) as err:
        sc.validate_assignment(_assignment(
            exact_change=f"Do the work. {phrase}"))
    assert err.value.code == "quota_language"


def test_quota_guard_covers_every_worker_field():
    with pytest.raises(sc.ContractError) as err:
        sc.validate_assignment(_assignment(
            acceptance_criteria=("finish within the token budget",)))
    assert err.value.code == "quota_language"
    with pytest.raises(sc.ContractError) as err:
        sc.validate_assignment(_assignment(
            handoff_requirements="Hand off with 1000 tokens to spare."))
    assert err.value.code == "quota_language"


def test_envelope_numbers_never_leak_into_worker_text():
    envelope = _envelope()
    with pytest.raises(sc.ContractError) as err:
        sc.assert_no_envelope_leak(
            "finish the step; band prepare_to_land is close", envelope)
    assert err.value.code == "envelope_leak"
    with pytest.raises(sc.ContractError) as err:
        sc.assert_no_envelope_leak(
            f"the window is {envelope.model_context_window}", envelope)
    assert err.value.code == "envelope_leak"
    with pytest.raises(sc.ContractError) as err:
        sc.assert_no_envelope_leak("occupancy 0.7 reached", envelope)
    assert err.value.code == "envelope_leak"
    # the legitimately rendered prompt passes the same guard
    sc.assert_no_envelope_leak(
        sc.render_worker_prompt(_assignment(), envelope), envelope)


def test_rendered_prompt_carries_required_duties():
    prompt = sc.render_worker_prompt(_assignment(), _envelope())
    assert sc.DEFAULT_BLOCKER_REPORTING in prompt
    assert sc.DEFAULT_EXTENSION_PROTOCOL in prompt
    assert sc.DEFAULT_UNRELATED_DISCOVERY in prompt
    assert sc.DEFAULT_HANDOFF_REQUIREMENTS in prompt
    assert "Checkpoint/commit allowed: no" in prompt


# ---------- pair validation, leases, producer cap (s6, s16.2) ----------

def test_pair_ids_must_link():
    with pytest.raises(sc.ContractError) as err:
        sc.validate_pair(_assignment(), _envelope(assignment_id="A-999"))
    assert err.value.code == "unlinked_records"


def test_write_role_requires_scope_and_lease():
    with pytest.raises(sc.ContractError) as err:
        sc.validate_assignment(_assignment(permitted_paths=()))
    assert err.value.code == "write_without_scope"
    with pytest.raises(sc.ContractError) as err:
        sc.validate_pair(_assignment(), _envelope(write_lease_paths=()))
    assert err.value.code == "write_without_lease"
    with pytest.raises(sc.ContractError) as err:
        sc.validate_pair(
            _assignment(role=sc.ROLE_READ_ONLY, permitted_paths=()),
            _envelope())
    assert err.value.code == "lease_without_write"


def test_read_only_pair_needs_no_lease():
    sc.validate_pair(
        _assignment(role=sc.ROLE_REVIEW_ONLY, permitted_paths=()),
        _envelope(write_lease_paths=()))


def test_overlapping_write_scopes_cannot_both_obtain_leases():
    held = (_envelope(assignment_id="W-1",
                      write_lease_paths=("services/api/app",)),)
    nested = _envelope(assignment_id="W-2",
                       write_lease_paths=("services/api/app/routes.py",))
    with pytest.raises(sc.ContractError) as err:
        sc.assert_grantable(held, nested)
    assert err.value.code == "lease_overlap"
    windows_form = _envelope(assignment_id="W-3",
                             write_lease_paths=("services\\api\\app",))
    with pytest.raises(sc.ContractError):
        sc.assert_grantable(held, windows_form)
    disjoint = _envelope(assignment_id="W-4",
                         write_lease_paths=("apps/web/pages",))
    sc.assert_grantable(held, disjoint)


def test_producer_cap_rejects_fourth_writer():
    held = tuple(_envelope(assignment_id=f"W-{i}",
                           write_lease_paths=(f"pkg{i}/mod.py",))
                 for i in range(sc.PRODUCER_CAP))
    fourth = _envelope(assignment_id="W-9",
                       write_lease_paths=("pkg9/mod.py",))
    with pytest.raises(sc.ContractError) as err:
        sc.assert_grantable(held, fourth)
    assert err.value.code == "producer_cap"
    # read-only agents may run without write authority at any count
    reader = _envelope(assignment_id="R-1", write_lease_paths=())
    sc.assert_grantable(held, reader)


def test_shared_mutable_resource_single_writer():
    held = (_envelope(assignment_id="W-1",
                      write_lease_paths=("pkg1/mod.py",),
                      lease_resources=("branch:control/D-024",)),)
    conflict = _envelope(assignment_id="W-2",
                         write_lease_paths=("pkg2/mod.py",),
                         lease_resources=("branch:control/D-024",))
    with pytest.raises(sc.ContractError) as err:
        sc.assert_grantable(held, conflict)
    assert err.value.code == "resource_overlap"


def test_envelope_validation_fail_closed():
    with pytest.raises(sc.ContractError) as err:
        sc.validate_envelope(_envelope(size_class="huge"))
    assert err.value.code == "bad_size_class"
    with pytest.raises(sc.ContractError) as err:
        sc.validate_envelope(_envelope(telemetry_sources=()))
    assert err.value.code == "missing_telemetry"
    with pytest.raises(sc.ContractError) as err:
        sc.validate_envelope(_envelope(telemetry_sources=("magic",)))
    assert err.value.code == "unknown_telemetry_source"
    with pytest.raises(sc.ContractError) as err:
        sc.validate_envelope(_envelope(telemetry_confidence="certain"))
    assert err.value.code == "bad_confidence"
    with pytest.raises(sc.ContractError) as err:
        sc.validate_envelope(_envelope(model_context_window=0))
    assert err.value.code == "bad_context_window"
    with pytest.raises(sc.ContractError) as err:
        sc.validate_envelope(_envelope(size_class=wc.COHESIVE_SUBAGENT,
                                       cohesion_rationale="  "))
    assert err.value.code == "missing_cohesion"


def test_contract_pair_digest_bound():
    pair = sc.build_pair(_assignment(), _envelope())
    payload = pair.to_dict()
    assert payload["assignment_digest"] == pair.assignment.digest()
    assert payload["envelope_digest"] == pair.envelope.digest()
    assert len(payload["assignment_digest"]) == 64


# ---------- private health bands (s5.5) ----------

def test_band_ordering_and_fractions_enforced():
    with pytest.raises(sc.ContractError) as err:
        sc.HealthBands(observe_occupancy=0.9, prepare_occupancy=0.7,
                       land_occupancy=0.8, emergency_occupancy=0.95)
    assert err.value.code == "band_order"
    with pytest.raises(sc.ContractError) as err:
        sc.HealthBands(observe_occupancy=0.0)
    assert err.value.code == "bad_band"
    with pytest.raises(sc.ContractError):
        sc.HealthBands(emergency_occupancy=1.0)


def test_bands_from_config_fail_closed():
    class Cfg:
        raw = {"subagent_health_bands": {"observe_occupancy": 0.4}}
    bands = sc.HealthBands.from_controller_config(Cfg())
    assert bands.observe_occupancy == 0.4

    class Bad:
        raw = {"subagent_health_bands": {"kill_at": 0.5}}
    with pytest.raises(sc.ContractError) as err:
        sc.HealthBands.from_controller_config(Bad())
    assert err.value.code == "unknown_band_key"


def test_detector_policy_validated():
    with pytest.raises(sc.ContractError):
        sc.DetectorPolicy(no_progress_window_minutes=0)
    with pytest.raises(sc.ContractError):
        sc.DetectorPolicy(repeated_attempt_limit=0)


# ---------- startup overhead measurement (s5.5, s6, s16.2) ----------

def test_startup_observation_measures_the_calibration_inputs():
    obs = so.StartupObservation(
        assignment_id="A-1", size_class=wc.COHESIVE_SUBAGENT,
        resolved_model="claude-opus-4-8", packet_tier="normal",
        packet_bytes=24_000, startup_tokens=9_000, startup_seconds=42.0,
        files_reopened=6, repeated_documents=2,
        time_to_first_evidence_seconds=180.0, outcome="completed",
        recorded_at_utc=NOW)
    record = obs.to_record()
    assert record.record_type == so.RECORD_TYPE
    assert record.measurements["startup_overhead_tokens"].value == 9_000
    assert record.measurements["startup_packet_bytes"].value == 24_000
    assert record.measurements["startup_files_reopened"].value == 6
    assert record.measurements[
        "startup_time_to_first_evidence_seconds"].value == 180.0
    assert record.attributes["packet_tier"] == "normal"
    assert record.attributes["outcome"] == "completed"


def test_unmeasured_startup_values_stay_unknown_never_zero():
    record = so.StartupObservation(
        assignment_id="A-2", size_class=wc.MAIN_SESSION,
        recorded_at_utc=NOW).to_record()
    assert record.measurements["startup_overhead_tokens"].is_unknown
    assert record.measurements["startup_overhead_seconds"].is_unknown
    assert record.measurements[
        "startup_time_to_first_evidence_seconds"].is_unknown


def test_ledger_bounded_with_counted_eviction():
    ledger = so.OverheadLedger(max_observations=2)
    for i in range(4):
        ledger.record(so.StartupObservation(
            assignment_id=f"A-{i}", size_class=wc.COHESIVE_SUBAGENT,
            startup_tokens=1_000 * (i + 1), recorded_at_utc=NOW))
    assert len(ledger) == 2
    assert ledger.evicted_observations == 2
    with pytest.raises(so.OverheadError):
        so.OverheadLedger(max_observations=0)


def test_calibration_uses_known_values_only_and_filters():
    ledger = so.OverheadLedger()
    ledger.record(so.StartupObservation(
        assignment_id="A-1", size_class=wc.COHESIVE_SUBAGENT,
        resolved_model="m1", startup_tokens=8_000, recorded_at_utc=NOW))
    ledger.record(so.StartupObservation(
        assignment_id="A-2", size_class=wc.COHESIVE_SUBAGENT,
        resolved_model="m1", startup_tokens=None, recorded_at_utc=NOW))
    ledger.record(so.StartupObservation(
        assignment_id="A-3", size_class=wc.MAIN_SESSION,
        resolved_model="m2", startup_tokens=100, recorded_at_utc=NOW))
    all_cal = ledger.calibration()
    assert all_cal.observations == 3
    cohesive = ledger.calibration(size_class=wc.COHESIVE_SUBAGENT,
                                  resolved_model="m1")
    assert cohesive.observations == 2
    assert cohesive.median_startup_tokens == 8_000  # None skipped, not zero
    assert cohesive.median_startup_seconds is None
    empty = ledger.calibration(size_class=wc.OVERSIZED_SPLIT)
    assert empty.observations == 0
    assert empty.median_startup_tokens is None


def test_observation_validation_fail_closed():
    with pytest.raises(so.OverheadError):
        so.StartupObservation(assignment_id="A-1",
                              size_class=wc.MAIN_SESSION, outcome="great")
    with pytest.raises(wc.WorkloadError):
        so.StartupObservation(assignment_id="A-1", size_class="huge")
    with pytest.raises(so.OverheadError):
        so.StartupObservation(assignment_id="A-1",
                              size_class=wc.MAIN_SESSION, startup_tokens=-1)
    with pytest.raises(so.OverheadError):
        so.StartupObservation(assignment_id="", size_class=wc.MAIN_SESSION)


# ---------- graph sizing + packet plans (s13, R080, R081) ----------

def _view() -> dict:
    return {
        "out_edges": [
            {"from": "tools/a.py", "to": "tools/b.py"},
            {"from": "tools/a.py", "to": "tools/c.py::helper"},
        ],
        "in_edges": [
            {"from": "tools/test_a.py", "to": "tools/a.py"},
            {"from": "tools/d.py", "to": "tools/a.py"},
        ],
        "in_edge_count": 2,
        "out_truncation": False,
        "in_truncation": False,
    }


def test_neighborhood_adapter_extracts_files_symbols_tests():
    hood = ws.neighborhood_from_view("tools/a.py", _view())
    assert "tools/b.py" in hood.files
    assert "tools/c.py::helper" in hood.symbols
    assert hood.tests == ("tools/test_a.py",)
    assert hood.dependency_breadth == 2
    assert not hood.truncated and not hood.stale


def test_malformed_view_fails_closed():
    with pytest.raises(ws.SizingError) as err:
        ws.neighborhood_from_view("tools/a.py", {"out_edges": []})
    assert err.value.code == "bad_view"


def test_tier_selection_reuses_the_accepted_tiers_exactly():
    hood = ws.neighborhood_from_view("tools/a.py", _view())
    signals = ws.tier_signals(hood, changed_files=2)
    plan = ws.packet_plan(assignment_id="A-1", role="producer",
                          neighborhood=hood, signals=signals)
    direct = budget.select_tier("A-1", "producer", signals)
    assert plan.tier == direct.tier
    assert plan.target_tokens == direct.target_tokens
    assert plan.withheld_larger_target == direct.withheld_larger_target


def test_medium_without_justification_stays_withheld():
    hood = ws.GraphNeighborhood(seed_path="tools/a.py",
                                files=("tools/a.py",),
                                dependency_breadth=20)
    signals = ws.tier_signals(hood)
    plan = ws.packet_plan(assignment_id="A-1", role="producer",
                          neighborhood=hood, signals=signals)
    # frozen adaptive-tier behavior: the tier NAME reflects the proposal but
    # the larger TARGET is withheld without a justification (D-013-R041)
    assert plan.tier == budget.MEDIUM
    assert plan.withheld_larger_target is True
    assert plan.target_tokens == budget.TIER_TARGET_TOKENS[budget.NORMAL]


def test_packet_plan_marks_omissions_or_stops():
    hood = ws.neighborhood_from_view("tools/a.py", _view())
    signals = ws.tier_signals(hood)
    plan = ws.packet_plan(
        assignment_id="A-1", role="reviewer", neighborhood=hood,
        signals=signals,
        omissions=(("known_decisions_and_risks",
                    "review packet is reconstructed from durable evidence; "
                    "producer decisions arrive as claims to verify"),))
    assert "known_decisions_and_risks" not in plan.included
    assert plan.sufficient
    with pytest.raises(ws.SizingError) as err:
        ws.packet_plan(assignment_id="A-1", role="reviewer",
                       neighborhood=hood, signals=signals,
                       omissions=(("known_decisions_and_risks", "  "),))
    assert err.value.code == "unjustified_omission"
    with pytest.raises(ws.SizingError) as err:
        ws.packet_plan(assignment_id="A-1", role="reviewer",
                       neighborhood=hood, signals=signals,
                       omissions=(("everything", "why"),))
    assert err.value.code == "unknown_category"


def test_unprovable_sufficiency_stops_instead_of_dropping_constraints():
    empty = ws.GraphNeighborhood(seed_path="tools/a.py")
    plan = ws.packet_plan(assignment_id="A-1", role="producer",
                          neighborhood=empty, signals=ws.tier_signals(empty))
    assert not plan.sufficient
    assert "stop" in plan.stop_reason
    truncated = ws.GraphNeighborhood(seed_path="tools/a.py",
                                     files=("tools/a.py",), truncated=True)
    plan2 = ws.packet_plan(assignment_id="A-1", role="producer",
                           neighborhood=truncated,
                           signals=ws.tier_signals(truncated))
    assert not plan2.sufficient
    assert "truncated" in plan2.stop_reason


# ---------- carried advisory G3-M1: eviction ORDER isolation ----------

def test_sdk_tracker_evicts_newer_completed_before_older_active():
    """G3-M1 (M0-T099 carried advisory): the existing bounded-eviction test
    completes the OLDEST task, so a pure-oldest-first mutant still passes it.
    Here the completed task is NEWER than an active one: completed-first must
    evict the newer completed entry and keep the older ACTIVE one — an
    oldest-first mutant fails this case."""
    tracker = ts.SdkTaskTracker(max_tasks=2)
    tracker.ingest_event({"type": "task_progress", "task_id": "older-active",
                          "total_tokens": 100}, now_utc_iso=NOW)
    tracker.ingest_event({"type": "task_progress", "task_id": "newer-done",
                          "total_tokens": 200}, now_utc_iso=NOW)
    tracker.ingest_event({"type": "task_completed", "task_id": "newer-done"},
                         now_utc_iso=NOW)
    tracker.ingest_event({"type": "task_progress", "task_id": "incoming",
                          "total_tokens": 300}, now_utc_iso=NOW)
    assert tracker.high_water("newer-done") == {}
    assert tracker.high_water("older-active")[
        "sdk_task_total_tokens"] == 100
    assert tracker.high_water("incoming")["sdk_task_total_tokens"] == 300
    assert tracker.evicted_tasks == 1


def test_subagent_registry_evicts_newer_closed_before_older_active():
    """G3-M1 parallel case for SubagentRegistry (same shape gap): closing an
    entry reinserts it at the END of insertion order, so a newer-closed entry
    must still evict before an older ACTIVE identity."""
    reg = th.SubagentRegistry(max_entries=2)
    reg.observe(th.ingest_hook_event(
        "TaskCreated", {"task_id": "older-active"}, now_utc_iso=NOW))
    reg.observe(th.ingest_hook_event(
        "TaskCreated", {"task_id": "newer-closed"}, now_utc_iso=NOW))
    reg.observe(th.ingest_hook_event(
        "TaskCompleted", {"task_id": "newer-closed"}, now_utc_iso=NOW))
    reg.observe(th.ingest_hook_event(
        "TaskCreated", {"task_id": "incoming"}, now_utc_iso=NOW))
    assert reg.get("newer-closed") is None
    assert reg.get("older-active") is not None
    assert reg.get("older-active")["state"] == "active"
    assert reg.get("incoming") is not None
