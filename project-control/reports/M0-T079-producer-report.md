# M0-T079 producer report — bounded unattended mode: durable budgets, wired breakers, live recovery probes, typed refusals

**Task:** M0-T079 (D-023 item 1, amended by D-023-R037)
**Branch / worktree:** `task/M0-T079-bounded-mode` in `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t079`
**Producer:** M0-T079 producer agent. Gates G0/G2/G3/G4/G5 are the reviewers' to run; this report is evidence, not a verdict.
**Platform of record:** Windows 11, Python 3.11.9, `git 2.47.1.windows.2`.

---

## 1. AD-093 qualifying evidence (supervisor-freeze rule §2/§3)

Four qualifying items, each independently sufficient under D-010 Section 0A.10.

### 1.1 A requirement explicitly listed in the owner directive

`project-control/directives/D-023-bounded-autonomy-campaign/requirements.json`:

- **D-023-R011** — "Deliver a genuinely bounded unattended mode capable of a measured 10-hour (36,000-second) run, built on the existing supervisor, Claude workers, Codex reviewers, project-control ledger, worktree isolation, and GitHub workflow."
- **D-023-R037** (owner amendment, `source-002-amendment.md`, verbatim: *"CORRCTOIN DO NOT HARDCODE A MAX LIMIT ON A RUN IT CAN RUN AS LONG AS IT WANTS DO"*) — "Do not hardcode a maximum run-length limit anywhere in the unattended mode: run duration is owner-controlled at launch and a run may run as long as the owner wants, including with no wall-clock limit at all."
- **D-023-R033** — "Do not activate unattended mode until its stated prerequisites and live canaries pass (active owner HOLD)." Honoured: the mode is implemented and **OFF**; see §5.

### 1.2 A reproduced defect — the `limited-auto` traceback refusal

Before this task, `cli.cmd_start` raised a bare `NotImplementedError` for `--mode limited-auto`. An operator saw a Python traceback; an unattended wrapper or OS scheduled task saw an interpreter exit code that said nothing about *why* the controller refused. Reproduced on the pre-change tree by the four tests that pinned it:

- `tools/test_agent_supervisor_loop.py::CliStartTests::test_start_limited_auto_refuses_by_name_before_any_input_check`
- `tools/test_agent_supervisor_phase1.py::CliTests::test_limited_auto_is_refused_by_name`
- `tools/test_agent_supervisor_endurance.py::CliTests::test_limited_auto_refuses_by_name`
- `tools/test_agent_supervisor_broker.py::OperatorCommandTests::test_limited_auto_still_refuses_by_name`

each of which asserted `assertRaises(NotImplementedError)`. All four now assert the **structured** refusal instead (same strength, machine readable).

### 1.3 A reproduced defect — unwired circuit breakers, recorded in the module's own note

`tools/agent_supervisor/circuit_breakers.py` carried, verbatim:

> "Phase 1 scope note: the breakers and their bookkeeping are complete and tested. WIRING them to real resource sampling (CPU/memory readings, spend ceilings) and to the notification surface is Phase 2/3; the gauge API is ready for it."

A grep of the pre-change package confirmed the counter half: only `claude_runs_per_task`, `codex_reviews_per_checkpoint` (loop.py) and `consecutive_hard_denies` (broker.py) had a production event site. `supervisor_cycles_per_task`, `model_calls_per_task`, `model_calls_per_day`, `external_writes_per_task`, `external_writes_per_day`, `restart_attempts`, `consecutive_invalid_outputs`, `consecutive_revision_loops`, and `consecutive_no_progress` were tallies nothing incremented — nine configured, manifest-covered, fail-closed limits that could never fire.

### 1.4 A reproduced defect — synthetic recovery revalidation

`cli.cmd_start` answered six S11.5 step-5 questions with one synthetic boolean and three more with a bare `True` (pre-change `cli.py` ~2846–2862):

```python
missing_inputs = _dispatch_inputs_missing(args)
dispatchable = not missing_inputs
revalidation = {
    "controller_manifest": manifest_ok,
    "journal_integrity": integrity.ok,
    "audit_chain": chain.ok,
    "task_authority": dispatchable,
    "branch": dispatchable,
    "worktree": dispatchable,
    "git_and_remote_state": dispatchable,
    "auth": dispatchable,
    "cli_capability_manifest": dispatchable,
    "pending_requests": True,
    "scheduled_deadlines": True,
    "last_external_effect": True,
}
```

A complete command line therefore **certified** that the branch existed, the worktree was settled, Git and the remote were in a known state, auth was present, the CLI capability manifest was intact, no approval was pending, no deadline was outstanding, and the last external effect was accounted for — none of which it had looked at. Reproduced live: see AS-8 in §6, which drives `start` with every input named against a directory that is not a git repository and has no ledger record; the pre-change code dispatched, the post-change code refuses `unsafe` (exit 11) naming all four missing facts.

---

## 2. What changed — file:line map

### 2.1 New modules

| File | SLOC | Responsibility |
|---|---:|---|
| `tools/agent_supervisor/run_budget.py` | 397 | Durable owner-controlled run budgets; the single clock-injection seam. |
| `tools/agent_supervisor/recovery_probes.py` | 586 | Live S11.5 step-5 probes; fail-closed on missing **or ambiguous** facts. |
| `tools/agent_supervisor/refusals.py` | 218 | The exit-code + structured-JSON refusal contract. |
| `tools/agent_supervisor/loop_breakers.py` | 147 | Which production event ticks which counter; budget stop at a seam. |
| `tools/agent_supervisor/owner_touch.py` | 98 | The S16.7 owner-touch budget (extracted from `loop.py`; re-exported). |
| `tools/agent_supervisor/start_gate.py` | 217 | The `start` pre-dispatch gate: owner mode gate, live probes, refusal mapping. |
| `tools/agent_supervisor/errors.py` | 14 | `LoopError` — the shared error taxonomy the loop's modules raise. |

New test modules: `tools/test_agent_supervisor_bounded_mode.py` (53 tests),
`tools/test_agent_supervisor_recovery_probes.py` (63 tests).

### 2.2 Deliverable 1 — durable owner-controlled run budgets

| Location | What |
|---|---|
| `run_budget.py:66` | `UNLIMITED = None`, with the comment stating why there is **no** companion maximum constant. |
| `run_budget.py:86` | `system_clock()` — the ONE injected seam; nothing else in the module reads a clock. |
| `run_budget.py:98`, `:110` | `utc_day_for` / `utc_iso_for` derive the per-day breakers' UTC day from that same seam. |
| `run_budget.py:122` | `RunBudget` — `wall_clock_seconds: float \| None = None` plus the existing counter limits. |
| `run_budget.py:134` | Validation: non-numeric, bool, NaN, ±inf and `<= 0` are refused; **no upper bound is checked**. |
| `run_budget.py:231` | `RunBudgetLedger` — the durable record, keyed `run_budget/<run_id>`. |
| `run_budget.py:268` | `start()` — persists run identity, the budget as supplied, the run-start epoch/ISO/day, and zeroed counter snapshots; on a resume it **reloads the original** and raises `budget_conflict` if the launch names different bounds. |
| `run_budget.py:337` | `elapsed()` — seconds since the persisted start, clamped to a durable high-water mark. |
| `run_budget.py:358` | `observe()` — advances and persists the mark; counts `backwards_clock_observations`. |
| `run_budget.py:379` | `check()` — the only timer. `wall_clock_seconds is None` ⇒ never exhausted. |
| `run_budget.py:419`, `:441` | `persist_counters` (monotonic) / `restore_counters` (reconcile upward only). |
| `run_budget.py:458` | `finalize()` — the machine-readable exit reason; clears **no** durable hold. |
| `circuit_breakers.py:194` | New `CircuitBreakers.restore(counters, day="")` — takes the max, never lowers, refuses unknown names. |
| `cli.py:2763` | The ledger is built from the immutable `config.limits` plus `--run-wall-clock-seconds`. |
| `cli.py:3294` | `--run-wall-clock-seconds`, `type=float, default=None`, help text spells out "OMIT IT FOR AN UNLIMITED RUN". |
| `loop.py:2663` | `run()` restores tallies and refuses immediately when the resumed budget is already spent. |
| `loop.py:2699` | The budget gate, at the seam **before** a unit is dispatched (S11.2). |
| `loop_breakers.py:153` | `budget_stop()` — observe, check, finalize, audit `run_budget_exhausted`. |

