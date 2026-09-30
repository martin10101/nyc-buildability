# Estimate — Waves 1–3 (derived, Wave 0 task M0-T162)

Plain summary first, then the working. Ranges, not promises: they move with reviewer hours and how fast owner decisions come back.

## In one paragraph

From the owner's GO, **Milestone 1 (one real lot, verified) takes about 6–9 weeks** if the reviewer gives 6–10 hours a week from week 2 and owner decisions come back within 2 days. With 3 hours a week or less it is about 9–13 weeks. **Milestone 2 (298 Wallabout) lands about 2–3 weeks after Milestone 1**, since part of it runs alongside. **The R6–R10 wave finishes about 4–7 weeks after Milestone 1** and is paced by reviews. The engineering is parallel. What serializes it is the benchmark data, the R6B rules, the golden record (reviewer + pilot lot) and the wiring.

## Sizes

S ≤ 1 lane-day · M 2–4 lane-days · L 1–2 lane-weeks. A lane-day includes the build, the independent reviews, CI (about 40 minutes a run) and the merge. Five lanes run in parallel; the integrator merges one PR at a time, C → B → A → D → E.

| Item | Plan IDs | Size | Wave |
|---|---|---|---|
| A-01 | M1-03 | M | 1 |
| A-02 | L-1, C-1, C-2, C-12 | L | 1 |
| A-03 | M2-07, C-3 | S | 1 |
| A-04 | M1-14, C-2, C-11 | L | 1→2 |
| A-05 | C-6, C-11 | S | 2 |
| A-06 | M1-25 | L | 2 |
| A-07 | M2-08 | M | 2 |
| A-08 | M1-04 | S | 1 |
| A-09 | M1-26 | M | 2 |
| A-10 | L-1 | M | 2 |
| A-11 | L-1 | L | 3 |
| A-12 | L-2, L-3 | L | 3 |
| A-13 | C-10 | M | 3 |
| A-14 | L-7, L-8, L-9 | L | 3+ |
| B-01 | M1-20, C-3, C-7, C-8, C-9 | M | 1 |
| B-02 | M1-07 | M | 1 |
| B-03 | M1-13 | L | 1 |
| B-04 | M1-13 | M | 1 |
| B-05 | M2-07 | M | 2 |
| B-06 | C-7 | S | 1 |
| B-07 | M2-05 | L | 2 |
| B-08 | M2-00 | S | 2 |
| B-09 | L-11 | L | 2→3 |
| B-10 | C-8 | S | 2 |
| B-11 | §11b | L | 3 |
| C-01 | M1-01 | S | 1 |
| C-02 | M1-02 | S | 1 |
| C-03 | M1-09 | M | 1 |
| C-04 | M1-06 | M | 1 |
| C-05 | M1-10 | L | 1 |
| C-06 | M1-11 | L | 1→2 |
| C-07 | M1-08 | M | 1 |
| C-08 | M1-12 | L | 2 |
| C-09 | M1-18 | M | 2 |
| C-10 | M1-26 | S | 1 |
| C-11 | M1-20 | M | 2 |
| C-12 | M2-03 | S | 2 |
| C-13 | — | S | 1 |
| C-14 | — | S | 1 |
| D-01 | M1-06 | M | 1 |
| D-02 | §3 | M | 1 |
| D-03 | M1-17 | L | 1→2 |
| D-04 | M1-13 | L | 1 |
| D-05 | §5 | M | 1 |
| D-06 | M2-07 | M | 1→2 |
| D-07 | M1-25 | M | 2 |
| D-08 | M1-15, M1-16 | M | 2 |
| D-09 | M1-24 | S | 2 |
| D-10 | M1-18 | M | 2 |
| D-11 | M2-08 | M | 2 |
| D-12 | M2-06, L-11 | M | 2 |
| D-13 | M1-00, M1-17 | S | 1 |
| D-14 | M2-01, M2-02 | M | 2 |
| D-15 | §11b | M | 3 |
| E-01 | M1-27 | L | 1 |
| E-02 | M1-22 | M | 1 |
| E-03 | M1-22 | M | 1→2 |
| E-04 | M1-19 | L | 2 |
| E-05 | M1-22 | M | 2 |
| E-06 | C-4, C-5, M1-27 | M | 2 |
| E-07 | §5c | M | 2→3 |
| E-08 | L-5 | M | 3 |
| E-09 | §11b, L-10 | L | 3 |

Lane-days per lane and wave (low–high):

| Lane | Wave 1 | Wave 2 | Wave 3 |
|---|---|---|---|
| A | 13–26 | 11.5–23 | 17–34 |
| B | 11.5–23 | 13–26 | 5–10 |
| C | 18.5–37 | 9.5–19 | — |
| D | 18.5–37 | 12.5–25 | 2–4 |
| E | 9–18 | 11–22 | 7–14 |

(Items spanning two waves, such as "1→2", are counted in the wave where they start.)

## Critical path to Milestone 1

1. **B-01** records the benchmark lot's official data (M, week 1).
2. **A-02** builds the R6B draft rules (L, weeks 1–2), in parallel with **C-03** wiring the contracts (M).
3. **A-04** builds the three-answer generator on the benchmark (L, weeks 2–3).
4. **M1-05, the golden record,** needs the owner's pilot lot (Q1) and the reviewer (Q12, 1–2 weeks of reviewer time). **This is the pace-setter.**
5. **C-08** wires engine → API → dashboard (L), and **A-06** adds the add-ons (L), weeks 4–6.
6. **E-01** builds the drawing kit in parallel from week 1. **E-03, E-04 and E-05** (DXF, report, Excel) follow in weeks 4–7; E-02 must admit a PDF converter first.
7. **C-11** runs the address-to-export journey in CI, then **M1-21**, the observed architect session (owner schedules), weeks 6–9.

Off the critical path but needed for it: the set-asides (**D-01, A-03, D-02**) and the §5a pass (**D-03**) in weeks 1–3; the site geometry and street widths (**B-03, B-04**) in weeks 1–3.

## Assumptions

- The owner's GO this week; the lanes run as cloud producers the integrator dispatches (the other option, Codex loops on the PC, first needs disk space and the owner-typed commissioning).
- Reviewer: 6–10 h/week from week 2 for the fast range; ≤ 3 h/week for the slow range. The reviewer marks rule tables reviewed and signs the golden record; AI never does.
- Owner decisions (Q1, Q4, Q8, Q10, reviewer) answered within 2 days.
- No new blocker from dependency admission (PDF/Excel libraries must be ≥ 7 days old and advisory-free) or from the Render runtime.
- Sign-in and durable storage (B-001, Q7) are not needed for Milestone 1 on fixtures. Saved revisions and read-only history wait for them.
- The GitHub CI budget absorbs about 5–10 PR runs a day across the lanes.

## What would make it faster

- Choose the pilot lot (Q1) early. If 215-16 Northern itself is acceptable as Pilot A, the benchmark and the golden record converge. It does have recorded zoning-lot documents, which the plan prefers to avoid.
- Block reviewer time in weeks 2–4 for the R6B tables and the golden record.

