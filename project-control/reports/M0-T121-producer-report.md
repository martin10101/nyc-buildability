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

The reachability test defines an **operator-recovery trigger** mechanically: an edge whose source is
blocking-or-terminal, whose target is NOT, and whose trigger begins with `owner_`. That yields
exactly `{owner_answer_validated, owner_approved_pending_prompt, owner_cleared_pause,
owner_explicit_restart}` — the four owner resume-into-the-live-cycle edges. Each now has exactly one
(or, for `owner_explicit_restart`, two — HALTED and EMERGENCY_STOPPED) documented callable CLI
surface. The `owner_*` edges to a terminal state (`owner_halt`, `owner_closed_stage`,
`owner_emergency_stop`) are intentionally NOT operator-recovery-resume edges: they DEEPEN a stop, are
loop-driven, and are excluded by the target-not-blocking-or-terminal rule. `COMPLETE -> IDLE`
(`run_closed`) is the internal run closeout, not an owner action, and is likewise excluded.

## 4. Reachability test — red/green + removal sensitivity (R309, AS-3; §3.1/§3.4)

`tools/test_agent_supervisor_restart_channel.py::ReachabilitySweep` derives the trigger set from
`TRANSITIONS` and, for a given set of registered CLI handlers, computes which triggers each handler's
transitive closure (within `cli` + `restart_channel`, docstrings stripped, constant NAMES resolved to
their string values) actually fires. Nothing is hand-listed.

**RED (verbatim), `register_restart_verbs(...)` temporarily disabled in `cli.py`
(`python -m pytest ...ReachabilitySweep::test_every_operator_recovery_edge_has_a_registered_cli_surface -q`):**
```
E       AssertionError: Items in the first set but not the second:
E       'owner_answer_validated'
E       'owner_explicit_restart' : operator-recovery edges with NO registered CLI surface:
        ['owner_answer_validated', 'owner_explicit_restart'] (the F-2 defect class)
1 failed in 0.49s
```
(The same RED was first observed against the earlier per-command registration design before the
modularity refactor; the mechanical result is identical because reachability is a pure function of
the registered handlers.) Because the producer is barred from git writes, RED is reproduced by
disabling the registration in-tree (a producer file edit), not by `git stash`.

**GREEN (registration restored):** `python -m pytest tools/test_agent_supervisor_restart_channel.py -q`
→ `31 passed in 4.13s`.

**Removal sensitivity (in-suite, no source edit):**
- `test_removing_resume_after_answer_unreaches_owner_answer_validated` — dropping the
  `resume-after-answer` registration from the discovered handler set removes `owner_answer_validated`
  from the reachable set (its only surface).
- `test_removing_owner_restart_and_ack_unreaches_owner_explicit_restart` — dropping BOTH
  `owner-restart` and `acknowledge-emergency-stop` removes `owner_explicit_restart` (its two surfaces).
- `test_pre_fix_registration_set_is_red` — the pre-fix registration subset leaves exactly
  `{owner_answer_validated, owner_explicit_restart}` unreachable (the reproduced defect).

## 5. Test matrix (R312) → named tests (AS-1..AS-8)

| Scenario (R312 / AS) | Named test(s) |
|---|---|
| AS-1 pre-fix live-shape journal (HALTED via `decision_halt_unsafe`, 3 denied asks in history, audit chain intact) restarts truthfully, no journal edit | `OwnerRestartHappyPath::test_AS1_live_shape_journal_restarts_truthfully` |
| AS-2 repeated invocation refuses cleanly (no 2nd transition) | `OwnerRestartHappyPath::test_AS2_repeated_invocation_refuses_cleanly` |
| AS-3 reachability RED→GREEN + removal sensitivity | `ReachabilitySweep::*` (§4) |
| AS-4 EMERGENCY_STOPPED: ordinary refuses; stronger exits; wrong/missing token refuses; flag-set refuses; non-emergency refuses | `EmergencyStopAcknowledgment::test_AS4_*`, `test_ack_refuses_non_emergency_state` |
| AS-5 five fail-closed preconditions, each individually | `OwnerRestartPreconditions::test_AS5a_open_ask` / `_AS5b_pending_effect` / `_AS5c_surviving_child` / `_AS5d_provider_identity_drift` / `_AS5e_unsafe_recovery_classification` (+`test_recovery_unclassified_refuses`) |
| AS-6 durable emergency-stop flag refuses (no implicit clear) | `OwnerRestartPreconditions::test_AS6_durable_emergency_stop_flag_refuses` |
| AS-7 concurrent controllers / stale runs / exactly-once | `LockContentionAndExactlyOnce::test_AS7_live_foreign_lock_refuses` / `test_AS7_exactly_once_across_sequential_invocations` / `test_AS7_stale_lock_is_taken_over_not_refused` |
| AS-8 no policy/budget/audit side effects (before/after byte-identical apart from appended records) | `NoSideEffects::test_AS8_only_state_and_trigger_keys_change` / `test_AS8_no_flag_or_budget_key_is_reset` |
| current/fresh journals; owner-answer resume; CLI wiring | `test_recovery_unclassified_refuses`, `OwnerAnswerResume::*`, `CliSurfaceEndToEnd::*` |

Audit-chain continuity (R312): AS-1/AS-4/owner-answer tests assert `verify_chain().ok` BEFORE and
AFTER; AS-8 asserts the durable state diff is exactly `{current_state, last_trigger}` and every other
key byte-identical (nothing erased, only appended).

Exactly-once (R313; §5.2): the transition runs under the held single-instance lock; a racing second
invocation fails closed on `lock_held`, and a sequential second invocation fails closed on
`wrong_state` — `test_AS7_exactly_once_across_sequential_invocations` asserts exactly one
`HALTED -> IDLE` transition across both calls.

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
- `restart_channel` = **31 passed**.
- Required minimum set + golden run (`restart_channel + invariants + recovery + crash + loop +
  endurance + golden_run`) = **410 passed** in 84.72s.
- Additional related sweeps, all passed: `golden_run + command_authority + recovery_probes +
  pending_prompt + operator_channel` = **248**; `loop + endurance + start_reentry + bounded_mode +
  pending_prompt + r595_actuation` = **346**; `restart_channel + invariants + recovery + golden_run +
  operator_channel + crash` = **263**. No pre-existing failure was observed in any suite.
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
