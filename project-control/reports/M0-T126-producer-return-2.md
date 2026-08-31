# M0-T126 — producer return 2 (delta; VERBATIM agent-return capture; transport entity-decoding only)

Captured by the orchestrator on 2026-08-31 from the return channel of the same unnamed roster
producer spawn (logical identity `supervisor-stabilization-producer`), at the completion of the
R385 continuation directive (see `M0-T126-producer-return-1.md`). Orchestrator seam note
(D-024-R395): at this return the producer's uncommitted worktree work was captured as a durable
patch (216,236 bytes, sha256 `1a2c28652a75e768398497af3a24cdfc01fa3b026b1690ea37a9828c3bda5328`,
28 files, `git apply --check` clean against the control tip) BEFORE any integration, and this
agent context is RETIRED — it is never resumed again. The producer reported no context pressure
(R396 valve not tripped).

---VERBATIM-BEGIN---
Everything is green at the final identity. Here is my delta report.

---

## DELTA REPORT — M0-T126 continuation (all 17 defects now complete)

Not under context pressure (~14.4M tokens remaining); completed the full R385 list. Same worktree `agent-af926a5886c3c4ab3`, base HEAD `1bb7735…`.

### What changed since return 1 (7 → 17/17 defects)

**D6** (journal-order/START_CLAUDE rest) — DONE. `recovery.record_dispatch_intent`/`reconcile_dispatch_intent`; `loop.run_cycle` journals the intent before `run_unit` and reconciles after; `recovery.classify` returns AMBIGUOUS_EFFECT (`unit_dispatch_unreconciled`) on an unreconciled intent (additive branch — fires only when the marker is present). Tests: 3 crash-injection rows (post-Popen, partial-stream, checkpoint-before-extract) + reconciled control.

**D10** (HIGH — cross-process forwarded-prompt loss) — DONE. `loop.run` persists a durable next-unit-prompt pointer on every forward and consumes it exactly once on CLAUDE_RUNNING entry, dispatching the forwarded bytes instead of the generic default; forward message-id cycle number is journal-advancing (`cycle_base`), so a re-decision isn't dead-ended by `duplicate_suppressed`. Tests: `CrossProcessForwardResumeD10Tests` (3). **Root-caused a golden_run failure**: `test_an_injected_controller_restart_continues_without_duplicate_work` was passing *only because of the D10 bug* (duplicate-suppression dead-ended the 2nd start); updated it to the certified single-cycle shape (`--max-cycles 1`) — now passes and tests the D10 resume correctly.

**D16** (legacy records / dead-child sweep) — DONE. `recovery.sweep_dead_child_records` archives determined-dead child records with provenance at `recover_boot` (after classify; never touches surviving/undetermined); the live-token fold (i) is via D5's recording. Test: sweep archives with provenance.

**D4** (degenerate native-tools flag) — DONE, net-zero in claude_runner (at SLOC limit): renamed `RunResult.native_tools_guidance_present`, computed as sentinel-PRESENCE on the dispatched bytes after both appends. Test: 3-shape (fresh/old-contract/pre-seeded), removal-sensitive on the fresh shape.

**D7** (dead safe_auto_resume / misleading epilogue) — DONE: (a) cli epilogue annotates `resume permitted` on an operator-typed start (net-zero); (b) recovery `safe_auto_resume` documented R595-gated citing remote_approvals.py:295/307.

**G4 correction 3** — completed both halves: verdict-persistence (before/after) and campaign-advancement (before/after) interruption rows in `next_task` tests; the design record's scenario-9 sub-matrix names every row.

**Static-analysis items** — verified/resolved: the flagged "undefined `_ceiling_context_tokens`/`_strip_trailing_comment`" are false positives (module-level-defined, executed by tests); `live_ctx` is consumed (RunResult + `_ceiling_context_tokens`); `.get` guarded by `usage is None`; `runner: Any` is intentional (FakeRunner). loop.py made F401-clean (removed dead `import re`; `# noqa` on the deliberate re-export facade — `lp.TOUCH_NOTIFY` is used by a test). Confirmed the D5 live figure is consumed by **every** ceiling consumer (rotation flag + record_provider_session directly; pre-dispatch rotate + evaluate_ceiling-on-resume transitively via the continuity record).

### Final verification (final frozen identity)
- **2980 supervisor tests pass, 2 pre-existing skips** (was 2889 baseline); **all 27 fast golden_run tests pass**.
- Defect packs together: 130 passed. New/updated test counts: next_task 19, recovery 63, runner 74, loop 121, launch_seam 69, command_docs 17, orientation 10, checkpoint_journey 22.
- **ruff**: All checks passed on every touched file. **modularity_check --check**: failures 0 (claude_runner 1383/1383, cli 2953/2953 at limit via net-zero mods; loop 2030/2088; recovery 525). **command-doc tooth**: exit 0.

### Final 17/17 defect map (defect → seam → test)
D1/D14/D15/D17 command_docs tooth+CI+runbook; D2 launch_seam.evaluate_repo_binding; D3 turn_budget+orientation; D4 native_tools_guidance_present; D5 live_context_tokens+_ceiling_context_tokens; D6 recovery dispatch-intent→AMBIGUOUS; D7 epilogue+R595 note; D8 ROTATE→rotation seam; D9 next_task; D10 next-unit-prompt pointer+advancing cycle; D11/D12 loop._intent_stop; D13 assert_can_act before budget; D16 sweep_dead_child_records. Every entry has file:line + a removal-sensitive test in the design record.

### Reports (both updated to 17/17, pure ASCII)
- `project-control/reports/M0-T126-design-record.md` — Section 0 (17/17), full defect map, scenario-9 sub-matrix, residual-limitations (no defect deferred).
- `project-control/reports/M0-T126-producer-report.md` — final commands/counts, files, status.

### Not done / limitations
- No register defect deferred. The only unrun item is the ~3h R247 recert (packet-assigned to M0-T127).
- claude_runner.py/cli.py sit at their exact modularity limit — flagged for future planning (any further growth needs a `modularity_exceptions.json` entry, not in my allowed_paths, or a decomposition). Not blocking.

**Requested status: awaiting_gate.** No self-accept.
---VERBATIM-END---
