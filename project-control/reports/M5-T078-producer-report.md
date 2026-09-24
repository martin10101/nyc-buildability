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

## Rework (G3 F1-F3 + G4 F1-F3 + HJ-1 cluster)

Producer: frontend-engineer (orchestrator-dispatched rework subagent). Worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t078`, branch `task/M5-T078-drawing-surface-a11y`; verified before
edits: `git rev-parse --show-toplevel` = the wt-m5t078 path, HEAD = `a57bb8dec34129a86e5c9bfe6ea2d2be1f5dfc1d`,
tree clean. Inputs read: M5-T078-G3.md, M5-T078-G4.md, M5-T078-HJ.md, this report, the task packet (scope
correction: `apps/web/src/app/property/architect.css` added to allowed_paths).

Evidence legend unchanged: [OBSERVED] ran locally; [PREDICTED] reasoned against source, CI on the pushed head
proves it (thin client - no npm/npx/node/vitest/playwright run); every web claim below is [PREDICTED].

### Files changed (exactly the allowed_paths)
- `apps/web/src/components/architect/ProposalOutlineDraw.tsx`
- `apps/web/src/components/architect/ProposalOutlineMap.tsx`
- `apps/web/src/components/architect/__tests__/proposal-outline-draw.test.tsx`
- `apps/web/src/components/architect/__tests__/proposal-outline-map.test.tsx`
- `apps/web/src/components/address/__tests__/lot-outline-map.test.tsx`
- `apps/web/src/app/property/architect.css`
- `project-control/reports/M5-T078-producer-report.md` (this appended section only; history above untouched)

No forbidden file touched (ProposalEditor.tsx, proposal-editor.test.tsx, ArchitectEntry.tsx, LotOutlineMap.tsx,
lib/outline-bridge-api.ts, lib/architect/, e2e/). No dependency, package.json or lockfile change. Public props of
ProposalOutlineDraw unchanged (`{ bbl, onAdopt, fetchImpl }`).

### BLOCKING closures

**G3-F1 = HJ-1 (blocked press rewrote the refusal card).**
Fix: the refusal card body is built from the outcome itself - `ProposalOutlineDraw.tsx:464`
`<p>{announcementForOutlineBridge(outcome)}</p>` (was `<p>{announcement}</p>`). A blocked press writes only the
announcer (`:263-274`). Rendered card text for every outcome-driven render is byte-identical to before (the old
`announcement` equalled `announcementForOutlineBridge(result)` right after convert); during a pending retry the card
now keeps the previous refusal text instead of a blank paragraph.
Specs: `proposal-outline-draw.test.tsx:531` (it.each: 422 out_of_neighborhood + 404 feature_unavailable - the
production-reachable HJ-1 path) - refusal, delete point 2, press Convert: announcer holds "Add 1 more point to
convert" (waitFor), `fetchSpy` still 1 call (`:571`), card `textContent` byte-equal to before (`:574`) and not
containing "Add 1 more point" (`:575`), onAdopt never called. `:610` - 404 refusal, retry (pending, 2 fetches),
press again: announcer "Conversion is already in progress.", still 2 fetches (`:630`), card text unchanged (`:633`).
Mutation trace [PREDICTED]: the LITERAL pre-fix (card renders `announcement`; blocked press sets it
synchronously) makes the card read "Outline not convertedAdd 1 more point to convert — ..." after the blocked press
-> `:574` toBe(cardText) and `:575` red in both it.each rows; in `:610` the pre-fix card is blank once the retry
starts and then reads "...Conversion is already in progress." -> `:633` red.

**G3-F2 = G4-F2 = HJ-3 = HJ-7 (status/instruction clauses ungated).**
Fix: every clause is composed from the same `mapSurface x hasSelection x selectedIsFinite` state -
`ProposalOutlineMap.tsx:198-246`:
- untyped selection status: `:227` present -> "... so a map click will place it."; `:228` any other surface ->
  keyboard wording "...; type its {label} in the table." (G3-F2(i));
- readiness sentence only when `readyApplicable = mapSurface === "present" && !hasSelection` (`:236`), so never
  while a click would MOVE the selected point (G3-F2(ii)); spoken once per transition (A7 below);
- untyped-selection instruction (`:214`) no longer offers "Click the point again to deselect" - it says "Use its
  Deselect button in the table to clear the selection." (G3-F2(iii) / HJ-7);
- exact gap noun for a half-typed row: `:200-201` via the shared `missingOrdinateLabel` (`:75`, moved from Draw so
  one definition serves the row marker, the hint and the selection copy): "has no latitude yet" / "type its
  latitude", "coordinates" only when both ordinates are missing.
Specs (`proposal-outline-map.test.tsx`):
- `:431` it.each over all 5 FALLBACK_STATES + loading: nothing selected -> status exactly "1 point drawn." (`:441`),
  no readiness; untyped row selected -> status exactly "1 point drawn. Point 1 selected — it has no coordinates yet;
  type its longitude and latitude in the table." (`:449-451`), and neither status nor instructions match `/click/i`
  (`:452-453`).
- `:457` present + FINITE selection: status exactly "2 points drawn. Point 1 selected." (`:465`); after deselect the
  readiness sentence speaks.
- `:500` present + untyped selection: no "Click the point again" (`:505`), table-deselect wording present, exact
  status.
- `:512` present + half-typed selection: exact instruction "Point 0 is selected but has no latitude yet — ... type
  its latitude ..." (`:519`), no "no coordinates yet" (`:521`), exact status (`:523`).
Mutation traces [PREDICTED]: literal pre-fix ungated clause -> `:449-452` red in all 6 variants; literal pre-fix
always-appended readiness -> `:465` red; literal pre-fix "Click the point again to deselect." -> `:505` red; literal
pre-fix "has no coordinates yet ... longitude and latitude" for a half-typed row -> `:519/:521/:523` red; G4 S3
(readiness gated on `mapSurface !== "unknown"`) -> `:441` red in the 5 fallback variants.

**G3-F3 = G4-F3 (duplicate split-line pair predicate).**
Fix: `ProposalOutlineDraw.tsx:326` `const rowComplete = isDrawnPointFinite(p);`. The per-ordinate booleans
(`:328-329`) now feed ONLY `aria-invalid` (`:345`, `:354`); the marker label comes from the shared
`missingOrdinateLabel(p)` (`:327`), which uses a filter/join (no `&&`). The old local `missingOrdinateLabel`
(with its `!lngFinite && !latFinite`) is deleted.
Grep evidence [OBSERVED] (cwd wt-m5t078; ripgrep multiline, `\s` spans newlines, so split-line forms match):
pattern `(Number\.isFinite\([^)]*\)|\b(lng|lat)Finite\b)\s*(&&|\|\|)\s*!?\s*(Number\.isFinite\(|\b(lng|lat)Finite\b)`
- over `apps/web/src/components/architect` at the rework tree -> exactly ONE hit:
  `ProposalOutlineMap.tsx:60:  return Number.isFinite(p.lng) && Number.isFinite(p.lat);` (the predicate itself);
- over the PRE-FIX blob (`git show HEAD:apps/web/src/components/architect/ProposalOutlineDraw.tsx`, saved to the
  session scratchpad) -> TWO hits: `60: if (!lngFinite && !latFinite) ...` and
  `288: const rowComplete = lngFinite && latFinite;` - i.e. this grep catches the split-line form the original
  single-line grep missed.
- every `Number.isFinite` in `Proposal*.tsx` [OBSERVED]: Draw `:51` (numInputValue, single value), Draw `:328/:329`
  (per-ordinate, aria-invalid only), Map `:60` (the predicate), Map `:76` (missingOrdinateLabel, per-ordinate
  label), ProposalEditor `:54` (numInputValue, forbidden file, untouched).
Mutation note (disclosed): the literal pre-fix `lngFinite && latFinite` is semantically identical to the predicate
TODAY, so no runtime spec can tell them apart; the guard for F3 is the grep above, which flags the literal
pre-fix. A runtime tooth would need a module-level mock that tightens the predicate - not added (see Not closed).

**G4-F1 (F7 untested at its original site).**
Spec: `proposal-outline-draw.test.tsx:443` - 2 finite + 1 longitude-only row (too-few arm): hint contains "1 row
still needs a latitude" (`:452`), does NOT contain "longitude and latitude", and equals exactly "Convert needs at
least 3 points with both coordinates filled in. 1 row still needs a latitude — fill it in or delete it (2 of 3
ready)." (`:455`). Mutation trace [PREDICTED]: G4 S1 / the literal pre-T078 blanket "needs a longitude and
latitude" -> `:452` red.

### Advisories folded in
- **G3-A1 / HJ-2** - `architect.css:45` `.architect-shell button:disabled,.architect-shell button[aria-disabled="true"]
  { cursor:not-allowed;opacity:.6; }` (one selector added to the existing rule). The only other `aria-disabled`
  in apps/web/src is on a `<Link>` (ArchitectShell.tsx:34), which a `button[...]` selector does not match.
- **G3-A2 / HJ-4** - `convertHintCopy` (`ProposalOutlineDraw.tsx:75-98`): "1 row is missing its latitude and will be
  left out — fill it in to include it, or delete it."; several rows name a shared ordinate ("are missing their
  latitude") or stay generic ("are missing coordinates") - no more "without their coordinates" for half-typed rows.
- **G3-A3 / HJ-6** - a blocked press clears the announcer, then sets the reason after `REANNOUNCE_DELAY_MS` (`:58`,
  100 ms) (`:263-274`); the pending set is cancelled by a newer press, by a conversion start/result (`:240`, `:244`)
  and on unmount (`:144`). Spec `:480` records the region's text with a MutationObserver during the SECOND press:
  `seen` contains the reason (`:496`) after "" (`:498`). Pre-fix (same string set again) -> no DOM change -> `:496`
  red. The earlier AS-4 spec (`:459`) now waits for the announcement (`waitFor`).
- **G3-A4 / HJ-5** - Convert gets `aria-describedby={hintVisible ? hintId : undefined}` (`:401`, id `:414`,
  `useId` `:133`); a bridged conversion that left rows out appends "M row(s) without both coordinates was/were not
  included." to the announcement (`:249-252`), composed in the component (outline-bridge-api.ts untouched). Spec
  AS-1 (`:362`): `toHaveAccessibleDescription(<exact hint>)` (`:382`) and the announcer clause (`:396`).
  Not done: linking each aria-invalid input to its row marker (G3-A4's second sentence) - not in the rework list.
- **G3-A5 / G4-A1** - spec `:501` counts live regions over the WHOLE `proposal-outline-draw` section across the
  loading -> interactive flip: 2 before (`:512`) and 2 after (`:519`), with the flip heard in the same status node.
  The draw mock gained a switchable `drawLotMock.variant` (default "plain" = the original output, so every earlier
  spec is unchanged). The wrapper-level count spec in proposal-outline-map.test.tsx stays.
- **G3-A7 / HJ-3(c)** - readiness lifecycle `ProposalOutlineMap.tsx:81-93` + `:231-246` (state adjusted during
  render: pending on each surface transition -> showing at the first status where a click would place -> done at the
  next status change). Spec `proposal-outline-map.test.tsx:472`: ready once; "2 points drawn." (`:481`); returning
  to "1 point drawn." does not re-announce (`:484`); a new transition (render-error then interactive) re-arms it
  once. Pre-fix -> `:481` red.
- **G4-A3** - spec `proposal-outline-draw.test.tsx:580`: deferred fetch; click -> 1 fetch, "Converting…" and
  aria-disabled="true"; second click -> still 1 fetch (`:596`) + "Conversion is already in progress." announced;
  release -> bridged, onAdopt once. G4 S4 (drop `&& !converting`) -> second fetch -> `:596` red.
- **G4-A5** - `lot-outline-map.test.tsx:550` `expect(new Set(ids)).toEqual(new Set(["lot-outline-fill",
  "lot-outline-line"]))` replaces the two presence checks (the drawn-layer negatives stay); no exact addLayer tally
  anywhere (DB-049(h) intact).
- **G3-A6 / G4-A7** - the copy table below lists "Conversion is already in progress." word for word.

### Copy table delta (before -> after; meaning protected)

| # | Location | Before | After | Meaning protected |
|---|---|---|---|---|
| R1 | Draw hint, too-few + incomplete, several rows (`convertHintCopy` `:86-90`) | "N rows still need their coordinates — fill them in or delete them (k of 3 ready)." | "N rows still need a {shared label}" when every incomplete row lacks the same ordinate(s), else "N rows still need coordinates" | F7 exactness; never "their coordinates" for half-typed rows (G3-A2). One-row wording unchanged ("1 row still needs a latitude"). |
| R2 | Draw omission hint, enough + incomplete (`:93-97`) | "Convert will include N points. M row(s) without {a <o> \| their coordinates} is/are not filled in and will not be included — fill it/them in or delete it/them to include it/them." | "Convert will include N points. M row(s) is/are missing {its\|their} {label} \| coordinates and will be left out — fill it/them in to include it/them, or delete it/them." | (a) omission never silent, same count and meaning; removes "delete it to include it" (G3-A2 / HJ-4). |
| R3 | Draw refusal card body (`:464`) | shared announcer state (rewritten by blocked presses; blank during a retry) | `announcementForOutlineBridge(outcome)` - identical text for every outcome; keeps the previous refusal during a retry | the server's refusal reason is never replaced by a client hint (G3-F1 / HJ-1). |
| R4 | Draw post-convert announcement, bridged with omitted > 0 (`:249-252`) | bridge announcement only | bridge announcement + " M row(s) without both coordinates was/were not included." | (a) omission spoken, not only shown (G3-A4 / HJ-5). Zero omitted -> byte-identical. |
| R5 | Draw blocked-press announcement (`:228`, `:263-274`) | the convert hint, or "Conversion is already in progress." set once | the SAME strings - "Conversion is already in progress." verbatim - delivered clear-then-set so a repeat is re-announced | (e) the reason is heard every press, only via the announcer (G3-A3 / HJ-6). |
| R6 | Convert accessible description (`:401`) | none | the visible hint text | how many rows will be left out, at the control (G3-A4 / HJ-5). |
| R7 | Map instruction, untyped selection on a present map (`:214`) | "Point X is selected but has no coordinates yet — click the map to place it, or type its longitude and latitude in the table below. Click the point again to deselect." | "Point X is selected but has no {coordinates\|longitude\|latitude} yet — click the map to place it, or type its {longitude and latitude\|longitude\|latitude} in the table below. Use its Deselect button in the table to clear the selection." | (d) PLACE not move; exact gap; no instruction to click a point that is not drawn (G3-F2(iii) / HJ-7). |
| R8 | Map status, untyped selection (`:226-228`) | " Point X selected — it has no coordinates yet, so a map click will place it." on EVERY surface | present: " Point X selected — it has no {noun} yet, so a map click will place it."; loading/fallback: " Point X selected — it has no {noun} yet; type its {label} in the table." | no map gesture promised where no map exists (G3-F2(i) / DB-047(d)). |
| R9 | Map status readiness suffix (`:93`, `:268`) | " The lot map is ready to draw on — click it to place points." appended to every status while present | same sentence, once per transition to present, at the first status where nothing is selected; dropped at the next status change | readiness is announced (c) but never claims a click places while it would move (G3-F2(ii)) and is not repeated (G3-A7 / HJ-3(c)). The visible instructions still carry the gesture invitation. |
| R10 | Row marker (`:333-338`) | "Needs {label}" when both per-ordinate checks were not both true | same text; shown whenever the shared predicate rejects the row | (b) every omitted row is marked (G3-F3). |
| R11 | Convert visual state (architect.css:45) | full ink + pointer at aria-disabled="true" | opacity .6 + not-allowed cursor, same as `:disabled` | the not-ready meaning is visible again (G3-A1 / HJ-2). |

Unchanged: the post-convert counts line (now via `omittedRowsClause`, byte-identical), the section honesty
paragraph, the map-context note, the refusal heading, residual/reason details, the too-few "Add N more points"
sentence, the finite-selection and no-selection instructions, and every fallback/loading instruction. No
disclosure, honest-gap, provenance or professional-review meaning was deleted or weakened; no number is computed in
the presentation layer (all counts are UI row tallies or the server report's vertex count).

### Local self-check
[OBSERVED] cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t078`: `python tools/modularity_check.py --check`
-> `selected 486 files; failures 0; warnings 23` -> exit 0. The only apps/web warning is the pre-existing
`apps/web/src/lib/surveyReview/types.ts` symbol_ceiling; no M5-T078 file is named (ProposalOutlineDraw.tsx 484
lines, ProposalOutlineMap.tsx 272 lines; spec files are outside the check's scope).
[OBSERVED] byte scan of the six edited files: zero control bytes; line endings consistent (CRLF working copy,
`core.autocrlf=true`).
[OBSERVED] consumer sweep (code graph `query.py --no-regen impact` returned "STALE (stale fingerprint)"; grep used):
ProposalOutlineDraw/Map are consumed only by ProposalEditor.tsx (forbidden, unchanged) and the in-scope specs;
proposal-editor.test.tsx / entry.test.tsx assert none of the changed strings (only the finite convert flow);
e2e/proposal-editor.spec.ts touches Convert only via its button text, `toBeFocused`, `toBeEnabled` and `click` on
convertible states; no source-scan spec reads the changed files.
[PREDICTED] web + web-e2e green on the pushed head (CI is the only proof).

### Not closed / limits
- F3 has grep teeth only (see its mutation note); a runtime tooth needs a module-level predicate mock.
- G3-A4 second half (aria-describedby from each aria-invalid input to its row marker) not done - not in the rework
  list.
- G4-A4 (two conversions / server count vs client count), G4-A6 (F8 comment overstates its guard), HJ-8
  (aria-invalid on a brand-new row, required by AS-2) and HJ-9 (result card never marks itself stale) are not
  addressed - not in the rework list.
- The re-announce delay (100 ms) and the readiness-once behavior are proven in jsdom only; real screen-reader
  behavior stays DB-049(i) (next e2e-touching increment).

### Discoveries (route; not fixed here)
- A map click on a selected HALF-typed row replaces its typed longitude/latitude with the clicked position (both
  ordinates); the copy says "click the map to place it" but does not warn that a typed ordinate is overwritten.
  Low; consider "(a click sets both coordinates)" in the next drawing-copy increment.
- With a finite point selected when the map becomes ready, readiness is held until the selection clears (by
  design: the place-points sentence would be false while a click moves the point). A move-worded readiness variant
  could be considered with DB-049(f)/(i).

### Requested status
awaiting_gate (rework resubmission for G3/G4 re-review; HJ confirmation advised). CI on the pushed head is the sole
proof of the [PREDICTED] web behavior.

END-OF-REPORT
