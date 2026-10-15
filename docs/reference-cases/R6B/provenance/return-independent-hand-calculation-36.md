# Independent reading for M5-T186 (option 11 (all programs combined), reading B) (provenance)

M5-T186 PROVENANCE -36 (OPTION 11, READING B)

What this is: an independent worked reading made on 2026-10-15 by a second AI helper that took no part in writing the program's rules. METHOD, stated exactly: the reader worked from the primary snapshots, the settled worked cases and the two draft-reading records, and listed the v1 snapshot folder itself to confirm which sections were among the captures; it read no program output. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names the pinned, read-only set of law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library that the reader worked from - it was not a sealed folder in the step-P7/P8 sense, and the header does not assert the reader was cut off from every outside source. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies, is buildable, is optimal or is feasible. It is reproduced below unchanged, byte for byte.

---

I have all primary sources, the settled worked cases, and the two draft-reading records. Writing my sealed reader-B return.

---

**SEALED WORKED-EXAMPLE READER-B — OPTION 11 "ALL PROGRAMS COMBINED"**
215-16 Northern Boulevard, Queens (block 7334, lot 70); R6B + C2-2 overlay; corner (Northern Blvd wide / 215th Place narrow).

This is an AI agent's unreviewed draft (ADR-007), not a professional determination. It decides no eligibility or use permission an agency must grant. Standing assumptions I do not decide: (i) the **zoning lot is unconfirmed (NB-01)** — every figure assumes lot 70 alone is the zoning lot; if the recorded 2022 ZONE joins lots 1+70 (~20,000 sq ft), areas roughly double but lot 1's existing floor area counts; (ii) **affordable/senior/UAP/CF eligibility** are legal determinations (HPD/NYS DOH); (iii) owner questions **N1 (what option 8 means)** and **N2 (shared housing)** stay open.

**Basis for every figure:** recorded lot area **10,075 sq ft** (NB-04, administrative_record); never the GIS outline 10,387.99 (display only). FAR = total floor area ÷ zoning-lot area (ZR 12-10).

**WORKED-VALUE TABLE**

| # | Item | Value | Unit | Basis | ZR section/clause | State | Conditions that change it |
|---|---|---|---|---|---|---|---|
|1|Combination ceiling (standard uses)|2.00|FAR|greatest single-use of residential 2.00, commercial 2.00, CF 2.00|35-31 "total of all FARs ≤ greatest FAR for any single use"; 23-20 same words|applies|"except where explicitly stated otherwise" carve-out sweep not finished; 35-32/35-33 don't reach R6B|
|2|Max total FA (standard mix)|20,150|sq ft|2.00 × 10,075|35-31; 12-10 FAR|applies|lot area; zoning lot (NB-01)|
|3|Combination ceiling (residential qualifies)|2.40|FAR|greatest single-use = residential qualifying 2.40 (> commercial/CF 2.00)|35-31; 23-22 2nd column (R6B 2.40)|applies|residential must be qualifying affordable or senior (eligibility)|
|4|Max total FA (qualifying mix)|24,180|sq ft|2.40 × 10,075|35-31; 23-22|applies|eligibility; carve-out sweep|
|5|Residential max FAR (standard)|2.00|FAR|R6B standard row, no wide-street footnote|23-22; 34-221/35-22 route|applies|—|
|6|Commercial overlay FAR|2.00|FAR|C2-2→R6B row (R5D R6B): Col A 2.00, Col C 2.00|33-121|applies|33-121(a): commercial portion ≤ Col A|
|7|Community-facility FAR|2.00|FAR|R6B contextual row|24-11 (coverage 80 corner/60 interior)|applies|24-162/24-111 don't change R6B figure|
|8|Shared-FA attribution|proportional; base = total FA **less** shared|—|per-use % of total FA less shared|35-31; 23-20|applies|design split of uses|
|9|Units (standard all-residential)|29|DU|20,150 ÷ 680 = 29.63 (0.63<0.75)|23-52(b); NB-05 not special-density|applies|falls as non-residential takes share|
|10|Units (qualifying affordable all-resi)|35|DU|24,180 ÷ 680 = 35.56 (0.56<0.75)|23-52(b)|applies|falls as non-residential grows|
|11|Units (qualifying senior)|no 23-52 limit|DU|no DU factor|23-52(a)(2)|applies|another provision may cap — not found (not_known)|
|12|Combined-building height row|R6B row of 23-432: 30/45/55 (std) or 45/65 (qualifying)|ft|R6B residential-equivalent row; no mixed-use row exists|23-432 via 35-63→35-631/35-632; residential-only via 34-11/34-24(b)(1)/35-63 (NB-06 draft)|not_known (draft)|row turns on whether **residential** qualifies, not on the commercial/CF use; mixed-building street-wall path not rule-backed, NB-06 awaiting review|

