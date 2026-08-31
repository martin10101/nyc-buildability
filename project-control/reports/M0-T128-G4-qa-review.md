# M0-T128 - G4 report (independent qa-engineer, read-only + read-only pytest) - VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31. VERDICT: PASS with 1 required correction
(BLOCKING for acceptance per gate-verdict semantics): the cli.py:3069 dispatch branch - the
task's central wiring point - has zero real test coverage (every test drives run_task_queue
directly; DefaultShapeTests re-implements the condition inline instead of invoking cmd_start).
Non-blocking O1 (next_task.py growth review_signal) and O2 (two category-1 sub-codes not
individually asserted). Every reproducible number MATCHED: 35/18 packs, full suite 3025/2/0
with the 2990+35 chain confirmed, no existing test file modified, bounded_mode+launch_seam 160,
tooth 12/0, modularity 0, ruff clean, golden blob byte-identical, reports ASCII. All ten R404
families audited with real-journal removal-sensitive bindings; all eleven R405 categories
covered by code-asserting tests. Remediation bundles with G3's C1/C2 into ONE fresh producer
pass (R395 standing).

---VERBATIM-BEGIN---
All verification complete. Here is my G4 gate report.

---

# G4 (QA) Gate Report - M0-T128 (Amendment-25 Stage-3 cross-task wiring)

**Task:** M0-T128 - wire the simulation-proven exactly-once next-task machinery into the live limited-auto path behind the existing bounded-mode owner gate (D-024-R400..R405)
**Reviewed identity:** branch tip `533f43a`; material `1485c73` (verified stable: `git diff 1485c73 HEAD -- tools/agent_supervisor/ tools/test_agent_supervisor_*.py` empty).
**Reviewer:** qa-engineer (independent, read-only + read-only pytest). No writes outside `.claude/agent-memory/qa-engineer/`; all test runtimes are temp dirs (R401 preserved; live journal never opened).
**Environment:** Python 3.11.9, pytest 8.4.2, ruff 0.13.0.

## VERDICT: PASS - with 1 numbered required correction (blocking for acceptance) + 2 non-blocking observations

The R404 ten-family and R405 eleven-category machinery is thoroughly implemented and removal-sensitively tested against a real durable journal. The one material gap is that the task's central wiring point - the `cli.cmd_start` dispatch branch that actually calls `run_task_queue` - has **zero test coverage**; every test drives the driver directly. This is a coverage gap at the integration seam, not a demonstrated defect, so PASS-with-required-correction (consistent with campaign precedent), but it must be closed before the R406/R407 commissioning steps rely on this wiring.

## (1) Reproduced-numbers table

| Claim | Reproduced | Result |
|---|---|---|
| `test_agent_supervisor_cross_task.py` | **35 passed** (5.86s) | MATCH |
| `test_agent_supervisor_next_task.py` unbroken | **18 passed** (1.62s) | MATCH |
| Full suite, one process, golden included | **3025 passed, 2 skipped, 0 failed** (648s) | MATCH |
| Baseline arithmetic 2990 + 35 = 3025 | 2990 (M0-T127) + 35 (new file) = **3025** | CONFIRMED |
| No pre-existing test changed (`git diff 7576e0d 1485c73 --name-only`) | change set = cli.py, next_task.py (production) + **new** cross_task test file + 3 reports + 1 campaign json; **no existing test file modified** | CONFIRMED |
| bounded_mode + launch_seam regression | **160 passed** (bounded_mode 91 + launch_seam 69) | MATCH (no regression) |
| modularity `--check` | **failures 0** (335 files; 11 warnings, next_task.py joins the warn list) | MATCH |
| command-doc tooth | **12 checked, 0 failures, exit 0** | MATCH |
| ruff (next_task.py, cli.py, cross_task.py) | **All checks passed!** | MATCH |
| golden blob unchanged (`git diff 7576e0d 1485c73 -- ...golden_run.py`) | **empty** | MATCH (no-new-golden decision) |
| both reports pure ASCII | design-record 0, producer-report 0 | MATCH |

The 2 skips are the pre-existing Python-3.12 PEP 695 env skips (unchanged since M0-T127).

## (2) R404 ten-family audit + removal-sensitivity (all families have real, substance-asserting tests)

