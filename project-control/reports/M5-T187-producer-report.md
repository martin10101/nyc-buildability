# M5-T187 producer report — the two-zone area-allocation web component (M5-T174 part A)

Builder: frontend-engineer. Worktree `/root/project/nyc-buildability/.claude/worktrees/agent-ae730336036ed881d`.
Claim/contract head `fdfd2749261366dfb219710c69e0dc25235f69ab` (task/wave27-comparison-appendix). Not pushed.

## What was built

A self-contained two-zone area-allocation renderer driven by one accepted 1.5.0 `area_allocation`
block, matching the accepted PDF drawing kernel (`services/api/app/drawings/kit/area_allocation.py`,
M5-T183) in words and behaviour. It is NOT mounted on any default route (R096: Part B mounts it in
lockstep with the PDF illustration, M5-T173). Three source files + three test files replaced their
seeds:

- `apps/web/src/lib/architect/area-allocation-tokens.ts` — the web literals for the two zone labels
  and the caption, byte-equal to `docs/design/presentation-tokens.json` wording group (G-15); the
  two methodology strings (measure words, physical-plate not-checked) come from the presentation
  contract, not the JSON, and are not parity-tested.
- `apps/web/src/lib/architect/area-allocation.ts` — `areaAllocationView(allocation, placement?)`: the
  fail-closed selector. Reason strings are byte-equal to the kernel's `Unavailable` text.
- `apps/web/src/components/architect/answers/AreaAllocation.tsx` — the renderer (bar / fitted
  placeholder / unavailable line).
- three test files (below).

No `services/api/**`, no `packages/contracts/**`, no benchmark-set member and no M5-T170 allowed_path
were touched (S7). `source-links.ts` was read only (never edited). The component is not referenced by
`ThreeAnswersPanel.tsx` or any route.

## Per-scenario outcome

- **S1 (unfitted bar).** `{fitted:false, share:0.65, 12025/6475/18500}` renders one proportional bar
  (`data-role` `area_bar_apartment` 65 % wide, `area_bar_other` 35 %), one percentage "65% apartment
  area", `data-apartment-fraction=0.65` (ratio = share within 0.5 %), and NO footprint, zone or
  division element. PASS.
- **S2 (wording parity, both directions).** The component literals equal the JSON wording tokens read
  from disk, and the rendered labels/caption are exactly those tokens with no trailing full stop.
  Mutating the JSON — or the literal — reddens the test (mutation 3 below). PASS.
- **S3 (fitted placeholder).** `fitted:true` with a placed placement draws no bar and no second
  illustration; it renders a marked placeholder (`area-allocation-fitted-deferred`). Table: fitted
  false → bar, true → placeholder. PASS.
- **S4 (no forbidden marks; one caption).** For every row {fitted∈[false,true], share∈[0.60,0.65,0.75]}
  the DOM holds no room / unit-wall / stair / elevator / apartment-plural / units text; the bar state
  has exactly one caption and the fitted placeholder has none (R093/R095). PASS.
