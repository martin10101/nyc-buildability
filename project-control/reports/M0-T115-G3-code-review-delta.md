# G3 DELTA Re-review — M0-T115 (D-024 Amendment 12, unit O)

**DELTA VERDICT: PASS.** BLOCKER-1 from my round-1 G3 is fully and correctly resolved; MINOR-1 (counts) corrected; no new defects introduced. All prior round-1 correctness findings remain intact.

*(Orchestrator provenance note: the reviewer's transient idle-notification caption read "FAIL (predicate-7 residual)"; on the orchestrator's explicit challenge the reviewer delivered this full report, whose verdict is PASS with BLOCKER-1 marked RESOLVED. The report below is the authoritative verbatim text.)*

**Frozen identity:** `29fc1e28e1e5c56036a87689d3ded203bf11f238` — confirmed `git rev-parse HEAD` matches; `git status --porcelain` empty (clean tree).

**Delta reviewed:** `4d3760e..29fc1e2`. Code correction is in commit **`d89d740`** (not c550309 — c550309/29fc1e2 are control-plane only: gates, reports, tasks, state.json). Code files changed: `broker.py` (+35), `loop_turnover.py` (+25/-6), `recovery_probes.py` (+16/-36 refactor), `test_agent_supervisor_recovery_probes.py` (+15), `test_agent_supervisor_turnover_live_seam.py` (+63). **cli.py untouched** (forbidden path clean — `git diff 4d3760e 29fc1e2 -- cli.py` empty).

