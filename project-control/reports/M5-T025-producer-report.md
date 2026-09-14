# M5-T025 producer report — D-056 web-fix packet

Task: M5-T025 (D-056-R001/R002/R003; also binds D-046-R001/R002, D-040-R001).
Producer: frontend-engineer. Contract head: `3d99c92a8b66aaa71dcaef57cf15b6bfc2d4a795`.
Worktree: `wt-m5t025` (isolated; primary checkout untouched — verified via
`git rev-parse --show-toplevel` before any edit, per the setup guard).

## Files changed (all 8 inside `allowed_paths`; nothing else touched)

- `apps/web/src/lib/provenance-link.ts` (placeholder replaced) — new module.
- `apps/web/src/lib/__tests__/provenance-link.test.ts` (placeholder replaced) — new tests.
- `apps/web/src/components/property/ProvenanceDisclosure.tsx` — R001.
- `apps/web/src/components/property/__tests__/sections.test.tsx` — R001 tests.
- `apps/web/src/components/rule-evaluation/RuleEvaluationResult.tsx` — R001.
- `apps/web/src/components/rule-evaluation/__tests__/rule-evaluation.test.tsx` — R001 tests.
- `apps/web/src/components/address/LotOutlineMap.tsx` — R002 + R003.
- `apps/web/src/components/address/__tests__/lot-outline-map.test.tsx` — R002 + R003 tests.

`package.json`/`package-lock.json` untouched; zero new dependencies (`maplibre-gl` was
already admitted in M5-T022). `git status --short` at the end of this round shows exactly
these 8 files.

## R001 — safe provenance source links

New `apps/web/src/lib/provenance-link.ts`: `isValidDatasetId` (strict regex
`^[a-z0-9]{4}-[a-z0-9]{4}$`, anchored both ends — the exact Socrata dataset-id shape, e.g.
the real PLUTO id `"64uk-42ks"`, `services/api/app/connectors/pluto_soda.py DATASET_ID`)
and `datasetLandingUrl` (constant prefix `https://data.cityofnewyork.us/d/` + the validated
id, or `null`). Mirrors the ZoLa link pattern in `AddressConfirmCard.tsx` (G5 F-1: client
validation is the only guard, href built only from a module constant + the re-validated
value). The function's ONLY input is a dataset id — there is no code path by which
`request_url` (or anything else server-echoed) can reach it, so the "never an href from a
reflected string" property is structural, not just tested.

Wired into both surfaces named in the packet:
- `ProvenanceDisclosure.tsx`: the existing "Dataset id" row now renders an `<a>` (target
  `_blank`, `rel="noopener noreferrer"`, text = the id) when `reproducibility.dataset_id`
  validates, else the prior plain-text rendering (byte-identical fallback). "Retrieved
  from" (host of `request_url`) is untouched — still text-only, never a link.
- `RuleEvaluationResult.tsx`: added a guarded `typeof provenance.dataset_id === "string"`
  row (same pattern as the existing guarded `source_id`/`request_url` reads on this
  open-schema citation-provenance object) that renders the same safe-link pattern.
  **Disclosure**: I traced the real backend shape (`services/api/app/rules/snapshots.py
  SectionSnapshot.provenance()`, and the committed fixture
  `packages/contracts/fixtures/valid/rule_evaluation/supported_family_draft.json`) and
  confirmed citation provenance for ZR legal-text citations **never carries a
  `dataset_id`** — it cites `zoningresolution.planning.nyc.gov`, not a Socrata dataset, so
  this row is currently always absent in production (no regression, no link ever rendered
  there today). It's wired anyway because: (a) the packet names this surface explicitly,
  (b) it's the same forward-compatible guarded-open-key idiom this file already uses for
  `source_id`/`derivation`-class fields, and (c) it's fully tested via a mutated clone of
  the real fixture. Flagged for G3/G4: confirm this reading of "the provenance rows in
  RuleEvaluationResult.tsx" matches intent, since the real data path never exercises it.

Tests (10 in `provenance-link.test.ts`, 4 in `sections.test.tsx`, 4 in
`rule-evaluation.test.tsx`): valid id → exact href in both surfaces; invalid/absent id → no
anchor, honest text; a hostile `request_url` (`<script>`/query-string/path-traversal
payloads) never appears in any rendered href in either surface, even when a valid link is
present alongside it; the pure module additionally proves anchored-regex rejection of
substrings, full URLs, and case variants.

## R002 — lot-outline visibility: root cause + fix

**Root cause (evidence-based, code-read; the live browser bug itself is not reproducible in
this environment — see Limitations).** In the pre-fix `LotOutlineMap.tsx`, the entire draw
step (`addSource`/`addLayer`×2/`fitBounds`) was gated behind exactly one
`map.on("load", callback)` registration, with no readiness check and no `error` handler.
MapLibre's `"load"` is a **one-time** event fired once, after the initial style finishes
loading and the map completes its first render; a listener attached **after** that single
firing is never invoked — a long-documented class of bug in MapLibre/Mapbox GL JS, which is
why MapLibre's own guidance recommends `"style.load"` plus an explicit readiness check
(`isStyleLoaded()`) over a bare `"load"` listener for exactly this "add sources/layers after
construction" use case. Two facts in the code make this class of bug match the reported
symptom exactly rather than just plausibly:
1. `EMPTY_STYLE`'s `background` layer requires no source and paints as soon as the style is
   applied — **independent of whether `"load"` ever fires**. So a missed `"load"` still
   produces a rendered (gray, `#eef1f4`) canvas.
