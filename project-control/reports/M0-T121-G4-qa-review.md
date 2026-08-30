# M0-T121 — G4 QA review (VERBATIM reviewer return; saved by the orchestrator, transport entity-decoding only)

All verification complete. Here is my G4 QA gate report.

---

# G4 QA Gate Report — M0-T121

**Task:** M0-T121 — Restart-channel defect fix: audited fail-closed operator recovery surfaces (HALTED/EMERGENCY_STOPPED/WAIT_FOR_OWNER) + F-2 edge-reachability closure
**Gate:** G4 (independent QA)
**Reviewer:** qa-engineer (read-only)
**Reviewed material identity:** work commit `668c824` (ancestor of control head `ab04bd9`)
**Checkout used:** `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` (control head `ab04bd9`)

## 0. Identity / reproduction integrity

- My worktree is at `d8b3899` (a different branch); I ran the code in the ctl24 checkout as instructed.
- `git diff --stat 668c824 ab04bd9` shows **only control-plane files** changed between the reviewed commit and control head (`M0-T121-G2.json`, G2 self-check, evidence-map, `state.json`, `M0-T121.json`). **No tool/test source changed** — `git diff 668c824 ab04bd9 -- restart_channel.py test_...restart_channel.py cli.py state_machine.py recovery.py` is empty.
- Confirmed ctl24 working files are **content-identical** (line-endings normalized) to the reviewed `668c824` blobs via SHA-256:
  - restart_channel.py: `f0a0b714…f646be` (reviewed) == `f0a0b714…f646be` (ctl24)
  - test file: `625c1784…a74cc3` == `625c1784…a74cc3`
  - cli.py: `64727539…37de8` == `64727539…37de8`
- The only difference is CRLF (Windows checkout) vs LF (git blob) — that IS the real runtime line-ending, so tests run at the reviewed identity.

## 1. Test reproduction (I ran these; not trusting the report)