### 2.3 Deliverable 2 — every circuit breaker at its real event site

| Counter | Site | Line |
|---|---|---|
| `supervisor_cycles_per_task` | top of `run_cycle`, before any provider call | `loop.py:1657` |
| `model_calls_per_task` + `_per_day` | the worker dispatch, **before** the call | `loop.py:1699` |
| `model_calls_per_task` + `_per_day` | the reviewer dispatch, **before** the call | `loop.py:1970` |
| `external_writes_per_task` + `_per_day` | the outbound send | `loop.py:2189` |
| `external_writes_per_task` + `_per_day` | the cross-process resume send | `loop.py:2607` |
| `restart_attempts` | each seam relaunch in `run()` | `loop.py:2758` |
| `consecutive_invalid_outputs` | a unit with no valid checkpoint | `loop.py:1757` |
| `consecutive_invalid_outputs` | a reviewer answer that never validated (`schema_retry_exhausted`) | `loop.py:1989` |
| `consecutive_invalid_outputs` | reset on a valid checkpoint | `loop.py:1885` |
| `consecutive_no_progress` | a checkpoint id that repeats the previous cycle's | `loop.py:1892` |
| `consecutive_no_progress` | reset on a new checkpoint id | `loop.py:1905` |
| `consecutive_revision_loops` | a `REVISE` decision, before the revision prompt is forwarded | `loop.py:2108` |
| `consecutive_revision_loops` | reset on any other decision | `loop.py:2115` |
| persistence | tallies written with the budget after every cycle/stop | `loop_breakers.py:115` |
| already wired, **not re-ticked** | `claude_runs_per_task`, `codex_reviews_per_checkpoint` (loop.py), `consecutive_hard_denies` (broker.py:427) | — |

`circuit_breakers.py:26` — the Phase-1 scope note was replaced with a truthful wiring-status note that quotes the old text and says exactly what is now wired and what (spend ceilings) is still out of scope and why.

### 2.4 Deliverable 3 — live recovery probes replacing the synthetic facts

| Probe | Line | Fails closed on |
|---|---|---|
| `probe_task_authority` | `recovery_probes.py:204` | no/unreadable ledger record, id or status mismatch, non-working status, unresolved blockers, packet without a task id |
| `probe_branch` | `:262` | git unavailable, no branch, detached HEAD, mismatch with `--branch` |
| `probe_worktree` | `:287` | missing dir, not a work tree, unfinished merge/rebase/cherry-pick/revert/bisect, unmerged paths |
| `probe_git_and_remote_state` | `:333` | git unavailable, unresolvable/non-SHA HEAD, `status` not answering; remote reachability **only when required**, unprovable ⇒ refuse |
| `probe_auth` | `:393` | an executable missing at the exact named path; an injected auth check that fails or is undetermined |
| `probe_cli_capability_manifest` | `:425` | a recorded FAILED capability probe; provider-CLI identity drift; unidentifiable binary; unreadable record |
| `probe_pending_requests` | `:497` | an unanswered approval request; an unreadable ask queue |
| `probe_scheduled_deadlines` | `:520` | an unparseable deadline (an *outstanding* one passes and is reported — `recover_boot` owns `deadline_restored`) |
| `probe_last_external_effect` | `:550` | an unreadable effect journal (a *pending* effect passes and is reported — `recover_boot` owns `AMBIGUOUS_EFFECT`) |
| `probe_config_identity` | `:578` | config not named, missing, or its manifest binding unverified |
| `probe_surviving_children` | `:605` | a surviving or undetermined recorded child; an unreadable child record |
| `run_live_probes` | `:659` | runs **all** of them so a refusal names every missing fact, not the first |

Wiring: `start_gate.py:121` (`live_revalidation`) builds the map and `cli.py` calls it; `start_gate.py:171` (`unprobed_revalidation`) answers every live step `False` - never `True` - when a required input was absent or the packet did not parse, so the one branch that answers without a probe fails closed. `ProbeResult.passes` (`recovery_probes.py:106`) is the single place the fail-closed rule lives: `ok and known`.

### 2.5 Deliverable 4 — machine-meaningful refusals

| Location | What |
|---|---|
| `refusals.py:63` | The seven outcomes and their stable exit codes: halted 10, unsafe 11, unsupported_platform 12, stale_state 13, approval_required 14, budget_exhausted 15, refused_mode 16. |
| `refusals.py:88` | `exit_code_for` raises on an unknown outcome — never mapped to success. |
| `refusals.py:100` | `Refusal` — `schema_version`, `refused`, `outcome`, `exit_code`, `reason_code`, `message`, `detail`, `at_utc`. |
| `refusals.py:183`, `:220`, `:243` | `outcome_for_recovery` (unknown ⇒ `unsafe`), `outcome_for_loop_refusal`, `outcome_for_unattended_stop`. |
| `start_gate.py:47` | `emit_refusal` — JSON to stdout under `--json`, human lines to stderr otherwise, no traceback. |
| `start_gate.py:59` | `bounded_mode_gate` — replaces the `NotImplementedError`. |
| `start_gate.py:200/218/248` | `recovery_refusal`, `dispatched_run_refusal`, `loop_refusal`. |
| `cli.py:3138` | `cmd_start` returns the typed exit code. |
| `cli.py:1379`, `:1382` | `doctor` reports the mode truthfully and prints the whole contract as data. |

---

## 3. Design decisions

### 3.1 The no-hardcoded-limit budget model (D-023-R037 compliance)

The amendment is a **prohibition**, so compliance had to be structural rather than a default someone could later "tighten".

