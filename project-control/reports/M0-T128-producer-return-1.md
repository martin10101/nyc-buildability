# M0-T128 - producer return 1 (VERBATIM agent-return capture; transport entity-decoding only)

Captured by the orchestrator on 2026-08-31 from the return channel of the FRESH unnamed roster
wiring producer (logical identity `supervisor-wiring-producer`), dispatched under Amendment 25.
Orchestrator seam note (R395 standing): the worktree work was captured as a durable patch
(94,045 bytes, sha256 `e5b0d3f08311762ecf7410871274ecc7b0ca7ac84611c4ee0631d34786aea322`,
5 files, `git apply --check` clean) BEFORE integration; this producer context is RETIRED.
Orchestrator verification at the integrated tree: 5 key packs 335 passed; modularity failures 0;
command-doc tooth 12/0; ruff clean on the three touched Python files.

---VERBATIM-BEGIN---
All work is complete and the task diff is strictly within allowed_paths. Here is my compact return to the orchestrator.

## M0-T128 producer return - Stage-3 live cross-task wiring (D-024 Amendment 25)

**Worktree / base:** `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\agent-a381aa68e1527a366` (`wt-m0t128`); base `7576e0dee2800cf54f520e944ea3a8bec6da0cc4` on `control/D-024-fable-codex-loop` (guard PASS, reset verified). No commit/push/ledger/gh performed.

**Per-requirement (file:line at final worktree state):**
- **R400** - driver `next_task.run_task_queue` (`tools/agent_supervisor/next_task.py:763`), wired at the existing dispatch branch `cli.cmd_start` (`cli.py:3069`, a one-line ternary) behind the pre-existing `bounded_mode_gate` (`cli.py:2918`). First task = owner-typed `--task-packet` via `_run_loop`; successors from new `--packet-queue` (`cli.py:3304`); bounded by new `--max-tasks` default 1 (`cli.py:3303`). No new activation surface, no R595/broker/allowlist change.
- **R402** - advancement via the existing single-winner CAS `record_advancement` (`next_task.py:187`) recorded BEFORE selection; completion gated by `run_reached_complete` (`next_task.py:702`); between-task seam `between_task_seam` (`next_task.py:664`) re-checks intents/budget/rotation-ceiling reusing `stop_intent` + durable budget report + `rotation.rotation_pending`; isolation re-enforced by driver eligibility (`launch_seam.enforce_launch_bindings`) AND `_run_loop`'s backstop (`cli.py:2655`); typed audit rows added. Only NEW durable keys written (R374/R375 intact).
- **R404** - new `tools/test_agent_supervisor_cross_task.py`, 35 tests, all ten families (map in design record sec 9).
- **R405** - `evaluate_eligibility` (`next_task.py:551`): eleven fail-closed categories, each a visible skip (code+reason+audit row), never silent; exhausted eligible set lands `NO_ELIGIBLE_WORK`.
- **R401/R403** - tests use temp runtimes only; no live runtime dir/preserved artifact/PR #241/clear-recovery/loop start/commissioning touched.

**Final test totals:**
- New file: `35 passed` (4.89s).
- Existing leaf: `tools/test_agent_supervisor_next_task.py` `18 passed` (unbroken).
- FULL supervisor suite (all `test_agent_supervisor_*.py`, one process, golden included): **`3025 passed, 2 skipped, 0 failed`** (662.92s). The 2 skips are the pre-existing Python-3.12 PEP 695 collection skips (was 2,990 passed at the M0-T127 recert baseline; +35 from this file).

**Self-checks:**
- Modularity: `python tools/modularity_check.py --check --repo .` -> `failures 0` (cli.py net-zero at 2953/2953; next_task.py 276->691, non-baseline, a non-blocking review_signal warning, below HARD 1000).
- Command-doc tooth: `python tools/supervisor_command_doc_check.py` -> `12 checked; 0 failure(s)`, exit 0 - no runbook/`command_docs.py` change needed (new flags are optional with certified defaults, deliberately NOT in `REQUIRED_START_FLAGS`).
- Ruff: `ruff check` on the three touched `.py` files -> `All checks passed!`.

**Changed files (all inside allowed_paths):** `tools/agent_supervisor/cli.py` (M, net-zero SLOC), `tools/agent_supervisor/next_task.py` (M, +527), `tools/test_agent_supervisor_cross_task.py` (new), `project-control/reports/M0-T128-design-record.md` (new), `project-control/reports/M0-T128-producer-report.md` (new). Both reports pure ASCII. Nothing outside allowed_paths (an in-worktree memory-file edit was reverted to keep the gated diff strictly scoped).

**Design/limitations (full list in the design record sec 12):** family 1 exercises the REAL `SupervisedLoop`+journal+`plan_close_run`+advancement with only the provider faked at the standard `run_unit`/`review` seam (not full `cmd_start`); the other nine families use a scripted `run_one` to control completion/crash/eligibility precisely. Eligible-status set is a narrow documented choice `{"claimed"}`. No new golden scenario (documented decision). No live commissioning (R403) - the R406 recert + R407 seven-fact commissioning are separate downstream steps.

**Requested status: `awaiting_gate`.** Implementation + removal-sensitive coverage complete, all self-checks green; independent G2/G3/G4 review pending - I do not self-accept.
---VERBATIM-END---
