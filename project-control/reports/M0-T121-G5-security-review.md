# M0-T121 — G5 security review (VERBATIM reviewer return; saved by the orchestrator, transport entity-decoding only)

I have completed my independent verification across all seven security questions. All required suites pass (76 + 283 = 359 tests green), the diff is scope-clean, and every claimed control reproduces in source. Here is my G5 report.

---

# G5 SECURITY REVIEW REPORT — M0-T121

**Task:** M0-T121 — audited fail-closed operator recovery surfaces (F-2 class closure)
**Reviewed material identity (work commit):** `668c824`
**Control head at review:** `ab04bd9` (`git rev-parse HEAD` → `ab04bd956b4b...`) — verified
**Reviewer:** security-reviewer (read-only)
**Scope:** `tools/agent_supervisor/restart_channel.py` (new, 563 SLOC) + `cli.py` (+2 wiring lines); tests, README, runbook, reports, agent-memory.

## Verdict summary
No SEC-MAJOR or SEC-MINOR findings. Three INFO observations (all by-design or pre-existing/out-of-scope). The three recovery verbs are edge-specific, fail-closed, lock-guarded, audited, and unreachable by any automatic path. Verdict: **PASS**.

---

## Q1 — AUTHORITY: no automatic path to the three verbs

**Verified PASS.** The only call sites of `owner_restart` / `acknowledge_emergency_stop` / `owner_answer_resume` are the three CLI handlers registered by `register_restart_verbs` (`restart_channel.py:530-563`), wired into the parser at `cli.py:3429`. A repo-wide grep for the trigger literals and function names shows **no** scheduler, recovery-classifier, succession/turnover, `start`, or subagent module references them:
- `grep -rn "owner_restart\|register_restart\|restart_channel\|owner_explicit_restart\|owner_answer_validated" tools/agent_supervisor/*.py` → matches only in `restart_channel.py`, the 2 `cli.py` wiring lines, and the pre-existing transition-table rows `state_machine.py:397,399`.

