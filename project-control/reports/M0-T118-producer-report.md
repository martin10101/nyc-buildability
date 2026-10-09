# M0-T118 producer report — bounded fixture recapture at Claude Code 2.1.251

Task: M0-T118 (D-024 Amendment 13 unit R, R281; M0-T092 precedent). Type: governance
(supervisor defect-only lane). Qualifying evidence: D-024-R281 (AD-093 provider CLI drift).
Worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t118` (verified via `rev-parse --show-toplevel`).

2.1.251 is NOT recorded as the admitted version by this task — admission lands with M0-T119 after
the full R282 pass list. This unit only recaptures the measured fixture pack and re-points the drift
teeth so they are GREEN at 2.1.251 and remain removal-sensitive.

## What changed

New fixtures (append-only; the 2_1_247/2_1_248 pack stays committed untouched):

- `tools/agent_supervisor/fixtures/hook_event_catalog_2_1_251.json`
- `tools/agent_supervisor/fixtures/loop_interception_detection_2_1_251.json`
- `tools/agent_supervisor/fixtures/guardrail_refusal_shapes_2_1_251.json`
- `tools/agent_supervisor/fixtures/capability_probe_live_2026-08-29_m0t118_2_1_251.json` (measured live)
- `tools/agent_supervisor/fixtures/native_runtime_detection_2026-08-29_m0t118.json` (measured live)

Re-pointed consumers:

- `tools/agent_supervisor/event_drift.py` — `CATALOG_FIXTURE_PATH` -> `hook_event_catalog_2_1_251.json`
- `tools/agent_supervisor/guardrail_refusal.py` — `SHAPES_FIXTURE_PATH` -> `guardrail_refusal_shapes_2_1_251.json`

Fixture-consuming tests updated (only as needed; no tooth weakened):

- `tools/test_agent_supervisor_event_bus.py` — `CATALOG_FIXTURE` pointer; `test_s8_catalog_fixture_valid_and_masked` (task M0-T118, version 2.1.251, events==33); `test_s8_recorded_drift_matches_computed_drift` rewritten for the non-identical +2 delta.
- `tools/test_agent_supervisor_capability_probe.py` — `CURRENT_FIXTURE` pointer; `test_current_fixture_records_2_1_251_masked_and_shaped` (renamed; 2.1.251 + m0t118).
- `tools/test_agent_supervisor_native_adapter.py` — `DETECTION_FIXTURE` pointer; `test_committed_detection_fixture_shape` (task M0-T118, version 2.1.251).
- `tools/test_agent_supervisor_operator_channel.py` — `DETECTION_FIXTURE` pointer; `test_the_installed_version_fixture_selects_the_measured_path` (2.1.251).

NOT touched (correctly): `.claude/**` (the `loop_command_interceptor.py` hook auto-selects the
newest `loop_interception_detection_*.json` via its existing glob and still resolves to
UserPromptSubmit, so no hook edit is needed); `telemetry_hooks.py`/`KNOWN_HOOK_EVENTS` (out of
scope — the +2 drift is recorded as a reconciled FACT the deterministic test bites on, not silently
widened); process.py/claude_runner.py/preflight.py/turnover_adapters.py/cli.py; runtime journal;
protected config. No new dependencies.

## The +2 event-set delta (named)

The 2.1.251 documented hook-event set has **33 events**; the 2.1.248 catalog had **31**. Diffed
name-for-name, the two ADDED events are:

- **PreModelSwitch**
- **PostModelSwitch**

No events were removed. This is a genuine drift, unlike the identical 2.1.247->2.1.248 set that
M0-T092 re-pointed. The reconciliation is recorded in `hook_event_catalog_2_1_251.json` under
`drift_vs_2_1_220` as `added=["PostModelSwitch","PreModelSwitch"]` (sorted, matching
`catalog_drift()`), `removed=[]`, with a note naming the additions. The deterministic test
`test_s8_recorded_drift_matches_computed_drift` now asserts `catalog_drift(events, KNOWN_HOOK_EVENTS)`
equals this recorded reconciliation and that `drift.describe() == "added: PostModelSwitch, PreModelSwitch"`.

## Acceptance-scenario mapping

- **AS-1** (catalog re-captured; deterministic drift matches `catalog_drift()`; S8 live tooth GREEN
  at 2.1.251, RED at any other version): met. `test_agent_supervisor_event_bus.py` passes; the +2
  reconciliation is deterministic; live tooth GREEN (was RED at 2.1.248).
- **AS-2** (capability probe re-run live at 2.1.251; recorded as a new fixture; no FAILED probe rows
  for depended-on capabilities): met. Probe run live -> claude `2.1.251 (Claude Code)`, codex
  `codex-cli 0.146.0`, all probed flags/verbs supported. `test_agent_supervisor_capability_probe.py`
  passes.
- **AS-3** (interception + guardrail-shape fixtures re-pointed/re-measured with honest confidence;
  unproven surfaces stay unproven): met. Interception payload inherited with a stated lineage note +
  event-set re-verification; guardrail shape stays `verified_live=false`/UNCAPTURED.
  `test_agent_supervisor_operator_channel.py` + `test_agent_supervisor_native_adapter.py` pass.
- **AS-4** (recapture after M0-T117 control; `claude --version` identical before/after): met — both
  stamps `2.1.251 (Claude Code)` (19:49:31Z / 20:07:08Z). See M0-T118-recapture-evidence.md.

## Counts

- Four fixture-consuming modules: **169 passed, 0 failed** (71.22s).
- Full supervisor suite: **2724 passed, 2 skipped, 0 failed** (560.01s), exit 0. 2726 collected =
  baseline; no new test functions added; the 2 skips are pre-existing conditional skips.
- Three drift teeth: RED (3 failed) at 2.1.248 pointers -> GREEN (3 passed) after re-point. Verbatim
  in M0-T118-recapture-evidence.md.

## Honest limitations

- The hook-event catalog is **official-docs confidence** (the delivered docs gave the 33 event
  NAMES only). Per-event field-level payloads for PreModelSwitch/PostModelSwitch were NOT delivered
  and are NOT invented; per-event measured-live capture remains the owner-gated C1 canary.
- The interception fixture's UserPromptSubmit payload is **inherited** from the 2.1.248 fixture, not
  re-measured live at 2.1.251 (bounded-probe constraint); only event-set membership was re-verified.
  zero_context_proof and queued_input_behavior stay honestly `pending-owner-C1`.
- No live Fable guardrail refusal exists at 2.1.251 (or any version): the recognized shape stays
  `verified_live=false`, UNCAPTURED, non-actuating (also gated by absent R595).
