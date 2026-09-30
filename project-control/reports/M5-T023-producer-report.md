# M5-T023 producer report — MapLibre lot-outline rendering + lot_geometry generator wiring

Task: M5-T023 (D-040:D-040-R001). Producer: frontend-engineer. Base SHA: c6aca328.
Worktree: wt-m5t023 (isolated; primary checkout untouched).

Closes the D-040-R001 web half: consumes the accepted flag-gated
`GET /api/v1/properties/{bbl}/lot-geometry` route (M5-T020) from the address confirm
card via a new hardened client + a new focused MapLibre component (first import of the
admitted `maplibre-gl@6.7.0`, M5-T022), replacing the lot-outline placeholder with honest
typed outcomes; and wires `lot_geometry` into the TS type generator's `--check`/`--write`
(the recorded M5-T020 follow-up).

## Files created / edited (complete inventory, all inside allowed_paths)

Created:
- `apps/web/src/lib/lot-geometry-api.ts` — hardened typed client.
- `apps/web/src/lib/__tests__/lot-geometry-api.test.ts` — offline client pack.
- `apps/web/src/components/address/LotOutlineMap.tsx` — focused map component.
- `apps/web/src/components/address/__tests__/lot-outline-map.test.tsx` — component pack (maplibre mocked).
- `apps/web/e2e/lot-outline.spec.ts` — Playwright human journey.
- `project-control/reports/M5-T023-producer-report.md` — this report.

Edited:
- `apps/web/src/components/address/AddressConfirmCard.tsx` — placeholder block swapped for `<LotOutlineMap>` (minimal composition; ZoLa link + BBL-absent branch kept verbatim).
- `apps/web/src/app/layout.tsx` — additive `import "maplibre-gl/dist/maplibre-gl.css";` (justified below).
- `apps/web/src/app/globals.css` — additive `.lot-outline` / `.lot-outline-map` container sizing.
- `apps/web/e2e/harness/fixture_api.py` — additive lot-outline transport seam (recorded fixtures through the real builder) + a synthetic address-resolver seam (scaffolding to reach the confirm card).
- `apps/web/src/components/address/__tests__/address-confirm.test.tsx` — placeholder assertion → new surface; fetch stub made URL-aware.
- `apps/web/src/components/address/__tests__/address-resolution.test.tsx` — fetch stubs made URL-aware (dispatcher) so the new lot-geometry fetch does not perturb the resolution-spy counts.
- `packages/contracts/scripts/generate_ts_types.py` — wired `lot_geometry` into `--check`/`--write`; refactored the four secondary artifacts' check/write into two shared helpers (modularity, see below).

