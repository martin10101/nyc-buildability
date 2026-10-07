# Independent hand-calculation, first round (provenance)

What this is: the first return from an AI helper that took no part in writing the program's rules. It was made on 2026-10-06 under one hard rule: work only from a sealed folder of pinned law-text captures and the lot's recorded official facts, with no access to the program or this repository. It is a draft reading of the law, not professionally reviewed and not a statement that anything complies. It is reproduced below unchanged; it is the origin of the expected values in the real-lot, interior-lots and corner-reach cases.

---

INDEPENDENT BLIND HAND-CALCULATION — 215-16 Northern Boulevard, Queens, BBL 4073340070. District R6B with a C2-2 commercial overlay (facts/lot_facts_pluto.json). Legend: [F]=sourced fact, [C]=calculation, [?]=NOT KNOWN from captured text. This is a DRAFT reading from law text, NOT legal advice and NOT a professionally-reviewed compliance determination. I obeyed the hard rule: nothing under /root/project was read or written (my scratch is under scratchpad/work-order/blind-calc/; I did not write agent-memory because its path is under /root/project).

== TASK 1 ==

a. LOT TYPE = CORNER LOT.
[F] Outline ring (facts/lot_outline_epsg2263.json, EPSG:2263 US survey feet) has 5 vertices P0..P4. Edge lengths (Euclidean between consecutive vertices):
 P0→P1 99.98 | P1→P2 103.88 | P2→P3 99.98 | P3→P4 101.71 | P4→P0 2.22. Shoelace area 10,387.99 sf (= MapPLUTO Shape__Area). 
[C] Half-width adjacency test (edge-midpoint distance to each recorded DCM centerline vs ½ mapped width):
 - P1→P2 is 51.1 ft from Northern Blvd centerline (½×100=50) → FRONTAGE on Northern Boulevard.
 - P2→P3 is 28.9 ft from the "215 Place" centerline OBJECTID 11453 (½×60=30) → FRONTAGE on the 60-ft cross street.
 - P0→P1 (west) and P3→P4 (south) are >79 ft from every centerline → interior/rear lot lines, not streets.
[C] The two frontage street lines meet at lot corner P2; interior angle there = 89.7°.
[Web def, ZR 12-10 "lot, corner"] "...a zoning lot which adjoins the point of intersection of two or more streets and in which the interior angle formed by the extensions of the street lines ... forms an angle of 135 degrees or less." 89.7° ≤ 135° → corner lot confirmed. (Interior lot = "neither a corner lot nor a through lot"; through lot needs two opposite ~parallel streets — not our case.)
[F] PLUTO lottype="3" but its meaning is NOT in the packet, so not relied on.
Two frontages (to 0.1 ft, from the outline): Northern Boulevard = 103.9 ft (edge P1→P2); cross street "215 Place" = 100.0 ft (edge P2→P3). [F] PLUTO records lotfront 100.76 / lotdepth 100.00; the ~3-ft gap vs my 103.9 is a tax-lot-vs-GIS difference — flagged.

b. WIDE/NARROW (ZR 12-10, packet: "A 'wide street' is any street 75 feet or more in width"; "A 'narrow street' is any street less than 75 feet wide"; amended 3/26/2026).
[F] Northern Boulevard mapped Streetwidth = 100 → ≥75 → WIDE. [F] Cross street mapped Streetwidth = 60 → <75 → NARROW.
DOES IT MATTER FOR R6B? Only for the setback depth in 23-433 (10 ft wide / 15 ft narrow). The R6B rows of the FAR table (23-22) and the height table (23-432) carry NO footnote, so wide-vs-narrow does NOT change FAR, min/max base height, or max building height in R6B.

