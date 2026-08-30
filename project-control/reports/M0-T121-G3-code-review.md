# M0-T121 — G3 code review (VERBATIM reviewer return; saved by the orchestrator, transport entity-decoding only)

I have completed my independent reproduction. Compiling the G3 report.

---

# G3 CODE REVIEW REPORT — M0-T121

**Task:** M0-T121 — audited fail-closed operator recovery surfaces (F-2 class closure)
**Reviewed material identity:** work commit `668c824` (verified `git rev-parse HEAD` = `ab04bd9`; `668c824..ab04bd9` changes only control-plane evidence files — task/state/gate/evidence-map/self-check — the reviewed source tree is identical)
**Reviewer:** code-reviewer (independent, read-only)
**Scope of change:** `restart_channel.py` (NEW 463 SLOC), `cli.py` (+2), `test_agent_supervisor_restart_channel.py` (NEW), README + runbook docs; `state_machine.py`/`recovery.py`/`recovery_probes.py` untouched.

## Verification method
Every producer/orchestrator claim was re-executed, not read. Python 3.11.9 (the supervisor floor). All commands run at the current checkout.

---

## Findings

### F1 — Surface correctness & the load-bearing duplicate question — INFO (PASS)
The three surfaces fire exactly the intended legal edges per `state_machine.TRANSITIONS`:
- `owner_restart()` → `HALTED -> IDLE` on `owner_explicit_restart` (`restart_channel.py:310-322`, table `state_machine.py:399`).
- `acknowledge_emergency_stop()` → `EMERGENCY_STOPPED -> IDLE` on `owner_explicit_restart` (`restart_channel.py:375-422`, table `:397`), gated on an explicit flag AND a journal-derived token.
- `owner_answer_resume()` → `WAIT_FOR_OWNER -> PREFLIGHT` on `owner_answer_validated` (`restart_channel.py:325-341`, table `:272`).

**`resume-after-answer` is NOT a duplicate of `cmd_resume_pending_prompt`.** The existing surface (`cli.py:1891-2019`) fires `owner_approved_pending_prompt -> FORWARD_PROMPT`, and its own docstring (`cli.py:1907-1909`) states it deliberately does **not** cover `owner_answer_validated`. Grep confirms `owner_answer_validated` had **zero** firing call sites before this task — it appeared only in the TRANSITIONS table and two `cli.py` comments:
```
grep -rn "owner_answer_validated" tools/agent_supervisor/   # only: state_machine.py:272, two cli.py comments, the new module
```
So `resume-after-answer` is genuinely the missing channel for a distinct edge (different trigger, different target). R308 "exactly one surface per intended edge" holds: `owner-restart` refuses from `EMERGENCY_STOPPED` (`expected_from_state=HALTED` → `wrong_state`, test line 439-444) and `acknowledge` refuses from any non-emergency state, so each of the two `owner_explicit_restart` edges has exactly one surface.
Commands run: the two greps above; `python -m pytest tools/test_agent_supervisor_restart_channel.py -q` → `31 passed`.

### F2 — Reachability test is trigger-granular, not edge-granular — MINOR (non-blocking)
`operator_recovery_triggers()` and `reachable_triggers()` (`test_...restart_channel.py:102-167`) operate on **triggers**, but `owner_explicit_restart` backs **two** edges (HALTED→IDLE and EMERGENCY_STOPPED→IDLE). Because the trigger is shared, dropping **only** the `acknowledge-emergency-stop` registration leaves `owner_explicit_restart` reachable via `owner-restart`, so `test_every_operator_recovery_edge_has_a_registered_cli_surface` stays GREEN while the EMERGENCY_STOPPED→IDLE edge loses its sole CLI surface. I reproduced this:
```
python -c "...; kept=[fn for n,fn in h.items() if n!='acknowledge-emergency-stop']; print('owner_explicit_restart' in r.reachable_triggers(kept))"
=> True   # meta-test would NOT catch the dropped ack surface
```
Also, `CliSurfaceEndToEnd::test_cmd_acknowledge_emergency_stop_requires_token` calls the handler **function** directly, not via the parser, so it too would not fail if the ack registration were dropped. Net: R309's edge-level intent ("fails whenever a defined recovery **edge** has no command call site") is not fully enforced for the EMERGENCY_STOPPED sibling.

This is a **test-robustness gap for future regressions, not a defect in the delivered surfaces** — today the edge has its surface and works (F3, tests `test_AS4_correct_token_and_ack_exits_emergency`). It is already known/documented (G2 self-check note; evidence-map R308 explicitly calls out the trigger-vs-edge reading). **Non-blocking.** Recommended (not required for PASS): add an assertion that each `(state_from, state_to)` recovery edge — not just each trigger — has a registered surface, or assert `"acknowledge-emergency-stop"` is a registered parser choice.

