# M0-T121 producer report — audited fail-closed operator recovery surfaces + F-2 edge-reachability closure

Task: M0-T121 (governance; D-024 Amendment 16 rows R302–R313, Amendment 17 R318–R322).
Producer: supervisor-restart-producer. Worktree:
`C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/.claude/worktrees/agent-a5895208e35d99e99`.
Reset to control tip `04216dd5c9f6ef415c445471abacf6d854dcd917`.
Reliability standard sections applied: §2 (smallest fitting change), §3 (red/green + mutation),
§5 (idempotency/exactly-once), §8 (verification contexts), §9 (triage).

## 0. Files changed (all inside allowed_paths)

- `tools/agent_supervisor/restart_channel.py` (NEW, 463 SLOC) — the substance: the read-only
  fail-closed precondition engine, the three operator-recovery surfaces, the emergency-stop
  confirmation token, and the thin CLI verbs + `register_restart_verbs`.
- `tools/agent_supervisor/cli.py` (+2 SLOC net; 2927→2929) — one import and one
  `register_restart_verbs(sub, add_common)` call, mirroring `register_operator_verbs`. No handler
  logic in cli.py (modularity; see §7).
- `tools/test_agent_supervisor_restart_channel.py` (NEW) — the removal-sensitive reachability sweep
  and the AS-1..AS-8 matrix (31 tests).
- `tools/agent_supervisor/README.md` — operator status table + a "leaving a blocking state" section.
- `docs/CONTROLLER_UPDATE_RUNBOOK.md` — new §9a documenting the three commands.
- `state_machine.py` / `recovery.py` were in scope but needed NO edit: the edges already exist in
  the table and `recovery.py` already exposes every read helper the preconditions use.

## 1. Root cause (primary evidence: code + the reproduced M0-T107 refusal)

The S7 table defines the owner recovery edges out of its blocking/terminal states, but three had
ZERO call sites — defined but unreachable, the pilot's F-2 class:

1. `HALTED -> IDLE` on `owner_explicit_restart` (`state_machine.py:399`) — the reproduced defect:
   the owner-typed certified cycle-2 start refused pre-dispatch (`illegal_transition HALTED ->
   HALTED (trigger 'act')`, exit 13) because nothing fires the trigger
   (`project-control/reports/M0-T107-cycle2-start-refusal.md` §1/§2).
2. `EMERGENCY_STOPPED -> IDLE` on `owner_explicit_restart` (`state_machine.py:397`) — the latent
   sibling named in that report.
3. `WAIT_FOR_OWNER -> PREFLIGHT` on `owner_answer_validated` (`state_machine.py:272`) — a THIRD
   latent instance this task's own reachability sweep uncovered. It is fired NOWHERE (grep across
   `tools/agent_supervisor/*.py`: it appears only in the table and in two `cli.py` comments that
   note `resume-pending-prompt` deliberately does NOT cover it). A run parked at `WAIT_FOR_OWNER`
   for an owner QUESTION (not a held prompt) was therefore stranded exactly like the HALTED case.

`recover_boot` classifies the at-rest journal (SAFE_CHECKPOINT in the live case) but never applies a
transition; the loop's `assert_can_act()` fails closed for every `BLOCKING_STATES` member, and
`clear-recovery`/`resume-pending-prompt` cover only `PAUSED_RECOVERY` / the held-prompt
`WAIT_FOR_OWNER` exit. Net: after any certified halt no documented surface could restart the loop.

## 2. Design (smallest fitting change; §2)

A new focused module `restart_channel.py` owns the whole responsibility; `cli.py` stays a thin wire
(the `register_operator_verbs` precedent). Three surfaces, one shared read-only precondition engine:

- `owner-restart` → `owner_restart()`: `HALTED -> IDLE` on `owner_explicit_restart`.
- `acknowledge-emergency-stop` → `acknowledge_emergency_stop()`: `EMERGENCY_STOPPED -> IDLE` on
  `owner_explicit_restart`, **materially stronger** — it requires BOTH an explicit
  `--acknowledge-emergency-stop` flag AND a `--confirm-emergency-token` matching a digest derived
  from THIS journal's emergency-stop provenance (the last transition into `EMERGENCY_STOPPED`),
  printed on a mismatch so the operator must deliberately read and re-supply it. Impossible to
  trigger by habit or a script default.