**WHICH PROGRAMS MAY COMBINE** (combine = allowed on one zoning lot / mixed building under the single 35-31 cap; not that the program computes it)

| Pair / set | May combine? | Clause |
|---|---|---|
|Affordable (2) + commercial (5)|MAY, one mixed building|35-31 shared cap; use 32-161 (UG VI) in C2-2; commercial FAR 33-121|
|Senior (3) + commercial (5)|MAY|same; senior adds 23-52(a)(2) no-factor|
|Residential + community facility (6)|MAY|35-31; CF use UG III (22-13 / 32-131); 24-11; 35-33 & 24-162 **exclude R6B** (suffix) → plain greatest-single-use|
|Residential + commercial + CF|MAY|35-31; 33-121(c) Col C 2.00, with 33-121(a) capping commercial to Col A|
|Affordable (2) **vs** Senior (3)|NOT SURE whether one development holds both|both route to the same 23-22 2nd column (2.40) / 23-432 qualifying column — no stacking benefit either way; no ZR text read barring or allowing; program treats them mutually exclusive|
|Two buildings, one zoning lot (8, reading A.2)|MAY|35-01 applies Chapter-5 bulk across the zoning lot; normal R6B per building. Subdivide (A.1) and district-boundary split (B, Art. VII Ch.7 / 77-00, **not captured**) unsettled — **N1 open**|
|Shared housing (9)|NOT SURE|rooming-unit use 22-12/22-121/32-121; 23-51 takes rooming units **out of** the 23-52 density cap; modern framework pending 2027 — **N2 open**|
|Parking waiver (10)|MAY, with any|orthogonal to FAR; Outer Transit Zone 25-221/25-222; sets no housing_program|

