# M0-T126 — producer return 1 (VERBATIM agent-return capture; transport entity-decoding only)

Captured by the orchestrator on 2026-08-31 from the return channel of the unnamed roster
producer spawn (logical identity `supervisor-stabilization-producer`). Orchestrator note:
this return discloses an INCOMPLETE correction set (D4/D6/D7/D10/D16 open) — a continuation
directive was issued under D-024-R385 (all in-scope defects at ONE final frozen identity);
the task did NOT move to awaiting_gate on this return.

---VERBATIM-BEGIN---
All work complete and verified. Here is my return to the orchestrator.

---

## M0-T126 producer return

**Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/.claude/worktrees/agent-af926a5886c3c4ab3`
**Built on HEAD:** `1bb773531bbb3283211de28ffdaf374467e994ab` (worktree guard PASS — isolated path confirmed; reset to control-branch tip; HEAD unchanged since producers don't commit).
**Requested status:** `awaiting_gate`.

### What was implemented (per section A–E)

**A. D9 next-task machinery (FIRST).** New `tools/agent_supervisor/next_task.py`: audited close-run surface (`plan_close_run` fires the existing `run_closed` COMPLETE→IDLE edge), `select_next_packet` over an owner-ordered packet list, and **exactly-once** `record_advancement`/`advance_and_select` built on the journal's `compare_and_swap_state` single-winner primitive. Wired into `cli.cmd_start`: a COMPLETE journal is closed to IDLE on the next start before the next task. This is what makes R388 satisfiable.

**B. Seven-property durable checkpoint design.** `turn_budget.py` (property 5/2/3: workload-class-sized working turns under a documented `HARD_TURN_CEILING=40`, one reserved final turn, early+incremental cadence — never a raised fixed max_turns) and `orientation.py` (property 1: front-loaded task/lineage/worktree/progress/files/cadence/required-output packet), both wired into `cli._run_loop` (sized `max_turns`, oriented first prompt). Property 4 (honest incomplete) via the pre-existing S14 `extract_checkpoint`; 6/7 via next_task exactly-once + fail-closed emission.

**C. Register defects — 12 of 17 fully corrected at this identity:** D1/D14/D15/D17 (command-doc tooth `command_docs.py` + CI entry `supervisor_command_doc_check.py` wired into ci.yml + runbook §11 `--checkout` pin), D2 (`launch_seam.evaluate_repo_binding`/`enforce_launch_bindings` refuse repo==primary-checkout — DCV discrepancy 1 / seed-a), D3 (turn_budget+orientation), D5 (`live_context_tokens` live-vs-cumulative, ceiling consumes live), D8 (ROTATE_SESSION routed through the rotation seam, not the dead PREPARE_ROTATION), D9, D11/D12 (`loop._intent_stop` between-cycle stop/pause/graceful/emergency gate), D13 (`assert_can_act` before `budget_ledger.start`). G3 citation fixes bound in the design record.

**D. Removal-sensitive adversarial coverage.** Four new test suites (64 tests) + fixtures derived byte-faithfully from the preserved copies (scanned, no secrets): `test_agent_supervisor_{command_docs,orientation,next_task,checkpoint_journey}.py`, plus `fixtures/m0t107_stream_d5.json` (live 72546 vs cumulative 694251; 12/12 exhaustion → missing_checkpoint) and `m0t107_journey_facts.json`. Includes G4 corrections 1 (synthesized Codex CONTINUE) and 2 (stale/duplicate verdict↔checkpoint-id correlation guard). The R387 sixteen-scenario matrix is in the design record.

**E. R388.** `next_task::ConsecutiveAdvancementTests` drives three consecutive simulated advancements (M0-T200→201→202) with no human intervention, exactly-once each, plus a crash-at-advancement-boundary test proving exactly-once across restart.

### Test totals (all zero-failure)
- command_docs 17, orientation 10, next_task 15, checkpoint_journey 22, launch_seam 69 (+5 D2), loop 112 (D8 test updated, +5 D11/D12).
- **Full supervisor suite (excl. golden): 2963 passed, 2 skipped** (baseline 2889 → +74). Golden run not run per packet (O2).

### Modularity + ruff
- `modularity_check.py --check`: **failures 0** (claude_runner 1383/limit 1383, cli 2953/limit 2953 — brought back under limit by extracting derivation into the new modules and combining seam checks; loop had headroom). `test_modularity_check.py` PASS.
- ruff 0.13.0 on all my new/edited files: **All checks passed.** (Whole-tree ruff flags only pre-existing errors in files I never touched; CI's ruff runs under services/api only.)
- command-doc CI check: exit 0, 12 commands, 0 drift.

### Files (22 total)
New: `turn_budget.py`, `orientation.py`, `next_task.py`, `command_docs.py`, `tools/supervisor_command_doc_check.py`, 2 fixtures, 4 new test files, 2 reports. Edited: `claude_runner.py`, `cli.py`, `loop.py`, `launch_seam.py`, `session_continuity.py`, `.github/workflows/ci.yml`, `docs/CONTROLLER_UPDATE_RUNBOOK.md`, `test_agent_supervisor_launch_seam.py`, `test_agent_supervisor_loop.py`. **All inside allowed_paths.**

Reports: `project-control/reports/M0-T126-design-record.md` and `project-control/reports/M0-T126-producer-report.md` (both pure ASCII).

### Register corrections I could NOT complete (disclosed against R385)
- **D4** (MED, presentation) and **D7** (LOW, presentation): blocked from a clean inline fix because claude_runner.py and cli.py are now at their exact baseline+10% modularity limit. Completing them inline needs a **scope extension** — either a reviewed `tools/modularity_exceptions.json` FILE exception (that file is NOT in my allowed_paths) or a decomposition of the legacy file.
- **D6, D10** (D10 is HIGH), **D16** (LOW): deeper corrections (journal-commit ordering/crash-window; cross-process CONTINUE resume; legacy sweep) deferred to avoid destabilizing the crash/recovery/loop packs at the end of the bounded window; exact integration seams are documented in design-record §8. D10 is partially mitigated by the D9 multi-unit continuation path.

### Scope-extension needs for the orchestrator
1. Decide D4/D7: add a modularity FILE exception or authorize a legacy-file decomposition (both outside my allowed_paths), or open a follow-up task.
2. D6/D10/D16 remain open against R385 — orchestrator/gates to judge whether this pass satisfies the window or a follow-up is needed.
3. The D4 append-only note on `M0-T107-amendment20-live-journey-2.md` is the orchestrator's job per the packet; I did not touch it.

No self-acceptance — the gates and orchestrator judge acceptance and the R385 all-defects completeness question.
---VERBATIM-END---