- `resume-after-answer` → `owner_answer_resume()`: `WAIT_FOR_OWNER -> PREFLIGHT` on
  `owner_answer_validated`, the discovered third instance (permitted only once the owner ask queue
  is empty — proof the question was answered through the authenticated `approve-once`/`deny` path).

Shared fail-closed preconditions (`evaluate_preconditions`, read-only, first failure wins), in order:
durable emergency-stop **flag** (refuses; directs to `stop --clear`), exact source state, open owner
asks (`broker.owner_unanswered_asks`), pending external effects (`journal.pending_effects`),
surviving/undetermined children (`recovery.account_for_children`), and the recorded recovery
classification (must be `SAFE_CHECKPOINT`; a failure attributable to `cli_capability_manifest`/`auth`
is surfaced as `provider_identity_drift` specifically, else `unsafe_recovery_classification`).

Each surface holds the single-instance lock across the check AND the transition (`_locked`), fires
the edge EXACTLY ONCE via `StateMachine.transition`, and appends a durable audited owner-recovery
event (`operator_owner_restart` / `operator_emergency_stop_ack_restart` /
`operator_owner_answer_resume`) alongside the machine's own `state_transition` event. It clears NO
flag, resets NO budget, and dispatches NOTHING (R310/R313).

**Provider-identity drift, non-live context (documented per the packet, never silently skipped).** A
full live drift probe hashes the installed executables and needs the named executables + a live
process, which this operator command has neither. The command instead relies on the recorded
recovery classification: `SAFE_CHECKPOINT` means every S11.5 revalidation step passed — including
`cli_capability_manifest` (the pinned provider-CLI identity compared to the installed executables) —
at the last `recover_boot`. The FRESH live probe is re-run by the subsequent `start` preflight
(`recovery_probes.probe_cli_capability_manifest`), which refuses on `provider_cli_drift` before any
provider contact; this surface only moves the journal to a re-validation entry point (`IDLE` /
`PREFLIGHT`) and dispatches nothing, so `start` gates identity live before the next provider call.

## 3. Enumeration + per-edge proof (R307/R308)

Blocking states: `WAIT_FOR_OWNER`, `PAUSED_RECOVERY`, `EMERGENCY_STOPPED`, `HALTED`
(`BLOCKING_STATES`). Terminal states: `COMPLETE`, `EMERGENCY_STOPPED`, `HALTED` (`TERMINAL_STATES`).

Every edge LEAVING a blocking-or-terminal state (mechanically derived by the reachability test):

| From | To | Trigger | Reachable by | Kind |
|---|---|---|---|---|
| `WAIT_FOR_OWNER` | `PREFLIGHT` | `owner_answer_validated` | **`resume-after-answer`** (NEW) | operator-recovery |
| `WAIT_FOR_OWNER` | `FORWARD_PROMPT` | `owner_approved_pending_prompt` | `resume-pending-prompt` + `loop.py:2109` | operator-recovery |
| `WAIT_FOR_OWNER` | `EMERGENCY_STOPPED` | `owner_emergency_stop` | `emergency-stop` path (loop) | to-terminal (not a resume) |
| `WAIT_FOR_OWNER` | `COMPLETE` | `owner_closed_stage` | loop-driven owner close | to-terminal |
| `WAIT_FOR_OWNER` | `HALTED` | `owner_halt` | loop-driven owner halt | to-terminal |
| `PAUSED_RECOVERY` | `PREFLIGHT` | `owner_cleared_pause` | `clear-recovery` | operator-recovery |
| `PAUSED_RECOVERY` | `EMERGENCY_STOPPED` | `owner_emergency_stop` | loop | to-terminal |
| `PAUSED_RECOVERY` | `HALTED` | `owner_halt` | loop | to-terminal |
| `EMERGENCY_STOPPED` | `IDLE` | `owner_explicit_restart` | **`acknowledge-emergency-stop`** (NEW) | operator-recovery |
| `HALTED` | `IDLE` | `owner_explicit_restart` | **`owner-restart`** (NEW) | operator-recovery |
| `COMPLETE` | `IDLE` | `run_closed` | loop run-closeout (not `owner_`) | internal closeout |

