# M5-T071 producer report — bounded evidence (rework resubmit 2)

**Task:** M5-T071 · **Branch:** task/M5-T071-drawing-hardening · **Producer:** frontend-engineer
**Directives:** D-082-R001, D-076-R002, D-066-R001, D-077-R002/R003
**Scope wall:** drawing-surface only; every finite-value flow byte-identical (ProposalEditor / the
LIVE T070 lane untouched; `LotOutlineMap.tsx` preserved).

## 0. Why this resubmit exists

The previous report embedded every file's full `git diff` and relied on Markdown headings to keep
each section "independently collectible." That is wrong: the whole file is one blob, so a single
over-cap file gets truncated as a unit and the draw-test / remaining map-test / leaf-condition
sections were cut. This report is **concise and reference-only** — it names each change by file and
line anchor and does **not** duplicate patches already visible via `git diff`. The forbidden leaf
is quoted only by short anchor, not embedded. This unit also **adds** the two coverage gaps the
review named: per-fallback-state keyboard-only copy, and an observer transition test.

Reproduce any change with `git diff HEAD -- <path>` in this worktree; read the forbidden leaf with
`git show HEAD:apps/web/src/components/address/LotOutlineMap.tsx`. The binding material identity is
the orchestrator's commit of these working-tree files; line anchors below are against the working
tree.

## 1. Change set (5 source/test files + this report)

| File | Scope | What changed |
|---|---|---|
| `architect/ProposalOutlineMap.tsx` | src | DB-047(d) copy gating + DB-047(e) finite count (prior unit; unchanged this resubmit) |
| `architect/__tests__/proposal-outline-map.test.tsx` | test | **this unit:** per-fallback-state coverage + observer transition test |
| `architect/ProposalOutlineDraw.tsx` | src | DB-047(e) finiteness gate (prior unit; unchanged this resubmit) |
| `architect/__tests__/proposal-outline-draw.test.tsx` | test | DB-047(e) finiteness specs (prior unit; unchanged this resubmit) |
| `address/__tests__/lot-outline-map.test.tsx` | test | DB-048 flake hardening (prior unit; unchanged this resubmit) |

`LotOutlineMap.tsx`, `ProposalEditor.tsx`, `outline-bridge-api.ts`, every T070-lane file, and all
of `e2e/` are absent from the change set (forbidden — preserved).

## 2. IMPLEMENTATION by file (line anchors)

