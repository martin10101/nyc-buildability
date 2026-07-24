# M0-T024 — Producer report (control consolidation under D-002)

**Producer:** orchestrator (controller tab). **Base:** post-#97 `origin/main` `2d44b47`.
**Branch:** `control/D-002-consolidation-2026-07-24`. Control-plane only — no product code, no
shared-hotspot edits, no producer dispatch in this tab.

## What was done (maps to D-002 CTRL requirements; evidence in M0-T024-evidence-map.json)
1. **PR #97 (D-001)** — verified all Section-1 identities matched (head 9bc1f13; reviewed ed8a6776;
   content 9ab6c960; post-review diff = project-control-only/evidence; CI + directive verification
   green; no unreviewed product code), then **accepted M0-T023 and merged #97** (merge `2d44b47`),
   fast-forwarded local main, and read the merged D-001 control system. (R004-R006)
2. **LOW-1** recorded durably as backlog task **M0-T025** + `M0-T024-LOW-1.md` (path containment for
   trusted checked-in `requirements_file`/`verification_file`; fail-closed preserved; not implemented;
   not a wave blocker). No re-amendment of #97. (R007-R011)
3. **D-002 captured** verbatim (`source-001.md`, sha256 aead44b8) at frozen 2d44b47; decomposed into
   69 atomic requirements (40 CTRL / 14 PROD / 15 POST) with scoped applicability (no wildcards);
   manifest + v2 verification + index registered active. `validate_directive_compliance.py --check`
   PASS (2 active directives). D-002 was confirmed available before use. (R012-R016)
4. **Reconciled** the seven open PRs (full inspection, not chat summaries) and recorded per-PR
   carried/superseded/unresolved dispositions in `M0-T024-PR-DISPOSITIONS.md`. Ported the currently
   valid control changes onto post-#97 main: M3 five-task chain + Document Evidence Verification Engine
   (#93); whole-system A-J analysis + DF matrix + B-014 (#95); frontend target + B-012 + B-013
   (age-only exception DECLINED) + M0-T019 eligibility (#94); B-011; B-001 M3-acceptance references.
   One refreshed `docs/SESSION_HANDOFF.md`; contradictory handoffs superseded. All holds (G6, B-001,
   B-002, B-004, B-010..B-014, survey, expansion, paid, deployment) preserved. (R017-R029, R031)
5. **First-wave integration contract** (`FIRST-WAVE-INTEGRATION-CONTRACT.md`) freezes every §5 field
   per producer and proves disjoint ownership + no unmerged-sibling dependency via a semantic-collision
   matrix; reserves the shared hotspots for controller/integration only. (R032-R035)
6. **Wave selection**: 3 genuinely-independent lanes contracted — M3-T001 (legal-source authority),
   M4-T007 (exact Decimal arithmetic / DF-2), M2-T017 (source_fact + analysis_state_transition
   hardening / DF-4/DF-5). Lane 4 (auth/RLS) intentionally idle — its acceptance path is blocked by
   B-001 + the thin-client no-local-DB rule. IDs assigned only after reconciling the authoritative
   ledger. Sequencing recorded (M3-T002 needs accepted M3-T001; no orchestrator-on-unmerged; M0-T019
   held). (R040-R044)
7. Communicated compactly — one continuous run, no per-substep owner returns. (R001-R003, R065)

## Self-check evidence
- `python tools/validate_directive_compliance.py --check` -> EXIT 0 (2 active directives).
- `python tools/test_project_control.py` -> 14/14 groups PASS (incl. S9 regime/identity proofs).
- `python -c` recompute of D-002 requirements id/content digests matches manifest.
- Per-task ref coverage: M0-T024 40/40; M3-T001/M4-T007/M2-T017 14/14 each.
- `git status` — only intended project-control/ + docs/SESSION_HANDOFF.md paths staged; agent-memory
  noise never staged.

## Rework (after independent gate round 1)
Round-1 independent review found real defects; reworked at the corrected identity:
- **G4 control-plane FAIL (fixed):** `B-011` `detail` carried bare tokens `M3-T001` and `M3-T004`, so
  `_blocker_references` made open B-011 spuriously block acceptance of first-wave lane 1 (M3-T001) and
  couple M3-T004. Reworded B-011 so only `M3-T005` is matchable; re-verified: no open blocker blocks any
  first-wave task; M3-T002/T003 blocked by B-001, M3-T005 by B-001+B-011. Gate reports saved under
  `project-control/reports/M0-T024-G3.md`, `-G4.md`, `-G5.md`.
- **CI control-plane FAIL (fixed):** `tools/test_directive_compliance.py::MultipleDirectivesTest` squatted
  on the id `D-002` as a synthetic fixture and asserted the real registry was exactly `{D-001}` — a latent
  bug that any real second directive triggers. D-002 was genuinely free in the registry (only D-001
  present) and is the owner's expected id, so D-002 is kept; the fixture is moved to a reserved synthetic
  id `D-900` with a robust (subset) coexistence assertion. Controller-only test-maintenance (D-002 §6);
  M0-T024 allowed_paths extended to that single test file. `test_directive_compliance.py` 55/55 PASS.
- **G3 advisory (applied):** superseding banner added atop the ported `M3-CORPUS-REPLAN-PROPOSAL.md`.

## Not done here (by design)
- Worktrees + capsules (D-002 §8/§9) happen only AFTER this consolidation PR is accepted+merged.
- Product implementation of M3-T001/M4-T007/M2-T017 is for the blind producer tabs, not this tab.
- Stale-PR closure happens after merge; #64 is NOT closed (unresolved changes owed by held M0-T019).
