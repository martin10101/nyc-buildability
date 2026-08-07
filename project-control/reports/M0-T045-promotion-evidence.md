# M0-T045 — Section 16.2 Promotion-Evidence Pack (POPULATED — rehearsal complete 2026-08-07)

**Claim ceiling (AS-3, stated first and binding):** this pack claims AT MOST readiness for the
**shadow → supervised-auto** step. It does NOT claim limited-auto readiness — limited-auto is
gated on its own evidence including **two real product tasks** through the pipeline — and it does
NOT activate anything. Every activation tier remains owner-gated; R595 evidence is a prerequisite,
not an authorization (D-010-R074, R104; M0-T036-ACTIVATION-CHECKLIST).

Each Section 16.2 item must link to reproducible primary evidence. Rows marked `[REHEARSAL]` are
completed only from the sealed R595 rehearsal trail (`M0-T045-r595-rehearsal.md` §4); rows citing
accepted-task evidence name the accepted task and its report/suite.

| # | 16.2 item | Evidence | Status |
|---|---|---|---|
| 1 | tests | Full supervisor suite at head `afc2da5`: **1317 passed / 2 skipped** (M0-T044 baseline 1271/2 + increment-1 hardening +36 + increment-2 cross-process locks +10; zero regressions; reproduced independently by the orchestrator both times) | **COMPLETE** |
| 2 | replay | M0-T044 journal-replay crash-reconciliation-without-blind-retry proofs (accepted, PR #170); `replay.py` corpus suite in the green run above | **COMPLETE** (accepted evidence) |
| 3 | crash simulation | M0-T044 crash-during-push/merge reconciliation proofs + live R6: mid-unit emergency stop → HALTED → recovery report, zero unaccounted children (`M0-T045-r595-rehearsal/estop-run/`) | **COMPLETE** |
| 4 | context rotation | **LIVE R595 rehearsal (closes the R593 residual leg):** real trip (ctx 134,497 ≥ threshold) → armed without interrupting the unit → owner digest-bound approval → forward exactly once → **digest-verified handoff `e75d07c0…` → new session minted → relaunch → successor completed cycle 2 through live review** (`M0-T045-r595-rehearsal/main-run/`) | **COMPLETE — LIVE** |
| 5 | child cleanup | Section 19.2 proofs (M0-T039/T041 suites) + live R6 child-tree termination verified by PID + live R1b/R4b quiesce ordering in the journal | **COMPLETE** |
| 6 | GitHub push/PR/merge | Per owner decision D-010-R119: stands on M0-T044 Section 19.4 proofs (57 tests, ten §5.5 predicates both directions, accepted PR #170) + the real PR history (#155..#172, incl. this task's own branch flow) | **COMPLETE** (accepted evidence + owner decision) |
| 7 | stale-SHA rejection | M0-T044 stale-remote-SHA block/reconcile proofs (accepted) | **COMPLETE** (accepted evidence) |
| 8 | secret scan | M0-T044 secret-finding-blocks proof + increment-1 SEC-3 redaction discipline (MergeRequest findings + condition logging) + gitleaks pre-commit on every rehearsal commit | **COMPLETE** |
| 9 | branch-protection verification | M0-T044 main/force hard-deny proofs + repository ruleset (8 required checks, verified green on PRs #154..#172) | **COMPLETE** (accepted evidence) |
| 10 | rollback | Live R6 (16.3): durable emergency stop mid-unit, process-tree termination, no-new-dispatch (`autostart refused`), owner-only clear, recovery report (`estop-run/r6-recovery-status.json`) | **COMPLETE — LIVE** |
| 11 | owner-touch count | R078: session-3 window 0 touches; this rehearsal window **8 typed operator acts** (2 authorizations R119/R120 + 6 launch/approval commands, 1 no-op) — enumerated in the rehearsal report | **COMPLETE** |

## Pre-activation checklist reconciliation (required for an honest pack)

Checklist reconciliation at head `afc2da5`:

- **Three pinned hardening sets: RESOLVED with test evidence** (increment 1, commit `4db6a71`):
  M0-T041 A-items (A1 pending_prompt failure-path locks; A2 empty-shape fixture lock; A3
  real-sampler CLI wiring + WARN-notify + doctor tests; A4 procedural live-bytes duty stated),
  M0-T042 G5 L-1/I-1/I-3, M0-T044 G3 MINOR-1/2 + G5 SEC-1/SEC-2/SEC-3/INFO-1.
- **R595 row: SATISFIED by the sealed live rehearsal trail** (this pack, row 4; finding R595-F1
  found → fixed → cross-process-locked same-window, commit `afc2da5`).
- **OPEN OWNER DECISIONS (explicit, NOT absorbed):** (i) supervised-auto activation itself;
  (ii) single-account Windows OS-ACL enforcement sufficiency (G5-L-2); (iii) any quota-fixture
  `verified_live` flip (requires independently confirmed live bytes — none flipped);
  (iv) per-tier authorization beyond supervised-auto (limited-auto needs its own evidence
  including two real product tasks).

## Residuals and open owner decisions (to enumerate at submit)

- Quota-fixture `verified_live` flips: remain fail-closed unless live bytes independently
  confirmed (M0-T041 G5 INFO-1).
- Supervised-auto activation itself: owner types the activation decision; this pack only
  evidences readiness.
