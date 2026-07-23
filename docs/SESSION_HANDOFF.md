# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, hard rules, and workflow routes live in
`CLAUDE.md` and the specialist docs it routes to — not here.

**Current main at `1acb9b5`** (origin/main when written; `git fetch` and reconcile). Main progression
since the last handoff: `5635c13` (**PR #88, M4-T006 implementation — MERGED**; frozen code `5d605d4`
after the owner R5-setback legal-semantics correction) → `1acb9b5` (**PR #90, prior handoff refresh —
MERGED**). This session opened **PR #91** (control-only, **OPEN**) — the M4 footprint 4-way split
proposals + metadata reconciliation (see "Next task"). **M4-T006 stays merged DRAFT / `awaiting_gate`,
NOT accepted** (G6).

**Accepted-task count = 42** (UNCHANGED this session — all footprint work is proposal-stage; nothing
contracted or accepted). Nothing in the M4/M5 chains is Published, Verified, or accepted — all
merged/awaiting as **draft `needs_review`**, gated on G6.

## Milestone reality (reconciled 2026-07-23)
- **M0** active (20/24 accepted incl. **M0-T022 owner-dashboard**, PR #89; M0-T007/T008 blocked;
  M0-T019/T021 active).
- **M1** complete (9/9 accepted).
- **M2** active (13/16 accepted; **M2-T014/T015/T016 survey-planning tasks HELD** — owner survey hold).
- **M3** planned (no tasks; M4 proceeded on `needs_review` rules per owner directive 2026-07-21).
- **M4** active — **0/6 accepted** (6 contracted: M4-T001..T006, all merged draft `awaiting_gate`).
  *(main's `master_plan.json` still reads "0/5 … T001..T005"; **PR #91** corrects it to 0/6.)*
- **M5** active — M5-T001 merged draft (0 accepted). *(main's `master_plan.json` still says M5
  "planned"; **PR #91** sets it "active" with an honest summary.)*

## M4 rules chain — merged DRAFT, awaiting G6 (do NOT accept/publish)
- **M4-T001** foundation (engine + first R5 FAR draft) merged (PR #76). **M4-T002/T003/T004/T005**
  merged, all `awaiting_gate`, gate JSONs recorded (reconciled in PR #85). None accepted.
- **M4-T005** = first internal rule-evaluation endpoint (disabled-by-default; `rule_evaluation` 1.0.0
  contract). Merged PR #84 @ `84b50a7`; G1/G3/G4/G5 PASS.
- **M4-T006** = R5-series **height & setback draft rule family** (this session). **MERGED** PR #88 @
  `5635c13`; frozen code `5d605d4`; **G0/G2/G3/G4/G5 all PASS** (independent; re-gated after the
  correction), CI 26/26 green incl. literal `exact-production-install`. `awaiting_gate`, **NOT
  accepted**. 6 per-district rules (R5 base35/bldg45 + §23-423 setback; R5A pitched perimeter-wall 25 /
  ridge 35; R5B 35; R5D 45; §23-424 QRS 45/55), 5 provenance-stamped ZR snapshots (effective
  2024-12-05, City-of-Yes §23-42 series), per-district (no defaults), separate typed constraints,
  fail-closed on unavailable inputs (street width / building type / QRS geography / overlay →
  `professional_review_required`), §23-424-vs-base → `rule_conflict`, **never `verified`**. FAR rule,
  evaluator core, integration, canonical contracts byte-unchanged. Values are `extracted_draft`
  (`raw_html_verified:false`) — **G6 must byte-verify against live ZR before any Verified surface.**
  - **Owner legal-semantics correction (this session):** the §23-423 setback now labels 10/15 ft as the
    **STANDARD UNMODIFIED minimum starting** depth and carries an always-on `documented_limitation`
    (`section_23_423_modifications_unresolved`) marking the section's reductions/modifications (front-yard
    offset with a **7-ft floor**, recesses/outer courts, >50-ft/orientation optionality, dormers) as
    unevaluated → modified/final setback **unresolved** (professional review); 10/15 is never the final
    setback. R5A already emits separate perimeter-wall/ridge constraints + flags the sloping-plane setback
    for professional review (verified correct, unchanged).
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

## Next task — the active frontier (M4 footprint follow-up; owner-approved 4-way split)
Frontier item 1 (R5 footprint constraints) is scoped and PROPOSED in **PR #91** (control-only, OPEN).
Owner chose a **4-way split**, contracted **one frozen-SHA task at a time, NO auto-dispatch**:
1. **M4-T007** lot coverage (§23-361/363) — leads; establishes the M5 consumer-boundary regression.
2. **M4-T008** rear yards + rear-yard equivalents (§23-342/343/344).
3. **M4-T009** front yards (§23-321).
4. **M4-T010** side yards (§23-332/333/334) — most entangled; last.

All `legal_rule`, `required_gates = G0,G1,G2,G3,G4,G5,G6` (G6 gates publication/verification/
acceptance, NOT the draft build). Per-variant via **§11-25** (base ⇒ suffix unless the section lists
separate suffix provisions; explicit per variant, NO family default; cite §11-25 + the substantive
section for suffix-derived values). **Fail-closed-HEAVY:** ZR **lot type is unusable from PLUTO**
(false-friend — PLUTO `LotType` 6 "Interior" = no frontage ≠ ZR interior = code 5 "Inside"), **building
type is unavailable**, and **zoning-lot area/width are only conditionally proxied by tax-lot facts**
(documented tolerance/comparison policy, not blanket `data_conflict`). CURRENT-effective **§23-3xx**
numbering (legacy §23-14/45/46/47 is STALE). PR #91 also carries the corrected input-readiness matrix,
the §11-25 applicability decision, a CLOSED source inventory (every cross-ref classified), and a bounded
metadata reconciliation. The M5 consumer-boundary regression is **test-only** (a negative guard; no M5
consumption).

**IMMEDIATE NEXT ACTION:** owner reviews/approves **PR #91**, then the orchestrator contracts + claims
**ONLY M4-T007** and returns its exact frozen SHA + full G0-G6 evidence + CI + product PR **before**
T008. Do NOT auto-dispatch T008/T009/T010.

Still open (frontier items 2-3, unchanged): the **M5 envelope-scenario** task (consumers MUST gate on
`coverage_status`, never `outputs` emptiness — M4-T006 modifier note) and **M4-T006 verification/G6-prep**
(byte-level raw-HTML confirmation of the snapshots; capture the §23-42/426/44/425 override contexts,
currently PRR exceptions with `citation_ref:null`; extend the snapshot digest to structured
`table`/`notes`, G5 LOW).

## Open PRs
- **#91** M4 footprint proposal (control-only, **OPEN**, this session) — 4-way split T007-T010 packets
  + corrected readiness matrix + §11-25 decision + closed source inventory + bounded metadata
  reconciliation. **No task JSON, no code.** Owner review/approval gates contracting M4-T007.
- **#64** M0-T019 frontend security + npm dependency-admission policy — FROZEN, owner-authorized merge
  only.
- **#88** M4-T006 implementation — MERGED (`5635c13`, code `5d605d4`). **#90** prior handoff refresh —
  MERGED (`1acb9b5`). (#83 stale handoff — CLOSED.) This handoff refresh travels on its own
  control-only branch/PR (`control/handoff-2026-07-23-footprint`).

## Preserved holds / conventions (unchanged)
- **G6** qualified-human legal approval mandatory before any rule is Published/Verified/accepted.
- **CP-0032** reserved for M0-T019 — **do not create one.** No new checkpoint created this session.
- **Survey hold**: M2-T014/T015/T016 planning-report dispatch held.
- **Expansion / 3D-UI holds** active (owner review of the expansion pack pending); no 3D/UI work.
- **Credentials pending** (do not block): B-001 Supabase (highest), B-002 Render, B-004 Geoclient.
- Thin-client (~7 GB free): no local DB / Docker / bulk data / local npm. Control-plane changes go via
  control-only PRs; producer code + gate records travel on the task branch to a single product PR.

## Unresolved owner decisions
1. **PR #91 review/approval** (M4 footprint 4-way split) — gates contracting **M4-T007** first (then
   T008-T010, one frozen-SHA task at a time). Merging #91 also lands the metadata reconciliation
   (M4 0/6, M5 active). Frontier items 2-3 (M5 envelope-scenario, M4-T006 G6-prep) follow.
2. PR #64 (M0-T019) merge — frozen, owner-authorized only.
3. M2-T014/T015/T016 survey planning-report dispatch (still held).
4. GDS / expansion-planning review (counter-notice §2 hold) and 3D holds — preserved.
5. Credentials B-001 (highest) / B-002 / B-004.
6. G6 qualified-human legal approval of the M4 chain (M4-T001..T006) — the gate to any Verified/Published
   result and final acceptance (incl. byte-level verification of the M4-T006 ZR snapshots).
