# G4 QA DELTA Re-Review — M0-T115 (correction round)

**DELTA VERDICT: PASS** (my prior MINOR-1 and MINOR-2 resolved; G3 BLOCKER-1 independently confirmed fixed; no new findings)
**Corrected frozen identity:** `29fc1e28e1e5c56036a87689d3ded203bf11f238` — HEAD verified, `git status --porcelain` clean. Correction control commit `c550309`; delta range `4d3760e..29fc1e2`.
**Reviewer:** qa-engineer (independent; read-only). This is a delta against my first-round PASS at `4d3760e`.

## Command table (exact observed results)

| # | Command | Expected | Observed |
|---|---------|----------|----------|
| 0 | `git rev-parse HEAD` / `git status --porcelain` | frozen SHA, clean | `29fc1e28e1e5…`, clean (empty) |
| 1 | `pytest command_authority + recovery_probes + turnover_live_seam -q` | 211 passed | **211 passed in 21.99s** |
| 2 | 14-pack affected sweep `-q` | 748 passed | **748 passed in 70.82s** |
| 3 | `git diff 4d3760e..29fc1e2 --name-only` (non-`project-control/`) | only extended allowed_paths | broker.py, loop_turnover.py, recovery_probes.py, test_recovery_probes.py, test_turnover_live_seam.py — **all in scope** |
| 4 | content-deletion lines in the two test files | none | **none** (additions only) |
| 5 | new `def test_` in turnover_live_seam delta | 5 seam tests | **5** (2 defect + 3 guard) |
| 6 | `grep open_asks() tools/agent_supervisor/*.py` | probe+seam via helper; cli inline only | **confirmed** (raw readers: helper body + cli.py:1496 only) |
| 7 | `python tools/modularity_check.py --check` | EXIT=0 | **EXIT=0** |

The 14-pack sweep (command #2) covered: broker, command_authority, recovery_probes, recovery, crash, start_reentry, phase1, turnover_live_seam, turnover_integration, turnover_controller, turnover_adapters, controller_succession, rotation, loop.

## Verification of each correction

**G3 BLOCKER-1 — rotation-seam feed (the fourth `open_asks()` consumer) — FIXED, independently confirmed.**
`full_turnover` previously computed its safety feed from raw `open_asks()` (I confirmed this in the pre-correction diff), so a resumed pre-fix journal would strand at its first rotation seam (`approval_pending` → `unsafe_seam`) — the same defect class as the live restart refusal. The fix extracts the feed into the new named `loop_turnover.seam_safety_state(journal, facts)`, which reads through `broker.owner_unanswered_asks(journal)`. I verified removal-sensitivity independently of the producer's stash: `turnover_seam.safety_state_from_run` derives `approval_pending=bool(len(open_asks))` (line 116), so a raw (unreconciled) feed on the pre-fix DENIED/APPROVED shapes yields `approval_pending True` and the two seam defect tests (`assertFalse`) would fail. The 5 new `SeamSafetyFeedReconciliationTests` cover both fixed shapes (denied/approved → not refused, reusing live ids `9f45b2ca`/`c73f9247`) and all three guards (pending `7e4b33d8`, no-record, non-broker → still refused).

**Shared-helper refactor — behavior-preserving.** `broker.owner_unanswered_asks` carries the byte-identical `_owner_answered` predicate I validated in round 1 (still an exact mirror of the cli.py status reconciliation). `probe_pending_requests` now delegates to it; for a real `DurableJournal` (has `all_state`) the reconciliation path is unchanged. Read errors propagate to the caller's fail-closed handling; a fake journal lacking `all_state` degrades conservatively to all-asks-blocking (safe; only affects reduced test fakes). No `full_turnover` semantics changed beyond the corrected feed.

**MINOR-1 (my round-1 finding) — corrected.** The true tally is now recorded and reconciles against the actual test functions: **14 new tests = 6 defect-named** (broker deny/approve-once; probe pre-fix denied/approved; seam pre-fix denied/approved) **+ 7 guards** (probe: pending/no-record/non-broker/digest-mismatch-leaves-open; seam: pending/no-record/non-broker) **+ 1 hardening** (all_state-unreadable). Confirmed exact.

**MINOR-2 (my round-1 finding) — corrected.** Repair-record §3 now records the RED per file (two separate single-`-k` invocations) and explicitly labels the round-1 two-`-k` one-liner as inaccurate shorthand. Reproducible as written.

**G5 LOW-2 — added and verified.** `test_an_unreadable_approval_state_is_not_an_empty_one` drives a journal whose `open_asks()` is readable but `all_state()` raises; the exception propagates out of the helper and the probe returns `passes=False, known=False, reason_code="pending_requests_unreadable"`. Fail-closed confirmed.

**§7 consumer enumeration — complete and honest.** I independently ran `grep open_asks() tools/agent_supervisor/*.py`: the only raw readers are the helper's own body and `cli.py:1496` (status command, pre-existing inline reconciliation — a forbidden path this unit cannot touch). Both blocking consumers (S11.5 probe, rotation seam) route through the shared helper. No fifth un-fixed consumer exists. The record also correctly retracts the round-1 mis-statement that `operator_ask.py` consumes `open_asks()`.

## Scope, gate integrity

- `allowed_paths` were formally extended to include `tools/agent_supervisor/loop_turnover.py` and `tools/test_agent_supervisor_turnover_live_seam.py`; the correction code diff touches exactly those plus the three original code paths — nothing outside, no forbidden path (`cli.py` untouched).
- Both test files are additions-only (zero content-deletion lines); `test_agent_supervisor_command_authority.py` was not touched in the correction; no existing M0-T080 seam test or round-1 test was modified, deleted, or weakened.
- Modularity `--check` EXIT=0 (broker.py grew for the shared single-source predicate; cohesion recorded per rule 6).

## Observations (non-blocking)

1. **cli.py predicate convergence (deferred, appropriate).** The status command keeps its own inline copy of the identical reconciliation predicate rather than calling the shared helper, because cli.py is a forbidden path for this unit. This is a documented follow-up, not a defect — the predicate is identical (verified round 1 and here). Converging it onto `owner_unanswered_asks` would remove a duplicated-but-correct copy when cli.py is next in scope.
2. **End-to-end live restart still deferred** to the R276 resume after M0-T116 recertification (honestly recorded §4). Both live-refused boundaries — the S11.5 probe and the rotation seam — are now unit-covered with removal-sensitive tests, which is sufficient for this defect-lane fix; R271 mandates the recert regardless.

## Conclusion

The correction round resolves G3 BLOCKER-1 at root (the rotation seam was the genuine fourth consumer of the defect), consolidates the reconciliation into a single shared predicate without changing real-journal behavior, and corrects both of my round-1 MINOR findings plus the G5 LOW-2 hardening gap. All recorded evidence reproduces at the corrected identity `29fc1e2`: 211/211 (three packs), 748/748 (14-pack sweep), modularity EXIT=0, additions-only, in-scope, removal-sensitivity independently confirmed. I have no remaining blocking or minor findings.

**G4 DELTA VERDICT: PASS.**
