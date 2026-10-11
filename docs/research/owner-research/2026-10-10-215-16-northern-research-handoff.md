# 215-16 Northern Boulevard: research findings and implementation handoff

**Queens · block 7334 · lot 70 · BBL 4073340070**  
**Research date: October 10, 2026.** Current zoning text was checked on that date. The ACRIS index reports a September 30, 2026 good-through date; that is not an October 10 title certification.

## Read this first

The research supports treating **lots 1 and 70 as a likely shared zoning lot that still needs document verification**. It does not support presenting lot 70's standalone development allowance as confirmed available capacity.

| Question | Answer | Consequence |
|---|---|---|
| Are lots 1 and 70 one zoning lot? | Strong corroboration: all three 2022 instruments are indexed against both lots, and a DOB filing explicitly describes one zoning lot. The instruments and approved zoning diagram were **not found in readable form**. | Carry a documented unresolved zoning-lot basis; obtain the actual instruments and approved plans. |
| Does lot 1 need to be subtracted from 39,934 sq ft? | **Not established.** DOB's PW1 instructions include retained buildings in proposed zoning floor area. | Determine the scope of 39,934 before performing a second subtraction. |
| Is 10,075 or 10,387.99 sq ft the legal area? | The printed tax map supports the 100.76-ft frontage, but the deed/survey area is **not found**. | Preserve the recorded and GIS figures separately; neither establishes the legal area by itself. |
| Is a rear yard necessarily required at the far corner? | **No such conclusion is justified.** The brief omits the independent short-block exception in ZR 23-344(b). The southern interfaces also appear to be neighboring side lines. | Reassess the yard logic using both exceptions, with survey and zoning-lot qualifications. |
| Is this a special density area? | **No.** The current definition lists Manhattan Core and Special Downtown Brooklyn only. | Resolve that geography flag. Keep the unit count dependent on the correct zoning lot, residential allowance and exemptions. |

This is source research and a stated reading of the zoning text, not a DOB determination. **The existing report's numbers should remain unchanged until the findings are checked against the missing official documents**, as the brief requires.

## 1. What is the zoning lot?

### Recorded evidence

