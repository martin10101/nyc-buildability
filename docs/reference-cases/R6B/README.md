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
| `cases/overlay-reading.json` + `overlay-reading.md` | The commercial-overlay reading worked from the step-P2 captures (task M4-T028): for the benchmark lot with its C2-2 overlay beside the same lot without the overlay, which district's bulk governs and by what route, floor area ratio, lot coverage, dwelling units, base and building heights, the setback, street-wall location, rear yard, which paragraphs of ZR 34-111, 34-24, 35-632 and 35-631 apply, what ZR 35-633 adds, and the sections and defined terms the overlay texts point to that are not captured (section 5 gap K9). |
| `cases/step-p3-worked.json` + `step-p3-worked.md` | The readings worked from the law text captured by task M4-T029 and read independently in step P3 (task M4-T030): the ZR 12-10 lot-line, lot-width and lot-depth definitions for the real lot and a made-up interior lot; the rear yard beyond the corner (the real lot and a made-up 150-by-100 corner lot), the interior lot (ZR 23-342) and the through lot (the rear-yard equivalent of ZR 23-343); ZR 23-436 and ZR 35-633 for the real lot; ZR 34-21 and ZR 34-111 versus ZR 34-112; the Manhattan Core and the Special Downtown Brooklyn District; from what level heights are measured and the base plane; ZR 23-434 and the different maximum of ZR 23-362(b); the definition of "residence, or residential"; and the base of the floor-area shares in ZR 23-231 and ZR 23-232 (section 8; backlog row DB-170 item (a)). |

Each case is kept twice from one source: a structured data file under `cases/` that a test can load, and
a page rendered from it that a person can read. The helper returns are kept unchanged under
`provenance/`: the two first-round returns, the two step-P1 readings, the two step-P2
commercial-overlay readings and the two step-P3 readings.

## Law text: what steps P1 and P2 captured, and what the readers did not have

**Step P1** (task M4-T025) captured the law text these cases waited for, and task M4-T027 worked the
rows from it (see `cases/step-p1-worked.json`): the ZR 12-10 definitions of a corner, interior and
through lot and of lot area; the ZR 12-10 definition of special density areas; **ZR 23-342** (rear
yard requirements); and **ZR 23-363** (special coverage rules for some interior and through lots). The
rows that were "not known" for want of that text now cite the captured snapshots.

**Step P2** (task M4-T026) captured the eight commercial-overlay sections - **ZR 34-11**, **ZR
34-111**, **ZR 34-24**, **ZR 35-53**, **ZR 35-63**, **ZR 35-631**, **ZR 35-632** and **ZR 35-633** -
and task M4-T028 worked the overlay reading from them (see `cases/overlay-reading.json`). Both readings
find the C2-2 overlay changes only the street-wall location rule (from the R6B line-up of ZR 23-431(a)
to the percentage rule of ZR 35-631(b)) and leaves the floor area ratio, lot coverage, dwelling units,
base and building heights, the setback and the all-residential rear yard the same as plain R6B.

The list below is the law text the readers did NOT have when they made these readings (on 2026-10-06
and 2026-10-07). Wherever a case file says a text is "not captured" or "uncaptured", it means exactly
that: it was not captured when that reading was made, so the readers did not have it. A text on the
list may be captured later without having been read for these cases; `docs/research/zr-snapshots/v1/`
shows what is captured now. Capturing a text changes no row on its own: a row changes only when two
independent readings of the new text are made, under the rule in the next section. These cases name
each such item and record the affected value as "not known" where the text is needed for a number:

- **ZR 23-343** (rear yard equivalent requirements) - the rear yard for a through lot.
- **ZR 23-434** (eligible sites) - the 65/50-percent lot-coverage branch of ZR 23-362(b).
- The **ZR 12-10** definitions of *front lot line*, *rear lot line*, *side lot line* and *lot width* -
  needed to identify a rear lot line and to set a rear-yard depth.
- The geographic **boundary definitions** of the *Manhattan Core* and the *Special Downtown Brooklyn
  District* - needed to place a lot in or out of a special density area.
