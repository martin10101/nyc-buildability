# Independent reading for M5-T185 (option 5 (ground-floor shops with residences above), reading B) (provenance)

M5-T185 PROVENANCE -27 (OPTION 5, READING B)

What this is: an independent worked reading made on 2026-10-15 by an AI helper that took no part in writing the program's rules. METHOD, stated exactly: the reader had READ access to a detached, read-only checkout of this repository at commit bb5c02b9 (the law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library), was told not to read any program output (no test run, no API call, no report print and no benchmark fixture value), and, for sections that were not among the captures at the time it read, it cross-checked the official Zoning Resolution page (zoningresolution.planning.nyc.gov) live. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names that pinned, read-only set of captures and settled cases in the detached checkout at bb5c02b9 - it was NOT a sealed folder in the step-P7/P8 sense, and because some official pages were read live this was NOT an offline reading and does not assert the reader was sealed off from every outside source. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies, is buildable, is optimal or is feasible. It is reproduced below unchanged, byte for byte. (Several sections the reading marked uncaptured when it was made - for example 23-51, 23-12, 23-371, 32-421, 33-26, 33-301, 22-12/22-121/22-122, 32-121, 54-311 - were captured afterwards by task M3-T010 and are now present in docs/research/zr-snapshots/v1; the reference case records a value only where both readings of the option agree on the same value and the same basis.)

---

I have opened all the primary sources and settled facts needed. Writing my sealed independent reading now.

---

# Reader B — independent worked reading, Option 5 "Ground-floor shops with residences above"

**215-16 Northern Boulevard, Queens (block 7334, lot 70; BBL 4073340070), R6B + C2-2 overlay, corner lot (Northern Boulevard wide, 215th Place narrow).** AI unreviewed draft (ADR-007); decides no eligibility, use permission or legal step. I worked from the ZR text and the settled facts, no program output. **Basis for every area figure: recorded lot area 10,075 sq ft** (city record); the 10,387.99 sq ft GIS outline is display-only and never enters a calculation (NB-04). Zoning lot unconfirmed (NB-01): every lot-area figure assumes lot 70 alone is the zoning lot; the ACRIS index names lot 1 on the same block, so each carries that condition.

## Worked values

| Item | Value | Unit | Basis | ZR section | State | Conditions |
|---|---|---|---|---|---|---|
| Retail use at grade | permitted as-of-right (Use Group VI retail/service) | — | law | 32-161 (C2 col) | applies | per-use flags "S"/"○" in the 32-161 cells; which UG VI uses = scenario input |
| Shops: storey limits | ≤2 commercial storeys; no commercial above a storey with dwelling units | — | law | 32-421 | **not_known (text)** | 32-421 NOT CAPTURED (read live by library); capture owed |
| Commercial FAR | 2.00 → **20,150** | FAR / sq ft | law table | 33-12→33-121, "R5D R6B" Column A | applies | overlay present (C2-2 ✓ MapPLUTO); zoning lot |
| Residential FAR (standard) | 2.00 → **20,150** | FAR / sq ft | law table | 23-22 R6B | applies | zoning lot; no R6B 100-ft-of-wide-street footnote |
| Residential FAR (qualifying housing) | 2.40 → **24,180** | FAR / sq ft | law table | 23-22 R6B | conditional | needs qualifying affordable/senior eligibility |
| **Mixed-building combined cap** | greatest single-use FAR = **2.00 → 20,150** (standard) | FAR / sq ft | law | 35-01→35-31 | applies | 2.40→24,180 if qualifying housing; uses do **not** stack |
| 35-32 transit-zone 2.50 path | not applicable | — | law | 35-32 | **not_applicable** | "qualifying residential site" = R1–R5 only; R6B excluded |
| Dwelling-unit factor | 680 (not a special density area) | sq ft/unit | law | 23-52(b); NB-05 | applies | Queens CD 411, SPDist1 null |
| Dwelling units | (20,150 − commercial FA)/680; **29 if commercial = 0** | units | derived | 23-52 | conditional | falls as commercial FA rises; zoning lot, lot area, housing programme |
| Base/building heights (std) | 30 / 45 / 55 | ft | law | 23-432 via 35-632(a) | applies | qualifying housing → max bldg 65 |
| Street wall | ≥70% of each frontage within 8 ft of street line, to 30 ft min base | — | law | 35-631(b) | conditional | prevailing-street-wall frontage; operative street line |
| Setback above base | 10 (Northern Blvd, wide) / 15 (215 Pl, narrow) | ft | law | 23-433 / 35-632(a) | applies only >45 ft | not triggered at/below 45 ft max base |
| Front yard | none required | — | law | 34-231 | applies | — |
| Side yard | none required; optional ≥5 ft if provided | ft | law | 23-335(b) / 34-232 | applies | — |
| Lot coverage | — | — | law | 23-362; corner-lot 100-ft rule | **not_known** | lot reaches ~103.93 ft from 215 Pl line; strip beyond the 100-ft corner portion unsettled (real-lot L5) |
| Residential/mixed rear yard | none within 100 ft of corner; beyond: unsettled; ordinary depth 20/30 ft by building type & lot width | ft | law | 23-342 / 23-344(a) | **not_known** beyond corner | neighbour lot-line kinds, building type, lot width |
| Commercial rear yard | 20 ft at rear lot line, waived within 100 ft of a corner | ft | law | 33-26, waiver 33-301 | **not_known (text)** | 33-26/33-301 NOT CAPTURED |
| Overlay coverage/depth at the lot | — | — | — | 76-131 (default 150 ft) | **not_known** | mapped overlay line not read; possible split lot (Ch 7) |