The reachability test defines an **operator-recovery EDGE** mechanically as a `(state_from, trigger)`
pair whose source is blocking-or-terminal, whose target is NOT, and whose trigger begins with
`owner_`. That yields exactly the FIVE edges `{(WAIT_FOR_OWNER, owner_answer_validated),
(WAIT_FOR_OWNER, owner_approved_pending_prompt), (PAUSED_RECOVERY, owner_cleared_pause),
(EMERGENCY_STOPPED, owner_explicit_restart), (HALTED, owner_explicit_restart)}`. Note
`owner_explicit_restart` appears on TWO edges — edge granularity (not trigger granularity) is
required by R309, because a trigger-level sweep stays GREEN when one of those two edges loses its sole
surface while the sibling keeps the trigger alive (the G3-F2 / G4 MEDIUM finding). Each edge now has
exactly one documented callable CLI surface whose handler names BOTH the trigger and the source
state. The `owner_*` edges to a terminal state (`owner_halt`, `owner_closed_stage`,
`owner_emergency_stop`) are intentionally NOT operator-recovery-resume edges: they DEEPEN a stop, are
loop-driven, and are excluded by the target-not-blocking-or-terminal rule. `COMPLETE -> IDLE`
(`run_closed`) is the internal run closeout, not an owner action, and is likewise excluded.

## 4. Reachability test — edge-granular, red/green + removal sensitivity (R309, AS-3; §3.1/§3.4)

`tools/test_agent_supervisor_restart_channel.py::ReachabilitySweep` derives the `(state_from,
trigger)` EDGE set from `TRANSITIONS` and, for a given set of registered CLI handlers, computes the
string literals each handler's transitive closure (within `cli` + `restart_channel`, docstrings
stripped, constant NAMES resolved to their string values) names. An edge is covered iff SOME handler's
literals contain BOTH its source state AND its trigger. Because the shared helpers (`_locked`,
`_fire_edge`, `evaluate_preconditions`) take the state and trigger as PARAMETERS and hardcode neither,
each handler contributes only the state+trigger of the ONE edge it wires (`owner_restart` names
`HALTED`+`owner_explicit_restart`; `acknowledge_emergency_stop` names
`EMERGENCY_STOPPED`+`owner_explicit_restart`) — so a sibling that fires the same trigger from a
different source cannot stand in. Nothing is hand-listed.

**GREEN (all registered):** `python -m pytest tools/test_agent_supervisor_restart_channel.py -q`
→ `34 passed`; `uncovered_edges(all handlers) == set()`.

**Single-surface removal sensitivity (in-suite AND reproduced by driving the helpers with reduced
handler sets — no source edit; this is the exact defect G4 proved the trigger-level sweep missed):**
```
ALL registered                       -> uncovered edges: []
drop ONLY 'owner-restart'            -> uncovered: [('HALTED', 'owner_explicit_restart')]
drop ONLY 'acknowledge-emergency-stop' -> uncovered: [('EMERGENCY_STOPPED', 'owner_explicit_restart')]
drop ONLY 'resume-after-answer'      -> uncovered: [('WAIT_FOR_OWNER', 'owner_answer_validated')]
pre-fix subset (all three new dropped) -> uncovered: [('EMERGENCY_STOPPED', 'owner_explicit_restart'),
                                                      ('HALTED', 'owner_explicit_restart'),
                                                      ('WAIT_FOR_OWNER', 'owner_answer_validated')]
```
- `test_dropping_only_owner_restart_fails_the_sweep` — dropping ONLY `owner-restart` uncovers
  `(HALTED, owner_explicit_restart)` while `(EMERGENCY_STOPPED, owner_explicit_restart)` stays covered.
- `test_dropping_only_acknowledge_emergency_stop_fails_the_sweep` — the mirror.
- `test_dropping_only_resume_after_answer_fails_the_sweep` — uncovers
  `(WAIT_FOR_OWNER, owner_answer_validated)` (and NOT the held-prompt edge).
