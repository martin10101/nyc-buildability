---
name: supervisor-gate-reproduction
description: Reusable QA facts for gating agent_supervisor stabilization tasks (M0-T125/T126 line) — count reconciliation, D5 replay fixtures, golden_run fast subset, static-analysis false positives
metadata:
  type: project
---

Gating the D-024 supervisor-stabilization tasks (M0-T126 and its recert M0-T127). These are stable facts about how to reproduce the evidence, not one-off state.

**Reconcile test counts at the FROZEN SHA, never the producer's numbers.** Producer per-pack counts drift from the integrated identity because they measure a transient uncommitted worktree. At M0-T126 identity e029c8a the producer claimed 395 (next_task 19, loop 121) but collection/run gave **391** (next_task **18**, loop **118**) — over-count of 4. The 8-pack combined `pytest -q` = 391 passed, 0 fail, 0 skip. Always `pytest <file> --co -q` per pack and trust that, not the report.

**Golden_run fast subset (27) is a hand-picked class list, not a marker.** Fast = TwoUnitGoldenRunTests(6)+InjectedFaultTests(5)+WatcherCaptureTests(4)+WatcherLabelingTests(7)+WatcherPassivityTests(3)+WatcherStartEpilogueTests(1)+EpochRotationCompositionTests(1) = 27, runs in ~12s. The other 15 classes (Soak, ExtendedPause, AcceleratedOvernight, AutonomousSelection, LadderRegister, GoldenSequenceRegister, Section169Register, CampaignCrossingEvidence, OnDemandAfterCompact) are the ~3h13m R247 recert — do NOT run in a normal gate; budgeted to M0-T127. Reproduce fast subset via `-k "TwoUnitGoldenRunTests or InjectedFaultTests or Watcher... or EpochRotationCompositionTests"`.

**D5 replay fixtures are DERIVED, not verbatim.** `fixtures/m0t107_stream_d5.json` = 12 synthetic assistant turns with monotonic ramp usage; only turn-12 usage (input 2 + cache_creation 3962 + cache_read 67935 + output 647 = **72546** live) and the result event (**694251** cumulative) are the real preserved numbers. `live_context_tokens()` takes the peak per-turn (=turn 12), excludes the `type==result` event. Cross-check against: transcript `...wt-m0t107\0835bb80-...jsonl` (97 events, 36 assistant, 12 distinct msg ids, all tool_use) and audit `preserved-artifacts\audit.jsonl` (53 recs; seq 50=694251, seq 21=604772 origin [also 24], seq 8=622599, seq 40=640224). All trace exactly.

**Static-analysis "undefined function" flags on this code are false positives.** loop.py `_ceiling_context_tokens` (def 555, called 972/1644), command_docs.py `_strip_trailing_comment` (def 234, called 220 inside a function body), claude_runner.py live_ctx (assigned 1472, stored into RunResult 1509-1510) — all module-level forward refs resolved at call time; packs execute them. Don't re-flag.

**D9 next_task machinery scope.** Only `plan_close_run` (COMPLETE→IDLE run_closed edge) is wired into cli.py:2687. `record_advancement`/`select_next_packet`/`advance_and_select` are exactly-once CAS machinery (durable `compare_and_swap_state` BEGIN IMMEDIATE) that is SIMULATION-tested only — live auto-dispatch of the next selected packet is deliberately reserved to the R393 owner-authorized live commissioning journey. That is correct scoping, not a gap.
