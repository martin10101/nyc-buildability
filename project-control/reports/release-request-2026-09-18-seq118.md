# Release request — accepted panel + street-dependent FAR to the internal deployment (D-073-R007)

Prepared 2026-09-18 (seq-118) as the ONE consolidated owner request D-073-R007 requires:
exact version, included changes, verification results, recovery path. Owner executes the
dashboard steps (D-043-R003 — no agent touches Render); everything below is preparation.

## 1. Exact version

- **Branch:** `candidate/D-024-mrl-option-b` (both services already point at it).
- **Deploy target:** the current branch head `7936aeb2` (or any later head the orchestrator
  names at execution time). Verified: `git diff 6504a2b0..7936aeb2 -- services/ apps/ packages/`
  is EMPTY — every commit after the M5-T037 acceptance seam is control-plane/docs only, so the
  head is product-material identical to the accepted, CI-green state (M5-T037 restamp
  `1179357c`; M5-T038 material CI at `8c089343`; per-task CI evidence in
  `project-control/reports/M5-T03*-ci-*.md` class records).
- **Status vocabulary (explicit):** all four lanes are ACCEPTED (ledger 222). PR #241 stays
  OPEN — merge is NOT part of this release (standing hold). LIVE-AND-VERIFIED is reached only
  after §4 below passes on the deployed services.

## 2. Included changes since the last live capture (backend `f0e7d82f`, 2026-09-17)

1. **Zoning context panel (M5-T036):** districts/overlays/special districts/landmark
   designations we already retrieve, displayed with provenance + validated ZoLa link.
   Displaying-vs-computing distinction preserved; flood flags deliberately omitted (tracked
   DB-017, open).
2. **Street-dependent conditional FAR end-to-end (M5-T037 + M5-T035):** rule_evaluation
   v1.1.0 additive contract; wide-street block (FAR row, governing FAR, D-052 provenance)
   reaches DevelopmentLimits, CalculationEvidence, and the printed brief from ONE validated
   document; DB-020 digest fix included. DRAFT-pending-legal-review labeling intact.
3. **Address-flow reliability polish (M5-T038):** never-retried `rejected` outcome for 4xx,
   timeout/focus test coverage, honest malformed-failure copy, a11y glyph fixes, landmark
   coverage badges.
4. **Named-street override matcher module (M5-T039):** inert in this release — no consumer
   imports it yet (wiring is M5-T040, in progress); the amended zr-12-10 snapshot repair
   (both copies) IS included and is the corrected source of record.
5. Wide-street engine hardening (M5-T035): provider ceilings, checklist §6c/§6d rows.

## 3. Owner dashboard steps (checklist refs; ~10 minutes)

On **nycdf-api** (Environment, then Manual Deploy from branch head):
1. Confirm/set `PYTHON_VERSION` = `3.12.11` (checklist §6d; DB-004 — geometry pin fails
   closed without it).
2. Confirm `INTERNAL_RULE_EVAL_ENABLED` = `1` (§6).
3. Read and record `LIVE_SPATIAL_PROVIDER_ENABLED` (§6a/§6b — the still-open D-059-R004
   confirmation); set to `1` for live spatial answers.
4. **NEW:** set `LIVE_WIDE_STREET_PROVIDER_ENABLED` = `1` (§6c) — this is what makes the
   street-dependent FAR LIVE instead of the conservative fail-safe.
5. Deploy; confirm `/api/v1/health` 200.

On **nycdf-web**: Manual Deploy (rebuild) from branch head. No env change needed
(`NEXT_PUBLIC_API_BASE_URL` unchanged; `INTERNAL_RULE_EVAL_ENABLED` already set per §2).

## 4. Post-deploy verification (owner device or orchestrator-guided)

1. §6b probe 1: control parcel `1008350041` rule-evaluation — expect a real district (or the
   documented split-zone `geometry_uncertain` refusal), not uniform
   `spatial_intersection_absent`.
2. §6c: a wide-street-adjacent parcel shows the conditional FAR row on the development-limits
   screen AND the printed brief, with DRAFT marking; a parcel near Broadway W94-97 / Allen St
   resolves to professional review (honest — wiring not yet released).
3. §9 walk: address resolves end-to-end; complete-address search and manual fallback preserve
   input; note observed search latency against the 6-second deadline (DB-008 WATCH:
   investigate from observed behavior, not by raising the deadline).
4. Re-check ZTLDB `rowsUpdatedAt` (DB-003 WATCH row).

## 5. Recovery path

`docs/DEPLOYMENT_AND_ROLLBACK.md` §2.1/§2.2: Render dashboard → service → Deploys → previous
successful deploy → Rollback (old artifact reused, no rebuild). Rollbacks do NOT restore env
vars — if an env change caused the incident, fix the variable and redeploy instead (§1.3).
The two new/changed flags are individually kill-switchable: unset either and the code
fail-safes (conservative FAR / no live spatial) with zero connector calls.

## 6. What this release does NOT include

Named-street wiring (M5-T040, building now), polish cluster (M5-T041, building now),
condo→base-lot resolution (research dispatched), split-lot apportionment (DB-001), any
Supabase-backed feature (B-001), any public-launch affordance (D-043-R004), PR #241 merge.