- The **base plane** and height-measurement rule for R6 through R12 districts.
- The sections the **step P2** overlay readings point to that the readers did not have: **ZR 34-21**,
  **ZR 34-22** and **ZR 34-23** (exceptions to applicability of Residence District controls, pointed
  to by ZR 34-11); **ZR 36-64** (special-area height and setback); **ZR 35-71** (the optional
  sky-exposure-plane envelope); **ZR 35-64** (additional height and setback); **ZR 23-435** (towers);
  and **ZR 23-436** (the additional height and setback regulations that ZR 35-633 brings in) - so what
  ZR 35-633 adds stays "not known". Also not among what the readers had: **ZR 23-41** (permitted obstructions, inside
  the mixed-building rule of ZR 35-53) and the defined terms *Manhattan Core*, *mixed building* and
  *prevailing street wall frontage*.

**Step P3** (task M4-T029) captured the law text the earlier readings waited for (27 texts), and task
M4-T030 read it independently (see `cases/step-p3-worked.json`). The step-P3 readers had, among the
newly captured text: the **ZR 12-10** definitions of a *front*, *rear* and *side lot line*, *lot
width*, *lot depth*, *street line* and *zoning lot*; **ZR 23-343** (the through-lot rear-yard
equivalent); **ZR 23-436** and the way **ZR 35-633** brings it in; **ZR 34-21** and **ZR 34-112**; the
**Manhattan Core** and **Special Downtown Brooklyn District** definitions; the **base plane**; **ZR
23-434** (eligible sites); and the definition of *residence, or residential*. With that text the
step-P3 rows settle the lot lines and lot depth of the real lot, the interior lot's width, depth and
rear yard, the through lot's rear-yard equivalent, which paragraph of ZR 23-436 binds a new building on
the real lot, ZR 35-633(a), ZR 34-21's routing, ZR 34-111 over ZR 34-112, the Manhattan Core (not in
it), from what level heights are measured, and the ZR 23-434 and ZR 23-362(b) scope; others stay not
known (the real lot's lot width and its rear yard beyond the corner, the base-plane elevation, ZR
35-633(b)). The step-P3 readings' passing remark that the standard coverage for this corner lot is 100
percent did not work the corner-lot-portion rule and is **not** a reading of whole-lot coverage, so the
coverage rows (real-lot L5, corner-reach real-lot-coverage, and the corner-coverage rows of
step-p1-worked) are unchanged.

From both step-P3 readings' own summary of what they still did not have, the step-P3 readers lacked (an
item is on this list only where BOTH readings name it): **ZR 34-22** (modification of floor area) and
**ZR 34-23** (modification of yards), both named by ZR 34-21; **Article X, Chapter 1** (the Special
Downtown Brooklyn District regulations); and the defined terms *large sites*,
*transportation-infrastructure-adjacent frontage*, *residential floor area*, *short dimension of a
block*, *curb level*, *street wall line level*, *rear wall line level*, and the qualifying-housing terms
(*qualifying affordable housing*, *qualifying senior housing*, *UAP developments*, *Mandatory
Inclusionary Housing areas*, *residential equivalent*) that select the ZR 23-432 height columns. They
also did not have the adjoining zoning lots' lot-line types (needed for the rear yard beyond the corner)
or the site's elevation and grade data (needed for the base plane). The two readings differ on a few
pointers, so those are recorded as differences, not as the agreed list: reading 8 names **ZR 23-34**
(inclusive) and further defined terms; reading 7 names **ZR 23-44** (inclusive) and **ZR 23-341** /
**23-311** / **23-312**. Reading 8 records that ZR 35-62, **35-64**, **35-71** and **36-64** were in the
readers' folder (both had them; reading 7 did not read some of them), so they are NOT on the step-P3
"did not have" list; the exact height and setback numbers stay not known for the undefined
qualifying-housing terms above. As before, a text the readers did not have may be captured later;
`docs/research/zr-snapshots/v1/` shows what is captured now.

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
