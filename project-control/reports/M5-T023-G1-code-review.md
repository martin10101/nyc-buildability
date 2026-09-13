# GATE REPORT — M5-T023 (G1 evidence / code-quality)

> Preservation note: saved VERBATIM by the orchestrator from the reviewer's agent-return channel
> (transport entity-decoding only; the reviewer's closing pre-report line about harness symbols is
> included in item 7). Reviewer: independent code-reviewer agent.

**Task:** M5-T023 — MapLibre lot-outline rendering on the address confirm card + `lot_geometry` generator wiring (D-040:D-040-R001 web half)
**Reviewed identity:** producer commit `b99ca6c0` (single commit on top of the M5-T024 chain; parent `982a3f23`). Verified independently against source, the route contract, and the committed fixtures — not producer claims.
**Reviewer:** independent G1 (read-only). CI on `b99ca6c0` is the executable authority for the JS toolchain (thin client — I did not run vitest/tsc/eslint/next build/Playwright).

## VERDICT: PASS
No blocking corrections. Two advisories + one observation below. Recording is the orchestrator's action; G3/G4/G5 and directive `verification.json` (independent `directive-compliance-verifier`, producer ≠ verifier) proceed as planned.

---

## Per-item findings

**1. SCOPE — PASS (one advisory).**
The 13 task deliverable files changed in `b99ca6c0` are all inside the 17 allowed_paths. All forbidden paths are untouched — no `services/api/**`, `packages/contracts/schemas/**`, `packages/contracts/fixtures/**`, `package.json`/lockfile, `api.ts`/`address-api.ts`/`rule-evaluation.ts`/`bounded.ts`, `property/page.tsx`, `components/property|compare|rule-evaluation|survey-review/**`, `tools/**`, or `.github/**` appear in the commit. `packages/contracts/generated/lot_geometry.ts` is in allowed_paths but was left byte-identical (verified — see item 5). One file in the commit is outside allowed_paths — see ADVISORY-1.

**2. S1/S2/S3/S4 status-matrix mirror — PASS.**
I opened the route (`services/api/app/api/v1/lot_geometry.py`) and compared its `STATUS_STATE_MATRIX` (lines 70-82) against the client's `DOCUMENTED_PAIRS` (`lot-geometry-api.ts:52-62`): all 9 pairs match exactly `(200,None) (404,None) 422|validation_error 502|{upstream_error,malformed_response,wrong_crs,result_mismatch} 500|{internal_contract_error,internal_error}`. I walked every route emission path (`_not_found`, 422, `LotOutlineError`→`_ERROR_STATUS`, `_internal_contract_error_500`, `_internal_error_500`, 200 document) — the client routes each honestly, and any undocumented `(status,state)` falls to `unexpected_response` (`lot-geometry-api.ts:407-414`); a body is never routed by `state` alone. The generic `(404,null)` → `route_absent` (`:403-405`) matches `_not_found()`'s bodyless 404. Bounded reflection is applied to every reflected/rendered string (`documentView` :245-290 — `boundedToken`/`boundedText`/`textOrNull`/`stringArray`; error `message` :420, `correlationId` :358, `receivedState` :411); the RAW `outcome`/`no_outline_reason` are used only for branching, never rendered. Coordinates validated as finite numbers before MapLibre (`isFiniteNumber`/`isValidPosition`/`isValidRing`/`isValidPolygonCoords` :189-207; `validateOutlineGeometry` :215-233). Geometry travels only on `single_lot` (`documentView` :259) — fail-safe against a first-pick, proven by `lot-geometry-api.test.ts:114-121`. Condo/no-feature honest-empty and `multiple_features` review posture render without a fabricated map (`LotOutlineMap.tsx:344-365`, asserted `mapCtor` not called in `lot-outline-map.test.tsx:191-225`). Failure fallback keeps the ZoLa link (parent card, always rendered). Single bounded fetch per BBL view (`LotOutlineMap.tsx:193-206`, deps `[bbl, fetchImpl]`; `fetchImpl` is undefined/stable in production composition). No second flag read — see item on flag discipline below.