### F3 — Fail-closed preconditions (R311) — PASS
`evaluate_preconditions` (`restart_channel.py:202-262`) refuses first-failure-wins in order: durable emergency-stop flag → exact source state → open owner asks → pending effects → surviving/undetermined children → recovery classification (with `provider_identity_drift` split out for `cli_capability_manifest`/`auth` failures). Each is individually forced by a dedicated test (AS-5a..e, AS-6, `test_recovery_unclassified_refuses`). The reads hit the **same reconciled surfaces**: `broker.owner_unanswered_asks` (`broker.py:741`) and `recovery.last_outcome`→`LAST_RECOVERY_KEY` (`recovery.py:539-540`, the key `recover_boot` writes at `:528`). AS-1 proves 3 **denied** asks yield `owner_unanswered_asks==0` — the M0-T115 stale-ask reconciliation is honored (denied/answered asks do not block); no stale-ask defect is resurrected. An unreadable ask queue fails closed (`asks_unreadable`, `:231-235`), never treated as empty.
Command: `python -m pytest tools/test_agent_supervisor_restart_channel.py -q` (all AS-5 tests pass).

### F4 — Emergency-stop flag discipline — INFO (PASS, stronger than the prompt's paraphrase)
The durable emergency-stop **flag** refuses **all** surfaces including `acknowledge-emergency-stop` (`test_AS4_ack_refuses_while_emergency_flag_set` → `emergency_stop_flag_set`). The operator must `stop --clear` the flag first, THEN `acknowledge-emergency-stop` moves the STATE. This is a deliberate two-key process — **stronger** than the reviewer-prompt phrasing "refuses everything except the acknowledgment verb," and consistent with AS-6 and the M0-T107 report's documented "clear-then-acknowledge" discipline (R305/R306). Importantly, the **live blocker** (HALTED via `decision_halt_unsafe`) does **not** set the emergency flag, so `owner-restart` is unaffected — AS-1 restarts the reconstructed live-shape journal successfully. The token (`emergency_ack_token`, `:359-372`) is `digest_of(provenance)[:16]` over the last transition into EMERGENCY_STOPPED and cannot be satisfied without reading the live journal (printed on mismatch, `:411-417`); wrong/missing token refuses (`test_AS4_wrong_token_refuses`, `test_AS4_missing_acknowledgment_refuses`).

### F5 — Exactly-once under lock (R313) — PASS
`_locked` (`restart_channel.py:425-460`) acquires the single-instance lock, re-checks preconditions **under** the lock, then fires the edge — closing the check-then-act window. `_fire_edge` (`:270-307`) commits the machine transition (which writes its own `state_transition` event) **first**, then appends the first-class operator-recovery event, so no recovery event exists without its transition. A live foreign holder → `lock_held` (`test_AS7_live_foreign_lock_refuses`); a stale/dead holder is taken over (`test_AS7_stale_lock_is_taken_over_not_refused`); a sequential re-invocation → `wrong_state`, with exactly one transition asserted (`test_AS7_exactly_once_across_sequential_invocations`). Verified: `168 passed` across invariants/recovery/pending_prompt/command_authority regression.

### F6 — Prohibitions (R310) — PASS
No generic state-changing capability: every surface hardcodes `state_to`/`trigger`; no CLI arg exposes a target state. No journal-edit path: the module writes only via `StateMachine.transition` + `audit.append` (no `set_state` of arbitrary keys). AS-8 (`test_AS8_only_state_and_trigger_keys_change`) asserts the durable diff is **exactly** `{current_state, last_trigger}` and every other key byte-identical; `test_AS8_no_flag_or_budget_key_is_reset` confirms a pre-set manual-pause flag survives. No policy/budget/audit erasure. The command broker/approval discipline is untouched (`cli.py` diff is one import + one register call).

### F7 — Reachability test is mechanical, removal-sensitive, principled — PASS (subject to F2)
The trigger set is derived purely from `TRANSITIONS` (`source ∈ blocking∪terminal`, `target ∉`, `trigger startswith owner_`); handlers are discovered from the built parser; reachable triggers come from an AST closure walk (docstrings stripped, constant NAMES resolved via globals) — nothing hand-listed (`OWNER_RECOVERY_TRIGGERS` in the module is explicitly documentation-only and the test never reads it, `:463-470`). I reproduced the derivation independently:
```
operator_recovery_triggers = ['owner_answer_validated','owner_approved_pending_prompt','owner_cleared_pause','owner_explicit_restart']
full set: owner_explicit_restart reachable=True, owner_answer_validated reachable=True
pre-fix subset missing = ['owner_answer_validated','owner_explicit_restart']   # the reproduced defect
```
The RED is reproduced **in-suite** (`test_pre_fix_registration_set_is_red`, GREEN because it asserts the pre-fix subset leaves exactly those two unreachable). Removal-sensitivity tests exist for `resume-after-answer` (sole surface) and the `owner-restart`+`ack` pair. Terminal exclusions (`owner_halt`/`owner_closed_stage`/`owner_emergency_stop` deepen a stop; `COMPLETE->IDLE run_closed` is internal) are excluded by the target-not-blocking/terminal + `owner_`-prefix rules — principled, not gerrymandered. `test_the_recovery_trigger_set_is_the_expected_owner_edges` pins the derived set so a future table edge forces revisiting.

