# M5-T066 producer report — map-CLICK interaction slice (click-to-place/adjust outline vertices)

Task: D-082-R001/R003 map-CLICK slice — the interaction layer the T065 compose-only wall left
undeliverable. The architect clicks the accepted lot map to PLACE outline points and click-selects a
placed point to MOVE or DELETE it; the clicked display-4326 positions enter the SAME single
drawn-outline state the accepted keyboard/numeric path fills, feeding the one accepted
drawing→bridge→adoption path. Zero new math, zero new dependencies. Map surface IN scope this time
(additive-optional prop on `LotOutlineMap`).

Regime refs: D-082-R001/R003, D-066-R001, D-076-R001/R002, D-077-R002/R003.
Base (contract/claim-seam) sha: `980159f4763586636434ff2b850c02f02020e03a`.

**Honesty banner (read first).** Web behavior (every component/e2e spec) and the mutation-revert
evidence are UNVERIFIED here — thin client, no local npm/npx/node (CODING_RULES). They prove ONLY in
CI on the pushed head. No web/mutation PASS is claimed. The single local command run is the documented
modularity check (§2), and its authoritative pass is the SUPERVISOR's recorded evidence at harvest —
the line below is my producer self-check outcome, not a gate record.

## §0 Revised handoff — truncation recovery (this pass)

The prior producer RETURN was truncated in transmission: the implementation and tests were
omitted from the message, never from the tree. All 11 change files are PRESENT and COMPLETE in
the working tree at this head (`git status --porcelain` = exactly the allowed paths, no forbidden
path; the table below lists each). No code defect is established by a transmission truncation.

Supervisor harvest collects the evidence — this report never duplicates source:
- Collect a BOUNDED per-file patch for each of the 8 TRACKED changes (`git diff -- <path>`),
  especially `ProposalOutlineDraw.tsx`, `ProposalEditor.tsx`, `proposal-draft.ts` and their tests.
- Retain the 3 UNTRACKED complete artifacts verbatim: `ProposalOutlineMap.tsx`,
  `__tests__/proposal-outline-map.test.tsx`, and this report.
- Behavior is referenced by file + symbol/line anchor (§1), never pasted.

Web + mutation outcomes stay PENDING controller-authorized CI tied to the HARVESTED commit (thin
client — no local npm/npx/node). Required CI evidence at the pushed head:
- every accepted regression suite green (address/architect web unit specs + the retained e2e
  keyboard AS-4 journey) AND the new specs green;
- the AS-6 reconciliation MUTATION proof: reverting `adoptOutlineVertices`' wall reconciliation
  turns `proposal-draft.test.ts` "AS-6: adopting a SMALLER outline drops the walls that would
  dangle" RED, and the restored code turns it GREEN;
- the LotOutlineMap early-click getLayer-guard mutation: reverting the guard turns
  `lot-outline-map.test.tsx` "AS-2 early-click guard …" RED.

No web/mutation PASS is claimed here. Resubmit for review once harvested; the gate/CI at the
pushed head is the sole verifier of web + mutation behavior (ADR-005).

## Digest binding

Change surface vs the base sha — exactly the allowed paths, no forbidden path
(`git status --porcelain`, `git --no-pager diff --numstat HEAD`):

| File | +add / −del | Role |
|---|---|---|
| `apps/web/src/components/address/LotOutlineMap.tsx` | 156 / 1 | additive-optional map-click interaction + **early-click hit-test guard** |
| `apps/web/src/components/address/__tests__/lot-outline-map.test.tsx` | 158 / 1 | byte-equivalence + click/overlay wiring + early-click guard |
| `apps/web/src/components/architect/ProposalOutlineMap.tsx` | new | interaction wrapper: pure overlay builder + place/move/select routing |
| `apps/web/src/components/architect/__tests__/proposal-outline-map.test.tsx` | new | overlay builder + click-routing unit tests |
| `apps/web/src/components/architect/ProposalOutlineDraw.tsx` | 73 / 8 | shared drawn-outline state: place/select/move/delete + focus + 1–2-pt hint |
| `apps/web/src/components/architect/__tests__/proposal-outline-draw.test.tsx` | 133 / 3 | PARENT integration (shared pointer/keyboard state) |
| `apps/web/src/components/architect/ProposalEditor.tsx` | 17 / 2 | adopt announce naming dropped walls |
| `apps/web/src/lib/architect/proposal-draft.ts` | 45 / 5 | `adoptOutlineVertices` reconciliation + `danglingWallIds` |
| `apps/web/src/lib/architect/__tests__/proposal-draft.test.ts` | 64 / 11 | reconciliation unit + mutation tests |
| `apps/web/e2e/proposal-editor.spec.ts` | 80 / 0 | AS-1 pointer journey (keyboard AS-4/AS-5 retained) |
| `project-control/reports/M5-T066-producer-report.md` | this file | |

