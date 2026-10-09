# M0-T107 — Amendment-20 attempt: certified start REFUSED PRE-DISPATCH (exit 11, `cwd_primary_checkout`) — preserved; owner decision requested

Recorded by the orchestrator 2026-08-30 (session `session_01SfXcRw7emzdojCDJmKxNTM`, campaign
seq 45→46). Primary evidence only; nothing was restarted, retried, cleared, or repaired.

## 1. What happened (both owner commands, executed separately, in order — R351)

1. **Step 1 `clear-recovery`** (owner-typed, verbatim §4): SUCCESS exactly as certified —
   journal PAUSED_RECOVERY → **PREFLIGHT** via exactly one audited `owner_cleared_pause`
   transition (transitions 18→19, audit head 43→44), nothing dispatched, no flag changed.
2. **Step 2 certified item-3 start** (owner-typed, verbatim §4): **REFUSED pre-dispatch,
   exit 11 (unsafe), reason `cwd_primary_checkout`** — "the launch would be bound to the
   orchestrator's PRIMARY control checkout … but the task packet declares the isolated
   worktree 'C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107'; a worker never runs in the
   control checkout (D-024-R336, the reproduced cycle-2 defect). Pass --worktree pointing
   at the packet's isolated worktree." Output states **"NOT DISPATCHED … no provider was
   contacted."** Recovery classification in the same output: SAFE_CHECKPOINT
   (`safe_no_auto_resume`), next state PREFLIGHT, resume permitted False.

## 2. State after the refusal (read-only verification — everything preserved)

* `status`: state **PREFLIGHT**, transitions **19** (no transition consumed by the refusal),
  audit chain ok head **45** (one new audit record documenting the refused start — evidence,
  not damage), pending effects 0, queued questions 0.
* `recovery-status`: PREFLIGHT; emergency stop False; manual pause False; surviving
  children 0; pending effects 0.
* No journal edit, no budget reset, no history clearing, no second clear-recovery, no
  repin, PR #241 untouched (R360 fully observed). `wt-m0t107` untouched, clean @ `796e18f`.

## 3. System-level finding: a certification-document defect, and the T123 seam working as designed

* **The seam did its job.** M0-T123 (material `16e1b3b`) added fail-closed packet-worktree
  cwd binding at the launch seam (`tools/agent_supervisor/launch_seam.py` — refusal code
  `CWD_PRIMARY_CHECKOUT` line 72; binding contract lines 135–140; `worktree_matches_packet`
  lines 184–196): an unbound or primary-checkout launch is refused BEFORE provider contact.
  This live refusal is the first live proof of exactly the protection T123 was built for
  (the reproduced cycle-2 defect, R336). No worker ran in the control checkout.
* **The certified command is defective relative to the certified code.** The M0-T124 §4
  item-3 start command carries **no `--worktree` flag** and was described there as "the
  same certified item-3 start (unchanged shape)". Post-T123 that shape can NEVER dispatch:
  the seam requires explicit binding to the packet's declared worktree. The fifth
  certification never executed `start` (certification is non-live by design), so the
  incompatibility between the §4 command text and the T123 arg contract was not caught by
  the R350 preflight (which also never runs `start`) nor by any test that covers the CLI
  presentation surface. This is a **documentation/certification-package defect in
  M0-T124 §4**, not a code defect. Follow-up candidate carried: certification packages
  must re-derive the presented start command from the live `start` arg contract (or a
  covered fixture) whenever the launch seam changes.

## 4. Why this is put to the owner rather than auto-continued

Amendment 20 (R351) bound the presentation to "the exact certified start command"; that
exact command is now proven non-dispatchable. Continuing requires a command that DIFFERS
from the certified verbatim shape by one flag (`--worktree
C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107` — the remedy the certified seam itself
prescribes, matching the packet's declared worktree). Whether that corrected command is
(A) the continuation of the SAME authorized attempt (nothing was dispatched; no provider
was contacted; the journal is untouched at PREFLIGHT; the seq-33 precedent treated a
pre-dispatch refusal with zero provider contact as not consuming the attempt) or (B) out
of scope for the Amendment-20 authorization (making this a live-journey failure under the
R361 posture: preserve + full assessment for a NEW owner decision) is an authorization
question only the owner can answer. R361's literal trigger ("post-dispatch stop or
live-journey failure") did not fire mechanically — but the choice between (A) and (B) is
not the orchestrator's to make. **No further action is taken until the owner decides.**
Owner-touch measurement: both typed commands are preserved in the measurement; a corrected
start would add one more owner touch (R349 — nothing reset or reinterpreted).