- `test_pre_fix_registration_set_is_red` — the pre-fix registration subset leaves exactly the three
  closed edges unreachable (the reproduced M0-T107 defect plus the latent third instance).
- `test_parser_registers_the_three_recovery_commands` — each new command is a real
  `cli.build_parser()` choice with a callable handler.

RED-history note: before this rework the sweep was trigger-granular; G4 empirically showed dropping
ONLY `owner-restart` left `owner_explicit_restart` reachable via the sibling (sweep stayed GREEN). The
edge-granular version above closes that R309 gap. A full-registration RED remains reproducible by
disabling `register_restart_verbs` in-tree (a producer edit; the producer is git-write-barred, so no
`git stash`): `uncovered_edges` then reports all three new edges.

## 5. Test matrix (R312) → named tests (AS-1..AS-8)

| Scenario (R312 / AS) | Named test(s) |
|---|---|
| AS-1 pre-fix live-shape journal (HALTED via `decision_halt_unsafe`, 3 denied asks in history, audit chain intact) restarts truthfully, no journal edit | `OwnerRestartHappyPath::test_AS1_live_shape_journal_restarts_truthfully` |
| AS-2 repeated invocation refuses cleanly (no 2nd transition) | `OwnerRestartHappyPath::test_AS2_repeated_invocation_refuses_cleanly` |
| AS-3 EDGE-granular reachability GREEN + per-surface removal sensitivity + parser registration | `ReachabilitySweep::*` (§4): `test_the_recovery_edge_set_is_the_expected_owner_edges`, `test_every_operator_recovery_edge_has_a_registered_cli_surface`, `test_pre_fix_registration_set_is_red`, `test_dropping_only_owner_restart_fails_the_sweep`, `test_dropping_only_acknowledge_emergency_stop_fails_the_sweep`, `test_dropping_only_resume_after_answer_fails_the_sweep`, `test_parser_registers_the_three_recovery_commands` |
| AS-4 EMERGENCY_STOPPED: ordinary refuses; stronger exits; wrong/missing token refuses; flag-set refuses; non-emergency refuses | `EmergencyStopAcknowledgment::test_AS4_*`, `test_ack_refuses_non_emergency_state` |
| AS-5 five fail-closed preconditions, each individually (+ defensive `asks_unreadable`) | `OwnerRestartPreconditions::test_AS5a_open_ask` / `_AS5b_pending_effect` / `_AS5c_surviving_child` / `_AS5d_provider_identity_drift` / `_AS5e_unsafe_recovery_classification` (+`test_recovery_unclassified_refuses`, `test_unreadable_ask_queue_refuses_never_treated_as_empty`) |
| AS-6 durable emergency-stop flag refuses (no implicit clear) | `OwnerRestartPreconditions::test_AS6_durable_emergency_stop_flag_refuses` |
| AS-7 concurrent controllers / stale runs / exactly-once | `LockContentionAndExactlyOnce::test_AS7_live_foreign_lock_refuses` / `test_AS7_exactly_once_across_sequential_invocations` / `test_AS7_stale_lock_is_taken_over_not_refused` |
| AS-8 no policy/budget/audit side effects (before/after byte-identical apart from appended records) | `NoSideEffects::test_AS8_only_state_and_trigger_keys_change` / `test_AS8_no_flag_or_budget_key_is_reset` |
| current/fresh journals; owner-answer resume; CLI wiring | `test_recovery_unclassified_refuses`, `OwnerAnswerResume::*`, `CliSurfaceEndToEnd::*` |

Audit-chain continuity (R312): AS-1/AS-4/owner-answer tests assert `verify_chain().ok` BEFORE and
AFTER; AS-8 asserts the durable state diff is exactly `{current_state, last_trigger}` and every other
key byte-identical (nothing erased, only appended).