1. **`None` is the only default.** `RunBudget.wall_clock_seconds` defaults to `None` and `RunBudget.from_limits` defaults to `UNLIMITED`. `--run-wall-clock-seconds` has `default=None`. There is no config key, no environment variable, and no fallback anywhere that supplies a number.
2. **There is no maximum constant to find.** `run_budget.py` defines no `MAX_*RUN*` / `*RUN*_CEILING`-shaped name, and a source-level test (`test_no_hardcoded_maximum_run_length_exists_anywhere`) asserts that with a regex and also asserts the CLI argument's `default is None` and that its help text says UNLIMITED. A future edit that adds a ceiling fails that test.
3. **`check()` short-circuits on unlimited** *before* any comparison: with `wall_clock_seconds is None` there is no arithmetic that could produce an exhaustion, so no timer exists to mis-tune. `test_an_unlimited_loop_run_is_never_stopped_by_the_budget` drives a real loop whose fake clock advances 90 days per unit and asserts it stops on `max_cycles_reached`, not on the budget.
4. **Large budgets are not clamped.** `test_an_enormous_owner_budget_is_accepted_without_clamping` sets 10⁹ seconds (~31 years) and asserts the value round-trips unchanged.
5. **Zero is refused, not read as unlimited.** `0` would be an ambiguous spelling of "no limit"; the error message says so explicitly and directs the owner to omit the flag.

The counter bounds are a separate axis and are **not** owner-supplied at launch: they come from the manifest-covered immutable `config.toml`, exactly as S3.1 requires, and are carried in the budget record only so the durable record states every bound the run is held to.

### 3.2 Unshrinkable elapsed time, and its honest limit

Wall clock, not `time.monotonic()`: a monotonic reading is meaningless across the process restart a crash-resume is made of, and the run-start instant must survive one. The hazard — a wall clock can move backwards — is handled in one place, `elapsed()`, which returns `max(now - started, high_water)` against a durable high-water mark.

The honest limit, stated in the docstring rather than papered over: a backwards clock cannot *shrink* elapsed, but it does *pause* accrual until the clock catches up. Each such observation increments `backwards_clock_observations` in the durable record so an operator can see the anomaly. `test_a_backwards_clock_cannot_shrink_elapsed_and_is_recorded` asserts both halves.

### 3.3 `budget_conflict` rather than "last launch wins"

A relaunch of the **same run id** naming different bounds is a fail-closed `budget_conflict` refusal (mapped to `stale_state`, exit 13) rather than a silent adoption of either value. Silently keeping the old budget would make the operator's new flag a no-op they could not see; silently taking the new one would let a run extend or shrink its own bounds by relaunching. Choosing different bounds is an owner act on a **new run id**, which the owner names.

### 3.4 Where the counters tick, and why `record_progress` had to be narrowed

Every trip is a synchronous pause **before** the counted thing happens, matching the pre-existing `claude_runs_per_task` discipline: a tripped `model_calls_*` never spends the call it would have been the (N+1)th of, and a tripped `external_writes_*` means nothing was sent.

One existing behaviour had to be narrowed for a counter to become meaningful. `CircuitBreakers.record_progress()` clears every `RESET_ON_PROGRESS` counter and was called on every successful forward — including a forward carrying a `REVISE` prompt, which is exactly the step `consecutive_revision_loops` exists to count. `loop_breakers.record_progress` (`loop_breakers.py:128`) therefore clears the unrelated counters on a REVISE and leaves the revision counter alone; a `CONTINUE` behaves exactly as before. This makes a breaker *able to fire*; it weakens nothing.

`consecutive_no_progress` uses the repeated-checkpoint-id signal — the classic unattended livelock, where the worker keeps answering and the work stands still — and takes the S7 table's existing `checkpoint_unsafe` edge out of `CHECKPOINT_RECEIVED` ("the checkpoint itself indicated a S4.5 condition"). **No transition-table edge was added anywhere in this task.**

### 3.5 Which probes fail the step, and which report and defer

Two probes deliberately **pass** their step while carrying evidence: an outstanding usage-limit deadline and a pending external effect. `recover_boot` already has a dedicated, more actionable verdict for each (`deadline_restored`, `AMBIGUOUS_EFFECT` → `RECONCILE_EXTERNAL_EFFECT`), and `UNSAFE_OR_DRIFTED` dominates in `classify`, so failing those steps would have replaced specific, operator-usable guidance with a generic drift message. Only an **unreadable** deadline or effect journal fails the step — "I could not look" is never "there is nothing there". Both behaviours are asserted (`test_no_deadline_passes_and_an_outstanding_one_is_reported_not_masked`, `test_a_pending_effect_is_reported_and_left_to_the_ambiguous_verdict`).

`config_identity` and `surviving_children` are **folded** rather than added to `recovery.REVALIDATION_STEPS`: `config_identity` ANDs into `controller_manifest` (`start_gate.py:160`) and `surviving_children` reports what `recover_boot`'s own child accounting already gates on. The frozen step vocabulary is unchanged; only the *answers* became honest.

### 3.6 Two safety holes closed while making the refusals typed

Making the pre-dispatch verdict machine readable exposed that `cmd_start` gated on `outcome.classification != SAFE_CHECKPOINT`, and `recovery.classify` returns **SAFE_CHECKPOINT** for both `safe_but_forbidden` (a durable emergency stop, manual pause, or open owner gate) and `deadline_restored`. Both therefore passed the gate. `cli.py:3030` now stops on those reason codes with `approval_required` / `stale_state`. `test_a_durable_emergency_stop_is_no_longer_dispatched_over` is the regression proof.

### 3.7 The owner gate, and what it does not lift

`RUNNABLE_MODES` is deliberately unchanged at `("shadow", "supervised")`; the bounded mode lives in a separate `OWNER_GATED_MODES` and `LoopConfig` refuses it unless `owner_enabled_bounded_auto=True`, which only `--owner-enable-bounded-auto` sets. A stray enable flag on a *non*-gated mode is refused rather than ignored, so it cannot sit unnoticed in a scheduled task's argv. `config.py` has no such field and a test asserts the string does not appear in it.

An owner-enabled bounded run still passes every existing gate unchanged: the live pre-dispatch probes, the `job_object` containment precondition, the four-tier policy, HARD-DENY / HALT_UNSAFE / STOP_FOR_OWNER / ASK, and every circuit breaker. The only behavioural difference is that an **AUTO-tier** forward is not parked for a human who is not there — it takes the S7 table's own `tier_auto` edge. The send itself is the *same* `_send_forward` code both modes run (`loop.py:2274`), so an unattended run cannot reach the outbox by a route a supervised run does not also take.

**This does not lift R595.** The supervisor-freeze rule §4 is intact: nothing here creates an approval path, and activating the mode on a live host remains a separate explicit owner act.

### 3.8 Modularity

`loop.py` and `cli.py` are grandfathered oversized files; `tools/modularity_check.py --check` failed on both after the first implementation pass (`cli.py` 3085 vs limit 2953; `loop.py` 2212 vs limit 2088). Rather than request an owner exception, the growth was **extracted** into the focused modules listed in §2.1 and duplication was removed (one shared `breaker_stop` closure for the six trip sites; one shared `_send_forward` for both forwarding modes). Final: `cli.py` 2932 (limit 2953), `loop.py` 2047 (limit 2088), `python tools/modularity_check.py --check` → **`failures 0`**, warnings all pre-existing.

Note for the reviewer: `modularity_check` selects files via `git ls-files`, so the seven **untracked** new modules are not yet in its census. Each was measured directly and is well under the 1,000 hard threshold; the largest, `recovery_probes.py` at 586, is under the 600 warn line.

---

## 4. Acceptance scenarios

Per `docs/ACCEPTANCE_SCENARIO_STANDARD.md`. Execution method for all: `python -m pytest <module> -q` on Windows, Python 3.11.9. No provider, no network, no real repository except AS-8/AS-9, which build a throwaway `git init` checkout in a temp directory. Cleanup for all: `tempfile.TemporaryDirectory` via `addCleanup`; no state outside the temp directory is written.

