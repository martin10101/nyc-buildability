# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** This file is orientation only; rules/gates live in `CLAUDE.md`; old blocks via
`git log -p docs/SESSION_HANDOFF.md`. CURRENT-ONLY: `context-budget` CI fails > ~4000 tok.

## Handoff — M0-T091 accepted; campaign seq 8; D-030 capability re-baseline gate

1. **Generated:** 2026-08-26 UTC · Fable 5 orchestrator, `session_01HfptKuEs3RDxaxsSHJjc7t` ·
   reason (owner, verbatim): *"owner-requested turnover after M0-T091; the successor must perform
   the native Claude Code capability re-baseline before claiming M0-T092 or any later D-024
   task"* · via the GLOBAL personal skill (profile identity verified: origin + markers). Invoked
   at the clean D-029 SEAM READY hold — zero active sub-agents (all four M0-T091 reviewers
   completed and reconciled), zero in-flight commands, tree clean at invocation.
2. **Identity (live at generation):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop`; seam commit `b2e3b2c` == origin tip at invocation; this
   handoff + the D-030 capture + campaign seq 8 are the only changes after it, committed+pushed.
3. **This session ACCEPTED M0-T091** (D-024 C2 invisible runtime supervision; campaign unit 8):
   five new modules — `lease_runtime` (serialized grant ledger closing the G5-M4 snapshot hole;
   nested children cannot evade cap/leases), `runtime_health` (band evaluation, one-message
   guard-proven landing, per-model calibration, catastrophic ceiling + partial-state recovery,
   routine platform caps refused), `runtime_detectors` (accelerated-clock no-progress/
   repeated-attempt/scope-drift; durable evidence only), `extension_gate` (s6.1 runtime,
   deny-to-backlog default, decision-is-a-record), `child_handoff` (durable partial handoffs +
   s6.3 turnover draining) — plus the FULL M0-T090 pre-activation correction bundle applied in
   the three C1 modules. Frozen content `ee564dd`, material identity `28806917…`; G3/G4/G5 PASS
   (G4 6/6 mutation teeth RED-on-mutant) + DCV 46/46 (all 10 deferred-share discharges
   verified); acceptance `4de29c2`; checkpoint `CP-D024-M0-T091` (`b2e3b2c`). Supervisor stays
   SHADOW-ONLY (no actuation surface; R595/§18 untouched).
4. **Suite baseline now: composite full `tools/` = 2707 passed / 3 skipped / 0 failed**
   (= 2653 + 54 runtime-supervision tests; chunked FOREGROUND: non-directive ~13 min, directive
   pack minus NegativeValidatorTests ~11 min, NegativeValidatorTests ~28 min). Same 3 adjudicated
   env-conditional skips (`M0-T099-G2-self-check.md` §2).
5. **New owner directives captured this session:** **D-029** (M0-T091 seam-hold: finish/review/
   accept/checkpoint/push exactly as scoped, then SEAM READY report + wait — fully discharged:
   report delivered, wait held), **D-030** (this turnover: successor CAPABILITY RE-BASELINE
   before any M0-T092+ claim; discharges the D-029 wait state and converts its hold — see
   D-030 source-001 interpretation note). Registry validator EXIT=0 at both captures.
6. **Active state:** campaign seq 8. **NEXT = D-030 capability re-baseline task FIRST** (create a
   new bounded gated ledger task: re-run `python -m tools.agent_supervisor.capability_probe`,
   re-verify `tools/agent_supervisor/fixtures/capability_matrix_v1.json` against INSTALLED
   claude/codex + current official docs; 2026-08-25 baseline claude 2.1.220 / codex 0.146.0
   potentially stale; prove drift-absence live, D-024-R001), THEN M0-T092 (Phase D controller
   state machine / safe seams / exact-once succession) — full canonical text incl. the carried
   advisory bundle (G5 L1–L5, G3 NIT-1/2, G4 ADV-1) in the campaign record's next_action. No
   task claimed. M0-T080 (D-023) still in_progress in its own lane — not this campaign's.
7. **Owner-visible items outstanding (not blockers):** purge **FIVE** leftover pack-repo agent
   worktrees (`agent-a97cd976cfb4344f0`, `agent-ac83580dbc0f69fce`, `agent-a1e58fd626f4ec1e6`,
   `agent-a2c40102cc6592d8e`, NEW `agent-aae01bab81983549b` = M0-T091 G4 reviewer) —
   classifier-denied for sessions; pattern in `M0-T099-statusline-handler.md` §8; never merge
   agent worktree branches.
8. **Standing restrictions:** NEVER merge PR #241 or any pre-existing PR; continuous activation
   owner-gated (D-024 §18, R595); Bootstrap Gate 0 every session before any write (primary cwd
   = this root; `/mcp` empty); supervisor commits cite a `D-024-R###` id; no worker token quotas
   ever (R045); expansion hold; repo PUBLIC.
9. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 8 next_action = canonical NEXT);
   `project-control/directives/D-030-successor-capability-rebaseline/source-001.md` (the
   re-baseline gate, verbatim + interpretation); `project-control/reports/
   M0-T086-capability-baseline.md` (the pattern to re-run); `project-control/tasks/M0-T092.json`.
10. **Exact next action:** create/claim the D-030 re-baseline task (G0 → claim → live probe +
    matrix re-verification → G2 → submit → independent review + DCV → accept), citing D-030:ALL
    (+ D-024 refs as resolved) and a `D-024-R###` freeze id if it touches `tools/agent_supervisor`
    fixtures; THEN proceed to M0-T092 per the campaign record. No further owner release needed
    after the accepted re-baseline (D-030-R003).
11. **Stop/change conditions:** Gate-0 failure (no writes, fresh session); validator non-zero;
    reviewer FAIL/BLOCKED (consolidated correction round, re-freeze, delta re-review); capability
    drift discovered that invalidates supervisor assumptions → record + replan before M0-T092;
    anything owner-only (credentials, payment, production, legal, PR #241, activation, worktree
    purge).
12. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD, and
    /mcp empty before any change. Read CLAUDE.md, docs/SESSION_HANDOFF.md,
    .claude/session-handoff-profile.md, and the §9 files. Run: python tools/project_control.py
    status and python -m tools.agent_supervisor.campaign_continuity --status. Reconcile against
    live git + the ledger (they win over prose). Detect stale, duplicated, or already-completed
    work. Report READY TO RESUME or BLOCKED. If ready, continue from the campaign record's NEXT
    action — the D-030 native Claude Code capability re-baseline as a bounded gated ledger task
    FIRST; only after its acceptance claim M0-T092 — without repeating completed work or
    broadening scope; stop for anything requiring owner approval."*
