# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, hard rules, and workflow routes live in
`CLAUDE.md` and the specialist docs it routes to — not here.

**Verified base at `46f8745cf38930f4e18ba4c858424b4c0e909153`** (origin/main when this was written;
`git fetch` and reconcile). Milestone **M0** active; M1 accepted; M2 profile integration **M2-T012
accepted** (contract 1.4.0 wave+spatial integration, merged PR #74 at frozen `82b92e1`; G0/G1/G2/G3/G4/G5
all PASS). Checkpoint **CP-0031** (CP-0032 is reserved for M0-T019 — do not create one).

## Next task — M4-T001 (zoning-rules-engine foundation + first R5 residential FAR rule family)
M2-T012 is accepted and merged; the 2026-07-20 planning-report dispatch hold on **M4-T001 only** is
released (survey holds M2-T014/T015/T016 remain held). M4-T001 is lead-only in a new isolated task
branch/worktree. Read the packet for scope, file scope, and STOP conditions:
`project-control/tasks/M4-T001.json` — not a summary here.
**Next action:** G0 reconciliation, then implement M4-T001 lead-only (versioned deterministic rules DSL;
exact ZR citations + effective dates; evaluation traces; uncertainty/missing-data propagation; no
AI-published/auto-`Verified` legal rule; R5 residential FAR as first family; structurally-different
second-family representability proof; G6 qualified-human boundary preserved). If the client R5 benchmark
sheet is unavailable, raise a bounded human-input blocker for that validation item only and continue all
architecture/engine/official-source/synthetic-fixture work that does not need it.

## Current blocker
None blocking M2-T012. Credentials pending (do not block this task): B-001 Supabase (highest),
B-002 Render, B-004 Geoclient.

## Frozen concurrent items — scheduled action required
- **M0-T019 / PR #64** OPEN, FROZEN at `39080822a361b6204813d2dcbd1f849b196100ea`; blocked only by its
  own dependency-age gate. At/after **2026-07-22T06:10:00Z** rerun ONLY the failed CI jobs at that SHA;
  if green, run ONLY `ci-evidence-verifier`. Do not merge/accept/regenerate-lock/weaken-policy/advance CP-0032.

## Unresolved owner decisions
1. M0-T019 / PR #64 merge (after the 2026-07-22T06:10Z gate resolves).
2. Survey M2-T014/T015/T016 planning-report dispatch hold — still held (M4-T001 hold released 2026-07-21).
3. Credentials B-001 (highest) / B-002 / B-004.
4. GDS/expansion planning review (counter-notice §2 hold) and 3D holds — preserved.
