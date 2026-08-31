# M0-T128 producer report - Stage-3 live cross-task wiring

Producer: supervisor-wiring-producer (fresh unnamed roster spawn), worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\agent-a381aa68e1527a366`
(`wt-m0t128`). Base identity `7576e0dee2800cf54f520e944ea3a8bec6da0cc4` on
`control/D-024-fable-codex-loop`. Design rationale: `M0-T128-design-record.md`.
This report carries the exact commands and outputs. No commit/push/ledger
mutation performed (orchestrator integrates from the worktree).

## Worktree discipline

- `git rev-parse --show-toplevel` ->
  `C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/.claude/worktrees/agent-a381aa68e1527a366` (isolated worktree - guard PASS).
- `git reset --hard 7576e0dee2800cf54f520e944ea3a8bec6da0cc4` -> `HEAD is now at 7576e0d`;
  `git rev-parse HEAD` -> `7576e0dee2800cf54f520e944ea3a8bec6da0cc4`.

## Changed files (all inside allowed_paths)

```
 M tools/agent_supervisor/cli.py           (+12 / -7 net-zero SLOC; see below)
 M tools/agent_supervisor/next_task.py     (+527: eligibility engine + between-task seam + cross-task driver)
 ?? tools/test_agent_supervisor_cross_task.py   (new: 10-family removal-sensitive coverage, 35 tests)
 ?? project-control/reports/M0-T128-design-record.md
 ?? project-control/reports/M0-T128-producer-report.md
