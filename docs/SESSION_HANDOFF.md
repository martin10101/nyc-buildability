# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only; operating rules, gates, and workflow routes live in `CLAUDE.md` and the
specialist docs it routes to.

**Current main at `1acb9b5`** (origin/main when written; `git fetch` and reconcile). **Main did NOT
advance this session** — all work landed on **control-only PRs (none merged)**. **Accepted-task count =
42** (unchanged). Nothing was accepted, moved, claimed, dispatched, deployed, purchased, or installed
this session.

## What this session did (three owner directives, all control-only)

1. **M3 legal-corpus replan → PR #93** (`control/M3-corpus-replan-2026-07-23`). Repairs the missing M3
   dependency BEFORE any M4-T007+ yard/coverage work. Now a **FIVE-packet** sequence with a Document
   Evidence Verification Engine (rev-5). Corpus IDs are PROPOSED backlog packets only:
   - **M3-T001** authority hierarchy + coverage matrix + registry channels + benchmark analysis +
     `legal_source_manifest` + `DOCUMENT_EVIDENCE_POLICY` + construction-code release-scope DRAFT.
   - **M3-T002** immutable source capture + versioning ONLY (exact bytes, content-addressed
     never-overwrite storage as an append-only interface, byte-level change detection) — **no
     parsing/rendering/OCR; no forward dependency on T003**.
   - **M3-T003** Document Evidence Verification Engine + the ENTIRE PDF-handling surface (classify →
     native/OCR extract → critical-token → cross-source → evidence-state machine → human-review
     bundles; PDF+OCR dependency chosen here via `/dependency-security`).
   - **M3-T004** cross-reference closure (§11-25; consumes ONLY eligible verified evidence).
   - **M3-T005** DOB Construction-Code + amendment overlay (reuses the T003 engine).
   - **M4-T007+ now depends on accepted M3-T004.** Authoritative doc: §17 of
     `project-control/reports/M3-CORPUS-REPLAN-PROPOSAL.md`. B-001 amended to block acceptance of
     M3-T002/T003/T005; regression **S9** proves it (control-plane CI). New blocker **B-011**
     (owner-approved construction-code release scope) gates M3-T005.

2. **Frontend P0 security reconciliation → PR #94** (`control/m0-t019-frontend-security-reconcile`).
   React CVE-2025-55182 (CVSS 10.0) + Next.js July-2026 release (4 HIGH + 5 MEDIUM). **M0-T019 target
   reconciled to `next`/`eslint-config-next` 15.5.21, `react`/`react-dom` 19.1.2** (re-verify later React
   CVEs); implementation must re-fork from a **frozen current-main SHA** (stale PR #64 branch, 115 behind,
   is **superseded — not merged/rebased**). New blockers: **B-012** (public-deploy hold) and **B-013**
   (owner **DECLINED** the age exception → **wait** to `2026-07-28T15:59:32.231Z`, when
   `next@15.5.21` reaches 7 complete days; **no exception path added to FE-S9**). A safe post-approval
   restart sequence (claimed→blocked→…→new worktree) is recorded, not executed.

3. **Whole-system trust replan → PR #95** (`control/whole-system-trust-replan-2026-07-23`). Control-only
   **proposal** (no task IDs contracted). End-to-end dataflow trace (production = one synchronous
   PLUTO-only endpoint; no auth/DB/orchestrator/snapshot-set/report), defect matrix DF-1..DF-11 (P0:
   no auth/RLS, binary-float legal math, no run orchestrator), inventory with dispositions, proposed
   areas **A–J**, holds classified by enforcement, cross-milestone holds. Owner decisions recorded:
   A–J **approved in principle, not contracted**; **Decimal/rational legal math + typed units = mandatory
   M4-publication blocker → B-014** (references M4-T001..T006); sequencing **A + I-foundation → B →
   I-operations**. Doc: `project-control/reports/WHOLE-SYSTEM-TRUST-REPLAN-2026-07-23.md`.

