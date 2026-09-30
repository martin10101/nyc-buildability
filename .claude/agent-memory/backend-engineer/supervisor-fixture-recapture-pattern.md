---
name: supervisor-fixture-recapture-pattern
description: How to recapture the D-024 supervisor fixture pack + drift teeth at a newly installed Claude Code version (M0-T092/M0-T118 precedent)
metadata:
  type: project
---

Bounded fixture recapture at a new installed Claude Code CLI version (D-024 admission-event
discipline; M0-T092 = 2.1.247->2.1.248, M0-T118 = 2.1.248->2.1.251).

**Why:** each deliberate CLI upgrade needs the measured fixture pack + three live drift teeth
re-pointed so they go GREEN at the new version and stay removal-sensitive (RED on the next drift).

**How to apply (the moving parts, verified in source):**
- Five fixtures, filename carries version+task: `hook_event_catalog_<ver>.json`,
  `loop_interception_detection_<ver>.json`, `guardrail_refusal_shapes_<ver>.json`,
  `capability_probe_live_<date>_<task>_<ver>.json`, `native_runtime_detection_<date>_<task>.json`.
  Old fixtures stay committed (append-only history).
- Two module pointers: `event_drift.py::CATALOG_FIXTURE_PATH` and
  `guardrail_refusal.py::SHAPES_FIXTURE_PATH`.
- Generate the two LIVE fixtures by running: `python -m tools.agent_supervisor.capability_probe --out <path>`
  and `native_runtime.build_detection_fixture(detect_native_capabilities(), task=...)` (dump indent=1,
  sort_keys, newline=LF). Both self-mask `[HOME]`.
- Three drift teeth (each exact-matches installed `claude --version` against its fixture's recorded
  version): `test_s8_live_version_matches_catalog_fixture` (event_bus), `test_live_reprobe_claude_version_matches_fixture`
  (capability_probe), `test_live_detection_matches_committed_fixture` (native_adapter). Capture them RED
  BEFORE re-point, GREEN after. Never weaken the `==`.
- Four consumer test modules to update pointers/version-asserts: event_bus, capability_probe,
  native_adapter, operator_channel. golden_run/guardrail_bridge consume guardrail_refusal.py but do NOT
  assert its version string or filename (safe to re-point).
- The `.claude/hooks/loop_command_interceptor.py` hook auto-selects the NEWEST
  `loop_interception_detection_*.json` via `sorted(...).glob(...)` reversed — so adding a new versioned
  interception fixture needs NO hook edit (and `.claude/**` is out of scope anyway).
- `KNOWN_HOOK_EVENTS` (telemetry_hooks.py) is the frozen 2.1.220 baseline (31 events). A real event-set
  drift (e.g. 2.1.251 added PreModelSwitch + PostModelSwitch => 33) is recorded as a reconciled FACT in
  the catalog fixture's `drift_vs_2_1_220` (added sorted, removed) that `catalog_drift()` must match — do
  NOT widen KNOWN_HOOK_EVENTS in a fixture-recapture task. `catalog_drift` sorts added/removed.
- Honesty invariants that must survive recapture: guardrail shape stays `verified_live=false`/UNCAPTURED;
  interception payload is INHERITED (state a lineage note) not re-measured; zero_context_proof +
  queued_input_behavior stay `pending-owner-C1`; loop_interception must keep tokens "measured-live"
  (UserPromptSubmit.payload), "UNPROVEN" (UserPromptExpansion.response_contract), "second-terminal",
  "NOT advertised as real-time". Full suite baseline ~2726 collected, 0 failures.
