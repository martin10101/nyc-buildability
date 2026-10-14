# M5-T171 producer report — website page-1 parity (the legal ceiling beside the apartment estimate)

Builder: frontend-engineer. Contract head: `654ea3fade56e075f7bb447eb2f87d0b88fb38a4`
(`task/wave24-report-v3`). Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-af09a58e6007bf493`.

## What changed and why

The Results panel now carries ONE additive block that shows the same answer report page 1 shows:
the legal ceiling beside the apartment estimate, the identical distinction line, the R055 lot-area
assumption line and, while the zoning lot is unconfirmed, the zoning-lot concern. The block is
additive — it changes no other card; the existing allowance card keeps its own `29 units` value
(`three-answers.ts` is untouched, read-only). Every figure is READ from the `results` document the
panel already receives and only formatted for reading; nothing is recalculated in TSX. The 29 is
never shown as settled; an absent limit or estimate degrades to no figure in plain words; a withheld
limit shows the document's own reason.

Files (all inside the packet's allowed paths; `three-answers.ts` and the forbidden tests untouched):

- `apps/web/src/lib/architect/apartment-figures.ts` (new) — pure view-model over the document.
  Mirrors report page 1 exactly: `legalCeiling` = `unit_limit_text.legal_ceiling`; `apartmentEstimateRange`
  = `readers.apartment_estimate_range`; `lotAreaBasisLine` = `page_decision_summary._floor_area_basis`
  (× is U+00D7; "alone" only while unconfirmed; the generic fallback line when recorded area / FAR /
  tax lot is absent); `zoningLotConcern` = `zoning_lot_item.zoning_lot_basis` (the ACRIS
  "register of recorded documents" marker); `recordedLotAreaText` = `readers.recorded_lot_area_text`;
  `formatIntCommas` / `formatRatio` / `formatMeasure` byte-match `report/formatting.py` (so the
  ceiling shows `29`, not `29 units`). Holds the distinction LITERAL `CEILING_ESTIMATE_DISTINCTION`.
- `apps/web/src/components/architect/answers/ApartmentFigures.tsx` (new) — renders the block with its
  OWN test ids (`apartment-figures`, `-ceiling`, `-ceiling-value`, `-ceiling-chip`, `-estimate`,
  `-estimate-value`, `-estimate-chip`, `-distinction`, `-lot-area`, `-zoning-lot`, `-draft-gated`).
  Never reuses `answer-conditional-marker` / `answer-value` / `answer-headline-number`. Status is told
  by the WORD on each chip; both chips carry one neutral surface, so status is never colour-only.
- `apps/web/src/components/architect/answers/ThreeAnswersPanel.tsx` — renders `<ApartmentFigures>`
  after the three answer cards (the same relative place report page 1 carries it, after the answers
  summary), passing `showDraftValues` so the draft gate applies.
- `apps/web/src/components/architect/answers/three-answers.css` — `.af-*` styles, tokens only (no
  colour literal; the pair wraps to one column on a narrow screen).
- `apps/web/src/components/architect/answers/__tests__/apartment-figures.test.tsx` — S1/S2/S4/S6/S7
  and the per-input-state table.
- `apps/web/src/components/architect/answers/__tests__/three-answers-panel.test.tsx` — DB-214 N2
  reconciled in-scope + the whole-panel marker-discipline guard (mutation #3 target).
- `apps/web/e2e/results-layout.flag-on.spec.ts` — the six widths now also assert the block is visible,
  holds no clipped text, and its ceiling/estimate cells never overlap. (Not run here — CI runs it.)

Design note (placement): the block is placed AFTER the answer cards, matching report page 1's order
(`page_decision_summary.render`: answers summary → ceiling/estimate block → uncertainties) and
keeping the identity and the floor-area headline in the first screen, which the e2e S12 case in this
same spec asserts at 390×844. "Beside the headline" is read as a prominent top-level block in the
results panel, not physically above the answer cards.

Draft gate (D-090-R010): the committed fixtures are all `draft: true`. On an architect surface (the
flag off) the block hides every figure and shows only
`Not available — the rules for this answer are not reviewed yet`, exactly as the answer cards do, so
an unreviewed number never reaches an architect. The flag-on surface (`showDraftValues`) shows the
figures.

## The block's exact visible text for the benchmark (`recorded_215_16_northern_journey`, flag-on)

- Heading: `The legal ceiling and the apartment estimate`
- Ceiling value: `Legal ceiling 29`  — chip `Conditional`
- Estimate value: `Estimate 17-22`  — chip `Provisional`
- Distinction: `The ceiling is a conditional zoning limit; the estimate is an unvalidated apartment-yield range; neither is a demonstrated layout.`
- Lot-area line: `10,075 sq ft recorded lot area × FAR 2.0, tax lot 70 alone` (the × is U+00D7)
- Zoning-lot concern (read verbatim from the document's own condition): `If lot 70 alone is the zoning lot. The city's register of recorded documents lists a zoning lot description recorded on February 8, 2022 that is filed on this lot together with lot 1 on the same block, so the zoning lot may include lot 1. The documents themselves were not read.`

## State / outcome / test table (one test per input state)