c. RESIDENTIAL FAR & FLOOR AREA (ZR 23-22, R6B row: standard 2.00, qualifying affordable/senior 2.40; no footnote — live-site confirmed today).
Lot area used = 10,075 sf = [F] PLUTO lotarea (the explicitly labeled lot-area field, units sf per the data dictionary). Alternate = 10,388 sf (MapPLUTO polygon / my shoelace); the ZR "lot area" definition is [?] not in the packet, so I show both.
[C] Standard: 2.00 × 10,075 = 20,150 sf (alt 2.00×10,388 = 20,776 sf).
[C] Qualifying affordable/senior: 2.40 × 10,075 = 24,180 sf (alt = 24,931 sf).
[?] C2-2 overlay: no overlay text in packet; whether/how it alters residential FAR is NOT KNOWN from captured text (residential-district rules used; commercial rules not computed).

d. HEIGHT (ZR 23-432, R6B row; no footnote — live-site confirmed today):
 Min base height 30 ft. Standard: max base 45 ft, max building 55 ft. Qualifying affordable/senior: max base 45 ft, max building 65 ft.
 Setback above base (23-432 + 23-433): between the min base (30 ft) and max base (45 ft), provide a setback ≥10 ft deep from any street wall on a WIDE street (Northern Blvd) and ≥15 ft deep from any street wall on a NARROW street (215 Place); reducible 1 ft per ft the wall is set behind the street line but never below 7 ft (23-433(a)); optional where a wall is >50 ft from a street line or meets the 65° angle test (23-433(c)).
 [?] The base-plane the heights are measured from for R6-R12 is not in the packet (captured 23-42 is R1-R5 only).

e. MAX LOT COVERAGE (ZR 23-362(a); live-site confirmed): corner lot → 100%. (Interior/through → 80%.)
 [F/Web] Nuance: ZR 12-10 limits the corner-lot regulation to "that portion bounded by the intersecting street line and lines parallel to and 100 feet from each intersecting street line." This lot is ~100 ft deep perpendicular to Northern Blvd and ~104 ft wide, so essentially all of it is within 100 ft of each street line; only a ~4-ft far-west sliver falls under the 80% interior-lot rule. [?] exact partition not computed to sf.

