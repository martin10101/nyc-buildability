# G3 Independent Code Review — M0-T115 (D-024 Amendment 12, unit O)

**Verdict: FAIL** (one BLOCKER; the two code changes themselves are correct, the FAIL is the RepairRecord's completeness/honesty attestation plus an undisclosed, reachable same-class residual).

**Frozen review identity:** `4d3760e10aae9b0e1d074dbe95760702dc36518b` — confirmed `git rev-parse HEAD` matches; `git status --porcelain` empty (clean tree).

**Deliverable commit reviewed:** `91664bb` — `git show --stat` confirms exactly 5 files, 247 insertions, **0 deletions**: `tools/agent_supervisor/broker.py` (+15), `tools/agent_supervisor/recovery_probes.py` (+26), `tools/test_agent_supervisor_command_authority.py` (+46), `tools/test_agent_supervisor_recovery_probes.py` (+58), `project-control/reports/M0-T115-repair-record.md` (+102). **cli.py untouched** (forbidden path clean). No out-of-scope path touched.

**Commands run (all read-only):**
- `git rev-parse HEAD` / `git status --porcelain` / `git show --stat --oneline 91664bb` / `git show 91664bb -- <files>`
- `python -c "import tools.agent_supervisor.recovery_probes, tools.agent_supervisor.broker"` → `IMPORT OK` (no import cycle)
- `python -m pytest tools/test_agent_supervisor_command_authority.py tools/test_agent_supervisor_recovery_probes.py -q` → **117 passed**
- `python -m pytest` on the 7 named packs → **353 passed** (affected-pack claim confirmed)
- `python tools/modularity_check.py --check` → **EXIT=0**; broker.py = **785 SLOC** (matches repair-record claim)
- `grep resolve_ask` / `grep 'open_asks()'` consumers across `tools/**` (predicate-2 and predicate-7 verification)

---

## What is correct (would pass on its own)

1. **broker.py placement — success paths only.** `approve_once` (broker.py:610-647): the `digest_mismatch` return is at :626 and the `not_pending` return at :630, both BEFORE the new `resolve_ask` at :644 — so it fires only on the approved success path. `deny_request` (:649-678): `digest_mismatch` returns at :661 before the new `resolve_ask` at :674 (deny has no not_pending branch by pre-existing design). Correct.
2. **Ask-id shape matches.** `defer` mints `ask_{request.request_id}` (broker.py:518); `revoke_all` resolves `ask_{key[len(APPROVAL_PREFIX):]}` (:700) == `ask_{request_id}`; the two new sites use `ask_{request_id}` — identical shape. `APPROVAL_PREFIX="approval/"`, `STATUS_PENDING="PENDING_OWNER"` (broker.py:68/70).
3. **Answered, never deleted; idempotent.** `resolve_ask` (durable_state.py:673-692) is an `UPDATE … WHERE ask_id=? AND answered_at_utc=''` inside `BEGIN IMMEDIATE`; row preserved as history, returns False on a second call. The broker ignores the return (unconditional call) — safe because idempotent.
4. **Probe predicate mirrors cli.py EXACTLY.** recovery_probes.py `_owner_answered` (:446-451) returns True iff `ask_id.startswith("ask_")` AND `isinstance(record, dict)` AND `record.get("status") != STATUS_PENDING`. That is the exact complement of cli.py's "stays open" branch (cli.py:1499-1503: open when record is not a dict OR status == STATUS_PENDING). Both import the same constants from broker.py (cli.py:86-87), single source of truth. Verified case-by-case: non-broker ask → stays open; broker ask with no record → stays open; broker ask PENDING → stays open; broker ask non-PENDING (DENIED/APPROVED/REVOKED/CONSUMED/INVALIDATED) → answered/filtered. Matches cli.py.
5. **Fails closed.** Both `open_asks()` (:423-427) and the new `all_state()` read (:439-444) return `_unknown(..., "pending_requests_unreadable")` on exception; surviving open asks → `_fail(..., "approval_pending")`. New local import `from .broker import APPROVAL_PREFIX, STATUS_PENDING` is used (recovery_probes.py:450-451); no new unused import.
6. **Tests prove behavior, none weakened.** The 4 red→green tests assert persisted rows via raw SQL (`SELECT ask_id, answered_at_utc, answer FROM queued_asks`) and probe `passes`/`reason_code`/`evidence` — behavior, not implementation. Pre-fix shape (`_queue_broker_ask`) faithfully reproduces the live defect: unanswered `ask_<id>` row + a `DENIED`/`APPROVED_ONCE` `approval/<id>` record; `test_a_pre_fix_denied_request…` also asserts the raw row is STILL unanswered afterward (proves read-only R273). Diff is 0 deletions — no existing assertion was removed or loosened. GREEN independently confirmed (117 / 353 passed).
7. **Predicate 2 (stale callers) is accurate.** `resolve_ask` call sites: broker.py:644 (new), :674 (new), :699 (revoke_all source), operator_ask.py:357 (independent, separate semantics). No stale caller. Correct.

---

## BLOCKER-1 — H2 predicate-7 ("search for other instances") is materially false; an undisclosed same-class residual survives at the rotation seam

`grep 'open_asks()'` (non-test) returns **four** consumers, not three:
- `tools/agent_supervisor/cli.py:1496` — status command (reconciles) ✓
- `tools/agent_supervisor/recovery_probes.py:423` — this probe (now reconciles) ✓
- **`tools/agent_supervisor/loop_turnover.py:86`** — **omitted from the RepairRecord**
- (def in durable_state.py)

`loop_turnover.py:86` (`full_turnover`) passes `open_asks=list(loop.journal.open_asks())` — RAW, unreconciled — into `turnover_seam.safety_state_from_run`. There, `turnover_seam.py:116` computes `approval_pending=bool(len(open_asks))`, and `assert_safe_seam` → `rotation.assert_safe_to_rotate` (rotation.py:640-647) **refuses the rotation seam** whenever `approval_pending` is True (`UNSAFE_MOMENT_CHECKS` entry `("approval_pending", "an approval is still outstanding")`, rotation.py:615). This is the identical defect class the task fixes — a broker-origin ask whose owner already answered it being treated as an open question.

Consequences:
- **The claim in predicate 7 is inaccurate twice over.** It enumerates "cli status (reconciles), operator surfaces (display-only), this probe (now reconciles)". No operator surface consumes `open_asks()` — operator_ask.py uses `resolve_ask`/`ask_by_id`, not `open_asks()` — so "operator surfaces (display-only)" does not correspond to a real `open_asks()` consumer, and the one real blocking consumer (`loop_turnover.py:86`) is omitted. Predicate 8's "FIXED at root; no other instances" therefore is not established.
- **Reachable residual for the exact live journal this task must unblock.** The broker fix resolves ask rows at answer-time for *new* journals, so the seam is safe going forward. But for the **pre-fix** journal `run_M0_T107_unitJ` (the live one R276 resumes), the DENIED records already exist with unresolved `ask_<id>` rows, and R273 forbids editing that journal. `revoke_all` will not rescue them (it skips `DENIED` — it only touches PENDING/APPROVED, broker.py:690). So after the probe fix lets pre-dispatch pass, the FIRST rotation seam that run reaches will compute `approval_pending=True` from those stale rows and refuse with `unsafe_seam`/`unsafe_rotation_point`. The same read-time reconciliation the producer correctly applied to the probe was NOT applied to the seam's `open_asks` feed.

Remedy (small, producer's choice): either (a) reconcile the seam's feed the same way — reconcile in `loop_turnover.py:86` before handing `open_asks` to `safety_state_from_run` (or reconcile inside `safety_state_from_run`), with a defect-named test proving a pre-fix DENIED/APPROVED journal does not refuse the seam while a genuine PENDING ask still does; or (b) if the seam is deemed out of M0-T115's scope, correct predicate 7 to enumerate `loop_turnover.py:86`/`safety_state_from_run` honestly, open a named follow-up task, and state an explicit, checkable reason the residual is non-blocking for the live resume. As written, the RepairRecord asserts completeness it does not have.

---

## MINOR-1 — new-test / guard counts don't reconcile with the diff

The commit message says "9 new tests (4 defect-named red->green + 5 guards)" and RepairRecord §3 describes the RED run as "4 failed, **6 passed**" guard tests. The diff adds **8 test functions** — 4 red→green (`test_deny_resolves_…`, `test_approve_once_resolves_…`, `test_a_pre_fix_denied_request_…`, `test_a_pre_fix_approved_request_…`) and **4** guards (`test_a_digest_mismatch_deny_leaves_the_ask_row_open`, `test_a_broker_ask_with_a_pending_record_still_blocks`, `test_a_broker_ask_with_no_approval_record_still_blocks`, `test_a_non_broker_ask_still_blocks_regardless_of_state`) — plus 1 helper method (`_queue_broker_ask`, not a test). The §3 RED command is abbreviated (`-k "pre_fix or still_blocks …"`) and its "4 failed, 6 passed" (=10 selected) does not reconcile with the 8 visible new tests unless pre-existing tests were also selected. Not a correctness defect — GREEN (117/353) is directly confirmed and the revert-sensitivity is sound by inspection — but the stated counts are inaccurate and should be corrected.

## INFO-1 — RED / revert-proof not independently reproduced (role constraint)

RepairRecord §3's RED and revert-proof steps require `git stash` / editing tracked files, which my read-only reviewer role forbids; I did not re-run them. I confirmed GREEN directly (117 and 353 passed) and verified the revert-sensitivity logically: reverting broker.py breaks the two broker resolve tests (open_asks would be non-empty), and reverting recovery_probes.py breaks the two `pre_fix` probe tests (probe would `_fail`). The guards would hold either way. Consistent with the record's claim.

## INFO-2 — pre-existing unused imports left in place (correctly)

RepairRecord §2 discloses pre-existing unused imports (`recovery_probes.py:48 json`, a test-file `AuditLog`) and declines to touch them (no silent scope-widening; `tools/` is not lint-gated in CI). Confirmed the fix introduces no new unused import. Acceptable.

---

## Summary

The two production changes (broker answer paths resolving their `ask_<request_id>` rows; probe read-time reconciliation mirroring cli.py) are correct, minimal, fail-closed, cycle-free, well-tested, and touch no forbidden path — 117/353 green, modularity EXIT=0. **They FAIL the gate only because the RepairRecord's H2 predicate-7 completeness attestation is materially false**: a fourth `open_asks()` consumer (`loop_turnover.py:86` → `turnover_seam.safety_state_from_run` → `rotation.assert_safe_to_rotate`) makes a *blocking* rotation decision from raw `open_asks`, was not enumerated, and carries the identical defect class for pre-fix journals — including the live `run_M0_T107_unitJ` that R276 resumes, where no journal-editing path can clear the stale DENIED ask rows. Either extend the same reconciliation to the seam feed (with a defect-named test) or honestly disclose+defer it with a checkable non-blocking justification. Recommend rework/resubmit at a new frozen identity.