| ID | Requirement | Preconditions | Exact input | Expected output | Invariant | Evidence |
|---|---|---|---|---|---|---|
| **AS-1** *(primary success)* | D-023-R037 | Fake clock; no owner wall clock | `RunBudget.from_limits(Limits())`; clock advances 1 s → 10 years | `check().exhausted is False` at every step; `remaining_seconds is None` | An unlimited run is never stopped by a timer | `test_agent_supervisor_bounded_mode.py::UnlimitedRunTests::test_an_unlimited_run_is_never_exhausted_however_long_it_runs` |
| **AS-2** *(primary success, end to end)* | D-023-R037 | Real loop, fake runner advancing 90 days/unit, `max_cycles=3` | `loop.run("first unit")` | `stopped == "max_cycles_reached"`; `run_budget["unlimited"] is True`; elapsed > 86 400 s | No timer exists to stop an unlimited run | `…::UnlimitedRunTests::test_an_unlimited_loop_run_is_never_stopped_by_the_budget` |
| **AS-3** *(boundary)* | D-023-R011 | Budget 100 s | clock → 99.999 s, then → 100.000 s | not exhausted, then exhausted, `dimension == "wall_clock"`; a repeated `check()` returns an identical dict | Exhaustion is exact and deterministic | `…::BudgetExhaustionTests::test_exhaustion_is_exact_and_repeatable` |
| **AS-4** *(boundary, end to end)* | D-023-R011 | Budget 100 s; each unit costs 40 s | `loop.run(...)`, `max_cycles=10` | `stopped == "budget_exhausted"`; exactly 3 units ran; durable `exit_reason == "budget_exhausted"` and `stopped_at_utc` set | The stop is at a seam — never mid-unit (S11.2) | `…::BudgetExhaustionTests::test_a_budgeted_loop_run_stops_between_cycles_with_an_exit_reason` |
| **AS-5** *(retry / idempotency)* | D-023-R011 | A run 60 s in, ledger reopened over the same journal 3× | `RunBudgetLedger(...).start()` | Same `started_at_epoch`; elapsed never below 90 s; exhausts on schedule | Elapsed can never reset across a crash-resume | `…::CrashResumeBudgetTests::test_a_resume_cannot_reset_elapsed_time` |
| **AS-6** *(ambiguous / conflicting input)* | D-023-R011 | A run started with 100 s | relaunch with 1 000 000 s, 1 s, and `None` | `BudgetError("budget_conflict")` in all three | A run can never extend, shrink, or reset its own bounds | `…::CrashResumeBudgetTests::test_a_relaunch_naming_a_different_budget_is_refused` |
| **AS-7** *(regression, end to end)* | D-023-R011 | A first loop run spends 2 model calls; a fresh `CircuitBreakers` is built | resume + `restore_counters` | The resumed breakers read 2, not 0 | A crash never returns a spent allowance | `…::CrashResumeBudgetTests::test_a_resumed_loop_re_enters_with_the_tallies_it_left` |
| **AS-8** *(missing input, the §1.4 defect)* | D-007 S11.5 | Temp dir that is **not** a git repo, no ledger record | `start` with **every** input named | `missing_inputs == []`, `dispatched False`, `provider_calls_made 0`, exit **11**, `probes.failed ⊇ {task_authority, branch, worktree, git_and_remote_state}` | A complete command line no longer certifies a live fact | `test_agent_supervisor_recovery_probes.py::StartProbeIntegrationTests::test_a_complete_command_line_no_longer_certifies_the_live_facts` |
| **AS-9** *(positive control)* | D-007 S11.5 | Real `git init` checkout + ledger record; `job_object` containment | same `start` | `probes.failed == []` and the run **dispatches** | The probes are not simply always-fail | `…::StartProbeIntegrationTests::test_a_real_checkout_with_a_ledger_record_passes_the_probes` |
| **AS-10** *(dependency failure)* | D-007 S11.5 | Git that cannot be executed at all | `run_live_probes` | branch / worktree / git_and_remote_state all `known=False`, all fail; every other probe still ran | "I could not tell" is a failure, and one failure never hides another | `…::SuiteTests::test_every_probe_runs_even_after_an_earlier_one_fails` |
| **AS-11** *(each fact, individually)* | D-007 S11.5 | A healthy probe baseline | flip each of the 9 live steps to `False` in turn | every single one ⇒ `UNSAFE_OR_DRIFTED`, step in `failed_steps`, outcome `unsafe` | One missing fact is enough; they need not accumulate | `…::SuiteTests::test_each_missing_fact_on_its_own_makes_the_recovery_verdict_unsafe` |
| **AS-12** *(security / hold isolation)* | D-023-R033 | Real checkout, durable emergency stop set | `start` with every input | `dispatched False`, `provider_calls_made 0`, exit **14**, `reason_code == "safe_but_forbidden"` | A durable hold is never dispatched over (see §3.6) | `…::StartProbeIntegrationTests::test_a_durable_emergency_stop_is_no_longer_dispatched_over` |
| **AS-13** *(security / approval)* | D-007 S11.5 | An unanswered `QueuedAsk` in the journal | `start` | `dispatched False`, exit 11, `pending_requests` in `probes.failed` | A run never starts past a question the owner has not answered | `…::StartProbeIntegrationTests::test_a_pending_approval_request_stops_the_next_start` |
| **AS-14** *(provider CLI drift)* | AD-093 drift category | An executable identity pinned on a first start | the pinned digest is altered | `provider_cli_drift`, fails closed | A CLI that changed under an unattended controller is drift, not a detail | `…::CapabilityProbeTests::test_a_changed_provider_cli_is_detected_as_drift` |
| **AS-15** *(regression, the §1.2 defect)* | D-023-R033 | Any checkout | `start --mode limited-auto` | exit **16**, JSON `outcome=refused_mode`, `reason_code=limited_auto_not_enabled`, **no traceback** | The refusal is unchanged in strength and now machine readable | `test_agent_supervisor_bounded_mode.py::CliBoundedModeTests::test_limited_auto_without_the_enable_is_a_structured_refusal` |
| **AS-16** *(null / stray input)* | D-023-R033 | Any checkout | `start --mode shadow --owner-enable-bounded-auto` | exit 16, `owner_enable_without_gated_mode` | A stray enable never sits unnoticed in a scheduled task's argv | `test_agent_supervisor_loop.py::CliStartTests::test_start_refuses_the_bounded_enable_on_a_non_gated_mode` |
| **AS-17** *(primary success, the mode itself)* | D-023-R011 | Owner-enabled bounded loop, approval gate returning **False** | `loop.run("first unit")` | 1 forward; path contains `FORWARD_PROMPT`, **not** `WAIT_FOR_OWNER`; journal records the `tier_auto` trigger | The mode is implemented, not a stub — and takes an existing S7 edge | `…::OwnerGateTests::test_an_owner_enabled_bounded_run_forwards_without_an_approval` |
| **AS-18** *(security, unattended ≤ supervised)* | D-023-R011 | Owner-enabled bounded loop; reviewer returns `HALT_UNSAFE` | `loop.run(...)` | `stopped == "halt_unsafe"`, final state `HALTED`, nothing forwarded | An unattended run may do LESS than a supervised one, never more | `…::OwnerGateTests::test_a_bounded_run_still_stops_for_every_non_auto_outcome` |
| **AS-19** *(the §1.3 defect, per counter)* | D-023-R011 | Tuned `Limits`, real loop, fake runner | one test per counter | each counter reaches its bound from its own event site and the trip stops the run | Nine previously-unfed counters now fire | `…::BreakerWiringTests` (11 tests) |
| **AS-20** *(regression guard)* | D-023-R011 | — | scan `loop.py` + `broker.py` | **every** name in `COUNTER_LIMITS` is referenced by a production wiring site | A new counter cannot be added without wiring it | `…::BreakerWiringTests::test_every_counter_in_the_registry_has_a_wired_event_site` |
| **AS-21** *(safe cleanup)* | D-023-R011 | Manual pause + a future resume deadline set; budget exhausted | `finalize(...)` | both durable values unchanged; emergency stop still false | Exhaustion releases no safety flag | `…::BudgetExhaustionTests::test_exhaustion_clears_no_durable_flag_hold_or_approval` |
| **AS-22** *(contract)* | D-023-R011 | — | `refusals` module | 7 outcomes, distinct exit codes, all > 1; unknown outcome **raises** | An unrecognized refusal is never reported as success | `…::RefusalContractTests` (8 tests) |