## Milestone reality (reconciled 2026-07-23)
- **M0** active (20/24 accepted). **M0-T019 is `claimed` but STALE** — its PR #64 branch is superseded
  (see PR #94); do not resume/merge/rebase it. M0-T007/T008 blocked (B-001).
- **M1** complete (9/9).
- **M2** active (13/16; M2-T014/T015/T016 survey-planning **HELD**).
- **M3** planned (**0 tasks on main**; 5 PROPOSED backlog packets on unmerged PR #93 — not contracted).
- **M4** active — **0/6 accepted**. M4-T001..T006 merged DRAFT (`needs_review`), all `awaiting_gate`,
  gated by **G6** (human legal approval) and now (proposed) **B-014** (exact-decimal legal math).
- **M5** active — M5-T001 scenario **foundation only** (`awaiting_gate`, no endpoint/optimizer).

## Open PRs (all control-only unless noted; NONE merged)
- **#93** M3 corpus five-packet replan (`36f25c4`) — rev-5, owner corrections applied; CI 13/13 green.
- **#94** frontend P0 security reconciliation (`fe540b7`) — CI green; carries the B-013 wait decision.
- **#95** whole-system trust replan proposal (`667cd16`) — CI 13/13 green.
- **#92** prior session-handoff refresh (footprint) — **STALE; superseded by this handoff** (leave to
  owner to close, or supersede).
- **#91** M4 footprint 4-way split — **superseded by the #93 approach**; still open (do not close until
  #93 is approved).
- **#64** M0-T019 frontend implementation — **FROZEN/superseded** (115 behind main); owner-authorized
  close only, per PR #94's restart plan.

## Open blockers
- **B-001** Supabase token (storage/RLS; blocks acceptance of M3-T002/T003/T005 on #93). **B-002** Render
  — `resolved_temporary`, **must be revalidated before deployment**. **B-004** Geoclient (free key).
  **B-010** client R5 benchmark sheet (PDF not committed; hash + observations only). **B-011**
  construction-code release scope (owner approval → gates M3-T005). **B-012** public-deployment hold.
  **B-013** frontend age wait to `2026-07-28T15:59:32.231Z`. **B-014** exact-decimal legal math before
  M4 publication. (B-005..B-009 unchanged.)

## Preserved holds / conventions (unchanged)
- **G6** qualified-human legal approval before any rule is Published/Verified/accepted.
- **CP-0032** reserved for M0-T019 — do not create one. No checkpoint created this session.
- **Survey hold** (M2-T014/T015/T016). **Expansion / 3D-UI holds** active. **No public deployment**
  (B-012; API is INTERNAL/DEV-only, no auth/RLS).
- Thin-client (~7 GB free): no local DB/Docker/bulk data/local npm. Control-plane changes go via
  control-only PRs; producer code + gate records travel on the task branch to a single product PR.
- Paid services: **nothing purchased/authorized.** Production Render (paid Starter web + paid
  worker/cron) and production Supabase (Pro/paid, PITR) will need purchase approval — reverify pricing
  immediately before any approval.

## Next actions / unresolved owner decisions
1. **Review + approve/amend PRs #93, #94, #95** (in that dependency order: corpus → frontend → replan).
2. On #93 approval: merge, then move **M3-T001 ONLY** backlog→ready→claim at a frozen SHA (T002–T005
   stay backlog); return full G0–G5 evidence before M3-T002; then close #91 as superseded.
3. On #94 approval: execute the recorded M0-T019 restart sequence at/after `2026-07-28T15:59:32.231Z`;
   close #64 as superseded.
4. On #95 approval (architecture only): a **separate** control PR assigns exact A–J task IDs before any
   implementation. Sequencing: **A + I-foundation → B → I-operations**.
5. Close/supersede the stale handoff PR **#92**.
6. Standing: G6 legal approval of the M4 chain; credentials B-001 (highest) / B-002 revalidation / B-004;
   Decimal-legal-math (B-014) before M4 publication.
