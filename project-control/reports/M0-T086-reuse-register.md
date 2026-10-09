# M0-T086 — D-024 reuse register (component map → phases)

Producer: orchestrator. Date: 2026-08-25. Source of truth: `tools/agent_supervisor/` at this
commit (58 modules), README ("Phases 1, 2, 3 and 4 exist today"), D-023 ledger state.
Verdicts: **REUSE** (use as-is), **EXTEND** (satisfies part; D-024 adds to it), **GAP** (build new).

## Codex transport (D-024 §2) — REUSE, verify against 0.146.0
`codex_reviewer.py`, `broker.py`, `protocol.py`, `preflight.py`, `probe_control_plane.py`,
`probe_result.py`, `review_packet.py`, `review_cadence.py`, `ephemeral_review.py`.
The accepted D-007 bridge already models read-only review, structured decisions, and preflight.
Live probe (capability_matrix_v1.json): codex 0.146.0 supports `exec`, `--sandbox`, `--json`,
`--output-schema`, `resume` — the full §2 transport surface. D-024 adds: version-probed invocation
contract binding these exact flags, identity-bound threads, fail-closed decision schema (16.3).

## Controller / states / succession (Phase D) — EXTEND (largest reuse block)
`state_machine.py`, `durable_state.py`, `locking.py` (one supervisor per checkout),
`loop.py`, `loop_turnover.py`, `turnover_controller.py`, `turnover_adapters.py`,
`turnover_seam.py`, `turnover_wiring.py`, `worker_turnover.py`, `rotation.py`,
`session_continuity.py`, `recovery.py`, `recovery_probes.py`, `resume_scheduler.py`,
`start_gate.py`, `external_effects.py`, `circuit_breakers.py`, `loop_breakers.py`,
`process.py` (Windows Job-Object containment), `model_change_ipc.py`, `anchor.py`.
D-023 M0-T080 (session/model turnover) is in round-3 review on its own branch — its identity is
NOT part of this baseline; reconcile before Phase D work begins. D-024 adds: §3 state-name
coverage, renewable epoch leases, §7 seam validation, exact-once successor race tests, bounded
idle, Codex-outage backoff/blocked states.
**Host-restart auto-resume already exists**: `cli.py autostart-plan / install-autostart /
uninstall-autostart` + `orchestrator-watchdog` (M0-T054/M0-T056 R595 work) — Phase D reuses this
instead of building a new startup mechanism.

## Telemetry (Phase B) — EXTEND core, GAP ingestion
`resource_sampling.py` (process-level sampling exists), `redaction.py`, `audit_log.py`,
`retention.py`, `evidence.py`. GAPS: typed source/confidence-labelled usage records, atomic
sidecar, primary status-line ingestion, `subagentStatusLine` ingestion (docs-confirmed fields in
capability_matrix_v1.json), hook-event ingestion, transcript-derived fallback, occupancy-vs-
cumulative separation.

## Workload sizing / bounded contracts (Phase C) — EXTEND models, GAP classifier
`models.py` (task/packet models), `run_budget.py` (owner-controlled budgets from M0-T079),
`policy.py`, `approved_models.py`. GAPS: worker-assignment vs controller-envelope schema split,
structural size classifier, startup-overhead measurement, private health bands, no-progress
detectors, extension gate. Concurrency cap and write leases partially exist in policy/locking.

## Guardrail bridge (Phase E) — EXTEND
`refusals.py` (typed refusals from M0-T079), quota classifier (`test_agent_supervisor_quota_
classifier.py`, D-007 am.12 detect-and-hold), `model_turnover.py`, `approved_models.py`.
D-024 adds: exact guardrail-refusal recognition distinct from quota, allowlisted continuation
actuation, mechanical 4.8-bridge restrictions, durable two-attempt counter, semantic-preservation
tests. The quota detect-and-hold policy is NOT superseded (§8; manifest audit_log).

## Operator channel (Phase F) — EXTEND CLI, GAP /loop-* + ask
`cli.py` already ships: `start` (mode-gated), `status`, `pause`, `resume`, `stop`,
`emergency-stop`, `export-handoff`, `pending-approvals`, `doctor`, `replay`, watchdog.
GAPS: no-duration canonical start alias ("Start the agent loop"), `ask` operation,
feature-detected `/loop-*` pre-model interception (docs confirm `UserPromptExpansion` exists on
2.1.220 with command-name matchers; `UserPromptSubmit` blocks + erases — capability_matrix_v1),
zero-context proof, notification-sink interface (`notifications.py` exists as a seed).

## Repair gate / GitHub (Phase G) — EXTEND
`github_flow.py`, `push_policy.py`, `external_effects.py` (intent journal), `evidence.py`.
GAPS: root-cause/replace-not-layer review evidence schema, compatibility-exception tracker.

## Cross-cutting REUSE
`config.py` + immutable-config manifest binding (M0-T072), `manifest.py`, `os_acl.py`,
`errors.py`, `redaction.py`, `owner_touch.py`, `remote_approvals.py` (D-023 M0-T084 boundary),
`replay.py` (historical-corpus harness — pattern for D-024 fixtures), `.claude/hooks/*` guards,
graph/context system under `tools/code_graph` + `tools/context_*` (Phase C sizing input; §10
regression duty), `tools/project_control.py` ledger (campaign/task authority — not duplicated).

## New in this task
`capability_probe.py` + `fixtures/capability_probe_live_2026-08-25.json` +
`fixtures/capability_matrix_v1.json` + `test_agent_supervisor_capability_probe.py` (16 tests) —
no control-behavior change; fixtures only.