2. `AttributionControl` is a DOM overlay added synchronously at construction time,
   unrelated to `"load"` — so attribution renders regardless.
3. Nothing else in the file could add the outline layers. If `"load"` is missed, the result
   is precisely: gray canvas + attribution + no outline, permanently (scrolling/zooming
   cannot help — there is nothing to zoom into).

I could not attach a live debugger to the owner's browser in this thin-client environment
(no `node_modules`, no browser, no WebGL here — confirmed below), so I cannot certify the
exact internal trigger of the missed event on the owner's device. What I *can* and did
verify by reading the code: the component had **zero defense** against this well-known race
(no readiness check, no idempotent draw, no error visibility), which is itself a genuine
defect independent of the precise trigger, and the observed symptom is the *exact* signature
this defect produces (not a guess-fit).

**Fix (`runOnStyleReady`, exported, `LotOutlineMap.tsx`):** checks `map.isStyleLoaded()`
synchronously right after construction; if already true, the draw callback runs
**immediately, with no event wait at all** — categorically closing the missed-event race
regardless of its trigger. Otherwise it arms **both** `"load"` and `"style.load"` with an
idempotency guard so draw runs exactly once even if both fire. This is the fix; it is not
theater — the previous mock's `on("load", cb)` always fired via `queueMicrotask` regardless
of timing, so it could never have caught this bug, which is exactly why the new
`lot-outline-map.test.tsx` mock now mirrors real "one-time listener, no-op if the event
already fired" semantics, and a genuinely red-on-old/green-on-new unit-test suite exists
against `runOnStyleReady` directly (see Tests below).

**Hardening (also required, D-056-R002 text): `map.on("error", ...)`** was entirely absent
before — any style/source/layer error was invisible (MapLibre only `console.error`s an
unhandled `error` event; it never crashes and never surfaces to the UI). Now routed to a new
`mapRenderFailed` state that renders a new typed fallback (`lot-outline-render-error`,
byte-new branch; the existing `lot-outline-webgl-unavailable` branch is untouched and still
reached only when WebGL itself is unavailable).

**Framing fix:** `fitBounds` `maxZoom` raised from `18` to `19.5` (`LOT_OUTLINE_MAX_ZOOM`,
exported). At NYC's latitude (~40.71°N, cos ≈ 0.758) the Web Mercator ground resolution at
zoom 18 is `156543.034 * 0.758 / 2^18 ≈ 0.45 m/px`; a canonical 25×100 ft NYC rowhouse lot
(7.62m × 30.48m) therefore rendered at roughly **17×67 px** inside the 320px panel — a real,
independently provable "fingernail size" defect even when the outline IS drawn. At 19.5 the
resolution is ≈0.16 m/px, rendering the same lot at roughly **48×190 px** — clearly visible.
No raster basemap tiles are wired (M5-T023 — flat background only), so there is no
tile-pixelation ceiling arguing for a lower cap.

**Display-only discipline preserved:** `geometryBounds` (camera-only bbox) is unchanged;
`geometry` is still passed to `addSource` verbatim; no new coordinate math, no measurement.

## R003 — zoom controls

`maplibre-gl` `NavigationControl` (already-admitted package, zero new dependency) added at
`"top-right"` with `showCompass: false` — this is a flat, top-down, display-only outline with
no other rotation-relevant affordance, so a bearing indicator would add clutter without
conveying anything. Keyboard accessibility comes from MapLibre's own native `<button>`
implementation (no custom code needed). Every existing fallback/dynamic-import/SSR path is
unchanged; `NavigationControl` is only constructed on the same drawable path the fill/line
layers already require.

## Tests added (net +14 across the pack; all existing tests' assertions preserved verbatim
except the two the packet explicitly required to change: `outcomeSummary`'s signature gained
a third parameter, and the "single_lot"/"!drawable" render branch gained a sibling)

- `provenance-link.test.ts`: 10 tests (valid/invalid/anchored-substring-rejection/full-URL-
  rejection/absent/negative-hostile-values/exact-output-shape).
- `sections.test.tsx`: +4 (`ProvenanceDisclosure` valid/invalid/absent/negative).
- `rule-evaluation.test.tsx`: +4 (citation-provenance valid/invalid/absent/negative).
- `lot-outline-map.test.tsx`: +6 — 3 pure `runOnStyleReady` unit tests (already-loaded →
  synchronous immediate draw, not-yet-loaded → both events armed + idempotent, `style.load`-
  only firing), 1 `lotOutlineFitBoundsOptions` unit test, 1 component-level "style already
  loaded before wiring attaches" regression (the mock now mirrors real one-time-event
  semantics so this scenario is meaningful), 1 `map.on("error", ...)` → typed-fallback test.
  The existing S1 test also gained assertions for the raised `maxZoom` and the new
  `NavigationControl` wiring.

