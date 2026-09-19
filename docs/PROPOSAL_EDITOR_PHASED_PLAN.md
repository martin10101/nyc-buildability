# Proposal-Editor Phased Plan (D-076, owner "Plan it" 2026-09-19)

Owner-endorsed order (source: the owner's research conversation + D-076 capture):
finish the dependable calculations → a simple proposal editor → assisted PDF import →
DWG/richer models. This plan turns that into packet-sized, gated increments grounded in
the machinery that already exists. Authority: D-076-R001 (this plan), R002 (honesty
rules every packet carries), R003 (the scoped hold release and its hard boundary).

## 0. Standing honesty rules (D-076-R002 — binding text for every packet below)

- A proposed building is a THIRD input class: never a city record, never a rule.
  Every proposal-derived number is a labeled proposed scenario (D-073-R006).
- AI may assist recognition (lines, boundaries, annotations); every measurement and
  rule comparison runs through the tested deterministic code.
- A drawing-derived area total is never auto-treated as zoning floor area; inclusions/
  exclusions are applied explicitly.
- Supported-check PASS / FAIL / COULD-NOT-CHECK stay distinct; a passing subset is never
  presented as whole-building approval.
- Survey/drawing vs city-mapping disagreements stay visible, never silently reconciled.

## Phase A — dependable per-property calculations (IN FLIGHT; nothing new here)

The current lanes (condo billing-BBL wiring; address→lot identity honesty) plus the
release backlog. Phase B starts feeding the loops as these close (D-075 continuity).

## Phase B — the proposal editor (flat: outline, walls, floors, heights)

**What exists to build on.** The deterministic evaluation route (rule engine + traces +
evidence), the scenario package (`services/api/app/scenario/`: contract, builder,
comparison, ranking, sensitivity, unused_floor_area), the spatial substrate (lot geometry,
EPSG:2263 measurement discipline), and the architect web surfaces (evaluation screen,
evidence panel, printed brief, scenario workspace). The editor is a NEW INPUT SURFACE for
this machinery — not a new engine.

**Proposal data model (B0 — the contract-shaped core decision).** A `proposed_massing`
scenario input: lot-anchored building outline (2263 feet, vertex list), per-level records
(floor count, floor-to-floor heights, per-level outline where it differs), named exterior
wall segments with their distance-to-lot-line/street-line derivations, and a provenance
stamp (`author=architect`, `kind=proposed`, editor version, parent scenario id). Additive
contract work through the accepted contract tooling with version bump — this is the ONLY
phase-B packet allowed to touch contract schemas, and it is Tier B (named specialist
review) by nature.

**Packet sequence (each a normal gated packet; producer/gates as noted):**

| # | Packet | Producer | Gates | Contents |
|---|---|---|---|---|
| B0 | Proposal scenario contract + validation | backend-engineer | G0,G1,G2,G3,G4,G5 | The `proposed_massing` input class (schema, additive version bump), server-side validation (geometry sanity, units, closed outline, level consistency), typed refusals; NO evaluation change yet |
| B1 | Deterministic derivation module | backend-engineer | G0,G2,G3,G4,G5 | From a valid proposal: footprint area, lot coverage, per-level areas, gross-vs-declared floor-area treatment (explicit inclusions/exclusions vocabulary), wall setbacks from lot/street lines (consuming the existing street-width attestation seam), height per level — all with evidence records; property tests against hand-computed fixtures |
| B2 | Rule-engine wiring: proposal-conditioned checks | rules-engineer | G0,G2,G3,G4,G5 | The existing published/needs_review rule families evaluated against proposal-derived facts (yards, coverage, FAR, height/setback where street width is attested); every result carries the proposal's scenario label; COULD-NOT-CHECK stays a first-class outcome |
| B3 | Editor UI increment 1: outline + heights, recalculation | frontend-engineer | G0,G1,G2,G3,G4,G5 + HJ | Draw/adjust the outline on the existing lot-outline map (MapLibre, display CRS discipline: edit in display, measure server-side in 2263), floors/heights entry, run-check button → the B2 results with numeric shortfalls ("rear yard: 18 ft provided; 20 ft required; 2 ft short"); every variation saved as a comparable scenario via the existing scenario workspace |
| B4 | Editor UI increment 2: wall nudging + affected-results propagation | frontend-engineer | G0,G2,G3,G4,G5 + HJ | Move one wall segment → server recomputes ALL affected results together (footprint, coverage, FAR, the specific yard); the affected-result set is explicit in the response so the UI can highlight what changed |
| B5 | Printed brief + comparison | frontend-engineer | G0,G2,G3,G4,G5 + HJ | Proposed scenarios in the printed brief and the existing comparison surface, permanently labeled proposed; records vs proposals vs calculated allowances visually distinct |

**Owner-review checkpoint (named, per D-076-R003):** after B3 lands, a plain-English
demo/report goes to the owner before B4/B5 proceed if any design question surfaced; any
3D/visual-massing ambition beyond this flat editor is drafted as a proposal for the owner
and stays HELD until they rule.

## Phase C — assisted PDF import (starts only after B3 is accepted and walked)

C1: PDF vector extraction service seam (select page/sheet; extract line work; typed
refusal for scan-only PDFs at first). C2: the confirm flow — units/scale confirmation
against a user-named known dimension; user confirms which polyline is the building
outline / property line / street frontage; alignment to the mapped lot with any
discrepancy shown, never auto-reconciled. C3: the confirmed geometry enters the SAME
B0 proposal contract (provenance `kind=imported_pdf`), then B1/B2 checks run unchanged.
C4: ask-only-what-is-unresolved (heights/floors from the architect when sheets don't
establish them). Real architect files become the fixture corpus BEFORE C1 is contracted
(a capture task, DB-row recorded) — supported-drawing classes are defined from real
files, not invented.

## Phase D — DWG and richer models (after C proves the workflow)

DWG parsing (layers/objects/units), richer 3D model ingestion, and any write-back
ambitions are separate future proposals; each needs its own recon + owner glance at the
plan level first. Nothing in D is authorized by D-076.

## Sequencing & lanes

Phase B packets are pairwise-disjoint by construction (contract vs derivation vs rules
vs web) and feed the loops under D-072/D-075 as current lanes close: B0 first (everything
depends on the contract), then B1 ∥ B3-scaffold, then B2, then B3 live, then B4/B5.
Follow-ups already queued from tonight's lanes (DB-031 multi-lot records-view channel;
the record-address channel) slot naturally beside phase B — DB-031's channel design and
B0's contract work belong to the same review conversation and must not fork competing
shapes.

## What this plan does NOT do

No 19-task expansion pack revival, no GDS P1–P8 application, no 3D massing engine, no
master-plan rewrite on the old pack's instruction (D-076-R003). The first demonstration
target stays concrete: one real property, the architect draws an outline, sets heights,
moves a wall two feet, and every affected number updates with its evidence.