Broker/worker command policy (Q1 core): a worker in-loop proposal of `python -m tools.agent_supervisor owner-restart …` is `action.kind == "command"`. In `policy.evaluate` (`policy.py:1546-1553`), a command reaches AUTO **only** via `_auto_git` (enumerated read-only git subcommands) or `_auto_test_command` (an exact shape match against the packet's closed `documented_test_commands`); everything else returns `_ask("S4.3/unclassified_command", "undocumented_command", …)`. The restart verb is neither, so it classifies **ASK, never AUTO**. `subagent` kind is independently ASK (`policy.py:1590-1593`), and `action.stated_reason` is deliberately never consulted (`policy.py:1512-1513`), so a model cannot talk its way to AUTO. This matches the frozen command-authority contract proven in `test_agent_supervisor_command_authority.py` (a documented command "still authorizes nothing else", `MAX_DOCUMENTED_TEST_COMMANDS ≤ 16`, unclassifiable→ASK).
- Verification: `python -m pytest tools/test_agent_supervisor_command_authority.py -q` (part of the 76-pass run).

**Defense-in-depth:** even in the hypothetical that an owner authored a packet whose `documented_test_commands` contained the restart verb (an owner action, not automatic), the subprocess would call `lock.acquire()` on the per-checkout `SingleInstanceLock`; while the live supervisor runs it holds that lock, so the child fails closed with `lock_held` (`restart_channel.py:441-447`; proven by `test_AS7_live_foreign_lock_refuses`).

## Q2 — EMERGENCY-STOP STRENGTH

**Verified PASS.**
- **Token derivation** (`emergency_ack_token`, `restart_channel.py:359-372`): `digest_of(provenance)[:16]` where `digest_of` = SHA-256 over canonical JSON (`models.py:64-66`), and `provenance` (`emergency_stop_provenance`, `:344-356`) is the **last recorded transition into EMERGENCY_STOPPED**: its `sequence`, `state_from`, `trigger`, `run_id`, and microsecond `committed_at_utc`. It is **not** predictable/timestamp-only/static: a script/model cannot form it without reading the live journal's recorded transition (the sequence and the microsecond commit timestamp are only knowable from the at-rest journal). An absent emergency-stop transition yields `""` and the ack fails closed `no_emergency_provenance` (`:402-408`).
- **State-bound / single-use:** the token binds to the specific incident (its sequence). After a successful ack, state→IDLE, so a replay refuses `wrong_state` (`evaluate_preconditions`, `:221-227`); re-entry to EMERGENCY_STOPPED produces a new sequence → new token. Verified: `test_AS4_correct_token_and_ack_exits_emergency`, `test_AS4_wrong_token_refuses`, `test_AS4_missing_acknowledgment_refuses`.
- **Ordinary restart genuinely refuses EMERGENCY_STOPPED in every path:** `owner_restart` fixes `expected_from_state=HALTED` (`:319-322`); `evaluate_preconditions` enforces exact `state != expected_from_state → wrong_state`. Although the state machine table *defines* both `EMERGENCY_STOPPED→IDLE` and `HALTED→IDLE` on the same `owner_explicit_restart` trigger (`state_machine.py:397,399`), the separation is enforced by the `expected_from_state` precondition, checked under the lock. Verified: `test_ordinary_restart_refuses_emergency_stopped_state`, `test_AS4_ordinary_surface_refuses_emergency_stopped` (both → `wrong_state`).
- **Durable stop FLAG refused on both surfaces:** `evaluate_preconditions` checks `flags.emergency_stop` **first** (`:213-219`), so exiting EMERGENCY_STOPPED requires a *separate* prior `stop --clear` (owner) to drop the durable flag, then the `--acknowledge-emergency-stop` flag, then the journal token — three independent gates. Verified: `test_AS6_durable_emergency_stop_flag_refuses`, `test_AS4_ack_refuses_while_emergency_flag_set` (→ `emergency_stop_flag_set`).

## Q3 — FAIL-CLOSED COMPLETENESS (R311)

**Verified PASS.** Each precondition has a check and a red-team test, all leaving state unchanged:

| R311 condition | Check (restart_channel.py) | Refusal code | Bypass test |
|---|---|---|---|
| durable emergency-stop flag | `:213-219` (`DurableFlags.read`) | `emergency_stop_flag_set` | `test_AS6…` |
| exact source state | `:221-227` | `wrong_state` | `test_AS2`, `test_ordinary_restart_refuses_emergency_stopped_state` |
| open owner asks | `:229-241` (`broker.owner_unanswered_asks`) | `open_asks` / `asks_unreadable` | `test_AS5a`, `test_owner_answer_resume_refuses_open_ask` |
| pending external effects | `:243-249` (`journal.pending_effects`) | `pending_effects` | `test_AS5b` |
| surviving/undetermined children | `:251-257` (`account_for_children`, surviving OR not determined) | `surviving_children` | `test_AS5c` |
| provider identity drift | `:187-194` | `provider_identity_drift` | `test_AS5d` |
| unsafe/absent recovery class | `:173-199` (must equal `SAFE_CHECKPOINT`) | `unsafe_recovery_classification` / `recovery_unclassified` | `test_AS5e`, `test_recovery_unclassified_refuses` |

- **TOCTOU / single-instance lock held across BOTH check and transition:** `_locked` (`:425-460`) acquires the lock, then runs `evaluate_preconditions` **and** `_fire_edge` inside the same `try`, releasing only in `finally`. A live foreign holder fails closed (`lock_held`); a stale (dead-pid) lock is honestly taken over (not spuriously refused). `_fire_edge` re-reads `_current_state` at fire time under the same held lock, so the check→act window is closed. Verified: `test_AS7_live_foreign_lock_refuses`, `test_AS7_exactly_once_across_sequential_invocations` (exactly one transition across two invocations), `test_AS7_stale_lock_is_taken_over_not_refused`.
- **Read errors fail closed, never default-open:** the owner-ask read is wrapped and a read error becomes `asks_unreadable` rather than an empty queue (`:229-235`); an unreadable/absent recovery record → `recovery_unclassified` (`:174-180`).
- **Missing journal fails closed:** a fresh/absent journal defaults to `INITIAL_STATE = IDLE` (`state_machine.py:107`), so `wrong_state` refuses. Verified: `test_cmd_owner_restart_refuses_fresh_journal` (exit 1). A corrupt SQLite DB raises at `open()` before any transition (no state change).

## Q4 — AUDIT INTEGRITY

**Verified PASS.** New events append through the shared hash-chained `AuditLog.append` (`audit_log.py:171-235`): each record carries `prev_digest` linking to the head and a `compute_record_digest` over its content; `verify_chain` (`:256-324`) detects reorder/gap (`sequence_gap_or_reorder`), duplication (`duplicate_sequence`), truncation (anchor sidecar), and content tampering (`digest_mismatch`). `append` **refuses** to extend a damaged/forked chain (`append_to_damaged_chain`, `:189-193`) — no silent rewrite, truncation, or reorder is possible.

**Exactly-once / crash ordering** (`_fire_edge`, `restart_channel.py:270-307`): `machine.transition` commits the journal transition (`record_transition`) **first**, then writes its own `state_transition` audit event; only after `transition` returns does `_fire_edge` append the first-class operator event (`operator_owner_restart` / `…ack_restart` / `…answer_resume`). Consequences:
- The operator event **can never precede** the transition it attests (append is strictly after commit) — no orphan operator record.
- A crash after commit but before an audit append leaves the transition truthful (the journal is authoritative and its transition row carries `operator_initiated=True` + `command`) with the audit chain valid-but-shorter — no duplicate, no orphan, no corruption. This is the documented journal-first crash-safety ordering (`state_machine.py:479-483`).
- A duplicate operator event is unreachable: a repeat invocation is refused at `wrong_state` before `_fire_edge`; the state-machine idempotency branch is a backstop (`:494-499`).
Verified: `test_AS1_live_shape_journal_restarts_truthfully` (chain verifies before and after; both `state_transition` and `operator_owner_restart` present; three denied asks preserved as answered history), `test_AS2` (chain intact after refused repeat), `test_AS4_correct_token_and_ack_exits_emergency` (chain ok).

## Q5 — SCOPE / SUPPLY-CHAIN

**Verified PASS (one INFO).**
- **No new dependencies:** every import in `restart_channel.py` is stdlib (`dataclasses`, `pathlib`, `sys`, `typing`) or an internal supervisor module (`:46-74`). No lockfile/manifest touched.
- **No subprocess/exec/network/permission-bypass:** `grep -nE "subprocess|os\.system|popen|socket|urllib|requests|httpx|eval\(|exec\(|--no-verify|--force|shell=True" restart_channel.py` → none.
- **No secret/token/absolute-path leakage:** scan of the new module, both report files, the runbook, and the agent-memory note for key/credential/PAT/absolute-home patterns → none. Command output is emitted through `emit_payload`, which routes payloads through `redact_structure` (`operator_channel_cli.py:48-60`). The emergency token that appears in a mismatch refusal is a digest of already-audited public transition metadata, explicitly non-secret (`restart_channel.py:366-367`).
- **INFO-1 (scope):** the commit also writes `.claude/agent-memory/backend-engineer/MEMORY.md` (+1) and `…/supervisor-cli-oversize-and-f2-reachability.md` (new), which are outside the packet `allowed_paths` and under a different agent's memory namespace than the packet's `producer_agent` ("supervisor-restart-producer"). Agent-memory is explicitly outside gate-evidence/ledger scope (`.claude/rules/project-control.md`), so this is not a security defect — noted only as a producer/identity-naming inconsistency for the orchestrator to reconcile.

## Q6 — REGRESSION

**Verified PASS.** The diff touches only: `restart_channel.py` (new), `cli.py` (+2), `README.md`, `docs/CONTROLLER_UPDATE_RUNBOOK.md`, the test file, two report files, two agent-memory files. `git diff-tree` confirms **none** of `policy.py`, `broker.py`, `run_budget.py`, `circuit_breakers.py`, `start_gate.py`, `preflight.py`, `recovery_probes.py`, `state_machine.py`, or `recovery.py` changed. Therefore policy tiers, broker approval binding, budgets, breakers, R293 shell-command discipline, and the `start` S11.5 preflight (including the live `provider_cli_drift` probe) are byte-unchanged. The transition-table edges (`state_machine.py:397,399`) pre-existed — this task adds call sites only, consistent with the F-2 premise (edges defined, no reachable command). No-side-effect proven functionally: `test_AS8_only_state_and_trigger_keys_change` (only `current_state` + `last_trigger` move; every other state key byte-identical) and `test_AS8_no_flag_or_budget_key_is_reset`. R310 "no generic state command" satisfied: each verb fires exactly one hard-coded edge — there is no arbitrary state-setter surface.

## Q7 — TEST EXECUTION

- `python -m pytest tools/test_agent_supervisor_restart_channel.py tools/test_agent_supervisor_command_authority.py -q` → **76 passed** (5.74s).
- `python -m pytest tools/test_agent_supervisor_adversarial.py tools/test_agent_supervisor_invariants.py tools/test_agent_supervisor_bounded_mode.py tools/test_agent_supervisor_bounded_contracts.py -q` → **283 passed** (22.08s).
- Reachability sweep confirmed removal-sensitive and derived mechanically from `state_machine.TRANSITIONS` (not the module's own tuple): RED pre-fix (`test_pre_fix_registration_set_is_red` leaves exactly `owner_answer_validated`, `owner_explicit_restart` unreachable), GREEN post-fix (`test_every_operator_recovery_edge_has_a_registered_cli_surface`), and per-edge deletion sensitivity (`test_removing_*`). An enumeration guard (`test_the_recovery_trigger_set_is_the_expected_owner_edges`) fails if the table gains a new owner-recovery edge.

## Additional INFO observations (non-blocking)
- **INFO-2 (by-design):** the emergency ack token is disclosed in the `confirm_token_mismatch` refusal so the operator can deliberately re-supply it. This is intentional (anti-habit/anti-default, not confidentiality) and layered behind the separately-cleared durable flag, the explicit `--acknowledge-emergency-stop` flag, and ASK-gating of any worker-proposed invocation. Not a weakness.
- **INFO-3 (pre-existing, out-of-scope):** because `StateMachine.transition` commits the journal before its audit append (frozen crash-safety ordering shared by all transition-firing commands), a pre-damaged audit chain would yield an unaudited-but-journaled transition plus an `AuditChainError` traceback rather than a typed pre-check refusal. The recovery surfaces do not pre-verify the audit chain before firing — but neither do the cited precedents (`clear-recovery`, `resume-pending-prompt`), the journal remains authoritative and truthful, and `append` still refuses silent extension. Not introduced by this task; recommend (future, non-blocking) an audit-chain `verify_chain()` pre-check in `_locked` for a cleaner typed refusal.

## Requirement coverage (in-regime spot confirmation; directive-compliance-verifier owns the authoritative pass)
R303 (three latent F-2 edges reachable) — met; R304/R310 (single edge, no flag/budget/audit side effects, no generic state command) — met (AS8); R305/R306 (distinct stronger ack; ordinary + automatic paths refuse emergency stop) — met (Q1, Q2, AS4); R311 (fail-closed preconditions) — met (Q3); R313 (exactly-once + durable audited record) — met (Q4).

---

Reproduction commands (all read-only):
```
git rev-parse HEAD
git show 668c824 --stat
git diff-tree --no-commit-id --name-only -r 668c824
python -m pytest tools/test_agent_supervisor_restart_channel.py tools/test_agent_supervisor_command_authority.py -q
python -m pytest tools/test_agent_supervisor_adversarial.py tools/test_agent_supervisor_invariants.py tools/test_agent_supervisor_bounded_mode.py tools/test_agent_supervisor_bounded_contracts.py -q
```

Relevant files (absolute):
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\restart_channel.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\cli.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\policy.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\state_machine.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\audit_log.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\recovery.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_restart_channel.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_command_authority.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M0-T121.json`

VERDICT: PASS

---

# G5 DELTA ATTESTATION (VERBATIM reviewer return; rework 668c824 -> 6432d2d; saved by the orchestrator)

Delta verified. The reworked test is a genuine hardening of the reachability sweep, not a weakening.

## DELTA ATTESTATION — M0-T121 (post-G5 rework 668c824 → 6432d2d)

**Control head:** `6432d2d` (verified via `git rev-parse HEAD`).

**(1) Scope — test-only + control-plane.** `git diff 668c824 6432d2d --stat`: the sole non-control-plane change is `tools/test_agent_supervisor_restart_channel.py` (`--numstat` = **+119/-46**, exactly as stated). Remaining entries are control-plane: gates/reports (incl. G3/G4/G5 report wording + producer report), `tasks/M0-T121.json`, `state.json`, evidence-map. Sensitive-file check `git diff 668c824 6432d2d --name-only -- restart_channel.py cli.py policy.py broker.py state_machine.py audit_log.py` returned **empty** → all six byte-unchanged. Therefore every basis of my G5 PASS (no automatic path to the verbs, emergency-token strength, R311 fail-closed preconditions, journal-first/audit-second ordering, scope/supply-chain, regression surface) is untouched by the delta.

**(2) Test-delta inspection — hardening, no masking.** The G3/G4 finding was that a *trigger-level* sweep stays GREEN if one of the two `owner_explicit_restart` edges (HALTED→IDLE vs EMERGENCY_STOPPED→IDLE) lost its sole surface while the sibling kept the trigger alive. The rework re-keys the sweep on `(state_from, trigger)` **edges** derived purely from `sm.TRANSITIONS` (`operator_recovery_edges`, restart_channel test :102-120), and `edge_has_surface` (:182-193) requires SOME single registered handler's closure to name **both** the source state AND the trigger — evaluated **per-handler, not unioned** — so a sibling firing the same trigger from a different source state "cannot stand in for a missing surface." Three new removal-sensitivity tests (`test_dropping_only_owner_restart/…_acknowledge_emergency_stop/…_resume_after_answer_fails_the_sweep`) assert the specific uncovered edge. The two grep-flagged patterns are benign: the `return True` (:192) is the legitimate positive of `edge_has_surface`; `self.journal.open_asks = _boom` (:215-217) is fault injection proving the `asks_unreadable` fail-closed path (state stays HALTED) — both strengthen, neither weakens, a refusal path. No skip/xfail/`assertTrue(True)`/mock of a production function under test was introduced.

**(3) Suite run.** `python -m pytest tools/test_agent_supervisor_restart_channel.py tools/test_agent_supervisor_command_authority.py -q` → **79 passed** (34+45) in 7.90s.

Original security verdict stands unaffected.

DELTA VERDICT: PASS
