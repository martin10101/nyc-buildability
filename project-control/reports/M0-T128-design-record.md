# M0-T128 design record - Stage-3 live cross-task wiring (D-024 Amendment 25)

Producer: supervisor-wiring-producer (fresh unnamed roster spawn). Base identity
`7576e0dee2800cf54f520e944ea3a8bec6da0cc4` on `control/D-024-fable-codex-loop`,
worktree `wt-m0t128`. This record is the design half of the deliverable; the
producer report carries the exact command outputs.

Authority: D-024-R400..R405 (Amendment 25, Option A) - wire the already-built,
simulation-proven exactly-once next-task machinery (`next_task.py`) into the LIVE
limited-auto path behind the EXISTING `--mode limited-auto
--owner-enable-bounded-auto` gate. No new activation surface; no change to the
R595/bounded-mode gate semantics; no broker/allowlist change; journal and
evidence untouched throughout (R401); no PR #241 merge, clear-recovery, loop
start, or live commissioning (R403). Engineering-reliability sections applied:
S4 (async/multi-task flow), S5 (idempotency/exactly-once), S6 (resume), S7
(caller-visible error surfaces), S8 (verification contexts).

## 1. What was unwired, and what this task wires

At the frozen M0-T127 identity only `plan_close_run` had a production caller
(`cli.py:2687`). `select_next_packet`, `record_advancement`, and
`advance_and_select` had ZERO callers (M0-T127 s7.4). Consequently R393 facts
5-full (audited exactly-once advancement live), 6 (next task selected), and
cross-task 7 (multiple successive tasks, no owner touch) were unprovable.

This task adds ONE live driver, `next_task.run_task_queue`, called from
`cli.cmd_start` only when the owner opts into multi-task, that:

1. runs the owner-typed first task exactly as today (`cli._run_loop`);
2. on a Codex COMPLETE verdict, records the AUDITED exactly-once advancement
   (`record_advancement`, over the durable single-winner CAS) BEFORE selection;
3. selects the next ELIGIBLE successor from the owner-supplied ordered queue,
   fail-closed (sec 3);
4. re-enforces the per-task isolated-worktree/repo launch seam (via both the
   driver's own eligibility check AND `cli._run_loop`'s existing
   `enforce_launch_bindings` backstop);
5. re-checks stop/pause/graceful/emergency intents, the run budget, and the
   rotation ceiling at the between-task seam (sec 4);
6. continues across MULTIPLE BOUNDED tasks under an explicit `--max-tasks` bound
   (sec 5), never unbounded fan-out.

`run_task_queue` stays a testable leaf: it decides and records; the loop (via the
injected `run_one=_run_loop` callback) owns every state transition, provider
contact, and dispatch. It writes only NEW durable keys
(`task_advancement/<id>`, `task_queue/queued_digest/<id>`), never the preserved
live journal's own rows (R374/R375 intact).

## 2. Selection source (design choice, documented)

The owner names the WHOLE universe of selectable work at start time; the
controller never invents candidates. Two NEW optional flags on `start`:

- `--max-tasks N` (int, DEFAULT 1). The hard bound on how many BOUNDED tasks one
  owner-typed start advances across. Default 1 = the exact certified single-task
  behaviour; the cli routing condition `int(args.max_tasks) > 1 or
  args.packet_queue` is False for the certified defaults, so `cmd_start` calls
  `_run_loop` directly and the driver is never entered (test
  `DefaultShapeTests`).
- `--packet-queue PATH` (default None). A JSON file listing the ORDERED
  SUCCESSOR tasks (task 2..N): `{"tasks": [ {"task_id","packet_path","worktree",
  "branch","repo"}, ... ]}`. Each entry carries the packet to bind AND the
  isolated worktree/branch/repo the next start must launch in, so selection can
  re-enforce the launch seam before dispatch. The first task remains the
  owner-typed `--task-packet` / `--worktree` / `--branch` / `--repo`, validated
  by `cmd_start` exactly as today.

