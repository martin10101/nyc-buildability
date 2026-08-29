# M0-T115 — RepairRecord (H2 8-predicate gate) + red/green/revert-proof evidence — REVISED (consolidated correction round)

Task: M0-T115 (unit O; Amendment 12 rows R272/R273/R274). Producer:
fable-orchestrator-session. Supervisor-freeze qualifying evidence: **D-024-R270/R272**.
Reliability standard sections applied: §1, §2, §3.1/§3.3/§3.4, §5, §8. **This REVISION is
the one consolidated correction round after the G3 FAIL (BLOCKER-1) — it supersedes the
first-round record in place; the first-round text is git-recoverable at `91664bb`.**

## 0. Correction-round disposition (what changed and why)

- **G3 BLOCKER-1 (accepted, fixed):** a FOURTH `open_asks()` consumer —
  `loop_turnover.py` `full_turnover`'s safety feed → `turnover_seam.safety_state_from_run`
  → `approval_pending` → `rotation.assert_safe_to_rotate` — read RAW asks, so the same
  defect class would refuse the FIRST rotation seam of any pre-fix journal (including the
  live `run_M0_T107_unitJ`). Fixed in this round; predicate 7 rewritten honestly (§6).
- **No third predicate copy (standard §2.5):** the reconciliation now lives ONCE, as
  `broker.owner_unanswered_asks(journal)`; the probe and the seam feed both call it. The
  probe's round-1 inline copy was REPLACED by the helper call (behavior-preserving
  refactor). `cli.py` (forbidden path) keeps its accepted pre-existing inline copy —
  convergence noted as a follow-up, not silently done out of scope.
- **Scope extension recorded:** `loop_turnover.py` + `test_agent_supervisor_turnover_live_seam.py`
  added to allowed_paths at the G3 seam with a recorded reason (completing the reviewed
  defect class per H2 predicates 7/8 — not R272 broadening; see the task packet's
  `scope_extension_note`).
- **G4 MINOR-1 / G3 MINOR-1 / DCV NOTE (counts) corrected:** round 1 added **8** test
  functions (4 defect-named + 4 guards), not 9/5 as the round-1 narrative said. With this
  round the unit's totals are **14 new tests: 6 defect-named + 7 guards + 1 hardening**
  (plus 1 helper method and 2 small fixture classes).
- **G4 MINOR-2 corrected:** the round-1 RED used one command with two `-k` flags (pytest
  honors only the last). The RED commands are now recorded per file (§3).
