# G3 Delta Re-Review Attestation — M5-T023 at final candidate `3ff94619`

> Preservation note: saved VERBATIM by the orchestrator from the same G3 reviewer's agent-return
> channel (transport entity-decoding only). Companion to M5-T023-G3-journey-review.md.

**Same-reviewer attestation** (human-journey-reviewer). Reviewed the actual delta `git diff b99ca6c0..3ff94619` on the three M5-T023 source files plus the CI evidence artifact. Read-only throughout.

## VERDICT: G3 PASS STANDS at `3ff94619` — ADVISORY-1 now SATISFIED (resolved); ADVISORY-2/3/4 remain advisory (posture unchanged)

### (a) ADVISORY-1 — SATISFIED

`outcomeSummary` now takes the `drawable` flag (`LotOutlineMap.tsx:136`, called at `:306` with the component's computed `drawable`). The single_lot branch resolves three ways:
- `geometryUnusable` → "The lot outline could not be drawn: the official geometry was not usable. Use the ZoLa map link **above**…"
- `!drawable` (geometry present, no interactive map / no WebGL) → **"An approximate outline is available for this lot, but this browser could not open an interactive map. Use the ZoLa map link above for the authoritative outline."**
- else (drawn) → "An approximate lot outline is shown, drawn from the official NYC City Planning MapPLUTO parcel geometry (plus or minus 20 feet)."

The new `!drawable` copy is **truthful** (no false "is shown"), **specific** ("could not open an interactive map"), and **points to ZoLa** ("Use the ZoLa map link above"). It now matches the visible `lot-outline-webgl-unavailable` fallback exactly. The `drawable` param only influences the single_lot case; no_outline/multiple_features/invalid_geometry branch on `outcome.view.outcome` first, so there is no cross-contamination.

**Test is load-bearing.** The WebGL-unavailable test (`lot-outline-map.test.tsx:298-303`) asserts the summary `toContain("could not open an interactive map")` AND `.not.toContain("An approximate lot outline is shown")` — it fails if this fix regresses.

### (b) Journey / copy / a11y qualities NOT weakened by the delta

- **e2e locator fix** (`lot-outline.spec.ts:23-32`): form-scoping + `{ exact: true }`. This corrects a real strict-mode failure (default `getByLabel("Borough")` substring-matched the "ZIP code (alternative to borough)" input). Same streets, same per-outcome assertions, same journey content — a test-correctness fix, not a weakening. It is why the earlier rounds (runs 34735243173 / 34735830129) failed and this candidate passes.
- **DCP_ATTRIBUTION constant** (`LotOutlineMap.tsx:118, :256`, G5 fold-in): `customAttribution` is rendered by MapLibre as HTML, so passing the reflected `view.attribution` there was an injection surface (`boundedText` does not neutralize HTML metacharacters). The control now receives a client constant; the reflected attribution still renders as React-escaped text via `AttributionAndAccuracy` (visible attribution text unchanged, and the DCP attribution stays on the map — "provenance on every shape" preserved). This is a **journey-neutral, positive** security hardening. Its new test (`lot-outline-map.test.tsx:164-186`) proves a hostile reflected attribution never reaches the control and shows inert. The effect dep-array narrowing `[geometry, attribution] → [geometry]` is correct (the constant needs no dependency).
- All six G3 qualities I passed at b99ca6c0 (honest states, ZoLa in every state, recovery/no-dead-end/no-spinner-forever, labeled landmark + SR summary, consistency/progressive-disclosure/no-color-only-meaning, e2e fidelity with the acceptable synthetic resolver seam) are intact — the delta touched none of them adversely.

### (c) ADVISORY-2/3/4 — posture unchanged, remain advisory

- **ADVISORY-2** (real WebGL map render unproven in-browser): the delta did not add software WebGL. CI evidence confirms the single_lot e2e passed but the captured summary lines cannot distinguish the map vs WebGL-fallback branch. Correctly folded into the advisory backlog. Still advisory.
- **ADVISORY-3** (weaker default copy when `accuracy_note` absent): untouched. Still advisory.
- **ADVISORY-4** (`interactive: true` on a display-only map, `LotOutlineMap.tsx:239` unchanged): untouched. Still advisory.

### CI evidence verified (stored artifact `project-control/reports/M5-T023-ci-evidence.md`)

Run **34736197598** on **`3ff94619`**, all 18 jobs `success`. My five named evidence items are covered: `web` green (typecheck + lint + `next build` with the first maplibre-gl import); `web-e2e` green — vitest **481/481**, Playwright **83 passed** including all 4 `lot-outline.spec.ts` journeys; regression suites (`address-confirm`, `address-resolution`) within the passing set; `contracts-typegen` green (generated TS byte-identical incl. `lot_geometry`); `modularity` green. The one caveat (map-vs-fallback branch not distinguishable from the summary lines) is the acknowledged ADVISORY-2 item, not a new defect.

**Attestation for orchestrator: G3 PASS STANDS at `3ff94619`. ADVISORY-1 is RESOLVED. ADVISORY-2, ADVISORY-3, and ADVISORY-4 remain open advisories (non-blocking) on the backlog. No new residuals introduced by the delta.**