Rationale for a queue file over a repeatable `--task-packet`: a single auditable
artifact that carries the per-task worktree/branch/repo triple the launch seam
needs; a repeatable flag would need parallel repeatable `--worktree`/`--branch`
flags with positional coupling, which is error-prone and harder to review.

The two flags have SAFE DEFAULTS, so they are NOT load-bearing for the certified
single-task command shape and are deliberately NOT added to
`command_docs.REQUIRED_START_FLAGS` (adding them would break the certified
command, which omits them). The command-doc tooth stays green with no runbook or
`command_docs.py` change (producer report, tooth section). A documented multi-task
command shape for the LATER R407 commissioning presentation is:

```
python -m tools.agent_supervisor start --mode limited-auto --owner-enable-bounded-auto \
  --checkout <ctl24> --repo <repo> --branch <task-1-branch> --worktree <wt-1> \
  --max-cycles 1 --task-packet project-control/tasks/<task-1>.json \
  --max-tasks 3 --packet-queue <queue.json> \
  --claude-executable <...> --codex-executable <...> --config <...> \
  --model-selection <...> --manifest <...>
```

That presentation (mechanically re-validated per R408) belongs to the R406/R407
recert+presentation step, not this wiring task; it is documented here for the
reviewer, not added to the runbook (which would only present it once the owner
authorizes the live journey).

## 3. Eligibility rule set (R405, fail-closed) - `evaluate_eligibility`

Applied to every SELECTED successor (never to the owner-typed first task, which
runs as today). Checks are cheapest-first; the FIRST failing check wins. Every
refusal carries a stable `code` + human `reason`; the driver records a
`cross_task_candidate_skipped` audit row and a `skipped` step - NEVER silent.

| # | Category | Refusal code | Refusal path |
|---|---|---|---|
| 1 | packet unreadable / not JSON / not an object | `packet_unreadable` / `packet_unparseable` / `packet_not_object` | `_read_packet_file` raises `NextTaskError`, caught -> ineligible verdict, skipped |
| 2 | queue entry id != packet's own `task_id` | `task_id_mismatch` | ineligible, skipped |
| 3 | status not in the narrow eligible set `{"claimed"}` | `ineligible_status` | ineligible, skipped |
| 4a | open `blockers` | `blocked` | ineligible, skipped |
| 4b | any owner-gate field truthy (`owner_gated`,`owner_hold`,`holds`,`awaiting_owner`,`requires_owner`,`on_hold`,`hold`) | `owner_gated` | ineligible, skipped |
| 5a | a dependency packet missing/unreadable | `dependency_unresolved` | ineligible, skipped |
| 5b | a dependency's own status != `accepted` | `dependency_unaccepted` | ineligible, skipped |
| 6a | declared worktree absent (not a dir) | `worktree_missing` | ineligible, skipped |
| 6b | worktree IS the primary control checkout | `worktree_primary_checkout` | ineligible, skipped |
| 6c | launch-seam binding refuses (`enforce_launch_bindings`: cwd/worktree or evidence/repo) | `binding_<code>` | ineligible, skipped |
| 7 | packet content changed since queueing (digest mismatch vs the queued snapshot) | `stale_packet` | ineligible, skipped |

Design notes:

- **Eligible-status set is narrow and explicit**: only `claimed` (a task claimed
  for supervised execution). `accepted`, `awaiting_gate`, `backlog`, `blocked`,
  `in_progress`, or any unknown status is refused. This is the "claimed for this
  run" reading of R405, verified against the live packet statuses (survey in the
  producer report). It also covers the "claimed-by-another/wrong-status" family:
  a task whose status is anything but `claimed` is refused.
- **Dependency acceptance** is read from each dependency's OWN packet
  (`status == "accepted"`) in the candidate's tasks directory. Advancement is NOT
  acceptance: a successor that depends on a task the supervisor just ADVANCED (but
  which no gate has ACCEPTED) stays ineligible and is skipped - the supervisor
  never runs ahead of a human/gate acceptance.
