# M2-T009 — G0 Definition-of-Ready record

- **Task:** M2-T009 — Tax-lot geometry connector (MapPLUTO ArcGIS, per-BBL)
- **Recorded by:** orchestrator (G0 administrative)
- **Date:** 2026-07-20
- **Owner authorization:** owner approval 2026-07-17 (NEXT CONNECTOR WAVE), strict order M2-T007 → M2-T008 → M2-T009. Both predecessors accepted (CP-0028, CP-0029) before this dispatch.

## Owner-required pre-dispatch revalidation (against main `fec997e`)

- Dependencies all accepted: M2-T008 (34th, CP-0029), M2-T007 (33rd, CP-0028), M1-T009.
- Spatial-scenario inputs on main: `services/api/tests/fixtures/zoning_features/**` (district polygons incl. the real R3-2 feature and nylh pages).
- Contract 1.3.0 stands; no profile integration in this packet (geometry facts join the profile under a later authorized task); STOP conditions unchanged.
- Environment changes since packet authoring, considered: repo is now PUBLIC with active ruleset `protect-main` (8 required status checks) — no packet impact; B-006/B-008/B-009 resolved — no packet impact.
- Carry-forwards folded into the dispatch brief (not packet changes):
  1. M2-T008 G3/G4 O6 — this is the FOURTH connector using the per-module retry-loop pattern; the shared-transport refactor recommendation stands but is owner-sequenced AFTER this wave (owner consolidation instruction; refactor task proposed in the post-M2-T009 report). Producer must reuse `pluto_soda` transport/digest exports read-only exactly as M2-T007/T008 did — no fourth copy of the transport itself, and no unilateral refactor (existing connector files are read-only).
  2. M2-T007 G5 O4 / M2-T008 precedent — wider secret-scan needle set in fixture tests; secretscan:allow pragma convention for any fake credentials in tests.
  3. Two-staleness quartet test pattern (reference: M2-T008 `test_s10_regression_the_two_staleness_dimensions_vary_independently`).
  4. Error-taxonomy naming aligned with M2-T007/M2-T008 plus the geometry states named in the packet.

## G0 checklist (docs/GATES_AND_CHECKPOINTS.md)

1. **Objective unambiguous** — PASS. Packet enumerates the six owner safeguards: identifier/result validation (zero/one/multiple explicit, condo billing-lot semantics per research §2.5), CRS validation before coordinate interpretation (no legal area from degrees; documented transformations), the full geometry-validity taxonomy, no-silent-repair policy with original+repaired digests and method/library recording, deterministic geometry digests with pinned Shapely/GEOS, and spatial test scenarios vs M2-T007 fixtures with named boundary-touch tolerance (±20 ft source accuracy).
2. **Dependencies accepted** — PASS (see revalidation).
3. **File scope exclusive** — PASS. New connector module(s) + new fixture dir `services/api/tests/fixtures/mappluto_geometry/` + new tests + one registry draft + own report; the ONLY shared-file touch is the Shapely dependency pin (requirements/pyproject) explicitly allowed with disclosure; 0 other tasks claimed.
4. **Inputs and outputs defined** — PASS (packet).
5. **Acceptance scenarios exist** — PASS. GEO-S1..GEO-S12 covering the geospatial scenario pack of docs/ACCEPTANCE_SCENARIO_STANDARD.md plus the owner negative list (polygon, multipolygon, holes, empty, null, self-intersection, ring closure, orientation, duplicate vertices, degenerate rings, geometry collections, multiple features).
6. **Source documentation available** — PASS. `docs/research/pluto-mappluto-2026-07-16.md` (MapPLUTO ArcGIS channel + condo semantics §2.5), zoning-features research §4.3 (±20 ft), registry draft `docs/research/source-registry-drafts/pluto-mappluto.json`.
7. **Credentials** — PASS (ArcGIS keyless; none).
8. **Required gates assigned** — PASS. G0/G1/G2/G3/G4; roster data-contract-verifier (G1), code-reviewer (G3), geospatial-engineer (G4 integration/geospatial competence per owner instruction); producer backend-engineer ∉ roster. No G5: reuses the G5-reviewed allowlist/transport pattern (M2-T007) with no new security surface; orchestrator adds G5 if the design deviates.
9. **Execution location and disk usage** — PASS. Owner-PC thin-client checkout; KB-scale fixtures; Shapely wheel is a small local pip install (tens of MB, within the 2 GB budget — DISCLOSED here as the one dependency addition; CI installs it from the pin); full CI in GitHub Actions (now unmetered, public repo).
10. **Cleanup and durable routing** — PASS. Git-committed fixtures/reports only; no persistence (B-001 stands); citywide FileGDB import remains deferred (B-001/B-002).

## Verdict

**G0 PASS** — ready; claim by backend-engineer follows in this control PR; worktree `.claude/worktrees/M2-T009`, branch `task/M2-T009-mappluto-geometry` from main after merge.