`packages/contracts/generated/lot_geometry.ts` was NOT modified (byte-identical; see S5).
No file outside allowed_paths was changed. `forbidden_paths` (services/**, packages/contracts/schemas/**,
packages/contracts/fixtures/**, package.json, package-lock.json, apps/web/src/lib/{api,address-api,bounded,rule-evaluation}.ts,
apps/web/src/app/property/page.tsx, apps/web/src/components/property|compare|rule-evaluation|survey-review/**, tools/**, .github/**, …) were read-only.

## What I built, per acceptance scenario

**S1 — single_lot outline rendered.** `LotOutlineMap` fetches the outline via the hardened
client, and on a `single_lot` document with usable geometry AND a WebGL context it
dynamically imports `maplibre-gl`, creates a map on a neutral background style, adds the
contract geometry as a GeoJSON source (VERBATIM — coordinates never re-rounded), adds a
fill + line layer, `fitBounds` to a bbox computed **only** for camera framing (no value
derived or shown), and registers an `AttributionControl` carrying the NYC DCP attribution.
The `±20 ft` accuracy note and the attribution are also rendered as visible text. The ZoLa
link and its BBL-absent branch are untouched on the parent card. `lot-outline-map.test.tsx`
asserts the geometry handed to `addSource` deep-equals the fixture geometry, that fitBounds +
both layers + the attribution control fire, and that no measurement text is derived.

**S2 — MultiPolygon and holes.** The client's `validateOutlineGeometry` passes Polygon and
MultiPolygon through STRUCTURALLY UNCHANGED (every polygon, every interior ring) or returns
`null` — never a first-pick, never a dropped/filled ring. Tests assert: (a) the committed
`single_lot_multipolygon` fixture reaches `addSource` with the same polygon count; (b) a
synthetic Polygon-with-interior-hole passes both rings through (holes are absent from the
committed CONTRACT fixtures, so this structural case is proven with an in-test input, clearly
labelled — no official geometry is fabricated).

**S3 — honest empties / review.** `no_outline` renders `lot-outline-empty` naming the reason
(condo unit lot carries no polygon → billing lot holds the merged outline; or no lot for this
BBL); `multiple_features` renders `lot-outline-review` (geometry withheld, never a silent
first-pick); `invalid_geometry` renders `lot-outline-invalid`. All keyboard-reachable, all keep
the ZoLa link (parent card). No map is constructed for these (asserted: `mapCtor` not called).

**S4 — failure posture.** Generic 404 → `route_absent`; network error / timeout / undocumented
`(status,state)` / malformed body → typed outcomes; each renders `lot-outline-unavailable`
stating the outline is unavailable and keeping the ZoLa link — never a crash, never a blank
container. WebGL-unavailable on a single_lot renders `lot-outline-webgl-unavailable` (and
`maplibre-gl` is never imported — asserted). Exactly one bounded fetch per BBL view (no retry
storm). The flag-off clause ("surface never mounts, no fetch fires") is inherited structurally:
the whole surface lives inside the flag-gated `AddressResolutionScreen` tree
(`PropertyLookup.tsx:265`) and is covered by the unchanged `address-resolution.test.tsx` S1
flag-off/no-fetch tests; no second (client/NEXT_PUBLIC) flag read was added.

**S5 — generator drift coverage.** `lot_geometry` is wired into `--check` and `--write`; the
committed `generated/lot_geometry.ts` is BYTE-IDENTICAL (git blob unchanged). Proven locally
(outputs below). `ci.yml` needs no change (it already runs `--check`).

**S6 — regression / a11y / modularity.** Existing web tests updated honestly (only the placeholder
assertion + URL-aware fetch stubs; nothing weakened). The map surface is a labelled `role="region"`
with a screen-reader outcome summary (`role="status"`); the ZoLa link and any map controls are
keyboard-reachable. `modularity_check --check` exits 0.

## Self-checks I ran (thin client: no local npm/vitest/playwright/tsc; those run on CI)

1. `python packages/contracts/scripts/generate_ts_types.py --check` → **exit 0**; prints
   `OK: generated lot_geometry TypeScript types are up to date.` alongside the other four artifacts.
2. `git hash-object packages/contracts/generated/lot_geometry.ts` → `b17f5f3e98c5937cc1be903376277c57e0847faf`
   before AND after a `--write` run (byte-identical; `git diff --numstat` empty).
3. S5 mutation: appended a comment to `generated/lot_geometry.ts` → `--check` **exit 1** with
   `ERROR: generated lot_geometry TypeScript types are out of date.`; restored (hash back to `b17f5f3e…`).
4. `python -m pytest packages/contracts/scripts/tests -q` → **29 passed** (generator drift/determinism
   tests unaffected by the check/write refactor).
5. `python tools/modularity_check.py --check` → **exit 0** (was exit 1 before the generator refactor;
   see modularity note).
6. Harness proof (real route + real builder over recorded fixtures, via FastAPI TestClient):
   - `GET …/1008350041/lot-geometry` → 200 `single_lot`; `…/1000151001` → 200 `no_outline` (condo unit);
     `…/1008350096` → 200 `multiple_features`; `…/2000020002` → 502 `upstream_error`.
   - `GET /api/v1/address-resolution?street=OUTLINE AVENUE&…` → 200 `resolved`, bbl `1008350041`.
   - Direct builder run confirmed LOT01→single_lot Polygon, LOT05→single_lot Polygon(holes),
     LOT06→single_lot MultiPolygon, LOT04→no_outline condo_unit, LOT02→no_outline no_feature.

## Modularity note (required disclosure)

Wiring `lot_geometry` into `generate_ts_types.py` grew that grandfathered file past its
baseline-growth budget (baseline 630 SLOC, threshold 693; it had drifted to 648 pre-edit and my
additions pushed it to 722 → `modularity_check` FAIL). `tools/**` is forbidden to me, so I could
not add a baseline exception. I instead removed genuine duplication that the modularity policy
favors: the four SECONDARY artifacts (rule_evaluation, scenario, survey_evidence, lot_geometry)
had near-identical `check_*`/`write_*` bodies, now factored into two shared helpers
(`_check_generated`, `_write_generated`); every public function name is preserved as a thin
wrapper (the drift tests call `generate_*()`/`main()`, never `check_*` directly — verified: 29
passed). Result: 651 SLOC, 42 under threshold, `modularity_check` exit 0, and all five generated
`.ts` files remain byte-identical. property_profile's inline check/write in `main()` is untouched.

## Boundary / architecture answers

- **LotOutlineMap.tsx owns ALL map behavior** (WebGL detection, dynamic maplibre import, source/
  layers/fitBounds/attribution, and every honest fallback). It computes no measurement; the only
  coordinate math is a camera bbox with no surfaced value.
- **lot-geometry-api.ts owns ALL transport** (documented status-matrix mirror, bounded reflection,
  cancellable + time-bounded fetch, coordinate number-validation, typed outcomes). No legal/geometry
  logic; it never picks a feature or fabricates a shape.
- **AddressConfirmCard.tsx change is minimal composition**: the placeholder `<p>` became
  `{canonicalBbl ? <LotOutlineMap bbl={canonicalBbl} /> : null}` (same gate as the ZoLa link). It
  absorbs no map or transport logic; public interfaces of existing modules are unchanged.
- **Flag architecture**: no second flag read; the surface inherits `PropertyLookup.tsx:265`.
- **Contract**: consumes `packages/contracts/generated/lot_geometry.ts` shape directly; the generator
  wiring preserves the committed artifact byte-for-byte.
- **layout.tsx/globals.css**: additive only — the maplibre stylesheet (needed for map controls/canvas
  positioning) and the map container height (a canvas needs an explicit height or it collapses to 0px).

## Disclosures / limitations

- **Cannot run locally** (thin client, no node_modules): TypeScript typecheck, ESLint, `next build`,
  vitest, and Playwright. CI (`web` + `web-e2e`) is the executable authority for all JS/TS. I wrote
  the code and tests to that standard; residual risk is a type/lint nuance only CI can surface.
- **maplibre-gl CSS import is in layout.tsx** (not imported by any vitest test), so component tests
  need no CSS handling; the map JS is a DYNAMIC import mocked at the module boundary in the component
  test and never loaded on the no-WebGL path.
- **No basemap tile source is wired.** No external tile provider is in the source registry, so the
  outline draws on a neutral background rather than an orthophoto/streets basemap. Adding a vetted
  basemap (with a source_registry entry) is a reasonable follow-up; drawing the real outline without a
  basemap is honest and self-contained.
- **e2e address-resolver seam is synthetic scaffolding.** No prior task wired an address-resolution
  seam, and the confirm card (hence the lot-outline surface) is reachable only via a resolved address.
  `harness_address_resolver` maps a handful of test street names to canonical BBLs (the same test-seam
  pattern as `harness_substrate_provider`). It is clearly synthetic; the GEOMETRY it leads to is the
  REAL recorded official fixture data through the REAL builder. Flagged for the reviewer.
- **invalid_geometry is not e2e-routable by a distinct BBL** (the synthetic LOT80 fixture's feature
  carries BBL 1008350041, and the builder's single-feature result-match check would raise
  `result_mismatch` for any other requested BBL). It is proven in the offline vitest client pack via
  the committed contract fixture instead.
- **Holes fixture**: no committed CONTRACT fixture carries an interior ring; hole preservation is proven
  with an in-test synthetic Polygon-with-hole (labelled), plus the real MultiPolygon fixture for
  multi-part coverage.
- **generated/lot_geometry.ts header** still says the generator wiring is a "follow-up"; I preserved it
  verbatim because the byte-identity duty forbids changing the committed artifact. A future contract
  task could reword it (which would require regenerating the file).

## Rework round 1 (review-wave fold-ins + CI fix)

Round-1 verdicts: G1/G3/G5 PASS (advisories only); CI web-e2e FAILED. Three items addressed, same
scope/worktree, no new files.

**RC-CI-1 (BLOCKING — CI run 34735243173).** All four `lot-outline.spec.ts` tests failed at
`resolveTo()` with `getByLabel('Borough')` strict-mode violation (the page also renders a
"Borough (source code)" provenance label, so the bare label matched multiple elements). Fix: scope
every address-form input to the form container — `const form = page.getByTestId("address-form")` then
`form.getByLabel("House number"|"Street"|"Borough")` and `form.getByTestId("address-submit")`. Audited
every other locator in the spec: the rest use unique `data-testid`s (`lot-outline`, `zola-link`,
`lot-outline-map`/`-webgl-unavailable`/`-empty`/`-review`/`-unavailable`/`-accuracy`/`-attribution`),
no other ambiguity. Harness reaching the form fill in CI confirms the fixture seams work; only locator
scoping changed.

**FOLD-IN 1 (G3 ADVISORY-1 — screen-reader honesty).** `outcomeSummary()` keyed only on the typed
outcome, so the no-WebGL single_lot branch (the likely headless-CI path and a real user path) announced
"An approximate lot outline is shown…" while the visible fallback said no map could be opened. Fix:
`outcomeSummary(outcome, drawable)` now returns, for a single_lot that is present but NOT drawable
(no WebGL, or geometry unusable), a summary that says the outline could not be drawn / no interactive
map could be opened and points to the ZoLa map above. The no-WebGL vitest test now asserts the summary
contains "could not open an interactive map" and does NOT contain "An approximate lot outline is shown".

**FOLD-IN 2 (G5 F-1 — latent DOM-XSS sink).** `AttributionControl` renders `customAttribution` as HTML
(innerHTML), and `boundedText` does not neutralize HTML metacharacters, so passing the reflected
`view.attribution` bypassed React escaping. Fix: a client-side CONSTANT `DCP_ATTRIBUTION =
"NYC Department of City Planning (DCP), MapPLUTO"` is passed to the control; the reflected
`view.attribution` is kept ONLY in the React-escaped `AttributionAndAccuracy` text (safe). The map
effect no longer depends on the reflected string. New vitest assertion: a document whose attribution is
`<img src=x onerror=…>` results in the AttributionControl receiving the CONSTANT (asserted on the mock's
captured options, and that it does not contain "onerror"), while the React text shows the reflected
value inert (no `<img>` element materializes; `window.__pwned` stays undefined).

Not touched (per instruction — advisory backlog): swiftshader WebGL CI config (.github forbidden),
interior-ring contract fixture (fixtures forbidden), `interactive:false`, accuracy-note default.

**Rework self-checks (re-run locally):**
- `python packages/contracts/scripts/generate_ts_types.py --check` → **exit 0** (all five artifacts
  "up to date", incl. `lot_geometry`). No generator/contract change this round; byte-identity intact.
- `python tools/modularity_check.py --check` → **exit 0** (LotOutlineMap edits are net-neutral in size).
- Still cannot run vitest/Playwright/tsc/ESLint locally (thin client); CI remains the authority. The
  spec fix is a pure locator-scoping change validated against `AddressForm.tsx` (form has
  `data-testid="address-form"`; borough select id `address-borough`).

Files changed this round: `apps/web/src/components/address/LotOutlineMap.tsx`,
`apps/web/e2e/lot-outline.spec.ts`, `apps/web/src/components/address/__tests__/lot-outline-map.test.tsx`,
and this report.

## Rework round 2 (CI closure — locator exact-match)

Round-1's form-scoping was insufficient (CI run 34735830129, same 4 tests): `getByLabel` matches
case-insensitive SUBSTRING by default, and INSIDE the form two labels contain "borough" — the
"Borough" select and the "ZIP code (alternative to borough)" input (AddressForm.tsx:130) — so the
in-form collision remained. Repair (spec-only, `resolveTo()`): added `{ exact: true }` to the three
label lookups (`House number`, `Street`, `Borough`), each verified unique in the form. No component,
test, or contract change. Local `generate_ts_types.py --check` and `modularity_check --check` remain
exit 0 (unchanged this round); vitest/Playwright still run only on CI (the next run is the verification).
