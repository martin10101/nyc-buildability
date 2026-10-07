# R6B reference cases

These are worked examples of the R6B zoning limits, kept in their own files, apart from any program
output. They exist so that later tests of the program can take their expected values from a case file
and never from a program run. This is step R0 of the R6B results work order
(`docs/plans/R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md`).

## What a reference case is, and what it is worth

Each case was prepared by an AI helper that took no part in writing the program's rules. The helper
worked only from a sealed folder: pinned law-text captures and the lot's recorded official facts, with
no access to the program. Each case was then recomputed by a second AI, independently, from the same
sealed folder.

That agreement, between two AI answers, is not on its own proof of anything. Each case is written so a
person can follow it with the law text and a calculator: every value gives the facts it used and where
they came from, the law quoted with its capture, why the rule applies, the arithmetic step by step, and
the expected value. Every case is a draft reading of the law. It is **not professionally reviewed** and
it is not a statement that any lot complies with anything.

Nothing in a case comes from a program run: not a value, not a column, not a sentence. The work order's
"Program today" and "First screen" columns stay in the work order.

## The cases

| File | What it covers |
|---|---|
| `cases/real-lot.json` + `real-lot.md` | The real lot, 215-16 Northern Boulevard, Queens (BBL 4073340070): floor area, heights, coverage, units, lot type, frontages, street widths, rear yard and setback (work order table A, rows L1 to L15). |
| `cases/interior-lots.json` + `interior-lots.md` | Four made-up interior lots, chosen to show the floor-area arithmetic and the dwelling-unit rounding threshold, plus the interior-lot coverage reading (table B: P1, P3, P4, P5 and the interior-coverage reading). |
| `cases/corner-reach.json` + `corner-reach.md` | How far a corner lot reaches from each street line and from the corner point: the real lot and three made-up rectangles C1, C2 and C3 (table C). |
| `cases/suffix.json` + `suffix.md` | Whether the sections that list the R6 group reach the suffixed R6B district, through ZR 11-25 (table D: ZR 23-362, 23-52, 23-344, and ZR 23-22 and 23-432 which list R6B directly). |
| `cases/step-p1-worked.json` + `step-p1-worked.md` | The rows worked from the step-P1 captures (task M4-T027): the ZR 12-10 corner, interior, through and lot-area definitions, special density areas, ZR 23-342 and ZR 23-363. It covers three made-up corner lots (100 by 100, 150 by 100, 200 by 120), a 40-by-100 interior lot, a 40-by-200 through lot, and special density areas (section 5 gaps K1, K2, K4, K11). |

Each case is kept twice from one source: a structured data file under `cases/` that a test can load, and
a page rendered from it that a person can read. The helper returns are kept unchanged under
`provenance/`: the two first-round returns and the two step-P1 readings.

## Law text: what step P1 captured, and what is still not captured

**Step P1** (task M4-T025) captured the law text these cases waited for, and task M4-T027 worked the
rows from it (see `cases/step-p1-worked.json`): the ZR 12-10 definitions of a corner, interior and
through lot and of lot area; the ZR 12-10 definition of special density areas; **ZR 23-342** (rear
yard requirements); and **ZR 23-363** (special coverage rules for some interior and through lots). The
rows that were "not known" for want of that text now cite the captured snapshots.

Some readings still rely on law text that is not captured. These cases name each such item and record
the affected value as "not known" where the text is needed for a number:

- **ZR 23-343** (rear yard equivalent requirements) - the rear yard for a through lot.
- **ZR 23-434** (eligible sites) - the 65/50-percent lot-coverage branch of ZR 23-362(b).
- The **ZR 12-10** definitions of *front lot line*, *rear lot line*, *side lot line* and *lot width* -
  needed to identify a rear lot line and to set a rear-yard depth.
- The geographic **boundary definitions** of the *Manhattan Core* and the *Special Downtown Brooklyn
  District* - needed to place a lot in or out of a special density area.
- The **base plane** and height-measurement rule for R6 through R12 districts.
- The **commercial-overlay** sections of **step P2** (the C2-2 overlay and the Article III use and bulk
  rules) - these cases read the residential rules only.

## The rule for changing an expected value

An expected value in a case changes only with a recorded reason, written in the case's change log:

- **corrected evidence** (a recorded fact was wrong and is corrected);
- **a corrected reading** of the law text; or
- **a change in the law** itself.

A disagreement between a case and the program is never, on its own, a reason to change the case. It is
**investigated on both sides**: the case's reading and the program's reading are both examined, and the
side that is wrong is corrected for a recorded reason.

## How a test uses a case

A later test reads a row's expected value by its case id and row id through the loader in
`services/api/tests/rules/reference_cases/`. The checker and test there also recompute every arithmetic
step from the operands in the data file, compare each cited capture's digest with the live capture file,
confirm the quoted words are in the capture, and prove that no case file carries a program result. None
of that code imports the rule engine, the scenario engine or any program output.
