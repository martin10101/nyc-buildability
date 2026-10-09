# M0-T089 — D-024 B2: subagent telemetry breadth + read-only shadow status

Producer: orchestrator. Date: 2026-08-25. Directive: D-024 (Phase B items 3–9 of §15-B;
requirements R039–R045/R100/R107 core; full applicable set = 34 ids, identical to M0-T088;
evidence map `M0-T089-evidence-map.json`). Supervisor-freeze qualifying evidence: **D-024-R100**
— cited in the packet objective, this report, and every commit message.

## What was built

Five new focused modules (stdlib-only, 3.11-compatible, no dependency change) extending the
accepted B1 core, plus the full carried M0-T088 gate-round bundle:

1. **`telemetry_subagent.py`** (§5.1 item 2 / 15-B item 3) — `subagentStatusLine` refresh-tick
   ingestion per the documented payload (one JSON object per tick, `tasks[]` rows). One typed
   record per visible task row. Feature-detection duties implemented exactly: `model`/
   `contextWindowSize` OMITTED until model resolution (>=2.1.205) → absence is normal;
   missing `tokenCount` → `unknown` never zero; `tokenCount` records as **occupancy** under
   `subagent-status-live` (the docs pair it with `contextWindowSize` — the task's live context
   view); **`tokenSamples` preserved raw as a TREND-ONLY attribute and never interpreted into a
   measurement** (no invented semantics). `sidecar_snapshot()` builds the compact bounded
   snapshot for the atomic `TelemetrySidecar` (fast refresh path, <4KiB in tests).
2. **`telemetry_hooks.py`** (§5.1 item 5 / 15-B item 5) — lifecycle-hook ingestion over the
   documented 31-event set (2.1.220, official docs in the capability matrix): typed
   `lifecycle_hook` records carrying identity facts only (no usage numbers invented); unknown
   event names recorded honestly (`known: false`, never crash/guess). `SubagentRegistry`:
   bounded identity tracker (start/create open, stop/complete close; closed entries evicted
   first past the bound).
3. **`telemetry_sdk.py`** (§5.1 item 1 / 15-B item 4) — Agent SDK task-event ingestion,
   feature-detected and NEVER installed (R040): `sdk_available()` probes with
   `importlib.util.find_spec` only (no import, no side effect; SDK remains absent-by-policy);
   the parsers are pure functions over event dicts so fixtures exercise them while the SDK stays
   absent. `SdkTaskTracker`: per-task cumulative high-water from `task_progress`
   (`sdk-task-cumulative` label; duplicate totals dedupe; regressions counted and never lower
   the high-water); completion/failure/stopped notifications tolerated out-of-order; **a final
   result's usage records as `final_request_*` with an explicit "FINAL API request only" caveat
   while the cumulative claim stays with the progress high-water (R043 proof)**.
4. **`telemetry_transcript.py`** (§5.1 item 6 / 15-B item 7) — version-probed read-only
   transcript derivation, the feature-detected FALLBACK. Parses shapes **measured live on the
   installed Claude Code 2.1.220** (2026-08-25): assistant lines (`message.id` + `usage{input,
   output, cache_creation_input, cache_read_input}`) and `system/compact_boundary` lines
   (`compactMetadata{preTokens, postTokens, cumulativeDroppedTokens, trigger}`). Dedup via the
   B1 `UsageAccumulator` (label parameterized to `transcript-derived`); torn/fragmented lines
   skipped+counted; unknown line types counted, never guessed; multiple compactions tracked
   (count + preTokens sum); resumption detected via multiple `sessionId`s; empty input →
   unknown, never zero; sums documented as a conservative lower bound.
5. **`telemetry_status.py`** (15-B items 8–9) — read-only shadow status with **actuation OFF**:
   `read_only_status()` assembles sidecars + journal tail from stored artifacts (missing
   artifacts → null, proven to create/remove no files); `python -m
   tools.agent_supervisor.telemetry_status` prints it (no supervisor control-flow module
   touched — `cli.py` unchanged). `compare_with_manual()` is the **opt-in test/canary
   diagnostic** comparing pipeline records against a manually collected payload — never
   scheduled, never a prompt; disagreement is reported, not raised.

### Carried M0-T088 gate-round bundle (all five items closed)

