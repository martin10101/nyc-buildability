# M0-T059 (P2) — G5 security review — VERDICT: PASS

Independent read-only security-reviewer return, preserved verbatim (transport decoding only). Reviewer did NOT
produce the code. Reviewed SHA `9c01612560d16a8019a9b0b801009791d18ed40f` (== HEAD; code deliverable clean).
Supervisor defect-only lane; qualifying evidence AD-093 §2 (reproduced fail-OPEN, M0-T053 G5 finding 5). Python 3.11.9.

## VERDICT: PASS
Correctly narrows the settle-clear from a whole-key wipe to an exact `(pid, start_token)` removal; closes the
pre-M0-T056 fail-OPEN on the no-duplicate-workers invariant (R347); no new fail-open, no cross-record erase, no
new surface, no secret/log exposure.

## Security property — "a settle clears EXACTLY its own child and NEVER another live child's record, and never
## fails to clear its own in a way that falsely blocks a legitimate later launch"
1. **Correct targeting under adversarial keys — PASS.** Predicate (recovery.py:202-207) removes only if Mapping
   AND pid matches AND start_token matches (str-coerced). (a) two children → settling pidA leaves pidB intact
   (SC1); (b) reused pid, different token → exact token equality prevents mis-clear (SC3); the settle's token
   comes from `recorded_start_token_for` = first (oldest) entry = its own token, so a later pid-reusing successor
   is protected; (c) empty/missing token → `clear(pid,"")` matches only the empty-token entry (SC / clearing test).
2. **Fail direction — PASS (fails CLOSED).** Unrecorded pid → `recorded_start_token_for` returns "" → `clear(pid,"")`
   is a strict no-op (SC2); can NEVER erase a live successor (recorded under a different pid and/or non-empty real
   start_token). Worst case = failing to clear its OWN entry (fail-closed); `account_for_children` re-derives
   liveness so a leftover stale entry does not actually block a legitimate later launch.
3. **No new fail-open re-introduced — PASS.** Grep: the old whole-key wipe exists nowhere in live code; only two
   writers of CHILD_PROCESSES_KEY (append `record_launched_child`, targeted `clear_child_record`); sole production
   caller `_settle_worker_record` still clears ONLY on verified exit (`poll() is None` + journal-None guards unchanged).
4. **No new surface / no secret — PASS.** `start_token` = non-secret process-creation stamp (Windows GetProcessTimes
   FILETIME / POSIX /proc/<pid>/stat starttime); record schema unchanged; `recorded_start_token_for` is a pure
   journal-read; `_settle_worker_record` does no logging (no log-poisoning). `int(...or 0)` mirrors the pre-existing
   idiom.

## Explicit adversarial answers
- **(a) Can ANY path erase a DIFFERENT live child's record?** **NO** — the AND-predicate requires exact
  `(pid, start_token)`; a cross-erase would need two simultaneously-live processes with identical pid AND identical
  creation stamp (impossible).
- **(b) Can it fail to clear its own record so as to falsely block a legitimate later launch?** **NO in practice** —
  the settle derives its clear token from the same durable record it removes (synchronous single-threaded settle);
  the only theoretical leftover is fail-CLOSED and `recover_boot` re-derives liveness → classified determined-gone.

## Test evidence (reproduced, Python 3.11.9, HEAD 9c01612)
- P2-SC1/SC2/SC3 + updated clearing test → 4 passed. Directly-affected files (recovery+start_reentry+runner) → 145 passed.
- Full supervisor suite `tools/test_agent_supervisor_*.py` → **1506 passed, 2 skipped, 0 failures** (freeze ≥1165
  satisfied). Producer report's 1499 predated the M0-T061 merge (+7 reviewer tests → 1506; reconciled, benign).
- Non-vacuity: revert-to-whole-key-wipe fails SC1/SC2/SC3; restore passes.

## Findings
Critical/High/Medium: none. **LOW/INFO (non-blocking, advisory):** `recorded_start_token_for` and `clear_child_record`
each do their own `get_state` read (two reads per settle). Benign under the current single-threaded settle (and a
stale read fails CLOSED). If M0-T056 ever introduces a concurrent recorder settling on the same pid, an atomic
read-modify-write (or documenting the single-writer assumption at that seam) would keep the exactly-own-clear
guarantee airtight. Advisory only; not a defect in this change — **carried forward as an M0-T056 consideration.**

## Verdict
**PASS.** Recommend orchestrator record G5 = PASS.
