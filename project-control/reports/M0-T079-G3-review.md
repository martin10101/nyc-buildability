# M0-T079 G3 code-walkthrough review (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the read-only reviewer agent's return channel
(report-preservation rule). Reviewer: t079-g3-reviewer (independent; reviewer ≠ producer ≠
verifier). Gate-verdict semantics (.claude/rules/project-control.md): PASS with required
corrections — the four IMPORTANT findings are BLOCKING for the next gate and for acceptance.

---

# G3 code-walkthrough review — M0-T079 (bounded unattended mode)

**Verdict: PASS**, with four **important** findings recorded as required rework. No must-fix. Every finding is on the *refusal* side of the code — the change never dispatches something it shouldn't, never corrupts durable state, and never widens authority. What it does, in four places, is refuse legitimate launches it shouldn't refuse, or advertise a check it doesn't actually perform.

## Independent verification of the producer's claims

| Item | Result |
|---|---|
| Suite | `1707 passed, 2 skipped, 555 deselected` in 197.45s — 0 failures. Matches report §6.2 exactly. |
| Modularity | `selected 272 files; failures 0; warnings 5`. The seven new modules are now tracked and censused (the report's 265 was pre-commit) and it still passes; all five warnings are the pre-existing ones. |
| Content identity | `tools/agent_supervisor` tree at `c52613f` is `0175f40edfc5fcc10b181a430730dc5f10c010be`, byte-identical at the session's current HEAD `73f5b85` (which added only ledger/evidence files). The review holds for both. |
| 5+ named acceptance tests | AS-2, AS-4, AS-6, AS-12, AS-15, AS-17, AS-20 all pass when run individually (7 passed in 4.19s). |

**R037 (no hardcoded max run length)** holds structurally. I grepped the whole package and the CLI argparse: no ceiling constant exists, `--run-wall-clock-seconds` has `default=None`, and `check()` (`run_budget.py:396`) returns not-exhausted on `wall is None` *before* any arithmetic, so there is no timer to mis-tune. Zero and negatives are refused rather than read as "unlimited". The source-scan test is not vacuous — I probed its regex against synthetic constants and it catches `MAX_RUN_SECONDS`, `RUN_CEILING`, `MAX_WALL_CLOCK`, `RUN_LENGTH_MAX` — but see minor finding M-2 for its blind spots.

**Crash-resume integrity** holds. `elapsed()` returns `max(now - persisted_start, durable_high_water, 0)`, so it cannot shrink; `observe()` only ever raises the mark and counts backwards-clock observations; `persist_counters` takes `max(current, incoming)` per counter and `CircuitBreakers.restore` does the same, so reconciliation only tightens. I found no path by which a run extends or resets its own budget: `started_at_epoch` has no setter, `finalize()` clears nothing, and `loop.py` only calls the read/observe methods. I confirmed `budget_conflict` live — reopening `run_abc` with a different wall clock raises `budget_conflict`, and reopening with the same bounds after tallies hit a limit reads `exhausted=True, dimension=counter`.

**Breaker wiring** is correct. All nine new counters tick at the claimed sites, and the six that gate a provider call or an outbound write tick strictly *before* it (`loop.py:1657, 1698, 1969, 2188, 2606`). The three pre-wired counters are each ticked exactly once and nowhere else — `claude_runs_per_task` at `loop.py:1680`, `codex_reviews_per_checkpoint` at `loop.py:1955`, `consecutive_hard_denies` at `broker.py:427` (and `broker.py` is not in the diff at all). A trip returns a `CycleResult` with `stopped` set, which breaks the `run()` loop at `loop.py:2706` — synchronous, no further dispatch.

**Amended tests are all strictly strengthening.** I read every one of the ten amendments. Each `assertRaises(NotImplementedError)` became an exit-code assertion *plus* the same message-phrase assertions *plus* `assertNotIn("Traceback", ...)`. Each `assertEqual(code, 0)` became an assertion on a specific typed exit code plus the refusal outcome, retaining every pre-existing assertion about `dispatched`, `provider_calls_made`, `containment`, and audit events. The `test_the_budget_module_cannot_widen_policy` amendment widened the scan from `loop.py` to `loop.py` + `owner_touch.py` and added a non-vacuity assertion. No assertion was weakened, no case deleted, no skip added.

**Extractions are faithful.** I diffed `owner_touch.py` line-by-line against the pre-change `loop.py`: only the new module docstring and its three import lines are novel — every code line is verbatim. `loop.py` re-exports `LoopError` and all of `owner_touch`'s names, so `lp.OwnerTouchLedger` and `from tools.agent_supervisor.loop import LoopError` still resolve for all seven external importers.

## The state_kv deviation — sound, not a parallel store

`DurableJournal.set_state` (`durable_state.py:371`) writes through the same connection under `journal_mode=WAL` + `synchronous=FULL` with an explicit `BEGIN IMMEDIATE` / `COMMIT` / `ROLLBACK`, into the `state_kv` table that `broker.py`, `anchor.py`, `claude_runner.py`, `loop.py`, `model_change_ipc.py`, and `notifications.py` already use for durable S7 records. It genuinely inherits the journal's transactional durability, uses the identical write path as every sibling durable record, and no migration was needed because `state_kv` has existed since schema v1. Choosing it over a new table is correct.

## Findings

### Important

**I-1. `probe_task_authority` reads a field the control plane never maintains** — `tools/agent_supervisor/recovery_probes.py:252-257`.

The probe fails closed on `if ledger.get("blockers")`, calling it "unresolved blocker(s)". But `tools/project_control.py` initialises `"blockers": []` at task creation (line 799) and *never* appends to or prunes it anywhere; the actual blocking authority is `project-control/blockers/B-*.json` with `status in ("open", "")`, matched against the task id by `_blocker_references` (line 1176). The task record's list is free-form historical annotation. Two consequences, both live today:

- **False refusal:** `M0-T019.json` is `accepted` while carrying `["B-017"]`, and `B-017` is `resolved`. Any task whose record carries a resolved blocker id can never be supervised — `start` exits 11 `task_blocked` forever, and the only remedy is editing historical ledger evidence.
- **Unbacked assurance:** an *open* blocker record referencing the task does not stop `start`, because the probe never reads `blockers/`. The probe's own detail text asserts "no unresolved blockers", which it has not established from the authoritative source — the same shape of defect this task exists to fix.

**I-2. The `deadline_restored` gate never compares the deadline to now** — `tools/agent_supervisor/cli.py:2996` reading `tools/agent_supervisor/recovery.py:520`.

`recovery.classify`'s override fires on any non-empty `resume_not_before_utc`, expired or not, and `cmd_start` now refuses on that reason code. `RESUME_NOT_BEFORE_KEY` is cleared *only* by `ResumeScheduler.cancel()` (`resume_scheduler.py:968`), reachable from `stop`, `emergency-stop`, and `cancel-scheduled-resume`; `mark_consumed()` does not clear it and has no callers. I verified this live against the producer's own fixture: with the key set to `2020-01-01T00:00:00Z` on an otherwise-healthy checkout, `start` exits **13** with `reason_code: deadline_restored`, `dispatched: False`, `probes.failed: []`; the identical control run with no deadline exits 0 and dispatches. Pre-change the gate was `outcome.classification != SAFE_CHECKPOINT` and this dispatched.

Two things make this a defect rather than a judgment call. `assert_may_contact_provider` (`resume_scheduler.py:998`) explicitly permits provider contact once the deadline has passed, so the two layers now disagree. And `probe_scheduled_deadlines` already computes exactly the fact needed — it records `outstanding=True/False` — but the gate ignores it. The report's §3.6 says the tightening stops dispatch over "an unexpired deadline"; the code stops over any deadline. Nothing in production sets the key on this build, which is why no test caught it, but the S11.4 usage-limit path is a later task in this same campaign and this is precisely the flow a 10-hour unattended run needs.

**I-3. The provider-CLI identity pin has no re-pin or clear path** — `tools/agent_supervisor/recovery_probes.py:65`, `467-490`.

`probe_cli_capability_manifest` pins each executable's digest on first `start` and refuses `provider_cli_drift` (unsafe, exit 11) on any later mismatch. I grepped the whole tree: nothing outside this function and its tests ever reads or writes `cli_executable_identity`, and no CLI command clears it. A routine Claude Code or Codex CLI auto-update therefore makes every subsequent `start` on that checkout refuse, with no supported remediation short of deleting the journal — which destroys the run's durable evidence, the very thing the rest of this task works to preserve. Drift detection is right; a drift latch with no owner-visible re-pin is an operational trap.

**I-4. Per-task tallies are now durable per run id, and the default run id is per checkout** — `tools/agent_supervisor/cli.py:2714` with `tools/agent_supervisor/run_budget.py:410-415`.

`run_id` defaults to `f"run_{checkout_key(checkout)[:12]}"`, so every `start` on a checkout reopens the same budget record and `restore_counters` reloads its tallies. Right for a crash-resume, but the code cannot distinguish a crash-resume from a deliberately new run — both are the same command with the same arguments. I verified the consequence directly: after persisting `claude_runs_per_task: 12` (the config default limit) and calling `finalize(exit_reason="max_cycles_reached")`, a fresh `RunBudgetLedger` for the same run id reads `resumed=True, exhausted=True, dimension=counter, counters=('claude_runs_per_task',)`. From that point every `start` on that checkout returns 0 cycles and exit 15 `budget_exhausted`; the message says "the owner-set run budget is spent" and does not mention that `--run-id` is the way out (and `--run-id` has no help text). The streak counters make this reachable sooner: three `start` invocations that each end in `no_valid_checkpoint` persist `consecutive_invalid_outputs: 3`, which is the default limit — I observed the first such start persisting `consecutive_invalid_outputs: 1` through the real CLI. This also changes a documented frozen semantic: `circuit_breakers.py:57-64` still says "a fresh `CircuitBreakers` is built per `start`, and the counter never resets, i.e. units-per-run", which is no longer true, and §2.3/§3.4 of the report do not note the change.

### Minor

**M-1.** `start_gate.py:122` annotates `journal: DurableJournal` but never imports the name. Runtime-safe only because of `from __future__ import annotations`; `typing.get_type_hints()` on `live_revalidation` would raise.

**M-2.** `test_no_hardcoded_maximum_run_length_exists_anywhere` scans only `run_budget.py`, not "anywhere". I probed its regex: it misses `_MAX_RUN_SECONDS` (leading underscore defeats the `^MAX_` anchor), `ABSOLUTE_RUN_CAP`, `HARD_STOP_SECONDS`, and `DEFAULT_WALL_CLOCK_SECONDS`, and a ceiling added in `loop.py` or `cli.py` would not fail it at all. Real R037 compliance rests on the structure, not this guard; the guard's name overclaims.

**M-3.** `restart_attempts` ticks *after* the relaunch (`loop.py:2757-2759`), unlike the other eight. The bound still holds, but the effective allowance is `limit` restarts where the before-tick counters allow `limit - 1` events. The report's blanket "every trip is a synchronous pause BEFORE the counted thing happens" does not hold at this one site.

**M-4.** `consecutive_no_progress` is restored durably but then zeroed by the first cycle after any resume, because `_previous_checkpoint_id` (`loop.py:960`) is per-process and starts empty, sending that cycle down the `else` branch at `loop.py:1905`. Total livelock is still bounded, because escaping this way requires restarts and `restart_attempts` is durable — but the counter's durable restore is not load-bearing the way §2.3 implies.

**M-5.** AS-20's registry scan (`test_every_counter_in_the_registry_has_a_wired_event_site`) matches a quoted counter name anywhere in the concatenated text of `loop.py` + `broker.py`, so a name appearing only in a comment satisfies it, and it does not read `loop_breakers.py` where the per-day tick logic actually lives.

## The four judgment calls, adjudicated

**1. Probe strictness (§8.1) — correct, with I-1 and I-3 as the exceptions.** The direction is right and AS-9 is a real positive control. I checked the probe's assumptions against the live ledger: `WORKING_STATUSES` covers `claimed` and `awaiting_gate`, which are the statuses this repo's 129 task records actually use, so that part is sound. The two places the strictness rests on something unsound are the blocker list (I-1) and the drift latch (I-3).

**2. Exit-code changes on previously-exit-0 paths (§8.2) — correct.** This is the defect, not a side effect. Codes start at 10 so they cannot collide with the interpreter's 1/2 or the pre-existing manifest-halt 1; `exit_code_for` raises on an unknown outcome rather than mapping to success; `doctor` prints the whole contract as data so an operator can script against it; and missing-input stops still exit 0, so the "not dispatchable because you didn't name a flag" case is unchanged. Attended modes keep exit 0 for a park, which preserves existing behaviour.

**3. Repeated-checkpoint-id as the no-progress signal (§8.3) — correct.** A worker re-reporting an identical checkpoint id has advanced nothing, and taking the S7 table's existing `checkpoint_unsafe` edge rather than adding an edge is the right call under the freeze. The caveat is M-4, not the choice of signal. Note the counter is ticked before the shadow branch at `loop.py:2148`, so a shadow run can now stop on it too — a tightening, and appropriate.

**4. `record_progress` narrowing on REVISE (§8.4) — correct.** `_REVISE_SAFE_RESETS` is precisely `RESET_ON_PROGRESS` minus `consecutive_revision_loops`. Nothing else changes; a CONTINUE calls `breakers.record_progress()` identically to before. Without the narrowing the counter could never accumulate, which is the reproduced defect. The same narrowing correctly applies on the cross-process resume path (`loop.py:2632`), where the parked record's decision label is passed through.

## The two safety tightenings (item 8)

Both tighten. `safe_but_forbidden` no longer dispatching is unambiguously right — `recovery.classify` returns SAFE_CHECKPOINT for a durable emergency stop, manual pause, or open owner gate, and the old classification gate let all three through. `record_progress` narrowing cannot regress a legitimate flow, as adjudicated above. The `deadline_restored` half of the first tightening is right in principle but wrong in its condition — that is I-2.

## Note on the verdict

Per `docs/ENGINEERING_RELIABILITY_STANDARD.md` §9, important findings are recorded as required rework and do not block, so this is a PASS. Under `.claude/rules/project-control.md`'s gate-verdict semantics, I-1 through I-4 should be treated as BLOCKING for the next gate and for acceptance, recorded by the orchestrator via `project_control.py progress --message`. I-2 has the cleanest fix (gate on the `outstanding` fact the probe already computes); I-1 should read `blockers/B-*.json` the way `accept()` does; I-3 and I-4 each need an owner-visible escape hatch rather than a change to the detection itself.

---

**Reviewed identity:** `c52613f28732d73085efa71114cddde7a1468614` (task commit `e830c4b3bc4519741358f85c7ccb67e74ddb63bb`; `tools/agent_supervisor` tree `0175f40edfc5fcc10b181a430730dc5f10c010be`).

**Commands run** — all read-only (pytest suite + individual acceptance tests, modularity check/report, scratchpad probe scripts for I-2/I-4/M-2/AS-6, git log/show/rev-parse/status/diff read-only forms, grep/Read across the package and governance docs). No repository file created, edited, or deleted; no git mutation; no tools/project_control.py invocation.
