# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, hard rules, and workflow routes live in
`CLAUDE.md` and the specialist docs it routes to — not here.

**Verified base at `9e8c22ca8a604e8eba500b35fbc372f8a3c6eb63`** (origin/main when this was written, after
the M4-T004 merge; `git fetch` and reconcile). Milestone **M0** active; M1 accepted; M2-T012/T013
accepted. Nothing Published/Verified; every R5 rule stays `needs_review`. **CP-0032 is reserved for
M0-T019 — do not create one.**

## Merged this session (owner-authorized)
- **M4-T004** pre-endpoint fail-closed safeguards **FH-1/FH-2/FH-3** — **PR #82** merged (merge commit
  `9e8c22c`, reviewed impl `3e45524`; 24/24 CI green; G0/G3/G4/G5 PASS). Local main reconciled.

## AWAITING OWNER MERGE DECISION — M4-T005 (do not merge without authorization)
- **M4-T005** rules-evaluation ↔ property-analysis endpoint + property-screen draft surface (new
  `rule_evaluation` v1.0.0 contract; FH-4) — **PR #84 OPEN**, base main. **Frozen implementation SHA
  `84b50a722d518d0ae6c233ee38affedbdaaebea3`**; PR head `46453d8` adds gate-report/ledger markdown only
  (`84b50a7..head` delta is project-control-only; all impl/test files byte-identical to the frozen SHA).
  **MERGEABLE / CLEAN, 25/25 CI green** incl. installed-wheel `web-e2e`. **All required gates PASS at the
  frozen SHA: G0 readiness, G1 data-contract, G3 code, G4 integration (qa) + UI/a11y (human-journey),
  G5 security.** This is the **first exposure of draft rules-evaluation through an API/UI surface.**
  - Contract `packages/contracts/schemas/v1/rule_evaluation.schema.json` @1.0.0 — `$ref`s canonical
    `coverage_status` (subset enum **excludes `verified`**, never redefined); input identified BY REFERENCE
    (`bbl` + `profile_contract_version` + sha256 `input_fingerprint` + `input_provenance`), root
    `additionalProperties:false` rejects any embedded profile. **`property_profile` stays 1.4.0
    byte-identical.**
  - Endpoint `GET /api/v1/properties/{bbl}/rule-evaluation` — **disabled by default in production**
    (fail-safe flag `INTERNAL_RULE_EVAL_ENABLED`; absent/unknown → generic 404, `include_in_schema=False`).
    Rebuilds profile SERVER-SIDE (never a browser-supplied profile); `assert_not_verified` boundary;
    strict response validation; safe typed errors (no traceback/secret/path). FH-4 = `as_of_date` routed
    through `_valid_iso_date` in `detect_rule_conflicts` (additive, fail-closed). Existing
    `/properties/{bbl}` unchanged.
  - Frontend: additive property-screen surface behind a two-factor fail-safe flag (server-only
    `INTERNAL_RULE_EVAL_UI` + `?ruleeval=on`) gating render AND fetch; six UI states; keyboard/live-region
    a11y; provenance drill-down; never shown as Published/Verified/legally-final/guaranteed; optional
    enrichment (profile stays usable if eval fails).
  - Pre-merge checklist (same as prior PRs): head `46453d8` unchanged, MERGEABLE/CLEAN, 25/25 green,
    `84b50a7..head` delta project-control-only, impl/test byte-identical to `84b50a7`.

## Deployability fix landed inside M4-T005 (owner-authorized scope expansion)
web-e2e exposed a **latent M4-T001 gap**: the rule engine reads four data-resource classes from disk that
were **absent from the installed wheel** (`pip install --no-deps .` in web-e2e + the real Render deploy),
so the endpoint 500'd when deployed. Fixed by shipping all four as **package-data** (mirrors the accepted
`_contract_schemas` pattern): ZR snapshots bundled under `app/_zr_snapshots/v1/` (byte-identical,
`services/api/scripts/sync_zr_snapshots.py --check` + guard) with `snapshots.py` resolving via
`importlib.resources`+docs fallback; `app/rules/rulesets/*.rule.json` and `app/rules/schemas/v1/*.schema.json`
via `app.rules` package-data globs. Regression guard `services/api/tests/rules/test_installed_deployability.py`
pins all three declarations. **Lesson for any future rule-engine runtime resource: it must be package-data,
or the installed wheel / Render deploy breaks while source-tree tests stay green.**

