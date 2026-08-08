# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-08-08 (session 6 close, CP-0044 — rotation at the ~400k ceiling, D-010 R113/R114)**.
**The block below supersedes the older sections** (pruned per the context-budget guard); the ledger
wins on any conflict.

## SESSION 6 CLOSE — M0-T048 gate wave complete; DCV + accept + merge = session 7's first unit

**Owner am.14 captured (source-014, R134–R143): C2 = CLOSE BEFORE ACTIVATION.** M0-T048 contracted
(bound R134–R143), producer delivered, ALL FIVE GATES PASS at final identity (control branch
`control/M0-T048-c2-close`, code head `ec0f55d`, merged into the control branch; submit + G0/G2/G3/
G4/G5 all recorded; suite 1374/2 triple-reproduced):

- **Design:** deterministic timestamp-free forwarded body = pure function of the five
  approval_digest-covered fields; FORWARDED-AT stamped only at actual forward time;
  `approved_digest` bound to the OPERATOR-NAMED digest; `verify_covered_instruction` reconstructs
  and refuses fail-closed (`pending_prompt_uncovered`/`_tampered`); old-shape records refuse, no
  fallback. The one non-covered input (packet_reference) was REMOVED from the body (dead
  LoopConfig field left per R140).
- **G5 (original C2 finder): PASS, no corrections — C2 RULED CLOSED** (two- and three-field
  forgeries fail closed; canonicalisation second-preimage-sound; INFO N-1/N-2/N-3 only).
- **G4: PASS, no corrections** — independently mutation-proved the forgery tests turn RED on
  pre-fix behavior; all 7 owner R138 properties concretely asserted; 4 advisory notes.
- **G3: PASS with MAJOR-1 routed to DCV** — post-approval `(approved_instruction, approved_digest)`
  resume-window forgery (attacker rewrites BOTH, self-consistently): reproduced at function level;
  G5 ruled the SAME shape INFO N-1 = outside R136's premise (that attack CHANGES the operator-named
  digest; standing full-journal-write trust-domain limit; true closure needs journal signing barred
  by R140 "no new infrastructure"). G3's suggested minimal remedy: anchor the resume verification's
  operator digest to the sealed hash-chained audit event instead of the mutable `approved_digest`.