Environment: `Python 3.11.9, pytest-8.4.2` (the supervisor's declared floor).

**New suite:**
```
python -m pytest tools/test_agent_supervisor_restart_channel.py -q
31 passed in 4.20s
```

**Producer's required minimum set (expected 410):**
```
python -m pytest tools/test_agent_supervisor_restart_channel.py \
  tools/test_agent_supervisor_invariants.py tools/test_agent_supervisor_recovery.py \
  tools/test_agent_supervisor_crash.py tools/test_agent_supervisor_loop.py \
  tools/test_agent_supervisor_endurance.py tools/test_agent_supervisor_golden_run.py -q
410 passed in 53.75s
```

Both counts match the producer report exactly. **No failures.**

**Modularity** (handwritten production source changed):
```
python tools/modularity_check.py --check
selected 329 files; failures 0; warnings 10
```
All 10 warnings are pre-existing signal warnings on other files; **none on `restart_channel.py`** (563 lines / 463 SLOC, under the 600 warn threshold). cli.py grew +2 lines (import + `register_restart_verbs` call) — confirmed via `git show --stat 668c824` (`cli.py | 2 ++`).

## 2. Flakiness (requirement 7)

Second run of the new suite:
```
python -m pytest tools/test_agent_supervisor_restart_channel.py -q -p no:randomly
31 passed in 4.48s
```
No nondeterminism observed across two runs (31/31 both). Tests use isolated `TemporaryDirectory` journals and deterministic pids (`os.getpid()`/`os.getppid()` for live, fixed large ints for stale). No shared runtime dir, no network, no provider.

## 3. AS-1..AS-8 adequacy (I read every test body)

| AS | Named test(s) | Genuinely verifies? | Notes |
|---|---|---|---|
| AS-1 | `OwnerRestartHappyPath::test_AS1_live_shape_journal_restarts_truthfully` | **YES** | Reconstructs HALTED via `decision_halt_unsafe`, adds 3 real denied asks (broker.defer→deny_request→`owner_denied`), records SAFE_CHECKPOINT via real `recover_boot`. Asserts exactly one HALTED→IDLE transition, durable `operator_owner_restart` + `state_transition` events, and 0 remaining unanswered asks. **Audit chain verified cryptographically via `verify_chain().ok` BEFORE (l.334) AND AFTER (l.345)** — not by count. |
| AS-2 | `test_AS2_repeated_invocation_refuses_cleanly` | **YES** | Second call refuses `wrong_state`, transition count unchanged, chain still verifies. |
| AS-3 | `ReachabilitySweep::*` (5 tests) | **YES, with a boundary** (see §4/§7) | Mechanical, table-derived, removal-sensitive. |
| AS-4 | `EmergencyStopAcknowledgment::*` (7) | **YES** | Ordinary surface refuses EMERGENCY (`wrong_state`); missing ack → `acknowledgment_required`; wrong token → `confirm_token_mismatch`; correct flag+token → one EMERGENCY→IDLE transition + chain verifies; flag-set refuses; non-emergency refuses. |
| AS-5 | `OwnerRestartPreconditions::test_AS5a..e` (+`recovery_unclassified`) | **YES** | Each of the 5 preconditions individually forces its typed refusal (`open_asks`, `pending_effects`, `surviving_children`, `provider_identity_drift`, `unsafe_recovery_classification`), state stays HALTED. |
| AS-6 | `test_AS6_durable_emergency_stop_flag_refuses` | **YES** | Flag set → `emergency_stop_flag_set`; asserts flag **not** cleared by the refusal. |
| AS-7 | `LockContentionAndExactlyOnce::*` (3) | **PARTIAL** — see §5 | Foreign live-pid lock → `lock_held`; sequential exactly-once; stale lock taken over. **No true concurrent race.** |
| AS-8 | `NoSideEffects::*` (2) | **YES** | `all_state()` snapshot BEFORE/AFTER: only `{current_state, last_trigger}` change, every other key byte-identical; separately proves a set `manual_pause` flag survives. |

**AS-1 fidelity note (LOW):** the reconstructed journal reaches HALTED by the *minimal legal path* — **9** transitions, not the live journal's stated **13**. The load-bearing defect properties (HALTED-via-`decision_halt_unsafe`, 3 denied/resolved asks in history, SAFE_CHECKPOINT classification, intact chain) are all faithfully reproduced. The exact transition count is immaterial to the restart surface (it keys off current state = HALTED + the precondition set), so this does not weaken the proof.

**AS-8 audit note:** AS-8 snapshots durable **state** (covers policy tiers, budgets, counters, flags, ask records — all stored as journal state keys). Audit-log continuity before/after is covered in AS-1/AS-4 via `verify_chain().ok`; the two together satisfy "policy/budget/audit before AND after." Adequate.

## 4. Removal sensitivity — mechanism verified without editing files (requirement 4)

The sweep discovers handlers from the **real** `cli.build_parser()` (so the +2-line cli.py wiring is live-exercised), then AST-walks each handler's source (docstrings stripped), collecting string constants and resolving `Name` nodes to their module-global string/callable values, descending into callables in `{cli, restart_channel}`. Nothing is hand-listed.

I proved removal sensitivity **without any file edit** by driving the test's own helpers with reduced handler sets (`scratchpad/probe_reach.py`, run in ctl24):
```
operator_recovery_triggers: ['owner_answer_validated','owner_approved_pending_prompt','owner_cleared_pause','owner_explicit_restart']
has owner-restart / acknowledge-emergency-stop / resume-after-answer registered: True / True / True
reachable (full set): all 4  (GREEN)
drop resume-after-answer            -> owner_answer_validated reachable? False   (caught)
drop ONLY owner-restart             -> owner_explicit_restart reachable? True    (NOT caught)
drop ONLY acknowledge-emergency-stop-> owner_explicit_restart reachable? True    (NOT caught)
drop BOTH                            -> owner_explicit_restart reachable? False  (caught)
```
`test_the_recovery_trigger_set_is_the_expected_owner_edges` guards the derivation itself; `test_pre_fix_registration_set_is_red` bakes the RED condition permanently (asserts the pre-fix registration subset leaves exactly `{owner_answer_validated, owner_explicit_restart}` unreachable). Both passed in my run:
```
ReachabilitySweep::test_every_operator_recovery_edge_has_a_registered_cli_surface PASSED
ReachabilitySweep::test_pre_fix_registration_set_is_red PASSED
ReachabilitySweep::test_removing_owner_restart_and_ack_unreaches_owner_explicit_restart PASSED
ReachabilitySweep::test_removing_resume_after_answer_unreaches_owner_answer_validated PASSED
ReachabilitySweep::test_the_recovery_trigger_set_is_the_expected_owner_edges PASSED
```

## 5. AS-7: is it a real race? (requirement 2)

**No — there is no concurrent execution in the suite.** `test_AS7_exactly_once_across_sequential_invocations` calls `owner_restart` twice **sequentially** (single-threaded); the second refuses `wrong_state`, and it asserts exactly one HALTED→IDLE transition. `test_AS7_live_foreign_lock_refuses` acquires the `SingleInstanceLock` under a **live, different pid** (`getppid()`) and asserts `owner_restart` refuses `lock_held`. Exactly-once under true concurrency is therefore verified **by proxy**, not by two racing threads/processes:
- the file lock is the real concurrency primitive, and it IS independently exercised (a genuinely-alive foreign holder is rejected);
- `_locked` holds the lock across the precondition re-check **and** the transition (l.443–456), and the `wrong_state` precondition is the serialization backstop after the first transition.

This proxy is sound (the lock's liveness-detection is real), but the report/evidence-map wording "racing invocations / under race" overstates it. **LOW-MEDIUM** — see §7.

## 6. R312 matrix completeness (requirement 3)

| R312 matrix item | Named test | Verdict |
|---|---|---|
| Pre-fix journals (live shape) | `test_AS1_live_shape_journal_restarts_truthfully` | Covered |
| Current / fresh journals | `test_cmd_owner_restart_refuses_fresh_journal`, `OwnerAnswerResume::*` | Covered |
| Repeated invocation | `test_AS2_repeated_invocation_refuses_cleanly` | Covered |
| Stale runs | `test_AS7_stale_lock_is_taken_over_not_refused` | Covered |
| Concurrent controllers | `test_AS7_live_foreign_lock_refuses` | Covered (proxy, §5) |
| Emergency-stop recovery | `EmergencyStopAcknowledgment::*` | Covered |
| Audit-chain continuity | `verify_chain().ok` before/after in AS-1/AS-2/AS-4/owner-answer | Covered — **cryptographic**, not count-based |
| Removal sensitivity | `ReachabilitySweep::test_removing_*`, `test_pre_fix_registration_set_is_red` | Covered (boundary in §7) |

No matrix item is covered only nominally, except the "concurrent controllers" row is a lock-contention proxy rather than a true concurrent race (§5).

## 7. Coverage gaps (severity-ranked)

- **MEDIUM — trigger-level (not edge-level) reachability blind spot.** R309/AS-3 are worded at EDGE granularity ("a defined recovery *edge* has no command call site"), but the sweep keys on the bare **trigger**. `owner_explicit_restart` backs two edges (HALTED and EMERGENCY_STOPPED); I empirically confirmed (§4) that deleting *only* `owner-restart` (or *only* `acknowledge-emergency-stop`) leaves the trigger reachable via the sibling, so the GREEN test would **not** catch that regression — which would re-open F-2 for one state. The `cmd_*` end-to-end tests call handlers directly (bypassing argparse), so they don't guard registration either. **Mitigations:** the whole-`register_restart_verbs` wiring removal IS caught; single-surface edges (`resume-after-answer`, and pre-existing `clear-recovery`/`resume-pending-prompt`) ARE caught; both shared edges are proven reachable+correct by functional tests; the producer report §3/§4 discloses the two-surface case and requires both dropped in the removal test. **Recommended hardening (not a current-state defect):** assert reachability at `(state_from, trigger)` granularity, or assert the specific verb names are present in `build_parser()`. I defer to the directive-compliance-verifier on whether trigger-level satisfies R309's literal edge wording.
- **LOW-MEDIUM — no true concurrent race (§5).** Exactly-once is proven via sequential calls + a foreign-lock-held refusal, not two racing threads. Acceptable because the lock primitive is independently exercised, but "race" language overstates; a real threaded race would strengthen it.
- **LOW — untested defensive branches.** `asks_unreadable` (the `except` in `_open_owner_asks`) and `illegal_transition` (the defensive `except` in `_fire_edge`) have no test. Both are fail-closed defensive paths; `illegal_transition` is unreachable-by-design given the `wrong_state` precondition.
- **LOW — asymmetric per-surface precondition matrix.** The full 5-precondition set is exercised only against the HALTED (`owner_restart`) surface; `resume-after-answer` tests only `open_asks`, and the ack surface tests only flag/token/state. Justified: all three surfaces call the *shared* `evaluate_preconditions` via `_locked`, so the guard is exercised once for all. `wrong_state` is likewise not enumerated from every source state (trivial string equality).
- **OBSERVATION (out of G4 scope) — freeze baseline.** `.claude/rules/supervisor-freeze.md` §4 requires re-establishing the ≥1165-test suite baseline. The producer ran 410 + additional sweeps (248/346/263) but deferred the whole-repo/CI run to the M0-T122 recertification (per standard R314). The G3 reviewer / orchestrator should confirm the ≥1165 baseline; not a G4 QA blocker.

## 8. Mutation-proof quality (requirement 6)

The RED in the producer report names **both** missing triggers (`owner_answer_validated`, `owner_explicit_restart`) and matches the F-2 defect class. It is stronger than a one-time observation: the RED condition is **permanently encoded** as `test_pre_fix_registration_set_is_red` (computationally reconstructs the pre-fix registration subset and asserts exactly those two are unreachable) and passed in my run, alongside the GREEN `test_every_operator_recovery_edge_has_a_registered_cli_surface`. The red/green pair is convincing under the engineering-reliability standard for the realistic regression (forgetting to register a recovery edge's surface, or dropping the wiring). Its one limitation is the shared-trigger single-edge case in §7.

## 9. Verdict rationale

All required suites reproduce exactly at the reviewed identity (31; 410), zero failures, no flakiness, modularity clean. AS-1..AS-8 genuinely (not nominally) verify their scenarios — audit continuity is cryptographic, preconditions each individually force typed refusals, the emergency-stop acknowledgment is genuinely stronger (explicit flag + journal-derived token), and no-side-effects is proven by a before/after byte-level snapshot. The reachability test is mechanical, table-derived, and demonstrably removal-sensitive. The single MEDIUM finding is a **future-regression-detection** sensitivity limitation for a narrow shared-trigger mutation — disclosed, functionally mitigated, and not a defect in the delivered behavior (every recovery edge is reachable and correct today). It is recorded as recommended hardening and flagged for the directive-compliance-verifier's R309 literal-wording assessment; it does not warrant a QA FAIL.

VERDICT: PASS

---

# G4 DELTA ATTESTATION (VERBATIM reviewer return; rework 668c824 -> 6432d2d; saved by the orchestrator)

All delta verifications reproduced. Here is my delta attestation.

---

## G4 QA Delta Attestation — M0-T121 (bounded test-only rework)

**Reviewed delta identity:** control head `6432d2d` (`668c824` is its ancestor)
**Checkout:** `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` (test file content-hash matches `6432d2d` blob: `a91c0343…6bd8bf`)

**Scope confirmed (read-only):** `git diff --stat 668c824 6432d2d -- tools/` = **only** `test_agent_supervisor_restart_channel.py` (+119/-46). `git diff 668c824 6432d2d --` over `restart_channel.py`/`cli.py`/`state_machine.py`/`recovery.py` is **empty** — production byte-unchanged, so my prior 410-min-set and modularity PASS carry over unchanged.

**(1) §4 empirical probe, NEW edge-granular helpers** (`(state_from,trigger)` pairs; `edge_has_surface` requires ONE handler's closure to name both state and trigger):
```
operator_recovery_edges: [(EMERGENCY_STOPPED,owner_explicit_restart),(HALTED,owner_explicit_restart),
                          (PAUSED_RECOVERY,owner_cleared_pause),(WAIT_FOR_OWNER,owner_answer_validated),
                          (WAIT_FOR_OWNER,owner_approved_pending_prompt)]
ALL registered            -> uncovered: []                                    (GREEN)
drop ONLY owner-restart   -> uncovered: [(HALTED, owner_explicit_restart)]     (now FAILS — was the blind spot)
drop ONLY acknowledge     -> uncovered: [(EMERGENCY_STOPPED, owner_explicit_restart)]  (now FAILS)
drop ONLY resume-after-answer -> uncovered: [(WAIT_FOR_OWNER, owner_answer_validated)]
drop all three            -> uncovered: all three new edges
```
The §7 MEDIUM is genuinely closed: dropping a single shared-trigger surface now leaves its edge uncovered, and — critically — does **not** spuriously uncover the sibling edge, proving the per-handler attribution is sound (shared helpers take state/trigger as parameters and leak no source-state constant across closures).

**(2) Suite twice:** `34 passed in 6.82s` / `34 passed in 6.65s` — matches expected 34, no flakiness.

**(3) New test bodies are genuine, not nominal:**
- `test_dropping_only_owner_restart_fails_the_sweep` / `_acknowledge_emergency_stop_` / `_resume_after_answer_`: each asserts the dropped edge is in `uncovered` AND the shared-trigger sibling stays covered — precise, matches my probe.
- `test_parser_registers_the_three_recovery_commands`: asserts all three verbs are choices on `build_parser()` with callable handlers — closes the "cmd_* tests bypass registration" gap.
- `test_unreadable_ask_queue_refuses_never_treated_as_empty`: monkeypatches `journal.open_asks` to raise `RuntimeError`, asserts `asks_unreadable` and state stays HALTED — genuinely forces the defensive branch fail-closed (passes only because `owner_unanswered_asks` really reads `open_asks`).

**(4) Report wording fixed:** producer report §5 and new §10 accurately describe exactly-once as a lock-held-across-check+transition proxy (sequential `wrong_state` + live-foreign-pid `lock_held`) and state explicitly "This is NOT a claim of tested 'racing invocations'." Overstatement resolved.

**Freeze baseline:** noted — orchestrator's full supervisor-suite run 2811 passed / 2 skipped / 0 failures (≥1165) covers my prior observation.

The bounded rework addresses both of my raised findings without altering shipped behavior; the R309 edge-granularity requirement is now met and empirically demonstrated.

DELTA VERDICT: PASS
