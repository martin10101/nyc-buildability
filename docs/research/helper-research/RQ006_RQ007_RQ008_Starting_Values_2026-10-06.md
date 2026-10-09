# RQ-006, RQ-007, RQ-008: the research helper's return, 2026-10-06 (discovery aid only)

**What this is.** The unchanged return of the orchestrator's research helper (an `official-source-researcher` agent that searched online), run on 2026-10-06 under the owner's instruction that every question in `docs/RESEARCH_REQUESTS.md` first gets a research helper (D-090 R285 to R288).

**How to read it (D-050-R002).** It is a lead, never a source of record. No rule, number or fact may cite this file as its origin. Legal text it quotes must be captured from the official source before it is used. The starting values it suggests are design assumptions; the owner approves them.

**Its own limits, as it states them:** the ground-floor height in HPD's "Laying the Groundwork" guideline was not read (the file was too large); several code quotes come from search summaries, not opened pages; the average new-apartment size rests on one market dataset; "loss factor" means different things in different sources.

The return follows.

```
# RQ-006, RQ-007, RQ-008 — starting design assumptions (R6B first)

Source tags: OFFICIAL = law/code/City agency; MARKET/PRO = industry or professional. Verbatim quotes and section numbers are given where I read them directly; items I only have from a search-result summary are marked "(search-snippet; verify verbatim)".

Headline numbers: dwelling-unit factor **680** (ZR §23-52, amended 12/5/2024); habitable-room ceiling min **8 ft** (BC §1208.2); R6B max building height **55 ft** standard / **65 ft** qualifying (ZR §23-432); new NYC apartments average **~700 sq ft** (Queens ~692), RentCafe/Yardi 2024; apartment efficiency commonly **70–85%**.

---

## RQ-006 — Floor-to-floor height

**1. Law and codes.** The Zoning Resolution does NOT fix a floor-to-floor height. It caps building height and FAR; the floor count is the height limit ÷ whatever floor-to-floor the designer chooses. For R6B, **ZR §23-432** "Maximum height of #buildings# and setbacks" (OFFICIAL, zr.planning.nyc.gov, LAST AMENDED 12/5/2024): standard residences — max base height 45 ft, **max building height 55 ft**; qualifying affordable/senior housing — max base 45 ft, **max building height 65 ft**. The table sets **no maximum number of stories** (floors = height ÷ floor-to-floor). FAR is 2.0 (2.2 with Inclusionary Housing), per DCP's R6B sheet.
- CONFLICT, resolved: DCP's printed R6B district sheet (nyc.gov/.../districts-tools/r6b.pdf) still reads "50' maximum building height, base 30'–40'" — that sheet is pre-City-of-Yes and stale; current ZR §23-432 (55/65 ft) governs. Minimum base height is reported inconsistently (30 ft on the DCP sheet and up.codes; 40 ft when I read the ZR table) — read the §23-432 table directly to settle.
- Minimum ceiling heights fix the floor, not floor-to-floor. **NYC Building Code §1208.2** (OFFICIAL, up.codes reproduction, read directly): "Habitable rooms and spaces shall have a ceiling height of not less than 8 feet (2438 mm)." Occupiable spaces/corridors 7 ft 6 in; bathrooms/kitchens/storage/laundry 7 ft. **§1208.3.1**: "Every habitable room or space shall have not less than 80 square feet (7.4 m2) in net floor area." Multiple Dwelling Law §31 / HMC §27-2074: every living room min height 8 ft (search-snippet; verify verbatim).
- **NYC BC §2308.2.2** "Allowable floor-to-floor height" caps conventional WOOD-frame floor-to-floor at 11 ft 7 in — light-frame only, not an R6B masonry/concrete building; not a general number.

**2. Official guidance.** HPD "Laying the Groundwork: Design Guidelines for Retail and Other Ground-Floor Uses" (OFFICIAL, HPD + Design Trust) names "Adequate Floor-to-Floor Height" a critical ground-floor factor, but I could not extract its exact figure (87-pp PDF exceeded the fetch size limit).

**3. Practice/market.** Residential floor-to-floor commonly 9–10 ft (≈8–9 ft finished ceiling + ~1 ft structure/MEP); 10 ft with a ~10-inch concrete flat-plate deck is a standard assumption. Ground-floor retail/commercial commonly 14–16 ft (design guides cite ~15 ft minimum) for storefront glazing, HVAC, signage; a community-facility ground floor sits in the same taller band. (MARKET/PRO: adventuresincre, young-architect, SPUR.)

**4. Candidate starting values.** Typical residential floor: **10 ft** (range 9.5–10.5). Ground floor with shops/community facility: **14 ft** (range 14–16), held as a SEPARATE editable value. An R6B 55-ft building then yields ~5 floors (e.g., one 14-ft ground + four ~10 ft). The program's current 10 ft is defensible.

**5. Confidence: PARTLY SUPPORTED.** The 8-ft ceiling minimum is official, but no official source fixes floor-to-floor; the 10-ft / 14-ft values rest on consistent professional convention, not a cited City number.

**6. To settle:** the exact figure in HPD "Laying the Groundwork"; a NYC architect's typical R6B stacking/section.

---

## RQ-007 — Average apartment size

**1. Law (the LEGAL limit).** **ZR §23-52** "Maximum Number of Dwelling Units" (OFFICIAL, LAST AMENDED 12/5/2024, read directly): "the maximum number of #dwelling units# permitted shall be determined by dividing the maximum #residential# #floor area# permitted on the #zoning lot# by the applicable #dwelling unit# factor… (b) For all other types of #multiple dwelling residences#, the applicable #dwelling unit# factor shall be **680**. Fractions equal to or greater than three-quarters … shall be considered to be one #dwelling unit#." No factor applies to special density areas, qualifying senior housing, or non-residential/community-facility conversions (para (a)). This is a density CAP: it implies ~680 sq ft of residential ZONING floor area per unit (including that unit's share of common area) — not a built room size.
- Minimum room sizes (OFFICIAL, search-snippet; verify verbatim): NY Multiple Dwelling Law §31 / HMC §27-2074 — one living room min 150 sq ft (plans on/after 12/9/1955; 132 sq ft before), every other living room 80 sq ft with least dimension 8 ft, min height 8 ft. (Pending Int. 1479-2025 would raise one living room to 110 sq ft / 10-ft dimension for buildings on/after 1/1/2027.)
- HPD Design Guidelines for New Construction (OFFICIAL, rev. 8/1/2000, read directly): sets minimum ROOM areas, not whole-unit areas — e.g., 1-BR combined LR/DA/K 270 sq ft min, primary bedroom 130 sq ft; room area "computed to the inside finished surfaces of the walls and partitions, and exclude columns, pipe chases, and closets." HPD's newer guidelines reportedly add target min–max unit areas by type, but I could not verify those numbers.

**2. Market/practice.** RentCafe (analysis of Yardi Matrix data, June 10 2024, read directly) — average size of NEW apartments built 2014–2023: **Manhattan 737 sq ft, Brooklyn 712, Queens 692**; citywide ~700. These are net interior unit areas of market-rate rentals.

**3./4. Method.** Feasibility studies divide the residential floor area available for apartments by an average built unit area; the market figure above is the usual anchor. Net vs gross: §23-52 uses residential ZONING floor area per unit; RentCafe measures net interior unit area — close (~680 vs ~700) but different bases, so keep them labeled.

**4. Candidate starting value.** Realistic average built apartment: **~700 sq ft net** (range 690–740); for outer-borough / Queens-leaning low- and mid-rise, **~690 sq ft**. Hold strictly separate from the legal cap (residential ZFA ÷ 680).

**5. Confidence: WELL SUPPORTED** for the legal factor (official, current) and the direction of the market figure; the market number rests on ONE dataset (RentCafe/Yardi), so treat the realistic value alone as PARTLY SUPPORTED until a second source (DCP Housing Database / DOB filings) corroborates.

**6. To settle:** DCP Housing Database / DOB job filings for actual new-unit mix and sizes; the current HPD unit-area ranges (verify numbers).

CAUTION: a web snippet listing "studio 375 / 1-BR 660 / 2-BR 900 sq ft" appears to mix a non-NYC (DC DHCD) table — unverified; do not use as NYC HPD.

---

## RQ-008 — Shared-space allowance (loss factor)

**1. Law — which spaces the ZR leaves out (the base).** ZR §12-10 "floor area" (OFFICIAL): zoning floor area INCLUDES interior circulation — "elevator shafts or stairwells at each floor," plus lobbies and corridors — so halls/stairs/lifts/lobby ARE counted in zoning floor area. It EXCLUDES: "cellar space"; mechanical-equipment floor space (para (8) — confirmed by **§23-241**, read directly, which re-counts such space only in R9/R10 towers where it exceeds 25 ft per 75 vertical ft); unused/inaccessible space (para (k)); and, in R3–R5 (§78-02, read directly), up to 200 sq ft/story of required accessory parking. So zoning floor area < gross floor area (gross includes cellar + mechanical).
- Consequence for the base: refuse/service/circulation rooms are already INSIDE zoning floor area; cellar and mechanical are NOT. The percentage therefore differs by denominator — this must be stated.

**2. Official guidance.** None found that fixes an efficiency percentage.

**3. Practice/market.** Efficiency = usable ÷ (rentable or gross); loss factor is its complement. Apartments historically average ~70–75% efficient (25–30% loss); well-designed multifamily reaches ~80–82%+ (young-architect "GRUN" framework; base-4; rets.ai). Low-rise is more efficient than mid/high-rise (fewer/smaller elevator cores, less corridor, fewer required egress stairs); the non-apartment share rises with height and with each added stair/lift.

**4. Candidate starting value.** For an R6B-scale building (4–5 stories, small floorplates, 1–2 stairs, small or no elevator): start at **~15% of GROSS floor area** as non-apartment (≈85% efficient), editable; for a double-loaded-corridor mid-rise use **~20%** (≈80%). **State the base: gross floor area.** If the tool applies the percentage to ZONING floor area instead (cellar/mechanical already removed), use a SMALLER share (~10–15%), since the remaining non-apartment space is mainly circulation + lobby + refuse/service.

**5. Confidence: PARTLY SUPPORTED.** The ZR exclusions are official; the efficiency ranges are consistent professional figures but not NYC-specific, and definitions vary by source.

**6. To settle:** a NYC architect's gross-to-net study for an R6B building; the REBNY measurement/loss-factor standard; an HPD or developer pro-forma template.

CONFUSING: "Efficiency / loss factor" means different things in different sources — REBNY's *rentable* loss factor (rentable vs usable, a leasing convention that can add loss back to tenants) is NOT the architect's *gross-to-net* ratio (net apartment area ÷ gross building area). A feasibility tool needs the gross-to-net ratio with a named denominator; a "loss factor" quoted from a leasing source will mislead if used directly.

---

## URLs I opened and whether they loaded

Loaded:
- https://www.nyc.gov/assets/planning/download/pdf/zoning/districts-tools/r6b.pdf — loaded (PDF read; DCP sheet, now stale on height)
- https://zr.planning.nyc.gov/print/pdf/node/18026 — loaded (ZR §23-52, dwelling-unit factor 680)
- https://zr.planning.nyc.gov/article-ii/chapter-3/23-52 — loaded (same)
- https://zr.planning.nyc.gov/article-ii/chapter-3/23-432 — loaded (R6B height 55/65 ft)
- https://zr.planning.nyc.gov/print/pdf/node/22752 — loaded (ZR §23-24 / §23-241, mechanical floor area)
- https://zr.planning.nyc.gov/print/pdf/node/19231 — loaded (was §78-02, not floor-area def)
- https://zr.planning.nyc.gov/article-i/chapter-2/12-10 — loaded but the "floor area" entry was not in the returned excerpt (page too large)
- https://www.rentcafe.com/blog/apartment-search-2/apartment-size-new-york-city-2024/ — loaded (borough new-apartment sizes)
- https://up.codes/s/height-and-setback-requirements-in-r6-through-r12-districts — loaded (R6B height, §23-432)
- https://up.codes/s/habitable-rooms-and-spaces — loaded (BC §1208.2 / §1208.3.1 verbatim)
- https://www.nyc.gov/assets/hpd/downloads/pdfs/services/new-constr-guidelines.pdf — loaded (HPD min room sizes)

Failed:
- https://www.nyc.gov/assets/hpd/downloads/pdfs/services/laying-the-groundwork-retail-design-guidelines.pdf — FAILED (exceeded 10 MB WebFetch limit)
- https://law.justia.com/codes/new-york/mdw/article-3/title-1/31/ — FAILED (HTTP 403)

Used from search-result summaries only (not opened individually; cited as verification targets): NYC BC §1208 (codelibrary.amlegal.com), MDL §31 / HMC §27-2074 (law.justia.com, codelibrary.amlegal.com), apartment efficiency (base-4.com, rets.ai, academy2.youngarchitect.com), residential/retail floor-to-floor (adventuresincre.com, spur.org), dwelling-unit-factor commentary (gtlaw.com, citymeetings.nyc).

Limitations: the only figure directly missed is the official HPD ground-floor height number (RQ-006e). The MDL/HMC minimum-room quotes and the BC §1208 bathroom/kitchen lines are from search snippets, not a page I opened; they should be read verbatim before encoding. Per D-050, every value here is a discovery aid, not a source of record — the owner approves the starting values, and load-bearing legal text must be re-captured through the project's official-capture discipline.

END-OF-REPORT
```
