# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

## Where main is
- **First blind-isolated parallel wave COMPLETE.** All three producers accepted + merged one-at-a-time
  (D-003 sequential integration): **M2-T017** (PR #99), **M4-T007** (PR #103, superseded #101),
  **M3-T001** (PR #104, superseded #100). Main advanced `cc14208 -> 2d489c1` this window.
- **Accepted-task count = 47.** On resume `git fetch` and take the current `origin/main` (the reconcile
  PR that carries this handoff will have advanced it by one commit).

## Active directives (regime ON — every new/reclaimed task must cite directive_refs)
- **D-001** active — Owner Directive Compliance System (scopes accepted M0-T023).
- **D-002** active — first-wave activation/consolidation. All 4 task rows PASS in its verification.json
  (M0-T024, M2-T017, M4-T007, M3-T001), each verified by directive-compliance-verifier != producer.
- **D-003** active — "first-wave integration + second-wave prep." M0-T026 (anchor) is **backlog**: the
  first-wave-integration part is done; the **second wave is intentionally NOT contracted** (owner
  directed reconcile-and-stop this session). Do NOT capture/plan/implement any Agent Teams adoption
  directive (owner prohibition, this session).

## What now works (first wave)
- **M2-T017**: `source_fact` + `analysis_state_transition` canonical contracts are CLOSED
  (additionalProperties:false); an allowlist serializer exists as a **frozen interface, NOT wired** into
  the production route/builder. Wiring is a **later controller-contracted integration task** (candidate
  second-wave lane 2).
- **M4-T007**: exact rational/Decimal legal arithmetic in `services/api/app/rules/` — no binary-float on
  the legal decision path; per-rule rounding + unit enforcement (fail-closed); differential recompute is
  independently oracle'd. **B-014 RESOLVED** (exact-math prerequisite met). M4 rule PUBLICATION is still
  blocked by **G6** (qualified-human legal approval) + B-010.
- **M3-T001**: legal-source authority policy, coverage matrix, document-evidence policy,
  construction-code release-scope DRAFT, additive `legal_source_manifest` schema + fixtures. **Unlocks
  M3-T002** (next in the sequential M3 chain).

## Milestone reality
- **M0** active (M0-T023/T024 accepted; M0-T025 = LOW-1 backlog; M0-T026 = D-003 anchor backlog; M0-T019
  **HELD** until `2026-07-28T15:59:32.231Z`, PR #64 still open; M0-T007/T008 blocked by B-001).
- **M1** complete. **M2** active (M2-T017 accepted; M2-T014/15/16 survey HELD).
- **M3** planned — M3-T001 accepted; M3-T002..T005 backlog (M3-T002/T003/T005 acceptance blocked by
  B-001; T005 also by B-011). **M3-T002 is now the next M3 lane** (blocked until B-001 + real durable-
  storage acceptance path).
- **M4** active — M4-T007 accepted; M4-T001..T006 merged DRAFT, G6-gated (0 published).
- **M5** planned. **M6/M7** planned.

## Candidate SECOND-WAVE lanes (evaluated, NOT contracted — owner deferred)
Per D-003 §"second wave": (1) M3-T002 immutable capture/CAS/version-detection — **only if B-001 resolves
+ a real durable-storage acceptance path exists** (else do not run fixture-only to fill a tab); (2) a new
integration task wiring the accepted M2-T017 serializer into `profile/builder.py` with fail-closed tests;
(3) a new rule-engine DF-6 hardening task (missing optional inputs inside exception predicates ->
indeterminate/professional-review, never silently false). Assign IDs only after ledger reconciliation;
prove disjoint ownership; fresh worktrees from a new frozen main SHA; do NOT reuse old branches/worktrees.

## Non-blocking follow-ups (logged, not yet tasked)
- M4-T007 (G5 LOW): bound `to_exact`/`quantize` decimal-exponent/`ndigits` (defense-in-depth; unreachable
  via validated `evaluate()` today). M2-T017 (G5 LOW): bound `input_vintages` map when a runtime writer is
  wired. Cosmetic: stale `source_fact v1 permits additional keys` comments in pluto_soda/ztldb_soda;
  M3-T001 `check_m3_t001.py` docstring cites a pre-relocation path.

## Holds / blockers
- **G6** legal approval blocks all M4 rule acceptance/publication. **B-001** Supabase token (blocks
  M0-T007/T008, M3-T002/T003/T005, auth/RLS). **B-002** Render; **B-004** Geoclient; **B-010** benchmark.
  **B-011** construction-code scope (blocks M3-T005; owner-controlled — accepting M3-T001 did NOT approve
  it). **B-012** deploy hold; **B-013** owner DECLINED frontend age-only exception. **B-014 RESOLVED.**
  **LOW-1** (M0-T025 backlog). Expansion + survey holds remain.

## Next action
Owner's call. The first wave is fully merged and reconciled; the second wave is contracted only on an
explicit go-ahead (and only for genuinely acceptance-ready, disjoint lanes). PR #64 (M0-T019) stays open
and HELD until its eligibility timestamp.