| State | Input | Outcome | Test |
|---|---|---|---|
| A | shown ceiling, way conditional (benchmark) | `Legal ceiling 29`, chip `Conditional` | apartment-figures.test.tsx S4 state A |
| J | shown ceiling, way settled (probe) | `Legal ceiling 29`, chip `Provisional` | S4 state J |
| B | ceiling withheld, gap work_owed (probe) | `Legal ceiling: <reason>`, chip `Pending verification`, no number | S4 state B |
| B2 | ceiling withheld, gap missing_information (probe) | chip `Unresolved` | S4 state B2 |
| C | no ceiling (synthetic_all_answers_available, 1.0.0) | `Legal ceiling not available`, no chip | S4 state C |
| D | capacity estimate ranged (benchmark) | `Estimate 17-22`, chip `Provisional` | estimate state D |
| E | capacity estimate `Not known` variant (probe) | `Apartment estimate not available`, no chip | estimate state E |
| F | no building_alternatives (probe) | `Apartment estimate not available` | estimate state F |
| G | ACRIS zoning-lot condition present (benchmark) | concern shown; lot line ends `tax lot 70 alone` | zoning/lot-area state G |
| H | no ACRIS condition (probe) | no concern; lot line ends `tax lot 70`, no `alone` | zoning/lot-area state H |
| I | no recorded area / FAR / tax lot (synthetic_building_alternatives_1_4_0) | `Residential FAR on the recorded lot area` (page-1 fallback) | zoning/lot-area state I |
| draft | draft doc, flag off (benchmark) | only `Not available — the rules for this answer are not reviewed yet` | draft gate |

Every one of the 12 committed valid results fixtures (1.0.0 → 1.5.0, incl. the 1.5.0 `synthetic_*`
documents) renders the block without throwing and reads the ceiling / estimate from the document or
degrades to no figure (S7, parameterised over the fixtures). S2 scans the block for each fixture and
holds none of: buildable, achievable, can be built, feasible, compliant, optimal, preferred, verified,
achieved, recommended.

## D-093 research and verification

Read the protocol and the named evidence records (NB-01 zoning-lot instruments, NB-04 lot-dimensions
basis, NB-05 special-density-area) and NB-04's cited primary sources (PLUTO 26v2, the 2017/2021 tax
maps, ZR 12-10). Confirmed the screen does not contradict the settled readings: the lot-area line uses
the recorded area 10,075 sq ft (basis administrative_record, G-10) and names it "recorded lot area",
never the GIS outline 10,387.99 sq ft (display-only, NB-04); the ceiling 29 stays Conditional, never
settled (NB-05 special-density condition is still open); the zoning lot stays unconfirmed and the
concern is the document's own words (NB-01). I did not edit any evidence record. Unresolved inputs
stay unresolved in every output (the "alone" suffix, the Conditional chip, the zoning-lot concern).

## Checks (direct exit codes)

- `npx --yes npm@11.18.0 ci --no-audit --no-fund` → exit `0` (added 314 packages; lockfile only, no
  package added).
- `npm run lint` → exit `0` (0 errors; 2 pre-existing warnings in unrelated files
  lot-site-setup.test.tsx, study-vocabulary.test.ts — not my files).
- `npm run typecheck` (`tsc --noEmit`) → exit `0`.
- `npx vitest run src/components/architect/answers src/lib/architect` → exit `0`;
  **Test Files 32 passed (32); Tests 591 passed (591)** (jsdom WebGL/getContext console noise ignored;
  the FAIL summary lines are clean).

## Mutation proofs (each applied, shown red, reverted; suite re-run green = 591 passed)

1. Changed one character of the distinction literal (`layout.` → `layoutX.`). Ran S1:
   **2 failed** — `expected '…layout.' to be '…layoutX.'` at apartment-figures.test.tsx:58 and :64
   (both the literal-vs-token and the rendered-line assertions). Reverted.
2. Made the ceiling chip read `"Provisional"`. Ran S4: **1 failed** —
   `expected 'Provisional' to be 'Conditional'` at apartment-figures.test.tsx:91 (state A). Reverted.
3. Gave the block's ceiling chip the test id `answer-conditional-marker`. Ran the whole-panel
   discipline test: **1 failed** — `expected true to be false` at three-answers-panel.test.tsx:332
   (a conditional marker is now inside the parity block). Reverted.

After reverting all three: `npx vitest run src/components/architect/answers src/lib/architect` →
exit `0`, 591 passed.

## What I could NOT check (CI's / the orchestrator's)

- The six-width browser layout (`results-layout.flag-on.spec.ts`) — never run locally (ruling V6:
  builders never start a server; ports 3000/3001/8000 left untouched, the owner's preview kept
  running). The spec is extended for the new block; CI runs it. The orchestrator captures the width
  screenshots.
- Full web unit + e2e suites and the dependency-security checks must PASS IN CI at the accepted head.

## sha256 of each changed file (LF-normalized: `tr -d '\r' < f | sha256sum`)

- `61ab6bb2e12aa27d8c36819d99d84795cbfd4b09933155cb119458ccd2d15905`  apps/web/src/lib/architect/apartment-figures.ts
- `78a6d26bba5170aecddaaf1487a71b721db7bd9c519573095a8b788c677f0ab1`  apps/web/src/components/architect/answers/ApartmentFigures.tsx
- `fdc22b46be302058b8a3e017d812ce6d977032604e61615f589fca995569c599`  apps/web/src/components/architect/answers/ThreeAnswersPanel.tsx
- `827ee4f536aef1ac08d826bf7ee0aee0331dbc655cd853b823edfd87a09dbe1e`  apps/web/src/components/architect/answers/three-answers.css
- `ee36aa9539ddf891fa52f87af1e78a361536c611873a4d654abb04b2154216c7`  apps/web/src/components/architect/answers/__tests__/apartment-figures.test.tsx
- `654488a8716d96ee99a081de3593771563b8f4ef2ab4d7ad2bb7ae4338dc300c`  apps/web/src/components/architect/answers/__tests__/three-answers-panel.test.tsx
- `35b48ee6546d48ac531eee046d264da0fa3434174cf9f0eea4f2a6d0d3e53e53`  apps/web/e2e/results-layout.flag-on.spec.ts