**SESSION 7 FIRST UNIT — finish M0-T048:**
1. Dispatch directive-compliance-verifier over D-010 R134–R143 at the frozen control-branch head.
   CENTERPIECE: adjudicate G3-MAJOR-1 vs G5-N-1 — is R136 ("…rather than relying solely on mutable
   journal fields") satisfied at the CROSS-PROCESS RESUME given `approved_digest` is journal-resident?
   Give the DCV both reports (`M0-T048-g3-code-review.md`, `M0-T048-g5-security.md`) + producer
   report §8.5 disclosure. If DCV rules PASS → verification row (task_verifications append,
   applicable set likely EMPTY again — am.14 rows bind task_ids [M0-T037, M0-T048]... NOTE: R134-
   R141 DO name M0-T048, so the derived applicable set is NON-empty this time; assemble the full
   per-requirement row set from the DCV verdicts, reviewed_manifest from the gate records,
   reviewed_sha = accept-time HEAD, row written UNCOMMITTED then accept then commit). If DCV rules
   R136 unmet → bounded rework (G3's audit-event anchoring) → delta re-reviews → re-gate → DCV.
2. Accept M0-T048; Tier A merge of `control/M0-T048-c2-close` → main after the 8 required checks
   (web-dependency-security stays red repo-wide until M0-T047 — NON-required, merge proceeds as
   PR #178/#179 did).
3. **Then the activation sequence resumes (R142):** elevated ACL apply + live PROTECTED capture +
   present the owner the activation decision line, WITH G3-MAJOR-1/G5-N-1 disclosed verbatim
   (mirroring the original C2 handling). ⛔ No activation without the owner's typed decision (R131).
4. **M0-T047 (nanoid)**: age-eligible 2026-08-10T10:39:22Z — execute then if that time has passed.
5. ⛔ M2-T015/T016 stay HELD (R133/R143).

## CURRENT STATE (2026-08-08, session 6 — confirm against the ledger + git)

**M0-T046 (owner am.12 pre-activation task) ACCEPTED; accepted count 67.** On
`control/M0-T046-preactivation` (contains the merged task code `a27068d`; PR to main pending/merged
— check git):

- **M0-T046 ACCEPTED** — the ONE bounded pre-activation task (D-010 R122–R133 bound): (1) R124
  park→approve fix: park-time byte anchor `prompt_bytes_digest`, fail-closed approval binding,
  sealed CLI refusals, 8 adversarial tests — **DCV adjudicated R124 PASS** (literal
  operator-names-byte-digest construction proven impossible-to-strengthen; the LOW-1 window is
  closed); (2) R125/R126 estop fork: `append()` now REFUSES on a detected duplicate-sequence fork
  (real behavior fix) + 7 regression tests locking the four owner-acknowledged conditions 1:1;
  (3) R127/R128 OS-ACL: `os_acl.py` fail-closed verdict (DACL + owner-elevation + bounded probes,
  absolute System32 tools), `harden_controller_config.ps1` (elevated apply/rollback, refuses
  unelevated), doctor posture wiring, 31 tests. Suite **1363/2**. Gates G0/G2/G3/G4/G5 PASS at
  identity `660bf133`/`32ea6f1` after a G5-C1 rework (bare-name icacls fail-open closed) + three
  delta re-reviews PASS at `a27068d`. DCV: 11 PASS + R132 acceptance-ordering DEFERRAL, no FAIL.
  Verification row: EMPTY derived applicable set (am.12 rows bind session task M0-T037; capture
  predates M0-T046; never bind onto already-gated tasks) + substantive 12-req verification in
  `M0-T046-dcv-final.md`.
- **Activation checklist mechanically reconciled** (am.12 R131 step; see the RECONCILIATION section
  of `M0-T036-ACTIVATION-CHECKLIST.md`): every reconcilable blocker SATISFIED with ledger evidence
  (R595 complete; quota classifier + B-rows + R207 sampling via accepted M0-T041; M0-T042/M0-T044
  pinned sets via accepted M0-T045; OS-ACL mechanism + LOW-1 + estop via M0-T046).
- **REMAINING before supervised-auto = the owner-held set (presented to the owner at CP-0043):**
  (a) elevated ACL apply (`harden_controller_config.ps1` under UAC) + orchestrator live
  `controller_config_acl.protected:true` capture; (b) G5-C2 residual decision (accept verbatim in
  the decision line OR order the content-binding fix); (c) the owner-typed activation decision line
  (R131/R132). ⛔ NO activation without the owner's typed decision. ⛔ M2-T015/T016 stay HELD (R133).

## NEXT SESSION — resume checklist (session 6 → 7)

1. Start-of-session: `python tools/project_control.py status` + reconcile git/CI (checkpoint
   CP-0043; **PR #178 MERGED** — origin/main `92f5d07` contains the full M0-T046 unit; both
   checkouts synced; M0-T046 branches deleted).
2. **M0-T047 (backlog, contracted): nanoid round-3 advisory.** GHSA-2v37-7h3g-55p8 (HIGH,
   nanoid <3.3.17) surfaced 2026-08-08 against the committed apps/web lock (in-lock 3.3.16,
   transitive via postcss). Every safe version fails the 7-day age gate until **2026-08-10T10:39:22Z**
   (3.3.17 publish + 604800s) — no agent waiver exists; the D-009 am.1 exception path was never
   implemented. Until remediation the NON-REQUIRED `web-dependency-security` context is red
   repo-wide (the 8-context required ruleset is unaffected — merges of dependency-untouched work
   may proceed Tier A, as PR #178 did). **At/after the eligibility instant:** claim M0-T047
   (packet complete: exact-pin override + CI-bot lock regeneration, NO local npm; AS-1..AS-5),
   re-verify 3.3.17 is still advisory-free, execute, gate (G0/G2/G3/G5 + DCV), merge.
3. **Blocked on owner:** the supervised-auto decision package is on the table (activation decision
   line + elevated ACL command, presented at session 6 close). If the owner has typed the
   activation decision, follow it exactly; if the owner ran the elevated apply, capture
   `python -m tools.agent_supervisor doctor --config "<path>" --json` →
   `controller_config_acl.protected: true` into a report BEFORE any activation step. Otherwise
   continue other unblocked, non-held work (e.g. M0-T021/M0-T034 rework queue, M3 chain under its
   blockers) — do NOT wait idle, and do NOT touch M2-T015/T016 (R133).
3. Carried rules: task branches from origin/main in the orch worktree (`…/orch`); spawn PRODUCERS
   UNNAMED; classifier denial ⇒ try exact-path staging first, else STOP and surface the `!` line;
   `project-control/directives/**` explicit LF; task files CRLF-tolerant via CLI; ADR-006 Tier A
   merges after green checks; commits stage exact paths (no directory adds).
4. **Reviewer models:** gate reviewers run `claude-opus-4-8` + `xhigh` (standing fallback; the 5
   flipped agent files remain uncommitted in the PRIMARY checkout — revert to `claude-fable-5` pins
   when the owner says "Fable is back"). Orchestrator ran `claude-fable-5`.
5. Standing holds unchanged: deployment/G6/Graphify/expansion; SHADOW-ONLY posture intact until the
   owner's typed activation decision (R131); survey-dispatch hold on M2-T015/T016 now folded into
   R133.

---

_History: superseded session blocks (sessions 1–4 = CP-0037..CP-0041; the 2026-08-05 batch states)
are pruned per the context-budget guard — recover with `git log -p docs/SESSION_HANDOFF.md`; the
ledger remains authoritative._
