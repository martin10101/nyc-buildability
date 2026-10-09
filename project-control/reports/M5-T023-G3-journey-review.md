# G3 Human-Journey Gate Report — M5-T023

> Preservation note: saved VERBATIM by the orchestrator from the reviewer's agent-return channel
> (transport entity-decoding only). Reviewer: independent human-journey-reviewer agent.

**Task:** M5-T023 — D-040-R001 web half: MapLibre lot-outline rendering on the address confirm card + `lot_geometry` generator wiring
**Reviewed identity:** material diff `git diff c6aca328..b99ca6c0` (later commits control-plane only)
**Reviewer:** human-journey-reviewer (independent, read-only)
**Method:** Code-and-copy-level journey walkthrough (thin client cannot run a browser; CI Playwright is the executable authority). Every rendered state read and walked as the analyst/screen-reader user.

## VERDICT: PASS — with required corrections (all ADVISORY; none BLOCKING)

The encoded journey is honest, recoverable, accessible, and consistent with the existing confirm-card patterns. Every failure and empty state is specific and truthful, never a blank or misleading container, and the ZoLa escape hatch survives in every state. The e2e spec walks the real analyst journey through the real route+builder over recorded official geometry. The advisory items below should be tracked as follow-ups; they do not block acceptance. I also name below exactly what the CI Playwright/vitest/build evidence must show for G4.

---

## 1. CLARITY — PASS

- The confirm card gates `<LotOutlineMap>` on the same re-validated `canonicalBbl` as the ZoLa link (`AddressConfirmCard.tsx:151`), a minimal composition swap of the old placeholder (`:142-151`). ZoLa link block (`:123-140`) and its BBL-absent branch are unchanged verbatim (diff confirms only the placeholder `<p>` was replaced + one import added).
- The analyst immediately understands the outline is approximate, display-only, ±20 ft, DCP-attributed: `lot-outline-accuracy` renders the document's `accuracy_note` ("…plus-or-minus 20 ft…display-only…no measurement derived…") and `lot-outline-attribution` renders "NYC Department of City Planning (DCP), MapPLUTO" (`LotOutlineMap.tsx:160-171`; fixture-verified).
- Copy is honest without reading like an apology — e.g. condo: "No parcel outline is drawn: this is a condominium unit lot, which carries no polygon of its own in the official MapPLUTO data — the billing lot holds the merged complex outline." (`:346-350`); multiple_features: "…returned more than one parcel…This needs review before an outline can be trusted — the platform never silently picks one." (`:356-362`). Factual, not defensive.
- ZoLa remains the authoritative escape hatch in every state: it lives on the parent card above the map (DOM order BBL → ZoLa → LotOutlineMap), and every honest state copy directs "Open the city's ZoLa map above."

## 2. HONEST STATES — PASS

Walked each state (`LotOutlineMap.tsx` render tree + client outcome mapping):

| State | Rendered outcome | Truthful? |
|---|---|---|
| single lot (WebGL) | map + accuracy + attribution; geometry VERBATIM to source | Yes |
| single lot (no WebGL) | `lot-outline-webgl-unavailable` copy + accuracy + attribution | Yes (visible); see ADVISORY-1 for SR summary |
| geometryUnusable single_lot | `lot-outline-unavailable` honest note | Yes |
| MultiPolygon | every polygon reaches source (S2 vitest deep-equals fixture) | Yes |
| condo unit | `lot-outline-empty` names reason + billing-lot hint | Yes |
| no_feature | `lot-outline-empty` naming no lot for BBL | Yes |
| multiple_features | `lot-outline-review` posture, geometry withheld (client nulls it) | Yes |
| invalid_geometry | `lot-outline-invalid` honest note | Yes |
| route 404 / flag-off | `route_absent` → "not available in this environment" | Yes |
| network / timeout / error / malformed / unexpected | `lot-outline-unavailable` → "could not be loaded (address details unaffected)" | Yes |
| WebGL unavailable | honest fallback; maplibre never imported (asserted) | Yes |

- Fail-safe against a silent first-pick is enforced at the transport layer: `documentView` sets `geometry: isSingle ? rawGeometry : null` (`lot-geometry-api.ts:259`), and a vitest hostile case injects geometry onto a multiple_features body and asserts it is discarded (`lot-geometry-api.test.ts:114-121`).
- No state renders an empty/ambiguous container: a `document` always carries a known `OUTLINE_OUTCOMES` outcome (else it becomes `unexpected_response`, non-document), and exactly one of {document branch, non-document fallback, loading} renders when `outcome!=null`.