---

## 5. Owner-hold compliance (D-023-R033 / R595)

- `RUNNABLE_MODES` still excludes the bounded mode (`loop.py:134`), asserted by the pre-existing `test_no_module_constant_can_switch_limited_auto_on` and by a new test.
- `LoopConfig(mode="limited-auto")` with no owner enable still raises `LimitedAutoRefused` with code `limited_auto_refused` and the message phrase "separate explicit owner activation" — the pre-existing assertion is unchanged and still green.
- The enable is a **launch input only**: `config.py` has no such field and a source scan asserts the string is absent from it.
- `doctor`'s `loop_modes` check now additionally proves the enable cannot be attached to a non-gated mode (`cli.py:1134`).
- Nothing in this change sets the durable `limited_auto_enabled` journal flag, and no new or expedited approval path was created.

---

## 6. Test-run output

### 6.1 Baseline, before any change (this worktree)

```
$ python -m pytest tools/ -k agent_supervisor -q
1590 passed, 2 skipped, 555 deselected in 97.67s
```

### 6.2 After the change

```
$ python -m pytest tools/ -k agent_supervisor -q
1707 passed, 2 skipped, 555 deselected in 139.33s
```

```
$ python -m unittest tools.test_agent_supervisor_<all 41 modules>
Ran 1709 tests in 135.584s
OK (skipped=2)
```

**Exact counts: 1707 passed / 0 failed / 2 skipped (pytest); 1709 run / 0 failures / 2 skipped (unittest).** Both exceed the `M0-T039-supervisor-freeze.md` floor of ≥ 1165 tests with 0 failures. Delta from baseline: **+117 tests, 0 regressions.** The two skips are the pre-existing platform-conditional skips and are unchanged.

New modules: `test_agent_supervisor_bounded_mode.py` 53 passed, `test_agent_supervisor_recovery_probes.py` 63 passed.

### 6.3 Modularity

```
$ python tools/modularity_check.py --check
selected 265 files; failures 0; warnings 5
```
All five warnings are pre-existing (`symbol_ceiling` on two files outside this task, `symbol_ceiling` on `cli.py`/`policy.py`, `review_signal` on `tools/context_benchmark.py`).

### 6.4 Live CLI smoke (Windows, no provider contacted)

```
$ python -m tools.agent_supervisor start --mode limited-auto --checkout <tmp> --runtime-base <tmp> --json
{ "schema_version": "1.0.0", "refused": true, "outcome": "refused_mode",
  "exit_code": 16, "reason_code": "limited_auto_not_enabled", ... }
exit=16

$ python -m tools.agent_supervisor start --mode limited-auto --checkout <tmp> --runtime-base <tmp>
REFUSED (refused_mode, exit 16): limited_auto_not_enabled      # on stderr, no traceback

$ python -m tools.agent_supervisor doctor --checkout <tmp> --runtime-base <tmp>
overall: PASS
limited-auto: IMPLEMENTED and OFF by default; enabling it is an explicit per-launch owner act.
refusal exit codes: halted=10, unsafe=11, unsupported_platform=12, stale_state=13,
                    approval_required=14, budget_exhausted=15, refused_mode=16
```

**Evidence label (D-023-R021):** everything above is unit / fake-runner / in-process-CLI proof. **No live end-to-end run against a real Claude or Codex provider was performed**, and no claim of 10-hour readiness is made — that is a measured-canary question the activation path owns.

---

## 7. Existing tests amended, and why each is a strengthening

The supervisor-freeze rule forbids weakening any existing check. Nine existing tests were amended; each is listed with the reason.

1–4. **The four `limited-auto` traceback tests** (`loop`, `phase1`, `endurance`, `broker`) — `assertRaises(NotImplementedError)` → assert the structured refusal: nonzero exit `16`, the documented outcome, the same message phrases ("limited-auto is DISABLED", "explicit owner activation"), and `assertNotIn("Traceback", ...)`. Strictly stronger: they now also pin the exit code and the absence of a traceback.

5. **`test_a_loop_refusal_is_a_report_not_a_traceback`** and 6. **`test_run2_scenario_clear_recovery_then_start_works`** (`loop`) — `assertEqual(code, 0)` → `assertEqual(code, EXIT_CODES[STALE_STATE])` plus an assertion on the refusal outcome. The refusal was already reported in the payload; a wrapper could not previously tell it from success.

7. **`test_a_posix_process_group_host_refuses_to_dispatch`** (`start_reentry`) — same change for the containment refusal (`unsupported_platform`, exit 12). Every existing assertion about `dispatched`, `provider_calls_made`, `containment`, and the audit event is retained.

8. **`test_doctor_human_output_is_readable`** and 9. **`test_doctor_reports_every_phase1_check`** (`phase1`) — the doctor text changed from "NOT IMPLEMENTED and disabled" to "IMPLEMENTED and OFF by default", because after this task the former would be **false**. The tests additionally assert the refusal contract is present in the report.

10. **`test_the_budget_module_cannot_widen_policy`** (`loop`) — extended to scan **both** `loop.py` and `owner_touch.py`, plus an assertion that `class OwnerTouchLedger` really is in `owner_touch.py` so the scan cannot be vacuous. Without this, moving the ledger would have quietly narrowed the guarantee.

**Four test fixtures** (`start_reentry`, `loop`, `manifest_binding`, `model_chain`) now build a real `git init` checkout with a `project-control/tasks/<id>.json` ledger record, because a fixture that DISPATCHES must be a checkout the live probes can read. This makes the C1/C2 containment evidence *more* realistic, not less.

---

## 8. Risks and judgment calls

