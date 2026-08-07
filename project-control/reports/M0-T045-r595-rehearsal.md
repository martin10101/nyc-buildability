# M0-T045 — R595 Supervised Rehearsal (DRAFT design — pending owner planning session)

**Status: DRAFT.** The rehearsal is SUPERVISED by definition (D-007-R619; D-010-R104): it executes
only in an owner-attended window, and this document is the orchestrator's prepared input to that
planning conversation (CP-0039 `next_action`: "plan it WITH the owner present"). Nothing in this
file authorizes execution; the promotion decision itself remains owner-gated. SHADOW-ONLY stays in
force for every autonomy tier throughout.

## 1. What this rehearsal closes

**R593 / QA-gap-4 — the live rotation-seam actuation** — was recorded at M0-T036 acceptance as an
explicitly accepted RESIDUAL (owner Option A, D-007-R618): structurally infeasible as a synthetic
probe under R594 because the seam needs a real forward and shadow-only forwards nothing. It was
deferred in time, **never waived**, and must be closed **by evidence, never by waiver**
(D-007-R621). 2 of 3 V1.2 live legs are proven (allow round-trip; model-mismatch detection); the
rotation leg is unit- and real-process-proven but not live-actuated.

## 2. Definition of "live actuation" (AS-1)

A real supervised run in which ALL of the following happen against real processes, with the owner
watching and the complete audit trail preserved:

1. a genuine context/rotation **threshold trip** (owner-policy threshold numbers from the
   controller config, Section 11.1 pre-dispatch thresholds; `rotation.RotationThresholds`);
2. **no rotation while a child is active** — the quiesce barrier holds (AD-031, AD-076);
3. rotation decided **at the safe seam** (`rotation.decide_pre_dispatch` → `RotationDecision`
   journal record);
4. **digest-verified handoff** written (D-010 §7.2 schema, as proven by M0-T038/M0-T043 evidence);
5. session parks at `WAIT_FOR_OWNER` with a `pending_prompt/<run_id>` record; the owner actuates
   the built operator affordance **`resume-pending-prompt`** (`cmd_resume_pending_prompt`,
   commit `b1ab12b`; fires exactly the `owner_approved_pending_prompt` edge);
6. the successor session **continues the work** from the handoff (rotation CONTINUES, not merely
   stops — D-010-R114);
7. the consumed `pending_prompt` record cannot be re-approved (M0-T041 AS-4 hardening: consumed
   marker drops the digest; re-approval fails closed).

## 3. Preconditions (all before the owner window)

- [ ] Increment-1 hardening merged: the three pinned checklist sets (M0-T041 A-items; M0-T042 G5
      L-1/I-1/I-3; M0-T044 G3 MINOR-1/2 + G5 SEC-1/2/3/INFO-1) resolved with tests; full
      supervisor suite green; zero regressions.
- [ ] Emergency-stop path verified cold (Section 16.3: kill command, durable pause flag,
      process-tree termination) — rehearsed BEFORE the live run so the abort path is proven.
- [ ] Rehearsal configuration reviewed by the owner: threshold values chosen so a genuine trip
      occurs within the attended window (owner-policy numbers; using a lower threshold is still a
      mechanically real trip — the seam, barrier, handoff, park, resume, and consume paths are
      identical; this choice is disclosed to reviewers, not hidden).
- [ ] The successor's resume unit chosen with the owner (a real, bounded, already-authorized unit
      — so "continues the work" is honest).
- [ ] Quota-fixture live-bytes duty noted (M0-T041 G5 INFO-1): NO fixture flips to
      `verified_live=True` during the rehearsal unless captured live bytes are independently
      confirmed as true account-quota exhaustion; otherwise fixtures stay fail-closed.

## 4. Rehearsal script (procedure level; exact command lines pinned at the owner session)

| Phase | Action | Pass condition | Evidence |
|---|---|---|---|
| R0 | Preflight + `doctor`; record baseline config, SHADOW posture, suite hash | doctor exit 0; posture disclosed | doctor output, config snapshot |
| R1 | Start supervised run under owner-approved rehearsal config | run starts; journal begins | journal head, audit log |
| R2 | Drive a real child unit; reach threshold WHILE child active | NO rotation until child quiesced (AD-031/AD-076) | journal ordering: trip → barrier → quiesce → seam |
| R3 | Safe seam reached → rotation decision → handoff written | `RotationDecision` recorded; handoff digest verifies | decision record; handoff JSON + digest check |
| R4 | Park at WAIT_FOR_OWNER (`pending_prompt/<run_id>`); owner runs `resume-pending-prompt` | exit 0; `owner_approved_pending_prompt` edge; successor continues the chosen unit | CLI transcript; journal edge; successor journal |
| R5 | Verify consume: re-approval of the consumed record | exit 1, fail-closed | CLI transcript |
| R6 | Emergency-stop demonstration (16.3) on a disposable run | children + write processes terminated; recovery report produced | stop transcript; recovery report |
| R7 | Seal evidence: journal + audit export, digests, owner-touch count (R078) | trail complete and hashed | sealed evidence bundle refs |

Abort rule: ANY unexpected state at any phase → emergency stop, evidence preserved, rehearsal
reported honestly as incomplete (never retried blind in the same window without owner agreement).

## 5. Independent review (AS-1 closure)

The five rostered reviewers (G3/G4/G5 + control-plane + directive-compliance legs) review the
sealed trail at the frozen head. The R593-closure claim is reviewed specifically against the
evidence in §4 — the residual closes only if every row's pass condition is met by primary
evidence (D-007-R621: by evidence, never by waiver).

## 6. Open items TO PIN with the owner (planning session agenda)

1. The supervised window (date/time; expected duration ~1-2 h including R6).
2. Rehearsal threshold values (which owner-policy numbers change, and their revert).
3. The successor's resume unit (a real bounded unit, e.g. the next wave-1/product task).
4. Whether the GitHub push/PR/merge leg of the Section 16.2 pack runs live inside the rehearsal
   window (supervised) or stands on the accepted M0-T044 harness proofs + this session's real
   PR history — the pack (see `M0-T045-promotion-evidence.md`) is honest either way.
5. Owner-touch counting convention for the rehearsal itself (R078).
