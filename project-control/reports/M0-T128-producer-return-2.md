# M0-T128 - producer return 2 (fresh-remediation; VERBATIM agent-return capture; transport entity-decoding only)

Captured by the orchestrator on 2026-08-31 from the return channel of the FRESH unnamed roster
remediation producer (logical identity `supervisor-wiring-producer`), dispatched per the
standing R395 rotate-at-seam rule after the G3/G4 verdicts (prior wiring-producer context
retired at its seam, never resumed). Orchestrator seam note: the remediation worktree work was
captured as a durable patch (42,312 bytes, sha256
`010cf7f52a47a2648bc2d48a21edafa7f7a9ea8b71466d57ac5400800d174444`, 6 files incl. 2
agent-memory files committed separately, `git apply --check` clean) BEFORE integration; this
context is likewise RETIRED. Orchestrator verification at the integrated tree: cross_task 45 +
next_task 18 + bounded_mode 91 = 154 passed; modularity failures 0; tooth 12/0.

---VERBATIM-BEGIN---
All four corrections are complete and verified. Returning to the orchestrator.

## M0-T128 remediation pass - complete (requested status: awaiting_gate)

**Worktree:** `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\agent-a4a43c0ea31c572e1` (isolated - guard PASS)
**Base SHA:** `93addac` (reset once, HEAD unchanged; no commit/push/ledger)

### Per-correction summary

**G3-C1 - driver mode confinement (production + test).** `run_task_queue` (`tools/agent_supervisor/next_task.py:763`; guard at `:792-793`) now asserts `args.mode == "limited-auto"` as its first act - before any packet read/snapshot/dispatch - refusing other modes with typed code `cross_task_mode_refused` + an audited `cross_task_mode_refused` row (rides the existing `next_task.NextTaskError` arm at cli.py:3070). The owner-enable half stays with `bounded_mode_gate` (division stated in design-record sec 7). Tests: `ModeConfinementTests` (4 nodes) in `tools/test_agent_supervisor_cross_task.py`. **Mutation proof:** neutralising the guard (`if False and ...`) turned the 3 refusal nodes RED (`NextTaskError not raised`), limited-auto positive stayed green; restore -> all green.

**G3-C2 - real `_run_loop`-altitude coverage + shared-budget doc.** `LiveRunLoopCrossTaskTests::test_two_task_journey_through_real_run_loop` drives both tasks through the REAL `cli._run_loop` (real config/model_selection; only `cli.ClaudeRunner`/`cli.CodexReviewer` faked), asserting (a) shared-run_id clean budget resume (`run_budget_started`x1, `run_budget_resumed`x1, no `budget_conflict`), (b) `run_closed` COMPLETE->IDLE on the shared journal between tasks, (c) D6 `pending_effects()` empty across the boundary. Documented in design-record new **section 5A**.

**G4-#1 - real dispatch-branch coverage.** `CmdStartDispatchTests` executes the VERBATIM cli.py:3069 `run = (...)` expression extracted from `cli.cmd_start` source (inspect+ast), not an inline copy: TRUE-branch node spies that dispatch reaches `run_task_queue` with `cli._run_loop` as the injected `run_one` and drives the journey through it; FALSE-branch node proves `_run_loop` called directly; a third guards the extraction. **Approach note:** full `cli.cmd_start` is impractical (its `auth`/`cli_capability_manifest` live probes need a real spawned provider + capability manifest - golden-run altitude; a `cli.main` probe refused at recover_boot). This is the "provably executes the real line" fallback the correction permits; the real `_run_loop` wrapper is separately covered by the C2 test.

**G4-O2 - category-1 sub-codes.** `Category1SubCodeTests`: `packet_unreadable` (missing file) and `packet_not_object` (valid JSON list) each assert their distinct code.

### Final self-check outputs (base 93addac)
- `pytest cross_task + next_task -q` -> **63 passed** (cross_task 45 = 35 original + 10 new; next_task 18 unbroken)
- FULL suite `pytest tools/test_agent_supervisor_*.py -q` -> **3035 passed, 2 skipped, 0 failed** (666.37s; baseline 3025 + 10; 2 skips are the pre-existing Py3.12 PEP-695 skips)
- `modularity_check.py --check` -> **failures 0**, warnings 11; next_task.py stays a non-blocking `review_signal` (712 SLOC). **cli.py UNCHANGED** (net-zero 2953/2953 preserved)
- `supervisor_command_doc_check.py` -> **12 checked, 0 failures** (exit 0)
- `ruff check` (next_task.py, cli.py, cross_task.py) -> **All checks passed!**
- ASCII: design-record 0, producer-report 0 non-ASCII bytes

### Changed files (all inside allowed_paths)
- `tools/agent_supervisor/next_task.py` (+22 - C1 guard only)
- `tools/test_agent_supervisor_cross_task.py` (+~380 - the four correction families)
- `project-control/reports/M0-T128-design-record.md` (sec 7 confinement + new sec 5A)
- `project-control/reports/M0-T128-producer-report.md` (remediation-pass section)

### Assumptions / limitations
- R401/R403 preserved: all tests use tempfile runtimes; no live runtime dir, preserved artifact, PR #241 merge, clear-recovery, loop start, or live commissioning touched.
- G4-#1 uses the exec-the-real-source-line fallback rather than full `cli.cmd_start` (rationale above); the real `_run_loop` wrapper is exercised end-to-end by the G3-C2 test.
- Scope was strictly the four corrections; no other behaviour changed. I do not self-accept - independent re-review pending.
---VERBATIM-END---