- **Worktree binding** reuses the EXISTING `launch_seam.enforce_launch_bindings`
  (`evaluate_packet_worktree_binding` + `evaluate_repo_binding`) so the driver's
  pre-selection check can never disagree with `_run_loop`'s runtime backstop. Two
  layers enforce isolation: the driver skips a binding-violating successor
  VISIBLY before dispatch, and `_run_loop` raises a typed `LoopError` at dispatch
  if one ever slipped through.
- **Staleness**: at driver start every successor's packet raw-bytes sha256 is
  snapshotted CAS-once under `task_queue/queued_digest/<id>`. Selection recomputes
  the digest and compares; any change (content or a moved worktree reflected in
  the packet) reads as `stale_packet`. CAS-once means a crash-resume that re-reads
  the same queue keeps the ORIGINAL snapshot, so a packet edited mid-journey can
  never silently re-baseline itself.

Ineligible successors are SKIPPED and the driver tries the next candidate; when
every remaining candidate is ineligible the journey lands `NO_ELIGIBLE_WORK`
visibly (sec 9 family). An empty successor queue after a completed first task lands
`queue_exhausted`.

## 4. Between-task seam - `between_task_seam`

Before dispatching each SUCCESSOR (never before the owner-typed first task) the
driver re-checks, reusing the EXISTING durable machinery so it can never disagree
with the between-CYCLE seam:

1. **owner intents** - `stop_intent.effective_intent(StopIntents.read(journal))`;
   any active emergency/graceful/pause wins over queued work -> stop
   `owner_intent_<intent>` (the removal-sensitive family-10 mechanism);
2. **run budget** - the prior run's durable ledger report
   (`run["run_budget"]["exhausted"]`) -> stop `budget_exhausted`; the next task's
   own first-cycle `_budget_stop` additionally backstops this;
3. **rotation ceiling** - `rotation.rotation_pending(journal)` -> stop
   `rotation_pending_before_next_task`; `_run_loop`'s
   `_rotate_over_ceiling_before_first_dispatch` additionally backstops the
   fresh-session ceiling.

Advancement of the just-completed task is recorded BEFORE the seam (R402: CAS
before selection), so a between-task stop preserves exactly-once integrity of the
finished task while refusing the next dispatch.

## 5. Multi-task bound (Amendment-3 R146)

`--max-tasks` (default 1) bounds the number of tasks DISPATCHED across the
journey; per-task `--max-cycles` and `turn_budget` continue to bound each task's
own units. A task already carrying a durable advancement record (a crash-resume)
counts toward the bound (it was dispatched in a prior process). Ineligible
successors that are skipped do NOT consume the bound (nothing was dispatched).
Never unbounded fan-out: the driver only ever iterates the finite owner-supplied
ordered list, and stops at `max_tasks_reached`.

## 5A. run_id and budget across a multi-task journey (G3-C2)

ONE owner-set run budget bounds the WHOLE journey, not one budget per task. The
mechanism, traced through the live `cli._run_loop` path:

- **Shared run_id.** The driver passes the SAME `args` to every task's
  `cli._run_loop` (it re-binds only `task_packet`/`worktree`/`branch`/`repo`,
  never `run_id`). The commissioning start omits `--run-id`, so each `_run_loop`
  derives the same run_id from the checkout (`run_{checkout_key(checkout)[:12]}`);
  when `--run-id` is supplied it is likewise shared. Either way every task in one
  journey runs under ONE run_id.
- **Budget clean-resume (not conflict).** Each task's `_run_loop` builds a
  `RunBudgetLedger(journal, run_id=run_id, budget=RunBudget.from_limits(...))` and
  calls `budget_ledger.start()`. Task 1 PERSISTS the budget for the run_id; task 2
  (same run_id, same budget digest, because the driver never changes `--checkout`
  or any budget-affecting arg) takes the durable ledger's clean RESUME branch
  (`run_budget.py:341-434`) - NOT a `budget_conflict`. A `budget_conflict` is the
  ledger's "a run tried to change its own bounds" tamper signal; it fires only if
  a second start named DIFFERENT bounds for the same run_id, which the driver never
  does. So the owner's single run budget (wall-clock and counter bounds) is loaded
  once and then reasserted, bounding the entire multi-task journey.