- **G5-S2** — `capability_matrix_v1.json` binary notes `[HOME]`-masked (the last committed
  fixture carrying the operator's home prefix), and a **cross-fixture assertion** now scans ALL
  committed `agent_supervisor/fixtures/*.json` for home-prefix leaks — the exposure class is
  closed, not one file.
- **G4-Adv2** — prompt-like keys holding LIST/DICT values are now withheld wholesale as one
  digest reference (`withhold_prompt_value`), red/green tested — landed BEFORE transcript/message
  ingestion as the reviewer required.
- **G4-Adv1** — a usage field never present in ANY ingested step now reports `unknown` in
  `snapshot()` (observed-field tracking), not a fabricated 0; red/green tested.
- **G3-minor** — per-step records now use the `step_*` measurement family
  (`provider_usage_step` never borrows `cumulative_*`); registry names added; B1 tests updated.
- **G3 nit** — `_derive_live_status` mixed-set handling made deterministic (sorted, no `pop()`).

## What was deliberately NOT built (scope honesty)

Live wiring of the status-line/subagentStatusLine commands into Claude Code settings and live
hook installation are operator/Phase F surface — these modules are the measurement layer with
contracts proven by docs-derived and live-measured fixtures. No live interactive harness fixture
for subagentStatusLine payloads yet (matrix `hooks.live_behavior_fixtures` stays `unknown`;
Phase B/F deliverable). SDK ingestion runs fixture-only while the SDK is absent-by-policy —
nothing installs it (R040). Actuation, health bands, and any consumer of these records remain
OFF (Phase C+). `tokenSamples` semantics deliberately uninterpreted pending live fixtures.

## Acceptance scenarios (all reproduced by `tools/test_agent_supervisor_subagent_telemetry.py`)

- AS-1 subagentStatusLine: multi-task payload (3 simultaneous tasks, full documented fields);
  unresolved-model rows; absent counts → unknown; tokenSamples trend-only; malformed
  payload/rows/bool counts → unknown; empty tick honest; compact atomic sidecar snapshot.
- AS-2 SDK (fixture-driven, SDK absent): availability probe has no side effects; progress
  high-water; duplicate progress no-double-count; regression never fresh; **final totalTokens
  never assumed cumulative**; out-of-order completion; malformed/unknown events → unknown.
- AS-3 hooks: 31-event documented set; known/unknown events; identity-only records; registry
  lifecycle open/close; bounded eviction (closed first); non-hook records ignored.
- AS-4 transcript: live-measured shapes; sums + labels; message-id dedup; fragmentation
  tolerated; compact-boundary preTokens; multiple compactions + resumption (sums grow across
  session ids — reset-immune); empty → unknown; malformed compactMetadata → unknown.
- AS-5 shadow status: assembles without writing (file-set equality proven); missing artifacts →
  null not zero; `main()` read-only; manual comparison opt-in with reported (not raised)
  disagreement.
- AS-6 structural: AST no-injection scan over all five B2 modules (additionalContext/
  hookSpecificOutput absent from every non-docstring string).
- AS-7 carried bundle: all five items red/green or assertion-tested as listed above.

## Self-check evidence (producer runs, this checkout, Python 3.11.9)

- `python -m pytest tools/test_agent_supervisor_subagent_telemetry.py
  tools/test_agent_supervisor_telemetry_core.py tools/test_agent_supervisor_capability_probe.py -q`
  → **102 passed** (37 new B2 + 49 B1 updated + 16 probe).
- Full suite `python -m pytest tools/test_agent_supervisor_*.py -q` → **2006 passed, 2 skipped,
  0 failed** (M0-T088 baseline 1969/2/0 + 37 new; freeze §4 duty re-established).
- `ruff check` (0.13.0, CI-matched) on all eight touched telemetry modules + both test files →
  clean. `python tools/modularity_check.py --check` → failures 0 (no new module near thresholds).
- Transcript shapes: live-probed on this workstation's real 2.1.220 transcripts (keys only)
  before implementation — assistant `message.id`/`usage` fields and `compact_boundary`
  `compactMetadata` key set match the parser exactly.

## Files changed

- New: `tools/agent_supervisor/telemetry_subagent.py`, `telemetry_hooks.py`, `telemetry_sdk.py`,
  `telemetry_transcript.py`, `telemetry_status.py`; `tools/test_agent_supervisor_subagent_telemetry.py`.
- Modified (carried bundle): `tools/agent_supervisor/telemetry_records.py` (registry names),
  `telemetry_ingest.py` (step_* names, observed-field unknown, step_label),
  `telemetry_redaction.py` (withhold_prompt_value), `fixtures/capability_matrix_v1.json`
  (binary notes masked), `tools/test_agent_supervisor_telemetry_core.py` (step_* assertions,
  deterministic helper).
- Reports: `project-control/reports/M0-T089-{G0-readiness,subagent-telemetry,evidence-map}.*`.
