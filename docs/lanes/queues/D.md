# Lane D — Architect interface: queue

Ordered: take the top unblocked item. Built from `docs/lanes/RECONCILIATION.md` (partial and missing items only) under the derived lane plan `docs/lanes/PARALLEL_BUILD_PLAN.md`. Each item becomes one ledger task `M<x>-T<n>` that cites D-090 and the plan ID; its "Done when" is the plan's text unless marked *derived*. Waves: 1 foundations · 2 Milestone 1 + 2 · 3 breadth and parity (plan §11b: never delays Milestone 1). Owned by Lane C; the lane updates only `docs/lanes/status/D.md`.

Nothing here starts before the owner's GO (D-090-R007).

| # | Plan ID | Task | Done when | Depends on | Blocked by | Wave | Size |
|---|---|---|---|---|---|---|---|
| D-01 | M1-06 | M1-06b + §7: proposal editor and coordinate drawing behind a default-off INTERNAL_PROPOSAL_EDITOR_ENABLED; real properties never start from rectangleSampleDraft; the example only in an explicit Example project; e2e harness turns the flag on (request to C) | M1-06: No example values in any real-property state, request or report | — | — | 1 | M |
| D-02 | §3 | Make the single-page dashboard the default entry; the multi-page screen goes behind a default-off flag with a server-side redirect (set-aside #4) | *derived:* One entry screen; nothing deleted | — | Q4 | 1 | M |
| D-03 | M1-17 | §5a pass part 1: one status strip (≤3 items), details on tap, "Notes (N)" grouping, standing notices behind the strip, readable text, no internal codes, "Not available — reason" instead of caution labels; the clutter cleanup list | M1-17: Passes UI review, including the §5a acceptance test | — | — | 1→2 | L |
| D-04 | M1-13 | Lot choice ("use all (default) or pick"), non-touching or cross-block combinations refused with the reason, "Based on the lots you selected — the app does not verify the zoning lot"; site facts with source labels and edit | M1-13: No measurement has to be typed for Pilot A | C-05, B-02 | — | 1 | L |
| D-05 | §5 | Three-answers panel against results fixtures: value, or "Not available" with the reason; completeness line | *derived:* Matches §5 calculation behavior on fixtures | M5-T125 contracts | — | 1 | M |
| D-06 | M2-07 | Hide the unused-floor-area section behind a flag now (set-aside #6); later the keep/remove step with the existing zoning floor area input and its source | *derived:* §3 step 4 on screen | A-03 | — | 1→2 | M |
| D-07 | M1-25 | Add-on switches with gains and requirements, Best combination goal picker, exclusions shown | M1-25: Gains relative to the current selection, and the best combination, equal the golden record; the goal and assumptions are saved with the option | A-06 | — | 2 | M |
| D-08 | M1-15, M1-16 | Plan, section and floor-stack views showing the server SVGs; editable floor-to-floor heights | M1-15: Dimensions match the numbers · M1-16: Section and massing match the numbers, or one line names what is missing | E-01 | Q8 (section view vs the hold) | 2 | M |
| D-09 | M1-24 | Floor-area availability reminder (exact §5a wording) from the status strip | M1-24: Available from the status strip and shown once in the report | D-03 | — | 2 | S |
| D-10 | M1-18 | Compare options side by side, plans at a common scale | M1-18: Identical rows; plans at a common scale | C-09, D-08 | — | 2 | M |
| D-11 | M2-08 | Keep / partial rebuild / full rebuild comparison with the headline | M2-08: On the 215-16 Northern Blvd benchmark, path 1 keeps more floor area than path 3, and the app says so | A-07 | — | 2 | M |
| D-12 | M2-06, L-11 | §8 warnings and §8a flags: once, beside the affected results, within the §5a limits | M2-06: Each warning appears once, beside the affected results | B-09 | — | 2 | M |
| D-13 | M1-00, M1-17 | Mockup for the architect review and the §5a rule-7 acceptance harness | M1-00: Two or three architects have reviewed the §3 flow; findings recorded · M1-17: Passes UI review, including the §5a acceptance test | D-03 | Q10 | 1 | S |
| D-14 | M2-01, M2-02 | Wallabout options (floor area only, height gap named once) and its comparison report | M2-01: Options shown; the height gap is named once · M2-02: Report matches the screen | B-07, A-04, E-04 | — | 2 | M |
| D-15 | §11b | Parity panels (scenario comparison, unit estimate with formula, unused floor area, data flags) | *derived:* §11b UI rows | B-11 | — | 3 | M |

## Blocked by owner or reviewer

- **D-02** — Q4
- **D-08** — Q8 (section view vs the hold)
- **D-13** — Q10

