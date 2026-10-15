# Independent reading for M5-T185 (option 8 (two buildings on one lot / a divided lot - both meanings), reading A) (provenance)

M5-T185 PROVENANCE -28 (OPTION 8, READING A)

What this is: an independent worked reading made on 2026-10-15 by an AI helper that took no part in writing the program's rules. METHOD, stated exactly: the reader had READ access to a detached, read-only checkout of this repository at commit bb5c02b9 (the law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library), was told not to read any program output (no test run, no API call, no report print and no benchmark fixture value), and, for sections that were not among the captures at the time it read, it cross-checked the official Zoning Resolution page (zoningresolution.planning.nyc.gov) live. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names that pinned, read-only set of captures and settled cases in the detached checkout at bb5c02b9 - it was NOT a sealed folder in the step-P7/P8 sense, and because some official pages were read live this was NOT an offline reading and does not assert the reader was sealed off from every outside source. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies, is buildable, is optimal or is feasible. It is reproduced below unchanged, byte for byte. (Several sections the reading marked uncaptured when it was made - for example 23-51, 23-12, 23-371, 32-421, 33-26, 33-301, 22-12/22-121/22-122, 32-121, 54-311 - were captured afterwards by task M3-T010 and are now present in docs/research/zr-snapshots/v1; the reference case records a value only where both readings of the option agree on the same value and the same basis.)

---

I have everything needed. Writing the sealed worked-example return.

---

**Option 8 — "A split lot with two buildings" — sealed worked reading**
215-16 Northern Boulevard, Queens (BBL 4073340070; block 7334, lot 70), R6B + C2-2 overlay, corner lot (Northern Boulevard wide, 215th Place narrow).

I am an AI agent. This is an unreviewed draft (ADR-007), not a professional or legal determination. It decides no eligibility, no use permission, no subdivision right, no DOB/zoning-lot approval. Every figure is worked on the **recorded** lot area 10,075 sq ft (PLUTO `lotarea`); the 10,387.99 sq ft GIS outline (NB-04) is a conflict check only, never mixed in. All figures are conditional on tax lot 70 alone being the zoning lot — **unconfirmed** (NB-01). No program output, API, benchmark or report value was read; values come from the law text and the settled facts.

The task names two meanings. **A** = two buildings on the one undivided zoning lot (library Reading A.2). **B** = the tax lot divided into two independent zoning lots, one building each (library Reading A.1). Reading B (district-boundary, ZR 77-xx) is **not** this situation; the C2-2 overlay edge as a "district boundary" is unresolved (library HX2) — kept unresolved.

**Worked values**

| # | Item | Value | Unit | Basis | ZR § | State | Key conditions |
|---|---|---|---|---|---|---|---|
| O1a | Option 1 max residential FA | 20,150 | sq ft | recorded area × FAR 2.00 | 23-22 | applies | zoning lot = lot 70 alone |
| O1b | Option 1 max dwelling units | 29 | DU | 20,150 ÷ 680, frac 0.63<0.75 drop | 23-52 | applies | standard residences |
| O1c | Heights (std) | 30 / 45 / 55 | ft | R6B row, no footnote | 23-432 | applies | base plane not known |
| A1 | **A** total FA (both buildings, **shared**) | 20,150 | sq ft | whole zoning lot, no per-building budget | 23-22 | applies | **gain over one building = 0** |
| A2 | **A** total units (shared) | 29 | DU | one 23-52 budget | 23-52 | applies | **gain = 0** |
| A3 | Distance between unconnected buildings (<125 ft) | 40 | ft | — | 23-371 | applies | **NOT CAPTURED** (library read live) |
| A4 | Legally-required window to wall/lot line | 20 | ft | — | 23-372 | applies | **NOT CAPTURED** |
| A5 | Court minima (if a court is formed) | inner ≥800 & ≥20; outer width ≥ depth | sq ft / ft | — | 23-35/-352/-353 | conditional (design) | **NOT CAPTURED** |
| A6 | Open area along side lot line | ≥5 | ft | — | 23-335(b) | applies | no side yard required |
| A7 | Combined cap if residential+commercial | greatest single use = 2.00 FAR | — | C2-2 Col A = 2.00 = R6B resid. | 35-01/35-31; 33-121 | applies | = same 20,150 |
| B0 | **B** subdivision | legal/recording act, not a zoning grant | — | ACRIS/title/survey | 12-10 "zoning lot" | fact owner must take+record | program cannot assume it |
| B1 | **B** FA per resulting lot (equal halves 5,037.5 sq ft) | 10,075 each; 20,150 total | sq ft | recorded area × 2.00 | 23-22 | applies | **gain vs O1 = 0** |
| B2 | **B** units per lot (680, per-lot fraction) | 15 each; **30 total** | DU | 10,075 ÷ 680 = 14.82, 0.82≥0.75 up | 23-52 | applies but **legality not sure** | +1 vs O1 = rounding artifact |
| B3 | Heights each lot | 30 / 45 / 55 | ft | R6B | 23-432 | applies | — |
| B4 | Corner-half max coverage | 100 | % | within 100 ft of both street lines | 23-362(a)+12-10 | conditional (geometry) | diagonal ≈112 ft → part beyond corner |
| B5 | Interior-half max coverage | 80 | % | interior lot | 23-362(a) | applies | **cost**; 23-363 may raise, not shown |
| B6 | Interior-half rear yard | 20 (≤75 ft) / 30 (>75 ft) | ft | depth ~100≥95, no shallow cut | 23-342 | applies | **new cost** vs undivided |
| B7 | Corner-half rear yard | none within 100 ft of corner; beyond | — | — | 23-344(a)/-342 | partial / not_known | adjoining lot-line kinds unknown |
| B8 | New division line | side lot line both lots; open area ≥5 ft | ft | — | 23-335(b)/34-232 | applies | no side yard required |
| B9 | Min lot area / width per half | ≥1,700 sq ft / ≥18 ft (mult. dwg); 2,375/25 (detached) | — | each half ≈5,037 sq ft / ≈50 ft | 23-12 | **not binding** | **NOT CAPTURED** (read live, below) |

