# M0-T121 — RepairRecord (H2 8-predicate gate) + red/green/removal-proof evidence

Task: M0-T121 (governance; D-024 Amendment 16 rows R303–R313). Producer:
supervisor-restart-producer. Supervisor-freeze qualifying evidence: **D-024-R302** (the reproduced
M0-T107 pre-dispatch refusal). Reliability standard sections applied: §2, §3.1/§3.4, §5, §8, §9.
Frozen identity: control tip `04216dd5c9f6ef415c445471abacf6d854dcd917`.

## 1. The defect (reproduced; named in the tests)

The S7 state machine defines owner recovery edges out of its blocking/terminal states, but three had
ZERO call sites — the pilot's F-2 class ("the edge the state machine always defined but no command
could reach"), twice fixed before (`clear-recovery` for `PAUSED_RECOVERY`, `resume-pending-prompt`
for the held-prompt `WAIT_FOR_OWNER` exit):

- **`HALTED -> IDLE` / `owner_explicit_restart`** (`state_machine.py:399`) — the reproduced defect:
  the owner-typed certified cycle-2 start refused pre-dispatch, `illegal_transition HALTED -> HALTED
  (trigger 'act')`, exit 13, 0 provider calls
  (`project-control/reports/M0-T107-cycle2-start-refusal.md`).
- **`EMERGENCY_STOPPED -> IDLE` / `owner_explicit_restart`** (`state_machine.py:397`) — the latent
  sibling named in that report.
- **`WAIT_FOR_OWNER -> PREFLIGHT` / `owner_answer_validated`** (`state_machine.py:272`) — a THIRD
  latent instance found by this task's removal-sensitive reachability sweep (fired nowhere; only in
  the table and in two `cli.py` comments noting `resume-pending-prompt` deliberately skips it).

## 2. The fix (smallest fitting change, §2)

- **NEW `restart_channel.py`**: the read-only fail-closed precondition engine
  (`evaluate_preconditions`), the three surfaces (`owner_restart`, `acknowledge_emergency_stop` —
  materially stronger, journal-token-bound — `owner_answer_resume`), the emergency-stop confirmation
  token (`emergency_ack_token`), and the thin CLI verbs + `register_restart_verbs`. Each fires ONE
  fixed edge under the single-instance lock, exactly once, and appends a durable audited
  owner-recovery event; it clears no flag, resets no budget, dispatches nothing.
- **`cli.py`**: one import + one `register_restart_verbs(sub, add_common)` call (the
  `register_operator_verbs` precedent). +2 SLOC net; no handler logic.
- **README + runbook**: the three commands, when to use each, and that leaving
  `HALTED`/`EMERGENCY_STOPPED` is an explicit audited owner act.
- NO edit to `state_machine.py` (edges already correct) or `recovery.py` (read helpers already
  present); no policy/schema/dependency change; no journal write outside the audited transition.

## 3. Red → green → removal-proof (§3.1, §3.4; R309 removal sensitivity)

**RED (verbatim), `register_restart_verbs` disabled in `cli.py`:**
`python -m pytest ...ReachabilitySweep::test_every_operator_recovery_edge_has_a_registered_cli_surface -q`
```
E   AssertionError: Items in the first set but not the second:
E   'owner_answer_validated'
E   'owner_explicit_restart' : operator-recovery edges with NO registered CLI surface:
    ['owner_answer_validated', 'owner_explicit_restart'] (the F-2 defect class)
1 failed in 0.49s
```
**GREEN:** `python -m pytest tools/test_agent_supervisor_restart_channel.py -q` → `31 passed`.
**REMOVAL-PROOF (in-suite):** dropping `resume-after-answer` unreaches `owner_answer_validated`;
dropping `owner-restart`+`acknowledge-emergency-stop` unreaches `owner_explicit_restart`; the pre-fix
registration subset leaves exactly those two unreachable. (Producer is git-write-barred, so RED is
reproduced by an in-tree registration edit, not `git stash`.)

## 4. Affected-suite evidence (control tip 04216dd)

Required minimum + golden run (`restart_channel + invariants + recovery + crash + loop + endurance +
golden_run`): **410 passed, 0 failed** (84.72s). Additional sweeps all green: `... command_authority
+ recovery_probes + pending_prompt + operator_channel` (248), `... start_reentry + bounded_mode +
r595_actuation` (346). `modularity_check --check` → **exit 0, failures 0**
(`cli.py` 2929 ≤ 2953; `restart_channel.py` 463 < 600).

## 5. H2 RepairRecord — the 8 predicates

1. **Wrapper-around-defective-path?** NO — no code path was fired before; the fix ADDS the missing
   callable surfaces the table always intended. Not a wrapper over a broken function.
2. **Stale callers?** None. `owner_explicit_restart`/`owner_answer_validated` had zero callers; the
   two existing F-2 surfaces (`clear-recovery`, `resume-pending-prompt`) are unchanged and still fire
   their own triggers (verified: they remain reachable in the GREEN sweep).
3. **Regression test fails if fix removed?** YES — the reachability sweep is RED with
   `register_restart_verbs` disabled (§3), and removal-sensitivity tests fail when a single command's
   registration is dropped. Mechanically derived, not hand-listed.
4. **Compatibility exception?** NONE — additive: three new commands + a new module; no interface
   break; `cli.py` call sites unchanged; the `register_operator_verbs` pattern preserved.
5. **Root cause vs symptom?** Root cause: unreachable table edges. Fixed at the boundary that owns
   operator-recovery surfaces (a focused module + the one CLI wire), not by loosening `assert_can_act`
   or the recovery classifier.
6. **Defect named in tests?** YES — docstrings and assertion messages cite the F-2 class, the
   reproduced M0-T107 refusal, and D-024 R303–R313; the RED message names the exact unreachable edges.
7. **Search for other instances — COMPLETE enumeration of recovery edges.** The reachability test
   derives EVERY owner recovery-resume edge from `TRANSITIONS` (source blocking-or-terminal, target
   not, trigger `owner_`): `{owner_answer_validated, owner_approved_pending_prompt, owner_cleared_pause,
   owner_explicit_restart}`. This sweep is what UNCOVERED the third instance
   (`owner_answer_validated`) beyond the two named in the packet; all four now have exactly one
   callable CLI surface (two for `owner_explicit_restart`). The `owner_*`-to-terminal edges
   (`owner_halt`, `owner_closed_stage`, `owner_emergency_stop`) and `COMPLETE -> IDLE` (`run_closed`)
   are intentionally NOT operator-recovery-resume edges and are excluded by the mechanical rule
   (producer report §3). A meta-test (`test_the_recovery_trigger_set_is_the_expected_owner_edges`)
   pins the derived set, so a future table edge forces the enumeration to be revisited.
8. **Disposition:** FIXED at root across the complete reachable class; no auto-accept — re-review by
   the four independent reviewers (code, qa, security, directive-compliance) at the frozen identity,
   then the R247 frozen-identity recertification (M0-T122) before the next certified start.
