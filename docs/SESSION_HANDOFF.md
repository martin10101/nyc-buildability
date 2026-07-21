# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, hard rules, and workflow routes live in
`CLAUDE.md` and the specialist docs it routes to — not here.

**Verified base at `0fb17838d28157bf8a773c92c32056b370cc376f`** (origin/main when this was written;
`git fetch` and reconcile). Milestone **M0** active; M1 accepted; M2 mostly accepted (profile
integration in progress). Checkpoint **CP-0031** (CP-0032 is reserved for M0-T019 — do not create one).

## Active task — M2-T012 (in_progress, lead-only)
One additive **contract 1.4.0** profile integration via the accepted M2-T010 tooling; uncertainty
never collapsed. Branch `task/M2-T012-profile`; worktree `.claude/worktrees/M2-T012-profile`; committed
head `152f0123e6b07076bb0421ea84eeb43c8d418c1a` (verify live). Read the packet for scope, file scope,
and STOP conditions: `project-control/tasks/M2-T012.json` — not a summary here.
**Next action:** continue M2-T012 to a frozen submit SHA, then dispatch its required reviewers
(data-contract, code, security) once, at that SHA.

## Current blocker
None blocking M2-T012. Credentials pending (do not block this task): B-001 Supabase (highest),
B-002 Render, B-004 Geoclient.

## Frozen concurrent items — scheduled action required
- **M0-T019 / PR #64** OPEN, FROZEN at `39080822a361b6204813d2dcbd1f849b196100ea`; blocked only by its
  own dependency-age gate. At/after **2026-07-22T06:10:00Z** rerun ONLY the failed CI jobs at that SHA;
  if green, run ONLY `ci-evidence-verifier`. Do not merge/accept/regenerate-lock/weaken-policy/advance CP-0032.
- **PR #73** (context-architecture cleanup, branch `control/context-architecture-cleanup`) OPEN, awaiting
  owner approval — do not merge.

## Unresolved owner decisions
1. M0-T019 / PR #64 merge (after the 2026-07-22T06:10Z gate resolves).
2. PR #73 (context cleanup) merge.
3. Release the 2026-07-20 planning-report dispatch hold on M4-T001 + survey M2-T014/T015/T016.
4. Credentials B-001 (highest) / B-002 / B-004.
5. GDS/expansion planning review (counter-notice §2 hold) and 3D holds — preserved.
