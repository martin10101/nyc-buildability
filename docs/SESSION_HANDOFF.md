# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, hard rules, and workflow routes live in
`CLAUDE.md` and the specialist docs it routes to — not here.

**Verified base at `dcb905d62b47919a3d2d78c7620d7bd07662ccf5`** (origin/main when this was written;
`git fetch` and reconcile). Milestone **M0** active; M1 accepted; M2-T012 accepted; **M4-T001
rules-engine foundation merged** (PR #76 at frozen `de88ba2`; G0/G2/G3/G4 all PASS, **awaiting G6**,
NOT accepted — every R5 rule stays `needs_review`, nothing Published/Verified). Checkpoint **CP-0031**
(CP-0032 is reserved for M0-T019 — do not create one).

## M4-T001 status — foundation merged, awaiting G6 (do not accept, do not publish)
The tested rules-engine + first R5 residential-FAR draft family are on main (PR #76 @ `de88ba2`).
Recorded G0/G2/G3/G4 PASS; task stays `awaiting_gate`. Acceptance is blocked on **G6** (qualified-human
legal approval — mandatory before any R5 rule is Published/Verified) and, for the client-validation item
only, **B-010** (client R5 benchmark sheet). These block ONLY publication/verification + final
acceptance — not continued engineering with `needs_review` rules (owner directive 2026-07-21).

## Next task — rules-engine ↔ property-analysis integration
Wire the M4-T001 engine into the property-profile / M2-T013 spatial-analysis API: feed property +
spatial facts into the evaluator; preserve split-lot ranges, conflicts, professional-review flags; fail
safely when spatial uncertainty exists or `spatial_context` is missing; return deterministic
calculation + citation traces; expose draft/review status honestly; prevent downstream callers from
treating draft results as Verified. Confirm the exact task ID from the ledger; if none exists, create
the smallest controlled task (never CP-0032). Implement to a frozen SHA + CI + risk-required reviews,
then return the evidence packet before merge.

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
