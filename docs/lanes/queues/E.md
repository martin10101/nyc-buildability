# Lane E — Outputs and parity: queue

Ordered: take the top unblocked item. Built from `docs/lanes/RECONCILIATION.md` (partial and missing items only) under the derived lane plan `docs/lanes/PARALLEL_BUILD_PLAN.md`. Each item becomes one ledger task `M<x>-T<n>` that cites D-090 and the plan ID; its "Done when" is the plan's text unless marked *derived*. Waves: 1 foundations · 2 Milestone 1 + 2 · 3 breadth and parity (plan §11b: never delays Milestone 1). Owned by Lane C; the lane updates only `docs/lanes/status/E.md`.

Nothing here starts before the owner's GO (D-090-R007).

| # | Plan ID | Task | Done when | Depends on | Blocked by | Wave | Size |
|---|---|---|---|---|---|---|---|
| E-01 | M1-27 | Drawing kit v0: server-made vector SVG site plan, section and axonometric massing from results geometry; drawing style table (colorblind-safe colors, hatches, line weights, CAD layer names) shared by screen, PDF and DXF; every label read from results; snapshot tests | M1-27: Every figure on a drawing matches the tables; benchmark PDFs match approved snapshots; the same SVGs appear on screen | M5-T125 contracts | — | 1 | L |
| E-02 | M1-22 | PDF converter trial (one day, benchmark lots): WeasyPrint vs headless Chromium; admission through the dependency-security gate (7 days, zero advisories, G5) and a Render runtime check | *derived:* A chosen converter admitted, or a blocker naming why not | — | — | 1 | M |
| E-03 | M1-22 | DXF from results geometry: lot and envelope on separate layers, feet 1:1, the measurement-status note when not surveyed, correct option label, lot-only export allowed | M1-22: The PDF contains every listed sheet; the Excel file matches the screen; the DXF opens correctly in AutoCAD and carries the measurement-status note when measurements are not from a survey | E-01, A-04 | — | 1→2 | M |
| E-04 | M1-19 | Report from the ReportModel, bound to option + revision; historical export record, read-only; "start a new study from this" copies inputs only | M1-19: Report matches the screen and revision | C-06, E-01, E-02 | — | 2 | L |
| E-05 | M1-22 | Excel that mirrors the screen, with values, units, sources and ZR sections (library admission through the gate) | M1-22: The PDF contains every listed sheet; the Excel file matches the screen; the DXF opens correctly in AutoCAD and carries the measurement-status note when measurements are not from a survey | E-04 | — | 2 | M |
| E-06 | C-4, C-5, M1-27 | Consistency sweep over every report value (heights, floors, parking, flood, elevators, units); benchmark PDF page snapshots in CI | *derived:* C-4 and C-5 pass on 215-16 Northern | E-04 | — | 2 | M |
| E-07 | §5c | Location and zoning maps from city open data (license-checked imagery only) | *derived:* §5c-2 maps | E-01 | — | 2→3 | M |
| E-08 | L-5 | "Explain this" and "Likely examiner questions" (AI explains, never changes numbers) | *derived:* Per plan L-5 | E-04 | — | 3 | M |
| E-09 | §11b, L-10 | 485-x eligibility, comparable sales (similar type and size), simple financials — every figure labeled with source and date | *derived:* §11b output rows | B-11 | — | 3 | L |

## Blocked by owner or reviewer

- none

