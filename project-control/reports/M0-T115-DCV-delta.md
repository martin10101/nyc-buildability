# DCV DELTA Re-Verification — M0-T115 (D-024 Amendment 12, unit O) at corrected identity

**OVERALL DELTA VERDICT: PASS** — R272 DELTA PASS, R273 DELTA PASS, R274 DELTA PASS. No requirement VIOLATED or UNVERIFIABLE. My prior round-1 NOTE (test-count off by one) is now resolved and explicitly acknowledged by the producer.

**Frozen identity:** `git rev-parse HEAD` = `29fc1e28e1e5c56036a87689d3ded203bf11f238` — matches the corrected identity. Not BLOCKED.
**Applicable set (re-derived):** `ok=true`, `applicable_ids = [D-024-R272, D-024-R273, D-024-R274]`, no missing/invalid. Unchanged.
**Validator:** `python tools/validate_directive_compliance.py --check` → **EXIT=0**.
**Three packs (reproduced by me):** `pytest command_authority + recovery_probes + turnover_live_seam -q` → **211 passed in 19.14s** (matches expected 211).
**Prohibited actions — none:** task `status="awaiting_gate"` (not accepted); no accept commit for M0-T115; no live/dispatch/deploy/canary surface touched.

**Correction trace:** code correction commit `d89d740` (parent e945491 = gate-report commit); resubmit `29fc1e2`. Reviewed code/report files are byte-identical between `d89d740` and HEAD (`git diff d89d740 HEAD` over the 7 paths is empty; the 3 later commits touch only control-plane json). Verifying at HEAD == verifying the correction.

## Per-row delta table

| Row | Delta verdict | Primary evidence I reproduced |
|---|---|---|
| R272 | **PASS** | Scope extension is completion of the reviewed defect class, within extended allowed_paths, M0-T114 files untouched, no forbidden path touched |
| R273 | **PASS** | Shared helper + seam feed + probe all read-time-only; zero journal writes; fail-closed preserved |
| R274 | **PASS** | Both live-refused boundaries proven vs both journal shapes; counts corrected (14 = 6+7+1); GREEN reproduced; RED/revert-proof documented per file |

## R272 — extended scope is not broadening — DELTA PASS
- **The extension completes the SAME defect class.** The 4th `open_asks()` consumer, `loop_turnover.py` seam safety feed → `turnover_seam.safety_state_from_run` → `approval_pending`, read RAW asks (confirmed in the d89d740 diff: the removed lines fed `list(loop.journal.open_asks())`). This is the IDENTICAL "raw open_asks not reconciled" root cause named in the task objective, at its rotation-seam boundary — it would refuse the first rotation seam of any pre-fix journal (incl. the live `run_M0_T107_unitJ` that R276 resumes). It was found by the independent G3 gate via H2 predicate 7, not introduced as new work. Fixing all instances of a defect class is what the engineering-reliability standard (predicate 7) requires; R272's "do not broaden" guards against scope creep, not against finishing the reviewed defect. Judged legitimate.
- **Scope-extension note recorded** in the task packet (`scope_extension_note`), justifying loop_turnover.py + turnover_live_seam pack as predicate 7/8 completion, single shared helper (no third predicate copy), with cli.py convergence deferred as a forbidden-path follow-up.
- **Correction diff stays within the extended allowed_paths.** Cumulative code/report files across the whole span (`b180754..HEAD`): broker.py, recovery_probes.py, loop_turnover.py, test_agent_supervisor_command_authority.py, test_agent_supervisor_recovery_probes.py, test_agent_supervisor_turnover_live_seam.py, M0-T115-repair-record.md — all 7 inside the extended allowed_paths.
- **M0-T114's file set untouched** across the entire span: `grep` for telegram_sink/live_observation/golden_run/M0-T114 over `b180754..HEAD` → NONE. Tasks remain separate.
- **No forbidden path touched** (cli.py, project_control.py, directive_registry.py, validate_directive_compliance.py, .claude/apps/packages/services/supabase) → NONE. cli.py keeps its pre-existing accepted inline reconciliation; convergence noted as follow-up.