Behavior below is anchored to file + symbol/line ranges at this working tree. MATERIAL identity is
frozen by the orchestrator at submit; the supervisor re-collects and hashes at harvest (these files are
uncommitted at report time; `git hash-object` is not in the permitted command set).

## §1 Demonstrated behavior (file + anchors)

### 1a. Additive-optional map surface — `LotOutlineMap.tsx`
- Interaction is gated purely by the presence of `onOutlineMapClick` (`interactive`, l.380): with NO
  interaction prop, no click listener attaches and no overlay source/layer is added — the
  address-confirm consumer is byte-equivalent (AS-3). New optional props documented ll.349–358.
- Click listener (ll.491–522) attaches at construction (behind `interactive`), reads callbacks from a
  ref so a parent re-render never rebuilds the map, keeps positions display-4326 (no CRS math), and
  routes a drawn-vertex hit to `onDrawnVertexClick`, else reports the 4326 position to
  `onOutlineMapClick`.
- **Early-click hit-test guard (the packet's "inspect early-click handling" item).** The drawn-vertex
  layer (`DRAWN_OVERLAY_POINTS`) is installed only by the overlay effect (map ready + a `drawnOverlay`,
  ll.582–611). The click listener attaches BEFORE that. The prior code queried the layer
  unconditionally; a click in that window queries a layer that does not yet exist, and real MapLibre
  fires an `error` event for an unknown layer id — which the module's own `error` handler routes to
  `failRender`, tearing the map down. Fix: `PointQueryMap.getLayer` (ll.70–79) now GUARDS the query
  (l.509) — the hit test runs only once the layer is installed; otherwise the click falls through
  to a place (there are no drawn vertices to hit anyway).

### 1b. Interaction wrapper — `ProposalOutlineMap.tsx` (new)
- `drawnOverlayData` (ll.40–60): PURE overlay builder (unit-tested without WebGL). Emits a Point
  feature per FINITE drawn point KEEPING its original index (so a hit maps back to caller state) with a
  `selected` flag, plus a connecting LineString for ≥2 finite points. A not-yet-typed keyboard row
  (non-finite) is intentionally not drawn.
- `handleMapClick` (ll.86–89): with a selection a map click MOVES the selected point, else PLACES a new
  one; a drawn-vertex click routes to `onSelect`. Every route has a keyboard equivalent in the table.
  The wrapper holds no map instance and no coordinate math beyond assembling the display overlay.

### 1c. Shared single drawn-outline state — `ProposalOutlineDraw.tsx`
- `placePoint` (ll.103–105) appends into the SAME `points` state the keyboard `addPoint` uses — one
  draft model (AS-1). `moveSelectedPoint` (ll.113–123) edits the selected point (keyboard equivalent =
  the row lng/lat inputs). `selectPoint` (ll.127–129) toggles selection.
- `deletePoint` (ll.131–145): focus-on-delete keeps the DB-043(a) remedy (records `pendingFocus`, a
  `useEffect` moves focus after the remove re-render — never a synchronous `.focus()` on a remounting
  node), AND reconciles the selection so it never dangles past the removed row.
- Persistent 1–2-point hint (HJ-4, ll.268–275): a `role="status"` note while Convert stays disabled
  with 1–2 points.
- `ProposalOutlineMap` is composed ABOVE the keyboard table (ll.181–189); typing coordinates stays an
  option, honesty copy is unchanged (drawn shape = proposed input, not a record).

### 1d. Adoption reconciliation — `proposal-draft.ts`, `ProposalEditor.tsx` (HJ-2 / DB-045(f) / AS-6)
- `adoptOutlineVertices` (ll.313–319) replaces the outline vertices AND drops every exterior wall whose
  endpoint index no longer exists, so the model is ALWAYS internally consistent. Equal- or larger-count
  adoption keeps every wall (all indices in range), preserving the accepted T065 equal-count semantics;
  lot-line segments address explicit coordinates (never vertex indices) so they cannot dangle
  (documented ll.292–312). `wallReferencesInRange` ll.269–278, `danglingWallIds` ll.288–290.
- `adoptDrawnOutline` (`ProposalEditor.tsx` ll.114–129) announces EXACTLY which walls were dropped
  (`danglingWallIds`) so a structural change is never silent, clears the stale outcome, and keeps the
  numeric table the visible editable authority.

## §2 Command evidence — explicit cwd (producer self-check; supervisor re-collects)

| Documented command | cwd | Producer outcome |
|---|---|---|
| `python tools/modularity_check.py --check` | worktree root | **failures 0**, 22 pre-existing warnings; NONE in this packet's touched files (LotOutlineMap.tsx and the architect components are NOT flagged). The early-click guard added ~13 lines and stays under the warn threshold. |

The authoritative modularity pass is the SUPERVISOR's gate evidence recorded at harvest; the row above
is my in-run self-check, not a gate record. No web command was run (thin client): every component and
e2e outcome is PENDING CI.

## §3 Acceptance-scenario coverage (honest; web = PENDING CI)

- **AS-1 (click placement)** — `proposal-outline-map.test.tsx` (overlay builder keeps index + selected;
  place-vs-move routing); `proposal-outline-draw.test.tsx` "AS-1: map clicks and keyboard entry append
  into the SAME table and the overlay stays in sync"; e2e "AS-1 pointer" places 3 real map clicks →
  table + Convert. **PENDING CI.**
- **AS-2 (click adjust/delete + keyboard-equivalent + focus)** — `proposal-outline-draw.test.tsx`
  "AS-2: … selected then MOVED by a map click …" and "AS-2: deleting a SELECTED drawn point … keeps
  focus on a delete control (DB-043(a))"; `lot-outline-map.test.tsx` AS-2 (vertex-hit routes to select).
  **PENDING CI.**
- **AS-3 (display-surface byte-equivalence)** — `lot-outline-map.test.tsx` "AS-3 byte-equivalence:
  with no interaction props, NO click listener attaches and only the 2 lot-outline layers are added";
  all accepted lot-outline/address-confirm specs untouched. **PENDING CI.**
- **AS-4 (end-to-end)** — e2e "AS-1 pointer" (pointer → bridge → adopt → check, stubbed bridge asserting
  the 4326→2263 request contracts); the keyboard "AS-4"/"AS-5" journeys are RETAINED unchanged.
  **PENDING CI.**
- **AS-5 (no new math/deps)** — no new dependency (lockfile untouched); no client-side CRS transform in
  any packet file (positions stay display-4326 until the accepted T065 bridge); the wrapper's only math
  is assembling the display overlay. **Grep-provable; PENDING CI for the runtime path.**
- **AS-6 (adoption reconciliation)** — `proposal-draft.test.ts`: equal-count preserves walls/levels;
  SMALLER-count drops exactly the dangling walls with a MUTATION GUARD (reverting the reconciliation —
  keeping `base.exterior_walls` — turns "AS-6: adopting a SMALLER outline drops the walls that would
  dangle" red because W-N/W-W point past the new 3-vertex outline); LARGER-count preserves every wall;
  `danglingWallIds` exact set. The mutation-revert RED is asserted in CI, not locally. **PENDING CI.**

## §4 Module-boundary justification
- The map surface change is ADDITIVE and OPTIONAL: the interaction path lives behind `interactive`
  (presence of `onOutlineMapClick`), so the accepted display consumers add no listener and no overlay
  layer — one module still owns all lot-outline map behavior, extended, not forked.
- The interaction/overlay assembly is a NEW focused wrapper (`ProposalOutlineMap.tsx`) that holds no
  map instance and no coordinate math; the map lifecycle/WebGL fallback/click plumbing stay in
  `LotOutlineMap`. The pure overlay builder is separately unit-testable without WebGL.
- Reconciliation lives in the draft-model layer (`proposal-draft.ts`) as pure/immutable helpers with
  focused tests; the component only announces the result.
- No file this packet touches is flagged by the modularity checker (§2).

## §5 Preservation / disjointness
Only the allowed paths changed (`git status --porcelain`); no forbidden path touched
(`AddressConfirmCard.tsx`, `PropertyOverview.tsx`, `outline-bridge-api.ts`, `e2e/helpers.ts`,
`services/api/`, `packages/contracts/` all untouched). The accepted lib spine
(`outline-bridge-api.ts`, and the T065 bridge) is composed, not edited. Clicked vertices enter the SAME
drawn-outline state as keyboard entry — one draft model, one bridge, one adoption path.

## §6 Outstanding / next action (orchestrator/supervisor)
1. Harvest the working tree and run gates G0/G2/G3/G4; push to obtain CI proof of every web component
   and e2e spec at the pushed head (the ONLY place web + mutation-revert behavior is verified). Not a
   producer action (ADR-005).
2. Record the modularity pass as the supervisor's gate evidence (re-collect from worktree root).
3. The e2e pointer journey requires the interactive map to paint; this relies on the same WebGL premise
   the accepted `architect-workspace.spec.ts` `settledMap` uses (CI Chromium has WebGL). If a CI runner
   ever lacks WebGL, that surfaces as a real signal, not a silent skip.