- **G5 LOW-2 (accepted):** dedicated test added for the all_state-unreadable path.
- **G5 LOW-1 (declined, with reason):** switching the predicate to an explicit
  answered-status allowlist would make the probe/seam diverge from the accepted `cli.py`
  status predicate — cross-surface divergence is exactly the defect class of this unit.
  The predicate stays IDENTICAL everywhere (single source in the helper); the flagged
  shape (approval record without a status key) is unreachable in-code (only the broker
  writes `approval/*`, always with a defined status — G5's own reachability analysis).

## 1. The defect (reproduced live, named in the tests)

First live limited-auto run `run_M0_T107_unitJ` (2026-08-29): owner denied three ASK
requests via the documented `deny` command; `clear-recovery` succeeded; the identical
certified restart was then REFUSED pre-dispatch — `UNSAFE_OR_DRIFTED`, revalidation failed
`['pending_requests']`, 0 provider calls, exit 11 (`M0-T113-activation-evidence.md`
addendum). Cause, at ALL of its boundaries:

- **Write side (`broker.py`):** `deny_request` and `approve_once` set the approval record
  answered but never resolve the `ask_<request_id>` row minted by `defer` — the exact
  omission M0-T070 fixed in `revoke_all` ONLY; `revoke_all` cannot repair it afterwards
  (it skips DENIED records).
- **Read side, restart gate (`recovery_probes.py`):** `probe_pending_requests` read raw
  `journal.open_asks()` without the M0-T070 read-time reconciliation the status command
  applies (`cli.py` ~1493) — blocked every restart forever.
- **Read side, rotation seam (`loop_turnover.py`) — found by G3 in this unit's review:**
  the seam safety feed also read raw `open_asks()`, so a resumed pre-fix run would strand
  at its first rotation seam (`approval_pending` → `unsafe_seam`).

## 2. The fix (smallest fitting change, §2)

- **`broker.py`:** (a) `deny_request` / `approve_once` resolve `ask_<request_id>` on the
  SUCCESS path only (never on digest-mismatch / not-pending refusals) — the literal
  `revoke_all` pattern; rows preserved as answered history. (b) NEW module-level
  `owner_unanswered_asks(journal)` — the single shared read-time reconciliation predicate
  (broker-origin `ask_` row whose approval record exists as a dict with
  `status != PENDING_OWNER` is answered; everything else stays open; read errors
  propagate to the caller's fail-closed handling; a journal without `all_state` degrades
  conservatively to all-asks-blocking).
- **`recovery_probes.py::probe_pending_requests`:** reads through
  `owner_unanswered_asks`; ANY read failure (open_asks or all_state) →
  `pending_requests_unreadable` (never an empty queue).
- **`loop_turnover.py`:** the seam safety feed is extracted into the named
  `seam_safety_state(journal, facts)` which reads open asks through the SAME helper;
  `full_turnover` calls it. No other seam semantics changed.
- NO cli.py edit (forbidden; already correct), no policy/schema/dependency change, no
  journal write anywhere. Pre-existing unused imports (`recovery_probes.py` `json`, test
  `AuditLog`) are unused at HEAD too and remain untouched (§2.4; `tools/` is not
  lint-gated — the CI ruff job runs inside `services/api`).

## 3. Red → green → revert-proof (§3.1, §3.4; R274 removal-sensitivity)

**Round 1 (broker + probe), recorded against `8d46318` (pre-fix):**
- RED per file: `python -m pytest tools/test_agent_supervisor_command_authority.py -k
  "resolves_the_queued_ask_row or digest_mismatch_deny" -q` → the 2 resolve tests FAILED,
  digest-mismatch guard passed; `python -m pytest tools/test_agent_supervisor_recovery_probes.py
  -k "pre_fix or still_blocks" -q` → the 2 pre-fix tests FAILED, still-blocks guards
  passed. (Combined observation recorded live as "4 failed, 6 passed"; the round-1
  one-liner with two `-k` flags was inaccurate shorthand — G4 MINOR-2 — and is corrected
  here.)
- GREEN: both packs **117/117**.
- REVERT-PROOF: `git stash push broker.py recovery_probes.py` → the same 4 tests FAILED
  (4 failed, 113 deselected) → `git stash pop` → 4 passed.

**Round 2 (seam fix + helper), recorded against the committed round-1 state `91664bb`+:**
- RED: the 2 seam defect tests fail against the pre-correction module (no
  `seam_safety_state`; raw feed) — observed via `git stash push broker.py
  recovery_probes.py loop_turnover.py` → selection run → **2 failed
  (`test_a_pre_fix_denied_journal_does_not_refuse_the_rotation_seam`,
  `test_a_pre_fix_approved_journal_does_not_refuse_the_rotation_seam`), 7 passed** (the
  committed round-1 fixes keep their tests green — their removal-sensitivity is the
  recorded round-1 proof) → `git stash pop` → **9 passed**.
- GREEN: three packs (command_authority + recovery_probes + turnover_live_seam) →
  **211 passed**.

## 4. R274 path proofs — decomposition

- **deny → clear-recovery → restart, pre-fix journal:** probe-level test (exact live
  shape: unanswered `ask_*` row + DENIED record) → probe PASSES; raw row proven STILL
  unanswered afterwards (read-only; R273).
- **deny → restart, new journal:** broker test (deny resolves the row).
- **approve-once → restart, both shapes:** mirrored pair (`APPROVED_ONCE`).
- **rotation seam, both shapes (correction round):** `seam_safety_state` with pre-fix
  DENIED/APPROVED journals → `approval_pending` False (seam not refused); PENDING,
  record-less broker ask, and non-broker ask → `approval_pending` True (seam still
  refused). The seam's `execute()`-level refusal guard (`unsafe_seam`) remains covered by
  the pre-existing test.
- **Gate not weakened:** 7 guard tests total (probe: pending / no-record / non-broker /
  digest-mismatch-leaves-open; seam: pending / no-record / non-broker) + 1 hardening test
  (all_state unreadable → `pending_requests_unreadable`).
- **End-to-end live confirmation:** the real deny→clear→restart against the REAL pre-fix
  journal executes at the R276 resume after M0-T116 recertification; both live-refused
  boundaries (S11.5 probe; rotation seam) are now unit-covered with removal-sensitive
  tests.

## 5. Affected-pack evidence (correction round)

14 packs (broker, command_authority, recovery_probes, recovery, crash, start_reentry,
phase1, turnover_live_seam, turnover_integration, turnover_controller, turnover_adapters,
controller_succession, rotation, loop): **748 passed, 0 failed**.
`modularity_check --check` EXIT=0 (broker.py 785→~820 SLOC — the helper is the shared
single-source predicate for the module's own approval semantics; cohesion recorded per
rule 6). Whole-suite + CI at the ONE frozen final identity land at M0-T116.

## 6. H2 RepairRecord — the 8 predicates (revised)

1. **Wrapper-around-defective-path?** NO — the owning functions and feeds themselves
   changed; the helper replaces two would-be copies, it does not wrap them.
2. **Stale callers?** `resolve_ask` call sites: broker deny/approve (new), revoke_all
   (pattern source), operator_ask.py:357 (independent semantics, unchanged). No stale
   caller.
3. **Regression test fails if fix removed?** YES — recorded round-1 stash proof (broker +
   probe) and round-2 stash proof (seam). 
4. **Compatibility exception?** NONE (no interface break; `full_turnover` behavior
   identical except the corrected ask feed; `seam_safety_state` is additive).
5. **Root cause vs symptom?** Root cause at the write side plus read-time reconciliation
   at EVERY blocking read of `open_asks()` — the only R273-compatible way to make
   pre-fix journals truthful.
6. **Defect named in tests?** YES — docstrings cite the M0-T113 live-restart defect,
   D-024-R274, and (seam class) G3 BLOCKER-1.
7. **Search for other instances — COMPLETE enumeration of `open_asks()` consumers
   (non-test):** `durable_state.py` (definition); `cli.py:1496` status command —
   reconciles inline (pre-existing, accepted; convergence onto the shared helper is a
   noted follow-up since cli.py is a forbidden path this unit);
   `recovery_probes.py` S11.5 probe — reconciles via the shared helper (this unit);
   `loop_turnover.py` rotation-seam feed — reconciles via the shared helper (this unit,
   correction round). The round-1 record's "operator surfaces (display-only)" entry was
   wrong (operator_ask.py does not consume `open_asks()`) and is retracted. No further
   consumers exist (`grep -rn "open_asks()" tools/agent_supervisor/*.py`).
8. **Disposition:** FIXED at root across all consumers reachable in scope; no
   auto-accept — re-review by the same four independent reviewers at the corrected
   frozen identity.