**THE COMBINATION MECHANIC (the core reading).** 35-31 (and 23-20 in the same words) gives each use its own max FAR but caps their **total at the greatest FAR permitted for any single use on the zoning lot** — uses **share one envelope, they do not stack** (two independent settled readers agree, step-p5#mixed-use-floor-area-combination). For R6B/C2-2 the single-use FARs are residential 2.00 (23-22), commercial 2.00 (33-121), CF 2.00 (24-11). So the standard combined ceiling is **2.00** → **20,150 sq ft**, the *same* envelope as option 1; adding shops or a CF does not add floor area, it trades against residential 1:1. The ceiling rises to **2.40 → 24,180 sq ft** only if the **residential** use qualifies as affordable or senior; commercial/CF still share that one 2.40 ceiling. Shared floor area (lobbies, corridors) is attributed per use by its % of total FA **less** the shared portion (35-31; worked settled example: 400 sq ft shared → commercial 83.58 / residential 316.42).

**SPLIT BY USE (recorded 10,075 basis).** Any allowed mix fits one envelope: standard **R + C + CF ≤ 20,150 sq ft total**, with C ≤ 2.00×10,075 and CF ≤ 2.00×10,075 individually but their **sum** capped at 20,150; qualifying-residential mix **≤ 24,180 sq ft total**. Units = residential share ÷ 680, so the all-residential case is the ceiling (29 std / 35 qualifying affordable) and falls as C/CF grow (settled opt6-dwelling-units: ≤29, depends on split).

**HEIGHTS WHEN USES MIX.** There is no separate mixed-use height row. The governing row is the **R6B row of 23-432**, reached for the overlay via 35-63→35-631/35-632 (R6–R12 equivalency) and for a residential-only building via 34-11/34-24(b)(1)/35-63 — both reach 35-631(b) (NB-06 draft, awaiting review). The column (standard 30/45/55 vs qualifying 45/65) turns only on whether the **residential** use qualifies. No setback is triggered at/below the 45 ft max base height; the wide/narrow class sets only setback depth above 45 ft (10 ft wide / 15 ft narrow).

**COMPARISON WITH OPTION 1** (settled: standard residences FAR 2.00 → 20,150 sq ft; heights 30/45/55; 29 units by the 680 factor). What option 11 **adds**: (a) use mix — shops (UG VI) and/or a community facility (UG III) inside the same 20,150 sq ft envelope; (b) where residential qualifies, +4,030 sq ft (20,150→24,180), +10 ft max building height (55→65), and up to +6 units (29→35 affordable; senior = no 23-52 cap); (c) a two-building layout on one zoning lot; (d) a transit-zone parking waiver. What it **costs**: every non-residential square foot comes **out of** the single shared ceiling (shops/CF reduce residential FA and units); the 2.40 bonus costs ≥4,030 sq ft of affordable floor area under a qualifying pathway; senior housing loses the per-unit DU cap but is occupancy-restricted. Option 11 does **not** stack multiple floor-area pools.

**WHAT STAYS NOT KNOWN (exact missing item → where found).**
1. **Zoning lot** (NB-01) — contents of the 2022 CERT/ZONE/DECL (CRFN 2022000059133/059134/121661) unread (ACRIS access_blocked); every area/FA/unit figure is conditional. → the recorded instruments + title review.
2. **24-11/24-111 now captured**, but **23-154 UAP text** and the **UAP income band** unread (HTTP 403). → ZR print/PDF node; HPD.
3. **35-31 "except where explicitly stated otherwise"** full carve-out sweep not done. → read 35-31 neighbours (35-34+).
4. **Mixed-building street-wall/height path** (35-631(b)/35-632→23-432/23-433) is a **draft reading awaiting review** (NB-06), and the exact street-wall position depends on an unresearched prevailing-street-wall-frontage fact and the operative street line (survey/ZD1).
5. **Affordable + senior together** — no ZR text read (no stacking benefit either way).
6. **Split-lot meaning (N1)** and **shared housing (N2)** — owner questions, not decided; Art. VII Ch.7 (77-00) **not captured**.
7. **Senior no-factor unit cap** — whether any other provision caps no-factor senior units: not found in captures.
8. **Commercial/CF lot coverage interaction, use selection, and which uses the owner intends** — design inputs not supplied; **rear yard beyond 100 ft of the corner** stays not_known (23-344(c), NB-03 draft).

**CONFLICTS between captures, settled cases and the library.**
- **Lot-area basis conflict (NB-04):** recorded 10,075 vs GIS 10,387.99 sq ft (~3.1%). I worked only on 10,075; the GIS value must never enter a zoning figure.
- **Library capture-state vs the folder:** option-11-combinations.md header rows mark 23-20/35-31 "NOT HANDLED" and once reported several sections "NOT CAPTURED"; I listed `zr-snapshots/v1/` myself and confirm 23-20, 33-121, 35-31, 35-32, 35-33, 24-11, 23-22, 23-432 are **all captured** (only 24-111/23-154 gaps noted there are stale — 24-11 is captured; 24-111 not read here). The library's own second-pass text already carries this correction; the first-pass flags remain wrong.
- **Library vs the law on "combination":** the library notes the owner's sample scenario 3 "all programs combined" reproduces only the UAP single-program sheet (pp.30-36), narrower than the 35-31 multi-use reading; whether option 11 should stack toward a stated objective is the owner product question (not law).
- **No contradiction** between the settled cases (step-p4/p5/p6, benchmark-options-2-3-6-7) and the primary snapshots on any figure I used: option-1 20,150/29/30-45-55, option-2/3 2.40→24,180 (35 affordable; senior no factor), option-6 combined cap 2.00→20,150 (≤29 units) all reproduce from the law text on the recorded 10,075 basis.

END-OF-REPORT
