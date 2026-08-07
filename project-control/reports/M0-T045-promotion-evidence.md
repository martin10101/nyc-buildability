# M0-T045 — Section 16.2 Promotion-Evidence Pack (SKELETON — populated at rehearsal completion)

**Claim ceiling (AS-3, stated first and binding):** this pack claims AT MOST readiness for the
**shadow → supervised-auto** step. It does NOT claim limited-auto readiness — limited-auto is
gated on its own evidence including **two real product tasks** through the pipeline — and it does
NOT activate anything. Every activation tier remains owner-gated; R595 evidence is a prerequisite,
not an authorization (D-010-R074, R104; M0-T036-ACTIVATION-CHECKLIST).

Each Section 16.2 item must link to reproducible primary evidence. Rows marked `[REHEARSAL]` are
completed only from the sealed R595 rehearsal trail (`M0-T045-r595-rehearsal.md` §4); rows citing
accepted-task evidence name the accepted task and its report/suite.

| # | 16.2 item | Evidence source (to link) | Status |
|---|---|---|---|
| 1 | tests | Full supervisor suite at frozen head (baseline 1271/2 at M0-T044 + increment-1 hardening additions; exact counts stamped at submit) | pending increment-1 |
| 2 | replay | Journal-replay proofs: M0-T044 crash-reconciliation-without-blind-retry tests; `replay.py` corpus suite | pending link |
| 3 | crash simulation | M0-T044 crash-during-push/merge reconciliation proofs; recovery.py suite; R6 emergency-stop recovery report `[REHEARSAL]` | pending |
| 4 | context rotation | `[REHEARSAL]` R2-R4: real trip → barrier → seam → digest-verified handoff → successor continues (closes R593) | pending rehearsal |
| 5 | child cleanup | Section 19.2 proofs (M0-T039/T041 suites: quiesce, orphan revocation, OS-descendant termination) + `[REHEARSAL]` R2/R6 | pending |
| 6 | GitHub push/PR/merge | M0-T044 Section 19.4 proofs (57 tests, both-direction predicates) + real PR history (#155..#172 pattern); live-in-rehearsal leg = owner decision (runbook §6 item 4) | pending owner decision |
| 7 | stale-SHA rejection | M0-T044 stale-remote-SHA block/reconcile proofs | pending link |
| 8 | secret scan | M0-T044 secret-finding-blocks proof + SEC-3 redaction hardening (increment 1) + gitleaks pre-commit evidence | pending increment-1 |
| 9 | branch-protection verification | M0-T044 main/force hard-deny proofs + repository ruleset verification (8 required checks) | pending link |
| 10 | rollback | Section 19.6 rollback proof + R6 emergency stop + pause-flag recovery `[REHEARSAL]` | pending rehearsal |
| 11 | owner-touch count | R078 measurement: per-session counts (session 3: 0; this session: stamped at submit) + rehearsal-window count `[REHEARSAL]` | pending |

## Pre-activation checklist reconciliation (required for an honest pack)

The pack is complete only when `M0-T036-ACTIVATION-CHECKLIST.md` reconciles: the three pinned
hardening sets (M0-T041 A-items; M0-T042 G5 L-1/I-1/I-3; M0-T044 G3 MINOR-1/2 + G5
SEC-1/SEC-2/SEC-3/INFO-1) resolved with test evidence (increment 1), the R595 row satisfied by the
sealed rehearsal trail, and the remaining owner-judgment rows (OS-ACL sufficiency; per-tier owner
authorization) explicitly listed as OPEN OWNER DECISIONS — never silently absorbed.

## Residuals and open owner decisions (to enumerate at submit)

- Quota-fixture `verified_live` flips: remain fail-closed unless live bytes independently
  confirmed (M0-T041 G5 INFO-1).
- Supervised-auto activation itself: owner types the activation decision; this pack only
  evidences readiness.