- **Between-task backstop.** `between_task_seam` additionally reads the prior
  run's durable `run_budget.exhausted` report before dispatching the next task, so
  a journey whose shared budget is spent stops at the seam (`budget_exhausted`)
  rather than starting another task; the next task's own first-cycle `_budget_stop`
  is a further backstop.
- **Close-run on the shared journal.** A task resting at COMPLETE is closed to
  IDLE by the NEXT task's `_run_loop` via `plan_close_run` (cli.py:2687) firing the
  existing `run_closed` edge on the SHARED journal, so the successor can start from
  a cycle-entry state. Closing never merges, accepts, or crosses an owner gate.
- **D6 dispatch-intent across the boundary.** Each task's real `SupervisedLoop`
  records a dispatch intent before provider contact and reconciles it when the unit
  returns (`recovery.record_dispatch_intent` / `reconcile_dispatch_intent`,
  loop.py:1627/1638) on the shared journal; after a completed multi-task journey no
  dispatch intent is left unreconciled (`journal.pending_effects()` empty).

Live-path coverage of this section: `LiveRunLoopCrossTaskTests` (drives the real
`cli._run_loop` across both tasks via the driver) asserts the shared-run_id clean
budget resume (no `budget_conflict`), the COMPLETE->IDLE close on the shared
journal between tasks, and the reconciled D6 dispatch intents; `CmdStartDispatchTests`
drives the same journey through the REAL `cli.cmd_start` routing (cli.py:3069).

## 6. Crash matrix (exactly-once across crashes, R402) - `run_reached_complete` + CAS

| Crash boundary | Behaviour | Test node |
|---|---|---|
| DURING a task (run returns non-complete) | `run_reached_complete` is False -> NO advancement; journey stops `task_not_completed`; a genuine restart re-runs and advances exactly once | `CrashMatrixTests::test_crash_BEFORE_advancement_leaves_nothing_advanced` |
| AFTER advancement, BEFORE next dispatch | genuine journal reopen; `is_advanced` True -> the advanced task is SKIPPED (never re-run), the restart selects the NEXT task, no double-advance | `CrashMatrixTests::test_crash_AFTER_advancement_before_dispatch_resumes_without_doubling` |
| duplicate/contradictory provider output for the same task | `record_advancement` CAS loses -> returns the STORED record, `newly_recorded=False`, never a second advance | existing `test_agent_supervisor_next_task.py` + `DuplicateAdvancementTests` |

Exactly-once argument: the durable `compare_and_swap_state(key, expected=None,
...)` is a single-winner primitive; the FIRST advancement of a task_id wins and
its presence is the exactly-once witness. Selection (`is_advanced`) skips any task
with a durable record, so re-entry after an advancement picks the NEXT task. A
crash anywhere in the advance->select->dispatch step therefore resumes without
duplicate or lost advancement. `run_reached_complete` gates advancement on the
durable COMPLETE state AND a last cycle whose Codex decision is COMPLETE carrying
a reviewed checkpoint id, so a run that stopped for budget/intent/REVISE/ASK/any
refusal never advances (family 5).

## 7. Owner gate + driver envelope confinement (R402; G3-C1)

The authorized envelope is `--mode limited-auto` AND
`--owner-enable-bounded-auto`, and it is now enforced in TWO complementary halves
so the driver can never run outside it:

- **Owner-enable half - `bounded_mode_gate(args)` (pre-dispatch, `cmd_start`).**
  `--mode limited-auto` without `--owner-enable-bounded-auto` is refused BY NAME
  before dispatch (exit 16, typed refusal), exactly as today. So a limited-auto
  start that reaches the driver has already proven the owner enable.
