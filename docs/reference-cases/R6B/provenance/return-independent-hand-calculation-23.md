# Independent reading for M5-T184 (reading A of options 6 (residences with a community facility) and 7 (a community facility alone)) (provenance)

M5-T184 PROVENANCE -23 (OPTIONS 6-7, READING A)

What this is: an independent worked reading made on 2026-10-15 by an AI helper that took no part in writing the program's rules. METHOD, stated exactly: each reader had READ access to a detached, read-only checkout of this repository at commit bb5c02b9 (the law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library), was told not to read any program output (no test run, no API call, no report print and no benchmark fixture value), and some readers read official Zoning Resolution pages live; each reader B was additionally told not to read any return- file; the comparer read both readings and opened captures and official pages. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names that pinned, read-only set of captures and settled cases in the detached checkout at bb5c02b9 - it was NOT a sealed folder in the step-P7/P8 sense, and because some official pages were read live this was not an offline reading. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies. It is reproduced below unchanged, byte for byte. A value is recorded in the benchmark-options-2-3-6-7 reference case for options 6 and 7 only where this reading and its paired reading (return-independent-hand-calculation-23.md and return-independent-hand-calculation-24.md) give the same answer on the same basis, confirmed by the independent comparer (return-independent-hand-calculation-25.md).

---

I have read all the primary CF sections, the overlay CF sections, the evidence records, and the settled reference cases. I did not run any program, API, or report. Here is my sealed, read-only worked-example reading.

---

**SEALED WORKED EXAMPLE — Options 6 (community facility + residences) and 7 (community facility alone), 215-16 Northern Boulevard (block 7334 lot 70), R6B + C2-2, corner lot.**

I am an AI agent. Everything below is an unreviewed draft reading of the law (ADR-007), not a professional determination. It decides no eligibility and no use permission an agency must grant; every such point is flagged. All figures use the **recorded** lot area 10,075 sq ft (city record / PLUTO `lotarea`), never the 10,387.99 sq ft GIS outline (a drawing measure, NB-04). Every lot-area figure is **conditional on lot 70 alone being the zoning lot** — unconfirmed; a 2022 ZONE instrument is indexed against lots 1 and 70, so the zoning lot likely includes lot 1 (NB-01, access_blocked).

Capture note: the law-library page lists these Chapter-4 sections as "NOT CAPTURED," but I found `zr-24-11/111/161/162/163/04/52/522/56/33/34/35/36/391` and `zr-22-13/32-131/33-121` all present in `docs/research/zr-snapshots/v1/` (captured 2026-10-14, Last Amended 12/5/2024, both channels pinned). I read the snapshots directly; the library summary is stale on capture state.

**Worked values (CF side; all "draft", not determinations):**

| Item | Value | Unit | Basis | ZR § | Status | Conditions |
|---|---|---|---|---|---|---|
| CF floor area ratio (R6B) | 2.00 | FAR | law, 24-11 R6B contextual row | 24-11 | applies | — |
| CF max floor area | 20,150 | sq ft | 2.00 × 10,075 | 24-11 | applies | zoning-lot + area basis |
| CF FAR for philanthropic/non-profit w/ sleeping accommodations | 2.00 | FAR | 24-111(c): R6B (suffix) defers to 24-11 (NOT the 2.43 non-suffixed-R6 table figure) | 24-111(c) | applies | special permit 74-903 could modify — not known |
| CF FAR in C2-2 overlay | 2.00 | FAR | 33-121 "R5D R6B" row, Col B (CF-only)=2.00, Col C (both)=2.00 | 33-121 | applies | — |
| 24-162 Col A/B CF reduction | — | — | opening clause excepts R6B | 24-162 | not_applicable | — |
| Combined cap, CF + residential (option 6) | 2.00 | FAR total | greatest single-use FAR (CF 2.00, residential 2.00) | 24-161; also 35-31 / 23-20 | applies | →2.40 if residential is qualifying affordable/senior housing |
| Combined max total floor area (standard) | 20,150 | sq ft | 2.00 × 10,075 | 24-161 | applies | per zoning lot |
| CF lot coverage, corner | 80 | % | 24-11 R6B row (corner) | 24-11 | applies | corner portion (within 100 ft of each street line) |
| CF lot coverage, interior/through | 60 | % | 24-11 R6B row | 24-11 | applies | part of lot lies >100 ft from 215 Pl line |
| Mixed-level coverage | higher (residential) | — | 24-163: higher coverage on any level with both uses | 24-163 | applies | mixed building only |
| CF min base / max base / max building height | 30 / 45 / 55 | ft | 24-04(b)(1) routes R6B CF to 23-43 chain → 23-432 R6B row | 24-04(b)(1); 23-432 | applies | measured from base plane (not fixed) |
| Setback above 45 ft base | 10 (wide) / 15 (narrow) | ft | 23-433 via 24-04(b)(1) | 23-433 | applies/not_triggered | only for wall above 45 ft; optional per 23-433(c) |
| 24-52 / 24-522 Chapter-4 height | — | — | 24-522 is "districts without a letter suffix"; superseded by 24-04(b)(1) | 24-52/522 | not_applicable | — |
| 24-56 special height areas | — | — | public-park / Manhattan CD6,9 / Brooklyn CD9 only | 24-56 | not_applicable | unless lot adjoins a 1–15-acre public park — not indicated |
| CF front yard | none required | — | 24-34 lists R1-R5 only; R6B absent | 24-34 | applies (none) | — |
| CF side yard | none required; if side open area provided, ≥8 ft | ft | 24-35(b) (R6-R12) | 24-35(b) | applies | residential 23-30 yards (5 ft) MAY be substituted via 24-04(c) |
| CF rear yard | 30 | ft | 24-36 at every rear lot line | 24-36 | applies | subject to 24-37/38/39 |
| Corner rear-yard waiver | no rear yard within 100 ft of corner | — | 24-391 (R6-R12, streets ≤135°; here ~89.7°) | 24-391 | applies | far corner ~144.6 ft from corner point → part beyond 100 ft, not known |
| Rear-yard CF obstruction | one story, ≤23 ft | ft | 24-33(b)(2) | 24-33 | applies | within 100 ft of wide street in R6B |

