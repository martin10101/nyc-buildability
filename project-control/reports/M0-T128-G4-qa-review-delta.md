# M0-T128 - G4 DELTA report (independent qa-engineer, read-only + read-only pytest) - VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31, re-verdicting required correction #1 and O2 at
the remediated identity de18f27. DELTA VERDICT: PASS, no residual corrections - the
CmdStartDispatchTests extraction is confirmed bound to the real cli.py:3069 bytes (a change to
the line fails the guard or branch tests), the real _run_loop journey test verified end-to-end,
both category-1 sub-codes asserted, all ten new tests removal-sensitive by binding, and every
number reproduced (45/18/91/3035-2-0 with the 3025+10 chain confirmed; modularity 0; tooth
12/0; ruff clean; ASCII clean; no existing test file modified).

---VERBATIM-BEGIN---
All verification complete. Here is my delta re-verdict.

---

# G4 (QA) Delta Re-Verdict - M0-T128 (remediated)

**Task:** M0-T128 - Amendment-25 Stage-3 cross-task wiring (remediation of G4 required-correction #1 and observation O2, plus G3 items C1/C2)
**Reviewed identity:** branch tip `1d00e7b`; remediated material `de18f27` (verified stable: `git diff de18f27 HEAD -- tools/agent_supervisor/ tools/test_agent_supervisor_*.py` empty). **cli.py is NOT in the delta** - cli.py:3069 is unchanged from my first review, so the new extraction test targets the real, untouched line.
**Reviewer:** qa-engineer (independent, read-only + read-only pytest). Delta name-only diff touches only `next_task.py` (production) + `cross_task.py` (new tests) + 3 reports - **no existing test file modified**.

## DELTA VERDICT: PASS - required correction #1 and observation O2 are both resolved; the 10 new tests are removal-sensitive; all numbers reproduce; no regression. No residual corrections.

## Required correction #1 (cli.py:3069 dispatch branch) - RESOLVED

Two complementary tests close the gap I raised, and they satisfy the exact fallback my correction permitted ("evaluates the actual cli.py:3069 line, not an inline copy"):

- **`CmdStartDispatchTests` (3) executes the VERBATIM real line.** `dispatch_expression()` does `inspect.getsource(cli.cmd_start)` -> `ast.parse`/walk for the `run = <IfExp>` assignment whose source segment contains `next_task.run_task_queue`, then returns `ast.get_source_segment(...)` - the real bytes, not a copy. The tests `exec(compile(dispatch_expression(), ...))` that segment:
  - TRUE branch (`--max-tasks 2`/queue): spies `nt.run_task_queue`, asserts `captured["run_one"] IS cli._run_loop`, `dispatched==2`, `advanced==["M0-TA","M0-TB"]`, both `is_advanced` over the real journal.
  - FALSE branch (defaults, supervised): asserts the driver is NOT entered and `_run_loop` is called exactly once.
  - Extraction guard: asserts the segment contains `run_task_queue(args, checkout, journal, audit, _run_loop)`, `_run_loop(args, checkout, journal, audit)`, `max_tasks`, `packet_queue`.
  I confirmed this is genuinely the real line: a change to cli.py:3069's condition or args changes the extracted segment and fails either the guard (structure/args) or the branch tests (behavior). This is not an inline copy - it is bound to the source.
- **`LiveRunLoopCrossTaskTests` (1) drives the REAL `cli._run_loop` end-to-end.** `run_task_queue(..., cli._run_loop)` with a real config.toml/model_selection.toml, only `cli.ClaudeRunner`/`cli.CodexReviewer` factories faked; everything else in `_run_loop` runs real. Asserts dispatched==2, advanced==[TA,TB] (real CAS), `run_budget_started`x1 + `run_budget_resumed`x1 with **no** `budget_conflict`/`run_budget_refused` (shared-run_id clean resume), a real `run_closed` COMPLETE->IDLE transition on the shared journal, and empty `pending_effects()` (D6 reconciled across the boundary).

The only untested span - `cmd_start`'s entry-to-3069 gauntlet - requires live auth + `cli_capability_manifest` probes (golden-run altitude), honestly disclosed by the producer and legitimately out of focused-unit scope. Correction #1's intent is met: the actual dispatch line is provably executed, and the real `_run_loop` wrapper is exercised end-to-end.

## Observation O2 (category-1 sub-codes) - RESOLVED

`Category1SubCodeTests` (2): missing file -> `packet_unreadable`; valid JSON list `[1,2,3]` -> `packet_not_object`. I confirmed `_read_packet_file` (next_task.py:489) raises three distinct codes at :501/:506/:509 (`packet_unreadable`/`packet_unparseable`/`packet_not_object`); all three category-1 sub-codes are now individually asserted (`packet_unparseable` was already covered).

## Reproduced numbers

| Claim | Reproduced | Result |
|---|---|---|
| cross_task | **45 passed** (35 original + 10 new) | MATCH |
| next_task unbroken | **18 passed** | MATCH |
| bounded_mode unbroken | **91 passed** (with next_task = 109 together) | MATCH |
| full suite, golden included | **3035 passed, 2 skipped, 0 failed** (644s) | MATCH |
| arithmetic 3025 + 10 = 3035 | collection **3037** = 3035 pass + 2 skip | CONFIRMED |
| modularity `--check` | **failures 0** (11 warnings; next_task.py review_signal) | MATCH |
| command-doc tooth | **12/0, exit 0** | MATCH |
| ruff (next_task.py, cli.py, cross_task.py) | **All checks passed!** | MATCH |
| both reports pure ASCII | design-record 0, producer-report 0 | MATCH |
| no existing test file changed | delta touches only new-tests file among tests | CONFIRMED |

## New-test quality (10 tests) - all removal-sensitive by binding

- **ModeConfinementTests (4):** 3 refusal nodes assert `NextTaskError` code `cross_task_mode_refused` AND the driver body never ran (`dispatched==[]`, no queued-digest snapshot, `cross_task_mode_refused` audited, no `cross_task_dispatch`); 1 positive proves limited-auto proceeds. Producer's mutation proof (`if False and ...` -> 3 nodes RED) confirms removal-sensitivity; I verified the guard at next_task.py:792 is the first act of `run_task_queue`, fail-closed before any packet read.
- **Category1SubCodeTests (2):** assert the two distinct codes (would fail if `_read_packet_file` collapsed them).
- **CmdStartDispatchTests (3):** bound to the real extracted source line (above); TRUE/FALSE branch + extraction guard each fail on the corresponding cli.py:3069 regression.
- **LiveRunLoopCrossTaskTests (1):** binds real-`_run_loop` advancement, shared-budget resume, real close-run, and D6 empty-effects (above).

## Prior observations
O1 (next_task.py growth to ~712 SLOC) remains a non-blocking `review_signal` warning (below HARD 1000); cli.py unchanged (net-zero at limit). No new observations.

**Requested gate result:** **PASS** (no residual required corrections) at remediated identity `de18f27` (tip `1d00e7b`). All commands reproduce read-only.

Note for the orchestrator: reviewed via `git checkout --detach 1d00e7b` in my own isolated worktree (clean tree restored first; my untracked memory index + a local memory edit set aside and re-applied). The orchestrator owns this worktree's post-review lifecycle.
---VERBATIM-END---
