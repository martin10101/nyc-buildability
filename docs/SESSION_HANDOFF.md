# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-08-08 (session 6, CP-0043)**. **The block below supersedes the older sections**
(pruned per the context-budget guard); the ledger wins on any conflict.

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
   CP-0043; confirm whether the `control/M0-T046-preactivation` → main PR is merged; if not,
   merge it under Tier A after green checks).
2. **Blocked on owner:** the supervised-auto decision package is on the table (activation decision
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