f. REAR YARD. [F] ZR 23-344(a): "no rear yard shall be required within 100 feet of the point of intersection of two street lines intersecting at an angle of 135 degrees or less." The two street lines meet at ~89.7° (≤135°) → within 100 ft of corner P2, NO rear yard required. [C] But vertices P0 (144.6 ft) and P4 (143.0 ft) lie BEYOND 100 ft from P2, so the far-SW portion is not covered by 23-344(a); 23-344(c)(3) may waive it (R6: no rear yard where a >100-ft side lot line meets a neighbor's side lot line) but that needs neighbor data.
 GENERAL rear-yard depth: [?] NOT KNOWN from captured text — ZR 23-342 is NOT in the packet. (For reference only, the live 23-342 page today reads "not less than 20 feet"; this is WEB-read, not packet, and not used in the numbers above.)

g. MAX DWELLING UNITS (ZR 23-52; live-site confirmed): divisor = dwelling-unit factor 680 (para (b)); formula = max residential floor area ÷ 680; rounding = "Fractions equal to or greater than three-quarters ... shall be considered to be one dwelling unit" (≥0.75 rounds up, else down).
[C] Standard (20,150 sf): 20,150/680 = 29.63 → frac 0.63 <0.75 → 29 DU (alt 20,776/680 = 30.55 → 30).
[C] Qualifying AFFORDABLE (24,180 sf): 24,180/680 = 35.56 → 35 DU (alt 24,931/680 = 36.66 → 36). Affordable housing is NOT in the 23-52(a) no-factor list, so 680 applies.
[?] Qualifying SENIOR housing: 23-52(a)(2) gives "no applicable dwelling unit factor" → DU count NOT determined by this formula (not limited by the 680 divisor).

== TASK 2 == (R6B, no overlay, standard residences; FAR 2.00; factor 680; ≥0.75 rounds up)

| Probe | Lot | Max FA = 2.00×A | Lot coverage (23-362) | FA/680 | DU |
|---|---|---|---|---|---|
| P1 interior 50×100, 5,000 sf, 60-ft st | 5,000 | 10,000 sf | 80% → 4,000 sf | 14.7059 (frac .706) | 14 |
| P2 corner 4,000 sf | 4,000 | 8,000 sf | 100% → 4,000 sf | 11.7647 (frac .7647 ≥.75) | 12 (rounds UP) |
| P3 (frac just BELOW .75) 5,350 sf | 5,350 | 10,700 sf | (interior 80%) | 15.7353 (frac .735) | 15 |
| P4 (frac AT/ABOVE .75) 5,360 sf | 5,360 | (interior 80%) | — | 15.7647 (frac .7647) | 16 |

P3/P4 show the threshold: 10,700/680 = 15.735 → 15 DU; 10,720/680 = 15.765 → 16 DU. (A=5,355 sf gives exactly 15.7500 → 16, demonstrating the "equal to" clause.) 60-ft street in P1 is narrow but R6B FAR is 2.00 regardless.
 - Does FAR or height depend on wide vs narrow street per the captured table/footnotes? NO for R6B — the R6B rows in 23-22 and 23-432 carry no footnote (the "within 100 ft of a wide street" footnotes apply to R6A/R6 etc., not R6B).
 - Different rule for qualifying housing? YES — 23-22 FAR 2.40 vs 2.00; 23-432 max building height 65 vs 55 ft (same 45-ft max base, 30-ft min base); and 23-52(a)(2) exempts qualifying SENIOR housing from the 680 factor.

== TASK 3 — ambiguities / missing text (section needed) ==
1. Lot-type defs "lot, corner/interior/through" — not in packet (ZR 12-10); classified by geometry + web-read def.
2. "zoning lot" def — not in packet (ZR 12-10); can't confirm tax lot 70 = the whole zoning lot / no merger.
3. "lot area" def — not in packet (ZR 12-10); PLUTO 10,075 vs polygon 10,388 (~3%) unresolved.
4. General rear-yard depth — ZR 23-342 absent from packet; baseline depth NOT KNOWN from captured text.
5. C2-2 commercial overlay — no overlay/Article-III text in packet (e.g. 33-xx, 32-xx); residential-FAR/use/parking/ground-floor effects unknown.
6. "front/side/rear lot line" and "street line" defs — not in packet (needed for 23-344 and frontage).
7. "floor area"/"residential floor area" def — not in packet (ZR 12-10); what counts toward FAR unknown.
8. "lot coverage" def — not in packet (ZR 12-10).
9. "qualifying affordable housing" / "qualifying senior housing" / "UAP developments" / "Mandatory Inclusionary Housing areas" defs & eligibility — referenced but not defined in packet; needed to use the 2.40 column, the 65-ft height, and the senior DU-factor exemption.
10. Base-plane/height-measurement rule for R6-R12 — not in packet (captured 23-42 is R1-R5).
11. "prevailing street wall frontage" (23-431) — undefined in packet; governs street-wall line-up vs percentage rule.
12. 23-413 (dormers / permitted obstructions) referenced by 23-433(d)/23-431 — not in packet.
13. 23-434 "eligible sites" (the 65%/50% lot-coverage branch) referenced by 23-362(b) — not in packet.
14. Exact 100-ft corner-lot-portion partition (coverage 100% vs 80%) and the 23-344(c) rear-lot-line adjacency — need neighbor geometry + 23-342.

== WEB PAGES READ (official only; 2026-10-06) ==
- https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22 — R6B FAR 2.00/2.40, no footnote: MATCHES packet.
- https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432 — R6B height 30/45/55/45/65, no footnote: MATCHES packet.
- https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362 — lot coverage interior/through 80%, corner 100%: MATCHES packet.
- https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52 — DU factor 680 + "equal to or greater than three-quarters": MATCHES packet.
- https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342 — rear-yard depth 20 ft: NOT in packet (packet lacks 23-342); web-read only, not used in numbers.
- https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 and zr.planning.nyc.gov/article-i/chapter-2/12-10 — lot-type definitions (corner/interior/through): packet's 12-10 capture holds ONLY wide/narrow street, so these defs are NEW (packet gap filled); wide/narrow wording in packet is consistent with the live page.

END-OF-REPORT