# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** This file is orientation only; rules/gates live in `CLAUDE.md`; old blocks via
`git log -p docs/SESSION_HANDOFF.md`. CURRENT-ONLY: `context-budget` CI fails > ~4000 tok.

## Handoff — first real /session-handoff turnover

1. **Generated:** 2026-08-25 UTC · Fable 5 orchestrator, `session_01GjYMcezy7AJ9kKwBBPwJhm` ·
   reason (verbatim): **controlled first real turnover** · via the GLOBAL personal skill
   (precedence proven live; profile identity verified: origin + 3 markers).
2. **Identity (live at generation):** root/worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`,
   branch `control/D-024-fable-codex-loop`, HEAD `aec396e` == origin tip (this handoff ships in one
   commit on top).
3. **Git status:** clean; zero unpushed commits; the only change in the turnover commit is this file.
4. **Active state:** campaign record `project-control/campaigns/D-024-fable-codex-loop.json`
   **seq 1, state active, NEXT = M0-T088**; no task claimed; no lease held; D-023 continues
   separately (M0-T080 round-3, its own branch). Directives D-024/D-025/D-026 active.
5. **Objective of the arc just landed:** D-026 — hybrid global/project `/session-handoff`.
6. **Completed (durable evidence):** this session accepted **M0-T098** (D-026: global personal
   skill sha256 `504fabbb…a58`; identity-verified repo profile `.claude/session-handoff-profile.md`;
   zero-drift project fallback; G3 PASS + DCV 27/27 at `722d494`; checkpoint `CP-D026-M0-T098`,
   commit `73d5fbf`). Prior arc (same conversation): D-024 v4 capture `0d9f6b1`; **M0-T097**
   (D-025 skill) at `daabf2c`; **M0-T086** (capability baseline) at `372b4f7`→`6b598c7`;
   **M0-T087** (campaign continuity, two-round review) at `0d7fa80`→`a9505ac`. Ledger: 4 accepted
   tasks this conversation; suite baseline 1920/2/0; validator EXIT=0 at every seam.
7. **Attempted, not completed:** none — every started unit was accepted; M0-T088 is NOT started.
8. **Decisions:** hybrid skill precedence per owner correction (personal wins); zero-drift by
   byte-identical bodies; campaign record is the canonical next-action pointer; rotation at safe
   seams per D-010 R113–R114.
9. **Rejected/failed:** none this arc (D-026 wave had no correction round; earlier M0-T087
   correction round is closed history — see `M0-T087-G3-code-review.md`).
10. **Files changed this arc:** `~/.claude/skills/session-handoff/SKILL.md` (global, outside repo),
    `.claude/session-handoff-profile.md`, `.claude/skills/session-handoff/SKILL.md` (fallback),
    D-026 capture + M0-T098 control records.
11. **Validation:** `validate_directive_compliance.py --check` EXIT=0 (×3 this arc);
    `context_budget_check.py` PASS; frontmatter/zero-drift/fallback tests in
    `M0-T098-global-session-handoff.md`.
12. **Sub-agents:** none active, none pending, none stopped — nothing to resume or replace.
13. **Outstanding:** none in flight. Noted follow-ups (not blockers): traversal-hardening clause
    for the skill pair on next touch (G3 nit); M0-T088 carries the probe hardening bundle.
14. **Standing restrictions:** NEVER merge PR #241; continuous activation owner-gated (D-024 §18,
    R595); Bootstrap Gate 0 every session (primary cwd = this worktree root; `/mcp` empty) before
    any write; supervisor changes need a cited `D-024-R###` id; no worker token quotas; ctl23
    read-only; stale primary worktree untouched; expansion hold; repo is PUBLIC — no secrets.
15. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
    `project-control/campaigns/D-024-fable-codex-loop.json`; `project-control/tasks/M0-T088.json`;
    `project-control/reports/M0-T086-reuse-register.md` (Phase B reuse map).
16. **Exact next action:** claim **M0-T088** (D-024 B1: telemetry core + primary-session ingestion
    + the carried hardening bundle) per the campaign record; G0 → claim → produce → G2 → submit →
    independent G3/G4/G5 + DCV at the frozen identity → accept → advance the record to M0-T089.
17. **Stop/change conditions:** Gate-0 failure (no writes, fresh session); validator non-zero;
    reviewer FAIL/BLOCKED (consolidated correction round, re-freeze, delta re-review); anything
    needing owner authority (credentials, payment, production, legal, PR #241, activation).
18. **Successor prompt:** see the `COPY INTO THE NEW SESSION` block printed in the terminal at
    turnover, or equivalently: *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD, and
    /mcp empty before any change. Read CLAUDE.md, docs/SESSION_HANDOFF.md, and the §15 files. Run
    `python tools/project_control.py status` and `python -m
    tools.agent_supervisor.campaign_continuity --status`. Reconcile against live git + the ledger
    (they win). Report READY TO RESUME or BLOCKED. If ready, continue from §16 exactly; do not
    repeat completed work or broaden scope; stop for anything needing owner approval."*
