# M5-T078 producer report — DB-049 drawing-surface disclosure + accessibility cluster

Producer: frontend-engineer (orchestrator-dispatched subagent).
Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t078`, branch `task/M5-T078-drawing-surface-a11y`,
contract-seam HEAD `b56f3d5b40171bcb6b760f97eb0eef574995f8ae` (verified before edits).

Evidence-status legend: [OBSERVED] ran locally; [PREDICTED] reasoned against source, CI proves
(thin client — no npm/npx/node/vitest/playwright run here); [BLOCKED] could not run.

Scope: exactly the six allowed_paths. `git status --porcelain` after edits lists only the five
source/test files below plus this report. No forbidden file (ProposalEditor.tsx, proposal-editor.test.tsx,
ArchitectEntry.tsx, MaxEnvelopePanel.tsx, LotOutlineMap.tsx, AddressConfirmCard.tsx, any e2e) touched.

## Files changed
- `apps/web/src/components/architect/ProposalOutlineMap.tsx` — F6 shared predicate; (c) map-ready
  fold; (d) untyped-selection copy + status; F8 reset-key comment.
- `apps/web/src/components/architect/ProposalOutlineDraw.tsx` — F6 consume; (a) omission hint +
  post-convert counts; (b)/(F7) row markers; (e) aria-disabled Convert + announce-on-activate.
- `apps/web/src/components/architect/__tests__/proposal-outline-draw.test.tsx` — aria-disabled
  migration of the existing gate assertions + AS-1/AS-2/F7/AS-4 specs.
- `apps/web/src/components/architect/__tests__/proposal-outline-map.test.tsx` — AS-3 one-region +
  AS-4 untyped-selection specs.
- `apps/web/src/components/address/__tests__/lot-outline-map.test.tsx` — (g) one-map-instance +
  (h) four exact-tally → presence-idiom conversions.

## Local self-check (the only thin-client command)
[OBSERVED] cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t078`:
`python tools/modularity_check.py --check` → `selected 484 files; failures 0; warnings 22` → **exit 0**.
None of the 22 warnings names an M5-T078 file (they are pre-existing api/tools/surveyReview signals).

## Per-AS evidence

