# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-08-07 (D-010 session-4 rotation, CP-0041)**. **The block below supersedes the older
sections further down** (kept only as history); the ledger wins on any conflict.

## CURRENT STATE (2026-08-07, session 4 — confirm against the ledger + git)

**D-010 wave-1 minimum-autonomy control chain COMPLETE.** Session 4 rotated at the post-merge seam
per R113/R115; accepted count **64**. Owner touches this session: **8 typed operator acts** (2
authorizations + 6 launch/approval commands — the supervised R595 window).

- **D-010 am.7 captured** (PR #172, merged `f61a735`): session-4 launch instruction verbatim, row
  **R118** (re-dispatch, no new obligations).
- **M0-T045 ACCEPTED + MERGED** (PR #173, merge `8533635`; accepted 64; identity `2a259525…`):
  **the R595 supervised rehearsal is COMPLETE with every leg LIVE-PROVEN** — threshold trip + armed
  seam (ctx 134,497, unit never interrupted), owner digest-bound approval, **LIVE SEAM ACTUATION**
  (forward exactly once `fwd/1/a4c3d170…` → digest-verified handoff `e75d07c0…` → new session
  `sup-5b5f59ac…` minted → relaunch → successor completed cycle 2 through live Codex review),
  re-approval fail-closed, emergency stop mid-unit (child tree terminated, autostart refused,
  recovery report). **The R593 residual is CLOSED BY EVIDENCE, never waiver** (D-007-R621).
  Owner authorizations R119 (am.8) + R120 (am.9) captured verbatim BEFORE the acts.
- **Live finding R595-F1** (approved FORWARD_PROMPT journal had no continuation path; parked record
  text-less → cross-process forward impossible) found by the rehearsal → **fixed + cross-process-
  locked same-window** (`afc2da5`, +10 tests). Pre-R595 hardening: all three pinned checklist sets
  resolved (`4db6a71`, +36 tests). Suite **1317/2, zero regressions**, reproduced independently 4×.
- **Five legs PASS:** G3; G4 (85/85 adversarial probes, audit chain cryptographically verified;
  material non-blocking: **estop audit-chain fork**, self-reported via `audit_chain_ok:false`);
  G5 (no HIGH/MEDIUM; **LOW-1** park→approve binding → activation checklist); control-plane 8/8;
  DCV **19/19** at identity `2a259525…`. Evidence sealed: 26 files, SHA-256 manifest.
- ⛔ **SHADOW-ONLY still in force. Nothing activated.** The supervised-auto **promotion pack is
  COMPLETE and owner-decision-ready** (`M0-T045-promotion-evidence.md`; AS-3 ceiling binding).
  Remaining pre-activation items pinned to `M0-T036-ACTIVATION-CHECKLIST.md`: G5 LOW-1 (bind
  forwarded bytes to the operator-named approval), G4 estop-fork follow-up, OS-ACL judgment,
  per-tier owner authorization. **Activation is an explicit owner decision.**

## NEXT SESSION — resume checklist (session 4 → 5)

1. Start-of-session: `python tools/project_control.py status` + reconcile git/CI (origin/main was
   `8533635` + this rotation PR at rotation; checkpoint CP-0041). Machine-readable handoff:
   `project-control/reports/session-handoff-2026-08-07-4.json`
   (digest `8b3804ab5f25bae051acb480406b203d4487facdbafac94f66f573c442f83951`) — verify: sha256
   over `json.dumps(doc, sort_keys=True)` with `digest=""`.
2. **Wave-1 is COMPLETE (M0-T036..M0-T045 accepted).** Per D-010 R116/0A.11 the next
   dependency-valid work is **PRODUCT work: two real product tasks** through the pipeline under
   the 80/20 rule (initiative-plan Lane 2: survey ingestion per accepted M2-T014 findings; M3
   corpus tasks remain blocked by B-001). Contract fresh product tasks; do NOT start new
   supervisor features (0A.10 freeze; only directive-cited defects).
3. **Owner-decision-ready, surface without pushing:** the supervised-auto promotion decision
   (pack complete; checklist items above outstanding). If the owner activates, the R595-gated
   automatic-continuation capability (R114) is now evidence-complete.
4. Carried rules (verbatim intent): task branch from origin/main in the orch worktree; spawn
   PRODUCERS UNNAMED (a named spawn makes readonly_agent_guard fail closed; reviewers unaffected);
   classifier denial => STOP, surface the exact `!` line, owner executes, capture any typed
   authorization as a D-010 amendment, never route around. NEW proven pattern: owner-executed
   launchers via `powershell Start-Process '<path>.cmd'` (never `cmd /c start` from `!` — Git
   Bash strips the title quotes and opens an empty window).
5. **Reviewer models:** gate reviewers ran `claude-opus-4-8` + `xhigh` (standing fallback; the 5
   flipped agent files remain uncommitted in the PRIMARY checkout; revert to `claude-fable-5`
   pins when the owner says "Fable is back"). Orchestrator ran `claude-fable-5`.
6. **Primary checkout** (task/M0-T036-supervisor-bridge @ 57ccb44): untouched per R099/R109.
   **Dormant batch** (D-009 + M0-T019 + M2-T014): untouched. All standing holds unchanged
   (deployment/G6/Graphify/expansion). Rehearsal scratch (`%TEMP%
595`) is disposable; the
   committed sealed evidence is authoritative.

---

_History: superseded session blocks (session 3 = CP-0039 / rotation PR #171; session 2 = CP-0038;
session 1 = CP-0037; the 2026-08-05 M0-T036/D-009 states) are pruned per the context-budget guard —
recover any of them with `git log -p docs/SESSION_HANDOFF.md`; the ledger remains authoritative._