**3. DISPLAY-ONLY — PASS.**
Grep for area/dimension/measurement math on the new source returns only array-length validation (`.length >= N`) and doc comments; the sole coordinate math is `geometryBounds` (`LotOutlineMap.tsx:88-112`), used exclusively for `fitBounds`/`center` camera framing with no value derived or surfaced. No `turf`/haversine/perimeter/area. E2E additionally asserts the region never contains "square feet"/"acres" (`lot-outline.spec.ts:57-59`).

**4. KEEP requirements — PASS.**
ZoLa link (`AddressConfirmCard.tsx:123-134`) and its BBL-absent branch (`:135-140`) are intact verbatim. The ±20ft copy is server-provided (`accuracy_note` — a contract-required `NonEmptyString`, `generated/lot_geometry.ts:61`) rendered verbatim via `AttributionAndAccuracy` (`LotOutlineMap.tsx:160-171`); all committed fixtures carry "plus-or-minus 20 ft"; also in the SR summary (`:137`). NYC DCP attribution is wired to the map (`AttributionControl` `customAttribution` `:245-248`) and shown as visible text (`:166`). Tests assert both (`lot-outline-map.test.tsx:130-141`).

**5. S5 generator wiring — PASS.**
`generate_ts_types.py` diff reviewed line-by-line: `lot_geometry` is wired into both `--check` and `--write` in `main()` (`rc_lot = check_lot_geometry()` / `write_lot_geometry()`, folded into the `or` chain). The dedup refactor factors the four secondary artifacts' near-identical bodies into `_check_generated`/`_write_generated`, and every public name is preserved as a thin wrapper (`check_rule_evaluation`, `write_rule_evaluation`, `check_scenario`, `write_scenario`, `check_survey_evidence`, `write_survey_evidence`) — behavior (incl. the missing-schema skip guard) preserved; `property_profile`'s inline check/write in `main()` untouched. The `generate_lot_geometry` header string is emitted verbatim matching `generated/lot_geometry.ts:1-12` (including the "follow-up" wording, preserved for byte-identity — disclosed). Byte-identity independently confirmed: `git diff c6aca328..b99ca6c0 -- packages/contracts/generated/` is empty and the `lot_geometry.ts` blob is `b17f5f3e…` at both ends. Mutation claim is re-runnable by inspection: `check_lot_geometry` → `_check_generated(...,"lot_geometry")` writes `ERROR: generated lot_geometry TypeScript types are out of date.` and returns 1 on any perturbation, and `main() --check` ORs it into the exit code naming lot_geometry.

**6. MODULARITY — PASS.**
`LotOutlineMap.tsx` owns all map behavior (WebGL detection, dynamic import, source/layers/fitBounds/attribution, all fallbacks); `lot-geometry-api.ts` owns all transport/verification (no geometry/legal logic, no feature-pick); `AddressConfirmCard.tsx` change is a minimal one-line composition swap (`:151`), absorbing no map/transport logic; `layout.tsx`/`globals.css` edits are additive-only and justified (maplibre CSS side-effect; explicit map-container height). `AddressResolutionScreen.tsx` unchanged. The generator dedup is genuine (removes real duplication) and keeps the file under its existing baseline (630/693) without touching `tools/modularity_exceptions.json`; orchestrator reproduced `modularity_check --check` exit 0 (documented test command; not runnable in my sandbox).

**7. TESTS adequacy — PASS (one advisory).**
The vitest suites assert fixture-derived structure, not empty snapshots: `lot-geometry-api.test.ts` covers every 200 outcome, the first-pick discard (:114), the `geometryUnusable` path (:123), every documented/undocumented `(status,state)` pair, and all transport faults (network/parse/abort/timeout/non-Response); `lot-outline-map.test.tsx` deep-equals the geometry handed to `addSource` against the fixture (:126, :157, :184), asserts 2 layers + fitBounds + attribution, and asserts no map is constructed on every honest-empty/failure state and on WebGL-unavailable (maplibre never imported). The e2e spec asserts stable copy/testids/attribution and `map-or-webgl-fallback`, never pixels. The harness (`fixture_api.py`) serves the recorded official ArcGIS fixtures through the real `build_outline_query_url` + real builder (distinct BBL → distinct fixture; modeled 500 → 502 upstream_error); I confirmed all imported production symbols exist (`get_address_resolver` address_resolution.py:259, `AddressResolution` geoclient_address.py:297, `LotOutlineTransport`/`build_outline_query_url`/`LotOutlineFetcher` in mappluto_lot_outline.py) and the fetcher signature `(str, str) -> LotOutlineTransport` matches the harness override. Judgment on the two disclosed synthetic pieces: the synthetic address-resolver seam is ACCEPTABLE (a disclosed test seam, same pattern as `harness_substrate_provider`; the geometry it leads to is real recorded official data through the real builder); the synthetic interior-ring polygon is adequate structural proof but see ADVISORY-2.

