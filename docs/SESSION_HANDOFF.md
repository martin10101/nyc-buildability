# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-08-04**, after the M0-T036 Phase 5 decision packet and the owner's packet decision
(D-007 amendment 7).

## Where main is

| | |
|---|---|
| `origin/main` at refresh | `cb9a999` (owner's PR #150 merge; unchanged through Phase 5) |
| accepted tasks | **54** (unchanged) |
| registries | D-004 v22 (733 ids) · D-005 · D-006 (32 ids) · **D-007 v8 (584 ids, amendments 1–7 all captured + audit-logged)** |
| task branch | `task/M0-T036-supervisor-bridge` — Phase 5 complete at frozen `43848bd` (packet SHA); tip carries review preservations + captures |

## 1. M0-T036 — Phase 5 COMPLETE; owner decision RENDERED

- **Decision packet:** `project-control/reports/M0-T036-PHASE5-DECISION-PACKET.md` (frozen
  `43848bd`, CI run 30886102559 all 13 jobs green). Shadow pilot runs 1–6; run 6 = full live
  cycle (Codex COMPLETE, gpt-5.6-sol attempt 1, 0/2 owner touches, forwarded nothing, ends AT
  the gate). Five independent gate reviews, all PASS, preserved verbatim under
  `project-control/reports/M0-T036-G3/G4/G5/CPV/DCV-*.md`; CPV corrections C1/C2 discharged;
  QA erratum applied to PILOT-LOG.
- **Owner decision (D-007 am.7, R577–R584): DO NOT ACTIVATE — shadow-only stands; supervised +
  limited-auto OFF; the §6 allowlist proposal is NOT adopted and inert.**
- **Authorized in-flight work:** ONE V1.1 correction unit, scope exactly B-1..B-4 + F-2 + F-4 +
  F-5-doctor-tz (hardening items only delta-scoped + separately cited); then a delta RE-GATE at a
  new frozen SHA under the same five-review scheme. Producer dispatched 2026-08-04.
- **M0-T035 acceptance:** owner-typed only. The D-006 verification row (blocking accept
  precondition) was a pending placeholder; independent verification dispatched 2026-08-04; the
  orchestrator records the verifier's return, then hands the owner the exact console lines.

## 2. Standing discipline (carry forward)

- **D-004-R721: EVERY MERGE QUEUES FOR THE OWNER** (all M0-T036-era merges were owner-executed:
  PRs #150/#151/#152).
- **Ledger writes go through `tools/project_control.py` ONLY** (CPV F-CP-1 lesson: hand-appended
  progress entries were caught and CLI re-recorded; never hand-edit control files). Every
  directive amendment gets a manifest.audit_log entry AT CAPTURE TIME (CPV F-CP-2).
- Gate-class spawns pinned Fable 5 (R732); producers unnamed, reviewers may be named; reviewers
  are read-only and may signal idle without delivering — demand the complete return and preserve
  it verbatim the moment it arrives.
- R024 public-repo hygiene; secret-shaped test fixtures use the runtime-assembly idiom (no
  scanner suppression anywhere).
- Owner-plane local state (never touch): `bad-amend-backup` branch, modified backend-engineer
  memory file, untracked agent-memory files, `.claude/settings.local.json.bak-2026-08-03`,
  parked supervisor runtime dirs under `%LOCALAPPDATA%\NYCBuildabilitySupervisor\*.pilot-run*-parked`,
  and the controller checkout `C:\SupervisorController` (owner-created; agents read-only).

## 3. NOT AUTHORIZED (unchanged unless a capture says otherwise)

Limited-auto activation (owner declined; R577) · supervised mode · the §6 AUTO-allowlist
proposal (inert; R578) · **`doctor --live` probe and the supervised single-forward rehearsal —
each returns to the owner separately AFTER the V1.1 re-gate (R582)** · M0-T035/M0-T034
acceptance except by owner-typed command (R583) · any merge without owner execution · effort
keys anywhere, ever · settings/hooks/rules changes · M0-T029/M0-T032/M0-T025 · product/legal-rule
changes · `teammateDefaultModel` · deployment/hold releases · G6, Graphify, expansion, survey work.

## 4. Owner backlog (stays backlog)

C1 MATERIAL_FIELDS inversion · OBS-6 preservation-time redaction · D-001 capture-guidance for
`classified_at_identity` · drive M0-T034 to submit/accept · OBS-B evidence-map internal identity
fields · read-only-guard gaps · qa-engineer `--no-regen` (G5 O3) · weak
`test_manifest_is_order_independent…` test · V1.1 hardening ledger not in the authorized unit
(G5 L-2 single-account-boundary consideration; any L/V items the unit skips).
