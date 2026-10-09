# M0-T116 — Second golden re-certification at the post-repair frozen final identity

Task: M0-T116 (unit P; Amendment 12 rows R273/R275/R276, instantiating R247/R271).
Recorded by: orchestrator (fable-orchestrator-session), 2026-08-29, campaign seq 28.
Supervisor-freeze qualifying evidence: **D-024-R275**.

## 1. Why this re-certification exists (R247/R271/R275)

After the M0-T112 certification, the first live limited-auto run exposed a restart-blocking
seam defect (owner-denied asks never resolved their queue rows). The owner ordered one
certification window (Amendment 12): **M0-T115** (broker answer paths resolve their ask
rows + the shared read-time reconciliation at BOTH blocking consumers — the S11.5 restart
probe and the rotation-seam feed; accepted after a G3-BLOCKER correction round with four
delta-PASS reviews) and **M0-T114** (the three pinned residuals: telegram queue-growth
like-for-like digest; sanitized register `source_record_key`; unit-K notes dispositioned
inert-by-design; accepted with four PASS + four delta-PASS reviews). Both moved
`tools/agent_supervisor/**`, invalidating the M0-T112 certification (R247). This unit
re-runs the full certification at the ONE frozen post-repair identity (R275). Resume
(R276) happens ONLY after this unit is accepted and the complete activation preflight
passes again.

## 2. The FINAL frozen post-repair identity (what was certified)

* Certification run head: **`c67830f`** (branch `control/D-024-fable-codex-loop`; code
  tree clean during every run; only pre-declared control-plane records changed at this
  seam).
* Supervisor material identity: `tools/agent_supervisor/**` last moved at **`f89aa29`**
  (M0-T114 deliverable; the M0-T115 correction `d89d740` sits beneath it); directory tree
  object `7487901cea729f5c254f98c8f7dcf859eb64e2c5`.
* Golden pack: blob `cf03caaa261da9726c7a12fc1676acb68851bac1` (last moved by M0-T114's
  register test + the scanner pragma; the certification SCENARIOS — two-unit golden run,
  rotation crossing, controller restart, injected faults, watcher/registers — are
  untouched since the M0-T112-certified `d2946392` version except for that one additive
  register test). **Not edited by this unit** — re-run only.
* Identity composition: post-repair identity = M0-T112-certified system + accepted
  M0-T115 (`91664bb`+`d89d740`) + accepted M0-T114 (`f89aa29`+pragma `a22e34a`). Nothing
  else touched supervisor code since `8574c58` (verified by per-unit reviewer diffs).

## 3. Re-run evidence (all executed at the identity above, foreground, this seam)

| Pack | Result |
|---|---|
| FULL golden-run pack (41 tests: the 40 certified scenarios + the M0-T114 register test) | **41 passed, 0 failed** (15.43s) |
| Affected packs (command-authority, recovery-probes, turnover-live-seam, telegram L-pack, operator-channel, codex-channel K-pack, adversarial, endurance, phase1, reviewer) | **705 passed, 0 failed** (59.64s) |
| WHOLE supervisor suite chunk 1/4 (files 1–15) | 680 passed |
| — chunk 2/4 (files 16–30) | 725 passed (1:35) |
| — chunk 3/4 (files 31–45) | 689 passed, 2 skipped |
| — chunk 4/4 (files 46–59) | 616 passed |
| **Whole-suite total** | **2,710 passed, 2 skipped, 0 failed** (2,712 collected) |

**Baseline reconciliation (freeze rule, exact):** M0-T112 baseline 2,696 collected
→ +14 (M0-T115: 6 defect + 7 guards + 1 hardening) → +2 (M0-T114: 2 defect tests)
= **2,712 collected**. Chunk arithmetic: 680+725+689+616 = 2,710 passed + 2 skipped =
2,712. No test removed, no unexplained drift. (Independent corroboration: the T115 G3
delta reviewer ran the full suite at the pre-T114 identity: 2,708 passed + 2 skipped =
2,710 collected — exactly this chain minus M0-T114's 2.)

* **CI (confirming whole-suite run on the pushed SHA):** the standard 20-check CI runs on
  the pushed certification tip (this report + the activation-package refresh commit); the
  tip SHA and its 20/20 conclusion are pinned in the M0-T116 `progress_log` at the submit
  seam. Prior tips `723f1d8` (T114 resubmit) and `29fc1e2` (T115 resubmit) were both
  20/20 green.

## 4. Activation-package refresh (items 10–12 + the top sequencing banner)

Items 10–12 of `M0-T096-activation-package.md` now cite the post-repair identity and this
re-certification. **Correction round (G3 MAJOR-1):** the initial refresh left the TOP
sequencing banner at its Amendment-8/M0-T112 state, which — with M0-T112 now accepted —
read as "already presentable" on an invalidated certification and contradicted the
refreshed item 11. The banner is now rewritten to the Amendment-12 state: it records the
completed Amendment-8 chain, the owner's already-exercised R187/R595 activation decision
(Amendment 9), the R247 invalidation by the repair window, and gates the **R276 RESUME**
on THIS unit's acceptance plus the complete activation preflight. The package still
activates nothing; what remains gated by this unit's acceptance is the R276 RESUME of the
authorized loop.

## 5. Residuals and known characteristics of the certified identity

The three previously-pinned residuals are RESOLVED (M0-T114) or dispositioned
(unit-K notes: inert-by-design, no consumer wired — inherited accepted design).
Newly pinned non-blocking notes from this window's reviews, carried forward:
1. Seam read-error raw propagation (G5-T115 LOW): an unreadable journal aborts
   `full_turnover` fail-closed but as a raw exception rather than a graceful
   `_turnover_refused`; optional wrap suggested.
2. `cli.py` reconciliation-predicate convergence onto `broker.owner_unanswered_asks`
   (identical semantics today; forbidden path in both repair packets).
3. Telegram queued-digest collision edge (G5-T114 INFO): two distinct raw summaries
   truncating to identical post-builder text suppress the second enqueue — byte-identical
   delivered content, pre-existing surface, at-least-once preserved.
By R247, fixing any of these later re-invalidates certification again.

## 6. Prohibition compliance (R248/R273)

No activation-state change, no PR #241 touch, no dependency, no `.claude/**`, no MCP, no
journal write occurred in this unit. The unit wrote only: this report, the G0 readiness
report, the activation-package items-10–12 refresh, and control-plane records. The
supervisor loop remains STOPPED pending the R276 resume sequence.