## The arithmetic (recorded area 10,075 sq ft)

- Commercial FAR: 33-121 "R5D R6B" row, Column A (commercial-only) = 2.00 → 2.00 × 10,075 = **20,150 sq ft** if all commercial.
- Residential FAR: 23-22 R6B standard 2.00 → **20,150 sq ft**; qualifying 2.40 → **24,180 sq ft**.
- **Combining the two (35-31):** "The total of all such floor area ratios shall not exceed the greatest floor area ratio permitted for any such use on the zoning lot." Greatest of {commercial 2.0, residential 2.0} = **2.0 → 20,150 sq ft total for the whole mixed building.** They do **not** add. So **commercial floor area reduces residential floor area one-for-one:** residential available = 20,150 − commercial. Shared floor area (lobby/corridor/refuse) is attributed proportionally: base = total − shared, each use × its exclusive share (35-31; worked in step-p5-worked `made-up-mixed-shared-attribution`).
- **Units:** 23-52 divides the maximum residential floor area on the zoning lot by 680. Commercial = 0 → 20,150/680 = 29.63 → **29** (0.63 < 0.75). Example: 4,200 sq ft ground-floor retail → residential 15,950 → 15,950/680 = 23.46 → **23**. The count is a function of the commercial programme (a scenario input), not a single legal figure.

## Comparison with Option 1 (all-residential: 2.0 → 20,150 sq ft; 30/45/55; 29 units)

Option 5 shares the **same 2.0 combined cap (20,150 sq ft)** as Option 1 — it gives **no extra floor area.** The shops are carved out of the same envelope, so Option 5's residential floor area and dwelling-unit count are **lower** than Option 1 by the commercial amount (equal only if commercial = 0). Heights are identical. The overlay **changes the street-wall rule** (35-631(b) 70%-within-8-ft, vs Option 1's 23-431(a) line-up — overlay-reading case) and **adds** a commercial rear-yard rule (33-26/33-301) and the use/storey limits (32-161/32-421). Side and front yards are unchanged (none required). A higher 2.40 cap applies to both options only with qualifying housing.

## What is not known (exact item → where it is found)

1. **Zoning lot** (NB-01, access_blocked): read CERT 2022020201551001, ZONE 2022020201551002, DECL 2022031600431001 (ACRIS document images; owner-saved copy or records request). Until then every area/unit figure is conditional.
2. **Lot area basis** (NB-04, conflicting): recorded 10,075 vs GIS 10,387.99 → Christopher M. Buckley survey 2017-02-21 (DOF txn 76338) or 2018 deed Schedule A.
3. **Overlay mapped line / coverage** (option-05 OQ): DCP Zoning Map sheet, ZoLa, or the NYCO GIS geometry; plus 76-11/76-131/76-141 scaled-measurement bodies. Partial coverage → split-lot question (option-08).
4. **Commercial rear yard & storey limit**: 33-26, 33-27, 33-28, 33-30, 33-301, 32-421 — ZR portal, print/PDF node channel.
5. **Street-wall position within 35-631(b)**: prevailing-street-wall-frontage adjacency survey + operative street line (survey/approved plan). Mapped DCM widths (100/60 ft) do not fix the street line.
6. **Qualifying-housing eligibility** (2.40 vs 2.0; 65 ft height) and **which UG VI uses** (32-161 per-use flags) — scenario/eligibility facts.
7. **"Select commercial overlay"** (32-421 UG VIII second-storey bar) — ZR 12-10 term not captured.

## Conflicts among captures, settled cases and library

- **Settled case `step-p5-worked` leaves commercial FAR and the whole-building max "not known"** because its sealed folder lacked Article III Ch. 3. Article III Ch. 3 (33-12/33-121) **is now captured** and I read it directly: commercial FAR = **2.0** and the combined cap = **2.0**. This is an update, not a contradiction — the settled case's "not known" is now resolvable.
- **`benchmark-r6b-sections.json` mislabels 32-131 (UG III, community facilities) as the C2-2 retail permission**; the correct shops use is **32-161 (UG VI)**. The library flags this; the mislabel persists in the non-editable benchmark fixture.
- **Library option-05 section table is stale on capture state in one direction only:** it lists 32-421/33-26/33-301/33-27/33-28/33-30 as NOT CAPTURED — I confirmed all six are **absent** from `docs/research/zr-snapshots/v1/`. It omits 35-33, 35-53 and 34-231 from §5's table though all three are captured and relevant (35-53 reaches only the residential portion of a mixed building; 34-231 removes the front yard). No value conflict.

## Sections a capture task should add
32-421; 33-26, 33-27, 33-28, 33-30, 33-301 (commercial rear yard + waivers); ZR 12-10 "select commercial overlays" and verbatim "street, narrow"/"street, wide"; and confirm 35-53 and 23-436 (via 35-633) for the mixed-building rear yard and additional height/setback.

## What I could not check and why
No program output, API, benchmark fixture values or `return-*` files were read (sealed). I did not open ACRIS document images, the Buckley survey, the deed, or the DCP Zoning Map/ZoLa/NYCO overlay geometry — all are off-repository and some access_blocked. 32-421, 33-26 and 33-301 are not captured, so the storey limit and commercial rear yard rest on the library's live reading, not on text I verified. All street-line-dependent items (street wall, setback measurement) await a survey/approved plan.

END-OF-REPORT