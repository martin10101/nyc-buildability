# M0-T090 — D-024 C1: bounded subagent contracts + structural workload sizing

**Producer:** orchestrator · 2026-08-26 UTC · branch `control/D-024-fable-codex-loop`
**Authority:** campaign `D-024-fable-codex-loop` seq 4 NEXT (owner directive D-024 v4; continuation
explicitly ordered by D-027-R011). Supervisor-freeze qualifying evidence: **D-024-R101** (Phase C),
cited in the packet, every new module docstring, and the content commit message.

## 1. What was built (five focused modules + one test pack)

All inside `tools/agent_supervisor/` (package stays a leaf — see §4), each with its own typed
error class, frozen digest-able records, closed vocabularies, and the D-024 docstring convention:

| Module | SLOC | Responsibility (D-024 anchor) |
|---|---|---|
| `workload_classifier.py` | 238 | the four owner-defined structural classes (`main-session` / `cohesive-subagent` / `oversized-split-at-seams` / `unknown-recon-first`), objective `WorkloadFeatures`, deterministic rule precedence, split-seam carry, configurable `[subagent_workload]` thresholds (s5.5; Phase C item 2) |
| `subagent_contracts.py` | 587 | the TWO LINKED pre-spawn records: `WorkerAssignment` (every s6 worker-facing field incl. honest-blocker, extension-protocol, unrelated-discovery, and handoff duties with default texts) + `SupervisionEnvelope` (size class, cohesion rationale, graph neighborhood, write lease, startup overhead, resolved model/window, telemetry sources+confidence, PRIVATE `HealthBands`, `DetectorPolicy`, landing opportunities, extension criteria); `render_worker_prompt`; the fail-closed **no-quota guard** (R045) over every worker-facing string; the **envelope-leak guard** (band names and every controller numeric never in worker text); `assert_grantable` (producer cap 3, overlapping write scopes and shared mutable resources refused — nested children pass through the same check); pair digests (Phase C item 1; parts of item 4 at the contract level) |
| `startup_overhead.py` | 218 | `StartupObservation` (packet size/tier, startup tokens/seconds, files reopened, repeated documents, time-to-first-evidence, closed outcome vocabulary; unknown = `None`, never zero), bounded `OverheadLedger` with counted eviction, median `OverheadCalibration` over KNOWN values only, `to_record()` into the accepted Phase B telemetry pipeline (reuse, not rebuild) (s5.5, s6; Phase C item 3) |
| `spawn_decision.py` | 239 | the Goldilocks decision (`stay-main`/`spawn-new`/`resume-existing`/`fork-parent`/`split-first`/`recon-first`): resume only a HEALTHY same-assignment subagent, never an overloaded one; fork only clean+beneficial parents; `model_fit` (window+demonstrated-capability routing, conservative on unknowns) (s5.5, s6; Phase C item 3) |
| `workload_sizing.py` | 260 | `GraphNeighborhood` by-value adapter over the `repo_views.neighborhood_edges` dict shape (stale ⇒ refused/conservative, R080), `tier_signals` → **reuses** `tools.context_pack_budget.select_tier` (tiers/targets/withholding preserved exactly, R081), `packet_plan` recording the smallest-complete s13 packet with justified omissions and STOP-on-unprovable-sufficiency (Phase C item 5) |

Test pack `tools/test_agent_supervisor_bounded_contracts.py` (686 lines, **53 tests**, pytest
style, deterministic, no network).

