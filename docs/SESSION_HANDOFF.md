# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff - seq 104: 190 accepted; R001 SERVER half DONE (M5-T020 lot-geometry route); MapLibre admission + web rendering remain

Generated 2026-09-12 ~10:50 ET by the same orchestrator session (seq-103 continuation). Root
`C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch `candidate/D-024-mrl-option-b`, HEAD
`2b8a6619` **pushed**. `main` untouched at `d8b3899f`. PR #241 OPEN - NEVER merge.

## STATE (verify live; ledger wins)

1. **Accepted = 190.** NEW since seq 103: **M5-T020 (190th, D-040-R001 SERVER half)** ACCEPTED -
   display-only EPSG:4326 MapPLUTO lot-outline transport (new focused module importing the
   BYTE-IMMUTABLE 2263 connector's discipline; no measurement from 4326 coords) + body-less
   flag-gated GET /api/v1/properties/{bbl}/lot-geometry (typed outcomes: single_lot /
   no_outline condo-unit / multiple_features-review never-first-pick / invalid_geometry) +
   NEW closed lot_geometry contract (both copies byte-identical + generated TS with an
   in-suite structural drift guard) + 6 LIVE-CAPTURED f=geojson&outSR=4326 fixtures (G1
   re-fetched LOT01's manifest URL live: byte-for-byte match) + 2 documented synthetics.
   Arc: G1(data-contract)/G4/G5 PASS; G4 required corrections (LOT05 holes assertions +
   TS guard, a3d59e03) discharged w/ empirical mutant kills; DCV row at 3c11a701 (identity
   ee2d7b2a; SERVER half verified - R001 stays OPEN at directive level until the web half);
   accept 2b8a6619. Follow-up backlog: generator/CI wiring for lot_geometry.ts BEFORE the
   web packet consumes it; transport resilience (G5 LOW-1..4); G4 A1-A6.
   Seq-103 recap: **M5-T019 (189th, D-040-R002 flag unification)**
   ACCEPTED end-to-end - the web rule-evaluation flag now reads the canonical
   INTERNAL_RULE_EVAL_ENABLED (design-spec section 6 one-flag intent; M5-T015 G5 F-1
   formally CLOSED); semantics byte-preserved, old name pinned inert by a guard test;
   G1/G4/G5 all PASS zero corrections; DCV row at a8acf33b; accept 8dbcee54.
   **OWNER RETURN ITEM (R002 deploy clause):** IF the owner ever set INTERNAL_RULE_EVAL_UI
   in a Render dashboard (web service - currently withheld from render.yaml), rename it to
   INTERNAL_RULE_EVAL_ENABLED; the API service env is unchanged; no repo file needs edits.
2. **C1 recap (seq 102).** The owner's TOP product priority (D-041 C1) is DONE both halves:
   - **M5-T017 (187th, server):** `unused_draft_zoning_floor_area` section on every scenario
     document - draft FAR cap MINUS PLUTO existing built floor area, cap verbatim, states
     computed/over_built/not_computable, honest negative preserved + routed to professional
     review (root PRR = fail_safe OR over_built), typed not-computable reasons, per-input
     provenance, machine-readable ZR 12-10 tax-lot-as-zoning-lot assumption, precise-noun
     label. New focused module `services/api/app/scenario/unused_floor_area.py` (builder got
     a ~13-line wire-in); the CLOSED contract gained the required key in BOTH schema copies +
     4 fixtures + generated scenario.ts (producer-disclosed, orchestrator-ratified expansion).
   - **M5-T018 (188th, web):** mirror-faithful validator update in
     `apps/web/src/lib/scenario-contract.ts` + `UnusedFloorAreaSection.tsx` rendering the
     line per research §3.1/§3.3 (document strings verbatim through boundedText, over-built
     statement in role=status, "No supported estimate" treatment).
   - Arc: 7/7 gates PASS (T017 G1/G4/G5; T018 G1/G3/G4/G5); ONE bounded test-only correction
     (G4's vacant-lot + fractional-remainder mutation guards, ae38a169) discharged via
     same-reviewer delta attestations incl. an empirical mutant re-run; dual DCV rows at
     0819aa20 (identities 6c4c8277 / 5ff176da); accepts at 94807b28. Reports under
     `project-control/reports/M5-T017-*` and `M5-T018-*`.
3. **CI:** combined-head runs 34690484292 (44048007) and 34691559695 (ae38a169) ALL green
   except the single owner-gated `web-dependency-security` (Next.js RCE, D-040-R004). The
   cross-layer lesson worth keeping: a REQUIRED key in the CLOSED scenario contract forces
   the hand-written web mirror validator + shared fixtures + generated TS to move in the SAME
   landing — M5-T017 alone turned web-e2e red; contracting M5-T018 restored green. Never let
   the server half merge without the web half.
4. **Advisory backlog from the C1 + R002 waves (no task contracted; owner/orchestrator triage):**
   G5-T018 A1 central bounding of the section in scenario-bounds.ts; G1-T018 A1 hoist the two
   generic check primitives into scenario-contract-checks.ts; G1-T017 A2 web consuming the
   generated contract instead of a hand mirror; G4-T017 F3 coverage-set breadth pin;
   G4-T018 F1 boundedText truncation test + F3/F4 minor pins; G5-T017 LOW-1 GET /scenario
   pre-send encode guard + LOW-2 FORBIDDEN_FACT_KEYS addition; G1-T017 A4 builder.py
   decomposition; plus the M0-T156 wave advisories (bare-CR rejection, audit_log key drift,
   status_projection normalizer, migration-manifest flip test). G3-T018 A1: Step-4 evidence
   drawer must include the C1 inputs when built.
5. **D-040 queue remaining: R001 ONLY** (Packet-3 lot outline; expansion-hold §2.1 releases
   only this increment; research complete - see NEXT ACTION). M5-T019 G4 advisories added to
   the backlog: NEXT_PUBLIC posture regression assertion; env-absent e2e (structural).
6. **Owner works in the SAME checkout in parallel** (docs commits landed mid-arc repeatedly).
   Verify foreign commits touch no in-flight allowed_paths; their pushes preempt in-flight CI
   (cancel-in-progress); hold pushes while a needed run is in flight.
7. Do not self-assign beyond D-040/D-041 scope (Part-4 gap list awaits owner triage;
   D-041-R003: no other gap-list item may cite D-041).

## NEXT ACTION (in order)

1. R001 remaining: (a) DEPENDENCY: /dependency-security admission of maplibre-gl@6.7.0
   (age-gate-passing as of 2026-09-12; Snyk clean; BSD-3-Clause; CVE-2026-85061 fixed in
   6.4.1). THIN-CLIENT LOCKFILE CONSTRAINT: no local npm - the package-lock entries
   (maplibre + ALL transitives, each age+advisory+pin+integrity-checked) must be built
   from npm-registry metadata over HTTPS and PROVEN by the CI web job (npm ci fails
   closed on a bad lock) + web-dependency-security machine gates; G5 provenance review
   required. NOTE the standing web-dependency-security red (Next.js, owner-gated) stays
   red - the job output must show the maplibre entries passing their checks. Wire the
   lot_geometry.ts generator/CI drift coverage in or before this packet. (b) WEB:
   confirm-card outline replacing lot-outline-placeholder (AddressConfirmCard.tsx
   :141-145) with MapLibre per the 3d-ui rule, consuming the ACCEPTED
   /lot-geometry route + lot_geometry.ts; MultiPolygon/holes/condo-empty/review honest
   states; ZoLa link + approximate-outline (+/-20ft) copy kept; G3 in the wave.
2. Owner return items outstanding: credentials (Supabase B-001 + Geoclient B-004 - the real
   end-to-end unlock), Next.js upgrade authorization (retires the last CI red), Render
   env-var rename (with R002), G6 legal sign-off (M4 chain).

## STANDING RESTRICTIONS (unchanged)

NEVER merge PR #241. Supervisor frozen/SHADOW-ONLY (changes need cited D-024-R###). Expansion
hold except the §2.1 lot-outline release. No bare `git stash`. No new packages without
/dependency-security admission. No hosted web deploy before the Next.js RCE fix (owner-gated).
API URL private; Geoclient key ONLY in owner env + Render dashboard. Thin client (no local
npm). G6 on M4-T001 = owner-only. Stop-and-ask only for credentials/payments/legal (D-008).
Bootstrap Gate 0 before any write.

## AUTHORITATIVE FILES (smallest set)

`project-control/state.json` + `directives/D-040-scoped-unblocks/` (the queue) +
`directives/D-041-c1-development-rights/` (delivered; verification rows are the DCV-row
shape precedent) · `tasks/M5-T017.json` + `tasks/M5-T018.json` + `reports/M5-T01{7,8}-*`
(the freshest dual-task arc: ratified scope expansion, cross-layer contract coupling, delta
attestations, dual DCV) · `docs/design/astra-presentation-research.md` (the presentation
contract for future UI work) · `.claude/rules/expansion-agent-dispatch-hold.md` §2.1 ·
`CLAUDE.md` · this file.

## COPY INTO THE NEW SESSION

resume from handoff seq 104: work from durable repository evidence. Verify root/branch/HEAD
(expect C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 on candidate/D-024-mrl-option-b), Bootstrap
Gate 0, read CLAUDE.md + docs/SESSION_HANDOFF.md, run `python tools/project_control.py status`,
reconcile vs live git/CI (origin may have advanced; ledger and CI win). 190 accepted; C1 +
D-040 R003/R002 + R001-server all done. Execute NEXT-ACTION item 1: maplibre-gl@6.7.0
dependency admission (/dependency-security; thin-client lockfile-from-registry-metadata,
CI-proven) then the web outline packet, both citing D-040:D-040-R001, pinning the research
+ the accepted M5-T020 route/contract. Report READY TO RESUME or BLOCKED before changing
anything. Stop only for owner-only items (credentials/payments/legal, PR #241, Next.js
upgrade/deploy, Supabase, G6).