## 3. RECOVERY — PASS

- No dead-ends: every failure keeps the ZoLa link (parent) and states the address details are unaffected.
- No retry storm: exactly one bounded fetch per BBL view; a superseded/unmounted request is aborted and filtered (`LotOutlineMap.tsx:193-206`).
- No spinner-forever: the loading state (`outcome===null`) always settles — the client has a 12 s timeout (`DEFAULT_LOT_GEOMETRY_TIMEOUT_MS`) mapping a hung upstream to `client_timeout` (`lot-geometry-api.test.ts:218-229`), and every terminal outcome sets state. The only unset case is `aborted`, which occurs only on deps-change/unmount where a fresh fetch immediately follows or the component is gone.

## 4. ACCESSIBILITY — PASS (with ADVISORY-1)

- Labeled landmark: `role="region" aria-label="Approximate tax lot outline"` (`:286-290`).
- Screen-reader textual equivalent in every state: `lot-outline-summary` `<p role="status">` with a deterministic outcome-derived summary (`:126-158, :292-294`). The canvas is not relied on for content — the summary and the visible per-state copy carry the outcome. Consistent with the existing `address-outcome-announcer` polite live-region pattern.
- Keyboard reachability: the ZoLa link is a normal anchor (parent); the AttributionControl is MapLibre's standard labeled control; the visible loading text is `aria-hidden` to avoid double-announce.
- Visible focus / responsive: `.lot-outline-map` has explicit height (320px / 240px mobile) so the canvas never collapses to 0px (`globals.css:664-683`); design-system focus styles apply.

## 5. CONSISTENCY — PASS

- Reads as part of the card: reuses `section-note` / `failure-meta` classes, kebab `lot-outline-*` testid discipline, and the collapsed provenance `<details>` is untouched.
- Progressive disclosure kept: no ingestion internals (source_registry, digests, connector ids) leak onto the map surface; provenance stays in the collapsed disclosure. `view.notes` is mapped but intentionally not rendered on the map.
- No color-only legal meaning: the blue fill/line is decorative; all outcomes carry text. Bounded reflection intact — all reflected strings pass `boundedText`/`boundedToken`; geometry validated as finite numbers before reaching MapLibre; static `EMPTY_STYLE` (no response string interpolated into style expressions), consistent with the maplibre-gl 6.7.0 attribution-sanitization fix (CVE-2026-85061).

## 6. E2E JOURNEY FIDELITY — PASS (with ADVISORY-2)

- `lot-outline.spec.ts` walks the real journey: `?ruleeval=on` opt-in → fill address → confirm card → assert the lot-outline surface per outcome. Covers single_lot (map **or** honest WebGL fallback), condo honest-empty (names "condominium unit lot"), multiple_features review ("more than one parcel"), and upstream failure ("could not be loaded"). Assertions are on stable copy/attribution/testids, never pixels — correct given headless WebGL uncertainty.
- The synthetic address-resolver seam in `fixture_api.py` (`harness_address_resolver`, street→BBL) is an **acceptable scaffold, not a hollowed journey**: it is only the navigation vehicle to reach the confirm card (no prior task wired an address-resolution seam), while the geometry under test flows through the **real** `get_lot_outline_fetcher` seam → real route → real MapPLUTO outline builder over committed official `f=geojson&outSR=4326` fixtures. No geometry byte is hand-written. Clearly disclosed in the harness docstring and producer report.
- Client↔route contract parity verified: the client `DOCUMENTED_PAIRS` (`lot-geometry-api.ts:52-62`) exactly mirror the route `STATUS_STATE_MATRIX` (`lot_geometry.py:70-82`) — all 9 pairs match, including the (200,None) outline family and the (404,None) flag-off sentinel.

---

## Required corrections (ADVISORY — track as follow-ups, non-blocking)