**Not in this unit (deliberate, per the campaign's Phase C split):** runtime enforcement loops
(live band evaluation against telemetry, no-progress/extension runtime, landing direction,
emergency task-stop, durable child handoffs — Phase C items 4-runtime and 6) belong to the next
campaign units; this unit delivers the schemas, classifier, measurement, sizing, and
contract-level guards they will consume. Nothing spawns, resumes, stops, or messages an agent;
the supervisor stays SHADOW-ONLY (R595 untouched).

## 2. s16.2 coverage map (the packet's "sizing cases incl. no-quota proof")

- vague/oversized rejected or split → `test_vague_assignment_rejected`, `test_empty_exact_change_rejected`, `test_oversized_cross_boundary_splits_at_seams`
- tiny targeted work stays main → `test_tiny_targeted_work_stays_in_main_session`, `test_frequent_parent_decisions_stay_main`
- follow-up resumes healthy resumable subagent → `test_followup_resumes_healthy_subagent`
- overloaded/confused not resumed → `test_overloaded_subagent_never_resumed_to_save_startup`
- fork only beneficial+clean; bloated parent not forked → `test_fork_only_when_clean_and_beneficial`
- one cohesive unit, not fragments → `test_cohesive_unit_is_one_subagent_not_fragments`; conservatism → `test_cohesion_unproven_is_never_optimistic`
- oversized split at graph/ownership/test seams → seam carry in `test_oversized_cross_boundary_splits_at_seams`
- unknown → recon first → `test_unknown_work_gets_recon_first`; stale graph reported never used (R080) → `test_stale_graph_is_reported_never_used`
- startup packet size / repeated loading / files reopened / time-to-first-evidence measured → `test_startup_observation_measures_the_calibration_inputs`, `test_unmeasured_startup_values_stay_unknown_never_zero`, `test_ledger_bounded_with_counted_eviction`, `test_calibration_uses_known_values_only_and_filters`
- lower-tier model only when window+capability fit → `test_lower_tier_model_needs_window_and_demonstrated_capability`
- more than three producers rejected → `test_producer_cap_rejects_fourth_writer` (read-only agents pass at any count)
- overlapping write scopes cannot both lease → `test_overlapping_write_scopes_cannot_both_obtain_leases` (incl. the Windows path form), `test_shared_mutable_resource_single_writer`
- **no-quota-in-worker-prompt proof (R045)** → `test_worker_prompt_contains_no_quota_language` (INDEPENDENT scan, not the guard's own table), `test_quota_language_rejected_fail_closed` (8 parametrized phrasings), `test_quota_guard_covers_every_worker_field`, `test_envelope_numbers_never_leak_into_worker_text`, `test_rendered_prompt_carries_required_duties`

Plus: health-band ordering/config fail-closed, detector validation, pair-linkage/digest tests,
tier-parity tests against the frozen adaptive-tier behavior (`medium`-without-justification stays
target-withheld), packet-plan omission/sufficiency tests.

## 3. Carried M0-T099 advisory bundle — disposition

| Advisory | Disposition |
|---|---|
| **G3-M1** (eviction-order isolation) | **DISCHARGED HERE** — `test_sdk_tracker_evicts_newer_completed_before_older_active` and `test_subagent_registry_evicts_newer_closed_before_older_active` (newer-completed vs older-active; each kills a pure-oldest-first mutant). HOSTED in this task's test file because the sibling telemetry pack is outside this packet's allowed paths; test-only, no production edit (the accepted implementations already behave correctly). |
| **G5-NIT-1** (dash mask into the cross-fixture class scan) | **CARRIED FORWARD** — the cross-fixture scan test lives outside this packet's allowed paths; no fixture was added or touched by this task. Next task touching the fixture-scan pack applies it. |
| **G5-NIT-2** (dash-username first-segment limitation) | Already documented in the accepted M0-T099 material; nothing here touches the mask. No action. |
| **G5-MIN-1** (neutralize usage numbers/UUIDs in future public fixtures) | Standing guidance for the Phase B/F live-canary task; this task adds no captured fixture. No action. |

## 4. Integration decisions a reviewer should check deliberately

- **Leaf package preserved:** no supervisor module imports the graph/index machinery; graph
  evidence arrives by value (`neighborhood_from_view` adapts the `repo_views` dict shape). The
  ONE cross-package import — `tools.context_pack_budget` (pure stdlib constants/dataclasses) — is
  LAZY inside `workload_sizing._budget()` with a typed fail-closed error, so the package stays
  importable standalone and the accepted tier table is genuinely reused, never copied (R081).
- **Distinct axis, shared discipline:** the four structural classes deliberately do NOT overload
  `rotation.py`'s SMALL/MEDIUM/LARGE session vocabulary; they mirror its patterns (objective
  features, conservative UNKNOWN, closed sets, config fail-closed via `config.raw` tables
  `[subagent_workload]` / `[subagent_health_bands]`).
- **False friend:** `resume_scheduler.py` is D-007 usage-limit wake scheduling, NOT
  resume-vs-new spawn logic; nothing was added there (it is near its SLOC ceiling). The
  resume-vs-new decision lives in `spawn_decision.py`.
- **Producer cap source:** the cap (3) implements the prose rule in
  `.claude/ORCHESTRATION_POLICY.md` §B (a forbidden path for this task — referenced, not edited).
- **No-quota guard breadth:** the R045 guard deliberately rejects ANY numeric-token phrasing in
  worker-facing fields (e.g. "about 3.5k tokens should suffice"), trading false positives for
  fail-closed certainty; callers rewrite wording.

## 5. Self-checks (G2 doc completes the suite figures)

- New pack: **53 passed / 0 failed**. Adjacent supervisor packs (statusline handler, telemetry
  core, subagent telemetry, rotation, scheduler): **290 passed / 0 failed**.
- `ruff check` over all six files: clean. `python tools/modularity_check.py --check`: exit 0
  (largest new module 587 SLOC, under the 600 warn line).
- Full `tools/` suite at the frozen tree: figures recorded in `M0-T090-G2-self-check.md`
  (supervisor-freeze baseline duty). Discovery during the first chunk run: 5 pre-existing-at-HEAD
  failures in `tools/test_mcp_policy.py` caused by the accepted M0-T100 settings key — repaired
  under the separate bounded task **M0-T101** (fail-closed `statusLine` shape; see its report);
  not part of this task's diff.
- No dependency added; no forbidden path touched; PR #241 untouched; no actuation surface.