**Arithmetic.** CF: 2.00 × 10,075 = **20,150 sq ft**. Combined option-6 total: greatest single-use FAR = max(CF 2.00, residential 2.00) = 2.00 → 20,150 sq ft; if residential qualifies for 2.40, cap rises to 2.40 × 10,075 = 24,180 sq ft (CF portion still ≤ 20,150). CF corner footprint: 0.80 × 10,075 = 8,060 sq ft; interior portion 0.60 = 6,045 sq ft. Shared floor area in a mixed building is attributed proportionally on a base of total floor area **less** the shared portion (35-31 / 23-20, settled step-P5).

**Which uses count as community facility (Use Group III, 22-13).** Educational (schools, colleges/universities, dormitories), faith-based (houses of worship, parish houses, seminaries, monasteries), health (non-profit/proprietary hospitals, ambulatory diagnostic/treatment [●P], long-term care [●P]), and "other" (libraries, museums, non-commercial art galleries/clubs/recreation, community centers, welfare centers, philanthropic/non-profit institutions [●S size-restricted]). In the C2-2 overlay these are permitted per 32-131 (most ●; some with "P" additional conditions or "S" size restriction). CF is also permitted in the underlying R6B residence district (22-13 lists R1-R12), but the **as-of-right vs size-limited (22-132) vs special-permit (22-134) status of each use in the residence district is NOT captured (22-131…135 residence-district tables) — not known.**

**Comparison with option 1 (standard residences: FAR 2.0 → 20,150 sq ft; heights 30/45/55; 29 units by the 680 factor — settled real-lot.json rows L1/L3/L6).**
- **Floor area: no gain.** CF FAR (2.00) equals residential FAR (2.00) in R6B, so option 6/7 adds **zero** extra floor area over option 1. The "B" suffix removes the CF uplift a non-suffixed R6 would get (2.43 under 24-111(b)); 24-162's reduction and 35-33's mixed tightening both except R6B. (A CPC special permit, 74-903, could modify the CF FAR — not captured, not known.)
- **Heights/setbacks: identical** (24-04(b)(1) applies the same 23-43 chain).
- **Lot coverage: a cost.** CF coverage (80% corner / 60% interior) is **lower** than residential (100% / 80%, 23-362). A pure-CF building covers less lot.
- **Dwelling units:** option 7 (pure CF) yields **0** dwelling units (institutional — the 29-unit figure does not apply). Option 6 (mixed) draws units from the residential floor area / 680 (not a special-density area, NB-05), so **fewer than 29** as the CF share grows.
- **Side open area:** CF requires ≥8 ft if provided (24-35(b)) vs 5 ft residential — a minor cost, waivable via 24-04(c).
- **What it adds:** the right to build an institutional Use-Group-III use (school, house of worship, health, library, museum, community center, etc.), alone (7) or combined with residences under one FAR cap (6), within the same 20,150 sq ft envelope.

**Not known / missing items (and where to find).**
1. Residence-district use permission per Group III use in R6B — read 22-131…22-134 (not captured).
2. Whether a 74-902/74-903 special permit raises the CF FAR above 2.00 — capture 74-902/74-903.
3. Qualifying-affordable/senior-housing eligibility (would lift the mixed cap to 2.40 and change units) — a housing-program input, not a lot fact.
4. The zoning lot (likely lots 1+70) and the certified lot area — the recorded 2022 CERT/ZONE/DECL instruments and the 2017 Buckley survey (NB-01, NB-04; access_blocked).
5. Rear-yard requirement on the lot portion beyond 100 ft of the corner — needs adjoining lot-line types, building type, lot width (NB-06; unchanged from option 1).

**Conflicts.** (a) Combination-citation ambiguity: 24-161 (Article II Ch 4, lists R6B) vs 35-31 (Chapter 5, reached via the C2-2 overlay) — both yield the same greatest-single-use 2.00, so the number is unaffected; the citation differs. (b) Lot-area basis conflict: recorded 10,075 vs GIS 10,387.99 sq ft (≈3.1%, NB-04) — I used 10,075. (c) Library stale-capture claim vs the actual present snapshots (resolved: snapshots read directly). No conflict found between the captures and the settled real-lot/overlay/step-P5 cases.

END-OF-REPORT