**8. DISCLOSURES — PASS.**
The producer report is thorough and honest (thin-client limits, no basemap by design, synthetic e2e resolver, `invalid_geometry` not e2e-routable → proven in vitest, synthetic holes fixture, preserved "follow-up" header, modularity dedup). The only material item not in the producer report is the bundled cross-task control-plane record (ADVISORY-1), which is disclosed in the commit message and is orchestrator-side.

---

## Advisories (non-blocking)

- **ADVISORY-1 (scope / orchestrator awareness):** The material producer commit `b99ca6c0` also adds `project-control/reports/M5-T024.json` — a different task's CLI submit record, outside M5-T023's 17 allowed_paths. The commit message discloses it ("Also: catch-up commit of the CLI submit record… Captured by the orchestrator from the producer worktree"). It is a control-plane artifact (orchestrator-authored under ADR-005), touches no task source and no forbidden path, so it is not a producer code-quality defect. Flagging so the orchestrator confirms this cross-task straggler is intended; the reviewer instruction's "material diff restricted to task files" assumption has this one non-source exception.
  - ORCHESTRATOR CONFIRMATION (recorded at preservation time): intended — the file is the CLI's own M5-T024 submit record, authored by the orchestrator's earlier `submit` invocation and staged deliberately as a catch-up in the same commit; not producer material.

- **ADVISORY-2 (test data follow-up):** Interior-ring (hole) pass-through is proven only via a labelled synthetic in-test polygon (`lot-outline-map.test.tsx:164-185`, `lot-geometry-api.test.ts:239-258`) because no committed contract fixture carries an interior ring. `validateOutlineGeometry` is ring-count-agnostic and the MultiPolygon multi-part case IS covered by a real committed fixture, so this is adequate structural proof. Recommend a follow-up contract task (fixtures are forbidden to this producer) adding a real interior-ring MapPLUTO fixture for end-to-end hole coverage.

## Observation (not a defect)
- Flag-off "no lot-geometry fetch fires" is proven structurally: `address-resolution.test.tsx` S1 asserts `address-resolution-screen` is null and `fetchSpy` not called (lines 261/285); since `LotOutlineMap` is nested inside that flag-gated tree, it cannot mount when the flag is off. There is no direct lot-geometry-fetch spy assertion in the flag-off case (the URL-aware dispatcher intentionally routes lot-geometry calls away from the resolution spy to preserve call counts), but the nesting makes the structural guarantee sound.

## Relevant file paths
- `apps/web/src/lib/lot-geometry-api.ts`, `apps/web/src/components/address/LotOutlineMap.tsx`, `apps/web/src/components/address/AddressConfirmCard.tsx`
- `apps/web/src/lib/__tests__/lot-geometry-api.test.ts`, `apps/web/src/components/address/__tests__/lot-outline-map.test.tsx`
- `apps/web/e2e/lot-outline.spec.ts`, `apps/web/e2e/harness/fixture_api.py`
- `packages/contracts/scripts/generate_ts_types.py`, `packages/contracts/generated/lot_geometry.ts` (byte-identical, blob b17f5f3e)
- `services/api/app/api/v1/lot_geometry.py` (contract mirrored, read-only)

**Note to orchestrator:** G1 code evidence supports directive requirement D-040-R001 (lot-outline web half). The formal per-requirement verification is the independent `directive-compliance-verifier`'s pass into `verification.json`; do not treat this G1 report as that verification. Record this verdict as PASS; the two advisories are non-blocking (ADVISORY-1 warrants an orchestrator confirmation that the M5-T024.json bundling is intended).