```

No files outside allowed_paths were touched. `command_docs.py`,
`supervisor_command_doc_check.py`, `.github/workflows/ci.yml`, the runbook, and
`claude_runner.py` / `loop.py` were NOT modified (not needed - see the tooth section below).

## Per-requirement summary with file:line

- **R400 (live cross-task continuation behind the existing gate)**: driver
  `next_task.run_task_queue` (`tools/agent_supervisor/next_task.py:763`), wired in
  `cli.cmd_start` at the existing dispatch branch (`tools/agent_supervisor/cli.py:3069`)
  behind the pre-existing `bounded_mode_gate` (`cli.py:2918`). First task ==
  owner-typed `--task-packet` via `_run_loop`; successors from `--packet-queue`
  (`cli.py:3304`); bounded by `--max-tasks` default 1 (`cli.py:3303`).
- **R402 (exactly-once / gates / budget / audit / isolation)**: advancement via
  the existing single-winner CAS `record_advancement` (`next_task.py:187`) recorded
  BEFORE selection; completion gated by `run_reached_complete` (`next_task.py:702`);
  between-task seam `between_task_seam` (`next_task.py:664`) re-checks intents /
  budget / rotation ceiling reusing `stop_intent`, the durable budget report, and
  `rotation.rotation_pending`; launch isolation re-enforced by the driver's
  eligibility (`launch_seam.enforce_launch_bindings`) AND `_run_loop`'s existing
  backstop (`cli.py:2655`); typed audit rows `cross_task_dispatch` /
  `cross_task_candidate_skipped` / `cross_task_advancement` /
  `cross_task_intent_stop` / `cross_task_budget_stop` / `cross_task_rotation_pending`.
  No new activation surface, no R595/broker/allowlist change.
- **R404 (ten removal-sensitive live-path families)**:
  `tools/test_agent_supervisor_cross_task.py` (35 tests). Family map in the design
  record sec 9.
- **R405 (never silently select ineligible work)**: `evaluate_eligibility`
  (`next_task.py:551`) - eleven fail-closed categories, each a visible skip with a
  code + reason + audit row. Rule set table in the design record sec 3.
- **R401 / R403 (prohibitions)**: all tests use `tempfile` runtime dirs (temp
  journal + temp audit); no live runtime dir, no preserved artifact, no PR #241,
  no clear-recovery, no loop start, no live commissioning touched.

(Line numbers are at the final worktree state; the reviewer should confirm against
source.)

## Live packet-status survey (grounds the eligible-status design choice)

`project-control/tasks/*.json` status census at base identity:
`accepted 142, backlog 17, awaiting_gate 9, blocked 2, claimed 2, in_progress 1`.
The narrow eligible set `{"claimed"}` selects only tasks claimed for supervised
execution; every other status is refused (family 2 `ineligible_status`).

## Commands run and outputs

### Import + wiring sanity

`python -c "import tools.agent_supervisor.next_task; import tools.agent_supervisor.cli; ..."`
-> `import OK`, `has run_task_queue True`.

### Modularity (net-zero on the at-limit files)

`python -c "source_lines(...)"`:
- `tools/agent_supervisor/cli.py` sloc=2953, baseline=2685, limit=2953 (net-zero, PASS).
- `tools/agent_supervisor/next_task.py` sloc=691 (NOT baseline-tracked; below HARD 1000; a non-blocking review_signal warning above WARN 600).

`python tools/modularity_check.py --check --repo .`:
```
selected 335 files; failures 0; warnings 11
  ... warn review_signal: tools/agent_supervisor/next_task.py - above the warning threshold ...
```
-> `failures 0` (PASS). next_task.py joins the existing warn list (durable_state,
process, recovery_probes, refusal_bridge, repair_gate) - consistent with the
repo's accepted state; no failure.

### Command-document tooth (unchanged, still green)

`python tools/supervisor_command_doc_check.py`:
```
summary: 12 presented supervisor command(s) checked; 0 failure(s)
```
-> `TOOTH_EXIT=0`. The two new flags (`--max-tasks`, `--packet-queue`) have safe
certified defaults and are deliberately NOT in `REQUIRED_START_FLAGS`, so the
runbook's pinned single-task start (line 232) still validates with no runbook /
`command_docs.py` change.

### Ruff (touched files)

`ruff check tools/agent_supervisor/next_task.py tools/agent_supervisor/cli.py tools/test_agent_supervisor_cross_task.py`
-> `All checks passed!` (ruff 0.13.0). (One initial `F841` unused-variable in the
test was removed before this pass.)

### New coverage file

`python -m pytest tools/test_agent_supervisor_cross_task.py -q`
-> `35 passed in 4.89s`.

### Existing next_task leaf tests (unbroken by the additions)

`python -m pytest tools/test_agent_supervisor_next_task.py -q`
-> `18 passed in 1.47s`.

### FULL supervisor suite (all test_agent_supervisor_*.py, one process, golden included)

`python -m pytest tools/test_agent_supervisor_*.py -q`
-> `3025 passed, 2 skipped in 662.92s (0:11:02)`  (exit 0).

The 2 skips are the pre-existing Python-3.12 PEP 695 collection skips (this sandbox
is 3.11; unchanged from the M0-T127 recert baseline of 2,990 passed / 2 skipped -
now +35 from this task's new file). Zero failures.

## Environment / limitations / anything out of scope

- Sandbox Python is 3.11 (2 pre-existing 3.12-only skips); all other tests run and
  pass. No new dependency added.
- Golden-run: no new golden scenario added (design record sec 10 - the two-task
  journey is proven by the real-loop family-1 test + crash-matrix reopen tests at
  a faster, deterministic altitude; a cross-task golden blob would move the
  disclosed golden blob for coverage already provided).
- Runbook: NOT modified. A documented multi-task command shape for the later R407
  commissioning presentation is in the design record sec 2; presenting/validating it
  belongs to the R406/R407 recert+presentation step, not this wiring task.
- I did NOT run `tools/project_control.py`, git commit/push, or `gh` (orchestrator
  duty). I did NOT run the live supervisor, touch the live runtime dir, or perform
  any commissioning (R401/R403).
- The R406 full R247 recertification at the final frozen identity + independent
  gates + DCV, and the R407 owner-executed seven-fact commissioning, are separate
  downstream steps this task does not perform.

## Remediation pass (M0-T128 rework; fresh producer, base 93addac)

A fresh remediation producer addressed the consolidated G3/G4 correction list at
base identity `93addac` (worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\agent-a4a43c0ea31c572e1`).
Scope was strictly the four named corrections; no other behaviour changed. Engineering-
reliability sections applied: S2 (smallest fitting change - the C1 confinement is a
single fail-closed guard in the owning module, cli.py untouched at net-zero), S3
(red/green + mutation proof, below), S5/S6 (the shared-run_id budget-resume semantics
proven at the real _run_loop altitude), S7 (typed refusal on the caller-visible path),
S8 (frozen-identity + integration contexts), S9 (severity triage).

**G3-C1 - driver mode confinement (production + test).** `run_task_queue`
(`tools/agent_supervisor/next_task.py:763`; the guard at :792-793) now asserts
`args.mode == "limited-auto"` as its FIRST act, before any packet is
read/snapshotted/dispatched, refusing any
other mode with the typed code `cross_task_mode_refused` + an audited
`cross_task_mode_refused` row. The owner-ENABLE half stays enforced pre-dispatch by
`bounded_mode_gate`; this is the complementary MODE half (division stated in design
record sec 7). The refusal rides the existing `next_task.NextTaskError` arm of the
cmd_start dispatch try/except (cli.py:3070) - a report, not a traceback. Removal-
sensitive test: `ModeConfinementTests` (`tools/test_agent_supervisor_cross_task.py`):
`test_supervised_multi_task_via_queue_is_refused`,
`test_shadow_multi_task_via_max_tasks_is_refused`,
`test_supervised_multi_task_via_max_tasks_only_is_refused` (each: typed refusal,
nothing dispatched, no successor digest snapshot, audit row) and
`test_limited_auto_multi_task_proceeds`. Mutation proof (S3.4): neutralising the
guard (`if False and mode != "limited-auto":`) turned the three refusal tests RED
(`NextTaskError not raised`) while the limited-auto positive stayed green; restoring
the guard returned all four to green.

**G3-C2 - real `_run_loop`-altitude cross-task coverage + shared-budget semantics.**
`LiveRunLoopCrossTaskTests::test_two_task_journey_through_real_run_loop` drives the
journey through the REAL `cli._run_loop` (real config + model_selection; only
`cli.ClaudeRunner`/`cli.CodexReviewer` faked to COMPLETE-returning loop fakes),
asserting (a) task 2 takes the clean budget RESUME branch on the shared
checkout-derived run_id (`run_budget_started` x1, `run_budget_resumed` x1, NO
`budget_conflict`/`run_budget_refused`), so ONE owner-set run budget bounds the whole
journey; (b) `plan_close_run` closes COMPLETE->IDLE on the SHARED journal between
tasks (a `state_transition` with `policy_result=run_closed`, `COMPLETE`->`IDLE`); (c)
the D6 dispatch-intent record/reconcile cycle behaves across the boundary
(`journal.pending_effects()` empty after the completed journey). The per-journey
shared-budget/run_id semantics are documented in design record new section 5A ("run_id
and budget across a multi-task journey").

**G4-#1 - real dispatch-branch coverage.** `CmdStartDispatchTests` executes the
VERBATIM `run = (next_task.run_task_queue(...) if ... else _run_loop(...))` expression
extracted from `cli.cmd_start`'s own source (via `inspect`/`ast`), NOT an inline copy:
`test_multi_task_start_routes_to_the_driver_with_run_loop_injected` (TRUE branch,
`--max-tasks 2`/`--packet-queue`) proves dispatch reaches `run_task_queue` with the
REAL `cli._run_loop` as the injected 5th `run_one` argument (spy asserts
`captured["run_one"] is cli._run_loop`) and drives the full two-task journey through
it; `test_default_start_calls_run_loop_directly_not_the_driver` (FALSE branch,
defaults) proves `_run_loop` is called directly and the driver is never entered;
`test_the_extracted_line_is_the_real_dispatch_expression` guards the extraction.
Approach note (per the correction's own allowance): full `cli.cmd_start` cannot be
driven in a focused unit test because its live-revalidation gauntlet (the `auth` and
`cli_capability_manifest` probes) requires a real launched provider process and a live
capability manifest (golden-run altitude); a direct probe of `cli.main` start refused
at `recover_boot` with `revalidation failed for ['auth','cli_capability_manifest']`.
Executing the extracted source line is the "provably executes the real line" fallback
the correction permits - a regression in the routing condition or in the arguments
passed to `run_task_queue` changes the executed bytes and is caught. The real
`_run_loop` wrapper is separately exercised end-to-end by the G3-C2 test.

**G4-O2 - category-1 sub-codes.** `Category1SubCodeTests`:
`test_a_file_io_error_is_packet_unreadable` (missing packet file -> `packet_unreadable`)
and `test_valid_json_that_is_not_an_object_is_packet_not_object` (valid JSON list ->
`packet_not_object`), each asserting its distinct code via `evaluate_eligibility`.

### Remediation self-check commands + outputs (base 93addac)

- `python -m pytest tools/test_agent_supervisor_cross_task.py tools/test_agent_supervisor_next_task.py -q`
  -> `63 passed` (cross_task 45 = 35 original + 10 new; next_task 18 unbroken).
- `python -m pytest tools/test_agent_supervisor_bounded_mode.py -q` -> included in the
  full suite (no regression).
- FULL suite, one process, golden included:
  `python -m pytest tools/test_agent_supervisor_*.py -q`
  -> `3035 passed, 2 skipped in 666.37s (0:11:06)` (0 failed). Baseline 3025 + 10 new.
  The 2 skips are the pre-existing Python-3.12 PEP 695 collection skips (sandbox is 3.11).
- `python tools/modularity_check.py --check` -> `selected 335 files; failures 0;
  warnings 11`; next_task.py stays a non-blocking `review_signal` warning (712 SLOC,
  below WARN-tracked HARD 1000). cli.py UNCHANGED (net-zero 2953/2953 preserved -
  the C1 check lives in next_task.py, which has headroom).
- `python tools/supervisor_command_doc_check.py` -> `12 presented supervisor
  command(s) checked; 0 failure(s)` (exit 0).
- `python -m ruff check tools/agent_supervisor/next_task.py tools/agent_supervisor/cli.py
  tools/test_agent_supervisor_cross_task.py` -> `All checks passed!` (ruff 0.13.0).
- ASCII check: design-record 0 non-ASCII bytes, producer-report 0 non-ASCII bytes.

Changed files (remediation pass, all inside allowed_paths): `tools/agent_supervisor/
next_task.py` (+22, the C1 confinement guard), `tools/test_agent_supervisor_cross_task.py`
(+~380, the four correction test families), `project-control/reports/M0-T128-design-record.md`
(sec 7 confinement statement + new sec 5A shared-budget semantics),
`project-control/reports/M0-T128-producer-report.md` (this section). `cli.py` NOT
modified. R401/R403 preserved: all tests use tempfile runtimes; no live runtime dir,
preserved artifact, PR #241 merge, clear-recovery, loop start, or live commissioning.

## Requested status

`awaiting_gate` - the four consolidated corrections (G3-C1/C2, G4-1/O2) are complete
with removal-sensitive + mutation-proven coverage; all self-checks green (full suite
3035 passed / 2 pre-existing skips / 0 failed, modularity 0 failures, tooth exit 0,
ruff clean, reports ASCII). Independent re-review pending; I do not self-accept.