## Self-checks run (exact commands + results)

```
$ python tools/modularity_check.py --check
selected 404 files; failures 0; warnings 17   (exit 0; none of the 17 warnings name a file
                                                I touched — all pre-existing elsewhere)
```

```
$ npm --prefix apps/web run test        -> 'vitest' is not recognized...
$ npm --prefix apps/web run typecheck   -> 'tsc' is not recognized...
$ npm --prefix apps/web run lint        -> 'eslint' is not recognized...
```

**Environment correction (flagged, not a code defect):** the dispatch packet stated
"`node_modules` already exists — use its binaries". I verified this is **not true** in this
worktree or anywhere else reachable on this machine (`find … -iname node_modules` under the
repo root and under the sibling worktree `wt-m0t071` — the latter has a 355-package
`node_modules` from an older task, but no `maplibre-gl`, confirming it predates M5-T022 and
cannot substitute). This matches the immediately-prior M5-T023 producer's own disclosed
limitation verbatim ("Cannot run locally (thin client, no node_modules)... CI is the
executable authority for all JS/TS"), so I followed that same established, accepted posture
rather than treat it as a blocker: I did NOT run `npm install` (forbidden either way), wrote
code and tests to the CI standard, and self-checked everything possible without npm
(balanced-braces/parens sanity pass via plain `node -e`, full manual re-read of every edited
file, and the one available real self-check, `modularity_check`). **Residual risk:** a
TypeScript/ESLint nuance (e.g. the `vi.fn()`-to-typed-interface assignments in the new
`runOnStyleReady` unit tests, or the `Partial<Reproducibility>`/`Partial<SourceFact>` test
helpers in `sections.test.tsx`) could only be caught by CI's `tsc`/`eslint`, not by me
locally. CI (`web` + `web-e2e`) is the executable authority per the packet's own
`documented_test_commands`.

## Design decisions

- **Guarded-open-key pattern for `RuleEvaluationResult`'s citation `dataset_id`** rather
  than inventing a different link target for ZR citations: matches the file's existing
  precedent (`source_id`, `request_url`, `retrieved_at` are all read the same guarded way
  off an intentionally-open `{}` schema type) and keeps the fix scoped to exactly what R001
  asked for (a link built from a *dataset id*), rather than fabricating a second kind of
  "official source link" for legal-text citations that the packet didn't ask for.
- **`mapRenderFailed` is a new, additive state/branch**, not a repurposing of the existing
  `lot-outline-webgl-unavailable` branch — keeps that branch's text and testid byte-
  identical (R002 explicitly requires all six typed fallback branches stay
  behavior-identical) while still satisfying "route to a typed unavailable fallback instead
  of a silent empty map" with copy that's factually accurate for a post-construction render
  failure (as opposed to a no-WebGL copy that would be misleading here).
- **`runOnStyleReady` extracted as a small, independently exported pure function** rather
  than inlined, specifically so jsdom (which lacks WebGL) can express a real red-on-old/
  green-on-new proof against the exact logic that changed, per the packet's own guidance.

## Limitations / flagged questions for G3/G4

1. The live owner-device symptom itself was not reproduced end-to-end here (no browser/
   WebGL/node_modules in this environment) — the root cause is argued from (a) the
   documented MapLibre one-time-event hazard, (b) the concrete absence of any defense
   against it in the pre-fix code, and (c) the exact match between that defect's predicted
   symptom and the reported one. This is the strongest evidence obtainable in this
   environment; a live re-test after the owner's Manual Deploy is the final confirmation
   (D-056-R006, owner-facing, out of this task's scope).
2. Flagged above: `RuleEvaluationResult`'s citation `dataset_id` row is real code, real
   tests, but currently unreachable with live data (ZR citations never carry a dataset_id).
   If the intended reading of "the provenance rows in RuleEvaluationResult.tsx" was actually
   the `input_provenance.zoning_district`/`lot_area_sq_ft` id-list rows instead, that would
   need a different design (those are lists of provenance-id *strings*, not full records —
   no dataset_id is available there either); I believe the citation rows are the intended
   target since they're the ones with "Retrieved from"/host text the packet named, but this
   is worth an explicit G3 confirmation.
3. `services/api/**`, `packages/contracts/**`, and all `forbidden_paths` were read-only
   research (root-cause tracing, fixture shapes) — nothing there was modified.

## Owner-facing note (D-056-R006, for the record at acceptance)

Auto-deploy is OFF on the hand-created web service (D-043 checklist). Once this packet is
accepted and pushed to `candidate/D-024-mrl-option-b`, the owner needs to click **Manual
Deploy** on that branch, then refresh the page, for the fix to reach the live site.
