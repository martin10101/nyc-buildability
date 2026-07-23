# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, hard rules, and workflow routes live in
`CLAUDE.md` and the specialist docs it routes to — not here.

**Current main at `a3784af`** (origin/main when written; `git fetch` and reconcile — it likely
advanced if PR #88 merged). Main progression this window: `2d31ff7` (PR #86, M5-T001 scenario
foundation) → `c5e8cd0` (PR #87, M4-T006 proposal) → `a3784af` (**PR #89, M0-T022 owner-dashboard —
merged AND accepted independently**). **PR #88 (M4-T006 implementation, frozen `6509db3`) is OPEN,
reconciled onto `a3784af` (state.json merge; reviewed rules code byte-identical to `6509db3`), awaiting
owner merge authorization** — merging it advances main again.

**Accepted-task count = 42** (through M2-T013 **+ M0-T022**, accepted independently via PR #89).
Nothing in the M4/M5 chains is Published, Verified, or accepted — all merged/awaiting as **draft
`needs_review`**, gated on G6.

## Milestone reality (reconciled 2026-07-23; corrected in PR #85)
- **M0** active (20/24 accepted incl. **M0-T022 owner-dashboard**, PR #89; M0-T007/T008 blocked;
  M0-T019/T021 active).
- **M1** complete (9/9 accepted).
- **M2** active (13/16 accepted; **M2-T014/T015/T016 survey-planning tasks HELD** — owner survey hold).
- **M3** planned (no tasks; M4 proceeded on `needs_review` rules per owner directive 2026-07-21).
- **M4** active — **0/5 accepted**. M4-T001..T005 merged draft; M4-T006 merged/awaiting (see below).
- **M5** active — M5-T001 merged draft (0 accepted).

## M4 rules chain — merged DRAFT, awaiting G6 (do NOT accept/publish)
- **M4-T001** foundation (engine + first R5 FAR draft) merged (PR #76). **M4-T002/T003/T004/T005**
  merged, all `awaiting_gate`, gate JSONs recorded (reconciled in PR #85). None accepted.
- **M4-T005** = first internal rule-evaluation endpoint (disabled-by-default; `rule_evaluation` 1.0.0
  contract). Merged PR #84 @ `84b50a7`; G1/G3/G4/G5 PASS.
- **M4-T006** = R5-series **height & setback draft rule family** (this session). Frozen `6509db3`,
  **PR #88 OPEN awaiting owner merge**; **G0/G2/G3/G4/G5 all PASS** (independent), CI 24/24 green incl.
  literal `exact-production-install`. 6 per-district rules (R5 base35/bldg45 + §23-423 setback; R5A
  pitched 25/35; R5B 35; R5D 45; §23-424 QRS 45/55), 5 provenance-stamped ZR snapshots (effective
  2024-12-05, City-of-Yes §23-42 series), per-district (no defaults), separate typed constraints,
  fail-closed on unavailable inputs (street width / building type / QRS geography / overlay →
  `professional_review_required`), §23-424-vs-base → `rule_conflict`, **never `verified`**. FAR rule,
  evaluator core, integration, canonical contracts byte-unchanged. Values are `extracted_draft`
  (`raw_html_verified:false`) — **G6 must byte-verify against live ZR before any Verified surface.**
- **Acceptance boundary for the whole M4 chain:** blocked on **G6** qualified-human legal approval of
  M4-T001; and for the client-validation item only, **B-010**. These block ONLY publication/
  verification + final acceptance — not continued `needs_review` engineering (owner directive
  2026-07-21). B-010 is NOT a blocker for M4-T002..T006 or M5 engineering.

## M5 scenario engine — merged DRAFT, awaiting G6-dependent acceptance
- **M5-T001** deterministic coverage-aware **scenario foundation**. Merged PR #86 @ `e994147`;
  **G0/G1/G3/G4/G5 all PASS**; `awaiting_gate`, **NOT accepted**. Consumes the canonical
  `max_residential_floor_area_sq_ft` as a **draft zoning-floor-area cap** (never recomputed; never
  labeled gross/net/feasible/envelope/building); every envelope constraint (height/setback/yard/
  lot-coverage/parking) shown **`missing`**; top-level `missing_critical`; fail-closed; never
  `verified`. New additive `scenario` 0.x contract. Final acceptance gated on the M4 chain clearing G6.

## Next task — the active frontier
Draw from the M5-T001 rule-coverage dependency matrix + `M4-T006-future-hardening.md`:
1. **Follow-up rule slice:** R5 **yards / lot coverage / open space** (footprint constraints) — the
   remaining `blocks_envelope` families after height/setback; same M4 rule-engineering pattern, draft.
2. **M5 envelope-scenario task:** wire FAR cap + M4-T006 height/setback (later + yards) into a narrow
   bounded R5 massing scenario (still draft, never a buildable-envelope claim until the matrix is
   covered). Consumers MUST gate on `coverage_status`, not `outputs` emptiness (M4-T006 modifier note).
3. **Verification/G6-prep:** byte-level raw-HTML verbatim confirmation of the M4-T006 snapshots +
   capture verbatim for the §23-42/426/44/425 override contexts (currently PRR exceptions,
   `citation_ref:null`); extend snapshot digest to cover structured `table`/`notes` (G5 LOW).

## Open PRs
- **#88** M4-T006 implementation (frozen `6509db3`) — OPEN, all gates PASS, CI green, **awaiting owner
  merge**. Merge integrates draft rules to main; M4-T006 stays unaccepted (G6).
- **#83** stale handoff (M4-T001 era) — **superseded by this refresh; do not merge #83 unchanged**.
- **#64** M0-T019 frontend security + npm dependency-admission policy — FROZEN, owner-authorized merge
  only.

## Preserved holds / conventions (unchanged)
- **G6** qualified-human legal approval mandatory before any rule is Published/Verified/accepted.
- **CP-0032** reserved for M0-T019 — **do not create one.** No new checkpoint created this session.
- **Survey hold**: M2-T014/T015/T016 planning-report dispatch held.
- **Expansion / 3D-UI holds** active (owner review of the expansion pack pending); no 3D/UI work.
- **Credentials pending** (do not block): B-001 Supabase (highest), B-002 Render, B-004 Geoclient.
- Thin-client (~7 GB free): no local DB / Docker / bulk data / local npm. Control-plane changes go via
  control-only PRs; producer code + gate records travel on the task branch to a single product PR.

## Unresolved owner decisions
1. **PR #88** (M4-T006) merge authorization.
2. PR #64 (M0-T019) merge — frozen, owner-authorized only.
3. M2-T014/T015/T016 survey planning-report dispatch (still held).
4. GDS / expansion-planning review (counter-notice §2 hold) and 3D holds — preserved.
5. Credentials B-001 (highest) / B-002 / B-004.