1. **Live probes make `start` stricter, and that is the point.** Any operator or fixture that ran `start` against a non-git directory, a checkout without a ledger record for its task, or one with an unfinished merge now gets a typed refusal. This is the defect being fixed, but it is a behaviour change reviewers should confirm matches how the controller is actually launched in production. Mitigation: AS-9 is a positive control proving a real checkout dispatches.
2. **Exit codes changed on four previously-exit-0 refusal paths.** Any script that treated `start`'s exit code as "0 means it ran" will now see 11/12/13/14/16. That is the intended correction; it is called out here because it is the most likely integration surprise.
3. **`consecutive_no_progress` uses the repeated-checkpoint-id signal.** A worker that legitimately re-reports the same checkpoint id across cycles would trip it at the configured bound (default 3). I judged a repeated id to be the honest livelock signal, but a reviewer may prefer `current_sha` or a compound key; the site is one place (`loop.py:1892`).
4. **`record_progress` narrowed on a REVISE forward** (§3.4). It is what makes `consecutive_revision_loops` able to fire at all, but it *is* a change to a previously-frozen behaviour and deserves an explicit reviewer look.
5. **`recovery_probes.py` is 586 SLOC**, close to the 600 warn line. It is one responsibility (the probes) and each probe is independent; a future addition should probably split it by fact family rather than grow it.
6. **The new modules are untracked**, so `modularity_check` has not yet censused them (§3.8). They will be covered the moment the orchestrator commits them; measured counts are in §2.1.
7. **`auth` proves presence, not credentials.** The probe verifies the named executables exist at their exact paths and says so in its own detail text (`live_credential_check: false`). A real token round trip is an injected `auth_check` seam that nothing currently supplies. I chose not to invent one rather than to claim more than was proven.
8. **`remote_approvals.py:308` now carries a stale note** ("limited-auto is not implemented in this build"). That file is outside this task's scope, so it was left alone — flagged in §9 for whichever task owns it.

---

## 9. Deliberately NOT done — later tasks own these

- **`github_flow.py`** — untouched. The `external_writes_*` counters are wired at the loop's own external write (the outbound send). Modeled effects that go through `ExternalEffectJournal` live in `github_flow.py`, and wiring them belongs to the GitHub-continuation task.
- **`rotation.py`, `worker_turnover.py`, `turnover_controller.py`, `model_turnover.py`, `turnover_adapters.py`** — untouched. `restart_attempts` is ticked at the seam **in `loop.py`**, the single point every relaunch shape passes through, so no turnover module needed editing.
- **Model selection / the model chain** — untouched.
- **`remote_approvals.py`** — untouched, including the now-stale note at line 308. Its factual claim ("cannot be enabled by any code path") is still true; the "not implemented" half is not, and the owning task should correct the wording.
- **Live activation of the bounded mode** — not attempted. R595 / D-023-R033 remain in force; this task implemented the machinery and left it off.
- **A measured 10-hour canary run** — not attempted, and no readiness claim is made (D-023-R023).
- **Spend ceilings** — no priced-usage signal exists on this build to sample; recorded as out of scope in the corrected `circuit_breakers.py` note rather than silently dropped.
- **`recovery.REVALIDATION_STEPS`** — not widened (§3.5).
- **The S7 transition table** — no edge added or altered anywhere in this task.
- **Windows Job Object containment** — untouched; the `job_object` precondition still gates every dispatch and now returns a typed `unsupported_platform` refusal instead of exit 0.

---

# CORRECTIONS APPLIED — consolidated round C1–C12

Round 2, applied against `M0-T079-consolidated-correction.md` (issued after G3
PASS-with-corrections, G4 PASS-with-correction, **G5 FAIL / 2 must-fix** at frozen
identity `c52613f` / task commit `e830c4b`). Every item C1–C12 is applied; nothing
is deferred except the two the correction set itself defers. Each entry names the
fix site and the test that would fail if the fix were reverted.

## Must-fix

### C1 (G5 M1) — budget self-reset via a missing or malformed record

**The defect.** `start()` took the resume branch only on `isinstance(existing,
Mapping) and existing.get("started_at_epoch") is not None`. Three distinct
corruptions — record deleted, record not a Mapping, record intact with
`started_at_epoch: null` — all fell through to the fresh-start path, which minted a
new start instant, zeroed `elapsed_high_water_seconds`, emptied `counters`, and
never reached the `budget_conflict` check. The supervised worker runs as the same
OS user on the same host and can write the journal, so one field edit bought an
unlimited run with fresh allowances — defeating `persist_counters`'s `max()`,
`restore`'s `max()`, and the elapsed clamp at once, because the record they all
defend was simply replaced.

**The fix.** `start()` (`run_budget.py:341`) now branches on ABSENCE, using a
module-level `_ABSENT` sentinel (`run_budget.py:56`) rather than `None` — a row
holding JSON `null` reads back as `None`, so `None` cannot distinguish "no row"
from "row present but empty", and that distinction is the whole finding. No row at
all → `_first_launch()` (`:433`). A row that exists → `_resume()` (`:374`), which
REFUSES five shapes with typed, audited errors and never falls through:

| shape | reason code |
|---|---|
| payload is not a record | `budget_record_unreadable` |
| `started_at_epoch` absent / null / non-numeric / ≤ 0 / NaN / bool | `budget_record_malformed` |
| budget block unreadable | `budget_record_malformed` |
| budget block no longer matches its own recorded digest | `budget_record_tampered` |
| well-formed, but this launch names different bounds | `budget_conflict` |

The digest self-check is new and closes the obvious follow-on: rewriting the
`budget` block under the record would otherwise have been accepted as "the
persisted budget" by the conflict comparison.

**Tests** (`test_agent_supervisor_bounded_mode.py::BudgetSelfResetTests`, 10):
`test_control_an_honest_relaunch_with_new_bounds_is_refused` (the control case),
`test_a_nulled_start_instant_refuses_instead_of_minting_a_fresh_budget` (the exact
proven attack — and asserts the untouched record still reads 3600 s / ≥3000 s
elapsed / 40 tallies afterwards),
`test_a_deleted_record_refuses_rather_than_starting_over`,
`test_a_non_record_payload_refuses` (5 payload shapes),
`test_a_non_numeric_or_impossible_start_instant_refuses` (6 values),
`test_a_rewritten_budget_block_is_caught_by_its_own_recorded_digest`,
`test_an_unreadable_budget_block_refuses`,
`test_an_absent_record_is_still_a_legitimate_first_launch` (the one shape that may),
plus the two audit tests under C6.

### C2 (G5 M2) — credential leak through probe evidence

**The defect.** `probe_git_and_remote_state` records the raw `git remote get-url`
result in both `evidence` and `detail`; `cmd_start` attaches the whole probe report
to the payload; `_emit` printed it with a bare `json.dumps`. A routine
`https://x-access-token:ghp_...@github.com/...` remote therefore put a live PAT on
stdout of every `start --json` — into a scheduled task's captured log. The
mitigation existed, is declared mandatory by `redaction.py`'s header, and is
honoured by `audit_log.append`, `evidence.py`, and `ephemeral_review.py`.

**The fix.** Redaction at the transmission boundary, so it covers this payload and
every future one rather than one probe's fields: `_emit` (`cli.py:1755`) routes
both the JSON and the human shape through `redact_structure`, and `refusals.emit`
(`refusals.py:147`) does the same for the refusal document on either channel. Same
call, same pattern set as the audit log.