## R273 — read-time only, no journal edit — DELTA PASS
- **New `broker.owner_unanswered_asks(journal)`** (broker.py diff): reads `journal.open_asks()` + `journal.all_state()`, filters in memory, returns a list. No writes. Read errors propagate (caller fail-closed); a journal lacking `all_state` degrades conservatively to all-asks-blocking.
- **`loop_turnover.seam_safety_state(journal, facts)`**: reads `pending_effects()` + `owner_unanswered_asks(journal)` and passes them into `ts.safety_state_from_run(...)` (pure computation). No journal write; the diff only swaps the raw feed for the reconciled one.
- **`probe_pending_requests`** now reads through the helper; any read failure → `pending_requests_unreadable` (never an empty queue). Fail-closed preserved.
- **Read-only proof retained**: the round-1 probe test still asserts the raw pre-fix ask row is unchanged after the probe passes.
- **No production journal-editing tooling** in the span. The only `set_state` calls in `tools/` are (a) test fixtures writing `approval/<id>` records into an in-memory MemoryJournal to build the pre-fix shape, and (b) the pre-existing broker approval-record write — neither edits the durable runtime journal at %LOCALAPPDATA%. The one raw-needle hit (NYCBuildabilitySupervisor/LOCALAPPDATA) is literal prose inside my own committed round-1 DCV report, not code.

## R274 — path proofs vs both boundaries × both journal shapes — DELTA PASS
- **S11.5 restart probe (boundary 1):** deny→restart and approve-once→restart, new + pre-fix journals — 4 defect tests (round 1), incl. the read-only proof.
- **Rotation-seam feed (boundary 2, the newly covered live-refused path):** `SeamSafetyFeedReconciliationTests` — `test_a_pre_fix_denied_journal_does_not_refuse_the_rotation_seam` and `..._approved_...` assert `approval_pending` is False against pre-fix DENIED/APPROVED_ONCE journals; 3 seam guards (`_a_pending_request_still_refuses`, `_no_record_still_refuses`, `_non_broker_ask_still_refuses`) assert it stays True. I read all five.
- **Counts corrected and reconciled exactly:** 6 defect (4 probe + 2 seam) + 7 guards (4 probe incl. digest-mismatch + 3 seam) + 1 hardening (all_state-unreadable) = **14 new tests**. Matches the producer's corrected figure and resolves my round-1 off-by-one, which repair-record §0 explicitly acknowledges ("round 1 added 8 test functions … not 9/5").
- **GREEN reproduced by me:** 211 passed.
- **RED + revert-proof:** repair-record §3 records RED per file (correcting the round-1 two-`-k`-flag inaccuracy, G4 MINOR-2) and both round-1 (broker+probe stash → 4 fail) and round-2 (seam stash → 2 fail) proofs with exact commands. I did NOT re-execute the stash (read-only mandate); removal-sensitivity is independently confirmed by code inspection — the pre-correction `loop_turnover` fed raw `open_asks()` and `seam_safety_state` did not exist, so the seam defect tests deterministically fail if the fix is removed, consistent with the recorded RED.
- **Predicate-7 enumeration complete + honest retraction:** §6 enumerates every non-test `open_asks()` consumer (durable_state definition, cli.py status inline, probe, seam) and retracts the round-1 wrong "operator surfaces (display-only)" claim (operator_ask.py does not consume open_asks). Honest, not a hidden gap.
- **Residual honestly disclosed:** real end-to-end deny→clear→restart and rotation seam against the REAL pre-fix journal run at the R276 resume after M0-T116 recert; both live-refused boundaries are now unit-covered with removal-sensitive tests.

## Exact commands run
- `git rev-parse HEAD`; `evaluate_task_refs(M0-T115.json)`
- `git show --stat c550309 / e945491 / d89d740`; `git show d89d740 -- broker.py recovery_probes.py loop_turnover.py <test packs>`
- `git diff --name-only b180754 HEAD` (scope) + grep for M0-T114 / forbidden paths
- `git diff --stat d89d740 HEAD -- <7 reviewed paths>` (empty = identical); `git diff --name-only d89d740 HEAD`
- `pytest tools/test_agent_supervisor_command_authority.py tools/test_agent_supervisor_recovery_probes.py tools/test_agent_supervisor_turnover_live_seam.py -q` → 211 passed
- `python tools/validate_directive_compliance.py --check` → EXIT=0
- journal-edit needle scan over `b180754..HEAD` (only report-prose + in-memory test fixtures; no production journal edits)

**All three rows DELTA PASS. Overall: PASS.**