## Ledger lifecycle note (merged-but-not-accepted)
M4-T002/M4-T003/M0-T021 (and M4-T004) are merged and clean-gated but remain **pre-acceptance**; M4 acceptance
is coupled to **M4-T001's outstanding G6** (owner directive: do not manufacture G6 or accept M4-T001).
M4-T005 is `awaiting_gate`/98% with all required gates PASS, PR open; it will merge **pre-acceptance** like
the others. Reconcile these states live; do not accept without owner authorization.

## Next task (owner priority after M4-T005 merges)
Natural follow-ups the M4-T005 contract deliberately kept a clean path for — confirm the exact ledger task
ID or create the smallest controlled task (never CP-0032):
1. Wire an **accepted spatial connector** into the rule-eval endpoint. Today the server-side substrate
   provider default returns `None` → honest fail-safe (`professional_review_required`); the injection seam
   `get_spatial_substrate_provider` is where a real M2-T013 substrate plugs in without touching the route.
2. A **versioned aggregate analysis endpoint** (profile + rules + scenarios + 3D) that reuses the
   `rule_evaluation` serializer unchanged (the contract is self-contained/versioned for exactly this).
3. Recorded future-hardening: M4-T004 FH-2 full `rule_series` grouping (still explicit future work), plus
   the two non-blocking LOW notes `FH-M4T005-1/2` (`project-control/reports/M4-T005-future-hardening.md`:
   spatial-uncertainty point-estimate emphasis; explicit `data_conflict` classifier branch).
Preserve throughout: draft/needs_review honesty, provenance-fail-closed, uncertainty preservation,
never-Verified, endpoint-disabled-by-default-in-production; frozen SHA + CI + G-gates (+ human-walkthrough
for UI) before merge.

## Frozen concurrent item — scheduled, owner-authorized only
- **M0-T019 / PR #64** OPEN, FROZEN at `39080822a361b6204813d2dcbd1f849b196100ea`, blocked only by its
  7-day dependency-age gate (unlocked **2026-07-22T06:10:00Z** — has now passed; verify before acting).
  At/after it: rerun ONLY the failed CI jobs at that SHA; if green, run ONLY `ci-evidence-verifier`. Do
  NOT bypass the gate, merge, regenerate the lock, weaken policy, or advance CP-0032. Owner-authorized only.

## Preserved holds (do not violate)
- Nothing Published/Verified; every R5 rule stays `needs_review`; **M4-T001 not accepted** (G6 + B-010
  outstanding — block only publication/verification + final acceptance, not continued `needs_review`
  engineering).
- **CP-0032 / M0-T019** untouched. **Expansion-planning owner-review hold** (counter-notice §2) preserved.
- **Force-push is disabled** in this environment: rebases/handoff updates are published non-destructively to
  a branch + PR (old branch/PR preserved). Do not commit directly to main. **Beware:** read-only reviewer
  agents dispatched with `git reset --hard <sha>` can move the SHARED task-branch ref under the orchestrator
  worktree — anchor on `origin/<branch>` and re-reset before recording gates (observed this session).

## Open PRs
| PR | What | State |
|----|------|-------|
| **#84** | M4-T005 rules-eval endpoint + UI | OPEN, MERGEABLE/CLEAN, 25/25 green, all gates PASS — **awaiting owner merge** |
| **#83** | This session-handoff doc | OPEN, doc-only |
| **#64** | M0-T019 frontend security + npm age-gate | Frozen; age-gate passed — owner-authorized merge only |

## Unresolved owner decisions
1. **Merge PR #84 (M4-T005)** — clean-gated, 25/25 green, all gates PASS, awaiting authorization.
2. Merge PR #83 (this handoff doc) so the next session is oriented on main.
3. M0-T019 / PR #64 merge (age-gate has passed; owner-authorized only).
4. Acceptance of merged-but-pre-acceptance M0-T021 / M4-T002 / M4-T003 / M4-T004 (M4 coupled to M4-T001 G6).
5. Credentials B-001 Supabase (highest) / B-002 Render / B-004 Geoclient.
6. Survey M2-T014/T015/T016 planning-report dispatch hold; GDS/expansion + 3D holds — preserved.