| # | Family | Test class (count) | Removal-sensitive binding |
|---|---|---|---|
| 1 | live cross-task selection through REAL loop | LiveCrossTaskSelectionTests (2) | `real_run_one` builds a real `SupervisedLoop`+`StateMachine`+journal+`plan_close_run`; asserts `dispatched==["M0-TA","M0-TB"]`, `is_advanced` True over the **real durable CAS**, `advanced==[TA,TB]`, `final_state==COMPLETE`. Revert selection/advancement -> order/is_advanced fail. |
| 2 | each ineligible category skipped w/ audit reason | EligibilitySkipTests (9) | each asserts the exact refusal code (`blocked`,`owner_gated`,`ineligible_status`,`worktree_missing`,`worktree_primary_checkout`,`packet_unparseable`,`task_id_mismatch`) + `cross_task_candidate_skipped` audit row |
| 3 | dependency ordering | DependencyOrderingTests (3) | unaccepted -> `dependency_unaccepted`; accepted -> eligible; missing -> `dependency_unresolved` |
| 4 | isolated-worktree binding refuses (visible) | WorktreeBindingTests (2) | `verdict.code.startswith("binding_")`; driver step outcome `skipped` with `binding_` detail; task not dispatched |
| 5 | completion required before advancement | CompletionRequiredTests (4) | `run_reached_complete` requires COMPLETE state **and** last-cycle COMPLETE decision **and** non-empty checkpoint id; each asserted False when one is missing |
| 6 | duplicate advancement refused | DuplicateAdvancementTests (1) | pre-advance A -> A step `already_advanced`, `dispatched==["M0-TB"]` |
| 7 | crash before/after advancement (genuine reopen) | CrashMatrixTests (2) | `reopen()` = close+reopen same sqlite; after-advancement->`dispatched==["M0-TB"]`, `advanced==["M0-TB"]`, no double-advance; before->nothing advanced, restart advances once |
| 8 | stale campaign state | StalePacketTests (3) | digest mismatch -> `stale_packet`; mid-journey edit refused; CAS-once snapshot survives restart |
| 9 | no eligible work visible | NoEligibleWorkTests (2) | all-ineligible -> `NO_ELIGIBLE_WORK`; empty queue -> `queue_exhausted` |
| 10 | between-task intents stop | BetweenTaskIntentTests (5) | sets real `EMERGENCY_STOP_KEY`/`MANUAL_PAUSE_KEY`/graceful/budget in journal -> `owner_intent_<intent>`/`budget_exhausted`; revert seam read -> next task dispatches (fails) |

The four load-bearing families I was asked to bind (family 1 live-path, family 7 crash-after-advancement, family 6 duplicate, family 10 between-task intent) all use the **real `DurableJournal` + `compare_and_swap_state`** and **genuine `reopen()`** (close all handles + fresh open on the same file) - real process-death simulation, not in-process exceptions. All are removal-sensitive as cited.

## (3) Family-1 honesty + the untested dispatch branch - REQUIRED CORRECTION #1

Family-1 honesty is **TRUE**: `real_run_one` (cross_task.py:207-244) genuinely constructs a real `SupervisedLoop` + `StateMachine` + real journal + `plan_close_run` + real `record_advancement` (inside `run_task_queue`), faking only the runner/reviewer at the standard `run_unit`/`review` seam. It does traverse the real loop and the real advancement CAS.

**However, the actual dispatch branch is untested.** I confirmed by grep: `run_task_queue` is invoked **only** in `test_agent_supervisor_cross_task.py`, always with a test-built `argparse.Namespace` and a test `run_one` - **never through `cli.cmd_start`**. The wiring line is:
```
cli.py:3069  run = (next_task.run_task_queue(args, checkout, journal, audit, _run_loop)
                    if int(getattr(args,"max_tasks",1) or 1) > 1 or getattr(args,"packet_queue",None)
                    else _run_loop(args, checkout, journal, audit))
```
`DefaultShapeTests` covers only: (a) parser defaults (`max_tasks=1`, `packet_queue=None`) via `build_parser`, and (b) the FALSE branch via an **inline copy** of the condition (`test_driver_is_not_entered_for_the_default_start` re-implements the expression rather than invoking `cmd_start`). No test invokes `cmd_start` with `max_tasks>1`/`packet_queue` to prove the TRUE branch routes to `run_task_queue` with the real `_run_loop`. Consequence: a regression in the cli.py:3069 condition or its argument passing would ship undetected - at the exact seam this task exists to create.