**Tests**: `RedactedOutputTests` (4) covers JSON, human lines, refusals on both
channels, and a non-destructiveness control (an ordinary payload round-trips
byte-identical). End to end through the real CLI with a real `git remote add`:
`test_agent_supervisor_recovery_probes.py::StartProbeIntegrationTests::test_a_credential_bearing_remote_never_reaches_stdout`
asserts the probe evidence IS present (so the test cannot pass vacuously) and the
token is NOT, with a `REDACTED` marker.

## Important

### C3 (G5 I1) — synthesized-argv enable replay

`OWNER_ACTIVATION_ARGUMENTS` (`process.py:98`), enforced in `assert_argv_safe`
(`:189`) beside the pre-existing bypass and effort deny sets, with the `=`-form
covered the same way. `turnover_adapters.py` untouched, as instructed — the shared
checker covers that path. The docstring states the scope plainly: this denies the
flag in argv the SUPERVISOR builds, and cannot (and should not) police what an
operator types. **Tests**: `ArgvReplayTests` (2), including a regression assertion
that the pre-existing deny sets and an ordinary argv are unchanged.

### C4 (G5 I2) — per-day tally decay

`_exhausted_counters` (`run_budget.py:558`) skips per-day counters when
`stale_day()` (`:553`) says the persisted window is not today's; `persist_counters`
(`:580`) replaces rather than `max()`es a per-day tally when the day rolls;
`restore_counters` (`:610`) does not restore a stale per-day tally into a fresh
breaker. Per-RUN counters stay monotonic throughout — they bound the run, not the
day. **Tests** (5):
`test_an_exhausted_per_day_counter_stops_exhausting_when_the_day_rolls` (day 1 hits
the 2000 cap → exhausted; +24 h → not exhausted),
`test_a_per_day_tally_from_an_earlier_day_is_not_restored`,
`test_a_same_day_resume_restores_the_per_day_tally`,
`test_a_rolled_day_replaces_the_persisted_per_day_peak`,
`test_a_per_run_tally_is_never_rolled_by_a_new_day`.

### C5 (G5 I3+I4) — typed refusals for corrupt persisted state

`_isolated` (`recovery_probes.py:612`) wraps each of the eleven probes so a raise
becomes that probe's UNDETERMINED result instead of killing the other ten and
escaping as a traceback; `run_live_probes` (`:631`) builds the report through it.
`RunBudget.from_dict` (`run_budget.py:207`) raises `BudgetError` on a corrupt wall
clock and on corrupt counter limits instead of a bare `float()` ValueError;
`restore_counters` validates tally names on READ (it already did on write) and
converts any `BreakerError` into a typed `unrestorable_counters` refusal;
`cmd_start` catches `(BudgetError, BreakerError)` and maps every code to a
structured refusal. **Tests**: `test_a_raising_probe_does_not_kill_the_other_ten`
(all eleven still answer; the journal-backed five are undetermined, the rest pass),
`test_a_probe_that_raises_is_undetermined_not_passed`, and
`CorruptStateTypedRefusalTests` (3) for the wall clock, the counter limits, and an
unknown tally name.

### C6 (G5 I5) — audit the tamper / breaker / refused events

Three events, following the `containment_gate_refused` precedent:

- `run_budget_started` / `run_budget_resumed` / `run_budget_refused`
  (`run_budget.py:319` `_audit`, `:336` `_refuse`) — `budget_conflict` and all four
  corruption codes are sealed. The ledger takes `audit`; `cli.py:2768` wires it.
- `circuit_breaker_tripped` (`loop.py:1642`) — names the counter and its value.
  This is what covers trips taken with `trigger=""`: the cycle counter and the
  pre-dispatch model-call counter stop at their legal entry state WITHOUT
  transitioning, so they reached the chain only through a transition detail that in
  those cases does not exist.
- `bounded_mode_launch_refused` (`start_gate.py:355`, called at `cli.py:2888`) —
  opens the audit log ALONE (no lock, no journal, no dispatch) so an attempted
  activation under the R033 hold leaves a trace.

All three appends are best-effort: a damaged chain refuses new appends by design,
and that refusal must not convert a clean refusal into a traceback. **Tests**:
`test_every_refusal_and_launch_is_sealed_in_the_audit_chain`,
`test_a_resume_is_sealed_too`,
`test_a_refused_bounded_launch_is_sealed_in_the_audit_chain`.

### C7 (G5 I6 / G4 F1) — missing-input refusal exited 0

Chose the typed refusal, as the correction set preferred. `missing_input_refusal`
(`start_gate.py:206`) returns `stale_state` / exit 13 with reason code
`missing_required_inputs` — `stale_state`'s documented meaning is already "a
required fact is missing or ambiguous". `doctor` additionally documents the
carve-outs it never named: `refusals.reserved_exit_codes()` (`refusals.py:257`)
declares `ok=0` and `legacy_halt=1` (the pre-existing `verify-controller` /
M0-T072 manifest security halt), and both appear in the printed contract and in the
JSON `reserved_exit_codes` field. **Amended pinned tests**:
`test_start_without_the_required_inputs_does_not_dispatch` (loop) and endurance's
`test_start_never_dispatches` / `test_start_releases_the_lock_it_took` now assert
exit 13 and the refusal reason code while retaining every prior assertion.
**Genuine dispatch still exits 0**:
`test_an_expired_deadline_no_longer_refuses_dispatch` asserts `dispatched` and
`code == 0` together.

### C8 (G3 I1) — probe read a never-maintained ledger field

`open_blockers_for` (`probe_control_plane.py:99`) reads
`project-control/blockers/B-*.json`, filters `status in ("open", "")`, and matches
the task id with the SAME word-bounded regex `_blocker_references` uses
(`project_control.py:1176`), across both `affects` and `detail`, base-id-matches-rework
included. `probe_task_authority` (`:32`) consults it, and an unreadable blocker set
is UNDETERMINED (`blockers_unreadable`), never "nothing is blocking". **Tests** (8):
`test_a_task_record_blockers_list_is_not_authority` (the M0-T019 / B-017 shape — a
resolved blocker no longer refuses forever),
`test_an_open_blocker_record_naming_the_task_refuses`,
`test_an_open_blocker_naming_the_task_only_in_its_detail_refuses`,
`test_a_blocker_with_no_status_counts_as_open`,
`test_an_open_blocker_naming_a_DIFFERENT_task_does_not_refuse`,
`test_a_rework_id_still_matches_its_base_task`,
`test_an_unreadable_blocker_record_fails_closed`,
`test_no_blockers_directory_at_all_is_not_a_refusal`.

### C9 (G3 I2 / G5 I7) — `deadline_restored` refused on expired deadlines

`deadline_blocks_dispatch` (`start_gate.py:224`) gates on the `outstanding` fact
`probe_scheduled_deadlines` already computes, and steps aside ONLY when the
deadline is the sole thing blocking — a durable emergency stop, manual pause, or
open owner gate still refuses whatever the deadline says. An undetermined deadline
keeps the refusal. `parse_utc_instant` (`recovery_probes.py:474`) replaces the
lexicographic ISO comparison with real instant parsing (`Z`, any offset form, naive
treated as UTC).