### AS-1 (omission never silent) — (a)
Component: hint now renders INDEPENDENT of Convert enablement —
`ProposalOutlineDraw.tsx:369` condition `drawnCount > 0 && (finiteCount < MIN_DRAWN_VERTICES || incompleteCount > 0)`
(was `... && finiteCount < MIN_DRAWN_VERTICES`). The "enough finite + untyped rows remain" branch
(`convertHint` else-arm, `:199-203`) states how many rows Convert will OMIT ("Convert will include N
points. M row(s) … will not be included"). Post-convert status names converted (server report count)
AND omitted (captured at convert time) — counts line `outline-draw-convert-counts` at `:390-394`;
omitted captured at `:216` (`setOmittedOnConvert(points.length - drawn.length)`), state at `:86`.
Spec: `proposal-outline-draw.test.tsx:346` — 4 rows / 3 finite → `aria-disabled="false"`, hint contains
"Convert will include 3 points" + "1 row" + "will not be included"; post-convert `outline-draw-convert-counts`
contains "3 points converted" + "1 row" + "not included"; onAdopt called once with 3 vertices.
[PREDICTED] Mutation: reverting the hint gate to `finiteCount < MIN` alone suppresses the hint at
finiteCount=3 → `getByTestId("outline-draw-min-hint")` throws → red. Dropping the omitted clause from
the counts line → "1 row"/"not included" assertions red.

### AS-2 (row-level markers) — (b) + F7
Component: each incomplete input carries `aria-invalid="true"` only on the MISSING ordinate
(`ProposalOutlineDraw.tsx:305` lng, `:314` lat; `undefined` when finite → attribute omitted), plus a
visible text marker `outline-draw-row-incomplete-{i}` naming the exact ordinate(s) via
`missingOrdinateLabel` (`:59`, rendered `:295-298`). Complete rows carry neither.
Spec: `proposal-outline-draw.test.tsx:375` — row 0 complete (no marker, no aria-invalid), row 1 missing
ONLY latitude ("Needs latitude", not "longitude and latitude"; only the latitude input aria-invalid),
row 2 missing both ("Needs longitude and latitude", both inputs aria-invalid).
[PREDICTED] Mutation: dropping `aria-invalid` on the latitude input reds the row-1 assertion; a blanket
"longitude and latitude" marker reds the F7 negative.

### AS-3 (one status region) — (c)
Component: the map-ready flip is folded into the wrapper's EXISTING `proposal-outline-map-status`
region (`ProposalOutlineMap.tsx:201-206`); no `aria-live`/`role=status`/`role=alert` added anywhere.
Spec: `proposal-outline-map.test.tsx:362` counts live regions in the wrapper container
(`liveRegionCount`, `:358`) = 1 while loading (mapSurface unknown, no readiness claim), then flips the
leaf to interactive and waits for "The lot map is ready" in the SAME node — count still 1, and
`getByTestId(...) === status` proves the same element.
[PREDICTED] Mutation: adding a new live region for the announcement makes the count 2 → red; not
folding the readiness into the status region reds the text wait.

### AS-4 (selection + keyboard) — (d) + (e)
Selection (d): `ProposalOutlineMap.tsx` derives `selectedIsFinite` (`:121-122`, shared predicate).
Untyped-selected instruction says PLACE not move (`:177-181`); status names the selection even at zero
finite points (`:204`). Spec: `proposal-outline-map.test.tsx:391` — untyped selected row 0 →
instruction "click the map to place it" and NOT "click the map to move it"; status "No points drawn
yet." + "Point 0 selected". `:405` guards the finite branch still says "move it".
Keyboard (e): Convert uses `aria-disabled={!canConvert}` (`ProposalOutlineDraw.tsx:360`, `disabled`
removed) so it stays in the tab order; `onConvertActivate` (`:231-237`) announces `convertBlockedReason`
through the existing announcer and returns WITHOUT a bridge call when not convertible.
Spec: `proposal-outline-draw.test.tsx:414` — 2 finite → `aria-disabled="true"`, `not.toBeDisabled()`,
click makes NO fetch call (spy `toHaveBeenCalled` false) and the announcer shows "Add 1 more point to
convert". Existing gate assertions migrated to aria-disabled at `:133/:139/:147/:149/:273/:335`.
[PREDICTED] Mutation: restoring `disabled` reds `not.toBeDisabled()` and (disabled button eats the
click) the announcer assertion; routing the blocked click into `convert()` reds the zero-call spy.

### AS-5 (single predicate + riders)
F6: `isDrawnPointFinite` exported once (`ProposalOutlineMap.tsx:59`) and consumed at all four sites —
`finitePointCount` (`:66`), `drawnOverlayData` (`:80`), `ProposalOutlineDraw` finiteCount (`:169`) and
convert filter (`:212`). [OBSERVED] `grep -rn "Number.isFinite(p.lng) && Number.isFinite(p.lat)"
apps/web/src` → exactly ONE hit (inside the predicate). F8: reset-key comment on the observer effect's
`[bbl]` dependency (`ProposalOutlineMap.tsx:154-161`). (g): AS-1 sync spec asserts one map instance
(`lot-outline-map.test.tsx:739`). (h): [OBSERVED] `grep -n "addLayer).toHaveBeenCalledTimes"
lot-outline-map.test.tsx` → zero; the four former tallies (:248/:530/:741/:785) now use the file's
presence idiom (`addedLayerIds`, `:219`; byte-equivalence negative at `:549-550`) while the guarded
duplicate-source and stale-payload defects still redden (unchanged AS-1 sync teeth at `:699-739`).

### AS-6 (compatibility + scope)
ProposalOutlineDraw public props unchanged (`{ bbl, onAdopt, fetchImpl }`). [OBSERVED] the forbidden
consumers do not reference any changed surface: `grep` over `proposal-editor.test.tsx` and
`entry.test.tsx` for min-hint/map-status/map-instructions/convert-counts/row-incomplete/aria-invalid/
aria-disabled/toBeDisabled/toBeEnabled → zero hits; both only exercise the finite convert flow
(`proposal-editor.test.tsx:145-174`), byte-identical here. e2e `proposal-editor.spec.ts` references the
Convert button only at `:334` (toBeFocused, after 3 finite points → focusable, was already convertible),
`:415` (toBeEnabled, after 3 finite map-clicks → `aria-disabled="false"` → enabled), `:418` (click →
convertible) — all remain green; no e2e asserts the button disabled. [OBSERVED] `git status --porcelain`
= exactly the six allowed_paths; no package.json/lockfile change; modularity exit 0.

## Copy table (before → after; the meaning each string protects)

| # | Location | Before | After | Meaning protected |
|---|---|---|---|---|
| 1 | Draw min-hint, too-few+incomplete (`ProposalOutlineDraw.tsx:190-197`) | "…N rows still need a longitude and latitude — fill…" | "…N rows still need {a <ordinate> \| their coordinates} — fill…" | (F7) never a false "longitude and latitude" for a half-typed row |
| 2 | Draw min-hint, too-few all-typed (`:197`) | "Add N more points to convert…" | unchanged | HJ-4 disable reason |
| 3 | Draw omission hint, enough+incomplete (NEW `:199-203`) | (nothing — silent drop) | "Convert will include N points. M row(s) … will not be included — fill/delete…" | (a) omission never silent, at the point of action |
| 4 | Draw row marker (NEW `:295-298`) | (none) | "Needs {longitude \| latitude \| longitude and latitude}" | (b)/(F7) row-level, exact ordinate, never color alone |
| 5 | Draw post-convert counts (NEW `:390-394`) | (only disclosure/provenance) | "N points converted to numeric coordinates[; M rows without both coordinates were not included]." | (a) converted AND omitted counts named |
| 6 | Draw blocked-activation announce (NEW, via announcer `:233`) | (none) | the convert reason string | (e) activation announces the reason |
| 7 | Map instruction, untyped selection (NEW branch `:181`) | (untyped selected showed "…click the map to move it…") | "Point X is selected but has no coordinates yet — click the map to place it…" | (d) PLACE not MOVE a point not on the map |
| 8 | Map status region (`:201-206`) | "N points drawn.[ Point X selected.]" (selection only in non-zero branch) | "{No points drawn yet.\|N points drawn.}[ Point X selected[ — it has no coordinates yet, so a map click will place it].][ The lot map is ready to draw on — click it to place points.]" | (c) map-ready announced via the one existing region; (d) selection named even at zero |

No existing disclosure, honesty/provenance note, or professional-review meaning was deleted or
weakened; visual states never remap backend statuses; no legal/zoning number is computed in the
presentation layer (converted count is the server report's vertex count, omitted count is a UI row
tally captured at convert time).

## DISCOVERIES (route to the orchestrator; not fixed in-packet)
- DB-049(f) leaf-readiness signal (the interactive `aria-label` paints before the canvas is clickable)
  stays routed — it needs the forbidden `LotOutlineMap.tsx`. Untouched here.
- DB-049(i) real-browser proof of the copy flip / MutationObserver cost stays routed to the next
  e2e-touching increment (no e2e edited here); AS-3 proves the fold against jsdom + a mocked leaf only.
- F8 mitigation is a comment, not a hard block: a `react-hooks/exhaustive-deps` autofix could still
  strip `[bbl]`. If the repo ever runs exhaustive-deps as an ERROR with autofix, consider an explicit
  `// eslint-disable-next-line react-hooks/exhaustive-deps` there. Currently the codebase ships this
  `[bbl]` dep green, so the comment matches the packet's ask and the existing lint posture.

## Requested status
awaiting_gate (G0/G2/G3/G4). CI on the pushed head is the sole proof of the [PREDICTED] web behavior.

END-OF-REPORT