- **Mode half - `run_task_queue`'s own fail-closed check (this task, G3-C1).**
  The driver asserts `args.mode == "limited-auto"` as its FIRST act, before any
  packet is read, snapshotted, or dispatched. A `--mode supervised/shadow
  --max-tasks 2 --packet-queue q.json` start - which `bounded_mode_gate` does NOT
  refuse (supervised/shadow are not owner-gated) and which the cli routing ternary
  (`max_tasks>1 or packet_queue`) WOULD otherwise carry into the driver - is
  refused fail-closed with the typed code `cross_task_mode_refused` and an audit
  row (`cross_task_mode_refused`). The refusal rides the existing
  `next_task.NextTaskError` arm of the `cmd_start` dispatch try/except
  (cli.py:3070): a report, not a traceback. The driver body never runs.

This closes the G3-C1 gap: the prior claim that "everything sits behind
`bounded_mode_gate`" was incomplete, because `bounded_mode_gate` only enforces the
enable half and never confines the driver to limited-auto. The invariant "a start
WITHOUT (owner-enable-bounded-auto AND limited-auto) cannot reach the queue driver
body" now HOLDS: the enable half is enforced by `bounded_mode_gate`, the mode half
by the driver's own check. Removal-sensitive test: `ModeConfinementTests`
(supervised/shadow with `max_tasks>1`/`--packet-queue` -> typed refusal, nothing
dispatched, audit row; limited-auto -> proceeds).

The driver is otherwise reached only inside the existing dispatch branch, after
every recovery/containment/manifest gate `cmd_start` already runs. No new flag
enables autonomy; `--max-tasks` / `--packet-queue` are launch inputs that select
WHICH bounded work runs, not WHETHER the bounded mode is authorized. No R595,
broker, or allowlist change.

## 8. Audit (R402)

Typed audit rows: `cross_task_dispatch` (each task dispatched),
`cross_task_candidate_skipped` (each ineligible skip, with code+reason),
`cross_task_advancement` (each advancement, with newly_recorded),
`cross_task_intent_stop` / `cross_task_budget_stop` /
`cross_task_rotation_pending` (between-task stops). The `TaskQueueResult` returned
to `cmd_start` (`run["task_queue"]`) carries the per-task steps, the advanced
list, the dispatched count, and the stop reason for the operator record.

## 9. R404 ten-family coverage map (family -> test node)

New file `tools/test_agent_supervisor_cross_task.py`. Family 1 drives the REAL
`SupervisedLoop` + real `StateMachine` + real durable journal + real
`plan_close_run`/`record_advancement` with only the provider (runner+reviewer)
faked at the standard `run_unit`/`review` seam - the "real loop path with a fake
runner, not the sim harness". Families driven by a scripted `run_one` exercise
the real production driver's decision logic (the scripted callback is the
provider-loop seam, not the driver).

| # | Family | Test node(s) |
|---|---|---|
| 1 | live cross-task selection (two-packet, first completes, second dispatches, REAL loop) | `LiveCrossTaskSelectionTests::test_two_task_journey_completes_and_advances_each_exactly_once` (+ bound test) |
| 2 | each ineligible category skipped with the audit reason | `EligibilitySkipTests` (owner-gated via blockers, owner-gate field, wrong status, accepted, missing worktree, primary-checkout worktree, unparseable, task_id mismatch, later-eligible-after-skips) |
| 3 | dependency ordering (unaccepted -> ineligible until accepted) | `DependencyOrderingTests` (unaccepted / accepted / missing dep) |
| 4 | isolated-worktree binding refuses (exit path, not silent) | `WorktreeBindingTests` (verdict + driver visible skip) |
| 5 | checkpoint + Codex-review completion required before advancement | `CompletionRequiredTests` (non-complete never advances; run_reached_complete requires checkpoint id / COMPLETE decision / COMPLETE state) |
| 6 | duplicate advancement refused | `DuplicateAdvancementTests` + existing `next_task` idempotency tests |
| 7 | crash BEFORE / AFTER advancement (genuine journal reopen) | `CrashMatrixTests` (two nodes) |
| 8 | stale campaign state | `StalePacketTests` (verdict, driver mid-journey edit, snapshot survives restart) |
| 9 | no eligible work lands NO_ELIGIBLE_WORK visibly | `NoEligibleWorkTests` (all ineligible; empty queue exhausted) |
| 10 | stop/pause/emergency/graceful intents between tasks | `BetweenTaskIntentTests` (emergency, pause, graceful, budget, no-intent) |

