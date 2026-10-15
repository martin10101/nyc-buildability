# Independent reading for M5-T185 (option 8 (two buildings on one lot / a divided lot - both meanings), reading B) (provenance)

M5-T185 PROVENANCE -29 (OPTION 8, READING B)

What this is: an independent worked reading made on 2026-10-15 by an AI helper that took no part in writing the program's rules. METHOD, stated exactly: the reader had READ access to a detached, read-only checkout of this repository at commit bb5c02b9 (the law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library), was told not to read any program output (no test run, no API call, no report print and no benchmark fixture value), and, for sections that were not among the captures at the time it read, it cross-checked the official Zoning Resolution page (zoningresolution.planning.nyc.gov) live. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names that pinned, read-only set of captures and settled cases in the detached checkout at bb5c02b9 - it was NOT a sealed folder in the step-P7/P8 sense, and because some official pages were read live this was NOT an offline reading and does not assert the reader was sealed off from every outside source. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies, is buildable, is optimal or is feasible. It is reproduced below unchanged, byte for byte. (Several sections the reading marked uncaptured when it was made - for example 23-51, 23-12, 23-371, 32-421, 33-26, 33-301, 22-12/22-121/22-122, 32-121, 54-311 - were captured afterwards by task M3-T010 and are now present in docs/research/zr-snapshots/v1; the reference case records a value only where both readings of the option agree on the same value and the same basis.)

---

I now have comprehensive grounding from the captured law and the settled reference cases. Here is my independent worked reading.

---

**OPTION 8 — "A split lot with two buildings" — 215-16 Northern Boulevard (Queens; block 7334, lot 70; R6B + C2-2; corner of Northern Boulevard (wide) and 215th Place (narrow)). Reader B, independent/sealed.**

**Label (ADR-007):** this is an unreviewed AI draft from the law text and the settled facts; it decides no eligibility, use permission or legal step. Every figure uses the **recorded** lot area **10,075 sq ft** (NB-04); the GIS outline 10,387.99 sq ft is a drawing measure only and is never used. **Standing condition (NB-01):** the zoning lot is *unconfirmed* — the ACRIS index puts a ZONING-LOT-DESCRIPTION against **both** lot 1 and lot 70, so "lot 70 alone" (Z1) is an assumption, not a fact; if 1+70 are one zoning lot, lot 1 already carries a building and every figure below shifts.

"Split lot" has two legal meanings; I worked both. (A third — a lot crossed by a *zoning-district* boundary, ZR Art. VII Ch. 7 — is **not** either meaning here and stays unresolved; see end.)

## Worked values (recorded-area basis)

| # | Item | Value | Unit | Basis | ZR section | State | Key condition |
|---|---|---|---|---|---|---|---|
| **Option 1 (one building, reference)** |
|1|Max residential FA|20,150|sq ft|2.00×10,075|23-22 (R6B=2.0)|applies|R6B row carries no wide-street footnote|
|2|Max dwelling units|29|units|20,150/680=29.63, frac 0.63<0.75→drop|23-52(b)|applies|not a special density area (NB-05)|
|3|Heights|30/45/55|ft|table|23-432 R6B|applies|min base/max base/max bldg|
| **Meaning A — two buildings on the ONE undivided zoning lot (shared budget)** |
|A1|Max FA (whole lot, shared)|20,150|sq ft|2.00×10,075|23-22|applies|**no per-building FA budget**|
|A2|Max units (whole lot, shared)|29|units|20,150/680→29|23-52(b)|applies|**one shared count, not per building**|
|A3|Min distance between 2 unconnected bldgs (<125 ft)|40|ft|law|23-371 (not captured; fetched, amd 12/5/2024)|applies_if two separate bldgs|measured between closest points|
|A4|Window-to-wall / courts|20 ft / court mins|ft|law|23-372; 23-35/-352/-353 (not captured)|not_known|needs footprints/heights|
|A5|Mixed res+commercial, 2 bldgs on 1 lot|Ch.5 bulk|—|law|35-01 (captured)|applies_if commercial present|C2-2 overlay use|
|A6|Gain over one building|none (FA, units)|—|—|23-22, 23-52|applies|no extra rounding on a shared budget|
| **Meaning B — subdivide the ONE zoning lot into TWO zoning lots (~half each)** |
|B0|Legal act to divide|recorded subdivision|—|law|12-10 "zoning lot"|applies|recorded metes-and-bounds; single-fee/party-in-interest; **all resulting lots + buildings must comply with ALL provisions**|
|B1|FA per half|10,075|sq ft|2.00×5,037.5|23-22|applies|equal split assumed|
|B2|Units per half|15|units|10,075/680=14.816, frac 0.816≥0.75→up|23-52(b)|applies|fraction rule applied **per lot**|
|B3|Units total|30|units|15+15|23-52(b)|conditional|**+1 vs option 1; "not sure" it is lawful (double-counts density?)**|
|B4|FA total|20,150|sq ft|10,075+10,075|23-22|applies|**same as option 1 (FAR is linear)**|
|B5|Heights per half|30/45/55|ft|table|23-432|applies|unchanged|
|B6|Coverage per half|100% corner-portion / 80% interior|%|law|23-362(a)+12-10 corner|applies|corner benefit only on the piece holding the corner|
|B7|Rear yard per half|20 or 30 ft, unless waived|ft|law|23-342; 23-344(a)/(b)/(c)|not_known|new interior line may be a **rear lot line**; non-corner piece loses the 23-344(a) corner waiver|
|B8|Min lot area / lot width per half|—|—|—|min-lot-area section (not captured)|not_known|each half ~50 ft wide / ~5,037.5 sq ft|

