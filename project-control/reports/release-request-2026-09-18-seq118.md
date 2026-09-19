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

Split-lot apportionment (DB-001), the condo→base-lot LIVE wiring (the resolver module and
its hardening are accepted but deliberately unconsumed until the wiring packet closes its
preconditions), any Supabase-backed feature (B-001), any public-launch affordance
(D-043-R004), PR #241 merge.

## 7. Update 2026-09-19 (same request, newer head)

Since this request was written, FOUR more pieces were accepted (224th-227th): the
named-street WIRING (M5-T040 — the honest named-street refusal with legal citation now
reaches screen and brief), the address/validator polish (M5-T041), the condo resolver
module + its pre-wiring hardening (M5-T042/M5-T044), and the wiring-module extraction
(M5-T043). All ride the same branch; at execution time deploy the then-current branch head
(product-path diff from every accepted material verified control-plane-clean per task).
Everything in §3-§5 is unchanged; the same one owner request stands.

## 8. Update 2026-09-19 (same request, overnight additions — 228th-230th)

THREE more pieces were accepted in the overnight D-075 window: the address→lot identity
honesty increment (M5-T046 — the entered-vs-matched confirm line, the equality-gate
library binding any future GeoSearch promotion, and the geosearch source-registry
record), the record-address display channel (M5-T047 — the confirm card now shows the
lot's official PLUTO record address when it differs from the matched frontage, over an
additive flag-gated route), and the condo billing-BBL live wiring (M5-T045 — the
condo→base-lot step wired fail-closed at both consumer seams behind the existing live
flag, with the registry records, the REAL key-absence fixture, and the identity-notice
display; the multi-lot records view is the recorded DB-031 successor). All ride the
same branch and the same flags posture (nothing newly enabled by default); at execution
time deploy the then-current branch head. Everything in §3-§5 is unchanged; the same
one owner request stands.


## 9. Acceptances 231-236 ride the same single owner pass (2026-09-19, session seq 119 close)

Six further acceptances landed after section 8, all fully reviewed (independent waves + DCV,
zero blocking): M5-T049 (internal matcher extraction - no product-visible change), M5-T048
(proposal scenario contract 1.1.0 - flag-gated, no live route change), M5-T050 (confirm-arc
polish riders - behind the existing address flags), M5-T052 (condo records view - behind
INTERNAL_RULE_EVAL_ENABLED like its siblings), M5-T053 (proposal validation route - same
flag posture, include_in_schema=False), M5-T051 (derivation module - pure library, no route).
FLAGS POSTURE UNCHANGED; nothing new becomes publicly reachable. The one owner pass described
in sections 1-7 covers everything through the 236th acceptance: deploy the then-current head.