One follow-through the correction did not name but truthfulness required:
`honest_reason_code` (`start_gate.py:259`) re-labels the refusal
`safe_but_forbidden` when an expired deadline is present but a FLAG is what
actually blocks — otherwise the operator was told the deadline stopped a run it did
not stop. **Tests** (7): expired dispatches (exit 0), outstanding refuses (exit 13,
`deadline_restored`), unparseable refuses, an expired deadline does not excuse a
manual pause (exit 14, `safe_but_forbidden`), plus
`test_the_deadline_parser_reads_instants_not_strings` and
`test_an_offset_form_deadline_is_compared_as_an_instant`, which asserts its own
premise — the two strings sort the wrong way round, so the case genuinely
discriminates.

## Load-bearing minors

### C10 (G3 I3) — provider-CLI drift latch

`--repin-cli-identity` (`cli.py:3285`) → `probe_cli_capability_manifest(repin=...)`
(`recovery_probes.py:305`). Detection is untouched and still refuses by default;
the flag accepts the new identity, records provenance (`replaced_digest`,
`replaced_path`, `repinned_at_utc`, `repinned_by`) and seals `cli_identity_repinned`.
The refusal message now names the remedy. **Test**:
`test_a_drifted_cli_can_be_repinned_by_an_explicit_owner_act` walks all four states
— pin, drift refuses (exit 11), re-pin passes with provenance and an audit event,
next ordinary start passes against the new pin.

### C11 (G3 I4) — permanent budget-exhaustion trap

The `budget_exhausted` message names `--run-id <fresh-id>` as the way to start a
fresh run and says the exhausted record stays as evidence (`run_budget.py:518`);
`--run-id` gained help text explaining that it IS the budget's identity and
therefore the escape hatch; and the stale `circuit_breakers.py:55` comment ("a
fresh `CircuitBreakers` is built per `start`, and the counter never resets") is
corrected — it described the defect, not the design, and C1/C4 make it untrue in
two directions. On the open question ("consider whether a deliberately-new run
should require an explicit new id"): it already does, and that is now stated rather
than implied. I did not add a `--new-run` alias; a second way to spell `--run-id`
would be a second thing to keep honest.

### C12 — hygiene

`DurableJournal` is imported in `start_gate.py` so `get_type_hints` resolves; the
R037 source scan now covers `run_budget.py`, `loop.py`, `cli.py`, and
`loop_breakers.py`, and its pattern catches `_MAX_RUN_SECONDS`, `ABSOLUTE_RUN_CAP`,
`HARD_STOP_SECONDS`, `DEFAULT_WALL_CLOCK_SECONDS` and five more — with
`test_the_ceiling_scan_actually_catches_a_ceiling` so the guard is not itself
unverified, plus a false-positive control; `_REVISE_SAFE_RESETS`
(`loop_breakers.py:53`) is DERIVED from `RESET_ON_PROGRESS` rather than hand-listed,
so a counter added later cannot silently drift out of it
(`RevisionResetDerivationTests`); `README.md:8` and `:269` no longer say
limited-auto is "not implemented at all, in any form".
`remote_approvals.py:308` left alone — M0-T080 owns it.

## Modularity

The correction round pushed `cli.py` and `recovery_probes.py` past their limits
again. Extracted rather than exempted, as in round 1:

- `probe_result.py` (69) — the `ProbeResult` / `ProbeReport` vocabulary and the one
  place the `ok and known` rule lives, so the three probe families can be split
  without any of them re-deciding it.
- `probe_control_plane.py` (127) — task authority + blockers. C8 made the seam
  obvious: the other probes read the REPOSITORY or the JOURNAL; these read the
  control plane, a third source with its own authority semantics.
- `start_gate.py` absorbed `dispatch_inputs_missing` and `seal_owner_gate_refusal`.

`recovery_probes.py` re-exports every moved name, so no caller or test changed.
Final: `cli.py` 2953 (limit 2953), `loop.py` 2056 (limit 2088),
`recovery_probes.py` 581 (back under the 600 warn line it had crossed at 723).
`python tools/modularity_check.py --check` → **failures 0, warnings 5**, the same
five pre-existing ones.

One judgment call worth flagging: I briefly moved `production_task_authority` out of
`cli.py` for headroom, and
`test_agent_supervisor_command_authority.py::test_the_production_path_loads_commands_through_the_validator`
caught it — that test AST-parses `cli.py` for exactly that function, pinning the
M0-T070 guarantee to that file. I reverted the move rather than amend the test; the
headroom came from my own docstrings instead.

## Test counts

| run | before this round | after |
|---|---|---|
| `pytest tools/ -k agent_supervisor -q` | 1707 passed / 0 failed / 2 skipped | **1752 passed / 0 failed / 2 skipped** |
| the two new modules alone | 116 | **161** |

+45 tests, 0 regressions. Six existing tests were amended this round
(`test_start_without_the_required_inputs_does_not_dispatch`,
`test_start_never_dispatches`, `test_start_releases_the_lock_it_took`,
`test_doctor_human_output_is_readable`,
`test_restore_reconciles_a_fresh_breaker_set_upward_only`), and
`test_an_unresolved_blocker_removes_authority` — which asserted the very behaviour
C8 identifies as the defect — was replaced by eight tests of the authoritative
source. Every amendment is a strengthening: each retains its prior assertions and
adds the exit code, the reason code, or the authoritative-source check.

## Minors deferred, and why

From the G5 and G3 minor lists, none of which are in C1–C12:

- **`probe_cli_capability_manifest` self-pins on first use (TOFU).** Inherent to
  pinning without an out-of-band identity source; C10 now gives the owner a visible
  re-pin, which is the part that was actually missing.
- **`probe_auth` asserts file presence only.** Already documented in the probe's own
  detail text (`live_credential_check: false`). The injected `auth_check` seam is
  there for whoever owns live credential verification; inventing one here would
  claim more than it proved.
- **`tick_daily` no-ops without a ledger.** Direct `SupervisedLoop` callers that
  pass no `run_budget` have no clock seam, and `record_daily` refuses an unknown day
  by design. The per-TASK companion still bounds the same event. Production always
  wires the ledger.
- **`tick_event`'s warning is discarded.** Both counters still tick and both still
  trip; only the WARN-level message of the second is dropped. Cosmetic.
- **`_previous_checkpoint_id` is not persisted (G3 M-4).** The first cycle after a
  resume cannot trip `consecutive_no_progress`. Total livelock stays bounded because
  escaping that way requires restarts and `restart_attempts` IS durable. Persisting
  it is a real improvement and a clean follow-up, but it is new behaviour rather
  than a correction, and this is a correction round.
- **`restart_attempts` ticks AFTER the relaunch (G3 M-3).** Deliberate, and I have
  corrected the report's blanket claim instead of the code: a restart that has
  already happened cannot be un-done by a breaker, so ticking after is the only
  truthful placement. The effective allowance is `limit` restarts, which is what the
  name says.
- **AS-20's registry scan matches a name in a comment (G3 M-5).** Left as-is; the
  per-counter wiring tests are the real proof, and this scan is only a backstop
  against adding a counter with no site at all.
- **`AuditLog` holds its chain head in memory; `recovery.py`'s dormant
  `limited_auto_enabled` key.** Both pre-existing, both documented, neither touched
  by this task.

## Still deliberately NOT done

Everything in §9 above still holds. Plus, from this round: `turnover_adapters.py`
(C3 says explicitly not to), `remote_approvals.py:308` (M0-T080), and the
journal-DB ACL hardening, which the correction set defers to the owner checkpoint
as a host act — C1 removes the exploit it enabled.