**Commands run (all read-only):**
- `git rev-parse HEAD`; `git status --porcelain`; `git log/diff --stat 4d3760e..29fc1e2`; `git show d89d740`; per-file `git diff`
- `python -c "import tools.agent_supervisor.loop_turnover, .recovery_probes, .broker"` → `IMPORT OK` (no cycle)
- `grep -rn "open_asks()"` and `"owner_unanswered_asks"` consumers across `tools/**`
- `pytest command_authority + recovery_probes + turnover_live_seam -q` → **211 passed**
- `pytest tools/test_agent_supervisor_*.py -q` → **2708 passed, 2 skipped** (full supervisor suite; the packet's 748/748 subset is within this)
- `modularity_check.py --check` → **EXIT=0**; broker.py 785→**820** SLOC, loop_turnover.py **345** SLOC

---

## BLOCKER-1 — RESOLVED (verified)

**Root cause now fixed at the 4th consumer.** `loop_turnover.full_turnover` no longer feeds RAW `open_asks()` into the seam safety state. The feed is extracted into the named `seam_safety_state(journal, facts)` (loop_turnover.py:73-88) which reads `open_asks=owner_unanswered_asks(journal)`; `full_turnover` calls it (loop_turnover.py:102). So a pre-fix journal's owner-answered (DENIED/APPROVED) but unresolved `ask_<id>` rows no longer set `approval_pending=True`, and the first rotation seam of the live `run_M0_T107_unitJ` will not be refused — while genuine PENDING and non-broker asks still refuse it.

**Single shared predicate, no third copy (reliability §2.5).** The reconciliation now lives once as `broker.owner_unanswered_asks(journal)` (broker.py:741-775). Its `_owner_answered` predicate is byte-identical in logic to my round-1 validation and to cli.py's inline copy: `ask_id.startswith("ask_")` AND `isinstance(record, dict)` AND `record.get("status") != STATUS_PENDING`. I confirmed the probe's round-1 inline copy was *replaced* by a call to the helper (recovery_probes.py:427-429) — behavior-preserving refactor, not a second implementation.

**Consumer enumeration now complete and accurate.** `grep 'open_asks()'` (non-test) at HEAD returns exactly: `broker.py:759` (the shared helper — reconciliation source) and `cli.py:1496` (status command inline copy). `loop_turnover.py` and `recovery_probes.py` no longer call `open_asks()` directly — both route through `owner_unanswered_asks`. This matches predicate-7's rewritten enumeration.

**cli.py convergence honestly deferred.** cli.py keeps its pre-existing inline copy (forbidden path this unit). I verified cli.py:1499-1503 is unchanged and its predicate is identical to the shared helper (no drift). The repair record §0/§6 notes convergence as a follow-up rather than silently doing it out of scope — correct.

**Behavior proven by tests (not implementation).** New `SeamSafetyFeedReconciliationTests` (turnover_live_seam.py) call `lt.seam_safety_state(...)` and assert `safety.approval_pending` — the exact field `rotation.assert_safe_to_rotate` refuses on: pre-fix DENIED → False; pre-fix APPROVED_ONCE → False; PENDING_OWNER → True; broker ask with no record → True; non-broker `rotation_pause/...` → True. The `MemoryJournal` fake gained `all_state()` to support reconciliation. Behavior proof at the precise boundary.

**Error handling collapsed correctly and hardened.** The helper lets `open_asks()`/`all_state()` errors propagate; `probe_pending_requests` wraps the single call so BOTH map to `pending_requests_unreadable` (fail-closed). New `test_an_unreadable_approval_state_is_not_an_empty_one` (a `HalfReadable` fake: readable `open_asks`, raising `all_state`) proves `passes=False`, `known=False`, `reason_code="pending_requests_unreadable"`. Confirms my round-1 concern is covered.

---

## MINOR-1 — RESOLVED (counts corrected, independently reconciled)

Repair record §0/§4 now states 14 new tests: 6 defect-named + 7 guards + 1 hardening (+1 helper, +2 fixture classes). I counted from the diffs and it reconciles exactly:
- Round 1 = 8: command_authority (deny-resolves, approve-resolves [2 defect]; digest-mismatch-leaves-open [1 guard]) + recovery_probes (pre-fix DENIED, pre-fix APPROVED [2 defect]; pending / no-record / non-broker still-blocks [3 guards]).
- Round 2 = 6: recovery_probes hardening [1] + turnover_live_seam (pre-fix DENIED, pre-fix APPROVED [2 defect]; pending / no-record / non-broker [3 guards]).
- Totals: 6 defect + 7 guards + 1 hardening = 14. Correct.

The §0 disclosure also honestly admits the round-1 narrative's "9/5" was wrong and the two-`-k`-flag RED command was inaccurate shorthand (now split per file). Transparent.

---

## Preserved round-1 correctness (re-confirmed intact)

The round-1 broker fix (`deny_request`/`approve_once` calling `resolve_ask("ask_<request_id>", …)` on the SUCCESS path only, after the digest-mismatch/not-pending early returns) is unchanged in this delta (broker.py:638/644/668/674) — the delta only ADDED the helper. Predicate-2 (stale callers) re-verified: `resolve_ask` sites remain broker deny/approve (new), revoke_all (source), operator_ask.py:357 (independent). No existing test weakened.

---

## INFO (non-blocking)

1. **RED / revert-proof not independently reproduced (read-only role).** §3's round-1 and round-2 stash proofs require `git stash`/tracked-file edits, which my role forbids; I did not re-run them. GREEN is directly confirmed (211 + 2708 passed), and removal-sensitivity is sound by inspection: reverting `loop_turnover.py` removes `seam_safety_state`, so the seam tests (which call `lt.seam_safety_state`) fail; reverting only the feed line breaks the two pre-fix seam tests. Consistent with my round-1 INFO-1.
2. **G5 LOW-1 decline is reasonable and its basis verified.** Keeping `record.get("status") != STATUS_PENDING` (rather than an explicit answered-status allowlist) preserves a single predicate identical to the accepted cli.py copy — switching only the helper would re-introduce the cross-surface divergence that is this unit's own defect class. I confirmed the underlying reachability claim: every `approval/*` write goes through the broker's own `_key()`/`set_state` (broker.py:335/638/668/694), always with a defined `status`, so a status-less record is unreachable in-code.
3. **Conservative-degradation nuance (benign).** For a journal fake lacking `all_state`, the helper now returns all open asks as blocking; this shifts the probe's reason_code for such fakes from `pending_requests_unreadable` (round-1 AttributeError path) to `approval_pending`. Both are fail-closed, and the real `DurableJournal` always has `all_state`, so no production behavior changes.

---

## Summary

The consolidated correction round fully addresses my BLOCKER-1: the fourth `open_asks()` consumer (the rotation-seam feed) is fixed via a single shared `broker.owner_unanswered_asks()` helper used by both the S11.5 restart probe and the seam, cli.py's forbidden-path inline copy is left identical with convergence deferred as a noted follow-up, predicate-7 is rewritten with a complete and independently-verified consumer enumeration (with the incorrect "operator surfaces" entry retracted), predicate-8's disposition holds, and MINOR-1 counts are corrected and reconcile exactly. Import graph clean, cli.py untouched, modularity EXIT=0, scope extension transparently recorded in the task packet's `scope_extension_note`, 211/2708 tests green. **DELTA VERDICT: PASS.**