- **S5 (G-14 in expandable detail).** The `<details>` methodology carries the exact conversion
  statement (equal to the block's own value AND to `AREA_ALLOCATION_CONVERSION_STATEMENT`) and lists
  "Physical floor plate (gross-up, exclusions, wall thickness)" as not checked; the statement is NOT
  in the one short caption. PASS.
- **S6 (source-links URL-form parity).** A self-contained positive/negative case table (no runtime
  parse of `law_links.py`): `officialZoningTextUrl` accepts exactly the valid
  `/article-<roman>/chapter-<n>[/<section>][#<section>]` zoningresolution.planning.nyc.gov forms and
  rejects bare-host, no-trailing-slash, wrong-host, http, query, port, credentials, non-roman article,
  three-digit chapter, malformed section, extra segment, bad anchor, space, backslash, over-length and
  non-string forms. PASS.
- **S7 (isolation).** `git show --stat` is six web files + this report only (see the return). PASS.

## Input-state table (selector + component)

| # | input state | result |
|---|---|---|
| 1 | not fitted, share 0.65 | bar, percent 65, fraction 0.65 |
| 2 | not fitted, share 0.60 | bar, percent 60 |
| 3 | not fitted, share 0.65 | bar, percent 65 |
| 4 | not fitted, share 0.75 | bar, percent 75 |
| 5 | share 0.80 (above range) | unavailable — "The apartment share is outside the range shown." |
| 6 | share 0.50 (below range) | unavailable — same out-of-range reason |
| 7 | apartment+other ≠ total | unavailable — "The apartment and other areas do not add up to the total." |
| 8 | apartment/total ≠ share | unavailable — "The apartment area does not match the share shown." |
| 9 | not an object (undefined/null/42/"x"/[]) | unavailable — "There is no area allocation to draw." |
| 10 | wrong fixed label / measure / conversion | unavailable — "The area allocation is incomplete." |
| 11 | non-numeric share | unavailable — "The apartment share is not a number." |
| 12 | non-numeric area split | unavailable — "The area split is not given in numbers." |
| 13 | unstated fitted flag | unavailable — "It is not stated whether the footprint is fitted." |
| 14 | fitted true WITH a placed outline | fitted_deferred (placeholder; zones drawn in Part B) |
| 15 | fitted true WITHOUT an outline | unavailable — "The footprint has not been placed on the lot, so the zones cannot be drawn yet." |

Rows 14/15 realise the "fitted with outline / fitted without outline" distinction and mirror the
kernel's fail-closed-to-not-placed behaviour; the component defers only the actual zones drawing.

## Checks (all in `apps/web` of this worktree unless noted; vitest runs flock-wrapped)

| check | command | exit | result |
|---|---|---|---|
| install | `npx --yes npm@11.18.0 ci --no-audit --no-fund` | 0 | 314 packages, lockfile only |
| lint | `npm run lint` | 0 | 0 errors, 2 pre-existing warnings in untouched files |
| typecheck | `npm run typecheck` | 0 | `tsc --noEmit` clean |
| three task tests | `vitest run <3 files>` | 0 | 3 files / 53 tests passed |
| full web unit suite | `vitest run` | 0 | 132 files / 2757 tests passed (jsdom WebGL/getContext noise from MapLibre is not a failure) |
| lane coverage | `python3 scripts/lanes/check_lane_paths.py --coverage` (worktree root) | 0 | PASS, 10676 files each owned by one lane |

## Mutation proofs (applied, observed red, restored byte-identical)

| mutation | test that went red | exit |
|---|---|---|
| not-fitted branch draws a `area_zone_apartment` element | S1 (component) — 1 failed / 13 passed | 1 |
| selector `percent` hard-coded to 65 | selector "share 0.60" and "share 0.75" — 2 failed / 13 passed | 1 |
| `AREA_ZONE_APARTMENT` changed to "Apartments area" | S2 parity (both asserts) — 2 failed / 12 passed | 1 |

After each, the file was restored from a pre-mutation backup; `diff` against the backups is empty and
no `MUTATION-PROOF` residue remains; the three task tests re-ran 53/53 green.

## Research / verification (D-093)

The component draws a pre-computed split from the document block and revises no evidence record. NB-04
(measure basis) read only to confirm the share applies to the estimate's own measure
(`residential_floor_area`). The settled allocation reading `placement-building-b.json` (step P8, the
one stated 60 % apartment-area share) is not contradicted: the renderer never invents or hardcodes a
share — it prints the block's own `share` (round(share×100)) and its own areas, and fails closed when
they do not reconcile. Reference cases read, never re-researched.

## What I could not check (out of a builder's scope)

- No server, no `npm run dev`, no Playwright, no ports 3000/3001/8000 were started (G-1). The
  real-preview readability check (R098) and the before/after captures bind to Part B when the
  component is mounted (G3 here is the visual-quality reviewer's unit-render check).
- R027 is satisfied here only as web-validator URL-form parity (the component renders no live law
  link); its full "rendered citations resolve to the exact section" is Part B.
- Full CI (web-e2e, security/age gates) runs on the exact head in CI, not locally.