### F8 — Third-edge scope extension within authorization — PASS
Closing `owner_answer_validated` is inside R303 ("the complete reproduced F-2 defect class") and inside `allowed_paths`. No diff exceeds packet scope: `state_machine.py`, `recovery.py`, `recovery_probes.py` are **unchanged** between the pre-task base and the work commit:
```
git diff 04216dd 668c824 -- tools/agent_supervisor/{recovery_probes,recovery,state_machine}.py --stat   # empty
```
The edges already existed in the table; the fix is purely the missing callable surfaces + wiring + test.

### F9 — Deferred live drift probe is documented, not silent — PASS
`recovery_probes.probe_cli_capability_manifest` and the `start` preflight are **unchanged** (F8 git diff empty). The `_recovery_classification_precondition` docstring (`restart_channel.py:148-172`) explains that the LIVE drift probe (hashing installed executables, needing a live process) is deferred to the subsequent `start`, and that this surface relies on the **recorded** SAFE_CHECKPOINT classification (which itself required `cli_capability_manifest`+`auth` to pass at the last recover_boot). This is an honest documented deferral; a drifted recorded classification is surfaced specifically as `provider_identity_drift` (`test_AS5d`).

### F10 — Code quality — PASS
Focused 463-SLOC module owning one responsibility (operator-recovery surfaces), mirroring the `operator_channel_cli.register_operator_verbs` precedent; `cli.py` stays a thin wire. Refusals are typed `RestartResult` values rendered to stderr exit 1 (`_emit_restart_result`, `:480-492`), never tracebacks; the defensive `IllegalTransitionError` catch in `_fire_edge` is honestly labeled unreachable-in-normal-use. Docstrings are accurate. `python tools/modularity_check.py --check` → exit 0, 0 failures, only pre-existing warnings (none on the new file). `cli.DEFERRED_COMMANDS == {}` holds.

### F11 — Docs honest (R319) — PASS
README/runbook additions document the three commands, the clear-flag-first two-step, and the stronger emergency ack, with **no** continuous-operability or full-autonomy claim. The live-journey proof (R320) is correctly deferred to the owner-typed cycle-2 act after M0-T122.

### F12 — Amendment-18 model identity / DCV — INFO (out of G3 scope)
R323-R326 (producer model identity) and full directive-requirement verification are the `directive-compliance-verifier`'s and orchestrator's responsibility. The evidence map records the mid-run determination (105/105 events `claude-opus-4-8`; authority D-004-R735 via checked-in frontmatter; final transcript re-read owed at accept). Not a G3 code-review concern; noted for completeness.

---

## Regression evidence (reproduced)
- `restart_channel` — **31 passed** (4.98s).
- `invariants + recovery + pending_prompt + command_authority` — **168 passed** (6.70s).
- `loop + operator_channel` — **161 passed** (102.45s).
- `modularity_check --check` → exit 0, 0 failures. `DEFERRED_COMMANDS == {}`.
No regressions observed in any suite I ran.

## Assessment
The three surfaces are correct, legal against the transition table, fail-closed on every named precondition, exactly-once under the single-instance lock, and free of any generic-state-change / journal-edit / policy-budget-audit side effect (AS-8 byte-identical). `resume-after-answer` is the genuinely-missing `owner_answer_validated` channel, not a duplicate of `resume-pending-prompt`. The reachability test is mechanical, removal-sensitive, and reproduces the reproduced defect. The unchanged probe/preflight and untouched `state_machine.py`/`recovery.py` are verified by git diff.

The single MINOR finding (F2) is a **non-blocking** test-robustness gap: the meta-test's trigger granularity cannot catch a future removal of the sole `acknowledge-emergency-stop` surface (the EMERGENCY_STOPPED→IDLE edge shares its trigger with the HALTED edge). The delivered surface is present and correct today; this is a recommendation to strengthen the removal-sensitivity assertion to edge granularity, and it is already flagged in the G2 self-check and evidence map. It does not gate acceptance of the delivered fix.

VERDICT: PASS
