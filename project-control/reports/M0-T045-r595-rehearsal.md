# M0-T045 — R595 Supervised Rehearsal (IN PROGRESS — owner window active 2026-08-07)

**Status: EXECUTING under owner authorization D-010-R119** (source-009, typed 2026-08-07:
"Approve R595 rehearsal per runbook: window now; GitHub leg on M0-T044 evidence; successor resumes
the next dependency-valid unit; begin."). The owner personally performs the operator acts
(launches + approvals) via `!` commands; the auto-mode classifier independently denied the
orchestrator's own launch attempt, and per the captured classifier-denial protocol the owner
executes — which is also the correct supervised-rehearsal shape (the acts ARE the R078 owner
touches). SHADOW-ONLY stays in force for every autonomy tier throughout; the promotion decision
remains owner-gated.

## LIVE RESULTS (2026-08-07 window)

- **R0 doctor: PASS** (fresh runtime minted; journal v1 intact; audit chain intact; owner config +
  model selection verified; no effort key anywhere).
- **R1 park: PROVEN LIVE.** Run `run_r595_rehearsal` (code under test = this branch @ `492a0f4`;
  owner-immutable config; synthetic workload; threshold 1): cycle 1 ran end to end
  (`START_CLAUDE → … → CODEX_REVIEW → VALIDATE_DECISION → POLICY_CHECK → WAIT_FOR_OWNER`), live
  usage 134,036 tripped the threshold → **`rotation_pending=True` armed with the unit never
  interrupted**, decision REVISE, continuation prompt HELD (nothing forwarded;
  `forwarded_message_ids: []`), parked with digest `e6f112c6…`. Evidence:
  `M0-T045-r595-rehearsal/r1-start-output.json`.
- **R4 step 1 (owner approval): PROVEN LIVE.** Owner-run `resume-pending-prompt` with the exact
  digest → audited `owner_approved_pending_prompt` transition to FORWARD_PROMPT, record consumed.
  Evidence: `M0-T045-r595-rehearsal/r4-resume-output.json`.
- **R4 step 2: FAIL-CLOSED REFUSAL — FIRST-CLASS LIVE FINDING (see below).** Seam actuation NOT
  yet live-proven.

## FINDING R595-F1 (live, 2026-08-07): approved FORWARD_PROMPT journal has no continuation path

The resume `start` refused: `bad_cycle_entry_state: a cycle starts from ['CLAUDE_RUNNING',
'PREFLIGHT'], not from 'FORWARD_PROMPT'` (fail-closed; 0 provider calls; journal unchanged).
Evidence: `M0-T045-r595-rehearsal/r4-start-output.json`. Root causes:

1. `loop.py:116` `CYCLE_ENTRY_STATES = {PREFLIGHT, CLAUDE_RUNNING}` — the loop cannot enter from
   FORWARD_PROMPT although the S7 table has the legal exit (`FORWARD_PROMPT → CLAUDE_RUNNING` on
   `prompt_forwarded`, `state_machine.py:217`).
2. The parked record (`loop.py:1681`) stores `{cycle, digest, decision, created_at_utc}` — no
   prompt TEXT (text is digest-only everywhere by design) — so a cross-process resume has nothing
   to forward; the CLI success message promised what the loop refuses.

Same class as the original V1.2 structural finding (a state with no operator exit), one level
deeper: the M0-T036 cure added the CLI edge but no loop entry, and no test crossed the process
boundary (park → CLI approve → fresh start). **Disposition: FIXED same-window** (owner retry
agreement D-010-R120), commit `afc2da5`: durable held-prompt text (F1), text-preserving approval
with re-approval dead (F2), FORWARD_PROMPT loop resume with digest-verified forward-exactly-once
via the shared outbox core (F3), fail-closed on every degenerate entry incl. old-shape records
(F4), truthful CLI contract (F5); +10 tests incl. the cross-process integration lock that would
have caught it; suite 1317/2, zero regressions, reproduced independently by the orchestrator.
The parked `run_r595_rehearsal` journal (old-shape, text-less record) is intentionally
UNRESUMABLE after the fix (fail-closed) and is preserved as discovery evidence
(`M0-T045-r595-rehearsal/discovery-run/`).

## FINAL RESULTS — all legs live-proven (2026-08-07 window, fixed code @ afc2da5)

| Phase | Result | Primary evidence (`M0-T045-r595-rehearsal/`) |
|---|---|---|
| R0 doctor | PASS (runtime minted, journal v1, audit chain, config verified) | doctor run recorded in session; config = owner `C:\SupervisorController` |
| R1b threshold trip + park | **PROVEN LIVE**: ctx 134,497 ≥ threshold → `rotation_pending=True` armed, unit NEVER interrupted; REVISE prompt HELD (nothing forwarded); parked WAIT_FOR_OWNER, digest `a4c3d170…` | `main-run/r1b-start-output.json` |
| R4b step 1 owner approval | **PROVEN LIVE**: digest-bound `owner_approved_pending_prompt` → FORWARD_PROMPT; text preserved under `approved_digest` | `main-run/r4b-resume-output.json` |
| R4b step 2 SEAM ACTUATION | **PROVEN LIVE** (the R593 missing leg): forward exactly once (`run_r595_rehearsal_b/fwd/1/a4c3d170…`) → rotation on `context_threshold`: **digest-verified handoff `e75d07c0…`, new session `sup-5b5f59ac…` minted, relaunched**; successor ran cycle 2 through checkpoint → evidence → live Codex review → policy check; parked safely (STOP_FOR_OWNER hold). Audit chain intact, 37 events. | `main-run/r4b-start-output.json`, `main-run/audit.jsonl`, `main-run/supervisor_journal.sqlite3` |
| R5 re-approval refusal | **PROVEN LIVE**: consumed digest re-approval → exit 1, "no pending-prompt record", zero mutation | `main-run/r5-reapprove-output.json`, `…-stderr.txt` |
| R6 emergency stop (16.3) | **PROVEN LIVE**: fired mid-unit with a real worker child running → run `halt_unsafe` → HALTED; child process tree terminated (verified by PID); durable flag blocks all new dispatch (`autostart refused`); clears only by explicit owner command; recovery report produced, zero unaccounted children/pending effects | `estop-run/r6-estop-output.json`, `estop-run/r6-recovery-status.json`, `estop-run/audit.jsonl` |
| R7 evidence seal | 26 files, SHA-256 manifest | `EVIDENCE_MANIFEST.json` |

**Owner-touch count (R078), this window:** 8 typed operator acts — 2 authorizations (R119 approve,
R120 same-window retry) + 6 launch/approval commands (one of which was a no-op due to a launcher
quoting defect on the first attempt, corrected same-window). All operator acts were owner-typed;
the auto-mode classifier denial of the orchestrator's own launch is preserved as part of the
supervised posture evidence.

**Boundaries honored:** synthetic workload only (throwaway repo, own bare origin); the only
forwarded prompt was the owner-approved synthetic continuation; SHADOW-ONLY untouched for all
real work; no activation flag changed; promotion remains owner-gated (AS-3 ceiling).

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
