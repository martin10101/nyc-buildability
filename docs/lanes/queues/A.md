# Lane A — Engine: queue

Ordered: take the top unblocked item. Built from `docs/lanes/RECONCILIATION.md` (partial and missing items only) under the derived lane plan `docs/lanes/PARALLEL_BUILD_PLAN.md`. Each item becomes one ledger task `M<x>-T<n>` that cites D-090 and the plan ID; its "Done when" is the plan's text unless marked *derived*. Waves: 1 foundations · 2 Milestone 1 + 2 · 3 breadth and parity (plan §11b: never delays Milestone 1). Owned by Lane C (the integrator); lane A never edits it and, under `docs/lanes/`, updates only `docs/lanes/status/A.md` and its own `docs/lanes/requests/A-<n>.md`.

Nothing here starts before the owner's GO (D-090-R007).

| # | Plan ID | Task | Done when | Depends on | Blocked by | Wave | Size |
|---|---|---|---|---|---|---|---|
| A-01 | M1-03 | Rule-coverage matrix: every R district in the current ZR × output (FAR, heights, setbacks, yards, coverage, units) × add-on, plus the street-width source per rule | M1-03: Every R district in the current Zoning Resolution is listed; every cell has a status, inputs and tests | — | — | 1 | M |
| A-02 | L-1, C-1, C-2, C-12 | R6B draft rule tables for the benchmark: FAR ZR 23-22 incl. the qualifying affordable/senior option (2.00 / 2.40); heights ZR 23-432 (30 / 45 / 55; 45 / 65) in ONE height family; corner coverage ZR 23-362; rear-yard waiver ZR 23-344(a); units ZR 23-52 (680, rounds up only at .75). DRAFT with ZR section + version | *derived:* Unit tests reproduce every competitor-review §A value for 215-16 Northern; every height anywhere comes from the one ZR 23-432 lookup (C-1); 20,150 and 24,180 sf both computed (C-2); unit estimate 29 with its formula (C-12). Status stays needs_review (D-090-R010) | M5-T125 contracts | reviewer (Q12) to mark reviewed — not to draft | 1 | L |
| A-03 | M2-07, C-3 | Stop subtracting city-recorded building area: the legacy subtraction goes behind a default-off flag; by default the engine answers "Remaining development capacity: Not confirmed" / "Needs verified zoning-lot boundaries and existing zoning floor area." (owner wording D-090-R038, 2026-10-01; DB-101 option A) (set-aside #6) | *derived:* No result anywhere takes existing floor area from DOF/PLUTO building area; code and tests kept behind the flag | — | — | 1 | S |
| A-04 | M1-14, C-2, C-11 | Three-answer generator on the benchmark fixture: allowance, permitted envelope, building option (floor stack with stated, editable floor-to-floor defaults; floor-by-floor table; computed shortfall reason), emitting results v1 with geometry in feet | M1-14: All three equal the golden record; any shortfall between the option and the allowance is explained | A-02, B-01, M5-T125 contracts | golden record M1-05 (Q1 pilot + Q12 reviewer) for final acceptance | 1→2 | L |
| A-05 | C-6, C-11 | No duplicate options (merge or explain) and no template sentences: every explanation is emitted only when computed true | *derived:* C-6 and C-11 pass on 215-16 Northern | A-04 | — | 2 | S |
| A-06 | M1-25 | Add-on model: automatic add-ons always on; optional switches start off and recalculate together; gains vs the current selection; Best combination with a stated goal from Groups A+B only, exclusions explained; completeness line | M1-25: Gains relative to the current selection, and the best combination, equal the golden record; the goal and assumptions are saved with the option | A-04 | golden record M1-05 | 2 | L |
| A-07 | M2-08 | Existing buildings §5b: keep / partial rebuild / full rebuild (ZR 54-41), rebuild budget, both path-2 traps, exceptions only when they apply, headline sentence; missing inputs → "Not available — needs existing floor-by-floor areas" | M2-08: On the 215-16 Northern Blvd benchmark, path 1 keeps more floor area than path 3, and the app says so | A-04, B-05 | — | 2 | M |
| A-08 | M1-04 | Pilot A candidates: 2–3 ranked lots (district with implemented height rules and ≥2 supported add-ons, R6–R10 preferred, no multi-lot zoning-lot history) with evidence | M1-04: Two or three ranked candidates with evidence | A-01, B-01 | owner confirms Q1 | 1 | S |
| A-09 | M1-26 | Engine validation cases: City Planning examples, DOB-filing comparisons for the pilot family, hand-checked lots; every difference logged | M1-26: The suite runs in CI; every difference from a filing or example is investigated and logged | A-04, C-10 | reviewer (Q12) for hand-checked lots | 2 | M |
| A-10 | L-1 | Wide-street portion: today the higher FAR applies to the whole lot if any part is within 100 ft; apportion per the rule text ("zoning lots, or portions thereof") | *derived:* Reviewer-approved reading implemented and tested; until then the wide-street branch stays behind its flags | — | reviewer legal ruling (Q12) | 2 | M |
| A-11 | L-1 | R6–R10 family completion (plan §12a wave 2): all ZR 23-432 rows, 23-433 setbacks, Quality Housing vs height factor, 23-73x sky-exposure, affordable-housing add-ons — one reviewed family at a time | *derived:* Each family: tables, tests, reviewer sign-off; R answers locked by golden tests | A-02 | reviewer pace | 3 | L |
| A-12 | L-2, L-3 | Groups B (certifications), C (neighbor estimate), D1 (approval switches, never in Best combination), D2 (opportunity notes, no number) | *derived:* Per plan §6 | A-06 | reviewer | 3 | L |
| A-13 | C-10 | Lot-split ideas: each resulting lot evaluated with its own lot type; the subdivision requirement stated | *derived:* C-10 passes | A-04, B-03 | — | 3 | M |
| A-14 | L-7, L-8, L-9 | Catalog upkeep process; commercial districts that allow housing (paired R rules, §12a safeguards); manufacturing-zone residential pathways | *derived:* Per plan L-7/L-8/L-9 and §12a safeguards 1–6 | A-11 | reviewer | 3+ | L |

## Blocked by owner or reviewer

- **A-02** — reviewer (Q12) to mark reviewed — not to draft
- **A-04** — golden record M1-05 (Q1 pilot + Q12 reviewer) for final acceptance
- **A-08** — owner confirms Q1
- **A-09** — reviewer (Q12) for hand-checked lots
- **A-10** — reviewer legal ruling (Q12)
- **A-11** — reviewer pace
- **A-12** — reviewer
- **A-14** — reviewer