### 2a. `ProposalOutlineMap.tsx` (src) — DB-047(d)/(e)
- `finitePointCount(points)` L52-56 — counts only points with both ordinates `Number.isFinite`.
- Observer gate L115-131 — `mapRendered` state; an effect keyed on `[bbl]` runs an initial `sync()`
  (querySelector for the leaf's interactive `aria-label`) plus a `MutationObserver(childList,
  subtree)` on the wrapper root, so a leaf transition that does not re-render the wrapper is still
  observed.
- Three-way instruction copy L145-149 — `mapRendered ? (hasSelection ? move : place) : keyboard-only`.
- Status L159-165 — announces `drawnCount = finitePointCount(points)`, never `points.length`.
No prop contract changed; no fetch added → ProposalEditor composition byte-identical for finite flows.

### 2b. `proposal-outline-map.test.tsx` (test) — CHANGED THIS UNIT
- `FALLBACK_STATES` L18-28 — the five required non-drawable leaf states keyed by the leaf's REAL
  data-testid (condo/no-polygon→`lot-outline-empty`, `multiple_features`→`lot-outline-review`,
  `invalid_geometry`→`lot-outline-invalid`, no-WebGL→`lot-outline-webgl-unavailable`, render
  error→`lot-outline-render-error`).
- Mock L40-52 — `"interactive"` renders the aria-labelled container; any other variant renders that
  state's real data-testid **without** the interactive aria-label (mirrors the leaf's branches).
- **NEW per-state coverage** L213-232 — `it.each(FALLBACK_STATES)`: for EACH required state the
  typed surface renders, the interactive `aria-label` is absent, and the copy leads keyboard-only
  (no "Click the lot map to place"). Binds AS-1's "in EACH typed fallback state".
- Selected-point mutation guard L234-243 — a fallback + selection still never says "click the map
  to move it".
- **NEW observer transition test** L245-279 — render interactive (verify click-to-place + label
  present) → flip the mock to `lot-outline-render-error` and `rerender` at the SAME `bbl` (so the
  wrapper effect does not re-run) → assert the copy updates to keyboard-only and the label is gone.
  Only the `MutationObserver` can update the copy on this path.
- Unchanged: `drawnOverlayData` pure specs, click-routing specs, DB-047(e) `finitePointCount`/status
  specs (L282+).

### 2c. `ProposalOutlineDraw.tsx` (src) — DB-047(e) (unchanged this resubmit)
- `finiteCount` / `incompleteCount` / `canConvert` L147-157 — Convert gates on FINITE count.
- `convert()` L159-174 — POSTs finite points only (no-op filter for an all-finite outline →
  byte-identical payload; bridge contract untouched).
- Disable hint L~278-295 (in the returned JSX) — explains added-but-untyped rows vs. too-few points.

### 2d. `proposal-outline-draw.test.tsx` (test) — DB-047(e) (unchanged this resubmit)
- Helpers `fillPoint` L108-112, `addFinitePoints` L114-119.
- Rewritten gate spec L127-151 — 3 added-but-untyped rows keep Convert disabled + hint + 0 overlay
  points; 2 finite still disabled; 3rd finite enables and draws exactly 3.
- Refusal specs L199-227 switched to `addFinitePoints(3)` (finite inputs; accepted behavior kept).

### 2e. `lot-outline-map.test.tsx` (test) — DB-048 (unchanged this resubmit)
- Per-instance instrumentation: `MockMap.sourceAddCounts` (constructor + `addSource`), `mapInstances`
  reset in `afterEach`.
- AS-1 sync spec rewritten: the exact cross-render `toHaveBeenCalledTimes(4)` tally is removed;
  final state is asserted by presence of the overlay source + both overlay layers, in-place update
  by `toHaveBeenLastCalledWith(overlay2)`, and one-source-only by PER-INSTANCE
  `sourceAddCounts["proposal-drawn-outline"]` (`.some(n===1)` and `.every(n<=1)`). A stable
  `fetchImpl` removes rebuild churn.

## 3. AS-5 mutation notes (teeth)

- **DB-047(d) copy gating** — reverting the gate to always-interactive copy reddens: the per-state
  `it.each` specs (each asserts no "Click the lot map to place"), the selected-point mutation guard
  (would surface "click the map to move it" with no map), and the observer transition test (stale
  click copy survives the removal).
- **Observer removal** — deleting the `MutationObserver` (keeping only the one-time initial `sync`)
  reddens the transition test specifically: initial `sync` sets `mapRendered` true while the leaf is
  interactive, and nothing re-syncs after the container is removed, so the copy stays click-to-place.
- **DB-047(e) finiteness** — reverting `canConvert`/status to raw `points.length` reddens the draw
  gate spec (Convert would enable on 3 untyped rows) and the map status spec (would announce "2
  points drawn" with one NaN row).
- **DB-048 duplicate-source** — dropping the leaf's `getSource(id) ? setData : addSource` guard
  drives one instance's `sourceAddCounts` past 1 → `.every(n<=1)` reds; a per-instance check does
  not false-fail on a legitimate whole-map rebuild.
- **DB-048 stale payload** — an in-place update with an outdated collection reds
  `toHaveBeenLastCalledWith(overlay2)` (a plain `toHaveBeenCalledWith` would not, since overlay2
  still sits earlier in history).

## 4. Leaf rendering conditions (forbidden `LotOutlineMap.tsx`, read-only reference)

The wrapper's `INTERACTIVE_MAP_LABEL` signal is emitted by the leaf ONLY on the drawable path, so
the mock's variants reproduce real branches, not invented ones. Read via
`git show HEAD:apps/web/src/components/address/LotOutlineMap.tsx`.
- Drawable predicate L409-413: `view.outcome === "single_lot" && view.geometry !== null &&
  webglAvailable`.
- Interactive container with `aria-label="Interactive approximate lot outline map"` renders ONLY at
  L640-647 (`drawable && !mapRenderFailed`).
- Typed fallbacks (NO aria-label): render error `lot-outline-render-error` L657; no-WebGL
  `lot-outline-webgl-unavailable` L672; unusable geometry `lot-outline-unavailable` L685; condo/no
  lot `lot-outline-empty` L696; `multiple_features` `lot-outline-review` L707; `invalid_geometry`
  `lot-outline-invalid` L719.

## 5. Acceptance scenarios

- **AS-1 (copy gating):** §2b per-state `it.each` (each required fallback → keyboard-only) + drawable
  click-to-place/move specs + §4 leaf conditions + §3 mutation note.
- **AS-2 (finiteness gate):** §2d gate spec + §2c production gate + §2b status/`finitePointCount`.
- **AS-3 (byte-compatibility):** §2a/§2c no-op filters, unchanged prop contract, no ProposalEditor
  edit (forbidden, absent from change set); accepted specs unchanged.
- **AS-4 (DB-048 hardening):** §2e — no exact cross-render tally remains in the AS-1 spec; one-source
  + in-place setData via per-instance counts and last-payload.
- **AS-5 (teeth):** §3 mutation notes.
- **AS-6 (scope):** exactly the packet's allowed_paths changed; zero new deps; no e2e touched;
  modularity exit below.

## 6. Self-check evidence (cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t071`)

- `python tools/modularity_check.py --check` → `selected 475 files; failures 0; warnings 22` (no
  warning names any file in this packet).
- Scope: only the 5 allowed source/test files + this report are modified; all forbidden files above
  are absent from the change set.

## 7. Verification boundary (thin client) — web results PENDING

No local npm/node was run or documented; the web unit/component specs prove ONLY in CI on the
orchestrator's pushed head. This report is the design/DOM argument; the independent G3/G4 gates and
CI are the proof. The orchestrator must supply CI evidence for the committed material commit,
covering the two architect test files, the address `lot-outline-map` test, and the unchanged
finite-flow suites that prove AS-3 byte-compatibility. No merge or acceptance is claimed here.

END OF REPORT