## Arithmetic
- Option 1: 2.00×10,075 = **20,150**; 20,150/680 = **29.63…**, 0.63<0.75 → **29** (matches real-lot L1/L6).
- A (shared): identical to option 1 — one budget, so **no rounding gain**.
- B (equal halves, recorded): 10,075/2 = 5,037.5 sq ft; FA 2.00×5,037.5 = **10,075** each (total 20,150); 10,075/680 = **14.816…**, 0.816≥0.75 → **15** each → **30** total. The +1 is the *maximum* obtainable: total 29.63 can be pushed to at most 30 across two roundings (each lot can "gain" at most 0.25), never to 31.

## Which gains are real
- **Floor area: no gain** either way — FAR is linear; total stays 20,150 sq ft.
- **Heights, FAR, coverage maxima: no gain** — the same district numbers apply per lot/per building.
- **Meaning A: no unit gain** — a single shared 23-52 budget gives 29, same as one building. A only adds *costs* (23-371 40-ft separation; 23-372/court rules), reducing usable footprint.
- **Meaning B: a +1 unit rounding gain (30 vs 29) is arithmetically real but legally uncertain and not free.** It requires a lawfully recorded subdivision (12-10) in which **each** resulting zoning lot and its building independently comply with *all* provisions. It is offset on at least one half by (i) loss of the corner-lot 100% coverage and the 23-344(a) corner rear-yard waiver, (ii) a possible rear yard on the new interior lot line (23-342 → 20/30 ft), and (iii) an unverified minimum lot area/width. The library's own reading says it is **"not sure"** whether two zoning lots may lawfully claim more total density than one.

## Not known (exact missing item → where it would come from)
1. **Is lot 70 alone the zoning lot?** (NB-01, access_blocked) → recorded 2022 CERT/ZONE/DECL contents + a title/zoning-lot review. Governs *everything*.
2. **Minimum lot area / lot width for R6B residences** → the current ZR minimum-lot-area/width section (not captured; ZR 23-32 is now "Front Yard Requirements", so the old number is gone). Decides whether a ~50-ft-wide half is even a legal zoning lot.
3. **Rear yard on each resulting lot / the new interior line** → the adjoining zoning lot's lot-line kind (survey/deed/neighbour records) and the operative street line (survey/approved ZD1); 23-344(c)(3) vs (c)(1) (NB-03).
4. **Lot-70 depth vs the 100-ft reach** → survey (Buckley 2017-02-21) or approved ZD1; 100 (tax-map) / 99.97 (GIS) / ~101.06 (derived) straddle the 100-ft line (NB-03 gap a).
5. **Distance/court detail for Meaning A** → building footprints and heights (design inputs); 23-371/23-372/23-35 bodies.

## Conflicts (captures / settled cases / library)
- **Library vs task labels:** the library calls "two buildings on one zoning lot" **A.2** and "subdivide into two zoning lots" **A.1**; the task's meaning (A) = library A.2 and meaning (B) = library A.1. Same substance, swapped letters.
- **Library staleness on captures:** option-08 marks 35-01 captured but 23-371/23-372/23-35/77-xx **NOT CAPTURED** — I confirmed from `docs/research/zr-snapshots/v1/` that those are still absent (verified today); 23-371 I fetched live. No conflict in substance.
- **Lot-area basis:** recorded 10,075 vs tax-rectangle 10,076 vs GIS 10,387.99 (NB-04, placement-building-b) — I used recorded only; unresolved by ~313 sq ft.
- **C2-2 overlay as a "district boundary" (library Reading B):** not settled by the text — two readings; likely moot (76-131 default 150-ft overlay depth > ~100-ft lot depth) but the mapped line was not read. Stays unresolved.

## Sections a capture task should add
- **Minimum lot area / minimum lot width for residences** (current R6-R12 section) — load-bearing for Meaning B; currently uncaptured.
- **23-371** (distance between buildings) and **23-372** + **23-35/-351/-352/-353** (courts) — for Meaning A.
- **Art. VII Ch. 7: 77-11/77-12/77-22/77-24/77-25/77-26/77-27/77-28** — only if the overlay-edge/district-boundary meaning is ever offered.

**Assumptions stated:** Z1 (lot 70 alone) is assumed, not confirmed; an equal subdivision is assumed for B1-B4; all figures are R6B residential-only; nothing here is a DOB determination, and no result is called compliant, buildable or feasible.

END-OF-REPORT