For both A and B a modest scheme (3 storeys, ~30 ft = the minimum base height) is permitted and needs no setback (≤45 ft max base); no captured provision sets a minimum height or storey count (step-p6).

**Arithmetic** — 2.00 × 10,075 = 20,150. 20,150 ÷ 680 = 29.63 → 29 (0.63 dropped). Equal-half split 10,075 ÷ 2 = 5,037.5; 2.00 × 5,037.5 = 10,075 each; 10,075 ÷ 680 = 14.82 → 15 each (0.82 ≥ 0.75); 15 + 15 = 30; 30 − 29 = **+1 unit**. Corner-half corner-point diagonal √(50.38² + 100²) ≈ 112 ft > 100 ft.

**Which gains are real.** Floor area: **no gain** either way (20,150 in O1, A and B alike — FAR is on area, which the split preserves). Units: **A gains nothing** (one shared 23-52 budget). **B shows +1 unit (30 vs 29) purely from applying the fraction rule per lot** — a rounding artifact; whether two zoning lots may lawfully yield more total units than one, or whether that double-counts density, is a legal reading the library marks **not sure**. Costs of the split: the interior half drops from the corner lot's up-to-100% to 80% coverage (B5) and gains a required rear yard (B6); two 5-ft open strips along the new side line (B8); and the legal/recording burden of subdivision (B0). A adds spacing/court constraints (A3–A5) that can only reduce buildable area. **Net: at most one extra, legally-doubtful unit, bought with coverage loss, a new rear yard, and a subdivision.**

**ZR 23-12 (read live, uncaptured).** "Lot Area and Lot Width Regulations in R6 through R12 Districts," Last Amended 12/5/2024, https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-12 — "no residence shall be permitted on a zoning lot with a total lot area or lot width less than": single/two-family detached or zero-lot-line R6–R12 = **2,375 sq ft / 25 ft**; other residences R6–R12 = **1,700 sq ft / 18 ft**. Each half far exceeds both, so the minimum is not binding. Not in `zr-snapshots/v1`.

**Not known (exact missing item → where found).** (1) Zoning-lot identity — the 2022 CERT 2022020201551001, ZONE 2022020201551002, DECL 2022031600431001 (CRFNs in NB-01) and the 2016 CERT/ZONE 2016081000837001/002, with exhibits, plus a title/zoning-lot review. Until read, both A and B may be framed on the wrong parcel. (2) Lot-area basis (10,075 vs 10,387.99, ~3%) — the 2017 Buckley survey (DOF txn 76338) / 2018 deed 2018013000919001 Schedule A / certified street-line record (NB-04). (3) Division geometry — the owner's recorded subdivision metes-and-bounds + survey; I assumed equal, perpendicular-to-Northern-Boulevard halves. (4) Coverage partition and rear yard beyond the corner — adjoining zoning lots' lot-line kinds, from their zoning-lot descriptions / survey. (5) Street-wall position (35-631(b), 70% within 8 ft) — a prevailing-street-wall adjacency survey (NB-06).

**Conflicts.** (a) DOB NB 440608941 `proposed_zoning_sqft` = 39,934 and A1-lot-1 `proposed` = 39,772, job text "ONE (1) ZONING LOT AND (2) TAX LOTS (LOT #1 & #70)" (NB-02) — far above lot-70-alone's 20,150 at FAR 2.00; a strong signal the real zoning lot is lots 1+70 (larger area) and/or a non-standard FAR programme. Kept unresolved (NB-01/02). (b) Captures vs library: 23-371, 23-372, 23-35x, 23-12 and the 77-xx chapter are read live by library helpers but are **not** snapshot-pinned — load-bearing for A and B. (c) Settled cases compute no two-lot split; `interior-lots.json` confirms per-lot 680 rounding (14/15/16 for made-up lots), consistent with my 15-per-half; the library's "not sure" on the aggregate-unit gain governs.

**Sections a capture task should add.** 23-371, 23-372 (distance between buildings / window-to-lot-line); 23-35, 23-351, 23-352, 23-353 (court regulations) — for A. 23-12 (minimum lot area/width R6–R12) — for B. If Reading B (district boundary) is ever offered: Article VII Chapter 7 (77-01, 77-11, 77-12, 77-21/-211, 77-22, 77-24, 77-25, 77-26, 77-27, 77-28). The 12-10 "zoning lot" subdivision clause is already captured (`zr-12-10-zoning-lot`).

**Could not check:** the recorded instruments (NB-01, access-blocked), the survey/deed (NB-04), the actual division line, neighbours' lot lines, and the mapped overlay/street-line positions — none is in the sealed materials; each is named above with its source.

END-OF-REPORT