I obtained the official ACRIS Real Property Legals, Master, Document Control Codes, References and Remarks datasets. The table distinguishes indexing from instrument contents. Sources: [Legals](https://data.cityofnewyork.us/resource/8h5j-fqxa.json?borough=4&block=7334&lot=70), [Master](https://data.cityofnewyork.us/resource/bnx9-e6tj.json?document_id=2022031600431001), [codebook](https://data.cityofnewyork.us/resource/7isb-wh4c.json); retrieved October 10, 2026. Full requests and responses are in the evidence pack.

| Instrument / document ID | Official code meaning | Document date / recording date | Indexed tax lots | What the contents establish |
|---|---|---|---|---|
| [2022020201551001](https://a836-acris.nyc.gov/DS/DocumentSearch/DocumentDetail?doc_id=2022020201551001), CRFN 2022000059133 | CERT: “CERTIFICATE” | Aug 4, 2016 / Feb 8, 2022 | Queens 7334/1 and 7334/70 | **Not found**: certificate subject, operative language, metes and bounds, area. |
| [2022020201551002](https://a836-acris.nyc.gov/DS/DocumentSearch/DocumentDetail?doc_id=2022020201551002), CRFN 2022000059134 | ZONE: “ZONING LOT DESCRIPTION” | Aug 9, 2016 / Feb 8, 2022 | Queens 7334/1 and 7334/70 | **Not found**: actual boundary description and stated area. |
| [2022031600431001](https://a836-acris.nyc.gov/DS/DocumentSearch/DocumentDetail?doc_id=2022031600431001), CRFN 2022000121661 | DECL: “DECLARATION” | Mar 16, 2022 / Mar 22, 2022 | Queens 7334/1 and 7334/70 | **Not found**: whether this is the operative zoning-lot declaration, its restrictions and exhibits. |

“CERTIFICATE” is generic; that code alone does not prove a zoning-lot certificate. Likewise, indexing a declaration against both lots does not tell us its legal effect. The index's easement or air-rights flags are not substitutes for reading the instrument.

Two earlier records indexed against lot 1 deserve inclusion in the document request:

- CERT **2016081000837001**, CRFN **2016000277657**, dated August 4, 2016, recorded August 11, 2016.
- ZONE **2016081000837002**, CRFN **2016000277658**, dated August 9, 2016, recorded August 11, 2016.

Their execution dates match the two instruments recorded in 2022. That is a possible connection to investigate, **not proof of re-recording or identical contents**. No reference-table entry linking these target instruments was found. Source: [lot 1 Legals](https://data.cityofnewyork.us/resource/8h5j-fqxa.json?borough=4&block=7334&lot=1), joined to Master by document ID; October 10 retrieval.

**Access result:** the ACRIS search routed to its [bandwidth policy](https://a836-acris.nyc.gov/BandwidthPolicy/ACRIS-BW-POL.html); a direct document-detail attempt also failed. I used the official Open Data index instead. I have **not read the ACRIS images**, and no legal-description quotation is supplied for them.

### DOB corroboration and the floor-area trap

Source: [DOB Job Application Filings, BIN 4157401](https://data.cityofnewyork.us/resource/ic3t-wcy2.json?bin__=4157401) and [BIN 4623241](https://data.cityofnewyork.us/resource/ic3t-wcy2.json?bin__=4623241), retrieved October 10, 2026. These are filing records, not downloaded approved plans.

| Job | Recorded status and date | Zoning floor area in filing | Interpretation limit |
|---|---|---|---|
| 421803891, A1, lot 1 | Plan exam disapproved; latest action Apr 11, 2022 | Existing **9,100**; proposed **39,772 sq ft** | Describes “ONE (1) ZONING LOT AND (2) TAX LOTS (LOT #1 &amp; #70)”. Strong evidence of intended shared treatment, but not an approved final area schedule. |
| 421199072, A1, lot 1 | Entire job permitted Feb 22, 2017; no signoff in returned row | Existing/proposed **14,150 sq ft** | Predates the March 2017 tax-map split. Its building/tract scope must be read from the plans; do not substitute this for current lot 1 ZFA. |
| 440608941, NB, lot 70 | Approved May 2, 2022; fully permitted Apr 23, 2024 | Proposed **39,934 sq ft** | The index field does not resolve whether this already includes retained lot 1 floor area. Construction area **45,388 sq ft** is a different measure. |

The key new source is the [DOB PW1 User Guide](https://www.nyc.gov/assets/buildings/pdf/pw1_userguide.pdf), **revised February 2020, printed/PDF page 14, section 12C**. Its proposed-ZFA instruction includes:

> “proposed building(s)/building segments and any existing building(s)/building segments on the zoning lot”

Section 12B on that page also calls for identifying the tax lots within the zoning lot. **Therefore, 39,934 cannot safely be labeled new-building-only merely because the job is filed on lot 70.** The filled PW1 and ZD1 must show how that total was assembled.

An arithmetic diagnostic illustrates the risk. Under the brief's hypothetical **20,000 sq ft zoning-lot area × 2.0 FAR = 40,000 sq ft** allowance, a **combined** proposed total of 39,934 would leave 66 sq ft. If 39,934 were instead new-building-only and 9,100 were separately retained, that sum would exceed the hypothetical allowance by 9,034 sq ft. **Neither residual is a finding of actual available rights or a compliance judgment.** Both rely on unsettled scope, area, use and applicable-rule assumptions. Do not combine the 2022 39,772 total with the later 39,934 total as though they were one approved revision.

### Present status and remaining capacity

I found **no later zoning-lot subdivision or replacement declaration** in the searched records. This is a search result, not proof of absence:

- ACRIS returned 37 distinct document IDs across lots 1 and 70. The latest located recordings were mortgage/assignment instruments recorded January 16, 2024. The dataset-wide [maximum good-through date](https://data.cityofnewyork.us/resource/8h5j-fqxa.json?%24select=max(good_through_date)) is **September 30, 2026**.
- DOB SI job **421158801**, completed June 12, 2015, describes splitting a tax lot into two. It does not establish a legal zoning-lot subdivision. Under [ZR 12-10](https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10), zoning-lot definition amended February 2, 2011, zoning and tax boundaries can differ; a zoning-lot subdivision has separate compliance conditions.
- [DOB NOW filings for lot 1](https://data.cityofnewyork.us/resource/w9ak-ipjd.json?bbl=4073340001) include two 2023 sign jobs, Q00921610-I1 and Q00921593-I1. [Lot 70 filings](https://data.cityofnewyork.us/resource/w9ak-ipjd.json?bbl=4073340070) include structural/services amendments, temporary works, signs and the 2026 restaurant fit-out Q01412228-I1/S1/S2. None of the returned descriptions identifies a zoning-lot subdivision. Some 2026 sign records still use the demolished building's BIN; BBL and address must also be checked.
- [DOB NOW CO index](https://data.cityofnewyork.us/resource/pkdm-hqz6.json?bbl=4073340070): CO **4623241-0000001**, issued **June 3, 2026**, associated with NB 440608941 and 38 dwelling units. This index is not the building-by-building zoning floor-area schedule.

**Not found:** the approved ZD1, filled PW1 zoning section, approved zoning calculation sheets, survey/plot plan, amendments supporting the CO, or an authoritative current ZFA for lot 1. BIS requests returned HTTP 403. The [DOB NOW portal](https://a810-dobnow.nyc.gov/publish/Index.html) displayed scheduled maintenance October 9–11, 2026. Searches of the accessible CO datasets returned no lot 1 CO establishing its ZFA; those datasets do not cover every historical certificate.

**What settles it:** the latest approved NB 440608941 ZD1/PW1 and area schedule, linked lot 1 approvals, the recorded zoning-lot instruments and a current title/zoning-lot review. Remaining capacity must be calculated once from the verified allowance and all retained/approved chargeable floor area, with private allocation restrictions separately checked.

## 2. Which area and dimensions are supportable?

**Short answer:** legal/survey area **not found**. The 100.76-ft frontage now has independent support from the actual printed DOF tax maps. The GIS polygon remains materially wider.

| Source and date | Measurement basis | Lot 70 | Lot 1 / combined |
|---|---|---|---|
| [DOF map 40733420140108123603](https://propertyinformationportal.nyc.gov/pdf/home/index/map_library/40733420140108123603), effective Jan 8, 2014; p. 1 | Printed tax-map dimensions | Lot 70 not yet separately shown | Old lot 1: **200.01-ft** Northern frontage; **100-ft** depth. |
| [DOF map 40733420170322143246](https://propertyinformationportal.nyc.gov/pdf/home/index/map_library/40733420170322143246), effective Mar 22, 2017; p. 1 | Printed tax-map dimensions | **100.76-ft** Northern frontage; **100-ft** depth | Lot 1 **99.25-ft** frontage; **100-ft** depth. Frontages sum to **200.01 ft**. |
| [DOF map 40733420210729120533](https://propertyinformationportal.nyc.gov/pdf/home/index/map_library/40733420210729120533), effective Jul 29, 2021; flagged current; p. 1 | Printed tax-map dimensions | Same **100.76 × 100 ft** labels | Same **99.25 × 100 ft** labels. |
| [PLUTO 26v2](https://data.cityofnewyork.us/resource/64uk-42ks.json?borough=QN&block=7334), retrieved Oct 10, 2026 | Administrative lot-area/frontage/depth attributes | **10,075 sq ft; 100.76-ft front; 100-ft depth** | Lot 1 **9,925 sq ft; 99.25-ft front; 100-ft depth**. Summed area **20,000 sq ft**. |
| [MapPLUTO 26v2 polygon](https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0/query?where=BoroCode%3D4%20AND%20Block%3D7334&outFields=*&outSR=2263&f=json), retrieved Oct 10 | Calculated GIS geometry, EPSG:2263, US survey feet | **10,387.99 sq ft**; north **103.87921 ft**; east **99.97605 ft**; west **99.97647 ft**; south **101.70896 + 2.22445 ft** | Lot 1 **9,922.45 sq ft**. Combined **20,310.44 sq ft**; combined north frontage **203.12900 ft**. |
| DOB 440655961, filed Dec 11, 2020; signed off Jul 22, 2026 | BPP filing description, not a survey | Northern **100.76 ft**; 215 Place **100 ft** | Description's related NB number is **121329641**, not 440608941. Preserve this inconsistency. |
| [2018 deed 2018013000919001](https://a836-acris.nyc.gov/DS/DocumentSearch/DocumentDetail?doc_id=2018013000919001), CRFN 2018000037480; Jan 18 / recorded Jan 31, 2018 | Deed/legal description | **Not found**: bearings, distances and stated area | The index identifies lot 70; it does not supply the deed's description. |

**A specific survey has been identified.** DOF's [Change History table](https://services6.arcgis.com/yG5s3afENB5iO9fj/ArcGIS/rest/services/DTM_ETL_DAILY_view/FeatureServer/9/query?where=Borough%3D%274%27%20AND%20Block%3D7334&outFields=*&f=json), transaction **76338**, objects **40104** and **74111**, dates the apportionment **March 22, 2017**. The authorization field names:

> “Survey by Christopher M. Buckley, 2/21/2017”

It also cites deed **CRFN 2005000015416**, dated January 7, 2005 in that field. The survey itself was **not found**. DOF's Lot Actions table identifies lot 70 as new and lot 1 as affected under transaction 76338. This is a precise retrieval lead for DOF, the owner or the surveyor.

### Conflicts that remain open

- **10,075 versus 10,387.99 sq ft:** difference **312.99 sq ft**, about **3.11%**, comparing administrative area with GIS area. No legal-area reconciliation has been found.
- **100.76 versus 103.87921 ft:** the printed tax map and BPP text support the former; GIS gives the latter. Graphic coordinates and printed dimensions in a tax-map system can be different evidentiary measures.
- **100.76 × 100 = 10,076**, not 10,075. The brief's parenthetical is not exact arithmetic. Frontage/depth descriptors should not be treated as an exact rectangular survey.
- **March 22 versus April 7, 2017:** DOF map/change history and PLUTO APPDate differ. They may reflect different administrative events; that explanation is not verified.
- Some legacy BIS rows put **4157401**, a BIN, in their `bbl` field. Match borough/block/lot and BIN together; do not treat every value in that field as a valid ten-digit BBL.
- The current tax map labels an **ALLEY** across the southern part of the northern lots. Its legal status, width and rights were **not found**. Obtain the survey and easement/title schedules before treating that strip as buildable or as a public street.

### Did a street change explain the discrepancy?

**Not found.** The Digital City Map alteration query returned **CP 4366 / Queens Borough President map 3114**, [one-sheet map](https://nycdcp-dcm-alteration-maps.nyc3.digitaloceanspaces.com/cp4366.pdf), dated **June 14, 1946**, with index effective date **May 10, 1947**. I inspected the sheet and the Northern Boulevard/215 Street/215 Place detail. It includes street-system and grade changes over several areas; the relevant detail shows grades and a **100-ft Northern Boulevard** width. It does not establish a 3.1-ft boundary shift at this parcel. The current centerline dataset gives **100/60/60-ft** widths for Northern/215 Place/215 Street; widths alone do not fix street-line positions.

DOF's queried block-boundary-change table returned no rows. The retrieved 1966-indexed archival map and 2014 map show the old combined **200.01-ft** frontage. Neither a negative table result nor those maps proves that no historical street action occurred. A certified street-line/topographic record and deed-to-survey reconciliation would settle this question.

## 3. Is a rear yard required beyond the corner area?

**Short answer:** the available evidence supports a **conditional no-rear-yard reading**, stronger than the brief's unresolved corner-only analysis. Approved-plan confirmation remains **not found**.

### First check the omitted exception

[ZR 23-344(b)](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344), amended **December 5, 2024**, official PDF **page 2**, addresses lots fronting the short dimension of a block. Its operative phrase is:

> “no rear yard shall be required within 100 feet of such street line”

[ZR 12-10](https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10), short-dimension definition amended **December 5, 2024**, uses the threshold **“less than 230 feet”** between the bounding streets.

**My application of those provisions to this geometry:** Northern Boulevard's block frontage between 215 Street and 215 Place measures **200.01 ft from printed tax-map labels** and **203.13 ft from GIS**. Both are below 230 ft. Lots 1 and 70 front that line. The maps label their depth 100 ft; the GIS maximum perpendicular distance from the Northern line is approximately **99.97 ft**. This strongly supports examining paragraph (b) for the whole northern tract, whether lot 70 is considered alone or with lot 1.

This is not survey-level proof at a 100-ft threshold: the GIS margin is only about **0.03 ft**, while the records have larger discrepancies. Confirm the operative street line and depth on the survey/ZD1. The **144.60-ft GIS diagonal from the street corner** tests a different, point-based exception in paragraph (a); it does not defeat the street-line-based exception in paragraph (b).

### Southern neighbors are now identified

The current DOF map and MapPLUTO establish the following **tax-parcel** adjacency. Whether each neighbor's legal zoning lot has the same boundary still needs title/plan verification.

| Tax lot and address | Street frontage | PLUTO 26v2 frontage / depth / area | Printed current tax map | Interface with the subject tract, measured in GIS |
|---|---|---|---|---|
| 1 — 215-10 Northern Boulevard | Northern Boulevard and 215 Street | **99.25 / 100 ft; 9,925 sq ft** | **99.25 / 100 ft** | Shares **99.97647 ft** with lot 70's west edge. This line is internal if the zoning lot is 1+70. |
| 11 — 45-12 215 Place | 215 Place | **28.42 / 100 ft; 2,842 sq ft** | **28.5-ft** street frontage; **100.01-ft** depth label | Shares the eastern **101.70896 ft** of lot 70's south boundary. |
| 61 — 45-11 215 Street | 215 Street | **28.58 / 100 ft; 2,858 sq ft** | **28.75-ft** street frontage; **100-ft** depth label | Shares the western **2.22445 ft** of lot 70's south boundary and **99.24971 ft** of lot 1's south boundary. |

Thus lot 70 touches **1, 11 and 61**. The combined 1+70 tract touches **11 and 61** externally. The north ends of the lot 11/61 dividing line meet lot 70 at the extra corner **2.22445 ft from lot 70's southwest corner**. The diagram and coordinate calculations are included in the evidence pack.

The neighbors also have GIS/record discrepancies: lot 11 GIS area is **2,939.77 sq ft**, and lot 61 GIS area is **2,933.19 sq ft**; their GIS street-front lengths are approximately **28.904 ft** each. Do not silently replace the different printed or PLUTO dimensions.

### Side-line classification and the alternative exception

Under the front/rear/side definitions in ZR 12-10, amended December 15, 1961, my reading is that the northern boundaries of lots 11 and 61 are **side lines**: each runs from its own street frontage toward its rear. The rear interface between 11 and 61 meets the subject boundary at a point; it does not coincide with it along a segment.

Consequently, if those tax boundaries are also the relevant zoning boundaries, **23-344(c)(3)** supplies an alternative no-rear-yard rule for an R6B subject portion adjoining those side lines. The small south-boundary portion more than 100 ft from 215 Place includes contacts with both neighbors. Lot 70's west boundary intersects Northern Boulevard and extends only about 99.97 ft from that line in GIS; it should not be labeled a rear line merely because it is over 100 ft from 215 Place.

For a joined 1+70 zoning lot, remove the internal boundary and evaluate the exterior geometry anew. Also check the multi-rear-line provisions in 23-344(d) if the confirmed layout calls for them. Do not reuse a tax-lot-only corner classification.

If a required rear yard survives the applicable exceptions, [ZR 23-342](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342), amended **December 5, 2024**, PDF **pp. 2–3**, does **not** prescribe one universal 30-ft depth: standard provisions distinguish height, building attachment and lot width. At/below 75 ft, 20 ft applies to detached/zero-lot-line buildings and to attached/semi-detached buildings on lots at least 40 ft wide; narrower attached/semi-detached lots and portions above 75 ft have 30-ft provisions, subject to modifications.

**Keep controls separate.** A rear-yard exception does not itself waive [lot coverage](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362), setbacks, window/open-space requirements or private rights. The C2-2 mixed-use setting also requires the residential/commercial applicability rules, including [ZR 35-22](https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-22) and [35-50](https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-50). This research does not certify a full building envelope.

### Approved yards and BSA/DOB decisions

**Not found:** NB 440608941's approved yard diagram or a site-specific DOB determination. Searches of official BSA [post-1998 decisions data](https://data.cityofnewyork.us/resource/yvxd-uipr.json?block=7334) and the [1916–1997 index](https://data.cityofnewyork.us/resource/f72e-3i4c.json?%24where=block%20like%20%27%257334%25%27) produced no Queens block 7334 match. Their metadata reports updates on September 21, 2026 and August 19, 2020 respectively. The older broad search returned two Brooklyn block 07334 cases, which are unrelated. Targeted address/block web searches also found no relevant decision. This does not exclude unindexed determinations, old files or matters outside those datasets. Obtain the approved ZD1 and any ZRD1/reconsideration or BSA references in the job folder.

## 4. Special density area: resolved, unit count still conditional

[ZR 12-10](https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10), definition amended **December 5, 2024**, currently lists:

> “(a) the Manhattan Core; and (b) the Special Downtown Brooklyn District.”

Manhattan Core comprises Manhattan Community Districts 1–8. This Queens site is in neither listed geography. Its ordinary multiple-dwelling scenario is therefore subject to the **680 factor** in [ZR 23-52](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52), amended **December 5, 2024**, PDF **pp. 2–3**, unless a separate listed exemption applies. Qualifying senior housing and specified conversions need separate handling. Qualifying affordable housing is not automatically exempt merely because it may receive a higher FAR.

The calculation uses **maximum permitted residential floor area on the zoning lot**, not GIS lot area, construction area, or automatically the NB's proposed total. Fractions of at least **0.75** round up; smaller fractions do not. As an explicitly hypothetical check only, **20,150 / 680 = 29.632… → 29 units**, not 30. This does not establish a legal cap of 29 for the existing 38-unit building, whose approved lot, area allocations, filing-era rules and amendments must be read first.

## 5. What Claude should do with this research

This is an implementation handoff, not authorization to replace unverified report numbers.

1. **Persist the evidence.** Add this handoff and the evidence manifest to the project's existing research/reference-case structure for 215-16 Northern. Add a short link in the existing session handoff and canonical project instructions so the next session reads it before changing this benchmark. Avoid creating a competing second source of truth.
2. **Separate facts from legal determinations.** Store source, retrieval date, document date, measurement basis, geographic scope and verification status for every area. Use distinct tax-lot and zoning-lot identifiers. Index evidence should never satisfy an instrument-content verification gate.
3. **Correct the question being asked about area.** A1 is not an owner preference between two interchangeable numbers. Append the discovered tax-map evidence and named survey to `/root/project/lanes-runtime/owner-docs/OWNER_QUESTIONS.md`; preserve the question history and mark the legal-area issue unresolved pending documents.
4. **Resolve the special-density geography flag** through the existing reviewed workflow. Preserve the independent unresolved inputs to the legal unit calculation. Use the correct 0.75 rounding rule and exemption handling.
5. **Review rear-yard logic.** Evaluate 23-344(b) as well as (a), then applicable (c)/(d). Use confirmed zoning-lot boundaries and segment-level neighboring-line classifications. Use distance to the relevant line for line-based rules and distance to the intersection point only where specified. Never infer an entire required yard from the diagonal alone.
6. **Prevent floor-area double counting.** Require the PW1/ZD1 area schedule to identify whether each amount is building-only or zoning-lot-wide and whether it includes retained buildings. Keep construction floor area separate. Do not publish 66 sq ft, 9,100 sq ft or 14,150 sq ft as verified remaining/retained rights.
7. **Keep historical approval and a current-law scenario distinct.** The NB approval/permit dates precede the December 2024 zoning changes. Do not evaluate the existing approval solely using today's sections without checking the applicable rules and amendments.
8. **Verify the meaningful changes.** Add focused regression cases for short-block versus corner-point tests; external versus internal lot lines; neighboring rear-line endpoint versus shared segment; the 680 factor and rounding boundary; and combined-ZFA double counting. Provide source-linked expected results, changed files, test output and any still-blocked calculation. A green test suite does not verify missing documents.

### Append these concrete requests to the existing questionnaire

| Request | Document needed | What it resolves |
|---|---|---|
| Q1 — Recorded zoning lot | Complete 2022 CERT, ZONE and DECL listed above, including exhibits, plus the two 2016 counterparts and current title/zoning-lot review | Operative tract, restrictions, legal description, current status. |
| Q2 — Approved zoning accounting | Latest approved ZD1, PW1 section 12, zoning/area sheets, survey and amendments for **440608941**; related lot 1 jobs **421803891 / 421199072** | Zoning-lot area, permitted/proposed totals, retained lot 1 ZFA, approved yards and applicable rule version. |
| Q3 — Survey and boundaries | **Christopher M. Buckley survey dated Feb 21, 2017**, any later certified survey, 2018 deed with Schedule A and relevant easement/title schedules | Recorded-versus-GIS discrepancy, street line, alley annotation, neighboring boundaries. |

Ask for those files or the authority to obtain them through the normal records process. Do not ask the owner to decide a legal boundary or approve an invented area. No outside party was contacted during this research.

## Evidence pack and reproducibility

The companion ZIP includes the retrieved **2014, 2017 and current tax maps**, the older archival map, **CP 4366**, the official **PW1 guide**, relevant official zoning PDFs, selected readable page images, the GIS diagram, official data responses, request URLs, retrieval times and SHA-256 hashes. It contains **no ACRIS instrument images or approved ZD1**, because those were not obtained.

`source-manifest.json` maps each captured source to its original request and local file. `geometry-calculations.json` records the GIS calculations; `build_geometry.py` reproduces them from the source polygon using ordinary vector geometry. Small differences in the last decimal from the ArcGIS stored area field arise from numerical calculation; the report rounds areas to two decimals. No survey dimensions were invented and no GIS outline was rescaled to force agreement with the tax-map labels.