- **ADVISORY-1 (screen-reader honesty gap in the no-WebGL single_lot state).** `outcomeSummary()` (`LotOutlineMap.tsx:129-158`) keys only on the typed outcome, not on `webglAvailable`/`drawable`. In the no-WebGL single_lot path — the *likely* headless-CI branch and a real user path on WebGL-blocked browsers — the `role="status"` live region announces "An approximate lot outline is shown, drawn from the official NYC City Planning MapPLUTO parcel geometry (plus or minus 20 feet)." while the visible fallback correctly says "this browser could not open an interactive map (no WebGL). Open the city's ZoLa map above." The live announcement is not truthful for that state and does not point to ZoLa. Downgraded to advisory because the truthful fallback `<p>` is not `aria-hidden`, so a screen-reader user navigating the region still reaches the correct text. Fix: make the summary account for the fallback (and reference ZoLa) when a single_lot outline exists but is not drawable.

- **ADVISORY-2 (real map render never exercised in-browser).** Because headless CI Chromium likely lacks WebGL, the single_lot e2e accepts the fallback branch, so the actual maplibre-gl render path (addSource with verbatim geometry, both layers, fitBounds, AttributionControl) is proven only by vitest with maplibre mocked plus a successful `next build`. Consider launching Playwright Chromium with software WebGL (`--use-gl=swiftshader`/angle) so the real map path is exercised at least once end-to-end; otherwise this first real render of the newly admitted dependency remains unverified in a browser. Disclosed and pre-acknowledged in the packet risk list.

- **ADVISORY-3 (weaker default when accuracy_note absent).** A 200 document passes 200-validation on `document_kind`/`display_only`/`crs`/`outcome` only; if a drifted-but-valid body omitted `accuracy_note`, the client default (`lot-geometry-api.ts:271-274`) is honest but drops the "±20 ft" phrasing. The server contract guarantees `accuracy_note`, so this is a defense-in-depth nit only.

- **ADVISORY-4 (interactive display-only map).** The map is created `interactive: true` (`LotOutlineMap.tsx:240`) for a display-only outline, adding pan/zoom/keyboard handlers with no textual affordance and a focusable canvas. Consider `interactive: false` (or documenting keyboard affordances) to better match the display-only posture.

## What the CI evidence must show (for G4 / to confirm this PASS)

1. `web` job green: TypeScript typecheck + ESLint + `next build` succeed with the first maplibre-gl import (dynamic import keeps it out of SSR; layout CSS side-effect only).
2. `web-e2e` job green: `lot-outline.spec.ts` 4 tests pass; **and the run log should reveal which branch the single_lot test took** (map vs WebGL fallback) — if fallback, note ADVISORY-2.
3. vitest green: `lot-outline-map.test.tsx` (geometry deep-equals fixture, both layers, fitBounds, attribution, honest states, no-WebGL fallback, mapCtor-not-called on empties) + `lot-geometry-api.test.ts` (all typed outcomes, malformed/timeout/abort/undocumented-pair).
4. Regression: `address-confirm.test.tsx` and `address-resolution.test.tsx` pass unchanged in intent — the flag-off S1 still asserts no fetch (surface never mounts), proving the inherited gate.
5. `python packages/contracts/scripts/generate_ts_types.py --check` exit 0 including `lot_geometry`, with `generated/lot_geometry.ts` byte-identical (orchestrator progress log already reproduced exit 0); `python tools/modularity_check.py --check` exit 0 (generator refactored under threshold).

---

**Files inspected (all absolute):**
- `apps/web/src/components/address/LotOutlineMap.tsx`
- `apps/web/src/lib/lot-geometry-api.ts`
- `apps/web/src/components/address/AddressConfirmCard.tsx`
- `apps/web/e2e/lot-outline.spec.ts`
- `apps/web/e2e/harness/fixture_api.py`
- `apps/web/src/components/address/__tests__/lot-outline-map.test.tsx`
- `apps/web/src/lib/__tests__/lot-geometry-api.test.ts`
- `apps/web/src/components/address/__tests__/address-confirm.test.tsx`
- `apps/web/src/components/address/__tests__/address-resolution.test.tsx`
- `apps/web/src/app/layout.tsx` / `globals.css`
- `services/api/app/api/v1/lot_geometry.py` (contract parity)
- `packages/contracts/fixtures/valid/lot_geometry/*` (fixture verification)
- `project-control/reports/M5-T023-producer-report.md`

**Verdict recorded for orchestrator: PASS with ADVISORY corrections 1–4 (non-blocking). No BLOCKING defects. Acceptance is conditioned on the CI evidence enumerated above being green.**