Mitigation (why PASS-with-correction, not FAIL): the `run_task_queue(args, checkout, journal, audit, run_one)` signature matches the cli.py:3069 call args (verified); the driver itself is exhaustively tested; the branch is owner-gated (limited-auto + `--owner-enable-bounded-auto`) and unreachable under the certified default shape.

**Required correction #1:** add at least one test that exercises the real `cli.cmd_start` routing (or evaluates the actual cli.py:3069 line, not an inline copy) with `--max-tasks>1`/`--packet-queue` set, asserting it dispatches to `run_task_queue` with `_run_loop` as the injected callback. This closes the integration-seam coverage gap before R406/R407.

## (4) Eligibility category coverage - 11 categories, 11 covered

`evaluate_eligibility` (next_task.py:551) implements 11 fail-closed categories, cheapest-first, first-failure-wins, each returning a distinct code; each is asserted by a test that would fail if the check were deleted:

| Category | Code | Test |
|---|---|---|
| 1 packet readable/JSON/object | `packet_unparseable` (+unreadable/not_object) | test_unparseable_packet_is_skipped |
| 2 id match | `task_id_mismatch` | test_task_id_mismatch_is_skipped |
| 3 status | `ineligible_status` | test_wrong_status / test_accepted_status_is_not_re_run |
| 4a blockers | `blocked` | test_owner_gated_via_blockers |
| 4b owner-gate field | `owner_gated` | test_owner_gate_field |
| 5a dep missing | `dependency_unresolved` | test_missing_dependency_packet |
| 5b dep unaccepted | `dependency_unaccepted` | test_unaccepted_dependency |
| 6a worktree missing | `worktree_missing` | test_missing_worktree |
| 6b primary checkout | `worktree_primary_checkout` | test_primary_checkout_worktree |
| 6c launch-seam binding | `binding_<code>` | test_worktree_not_matching / driver visible-skip |
| 7 staleness | `stale_packet` | test_packet_changed_after_queueing (+driver +snapshot) |

Count: **11 categories, each with a code-asserting test.** (Observation O2 below on category-1 sub-codes.)

## (5) Certified-shape regression
bounded_mode + launch_seam: **160 passed**. Command-doc tooth **12/0** - the two new flags have safe certified defaults and are (correctly) NOT added to `REQUIRED_START_FLAGS`, so the section-11 runbook start command still validates with no runbook/`command_docs.py` change. `DefaultShapeTests` confirms `--max-tasks` default 1 / `--packet-queue` default None keep the single-task shape.

## (6) Tooling
modularity failures 0; ruff clean on all three touched files; both reports pure ASCII; golden blob byte-identical (empty diff). `cli.py` net-zero at limit (2953/2953).

## Non-blocking observations
- **O1 - next_task.py growth:** 276 -> 691 SLOC (888 raw lines). A `review_signal` warning (above WARN 600, below HARD 1000), not a failure. The design acknowledges a focused module would be cleaner but placement in next_task.py was packet-directed and it's outside a new module's allowed_paths. Non-blocking; flag for future decomposition.
- **O2 - category-1 sub-codes:** category 1 (packet readability) has three codes (`packet_unreadable`/`packet_unparseable`/`packet_not_object`) but only `packet_unparseable` is directly asserted; the file-IO-error and valid-JSON-non-dict variants aren't individually tested. The category is covered; the two sub-codes are a minor completeness gap.

**Requested gate result:** **PASS** with required correction #1 (cli.py:3069 dispatch-branch coverage) and observations O1/O2, at material identity `1485c73` (tip `533f43a`). All commands reproduce read-only.

Note for the orchestrator: reviewed via `git checkout --detach 533f43a` in my own isolated worktree (clean tree restored first; my untracked memory index + a local memory edit were set aside and re-applied). The orchestrator owns this worktree's post-review lifecycle.
---VERBATIM-END---