Exactly-once (R313; §5.2): the single-instance lock is HELD across both the precondition re-check and
the transition (`_locked`), so the check-then-act window is closed. Exactly-once is proven by two
in-process tests that are a sound proxy for a true multi-process race (the CI host runs one process):
`test_AS7_exactly_once_across_sequential_invocations` calls the surface twice sequentially and asserts
exactly ONE `HALTED -> IDLE` transition (the second fails closed on `wrong_state`, state already
`IDLE`); `test_AS7_live_foreign_lock_refuses` pre-acquires the lock under a LIVE foreign pid
(`os.getppid()`) and asserts the surface refuses `lock_held` with no transition. Because the lock is
held across check+transition, a second concurrent caller cannot pass the lock while the first holds
it, so it takes the sequential/`wrong_state` path once the first releases — i.e. the two proxies
together bound both interleavings. This is NOT a claim of tested "racing invocations".

## 6. Self-check results (§8 verification contexts)

- **Clean checkout (§8.1):** run in the isolated worktree reset to the control tip; no uncommitted
  dependency, stdlib only.
- **Platform (§8.2):** Windows PC, Python 3.11.9 (the supervisor's floor). The lock/child probes use
  `os.getppid()` (live) and a non-live pid for the stale case — deterministic on Windows and POSIX.
- **Concurrency (§8.3):** live-foreign-lock and exactly-once tests (AS-7).
- **Unsafe paths (§8.4):** the five preconditions, wrong token, unreadable-ask fail-closed,
  no-emergency-provenance, recovery-unclassified.
- **Stale state (§8.5):** stale-lock takeover; the AS-1 reconstructed pre-fix live-shape journal.
- **Frozen identity (§8.8):** all evidence recorded against control tip
  `04216dd5c9f6ef415c445471abacf6d854dcd917`; a later commit re-runs it.
- **Independent final review (§8.9):** NOT self-certified — submitted for G0/G2/G3/G4/G5 by the four
  named reviewers.

Test totals (all PASS, 0 failures, control tip `04216dd`):
- `restart_channel` = **34 passed** (rework round; was 31, +3: `test_dropping_only_owner_restart_*`,
  `test_dropping_only_acknowledge_emergency_stop_*`, `test_parser_registers_the_three_recovery_commands`,
  `test_unreadable_ask_queue_refuses_never_treated_as_empty` added; the two prior union-removal tests
  and the trigger meta-test were replaced by the edge-granular equivalents).
- `restart_channel + invariants` (rework verification run) = **80 passed** (34 + 46).
- Pre-rework required minimum + golden run (`restart_channel + invariants + recovery + crash + loop +
  endurance + golden_run`) = **410 passed** in 84.72s; the +3 new restart_channel tests are additive
  and touch no other suite. Additional related sweeps, all passed: `golden_run + command_authority +
  recovery_probes + pending_prompt + operator_channel` = **248**; `loop + endurance + start_reentry +
  bounded_mode + pending_prompt + r595_actuation` = **346**. No pre-existing failure in any suite.
- `cli.DEFERRED_COMMANDS == {}` still holds (`test_agent_supervisor_endurance.py:674`).

## 7. Modularity note (CLAUDE.md principle 16; §2)

`cli.py` is grandfathered-oversized (baseline 2685; limit 2953; HEAD 2927, headroom 26). The first
draft put the handlers in `cli.py` and pushed it to 3021 → `modularity_check --check` FAILED
(`baseline_growth`). Corrected by moving ALL handler logic + argparse registration into
`restart_channel.py` behind `register_restart_verbs`, mirroring
`operator_channel_cli.register_operator_verbs`. Final: `cli.py` = **2929 SLOC** (+2 net: one import,
one register call); `restart_channel.py` = **463 SLOC** (< 600 warn). `python
tools/modularity_check.py --check` → **exit 0, failures 0, warnings 10** (all pre-existing signal
warnings; none on the new file).

## 8. Prohibitions honored (R310/R311) and Amendment-17 scope

No generic state-changing command (each surface fires ONE fixed edge, takes no target state); no
manual journal edit or migration (the AS-1 fixture drives legal transitions only; the command writes
only the transition + audit append); no policy loosening, no budget reset, no audit-history erasure
(AS-8 proves the durable diff is exactly the two transition keys). R311 preconditions each force an
individual refusal (AS-5). **Amendment 17 (R319):** this report does NOT claim continuous operability
— unit tests passing is not the live journey. The live end-to-end proof over the REAL preserved
journal (owner restart → preflight → fresh Fable rotation → Codex review → M0-T107 advancement,
R320) is the owner-typed cycle-2 act AFTER the M0-T122 frozen-identity recertification (R314/R315);
this fix invalidates the current certification and re-triggers R247 (recert = M0-T122).

## 9. Risks / limitations

- The fix touches `tools/agent_supervisor/**`, so it INVALIDATES the current certification and
  re-triggers the full R247 window (M0-T122) before the next certified start (R314; expected).
- The provider-identity live drift probe is deferred to `start` preflight by design (documented §2);
  reviewers should confirm the subsequent `start` gates `provider_cli_drift` — it does
  (`recovery_probes.probe_cli_capability_manifest`, unchanged).
- `owner_answer_validated` was a pre-existing latent defect discovered here, not introduced by
  M0-T107; closing it is authorized by R303 ("the complete reproduced F-2 defect class"). The
  reachability test would otherwise be red or gerrymandered — closing it is the honest outcome (§3.5).
- Not re-run in this session: the full whole-repo pytest and CI — those land at the frozen final
  identity in the recertification (M0-T122), per the standard R314 process.

## 10. Rework round delta (post-gate; test-only + report wording)

All three gates returned PASS; G3-F2 and G4's MEDIUM converged on an R309 gap: the reachability sweep
was TRIGGER-granular, and G4 empirically proved that dropping ONLY `owner-restart` (or ONLY
`acknowledge-emergency-stop`) left `owner_explicit_restart` reachable via the sibling — so a defined
recovery EDGE could lose its sole call site while the sweep stayed GREEN. R309 requires failure
"whenever a defined recovery edge has no command call site". Bounded rework, **test + report only —
the three shipped surfaces were NOT changed** (`git status` shows only
`tools/test_agent_supervisor_restart_channel.py` modified plus this report; `restart_channel.py`,
`cli.py`, `state_machine.py`, `recovery.py`, README, runbook all byte-unchanged in this round).

- **Sweep made EDGE-granular.** `operator_recovery_triggers()` → `operator_recovery_edges()` returns
  `(state_from, trigger)` pairs; `reachable_triggers()` → `reachable_literals()` returns ALL reachable
  string literals (no trigger intersection); new `edge_has_surface()` / `uncovered_edges()` require a
  handler whose closure names BOTH the source state AND the trigger. This works because the handlers
  hardcode `expected_from_state` and the shared helpers take state/trigger as parameters, so the AST
  walk binds surface→edge. Fully mechanical, no hand-maintained list.
- **New / renamed tests** (`ReachabilitySweep`): `test_the_recovery_edge_set_is_the_expected_owner_edges`
  (was trigger meta), `test_dropping_only_owner_restart_fails_the_sweep`,
  `test_dropping_only_acknowledge_emergency_stop_fails_the_sweep`,
  `test_dropping_only_resume_after_answer_fails_the_sweep` (replacing the two union-removal tests),
  `test_parser_registers_the_three_recovery_commands`. `test_every_operator_recovery_edge_has_a_registered_cli_surface`
  and `test_pre_fix_registration_set_is_red` kept and rewritten to edges (still green, not weakened).
  New precondition test `OwnerRestartPreconditions::test_unreadable_ask_queue_refuses_never_treated_as_empty`
  covers the `asks_unreadable` defensive branch (G4 LOW).
- **Proof the two single-surface drops now FAIL the sweep** (driving the helpers with reduced handler
  sets, §4): drop-owner-restart → `[('HALTED', 'owner_explicit_restart')]`; drop-acknowledge →
  `[('EMERGENCY_STOPPED', 'owner_explicit_restart')]`; drop-resume-after-answer →
  `[('WAIT_FOR_OWNER', 'owner_answer_validated')]`; all-registered → `[]`.
- **Counts:** `restart_channel` 31 → **34 passed**; `restart_channel + invariants` = **80 passed**
  (34 + 46). 0 failures.
- **AS-7 wording corrected** (§5): exactly-once is proven via a sequential second invocation
  (`wrong_state`) plus a live-foreign-pid lock-contention refusal (`lock_held`) with the lock held
  across check+transition — a sound proxy, NOT a claim of tested "racing invocations".