Removal-sensitivity: each family asserts a specific refusal code / dispatch order
/ advancement fact that depends on its mechanism, so reverting a mechanism (e.g.
dropping the status gate, the dependency check, the staleness snapshot, the
between-task intent read, or the completion gate) fails its family.

## 10. Golden-run decision

No new golden-run scenario added. The two-task live journey is proven at the
appropriate altitude by family 1 (real loop + real journal + fake provider) plus
the crash-matrix reopen tests, which are faster, deterministic, and
removal-sensitive. The golden pack certifies the single-task journey shape at the
frozen identity; a cross-task golden blob would move the disclosed golden-blob
(T120 precedent) for coverage already provided at the unit/integration layer.
Decision: documented NO golden change; the full recert (R406) re-runs the
existing golden unchanged.

## 11. Modularity / flags / tooth

- `cli.py` net-zero (2953/2953): two multi-line `add_argument` calls folded to one
  physical line each to fund the two new one-line flags; the driver-routing change
  and the `NextTaskError` catch are net-zero (one statement -> one statement,
  same lines). `claude_runner.py` untouched.
- `loop.py` untouched (no need; the loop already closes-run and re-binds per
  task; the driver wraps it).
- All new selection/eligibility/queue/driver logic lives in `next_task.py` (the
  packet's designated home). It grows 276 -> ~691 SLOC. next_task.py is NOT
  baseline-tracked, so modularity `--check` fails only above the HARD 1000
  threshold; 691 is a non-blocking `review_signal` warning (above WARN 600, below
  JUSTIFY 750). A new focused module would be cleaner but is outside allowed_paths;
  the packet directed placement in next_task.py. `modularity_check.py --check`
  reports 0 failures.
- Command-doc tooth: 0 changes needed (the new flags are optional with certified
  defaults, so `REQUIRED_START_FLAGS` and the runbook are unchanged); the tooth
  reports 0 failures.

## 12. Residual limitations (honest list)

1. **Real-loop coverage altitude**: family 1 exercises the real `SupervisedLoop`
   with a faked provider (the standard `run_unit`/`review` seam), NOT the full
   `cli.cmd_start` process (which needs live config/model_selection/manifest files
   and containment). The driver + loop + journal + close-run + advancement are all
   real; only the provider and the outer cli gating are faked. The other nine
   families use a scripted `run_one` so completion/crash/eligibility can be
   controlled precisely.
2. **Eligible-status set is a design choice** (`{"claimed"}`). If a future campaign
   claims tasks under a different status vocabulary, the set must be widened
   (explicit constant `ELIGIBLE_STATUSES`, one edit) - a conscious narrow default,
   not an oversight.
3. **Between-task budget/ceiling** are read from the prior run's durable report and
   `rotation.rotation_pending`; the authoritative enforcement remains the next
   task's own first-cycle `_budget_stop` / `_rotate_over_ceiling_before_first_dispatch`.
   The seam is an early, auditable stop, not a second budget ledger.
4. **`last_run is None` edge** (every queued task already advanced on resume, no
   eligible successor) returns a non-dispatched shape stopped `NO_ELIGIBLE_WORK`,
   which the unattended-refusal mapper reports as a detectable non-zero exit - an
   unattended start that found nothing to do surfaces loudly rather than silently
   exiting 0.
5. **No live commissioning performed** (R403): this task only wires and tests. The
   R406 recert and R407 owner-executed seven-fact commissioning are separate steps.
