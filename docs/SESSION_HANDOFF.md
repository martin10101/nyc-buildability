# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md` and the
docs it routes to — not here. This is the single handoff; earlier handoffs (PRs #92, #96) are superseded.

## Where main is
- **PR #97 (D-001 Owner Directive Compliance System) is MERGED** — merge commit `2d44b47`; M0-T023
  **accepted**. Frozen reviewed identity `ed8a6776` / content `9ab6c960`.
- Then **control consolidation** (task **M0-T024**, PR from branch `control/D-002-consolidation-2026-07-24`):
  captured directive **D-002**, reconciled the stale PRs, contracted the first parallel build wave. On
  resume, `git fetch` and take the current `origin/main`.
- **Accepted-task count = 43** (through M2-T013 + M0-T022 + M0-T023). Nothing in M3/M4/M5 is Published,
  Verified, or accepted.

## Active directives (D-001 regime is ON — every new/reclaimed task must cite directive_refs)
- **D-001** active — Owner Directive Compliance System (governance; scopes M0-T023, accepted).
- **D-002** active — "Activate control system, consolidate, prepare first blind-isolated parallel wave."
  69 requirements (40 CTRL->M0-T024 / 14 PROD->first-wave producers / 15 POST->post-merge controller).
  Registry: `project-control/directives/D-002-activate-control-system-first-wave/`. Validate:
  `python tools/validate_directive_compliance.py --check`.

## Milestone reality
- **M0** active (M0-T023 accepted; M0-T024 = this consolidation; M0-T025 = LOW-1 backlog; M0-T019
  **HELD** until `2026-07-28T15:59:32.231Z`; M0-T007/T008 blocked by B-001).
- **M1** complete (9/9). **M2** active (13/16; M2-T014/15/16 survey HELD; **M2-T017** = first-wave lane 3).
- **M3** planned — five-task chain contracted (D-002, carried from #93): **M3-T001** first-wave lane 1;
  M3-T002..T005 backlog/sequential (M3-T002/T003/T005 acceptance blocked by B-001; T005 also by B-011).
- **M4** active — 0/6 accepted; M4-T001..T006 merged DRAFT (G6-gated). **M4-T007** = first-wave lane 2
  (exact Decimal arithmetic / DF-2 / B-014). PR #91 footprint (sketched M4-T007..T010) SUPERSEDED.
- **M5** planned (M5-T001 merged draft). **M6/M7** planned.

## First parallel build wave (blind islands; contract = `project-control/reports/FIRST-WAVE-INTEGRATION-CONTRACT.md`)
Three genuinely-independent producer lanes; the 4th (auth/RLS) is idle (B-001 credential blocker):
- **M3-T001** — legal-source authority/coverage/registry/manifest/policy (docs + `legal_source_manifest` schema).
- **M4-T007** — exact Decimal/legal-units arithmetic in `services/api/app/rules/` (DF-2).
- **M2-T017** — close `source_fact` + `analysis_state_transition` contracts (DF-4/DF-5); sole owner of `property_profile.ts`.
Ownership is disjoint (collision matrix in the contract); none depends on a sibling's unmerged output.
Producers work in separate worktrees, start from one frozen post-consolidation base SHA, open one PR each,
never merge, never edit a shared contract. Parallel production, **sequential merging** (provider-before-consumer).

## Architecture-of-record (do not lose)
- Whole-system A-J trust analysis + defect matrix DF-1..DF-11: `project-control/reports/WHOLE-SYSTEM-TRUST-REPLAN-2026-07-23.md`.
- M3 legal-corpus five-packet plan + Document Evidence Verification Engine: `project-control/reports/M3-CORPUS-REPLAN-PROPOSAL.md`.
- Frontend security reconciliation: `project-control/reports/M0-T019-frontend-security-reconciliation-2026-07-23.md`.

## Holds / blockers (all preserved)
- **G6** qualified-human legal approval blocks all M4 rule acceptance/publication.
- **B-001** Supabase token (blocks M0-T007/T008, M3-T002/T003/T005 acceptance, auth/RLS lane).
- **B-002** Render key; **B-004** Geoclient; **B-010** R5 benchmark sheet.
- **B-011** construction-code release scope (blocks M3-T005). **B-012** public-deployment hold.
- **B-013** owner **DECLINED** frontend age-only exception (wait full 7-day threshold).
- **B-014** exact Decimal legal math required before M4 rule publication.
- **LOW-1** (M0-T025 backlog) path-containment hardening — not a blocker, not implemented under D-002.
- Expansion-agent planning HOLD (owner review) and survey-dispatch HOLD remain in force.

## Next action
Owner opens each first-wave producer worktree (paths in the D-002 owner return) in a separate Cursor
window and pastes that lane's startup capsule (`project-control/reports/<TASK>-CAPSULE.md`). The controller
tab integrates completed producer PRs one at a time (D-002 §11): fetch, inspect diff vs allowed paths,
check CI + independent review, rebase if behind, merge one, ff main, read, then the next.
